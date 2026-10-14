extends Node3D
class_name SkyIsland

## One sky island (research/sky_islands/00_plan.md; layout from tools/sky/make_islands.py -> remake/sky/islands.json).
## SkyIslands places it every physics tick (its frame: +X south, +Y up, +Z west; y 0 the deck at its dock faces).
##
## Three tiers, by distance from the player:
##   far   remake/sky/islands/<id>.lod2.glb (a few hundred triangles; always loaded);
##   mid   <id>.lod1.glb (coarse rock, deck, buildings as boxes);
##   near  the whole island, built a piece a frame: the landmass (<id>.rock.glb: deck with its collision, underside),
##         the buildings (the shared models, SKY-M-*, with their shared kit parts), and everything the layout keeps
##         as data -- path ribbons, ponds, the fence (MultiMesh, gaps at the bridges), moss and vines (MultiMesh),
##         balloon hubs and tethers, bridges, hoists, line launchers, lark pads, cloud nets.
## The balloons themselves are SkyIslands' MultiMeshes (all islands at once).
##
## Snow: `snow` 0..1 (SkyIslands sets it: it builds up while the island is in a cloud and melts very slowly after).
## Every mesh of the near and mid tiers gets the island's snow overlay (sky_snow.gdshader): coverage grows patch by
## patch over upward faces into a blanket, and shrinks back the same way.
##
## Cargo: each hoist now and then lowers its line and hook to the floor and draws a container up (or lowers one
## down and lets it go).  The line bends with the spin: a load going down drifts antispinward (west, +Z here), one
## coming up spinward -- the crews lead their drops for it.

const NEAR := 800.0
const MID := 3600.0
const PART := "res://remake/sky/parts/%s.glb"
const OMEGA := 0.0313                # rad/s, the station's spin (sqrt(9.8 / 10,000))
const LOWER_SPEED := 12.0            # m/s: an expert drop
const RAISE_SPEED := 5.0
const HOOK_CLEAR := 2.0

var idx := 0
var data: Dictionary                 # the layout
var canon: Dictionary
var sys: Node                        # SkyIslands
var tier := -1
var snow := 0.0
var snowing := 0.0                   # how hard it's snowing here now (SkyIslands)
var bridges: Array[SkyBridge] = []
var larks_parked: Array = []
var _blds: Array = []               # {b, holder, lod1, full, loading}
var _full_t := 0.0
var bridge_at := {}                  # "side:along" -> SkyBridge
var _far: Node3D
var _mid: Node3D
var _near: Node3D
var _build: Array[Callable] = []     # the near tier's pieces still to build
var _pending := {}                   # path -> callable(PackedScene) waiting on a threaded load
var _merging := {}                   # path -> [task, ps, callables]
var _snow_mat: ShaderMaterial
var _snow_shown := -1.0
var _hoists: Array = []              # {node, hook, line (ImmediateMesh), state, t, len, depth, cargo, dir}
var _height: PackedByteArray
var _geoms: Array = []               # every mesh the snow lies on
const SNOW_MIN := 0.002
var _hg := {}

static var _parts := {}
static var _shared := {}             # material / mesh caches


func setup(p_sys: Node, p_idx: int, p_data: Dictionary, p_canon: Dictionary) -> void:
	sys = p_sys
	idx = p_idx
	data = p_data
	canon = p_canon
	name = "SkyIsland_%s" % data.id
	_hg = data.get("height", {})
	if not _hg.is_empty():
		_height = Marshalls.base64_to_raw(_hg.data)
	_snow_mat = ShaderMaterial.new()
	_snow_mat.shader = load("res://remake/shaders/sky_snow.gdshader")
	_snow_mat.set_shader_parameter("snow_tex", load("res://remake/sky/textures/snow_albedo.png"))
	_snow_mat.set_shader_parameter("cover_tex", load("res://remake/sky/textures/snow_coverage.png"))
	_snow_mat.set_shader_parameter("snow", 0.0)
	_load(data.lod.lod2, func(ps: PackedScene) -> void:      # (on a worker: 100 of them at load)
		_far = ps.instantiate()
		add_child(_far)
		_no_shadow(_far)
		_vertex_colours(_far)
		_far.visible = tier <= 0)


