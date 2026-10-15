# R4: design: warren cities on the sky islands (2026-10-15)

The method survey and sources are in r4_methods.md. This document is the concrete pipeline: what runs where, the data
formats, the kit, chunking and LODs, the budgets and the build steps.

## 0. Decisions
1. **Generate offline, assemble at runtime.**
   - A Python tool (`tools/sky/warren/`) grows each island's city on a 3D cell lattice and chooses kit pieces. It
     writes a compact **placement file** per island.
   - The game merges the shared kit pieces into chunk meshes on worker threads.
   - Why: deterministic and inspectable (previewed in Blender); no solver at load; and a footprint of about 50–150 KB
     per island against round 2's ~1.5 GB of model glbs.
   - Every mesh is a **shared kit piece**, as the user asked; the only per-island data is placements.
2. **No per-building models and no lots.** The city is one fused mass. "Buildings" exist only as units (rooms) for the
   population and the doors.
3. **A full rule pass, no free WFC.** The mass grows by civilization rules in epochs. Pieces are chosen by
   dual-grid / marching rules from the occupancy and neighbours, with local adjacency constraints for facade strips.
   It's one deterministic pass with no backtracking, so nothing fails silently.
4. **Interiors only where you can enter.** Ground-floor shops on main streets and plazas, and a share of home doors,
   get a one-cell interior from interior kit pieces. Every other window uses a procedural **interior-mapping**
   shader: a fake room with depth, lit at night, with a sky-fresnel reflection by day.
5. **Islands move, so nodes must be few.**
   - Chunk meshes are RenderingServer instances owned by SkyIsland, not nodes; the transforms are pushed in
     `_place_islands`.
   - Each island has one StaticBody whose chunk collision shapes exist only near the player.
   - Target: ≤ 60 nodes per near island, against ~2,000 today.
6. **Hash in the island's frame.** Every procedural pattern (windows, signs, foliage) uses local coordinates
   (lesson: the lod_vc flicker).

## 1. The lattice
- Cell: **3.0 m × 3.0 m in plan × 3.2 m storey** (storey 0 is the deck). Civilizations vary proportions *within* a cell
  through their pieces: wall thickness, opening sizes, eave depth. Tower civs use 2 cells per storey for
  double-height halls.
- The island plan is about 100 × 100 cells at most (300 m), and up to 16 levels (51 m). Low g allows a little more
  for tower civs.
- Each cell stores:
  - `occ`: empty, room, open court, or roof terrace;
  - `epoch` (0–5): the layer that built it;
  - `use`: home, shop, work, civic, stair, or passage;
  - `unit` (id), `support` flags, `access` (reachable);
  - `enter` (has a real interior);
  - `light` (night pattern seed).
- The site (from make_islands) feeds in:
  - outline, height grid, dock faces and bridge clearances;
  - tether corridors (a vertical cylinder above each anchor kept empty);
  - lark pads, hoists, launchers;
  - water, pastures, the fence band.

## 2. Growth in epochs
Each civilization is a Python rules module (`civ/<id>.py`) with parameters and hooks. A generic engine runs:

**E0, the site and the spine (walkability first):**
- Main streets 8–12 m from the main bridges to the central plaza (a loop or cross on islands of 6+ blocks); 3–4 cells
  wide, paved, open to the sky.
- Activity nodes: the central plaza (14–21 m) and one more per ~275 m.
- Greens: the pond banks, plus one garden court per 3 blocks, so everything is within ~230 m of green.
- The pond, pasture and wild margins are reserved.
- Result: a guaranteed connected **public network** (the Spelunky "critical path").

**E1, the foundation (the oldest layer):** the civ's founding plan on the free land.
- Lot and courtyard patterns: courtyard houses round a court (Arabic and Persian), tower-house footprints (Yemeni),
  shophouse strips (Chinese and SE Asian), mohalla clusters on galis (Karachi and Delhi), perimeter blocks
  (European), fused megablocks (Kowloon), and so on.
- Lanes grow by the civ's street grammar from the spine: tree-like cul-de-sacs, a grid or a herringbone; 1–2 cells
  wide. Blocks are kept to ≤ 15 cells between lanes or passages.
- Heights are 1–3 levels, in the civ's masonry. `epoch = 0`.

**E2–E4, accretion (centuries):** each epoch applies the civ's rules, weighted by street frontage, age, and the
height of neighbours:
- **Rise:** a room on a roof, flush or set back.
- **Jetty / cantilever:** an upper cell over a lane wider than 2 cells. Lanes narrow upward.
- **Sabat / bridge:** a room or footbridge across a lane of ≤ 2 cells at level ≥ 2. A run of these makes a **covered
  passage** (a tunnel).
- **Infill:** courts filled (Kowloon). Protected civs keep their courts (Arabic, Persian).
- **Towers:** tower civs raise single footprints to 6–9 levels.
- **Roof world:** terraces, roof gardens, pigeon lofts, water tanks, shacks.
- **Structure:** a cell needs support below, a cantilever ≤ 1 cell from support, or a span of ≤ 3 cells with both
  ends supported.
