extends RefCounted
class_name FleaCalendar

## The flea markets' calendar (research/flea_markets/00_plan.md §4, §5.1): which islands are booked to moor at which
## market and when, and what each market is doing at any hour. Pure: a function of (seed, market, day, hour) only, the
## same in any order and for markets nobody has loaded (the story engine can ask about next week).
##
##   FleaCalendar.state(m, day, hour)  -> {mode, phase, local_open, islander_open, gondolas, lot_lit, festoons,
##                                         moored, in_service, fair}
##     mode:   CLOSED (Mon-Thu, no island)   LOCAL (Fri-Sun 09-18)   ISLANDER (Mon-Thu with an island moored)
##             CELEBRATION (Bright Week: >= 5 islands; everything open daily, a lantern market to 21:00)
##             HOLIDAY (the Sky Holiday: >= 7 at a town or village; to 22:00; at most 3 days in a row)
##     phase:  CLOSED | AFTER_HOURS | SETUP | OPEN | LANTERN | TEARDOWN
##     gondolas: "none" | "passenger" (after hours: people only) | "all" (people and cargo)
##   FleaCalendar.week_plan(w)         -> every booking that begins in week w (all markets)
##   FleaCalendar.visits(m, w)         -> the bookings of market m that begin in week w
##   FleaCalendar.bookings_on(m, day)  -> the bookings of market m with an island there on that day
##   FleaCalendar.members_at(m, t)     -> the islands in SERVICE at absolute hour t (day * 24 + hour)
##   FleaCalendar.holiday(day)         -> [{market, town, towns, radius_m, days}]   (the Sky Holiday's area, 00 §6.4)
##   FleaCalendar.is_celebration(m, d) / is_holiday(m, d) / market_open_day(m, d)
##
## `m` is a market id ("FM-SOL") or its dict (FleaData). A booking is
##   {id, market, week, kind: ""|"great_fair"|"market_day", n, members: [{island, role: host|follower, ground: bool,
##    arrive, service, leave}]}   (times: absolute game hours from day 0 00:00; leave is a Monday 06:00)
##
## The model (00 §5.1, with the choices that make it pure; handoff_world.md "Decisions"):
##   - each week each market books a host island with p by tier (city 0.40, town 0.25, village 0.15; a city's Great
##     Fair week 1.0, a town's Market Day 0.8); the host arrives Wed 12:00 - Thu 18:00 and is in SERVICE 7 h 15 later;
##   - every island that reaches SERVICE draws one more with q (city 0.60, town 0.45, village 0.42; Great Fair 0.75;
##     Market Day town 0.60, village 0.55), arriving 6-36 h later, up to the Ten Knot's 10: P(N >= k) = q^(k-1);
##   - stays: 70 % leave the Monday 06:00 after their first weekend, 18 % after the second, 12 % after the third; no
##     island stays past 21 days, nor a follower past its host + 7 days; the market knot holds the raft together while
##     it grows (nobody casts off before the last member's first weekend is over);
##   - an island can moor once in any 4 weeks: island i is free to be booked in week w when (w + phase_i) % 4 == 0
##     (phase_i hashed): 25 islands a week, and no island is ever booked at two markets at once.

const HOST_P := {"city": 0.40, "town": 0.25, "village": 0.15}
const CHAIN_Q := {"city": 0.60, "town": 0.45, "village": 0.42}
const FAIR_P := 1.0
const FAIR_Q := 0.75
const MDAY_P := 0.8
const MDAY_Q := {"city": 0.60, "town": 0.60, "village": 0.55}
const MAX_RAFT := 10
const SERVICE_H := 7.25          # arrival -> SERVICE: hold, crew down, anchor, logistics, rigging (00 §5.2)
const GAP_H := Vector2(6.0, 36.0)
const PHASES := 4
const STAY := [0.70, 0.88]       # cumulative: one weekend, two, (else) three
const MAX_STAY_H := 21.0 * 24.0
const FOLLOWER_PAST_HOST_H := 7.0 * 24.0
const FAIR_N := 3
const BRIGHT_N := 5
const HOLIDAY_N := 7
const HOLIDAY_MAX_DAYS := 3
const HOLIDAY_R := 8000.0
const LAW := "res://remake/law/settlements.json"

