# Requests from RUNTIME to KIT and GENERATOR

(`kit_requests.md` is written by the generator's `kit_requests.py`, so RUNTIME's requests are kept here.)

## 2026-10-15
1. **KIT, the medina's shutters.** In Ithaca's lanes (`research/sky_islands/img/warren_game_ithaca_lane_day.png`),
   `wall_shopfront_a_k` ("rolling shutter half down") reads as a heavy black slatted slab. The cause is the
   maghrebi_medina palettes' `metal` slot, `#3a3632`, in all 4 variants. Asked:
   - give the medina painted timber shutters or doors (`frame` colour, or a green or blue painted `metal` such as
     `#4f6b4a` / `#2d5f8a`), or a medina shopfront without a roller shutter;
   - in general, no near-black slot over a whole wall bay: in the toon light it reads as a hole.
2. **GENERATOR, the wall climbers' frame.** `bougainvillea`, `jasmine` and `banyan_wall` are written at the HOUSE
   cell's centre, scattered by up to 0.8 m, and their `rot` is the face index 0..3 stored as radians (pick.py FACE:
   0 −Z, 1 −X, 2 +Z, 3 +X).
   - SkyWarren currently snaps them to the cell, moves them out onto that face and turns them to face out (+Z out of
     the wall, SkyPlants' frame).
   - Asked: write them on the face, with yaw = atan2(dx, dz) of the outward direction, so the runtime takes them as
     they are. Say when, so the snap can go.
3. **GENERATOR, species.** Species with meshes in `SkyPlants` (godot_project/remake/scripts/sky/sky_plants.gd, all
   ≤ 250 tris):
   - date_palm, fan_palm, coconut_palm, bitter_orange, lemon (citrus, orange);
   - fig, olive, maple, plane_tree, cypress, pine, willow;
   - banyan_tree, banyan_wall, bougainvillea, jasmine (ivy), grapevine_pergola;
   - pot_mint_geranium, potted_plants, roof_garden, reeds, bamboo, banana, lotus (water_plants).

   Any other id draws as a plain shrub, with a warning. Use these ids per civ, or ask for new ones here.
4. **GENERATOR, distant models.** After writing warrens, run `~/.venvs/ssc-assets/bin/python tools/sky/warren/lods.py`.
   It rewrites each warren island's `.lod1.glb` / `.lod2.glb` city from the lattice. Then reimport with
   `godot --headless --path godot_project --import`.

### KIT reply (2026-10-15)
- 1 done: the maghrebi_medina palettes' `metal` is now painted per variant (`#4f6b4a` green, `#2d5f8a` blue,
  `#6b5236` timber, `#3f6f6a` teal), so `wall_shopfront_*` shutters read as painted. And every family's palette
  is floored: `metal` average sRGB >= 64, `frame`/`screen` >= 48 (no near-black slot over a bay). In pieces.json now.

## 2026-10-15 (afternoon): flicker and walking (see flicker.md)
5. **KIT, coplanar faces.** 138 pieces have overlapping faces of different slots within 4 mm (`kit_coplanar_faces.txt`;
   check with `tools/sky/warren/check/coplanar.py`).
   - The runtime lifts overlay slots by 3–18 mm as a stopgap (`SkyWarren.SLOT_LIFT`).
   - Asked: offset overlays by at least 5 mm, or remove the face beneath. Fix the same-slot overlaps (towers,
     roof ends, badgir) and wall_talar_k's mid.
6. **GENERATOR, duplicate placements.** The same piece twice in one cell at one height: SKY-071 149, SKY-078 55
   (`tools/sky/warren/check/placed.py`). They z-fight when their palette variants differ.
7. **GENERATOR, stairs entered from the side.** The walk graph links a stair cell to its neighbours across the
   stair's sides. Mid-ramp, that side is a 0.4–0.8 m lip the player can't climb. Seen walking:
   - SKY-071 (1,36)→(1,37);
   - SKY-099 (8,36) paving → (9,36) step_low_4 rot 0, and (6,6);
   - the stuck points in `reference/tmp/walk_*.out`.

   Asked: only link a stair along its axis (foot ↔ low neighbour, head ↔ high neighbour). Alternatively, where
   cells beside a stair are walked, give them stairs at the same quarter and axis, so the side edges match.

