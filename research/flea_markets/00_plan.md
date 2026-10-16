# Flea markets and the island moorings: plan and contract (2026-10-15)

Status: DESIGN ONLY. Nothing in the game is built yet. This is the contract for the KIT, GENERATOR, RUNTIME and DATA
streams. **Revised 2026-10-15** with the user's decisions:
- the game opens on a Wednesday;
- the islanders come down often and settle in large numbers (the canon is updated);
- the name "Lowliners" is approved, and discrimination follows the region;
- every town gets its own market;
- every market has a name, with regional sign styles.

The canon change is **done** in `tools/bible/canon_sky.py` (regenerated: `remake/bible/sky_islands.json`,
`research/bible/13_sky_islands.md`). New companion file: 08_signage_briefs.md (the Grok sign sheets).
Companion files:
- 01_research.md: tents, lights, flea-market layouts, ropeways, Roma/Traveller history.
- 02_open_questions.md: the defaults I chose.
- 03_american_flea_markets.md: profiles of the real markets.
- 04_economics.md: flea market economics.
- 05_bazaar_history.md: the history of the bazaar.
- 06_secondary_economy.md: the synthesis into the game's secondary economy.
- 07_names_and_signage.md: the market names, sign styles, sign kit and Grok prompts.

## The user's brief, 2026-10-15 (verbatim)
> Every city needs a large flea market where  locals come to buy and sell on the weekends. These need to be on the
> outskirts of the city but within the city limits. The flea markets need large paved parking lots. The markets will
> maintain at least 80% occupancy with 35% of the shops being permanent and the rest rotating every few months.
> Individuals from all walks of life will set up in the markets. When a floating island is near one, it will drop lines
> and a gondola with a crew of 24 people per island. They will anchor the island and begin setting up logistics tents.
> After that, more cables will drop and several gondolas bringing people and merchandist down and up will begin
> operating. When this happens, the islanders will set up in every vacant shop in the flea market. Other nearby floating
> islands will be drawn to the anchored island and will link up, dropping their own lines and gondolas. When three
> islands have anchored at a flea market, the islanders will begin setting up trading tents around the parking lot on
> any open adjacent area. The trading tents will have shelves and tables, with at least two islanders working in them.
> Look up bazaar tents and event tents. The islanders tents must be colorful, whimsical, and well lit. The isdlanders
> love lights. The flea markets operate from 9am-6pm Friday Saturday and Sunday. After hours the tents close, and the
> gondolas only carry people to and from the islands. The parking lot stays well lit throughouty the night. Most
> islands will leave after one weekend, but can stay for up to three weeks. When a flea market has an island anchored to
> it, it stays open all week, however the booths run by the locals remain closed except for the weekends. The islands
> will need buildings and platforms for operating anchroing lines and gondolas. Manning and maintaining these systems
> will be it's own highly valued profession. The islands are hyper capitalist in a good way. People are hard working
> and happy. People from the surface enjoy going up to the islands to explore and have fun and the islands cater to
> this micro-tourism. Very few people from the surface manage to settle in the islands but is is not unheard of. More
> people from the islands decide to settle on the surface. They form a disadvantaged minority akin to Roma people who
> do not travel anymore.

> (widened, same day) The flea markets will each need their own name and stylized signage. I suggest you research
> prominent flea markets in America. Trader's World, The Red Barn, The Wagon Wheel, Flea World, Gibraltar Trade Center
> among others. Do exhaustive research on flea market economics and bazaar history. We will be melding the two and this
> will form the backbone of our secondary economy.

---

## 0. What exists today (the survey, with citations)

### Cities, towns and city limits
- **Every settlement is generated at 1:1.** `tools/settlegen/towns.py:14-111` (`SPECS`) lists 21 settlements, with
  their pop, tier, region, seed and prefix. Calder keeps its own plan (`tools/settlegen/calder.py`).
  `tools/map_expanded.py:2041-2047` builds Calder and then every spec, largest first (`build_generated`, `:1889`).
  The catalog holds SOL 11,428 records, HF 11,150, PCR 9,590 and K 9,191, so all four cities exist as buildings.
- **The cities** (`tier="city"`):
  - Solana Point (pop 44,200, region "ca", seed 101, `towns.py:16`);
  - Harrow Falls (41,800, "gl", `:27`);
  - Port Carrow (38,600, "ne", `:37`);
  - Kessler (34,500, "gl", `:48`).
  `godot_project/remake/law/settlements.json` agrees on the same four cities (law pops 40k/35k/24k/22k). It also has
  five towns: Oceanview, Brightwater, Playa Verde, Marlowe and Bellhaven.
- **There is no explicit city-limits polygon anywhere.** The nearest things:
  - The plan's reach. `plan_city` sets `U = (600 + 13*sqrt(pop)) * (1.35 if waterfront)` along Main and
    `V = 450 + 13*sqrt(pop)` across it, with `cfg["bounds"] = (-U, U, -V, V)` (`tools/settlegen/city.py:114-118`).
    The Planner refuses anything outside these bounds (`pl.inside`).
  - The built-up footprint. map_expanded grows each town's streets, buildings and areas by about 25 m into `FOOT` /
    `TMASK` (`tools/map_expanded.py:2120-2140`), and uses it only to clip farmland and section roads.
  - `law/settlements.json` has a `centre` per settlement and no radius.
  - **Decision:** city limits = the plan bounds (an ellipse inscribed in them, below). The generator writes them out as
    a polygon (§1.1).
- **Edge siting already exists.** The industrial-park pass searches a 40 m grid of free, dry, flat rectangles, farthest
  from the heart first (`city.py:573-700`):
  - It skips sites with normalised radius `hypot(u/U, v/V) < 0.45` (`:622`).
  - Each candidate is checked with `pl.inside`, `pl.occ.free`, `pl.dry`, `blocked()` samples and a slope of at most
    0.06 (`:634-639`).
  - A frontage street runs 8 m out, with a connector to the nearest street within 260 m. Both are occupancy-checked,
    because unchecked connectors once cut through 6,000 buildings (`:640-656`).
  - The pass runs on **its own RNG stream after everything else**, so the rest of the plan doesn't move (`:577`).
  - The flea-market siting copies this pattern exactly.
- **Other generators.** Shopping centres (`city.py:705-722`, `centers.strip_center`) write parking areas at
  `STALL = 32 m2` gross per stall (`tools/settlegen/centers.py:25`). Postwar edge tracts are `_edge_tracts`
  (`city.py:532`).

### Parking
- `tools/parking_lots.py:1-32` writes terrain.json `areas` of kind `"parking"` carrying a `"lot"` record: `{type, town,
  city, spaces, accessible, rows: [[u0,u1,v_front,depth,facing]], access, dir, stop}`.
  - Stalls are 2.75 x 5.5 m with 7.3 m two-way aisles, and one accessible stall per 25.
  - `tools/road_furniture.py:794-813` paints the stall lines and puts up the P signs.
- Parking at runtime:
  - `MapTerrain.area_kind` (`godot_project/scripts/world/MapTerrain.gd:894-902`) answers the area under a point.
  - `MapTerrainMesh.gd:133` colours parking dark grey.
  - **Gotcha:** `road_surface.gd:83` gives parking areas the **"dirt"** surface. A paved market lot needs "asphalt".
- NpcTraffic parks cars only at the kerb (`npc_traffic.gd:16-31, :539-579`), never in a lot. A market's visitors
  will need lot-stall assignment (§6.4).

### Street lighting
- `tools/street_lamps.py:1-40` writes `street_lamps.json`:
  - `lamps [s,x,yaw,kind]`: 0 street, 1 town-centre, 2 alley, 3 beach;
  - `strings [s0,x0,h0,s1,x1,h1,scheme]`: festoons, scheme 1 the beach multicolour (`:301,:335`), scheme 2 the
    town-centre warm (`:272`);
  - palms wrapped in lights.
- `godot_project/scripts/world/StreetLights.gd`:
  - two tiers: near cells of 400 m, kept within 750 m; far bulbs out to 4.4 km (`:25-33`);
  - `HEAD` per lamp kind (`:39-45`);
  - **28 pooled OmniLights** moved every 0.5 s to the lamps nearest the player (`:22, :34, :79-90`);
  - festoons drawn by `_festoon` (`:299`).
- **There is no parking-lot pole kind yet**; one is added (§3.6).
- On the islands, `sky_signs.gd:1-25` merges neon, LED boards, wall wash, solid signs and **bulbs** (one MultiMesh,
  `sky_bulbs.gdshader`) into a few draw calls. The islanders' tents reuse these shaders.

### Calendar, places, schedules, jobs, money
- `DaySkySystem.DAY_LENGTH_SECONDS = 2880` (`scripts/world/DaySkySystem.gd:14`), so one game hour is two real minutes.
  `var day: int = 0` ("day 0 is a Monday", `:66-67`), and `day` increments in `_process` (`:211-215`).
- **There are days of the week**:
  - `NpcPlaces.DAYS` (`remake/characters/npc_places.gd:18`) and `open_on(t, day)` with `posmod(day, 7)` (`:313-325`)
    already parse ranges such as `"fri-sun"`, plus "daily", "never" and "seasonal".
  - `NpcLife.stays(pid, day)` (`npc_life.gd:393-500`) builds work, school, worship (Sunday, `:461`) and errands.
    Errands to retail, leisure, food and drink get ×1.4 at weekends (`:487`).
  - **Calendar (decided: the game opens on Wednesday 2752-05-24):** the bible's date wins
    (`research/bible/01_world.md:79`).
    - `tools/make_events.py:52` already writes `"start_date": "2752-05-24", "start_weekday": 2` into
      `remake/events.json`, and TransitDemand reads it (`remake/scripts/transit/transit_demand.gd:37-39`).
    - NpcLife and NpcPlaces still assume day 0 is a Monday (`posmod(day, 7)`), and so does the comment at
      `DaySkySystem.gd:66`. The plan makes everything read the one source (§4.1).
- **Place types** are `tools/places/make_places.py` `pt(id, name, cat, shells, jobs, hours[open,close,days], visits,
  ...)` (`:49-57`).
  - The shells already include `kiosk` and `pavilion` (`:18-40`).
  - Seasonal stands exist (`:169-173`); there is no market type.
- **Occupancy contract:** `research/lives/07_occupancy.md:62-99` and `NpcOccupancy` (`npc_occupancy.gd`):
  - posts come from shift templates driven by the hours;
  - weekly rota;
  - **one settlement = one labour market**, solved from the seed;
  - seeded vacancies with a `vacant_reason`;
  - the pure queries `on_duty / roster / who / where` (`:423-530`).
- **Money:**
  - Wages are in dollars (`npc_traits.json:112-113`; `research/lives/02_money.md:9-15`).
  - `money_style`: "tight people haggle" (`02_money.md:38`).
  - The bible's currency is the **Columbia dollar (C$)** from the Commons Bank. The **Draw** guarantees food, a home,
    air, water and clothing, and "money buys everything else" (`research/bible/01_world.md:110-111`). Draw Day is the
    first of the month (`06_culture.md:125`).
  - **There is no player wallet, shop or trade code in the game yet** (grep for wallet/money/credits finds none).

### Sky islands
- The contract is `research/sky_islands/00_plan.md`:
  - deck at 750 m, 0.925 g (`:36-38`);
  - 1 block = 100 x 80 m (`:40`);
  - the dock rules (`:47-49`);
  - drift 4–9 m/s west (`:50`);
  - the local frame +X south, +Y up, +Z west (`:56-65`);
  - the layout format with hoists, launchers and pads (`:93-107`).
- **SkyDrift** (`remake/scripts/sky/sky_drift.gd`) is a pure sim:
  - Rafts are `{s, x, vx, members, edges, tow, h, meet_h}` (`:37-38, :79-89`).
  - `DOCK_RANGE 3000`, `DOCK_GAP 26`, `LASH_DAYS 3`, `MAX_RAFT 10`, `X_LIM 9000`, `DRIFT 4..9` (`:21-35`).
  - `step()` advances s by the raft's velocity (`:150-174`); `_meetings` fires lines (`:232-256`); `_lash` (`:392`);
    `_cast_offs` after LASH_DAYS (`:406-414`).
  - It is seeded (`setup`, `:49`) and has `warm_up` (`:507`). **It has no notion of holding position.**
- **SkyIslands** (`sky_islands.gd`):
  - places the islands at 10 Hz with interpolation (`:167-258`);
  - `deck_velocity`, `frame_at`, carry (`:259-327`);
  - **fast_travel** onto an island (`:334-420`);
  - lines and rockets (`:546`);
  - the plumbs' lark descents (`:723-780`).