# ------------------------------------------------------------------ tiers
func set_tier(t: int) -> void:
	if t == tier:
		return
	tier = t
	if _far:
		_far.visible = t == 0
	if t >= 1 and _mid == null:
		_load(data.lod.lod1, func(ps: PackedScene) -> void:
			_mid = ps.instantiate()
			add_child(_mid)
			_no_shadow(_mid)
			_vertex_colours(_mid)
			_dress(_mid)
			_mid.visible = tier == 1)
	if _mid:
		_mid.visible = t == 1
	if t == 2 and _near == null:
		_near = Node3D.new()
		_near.name = "Near"
		add_child(_near)
		_queue_near()
	if _near:
		_near.visible = t == 2
	if t < 2 and _near and t == 0:
		_drop_near()


func _drop_near() -> void:
	_near.queue_free()
	_near = null
	_build.clear()
	bridges.clear()
	bridge_at.clear()
	_hoists.clear()
	larks_parked.clear()
	_blds.clear()


func _process(delta: float) -> void:
	# the near tier: a piece a frame
	if not _build.is_empty() and _near:
		var f: Callable = _build.pop_front()
		f.call()
	_poll_loads()
	for k in larks_parked.duplicate():
		if is_instance_valid(k) and ((k as RemakeAirVehicle).pilot != null or not (k as RemakeAirVehicle).fly_input.is_empty()):
			# someone has taken it up: off the island's books (over the island, the moving frame carries it now)
			larks_parked.erase(k)
			(k as Node).reparent(sys, true)
			(k as Node).remove_meta("riding")
	if _near and tier == 2:
		_hoist_step(delta)
		_full_t -= delta
		if _full_t <= 0.0:
			_full_t = 0.5
			_stream_full()


func _queue_near() -> void:
	_build.append(func() -> void:
		_load(data.lod.rock, func(ps: PackedScene) -> void:
			if _near == null:
				return
			var rock: Node3D = ps.instantiate()
			rock.name = "Rock"
			_near.add_child(rock)
			_vertex_colours(rock)
			_dress(rock)
			if _mid:
				_mid.visible = false))
	_build.append(_build_paths)
	_build.append(_build_water)
	_build.append(_build_fence)
	_build.append(_build_moss)
	_build.append(_build_tethers)
	_build.append(_build_bridges)
	_build.append(_build_props)
	var by_model := {}
	for b in data.buildings:
		by_model[b.model] = by_model.get(b.model, []) + [b]
	for m in by_model:
		var list: Array = by_model[m]
		_build.append(func() -> void: _load_building(m, list))


# ------------------------------------------------------------------ loading
func _glb(path: String) -> Node3D:
	if not ResourceLoader.exists(path):
		return null
	var ps: PackedScene = load(path)
	return ps.instantiate() as Node3D


func _load(path: String, then: Callable) -> void:
	if not ResourceLoader.exists(path):
		return
	if ResourceLoader.has_cached(path):
		then.call(load(path))
		return
	if not _pending.has(path):
		_pending[path] = []
		ResourceLoader.load_threaded_request(path)
	_pending[path].append(then)


func _poll_loads() -> void:
	for path in _pending.keys():
		var st := ResourceLoader.load_threaded_get_status(path)
		if st == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			continue
		var calls: Array = _pending[path]
		_pending.erase(path)
		if st != ResourceLoader.THREAD_LOAD_LOADED:
			continue
		var ps: PackedScene = ResourceLoader.load_threaded_get(path)
		if path.begins_with("res://remake/buildings/"):
			_merging[path] = [WorkerThreadPool.add_task(RemakeBuilding.merge_kit.bind(ps)), ps, calls]
		else:
			for c in calls:
				(c as Callable).call(ps)
	for path in _merging.keys():
		if WorkerThreadPool.is_task_completed(_merging[path][0]):
			WorkerThreadPool.wait_for_task_completion(_merging[path][0])
			var m: Array = _merging[path]
			_merging.erase(path)
			for c in m[2]:
				(c as Callable).call(m[1])


