var s = root.get_node('PruettTest')
var only = ONLY_BUILDING
var space = root.get_world_3d().direct_space_state
var out = []
for b in s.get_children():
	if not (b is RemakeBuilding): continue
	if only != '' and str(b.name) != only: continue
	if str(b.name) in ['P-SITE', 'P-BR-US30', 'P-BR-RAIL', 'P-CULVERT']: continue
	var lights = []
	var stack = [b]
	while stack.size() > 0:
		var n = stack.pop_back()
		for c in n.get_children():
			stack.append(c)
			if str(c.name).begins_with('light_') and not (c is OmniLight3D): lights.append(c)
	var box = AABB(b.global_position, Vector3.ZERO)
	for l in lights: box = box.expand(l.global_position)
	box = box.grow(8.0)
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
	var t0 = Time.get_ticks_msec()
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
	# start: open ground at the corner of the search box
	var start = NavigationServer3D.map_get_closest_point(map, Vector3(box.position.x + 2.0, b.global_position.y, box.position.z + 2.0))
	var bad = []
	var inv = b.global_transform.affine_inverse()
	var skipped = 0
	for l in lights:
		var nmn = str(l.name)
		if 'fire' in nmn or 'cupola' in nmn or 'gallery' in nmn or 'canopy' in nmn or 'street' in nmn:
			skipped += 1
			continue
		var p = l.global_position
		var ok = false
		var best = ''
		for k in range(17):
			var off = Vector3.ZERO
			if k > 0:
				var ang = (k % 8) * PI / 4.0
				var rad = 0.6 if k <= 8 else 1.2
				off = Vector3(cos(ang), 0, sin(ang)) * rad
			var q = p + off
			var hit = space.intersect_ray(PhysicsRayQueryParameters3D.create(q, q + Vector3.DOWN * 6.0))
			if not hit: continue
			var fp = hit.position
			var tgt = NavigationServer3D.map_get_closest_point(map, fp)
			if Vector2(tgt.x - fp.x, tgt.z - fp.z).length() > 0.35 or absf(tgt.y - fp.y) > 0.3: continue
			var path = NavigationServer3D.map_get_path(map, start, tgt, true)
			if path.size() > 0 and path[path.size() - 1].distance_to(tgt) < 0.3:
				ok = true
				break
			var e = inv * (path[path.size() - 1] if path.size() > 0 else start)
			var lf = inv * fp
			best = 'e.g. floor(%.1f,%.1f,%.1f) pathend(%.1f,%.1f,%.1f)' % [lf.x, -lf.z, lf.y, e.x, -e.z, e.y]
		if not ok:
			var lp = inv * p
			bad.append('%s at (%.1f,%.1f,%.1f) %s' % [nmn, lp.x, -lp.z, lp.y, best])
	out.append('%s: %d rooms/lights, %d unreachable, bake %d ms, polys %d' % [b.name, lights.size() - skipped, bad.size(), Time.get_ticks_msec() - t0, nm.get_polygon_count()])
	for x in bad: out.append('    ' + x)
	NavigationServer3D.free_rid(reg)
	NavigationServer3D.free_rid(map)
return out
