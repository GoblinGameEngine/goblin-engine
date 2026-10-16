# GENERATOR handoff — sky-island warrens, walkability pass (2026-10-15)

Written by the outgoing GENERATOR fork for its replacement. Nothing is committed. The last full run (`--all` + `lods.py`)
finished clean just before this was written; its log is `/home/deck/.claude/jobs/204e5d66/tmp/all7.log` (that job dir is
temporary — rerun to regenerate). Python: `~/.venvs/ssc-assets/bin/python` (numpy lives there; the system python has none).
Run everything from `/home/deck/goblin-engine`.

## 1. What the user asked for (in order)

1. "Everything needs to be traversable. Buildings need entrances and those entrances need to be accessible. I'm seeing a
   lot of doors two storeys up and stairs that you need to jump to traverse. The ground needs paved walking paths."
2. (coordinator, after the in-game walk reached 12/24 doors) stairs reachable only along their axis; duplicate placements;
   SKY-078 arrival stair + pond kerbs; a physical walk check (pieces.json `ramp` quads, 0.3 m step); rerun `--all` + `lods.py`.
3. (coordinator) walk check 100/100: sealed lots via fallbacks (a) regrade street (b) side/back door via a 1-cell yard
   (c) lower the floor (d) annex/garden; SKY-081 over the 25k-tri chunk budget; the 52 unsupported rooms; remove WALK_OLD.
4. "The player character does not fit through a lot of the arches": the physical check tests the capsule (require
   ≥1.0 × 2.2 m) through every opening; route around or swap for a wider portal; report openings failed before the fix.
5. (KIT) `pass` / `frame` boxes landed in pieces.json (35 walk-through pieces, `pass_kind` open|door, `clear`, `foot`);
   use them; `door` kinds are walk-through only into a room or lane; shared `wall_door_t/_k` opening is now 1.1 × 2.35.
6. (RUNTIME sweep on SKY-071, before the frame change) 1,469 / 8,521 walk-graph edges blocked: roof shacks ov_shack_a/b/c
   (1,222), wall_door_t (142), edge_parapet_plain_t (48). Overlay cells non-walkable, parapets barriers, doors only into a
   room/lane, physical check = runtime collision. Also SKY-078 in-game: 2/10 doors, six stuck beside the arrival at cells
   (75–76, 44) — full-storey stair on a bank cell beside a kerb with retaining walls both sides.

## 2. State at handoff (all7 run, 100 islands, ~16 min)

| | |
|---|---|
| walk-graph check (`walk.check`) | 100 / 100 pass; 42,459 / 42,459 doors; 152,610 / 152,610 public cells; 4,780 stairs all with foot + head |
| physical check (`walk.physical`) | 100 / 100 pass; 42,459 / 42,459 doors; 152,609 / 152,609 cells (1 landmark cell taken off the walk) |
| lots without entrance | 0 (fallbacks used: 901 stoops, 122 porches, 9 yards, 21 storeys added, 160 annexed, 2 gardens) |
| fill over the deck | mean 0.30 m per island (max island mean 0.95 m) |
| unsupported rooms | 0 (54 removed) |
| chunk tri budget | max 25,000 everywhere (SKY-081 fixed) |
| duplicates | 0 left (33 removed by the exact-dup filter; `check/placed.py` shows only stacked-at-one-height pairs, not repeats) |
| openings (capsule box 1.0 × 2.2) | before fix: 7,860 edges + 2,520 doors blocked; after: 10 edges, 0 doors (those 10 edges are excluded from the physical walk and the graph) |
| runtime walk graph pruned (`openings.prune_graph`) | 3,824 edges cut, 1,344 roof nodes blocked (shacks/tanks), 653 ladders/planks removed |
| graph components | 90 islands one component; 10 have small leftovers (e.g. SKY-071 [6153, 19, 17, 16], SKY-081 [1505, 36, 8, 7]) — roof pockets cut off by the pruning, see §5.6 |
| LODs | `lods.py` exit 0 |

