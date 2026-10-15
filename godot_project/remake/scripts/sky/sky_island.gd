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

const NEAR := 450.0
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
	_lark_pads.clear()
	_lark_mm = null


func _process(delta: float) -> void:
	Prof.begin("sky.island")
	_process_inner(delta)
	Prof.end("sky.island")


func _process_inner(delta: float) -> void:
	if tier <= 0 and _pending.is_empty() and _merging.is_empty() and _build.is_empty():
		return                                     # (a far island with nothing loading: nothing to do)
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
			_lark_step()


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
	_build.append(_build_links)
	_build.append(_build_signs)                    # (SkySigns: the island's lights after dark)
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
				RemakeBuilding.light_windows(l1, _glow_of(b))
				_ranges(l1, 0.0, LOD1_END)
				holder.add_child(l1)
				var l2: Node3D = ps2.instantiate()
				RemakeBuilding.prepare_lod(l2, base + ".lod2.glb")
				RemakeBuilding.light_windows(l2, _glow_of(b))
				_ranges(l2, LOD1_END, 0.0)
				_no_shadow(l2)
				holder.add_child(l2)
				_dress(holder)
				_blds.append({"b": b, "holder": holder, "lod1": l1, "lod2": l2, "full": null, "loading": false})))


static func _glow_of(b: Dictionary) -> Color:
	## a building's windows at night: its mood (make_islands.py, from the style's night moods), warmed toward lamplight
	var m = b.get("mood", "")
	var c := Color(m) if m is String and m != "" else RemakeBuilding.WINDOW_GLOW
	return c.lerp(RemakeBuilding.WINDOW_GLOW, 0.35)


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
				RemakeBuilding.light_windows(rb, _glow_of(e.b))
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


# ------------------------------------------------------------------ batching (an island moves every tick: every node
# on it moves too -- ~0.3 us a node plus a physics-server update a body.  Static pieces are merged into one mesh per
# material; parked larks are one impostor MultiMesh; collision shapes live on their body (shape owners), not as nodes.)
static var _part_surfs := {}         # part name -> [[mesh, surface, transform in the part, material], ...]
static var _part_marks := {}         # part name -> {node name: transform in the part}


static func _surfs_of(n: String) -> Array:
	if not _part_surfs.has(n):
		var inst := part(n).instantiate()
		var out: Array = []
		var marks := {}
		var stack: Array = [[inst, Transform3D.IDENTITY]]
		while not stack.is_empty():
			var it: Array = stack.pop_back()
			var nd: Node = it[0]
			var xf: Transform3D = it[1]
			for c in nd.get_children():
				if not (c is Node3D):
					continue
				var cx: Transform3D = xf * (c as Node3D).transform
				marks[str(c.name)] = cx
				if c is MeshInstance3D and (c as MeshInstance3D).mesh:
					var mi := c as MeshInstance3D
					for si in mi.mesh.get_surface_count():
						var m: Material = mi.material_override if mi.material_override else mi.mesh.surface_get_material(si)
						out.append([mi.mesh, si, cx, m])
				stack.append([c, cx])
		inst.free()
		_part_surfs[n] = out
		_part_marks[n] = marks
	return _part_surfs[n]


static func part_mark(n: String, node_name: String) -> Transform3D:
	## a named node's transform within a part (a hoist's hook, a launcher's muzzle)
	_surfs_of(n)
	return _part_marks[n].get(node_name, Transform3D.IDENTITY)


static func batch_mesh(items: Array) -> ArrayMesh:
	## items: [part name, Transform3D] -> one ArrayMesh, a surface per material
	var groups := {}                    # material -> SurfaceTool
	var mats := {}
	for it in items:
		for sf in _surfs_of(it[0]):
			var m: Material = sf[3]
			var key := "%d|%d" % [m.get_instance_id() if m else 0, 1 if (sf[0] as Mesh).surface_get_format(sf[1]) & Mesh.ARRAY_FORMAT_BONES else 0]
			if not groups.has(key):
				var st := SurfaceTool.new()
				st.begin(Mesh.PRIMITIVE_TRIANGLES)
				groups[key] = st
				mats[key] = m
			(groups[key] as SurfaceTool).append_from(sf[0], sf[1], (it[1] as Transform3D) * (sf[2] as Transform3D))
	var am := ArrayMesh.new()
	for key in groups:
		(groups[key] as SurfaceTool).commit(am)
		if mats[key]:
			am.surface_set_material(am.get_surface_count() - 1, mats[key])
	return unskinned(am)


