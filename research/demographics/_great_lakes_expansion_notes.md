# Great Lakes South-Shore Expansion Notes

Part 3 of the demographics research task: which new settlements were added, which archetype gap
each fills, and physical-layout patterns specific to the Great Lakes south shore that the
original 36-settlement (mostly generic-Midwest) sample didn't capture.

## What was added and why

The original 36 settlements were real Midwestern towns grounded only loosely in "the Great
Lakes region" — most had no direct lake frontage, and the sample contained **no dedicated
college town, no dedicated lake-resort/tourism town, and no genuinely severe rust-belt decline
case** (Danville IL's -11.6%/decade was the closest, but nothing matched Benton Harbor's -52%
long-run collapse). Ten new settlements were added, all real places on the south shore of Lake
Erie, Lake Michigan, or (by extension of the search) inland but within the same
watershed/cultural region:

| New settlement | State | 2020 pop. | Archetype gap filled | Filed in |
|---|---|---|---|---|
| South Haven | MI | 3,964 | Lake-Resort/Tourism (small village scale) | `population_tiers/villages_500_5000/` |
| Saugatuck | MI | 865 | Lake-Resort/Tourism, arts-colony/gentrified variant | `population_tiers/villages_500_5000/` |
| Oberlin | OH | 8,555 | College Town | `population_tiers/small_towns_6000_10000/` |
| Benton Harbor | MI | 9,103 | Declining Rust-Belt Industrial, **severe** | `population_tiers/small_towns_6000_10000/` |
| Holland | MI | 34,528 | College Town + Tourism hybrid | `population_tiers/small_cities_30000_50000/` |
| Elyria | OH | 52,656 | Declining Rust-Belt Industrial, moderate (large scale) | `population_tiers/small_cities_30000_50000/` (stretches ceiling, same precedent as Carroll IA/Danville IL) |
| Avon Lake | OH | 25,206 | Growing Exurban/Bedroom Community | **new** `population_tiers/lakeshore_towns_10000_30000/` |
| Sandusky | OH | 25,095 | Lake-Resort/Tourism-and-Retiree, large scale | **new** `population_tiers/lakeshore_towns_10000_30000/` |
| Ashtabula | OH | 17,975 | Declining Rust-Belt/Harbor Industrial, moderate | **new** `population_tiers/lakeshore_towns_10000_30000/` |
| Put-in-Bay | OH | 154 | Lake-Resort, extreme micro-scale/seasonal | **new** `population_tiers/micro_resort_villages_under_500/` |

**Two new population-tier subfolders were created** because so many strong, well-documented
Great Lakes exemplars happened to land in population bands the original three tiers didn't
cover:
- `lakeshore_towns_10000_30000/` — a genuine gap between the small-towns (6,000-10,000) and
  small-cities (30,000-50,000) tiers that three separate, well-documented Lake Erie towns fell
  into (Avon Lake, Sandusky, Ashtabula), each illustrating a different archetype. Worth keeping
  as a real tier for future work, not just a one-off exception.
- `micro_resort_villages_under_500/` — a single deliberate outlier (Put-in-Bay) kept as a
  labeled special case, not blended into the villages tier's numeric parameters, because its
  built-form logic (tiny always-present core + massive seasonal overlay) doesn't follow the same
  founding-type rules as the villages tier's mainland farm-trade towns.

