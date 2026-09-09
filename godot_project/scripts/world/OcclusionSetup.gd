extends Node
class_name OcclusionSetup

# Tier 2 optimization: occlusion culling. Godot's docs are explicit that
# open fields barely benefit from this, but "interiors, cities, and
# canyon-style layouts benefit enormously" -- a residential street lined
# with houses is exactly that case: standing on Lloyd St, everything behind
# the houses on Ira Ave doesn't need to be rendered at all, but frustum
# culling alone can't know that (it's still within the view cone).
#
# There's no headless/runtime way to bake occluders from real mesh geometry
# (that's an editor-only tool) -- instead, every house gets one simple
# BoxOccluder3D sized to its footprint/height. A box doesn't account for
# the door/window openings, so it's slightly conservative (it can hide
# something technically visible through an open doorway at a steep angle),
# but that's the standard trade a simplified occluder makes, and a solid
# house reads as "opaque" for occlusion purposes the overwhelming majority
# of the time anyway.

static func setup(root: Node3D) -> int:
	if not ProjectSettings.get_setting("rendering/occlusion_culling/use_occlusion_culling", false):
		ProjectSettings.set_setting("rendering/occlusion_culling/use_occlusion_culling", true)

	var houses: Array = []
	_collect_houses(root, houses)
	for house in houses:
		_add_box_occluder(house)
	return houses.size()

static func _collect_houses(node: Node, out: Array) -> void:
	if node.name.begins_with("House_") and node is Node3D:
		out.append(node)
	for c in node.get_children():
		_collect_houses(c, out)

static func _add_box_occluder(house: Node3D) -> void:
	var aabb := _combined_aabb(house)
	if aabb.size == Vector3.ZERO:
		return
	var occ := OccluderInstance3D.new()
	var shape := BoxOccluder3D.new()
	# Shrink slightly (a real box exactly matching the mesh can z-fight/
	# false-negative against the geometry it's meant to represent).
	shape.size = aabb.size * 0.92
	occ.occluder = shape
	house.add_child(occ)
	occ.position = aabb.get_center()  # aabb is already in house-local space

static func _combined_aabb(house: Node3D) -> AABB:
	# Godot's `to_local()` only transforms points, not AABB size vectors
	# directly -- but house roots are always axis-aligned at 0/90/180/270
	# degrees (see build_neighborhood.py), so converting the min/max
	# CORNERS to local space and rebuilding the box from those stays exact
	# even though a naive `to_local(world_aabb.position/size)` wouldn't be
	# for an arbitrarily-rotated house.
	var result := AABB()
	var first := true
	for c in house.get_children():
		if c is MeshInstance3D and (c as MeshInstance3D).mesh != null:
			var world_aabb: AABB = c.global_transform * c.get_aabb()
			var lo := house.to_local(world_aabb.position)
			var hi := house.to_local(world_aabb.position + world_aabb.size)
			var box := AABB(Vector3(min(lo.x, hi.x), min(lo.y, hi.y), min(lo.z, hi.z)),
				Vector3(abs(hi.x - lo.x), abs(hi.y - lo.y), abs(hi.z - lo.z)))
			if first:
				result = box
				first = false
			else:
				result = result.merge(box)
	return result
