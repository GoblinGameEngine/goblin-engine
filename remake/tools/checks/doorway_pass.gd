var space = root.get_world_3d().direct_space_state
var doors = root.get_tree().get_nodes_in_group('remake_door')
var cap = CapsuleShape3D.new()
cap.radius = 0.25
cap.height = 1.75
var done = {}
var res = []
var nok = 0
for d in doors:
	if d.locked or 'closet' in d.door_id or d.door_id.begins_with('cl') or d.door_id == 'dr_cl': continue
	var key = str(d.get_parent().get_instance_id()) + d.door_id
	if done.has(key): continue
	done[key] = true
	var cs = null
	for c in d.get_children():
		if c is CollisionShape3D: cs = c
	var lw = cs.shape.size.x
	var closed = d.get_parent().global_transform * Transform3D(Basis(Vector3.UP, d._closed_rot), d.position)
	var along = closed.basis.x.normalized()
	var nrm = closed.basis.z.normalized()
	var width = lw * (2 if d.partners.size() > 0 else 1)
	var centre = closed.origin + along * (width / 2.0)
	if d.partners.size() > 0:
		# centre between the two hinges
		var p = d.partners[0]
		var pc = p.get_parent().global_transform * Transform3D(Basis(Vector3.UP, p._closed_rot), p.position)
		centre = (closed.origin + pc.origin) / 2.0
	var base = centre.y
	# open all leaves of this door instantly
	var floors = []
	for s in [-1, 1]:
		var from = centre + nrm * (0.75 * s) + Vector3.UP * 1.2
		var hit = space.intersect_ray(PhysicsRayQueryParameters3D.create(from, from + Vector3.DOWN * 2.5))
		floors.append(hit.position.y if hit else base - 1.0)
	var z = base + 0.07
	var a = Vector3(centre.x, z, centre.z) + nrm * -0.75 + Vector3.UP * (1.75 / 2.0)
	var q = PhysicsShapeQueryParameters3D.new()
	q.shape = cap
	q.transform = Transform3D(Basis(), a)
	q.motion = nrm * 1.5
	var r = space.cast_motion(q)
	var bld = d.get_parent()
	while bld and not (bld is RemakeBuilding): bld = bld.get_parent()
	if r[0] < 1.0:
		var hitp = a + nrm * 1.5 * r[1]
		q.transform = Transform3D(Basis(), hitp)
		q.motion = Vector3.ZERO
		var ri = space.get_rest_info(q)
		var who = ''
		if ri.has('collider_id'):
			var o = instance_from_id(ri.collider_id)
			if o: who = str(o.get_parent().name) + '/' + str(o.name)
		var lp = bld.global_transform.affine_inverse() * (ri.point if ri.has('point') else hitp)
		res.append('%s %s frac %.2f floors(%.2f,%.2f) base %.2f hit %s at (%.2f,%.2f,%.2f)' % [bld.name, d.door_id, r[0], floors[0], floors[1], base, who, lp.x, -lp.z, lp.y])
	else:
		nok += 1
res.push_front('passable: %d' % nok)
return res