Culprits of blocked openings (before fix, whole run): wall_shopfront_b_k 1,552, wall_shopfront_b_t 1,248, ov_lantern 598,
ov_ac 528, wall_tbilisi_balcony_t 417, wall_jetty_t 351, band_damp 325, ov_stall 319, ov_planter 303, band_zocalo 295,
utility_pole 249, ov_sign_arm_big 162, bastion_wall_slope 135, band_flood 117. Structure kept in the way (reported, not
removed): pagoda_temple_tiers ×1 (SKY-045; its cell was taken off the walk instead).

## 3. Files changed (all under tools/sky/warren unless noted) — nothing half-finished

Git: `walk.py`, `walknet.py`, `openings.py`, `check/` are UNTRACKED (new this round, never committed);
`kitmap.py pick.py units.py writer.py make_warren.py assemble.py FORMAT.md civ/{family,maghrebi_medina,cycladic,
hakka_tulou,caucasian_balcony,nouvelle_france,saharan_kasbah,knights_harbour}.py` are modified. `research/sky_islands/
warrens/runtime_requests.md` is modified (runtime's), `flicker.md`, `kit_coplanar_faces.txt` untracked (runtime/kit's).

### walknet.py (NEW, the ground layout — replaces the old repair loop)
Builds the walk network path by path from the arrival cell. Every walk cell is FREE until a path takes it, then FIXED as
`("f", q)` flat paving at q quarters (0.8 m; q even = half-storey terraces, see `walk.base_q`) or `("s", q, rot)` a
`steps_up` stair from q rising 2 quarters toward `FACE[rot]`. Paths only take free cells or cross fixed ones as they are, so
the network is connected by construction.
- `Net` (60): `base` (lowest q over the deck per cell), `cap` (headroom under a room: `4*k-3`; a room so low there is no
  2.4 m headroom is cleared → `L.opened`), `flat_ok`/`stair_ok` (cost or None; `MAXF`=8 quarters max fill, `FILL_W` 0.6 per
  quarter, `STAIR_C` 2.0, `DOOR_P` 4.0 penalty for paving a door's step at none of the house's floors), `moves` (flat,
  up a stair, down a stair), `search` (Dijkstra over (cell, q) until a fixed flat cell; `MAX_POPS` 40k), `conflicts`,
  `commit`.
- `fronts` (31): entrance candidates per lot (front faces → any room cell beside walk ground → entry yard → own court).
- `route_lot` (230): starts = flat at a floor, or a stoop (stair on the step, foot behind); then side/back faces; then a
  porch (`porch_starts` 199: house gives its front room to a stair cell, up to the floor or down from it; `down` porches
  are `L.door_feet`); then a 1-cell yard (lot cell beside walk ground paved at a floor, door from the yard).
- `ripup` (401) / `ripup_r` (413): a hemmed-in lot takes up paving within radius 2 then 4 of its front, lays its own path
  first, relays every door that lost its way; kept only if `door_ok` for all.
- `run_round` (465), `solve` (483): rounds (`WALK_ROUNDS`, default 4) with failed lots first; then the leftovers: carve
  passages to shut-in pockets (`walk.carve`, max 8), sunk houses gain storeys (`L.grown`), unreached public ground joined
  cheaply or planted (PASTURE), stale doors dropped, stairs into walls flattened, annex/garden for anything still sealed
  (`lot["annex_of"]` / `lot["garden"]`; a lot with no door gets no unit in `units.make_units`, so nobody lives sealed in),
  hanging rooms removed (`L.supported`, `unsupported_removed`), then `walk.check` and the stats.
- Debug: `WALK_DEBUG=1` prints FAILED lots, BAD DOOR, BAD STAIR; `WALK_ROUNDS`, `DOOR_P` env overrides.

### walk.py (NEW — shared pieces + checks; the old `solve/grade/doors/stairs` repair loop was DELETED, WALK_OLD is gone)
`walk_cells`, `base_q` (ceil(ground/0.8) rounded up to even), `rooms_of`, `carve`, `edge`/`connected` (123: flat edges
equal, a stair only at its foot from behind and its head onward; side-by-side only the same flight), `check` (139: BFS
from the arrival → `L.reached`, fails for doors/shops/cells/stairs; a stair passing a door sideways fails the door),
`ground_y`, `green_paths`, `_ramp_y`, `physical` (286: from the PLACED records — paving height or the piece's
pieces.json `ramp` quads turned by kit rot; centre-to-centre, `STEP` 0.3 m per shared edge and doorway; `blocked` edge
set from openings; `L.phys_reached`, `L.phys_h(c, rot|None)`; returns stats incl. `arrival` neighbourhood dump).

