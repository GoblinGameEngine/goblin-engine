# Shared building parts (the kit) -- design, 2026-10-12

Goal: make the game smaller (and no slower) by storing each repeated building piece once.

## Where the size is

The imported building meshes are 11.2 GB of the ~12 GB game:

| Level | Size |
|---|---|
| Full detail (`<ID>.glb`) | 10.41 GB |
| lod1 | 0.72 GB |
| lod2 | 0.06 GB |
| lod3 | 0.04 GB |

Within one full-detail building (C-106), the visible mesh holds about 67% of the vertices, collision 23% and door leaves 10%.

Godot import settings also inflate every building. `meshes/generate_lods` and `meshes/create_shadow_meshes` add 42% to C-106's `.scn`. The game swaps in its own lod1-3 models anyway, so the generated detail levels are largely redundant. Turning both off is a separate, cheap step; measure fps before and after.

## What repeats

Measured with `reference/tmp/kit_measure.py` on 40 random buildings. It counts the faces each builder call adds:

- **80% of visible faces come from item calls:** windows 32%, doors 20%, furniture and shop fittings about 22%, shutters 4%, rails and stairs 3%.
- **About 88 items per building**, so the per-building placement list is tiny.
- **Few distinct pieces:** 554 across the 40 buildings. For example, 1,103 window calls produce only 32 distinct windows, and 187 chairs only 8.
- **Result:** visible faces drop to 34% of today, kit included. Spread across the whole library, the kit costs less per building, so the real figure is lower.

A piece's key is the call minus its placement: for a window, its width, height, wall thickness, sash layout and materials.

## Design

### Builder (Blender)

The kit is built at the generator, not by cutting finished meshes apart.

1. Wrap the item calls (gbfurn, shopfit and the gbhouse fixtures, plus gblib's window, door casing, shutter_pair, lintel and transom). This is the same mechanism as the furniture recorder in `build_record.py`.
2. On the first sight of a piece key, build the piece once at the origin, in the item's own frame, into the kit library. Its UVs come out canonical. Their phase can differ from an in-place build, which doesn't show on trim, glass or furniture.
3. In the building, record an instance (piece id plus transform) and emit no visible geometry for it.
4. Collision is unchanged in phase 1. A "-col" piece still adds its collision faces to the building's collision mesh, so physics, the audit and occupancy are untouched.
5. Run the audit (gbaudit) before the visible geometry is removed, so it still sees every window and door.

### Outputs

- `remake/kit/<piece>.glb`: one mesh per piece, with surfaces carrying the same hashed material keys as `.mats.json`.
- `<ID>.kit.json`: `[[piece, x, y, z, yaw], ...]` in the building frame. Most items are yaw-only; a window is placed by its wall frame, so a general rotation is allowed where needed.
- The building's `.glb` keeps everything that is unique to it: walls, roofs, floors, signs, door leaves and collision.

### Game (Godot)

1. `RemakeBuilding.merge_kit` reads `<ID>.kit.json` and folds the kit pieces back into the building's visible mesh with `SurfaceTool.append_from`, which also moves normals and tangents. The result has one surface per material, as today. This runs once per model, and the merged mesh is the model's shared resource. The detail streamer runs it on a worker thread between the threaded load and `_attach`.
2. **Draw calls:** the first version drew a MultiMesh per piece per building. In Calder it cost 17–21% more draws and 10–14% fps at busy spots, so it was replaced by the merge. With the merge, draws and GPU time match the old library.
3. **Lit night glass:** unchanged. The merged surfaces keep their material keys, so `_apply_defs` picks lit glass per building as before.
4. **Shadow mesh:** the import's shadow copy still has the old surfaces, and the renderer indexes it in step with them. It is dropped after the merge, so shadows use the merged mesh.
5. **Exports:** the export presets include `*.kit.json` and `kit/*.mats.json`. The kit `.glb`s export as resources.

### Measured (Calder, 2026-10-13)

- Full-detail glbs are 31% smaller (211→146 MB per 100 buildings, with the new lettering on both sides). The 802 pieces cost 88 MB once.
- Visible-mesh bounds are unchanged, so `placement.py` is unaffected.
- Close-up, daytime and night views match the old library.

### Order

1. Windows (the biggest share, simplest). Build, then measure size, fps and load time in game.
2. Furniture and shop fittings.
3. Door casings, then door leaves as kit meshes. The leaves stay as nodes named for `door.gd`.
4. Then the plan's #1 (mesh compression and import settings) and #3 (compressed JSON).

### Risks and checks

- **Tools that read the visible-mesh bounds:** `placement.py` reads the `_visual` bounds. Store the full bounds explicitly.
- **Lit-window night glow:** check it in game at night.
- **Seams and texture phase:** check close up.
- **Detail streamer:** it loads the glb on a thread. The kit meshes have to be ready by the time `_attach` runs.
- **Kept unchanged:** the far-side bakes and the LOD2/LOD3 merged cells are made from the lod glbs.
