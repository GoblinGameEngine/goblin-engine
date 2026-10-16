extends RefCounted
class_name SkyMooring

## The sky side of the flea-market moorings (research/flea_markets/00_plan.md §5; handoff_sky.md): the islands
## FleaCalendar books to a market are steered to its mooring field, come down to MOOR_H, hold there while they are
## moored, lash into a raft and cast off when their stay is over.  SkyDrift owns one (drift.mooring) and calls drive()
## every step; the rafts it drives are left out of the free drift, the meetings, the cast-offs and the wander.
##
## Pure in what matters: who comes, when and for how long is FleaCalendar's (seed, market, week); where each member
## hangs, which of its gondola stations runs to which ground station and which line house drops hawsers to which
## deadman is layout(booking) -- a function of the booking and the data (remake/sky/moorings.json, the warren
## generator's; remake/markets/flea_markets.json, MARKETS-WORLD's).  Only the approach is stateful (an island flies
## from wherever the free drift left it).
##
## Phases of a member (game hours from its arrival A; 00 §5.2):
##   TRIM      A - 24 .. A - 6   alone (cast off from any raft), flying for its berth at the drift's pace
##   APPROACH  A - 6 .. A        and coming down to MOOR_H
##   HOLD 0 .. 0:20  CREW_DOWN .. 0:45  ANCHOR .. 2:15  LOGISTICS .. 4:15  RIGGING .. 7:15  SERVICE .. leave - 12
##   STRIKE    leave - 12 .. leave      CAST_OFF leave .. leave + 0.5 (the crew up, the hawsers slipped: then free)
## A follower that does not make fast to the ground (k >= the tier's ground_islands) lashes to its layout parent at A
## and skips CREW_DOWN .. RIGGING (it is "LASHED", then SERVICE: its people cross by the bridges).
##
##   members                   drift island index -> state {booking, k, market, phase, ground, ...}
##   phase_of(i) / is_moored(i) / at_market(id)
##   layout(booking)           {members: [{island, off (east, south m from the booking origin), station, gstation,
##                              hawsers, davit, parent, side, along_a, along_b, absent}], origin (s, x), M}
##   wind_at                   Callable(s, x) -> m/s (SkyIslands: the storms); over WIND_LIMIT the gondolas stop and an
##                              island holds its height

const MOOR_H := 600.0
const TRIM_H := 24.0
const DESCENT_H := 6.0
const CAST_H := 0.5
const H_OFF := 40.0                  # m: a ground station lies this far out from under its island station's berths
const MAX_ROPE_H := 300.0            # m: the farthest a follower's ropeway reaches out (else hawsers and bridges only)
const VMAX := 45.0                   # m/s, a trimming island at most (most fly at the drift's 4-9)
const WIND_LIMIT := 9.0              # m/s at 700 m (00 §5.3)
const NO_OVER := 20.0                # m round the market floor no island hangs over
const REFRESH := 2.0                 # s between calendar looks
const HOUR_S := 120.0                # real s a game hour (DaySkySystem.DAY_LENGTH_SECONDS / 24, at load)
const MOORINGS := "res://remake/sky/moorings.json"
const PH := {"HOLD": 0.0, "CREW_DOWN": 1.0 / 3.0, "ANCHOR": 0.75, "LOGISTICS": 2.25, "RIGGING": 4.25, "SERVICE": 7.25}
const ORDER := ["HOLD", "CREW_DOWN", "ANCHOR", "LOGISTICS", "RIGGING", "SERVICE"]
const HAWSERS := {"city": 4, "town": 3, "village": 3}

var now_h := 0.0                     # absolute game hours (SkyIslands sets it before each step)
var members := {}                    # island index -> state
var moor := {}                       # island id -> [mooring dict]
var by_id := {}                      # island id -> drift index
var wind_at: Callable
var snapped: Array = []              # islands placed by a jump this step (SkyIslands: no easing for them)
var log_events: Array = []           # [hour, island id, phase] for the tests / the story engine
var _layouts := {}
var _t := 0.0
var _last_now := -1.0e9
var _wind := {}                      # market id -> m/s (refreshed with the calendar)
var _t2 := 0.0
var _held_last := {}
var _act: Array = []                 # member indices whose raft still moves every step (TRIM / APPROACH / descending)


