extends Node3D
class_name SpaceStation

# Bootstrap for the torus space-station map -- a deliberate physics
# prototype (validate "walk the inside of a ring under artificial
# gravity" before building any real content on top of it), not a
# finished level. See scripts/world/StationRingBuilder.gd for the ring
# geometry and scripts/StationPlayer.gd for the other half of the
# physics (radial gravity, up-direction reorientation).
#
# NOT a rotating/centrifugal station any more -- RingBody never moves.
# That model (spin the ring, feel omega^2*r as gravity) went through
# several fix rounds (orientation not co-rotating with the spin, a
# spawn embedded in the floor collision, float32 precision exploding
# at large radii, and finally the compass reading world-frame heading
# instead of station-frame while a standing-still player was correctly
# being carried around by the spin) before landing on a simpler call:
# drop the rotation entirely and use a stationary radial gravity
# gradient instead (gravity_at() below) -- an artificial-gravity-
# plating trope rather than a physically rotating habitat. That
# removes the whole category of "carried by a moving platform" bugs at
# the source: nothing here moves, so there's no platform-carry, no
# spin to co-rotate with, and no compass drift to correct for.
#
# Everything here is built at runtime in _ready() -- same "headless
# CLI/scripting, no editor GUI session" workflow the rest of this
# project uses (see README), so there's no binary asset to export/
# reimport and the dimensions below stay trivially tunable constants.
#
# LIVE TUNING: the values below are `static var`, not `const`, and every
# physics/geometry read goes through them fresh each time -- so they can
# be changed from a running game with no restart, via gcmd.py:
#
#   # "feel" params -- read fresh every physics frame, no rebuild needed:
#   run "StationPlayer.WALK_SPEED = 6.0"
#   run "StationPlayer.JUMP_VELOCITY = 5.5"
#   run "StationPlayer.MOUSE_SENSITIVITY = 0.0018"
#   run "SpaceStation.GRAVITY_BANDS = 20"   # finer/coarser gradient steps, no rebuild needed
#
#   # geometry params -- baked into the built mesh + collision, so
#   # changing these needs rebuild_ring() to regenerate them in place
#   # (tears down and rebuilds the ring, respawns the player):
#   run "root.get_tree().get_first_node_in_group('space_station').rebuild_ring({\"radius\": 800.0, \"ceiling_height\": 150.0})"
#
# rebuild_ring() takes any subset of {target_g, radius, ceiling_height,
# width, segments}; omitted keys keep their current value. Segment COUNT
# is independent of radius (it's an angular subdivision, TAU/segments --
# see StationRingBuilder's file comment), so cranking radius up just
# makes each of the same 96 segments a longer, flatter chord; it
# doesn't blow up the build cost. Keep RADIUS in the low thousands of
# meters or under regardless: past roughly that, float32 world-space
# precision starts breaking CharacterBody3D's own collision/floor-snap
# math (confirmed live, independent of whether anything is rotating).
static var RADIUS := 500.0          # floor's distance from the axis -- also the "wall" gravity_at() ramps up to
static var CEILING_HEIGHT := 150.0  # floor to ceiling
static var WIDTH := 200.0           # wall-to-wall, along the axis
static var SEGMENTS := 96           # angular subdivision -- TAU/segments per facet, independent of radius

static var TARGET_G := 9.8

# gravity_at() splits [0, RADIUS] into this many equal-width concentric
# bands and steps gravity up by TARGET_G/GRAVITY_BANDS with each one,
# 0G at the axis to a full TARGET_G at the wall (band 10 of 10) --
# requested as "increase gravity at a rate of .1G across 10 concentric
# rings." A step function, not a smooth ramp, per that spec.
static var GRAVITY_BANDS := 10

# The ring's central axis (world X -- both this node and RingBody sit
# at the origin with no rotation, permanently, so local and world space
# coincide) -- kept as a named constant rather than hardcoding
# Vector3.RIGHT at StationPlayer.gd's _radial_vector() call site.
const AXIS := Vector3.RIGHT

