extends Node
class_name SettlementLayout

# Pure data + pure functions describing the loop's 9-settlement
# arrangement -- 2 cities, 4 towns, 3 villages, farmland between every
# one of them. Replaces the old fixed 4-zone (Lake/Downtown/Residential/
# Farm quarter) system entirely: "We are completely abandoning my rules
# about the commercial residential agricultural and lake zones.
# Communities will be laid out and spaced according to your research,
# not my rules. We need two cities, four towns and three villages with
# farmland in between."
#
# Zero dependencies on any other class_name script here, matching
# TerrainHeight.gd's own leaf-dependency rule (see that file's header
# for why: RingCoords depends on TerrainHeight, which needs this
# layout for bluff/lake siting and road-flatten gating, and RingCoords
# is itself a dependency of everything that BUILDS a settlement -- so
# this file must not depend on any of that, or the cycle GDScript can't
# resolve comes right back.
#
# ORIENTATION (the key station-specific engineering call this file
# makes, undictated by the research): each settlement's Main Street
# runs AXIALLY (along the width, now 3,000 m -- abundant) rather than
# tangentially (along the arc, the scarce resource: 9 settlements +
# 9 farmland gaps must all fit on one ~3,141.6 m loop). A settlement's
# ARC-LENGTH footprint is therefore its "how many blocks deep"
# cross-street dimension, not its Main-Street length -- Main Street
# itself can run as long as generator_rules.md §2-3 wants using the
# width dimension instead. This is the same category of realism-vs-
# station-geometry trade-off already made for the river's compressed
# meander belt, just applied to settlement spacing instead.

enum Tier { CITY, TOWN, VILLAGE }

# Arc-length "depth" budget per tier -- NOT Main-Street length, see
# header. Sized off generator_rules.md §3 (small-city ~300ft/91m
# blocks, "multi-block" CBD => budget ~3-4 blocks deep; small-town
# "full Main Street" => ~2-3 blocks deep; village "1-3 block Main
# Street or bare crossroads" => ~1 block deep), then compressed
# further so 2 cities + 4 towns + 3 villages + 9 farmland gaps all fit
# on the loop -- a documented station-specific compression, not a
# research figure.
const TIER_ARC := {
	Tier.CITY: 340.0,
	Tier.TOWN: 220.0,
	Tier.VILLAGE: 100.0,
}

# Tier-scaled dimensions, per generator_rules.md §2-4 (small-town
# tier's own numbers reused for TOWN; CITY scales up toward the
# small-city figures; VILLAGE scales down toward the village figures).
# main_street_len is now an AXIAL (width-direction) length, not arc --
# see header.
const FT := 0.3048
const TIER_CONFIG := {
	Tier.CITY: {
		"main_street_len": 900.0,       # ~6-7 blocks of Main Street, axially
		"block_size": 91.0,             # 300 ft, small-city standard reference
		"main_st_width": 24.0 * FT,     # narrower than arterials despite density, per §2
		"secondary_st_width": 20.0 * FT,
		"sidewalk_width": 10.0 * FT,
		"alley_width": 18.0 * FT,
		"n_cross_streets": 8,
		"residential_band": 500.0,      # additional axial depth for houses beyond downtown
		"house_spacing": 22.0,
	},
	Tier.TOWN: {
		"main_street_len": 500.0,       # ~5 blocks, axially
		"block_size": 91.0,             # 1 chain = 66ft is the historic platting unit, but 300ft downtown-block reference already matches this project's existing storefront/lot conventions
		"main_st_width": 30.0 * FT,
		"secondary_st_width": 30.0 * FT,
		"sidewalk_width": 10.0 * FT,
		"alley_width": 16.0 * FT,
		"n_cross_streets": 5,
		"residential_band": 300.0,
		"house_spacing": 26.0,
	},
	Tier.VILLAGE: {
		"main_street_len": 150.0,       # "1-3 block Main Street or bare crossroads"
		"block_size": 91.0,
		"main_st_width": 20.0 * FT,
		"secondary_st_width": 20.0 * FT,
		"sidewalk_width": 6.0 * FT,
		"alley_width": 16.0 * FT,
		"n_cross_streets": 2,
		"residential_band": 120.0,
		"house_spacing": 30.0,
	},
}