func setup(drift: SkyDrift) -> void:
	var d = DataFile.json(MOORINGS)
	if d is Dictionary:
		moor = (d as Dictionary).get("islands", {})
	for i in drift.islands.size():
		by_id[drift.islands[i].id] = i


# ------------------------------------------------------------------ queries
func phase_of(i: int) -> String:
	var st: Dictionary = members.get(i, {})
	return str(st.get("phase", ""))


func is_moored(i: int) -> bool:
	## down at a market or on its way down (banners furl, the hoists keep still)
	var p := phase_of(i)
	return p != "" and p != "TRIM"


func at_market(market_id: String) -> Array:
	var out: Array = []
	for i in members:
		if str(members[i].market) == market_id:
			out.append(i)
	return out


func markets() -> Dictionary:
	## market id -> [island index] of every market with an island booked there now (trimming included)
	var out := {}
	for i in members:
		var m := str(members[i].market)
		if not out.has(m):
			out[m] = []
		out[m].append(i)
	return out


func wind(market_id: String) -> float:
	return float(_wind.get(market_id, 5.0))


static func phase_at(e: Dictionary, ground: bool, t: float) -> String:
	var a := float(e.arrive)
	var lv := float(e.leave)
	if t < a - TRIM_H or t >= lv + CAST_H:
		return ""
	if t >= lv:
		return "CAST_OFF"
	if t < a - DESCENT_H:
		return "TRIM"
	if t < a:
		return "APPROACH"
	if t >= lv - 12.0 and t >= float(e.service):
		return "STRIKE"
	var dt := t - a
	if not ground:
		return "SERVICE" if dt >= PH.SERVICE else ("HOLD" if dt < PH.CREW_DOWN else "LASHED")
	var ph := "HOLD"
	for p in ORDER:
		if dt >= float(PH[p]):
			ph = p
	return ph


# ------------------------------------------------------------------ the layout (pure)
func layout(b: Dictionary, drift: SkyDrift) -> Dictionary:
	var key := str(b.id)
	if _layouts.has(key):
		return _layouts[key]
	var L := _make_layout(b, drift)
	if _layouts.size() > 64:
		_layouts.erase(_layouts.keys()[0])      # (FIFO: the oldest booking goes; never clear() -- recomputing every
	_layouts[key] = L                           # active layout in one refresh cost 10+ ms a step on long runs)
	return L


static func _k(h: float) -> float:
	return StationGeo.R / (StationGeo.R - h)


static func _uv(M: Dictionary, s: float, x: float) -> Vector2:
	## (s, x) on the ring -> the market's site frame (u, v)
	var f: Dictionary = M.get("frame", {})
	var a := float(f.get("yaw", 0.0))
	var ds := StationGeo.wrap_ds(s - float(f.get("s", 0.0)))
	var dx := x - float(f.get("x", 0.0))
	return Vector2(ds * cos(a) + dx * sin(a), -ds * sin(a) + dx * cos(a))


static func _ex(lp: Array) -> Vector2:
	## an island-frame point [x, y, z] -> deck metres (east, south)
	return Vector2(-float(lp[2]), float(lp[0]))


func _rect(i: int, drift: SkyDrift) -> Rect2:
	## the island's deck in deck metres (east, south) about its centre
	var n: Dictionary = drift.islands[i].n
	return Rect2(-float(n.W), -float(n.N), float(n.W) + float(n.E), float(n.N) + float(n.S))


func _over_floor(M: Dictionary, origin: Vector2, off: Vector2, i: int, drift: SkyDrift) -> float:
	## how much of the island (at origin + off, deck metres) hangs over the market floor + NO_OVER: the share of a
	## 9 x 9 sample of its deck inside the floor's rectangle
	var fl: Array = M.get("floor", [])
	if fl.size() < 3:
		return 0.0
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for p in fl:
		lo = Vector2(minf(lo.x, float(p[0])), minf(lo.y, float(p[1])))
		hi = Vector2(maxf(hi.x, float(p[0])), maxf(hi.y, float(p[1])))
	lo -= Vector2(NO_OVER, NO_OVER)
	hi += Vector2(NO_OVER, NO_OVER)
	var r := _rect(i, drift)
	var k := _k(MOOR_H)
	var hit := 0
	for a in 9:
		for c in 9:
			var e := r.position.x + r.size.x * a / 8.0 + off.x
			var so := r.position.y + r.size.y * c / 8.0 + off.y
			var uv := _uv(M, origin.x + e * k, origin.y + so)
			if uv.x > lo.x and uv.x < hi.x and uv.y > lo.y and uv.y < hi.y:
				hit += 1
	return hit / 81.0


