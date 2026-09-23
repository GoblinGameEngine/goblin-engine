extends Node
class_name LakeGenerator

# Lake/beach zone roads: a loop road that circles the lake (a road along
# each shore, joined by a curved cap at each end of the zone, forming one
# continuous loop) plus spoke side streets that branch off the loop at
# intervals, curving out toward the zone's outer width edge -- curved
# like ResidentialGenerator.gd's paths, but LESS curved (a lower
# `curviness`), per spec.
#
# The lake body itself (water/sand/shore geometry) is a later phase --
# this only lays down the road skeleton, using the same assumed lake
# footprint (centered in the zone's width, LAKE_HALF_WIDTH either side)
# that the eventual water geometry will use, so the roads end up
# correctly placed just outside the shoreline once the lake is built.
#
# Real-world feet-derived meters, no compression (see DowntownGenerator.gd).

const FT := 0.3048

const LAKE_HALF_WIDTH := 65.0          # assumed water extent either side of zone-width center
const SHORE_GAP := 12.0                # shoreline to ring-road gap
const RING_ROAD_WIDTH := 34.0 * FT
const SIDEWALK_WIDTH := 5.0 * FT
const SPOKE_WIDTH := 24.0 * FT         # narrower than the ring road -- these are minor side streets
const SPOKE_LENGTH := 30.0             # meters, how far a spoke extends outward from the ring road
const SPOKE_CURVINESS := 0.4           # gentler curve than ResidentialGenerator's 1.0
const N_SPOKES_PER_SIDE := 5
const END_CAP_LEN := 40.0              # arc length each rounded end-cap connector uses

const UV_TILE := 8.0

## Shallow "forced-perspective" water depth (reference/memory.txt's
## documented shore trick): the shared ring floor (built once, whole-ring,
## by StationRingBuilder with no zone awareness) is reused as-is for the
## lake bed rather than carving a real basin into it -- an opaque water
## plane sitting this far above the ordinary floor reads as a real lake
## from outside while staying fully walkable/swimmable underneath.
const WATER_HEIGHT := 1.8
const WATER_TRIGGER_MARGIN := 0.6  # extra headroom above the surface the swim volume still counts as "in water"
const UV_TILE_WATER := 12.0

