class_name RemakeLodClusters
## Hierarchical LOD for many placed buildings (the distance versions gblod.py exports beside each
## glb: <id>.lod1/2/3.glb).
##
## Per building: LOD0 (the full glb, doors and lights -- a RemakeBuilding) and LOD1 (the exterior)
## switch by distance, scaled by the building's size.  Farther out, buildings are drawn by merged
## meshes: every normal-size building's LOD2 in a CELL2 m cell becomes one mesh (one draw call), its
## LOD3 in a CELL3 m cell another.  Visibility parents chain them: a building's LOD1 hides while its
## cell's LOD2 mesh shows, and that hides while the coarser cell's LOD3 mesh shows.  Landmarks (15 m
## tall or 45 m long or more: elevators, spires, towers, silos, factories, long bridges) stay out
## of the merge and keep their own full chain, so they don't coarsen with their cell.
##
## Switch distances are for a ~12 m building (LOD1 from 60 m, LOD2 from 200 m, LOD3 from 600 m); a
## merged cell switches once its farthest building has passed them.

const D1 := 60.0
const D2 := 200.0
const D3 := 600.0
const CELL2 := 150.0
const CELL3 := 400.0
const LANDMARK_H := 15.0            # a landmark: this tall or taller (spires, elevators, towers, silos) ...
const LANDMARK_W := 45.0            # ... or this long (big blocks, factories, long bridges)
const MARGIN := 0.08                 # hysteresis at each switch, a fraction of the distance

## entries: Array of Dictionaries {id: String, xform: Transform3D (in parent's space),
##   key2: Variant, key3: Variant (cell keys: buildings with equal keys merge)}.
## full: build each building's LOD0 too (false when a streamer loads LOD0 on demand).
## Returns {"buildings": n, "cells2": n, "cells3": n, "landmarks": n}.
static func build(parent: Node3D, entries: Array, full := true) -> Dictionary:
	var lod_scenes := {}
	var cells2 := {}
	var cells3 := {}
	var lod1_of_cell2 := {}
	var landmarks := 0
	for e in entries:
		var id: String = e.id
		if not lod_scenes.has(id):
			lod_scenes[id] = []
			for l in [1, 2, 3]:
				var p := "res://remake/buildings/%s.lod%d.glb" % [id, l]
				lod_scenes[id].append(load(p) if ResourceLoader.exists(p) else null)
		var sc: Array = lod_scenes[id]
		if sc[0] == null:
			continue
		var root := Node3D.new()
		root.name = id
		root.transform = e.xform
		parent.add_child(root)
		var lod1: Node3D = sc[0].instantiate()
		root.add_child(lod1)
		RemakeBuilding.prepare_lod(lod1, "res://remake/buildings/%s.lod1.glb" % id)
		# size and prominence from the massing (LOD2 has no yard props): switch distances scale with
		# it, and a tall or very long building is a landmark that keeps its own chain
		var l2: Node3D = sc[1].instantiate() if sc[1] else null
		var ab := _aabb(l2 if l2 else lod1)
		var wide := maxf(ab.size.x, ab.size.z)
		var k := clampf(maxf(ab.size.y, wide * 0.8) / 12.0, 0.7, 4.0)
		var landmark := ab.size.y >= LANDMARK_H or wide >= LANDMARK_W
		if full:
			var b := RemakeBuilding.new()
			root.add_child(b)
			b.load_building(load("res://remake/buildings/%s.glb" % id))
			_ranges(b, 0.0, D1 * k)
			_light_fade(b)
		if landmark:
			# its own chain all the way out
			landmarks += 1
			_ranges(lod1, D1 * k, D2 * k)
			for l in [2, 3]:
				var inst: Node3D = l2 if l == 2 else (sc[2].instantiate() if sc[2] else null)
				if inst == null:
					continue
				root.add_child(inst)
				RemakeBuilding.prepare_lod(inst, "res://remake/buildings/%s.lod%d.glb" % [id, l])
				_ranges(inst, (D2 if l == 2 else D3) * k, D3 * k if l == 2 else 0.0)
			continue
		_ranges(lod1, D1 * k, 0.0)
		for pair in [[cells2, e.key2, 1], [cells3, e.key3, 2]]:
			var cells: Dictionary = pair[0]
			if sc[pair[2]] == null:
				continue
			if not cells.has(pair[1]):
				cells[pair[1]] = {"st": SurfaceTool.new(), "n": 0, "key3": e.key3}
				cells[pair[1]].st.begin(Mesh.PRIMITIVE_TRIANGLES)
			var c: Dictionary = cells[pair[1]]
			_append(c.st, l2 if pair[2] == 1 else sc[pair[2]].instantiate(), e.xform)
			c.n += 1
		if not lod1_of_cell2.has(e.key2):
			lod1_of_cell2[e.key2] = []
		lod1_of_cell2[e.key2].append(lod1)
	# the merged meshes, and the visibility chain LOD1 -> cell LOD2 -> cell LOD3
	var nodes3 := {}
	for key in cells3:
		var mi := _commit(cells3[key].st, "lod3_%s" % str(key))
		parent.add_child(mi)
		var r := _radius(mi)
		mi.visibility_range_begin = D3 + r
		mi.visibility_range_begin_margin = (D3 + r) * MARGIN
		nodes3[key] = mi
	for key in cells2:
		var mi := _commit(cells2[key].st, "lod2_%s" % str(key))
		parent.add_child(mi)
		var r := _radius(mi)
		mi.visibility_range_begin = D2 + r
		mi.visibility_range_begin_margin = (D2 + r) * MARGIN
		var p3: MeshInstance3D = nodes3.get(cells2[key].key3)
		if p3:
			mi.visibility_parent = mi.get_path_to(p3)
		for lod1 in lod1_of_cell2.get(key, []):
			_parent_all(lod1, mi)
	return {"buildings": entries.size(), "cells2": cells2.size(), "cells3": cells3.size(), "landmarks": landmarks}


