extends RefCounted
class_name FleaVendors

## Who holds each flea-market stall on a given day (research/flea_markets/00_plan.md §2): pure, from (seed, market,
## stall, day) and the vendor pools (remake/markets/vendor_pool.json, tools/markets/bake_vendor_pool.py).
##
##   FleaVendors.tenant(m, stall, day)  -> {pid, kind: permanent|season|day|islander|"", category, since_week, island}
##   FleaVendors.roster(m, day)         -> what is OPEN that day: {who: PackedInt32Array (pool index; -1 none;
##                                         <= -10: islander island -10 - ix), kind: PackedByteArray (0 none, 1 permanent,
##                                         2 season, 3 day, 4 islander), cat: PackedByteArray}
##   FleaVendors.local_roster(m, day)   -> the town's own vendors that day, whatever the mode (leases and day vendors)
##   FleaVendors.occupancy(m, day)      -> local vendors / stalls on that day's roster
##   FleaVendors.vending(pid, day)      -> {market, stall, t0, t1} if this person keeps a stall today, else {}
##   FleaVendors.islander_stalls(m, day)-> PackedInt32Array of the stalls islanders hold today
##
## Tenure (00 §2.2):
##   - permanent stalls (sheds and half the food pads, 35 %) on 52-week leases from a hashed start week; renewed with
##     p 0.85; a new tenant takes over the week after a lease lapses (that week the stall is the day vendors');
##   - rotating stalls on season leases of 8-16 weeks: each stall's 24-week blocks split in two terms (L, 24 - L),
##     L in 8..16, staggered by stall: ~8 % change hands any week;
##   - presence: a permanent tenant comes with p 0.96, a season tenant 0.88; the empty pitches are resold at dawn to
##     day vendors up to the day's target T in [0.80, 0.97] (May-Sep 0.90-0.97, Dec-Feb 0.80-0.86, else 0.85-0.93);
##   - nobody holds two stalls on one day (a later stall's double-booked tenant is a no-show; the dawn resale fills it);
##   - while islands are in SERVICE, every stall still empty goes to the islanders (2 a stall), shared out over the
##     raft by size (rendezvous hashing: a stall keeps its island while that island stays); on Mon-Thu outside a
##     Bright Week the town's booths are shut and the islanders keep the stalls that are empty on that week's Friday.

const POOL := "res://remake/markets/vendor_pool.json"
const PERM_WEEKS := 52
const PERM_RENEW := 0.85
const PERM_CHAIN := 40               # (a lease chain is cut at least every 40 terms, so the look-back is bounded)
const SEASON_BLOCK := 24
const SEASON_MIN := 8
const P_PERM := 0.96
const P_SEASON := 0.88
const HOURS := Vector2(8.25, 18.5)   # vendors set up before 09:00 and pack up by 18:30
const K_NONE := 0
const K_PERM := 1
const K_SEASON := 2
const K_DAY := 3
const K_ISLANDER := 4
const KIND_NAMES := ["", "permanent", "season", "day", "islander"]

static var _loaded := false
static var _pool := {}               # market id -> {pids: PackedStringArray, cats: PackedInt32Array, n}
static var _of_pid := {}             # pid -> [market id, pool index]
static var _trip_of := {}            # pid -> [the market they make trips to, their chance a market day]
static var _cache := {}              # "local|id|day" / "open|id|day" -> roster
static var _cache_old := {}
const CACHE_MAX := 256
static var _mx := Mutex.new()
static var food_cat := 14


static func _load() -> void:
	if _loaded:
		return
	_mx.lock()
	if not _loaded:
		var d = DataFile.json(POOL)
		if d is Dictionary:
			food_cat = maxi(0, (d.get("categories", []) as Array).find("food"))
			for id in d.get("markets", {}):
				var e: Dictionary = d.markets[id]
				var pids := PackedStringArray(e.get("pids", []))
				var cats := PackedInt32Array(e.get("cats", []))
				_pool[id] = {"pids": pids, "cats": cats, "n": pids.size()}
				for i in pids.size():
					_of_pid[pids[i]] = [id, i]
				var tps := PackedStringArray(e.get("trippers", []))
				var tpp := PackedFloat32Array(e.get("trip_p", []))
				_pool[id]["trippers"] = tps
				_pool[id]["trip_p"] = tpp
				_pool[id]["trip_shard"] = PackedStringArray(e.get("trip_shard", []))
				for i in tps.size():
					_trip_of[tps[i]] = [id, tpp[i] if i < tpp.size() else 0.0]
		else:
			push_warning("FleaVendors: %s missing (tools/markets/bake_vendor_pool.py)" % POOL)
		_loaded = true
	_mx.unlock()


