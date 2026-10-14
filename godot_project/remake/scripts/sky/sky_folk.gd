extends Node
class_name SkyFolk

## The Aloft on the islands near the player (research/sky_islands/03_society.md): generated like the floor's people
## (NpcTraits.sky_folk: the "sky" population, dressed in their clan's colours for their work), never stored.  They
## live on their island's path graph (the layout's "graph": paths, roads, the promenade, spurs to doors, bridges,
## pads, hoists, pens and pond banks), in its own frame -- children of the island, so they ride it -- walking, or
## riding bicycles (BIKE_SHARE).  Where a bridge is down to a docked island, some cross: out along the bridge to the
## other's, and on through its streets.

const PER_ISLAND := Vector2i(6, 26)  # people out on a near island, by its population
const MAX_LIVE := 40
const FOLK_R := 450.0               # m: islands further than this have nobody out (they're dots)
const BIKE_SHARE := 0.3
const WALK := 1.3
const BIKE := 4.0
const CROSS_CHANCE := 0.35           # a walker on a docked island choosing the bridge next
const SEED := 7714

var sys: SkyIslands
var live := {}                       # pid -> entry
var _pending := {}                   # pid -> job
var _graphs := {}                    # island idx -> {nodes: PackedVector2Array, adj: Array, bridge_node: {"side:along": node}}
var _t := 0.0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = SEED


func _process(delta: float) -> void:
	if sys == null or not sys.is_ready():
		return
	_t -= delta
	if _t <= 0.0:
		_t = 1.0
		_populate()
	_collect()
	for pid in live.keys():
		_move(live[pid], delta)


# ------------------------------------------------------------------ who's out
func _populate() -> void:
	var want := {}
	var budget := MAX_LIVE
	var near: Array = []
	for i in sys.islands.size():
		var isl: SkyIsland = sys.islands[i]
		if isl.tier == 2 and isl.has_node("Near/Rock") and _dist(i) < FOLK_R:
			near.append(i)
	near.sort_custom(func(a: int, b: int) -> bool: return _dist(a) < _dist(b))
	for i in near:
		var pop: int = sys.islands[i].canon.get("population", 600)
		var n := clampi(pop / 50, PER_ISLAND.x, PER_ISLAND.y)
		n = mini(n, budget)
		budget -= n
		var id: String = sys.layouts[i].id
		for k in n:
			want["%s:%d" % [id, k]] = i
	for pid in live.keys():
		var e: Dictionary = live[pid]
		if not is_instance_valid(e.npc) or not want.has(pid) or sys.islands[e.at].tier < 2:
			_despawn(pid)
	for pid in want:
		if not live.has(pid) and not _pending.has(pid):
			_spawn(pid, want[pid])


func _dist(i: int) -> float:
	return sys.islands[i].global_position.distance_to(sys.player.global_position)


func _spawn(pid: String, i: int) -> void:
	var c: Dictionary = sys.islands[i].canon
	var jobs: Dictionary = c.get("jobs", {})
	var job := _pick_job(jobs, pid)
	var v := NpcTraits.shared().sky_folk(SEED, pid, sys.layouts[i].id, job, ["L0", "L1"])
	var job_ := {"v": v, "i": i, "data": {}}
	job_.task = WorkerThreadPool.add_task(func(): job_.data = NpcCharacter.prepare(v, pid, SEED, "work"), false, "sky folk " + pid)
	_pending[pid] = job_


func _pick_job(jobs: Dictionary, pid: String) -> String:
	var total := 0
	for j in jobs:
		total += int(jobs[j])
	if total <= 0:
		return ""
	var r := absi(hash(pid)) % total
	for j in jobs:
		r -= int(jobs[j])
		if r < 0:
			return j
	return ""