Elyria (52,656, ~5% over the small-cities ceiling) and Carroll IA / Danville IL from the original
36 (already over/under their tiers' nominal bounds) establish a consistent project precedent:
minor tier-boundary overshoots are acceptable when the settlement is otherwise a strong,
well-documented example.

## Great-Lakes-specific physical/demographic patterns not already captured in the tier research

These are new findings from Part 3 that extend or complicate the physical-layout patterns
already documented in the three original `_tier_summary.md` files:

1. **Vacant/derelict downtown storefronts as a distinct "building condition" variant.**
   The original small-cities tier research documented a "modernized storefront below, preserved
   historic facade above" pattern for healthy Great Lakes downtowns (Manitowoc). The declining
   rust-belt examples show the alternative end state: **genuinely vacant/boarded storefronts**,
   most cleanly attributable in Elyria to a single dated cause (the 1967 Midway Mall drawing
   retail out of downtown, with no revitalization narrative found — contrast with Manitowoc's
   active riverfront-condo revival). **Recommendation: add a "building condition" variant
   (occupied / modernized-adaptive-reuse / vacant-derelict) to the generator's downtown building
   model**, driven by archetype (Declining Rust-Belt → higher vacant-storefront probability) and
   by whether a specific "what killed downtown" event (mall, highway bypass, plant closure) is
   flagged for that settlement.

2. **Two causes of housing vacancy that look identical in a raw vacancy statistic but should
   render completely differently.** South Haven MI has 45.6% of all housing units vacant — but
   this is **seasonal/vacation-home vacancy** (well-maintained, high-value lakefront housing,
   occupied only in summer). Benton Harbor MI has meaningfully lower raw vacancy (~12.3%) but it
   is **abandonment/disinvestment vacancy** (low property values, genuine disrepair).
   **Recommendation: the generator should model vacancy as two separate variables — a "seasonal
   vacancy %" (Lake-Resort archetype, high-value/well-kept buildings) and an "abandonment
   vacancy %" (Declining Rust-Belt archetype, low-value/derelict buildings) — never one
   undifferentiated vacancy slider**, since the visual and gameplay implications are opposite.

3. **Marina/harbor infrastructure as a distinct downtown-adjacent building type**, not
   previously modeled: South Haven's 64-slip marina and pierhead lighthouse sit directly against
   the Main Street commercial core; Sandusky's Battery Park Marina occupies a former rail-yard
   site immediately off downtown. Distinct from generic "waterfront edge" — this is a specific
   building/infrastructure cluster (docks, harbormaster building, fuel dock, chandlery-type
   retail) worth its own small footprint template.

4. **Hand-cranked pedestrian chain ferry** (Saugatuck, crossing the Kalamazoo River to Mount
   Baldhead dune/Oval Beach) — small-scale, low-tech water-crossing infrastructure not present
   anywhere in the original 36-settlement sample. Worth a distinctive small building/mechanism
   type for resort-village variants.

5. **Real dune/hill relief directly at the water's edge** (Saugatuck's Mount Baldhead and the
   Saugatuck Dunes). Every topography pattern in the three original tier summaries describes
   flat-to-gently-rolling till plain; Saugatuck is a genuine exception and a useful alternate
   terrain preset specifically for the Lake Michigan dune coast (distinct from the Lake
   Erie/Lake Ontario south-shore towns, which remained flat coastal plain in every example
   researched, consistent with the original small-cities tier's findings).

6. **Twin-city river-divided inequality.** Benton Harbor and St. Joseph, MI sit on opposite banks
   of the same river mouth but have starkly different wealth profiles (Benton Harbor: $31k median
   income, 40%+ poverty; St. Joseph: much higher, not separately profiled here but noted as the
   documented contrast). This is a distinct **paired-settlement pattern** — not one town's water
   relationship but two towns whose fates diverged from a shared founding — worth a generator
   option for placing two demographically opposite settlements across a single river mouth or
   strait.

7. **Employer "donut" pattern.** Whirlpool Corporation's headquarters/campus sits immediately
   adjacent to Benton Harbor but technically within Benton Charter Township, outside city limits
   — the dominant local employer is present in the workforce but absent from the struggling
   city's own tax base. A useful mechanic for explaining "why is this town poor despite a major
   employer nearby" without requiring the employer itself to be failing.

8. **College-town square with no town/gown boundary** — Oberlin's Tappan Square (13 acres)
   functions simultaneously as the college green and the town's civic square, with downtown
   storefronts built directly against it. This is a **third civic-anchor/downtown-organization
   preset**, alongside the courthouse-square and park/green-square patterns already documented
   in the small-towns tier summary (which also noted a third "rail-corridor spine" pattern for
   railroad towns) — recommend the generator's College Town archetype default to this campus-green
   civic anchor rather than rolling a generic courthouse square.

9. **Inland-lake-plus-channel founding** (Holland, MI) — the town core sits on sheltered inland
   Lake Macatawa, connected to open Lake Michigan by a dredged channel, with a separate
   beach-park unit (Holland State Park / "Big Red" lighthouse) at the channel mouth several miles
   from downtown. A third water-founding archetype distinct from both direct-open-lakefront towns
   (Avon Lake) and river-mill towns already documented in the small-towns tier.

10. **Bay-head-plus-peninsula founding** (Sandusky, OH) — downtown sits at the head of a
    sheltered bay using a distinctive diagonal-avenue "Kilbourne Plat" grid, while the town's
    dominant tourism infrastructure (Cedar Point) occupies a separate lake-facing peninsula
    reached by a 1957 causeway. Tourism infrastructure here is spatially separated from the
    historic downtown rather than integrated into it — contrast with South Haven/Saugatuck,
    where the tourism-relevant buildings (marina, arts center) sit directly on the Main Street
    spine.

11. **Twin-core harbor-mouth layout linked by a working lift bridge** (Ashtabula, OH) — an
    upland "uptown" commercial/civic core is physically separated from a low-lying historic
    "Harbor" commercial district at the river mouth, connected by a drawbridge that is a literal
    traffic chokepoint tied to ship passage. Not seen in any of the original 36 river-mill towns
    (whose downtowns sit on one side of the water, not split across it).

12. **Industrial use directly on an otherwise-residential open shoreline** (Avon Lake, OH) — the
    now-decommissioned coal-fired Avon Lake Power Plant occupied a large stretch of open Lake
    Erie shoreline for a century, surrounded by residential bedroom-suburb development, rather
    than industry being segregated to a river mouth or harbor as in every rust-belt example
    already documented. Its 2022 decommissioning and planned park conversion is a clean,
    datable "industrial lakefront → public park" redevelopment case the generator could use as a
    late-stage variant of the growing-exurb archetype.

13. **Superfund/contaminated-waterfront remediation** (Ashtabula's coal-transshipment harbor,
    dredged and remediated 2012-2014) — a sourced industrial-harbor-to-cleaned-up-waterfront
    transition distinct from the simpler industrial-to-recreational conversions already
    documented for Mankato/Manitowoc; useful as a "still mid-remediation" intermediate state
    between "working industrial harbor" and "converted amenity waterfront."

14. **Heated downtown snowmelt sidewalk/street infrastructure** (Holland, MI) — a genuinely
    unique cold-climate tourist-town infrastructure detail (heated pavement under the historic
    core, aimed at keeping the winter tourist downtown walkable) not found in any other
    settlement researched across the whole 46-town project.

15. **Extreme seasonal population multiplier as a quantified mechanic.** Saugatuck's ~3.5x
    summer population swell (865 → ~3,000) is a normal-strength example; Put-in-Bay's ~65-70x
    swing (138-154 year-round → 10,000+ peak summer) is the extreme case. Recommend the
    generator expose "seasonal population multiplier" as an explicit tunable for the Lake-Resort
    archetype, with Saugatuck and Put-in-Bay as the two calibration anchors.

16. **Poverty-rate false-positive risk**, already flagged in `_demographic_archetypes.md`:
    Oberlin's 16.1% poverty rate (student-income artifact) and Benton Harbor's 40%+ rate
    (genuine economic collapse) could trigger the same naive "declining town" flag from poverty
    rate alone. The generator should cross-check homeownership rate, median income, and
    vacancy-cause together before classifying a settlement as economically distressed.

## Net takeaway for the generator

The Great Lakes south shore is not demographically or physically uniform even within a single
archetype — a "declining rust-belt" roll can mean anything from Ashtabula's moderate, still-intact
uptown (poverty ~30%, homeownership ~48%) to Benton Harbor's severe collapse (poverty 40%+,
homeownership 37%), and a "lake resort" roll can mean anything from Saugatuck's gentrified art
colony (median income $121k+) to Put-in-Bay's ferry-only seasonal extreme. The archetype file's
numeric ranges are deliberately wide for this reason — treat within-archetype variation (via a
"severity" or "scale" sub-roll) as a first-class generator parameter, not noise to average away.