static var _plans := {}          # week -> [booking]
static var _plans_old := {}
const PLANS_MAX := 64
static var _mx := Mutex.new()
static var _towns: Array = []    # [{name, tier, centre}] (law settlements)


static func _m(m) -> Dictionary:
	return m if m is Dictionary else FleaData.market(str(m))


static func monday(w: int) -> int:
	## the game day of week w's Monday (StationCalendar.week: the start's week is 0)
	return 7 * w - int(StationCalendar.start().wd)


static func _mon_after(t: float) -> float:
	## the Monday 06:00 that ends the first weekend at or after absolute hour t (a weekend ends Sunday 18:00)
	var d := floori(t / 24.0)
	var wd := StationCalendar.weekday(d)
	var w := StationCalendar.week(d)
	var late := wd == 6 and t - d * 24.0 >= 18.0
	return float(monday(w + (2 if late else 1))) * 24.0 + 6.0


# -- special weeks ----------------------------------------------------------------------------------------------

static func special(m, w: int) -> String:
	## "great_fair" (a city's, in its month's second weekend), "market_day" (a town's or village's own weekend, once a
	## year: its month fixed, May-Sep; the weekend hashed by year) or ""
	var M := _m(m)
	var sat := monday(w) + 5
	var dt := StationCalendar.date(sat)
	var d := int(dt.d)
	if int(M.get("great_fair_month", 0)) == int(dt.m) and d >= 8 and d <= 14:
		return "great_fair"
	if str(M.get("tier", "")) != "city":
		var hid := int(M.hid)
		var mon := 5 + int(FleaData.u(hid, 7) * 5.0)
		var k := 1 + int(FleaData.u(hid, int(dt.y), 9) * 4.0)
		if int(dt.m) == mon and d >= 7 * (k - 1) + 1 and d <= 7 * k:
			return "market_day"
	return ""


# -- the week's bookings ----------------------------------------------------------------------------------------

static func week_plan(w: int) -> Array:
	_mx.lock()
	var got = _plans.get(w)
	if got == null and _plans_old.has(w):
		got = _plans_old[w]
		_plans[w] = got
	_mx.unlock()
	if got != null:
		return got
	var out := _plan(w)
	_mx.lock()
	if _plans.size() >= PLANS_MAX:
		_plans_old = _plans
		_plans = {}
	_plans[w] = out
	_mx.unlock()
	return out


static func _plan(w: int) -> Array:
	var isl := FleaData.islands()
	var free: Array = []
	for i in isl:
		if posmod(w + int(FleaData.u(int(i.hid), 11) * PHASES), PHASES) == 0:
			free.append(i)
	var used := {}
	var order: Array = []
	for M in FleaData.markets():
		var sp := special(M, w)
		order.append([0 if sp != "" else 1, FleaData.u(int(M.hid), w, 13), M, sp])
	order.sort_custom(func(a, b): return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1]))
	var out: Array = []
	for o in order:
		var M: Dictionary = o[2]
		var sp: String = o[3]
		var hid := int(M.hid)
		var tier := str(M.tier)
		var p: float = FAIR_P if sp == "great_fair" else (MDAY_P if sp == "market_day" else float(HOST_P.get(tier, 0.15)))
		var q: float = FAIR_Q if sp == "great_fair" else (float(MDAY_Q.get(tier, 0.55)) if sp == "market_day" else float(CHAIN_Q.get(tier, 0.42)))
		if FleaData.u(hid, w, 17) >= p:
			continue
		var host := _pick(free, used, true, FleaData.u(hid, w, 19))
		if host.is_empty():
			continue                                     # (every free island is out already: the booking falls through)
		var ids: Array = [host]
		while ids.size() < MAX_RAFT and FleaData.u(hid, w, 23, ids.size()) < q:
			var f := _pick(free, used, false, FleaData.u(hid, w, 29, ids.size()))
			if f.is_empty():
				break
			ids.append(f)
		out.append(_times(M, w, sp, ids))
	return out