- **SkyIsland hoists** (`sky_island.gd:1128-1222`):
  - The line states are idle → lower → ground → raise.
  - The line is an ImmediateMesh strip bowed by Coriolis (`_line_point`, `:1180`): `LOWER_SPEED 12`, `RAISE_SPEED 5`
    (`:28-29`).
  - A line never comes down over water (`_wet`). Containers are dropped through `sys.drop_cargo`.
  - **This is the nearest thing to a gondola, and the ropeway builds on it.**
- **Warrens:**
  - Lattice cells are 3 x 3 m with a 3.2 m storey, in 8x8 chunks (`tools/sky/warren/FORMAT.md:6-13`).
  - `lattice.py:116-120` reserves discs for pads (7.5 m) and for hoists and launchers (4.5 m), plus gate strips at the
    bridges. Mooring houses get reserved the same way.
  - Hoists are placed at the rim on the diagonals: 1–3 per island by blocks (`tools/sky/make_islands.py:721-733`).
  - The kit (`pieces.json`, 402 pieces) already has `ov_stall` (160 tris), `ov_festoon` (134), `ov_lantern`,
    `ov_suq_canopy`, `ov_toldo`, `ov_awning_cane`, `ov_chochin_string`, `hoist_beam` and **`cable_car`** (86 tris,
    a decor gondola line, `remake/blender/sky/warren_kit/pieces_b4.py:660,735`).
- **Canon** (`tools/bible/canon_sky.py` → `remake/bible/sky_islands.json`):
  - 100 islands, 97,070 people, 387 blocks; island pops range from 180 to ~2,000.
  - `JOBS` (`canon_sky.py:109-152`) includes winch_hand, hoist_master, rigger, line_rocketeer, factor, plumb,
    shopkeeper and weigher.
  - `SPECIALTIES` (`:154-176`) are what each island sells.
  - `hoist_trade`: the skybox is 2.4 x 2.4 x 3 m at 2 t, and hoists are booked by the plumb a week ahead.
  - The lexicon: groundfolk / "heavies"; "cold hands" = an honest trader; "lift" = buoyancy, wealth, room.
  - Society (`research/sky_islands/03_society.md:30-46`): the Aloft "rarely come down": weight is life, there is
    ground-sickness, "most Aloft meet groundfolk only through their plumb".
  - **Changed 2026-10-15 (done):** coming down is routine, and half of all island children settle on the floor
    (§8.1, §9).

---

## 1. Siting: a flea market in every town

The user, 2026-10-15: every town gets its own market.
- The smaller towns' markets are smaller, but each one is unique, a local draw and the town's pride.
- People travel round the map to visit other towns' markets (§6.3).
- Every market has static mooring attachments for the islands and extra room outside it for the islanders'
  trading tents.
- There are **22 markets**: the 21 `towns.py` settlements plus Calder.

### 1.1 City limits and the outskirts
- **The limits.** `limits(town)` is the ellipse `(u/U)^2 + (v/V)^2 <= 1` in the town frame of `plan_city`, clipped to
  dry land. The generator writes it as a polygon of 48 points `(s, x)` into a new `limits` field of
  `law/settlements.json`.
  - The PDA map, the law and the fast-travel tiers can all use it later.
- **Outskirts** means normalised radius `r = hypot(u/U, v/V)` in **[0.60, 0.95]**: the whole site, mooring field and
  apron must lie inside the limits.
- The site must also be:
  - outside the downtown and inner zones;
  - at least 250 m from any school or hospital site (crowds, traffic);
  - on flat ground (lot slope at most 0.04: a paved lot drains at 1–2 %, and 4 % is the most for stalls);
  - dry (`pl.dry`) and not `blocked()`;
  - free in the occupancy raster;
  - with its main entrance on Main or a collector, or within 260 m of one by a connector.
- **Mooring clearance.** The island hangs 600–750 m overhead.
  - The sky above the mooring field must be clear of the end caps (|x| ≤ 9,000, true for every city).
  - The field must be clear of the town's tallest landmarks within 150 m.
  - A water check is not needed: the field is dry by construction.
- **Search.** The generator copies `_jobs_pass` (`city.py:610-668`): a 40 m candidate grid, sorted by a score.
  - The score is `|r - 0.78|` (the middle of the outskirts) plus a small preference for the leeward
    (antispinward, −s) side, because islands arrive drifting west.
  - Each candidate rectangle is tried at 2 rotations.
  - The pass runs on its own RNG stream (`seed * 7919 + 303`) after `_jobs_pass`, so existing lots don't move. Only
    free land is taken.
  - If no candidate fits at full size, the stall count steps down 15 % and the search runs again, at most 3 times.
    After that the city reports `no_site` (a build failure in the test).

### 1.2 Size and mooring tier (all 22 markets)

**Stalls:**
- Cities (pop > 30k): `round(pop / 120, -1)`.
- Everywhere else: `ceil((40 + pop / 140) / 10) * 10`.
- Rural markets are regional draws, so even a hamlet keeps ≥ 40 stalls. Rogers, Ohio, a village of a few hundred,
  runs ~1,600 spaces (03 §15).

**Paved parking:** 1.8 spaces a stall, plus a grass apron for overflow.

**Style t:** the north (0) to south (1) gradient of 07 §1, from the town's x: `t = (x + 5600) / 11200`.

| market (07) | town | region | pop | stalls | perm. | paved spaces | mooring tier (§5.3) | tent slots ≥ | style t |
|---|---|---|---|---|---|---|---|---|---|
| The Ropewalk | Port Carrow | north_shore | 38,600 | 320 | 112 | 576 | city | 60 | 0.00 |
| The Lobster Pot | Brightwater | north_shore | 6,200 | 90 | 31 | 162 | town | 36 | 0.01 |
| The Tide Clock | Haven Point | north_shore | 3,900 | 70 | 25 | 126 | village | 24 | 0.01 |
| The Net Loft | Tern Harbor | north_shore | 1,300 | 50 | 18 | 90 | village | 24 | 0.01 |
| The Water Tower | Loomis Grove | northland | 390 | 50 | 18 | 90 | village | 24 | 0.24 |
| The Book Barn | Fenwick | northland | 6,400 | 90 | 31 | 162 | town | 36 | 0.31 |
| The Weathervane | Dunmore Crossing | northland | 480 | 50 | 18 | 90 | village | 24 | 0.31 |
| Brannock County Trade Days | Marlowe | northland | 9,100 | 110 | 39 | 198 | town | 36 | 0.32 |
| The Boathouse Swap | Port Tamsin | kettle_valley | 3,400 | 70 | 25 | 126 | village | 24 | 0.33 |
| Four Corners Swap | Haskins Corner | northland | 2,600 | 60 | 21 | 108 | village | 24 | 0.34 |
| The Regatta Swap | Victory Bay | kettle_valley | 900 | 50 | 18 | 90 | village | 24 | 0.43 |
| Millwheel Market | Cedar Ford | kettle_valley | 1,150 | 50 | 18 | 90 | village | 24 | 0.44 |
| Traders' Landing | Harrow Falls | kettle_valley | 41,800 | 350 | 122 | 630 | city | 60 | 0.58 |
| Iron Wheel Trade Days | Kessler | southland | 34,500 | 290 | 102 | 522 | city | 60 | 0.68 |
| The Red Granary | Bellhaven | southland | 7,200 | 100 | 35 | 180 | town | 36 | 0.68 |
| The Tall Tamarack | Tamarack | southland | 8,300 | 100 | 35 | 180 | town | 36 | 0.69 |
| Elevator Flea Days | Pruett | southland | 820 | 50 | 18 | 90 | village | 24 | 0.71 |
| Route 30 Swap Meet | Calder | southland | 7,000 | 90 | 31 | 162 | town | 36 | 0.72 |
| La Pulga Verde | Playa Verde | south_shore | 5,400 | 80 | 28 | 144 | town | 36 | 0.98 |
| The Starlite Swap | Solana Point | south_shore | 44,200 | 370 | 130 | 666 | city | 60 | 0.99 |
| The Carousel Swap | Oceanview | south_shore | 9,800 | 110 | 39 | 198 | town | 36 | 0.99 |
| The Pelican Swap | Pelican Cove | south_shore | 1,600 | 60 | 21 | 108 | village | 24 | 0.99 |

**Totals:** 2,660 stalls on the floor. Pops are the design pops (`towns.py`). Tiers: city > 30k, town ≥ 5k, village
below.

- **Why these numbers** (01 §3, 03 §23, 04):
  - Big American markets run 300–2,500 spaces on 10–60 acres. Sprawling outdoor sites hold 12–25 vendors an acre;
    these are compact paved markets of 55–60 an acre.
  - Parking takes 25–50 % of real sites. Here paved parking is ~33 %, and ~50 % with the grass overflow.
  - Saturday demand: ~10 visitors a stall a day, so ~3 a stall on site at the peak; 75 % come by car at 2.3 a car;
    plus vendors and staff. That gives **1.8 per stall paved**. Fairs and the weekend trips (§6.3) use the grass apron
    for ~1.0 more per stall.