### openings.py (NEW — the capsule clear box)
`CLEAR_W` 1.0, `CLEAR_H` 2.2, `STEP_LIFT` 0.35 (box starts above the floor), `EPS` 0.02.
- `geometry(pieces)` (44): per piece the collision triangles — pieces.json `frame` boxes where present (`_framed`), else
  the kit.glb mesh (read with `check/kitglb.py`); for door-ish pieces the leaf/handle/glass materials (`wk_frame`,
  `wk_metal`, `wk_glass`) are dropped; `_door_geo` = wall + trim only, used when a piece is tested AS the doorway.
- `Scene` (112): records → world triangles (face mount +1.5 Z, corner +1.5 X/Z, kit rot about Y, y from level+quarter or
  DECK); `FLOORISH` kinds (ground, stair, water_edge, interior, ceiling, slab, bridge) are floor, not obstacles.
- `scan` (170): every pair of `phys_reached` cells joined on the walk + every door (0.5 m into the house); a `pass_kind
  == "door"` piece on a crossed face counts as blocking (closed door between two ways) — walk-through only into the room.
- `fix` (315): decoration (`REMOVABLE` kinds overlay/decor/sign/cell) dropped; walls never removed — swapped: door/portal
  → kept and counted as `kit_door_too_small` (now empty since the frame boxes), arch/gate → `wall_arch_round_*`,
  shopfront → `wall_shopfront_a_*`, else `wall_window_m_*` → `wall_plain_*`; roof → `roof_tin`/`roof_terrace`; towers,
  bridges etc. kept (`structure_kept`). Stats in `physical.openings`.
- `occupied` (234): walk cells whose middle a structure stands in → off the walk (`landmark_cells`).
- `prune_graph` (249): the RUNTIME walk graph (`units.walk_graph`, `L.walk`) against the same collision: ground edges
  the scan blocked, roof nodes with a solid piece in their box (shacks, tanks), level roof crossings/planks with
  something in the box (parapets), and their ladders/planks removed from the records. Stats `physical.graph`.
- `is_door_piece`.

### make_warren.py — pipeline order now (lines 95–140)
`pick.run` (→ `walknet.solve`) → `units.make_units/balance_homes/walk_graph` → ladders/planks (deduped) → `kitmap.translate`
→ `walk.physical` (for `L.phys_h`) → `openings.fix` → loop ≤3× {`kitmap.budget`, `openings.fix`} → `occupied` →
`scan` → `L.doors_blocked` (doors blocked by anything but their own door piece) → `walk.physical(blocked=…)` → stats →
`prune_graph`. Stats keys added: `walk_check` (see §6), `duplicates_removed`. `WALK_DEBUG=1` prints BLOCKED DOOR/EDGE.

### pick.py
- line 115: calls `walknet.solve` only.
- Ground paving block (~240–280): graded paving at level+quarter (never DECK), `_skirt` where a neighbour is lower,
  plinth stacks (retaining) where a drop > 0.6 m and no stair climbs it, kerbs/kerb_posts at water, stairs from `L.stair`
  (`step_low_4` for rise 1, `steps` for 2 — walknet only makes rise 2), `civ.steps_map` applied.
- `arch_mouth` emitted at the paving's edge height (a stair head is +2 quarters).
- Interiors emitted once per cell (`entered` set).
- After `civ.marks`: kerbs removed where a bank flight goes down into the water (`L.kerb_skip`).

### units.py
`walk_graph`: `L.edge_extra` (edge index → ladder/planks), `L.walk_index`; nodes marked `"blocked"` by prune_graph.
`make_units` skips lots without a door (unchanged behaviour; annexed lots have `cells = []`).

