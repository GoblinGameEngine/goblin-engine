# Frame rate aboard the sky islands, and on the ground (2026-10-14)

The user:
> We need to work on the framerate again. Onboard the islands it is slow and there is really bad flickering at night.
> ... This all needs to run smoothly. We can use our LOD model trick to make distant islands less stressful. Likewise
> at the altitude of the islands, we don't need models for the ground, only textures. Find what I missed and get it
> to 60fps onboard the islands. It also needs to look good. Be more granular about what gets LOD models. See where we
> don't need to render the interior of buildings. Use tricks like lens flare and reflections to hide building
> interiors, but only where necessary.

## Measured (aboard Lumen, SKY-041, at night)
- Settled: 37–46 fps. GPU 8–11 ms, and process time is the main cost. Turning off SkyIslands' physics step gives
  70 fps (`_place_islands` takes ~2.3 ms per tick: moving the near islands' ~8k nodes, several ticks a frame).
- Node counts per near island:
  - a parked lark: 137 nodes, 58 meshes, 6 bodies, four per island;
  - full-detail buildings: up to 3,400 nodes;
  - the fence body: 100–300 box nodes;
  - props, hubs and pads: 170–300 nodes;
  - bridges: up to 740 nodes and 280 bodies.
- Night flicker fixed: lod_vc.gdshader hashed its panes in world space, which reshuffled every frame on the moving
  islands. It now hashes in the mesh's own frame.

## Note
The islands' BUILDINGS are being redone from scratch: one generated warren city per island
(research/sky_islands/warrens/). Don't tune the current SKY-<style> buildings. Make the systems around them cheap,
and design the hooks so a city made of merged chunk meshes plugs in.

## The game lock (one instance at a time)
Before launching the game, create `/home/deck/goblin-engine/reference/tmp/game.lock` holding your stream name and
the game's PID, only if the file doesn't exist. If it exists and isn't yours, wait and poll every minute. When done
(each session at most ~15 min), kill your game by its exact PID and delete the lock.
- Launching with `cd x && godot &` makes `$!` the subshell's PID: use `(setsid nohup ../godot/godot4 --path . > log 2>&1 &)`
  and find the PID with `pgrep -x godot4`, checking it's the one you started.
- A headless godot run rewrites the DevBridge token, so run headless only while holding the lock.
- Never `pkill -f` or `pgrep -f | kill`: the user may be running the exported game themselves.
- The gcmd screenshot path must be absolute.
