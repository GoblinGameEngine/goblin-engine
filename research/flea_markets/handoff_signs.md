# Handoff: signage (sign art, flags, banners, city shop signs)

State as of 2026-10-16. Nothing is committed (the user said: don't commit). Every file below is untracked or modified in
the working tree.

## 1. Files made or changed

### Tools (`tools/signs/`, all new)
| file | what it does |
|---|---|
| `sheet_manifest.py` | What is in every cell of every Grok sheet, in reading order. A1–A5 are markets, B1–B9 island families (`B_FAM`), C1–C4 business blanks (`BIZ`), G1–G10 street life (`G`, at the end of the file). It is the single source for the B/C prompts and for the atlas index. |
| `crop_sheets.py` | Cuts the sheets into 256 px cells: keying, tile flooding, slivers, despill, emissive mask. It packs the atlases in `ATLASES`, writes `signs.json` (it keeps other sections: `keep.update(index)`) and the contact sheets. `BOXES` holds hand boxes (B1, B2, G9), `EXTRAS` the extra cells, `TILED` the sheets with coloured tiles. Default output is 256-colour PNG; `--full` gives RGBA, `--debug` writes box overlays to /tmp/signs_debug. |
| `make_flags.py` | The 100 island flags and 400 banners, plus `research/sky_islands/flags.md`. It adds the `flags` and `banners` sections to `signs.json`. |
| `make_signs.py` | City shop signs: inventory, names, style assignment, render, shelf-pack per town, `city_signs.json`. It also writes `research/flea_markets/09_sign_styles.md`. `--only <Settlement>` renders one town (no JSON or doc). |
| `fetch_fonts.sh` | Fetches 41 OFL/Apache Google Fonts into the gitignored `reference/fonts/`. Only rendered output ships; the fonts stay out of git (OFL allows that). Rerun it on a fresh checkout before running make_signs or make_flags. |

Run everything with `~/.venvs/ssc-assets/bin/python` (PIL, numpy, scipy). Order:
`fetch_fonts.sh` → `crop_sheets.py` → `make_flags.py` → `make_signs.py`. make_signs reads `biz.png` and
`signs.json`, both from crop_sheets.

### Game data (`godot_project/remake/signs/`, all new; about 28 MB in all)
- From crop_sheets (cells are 256 px, 8 columns; each has an `_emit.png`, an L-mode night mask at the same size):
  - `markets.png`: 45 cells from A1–A5;
  - `sky_a.png`: 68 cells from B1–B4; `sky_b.png`: 80 cells from B5–B9;
  - `biz.png`: 64 cells from C1–C4;
  - `mascots.png` 32 (G1, G2), `ads.png` 14 (G3 billboards, G4 posters), `small.png` 32 (G5 menu/A-frame/OPEN, G10
    decals/neon outlines), `stalls.png` 32 (G6 stall and tent signs, G9 lanterns and festoons), `goods.png` 50 (G7
    flea goods, G8 island goods).
- `flags.png`: 100 flags of 128 x 80 in a 10 x 10 grid, alpha cut in the forked fly.
- `banners_a.png` / `banners_b.png` (2048 x 7168, 256 colours; `_emit.png` L at half resolution): grid atlases for
  the RUNTIME's `sky_banner.gdshader`, 32 x 7 cells of 64 x 1024. Island i has its name in cell 2i and its wares in
  2i + 1 of `a`; its flag streamer in 2i and its clan in 2i + 1 of `b`. Indexed in `signs.json` `banner_atlas`.
  They are made by `make_flags.py pack_banner_atlases()`.
- `sky/banners/SKY-xxx.png`: one 256 x 1024 strip per island, four 64 x 1024 banners side by side. Each has an
  `SKY-xxx_emit.png` at 128 x 512 (L).
- `city/<Settlement>.png` (22 towns): signs shelf-packed at 48 px high in 2048-wide atlases, 256 colours. Each has a
  `<Settlement>_emit.png`: RGB at half resolution, holding the glow colour (albedo x night mask).
- `signs.json`: the sections `cells` (every crop_sheets cell), `atlases`, `flags`, `banners` and `banner_atlas`.
- `city_signs.json` (1.3 MB): the city quads (schema in §4).
- The `.import` files for all of these were made by the RUNTIME agent's `--import` and by my test's import.

### Game scripts (wiring the city signs)
- **NEW** `godot_project/remake/scripts/city_signs.gd`: a static helper with **no class_name**. Every user preloads it
  as `const CitySigns := preload(...)`, so no `--import` is needed. Its functions:
  - `drop_rows(model)` (thread-safe; called from merge_kit on workers);
  - `attach(root, building_id)`: one MeshInstance3D "city_signs" per building, one surface, the town's shared material;
  - `set_night(n)`;
  - `signs_of(id)`.

  It **disables itself** when the first town atlas isn't imported (`ResourceLoader.exists`); then the 3D lettering
  stays. Material: albedo atlas, emission texture = the emit atlas, alpha scissor 0.5, no shadow,
  `visibility_range_end` 240 m.
- `godot_project/remake/scripts/building_loader.gd`:
  - `:3` preloads CitySigns;
  - `:307` in `merge_kit` loops rows with an index and skips the kit "T" rows listed for the model
    (`drop_rows`): those are the 3D letters the bitmaps replace;
  - `:537` `set_night()` calls `CitySigns.set_night(n)`.
- `godot_project/remake/scripts/detail_streamer.gd`: `:3` preload; `:464` `_put_lod1` calls
  `CitySigns.attach(root, r.id)` (ordinary streamed buildings).
- `godot_project/remake/scripts/lod_clusters.gd`: `:2` preload; `:287` attaches for every root it builds itself
  (landmarks; all buildings when not streaming), `if bake_into == null`.
- All four pass `godot4 --check-only`.

### Docs
- `research/flea_markets/08_signage_briefs.md`: a margin-fix note in §0.5 and a Status section at the end.
- `research/flea_markets/09_sign_styles.md`: generated by make_signs. It holds the 25 floor styles, the 9 x 5 island
  styles, the inventory and the style counts.
- `research/sky_islands/flags.md`: generated. The flag grammar and all 100 flags with their meaning.
- `research/sky_islands/warrens/runtime_requests.md`: two sections appended, "2026-10-15 (evening): island flags and
  trailing banners" and "bitmap shop signs on the islands".
- Contact sheets in `research/flea_markets/img/`: `signs_<atlas>.jpg`, `flags.jpg`, `banners_0..3.jpg`,
  `city_signs_<Settlement>.jpg` (day above, night below).

### Test helper
- `reference/tmp/signs_test.sh` (gitignored). Do NOT run it as is: it waits for the lock in a loop. It ran once and
  was killed partway (see §6). Use it as a recipe for short manual windows.

## 2. Grok usage: 33 images, all at 1024 px (image_gen offers only an aspect ratio), model grok-4.7-build-fast
Prompts as sent are in `reference/grok/signs/prompts/<sheet>.md`; images are `reference/grok/signs/<sheet>/<sheet>_img1.jpg`.
No 402 so far.

| sheets | images | for | problems |
|---|---|---|---|
| A1–A5 | 5 | market signs and mascots (names painted in) | A1: pink gradient, grid lines, 3 cells to the edge, clock keeps its white wall. A2: weathervane letters and MARLOWE garbled. A3: grey backdrop on cell 5; the TRADERS' apostrophe is lost. |
| B1–B9 | 9 | island blanks: fascia, blade, emblem x 44 families + 12 shared | B1 laid out in columns, B2 a 5 x 4 tile grid: both cut with hand `BOXES`. B4 has a literal horse head on the Jiangnan board. B5's HK blade has Chinese characters. Row-by-row prompts fixed the layout from B3 on. |
| C1–C4 | 4 + 1 fix | business board blanks with pictograms (north C1–C2, south C3–C4) | C1, C2, C4 have tiles; C2 has drop shadows. C4's `image_edit` fix (`C4_fix_img1.jpg`, used instead) changed only one cell. C3's lilac south_liquor board keys out. |
| E1, E2 | 2 | flag emblem silhouettes (specialties; governance, faith, landmarks) | E2 has an extra first row repeating E1 (6 rows; handled). |
| BN1, BN2 | 2 | banner caps, tails and borders per island cultural group (9 each) | The top halves repeat emblem cells (Grok carried over context); only the lower half is used. |
| G1–G10 | 10 | mascots N/S, billboards, posters, menu boards and A-frames, stall/tent signs, flea and island goods, festoons and lanterns, window decals and neon outlines | G2, G6, G10 have tiles (`TILED`). G9's light strings span cells (hand `BOXES`). The pink flamingo (G2) keys out. |

Images: 5 + 9 + 4 + 1 + 2 + 2 + 10 = **33**. Separately, three calls had failed tool attempts that saved no image.

## 3. Sign styles: 5 per region (catalogue `09_sign_styles.md`; parameters in `make_signs.py` `REGIONS`, line 74)
- **North Sea shore:** quarterboard, chandlery (Grok north pictogram), signal_enamel, teak_brass, cannery_stencil.
- **North Land:** federal_gilt, painted_shingle (pictogram), porcelain, brass_plaque, ghost_sign.
- **River towns (kettle_valley):** riverboat, deco_terracotta, mainstreet_porcelain (neon frame), rail_depot,
  serif_neon_script.
- **South Land:** googie_neon (Grok south pictogram), streamline_channel, mission_tile, citrus_label, drive_in_marquee.
- **South Sea shore:** surf_handpaint, tiki_carved, rotulo, supergraphic, beach_neon_script.
- **Islands:** 9 cultural groups x 5 named styles (`ISLAND_STYLES`). These are a spec for the RUNTIME only; no island
  name signs are rendered.

Each style sets fonts, 2–3 palettes, a case, a frame (one of about 25 frame painters in `render()`, `:543`), a letter
treatment, a night look, and affinities (`cats`, `era`, `wealth`).

**Assignment** (`pick_style`, `:448`) is deterministic per unit id. Each candidate's weight is:
- the region family's weight (river towns also draw on North and South by the gradient t, North Land near the river
  on the river family, South Land likewise);
