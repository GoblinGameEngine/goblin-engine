# Offline geometry audit (tools/sky/warren/audit)

Checks every warren island's assembled geometry -- render mesh and collision exactly as the game builds them -- and
walks the player's capsule over it, without launching the game.  Python: `~/.venvs/ssc-assets/bin/python`
(numpy, scipy, shapely, PIL, trimesh 5.1.1, embreex 4.4.0 for the ray casting).  Run from the repo root.

```
P=~/.venvs/ssc-assets/bin/python
$P tools/sky/warren/audit/audit.py SKY-022            # all checks -> reference/tmp/audit/SKY-022.json, .png, _render.png
$P tools/sky/warren/audit/audit.py --all              # every island -> all.json + per island files
$P tools/sky/warren/audit/audit.py SKY-022 --wdir DIR # audit an island's files from another directory (mutants, drafts)
$P tools/sky/warren/audit/bounds.py [--png N]         # kit.glb + kit_mid.glb against their contracts -> bounds_kit.txt
$P tools/sky/warren/audit/kitmesh.py [x.glb ...]      # topology + normals of every mesh in a GLB (default the kit)
$P tools/sky/warren/audit/calibrate.py all            # agreement with the game's own measurements (see Verification)
$P tools/sky/warren/audit/mutate.py SKY-099           # mutation self-test: does each check catch its fault
$P tools/sky/warren/audit/assemble.py SKY-022         # just build + cache the geometry, print counts
$P tools/sky/warren/audit/render.py SKY-022 --persp EX,EY,EZ TX,TY,TZ | --top   # offline PNG view (Embree, no GPU)
```
Runtime: 45-70 s an island (SKY-022, 73 k placements, 2.8 M render / 0.76 M collision triangles: 45 s with the pair
cache warm), small islands 10-20 s.  Geometry is cached per island in `reference/tmp/audit/cache/` (keyed by the
input files' mtimes), pair configurations in `cache/pairs_<kit hash>.pkl` (shared by all islands).

## Files
| file | what |
|---|---|
| common.py | readers: warren file with its chunk table, pieces.json + kit.glb as the runtime loads them (`Kit`: mesh, AABB, collision rule), islands.json deck grid (`Deck`), a general glTF reader, placement transforms |
| assemble.py | `build(iid)` -> `Geo`: render triangles (per placement), collision triangles exactly as sky_warren.gd builds them, plus the deck (rock.glb `deck-col`, tucked like `_tuck_deck`), the rim fence (`_build_fence`), the bridges (sky_bridge.gd: every mesh solid, stowed pose). `Geo.label(prim)` names a collision triangle's piece (slabs resolve to the floor piece of their cell) |
| meshlib.py | the REUSABLE library (any triangle soup / GLB): topology (open / non-manifold / inconsistent-winding edges, degenerate + duplicate faces, components, inside-out parts), inward normals (ray parity), coplanar overlaps (z-fighting), duplicates across groups, interpenetration (edges piercing faces), bounds (mesh vs box), tri/box overlap, `visible()` (is a point seen from in front of its face), `TriIndex`, `read_glb_meshes` |
| rays.py | Embree ray caster (`Rays(tris).cast(o, d, tmax)` -> distance, triangle, facing normal); ~3 M rays/s |
| walksim.py | the player's capsule as ray bundles, many agents per Embree call; `walk_edges` (every graph edge) and `walk_paths` (walktest.gd's door walks) |
| walkcheck.py | the walk check: every walk-graph edge both ways, BFS from the travel point, door reachability + entry |
| pairs.py | piece-vs-piece checks once per configuration (piece a, rot/mount, piece b, offset), cached |
| checks.py | the warren checks (below) -> hotspots |
| bounds.py | the kit client of meshlib.bounds |
| kitmesh.py | meshlib.topology + inward_normals over every mesh of any GLB (kit.glb, kit_mid.glb by default) |
| img.py | PNG views (front/side/top of a part against its boxes) and the island plan canvas |
| render.py | offline perspective / top views: a ray per pixel, kit palette colours, sun + shadow ray (~1-8 s a view) |
| audit.py, calibrate.py, mutate.py | the CLIs |

