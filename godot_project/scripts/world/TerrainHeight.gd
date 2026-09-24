extends Node
class_name TerrainHeight

# Closed-loop river/lake/pond/creek/ditch elevation for the station
# ring's floor -- REAL carved depth this time, not the earlier "forced
# perspective" water-above-flat-floor hack: "I would like the full ring
# spanning full on river system with drainage, creeks, ponds and
# tributaries all carved into the ground. likewise the lake will need to
# be a lower elevation as water flows downhill."
#
# depth_at(radius, segments, s, x) returns a non-negative "how far to
# recess the floor" value in meters (0 = ungraded/normal floor).
# RingCoords.floor_point() subtracts this along "up" (i.e. moves the
# point radially OUTWARD, away from the spin axis) -- so every existing
# call site (streets, buildings, the player, water) automatically
# follows the terrain with zero changes of its own, and stays exactly
# as it was wherever depth_at() is 0 (everywhere far from water).
#
# The river centerline (river_x() below) is a short Fourier series in
# the loop angle, per research/hydrology_drainage/
# _station_river_loop_design_notes.md ("Closed-loop adaptation" -- the
# research doc's own words: "my own engineering proposal, not a cited
# real-world fact"). Channel width/depth/meander-wavelength numbers ARE
# from that doc's cited research. PHI1..PHI4 (the phase offsets) are
# NOT researched -- they're solved so the primary meander's WIDEST bend
# lands exactly at theta=LAKE_CENTER_THETA (45 degrees), which
# SettlementLayout.gd sites the water-founded settlement's own center
# on -- so the lake/river math never has to move to meet wherever a
# settlement ends up; the settlement layout moves to meet the water
# instead. Verified numerically (see the job's tmp/ scratch scripts
# this was derived with): river_x() == 0 to 1e-13 there, and the A1
# envelope peaks (widest bend) at that exact same point.
#
# The 9-settlement distribution (2 cities, 4 towns, 3 villages,
# farmland between every one) lives in SettlementLayout.gd, NOT here --
# this file only needs each settlement's own road SHAPE (for the
# road-flatten gating below) and its center (for siting the lake/bluff-
# tilt trough), both exposed as pure functions there.
#
# Wherever a carved water feature would run under an already-built
# settlement road, depth is gated to 0 by _is_under_road() -- expected
# and BY DESIGN, not a bug ("we will need smaller bridges for the side
# roads crossing over creeks and tributaries" was the original brief
# for the river; the same reasoning now applies to every settlement's
# own street grid). The raised bluff/tilt terrain (bluff_height()/
# zone_tilt() below) is deliberately NOT gated the same way -- it's
# smooth by construction (tanh/cosine, no sharp edges), so a road
# climbing the bluff just follows its grade, the way a real hillside
# road would.
#
# DEPENDENCY RULE (load-bearing, confirmed empirically -- not a style
# preference): this file calls into NO other class_name script except
# SettlementLayout.gd, which is itself a pure leaf with no dependencies
# of its own (same rule, one level removed). RingCoords.floor_point()
# -- the one function every single placement in the game goes through
# (streets, buildings, the player, water) -- calls TerrainHeight.
# elevation_at() for every point. That makes RingCoords a hard
# dependent of this file, and RingCoords is itself a dependency of
# every settlement-building script and of StationRingBuilder, which
# SpaceStation.gd calls. If TerrainHeight called back into ANY of those
# it would form a two-file cycle, and GDScript's class_name resolution
# genuinely cannot parse that (verified directly with a minimal 2-file
# repro: two class_name scripts calling each other's static funcs fail
# to compile with "Identifier ... not declared in the current scope",
# even though neither `extends` the other). So every constant/formula
# TerrainHeight needs beyond SettlementLayout.gd's own pure data is
# duplicated below instead. The one exception is RING_WIDTH: a static
# var WRITTEN by StationRingBuilder.build() (which already receives
# `width` as a parameter) rather than read from SpaceStation.WIDTH
# directly -- that's a one-way write, not a reference back, so it
# doesn't reintroduce the cycle.

const FT := 0.3048

## The remake world: the terrain is the map's (MapTerrain.gd, ported from tools/map_preview.py) --
## elevation_at()/depth_at() delegate to it; everything below is the earlier layout's model.
static var USE_MAP := false
static var RING_WIDTH := 1000.0  # set by StationRingBuilder.build()'s first line -- see this file's header

