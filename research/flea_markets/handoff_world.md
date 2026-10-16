# Handoff: MARKETS-WORLD (streams A pure model, B siting, D static market)

Kept current after every milestone (a usage limit can cut the session off). Nothing is committed: the coordinator
commits. Last update: 2026-10-16 ~18:00 (Resume 2 complete): A, B, D and ALL Round-2 extras done; far side rebaked
day + night and reimported; game lock released; FM-C far tile (f_16_06) eyeballed: the lot shows from afar.

## State
- [x] **A. pure model + tests: DONE, both tests PASS.**
- [x] **B. siting: 22 of 22 sited (Victory Bay = floating pier), check_markets 0 failures, all bakes fresh.**
- [x] **D. static market in game: kit pieces, signs, hours, vendors, shoppers, trips, lot parking; checked in game.**
- [x] **Round 2 extras: pier in game, kit trucks/office/gatehouse/restroom, Sky Holiday closures + holiday_fair +
  apron overflow, trippers, npc_life_test fixed and green, far-side day+night rebake.**

## A. What exists
| file | what |
|---|---|
| `tools/markets/markets_spec.py` | the 22 markets as numbers (00 §1.2): id `FM-<prefix>`, name, sign cell, tier, stalls, kinds, spaces, mooring tier, draw tags, Great Fair month. Run it to print the table (2,660 stalls). |
| `tools/markets/make_markets.py` | writes `godot_project/remake/markets/flea_markets.json`. `--spec-only` = no geometry (markets at the law centres, stalls by kind); `write(sites)` is for map_expanded. |
| `tools/markets/bake_vendor_pool.py` | `remake/markets/vendor_pool.json` (390 KB): per market a weighted sample of 8 x stalls townsfolk (21,280 people) from the lives JSON by the §2.3 weights; every person in ONE pool; small markets borrow within 8 km. Rerun after bake_lives or siting. |
| `godot_project/remake/scripts/markets/flea_data.gd` | `FleaData`: loads the markets + islands (bible); the shared integer hash `u(a,b,c,d)`; `to_world`, `centre`. |
| `.../flea_calendar.gd` | `FleaCalendar`: `week_plan(w)`, `visits`, `bookings_on`, `members_at`, `in_service`, `state(m, day, hour)` (modes CLOSED/LOCAL/ISLANDER/CELEBRATION/HOLIDAY; phases SETUP/OPEN/LANTERN/TEARDOWN/AFTER_HOURS; gondolas none/passenger/all), `is_celebration`, `is_holiday`, `market_open_day`, `holiday(day)` (8 km area). |
| `.../flea_vendors.gd` | `FleaVendors`: `local_roster`, `roster`, `tenant`, `occupancy`, `vending(pid, day)`, `islander_stalls`. |
| `godot_project/remake/tools/flea_calendar_test.gd` | 730 days x 22 markets. PASS: worst occupancy 0.809, mean 0.908; 35 % +-1; season terms 8-16 wk; no doubles; booths shut Mon-Thu; islanders fill every vacancy; modes; purity; vending(). ~22 s. |
| `godot_project/remake/tools/flea_occasions_test.gd` | 20 years. PASS: moorings/yr city 87.8 (85.6), town 105.8 (108.4), village 84.2 (84.5); rafts >=3/>=5 per tier within 30 %; Bright Weeks 19.1/yr (20); Sky Holidays 1.9/yr (1.8); holiday only towns/villages, <= 3 days; stays 62 % one weekend; none > 21 d; no island at two markets. ~2 s. |

## Decisions taken (deviations from or additions to 00_plan, with reasons)
1. **An island moors at most once in any 4 weeks** (phase hashed per island: 25 free a week). This makes the booking
   calendar pure per week (no island at two markets) without simulating history; supply (~10/week used) is ample.
2. **ATTRACT 12 km drift test skipped**: every island passes every s in ~3 days, and |dx| < 12 km almost always, so
   any free island qualifies. SkyDrift steering (stream E/F) honours the calendar.
3. **The market knot holds a raft of 5+ together** while it grows (nobody casts off before the last member's first
   weekend), so every raft of 5+ really has 5 in SERVICE at once (Bright Week). Smaller rafts meet within a weekend
   anyway (99.6 % of rafts of 3+ make a fair).
4. **Permanent tenants are FleaVendors draws, not NpcOccupancy posts**: posts are matched by occupation and nobody has
   occupation market_trader; weekend vending is a second activity. The pool excludes weekend workers.
