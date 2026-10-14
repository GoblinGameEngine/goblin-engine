# API requests between the sky-island streams (2026-10-14)

## Generator -> LIGHTS (SkySigns)
1. **Sign kinds with underscores.** `_from_anchors` splits `sign_<kind>_<w>x<h>` on "_" and takes `parts[1]` as the kind
   and `parts[2]` as the size, so `neon_script` / `dot_matrix` / `neon_frame` can't be named.  The generator writes
   single-word kinds: `neon` (-> neon_script), `dotmatrix` (-> dot_matrix), `lightbox`, `chochin`, `brass`, `painted`,
   `blade`, `billboard`.  Please map `neon` and `dotmatrix` (else they fall to a random kind) -- or parse the size as
   the last `<w>x<h>` part and join the rest as the kind.
2. **Anchors live in the layout**, as SkySigns already reads them: `islands.json` `models[<id>].anchors` =
   `[name, x, y, z, yaw]` (the building's Godot frame; yaw about +Y, the sign's +Z out of its face).  Names used:
   `sign_<kind>_<w>x<h>` (storefronts at ~3 m, upper-floor boards, front-corner blades, rooftop billboards),
   `glow_floor_<L>` / `glow_crown_<L>` (runs along the anchor's +X), `lights_<n>` (pairs: across the parapet, across
   alternate floors).
3. New per-building fields in `islands.json` `buildings[]` (style models only): `shops` [{name, kind}] in storefront
   order (names from b_signs_and_light.md section 4), `mood` (hex), `style`.  `models[<id>]` also has `mood`,
   `signage` {kinds, density}, `pad`, `homes`, `blocks`.

## Generator -> RUNTIME (SkyIsland)
4. **Links** -- `islands.json` `islands[].links`: [{a, b (building ids), kind: skybridge | plank | covered_alley,
   from [x, y, z], to [x, y, z] (island frame, y the height at each end), width}].  Draw from shared parts (a deck, rails;
   a covered alley a closed box with windows), collide, and add them to the walk graph if the folk should use them.
   Roof links (skybridge, plank) run roof to roof (heights within 3.2 m: a sloped deck); covered alleys run wall to
   wall at a floor both blocks have (no doors are cut: they're facades' bridges).
5. **Lark cradles** now sit where the generator left a big main roof clear (`models[].pad`, placed per building into
   `pads[]`), not at the lot's centre.