## Stepped radial gravity gradient: 0 at the axis, TARGET_G at the wall
## (radial_len >= RADIUS), in GRAVITY_BANDS equal steps between. See the
## GRAVITY_BANDS comment above for why a step function.
static func gravity_at(radial_len: float) -> float:
	var band_width := RADIUS / float(GRAVITY_BANDS)
	var band := clampi(ceili(radial_len / band_width), 0, GRAVITY_BANDS)
	return (float(band) / GRAVITY_BANDS) * TARGET_G

const STATION_PLAYER_SCENE := preload("res://scenes/StationPlayer.tscn")

@onready var ring_body: AnimatableBody3D = $RingBody
var player: StationPlayer

func _ready() -> void:
	add_to_group("space_station")
	_setup_environment()
	_build_ring()
	_spawn_player()
	Settings.changed.connect(_on_settings_changed)

## Same reasoning as Main.gd's own _on_settings_changed(): draw distance
## is the only Settings field that needs active re-application (baked
## into visibility_range_end on many nodes at a point in time, unlike
## the fields read live where they're used). Re-finds "Neighborhood"
## fresh each call rather than caching a reference, since rebuild_ring()
## frees and recreates it.
func _on_settings_changed() -> void:
	var neighborhood := ring_body.get_node_or_null("Neighborhood")
	if neighborhood == null:
		return
	var culled := DistanceCulling.apply_to_world(neighborhood, Settings.draw_distance_mult)
	print("SpaceStation: draw distance changed -- reapplied culling (%d small props, %d trees, %d houses, %d crop groups)" %
		[culled["small"], culled["tree"], culled["house"], culled["crop"]])

func _setup_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.01, 0.01, 0.02)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.08, 0.08, 0.1)
	env.ambient_light_energy = 0.6
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-35, 40, 0)
	sun.light_energy = 1.3
	sun.light_color = Color(1.0, 0.98, 0.92)
	sun.shadow_enabled = true
	add_child(sun)

func _build_ring() -> void:
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_texture = load("res://assets/textures/grass_tinted.png")

	var wall_mat := StandardMaterial3D.new()
	wall_mat.albedo_texture = load("res://assets/textures/station_metal_wall.png")

	var ceiling_mat := StandardMaterial3D.new()
	ceiling_mat.albedo_texture = load("res://assets/textures/station_ceiling_panel.png")

	StationRingBuilder.build(ring_body, RADIUS, CEILING_HEIGHT, WIDTH, SEGMENTS,
		floor_mat, wall_mat, ceiling_mat)
	StationRingBuilder.add_light_fixtures(ring_body, RADIUS, CEILING_HEIGHT, WIDTH, SEGMENTS, 4)

	# Cel-shade just the floor/wall/ceiling mesh, matching the rest of
	# the game's look (see ToonShading.gd) -- deliberately NOT walking
	# ring_body as a whole, so the light fixtures' emissive material
	# (added above) keeps its glow instead of being flattened into toon
	# bands.
	var ring_mesh: MeshInstance3D = ring_body.get_node("RingMesh")
	var toon_count := ToonShading.apply_to_world(ring_mesh)
	print("SpaceStation: cel-shaded %d ring materials" % toon_count)

	# The procedural Midwestern neighborhood (see the plan file / Phase
	# A-E commits) -- a separate "Neighborhood" node under ring_body, not
	# ring_body's direct children like RingMesh above, so
	# NeighborhoodGenerator.build()'s own SceneryOptimizer/ToonShading
	# passes only ever walk the neighborhood's own content, not the ring
	# shell + light fixtures too. Still a child of ring_body, so
	# rebuild_ring()'s child-free loop above tears it down and
	# regenerates it in place along with everything else, same as always.
	var neighborhood := Node3D.new()
	neighborhood.name = "Neighborhood"
	ring_body.add_child(neighborhood)
	NeighborhoodGenerator.build(neighborhood, RADIUS, CEILING_HEIGHT, WIDTH, SEGMENTS)

