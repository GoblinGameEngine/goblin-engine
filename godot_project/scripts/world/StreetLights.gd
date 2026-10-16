extends Node3D
class_name StreetLights

## Street lighting (research/night/00_brief.md; data: remake/street_lamps.json from tools/street_lamps.py).
## The user, 2026-10-14: "The towns need streetlights. the south coast towns need colored lights in the trees by the
## beach and on the street along the beach ... There needs to be good artificial illumination on the streets and in the
## cities and town centers. All streets with buildsings need lights."
##
##   lamps     a post on every street with buildings: 0 street (a cobra head over the road), 1 town centre (an
##             ornamental post with two lanterns: closer, warmer, brighter), 2 alley (a short gooseneck), 3 the south
##             coast's beach streets (a white post and a globe)
##   strings   festoons: across the town centres' main streets (warm) and along the south coast's beach streets and
##             promenades (multicolour, twinkling)
##   palms     palms along the beach streets and promenades (there were no trees by those beaches), coloured lights
##             wound up their trunks and out along their fronds
##   walk lamps  the coastal walks' own posts (CoastalWalks draws them): bulbs, and their share of the real lights
##
## Drawn in two tiers round the player:
##   near (CELL m cells within NEAR_KEEP m): the posts and palms (MultiMesh), the pools of light on the ground (one
##        merged mesh: street_pool.gdshader) and the bulbs (street_bulb.gdshader, nearer than CUT m)
##   far  (FAR_CELL m cells within FAR_KEEP m): the bulbs alone, beyond CUT m -- so a town reads as lit from km off
## Built on a worker, a cell at a time.  The real light: N_LIGHTS OmniLight3Ds, every 0.5 s on the lamps nearest the
## player (people, cars and walls near you are truly lit).  Night only: everything fades in at dusk.

const CELL := 400.0
const NEAR_KEEP := 750.0
const NEAR_FREE := 950.0
const FAR_CELL := 1600.0
const FAR_KEEP := 4400.0
const FAR_FREE := 5000.0
const CUT := 820.0                    # m: near bulbs nearer, far bulbs further
const POST_FAR := 600.0
const PALM_FAR := 900.0
const N_LIGHTS := 28
const LIGHT_R := 110.0

# per kind: [bulb positions (local: +y up, -z toward the road), bulb colour, bulb size, pool radius, pool strength,
#            real light range, real light energy]
const HEAD := {
	0: [[Vector3(0, 7.75, -2.2)], Color(1.0, 0.86, 0.66), 1.2, 12.0, 0.62, 22.0, 3.2],
	1: [[Vector3(-0.55, 4.15, 0.0), Vector3(0.55, 4.15, 0.0)], Color(1.0, 0.74, 0.44), 0.95, 9.5, 0.75, 16.0, 3.0],
	2: [[Vector3(0, 3.3, -0.6)], Color(1.0, 0.8, 0.55), 0.75, 6.5, 0.55, 11.0, 2.2],
	3: [[Vector3(0, 5.85, -1.2)], Color(1.0, 0.9, 0.74), 1.1, 11.5, 0.8, 18.0, 3.0],
	4: [[Vector3(0, 4.4, 0.0)], Color(1.0, 0.9, 0.7), 0.85, 0.0, 0.0, 12.0, 2.2],
}
const BEACH_COLS := [Color(1.0, 0.2, 0.25), Color(0.25, 1.0, 0.35), Color(0.3, 0.5, 1.0), Color(1.0, 0.85, 0.2),
	Color(1.0, 0.3, 0.9), Color(0.2, 0.95, 1.0), Color(1.0, 0.55, 0.15)]
