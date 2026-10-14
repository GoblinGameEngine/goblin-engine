extends RefCounted
class_name SkyDrift

## The sky islands' drift and docking (research/sky_islands/00_plan.md): pure data, no nodes.
##
##   Every island rides the wind west (antispinward, -s) at DECK_H, each at its own pace, and wanders along the axis.
##   Islands travel in rafts (a lone island is a raft of one).  When two rafts come within DOCK_RANGE (edge to edge),
##   their crews fire line rockets, and the lines winch the newcomer in until a dock face of one of its islands lies
##   DOCK_GAP from a free dock face of an island of the other, two bridges lined up; then they are lashed (an edge) and
##   move as one raft.  An edge holds LASH_DAYS in-game days, then is cast off: the raft splits along it and the two
##   parts drift apart (they won't lash to each other again till they've been DOCK_RANGE + PART_MARGIN apart).
##   Each raft rides up and down at random, DECK_H +- H_SWING.  When the rockets fire, the two rafts make for the mean
##   altitude of all their islands as they were at that moment, and a lashed raft holds it (the user, 2026-10-14:
##   "they will meet at the mean altitude").
##   No raft holds more than MAX_RAFT islands (the user, 2026-10-14: "they will stay together for 3days and break
##   apart. They will not dock more than 10 islands together").
##
## Islands don't turn: N always faces north.  Offsets in a raft are metres on the deck: east (+s) and south (+x).
## Fixed seed: the same sky every launch.

const DECK_H := 750.0           # the mean altitude ...
const H_SWING := 150.0         # ... each raft wanders this far above or below it (the user, 2026-10-14)
const H_RATE := 0.5            # m/s it climbs or sinks at, at most
const K_S := StationGeo.R / (StationGeo.R - DECK_H)     # deck metres -> floor s units (at the mean altitude)
const DOCK_RANGE := 3000.0
const PART_MARGIN := 600.0
const DOCK_GAP := 26.0
const WINCH := 3.0             # m/s a winched raft closes at
const ROCKET_SPEED := 160.0    # m/s a line rocket flies
const LASH_DAYS := 3.0
const MAX_RAFT := 10
const X_LIM := 9000.0          # |x| of any island's centre (clear of the end caps' mountains)
const DRIFT := Vector2(4.0, 9.0)      # m/s west, an island's own pace
const SHEAR := 0.25                  # the wind's change along the axis (fraction)
const WANDER := 1.2                  # m/s, the axial wander's range

var islands: Array = []        # {id, n (N/S/E/W face distances), bridges {side: [along]}, base_v, phase, raft, off: Vector2(east, south)}
var rafts := {}                # id -> {id, s, x, vx, members: [i], edges: [edge], tow: {} (winching in), seed}
var lines: Array = []          # line rockets in flight / lines out: {a, b, from: Vector2(e,s) offsets..., t0, raft_a, raft_b}
var hours := 0.0               # in-game hours since the start
var t := 0.0                   # real seconds
var _next_raft := 0
var _rng := RandomNumberGenerator.new()
var _banned := {}              # Vector2i(lo, hi) island pair -> true till they've drifted apart
var _check := 0.0
var events: Array = []         # [kind, data] since the runtime last read them ("fire", "lash", "cast_off")


