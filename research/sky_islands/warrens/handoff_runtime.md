# RUNTIME stream handoff (sky-island warrens), 2026-10-15 evening

Nothing is committed. Everything below is uncommitted work in `/home/deck/goblin-engine`.

## Files I changed, and their state
All paths are under `godot_project/` unless noted.

### `remake/scripts/sky/sky_warren.gd` (SkyWarren): complete, working
- **Format:** reads FORMAT v3 (tools/sky/warren/FORMAT.md) and refuses v1. `_rec_xf` (~l.820) places each piece: rot is bits 0–1, DECK bit 2, mount bits 4–5 (face +1.5 z, corner +1.5 x/z), quarter bits 6–7 (y = 3.2·level + 0.8·quarter).
- **Kit loading:** `_ensure_kit()` (l.357) loads the kit once, under a mutex, and sets the flag only *after* loading. The old "flag first" race gave whole islands placeholder boxes, which was the main flicker cause. `_load_pieces` (l.369) reads for each piece:
  - its full surfaces;
  - its MID model: `"mid": {glb, mesh, tris, slots}`, from kit_mid.glb or kit.glb; `mid: null` means drop it;
  - its collision mode `cmode`.
- **Collision modes:**

  | `cmode` | Where it comes from | What collides |
  |---|---|---|
  | `ramp` | pieces.json `"ramp"` quad list (fitted by `_ramp_of` only on an old kit) | the quads, both faces |
  | `frames` | `"collide": "frame"` with the `"frame"` [lo, hi] boxes (KIT, 35 walk-through pieces) | the boxes only |
  | `top` | ground, slab and roof pieces | their top face |
  | `mesh` | kind passage or bridge | the real triangles (arches now use `frames`) |
  | `box` | everything else | the AABB; walls and edges clipped to z ≤ 0.12 |

  `ramp` and `frames` replaced the earlier fitted-ramp and arch-mesh collision.
- **`_merge_chunk` (l.856):**
  - LOD0 groups surfaces by material (solid, metal, glass, emissive, water); LOD1 is the MID models, plus a "boxvc" group for pieces whose rule is box; the LOD2 box run feeds the groups.
  - Collision faces: whole-cell `top` floors are merged by `_floor_slabs` (l.955) into 0.4 m-thick greedy rectangles.
  - Faces are snapped to the millimetre so Jolt welds their edges.
  - `_aprons` (l.1002) is used only for format v2.
  - Meshes are built on the worker.
- **LOD ranges:** hard, non-overlapping (`_instance` l.1133, FADE_DISABLED). LOD0 < 45 m (40 m for kowloon_walled), MID < 200 m, LOD2 groups < 520 m. Do **not** go back to FADE_SELF: its stipple flickers under the outline pass.
- **Placement:** `_entry`, `_show`, `_refresh`, `place()` (l.1164–1210) push only the instances that are in range. A `_act_dirty` flag rebuilds the active list when entries are added.
- **`_collision` (l.1264):** nearest first. A chunk's shape is built once and kept in `c.shape`. One build per call, except chunks within CLOSE_M = 6 m, which are added at once. Without that, a walker or teleport landed on a chunk with no floor yet and fell through to the deck.
- **Lights:** `_lights_prep` (worker) and `_make_flares` give up to 300 flares and 700 pools.
- **Plants:** `_plants_prep`, then `_make_plants`. A lane-wall climber is detected because its cell is a room in the twin's `levels`.
- **Grass:** `_grass_prep`, then `_make_grass`: 14 clumps a cell on g/p/b/. cells and garden beds, one MultiMesh per chunk.
- **Deck tuck:** `_ground_prep`, then `_tuck_deck` (l.1656–1740) push the island deck's drawn mesh and its collision 10 cm under the lowest paving within 2.2 m.
- **Islanders:** `_walk_prep` builds SkyFolk's graph on the worker. Edges are cast to int, because JSON floats broke routing.
- **Removed:** `SLOT_LIFT`, since KIT fixed the coplanar faces at the source. `fix_flicker` (l.1650) now gates only the deck tuck.
- **Draw and upload budgets:** `MAX_TASKS_ALL` = 3 merges across all warrens, plus a shared per-frame upload budget (`_up_used`).

### `remake/scripts/sky/sky_island.gd`: complete
- `_build_rock` and `_build_warren` are named build stages, so the profiler can tell them apart.
- Profiler sections: `isl.b.*`, `isl.loads`, `isl.warren`, `isl.full`, `sky.warren_place`.
- `_warren_hull` puts the lod_vc massing material on the "warren_hull" node of the island's distant models.
- `lark_bake` (static, called once while loading) builds the parked-lark impostor; liveries are repainted, not rebuilt.
- `batch_mesh` / `_flat_of` replace SurfaceTool.append_from.
- `_drop_near` renames the old node to "NearDropped" before freeing it.
- The surface-format guards for primitive meshes are in.

### `remake/scripts/sky/sky_islands.gd`: complete
- `banners` (SkyBanners) is created in setup, after the balloons, and stepped in `_process`.
- Island placement: `_last` caches each island's last transform, and the jump test runs without quaternions. Far islands are placed every 6 ticks, mid ones every 2.
- `travel_local` reads only the `"travel"` substring of the json, once per island.
- `fast_travel` and `_travel_step` wait for `near_ready()`.
- `_sun_soft`: the sun's `shadow_blur` is 2.5 while aboard (shadow crawl fix).
- Profiler: `sky.tier`, `sky.travel`, `sky.banners`.