func _stations(iid: String, kinds := ["pax"]) -> Array:
	var out: Array = []
	for m in moor.get(iid, []):
		if str(m.kind) in kinds:
			out.append(m)
	return out


func _tip(st: Dictionary) -> Vector2:
	## the station's two berths' rope exits, their middle, in deck metres (east, south) about the island centre
	var an: Dictionary = st.get("anchors", {})
	var a: Array = an.get("rope_exit_0", st.origin)
	var b: Array = an.get("rope_exit_1", a)
	return (_ex(a) + _ex(b)) * 0.5


func _make_layout(b: Dictionary, drift: SkyDrift) -> Dictionary:
	var M := FleaData.market(str(b.market))
	var out := {"M": M, "members": [], "origin": Vector2.ZERO, "id": b.id}
	if M.is_empty() or not M.get("sited", false):
		return out
	var tier := str(M.get("tier", "village"))
	var k := _k(MOOR_H)
	# ground stations and deadmen on the ring
	var gs: Array = []
	for g in M.get("stations", []):
		gs.append(FleaData.to_world(M, float(g[0]), float(g[1])))
	var dms: Array = []
	for d in M.get("deadmen", []):
		dms.append(FleaData.to_world(M, float(d[0]), float(d[1])))
	var masts: Array = []
	for mp in M.get("masts", []):
		masts.append(FleaData.to_world(M, float(mp[0]), float(mp[1])))
	var g_used := {}
	var d_used := {}
	var placed: Array = []           # [{i, off, faces_used {side: true}}]
	var rope_faces := {}             # island index -> side its ropeway hangs from (no lashing there)
	for kk in (b.members as Array).size():
		var e: Dictionary = b.members[kk]
		var iid := str(e.island)
		var rec := {"island": iid, "i": int(by_id.get(iid, -1)), "k": kk, "ground": bool(e.ground), "absent": false,
			"station": {}, "gstation": Vector2.INF, "gyaw": 0.0, "hawsers": [], "davit": [], "parent": -1, "off": Vector2.ZERO}
		var i: int = rec.i
		if i < 0:
			rec.absent = true
			out.members.append(rec)
			continue
		if kk == 0:
			# the host: one of its passenger stations over a ground station, hung clear of the floor; the origin is its
			# centre on the ring
			var best := []
			var cands := _stations(iid, ["pax"])
			if cands.is_empty():
				cands = _stations(iid, ["cargo"])
			for st in cands:
				var n := _ex(st.out)
				var tip := _tip(st)
				for gi in gs.size():
					var G: Vector2 = gs[gi]
					# (further out from under the berths only if the island would hang over the floor: a longer
					# slant to the plinth)
					for ho in [H_OFF, H_OFF * 2.5, H_OFF * 5.0]:
						var c := Vector2(fposmod(G.x - n.x * float(ho) - tip.x * k, StationGeo.CIRC), G.y - (n.y * float(ho) + tip.y))
						var over := _over_floor(M, c, Vector2.ZERO, i, drift)
						var Tt := Vector2(c.x + tip.x * k, c.y + tip.y)
						var sc := over * 1000.0 + gi * 2.0 + float(ho) * 0.05 + (500.0 if _rope_over_floor(M, Tt, G) else 0.0)
						if best.is_empty() or sc < float(best[0]):
							best = [sc, st, gi, c]
						if over == 0.0 and sc < 400.0:
							break
			if best.is_empty():
				# (no station at all: over the field's middle, hawsers only)
				var mf: Array = M.get("mooring", [])
				var cc := Vector2.ZERO
				for p in mf:
					cc += Vector2(float(p[0]), float(p[1]))
				cc /= maxf(1.0, mf.size())
				out.origin = FleaData.to_world(M, cc.x, cc.y)
			else:
				out.origin = best[3]
				rec.station = best[1]
				rec.gstation = gs[best[2]]
				g_used[best[2]] = true
				rope_faces[kk] = str(best[1].side)
			placed.append({"k": kk, "i": i, "off": Vector2.ZERO, "used": {}})
		else:
			var pl := _berth_for(i, placed, drift, M, out.origin, rope_faces)
			if pl.is_empty():
				rec.absent = true                     # (no free face clear of the floor: it doesn't come)
				out.members.append(rec)
				continue
			rec.off = pl.off
			rec.parent = pl.parent_k
			rec.side = pl.side
			rec.along_a = pl.along_a
			rec.along_b = pl.along_b
			placed.append({"k": kk, "i": i, "off": pl.off, "used": {SkyDrift._opp(pl.side): true}})
			for q in placed:
				if q.k == pl.parent_k:
					q.used[pl.side] = true
			if rec.ground:
				# its ropeway: a passenger station not on its lashed face, to the nearest free ground station in front of it
				var bestg := []
				for st in _stations(iid, ["pax"]):
					if str(st.side) == SkyDrift._opp(pl.side):
						continue
					var n := _ex(st.out)
					var tip: Vector2 = _tip(st) + (pl.off as Vector2)
					var T := Vector2(out.origin.x + tip.x * k, out.origin.y + tip.y)
					for gi in gs.size():
						if g_used.has(gi):
							continue
						var G: Vector2 = gs[gi]
						var dv := Vector2(StationGeo.wrap_ds(G.x - T.x) / k, G.y - T.y)
						if dv.dot(n) <= 0.0 or dv.length() > MAX_ROPE_H or _rope_over_floor(M, T, G):
							continue
						if bestg.is_empty() or dv.length() < bestg[0]:
							bestg = [dv.length(), st, gi]
				if not bestg.is_empty():
					rec.station = bestg[1]
					rec.gstation = gs[bestg[2]]
					g_used[bestg[2]] = true
					rope_faces[kk] = str(bestg[1].side)
				else:
					# (no listed plinth in reach: one set straight under its berths, if that is open market ground)
					for st in _stations(iid, ["pax"]):
						if str(st.side) == SkyDrift._opp(pl.side):
							continue
						var Gs := _under(M, st, pl.off, out.origin)
						if Gs.is_finite():
							rec.station = st
							rec.gstation = Gs
							rope_faces[kk] = str(st.side)
							break
		# the hawsers: its share of the deadmen, nearest each line house (the host also to the masts' heads)
		if rec.ground:
			var share: int = HAWSERS.get(tier, 3)
			var lines := _stations(iid, ["line"])
			if lines.is_empty():
				lines = _stations(iid, ["pax", "cargo"])
			for h in share:
				if lines.is_empty():
					break
				var ln: Dictionary = lines[h % lines.size()]
				var an: Array = ln.get("anchors", {}).get("hawser", ln.get("anchors", {}).get("rope_exit_0", ln.origin))
				var p: Vector2 = _ex(an) + (rec.off as Vector2)
				var P := Vector2(out.origin.x + p.x * k, out.origin.y + p.y)
				var bd := INF
				var bi := -1
				for di in dms.size():
					if d_used.has(di):
						continue
					var dd := Vector2(StationGeo.wrap_ds(dms[di].x - P.x) / k, dms[di].y - P.y).length()
					if dd < bd:
						bd = dd
						bi = di
				if bi < 0:
					break
				d_used[bi] = true
				rec.hawsers.append({"from": an, "to": dms[bi], "mast": false})
			if kk == 0:
				for mp in masts:
					if lines.is_empty():
						break
					var ln2: Dictionary = lines[0]
					var an2: Array = ln2.get("anchors", {}).get("hawser", ln2.origin)
					rec.hawsers.append({"from": an2, "to": mp, "mast": true})
			# the drop cage's davit (beside the first passenger station), else the station's own berth
			for dv in _stations(iid, ["davit"]):
				rec.davit = dv.get("anchors", {}).get("hook", [])
				break
			if (rec.davit as Array).is_empty() and not (rec.station as Dictionary).is_empty():
				rec.davit = (rec.station as Dictionary).get("anchors", {}).get("pivot_0", [])
		# its cargo ropeway: a cargo station whose berths hang over open market ground (the field, the apron)
		rec["cargo"] = {}
		if rec.ground:
			for st in _stations(iid, ["cargo"]):
				if kk > 0 and str(st.side) == SkyDrift._opp(str(rec.get("side", ""))):
					continue
				var Gc := _under(M, st, rec.off, out.origin)
				if Gc.is_finite():
					var tipc: Vector2 = _tip(st) + (rec.off as Vector2)
					var Tc := Vector2(out.origin.x + tipc.x * k, out.origin.y + tipc.y)
					rec.cargo = {"station": st, "gstation": Gc,
						"gyaw": atan2(StationGeo.wrap_ds(Tc.x - Gc.x), Tc.y - Gc.y)}
					break
		if not (rec.station as Dictionary).is_empty():
			# the ground station's +x points at the island's berths (its rope exits face the span)
			var tip2: Vector2 = _tip(rec.station) + (rec.off as Vector2)
			var T2 := Vector2(out.origin.x + tip2.x * k, out.origin.y + tip2.y)
			var G2: Vector2 = rec.gstation
			rec.gyaw = atan2(StationGeo.wrap_ds(T2.x - G2.x), T2.y - G2.y)
		out.members.append(rec)
	return out