func _load_building(model: String, list: Array) -> void:
	## Every building as its model's LOD1 (to LOD1_END) and LOD2 (beyond): shared scenes, light.  Full detail
	## (interiors, doors, collision) streams in per building within FULL_R of the player (_stream_full).
	var base := "res://remake/buildings/%s" % model
	_load(base + ".lod2.glb", func(ps2: PackedScene) -> void:
		_load(base + ".lod1.glb", func(ps1: PackedScene) -> void:
			if _near == null:
				return
			for b in list:
				var holder := Node3D.new()
				holder.name = b.id
				holder.transform = Transform3D(Basis(Vector3.UP, float(b.yaw)), Vector3(b.x, b.y, b.z))
				_near.add_child(holder)
				var l1: Node3D = ps1.instantiate()
				RemakeBuilding.prepare_lod(l1, base + ".lod1.glb")
				_ranges(l1, 0.0, LOD1_END)
				holder.add_child(l1)
				var l2: Node3D = ps2.instantiate()
				RemakeBuilding.prepare_lod(l2, base + ".lod2.glb")
				_ranges(l2, LOD1_END, 0.0)
				_no_shadow(l2)
				holder.add_child(l2)
				_dress(holder)
				_blds.append({"b": b, "holder": holder, "lod1": l1, "full": null, "loading": false})))


const FULL_R := 55.0                 # m: full detail within (the main world's LOD0_MAX)
const LOD1_END := 200.0
const MAX_FULL := 8


func _stream_full() -> void:
	## the buildings near the player in full: their interiors, doors and collision
	var cam: Vector3 = sys.player.global_position
	var n_full := 0
	for e in _blds:
		if e.full != null or e.loading:
			n_full += 1
	for e in _blds:
		var holder: Node3D = e.holder
		var d := holder.global_position.distance_to(cam)
		if e.full == null and not e.loading and d < FULL_R and n_full < MAX_FULL:
			e.loading = true
			n_full += 1
			_load("res://remake/buildings/%s.glb" % e.b.model, func(ps: PackedScene) -> void:
				e.loading = false
				if not is_instance_valid(holder):
					return
				var rb := RemakeBuilding.new()
				rb.name = "Full"
				holder.add_child(rb)
				rb.load_building(ps)
				rb.cull_inner_doors()
				_ranges(rb, 0.0, FULL_R * 1.3)
				_ranges(e.lod1, FULL_R * 1.3, LOD1_END)
				_dress(rb)
				e.full = rb)
		elif e.full != null and d > FULL_R * 1.5:
			(e.full as Node).queue_free()
			e.full = null
			_ranges(e.lod1, 0.0, LOD1_END)


static func _ranges(n: Node, begin: float, end: float) -> void:
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			var g := c as GeometryInstance3D
			g.visibility_range_begin = begin
			g.visibility_range_begin_margin = begin * 0.08
			g.visibility_range_end = end
			g.visibility_range_end_margin = end * 0.08


static func part(n: String) -> PackedScene:
	if not _parts.has(n):
		_parts[n] = load(PART % n)
	return _parts[n]


static func part_mesh(n: String) -> Mesh:
	## the first mesh in a part's glb (for MultiMesh)
	var key := "mesh:" + n
	if not _shared.has(key):
		var inst := part(n).instantiate()
		var stack: Array[Node] = [inst]
		while not stack.is_empty():
			var c: Node = stack.pop_back()
			if c is MeshInstance3D:
				_shared[key] = (c as MeshInstance3D).mesh
				break
			stack.append_array(c.get_children())
		inst.free()
	return _shared.get(key)


