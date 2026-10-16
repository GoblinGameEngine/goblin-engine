# AUDIT stream handoff (offline warren geometry audit), started 2026-10-16

Task: tools/sky/warren/audit/ -- assemble each island's render + collision geometry offline (exactly as sky_warren.gd
builds it), check holes / cracks / non-manifold / z-fight / floating / interpenetration / walk (capsule sim + BFS),
verify with mutation tests + calibration against the in-game walks, then fix SKY-022 at the generator and run --all.
Rules: no game launch, no commits, no subagents.

## State
- 10-16 start: read FORMAT.md, sky_warren.gd collision (l.420-465, 856-1020), sky_island.gd (deck = rock.glb
  "deck-col" trimesh, tucked 0.1 m under paving within 2.2 m; fence boxes 1.4 x 0.12), sky_bridge.gd (bridges: every
  mesh a trimesh body "solid", housing fixed, span stowed upright), walktest.gd (door choice + BFS route on the folk
  graph, straight walk between nodes, stuck = 5 s without 0.5 m progress).
- pip: trimesh 5.1.1, rtree 1.4.1, embreex 4.4.0 installed and importing in ~/.venvs/ssc-assets.
- Early findings (before any tool): SKY-099's two in-game stucks are on COURT edges of the walk graph (units.walk_graph
  links the door's outside node straight to the court, 20-30 m through the house); SKY-022's arrival stuck (159.7, 1.5)
  is 4.6 m inland of the S face = the bridge style's "clear.inland" 4.6 -> the bridge housing.

## Added requirements (coordinator, 10-16)
1. Mesh checks as a REUSABLE LIBRARY (any GLB or triangle soup): non-manifold, open edges, degenerate/duplicate faces,
   winding consistency across shared edges, normals pointing into the closed volume, interpenetration, z-fighting.
   Warren assembly + walk sim = one client.  README must state the plan (later: kit, city buildings, vehicles,
   characters, terrain, roads).
2. BOUNDS check (library + warren client): mesh extents vs declared contract (pieces.json bounds; slot envelope per
   kind/mount; collision vs render mesh), in-island intrusions (cells/lanes/walk clearance/pass volumes/neighbour
   walls), general GLB-vs-box API.  Output: ranked list (piece, bound, cm, placements), overlay PNG per offender
   (front/side/top, overrun red), island heat map.  Mutation tests (scale 10 %, shift wall 20 cm, collision box > mesh).
   Run on kit.glb + kit_mid.glb now; top offenders in report; KIT fixes listed here, not edited unless trivial.

3. PHASE 2 (plan only, write into README + here; phase 1 = this warren audit first): one CLI (tools/geo/geo.py)
   list / load-assemble (any model or region, as the game places it, cite file:line, verify vs game) / render
   (headless PNG: ortho, perspective, section, colour by material/normal/problem) / inspect (stats, point + box
   queries, raycasts) / check (the library) / diff / edit (through each asset's real source of truth, never the
   exported GLB).  Fast + cached (island/district < 1 min), mutation self-tests + smoke test per asset type.

## Layout (tools/sky/warren/audit/)
common.py (readers), assemble.py (island render + collision tris, cached), meshlib.py (general mesh checks),
rays.py (embree), walksim.py (batched capsule walker), checks.py, bounds.py, audit.py (CLI), mutate.py, calibrate.py.