static func _rope_over_floor(M: Dictionary, T: Vector2, G: Vector2) -> bool:
	## does a span from the berths (T, ring s/x) down to its plinth (G) pass over the market floor (+ 10 m)?
	var fl: Array = M.get("floor", [])
	if fl.size() < 3:
		return false
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for p in fl:
		lo = Vector2(minf(lo.x, float(p[0])), minf(lo.y, float(p[1])))
		hi = Vector2(maxf(hi.x, float(p[0])), maxf(hi.y, float(p[1])))
	lo -= Vector2(10.0, 10.0)
	hi += Vector2(10.0, 10.0)
	var a := _uv(M, T.x, T.y)
	var b := _uv(M, G.x, G.y)
	for k in 33:
		var q := a.lerp(b, k / 32.0)
		if q.x > lo.x and q.x < hi.x and q.y > lo.y and q.y < hi.y:
			return true
	return false


func _under(M: Dictionary, st: Dictionary, off: Vector2, origin: Vector2) -> Vector2:
	## a ground station's spot H_OFF out from under a station's berths -- if that is on the mooring field or an apron
	## (never the floor, the lot or outside the site), else Vector2.INF
	var k := _k(MOOR_H)
	var n := _ex(st.out)
	var tip := _tip(st) + off
	var G := Vector2(fposmod(origin.x + tip.x * k + n.x * H_OFF, StationGeo.CIRC), origin.y + tip.y + n.y * H_OFF)
	var uv := _uv(M, G.x, G.y)
	var polys: Array = [M.get("mooring", [])]
	polys.append_array(M.get("apron", []))
	for poly in polys:
		if (poly as Array).size() < 3:
			continue
		var lo := Vector2(INF, INF)
		var hi := Vector2(-INF, -INF)
		for p in poly:
			lo = Vector2(minf(lo.x, float(p[0])), minf(lo.y, float(p[1])))
			hi = Vector2(maxf(hi.x, float(p[0])), maxf(hi.y, float(p[1])))
		if uv.x > lo.x + 8.0 and uv.x < hi.x - 8.0 and uv.y > lo.y + 8.0 and uv.y < hi.y - 8.0:
			return G
	return Vector2.INF