# ------------------------------------------------------------------ the deck
func deck_y(x: float, z: float) -> float:
	## the deck's height at (x, z): the layout's grid, bilinear
	if _hg.is_empty():
		return 0.0
	var fx := (x - float(_hg.x0)) / float(_hg.step)
	var fz := (z - float(_hg.z0)) / float(_hg.step)
	var nx: int = _hg.nx
	var nz: int = _hg.nz
	var ix := clampi(floori(fx), 0, nx - 2)
	var iz := clampi(floori(fz), 0, nz - 2)
	var tx := clampf(fx - ix, 0.0, 1.0)
	var tz := clampf(fz - iz, 0.0, 1.0)
	var h00 := _h(ix, iz, nx)
	var h10 := _h(ix + 1, iz, nx)
	var h01 := _h(ix, iz + 1, nx)
	var h11 := _h(ix + 1, iz + 1, nx)
	return lerpf(lerpf(h00, h10, tx), lerpf(h01, h11, tx), tz)


func _h(ix: int, iz: int, nx: int) -> float:
	return _height.decode_s16((iz * nx + ix) * 2) * 0.01


func inside(lp: Vector3) -> bool:
	## lp (local) over the deck's bounds
	var f: Dictionary = data.faces
	return lp.x > float(f.N) - 2.0 and lp.x < float(f.S) + 2.0 and lp.z > float(f.E) - 2.0 and lp.z < float(f.W) + 2.0


static func _mat(key: String, col: Color, rough := 0.95) -> StandardMaterial3D:
	if not _shared.has(key):
		var m := StandardMaterial3D.new()
		m.albedo_color = col
		m.roughness = rough
		_shared[key] = m
	return _shared[key]


func _build_paths() -> void:
	## the walkable network as flat ribbons a little over the deck (roads wider and darker)
	var g: Dictionary = data.get("graph", {})
	if g.is_empty():
		return
	var nodes: Array = g.nodes
	var sts := {}
	for e in g.edges:
		var w: float = e[2]
		var key := "road" if w >= 5.0 else "path"
		if not sts.has(key):
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			sts[key] = st
		var a := Vector2(nodes[e[0]][0], nodes[e[0]][1])
		var b := Vector2(nodes[e[1]][0], nodes[e[1]][1])
		var L := a.distance_to(b)
		if L < 0.05:
			continue
		var side := (b - a).normalized().orthogonal() * (w * 0.5)
		var lift := 0.05 if key == "road" else 0.04
		var n := maxi(1, ceili(L / 4.0))
		for k in n:
			var p0 := a.lerp(b, float(k) / n)
			var p1 := a.lerp(b, float(k + 1) / n)
			var q := [p0 - side, p0 + side, p1 + side, p1 - side]
			var v: Array[Vector3] = []
			for p in q:
				v.append(Vector3(p.x, deck_y(p.x, p.y) + lift, p.y))
			var st: SurfaceTool = sts[key]
			st.set_normal(Vector3.UP)
			for i in [0, 2, 1, 0, 3, 2]:
				st.add_vertex(v[i])
	for key in sts:
		var mi := MeshInstance3D.new()
		mi.name = "Paths_" + key
		mi.mesh = (sts[key] as SurfaceTool).commit()
		mi.material_override = _mat("sky_" + key, Color(0.36, 0.35, 0.34) if key == "road" else Color(0.62, 0.57, 0.48))
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_near.add_child(mi)
		_dress(mi)


