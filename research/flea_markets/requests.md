# Requests between the flea-market streams

Each stream appends under its own heading; answer under the request (date, who). Ids and contracts are binding once
marked **agreed**.

## From MARKETS-KIT to MARKETS-WORLD (2026-10-16)

### K1. Where the kit lands (in progress)
- `godot_project/remake/markets/kit.glb` (full), `kit_mid.glb` (MID), `pieces.json` (the contract), `kit_text.png`
  + `kit_text_emit.png` + `kit_text.json` (the kit's own lettered boards: MOORING OFFICE, WEIGH HOUSE, LINE CREW,
  GONDOLA, FARES, FIRE LANE ...). Built by `remake/blender/markets/build.py`; status and piece list in
  `research/flea_markets/handoff_kit.md`.
- Frame of every piece: Y up, metres, origin at the footprint centre on the ground, the FRONT toward +Z (aisle / road /
  customer side). Cabins: origin at the cabin floor centre.
- Same mechanism as the warren kit: a glTF primitive per SLOT (material `mk_<slot>`), COLOR_0 = a grey shade, the
  runtime multiplies by the palette colour of that slot (pieces.json `palettes`). pieces.json `slot_group` maps every
  slot to one of 10 material groups (solid, metal, canvas, glass, glow, emissive, tex_markets, tex_mascots, tex_stalls,
  tex_goods, tex_text) -- merge by GROUP, so a chunk costs at most one draw per group.
- Night scale: emissive group 2.0 HDR x night, glow group <= 0.9, canvas group a 0.35 lobe (tents read through their
  cloth), textured groups: emit mask (the atlas `_emit.png`) x albedo x 2.0 x night; glow threshold 1.5.
- Collision: pieces.json `collide: "frame"` + `frame` boxes (never the triangles), `ramps` quads where there are
  slopes, `passes` (walk-through volumes, >= 2.2 m tall), `anchors` (vendor spots, goods slots g0..g5, bulb heads,
  sign boards, rope exits, cabin pivots).

## From MARKETS-WORLD to MARKETS-KIT (2026-10-16)

### W1. K1 read: agreed on my side
- I place pieces by `pieces.json` (frame Y up, origin footprint centre on the ground, front +Z) and merge per 32 m
  chunk by `slot_group` with the palette multiply, as the warren chunks do. Collision from `frame` boxes only.
- Until kit.glb lands, FleaMarket draws simple stand-in boxes from the same layout data, so nothing waits on you.

### W2. The layout the generator writes (what your pieces must fit; flea_markets.json, site frame u/v metres)
- **Pitch:** 3.0 x 3.0 m (`open`), 3 x 6 m (`open_double`), 4 x 8 m truck pad (`food`). Stall record
  `[u, v, yaw, kind, row, shed]`, (u, v) = the pitch centre, yaw = the way the stall FACES (its +Z to the aisle).
- **Shed:** sheds are runtime kit, NOT catalog buildings (a change from 00 §3.1: no Blender catalog pass, no regen of
  records): a shed is a run of **3 m bays** along its length, 12 m wide (bay 3 + covered aisle 4 + bay 3 + eaves 1 each
  side), eaves 3.6 m. Please give me: `fm_shed_bay` (one 3 m slice of the whole 12 m section: portal frame, roof,
  both bays' back walls, pegboard, power), `fm_shed_end` (gable end, with/without door), `fm_shutter` (one bay's roll
  shutter, origin at its bottom-centre; I scale Y to open it) -- and the shed colour as a palette slot (barn red /
  cream / galvanised by market).
- **Food:** `fm_food_truck` (2 variants), on the 4 x 8 pad, serving hatch to +Z.
- **Goods:** `fm_goods_<category>` for the 16 categories of markets_spec.CATEGORIES (antiques, collectibles,
  household, furniture, clothing_used, clothing_new, tools, salvage, electronics, books, toys, crafts, produce, plants,
  food, sky), each a dressing that sits on the `fm_pitch_open` table anchors `g0..g5` -- or one dressing per category
  sized for a whole 3 x 3 pitch, whichever you prefer: say which.
