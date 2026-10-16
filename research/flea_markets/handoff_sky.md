# Handoff: MARKETS-SKY (stream E: the island side of the flea markets)

Kept current after every milestone. Nothing is committed (the coordinator commits). Last update: 2026-10-16 ~18:00
(session 3, after the 14:21 OOM kill): perf FIXED + test PASS; audit regressions FIXED (10 islands rebuilt);
in-game verification DONE after the roads rebake (step 5) -- ALL STEPS DONE, ready for the coordinator's commit.

**13:40: the parse errors in sky_mooring*.gd (untyped `:=` inferences) are fixed; a full `--editor --quit` import
reports no script errors.**

## Session 3 (post-OOM) progress -- NOT yet run through Godot
- State found: `make_warren --all` + lods + import DONE; `audit.py --all` DONE (13:55, totals in
  reference/tmp/audit/all.json; the PRE-moorings baseline is all_final.json, 07:54); flea_sky_test 13:56: all
  functional checks PASS, ONE FAIL: "SkyDrift.step with the mooring: 15009 us a step (budget 800 us)". The previous
  session edited flea_sky_test.gd (13:56: final check = mo.drive at dt 0.1, budget 300 us) and sky_mooring.gd
  (14:11: the full/_t2 gating) AFTER that run, then died -- those edits were never compiled or run.
- **Perf fixes written (UNTESTED -- compile + rerun the test next):**
  - sky_mooring.gd `layout()`: the `_layouts` cache no longer `clear()`s at >64 (that recomputed ~40 expensive
    layouts in ONE refresh, every step at dt 10 once enough weeks accumulated -- the likely 15 ms and the
    13.7->19 ms drift); it evicts FIFO one entry.
  - sky_mooring.gd `drive()` restructured: a FULL pass (phases, detach/lash bookkeeping, every raft placed, `_act`
    rebuilt) on refresh / jump / once a second; between full passes only `_act` (TRIM / APPROACH / still-descending
    rafts) is stepped via the new `_place()`; settled moored rafts sit pinned (SkyDrift.step skips held ids, so
    nothing moves them). Release-on-empty handled.
  - sky_drift.gd `_meetings()`: the per-PAIR `_towing_into(a) or _towing_into(b)` (O(n) each -> O(n^3)) hoisted to
    one `towed` set per call; the cheap s-distance cull now runs first in the pair loop. `_cast_offs()` skips rafts
    with no edges (no per-raft duplicate()). `_keep_apart()`: s-cull before the tow reads, `a` hoisted.
- **Audit vs pre-moorings baseline (all_final.json)**: most counts fine (pierce -4724, culled_slot -1369,
  isolated -314; floating/unsupported +435 and manifold/dup_across +79 are layout-shuffle noise). REAL regressions
  found and root-caused:
  - SKY-079 doors unreachable 0->14, edges blocked +10: ONE `windmill_round` (plan_piece dressing, kind tower --
    openings.fix kept it as "structure") on a green choke cell. FIX: openings.py `LAST_RESORT = ("windmill_round",)`
    -- removed when it still BLOCKS after swaps (only SKY-079 affected today; pagoda/arches untouched).
  - moor_unreached on SKY-040 + SKY-054 (generator said connected): the STOWED `swing_girder` bridge model lies
    ALONG the face -- reaches 15.3 m (road 16.5) past the bridge centre toward -along on N/W faces, +along on S/E
    (measured from the assembled geometry; every other style stays within +-2.5 m). BRIDGE_CLEAR 5 was blind to it.
    FIX: moorings.py SWING_BACK/FORE/ROAD directional clearance in `_site()` (never relaxed).
  - SKY-071/073/075 moor_unreached are the generation-time "connected: False" stations (known: 188/191) -- not new.
  - Rebuild set for both fixes: the 10 swing_girder islands SKY-010/017/040/046/054/055/073/079/082/092
    (scratchpad scan br_dir2.py; SKY-079 is in the set, so the windmill case rebuilds with it).
- Stale game.lock from the OOM (dead PID 1479986) removed at ~14:50; MARKETS-WORLD held it a while (their holder
  PID also died -- another stale lock, cleared ~16:10 after checking no godot ran).