### kitmap.py
- `put()`: `_skirt` falls back to the plain civ paving when the kit has no skirted twin (fixes 17 missing cells on
  cycladic `pave_slate_whitejoint_skirt`); same in the `kit_id` path.
- End of `translate`: exact-duplicate filter on `(kid,i,j,lv,rot,flags,mount)` (planks on `(kid,i,j,lv,mount)`),
  `L.dup_removed`.
- `budget` (401): after the SHED stages, two more: heaviest overlay/decor/sign/crown dropped, then interiors dropped and
  rich walls → `wall_plain_*` (never doors). The loop in make_warren re-runs openings.fix after each budget pass because
  budget's own swaps can re-block an opening.

### civ/
- `family.py`: `bank_steps` marks now stand IN the water cell at the bank's graded level (toward_water flights hang down
  from y 0; plain `steps` rise out of the water), `L.kerb_skip` set; `fountain`/`stalls`/`plan_piece` keep off
  `L.keep_clear` (door steps, stairs, their feet/heads); `civic_tower` not on any door cell.
- `maghrebi_medina.py`: fountain/stalls off keep_clear; minaret not on a door cell.
- `saharan_kasbah.py`: ghorfa cells on greens, not courts. `knights_harbour.py`: `steps_map` → stair_knight removed
  (2-cell span overlapped the next cell). `cycladic/hakka/caucasian/nouvelle_france.py`: decor stairs-to-nowhere removed
  (earlier this round).

### writer.py / assemble.py / FORMAT.md
Format v3 (quarter bits 6–7 of rot_flags, mount bits 4–5, y = 3.2·level + 0.8·quarter, ground pieces non-DECK) — written
and documented earlier this round; nothing pending there. Foliage climbers: face plane + yaw (runtime request 2, done).

## 4. Commands

```
cd /home/deck/goblin-engine
P=~/.venvs/ssc-assets/bin/python
$P tools/sky/warren/make_warren.py --all --no-preview > /tmp/all.log      # ~16 min (954 s build time summed)
$P tools/sky/warren/lods.py                                                # ~2 min, run after EVERY regen
$P tools/sky/warren/make_warren.py SKY-078:rajput_sandstone --no-preview   # one island (family from assign.json), 5–60 s
$P tools/sky/warren/check/placed.py SKY-071        # coincident floors / duplicates per cell
$P tools/sky/warren/check/coplanar.py …  check/deck.py …                     # runtime's checkers (see their headers)
WALK_DEBUG=1 $P tools/sky/warren/make_warren.py SKY-071:kowloon_walled --no-preview 2>&1 | grep "FAILED\|BAD\|BLOCKED"
```
Family per island: `godot_project/remake/sky/warrens/assign.json` → `assign[id]`. Output per island:
`godot_project/remake/sky/warrens/SKY-xxx.json` (stats + sidecar) and `.bin.gz` (records, FORMAT.md v3).
A helper that prints walk stats for several islands lived in the job tmp dir (`one.sh`); trivial to recreate: run the
island, parse the `SKY-xxx {...}` line, print `walk_check`.

## 5. Open tasks (nothing is known-broken; these are the follow-ups)

1. **Sealed lots — DONE** (0 left). Fallback order implemented in `route_lot`/`solve`: flat/stoop at a floor → side/back
   face → porch → yard → ripup radius 2/4 → storeys added for sunk houses → annex to the touching neighbour with a shared
   storey (`lot["annex_of"]`; cells moved to the host lot, lot gets no unit) → garden (`lot["garden"]`, rooms cleared,
   cells PASTURE). Fallback (c) "lower the floor" is NOT implemented — the annex step absorbed the cases. If the user
   wants fewer annexes (160), add it before the annex step (clear the ground storey, move `gk`… note `L.gk` is derived
   in lattice.py:102 from the deck, so lowering means removing room level gk and re-pointing `rooms_of`).
2. **SKY-081 tri budget — DONE** (extra shed stages in `kitmap.budget`; max is exactly 25,000 on several islands, i.e.
   the budget is binding and the new stages are shedding interiors/wall detail there — check visually).
3. **Unsupported rooms — DONE** by removal (54). The coordinator preferred columns/arcade piers/sottoportego; nothing of
   that kind exists in the kit — a KIT request if wanted.
