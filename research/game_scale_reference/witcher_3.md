# The Witcher 3: Novigrad's Density Illusion vs. Velen's Honest Smallness

Focus: Novigrad as the "largest city in the North," and Velen's scattered
hamlets as the contrasting small-settlement case. Research goal: how CD Projekt
Red makes a ~30,000-population city feel dense and real with an actual simulated
population several orders of magnitude smaller, and how they handle honestly
small settlements without them feeling empty.

---

## 1. Novigrad's implied vs. actual scale

The Witcher 3's in-fiction claim for Novigrad is unambiguous: dialogue and lore
describe it as **the largest and richest city in the North, with a population
approaching 30,000**. That is explicitly stated in-world, not just implied —
Novigrad is framed as bigger than Oxenfurt, bigger than Vizima, a true
metropolis.

The *built* city obviously does not contain 30,000 simulated inhabitants. Hard
NPC headcount figures for Novigrad specifically are not published by CDPR in a
clean single number the way UESP tracks Skyrim, but the achievable, well
documented proxy is: **Novigrad has around 2,000 openable doors** — i.e. roughly
2,000 distinct addressable interior/building entry points across the whole
city, the large majority of which lead to shallow, non-simulated pocket spaces
(a single room, a shop counter) rather than full households. Actual walking,
scheduled, named NPCs number in the hundreds at most, with the visible "crowd"
made of a much smaller pool of background character models than the headcount
implies (see verticality/crowd techniques below). So — like Skyrim — the
implied-to-actual population ratio is on the order of **100:1 to 1,000:1+**,
closed entirely through urban-design techniques, not brute-force character
count.

## 2. How density is faked: urban-planning theory, not raw density

CD Projekt's own design approach to Novigrad, as documented in design-analysis
writeups, explicitly borrowed **Kevin Lynch's "Image of the City" urban-theory
framework** — the same five-element vocabulary urban planners use to describe
how real cities are legible to the people navigating them:

- **Paths** — the streets/canals themselves; Novigrad's paths are deliberately
  *winding, narrow, and irregular* (not a grid), because the city imitates
  organic, unplanned medieval growth rather than a centrally-planned city.
- **Nodes** — key junctions and public squares (Gildorf, Glory Lane) where
  paths converge; these get disproportionate visual investment (fountains,
  markets, gallows, public performances) because players orient themselves
  by these landmarks.
- **Edges** — city walls, the river, canal boundaries — hard boundaries that
  divide the city into legible chunks.
- **Districts** — distinct character zones (the docks, the slums, the
  wealthy quarter around the bank) each with a consistent material/color
  palette and building type so players can tell at a glance "which part of
  the city" they're in.
- **Landmarks** — singular, tall, visually unique structures (the Temple of
  the Eternal Fire, Vivaldi Bank's vaulted clerestory hall) that break the
  skyline and serve as long-distance navigation anchors, deliberately made
  *architecturally distinct* from the repeated residential building stock
  around them.

Because medieval cities historically grew without centralized zoning, CDPR
leaned into *irregularity itself* as the design tool — narrow, crooked streets,
buildings of inconsistent height and setback crowded close together, and
blind alleys — which reads as "old and dense" even without a large raw
building count, because irregularity is what a real organically-grown city
looks like and a regular grid reads as small/planned/empty by comparison.

Novigrad's visual references were **medieval Amsterdam** (canals, narrow
gabled townhouses) **with touches of Venice** — CDPR did not copy these
1:1, but used them for tall, narrow, closely-packed building forms that
maximize apparent density per unit of footprint, since a narrow-and-tall
building silhouette reads as "more city" per square meter of ground plan
than a wide, low building does.

## 3. Layered facades and background-vs-foreground NPCs

