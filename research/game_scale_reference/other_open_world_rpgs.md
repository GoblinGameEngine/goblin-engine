# Other Open-World RPGs: Red Dead Redemption 2 and Kingdom Come: Deliverance

Picks and rationale: **Red Dead Redemption 2** (Valentine/Saint Denis town
design and ambient-life systems) is extremely well documented and directly
relevant to the American-small-town aesthetic tier of our generator, and adds
a scripted-routine/behavior-driven ambient-NPC angle that neither Elder
Scrolls nor Witcher 3 cover in quite the same way. **Kingdom Come:
Deliverance** is included as a second pick because it is the most directly
analogous case to our own *village* tier: a historically-grounded, small,
single-settlement NPC-scheduling design built around real medieval Bohemian
villages, and it documents a concrete, reusable technique (deliberately
compressing real-world geography) that neither of the other games in this
research batch discuss.

---

## Red Dead Redemption 2

### Scale claim vs. reality

RDR2's world is explicitly built as a period-accurate simulation of the
American West/South circa 1899, and its towns are scaled to their narrative
role rather than to any real historical population figure. The scale gap is
made explicit in commentary on the game's technical ambitions: a real
turn-of-the-century city the size the game gestures at (using Manhattan
circa 1900 as the real-world comparison point) would have had roughly
**287,000 people across ~170 square miles** — a population and area that is,
in the commentary's own words, beyond "the technical possibilities for any
video game," which is exactly why Rockstar didn't attempt it. Saint Denis,
RDR2's largest settlement (explicitly the "Jewel of Lemoyne" and the state
capital of the fictional Lemoyne), is built to *read* as a real turn-of-
the-century industrial city — paved streets, tram lines, a uniformed
constabulary, factories — using the same "imply scale via infrastructure and
civic architecture, not population count" trick documented in Skyrim and
Novigrad above, rather than by simulating anything close to a real city's
population.

### Developer-authored account: Rockstar on balancing realism and authenticity

Rockstar rarely gives GDC talks or technical postmortems (a GDC Vault search
for "Red Dead Redemption" and "Rockstar" returns no sessions from the studio
itself — consistent with the "little published internal architecture" gap
already noted below), but two named Rockstar developers gave substantial
on-record interviews around RDR2's launch that speak directly to the
scale/authenticity question this research tracks:

- **Rob Nelson, co-head of Rockstar Games studio** (quoted in *The Guardian*,
  Oct 2018): "What does realism mean? I think we wanted it to feel like an
  authentic representation of a place and a time. But how slavishly we adhere
  to realism, that's a balance that we have to strike. How do you populate a
  world this size with enough to do? What are the things that make a city or
  a town feel authentic? How are people going to be hanging out in the world
  — and then what systems are you going to need to have them behave
  believably? You can't go out in the world and have it just fall apart on
  you, with little robot people walking around." This is a direct, named-
  developer statement of the exact population-gap/authenticity trade-off this
  whole research series is about — Rockstar frames it explicitly as a
  *deliberate balance*, not an unfortunate compromise: realism is subordinate
  to "feeling authentic" and to ambient systems not visibly breaking, not to
  raw simulated headcount.
- **Aaron Garbut, Rockstar North art director** (quoted in *Polygon*, Oct
  2018): "We were building a place, not a linear or static representation
  ... We are not building a passive experience." Garbut's framing — a
  *place* the player inhabits and moves through, rather than a backdrop
  or diorama — is the developer-side articulation of why RDR2's towns are
  built to be walked through and lived in at a small, tight scale (see
  Valentine below) rather than dressed up as an unconvincingly large
  simulation.

### Town-tier design: Valentine as the "honest small town" case

Valentine is widely cited (including in critical retrospectives comparing it
favorably to Saint Denis) as RDR2's *best-designed* town precisely because it
does not try to be more than a small town: a general store, gunsmith, doctor,
saloon, and a stockyard/livestock pen, all within a tight, walkable footprint.
Its "close-knit, friendly" feel comes from matching building count and
NPC density to its claimed size (a cattle town) rather than over-dressing it —
directly analogous to Velen's honesty-over-density approach in The Witcher 3.