func setup(defs: Array, seed_: int = 20261014) -> void:
	## defs: [{id, faces {N,S,E,W}, bridges [{side, along}], seed}]
	_rng.seed = seed_
	for d in defs:
		var br := {"N": [], "S": [], "E": [], "W": []}
		for b in d.get("bridges", []):
			br[b.side].append(Vector2(float(b.along), float(b.get("width", 3.6))))   # (a road bridge meets only a road bridge)
		var f: Dictionary = d.faces
		islands.append({"id": d.id, "n": {"N": absf(f.N), "S": absf(f.S), "E": absf(f.E), "W": absf(f.W)},
			"bridges": br, "base_v": -_rng.randf_range(DRIFT.x, DRIFT.y), "phase": _rng.randf() * TAU,
			"raft": -1, "off": Vector2.ZERO})
	# spread round the ring, never closer than DOCK_RANGE / 2 to another
	var placed: Array = []
	for i in islands.size():
		var s := 0.0
		var x := 0.0
		for tries in 200:
			s = _rng.randf() * StationGeo.CIRC
			x = _rng.randf_range(-X_LIM * 0.95, X_LIM * 0.95)
			var ok := true
			for p in placed:
				if Vector2(StationGeo.wrap_ds(s - p.x) / K_S, x - p.y).length() < DOCK_RANGE * 0.5:
					ok = false
					break
			if ok:
				break
		placed.append(Vector2(s, x))
		_new_raft([i], s, x)


func _new_raft(members: Array, s: float, x: float, h := NAN) -> Dictionary:
	if is_nan(h):
		h = DECK_H + _rng.randf_range(-H_SWING, H_SWING)
	var r := {"id": _next_raft, "s": s, "x": x, "vx": _rng.randf_range(-WANDER, WANDER), "members": members,
		"edges": [], "tow": {}, "h": h, "h_to": DECK_H + _rng.randf_range(-H_SWING, H_SWING), "meet_h": NAN}
	_next_raft += 1
	rafts[r.id] = r
	for i in members:
		islands[i].raft = r.id
	return r


# ------------------------------------------------------------------ queries
static func _k(r: Dictionary) -> float:
	## metres at the raft's height -> floor s units
	return StationGeo.R / (StationGeo.R - float(r.h))


func pos(i: int) -> Vector2:
	## The island's (s, x) on the floor map.
	var isl: Dictionary = islands[i]
	var r: Dictionary = rafts[isl.raft]
	return Vector2(fposmod(r.s + isl.off.x * _k(r), StationGeo.CIRC), r.x + isl.off.y)


func transform(i: int) -> Transform3D:
	## A lone island lies level on its own patch of the cylinder.  A raft is lashed rigid: its islands share the frame
	## of its root (one flat plane), so the bridges between them meet level, nose to nose (on separate curved frames a
	## big island and a small one were up to a metre apart where their bridges met, and tilted).
	var r := raft_of(i)
	if r.members.size() == 1:
		var p := pos(i)
		return Transform3D(StationGeo.basis(p.x), StationGeo.point(p.x, p.y, r.h))
	var off: Vector2 = islands[i].off
	var root := Transform3D(StationGeo.basis(r.s), StationGeo.point(r.s, r.x, r.h))
	return root * Transform3D(Basis(), Vector3(off.y, 0.0, -off.x))     # (local X south, -Z east)


func altitude(i: int) -> float:
	return raft_of(i).h


func velocity(i: int, at := Vector3.INF) -> Vector3:
	## m/s in the world: the raft's drift (at a point: the deck's own motion there, curving round the axis).
	var r: Dictionary = rafts[islands[i].raft]
	var p := pos(i)
	var h: float = r.h if at == Vector3.INF else StationGeo.h_of(at)
	var vs: float = _raft_v(r) * (StationGeo.R - h) / (StationGeo.R - float(r.h))
	var v: Vector3 = StationGeo.forward(p.x) * vs + Vector3.RIGHT * float(r.vx) + StationGeo.up(p.x) * float(r.get("vh", 0.0))
	if not r.tow.is_empty():
		v += StationGeo.forward(p.x) * float(r.tow.vel.x) + Vector3.RIGHT * float(r.tow.vel.y)
	return v


func raft_of(i: int) -> Dictionary:
	return rafts[islands[i].raft]


func deployed(i: int) -> Array:
	## The island's bridges that are down: [[side, along], ...]
	var out := []
	var r := raft_of(i)
	for e in r.edges:
		if e.a == i:
			out.append([e.side, e.along_a])
		elif e.b == i:
			out.append([_opp(e.side), e.along_b])
	return out


