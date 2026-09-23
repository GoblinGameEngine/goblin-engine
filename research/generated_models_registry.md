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

## Commercial / civic / farm buildings

| Model | Category | Status | Build script | Output file(s) | Textures | Date | Notes |
|---|---|---|---|---|---|---|---|

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
| Residential buildings | 17 | 3 | 0 | 0 |
| Commercial/civic/farm buildings | 27 | 0 | 0 | 0 |
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