static func _append(st: SurfaceTool, inst: Node, xform: Transform3D) -> void:
	var stack: Array[Node] = [inst]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		if n is MeshInstance3D and (n as MeshInstance3D).mesh:
			var mi := n as MeshInstance3D
			var local := _local_xform(mi, inst)
			for s in mi.mesh.get_surface_count():
				st.append_from(mi.mesh, s, xform * local)
	inst.free()


static func _local_xform(n: Node3D, top: Node) -> Transform3D:
	var t := n.transform
	var p := n.get_parent()
	while p and p != top and p is Node3D:
		t = (p as Node3D).transform * t
		p = p.get_parent()
	return (top as Node3D).transform * t if top is Node3D else t


static func _commit(st: SurfaceTool, name: String) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = name
	mi.mesh = st.commit()
	mi.material_override = RemakeBuilding.lod_vc_material()
	mi.lod_bias = 1000.0
	return mi


static func _radius(mi: MeshInstance3D) -> float:
	var ab := mi.get_aabb()
	return Vector2(ab.size.x, ab.size.z).length() * 0.5


static func _aabb(n: Node) -> AABB:
	var box := AABB()
	var first := true
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is MeshInstance3D and (c as MeshInstance3D).mesh:
			var ab: AABB = (c as MeshInstance3D).get_aabb()
			box = ab if first else box.merge(ab)
			first = false
	return box


static func _ranges(n: Node, begin: float, end: float) -> void:
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			var g := c as GeometryInstance3D
			g.visibility_range_begin = begin
			g.visibility_range_begin_margin = begin * MARGIN
			g.visibility_range_end = end
			g.visibility_range_end_margin = end * MARGIN


static func _parent_all(n: Node, vis_parent: GeometryInstance3D) -> void:
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is GeometryInstance3D:
			(c as GeometryInstance3D).visibility_parent = c.get_path_to(vis_parent)


static func _light_fade(n: Node) -> void:
	# room lights out beyond ~40 m (lit windows stand in for them farther out)
	var stack: Array[Node] = [n]
	while stack.size() > 0:
		var c: Node = stack.pop_back()
		stack.append_array(c.get_children())
		if c is Light3D:
			var l := c as Light3D
			l.distance_fade_enabled = true
			l.distance_fade_begin = 35.0
			l.distance_fade_length = 10.0
