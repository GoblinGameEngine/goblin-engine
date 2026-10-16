extends RefCounted
class_name FleaLots

## The flea markets' car parks for the traffic (research/flea_markets/00_plan.md §6.1 "NpcTraffic"): a car whose
## driver is going to a market parks in that market's lot rows, in the free bay nearest the entrance, instead of at a
## kerb. Bays come from flea_markets.json `lot.rows` ([u0, u1, v_front, depth, facing] in the site frame; 2.75 m bays).
##
##   FleaLots.market_at(door)  -> the market id whose place unit has this door ("" if none)
##   FleaLots.bays(id)         -> [[Vector2 centre (s, x), Vector2 facing (s, x)]], nearest the walk entrance first
##   FleaLots.bays_on(id, day) -> bays(id), and on a fair day (>= 3 islands in SERVICE) the apron's grass overflow after
##                                them (00 §5.6: the back apron, clear of the tent slots; marked by the tent ring)

const BAY_W := 2.75
static var _doors: Array = []        # [[Vector2 door, market id]]
static var _bays := {}
static var _apron := {}
static var _mx := Mutex.new()


static func _load() -> void:
	if not _doors.is_empty():
		return
	_mx.lock()
	if _doors.is_empty():
		for M in FleaData.markets():
			if not M.get("sited", false):
				continue
			var walk := [0.0, 0.0]
			for e in M.get("entrances", []):
				if str(e[3]) == "walk":
					walk = e
			var arch: Array = M.get("arch", [0.0, 0.0])
			_doors.append([FleaData.to_world(M, float(walk[0]), float(walk[1])), str(M.id)])
			_doors.append([FleaData.to_world(M, float(arch[0]) + 10.0, float(arch[1])), str(M.id)])
		if _doors.is_empty():
			_doors.append([Vector2.INF, ""])
	_mx.unlock()


static func market_at(door: Vector2) -> String:
	_load()
	for d in _doors:
		if (d[0] as Vector2) != Vector2.INF and NpcPlaces.dist(d[0], door) < 4.0:
			return str(d[1])
	return ""


static func bays(id: String) -> Array:
	_mx.lock()
	var got = _bays.get(id)
	_mx.unlock()
	if got != null:
		return got
	var M := FleaData.market(id)
	var out: Array = []
	if not M.is_empty():
		var a := float((M.frame as Dictionary).get("yaw", 0.0))
		var vdir := Vector2(-sin(a), cos(a))                 # the site's +v on the ring (s, x)
		var walk := Vector2.ZERO
		for e in M.get("entrances", []):
			if str(e[3]) == "walk":
				walk = Vector2(float(e[0]), float(e[1]))
		var rows: Array = (M.get("lot", {}) as Dictionary).get("rows", [])
		var tmp: Array = []
		for r in rows:
			var u0 := float(r[0])
			var n := int((float(r[1]) - u0) / BAY_W + 1e-6)
			var vc := float(r[2]) + float(r[3]) * 0.5
			# facing -1: the row's aisle is on its +v side, the car drove in heading -v (and the other way)
			var face := vdir * (1.0 if int(r[4]) > 0 else -1.0)
			for k in n:
				var uc := u0 + BAY_W * (k + 0.5)
				tmp.append([Vector2(uc, vc).distance_squared_to(walk), FleaData.to_world(M, uc, vc), face])
		tmp.sort_custom(func(x, y): return float(x[0]) < float(y[0]))
		for t in tmp:
			out.append([t[1], t[2]])
	_mx.lock()
	_bays[id] = out
	_mx.unlock()
	return out


static func bays_on(id: String, day: int) -> Array:
	var b := bays(id)
	var M := FleaData.market(id)
	if M.is_empty() or FleaCalendar.in_service(M, day * 24.0 + 12.0) < FleaCalendar.FAIR_N:
		return b
	return b + apron_bays(id)


static func apron_bays(id: String) -> Array:
	## grass bays on the apron polygons (rows facing along the site's v), off the tent slots
	_mx.lock()
	var got = _apron.get(id)
	_mx.unlock()
	if got != null:
		return got
	var M := FleaData.market(id)
	var out: Array = []
	var a := float((M.frame as Dictionary).get("yaw", 0.0))
	var vdir := Vector2(-sin(a), cos(a))
	var tents: Array = M.get("tent_slots", [])
	for poly in M.get("apron", []):
		var u0 := INF
		var u1 := -INF
		var v0 := INF
		var v1 := -INF
		for q in poly:
			u0 = minf(u0, float(q[0]))
			u1 = maxf(u1, float(q[0]))
			v0 = minf(v0, float(q[1]))
			v1 = maxf(v1, float(q[1]))
		# bays 2.75 x 5.5 in double rows with a 7.3 m aisle (an 18.3 m module), 2 m in from the edges
		var vv := v0 + 2.0
		while vv + 18.3 <= v1 - 2.0:
			for row in 2:
				var vc := vv + (2.75 if row == 0 else 15.55)
				var uu := u0 + 2.0 + BAY_W * 0.5
				while uu + BAY_W * 0.5 <= u1 - 2.0:
					var clear := true
					for t in tents:
						if absf(float(t[0]) - uu) < float(t[3]) * 0.5 + 1.5 and absf(float(t[1]) - vc) < float(t[3]) * 0.5 + 3.0:
							clear = false
							break
					if clear:
						out.append([FleaData.to_world(M, uu, vc), vdir * (-1.0 if row == 0 else 1.0)])
					uu += BAY_W
			vv += 18.3
	_mx.lock()
	_apron[id] = out
	_mx.unlock()
	return out