func _collect() -> void:
	for pid in _pending.keys():
		var job: Dictionary = _pending[pid]
		if not WorkerThreadPool.is_task_completed(job.task):
			continue
		WorkerThreadPool.wait_for_task_completion(job.task)
		_pending.erase(pid)
		var i: int = job.i
		var isl: SkyIsland = sys.islands[i]
		if job.data.is_empty() or isl.tier < 2 or not isl.has_node("Near"):
			continue
		var g := _graph(i)
		if g.nodes.is_empty():
			continue
		var npc := NpcCharacter.from_prepared(job.data)
		isl.get_node("Near").add_child(npc)
		SkyIsland._ranges(npc, 0.0, 250.0)
		var anim := NpcAnimator.attach(npc)
		var at: int = _rng.randi() % g.nodes.size()
		var e := {"npc": npc, "anim": anim, "home": i, "at": i, "node": at, "pos": g.nodes[at], "path": [],
			"wait": _rng.randf_range(0.0, 4.0), "speed": WALK * _rng.randf_range(0.85, 1.15), "yaw": _rng.randf() * TAU}
		var age := int(job.v.get("age", 30))
		if age >= 10 and age < 70 and absi(hash(pid + "bike")) % 100 < int(BIKE_SHARE * 100.0):
			var bike := NpcBike.make()
			isl.get_node("Near").add_child(bike)
			e.bike = bike
			e.speed = BIKE * _rng.randf_range(0.85, 1.15)
		live[pid] = e
		_place(e)
		return                                  # (one a frame: the mesh upload is the main thread's cost)


func _despawn(pid: String) -> void:
	var e: Dictionary = live[pid]
	if is_instance_valid(e.npc):
		(e.npc as Node).queue_free()
	if e.has("bike") and is_instance_valid(e.bike):
		(e.bike as Node).queue_free()
	live.erase(pid)


# ------------------------------------------------------------------ the graph
func _graph(i: int) -> Dictionary:
	if _graphs.has(i):
		return _graphs[i]
	var L: Dictionary = sys.layouts[i]
	var g: Dictionary = L.get("graph", {})
	var nodes := PackedVector2Array()
	var adj: Array = []
	for n in g.get("nodes", []):
		nodes.append(Vector2(n[0], n[1]))
		adj.append([])
	for e in g.get("edges", []):
		adj[e[0]].append(e[1])
		adj[e[1]].append(e[0])
	var bn := {}
	var f: Dictionary = L.faces
	for b in L.bridges:
		var al: float = b.along
		var p: Vector2 = {"N": Vector2(f.N, al), "S": Vector2(f.S, al), "E": Vector2(al, f.E), "W": Vector2(al, f.W)}[b.side]
		var best := -1
		var bd := INF
		for k in nodes.size():
			var d := nodes[k].distance_to(p)
			if d < bd:
				bd = d
				best = k
		if best >= 0 and bd < 15.0:
			bn["%s:%.2f" % [b.side, al]] = best
	_graphs[i] = {"nodes": nodes, "adj": adj, "bridge_node": bn}
	return _graphs[i]


func _route(g: Dictionary, from: int, to: int) -> Array:
	## breadth-first over the graph (islands are small): the nodes after `from` up to `to`
	var prev := {from: -1}
	var q := [from]
	while not q.is_empty():
		var n: int = q.pop_front()
		if n == to:
			break
		for m in g.adj[n]:
			if not prev.has(m):
				prev[m] = n
				q.append(m)
	if not prev.has(to):
		return []
	var out := []
	var n := to
	while n != from:
		out.push_front(n)
		n = prev[n]
	return out


# ------------------------------------------------------------------ moving
func _move(e: Dictionary, delta: float) -> void:
	if not is_instance_valid(e.npc):
		return
	var anim: NpcAnimator = e.anim
	if e.wait > 0.0:
		e.wait -= delta
		anim.speed = 0.0
		if e.has("bike"):
			(e.bike as NpcBike).update(delta, 0.0, 0.0)
			anim.ride = (e.bike as NpcBike).rider_pose()
		return
	if e.has("cross"):
		_crossing(e, delta)
		return
	var path: Array = e.path
	if path.is_empty():
		_next_errand(e)
		return
	var g := _graph(e.at)
	var tgt: Vector2 = g.nodes[path[0]]
	var to: Vector2 = tgt - e.pos
	var d := to.length()
	var step: float = e.speed * delta
	var yaw0: float = e.yaw
	if d <= step:
		e.pos = tgt
		e.node = path.pop_front()
		if path.is_empty() and e.has("to_bridge"):
			_start_cross(e)
	else:
		e.pos += to / d * step
		e.yaw = atan2(-to.x, -to.y)            # (local -Z is a model's front)
	anim.speed = e.speed if not e.has("bike") else 0.0
	if e.has("bike"):
		(e.bike as NpcBike).update(delta, e.speed, angle_difference(yaw0, float(e.yaw)) / maxf(delta, 1e-3))
		anim.ride = (e.bike as NpcBike).rider_pose()
	_place(e)


