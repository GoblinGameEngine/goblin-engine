# Warren placement format: see tools/sky/warren/FORMAT.md

The GENERATOR's `tools/sky/warren/FORMAT.md` (version 2) is the format (binary header, palette list, piece-id and
species tables, chunk table, global cell indices, DECK / MIRROR / mount flags, the palette variant, units, doors,
travel, foliage). `godot_project/remake/scripts/sky/sky_warren.gd` (SkyWarren) reads exactly that and refuses v1 files.

## How the runtime reads v2 (2026-10-15)
1. **Piece ids** are the KIT's own (`pieces.json`). There is no alias table and no thickness lookup. An id the kit
   lacks draws as a placeholder box and is listed in `SkyWarren.missing` (empty for SKY-100 and SKY-071).
2. **Frames:** the kit pieces are used as authored (no adapter).
   `T = translate(cell centre at y) * R(rot * 90°)`, then `* translate(0, 0, 1.5)` for mount 1 (face) or
   `* translate(1.5, 0, 1.5)` for mount 2 (corner). The mount comes from rot_flags bits 4–7.
3. **Colours** (`"palette_mode": "kit_variant"`): pal_epoch bits 0–3 pick `pieces.json palettes[civ][variant]`, and
   every slot of the piece takes that variant's colour for the slot, times the kit's COLOR_0 shade. LOD1 boxes take
   the variant's wall colour.
4. **LOD0 radius per civ:** `SkyWarren.LOD0_CIV` (kowloon_walled 40 m; others 70 m). A twin json `"lod0_m"`
   overrides it. Past it, the chunk's LOD1 boxes draw.
5. **Twin json:** SkyWarren reads `travel`, `anchors`, `walk` (`[x, y, z, kind]` nodes, `[a, b]` edges) and
   `lights` (`[x, y, z, kind, "#rrggbb"]`).
   - Lens flares: up to 300, on lanterns, shops, doors, stalls, fluoros, festoons, fountains, minarets and towers.
   - Light pools: up to 700 additive discs on the ground under the street lights, in the light's colour.
   - `lamp` (interior lamps) get neither.

## Plants, distant models, placement (2026-10-15)
- **Plants:** the .bin foliage `[species, x, y, z, rot, scale]` is drawn by `SkyPlants` (sky_plants.gd).
  - Meshes are built in code, ≤ 250 tris: about 25 base species plus 88 kin in `SkyPlants.KIN`, which map the civ
    modules' species onto the shapes with their own colours. An unknown id draws as a shrub, with a warning.
  - Drawing: one MultiMesh per species per 4 × 4-chunk quadrant, as RenderingServer instances, out to 180 m.
  - Shader: `warren_foliage.gdshader`, toon-lit, swaying in the plant's own frame and tinted per instance.
  - A plant whose cell is a room (the twin's `levels`) is a lane-wall climber. Its rot (0..3) is the face, and it is
    moved out onto that face. See `runtime_requests.md` 2.
- **Distant models:** `tools/sky/warren/lods.py` rewrites each warren island's `<id>.lod1.glb` / `.lod2.glb` city as
  the lattice's hull, node `warren_hull`, drawn with lod_vc massing (a lit window grid at night). Rerun it after the
  generator, then `godot --headless --import`.
- **Placement:** only the instances in their draw range (from the camera, with a margin) are shown and pushed each
  tick. The rest are hidden and pushed again when they come in range.