static func _pick(free: Array, used: Dictionary, host: bool, r: float) -> Dictionary:
	var c: Array = []
	for i in free:
		if not used.has(i.id) and (not host or bool(i.eligible)):
			c.append(i)
	if c.is_empty():
		return {}
	var got: Dictionary = c[mini(c.size() - 1, int(r * c.size()))]
	used[got.id] = true
	return got


static func _times(M: Dictionary, w: int, sp: String, ids: Array) -> Dictionary:
	var hid := int(M.hid)
	var base := float(monday(w)) * 24.0
	var mem: Array = []
	var a := base + 60.0 + FleaData.u(hid, w, 31) * 30.0           # Wed 12:00 .. Thu 18:00
	var ground_n := int((M.get("mooring_tier", {}) as Dictionary).get("ground_islands", 3))
	for k in ids.size():
		if k > 0:
			a = float(mem[k - 1].service) + GAP_H.x + FleaData.u(hid, w, 37, k) * (GAP_H.y - GAP_H.x)
		var r := FleaData.u(hid, w, 41, k)
		var wk := 1 if r < STAY[0] else (2 if r < STAY[1] else 3)
		mem.append({"island": ids[k].id, "role": "host" if k == 0 else "follower", "ground": k < ground_n,
			"arrive": a, "service": a + SERVICE_H, "leave": _mon_after(a) + (wk - 1) * 168.0})
	# the market knot: a raft big enough for a Bright Week holds together while it grows (nobody casts off before the
	# last member's first weekend is over); smaller rafts come together inside a weekend anyway
	var hold := _mon_after(float(mem[-1].arrive)) if mem.size() >= BRIGHT_N else 0.0
	for k in mem.size():
		var e: Dictionary = mem[k]
		var lv := maxf(float(e.leave), hold)
		while lv > float(e.arrive) + MAX_STAY_H:
			lv -= 168.0
		if k > 0:
			while lv > float(mem[0].leave) + FOLLOWER_PAST_HOST_H:
				lv -= 168.0
		e.leave = lv
	return {"id": "%s/w%d" % [M.id, w], "market": M.id, "week": w, "kind": sp, "n": mem.size(), "members": mem}


static func visits(m, w: int) -> Array:
	var id := str(_m(m).get("id", ""))
	var out: Array = []
	for b in week_plan(w):
		if b.market == id:
			out.append(b)
	return out


static func bookings_on(m, day: int) -> Array:
	## bookings with an island at the market (arrived, not yet gone) at some time of game day `day`
	var id := str(_m(m).get("id", ""))
	var t0 := day * 24.0
	var out: Array = []
	var w := StationCalendar.week(day)
	for ww in range(w - PHASES, w + 1):
		for b in week_plan(ww):
			if b.market != id:
				continue
			for e in b.members:
				if float(e.arrive) < t0 + 24.0 and float(e.leave) > t0:
					out.append(b)
					break
	return out


static func members_at(m, t: float) -> Array:
	## the islands in SERVICE (anchored, gondolas running) at absolute hour t, in arrival order
	var day := floori(t / 24.0)
	var out: Array = []
	for b in bookings_on(m, day):
		for e in b.members:
			if float(e.service) <= t and t < float(e.leave):
				out.append(e)
	return out


static func present_at(m, t: float) -> Array:
	## every island at the market at t, from its arrival (approach, anchoring) to its departure
	var day := floori(t / 24.0)
	var out: Array = []
	for b in bookings_on(m, day):
		for e in b.members:
			if float(e.arrive) <= t and t < float(e.leave):
				out.append(e)
	return out


static func in_service(m, t: float) -> int:
	return members_at(m, t).size()


# -- the day's mode ---------------------------------------------------------------------------------------------

static func is_celebration(m, day: int) -> bool:
	## Bright Week: >= 5 islands in SERVICE at the day's SETUP (07:30)
	return in_service(m, day * 24.0 + 7.5) >= BRIGHT_N


static func _holiday_qual(M: Dictionary, day: int) -> bool:
	return str(M.get("tier", "")) != "city" and in_service(M, day * 24.0 + 6.0) >= HOLIDAY_N


