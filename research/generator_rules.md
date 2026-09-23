# Procedural Map Generator — Rules & Parameters

Synthesized from all research in `research/population_tiers/`, `research/hydrology_drainage/`,
and `research/building_catalog/`. This is the file the map generator (Phase 3, not yet built)
should actually read values from. Every number below is a **range to sample from**, not a fixed
constant — real settlements vary roughly 2x on most dimensions even within one population tier.
Full sourcing/caveats live in each tier's `_tier_summary.md`; this file only carries the
generator-usable conclusions.

Station geometry recap (current, `SpaceStation.gd`): ring circumference **C ≈ 3,142 m**
(radius 500 m), floor width **1,000 m**, 96 segments, four zones in sequence around the loop
— Lake → Downtown → Residential → Farm → back to Lake — each spanning 24 segments (~785 m arc).

---

## 1. Settlement scale / population-tier selection

The station's single ring represents **one settlement**. Three real-world tiers were
researched, each with its own parameter set below. Pick one tier as the station's baseline
(recommended default: **small town, 6,000-10,000** — its Main Street/block/lot scale fits the
existing ~785 m-long, zero-setback downtown already built, and its street-width doubling
already applied to residential/farm matches this tier's local-street norms). A more advanced
generator could blend tiers by zone (e.g. a denser small-city-scale downtown against a
village-scale farm edge) — the tables below are written per-tier specifically to support that.

| Tier | Population | Downtown character | Residential character |
|---|---|---|---|
| Village | 500-5,000 | 1-3 block Main Street or bare crossroads; 5-60 storefronts scaling with population | 2-10 residential streets, simple grid, farmland 400-800 m from core |
| Small town | 6,000-10,000 | Full Main Street, courthouse/green/rail-spine organization | 2-3 zoning tiers, grid core fraying to curvilinear edges |
| Small city | 30,000-50,000 | Multi-block CBD, distinct from arterial strip commercial | Grid near-core (narrow pre-war lots) + postwar curvilinear subdivisions |

---

## 2. Street / road hierarchy

| Class | Village | Small town | Small city |
|---|---|---|---|
| Primary commercial street (Main St / CBD) | 66 ft / 20 m ROW (default) | 90-100 ft ROW; **~1.5x** ordinary grid street | Often narrower than arterials despite highest density; being narrowed in "revitalized" variants |
| Ordinary grid / local street | ~50 ft / 15 m secondary | 60-66 ft ROW (66 ft = 1 chain, the standard 19th-c. platting unit) | 50-65 ft ROW; 22-40 ft curb-to-curb (28 ft most common) |
| Collector | n/a at this scale | ~66-80 ft ROW | ~66 ft (up to 80 ft near arterial junctions), 11 ft/lane |
| Arterial | n/a | n/a (villages/small towns rarely have a true arterial) | 60-100+ ft ROW (up to 200 ft principal arterial), 12 ft/lane |
| Alley | 16 ft / 4.9 m | 16 ft / 4.9 m | 16-20 ft |

**Rule of thumb (cross-tier):** primary commercial street ≈ 1.5x an ordinary grid street's
width. Residential streets get progressively narrower and lose curbs/sidewalks moving from
city → town → village, and toward each settlement's own outer edge regardless of tier.

**Building-type clustering by street class:** local/collector streets carry houses and small
multifamily; collector-adjacent land also picks up churches and elementary schools; arterials
(small-city tier only) carry big-box retail, strip malls, drive-throughs, auto dealerships,
hotels — uses needing high visibility and 2+ acre parcels, zoned apart from downtown since the
1920s-30s specifically to separate car-oriented retail from pedestrian retail and housing.

---

## 3. Block & lot dimensions

| Parameter | Village | Small town | Small city |
|---|---|---|---|
| Downtown block size | n/a (too small for a block grid under ~2,000 pop) | ~300-400 ft/side | ~250-330 ft/side (300 ft standard reference) |
| Commercial lot width | n/a | ~25 ft (storefront bays divide into 25-30 ft segments even on combined lots) | ~25 ft (same convention persists) |
| Commercial lot depth | n/a | ~50-100+ ft | ~50-100+ ft |
| Residential lot size | 0.15-0.2 acre core, 0.25-1+ acre at farm edge (50-66 ft x 120-140 ft) | ~60 ft wide, 7,000-9,000 sq ft (~0.16-0.2 acre) | 6,000-8,000 sq ft; pre-war near-downtown lots often only 40-50 ft wide (narrower than later minimums → deliberate non-conformity/variance flavor) |
| Original platted core size | ~10-20 blocks (anchors a village that will reach 1,000-2,000 pop) | n/a | n/a |

---

## 4. Setbacks & building spacing

| Parameter | Village | Small town | Small city |
|---|---|---|---|
| Downtown building setback | 0 ft (contiguous 1-2 block core; freestanding w/ gaps outside it) | 0 ft — the single most consistent finding across every tier | 0 ft, zero-lot-line/party-wall |
| Downtown building height | 1-2 stories, rare 3-story anchor | 1-2 stories, occasional 3-story anchor (opera house, hotel, courthouse) | 2-4 stories, ~1-in-12 chance of a single "prestige tower" outlier (company-town landmark) |
| Residential front setback | n/a specific (assume small-town value) | derived from small-city figures below | 20-30 ft |
| Residential side setback | n/a specific | derived from small-city figures below | 6-15 ft, 7-7.5 ft most common (up to 15-20 ft outlier) |
| Through-lot rule | — | Fairfield IA: 35 ft rear setback on lots >95 ft deep; **both** street frontages of a through-lot get front-setback treatment, no reduced "cheat" rear setback | same rule, apply generically |

Already implemented in `DowntownGenerator.gd`: 3 m sidewalk setback, 8 m building-to-building
gap, 75%-of-street-width gravel alley behind each row — these track the small-town/small-city
zero-setback-at-street / gapped-alley-behind pattern reasonably well; the research above
suggests the *storefront* setback should trend toward 0 rather than 3 m if a more literal
small-town read is wanted in a future revision (flagging for that decision, not changing it here
since this phase is research-only).

---

## 5. Parking

| Parameter | Village | Small town | Small city |
|---|---|---|---|
| Primary supply | On-street along the 1-3 block core; no structured/large lots | Angled on-street parking on Main St both sides (stalls ~18-20 ft x 8.5-10 ft); at most 1-2 small municipal lots | 3-5 spaces/1,000 sq ft retail ratio; downtown = rear/side shared small lots, arterial/big-box = large front lots (1-2x building footprint) |
| Why | Population too small to justify formal lots | Municipal budget doesn't justify garages at this scale | Downtown parcels too narrow/valuable for front lots (would break zero-setback frontage); arterial visibility is itself a marketing requirement |

---

## 6. Downtown organization archetypes

Three recurring patterns, roughly evenly split at the small-town tier and still present at
village/small-city scale — pick one per generated settlement (weighted ~1/3 each, or biased by
founding-type flag if the generator models founding history):

1. **Courthouse square** — civic building centers a full block, storefronts face inward on all
   4 sides. (County-seat settlements only.)
2. **Park/green square** — a public park/green anchors downtown in place of a courthouse.
3. **Rail-corridor spine** — commercial street runs parallel to tracks, no central square at
   all. Common in pure railroad-founded towns (a plurality at the small-town tier); grain
   elevator sits on a side street near the corridor, physically separate from Main Street
   retail — **never place a grain elevator directly on the primary commercial street.**

---

## 7. Water siting, property value, and commercial intensity

**Founding-type-conditioned rule (applies at every tier):**

- If the settlement's founding type is **water/mill-based**: site downtown directly against
  the water body; make near-water blocks the oldest/densest; downtown grid elongates along the
  bank rather than forming a square (confirmed strongly at small-city tier with bluff
  topography, and at small-town river-mill towns).
- If founding type is **rail or inland/trail-based**: water (if present at all) sits at a
  middle distance from downtown as a recreational amenity that boosts nearby **residential**
  land value, not commercial value. Do not pull downtown toward water in this case.
- **Village tier only:** roll water-founding at **~1-in-3 to 1-in-4 probability**; when it
  occurs, place the core within about one block of the water (mill-site style), not merely
  "nearby." **Do not model a water-proximity residential value premium at the village tier at
  all** — it doesn't appear until the small-town/small-city scale.
- **Small-city tier quantified effect:** riverfront park investment correlates with roughly
  **2x the property-appreciation rate** of the surrounding settlement, with a real redevelopment
  arc of industrial/warehouse waterfront → partial conversion to park/promenade/condo, raising
  value specifically along the converted stretch, not uniformly.
- **Generator rule:** any river/lake-adjacent stretch should default to a legacy
  industrial/warehouse read on its oldest blocks, with an optional "revitalized" variant that
  converts a portion to park/promenade and raises nearby building height/density.

---

## 8. Topography / drainage archetypes

Three selectable presets, consistent across small-town and small-city tiers:

1. **Bluff-and-river-valley** — flood-exposed flat land directly on the river (oldest,
   historically industrial), rising bluff behind carrying prestige civic buildings, upland
   beyond for postwar residential.
2. **Dead-flat drained plain** — minimal relief, drainage via artificial ditch/tributary
   network, downtown grid forms a regular square (no natural constraint on its shape).
3. **Rolling hill country at a confluence** — genuine local relief; park/preserved land
   clusters specifically on the rough terrain near hills/confluence; surrounding farmland stays
   flat and fully cultivated to the town edge.

**Floodplain rule (all tiers):** mark any floodplain/relict-channel/oxbow polygon near a river
as park/undevelopable by default, not buildable land. Keep the lowest streets/blocks set back
at least one block from an adjacent creek/river (village-tier "Water Street" naming pattern is
a good generator flavor-text hook for this exact setback).

**Natural creek vs. engineered ditch:** treat these as two different setback categories —
engineered drainage ditches/tile systems are commonly *exempt* from riparian setback rules that
still apply to natural stream banks.

---

## 9. Civic/institutional building presence thresholds (by population)

| Population | School | Other civic |
|---|---|---|
| < 700 | No school building (bused to a consolidated district elsewhere) | Church(es) near-universal; post office assumed universal |
| 700-2,000 | One shared/consolidated school building, often named for a paired neighboring town | Grain elevator if rail-served; depot (possibly adaptively reused as museum/trail HQ) |
| 2,000-5,000 | One or two full school buildings, optionally + a separate parochial school | Carnegie library possible even at this scale (construction-era artifact, not population-linked) |
| County seat (any tier) | — | Courthouse — generate **once per county seat, not per settlement** |
| 6,000-10,000+ | Full public school district | 2-3 tier residential zoning; opera house/hall plausible |
| 30,000-50,000 | Full district + likely multiple schools | Distinct CBD zoning tier separate from arterial commercial; police station/courthouse plausible |

Non-residential building placement: grain elevators sit on a side street near the rail
corridor, never on Main Street; churches and depot/museum conversions sit within about one
block of Main Street; founder's-mansion-style building included at most once per settlement,
only if a named founder is modeled.

---

## 10. Station river / lake / pond / farm-drainage system

The full derivation is in `research/hydrology_drainage/_station_river_loop_design_notes.md` —
this section is the numbers table a generator should actually implement against. **The closed-
loop river geometry is this project's own engineering proposal** (no real-world precedent exists
for a meandering river forced into an exact closed loop); everything else in this section
summarizes cited real-world research.