## Results so far
- CONTACTS (calibrate.py contacts): every in-game capsule-sweep contact point on WarrenBody / bridge "solid" /
  FenceBody lies on the assembled collision within 1 cm and on the right body: 099 85/85, 078 92/92, 071 191/191,
  022 85/85 (larks + the player's own body not modelled: skipped).  => transforms + collision rules exact.
- WALKTEST replica (calibrate.py walktest; same doors, same BFS route, walksim capsule): 40/40 door walks explained
  (reference/tmp/audit/calibrate.out).  Strict model = sphere-contact physics (an edge is floor only if the contact
  normal is within 55 deg: 7.7 cm on the flat, ~0 cm at the top of a 28 deg ramp); lenient = edges <= 6 cm over the
  ramp plane taken (Godot's slide+snap gets over ~5 cm lips most times).  Game stucks are on:
  * bridge housings (SKY-022 arrival 159.7,1.5; SKY-071 72.9,103.5): bridge glb "solid" trimesh 4.6 m inland, the walk
    graph runs through it;
  * court edges (SKY-099 both): units.walk_graph joins a door's outside node straight to the court, through the house;
  * 5.2 cm lips at stair heads (SKY-078 114,-5.4 x3; SKY-022 103.8,-9.2 x5, 147.2,-2.7 x1): steps_up's ramp ends at
    the storey line, pave_garden / pave_garden_skirt tops are +0.052 (also wall_brick_herringbone +0.10,
    ground_falaj +0.06, pave_calcada +0.028, pave_slate_whitejoint +0.018).  Stochastic in game (~30-80 % stuck).
- Kit notes found on the way: stair_plex_outdoor ramp starts 0.18 m up, stair_spiral(_courtyard) 0.20-0.21 m (lips
  at their feet); basketball_court collides as a "top" quad at 3.65 m (its hoops) over 6 x 9 m.

- audit.py works end to end: SKY-022 45 s (pair-config cache warm; ~70 s cold).  Files: walkcheck.py (edge walks
  + BFS + doors), checks.py, pairs.py (per-configuration pair checks, cached), meshlib.py (+ visible(), TriIndex),
  bounds.py (kit), img.py.  SKY-022 before-fix audit: doors 1359 -- 0 ok-safe: 1206 reachable only over a risky
  lip (the arrival's stair head 147,-1.5), 145 entry blocked (shopfronts collide as boxes 74, int_counter in the
  doorway 33, roller shutters 18), 8 unreachable (bridge housings); 81 blocked directed edges (bridge 61, fence 20);
  846 rooms behind doors with no floor (interiors shed by kitmap.budget); 2662 exterior room faces with no wall.
- kit bounds (bounds.py): every mesh within its pieces.json bounds; MID models: band_peranakan_tile reaches 100 m in
  +z (broken MID), chapel_cycladic +50 cm, steps_up -15 cm, most MID walls +10 cm in y; frame boxes of 8 door/arch
  pieces 6-7 cm below their mesh (mesh starts at y 0.07).

- MUTATIONS (mutate.py SKY-099): 9/9 faults caught (floor, raise, arch, wall, dup, float + kit scale, shift,
  colbox); collateral hotspots are consequences of the same fault (a raised slab also floats + fills the node's
  clearance; a box in an arch also z-fights/pierces it) -> reference/tmp/audit/mut/mutate.json.
- SKY-022 FIXED AT THE GENERATOR (backups of the originals: reference/tmp/audit/gen_backup/):
  * lattice.py: FENCE_CLEAR 1.6 (walk cell centres >= 1.6 m in from the outline; fence at 1.0 m) and bridge
    footprints (bridge_styles clear.inland + width/2 + 0.45, + 0.25 m) set OUT and taken off the gate cells;
  * kitmap.py: flush(): a raised ground piece (pave_garden(_skirt) +5 cm, brick +10 cm ...) on a stair's head or
    foot cell -> pave_lane(_skirt) (L.flush_swapped);
  * units.py walk_graph: no sideways edge between two stair cells of a wide flight (the 20 cm slot between the
    kit's 2.8 m ramps) (L.walk_side_cut).
  Regenerated (make_warren.py SKY-022:hk_neon_canyon, lods.py SKY-022).  Audit before -> after:
  directed edges blocked 81 -> 0, risky 20 -> 0; nodes reached safely 17/3112 -> 3081/3081; doors ok-safe 0/1359 ->
  1190/1315 (rest: 125 entry blocked by kit/generator interiors, below); door walks predicted by the replica 10/10
  (game was 2/10).  Files: reference/tmp/audit/before/ (old island + audit), SKY-022.after.audit.json.
  OTHER ISLANDS ARE NOT REGENERATED: the fixes apply to all on the next `make_warren.py --all` + lods.py.
- Remaining on SKY-022 (owners):
  * KIT: wall_shopfront_a_t/_k collide as boxes -> shops can't be entered (69 doors): give them frame + pass;
    steps_up ramp quads x +-1.4 (20 cm slots in wide flights); stair_plex_outdoor / stair_spiral(_courtyard) ramps
    start 18-21 cm up; basketball_court "top" quad at 3.65 m; MID models: band_peranakan_tile +100 m z, chapel +50 cm,
    most walls +10 cm y; wall_sign_column_t is see-through as a room's facade (133) and pokes into the room (267).
  * RUNTIME/GENERATOR decision: 804 doors open (frame collision) into rooms with no floor (interiors only on
    "entered" cells: pick.py enter_doors 0.25) -> collide the leaf of non-entered doors, or floor every door room.
  * GENERATOR: int_counter in a doorway (22), roller shutters closing shop doors (15); 2458 exterior room faces with
    no wall (not buried; cause not found yet -- cells in SKY-022.json hotspots cracks/missing_wall), 223 "buried"
    faces (pick.py skips walls below the next column's ground level, but the deck is a surface: the room looks into
    the hollow under it).
  * BRIDGES: the housing platform top is +0.27 m over the island deck (rolling_lift glb "bridge" node): a 27 cm
    lip -- the player cannot step onto a lowered bridge.

- Missing walls explained: of SKY-022's 2681 bare exterior room faces 2403 are 1-cell slots between rooms that the
  civ leaves bare on purpose (SPEC cull_slots: hk_neon_canyon, chongqing, korean, knights, hanseatic, yokocho,
  karachi) -> kind culled_slot; 219 buried_face; 59 unexplained missing_wall; 134 see_through (wall_sign_column_t).
- kitmesh.py (normals/topology of every GLB mesh): kit.glb 402 meshes -- 0 inconsistent winding, 0 inside-out
  closed parts, 88 with non-manifold edges (wall_ablaq_portal_k 56, wall_yemeni_mafraj_k 33, ov_prayer_flags 30,
  wall_mashrabiya_box_k 24, wall_door_portal_k 18 ...), 340 open (single-sided walls: expected); kit_mid.glb 222 --
  22 non-manifold (skybridge_timber 18, minaret_mamluk_shaft 12, church_spire_copper 12 ...).
- README.md written (usage, checks, verification, limits, phase-2 plan).

- --all (2026-10-16 ~03:30, current files: SKY-022 fixed, the other 99 as the GENERATOR left them): 100 islands,
  2533 s (mean 25 s, max 75 s, min 5 s), 0 errors -> reference/tmp/audit/all.json + SKY-xxx.json/.png/_render.png.
  Doors 47,460: ok 36,511 (77 %), entry blocked 5,634, risky 2,170, unreachable 3,145; directed edges 417,844:
  blocked 10,963, risky 407, fell 125, height 200, drop 9.  Blockers of edges: bridge 3,747, fence 3,499,
  utility_pole 2,798 (NEW: poles on walk cells), raised paving slabs (pave_lane / brick / falaj) ~400, int_counter 142.
  Unreachable doors: bridge 1,448, fence 730, utility_pole 621, ground_falaj lips 323.  Entry blocked: shopfronts
  3,184, int_counter 815, wall_portal_knockers_k 481, plain walls on a door face 517 (door swapped away?).
  Risky: pave_garden_skirt 213, steps_up side slots 107, pave_slate_whitejoint 45, ground_falaj 19.
  Others: holes/no_floor 1,980 (SKY-071 1,308 -- its roof walk nodes: lead, unchecked), roof_open 3,328 (SKY-011
  1,552, SKY-046 1,109: rays from above fall to the deck -- lead), room_floor_missing 7,870, culled_slot 19,986,
  buried_face 5,701, missing_wall 3,754, see_through 6,132 (wall_jetty_t 2,366, wall_sign_column_t 790,
  wall_jharokha_canted_k 778), zfight 170,653 visible pairs (corner_column, plinth_k, int_ceiling, wall_plain_k),
  pierce 250,559 (int_ceiling/int_floor through walls ~175 k), floating isolated 12,944 (ov_lantern 6,473,
  ov_laundry 4,413), pass intrusions 5,415 (wall_arch_round_k 2,490, int_counter 1,122).

## Next step (for whoever continues)
1. Regenerate everything with the four generator fixes (make_warren.py --all, lods.py), re-run audit --all: expect
   the bridge + fence classes (~7,200 blocked edges, ~2,200 unreachable doors) and the stair-head risky lips to go.
2. GENERATOR: utility_pole off walk cells (2,798 edges); ground_falaj / brick / slate raised tops at ramp ends are
   covered by kitmap.flush, but raised paving next to flat paving > 7.7 cm (brick +10 cm) still blocks: flush them
   on walk cells or give them a 0 top; counters out of doorways; the 59+3,754 missing walls; leads above.
3. KIT / RUNTIME requests: as listed under "Remaining on SKY-022" (shopfront frames, ramp widths and feet, door
   leaves of non-entered doors, MID overruns, non-manifold meshes in kitmesh_kit.txt).
4. Phase 2 (tools/geo/geo.py) per README.

## Commands
P=~/.venvs/ssc-assets/bin/python
$P tools/sky/warren/audit/assemble.py SKY-022            # build + cache geometry (5 s), prints counts
$P tools/sky/warren/audit/calibrate.py all [SKY-xxx]     # contacts + walktest vs reference/tmp/pass3.out
$P tools/sky/warren/audit/audit.py SKY-022               # -> reference/tmp/audit/SKY-022.json/.png/_render.png
$P tools/sky/warren/audit/audit.py --all                 # every island + all.json
$P tools/sky/warren/audit/bounds.py                      # kit + MID bounds -> bounds_kit.txt, bounds/<piece>.png
$P tools/sky/warren/audit/mutate.py SKY-099              # mutation self-test (~2.5 min)