### KIT reply to 5 (2026-10-15): coplanar faces fixed at the source
- `tools/sky/warren/check/coplanar.py` now reports **0 pieces** for `kit.glb` and for `kit_mid.glb` (it was 138).
  **The SLOT_LIFT stopgap can come out.**
- Every piece passes the KIT's new flicker pass (`remake/blender/sky/warren_kit/flicker.py`, run by `build.py`) at
  a stricter 2.5 cm: no two same-facing, overlapping faces anywhere in a piece are closer than that.
  - Small overlays (strips, decals, signs, trims) step OUT to 2.8 cm.
  - The hidden part of a face covered by a bigger one is cut away.
  - Wall and edge bays are clipped to their own 3 m width (eaves, roofs and louvres no longer lie flush on the
    neighbour bay's).
  - Corner pieces stand 5 cm proud of the bays they join.
  - Parts hung under a projection (soffits, corbels) step 3 cm back, off the storey below.
- Source fixes: pave joint sheets 3.5 cm down; skirts 3 cm in; garden kerbs 6 cm in; lattice cross-bars 3 cm proud;
  roof ribs 3 cm off the slope; gable-end walls tucked under the roof slopes; tower sides each own one corner
  (mudejar, baroque belfry, badgir); stair_run's bow-tied stringers re-ordered; arch mouldings 3 cm off their
  reveals; the medina / Cairo / Levant / Newar / jharokha details listed in the KIT report.
- The 3 flagged mids (wall_talar_k, wall_zellij_k, minaret_square_carved_top) are clean.

## 2026-10-15 (evening): island flags and trailing banners (SIGNS -> RUNTIME)
The user: "Each Island should be trailing large colorful banners that stretch 300m below the islands advertising it's
name and its wares. Each Island will need it's own ethno/political flag." The art is made; the runtime is yours.

**Art (made by `tools/signs/make_flags.py`; doc `research/sky_islands/flags.md`; index `godot_project/remake/signs/signs.json`):**
- `remake/signs/flags.png`: 100 flags of 128 x 80 px in a 10 x 10 atlas. They are RGBA, with alpha cut in the forked
  fly; every Skein flag is swallowtailed. `signs.json` `flags.islands[SKY-xxx]` gives `region`/`uv`, colours, layout and
  emblem. All are marked `provisional`.
- `remake/signs/sky/banners/SKY-xxx.png`: one 256 x 1024 strip per island holding four 64 x 1024 banners side by side
  (`banners.islands[id].banners[k].uv`). Banner 0 is the name, 1 the wares (pictograms and words), 2 a streamer in the
  flag's colours, 3 the clan. The ornate cap is at the top (v = 0), the tail at the bottom.
  `SKY-xxx_emit.png` (128 x 512, L) is the night mask for the LED edges, bulbs and lettering. The 100 strips total about 5 MB.

**Asked:**
1. **Trailing banners.** Each island trails its 4 banners, about **300 m** long (`banners.length_m`) and about 18 m wide.
   - Hang them from the island's underside rim, spread round it (e.g. 90° apart, or two pairs on the downwind side).
   - Build each as a ribbon mesh: a strip of about 24–32 segments down the length, UV v 0 at the top to 1 at the tail.
     Stretch the texture over the whole length (it is drawn at 1:16 for a 1:16 ribbon); don't tile it.
   - Use a **wind shader** (vertex): sway and flutter increasing toward the tail, phase per banner, and trail
     downwind of the drift (`SkyIsland` travel velocity: the ribbons stream behind and slightly aft).
     Double-sided, with alpha scissor for the forked tails.
   - **One draw per island:** put the 4 ribbons in one mesh with one material on the island's strip texture. Use
     emission = albedo x emit mask x `night` (the existing night gating, as `sky_bulbs`), so the names glow at night
     and read from the floor.
   - **Furl them** (shorten to about 30 m, lerping over 20 s) when the island is below about 900 m, moored at a
     market (`market_moorings`), or docked or lashed. Hide them beyond the island's far-LOD distance, or keep a
     2-segment card.
   - The banners advertise the island's wares to the floor. Keep them clear of the hoist lines and the gondola ropes
     (the drop zone under the Box).
2. **Flags** on masts and rooftops:
   - the Box mast top;
   - the Mooring Office tent and the gondola station;
   - 2–6 rooftop flagpoles on the tallest roofs (the warren's `landmark` and towers).

   Each flag is a cloth quad of about 3 x 1.9 m (12 x 7.5 m on the Box mast) with the same wind shader at a faster
   flutter, its atlas cell from `flags.islands[id].uv`, and alpha for the fork. One material for all flags (the atlas)
   lets them batch: a MultiMesh per island, with the cell offset in INSTANCE_CUSTOM.
3. The flags are also the island's identity on the floor: the market tents, the PDA island list, and the Lowliners'
   porch flags. Please expose `SkySigns.flag_uv(island_id)` so other systems can use them.

## 2026-10-15 (evening): bitmap shop signs on the islands (SIGNS -> RUNTIME)
The user: "bitmap signs on every shop". The floor's city shops now have them (`remake/scripts/city_signs.gd`). The
islands are yours (`sky_signs.gd`, `sky_warren.gd`), so here is the art and what to do with it.

**What there is to sign:** the 100 warrens have **37,734 sign anchors**: 18,807 `sign_box`, 11,073 `sign_blade` and
7,854 `sign_board`. Their units include 3,972 shops, 2,739 stores, 4,302 dentists, 17,385 workshops and 11,559 factories.

**Art (index `godot_project/remake/signs/signs.json` `cells`; review `research/flea_markets/img/signs_sky_a.jpg`, `_b.jpg`):**
- `remake/signs/sky_a.png` (B1–B4) and `sky_b.png` (B5–B9): **per warren family three 256 px blanks**, a fascia
  `sky_<family>_fascia`, a blade `_blade` and an emblem `_emblem`. There are 4 extra variants (`..._emblem2`,
  `..._frame`, `..._blade2`) and 12 shared Skein cells (`sky_shared_*`: Mooring Office, Weigh House, gondola
  station, Line Hall, tent planks, pennants, fare board, Crew Tent, Low Lashing banner, market warden, rope steward).
  `*_emit.png` is the night mask; the cells keep their content rect (`content`) for the aspect.
- `remake/signs/stalls.png` (`stall_*`, `festoon_*`) holds tent and stall signs, lanterns, bulb strings and pennant
  strings. `goods.png` (`goods_*`, G8) holds island trade goods for the stall tables.
- The 5 sign styles per broad cultural group (B1–B9) are in `research/flea_markets/09_sign_styles.md` (Islands).

**Asked:**
1. **Box and board anchors:** use the family's fascia blank as the board texture (UV into the cell's `content` rect).
   Draw the name on top with your procedural names, a light emissive tint and the family palette's `emissive`.
   - **Box** (lightbox) anchors use the emblem cell or the fascia, with the whole face emissive at night.
2. **Blade anchors:** use the blade cell, with the name stacked vertically for the East Asian families (B4, B5),
   rotated for the others.
3. **Variety within a culture:** pick per unit from the family's cells (fascia, blade, extra variant) and from the 5 group
   styles' tints, hashed per unit. Neighbouring shops should differ while the lane stays one place.
4. **One material per island:** both sky atlases, or a per-island packed atlas if you prefer. Keep it to one or
   two draws per chunk (the warren's chunks).
5. If you'd rather have the names baked into bitmaps (like the floor's), export the island's shop list
   (unit -> name, family, anchor kind, size). `tools/signs/make_signs.py` can grow an island mode that renders
   them into per-island atlases.

### SIGNS addendum (2026-10-16): banner GRID atlases for `SkyBanners` / `sky_banner.gdshader`
Your shader samples one `atlas` as a grid (`atlas_grid`, cell = `INSTANCE_CUSTOM.a`), so the banners now also come
packed for it:
- **`remake/signs/banners_a.png`** (2048 x 7168, `_emit.png` 1024 x 3584 L): a **32 x 7 grid of 64 x 1024 cells**. Island
  index i (its order in `sky_islands.json` / `sys.islands`) has its **name banner in cell 2i** and its **wares banner in
  cell 2i + 1**.
- **`remake/signs/banners_b.png`**: the same grid, with the flag-colour streamer in cell 2i and the clan banner in 2i + 1.
- **Index:** `signs.json` `banner_atlas`: `{png_a, emit_a, png_b, emit_b, grid: [32, 7], cell_px: [64, 1024],
  islands: {SKY-xxx: {index, name, wares, flag_streamer, clan, atlas: {...: "a"|"b"}}}}`.
- **Use:** set `atlas = banners_a`, `atlas_grid = (32, 7)` and `has_atlas = true`. Give the banners on an island's
  outline cells `2i` and `2i + 1` alternately; a 3rd or 4th banner could use `banners_b` through a second material, or
  repeat. Use v 0 for the cap (top of the ribbon) and 1 for the tail.
- **Emission** = albedo x `emit_a` x night. Use alpha scissor for the forked tails.
- **Note:** `SkyBanners._atlas_cells()` (`sky_banners.gd:155`) looks up `banners[id].cell` in `cells` keys. That
  doesn't match: read `banner_atlas.islands[id].name` instead (an int, already the grid cell). The per-island strips
  under `remake/signs/sky/banners/` hold the same art; drop them if you use the grids.

### SIGNS addendum (2026-10-16): blend the people and the architecture (the user's rule)
An island's people (`heritage` in sky_islands.json) and its architecture (`warren`) often differ: Ithaca is Black
Anglo people in a Maghrebi medina. The user: "it shows how cultures mixed. There will be a lot of mixing as well as
emergent characteristics." So the island signs should **blend both**, plus island-specific touches (clan, trade,
landmark, customs). Don't pick one side. The flags and banners now do this:
- **Flags:** the warren culture's motif in the upper fly, coloured by the heritage. Fields are the clan's colours;
  the layout comes from governance and the emblem from the trade.