- x its affinity for the business category;
- x the era (catalog `year_built` inside the style's years, else 0.25);
- x wealth (condition + the type's `price` + the town tier inside its range, else 0.3).

On top of that, a block lead style (a hash per 90 m block) gets x2.6 so the street reads as one place, and the
previous storefront's style gets x0.15 so neighbours vary. Vacant units go to ghost signs and planks, reading FOR LEASE.

## 4. City signs: how they're produced (`make_signs.py main`, `:871`)
1. **Slots** (`sign_slots`, `:331`). From each model's `buildings/<model>.kit.json` "T" rows (lettering), keep:
   - rows facing ±Z (the store front);
   - 2.3 < y < 9 m;
   - em scale 0.06–0.5;
   - material gold (metal > 0.5, yellowish) or neon (emission), from `<model>.mats.json`.

   Rows are grouped by (x, z); the lines are sorted top-down. The board rectangle is recovered from store.py's
   `sign_board` geometry (`remake/blender/gen/store.py:305-395`, `gen/common.py:154`):
   - h = 0.75 m (band1 − band0 − 0.05);
   - band0 = y0 + s0·0.35 − h·(1 − 0.5/n);
   - w from the text-size formula `size = clamp(bwid/max(6,len)·1.35, 0.14, 0.42)`, inverted, with clamped cases
     estimated and capped by the neighbour spacing − 0.6;
   - centre pushed 12 mm out along the lettering's +z.
2. **Units.** Board i is unit `<bid>/B<i>` (room manifests; or `<bid>/<i>`). A wide shop's extra board repeats the
   nearest B unit. Upstairs offices `<bid>/O<floor>_<n>` get one **brass tenant plaque** (0.96 x 0.48 m, at y 1.55,
   0.95 m beside the `STAIRHALL` street door from `remake/rooms/<Town>.json`) listing "floor name" lines.
3. **Names** (`shop_name`, `:413`). The catalog's old sign text is kept when the unit's hint matches its type (or it
   has none). Otherwise a proprietor is taken from the old sign (`proprietor()` strips trade words) or a local catalog
   surname, plus the type's noun (`NOUN`), in a hashed pattern ("X's Bakery", "X Bakery", "The X Bakery", "X & Co. …").
4. **Render** at 3x supersampling. The width is `48·w/h` px (96–576), the height 48 px (64 px/m). The mask levels:
   floodlit boards 60, backlit 150, neon, bulbs and lit letters 255.
5. **Pack** per settlement: shelf rows of 48 px in a 2048-wide atlas, the height rounded up to a power of two.
   Atlas: 256-colour PNG. Emit: half resolution, RGB = albedo x mask (it drives the material's emission texture
   directly).
6. **`city_signs.json` schema:**
   ```
   {"px_per_m": 64,
    "settlements": {Town: {png, emit, size:[2048,H], signs}},
    "buildings": {bid: {settlement, model, quads:[{uid, type, name, sub, style, region,
                         c:[x,y,z] centre, r:[..] reading dir, u:[..] up, w, h (m), uv:[u0,v0,du,dv]}]}},
    "models_drop_rows": {model: [kit row indices]}}
   ```
   The quads are in the building root's frame (placement transform = the glb root frame).
7. **Totals:** 4,225 signs (3,354 boards, all signed, plus about 870 plaques) in 22 atlases, **13.7 MB**. Port
   Carrow has 463+ signs (2048 x 4096); Solana Point is similar.

**Inventory** (also in 09):
- Floor units 10,031; shop units by region:
  - North Sea shore 1,476;
  - North Land 675;
  - the river towns 1,046;
  - South Land 1,198;
  - South Sea shore 1,398.
- **Still without a bitmap:**
  - about 806 shop units: Calder's strip malls and big boxes (63 + 14 units), kiosks and comfort stations;
  - upper offices with no stair door found.

  The strip and big-box letters are solid extruded meshes baked into the glb (`gen/works.py:497-533`), not kit
  rows, so they keep their 3D catalog names and can't be swapped without a rebuild.
- **Islands:** 37,734 sign anchors (18,807 box, 11,073 blade, 7,854 board); units: 3,972 shops, 2,739 stores, 4,302
  dentists, 17,385 workshops.
- **Markets:** 2,660 stalls on the floor (00_plan table); tent slots 60 per city, 36 per town, 24 per village.

## 5. Flags and banners (`make_flags.py`)
- **Flags:** governance → layout (helm: hoist triangle; plumb rule: pale; council: tribar; consensus: disc; mother
  house: bordure; lot: bend; guild: canton). Colours are the clan's 3 (best-contrast pair as the field). The emblem is
  the specialty silhouette from E1. Every flag has a forked fly (the Skein mark). Uniqueness is asserted. All are
  marked provisional.
- **Banners:** 4 per island, each 64 x 1024:
  - 0: the name in the group's font (stacked letters for B4/B5);
  - 1: wares (up to 3 pictograms plus 2 short trade phrases);
  - 2: a streamer in the flag colours with the emblem;
  - 3: the clan.

  Caps, tails and side borders come from BN1/BN2; LED bulbs are drawn along the edges.
- **Index:**
  - `signs.json` `flags.islands[SKY-xxx]` = {layout, layout_meaning, colours, emblem, emblem_colour, i, j, region,
    uv, name, clan, provisional};
  - `banners.islands[SKY-xxx]` = {png, emit, size [256,1024], banner_px [64,1024], group,
    banners:[{kind name|wares|flag_streamer|clan, text, pictograms?, uv:[k/4,0,0.25,1]}]};
  - `banners.length_m` 300.
- The RUNTIME agent appears to already have banner/flag MultiMeshes in `sky_islands.gd` (`banners._near`, `_far`,
  `_flags`, `_pennants`; seen in `reference/tmp/pass.sh`). Check whether they read these atlases.

### The mix rule (the user, 2026-10-16)
Flags, banners and island signs must blend the island's people (`heritage`) with its architecture (`warren`), plus
emergent island traits.
- **Before this rule:** the flags used only island traits (clan colours, governance layout, trade emblem) and no
  culture element at all. The banners used only the warren side (fonts, caps) plus clan colours.
- **Now (`make_flags.py`):**
  - `WARREN_MOTIF` puts the architecture's ornament (an E2 silhouette per cultural group) in the flag's upper fly, in
    `HERITAGE`'s invented accent colour.
  - The clan banner uses the heritage's lettering family, with heritage-colour edge bands.
  - Index fields: `warren_motif`, `warren`, `heritage`, `motif_colour`.
  - flags.md has two new columns.
- **Requested of the RUNTIME** for island shop signs (runtime_requests.md addendum).
- **Not yet applied:** the floor's city signs have no per-shop heritage input. A Lowliner-owned shop in a South town
  could take an island family's look; that would need an owner-heritage field from the occupancy data.

## 6. What is wired, and what was tested in game
- **Wired:** city shop signs (quads plus dropped 3D lettering) and the night glow, through `set_night`.
- **Not wired:** flags, banners, island signs (RUNTIME's), market signs (markets aren't built), and the
  mascots/ads/goods/festoons (art only).
- **"Live in their game":** the RUNTIME agent ran an `--import` (`.godot/imported` gained the `remake/signs` PNGs),
  so `CitySigns` enables itself in any game launched since. Their game log showed no errors from my scripts.
  Nobody has confirmed what they saw.
- **My test (2026-10-15 23:30, `reference/tmp/signs_test/`):** import OK, LOAD complete. The 29 SCRIPT ERRORs in
  the log are `npc_life.gd:352` (another agent's file), not mine. Screenshots `calder_0.5.png`, `calder_0.9.png`,
  `port_carrow_0.5.png`, `port_carrow_0.9.png`. Results (editor run; fps and draws from RenderingServer;
  frame time from `mainthread.sh`):

  | spot | time | sign meshes | signs shown | signs hidden |
  |---|---|---|---|---|
  | Calder C-016 (Main St) | day | 197 | 40 fps, 1714 draws, 25.5 ms | 39 fps, 1711 draws, 28.4 ms |
  | Calder | night | 197 | 35 fps, 1927 draws, 29.4 ms | 35 fps, 1750 draws, 27.1 ms |
  | Port Carrow PCR-0732 | day | 239 | 44 fps, 1599 draws, 25.9 ms | 34 fps, 1767 draws, 31.5 ms |
  | Port Carrow | night | 239 | 34 fps, 2128 draws, 31.2 ms | 33 fps, 2011 draws, 28.5 ms |

  - The day numbers are noise-level: "hidden" was measured second, while streaming continued, so no cost shows.
  - At night up to about 180 more draws: probably the emissive pass, or glow. Measure again.
  - Solana Point wasn't reached (the run was killed).
  - **Second run (2026-10-16, `reference/tmp/signs_test2/`, hidden measured first, then shown, 50 s settle):**

    | spot | time | sign meshes | hidden | shown |
    |---|---|---|---|---|
    | Solana Point SOL-0072 | day | 250 | 25 fps, 875 draws, 41 ms | 29 fps, 896 draws, 33 ms |
    | Solana Point | night | 250 | 28 fps, 927 draws | 31 fps, 993 draws |
    | Calder | day | 197 | 59 fps, 1534 draws, 16.6 ms | 59 fps, 1538 draws, 16.9 ms |
    | Calder | night | 197 | 61 fps, 1542 draws | 60 fps, 1543 draws |
    | Port Carrow | day | 239 | 55 fps, 1543 draws, 18.1 ms | 56 fps, 1558 draws, 18.3 ms |
    | Port Carrow | night | 239 | 50 fps, 1689 draws, 19.2 ms | 41 fps, 1709 draws, 19.5 ms |

    The signs cost **+4 to +66 draws** (one per building in view) and no measurable frame time: process and frame
    times are within ±0.4 ms. The fps column is noisy (`Engine.get_frames_per_second` while streaming). "Hidden" means `visible = false` on the quads; the 3D lettering
    stays dropped either way.
- **Seen in the screenshots:**
  - Day: correct, e.g. "RING LINE CAFE" on its board, an enamel bank sign, a brass tenant plaque by a door,
    "TREMBLAY BARBER SHOP" with its pictogram.
  - **Night: far too bright**, white blown-out rectangles. **Fixed 2026-10-16:** `_energy()` in `city_signs.gd` is
    now `n * 0.7` (it was `0.05 + n*2.2`). Re-test pending (§7.1).
  - Some boards may come out narrower than the real board when the text size was clamped (Port Carrow barber).

## 6b. Night legibility: the emissive values (the user, 2026-10-16: "I cannot read the illuminated signs. They are washed out at night")
**The root cause.** `city_signs.gd` set `emission = WHITE` with an emission texture under Godot's default operator
**ADD**, i.e. `(colour + texture) x energy`: every quad glowed solid white at night, whatever its mask held. It is
now **`EMISSION_OP_MULTIPLY`**: `emission = WHITE x emit_texture x EMIT_SCALE x night`.

**The shared night scale** (from the coordinator, to match the island signs):

| part | mask level (make_signs.py) | HDR at full night (x EMIT_SCALE 2.0) |
|---|---|---|
| letters, neon, bulbs | 255 (`LETTER_EMIT`; neon and bulbs drawn at 255) | 2.0 x albedo (the shared "letters and neon 2.0") |
| lightbox faces (backlit styles only, inside the lettering box) | 115 (`FACE_EMIT`) | at most 0.9 (sRGB 115/255 decodes to about 0.17 x albedo x 2.0) |
| board grounds, frames, backings | 0 | dark (lamp light only) |

- The emit texture is RGB = albedo x mask/255 (sRGB PNG, half resolution).
- `night` = DaySkySystem `night_mix`, through `RemakeBuilding.set_night`. Day: 0.
- **The glow** (DaySkySystem.gd:334-340, set by another agent): threshold 1.5, intensity 0.7, no bloom, additive.
  Bright letters and neon (about 1.8–2.0) pass just over the threshold for a thin halo; faces stay under it.
- **Values that washed out** (with ADD and whole-board masks): `0.05 + 2.2 n`, `0.7 n`, `1.6 n`.
- **Lit letters are found by their palette colour** inside the lettering box, so dark letters on light enamel stay
  unlit and lamp-lit. The ground never emits.
- **Verified 2026-10-16** (`reference/tmp/signs_test3/`: night at 5 and 20 m facing the shops; `signs_test4/`: night
  along the street at about 30 and 60 m, both ways; Calder and Port Carrow):
  - legible, letters lit on dark boards, no white slabs;
  - "RING LINE CAFE" and "TREMBLAY BARBER SHOP" read at 5 and 20 m;
  - "DECARLO & BAZZI BEAUTY SHOP" reads at about 30 m along the street;
  - at 60 m the names are small but show as lit lettering, not blobs.

  (`signs_test3`'s straight-back 60 m shots put the camera behind the buildings opposite: ignore them.) Earlier runs: `signs_test3_addop/` (the ADD bug, white slabs) and
  `signs_test3_run2/` (DevBridge token rewritten by another agent's import: no shots).

## 7. Next, in order
1. (DONE 2026-10-16: night fix §6b, test numbers §6.) Earlier plan, for reference:
   - take the lock, launch, then Solana Point plus Calder and Port Carrow at night;
   - measure again with signs shown and hidden in a fixed order (hidden first, then shown, after 60 s of settling);
   - quit, kill by PID, release the lock.
2. Board width: read the real `sign_board` box from the model, e.g. the kit's or glb's sign_board faces, or
   recompute `fronts_info` from the catalog like store.py does, instead of inverting the text size.
3. Banner cells for the RUNTIME: **done 2026-10-16.** `banners_a`/`banners_b` grid atlases, and an addendum in
   runtime_requests.md telling them to read `banner_atlas.islands[id].name/wares` (their `_atlas_cells()` at
   `sky_banners.gd:155` expects another format). Waiting on them.
4. Unsigned shops (strip malls, big boxes): rebuild them with kit-row letters in `gen/works.py`, or overlay quads at
   the canopy fascia (front door z − 2.63, height FL+H−0.35).
5. Export: add `remake/signs/*.json` to `export_presets.cfg` `include_filter`, or add `city_signs.json` to
   `tools/pack_data.py` and ship the `.gz` (DataFile reads either). Otherwise the export has no signs.
6. Keying flaws: lilac and pink art that is close to magenta (south_liquor, flamingo). Use a green-screen sheet for
   those if they're wanted.
7. Optional: an island mode in make_signs for baked island name signs, if the RUNTIME asks (request §5).

- Export: `remake/signs/*.json` was added to every `include_filter` in `godot_project/export_presets.cfg` (3 presets).
  The atlas PNGs are resources and export as usual.

No half-finished edits. Every script above parses (`--check-only`).
