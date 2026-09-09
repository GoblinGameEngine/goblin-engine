extends Node
class_name LakeSetup

# Finds Summit Lake's water-surface mesh (built in build_neighborhood.py's
# build_lake(), named "lake_water_surface" -- no "-col" suffix, so it's
# visual-only, no collision) and attaches LakeWater.gd to it for the
# animated-UV-scroll effect. Everything else about the lake (beach,
# parking lot, underwater floor, invisible wall, signs) is plain static
# geometry/collision that needs no runtime setup at all.

const WATER_SCRIPT := preload("res://scripts/world/LakeWater.gd")

static func setup(root: Node3D) -> bool:
	var mesh := _find(root)
	if mesh == null:
		return false
	mesh.set_script(WATER_SCRIPT)
	return true

static func _find(node: Node) -> MeshInstance3D:
	if node.name.begins_with("lake_water_surface") and node is MeshInstance3D:
		return node
	for c in node.get_children():
		var found := _find(c)
		if found:
			return found
	return null