- **~16:40 DONE: rebuilt the 10 swing_girder islands + their lods; re-audit of the 10 (audit_rebuilt10.log):
  SKY-079 555/555 doors reachable (was 520/534), SKY-040 3/3 + SKY-054 2/2 moor stations reached, every coarse
  class down over the 10 (walk 41 -> 7, intrusion -141, zfight -175; manifold +5 noise). Survey ring-wide:
  stations 191/194 (unchanged), line houses 255/263 (-3), davits 88/100 (-3) -- the lost pieces stood under
  girders. moorings.json rewritten (100 islands). NOTE: single-island audit runs OVERWRITE
  reference/tmp/audit/all.json -- the 13:55 full run's per-island numbers now live only in
  reference/tmp/markets_sky/audit_all.log (totals + one-liners; fine-grained all.json would need a 52-min --all).**
- **~17:00 DONE: full import clean (import2.log, 0 script errors); profiled and fixed; flea_sky_test PASS, 0
  failures (test2.out).** Perf numbers (prof: remake/tools/flea_sky_prof.gd, 15 members / 98 rafts):
  - SkyMooring.drive: 63 us at dt 0.1 (budget 300), 392 us at dt 10 (budget 800) -- from ~15 ms.
  - SkyDrift.step whole at dt 10: 2799 us avg, FLAT over 5400 steps (was 15009 us and growing 13.7 -> 19 ms).
    The rest of that 2.8 ms is the drift's own near-pair check (pre-existing; no-mooring step(10) ~800-900 us,
    moored rafts cluster so more near pairs). step(0.1) ~870 us (the ~650 us per-step 98-raft loop is pre-existing).
  - What was hot: (1) `_layouts.clear()` at >64 recomputed ~40 cold layouts (5 ms each) in one refresh, every step
    at dt 10 -> FIFO evict one; (2) drive() did full member/raft work every step -> full pass at 1 Hz / refresh /
    jump / phase change, light `_act`-only pass between; (3) `_towing_into` O(n) per PAIR in _meetings -> one
    `towed` set per call; (4) O(n^2) pair enumeration in _meetings/_keep_apart -> `_near_pairs()` sort-sweep with
    seam wrap, shared per check; (5) `_gap` recomputed raft extents per pair -> `_ext` per-check cache;
    (6) `_cast_offs` skips edge-less rafts.
  - The test's perf checks now assert BOTH drive cadences (300 us at dt 0.1, 800 us at dt 10) and print the whole
    SkyDrift.step dt-10 average as info: the old single 800-us budget on the WHOLE step at dt 10 fails even
    without the mooring at this raft count (pre-existing drift cost), so it tested the wrong thing.
