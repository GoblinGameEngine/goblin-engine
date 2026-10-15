# Night lighting: brief (2026-10-14)

## The user
> We need to fix the lighting at night. The towns need streetlights. the south coast towns need colored lights in
> the trees by the beach and on the street along the beach. The buildings need to be nicely lit at night inside. The
> moonlight should illuminate the entire ring, not just the slice where the character is standing. We need to see
> lights baked into the farside texture. There needs to be good artificial illumination on the streets and in the
> cities and town centers. All streets with buildsings need lights.

## The survey (what's there now)
- There are no street lamps. StreetFurniture.gd was deleted (commit 7caa71423), and only the coastal walks have lamp
  posts (about 735, non-lit emissive boxes).
- Moon and sun: one DirectionalLight placed over the player (DaySkySystem). Ambient at night is 0.13.
- The far side is darkened to 10% at night (farside.gdshader), and nothing on it glows.
- Windows don't glow past about 55 m: gblod bakes glass as opaque GLASS_RGB (0.09, 0.105, 0.12) in LOD_VC.
- Interior omnis: 7 m range, 1.2 energy, always on, only in full detail.
- Reusable pieces: sky_wash (light pools), sky_bulbs (bulb sprites), sky_glitter, and sky_signs._path_lamps.

## Streams and ownership
1. **STREETS:**
   - `tools/street_lamps.py` → `godot_project/remake/street_lamps.json/.bin` (packed by pack_data).
   - `godot_project/scripts/world/StreetLights.gd`, new shaders `remake/shaders/street_*.gdshader`, one hook line in
     remake_station.gd.
   - Delivers:
     - lamps on every street with buildings;
     - denser, brighter and more ornamental lamps in town and city centres;
     - south-coast beach festoons along the beach streets, and coloured lights in the trees near the beaches;
     - bulbs, light pools and a pool of real OmniLights nearest the player;
     - night only.
2. **SKY:**
   - Owns DaySkySystem.gd (night lighting), farside.gdshader, far_side.gd, terrain_cover.gdshader (night terms only)
     and `tools/farside_night.py` → `remake/farside/n_SS_XX.*`.
   - Delivers moonlight over the whole ring, and night lights baked into the far side.
3. **BUILDINGS:**
   - Owns building_loader.gd (night/LOD materials, interior lights), lod_clusters.gd (light fade) and a new
     `remake/shaders/lod_vc.gdshader`.
   - Delivers interiors nicely lit at night, and windows glowing at every distance (LOD_VC glass is detected by its
     vertex colour).

## The game lock (one instance at a time)
Before launching the game, create `/home/deck/goblin-engine/reference/tmp/game.lock` holding your stream name and
the game's PID, only if the file doesn't exist. If it exists and isn't yours, wait and poll every minute; never kill
another stream's game. When done (each session at most ~15 min), kill your game by its exact PID and delete the lock.
Any headless godot run rewrites the DevBridge token, so do headless runs only while you hold the lock (or with no
game running). Never `pkill -f` or `pgrep -f | kill`: the user may be running the game themselves.
