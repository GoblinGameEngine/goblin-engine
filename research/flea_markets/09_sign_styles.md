# 09 Sign styles: five families with a shared heritage per region

The user, 2026-10-15: bitmap signs on every shop; "come up with ... styles for each region that share a
common heritage. It will add diversity to the world" (5 per region, corrected). Regions as 07 §1.2.

Each style below is a parameter set in `tools/signs/make_signs.py` (`REGIONS`): fonts (OFL / Apache, fetched
by `tools/signs/fetch_fonts.sh`), palettes (ground, letters, accent), frame, letter treatment, night look and the
affinities that assign it. Grok made what PIL can't: the trade pictograms on the painted and Googie styles
(C sheets), and the island blanks (B sheets).

**Assignment** (deterministic, `pick_style`): each candidate style's weight = its region family's weight
(river towns also draw on the North and South by the gradient t) x its affinity for the business's category x
1 if the building's year suits the style's era (else 0.25) x 1 if the area's wealth (building condition, the
trade's price level, the town's tier) is in its range (else 0.3). A **block lead style** (hashed per 90 m
block) gets x2.6, so the street reads as one place; the next-door shop's style gets x0.15, so neighbours
vary. Vacant units get ghost signs and FOR LEASE boards.

## North Sea shore

**Heritage.** Maritime New England on the cold sea: the chandlers, net lofts and ropewalks of Port Carrow, Brightwater, Haven Point and Tern Harbor. Sign-painting learned from ship carvers: quarterboards, gilt incised Roman capitals, rope and anchor ornament. Materials: painted pine, teak, brass, enamelled iron, weathered shingle. Palette: navy, white, signal red, brass, sea green, tar black. Lettering: Roman serif capitals (carved), slab stencils on the working waterfront. Lights: goose-neck floodlamps and ship's lanterns, never neon.

| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |
|---|---|---|---|---|---|---|
| **Ship's quarterboard** (`quarterboard`): a long carved board with pointed scroll ends, gilt incised capitals, like a ship's name board | Cinzel, PlayfairDisplay | #f2eee2/#c9a23a/#1d2b45; #1d2b45/#d8b452/#f2eee2; #7c2420/#e2c26a/#f2eee2 | pointed | incised | flood | retail, drink, food; 1800-1960; wealth 0.3-1.0 |
| **Chandlery painted board** (`chandlery`): a painted board with a rope border and the trade's pictogram at the left end (Grok blanks C1-C2) | IMFeENrm28P, OldStandard-Bold | #2f5d50/#f2eee2/#c9a23a; #24324a/#f2eee2/#b8402e; #6e3b2a/#f2e6c8/#2f5d50 | rope | shadow | flood | retail, food, industry; 1820-1940; wealth 0.2-0.8 |
| **Signal-flag enamel** (`signal_enamel`): vitreous enamel with a white rim and a signal-flag stripe at the end | Oswald, Arvo-Bold | #1b2a4a/#f4f4f0/#c8202a; #f4f4f0/#1b2a4a/#e0b020; #c8202a/#f4f4f0/#1b2a4a | enamel | flat | flood | service, health, office; 1900-; wealth 0.2-0.9 |
| **Teak and brass** (`teak_brass`): varnished teak with raised brass letters: the harbour's banks, hotels and better shops | Marcellus-Regular, Cinzel | #5a3418/#e0bc62/#2b1a0c; #3a2412/#e8c878/#1a0f06 | wood | metal | flood | office, lodging, service; 1880-; wealth 0.6-1.0 |
| **Cannery stencil** (`cannery_stencil`): stencilled slab letters on weathered planks: the working waterfront | AlfaSlabOne-Regular, Oswald | #8a8c86/#1e1e1c/#b23a2a; #5b6a66/#ecebe4/#c89b2a; #9c4a32/#f0e6d0/#2a2a28 | planks | stencil | none | industry, food, service; 1880-1990; wealth 0.0-0.5 |

## North Land

