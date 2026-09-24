extends RefCounted
class_name MapWater

## Water surfaces for the map's terrain (MapTerrain): the Kettle River and Lake Tamsin as one
## surface at the bank-full MapTerrain.water_level(s), in STEP m strips round the ring across the
## whole depression (MapTerrain.outline + OVERLAP, which the banks hide), with the game's
## scrolling water material (LakeWater.gd).
## build_small(): the creeks, spurs, ponds and oxbow lakes, filled FILL of their depth.

const STEP := 4.0
const OVERLAP := 1.5                 # past the rim, under the bank


static func build(root: Node3D, s0 := 0.0, s1 := -1.0) -> MeshInstance3D:
	if s1 < 0.0:
		s1 = StationGeo.CIRC
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load("res://assets/textures/water_tinted_0.png")
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(1.0, 1.0, 1.0, 0.9)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := ceili((s1 - s0) / STEP)
	var prev := []
	for i in n + 1:
		var s := s0 + (s1 - s0) * i / float(n)
		var e := MapTerrain.outline(s)                     # the whole depression, rim to rim
		var lvl := MapTerrain.water_level(s)
		var up := StationGeo.up(s)
		var row := []
		for x in [e.x - OVERLAP, (e.x + e.y) * 0.5, e.y + OVERLAP]:
			row.append([StationGeo.point(s, x, lvl), Vector2(x / 20.0, s / 20.0), up])
		if not prev.is_empty():
			for j in 2:
				for v in [prev[j], row[j], row[j + 1], prev[j], row[j + 1], prev[j + 1]]:
					st.set_normal(v[2])
					st.set_uv(v[1])
					st.add_vertex(v[0])
		prev = row
	st.set_material(mat)
	var mi := MeshInstance3D.new()
	mi.name = "map_water_surface"
	mi.mesh = st.commit()
	mi.set_script(load("res://scripts/world/LakeWater.gd"))
	root.add_child(mi)
	return mi


const FILL := 0.75                   # the small water stands at this fraction of its carved depth


static func build_small(root: Node3D) -> MeshInstance3D:
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MapTerrain.PATH))
	MapTerrain.elevation(0.0, 0.0)                        # loads the terrain data
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	# creeks and spurs: a ribbon along the line at the bank-full level; broken where a road crosses
	# (it runs through a culvert under the road there)
	for cr in d.creeks:
		var pts: Array = cr.pts
		var hw: float = cr.hw + 0.8
		var prev := []
		for k in pts.size():
			var c := Vector2(pts[k][0], pts[k][1])
			var nb := Vector2(pts[mini(k + 1, pts.size() - 1)][0], pts[mini(k + 1, pts.size() - 1)][1])
			var pb := Vector2(pts[maxi(k - 1, 0)][0], pts[maxi(k - 1, 0)][1])
			var dv := Vector2(StationGeo.wrap_ds(nb.x - pb.x), nb.y - pb.y).normalized()
			var side := Vector2(-dv.y, dv.x)
			var row := []
			if MapTerrain.road_weight(c.x, c.y) < 0.3 and MapTerrain._body_profile(fposmod(c.x, StationGeo.CIRC), c.y) <= 0.0:
				var lvl := MapTerrain.elevation(c.x, c.y) + FILL * float(cr.depth)
				var l := c + side * hw
				var r := c - side * hw
				row = [StationGeo.point(l.x, l.y, lvl), StationGeo.point(r.x, r.y, lvl), c, StationGeo.up(c.x)]
			if not prev.is_empty() and not row.is_empty():
				_quad(st, prev[0], row[0], row[1], prev[1], prev[3], row[3], prev[2], row[2])
			prev = row
	# ponds: filled ellipses
	for p in d.ponds:
		var lvl := MapTerrain.elevation(p.s, p.x) + FILL * float(p.depth)
		var ring := []
		for k in 33:
			var t := TAU * k / 32.0
			var u: float = p.a * 1.08 * cos(t)
			var v: float = p.b * 1.08 * sin(t)
			var ds: float = u * cos(float(p.rot)) - v * sin(float(p.rot))
			var dx: float = u * sin(float(p.rot)) + v * cos(float(p.rot))
			ring.append(Vector2(p.s + ds, p.x + dx))
		_fan(st, Vector2(p.s, p.x), ring, lvl)
	# oxbow lakes: their outlines, triangulated
	for ox in d.oxbows:
		var poly := PackedVector2Array()
		var lo := 1e9
		for q in ox.poly:
			poly.append(Vector2(q[0], q[1]))
		var tris := Geometry2D.triangulate_polygon(poly)
		var cen := Vector2.ZERO
		for q in poly:
			cen += q
		cen /= poly.size()
		lo = MapTerrain.elevation(cen.x, cen.y) + FILL * float(ox.depth)
		for i in range(0, tris.size(), 3):
			for j in [0, 2, 1]:
				var q: Vector2 = poly[tris[i + j]]
				st.set_normal(StationGeo.up(q.x))
				st.set_uv(q / 20.0)
				st.add_vertex(StationGeo.point(q.x, q.y, lo))
	st.set_material(_small_material())
	var mi := MeshInstance3D.new()
	mi.name = "map_small_water"
	mi.mesh = st.commit()
	mi.set_script(load("res://scripts/world/LakeWater.gd"))
	root.add_child(mi)
	return mi


static func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, n0: Vector3, n1: Vector3, m0: Vector2, m1: Vector2) -> void:
	var q := [[a, n0, m0], [b, n1, m1], [c, n1, m1], [d, n0, m0]]
	for j in [0, 1, 2, 0, 2, 3]:
		st.set_normal(q[j][1])
		st.set_uv(q[j][2] / 20.0)
		st.add_vertex(q[j][0])


static func _fan(st: SurfaceTool, c: Vector2, ring: Array, lvl: float) -> void:
	for k in ring.size() - 1:
		var a: Vector2 = ring[k]
		var b: Vector2 = ring[k + 1]
		for q in [c, b, a]:
			st.set_normal(StationGeo.up(q.x))
			st.set_uv(q / 20.0)
			st.add_vertex(StationGeo.point(q.x, q.y, lvl))


static func _small_material() -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load("res://assets/textures/water_tinted_0.png")
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0.9, 0.95, 0.9, 0.88)
	return mat