## The collision it reproduces (sky_warren.gd, file:line as of 2026-10-16)
* `_load_pieces` (l.369-465): per piece `cmode` -- `ramp` (pieces.json ramp quads), `frames` (frame boxes),
  `top` (ground / slab / roof, interior < 0.3 m: the top face of the mesh AABB), `mesh` (passage, bridge, ids with
  "arch" but not "blind"), `box` (the mesh AABB; walls and edges clipped to z <= 0.12); the AABB is the MESH's, not
  pieces.json bounds.
* `_rec_xf` (l.820): cell centre at y (DECK: deck_y; else 3.2 k + 0.8 q), `Basis(UP, rot pi/2)`, face +1.5 z,
  corner (+1.5, +1.5).  Collision ignores the mirror bit.
* `_merge_chunk` (l.856): `top` with DECK -> no collision; whole-cell `top` (AABB covers +-1.45, mount 0) ->
  `_floor_slabs` (l.955): per chunk, per height (cm), greedy rectangles, 0.4 m thick boxes; vertices snapped to
  1 mm.  `ConcavePolygonShape3D`, backface collision on.
* deck: `<id>.rock.glb` node `deck-col` (its trimesh), vertices pushed 0.1 m under the lowest paving top within
  2.2 m (`_ground_prep` / `_tuck_deck` l.1656-1740).  Fence: sky_island.gd `_build_fence` (l.873): 1.4 x 0.12 m
  boxes per ~3 m, none within gap width / 2 + 1.5 m.  Bridges: sky_island.gd `_build_bridges` (l.976) +
  sky_bridge.gd `setup` (every mesh a trimesh body "solid"; the moving nodes at deploy 0 = stowed; `--` the span
  stands upright 1.0-4.5 m inland).
* RUNTIME rules added 2026-10-16 (mirrored, ASM_VERSION 5): `_door_prep`/`_door_leaf` -- a pass_kind "door" piece on a
  face is shut by a solid leaf box (x pass +-0.03, y 0..pass top + 0.03, z -0.14..-0.08) unless a door record on that
  face (either side) is entered; `_room_floors` -- an entered door's cell gets a whole-cell floor at its storey if
  none is within 0.4 m; sky_bridge.gd `ramp_box` -- the 4 cm threshold ramp (z -1.7, y -0.12 to z -0.45, y 0.03).
  The walk check treats non-entered doors as shut (only their step outside must be reachable).
* Parked larks (sky_island.gd `_build_props` / `_spawn_lark`): a box +-0.95 x +-2.35 m, 2.75 m tall on each of the first
  `aerostats` pads (remake/bible/sky_islands.json), at the pad's y (or the deck) + 0.02, turned by its yaw (source
  LARK).  RUNTIME `_ramp_under` (ASM 7): every ramp quad is a 0.2 m slab along its upward normal (underside + edges).
* Not modelled: the player's own body, islanders, larks in flight.

