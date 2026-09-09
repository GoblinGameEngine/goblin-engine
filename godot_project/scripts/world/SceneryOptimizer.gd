extends Node
class_name SceneryOptimizer

# Post-import performance pass for the neighborhood scene (Tier 1
# optimization -- see reference/memory.txt):
#  1. Disables shadow casting on decorative (non-collision) scenery --
#     small foliage detail costs real shadow-pass time for very little
#     visible shadow contribution.
#  2. Groups decorative MeshInstance3D nodes that share the exact same
#     mesh + material AND fall in the same coarse map-grid cell (see
#     build_neighborhood.py's shared-geometry helpers: place_shared() + the
#     small fixed color palettes) into MultiMeshInstance3D nodes -- real
#     GPU instancing, one draw call per group instead of one per leaf/bush/
#     weed/flower/perimeter-hedge-clump. The grid-cell part of the key
#     matters as much as (mesh, material): grouping purely by (mesh,
#     material) merged instances scattered across the ENTIRE map into one
#     MultiMesh whose bounding box therefore spans the whole map -- Godot
#     frustum-culls a MultiMeshInstance3D as ONE unit, so that box was
#     essentially never off-screen, meaning every instance in the group got
#     processed every frame regardless of where the camera was pointed.
#     Individual MeshInstance3D nodes used to get culled independently;
#     bucketing by grid cell keeps each MultiMesh's bounding box small
#     enough that distant ones are properly culled again.
#
# Collision ("-col"-suffixed in Blender, StaticBody3D-wrapped on import)
# geometry is left completely alone: trunks, fence posts/rails, houses,
# curbs, etc. each need their own individual collision regardless of
# whether their mesh data happens to be shared.

const DECOR_PREFIXES := [
	"leaf_", "conifer_", "canopy_", "drape_", "branch_", "bush_", "bushspike_",
	"bloom_", "stem_", "weed_", "perimleaf_", "dash_",
]
const DECOR_EXACT_NAMES := ["streets_dashes"]
const MIN_GROUP_SIZE := 4  # below this, a MultiMesh node isn't worth the overhead
const GRID_CELL := 35.0    # meters per bucket -- a few house-lots wide

static func _grid_key(pos: Vector3) -> String:
	return "%d_%d" % [floori(pos.x / GRID_CELL), floori(pos.z / GRID_CELL)]

static func optimize(root: Node3D) -> Dictionary:
	var decor: Array = []
	_collect_decor(root, decor)

	for m in decor:
		(m as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	var groups: Dictionary = {}  # "<mesh id>_<material id>_<grid cell>" -> Array[MeshInstance3D]
	for m in decor:
		var mi: MeshInstance3D = m
		var mesh := mi.mesh
		if mesh == null or mesh.get_surface_count() == 0:
			continue
		var mat := mi.get_surface_override_material(0)
		if mat == null:
			mat = mesh.surface_get_material(0)
		var key := "%d_%d_%s" % [mesh.get_instance_id(), (mat.get_instance_id() if mat else 0), _grid_key(mi.global_position)]
		if not groups.has(key):
			groups[key] = []
		groups[key].append(mi)

	var mm_count := 0
	var collapsed_count := 0
	for key in groups.keys():
		var members: Array = groups[key]
		if members.size() < MIN_GROUP_SIZE:
			continue
		_build_multimesh(root, members)
		mm_count += 1
		collapsed_count += members.size()

	return {"decor_total": decor.size(), "multimeshes": mm_count, "collapsed": collapsed_count}

static func _collect_decor(node: Node, out: Array) -> void:
	if node is MeshInstance3D:
		var matched := DECOR_EXACT_NAMES.has(node.name)
		if not matched:
			for prefix in DECOR_PREFIXES:
				if node.name.begins_with(prefix):
					matched = true
					break
		if matched:
			out.append(node)
	for c in node.get_children():
		_collect_decor(c, out)

static func _build_multimesh(root: Node3D, members: Array) -> void:
	var first: MeshInstance3D = members[0]
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = first.mesh
	mm.instance_count = members.size()

	var mmi := MultiMeshInstance3D.new()
	mmi.name = first.name + "_multimesh"
	root.add_child(mmi)  # local transform defaults to identity, matching root's own frame
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	var mat: Material = first.get_surface_override_material(0)
	if mat == null and first.mesh:
		mat = first.mesh.surface_get_material(0)
	if mat:
		mmi.material_override = mat

	var root_inv := root.global_transform.affine_inverse()
	for i in range(members.size()):
		var m: MeshInstance3D = members[i]
		mm.set_instance_transform(i, root_inv * m.global_transform)
		var p := m.get_parent()
		if p:
			p.remove_child(m)
		m.queue_free()
