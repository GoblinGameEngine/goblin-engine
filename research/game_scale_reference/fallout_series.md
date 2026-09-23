# Fallout Series: Making Tiny Settlements Feel Like "The Big City"

Research focus: Fallout 3, Fallout 4, Fallout: New Vegas, with Fallout 76 noted for contrast. Goal: extract
concrete, sourced numbers on settlement NPC/building counts, the Radiant AI scheduling system, and Fallout
4's settlement-building kit, as parallels for our own tiny-population, believable-settlement generator.

---

## 0. Priority sourcing pass: developer talks and critical/academic analysis

Added in a follow-up research pass specifically to surface **(a) statements from Bethesda's own named
designers** and **(b) critical/academic analysis of the world design itself** — prioritized over the
community/forum/wiki estimates used elsewhere in this file. Where this material upgrades or fills a gap
flagged below, that is called out at the point of use.

### (a) Developer-stated facts — from the map makers themselves

- **Joel Burgess**, Bethesda Lead Level Designer, published his own GDC talk transcripts on his personal blog
  — as close to a primary, in-the-designer's-own-words source as this research found:
  - GDC 2013, "Skyrim's Modular Level Design" (explicitly references the *same* technique used on Fallout 3):
    "A basic pipe kit, like the one from Fallout 3, may only be four simple pieces of art which can be used
    together... The most important attribute of a kit is that it adds up to far more than the sum of its
    parts." Skyrim's dungeon content — **well over 400 cells (unique loaded interiors)** — was built by **two
    full-time kit artists supporting eight level designers**, i.e., a small kit-art team multiplying a larger
    design team's output. Burgess uses the word "kitbashing" himself. **This directly confirms, from the
    studio's own lead level designer, that modular kit-based reuse is an explicit, named, developer-endorsed
    technique** (contrast with Rockstar/GTA V, where the art director has publicly *disputed* the equivalent
    characterization — see gta_series.md Section 0). [Joel Burgess: "Skyrim's Modular Level Design — GDC 2013
    Transcript"](http://blog.joelburgess.com/2013/04/skyrims-modular-level-design-gdc-2013.html)
  - GDC 2014, "How We Used Iterative Level Design to Ship Skyrim and Fallout 3": Skyrim's level design team
    produced **"over two hundred locations which involve level designer effort,"** using a staged process
    (concept → proof → graybox → build-out → polish) that deliberately keeps early passes "functional-but-ugly"
    so design and art can iterate in parallel. Burgess also describes using environmental-storytelling
    backstory even when "we don't intend to communicate this information to the player in any concrete way" —
    it still "informs hundreds of seemingly-inconsequential decisions" about how a space is built. [Joel
    Burgess: "GDC 2014 Transcript: The Iterative Level Design Process"](http://blog.joelburgess.com/2014/07/gdc-2014-transcript-iterative-level.html)
  - **This upgrades Section 3's sourcing below**: the "constrained modular kit" claim for Fallout 4's
    settlement system is no longer only inferred from the Fallout Wiki's settlement-objects page — Bethesda's
    own lead level designer has publicly and specifically described this exact technique (kit pieces +
    kitbashing + iterative graybox passes) as core studio practice across Skyrim and Fallout 3/4.

- **Joel Burgess** and **Gavin Carter** (Fallout 3 Lead Producer), in a 2018 retrospective interview, gave a
  first-party account of a **documented density/scale design mistake**: Washington D.C. had to be split into
  disconnected zones linked by a Metro system "due to how the game engine worked," and playtesters "routinely
  struggled to navigate the Metro" and found the added friction unenjoyable. Bethesda tried removing the zone
  dividers, but "the initial test did not show promise," so the idea was dropped under time pressure. Burgess
  calls the whole D.C. area **"the big mistake I feel I made on [Fallout 3],"** and says a *better-run* test —
  not a different design — might have fixed it. This is a rare named-designer account of a compression/scale
  decision going wrong, directly relevant to any station-ring compression choices we make. [TechRadar:
  "Vaulting ambition: Fallout 3 and the making of an RPG classic" (Samuel Horti)](https://www.techradar.com/news/vaulting-ambition-how-fallout-3-changed-the-game)

- **Emil Pagliarulo** (Fallout 3 Lead Designer) and **Todd Howard**, per GameSpot's coverage of their **GDC
  2009** talk: the central D.C. ruins area was originally built at roughly **twice its shipped size**, fully
  built and polished, before Howard made the call to cut it down for scope/pacing reasons — a sourced example
  of Bethesda deliberately *shrinking* a fully-built area rather than starting small and growing it. An
  ambitious Enclave-assault-on-Rivet-City mission was also cut as "too resource-intensive"; Pagliarulo, who had
  originally pushed for it, later agreed: "In the end he was right, we couldn't do it." Pagliarulo's stated
  design philosophy from the same talk: "You just have to be honest with yourself and admit when something
  isn't working," and "Great games are played, not made" (i.e., prioritize constant playtesting over
  up-front planning). [GameSpot: "GDC 2009: Fallout 3 lead opens game design vault"](https://www.gamespot.com/articles/gdc-2009-fallout-3-lead-opens-game-design-vault/1100-6206965/)

### (b) Critical / academic analysis of the world design itself

- Kevin McClancy, **"The Wasteland of the Real: Nostalgia and Simulacra in Fallout,"** published in *Game
  Studies* (the peer-reviewed academic games journal — not a wiki or fan site), argues the franchise's
  retrofuturist gameworld design functions as a Baudrillardian simulacrum that *critiques* Cold War nostalgia
  rather than indulging it, and that menu/inventory/V.A.T.S. systems deliberately break immersion to keep
  reminding the player the "world" is a constructed system. A genuine academic games-studies analysis of
  gameworld design intent, though it engages tone/theme more than density/scale specifically. [Game Studies:
  McClancy, "The Wasteland of the Real"](https://gamestudies.org/1802/articles/mcclancy)
- A further academic book chapter, "Worldbuilding, Nuclear Engagement, Resource Scarcity, and Raymond
  Williams' Structure of Feeling in Bethesda's Fallout 4," analyzes Fallout 4's worldbuilding and
  resource-scarcity framing in academic terms — noted here as an available further academic source, not
  deeply excavated in this pass. [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-67980-3_13)

### Filling the flagged NPC-count gaps

- **Novac**: still no official total population figure exists (Obsidian never states one in-fiction or via
  interview), but the Fallout Wiki's own character roster for Novac enumerates **12 distinct named residents**
  (Craig Boone, Manny Vargas, Ranger Andy, Jeannie May Crawford, Cliff Briscoe, No-Bark Noonan, Alice McBride,
  Dusty McBride, Ada Straus, Bruce Isaac, Daisy Whitman, Chris Haversam) plus an unspecified number of generic
  "Novac settlers." This is a concrete, enumerable (if still unofficial) number, an improvement over this
  file's prior "no precise population figure found." [Fallout Wiki: Novac](https://fallout.fandom.com/wiki/Novac)
- **Diamond City**: still no official Bethesda-stated total, but the individually-named, schedule/dialogue-
  bearing NPC roster enumerates to **roughly 40+ named characters** across companions (Piper Wright, Nick
  Valentine), vendors/services (Arturo Rodriguez, Doc Crocker, the Bobrov brothers, Pastor Clements, etc.),
  quest-related characters (Mayor McDonough, Nat Wright, Travis Miles, etc.), and other named residents —
  consistent with, and more concrete than, this file's prior "a few dozen unique named characters" statement.
  Community claims of an exact single number (e.g. "52") were found only on low-quality aggregator/AI-answer
  sites and are **not used here** since they could not be traced to a primary count. [Fallout Wiki: Diamond
  City (archive mirror)](https://fallout-archive.fandom.com/wiki/Diamond_City)

---

## 1. Actual building/NPC counts for named "big" settlements

### Megaton (Fallout 3)

- Megaton has **28 named inhabitants, 10 unnamed Megaton settlers, and 4 Children of the Atom — 42 NPCs
  total.** Sourced as second-most-populated settlement in the game after Rivet City.
  [Fallout Wiki: Megaton](https://fallout.fandom.com/wiki/Megaton)
- Megaton is built from scavenged scrap around a live nuclear bomb crater — its entire physical footprint is
  a handful of shack/shop interiors (Moriarty's Saloon, Craterside Supply, Doc Church's clinic, the Brass
  Lantern diner, a handful of houses) ringing one central plaza. The *fiction* explicitly frames it as a
  scrappy, small settlement rather than a metropolis — the game doesn't need to justify a big population
  because the narrative purpose of Megaton is "biggest thing for miles in a mostly-dead wasteland," not "a
  real city." This narrative framing (post-apocalyptic collapse) does a lot of the "why does this feel like
  enough" work that a purely sci-fi/space setting would have to do differently.

### Diamond City (Fallout 4)

- No official precise NPC count was found; the Fallout Wiki's own named-character roster for Diamond City
  enumerates to **roughly 40+ individually-named NPCs** (companions, vendors, quest-related characters, other
  residents — see Section 0 for the itemized breakdown from this sourcing pass), while additional unnamed
  generic settler/guard NPCs pad out the visible crowd. Framed narratively as "the largest settlement in the
  Commonwealth," built inside Fenway Park's stadium bowl — the *stadium shell itself* (a real, recognizable,
  single large landmark structure) does most of the "this must be a big, important place" work, not building
  count. **Precise official Bethesda-stated total NPC count still not found — the ~40+ figure is an enumerated
  wiki-roster count, not a developer-published number**, and is more concrete than but not a replacement for a
  hard source. [Gamerant: Every Major City in Fallout 4 & How Many NPCs Live There](https://gamerant.com/fallout-four-major-city-npc-population/),
  [Fallout Wiki: Diamond City](https://fallout-archive.fandom.com/wiki/Diamond_City)

### Goodsprings (Fallout: New Vegas)

- Goodsprings has an official population of **13**, per the game guide — explicitly a "barely active town"
  whose in-fiction decline (trade along the Long 15 highway drying up) is used to *justify* its small size
  narratively rather than hide it. [Fallout Wiki: Goodsprings](https://fallout.wiki/wiki/Goodsprings)
- The settlement consists of only a handful of buildings (saloon, general store/gas station, a few houses,
  a school-turned-fortified-position) — small enough that the player can walk its entire footprint in under
  a minute, yet it functions as a fully "real" starting town because of writing/quest density, not size.

### Novac (Fallout: New Vegas)

- No official total population figure found in this research pass, but the Fallout Wiki's character roster
  enumerates **12 distinct named residents** (Craig Boone, Manny Vargas, Ranger Andy, Jeannie May Crawford,
  Cliff Briscoe, No-Bark Noonan, Alice McBride, Dusty McBride, Ada Straus, Bruce Isaac, Daisy Whitman, Chris
  Haversam) plus an unspecified number of generic "Novac settlers" — see Section 0. Descriptively, Novac is
  "little more than a lonely desert highway motel" — a motor court of a few dozen bungalow-style rooms around
  a giant dinosaur statue (the Dino Dee-lite Motel's "Dinky" statue), a diner, and a sniper's nest. Like
  Diamond City's stadium, **one big single landmark object (the giant dinosaur) anchors the whole location's
  memorability** far more than building count does. [Fallout Wiki: Novac](https://fallout.fandom.com/wiki/Novac)

### General population framing

- Fan/community estimates for the entire Capital Wasteland (Fallout 3's setting) range wildly — from ~2,500
  to 10,000-15,000 people depending on assumptions — precisely because Bethesda never commits to a hard
  number in-fiction. **These are fan extrapolations, not official figures**, and the wide variance itself is
  informative: the game never needs an internally consistent population number because the fiction (nuclear
  war depopulation) makes "we don't actually know how many people are left" thematically appropriate rather
  than a plot hole. [alternatehistory.com forum discussion](https://www.alternatehistory.com/forum/threads/fallout-3-future-of-the-capital-wasteland.196679/)
- Fallout 3 as a whole contains **319 distinct characters** across its entire game world (all locations
  combined) — a directly useful "total simulated NPC budget for an entire open world" data point.
  [Fallout Wiki: Fallout 3 characters](https://fallout.fandom.com/wiki/Fallout_3_characters)
- Fallout: New Vegas has **over 380 uniquely named NPCs** across its entire map.
  [TheGamer: How Many NPCs Are In The Game?](https://www.thegamer.com/fallout-new-vegas-how-many-npcs/)

### Sanctuary Hills (Fallout 4) — pre-war vs. post-war contrast

- Per Fallout tabletop-RPG sourcebook lore, pre-war Sanctuary Hills was a small suburb of **fourteen
  prefabricated homes**. [Fallout Wiki: Sanctuary Hills](https://fallout.fandom.com/wiki/Sanctuary_Hills)
- As a player-rebuildable settlement, Sanctuary Hills (like all Fallout 4 settlements) is capped at a
  **maximum of ~20 settlers** (modifiable somewhat by the player's Charisma stat) — this is a deliberate,
  documented game-design cap, not a technical limit alone; it exists specifically so the settlement-building
  system stays performant and manageable. [Steam Community discussion on the 20-settler cap](https://steamcommunity.com/app/377160/discussions/0/458604254433931291/)

### Why a handful of NPCs "feels earned"

The consistent pattern across Fallout 3/NV/4: the fiction of **nuclear war + centuries of societal collapse**
directly explains and justifies tiny populations. The game never has to hide the low NPC count — it leans
into it, using dialogue, environmental storytelling (graves, abandoned houses, notes/terminals implying people
who used to live there and are now gone), and characters explicitly commenting on how depleted the world is.
This is the single biggest transferable lesson: **a sparse population reads as intentional and earned when
the fiction explains the scarcity, rather than the game pretending a bustling crowd exists just off-screen.**

---

## 2. Radiant AI and NPC scheduling — making a small cast feel alive

- **Radiant AI** is Bethesda's system, introduced in *The Elder Scrolls IV: Oblivion* (2006) and carried
  forward (in evolved/simplified form) into Fallout 3, New Vegas, and Fallout 4. It lets NPCs follow **24-hour
  schedules** and choose actions (eat, sleep, work, socialize, patrol) based on personal goals and simple
  utility scoring, rather than being hand-scripted to stand in one spot. [Wikipedia: Radiant AI](https://en.wikipedia.org/wiki/Radiant_AI)
- In Oblivion specifically, over **1,000 NPCs** ran on schedule-driven Radiant AI simultaneously — this was
  the original ambitious version. Some of the more emergent/dangerous behaviors (NPCs improvising drastic
  solutions to needs, e.g. theft or violence to solve hunger) were famously **reined in before release**
  because they produced unpredictable, sometimes game-breaking outcomes — a documented cautionary lesson about
  giving simulated NPCs too much autonomy without safety rails. [Medium: Lost Features — critical essay on Oblivion's Radiant AI](https://medium.com/@gatherer286/lost-features-a-critical-essay-on-tes-iv-oblivions-radiant-ai-a0150144ddef),
  [paavohtl blog: What was Radiant AI, anyway?](https://blog.paavo.me/radiant-ai/)
- By Fallout 3 (and later Skyrim), Bethesda **toned down the fully emergent version** of Radiant AI in favor
  of more tightly authored schedules plus a separate "Radiant Story/Radiant Quest" system for quest variation
  — i.e., the *scheduling* half of Radiant AI (move NPCs between hand-placed locations on a clock) proved far
  more reliable and shippable than the *emergent decision-making* half, and is the part that persisted.
  [Wikipedia: Radiant AI](https://en.wikipedia.org/wiki/Radiant_AI)
- **Mechanically, in Fallout 3/New Vegas (via the GECK editor)**, NPC routines are built from:
  - **AI Packages** — discrete behavior units (e.g., "Travel," "Sleep," "Sandbox," "Patrol," "Use Item at
    location") assigned to an NPC with an associated **schedule** (which days/hours the package is active,
    in minimum 1-hour blocks). [GECK Wiki: Category:Packages](https://geckwiki.com/index.php/Category:Packages)
  - The **Sandbox Package** specifically is the key "feels alive without being hand-scripted" tool: when
    active, an NPC scans nearby objects (furniture, food items, idle markers, other NPCs) and **scores each
    potential interaction**, picking one to perform, avoiding repeating the same action twice in a row. Sleep
    start time/duration is randomized within a configured range (`fSandboxSleepStartMin`/`fSandboxSleepStartMax`)
    and recalculated daily, so NPCs don't all sleep at exactly the same clock tick. [GECK Wiki: Sandbox Package](https://geckwiki.com/index.php/Sandbox_Package)
  - This means a single NPC with **one Sandbox package** covering "idle time" plus two or three scheduled
    Travel packages (go to work location in the morning, go home at night) produces a visibly "living" daily
    routine using only a handful of authored waypoints, not a full simulation.
- **Transferable pattern:** a small number of NPCs each cycling through **2-4 named locations on a clock**
  (home, workplace, a social/food location, a patrol route), with **local, low-cost idle behavior
  (sandbox-style furniture/prop interaction) filling the gaps**, reads as "a living town" far more effectively
  than a larger number of NPCs standing static. The perceived aliveness comes from **movement and routine
  variety**, not from raw headcount.

---

## 3. Fallout 4's settlement-building system — modular kit reuse

- Fallout 4's Workshop/settlement system lets the player (and, more relevantly for us, the game's own
  pre-built settlements) construct locations from a **constrained kit of pre-fabricated structural pieces**:
  walls, floors, roofs, and snap-together modular segments, plus craftable furniture/decoration objects.
  [Fallout Wiki: Fallout 4 settlement objects](https://fallout.fandom.com/wiki/Fallout_4_settlement_objects)
- The base game's own hand-built settlements (Sanctuary, Starlight Drive-In, County Crossing, etc.) are
  themselves assembled from this same constrained modular piece kit re-skinned with salvage/scrap textures,
  not bespoke unique architecture per settlement — the *variety* comes from **how existing pieces are
  arranged and combined**, and from a settlement's terrain/pre-existing (pre-war) structure providing a unique
  base layout, not from unique geometry per building.
- The **DLC expansions (e.g., Wasteland Workshop) added more kit pieces** (cages, arena components, concrete
  structural variants) rather than replacing the underlying system — i.e., Bethesda's own strategy for adding
  variety over time was "grow the shared kit," directly analogous to how a procedural generator should be
  extended: add more modular pieces to the shared palette, not more unique one-off buildings.
- This is a very close structural parallel to what a station procedural generator should do: **one shared
  library of structural/decorative pieces, recombined per-location, with location identity coming from layout
  and material/prop dressing choices rather than unique meshes.**
- **This is no longer just inferred from a fan wiki.** Bethesda's own Lead Level Designer, Joel Burgess,
  confirms and names this exact technique in his GDC talks (see Section 0 above): a Fallout 3 "pipe kit" of as
  few as **four pieces of art**, combined ("kitbashed") to cover far more ground than the piece count implies;
  and Skyrim's **400+ dungeon cells** built by just **two kit artists supporting eight level designers** — a
  small kit-art team directly multiplying a larger design team's content output. This is the single strongest
  piece of developer-sourced evidence in either file for the "shared modular kit" recommendation below.

---

## 3a. Scope-cutting as a density/scale technique — a documented developer mistake and a documented developer fix

Two developer-sourced anecdotes (Section 0) show Bethesda treating city/settlement scale as something to be
*tested and cut*, not fixed upfront:

- **The mistake**: Fallout 3's Washington D.C. was split into disconnected zones linked by an unpopular Metro
  system, a decision Joel Burgess later called "the big mistake I feel I made on [Fallout 3]" — an attempt to
  fix it late (removing zone dividers) failed only because the *test* of the fix was rushed, not because the
  fix itself was wrong. Lesson: **test compression/connectivity decisions early enough to actually act on the
  result**, not after the surrounding content is already built around the flawed structure.
- **The fix**: the central D.C. ruins were built at roughly twice their shipped size and fully polished before
  Todd Howard cut them down for scope/pacing reasons, and a large Rivet City assault mission was cut as too
  resource-intensive despite lead designer Emil Pagliarulo initially wanting it. Lesson: **build density
  generously in early passes, then deliberately cut back** rather than trying to hit the final density target
  on the first pass — it's easier to identify what to remove from something built too dense than to guess the
  right amount of density from zero.

---

## 4. Fallout 76 note (brief, for contrast)

- Fallout 76 is set in a *recently* post-war Appalachia (scarcity framing is even more extreme — nearly all
  human NPCs are simply absent at launch, replaced by robots and environmental storytelling, with human NPCs
  added later via updates). This is the most extreme version of "use the fiction to justify near-zero
  population" in the franchise, and confirms the pattern: **the emptier the intended feel, the more the
  fiction should foreground catastrophe/scarcity as the reason**, rather than leaving unexplained empty space.
  (General franchise knowledge; not independently re-verified with a fresh citation in this pass — flagged as
  background context rather than a sourced statistic.)

---

## Recommendations for our generator

1. **Let the fiction carry the population gap — state it, don't hide it.** Fallout's single biggest technique
   is not technical, it's narrative: nuclear war explains why a "big" settlement has 13-40 people. Our
   station's premise (a ring built for ~100,000 but never fully filled) should be stated in-world — e.g. the
   station was built for a larger population that never fully arrived, or has been in slow decline/partial
   evacuation — so a sparse simulated population reads as *intentional worldbuilding*, not a technical
   shortcon. Aim to have at least one in-world text source (terminal, sign, NPC line) per major district that
   explicitly acknowledges the gap between built capacity and actual occupancy.

2. **NPC "aliveness" budget: 1 NPC can cover 2-4 distinct locations via a scheduled routine, plus idle
   sandbox-style behavior, rather than needing 1 NPC per location.** Concretely, borrow the Package + Schedule
   + Sandbox pattern: each simulated NPC gets (a) 2-3 scheduled "travel to location X at hour Y" waypoints
   (home / workplace / social hub) and (b) a local idle behavior pool (interact with nearby props/furniture,
   randomized within a time window) for time not spent traveling. This makes even a very small NPC roster
   (tens, not thousands) visibly populate multiple parts of a district across a day/night cycle.

3. **Cap simulated settlement population deliberately, the way Fallout 4 caps settlements at ~20 settlers.**
   Pick a hard per-district or per-deck NPC cap (a specific tunable number, e.g. 15-30) justified by
   performance, and don't apologize for it in fiction — instead use environmental storytelling (idle personal
   quarters, "reserved but unused" signage, automated systems standing in for absent residents) to imply the
   difference between capacity and actual headcount, exactly as Sanctuary Hills' 20-settler cap coexists with
   its lore as a "small suburb of 14 prefab homes" without narrative tension.

4. **Build one shared modular structural kit and reuse it everywhere; vary layout and dressing, not geometry.**
   Directly mirror the Fallout 4 Workshop pattern — now confirmed by Bethesda's own lead level designer, not
   just a wiki: Joel Burgess describes a Fallout 3 kit of as few as **four art pieces** producing far more
   apparent variety than the piece count implies, and a two-artist kit team supporting eight level designers
   across 400+ Skyrim dungeon cells (Section 0). Define a constrained palette of wall/floor/roof/corridor/
   fixture pieces once, and have every station district (residential ring, market deck, industrial deck)
   assemble from that same kit with different arrangement, salvage/wear texture variants, and prop dressing.
   Grow variety over time by adding new pieces to the shared kit (as Bethesda did via DLC), not by hand-
   authoring unique buildings per district.

5. **Anchor each district with one unmistakable single landmark object, not building density.** Diamond
   City's stadium shell and Novac's giant dinosaur statue do more to make a location feel significant than
   raw building count ever could. Budget one strong, unique, non-modular landmark prop per named district on
   the ring (a distinctive structure, statue, or architectural centerpiece) as the primary "this place is
   real and important" signal, and let the surrounding modular kit buildings support it rather than compete
   with it.

6. **Total simulated-NPC budget for the whole map can be surprisingly small and still feel sufficient.**
   Fallout 3's entire game world runs on 319 characters total; New Vegas on ~380+. As an order-of-magnitude
   generator target: a station ring with a dozen or so named districts could run comfortably on **roughly
   15-40 actively-simulated NPCs per district (a few hundred total across the whole station)**, provided the
   scheduling/idle-behavior techniques above are used to make each one "cover" more perceived ground than a
   static NPC would. Treat this as the same order of magnitude Bethesda used for an entire open world, not
   per-location — flagged as an extrapolated target range for our use, not a claim that Bethesda used this
   exact per-district figure.

7. **Build generously, then cut deliberately — and test compression decisions early enough to act on the
   result.** Two developer-sourced anecdotes (Section 0 / 3a) both point the same direction: Bethesda built
   Fallout 3's D.C. ruins at roughly twice their shipped size and then cut them down once playtesting showed
   the smaller version worked better, but *failed* to properly re-test a fix to the D.C. Metro zone-division
   problem because the retest itself was rushed. For our generator: over-generate a district's density/detail
   in an early pass, playtest it, and cut back deliberately — but budget real time for testing any fix to a
   flawed compression/connectivity decision, not just for the initial build.

---

## Sources

### Developer talks and critical/academic analysis (priority sourcing pass)

- [Joel Burgess: "Skyrim's Modular Level Design — GDC 2013 Transcript"](http://blog.joelburgess.com/2013/04/skyrims-modular-level-design-gdc-2013.html)
- [Joel Burgess: "GDC 2014 Transcript: The Iterative Level Design Process"](http://blog.joelburgess.com/2014/07/gdc-2014-transcript-iterative-level.html)
- [TechRadar: "Vaulting ambition: Fallout 3 and the making of an RPG classic" (Samuel Horti)](https://www.techradar.com/news/vaulting-ambition-how-fallout-3-changed-the-game)
- [GameSpot: "GDC 2009: Fallout 3 lead opens game design vault"](https://www.gamespot.com/articles/gdc-2009-fallout-3-lead-opens-game-design-vault/1100-6206965/)
- [Game Studies: Kevin McClancy, "The Wasteland of the Real: Nostalgia and Simulacra in Fallout"](https://gamestudies.org/1802/articles/mcclancy)
- [Springer: "Worldbuilding, Nuclear Engagement, Resource Scarcity, and Raymond Williams' Structure of Feeling in Bethesda's Fallout 4"](https://link.springer.com/chapter/10.1007/978-3-031-67980-3_13)
- [Fallout Wiki: Novac](https://fallout.fandom.com/wiki/Novac)
- [Fallout Wiki: Diamond City (archive mirror)](https://fallout-archive.fandom.com/wiki/Diamond_City)

### Original pass sources

- [Fallout Wiki: Megaton](https://fallout.fandom.com/wiki/Megaton)
- [Gamerant: Every Major City In Fallout 4 & How Many NPCs Live There](https://gamerant.com/fallout-four-major-city-npc-population/)
- [Fallout Wiki: Goodsprings](https://fallout.wiki/wiki/Goodsprings)
- [TheGamer: Fallout New Vegas — How Many NPCs Are In The Game?](https://www.thegamer.com/fallout-new-vegas-how-many-npcs/)
- [Fallout Wiki: Fallout 3 characters](https://fallout.fandom.com/wiki/Fallout_3_characters)
- [alternatehistory.com forum: Fallout 3 Capital Wasteland population discussion](https://www.alternatehistory.com/forum/threads/fallout-3-future-of-the-capital-wasteland.196679/)
- [Fallout Wiki: Sanctuary Hills](https://fallout.fandom.com/wiki/Sanctuary_Hills)
- [Steam Community: Why is my Sanctuary Hills population stuck at 20?](https://steamcommunity.com/app/377160/discussions/0/458604254433931291/)
- [Wikipedia: Radiant AI](https://en.wikipedia.org/wiki/Radiant_AI)
- [Medium: Lost Features — A Critical Essay on TES IV: Oblivion's Radiant AI](https://medium.com/@gatherer286/lost-features-a-critical-essay-on-tes-iv-oblivions-radiant-ai-a0150144ddef)
- [paavohtl blog: What was Radiant AI, anyway?](https://blog.paavo.me/radiant-ai/)
- [GECK Wiki: Category:Packages](https://geckwiki.com/index.php/Category:Packages)
- [GECK Wiki: Sandbox Package](https://geckwiki.com/index.php/Sandbox_Package)
- [Fallout Wiki: Fallout 4 settlement objects](https://fallout.fandom.com/wiki/Fallout_4_settlement_objects)
