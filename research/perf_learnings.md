# Performance: what we learnt (2026-10-14/15)

From getting the sky islands from 37–46 fps to 80–107 fps aboard (Steam Deck, vsync off), and from the night-lighting
and interiors work. Measured with the in-game monitors (Performance TIME_PROCESS and TIME_PHYSICS_PROCESS,
`RenderingServer.viewport_get_measured_render_time_gpu` with measuring enabled, draws and primitives) and the
Prof/PerfProbe sections. These rules apply to the whole engine.

## Results
| Where | Before | After |
|---|---|---|
| Aboard Lumen (SKY-041), night | 37–46 fps (5–8 fps while its contents built) | 81–86 fps, GPU 7.7 ms, ~925 draws |
| Aboard Hobnob after fast travel, night | — | 91–107 fps, ~1,250 draws |
| 900 m over Calder, night | 25–84 fps, 213 draws | 117–139 fps, 64 draws (aloft mode) |
| Playa Verde, night | — | 63.5 fps |
| Calder, night | ~42 fps | ~42 fps: CPU-bound by traffic (4–8 ms) and people (~2 ms) |

## The lessons
1. **Moving a node tree costs per node, every tick.** Setting the transform of a parent with thousands of
   descendants re-propagates through all of them: each mesh instance updates its rendering-server transform, and each
   collision body updates in the physics server and broadphase. A near island had about 8,000 nodes, and placing the
   islands cost 2.3 ms a tick, several ticks a frame at low fps (a spiral). The fixes:
   - **Fewer nodes:**
     - merge static meshes per island (props went from hundreds of nodes to 2 meshes);
     - put collision shapes on their body, not as hundreds of `CollisionShape3D` children (a fence went from
       100–300 nodes to 1);
     - draw parked vehicles as one MultiMesh impostor (a parked lark was 137 nodes);
     - keep collision only near the player (`DISABLE_MODE_REMOVE`).
   - **Fewer updates:** step the simulation at 10 Hz and interpolate transforms. Place far islands every fourth tick,
     staggered, and always place the one the player is on.
   - **The plan for warrens:** draw merged chunks as RenderingServer instances, not scene nodes. That's about 60
     nodes per near island.
2. **Measure the settled state, not the first seconds.** An island building its contents (threaded loads and kit
   merges finishing on the main thread) dropped to 5–8 fps for a few seconds; settled, it was 37–46 fps. Spread
   builds over frames with a time budget.
3. **Bisect by switching systems off** (`set_process`, `set_physics_process`, visibility) and watch process, physics
   and GPU time separately. The cost is usually not where it seems. The aloft-ground switch saved little aboard an
   island, because the islands themselves were the cost; turning off SkyIslands' physics step showed it at once.
4. **Cheap rejects before expensive per-object work:**
   - `frame_at`, called by 99 parked aerostats every tick, looped all 100 islands; an altitude test rejects them at
     once.
   - The snow check sampled ten points against every cloud; one distance test first makes it nearly free.
   - Cloud steering moved from a once-a-second burst to a few clouds per frame.
5. **Don't draw what isn't seen:**
   - **Aloft**, above 450 m, the floor is the far-side images: no ground buildings, trees, roads, traffic, people or
     transit. That gave a 2–5× gain over a town.
   - **Interiors:** furniture is a separate interior mesh drawn only near the building. From outside, windows are a
     reflection over a fake lit room (interior mapping in the building's own frame) with curtains. That gave −250
     draws and −150k triangles in Calder.
   - **LOD by size:** full detail at `clamp(36·k, 26, 55)` m, so small buildings switch early.
6. **Night costs are their own budget:**
   - Every real light adds per-cluster work; there are 28 pooled OmniLights for street lamps and no per-sign lights.
   - Emissive materials with bloom do the rest.
   - Car lights add about 1,000 meshes at night in Calder (not yet fixed).
7. **Flicker:** a shader that hashes in world space (lit or unlit window panes) reshuffles on anything that moves.
   Hash in the mesh's own frame (`VERTEX`, `NORMAL`, and the world up taken into the mesh frame).
8. **Light that ignores walls:** shadowless omni lights inside buildings also light the outer walls nearby. Gate room
   lights by distance or by the player being inside, and check the material first: the screen-mesh material
   (alpha 0.35) was being treated as window glass.
9. **Emission seen at grazing angles:** baked night-light halos on the coarse ground near a town made a blinding
   horizon band. Show the baked lights only where the real ones aren't drawn (beyond flat_arc), and suppress halos
   close by.
10. **Test hygiene:**
    - A headless godot run rewrites the DevBridge token.
    - A release build's stdout is block-buffered; use `stdbuf -oL`.
    - `cd x && godot &` makes `$!` the subshell's PID.
    - Never `pkill -f` the game's name: it killed the user's own copy once.
    - Use one game instance at a time, under a lock file (`reference/tmp/game.lock`) when several streams test.

## What's left
- Calder is CPU-bound: traffic 4–8 ms (and its car lights at night), people about 2 ms.
- Bridge meshes mostly sit under moving parts, so they couldn't be merged.
- The round-2 island buildings (about 3,400 nodes on Lumen) are to be replaced by the warrens.
