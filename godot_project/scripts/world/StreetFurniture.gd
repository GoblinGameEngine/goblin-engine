extends Node
class_name StreetFurniture

# Fire hydrant + lamp post placement along downtown/residential streets
# (blender_scripts/build_street_furniture.py's fire_hydrant.glb/
# lamp_post.glb). One shared placement routine for both zones despite
# downtown's streets being straight and residential's being curved:
# callers hand in an `x_at` Callable(s: float) -> float giving the
# street's actual axial position at arc length s -- a constant-x lambda
# for downtown's straight streets, ResidentialGenerator._curve_x_at()
# (bound to that path's own waypoints) for residential's meandering
# ones. Node names are lowercase with the underscore DistanceCulling.gd's
# SMALL_KEYWORDS ("hydrant", "lamp_post") and OcclusionSetup's box-
# occluder pass don't need to (street furniture is too small/thin to be
# a useful occluder) actually match on.

const HYDRANT_SCENE := preload("res://assets/street_furniture/fire_hydrant.glb")
const LAMP_SCENE := preload("res://assets/street_furniture/lamp_post.glb")

const LAMP_INTERVAL := 30.0     # meters between lamp posts along one sidewalk edge
const HYDRANT_INTERVAL := 90.0  # meters between hydrants -- sparser, real-world-ish spacing
const PLACEMENTS_PER_FRAME := 4  # yield budget -- each one carries a create_trimesh_collision() call

## Places lamp posts along EVERY offset in `edge_offsets` (each an axial
## distance from the street's own x, e.g. +/-(half-width + sidewalk) for
## the two sidewalk edges), at LAMP_INTERVAL arc-length spacing, plus
## fire hydrants at the sparser HYDRANT_INTERVAL on just `edge_offsets[0]`
## (one side only -- matches how real hydrants are placed, not every
## street edge). `x_at(s)` gives the street's actual axial position at
## arc length s. Yields (RingCoords.yield_frame()) every
## PLACEMENTS_PER_FRAME items -- called from ZoneStreamer.gd's background
## zone-detail loading, same reasoning as CropFieldGenerator.build_async().
## Returns placement counts for a one-line boot log, same convention as
## this project's other generator/optimizer return dicts.
static func place_along_async(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, x_at: Callable, edge_offsets: Array) -> Dictionary:
	var lamp_count := 0
	var s := s_start + LAMP_INTERVAL * 0.5
	while s < s_end:
		var base_x: float = x_at.call(s)
		for off in edge_offsets:
			_place_one(parent, LAMP_SCENE, "lamp_post", radius, segments, s, base_x + float(off), lamp_count)
			lamp_count += 1
			if lamp_count % PLACEMENTS_PER_FRAME == 0:
				await RingCoords.yield_frame()
		s += LAMP_INTERVAL

	var hydrant_count := 0
	if not edge_offsets.is_empty():
		s = s_start + HYDRANT_INTERVAL * 0.5
		while s < s_end:
			var base_x: float = x_at.call(s)
			_place_one(parent, HYDRANT_SCENE, "fire_hydrant", radius, segments, s, base_x + float(edge_offsets[0]), hydrant_count)
			hydrant_count += 1
			if hydrant_count % PLACEMENTS_PER_FRAME == 0:
				await RingCoords.yield_frame()
			s += HYDRANT_INTERVAL

	return {"lamps": lamp_count, "hydrants": hydrant_count}

const LAMP_LIGHT_HEIGHT := 3.98  # meters up the pole, at the lantern head -- see build_street_furniture.py's own head_z math
const LAMP_LIGHT_COLOR := Color(1.0, 0.85, 0.55)
const LAMP_LIGHT_RANGE := 14.0
const LAMP_LIGHT_ENERGY := 3.0

static func _place_one(parent: Node3D, scene: PackedScene, name_prefix: String,
		radius: float, segments: int, s: float, x: float, index: int) -> void:
	var inst := scene.instantiate()
	inst.name = "%s_%d" % [name_prefix, index]
	RingCoords.place_on_ring(inst, radius, segments, s, x)
	parent.add_child(inst)
	RingCoords.add_trimesh_collision(inst)

	if name_prefix == "lamp_post":
		# Requested directly: streetlights need to actually emit light at
		# night. shadow_enabled=false -- with potentially hundreds of these
		# live at once, per-light shadow maps would be a real cost for a
		# small decorative glow; DaySkySystem.gd toggles `visible` in bulk
		# via the "lamp_lights" group rather than every light checking the
		# time of day itself each frame. Initial visibility reads
		# DaySkySystem's CURRENT global state (a static var, not an
		# instance call -- this runs from generator code with no
		# DaySkySystem reference) so a lamp post streamed in at night
		# already starts lit instead of waiting for the next day/night
		# transition to notice it exists.
		var light := OmniLight3D.new()
		light.name = "lamp_light"
		light.light_color = LAMP_LIGHT_COLOR
		light.omni_range = LAMP_LIGHT_RANGE
		light.light_energy = LAMP_LIGHT_ENERGY
		light.shadow_enabled = false
		light.position = Vector3(0.0, LAMP_LIGHT_HEIGHT, 0.0)
		light.visible = DaySkySystem.lamp_light_on
		light.add_to_group("lamp_lights")
		inst.add_child(light)