**Heritage.** The stately Midwest and New England interior: courthouse squares, county seats, college towns (Marlowe, Fenwick, Dunmore Crossing). Federal and Victorian sign-painting, gold leaf on black smalt, porcelain enamel from the 1900s, brass plaques on the professions, painted ghost signs on the brick. Materials: painted wood, gold leaf, enamel, brass, brick. Palette: oxblood, navy, forest green, cream, gold leaf, black. Lettering: Roman and Didone serifs, small caps, gilt with a shade line. Lights: warm floodlamps; no neon.

| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |
|---|---|---|---|---|---|---|
| **Federal gilt on black** (`federal_gilt`): gold leaf letters with a dark shade line on a black smalt board, a gilt rule round it | PlayfairDisplay, Cinzel | #141414/#d6b04a/#7a1f1f; #1c2a1c/#d6b04a/#e8dcc0; #26172a/#d6b04a/#e8dcc0 | gilt_rule | gilt | flood | retail, service, drink; 1790-; wealth 0.4-1.0 |
| **Painted shingle with pictogram** (`painted_shingle`): Colonial Revival carved and painted board, the trade's gilt pictogram at the left (Grok blanks) | IMFeENrm28P, PlayfairDisplay | #8e2b22/#efe3c2/#c9a23a; #24324a/#efe3c2/#c9a23a; #2f5034/#efe3c2/#c9a23a | carved | shadow | flood | retail, food, service; 1800-1950; wealth 0.2-0.8 |
| **Porcelain enamel** (`porcelain`): a curved-cornered enamel sign with a white rim and a chip or two | Oswald, Arvo-Bold | #1f3f8a/#f6f4ee/#c8202a; #a8201c/#f6f4ee/#1f3f8a; #f6f4ee/#1f3f8a/#a8201c | enamel | flat | flood | health, retail, service; 1895-1970; wealth 0.2-0.8 |
| **Brass plaque** (`brass_plaque`): polished brass, engraved and black-filled, four rivets: the professions | Marcellus-Regular, OldStandard-Bold | #b8923e/#2a1e10/#e8cf86; #9a7a34/#1e160a/#d8bc70 | riveted | engraved | flood | office, health, service; 1800-; wealth 0.5-1.0 |
| **Mill-town ghost sign** (`ghost_sign`): letters painted straight on the brick a century ago, half weathered away | AlfaSlabOne-Regular, AbrilFatface-Regular | #8d4a36/#e8dcc4/#5a2e20; #7a4434/#e6d6a8/#3e2418 | brick | faded | none | none, industry, retail; 1860-1940; wealth 0.0-0.4 |

## the river towns

**Heritage.** The Kettle Valley and its river cities (Harrow Falls, Port Tamsin, Victory Bay, Cedar Ford): the gradient between the shores. Riverboat and rail brought both: the North's serifs and gilt meet the South's neon and pastel, so a classic base wears one laid-back accent. Materials: brick, cast iron, terracotta, enamel, painted steel, a neon tube. Palette: the North's reds, greens and creams with a sunset trim (coral, turquoise). Lettering: slab and Victorian display faces, Deco caps, a script word in neon. Lights: bulbs and one neon element.

| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |
|---|---|---|---|---|---|---|
| **Riverboat Victorian** (`riverboat`): ornate Victorian display letters, scroll corners and a row of bulbs, like a packet boat's | Rye-Regular, Sancreek-Regular | #8e1e1e/#f2e2b0/#e0b040; #f2ead8/#8e1e1e/#1d4a6a; #1d4a6a/#f2e2b0/#e0b040 | scroll | shadow | bulbs | drink, leisure, lodging; 1840-1930; wealth 0.2-0.9 |
| **Art Deco terracotta** (`deco_terracotta`): glazed terracotta with Deco sunburst corners and stepped caps, a neon line under the name | Limelight-Regular, PoiretOne-Regular | #e8d8b8/#2a5a4a/#c87a3a; #e8d0b0/#7a2a2a/#2a5a6a; #2a3a3a/#e8c870/#c87a3a | deco | flat | flood_accent | leisure, service, retail; 1922-1950; wealth 0.4-1.0 |
| **Main Street porcelain with neon** (`mainstreet_porcelain`): classic enamel, outlined in a neon tube that lights at dusk | Oswald, Righteous-Regular | #245a3a/#f4f0e2/#ff7a52; #7a1e2a/#f4f0e2/#3ac8c8; #22385a/#f4f0e2/#ff8a3a | enamel_neon | flat | neon_frame | retail, food, health; 1925-1975; wealth 0.2-0.8 |
| **Rail-depot board** (`rail_depot`): a black depot board with spaced white slab capitals and a double rule | JosefinSlab, Arvo-Bold | #141414/#f2f0e8/#c8a040; #2a3a2a/#f2f0e8/#c8a040; #3a2a22/#f2e8d0/#c86a3a | double_rule | flat | flood | logistics, office, industry; 1850-1960; wealth 0.1-0.8 |
| **Serif board with a neon word** (`serif_neon_script`): the name's first word in classic serif, the trade in glowing neon script: the river's signature | PlayfairDisplay, Pacifico-Regular | #efe6cc/#2a2a2a/#ff4a8a; #2a3a4a/#efe6cc/#3ae0d0; #6a1e1e/#efe6cc/#ffb43a | plain_rule | flat | neon_word | food, drink, retail; 1900-; wealth 0.2-1.0 |