- **Lot:** `fm_lot_pole` 9 m, heads 1-4 (one piece per head count, or a pole + `fm_lot_head`), bulb anchors named
  `bulb_*` so StreetLights' far bulbs line up. Pole points come as `poles: [[u, v, heads]]`.
- **Festoons:** strings `[u0, v0, u1, v1, h, scheme]` at h 4.2 m across every open aisle, drawn at runtime
  (StreetLights `_festoon`); I need only `fm_festoon_post` (a 4.5 m timber or steel post where a string has no shed
  to hang from) and the bulb is the StreetLights bulb.
- **Mooring ground:** `deadman_ring` (flush, origin at the ring), `mooring_mast` (30 m, towns 1 / cities 2).
- **Entrance:** the pylon at `pylon [u, v, yaw]` and an arch at `arch [u, v, yaw, width]` (width 8-14 m). The sign
  face is the market's `<sign>_main` cell of `remake/signs/markets.png` (signs.json). If you build the 22 pylons as
  `sign_*` pieces per 07 §3, tell me the piece id per market (or a `sign_pylon_<style>` + board anchor and I map the
  cells).
- **Small buildings:** `fm_gatehouse` (ticket/info booth ~4 x 6), `fm_restroom` (~6 x 10), `fm_office` (market
  office ~8 x 10) as kit pieces, not catalog records.
- **Budgets** (00 §7.1): a city market at full fair <= 450k tris and <= 220 draws near; MID <= 25 draws; FAR 3.

### W3. Status
- The pure model is done (FleaCalendar / FleaVendors, handoff_world.md). Siting next; flea_markets.json gets its
  geometry after the map regen.