# --- Lake -- now just a widened stretch of the river centered on the
# water-founded settlement (SettlementLayout.WATER_SETTLEMENT_INDEX),
# not a dedicated zone with its own shore-road loop (that whole concept
# is gone along with the old 4-zone system). Half-span chosen to
# roughly match the old lake's own extent; independent of any
# settlement's own (much smaller) arc-depth, since a lake reasonably
# extends into the surrounding farmland gaps either side.
const LAKE_HALF_WIDTH := 65.0
const LAKE_HALF_SPAN := 350.0
const LAKE_END_CAP_LEN := 40.0

# --- Bluff/relief terrain (generator_rules.md §16) -- reuses the
# river's own k=6 harmonic/phase (PHI1, PHI4 below) so cut-bank (high)
# and point-bar (low) sides stay automatically correlated with the
# river's bends, per that section's own "core trick." Numbers are
# straight from that section's table.
const H_BLUFF_BASE := 18.0   # bluff height, compressed from real 21-55m town relief for buildable grades
const D0 := 80.0             # flat low-terrace setback before the climb starts
const L_BLUFF := 75.0        # transition run (~24% max grade, easing flat within ~3xL_BLUFF)
const BLUFF_FLIP_SHARPNESS := 1.5  # see bluff_height() -- lower = longer, gentler high/low bank swap along s
const Z1 := 10.0             # gentle k=1 regional tilt, troughs at the water-settlement's center

const A1_BASE := 150.0
const A2 := 45.0
const A3 := 25.0
# Solved so LAKE_CENTER_THETA (theta=PI/4, where the water-founded
# settlement's own center sits -- see SettlementLayout.gd) simultaneously
# zeroes all three sine terms AND sits at the A1 envelope's peak -- see
# this file's header comment.
const PHI1 := PI * 0.5
const PHI2 := -PI * 0.25
const PHI3 := -PI * 0.25
const PHI4 := 0.0

const CHANNEL_BED_HALF_WIDTH := 12.0
const CHANNEL_BANK_WIDTH := 10.5   # bed+bank = 22.5 => 45m channel width total, per research
const CHANNEL_DEPTH := 2.5

const LAKE_DEPTH := 4.5            # deeper than the plain channel -- "water flows downhill" into the lake
const LAKE_SHELF_WIDTH := 20.0     # how far in from the lake's outer (water-line) edge the flat deep bed starts

const POND_DEPTH := 1.8
const POND_BANK_WIDTH := 6.0
const CREEK_HALF_WIDTH := 3.0      # 6m wide, per research's tributary-creek spec
const CREEK_BANK_WIDTH := 3.0
const CREEK_DEPTH := 1.1

const DITCH_HALF_WIDTH := 0.9      # ~1.8m wide, farm drainage
const DITCH_BANK_WIDTH := 1.5
const DITCH_DEPTH := 0.6

const ROAD_CLEARANCE := 4.0        # meters of margin on each side of a detected road, gated flat

# Curated, fixed (deterministic -- no RNG, same input/same output by
# construction) ponds: [s_center, x_center, long_axis_len, half_width].
# Distributed across Residential/Farm's open middle ground plus one
# near-downtown oxbow remnant, per research/hydrology_drainage's own
# siting guidance -- positions chosen (and checked against each zone's
# own road/building formulas) to sit clear of built footprints; see
# this file's header for the verification approach.
const PONDS := [
	[1650.0, -150.0, 80.0, 25.0],
	[2250.0, 170.0, 70.0, 22.0],
	[2450.0, -180.0, 90.0, 28.0],
	[2700.0, 200.0, 70.0, 24.0],
	[3000.0, -190.0, 80.0, 26.0],
	[900.0, 190.0, 65.0, 20.0],
]

# Short tributary creeks, one per pond above, running from the pond's
# own center to a point on the river's own centerline at CREEK_RIVER_S[i]
# (computed at runtime via river_x()) -- chosen close to the pond's own s
# for a short, direct run, per the 60-300m tributary length spec.
const CREEK_RIVER_S := [1650.0, 2250.0, 2470.0, 2700.0, 3000.0, 920.0]

