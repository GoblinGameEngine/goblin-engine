extends Node
class_name NeighborhoodGenerator

# Top-level orchestrator for the procedural Midwestern neighborhood built
# onto the station ring's floor. Splits the ring's circumference into 4
# equal zones -- lake/beach, downtown, residential, farm, in that order
# going around (downtown adjacent to the lake on the waterfront side,
# farm touching the lake's far/undeveloped shore, residential directly
# opposite the lake) -- and calls each zone's generator in turn. Each
# zone generator lays out its OWN, deliberately different road topology
# (see the zone scripts) -- this orchestrator's other job is stitching
# them together: the buffer gap at each zone seam isn't just a no-build
# margin any more, it's where a short connector road links whichever
# roads reach one zone's edge to whichever roads start the next zone's
# (see _connect_zones() below).
#
# STREAMING (requested directly: "do we need to keep so much of the ring
# in memory... a background pre-loading system that loads the next
# section as we need it... only rendering in detail what's close to the
# player"): split into build_skeleton() -- roads/sidewalks/stop signs for
# ALL 4 zones, built once at boot, cheap (a handful of committed meshes,
# no per-building node/collision overhead) -- and
# load_zone_detail_async()/ZoneStreamer.gd's unload -- buildings, crop
# fields, and street furniture, which dominate both node count and
# collision-generation cost, built/freed per zone as the player
# approaches/leaves (ZoneStreamer.gd drives this from the player's own
# arc-length position). The always-on road skeleton doubles as exactly
# the "distant low-poly representation" asked for: from far away (or
# before a zone has streamed in) you see the street layout, which is
# already about as cheap as geometry gets, while the expensive detail
# only ever exists near the player.

const ZONE_NAMES := ["lake", "downtown", "residential", "farm"]

## Segment/arc-length/angle bounds for each of the 4 zones. Assumes
## `segments` divides evenly by 4 (true for SpaceStation's default 96);
## an uneven remainder would just make the last zone a few segments
## larger, which is harmless but not what this returns today.
static func zone_ranges(radius: float, segments: int) -> Array[Dictionary]:
	var zone_segments := segments / 4
	var seg_arc := (TAU / segments) * radius
	var zones: Array[Dictionary] = []
	for i in range(4):
		var seg_start := i * zone_segments
		var seg_end := seg_start + zone_segments
		zones.append({
			"name": ZONE_NAMES[i],
			"seg_start": seg_start,
			"seg_end": seg_end,
			"s_start": float(seg_start) * seg_arc,
			"s_end": float(seg_end) * seg_arc,
			"angle_start": float(seg_start) * (TAU / segments),
			"angle_end": float(seg_end) * (TAU / segments),
		})
	return zones

## Builds every zone's road/sidewalk/stop-sign skeleton (the always-on
## part) and the connector roads bridging each zone seam. Returns one
## info Dictionary per zone (s_start/s_end/width plus whatever that
## zone's own build_roads() returned under "roads") -- ZoneStreamer.gd
## keeps this array and hands entries back to load_zone_detail_async()
## when a zone needs to stream in, so the detail phase never has to
## recompute anything the roads phase already worked out (waypoints,
## street positions, connector arc-length positions).
static func build_skeleton(root: Node3D, radius: float, segments: int, width: float) -> Array:
	var zones := zone_ranges(radius, segments)

	# ~33m at default scale -- both the no-build margin each zone's own
	# generator gets trimmed by, AND the span the connector roads built
	# below get to bridge each seam.
	var buffer := (TAU / segments) * radius

	var zone_info: Array = []

	var lake: Dictionary = zones[0]
	var lake_s0: float = lake["s_start"] + buffer
	var lake_s1: float = lake["s_end"] - buffer
	var lake_roads := LakeGenerator.build_roads(root, radius, segments, lake_s0, lake_s1, width)
	zone_info.append({"name": "lake", "s_start": lake_s0, "s_end": lake_s1, "width": width, "roads": lake_roads})

	var downtown: Dictionary = zones[1]
	var downtown_s0: float = downtown["s_start"] + buffer
	var downtown_s1: float = downtown["s_end"] - buffer
	var downtown_roads := DowntownGenerator.build_roads(root, radius, segments, downtown_s0, downtown_s1, width)
	zone_info.append({"name": "downtown", "s_start": downtown_s0, "s_end": downtown_s1, "width": width, "roads": downtown_roads})

	var residential: Dictionary = zones[2]
	var residential_s0: float = residential["s_start"] + buffer
	var residential_s1: float = residential["s_end"] - buffer
	var residential_roads := ResidentialGenerator.build_roads(root, radius, segments, residential_s0, residential_s1, width)
	zone_info.append({"name": "residential", "s_start": residential_s0, "s_end": residential_s1, "width": width, "roads": residential_roads})

	var farm: Dictionary = zones[3]
	var farm_s0: float = farm["s_start"] + buffer
	var farm_s1: float = farm["s_end"] - buffer
	var farm_roads := FarmGenerator.build_roads(root, radius, segments, farm_s0, farm_s1, width)
	zone_info.append({"name": "farm", "s_start": farm_s0, "s_end": farm_s1, "width": width, "roads": farm_roads})

	var connector_mat := StandardMaterial3D.new()
	connector_mat.albedo_texture = load("res://assets/textures/road_tinted.png")
	var st_connect := SurfaceTool.new()
	st_connect.begin(Mesh.PRIMITIVE_TRIANGLES)
	var any_connectors := false
	for i in range(4):
		var this_zone: Dictionary = zones[i]
		var next_zone: Dictionary = zones[(i + 1) % 4]
		var exit_s: float = this_zone["s_end"] - buffer
		var entry_s: float = next_zone["s_start"] + buffer
		if next_zone["s_start"] < this_zone["s_start"]:
			# The farm->lake seam wraps past the TAU origin -- push
			# entry_s one full lap ahead so it's still numerically after
			# exit_s; RingCoords.floor_point/floor_basis wrap any s via
			# fposmod internally, so a value past TAU*radius still lands
			# in the right physical spot.
			entry_s += TAU * radius
		var exit_x: Array = zone_info[i]["roads"]["exit_x"]
		var entry_x: Array = zone_info[(i + 1) % 4]["roads"]["entry_x"]
		if _connect_zone_pair(st_connect, radius, segments, exit_x, entry_x, exit_s, entry_s):
			any_connectors = true
	if any_connectors:
		st_connect.set_material(connector_mat)
		var connector_mesh := ArrayMesh.new()
		st_connect.commit(connector_mesh)
		var connector_instance := MeshInstance3D.new()
		connector_instance.name = "ZoneConnectors"
		connector_instance.mesh = connector_mesh
		root.add_child(connector_instance)

	# No-op today: the lake zone's water/sand/shore geometry itself was
	# never built (see LakeGenerator.gd's own comment) -- a real gap left
	# from earlier phases. Scoped to the skeleton, not per-zone-detail:
	# water/terrain belongs with the always-on roads, not the streamed
	# buildings/crops, once it exists.
	LakeSetup.setup(root)

	# Backface-culling fix, same reasoning as before: a freshly built
	# StandardMaterial3D mesh here is backface-culled under cull_back
	# from every angle a player would view a street from, and this has
	# to run before a player ever sees a frame of it. Scoped to `root`
	# at THIS point in time -- zone detail hasn't streamed in yet, so
	# this only ever walks the (cheap) skeleton; each zone's own detail
	# gets its own ToonShading pass in load_zone_detail_async() below.
	ToonShading.apply_to_world(root)

	return zone_info