# ------------------------------------------------------------------ the step
func step(dt: float) -> void:
	t += dt
	hours += dt * 24.0 / DaySkySystem.DAY_LENGTH_SECONDS
	for id in rafts.keys():
		var r: Dictionary = rafts[id]
		_wander(r, dt)
		_climb(r, dt)
		var v := _raft_v(r)
		var tv := Vector2.ZERO
		if not r.tow.is_empty():
			_winch(r, dt)
			if not rafts.has(id):
				continue                 # (lashed on: it's part of the host now)
			if not r.tow.is_empty():
				tv = r.tow.vel
		r.s = fposmod(r.s + (v + tv.x) * _k(r) * dt, StationGeo.CIRC)
		r.x = clampf(r.x + (r.vx + tv.y) * dt, -X_LIM, X_LIM)
	_check -= dt
	if _check <= 0.0:
		_check = 2.0
		_cast_offs()
		_meetings()
		_keep_apart()
	for ln in lines:
		ln.fly = minf(1.0, ln.fly + dt * ROCKET_SPEED / maxf(ln.dist, 1.0))


func _raft_v(r: Dictionary) -> float:
	var v := 0.0
	for i in r.members:
		var isl: Dictionary = islands[i]
		v += float(isl.base_v) * (1.0 + SHEAR * sin(float(r.x) / 2600.0 + float(isl.phase)))
	return v / r.members.size()


func _wander(r: Dictionary, dt: float) -> void:
	r.vx = clampf(r.vx + _rng.randf_range(-0.04, 0.04) * dt, -WANDER, WANDER)
	if r.x > X_LIM - 600.0 and r.vx > 0.0 or r.x < -X_LIM + 600.0 and r.vx < 0.0:
		r.vx = move_toward(r.vx, -signf(r.x) * WANDER, 0.05 * dt)


func _climb(r: Dictionary, dt: float) -> void:
	## Up and down: a lone raft wanders between DECK_H +- H_SWING; one docking or lashed makes for its meeting height.
	var want: float = r.meet_h
	if is_nan(want):
		if absf(r.h - r.h_to) < 2.0 or _rng.randf() < dt / 1800.0:
			r.h_to = DECK_H + _rng.randf_range(-H_SWING, H_SWING)
		want = r.h_to
	var rate := H_RATE * clampf(absf(want - r.h) / 40.0, 0.1, 1.0)       # (easing in to the height)
	var h0: float = r.h
	r.h = move_toward(r.h, want, rate * dt)
	r.vh = (r.h - h0) / maxf(dt, 1e-4)


func _extent(r: Dictionary) -> Rect2:
	## The raft's bounds on the deck: east (+s) by south (+x), about its root.
	var rc := Rect2()
	var first := true
	for i in r.members:
		var b := _box(i)
		rc = b if first else rc.merge(b)
		first = false
	return rc


func _box(i: int) -> Rect2:
	var isl: Dictionary = islands[i]
	var n: Dictionary = isl.n
	return Rect2(isl.off.x - n.W, isl.off.y - n.N, n.W + n.E, n.N + n.S)


func _gap(a: Dictionary, b: Dictionary) -> float:
	## edge-to-edge distance between two rafts' bounds
	var ra := _extent(a)
	var rb := _extent(b)
	var d := Vector2(StationGeo.wrap_ds(b.s - a.s) / K_S, b.x - a.x)
	rb.position += d
	var dx := maxf(0.0, maxf(ra.position.x - rb.end.x, rb.position.x - ra.end.x))
	var dy := maxf(0.0, maxf(ra.position.y - rb.end.y, rb.position.y - ra.end.y))
	return Vector2(dx, dy).length()