### Ambient-life system: scripted routines over raw AI complexity

RDR2's world-simulation reputation rests less on any single novel algorithm
than on **layering many small scripted/state-driven routines** across NPCs,
animals, and the player's own camp, synchronized to time-of-day and weather,
so that the world reads as continuing to exist independent of the player:

- **The player's camp itself runs on a documented schedule system**: camp
  members have routines built around practical, recognizable tasks —
  building/maintaining the campfire, food preparation, sentry duty — which
  gives even the small, fixed cast of companion NPCs (a much smaller, fully
  authored set, unlike the ambient crowd) a rhythm across the day without
  needing complex AI, just well-chosen, legible everyday tasks tied to time
  blocks.
  - Rule of thumb worth borrowing: pick activities that are *visually
    self-explanatory at a glance* (someone stoking a fire, someone chopping
    wood, someone eating) rather than activities that require dialogue or
    UI to explain what the NPC is doing.
- **Ambient town/street NPCs** run on simpler routines than named/quest NPCs:
  general wandering, shopping, working a stall, or sitting on a porch,
  gated by time-of-day (shops open/close, street traffic changes at
  night) and weather (NPCs seek shelter in rain), without the deep
  per-character state that companion or quest NPCs get.
- **Wildlife migration patterns** and weather-driven behavior changes extend
  the same "the world runs on its own clock, not the player's presence" idea
  beyond NPCs to animals — reinforcing the illusion of a living world using
  the same lightweight time/weather-gated state-machine approach applied to
  a different actor type.
- Rockstar has published relatively little of their internal AI architecture
  compared to Bethesda or CDPR (their public GDC talks on RDR2 cover
  locomotion, horse animation, and wildlife rendering rather than the
  ambient-NPC/crowd system directly), so the *system design* here is inferred
  from observed behavior and developer commentary rather than a single
  authoritative technical source — treat the "many small time/weather-gated
  routines, tiered by NPC importance" pattern as the takeaway rather than any
  specific numeric budget.

---

## Kingdom Come: Deliverance

### Historical grounding and the "compress the geography" technique

Kingdom Come: Deliverance is built on real locations in Bohemia (centered on
the area of Stříbrná Skalice), and Warhorse Studios did extensive historical
reconstruction from satellite maps and archival research to rebuild period-
accurate villages, castles, and churches — nearly all major locations and many
NPCs are based on real historical counterparts.

The single most directly reusable technique documented here: Warhorse
explicitly **did not use the real, historically-accurate distances between
settlements**, because that geography is realistically sparse (long barren
travel distances between small villages, accurately reflecting low real
medieval population density). Instead they built what they called an
**"adjusted realistic map"** — deliberately moving villages and towns closer
together and shrinking the forests between them, specifically **to make the
game world feel more densely populated and avoid tedious barren travel**,
while keeping every individual location internally faithful to its real
historical layout. This is a clean, explicit statement of a technique our
generator can borrow directly: preserve local realism/detail per settlement,
but compress the *macro-scale spacing* between settlements relative to a
"real" 1:1 map, because raw geographic accuracy reads as emptiness, not
believability.