static func pool(id: String) -> Dictionary:
	_load()
	return _pool.get(id, {"pids": PackedStringArray(), "cats": PackedInt32Array(), "n": 0})


static func market_of(pid: String) -> String:
	_load()
	return str(_of_pid.get(pid, ["", -1])[0])


# -- leases -----------------------------------------------------------------------------------------------------

static func _lease(M: Dictionary, s: int, w: int) -> Array:
	## [pool index or -1, kind, since_week, term key] of stall s's lease in week w
	var hid := int(M.hid)
	var n := int(pool(str(M.id)).n)
	if n == 0:
		return [-1, K_NONE, w, 0]
	if int((M.perm as PackedByteArray)[s]) == 1:
		var off := int(FleaData.u(hid, s, 101) * PERM_WEEKS)
		var k := floori(float(w - off) / PERM_WEEKS)
		var j := k
		while j > k - PERM_CHAIN:
			if posmod(j, PERM_CHAIN) == 0 or FleaData.u(hid, s, 103, j) >= PERM_RENEW:
				break
			j -= 1
		var since := off + PERM_WEEKS * j
		if w == since:
			return [-1, K_NONE, since, j]                  # (the week after a lapse: the waiting list's head comes next week)
		return [int(FleaData.u(hid, s, 107, j) * n), K_PERM, since + 1, j]
	var off2 := int(FleaData.u(hid, s, 109) * SEASON_BLOCK)
	var b := floori(float(w - off2) / SEASON_BLOCK)
	var p := w - off2 - SEASON_BLOCK * b
	var L := SEASON_MIN + int(FleaData.u(hid, s, 113, b) * (SEASON_BLOCK - 2 * SEASON_MIN + 1))
	var term := 2 * b + (0 if p < L else 1)
	var since2 := off2 + SEASON_BLOCK * b + (0 if p < L else L)
	return [int(FleaData.u(hid, s, 127, term) * n), K_SEASON, since2, term]


static func _cat_of(M: Dictionary, s: int, who: int, salt: int) -> int:
	if int((M.kind as PackedByteArray)[s]) == FleaData.KIND_FOOD:
		return food_cat
	var mask := int((pool(str(M.id)).cats as PackedInt32Array)[who]) if who >= 0 else 0
	var bits: Array = []
	for b in 16:
		if mask & (1 << b):
			bits.append(b)
	if bits.is_empty():
		return 2
	return bits[mini(bits.size() - 1, int(FleaData.u(int(M.hid), s, salt, 151) * bits.size()))]


static func target(M: Dictionary, day: int) -> float:
	## the day's occupancy target T (the dawn resale fills up to it)
	var mo := int(StationCalendar.date(day).m)
	var r := FleaData.u(int(M.hid), day, 157)
	if mo >= 5 and mo <= 9:
		return 0.90 + 0.07 * r
	if mo == 12 or mo <= 2:
		return 0.80 + 0.06 * r
	return 0.85 + 0.08 * r


# -- rosters ----------------------------------------------------------------------------------------------------

static func _cached(key: String) -> Variant:
	_mx.lock()
	var r = _cache.get(key)
	if r == null and _cache_old.has(key):
		r = _cache_old[key]
		_cache[key] = r
	_mx.unlock()
	return r


static func _store(key: String, r: Dictionary) -> void:
	_mx.lock()
	if _cache.size() >= CACHE_MAX:
		_cache_old = _cache
		_cache = {}
	_cache[key] = r
	_mx.unlock()