func _batched(n: String, items: Array) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = n
	mi.mesh = batch_mesh(items)
	_near.add_child(mi)
	_dress(mi)
	return mi


static func add_box(body: CollisionObject3D, size: Vector3, xf: Transform3D) -> void:
	## a box on body without a node of its own
	var box := BoxShape3D.new()
	box.size = size
	var o := body.create_shape_owner(body)
	body.shape_owner_add_shape(o, box)
	body.shape_owner_set_transform(o, xf)


# ------------------------------------------------------------------ parked larks
# Each pad's lark is drawn as one instance of a merged impostor (the craft's meshes in this clan's livery, baked once
# per livery); within LARK_REAL of the player, or when a plumb takes one up, the real RemakeFleetCraft stands there.
const LARK_REAL := 40.0
const LARK_DROP := 70.0
static var _lark_meshes := {}        # livery key -> ArrayMesh
var _lark_pads: Array = []           # {at: Transform3D, real: craft or null, away: bool}
var _lark_mm: MultiMeshInstance3D
var _lark_t := 0.0


func _lark_impostor() -> ArrayMesh:
	var cols: Array = canon.get("colors", [])
	var key := str(cols)
	if _lark_meshes.has(key):
		return _lark_meshes[key]
	var holder := Node3D.new()
	add_child(holder)
	var k := RemakeFleetCraft.new("sky_skiff")
	k.process_mode = Node.PROCESS_MODE_DISABLED
	holder.add_child(k)
	if cols.size() >= 3:
		k.set_livery(cols)
	var inv := k.global_transform.affine_inverse()
	var groups := {}
	var mats := {}
	for mi in k.find_children("*", "MeshInstance3D", true, false):
		var m3 := mi as MeshInstance3D
		if m3.mesh == null or not m3.is_visible_in_tree():
			continue
		var rel := inv * m3.global_transform
		for si in m3.mesh.get_surface_count():
			var m: Material = m3.get_active_material(si)
			# (one merge per material and per skinned-or-not: a SurfaceTool mixing them drops the weights' sizes)
			var gk := "%d|%d" % [m.get_instance_id() if m else 0, 1 if m3.mesh.surface_get_format(si) & Mesh.ARRAY_FORMAT_BONES else 0]
			if not groups.has(gk):
				var st := SurfaceTool.new()
				st.begin(Mesh.PRIMITIVE_TRIANGLES)
				groups[gk] = st
				mats[gk] = m
			(groups[gk] as SurfaceTool).append_from(m3.mesh, si, rel)
	var am := ArrayMesh.new()
	for gk in groups:
		(groups[gk] as SurfaceTool).commit(am)
		if mats[gk]:
			am.surface_set_material(am.get_surface_count() - 1, mats[gk])
	holder.free()
	am = unskinned(am)                         # (the craft's parts carry skin weights: no skeleton in a MultiMesh)
	_lark_meshes[key] = am
	return am


static func unskinned(am: ArrayMesh) -> ArrayMesh:
	## the same mesh without bone indices and weights
	var out := ArrayMesh.new()
	for i in am.get_surface_count():
		var arr := am.surface_get_arrays(i)
		arr[Mesh.ARRAY_BONES] = null
		arr[Mesh.ARRAY_WEIGHTS] = null
		out.add_surface_from_arrays(am.surface_get_primitive_type(i), arr)
		out.surface_set_material(i, am.surface_get_material(i))
	return out


