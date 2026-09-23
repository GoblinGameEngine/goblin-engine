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

## 13. Residential yard/lot contents

Full templates: `research/lot_contents/` (3 era/setting base files + 2 income-modifier layers +
1 cross-cutting climate layer + `_lot_contents_index.md`, which also carries the full
building-archetype-to-lot-file cross-reference table — use it directly, not reproduced here).

**How to layer (generation order):** pick one era/setting base file
(`prewar_intown_lots.md` / `postwar_suburban_lots.md` / `rural_farm_adjacent_lots.md`) per the
house archetype already chosen in §11 — the cross-reference table gives the mapping — then
apply an income-modifier file (`low_income_lots.md` / `upper_middle_income_lots.md`) only if
the household's income roll (§14) is an outlier; the base file's own middle already represents
the unmodified case. Layer `great_lakes_climate_items.md` on top of either using the lot's era
(storm-window/basement probabilities) and setting (woodpile/snow-equipment probabilities).

**Load-bearing findings:**

- **Garage/driveway flip is the single biggest structural fact**: pre-war narrow lots hide the
  garage on a rear alley (~70-85% where the alley is intact — alleys predate mass car
  ownership); postwar lots have no alley, so ~80-90% have an attached garage/driveway apron
  dominating the front facade instead. This should drive most of the front-yard difference
  between the two base era files.
- **Pool type, not pool presence, is the sharpest income signal in the whole lot-contents
  catalog**: only ~8% of households have any pool (59% in-ground/41% above-ground split);
  in-ground (~$66k avg) skews `upper_middle_income_lots.md`, above-ground (~$1-6k) is the
  accessible option for low/middle tiers. Sample a code-compliant pool fence at ~90%+ wherever
  any pool exists, regardless of tier — this is a real safety-code requirement, not a
  discretionary choice.
- **Clotheslines are the cleanest income+era dial available**: ~35-45% at low-income/rural,
  ~3-8% at upper-middle-income. Several Great Lakes states (IL, IN, WI) have real "right to
  dry" laws specifically because wealthier subdivisions tried to ban the practice.
- **Vegetable gardens follow a U-shape by income**, not a simple decline: high at rural
  (~55-70%, production tradition) and low-income (~35-50%, budget motivation) tiers, a dip at
  ordinary postwar-suburban middle income (~25-40%), partial recovery at upper-middle
  (~30-40%, reframed as a hobby "kitchen garden").
- **Backyard chickens are a distinct, ordinance-bound in-town exception**, separate from the
  farm-zone chicken coop already in `building_catalog`. Typical Midwest municipal caps: 4-8
  hens, no roosters, 10-25 ft/25-50 ft setbacks. Sample low (~5-10%) on generous-lot in-town
  properties, well below the rural tier's ~30-45% unregulated rate.
- **Driveway material is an era+setting+income triple signal**: gravel (rural, long driveways);
  concrete ribbon strip (pre-war alley aprons); asphalt/concrete apron (postwar suburban);
  stamped concrete/pavers (upper-middle-income only).
- **Mailbox style** ties into the existing street-furniture system: wall/porch-mounted
  (pre-war in-town), single post-mounted curbside (postwar suburban, USPS-standard 41-45 in
  height), roadside post box or cluster box unit/CBU (rural).
- **Weak spot, flagged honestly by the research**: lawn ornaments/seasonal decor had no
  citable quantitative source — treat as low-confidence/flavor-only, not a weighted pool.

---

## 14. Interior demographic weighting + settlement economic condition

Full framework: `research/interior_contents_why/` (`residential_demographic_framework.md`,
`residential_why_notes.md`, `commercial_civic_farm_economic_condition.md`, `_synthesis.md`).
**Core principle: this layer modifies the §11 base pool's weights — which end of a stated
range, which optional items are present, what condition/quality descriptor to render — it never
replaces or adds a different room/item set.**

**Residential — 3 independently-rolled dimensions, applied in this order:**

1. **Household structure** (single / couple / family-with-kids / retiree-empty-nester /
   multigenerational-roommates) — rolled first because it gates room *use* before any item
   sampling (a bedroom becomes a kid's room vs. home office vs. craft room vs. second primary
   bedroom depending on this roll).