const WARM := Color(1.0, 0.82, 0.52)
## (2026-10-16, the user: pools of light spilling from the lamps, dark between them -- no ambient lift).  The first try
##  (reach x1.3, strength x1.8) washed Calder's asphalt out white under each lamp (coordinator review): the pools are
##  additive and unshaded, and the real OmniLights near the player light the same road.  Now the lamps' own reach and
##  strength, a tighter core (POOL_FALLOFF) and POOL_SHADER_GAIN on the whole pass.
const POOL_REACH := 1.0
const POOL_GAIN := 1.0
const POOL_SHADER_GAIN := 0.55
const POOL_FALLOFF := 2.4
## lit storefronts: a pool on the pavement in front of every shop sign below SHOP_MAX_Y (remake/signs/city_signs.json,
## the SIGNS agent's quads in each building's placement frame; plaques skipped), SHOP_OUT m out from the board
const SHOP_OUT := 2.2
const SHOP_MAX_Y := 6.0
const SHOP_R := 4.0
const SHOP_COL := Color(1.0, 0.86, 0.62, 0.55)

var target: Node3D
var ready_ := false
var _lamps: Array = []
var _strings: Array = []
var _palms: Array = []
var _walk: Array = []
var _wkinds: Array = []
var _shops := PackedFloat32Array()   # [s, x] per lit storefront (its pool centre)
var _near_items := {}                 # Vector2i -> {l, s, p, w: [index]}
var _far_items := {}
var _near_nodes := {}                 # Vector2i -> [Node]
var _far_nodes := {}
var _near_lights := {}                # Vector2i -> [[world head, kind]]
var _task := -1
var _job := {}
var _check_t := 0.0
var _light_t := 0.0
var _night := 0.0
var _sky: Node
var _lights: Array[OmniLight3D] = []
var _post_mesh := {}                  # kind -> Mesh
var _palm_mesh: Mesh
var _bulb_quad: QuadMesh
var _near_bulb_mat: ShaderMaterial
var _far_bulb_mat: ShaderMaterial
var _pool_mat: ShaderMaterial
var _post_mat := {}
var _palm_mat: StandardMaterial3D


func setup() -> void:
	name = "StreetLights"
	_build_meshes()
	_task = WorkerThreadPool.add_task(_load, false, "street lights data")
	for i in N_LIGHTS:
		var l := OmniLight3D.new()
		l.shadow_enabled = false
		l.visible = false
		l.omni_attenuation = 1.3
		add_child(l)
		_lights.append(l)
	set_process(true)


func _load() -> void:
	## (worker) the data, sorted into near and far cells
	var d: Dictionary = DataFile.json("res://remake/street_lamps.json")
	if d == null or d.is_empty():
		return
	_lamps = d.lamps
	_strings = d.strings
	_palms = d.palms
	_walk = d.get("walk_lamps", [])
	_wkinds = d.get("walk_kinds", [])
	for i in range(0, _lamps.size(), 4):
		_bucket("l", i, _lamps[i], _lamps[i + 1])
	for i in range(0, _strings.size(), 7):
		_bucket("s", i, _strings[i], _strings[i + 1])
	for i in range(0, _palms.size(), 4):
		_bucket("p", i, _palms[i], _palms[i + 1])
	for i in range(0, _walk.size(), 3):
		_bucket("w", i, _walk[i], _walk[i + 1])
	_load_shops()
	for i in range(0, _shops.size(), 2):
		_bucket("f", i, _shops[i], _shops[i + 1])


func _load_shops() -> void:
	## (worker) a pool centre in front of each storefront sign: the sign's quad (building frame) pushed SHOP_OUT along its
	## outward normal, through the building's placement transform (as RemakeWorld._entry places it)
	var d = DataFile.json("res://remake/signs/city_signs.json")
	if not (d is Dictionary):
		return
	var bs: Dictionary = d.get("buildings", {})
	for id in bs:
		var i := Placement.index(str(id))
		if i < 0:
			continue
		var ps := Placement.s(i)
		var px := Placement.x(i)
		var h := MapTerrain.pad_height(str(id))
		if is_nan(h):
			h = MapTerrain.elevation(ps, px)
		var xf := Transform3D(StationGeo.basis(ps, Placement.yaw(i)), StationGeo.point(ps, px, h))
		for q in bs[id].get("quads", []):
			if str(q.get("type", "")) == "plaque" or float(q.c[1]) > SHOP_MAX_Y:
				continue
			var n := Vector3(q.r[0], q.r[1], q.r[2]).cross(Vector3(q.u[0], q.u[1], q.u[2])).normalized()
			var w := xf * (Vector3(q.c[0], 0.0, q.c[2]) + Vector3(n.x, 0.0, n.z).normalized() * SHOP_OUT)
			_shops.append(StationGeo.s_of(w))
			_shops.append(w.x)