func _build_water() -> void:
	for w in data.get("water", []):
		var poly := PackedVector2Array()
		for p in w.outline:
			var v := Vector2(p[0], p[1])
			if poly.is_empty() or poly[poly.size() - 1].distance_to(v) > 0.01:
				poly.append(v)
		if poly.size() > 3 and poly[0].distance_to(poly[poly.size() - 1]) < 0.01:
			poly.remove_at(poly.size() - 1)          # (the outline comes closed)
		var tri := Geometry2D.triangulate_polygon(poly)
		if tri.is_empty():
			poly.reverse()
			tri = Geometry2D.triangulate_polygon(poly)
		if tri.is_empty():
			poly = Geometry2D.convex_hull(poly)        # (a self-touching outline: its hull, the basin holds it)
			poly.remove_at(poly.size() - 1)
			tri = Geometry2D.triangulate_polygon(poly)
		if tri.is_empty():
			push_warning("SkyIsland %s: a pond won't triangulate" % data.id)
			continue
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		st.set_normal(Vector3.UP)
		var lv: float = w.get("level", 0.0)
		for k in range(0, tri.size(), 3):
			for j in [0, 2, 1]:
				var p := poly[tri[k + j]]
				st.add_vertex(Vector3(p.x, lv, p.y))
		var mi := MeshInstance3D.new()
		mi.name = "Water"
		mi.mesh = st.commit()
		var m := _mat("sky_water", Color(0.25, 0.42, 0.5, 0.82), 0.08)
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.metallic_specular = 0.8
		mi.material_override = m
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_near.add_child(mi)


func _build_fence() -> void:
	var pts: Array = data.get("fence", [])
	if pts.size() < 2:
		return
	var gaps: Array = data.get("fence_gaps", [])
	var xf: Array[Transform3D] = []
	var body := StaticBody3D.new()
	body.name = "FenceBody"
	for i in pts.size():
		var a := Vector2(pts[i][0], pts[i][1])
		var b := Vector2(pts[(i + 1) % pts.size()][0], pts[(i + 1) % pts.size()][1])
		var L := a.distance_to(b)
		if L < 0.2:
			continue
		var n := maxi(1, roundi(L / 3.0))
		var dir := (b - a) / L
		for k in n:
			var p0 := a + dir * (L * k / n)
			var p1 := a + dir * (L * (k + 1) / n)
			var mid := (p0 + p1) * 0.5
			var gap := false
			for gp in gaps:
				if mid.distance_to(Vector2(gp.at[0], gp.at[1])) < float(gp.width) * 0.5 + 1.5:
					gap = true
					break
			if gap:
				continue
			var y0 := deck_y(p0.x, p0.y)
			var y1 := deck_y(p1.x, p1.y)
			var v := Vector3(p1.x - p0.x, y1 - y0, p1.y - p0.y)
			var xa := v / 3.0                                 # the unit is 3 m along +X
			var yb := Vector3.UP
			var zb := xa.normalized().cross(yb).normalized()
			xf.append(Transform3D(Basis(xa, yb, zb), Vector3(p0.x, y0, p0.y)))
			var cs := CollisionShape3D.new()
			var box := BoxShape3D.new()
			box.size = Vector3(v.length(), 1.4, 0.12)
			cs.shape = box
			cs.transform = Transform3D(Basis(xa.normalized(), yb, zb), Vector3((p0.x + p1.x) * 0.5, (y0 + y1) * 0.5 + 0.7, (p0.y + p1.y) * 0.5))
			body.add_child(cs)
	_near.add_child(body)
	_near.add_child(_multi("Fence", part_mesh("fence"), xf))


func _multi(n: String, mesh: Mesh, xf: Array[Transform3D], shadow := true) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = xf.size()
	for i in xf.size():
		mm.set_instance_transform(i, xf[i])
	var mmi := MultiMeshInstance3D.new()
	mmi.name = n
	mmi.multimesh = mm
	if not shadow:
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_dress(mmi)
	return mmi


