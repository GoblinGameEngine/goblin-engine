# 08 Signage briefs for Grok (sign sheets)

For the agent that runs Grok. **Do not run these from the design stream.** The user has very little Grok credit left,
so:
- every image is a **sheet of many signs**;
- each sheet is made **once with `image_gen`**;
- `image_edit` is kept only for fixing a broken sheet.

**Order:** (A) all the market signs, then (B) the island signs per warren family (44), then (C) city business signs
by region and business type.

## 0. How the sheets fit the existing sign pipelines

### 0.1 What exists (checked 2026-10-15)
- **Road signs:** `tools/sign_atlas.py` draws `godot_project/remake/textures/road_signs.png`, an **8 x 8 atlas of
  256 px cells** with transparent surrounds. `RoadFurniture.gd`'s `ATLAS` table maps cell names. **This is the
  convention the new atlases follow.**
- **City business signs:** built into each building glb by `remake/blender/gen/store.py:305-395`.
  - A `sign_board` solid with **3D text meshes** (`g.text_mesh`, gold or `neon_r`).
  - Named nodes: `sign_front{i}`, `sign_blade{i}_{±}`, `sign_awning{i}`, `sign_window{i}`.
  - No sign textures exist yet. The boards are flat colours.
- **Island signs:** `godot_project/remake/scripts/sky/sky_signs.gd`.
  - Merged procedural meshes: neon, led, wash, solid boards, bulbs.
  - Kinds `neon_script, lightbox, dot_matrix, chochin, brass, painted, neon_frame, video, figure` (`:5`).
  - Procedural names from `GOODS/ADJ/NOUN/SHOP/PUNS` (`:26-41`).
  - The LED boards use `SkyDotFont.strip_texture` (`sky_dot_font.gd:90`).
  - **No image textures.**
- **The warren kit's sign pieces** (`remake/sky/warrens/pieces.json`): `ov_sign_blade` (36 tris), `ov_sign_box` (24),
  `ov_sign_board` (24), `ov_sign_arm` (Kowloon), `ov_sign_arm_big` (HK), and `wall_sign_column_t` /
  `ov_sign_vertical_stack` (Japan, HK, Taipei). Palette per family (`palettes[civ][variant]`).

### 0.2 Design rule: textures carry the art, the game carries the words
- **Market signs (A)** are unique, so **their names are painted in the art**. If Grok misspells one, keep the art and
  overlay the name with the kit's letters (07 §3), or spend one reserve `image_edit`.
- **Island (B) and business (C) signs are BLANKS: frame, ornament, pictogram and colour, with no words.**
  - The names stay procedural and are drawn on top by the existing systems: `text_mesh` on city boards; sky_signs'
    names, neon and dot font aboard.
  - So 44 families × 3 blanks serve thousands of shops, and Grok's weak lettering never matters.

### 0.3 The crop pipeline (`tools/signs/crop_sheets.py`, to be written in the KIT/DATA stream)
1. Split each sheet on its grid (3x3 or 4x4 equal cells; the prompt asks for even spacing).
2. **Key out the background:** a flat pure magenta `#FF00FF`. Colour distance plus a 1-px erode gives alpha.
3. Trim, centre, and resize to **256 x 256** (market hero faces: 256 x 512 tall or 512 x 256 wide, from two cells
   where needed).
4. **Emissive mask:** pixels with high value and saturation in the neon, bulb or lightbox hues → a mask in the
   atlas's second texture. **The night look is a shader, not a second image** (no night sheets: they would double the
   cost).
5. Pack into atlases like road_signs.png:
   - `textures/signs/markets.png` (8 x 8);
   - `textures/signs/sky_A.png` and `sky_B.png` (8 x 8 each, 132 family cells plus the shared cells);
   - `textures/signs/biz.png` (8 x 8).
   - Each has a `signs.json` cell map: `{cell: [atlas, i, j, kind, band|family, emissive]}`.