This "adjusted realistic map" description is directly attributable to named
Warhorse staff, not just paraphrase: PCGamesN's historical-accuracy piece
quotes **Tobias Stolz-Zwilling, Warhorse's PR manager**, describing the map
as moving "the villages and cities a bit closer to each other to make it
more densely populated and [makes] the forests a bit smaller," and quotes
**Prokop Jirsa, a Warhorse designer**, on how the studio balances historical
grounding against gameplay/pacing needs more generally ("It enriches the
lore so you are more interested in it, but often we can use it in gameplay
too"). Separately, Warhorse's own historical consultant **Joanna Nowak** has
been publicly candid that compromises were deliberate and necessary: "It's a
game, it's not an open-air museum, it's not a medieval simulator!" — a
useful, developer-sourced reminder that even a studio marketing itself on
historical authenticity treats that authenticity as a means to gameplay
ends, not an end in itself, and says so on the record.

### Village-scale NPC scheduling

KCD's villages (Skalitz in the prologue, Rattay as the main open-world hub)
are built around **dawn-to-dusk NPC routines**: named villagers are tied to
specific locations and tasks across the day — tavern-goers, field workers,
household chores — using the same time-gated schedule-package concept Elder
Scrolls popularized, but applied at a much smaller, single-village scale and
grounded in specifically medieval daily-life tasks (farm labor, blacksmithing,
prayer, market trade) rather than generic "wander" behavior. Reputation
effects are also tracked at the settlement level and carry between
settlements (e.g., Skalitz refugee status affects how Rattay's guards and
townsfolk react to the player), which is a cheap way to make a handful of
small, separately-simulated settlements feel like they're part of one
continuous, remembering world rather than disconnected instanced zones.

Specific per-village NPC headcounts are not consistently published by
Warhorse in a single citable source, but qualitatively, KCD's villages are
built at a scale consistent with a genuinely small medieval village (a few
dozen named residents at most per settlement, not hundreds) — reinforcing
that a small, honest population count combined with legible, historically-
grounded daily tasks is sufficient for a village tier to feel real, without
needing Skyrim-or-larger city-scale population-gap tricks at all.

---

## Critical and academic reception

Games-journalism critique that specifically analyzes RDR2's or KCD's
*settlement design and density* (as opposed to general reviews of story or
gameplay) is thinner in easily-citable form than the developer material
above — this session's web search tooling was rate-limited/blocked for
general search engines (DuckDuckGo, Bing, and Google's own web search all
refused automated queries), which constrained discovery to Google Scholar
and direct-fetch of known outlets. Within that constraint, the following
peer-reviewed academic sources were located and are the strongest
non-developer, non-fan layer available for these two games:

- **Donald, I. and Reid, A., "The Wild West: Accuracy, Authenticity and
  Gameplay in Red Dead Redemption 2"** (Abertay University, 2020) —
  an academic paper specifically examining how RDR2 balances historical
  accuracy against gameplay/authenticity claims. Full text was not
  retrievable in this session (Cloudflare-protected host), so only the
  title/venue is confirmed via Google Scholar, not direct quotes — flag
  this one for a follow-up pass with working search access.
- **Ali, M. and Gurdalli, H., "Representation of Culture Through
  Architectural Space in Video Games: The City of Saint Denis, Red Dead
  Redemption II"** (*Design Dialogue Journal*, Vol. 2 No. 1, 2025) — a
  semiotic architecture analysis of Saint Denis specifically, at both
  urban (macro) and individual-building (micro) scale. The abstract's
  conclusion is that "RDR 2 does an excellent job in detailing the city of
  Saint Denis," i.e. this academic source is *not* a critique of Saint
  Denis's scale/density but a confirmation, from an architecture-analysis
  angle independent of Rockstar's own marketing, that the city reads as an
  authentic representation of a turn-of-the-century industrializing
  American city — corroborating this file's existing claim that Saint
  Denis works through infrastructure/civic-architecture signaling rather
  than population count.
- **Westerside, A. and Holopainen, J., "Sites of Play: Locating Gameplace
  in Red Dead Redemption 2"** (DiGRA 2019) — a performance-studies analysis
  of "placeness" in RDR2 built from 30+ hours of observed play; theoretical
  rather than descriptive of specific town design, so it is cited here as a
  pointer for further reading rather than a source of concrete claims.
- **Heinemann, J., "Kingdom Come: Deliverance a problematika nároku na
  autentičnost v počítačových hrách"** ["Kingdom Come: Deliverance and the
  problematic claim of authenticity in digital games"] (*Bohemia*, 2021,
  in Czech) — an explicitly critical academic piece arguing that KCD's
  marketing promise of "authentic," "truthful" and "realistic" depiction of
  the past is itself the problem: it lends unearned authority to a
  necessarily selective, compromise-laden representation, especially where
  the game's narrative choices carry hidden political agenda. This is the
  clearest academic pushback found on the "authenticity" framing this file
  otherwise takes at face value from developer sources — a useful
  counterweight: our generator's marketing/UI should avoid over-claiming
  "authentic" or "real" as absolute properties, for the same reason.
