for d in root.get_tree().get_nodes_in_group('remake_door'):
	if d.locked: continue
	d.rotation.y = d._closed_rot + d.open_sign * d.OPEN_ANGLE
	d.is_open = true
return 'ok'
