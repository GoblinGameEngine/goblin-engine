# Community Demographic Archetypes

Synthesis of demographic patterns across all 46 researched settlements (36 original Midwest
settlements + 10 Great Lakes south-shore additions from Part 3) into a small set of reusable
"community demographic archetype" categories. Each archetype gives a **numeric signature**
(growth trend, income, age skew, homeownership, employment mix, poverty) tight enough that a
generator can roll one archetype per settlement and derive every other demographic number from
it via the ranges below, rather than needing 8 independent random rolls per settlement.

Source data: `community_profiles/villages_demographics.md`, `community_profiles/small_towns_demographics.md`,
`community_profiles/small_cities_demographics.md`, and the per-town files in `community_profiles/`
and `../population_tiers/*/`.

## How to use this file

1. The generator rolls (or is assigned, for a story-relevant settlement) one archetype below.
2. Population trend, income band, age skew, homeownership band, and poverty band are then
   **sampled from that archetype's ranges**, not rolled independently — this keeps a generated
   settlement internally consistent (e.g. a "Declining Rust-Belt" roll should not also roll a
   90% homeownership rate or a 3% poverty rate; those belong to a different archetype).
3. Settlement **size tier** (village/small town/small city/gap-tier city) is mostly orthogonal to
   archetype — most archetypes appear at more than one size — with two exceptions noted below
   (College Town needs an anchoring institution feasible only at small-town-plus scale; extreme
   Micro-Resort is a size-locked special case, not a normal tier roll).

---

## 1. Stable Agricultural/Manufacturing Service Town
**The single most common archetype in this dataset — roughly half of all 46 settlements.**

The default "generic Midwest town" — a farm-trade-center or small manufacturing town whose
population has been flat-to-mildly-declining for decades but has not collapsed.

- **Population trend:** flat to mild decline, **-12% to +7%** per decade; occasionally mild
  growth (Napoleon OH +1.3%, Carroll IA +2.2%, Mount Pleasant IA +7.0%)
- **Median household income:** **$45,000-$77,000** (below-to-near state median)
- **Age skew:** aging population, median age **37-46**; %65+ typically **18-25%**; %under18
  **20-26%**