func _meetings() -> void:
	var ids := rafts.keys()
	for ai in ids.size():
		var a: Dictionary = rafts[ids[ai]]
		if not a.tow.is_empty():
			continue
		for bi in range(ai + 1, ids.size()):
			var b: Dictionary = rafts[ids[bi]]
			if not b.tow.is_empty() or _towing_into(a) or _towing_into(b):
				continue
			if a.members.size() + b.members.size() > MAX_RAFT:
				continue
			if absf(StationGeo.wrap_ds(b.s - a.s)) / K_S > DOCK_RANGE + 2000.0:
				continue
			if _gap(a, b) > DOCK_RANGE or _is_banned(a, b):
				continue
			var big := a if a.members.size() >= b.members.size() else b
			var small := b if big == a else a
			var plan := _berth(big, small)
			if plan.is_empty():
				_ban(a, b)
				continue
			_fire(big, small, plan)
			return              # (one at a time: rafts change)


func _towing_into(r: Dictionary) -> bool:
	for o in rafts.values():
		if not o.tow.is_empty() and o.tow.to == r.id:
			return true
	return false


func _berth(host: Dictionary, guest: Dictionary) -> Dictionary:
	## Where guest can lash on: {a (host island), b (guest island), side (a's face), along_a, along_b, off (guest
	## root's offset from host root)} nearest where the guest is now, or {} if nowhere is free.
	var here := Vector2(StationGeo.wrap_ds(guest.s - host.s) / K_S, guest.x - host.x)
	var best := {}
	var bd := INF
	var used := {}
	for e in host.edges:
		used[Vector2i(e.a, _side_i(e.side))] = true
		used[Vector2i(e.b, _side_i(_opp(e.side)))] = true
	for a in host.members:
		for side in ["E", "W", "N", "S"]:
			if used.has(Vector2i(a, _side_i(side))) or islands[a].bridges[side].is_empty():
				continue
			for b in guest.members:
				var ob := _opp(side)
				if islands[b].bridges[ob].is_empty() or _face_used(guest, b, ob):
					continue
				for ba in islands[a].bridges[side]:
					for bb in islands[b].bridges[ob]:
						if ba.y != bb.y:
							continue
						var al: float = ba.x
						var bl: float = bb.x
						var rel := _rel(a, b, side, al, bl)        # b's offset from a
						var off: Vector2 = islands[a].off + rel - islands[b].off   # guest root from host root
						if not _fits(host, guest, off):
							continue
						var d := off.distance_to(here)
						if d < bd:
							bd = d
							best = {"a": a, "b": b, "side": side, "along_a": al, "along_b": bl, "off": off}
	return best


func _face_used(r: Dictionary, i: int, side: String) -> bool:
	for e in r.edges:
		if e.a == i and e.side == side or e.b == i and _opp(e.side) == side:
			return true
	return false


func _rel(a: int, b: int, side: String, al: float, bl: float) -> Vector2:
	## b's centre from a's when lashed face to face on a's `side` (east, south)
	var na: Dictionary = islands[a].n
	var nb: Dictionary = islands[b].n
	match side:
		"E": return Vector2(na.E + DOCK_GAP + nb.W, al - bl)          # along E/W faces is local X = south
		"W": return Vector2(-(na.W + DOCK_GAP + nb.E), al - bl)
		"S": return Vector2(-(al - bl), na.S + DOCK_GAP + nb.N)       # along N/S faces is local Z = west
		_: return Vector2(-(al - bl), -(na.N + DOCK_GAP + nb.S))


func _fits(host: Dictionary, guest: Dictionary, off: Vector2) -> bool:
	for g in guest.members:
		var gb := _box(g)
		gb.position += off
		gb = gb.grow(DOCK_GAP * 0.5 - 1.0)            # (a lashed pair's boxes then stand 2 m apart; anything closer clashes)
		for h in host.members:
			if _box(h).grow(DOCK_GAP * 0.5 - 1.0).intersects(gb):
				return false
	# and the raft must stay off the end caps
	var rc := _extent(host).merge(Rect2(_extent(guest).position + off, _extent(guest).size))
	return host.x + rc.end.y < X_LIM + 1500.0 and host.x + rc.position.y > -X_LIM - 1500.0