## Angle=0 spawn point, standing on the floor, facing along the loop --
## shared by initial spawn and by rebuild_ring()'s post-rebuild respawn
## so the two can't drift out of sync with each other.
func _floor_spawn_transform() -> Transform3D:
	# The floor's collision box (see StationRingBuilder._add_collision_segments)
	# is centered AT radius with 1.0 of radial thickness, so its actual
	# walkable surface -- the inner face the player stands on -- is at
	# radius - 0.5, not radius itself. Spawning feet at the raw radius
	# (as this used to) buries them 0.5m into the box's solid interior.
	# Confirmed live at the 100km scale: it turned the very next physics
	# frames into a depenetration explosion, launching the player at
	# ~2900 m/s -- the same 0.5m overlap was presumably always there at
	# the original 200m test radius too and just wasn't violent enough
	# to notice. A small clearance above the true surface, rather than
	# landing exactly on it, avoids spawning already-touching and
	# relying on exact float equality to mean "not overlapping."
	const SURFACE_CLEARANCE := 0.05
	var surface_radial := RADIUS - 0.5 - SURFACE_CLEARANCE
	var floor_pos := Vector3(0, surface_radial, 0)
	var up_dir := Vector3(0, -1, 0)
	var forward := Vector3(0, 0, 1)
	# 1.43m eye-to-foot offset, same capsule as Player.tscn (radius
	# 0.18, height 1.45, collision shape offset -0.705 -> feet sit
	# 1.43m "down" from the body origin).
	return Transform3D(Basis.looking_at(forward, up_dir), floor_pos + up_dir * 1.43)

func _spawn_player() -> void:
	player = STATION_PLAYER_SCENE.instantiate() as StationPlayer
	# Set the transform BEFORE add_child(): add_child() runs the
	# player's _ready() synchronously (station is already inside the
	# tree), and StationPlayer.gd's _ready() captures spawn_transform
	# from whatever global_transform is at that point -- if that
	# happened before this assignment, spawn_transform would freeze at
	# the instantiate()-time default (world origin, which also happens
	# to be the ring's central axis, the one position this map's radial
	# gravity is exactly zero at), and respawn-on-death would strand the
	# player there with broken orientation/gravity instead of putting
	# them back on the floor.
	player.global_transform = _floor_spawn_transform()
	add_child(player)

## Live-tuning entry point -- see the file-level comment for the
## gcmd.py incantation. Applies any provided overrides, tears down and
## regenerates the ring geometry/collision, and puts the player back on
## the (possibly relocated) floor. Player weapons/health/faction are
## untouched since the player node itself isn't recreated.
func rebuild_ring(overrides: Dictionary = {}) -> void:
	if overrides.has("target_g"):
		TARGET_G = overrides["target_g"]
	if overrides.has("radius"):
		RADIUS = overrides["radius"]
	if overrides.has("gravity_bands"):
		GRAVITY_BANDS = overrides["gravity_bands"]
	if overrides.has("ceiling_height"):
		CEILING_HEIGHT = overrides["ceiling_height"]
	if overrides.has("width"):
		WIDTH = overrides["width"]
	if overrides.has("segments"):
		SEGMENTS = overrides["segments"]

	# Immediate free(), not queue_free(): this runs outside physics/
	# signal reentrancy (a direct gcmd/script call), and _build_ring()
	# below needs RingMesh's old name free right away, not next frame.
	for child in ring_body.get_children():
		child.free()
	_build_ring()

	if player:
		player.global_transform = _floor_spawn_transform()
		player.spawn_transform = player.global_transform
		player.velocity = Vector3.ZERO
		# StationPlayer's _physics_process co-rotates the body from last
		# frame's "up" -- after this teleport that's stale (see the
		# matching comment on _on_died() in StationPlayer.gd), so reseed
		# it instead of slamming a huge spurious rotation onto the fresh
		# spawn.
		player._prev_up_valid = false
