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

## Bridges

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

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

## Street furniture / misc scenery

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Yard / lot props

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Interior props / furniture

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

## Vehicles, animals, and other categories from the expansion pass

*(sections to be added once `scenery_asset_checklist_expansion.md` is finalized and folded in —
placeholder so this file's structure doesn't need to be redesigned when that happens)*

---

## Running totals

| Category | Planned | Done | Needs revisit | In progress |
|---|---|---|---|---|
| Residential buildings | 17 | 11 | 0 | 0 |
| Commercial/civic/farm buildings | 27 | 21 | 0 | 0 |
| Bridges | 6 | 0 | 0 | 0 |
| Road sections/intersections | 11 | 0 | 0 | 0 |
| Water features | 11 | 0 | 0 | 0 |
| Trees/vegetation | ~24 | 0 | 0 | 0 |
| Fences | ~11 | 0 | 0 | 0 |
| Street furniture/misc | 8 | 0 | 0 | 0 |
| Yard/lot props | 26 | 0 | 0 | 0 |
| Interior props | 265 | 0 | 0 | 0 |
| Expansion-pass items (`scenery_asset_checklist_expansion.md`, 94 items) | 94 | 0 | 0 | 0 |
| **Total** | **505** (240 exterior/infra [146 original + 94 expansion] + 265 interior) | **3** | **0** | **0** |

Already-existing assets (house1-3, farmhouse_foursquare/gable, 4 storefronts,
post_office, barn, pole_building, lamp_post, fire_hydrant, 4 fence types, 7 tree types, 4
vehicles — confirmed via repo scan 2026-09-22, see `scenery_asset_checklist.txt`'s own
`[EXISTING]` tags) are **not** re-listed here since they predate this registry and were built
under a different, undocumented process — this file starts tracking from the first model built
under the current research-driven pipeline forward (the 3 residential buildings above are the
first entries).
