# The Elder Scrolls Series: Faking Scale in "Major Cities"

Focus: Skyrim (Whiterun, Solitude, Windhelm, Markarth), with Oblivion and Morrowind
as contrasting design points. Research goal: how Bethesda makes settlements the
lore describes as major population centers (holds capitals, provincial capitals)
feel real with a tiny actual simulated population, and how Radiant AI schedules
make that tiny population feel alive.

---

## 1. The implied-vs-actual population gap

Skyrim's in-lore population for its holds is never given an exact number in-game,
but community lore analysis built from in-game context clues (tax records, census
dialogue, army sizes referenced in quests) puts numbers like Whiterun Hold at
roughly **275,000**, with the city of Whiterun itself estimated around
**110,000–115,000** including the area just outside the walls. The *actual*
simulated population is a rounding error of that:

| City | Actual NPC population (UESP / community counts) |
|---|---|
| Whiterun | 73 (74 with Hearthfire) |
| Markarth | 65 |
| Solitude | 62 |
| Riften | 58 |
| Windhelm | 56 |
| Dawnstar | 33 |
| Morthal | 23 |
| Falkreath | 20 |
| Winterhold | 29 |

Total unique named NPCs across all of Skyrim (UESP demographics count,
dungeon-dwellers/random encounters/most DLC excluded): **659**, spread across the
nine holds (Whiterun Hold 105, The Rift 118, The Reach 114, Haafingar 90,
Eastmarch 84, Winterhold 37, Pale 41, Falkreath 33, Hjaalmarch 26).

So the ratio between "what the fiction claims" and "what is actually simulated"
is on the order of **1,000:1 to 1,500:1** for the biggest holds. Bethesda never
tries to close this gap with raw NPC count — it closes it with **presentation**:

- **Layered, unenterable background architecture.** Whiterun's Wind District and
  the tiered city (Plains District → Wind District, connected by stairways, with
  Dragonsreach looming above) reads as a real hill-city skyline even though only
  a fraction of the visible structures are enterable. Windhelm's long, roofed
  "Snow Quarter" street of houses reads as a dense old city even with a handful
  of actual households.
- **Scale-signaling architecture**: oversized walls, gatehouses, and public
  buildings (Blue Palace, Dragonsreach, the Palace of the Kings) that dwarf the
  handful of NPCs living around them, borrowing the visual grammar of a real
  capital city without the population to match.
- **Verbal scale-signaling**: guard/NPC dialogue and books refer to holds, armies,
  and trade in terms that imply a much larger world than what's rendered — the
  fiction does the population math that the engine can't render.
- **Compressed but legible city structure**: districts (market/plains district,
  temple district, residential district) are laid out as if the city were much
  bigger, so the *shape* of a real city (specialized zones connected by a small
  number of primary paths) is present even though each zone is only 3–8
  buildings.

This same design compromise is visible across the series but at very different
ambition levels — see section 4.

## 2. Radiant AI: how a handful of NPCs feel alive

"Radiant AI" (introduced in Oblivion, 2006; carried forward and technically
matured, but *behaviorally scaled back*, in Skyrim, 2011) is Bethesda's system
for giving NPCs autonomous daily routines instead of static, rooted placement.

**Core mechanic**: instead of scripting an NPC's exact path and animation frame
by frame, designers assign **schedule packages** — high-level goals tied to a
location and a time window, e.g. "be at the forge and work, 8am–6pm," "be at the
tavern and socialize, 6pm–10pm," "be at this bed and sleep, 10pm–8am." The AI
independently pathfinds, picks appropriate idle animations/dialogue barks, and
resolves conflicts (an occupied bed, a blocked door) on its own, rather than the
designer hand-animating each transition. Todd Howard framed the goal as giving
the world an "organic feel" — NPCs that are never just standing in one spot
waiting to be talked to.

**Package types actually used per NPC** are small in number — typically only a
handful of state changes across 24 hours (sleep, one or two work blocks, one or
two social/eat blocks, a "wander" or "patrol" filler state), not a continuous
simulation. The believability comes from *time-of-day gating* (light changes,
shops opening/closing, doors locking) synchronized with those state changes, not
from behavioral complexity.

**Oblivion's version was far more ambitious and had to be cut down before
ship.** Early Radiant AI let NPCs make truly autonomous choices to satisfy needs
(hunger, sleep, safety) using the environment — which produced now-famous
failure cases: NPCs bought out an entire shop's stock, murdered rivals for food
or position, or otherwise "solved" their goals in ways that broke quests and
towns. Bethesda scaled the simulation back substantially before release, and
Skyrim's Radiant AI is *more curated/scripted* than Oblivion's original vision,
trading emergent unpredictability for reliability — schedules are simpler and
more scripted-feeling but far more stable. A Bethesda designer has since
described continued investment in Radiant AI as "enormous" for the return it
gives, which is part of why so few other studios have copied it wholesale.