func _bucket(k: String, i: int, s: float, x: float) -> void:
	for pair in [[_near_items, CELL], [_far_items, FAR_CELL]]:
		var c := Vector2i(floori(fposmod(s, StationGeo.CIRC) / float(pair[1])), floori(x / float(pair[1])))
		var cells: Dictionary = pair[0]
		if not cells.has(c):
			cells[c] = {"l": [], "s": [], "p": [], "w": [], "f": []}
		cells[c][k].append(i)


# ------------------------------------------------------------------ streaming
func _process(delta: float) -> void:
	if not ready_:
		if _task >= 0 and WorkerThreadPool.is_task_completed(_task):
			WorkerThreadPool.wait_for_task_completion(_task)
			_task = -1
			ready_ = true
			print("StreetLights: %d lamps, %d festoons, %d palms, %d walk lamps" % [_lamps.size() / 4, _strings.size() / 7,
				_palms.size() / 4, _walk.size() / 3])
		return
	_light_t -= delta
	if _light_t <= 0.0:
		_light_t = 0.5
		_update_night()
		_place_lights()
	if _task >= 0:
		if not WorkerThreadPool.is_task_completed(_task):
			return
		WorkerThreadPool.wait_for_task_completion(_task)
		_task = -1
		_commit(_job)
		_job = {}
	_check_t -= delta
	if _check_t > 0.0 or target == null:
		return
	_check_t = 0.3
	var p := target.global_position
	var sp := StationGeo.s_of(p)
	var xp := p.x
	# free what's gone out of range
	for c in _near_nodes.keys():
		if _cell_dist(c, CELL, sp, xp) > NEAR_FREE:
			_free(_near_nodes, c)
			_near_lights.erase(c)
	for c in _far_nodes.keys():
		if _cell_dist(c, FAR_CELL, sp, xp) > FAR_FREE:
			_free(_far_nodes, c)
	# the nearest wanted cell not built yet: near first
	var best := {}
	var bd := INF
	for c in _near_items:
		if _aloft:
			break
		if _near_nodes.has(c):
			continue
		var d := _cell_dist(c, CELL, sp, xp)
		if d < NEAR_KEEP and d < bd:
			bd = d
			best = {"tier": "near", "c": c}
	if best.is_empty():
		for c in _far_items:
			if _far_nodes.has(c):
				continue
			var d := _cell_dist(c, FAR_CELL, sp, xp)
			if d < FAR_KEEP and d < bd:
				bd = d
				best = {"tier": "far", "c": c}
	if best.is_empty():
		return
	(_near_nodes if best.tier == "near" else _far_nodes)[best.c] = []      # (claimed)
	_job = best
	_task = WorkerThreadPool.add_task(_build.bind(best), false, "street lights cell")


func _cell_dist(c: Vector2i, size: float, sp: float, xp: float) -> float:
	var ds := StationGeo.wrap_ds(sp - (c.x * size + size * 0.5))
	var dx := xp - (c.y * size + size * 0.5)
	return Vector2(maxf(absf(ds) - size * 0.5, 0.0), maxf(absf(dx) - size * 0.5, 0.0)).length()


func _free(nodes: Dictionary, c: Vector2i) -> void:
	for n in nodes[c]:
		if is_instance_valid(n):
			(n as Node).queue_free()
	nodes.erase(c)


