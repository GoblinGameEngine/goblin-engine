# GTA Series: Faking a Big City Without Simulating One

Research focus: GTA V (Los Santos), with GTA IV (Liberty City) and San Andreas as contrast. Goal: extract
concrete, sourced (or clearly-flagged-as-estimated) numbers and techniques for making a settlement *read* as
much larger and more populated than what is actually built/simulated.

---

## 0. Priority sourcing pass: developer statements and critical/academic analysis

Added in a follow-up research pass specifically to surface **(a) statements from Rockstar's own named
designers** and **(b) critical/academic analysis of the map design itself** — prioritized over the
community/forum estimates used elsewhere in this file, per a "check the map makers themselves, not just
wikis/forums" sourcing requirement. Where this new material confirms, complicates, or contradicts an existing
fan-sourced claim below, that is called out explicitly at the point of use.

### (a) Developer-stated facts

- **Dan Houser** (Rockstar Vice President, writer) on the compression decision behind Los Santos: "the game is
  going to be a twentieth of that size – so what are the iconic things you have to have?" He describes the
  process as "more urban planning than architecture" and the goal as capturing "the essence of what's really
  there in a city, but in a far smaller area." **This is a developer-stated ~1/20 compression figure**, distinct
  from (and rhetorically looser than) the ~10:1 area-based estimate calculated independently in Section 1 from
  sq-mile comparisons — both point the same direction, but only the sq-mile figure is independently checkable.
  [The Guardian: Dan Houser interview](https://www.theguardian.com/technology/2013/sep/17/grand-theft-auto-5-gta-dan-houser-interview)
- **Aaron Garbut** (Rockstar North Art Director) directly disputes the "kitbashed/procedurally generated"
  framing used by the modding community (see Section 2 below): "We've simply not copied buildings around the
  map or procedurally generated the terrain to pad it out... Every little bit of this world has had a large
  number of extremely talented artists pore over it." He also states the population-illusion goal explicitly:
  "The obsession was to make sure that it was teeming with life... our goal was to get everything in the game."
  **This is a named-developer counterpoint to the fan/forum "constrained facade kit" theory in Section 2** —
  Rockstar's own messaging claims hand-crafted uniqueness, while outside visual/asset analysis still finds
  repeated modular elements. Treat these as what they are: an official developer claim vs. an outside technical
  inference, not two versions of the same fact. [BuzzFeed News: "Way Beyond Anything We've Done Before" by
  Joseph Bernstein](https://www.buzzfeednews.com/article/josephbernstein/way-beyond-anything-weve-done-before-building-the-world-of-g)
- On GTA IV specifically, Garbut described Rockstar's approach to Liberty City as capturing "a caricature of
  the city" rather than 1:1 geographic accuracy, reasoning most players only know a city's "highlights." The
  team also deliberately minimized "dead spots and irrelevant spaces" (explicitly contrasted against San
  Andreas's open deserts), and **built the city geometry first, then authored missions into the finished
  space** rather than designing missions and building supporting geometry around them. [Development of Grand
  Theft Auto IV — Wikipedia, aggregating original Eurogamer/IGN/OPM UK interviews](https://en.wikipedia.org/wiki/Grand_Theft_Auto_IV)

### (b) Critical / academic analysis of the map design itself

- Mark Teo's academic paper "The Urban Architecture of Los Angeles and Grand Theft Auto" applies Kevin Lynch's
  urban-legibility theory and Rowe & Koetter's "Collage City" framework directly to Los Santos. Its most
  transferable finding: Los Santos (measured at 45.52 km² in the paper) **compresses LA's population and
  economic activity into what the paper calls "a zero-population scenario"** in Downtown specifically — i.e.,
  academic urban-theory analysis independently confirms the "big city, functionally empty" pattern documented
  from the systems side in Section 3, and frames it as a *legibility* technique (landmarks, wayfinding, wide
  roads) rather than a simulation shortfall. [academia.edu: Mark Teo, "The Urban Architecture of Los Angeles
  and Grand Theft Auto"](https://www.academia.edu/18173221/The_Urban_Architecture_of_Los_Angeles_and_Grand_Theft_Auto)
- The architecture-critique essay "Learning from Los Santos" (Alephograph) coins the term **"Hidden Interior
  Universe"** for GTA V's strategy of fragmenting the city by concealing almost all interior space from the
  player, and notes the city's public infrastructure "is a rather well supported city" despite its
  outlaw-playground narrative framing. It argues the city's credibility comes from scale-shifting "long zoom"
  views and well-modeled *exteriors*, not from interior access — directly supporting, and adding critical
  framing to, this file's Section 2 enterable-building analysis. [Alephograph: "Learning from Los
  Santos"](https://www.alephograph.com/learning-from-los-santos)

### What's still unsourced after this pass

GTA V's **exact total building count** and an **exact enumerated facade-kit piece count** were not found in any
developer talk, postmortem, or critical essay located in this pass (or the prior one) — Rockstar has never
published either figure. Aaron Garbut's on-record statement above actively disputes the framing that would make
a "facade kit count" meaningful in the first place. The ~40-50 enterable interiors / <2% figure in Section 2
remains the best available number and is still forum-sourced only; the "constrained facade kit" theory should
now be read as **outside technical inference that Rockstar's own art director has publicly disputed**, not a
confirmed studio technique.

---

## 1. Real-world basis and scale compression

### GTA V — Los Santos / San Andreas (based on Los Angeles / Southern California)

- Los Santos + Blaine County map is roughly **49 square miles (~127 km²)** in-game.
- The real Greater Los Angeles area it evokes is roughly **500+ square miles (502.7 sq mi city proper)**.
- That's roughly a **10:1 linear/area compression** of the real region into the game map — Rockstar
  compresses the *geography*, not just the building count. [Beebom GTA 5 map guide](https://beebom.com/gta-5-map-guide/),
  [ArchUp comparative analysis](https://archup.net/comparing-los-santos-map-los-angeles/)
- For context, the compressed 49 sq mi map is still larger than real San Francisco (121 km²), Paris (105 km²),
  or central Tokyo (126 km²) — i.e., Rockstar didn't shrink the map to "small," they shrank it to "a size a
  single player can traverse in minutes but that still reads as a big metropolitan area."
- Real Los Angeles city population: ~3.9 million (city proper), ~13 million (metro). GTA V never states a
  population figure for Los Santos in fiction, so there is no official number to compress against — the
  "compression ratio" for population is therefore **unsourced / not tracked by Rockstar** and any number
  quoted online is a fan estimate. What *is* directly measurable and sourced is the **geographic compression
  (~10:1)** and the **enterable-building ratio** below.

### GTA IV — Liberty City (based on New York City)

- Liberty City's three boroughs total about **6.23 square miles**, versus New York City's ~302.6 square
  miles — roughly a **48:1 area compression**, i.e. GTA IV compressed its real-world analogue far more
  aggressively than GTA V did. [gta4.net real-world comparison](https://www.gta4.net/setting/liberty-city-versus-real-world.php),
  [GTA Wiki: State of Liberty](https://gta.fandom.com/wiki/State_of_Liberty_(HD_Universe))
- Each north-south city block in Liberty City is said to represent roughly ten real NYC blocks — i.e., block
  density itself is compressed, not just the outer map boundary. This is the clearest sourced technique:
  **compress the grid, not just the footprint** — keep block-to-block travel time short while implying a much
  larger street grid continues beyond what's rendered (via skyline backdrops, bridges to "elsewhere," etc.).

### San Andreas (GTA:SA) — contrast point

- San Andreas represented an entire fictional US state (three cities — Los Santos, San Fierro, Las Venturas —
  plus countryside) in one map, using much simpler, blockier building geometry and far more (but far cruder)
  enterable interiors than GTA V. The tradeoff Rockstar made between GTA:SA and GTA V is well documented by
  players/critics as "more (but shallower) interiors and more cities" vs. "one city, much higher fidelity,
  fewer interiors" — GTA V deliberately traded *breadth* of interactivity for *depth* of visual/graphical
  fidelity per building. [Sportskeeda: 5 biggest downgrades in GTA 5's map](https://www.sportskeeda.com/gta/5-biggest-downgrades-gta-5-san-andreas-map)

---

## 2. The "Hollywood facade" technique — enterable vs. total buildings

- A commonly cited (forum-sourced, not an official Rockstar statistic) figure is that GTA V has around
  **~40-50 truly enterable interiors** (shops, safehouses, a handful of story locations) against a city
  containing many thousands of individual building models. Quoted estimates put this at **under 2% of
  buildings being enterable**. **This specific percentage is a fan/forum estimate, not a Rockstar-sourced
  figure** — flagged accordingly. [GTAForums: how many enterable buildings](https://gtaforums.com/topic/594495-how-many-enterable-buildings-are-there-list-unique-ones/)
- The interiors that *do* exist are concentrated in **functional categories**: clothing stores, gun shops,
  barbershops, tattoo parlors, safehouses/apartments, and story-critical locations (Franklin's aunt's house,
  Michael's mansion, etc.) — i.e., interiors are budgeted for **gameplay necessity**, not geographic coverage.
  Every other building is an exterior-only "set piece."
  [GTAForums: list of enterable interiors](https://gtaforums.com/topic/836929-list-of-enterable-interiors/)
- This was a widely noted point of player criticism at launch — reviewers and players described Los Santos as
  feeling like "a movie set" specifically because so few doors open. Rockstar's choice was clearly a
  **fidelity vs. coverage tradeoff**: put full art/prop budget into a small number of real interiors and let
  everything else be a well-dressed shell.
- GTA 6 (unreleased at research time, but frequently discussed relative to GTA V as the "fix") is reported/
  rumored (not yet confirmed by Rockstar at full detail) to push toward **~40-70% of buildings enterable /
  700+ interiors**, explicitly positioned by press as a reaction to GTA V's low interior ratio. This is useful
  as a forward-looking data point but should be treated as **unconfirmed / marketing-stage claims**, not a
  shipped, provable number. [GTA6Bible rumor roundup](https://gta6bible.com/rumors/gta-6-features-700-interiors-and-40-of-buildings-are-enterable/)

**Takeaway on kitbashing / variety:** GTA V's non-enterable buildings are known (from asset-modding community
observation, not an official dev statement) to reuse a constrained kit of modular facade pieces — window
rows, cornices, rooftop AC units, awnings, signage plates — recombined with palette/material swaps per
district, rather than every building being a fully unique model. This is standard "kitbashing," well attested
in city-builder/open-world dev talks generally, though no single citable Rockstar interview enumerating the
exact GTA V facade kit count was found in this research pass — flagged as **inferred from visual analysis
and general industry practice, not sourced to a specific Rockstar statement**. **Update from the priority
sourcing pass (see Section 0):** Rockstar North Art Director Aaron Garbut has publicly and specifically denied
this characterization — "We've simply not copied buildings around the map or procedurally generated the
terrain to pad it out" — so this remains an outside inference that the developer disputes, not a confirmed
technique. For contrast, Bethesda's Joel Burgess *does* publicly confirm and name this exact modular-kit
technique for Fallout/Skyrim (see fallout_series.md Section 0) — the two studios' own public statements about
the same class of technique genuinely diverge, which is itself a useful data point: don't assume every AAA
open-world studio uses (or admits to) kitbashing just because one clearly does.

---

## 3. Pedestrian / traffic density — simulating only what's near the player

- GTA V (and the RAGE engine generally) does **not** simulate the whole city's population at once. It uses a
  **population density/streaming system** keyed to the player's position:
  - A **creation radius** around the player where peds/vehicles are allowed to spawn.
  - A **deletion radius** beyond which entities are despawned once out of relevance.
  - A **population density scalar** ("ped density," "car density") that controls how many entities are
    allowed to exist simultaneously within that active radius — directly trading off against VRAM/RAM budget.
  - These are tuned via config data (community-documented as living in files like `popcycle.dat` /
    `gameconfig.xml`) that vary density **by time of day and by zone type** (downtown vs. suburb vs. highway),
    not uniformly across the whole map.
    [Steam discussion: population density explained](https://steamcommunity.com/app/271590/discussions/0/611703709832246357/),
    [GTA5-mods: Dynamic Population Density](https://www.gta5-mods.com/scripts/dynamic-population-density)
  - Critically, **increasing draw/spawn distance reduces achievable density** (more entities visible at once
    costs more budget), so Rockstar's tuning is a direct trade between "how far you can see peds" and "how
    many peds exist" — they chose a *relatively short, dense bubble around the player* over a sparse but
    far-seeing crowd. [Adrian Courrèges GTA V graphics study](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/)
- This is the core trick that lets a city feel "alive" everywhere the player currently is, while the vast
  majority of the map at any instant has **zero simulated pedestrians** — because the player literally isn't
  there to notice.

---

## 4. District identity without uniform detail

- GTA V's neighborhoods (Rockford Hills = Beverly Hills analogue, Vinewood Hills = Hollywood Hills analogue,
  Downtown/Pillbox Hill = Downtown LA analogue, etc.) establish identity primarily through:
  - **One or two unique landmark elements per district** — e.g., the Vinewood Sign, the Rockford Hills Sign
    park, a specific architectural style cluster (Spanish-style mansions in Rockford Hills).
  - **Consistent architecture-type per district** (mansions vs. high-rises vs. stucco strip malls) rather than
    unique buildings everywhere — the *type* changes per district, the *individual instances* within a type
    are still repeated/modular.
  - **Signage and named streets/landmarks** doing a lot of identity work cheaply (a sign is far cheaper than
    a unique building). [GTA Wiki: Rockford Hills](https://gta.fandom.com/wiki/Rockford_Hills),
    [GTA Wiki: Vinewood Hills](https://gta.fandom.com/wiki/Vinewood_Hills)
  - Sub-zoning *within* a district (e.g., Rockford Hills splits into a residential north and a shopping-street
    south) so even a single named district doesn't read as monotonous.

---

## 5. Draw distance / LOD / pop-in management

- RAGE's streaming system loads geometry/LOD based on player speed and distance — normal driving speed keeps
  up with full detail streaming; fast movement (aircraft) forces the game to reduce mesh LOD and can still
  show pop-in, which is a known, documented limitation Rockstar mitigates by **capping/reducing vehicle top
  speeds relative to streaming radius** rather than solving it outrightly.
  [Adrian Courrèges: GTA V Graphics Study Part 2](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/)
- Weather/time-cycle config files control draw distance for structures, people, and vehicles as a single
  tunable, meaning the game deliberately **trades peak draw distance against ped/vehicle density** — it is
  not trying to render "everyone, everywhere, always"; it explicitly narrows the radius of full simulation in
  exchange for a livelier *nearby* radius.
- Net effect: the far distance is dressed with static, cheap-to-render skyline/silhouette geometry (buildings
  with no interior logic, no AI, often lower-poly/baked), while the immediate few hundred meters around the
  player carry the "real" simulated population.

---

## Recommendations for our generator

These are concrete, actionable rules distilled from the above, explicitly separated from the descriptive
research so they can be applied directly to the station's procedural map generator.

1. **Compress geography before compressing population.** GTA V (~10:1 by sq-mile comparison; Rockstar's own
   Dan Houser independently described the target as "a twentieth of the size" of the real analogue in
   interview — see Section 0) and GTA IV (~48:1) both shrink the *area* far more aggressively than they ever
   try to track population. Don't attempt to justify our station's footprint against a literal 100,000-person
   density model — instead pick a habitat-ring footprint that *reads* as city-scale (varied districts,
   walkable block rhythm, skyline silhouette) at whatever size is actually simulatable, and let population be
   an unstated/implied fiction number, not a tracked one. Academic analysis of Los Santos (Mark Teo, Section 0)
   independently found its Downtown functions as "a zero-population scenario" from a simulation standpoint —
   i.e., even the "realest" GTA district is legibility-driven scenery, not simulated density, which validates
   leaning hard on this technique rather than treating it as a shortcut to apologize for.

2. **Enterable-interior budget: aim for a small, deliberately curated interior set (roughly 1-2% of total
   exterior building count, matching GTA V's rough ratio), allocated by gameplay function, not geographic
   coverage.** Concretely: every shop-type the player needs (general store, bar, clinic, workshop, a couple
   of unique "story" locations) gets a real interior; everything else — the vast bulk of housing-block
   exteriors — is a non-enterable shell. Budget interior art/prop work only where the player will actually
   transact or quest, exactly as GTA V allocates interiors to clothing stores/gun shops/safehouses rather than
   spreading thin coverage across the whole map.

3. **Build a constrained modular facade kit per district "type," not unique buildings per lot.** GTA V's
   apparently-repeated window/cornice/signage pieces recombined with palette swaps are the best inferred
   explanation for how thousands of building faces were covered — **even though Rockstar's own art director
   publicly disputes this characterization for GTA V specifically (Section 0)**. This recommendation still
   stands on its own merits regardless of what Rockstar did: Bethesda's Joel Burgess independently and
   explicitly confirms the same class of technique for Fallout/Skyrim in his own GDC talks (see
   fallout_series.md Section 0), and we do not have Rockstar's ~1,000-person art team, so a small studio/solo
   generator should default to the kit approach on production-capacity grounds alone. For the station ring:
   define maybe 5-8 base building "hull" meshes per district archetype (residential deck, market deck,
   industrial deck, etc.) with swappable trim, signage, and color/material variants — most of the sense of
   variety should come from *recombination and palette*, not from unique geometry per building.

4. **Population/NPC density should be a player-local streaming bubble, not a station-wide simulation.**
   Mirror RAGE's creation/deletion radius + density scalar: define a radius around the player within which
   NPCs actually exist and act, tuned per district (busy market deck vs. quiet residential ring), and
   despawn/recycle NPCs outside it. Explicitly trade draw distance against density — a shorter "alive" radius
   with a denser crowd reads as more populated than a long sightline with sparse NPCs.

5. **District identity needs only 1-2 unique landmark elements plus a consistent architecture "type," not
   unique detail everywhere.** For each named district on the ring (e.g., "the market ring," "the engineering
   spine," "the garden deck"), budget one hero landmark (a sign, a distinctive structure, a plaza) and one
   consistent material/architecture theme applied to otherwise-modular filler buildings. This is cheap and is
   exactly how Rockford Hills/Vinewood Hills read as distinct despite sharing a huge amount of underlying
   modular kit geometry.

6. **Far/background geometry should be cheap, non-simulated silhouette only.** Anything beyond the player's
   active-population radius (the far side of the ring, decks not currently occupied) should render as
   low-detail/no-AI backdrop — visible for scale and immersion, but carrying zero simulation cost, exactly as
   GTA's distant skyline is static dressing while only the nearby streets carry live pedestrian logic.

7. **Treat "enterable ratio" and "district landmark count" as tunable generator parameters**, e.g.
   `enterable_interior_ratio ≈ 0.01–0.02` and `landmarks_per_district ≈ 1–2`, so the generator can be dialed
   toward "GTA V-style sparse-but-deep" or a denser interior ratio later without a full redesign.

---

## Sources

### Developer statements and critical/academic analysis (priority sourcing pass)

- [The Guardian: Dan Houser interview on Los Santos](https://www.theguardian.com/technology/2013/sep/17/grand-theft-auto-5-gta-dan-houser-interview)
- [BuzzFeed News: "Way Beyond Anything We've Done Before: Building the World of GTA V" (Aaron Garbut interview)](https://www.buzzfeednews.com/article/josephbernstein/way-beyond-anything-weve-done-before-building-the-world-of-g)
- [TechRadar: "The tech that built an empire: how Rockstar created the world of GTA 5"](https://www.techradar.com/news/gaming/the-tech-that-built-an-empire-how-rockstar-created-the-world-of-gta-5-1181281)
- [Development of Grand Theft Auto IV — Wikipedia (aggregates Eurogamer/IGN/OPM UK Aaron Garbut/Dan Houser interviews)](https://en.wikipedia.org/wiki/Grand_Theft_Auto_IV)
- [academia.edu: Mark Teo, "The Urban Architecture of Los Angeles and Grand Theft Auto"](https://www.academia.edu/18173221/The_Urban_Architecture_of_Los_Angeles_and_Grand_Theft_Auto)
- [Alephograph: "Learning from Los Santos"](https://www.alephograph.com/learning-from-los-santos)

### Original pass sources

- [Beebom: GTA 5 Map Guide](https://beebom.com/gta-5-map-guide/)
- [ArchUp: Los Santos vs. Los Angeles comparative analysis](https://archup.net/comparing-los-santos-map-los-angeles/)
- [gta4.net: Liberty City vs. real-world comparisons](https://www.gta4.net/setting/liberty-city-versus-real-world.php)
- [GTA Wiki: State of Liberty (HD Universe)](https://gta.fandom.com/wiki/State_of_Liberty_(HD_Universe))
- [Sportskeeda: 5 biggest downgrades in GTA 5's San Andreas map](https://www.sportskeeda.com/gta/5-biggest-downgrades-gta-5-san-andreas-map)
- [GTAForums: How many enterable buildings are there](https://gtaforums.com/topic/594495-how-many-enterable-buildings-are-there-list-unique-ones/)
- [GTAForums: List of enterable interiors](https://gtaforums.com/topic/836929-list-of-enterable-interiors/)
- [GTA6Bible: GTA 6 features 700+ interiors, 40% enterable (rumor, unconfirmed)](https://gta6bible.com/rumors/gta-6-features-700-interiors-and-40-of-buildings-are-enterable/)
- [Steam Community: What does Population Density do?](https://steamcommunity.com/app/271590/discussions/0/611703709832246357/)
- [GTA5-Mods: Dynamic Population Density script](https://www.gta5-mods.com/scripts/dynamic-population-density)
- [Adrian Courrèges: GTA V Graphics Study, Part 2](https://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study-part-2/)
- [GTA Wiki: Rockford Hills](https://gta.fandom.com/wiki/Rockford_Hills)
- [GTA Wiki: Vinewood Hills](https://gta.fandom.com/wiki/Vinewood_Hills)