2. **Income tier** (low / middle / upper-middle) — weighted by the settlement's population
   tier (villages skew low/middle; small cities carry the full spread) and, per §15 below,
   nudged one step by the settlement's economic-condition roll. Sets item count-within-range
   bias, optional-item presence probability, and a quality/wear/clutter descriptor for every
   placed item.
3. **Construction era** (pre-1945 / 1945-1980 / 1980-present) — usually just the archetype's
   stated era from §11, with an optional renovation roll bumping specific rooms to a later
   effective era independent of the shell.

New diagnostic items worth sampling alongside the base pools: chest freezer (rural/bulk-buying,
~50% national ownership), home gym equipment (~68% ownership at $100k+ income), religious/
cultural iconography, multiple TVs/game systems in kids' rooms, plastic slipcovers, gun
cabinet/safe, hobbyist workshop buildout.

**Commercial/civic/farm — one settlement-level roll, applied to every building in that
settlement:** Thriving / Stable-but-plain / Struggling-Rust-Belt, optionally combined with a
Lake-resort/tourist-adjacent modifier flag. This is rolled **once per settlement, not once per
building** — a town's economic condition is a shared fact every Main Street business
experiences together. Dedicated condition tables exist for 10 priority archetypes (hardware
store, diner/cafe, general store, small grocery, church, library, town hall, bank branch, gas
station, bar/tavern); the same thriving=fuller/newer, struggling=thinner/older/deferred-
maintenance, resort=seasonal-stock-layered-on-top pattern generalizes to the other 22 by
analogy.

**Why two separate rolls, not one:** household income and settlement economic condition are
correlated in reality but not identical — even a struggling town has some solidly middle-income
households, and even a thriving town has some low-income ones. Bias the household income-tier
distribution one step toward the settlement's condition (Struggling → more low/fewer
upper-middle; Thriving → the reverse) rather than hard-locking every household to match — this
avoids both an implausibly uniform "everyone in this town is poor" result and an equally
implausible "lavishly stocked hardware store on a boarded-up Main Street" result.

---

## 15. Community demographic archetypes

Full data: `research/demographics/` — `_demographic_archetypes.md` (6 archetypes with numeric
signatures), `_great_lakes_expansion_notes.md` (16 Great-Lakes-specific physical patterns),
`community_profiles/` (46 settlements total: the original 36 from §1's tiers + 10 new Great
Lakes south-shore additions). Two new population-tier folders exist alongside the original
three: `population_tiers/lakeshore_towns_10000_30000/` (a real gap between small-town and
small-city scale — Avon Lake OH, Sandusky OH, Ashtabula OH) and
`population_tiers/micro_resort_villages_under_500/` (Put-in-Bay OH, a labeled extreme outlier).

**Roll one archetype per settlement; sample every other demographic number from that
archetype's range, not independently** — this is what keeps a generated settlement internally
consistent (a "Declining Rust-Belt" roll should not also roll 90% homeownership).

| Archetype | Share of researched sample | Defining signal |
|---|---|---|
| Stable Agricultural/Manufacturing Service Town | ~half — the default "generic Midwest town" | Manufacturing #1-2 employer; flat-to-mild-decline population (-12% to +7%/decade); income $45-77k |
| Declining Rust-Belt Industrial (moderate/severe sub-bands) | — | Population -3% to -12%/decade (up to -52% long-run); severe = income <$35k, homeownership <40%, poverty 40%+ |
| Growing Exurban/Bedroom Community | — | Strongest growth of any archetype (+10% to +45%); income $100-125k+; poverty only 3-5% |
| Stable County-Seat/Administrative Center | — | Government employment dominant; flattest population trend of any archetype (-2% to +2%) |
| College Town | — | Median age 24-34 (youngest by a wide margin); **poverty rate 16-29% is a student-income statistical artifact, not distress** — do not flag as declining on poverty alone |
| Lake-Resort/Tourism-and-Retiree | Nearly absent from the original 36; added via Great Lakes expansion | Bimodal income; housing vacancy far above any other archetype (up to 45.6%, South Haven) — but see the vacancy-cause distinction below |