func _build_larks() -> void:
	if _near == null or _lark_pads.is_empty():
		return
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = _lark_impostor()
	mm.instance_count = _lark_pads.size()
	_lark_mm = MultiMeshInstance3D.new()
	_lark_mm.name = "Larks"
	_lark_mm.multimesh = mm
	_near.add_child(_lark_mm)
	_ranges(_lark_mm, 0.0, 600.0)
	_lark_show()


func _lark_show() -> void:
	if _lark_mm == null:
		return
	var mm := _lark_mm.multimesh
	for i in _lark_pads.size():
		var pd: Dictionary = _lark_pads[i]
		mm.set_instance_transform(i, pd.at if pd.real == null and not pd.away else Transform3D(Basis.from_scale(Vector3.ONE * 1e-4), pd.at.origin))


func _lark_step() -> void:
	## (tier 2, every half second) real craft on the pads the player is near; impostors elsewhere
	if _near == null or _lark_pads.is_empty() or sys.player == null:
		return
	var lp := global_transform.affine_inverse() * (sys.player as Node3D).global_position
	var changed := false
	for pd in _lark_pads:
		if pd.away:
			continue
		var d: float = (pd.at.origin as Vector3).distance_to(lp)
		if pd.real == null and d < LARK_REAL:
			pd.real = _spawn_lark(pd.at)
			changed = true
		elif pd.real != null and d > LARK_DROP and is_instance_valid(pd.real):
			var k: RemakeAirVehicle = pd.real
			if k.pilot == null and k.fly_input.is_empty() and k.position.distance_to(pd.at.origin) < 1.0:
				larks_parked.erase(k)
				k.queue_free()
				pd.real = null
				changed = true
	if changed:
		_lark_show()


func _spawn_lark(at: Transform3D) -> RemakeFleetCraft:
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
	return k


func take_lark() -> RemakeFleetCraft:
	## a lark for a plumb's flight: the real craft on a pad (made now if the pad shows its impostor)
	for pd in _lark_pads:
		if pd.away:
			continue
		if pd.real == null:
			pd.real = _spawn_lark(pd.at)
		var k: RemakeFleetCraft = pd.real
		larks_parked.erase(k)
		pd.away = true
		pd.real = null
		_lark_show()
		return k
	return null


func return_lark(k: Node3D, at: Transform3D) -> void:
	## a plumb back on its pad
	for pd in _lark_pads:
		if pd.away and (pd.at.origin as Vector3).distance_to(at.origin) < 0.5:
			pd.away = false
			pd.real = k
			larks_parked.append(k)
			_lark_show()
			return
	larks_parked.append(k)


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


func radius() -> float:
	## m from its centre to its furthest dock face
	var f: Dictionary = data.faces
	return maxf(maxf(absf(float(f.N)), absf(float(f.S))), maxf(absf(float(f.E)), absf(float(f.W))))


func inside(lp: Vector3, margin := 2.0) -> bool:
	## lp (local) over the deck's bounds, and margin m past them
	var f: Dictionary = data.faces
	return lp.x > float(f.N) - margin and lp.x < float(f.S) + margin and lp.z > float(f.E) - margin and lp.z < float(f.W) + margin


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
		mi.material_override = _pond_mat(lv)
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_near.add_child(mi)


var _pond_mats := {}
var _height_tex: ImageTexture