# Simplified farm drainage ditches: [s_center, x_center, x_river_end]
# short straight-ish field ditches staged into the nearest creek/pond
# rather than direct into the river (per research's ditch->creek->river
# hierarchy) -- a curated handful rather than a full systematic grid
# (an explicit scope simplification; see the session's own notes).
const DITCHES := [
	[2430.0, -100.0, -180.0],
	[2470.0, -60.0, -180.0],
	[2680.0, 120.0, 200.0],
	[2720.0, 160.0, 200.0],
]


static func river_theta(radius: float, s: float) -> float:
	return s / radius

## The river centerline's axial (x) offset at arc length `s`. See this
## file's header for the harmonic stack and phase-tuning rationale.
static func river_x(radius: float, s: float) -> float:
	var theta := river_theta(radius, s)
	var envelope := A1_BASE * (1.0 + 0.3 * sin(2.0 * theta + PHI4))
	return envelope * sin(6.0 * theta + PHI1) + A2 * sin(13.0 * theta + PHI2) + A3 * sin(theta + PHI3)

## Trapezoidal cross-section: flat `depth` out to `bed_hw`, smoothly
## tapering to 0 over the next `bank_w`, 0 beyond. `au` is the absolute
## perpendicular distance from whatever centerline/point this is being
## measured against.
static func _trapezoid_depth(au: float, bed_hw: float, bank_w: float, depth: float) -> float:
	if au <= bed_hw:
		return depth
	if bank_w <= 0.001:
		return 0.0
	if au <= bed_hw + bank_w:
		var t := (au - bed_hw) / bank_w
		return depth * (1.0 - smoothstep(0.0, 1.0, t))
	return 0.0

## Depth from the nearest point on the segment (s_a,x_a)-(s_b,x_b) --
## used for both ponds (a short "long axis" segment, giving a stadium/
## capsule oval shape) and creeks/ditches (an actual connector). `s`/`x`
## are treated as a flat 2D plane (arc length and axial meters are both
## metric and roughly orthogonal at this scale over a short span) --
## fine for these short (well under one meander wavelength) features.
static func _segment_depth(s: float, x: float, s_a: float, x_a: float, s_b: float, x_b: float,
		bed_hw: float, bank_w: float, depth: float) -> float:
	var pa := Vector2(s_a, x_a)
	var pb := Vector2(s_b, x_b)
	var p := Vector2(s, x)
	var ab := pb - pa
	var len2 := ab.length_squared()
	var t := 0.0
	if len2 > 0.0001:
		t = clampf((p - pa).dot(ab) / len2, 0.0, 1.0)
	var closest: Vector2 = pa + ab * t
	return _trapezoid_depth(p.distance_to(closest), bed_hw, bank_w, depth)

static func river_channel_depth(radius: float, s: float, x: float) -> float:
	var au := absf(x - river_x(radius, s))
	return _trapezoid_depth(au, CHANNEL_BED_HALF_WIDTH, CHANNEL_BANK_WIDTH, CHANNEL_DEPTH)

## theta where PHI1..PHI4 were solved so the river's widest bend sits at
## x=0 (see this file's header) -- the water-founded settlement's own
## center (SettlementLayout.LAKE_CENTER_S, a duplicated copy of
## LAKE_CENTER_THETA*radius for the same leaf-dependency reason as
## everything else duplicated in that file).
const LAKE_CENTER_THETA := PI * 0.25

static func lake_center_s(radius: float) -> float:
	return LAKE_CENTER_THETA * radius

static func _lake_s_range(radius: float) -> Vector2:
	var c := lake_center_s(radius)
	return Vector2(c - LAKE_HALF_SPAN, c + LAKE_HALF_SPAN)

## Mirrors LakeGenerator._lake_half_width() exactly.
static func _lake_half_width_local(s: float, s_start: float, s_end: float, straight_s0: float, straight_s1: float) -> float:
	if s < straight_s0:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clampf((s - s_start) / (straight_s0 - s_start), 0.0, 1.0))
	if s > straight_s1:
		return LAKE_HALF_WIDTH * smoothstep(0.0, 1.0, clampf((s_end - s) / (s_end - straight_s1), 0.0, 1.0))
	return LAKE_HALF_WIDTH

