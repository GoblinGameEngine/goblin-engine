extends Node3D
class_name MapRoads

## The map's roads, streets and railway (remake/terrain.json, from tools/map_preview.py), surfaced
## on the graded terrain (MapTerrain grades the ground flat across each road at its centreline).
## Each road is a ribbon of its map width sampled every STEP m, LIFT above the ground; spans over
## the river / lake are left out (the crossings' bridges carry the road there).  Ribbons are merged
## per CELL m cell and surface -- asphalt (highways, county roads, main streets, streets), gravel,
## concrete (alleys), ballast (the railway) -- one mesh each.  The ribbons are built on a worker
## thread; the main thread only makes the mesh nodes, a few a frame.

const STEP := 3.0
const LIFT := 0.06
const CELL := 400.0
const FAR := 1800.0                  # past this a road is under a pixel wide
const SURFACE := {"hwy": "asphalt", "county": "asphalt", "main": "asphalt", "street": "asphalt",
	"gravel": "gravel", "alley": "concrete", "rail": "ballast"}
const TEX := {"asphalt": ["lib/asphalt", 6.0], "gravel": ["p-site/gravel_road", 6.0],
	"concrete": ["lib/concrete", 3.0], "ballast": ["p-site/ballast", 3.0]}

var _roads: Array = []
var _task := -1
var _out: Array = []                 # [cell key, surface arrays] from the worker
var _cells := {}                     # [cell key, surface] -> SurfaceTool
var _mats := {}


func setup() -> void:
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MapTerrain.PATH))
	_roads = d.roads
	_roads.append({"cls": "rail", "w": 4.0, "pts": d.rail.pts})
	for key in TEX:
		var m := StandardMaterial3D.new()
		var root := "res://remake/textures/%s_" % TEX[key][0]
		m.albedo_texture = load(root + "albedo.webp")
		m.normal_enabled = true
		m.normal_texture = load(root + "normal.webp")
		m.roughness_texture = load(root + "rough.webp")
		m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		m.cull_mode = BaseMaterial3D.CULL_DISABLED        # a ribbon's winding follows its road's direction
		_mats[key] = m
	MapTerrain.elevation(0.0, 0.0)                         # loads the terrain data (_body_profile reads it)
	_task = WorkerThreadPool.add_task(_build_all, false, "roads")
	set_process(true)


func _build_all() -> void:
	for rd in _roads:
		_add_road(rd)
	var out := []
	for key in _cells:
		out.append([key, (_cells[key] as SurfaceTool).commit_to_arrays()])
	_cells.clear()
	_out = out


func _process(_delta: float) -> void:
	if _task < 0 or not WorkerThreadPool.is_task_completed(_task):
		return
	WorkerThreadPool.wait_for_task_completion(_task)
	_task = -1
	_commit()
	set_process(false)


func _exit_tree() -> void:
	if _task >= 0:
		WorkerThreadPool.wait_for_task_completion(_task)


func _add_road(rd: Dictionary) -> void:
	var pts: Array = rd.pts
	var surf: String = SURFACE.get(rd.cls, "asphalt")
	var hw: float = rd.w * 0.5
	var tile: float = TEX[surf][1]
	var run := 0.0
	var prev := []
	for k in pts.size() - 1:
		var a := Vector2(pts[k][0], pts[k][1])
		var b := Vector2(pts[k + 1][0], pts[k + 1][1])
		var dv := Vector2(StationGeo.wrap_ds(b.x - a.x), b.y - a.y)
		var seg_len := dv.length()
		if seg_len < 0.01:
			continue
		var dirv := dv / seg_len
		var side := Vector2(-dirv.y, dirv.x)
		var n := maxi(1, ceili(seg_len / STEP))
		for i in range(0 if k == 0 else 1, n + 1):
			var c := a + dv * (i / float(n))
			var over_water := MapTerrain._body_profile(fposmod(c.x, StationGeo.CIRC), c.y) > 0.05
			var l := c + side * hw
			var r := c - side * hw
			var row := [] if over_water else [
				StationGeo.point(l.x, l.y, MapTerrain.elevation(l.x, l.y) + LIFT),
				StationGeo.point(r.x, r.y, MapTerrain.elevation(r.x, r.y) + LIFT),
				run / tile, StationGeo.up(c.x)]
			if not prev.is_empty() and not row.is_empty():
				var key := [Vector2i(floori(fposmod(c.x, StationGeo.CIRC) / CELL), floori(c.y / CELL)), surf]
				var st: SurfaceTool = _cells.get(key)
				if st == null:
					st = SurfaceTool.new()
					st.begin(Mesh.PRIMITIVE_TRIANGLES)
					_cells[key] = st
				var q := [[prev[0], Vector2(0.0, prev[2]), prev[3]], [row[0], Vector2(0.0, row[2]), row[3]],
					[row[1], Vector2(rd.w / tile, row[2]), row[3]], [prev[1], Vector2(rd.w / tile, prev[2]), prev[3]]]
				for j in [0, 2, 1, 0, 3, 2]:
					st.set_normal(q[j][2])
					st.set_uv(q[j][1])
					st.add_vertex(q[j][0])
			prev = row
			run += seg_len / n


func _commit() -> void:
	for job in _out:
		var key: Array = job[0]
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, job[1])
		mesh.surface_set_material(0, _mats[key[1]])
		var mi := MeshInstance3D.new()
		mi.name = "roads_%d_%d_%s" % [key[0].x, key[0].y, key[1]]
		mi.mesh = mesh
		mi.visibility_range_end = FAR
		mi.visibility_range_end_margin = FAR * 0.08
		add_child(mi)
	_out.clear()