static func build_roads(parent: Node3D, radius: float, segments: int,
		s_start: float, s_end: float, width: float) -> Dictionary:
	var mesh := ArrayMesh.new()

	var road_mat := StandardMaterial3D.new()
	road_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var sidewalk_mat := StandardMaterial3D.new()
	sidewalk_mat.albedo_texture = load("res://assets/textures/sidewalk_tinted_0.png")

	var st_road := SurfaceTool.new()
	st_road.begin(Mesh.PRIMITIVE_TRIANGLES)
	var st_sidewalk := SurfaceTool.new()
	st_sidewalk.begin(Mesh.PRIMITIVE_TRIANGLES)

	var x_left := -(LAKE_HALF_WIDTH + SHORE_GAP)
	var x_right := LAKE_HALF_WIDTH + SHORE_GAP

	var straight_s0 := s_start + END_CAP_LEN
	var straight_s1 := s_end - END_CAP_LEN

	# The two shore roads, plus the rounded end caps joining them into
	# one loop -- caps built with the strip builder's own diagonal-lerp
	# (x_start != x_end across a short s span) rather than a hard
	# perpendicular jog, so the loop's ends read as rounded, not square.
	StreetBuilder.build_tangential_strip(st_road, radius, segments, straight_s0, straight_s1, x_left, x_left, RING_ROAD_WIDTH, UV_TILE)
	StreetBuilder.build_tangential_strip(st_road, radius, segments, straight_s0, straight_s1, x_right, x_right, RING_ROAD_WIDTH, UV_TILE)
	StreetBuilder.build_curved_strip(st_road, radius, segments, s_start, straight_s0, x_left, x_right, RING_ROAD_WIDTH, UV_TILE, 1.0)
	StreetBuilder.build_curved_strip(st_road, radius, segments, straight_s1, s_end, x_right, x_left, RING_ROAD_WIDTH, UV_TILE, 1.0)

	var ring_hw := RING_ROAD_WIDTH * 0.5
	var sidewalk_gap := ring_hw + SIDEWALK_WIDTH * 0.5
	for x in [x_left, x_right]:
		StreetBuilder.build_tangential_strip(st_sidewalk, radius, segments, straight_s0, straight_s1,
			x - sidewalk_gap, x - sidewalk_gap, SIDEWALK_WIDTH, UV_TILE)
		StreetBuilder.build_tangential_strip(st_sidewalk, radius, segments, straight_s0, straight_s1,
			x + sidewalk_gap, x + sidewalk_gap, SIDEWALK_WIDTH, UV_TILE)

	# Spokes: short curved spurs off each shore road, heading outward
	# (away from the lake) toward the zone's outer width edge.
	var half_width_margin := width * 0.5 - 10.0
	var spoke_span := straight_s1 - straight_s0
	for i in range(N_SPOKES_PER_SIDE):
		var t := (float(i) + 0.5) / float(N_SPOKES_PER_SIDE)
		var s_spoke := straight_s0 + spoke_span * t
		var left_out := maxf(-half_width_margin, x_left - SPOKE_LENGTH)
		var right_out := minf(half_width_margin, x_right + SPOKE_LENGTH)
		var wp_left := [Vector2(s_spoke, x_left), Vector2(s_spoke, left_out)]
		var wp_right := [Vector2(s_spoke, x_right), Vector2(s_spoke, right_out)]
		StreetBuilder.build_curved_road(st_road, radius, segments, wp_left, SPOKE_WIDTH, UV_TILE, SPOKE_CURVINESS)
		StreetBuilder.build_curved_road(st_road, radius, segments, wp_right, SPOKE_WIDTH, UV_TILE, SPOKE_CURVINESS)
		StreetBuilder.place_stop_sign(parent, radius, segments, s_spoke, x_left - ring_hw - 1.0)
		StreetBuilder.place_stop_sign(parent, radius, segments, s_spoke, x_right + ring_hw + 1.0)

	st_road.set_material(road_mat)
	st_road.commit(mesh)
	st_sidewalk.set_material(sidewalk_mat)
	st_sidewalk.commit(mesh)

	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "LakeRoads"  # no "structure" keyword -- see DowntownGenerator.gd's note
	mesh_instance.mesh = mesh
	parent.add_child(mesh_instance)

	# The loop's own end caps already close it within [s_start, s_end],
	# so unlike the other zones this one doesn't hand off a through-road
	# at its boundaries -- entry/exit are empty, meaning
	# NeighborhoodGenerator.gd's inter-zone connectors have nothing of
	# this zone's own to hook into at the seams (the loop is a closed
	# shape, on purpose).
	return {"entry_x": [], "exit_x": []}

## No streamed BUILDING/prop detail exists yet for this zone (docks,
## fishing shacks, etc. would go here later) -- the water itself is
## intentionally NOT built here; see build_water() below and its call
## site's comment for why. Kept as a real (if empty) async function so
## ZoneStreamer.gd can call every zone's build_detail_async() uniformly
## instead of special-casing the lake.
static func build_detail_async(_parent: Node3D, _radius: float, _segments: int, _width: float) -> void:
	await RingCoords.yield_frame()