func _berth_for(i: int, placed: Array, drift: SkyDrift, M: Dictionary, origin: Vector2, rope_faces: Dictionary) -> Dictionary:
	## where follower i lashes on (00 §5.3: along the drift, E or W, before N or S -- and near the mooring field, so
	## its ropeway can reach a plinth); never over the floor, never on a face a ground member's ropeway hangs from
	var isl: Dictionary = drift.islands[i]
	var mf: Array = M.get("mooring", [])
	var fc := Vector2.ZERO
	for p in mf:
		fc += Vector2(float(p[0]), float(p[1]))
	fc /= maxf(1.0, mf.size())
	var k := _k(MOOR_H)
	var best := {}
	var bs := INF
	for side in ["E", "W", "N", "S"]:
		for q in placed:
			var a: int = q.i
			if q.used.has(side) or rope_faces.get(q.k, "") == side:
				continue
			var ob := SkyDrift._opp(side)
			if (drift.islands[a].bridges[side] as Array).is_empty() or (isl.bridges[ob] as Array).is_empty():
				continue
			for ba in drift.islands[a].bridges[side]:
				for bb in isl.bridges[ob]:
					if ba.y != bb.y:
						continue
					var off: Vector2 = (q.off as Vector2) + drift._rel(a, i, side, ba.x, bb.x)
					if _clash(i, off, placed, drift):
						continue
					if _over_floor(M, origin, off, i, drift) > 0.0:
						continue
					var uv := _uv(M, origin.x + off.x * k, origin.y + off.y)
					var sc := uv.distance_to(fc) + (0.0 if side in ["E", "W"] else 60.0)
					if sc < bs:
						bs = sc
						best = {"off": off, "parent_k": q.k, "side": side, "along_a": ba.x, "along_b": bb.x}
	return best


