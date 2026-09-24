var s = root.get_tree().current_scene
var b = s.get_node(BNAME)
var box = AABB(b.global_position, Vector3.ZERO).grow(14.0)
box.position.y = b.global_position.y - 3.0
box.size.y = 20.0
var nm = NavigationMesh.new()
nm.agent_radius = 0.25
nm.agent_height = 1.7
nm.agent_max_climb = 0.36
nm.agent_max_slope = 52.0
nm.cell_size = 0.05
nm.cell_height = 0.025
nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
nm.filter_baking_aabb = box
var src = NavigationMeshSourceGeometryData3D.new()
NavigationServer3D.parse_source_geometry_data(nm, src, s)
NavigationServer3D.bake_from_source_geometry_data(nm, src)
var map = NavigationServer3D.map_create()
NavigationServer3D.map_set_cell_size(map, 0.05)
NavigationServer3D.map_set_cell_height(map, 0.025)
NavigationServer3D.map_set_active(map, true)
var reg = NavigationServer3D.region_create()
NavigationServer3D.region_set_map(reg, map)
NavigationServer3D.region_set_navigation_mesh(reg, nm)
NavigationServer3D.map_force_update(map)
var out = []
var inv = b.global_transform.affine_inverse()
for pt in PTS:
	var g = b.global_transform * Vector3(pt[0], pt[2], -pt[1])
	var c = inv * NavigationServer3D.map_get_closest_point(map, g)
	out.append('(%.2f,%.2f,%.2f) -> (%.2f,%.2f,%.2f)' % [pt[0], pt[1], pt[2], c.x, -c.z, c.y])
NavigationServer3D.free_rid(reg)
NavigationServer3D.free_rid(map)
return out