func _fire(host: Dictionary, guest: Dictionary, plan: Dictionary) -> void:
	# the meeting height: the mean of every island's altitude now (the user, 2026-10-14)
	var nh: int = host.members.size()
	var ng: int = guest.members.size()
	var meet: float = (host.h * nh + guest.h * ng) / float(nh + ng)
	host.meet_h = meet
	guest.meet_h = meet
	guest.tow = {"to": host.id, "plan": plan, "vel": Vector2.ZERO, "t0": t}
	var dist: float = (Vector2(StationGeo.wrap_ds(guest.s - host.s) / K_S, guest.x - host.x) - plan.off).length()
	lines.append({"a": plan.a, "b": plan.b, "side": plan.side, "fly": 0.0, "dist": maxf(dist, 50.0), "t0": t, "guest": guest.id})
	events.append(["fire", {"a": plan.a, "b": plan.b}])


func _winch(r: Dictionary, dt: float) -> void:
	## the guest raft hauled toward its berth by the lines (once the rockets have carried them over)
	var host: Dictionary = rafts.get(r.tow.to, {})
	if host.is_empty():
		_cancel_tow(r, {})
		return
	var plan: Dictionary = r.tow.plan
	if not host.members.has(plan.a) or not r.members.has(plan.b) or _face_used(host, plan.a, plan.side) or _face_used(r, plan.b, _opp(plan.side)) or host.members.size() + r.members.size() > MAX_RAFT \
			or not _fits(host, r, plan.off):
		_cancel_tow(r, host)                 # (the host cast off or filled that berth meanwhile)
		return
	var ln := _line_of(r.id)
	var want: Vector2 = r.tow.plan.off
	var here := Vector2(StationGeo.wrap_ds(r.s - host.s) / K_S, r.x - host.x)
	var to := want - here
	if ln.is_empty() or ln.fly < 1.0:
		r.tow.vel = Vector2.ZERO
		return
	var d := to.length()
	if d < 0.5:
		_lash(host, r)
		return
	# match the host's drift, then close at WINCH (slowing for the last 30 m)
	var rel_v := _raft_v(host) - _raft_v(r)
	var close := to.normalized() * minf(WINCH * clampf(d / 30.0, 0.15, 1.0), d / dt)
	r.tow.vel = Vector2(rel_v, 0.0) + close
	r.tow.vel.y += float(host.vx) - float(r.vx)


func _cancel_tow(r: Dictionary, host: Dictionary) -> void:
	lines = lines.filter(func(ln: Dictionary) -> bool: return ln.guest != r.id)
	r.tow = {}
	if r.edges.is_empty():
		r.meet_h = NAN
	if not host.is_empty() and host.edges.is_empty():
		host.meet_h = NAN
	if not host.is_empty():
		_ban(r, host)
	events.append(["slip", {"raft": r.id}])


func _line_of(guest_id: int) -> Dictionary:
	for ln in lines:
		if ln.guest == guest_id:
			return ln
	return {}


func _lash(host: Dictionary, guest: Dictionary) -> void:
	var plan: Dictionary = guest.tow.plan
	for i in guest.members:
		islands[i].off += plan.off
		islands[i].raft = host.id
		host.members.append(i)
	host.edges.append_array(guest.edges)
	var edge := {"a": plan.a, "b": plan.b, "side": plan.side, "along_a": plan.along_a, "along_b": plan.along_b, "born": hours}
	host.edges.append(edge)
	lines = lines.filter(func(ln: Dictionary) -> bool: return ln.guest != guest.id)
	rafts.erase(guest.id)
	events.append(["lash", edge])


func _cast_offs() -> void:
	for id in rafts.keys():
		var r: Dictionary = rafts.get(id, {})
		if r.is_empty():
			continue
		for e in r.edges.duplicate():
			if hours - float(e.born) >= LASH_DAYS * 24.0:
				_split(r, e)
				break