## Builds the lake's water surface + swimmable volume. Called once from
## NeighborhoodGenerator.build_skeleton() (NOT from build_detail_async
## above) -- water is a permanent landmark like the roads, not streamed
## buildings/crops the player has to walk up to first; see that call
## site's own comment. Water plane sits a shallow WATER_HEIGHT above the
## ordinary shared floor (see the constant's own comment) and tapers to
## 0 width at both ends of [s_start, s_end] over END_CAP_LEN, echoing the
## road loop's own rounded end caps.
static func build_water(root: Node3D, radius: float, segments: int, s_start: float, s_end: float) -> void:
	var straight_s0 := s_start + END_CAP_LEN
	var straight_s1 := s_end - END_CAP_LEN

	var water_mat := StandardMaterial3D.new()
	water_mat.albedo_texture = load("res://assets/textures/water_tinted_0.png")
	water_mat.cull_mode = BaseMaterial3D.CULL_DISABLED  # visible from below while submerged, not just from above
	water_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water_mat.albedo_color = Color(1.0, 1.0, 1.0, 0.92)

	var st_water := SurfaceTool.new()
	st_water.begin(Mesh.PRIMITIVE_TRIANGLES)

	var water_volume := Area3D.new()
	water_volume.name = "LakeWaterVolume"
	water_volume.set_script(load("res://scripts/world/WaterVolume.gd"))
	root.add_child(water_volume)

	var seg_arc := (TAU / segments) * radius
	var i0 := int(floor(s_start / seg_arc))
	var i1 := int(ceil(s_end / seg_arc))
	for i in range(i0, i1):
		var seg_s0: float = max(s_start, float(i) * seg_arc)
		var seg_s1: float = min(s_end, float(i + 1) * seg_arc)
		if seg_s1 <= seg_s0:
			continue
		var hw_a := _lake_half_width(seg_s0, s_start, s_end, straight_s0, straight_s1)
		var hw_b := _lake_half_width(seg_s1, s_start, s_end, straight_s0, straight_s1)
		if hw_a <= 0.1 and hw_b <= 0.1:
			continue
		var mid_s := (seg_s0 + seg_s1) * 0.5
		var up := RingCoords.floor_basis(radius, segments, mid_s).y
		var offset := up * WATER_HEIGHT
		var p0 := RingCoords.floor_point(radius, segments, seg_s0, -hw_a) + offset
		var p1 := RingCoords.floor_point(radius, segments, seg_s0, hw_a) + offset
		var p2 := RingCoords.floor_point(radius, segments, seg_s1, hw_b) + offset
		var p3 := RingCoords.floor_point(radius, segments, seg_s1, -hw_b) + offset
		var v0 := seg_s0 / UV_TILE_WATER
		var v1 := seg_s1 / UV_TILE_WATER
		StationRingBuilder._quad(st_water, p0, p1, p2, p3, up,
			Vector2(-hw_a / UV_TILE_WATER, v0), Vector2(hw_a / UV_TILE_WATER, v0),
			Vector2(hw_b / UV_TILE_WATER, v1), Vector2(-hw_b / UV_TILE_WATER, v1))

		var box_hw: float = max(hw_a, hw_b)
		if box_hw > 0.1:
			_add_water_trigger_box(water_volume, radius, segments, mid_s, seg_s1 - seg_s0, box_hw)

	st_water.set_material(water_mat)
	var water_mesh := ArrayMesh.new()
	st_water.commit(water_mesh)
	var water_instance := MeshInstance3D.new()
	water_instance.name = "lake_water_surface"  # LakeSetup._find() matches this prefix
	water_instance.mesh = water_mesh
	root.add_child(water_instance)

	LakeSetup.setup(root)  # attaches LakeWater.gd's cosmetic UV-scroll to the mesh just built above

## Half-width of the water polygon at arc length `s`: full LAKE_HALF_WIDTH
## in the straight middle section, smoothstepped down to 0 over the last
## END_CAP_LEN at each end so the lake reads as a rounded oval rather than
## a sharp-cornered rectangle.
static func _lake_half_width(s: float, s_start: float, s_end: float, straight_s0: float, straight_s1: float) -> float:
	if s < straight_s0:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clamp((s - s_start) / (straight_s0 - s_start), 0.0, 1.0))
	if s > straight_s1:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clamp((s_end - s) / (s_end - straight_s1), 0.0, 1.0))
	return LAKE_HALF_WIDTH

## One convex swim-trigger box for one ring segment's worth of lake,
## spanning from the shared floor up through WATER_TRIGGER_MARGIN above
## the water surface. `chord` and `half_width` bound the box's footprint;
## `radius`/`segments`/`mid_s` place and orient it via the same flat-quad
## floor math everything else on the ring uses (RingCoords), so it never
## floats off the real segment the way an idealized-circle placement would.
static func _add_water_trigger_box(parent: Node3D, radius: float, segments: int,
		mid_s: float, chord: float, half_width: float) -> void:
	var basis := RingCoords.floor_basis(radius, segments, mid_s)
	var col_h := WATER_HEIGHT + WATER_TRIGGER_MARGIN
	var center := RingCoords.floor_point(radius, segments, mid_s, 0.0) + basis.y * (col_h * 0.5)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(half_width * 2.0, col_h, chord * 1.08)
	cs.shape = box
	cs.transform = Transform3D(basis, center)
	parent.add_child(cs)
