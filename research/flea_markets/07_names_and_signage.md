# 07 Market names, regional sign styles and the sign kit

The user, 2026-10-15:
- "The flea markets will each need their own name and stylized signage."
- Every town gets its own market, each "unique, a local draw and the town's pride".
- The user approved The Ropewalk, The Starlite Swap, Traders' Landing and Iron Wheel Trade Days.
- **Regional style:** the North Land is stately and classic; the South Land is laid-back and California-inspired; the
  river towns are a gradient of both, showing how they are culturally connected; the islands are flashy and modern,
  with each society's ethnic flair.

The Grok briefs that make the sign art are in **08_signage_briefs.md**.

## 1. How the names and styles were made

### 1.1 Names
- **American flea-market naming patterns** (03 §23):
  - **Trade/Trader** (Trader's World, Trade Days);
  - **World/Village/Center**;
  - **a rural or roadside object** (Barn, Wheel, Mustang, Starlite);
  - **Swap** (Swap Shop, swap meet);
  - **place plus event** (First Monday Trade Days);
  - Spanish nicknames (La Pulga).
- **Origins** (03 §23): auction barns, court days, drive-in theatres, reused sites, fairgrounds and highway land.
- **Heritage, not anachronism.** In 2752 the station keeps its American heritage on purpose (Gregorian months, Draw
  Day, sheet cakes, polkas: `research/bible/01_world.md:76`, `06_culture.md`). A retro roadside name is loved
  heritage.
- **Each name comes from its town's own character** (`tools/settlegen/towns.py:14-111`) and the thing it is known
  for.

### 1.2 The style axis
`t = (x + 5600) / 11200`: 0 is the North Sea shore and 1 the South Sea shore, from each town's centre x in
`law/settlements.json`.

| band | t | feel | type | colour | light | build |
|---|---|---|---|---|---|---|
| **North Land** (north_shore, northland) | < 0.35 | stately, classic, civic | gilt or carved Roman serifs, small caps, engraved slab | deep reds, navy, forest green, cream, gold leaf, granite | warm amber bulbs, gas-lamp style, floodlit boards; **no neon** | granite, brick, painted timber, cast iron, symmetry, heraldic and maritime motifs |
| **River towns** (kettle_valley + the inland edges) | 0.35–0.65 | the gradient | a classic serif or slab **with one laid-back accent** (a neon script word, a painted swash) | classic base colours with a pastel or sunset trim | bulbs, plus one neon element | brick and steel with a stucco, tile or awning touch: the Kettle connects both shores |
| **South Land** (southland, south_shore) | > 0.65 | laid-back, sunny, playful (California) | neon script, Googie sans, hand-lettered brush, Streamline Moderne inland | sunset orange, pink, turquoise, sand, palm green, night blue | neon, chase bulbs, marquee boards | stucco, mission tile, drive-in screens, palms, starbursts, fibreglass mascots |
| **Islands** (aboard, and the islanders' tents and stalls at a market) | — | flashy, modern, each society's own flair | each warren family's script and motifs (08 §B) | the family palette plus clan colours | LED, neon, dot-matrix, lanterns, video | the warren kit's sign pieces (`ov_sign_*`, `ov_sign_arm_big`, `wall_sign_column_t`) |

- **Inland southland towns (t ≈ 0.68–0.72)** are "inland California": Central Valley and Route 66 roadside. Googie
  and Streamline, rather than beach.
- **Kessler (t 0.68)** keeps its Art Deco rail identity as **Streamline Moderne**, the Los Angeles side of Deco.
- **A Lowliner touch in the South:** southern markets with many Lowliner vendors carry a Skein lantern or a clan pennant
  on their sign. That is part of how the South looks now.

## 2. The 22 markets
Format: **Name**, town (region, t). Then: what it's known for (its draw, which feeds the weekend trips, 00 §6.3); the
sign; the mascot or landmark; colours.

### North Land (t < 0.35): stately and classic

**1. The Ropewalk** ("Carrow Ropewalk Market & Swap"), Port Carrow (north_shore, 0.00), city.
- **Draw:** maritime antiques, sailcloth and rope; the Skein's rope stalls. The covered sheds are a restored 300 m
  ropewalk.
- **Sign:** a 12 m granite-and-timber pylon wrapped by a giant figure-eight rope knot with amber chase bulbs.
  Gold-leaf Roman serif "THE ROPEWALK" on barn red; a cream band "MARKET & SWAP · FRI SAT SUN".
- **Mascot:** "Salty", a herring gull in a yellow sou'wester holding a rope coil (painted sheet metal, a bulb eye).
- **Colours:** #8E2B22 barn red, #EFE3C2 cream, #C9A23A gold, #6E6E6A granite, #2F5D50 sea green.

**2. The Lobster Pot** ("Brightwater Lobster Pot Antique & Flea Fair"), Brightwater (north_shore, 0.01), town.
- **Draw:** resort antiques, summer-cottage clear-outs, crafts, chowder.
- **Sign:** a giant slatted lobster trap on granite posts, strung with painted buoys; an oval gilt-serif board.
- **Mascot:** a red lobster weathervane on the pot.
- **Colours:** lobster red, buoy yellow, white, navy, weathered cedar.

**3. The Tide Clock**, Haven Point (north_shore, 0.01), village.
- **Draw:** nautical instruments, clocks, chandlery salvage, brass.
- **Sign:** a tall white clapboard tower with a giant **tide-clock face** (one hand, HIGH/LOW), and an engraved slab
  "THE TIDE CLOCK · MARKET".
- **Landmark:** the clock itself.
- **Colours:** white, navy, brass, signal red.

**4. The Net Loft**, Tern Harbor (north_shore, 0.01), village.
- **Draw:** fishing gear, nets, smoked fish, cannery-closure bargains (a rust-belt village: the cheapest pitches on
  the north shore).
- **Sign:** the grey-shingled gable of an old net loft, lettered in white sign-painter serif, with a net and glass
  floats hung below.
- **Mascot:** a carved tern on the ridge.
- **Colours:** shingle grey, white, faded red, float green.

**5. The Water Tower**, Loomis Grove (northland, 0.24), village.
- **Draw:** tools, salvage and junk; farm auctions. A declining crossroads with the cheapest stalls on the map.
- **Sign:** the village water tower, painted with "LOOMIS GROVE · THE WATER TOWER · FLEA" in classic block capitals
  and floodlit.
- **Colours:** silver, black, oxblood.

**6. The Book Barn** ("Fenwick Book Barn & Flea"), Fenwick (northland, 0.31), town.
- **Draw:** books, maps, records, college clear-outs (students, teachers).
- **Sign:** a white classic barn with green trim. Over its doors hangs a giant **open book** carved and gilded, with
  the name in small-caps serif on its pages. Brass lamps.
- **Colours:** white, college green, gold, oxblood.

**7. The Weathervane** ("Dunmore Weathervane Auction & Flea"), Dunmore Crossing (northland, 0.31), village.
- **Draw:** **the Friday livestock and farm auction** (Rogers model), with flea stalls round the sale barn.
- **Sign:** a tall post crowned by a giant copper **bull weathervane** with N-E-S-W letters, over a painted board:
  "AUCTION FRI · FLEA SAT SUN".
- **Colours:** verdigris copper, barn red, white.

**8. Brannock County Trade Days**, Marlowe (northland, 0.32), town.
- **Draw:** quilts, crafts, antiques and county-fair food, under the county's name (the courthouse town).
- **Sign:** a classic **county-fair arch** of white timber with a gilt eagle finial; "BRANNOCK COUNTY TRADE DAYS" in
  gilt serif on navy; bunting.
- **Colours:** navy, white, gilt, flag red.

### River towns (0.33–0.65): the gradient

**9. The Boathouse Swap**, Port Tamsin (kettle_valley, 0.33), village.
- **Draw:** boats, outboards, tackle, lake gear.
- **Sign:** a classic green-and-white boathouse with a striped awning. Over the doors, **one neon script word**
  "Swap", and a leaping-fish outline in turquoise neon.
- **Colours:** forest green, white, turquoise neon.

**10. Four Corners Swap**, Haskins Corner (northland, 0.34), village.
- **Draw:** new goods, family stuff, exurban yard-sale bargains.
- **Sign:** a **finger-post tree**: a classic white post with arrow boards pointing to every other market, with their
  km ("THE ROPEWALK 31 · STARLITE 58 …"). The top board carries a small sunset-painted "SWAP". It shows the circuit.
- **Colours:** white, black lettering, a sunset accent.

**11. The Regatta Swap**, Victory Bay (kettle_valley, 0.43), village.
- **Draw:** upscale antiques and designer goods (an upscale island village).
- **Sign:** a tall white racing-sail pylon with **regatta pennants**. Classic serif, with a pastel striped
  spinnaker accent.
- **Colours:** white, navy, pastel stripes.

**12. Millwheel Market**, Cedar Ford (kettle_valley, 0.44), village.
- **Draw:** handmade crafts, woodwork, flour and bread from the grist mill.
- **Sign:** a **timber waterwheel** (5 m) that really turns, its paddles edged with warm bulbs; a carved slab board
  with a hand-painted swash.
- **Colours:** oak, millstone grey, cream, a terracotta trim.

**13. Traders' Landing**, Harrow Falls (kettle_valley, 0.58), city.
- **Draw:** **the first mooring (VY 418)** and the Skein's biggest landing; **the Low Lashing** each June.
- **Sign:**
  - the **bow of a lake freighter** as the entrance arch (red over black, condensed slab capitals outlined in bulbs);
  - a **lighthouse** pylon with a turning beacon;
  - the gradient touch: a neon script "Landing" under the slab "TRADERS'".
- **Mascot:** "Cap'n Harrow", a fibreglass freighter captain with a lantern.
- **Colours:** freighter red, black, white, lake blue, brass, plus a sunset-orange neon.

### South Land (t > 0.65): laid-back and California-inspired

**14. Iron Wheel Trade Days**, Kessler (southland, 0.68), city.
- **Draw:** tools, parts, machinery, railwayana.
- **Sign:** a 6 m **locomotive driving wheel** with chase bulbs on its spokes, on a **Streamline Moderne** plinth;
  a fin carrying "IRON WHEEL" in thin-thick Moderne neon, white, with "TRADE DAYS" in green.
- **Colours:** black, Deco green, chrome, signal red, cream.

**15. The Red Granary**, Bellhaven (southland, 0.68), town.
- **Draw:** farm produce, college clear-outs, vinyl records.
- **Sign:** a red granary with a white **sunburst** painted on its gable and Googie script "Red Granary". Chase bulbs
  on the roofline.
- **Colours:** barn red, white, sunburst yellow.

**16. The Tall Tamarack**, Tamarack (southland, 0.69), town.
- **Draw:** lumber, furniture, woodcraft (a mill town).
- **Sign:** a 14 m fibreglass **tamarack tree** wrapped in coloured bulbs (gold in autumn, like the real larch), with
  a 1950s boomerang board.
- **Colours:** tamarack gold, pine green, turquoise.

**17. Elevator Flea Days**, Pruett (southland, 0.71), village.
- **Draw:** farm equipment, seed, rail relics.
- **Sign:** the town's grain elevator, painted with a giant **roadside-postcard** "ELEVATOR FLEA DAYS" in pastel
  letters, each letter a little picture.
- **Colours:** concrete white, pastel postcard colours.

**18. Route 30 Swap Meet**, Calder (southland, 0.72), town.
- **Draw:** car parts, roadside Americana, the hospital town's weekend crowd. Calder sits on US 30.
- **Sign:** a giant **highway-shield pylon** ("US 30" shield shape) in Googie neon with a starburst; "SWAP MEET" on a
  boomerang arrow.
- **Mascot:** "Ozzie", a smiling fibreglass roadside mechanic waving a wrench.
- **Colours:** shield white and black, turquoise, orange neon.

**19. La Pulga Verde**, Playa Verde (south_shore, 0.98), town.
- **Draw:** plants, produce, cooked food, crafts. A pier town: palms and families.
- **Sign:** a neon **pier-and-palm** pylon in green and turquoise; "LA PULGA VERDE" in brush-script neon over a
  mission-tile cap. No caricature mascot: the sign stays about the place.
- **Colours:** palm green, turquoise, terracotta, sand.

**20. The Starlite Swap** ("Starlite Drive-In Swap Meet", nickname "La Estrellita"), Solana Point (south_shore, 0.99),
city.
- **Draw:** everything. The biggest Lowliner market, night swaps on fair evenings, and the island routes' favourite
  mooring.
- **Sign:** the old 20 m **drive-in screen tower** with a sunset mural. "STARLITE SWAP" in 1950s neon script with a
  Googie starburst; a marquee board ("THIS WEEKEND · ISLAND FAIR!").
- **Mascot:** "Sunny", a smiling sun in sunglasses.
- **Colours:** #F0803C, #E85A8C, #2BB3B1, #E9D6A8, #3F7A3A, #1B2A4A.

**21. The Carousel Swap**, Oceanview (south_shore, 0.99), town.
- **Draw:** boardwalk toys, surf gear, beach things, games.
- **Sign:** a giant **carousel horse** on a striped pole, with rainbow bulb letters on a carousel canopy.
- **Colours:** candy stripes, gold, sky blue.

**22. The Pelican Swap**, Pelican Cove (south_shore, 0.99), village.
- **Draw:** bait, tackle, shells, surfboards, fish tacos.
- **Sign:** a fibreglass **pelican** in a sun hat perched on a piling, beside a surfboard-shaped board in
  hand-lettered brush script.
- **Colours:** sand, sea turquoise, coral, white.

### 2.23 The islanders' overlay (every market)
- **The Skein banner:** clan pennants across the entrance while an island is moored.
- A lit **ISLAND FAIR** dot-matrix board (`sky_dot_font.gd`) scrolls the moored islands' names.
- Every islander tent has its family's sign style (08 §B).

## 3. The sign kit (KIT stream)
Assembled from data (`market_styles.json`). The faces are **textures cropped from the Grok sheets** (08). The
structures are modular meshes.

| piece | variants | notes |
|---|---|---|
| `sign_pylon_post` | granite, timber, steel lattice, Moderne fin, stucco tower, clapboard tower | 6/9/12/20 m; anchors `sign_face_*` |
| `sign_board` | flat, oval, cabinet (backlit), marquee (letter tracks), boomerang, shield | takes an atlas face |
| `sign_arch` | timber fair arch, steel truss, freighter bow | spans 8–14 m |
| `sign_landmark_*` | rope knot, lobster pot, tide clock, water tower (texture only), open book, bull weathervane, finger-post, sail, waterwheel, lighthouse, iron wheel, tamarack tree, highway shield, pier-palm, screen tower, carousel horse, pelican | one each, 2–8k tris |
| `mascot_*` | salty, capn_harrow, sunny, ozzie | fibreglass figures |
| `neon_tube_*`, `bulb_chase` | outline sets | `sky_neon` / `sky_bulbs` shaders |
| `marquee_tracks` | changeable letters | data-driven text (fair board) |

- **Lit parts come from the face textures.** `crop_sheets.py` makes an emissive mask by hue and value: neon tubes,
  bulbs and lightbox faces. The night look is a shader, not a second image (08 §0).
- **Budgets:** a pylon sign ≤ 6k tris plus bulbs at LOD0; ≤ 1.5k at LOD1; a 150-tri card plus bulbs far. Bulbs and neon
  join the far bulb tier, so the signs read from km off at night. No real lights; at most one claimed pool light within
  40 m.

## 4. Data: `godot_project/remake/markets/market_styles.json`
```
{"FM-PCR": {"name": "The Ropewalk", "long": "Carrow Ropewalk Market & Swap", "band": "north", "t": 0.00,
            "draw": ["maritime_antiques", "rope"], "landmark": "rope_knot", "mascot": "salty",
            "face": "markets/fm_pcr_main", "face2": "markets/fm_pcr_mascot",
            "palette": ["#8E2B22", "#EFE3C2", "#C9A23A", "#6E6E6A", "#2F5D50"], "neon": false, "festoon": 4},
 "FM-SOL": {"name": "The Starlite Swap", "nick": "La Estrellita", "band": "south", "t": 0.99, ...},
 ... one per market, 22 in all }
```
