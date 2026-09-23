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
# NOT researched -- they're solved here so the primary meander's WIDEST
# bend lands exactly at the existing Lake zone's arc midpoint at x=0,
# which is exactly where LakeGenerator.gd's already-built, already-
# tested shore-road loop (LAKE_HALF_WIDTH=65, centered x=0) sits. That
# means the lake's road skeleton needed zero changes -- the river was
# tuned to flow through the lake that was already there, not the other
# way around. Verified numerically (see the job's tmp/ scratch scripts
# this was derived with): river_x(lake zone midpoint) == 0 to 1e-13,
# and the A1 envelope peaks (widest bend) at that exact same point.
#
# Wherever a carved feature would run under an EXISTING road, depth is
# gated to 0 by _is_under_road() -- expected and BY DESIGN, not a bug
# ("we will need smaller bridges for the side roads crossing over
# creeks and tributaries" was the original brief). Downtown is the one
# zone where the river's ~220m excursion amplitude spends most of its
# time inside downtown's much narrower (~115m half-corridor) built
# footprint -- rather than trying to carve a river through streets and
# storefronts that were never built river-aware, the WHOLE downtown
# corridor is treated as one no-carve zone (see _is_under_road()):
# the river reads as flowing past/alongside downtown, visibly carved
# right up to the built corridor's edge and resuming just past it, the
# same way a real downtown's waterfront blocks sit at grade up to the
# bank rather than showing a carved ravine mid-street. Residential and
# Farm don't need this -- their built areas sit further out than the
# river's excursion reaches there (verified numerically), so ordinary
# per-road-line gating there leaves the carved river fully visible.
#
# DEPENDENCY RULE (load-bearing, confirmed empirically -- not a style
# preference): this file calls into NO other class_name script.
# RingCoords.floor_point() -- the one function every single placement
# in the game goes through (streets, buildings, the player, water) --
# calls TerrainHeight.depth_at() for every point. That makes RingCoords
# a hard dependent of this file. RingCoords is itself a dependency of
# every zone generator (Downtown/Residential/Farm/Lake) and of
# StationRingBuilder, which SpaceStation.gd calls. If TerrainHeight
# called back into ANY of those (which it needs data from -- zone
# s-ranges, road widths, the lake's own taper shape) it would form a
# two-file cycle, and GDScript's class_name resolution genuinely cannot
# parse that (verified directly with a minimal 2-file repro: two
# class_name scripts calling each other's static funcs fail to compile
# with "Identifier ... not declared in the current scope", even though
# neither `extends` the other). So every constant/formula TerrainHeight
# needs from those other files is duplicated below instead, each
# commented with which file it must be kept in sync with by hand. The
# one exception is RING_WIDTH: a static var WRITTEN by StationRingBuilder.
# build() (which already receives `width` as a parameter) rather than
# read from SpaceStation.WIDTH directly -- that's a one-way write, not a
# reference back, so it doesn't reintroduce the cycle.

const FT := 0.3048

static var RING_WIDTH := 1000.0  # set by StationRingBuilder.build()'s first line -- see this file's header

# --- Lake -- mirrors LakeGenerator.gd's own LAKE_HALF_WIDTH/SHORE_GAP/
# RING_ROAD_WIDTH/SIDEWALK_WIDTH/END_CAP_LEN consts and _lake_half_width(). ---
const LAKE_HALF_WIDTH := 65.0
const LAKE_SHORE_GAP := 12.0
const LAKE_RING_ROAD_WIDTH := 34.0 * FT
const LAKE_SIDEWALK_WIDTH := 5.0 * FT
const LAKE_END_CAP_LEN := 40.0

# --- Downtown -- mirrors DowntownGenerator.gd's own consts/BAND_DEPTH. ---
const DOWNTOWN_ST_WIDTH := 30.0 * FT
const DOWNTOWN_SIDEWALK_WIDTH := 10.0 * FT
const DOWNTOWN_HALF_ST := DOWNTOWN_ST_WIDTH * 0.5 + DOWNTOWN_SIDEWALK_WIDTH
const DOWNTOWN_BAND_DEPTH := DOWNTOWN_HALF_ST + 3.0 + 28.0 + 2.0 + (DOWNTOWN_ST_WIDTH * 0.75) + 2.0 + DOWNTOWN_HALF_ST

# --- Residential -- mirrors ResidentialGenerator.gd's own consts/_meander_x()/_curve_x_at(). ---
const RES_N_SECTIONS := 9
const RES_MEANDER_AMPLITUDE := 20.0
const RES_MEANDER_FREQ := 0.9
const RES_LOCAL_ST_WIDTH := 34.0 * FT * 2.0
const RES_VERGE_WIDTH := 4.0 * FT
const RES_SIDEWALK_WIDTH := 5.0 * FT

# --- Farm -- mirrors FarmGenerator.gd's own consts. ---
const FARM_MAIN_ROAD_WIDTH := 24.0 * FT * 2.0
const FARM_CONNECTOR_WIDTH := 20.0 * FT * 2.0
const FARM_N_CONNECTORS := 4

const A1_BASE := 150.0
const A2 := 45.0
const A3 := 25.0
# Solved so theta_mid (the Lake zone's own arc midpoint) simultaneously
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

## The 4 zones' [s_start, s_end] (lake/downtown/residential/farm, in that
## order), already trimmed by the one-segment buffer -- mirrors
## NeighborhoodGenerator.zone_ranges() + build_skeleton()'s own buffer
## trim exactly (same formula), so this never drifts from where those
## zones' roads were actually built.
static func _zone_s_ranges(radius: float, segments: int) -> Array:
	var zone_segments := segments / 4
	var seg_arc := (TAU / segments) * radius
	var buffer := seg_arc
	var out: Array = []
	for i in range(4):
		var s0 := float(i * zone_segments) * seg_arc + buffer
		var s1 := float((i + 1) * zone_segments) * seg_arc - buffer
		out.append(Vector2(s0, s1))
	return out

