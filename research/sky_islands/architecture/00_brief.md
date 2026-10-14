# Sky island architecture: brief and contracts (2026-10-14, round 2)

## The user, 2026-10-14
> The aerostats are clipping through the building tops on the islands. Increase the top altitute for all aerostats to
> 2.5km. I want more variety in the buildings on the islands. Research different building styles around the world.
> Specifically look at Arabic Old Town architecture and Hong Kong and Tokyo and Delhi and Mumbai. Find building styles
> from each city, many examples. When you are satisfied, make shared components for the buildings, resuing as much as
> possible. Research spanish architecture. Make a model for ceiling tiles. When an architecture style does have tall
> buildings, find examples of stacked warrens. Find floor plans. Look at fantasy art. Arabic Old Town Warrens, things
> like that. Each island needs to be fascinating. They will have lots and lots of lights with billboards and flashing
> signs. At night they should light up like a christmas tree. These are commerce based societies, they will enjoyu
> advertising. These should be the most visually interesting parts of the map. Each store has it's own light up
> stylized sign. Each apartment complex has mood lighting and a stylish motif. Generate a wealth of styles and assign
> each to an island.
> (follow-up) then redo the buildings on each island to match its;s style

(The aerostat ceiling is done: RemakeAirVehicle.ceiling_h 2,500 m for every aerostat.)

## Order
1. Research (two streams), writing `research/sky_islands/architecture/`:
   - A: Arabic old towns, Spanish, Delhi, Mumbai.
   - B: Hong Kong, Tokyo, stacked warrens, fantasy art, signage and night light.
2. Merge into one style catalogue, `styles.json`, with 30+ styles. Assign one to each of the 100 islands; the canon
   records it.
3. Shared components (Blender, the kit), including ceiling tiles, and a sky-island building generator that composes
   them per style.
4. Regenerate every island's buildings in its style, then rebuild, import and verify in game.
5. Running in parallel from the start: signs and night lighting at runtime (SkySigns), driven by anchors the
   generator writes.

## Style catalogue entry (`styles_<stream>.json` → merged `styles.json`)
```
{"id": "sanaa_tower", "name": "...", "sources": ["Sana'a, Yemen", ...], "refs": [{"title":, "url":}],
 "typology": "tower_house|tong_lau|zakkyo|haveli|chawl|warren|courtyard|terrace|...",
 "massing": {"storeys": [min, max], "footprint_m": [[w, d] ranges], "stack": "none|setback|overhang|cantilever|pile",
             "stack_rules": "how upper volumes sit on lower ones", "skybridges": bool, "courtyard": bool, "lightwell": bool},
 "roof": ["flat_terrace", "crenellated", "dome", "pagoda_eave", "rooftop_shacks", "water_tanks", ...],
 "walls": {"materials": [...], "palette": ["#hex", ...]},
 "openings": ["mashrabiya", "roshan_bay", "jharokha", "cage_balcony", "louvre", ...],
 "components": ["<component id>", ...],          # from the shared vocabulary (below)
 "ground": "shops|arcade|market_stalls|...",
 "signage": {"kinds": ["neon_blade", "lightbox", "dot_matrix", "lantern_string", "painted", "brass_letters", ...],
             "density": 0..1, "palette": ["#hex"], "animation": ["flash", "chase", "scroll", "flicker", "steady"]},
 "night": {"mood": ["#hex", ...], "motifs": ["window_glow", "strip_outline", "lantern_string", "uplight", ...]},
 "floor_plan": "the plan type (ground shops, stair core, lightwell, units per floor) -- see plans/*.md",
 "fantasy": "what fantasy art adds to it (optional)"}
```
Shared component vocabulary (`components.json`): `{id, description, size_m, variants, used_by: [style ids]}`. Reuse
first: a component that serves many styles is better than many that serve one.

## Sign and light anchors (the generator writes them; SkySigns fills them)
- An empty node in a building glb named `sign_<kind>_<w>x<h>[_<n>]` (metres, e.g. `sign_blade_1.2x6`) is a sign's
  face. Local +Z points out of the face and +Y is up; the origin is the face's centre.
- `glow_<motif>_<n>`: a mood-light run, such as an edge line (a strip along local +X, length in the name) or an
  uplight.
- `lights_<n>`: the anchors of a string of lights. They are paired in order, and a catenary runs between each pair.
- The building record's traits carry `style`, `use`, `shop_name` and `shop_kind` (per storefront), and `mood` (hex).
