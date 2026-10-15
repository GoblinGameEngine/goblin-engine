# Warren placement files (tools/sky/warren -> godot_project/remake/sky/warrens/)

Written by `tools/sky/warren/make_warren.py` (the GENERATOR stream); read by the runtime (`sky_warren.gd`). Contract for
research/sky_islands/warrens/00_brief.md "Build, milestone 1" and r4_design.md §5.

## Frame and lattice
- The island's local frame: +X south, +Y up, +Z west, -Z east; y 0 is the deck at the dock faces.
- Lattice: cell 3.0 m x 3.0 m in plan, storey 3.2 m. Cell (i, j, k) has its **floor centre** at
  `(x0 + 3 i + 1.5, 3.2 k, z0 + 3 j + 1.5)` -- x0, z0 in the header. Levels are absolute (k 0 = the deck's y 0);
  on rolling decks a column's ground level `gk` is the lowest level whose floor is at most 0.4 m below the deck there
  (the kit has no plinth yet: where the floor stands above the slope the gap shows; counted in stats
  "plinths_missing").
- Chunks are 8 x 8 cells (all levels): chunk (ci, cj) holds cells i in [8 ci, 8 ci + 7], j likewise.

## A piece placement (version 2: the KIT's ids, frames and palettes)
`[u16 piece, u8 i, u8 j, u8 level, u8 rot_flags, u8 pal_epoch]` (7 bytes, little endian).
- `piece`: index into the file's piece-id table; every id is a piece of `godot_project/remake/sky/warrens/pieces.json`
  (mesh of the same name in `kit/kit.glb`).
- `rot_flags`: bits 0-1 `rot`; bit 2 `DECK` -- y = the deck height at the cell centre (paving, garden beds, steps,
  stalls, fountains follow the deck), else y = 3.2 * level; bit 3 `MIRROR` (x -> -x, unused so far); bits 4-7 `mount`.
- `pal_epoch`: bits 0-3 the **palette variant** -- `pieces.json palettes[civ][variant]` (a slot -> colour dict: wall,
  trim, frame, glass, screen, roof, metal, fabric, emissive, tile, water, ground, plant), chosen per HOUSE (lot), so a
  house's walls, corners, parapets and roof share one colour; bits 4-7 the epoch that built it (0-5).
- Transform, Godot (`R = Basis(Vector3.UP, rot * PI / 2)`: rot 0 turns the piece's +Z to +Z, 1 to +X, 2 to -Z, 3 to -X):
  - `mount` 0, cell: `T = translate(cell centre at y) * R` -- origin the cell centre, y 0 the walking surface / roof
    top / (ceiling pieces) the ceiling; a piece with `span` [nx, nz] reaches into the next cells along its +X / +Z
    (`stair_run` [1, 2]: from this cell up 3.2 m into the next along its +Z).
  - `mount` 1, face: `T = translate(cell centre at y) * R * translate(0, 0, 1.5)` -- walls, passages (arches), edges
    (parapets, eaves, crown_band: y = the roof top, i.e. level = the storey above the room), signs, and the overlays
    hung on a face (ov_ac, ov_lantern, ov_fluoro, ov_planter, ov_pipe_run) and the ladder.  The piece's +Z points out
    of cell (i, j) toward the neighbour: rot 0 -> (i, j+1), 1 -> (i+1, j), 2 -> (i, j-1), 3 -> (i-1, j).
  - `mount` 2, corner: `T = translate(cell centre at y) * R * translate(1.5, 0, 1.5)` -- rot 0 the (+X, +Z) corner of
    the cell, 1 (+X, -Z), 2 (-X, -Z), 3 (-X, +Z); the cell lies in the piece's -X/-Z.
  Kind water_edge (pond kerbs, DECK) mounts as a face: +Z toward the water.
  The `<id>.json` twin lists the same mount per piece id ("mounts").  (Rule of thumb, for a runtime that prefers
  pieces.json: kind corner -> corner; kind wall/edge/sign/passage, the five face-hung overlays and ladder -> face;
  the rest -> cell.)
- Collision: pieces.json "collide" (stairs: "ramp").
- Open ground: one DECK piece per open cell, flat at the deck height of the cell centre -- paving, or where the next
  walkable cell is higher a flight up toward it in place of the paving (step_low_1 for < 0.45 m, step_low_4 for
  < 1.2 m, steps_up beyond), so a sloping street is terraces joined by risers.  Pond edges: kerb_straight on every
  open cell edge against the water (DECK, face mount, +Z to the water).

## The file (gzip)
```
"WRN1" u16 version (2)
str civ              (str = u16 length + utf-8)
f32 x0, f32 z0, f32 cell (3.0), f32 storey (3.2)
u16 nx, u16 nz, u8 levels
u8 n_palette, then n_palette x [u8 r, g, b]          (sRGB; v2: each kit palette variant's wall colour, informative)
u16 n_pieces, then n_pieces x str                    (piece ids)
u16 n_species, then n_species x str                  (foliage species ids)
u16 n_chunks, then n_chunks x [u8 ci, u8 cj, u32 first record, u32 count]
u32 n_records, then n_records x record (7 bytes)     (sorted by chunk)
u16 n_units, then n_units x [u8 use, u8 homes, u8 floors, u16 cells]
u16 n_doors, then n_doors x [u16 unit, u8 i, u8 j, u8 level, u8 rot, u8 enter]   (rot: the face, as a face mount)
f32 travel x, y, z, yaw
u32 n_foliage, then n_foliage x [u8 species, i16 x (dm), i16 z (dm), u8 y (0.25 m), u8 rot (/256 turn), u8 scale (/64)]
                     (rot = yaw about +Y turning the plant's +Z; wall climbers stand on the wall's face plane
                      with +Z out of the wall)
```
`use`: 0 home, 1 shop, 2 work, 3 civic, 4 stair, 5 passage, 6 storeroom, 7 vacant.  Homes beyond the island's
canon population are repurposed (workshops, factories, dentists, stores, shrines, storerooms, vacant); the twin's
units carry the `kind`.

## The readable twin `<id>.json`
`"palette_mode": "kit_variant"`: every slot of a piece takes `pieces.json palettes[civ][variant][slot]` (no
slot_palette needed).  `lights`: `[[x, y, z, kind, "#rrggbb"]]` in the island frame -- kind lantern, fluoro, festoon,
lamp (interiors), shop, door, stall, fountain, minaret, tower; the colour is the variant's emissive.
Header and stats, "palettes" (the kit variants), "mounts", units, doors (with their unit's use), `travel`, `anchors` (sign anchors
`[name, x, y, z, yaw]` like the old models' anchors), `walk` (`nodes [[x, y, z, kind]]`, `edges [[a, b]]`), `pads`,
`foliage_species`, `chunks` (per chunk: placements, estimated triangles), and the lattice's per-level occupancy as
strings (debug).
