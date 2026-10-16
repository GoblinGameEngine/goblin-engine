# Handoff: MARKETS-KIT (the flea-market 3D kit)

Kept current after every milestone. Nothing is committed (the coordinator commits). Last update: 2026-10-16.

## State
- [x] Kit core, local market, signs, islanders' tents, lights, ropeway, moorings: **151 pieces**, offline audit
  clean (check.py: 0 problems; the toolkit's kitmesh.py: 0 inconsistent, 0 inside-out, 0 non-manifold, 0 duplicate).
- [x] Island-side buildings in the WARREN kit (`pieces_moor.py`: 5 pieces), warren kit rebuilt, no other piece
  changed (pieces.json diffed against a backup in reference/tmp/markets_kit/warren_before/).
- [x] Notes for MARKETS-WORLD and the warren generator: requests.md K1-K4.
- [x] Contact sheets: research/flea_markets/img/kit_*.png (full, MID, and night for the lit sheets), each <= 400 KB.
- [ ] Not done: an in-game look (not needed so far; the game was not launched). Godot's import of the kit.glb's
  external atlas URIs (`../signs/markets.png`) is untested: the runtime sets its own materials anyway (K3).

## Files
- `remake/blender/markets/` -- pure Python on the warren kit's `geom.py` (the warren kit is built the same way);
  Blender only renders and imports (a glTF validity check by use):
  - `mk.py` core: slots and the 10 material groups, atlas cells (`cells()`, `card()`), helpers (sweep, catenary,
    bulbs, festoons, lathe (either profile direction), tori, rounded rects, prisms), the exporter, the registry;
  - `p_local.py` sheds, shutters, pitches, canopies, display furniture, goods clusters, lot pole, lot paint, kerbs;
  - `p_signs.py` 3 entrance arches, 22 market boards, 22 landmark mounts (+ the millwheel's wheel, Traders'
    Landing's lighthouse, the Starlite's marquee), the Island Fair board, the Skein banner;
  - `p_island.py` tents, tent furniture, lanterns, festoons, gondola cabins and door, carriage, drop cage, rope
    units, deadmen, masts and heads, ground station and its wheel;
  - `palettes.py`, `textsigns.py` (the kit's lettered boards: kit_text atlas), `build.py`, `check.py` (the audit),
    `render.py` (Blender sheet renderer), `sheets.py` (all contact sheets), `moor_preview.py`, `kit_table.py`.
- Output `godot_project/remake/markets/`: `kit.glb`, `kit_mid.glb`, `pieces.json`, `kit_text.png`,
  `kit_text_emit.png`, `kit_text.json`. (flea_markets.json and vendor_pool.json there are MARKETS-WORLD's.)
- Warren kit: `remake/blender/sky/warren_kit/pieces_moor.py` (new); `pieces_b2.py` (+1 import line); `build.py`
  (imports pieces_moor: SPECIAL frames, ANCHORS into pieces.json, hand-made MIDS). Rebuilt
  `godot_project/remake/sky/warrens/kit/kit.glb`, `kit_mid.glb`, `pieces.json` (407 pieces).

## Commands
```
P=~/.venvs/ssc-assets/bin/python
$P remake/blender/markets/textsigns.py          # once (fonts: reference/fonts via tools/signs/fetch_fonts.sh)
$P remake/blender/markets/build.py --previews   # ~40 s; previews in reference/tmp/markets_kit/
$P remake/blender/markets/check.py              # ~5 s -> reference/tmp/markets_kit/audit.txt (problems first)
$P tools/sky/warren/audit/kitmesh.py godot_project/remake/markets/kit.glb godot_project/remake/markets/kit_mid.glb
$P remake/blender/sky/warren_kit/build.py       # the warren kit (4.5 min) after pieces_moor.py changes
$P remake/blender/markets/moor_preview.py && $P remake/blender/markets/sheets.py [sheet ...]   # ~15 min, all sheets
$P remake/blender/markets/kit_table.py          # the piece table below
$P remake/blender/markets/moor_check.py         # clip / zfight / pass / topology on the warren mooring pieces
```

## Conventions (the contract is pieces.json; summary in requests.md K1-K3)
- Frame: Y up, metres, origin at the footprint centre on the ground, front +Z; cabins and the cage at their floor.
  Anchors `[x, y, z, yaw]`, yaw a right-handed turn about +Y (Godot's Basis(UP, yaw)).
- A glTF primitive per SLOT (`mk_<slot>`), COLOR_0 a grey shade; the runtime applies `palettes[key][variant][slot]`
  and merges by `slot_group` (solid, metal, canvas, glass, glow, emissive, 4 atlas groups): <= 10 draws a chunk.
- Collision: `frame` boxes only (clamped to the visible mesh at build), `ramps` quads (the station's ramps),
  `passes` (>= 2.2 m tall, proven empty), `walk` areas (>= 2.2 m head room proven).
- Night: emissive 2.0 HDR (bulbs, neon, lamp lenses, obstruction lights), glow <= 0.9 (lantern glass and paper,
  lightbox faces, the cabin's ceiling panels, lit counters and shelf edges), canvas 0.35 lobe (tents read through
  their cloth), atlas cards by their `_emit.png` masks; glow threshold 1.5. Backings and boards are never emissive.
- Clearances: canopies 2.25 m under the valance, bazaar pagodas 2.25 (scallops), event marquees 2.35 under the
  bunting, the cabin 2.42 to the ceiling (panels at 2.39), the cage 2.4, sheds 3.4, arches 4.35-4.8.

## Decisions (with reasons)
- Geometry in Python like the warren kit (not Blender modelling): same toon look (flat faces, palette shades),
  same flicker cure and MID helpers, deterministic rebuilds; Blender for renders.
- Signs: each landmark is a 3D structure carrying its atlas cells as cards (two-faced where seen from behind);
  cells that ARE the object (water tower lettering, open book pages, the shield) are mapped onto the 3D surfaces.
- Goods: 22 clusters of goods-atlas cards on trays and in crates (cheap, merge into one atlas draw).
- The village mooring tier gets a 12 m guyed post (`mooring_mast_village`) at the ring's centre (the brief asked
  for mast tiers; 00_plan gives villages no lattice mast).
- Festoon bulbs hang straight from the wire (8 tris a bulb, no leads): cheap emissive geometry.
- Warren moorings: the rim is the piece's -Z; the stations' berths sit on decks cantilevered 7.5 m over the void
  so the cabins can hang below the deck (no pit in the island's deck is needed).
- No Grok images were used: the forms are standard (pagodas, marquees, a 3S cabin, lattice masts) and the sign art
  already existed in the atlases.

## Audit rules (check.py, on tools/sky/warren/audit meshlib + rays)
- topology: no degenerate, duplicate, inconsistent or inside-out faces; no non-manifold edges (full and MID).
- zfight: no same-facing coplanar overlaps between parts (flicker.cure also runs at build).
- clip: no edge through a sheet (card, glass, cloth, a canopy face) or a soft part (glow, emissive, canvas, cards);
  solid-into-solid joints (a post in its plinth, a ring through its eye plate) are counted only (`joints`).
- bounds (declared footprint + 0.35 m; MID inside the full), passes, head room, frames inside the mesh, lit parts
  small or thin, tris within budget.
- kitmesh's ray-parity "inward" flag on 4-5 meshes is a false alarm: per closed part alone 0 inward faces, except
  the drop cage's welded deck-and-posts part (touching boxes share internal faces; volume positive, winding consistent).

## The pieces
(regenerate with kit_table.py)
| piece | group | tris | MID | budget | collide | what |
|---|---|---|---|---|---|---|
| `fm_shed_bay` | shed | 852 | 332 | 1500 | frame | one 3 m bay of a 12 m open-sided steel shed |
| `fm_shed_end_near` | shed | 84 | 60 | 300 | frame | the row's first end (no frame |
| `fm_shed_end_far` | shed | 168 | 120 | 500 | frame | the row's last end |
| `fm_shutter` | shed | 32 | 16 | 60 | frame | a roll shutter, down; the front is +z.  Roll it up by scaling y about the pivot (2.6 m |
| `fm_pitch_open` | stall | 250 | 136 | 320 | frame | a painted 3x3 m open pitch with a folding table (cloth), two crates and a stool; goods clusters at g0..g5; an  |
| `fm_pitch_table_long` | stall | 348 | 184 | 360 | frame | the clothing pitch: a 2.4 m table and a rolling rail of garments |
| `fm_canopy_3x3` | stall | 152 | 104 | 200 | frame | a pop-up canopy (the US 10 x 10 ft) |
| `fm_canopy_3x6` | stall | 220 | 148 | 300 | frame | a pop-up canopy (the US 10 x 20 ft) |
| `fm_table_folding` | display | 52 | 32 | 120 | frame | a bare 6 ft folding table (the islanders' tents and the sheds use it too) |
| `fm_shelf_unit` | display | 70 | = | 250 | frame | a 1.2 m four-shelf unit, open front (+z); goods clusters on g0..g3 (shelf tops) |
| `fm_shelf_low` | display | 60 | = | 200 | frame | a low three-shelf stand (a counter front) |
| `fm_crate_stack` | display | 156 | = | 200 | frame | three crates, two on the ground and one on top; goods inside at g0..g2 |
| `fm_rack_clothes` | display | 260 | 128 | 300 | frame | a rolling garment rail with seven garments |
| `fm_bin_produce` | display | 160 | 124 | 200 | frame | a tilted three-bin produce stand; produce clusters at g0..g2 |
| `fm_tarp_ground` | display | 50 | 2 | 60 | none | a blanket vendor's ground tarp (no collision: walk over it) |
| `fm_goods_household` | goods | 50 | = | 120 | none | goods: lamps, a tea set, plates, a vase (goods atlas cards; stand on a g* anchor) |
| `fm_goods_antiques` | goods | 50 | = | 120 | none | goods: a clock, a painting, a radio, a barometer (goods atlas cards; stand on a g* anchor) |
| `fm_goods_machines` | goods | 42 | = | 120 | none | goods: a sewing machine and a typewriter (goods atlas cards; stand on a g* anchor) |
| `fm_goods_books` | goods | 66 | = | 120 | none | goods: books and a box of records (goods atlas cards; stand on a g* anchor) |
| `fm_goods_maps` | goods | 42 | = | 120 | none | goods: charts and old books (goods atlas cards; stand on a g* anchor) |
| `fm_goods_tools` | goods | 62 | = | 120 | none | goods: a crate of tools (goods atlas cards; stand on a g* anchor) |
| `fm_goods_clothing` | goods | 46 | = | 120 | none | goods: sweaters, boots, a hat (goods atlas cards; stand on a g* anchor) |
| `fm_goods_toys` | goods | 46 | = | 120 | none | goods: a tin robot, a guitar, a kite (goods atlas cards; stand on a g* anchor) |
| `fm_goods_produce` | goods | 66 | = | 120 | none | goods: apples and bananas (goods atlas cards; stand on a g* anchor) |
| `fm_goods_eggs_honey` | goods | 46 | = | 120 | none | goods: eggs, honey, berries (goods atlas cards; stand on a g* anchor) |
| `fm_goods_plants` | goods | 42 | = | 120 | none | goods: a fern and cut flowers (goods atlas cards; stand on a g* anchor) |
| `fm_goods_quilts` | goods | 42 | = | 120 | none | goods: folded quilts (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_knit` | goods | 46 | = | 120 | none | goods: island knitwear, dyed yarn, sailcloth (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_rope` | goods | 42 | = | 120 | none | goods: rope coils and knotted cord (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_lights` | goods | 50 | = | 120 | none | goods: lanterns, a bell, beeswax candles (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_food` | goods | 50 | = | 120 | none | goods: cheese, sky honey, mead, pickles (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_smoked` | goods | 42 | = | 120 | none | goods: dried fish and a smoked ham (goods atlas cards; stand on a g* anchor) |
| `fm_goods_sky_wonders` | goods | 46 | = | 120 | none | goods |
| `fm_goods_sky_pets` | goods | 42 | = | 120 | none | goods: a dove cage and a lark fan (goods atlas cards; stand on a g* anchor) |
| `fm_goods_bicycle` | goods | 4 | = | 40 | none | a big goods card standing on the ground (beside a table) |
| `fm_goods_rocking_chair` | goods | 4 | = | 40 | none | a big goods card standing on the ground (beside a table) |
| `fm_goods_rolled_rug` | goods | 4 | = | 40 | none | a big goods card standing on the ground (beside a table) |
| `fm_lot_pole_1` | lot | 216 | 96 | 400 | frame | the 9 m lot pole (StreetLights lamp kind 5) with 1 LED shoebox head(s) on 0.85 m arms; its pier stands 0.6 m p |
| `fm_lot_pole_2` | lot | 264 | 132 | 400 | frame | the 9 m lot pole (StreetLights lamp kind 5) with 2 LED shoebox head(s) on 0.85 m arms; its pier stands 0.6 m p |
| `fm_lot_pole_4` | lot | 360 | 204 | 400 | frame | the 9 m lot pole (StreetLights lamp kind 5) with 4 LED shoebox head(s) on 0.85 m arms; its pier stands 0.6 m p |
| `fm_paint_bays_4` | lot | 40 | = | 100 | none | 4 double-loaded 90-degree bays (2.75 x 5.5 m) along x, nose line at z 0 |
| `fm_paint_bays_8` | lot | 76 | = | 100 | none | 8 double-loaded 90-degree bays (2.75 x 5.5 m) along x, nose line at z 0 |
| `fm_paint_bays_row_8` | lot | 18 | = | 60 | none | a single row of 8 bays (z 0..5.5 m; the aisle side at +z) |
| `fm_paint_arrow` | lot | 5 | = | 12 | none | a one-way arrow pointing +z |
| `fm_paint_crosswalk` | lot | 12 | = | 24 | none | a 3 m crossing (bars along z): tile along x |
| `fm_paint_fire_lane` | lot | 8 | = | 24 | none | a red fire-lane edge line with dash marks (3 m, tile along x) |
| `fm_paint_pitch` | lot | 10 | = | 40 | none | an open-air pitch outline (3 x 3 m) with its number plate at the aisle edge (+z) |
| `fm_kerb_3m` | lot | 14 | = | 24 | frame | a 150 mm concrete kerb, its face toward +z, 3 m (tile along x) |
| `fm_kerb_fire_3m` | lot | 14 | = | 24 | frame | the kerb painted red (fire lane) |
| `fm_kerb_corner` | lot | 40 | 22 | 60 | frame | a quarter-round kerb corner (radius 1.35-1.62 m about (-1.5, -1.5)) |
| `fm_wheel_stop` | lot | 10 | = | 16 | frame | a 1.8 m wheel stop (yellow paint slot) |
| `fm_lot_island_end` | lot | 73 | 45 | 120 | frame | the rounded end of a landscape island (kerb half ring + grass at 12 cm); a lot pole stands at `pole` |
| `fm_arch_timber` | sign | 560 | 100 | 900 | frame | NORTH entrance |
| `fm_arch_truss` | sign | 504 | 92 | 1200 | frame | RIVER entrance: brick piers and a steel box truss with bulbs; 11.9 m x 4.6 m clear |
| `fm_arch_googie` | sign | 264 | 60 | 900 | frame | SOUTH entrance |
| `fm_board_fm01_ropewalk` | sign | 4 | = | 8 | none | fm01_ropewalk's main cell as a two-faced board (1.6 m tall, centred on its anchor) |
| `fm_board_fm02_lobster_pot` | sign | 4 | = | 8 | none | fm02_lobster_pot's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm03_tide_clock` | sign | 4 | = | 8 | none | fm03_tide_clock's main cell as a two-faced board (1.6 m tall, centred on its anchor) |
| `fm_board_fm04_net_loft` | sign | 4 | = | 8 | none | fm04_net_loft's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm05_water_tower` | sign | 4 | = | 8 | none | fm05_water_tower's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm06_book_barn` | sign | 4 | = | 8 | none | fm06_book_barn's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm07_weathervane` | sign | 4 | = | 8 | none | fm07_weathervane's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm08_brannock_trade_days` | sign | 4 | = | 8 | none | fm08_brannock_trade_days's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm09_boathouse_swap` | sign | 4 | = | 8 | none | fm09_boathouse_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm10_four_corners_swap` | sign | 4 | = | 8 | none | fm10_four_corners_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm11_regatta_swap` | sign | 4 | = | 8 | none | fm11_regatta_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm12_millwheel_market` | sign | 4 | = | 8 | none | fm12_millwheel_market's main cell as a two-faced board (1.6 m tall, centred on its anchor) |
| `fm_board_fm13_traders_landing` | sign | 4 | = | 8 | none | fm13_traders_landing's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm14_iron_wheel` | sign | 4 | = | 8 | none | fm14_iron_wheel's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm15_red_granary` | sign | 4 | = | 8 | none | fm15_red_granary's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm16_tall_tamarack` | sign | 4 | = | 8 | none | fm16_tall_tamarack's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm17_elevator_flea_days` | sign | 4 | = | 8 | none | fm17_elevator_flea_days's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm18_route30_swap_meet` | sign | 4 | = | 8 | none | fm18_route30_swap_meet's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm19_la_pulga_verde` | sign | 4 | = | 8 | none | fm19_la_pulga_verde's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm20_starlite_swap` | sign | 4 | = | 8 | none | fm20_starlite_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm21_carousel_swap` | sign | 4 | = | 8 | none | fm21_carousel_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `fm_board_fm22_pelican_swap` | sign | 4 | = | 8 | none | fm22_pelican_swap's main cell as a two-faced board (2.4 m tall, centred on its anchor) |
| `sign_fm01_ropewalk` | sign | 1230 | 322 | 4500 | frame | a 12 m granite-and-timber pylon wrapped by a giant figure-eight rope with amber chase bulbs, the barn-red boar |
| `sign_fm02_lobster_pot` | sign | 996 | 380 | 3500 | frame | a giant slatted lobster trap on two granite posts, strung with buoys, a red lobster weathervane on top, the ov |
| `sign_fm03_tide_clock` | sign | 304 | 64 | 1800 | frame | a white clapboard tower (9 m + cap) with the giant one-handed tide clock both faces, a red lamp on top, the en |
| `sign_fm04_net_loft` | sign | 72 | 32 | 2000 | frame | the grey-shingled gable of an old net loft (5 m wide), the lettered gable cell on its front, a net with glass  |
| `sign_fm05_water_tower` | sign | 676 | 246 | 4000 | frame | the village water tower |
| `sign_fm06_book_barn` | sign | 298 | 230 | 2600 | frame | a white classic barn front (8 m) with green trim and double doors; the carved, gilded open book over the doors |
| `sign_fm07_weathervane` | sign | 206 | 102 | 1500 | frame | a tall post crowned by the copper bull weathervane (its cell, both faces) over a ball finial; the red auction  |
| `sign_fm08_brannock_trade_days` | sign | 368 | 248 | 3000 | frame | the county-fair arch |
| `sign_fm09_boathouse_swap` | sign | 94 | 78 | 2200 | frame | a green-and-white boathouse front with a striped awning over its doors, the boathouse cell (the neon 'Swap' sc |
| `sign_fm10_four_corners_swap` | sign | 186 | 122 | 1600 | frame | a white finger-post tree pointing to the other markets (eight arrow boards), the circuit board (its cell) on t |
| `sign_fm11_regatta_swap` | sign | 368 | 100 | 2200 | frame | a tall white racing-sail pylon |
| `sign_fm12_millwheel_market` | sign | 206 | = | 1800 | frame | the mill's timber frame and race for a 5 m waterwheel that really turns (sign_fm12_millwheel_market_wheel at ` |
| `sign_fm13_traders_landing` | sign | 316 | 92 | 5000 | frame | the bow of a lake freighter as the entrance arch |
| `sign_fm14_iron_wheel` | sign | 1342 | 374 | 5500 | frame | a 6 m locomotive driving wheel (tyre, 12 spokes with chase bulbs, counterweight, hub) on a Streamline Moderne  |
| `sign_fm15_red_granary` | sign | 246 | 30 | 1800 | frame | a red granary with its gable cell (the white sunburst and the Googie 'Red Granary' script) across the front, c |
| `sign_fm16_tall_tamarack` | sign | 846 | 298 | 4000 | frame | a 14 m fibreglass tamarack (tiered golden foliage over a trunk) wound with coloured bulbs, the 1950s boomerang |
| `sign_fm17_elevator_flea_days` | sign | 222 | 140 | 3000 | frame | the town's grain elevator |
| `sign_fm18_route30_swap_meet` | sign | 416 | 88 | 4000 | frame | a giant US 30 shield cabinet (its cell both faces, turquoise neon round it) on twin legs with a bulb starburst |
| `sign_fm19_la_pulga_verde` | sign | 124 | 88 | 3000 | frame | a stucco pier pylon under a mission-tile cap with the neon pier-and-palm cell both faces, a palm beside it |
| `sign_fm20_starlite_swap` | sign | 156 | 50 | 6000 | frame | the old 20 m drive-in screen tower |
| `sign_fm21_carousel_swap` | sign | 492 | 292 | 4000 | frame | a carousel canopy (16 candy-striped gores, scalloped valance, a bulb ring) on a striped centre pole, the giant |
| `sign_fm22_pelican_swap` | sign | 66 | = | 1500 | frame | the fibreglass pelican in a sun hat on its piling (its cell, both faces) on a sand plinth, beside the surfboar |
| `sign_fm12_millwheel_market_wheel` | sign | 1180 | 452 | 2400 | none | the Millwheel's turning wheel (5 m, 16 paddles edged with bulbs) |
| `sign_fm13_traders_landing_lighthouse` | sign | 626 | 326 | 1800 | frame | Traders' Landing's lighthouse pylon (12.4 m) |
| `sign_fm20_starlite_swap_marquee` | sign | 24 | = | 60 | frame | the Starlite's marquee board (the extra cell) on two legs; at sign_fm20's `marquee` |
| `fm_board_island_fair` | sign | 36 | = | 80 | frame | the lit ISLAND FAIR dot-matrix board on two legs (any market while islands are moored) |
| `fm_skein_banner` | sign | 28 | = | 60 | frame | the Skein banner (clan pennants and lanterns) strung on two posts across an entrance while an island is moored |
| `tent_bazaar_6` | tent | 1588 | 850 | 1800 | frame | the islanders' bazaar pagoda (6 x 6 m, eave 2.55, peak 5.6) |
| `tent_bazaar_6x12` | tent | 2324 | 1252 | 3000 | frame | two bazaar pagodas joined (6 x 12 m), one long kanat back wall, a 12 m open front with a post at the middle |
| `tent_shelf` | tent_furniture | 152 | 84 | 250 | frame | an island shelf: painted sides, lit shelf edges (glow), a carved crest; goods at g0..g3 |
| `tent_table` | tent_furniture | 132 | 68 | 140 | frame | a cloth-hung trading table |
| `tent_counter` | tent_furniture | 58 | 34 | 200 | frame | the lit counter: a glowing front panel |
| `tent_rail` | tent_furniture | 132 | 56 | 160 | frame | a hanging rail of rugs and a lantern, against a wall |
| `tent_ballast` | tent_furniture | 52 | 43 | 80 | frame | a water barrel and a sandbag: paved-lot tent ballast |
| `tent_event_9` | tent | 1454 | 540 | 2200 | frame | the event marquee (9 x 9 m, eave 2.75, ridge 4.75) |
| `tent_event_9x18` | tent | 2354 | 874 | 3800 | frame | the event marquee (9 x 18 m, eave 2.75, ridge 4.75) |
| `tent_logistics_office` | tent | 944 | 760 | 2000 | frame | the mooring crew's white frame tent (9 x 15 m) |
| `tent_logistics_weigh` | tent | 976 | 792 | 2000 | frame | the mooring crew's white frame tent (9 x 15 m) |
| `tent_logistics_crew` | tent | 944 | 760 | 2000 | frame | the mooring crew's white frame tent (9 x 15 m) |
| `tent_lantern_top` | tent | 3106 | 806 | 9000 | frame | the Lantern Top |
| `tent_canopy_striped` | tent | 480 | 208 | 600 | frame | a striped trading awning (6 x 3 m) for the tent ring |
| `skein_lantern_pierced` | light | 372 | 136 | 400 | none | a Skein lantern |
| `skein_lantern_fanous` | light | 236 | 116 | 400 | none | a Skein lantern |
| `skein_lantern_paper` | light | 158 | 126 | 400 | none | a Skein lantern: a round paper lantern; origin at its hook, hanging down (-y) |
| `skein_lantern_globe` | light | 162 | 114 | 400 | none | a Skein lantern: a glass globe on a brass collar; origin at its hook, hanging down (-y) |
| `skein_lantern_star` | light | 108 | 84 | 400 | none | a Skein lantern |
| `skein_lantern_bell` | light | 172 | 124 | 400 | none | a Skein lantern: a bell-shaped glass lantern; origin at its hook, hanging down (-y) |
| `festoon_warm_6` | light | 142 | 60 | 180 | none | a 6 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_skein_6` | light | 142 | 60 | 180 | none | a 6 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_warm_9` | light | 194 | 90 | 270 | none | a 9 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_skein_9` | light | 194 | 90 | 270 | none | a 9 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_warm_12` | light | 234 | 112 | 360 | none | a 12 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_skein_12` | light | 234 | 112 | 360 | none | a 12 m festoon string (6 % sag, a bulb every 0.6 m |
| `festoon_bulb` | light | 20 | = | 20 | none | one festoon bulb and its lead (MultiMesh it along the runtime's own catenaries |
| `festoon_pole` | light | 42 | 34 | 80 | frame | a 5 m pole for festoon strings across open aisles (hook at 4.6 m) |
| `gondola_cabin_pax` | ropeway | 1922 | 1178 | 3500 | frame | the passenger cabin (Peak 2 Peak class) |
| `gondola_cabin_door` | ropeway | 66 | 52 | 120 | frame | a cabin's sliding door leaf |
| `gondola_cabin_cargo` | ropeway | 232 | 180 | 2500 | frame | the cargo cabin |
| `gondola_carriage` | ropeway | 372 | 164 | 1200 | none | the carriage |
| `gondola_drop_cage` | ropeway | 942 | 372 | 2400 | frame | the crew's drop cage |
| `rope_track_unit` | rope | 12 | = | 12 | none | a track rope (60 mm) |
| `rope_haul_unit` | rope | 10 | = | 12 | none | the haul rope (46 mm) |
| `rope_hawser_unit` | rope | 12 | = | 12 | none | a mooring hawser (120 mm) |
| `rope_hoist_unit` | rope | 8 | = | 12 | none | a free hoist line |
| `rope_ribbon_unit` | rope | 2 | = | 2 | none | a 1 x 1 m ribbon along +x facing +z |
| `deadman_ring` | mooring | 102 | 70 | 200 | frame | a buried concrete deadman flush in the lawn (3 cm chamfered cap, its collision only the block) with its ring l |
| `deadman_ring_up` | mooring | 112 | 80 | 200 | frame | a buried concrete deadman flush in the lawn (3 cm chamfered cap, its collision only the block) with its ring s |
| `mooring_mast_city` | mooring | 3154 | 986 | 5000 | frame | the city mooring mast |
| `mooring_mast_head_city` | mooring | 246 | 174 | 600 | none | the city mast's turning head |
| `mooring_mast_town` | mooring | 2286 | 738 | 5000 | frame | the town mooring mast |
| `mooring_mast_head_town` | mooring | 246 | 174 | 600 | none | the town mast's turning head |
| `mooring_mast_village` | mooring | 202 | 170 | 800 | frame | the village mooring post |
| `ground_station` | ropeway | 1330 | = | 6000 | frame | the ground (bottom) station of an island's jig-back ropeway |
| `ground_station_wheel` | ropeway | 404 | 212 | 800 | none | the station's horizontal bull wheel (r 3.25 m) |

151 pieces, 46310 tris full, 22491 MID

Warren kit mooring pieces (tris full / MID): `moor_line_house` 662 / 490, `moor_station_pax` 2,600 / 1,500,
`moor_station_cargo` 2,316 / 1,296, `moor_drop_cage_davit` 284 / 172, `moor_signal_mast` 646 / 128. kitmesh: 0
non-manifold, inconsistent, inside-out or duplicate faces, full and MID; the market kit's clip / zfight / pass checks
on them (remake/blender/markets/moor_check.py): 0. bounds.py: only the intended -z overhangs over the void.

## Contact sheets (research/flea_markets/img/, each <= 400 KB, palette PNG)
`kit_local`, `kit_lot`, `kit_goods`, `kit_signs_a`, `kit_signs_b`, `kit_tents` (dressed), `kit_furniture`,
`kit_lights`, `kit_ropeway`, `kit_warren_moor` (from the rim side), each with `_mid`; the lit sheets also `_night`.
Freestyle draws the outline of each alpha-cut card's quad (a render artefact: no outlines in game).

## Next (if wanted)
- An in-game look at a dressed market at dusk (take reference/tmp/game.lock; kill only by own PID).
- More goods clusters as the goods atlas grows; per-family dressing presets for the warren mooring pieces.
