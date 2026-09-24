extends RefCounted
class_name MapWater

## Water surfaces for the map's terrain (MapTerrain): the Kettle River and Lake Tamsin as one
## surface at the bank-full MapTerrain.water_level(s), in STEP m strips round the ring across the
## whole depression (MapTerrain.outline + OVERLAP, which the banks hide), with the game's
## scrolling water material (LakeWater.gd).
## Creeks, ponds and oxbows come later.

const STEP := 4.0
const OVERLAP := 1.5                 # past the rim, under the bank


static func build(root: Node3D, radius: float, segments: int, s0 := 0.0, s1 := -1.0) -> MeshInstance3D:
	var circ := TAU * radius
	if s1 < 0.0:
		s1 = circ
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
		var up := RingCoords.floor_basis(radius, segments, s).y
		# shading normal: the cylinder's own (smooth round the ring), not the 96-gon facet's -- a
		# facet normal steps 3.75 degrees at every facet edge and the outline pass inks each step
		var th := s / radius
		var smooth_up := Vector3(0.0, -cos(th), -sin(th))
		var row := []
		for x in [e.x - OVERLAP, (e.x + e.y) * 0.5, e.y + OVERLAP]:
			row.append([_flat(radius, segments, s, x) + up * lvl, Vector2(x / 20.0, s / 20.0), smooth_up])
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


static func _flat(radius: float, segments: int, s: float, x: float) -> Vector3:
	var theta := fposmod(s / radius, TAU)
	var d_theta := TAU / segments
	var i := mini(int(floor(theta / d_theta)), segments - 1)
	var t := (theta - d_theta * i) / d_theta
	var p0 := Vector3(x, radius * cos(d_theta * i), radius * sin(d_theta * i))
	var p1 := Vector3(x, radius * cos(d_theta * (i + 1)), radius * sin(d_theta * (i + 1)))
	return p0.lerp(p1, t)
