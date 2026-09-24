extends Node3D
class_name MapTrees

## Trees where the map has them: its woods (riparian strips along the creeks, the steep bluff
## faces) and the windbreak grove behind each farmstead (MapTerrain.landcover classes 3 and 5).
## A jittered grid -- every WOODS_STEP / GROVE_STEP m, each tree's offset, size and turn a hash of
## its grid spot, so the same trees come back every time -- skipping roads, water and built land.
## Drawn as MultiMeshes per CELL m cell, one draw call each:
##   near (< NEAR m)  a low-poly deciduous tree, trunk + two-lobed canopy (~130 triangles)
##   far  (< FAR m)   one squat blob (~20 triangles)
##   beyond            the woods' ground tint alone
## Built a cell per frame.

const WOODS_STEP := 6.0
const GROVE_STEP := 5.0
const CELL := 200.0
const NEAR := 320.0
const FAR := 900.0

var _cells: Array = []
var _next := 0
var _near_mesh: ArrayMesh
var _far_mesh: ArrayMesh


func setup() -> void:
	MapTerrain.elevation(0.0, 0.0)
	_near_mesh = _tree_mesh(true)
	_far_mesh = _tree_mesh(false)
	for cs in ceili(StationGeo.CIRC / CELL):
		for cx in ceili(StationGeo.LENGTH / CELL):
			_cells.append(Vector2i(cs, cx))
	set_process(true)


func _process(_delta: float) -> void:
	if _next >= _cells.size():
		set_process(false)
		return
	_build_cell(_cells[_next])
	_next += 1


func _build_cell(c: Vector2i) -> void:
	var s0 := c.x * CELL
	var x0 := -StationGeo.HALF_LEN + c.y * CELL
	var xforms: Array[Transform3D] = []
	var cols: Array[Color] = []
	var step := minf(WOODS_STEP, GROVE_STEP)
	var i := 0
	while i * step < CELL:
		var j := 0
		while j * step < CELL:
			var s := s0 + i * step
			var x := x0 + j * step
			j += 1
			if s >= StationGeo.CIRC or absf(x) > StationGeo.HALF_LEN - 35.0:     # clear of the cliffs' scree
				continue
			var lc := MapTerrain.landcover(s, x)
			if lc.x != 3 and lc.x != 5:
				continue
			var gs := GROVE_STEP if lc.x == 5 else WOODS_STEP
			# thin the finer grid to this cover's spacing, deterministically
			if lc.x == 3 and _hash(floori(s / step), floori(x / step), 0) > (step / gs) * (step / gs):
				continue
			var js := s + (_hash(floori(s), floori(x), 1) - 0.5) * gs * 0.8
			var jx := x + (_hash(floori(s), floori(x), 2) - 0.5) * gs * 0.8
			if MapTerrain.road_weight(js, jx) > 0.05 or MapTerrain.water_depth(js, jx) > 0.1:
				continue
			var h := MapTerrain.elevation(js, jx)
			var sc := 0.75 + 0.6 * _hash(floori(s), floori(x), 3)
			var b := StationGeo.basis(js, TAU * _hash(floori(s), floori(x), 4)).scaled(Vector3(sc, sc * (0.9 + 0.25 * _hash(floori(s), floori(x), 5)), sc))
			xforms.append(Transform3D(b, StationGeo.point(js, jx, h - 0.2)))
			var g := 0.85 + 0.3 * _hash(floori(s), floori(x), 6)
			cols.append(Color(g * (0.95 + 0.1 * _hash(floori(s), floori(x), 7)), g, g * 0.9))
		i += 1
	if xforms.is_empty():
		return
	for version in [[_near_mesh, 0.0, NEAR], [_far_mesh, NEAR, FAR]]:
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = version[0]
		mm.instance_count = xforms.size()
		for k in xforms.size():
			mm.set_instance_transform(k, xforms[k])
			mm.set_instance_color(k, cols[k])
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.visibility_range_begin = version[1]
		mmi.visibility_range_begin_margin = version[1] * 0.08
		mmi.visibility_range_end = version[2]
		mmi.visibility_range_end_margin = version[2] * 0.08
		mmi.name = "trees_%d_%d_%s" % [c.x, c.y, "near" if version[1] == 0.0 else "far"]
		add_child(mmi)


static func _hash(a: int, b: int, salt: int) -> float:
	var h := (a * 73856093) ^ (b * 19349663) ^ (salt * 83492791)
	h = ((h ^ (h >> 13)) * 1274126177) & 0x7fffffff
	return float(h % 100000) / 100000.0


func _tree_mesh(near: bool) -> ArrayMesh:
	## A deciduous tree about 11 m tall (local y up): trunk and a two-lobed canopy -- or, far, one
	## squat blob.  Leaves and bark take the instance colour (a per-tree tint).
	var mesh := ArrayMesh.new()
	var bark := StandardMaterial3D.new()
	bark.albedo_color = Color(0.3, 0.24, 0.18)
	bark.vertex_color_use_as_albedo = true
	var leaf := StandardMaterial3D.new()
	leaf.albedo_color = Color(0.26, 0.4, 0.17)
	leaf.vertex_color_use_as_albedo = true
	leaf.roughness = 0.95
	var bark_st := SurfaceTool.new()
	var leaf_st := SurfaceTool.new()
	if near:
		var trunk := CylinderMesh.new()
		trunk.top_radius = 0.18
		trunk.bottom_radius = 0.3
		trunk.height = 5.0
		trunk.radial_segments = 6
		trunk.rings = 1
		bark_st.append_from(trunk, 0, Transform3D(Basis(), Vector3(0, 2.5, 0)))
		var lobe := SphereMesh.new()
		lobe.radius = 3.4
		lobe.height = 5.6
		lobe.radial_segments = 8
		lobe.rings = 4
		leaf_st.append_from(lobe, 0, Transform3D(Basis(), Vector3(0, 6.8, 0)))
		var lobe2 := SphereMesh.new()
		lobe2.radius = 2.4
		lobe2.height = 4.0
		lobe2.radial_segments = 7
		lobe2.rings = 3
		leaf_st.append_from(lobe2, 0, Transform3D(Basis(), Vector3(0.9, 9.0, -0.4)))
		bark_st.set_material(bark)
		bark_st.commit(mesh)
	else:
		var blob := SphereMesh.new()
		blob.radius = 3.6
		blob.height = 8.0
		blob.radial_segments = 5
		blob.rings = 2
		leaf_st.append_from(blob, 0, Transform3D(Basis(), Vector3(0, 6.0, 0)))
	leaf_st.set_material(leaf)
	leaf_st.commit(mesh)
	return mesh