## South Land

**Heritage.** Inland California: the Central Valley and Route 30 (Kessler, Bellhaven, Tamarack, Pruett, Calder). Roadside commerce read from a moving car: Streamline Moderne in the rail city, Googie on the highway strip, Mission Revival in the old plazas, citrus-crate colour everywhere. Materials: stucco, terracotta tile, porcelain steel, chrome, neon tube, chase bulbs. Palette: turquoise, sunset orange, cream, chrome, red, palm green, night blue. Lettering: Deco and Streamline caps, Googie script, slab marquee letters. Lights: neon and chase bulbs.

| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |
|---|---|---|---|---|---|---|
| **Googie neon** (`googie_neon`): a boomerang board with a starburst, neon letters and the trade's roadside pictogram (Grok blanks) | Righteous-Regular, Monoton-Regular | #3ab8b0/#fff6e0/#ff6a2a; #ff8a3a/#fff6e0/#2a6ab0; #1a2a4a/#ffe0a0/#ff4a8a | boomerang | neon | neon | food, leisure, lodging; 1945-1975; wealth 0.2-0.9 |
| **Streamline Moderne channel letters** (`streamline_channel`): raised chrome-edged letters with speed lines on a cream fascia; the letters glow at night | Limelight-Regular, PoiretOne-Regular | #d8dcd8/#c8202a/#2a2a2a; #d8dcd8/#1a4a8a/#2a2a2a; #2a2a2a/#e8e8e0/#3ac8c8 | speed_lines | channel | halo | leisure, retail, service; 1930-1955; wealth 0.4-1.0 |
| **Mission tile** (`mission_tile`): stucco with a terracotta tile cap and painted Mission lettering | Sancreek-Regular, Marcellus-Regular | #efe0c4/#7a2e1a/#b8562a; #e8d4b0/#2a4a3a/#b8562a | tile_cap | flat | flood | civic, food, service; 1890-1940; wealth 0.3-1.0 |
| **Citrus-crate label** (`citrus_label`): a crate label: sun rays, a bordered field and fat outlined script | Shrikhand-Regular, Lobster-Regular | #1a3a6a/#ffb02a/#ff6a2a; #2a5a2a/#fff0c0/#ff8a2a; #8a1a2a/#ffe08a/#2a8a4a | label | outline | flood | food, retail, drink; 1900-1960; wealth 0.1-0.8 |
| **Drive-in marquee** (`drive_in_marquee`): a backlit changeable-letter box with chase bulbs | Bungee-Regular, Oswald | #f6f2e0/#1a1a1a/#ff3a3a; #f6f2e0/#c8202a/#1a1a1a | marquee | flat | backlit_bulbs | leisure, lodging, food; 1930-1980; wealth 0.1-0.9 |

## South Sea shore