static func is_holiday(m, day: int) -> bool:
	## the Sky Holiday: a town or village market opening with >= 7 in SERVICE at 06:00, the first 3 days of such a run
	var M := _m(m)
	if M.is_empty() or not _holiday_qual(M, day):
		return false
	var run := 1
	for k in range(1, HOLIDAY_MAX_DAYS + 1):
		if not _holiday_qual(M, day - k):
			break
		run += 1
	return run <= HOLIDAY_MAX_DAYS


static func market_open_day(m, day: int) -> bool:
	## the local booths open today (Fri-Sun, and every day of a Bright Week or a Sky Holiday)
	return StationCalendar.weekday(day) >= 4 or is_celebration(m, day) or is_holiday(m, day)


static func state(m, day: int, hour: float) -> Dictionary:
	var M := _m(m)
	var t := day * 24.0 + hour
	var hol := is_holiday(M, day)
	var cel := not hol and is_celebration(M, day)
	var local_day := StationCalendar.weekday(day) >= 4
	var islanders := in_service(M, day * 24.0 + 7.5) > 0 or (in_service(M, t) > 0 and hour >= 9.0)
	var mode := "CLOSED"
	if hol:
		mode = "HOLIDAY"
	elif cel:
		mode = "CELEBRATION"
	elif local_day:
		mode = "LOCAL"
	elif islanders:
		mode = "ISLANDER"
	var close := 18.0
	var lantern_end := 18.0
	if mode == "CELEBRATION":
		lantern_end = 21.0
	elif mode == "HOLIDAY":
		lantern_end = 22.0
	var phase := "CLOSED"
	if mode != "CLOSED":
		if hour < 7.5:
			phase = "AFTER_HOURS"
		elif hour < 9.0:
			phase = "SETUP"
		elif hour < close:
			phase = "OPEN"
		elif hour < lantern_end:
			phase = "LANTERN"
		elif hour < lantern_end + 1.0:
			phase = "TEARDOWN"
		else:
			phase = "AFTER_HOURS"
	var n := in_service(M, t)
	var gond := "none"
	if n > 0:
		# people round the clock; cargo 07:00-19:00 (02 #8), and through a lantern market's evening
		gond = "all" if (hour >= 7.0 and hour < maxf(19.0, lantern_end)) else "passenger"
	var fest := "security"
	if n > 0 or mode in ["CELEBRATION", "HOLIDAY"] or phase in ["SETUP", "OPEN", "LANTERN", "TEARDOWN"]:
		fest = "all"
	return {"mode": mode, "phase": phase,
		"local_open": phase == "OPEN" and mode in ["LOCAL", "CELEBRATION", "HOLIDAY"],
		"islander_open": islanders and phase in ["OPEN", "LANTERN"],
		"gondolas": gond, "lot_lit": hour < 6.5 or hour >= 19.0, "festoons": fest,
		"moored": present_at(M, t).size() > 0, "in_service": n, "fair": n >= FAIR_N}


# -- the Sky Holiday's area -------------------------------------------------------------------------------------

static func _load_towns() -> void:
	if not _towns.is_empty():
		return
	var d = DataFile.json(LAW)
	if d is Dictionary:
		for s in d.get("settlements", []):
			_towns.append({"name": s.name, "tier": s.tier, "centre": Vector2(float(s.centre[0]), float(s.centre[1]))})


static func holiday(day: int) -> Array:
	## [{market, town, towns: [the settlements declared: the host and every non-city within 8 km], cities_near: [...],
	##   radius_m, days: [the run's holiday days]}]
	_load_towns()
	var out: Array = []
	for M in FleaData.markets():
		if not is_holiday(M, day):
			continue
		var c := FleaData.centre(M)
		var towns: Array = [M.town]
		var cities: Array = []
		for t in _towns:
			if t.name == M.town:
				continue
			var d := Vector2(StationGeo.wrap_ds(float(t.centre.x) - c.x), float(t.centre.y) - c.y).length()
			if d <= HOLIDAY_R:
				if str(t.tier) == "city":
					cities.append(t.name)
				else:
					towns.append(t.name)
		var days: Array = []
		var d0 := day
		while d0 > day - HOLIDAY_MAX_DAYS and is_holiday(M, d0 - 1):
			d0 -= 1
		var dd := d0
		while is_holiday(M, dd):
			days.append(dd)
			dd += 1
		out.append({"market": M.id, "town": M.town, "towns": towns, "cities_near": cities, "radius_m": HOLIDAY_R, "days": days})
	return out