static func local_roster(m, day: int) -> Dictionary:
	var M: Dictionary = m if m is Dictionary else FleaData.market(str(m))
	var key := "local|%s|%d" % [M.id, day]
	var got = _cached(key)
	if got != null:
		return got
	var n := (M.kind as PackedByteArray).size()
	var who := PackedInt32Array()
	who.resize(n)
	var kind := PackedByteArray()
	kind.resize(n)
	var cat := PackedByteArray()
	cat.resize(n)
	var since := PackedInt32Array()
	since.resize(n)
	var hid := int(M.hid)
	var w := StationCalendar.week(day)
	var used := {}
	var have := 0
	for s in n:
		who[s] = -1
		var L := _lease(M, s, w)
		if int(L[0]) < 0:
			continue
		var pres := P_PERM if int(L[1]) == K_PERM else P_SEASON
		if FleaData.u(hid, s, day, 131) >= pres or used.has(int(L[0])):
			continue
		used[int(L[0])] = true
		who[s] = int(L[0])
		kind[s] = int(L[1])
		since[s] = int(L[2])
		cat[s] = _cat_of(M, s, int(L[0]), int(L[3]) * 7 + 3)
		have += 1
	# the dawn resale: day vendors on the empty pitches, in a hashed order, up to the day's target
	var np := int(pool(str(M.id)).n)
	var goal := ceili(target(M, day) * n)
	if np > 0 and have < goal:
		var order: Array = []
		for s in n:
			if who[s] < 0:
				order.append([FleaData.u(hid, s, day, 137), s])
		order.sort()
		for o in order:
			if have >= goal:
				break
			var s: int = o[1]
			for k in 6:
				var c := int(FleaData.u(hid, s, day, 139 + k) * np)
				if not used.has(c):
					used[c] = true
					who[s] = c
					kind[s] = K_DAY
					since[s] = w
					cat[s] = _cat_of(M, s, c, day * 3 + 5)
					have += 1
					break
	var r := {"who": who, "kind": kind, "cat": cat, "since": since, "local": have, "n": n}
	_store(key, r)
	return r


static func _island_for(M: Dictionary, s: int, members: Array) -> int:
	## rendezvous hashing weighted by size: the raft member that holds stall s (stable as members come and go)
	var best := -1
	var bs := INF
	for e in members:
		var isl := FleaData.island(str(e.island))
		var wgt := 1.0 + float(isl.get("blocks", 3))
		var sc := -log(maxf(1e-12, FleaData.u(int(M.hid), s, int(isl.get("hid", 0)), 163))) / wgt
		if sc < bs:
			bs = sc
			best = int(isl.get("ix", -1))
	return best


static func roster(m, day: int) -> Dictionary:
	## the stalls open (held and staffed) on game day `day`
	var M: Dictionary = m if m is Dictionary else FleaData.market(str(m))
	var key := "open|%s|%d" % [M.id, day]
	var got = _cached(key)
	if got != null:
		return got
	var n := (M.kind as PackedByteArray).size()
	var members := FleaCalendar.members_at(M, day * 24.0 + 7.5)
	var local_open := FleaCalendar.market_open_day(M, day)
	var r: Dictionary
	if local_open:
		var lr := local_roster(M, day)
		r = {"who": (lr.who as PackedInt32Array).duplicate(), "kind": (lr.kind as PackedByteArray).duplicate(),
			"cat": (lr.cat as PackedByteArray).duplicate(), "since": lr.since, "local": lr.local, "n": n}
	else:
		var who := PackedInt32Array()
		who.resize(n)
		who.fill(-1)
		var z := PackedByteArray()
		z.resize(n)
		r = {"who": who, "kind": z, "cat": z.duplicate(), "since": PackedInt32Array(), "local": 0, "n": n}
	var isl_n := 0
	if not members.is_empty():
		var vac: Dictionary = r
		if not local_open:
			# Mon-Thu: the islanders keep the stalls empty on this week's Friday
			vac = local_roster(M, monday_of(day) + 4)
		var sky := FleaData.categories.find("sky")
		var vw: PackedInt32Array = vac.who
		var who2: PackedInt32Array = r.who
		var kind2: PackedByteArray = r.kind
		var cat2: PackedByteArray = r.cat
		for s in n:
			if vw[s] == -1:
				var ix := _island_for(M, s, members)
				if ix >= 0:
					who2[s] = -10 - ix
					kind2[s] = K_ISLANDER
					cat2[s] = maxi(0, sky)
					isl_n += 1
		r.who = who2
		r.kind = kind2
		r.cat = cat2
	r["islander"] = isl_n
	_store(key, r)
	return r


