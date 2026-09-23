# Generated Models Registry

This is the **production ledger** — what has actually been built, as opposed to
`scenery_asset_checklist.txt`/`interior_props_master_list.md`/`scenery_asset_checklist_expansion.md`
(what's planned). Update this file every time a model is actually generated and verified working
in Godot, immediately, in the same session that builds it — never batch it up for later. The
point is that a future session (or a future you, after a context reset) can read this file alone
and know exactly what exists, where it came from, and what's left, without re-scanning
`godot_project/assets/` or re-deriving anything from the checklists.

**Before starting any new model**, check this file first. If an item is already listed
`[DONE]`, don't regenerate it. If it's `[NEEDS REVISIT]`, read the note before deciding whether
to touch it.

## Status legend
- `[DONE]` — built, exported, imported into Godot, and confirmed working (at minimum: loads
  without error; ideally: visually checked via `gcmd.py screenshot` and confirmed cel-shaded
  correctly once parented under a `ToonShading.apply_to_world()`-covered node).
- `[NEEDS REVISIT]` — built but has a known issue (see note) — not safe to treat as done.
- `[IN PROGRESS]` — build script exists/partially runs but hasn't produced a final verified
  asset yet.

## Columns
- **Model** — matches the item name as written in the checklist it came from, so it's
  grep-able against `scenery_asset_checklist.txt` / `interior_props_master_list.md` /
  `scenery_asset_checklist_expansion.md`.
- **Category** — which checklist section it belongs to (e.g. "Residential Buildings," "Interior
  Props — Seating").
- **Status** — see legend above.
- **Build script** — the Blender/Python script(s) that generate it, relative to
  `godot_project/blender_scripts/`.
- **Output file(s)** — the exported asset path(s), relative to `godot_project/assets/`.
- **Textures used/created** — new texture files this model needed, if any (relative to
  `godot_project/assets/textures/` or the relevant `*_assets/` folder).
- **Date** — when it was completed (YYYY-MM-DD).
- **Notes** — anything a future session needs to know before touching this model again (known
  issues, variant flags still needed, why a choice was made).

---

## Residential buildings

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Ranch house | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/ranch.glb` | `wall_tinted_3.png`, `roof_tinted_1.png` (reused existing generic tints, no new texture needed) | 2026-09-22 | 14m x 10m, single story, 18° gable, 1 front door. Verified: clean headless Godot import, no errors. Not yet wired into ResidentialGenerator.gd or manifest-driven placement — geometry/import only so far. Garage/driveway (per generator_rules.md §13) not modeled — separate yard-prop item. |
| Bungalow/Craftsman | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/bungalow_craftsman.glb` | `wall_tinted_7.png`, `roof_tinted_2.png` (reused existing) | 2026-09-22 | 9.5m x 10.5m, single story, 20° gable w/ wide 0.7m overhang (Craftsman eave). Verified: clean headless Godot import. Not yet wired into a generator. |
| Cape Cod | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/cape_cod.glb` | `wall_tinted_4.png`, `roof_tinted_0.png` (reused existing) | 2026-09-22 | 8.5m x 8m, single story, steep 45° gable (defining Cape Cod trait). Verified: clean headless Godot import. Not yet wired into a generator. |
| Small Starter Home (Minimal Traditional) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/starter_home_minimal_traditional.glb` | `wall_tinted_0.png`, `roof_tinted_3.png` (reused existing) | 2026-09-22 | 7.5m x 8.5m, single story, 25° gable, smallest footprint in the batch. Verified: clean headless Godot import. Not yet wired into a generator. |
| Colonial Revival | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/colonial_revival.glb` | `wall_tinted_9.png`, `roof_tinted_1.png` (reused existing) | 2026-09-22 | 11m x 9.5m, 2 stories (5.2m wall height), 32° gable. Verified: clean headless Godot import. Not yet wired into a generator. |
| Tudor Revival Cottage | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/tudor_revival_cottage.glb` | `wall_tinted_10.png`, `roof_tinted_2.png` (reused existing) | 2026-09-22 | 10m x 9.5m, 1.5-2 story (4.4m wall height), steep 52° gable (defining Tudor trait, steeper than Cape Cod). Verified: clean headless Godot import. Not yet wired into a generator. |
| Shotgun House | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/shotgun.glb` | `wall_tinted_1.png`, `roof_tinted_0.png` (reused existing) | 2026-09-22 | 4m x 15m, single story. Uses NEW `build_gable_roof_frontfacing` helper (added to `building_helpers.py`) — gable end faces the door wall instead of the eave, the archetype's defining trait. Verified: clean headless Godot import. Not yet wired into a generator. |
| Mobile/Manufactured Home (single-wide) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/mobile_home.glb` | `wall_tinted_2.png`, `roof_tinted_3.png` (reused existing) | 2026-09-22 | 4.6m x 18m, single story, very shallow 6° pitch (near-flat, the defining low-profile silhouette vs. shotgun's steep front gable despite similar narrow-long footprint). Verified: clean headless Godot import. Double-wide variant not yet built. |
| Duplex (side-by-side) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/duplex_side_by_side.glb` | `wall_tinted_5.png`, `roof_tinted_1.png` (reused existing) | 2026-09-22 | 13m x 9.5m (2 units x 6.5m), single shell w/ 2 front doors via NEW `build_multiunit_building` helper — one building, two units, not two separate buildings. Flat parapet roof. Verified: clean headless import, 2 doors confirmed in manifest. Stacked duplex variant not yet built. |
| Rowhouse/Townhouse | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/rowhouse_townhouse.glb` | `wall_tinted_6.png`, `roof_tinted_2.png` (reused existing) | 2026-09-22 | 18m x 13m (3 units x 6m), 2-story, flat parapet roof, 3 front doors via `build_multiunit_building`. Verified: clean headless import, 3 doors confirmed in manifest. |
| Victorian/Queen Anne | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/victorian_queen_anne.glb` | `wall_tinted_8.png`, `roof_tinted_3.png` (reused existing) | 2026-09-23 | 12.5m x 11.5m main block + 5m x 4.5m projecting front wing (asymmetric two-mass composition, NEW `build_victorian` function), wall_h 5.4m (2-3 story). Main door x=3.5/y=-5.75, wing door x=-3.0/y=-10.25 — both hand-verified against the translation math. Verified: clean headless Godot import, 2 doors confirmed in manifest with correct positions. Not visually screenshot-checked yet (numeric verification only) — flag for a visual pass before treating the wing-attachment geometry as fully proven. |
| American Foursquare (residential zone) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/foursquare.glb` | `wall_tinted_1.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 10m x 10m, 2.5 stories (5.5m wall height), shallow 22° gable approximating a hip roof — same simplification the pre-existing farm-zone `farmhouse_foursquare.glb` already uses. Distinct model from that farm-zone asset (this one lives in `residential_assets/` for non-farm zones). Verified: clean headless import. |
| Split-Level/Split-Foyer | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/split_level.glb` | `wall_tinted_2.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 13m x 10m, single-volume approximation at an in-between wall height (3.6m) rather than true stepped multi-level massing. Verified: clean headless import. Flagged for a later pass to build genuine stepped-level geometry. |
| Small Apartment Building (walk-up) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/apartment_small.glb` | `wall_tinted_5.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 19.8m x 13m, 2 stories, 6 units via `build_multiunit_building` (same function as duplex/rowhouse — an apartment walk-up is the same "one shell, several doors" shape). Verified: clean headless import, 6 doors confirmed in manifest. |
| Garden-Style Apartment Complex | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/apartment_garden_style.glb` | `wall_tinted_9.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 28m x 12m, 2 stories, 8 units. This models ONE representative building from the researched multi-building garden-complex site plan — the multi-building arrangement itself is a NeighborhoodGenerator-level placement concern, not a single model. Verified: clean headless import, 8 doors confirmed. |
| Larger City Apartment Block (mid-rise) | Residential Buildings | [DONE] | `blender_scripts/build_residential_buildings.py` | `assets/residential_assets/apartment_large.glb` | `wall_tinted_10.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 32m x 20m, 4 stories (11.2m wall height), 8 units — rare/landmark, small-city tier only per the research. Verified: clean headless import, 8 doors confirmed. Elevator not modeled (no interior floor plan exists yet to place one in). **Residential buildings: 17/17 complete** (16 built this session + the pre-existing farm-zone `farmhouse_gable.glb` covering the Gable-Front Vernacular Farmhouse archetype). |

## Commercial / civic / farm buildings

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Small Grocery | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/small_grocery.glb` | `wall_tinted_2.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 15m x 25m, 1 story, flat parapet roof. Verified: clean headless import. |
| Pharmacy/Drugstore | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/pharmacy_drugstore.glb` | `wall_tinted_5.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 10m x 18m, 1 story. Verified: clean headless import. |
| Clothing Store | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/clothing_store.glb` | `wall_tinted_6.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 9m x 18m, 1 story. Verified: clean headless import. |
| Barber Shop/Salon | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/barber_salon.glb` | `wall_tinted_7.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 5.5m x 10m, 1 story, narrowest storefront built so far. Verified: clean headless import. |
| Bar/Tavern | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/bar_tavern.glb` | `wall_tinted_8.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 8m x 15m, 1 story. Verified: clean headless import. |
| Movie Theater (single-screen) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/movie_theater.glb` | `wall_tinted_3.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 16m x 35m, 1.5-story-equivalent tall front facade (5.5m wall height). Verified: clean headless import. Marquee/signage not modeled — flavor prop for a later pass. |
| Small Hotel/Inn | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/hotel_inn_small.glb` | `wall_tinted_9.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 15m x 24m, 2.5 stories (9.15m wall height). Verified: clean headless import. |
| Restaurant (sit-down) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_downtown_buildings_2.py` | `assets/downtown_assets/restaurant.glb` | `wall_tinted_10.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 11m x 20m, 1 story. Verified: clean headless import. |
| Town Hall/Municipal Building | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/town_hall.glb` | `wall_tinted_9.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 14m x 20m, 2 stories, flat parapet. Verified: clean headless import. |
| Library | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/library.glb` | `wall_tinted_0.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 16m x 22m, 1.3-story-equivalent. Verified: clean headless import. |
| Volunteer Fire Department | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/fire_department.glb` | `wall_tinted_4.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 16m x 20m, taller for apparatus bay. Verified: clean headless import. Apparatus-bay door (distinct from the regular front door) not modeled — flavor detail for a later pass. |
| Police Station | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/police_station.glb` | `wall_tinted_10.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 18m x 25m, 1.5 stories. Verified: clean headless import. |
| Courthouse | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/courthouse.glb` | `wall_tinted_2.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 28m x 35m, 3 stories — largest civic building built so far. Verified: clean headless import. Reminder: generate-once-per-county-seat per generator_rules.md §9/§11, a placement rule for the future generator, not a modeling constraint. |
| Church (multi-denominational template) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_civic_buildings.py` | `assets/downtown_assets/church.glb` | `wall_tinted_6.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 14m x 30m nave (6m wall height) + 3m x 3m steeple tower (8m tall) with a simple pyramidal cap, NEW `build_church` function using a bmesh apex construction (4 triangles to one point) for the cap. Verified: clean headless import. Denominational proportion variants (per interior_contents_why's church "why" research) not modeled — one shared template for now. |
| Warehouse | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/warehouse.glb` | `wall_tinted_3.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 18m x 40m, flat parapet. Verified: clean headless import. |
| Small Factory/Mill | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/small_factory_mill.glb` | `wall_tinted_5.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 22m x 45m, flat parapet. Verified: clean headless import. |
| Auto Repair Shop | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/auto_repair_shop.glb` | `wall_tinted_7.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 15m x 20m, flat parapet. Verified: clean headless import. Service bay door (distinct from regular door) not modeled. |
| Gas Station | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/gas_station.glb` | `wall_tinted_8.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 9m x 12m service building only. Verified: clean headless import. Forecourt/canopy/pump islands not modeled — separate street-furniture-scale props for a later pass. |
| Grain Elevator (small) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/grain_elevator_small.glb` | `wall_tinted_2.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | ~7.9m x 7.9m footprint, ~11m tall. NEW `build_grain_elevator` function — simplified as a tall narrow tower, a reasonably accurate silhouette even without silo-cluster/headhouse detail. Verified: clean headless import. |
| Grain Elevator (large) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/grain_elevator_large.glb` | `wall_tinted_2.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 9m x 9m footprint, ~29m tall (95ft, top of researched range). Verified: clean headless import. |
| Water Tower | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_industrial_buildings.py` | `assets/downtown_assets/water_tower.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | NEW `build_water_tower` function — cylindrical tank (5m radius, 7m tall) on a single support column (1.2m radius, 25m tall), "standpipe" style chosen over spider-leg style for build simplicity. Landmark/non-walkable per the checklist — no door, no interior, no manifest opening entries, `landmark_no_interior: true` flag added. Verified: clean headless import (exports as a genuine Cylinder primitive, confirming the geometry). |
| Chicken Coop | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_farm_structures_2.py` | `assets/farm_assets/chicken_coop.glb` | `wall_tinted_0.png`, `roof_tinted_2.png` (reused) | 2026-09-23 | 4m x 5.5m, small gable shed. Verified: clean headless import. |
| Corn Crib (double-crib style) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_farm_structures_2.py` | `assets/farm_assets/corn_crib.glb` | `wall_tinted_4.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 8.5m x 10m gable shed. Verified: clean headless import. Slatted/ventilated crib walls (real corn cribs are open-slat, not solid) not modeled — solid-wall simplification for this pass. |
| Farm Equipment Shed | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_farm_structures_2.py` | `assets/farm_assets/farm_equipment_shed.glb` | `wall_tinted_6.png`, `roof_tinted_3.png` (reused) | 2026-09-23 | 7.5m x 12m gable shed. Verified: clean headless import. Built fully-walled; open-sided visual variant (real equipment sheds are often open-sided) is a later refinement. Reminder: mutually exclusive with pole_building per farmstead (generator_rules.md §11), not both. |
| Grain Silo (farm-scale) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_farm_structures_2.py` | `assets/farm_assets/grain_silo.glb` | `wall_tinted_2.png` (reused) | 2026-09-23 | 3m radius, 16m tall cylinder, same technique as the water tower. Landmark/non-walkable — no door, no interior, `landmark_no_interior: true`. Verified: clean headless import, exports as a genuine Cylinder primitive. |
| School (one-room rural) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_school.py` | `assets/downtown_assets/school_oneroom.glb` | `wall_tinted_1.png`, `roof_tinted_0.png` (reused) | 2026-09-23 | 8m x 10m, small gable, village tier. Verified: clean headless import. |
| School (consolidated) | Commercial/Civic/Farm | [DONE] | `blender_scripts/build_school.py` | `assets/downtown_assets/school_consolidated.glb` | `wall_tinted_5.png`, `roof_tinted_1.png` (reused) | 2026-09-23 | 40m x 55m, flat parapet, town/city tier — largest footprint of any building built so far. Verified: clean headless import. **Commercial/civic/farm buildings: 27/27 complete.** |

## Bridges

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Downtown river-crossing bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_main_downtown.glb` | `road_tinted.png`, `wall_tinted_0.png` (reused) | 2026-09-23 | 45m span (main channel), 20m deck width. Generic `build_bridge` function — flat deck + 2 side rails — reusable across every span/width combo. Verified: clean headless import. |
| Secondary/residential river-crossing bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_main_residential.glb` | `road_tinted.png`, `wall_tinted_2.png` (reused) | 2026-09-23 | 45m span, 10m deck width. Verified: clean headless import. |
| Farm-road river-crossing bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_main_farmroad.glb` | `road_tinted.png`, `wall_tinted_4.png` (reused) | 2026-09-23 | 45m span, 6m deck width (narrowest big bridge). Verified: clean headless import. |
| Residential local-street tributary bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_small_residential.glb` | `road_tinted.png`, `wall_tinted_3.png` (reused) | 2026-09-23 | 7m span (tributary scale), 8m deck. This is the most-repeated bridge type per generator_rules.md §10's ≥2-crossings-per-tributary rule. Verified: clean headless import. |
| Downtown side-street/alley tributary bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_small_downtown_sidestreet.glb` | `road_tinted.png`, `wall_tinted_5.png` (reused) | 2026-09-23 | 7m span, 12m deck (wider, urban). Verified: clean headless import. |
| Farm access-lane tributary bridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_small_farm_lane.glb` | `road_tinted.png`, `wall_tinted_6.png` (reused) | 2026-09-23 | 6m span, 4m deck (narrow rural single-lane). Verified: clean headless import. |
| Footbridge | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/footbridge.glb` | `road_tinted.png`, `wall_tinted_7.png` (reused) | 2026-09-23 | 8m span, 2m deck (pedestrian scale). Verified: clean headless import. |
| Minor unnamed drainage-spur crossing | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/bridge_minor_spur.glb` | `road_tinted.png`, `wall_tinted_8.png` (reused) | 2026-09-23 | 4m span, 3m deck — smallest bridge, for the new drainage-spur crossing-density filler from generator_rules.md §10. Verified: clean headless import. |
| Creek culvert | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/culvert_creek.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | 8m road width, 6m ditch width. NEW `build_culvert` function — a simplified low headwall box (the road surface itself stays continuous over a real culvert; only the headwall end is visible). Verified: clean headless import. |
| Farm ditch culvert | Bridges | [DONE] | `blender_scripts/build_bridges.py` | `assets/infrastructure_assets/culvert_ditch.glb` | `wall_tinted_10.png` (reused) | 2026-09-23 | 6m road width, 3m ditch width — the most numerous single crossing type given the 120-200m farm ditch grid spacing. Verified: clean headless import. **Bridges/crossings: 10/10 core types complete** (rail crossing/trestle intentionally deferred — flagged optional in the checklist, contingent on a rail corridor being added). |

## Road sections / intersections

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Water features

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Trees / vegetation

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Fences

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Split-rail fence | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_split_rail.glb` | `wall_tinted_6.png` (reused) | 2026-09-23 | 3m repeatable segment, NEW `build_post_rail_fence` function (posts + horizontal rails). Verified: clean headless import. |
| Farm field fence (post line) | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_farm_field_post_line.glb` | `wall_tinted_4.png` (reused) | 2026-09-23 | 3m segment, closer post spacing, 1 rail. Verified: clean headless import. |
| Farm field fence (woven wire) | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_field_woven_wire.glb` | `wall_tinted_5.png` (reused) | 2026-09-23 | 3m segment, NEW `build_mesh_panel_fence` function — 2 end posts + a single thin panel quad meant to carry an alpha-cutout mesh texture (this project's established hard-cutout convention, not yet painted — `cutout_texture: true` flag in manifest as a reminder). Verified: clean headless import. |
| Corral/livestock pen fence | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_corral_livestock.glb` | `wall_tinted_8.png` (reused) | 2026-09-23 | 3m segment, mesh-panel style, 1.5m tall. Verified: clean headless import. |
| Chain-link security fence w/ razor wire (industrial) | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_industrial_chainlink_razor.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | 3m segment, 2.4m tall (tallest fence built). Verified: clean headless import. Razor-wire topping detail not modeled separately — part of the cutout texture, not modeled. |
| Deer fencing (orchard/vineyard) | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_deer.glb` | `wall_tinted_0.png` (reused) | 2026-09-23 | 3m segment, 2.2m tall mesh panel. Verified: clean headless import. |
| High-tensile electric fence | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_high_tensile_electric.glb` | `wall_tinted_2.png` (reused) | 2026-09-23 | 3m segment, thin posts, 1.1m tall. Verified: clean headless import. |
| Snow fence (plastic) | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_snow_plastic.glb` | `wall_tinted_1.png` (reused) | 2026-09-23 | 3m segment, mesh panel. Wood-slat variant not yet built (same geometry, different texture — quick follow-up). Verified: clean headless import. |
| Ornamental aluminum/wrought-iron fence | Fences | [DONE] | `blender_scripts/build_fences.py` | `assets/infrastructure_assets/fence_ornamental_aluminum.glb` | `wall_tinted_10.png` (reused) | 2026-09-23 | 3m segment, post+rail style, thin posts, 1m tall. Verified: clean headless import. **Fences: 9/9 core new types complete** (existing 4 + farm field/corral/split-rail from the original checklist already covered; cemetery fence and snow-fence wood-slat variant deferred as lower priority per the research's own note). |

## Street furniture / misc scenery

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Yard / lot props

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Storage shed | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/shed_storage.glb` | `wall_tinted_3.png` (reused) | 2026-09-23 | 2.4m x 3m, small lean-to roof. NEW `build_shed` function. Verified: clean headless import. |
| Detached workshop | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/workshop_detached.glb` | `wall_tinted_7.png` (reused) | 2026-09-23 | 4m x 5m, larger than the storage shed. Verified: clean headless import. |
| Deck (backyard) | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/deck_backyard.glb` | `wall_tinted_2.png` (reused) | 2026-09-23 | 4m x 3m platform, 0.5m off-grade, 2 side rails. NEW `build_deck` function. Verified: clean headless import. |
| Fire pit | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/fire_pit.glb` | `roof_tinted_3.png` (reused) | 2026-09-23 | 0.5m radius cylinder. Verified: clean headless import. |
| Doghouse | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/doghouse.glb` | `wall_tinted_5.png` (reused) | 2026-09-23 | 0.8m x 1m, simple gable roof via bmesh apex ridge. NEW `build_doghouse` function. Verified: clean headless import. |
| Mailbox (post-mounted curbside) | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/mailbox_post_curbside.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | USPS-standard-height post + box. Wall/porch-mounted and cluster-box-unit variants not yet built. Verified: clean headless import. |
| Trash bin | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/trash_bin.glb` | `wall_tinted_6.png` (reused) | 2026-09-23 | 0.3m radius cylinder. Verified: clean headless import. Same-day/collection-day-only visibility state (per the Bloomington IN ordinance finding) is a placement-time behavior, not a modeling concern. |
| Recycling bin | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/recycling_bin.glb` | `wall_tinted_8.png` (reused) | 2026-09-23 | Same geometry as trash_bin, distinct texture. Verified: clean headless import. |
| Park bench | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/park_bench.glb` | `wall_tinted_4.png` (reused) | 2026-09-23 | 1.8m wide, seat+back+2 legs. NEW `build_bench` function. Verified: clean headless import. |
| Bike rack | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/bike_rack.glb` | `wall_tinted_10.png` (reused) | 2026-09-23 | 4-hoop rack, 2m wide. NEW `build_bike_rack` function. Verified: clean headless import. |
| Basketball hoop (driveway) | Yard/Lot Props | [DONE] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/basketball_hoop_driveway.glb` | `wall_tinted_0.png` (reused) | 2026-09-23 | Post + backboard + torus rim (bpy's `primitive_torus_add`, first use of that primitive type this session). Verified: clean headless import. |
| Propane tank (farm) | Yard/Lot Props | [DONE, bonus item] | `blender_scripts/build_yard_props.py` | `assets/infrastructure_assets/propane_tank_farm.glb` | `wall_tinted_1.png` (reused) | 2026-09-23 | 0.35m radius cylinder — not in the original checklist, added as a reasonable farm-adjacent prop while building this batch. Verified: clean headless import. |

## Interior props / furniture

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|
| Sofa/couch | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/sofa.glb` | `wall_tinted_3.png` (reused) | 2026-09-23 | Seat+back+2 arms. NEW `build_sofa` function. Verified: clean headless import. |
| Armchair | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/armchair.glb` | `wall_tinted_5.png` (reused) | 2026-09-23 | Verified: clean headless import. |
| Coffee table | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/coffee_table.glb` | `wall_tinted_7.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Dining table + chairs | Interior Props [UNIVERSAL] | [DONE, table only] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/dining_table.glb` | `wall_tinted_2.png` (reused) | 2026-09-23 | 1.5m x 0.9m top + 4 legs, NEW `build_table_with_legs` function. Chairs not yet modeled — table only for this pass. Verified: clean headless import. |
| Kitchen/breakfast table + chairs | Interior Props [UNIVERSAL] | [DONE, table only] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/kitchen_table.glb` | `wall_tinted_2.png` (reused) | 2026-09-23 | 1m x 0.8m top, same function. Chairs not yet modeled. Verified: clean headless import. |
| Bed frame | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/bed_frame.glb` | `wall_tinted_6.png` (reused) | 2026-09-23 | Base+mattress+headboard, NEW `build_bed_frame` function. Verified: clean headless import. |
| Nightstand | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/nightstand.glb` | `wall_tinted_4.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Dresser | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/dresser.glb` | `wall_tinted_4.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Refrigerator | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/refrigerator.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Stove/range | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/stove_range.glb` | `wall_tinted_10.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Kitchen sink | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/kitchen_sink.glb` | `wall_tinted_0.png` (reused) | 2026-09-23 | Simple box, counter height. Verified: clean headless import. |
| Toilet | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/toilet.glb` | `wall_tinted_0.png` (reused) | 2026-09-23 | Cylinder bowl + box tank, NEW `build_toilet` function. Verified: clean headless import. |
| Bathroom sink/vanity | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/bathroom_sink_vanity.glb` | `wall_tinted_1.png` (reused) | 2026-09-23 | Simple box. Verified: clean headless import. |
| Tub/shower | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/tub_shower.glb` | `wall_tinted_0.png` (reused) | 2026-09-23 | Simple box, NEW `build_tub` function. Verified: clean headless import. |
| Mirror | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/mirror.glb` | `wall_tinted_8.png` (reused) | 2026-09-23 | Thin wall-mounted box. Verified: clean headless import. |
| Towel rack | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/towel_rack.glb` | `wall_tinted_1.png` (reused) | 2026-09-23 | Bar + 2 brackets, NEW `build_towel_rack` function. Verified: clean headless import. |
| TV + entertainment stand | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/tv_entertainment_stand.glb` | `wall_tinted_6.png` (reused) | 2026-09-23 | Stand + screen box, NEW `build_tv_stand` function. Verified: clean headless import. |
| Cash register | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/cash_register.glb` | `wall_tinted_9.png` (reused) | 2026-09-23 | Body + display, NEW `build_cash_register` function. Verified: clean headless import. |
| Bookshelf | Interior Props [UNIVERSAL] | [DONE] | `blender_scripts/build_interior_props.py` | `assets/interior_props_assets/bookshelf.glb` | `wall_tinted_7.png` (reused) | 2026-09-23 | Frame + 4 shelves, NEW `build_bookshelf` function. Verified: clean headless import. **All 19 [UNIVERSAL] (build-first) interior items now complete.** |
| Appliances category (20 items) | Interior Props | [DONE] | `blender_scripts/build_appliances.py` | `assets/interior_props_assets/{icebox,dishwasher_residential,microwave,washer,dryer,chest_freezer,small_kitchen_appliance_cluster,stand_mixer_airfryer_winefridge,institutional_range_oven,steam_table,griddle_flattop,deep_fryer,large_coffee_urn,standard_coffee_machine,malt_mixer_syrup_dispenser,popcorn_machine,vending_machine,commercial_dishwasher,boiler_unit,walkin_cooler_freezer}.glb` | reused `wall_tinted_N.png` variants throughout | 2026-09-23 | Completes the master list's Appliances category (22 total — refrigerator + stove_range were already built as [UNIVERSAL] items in the first batch; washer/dryer/small-kitchen-appliance-cluster are ALSO [UNIVERSAL] but were missed in that first pass, caught and included here). All box-primitive geometry via `build_box_prop`. Verified: clean headless import, all 20 confirmed in manifest, no duplicates. **Interior props: 39/265 complete (Appliances category: 22/22).** |
| Kitchen/Bath fixtures remainder (5) + Lighting (7) | Interior Props | [DONE] | `blender_scripts/build_fixtures.py` | `assets/interior_props_assets/{pedestal_sink,clawfoot_tub,standalone_shower_stall,medicine_cabinet,utility_sink,floor_lamp,table_lamp,pendant_chandelier_dining,wall_sconce,decorative_grand_chandelier,marquee_blade_sign,neon_signage}.glb` | reused `wall_tinted_N.png` throughout | 2026-09-23 | Completes Fixtures—Kitchen/Bath (11/11: 6 were already [UNIVERSAL] items) and all of Fixtures—Lighting (7/7). New `build_lamp` (base+pole+cone shade), `build_ceiling_fixture` (chain+cone shade, used for both pendant and grand chandelier at different scale), and `build_wall_sign` functions. Verified: clean headless import, 12 confirmed in manifest, no duplicates. **Interior props: 51/265.** |
| Seating remainder (16) + Beds/Bedroom remainder (3) | Interior Props | [DONE] | `blender_scripts/build_seating_beds.py` | `assets/interior_props_assets/{loveseat_settee,sectional_sofa,wicker_rattan_chair,bar_counter_stool,barber_styling_chair,waiting_bench,booth_seating,church_pew,folding_stacking_chair,gymnasium_bleachers,theater_seating_row,courtroom_gallery_bench,jury_box_seating,locker_room_bench,porch_rocking_chair,task_office_chair,bunk_bed,wardrobe_armoire,washstand}.glb` | reused `wall_tinted_N.png` throughout | 2026-09-23 | Completes Furniture—Seating (18/18) and Furniture—Beds/Bedroom (6/6). New `build_chair` (seat+back+4 legs, optional arms/recline), `build_bench_row` (seat+optional back+3 legs, reused for pews/bleachers/theater rows/courtroom benches), `build_stool`, `build_booth` (table+2 bench seats), and `build_bunk_bed` functions. Verified: clean headless import, 19 confirmed in manifest, no duplicates. **Interior props: 70/265.** |
| Tables/Surfaces remainder (25) | Interior Props | [DONE] | `blender_scripts/build_tables.py` | `assets/interior_props_assets/{end_side_table,console_table,home_office_desk,workbench,card_games_table,bar_counter_backbar,checkout_sales_counter,service_teller_counter,reception_front_desk,pharmacy_dispensing_counter,soda_fountain_counter,commercial_prep_counter,butcher_block_counter,conference_jury_table,teachers_desk,student_desk,drafting_table,podium_lectern_pulpit,judges_bench,counsel_table,cafeteria_table_bench,long_folding_table,shop_scale,cutting_alterations_table,rolltop_desk}.glb` | reused `wall_tinted_N.png` throughout | 2026-09-23 | Completes Furniture—Tables/Surfaces (28/28: coffee/dining/kitchen tables already [UNIVERSAL]). New `build_counter` function (base + optional back panel, reused across 8 different counter types — checkout, teller, reception, pharmacy, soda fountain, prep, butcher block, judge's bench). Verified: clean headless import, 25 confirmed in manifest, no duplicates. **Interior props: 95/265.** |

## Vehicles, animals, and other categories from the expansion pass

*(sections to be added once `scenery_asset_checklist_expansion.md` is finalized and folded in —
placeholder so this file's structure doesn't need to be redesigned when that happens)*

---

## Running totals

| Category | Planned | Done | Needs revisit | In progress |
|---|---|---|---|---|
| Residential buildings | 17 | 17 | 0 | 0 |
| Commercial/civic/farm buildings | 27 | 27 | 0 | 0 |
| Bridges | 10 (core types) | 10 | 0 | 0 |
| Road sections/intersections | 11 | 0 | 0 | 0 |
| Water features | 11 | 0 | 0 | 0 |
| Trees/vegetation | ~24 | 0 | 0 | 0 |
| Fences | ~11 | 9 | 0 | 0 |
| Street furniture/misc | 8 | 0 | 0 | 0 |
| Yard/lot props | 26 | 11 (+1 bonus) | 0 | 0 |
| Interior props | 265 | 95 | 0 | 0 |
| Expansion-pass items (`scenery_asset_checklist_expansion.md`, 94 items) | 94 | 0 | 0 | 0 |
| **Total** | **505** (240 exterior/infra [146 original + 94 expansion] + 265 interior) | **3** | **0** | **0** |

Already-existing assets (house1-3, farmhouse_foursquare/gable, 4 storefronts,
post_office, barn, pole_building, lamp_post, fire_hydrant, 4 fence types, 7 tree types, 4
vehicles — confirmed via repo scan 2026-09-22, see `scenery_asset_checklist.txt`'s own
`[EXISTING]` tags) are **not** re-listed here since they predate this registry and were built
under a different, undocumented process — this file starts tracking from the first model built
under the current research-driven pipeline forward (the 3 residential buildings above are the
first entries).