- **Each market is unique (the town's pride):**
  - its own name, sign and mascot (07);
  - its own specialty that draws visitors from other towns (07 §2: Fenwick's books, Dunmore's livestock auction,
    Cedar Ford's mill crafts, and so on);
  - its own shed colour and layout variant;
  - its own Great Fair date (06 §8).
- **Parts of a site** (city sizes; towns and villages scale by stalls):
  - **Market floor** ≈ 23 m² gross per stall: 9 m² stall, 9 m² aisle share, plus fire lanes, food court and
    restrooms. 350 stalls ≈ 0.8 ha.
  - **Paved parking** at `STALL = 32 m²` gross (`centers.py:25`): 630 spaces ≈ 2.0 ha.
  - **Apron**: an unpaved lawn band 30–40 m wide round 2–3 sides of the lot (grass overflow parking on fair days and
    the trading-tent ring), ≈ 1.2 ha.
  - **Mooring ground** (the static attachments, by tier; built whether or not an island ever comes):
    - **city:** a Mooring Field, a 120 x 100 m lawn with 24 buried anchor blocks and 2 mooring masts, for a raft of
      up to 10;
    - **town:** 1 mast and a ring of 12 anchor blocks in a 90 x 70 m lawn, for 4 ground-anchored islands;
    - **village:** a ring of 8 anchor blocks in a 70 x 60 m lawn, for 3 ground-anchored islands.
    - **Every tier takes a raft of up to 10:** later islands lash to the anchored ones (§5.3), so Bright Weeks and
      Sky Holidays can happen anywhere.
    - It sits beside the market on its leeward (west) side and holds the island's ground stations.
  - **Tent room:** the apron plus the mooring margins hold at least 60 / 36 / 24 tent slots (city / town /
    village) outside the market itself.
  - Entry drives, the vendor lane, landscaping strips, and a bus/tram pull-in.

### 1.3 Layout (the site's own frame: u along the frontage, v away from the road)
```
road ─────────────────────────────────────────────────────────────────────────
  pylon sign ▲  entrance(s)  exit                    bus / tram pull-in
  ┌─ landscape strip 3 m ──────────────────────────────────────────────────┐
  │  PAVED PARKING  (double-loaded bays 2.75 x 5.5, aisles 7.3 m, 90 deg)   │  apron (lawn)
  │  light poles (kind 5) in the islands between bays                       │  = overflow parking
  ├─ fire lane 6 m + drop-off ─────────────────────────────────────────────┤  = tent ring zone
  │  ARCH / gate house, ticket booth, info, restrooms, food court           │
  │  COVERED SHEDS (permanent stalls): 2-4 long open-sided sheds,           │
  │     3 x 3 m bays both sides of a 4 m covered aisle                      │
  │  OPEN-AIR ROWS (rotating stalls): back-to-back 3 x 3 m pitches,         │
  │     6 m aisles (fire access every 4th aisle 6 m clear, no awnings)      │
  │  vendor lane (6 m) behind the outer row; vendor parking                 │
  └────────────────────────────────────────────────────────────────────────┘
          MOORING FIELD (leeward, west): deadmen, ground station(s), logistics tents
```
- **Stall pitch:** 3.0 x 3.0 m (the 10 x 10 ft US standard, and exactly one warren lattice cell, so stall goods, kit
  pieces and the islanders' tents are interchangeable).
  - Double pitches are 3 x 6 m (furniture, food trucks).
  - Food pitches are 4 x 8 m, with the trucks round the food court.
- **Aisles:**
  - shed aisles 4 m, covered;
  - open aisles 6 m (20 ft, which takes crowds plus a hand truck);
  - a fire lane of 6 m clear every 60 m and round the whole perimeter;
  - no stall more than 45 m from a lane.
- **Rows** are double-loaded and back-to-back: `[pitch 3][pitch 3][aisle 6]`, a 12 m module per two rows.
- **Sheds:** steel-portal, open-sided, 12 m wide (3 m bay, 4 m aisle, 3 m bay, plus eaves).
  - Lengths are 60–120 m and the eaves 3.6 m.
  - Barn-red, cream or galvanised, by city style (07).
  - Permanent stalls have lockable roll shutters and pegboard; open pitches have none.

### 1.4 Lighting (the user: "the parking lot stays well lit throughout the night")
- **The lot:** a new lamp kind **5, lot pole**:
  - a 9 m pole with 1–4 heads;
  - spacing about 2.5x the mounting height (≈ 22–25 m) in the landscape islands, giving 16–32 lux average with a
    max/min uniformity under 4:1 (IES RP-20 practice, 01_research §2.4);
  - on **dusk to dawn every night**, whatever the market's state.
- **The market floor:**
  - warm festoons across every open aisle at 4.2 m (scheme 4 "market warm");
  - fluorescent/LED battens inside the sheds;
  - all off at night except a security level, a festoon every 4th aisle, while no island is anchored.
- **Islanders' tents and their stalls:** multicolour festoons, lanterns, chase bulbs and wash, scheme 5 "Skein".
  - The tents glow through their canvas (an emissive canvas lobe), so they read from a kilometre away.
  - They stay lit after hours but shuttered: a tent is "closed but glowing", the islanders' signature.
- **Real lights:** none of their own. The market's bulbs and pools join the StreetLights pool (§7.2).

---

## 2. Stalls and occupancy

### 2.1 Stall kinds
| kind | size | where | share | tenure |
|---|---|---|---|---|
| `shed` | 3 x 3 m bay, shutter, pegboard, power | covered sheds | 35 % of all stalls (= every permanent stall) | **permanent** lease (a year, renewed) |
| `open` | 3 x 3 m painted pitch | open-air rows | ~55 % | **rotating**, by the season |
| `open_double` | 3 x 6 m | row ends, by the vendor lane | ~6 % | rotating |
| `food` | 4 x 8 m truck pad with a hook-up | round the food court | ~4 % | permanent half / rotating half |

Two further kinds are **not** counted in the brief's percentages:
- `tent_slot`: 6 x 6 m and 9 x 9 m pads in the apron, for the islanders at a fair (§5.6);
- `logistics`: the mooring field's own pads.

### 2.2 The tenure model (pure, deterministic from the world seed)
- **Permanent stalls (35 %)** hold an annual lease.
  - Each lease runs `term = 52 weeks` from a hashed start week. The renewal chance is 0.85.
  - On a non-renewal, the stall goes to the head of that market's waiting list the following week.
  - A stall's tenant is a **post** in the NpcOccupancy sense: role `market_trader`. Its id is `<market>/S<n>:trader:0`,
    and a second post `:hand:0` covers busy stalls.
  - Each tenant is a real person of that town. The cluster market solves the post like any job.
  - Their hours are Fri–Sun 08:15–18:30, setting up before the 9:00 opening.
- **Rotating stalls (65 %)** turn over "every few months".
  - A **season lease of 8–16 weeks** (hash per stall and term). Seasons are staggered, so ~8 % of the rotating stalls
    change hands in any week.
  - A season tenant is drawn per stall per term from **the vendor pool** (§2.3) of the market's city cluster, and the
    nearest towns within 8 km.
- **Weekly presence:**
  - A permanent tenant is present with p = 0.96 (sickness, holidays).
  - A season tenant is present with p = 0.88.
  - Empty pitches are then **back-filled by day vendors** from the waiting list (the Shipshewana and Kobey's rule:
    no-shows are resold at dawn). A day vendor is a hashed draw from the same pool.
- **The guarantee:** for every market and every open day, `occupied / stalls >= 0.80`.
  - Day vendors fill up to a hashed per-day target `T(day) in [0.80, 0.97]`, higher in summer and lower in Dec–Feb.
  - The test proves it over 2 game years (§12).
  - **The vacancies are the islanders' room:** at 80–97 % there are always 3–20 % of stalls free when an island
    arrives (§5.5).
- **Purity:** `tenant(market, stall, day) -> {pid|islander, kind: permanent|season|day|islander, category, since}`.
  - It is a pure function of (seed, market, stall, day, journal deltas), like `NpcOccupancy.on_duty` (07_occupancy.md
    "Queries").
  - It works for unloaded markets, and the story engine can query it.

### 2.3 The vendor pool: "individuals from all walks of life"
- **Who can vend.** Any adult in the cluster can be a vendor. A person's weekend vendor propensity is a weighted draw
  over their existing traits (no new trait layer). The main sources are:

  | who | weight × | sells (category) |
  |---|---|---|
  | retired | 3.0 | antiques, collectibles, books, tools, crafts |
  | homemaker | 2.0 | household, clothing, baked goods, crafts, plants |
  | unemployed / struggling or in debt | 2.0 | used household, clothing, salvage, repairs |
  | second job: `money_reasons` has two_jobs, sends_money_home or raising_kids_alone | 2.5 | new goods, food, clothing |
  | owns_business, `money_style` spender or saver | 1.2 | new goods, specialty |
  | trades: mechanic, builder, smith-like, factory hand | 1.5 | tools, parts, salvage, repairs |
  | farm households | 2.0 | produce, eggs, honey, plants, meat |
  | students over 18 | 0.8 | clothing, media, food |
  | Lowliners (§9) | 3.0 in the South, 2.0 in the north | knitwear, rope, lights, bells, sky goods, repairs, cooked food |
  | everyone else | 1.0 | any |

- **Categories** (06 has the full table and price bands). There are 16:
  antiques, collectibles, used household, furniture, clothing (used), clothing (new), tools and hardware, salvage and
  parts (from the Drops), electronics and repairs (rare: the Panel Board rations panels), books and media, toys and
  games, crafts, produce and farm, plants, food (cooked), sky goods (islanders only).
- **Shelf rules:**
  - A stall's goods come from its category: a stall-dressing table in 06 lists the kit pieces per category.
  - Its signage is a hand-lettered board from the sign atlas.
  - The vendor's outfit uses the person's own outfit, with an apron or lanyard prop.

### 2.4 Island-anchored occupancy (the brief: "the islanders will set up in every vacant shop")
- From the first market day after the gondolas run (§5.4), **every stall that `tenant()` leaves empty on that day
  becomes an islander stall**: kind `islander`, island id, and 2 islanders.
  - On Fri–Sun this is the 3–20 % vacancy.
  - **On Mon–Thu (island mode) every stall not held by an islander is closed** (local booths only open at weekends).
    The islanders hold their stalls every day, and the open-day occupancy is just the islander stalls plus the tents.
- Islander stalls carry their island's specialty goods (`sky_islands.json islands[].trade`) and the islanders' lights
  (scheme 5).

---

## 3. What the generator writes (the GENERATOR stream)

### 3.1 Siting inside `plan_city`
- A new function `_market_pass(pl, spec, U, V, core, height, blocked)` in `tools/settlegen/market.py`, called from
  `plan_city` right after `_jobs_pass` (`city.py:299`). It runs for **every settlement**.
  - Villages under 2,000 people skip `_jobs_pass` (`city.py:582`) but still get a market.
  - Calder plans through `tools/settlegen/town.py` / `calder.py`, so the same pass is called from `build_calder`
    (`tools/map_expanded.py:1728`).
  - It reserves the whole site: market, parking, apron and mooring field. Each part is stamped with `pl.occ.poly`, and
    its areas are appended to `pl.areas`.
  - It lays the frontage street and connector as `pl.street(...)`, with the industrial-park checks.
  - It puts `{"market": {...}}` into the plan result: the site polygon, the frame `(ua, side, va)`, the stalls, the
    sheds, the parking rows, the apron, the mooring field and the entrances.
- `city.structures()` (`city.py:833`) gives each shed, gate house, food-court block and restroom a catalog record
  (prefix `<PFX>-M01..`).
  - Sheds are a new `works`-like kind `market_shed`: a steel portal, open sides and roll shutters.
  - Stalls, tents and goods are **not** catalog buildings. They are runtime kit (§11).
- map_expanded `--game-data` (`tools/map_expanded.py:2126+`) writes the terrain.json areas:
  - `market_floor` (paved: "asphalt" surface; see §0 parking gotcha);
  - `parking` with a `"lot"` record in the `parking_lots.py` format, `type: "market"`;
  - `market_apron` (lawn);
  - `mooring_field` (lawn, with `deadmen` points).

### 3.2 `godot_project/remake/markets/flea_markets.json` (written by `tools/markets/make_markets.py`, packed)
```
{"version": 1,
 "markets": [{
   "id": "FM-SOL", "city": "Solana Point", "name": "…", "style": "<sign style id, 07>",
   "frame": {"s": s0, "x": x0, "yaw": a},          # site frame: u along the frontage, v away from the road
   "limits_r": 0.78,                                # its normalised radius (the test reads it)
   "site": [[s, x], ...], "floor": [[s, x], ...], "apron": [[[s, x], ...], ...], "mooring": [[s, x], ...],
   "entrances": [[s, x, yaw, "car|walk|vendor"]], "pylon": [s, x, yaw], "arch": [s, x, yaw, width],
   "stalls": [[u, v, yaw, kind, row, shed_or_-1], ...],   # kind 0 shed 1 open 2 open_double 3 food
   "sheds":  [{"id": "SOL-M01", "u0":, "u1":, "v0":, "v1":}],
   "tent_slots": [[u, v, yaw, size_m, ring], ...],        # ring 0 lot perimeter, 1 apron, 2 mooring margin
   "lot": {"spaces": n, "accessible": n, "rows": [[u0, u1, v_front, depth, facing], ...]},
   "poles": [[u, v, heads], ...], "festoons": [[u0, v0, u1, v1, h, scheme], ...],
   "deadmen": [[u, v], ...], "stations": [[u, v, yaw], ...],   # ground anchors; ground stations (up to 4 per island)
   "stats": {"stalls": n, "permanent": n, "spaces": n, "floor_m2":, "parking_m2":, "apron_m2":}
 }]}
```
- Coordinates are in the site frame (metres, u/v); the runtime maps them through `frame`.
- One file covers all markets, about 30 KB packed.

### 3.3 Islands: `godot_project/remake/sky/islands.json` (make_islands) gets `"moorings"`
```
"moorings": {"line_houses": [{"x":, "z":, "yaw":, "side": "N|S|E|W", "cells": [w, d]}],      # anchor hawser winches
             "stations":    [{"x":, "z":, "yaw":, "kind": "passenger|cargo", "cells": [w, d]}]}
```
- Each is placed on the rim between the bridges and away from the hoists.
- There are 2–4 line houses (by blocks) and 1–4 stations: 1 at 1–2 blocks, 2 at 3–5, 3 at 6–8, 4 at 9–10.
- The warren lattice reserves them like hoists (`tools/sky/warren/lattice.py:116-120`): a rectangle of `cells`
  marked RESERVED, plus a 1-cell walk strip to the paths.
- **This is a request to the warren GENERATOR stream** (other agents own these files now). See §13.

### 3.4 Canon (DATA)
**Done 2026-10-15** in `tools/bible/canon_sky.py`: `market_moorings`, `line_ranks`, `settled`, the Skein's
`families` / `coming_down` / `line_or_ground`, the new history and lexicon (§8.1).

**Still to add when the runtime needs them:**
- per island, `mooring_crew`: 24 named posts drawn from its winch hands, riggers and hoist masters;
- per island, `market_goods`: from `trade` and `specialty`;
- per island, `settled_origin_weight`: which towns its settlers favour, for the Line Rows mix.

These are new keys only, so nothing existing reshuffles. Then rerun `make_bible` with the venv python.

### 3.5 Places and occupations (DATA)
- `tools/places/make_places.py` adds:
  - `pt("flea_stall", "Flea market stall", "retail", ["stall"], {"market_trader": 1}, ["09:00", "18:00", "fri-sun"],
    [("flea", 0.35, ADULT, 75), ("browse", 0.2, ANY, 50)], third=True, price=0, ...)`;
  - the shell `stall`;
  - `flea_food` (food trucks);
  - `flea_office` (the market office: a manager, a warden and a clerk, Mon–Sun).
- The occupations table (npc_traits.json) adds `market_trader` (wage band like shopkeeper's) and `market_warden`.
  Islander jobs live in sky canon, not in the floor table.

### 3.6 Lamps
- `tools/street_lamps.py` adds lamp kind **5, lot pole** (`HEAD[5]`: 9 m, 2–4 heads, warm-neutral):
  - from `markets[].poles`;
  - from **every** `parking` area with a lot record (downtown and park-and-ride lots get lit too: a gap today).
- It adds festoon schemes **4, market warm** and **5, Skein multicolour**.
  - Scheme 5 strings are **not** baked. They are made at runtime by the tents (§6.3), because they exist only while
    islanders are present.

---

## 4. The calendar and the hours (state machine)

### 4.1 Weekdays (decided: the game opens on a Wednesday)
- **The single source** is `remake/events.json` → `"start_date": "2752-05-24", "start_weekday": 2` (0 = Monday),
  written by `tools/make_events.py:52`. TransitDemand already reads it (`transit_demand.gd:37-39`).
- **A new pure helper, `GameCalendar`** (`remake/scripts/world/game_calendar.gd`), loads it once:
  - `weekday(day) = posmod(day + start_weekday, 7)`, 0 = Monday, so day 0 is Wednesday;
  - `date(day)` (Gregorian from `start_date`);
  - `month`, `season`;
  - `is_market_day(day)` for Fri, Sat and Sun.
- **Everyone uses it:**
  - NpcLife (`npc_life.gd:399`) and NpcPlaces (`npc_places.gd:315`) switch from `posmod(day, 7)` to it.
  - TransitDemand switches from its own copy to it.
  - The comment at `DaySkySystem.gd:66` changes to "day 0 is the start date (events.json)".
  - **The Communicator's Date & Time app** (being built by another agent) must read `GameCalendar`, not its own
    weekday maths, so the app, the markets, NpcLife and transit can never disagree.
- Switching NpcLife to Wednesday shifts every baseline schedule by two weekdays, so lives need a rebake.
- One game day lasts 2,880 s real (`DaySkySystem.gd:14`). A market weekend is 2.4 real hours, and three weeks
  16.8 real hours.
- The game opens on a Wednesday, so the first market weekend begins two game days in (≈ 1.6 real hours).

### 4.2 Market modes (per market, per (day, hour); pure)
`FleaCalendar.mode(market, day, hour)` returns one of:

| mode | when | local stalls | islander stalls and tents | gondolas | lot lights | floor festoons |
|---|---|---|---|---|---|---|
| `CLOSED` | Mon–Thu and no island moored | shut | — | — | dusk–dawn | off (security level) |
| `SETUP` | Fri–Sun 07:30–09:00 | vendors arrive and set out | islanders set out | passenger + cargo | on if dark | on |
| `OPEN` | Fri–Sun 09:00–18:00 | open | open (if moored) | passenger + cargo | on if dark | on |
| `ISLAND_DAY` | Mon–Thu 09:00–18:00 while moored | **shut** (roll shutters down, pitches empty) | open | passenger + cargo | on if dark | on over the islander aisles |
| `TEARDOWN` | 18:00–19:00 every open day | day vendors pack up; sheds roll down | tents close (flaps down, lights stay on) | passenger + cargo | on | on |
| `AFTER_HOURS` | 19:00–07:30 | shut | **closed, lit** (scheme 5 glow at 60 %) | **passenger only**, every 15 min (every 30 min 00:00–06:00) | **on** | 1 in 4 aisles (security), all aisles while moored |
| `MOORING` / `CASTING_OFF` | the sequence phases (§5) | as the day's row | — | as §5 | on | as the day's row |
| **`CELEBRATION`** (**Bright Week**: ≥ 5 islands moored) | **every day** 09:00–18:00, plus a lantern market 18:00–21:00 | **open every day**, local booths included (weekday no-shows filled by day vendors, so ≥ 80 % holds daily) | open, plus the evening lantern market | passenger + cargo; passenger only after 21:00 | on | **all aisles all night**, plus the islands' lights strung over the whole market and lot |
| **`HOLIDAY`** (**the Sky Holiday**: ≥ 7 islands at a town or village market) | as CELEBRATION, with the tents and food open to 22:00 | open | open | **free for children**; extra cabins | on | all, plus the town decorated (§6.4) |

- **The lot is lit dusk to dawn in every mode**, moored or not (the brief).
- **Precedence:** `HOLIDAY` > `CELEBRATION` > the moored or local rows.
  - CELEBRATION runs from the first SETUP after the 5th island reaches SERVICE until fewer than 5 remain.
  - HOLIDAY days are each day the market opens with ≥ 7 in SERVICE at 06:00, **at most 3 days in a row**.
  - HOLIDAY applies at **town and village** tiers only. A city with 7+ is a CELEBRATION; its Great Fair is its own
    feast (06 §8).
- The NpcPlaces hook:
  - `NpcPlaces.open_on/is_open(uid)` for kind `flea_stall` delegate to `FleaCalendar.stall_open(market, stall, day,
    hour)`. That combines the stall's tenant (§2.2) with the mode.
  - So NpcLife errands (`npc_life.gd:470-497`) see the right hours with no special case.

## 5. The mooring (anchoring) sequence

### 5.1 Who comes, and when: a deterministic visit calendar
- The brief's "when a floating island is near one" meets two facts:
  - The drift is fast. At 4–9 m/s west and a ~58 km deck circumference, every island passes every city's s once in
    about 3 game days (`sky_drift.gd:33`).
  - Within ±3 km of a market's x, that is **~10 islands a day per market**.
- So nearness alone would moor an island everywhere, always. The canon already has the answer: hoists are **booked by
  the plumb a week or more ahead, and the weather reader trims the island to pass over at that hour**
  (`sky_islands.json hoist_trade.schedule`).
- **`FleaCalendar.visits(market, week)`** is a pure function of (seed, market, week). It returns the islands booked to
  moor, with an arrival hour, a stay and a host/follower role.
  - **A booking:** each week, each market has a chance of a **host** booking: p = 0.40 for a city, 0.25 for a town
    and 0.15 for a village. A host arrives Wed 12:00–Thu 18:00 (so it
    is trading by Friday). It is hashed from the islands not already booked that week, and only those with
    `specialty` in a trade set or `factor >= 10`.
  - **Followers ("drawn to the anchored island"), a chain:**
    - Each island that reaches SERVICE draws **one more** island with probability `q`.
    - The newcomer is hashed from the islands whose drift passes within `ATTRACT = 12 km` during the stay and that
      are not booked elsewhere. It arrives 6–36 h later. The chain stops at `MAX_RAFT 10` (`sky_drift.gd:31`).
    - So the raft size N has `P(N ≥ k) = q^(k-1)`.
    - `q` by tier: **city 0.60, town 0.45, village 0.42**.
    - Raised on special weeks: a **Great Fair 0.75** (cities, 06 §8) and a **town's Market Day 0.60 (town) / 0.55
      (village)**, which are booked at host p 0.8.
  - **Expected numbers** (4 cities, 8 towns, 10 villages; 52 weeks):
    - Moorings a year: cities 4 × 0.40 × 52 ≈ 83; towns 8 × 0.25 × 52 ≈ 104; villages 10 × 0.15 × 52 ≈ 78. That is
      ~265 island weekends, ~5 a game week.

      | per mooring | ≥ 3 (fair) | ≥ 5 (Bright Week) | ≥ 7 |
      |---|---|---|---|
      | city, q 0.60 | 36 % | 13 % | 4.7 % |
      | town, q 0.45 | 20 % | 4.1 % | 0.83 % |
      | village, q 0.42 | 18 % | 3.1 % | 0.55 % |

    - **Bright Weeks (celebrations), per year:**
      - cities 83 × 0.13 ≈ 10.8, plus Great Fairs 4 × 0.32 ≈ 1.3;
      - towns 104 × 0.041 ≈ 4.3, plus Market Days 8 × 0.8 × 0.13 ≈ 0.8;
      - villages 78 × 0.031 ≈ 2.4, plus Market Days 10 × 0.8 × 0.092 ≈ 0.7.
      - Total **≈ 20 a year, about 5 a season across the map**: special but regular. A city has one about every
        4 months; a given town about once in 2 years.
    - **Sky Holidays (≥ 7 at a town or village), per year:**
      - towns 104 × 0.0083 ≈ 0.86, plus Market Days 6.4 × 0.047 ≈ 0.30;
      - villages 78 × 0.0055 ≈ 0.43, plus Market Days 8 × 0.028 ≈ 0.22.
      - Total **≈ 1.8 a year somewhere on the map**. A given small town sees one about every 10 years ("most towns see
        one in a lifetime" in story terms): rare and memorable.
    - Tuning knobs: `q` per tier (frequency of large rafts) and host p (overall). The `flea_sky_test` histogram checks
      these within ±30 % over 20 simulated years.
    - With 100 islands and ~1,500 going down to settle each year, islands are on the ground somewhere every weekend:
      **coming down is routine** (canon `market_moorings`).
  - **Stay** (drawn at arrival): 70 % leave after the first weekend (Mon 06:00), 18 % after the second, 12 % after
    the third. **No island stays more than 21 days** from its mooring.
  - A follower never stays past its host plus 7 days. If the host leaves first, the longest-staying member becomes
    host.
- **SkyDrift is steered to honour the calendar.** A raft with a booking gets `r.booking = {market, eta, s, x}`. Then
  `_raft_v` and `_wander` aim for it:
  - pace within `DRIFT` 4–9 m/s;
  - `vx` within ±`WANDER`, extended to ±3 m/s when booked;
  - if the island cannot make the ETA, the booking slips to the next lap (≤ 3 days), and the calendar's arrival hour is
    re-derived from the same hash. This keeps the calendar pure: the booking is a target, not a teleport.
  - At load, `warm_up` (`sky_drift.gd:507`) puts moored islands straight into their moored state.

### 5.2 The phases (game time; real time = game minutes / 30)

| # | phase | game time | what happens | rendering |
|---|---|---|---|---|
| 0 | `APPROACH` | −6 h … 0 | trims to the ETA; descends to **moor height 600 m** (`DECK_H − H_SWING`), H_RATE 0.5 m/s | bell-speech, signal lights |
| 1 | `HOLD` | 0:00–0:20 | station-keeping over the mooring field (vx = v = 0, a 30 m deadband) | fans |
| 2 | `CREW_DOWN` | 0:20–0:45 | **the first gondola**, the drop cage (one cabin on a single hoist line from the passenger station), **carries the mooring crew of 24** down | the cabin descends |
| 3 | `ANCHOR` | 0:45–2:15 | the line houses lower **8–24 hawsers** (2 + blocks × 2) onto the deadmen; the crew shackles them; the winches take up tension; the island is **anchored** | hawser lines appear one by one |
| 4 | `LOGISTICS` | 2:15–4:15 | the crew raise **3 logistics tents** on the mooring field: the Mooring Office (radio, schedule, fares), the Weigh House (every load and person weighed: the weigher), and the Crew Tent (rest, kitchen, first aid) | tents rise |
| 5 | `RIGGING` | 4:15–7:15 | **more cables drop**: track and haul ropes for each station; the crew bolt the portable ground-station frames to the plinths | ropes come down, one station at a time |
| 6 | `SERVICE` | 7:15 → | **several gondolas run** (§5.4), carrying people and goods; islanders come down and take every vacant stall at the next `SETUP` or `ISLAND_DAY` | cabins shuttle |
| 7 | `FAIR` | when ≥ 3 islands of the raft are in `SERVICE` | **trading tents ring the lot and every open adjacent area** (§5.6) | tents rise over ~3 h |
| 8 | `STRIKE` | departure −12 h | stalls cleared (Sun 18:00–22:00), tents down by Mon 04:00, cargo up | reverse |
| 9 | `CAST_OFF` | departure | the crew of 24 ride up last; hawsers slipped and hauled up; the island leaves the raft (`_split`) and climbs back into its band | lines rise |

- **Followers repeat phases 1–6 on their own.** Each drops its own crew of 24, its own hawsers and its own gondolas,
  and adds one more Crew Tent. They lash to the raft first with the existing rockets and bridges (`_fire`/`_lash`),
  then descend with it.
  - A moored raft's descent is shared: every member holds the raft's moor height.

### 5.3 Physics and placement rules
- **Static attachments by tier** (built with the market, §1.2):
  - city: a Mooring Field with 24 anchor blocks and 2 masts;
  - town: 1 mast and a 12-block ring;
  - village: an 8-block ring.
- **How an island makes fast:**
  - The host takes the mast (hawsers to the mast head, then to blocks) or the ring.
  - **Only the first few make fast to the ground:** 6 at a city, 4 at a town, 3 at a village. Each uses its share of
    the blocks: 4 per island in a city, 3 at a town, 2–3 at a village.
  - **Every later island lashes to the raft** (rockets, hawsers and bridges, as aloft) and rides on the anchored ones'
    hawsers. A raft is one body (`SkyDrift.transform` already makes a raft rigid), so the anchored members hold it all.
- **Each tier's limit is the Ten Knot's raft of 10 everywhere.**
  - Ground-anchored islands run their own gondolas to ground stations on the mooring ground and the apron.
  - Rafted-on islands send their people across the bridges to an anchored neighbour's stations, and run cargo by hoist
    (`_hoist_step`) to any dry open ground below.
  - At a village, a raft of 7–10 (≈ 1–1.5 km across) hangs over the town and its fields: the Low Sky.
- **Where the raft hangs:** the host's centre is over the mooring ground's centre.
  - Followers lash E or W first (along the drift), then N or S, so a raft of 3 spans about 300–800 m.
  - Islands never hang over the market floor itself (a "no-overhang" polygon = the floor plus 20 m). If a follower's
    berth would overhang it, the follower takes another face. If no face is clear, it doesn't come.
- **Ground stations:**
  - Each one stands on the mooring field or the apron, within 300 m horizontally of its island station.
  - The ropes run as a single span with no towers, like Peak 2 Peak's 3 km span (01 §4.2). The chord length is about
    `sqrt(600² + d²)`, 600–670 m.
  - A follower whose stations can't reach open ground runs a **cargo hoist only** (existing `_hoist_step`), and its
    people use the host's gondolas over the bridges.
- **Wind window:** a booking holds only if the weather system's forecast wind at 700 m is ≤ 9 m/s for the arrival day.
  The drag maths is in 01 §4.7.
  - In a storm (RemakeRain storm state), moored islands **stop the gondolas, ride out on the hawsers**, and in a storm
    longer than 6 h cast off early. This is a rare spectacle and a story hook.
- **No Coriolis bow on the fixed track ropes:** they are fixed. The haul rope and the free hoist lines keep
  `_line_point`'s bow (`sky_island.gd:1180`).
- **Weight (canon: weight is life):** every person down is 70 kg of lift gained aloft.
  - The weigher trims by taking up **ballast water** from a market standpipe in the cargo cabins (a nice visible job).
  - The calendar caps islanders on the ground at **25 % of the island's population** at any moment.
  - It caps **surface visitors aboard at `40 × blocks`**: this is the tourists' "lift ticket" (§9.2).

### 5.4 Gondolas (per island station)
- **The system** is an aerial-tram jig-back: **2 track ropes + 1 haul rope**, two cabins counterbalanced, one up while
  the other comes down.
  - Speed is 8 m/s, so a 640 m chord takes **~80 s** plus a 60 s dwell.
- **Two cabin types:**
  - **passenger: 28 people** (24 seated + 4 standing, the Peak 2 Peak cabin) plus **1 cabin warden**;
  - **cargo**: one skybox (2.4 × 2.4 × 3 m, 2 t, `hoist_trade.container`), or 3 pallets.
- **Stations per island:** 1–4 by blocks (§3.3). The first station is always passenger. At 3 or more, one is cargo.
- **Capacity per passenger station:** ≈ 28 × 3600 / 140 ≈ **720 people/h each way**. A raft of 3 moves ~2,000/h, which
  is plenty for a fair.
- **The first gondola (`CREW_DOWN`)** is the same passenger cabin, lowered **free-hanging on the station's hoist line**
  before any track rope exists. It is slow (2 m/s, ~5 min) and visibly swings.
- **Rendering:** ropes are line strips (the `_draw_line` pattern) or thin camera-facing ribbons; cabins are kit meshes
  (§11).
- **Riders** are NPC impostors inside within 120 m, and nothing beyond.
- **The player can ride:** the cabin is a moving platform carried like the island decks (`SkyIslands._carry`,
  `sky_islands.gd:280`).

### 5.5 The islanders fill every vacant stall
- At each `SETUP` / `ISLAND_DAY` while in `SERVICE`, `FleaVendors.islander_stalls(market, day)` = every stall whose
  `tenant()` is empty. Each one gets 2 islanders.
- **Which island holds a stall:** round-robin by island size over the raft's members. A stall stays with its island
  for the island's whole stay.
- **Goods:** from the island's `market_goods`. **Lights:** scheme 5, plus a clan-coloured cloth hung over the shed bay
  or the pitch.

### 5.6 The fair (3 or more islands anchored): trading tents
- **When:** at `FAIR`, tents go up on `tent_slots` in ring order:
  - ring 0: the lot perimeter, on the landscape strip and the apron's first 10 m;
  - ring 1: the rest of the apron;
  - ring 2: the mooring field margins (clear of the hawsers and stations);
  - ring 3 ("any open adjacent area"): extra slots the generator found on free, dry, flat cells within 150 m of the
    site **and inside the city limits**. Never on roads, never in lots of other buildings.
  - **ring 4 (Bright Week and the Sky Holiday only): the spill.**
    - Nearby fields, parks, school grounds and **closed streets** within 600 m (towns and villages: anywhere inside
      the limits).
    - The generator lists these as `spill_slots` with a kind: `field` / `park` / `schoolground` / `street`.
    - Street slots line both kerbs of a closed main-street block, leaving a 4 m middle lane for emergency vehicles.
    - On those days NpcTraffic treats the closed blocks as closed (no through route).
- **How many:** `tents = Σ over the raft (6 + 3 × blocks)`, capped by the slots. A raft of 3 average islands (~4 blocks
  each) puts up ≈ 54 tents.
- **What a tent is:**
  - **≥ 2 islanders** working it (3 in a 9 × 9 tent);
  - **shelves and tables**: 2 shelf units, 1–2 tables and a counter;
  - goods from the island's trade;
  - its own string lights.
- **Kinds** (§11): `bazaar_pagoda` 6 × 6, `bazaar_double` 6 × 12 (two pagodas joined), `event_marquee` 9 × 9 and
  9 × 18 (food halls, music), and one **Lantern Top** (a 24 m round big-top) per fair of 5 or more islands.
- **Colour:** the island's clan colours (`islands[].colors`) on alternating panels, kanat-style patterned linings, and
  pennants and bunting. **Colourful, whimsical and lit**, per the brief.
- **Lot use:** the lot keeps its stalls clear. On fair days the **apron's remaining grass becomes overflow parking**
  (marked by the tent ring), and 30 % of the paved bays nearest the entrance become bus and tram drop-off.

### 5.7 States in data
`FleaCalendar.mooring(market, day, hour)` returns `{phase, members: [{island, role, phase, arrive, leave, stations,
crew_posts}], fair: bool}`. It is pure. SkyDrift and SkyMooring read it, and the story engine can query it.

---

## 6. Runtime classes (the RUNTIME stream; `godot_project/remake/scripts/markets/`)

| class | kind | job |
|---|---|---|
| `GameCalendar` | static, pure | weekday, date and season from `DaySkySystem.day` (§4.1) |
| `FleaCalendar` | static, pure | `mode(m, day, hour)`, `visits(m, week)`, `mooring(m, day, hour)`, `stall_open(...)` (§4, §5) |
| `FleaVendors` | static, pure | `tenant(m, stall, day)`, `islander_stalls(m, day)`, `tents(m, day)`, the vendor pool per city cluster (§2) |
| `FleaMarkets` | Node (in RemakeStation after StreetLights) | loads flea_markets.json; per market a tier: FAR (pylon bulbs, lot glow), MID (< 900 m: merged sheds and stalls), NEAR (< 250 m: goods, people, shutters); answers WorldQuery |
| `FleaMarket` | Node3D per loaded market | builds stalls, shed shutters, goods, festoons and signage as merged chunks (32 m cells, RenderingServer instances like the warren chunks); swaps state on mode change |
| `FleaTents` | helper of FleaMarket | builds the islanders' tents for the day's `tents()` list: frame, canvas, shelves and tables, goods, Skein lights; one merged mesh per 4–6 tents |
| `SkyMooring` | RefCounted inside SkyDrift | the moored raft state: `booking`, `moored {market, h, anchor}`, holds v = 0; suppresses `_cast_offs` for moored edges (the "market knot", §8.1); steers booked rafts (§5.1) |
| `SkyRopeway` | Node3D child of the island (near tier) + ground part | hawsers, track and haul ropes, the jig-back cabins, the drop cage; ground stations and logistics tents; riders as impostors; the player as a carried rider |
| `FleaCrowd` | feeds NpcPopulation | shoppers come from NpcLife stays (`what: "flea"`); vendors from FleaVendors; islanders from SkyFolk's generator (sky outfits) placed on the market's walk graph |

### 6.1 Hooks into existing code (small, named edits)
- **NpcPlaces** `open_on` / `is_open` (`npc_places.gd:313-335`): kind `flea_stall` → `FleaCalendar.stall_open`.
- **NpcLife** `stays` (`npc_life.gd:393`):
  - a vendor's own entries (`what: "vending"`, Fri–Sun 08:15–18:30 on days `tenant()` names them);
  - the market as a weekend errand through the normal `reg` / visits path (purpose `flea`, `per_week 0.35`; at
    weekends ×1.4 already applies, `:487`);
  - an extra "island fair" boost of ×2.5 while a fair is on.
- **NpcOccupancy** (`npc_occupancy.gd:207`): the permanent stalls and the market office are posts. The season and day
  vendors are **not** posts: they are FleaVendors draws, so the cluster market isn't re-solved weekly (keeps
  07_occupancy "Stability").
- **SkyDrift** (`sky_drift.gd:150-256, :406`): `step` skips the movement of moored rafts and steers booked ones;
  `_meetings` lets followers berth on a moored raft; `_cast_offs` honours the stay instead of LASH_DAYS while moored.
- **SkyIslands** (`sky_islands.gd:204-258, :280`): place moored islands; carry riders in cabins.
- **SkyIsland**:
  - the hoists (`sky_island.gd:1128`) are paused while moored, except as a follower's cargo-only fallback;
  - the line houses and stations come from the `moorings` layout.
- **StreetLights**: lamp kind 5, festoon schemes 4 and 5, and a public `claim_lights(n, points)` so FleaMarkets shares
  the pooled OmniLights (§7.2).
- **road_surface.gd:83**: `market_floor` and market `parking` → "asphalt".
- **NpcTraffic** (`npc_traffic.gd:539`): drivers whose destination is a market park **in its lot rows**
  (`flea_markets.json lot.rows`), nearest free bay to the entrance, then the apron overflow. This also fixes kerbside
  overflow on fair days.
- **WorldQuery**: `market` (mode, mooring, tenants), `tenant`, `islanders_at`.

### 6.2 Player-facing
- Walk the market; buy and sell, haggle (06); rent a stall (06 §9).
- Ride a gondola up to the island, as a passenger with a fare; work as a hauler of cargo cabins (06).
- The fast-travel list shows moored islands as "Island fair at <market>".
- The PDA map marks markets with their sign icon, and marks a mooring with the island's name.

### 6.3 Weekend trips to other towns' markets (NpcLife)
The user: "people travel around the map to visit other towns' markets."
- **A new purpose `market_trip`** in `NpcLife.stays`. It is pure, seeded per (pid, day), like the errands at
  `npc_life.gd:470-497`.
- **Who:** adults (and children with them), on Fri, Sat or Sun.
  - Base chance 0.06 per market day (an out-of-town market about once in 6 weekends).
  - ×1.5 for retired people and for those whose `money_style` is tight (bargain hunters).
  - ×0.5 with no car access and no transit within 800 m.
  - ×2.5 if the destination is holding a **fair** that day (from `FleaCalendar`, pure).
  - Never on a day they work.
- **Where** (a gravity choice over all 22 markets except their own):
  - weight = `stalls × (1 + 1.5 × fair) × (1 + 0.5 × specialty match) / max(d_km, 2)^2`;
  - `specialty match` is 1 when the destination's draw (07 §2) suits the person: books for students and teachers,
    the livestock auction for farm households, antiques for the retired, sky goods for Lowliners;
  - the home market is the ordinary errand (`flea`).
- **When and how long:** leave 08:00–11:00; stay 2–4 h; travel by car (NpcTraffic, parking in that market's lot) or by
  tram/transit (`NpcLife` travel modes, `npc_life.gd:375-390`).
- **Cost:** the trip is one stay entry. Trippers count toward the destination's crowd only when it is loaded.
  - Their cars use the destination's lot rows.
  - Their absence empties their home a little at weekends, which reads well.
- **Story:** WorldQuery `who` can answer "who's at Traders' Landing from Calder today".

### 6.4 Bright Week and the Sky Holiday (the user, 2026-10-15)
- **Bright Week** (≥ 5 islands, any tier): mode `CELEBRATION` (§4.2).
  - The whole market, local booths included, is open every day while the islands stay, plus an evening lantern market.
  - NpcLife: `flea` visits ×2 in the town and ×1.5 in market trips toward it (on top of the fair's ×2.5).
  - The islands' lights are strung over the market and lot (scheme 5 festoons on every aisle and lot row: still
    bulbs, no new real lights).
- **The Sky Holiday** (≥ 7 islands at a **town or village** market): mode `HOLIDAY`, declared for **the surrounding
  area**:
  - **What "the surrounding area" is:**
    - the host town, plus every settlement and farm whose centre lies within **8 km** (floor distance, wrapping in s)
      of the market;
    - a **city** inside that radius is not declared (it is too big), but its trips toward the holiday get ×3.
    - Example: a holiday at Calder (s 26,300, x 2,411) takes in Pruett (3.7 km) and Bellhaven (5.3 km). Cedar Ford
      (3.4 km) is in too.
    - Data: `FleaCalendar.holiday(day) -> [{market, towns: [names], farms: bool, radius_m: 8000, days: [d0..]}]`.
      It is pure.
  - **Effects in NpcLife (`stays`)** for people whose home is in the area, on holiday days:
    - **Work:** only **essential** posts keep their shifts:
      - hospital, care home, police and fire, transit;
      - the charge stop and utilities;
      - food and drink (open and busy);
      - lodging;
      - farm chores (animals: 2 h morning and evening).
      - Everything else (offices, schools, retail outside the market, industry, civic) is **closed**.
      - `NpcPlaces.open_on` returns false for non-essential kinds in the area. `NpcOccupancy.on_duty` reports
        `vacant_reason: "holiday"`.
    - **The fair:** p 0.75 per person per day (children with parents), a 2–6 h stay, many in the evening (18:00–22:00).
      Leave home in family groups.
    - **Outside the area within 25 km:** p 0.15 per adult per holiday day (the `market_trip` path ×3).
    - **Decorations:**
      - every dwelling in the area hangs a **lantern** (a window glow and a porch bulb via `building_loader`'s room
        lights, forced on at dusk);
      - the town's main streets get **festoons** (scheme 5, runtime strings added to StreetLights for the holiday) and
        bunting;
      - the islands' bells and the town band are on a timetable.
  - **Transit:**
    - TransitDemand (`transit_demand.gd`, which already reads `events.json`) gets a dynamic event from FleaCalendar:
      demand ×2.5 on lines serving the area;
    - extra tram runs (TransitNet frequency ×2 on those lines);
    - a shuttle loop from the area's villages to the market.
  - **Traffic:** spill-slot streets closed; overflow parking on the fields; NpcTraffic routes round them.
- **How it's announced:**
  - **Bright Week:** on the market's marquee or dot-matrix board, a Wire radio advert, and the town paper. The PDA
    news feed (the Communicator) posts "Bright Week at <market>" the day the 5th island books (the calendar is pure,
    so it knows ahead).
  - **The Sky Holiday:**
    - The **town council declares it** the evening before (18:00), once the 7th island's mooring is confirmed.
    - It goes out over the Wire radio, on the Boards (public notice screens), and in town criers' bells. Bell-speech
      comes from the islands overhead.
    - A **PDA notification** reaches every player in or entering the area, as a Communicator alert with the holiday's
      days, closures and a map pin.
    - The Date & Time app marks the days.
  - Both are added to `events.json`-style dynamic events, so any system (transit, story, the radio) can read them.
- **Story hooks:**
  - "The Low Sky at Cedar Ford" is the event a village dates things by.
  - Weddings are timed to it (a lashing custom).
  - Lowliner families reunite with island kin.
  - Pickpocket-free (no caricature). The work at a holiday is crowds, lost children and a gondola stalled in wind.

## 7. Budgets (60 fps on the Steam Deck)
The baseline is Calder at ~42 fps, CPU-bound by traffic (4–8 ms) and people (~2 ms) (`research/perf_learnings.md:15,70`).
The markets are on the outskirts, so the town's traffic peak is not under them. But a fair is the busiest place in the
game, so the budgets are firm.

### 7.1 Geometry and draws
| item | LOD0 tris | LOD1 | LOD2 / far | draws (near, merged) |
|---|---|---|---|---|
| open stall: pitch + table + goods | 300 + goods 200–600 | 120 | — (MID: a coloured quad block) | 32 m chunk merge: ~1 draw per material per chunk |
| shed bay (shed is a catalog building) | 1,500 per 12 m bay | 400 | 60 | building LOD chain (existing) |
| shutter (down/up) | 40 | 40 | — | in the shed chunk |
| bazaar pagoda 6x6 (frame + canvas + lining) | 1,800 | 500 | 60 | 1 per 4–6 tents (merged) |
| bazaar double 6x12 | 3,000 | 800 | 90 | " |
| event marquee 9x9 / 9x18 | 2,200 / 3,800 | 600 / 900 | 80 / 120 | " |
| logistics frame tent 9x15 | 2,000 | 500 | 80 | 1 |
| Lantern Top (24 m round) | 9,000 | 2,000 | 300 | 2 |
| shelf unit / table / counter | 250 / 120 / 200 | drop | — | in the tent merge |
| gondola cabin (passenger / cargo) | 3,500 / 2,500 | 700 | 80 | 1 per cabin (moving) |
| ground station frame + plinth | 6,000 | 1,500 | 200 | 1 |
| island station / line house | from warren kit pieces (request, §11) | kit LODs | kit | kit chunks |
| ropes and hawsers | line strips or 2-tri ribbons per segment | same | far: none past 3.6 km (MID island tier) | 1 per island |
| festoon bulbs | 2 tris each (billboard, MultiMesh) | — | far bulbs to 4.4 km (StreetLights far tier) | 1 per market |
| pylon sign | 4,000 + neon tubes | 1,200 | 150 + bulbs | 2 |

- **Market at full fair, near (< 250 m):** ≤ 450k tris and **≤ 220 draws**, night included.
  - The rest of the scene stays within the existing Calder-class budgets (~2.6M tris city-wide noon, per the 20 km
    ring note).
  - A market at MID costs ≤ 25 draws; at FAR, 3.

### 7.2 Lights
- **No new real lights by default.**
  - The market's lot poles, aisle festoons and tent glows are **emissive bulbs** (MultiMesh, `street_bulb` /
    `sky_bulbs` shaders), plus **ground pools** in the merged `street_pool.gdshader` mesh.
  - Tent canvas glows by an emissive lobe in the canvas material.
- **Real OmniLights:** FleaMarkets claims **up to 8 of StreetLights' 28 pooled lights** (`StreetLights.gd:34`), every
  0.5 s, on the bulbs/tents nearest the player. They are shadowless, with omni_attenuation 1.6.
  - Gondola cabins have no real light: emissive windows, plus one pool decal under the station.

### 7.3 People and CPU
- **Animated NPCs:** ≤ 120 within 60 m. Beyond 60 m they are impostors (the NpcPopulation far-walker path), with
  every other frame updates beyond 30 m.
- **Market tick:** ≤ 0.4 ms a frame (mode checks 1 Hz, tenant lookups cached per day, chunk builds time-sliced on a
  worker as StreetLights does).
- **Mooring sim:** SkyMooring ≤ 0.05 ms per raft tick (SkyDrift runs at 10 Hz). Rope redraw ≤ 0.2 ms (13-point
  strips, only near-tier islands).
- **Memory:** markets ≤ 40 MB resident (shared kit plus merged chunks). Data ≤ 0.2 MB packed.

## 8. The island side and the profession

### 8.1 Canon: the market moorings (DONE 2026-10-15)
Canon now in `tools/bible/canon_sky.py`, regenerated into `sky_islands.json` and `research/bible/13_sky_islands.md`.

**New canon blocks:**
- `market_moorings`: the procedure, how often, stays, anchors by tier, weather and weight;
- `line_ranks`: the 7 ranks, which add up to the crew of 24 (checked by the build);
- `settled`: the Lowliners;
- confederation `families`, `coming_down`, `line_or_ground`.

**History:**
- **VY 418 the Mooring Compact:** every town keeps a mooring ground by its flea market. "Mooring Fields" is the old
  name from the hulks' service days. Traders' Landing was the first.
- **VY 431** the first gondolas (Andean-style jig-backs) and the Lines.
- **VY 452** the first Line Rows behind Solana Point's harbour.
- **VY 474 the Settlers' Shares Act:** island-born settlers get a birth share only after two years' registration.
- **VY 486 the Full Book:** the weight books fill, so about half of every family's children go down. That is some
  1,500 a year.
- **VY 489 the Draw Housing Ruling:** settlers queue for Draw homes like everyone else; the South Shore's poorer streets
  resent it.

**Changed wording:**
- The Long Drop is no longer "the only time most go to the floor".
- The plumb is no longer the Aloft's only contact.
- New lexicon: Lowliner, going down the line, the Lines.

**Kept stable on purpose:**
- No island's population, jobs or customs picks changed. The new custom went into the confederation text, not the
  hashed CUSTOMS list.
- The line ranks are separate from `JOBS`, so the island job counts are unchanged.

**Knot law:** at a mooring the Three-Day Knot is kept by **the market knot**, a short moot every third day.

**Weight:** the Weigh House weighs every person and load. Islands take on water ballast as people go down.

**Aligned (2026-10-15):** `research/sky_islands/03_society.md` (now "Why they live aloft, and why so many come down", the
plumb paragraph, the hooks), `02_history.md` (VY 418–489) and the sky `00_plan.md` (a canon-change note under the brief).

### 8.2 Island buildings and platforms (fitted to the warren lattice; a request to the warren streams)
All snap to the 3 m lattice, sit on the rim, and are reserved in `lattice.py` like hoists.

| piece | cells (w x d) | storeys | what |
|---|---|---|---|
| `moor_line_house` | 3 x 3 | 2 | a winch house at the rim: hawser drum, fairlead out over the edge, a control cab; 2–4 per island |
| `moor_station_pax` | 4 x 6 | 2 + roof | gondola top station: bull wheel and drive house, a platform with gates, a waiting hall, fare booth, rope anchors cantilevered 6 m past the rim |
| `moor_station_cargo` | 4 x 5 | 2 | as above, with a skybox cradle and a weigh scale |
| `moor_drop_cage_davit` | 2 x 2 | — | the davit for the first (free-hanging) gondola, beside a passenger station |
| `moor_signal_mast` | 1 x 1 | 4 | signal lights and the bell for bell-speech; tops a line house |

- **Per family:** each of the 44 warren families (`tools/sky/warren/civ/*`) dresses these with its own palette
  (`pieces.json palettes[civ]`) and 1–2 overlay pieces it already has: `ov_festoon`, `ov_lantern`, `ov_chochin_string`,
  `ov_awning_cane`, `ov_suq_canopy`.
- **The cores are shared:** the machinery, platforms and gates are one set.
- **About 6 new kit pieces plus per-family trims** (see §11).

### 8.3 The profession: the line crews ("the Lines")
Manning and maintaining moorings is the most esteemed trade aloft: it is how the island earns. New `JOBS` entries,
building on the winch hand, rigger and hoist master:

| rank (job id) | name | does | per island | pay share |
|---|---|---|---|---|
| `mooring_master` | the Mooring | commands the mooring: book, approach, anchor, strike; sits with the Helm at lashings | 1 | 4 shares |
| `anchor_master` | anchor master | the hawsers and the deadmen; the 3-day load survey | 1–2 | 3 |
| `sheave_keeper` | sheave keeper | the station machinery: bull wheels, drives, brakes; the daily inspection run | 2–4 | 2.5 |
| `rope_reader` | rope reader | walks and reads every rope (the magnetic test, by hand and by instrument): the rope log | 1–2 | 2.5 |
| `cabin_warden` | cabin warden | rides every passenger cabin (the tram rule: an attendant aboard), fares, safety, the tourists | 2 per station | 2 |
| `line_hand` | line hand | the crew: shackling, rigging tents, cargo, rescue on the rope | 10–16 | 1.5 |
| `greenline` | greenline | an apprentice, up to 3 years: knots, rope lore, the weigh book | 2–4 | 1 |

- **The mooring crew of 24** is drawn from these ranks. The rest are line hands and winch hands on call.
- **Pay (hyper-capitalist, the good way):**
  - Every fare and freight fee pays **the line toll**, 20 % of the gross, into the Lines' purse.
  - The purse is split by shares each lashing.
  - A line hand's year is ~C$ 52k-equivalent, against a floor median of ~C$ 41k (`02_money.md:22`). A Mooring earns
    ~C$ 140k.
- **Prestige:**
  - Rope marks (canon custom `rope_marks`) are extended with a **cabin bead** for every 100 descents.
  - "Cold hands" is the highest praise.
  - A Mooring is a candidate for the Helm.
- **Hazards:** storms, rope rescue (the 3.5 h evacuation rule), ground-weight. The healers carry line-burn salve.
- **On the floor:** the ground end of each station has **2 ground stewards** hired from the town: dock hands, mostly
  Cannery Union, whose canon stance is +0.1. The market office employs a **market warden** (06 §4).

## 9. Islander culture, tourism, and settlement

### 9.1 "Hyper-capitalist in a good way"
- Everyone aloft trades. A child keeps a stall at eight.
- Prices are haggled warmly; a deal is sealed with a cold handshake.
- Profit is honourable when it is **light**: honest weight, no hidden faults. A cheat is "heavy" and is shamed at the
  market knot.
- Clans compete on lights, signs and showmanship (`sky_signs.gd` already gives every store a lit sign). Wealth is
  shown by **giving lights**: a rich factor strings the whole lot.
- Work is hard and cheerful. The long kitchen feeds everyone, so no one trades from hunger, which is why they trade
  for joy.
- Dialogue cards use the lexicon: `lift`, `weigh`, `cold hands`, `heavy word`.

### 9.2 Micro-tourism (surface → island)
- **Getting up:** a surface visitor rides up for a fare (C$ 12 return, children half; 06 §11). Visitors aboard are
  capped at `40 × blocks` (lift). A queue forms at the Mooring Office tent.
- **What the islands sell:**
  - guided **rim walks**;
  - **snow** in a cloud (snow is a wonder since the Last Snow, VY 212; `canon_sky.py` "ice" specialty);
  - bell towers and the dove lofts;
  - food and drink in the long kitchens (paid seats for visitors);
  - knitwear fittings;
  - a lark joyride (expensive);
  - night markets under the island's lights;
  - **edge swings and rope bridges** between lashed islands (the whimsical part).
- **The islands cater to it:**
  - signs in floor speech;
  - a "heavies' rail" (an extra rail at the rim);
  - ground-weight chairs (inverted: low-g seats for fun);
  - souvenir cords with one knot ("your first lashing").
- **Game:** gondola rides are the cheap fast-travel to an island while it is moored. Ride time is ~80 s real.

### 9.3 Settlement flows (canon: `settled`)
- **Island → surface: routine and large.**
  - Families aloft have four or five children. Since the Full Book (VY 486) **about half of all island children grow up
    to settle on the floor**: some 1,500 a year.
  - They go at 16–25, usually at a mooring: a feast like a wedding, a knotted cord and a lantern for the new home.
  - **The Lowliners number ~29,000 (12 % of the floor):**

    | region | Lowliners | share of the region | note |
    |---|---|---|---|
    | south_shore | 15,000 | ~25 % | about a quarter of Solana Point; Line Rows in every South Sea town |
    | southland | 7,000 | ~12 % | |
    | kettle_valley | 4,800 | ~10 % | |
    | northland | 1,400 | ~7 % | |
    | north_shore | 800 | ~2 % | the fewest |

  - **Why the South** (canon `why_south`): chain migration to the first Line Rows, cannery and harbour work, the open
    weekend markets, and the island routes, which moor most often at the Starlite Swap.
- **Surface → island: rare but not unheard of.** It needs a moot's consent, a place in the weight book, and usually a
  marriage or a needed trade. About 50 a year (canon `the_other_way`); story hooks.

### 9.4 The Lowliners on the floor (name approved; discrimination follows the region)
- **Names:**
  - **Lowliner** is their own word, said with pride, and approved by the user.
  - The floor's formal census term, the other peoples' proper ethnic names, and any sub-group names wait for the
    political work. Use the **`[ETHNONYM: …]` placeholders** in data and docs, and never invent them in content.
  - "Cloudies" (existing canon) is a slur. Hostile NPCs only; the game frames it as such.
- **Regional feeling** (canon `regional_feeling`):
  - **North (north_shore, northland; t < 0.35):** they are few, and liked as neighbours, craftspeople and riggers.
    Prejudice is hardly felt.
  - **River towns (0.35–0.65):** in between.
  - **South (southland, south_shore; t > 0.65):** many, with **real, tangible friction in the poorer streets**:
    - Draw housing queues (the VY 489 ruling);
    - competition for entry work at the canneries, docks and building sites;
    - crowded schools;
    - the lights and music late.
    - It is warmer in the affluent districts and among people who work beside them (the contact effect).
- **What the systems model** (structural, never "deserved"):
  - **NPC attitude** toward a Lowliner = faction stance + personality (low A, high N → more prejudice) +
    **`regional_friction(t, area)`**:
    - near 0 in the north;
    - in the south it scales with the area's finances band (struggling/getting by → more) and the local Lowliner
      share (high share and low means → most friction; high share and comfortable → less).
  - **Hiring (cluster market, 07_occupancy):**
    - the pick weight for Lowliner applicants is 1.0 in the north;
    - it is 0.85 in southern employers with a negative faction stance or in struggling areas;
    - the Open Hand and Waymakers employers are 1.0 everywhere;
    - shown in WorldQuery stats so the story can name it.
  - **Money:** median wage ×0.85 in the South through the job mix (cannery, docks, building, markets), ×1.0 in the
    north. Not a trait penalty.
  - **Housing:** the South Sea cities' Line Rows (§9.5); elsewhere scattered or in small Line Rows.
  - **School:** no mechanic. A story beat can be an overcrowded southern school.
  - **Policing:** story only, handled with care.
- **No caricature** (01 §5.6):
  - no thief, curse, fortune-telling or "exotic" tropes;
  - individuals in every trade and every politics;
  - mixed families common (they intermarry widely);
  - their culture is the Aloft's own invented culture (bell-speech, rope marks, the long kitchen, the Line Halls), with
    no Romani words or symbols borrowed;
  - **a sensitivity read** (Romani and Traveller readers) before story content ships.
- **Institutions:** a Line Hall in every city (guild, savings club, chapel, dance floor; the Showmen's Guild model);
  **the Low Lashing** each June at Traders' Landing (the Appleby model); their own knot keepers.

### 9.5 Line Rows: surface warrens in the South Sea cities
The user: "the city turns into warrens for blocks at a time", in a hodge-podge of every island's style, with mixed
families per block. This is **the surface use of the warren generator and kit** (`tools/sky/warren`,
`remake/sky/warrens/kit`).

- **Where:**
  - Solana Point: ~11,000 Lowliners, half in Line Rows, ~14–18 blocks in 2–3 clusters (the oldest behind the harbour,
    the canon's VY 452 cannery streets).
  - Oceanview: ~2,400, 3–5 blocks.
  - Playa Verde: ~1,300, 2–3 blocks.
  - Pelican Cove: 1 block.
  - Small Line Rows (1–2 blocks) in Kessler, Calder, Bellhaven and Harrow Falls.
  - None as warrens in the north: there Lowliners live scattered in ordinary houses.
- **Settlegen side** (`tools/settlegen/city.py`, a new `_line_rows_pass` after `_market_pass`, own RNG stream):
  - It picks whole **street blocks** (the grid's `BK_U x BK_V`, 100 x 84 m in a city, `city.py:124`) in the inner and
    middle zones near the harbour or rail, in the older era bands.
  - It replaces their lots with one `warren_block` lot. The **streets, kerbs and sidewalks stay** (the block keeps its
    frontage), and the household count is kept: the people the lots held, at warren density.
  - It writes the block polygon, frontage sides, ground heights and the household list into
    `remake/warrens_surface/<town>.json`.
- **Warren generator side** (`tools/sky/warren`, a new entry `make_warren.py --surface <town>`):
  - **The deck is the block:**
    - the outline is the block polygon in a local frame (+X along the street grid);
    - the dock faces are replaced by **frontages**: the cells along each street are the walk/door edge, and doors face
      the sidewalk;
    - no rim, fence, balloons, hoists or bridges.
  - **Ground:** graded from MapTerrain heights (the generator already grades rolling decks, `FORMAT.md` "Walking").
  - **Mixed families, a hodge-podge:**
    - each **house lot** inside the block gets its **own civ (warren family)**, drawn from the islands its household
      came from (canon `islands[].warren`), weighted by the town's Lowliner origins;
    - so one block mixes, for example, a Cycladic house, a Kowloon stack, a Maghrebi courtyard and a Hanseatic
      gable;
    - the palette is per lot, as today (`pal_epoch`, FORMAT.md);
    - the generator's `civ` header becomes per lot: format version 4 adds a `u8 civ` per unit, plus a civ table.
  - **Height:** 3–5 storeys, stepping down to 2 at the block ends so the warren meets ordinary streets. Courtyards,
    stairs and passages as on the islands.
  - **Ground floors on the street:** shops (Lowliner trades: knitwear, rope, bells, lights, cookshops), a Line Hall in
    the main cluster, and island-style stall arcades.
  - **Units → households:** each `home` unit is a Lowliner household (with mixed families: a share are married to
    floor-born partners).
- **Runtime:**
  - `SkyWarren` is reused with a **static ground frame** (a Transform3D from the block's (s, x), no drift, no carry).
  - Chunks, LODs and the 3 m lattice are as aboard.
  - Far LODs join the building LOD chain (`building_loader`), so a warren block reads as a town block from afar.
  - Night: the Aloft love of lights carries down: SkySigns-style signs and festoons over the lanes. That's the
    South's lively night.
- **Occupancy:** NpcOccupancy reads the units as a manifest (`rooms`-like JSON from the warren twin's units and
  doors), so residents, workers and shoppers work as everywhere else.
- **Kit needs:** none new for a start. Ground-floor shopfronts already exist in many families. A `kerb_frontage`
  piece and a low `block_end_step` may be requested.
- **Budgets:** the same as a warren chunk aboard (perf_learnings: 84–110 fps aboard). A 14-block Line Rows cluster ≈
  2 islands' worth of chunks, streamed by distance.
- **Ownership:** the warren generator and kit are another stream's today. This is **a request**, scheduled after their
  work lands (§13).

---

## 10. Data formats (summary)

| file | writer | contents |
|---|---|---|
| `godot_project/remake/markets/flea_markets.json` (packed) | `tools/markets/make_markets.py` (from the plan via map_expanded `--game-data`) | §3.2: sites, stalls, sheds, tent slots, lot rows, poles, festoons, deadmen, stations, signage anchors |
| `godot_project/remake/markets/market_styles.json` | DATA (07) | per market: name, sign style, palette, mascot, festoon scheme, shed colour, typeface atlas ids |
| `godot_project/remake/markets/goods.json` | DATA (06) | categories → price bands, haggle factors, kit dressing pieces, sourcing |
| `terrain.json areas` | map_expanded | `market_floor`, `parking` (lot record `type: "market"`), `market_apron`, `mooring_field` |
| `law/settlements.json` | map_expanded | new `limits` polygon per settlement (§1.1) and `market` id |
| `street_lamps.json` | street_lamps.py | lamp kind 5, festoon schemes 4/5 |
| `remake/sky/islands.json` | make_islands (warren stream) | `moorings {line_houses, stations}` (§3.3) |
| `remake/bible/sky_islands.json` | canon_sky | **done:** `market_moorings`, `line_ranks`, `settled`; **to add:** per island `mooring_crew`, `market_goods`, `settled_origin_weight` (§3.4) |
| `remake/events.json` | make_events.py | `start_date`, `start_weekday` 2: **the one day-of-week source** (§4.1) |
| `remake/warrens_surface/<town>.json` + warren files | settlegen `_line_rows_pass` + `make_warren.py --surface` | Line Rows blocks (§9.5) |
| `remake/textures/signs/*.png` + `signs.json` | `tools/signs/crop_sheets.py` from the Grok sheets (08) | market, island and business sign atlases |
| `npc_places.json` | make_places | `flea_stall`, `flea_food`, `flea_office`, shell `stall` |
| `npc_traits.json` occupations / populations | traits tools (`traits_fmt.py`) | `market_trader`, `market_warden`, `rope_steward`; population `lowliner` (sky-derived traits, floor-born) |

- **Nothing about tenants or visits is baked.** They are pure functions of the seed (§2.2, §5.1), so the files stay
  small and stable.

## 11. Kit pieces (the KIT stream; Blender, built to the shared-kit rules)
- Low-poly with a shared atlas.
- Emissive bulbs are separate small meshes, or MultiMesh-instanced points named `bulb_*`.
- `lights_*` anchors follow the sky 00_brief contract.

| id | what | notes |
|---|---|---|
| `fm_pitch_open` | painted 3x3 pitch, table, cloth, 2 crates | goods slots `g0..g5` |
| `fm_pitch_table_long` | 2.4 m table + rack | clothing variant |
| `fm_shed_bay` | catalog kind `market_shed` (the gen pipeline, not runtime kit) | shutter states |
| `fm_shutter` | roll shutter, up/down | animated by scale |
| `fm_goods_*` (≈ 40) | goods clusters by category (06 table): crates of tools, racks of clothes, book boxes, furniture, produce bins, plants, lamps, rugs, sky goods (knitwear, rope coils, bells, honey jars, lanterns) | 150–600 tris each, atlas |
| `fm_food_truck` | 2 variants | from the fleet bodies if one exists; else a static prop |
| `fm_gatehouse` / `fm_restroom` / `fm_foodcourt` | small catalog buildings | gen pipeline |
| `fm_lot_pole` | lamp kind 5 head + pole | StreetLights HEAD[5] |
| `fm_festoon` | festoon catenary + bulb | runtime-drawn (`_festoon`); bulb mesh only |
| `tent_bazaar_6` | pagoda 6x6: eave 2.4, ridge 5.6, frame, PVC canvas in 2 colour slots, kanat lining, finial, pennant | shelves and tables are separate |
| `tent_bazaar_6x12` | two pagodas joined | |
| `tent_event_9` / `tent_event_9x18` | frame marquee, gable, clear or bunting walls | food hall, music |
| `tent_lantern_top` | 24 m round top, 4 king poles 12 m, striped | one per big fair |
| `tent_logistics_9x15` | white frame tent, ballast blocks, signs "MOORING OFFICE / WEIGH HOUSE / CREW" | |
| `tent_shelf` / `tent_table` / `tent_counter` / `tent_rail` | display furniture | |
| `tent_ballast` | water barrel and sandbag | paved-lot ballast (01 §1.1) |
| `skein_lantern` ×6 | hanging lanterns: pierced, fanous-like glass, paper, globe, star, bell | emissive |
| `skein_bunting` / `skein_pennant` | runtime strips, clan colours | |
| `gondola_cabin_pax` | 28-person cabin, warden's console, big windows, clan livery | 3.5k tris |
| `gondola_cabin_cargo` | open frame carrying a skybox | 2.5k tris |
| `gondola_carriage` | track-rope carriage with sheaves (both cabins) | |
| `ground_station` | portable steel frame: return wheel, rope anchors, platform, gates, plinths | 6k tris |
| `deadman_ring` | concrete anchor block with a ring, flush in the lawn | every market (8 / 12 / 24 by tier) |
| `mooring_mast` | 30 m steel lattice mast with a turning head, a hawser cone, a ladder, red obstruction lights and festoons to the ground | towns (1) and cities (2); a landmark when no island is moored |
| `moor_line_house`, `moor_station_pax`, `moor_station_cargo`, `moor_drop_cage_davit`, `moor_signal_mast` | island pieces (§8.2) | **warren kit request**: the warren_kit stream builds these to the lattice when free |
| sign kit (07 §3) | pylon sections, arch, letter set (lit and unlit), mascots ×4, marquee board | |

## 12. Tests
- **`tools/markets/check_markets.py`** (GENERATOR):
  - **22 markets**, one per settlement;
  - the site is fully inside `limits`, with r in [0.60, 0.95] (villages: [0.5, 0.95]);
  - slope ≤ 0.04; dry;
  - no overlap with buildings, roads or other areas;
  - the connector meets a street;
  - the stall counts match §1.2, and permanent = 35 % ± 1 stall;
  - paved spaces ≥ 1.8 × stalls;
  - fire lanes: every stall ≤ 45 m from a 6 m lane;
  - tent slots ≥ 60 / 36 / 24 by tier;
  - the mooring ground and attachments match the tier.
- **`remake/tools/game_calendar_test.gd`:**
  - day 0 is Wednesday 2752-05-24;
  - `weekday`, `date` and month roll-overs are correct over 3 years;
  - NpcLife, NpcPlaces and TransitDemand agree with GameCalendar (no stray `posmod(day, 7)`: a grep check).
- **`remake/tools/flea_calendar_test.gd`** (headless):
  - over 730 days × 22 markets, weekend occupancy ≥ 0.80 every open day;
  - 35 % permanent;
  - rotating terms 8–16 weeks;
  - day vendors only on vacancies;
  - local stalls never open Mon–Thu;
  - modes as in §4.2;
  - purity: the same answers in two runs and in any query order.
- **`remake/tools/flea_sky_test.gd`** (WARM/DAYS env like `sky_drift_test.gd`), over 120 game days:
  - bookings honoured within a lap;
  - no stay over 21 days;
  - ≥ 60 % of islands leave after one weekend;
  - followers lash only to a moored raft;
  - rafts ≤ 10 everywhere; only the first 6 / 4 / 3 (city / town / village) anchored to the ground, the rest lashed;
  - fairs only at ≥ 3;
  - no island over a market floor;
  - crew of 24 per island;
  - on-ground islanders ≤ 25 % of each island's population;
  - islands moored somewhere on most weekends.
- **`flea_occasions_test.gd`:**
  - over 20 simulated years: Bright Weeks ≈ 20 a year (±30 %), Sky Holidays ≈ 1.8 a year (±50 %);
  - the CELEBRATION mode opens local booths every day;
  - HOLIDAY only at town and village tiers, at most 3 days in a row;
  - the holiday area matches the 8 km rule;
  - non-essential posts are closed there and essential ones are not;
  - fair attendance and transit multipliers apply.
- **`flea_trips_test.gd`:**
  - market_trip shares by age and money style;
  - the destination histogram follows the gravity weights (fairs pull ×2.5);
  - no trips on workdays;
  - trippers park in the destination's lot.
- **`flea_vendors_test.gd`:**
  - the vendor mix histograms differ from the town baseline in the expected directions;
  - Lowliners are over-represented, more in the South;
  - islanders fill exactly the vacant stalls.
- **`lowliner_stats_test.gd`:**
  - regional counts match canon `settled.by_region` ± 10 %;
  - hiring friction applies only where §9.4 says;
  - Line Rows households are Lowliner-majority with mixed families.
- **Perf (in game, DevBridge, `reference/tmp/mainthread.sh`):**
  - a city market at noon on a Saturday, a village market, AFTER_HOURS at night, and a 3-island city fair at dusk:
    targets as in §7, with a gate of ≥ 55 fps worst 1 s on the Deck build;
  - a walk through Solana Point's Line Rows at night.
- **Visual:** screenshots of approach, CREW_DOWN, ANCHOR, LOGISTICS, the first gondola, a fair at night, the lot at
  03:00, every market's pylon at night, and a Line Rows block.

## 13. Build plan (ordered; streams can overlap where noted)

**Phase A: data and pure model (no art; can start now)**
1. DATA/RUNTIME: `GameCalendar` reading `events.json` (Wednesday start). Route NpcLife, NpcPlaces and TransitDemand
   through it. Tell the Communicator Date & Time agent to use it. Rebake lives. Calendar test.
2. DATA: `goods.json`, the vendor categories, `market_styles.json` with the 22 names (07).
3. RUNTIME: `FleaCalendar` (modes, visits by tier), `FleaVendors` (tenants, pool, islander fill), and the
   `market_trip` stays. Tests (calendar, vendors, trips) work from the §1.2 stall counts, with no geometry.
4. DATA: canon done; add per-island `mooring_crew`, `market_goods`, `settled_origin_weight`. Lowliner population
   weights per region into the traits/households tools (heritage `lowliner`, placeholder ethnonym fields).

**Phase B: Grok sign sheets (credit-limited; another agent runs them)**
5. Run 08's 20 sheets: markets first, then the island families, then city businesses. `tools/signs/crop_sheets.py`
   → sign atlases.

**Phase C: generator (needs one full map regen, ~35 min plus re-bakes; after the current sky work lands)**
6. GENERATOR: `_market_pass` for all 22 (plus Calder's hook); records for sheds, gatehouses and masts; the `limits`
   polygon; terrain areas; flea_markets.json; check_markets.
7. GENERATOR: `_line_rows_pass` (South Sea cities, then the small southern clusters) → warrens_surface; lot rows;
   street_lamps kind 5 for all lots; festoon scheme 4; asphalt; road_furniture paints the market lots.
8. GENERATOR (warren stream, when free): `make_warren.py --surface` (format v4, civ per lot); `moorings` in
   make_islands; lattice reservations; regenerate.

**Phase D: kit (parallel to C)**
9. KIT: stalls, goods, sheds, lot pole, mooring mast, anchor block, tents, lanterns, logistics tent, gondola cabins,
   carriage, ground station; the sign kit using the atlases (07 §4).
10. KIT (warren stream): the five island mooring pieces with family trims; `kerb_frontage` and `block_end_step` for
    Line Rows.

**Phase E: runtime, markets**
11. `FleaMarkets` / `FleaMarket` (static, every town), hooks, lot parking, signs; perf pass 1 (city and village).
12. `FleaCrowd` with weekend trippers.

**Phase F: runtime, islands and Line Rows**
13. `SkyMooring` (bookings, steering, moored state by tier, the market knot); flea_sky_test.
14. `SkyRopeway`; riders; the player rides; perf pass 2.
15. Islander stalls, `FleaTents`, the fair, the Skein lights; perf pass 3 (the dusk fair).
16. Surface `SkyWarren` with a ground frame for Line Rows; occupancy manifests; regional attitude and hiring
    friction; Line Halls; the Low Lashing.

**Phase G: economy and ship**
17. Wallet, haggling, stall rental, fares, hauling (06).
18. Export build: verify load time and the pck size; story hooks to deck-ea.

## 14. The secondary economy, names and signage (summary; details in 06, 07, 08)
- **The secondary economy (06):**
  - The 22 flea markets plus the island bazaars are **the second economy**: haggled, reputation-driven and cash.
  - **Market wardens** keep it honest; **fair letters** carry credit; the Great Fairs rotate.
  - **Weekend trips** make the markets a ship-wide circuit, with the islands as the caravans.
  - Player loops: stalls, haggling, circuit trading, hauling, tours.
- **Names (07 §2), all 22:**
  - north_shore: The Ropewalk (Port Carrow), The Lobster Pot (Brightwater), The Tide Clock (Haven Point), The Net Loft
    (Tern Harbor);
  - northland: Brannock County Trade Days (Marlowe), The Book Barn (Fenwick), Four Corners Swap (Haskins Corner), The
    Water Tower (Loomis Grove), The Weathervane (Dunmore Crossing);
  - kettle_valley: Traders' Landing (Harrow Falls), The Boathouse Swap (Port Tamsin), The Regatta Swap (Victory Bay),
    Millwheel Market (Cedar Ford);
  - southland: Iron Wheel Trade Days (Kessler), The Red Granary (Bellhaven), Route 30 Swap Meet (Calder), The Tall
    Tamarack (Tamarack), Elevator Flea Days (Pruett);
  - south_shore: The Starlite Swap (Solana Point), The Carousel Swap (Oceanview), La Pulga Verde (Playa Verde), The
    Pelican Swap (Pelican Cove).
- **Sign style:** the north is stately and classic; the south laid-back and California; the river towns a gradient
  (t); the islands flashy and modern with each family's flair.
- **Grok sheets (08):** **20 images** in all (5 market, 9 island-family, 4 business, 2 spare for fixes). Every sheet
  is a 3x3 or 4x4 grid cropped into 256-px atlas cells.

## 15. Risks
0. **Line Rows (surface warrens)** extend the warren generator to ground blocks: a new format version, per-lot civs,
   frontages and street grading. They also replace real lots in four southern cities: household counts must hold, and
   regen churns the occupancy. Mitigation: its own RNG stream after `_market_pass`; keep each block's household
   count; the warren stream builds it after its current work; start with one block in Solana Point.
1. **Crowds and CPU at a fair.** The worst case is a dusk fair with ~500 islanders, shoppers and moving cabins. Calder
   is already CPU-bound by people and traffic. Mitigation: hard caps (§7.3), impostors, the market on the outskirts
   (no downtown traffic under it), early perf passes in phases D and E.
2. **The map regen.** Siting the market reshapes plans and needs a full world regen plus re-bakes (places, lives,
   rooms, lamps, far side). Mitigation: its own RNG stream after `_jobs_pass` (takes free land only); run it in one
   regen window with other generator work; `check_markets.py` before the bake.
3. **SkyDrift determinism and steering.** Free drift plus bookings could fight (missed ETAs, rafts towing into moored
   ones). Mitigation: bookings are targets that slip by a lap; the calendar stays pure; `flea_sky_test` runs 120 days.
4. **Canon and physics:**
   - Canon now has the Aloft coming down routinely (done). The 3-day lash is kept by the market knot, and the lights
     are electric (hydrogen: no flame).
   - Mooring takes ~1.6 MN of drag a balloon; that is why every market has anchor blocks and masts, and why there is
     a wind window.
5. **The calendar switch to Wednesday.** It shifts every NpcLife baseline by two weekdays (rebake lives). The
   Communicator Date & Time app must use the same source. Mitigation: GameCalendar reads `events.json`, and a grep
   test finds stray `posmod(day, 7)`.
6. **Representation.** A large minority with real friction in the South can slide into stereotype or into "they
   cause it". Mitigation:
   - §9.4 rules;
   - friction modelled from structural causes (housing queues, entry work, shares) and NPC attitudes, never as a group
     trait;
   - warm northern relations as a contrast;
   - ethnonym placeholders until the political work;
   - a sensitivity read before story content.
7. **File ownership.** The warren generator and kit are owned by other agents today. Mitigation: the island pieces and
   `moorings` are requests (§3.3, §8.2), scheduled after their work lands.
8. **Size.** The kit (tents, goods, gondolas, signs) adds to the pck (3.2 GB). Mitigation: shared atlas, ≤ 40 MB
   budget, LODs, data packing.
