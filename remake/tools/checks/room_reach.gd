var s = root.get_tree().current_scene
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
	# bake around the whole building (its merged visual mesh), not just the rooms' lights
	var box = AABB(b.global_position, Vector3.ZERO)
	for l in lights: box = box.expand(l.global_position)
	var ms = [b]
	while ms.size() > 0:
		var n2 = ms.pop_back()
		for c in n2.get_children():
			ms.append(c)
			if c is MeshInstance3D and str(c.name).ends_with("_visual"):
				var ab = c.global_transform * c.get_aabb()
				box = box.merge(ab)
	box = box.grow(6.0)
	box.position.y = b.global_position.y - 3.0
	# tall enough for the highest room (a 5-storey works' top floor is ~18 m up)
	var top = 20.0
	for l in lights: top = max(top, l.global_position.y - b.global_position.y + 6.0)
	box.size.y = top
	# Recast lays its voxel grid from the bake box's corner, so a stair whose treads happen to line up
	# badly with the 5 cm cells can drop out of the navmesh: a room only counts as unreachable when it
	# fails from three different grid offsets (the player walks those stairs fine either way)
	var todo = []
	var skipped = 0
	for l in lights:
		var nmn0 = str(l.name)
		if 'fire' in nmn0 or 'cupola' in nmn0 or 'gallery' in nmn0 or 'canopy' in nmn0 or 'street' in nmn0 or 'loft' in nmn0 or 'locked' in nmn0:
			skipped += 1
		else:
			todo.append(l)
	var bad = []
	var inv = b.global_transform.affine_inverse()
	var t0 = Time.get_ticks_msec()
	var polys = 0
	for shift in [Vector3.ZERO, Vector3(0.025, 0.0125, 0.025), Vector3(0.0125, 0.006, 0.037)]:
		if todo.is_empty(): break
		var nm = NavigationMesh.new()
		nm.agent_radius = 0.25
		nm.agent_height = 1.7
		nm.agent_max_climb = 0.36
		nm.agent_max_slope = 52.0
		nm.cell_size = 0.05
		nm.cell_height = 0.025
		nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
		nm.filter_baking_aabb = AABB(box.position + shift, box.size)
		# only this building and its own ground patch (in a batch, neighbours' yards and elevator bins can
		# reach into the box): both go in a bake group for the parse
		nm.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
		nm.geometry_source_group_name = &"reach_bake"
		b.add_to_group(&"reach_bake")
		for gp in s.get_children():
			if gp is StaticBody3D and not (gp is RemakeBuilding) and Vector2(gp.global_position.x - b.global_position.x, gp.global_position.z - b.global_position.z).length() < 0.5:
				gp.add_to_group(&"reach_bake")
		var src = NavigationMeshSourceGeometryData3D.new()
		NavigationServer3D.parse_source_geometry_data(nm, src, s)
		for gn in root.get_tree().get_nodes_in_group(&"reach_bake"):
			gn.remove_from_group(&"reach_bake")
		NavigationServer3D.bake_from_source_geometry_data(nm, src)
		polys = max(polys, nm.get_polygon_count())
		var map = NavigationServer3D.map_create()
		NavigationServer3D.map_set_cell_size(map, 0.05)
		NavigationServer3D.map_set_cell_height(map, 0.025)
		NavigationServer3D.map_set_active(map, true)
		var reg = NavigationServer3D.region_create()
		NavigationServer3D.region_set_map(reg, map)
		NavigationServer3D.region_set_navigation_mesh(reg, nm)
		NavigationServer3D.map_force_update(map)
		# start: the street, 3 m in front of the building's visual mesh (its +y face is Godot -z)
		var vis_box = AABB(b.global_position, Vector3.ZERO)
		var ms2 = [b]
		while ms2.size() > 0:
			var n3 = ms2.pop_back()
			for c in n3.get_children():
				ms2.append(c)
				if c is MeshInstance3D and str(c.name).ends_with("_visual"):
					vis_box = c.global_transform * c.get_aabb()
		var start = NavigationServer3D.map_get_closest_point(map, Vector3(vis_box.get_center().x, b.global_position.y + 0.1, vis_box.position.z - 3.0))
		var still = []
		bad = []
		for l in todo:
			var nmn = str(l.name)
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
				var hit = space.intersect_ray(PhysicsRayQueryParameters3D.create(q, q + Vector3.DOWN * 14.0))
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
				still.append(l)
				var lp = inv * p
				bad.append('%s at (%.1f,%.1f,%.1f) %s' % [nmn, lp.x, -lp.z, lp.y, best])
		todo = still
		NavigationServer3D.free_rid(reg)
		NavigationServer3D.free_rid(map)
	out.append('%s: %d rooms/lights, %d unreachable, bake %d ms, polys %d' % [b.name, lights.size() - skipped, bad.size(), Time.get_ticks_msec() - t0, polys])
	for x in bad: out.append('    ' + x)
return out