**Two cross-cutting traps the generator must guard against** (both real findings, not
speculation):
1. **Poverty-rate false positives**: College Town (student-income artifact) and larger
   Lake-Resort cities (workforce/homeowner demographic split) can both show high poverty
   without genuine economic distress. Check homeownership + vacancy-cause + income together
   before labeling a settlement "struggling" — never poverty rate alone.
2. **Two causes of housing vacancy that look identical in a raw percentage but must render
   oppositely**: seasonal/vacation vacancy (Lake-Resort archetype — well-maintained, high-value,
   empty only off-season) vs. abandonment/disinvestment vacancy (Rust-Belt archetype —
   low-value, genuine disrepair). Model as two separate variables, never one vacancy slider.

**New building-condition variant recommended by this research** (not yet in §11's generation
flow — flagged for the next phase): downtown buildings should carry an
occupied / modernized-adaptive-reuse / vacant-derelict condition state, driven by the
settlement's archetype and, optionally, a specific "what killed downtown" flag (mall,
highway bypass, plant closure) for Rust-Belt settlements.

---

## 16. Station elevation design (closed-loop, correlated with the river)

Full derivation: `research/hydrology_drainage/_station_elevation_design_notes.md` (proposal)
and `real_elevation_data.md` (real-world grounding). **This is this project's own engineering
proposal**, exactly like §10's river geometry — no real precedent exists for a heightfield
forced into an exact closed loop. It is deliberately built to **reuse the river's own harmonic
and phase rather than being tuned independently**, so cut-bank (high) and point-bar (low) sides
stay automatically correlated with the river's bends everywhere around the loop.

**Core trick (same as §10):** any smooth function of `(x − y(θ))`, where `y(θ)` is the
river's already-periodic centerline from §10, is automatically periodic in θ too — no separate
harmonic series needed for the cross-section shape itself.

| Parameter | Value | Grounding |
|---|---|---|
| Primary bluff harmonic | k=6, reused from the river's own y(θ) term, same φ1 | Not an independent choice — required for automatic cut-bank correlation |
| Cross-section shape | `tanh((\|x−y(θ)\|−d0)/L_bluff)` | tanh chosen specifically for genuinely flat terrace/upland shoulders (a sine term would roll back down instead) |
| Bend-size variability | reused `(1+0.3·sin(2θ+φ4))` envelope from the river's A1(θ) | Same mechanism, same φ4 — bends don't read as stamped copies |
| Zone-scale tilt | k=1, phased to trough at the Lake zone's center | Lowest available harmonic; sets a gentle regional low near the water without competing with the k=6 bluff pulses |
| H_bluff_base (bluff height) | **18 m (~59 ft)** | Compressed from the real 21-55 m (70-180 ft) town-relief range for buildable street grades — same kind of trade-off as §10's meander-belt compression |
| Bend-to-bend bluff range | ~13-23 m (43-77 ft) | From the reused (1±0.3) envelope |
| d0 (flat low-terrace setback) | 80 m | Genuine flat riverside frontage before the climb starts, matching the real "flat land directly along the river" pattern |
| L_bluff (transition run) | 75 m | ~24% max grade at the steepest point, easing to flat within ~225 m |
| Total bluff footprint (d0+3×L_bluff) | ~305 m | Tight against the worst-case ~250-300 m cut-bank clearance left by §10's river excursion cap — flagged as genuinely tight, accepted as realistic (real bluff towns are tight here too) |
| Z1 (zone-scale Lake-low tilt) | 10 m | Kept under half of H_bluff_base so it reads as background, not competing relief |
| Bluff pulses per loop | 6 (cut-bank/high) + 6 (point-bar/low) = 12 total | Locked to the river's own 12 bend apexes |
| Real relief range this is grounded in | 70-180 ft (21-55 m) town-specific; 250 ft (76 m) regional valley-wall ceiling (Mankato); 80 ft (24 m) engineered bluff (Salina) | `real_elevation_data.md`, 9 settlements across the 3 archetypes in §8 |
| Dead-flat archetype real slope reference | ~4 ft/mile (~0.076%), Great Black Swamp | Confirms Farm/Lake zone baseline should read as visually flat, not merely "flatter" |