## The player (StationPlayer)
Capsule r 0.18, height 1.45 (origin 1.43 m over its bottom), floor_max_angle 55 deg, floor_snap 0.5 m, no step-up,
4.2 m/s, gravity 9.8 x 0.89 (walktest.gd).  walksim:
* horizontal: ray bundles along the motion (11 heights x 7 across the capsule's width at that height; on a floor the
  rays follow its plane, as move_and_slide's motion does); a hit on a non-floor surface stops the capsule at
  `t - sqrt(rh^2 - o^2)`, the rest slides along it (3 slides).
* the lowest layer sits at the tallest edge the capsule can still take as floor: the sphere's first contact with
  an edge e over the plane it rolls on must have a normal within 55 deg -> 7.7 cm on the flat, 3.7 cm at 15 deg,
  ~0 at the top of a 28 deg ramp (so a paving top 5 cm above a ramp's head is a wall).  STRICT mode uses exactly
  that; LENIENT takes edges up to 6 cm over the plane (Godot's slide + snap gets the capsule over a 5 cm stair-head
  lip in ~30-80 % of walks in game) and records the difference as hazards ("risky").
* support: rays down from the capsule's top inside its footprint, each lifting a sphere (y + sqrt(r^2 - d^2) - r);
  a hit above the allowed rise is something inside the capsule: the step is undone; supports within 0.5 m below
  snap, else the capsule falls.

## The checks (hotspots: check, kind, xyz, cell (i, j, level), pieces, value)
| check / kind | how | owner of a fix |
|---|---|---|
| walk / edge_blocked, edge_fell, edge_height, edge_risky, edge_drop | every walk-graph edge of neighbouring cells, both ways, strict; failures re-run lenient (pass -> risky).  Edges onto stair-core nodes (k * 3.2 + 0.1, inside houses) are the islanders' ("core", not tested); long court/plank edges are tested but reported as virtual_* and kept out of the BFS | generator (graph, grading), kit (ramps, lips) |
| walk / door_unreachable, door_risky, door_entry_blocked, door_no_node_outside | BFS from the travel point over the passing directed edges (risky edges: reachable but not safely); each door's outside node; an entry walk 0.65 m through the doorway; unreachable doors carry the first failing edge on the graph's own route | generator / kit |
| holes / no_floor, floor_off | rays down at every walk node (5 points) must meet collision at the node height | generator / runtime |
| holes / roof_open | 16 rays down over every column's top room (render) must stop at its roof | generator / kit |
| holes / room_floor_missing | a door's entry walk falls just inside: the room has no floor | runtime / generator |
| cracks / missing_wall, buried_face, culled_slot, see_through, seam | rays from outside every exterior room face (0.4 m, or 0.1 m beyond what the face's pieces put out: jetties, oriels) (4 heights x 7 across, openings skipped in their opening) must hit the facade (render); none = no wall piece there / looking into the hollow under the deck / through a piece / between two bays | generator / kit |
| cracks / riser_gap | where a walk cell stands > 6 cm over its neighbour the face between must be closed (skirt, plinth) | generator |
| manifold / kit_piece | meshlib.topology of every kit piece used (non-manifold, inconsistent winding, inside-out, duplicate faces) | kit |
| manifold / dup_across | identical same-facing faces of two placements (per configuration) | generator |
| zfight / coplanar | same-facing coplanar overlaps of two placements that can be seen (view ray from 0.3 m in front meets only the pair) and differ in material or palette (one material + one palette can't be seen to fight) | kit / generator |
| floating / isolated, unsupported | a placement whose box (+3 cm) touches no other box nor the deck; a ground-standing piece (stair, decor, cell, tower, water edge) with nothing within 8 cm under its lowest faces | generator |
| intrusion / pass, clearance, render_clear | rays through every walk-through piece's pass volume and through the capsule's standing volume at every ground node: other pieces' collision (blocks) or render (shows through the player) | generator / kit |
| intrusion / into_room | rays along each exterior wall's inner face: something poking through the wall into the room | kit |
| intrusion / pierce | edges of one placement piercing > 2 cm into another's faces, where it shows, with a non-structural piece involved (wall/corner/roof joints and hung overlays are construction: in stats only) | kit / generator |
| bounds (bounds.py) | each kit piece's mesh vs pieces.json bounds ("declared"), its declared box vs the slot envelope of its kind/mount ("declared>slot": the declared overhangs), the runtime collision vs the mesh ("collision>mesh"), solid kinds' mesh far past their box collision ("mesh>collision"), the MID model vs the full piece ("mid>full"); PNG per offender (front/side/top, overrun red) | kit |

The island heat maps: `<id>.png` -- grey = collision height, blue graph = walk edges, red = blocked edges /
unreachable or blocked doors, orange = risky, crosses = geometry hotspots by kind; `<id>_render.png` -- render
problems (z-fighting, piercing, see-through) as a per-3 m-cell density.  Plan orientation: rows = +X (south) down,
columns = +Z (west) right, like the twin's plan strings.

## Verification (2026-10-16)
* Collision assembly: every contact point of the in-game capsule sweep (reference/tmp/passcheck.gd results on the
  same files: SKY-099, 078, 071, 022) lies on the assembled collision within 1 cm, on the right body (warren /
  bridge "solid" / fence): 453/453 (larks and the player's own body skipped).
* Walk sim vs walktest.gd (reference/tmp/pass3.out: 10 door walks each): 40/40 explained -- same verdict, stuck
  spots within 2.5 m or on the same graph edge, or the game stuck on a lip the strict model refuses and the lenient
  one takes (stochastic in game).  Game stucks: bridge housings (022 arrival, 071), court edges through houses
  (099), 5.2 cm stair-head lips of pave_garden(_skirt) (078 x3, 022 x6).
* Mutations (mutate.py): floor deleted, paving raised, solid box in an arch, wall bay removed, piece duplicated,
  piece floated, kit piece scaled 10 %, wall shifted 20 cm, collision box past its mesh, all faces flipped, one
  face flipped: 11/11 caught by their checks;
  the other checks only report consequences of the same fault.

## Known limits
* walksim approximates move_and_slide with rays: thin features between the 7 x 11 rays (< ~4 cm), exact Jolt contact
  normals, recovery and the island's drift are not modelled; LENIENT's 6 cm is calibrated on 3 sites only.
* The stowed bridge pose is assumed (a lowered bridge's deck colliders and plate are not added; the bridge housing's
  27 cm platform lip is real either way).  Larks are not modelled.
* floating/isolated is box-based (a piece whose box overlaps a neighbour's but whose triangles don't is missed);
  zfight buckets faces by 1.5 m cells (overlaps between faces whose centres fall in different cells are missed);
  pierce depth is along the piercing edge, not the true penetration.
* cracks rays test 4 heights x 7 positions per face: holes smaller than ~0.4 m can slip between; openings are
  recognised by name (door, arch, gate, portal, shopfront, ...) or a pass volume.
* walk tests the twin's walk graph: cells the graph doesn't join are not tested as routes.
* Normals: winding consistency is exact (shared welded edges); "inside-out" needs a closed component (glTF CCW =
  outward); the ray-parity inward fraction is only meaningful for watertight parts (open single-sided kit walls
  read 10-40 %).
* bounds' slot envelope for face pieces uses the id suffix for thickness (_t 0.25, _k 0.6) and a 0.6 m overhang.

## Phase 2: one geometry toolkit for every asset (plan)
The goal (the user): the AI working through a shell SEES, CHECKS and MODIFIES any of the game's geometry without the
game.  meshlib/rays/img are already asset-agnostic; the warren is one client.  Next:
1. `tools/geo/geo.py` with subcommands, text output + small PNGs:
   * `list` -- every geometry source with ids: kit pieces (pieces.json), warren islands (remake/sky/warrens),
     city and town buildings (godot_project/remake/buildings/*.glb + their records), terrain and roads (the bakes),
     vehicles and fleet bodies, characters (the NPC generator's outputs), props, the sky islands' bases (rock.glb).
   * `load` / `assemble` -- one model, or a region by coordinates or name ("Calder x,z r 150", "SKY-022"), placed as
     the game places it: mirror each placement script the way assemble.py mirrors sky_warren.gd, cite file:line,
     verify once against the game (a DevBridge dump or existing screenshots / sweeps, as calibrate.py contacts does).
   * `render` -- offscreen PNGs: ortho front/side/top, perspective from a point at a target, a section at a height,
     colour by material / normal / problem.  Candidates: a numpy + Embree ray caster (already here: one primary ray
     per pixel, ~3 M rays/s -> 640 x 480 in ~0.1 s on an island), Blender -b via flatpak for shaded views
     (`flatpak run org.blender.Blender -b --factory-startup --python ...`, output under /home/deck), pyrender+EGL.
     Measure and pick; the Embree caster needs no GPU and runs beside the game.
   * `inspect` -- stats (tris, materials, bounds, components), "what is at x,y,z", "which pieces touch this box",
     raycasts (Geo.label already does this for warrens).
   * `check` -- the library: manifold, normals (winding + inward), bounds/envelope, clipping/interpenetration,
     z-fighting, holes, floating, and the walk sim wherever a walk graph or a navmesh exists.
   * `diff` -- before/after of a model or region: numbers (per check) + an image pair / difference image.
   * `edit` -- small scripted changes through each asset's SOURCE of truth, never the exported GLB: kit pieces via
     remake/blender/sky/warren_kit (build.py), warrens via tools/sky/warren (the generator), vehicles via their
     modular builders (tools/assets, remake/blender), buildings via their build scripts; report the source per type.
2. Fast and cached: an island or a district in under a minute, a model in seconds (per-configuration pair caching
   as pairs.py does; geometry caches keyed by source mtimes).
3. Self-tests: a mutation test per check (as mutate.py) and a smoke test over a sample of every asset type.