- **Banners:** the name and wares banners letter in the warren culture's manner; the clan banner letters in the
  heritage's manner, with heritage-colour edge bands.
- **Asked for shop signs:**
  - Use the warren family's blank (fascia, blade, emblem) as the frame and ground.
  - Draw the name in a lettering chosen by the shopkeeper's heritage, or the island's when no per-person heritage
    exists. The heritage -> font and accent table is `HERITAGE` in `tools/signs/make_flags.py`; use it, or ask for an
    island atlas render.
  - Tint the LED edge or name glow with the heritage accent on a share of shops, by hash, so the mix varies lane to lane.

### AUDIT / GENERATOR / KIT (2026-10-16, the offline audit stream; handoff_audit.md)
- **Reimport needed:** kit.glb, kit_mid.glb and pieces.json were rebuilt (remake/blender/sky/warren_kit). The changes:
  - shopfront_a now has a door frame and pass;
  - steps_up ramps are the full 3 m wide; spiral ramps start at y 0;
  - basketball_court collides at its surface (a ramp quad);
  - ground pieces are set down so their tops are at y 0;
  - flying-eave hip roofs are closed;
  - utility_pole collides as a frame (the pole only);
  - MID models stay inside their pieces.
  All 100 warrens are being regenerated (make_warren --all, then lods.py). Please run `--headless --path godot_project --import` under the lock before the next in-game walk.
- **Mirrored offline** (tools/sky/warren/audit/assemble.py ASM 5): your closed door leaves, entered-room floors and
  bridge threshold ramp.
- **No runtime change requested by the audit at this point.** If you change a collision rule, tell me and I'll mirror it
  (assemble.py `Kit._rule` / `collision`), then re-run `calibrate.py contacts` on a fresh passcheck sweep.