**Core construction trick:** build the river centerline as a short Fourier series in the loop's
angle θ (0→2π, arc length s = θ·C/2π). Any sum of `A_k·sin(k·θ + φ_k)` terms with integer k is
*exactly* periodic over one full loop — it closes seamlessly with no manual seam-stitching.

| Feature | Value |
|---|---|
| River channel width | 45 m (range 40-55 m) |
| Meander wavelength | 524 m (k=6 harmonic, C/6); keep λ ≈ 10-14x channel width if width changes, pick nearest integer k = C/λ |
| Meander bends around loop | 12 apexes (6 wavelengths, alternating left/right) |
| Bend radius of curvature | 90-135 m (2-3x channel width) — minimum spline turn radius |
| Channel depth (if needed for gameplay) | ~2-3 m typical (W/15-W/20) |
| Recommended harmonic stack | k=6 primary (bends) + k=13 secondary at ~30% amplitude (bank irregularity) + k=1 slow drift at ~20-30 m amplitude (breaks 6-fold symmetry) |
| Amplitude budget | A1≈150 m, A2≈45 m, A3≈25 m; cap combined excursion at ~250 m off midline |
| Effective meander belt width | ~360 m (deliberately compressed from the real 6-18x ratio to leave room for all four zones on the 1,000 m floor — a conscious realism/gameplay trade-off) |
| Lake size | 1,000 m x 300 m (3.3:1 ratio; real range 2:1-5:1); site at a peak of the primary bend envelope, inside the Lake zone |
| Lake inlet/outlet necking | 100-150 m taper back to channel width at both ends |
| Pond count | 5-7, biased toward Residential/Farm-zone low ground; ~half styled as oxbow remnants, half as tributary-fed |
| Pond size | 60-150 m long axis |
| Pond cadence along river | every 500-1,000 m (echoes the primary meander wavelength) |
| Tributary creek (pond↔river) | 4-10 m wide, 60-300 m long, gently curved |
| Farm ditch grid | 120-200 m spacing, rotated independently of the river's meander direction (rigid-grid-vs-sinuous-river contrast is itself the "this is farmland" visual signal) |
| Farm ditch width | 2-4 m |
| Drainage routing hierarchy | field ditch → 2-4 named creeks per farm-zone stretch → main river or nearest pond (never ditch directly into the main channel) |
| Optional tile-drainage hint | faint parallel crop-color striping, 20-40 m spacing, perpendicular to ditches, for close-up/overhead views only |