func _clash(i: int, off: Vector2, placed: Array, drift: SkyDrift) -> bool:
	var r := _rect(i, drift)
	r.position += off
	r = r.grow(SkyDrift.DOCK_GAP * 0.5 - 1.0)
	for q in placed:
		var o := _rect(q.i, drift)
		o.position += q.off
		if o.grow(SkyDrift.DOCK_GAP * 0.5 - 1.0).intersects(r):
			return true
	return false


func target_of(st: Dictionary) -> Vector2:
	## the island centre's (s, x) when moored
	var L: Dictionary = st.layout
	var rec: Dictionary = L.members[int(st.k)]
	var k := _k(MOOR_H)
	return Vector2(fposmod(L.origin.x + rec.off.x * k, StationGeo.CIRC), L.origin.y + rec.off.y)


# ------------------------------------------------------------------ the bookings now
func _refresh(drift: SkyDrift) -> void:
	var t := now_h
	var day := floori(t / 24.0)
	var w := StationCalendar.week(day)
	var got := {}
	for ww in range(w - 4, w + 2):
		for b in FleaCalendar.week_plan(ww):
			for kk in (b.members as Array).size():
				var e: Dictionary = b.members[kk]
				var ph := phase_at(e, bool(e.ground), t)
				if ph == "":
					continue
				var i := int(by_id.get(str(e.island), -1))
				if i < 0:
					continue
				var L := layout(b, drift)
				var rec: Dictionary = L.members[kk]
				if rec.absent:
					continue
				got[i] = {"booking": b, "k": kk, "market": str(b.market), "e": e, "ground": bool(e.ground),
					"layout": L, "phase": ph}
	for i in got:
		var old: Dictionary = members.get(i, {})
		if old.is_empty() or str(old.phase) != str(got[i].phase):
			log_events.append([t, drift.islands[i].id, got[i].phase, got[i].market])
			if log_events.size() > 400:
				log_events = log_events.slice(200)
	for i in members:
		if not got.has(i):
			log_events.append([t, drift.islands[i].id, "FREE", members[i].market])
	members = got
	# the wind over each market now
	_wind.clear()
	if wind_at.is_valid():
		for i in members:
			var m := str(members[i].market)
			if not _wind.has(m):
				var c := FleaData.centre(FleaData.market(m))
				_wind[m] = float(wind_at.call(c.x, c.y))