**Radiant Story** (Skyrim addition) is the complementary system that generates
dynamic quest content (bounties, "a family member has been kidnapped," etc.)
using the existing small NPC roster and world locations, rather than requiring
bespoke unique content — another lever for making the same finite cast of NPCs
generate more perceived world activity.

## 3. Modular architecture and kit reuse (the actual build economics)

The clearest documented numbers on how few unique art assets support Skyrim's
world come from Bethesda level designer **Joel Burgess's GDC 2013 talk**
("Creating a Landscape of Emergent Stories" / Skyrim's modular level design):

- Total Bethesda Game Studios dev team: ~90 people.
- Dungeon/interior content team: only **10 people** — **2 full-time kit
  (modular art) artists** and **8 level designers**.
- Those 2 kit artists produced **7 modular kits** over the project, which the 8
  level designers used to assemble **"well over 400 cells"** (unique loaded
  interior spaces) over roughly **2.5 years**.
- The **Cave kit** alone was reused **200+ times** across the game, built from 7
  sub-kits and roughly 50 individual hallway/room pieces — a small parts
  catalog assembled combinatorially into hundreds of "different" caves.
- By contrast, a narrow-purpose kit like the **Ratway** (a one-off sewer/slum
  location) was only used twice, and had a much smaller parts set (3 sub-kits, 7
  pieces per hallway) — Bethesda scales kit *investment* to reuse count, a
  directly reusable cost/benefit rule.
- World scope for the whole game: a ~16 square mile overworld, **5 major
  cities**, 2 hidden worldspaces, **300+ dungeons**, **140+ points of interest**,
  and **37 towns/farms/villages** — all built from that same small library of
  kits plus city-specific unique set-dressing.

The takeaway: **a two-person kit team feeding eight designers produced the
entire dungeon layer of the game.** Uniqueness at the macro scale (300+
distinctly-named, distinctly-laid-out dungeons) comes from *combinatorial reuse*
of a handful of kits, not from unique authored geometry per location. The same
approach visibly extends to city buildings — city exteriors and interiors reuse
a limited set of "Nordic city" wall, roof, and furniture pieces re-dressed with
different clutter, signage, and NPC placement per city, rather than being
built as bespoke unique structures.

## 4. Contrast: Oblivion and Morrowind approached the same problem differently

- **Oblivion (2006)**: The Imperial City reads as a genuinely sprawling capital
  with distinct districts (Market District, Arcane University, Temple District,
  Elven Gardens, etc.), but in-game only has roughly **~100 NPCs** total — a
  number the game itself lampshades as representing "thousands" in lore. Its
  Radiant AI was the more ambitious, more autonomous version described above,
  later dialed back for stability.
- **Morrowind (2002)**: Went further in the opposite direction from Skyrim —
  **Vivec City alone had roughly 417 NPCs** in vanilla Morrowind, described by
  players as "at least as large and populous as the three biggest cities in
  Skyrim combined." Morrowind's city designs (Vivec's giant ziggurat-cantons,
  Sadrith Mora's giant living-mushroom architecture) were built for sheer
  visual "wow factor" and distinctiveness rather than the more restrained,
  quasi-realistic medieval-city layout Skyrim uses. The community
  Morrowind-in-Skyrim's-engine remake mod "Skywind" has needed **3,000+ unique
  voiced characters across ~300 voice actors** to match Morrowind's original
  NPC density — roughly 3x Skyrim's total named-NPC count.
- **Why Skyrim shrank the numbers**: widely attributed to seventh-generation
  console hardware constraints (Xbox 360/PS3-era memory and streaming budgets)
  forcing smaller, more curated NPC counts per city than Morrowind or even
  Oblivion attempted, compensated for by *higher per-NPC fidelity* (voiced
  dialogue, individual schedules, unique faces) rather than raw numbers — a
  deliberate quality-over-quantity trade that is itself a reusable design
  lesson.

## 5. Academic critique: spectacle over function, and the Whiterun problem

The developer-authored material in sections 1-4 above (UESP data, Joel
Burgess's GDC talk) explains *how* Bethesda built the population-gap
illusion. It does not, on its own, establish whether that illusion actually
holds up under scrutiny — for that, an academic game-studies source is more
useful than developer commentary, since developers have an obvious incentive
to describe their own technique as successful.

**Vella, D. and Bonello Rutter Giappone, K., "The City in Singleplayer
Fantasy Role Playing Games" (DiGRA 2018 Conference Proceedings)** is a
peer-reviewed paper analyzing city design in Skyrim, The Witcher III,
Oblivion, Baldur's Gate, and Dragon Age: Origins through Christian
Norberg-Schulz's phenomenology of built space (centring, the demarcation of
inside/outside, movement, and encounter) — the same academic tradition Kevin
Lynch's urban-legibility framework (used for Witcher 3, see `witcher_3.md`)
belongs to. Its assessment of Skyrim's two flagship cities is a direct,
citable version of the "style over substance" critique:

> "A city such as Solitude in Skyrim, perched upon a monumental stone arch,
> is a striking visual figure first and a functionally thought-through city
> second. In the same game, the city of Whiterun, dominated by Dragonsreach
> hall standing on a rocky crag that rises above the surrounding plain,
> seems primarily intended to figurally recall the city of Edoras as
> visualized in Peter Jackson's filmic adaptation of *The Lord of the Rings:
> The Two Towers* (2002)."

This is a precise, sourced statement of the risk this generator needs to
guard against: Whiterun's silhouette is explicitly read by academic analysis
as borrowed *movie-set* iconography (Edoras) rather than as a design derived
from the functional needs of a city its lore calls a hold capital of
~275,000 people. The paper's broader "centring" argument reinforces why this
works as well as it does anyway — Norberg-Schulz's claim that a settlement
"has to possess *figural* quality in relation to the surrounding landscape"
to read as a centre at all means the striking silhouette *is* doing real
legibility work, just not the same work as population or building count
would. In other words: the visual-spectacle trick is not a failure, but it
is doing a different job than a "real capital" would need to do, and a
generator that leans on it should know that's the trade being made.

Other academic sources (found via Google Scholar; full text not retrieved
this session, cited here as pointers for further reading rather than sources
of direct quotes) independently treat Whiterun's outsized narrative role
against its modest built footprint as worth analyzing in its own right:

- Nijtmans, H., "The Inevitable Fate of the 'Dragonborn:' Selling Player
  Agency in The Elder Scrolls V: Skyrim" (in *Video Games and Spatiality in
  American Studies*, 2022) — frames Whiterun as "the first obstacle" in the
  game's critical path, i.e. treats its narrative gatekeeping role as
  disproportionate to its size.