- **Access:** after each epoch, any unreachable occupied cell gets an external stair, a ladder or a bridge to the
  nearest reachable cell, or is removed.

**E5, the cyberpunk overlay (the newest layer):** neon and screens on the main street and plazas, cables across
lanes, AC units and pipes on the newest walls, tin and plastic shacks on roofs, lantern strings. Its density is a
civ parameter (Kowloon 1.0, Ghadames 0.3).

**After the epochs:**
- Units are flood-filled, with doors on lanes, streets and stairs.
- `enter` is set for ground-floor shops on the spine and plazas (100%), one door in four on lanes, and civic halls.
- The arrival point (fast travel) is set on the gate plaza.

## 3. Choosing pieces (dual grid)
For each level, take the corner lattice: each corner looks at its 4 surrounding cells (2D marching squares per level),
plus the cells above and below.
- **Walls:** each exterior face of an occupied cell gets a `wall.*` piece. The civ's facade rules choose its kind:
  plain, window, window pair, door, shopfront, screen, balcony, bay, or arch passage.
  - The choice depends on level, use, the width of the lane it faces (a narrow lane gets small windows high up), its
    epoch (material and age), and vertical stacking (screens and bays align up a facade, as Gehl's "varied edges" and
    the civ's rhythm want).
  - The strip constraints are small adjacency tables, for example "a shopfront run continues", "an arcade bay
    repeats".
- **Corners:** outer corners, inner corners and corner columns come from the corner configuration (6 unique up to
  rotation). These make the civ's corner: rounded mud-brick, quoins, timber posts, chamfers.
- **Roofs:** a roof edge (parapet, eave or gutter) on each top-face edge with an empty neighbour; roof field pieces
  (terrace, tile, tin); civ crowns (crenels, the white bands of Sana'a, pagoda eaves, gable fronts).
- **Ground and passages:** paving per cell (main-street paving, lane paving, plaza, garden), steps where the deck
  rises, stairs, and arches where a lane passes under rooms.
- **Decoration:** signs (anchors for SkySigns), cables, AC units, tanks, laundry, lanterns, planters, awnings, vines,
  shrines, and foliage instances.

## 4. The kit (shared parts library)
Pieces live in the shared library (remake/blender/sky/components + gbkit). Each piece is a 3 m bay or a corner, with
material slots. A piece is used by many civs, with civ palettes and parameters chosen at build time; a small set of
mark pieces is civ-specific. Rough count:

| Group | Pieces | Variants |
|---|---|---|
| Walls (3 m bay × 3.2 m) | plain, window ×3 sizes, window pair, door, shopfront ×2, screen panel (lattice family: mashrabiya / jali / grille / shoji), balcony ×3 (cage, timber, iron), bay/oriel ×2, arch passage ×3 (round, pointed, horseshoe), blind arch | each by wall thickness (thin / thick) |
| Corners | out, in, column, rounded, chamfer | thin / thick |
| Roofs | terrace, parapet edge ×4 (plain, crenel, stepped, jali), eave edge ×3 (tile, pagoda, tin), gable front ×3, dome cap (civic only), pagoda tier | |
| Ground | paving ×5 (main, lane, plaza, garden, court), steps, stair (int / ext / spiral), ladder, bridge (plank, timber, steel), arcade pier | |
| Interior (enter cells only) | floor, ceiling tiles ×6 (existing), counter, shelves, table set, bed, lamp | |
| Overlay | cable span, AC, water tank, pipe run, sign mounts (blade, box, board), lantern, festoon, laundry, shack panel ×3 | |
| Plants | per species (see §6) | |

The total is about 150 shared pieces, plus ~3–6 mark pieces per civ, against 335 unique models in round 2.

**Material slots:** wall, trim, frame, glass (interior-mapped), screen, roof, metal, fabric, emissive. A civ's palette
fills the slots, and a piece can wear any civ's palette.

## 5. Runtime (Godot)
- **Data:** `remake/sky/warrens/<id>.bin.gz`. Its contents:
  - the civ id and chunk table;
  - per chunk, records of `[u16 piece, u8 cx, u8 cz, u8 level, u8 rot|flags, u8 palette slot|epoch]`, 7 bytes each;
  - the unit and door list;
  - the arrival point;
  - foliage instances `[u8 species, i16 x, i16 z, u8 y, u8 rot, u8 scale]`.

  At about 25k placements per island that's ~175 KB raw and ~50 KB gzipped, about 5 MB for all 100.
- **SkyWarren** (replacing the buildings and LODs in SkyIsland's near tier):
  - The kit's surface arrays are cached once per piece (main thread).
  - Per chunk (8×8 cells, 24 m × 24 m, all levels), a worker concatenates the arrays per material slot, applying the
    placement transforms and palette (vertex colour); the main thread calls `add_surface_from_arrays`.
  - Each chunk is one RenderingServer instance per material (~6–8 surfaces in one mesh: one instance, ~6–8 draws).
  - **Chunk LOD:**
    - LOD0 (< 70 m): full pieces.
    - LOD1 (70–220 m): built from the same lattice with box pieces only (one quad per exterior face, window pattern
      in the shader, crowns kept), about 1/15 the triangles.
    - LOD2: chunk groups (4×4 chunks) merged into one hull per island quadrant, beyond 220 m.
    - Past the near tier, the existing island lod1/lod2 glbs, regenerated from the lattice hull.
  - **Collision:** one StaticBody per island. Chunk shapes are boxes per occupied face, merged into a
    ConcavePolygonShape per chunk, and exist only for the chunks within 40 m of the player (and only while
    PHYS_R is active).
  - **Nodes per near island:** island root, StaticBody, ~4 MultiMeshInstances (foliage), SkySigns' 4 merged meshes,
    NPCs, bridges, and a lark impostor (a single mesh until you come within 40 m). That's ≤ 60, against ~2,000 now.
- **Windows (lod_vc and the warren material):**
  - Interior mapping, procedural: a box room (floor, ceiling and back wall colour from the civ palette, a furniture
    silhouette card from a 4-shape atlas, curtains on 30%).
  - A night lamp glow decided per window by a local hash and the hour's lit share.
  - A daytime fresnel mix of the global `sky_color`.
  - Screens (mashrabiya) are real geometry in front.
  - At night, additive lens-flare sprites (a MultiMesh) only on the brightest lanterns, signs and windows within
    150 m. They make the night glitter, and they hide the absence of interiors.
- **SkySigns:** reads sign anchors from the placements. **SkyFolk:** walks the walk graph built from the lattice,
  which includes stairs and roof terraces.

## 6. Plants (per civilization)
- Species are low-poly meshes (≤ 250 triangles) generated offline by space colonisation, or hand-built in the
  existing glb writer:
  - date palm, fan palm, coconut palm;
  - cypress, olive, citrus;
  - bamboo clump, banyan, pine, maple, plane tree, willow;
  - bougainvillea and jasmine shrubs, cactus and agave;
  - ivy and vine cards; potted plants; roof-garden beds.
- The vertex colour R channel is the sway mask.
- `foliage.gdshader`: toon shading, sway from TIME plus the instance phase (INSTANCE_CUSTOM), per-instance tint, alpha
  scissor for leaf cards, and wind phase hashed in the island frame.
- One MultiMesh per species per island quadrant. Visibility: near 0–180 m; cross-fade to the LOD2 hull's painted
  canopy beyond.
- Placement comes from the lattice: courts (Arabic: a palm and a citrus), plazas (a shade tree), lane edges,
  planters by doors, roof gardens, pond banks, and vines on old (epoch 0–1) walls facing lanes. Each civ module lists
  its species and densities.

## 7. Budgets (Steam Deck, 60 fps)
| What | Budget |
|---|---|
| Frame, aboard | CPU ≤ 10 ms, GPU ≤ 12 ms |
| Sky physics (`_place_islands` etc.) | ≤ 0.8 ms per tick |
| Draws, aboard (whole scene) | ≤ 900 |
| Near island | ≤ 250 draws, ≤ 700k triangles |
| A LOD0 chunk | ≤ 25k triangles, ~8 draws |
| Foliage instances per island | ≤ 3,000 |
| Lens flares | ≤ 300 |
| Real lights near | ≤ 24 (shared with StreetLights) |
| Data | ≤ 10 MB placements + ≤ 40 MB kit (all islands, all civs) |
| Load | ≤ +0.5 s; chunks build lazily as islands come near (≤ 3 ms of main thread per frame) |

## 8. Fast travel
SkyIslands already offers the "Floating Cities" group in the PDA Navigator's Travel page and holds the traveller until
the deck loads. The generator writes `travel` (the gate plaza by the main bridge, a 6 m clear disc with a landmark in
view), which `travel_local(i)` reads.

## 9. Implementation steps
1. **The engine and two civs** (Arabic medina with tower houses; Kowloon megablock):
   - `tools/sky/warren/` holds the lattice, the epochs, the dual-grid selection and the writers.
   - Debug output: matplotlib level slices, plus a Blender preview that assembles the real kit.
   - Checks: connectivity, support, clear tether corridors, budgets per chunk.
2. **Kit v1 for those civs** in the shared library, with the piece contract (bay size, origin, material slots) and
   the dedup checks (check_models).
3. **Runtime:**
   - SkyWarren: decode, worker merge, RS instances, chunk LODs, collision near, the interior-mapped window material,
     lens flares.
   - Wire SignAnchors, the walk graph and the arrival point.
   - **Measure:** 60 fps aboard, day and night, before going further.
4. **Plants:** the foliage shader, species meshes, placement.
5. **Scale out:** add civ modules one by one from research streams 1–3, at least 20 families. Each comes with a
   preview, a visual review against its research references, and a performance check.
6. **Island LODs** from the lattice hulls. Remove the round-2 SKY-<style> models and records. Confirm the footprint
   with an export.
7. Document in research/sky_islands/warrens/ and memory.