# ------------------------------------------------------------------ driving the rafts (SkyDrift.step)
func drive(drift: SkyDrift, dt: float) -> Dictionary:
	## -> {raft id: true} for every raft placed here this step (SkyDrift leaves them out of the free drift).
	## The FULL pass (phases, the raft bookkeeping, every raft placed, _act rebuilt) runs on a refresh, a clock jump
	## and at least once a second; between full passes only the rafts still on the move (_act: TRIM, APPROACH, or
	## still descending) are stepped -- the rest sit where the full pass pinned them (SkyDrift.step skips held rafts,
	## so nothing drifts them meanwhile).
	snapped.clear()
	var jump := absf(now_h - _last_now) > 0.5 + dt / HOUR_S * 4.0
	_last_now = now_h
	_t -= dt
	var full := jump
	if _t <= 0.0 or jump:
		_t = REFRESH
		_refresh(drift)
		full = true
	_t2 -= dt
	if _t2 <= 0.0:
		full = true
	if members.is_empty():
		for id in _held_last:
			var r0: Dictionary = drift.rafts.get(id, {})
			if not r0.is_empty():
				r0["held"] = false
				if r0.edges.is_empty():
					r0.meet_h = NAN
		_held_last = {}
		_act.clear()
		return _held_last
	if not full:
		# the light step: only the rafts still on the move
		_place(drift, dt, false, _act, {}, false)
		return _held_last
	_t2 = 1.0
	# phases: from the clock
	for i in members:
		var st: Dictionary = members[i]
		st.phase = phase_at(st.e, st.ground, now_h)
	# 1. who must be on their own: trimming, approaching, casting off -- or lashed to a raft that isn't theirs
	for i in members:
		var st: Dictionary = members[i]
		var ph := str(st.phase)
		var r := drift.raft_of(i)
		if ph in ["TRIM", "APPROACH", "CAST_OFF"]:
			if r.members.size() > 1:
				_detach(drift, i)
		elif ph != "" and r.members.size() > 1:
			# (a stranger lashed on before it was booked -- or one of ours already gone: cast off)
			for j in r.members.duplicate():
				if j != i and (not members.has(j) or str(members[j].booking.id) != str(st.booking.id)):
					_detach(drift, j)
	# 2. the moored: lashed to their layout parent (the bridges come down), held over the field
	for i in members:
		var st: Dictionary = members[i]
		var ph := str(st.phase)
		if ph in ["", "TRIM", "APPROACH", "CAST_OFF"]:
			continue
		var rec: Dictionary = st.layout.members[int(st.k)]
		var pk := int(rec.parent)
		if pk >= 0:
			var prec: Dictionary = st.layout.members[pk]
			var pi := int(prec.i)
			if pi >= 0 and members.has(pi) and str(members[pi].booking.id) == str(st.booking.id) \
					and not (str(members[pi].phase) in ["", "TRIM", "APPROACH", "CAST_OFF"]) \
					and drift.islands[pi].raft != drift.islands[i].raft:
				_lash_to(drift, pi, i, rec, prec, st.layout, jump)
	var held := {}
	_act.clear()
	_place(drift, dt, jump, members.keys(), held, true)
	# (and nobody winches a stranger into a moored raft)
	for id in drift.rafts.keys():
		var g: Dictionary = drift.rafts.get(id, {})
		if not g.is_empty() and not (g.tow as Dictionary).is_empty() and held.has(int(g.tow.to)) and not held.has(id):
			drift._cancel_tow(g, drift.rafts.get(int(g.tow.to), {}))
	# 3. the released: free again (their raft's flag cleared; they climb back into the band on their own)
	for id in _held_last:
		var r: Dictionary = drift.rafts.get(id, {})
		if not r.is_empty() and not held.has(id):
			r["held"] = false
			if r.edges.is_empty():
				r.meet_h = NAN
	_held_last = held
	return held