- **Bostal, M., "Medieval Video Games as Reenactment of the Past: A Look at
  Kingdom Come: Deliverance and Its Historical Claim"** (2019) — situates
  KCD within reenactment theory; confirms from an independent academic
  angle that KCD's "historical accuracy" is a curated reenactment, not a
  1:1 simulation, consistent with the "adjusted realistic map" compression
  technique documented above.

No comparable critical-academic source specifically calling out an RDR2 or
KCD settlement as "too small for its claimed importance" (the Whiterun-style
failure mode) was found — Valentine and KCD's villages are consistently
treated, in both developer and academic sources located, as *appropriately*
scaled to their claimed small-town/village status rather than as
scale-mismatched. See `elder_scrolls_series.md` and `witcher_3.md` for the
academic critique of that specific failure mode (Whiterun/Solitude, sourced
to a DiGRA 2018 paper), which is the standing cautionary example for this
generator rather than anything found in the RDR2/KCD material.

---

## Recommendations for our generator

1. **Compress macro-scale spacing between settlements, not their internal
   detail.** Directly borrow KCD's "adjusted realistic map" technique: when
   laying out the station ring's habitat sections, keep each settlement's
   *internal* layout and detail density realistic/faithful to its declared
   type, but deliberately shrink the "dead space" (empty corridor/transit
   sections) between settlements relative to what raw structural geography
   would imply — realistic emptiness reads as a bug, not scale.

2. **Tier NPC routine complexity by narrative importance, not settlement
   size.** Use RDR2's pattern: a small set of "named/foreground" NPCs (quest
   givers, shopkeepers, station officials) get full multi-block daily
   schedules with legible, self-explanatory tasks; the much larger ambient
   population gets a cheap, shared 2-3 state routine (wander/work-stub/
   shelter-at-night) gated only by time-of-day and a station-equivalent of
   weather (e.g., shift changes, life-support alerts, gravity fluctuations).
   This scales independent of whether the settlement is a village-tier or
   city-tier location.

3. **For our smallest tiers (village/outpost), don't reach for
   population-gap tricks at all** — Kingdom Come and Valentine both show
   that a small settlement with a genuinely small, honestly-scaled NPC roster
   and historically/functionally grounded daily tasks (not generic idles)
   reads as believable on its own terms. Reserve the heavier illusion
   machinery (background crowds, layered facades, unenterable megastructure)
   for settlement tiers that are explicitly claiming city/metropolis scale.

4. **Make ambient routines visually self-explanatory without UI**, per RDR2's
   camp-schedule design: prefer tasks a player can identify at a glance
   (maintenance work at a console, queueing at a mess hall, sleeping in a
   bunk) over abstract "idle" states, since legibility of *what* an NPC is
   doing is what sells a routine as purposeful rather than random.

