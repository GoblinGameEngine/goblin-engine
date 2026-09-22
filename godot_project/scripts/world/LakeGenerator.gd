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

## No detail content exists yet for this zone (the lake's own water/sand/
## shore geometry was never built -- see this file's own header comment
## and reference/memory.txt) -- a real gap from earlier phases, not
## something ZoneStreamer.gd's arrival changes. Kept as a real (if empty)
## async function so ZoneStreamer.gd can call every zone's
## build_detail_async() uniformly instead of special-casing the lake.
static func build_detail_async(_parent: Node3D, _radius: float, _segments: int, _width: float) -> void:
	await RingCoords.yield_frame()
