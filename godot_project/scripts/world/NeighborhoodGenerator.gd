extends Node
class_name NeighborhoodGenerator

# Top-level orchestrator for everything built onto the station ring's
# floor. Replaces the old fixed 4-zone (Lake/Downtown/Residential/Farm
# quarter) system entirely: "We are completely abandoning my rules
# about the commercial residential agricultural and lake zones.
# Communities will be laid out and spaced according to your research,
# not my rules. We need two cities, four towns and three villages with
# farmland in between." SettlementLayout.gd owns the actual 9-settlement
# arrangement (arc bounds, tier config); this file just walks it.
#
# Split into build_skeleton() (roads only -- cheap, synchronous, meant
# to stay resident for the whole ring's lifetime) and build_detail_async()
# (buildings + crop fields -- the expensive part, RingCoords.
# add_trimesh_collision() per storefront foremost among it) exactly
# like the old 4-zone system's own build_skeleton()/load_zone_detail_
# async() split, for the same reason: building all 9 settlements'
# buildings synchronously in one call was measured live to block the
# main thread for minutes. The difference from the old system is
# streaming ALL 9 settlements' detail once at boot (fire-and-forget,
# not awaited -- see SpaceStation.gd's own call site) rather than
# per-zone proximity streaming via ZoneStreamer.gd -- 9 much smaller
# settlements keep the total building count comparable to or smaller
# than the old 4 large zones, so a simpler "stream everything in once"
# pass was enough; a follow-up could reintroduce proximity-based
# load/unload if a later density increase makes it worth it.

static func build_skeleton(root: Node3D, radius: float, segments: int, width: float) -> void:
	var layout := SettlementLayout.build_layout(radius)

	for entry in layout:
		SettlementGenerator.build_roads(root, radius, segments, entry)

	LakeGenerator.build_water(root, radius, segments,
		TerrainHeight.lake_center_s(radius) - TerrainHeight.LAKE_HALF_SPAN,
		TerrainHeight.lake_center_s(radius) + TerrainHeight.LAKE_HALF_SPAN)

	# The full ring-spanning river/ponds/creeks is built by SpaceStation
	# itself right after this function returns, NOT here -- RiverGenerator
	# calls back into SettlementLayout for its bridge placement, and
	# GDScript's class_name resolution can't handle two scripts calling
	# each other's static functions (confirmed empirically, not just a
	# style preference) -- see TerrainHeight.gd's header for the fuller
	# explanation of this project's dependency-direction rule.

	# Backface-culling fix, same reasoning as before: a freshly built
	# StandardMaterial3D mesh here is backface-culled under cull_back
	# from every angle a player would view a street from, and this has
	# to run before a player ever sees a frame of it. Scoped to `root`
	# at THIS point in time -- detail hasn't streamed in yet, so this
	# only ever walks the (cheap) skeleton; build_detail_async() below
	# runs its own pass afterward for the buildings/crops it adds.
	ToonShading.apply_to_world(root)

## Buildings (all 9 settlements) + crop fields -- the expensive,
## streamed part. Callers should NOT await this synchronously if the
## goal is a hitch-free boot; SpaceStation.gd fires it and lets it run
## in the background across many frames.
static func build_detail_async(root: Node3D, radius: float, segments: int, width: float) -> void:
	var layout := SettlementLayout.build_layout(radius)
	for entry in layout:
		await SettlementGenerator.build_buildings_async(root, radius, segments, entry)
	await _build_farmland_async(root, radius, segments, width, layout)

	var opt := SceneryOptimizer.optimize(root)
	OcclusionSetup.setup(root)
	DistanceCulling.apply_to_world(root, Settings.draw_distance_mult)
	var toon_count := ToonShading.apply_to_world(root)
	print("NeighborhoodGenerator: streamed in %d settlements -- %d decor collapsed into %d multimesh, %d materials toon-shaded" %
		[layout.size(), opt["decor_total"], opt["multimeshes"], toon_count])

## Crop fields everywhere a settlement ISN'T: the s-gaps between every
## pair of adjacent settlements (full width), plus each settlement's own
## leftover width beyond its residential band (SettlementLayout.
## residential_x_extent()) out to the wall -- a settlement "sits in" its
## surrounding farmland rather than farmland only existing in the gaps.
## CropFieldGenerator's own connector-clearance param is unused here
## (empty array) -- these fields have no roads running through them to
## skip around, unlike the old Farm zone's connector streets.
## Crop fields at CropFieldGenerator's own 5m stalk spacing over the
## FULL half-width (up to 1500m now that WIDTH=3000) was measured live
## to generate several hundred thousand individual stalk instances
## across 9 farmland gaps -- blocking for minutes even with per-batch
## yielding, since each instance still costs a real Object allocation/
## transform/add_child before any of that count can be collapsed by
## SceneryOptimizer's later multimesh batching pass. Capped to a belt
## flanking each gap/settlement margin instead of the true full width --
## reads as "surrounded by farmland" without needing literal crops all
## the way to the outer wall.
const FARM_BELT_WIDTH := 180.0

static func _build_farmland_async(root: Node3D, radius: float, segments: int, width: float, layout: Array) -> void:
	var half_w := width * 0.5
	var belt: float = minf(FARM_BELT_WIDTH, half_w)
	var rng := RandomNumberGenerator.new()
	rng.seed = 20260921  # deterministic, matches the crop field system's own existing seed convention

	var n := layout.size()
	for i in range(n):
		var entry: Dictionary = layout[i]
		var next_entry: Dictionary = layout[(i + 1) % n]
		var gap_s0: float = entry["s_end"]
		var gap_s1: float = next_entry["s_start"]
		if gap_s1 < gap_s0:
			gap_s1 += TAU * radius
		if gap_s1 - gap_s0 > 5.0:
			var field_gap := 3.0
			await CropFieldGenerator.build_async(root, radius, segments, gap_s0, gap_s1, field_gap, belt, "corn", [], rng)
			await CropFieldGenerator.build_async(root, radius, segments, gap_s0, gap_s1, -belt, -field_gap, "soy", [], rng)

		var res_extent := SettlementLayout.residential_x_extent(entry)
		var margin_far: float = minf(res_extent + belt, half_w)
		if margin_far - res_extent > 5.0:
			await CropFieldGenerator.build_async(root, radius, segments, entry["s_start"], entry["s_end"], res_extent, margin_far, "soy", [], rng)
			await CropFieldGenerator.build_async(root, radius, segments, entry["s_start"], entry["s_end"], -margin_far, -res_extent, "corn", [], rng)