func _build_moss() -> void:
	## moss and vine cards: hung round the rim (outward) and under the rock
	var moss: Dictionary = data.get("moss", {})
	var by := {}
	for r in moss.get("rim", []):
		var p := Vector3(r[0], deck_y(r[0], r[1]) - 0.3, r[1])
		var out := Vector2(r[0], r[1]).normalized()
		var yaw := atan2(out.x, out.y)
		var k: String = r[3] if r.size() > 3 else "moss_a"
		var xf := Transform3D(Basis(Vector3.UP, yaw).scaled(Vector3(1.0, float(r[2]), 1.0)), p + Vector3(out.x, 0, out.y) * 0.4)
		by[k] = by.get(k, []) + [xf]
	for u in moss.get("under", []):
		var k: String = u[4] if u.size() > 4 else "vine_a"
		var xf := Transform3D(Basis(Vector3.UP, float(hash(u) % 628) * 0.01).scaled(Vector3(1.0, float(u[3]), 1.0)), Vector3(u[0], u[1], u[2]))
		by[k] = by.get(k, []) + [xf]
	for k in by:
		var arr: Array[Transform3D] = []
		arr.assign(by[k])
		var m := part_mesh(k)
		if m:
			var mm := _multi("Moss_" + k, m, arr, false)
			_ranges(mm, 0.0, 200.0 if k.begins_with("vine") else 600.0)   # (thin vines ink to dotted noise further off)
			_near.add_child(mm)


func _build_tethers() -> void:
	## each balloon's hub (SkyIslands draws the envelopes) and its tethers down to the deck anchor
	var im := ImmediateMesh.new()
	im.surface_begin(Mesh.PRIMITIVE_LINES)
	var hub := part("balloon_hub")
	for b in data.balloons:
		var top := Vector3(b.x, sys.BALLOON_BASE, b.z)
		var h := hub.instantiate() as Node3D
		h.position = top
		_near.add_child(h)
		var a := Vector3(b.anchor[0], b.anchor[1], b.anchor[2])
		for o in [Vector3(1.2, 0, 0), Vector3(-1.2, 0, 0), Vector3(0, 0, 1.2), Vector3(0, 0, -1.2)]:
			im.surface_add_vertex(top + o * 3.0)
			im.surface_add_vertex(a + o)
	im.surface_end()
	var mi := MeshInstance3D.new()
	mi.name = "Tethers"
	mi.mesh = im
	mi.material_override = _mat("sky_tether", Color(0.2, 0.18, 0.15))
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_near.add_child(mi)


func _build_bridges() -> void:
	var f: Dictionary = data.faces
	var style: String = data.get("bridge_style", canon.get("bridge_style", "bascule_timber"))
	var down: Array = sys.drift.deployed(idx)
	for b in data.bridges:
		var br := SkyBridge.new()
		var st := style + ("_road" if float(b.get("width", 3.6)) >= 5.0 else "")
		var al: float = b.along
		match b.side:
			"N": br.transform = Transform3D(Basis(Vector3.UP, -PI * 0.5), Vector3(f.N, 0, al))
			"S": br.transform = Transform3D(Basis(Vector3.UP, PI * 0.5), Vector3(f.S, 0, al))
			"E": br.transform = Transform3D(Basis(Vector3.UP, PI), Vector3(al, 0, f.E))
			_: br.transform = Transform3D(Basis(), Vector3(al, 0, f.W))
		_near.add_child(br)
		br.setup(st)
		var key := "%s:%.2f" % [b.side, al]
		bridge_at[key] = br
		bridges.append(br)
		for d in down:
			if d[0] == b.side and absf(float(d[1]) - al) < 0.01:
				br.snap(1.0)
		_dress(br)


func _park_lark(at: Transform3D) -> void:
	## the clan's lark in its cradle (fleet type sky_skiff): a child of the island while parked, so it rides along
	if _near == null:
		return
	var k := RemakeFleetCraft.new("sky_skiff")
	k.name = "Lark_%d" % larks_parked.size()
	k.set_meta("riding", true)
	_near.add_child(k)
	k.transform = at
	var cols: Array = canon.get("colors", [])
	if cols.size() >= 3:
		k.set_livery(cols)
	larks_parked.append(k)
	_ranges(k, 0.0, 350.0)