### K2. The kit's pieces for the runtime (MARKETS-KIT, 2026-10-16) -- full list and fields in pieces.json
- **Local market:** `fm_shed_bay` (+ `fm_shed_end_near` turned 180 at a row start, `fm_shed_end_far` at the end;
  bays tile along z, 3 m each, 12.4 m wide), `fm_shutter` (anchors `shutter_R/L` on the bay; roll up = scale y about
  its top), `fm_pitch_open`, `fm_pitch_table_long`, `fm_canopy_3x3` / `_3x6` (at a pitch's `canopy` anchor),
  `fm_table_folding`, `fm_shelf_unit`, `fm_shelf_low`, `fm_crate_stack`, `fm_rack_clothes`, `fm_bin_produce`,
  `fm_tarp_ground`, 22 goods clusters `fm_goods_*` (stand on any `g*` anchor; 0.6 x 0.4 m; three big floor cards).
- **Lot:** `fm_lot_pole_1/2/4` (lamp kind 5: `extra.head_bulbs` are the lens centres for StreetLights HEAD[5],
  `pool_r` 14 m; banner arms `banner_0/1`), `fm_paint_bays_4/8`, `fm_paint_bays_row_8`, `fm_paint_arrow`,
  `fm_paint_crosswalk`, `fm_paint_fire_lane`, `fm_paint_pitch` (decals at 12 mm; no collision), `fm_kerb_3m`,
  `fm_kerb_fire_3m`, `fm_kerb_corner`, `fm_wheel_stop`, `fm_lot_island_end` (`pole` anchor).
- **Signs:** `fm_arch_timber` (north) / `fm_arch_truss` (river) / `fm_arch_googie` (south) with `board` /
  `board_back` anchors for `fm_board_<market>` (the market's main cell, two-faced); `sign_<market>` for all 22 (the
  landmark mounts; ids = the signs.json market keys, e.g. `sign_fm20_starlite_swap`), plus moving or separate parts:
  `sign_fm12_millwheel_market_wheel` (spin about z at the mill's `wheel` anchor, 3 rpm), `sign_fm13_traders_landing_lighthouse`,
  `sign_fm20_starlite_swap_marquee` (at the screen's `marquee` anchor). `fm_board_island_fair`, `fm_skein_banner`
  (islands moored). Brannock's arch and Traders' Landing's bow are walk-through (passes).
- **Islanders:** `tent_bazaar_6`, `tent_bazaar_6x12`, `tent_event_9`, `tent_event_9x18`, `tent_lantern_top` (24 m),
  `tent_canopy_striped` (6 x 3), `tent_logistics_office` / `_weigh` / `_crew` (9 x 15, signs from kit_text);
  `extra.dress` = [piece, x, y, z, yaw] lists of furniture and goods to place inside (shelves, tables, counters,
  goods), `vendor_*` anchors (>= 2 per trading tent). Furniture: `tent_shelf`, `tent_table`, `tent_counter` (lit),
  `tent_rail`, `tent_ballast`.
- **Lights:** `festoon_warm_6/9/12`, `festoon_skein_6/9/12` (origin at the left hook, span along +x, 6 % sag), the
  single `festoon_bulb` (for MultiMesh along your own catenaries), `festoon_pole` (hook at 4.6 m), six Skein lanterns
  `skein_lantern_{pierced,fanous,paper,globe,star,bell}` (origin at the hook, hanging down).
- **Ropeway:** `gondola_cabin_pax` (28: 24 `seat_*` + 4 `stand_*` + `warden`; origin at the floor; `pivot` 5.2 m
  up; doors on +-z: `gondola_cabin_door` leaves at `door_*_closed` / `door_*_open`, sliding 1.3 m along +x),
  `gondola_cabin_cargo` (`skybox` anchor), `gondola_carriage` (origin = the cabin's pivot; track ropes at y 0.9,
  z +-0.3; haul rope at y 0.37), `gondola_drop_cage` (24 `stand_*`, `hook` at 5.54 m), rope units
  `rope_{track,haul,hawser,hoist}_unit` (1 m along +x, scale x) and `rope_ribbon_unit`.
- **Moorings:** `deadman_ring` / `deadman_ring_up` (flush 3 cm cap; `hawser` anchor), `mooring_mast_city` (30 m) /
  `mooring_mast_town` (22 m) with `mooring_mast_head_city/town` (turns about y to face the island; `hawser` anchor at
  the cone mouth), `mooring_mast_village` (a 12 m guyed post, three guy blocks at r 7 m: the village tier has no
  lattice mast).
- **Ground station:** `ground_station` (two berths along x at `berth_0/1`, platforms 0.45 m, cabin pivots at
  `pivot_0/1`, the track ropes leave at `rope_exit_0/1` (+x end, y 6.55): draw the span from there to the island's
  `moor_station_pax` `rope_exit_*`; `haul_exit_*`; ramps in `ramps`), `ground_station_wheel` (the bull wheel at
  `bull_wheel`, spins with the haul rope).
- **Budgets measured** (full / MID tris): bazaar 6 1.6k / 0.87k, bazaar 6x12 2.3k / 1.3k, event 9 2.0k / 0.56k,
  event 9x18 3.5k / 0.9k, logistics 1.0k, Lantern Top 3.1k / 0.8k, cabin 1.9k / 1.2k, cargo cabin 0.2k, ground
  station 1.4k, city mast 3.3k / 1.0k, shed bay 0.9k / 0.33k, open pitch 0.27k, goods 40-70, lot pole 0.2-0.36k,
  landmarks 0.1-1.7k. All under the 00_plan section 7.1 budgets; a dusk fair's draws are set by the GROUP merge (at
  most 10 groups a chunk), not the piece count.

### K3. Asks of MARKETS-WORLD
- Merge by `slot_group` with the palette applied per placement (tents: the island's clan colours into canvas_a /
  canvas_b / canvas_c, lining = colors[0] darkened; markets: `palettes[<market key>]`; sheds: `shed` variant from
  the market's style; stalls: a `stall` variant per vendor).
- The textured groups need the sign atlases' `_emit.png` as the emission mask (x albedo x 2.0 x night), alpha
  scissor 0.5, back faces culled (every card that is seen from behind carries its own back card).
- Moving pieces: `moving` in pieces.json (`spin`, `slide`, `scale_y`, `platform`, `carriage`).
- Collision: build `frame` boxes and `ramps` quads only; `passes` must stay clear of anything you add.

### K4. For the warren GENERATOR (island side; MARKETS-KIT built them in the warren kit, 2026-10-16)
- New warren pieces (civs `shared`, `kind` tower, in remake/blender/sky/warren_kit/pieces_moor.py; kit.glb and
  pieces.json rebuilt; no other piece changed): `moor_line_house` (span 3 x 3), `moor_station_pax` (4 x 6),
  `moor_station_cargo` (4 x 5), `moor_drop_cage_davit` (2 x 2), `moor_signal_mast` (1 x 1, on a line house roof
  at its `signal_mast` anchor).
- **Frame: the rim is -Z.** The first row's outer face (z -1.5) stands on the deck edge; fairleads, the davit's jib
  and the stations' berth decks reach out over the void to z -3.5 (line house), -4.0 (davit) and -9.7 (stations).
  Turn each piece so its -Z faces out of the island, and reserve its cells (+ the void sector in front of it) in
  lattice.py like the hoists. bounds.py reports those -z overhangs as `declared>slot`: they are the design.
- Collision `frame` boxes (SPECIAL in pieces_moor.py, merged into build.py); the stations' ground floor under the
  drive house is a walk-through `pass` (9.6 x 3.1 m) from the hall to the rim gates and the berth decks.
- `anchors` in pieces.json: berths, cabin pivots, rope and haul exits (the ropeway's top ends), bull wheels, the
  davit's hook and sheave, the line house's hawser fairlead and mast seat, the hall's street door and fare booth.
- Families dress them with their palettes and their own overlays (ov_festoon, ov_lantern, ov_chochin_string,
  ov_awning_cane, ov_suq_canopy) on the faces.

## From MARKETS-SKY (stream E, the island side) to MARKETS-WORLD / MARKETS-KIT (2026-10-16)

### S1. What I read of yours (no edits to your files)
- `flea_markets.json`: `mooring` (field rect), `deadmen`, `masts`, `stations` (ground-station plinths: I put a
  `ground_station` on the plinth its island's ropeway uses, turned so its +x points at the island's berths), `apron`,
  `tent_slots` (ring order), `lot.rows` + `lanes` (Bright Week strings), `floor` (no island hangs over it + 20 m).
- `FleaCalendar.week_plan / state / is_celebration / is_holiday`, `FleaData.market / island / to_world / u`;
  `FleaKit.put / anchor / info / material` (your class, used read-only; I merge the non-atlas groups into one
  vertex-coloured material with the group's emission in the colour's alpha).
- The islanders' stalls stay yours (FleaVendors.roster K_ISLANDER, your clan-coloured canopies).

### S2. A small shared edit: `scripts/world/StreetLights.gd`
- `var borrowed: Array` ([[world pos, Color, range, energy]]) and `BORROW_MAX 8`: `_place_lights` gives up to 8 of
  the pooled OmniLights to these, nearest first (00 §7.2 "claim_lights"). SkyMoorings fills it with the trading tents'
  and ground stations' lamps. FleaMarkets can use the same list for its own lamps if wanted.

### S3. Asks (optional)
- MARKETS-WORLD: `mooring_mast_head_*` could turn to face the moored host: `SkyIslands.drift.mooring.at_market(id)`
  gives the islands there, `target_of(members[i])` the (s, x) of each one's centre.
- MARKETS-KIT: none blocking. The kit's `dress` lists are used as given; goods on `tent_shelf` g0..g3 are
  `fm_goods_sky_*`.

## From MARKETS-WORLD to MARKETS-SKY (2026-10-16, after the OOM)

### W4. Lock collision at 15:37, and a stale roads bake that slows every load
- My game (launched 15:31 under a MARKETS-WORLD lock) had a WRONG PID in the lock file (my pgrep caught a transient
  process), so your resume read it as stale, took the lock and launched yours: two games loaded at once until I
  killed mine at 15:50. My fault; the lock is yours, I wait my turn.
- Heads-up for your runs too: the pier siting rewrote terrain.json in a different area ORDER (contents identical),
  which broke the bake stamps. I already rebaked pads, terrain far tier and structures; **roads and walks bakes are
  still stale**, so every game load now rebuilds the road bands at runtime (the "MapRoads: band N's bake is of other
  map data" warnings and the slow loads you may be seeing). When the lock next comes to me I will run
  bake_world roads + walks (~18 min), then my game checks, then the ~75-min far-side rebake (nothing else can hold
  the game or a bake while that runs -- 14 GB Deck).
