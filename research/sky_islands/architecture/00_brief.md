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

## Round-2 build contract (2026-10-14, after the research)
Merged by `tools/sky/styles.py`:
- `styles.json` (67 styles, each with a `region`) and `components.json` (232 ids) here.
- The game's copy, `godot_project/remake/sky/styles.json`, and `godot_project/remake/sky/style_assign.json`
  (island → style; the canon's `islands[].style`).

The user's additions: stacked warrens (Europe, South America, Canada, North Africa, Asia; no sub-Saharan Africa).

**Footprint rules** (the user: "use all the tricks we've learned to reduce the footprint"):
- Facades are built from modular panels: per style a set of bay panels at a standard bay width and storey height
  (plain, window variants, door, balcony, bay box, shopfront), plus the shared components. gbkit's dedup then stores
  each panel once (`SSC_KIT=1`).
- Interiors are present but light, using shared furniture and the ceiling tiles.
- Target: an average building glb under ~300 KB, and all island building models together under ~250 MB with their LODs.
- About 5–6 models per style (~350–400 models). Varied at runtime by clan colours, unique signs and mood light.

**Components library** (`remake/blender/sky/components/`), the API the generator calls:
```
import sky_components as SC
SC.place(b, part, cid, frame, size=None, variant=None, mat=None, **kw) -> list of objects
#   b: gblib.Building; part: its Part (or a new one); cid: a components.json id; frame: Matrix (Blender, z up)
#   at the component's anchor (its documented origin); size overrides the default size_m.
SC.panel(b, style_id, kind, frame, bay_w, storey_h, **kw)
#   a facade bay: kind in {plain, window, window_pair, door, shopfront, balcony, bay_box, screen, arch}
SC.ceiling(b, part, rect, z, variant)   # the ceiling tiles (suspended_grid_600, pressed_tin, artesonado_coffer,
                                        # batten, coffered, painted_plaster)
SC.catalogue() -> {cid: {"size_m":, "anchor":, "variants": [...]}}
```
Each component is built in one deterministic way, so gbkit recognises its repeats. A component may also leave
anchors (`sign_*`, `glow_*`, `lights_*` empties) for SkySigns.

**Generator**: a new kind `"sky"` (`remake/blender/gen/sky.py`, dispatched in build_record.py). It reads a record's
`traits.style` and the style's massing, stack rules, plan and components; builds floors, rooms, stairs and roof access
(roofaccess.py); and writes the anchors. Records are `remake/catalog/SKY-<style>-NN.json`. tools/sky/make_islands.py
then lays out each island from its style's models, with stacked warrens: skybridges, plank bridges and covered alleys
between buildings, as data drawn from shared parts.
