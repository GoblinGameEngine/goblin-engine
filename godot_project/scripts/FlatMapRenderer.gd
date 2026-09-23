extends Node3D

# STATUS: UNFINISHED, never produced an image. On the Intel Haswell
# (HD 4400) test machine every attempt either segfaulted in the Mesa
# Vulkan driver or ballooned to ~7GB RAM -- the last one locked up and
# rebooted the whole machine. Map image deferred; if retried, run it
# under a hard memory cap first, e.g.
#   systemd-run --user --scope -p MemoryMax=3G -p MemorySwapMax=0 godot4 ...
# The ToonShading material cache added since may well have been the fix
# for the RAM blowup (it was 2.8GB+ in the live game too) -- untested here.
#
# One-shot batch job: builds a flat, "rolled out" copy of the whole
# station using the SAME generation code the live game uses (just with
# RingCoords.FLAT_MODE=true, which unrolls the ring into a plane instead
# of wrapping it around the cylinder -- see that var's own doc comment),
# frames it with a big top-down orthographic camera, and saves a PNG.
# "make a copy and roll it out flat with all the assets rendered. Take
# a picture of it and use it as a map I will evaluate... we will then
# use this map in-game for various things so make sure it's a high
# resolution image."
#
# Launch as its own dedicated process (this never runs inside the actual
# playable game -- FLAT_MODE/SKIP_COLLISION are global static vars, and
# toggling them live would be a real risk otherwise; see RingCoords.gd's
# own comments):
#   godot4 --path godot_project scenes/FlatMapRenderer.tscn
#
# Renders straight into the MAIN window's own already-initialized
# viewport, at whatever size the window already is -- no resize, no new
# SubViewport. Both of those were tried first and BOTH reproducibly
# crashed this test machine's GPU driver (Intel Haswell, "incomplete
# Vulkan support" per its own boot warning), independent of target size
# (~4056x4240, ~1716x1793, and ~1024x1077 all crashed identically,
# which ruled out "too large" as the cause) -- so the actual trigger
# looks like creating/resizing a render target at runtime on this
# driver at all, not size. The one render path proven reliable all
# session on this exact machine is gcmd.py's own `screenshot` command,
# which reads the main viewport's texture at its default, engine-
# initialized-at-startup size and has never once crashed -- so this
# does the same thing instead of fighting the driver further. This
# means the final image is capped at this project's default window
# resolution rather than a genuinely custom "high resolution" size --
# a real, test-machine-specific limitation, flagged honestly rather
# than claiming a resolution this box can't actually produce. Real
# target hardware, with a real Vulkan/GPU driver, should have no
# trouble with a much larger SubViewport-based capture -- the code
# path for that (tried first, see above) is sound, just not usable on
# this specific box.
#
# Skips StationRingBuilder.build()'s ceiling/walls entirely (built in
# real, non-flat 3D space -- see StationRingBuilder.build_floor_surface()'s
# own doc comment for why this calls that directly instead) -- only the
# floor + everything built on it (settlements, river/lake/ponds/creeks,
# farmland) is part of the map.

const OUTPUT_PATH := "/home/nelahi/goblin-engine/station_map.png"
const MARGIN := 60.0  # meters of border around the map's true extent

func _ready() -> void:
	print("FlatMapRenderer: starting -- this will take a while (same generation work as a live boot, done synchronously).")
	RingCoords.FLAT_MODE = true
	# No gameplay in this one-shot render -- skipping collision generation
	# (RingCoords.add_trimesh_collision(), called once per storefront
	# across all 9 settlements) was a real, measured fix for an earlier
	# attempt ballooning to 7GB+ RSS and forcing this whole machine into
	# swap thrashing.
	RingCoords.SKIP_COLLISION = true

	var radius: float = SpaceStation.RADIUS
	var segments: int = SpaceStation.SEGMENTS
	var width: float = SpaceStation.WIDTH
	var circumference := TAU * radius

	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_texture = load("res://assets/textures/grass_tinted.png")
	var mesh := ArrayMesh.new()
	TerrainHeight.RING_WIDTH = width
	StationRingBuilder.build_floor_surface(mesh, radius, segments, width * 0.5, floor_mat)
	var floor_instance := MeshInstance3D.new()
	floor_instance.name = "FlatFloor"
	floor_instance.mesh = mesh
	add_child(floor_instance)

	NeighborhoodGenerator.build_skeleton(self, radius, segments, width)
	await NeighborhoodGenerator.build_detail_async(self, radius, segments, width)
	RiverGenerator.build(self, radius, segments)

	print("FlatMapRenderer: world built, framing camera (ToonShading already ran once inside build_detail_async -- not re-run here)...")

	_setup_lighting()
	_capture(width, circumference)

func _setup_lighting() -> void:
	var env_node := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.5, 0.7, 0.95)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.85, 0.88, 0.95)
	env.ambient_light_energy = 1.1
	env_node.environment = env
	add_child(env_node)

	# Angled, not straight down -- so bluffs/banks cast real, readable
	# shadows (a relief-map read), not a flat shadowless wash.
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, 35, 0)
	sun.light_energy = 1.4
	sun.light_color = Color(1.0, 0.98, 0.92)
	sun.shadow_enabled = true
	add_child(sun)

func _capture(width: float, circumference: float) -> void:
	var half_w := width * 0.5 + MARGIN
	var half_len := circumference * 0.5 + MARGIN
	var center_z := circumference * 0.5

	var vp_size: Vector2i = get_viewport().size  # default window size -- deliberately NOT resized, see this file's header
	var vp_aspect := float(vp_size.x) / float(vp_size.y)
	var map_aspect := half_w / half_len

	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.far = 5000.0
	cam.global_position = Vector3(0.0, 400.0, center_z)
	cam.rotation_degrees = Vector3(-90, 0, 0)
	if vp_aspect >= map_aspect:
		# Viewport is proportionally wider than the map -- height is the
		# tight dimension, so fit the map's full length and accept side
		# padding rather than cropping anything off the top/bottom.
		cam.keep_aspect = Camera3D.KEEP_HEIGHT
		cam.size = half_len * 2.0
	else:
		cam.keep_aspect = Camera3D.KEEP_WIDTH
		cam.size = half_w * 2.0
	add_child(cam)
	cam.current = true

	print("FlatMapRenderer: capturing at the default window size %dx%d px (map extent %.0fm x %.0fm)..." % [vp_size.x, vp_size.y, half_w * 2.0, half_len * 2.0])
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw

	var img := get_viewport().get_texture().get_image()
	var err := img.save_png(OUTPUT_PATH)
	if err != OK:
		print("FlatMapRenderer: FAILED to save PNG, error code %d" % err)
	else:
		print("FlatMapRenderer: saved %s (%dx%d)" % [OUTPUT_PATH, img.get_width(), img.get_height()])
	get_tree().quit()
