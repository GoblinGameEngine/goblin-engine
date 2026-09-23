# Elevation, Terrain, and Verticality as Scale-Illusion Techniques

Research focus: how open-world games use elevation change, terrain undulation, and
verticality to make a compressed map feel larger than it is, gate exploration
pacing, and separate districts/biomes without spending footprint. Games covered:
**The Legend of Zelda: Breath of the Wild / Tears of the Kingdom**, **Skyrim**,
**The Witcher 3** (Skellige vs. Velen/Novigrad), **Red Dead Redemption 2**
(Grizzlies vs. Heartlands), **Kingdom Come: Deliverance**, and **Horizon Zero
Dawn / Forbidden West**. This file assumes the prior population/density research
in this directory (gta_series.md, fallout_series.md, elder_scrolls_series.md,
witcher_3.md, other_open_world_rpgs.md) as context and does not repeat their
NPC-density/facade findings except where elevation directly interacts with them
(e.g., Skellige/Velen terrain and Toussaint's cliff-city).

**Research-process note:** this pass had no working web-search access (the
session's search budget was already exhausted by the prior research files, and
this is very likely why an earlier attempt at this file was cut short) — all
sourcing below comes from direct page fetches (Wikipedia, UESP, developer
interview sites, IGN, PCGamesN, 80.lv) rather than search-driven discovery. Some
well-known claims about specific GDC talks (see BOTW section) could not be
independently re-verified against a primary transcript in this pass and are
flagged accordingly rather than asserted as confirmed quotes.

---

## 1. The Legend of Zelda: Breath of the Wild / Tears of the Kingdom

### Sightline control and the "climb anything" mechanic

BOTW's single most load-bearing design decision for making a modestly-sized
Hyrule feel enormous is that **the player can climb almost any surface**, which
Wikipedia's development summary describes as letting "players reach areas
without following a particular path." Digital Trends is quoted (via Wikipedia)
describing this as freedom of movement that "broke the genre open, pushing
developers to rethink how players interact with the world," explicitly noting
it forced "extra thought into vertical design," and drawing a contrast with
"Ubisoft-style" games that fill a map with signposted points of interest —
BOTW instead lets terrain and verticality themselves generate discovery.
[Wikipedia: The Legend of Zelda: Breath of the Wild](https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild)

The starting area, the **Great Plateau**, was deliberately designed as a
plateau — elevated above the surrounding terrain — specifically "so that
players can see the world's expansive environments" from the outset. This is a
directly documented design choice: elevation used as a one-time, up-front
"establishing shot" that lets the game imply the scale of the whole map without
building all of it, then lets the player spend the rest of the game discovering
that the straight-line view from the Plateau does not correspond to a straight
walkable path. [Wikipedia: The Legend of Zelda: Breath of the Wild](https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild)

**Terrain authoring**: the landscape was based on real locations in and around
Kyoto (director Hidemaro Fujibayashi's hometown), and **Monolith Soft** (the
Xenoblade Chronicles developer) was brought in specifically to assist with
**topographical level design**, credited by Nintendo for their experience
building open-world game terrain. Producer Eiji Aonuma has also stated the
art direction was inspired by **gouache painting and en plein air technique**
— a visual-legibility choice explicitly meant "to help identify the vast
world," i.e., color/value composition was tuned so that distant terrain forms
(ridgelines, mountains) read clearly enough at a distance to function as
navigation anchors. [Wikipedia: The Legend of Zelda: Breath of the Wild](https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild)

At E3 2016, Nintendo stated Breath of the Wild's open world is **12 times
larger** than Twilight Princess's, and that the E3 demo area represented only
**1%** of the total map — a concrete, sourced scale-multiplier statement,
though (as with GTA/Fallout population claims in the earlier research files)
Nintendo did not publish an absolute km²/sq-mile figure alongside it in this
source. [IGN: E3 2016 — Zelda: Breath of the Wild's Open World is 12 Times
Bigger than Twilight Princess](https://www.ign.com/articles/2016/06/14/e3-2016-zelda-breath-of-the-wilds-open-world-is-12-times-bigger-than-twilight-princess)

**On the "triangle rule" / landmark-visibility claim specifically:** this
technique — designing terrain so that at least one or two additional points
of interest are always visible from any given landmark, deliberately avoiding
straight walkable lines between them, forcing detours around ridgelines and
valleys — is widely discussed in enthusiast and critical game-design analysis
(e.g., video essays such as Game Maker's Toolkit's coverage of BOTW's landmark
design) as the core mechanism behind Nintendo's publicly-stated GDC 2017 talk
("The Legend of Zelda: Breath of the Wild: A Distinct Approach to an
Open-World Game," presented by Fujibayashi and colleagues). **This research
pass could not independently re-fetch a primary transcript or first-party
write-up of that specific talk** (GDC Vault requires a paid membership login,
and general web search was unavailable) — so the "triangle" framing is
reported here as a well-established secondary characterization of Nintendo's
publicly-known design philosophy, not as a verified direct quote. The
underlying, independently-sourced facts above (Great Plateau vantage design,
Monolith Soft topographical assist, climb-anywhere mechanic, gouache-inspired
legibility) are the verified load-bearing evidence for the same conclusion:
**BOTW uses terrain elevation explicitly to control what's visible from where,
and deliberately avoids letting a visible landmark imply a walkable straight
line to it.**

### Tears of the Kingdom's addition: verticality as literal new content layer

TotK (2023) extended the same map footprint by adding sky islands above and
cave/Depths layers below Hyrule's surface — i.e., where BOTW used terrain
elevation to control *sightlines across* one ground plane, TotK used vertical
stacking to add *entirely new traversable volume* on the same footprint
without expanding the map's outer boundary. (General franchise knowledge; not
independently re-verified with a fresh citation in this pass — flagged as
background context rather than a sourced statistic, consistent with how
other_open_world_rpgs.md flags the Fallout 76 note.)

---

## 2. Skyrim: terrain as an explicit anti-flatness design choice

Skyrim's Wikipedia development section states directly: the team "set the
game in the province of Skyrim, designing it by hand. While similar in size
to Oblivion's game world of Cyrodiil, **the mountainous topography of the
world inflates the game space and makes it more difficult to traverse than
Cyrodiil, which was relatively flat.**" This is about as explicit a
documented statement of "elevation as scale illusion" as exists in this
research: two maps of comparable raw area, where the mountainous one reads
(and plays) as bigger purely because of terrain relief.
[The Elder Scrolls V: Skyrim — Wikipedia](https://en.wikipedia.org/wiki/The_Elder_Scrolls_V:_Skyrim)

**Terrain authoring approach — a documented procedural-to-hand-crafted
reversal:** the same section states that "efforts to make Skyrim's world feel
hand-crafted extended to the team **abandoning the use of generated
landscapes as they had done in Oblivion**." Oblivion's Cyrodiil terrain had
relied on procedurally generated landscape data; for Skyrim, Bethesda
deliberately went fully hand-authored instead, specifically in service of
making the terrain feel less generic/interchangeable and more purposefully
composed — a direct, sourced counter-example to "just run noise and be done,"
and a useful data point for our own hybrid-vs-hand-authored decision.
[The Elder Scrolls V: Skyrim — Wikipedia](https://en.wikipedia.org/wiki/The_Elder_Scrolls_V:_Skyrim)

**Numeric elevation figure**: the Throat of the World, Skyrim's tallest
mountain (home to the Greybeards' monastery) and explicitly the tallest peak
in the setting's home continent, measures **766.5 meters (838.3 yards) above
sea level "according to the Creation Kit"** — i.e., a figure pulled directly
from the shipped game data files, not a marketing estimate.
[UESP: Skyrim:Throat of the World](https://en.uesp.net/wiki/Skyrim:Throat_of_the_World)

**Relief-to-footprint ratio (derived, not sourced — flagged as our own
calculation):** Skyrim's overworld is commonly cited at roughly **16 square
miles (~41.4 km²)**, per a contemporaneous 1UP review headline cited on
Wikipedia. [The Elder Scrolls V: Skyrim — Wikipedia](https://en.wikipedia.org/wiki/The_Elder_Scrolls_V:_Skyrim)
Treating that footprint as roughly square gives a side length of ≈6.4 km.
Against a summit elevation of 766.5 m, that yields a **relief-to-footprint
ratio of roughly 766.5 m / 6,430 m ≈ 0.12 (about 12%)** — i.e., Skyrim's
single tallest peak rises to roughly a ninth to an eighth of the map's own
linear span. This is offered as a rough order-of-magnitude anchor, analogous
in spirit to the meander-wavelength-to-channel-width ratio used in
`research/hydrology_drainage/meander_geometry.md`, not as a precise or
universal constant — Skyrim's overall relief distribution is also uneven
(holds like Hjaalmarch/Morthal sit in low marshland while The Reach and the
area around the Throat of the World are dramatically higher), so a single
ratio understates local variation.

**Also relevant to district separation (see elder_scrolls_series.md for the
population/NPC side of this)**: Skyrim's nine holds are given genuinely
distinct terrain identities — Hjaalmarch/Morthal's marsh and lowland fog,
The Reach's canyon/mountain terrain around Markarth, the alpine terrain
around the Throat of the World, Winterhold's exposed coastal cliffs and
post-collapse geography — meaning elevation and terrain type, not just
distance, do a large share of the work making nine holds within one
comparatively small province feel like genuinely different regions.

---

## 3. The Witcher 3: elevation as a sightline tool, a pacing tool, and a wealth-stratification tool

The prior research file (`witcher_3.md`) already covers Velen's **terrain-first
placement workflow** (CD Projekt Red placed mountains/rivers/lakes first, then
decided settlement locations relative to that terrain) — this section adds the
elevation-specific detail that file did not cover.

**Terrain used directly to control sightlines to quest content — a documented
case of literally moving a mountain:** CDPR Senior Environment Artist Michał
Janiszewski, in an 80.lv interview, describes a concrete case where "a mountain
was obstructing the visibility of an important quest location, so we had to
remove the mountain and replaced it with a lake and a small village on the
shore instead." This is a first-party confirmation that terrain height in
Witcher 3 was treated as a *tunable sightline-control variable*, adjusted
after the fact specifically because it was blocking (or, implicitly, could be
used to hide) content visibility — the same lever GTA/Skyrim use to hide
scale, deployed here in the opposite direction (removing terrain that was
*over-hiding* something the designers wanted visible).
[80.lv: World Building of Witcher 3](https://80.lv/articles/world-building-of-witcher-3)

**Terrain height explicitly named as a pacing/variety tool, independent of
plot:** the same interview states the biggest open-world design challenge is
making long traversal "beautiful, believable and fun to explore," and that
the team had to "break up the forest scenery with some clearings, terrain
height, or water" to avoid monotony during extended travel — terrain
undulation is named in the same breath as clearings and water as one of the
three primary levers for breaking up a long traverse. For "mountainous
regions of the world, or islands like Skellige," Janiszewski specifically
notes the team had "ample room to provide players with breathtaking and
varied vistas with well-planned settlements or other elements visible in the
background" — i.e., high terrain relief was used as a *vista/reveal
generator*, deliberately composing settlements to be dramatically visible
from elevation rather than hidden. [80.lv: World Building of Witcher 3](https://80.lv/articles/world-building-of-witcher-3)

**Elevation as social/wealth stratification within a single city:** the city
of **Toussaint** (Blood and Wine expansion) is built directly on top of a
cliff, with poor districts at the bottom and richer districts appearing as
the player climbs higher behind the city walls — the same "elevation = status"
grammar real hillside cities use (and which Witcher 3's own city-building
process treated as a deliberate district-differentiation tool, alongside the
wall-based district system witcher_3.md already documents for Novigrad).
[80.lv: World Building of Witcher 3](https://80.lv/articles/world-building-of-witcher-3)

**Skellige vs. Velen/Novigrad as the clearest region-level contrast in this
research batch:** Skellige's fjords, cliffs, and mountainous islands (visually
referencing Norse/Scandinavian terrain, consistent with its Norse-Gael
culture) sit in stark relief-contrast against Velen's marshy lowland and
Novigrad's flat urban footprint. Because CDPR's terrain-first placement
workflow (documented in witcher_3.md) put geography before settlement, this
means the *region itself* — not travel distance — is what tells the player
"you have left one kind of place and entered another." A relatively modest
total map (commonly discussed in the ~100+ km² class, though this research
pass could not re-verify an exact figure without search access — flagged as
unconfirmed) reads as three or four genuinely distinct macro-regions largely
because of this terrain-type/elevation contrast, not because the regions are
geographically far apart.

---

## 4. Red Dead Redemption 2: mountain-to-plain relief as the map's primary internal variety generator

RDR2's five constituent regions, per Wikipedia's plot/setting summary, are
built around explicit terrain-type contrast:

- **Ambarino**: "a sparsely populated **mountain wilderness**," containing the
  Grizzlies mountain range and only one settlement (the Wapiti Indian
  Reservation) — the map's most sparsely built, highest-relief region.
- **New Hanover**: "a sweeping valley, woody foothills, and plains" — i.e., a
  deliberate transition zone with graduated relief between Ambarino's peaks
  and the flatter regions to the south, home to Valentine (the "Heartlands"
  cattle-town case discussed in other_open_world_rpgs.md).
- **Lemoyne**: bayous and plantations (Deep South analogue), functionally flat
  wetland terrain, contrasting sharply with Ambarino.
- **West Elizabeth**: "wide plains and dense forests," later expanded
  northward with the mountain resort town of Strawberry — another
  plains/mountain contrast pairing within a single region.
- **New Austin**: arid desert/canyon terrain on the Mexican border.

[Red Dead Redemption 2 — Wikipedia](https://en.wikipedia.org/wiki/Red_Dead_Redemption_2)

**Why this matters for scale illusion specifically**: the Grizzlies (Ambarino)
sit at the literal opposite terrain extreme from the Heartlands (the flat
central plains around Valentine/New Hanover) within a single, comparatively
compact overall map. Rockstar's own public commentary on RDR2's technical
ambitions has been unusually limited compared to Bethesda/CDPR — as the
prior research file (other_open_world_rpgs.md) already notes, Rockstar's
public GDC talks on RDR2 covered locomotion/animation/wildlife rendering
rather than world-terrain design directly, so **no primary Rockstar
statement about deliberate relief-to-footprint ratios was found in this
research pass either** — this section's conclusions are inferred from the
shipped map's observed regional design (mountain wilderness immediately
adjacent to flat cattle country, both reachable within a single in-game day's
travel) rather than a sourced developer quote, and should be treated
accordingly.

**Practical takeaway independent of exact sourcing**: RDR2 is the clearest
example in this research batch of using **terrain-type juxtaposition itself**
(snow-capped alpine wilderness bordering flat farmland bordering swamp
bordering desert) as the primary technique for making five different named
regions feel like they belong to different climates/latitudes/cultures
without requiring the vast real-world distances that would actually separate
such terrain types (RDR2's real-world analogue commentary, cited in
gta_series.md-adjacent research, notes a genuinely equivalent-scope real
region would be "beyond the technical possibilities for any video game").

---

## 5. Kingdom Come: Deliverance: elevation as a byproduct of honest real-world reconstruction

KCD's terrain is a special case in this research batch: because Warhorse
Studios reconstructed real Bohemian terrain (centered on Stříbrná Skalice,
~50 km south of Prague) from **satellite maps**, the game's hill-and-valley
relief is not an artificially engineered scale-illusion device — it is simply
what that real landscape looks like, imported close to 1:1 in local detail
even while (per other_open_world_rpgs.md) the macro-scale distance *between*
settlements was deliberately compressed. [PCGamesN: The obsessive historical
accuracy of Kingdom Come: Deliverance](https://www.pcgamesn.com/kingdom-come-deliverance/kingdom-come-deliverance-historical-accuracy)

The same PCGamesN piece includes a framing line directly relevant to this
research question: "We've reached the end of the era in which simply telling
us we can go all the way to that mountain on the horizon is impressive. We
need some kind of meaning to the giant spaces that games now occupy" — a
critical observation that **visible-but-reachable terrain relief, by itself,
stopped being a novelty** by the time KCD shipped (2018), and that
historically/narratively *grounded* terrain (real Bohemian hills, real
villages sited the way real medieval villages were actually sited relative to
terrain) is what gives KCD's elevation change meaning beyond raw visual
spectacle. [PCGamesN: The obsessive historical accuracy of Kingdom Come:
Deliverance](https://www.pcgamesn.com/kingdom-come-deliverance/kingdom-come-deliverance-historical-accuracy)

No specific numeric elevation-relief figure for KCD's map was found in this
research pass (flagged as not sourced) — qualitatively, the real Bohemian
highland terrain the game reconstructs is rolling hill country (broad,
gentle elevation change measured in the tens-to-low-hundreds of meters
locally), not high-alpine terrain — closer in character to Velen/New Hanover
than to Skyrim's mountains or Skellige's cliffs.

---

## 6. Horizon Zero Dawn / Forbidden West: hybrid procedural + hand-crafted terrain, biome-as-elevation-function

This is the clearest documented **hybrid terrain-authoring pipeline** in this
research batch. Per Wikipedia's development summary: "the environment was
built through a mix of **procedural generation and hand-crafting**. While
**vegetation and rivers used procedural placement, rock formations and
mountains were hand-made**." The team also built "World Data Maps" to drive
shaders/placement systems from environmental conditions like humidity and
temperature (enabling detail like fireflies appearing only near bushes at
night) — i.e., climate/biome data layered on top of hand-authored base
terrain, rather than terrain itself being climate-driven procedural output.
[Horizon Zero Dawn — Wikipedia](https://en.wikipedia.org/wiki/Horizon_Zero_Dawn)

This is a directly useful, sourced data point for our own terrain-authoring
choice: Guerrilla Games' split was **hand-author the macro landform (the part
that defines sightlines, ridgelines, and scale illusion) and let the cheaper,
more proceduralizable content (vegetation, rivers) fill in around that
hand-placed skeleton** — the opposite allocation from a "generate everything
with noise" approach, and consistent with Skyrim's decision (above) to
abandon procedural landscape generation entirely.

Guerrilla also built **two separate navigation systems for elevation**: a
navigation mesh for ground-based machine pathing that "recognises and adapts
to changes in local terrain," and a completely separate **runtime-generated
heightmap of the flyable airspace** for aerial machine navigation — a
concrete engineering example of elevation data being consumed differently by
different systems (ground pathing vs. air pathing) rather than treated as a
single undifferentiated terrain layer. [Horizon Zero Dawn — Wikipedia](https://en.wikipedia.org/wiki/Horizon_Zero_Dawn)

**Biome variety on a compact map**: Horizon's tribes are explicitly tied to
terrain type — the Nora are mountain-dwelling hunter-gatherers, the Carja are
desert-dwelling city builders — meaning, as in RDR2, **culture/settlement type
is bound to terrain/elevation type**, letting a relatively compact explorable
map read as containing multiple distinct civilizations because their terrain
(and the elevation-driven biome that terrain produces) visibly differs, not
because they are separated by unbridgeable real-world distance. No official
km²/sq-mile figure for Horizon's map was found in this research pass
(flagged as not sourced).

---

## Cross-game synthesis

| Game | Elevation used primarily for | Terrain authoring | Numeric relief data found |
|---|---|---|---|
| BOTW/TotK | Sightline control, vantage-point reveal, non-straight-line pathing | Hand-authored w/ Monolith Soft topography assist; gouache-legibility art direction | 12× larger than Twilight Princess (no absolute figure found) |
| Skyrim | Explicit "inflate the game space" scale illusion vs. flat Oblivion | Hand-authored (deliberately abandoned Oblivion's generated landscapes) | Throat of the World 766.5 m; ~16 sq mi (41.4 km²) footprint; derived relief/footprint ≈ 0.12 |
| Witcher 3 | Sightline tuning (mountain removed for visibility), pacing/vista variety, wealth stratification (Toussaint), region-type separation (Skellige vs. Velen/Novigrad) | Terrain-first placement (per witcher_3.md); grey-box iteration; mountains adjusted post-hoc for sightlines | No verified absolute figures this pass |
| RDR2 | Region-to-region terrain-type contrast (mountain/plains/bayou/desert) as identity generator | Not documented in sources found this pass | No verified absolute figures this pass |
| KCD | Honest reconstruction of real hill country; narrative/historical grounding over spectacle | Satellite-map-based real-terrain reconstruction, macro-spacing compressed | No verified absolute figures this pass |
| HZD/Forbidden West | Biome-as-elevation-function (mountain vs. desert tribes), separate ground/air elevation systems | Hybrid: hand-made mountains/rock, procedural vegetation/rivers | No verified absolute figures this pass |

**Common thread**: every game in this batch that documents its terrain-authoring
choice explicitly (Skyrim, HZD) chose **hand-authored or hand-finished macro
landforms** over pure procedural generation, specifically because raw
procedural terrain reads as generic/interchangeable and undermines the
sightline-control and vista-composition techniques above — procedural
generation, where used at all (HZD's vegetation/rivers), was reserved for
*detail* layered on a hand-placed terrain skeleton, not for the skeleton
itself.

---

## Recommendations for our generator

**The central tension, stated explicitly**: our station's floor is
~1,000 m wide (wall-to-wall, radial cross-section) by ~3,142 m circumference
(the walkable loop distance around the ring), giving a total floor area of
roughly **3.14 km²** (1,000 m × 3,142 m) — smaller than Skyrim's ~41.4 km²
overworld footprint by more than an order of magnitude, and smaller than any
of the other games surveyed here. Unlike every game above, our "terrain" is
not free-standing landscape — it's the interior floor of a spinning ring,
where **usable flat ground for buildings/streets is the scarce resource the
generator exists to place**, and where a hard ceiling height (set by the
station's structural radius and spin-gravity physics — confirmed by reading
`godot_project/scripts/world/StationRingBuilder.gd`, which currently builds a
flat floor/ceiling pair at fixed radii) puts a hard ceiling on how much
vertical relief is even physically available before terrain starts colliding
with the deck above or eating into the artificial-gravity-critical rotation
radius. This is a constraint none of the surveyed open-world games have to
deal with — Skyrim's mountains can rise as high as the art team wants; ours
cannot.

1. **Budget elevation relief as a small, explicit fraction of ceiling
   height, not of floor footprint.** Skyrim's derived relief-to-footprint
   ratio (~0.12, i.e., its tallest peak is roughly 1/8th–1/9th of the map's
   linear span) is not directly transferable to a station ring, because our
   binding constraint isn't linear map span, it's vertical clearance under
   the next deck. Concretely: reserve a small, fixed vertical budget (e.g.,
   on the order of single-digit percent of the floor-to-ceiling height
   `ceiling_height` already defined in `StationRingBuilder.gd`) for terrain
   relief, and treat that budget as non-negotiable structural headroom, not
   a target to fill — a station with rolling hills that nearly touch the
   ceiling reads as a mistake, not grandeur, unlike an open sky in a
   planetary game.

2. **Distribute relief as gentle, broad undulation along most of the ring,
   with 1-2 concentrated higher-relief "ridgeline" zones, not uniform gentle
   rolling everywhere.** This directly mirrors the games surveyed: no game
   here uses uniform terrain height — Skyrim contrasts marshland
   (Hjaalmarch) against alpine terrain (near the Throat of the World);
   Witcher 3 contrasts Skellige's cliffs against Velen/Novigrad's flatness;
   RDR2 contrasts the Grizzlies against the Heartlands. For the station:
   pick one or two arc-segments of the ring (analogous to a "mountain
   district") to carry most of the available vertical relief budget as a
   deliberately raised/lowered terrain feature (a sunken agricultural
   trench, a raised industrial spine, a stepped hillside residential
   district), and keep the remaining majority of the ring's circumference
   close to flat, buildable ground. This both (a) reads as more varied than
   uniform gentle rolling would, at the same total relief budget, and
   (b) preserves the most contiguous flat ground for the districts that
   actually need it (markets, plazas, street grids).

3. **Use elevation to block sightlines along the ring's circumference, not
   just across its width.** Because the ring is a closed loop, a player at
   any point can in principle see very far around the curve (limited mainly
   by the ring's own curvature and any structural spokes) — this is exactly
   analogous to BOTW's problem of a flat map letting players see "the edge."
   A raised terrain feature (a hill, a raised deck-support structure
   dressed as a ridge, a stepped district) placed across the walking path at
   intervals prevents a player from seeing more than one or two districts
   ahead at once, which (per the BOTW/Witcher 3 sightline-control findings
   above) makes the ~3,142 m loop feel considerably longer to walk than its
   straight-line/curvature-implied distance, and turns "cresting a rise"
   into a discovery moment revealing the next district — directly
   reproducing BOTW's Great-Plateau-style reveal technique and Skyrim's
   "inflates the game space" effect, at station scale.

4. **Follow Skyrim and HZD's documented pattern: hand-author (or
   hand-tune) the macro relief skeleton; reserve procedural/noise-based
   generation for surface detail layered on top.** Both sourced
   terrain-authoring cases in this research explicitly avoided pure
   procedural macro-terrain because it reads as generic and undermines
   deliberate sightline/vista composition. For our generator, this suggests:
   define the ring's relief profile (where the 1-2 ridgeline zones sit, how
   tall, how the transition to flat ground is shaped) as a small number of
   designer/generator-level parameters placed deliberately per district
   (mirroring HZD's hand-made "rock formations and mountains"), and reserve
   any noise-based procedural variation for secondary surface detail
   (ground texture roughness, minor rubble/terrain-scatter, planter-bed
   micro-relief) — mirroring HZD's procedural vegetation/rivers layered over
   hand-placed mountains.

5. **Tie elevation to district/biome identity, the way RDR2 and HZD tie
   terrain type to culture.** Rather than treating relief as purely a
   sightline tool, assign the station's raised/lowered terrain zones to
   specific district types where elevation change is diegetically motivated
   (e.g., a raised agricultural terrace catching simulated "high" light in a
   rotating habitat, a sunken industrial/maintenance trench along the spine,
   a stepped residential district climbing toward a raised civic/religious
   structure — echoing Toussaint's elevation-as-wealth-stratification
   grammar). This makes the elevation choice read as purposeful world-design
   rather than arbitrary noise, at zero extra footprint cost.

6. **Do not let terrain relief consume more than a small minority of total
   buildable flat area.** Given the acute flat-ground scarcity relative to
   every other game surveyed (3.14 km² total vs. 41+ km² for Skyrim alone),
   the generator should treat "flat, buildable ground" as the default state
   and "elevated/depressed terrain feature" as the deliberately-budgeted
   exception — a strict reversal of a planetary open-world game's economy,
   where flat ground is the exception and terrain is the default. A
   reasonable starting target: **80-90% of the ring's circumference stays
   within a shallow, easily-buildable grade band, with the remaining
   10-20% carrying the concentrated ridgeline/depression relief** described
   in recommendation 2 — treat this ratio as a tunable generator parameter
   to validate against actual building/street placement once the terrain
   pass is implemented, not as a fixed constant.

---

### Sources

- [The Legend of Zelda: Breath of the Wild — Wikipedia](https://en.wikipedia.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild)
- [IGN: E3 2016 — Zelda: Breath of the Wild's Open World is 12 Times Bigger than Twilight Princess](https://www.ign.com/articles/2016/06/14/e3-2016-zelda-breath-of-the-wilds-open-world-is-12-times-bigger-than-twilight-princess)
- [The Elder Scrolls V: Skyrim — Wikipedia](https://en.wikipedia.org/wiki/The_Elder_Scrolls_V:_Skyrim)
- [UESP: Skyrim:Throat of the World](https://en.uesp.net/wiki/Skyrim:Throat_of_the_World)
- [80.lv: World Building of Witcher 3](https://80.lv/articles/world-building-of-witcher-3)
- [Red Dead Redemption 2 — Wikipedia](https://en.wikipedia.org/wiki/Red_Dead_Redemption_2)
- [PCGamesN: The obsessive historical accuracy of Kingdom Come: Deliverance, and how it makes for a better RPG](https://www.pcgamesn.com/kingdom-come-deliverance/kingdom-come-deliverance-historical-accuracy)
- [Horizon Zero Dawn — Wikipedia](https://en.wikipedia.org/wiki/Horizon_Zero_Dawn)
- [Kingdom Come: Deliverance — Wikipedia](https://en.wikipedia.org/wiki/Kingdom_Come:_Deliverance)
- This directory's own prior research: `witcher_3.md`, `other_open_world_rpgs.md`, `elder_scrolls_series.md` (read for context per task instructions, not re-cited for facts already sourced there)
- `research/hydrology_drainage/meander_geometry.md` (referenced for the "ratio as a design constant" framing convention used in Recommendation/derived-ratio sections)
- `godot_project/scripts/world/StationRingBuilder.gd` (read directly to confirm current flat floor/ceiling implementation and the radius/width/ceiling_height parameters referenced in the Recommendations section)

**Explicitly flagged gaps from this pass** (would benefit from a follow-up
pass once web search is available again): a verified primary-source quote or
transcript excerpt for BOTW's GDC 2017 talk and the specific "triangle"
landmark-visibility claim; absolute km²/sq-mile figures for BOTW, Witcher 3,
RDR2, KCD, and Horizon Zero Dawn's maps; any Rockstar-sourced statement about
RDR2's terrain design process; any Warhorse-sourced numeric elevation-relief
figure for KCD's map; confirmation of whether erosion-simulation tools
(e.g., World Machine, Houdini's erosion SOPs) were used by any of these
studios specifically — this research pass found no citable confirmation
either way for any of the six games and did not include an unsupported claim
about erosion-simulation usage as a result.