# ------------------------------------------------------------------ building (worker)
func _lamp_xf(i: int) -> Transform3D:
	var s: float = _lamps[i]
	var x: float = _lamps[i + 1]
	return Transform3D(StationGeo.basis(s, _lamps[i + 2]), StationGeo.point(s, x, MapTerrain.elevation(s, x)))


func _build(job: Dictionary) -> void:
	var near: bool = job.tier == "near"
	var it: Dictionary = (_near_items if near else _far_items)[job.c]
	var bx: Array[Transform3D] = []
	var bc: Array[Color] = []
	var bu: Array[Color] = []
	var posts := {0: [], 1: [], 2: [], 3: []}
	var palms: Array[Transform3D] = []
	var lights := []
	var pool := SurfaceTool.new()
	var pooled := false
	if near:
		pool.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in it.l:
		var kind: int = int(_lamps[i + 3])
		var xf := _lamp_xf(i)
		var hd: Array = HEAD[kind]
		var ph := fposmod(float(_lamps[i]) * 0.137 + float(_lamps[i + 1]) * 0.71, 1.0)
		for lp in hd[0]:
			bx.append(Transform3D(Basis(), xf * (lp as Vector3)))
			bc.append(hd[1])
			bu.append(Color(0.0, ph, float(hd[2]), 0.0))
		if near:
			posts[kind].append(xf)
			var centre: Vector3 = hd[0][0]
			if kind == 1:
				centre = Vector3.ZERO
			var head: Vector3 = xf * Vector3(centre.x, 0.0, centre.z)
			_pool(pool, float(_lamps[i]) + 0.0, head, float(hd[3]) * POOL_REACH, Color(hd[1], minf(float(hd[4]) * POOL_GAIN, 1.6)))
			pooled = true
			lights.append([xf * (hd[0][0] as Vector3), kind])
	for i in it.w:
		var s: float = _walk[i]
		var x: float = _walk[i + 1]
		var kd: String = str(_wkinds[int(_walk[i + 2])]) if int(_walk[i + 2]) < _wkinds.size() else "promenade"
		var z := CoastalWalks._deck_z(kd, s, x)
		var head := StationGeo.point(s, x, z + 4.4)
		bx.append(Transform3D(Basis(), head))
		bc.append(HEAD[4][1])
		bu.append(Color(0.0, fposmod(s * 0.31, 1.0), HEAD[4][2], 0.0))
		if near:
			lights.append([head, 4])
	if near:
		for i in it.f:
			var cs: float = _shops[i]
			var cx: float = _shops[i + 1]
			_pool(pool, cs, StationGeo.point(cs, cx, MapTerrain.elevation(cs, cx)), SHOP_R, SHOP_COL)
			pooled = true
	for i in it.s:
		_festoon(i, bx, bc, bu)
	for i in it.p:
		var s: float = _palms[i]
		var x: float = _palms[i + 1]
		if MapTerrain.water_depth(s, x) > 0.05:
			continue
		var sc: float = _palms[i + 3]
		var xf := Transform3D(StationGeo.basis(s, _palms[i + 2]).scaled(Vector3.ONE * sc), StationGeo.point(s, x, MapTerrain.elevation(s, x) - 0.1))
		if near:
			palms.append(xf)
		_palm_lights(xf, i, bx, bc, bu)
	job["bulbs"] = [bx, bc, bu]
	job["posts"] = posts
	job["palms"] = palms
	job["lights"] = lights
	job["pool"] = pool.commit_to_arrays() if pooled else []