static func _lake_s_range(radius: float, segments: int) -> Vector2:
	return _zone_s_ranges(radius, segments)[0]

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
	var rng := _lake_s_range(radius, segments)
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

## Mirrors ResidentialGenerator._meander_x().
static func _res_meander_x(base: float, k: int, phase: float) -> float:
	return base + RES_MEANDER_AMPLITUDE * sin(float(k) * RES_MEANDER_FREQ + phase)

## Mirrors StreetBuilder._curved_x() at curviness=1.0 -- the only value
## ResidentialGenerator's own build_curved_road() calls use.
static func _curved_x_local(x_start: float, x_end: float, s_start: float, span: float, s: float) -> float:
	if span <= 0.0:
		return x_start
	var t := (s - s_start) / span
	return lerpf(x_start, x_end, smoothstep(0.0, 1.0, t))

## Mirrors ResidentialGenerator._curve_x_at().
static func _res_curve_x_at(waypoints: Array, s: float) -> float:
	for i in range(waypoints.size() - 1):
		var a: Vector2 = waypoints[i]
		var b: Vector2 = waypoints[i + 1]
		if s >= a.x and s <= b.x:
			return _curved_x_local(a.y, b.y, a.x, b.x - a.x, s)
	var last: Vector2 = waypoints[waypoints.size() - 1]
	return last.y

## True if (s,x) falls under an already-built road (any zone) -- gates
## carving to 0 there so roads stay flat/intact; see this file's header
## for the downtown-specific whole-corridor exemption and the top-of-file
## dependency rule for why this duplicates each zone's own road-shape
## formula instead of calling into it.
static func _is_under_road(radius: float, segments: int, s: float, x: float) -> bool:
	var width := RING_WIDTH
	var zones := _zone_s_ranges(radius, segments)

	var lake_s0: float = zones[0].x
	var lake_s1: float = zones[0].y
	if s >= lake_s0 and s <= lake_s1:
		var half: float = LAKE_RING_ROAD_WIDTH * 0.5 + LAKE_SIDEWALK_WIDTH + ROAD_CLEARANCE
		var lx := LAKE_HALF_WIDTH + LAKE_SHORE_GAP
		if absf(x - lx) < half or absf(x + lx) < half:
			return true

	# Downtown: the WHOLE built corridor (all 4 building bands + all 5
	# streets), not individual street lines -- see this file's header for
	# why (the river spends most of its downtown presence inside a
	# corridor narrower than its own excursion amplitude).
	var dt_s0: float = zones[1].x
	var dt_s1: float = zones[1].y
	if s >= dt_s0 and s <= dt_s1:
		var corridor_half: float = 2.0 * DOWNTOWN_BAND_DEPTH + DOWNTOWN_HALF_ST + ROAD_CLEARANCE
		if absf(x) < corridor_half:
			return true

	var res_s0: float = zones[2].x
	var res_s1: float = zones[2].y
	if s >= res_s0 and s <= res_s1:
		var half_width_margin: float = width * 0.5 - 15.0
		var base_a := -half_width_margin * 0.5
		var base_b := half_width_margin * 0.5
		var wp_a: Array = []
		var wp_b: Array = []
		for k in range(RES_N_SECTIONS + 1):
			var ws: float = res_s0 + (res_s1 - res_s0) * float(k) / float(RES_N_SECTIONS)
			wp_a.append(Vector2(ws, _res_meander_x(base_a, k, 0.0)))
			wp_b.append(Vector2(ws, _res_meander_x(base_b, k, PI * 0.5)))
		var half: float = RES_LOCAL_ST_WIDTH * 0.5 + RES_VERGE_WIDTH + RES_SIDEWALK_WIDTH + ROAD_CLEARANCE
		if absf(x - _res_curve_x_at(wp_a, s)) < half:
			return true
		if absf(x - _res_curve_x_at(wp_b, s)) < half:
			return true

	var farm_s0: float = zones[3].x
	var farm_s1: float = zones[3].y
	if s >= farm_s0 and s <= farm_s1:
		var x_a := -width * 0.25
		var x_b := width * 0.25
		var half: float = FARM_MAIN_ROAD_WIDTH * 0.5 + ROAD_CLEARANCE
		if absf(x - x_a) < half or absf(x - x_b) < half:
			return true
		var zone_len := farm_s1 - farm_s0
		var half_w := width * 0.5
		if x >= -half_w and x <= half_w:
			for i in range(1, FARM_N_CONNECTORS + 1):
				var s_conn: float = farm_s0 + zone_len * float(i) / float(FARM_N_CONNECTORS + 1)
				if absf(s - s_conn) < FARM_CONNECTOR_WIDTH * 0.5 + ROAD_CLEARANCE:
					return true

	return false

## Combined recess depth at (s, x) -- the single entry point RingCoords.
## floor_point() calls. Deepest feature wins (max, not sum) so
## confluences (a creek meeting the river, a ditch meeting a creek)
## blend instead of double-carving; gated to exactly 0 under any
## existing road so those stay flat and intact.
static func depth_at(radius: float, segments: int, s: float, x: float) -> float:
	if _is_under_road(radius, segments, s, x):
		return 0.0
	var d := river_channel_depth(radius, s, x)
	d = maxf(d, lake_depth(radius, segments, s, x))
	d = maxf(d, ponds_depth(s, x))
	d = maxf(d, creeks_depth(radius, s, x))
	d = maxf(d, ditches_depth(s, x))
	return d

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
		var lake_rng := _lake_s_range(radius, segments)
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