- Bispo, J.I.C., "Examining the Bordered Heterocosm of The Elder Scrolls V:
  Skyrim" (*Loading*, Vol. 17 No. 28, 2025) — a "bordered heterocosm"
  (boundaries/transgression) reading of Skyrim's space that treats Whiterun
  as playing "a pivotal role" architecturally and narratively.

A useful additional data point from the same DiGRA paper, citing Ekman
(2013): across fantasy maps in general (not games specifically, but the same
neomedieval fantasy tradition Skyrim draws on), only **"2 to 12 per cent" of
fantasy maps are city maps** — i.e. even in the source material this genre
draws its visual grammar from, cities are a small, dense feature within a
much larger world-map, not the dominant element. This is a mild caution
against over-investing generator budget in making every settlement's own
internal map large; the genre convention is small-footprint, high-impact
city representations within a big world, which is exactly Bethesda's
approach.

---

## Recommendations for our generator

1. **Don't try to close the population gap with building/NPC count — close it
   with presentation.** Budget roughly the same order of magnitude Bethesda
   used: a "hold capital"-equivalent settlement in our generator should aim for
   dozens of actually-enterable/simulated buildings (~50–100) and a comparable
   NPC roster, regardless of what population number the lore/UI claims for it.
   Spend the saved budget on layered unenterable background structures, oversized
   civic architecture (walls, gates, a dominant central structure), and
   UI/dialogue text that states the "real" population — the disparity is
   invisible to players if the scale cues are consistent.

2. **Build a small kit library and scale reuse count to purpose, not the
   reverse.** Concretely: a handful of dedicated "kit artists" (or, for us, a
   handful of parameterized modular building generators) should support
   hundreds of distinct-feeling structures. Follow Bethesda's ratio literally:
   one broadly-reused kit (like their Cave kit, reused 200+ times) needs a
   *larger* sub-piece catalog (~50 pieces / 7 sub-kits) than a narrow, rarely
   reused kit (~7 pieces / 3 sub-kits for something used only twice). Our
   generator should size a building-kit's part catalog proportionally to how
   many times the planner intends to place it.

3. **Give every occupant NPC only a handful of daily states, gated by
   time-of-day, not a continuous simulation.** Concretely: sleep block, 1–2 work
   blocks, 1–2 social/eat blocks, and a generic wander/idle filler — 4-6 states
   total per NPC across 24 hours — synchronized with environment cues (lit
   windows, shop open/closed flags, locked doors at night). This is exactly the
   level of complexity Skyrim ships with (Oblivion's more ambitious, more
   autonomous version was cut for being unpredictable and expensive) — treat
   "4-6 scheduled states + environment sync" as the sweet spot, not a
   simplification to apologize for.