Novigrad (and CDPR's crowd tech generally in REDengine) relies on a
two-tier NPC/asset strategy, evident from both design writeups and asset
analysis of the shipped game:

- **Foreground/interactive NPCs**: fully modeled, individually scheduled
  (see below), with unique or semi-unique appearances, used for quest givers,
  shopkeepers, guards, and named background characters players are likely
  to approach.
- **Background/ambient crowd NPCs**: reuse a much smaller pool of
  "single-appearance-file" background character models with deliberately
  lower-fidelity LOD and simplified lighting response, cheap enough to
  populate a street in bulk. These give the *impression* of a crowd density
  the game could never afford if every crowd member were built to
  foreground-NPC fidelity.
- **Facade stacking**: multi-story building fronts are pushed close together
  along narrow streets, with visible upper floors, rooftops, chimneys, and
  laundry-lines layered above street level that the player can see but not
  enter — vertical layering of non-simulated detail standing in for the
  building volume a real city block would have, exactly analogous to
  Skyrim's unenterable background architecture but leaned on harder because
  Novigrad's claimed scale is much larger.

Novigrad's day/night ambient schedules (shops shuttering at night, NPCs
moving from market stalls to taverns to homes, guards changing patrol
patterns) are the same *radiant-schedule* concept Elder Scrolls popularized —
CDPR's version is described in design retrospectives as giving Novigrad "a
day-night routine that helps it feel lived in and real," applied to a much
larger nominal population than Skyrim's cities, which is precisely why the
foreground/background NPC split matters more here than it does in Skyrim:
CDPR could not afford full simulation depth on every one of the "thousands"
of implied inhabitants, so only a curated subset get real schedules while
the rest are crowd dressing.

## 4. Velen: the honest small-settlement case

Velen is the direct architectural opposite of Novigrad, and useful as a
contrasting reference point for a generator's smallest settlement tiers:

- Velen is explicitly modeled after **rural Polish villages and countryside**,
  but — like Novigrad's Amsterdam/Venice references — CDPR never copied real
  places 1:1; references were inspiration, and the actual layout was driven
  by gameplay flow and level design first.
- Velen's world-building process worked **terrain-first**: the location team
  placed mountains, rivers, and lakes where they made narrative/geographic
  sense, and only then decided where villages would logically sit relative to
  that terrain — a "settlements follow geography" placement rule, not
  "geography follows settlement placement."
- Velen's hamlets (Blackbough, Midcopse, and others) are deliberately **tiny
  and not hubs of activity** — the game does not try to make them feel like
  scaled-down cities. Instead it leans entirely into **environmental
  storytelling**: scorched earth, "No Man's Land" signage, abandoned houses,
  and visible war damage communicate the hamlet's state (dying, war-ravaged,
  barely surviving) without any NPC count or dialogue needed. A convincing
  small settlement, in this model, doesn't need bustling activity — it needs
  *legible visual evidence of its own history and current condition*.
- This is a deliberate contrast with Novigrad: Velen never pretends to be
  bigger than it is. Its believability comes from matching *tone and detail
  density* to its claimed small size, rather than from any density-faking
  trick — the opposite lesson from Novigrad, but equally load-bearing for a
  generator that needs both large and small settlement tiers to feel
  correct at their own scale.

## 5. Academic critique: Novigrad through a phenomenology-of-space lens

The Kevin Lynch urban-legibility framework already covered above (section 2)
is CDPR's own stated design tool. A separate, independent academic source —
**Vella, D. and Bonello Rutter Giappone, K., "The City in Singleplayer
Fantasy Role Playing Games" (DiGRA 2018)**, which also supplies the Whiterun
critique in `elder_scrolls_series.md` — analyzes Novigrad through a
different lens (Christian Norberg-Schulz's phenomenology of built space:
centring, inside/outside, movement, encounter) and reaches conclusions that
both confirm and complicate the "density illusion" story above:

- **Centring confirms the deliberate placement claim.** The paper notes
  "Novigrad stands at the apex of the roughly triangular expanse of the land
  of Velen, at the confluence of the map's two main waterways and at the
  terminus of all its paths" — an independent, geometry-level confirmation
  that Novigrad's map position is engineered to be the gravitational centre
  of the whole game world, not an accident of where a "big city" happened to
  be placed.