func _pond_mat(level: float) -> ShaderMaterial:
	## the frosty pond (sky_pond.gdshader): it reads the island's height grid to know how deep it is where
	if _pond_mats.has(level):
		return _pond_mats[level]
	if _height_tex == null and not _hg.is_empty():
		var nx: int = _hg.nx
		var nz: int = _hg.nz
		var img := Image.create(nx, nz, false, Image.FORMAT_RF)
		for iz in nz:
			for ix in nx:
				img.set_pixel(ix, iz, Color(_h(ix, iz, nx), 0, 0))
		_height_tex = ImageTexture.create_from_image(img)
	var m := ShaderMaterial.new()
	m.shader = load("res://remake/shaders/sky_pond.gdshader")
	m.set_shader_parameter("level", level)
	if _height_tex:
		var st: float = _hg.step
		# (sample i sits at x0 + i * step: the texture's cell i spans half a step either side)
		m.set_shader_parameter("grid", Vector4(float(_hg.x0) - st * 0.5, float(_hg.z0) - st * 0.5, int(_hg.nx) * st, int(_hg.nz) * st))
		m.set_shader_parameter("height_tex", _height_tex)
	_pond_mats[level] = m
	return m


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
			add_box(body, Vector3(v.length(), 1.4, 0.12),
				Transform3D(Basis(xa.normalized(), yb, zb), Vector3((p0.x + p1.x) * 0.5, (y0 + y1) * 0.5 + 0.7, (p0.y + p1.y) * 0.5)))
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
	var hubs: Array = []
	for b in data.balloons:
		var top := Vector3(b.x, sys.BALLOON_BASE, b.z)
		hubs.append(["balloon_hub", Transform3D(Basis(), top)])
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
	_batched("Hubs", hubs)


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
				var other := _partner_of(b.side, al)
				if other >= 0:
					br.match(float(SkyBridge.styles().get(sys.islands[other].bridge_style(), {}).get("nose_y", 0.0)))
		_dress(br)


func _partner_of(side: String, along: float) -> int:
	## the island lashed to this one at that bridge (-1: none)
	for e in sys.drift.raft_of(idx).edges:
		if e.a == idx and e.side == side and absf(float(e.along_a) - along) < 0.01:
			return e.b
		if e.b == idx and SkyDrift._opp(e.side) == side and absf(float(e.along_b) - along) < 0.01:
			return e.a
	return -1


func set_bridge(side: String, along: float, down: bool, partner_style := "") -> void:
	var br: SkyBridge = bridge_at.get("%s:%.2f" % [side, along])
	if br:
		br.target = 1.0 if down else 0.0
		if down and partner_style != "":
			br.match(float(SkyBridge.styles().get(partner_style, {}).get("nose_y", 0.0)))


func bridge_style() -> String:
	return data.get("bridge_style", canon.get("bridge_style", "bascule_timber"))


func _build_links() -> void:
	## The warren's links between buildings (make_islands.py "links"): skybridges (steel deck, rails), planks (a narrow
	## timber walk with rope rails) and covered alleys (a passage with low walls and a roof) -- one mesh per material
	## for the island, and one body holding a box per walking surface, wall and roof.
	var links: Array = data.get("links", [])
	if links.is_empty():
		return
	var sts := {}
	var body := StaticBody3D.new()
	body.name = "LinksBody"
	for l in links:
		var a := Vector3(l.from[0], l.from[1], l.from[2])
		var b := Vector3(l.to[0], l.to[1], l.to[2])
		var L := a.distance_to(b)
		if L < 0.2:
			continue
		var w: float = l.get("width", 1.5)
		var x := (b - a) / L
		var side := x.cross(Vector3.UP).normalized()
		if side.length() < 0.5:
			continue
		var up := side.cross(x).normalized()
		var bas := Basis(x, up, side)
		var mid := (a + b) * 0.5
		match str(l.kind):
			"plank":
				_lbox(sts, "plank", body, bas, mid + up * -0.04, Vector3(L + 0.4, 0.08, w))
				for sgn in [-1.0, 1.0]:
					_lbox(sts, "rope", null, bas, mid + up * 0.95 + side * (w * 0.5 * sgn), Vector3(L, 0.03, 0.03))
					_lbox(sts, "rope", body, bas, mid + up * 0.55 + side * (w * 0.5 * sgn), Vector3(L, 1.1, 0.04), true)
			"covered_alley":
				_lbox(sts, "alley", body, bas, mid + up * -0.1, Vector3(L + 0.3, 0.2, w + 0.3))
				for sgn in [-1.0, 1.0]:
					_lbox(sts, "alley", body, bas, mid + up * 0.55 + side * ((w * 0.5 + 0.08) * sgn), Vector3(L, 1.1, 0.16))
				_lbox(sts, "alley_roof", body, bas, mid + up * 2.55, Vector3(L + 0.6, 0.18, w + 0.7))
				for sgn in [-1.0, 1.0]:
					for e in [-0.5, 0.5]:
						_lbox(sts, "alley", null, bas, mid + x * (L * e) + up * 1.8 + side * ((w * 0.5 + 0.08) * sgn), Vector3(0.18, 1.5, 0.18))
			_:
				_lbox(sts, "bridge", body, bas, mid + up * -0.08, Vector3(L + 0.4, 0.16, w))
				for sgn in [-1.0, 1.0]:
					_lbox(sts, "rail", body, bas, mid + up * 0.55 + side * ((w * 0.5 - 0.03) * sgn), Vector3(L, 1.1, 0.06), true)
					_lbox(sts, "rail", null, bas, mid + up * 1.1 + side * ((w * 0.5 - 0.03) * sgn), Vector3(L, 0.06, 0.1))
	var cols := {"plank": Color(0.52, 0.38, 0.24), "rope": Color(0.62, 0.55, 0.42), "alley": Color(0.70, 0.62, 0.52),
		"alley_roof": Color(0.38, 0.30, 0.26), "bridge": Color(0.30, 0.32, 0.36), "rail": Color(0.22, 0.24, 0.27)}
	for k in sts:
		var mi := MeshInstance3D.new()
		mi.name = "Links_" + k
		mi.mesh = (sts[k] as SurfaceTool).commit()
		mi.material_override = _mat("sky_link_" + k, cols.get(k, Color.GRAY))
		_near.add_child(mi)
		_dress(mi)
	_near.add_child(body)