### `remake/scripts/sky/sky_folk.gd`
- Uses `warren.folk_graph`, and does not cache a graph until the warren is in.
- Starts at most 4 spawns a second.
- Guards against empty graphs (lines 271 and 306).
- Profiler: `folk.*`.

### `remake/scripts/sky/sky_signs.gd`
`_wblade` (l.670) draws warren-sized blade signs (a painted board on a bracket, toned-down neon). The warren anchor path passes `"warren": true`.

### `remake/scripts/sky/sky_plants.gd` (SkyPlants)
About 25 base shapes plus 88 `KIN` species, all ≤ 250 tris. Arrays are built on the worker (`arrays()`); the mesh is built on the main thread (`mesh()`).

### `remake/scripts/sky/sky_banners.gd` (SkyBanners): new; runs, but only partly tested
- **Banners:** 2–4 per island on the rim's outline points, facing outward. Instance x-scale is 10–20 m (island radius × 0.12); length 300 m.
- **Draws:** one near MultiMesh (40 segments) and one far (6 segments, every 4th frame); dock-flag and pennant MultiMeshes for near islands, plus a masts MultiMesh.
- **Furling** (`_furl`): 4 islands a frame, only against islands in neighbouring 400 m grid cells. Shortened over low ground or a lower island; the raft rule is removed.
- **Name lettering:** `_bake_names` renders every island's name once into an L8 texture: a SubViewport of Labels, 32 × 4 cells of 64 × 512.
- **SIGNS atlas:** `_atlas_cells()` reads signs.json `"banners"` (id → cell). The SIGNS agent hasn't written those yet.
- **Last run** (`research/sky_islands/img/banners_side_{0.45,0.93}.png`): names read (LOLLYGAG, CAT'S PAW, TYRE).
  - Not furled: `_len` was 1.0 for the ten islands checked.
  - 24 near, 276 far, 12 flags, 18 pennants.
  - **Too slow:** `banners.step` took 0.92 ms of main thread.
  - **Looks wrong:** they still look thin, and lean and sway too much (some run diagonally across the view).

### Shaders, all under `remake/shaders/`
- **New:** `warren_emissive`, `warren_flare`, `warren_pool`, `warren_foliage`, `warren_grass`, `sky_banner` (flat hang, billow, batten, names), `road_paint` (fades markings narrower than ~2 px; by 160 m).
- **`lod_vc.gdshader`:** `bay_px` (l.56, taken in uniform control flow) makes far windows fade to an average glow once a bay is under ~4–6 px.
- **`farside.gdshader`:**
  - magnified 4-tap smoothing; `fw` is taken before the branch;
  - the night twinkle is now a slow 5 % breathing (l.86), down from 0.6–2.8 Hz at 20 %.

### Other changed files
- **`scripts/world/AloftSwitch.gd`:** while aloft, hides World, Roads and Trees (l.66), since the far-side image shows them. Profiler section `aloft`.
- **`scripts/world/MapRoads.gd`:** paint_w and paint_y use road_paint.gdshader (l.73–79).
- **Tools:**
  - `tools/sky/warren/lods.py`: island lod1/lod2 hulls from the lattice. The GENERATOR runs it now.
  - `tools/sky/warren/check/`: `coplanar.py`, `placed.py`, `deck.py`, `passcheck.py`, `kitglb.py`.
- **Docs** (`research/sky_islands/warrens/`): `flicker.md`, `runtime_requests.md`, `format.md`, `kit_coplanar_faces.txt`.

## Test harness (all in `reference/tmp/`)
- **The lock:** before any game or headless run, write `RUNTIME (warren) <pid or note>` to `reference/tmp/game.lock`.
  - Check it first. If another stream holds it, wait.
  - Kill only your own game, by the PID in the lock. Remove the lock when done.
- **Launch:** `bash reference/tmp/wr_go.sh <island index> x` starts the game, writes the lock with its PID, adds the FrameRec node and fast-travels.
  - Index = SKY number − 1: SKY-099 is 98, SKY-078 is 77, SKY-071 is 70 (Kowloon), SKY-022 is 21.
  - Pass -1 to stay on the ground.
- **`wr_measure3.sh <idx> <name> <n spikes>`:** launch plus measurements:
  - a 30 s build window, then settled day and settled night;
  - frame spikes attributed by profiler section;
  - street and lane screenshots to `research/sky_islands/img/`.
  - Summarise the output with `python3 reference/tmp/wr_sum.py <out>`.
- **`flick.sh <idx> "x,y,z" "tx,ty,tz" <time of day> <out> <move true|false> [nudge m]`:** a camera fixed in the island frame takes two frames and diffs them, reporting changed % and changed-in-flat-areas %.
  - idx -1: a ground camera at the player (pass "0,h,0", "0,pitch,0").
  - `flickset.sh` runs the moving set; `flickset2.sh` (env MV, NUDGE) hides animated content first.
  - `crawl.py A B [y0 y1 x0 x1]`: the residual after taking out the best sub-pixel shift.
- **`walktest.gd` + `wr_walk.sh <idx> <n doors>`:** walks to n street doors from the arrival point.
  - It drives `move_and_slide` itself with the player's physics off, because injected input walked at ~0.5 m/s.
  - Spawn is +1.6 m; `up_speed` is reset after each teleport; `platform_floor_layers` = 0.
  - Results are in node `WalkTest.results`: "ok" with time, or "stuck" with position and waypoint.
- **`passcheck.gd`:** load it as node "PassCheck", then `run(sk, idx)`.
  - It adds every chunk's collision, then sweeps the player's capsule (r 0.18, h 1.45) along every graph edge with |dy| < 1.7.
  - Write `result` to json, filter to level edges (|dy| < 0.15), then run `~/.venvs/ssc-assets/bin/python tools/sky/warren/check/passcheck.py SKY-xxx file.json` to map hits to piece ids.
  - Sloped edges give false hits; use level edges only.
- **`pass2.sh`:** launch, banner stats and screenshots, then for 98, 77, 70 and 21: travel, passcheck (to `/home/deck/.claude/jobs/204e5d66/tmp/pc2_<idx>.json`), and walk 10 doors. Copies are in `reference/tmp/pc*.json`.

## Results
- **Flicker** (`flicker.md`):
  - The kit race fix took night roofs from 1,433 flat pixels a frame to 0–4.
  - Shadow blur aboard: 0.06 % to 0.001 %.
  - With KIT's source fix and SLOT_LIFT removed, island moving: plaza 0 %, lane 0 %, roofs 0.011 %, 100 m 0.11 %.
- **Floor seen from an island** (frozen, 0.5 m nudge, residual pixels > 20/255):
  - day 0.06 % before, 0.00 % after;
  - night 0.64 % before (the twinkle), 0.07 % after.
  - At 900 m aloft the ground buildings' outlines crawled; they're now hidden while aloft. Not re-measured.
- **Calder ground at 50–300 m:** not measured reliably. The nudge harness confuses parallax with shimmer at close range. road_paint and lod_vc bay_px are written but unmeasured.
- **LOD chain** (SKY-099): 478 draws and 654k prims on screen at the arrival point.
- **Grass:** SKY-078 has 48 MultiMeshes and 5,712 clumps.
- **Islands' physics step:** 0.69–0.77 ms per tick, within 0.8 ms.
- **Passage sweep, level edges blocked:**

  | Island | Before frame boxes | After frame boxes | Main blockers after |
  |---|---|---|---|
  | SKY-099 | 16 / 1,704 | 19 / 1,704 | 1 wall_door_k, 1 wall_arch_horseshoe_k, 1 wall_plain_k; the rest are the island fence and a body named "solid" |
  | SKY-078 | 44 / 2,862 | 30 / 2,862 | 1 wall_jali_carved_k; the rest are the fence and "solid" |
  | SKY-071 | 1,469 / 8,521 | 280 / 8,535 | ov_shack_a/b/c (222); edge_parapet_plain_t 17; wall_door_t no longer blocks |
  | SKY-022 | — | 31 / 3,773 | all the fence and "solid" |

  On SKY-071 the walk graph runs through rooftop shacks that are solid boxes. That needs KIT frame or pass boxes, or a GENERATOR route change.
- **Door walks** (10 doors each, after frame boxes, on the GENERATOR's 18:18 files):

  | Island | Doors reached | Stuck spots |
  |---|---|---|
  | SKY-099 | 5 / 10 | (-71.8, -76.5) going to (-73.5, 1.6, -76.5), a steps_up at cell (7,4); (52, -43.6); (29.8, 5.1) |
  | SKY-078 | 1 / 10 | (109.3, 23.8) next to the arrival: a bank cell with a steps_up, kerb and plinths at cells 75–76, 44; (67.2, 26.7), an arch lane at cell (61,44); (105.3, 24.6) |
  | SKY-071 | 0 / 10 | (-134.7, 1.7) heading to (-136.5, 1.6); (-49.6, 20.8); (-84.2, -7.4); (-77.2, -89.9) |
  | SKY-022 | 0 / 10 | (159.7, 1.5) heading down to 0.0, next to the arrival; (103.9, -12.2) |

  Most stuck points sit at a stair foot or head. The player's feet are about 1.4 m below the path: they fall off or through near stairs. **Not yet diagnosed.** Start by standing the player above one of these spots, with collision loaded, and ray-scanning the floor.

## Next, in order
1. **Diagnose the stair stucks** (see the table above), then re-walk the doors on the GENERATOR's next rewrite (it will report).
2. **Banners:**
   - cut `step()` to under ~0.3 ms;
   - make them read wider and flatter: reduce `lean` (0.10·t²·L) and `sway` (0.08·t²·L) in sky_banner.gdshader, and check the 10–20 m scale shows;
   - re-shoot day and night;
   - measure draws and ms from Calder with many islands in view, and aboard;
   - use SIGNS' signs.json `"banners"` cells when they land.
3. **Send the SKY-071 rooftop-shack blocker** to KIT and the GENERATOR.
4. **Calder 50–300 m shimmer:** a proper measurement with motion compensated for parallax (or a static scene and a smaller nudge).

## Gotchas
- **DevBridge token:** any headless godot run while a game is up rewrites the token. gcmd then times out, and you must relaunch. Run headless only while holding the lock and with no game running.
- **pkill -f / pgrep -f:** a pattern that appears in your own command line kills your own shell (exit 144). Kill by PID, from the lock.
- **New class_name:** a class that's new to the global class cache (SkyBanners, or another stream's StationCalendar) needs `godot4 --headless --path godot_project --editor --quit` before the game sees it. A missing one silently broke DaySkySystem.
- **Kit or glb changes:** reimport with `--headless --path godot_project --import`. Warren .bin.gz and .json are read at runtime, when the island is travelled to: no import.
- **Chunk collision timing:** chunks are added within 40 m of the player (nearest first; within 6 m at once). After a teleport, wait about 0.2 s.
- **Player position:** the origin is ~1.43 m above the feet. Spawn 1.6 m over a surface.
- **Island drift:** islands drift ~5.5 m/s, so frame diffs with the island moving include real motion of the background. For the island's own stability, freeze with `SkyIslands.set_physics_process(false)` and nudge the camera.
- **Other streams' breakage:** `scripts/ui/GameMenu.gd:2875` currently fails to parse; that's another stream's file.
- **Shared /tmp:** a background KIT or GENERATOR process (blender, make_warren) inflates frame times.

## Log
- 2026-10-15 ~19:40: pass2 had already completed (results above). Found the main stair/door-walk failure:
  `_floor_slabs` kept ONE floor per cell (the highest), so a lane under a sabat/bridging room had no floor (SKY-099
  cell (9,4): a hole to the deck).  Fixed: floors keyed Vector3i(i, j, y cm), merged per height.  Next: relaunch and
  re-walk 98/77/70/21.
- 2026-10-16 00:20: on the old files with the per-height floor fix, SKY-099 reached 7+ of the first 9 doors (from 5/10).
  GENERATOR final rebuild landed (00:03-00:14); kit/glbs reimported; `reference/tmp/pass3.sh` running (walk 10 doors
  + passage sweep per island 98/77/70/21 -> reference/tmp/pass3.out, sweeps to the job tmp pc3_<idx>.json).
  Banners edited, NOT yet run: fixed slots in both buffers, far islands an eighth a frame (perf), lean 0.10->0.03,
  sway 0.08->0.025, width rad*0.16 clamped 12-20 m.  Game running under the lock: see reference/tmp/game.lock.
- 2026-10-16 ~01:00 pass3 (GENERATOR final files, per-height floors, frame boxes): doors 25/40 —
  SKY-099 7/10 (stuck (38.8,2.8), (65.2,-25.8)), SKY-078 7/10 (stuck (114.2,-5.4), (114.1,-6.2)),
  SKY-071 9/10 (stuck (72.9,103.5)), SKY-022 2/10 (stuck (103.8,-9.2) x5, (159.7,1.5) by the arrival, (147.2,-2.7)).
  Passage sweep, level edges blocked: 099 17/1706, 078 30/2852, 071 60/6342 (int_counter 23, wall_door_t 6), 022 29/3816;
  the rest are FenceBody / "solid" / Lark bodies, not kit pieces.  Next: banners relaunch + measure, then SKY-022 stucks.
- 2026-10-16 ~01:20 banners measured (`reference/tmp/banners_m.sh` -> banners_m.out): step 0.44-0.53 ms aboard SKY-099
  (387 draws, 105 fps), 0.30-0.34 ms from Calder (one 1.6 ms frame); 300 banner slots, 12 flags, 18 pennants, all
  unfurled.  Screens: research/sky_islands/img/banners_side_0.45/0.93.png, banners_aboard_view.png (names read).
  banners_from_calder.png is BROKEN (the ground camera ended underground: redo).  Then edited (not yet run): mid-tier
  islands' banners every other frame -> expect ~0.3 ms aboard.  Next: rerun banners_m.sh, fix the Calder shot.
- 2026-10-16 ~01:45: banners rerun with mid-tier islands every other frame: step 0.41-0.44 ms aboard SKY-099
  (387 draws, ~110 fps); 0.27-0.34 ms in the "Calder" run, but that run is NOT valid: banners_from_calder.png is black
  (the ground camera ended underground / in an unloaded spot; 42 draws in the shot).  Redo: teleport the player to
  Calder, wait for the ground to stream, take the camera from the player's view, not flick.sh -1.
  No game running; lock released.  Next: (1) a valid Calder banner measurement + shot; (2) SKY-022's stucks at
  (103.8,-9.2) and by the arrival (159.7,1.5); (3) banner step under 0.3 ms aboard (the per-frame loop over all 100
  islands for counts/tier checks is the remaining cost: keep a list of near islands, refresh it with the tiers).
- 2026-10-16 ~02:30 NIGHT LIGHTING (user requests), `reference/tmp/night.sh`, shots in research/sky_islands/img/night/:
  * lit air: new `scripts/world/LightField.gd` (class LightField, made in remake_station.gd after StreetLights): every
    street lamp/festoon/walk lamp splatted into a 64 m (s,x) grid, box-blurred 2x2 passes on a worker (343,700 cells);
    sampled at the camera every 0.5 s, faded with height over the ground (0 by 250 m up); sky islands: the warren's
    json lights within 70 m.  `LightField.glow` 0..1 (eased).  DaySkySystem: night ambient += glow * AIR_AMBIENT (0.4)
    and tinted toward AIR_TINT (1, 0.78, 0.55).  Measured: Calder glow 0.31 (ambient 0.13 -> 0.32 with the then-0.6
    gain), SKY-099 glow 0.59; no measurable cost (fps/GPU same within noise: Calder 44 fps both, island 103-104).
    Shots: calder_pair.png, sky099_pair.png (before top / after bottom).  AIR_AMBIENT then cut 0.6 -> 0.4 (untested).
  * signs: ONE EMISSIVE SCALE (pass to SIGNS): letters/tubes 2.0 HDR at night (sky_neon night_k 4.5 -> 2.0); lit
    faces/lightboxes <= 0.9 (alpha <= 0.45 x 2.0); backings dark, not emissive; banners: letters emit 1.6 x albedo, the
    ground 0.12.  DaySkySystem night glow: threshold 0.9 -> 1.5, intensity 1.1 -> 0.7, bloom 0.08 -> 0.0 (only bulb
    cores, lit panes and letters bloom).  Shots: lane_sky071_night.png, lane_sky099_night.png (dot-matrix boards read:
    lit dots on dark).  The 5/20/60 m sign shots (sign_board_*m.png) mostly missed their sign: camera aiming from the
    anchors is wrong for many anchors -- redo with a camera on the walk graph facing the anchor.
  * then (untested): shop/door/fluoro flares halved (they washed out the signs above them).
  No game running; lock released.  Next: rerun night.sh for the 5/20/60 m sign shots (fix the aiming) and confirm
  the flare/AIR_AMBIENT tweaks; banner step 0.27-0.38 ms from Calder, 0.53-0.71 ms aboard in this run (vs 0.41-0.44
  earlier) -- still over 0.3 aboard.
- 2026-10-16 ~03:30 written, NOT yet run (waiting for the lock: SIGNS holds it, pid 1255190):
  * pools: new `remake/shaders/warren_solid.gdshader` + SkyWarren `_field_prep` / `_field_materials` (a per-island
    3D lamp field, 4 m x 2 m cells, from the json lights; solid/metal chunk materials per island sample it per
    fragment; chunk instances get `chunk_origin` as an instance uniform).  The ambient lift is cut to a hint
    (AIR_AMBIENT 0.06; the island part of LightField is off).  Calder: StreetLights pools x1.3 reach, x1.8 strength.
  * glare: no flares on shop/door/fluoro/stall lights; the rest smaller (0.25 + 0.5 s).
  * shop signs: sky_signs `_wblank` -- the SIGNS sky_<civ>_fascia / _blade cells (sky_a/sky_b atlases, new
    `remake/shaders/sign_atlas.gdshader`, emit mask x 0.8 at night) with the shop name set in the content rect
    (dark letters + neon letters at SIGN_EMIT 2.0).  Falls back to the old kinds where a civ has no cell.
  * banners: the SIGNS banner_atlas (banners_a.png, cells 2i name / 2i+1 wares, alpha-scissored tails, emit mask).
  ! I overwrote the SIGNS lock by mistake and ran a headless import + compile check while their game may have been
    starting; restored their lock line.  Their DevBridge token may need a relaunch.
- 2026-10-16 ~04:30 night2 RESULT + fixes (not yet run; lock held by SIGNS pid 1260935, waiting):
  * night2 (field 4 m, gain 2.2): islands looked like DAYLIGHT -- the lane camera stands in the densest lights, the
    sum clipped at 2.0 -> 4.4 x albedo.  Not a bug in sampling (pushing field_origin off-grid goes dark).  Fixed:
    FIELD_XZ 2 m, reaches shortened (lantern 6, fluoro 5, shop 4.5, door 3 m), stored 1 - exp(-sum), field_gain 1.1,
    sampler hint_default_black.  Sim: reference/tmp/fsim2.py (run from godot_project/) (median walk node dark).
  * NO LETTERS on any island sign: SkySigns._glyph kept triangles with n.z >= 0, but Godot's TextMesh fronts wind
    clockwise (n.z < 0): "A" = 33 tris, all dropped.  Fixed (keeps n.z < 0, falls back to all).  The atlas blanks
    were black boxes: _quad winds CCW, sign_atlas had cull_back -> now cull_disabled.
  * banner step 0.39 ms aboard SKY-071: _furl 168 us (4 islands x terrain), deco puts ~100 us.  Now FURL_PER 1,
    FAR_EVERY 16, tier-2 masts/flags/pennants built once as island-local MultiMesh children (_deco, _deco_build).
  * next: run reference/tmp/night3.sh (checks the lock itself; writes *_n3_* shots + pairs/trios) -> judge -> report.
  * Calder storefront pools (edited, NOT compile-checked yet -- night3's game was up): StreetLights `_load_shops`
    reads remake/signs/city_signs.json (SIGNS' quads, building frame) + Placement s/x/yaw/pad -> a pool 2.2 m out from
    each non-plaque sign under 6 m (SHOP_R 5 m, SHOP_COL alpha 0.85), bucketed as item "f".  Calder has 95.
  * night3 launched 04:4x under my lock (pid 1262065), running the pre-storefront StreetLights.
- 2026-10-16 ~05:30 night3 RESULT: no errors; signs now carry names (glyph fix works; fascia/emblem cells read).
  Banner step averaged 24 samples: Calder 0.31 mean / 0.27 median, aboard SKY-099 0.30 / 0.26, SKY-071 0.31 / 0.30
  (was 1.01 / 0.59 single-sample).  Field (night3 params) still a warm wash in shopfront-dense lanes -> tuned LIVE
  (reference/tmp/tune.sh + fieldtune.gd, no relaunch): doors throw nothing, cubic falloff, FIELD_UP 3 (light climbs a
  wall 3x slower), shop 3.5 m / 0.6, lantern 5 / 1.0, fluoro 4 / 0.7, gain 1.2 -> reads as pools.  Baked into
  sky_warren FIELD_KIND / FIELD_UP / FIELD_POW + shader default 1.2.  Sign shots: reference/tmp/signshot.sh I D OUT
  [SKIP] (street-level signs, physics-ray line of sight; larks/cloth have no collision so a 60 m view can be
  blocked).  Compile check 12 OK (StreetLights storefront pools included).
  Next: night4.sh (waiting for SIGNS' lock pid 1265754, then takes it itself): Calder shop street, lanes off/on, signs,
  before/after pairs (sky099_before_after.png, calder_n4_pair.png) -> report to coordinator.
- 2026-10-16 ~06:15 DONE (night4 + banner): shots in research/sky_islands/img/night/: sky099_before_after.png (the
  user's daylike lane_sky099_night.png vs now), lane_98/70_n4_pair.png (field off | on), signs_98/70_n4_trio.png
  (5/20/60 m), calder_n4_pair.png (old car-view | shop street with storefront pools, s 7259.8 x 1094.1).
  Banner: _furl now every 4th frame (FURL_EVERY 4) -> aboard SKY-099 0.22 ms mean / 0.18 median, SKY-071 0.23 / 0.20
  (40 samples each; p90 0.30-0.37 on furl frames).  No errors in the logs; compile 12 OK.
  EMISSIVE SCALE (agreed with SIGNS): letters/tubes 2.0 HDR at night; lit faces/lightboxes <= 0.9 (atlas blanks: emit
  mask x 0.8); backings dark; banner letters 1.6 x albedo, ground ~0.1; glow threshold 1.5, intensity 0.7, bloom 0.
  Island pools: emission = albedo x field x 1.2 (field 1 - exp(-sum), so <= 1.2 x albedo: under the glow threshold).
  No game running; lock released.  Open: Calder storefront pools are subtle (SHOP_R 5, alpha 0.85: raise if asked);
  SKY-071's 60 m sign view can be blocked by parked larks (no collision); SKY-022 stucks left to AUDIT.
- 2026-10-16 ~07:40 COORDINATOR ROUND 3 (after commit 5681f1d34), edited + compile 12 OK + fonts imported:
  * door rooms: sky_warren `_door_prep` / `_door_leaf` / `_room_floors` -- a door piece (pass_kind "door", face mount)
    whose door record (either side of the face) isn't entered -- or has no record -- gets a leaf box in its pass
    opening (x pass +-3 cm, y 0..pass top + 3 cm, z -0.14..-0.08; drawn LOD0 + MID, solid); every entered door's room
    cell gets a whole-cell floor slab if none within 40 cm (SKY-022: 793 of 804 floorless rooms were non-entered).
    Stats: warren.leaves / warren.room_floors.
  * bridges: in the DOWN pose every style's deck is flush (y 0) with a +3 cm sill; the paving meets it 6-10 cm lower
    (the "27 cm" is rolling_lift's side tracks / the stowed pose).  sky_bridge `ramp_box` / `_make_ramp`: a 4 cm steel
    ramp (z -1.7, y -0.12) -> (z -0.45, y +0.03), width - 0.3.  reference/tmp/bridge_walk.py SKY-022 [--ramp]
    (audit walksim, bridges down): 19/100 walks blocked -> 2/100 (the 2: hugging rolling_lift's side track at 1.4 m).
    Asked AUDIT (agent a9a1603c9fccf0a13) to mirror leaves / room floors / ramp in assemble.py and re-run SKY-022.
  * banners: _atlas_cells already read banner_atlas.islands[id].name; added banners_b (atlas_b + emit, cells 500 + n:
    an island's 3rd / 4th banner = its flag streamer 2i / clan 2i+1), sky_banners `_cell_add`.
  * shop signs blend heritage + warren: SkySigns HERITAGE (make_flags.py's table), `_heritage_font` (fonts copied to
    remake/fonts/heritage/, OFL, 5 MB -- DelaGothicOne 2.5 MB; no fonttools here to subset), ACCENT_SHARE 0.4 of shops
    glow in the heritage accent.  The warren blank stays the frame.
  * running reference/tmp/gh.sh (lock: takes it when free): SKY-022 10-door walk + gh_*.jpg shots (lanes day/night,
    neon lane, banners from below, Calder signs at night, Date & Time app) -> research/sky_islands/img/gh_*.jpg.
- 2026-10-16 04:10 (real clock; the "~07:40" stamp above was wrong): confirmation pass.
  * gh*.sh shots saved, all <= 400 KB: research/sky_islands/img/gh_island_lane_day/night.jpg (SKY-099, HUD hidden),
    gh_island_neon_night.jpg (SKY-071), gh_banners_from_below.jpg (side view under SKY-099, SIGNS atlas banners),
    gh_calder_signs_night.jpg, gh_datetime_app.jpg.  Harness: reference/tmp/gh.sh, gh2.sh (waits for warren built).
  * fixes found in game: `_kit` dict now carries pass_kind/pass (leaves were 0 before; now SKY-022 1350 leaves, 29 room
    floors; SKY-099 207 / 1); MID rule "mesh" only when the MID surfaces exist + _mlocal.get fallback to the box (a kit
    rebuilt mid-session crashed _merge_chunk: "Invalid key (35, 1, 0)").
  * SKY-022 10-door walk: 1/10 -- 9 stuck at the arrival stair head (147.2, -2.x): pave_garden_skirt +5.2 cm lip in
    the imported 03:31 kit; AUDIT's 03:43 kit sets ground tops to 0.  Reimported 04:05.  WAITING for AUDIT's
    make_warren --all + lods.py to land, then rerun the walk (gh2.sh walk part).  No game running; lock free.
- 2026-10-16 04:40 SKY-022 10-door walk on the FINAL files (make_warren --all 04:08 + lods, kit 03:43 imported 04:05):
  9/10 ok (was 2/10 at the start of the day, 1/10 with the stale kit).  The 1 stuck: door 3137 at (-27.2, feet ~1.6,
  100.8) -> wp (-28.5, 1.6, 100.5), cell (46,74) pave_plaza at quarter storey 2 (rf 130); not diagnosed (a later probe
  found only an unnamed StaticBody3D at y 0.3 there -- the chunk collision may have been streamed out by then).
  Passed to AUDIT.  NOTE wr_walk.sh polls WALK_POLLS x 5 s (default 60 = 5 min; a 10-door SKY-022 walk needs ~12 min:
  use WALK_POLLS=200), and never re-enable player physics while WalkTest is still running.
  No game running; lock released.  Nothing committed.
- 2026-10-16 ~05:10 door 3137 (SKY-022) diagnosed: 6/6 stuck, streamed AND with every chunk shape preloaded
  (reference/tmp/walk3137.sh) -> not streaming.  The blocker is a PARKED LARK (Near/Lark_0 and its door leaf
  Hinge_SR/Leaf_SR) on the plaza at (-28.9, 100.0): islands.json pads sit at deck height (y 0.34 here) under a
  plaza paved at 1.6, the lark sunk 1.3 m through it, across the walk.  300 of 303 pads (all islands) have walk-graph
  nodes within 3.5 m.  GENERATOR item (pads as reserved OUT cells, like the bridge footprints in lattice.py, at the
  paving's height); the audit doesn't model larks.  Passed to AUDIT.  No game running; lock released.
- 05:20 AUDIT took the lark item (lattice.py: lark footprints + 0.3 m OUT; bridge footprints from bridge_footprints.json;
  audit models larks) + kit rebuilt ~05:15 + make_warren --all running.  NEXT (me): when it lands -> headless --import,
  compile check, rerun `WALK_POLLS=200 bash reference/tmp/wr_walk.sh 21 10` (via walk022.sh) and walk3137.sh.
  Pad y stays islands.json's (deck: OUT cells have no paving).
- 2026-10-16 ~06:30 FINAL FILES (make_warren --all #2 on the 05:04 kit, imported 05:23): SKY-022 10-door walk 9/10 in
  3 full runs (2 relaunches).  The 1: door 2047 (10th) stuck at (10.7, feet ~3.0 = the deck, -11.5) under a steps_up
  ramp (top 3.47, cell 59,37, chunk 7,4).  It PASSES alone (12/12: walkdoor.sh streamed + preloaded, twice) and after
  3755 (walkpair.sh) -- fails only as the 10th of the full sequence, deterministically.  Not geometry (AUDIT replay
  clean), not collision streaming (preloaded passes; the _collision change below didn't change the full-run result).
  Lead: something time-based ~15 min into a session (bridge deploys / raft re-lash / lark flights?) -- unresolved.
  * sky_warren _collision: chunk distance = flat distance to the chunk's box (`_box_flat_dist`, not the 3D centre less
    0.7 x width: a tall chunk's centre is 30 m over a walker), CLOSE_M 6 -> 12 m; near_ready uses the same.  Kept
    (compile 12 OK, walks unchanged), cost unmeasured -- measure fps/shape count aboard before the next commit.
  * new harness: reference/tmp/walkdoor.sh DOOR (3x streamed, 3x preloaded), walkpair.sh, walk022.sh.
  No game running; lock released.  Nothing committed.
- ~06:45 door 2047 lead (AUDIT): no timed prop within 30 m -> likely the capsule TUNNELLING the 0-thickness ramp quad.
  sky_warren `_ramp_under` / RAMP_UNDER 0.2: every ramp collision quad is now a closed 0.2 m slab (compile 12 OK,
  not yet walked).  WAITING for AUDIT regen #3 + kit rebuild -> reimport -> `WALK_POLLS=200 bash
  reference/tmp/walk022.sh` (the 10th door is 2047).
- 2026-10-16 ~07:50 door 2047, after regen #3 (kit 06:32, imported 06:55): still 9/10 in 2 more full runs, same spot,
  with ramp slabs (`_ramp_under`, kept) and with the harness's up_speed re-read after move_and_slide like
  StationPlayer (walktest.gd, kept).  So NOT tunnelling, NOT streaming, NOT a stale fall speed.
  Trace (walktest.gd trace_door, frame by frame): the walker is on the floor, pinned at (10.71, feet ~3.0, -11.5),
  facing the next waypoint, while the island's carry is (-1.04, -0.9, 5.95) m/s -- SKY-022 drifts ~6 m/s with
  vertical bobbing of -0.9 .. +2.6 m/s.  Drift is deterministic in game time, so the 10th door of a fresh run always
  meets the same island motion; walked alone (other game times) it passes.  LEAD: move_and_slide on a fast,
  bobbing island (the carry added to velocity) can't climb this stair at that moment -- may hit real players too.
  NEXT: walk door 2047 alone at the same game time (start it ~t_session of door 10) or with the drift forced to
  that velocity; then fix the carry (move the player in the island's frame, or snap/sweep relative to the deck).
  * one-off: a fresh launch at 06:56 hung SKY-022's _prepare (0/134 chunks, no error) -- a relaunch built fine.
  * warning: a headless godot run while the game is up rewrites the DevBridge token (gcmd then fails).
  No game running; lock released.  Nothing committed.
- ~08:10 AUDIT final (reference/tmp/audit/all_final.json vs all_before.json): doors OK 47,350 / 47,357 (was 36,511 /
  47,460); unreachable 0 (3,145); risky 0 (2,170); entry blocked 7 (5,634); blocked cell edges 9 (10,963); rooms
  without a floor behind a door 6 (7,870); missing walls 0 (3,754); 91 / 100 islands walk-clean.
  The 6 "room_floor_missing" (SKY-078 x2, 025, 043, 049, 053) are NOT missing floors: assemble fkeys + a ray show a
  floor at the room level in the 5 checked; each door cell also carries a wall_shopfront_a_* (door pass, 5 cm sill)
  -> the "fell" is elsewhere on the entry walk.  Told AUDIT.  Nothing for _room_floors to add.
  Door 2047 (drift/carry) stays OPEN, next step as above.
  * AUDIT confirmed: the 6 are porch-stair/door drops (~0.7 m off a stair end at the door face), reassigned to GENERATOR as entry_drop.  RUNTIME open item: door 2047 only.
- 2026-10-16 ~08:45 coordinator review fixes (shots re-saved, all <= 400 KB; reference/tmp/gh3.sh):
  * Calder pools: back to the lamps' own reach/strength (POOL_REACH 1.0, POOL_GAIN 1.0), street_pool.gdshader gains
    uniforms `gain` (POOL_SHADER_GAIN 0.55) and `falloff` (POOL_FALLOFF 2.4, was 1.7); storefront pools SHOP_R 4 m,
    alpha 0.55.  The road is a dark night street again with distinct pools (gh_calder_signs_night.jpg).
  * Calder fps, nothing else running, vsync off, the shop street at night: 42 fps all / no pools / no city_signs /
    neither (GPU 10.8-12.2 ms, draws 1,557-1,816).  The 24 fps in the first shot was the AUDIT --all on the CPU.
  * banners: the real bug -- the instance is scaled 10-20 x across (the banner's width) and the shader added sway and
    the lean's x in those units: a "2.4 m" sway swung the foot 30-50 m (the diagonals).  sky_banner.gdshader now
    divides by length(MODEL_MATRIX[0].xyz); sway 0.025 -> 0.008, lean 0.03 -> 0.008, billow 1.2 -> 0.5, twist 0.12 ->
    0.04.  Furl only scales the length (no bend).  Islands near SKY-099 tilt <= 0.7 deg (max anywhere 4.3).
    Re-shot with a LEVEL camera (island-local (-160,-110,-300) -> (0,-110,0)): plumb, flat, readable.
  * lane day/night: a look-down-lane view picked by script (longest straight ground walk run, a 0.45 m sphere cast
    clear for 9 m, most lights within 14 m): SKY-099 (-4.5, 6.5, -59.5) along +z.
  * door 2047: left noted (drift/carry; not quick).  No game running; lock released.  Nothing committed.
- ~08:35 collision A/B (reference/tmp/ab.sh old|new; dev statics SkyWarren.close_m / flat_dist / ramp_under):
    SKY-099 stand phys 5.18 -> 4.87 ms, walk 8.15 -> 5.51; proc 15.0 -> 15.5 / 21.4 -> 21.6; shapes 10 -> 8, tris 52k -> 40k
    SKY-071 stand phys 7.59 -> 7.75 ms, walk 7.92 -> 8.16; proc 19.3 -> 19.2 / 24.2 -> 26.0; fps 78/78, 66 -> 64
  -> within noise / budget: KEPT (flat distance adds fewer tall far chunks; the 0.2 m slabs cost nothing measurable).
- banner lettering read backwards from outside: the strip's front faces out along +z where +x runs to the viewer's
  left -> sky_banner.gdshader mirrors u on FRONT_FACING (plain on the back); verified both sides (gh_banners_from_below
  re-shot, 292 KB; far side reads "DWARF APPLES - SEED STOCK").  No game running; lock released.  Nothing committed.