# Order around the loop -- spread rather than clustered (research
# doesn't dictate sequence; a station-specific design choice).
const SEQUENCE: Array = [Tier.CITY, Tier.TOWN, Tier.VILLAGE, Tier.TOWN, Tier.CITY, Tier.TOWN, Tier.VILLAGE, Tier.TOWN, Tier.VILLAGE]

# Which SEQUENCE index is water/mill-founded (generator_rules.md §7:
# "site downtown directly against the water body... downtown grid
# elongates along the bank"). Its slice is positioned so it CONTAINS
# the river/lake system's already-tuned widest bend (see TerrainHeight.
# gd's header for that phase derivation) -- the settlement layout moves
# to meet the already-built hydrology, not the other way around, so
# none of the river/lake math needed to change.
const WATER_SETTLEMENT_INDEX := 0  # the first city in SEQUENCE

# s-value of the river's widest bend / existing lake center -- theta=PI/4
# (45 degrees) times RADIUS, from TerrainHeight.gd's PHI1..PHI4 solve.
# Duplicated here as a plain number (not a live reference) for the same
# leaf-dependency reason as TerrainHeight.gd's own duplicated constants.
const LAKE_CENTER_S := 392.7

## One settlement's full geometry: {index, tier, s_start, s_end, s_center,
## config}. Computed fresh from RADIUS every call (cheap -- 9 entries) so
## it's always consistent with whatever RADIUS the ring was last built at
## (matches this project's "SEGMENTS/RADIUS are static vars, re-derive
## rather than cache" convention elsewhere).
static func build_layout(radius: float) -> Array:
	var circumference := TAU * radius
	var total_settlement_arc := 0.0
	for tier in SEQUENCE:
		total_settlement_arc += TIER_ARC[tier]
	var n := SEQUENCE.size()
	var gap := (circumference - total_settlement_arc) / float(n)

	# Lay out starting at s=0 (gap, settlement) x n, then measure where
	# WATER_SETTLEMENT_INDEX's own center landed and shift the whole
	# layout so that center sits exactly at LAKE_CENTER_S instead.
	var raw: Array = []
	var s := 0.0
	for i in range(n):
		s += gap
		var tier = SEQUENCE[i]
		var arc: float = TIER_ARC[tier]
		var s_start := s
		var s_end := s + arc
		raw.append({"index": i, "tier": tier, "s_start": s_start, "s_end": s_end, "s_center": (s_start + s_end) * 0.5})
		s = s_end

	var water_center: float = raw[WATER_SETTLEMENT_INDEX]["s_center"]
	var offset := fposmod(LAKE_CENTER_S - water_center, circumference)

	var out: Array = []
	for entry in raw:
		var s_start: float = fposmod(entry["s_start"] + offset, circumference)
		var s_end: float = s_start + (entry["s_end"] - entry["s_start"])
		out.append({
			"index": entry["index"],
			"tier": entry["tier"],
			"s_start": s_start,
			"s_end": s_end,
			"s_center": s_start + (entry["s_end"] - entry["s_start"]) * 0.5,
			"config": TIER_CONFIG[entry["tier"]],
		})
	return out

## Convenience: the water-founded settlement's own layout entry.
static func water_settlement(radius: float) -> Dictionary:
	return build_layout(radius)[WATER_SETTLEMENT_INDEX]

## Number of axial "rows" (streets running along the width, parallel to
## Main Street, spread across the settlement's own arc-length depth) --
## a village is just Main Street itself ("bare crossroads" per
## generator_rules.md §1); town/city add parallel rows toward each
## side's block depth.
static func n_axial_rows(tier: int) -> int:
	match tier:
		Tier.CITY:
			return 5
		Tier.TOWN:
			return 3
		_:
			return 1

