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
	"bloom_", "stem_", "weed_", "perimleaf_", "dash_", "corn_", "soy_",
]
const DECOR_EXACT_NAMES := ["streets_dashes"]
const MIN_GROUP_SIZE := 4  # below this, a MultiMesh node isn't worth the overhead
const GRID_CELL := 35.0    # meters per bucket -- a few house-lots wide

static func _grid_key(pos: Vector3) -> String:
	return "%d_%d" % [floori(pos.x / GRID_CELL), floori(pos.z / GRID_CELL)]

## ORIGINAL BUG (flat neighborhood map, pre-station-ring): MultiMesh-
## Instance3D geometry reported badly wrong values to the depth buffer
## the screen-space outline pass (screen_outline.gdshader) reads --
## measured directly at the time, a conifer tree 10.99m from the camera
## read back as 147.64m, ~13x too far, while an ordinary MeshInstance3D
## (a house, same toon.gdshader material) read correctly at every
## distance tested. Root cause was never fully chased into Godot's own
## internals then -- fixed pragmatically by disabling batching entirely.
##
## RE-TESTED LIVE for the station-ring neighborhood (this feature):
## reproduced the exact methodology above -- debug_mode 3's raw depth
## readback, byte-for-byte pixel comparison between a MultiMeshInstance3D
## and an identical MeshInstance3D control at the same position -- across
## three increasingly faithful attempts (a single instance; 4 instances
## with ToonShading applied afterward, matching Main.gd's real ordering;
## thin tree-like geometry at the original bug's own ~11m distance).
## Every attempt: ZERO byte differences across 80-180 sampled pixels
## each. The bug did not reproduce. Re-enabled on that basis, PLUS a
## defensive fix regardless of whether it was ever the actual cause:
## _build_multimesh() below now computes and sets custom_aabb explicitly
## after all instance transforms are assigned, rather than leaving
## Godot's automatic AABB to whatever it infers from mm.instance_count
## having been set with default-identity transforms first (see that
## function's own comment) -- removes a plausible timing dependency
## outright rather than merely fail to reproduce a bug that depends on it.
const ENABLE_MULTIMESH_BATCHING := true

static func optimize(root: Node3D) -> Dictionary:
	var decor: Array = []
	_collect_decor(root, decor)

	for m in decor:
		(m as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	if not ENABLE_MULTIMESH_BATCHING:
		return {"decor_total": decor.size(), "multimeshes": 0, "collapsed": 0}

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

	# Explicit custom_aabb spanning every instance's actual placed
	# position, computed AFTER all real transforms are set below --
	# see the ENABLE_MULTIMESH_BATCHING comment above for why (a
	# defensive fix, not a confirmed-necessary one).
	var mesh_local_aabb: AABB = first.mesh.get_aabb() if first.mesh else AABB()
	var combined_aabb: AABB
	var aabb_started := false

	var root_inv := root.global_transform.affine_inverse()
	for i in range(members.size()):
		var m: MeshInstance3D = members[i]
		var local_xform := root_inv * m.global_transform
		mm.set_instance_transform(i, local_xform)
		for corner_idx in range(8):
			var world_corner := local_xform * mesh_local_aabb.get_endpoint(corner_idx)
			if not aabb_started:
				combined_aabb = AABB(world_corner, Vector3.ZERO)
				aabb_started = true
			else:
				combined_aabb = combined_aabb.expand(world_corner)
		var p := m.get_parent()
		if p:
			p.remove_child(m)
		m.queue_free()

	if aabb_started:
		mmi.custom_aabb = combined_aabb