func _lbox(sts: Dictionary, k: String, body: StaticBody3D, bas: Basis, c: Vector3, size: Vector3, invisible := false) -> void:
	## an oriented box: drawn (unless invisible: a rail's collision panel) and, with a body, solid
	var xf := Transform3D(bas, c)
	if not invisible:
		if not sts.has(k):
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			sts[k] = st
		var bm := BoxMesh.new()
		bm.size = size
		(sts[k] as SurfaceTool).append_from(bm, 0, xf)
	if body:
		add_box(body, size, xf)


func _build_props() -> void:
	## pads, cloud nets, line launchers and hoists: one merged mesh (they don't move); the larks as impostors
	var larks: int = canon.get("aerostats", 2)
	var items: Array = []
	for p in data.get("pads", []):
		var at := Transform3D(Basis(Vector3.UP, float(p.yaw)), Vector3(p.x, p.get("y", deck_y(p.x, p.z)) + 0.02, p.z))
		items.append(["pad", at])
		if larks > 0:
			larks -= 1
			_lark_pads.append({"at": at, "real": null, "away": false})
	for c in data.get("cloud_nets", []):
		items.append(["cloud_net", Transform3D(Basis(Vector3.UP, float(c[3])), Vector3(c[0], c[1], c[2]))])
	for l in data.get("launchers", []):
		var yaw: float = {"N": -PI * 0.5, "S": PI * 0.5, "E": PI, "W": 0.0}[l.side]
		items.append(["launcher", Transform3D(Basis(Vector3.UP, yaw), Vector3(l.x, deck_y(l.x, l.z), l.z))])
	var hook := part_mark("hoist", "hook")
	for h in data.get("hoists", []):
		var hx := Transform3D(Basis(Vector3.UP, float(h.yaw)), Vector3(h.x, deck_y(h.x, h.z), h.z))
		items.append(["hoist", hx])
		var im := ImmediateMesh.new()
		var line := MeshInstance3D.new()
		line.mesh = im
		line.material_override = _mat("sky_tether", Color(0.2, 0.18, 0.15))
		line.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_near.add_child(line)
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(data.id + str(h.x))
		_hoists.append({"top": (hx * hook).origin, "im": im, "line": line, "state": "idle", "t": rng.randf_range(20.0, 240.0),
			"len": 0.0, "cargo": null, "up": rng.randf() < 0.6, "rng": rng})
	_batched("Props", items)
	_build.push_front(_build_larks)                # (the impostor bakes a craft once per livery: a frame of its own)