func set_bridge(side: String, along: float, down: bool) -> void:
	var br: SkyBridge = bridge_at.get("%s:%.2f" % [side, along])
	if br:
		br.target = 1.0 if down else 0.0


func _build_props() -> void:
	var larks: int = canon.get("aerostats", 2)
	for p in data.get("pads", []):
		var n := part("pad").instantiate() as Node3D
		var at := Transform3D(Basis(Vector3.UP, float(p.yaw)), Vector3(p.x, p.get("y", deck_y(p.x, p.z)) + 0.02, p.z))
		n.transform = at
		_near.add_child(n)
		_dress(n)
		if larks > 0:
			larks -= 1
			_build.push_front(func() -> void: _park_lark(at))     # (the craft is heavier: a frame of its own)
	for c in data.get("cloud_nets", []):
		var n := part("cloud_net").instantiate() as Node3D
		n.transform = Transform3D(Basis(Vector3.UP, float(c[3])), Vector3(c[0], c[1], c[2]))
		_near.add_child(n)
		_dress(n)
	for l in data.get("launchers", []):
		var n := part("launcher").instantiate() as Node3D
		var yaw: float = {"N": -PI * 0.5, "S": PI * 0.5, "E": PI, "W": 0.0}[l.side]
		n.transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(l.x, deck_y(l.x, l.z), l.z))
		n.name = "Launcher_" + str(l.side)
		_near.add_child(n)
		_dress(n)
	for h in data.get("hoists", []):
		var n := part("hoist").instantiate() as Node3D
		n.transform = Transform3D(Basis(Vector3.UP, float(h.yaw)), Vector3(h.x, deck_y(h.x, h.z), h.z))
		_near.add_child(n)
		_dress(n)
		var hook := n.find_child("hook", true, false) as Node3D
		var im := ImmediateMesh.new()
		var line := MeshInstance3D.new()
		line.mesh = im
		line.material_override = _mat("sky_tether", Color(0.2, 0.18, 0.15))
		line.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_near.add_child(line)
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(data.id + str(h.x))
		_hoists.append({"node": n, "hook": hook, "im": im, "state": "idle", "t": rng.randf_range(20.0, 240.0),
			"len": 0.0, "cargo": null, "up": rng.randf() < 0.6, "rng": rng})


# ------------------------------------------------------------------ cargo
func _hoist_step(delta: float) -> void:
	for h in _hoists:
		var top: Vector3 = _near.to_local((h.hook as Node3D).global_position) if h.hook else (h.node as Node3D).position + Vector3(0, 4, 0)
		var depth := _ground_depth(top)
		match h.state:
			"idle":
				h.t -= delta
				if h.t <= 0.0 and (depth < 100.0 or _wet(top, depth)):
					h.t = 20.0                              # (not here: look again in a while)
				elif h.t <= 0.0:
					h.state = "lower"
					h.up = h.rng.randf() < 0.6          # (most runs draw a load up; some send one down)
					if not h.up:
						h.cargo = _container()
			"lower":
				h.len = minf(h.len + LOWER_SPEED * delta, depth - HOOK_CLEAR)
				if h.len >= depth - HOOK_CLEAR - 0.01:
					h.state = "ground"
					h.t = 25.0
					if not h.up and h.cargo:
						_set_down(h)                    # (let go: the box stays on the floor for the ground crew)
			"ground":
				h.t -= delta
				if h.t <= 0.0:
					h.state = "raise"
					if h.up:
						h.cargo = _container()
			"raise":
				h.len = maxf(h.len - RAISE_SPEED * delta, 0.0)
				if h.len <= 0.0:
					h.state = "idle"
					h.t = h.rng.randf_range(300.0, 900.0)
					if h.cargo:
						(h.cargo as Node3D).queue_free()
						h.cargo = null
		_draw_line(h, top)