## The lake basin: reuses the lake's own taper shape (_lake_half_width_
## local(), above) as the "bank-top" edge, with a flat, LAKE_DEPTH-deep
## bed inset LAKE_SHELF_WIDTH in from that edge, blending down to plain
## CHANNEL_DEPTH as the taper narrows to ordinary channel width at the
## necked ends -- shallower necking, deeper open water, exactly the
## "lake is lower than the river that feeds it" the ask called for.
static func lake_depth(radius: float, segments: int, s: float, x: float) -> float:
	var rng := _lake_s_range(radius)
	var lake_s0: float = rng.x
	var lake_s1: float = rng.y
	if s < lake_s0 or s > lake_s1:
		return 0.0
	var straight_s0 := lake_s0 + LAKE_END_CAP_LEN
	var straight_s1 := lake_s1 - LAKE_END_CAP_LEN
	var lake_hw := _lake_half_width_local(s, lake_s0, lake_s1, straight_s0, straight_s1)
	if lake_hw <= 0.5:
		return 0.0
	var channel_outer := CHANNEL_BED_HALF_WIDTH + CHANNEL_BANK_WIDTH
	var span: float = maxf(0.001, LAKE_HALF_WIDTH - channel_outer)
	var depth_here: float = lerpf(CHANNEL_DEPTH, LAKE_DEPTH, clampf((lake_hw - channel_outer) / span, 0.0, 1.0))
	var bed_hw: float = maxf(CHANNEL_BED_HALF_WIDTH, lake_hw - LAKE_SHELF_WIDTH)
	var bank_w: float = maxf(0.5, lake_hw - bed_hw)
	return _trapezoid_depth(absf(x), bed_hw, bank_w, depth_here)

static func ponds_depth(s: float, x: float) -> float:
	var best := 0.0
	for pond in PONDS:
		var s_c: float = pond[0]
		var x_c: float = pond[1]
		var half_len: float = pond[2] * 0.5
		var half_w: float = pond[3]
		var d := _segment_depth(s, x, s_c - half_len, x_c, s_c + half_len, x_c, half_w, POND_BANK_WIDTH, POND_DEPTH)
		best = maxf(best, d)
	return best

static func creeks_depth(radius: float, s: float, x: float) -> float:
	var best := 0.0
	for i in range(PONDS.size()):
		var pond: Array = PONDS[i]
		var s_c: float = pond[0]
		var x_c: float = pond[1]
		var s_river: float = CREEK_RIVER_S[i]
		var x_river := river_x(radius, s_river)
		var d := _segment_depth(s, x, s_c, x_c, s_river, x_river, CREEK_HALF_WIDTH, CREEK_BANK_WIDTH, CREEK_DEPTH)
		best = maxf(best, d)
	return best

static func ditches_depth(s: float, x: float) -> float:
	var best := 0.0
	for ditch in DITCHES:
		var s_c: float = ditch[0]
		var x_c: float = ditch[1]
		var x_end: float = ditch[2]
		var d := _segment_depth(s, x, s_c, x_c, s_c, x_end, DITCH_HALF_WIDTH, DITCH_BANK_WIDTH, DITCH_DEPTH)
		best = maxf(best, d)
	return best

## True if (s,x) falls under an already-built settlement road -- gates
## carving to 0 there so roads stay flat/intact. Iterates SettlementLayout.
## build_layout()'s 9 settlements and checks each one's own road formula
## (SettlementLayout.is_under_settlement_road()) -- that file is a pure
## leaf (no dependencies of its own), so this stays consistent with this
## file's top-of-file dependency rule despite needing settlement-shaped
## data. Cheap to call unconditionally (9 settlements, most immediately
## rejected by their own s-range check).
static func _is_under_road(radius: float, segments: int, s: float, x: float) -> bool:
	for entry in SettlementLayout.build_layout(radius):
		var s_start: float = entry["s_start"]
		var s_end: float = entry["s_end"]
		if s < s_start - ROAD_CLEARANCE or s > s_end + ROAD_CLEARANCE:
			continue
		if SettlementLayout.is_under_settlement_road(entry, s, x, ROAD_CLEARANCE):
			return true
	return false

## Combined recess depth (water features only, non-negative) at (s, x)
## -- kept separate from elevation_at() below because LakeGenerator.gd/
## RiverGenerator.gd need this specific "how deep is the water here"
## number for their own water-surface placement (WATER_SURFACE_DROP
## etc.), unaffected by the bluff feature (spatially separate anyway --
## bluffs only start D0=80m out, water features cap out well under
## that). Deepest feature wins (max, not sum) so confluences (a creek
## meeting the river, a ditch meeting a creek) blend instead of double-
## carving; gated to exactly 0 under any existing road so those stay
## flat and intact.
static func depth_at(radius: float, segments: int, s: float, x: float) -> float:
	if USE_MAP:
		return MapTerrain.water_depth(s, x)
	if _is_under_road(radius, segments, s, x):
		return 0.0
	var d := river_channel_depth(radius, s, x)
	d = maxf(d, lake_depth(radius, segments, s, x))
	d = maxf(d, ponds_depth(s, x))
	d = maxf(d, creeks_depth(radius, s, x))
	d = maxf(d, ditches_depth(s, x))
	return d