### 0.4 Hook-up (RUNTIME, later)
- **City buildings:**
  - At load, `building_loader` finds the `sign_front*` / `sign_blade*` nodes and sets a material override with the
    atlas cell for the place's purpose (`npc_place_index`) and the town's band. River towns pick north or south per
    building with probability t.
  - The 3D text stays on top.
  - No building rebuild is needed.
- **Islands:** sky_signs' `painted`, `lightbox` and `brass` boards and the kit's `ov_sign_*` pieces get UVs into the
  family's three cells (B). The neon, LED and video kinds stay procedural.
- **Markets:** `market_styles.json` `face`/`face2` name the cells (07 §4).

### 0.5 Prompt rules (every sheet)
- **Resolution:**
  - Ask for a **square 1:1 image at the smallest size Grok offers**. The CLI returns about 1024 px; that is the
    floor, and it is enough.
  - 3 x 3 cells come out at ≈ 340 px and are downscaled to 256. 4 x 4 cells come out at ≈ 256 px and are used
    directly.
- **Fixed wording, repeated in every prompt:** "a reference sheet of N separate signs in an evenly spaced R x C grid;
  each sign seen straight from the front, orthographic, flat, no perspective, no shadow, no scene, no people, no
  ground; each sign centred in its cell with a clear margin; on a perfectly flat uniform pure magenta (#FF00FF)
  background with no gradient or texture; clean flat colours and bold simple shapes suitable for small game
  textures; daylight colours with the bulbs and neon drawn lit".
- **Margin fix (added 2026-10-15 after A1):** A1 came back on a pink gradient (not pure magenta) with drawn grid lines, and three signs ran to the cell edges (a wall behind the clock, a gable and a tower cut off). Every later prompt appends: "Every sign is small enough to sit wholly inside its cell with a wide empty magenta margin (at least one sixth of the cell) on all four sides; nothing touches or crosses a cell edge; no backdrop panels, walls or frames behind the signs; no grid lines or dividers drawn; the whole background is one single saturated #FF00FF magenta, identical everywhere." Each call also says "make exactly ONE image, call image_gen once, square 1:1"; image_gen has no size option (1024 px floor). The prompts as sent are in `reference/grok/signs/prompts/`. The cropper keys by flood fill from the cell border, so a slightly uneven pink still cuts out.
- **Words:** for blanks, "**no words or letters on any sign**". For market signs, the exact wording in quotes, with
  "spell exactly".

### 0.6 Count
| set | sheets | grid | cells used |
|---|---|---|---|
| A markets | 5 | 3 x 3 | 44 (22 markets x 2) + 1 shared |
| B island families | 9 | 4 x 4 | 132 (44 families x 3) + 12 shared |
| C city businesses | 4 | 4 x 4 | 64 (32 business types x north and south) |
| reserve `image_edit` | 2 | — | fixes only |
| **total** | **18 image_gen + up to 2 edits = 20 images at most** | | 241 + 13 shared |

---

## (A) Market signs: 5 sheets of 3 x 3, in style-gradient order (north → south)
Per market: cell 1 is **the main sign face** (the board, arch or tower face with the name). Cell 2 is **the mascot or
landmark element** (a cut-out). Cells read left to right, top to bottom.

### A1: the North Shore (stately, classic)
> A reference sheet of 9 separate signs in an evenly spaced 3 x 3 grid; each sign seen straight from the front,
> orthographic, flat, no perspective, no shadow, no scene, no people, no ground; each sign centred in its cell with a
> clear margin; on a perfectly flat uniform pure magenta (#FF00FF) background with no gradient or texture; clean flat
> colours and bold simple shapes suitable for small game textures; daylight colours with bulbs drawn lit. Style:
> stately classic New England seaside, gold leaf, sign-painter Roman serifs, no neon. Spell all words exactly.
> 1. A barn-red painted wooden signboard with a cream border and gold-leaf Roman serif capitals "THE ROPEWALK", and a
>    cream band below reading "MARKET & SWAP · FRI SAT SUN".
> 2. A cut-out sheet-metal mascot: a friendly herring gull in a yellow sou'wester holding a coil of rope, one round
>    glowing bulb eye.
> 3. An oval gilt-framed navy board, "THE LOBSTER POT" in gold serif capitals, "ANTIQUE & FLEA FAIR · BRIGHTWATER"
>    smaller below.
> 4. A slatted wooden lobster trap hung with red, yellow and white painted buoys, a red lobster weathervane on top.
> 5. A large white clock face with a single hand and the words "HIGH" at top and "LOW" at bottom, in a white
>    clapboard frame.
> 6. A black-and-white engraved slab sign "THE TIDE CLOCK · MARKET" in classic serif.
> 7. A grey shingled gable end with "THE NET LOFT" painted in white serif capitals.
> 8. A fishing net with green glass floats hanging under a carved wooden tern.
> 9. A silver village water tower tank with "THE WATER TOWER · FLEA" painted in black block capitals.

### A2: the Northland, then the river towns begin
> (same opening paragraph as A1) Style: stately classic Midwest country, gilt serifs, white timber, copper; the last
> three cells begin to add one laid-back touch.
> 1. A floodlit board for the water tower's base: "LOOMIS GROVE" in oxblood block capitals on silver.
> 2. A white barn-door sign with green trim: a giant gilded open book whose pages read "THE BOOK BARN" in small-caps
>    serif.
> 3. A brass-lamp-lit plaque "FENWICK · BOOK BARN & FLEA" in green and gold.
> 4. A copper verdigris bull weathervane with N E S W letters on its arms.
> 5. A barn-red painted board "THE WEATHERVANE · AUCTION FRI · FLEA SAT SUN" in white serif.
> 6. A white timber county-fair arch with a gilt eagle finial and "BRANNOCK COUNTY TRADE DAYS" in gilt serif on navy.
> 7. Red, white and navy bunting with a small round "MARLOWE" medallion.
> 8. A green-and-white boathouse gable with a striped awning, "THE BOATHOUSE" in classic serif and the word "Swap" in
>    glowing turquoise neon script.
> 9. A turquoise neon outline of a leaping fish.

### A3: the river gradient
> (same opening paragraph) Style: classic serif bases, each with one laid-back accent (a neon word, a pastel stripe,
> a painted swash).
> 1. A white finger-post with eight arrow boards in black serif capitals pointing left and right: "THE ROPEWALK 31",
>    "STARLITE 58", "TRADERS' LANDING 22", "IRON WHEEL 40", "BOOK BARN 17", "RED GRANARY 35", "THE NET LOFT 26",
>    "CAROUSEL 47". On top, a small sunset-painted board "FOUR CORNERS SWAP".
> 2. A white racing-sail pylon with navy serif "THE REGATTA SWAP" and pastel spinnaker stripes.
> 3. A string of colourful regatta pennants.
> 4. A wooden waterwheel with warm bulbs along its paddles.
> 5. A carved oak slab "MILLWHEEL MARKET" in serif with a painted terracotta swash underline.
> 6. A red freighter bow face with a hanging anchor, "TRADERS'" in tall white condensed slab capitals outlined in white
>    bulbs, and "Landing" below in orange neon script.
> 7. A white lighthouse with a red band and a glowing lamp room, a small red panel "MARKET".
> 8. A cut-out fibreglass figure: a cheerful bearded freighter captain in a navy peacoat and white captain's cap,
>    holding up a brass lantern.
> 9. A dot-matrix sign frame with amber LEDs reading "ISLAND FAIR" (shared, used at every market).

### A4: the South Land, inland (Streamline, Googie, Route 66)
> (same opening paragraph) Style: laid-back inland California roadside, Streamline Moderne and Googie, neon and chase
> bulbs, pastel and turquoise.
> 1. A black Streamline Moderne fin with chrome speed lines, "IRON WHEEL" in tall thin-thick white neon capitals,
>    "TRADE DAYS" in green neon below.
> 2. A black locomotive driving wheel with counterweight, spokes and rim outlined in white chase bulbs.
> 3. A red granary gable with a white painted sunburst and "Red Granary" in Googie script, bulbs along the roofline.
> 4. A tall fibreglass tamarack tree in autumn gold wrapped in coloured bulbs.
> 5. A 1950s boomerang-shaped board "THE TALL TAMARACK" in turquoise and gold.
> 6. A pastel roadside-postcard lettering board "ELEVATOR FLEA DAYS", each big letter filled with a tiny farm picture.
> 7. A highway route shield sign shape reading "US 30", outlined in turquoise neon with an orange starburst.
> 8. A Googie boomerang arrow board "SWAP MEET · ROUTE 30" in orange neon script with chase bulbs.
> 9. A cut-out fibreglass roadside mascot: a smiling mechanic in blue overalls waving a big wrench.

### A5: the South Sea shore (beach California)
> (same opening paragraph) Style: laid-back Southern California beach, neon script, Googie starbursts, sunset pastels,
> palms, stucco and mission tile.
> 1. A neon pier-and-palm pylon in green and turquoise, "LA PULGA VERDE" in brush-script neon under a terracotta
>    mission-tile cap.
> 2. A drive-in screen tower face with a sunset mural and "STARLITE SWAP" in 1950s orange and pink neon script and a
>    turquoise starburst.
> 3. A white changeable-letter marquee board with chase bulbs reading "THIS WEEKEND · ISLAND FAIR!".
> 4. A cut-out smiling cartoon sun wearing black sunglasses, waving, with a turquoise neon outline.
> 5. A carousel horse on a gold-and-red striped pole.
> 6. A carousel canopy board "THE CAROUSEL SWAP" in rainbow bulb-outlined letters.
> 7. A fibreglass pelican in a straw sun hat standing on a wooden piling.
> 8. A surfboard-shaped sign "THE PELICAN SWAP" in hand-lettered coral brush script on turquoise.
> 9. A long string of colourful clan pennants and paper lanterns (the Skein banner, shared).

---

## (B) Island signs per warren family: 9 sheets of 4 x 4 (blanks: no words)
- **Per family, 3 cells:**
  - **(a) a fascia or shopfront board blank:** the family's frame, ornament and colours, with an empty centre for the
    name;
  - **(b) a blade, hanging or vertical sign blank** (vertical for the East Asian families);
  - **(c) a lit emblem:** a lightbox or neon motif with no letters (a trade pictogram or the family's lucky symbol).
- **Style for all:** "flashy and modern with the society's own flair". These are sky cities that love lights:
  - LED edges, neon outlines and lightbox glow;
  - plus each culture's own ornament and colours (the family research files in
    `research/sky_islands/warrens/r1_*` to `r3_*`).
- **The 4th row's leftover cells** are shared Skein, market and Lowliner signs (listed per sheet).

Opening paragraph for every B sheet:
> A reference sheet of 16 separate signs in an evenly spaced 4 x 4 grid; each sign seen straight from the front,
> orthographic, flat, no perspective, no shadow, no scene, no people; each sign centred in its cell with a clear
> margin; on a perfectly flat uniform pure magenta (#FF00FF) background with no gradient or texture; clean flat
> colours and bold simple shapes suitable for small game textures; **no words or letters on any sign: leave name
> panels empty**; a flashy modern style for floating sky cities that love lights (LED edge strips, neon outlines,
> glowing lightboxes) mixed with each culture's own traditional ornament and colours. Rows of three cells per culture,
> in order: (a) a wide shopfront name board with an empty centre panel, (b) a hanging or vertical blade sign with an
> empty panel, (c) a glowing emblem with no letters.

### B1: North Africa and the Levant
- Maghrebi medina:
  - (a) a zellige-tile-bordered board in green, blue and white with a horseshoe-arch outline in LED;
  - (b) a hanging pierced-brass lantern-style blade;
  - (c) a glowing eight-point star emblem.
- Saharan kasbah:
  - (a) an ochre mud-plaster board with triangle-and-chevron relief and red LED edges;
  - (b) a vertical board with a crenellated top;
  - (c) a glowing Tuareg-cross-shaped lamp.
- Mzab and Ghadames:
  - (a) a whitewashed board with palm-rib framing and blue trim;
  - (b) a palm-wood blade;
  - (c) a glowing palm-tree motif.
- Cairene Mamluk:
  - (a) a striped ablaq (red and cream stone bands) board with a muqarnas top and gold LED;
  - (b) a mashrabiya lattice blade;
  - (c) a glowing coloured-glass fanous lantern.
- Levantine courtyard:
  - (a) a black-and-white stone board with a jasmine-vine border;
  - (b) a wrought-iron bracket sign;
  - (c) a glowing pomegranate emblem.
- Cell 16 (shared): a Mooring Office sign blank (white board, navy rope border, an anchor-and-gondola pictogram).

### B2: Arabia, Persia, the Silk Road
- Hejazi roshan:
  - (a) a carved teak roshan-lattice frame board in turquoise and white;
  - (b) a vertical lattice blade;
  - (c) a glowing coffee-pot (dallah) emblem.
- Yemeni tower:
  - (a) a brown board with white gypsum zigzag bands and qamariya half-moon stained-glass window top;
  - (b) a tall narrow tower-shaped blade;
  - (c) a glowing qamariya rainbow-glass half-moon.
- Omani oasis:
  - (a) a sand-coloured board with a carved wooden door-stud border;
  - (b) a frankincense-burner-shaped blade;
  - (c) a glowing khanjar-curve emblem.
- Persian desert:
  - (a) a turquoise-and-cobalt tile board with an arabesque border;
  - (b) a windcatcher-shaped vertical sign;
  - (c) a glowing tiled dome emblem.
- Silk Road:
  - (a) a blue majolica board with a carved wooden ivan frame;
  - (b) a suzani-embroidered hanging banner;
  - (c) a glowing camel-caravan emblem.
- Cell 16 (shared): a Weigh House sign blank (brass board, a balance-scale pictogram).

### B3: South Asia
- Mughal walled city:
  - (a) a red sandstone board with white marble inlay (pietra dura flowers) and gold LED;
  - (b) a scalloped-arch blade;
  - (c) a glowing lotus emblem.
- Rajput sandstone:
  - (a) a golden sandstone board with jharokha balcony carving and mirror-work sparkle;
  - (b) a mirror-embroidered hanging banner;
  - (c) a glowing peacock emblem.
- Ganga ghat:
  - (a) a saffron-and-marigold board with marigold-garland LED;
  - (b) a brass-bell blade;
  - (c) a glowing oil-lamp (diya) emblem drawn as an electric bulb.
- Karachi:
  - (a) a truck-art board, every inch painted with flowers, chains and borders in hot colours with chrome edges;
  - (b) a truck-art hanging panel with chain fringe;
  - (c) a glowing truck-art eye-and-flower motif.
- Newar:
  - (a) a carved dark-timber board with a torana arch and copper-gold trim;
  - (b) a pagoda-roof blade;
  - (c) a glowing plain stupa-dome emblem.
- Cell 16 (shared): a gondola station sign blank (sky blue board, a gondola-cabin-on-rope pictogram).

### B4: the Himalaya and China
- Tibetan Lhasa:
  - (a) a black-framed window-shaped board with a red-and-white striped valance;
  - (b) a prayer-flag strip blade (blank flags);
  - (c) a glowing endless-knot emblem.
- Chongqing cliff:
  - (a) a stacked-signs board in red and yellow LED with a metal frame;
  - (b) a vertical red lightbox;
  - (c) a glowing chili-pepper emblem.
- Hakka tulou:
  - (a) a round earthen-wall-coloured board with a black tile eave;
  - (b) a red paper-lantern pair blade;
  - (c) a glowing round tulou-ring emblem.
- Jiangnan water town:
  - (a) a white-wall black-tile board with a grey horse-head gable;
  - (b) a hanging cloth shop banner with an empty panel;
  - (c) a glowing lotus-pond emblem.
- Kowloon walled city:
  - (a) a dense cluster of mismatched small lightboxes on a steel frame;
  - (b) a projecting arm sign;
  - (c) a glowing dragon-silhouette emblem.
- Cell 16 (shared): a Lowliner Line Hall sign blank (knotted-rope border round an empty panel, a lantern hanging below).

### B5: East Asian neon + shared
- Hong Kong neon canyon:
  - (a) a big neon-tube-framed board in pink and cyan;
  - (b) a two-storey neon arm-sign frame;
  - (c) a glowing neon fish emblem.
- Taipei tiepi:
  - (a) a corrugated-metal board with green-and-red LED edging;
  - (b) a vertical lightbox column;
  - (c) a glowing bubble-tea-cup emblem.
- Japan yokocho:
  - (a) a wooden noren-curtain board under a red paper chochin row;
  - (b) a vertical lit sign column panel;
  - (c) a glowing red chochin lantern.
- Korean hillside:
  - (a) a pastel-blue board with dancheong-painted eave edges;
  - (b) a vertical LED board;
  - (c) a glowing round sun-and-cloud emblem.
- Cells 13–16 (shared):
  - a tent plank sign blank (hand-painted wood, clan-colour stripes);
  - a second tent plank blank (curved top, bulb edge);
  - a clan pennant set (six blank pennants in different colours);
  - a fare board blank (a black board with brass rope edge and an empty price list area).

### B6: Southeast Asia + Matera
- Viet tube house:
  - (a) a narrow yellow facade board with a green shutter frame;
  - (b) a vertical red-and-yellow banner;
  - (c) a glowing silk-lantern emblem.
- Siam khlong:
  - (a) a teak board with a gilded chofa gable flourish;
  - (b) a boat-prow blade;
  - (c) a glowing lotus-bud emblem.
- Manila estero:
  - (a) a jeepney-style board with chrome edges and painted stripes;
  - (b) a capiz-shell window blade;
  - (c) a glowing parol star lantern.
- Straits shophouse:
  - (a) a pastel shophouse fascia with Peranakan tile border;
  - (b) a vertical black-lacquer board with gold edge;
  - (c) a glowing phoenix-and-peony tile emblem.
- Rupestrian terraces:
  - (a) a tufa-stone board carved into rock with an iron lamp;
  - (b) a wrought-iron blade;
  - (c) a glowing bread-loaf emblem.
- Cell 16 (shared): a Crew Tent sign blank (white board, a rope coil and helmet pictogram).

### B7: the Americas
- Andean neo:
  - (a) a cholet-style board with bright mirrored-glass colours and Andean step-pattern borders;
  - (b) a vertical aguayo-weave banner;
  - (c) a glowing condor-silhouette emblem.
- Latin hillside:
  - (a) a brightly painted favela-colour board with tile edges;
  - (b) a hand-painted hanging sign;
  - (c) a glowing hummingbird emblem.
- Creole colonial:
  - (a) a pastel board with wrought-iron lace corners;
  - (b) a cast-iron bracket blade;
  - (c) a glowing magnolia-flower emblem.
- Nouvelle-France:
  - (a) a carved wooden board with a bell-cast roof flourish in red and white;
  - (b) a wrought-iron blade;
  - (c) a glowing maple-leaf emblem.
- Lusitanian hill:
  - (a) a blue-and-white azulejo tile board;
  - (b) a tiled blade;
  - (c) a glowing sardine emblem.
- Cell 16 (shared): a Low Lashing banner blank (a long festival banner with lanterns and an empty centre).

### B8: the Mediterranean and Anatolia
- Iberian white town:
  - (a) a whitewashed board with a yellow-ochre border and a hand-painted tile panel;
  - (b) a canvas awning blade;
  - (c) a glowing flowerpot emblem.
- Cycladic:
  - (a) a white board with a blue dome-arch top;
  - (b) a blue shutter blade;
  - (c) a glowing windmill emblem.
- Tyrrhenian canyon:
  - (a) a pastel-orange board with green shutters;
  - (b) a ceramic lemon-painted blade;
  - (c) a glowing lemon emblem.
- Knights' harbour:
  - (a) a honey-limestone board with a carved baroque frame;
  - (b) a coloured enclosed-balcony (gallarija) blade;
  - (c) a glowing eight-point star emblem.
- Ottoman timber:
  - (a) a dark timber board with a projecting cumba bay and Iznik tile inset;
  - (b) a hanging carved blade;
  - (c) a glowing tulip emblem.
- Cell 16 (shared): a market warden's sign blank (green board, a balance and a key pictogram).

### B9: Northern Europe, the Balkans, the Caucasus
- Hanseatic gable:
  - (a) a stepped-gable brick-red board with white trim;
  - (b) a wrought-iron guild bracket sign with an empty hanging panel;
  - (c) a glowing cog-ship emblem.
- Scots lands:
  - (a) a dark-stone board with a crow-step gable top and a tartan stripe;
  - (b) a painted pub-style hanging board;
  - (c) a glowing thistle emblem.
- Kulla stone:
  - (a) a grey fieldstone board with a tiny arrow-slit window and red-black textile trim;
  - (b) a carved wooden blade;
  - (c) a glowing eagle-feather emblem.
- Caucasian balcony:
  - (a) a carved fretwork balcony-railing board in blue and white;
  - (b) a grapevine iron blade;
  - (c) a glowing grape-cluster emblem.
- Mardin terraces:
  - (a) a carved honey-stone board with arched niches;
  - (b) a copper-plate blade;
  - (c) a glowing copper-coffee-pot emblem.
- Cell 16 (shared): a "rope steward" ground-station sign blank (orange safety board, a rope-and-hook pictogram).

---

## (C) City business signs: 4 sheets of 4 x 4 (blanks with a pictogram, no words)
- **32 business sign types × 2 bands.** River towns use either band, picked per building with probability t (07 §1.2),
  so the gradient shows as a mix: "culturally connected".
- **The types,** from `tools/places/make_places.py`:
  1. grocery
  2. bakery
  3. butcher
  4. fish market
  5. café
  6. diner
  7. restaurant
  8. bar or tavern
  9. liquor store
  10. hardware
  11. clothing
  12. thrift or variety
  13. bookstore
  14. jeweller
  15. florist
  16. furniture
  17. sporting goods or gym
  18. charge stop
  19. newsagent
  20. drug store
  21. doctor or dentist
  22. barber
  23. beauty salon
  24. laundromat
  25. bank
  26. office (insurance, law)
  27. print shop
  28. repair or auto repair
  29. funeral home
  30. movie theatre
  31. arcade or amusement
  32. hotel or motel
- Each cell is the business's **board blank with an empty name panel and the trade's pictogram at one end**. The name
  is drawn on top in game.

Opening paragraph for every C sheet:
> A reference sheet of 16 separate shop signs in an evenly spaced 4 x 4 grid; each sign seen straight from the front,
> orthographic, flat, no perspective, no shadow, no scene, no people; each sign centred in its cell with a clear
> margin; on a perfectly flat uniform pure magenta (#FF00FF) background with no gradient or texture; clean flat
> colours and bold simple shapes suitable for small game textures; **no words or letters on any sign**: each sign has
> an empty name panel and a simple pictogram of its trade at the left end.

### C1: North Land (stately, classic), types 1–16
> Style: stately classic New England and Midwest main-street signs, painted wood and gilt, carved borders, deep red,
> navy, forest green, cream and gold leaf, brass lamp brackets, no neon. In order: grocery (a produce crate), bakery
> (a wheat sheaf and loaf), butcher (a cleaver and steer), fish market (a fish on ice), café (a steaming cup), diner (a
> pie slice), restaurant (a fork, knife and plate), tavern (a tankard), liquor store (a bottle and glass), hardware (a
> hammer and saw), clothing (a coat on a hanger), thrift and variety (a teapot and lamp), bookstore (an open book),
> jeweller (a ring and gem), florist (a bouquet), furniture (an armchair).

### C2: North Land, types 17–32
> Same style as C1. In order: sporting goods (a baseball and racquet), charge stop (a plug and lightning bolt in a
> cartouche), newsagent (a folded newspaper), drug store (a mortar and pestle), doctor or dentist (a plain
> cross and tooth), barber (a striped barber pole), beauty salon (scissors and comb), laundromat (a washing
> tub), bank (a classical columned facade), office (a quill and ledger), print shop (a press roller), repair (a wrench
> and gear), funeral home (a laurel wreath), movie theatre (a film reel), arcade (a pinball flipper), hotel or motel
> (a key and bed).

### C3: South Land (laid-back, California), types 1–16
> Style: laid-back Southern California roadside signs, Googie boomerangs, starbursts and kidney shapes, pastel
> turquoise, coral, sunset orange, sand and palm green, neon outline tubes and chase bulbs drawn lit, stucco and
> mission-tile caps. Same pictograms and order as C1: grocery, bakery, butcher, fish market, café, diner, restaurant,
> bar, liquor store, hardware, clothing, thrift and variety, bookstore, jeweller, florist, furniture.

### C4: South Land, types 17–32
> Same style as C3. Same pictograms and order as C2: sporting goods, charge stop, newsagent, drug store, doctor or
> dentist, barber, beauty salon, laundromat, bank, office, print shop, repair, funeral home, movie theatre, arcade,
> hotel or motel.

---

## Reserve (2 `image_edit` at most)
- Use only if a sheet comes back unusable: wrong grid count, a sign bleeding across cells, a perspective view, or a
  market name misspelled beyond overlay repair.
- Edit that sheet; don't regenerate it. Example: "keep everything, fix cell 6's lettering to read exactly
  'TRADERS''".
- If Grok returns HTTP 402 (out of credit), stop and tell the user (memory: ssc-grok-asset-pipeline).

## Storage
Save the sheets to `reference/grok/signs/{A1..A5,B1..B9,C1..C4}.png` (gitignored), with this file's prompt text
beside each sheet as `<sheet>.md`.

## Status (2026-10-15): made
- **Images used: 19 of 20.** 18 sheets made with `image_gen`, plus 1 `image_edit` on C4 (it only changed one cell). One
  reserve is left. The sheets and the prompts as sent are in `reference/grok/signs/<sheet>/` and `reference/grok/signs/prompts/`.
- **Cut by `tools/signs/crop_sheets.py`** (cell lists in `tools/signs/sheet_manifest.py`). It writes:
  - the atlases `godot_project/remake/signs/{markets,sky_a,sky_b,biz}.png` (256-colour, 256 px cells);
  - the matching `*_emit.png` night masks (128 px cells);
  - the `signs.json` index (257 cells);
  - the contact sheets `research/flea_markets/img/signs_*.jpg`.
- **The atlas layout differs from §0.3.** The atlases live in `remake/signs/` (the user's choice), with 8 columns and as
  many rows as needed. sky_a holds B1–B4 and sky_b holds B5–B9. There are 4 extra island cells, from extras Grok drew.
- **Sheets that ignored the grid:**
  - B1 is laid out in columns and B2 on a 5 x 4 grid of tiles; both are cut with hand boxes (`BOXES`).
  - B2, C1, C2 and C4 drew flat tiles behind the signs; the cropper keys them out (`TILED`).
  - Writing each B and C row out separately fixed the layout from B3 on.
- **Known flaws:**
  - Weathervane letters and the MARLOWE medallion are garbled (overlay them), and the apostrophe in TRADERS' is lost.
  - The Jiangnan board has a literal horse head.
  - The HK blade has Chinese characters (it is not a blank).
  - The A1 clock keeps its white wall.
  - The C3 south_liquor board is lilac-magenta, so it keyed out with the background.