4. **Overlay cells / parapets / doors (runtime sweep item) — DONE in the generator's graph** (`prune_graph`): roof shack
   /tank/AC cells are `"blocked"` nodes, parapet-crossing roof edges cut, door pieces block a ground crossing unless the
   crossing is INTO the door's room (scan treats a `pass_kind == "door"` face on an edge between two walk cells as closed).
   Not verified in game yet — the runtime should re-sweep SKY-071; `walk_components` will show roof pockets cut off (10
   islands have small extra components: those are roofs now reachable only by their stair core, or none — a next step is
   to drop the ladders/planks that lead only into a blocked pocket, or re-link via a different roof route).
5. **Physical check = runtime collision — DONE as far as pieces.json goes**: `frame` boxes for the 35 walk-through
   pieces, meshes for the rest, `ramp` quads for stairs, overlays solid. If the runtime builds collision differently for
   any kind (e.g. convex hulls of overlays), align `openings.FLOORISH`/`Scene.__init__`.
6. **SKY-078 arrival (cells 75–76, 44)** — in the new layout the arrival is (77,36) at q 2, flat plaza all round
   (`physical.arrival` in its stats); cells (73–76, 43–46) are now a bank with `steps_up` on (74,43)/(74,44)/(75,43)/
   (76,44) at level 0 quarter 2 rising to the lane, kerbs on (74,44)/(76,44)/(77,42–43), plinths beside. The graph and
   physical checks pass there, but it is exactly the "stair beside a kerb with plinths" shape the runtime complained
   about; a kerb piece on a stair cell's side is harmless to the check (kerb kind water_edge = FLOORISH) but the kerb on
   (74,44) sits ON the stair cell — worth an in-game look. If it still traps the player, forbid stairs on BANK cells in
   `Net.stair_ok` (`L.plan[c] == BANK → None`).
7. **Shared door now 1.1 × 2.35** — nothing in the layout assumes a door size; the only size assumptions are
   `CLEAR_W/CLEAR_H` and `STEP_LIFT` in openings.py and `STEP` in walk.py. `kit_door_too_small` is empty on all islands.
8. **Openings still blocked after fix: 10 edges** across the run (`edges_blocked_after`); they are excluded from the
   walk and the graph (`L.walk_stats.physical.openings.still_blocking` names the piece). Find with
   `grep -o '"still_blocking": \[[^]]*\]' godot_project/remake/sky/warrens/SKY-*.json | grep -v '\[\]'`.
9. **Visual**: 3,627 decor pieces removed and 4,415 swapped for the capsule box — shopfront_b (awning at 2.05 m over the
   lane) is the biggest; a KIT `wall_shopfront_b` with the awning at ≥2.3 m would give most of them back.

## 6. Reading the walk check in an island's stats (`SKY-xxx.json` → `stats.walk_check`)

```
doors / doors_reached           lots with a door / reached on the walk graph (walk.check)
shop_cells / shops_reached      shop cells kept where the street meets the floor
public_cells / public_reached   PUBLIC_W plan classes (rim, bank, green, pasture, main, plaza, gate, lane, reserved, artery)
stairs / stairs_both_ends       L.stair entries / with foot and head connected
stoops porches yards storeys_added annexed gardens unsupported_removed carved planted_cells  (walknet fallbacks)
raised_cells fill_mean_m fill_max_m   fill over base_q
lots_without_entrance no_entrance_why no_entrance_n   must be 0 / []
failures {doors:[(lot,c,m)], cells:[c], stairs:[c], shops:[]}   first 8 each
pass                            the graph check
physical: doors/doors_reached public_cells/public_reached no_surface no_surface_at door_failures arrival pass
          openings: edges_blocked_before doors_blocked_before pieces_swapped pieces_removed edges_blocked_after
                    doors_blocked_after kit_door_too_small structure_kept culprits still_blocking
          landmark_cells
          graph: graph_edges_cut graph_nodes_blocked ladders_planks_removed
```
Top-level `walk_nodes/walk_edges/walk_components` are the RUNTIME graph (`units.walk_graph`) after pruning.

