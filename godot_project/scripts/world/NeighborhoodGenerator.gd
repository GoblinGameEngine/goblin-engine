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
# Phase A scope: zone range math + street skeletons for all 4 zones,
# stitched at the seams. Buildings, the lake's own water/sand geometry,
# and crops are later phases (see the plan file) -- their generator
# calls get added here as each phase lands, following the same pattern.

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

static func build(root: Node3D, radius: float, ceiling_height: float, width: float, segments: int) -> void:
	var zones := zone_ranges(radius, segments)

	# ~33m at default scale -- both the no-build margin each zone's own
	# generator gets trimmed by, AND (now) the span the connector roads
	# built below get to bridge each seam.
	var buffer := (TAU / segments) * radius

	var lake: Dictionary = zones[0]
	var lake_result := LakeGenerator.build(root, radius, segments,
		lake["s_start"] + buffer, lake["s_end"] - buffer, width)

	var downtown: Dictionary = zones[1]
	var downtown_result := DowntownGenerator.build(root, radius, segments,
		downtown["s_start"] + buffer, downtown["s_end"] - buffer, width)

	var residential: Dictionary = zones[2]
	var residential_result := ResidentialGenerator.build(root, radius, segments,
		residential["s_start"] + buffer, residential["s_end"] - buffer, width)

	var farm: Dictionary = zones[3]
	var farm_result := FarmGenerator.build(root, radius, segments,
		farm["s_start"] + buffer, farm["s_end"] - buffer, width)

	var results := [lake_result, downtown_result, residential_result, farm_result]
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
		if _connect_zone_pair(st_connect, radius, segments, results[i]["exit_x"], results[(i + 1) % 4]["entry_x"], exit_s, entry_s):
			any_connectors = true
	if any_connectors:
		st_connect.set_material(connector_mat)
		var connector_mesh := ArrayMesh.new()
		st_connect.commit(connector_mesh)
		var connector_instance := MeshInstance3D.new()
		connector_instance.name = "ZoneConnectors"
		connector_instance.mesh = connector_mesh
		root.add_child(connector_instance)

	# OcclusionSetup/LakeSetup/DistanceCulling still land in the LOD pass
	# (Phase E, see the plan file). SceneryOptimizer runs here now, though
	# (Phase D): CropFieldGenerator.gd's corn_*/soy_* stalks (placed
	# inside FarmGenerator.build() above) need to actually get grouped
	# into MultiMeshInstance3D nodes to be worth having built the batching
	# system for at all -- Main.gd's flat-map pipeline calls
	# SceneryOptimizer.optimize() for exactly this reason, but nothing
	# equivalent existed on the station-ring path (SpaceStation.gd calls
	# this function, not Main.gd) until now. Must run BEFORE ToonShading,
	# same order Main.gd already uses: apply_to_world() below has to see
	# the final MultiMeshInstance3D nodes to toon-shade (and billboard-
	# flag) them, not the pre-batching individual MeshInstance3D stalks
	# it would replace and then have collapsed out from under it.
	var opt := SceneryOptimizer.optimize(root)
	print("NeighborhoodGenerator: scenery optimize -- %d decorative meshes, collapsed %d into %d MultiMeshInstance3D" %
		[opt["decor_total"], opt["collapsed"], opt["multimeshes"]])

	# ToonShading needs to run after the above, not deferred to Phase E:
	# confirmed live that a freshly built StandardMaterial3D mesh here is
	# backface-culled under its own default cull_back mode from every
	# angle a player would actually view a street from (the same _quad()/
	# normal convention StationRingBuilder's own floor already uses --
	# that one only ever renders correctly because SpaceStation.
	# _build_ring() toon-shades it, with toon.gdshader's render_mode
	# cull_disabled, before a player ever sees a frame of it). Re-running
	# this per phase as more content is added is idempotent and cheap --
	# ToonShading.apply_to_world() just walks whatever's under `root`
	# each time.
	ToonShading.apply_to_world(root)

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