**Heritage.** The laid-back beach towns (Solana Point, Oceanview, Playa Verde, Pelican Cove): surf, piers, taco stands and boardwalks, with the Lowliners' lanterns among them. Hand-painted by locals, bright and sun-faded; tiki bars; Mexican rótulo painters; 1970s surf-shop supergraphics; neon script over the boardwalk at night. Materials: painted plywood and planks, bamboo, carved wood, stucco, neon. Palette: turquoise, coral, sunset orange, pink, sand, palm green, night blue. Lettering: brush script, fat 70s display, hand-shadowed rótulo letters. Lights: neon script, string bulbs, tiki torches.

| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |
|---|---|---|---|---|---|---|
| **Surf-shop hand-paint** (`surf_handpaint`): brush script on painted planks, sun-faded | KaushanScript-Regular, Satisfy-Regular | #3ac8c8/#fff6e0/#ff6a52; #ff8a6a/#1a3a5a/#fff6e0; #f6e6c0/#1a6a8a/#ff6a52 | planks_bright | shadow | flood | retail, leisure, food; 1950-; wealth 0.1-0.7 |
| **Tiki carved** (`tiki_carved`): carved wood in a bamboo frame, lit by torches | Sancreek-Regular, Rye-Regular | #6a3a1a/#f2d28a/#2a1a0a; #4a2a12/#ff9a3a/#1a0e06 | bamboo | incised | flood_warm | drink, food, leisure; 1935-1975; wealth 0.2-0.9 |
| **Mexican rótulo** (`rotulo`): hand-lettered in bright flat colours with a drop shade and flourishes | Lobster-Regular, Shrikhand-Regular | #ffd23a/#c8202a/#1a5a2a; #2ab0a0/#fff6e0/#ff4a8a; #ff5a8a/#fff6e0/#1a3a8a | flourish | shadow | flood | food, retail, drink; 1900-; wealth 0.0-0.7 |
| **1970s supergraphic** (`supergraphic`): rainbow stripes and fat lower-case letters on a backlit box | Shrikhand-Regular, Bungee-Regular | #f6e8c8/#5a2a12/#ff7a1a; #f6e8c8/#1a3a5a/#2ab0a0 | stripes | flat | backlit | retail, leisure, service; 1965-1995; wealth 0.2-0.8 |
| **Boardwalk neon script** (`beach_neon_script`): neon script on a dark backer over the boardwalk | Pacifico-Regular, Sacramento-Regular | #141c3a/#ff4a9a/#3ae0e0; #141c3a/#3ae0e0/#ffd23a; #1a1a2a/#ffb43a/#ff4a9a | dark_backer | neon | neon | drink, leisure, food; 1925-; wealth 0.2-1.0 |

## Islands

Island shops are the RUNTIME's (`sky_signs.gd`, names drawn procedurally). Their art is the B-sheet blanks
(`sky_a.png`, `sky_b.png`: per warren family a fascia, a blade and an emblem), grouped in nine broad cultural
groups, five styles each (`ISLAND_STYLES` in this file) and the request in
`research/sky_islands/warrens/runtime_requests.md`.