- **Homeownership:** moderate-high, **60-85%** where measured
- **Employment mix:** **Manufacturing is #1 or #2 in a strong majority of examples** (often
  15-35% of workforce), paired with Health Care & Social Assistance (#2 most often) and Retail
  Trade (#3); a few pure-farm-trade examples show Retail/Ag/Construction leading instead.
- **Poverty rate:** **9-20%**
- **Household size:** **2.2-2.4**
- **Bachelor's+:** low, roughly **10-27%** where found
- **Examples:** Buda IL, Wyanet IL, Toulon IL, Dysart IA, Clarksville IA, Wyoming IL, Roanoke IL,
  New Hampton IA, Hoopeston IL, Wapakoneta OH, Charles City IA, McCook NE, Kendallville IN,
  Bryan OH, Napoleon OH, Mount Pleasant IA, Carroll IA, Rice Lake WI, Litchfield MN, Fond du Lac
  WI, Michigan City IN, Manitowoc WI, Findlay OH, Hutchinson KS, Salina KS

**Sub-variant — Growing Ag/Rail Service Node** (Calmar IA +15.0%, Plainview NE +2.9%, Kearney NE
+9.8%): same employment/income signature but positive growth, usually tied to a highway/rail
junction role or a mid-size regional hospital/college pulling in population from a wider rural
catchment. Treat as the same archetype with the trend band shifted to **0% to +15%**.

---

## 2. Declining Rust-Belt Industrial
Legacy manufacturing/shipping town whose core economic driver has shrunk or left. **Two
severities** — treat as one archetype with a severity roll, not two archetypes, since the
underlying signature (income/poverty/homeownership all move together) is the same shape at
different magnitudes.

- **Population trend:** declining, **-3% to -12% per decade**, often **-15% to -52%** over the
  long run (multi-decade peak-to-now)
- **Median household income:** **Moderate severity $45,000-$60,000; Severe severity below
  $35,000** (Benton Harbor MI: $31,117, less than half the state median)
- **Homeownership:** **Moderate 48-60%; Severe below 40%** (Benton Harbor: 36.7%, Ashtabula:
  48.3%)
- **Poverty rate:** **Moderate 13-30%; Severe 40%+** (Benton Harbor: 40.1-42.6%, highest of all
  46 settlements)
- **Age skew:** mixed — can be young (Benton Harbor 32.2% under 18, only 10.6% 65+, consistent
  with out-migration of retirees/upwardly-mobile residents leaving a younger, poorer population
  behind) or middle-aged (Elyria, Ashtabula, Danville IL: median age 38-41, closer to the
  Stable-Town norm)
- **Employment mix:** legacy manufacturing still present but shrinking share; Health Care &
  Social Assistance has often overtaken it as the #1 sector; Accommodation & Food Service and
  Retail round out the top 3.
- **Household size:** not cleanly isolated in most examples; where found, **2.2-2.5**
- **Physical/building-condition signature (see also expansion notes):** vacant/derelict downtown
  storefronts, especially where a suburban mall preceded the decline (Elyria's 1967 Midway Mall);
  industrial waterfront/harbor infrastructure sitting un-redeveloped rather than converted to
  park/amenity use (Ashtabula's Superfund coal harbor, closed 2016).
- **Examples:** Danville IL (-11.6%/decade, 24.5-25.1% poverty), Elyria OH, Ashtabula OH, Benton
  Harbor MI (severe)

---

## 3. Growing Exurban/Bedroom Community
Commuter suburb of a larger metro, growing on housing demand and commute access rather than a
local economic engine.

- **Population trend:** strong growth, **+10% to +45%** (decade-or-longer window); Avon Lake OH
  +45.2% since 2000 is the strongest growth rate in the whole 46-settlement dataset
- **Median household income:** high, **$100,000-$125,000+**, well above state median
- **Age skew:** median age **44-45** — notably *older* than a "young family frontier" stereotype
  would suggest, consistent with an established/maturing suburb rather than raw new
  construction; %under18 ~23%, %65+ ~21%
- **Homeownership:** very high, **75-85%**
- **Poverty rate:** very low, **3-5%** — the lowest band of any archetype
- **Employment mix:** Health Care & Social Assistance and Professional/Scientific/Technical
  Services lead, with a manufacturing base often still present nearby (commuters plus local
  employers coexist rather than one replacing the other)
- **Bachelor's+:** high, **~49%+**
- **Household size:** **~2.5**
- **Examples:** Avon Lake OH (only fully-confirmed example in this dataset; treat as the
  reference case — no original-36 settlement matched this signature closely, which is itself
  the Part-3 finding: generic Midwest research under-sampled this archetype)

---

## 4. Stable County-Seat/Administrative Center
Population and economy anchored by government employment (county or state), which buffers
against both the growth swings of bedroom suburbs and the decline of industrial towns.

- **Population trend:** flat, **-2% to +2%** — the most stable trend band of any archetype
- **Median household income:** moderate, **$50,000-$65,000**
- **Employment mix:** Government (county or, for a state capital, state government) as the
  dominant or clearly top-3 sector — Jefferson City MO: state government alone accounts for
  14,223 jobs; small-village county seats (Toulon IL, New Hampton IA) show the same pattern at
  much smaller scale (courthouse + associated legal/administrative services)
- **Poverty rate:** moderate, **8-18%**, generally lower-volatility than industrial towns
- **Homeownership / age / household size:** track the Stable Agricultural/Manufacturing Town
  archetype closely — administrative function is best modeled as an employment-mix overlay on
  top of that base archetype rather than a fully separate demographic profile
- **Examples:** Jefferson City MO (capital), Fairfield IA, Mount Pleasant IA, Toulon IL, New
  Hampton IA (village-scale county seats)

---

## 5. College Town
Population and economy dominated by a resident college/university; requires an anchoring
institution, which in practice means this archetype needs at least small-town scale (6,000+) to
support a real campus — do not roll it for the villages tier.

- **Population trend:** flat to mild growth, tracks enrollment rather than the local economy;
  **-2% to +10%**
- **Median household income:** varies widely, **$50,000-$87,000** — driven by faculty/staff
  households averaged with low-income student households, so median income alone
  under-describes the town
- **Age skew:** the defining signal — **median age 24-34**, the youngest band of any archetype
  by a wide margin (Bowling Green OH 23.6-24.0, Mankato MN 27.7, Oberlin OH 27.4-28.0, Cape
  Girardeau MO 34.0)
- **Homeownership:** low, **~39-58%** (renter-heavy due to student population)
- **Poverty rate:** **artificially elevated, 16-29%** — this is a statistical artifact of
  counting low/no-income students as separate poverty-line households, **not** economic
  distress; see the false-positive warning in the expansion notes. Do not let a generator flag a
  College Town as "declining/distressed" on poverty rate alone.
- **Employment mix:** Educational Services dominant, **19-29%** of workforce (the single highest
  one-sector concentration of any archetype except severe company-towns), Health Care & Social
  Assistance typically #2
- **Bachelor's+:** high, **37%+** where measured (Mankato 37.6%, Oberlin 41.1%)
- **Civic-anchor pattern:** a college green functioning as a shared town/campus square with no
  fenced boundary (Oberlin's Tappan Square) is a genuine third downtown-organization preset
  alongside the courthouse-square and park-square patterns already documented for the small-towns
  tier — see expansion notes.
- **Examples:** Mankato MN (Minnesota State University), Cape Girardeau MO (SE Missouri State),
  Bowling Green OH (Bowling Green State University), Oberlin OH (Oberlin College), Holland MI
  (Hope College — hybrid, see archetype 6)

---

## 6. Lake-Resort/Tourism-and-Retiree
The archetype the original 36-settlement sample almost entirely missed (only Rice Lake WI hinted
at it) — added via Part 3. A town whose built environment and economy are sized for a seasonal
tourist/second-home population much larger than its year-round resident base.

- **Population trend:** flat to declining year-round population (**-6% to -13%** per decade is
  typical), which can coexist with a *growing* tourism economy — the generator should track
  resident population and tourism intensity as separate variables, not one "growth" number
- **Age skew:** bimodal by scale —
  - **Small resort villages** (pop. under 5,000): very old, median age **53-62** (South Haven
    56.2-61.7, Saugatuck 53.3-53.9), reflecting retiree in-migration plus year-round-population
    hollowing
  - **Larger resort-and-working cities** (pop. 10,000-30,000, e.g. Sandusky OH): more moderate,
    median age **36.5-39.5**, because a genuine service/hospitality workforce still lives
    year-round in the town
- **Income:** **bimodal, not one band** — small gentrified art-colony resorts skew very high
  ($67,000-$124,000, Saugatuck highest at ~$121,000-124,000 reflecting second-home-driven
  gentrification), while larger tourism-and-retiree cities can show only moderate income
  ($51,000, Sandusky) *alongside* high poverty, because the wealthy seasonal-homeowner
  population and the low-wage hospitality workforce are demographically separate groups living
  in the same town.
- **Poverty rate:** **11-26%** — the small gentrified villages sit at the low end (South Haven
  15.8%, Saugatuck 11.0%), the larger tourism-and-retiree cities at the high end (Sandusky
  25.6%) despite a thriving visible tourist economy — a second false-positive risk for a naive
  "prosperous because tourists" generator heuristic.
- **Homeownership / vacancy — the key differentiator from Growing Exurban:** nominal
  homeownership can look high (70-84%) but this **counts second/vacation homes as "owned,"**
  and the more diagnostic figure is **housing-unit vacancy**, which runs far above any other
  archetype: South Haven **45.6%** of all housing units are vacant (seasonal/vacation, not
  abandoned) — see expansion notes for the visual-signature distinction from rust-belt vacancy.
- **Household size:** small, **1.8-2.3**
- **Employment mix:** Accommodation & Food Services, Retail Trade, Arts/Entertainment lead; a
  base-layer of Manufacturing often persists underneath the visible tourist economy even in
  small resort villages (South Haven, Saugatuck both show manufacturing in their commute-based
  employment stats despite a Main-Street economy that reads as pure tourism/arts)
- **Extreme micro-scale sub-variant (Put-in-Bay OH, pop. 154):** the same archetype taken to its
  limit — year-round population **under 500** (outside all three standard tiers) with a
  **~65-70x seasonal population multiplier** (10,000+ peak-summer vs. 138-154 year-round).
  Standard ACS demographic percentages are not reliably available at this population size;
  model this sub-variant primarily via the population-multiplier mechanic and
  ferry/golf-cart-scaled infrastructure rather than via the numeric bands above. Saugatuck's more
  moderate **~3.5x** summer swell (865 → ~3,000) is a good "normal-strength" seasonal multiplier
  to contrast against Put-in-Bay's extreme case.
- **Examples:** South Haven MI, Saugatuck MI, Sandusky OH, Rice Lake WI (partial/original-36
  precedent), Put-in-Bay OH (extreme micro sub-variant)

---

## Cross-archetype notes for the generator

- **Two poverty-rate false positives exist** and should not be conflated with genuine economic
  distress: College Town (student-income artifact) and Lake-Resort-and-Retiree at the larger
  scale (workforce/homeowner demographic split). Before a generator labels a settlement
  "struggling," it should check homeownership rate + vacancy cause + income together, not
  poverty rate alone — this is the single clearest cross-cutting lesson from Part 3.
- **Homeownership rate alone is ambiguous** between Growing Exurban (75-85%, genuinely
  owner-occupied) and small Lake-Resort villages (70-84% nominal, but driven by vacation-home
  ownership with 30-45% overall unit vacancy). The generator should pair homeownership with a
  vacancy-rate and vacancy-cause variable (see expansion notes' "two causes of vacancy" flag) to
  distinguish them.
- **Manufacturing appears as a base-layer employer across nearly every archetype** except the
  severe end of Declining Rust-Belt (where it has substantially eroded) and the purest
  College-Town cases — even resort villages and the wealthy exurb (Avon Lake) show a
  manufacturing employment component. Do not treat "has some manufacturing employment" as
  diagnostic of any one archetype; treat its *rank and share* (dominant #1 vs. minor #4) as the
  useful signal instead.
- **Population trend and local income can move independently** — Sandusky and Avon Lake sit at
  nearly identical 2020 populations (~25,100-25,200) with opposite trends (declining vs. +45%
  growth) and a 2.4x income gap ($51k vs. $124k). Population size should not, by itself, drive a
  generator's affluence or decline parameters — archetype (founding/water-relationship type)
  matters more than raw population.