func _pool(st: SurfaceTool, _s: float, centre: Vector3, r: float, col: Color) -> void:
	## a pool of light: a fan of 8 triangles on the ground round centre (each corner on the terrain)
	if r <= 0.0:
		return
	var s := StationGeo.s_of(centre)
	var up := StationGeo.up(s)
	var fwd := StationGeo.forward(s)
	var ax := Vector3.RIGHT
	var ring: Array[Vector3] = []
	var uvs: Array[Vector2] = []
	for k in 8:
		var a := TAU * k / 8.0
		var o := (ax * cos(a) + fwd * sin(a)) * r
		var q := centre + o
		var qs := StationGeo.s_of(q)
		ring.append(StationGeo.point(qs, q.x, MapTerrain.elevation(qs, q.x) + 0.07))
		uvs.append(Vector2(0.5 + 0.5 * cos(a), 0.5 + 0.5 * sin(a)))
	var cs := StationGeo.s_of(centre)
	var c := StationGeo.point(cs, centre.x, MapTerrain.elevation(cs, centre.x) + 0.07)
	st.set_normal(up)
	for k in 8:
		st.set_color(col)
		st.set_uv(Vector2(0.5, 0.5))
		st.add_vertex(c)
		st.set_color(col)
		st.set_uv(uvs[(k + 1) % 8])
		st.add_vertex(ring[(k + 1) % 8])
		st.set_color(col)
		st.set_uv(uvs[k])
		st.add_vertex(ring[k])


func _festoon(i: int, bx: Array[Transform3D], bc: Array[Color], bu: Array[Color]) -> void:
	var s0: float = _strings[i]
	var x0: float = _strings[i + 1]
	var s1: float = _strings[i + 3]
	var x1: float = _strings[i + 4]
	var scheme := int(_strings[i + 6])
	var a := StationGeo.point(s0, x0, MapTerrain.elevation(s0, x0) + float(_strings[i + 2]))
	var b := StationGeo.point(s1, x1, MapTerrain.elevation(s1, x1) + float(_strings[i + 5]))
	var L := a.distance_to(b)
	var n := maxi(3, int(L / 1.3))
	var down := -StationGeo.up(StationGeo.s_of((a + b) * 0.5))
	var sag := 0.35 + L * 0.035
	for k in n + 1:
		var f := k / float(n)
		var p := a.lerp(b, f) + down * sag * 4.0 * f * (1.0 - f)
		bx.append(Transform3D(Basis(), p))
		if scheme == 1:
			bc.append(BEACH_COLS[(k + i) % BEACH_COLS.size()])
			bu.append(Color(1.0, fposmod(f * 3.0 + s0 * 0.01, 1.0), 0.32, 1.0))
		else:
			bc.append(WARM if k % 5 != 0 else Color(1.0, 0.6, 0.25))
			bu.append(Color(3.0, fposmod(f + s0 * 0.003, 1.0), 0.26, 0.55))


func _palm_lights(xf: Transform3D, i: int, bx: Array[Transform3D], bc: Array[Color], bu: Array[Color]) -> void:
	## lights wound up the trunk, then out along the fronds
	var lean := PALM_LEAN
	for k in 24:
		var y := 0.4 + k * 0.29
		var a := k * 1.7
		var r := 0.24 * (1.0 - y / 14.0)
		var p := Vector3(lean * pow(y / PALM_H, 1.6) + r * cos(a), y, r * sin(a))
		bx.append(Transform3D(Basis(), xf * p))
		bc.append(BEACH_COLS[(k + i) % BEACH_COLS.size()])
		bu.append(Color(1.0, fposmod(k * 0.13 + i * 0.07, 1.0), 0.28, 1.2))
	var top := Vector3(lean, PALM_H, 0.0)
	for f in PALM_FRONDS:
		var ang := TAU * f / PALM_FRONDS
		for k in 3:
			var t := (k + 1) / 3.0
			var p := top + Vector3(cos(ang), 0.0, sin(ang)) * PALM_FROND_L * t + Vector3(0.0, 0.5 * t - 1.6 * t * t, 0.0)
			bx.append(Transform3D(Basis(), xf * p))
			bc.append(BEACH_COLS[(f + k + i) % BEACH_COLS.size()])
			bu.append(Color(1.0, fposmod(f * 0.21 + k * 0.1, 1.0), 0.3, 1.2))