- **Inside/outside is academically read as an active exclusion mechanism,
  not just flavor.** "Novigrad is a closed city, locked down in response to
  the destabilisation caused by the Nilfgaardian Empire's military expansion
  ... Geralt is also excluded — he must obtain official papers before the
  guards posted at the gates will allow him to enter the city ... his
  newly-obtained privilege is remarked upon as such by the refugees who have
  still not been granted that right: the mechanism of exclusion remains in
  practice." This reframes the walls-and-gates trick less as scale-signaling
  set dressing and more as a *narrative-mechanical* device: the border
  itself is doing storytelling work (who gets in, who doesn't) independent
  of how large the city behind it actually is.
- **A specific critique relevant to our generator: quest-marker UI can
  flatten the city's designed complexity.** The paper observes that
  Novigrad's "streets generally constitute ... a multicursal maze structure,
  giving the player multiple possibilities of traversal," but that "the
  minimap highlights the shortest route to the currently active quest
  location marker, superimposing a single unicursal path upon the
  multicursal complexity of the city space." For a player focused on
  objectives, all the deliberate irregularity/density-faking work described
  in section 2 above is invisible — they see only a single line on a
  minimap. This is a genuine tension the earlier "irregular streets read as
  dense" recommendation doesn't account for: **the payoff of urban
  irregularity depends on the player actually looking at the environment
  instead of following a waypoint.**

This third point is the one piece of new material from this pass that
should change a recommendation (see below): a wayfinding UI that's too
helpful can quietly waste all the density-faking effort a generator puts
into irregular street layouts.

---

## Recommendations for our generator

1. **Use the five-element urban-legibility framework (paths, edges, districts,
   nodes, landmarks) as an explicit planning pass for any settlement above
   village scale.** Concretely: designate 1-3 "node" plazas/junctions per
   district for above-average detail investment, force at least one
   architecturally distinct "landmark" building per major district that
   breaks the height/silhouette pattern of its surrounding building stock, and
   deliberately introduce street irregularity (varied width, non-grid
   junctions, dead ends) in older/organic districts rather than defaulting to
   a uniform grid everywhere — grid regularity should be reserved for
   districts the fiction says were centrally planned (e.g., a station's
   engineered core sections).

2. **Split NPCs into a foreground tier and a background/crowd tier with very
   different budgets.** Foreground NPCs (shopkeepers, named residents, quest-
   relevant characters) get full schedules and unique dressing; background
   crowd NPCs reuse a small shared appearance pool and much simpler behavior
   (wander/loiter, no real schedule) so that a "30,000-population city" can
   visually read as crowded in its public spaces without the generator having
   to simulate more than a few hundred actual entities.

3. **Push vertical/facade layering, not footprint, to sell size.** A narrow,
   tall, densely-packed building silhouette along a tight street reads as
   "more city" than the same floor area spent on wide, low, evenly-spaced
   buildings. For a station ring, this maps directly to stacking visible
   (non-enterable) deck levels, catwalks, and habitation-block facades above
   and below the walkable path, rather than spreading the same number of
   buildings across a flat plan.

4. **Give small-tier settlements (village/hamlet analogs) an honesty budget
   instead of a density-faking budget.** Don't try to make a 5-10 building
   outpost look bigger than it is — instead spend the generator's effort on
   *legible condition storytelling* (visible disrepair, abandonment, recent
   damage, mismatched improvised repairs, resource scarcity cues) that
   explains why the settlement is small, which reads as intentional and true
   rather than as a downgraded city.

5. **Let terrain/structural constraints drive settlement placement, not the
   reverse**, mirroring Velen's terrain-first workflow: for the station ring,
   place habitation/settlement zones in response to the station's structural
   "geography" (load-bearing spokes, existing utility corridors, hull
   curvature, artificial-gravity zones) rather than laying out settlements
   first and forcing the structure to accommodate them — this is what makes
   placement feel motivated rather than arbitrary.

6. **Budget the density-faking effort knowing wayfinding UI will often
   bypass it — and design the UI with that trade-off in mind.** The DiGRA
   paper's critique above is specific: an efficient quest-marker/minimap
   route collapses a deliberately multicursal, irregular street layout into
   a single followed line, and most players in "objective mode" will never
   consciously register the irregularity we spent budget building. Two
   valid responses, not mutually exclusive: (a) accept it as a sunk cost —
   the irregularity still pays off for exploration-mode players and for
   ambient believability even if goal-directed players don't consciously
   notice it, so it's not wasted; or (b) deliberately design the waypoint/
   pathing system to *not* always take the shortest unicursal route — e.g.
   route suggestions that follow major "node" plazas and landmark sightlines
   rather than the geometrically shortest path — so that even players
   following the UI experience some of the district's designed structure.
   Pick consciously rather than defaulting to shortest-path routing without
   considering this cost.

---

### Sources

**Developer-authored:**
- [Faces of Novigrad: a closer look at The Witcher 3's biggest city – PC Gamer](https://www.pcgamer.com/faces-of-novigrad-a-closer-look-at-the-witcher-3s-biggest-city/)
- [Designing the World of 'The Witcher 3: Wild Hunt' – Vice](https://www.vice.com/en/article/designing-the-world-of-the-witcher-3-wild-hunt/)
- [World Building of Witcher 3 – 80.lv](https://80.lv/articles/world-building-of-witcher-3)

**Academic/critical:**
- [Vella, D. and Bonello Rutter Giappone, K., "The City in Singleplayer Fantasy Role Playing Games" – DiGRA 2018 (full text)](https://dl.digra.org/index.php/dl/article/view/948/948) — source of the centring/inside-outside/movement analysis of Novigrad quoted above, including the quest-marker/unicursal-path critique.
- [Planning Novigrad – Unwinnable (Kevin Lynch urban-theory framework analysis)](https://unwinnable.com/2019/08/12/planning-novigrad/)
- [The Witcher 3 Map Velen: Why This Swamp Is Still a Masterclass in Level Design – Ponderworthy](https://ponderworthy.com/the-witcher-3-map-velen-why-this-swamp-is-still-a-masterclass-in-level-design-1y0y)
- [7 Years On, Novigrad's Still The Best City In Gaming – DualShockers](https://www.dualshockers.com/the-witcher-3-novigrad-best-city-gaming/) — largely celebratory rather than critical; included as the closest games-journalism long-form piece located specifically analyzing Novigrad's design (as opposed to a general review), not as academic critique.

**Community/fan sources (lower-confidence, unchanged from prior pass):**
- [Novigrad – The Official Witcher Wiki](https://witcher-games.fandom.com/wiki/Novigrad)
- [Novigrad – Witcher Wiki (Fandom)](https://witcher.fandom.com/wiki/Novigrad)
- [Taking a short city break in The Witcher 3's Novigrad – GamesRadar+](https://www.gamesradar.com/taking-a-short-city-break-in-the-witcher-3s-novigrad/)
- [Wild Open Spaces: A Visual Guide to the World of 'The Witcher 3' – Vice](https://www.vice.com/en/article/wild-open-spaces-a-visual-guide-to-the-world-of-the-witcher-3-2155/)

**Note on search-tooling limitation:** as with the other two files in this
set, general web search engines actively blocked automated queries this
session; Google Scholar and direct PDF fetch supplied the new academic
material. No dedicated critical-journalism essay specifically arguing
Novigrad's claimed 30,000 population is a scale mismatch (the Whiterun-style
failure mode) was located — reviewers and critics located this session are
uniformly positive about Novigrad's design, in contrast to the more mixed
Whiterun case documented in `elder_scrolls_series.md`.