func _place(drift: SkyDrift, dt: float, jump: bool, idxs: Array, done: Dictionary, rebuild: bool) -> void:
	## places each raft of the given members once (the raft's root so that the member sits on its target); on a full
	## pass (idxs = every member, done = the new held set) it also rebuilds _act with the rafts still on the move
	for i in idxs:
		var st: Dictionary = members.get(i, {})
		if st.is_empty():
			continue
		var ph := str(st.phase)
		if ph == "" or ph == "CAST_OFF":
			continue
		var r := drift.raft_of(i)
		if done.has(r.id):
			continue
		done[r.id] = true
		r["held"] = true
		var tgt := target_of(st)
		var k := _k(float(r.h))
		var off: Vector2 = drift.islands[i].off
		var want := Vector2(fposmod(tgt.x - off.x * k, StationGeo.CIRC), tgt.y - off.y)
		var calm := wind(str(st.market)) <= WIND_LIMIT
		var moving := true
		if ph == "TRIM" or ph == "APPROACH":
			var left_s := (float(st.e.arrive) - now_h) * HOUR_S
			var d := Vector2(StationGeo.wrap_ds(want.x - r.s) / k, want.y - r.x)
			var dist := d.length()
			if jump:
				# (the clock jumped into the approach: placed on its way in with the wind, from the east, the share of
				# the trim still to fly)
				var f := clampf((float(st.e.arrive) - now_h) / TRIM_H, 0.0, 1.0)
				r.s = fposmod(want.x + 6000.0 * f * k, StationGeo.CIRC)
				r.x = want.y
				r.h = MOOR_H + (SkyDrift.DECK_H - MOOR_H) * clampf((float(st.e.arrive) - now_h) / DESCENT_H, 0.0, 1.0)
				snapped.append(i)
			elif dist > 0.5:
				var v := clampf(dist / maxf(left_s, 1.0) * 1.15, minf(SkyDrift.DRIFT.x, dist / maxf(dt, 1e-3)), VMAX)
				var step_ := minf(v * dt, dist)
				var mv := d / dist * step_
				r.s = fposmod(r.s + mv.x * k, StationGeo.CIRC)
				r.x = r.x + mv.y
			var hw := MOOR_H if (ph == "APPROACH" and calm) else SkyDrift.DECK_H
			var h0 := float(r.h)
			r.h = move_toward(r.h, hw, SkyDrift.H_RATE * dt)
			r.vh = (r.h - h0) / maxf(dt, 1e-4)
		else:
			r.s = want.x
			r.x = want.y
			var h0 := float(r.h)
			if jump:
				r.h = MOOR_H
				snapped.append_array(r.members)
			elif calm or r.h < MOOR_H + 1.0:
				r.h = move_toward(r.h, MOOR_H, SkyDrift.H_RATE * dt)
			r.vh = (r.h - h0) / maxf(dt, 1e-4)
			r.meet_h = MOOR_H
			moving = float(r.h) != MOOR_H
		r.vx = 0.0
		if not (r.tow as Dictionary).is_empty():
			drift.lines = drift.lines.filter(func(ln: Dictionary) -> bool: return ln.guest != r.id)
			r.tow = {}
		if rebuild and moving:
			_act.append(i)


func _detach(drift: SkyDrift, i: int) -> void:
	## island i on its own raft (every edge it is lashed by cast off), its frame unchanged
	for _guard in 12:
		var r := drift.raft_of(i)
		if r.members.size() <= 1:
			break
		var e_ := {}
		for e in r.edges:
			if e.a == i or e.b == i:
				e_ = e
				break
		if e_.is_empty():
			break
		drift._split(r, e_)
	var r2 := drift.raft_of(i)
	if r2.members.size() == 1:
		var off: Vector2 = drift.islands[i].off
		if off != Vector2.ZERO:
			r2.s = fposmod(r2.s + off.x * SkyDrift._k(r2), StationGeo.CIRC)
			r2.x = r2.x + off.y
			drift.islands[i].off = Vector2.ZERO


func _lash_to(drift: SkyDrift, pi: int, i: int, rec: Dictionary, prec: Dictionary, L: Dictionary, jump: bool) -> void:
	## follower i lashed to its parent pi as the layout has it (SkyDrift._lash: the bridges come down)
	_detach(drift, i)
	var host := drift.raft_of(pi)
	var guest := drift.raft_of(i)
	if host.id == guest.id:
		return
	var rel: Vector2 = rec.off - prec.off
	var plan := {"a": pi, "b": i, "side": str(rec.side), "along_a": float(rec.along_a), "along_b": float(rec.along_b),
		"off": drift.islands[pi].off + rel - drift.islands[i].off}
	guest.tow = {"to": host.id, "plan": plan, "vel": Vector2.ZERO, "t0": drift.t}
	drift._lash(host, guest)
	host.meet_h = MOOR_H
	if jump:
		snapped.append(i)


func snap(drift: SkyDrift) -> void:
	## after the warm-up (or a jump): everyone where the calendar has them, at once
	_last_now = -1.0e9
	drive(drift, 0.0)