## 7. Gotchas a new agent would otherwise rediscover

- The old repair loop (raise the lower side of every blocked edge, iterate) ratchets whole hillsides up 8–19 m on hilly
  islands and never converges on some — that is why walknet exists. Don't resurrect it (it's deleted; the file at
  `/home/deck/.claude/jobs/204e5d66/tmp/walk_before_prune.py` is the last copy, job dir is temporary).
- `base_q` rounds to EVEN quarters: the ground is half-storey terraces, every rise a `steps_up` (1.6 m). `step_low_4` is
  no longer produced by the layout (pick.py still handles rise 1 if something sets it).
- Doors: `lot["door"] = (house cell, rot toward the street)`, `lot["door_k"]` = storey; the step outside is
  `m = c + FACE[rot]`; the door piece record is face-mounted on the house cell with kit rot `(rot+2)&3`.
- `FACE = {0:(0,-1), 1:(-1,0), 2:(0,1), 3:(1,0)}` (generator) and kit rot = generator rot + 2 (ACROSS pieces +1) — see
  kitmap.put. `openings.Scene.world` uses kit rot about +Y with world x along i, z along j, 3 m cells.
- `L.stoop[m] = (rot toward the door, 2)`; `L.door_feet` = porch stairs whose foot is the door itself (walk.check's
  foot_ok exemption). After solve, stoops are recomputed from the final fixes, so trust `L.stoop` not state["stoops"].
- Per-island build time 0.2–60 s; hk_neon_canyon/karachi are the slow ones (ripup).
- `kitmap.budget` is binding (≤25k) on ~45 islands; its late stages strip interiors — if the game looks bare in dense
  chunks, that's why.
- pieces.json top level: `{"pieces": {...}, "palettes", "slots"(list), "frames", "units", ...}` — always index
  `["pieces"]`. `pass`/`frame`/`clear`/`foot`/`pass_kind` on 35 pieces, `collide: "frame"` on those, `"ramp"` on 15.
- The KIT status map is `research/sky_islands/warrens/kit_status.md`; `kit_requests.md` is generator-owned (overwritten
  by `kit_requests.py`); `runtime_requests.md` is runtime-owned.
- Memory note for the user's persistent memory already added: `~/.claude/projects/-home-deck/memory/ssc-sky-islands.md`
  (last bullet) — update it if walknet changes shape.
- Don't commit, don't launch the game, don't run `godot --import` (coordinator rules for this fork).

## Log (newest last)
- 10-15 after all7: walknet `Net.bank` — no stairs on bank cells / cells beside water (SKY-078 75–76,44 is now flat
  bank paving; the steps_up left at (74,43),(75,43) are the rajput bank_steps IN the water cells, decor). Fixed a
  KeyError in route_lot's yard branch (yard start looked up by the path's last cell; now by `(c,q) in N.yard_meta`).
  Rerun all9 (`--all` + `lods.py`) RUNNING → next: read totals from all9.log (script in §2 style), update §2, report.
- all9 done: walk 98/100 (SKY-032, SKY-075 one stair each whose run-partner was flattened), physical 100/100, 0 sealed lots.
  Fix: walknet.solve final pass flattens stairs whose foot/head no longer connect (before the reachability step).
  Rerun all10 RUNNING → next: totals, report.
- 10-16 all10 DONE (+ lods.py exit 0): walk 100/100, physical 100/100; 42,440/42,440 doors, 152,475 public cells all
  reached, 4,620 stairs all both ends, 0 sealed lots (919 stoops, 136 porches, 8 yards, 21 storeys added, 172 annexed,
  9 gardens), 0 unsupported (59 removed), max chunk 25,000, fill mean 0.30 m. Openings: 7,833 edges + 2,585 doors blocked
  before, 11 edges / 0 doors after. Runtime graph: 3,810 edges cut, 1,334 roof nodes blocked, 644 ladders/planks removed;
  10 islands have small cut-off roof pockets. Nothing half-finished. Next: runtime re-sweeps SKY-071 / re-walks SKY-078;
  optional: drop ladders into cut-off roof pockets; KIT shopfront_b awning ≥2.3 m.
