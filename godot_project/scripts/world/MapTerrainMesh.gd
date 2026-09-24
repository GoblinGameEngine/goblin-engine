extends Node3D
class_name MapTerrainMesh

## The ring floor drawn from MapTerrain (the map's terrain), streamed in tiers round the player:
##   T0  chunk (CHUNK_SEGS ring segments x CHUNK_X m), 2 m grid, with collision -- within NEAR
##   T1  the same chunk on an 8 m grid                               -- the rest of a near group
##   T2  a group (GROUP x GROUP chunks) merged, 8 m grid              -- groups within MID
##   T3  the group on a 32 m grid                                    -- everything else
## Every tier samples the exact height function; coarse grids' points are a subset of the fine
## ones, and each mesh hangs a short skirt below its edges so tier seams never show a crack.
## Vertex colours tint the ground: grass, bank mud and river bed by carved depth, bare earth on
## steep slopes.  Water surfaces (river, lake) are built alongside (build_water).

const CHUNK_SEGS := 2
const CHUNK_X := 100.0
const GROUP := 4
const NEAR := 220.0
const MID := 650.0
const SKIRT := 1.5
const TEX_M := 8.0

var radius: float
var segments: int
var half_w: float
var target: Node3D
var material: Material
var _n_cs: int                        # chunks round the ring
var _n_cx: int                        # chunks across
var _t0 := {}                         # Vector2i chunk -> MeshInstance3D (with collision)
var _t1 := {}                         # Vector2i chunk -> MeshInstance3D
var _t2 := {}                         # Vector2i group -> MeshInstance3D
var _t3 := {}                         # Vector2i group -> MeshInstance3D
var _queue: Array = []                # pending builds: [tier, key]
var _far_todo: Array = []             # groups whose far tier isn't built yet
var _t := 0.0


func setup(p_radius: float, p_segments: int, width: float, p_target: Node3D, p_material: Material) -> void:
	radius = p_radius
	segments = p_segments
	half_w = width * 0.5
	target = p_target
	material = p_material
	_n_cs = segments / CHUNK_SEGS
	_n_cx = ceili(width / CHUNK_X)
	# nothing big here: only the chunks right under the player are built now (they stand on them);
	# the rest -- near tiers nearest first, then every group's far tier -- builds a few per frame
	for gs in range(0, _n_cs, GROUP):
		for gx in range(0, _n_cx, GROUP):
			_far_todo.append(Vector2i(gs / GROUP, gx / GROUP))
	if target:
		_update()
		var n := 0
		while not _queue.is_empty() and _queue[0][0] == 0 and n < 4:
			_do(_queue.pop_front())
			n += 1
	set_process(target != null)


# ------------------------------------------------------------------ geometry
func _seg_s() -> float:
	return TAU * radius / float(segments)


func _chunk_rect(c: Vector2i) -> Rect2:
	## (s0, x0, ds, dx) of chunk c
	var cs := _seg_s() * CHUNK_SEGS
	return Rect2(c.x * cs, -half_w + c.y * CHUNK_X, cs, minf(CHUNK_X, half_w - (-half_w + c.y * CHUNK_X)))


func _group_rect(g: Vector2i) -> Rect2:
	var a := _chunk_rect(Vector2i(g.x * GROUP, g.y * GROUP))
	var b := _chunk_rect(Vector2i(mini(g.x * GROUP + GROUP, _n_cs) - 1, mini(g.y * GROUP + GROUP, _n_cx) - 1))
	return Rect2(a.position, b.end - a.position)


func _flat_point(s: float, x: float) -> Vector3:
	## RingCoords.floor_point() without the terrain (the ring's own polygonal floor).
	var theta := fposmod(s / radius, TAU)
	if RingCoords.FLAT_MODE:
		return Vector3(x, 0.0, s)
	var d_theta := TAU / segments
	var i := mini(int(floor(theta / d_theta)), segments - 1)
	var t := (theta - d_theta * i) / d_theta
	var p0 := Vector3(x, radius * cos(d_theta * i), radius * sin(d_theta * i))
	var p1 := Vector3(x, radius * cos(d_theta * (i + 1)), radius * sin(d_theta * (i + 1)))
	return p0.lerp(p1, t)


func _tint(depth: float, slope: float) -> Color:
	var grass := Color(1.0, 1.0, 1.0)
	var mud := Color(0.55, 0.47, 0.36)
	var bed := Color(0.42, 0.38, 0.32)
	var c := grass.lerp(mud, clampf(depth / 0.6, 0.0, 1.0))
	c = c.lerp(bed, clampf((depth - 0.6) / 1.5, 0.0, 1.0))
	return c.lerp(Color(0.7, 0.6, 0.45), clampf((slope - 0.35) / 0.3, 0.0, 1.0))