static func monday_of(day: int) -> int:
	return FleaCalendar.monday(StationCalendar.week(day))


static func occupancy(m, day: int) -> float:
	var r := local_roster(m, day)
	return float(r.local) / maxf(1.0, float(r.n))


static func islander_stalls(m, day: int) -> PackedInt32Array:
	var r := roster(m, day)
	var out := PackedInt32Array()
	var k: PackedByteArray = r.kind
	for s in k.size():
		if k[s] == K_ISLANDER:
			out.append(s)
	return out


static func tenant(m, stall: int, day: int) -> Dictionary:
	var M: Dictionary = m if m is Dictionary else FleaData.market(str(m))
	var r := roster(M, day)
	var k := int((r.kind as PackedByteArray)[stall])
	var w := int((r.who as PackedInt32Array)[stall])
	var out := {"pid": "", "kind": KIND_NAMES[k], "category": "", "since_week": -1, "island": ""}
	if k == K_NONE:
		return out
	var ci := int((r.cat as PackedByteArray)[stall])
	out.category = FleaData.categories[ci] if ci < FleaData.categories.size() else ""
	if k == K_ISLANDER:
		out.island = str(FleaData.islands()[-10 - w].id)
		return out
	out.pid = (pool(str(M.id)).pids as PackedStringArray)[w]
	var since: PackedInt32Array = r.since
	out.since_week = since[stall] if stall < since.size() else -1
	return out


static func vending(pid: String, day: int) -> Dictionary:
	## {market, stall, t0, t1} when this person keeps a stall today (a lease or a dawn pitch)
	_load()
	var e = _of_pid.get(pid)
	if e == null:
		return {}
	var M := FleaData.market(str(e[0]))
	if M.is_empty() or not FleaCalendar.market_open_day(M, day):
		return {}
	var r := roster(M, day)
	var who: PackedInt32Array = r.who
	var ix := int(e[1])
	var s := who.find(ix)
	if s < 0:
		return {}
	return {"market": M.id, "stall": s, "t0": HOURS.x, "t1": HOURS.y}


# -- trips to other towns' markets (00 §6.3; tools/markets/bake_vendor_pool.py "trippers") ---------------------------

static func trip_of(pid: String) -> Array:
	## [market id, chance a market day] of this person's usual out-of-town market, or []
	_load()
	return _trip_of.get(pid, [])


static func trip_today(pid: String, day: int) -> String:
	## the market this person goes to today ("" if none): their usual one, on its open days, with their chance (x2.5
	## toward a fair) -- the same draw NpcLife's market_trip and the destination's crowd make
	var t := trip_of(pid)
	if t.is_empty():
		return ""
	var M := FleaData.market(str(t[0]))
	if M.is_empty() or not M.get("sited", false) or not FleaCalendar.market_open_day(M, day):
		return ""
	var p := float(t[1])
	if FleaCalendar.in_service(M, day * 24.0 + 12.0) >= FleaCalendar.FAIR_N:
		p *= 2.5
	if FleaCalendar.is_holiday(M, day):
		p *= 3.0
	return str(M.id) if FleaData.u(NpcRng.fnv1a64(pid), day, 211) < p else ""


static func trippers_today(m, day: int) -> PackedStringArray:
	## who comes from other towns to market m today (before their own day's plans: the caller checks those)
	var M: Dictionary = m if m is Dictionary else FleaData.market(str(m))
	var out := PackedStringArray()
	if M.is_empty():
		return out
	var tps: PackedStringArray = pool(str(M.id)).get("trippers", PackedStringArray())
	for pid in tps:
		if trip_today(pid, day) == str(M.id):
			out.append(pid)
	return out


static func trip_shard(m, pid: String) -> String:
	var M: Dictionary = m if m is Dictionary else FleaData.market(str(m))
	var P: Dictionary = pool(str(M.get("id", "")))
	var tps: PackedStringArray = P.get("trippers", PackedStringArray())
	var i := tps.find(pid)
	var sh: PackedStringArray = P.get("trip_shard", PackedStringArray())
	return sh[i] if i >= 0 and i < sh.size() else ""