- **North Africa and the Levant (B1):** **zellige LED fascia** (tile border, horseshoe arch in LED); **pierced-brass lantern blade** (brass and coloured glass, warm bulbs); **kufic neon** (angular kufic-style Latin in green and gold neon); **ablaq lightbox** (red and cream bands, gold LED); **jasmine stone board** (black and white stone, vine border, floodlit)
- **Arabia, Persia, the Silk Road (B2):** **roshan lattice** (turquoise and white lattice frame); **qamariya glass** (rainbow half-moon top, backlit); **tile arabesque** (cobalt and turquoise tile, gold LED); **suzani banner** (embroidered hanging cloth with lamps); **brass coffee-house** (brass plaque with a glowing dallah)
- **South Asia (B3):** **pietra dura** (red sandstone with marble inlay, gold LED); **mirror-work banner** (mirror embroidery catching the bulbs); **marigold garland** (saffron board in a marigold LED garland); **truck art** (every inch painted, chrome edge, chains); **torana timber** (dark carved timber arch, copper trim)
- **the Himalaya and China (B4):** **stacked lightboxes** (red and yellow LED boxes stacked up a wall); **vertical red lightbox** (stacked letters, gold edge); **lantern pair** (red paper lanterns either side); **horse-head gable board** (white wall, black tiles); **prayer-flag strip** (five colours, endless knot)
- **East Asian neon (B5):** **neon canyon** (pink and cyan tube frames); **tiepi LED** (corrugated metal, green and red LED); **noren and chochin** (cloth curtain under paper lanterns); **dancheong eave** (pastel blue with painted eaves); **vertical LED column** (stacked letters in white LED)
- **Southeast Asia and Matera (B6):** **tube-house facade** (yellow board, green shutters); **chofa gilt** (teak with a gilded gable flourish); **jeepney chrome** (chrome edges, painted stripes, parol star); **Peranakan tile** (pastel fascia with tile border); **tufa and iron** (carved stone with an iron lamp)
- **the Americas (B7):** **cholet mirror-glass** (bright mirrored colours, step borders); **favela hand-paint** (bright painted board, tile edges); **iron lace** (pastel board, cast-iron lace corners); **bell-cast wood** (red and white carved board, maple leaf); **azulejo** (blue and white tile)
- **the Mediterranean and Anatolia (B8):** **whitewash and tile** (yellow ochre border, tile panel); **Cycladic dome** (white with a blue dome arch); **lemon ceramic** (painted ceramic plaque); **baroque limestone** (honey stone, carved frame, gallarija); **Iznik timber** (dark timber, tile inset, tulips)
- **Northern Europe, the Balkans, the Caucasus (B9):** **stepped gable** (brick red with white trim); **guild bracket** (wrought-iron bracket, hanging board); **tartan crow-step** (dark stone with a tartan stripe); **fretwork balcony** (blue and white carved railing); **copper plate** (Mardin copper, glowing coffee pot)

## Inventory (2026-10-15)

Place units from `npc_place_index.json` (every building's units), sign boards found in the models' lettering.

| region | all units | shop units | sign boards | signed | shop units without a board |
|---|---|---|---|---|---|
| North Sea shore | 2632 | 1476 | 862 | 862 | 171 |
| North Land | 1164 | 675 | 420 | 420 | 65 |
| the river towns | 1818 | 1046 | 588 | 588 | 149 |
| South Land | 1953 | 1198 | 664 | 664 | 229 |
| South Sea shore | 2464 | 1398 | 820 | 820 | 192 |

Shop units by category and region:

| region | civic | drink | food | health | industry | leisure | lodging | logistics | none | office | retail | service |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| North Sea shore | 5 | 67 | 145 | 205 | 21 | 6 | 0 | 0 | 0 | 369 | 198 | 460 |
| North Land | 7 | 19 | 69 | 94 | 1 | 3 | 0 | 0 | 0 | 170 | 89 | 223 |
| the river towns | 5 | 39 | 111 | 139 | 2 | 7 | 0 | 0 | 0 | 272 | 156 | 315 |
| South Land | 5 | 44 | 142 | 164 | 3 | 6 | 1 | 0 | 0 | 293 | 163 | 377 |
| South Sea shore | 3 | 56 | 153 | 175 | 0 | 7 | 0 | 0 | 0 | 396 | 174 | 434 |

Styles used:

- North Sea shore: quarterboard 256, chandlery 229, teak_brass 154, signal_enamel 153, cannery_stencil 70
- North Land: painted_shingle 111, porcelain 77, federal_gilt 77, brass_plaque 53, ghost_sign 38, riverboat 21, rail_depot 16, serif_neon_script 14, mainstreet_porcelain 9, deco_terracotta 4
- the river towns: riverboat 128, rail_depot 102, serif_neon_script 83, mainstreet_porcelain 54, deco_terracotta 52, painted_shingle 35, mission_tile 24, federal_gilt 24, porcelain 22, citrus_label 18, ghost_sign 16, brass_plaque 13, googie_neon 7, streamline_channel 6, drive_in_marquee 4
- South Land: mission_tile 179, citrus_label 167, riverboat 58, googie_neon 52, drive_in_marquee 48, rail_depot 47, streamline_channel 47, serif_neon_script 26, deco_terracotta 22, mainstreet_porcelain 18
- South Sea shore: rotulo 330, supergraphic 160, tiki_carved 115, beach_neon_script 110, surf_handpaint 105