func _build(r: Rect2, step: float, collide: bool, name: String) -> MeshInstance3D:
	var ns := maxi(1, roundi(r.size.x / step))
	var nx := maxi(1, roundi(r.size.y / step))
	var ups := []
	for i in ns + 1:
		ups.append(RingCoords.floor_basis(radius, segments, r.position.x + r.size.x * i / float(ns)).y)
	var pts := []
	var hs := []
	for i in ns + 1:
		var s := r.position.x + r.size.x * i / float(ns)
		var up: Vector3 = ups[i]
		var row_p := []
		var row_h := []
		for j in nx + 1:
			var x := r.position.y + r.size.y * j / float(nx)
			var smp := MapTerrain.sample(s, x)
			row_p.append(_flat_point(s, x) + up * smp.x)
			row_h.append([smp.x, smp.y])
		pts.append(row_p)
		hs.append(row_h)
	# normals from the grid itself (central differences), so a skirt can carry the ground's normal:
	# the outline pass then sees no edge where tiles meet
	var nrm := []
	for i in ns + 1:
		var row_n := []
		for j in nx + 1:
			var ps: Vector3 = pts[mini(i + 1, ns)][j] - pts[maxi(i - 1, 0)][j]
			var px: Vector3 = pts[i][mini(j + 1, nx)] - pts[i][maxi(j - 1, 0)]
			var n := px.cross(ps).normalized()
			if n.dot(ups[i]) < 0.0:
				n = -n
			row_n.append(n)
		nrm.append(row_n)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in ns:
		for j in nx:
			var q := [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]]
			var slope := absf(hs[i + 1][j][0] - hs[i][j][0]) / (r.size.x / ns) + absf(hs[i][j + 1][0] - hs[i][j][0]) / (r.size.y / nx)
			for k in [0, 1, 2, 0, 2, 3]:            # counter-clockwise seen from above (toward the axis)
				var a: int = q[k][0]
				var b: int = q[k][1]
				st.set_color(_tint(hs[a][b][1], slope))
				st.set_normal(nrm[a][b])
				st.set_uv(Vector2((r.position.y + r.size.y * b / float(nx)) / TEX_M, (r.position.x + r.size.x * a / float(ns)) / TEX_M))
				st.add_vertex(pts[a][b])
	# skirts: hang each border edge SKIRT m down (along -up), hiding cracks against coarser tiers
	var border := []
	for i in ns:
		border.append([[i, 0], [i + 1, 0]])
		border.append([[i + 1, nx], [i, nx]])
	for j in nx:
		border.append([[ns, j], [ns, j + 1]])
		border.append([[0, j + 1], [0, j]])
	for e in border:
		var a: Array = e[0]
		var b: Array = e[1]
		var pa: Vector3 = pts[a[0]][a[1]]
		var pb: Vector3 = pts[b[0]][b[1]]
		var da: Vector3 = ups[a[0]] * SKIRT
		var db: Vector3 = ups[b[0]] * SKIRT
		var na: Vector3 = nrm[a[0]][a[1]]
		var nb: Vector3 = nrm[b[0]][b[1]]
		for v in [[pa, na], [pb - db, nb], [pb, nb], [pa, na], [pa - da, na], [pb - db, nb]]:
			st.set_color(Color(0.55, 0.47, 0.36))
			st.set_normal(v[1])
			st.set_uv(Vector2.ZERO)
			st.add_vertex(v[0])
	st.set_material(material)
	var mi := MeshInstance3D.new()
	mi.name = name
	mi.mesh = st.commit()
	add_child(mi)
	if collide:
		var body := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var shape := mi.mesh.create_trimesh_shape()
		shape.backface_collision = true          # a ground you can't fall through from either side
		cs.shape = shape
		body.add_child(cs)
		mi.add_child(body)
	return mi


# ------------------------------------------------------------------ streaming
func _process(delta: float) -> void:
	_t -= delta
	if _t <= 0.0:
		_t = 0.5
		_update()
	# a build per frame, nearest first; the far tier fills in when the near work is done
	if not _queue.is_empty():
		_do(_queue.pop_front())
	elif not _far_todo.is_empty():
		var g: Vector2i = _far_todo.pop_front()
		_t3[g] = _build(_group_rect(g), 32.0, false, "t3_%d_%d" % [g.x, g.y])
		_apply_visibility(_vis_state[0], _vis_state[1], _vis_state[2])