## Streams one zone's buildings/crop-fields/street-furniture in, as a
## fresh child of `root` (so ZoneStreamer.gd can just queue_free() that
## one node to unload it later -- no need to track which of `root`'s
## other children belong to which zone). `info` must be one of
## build_skeleton()'s own returned entries for this `zone_index`
## (0=lake, 1=downtown, 2=residential, 3=farm -- matches ZONE_NAMES).
## Time-sliced (every generator's build_detail_async() awaits
## RingCoords.yield_frame() periodically) -- callers should NOT await
## this synchronously if the goal is a hitch-free stream-in; ZoneStreamer.
## gd fires it and lets it run in the background.
static func load_zone_detail_async(root: Node3D, radius: float, segments: int,
		zone_index: int, info: Dictionary) -> Node3D:
	var detail_root := Node3D.new()
	detail_root.name = "ZoneDetail_%s" % info["name"]
	root.add_child(detail_root)

	var roads: Dictionary = info["roads"]
	match zone_index:
		0:
			await LakeGenerator.build_detail_async(detail_root, radius, segments, info["width"])
		1:
			await DowntownGenerator.build_detail_async(detail_root, radius, segments,
				info["s_start"], info["s_end"], roads["street_x"], 0.0)
		2:
			await ResidentialGenerator.build_detail_async(detail_root, radius, segments,
				roads["wp_a"], roads["wp_b"])
		3:
			await FarmGenerator.build_detail_async(detail_root, radius, segments,
				info["s_start"], info["s_end"], info["width"], roads["connector_s"])

	if not is_instance_valid(detail_root):
		# ZoneStreamer.gd unloaded this zone again while the above was
		# still streaming in (player doubled back) -- nothing left to
		# post-process.
		return null

	var opt := SceneryOptimizer.optimize(detail_root)
	OcclusionSetup.setup(detail_root)
	DistanceCulling.apply_to_world(detail_root, Settings.draw_distance_mult)
	var toon_count := ToonShading.apply_to_world(detail_root)
	print("NeighborhoodGenerator: streamed in %s detail -- %d decor collapsed into %d multimesh, %d materials toon-shaded" %
		[info["name"], opt["decor_total"], opt["multimeshes"], toon_count])
	return detail_root

## Bridges one zone seam: for every x in `exit_x` (roads leaving the
## first zone), finds the nearest x in `entry_x` (roads starting the
## next zone) and builds a curved connector strip between them across
## the buffer span. Different zone topologies hand back different
## counts of boundary roads (downtown's grid: 5; residential's curving
## paths: 2; the lake loop: 0, since it's a closed shape with nothing to
## hand off), so this is deliberately many-to-one rather than requiring
## equal counts or a 1:1 pairing. Returns true if anything was built.
static func _connect_zone_pair(st: SurfaceTool, radius: float, segments: int,
		exit_x: Array, entry_x: Array, exit_s: float, entry_s: float) -> bool:
	if exit_x.is_empty() or entry_x.is_empty():
		return false
	const CONNECTOR_WIDTH := 8.0  # generic connector width -- a modest local-road scale
	for x0 in exit_x:
		var best: float = entry_x[0]
		var best_dist: float = absf(entry_x[0] - x0)
		for x1 in entry_x:
			var d: float = absf(x1 - x0)
			if d < best_dist:
				best_dist = d
				best = x1
		StreetBuilder.build_curved_strip(st, radius, segments, exit_s, entry_s, x0, best, CONNECTOR_WIDTH, 8.0, 1.0)
	return true
