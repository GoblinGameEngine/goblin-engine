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
| Residential buildings | 17 | 0 | 0 | 0 |
| Commercial/civic/farm buildings | 27 | 0 | 0 | 0 |
| Bridges | 6 | 0 | 0 | 0 |
| Road sections/intersections | 11 | 0 | 0 | 0 |
| Water features | 11 | 0 | 0 | 0 |
| Trees/vegetation | ~24 | 0 | 0 | 0 |
| Fences | ~11 | 0 | 0 | 0 |
| Street furniture/misc | 8 | 0 | 0 | 0 |
| Yard/lot props | 26 | 0 | 0 | 0 |
| Interior props | 265 | 0 | 0 | 0 |
| **Total (pre-expansion)** | **~411 exterior + 265 interior = ~676** | **0** | **0** | **0** |

Totals above will be updated once the checklist-expansion pass (in progress) is folded in, and
should be recomputed any time an item count changes in the source checklists. Already-existing
assets (house1-3, farmhouse_foursquare/gable, 4 storefronts, post_office, barn, pole_building,
lamp_post, fire_hydrant, 4 fence types, 7 tree types, 4 vehicles — confirmed via repo scan
2026-09-22, see `scenery_asset_checklist.txt`'s own `[EXISTING]` tags) are **not** re-listed
here since they predate this registry and were built under a different, undocumented process —
this file starts tracking from the first model built under the current research-driven pipeline
forward.
