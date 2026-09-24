var space = root.get_world_3d().direct_space_state
var res = []
for d in root.get_tree().get_nodes_in_group('remake_door'):
	var cs = null
	for c in d.get_children():
		if c is CollisionShape3D: cs = c
	var box = BoxShape3D.new()
	box.size = cs.shape.size * Vector3(0.8, 0.9, 0.5)
	var excl = [d.get_rid()]
	var player = root.get_tree().current_scene.get_node_or_null('TestPlayer')
	if player: excl.append(player.get_rid())
	for p in d.partners: excl.append(p.get_rid())
	var bld = d.get_parent()
	while bld and not (bld is RemakeBuilding): bld = bld.get_parent()
	var bad = []
	for ang in [0.5, 1.0]:
		var t = Transform3D(Basis(Vector3.UP, d._closed_rot + d.open_sign * d.OPEN_ANGLE * ang), d.position)
		var gt = d.get_parent().global_transform * t * cs.transform
		var q = PhysicsShapeQueryParameters3D.new()
		q.shape = box
		q.transform = gt
		q.exclude = excl
		var pts = space.collide_shape(q, 2)
		if pts.size() > 0:
			var lp = bld.global_transform.affine_inverse() * pts[0]
			var ri = space.get_rest_info(q)
			var cn = ''
			if ri.has('collider_id'):
				var o = instance_from_id(ri.collider_id)
				if o: cn = str(o.get_parent().name)
			bad.append('%s@(%.2f,%.2f,%.2f)%s' % [ang, lp.x, -lp.z, lp.y, cn])
	if bad.size() > 0:
		var h = bld.global_transform.affine_inverse() * d.global_position
		res.append('%s %s hinge(%.2f,%.2f,%.2f) size%s -> %s' % [bld.name, d.name, h.x, -h.z, h.y, str(cs.shape.size), str(bad)])
return res