5. **Treat "authentic"/"realistic" as a gameplay tool, not a claim to defend
   literally.** Both Rob Nelson's on-record framing ("how slavishly we
   adhere to realism, that's a balance we have to strike") and the academic
   pushback on KCD's authenticity marketing (Heinemann 2021) point the same
   direction: state believability goals in terms of what the player
   experiences (a town that "feels" authentic, doesn't visibly break) rather
   than in absolute terms ("this is a real X-person settlement") in any
   in-fiction or UI text our generator produces — absolute claims are what
   invite the Whiterun-style scale-mismatch critique documented in
   `elder_scrolls_series.md`, while experiential claims are much harder to
   falsify by simply counting buildings.

---

### Sources

**Developer-authored (Rockstar / Warhorse, on-record):**
- [Get real: behind the scenes of Red Dead Redemption 2, the most realistic video game ever made – The Guardian](https://www.theguardian.com/games/2018/oct/24/get-real-behind-the-scenes-of-red-dead-redemption-2-the-most-realistic-video-game-ever-made) (Rob Nelson, Rockstar co-studio head, on balancing realism/population/authenticity)
- [How Red Dead Redemption 2's world was inspired by 19th century landscape painters – Polygon](https://www.polygon.com/red-dead-redemption/2018/10/26/18024982/red-dead-redemption-2-art-inspiration-landscape-paintings) (Aaron Garbut, Rockstar North art director, "building a place, not a linear or static representation")
- [The obsessive historical accuracy of Kingdom Come: Deliverance, and how it makes for a better RPG – PCGamesN](https://www.pcgamesn.com/kingdom-come-deliverance/kingdom-come-deliverance-historical-accuracy) (named quotes from Tobias Stolz-Zwilling, PR manager, and Prokop Jirsa, designer, on the "adjusted realistic map" and historical/gameplay balance; also quotes historical consultant Joanna Nowak)

**Academic/critical:**
- [Ali, M. and Gurdalli, H., "Representation of Culture Through Architectural Space In Video Games: The City Of Saint Denis, Red Dead Redemption II" – Design Dialogue Journal, 2025](https://designdialoguejournal.com/index.php/home/article/view/13)
- [Westerside, A. and Holopainen, J., "Sites of play: Locating gameplace in Red Dead Redemption 2" – DiGRA 2019](https://dl.digra.org/index.php/dl/article/view/1111)
- Donald, I. and Reid, A., "The Wild West: Accuracy, authenticity and gameplay in Red Dead Redemption 2" – Abertay University, 2020 (title/venue confirmed via Google Scholar; full text was behind a Cloudflare challenge this session, not independently verified beyond the abstract-level description above)
- Heinemann, J., "Kingdom Come: Deliverance a problematika nároku na autentičnost v počítačových hrách" – Bohemia, 2021 (in Czech; critical academic piece on KCD's authenticity marketing)
- Bostal, M., "Medieval video games as reenactment of the past: a look at Kingdom Come: Deliverance and its historical claim" – 2019 (via Academia.edu; title/venue confirmed, full text not independently pulled this session)

**Community/fan estimates (unchanged from prior pass, treat as lower-confidence):**
- [Red Dead Redemption 3 Needs To Learn From RDR2's Biggest Town Mistakes – ScreenRant](https://screenrant.com/red-dead-redemption-3-towns-valentine-industrial-op-ed/)
- [Saint Denis – Red Dead Wiki (Fandom)](https://reddead.fandom.com/wiki/Saint_Denis)
- [The Reality of Red Dead Redemption 2's AI (Part 1) – The Sound of AI, Medium](https://medium.com/the-sound-of-ai/the-reality-of-red-dead-redemption-2s-ai-part-1-c276e9da2763)
- [The Reality of Red Dead Redemption 2's AI (Part 2) – The Sound of AI, Medium](https://medium.com/the-sound-of-ai/the-reality-of-red-dead-redemption-2s-ai-part-2-c0887123cffd)
- [Kingdom Come: Deliverance – Wikipedia](https://en.wikipedia.org/wiki/Kingdom_Come:_Deliverance)
- [Ordinary Routine – Kingdom Come: Deliverance Wiki (Fandom)](https://kingdom-come-deliverance.fandom.com/wiki/Ordinary_Routine)
- [NPCs – Kingdom Come Deliverance Wiki (Fextralife)](https://kingdomcomedeliverance.wiki.fextralife.com/NPCs)

**Note on search-tooling limitation:** this pass's WebSearch quota was
already exhausted at session start (inherited from a prior interrupted
attempt), and DuckDuckGo/Bing/Google web search all actively blocked
automated WebFetch access (CAPTCHA/anomaly detection). Google Scholar and
direct-URL fetches (including via `curl` for a few sites WebFetch itself
couldn't reach) worked and are the source of everything new in this pass.
A dedicated Rockstar GDC talk on town/world design does not appear to exist
in GDC Vault's catalog as of this check — their public talks are on
locomotion/wildlife/audio, not settlement design, consistent with this
file's original note.