**Town-siting cross-check:** site Downtown's oldest/densest core on the **outside of a bend**
(cut-bank side — higher, firmer ground); keep the inside/point-bar side low-density
park/floodplain/farmland. Setback buffer between river edge and buildings should be wider on
the point-bar side than the cut-bank side.

---

## 11. Building archetype selection (interior-generation pointer)

Full templates (room lists with size ranges + per-room furniture/fixture pools with count
ranges + placement notes) live in `research/building_catalog/residential/` (17 archetypes) and
`research/building_catalog/commercial_civic_farm/` (32 archetypes) — see each directory's
`_catalog_index.md` for the full table. **These ARE the generator's building-template data.**
The intended generation flow per building instance:

1. Pick a zone (Downtown/Residential/Farm) and a settlement tier (§1).
2. Pick an archetype from the matching catalog, weighted by that archetype's tagged tier(s)
   and era (villages/small towns skew toward older archetypes — farmhouse, foursquare,
   bungalow, Cape Cod, starter home, mobile home; small cities get the full spread including
   postwar/modern types and all three apartment archetypes).
3. Sample a footprint within the archetype's size range; place per the zone's block/lot/setback
   rules (§3-4).
4. For the interior: sample the archetype's room list (room count and each room's size within
   its range), then for each room sample its furniture/fixture pool (item presence and count
   within the noted ranges) — this is the actual runtime step that replaces loading a
   pre-authored unique interior, directly satisfying the "don't load the whole map into memory"
   goal.

Special-case archetypes to route differently: **Courthouse** generates once per county seat,
not per settlement. **Water Tower** and farm-scale **Grain Silo** are landmark structures with
no interior (skip step 4). **Pole Building/Machine Shed** and **Farm Equipment Shed** are
mutually exclusive per farmstead — pick one based on farm-size, not both.

---

## 12. Open questions / flagged for the next phase

- Which single tier (or per-zone blend) the station should actually target is not decided here
  — recommended default is small-town, but this is a design choice, not a research finding.
- Real tile-drainage and ditch spacing (9-30 m) is far finer than is legible at map scale; the
  120-200 m ditch grid above is already an abstraction, flagged as such in the hydrology notes.
- Several zoning-ordinance PDFs across all three tiers were unreadable by automated fetch
  (image-based/compressed); the affected figures fall back to well-corroborated generic
  small-town/US-suburban norms rather than town-verified numbers — noted per-figure in each
  tier's `_tier_summary.md`. A future pass with direct GIS/satellite tooling could tighten
  block-length and lot-size figures considerably.