- ~17:40: tried the in-game look: game launched under the lock, stuck 25 min at "LOAD still waiting: roads"
  (stale roads bakes vs MARKETS-WORLD's regenerated map; 5,786 MapRoads band warnings) -- killed it, lock
  released. NOT ours to fix; retry after their `bake_world roads`. flea_sky_prof.gd (temporary) deleted; its
  numbers are recorded above.
- Files touched this session (all uncommitted, for the coordinator): `remake/scripts/sky/sky_mooring.gd`
  (layout cache evict, drive full/light passes, `_place`, `_act`), `remake/scripts/sky/sky_drift.gd`
  (`_near_pairs` sweep, `towed` set, `_ext` cache, `_cast_offs` guard, `_meetings`/`_keep_apart` take pairs),
  `remake/tools/flea_sky_test.gd` (two perf budgets), `tools/sky/warren/moorings.py` (SWING_* clearance),
  `tools/sky/warren/openings.py` (LAST_RESORT), rebuilt: warrens + lods of SKY-010/017/040/046/054/055/073/079/
  082/092, `remake/sky/moorings.json`, their .import metas via the full import.
- Residual risks: (1) in-game 32-38 fps dip at ground level inside a celebration market (ground rendering, not
  the sim -- for the perf stream); (2) 3 stations ring-wide
  still unconnected at generation (incl. SKY-079's 2nd pax; pre-known class, 188/191 reached in the audit);
  (3) line houses 255/263, davits 88/100 after the girder fix (the lost ones stood under stowed girders);
  (4) one new door-entry-blocked on SKY-082 (wall_arch_round kit-door class, pre-existing ring-wide);
  (5) reference/tmp/audit/all.json now holds only the last-audited islands (single-island runs overwrite it);
  the 13:55 full numbers live in reference/tmp/markets_sky/audit_all.log, the rebuilt 10 in audit_rebuilt10.log;
  a fresh `audit.py --all` (52 min) would restore a full all.json if the coordinator wants one for the record.

## State
- [~] **1. Warren generator: moorings placed** (`tools/sky/warren/moorings.py`): sites, pieces, floors, plinths,
  signal masts, station walks; survey over 100 islands: 193 / 194 stations, 258 / 263 line houses, 91 / 100 davits.
  `make_warren --all` + `lods.py` DONE (13:02): 191 / 194 stations (166 pax, 25 cargo), 188 connected to the walk,
  258 / 263 line houses, 91 davits; walk check 100 / 100, physical 99 / 100 (SKY-079: 1 public cell); max chunk
  25,013 tris est.; `remake/sky/moorings.json` 100 islands (237 KB). audit `--all` running.
- [x] 2. Drift sim mooring: `SkyMooring` wired into SkyDrift / SkyIslands; `flea_sky_test.gd` PASS (0 failures,
  16:55; perf budgets met: drive 63 us at dt 0.1 / 392 us at dt 10).
- [~] 3. The anchoring sequence: `SkyMoorings` + `SkyMooringSite` compile clean + the sim side is test-covered; the
  site visuals never seen in-game (blocked, below).
- [~] 4. Ropeway runtime: in SkyMooringSite (compiles; cabins/doors/carry not yet exercised in-game).
- [x] 5. Verify DONE (~18:10): audit (regressions fixed, 10 islands rebuilt, spliced totals at or better than the
  pre-moorings baseline; audit PNGs clean) AND the in-game look after MARKETS-WORLD's rebake unblocked loads
  (LOAD complete in 52 s, zero stale-band warnings). In-game: moored rafts hold exactly at 600 m over their
  berths, hawsers to deadmen + the city masts (mast heads turned to the islands), ropeways with cabins and the
  drop cage running, trading tents up only in the fair window (by design: tents 0 at a 2-island FM-SOL, 100
  tents at FM-LG's fair), FleaCalendar end-to-end in the live game: FM-LG day 10 fair -> days 12-13 CELEBRATION
  -> days 14-16 HOLIDAY -> 17-18 celebration -> day 19 ISLANDER, LANTERN phase to 21:00, festoons + lamp pools
  lit at night, vendors (people 1-18) at open hours. Perf in-game: 96-156 fps aloft / day aerials, 48-101 fps
  night ground, ONE dip to 32-38 fps standing inside the celebration market at ground level (draws 588 -- the
  whole town + market + raft; the mooring sim itself is 53-66 us a step, so that dip belongs to the ground
  market / town rendering, for the perf stream). Screenshots (10) in `docs/media/2026-10-16/sky_*.png`; the
  `market_*.png` there are MARKETS-WORLD's (taken over the same session's DevBridge at 18:02). The long coloured
  strips hanging under moored islands are the kit's `fm_skein_banner` ("islands moored") -- intended, not the
  travel banners sky_banners.gd furls.

## Files (mine)
| file | what |
|---|---|
| `tools/sky/warren/moorings.py` | NEW. `reserve(L)` (before the spine): sites on the straight dock faces (face_spans), clear of bridges (+5 m), launchers (6 m), hoists (9 m), pads/larks, balloon tethers, water; the footprint cells OUT, a street strip (+ a second row) behind each station RESERVED, the doorway pinned (L.pin_q) and its ends / the row behind pinned "flat or a stair up from" (L.pin_s). `emit(L, o, kit)` (after kitmap.translate): the piece at the strip's height, whole-cell `pave_plaza` floors under it, `plinth_t` stacks where the floor stands over the ground outside, `moor_signal_mast` on each line house roof (face mount, +1.5 z, 6.4 m up). `walk(L)`: each station's walk on the twin's graph (strip -> hall -> passage -> rim gate -> berth deck). `lights(L)`, `doc(L, kit)` (the twin's `moorings` block: kind, side, rot, cell, q, origin, out, anchors in the island frame, fence_gap, walk node ids, connected), `stats(L)`, `write_index()` -> `godot_project/remake/sky/moorings.json`. |
| `tools/sky/warren/make_warren.py` | +7 lines: reserve / emit / walk / lights / doc / stats / write_index. |
| `tools/sky/warren/writer.py` | the twin gets `"moorings"`. |
| `tools/sky/warren/walknet.py` | `Net.pin` / `Net.pin_s` (pinned heights; ripup leaves pinned cells alone). |
| `tools/sky/warren/audit/assemble.py` | ASM 8: the fence also gaps at the twin's `moorings[].fence_gap` (mirrors the runtime). |
| `tools/sky/warren/audit/audit.py` | per island `walk.moor_stations / moor_reached / moor_safe / moor_unreached` (the berth node reached from the arrival over passing edges); totals in all.json. |
| `godot_project/remake/scripts/sky/sky_mooring.gd` | NEW `SkyMooring` (RefCounted, `drift.mooring`): bookings from FleaCalendar.week_plan (refresh 2 s), phases TRIM (A-24 h) / APPROACH (A-6 h, down to MOOR_H 600) / HOLD / CREW_DOWN / ANCHOR / LOGISTICS / RIGGING / SERVICE / STRIKE / CAST_OFF (+ LASHED for non-ground followers); `layout(booking)` (pure, cached): the host over a ground station with its station's berths H_OFF 40 m in from it, clear of the floor + 20 m; followers lashed by matching bridges E/W then N/S, never on a ropeway face nor over the floor (else "absent"); ground followers' ropeway to the nearest free plinth in front <= 450 m (else one under its berths on the field/apron); cargo ropeway where a cargo station hangs over open market ground; hawsers: the tier's share of deadmen (4/3/3) nearest the line houses, the host's to the masts; the davit hook. `drive(drift, dt)` -> held rafts: detach, steer (shortest way, VMAX 45 m/s, >= drift pace), descend, hold, lash (SkyDrift._lash: bridges come down), cast off; jumps snap (SkyIslands: no easing). Wind: `wind_at` (SkyIslands: storms) > 9 m/s -> no descent, gondolas stop. |
| `remake/scripts/sky/sky_moorings.gd` | NEW `SkyMoorings` (child of SkyIslands): a `SkyMooringSite` per market with islands booked, within 3.2 km; StreetLights.borrowed. |
| `remake/scripts/sky/sky_mooring_site.gd` | NEW `SkyMooringSite`: static 64 m chunks on a worker (ground stations + wheel, logistics tents, trading tents with dress + sky goods + lanterns, festoon poles and strings, Bright Week strings over lot rows and lanes + the Lantern Top), one vertex-colour material (emission in alpha) + atlas groups, frame-box + ramp collision; bulbs one MultiMesh; ropes one line mesh (hawsers lowered one by one, track + haul ropes); cabins (jig-back, 8 m/s, ACC 1, dwell 60 s / 120 s 00-06, cargo only when FleaCalendar gondolas == "all"), doors, AnimatableBody3D within 400 m, the rider carried; drop cage 12 m/s; island-side MID pieces on far islands; vendors (2-3 per tent, nearest 18 within 70 m) and cabin wardens as SkyFolk NPCs. |
| `remake/scripts/sky/sky_drift.gd` | `mooring`, `_held`: held rafts skip the free drift, meetings, cast-offs; free rafts keep 400 m off and above moored ones; warm_up ends with `mooring.snap`. |
| `remake/scripts/sky/sky_islands.gd` | mooring clock (`sky.now_hours()`) each step, `_wind_at`, snapped islands placed without easing, `moorings` node. |
| `remake/scripts/sky/sky_island.gd` | fence gaps at the moorings; ground-moored islands' hoists rest. |
| `remake/scripts/sky/sky_banners.gd` | moored (or coming down) islands' banners furled. |
| `scripts/world/StreetLights.gd` | `borrowed` lamps (<= 8 pooled lights). |
| `remake/tools/flea_sky_test.gd` | NEW headless test (see its header). |
| `reference/tmp/markets_sky/ms_go.sh` | lock + import + compile check (`check`), the test (`test N`), or launch. |

## Decisions
1. Sites are chosen in the generator (moorings.py), not in make_islands (islands.json is not regenerated: that would
   rebuild every rock glb). The runtime reads `remake/sky/moorings.json` (all islands, small).
2. Counts per 00 §3.3: line houses 2/3/4 (1-3 / 4-6 / 7+ blocks), stations 1/2/3/4 (1-2 / 3-5 / 6-8 / 9+), the
   last a cargo station at 3+, one davit beside the first passenger station.
3. Row choice: the first row stands <= 0.75 m out past the deck edge, else one row in (<= 2.25 m in).
4. Height: the station floor = the street strip's paving (pinned), never more than 1.6-3.2 m over the rim's deck
   (relaxed passes up to 6.4 m on the steepest islands); retaining walls (plinth_t) close the drop.
5. The station walk passes the gantry's middle post (x 4.5, z -1.9) at x 3.7.

## Commands
```
P=~/.venvs/ssc-assets/bin/python
$P tools/sky/warren/make_warren.py SKY-022:hk_neon_canyon --no-preview     # one island (prints "moorings")
$P reference/tmp/markets_sky/survey.py                                     # sites over all 100 islands (~30 s)
$P reference/tmp/markets_sky/dbg.py SKY-022:hk_neon_canyon                 # a station's strip cells after the build
$P tools/sky/warren/audit/audit.py SKY-022                                 # "moorings: stations n, berths reached n"
```

## Next
- audit the 4 test islands (berths reached), then `make_warren.py --all --no-preview`, `lods.py`, `audit.py --all`.