# ------------------------------------------------------------------ committing (main thread)
func _commit(job: Dictionary) -> void:
	var near: bool = job.tier == "near"
	var nodes: Dictionary = _near_nodes if near else _far_nodes
	if not nodes.has(job.c) or not job.has("bulbs"):
		return
	var made: Array = []
	var b: Array = job.bulbs
	if (b[0] as Array).size() > 0:
		made.append(_bulb_mm(b[0], b[1], b[2], _near_bulb_mat if near else _far_bulb_mat))
	if near:
		for kind in job.posts:
			var xs: Array = job.posts[kind]
			if xs.is_empty():
				continue
			made.append(_mm(_post_mesh[kind], xs, POST_FAR))
		if not (job.palms as Array).is_empty():
			made.append(_mm(_palm_mesh, job.palms, PALM_FAR))
		if not (job.pool as Array).is_empty():
			var am := ArrayMesh.new()
			am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, job.pool)
			var mi := MeshInstance3D.new()
			mi.mesh = am
			mi.material_override = _pool_mat
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			mi.visibility_range_end = NEAR_FREE
			add_child(mi)
			made.append(mi)
		_near_lights[job.c] = job.lights
	nodes[job.c] = made


func _mm(mesh: Mesh, xs: Array, far: float) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = xs.size()
	for k in xs.size():
		mm.set_instance_transform(k, xs[k])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mmi.visibility_range_end = far
	add_child(mmi)
	return mmi


func _bulb_mm(xs: Array, cols: Array, cus: Array, mat: ShaderMaterial) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.use_custom_data = true
	mm.mesh = _bulb_quad
	mm.instance_count = xs.size()
	for k in xs.size():
		mm.set_instance_transform(k, xs[k])
		mm.set_instance_color(k, cols[k])
		mm.set_instance_custom_data(k, cus[k])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.material_override = mat
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mmi)
	return mmi


# ------------------------------------------------------------------ night and the real lights
func _update_night() -> void:
	if _sky == null or not is_instance_valid(_sky):
		_sky = get_parent().get_node_or_null("DaySkySystem")
	var dl: float = _sky.daylight() if _sky else 1.0
	_night = clampf((0.78 - dl) / 0.45, 0.0, 1.0)
	CoastalWalks.set_night(_night)


var _aloft := false


func set_aloft(on: bool) -> void:
	## (AloftSwitch) high above the floor: the near tier (posts, palms, pools, near bulbs) and the real lights go -- the
	## far bulbs stay, and the far side's night image shows the rest; back down, the near cells build again
	_aloft = on
	if on:
		for c in _near_nodes.keys():
			_free(_near_nodes, c)
		_near_lights.clear()
		for l in _lights:
			l.visible = false
	_check_t = 0.0


func _place_lights() -> void:
	## the real lights on the lamps nearest the player
	if _night < 0.02 or target == null or _aloft:
		for l in _lights:
			l.visible = false
		return
	var p := target.global_position
	var cand: Array = []
	for c in _near_lights:
		for e in _near_lights[c]:
			var d := (e[0] as Vector3).distance_squared_to(p)
			if d < LIGHT_R * LIGHT_R:
				cand.append([d, e])
	cand.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0])
	for k in _lights.size():
		var l := _lights[k]
		if k >= cand.size():
			l.visible = false
			continue
		var e: Array = cand[k][1]
		var hd: Array = HEAD[int(e[1])]
		var pos: Vector3 = e[0]
		l.global_position = pos + StationGeo.up(StationGeo.s_of(pos)) * -0.35
		l.omni_range = hd[5]
		l.light_color = hd[1]
		l.light_energy = float(hd[6]) * _night
		l.omni_attenuation = 1.6              # (a lamp lights its pool and the kerb, not a facade 15 m off to a glare)
		l.visible = true


# ------------------------------------------------------------------ meshes
const PALM_H := 7.4
const PALM_LEAN := 0.9
const PALM_FRONDS := 9
const PALM_FROND_L := 3.4


