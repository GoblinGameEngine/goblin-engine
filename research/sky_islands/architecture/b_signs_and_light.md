# B5. Signs and night light: the catalogue for SkySigns

The user, 2026-10-14: "lots and lots of lights with billboards and flashing signs. At night they should light up like a
christmas tree ... Each store has it's own light up stylized sign. Each apartment complex has mood lighting and a stylish
motif."

**Canon constraints:**
- **No flame** under hydrogen ("No flame, no fall"). Every light is electric: cold-cathode neon, LED, bulbs, and lit
  dot-matrix LCDs (plentiful in station canon; see ssc-boards). Lanterns are electric.
- **Every kilo is weighed.** Signs are light: a tube on a wire frame, cloth over a frame, a thin lightbox. Giant signs hang
  from balloon rigging rather than standing on roofs.
- **Power:** the sunskin envelopes charge cells by day. **Night is when the islands spend it**, a nightly display of wealth,
  and a commerce culture flaunts it.

## 1. Sign kinds

Sizes are in metres. Anchor names follow 00_brief.md (`sign_<kind>_<w>x<h>`). Mounting: F = flush on the wall,
P = projecting (perpendicular to the wall), R = roof, H = hung on a line or rigging, G = on the ground.

| kind | what it is | size w × h (depth) | mount, height | palette | animation |
|---|---|---|---|---|---|
| `neon_blade` | Hong Kong projecting neon: a tall panel of characters or letters, a tube outline on a dark frame | 0.8–1.6 × 3–10 (0.3) | P, base ≥ 3.5 above the path, reaching ≤ 4.2 out; stacked down a corner | red-orange `#ff4a2a`, neon pink `#ff3fa4`, argon blue `#3a7bff`, green `#2bff88`, amber `#ffb02e` | steady 70 %; flicker 10 %; per-letter on in sequence then all-flash 20 % |
| `neon_script` | cursive tube lettering, flush on the wall or over a door, often with a picture (a cup, a goat, a lark) | 1.2–5 × 0.5–1.5 | F, 2.6–4 m up | as neon_blade, plus white `#f4f0ff` and violet `#b24bff` | steady, or word by word on a 0.4 s step then 1.5 s hold, a loop of about 3 s |
| `lightbox` | internally lit panel with a printed or painted face (the Tokyo projecting kanban) | 0.6 × 1–2.6 (0.2), or a flush 1.5–4 × 0.6–1 | P or F | white-backed faces in a clan colour; warm-white glow `#fff2d6` | steady; the dimmed ones read as cheap |
| `sign_vertical_stack` | zakkyo-style projecting column of **one lightbox per floor per tenant** up the corner | 0.6 × 1 per floor, full height | P, from 1F to the top | each panel a different colour | steady; one panel flickers |
| `directory_board` | backlit tenant list at the door, one row per tenant | 0.6–1 × 1.2–2 | F or G | white rows, coloured names | steady |
| `dot_matrix` | station-canon LCD/LED moving-message board: **7-pixel-high characters**; character height ≈ pitch × 7 ([FDOT](https://www.cflsmartroads.com/projects/working_group/docs/DMS%20101.pdf)) | 0.5–4 × 0.15–0.6; pitch 20–40 mm | F over doors, P, or a band round a building | amber `#ffaa1e` (canon LCD), red `#ff2a1a`, green `#3cff6a` | **scroll** at about 6 characters/s; or page every 2.5 s; a "SALE" blink at 2 Hz |
| `chochin` | Japanese paper-look lantern, electric, with a painted name; red is the **izakaya** | ⌀0.33 × 0.67 (izakaya); ⌀0.2–0.6 | H by the door, 2–2.4 m up; pairs | red `#d8261c` with black letters, white `#f6efe0` | steady; a slow sway of ±4° at 0.3 Hz |
| `lantern_cn` | Chinese round silk lantern with a tassel | ⌀0.3–0.45 × 0.55–0.65 ([boozed](https://boozed.nl/en/product/chinese-lantern-red-fabric-globe-o33xh55/)) | H, rows along eaves or across lanes | red `#e0201a`, gold `#ffc23a` | sway |
| `lantern_string` | festoon bulbs on a catenary between buildings, across lanes, up balloon tethers | bulb ⌀0.05–0.13 (S14 or G40), every 0.5 m (also 0.9 m); sag 4–8 % of span ([Harvey Norman](https://www.harveynorman.com.au/jingle-jollys-s14-bulb-41m-led-festoon-lights-kit-warm-white.html)) | H via `lights_<n>` anchors | warm `#ffd38a`, or carnival mixed red/amber/green/blue | steady; carnival **chase** of 3–4 phases (every Nth bulb a channel, [Wikipedia: Chase](https://en.wikipedia.org/wiki/Chase_(lighting))) at a 0.25 s step |
| `marquee_bulbs` | bulb border round a sign or arch (Columbia's fairground) | bulbs ⌀0.06 every 0.15–0.25 | F | warm white | **chase**: 3 phases, 0.2 s step; or all-blink 1 Hz |
| `brass_letters` | separate cut letters on the facade, halo-lit from behind | letter h 0.3–0.9 | F | gilt `#d9a441` lit from behind with warm `#ffb860` | steady |
| `painted_board` | hand-painted timber board, lit by a gooseneck lamp | 1–4 × 0.4–1 | F | clan palette | steady; the old ones are "ghost signs" |
| `noren` | split cloth curtain in the door with the shop crest | 0.85 × 0.9–1.5 (2–4 panels) | in the door | indigo `#22355e`, red, white | cloth sway |
| `banner_vertical` | cloth banner (nobori) on a pole, or a long vertical drop down a facade | 0.45–0.6 × 1.8–2.4 (nobori); drops 1 × 6–20 | G or F | clan colours | wind flutter |
| `sign_figure_3d` | giant figure sign, Kani Dōraku style: a goat, bee, bell, lark, fish or kettle, with **moving parts** | 2–6.5 | over the shop entrance | as the object, plus neon outline | limbs or wings move on a 1–3 s loop; eyes blink |
| `rooftop_billboard` | lit billboard frame on a roof, its back a catwalk | 6–20 × 3–10 (Glico: 10.4 × 20, [Wikipedia](https://en.wikipedia.org/wiki/D%C5%8Dtonbori)) | R | full colour; neon border | the image swaps every 8 s; a border chase |
| `balloon_ad` | **ad printed on, or projected onto, a balloon envelope**: the biggest signs on the station, seen across the ring | 60–90 wide band × 100–600 tall on the 1 km envelope | the envelope | clan colours, gold | lit from inside at night; the band slowly scrolls round; a "lit window" panel pulses |
| `video_board` | retrofit screen (Blade Runner) made of dot-matrix tiles, showing a slow two-colour animation | 2–8 × 1.5–5 | F | amber or green | frame-by-frame at 4–8 fps |
| `vending_glow` | the vending-machine face: a lit panel of cans | 1 × 1.8 | G | white with coloured cells | steady; it hums |
| `window_sticker` | lettering on lit shop glass | 0.5–2 × 0.3–0.8 | in a window | white and gold | steady |

**Density per style** (`signage.density` in styles_b.json, 0..1): the sign count per storefront and facade metre.
- **0.2:** one sign per shop.
- **0.5:** a shop sign, a projecting blade, and a lantern pair.
- **0.8:** every shop has 2–4 signs, every facade a projecting stack, and lights strung across every lane.
- **1.0:** Kowloon or Mong Kok: signs overlap and hide the facade above the first floor.

## 2. Animation patterns (shader timing)
Every pattern is a function of time, so they can all run in one shader:
- `steady`: on.
- `flicker`: a failing tube, on 92–98 % of the time. Dropouts last 40–120 ms in bursts of 2–5 every 4–20 s, with a 30 %
  dimming buzz.
- `flash`: 1 Hz, 50 % duty; or a "double blink" of 0.15 on, 0.15 off, 0.15 on, then 1.5 s off.
- `sequence`: segments light in order, 0.3–0.5 s per segment, hold 1.5 s, then everything off for 0.4 s and repeat. This is
  the classic neon sign sequencer.
- `chase`: N phases (3 or 4), the bulb at index i lit when `(i - floor(t / step)) mod N == 0`, step 0.15–0.3 s.
- `scroll`: dot-matrix text moving at 6 chars/s (about 40 px/s at 7 px characters); pause 1 s between messages.
- `swap`: a billboard cross-fading between 2–4 images every 6–10 s.
- `breathe`: mood light, a sine of period 6–12 s between 70 % and 100 %.
- `sway`: lanterns ±3–5° at 0.2–0.4 Hz, with phase varied per lantern.
- **Phase:** per sign, take a hash of the sign id × the period, so a street never blinks in unison. *Except* a few signs on
  each island that are **deliberately synced** (an island's "heartbeat" sign).

## 3. Night light: the layers (what makes "a christmas tree")
From the Nathan Road photographs, the "dense, overlapping canopy of glowing glass tubes ... crimson, emerald and amber"
([Blue Lotus](https://bluelotus-gallery.com/blog/2026/7/8/city-of-lights-keith-macgregor-on-documenting-hong-kongs-lost-neon-nightscapes)).
Build each island's night in these layers, back to front:
1. **Window glow:** every residence lights its windows in **the building's mood colour**. Apartment complexes each get one
   mood: amber `#ffb35c`, rose `#ff7aa8`, teal `#3fe0d0`, violet `#9a6bff`, warm white `#ffe2b0` or cold white `#dfe9ff`.
   About 60–85 % of windows are lit in the evening, falling to 20 % at 3 am.
2. **Architectural motif lighting (apartment complexes):** one stylish motif per complex. It is drawn as `glow_<motif>_<n>`
   anchors written by the generator:
   - `strip_outline`: LED lines along the floor slabs and parapets (the Chungking 2010 LED bands);
   - `uplight`: lights washing the pilasters;
   - `porthole_ring`: a ring round each round window;
   - `eave_line`: bulbs along every eave (bathhouse);
   - `arch_bulbs`: bulbs round each arch;
   - `lattice_backlit`: light behind a lattice screen.
3. **Shop signs:** each store's own sign (§1), its kind picked from the island style's `signage.kinds`, the name from the
   generator (§4), and a colour from the style's palette.
4. **Street and lane light:** lanterns over doors, lantern strings across lanes, and festoons along the promenade and the
   fence top.
5. **Rooftop:** billboards, roof-shrine lanterns, **marquee bulbs on the bridge gates**, and lit **water tanks** (they glow
   when back-lit).
6. **The balloons:** **lit from inside** in the clan colour, 3–8 % emission so they read as giant paper lanterns; plus the
   **balloon ads** and **tether festoons** running down to the deck. This is what the floor sees: from 10 km away, every island
   is a cluster of glowing columns.
7. **Reflection:** snow on the deck brightens and takes the colour of the signs (the snow overlay can add sign colour).
   Ponds reflect.

**Doing it cheaply** (game technique):
- Neon is a **bright thin core with a wide soft halo**, so render the emissive tube slightly over white in HDR and let
  **bloom** make the halo. Don't blur the texture itself, which looks muddy
  ([codemia](https://codemia.io/knowledge-hub/path/algorithm_for_neon_glow_graphics_programming)).
- **Flicker from a time-driven shader or a scrolling emission mask**, not from lights
  ([Neon Trigger devlog](https://aidanbrennan55.itch.io/neontrigger/devlog/975891/neon-trigger-devlog-6-shaders-and-post-processing-for-unity)).
- Too much bloom makes thin glows alias and flicker with distance
  ([Unreal answers](https://answers.unrealengine.com/questions/421/view.html)). So fade small signs out by distance, keep the
  emission moderate, and **swap to a per-building "glow card" at LOD1/LOD2**: one emissive quad per face in the dominant
  colours.
- **No real lights per sign.** At most one OmniLight per near storefront cluster, with **fake light pools on the ground**
  (an additive decal or quad in the sign colour under each sign).
- Text: Godot TextMesh or Label3D with an emissive unshaded material (no glyph atlas files). The sign shapes are a few
  shared meshes (box, frame, tube outline) plus TextMesh.

## 4. Shop-name generator (Aloft commerce culture)
Inputs come from the canon (remake/bible/sky_islands.json): goods, slang (lexicon), sayings and customs.

**Tone:** dry, proud, weight-obsessed, nautical-knotted, punning (Ankh-Morpork humour). Shops are **family and clan**
businesses, and names often carry the owner, the island or a knot.

**Templates** (pick by `shop_kind`):
- `{Owner}'s {Goods}`: e.g. "Ama's Ganseys", "Old Petra's Moss".
- `The {Adjective} {Thing}`: "The Light Kettle", "The Honest Kilo", "The Last Snow".
- `{Knot} & {Knot}`: "Bowline & Hitch" (a chandler), "Sheet Bend Tailors".
- `{Pun}`: below.
- `{Number} {Things}`: "Three Days Lashed" (a bar), "Ten Islands Tea", "Seven Larks".
- `{Island} {Goods} House`: "Thule Ice House", "Ophir Bell Works".
- `{Saying}`: "Light Hands, Long Lines" (a broker), "No Flame No Fall" (an electrical shop).

**Vocabulary:**
- **Adjectives:** light, weighed, honest, high, cold, quiet, last, first, lucky, lashed, drifting, patched, silver, warm,
  white, westward, Lightening.
- **Things:** kettle, kilo, knot, line, hook, skybox, lark, bell, envelope, cloud, snow, gust, drift, raft, rim, plumb,
  hoist, winch, gansey, mitten, hive, dove, goat.
- **Shop kinds and goods** (from canon trade):

  | kind | goods |
  |---|---|
  | knitwear | ganseys, mittens, hats |
  | down | quilts, jackets |
  | moss | remedies, tea, dye |
  | mead_honey | sky honey, mead |
  | ice | snow, ice cream |
  | bells | bells, chimes, fiddles |
  | larks | parts, fans |
  | weather | forecasts, barometers |
  | rope | rope, nets, lashing line |
  | skycloth | envelope fabric |
  | fish | perch, crayfish |
  | dried_food | berries, greens |
  | air_cured | goat |
  | broker | brokerage |
  | air_post | letters |
  | survey | maps |
  | view | "a view for hire" |
  | books | copied books |
  | beer | cold beer |
  | wine | berry wine |
  | tea_house | moss tea, cloud porridge |
  | long_kitchen | eating house |
  | gas | hydrogen bottles |
  | electrical | cells, boards |
  | dentist/healer | |
  | barber | |
  | pawn | "weighed and lent" |
  | arcade | games |

- **Puns and joke names** (seed list; the generator mixes these with the templates):
  - "Weigh More" (a scale maker)
  - "Heavier Than You'd Think" (a bakery)
  - "Ground Floor" (a bar for plumbs)
  - "The Lightening Rod" (an electrical shop)
  - "Knot Bad" (a café)
  - "Hitch & Brew"
  - "Gust Come In"
  - "Lift & Shift" (movers)
  - "The Snow Must Go On" (an ice shop)
  - "Mind the Edge"
  - "Bee Line" (a honey shop)
  - "Cloud Nine Teas"
  - "Long Drop Funerals" (canon: the dead go down)
  - "Three Days Lashed"
  - "The Knives" (a cutler; the Casting Off)
  - "Heavies Welcome" (a tourist inn)
  - "Light Fingers" (a pickpocket-proof bag shop)
  - "Rim Shots" (a bar on the rim)
  - "Up & Away" (a lark charter)
  - "The Plumb Line" (a tailor)
  - "Kilo for Kilo" (a barter house)
  - "Dove Tales" (books)
  - "Fan Club" (a lark-fan repairer)
  - "Mitten Kitten"
  - "Hot Can Machine"
  - "Weather or Not" (a forecaster)
- **Scripts:** most signs are in the station's English. Each island's **heritage** (canon `heritage`) can add a **second line
  in a heritage script**: Chinese, Japanese, Arabic, Devanagari, Spanish and others, rendered by TextMesh with the right
  font. This matches HK and Tokyo bilingual signage
  ([Varnelis](https://varnelis.net/works_and_projects/the-zakkyo-biru-of-ginza/)).
- **Dot-matrix messages** (scrolling):
  - "HOIST AT 14:00 — GRAIN 2 BOXES"
  - "LASHING SALE"
  - "SNOW HONEY IN"
  - "WEIGHED FAIR SINCE VY 412"
  - "LARK PARTS — ASK INSIDE"
  - "THREE DAYS LASHED — DRINK NOW"
  - "FORECAST: CLOUD 18:00 — SNOW"

## 5. Apartment complex motifs (one per complex; the style suggests a pool)
| motif | the look by day | the look by night |
|---|---|---|
| `lantern_balconies` | a chōchin or lantern on every balcony | warm dots in a grid |
| `strip_outline` | LED lines on the slab edges | coloured contour lines (Chungking) |
| `porthole_glow` | round windows (capsules, Zonai) | rings of light |
| `lattice_glow` | screen lattices (koshi, mashrabiya) | a backlit lattice pattern |
| `eave_bulbs` | stacked eaves (bathhouse) | bulb lines along every eave |
| `rooftop_garden_lights` | roof gardens | fairy lights in planters |
| `laundry_lights` | laundry lines | festoons on the laundry poles |
| `mural` | painted end walls | an uplit mural |
| `bell_tower` | a little belfry | its bells lit gold |
| `stained_glass` | the stair tower's glass | the stair glows in colours |

Each complex picks a **motif** and a **mood colour** (traits.mood), and SkySigns lights it.