5. **Islanders on Mon-Thu** hold the stalls empty on that week's Friday (pure; same stalls all week).
6. **Celebration** = >= 5 in SERVICE at 07:30 that day; **Holiday** = town/village, >= 7 at 06:00, first 3 days of a run.
7. Lowliner weighting is wired to `lineage == "lowliner"` / `name_heritage == "lowliner"`, which no person has yet
   (plan step 4, the traits stream).

## B. What exists (siting)
**Decision 8: no map_expanded rerun.** map_expanded `--game-data` rewrites `remake/inventory/map_inventory.json`, which
I must not touch, and plans/records don't need to change: markets take only free land. So the siting is a **post-pass on
the game data** (`tools/markets/site_markets.py`), a step of `tools/regen_world.sh` right after the import, idempotent
(it takes out its own areas/drives first). The regeneration is `regen_world.sh` (~35 min + bakes).
| file | what |
|---|---|
| `tools/markets/market_layout.py` | one market's plan in its site frame (u along frontage, v away from the road): landscape strip, lot (2.75 x 5.5 bays, 7.3 aisles, islands with poles every ~24 m), fire lane, food row + court, sheds (3 m bays both sides of a 4 m covered aisle, <= 120 m), open back-to-back rows with 6 m aisles and a cross lane every 54 m, doubles at row ends, festoons, side fire lanes, vendor lane, apron, mooring field (deadmen ring, masts, station plinths), tent slots (rings 0-2), entrances, pylon, arch, bus stop. 6 VARIANTS (field at side/back x core width 0.75/1/1.3). |
| `tools/markets/site_markets.py` | the search (40 m grid, 2 orientations, 6 variants, 2 m occupancy raster of roads' full ROW, rail, structures +3 m, areas, woods, water; same dry landmass as the heart; slope <= 4 % on natural ground; >= 250 m from schools/hospitals/childcare; a drive <= 260 m to a main/county road or <= 140 m to a town street). Writes terrain.json areas `parking` (lot record `type: market`), `market_floor`, `market_apron` x2, `mooring_field` (all tagged `market: id`) and the drive (a `street`, `market: id`), and flea_markets.json via make_markets.write. `--dry`, `--only Town,Town`. ~8 s. |
| `tools/markets/check_markets.py` | §12 checks. PASS for 21; FAIL FM-VBY not sited. `FM_PATH=` to check another file. |
| `tools/markets/render_sites.py` | plan views: `research/flea_markets/img/sites.jpg`, `--each` -> `img/site_<ID>.png`. |

**Decision 9: city limits = a superellipse (exponent 4) inscribed in the plan bounds**, not the ellipse: the four cities
fill their ellipses to the edge (render: `reference/tmp/markets_world/`), so with the ellipse Port Carrow had no site and
Solana Point only on its sea island. Whole site inside r <= 1.0, centre r in [0.60, 0.95] (villages 0.50).
`limits_sx` (48 points) is in each market's record (not yet in law/settlements.json: that file is make_law's).
**Victory Bay (The Regatta Swap): no free land** on its island (all estates). Options for the user: replace an estate
block; site it on the mainland at the Tamsin Bridge (Harrow Falls' limits); or a floating pier market (Regatta theme).
FleaData keeps it with `sited: false` (pure model works; no geometry).

Other B edits (all for the regen):
- `tools/parking_lots.py`: keeps `lot.type == market` areas (it deleted every lot area before re-making its own).
- `tools/street_lamps.py`: lamp **kind 5 lot pole** on every market pole AND every other lot (downtown, park & ride:
  unlit before); festoon **scheme 4** strings from flea_markets.json festoons. `StreetLights.gd`: HEAD[5] (9 m, 2 heads),
  post mesh 5, posts dict.
- `road_surface.gd`: `parking`, `market_floor`, `culdesac` areas are **asphalt** (checked before the land cover; a lot
  inside the built-up ground used to read "lawn", outside "dirt").
- `MapTerrainMesh.gd` AREA_TINT + `NavMap.gd` AREA_NAMES: market_floor / market_apron / mooring_field.
- `tools/regen_world.sh`: new steps site_markets (2), vendor_pool (after bake_lives), street_lamps + check_markets
  (after road_furniture).
- `export_presets.cfg`: `remake/markets/*.json` in all three include filters.

## D (started): schedule hooks, written before the regen so the rebake picks them up
- `make_places.py`: types `flea_stall` (purpose `flea` 0.35/wk, age >= 13; no posts) and `flea_office` (clerk 2,
  janitor 2, Fri-Sun); shells `stall`, `market_office`.
- `bake_places.py`: per sited market units `<FM-ID>/M` (flea_stall, door = walk entrance) and `<FM-ID>/O` (office),
  `market` field. `bake_paths.py`: markets attached where the drive meets the lot.
- `NpcPlaces.unit_open_on(uid, t, day)` (markets: FleaCalendar.market_open_day), `is_open` for flea_stall = state's
  local_open or islander_open.
- `NpcLife.stays`: `_flea()` before the errands: `vending` (FleaVendors.vending, 08:15-18:30 at `<id>/M`) or a
  `market_trip` (0.06 per market day, x1.5 retired/struggling, x0.5 no car, x2.5 toward a fair; gravity over the other
  markets; leave 08-11, 2-4 h). Errands use unit_open_on; `flea` visits x FleaCalendar.visit_boost (fair 2.5, Bright
  Week 2, holiday 3).
- `FleaCalendar.trip_weights(day)`, `visit_boost(m, day)`.
- `NpcTraffic._find_spot`: a destination door at a market -> the free lot bay nearest the entrance (`FleaLots`,
  new `remake/scripts/markets/flea_lots.gd`).

## D runtime
- `remake/scripts/markets/flea_kit.gd` `FleaKit`: loads MARKETS-KIT's kit.glb / kit_mid.glb + pieces.json, puts a
  piece (palette x shade vertex colour) into per-group arrays, one shared shader per group (night: emissive 2.0, glow
  0.9, canvas 0.35, textured atlas x emit mask x 2.0).
- `remake/scripts/markets/flea_markets.gd` `FleaMarkets` (added to `remake_station.gd` after StreetLights): builds a
  market within 900 m on a worker in 64 m chunks; kit pieces (fm_shed_bay + ends + boards, fm_shutter rolled by the
  roster, fm_pitch_open / fm_pitch_table_long + goods at g0-g2 + fm_canopy_3x3/3x6 in the vendor's or island's
  colours, fm_paint_pitch for empty pitches, the market's sign_<fmNN> pylon, fm_arch_* by band with its boards,
  mooring masts + heads, deadman_ring) to 260 m, the kit MIDs to 950 m; stand-in boxes when no kit (and for food
  trucks, office, gate house, restrooms: no kit pieces); frame-box colliders. Rebuilt when day / open state change.
  `vendor_spot`, `shopper_spot`, `stats()`.
- `npc_population.gd`: flea_stall is OUTDOORS; a market's unit indexed round its floor centre (7x7 cells), scanned
  once a round; its people = today's vendors + 400 hashed regulars; vendors stand behind their tables, shoppers browse
  stall to stall (`_flea_people`, `_flea_spot`).
- `npc_occupancy.gd town_of`: `FM-*` buildings -> the market's town.
- Test recipe: `reference/tmp/markets_world/mw_shot.sh MARKET DAY HOUR OUT [DIST]` (hold the game lock).

## Half-finished edits
- none (all parse; npc_traffic --check-only reports the usual autoload errors from StationPlayer/air_vehicle).

## Results (2026-10-16 afternoon): regen done, in-game checks done
- **regen_world.sh** ran end to end (10:54-12:45; check_markets now `--allow-unsited`). After it: check_markets 21 PASS
  + FM-VBY warned; flea_calendar_test PASS (worst 0.809, mean 0.908); flea_occasions_test PASS; flea_life_probe: Calder
  pool sample of 400 on a Friday -> 35 vending, 12 market trips, 14 flea errands; 4,499 Calder people have FM-C as
  their market; 42 market units in npc_place_index; 21 markets attached in npc_paths; 562 lot poles (kind 5) and 643
  market festoons in street_lamps.json; road_furniture painted 26 lots / 5,614 stall lines.
- **In game** (editor, Deck, vsync off; shots in `reference/tmp/markets_world/`):
  | where | when | result |
  |---|---|---|
  | Calder FM-C (town) | Fri 11:00 | LOCAL OPEN; 91 fps, 10.9 ms, GPU 10.0; flea 48 draws, 193k verts; 24 cars parked in the lot bays nearest the entrance; US 30 pylon + Ozzie, Googie arch, shed, canopied rows, vendors |
  | Calder | Fri 22:00 | lot lit by the poles (pools), sign glowing; 122 fps |
  | Solana Point FM-SOL (city) | Sat 12:00 | on the floor: 72.7 fps, 13.8 ms, GPU 10.2, 720 draws, 28 live (24 vendors, 4 shoppers); market geometry costs ~0.6 ms / ~40 draws (hidden vs shown); the frame is CPU-bound by people (population 4 ms, pop.space 3, animator 3) |
  | Loomis Grove FM-LG (village) | Sun 12:00 / Wed 12:00 | 108 fps; Sunday open (canopies, goods), Wednesday CLOSED (empty painted pitches, shutters down) |
  | Pruett FM-P | Wed (day 0) 11:00 | ISLANDER: only the 4 islander stalls out, in clan colours |
- **Fixed during the checks:** NpcPopulation let 60 people live (vendors' plans never end, so the old "despawn when the
  plan is done" never fired): now past MAX_LIVE the unwanted beyond 25 m go mid-plan; shoppers are spawned before
  vendors (distance x 0.6), 900 regulars looked at per round.
- **Not mine, seen in the log:** the island stream's untracked `remake/scripts/sky/sky_mooring*.gd` don't parse (type
  inference errors), which breaks SkyDrift / SkyIslands and reports remake_station.gd as "failed to compile depended
  scripts" on load (the station still ran). Tell that stream.
- `npc_life_test.gd` is stale (empty sample since lives are compact: division by zero, then the headless run hangs):
  pre-existing, not changed; use `remake/tools/flea_life_probe.gd`.

## Round 2 (the coordinator's list, 2026-10-16 afternoon) -- IN PROGRESS
Done (code and data; not yet run in game unless said):
- **npc_life_test.gd fixed:** samples one settlement's shard (`-- people [town]`, Calder by default), quits with FAIL
  on an empty sample, divisions guarded. (Not yet re-run: the lock was MARKETS-SKY's.)
- **Limits in law:** `tools/markets/write_limits.py` (called by site_markets) writes `limits` + `market` into
  law/settlements.json in place; `tools/law/make_law.py` keeps them on its own runs. 22 settlements written.
- **Sky Holiday closures:** FleaCalendar `holiday_list / holiday_at / holiday_near / essential` (ESSENTIAL_TYPES,
  ESSENTIAL_CATS); NpcPlaces.unit_open_on shuts non-essential units in the area; NpcLife.stays drops non-essential
  work and school there, adds `holiday_fair` (p 0.75, 2-6 h, 45 % in the evening; children 0.75, 3 h) and a 0.15
  trip toward a holiday within 25 km.
- **Apron overflow parking:** FleaLots.bays_on(id, day) adds apron_bays (grass, 2.75 x 5.5 double rows, clear of
  the tent slots) on fair days; NpcTraffic uses it.
- **Trippers visible at the destination:** bake_vendor_pool.py now bakes per market `trippers` (12 x stalls people
  from other towns who chose it by gravity), `trip_p`, `trip_shard`; FleaVendors.trip_of / trip_today /
  trippers_today; NpcLife's market_trip uses trip_today (so the person and the destination agree);
  NpcPopulation._flea_people adds today's trippers from loaded shards and one small (< 6 MB) neighbour shard;
  NpcLife.MAX_SHARDS 2 -> 3. (Trip model change: each adult has one usual out-of-town market.)
- **Kit pieces (remake/blender/markets/p_world.py, imported by build.py; palette "pier" in palettes.py; sheet
  "world"):** fm_food_truck_a/b, fm_office, fm_gatehouse, fm_restroom, fm_bike_rack, fm_pier_deck_3/6,
  fm_pier_rail_6, fm_pier_ramp (ramps quad collision), fm_pier_bollard. kit rebuilt (162 pieces); **check.py 0
  problems; kitmesh 0 non-manifold / 0 inconsistent / 0 inside-out**. Sheet: research/flea_markets/img/kit_world.png.
- **Victory Bay floating pier:** markets_spec PIER_TOWNS; `tools/markets/market_pier.py` (landing, 12 m gangway,
  26 m deck of four pitch columns on two aisles, a 30 m head with the mast and 8 bollards, a 30 m tent raft:
  50 stalls, 24 tents); site_markets `site_pier` (after the land search fails: a shore cell of the heart's land
  within 60 m of a street, 16 directions, every deck sample over open water 6 m clear of roads/docks/bridges/
  structures, inside the limits). Sited: landing 7 m from a street, deck at -10.88 m (landing -9.93).
  check_markets: 22 markets, 0 failures. bake_places / bake_paths rerun (FM-VBY attached).
- **FleaMarkets:** kit food trucks / office / gate house / restrooms replace the stand-ins; `_build_pier` (deck
  modules, edge rails but at joins and the gangway, the gangway scaled to the shore's rise, bike racks); bollards
  for the pier's anchor points; heights on the pier from `_pier_h`; ramp quads become ConcavePolygonShape3D; scaled
  pieces get orthonormal boxes. `FleaMarkets.deck_h(s, x)`; NpcPopulation._place stands people on the deck.

**Resume 2 (after the 14:21 OOM killed the session):** the far-side rebake died with NOTHING done (farside_cols
empty, remake/farside/ all Oct 14) -- restart it from scratch. The 12:57 npc_life_test background run used the OLD
script (0 people, division by zero): the fixed test (13:16) was never run. vendor_pool.json (13:18) and the fleet
(12:23) predate the pier siting (13:39): bake_lives -> vendor_pool -> make_vehicles still to run. bake_places /
bake_paths DID rerun (13:42-43). Stale game lock (sky's dead PID) cleared by sky's resume; MARKETS-WORLD holds the
lock now. Memory OK (10 GB available), nothing heavy running.

**Resume 2 progress:** import rerun (kit.glb 13:36 was newer than the 13:26 import); all 6 flea scripts + npc_life/
places parse clean (npc_population / npc_traffic --check-only still shows the usual autoload errors: Controls /
WeaponManager). Bakes rerun in order: **bake_lives** (214,356 people, 0 unplaced, 99 % staffed, 21 min),
**vendor_pool** (21,280 vendors in 22 pools, now with trippers), **make_vehicles** (140 types, problems: none),
**bake_transit**. Tests: **check_markets 22 markets 0 failures**; **flea_calendar_test PASS** (worst 0.809, mean
0.908); **flea_occasions_test PASS**; **npc_life_test (fixed) healthy**: 6,444 people in Calder's shard,
determinism 100/100, 0 out-of-order segments (vs the old 0-people division-by-zero); **flea_life_probe**: Calder
Friday 400-sample = 35 vending, 18 trips, 13 flea errands; roster 87 local + 3 islander. Found: the pier siting
rewrote terrain.json in a different AREA ORDER (content identical -- verified by set-compare against
terrain_before_pier.json), which broke three bake stamps seen in the last game log; **rebaked pads (62,934),
terrain far tier, structures (28 bands, same as the regen)**. The game load then showed **roads and walks bakes are
stale too** (MapRoads "band N's bake is of other map data", CoastalWalks likewise): rebake roads (~17 min) + walks
before anything heavy. Still open here: bake roads + walks, game checks (pier, Calder trucks/office, holiday),
far-side rebake.
**Resume 2 game checks (16:00-16:50), all PASS; shots in reference/tmp/markets_world/ (gcmd screenshot needs an
ABSOLUTE path -- a relative one is silently lost):**
- **FM-VBY pier** (Fri 11:00, LOCAL OPEN): deck over water at -10.88 m, gangway, edge rails, mast + guys, tent raft
  in clan colours, bollards, cars at the landing; 24 NPCs on/near the deck; 76-80 fps, flea ~30 draws / 243k verts
  (vby_fri11_high.png, vby_deck_close.png).
- **Calder FM-C kit buildings** (Fri 11:00): fm_office (awnings), fm_gatehouse, both fm_food_truck variants on the
  pads, Googie arch + boards, no stand-in boxes left; 89 fps (calder_arch_kit.png).
- **Sky Holiday** (FM-LG day 14, HOLIDAY OPEN; holiday_list finds d14-16 LG, d36-38 OCV): market ringed by islander
  tents + event tents (lg_holiday14_high.png); Loomis Grove units day 14: 91 of 105 SHUT, the 14 open all essential
  (town hall / post office / school shut); FleaLots bays 125 on the holiday vs 116 on a plain Friday (apron
  overflow); 215 of 301 LG people hold a holiday_fair stay (p 0.75).
- **Trippers**: FleaVendors.trippers_today('FM-C', 2) = 377, all out-of-town (B-xxxx etc.).
- Trees bake was stale too (same stamp break) -- rebaked. **All bakes now fresh** (pads, terrain far tier,
  structures, roads 24 bands, walks, trees): game4.log's only "of other data" warnings were the trees ones, fixed.
- **Far-side DAY rebake started ~16:55** (FarsideBake.tscn, log reference/tmp/markets_world/farside_bake.log,
  resume columns in user://farside_cols). After it: rerun tools/farside_night.py (~1-2 min) so the new market lot
  poles/festoons glow in the night images too.
**Lock collision 15:37:** my game's lock carried a wrong PID (pgrep caught a transient), MARKETS-SKY's resume read
it as stale, took the lock and launched its game beside mine; I killed mine at 15:50 (OOM risk) and wait for the
lock (requests.md W4). When taking the lock, verify the PID written is the game's (pgrep right after setsid is
unreliable: sleep first, then match the newest godot4 whose log file is ours).

Still to do in this round: NOTHING -- all done (see Resume 2 notes above and below).
- ~~with the lock: --import, --check-only, the flea tests, npc_life_test, flea_life_probe; bake_lives, vendor_pool,
  make_vehicles; a game check of the Victory Bay pier, Calder's trucks/office, a holiday day; the far-side
  rebake~~ ALL DONE (Resume 2, 2026-10-16 evening).
- **Far-side rebake DONE 17:49**: FARSIDE_BAKED 400 tiles (123 columns, 75.1 min, exit 0; the "finalize ... render
  thread" error at quit is the usual bake_world shutdown noise); then `tools/farside_night.py` rerun (400 night
  tiles, 2,859,799 lit px -- the market lot poles and festoons now glow from afar) and a headless reimport of the
  800 webps. The market lots show from a distance now.
- ~~the pier has no night lights yet~~ DONE (this note was stale): street_lamps.py writes the pier strings at
  ABS_H + deck_h + 4.2 and StreetLights._festoon decodes heights over ABS_H as absolute; street_lamps.json has the
  14 pier strings at 99993.32 (verified in the data; no night shot taken).

## Next step
- Stream E (the island side) takes over: SkyMooring / SkyRopeway / FleaTents use FleaCalendar.week_plan / members_at /
  state and FleaVendors.islander_stalls; tent slots and stations are in flea_markets.json.
- Mine, all CLOSED as of Resume 2 (2026-10-16 evening): Victory Bay sited as the floating pier (22/22 sited,
  check_markets 0 failures); kit food trucks / office / gatehouse / restroom in game; Sky Holiday closures +
  holiday_fair + apron overflow in game and probed; limits in law/settlements.json; trippers baked and visible;
  pier night strings baked (ABS_H); far-side day + night rebaked and reimported.
- Still open for the coordinator / later rounds:
  - `tools/pack_data.py` before an export (flea_markets.json + vendor_pool.json are in the export filter).
  - No night screenshot of the pier strings was taken (data + code verified only).
  - The sky stream's untracked sky_mooring*.gd parse errors (seen earlier) are theirs; moorings looked fine in
    today's FM-LG holiday shot.
  - Nothing committed: the coordinator commits (this stream's changed files: tools/markets/*, tools/street_lamps.py,
    tools/places/make_places.py, remake/scripts/markets/*, remake/characters/npc_*.gd, scripts/world/StreetLights.gd,
    remake/tools/npc_life_test.gd, remake/markets/*.json, law/settlements.json, remake/farside/*, baked/*).

## Commands
- Market table: `~/.venvs/ssc-assets/bin/python tools/markets/markets_spec.py`
- Site (dry): `~/.venvs/ssc-assets/bin/python tools/markets/site_markets.py --dry [--only Town]`; check:
  `tools/markets/check_markets.py [--allow-unsited]`; plans: `tools/markets/render_sites.py [--each]`
- Pools: `tools/markets/bake_vendor_pool.py`; whole chain: `tools/regen_world.sh` (steps 2, 16, 23, 24 are mine)
- Tests (hold the game lock): `../godot/godot4 --headless --path . --script res://remake/tools/flea_calendar_test.gd`,
  `flea_occasions_test.gd [-- years]`, `flea_life_probe.gd [-- Town]`
- In game: `reference/tmp/markets_world/mw_shot.sh FM-C 2 11.0 OUT [DIST]`, `mw_cam.sh FM-C u v h lu lv OUT.png`
