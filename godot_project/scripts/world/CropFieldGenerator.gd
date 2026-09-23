extends Node
class_name CropFieldGenerator

# Scatters individual billboard-quad MeshInstance3D "stalks" (corn_sprite.
# png / soy_sprite.png, see blender_scripts/gen_crop_sprites.py) across a
# field footprint on the ring floor. Deliberately does NOT build a
# MultiMeshInstance3D itself -- each stalk is named "corn_<n>"/"soy_<n>",
# matching SceneryOptimizer.DECOR_PREFIXES, so the existing batching pass
# (SceneryOptimizer.optimize(), already run once per zone by
# NeighborhoodGenerator.build()) groups and instances them the same way
# it already does for trees/bushes/weeds -- one system, not a second one
# to maintain.
#
# Each stalk gets a FULL ring basis (RingCoords.floor_basis(), not a bare
# Y-rotation), so its own local Y axis is the true "up" at its position
# on the curved floor. toon.gdshader's vertex() billboard override reads
# that per-instance MODEL_MATRIX Y axis (not world Y) to decide which way
# is "up" when rotating the quad to face the camera -- required here
# specifically because "up" varies by position around the ring, unlike a
# flat map where world Y would already be correct.

const CORN_SPRITE := preload("res://assets/textures/corn_sprite.png")
const SOY_SPRITE := preload("res://assets/textures/soy_sprite.png")

const ROW_SPACING := 5.0    # meters between stalks, both axes -- a visual "planted field" density, not literal real-world row spacing (that would be ~10-100x denser than this billboard system needs to look right from normal play distance)
const JITTER := 1.6         # meters, random per-stalk offset so the grid doesn't read as a perfect lattice
const CORN_HEIGHT := 2.3    # meters, full-grown sweet corn
const SOY_HEIGHT := 0.7
const EDGE_MARGIN := 10.0   # s-distance kept clear at each field end (road shoulder buffer)
const CONNECTOR_CLEARANCE := 9.0  # +/- s-distance kept clear around each cross-connector road
const STALKS_PER_FRAME := 60  # yield budget -- cheap per-stalk (no collision), so a big batch is fine

## Per-crop-type shared mesh + material, built lazily once and reused for
## EVERY stalk of that crop across the whole build (even across multiple
## build() calls/fields) -- SceneryOptimizer's grouping key is keyed off
## (mesh instance id, material instance id, grid cell), so giving each
## stalk its own freshly-`.new()`-ed QuadMesh/StandardMaterial3D would
## make every stalk its own group of 1, permanently under
## SceneryOptimizer.MIN_GROUP_SIZE -- nothing would ever batch. Per-stalk
## size variance below comes entirely from the instance TRANSFORM's scale
## instead, which is what MultiMesh instancing is actually built to vary.
static var _mesh_cache: Dictionary = {}
static var _mat_cache: Dictionary = {}

static func _shared_mesh_and_material(crop: String) -> Array:
	if _mesh_cache.has(crop):
		return [_mesh_cache[crop], _mat_cache[crop]]
	var sprite: Texture2D = CORN_SPRITE if crop == "corn" else SOY_SPRITE
	var aspect := float(sprite.get_width()) / float(sprite.get_height())
	var quad := QuadMesh.new()
	quad.size = Vector2(aspect, 1.0)  # unit height; per-stalk height set via transform scale
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = sprite
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mesh_cache[crop] = quad
	_mat_cache[crop] = mat
	return [quad, mat]

## Scatters one field of `crop` ("corn" or "soy") over the rectangle
## s in [s_start, s_end] x x in [x_min, x_max]. `connector_s` is the list
## of arc-length positions where a perpendicular road crosses this field
## (FarmGenerator's 4 wall-to-wall connectors) -- stalks within
## CONNECTOR_CLEARANCE of any of those are skipped so the field doesn't
## grow through the road surface. Yields (RingCoords.yield_frame()) every
## STALKS_PER_FRAME stalks -- ZoneStreamer.gd streams this in while the
## player may already be walking around nearby, and a farm field runs to
## ~1000+ stalks, measured taking a real, stutter-worthy chunk of the
## ~460ms a whole farm zone's synchronous detail build used to cost.
static func build_async(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, x_min: float, x_max: float,
		crop: String, connector_s: Array, rng: RandomNumberGenerator) -> int:
	var base_height: float = CORN_HEIGHT if crop == "corn" else SOY_HEIGHT
	var mesh_and_mat := _shared_mesh_and_material(crop)
	var quad: QuadMesh = mesh_and_mat[0]
	var mat: StandardMaterial3D = mesh_and_mat[1]

	var count := 0
	var s := s_start + EDGE_MARGIN
	while s < s_end - EDGE_MARGIN:
		var blocked := false
		for cs in connector_s:
			if absf(s - float(cs)) < CONNECTOR_CLEARANCE:
				blocked = true
				break
		if not blocked:
			var x := x_min
			while x < x_max:
				var jx: float = x + rng.randf_range(-JITTER, JITTER)
				var js: float = s + rng.randf_range(-JITTER, JITTER)
				# Skip stalks over carved ground -- a farm field's own
				# footprint has no idea the river/ponds/creeks/ditches now
				# cut through it (TerrainHeight was built after this field
				# layout), so without this a crop would appear to grow
				# out of open water. RingCoords.floor_point() already
				# follows the carved terrain correctly wherever a stalk
				# DOES get placed -- this only prevents placing one in the
				# water in the first place.
				if TerrainHeight.depth_at(radius, segments, js, jx) < 0.15:
					_place_stalk(parent, radius, segments, js, jx, quad, mat, base_height, crop, count, rng)
				count += 1
				if count % STALKS_PER_FRAME == 0:
					await RingCoords.yield_frame()
				x += ROW_SPACING
		s += ROW_SPACING
	return count

static func _place_stalk(parent: Node3D, radius: float, segments: int, s: float, x: float,
		quad: QuadMesh, mat: StandardMaterial3D, base_height: float, crop: String, index: int,
		rng: RandomNumberGenerator) -> void:
	var h: float = base_height * rng.randf_range(0.82, 1.18)

	var mi := MeshInstance3D.new()
	mi.name = "%s_%d" % [crop, index]
	mi.mesh = quad
	# Per-SURFACE override, not the whole-instance material_override --
	# SceneryOptimizer._build_multimesh() reads a member's material via
	# get_surface_override_material(0) (falling back to the mesh
	# resource's own baked-in surface material, which a bare procedural
	# QuadMesh never has), the same property ToonShading.apply_to_world's
	# MeshInstance3D branch reads/replaces via get_active_material(i)/
	# set_surface_override_material(i, ...). Using material_override here
	# instead left every batched MultiMeshInstance3D with no material at
	# all -- confirmed live, rendered as Godot's default black/white
	# checker fallback instead of the sprite.
	mi.set_surface_override_material(0, mat)
	parent.add_child(mi)

	var basis := RingCoords.floor_basis(radius, segments, s)
	# QuadMesh is centered on its own origin -- lift by half its height
	# along local "up" so the bottom edge sits on the floor instead of
	# the stalk being buried knee-deep. Uses the UNSCALED unit basis.y
	# for this offset (the scaled copy below is only for the transform's
	# rotation/scale part, not this position math).
	var pos := RingCoords.floor_point(radius, segments, s, x) + basis.y * (h * 0.5)
	var xform_basis := basis.scaled(Vector3(h, h, h))
	mi.global_transform = Transform3D(xform_basis, pos)