# -- for NpcLife (pure, cached by day) ---------------------------------------------------------------------------

static var _trip_cache := {}


static func trip_weights(day: int) -> Array:
	## [[market id, stalls, centre (Vector2 s, x), fair 0/1, draw tags]] of the sited markets on game day `day`
	## (NpcLife's market_trip gravity choice, 00 §6.3)
	_mx.lock()
	var got = _trip_cache.get(day)
	_mx.unlock()
	if got != null:
		return got
	var out: Array = []
	for M in FleaData.markets():
		if not M.get("sited", false):
			continue
		var fair := 1.0 if in_service(M, day * 24.0 + 12.0) >= FAIR_N else 0.0
		out.append([M.id, (M.kind as PackedByteArray).size(), FleaData.centre(M), fair, M.get("draw", [])])
	_mx.lock()
	if _trip_cache.size() > 16:
		_trip_cache.clear()
	_trip_cache[day] = out
	_mx.unlock()
	return out


static func visit_boost(m, day: int) -> float:
	## the home market's pull on a day (00 §6.1, §6.4): a fair x2.5, a Bright Week x2 more, a Sky Holiday x3 more
	var M := _m(m)
	if M.is_empty():
		return 1.0
	var k := 1.0
	var n := in_service(M, day * 24.0 + 12.0)
	if n >= FAIR_N:
		k *= 2.5
	if is_holiday(M, day):
		k *= 3.0
	elif n >= BRIGHT_N:
		k *= 2.0
	return k


# -- the Sky Holiday in people's days (00 §6.4) ------------------------------------------------------------------

## the trades that keep working on a Sky Holiday: hospital, care, police and fire, transit, the utilities and charging,
## food and drink, lodging, farm chores
const ESSENTIAL_TYPES := ["hospital", "care_home", "police_fire", "transit_depot", "transit_station", "life_support_plant",
	"water_works", "power_station", "charge_stop", "hotel", "motel", "farm", "port", "flea_stall", "flea_office"]
const ESSENTIAL_CATS := ["food", "drink", "lodging"]
const HOLIDAY_TRIP_R := 25000.0
static var _hol_cache := {}


static func holiday_list(day: int) -> Array:
	## holiday(day) with each area's towns as a set and its centre (cached by day)
	_mx.lock()
	var got = _hol_cache.get(day)
	_mx.unlock()
	if got != null:
		return got
	var out: Array = []
	for h in holiday(day):
		var towns := {}
		for t in h.towns:
			towns[t] = true
		out.append({"market": h.market, "towns": towns, "centre": FleaData.centre(FleaData.market(h.market))})
	_mx.lock()
	if _hol_cache.size() > 32:
		_hol_cache.clear()
	_hol_cache[day] = out
	_mx.unlock()
	return out


static func holiday_at(town: String, at: Vector2, day: int) -> String:
	## the market whose Sky Holiday covers this place today ("" if none): its towns, and the farms and country within
	## 8 km of it
	for h in holiday_list(day):
		if (h.towns as Dictionary).has(town):
			return str(h.market)
		if (town == "" or town == "_country") and NpcPlaces.dist(at, h.centre) <= HOLIDAY_R:
			return str(h.market)
	return ""


static func holiday_near(at: Vector2, day: int) -> String:
	## a Sky Holiday within 25 km (the trips toward it, x3)
	for h in holiday_list(day):
		if NpcPlaces.dist(at, h.centre) <= HOLIDAY_TRIP_R:
			return str(h.market)
	return ""


static func essential(t: Dictionary, type_id: String) -> bool:
	return type_id in ESSENTIAL_TYPES or str(t.get("category", "")) in ESSENTIAL_CATS