## Raised bluff terrain (generator_rules.md §16): reuses the river's own
## k=6 harmonic/phase (same PHI1/PHI4 as river_x()/its envelope) so
## cut-bank (high) and point-bar (low) sides stay automatically
## correlated with the river's bends everywhere around the loop -- "any
## smooth function of (x-y(theta)) is automatically periodic in theta
## too," the same trick the water features already rely on. Flat within
## D0 of the river (the low terrace buildings/roads actually sit on),
## rising over the next L_BLUFF via tanh (chosen for genuinely flat
## upland shoulders -- a sine would roll back down instead), clamped to
## 0 on the near side so it never goes negative before the climb starts.
static func bluff_height(radius: float, s: float, x: float) -> float:
	var theta := river_theta(radius, s)
	var envelope := H_BLUFF_BASE * (1.0 + 0.3 * sin(2.0 * theta + PHI4))
	# Smoothed sign, not signf(): a hard sign flipped the bluff from +H to
	# -H in zero distance at 12 points around the ring -- a ~36m cliff no
	# 33m floor segment can follow (confirmed live: 12.5% of the floor was
	# >5m off this function, so anything placed via floor_point() floated
	# or sank there). Normalized tanh still reaches exactly +-1 at the
	# peaks, but eases through zero over ~120m of s.
	var sign_val := tanh(BLUFF_FLIP_SHARPNESS * sin(6.0 * theta + PHI1)) / tanh(BLUFF_FLIP_SHARPNESS)
	var u := absf(x - river_x(radius, s))
	var step := maxf(0.0, tanh((u - D0) / L_BLUFF))
	return envelope * sign_val * step

## Gentle k=1 regional tilt, troughing at the water-founded settlement's
## own center -- "real lakes often have one bluffier and one flat/marshy
## shore." Lowest available harmonic, kept well under H_BLUFF_BASE so it
## reads as background, not competing relief.
static func zone_tilt(radius: float, s: float) -> float:
	var theta := river_theta(radius, s)
	return -Z1 * cos(theta - LAKE_CENTER_THETA)

## Combined SIGNED elevation offset -- positive raises (bluff/tilt),
## negative recesses (water features, via depth_at() which already
## gates itself to 0 under roads). This is what RingCoords.floor_point()
## actually applies to every point on the ring; bluff/tilt are smooth by
## construction (tanh/cosine, no sharp edges) so they're deliberately
## NOT gated under roads the way the water features are -- a road
## climbing the bluff just follows its grade, same as a real hillside
## road would.
static func elevation_at(radius: float, segments: int, s: float, x: float) -> float:
	if USE_MAP:
		return MapTerrain.elevation(s, x)
	return bluff_height(radius, s, x) + zone_tilt(radius, s) - depth_at(radius, segments, s, x)