func _next_errand(e: Dictionary) -> void:
	## somewhere else on the island -- or, where a bridge is down, over to the docked neighbour
	var g := _graph(e.at)
	e.wait = _rng.randf_range(1.0, 8.0)
	var downs: Array = sys.drift.deployed(e.at)
	if not downs.is_empty() and not e.has("bike") and _rng.randf() < CROSS_CHANCE:
		var d: Array = downs[_rng.randi() % downs.size()]
		var key := "%s:%.2f" % [d[0], d[1]]
		if g.bridge_node.has(key):
			e.path = _route(g, e.node, g.bridge_node[key])
			e.to_bridge = d
			if e.path.is_empty():
				_start_cross(e)
			return
	e.path = _route(g, e.node, _rng.randi() % g.nodes.size())


func _start_cross(e: Dictionary) -> void:
	## out along the bridge: from this face to the other island's (SkyDrift.DOCK_GAP), then onto its graph
	var d: Array = e.to_bridge
	e.erase("to_bridge")
	var other := _partner(e.at, d[0], d[1])
	if other.is_empty():
		return
	var f: Dictionary = sys.layouts[e.at].faces
	var out: Vector2 = {"N": Vector2(-1, 0), "S": Vector2(1, 0), "E": Vector2(0, -1), "W": Vector2(0, 1)}[d[0]]
	var face: Vector2 = {"N": Vector2(f.N, d[1]), "S": Vector2(f.S, d[1]), "E": Vector2(d[1], f.E), "W": Vector2(d[1], f.W)}[d[0]]
	e.cross = {"from": face, "dir": out, "k": 0.0, "to": other}
	e.pos = face


func _partner(i: int, side: String, along: float) -> Dictionary:
	for edge in sys.drift.raft_of(i).edges:
		if edge.a == i and edge.side == side and absf(float(edge.along_a) - along) < 0.01:
			return {"i": edge.b, "side": SkyDrift._opp(side), "along": edge.along_b}
		if edge.b == i and SkyDrift._opp(edge.side) == side and absf(float(edge.along_b) - along) < 0.01:
			return {"i": edge.a, "side": edge.side, "along": edge.along_a}
	return {}


func _crossing(e: Dictionary, delta: float) -> void:
	var c: Dictionary = e.cross
	c.k = float(c.k) + e.speed * delta
	(e.anim as NpcAnimator).speed = e.speed
	e.yaw = atan2(-c.dir.x, -c.dir.y)
	e.pos = c.from + c.dir * minf(c.k, SkyDrift.DOCK_GAP)
	if c.k < SkyDrift.DOCK_GAP:
		_place(e, 0.0)
		return
	# across: now the other island's
	var to: Dictionary = c.to
	e.erase("cross")
	var j: int = to.i
	var isl: SkyIsland = sys.islands[j]
	if isl.tier < 2 or not isl.has_node("Near"):
		_despawn_entry(e)
		return
	var f: Dictionary = sys.layouts[j].faces
	var al: float = to.along
	e.pos = {"N": Vector2(f.N, al), "S": Vector2(f.S, al), "E": Vector2(al, f.E), "W": Vector2(al, f.W)}[to.side]
	(e.npc as Node).reparent(isl.get_node("Near"), false)
	e.at = j
	var g := _graph(j)
	var key := "%s:%.2f" % [to.side, al]
	e.node = g.bridge_node.get(key, 0)
	e.path = [e.node]
	_place(e)


func _despawn_entry(e: Dictionary) -> void:
	for pid in live:
		if live[pid] == e:
			_despawn(pid)
			return


func _place(e: Dictionary, y := NAN) -> void:
	var isl: SkyIsland = sys.islands[e.at]
	var p: Vector2 = e.pos
	var h := isl.deck_y(p.x, p.y) if is_nan(y) else y
	var xf := Transform3D(Basis(Vector3.UP, float(e.yaw)), Vector3(p.x, h, p.y))
	if e.has("bike"):
		var bike: NpcBike = e.bike
		if bike.get_parent() != (e.npc as Node).get_parent():
			bike.reparent((e.npc as Node).get_parent(), false)
		bike.transform = xf
		(e.npc as Node3D).global_transform = bike.rider_frame()
		return
	(e.npc as Node3D).transform = xf