# ------------------------------------------------------------------ cargo
func _hoist_step(delta: float) -> void:
	for h in _hoists:
		var top: Vector3 = h.top
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


var _phys_on := true
var _phys_seen := -1


func set_physics_active(on: bool) -> void:
	## Only the islands near the player keep their collision in the physics world: every body on an island moves
	## every tick with it, and a moved body is put back into the broadphase -- a raft's worth of decks, buildings,
	## fences and bridges cost ~8 ms a tick.  Off: removed (DISABLE_MODE_REMOVE), drawn as ever.
	if _near == null:
		_phys_on = true
		_phys_seen = -1
		return
	var n := _near.get_child_count()
	if on == _phys_on and (on or n == _phys_seen):
		return
	_phys_on = on
	_phys_seen = n
	for b in _near.find_children("*", "CollisionObject3D", true, false):
		if b is RemakeAirVehicle:
			continue                      # (a lark keeps its own body)
		var co := b as CollisionObject3D
		co.disable_mode = CollisionObject3D.DISABLE_MODE_REMOVE
		co.process_mode = Node.PROCESS_MODE_INHERIT if on else Node.PROCESS_MODE_DISABLED


static func _no_shadow(n: Node) -> void:
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			(c as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


# ------------------------------------------------------------------ lights after dark (SkySigns, sky_glitter)
var _glitter_mat: ShaderMaterial
var _glittered := {}                 # the LOD node -> true once its glitter twins are in


func _build_signs() -> void:
	## every store's sign, every building's mood lighting, the string lights: built over the next frames
	if _near == null:
		return
	var s := SkySigns.new()
	_near.add_child(s)
	s.setup(self)


func set_night(n: float) -> void:
	## (SkyIslands, every second or so) far off at night the island glitters: its far and mid LODs get twins drawn
	## with sky_glitter (lit windows, roof signs, rim bulbs) -- added the first night they're seen, shown only at night
	var on := n > 0.02
	var lods: Array = [_far, _mid]
	# (the buildings' own distant forms glow by themselves now: lod_vc.gdshader)
	for lod in lods:
		if lod == null or not is_instance_valid(lod):
			continue
		if on and not _glittered.has(lod):
			_glitter(lod)
		for g in (lod as Node).get_meta("glitter", []):
			if is_instance_valid(g):
				(g as Node3D).visible = on


func _glitter(lod: Node3D) -> void:
	_glittered[lod] = true
	if _glitter_mat == null:
		_glitter_mat = ShaderMaterial.new()
		_glitter_mat.shader = load("res://remake/shaders/sky_glitter.gdshader")
		_glitter_mat.set_shader_parameter("seed", float(idx) * 1.37)
		var cols: Array = canon.get("colors", [])
		if not cols.is_empty():
			_glitter_mat.set_shader_parameter("mood", Color(str(cols[0])).lightened(0.35))
	var twins: Array = []
	var stack: Array[Node] = [lod]
	while not stack.is_empty():
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is MeshInstance3D and (c as MeshInstance3D).mesh and not c.has_meta("glitter_twin"):
			var t := MeshInstance3D.new()
			t.mesh = (c as MeshInstance3D).mesh
			t.material_override = _glitter_mat
			var gi := c as GeometryInstance3D              # (a twin shows over the same distances as its LOD)
			t.visibility_range_begin = gi.visibility_range_begin
			t.visibility_range_begin_margin = gi.visibility_range_begin_margin
			t.visibility_range_end = gi.visibility_range_end
			t.visibility_range_end_margin = gi.visibility_range_end_margin
			t.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			t.set_meta("glitter_twin", true)
			c.add_child(t)
			twins.append(t)
	lod.set_meta("glitter", twins)