## Arc-length (s) position of each axial row, evenly spread across the
## settlement's own [s_start, s_end] depth. Main Street is whichever row
## is closest to the settlement's center (main_row_index() below).
static func axial_row_positions(entry: Dictionary) -> Array:
	var n := n_axial_rows(entry["tier"])
	var depth: float = entry["s_end"] - entry["s_start"]
	var rows: Array = []
	for k in range(n):
		rows.append(entry["s_start"] + depth * (float(k) + 0.5) / float(n))
	return rows

static func main_row_index(tier: int) -> int:
	return n_axial_rows(tier) / 2

## Main Street's own axial span, STRADDLING the centerline (x=0) rather
## than offset to one side -- for the water-founded settlement this
## means Main Street crosses the river/lake near the settlement's own
## center (a Main-Street bridge over the water, a common real river-
## town pattern), and for every settlement it makes symmetric use of
## the now-abundant 3,000 m width instead of leaving one whole side
## unused.
static func main_street_x_range(entry: Dictionary) -> Vector2:
	var half: float = entry["config"]["main_street_len"] * 0.5
	return Vector2(-half, half)

## Cross-street (tangential) x-positions along Main Street's own length,
## spaced by block_size -- mirrors the old DowntownGenerator's BLOCK_
## SIZE-driven cross-street spacing, just along x instead of s.
static func cross_street_x_positions(entry: Dictionary) -> Array:
	var cfg: Dictionary = entry["config"]
	var rng := main_street_x_range(entry)
	var block: float = cfg["block_size"]
	var xs: Array = []
	var x: float = rng.x
	while x <= rng.y:
		xs.append(x)
		x += block
	return xs

## Full residential axial extent on ONE side (symmetric on the other):
## from Main Street's own edge out through the residential band.
static func residential_x_extent(entry: Dictionary) -> float:
	var cfg: Dictionary = entry["config"]
	return entry["config"]["main_street_len"] * 0.5 + cfg["residential_band"]

## True if (s, x) falls under this settlement's own road network --
## every axial row (its own width) and every cross street (its own
## depth-spanning width), both sides of centerline. Pure function of
## the settlement entry + tier config, so TerrainHeight.gd can call
## this for road-flatten gating without needing the roads to actually
## be built yet (same "replicate the formula, not the built geometry"
## pattern TerrainHeight.gd's header already documents).
static func is_under_settlement_road(entry: Dictionary, s: float, x: float, clearance: float) -> bool:
	var cfg: Dictionary = entry["config"]
	var rows := axial_row_positions(entry)
	var row_half: float = cfg["secondary_st_width"] * 0.5 + cfg["sidewalk_width"] + clearance
	var main_half: float = cfg["main_st_width"] * 0.5 + cfg["sidewalk_width"] + clearance
	var main_i := main_row_index(entry["tier"])
	var x_range := main_street_x_range(entry)
	var res_extent := residential_x_extent(entry)
	for i in range(rows.size()):
		var half: float = main_half if i == main_i else row_half
		if absf(s - rows[i]) < half and x >= -res_extent - clearance and x <= res_extent + clearance:
			return true
	var cross_half: float = cfg["secondary_st_width"] * 0.5 + clearance
	if s >= entry["s_start"] - clearance and s <= entry["s_end"] + clearance:
		for cx in cross_street_x_positions(entry):
			if absf(x - cx) < cross_half:
				return true
	return false

## True if `s` (unwrapped, will be fposmod'd) falls within any
## settlement's [s_start, s_end] -- s_end is NOT wrapped (may exceed
## `circumference`) so a settlement straddling the s=0 seam still works
## with simple range checks; callers pass in the same unwrapped `s`
## space, wrapping their own query point the same way first if needed.
static func settlement_at(radius: float, s: float) -> Dictionary:
	var circumference := TAU * radius
	var s_wrapped := fposmod(s, circumference)
	for entry in build_layout(radius):
		var s_start: float = entry["s_start"]
		var s_end: float = entry["s_end"]
		if s_wrapped >= s_start and s_wrapped <= s_end:
			return entry
		# Handle a settlement whose s_end wrapped past the seam.
		if s_end > circumference and s_wrapped <= fmod(s_end, circumference):
			return entry
	return {}