func _wet(top: Vector3, depth: float) -> bool:
	## would the line come down in water (a sea, the lake, a river)?  -- where it lands, drifted west by the spin;
	## the crews wait for dry ground under them (and check again in a while)
	var w := global_transform * _line_point(top, depth, 1.0, 1.0)
	var wet := MapTerrain.water_at(StationGeo.s_of(w), w.x).x > -9000.0
	return wet


func _ground_depth(top: Vector3) -> float:
	var w := global_transform * top
	var s := StationGeo.s_of(w)
	return StationGeo.h_of(w) - maxf(MapTerrain.elevation(s, w.x), 0.0)


func _line_point(top: Vector3, L: float, k: float, sign_: float) -> Vector3:
	## a point k (0..1) down a line paid out to L: Coriolis on a load moving radially at v swings the line by
	## 2 omega v / g -- antispinward going down (local +Z: west), spinward coming up -- most at the load, so the
	## line bows (a parabola), not a straight slant
	var v := LOWER_SPEED if sign_ > 0.0 else RAISE_SPEED
	var lean := 2.0 * OMEGA * v / 9.8
	return top + Vector3(0.0, -L * k, sign_ * lean * L * k * k)


func _draw_line(h: Dictionary, top: Vector3) -> void:
	var im: ImmediateMesh = h.im
	im.clear_surfaces()
	if h.len <= 0.5:
		if h.cargo:
			(h.cargo as Node3D).visible = false
		return
	var sign_ := 1.0 if h.state == "lower" or h.state == "ground" else -1.0
	im.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	for k in 13:
		im.surface_add_vertex(_line_point(top, h.len, k / 12.0, sign_))
	im.surface_end()
	if h.cargo:
		var c := h.cargo as Node3D
		c.visible = true
		c.position = _line_point(top, h.len, 1.0, sign_) - Vector3(0, 4.6, 0)    # (hung by its bridle)


func _container() -> Node3D:
	var c := part("container").instantiate() as Node3D
	c.visible = false
	_near.add_child(c)
	_dress(c)
	return c


func _set_down(h: Dictionary) -> void:
	var c := h.cargo as Node3D
	h.cargo = null
	var at := c.global_position
	c.get_parent().remove_child(c)
	sys.drop_cargo(c, at)


# ------------------------------------------------------------------ snow
func set_snow(v: float) -> void:
	var was := snow > SNOW_MIN
	snow = v
	if (snow > SNOW_MIN) != was:
		_overlay_all()                 # (no snow: no overlay, no extra draws)
	if absf(v - _snow_shown) < 0.004:
		return
	_snow_shown = v
	_snow_mat.set_shader_parameter("snow", v)


func _overlay_all() -> void:
	var on := snow > SNOW_MIN
	_geoms = _geoms.filter(func(g) -> bool: return is_instance_valid(g))
	for g in _geoms:
		(g as GeometryInstance3D).material_overlay = _snow_mat if on else null


func _dress(n: Node) -> void:
	## the island's snow, over every mesh under n
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D and not c.name.begins_with("Water"):
			_geoms.append(c)
			if snow > SNOW_MIN:
				(c as GeometryInstance3D).material_overlay = _snow_mat


static var _vc_mats := {}


static func _vertex_colours(n: Node) -> void:
	## the island glbs (make_islands.py) carry their colour per vertex: their materials must use it
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is MeshInstance3D and (c as MeshInstance3D).mesh:
			var mi := c as MeshInstance3D
			for si in mi.mesh.get_surface_count():
				var m := mi.get_active_material(si) as StandardMaterial3D
				if m == null or m.vertex_color_use_as_albedo:
					continue
				if not _vc_mats.has(m):
					var d := m.duplicate() as StandardMaterial3D
					d.vertex_color_use_as_albedo = true
					d.vertex_color_is_srgb = true
					_vc_mats[m] = d
				mi.set_surface_override_material(si, _vc_mats[m])


static func _no_shadow(n: Node) -> void:
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			(c as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