func _update() -> void:
	var p := target.global_position
	var s_here := RingCoords.s_from_position(radius, p)
	var x_here := p.x
	var cs := _seg_s() * CHUNK_SEGS
	var want0 := {}
	var want_near_groups := {}
	var want2 := {}
	for c in range(floori((s_here - NEAR) / cs), floori((s_here + NEAR) / cs) + 1):
		for cx in range(maxi(0, floori((x_here + half_w - NEAR) / CHUNK_X)), mini(_n_cx - 1, floori((x_here + half_w + NEAR) / CHUNK_X)) + 1):
			var key := Vector2i(posmod(c, _n_cs), cx)
			var rc := _chunk_rect(key)
			var dx := maxf(0.0, maxf(rc.position.y - x_here, x_here - rc.end.y))
			var ds := maxf(0.0, absf(_wrap_s(rc.get_center().x - s_here)) - rc.size.x * 0.5)
			if Vector2(ds, dx).length() < NEAR:
				want0[key] = true
				want_near_groups[Vector2i(key.x / GROUP, key.y / GROUP)] = true
	# groups by distance from their nearest point: MID -> merged 8 m tier
	for g in _all_groups():
		var rg := _group_rect(g)
		var dx := maxf(0.0, maxf(rg.position.y - x_here, x_here - rg.end.y))
		var ds := maxf(0.0, absf(_wrap_s(rg.get_center().x - s_here)) - rg.size.x * 0.5)
		if not want_near_groups.has(g) and Vector2(ds, dx).length() < MID:
			want2[g] = true
	# retire what's no longer wanted
	for key in _t0.keys():
		if not want0.has(key):
			_t0[key].queue_free()
			_t0.erase(key)
	for key in _t1.keys():
		if not want_near_groups.has(Vector2i(key.x / GROUP, key.y / GROUP)):
			_t1[key].queue_free()
			_t1.erase(key)
	for g in _t2.keys():
		if not want2.has(g):
			_t2[g].queue_free()
			_t2.erase(g)
	# queue what's missing, nearest first
	_queue.clear()
	var jobs := []
	for key in want0:
		if not _t0.has(key):
			jobs.append([0, key, _chunk_rect(key).get_center()])
	for g in want_near_groups:
		for i in GROUP:
			for j in GROUP:
				var key := Vector2i(g.x * GROUP + i, g.y * GROUP + j)
				if key.x < _n_cs and key.y < _n_cx and not _t1.has(key):
					jobs.append([1, key, _chunk_rect(key).get_center()])
	for g in want2:
		if not _t2.has(g):
			jobs.append([2, g, _group_rect(g).get_center()])
	jobs.sort_custom(func(a, b): return _jobdist(a, s_here, x_here) < _jobdist(b, s_here, x_here))
	_queue = jobs
	_apply_visibility(want0, want_near_groups, want2)


func _all_groups() -> Array:
	var out := []
	for gs in range(0, _n_cs, GROUP):
		for gx in range(0, _n_cx, GROUP):
			out.append(Vector2i(gs / GROUP, gx / GROUP))
	return out


func _jobdist(j: Array, s_here: float, x_here: float) -> float:
	var c: Vector2 = j[2]
	return Vector2(_wrap_s(c.x - s_here), c.y - x_here).length() + j[0] * 50.0


func _wrap_s(ds: float) -> float:
	var circ := TAU * radius
	return fposmod(ds + circ * 0.5, circ) - circ * 0.5


func _do(job: Array) -> void:
	var tier: int = job[0]
	var key: Vector2i = job[1]
	match tier:
		0:
			if not _t0.has(key):
				_t0[key] = _build(_chunk_rect(key), 2.0, true, "t0_%d_%d" % [key.x, key.y])
		1:
			if not _t1.has(key):
				_t1[key] = _build(_chunk_rect(key), 8.0, false, "t1_%d_%d" % [key.x, key.y])
		2:
			if not _t2.has(key):
				_t2[key] = _build(_group_rect(key), 8.0, false, "t2_%d_%d" % [key.x, key.y])
	_apply_visibility(_vis_state[0], _vis_state[1], _vis_state[2])


var _vis_state := [{}, {}, {}]

func _apply_visibility(want0: Dictionary, near_groups: Dictionary, want2: Dictionary) -> void:
	_vis_state = [want0, near_groups, want2]
	for g in _t3:
		_t3[g].visible = not near_groups.has(g) and not (want2.has(g) and _t2.has(g))
	for g in _t2:
		_t2[g].visible = want2.has(g)
	for key in _t1:
		_t1[key].visible = not (want0.has(key) and _t0.has(key))
	# a near group whose T1 chunks aren't all built yet keeps its T3 until they are
	for g in near_groups:
		var ready := true
		for i in GROUP:
			for j in GROUP:
				var key := Vector2i(g.x * GROUP + i, g.y * GROUP + j)
				if key.x < _n_cs and key.y < _n_cx and not _t1.has(key) and not _t0.has(key):
					ready = false
		if not ready and _t3.has(g):
			_t3[g].visible = true
			for i in GROUP:
				for j in GROUP:
					var key := Vector2i(g.x * GROUP + i, g.y * GROUP + j)
					if _t1.has(key):
						_t1[key].visible = false
					if _t0.has(key):
						_t0[key].visible = true