## Critical x-breakpoints for one ring segment (its two s-edges) --
## guarantees the adaptive floor mesh/collision always samples exactly
## at each active feature's own bed/bank edges, however the meander has
## shifted them, rather than risking a fixed grid straddling (and nearly
## erasing) a feature between samples. Always includes both width
## extremes. Deliberately generous (checks every feature at both
## segment edges) since this only runs 96 times per rebuild, not once
## per frame.
static func critical_x_values(radius: float, segments: int, seg_s0: float, seg_s1: float, half_width: float) -> Array:
	var xs: Array = [-half_width, half_width]
	for s in [seg_s0, seg_s1]:
		var rc := river_x(radius, s)
		for off in [-CHANNEL_BED_HALF_WIDTH - CHANNEL_BANK_WIDTH, -CHANNEL_BED_HALF_WIDTH,
				CHANNEL_BED_HALF_WIDTH, CHANNEL_BED_HALF_WIDTH + CHANNEL_BANK_WIDTH]:
			xs.append(clampf(rc + off, -half_width, half_width))
		var lake_rng := _lake_s_range(radius)
		if s >= lake_rng.x and s <= lake_rng.y:
			var lake_s0: float = lake_rng.x
			var lake_s1: float = lake_rng.y
			var straight_s0 := lake_s0 + LAKE_END_CAP_LEN
			var straight_s1 := lake_s1 - LAKE_END_CAP_LEN
			var lake_hw := _lake_half_width_local(s, lake_s0, lake_s1, straight_s0, straight_s1)
			for off in [-lake_hw, lake_hw]:
				xs.append(clampf(off, -half_width, half_width))
		for pond in PONDS:
			var s_c: float = pond[0]
			var half_len: float = pond[2] * 0.5
			if s >= s_c - half_len - 20.0 and s <= s_c + half_len + 20.0:
				var x_c: float = pond[1]
				var hw: float = pond[3]
				xs.append(clampf(x_c - hw - POND_BANK_WIDTH, -half_width, half_width))
				xs.append(clampf(x_c + hw + POND_BANK_WIDTH, -half_width, half_width))
		for i in range(PONDS.size()):
			var pond: Array = PONDS[i]
			var s_c: float = pond[0]
			var x_c: float = pond[1]
			var s_river: float = CREEK_RIVER_S[i]
			var x_river := river_x(radius, s_river)
			if _near_segment(s, s_c, x_c, s_river, x_river, 60.0):
				xs.append(clampf(_project_x(s, s_c, x_c, s_river, x_river), -half_width, half_width))
		for ditch in DITCHES:
			var s_c: float = ditch[0]
			if absf(s - s_c) < 30.0:
				xs.append(clampf(ditch[1], -half_width, half_width))
				xs.append(clampf(ditch[2], -half_width, half_width))
		# Bluff transition (smooth tanh, no sharp edge -- a handful of
		# samples across the run is enough, not exact breakpoints like
		# the water features' trapezoid corners need).
		for frac: float in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]:
			var u := D0 + frac * L_BLUFF
			xs.append(clampf(rc + u, -half_width, half_width))
			xs.append(clampf(rc - u, -half_width, half_width))
		# Settlement road edges -- so a settlement's own street grid gets
		# a real breakpoint at each road, not just wherever it happens to
		# land relative to the water/bluff breakpoints above.
		for entry in SettlementLayout.build_layout(radius):
			if s < entry["s_start"] - 2.0 or s > entry["s_end"] + 2.0:
				continue
			for cx in SettlementLayout.cross_street_x_positions(entry):
				xs.append(clampf(cx, -half_width, half_width))
			var res_extent := SettlementLayout.residential_x_extent(entry)
			xs.append(clampf(-res_extent, -half_width, half_width))
			xs.append(clampf(res_extent, -half_width, half_width))
	xs.sort()
	var out: Array = []
	for v in xs:
		if out.is_empty() or v - out[out.size() - 1] > 1.0:
			out.append(v)
	return out

static func _near_segment(s: float, s_a: float, x_a: float, s_b: float, x_b: float, tol: float) -> bool:
	# s-only proximity check (ignores x) -- cheap pre-filter for whether
	# this segment's arc-length range is anywhere near `s` at all.
	var lo := minf(s_a, s_b) - tol
	var hi := maxf(s_a, s_b) + tol
	return s >= lo and s <= hi

static func _project_x(s: float, s_a: float, x_a: float, s_b: float, x_b: float) -> float:
	if absf(s_b - s_a) < 0.001:
		return x_a
	var t := clampf((s - s_a) / (s_b - s_a), 0.0, 1.0)
	return lerpf(x_a, x_b, t)

## Lifts an already-computed carved bed point up to a flat water surface
## `drop` meters below original (ungraded) grade -- takes `bed`/`depth`
## as already-known values (rather than calling RingCoords.floor_point()/
## depth_at() itself) per this file's top-of-file dependency rule: this
## file must not call into RingCoords. Callers (RiverGenerator.gd;
## LakeGenerator.gd keeps its own small private copy, already verified
## working) compute both via RingCoords.floor_point()/TerrainHeight.
## depth_at() themselves, which is safe for THEM since neither of those
## two files is anything TerrainHeight depends on. Callers must keep
## `drop` less than the shallowest depth they'll sample, or the
## "surface" ends up below the bed.
static func water_surface_point(bed: Vector3, depth: float, up: Vector3, drop: float) -> Vector3:
	return bed + up * (depth - drop)