func _build_meshes() -> void:
	_bulb_quad = QuadMesh.new()
	_bulb_quad.size = Vector2.ONE
	var sh := load("res://remake/shaders/street_bulb.gdshader")
	_near_bulb_mat = ShaderMaterial.new()
	_near_bulb_mat.shader = sh
	_near_bulb_mat.set_shader_parameter("cut_max", CUT)
	_far_bulb_mat = ShaderMaterial.new()
	_far_bulb_mat.shader = sh
	_far_bulb_mat.set_shader_parameter("cut_min", CUT)
	_pool_mat = ShaderMaterial.new()
	_pool_mat.shader = load("res://remake/shaders/street_pool.gdshader")
	_pool_mat.set_shader_parameter("gain", POOL_SHADER_GAIN)
	_pool_mat.set_shader_parameter("falloff", POOL_FALLOFF)
	var iron := _metal(Color(0.12, 0.13, 0.14))
	var green := _metal(Color(0.09, 0.16, 0.12))
	var white := _metal(Color(0.85, 0.86, 0.84))
	# 0: a cobra head over the road
	var st := _st()
	_cyl(st, Vector3.ZERO, 0.11, 0.08, 0.0, 7.8)
	_box(st, Vector3(0, 7.8, -1.1), Vector3(0.08, 0.08, 2.2))
	_box(st, Vector3(0, 7.8, -2.25), Vector3(0.34, 0.14, 0.66))
	_post_mesh[0] = _finish(st, iron)
	# 1: an ornamental post with two lanterns
	st = _st()
	_cyl(st, Vector3.ZERO, 0.16, 0.07, 0.0, 0.9)
	_cyl(st, Vector3.ZERO, 0.07, 0.06, 0.9, 4.0)
	_box(st, Vector3(0, 3.95, 0), Vector3(1.2, 0.07, 0.07))
	for sx in [-0.55, 0.55]:
		_box(st, Vector3(sx, 4.15, 0), Vector3(0.3, 0.42, 0.3))
		_box(st, Vector3(sx, 4.4, 0), Vector3(0.36, 0.06, 0.36))
	_post_mesh[1] = _finish(st, green)
	# 2: an alley gooseneck
	st = _st()
	_cyl(st, Vector3.ZERO, 0.06, 0.05, 0.0, 3.45)
	_box(st, Vector3(0, 3.45, -0.3), Vector3(0.05, 0.05, 0.6))
	_box(st, Vector3(0, 3.38, -0.62), Vector3(0.22, 0.1, 0.22))
	_post_mesh[2] = _finish(st, iron)
	# 3: the beach street's white post and globe
	st = _st()
	_cyl(st, Vector3.ZERO, 0.1, 0.07, 0.0, 6.0)
	_box(st, Vector3(0, 6.0, -0.6), Vector3(0.07, 0.07, 1.2))
	_cyl(st, Vector3(0, 0, -1.2), 0.2, 0.2, 5.65, 6.05)
	_post_mesh[3] = _finish(st, white)
	_palm_mesh = _make_palm()