**Per-zone flat-ground check (already verified, no further compression needed):** Downtown
gets a flat low terrace on the cut-bank riverside plus flat upland beyond the bluff for civic
buildings; Residential sees the *least* relief-driven land loss of the four zones (it's mostly
flat upland terrace, the real-world siting for postwar subdivisions); Farm keeps the majority
of each ~524 m bend wavelength and ±500 m floor half-width genuinely flat for the ditch grid;
Lake stays flat by construction (the Z1 tilt's minimum sits there) with only a moderate local
bluff pulse on one shore, matching how real lakes often have one bluffier and one flat/marshy
shore.

---

## 17. Population-scale illusion techniques (from open-world game design research)

Full research: `research/game_scale_reference/` — `gta_series.md`, `fallout_series.md`,
`elder_scrolls_series.md`, `witcher_3.md`, `other_open_world_rpgs.md`,
`elevation_verticality_techniques.md`. The station will never simulate 100,000 people; these
are the concrete, sourced techniques other successful open-world games use to make a much
smaller actual simulation *feel* like a large population — several backed by primary
developer sources (Bethesda's Joel Burgess GDC talks, Rockstar's Dan Houser/Aaron Garbut/Rob
Nelson on-record interviews, Warhorse's Tobias Stolz-Zwilling/Prokop Jirsa), not just fan
inference.

**State the population gap in-fiction rather than hiding it.** Fallout's core technique is
narrative, not technical: nuclear war explains a "big" settlement having 13-40 people. The
station's own premise (built for ~100,000, never fully filled, or in slow decline) should be
stated in-world — at least one text source (terminal, sign, NPC line) per major district
acknowledging built capacity vs. actual occupancy — so a sparse population reads as intentional
worldbuilding, not a shortcut.

**Enterable-interior budget: ~1-2% of total exterior buildings**, allocated by gameplay
function (every shop-type the player actually needs) not geographic coverage — matches GTA V's
inferred ratio. Everything else is a non-enterable shell.

**NPC "aliveness" budget: one NPC covers 2-4 locations via a scheduled routine, not one NPC
per location.** Borrow Fallout/Skyrim's Package+Schedule+Sandbox pattern directly: 2-3 daily
waypoints (home/work/social) plus local idle behavior between them, 4-6 total daily states
synced to environment cues (lit windows, shop-open flags). This is the well-documented Radiant
AI "sweet spot" — Bethesda's own more ambitious, fully autonomous Oblivion-era version was cut
back pre-launch for being unpredictable and expensive; don't over-build past this point.

**Build one shared modular kit per building/district type; vary arrangement and palette, not
geometry.** Bethesda's Joel Burgess (GDC 2013/2014, primary source): a Fallout 3 kit of as few
as 4 pieces, and just 2 kit artists supporting 8 level designers across 400+ Skyrim dungeon
cells — size a kit's sub-piece catalog proportionally to its reuse count (a kit reused 200+
times needs ~50 pieces; one used twice needs only ~7). **Caveat**: Rockstar's own Aaron Garbut
explicitly disputes this characterization for GTA V specifically ("we've simply not copied
buildings around the map") — treat kitbashing as confirmed-for-Bethesda, disputed-for-Rockstar,
and default to it anyway on our own production-capacity grounds regardless of which is literally
true for either studio.

**Split NPCs into a foreground tier (full schedule, unique dressing) and a background/crowd
tier (shared appearance pool, no real schedule)** — Witcher 3's approach to making Novigrad's
public spaces read as crowded without simulating more than a few hundred real entities.

**Anchor each district with one unmistakable landmark, not building density** — Diamond City's
stadium shell, Novac's dinosaur statue. One strong non-modular landmark per named district does
more for "this place is real" than raw building count.

**Push vertical/facade layering over footprint to sell size** — a narrow, tall, densely-packed
silhouette along a tight street reads as "more city" than the same floor area spent wide and
low. Maps directly to stacking visible (non-enterable) deck levels and habitation-block facades
above/below the walkable path.

**Compress macro-scale spacing between districts, not their internal detail** — Kingdom Come's
"adjusted realistic map" technique (named developers: Tobias Stolz-Zwilling, Prokop Jirsa):
keep each settlement's internal layout faithful to its type, but shrink the "dead space"
between settlements — realistic emptiness reads as a bug, not scale.

**Avoid the Whiterun failure mode**, a sourced academic finding (Vella & Bonello Rutter
Giappone, DiGRA 2018): Whiterun's silhouette was found to primarily recall Edoras from the LOTR
films — a striking visual reference built first, a functionally-thought-through city built
second. If the station's UI/lore claims a district is a "capital" or "major hub," its physical
design (silhouette, gate scale, visible district count) needs to read as commensurately
important on its own, independent of any stated population number.

**Elevation as a scale technique — the station's own physical constraint changes the playbook**
(full detail in `elevation_verticality_techniques.md`, which was written after directly reading
`StationRingBuilder.gd` to confirm the constraint): unlike every surveyed game, the station has
a **hard ceiling height** limiting available vertical relief — mountains can't rise as high as
the art team wants. Recommended approach:
- Budget relief as a small fraction of `ceiling_height`, not of floor footprint — the binding
  constraint is vertical clearance under the next deck, not linear map span.
- Concentrate most relief into 1-2 "ridgeline" arc-segments (mirroring §16's bluff pulses)
  rather than uniform gentle rolling everywhere; target **80-90% of the ring's circumference
  staying within a shallow, easily-buildable grade band**, with the remaining 10-20% carrying
  the concentrated relief.
- Use elevation specifically to block sightlines *along* the ring's circumference (not just
  across its width) — since the loop is closed, a player could otherwise see very far around
  the curve; a raised feature every so often prevents seeing more than one or two districts
  ahead, making the 3,142 m loop feel longer to walk than its true distance (directly
  reproducing BOTW's "point of interest visible, path never straight" technique and Skyrim's
  documented "inflates the game space" effect).
- Hand-author the macro relief skeleton (where ridgelines sit, how tall); reserve procedural
  noise for surface-detail texture only — both Skyrim and Horizon Zero Dawn documented this
  same hand-macro / procedural-detail split, and both explicitly avoided pure-procedural
  macro-terrain as reading "generic."

---

## 18. Open questions / flagged for the next phase

- Which single tier (or per-zone blend) the station should actually target is not decided here
  — recommended default is small-town, but this is a design choice, not a research finding.
- Real tile-drainage and ditch spacing (9-30 m) is far finer than is legible at map scale; the
  120-200 m ditch grid above is already an abstraction, flagged as such in the hydrology notes.
- Several zoning-ordinance PDFs across all three tiers were unreadable by automated fetch
  (image-based/compressed); the affected figures fall back to well-corroborated generic
  small-town/US-suburban norms rather than town-verified numbers — noted per-figure in each
  tier's `_tier_summary.md`. A future pass with direct GIS/satellite tooling could tighten
  block-length and lot-size figures considerably.
- §16's elevation proposal leaves a genuinely tight ~305 m footprint against a ~250-300 m
  worst-case clearance directly at a bend apex under Downtown — workable per the research's own
  check, but worth validating once real block/street geometry is generated, not just reasoned
  about on paper.
- §17's game-scale research hit search-tooling limits late in the session (WebSearch quota
  exhaustion, general search engines blocking automated fetch) — Google Scholar and direct-URL
  fetches filled the gap well, but a few items remain explicitly unsourced rather than guessed:
  GTA V's total building count and exact facade-kit piece count, exact Diamond City/Novac NPC
  counts, absolute km²/sq-mile figures for BOTW/Witcher 3/RDR2/KCD/Horizon Zero Dawn, and
  confirmation either way of whether any surveyed studio used erosion-simulation terrain tools.
- §15's two new population-tier folders (`lakeshore_towns_10000_30000/`,
  `micro_resort_villages_under_500/`) are real, well-documented gaps worth keeping as ongoing
  tiers rather than one-off exceptions — not yet integrated into §1-9's tier tables above,
  which still only cover the original three tiers explicitly.
- The building-condition variant (occupied/modernized/vacant-derelict) and the two-cause
  vacancy model flagged in §15 are new concepts this research surfaced but that don't yet have
  a "how the generator actually applies this" flow written the way §11/§14 do for buildings and
  their contents — worth a short follow-up synthesis pass before Phase 2 implementation.
