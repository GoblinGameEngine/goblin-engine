extends RefCounted
class_name MapWater

## Water surfaces for the map's terrain (MapTerrain): the Kettle River and Lake Tamsin as one
## surface at the bank-full MapTerrain.water_level(s), in STEP m strips round the ring across the
## whole depression (MapTerrain.outline + OVERLAP, which the banks hide), with the game's
## scrolling water material (LakeWater.gd).
## Creeks, ponds and oxbows come later.

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