func _metal(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 0.55
	m.metallic = 0.4
	m.cull_mode = BaseMaterial3D.CULL_DISABLED          # (the posts' boxes and tubes are wound either way)
	return m


func _st() -> SurfaceTool:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	return st


func _finish(st: SurfaceTool, mat: Material) -> Mesh:
	st.generate_normals()
	var m := st.commit()
	m.surface_set_material(0, mat)
	return m


func _cyl(st: SurfaceTool, base: Vector3, r0: float, r1: float, y0: float, y1: float, n := 8) -> void:
	for k in n:
		var a0 := TAU * k / n
		var a1 := TAU * (k + 1) / n
		var p00 := base + Vector3(cos(a0) * r0, y0, sin(a0) * r0)
		var p10 := base + Vector3(cos(a1) * r0, y0, sin(a1) * r0)
		var p01 := base + Vector3(cos(a0) * r1, y1, sin(a0) * r1)
		var p11 := base + Vector3(cos(a1) * r1, y1, sin(a1) * r1)
		for v in [p00, p01, p11, p00, p11, p10]:
			st.add_vertex(v)
		for v in [base + Vector3(0, y1, 0), p11, p01]:
			st.add_vertex(v)


func _box(st: SurfaceTool, c: Vector3, sz: Vector3) -> void:
	var h := sz * 0.5
	var v := [c + Vector3(-h.x, -h.y, -h.z), c + Vector3(h.x, -h.y, -h.z), c + Vector3(h.x, h.y, -h.z), c + Vector3(-h.x, h.y, -h.z),
		c + Vector3(-h.x, -h.y, h.z), c + Vector3(h.x, -h.y, h.z), c + Vector3(h.x, h.y, h.z), c + Vector3(-h.x, h.y, h.z)]
	for f in [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [3, 7, 6, 2], [0, 4, 7, 3], [1, 2, 6, 5]]:
		for i in [0, 1, 2, 0, 2, 3]:
			st.add_vertex(v[f[i]])


func _make_palm() -> Mesh:
	## a palm: a leaning, tapering trunk and a crown of drooping fronds (vertex coloured, one material)
	var st := _st()
	var segs := 7
	for k in segs:
		var y0 := PALM_H * k / segs
		var y1 := PALM_H * (k + 1) / segs
		var b0 := Vector3(PALM_LEAN * pow(y0 / PALM_H, 1.6), 0, 0)
		var b1 := Vector3(PALM_LEAN * pow(y1 / PALM_H, 1.6), 0, 0)
		var r0 := lerpf(0.2, 0.13, y0 / PALM_H)
		var r1 := lerpf(0.2, 0.13, y1 / PALM_H)
		st.set_color(Color(0.42, 0.33, 0.22) if k % 2 == 0 else Color(0.36, 0.28, 0.19))
		for j in 7:
			var a0 := TAU * j / 7.0
			var a1 := TAU * (j + 1) / 7.0
			var p00 := b0 + Vector3(cos(a0) * r0, y0, sin(a0) * r0)
			var p10 := b0 + Vector3(cos(a1) * r0, y0, sin(a1) * r0)
			var p01 := b1 + Vector3(cos(a0) * r1, y1, sin(a0) * r1)
			var p11 := b1 + Vector3(cos(a1) * r1, y1, sin(a1) * r1)
			for v in [p00, p01, p11, p00, p11, p10]:
				st.add_vertex(v)
	var top := Vector3(PALM_LEAN, PALM_H, 0)
	for f in PALM_FRONDS:
		var ang := TAU * f / PALM_FRONDS + 0.3
		var d := Vector3(cos(ang), 0, sin(ang))
		var side := d.cross(Vector3.UP).normalized()
		st.set_color(Color(0.2, 0.42, 0.18) if f % 2 == 0 else Color(0.25, 0.48, 0.2))
		var prev := top
		var pw := 0.08
		for k in 4:
			var t := (k + 1) / 4.0
			var p := top + d * PALM_FROND_L * t + Vector3(0, 0.5 * t - 1.6 * t * t, 0)
			var w := 0.45 * sin(PI * t) + 0.04
			for v in [prev - side * pw, p - side * w, p + side * w, prev - side * pw, p + side * w, prev + side * pw]:
				st.add_vertex(v)
			for v in [prev - side * pw, p + side * w, p - side * w, prev - side * pw, prev + side * pw, p + side * w]:
				st.add_vertex(v)
			prev = p
			pw = w
	st.generate_normals()
	var m := st.commit()
	_palm_mat = StandardMaterial3D.new()
	_palm_mat.vertex_color_use_as_albedo = true
	_palm_mat.roughness = 0.85
	_palm_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.surface_set_material(0, _palm_mat)
	return m