func _split(r: Dictionary, e: Dictionary) -> void:
	## Cast off edge e: the side holding e.b becomes a raft of its own.
	r.edges.erase(e)
	var side_b := _component(r, e.b)
	if side_b.has(e.a):
		return                   # (still joined some other way)
	var keep: Array = r.members.filter(func(i: int) -> bool: return not side_b.has(i))
	var root_off: Vector2 = islands[side_b[0]].off
	var p := Vector2(fposmod(r.s + root_off.x * _k(r), StationGeo.CIRC), r.x + root_off.y)
	r.members = keep
	var moved_edges: Array = r.edges.filter(func(x: Dictionary) -> bool: return side_b.has(x.a))
	r.edges = r.edges.filter(func(x: Dictionary) -> bool: return not side_b.has(x.a))
	# part: the two drift apart along the axis
	var away := signf(float(islands[e.b].off.y) - float(islands[e.a].off.y) + 0.01)
	var nr := _new_raft(side_b, p.x, p.y, r.h)
	if r.edges.is_empty():
		r.meet_h = NAN             # (alone again: free to wander up and down)
	if nr.edges.is_empty():
		nr.meet_h = NAN
	else:
		nr.meet_h = r.h
	nr.edges = moved_edges
	for i in side_b:
		islands[i].off -= root_off
	nr.vx = away * WANDER
	r.vx = -away * WANDER
	_ban(r, nr)
	events.append(["cast_off", e])


func _component(r: Dictionary, start: int) -> Array:
	var seen := [start]
	var todo := [start]
	while not todo.is_empty():
		var i: int = todo.pop_back()
		for e in r.edges:
			var o: int = e.b if e.a == i else (e.a if e.b == i else -1)
			if o >= 0 and not seen.has(o):
				seen.append(o)
				todo.append(o)
	return seen


func _ban(a: Dictionary, b: Dictionary) -> void:
	for i in a.members:
		for j in b.members:
			_banned[Vector2i(mini(i, j), maxi(i, j))] = true


func _is_banned(a: Dictionary, b: Dictionary) -> bool:
	for i in a.members:
		for j in b.members:
			if _banned.has(Vector2i(mini(i, j), maxi(i, j))):
				return true
	return false


func _keep_apart() -> void:
	## Lift bans once a pair has drifted well apart; rafts that can't lash steer round each other along the axis.
	var drop := []
	for k in _banned:
		var pa := pos(k.x)
		var pb := pos(k.y)
		if Vector2(StationGeo.wrap_ds(pb.x - pa.x) / K_S, pb.y - pa.y).length() > DOCK_RANGE + PART_MARGIN + 400.0:
			drop.append(k)
	for k in drop:
		_banned.erase(k)
	var ids := rafts.keys()
	for ai in ids.size():
		for bi in range(ai + 1, ids.size()):
			var a: Dictionary = rafts[ids[ai]]
			var b: Dictionary = rafts[ids[bi]]
			if a.tow.get("to", -1) == b.id or b.tow.get("to", -1) == a.id:
				continue
			if absf(StationGeo.wrap_ds(b.s - a.s)) / K_S > 3000.0:
				continue
			if _gap(a, b) < 150.0:
				var away := signf(b.x - a.x + 0.01)
				a.vx = -away * WANDER
				b.vx = away * WANDER


static func _opp(side: String) -> String:
	return {"N": "S", "S": "N", "E": "W", "W": "E"}[side]


static func _side_i(side: String) -> int:
	return "NSEW".find(side)


func warm_up(game_hours: float, dt := 20.0) -> void:
	## Run the sky forward (at load: rafts already formed and under way).
	var steps := int(game_hours * DaySkySystem.DAY_LENGTH_SECONDS / 24.0 / dt)
	for k in steps:
		step(dt)
	events.clear()


func summary() -> String:
	var sizes := {}
	for r in rafts.values():
		sizes[r.members.size()] = sizes.get(r.members.size(), 0) + 1
	var towing := 0
	for r in rafts.values():
		if not r.tow.is_empty():
			towing += 1
	return "rafts %d by size %s, towing %d, lines %d, hour %.1f" % [rafts.size(), sizes, towing, lines.size(), hours]