4. **Treat population tiers the way Skyrim vs. Morrowind treat them: pick a
   scale-per-settlement-tier budget and hold it constant regardless of claimed
   lore population**, but vary *fidelity* (interior detail, unique dialogue,
   named vs. generic NPCs) by tier/importance rather than varying raw count
   per claimed population. A station's "capital ring segment" should look like
   Whiterun (tight, curated, ~50-100 buildings) dressed up with background
   megastructure, not attempt Morrowind-scale unique NPC counts.

5. **For dungeon/interior analog content** (station maintenance tunnels, cargo
   holds, residential blocks), directly borrow the "400 cells from 7 kits, 2
   kit-builders, 400+ output" ratio as a sanity check for our own generator's
   parameter budget: a small number of well-designed modular kits, combined
   combinatorially, should be sufficient to produce hundreds of distinct-feeling
   interior spaces without per-space bespoke authoring.

6. **Avoid the Whiterun failure mode: don't let claimed importance outrun
   physical legibility.** The DiGRA 2018 academic critique above makes a
   sourced, specific point our generator should treat as a hard constraint:
   Whiterun's silhouette reads as borrowed movie iconography (Edoras) doing
   *centring* work, not as a scaled-down version of a real ~275,000-person
   capital doing believable *city* work. That gap is invisible right up until
   a player or a critic stops to think about it — at which point it becomes a
   specific, citable complaint. Concretely: if our generator's UI/lore text
   claims a station section is a "capital" or "major hub," the *physical*
   design (silhouette, gate scale, number of visible districts) needs to
   read as commensurately important on its own terms, independent of the
   claimed population number — don't rely on a population claim the built
   space can't visually justify at a glance.

---

### Sources

**Developer-authored:**
- [Skyrim's Modular Approach to Level Design – Game Developer (Joel Burgess GDC 2013 coverage)](https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design)
- [Elder Scrolls designer on Radiant AI's "enormous" investment cost – FRVR](https://frvr.com/blog/news/elder-scrolls-designer-explains-that-radiant-ai-is-an-enormous-investment-for-bethesda-but-every-improvement-actually-makes-it-less-noticeable-to-players/)

**Academic/critical:**
- [Vella, D. and Bonello Rutter Giappone, K., "The City in Singleplayer Fantasy Role Playing Games" – DiGRA 2018 (full text)](https://dl.digra.org/index.php/dl/article/view/948/948) — source of the Whiterun/Edoras "visual figure first, functional city second" critique quoted above.
- Nijtmans, H., "The Inevitable Fate of the 'Dragonborn:' Selling Player Agency in The Elder Scrolls V: Skyrim" – in *Video Games and Spatiality in American Studies*, 2022 (title/venue confirmed via Google Scholar; full text not retrieved this session)
- Bispo, J.I.C., "Examining the Bordered Heterocosm of The Elder Scrolls V: Skyrim: Spaces, Boundaries, Transgression and Sociocultural Significance" – *Loading*, Vol. 17 No. 28, Fall 2025, pp. 51–70, [DOI](https://doi.org/10.7202/1123035ar)
- [Lost Features: A Critical Essay on TES IV: Oblivion's Radiant AI – Medium](https://medium.com/@gatherer286/lost-features-a-critical-essay-on-tes-iv-oblivions-radiant-ai-a0150144ddef)

**Community/fan estimates (lower-confidence, unchanged from prior pass):**
- [Skyrim:Whiterun People – UESP](https://en.uesp.net/wiki/Skyrim:Whiterun_People)
- [Skyrim:Demographics – UESP](https://en.uesp.net/wiki/Skyrim:Demographics)
- [Every Major City In Skyrim & How Many NPCs Live There – Game Rant](https://gamerant.com/every-major-city-skyrim-many-npcs-live/)
- [Here's What the Population of Skyrim Is - By Holds – Fiction Horizon](https://fictionhorizon.com/heres-what-the-population-of-skyrim-is-by-holds/)
- [Radiant AI – Wikipedia](https://en.wikipedia.org/wiki/Radiant_AI)
- [Morrowind, thoughts on population size – TotalWar Center forum (Vivec NPC counts)](https://www.twcenter.net/threads/morrowind-thoughts-on-population-size.656441/)
- [Do cities feel small in Skyrim for you too? – UESP Forums](https://forums.uesp.net/viewtopic.php?f=38&t=39838) — community discussion making informally the same complaint the DiGRA paper substantiates academically above.
- [Skywind – Wikipedia](https://en.wikipedia.org/wiki/Skywind)

**Note on search-tooling limitation:** this pass's general web search (DuckDuckGo/Bing/Google) was blocked by anti-bot measures for automated tools; Google Scholar and direct PDF fetches worked and are the source of the new academic material above.
