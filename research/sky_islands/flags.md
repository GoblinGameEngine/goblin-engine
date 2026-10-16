# Island flags (PROVISIONAL)

One flag per sky island, made by `tools/signs/make_flags.py` from the canon (`remake/bible/sky_islands.json`).
**Provisional** until the political work: the designs are invented here and may change.

## The grammar

Real vexillology rules (simple enough to draw from memory, 2-3 colours, one emblem, readable at a distance, no
lettering, distinctive), and no copy of any real national flag.

- **The forked fly** (a swallowtail cut into the fly) is on every Skein flag: the confederation's shared mark,
  "flown like a skein of geese". It is also what makes them read as sky flags from the floor.
- **The field layout is the island's governance:**
  - the Helm: a prow-shaped triangle at the hoist, the captain's bow
  - plumb rule: a central upright band, the plumb line
  - council of elders: three bands, the Old Lines
  - consensus: a disc, the ring where everyone speaks
  - the mother house: a border enclosing the field, the house
  - sortition by lot: a diagonal cut, chance's division
  - the guild: a canton, the guild hall in the corner
- **The colours are the clan's**, its three colours (bible `clans[].colors`), the two most contrasting as the
  field and the third as the device or fimbriation.
- **The emblem is the island's specialty**, what it makes and trades, in whichever colour contrasts best:
  skycloth cloth, cordage rope, knitwear mitten, down feather, honey honeycomb, weather weather, ice snowflake, moss moss, larks lark, bells bell, brewing hop, survey plumb triangle, courier kite letter, dried drying fish, gas gas flask, lore knot cord, gardens terraces seedling, wool ram, fish perch, trade scale.
- **The mix (the user, 2026-10-16):** an island's people and its architecture often differ (Ithaca: Black
  Anglo people in a Maghrebi medina), "it shows how cultures mixed". So the **upper fly carries the warren
  culture's motif** (the architecture's ornament: North Africa and the Levant rosette, Arabia, Persia, the Silk Road compass star, South Asia lotus wheel, the Himalaya and China lantern, East Asian neon wave lines, Southeast Asia and Matera seven lamp, the Americas terraced hill, the Mediterranean and Anatolia bell tower, Northern Europe, Balkans, Caucasus knot crown)
  **in the heritage's colour** (an invented accent per heritage, e.g. black_anglo green, hispanic gold). On the
  banners the name and wares banners letter in the warren culture's manner, the clan banner in the heritage's.
- Emblem art: Grok silhouette sheets `reference/grok/signs/E1`, `E2` (also governance, faith and landmark
  motifs, kept for later charges).

Atlas: `godot_project/remake/signs/flags.png`, 10 x 10 flags of 128 x 80 px, alpha in the fork; index in
`signs.json` `flags.islands`.

## Banners

Four 64 x 1024 banners per island (`remake/signs/sky/banners/SKY-xxx.png`, side by side; `_emit.png` the night
mask): **0** the island's name in its cultural group's lettering, **1** its wares (pictograms and words from the
canon trades), **2** a streamer of the flag's colours with the emblem, **3** the clan. Caps, tails and borders
are Grok blanks per cultural group (`BN1`, `BN2`); East Asian groups stack their letters. Made to trail about
300 m below the island (the runtime request is in `research/sky_islands/warrens/runtime_requests.md`).

## The flags

| island | clan | governance -> layout | colours | emblem (specialty) | architecture (motif) | people (colour) |
|---|---|---|---|---|---|---|
| SKY-001 Halyard | the McFadden kin | plumb_rule -> pale | #f0c9d6 #2a2a2a #9e2a5b | scale (trade) | scots_lands: Northern Europe, Balkans, Caucasus (knot crown) | irish_scots (#2f8a5a) |
| SKY-002 Bowline | the Lanus kin | lot -> bend | #1d3557 #f1faee #7a1f2b | ram (wool) | hanseatic_gable: Northern Europe, Balkans, Caucasus (knot crown) | black_anglo (#2f7d3a) |
| SKY-003 Spindrift | the Fernandez kin | mother_house -> bordure | #283618 #fefae0 #dda15e | perch (fish) | iberian_white: the Mediterranean and Anatolia (bell tower) | hispanic (#d9a521) |
| SKY-004 Gunwale | the Feld kin | lot -> bend | #f0c9d6 #2a2a2a #9e2a5b | weather (weather) | hanseatic_gable: Northern Europe, Balkans, Caucasus (knot crown) | german (#303030) |
| SKY-005 Mizzen | the Gaudreault kin | helm -> hoist triangle | #fff3b0 #9e2a2b #335c67 | mitten (knitwear) | tyrrhenian_canyon: the Mediterranean and Anatolia (bell tower) | francophone (#2b5aa8) |
| SKY-006 Topgallant | the Robinson kin | plumb_rule -> pale | #5f0f40 #fb8b24 #0f4c5c | lark (larks) | tyrrhenian_canyon: the Mediterranean and Anatolia (bell tower) | black_anglo (#2f7d3a) |
| SKY-007 Crow's Nest | the Zheng kin | guild -> canton | #e8dcc4 #2b3a55 #8c2f2b | scale (trade) | hakka_tulou: the Himalaya and China (lantern) | east_asian (#c8302a) |
| SKY-008 Fathom | the Grose kin | mother_house -> bordure | #0b3954 #bfd7ea #ff5a5f | kite letter (courier) | caucasian_balcony: Northern Europe, Balkans, Caucasus (knot crown) | anglo (#1f3a68) |
| SKY-009 Windlass | the Falcone kin | lot -> bend | #3c1518 #f2f3ae #a44200 | drying fish (dried) | rupestrian_terraces: Southeast Asia and Matera (seven lamp) | italian (#3a8a4a) |
| SKY-010 Cat's Paw | the Huber kin | guild -> canton | #22303c #e7eef3 #7fa7c9 | snowflake (ice) | hanseatic_gable: Northern Europe, Balkans, Caucasus (knot crown) | german (#f4f1e8) |
| SKY-011 Capstan | the Pacheco kin | plumb_rule -> pale | #6d597a #eaac8b #e56b6f | feather (down) | chongqing_cliff: the Himalaya and China (lantern) | hispanic (#d9a521) |
| SKY-012 Taffrail | the Behrens kin | mother_house -> bordure | #6d597a #eaac8b #e56b6f | plumb triangle (survey) | nouvelle_france: the Americas (terraced hill) | anglo (#1f3a68) |
| SKY-013 Bosun's Chair | the Litchfield kin | mother_house -> bordure | #e8dcc4 #2b3a55 #8c2f2b | mitten (knitwear) | creole_colonial: the Americas (terraced hill) | anglo (#f4f1e8) |
| SKY-014 Clove Hitch | the Padlan kin | council_elders -> tribar | #f0c9d6 #2a2a2a #9e2a5b | drying fish (dried) | straits_shophouse: Southeast Asia and Matera (seven lamp) | east_asian (#c8302a) |
| SKY-015 Lee Rail | the Hahn kin | helm -> hoist triangle | #2b2d42 #edf2f4 #d90429 | lark (larks) | hanseatic_gable: Northern Europe, Balkans, Caucasus (knot crown) | german (#edf2f4) |
| SKY-016 Sheet Bend | the Snow kin | plumb_rule -> pale | #0d3b66 #faf0ca #f95738 | mitten (knitwear) | nouvelle_france: the Americas (terraced hill) | multi (#8a4fb8) |
| SKY-017 Weather Gauge | the Nalley kin | guild -> canton | #2b2d42 #edf2f4 #d90429 | perch (fish) | taipei_tiepi: East Asian neon (wave lines) | multi (#8a4fb8) |
| SKY-018 Spritsail | the Jiang kin | plumb_rule -> pale | #22303c #e7eef3 #7fa7c9 | weather (weather) | hk_neon_canyon: East Asian neon (wave lines) | east_asian (#c8302a) |
| SKY-019 Dogwatch | the Najera kin | plumb_rule -> pale | #22303c #e7eef3 #7fa7c9 | kite letter (courier) | creole_colonial: the Americas (terraced hill) | hispanic (#d9a521) |
| SKY-020 Sounding Line | the Hsia kin | helm -> hoist triangle | #14213d #e5e5e5 #fca311 | bell (bells) | japan_yokocho: East Asian neon (wave lines) | east_asian (#c8302a) |
| SKY-021 Fairlead | the Terracciano kin | council_elders -> tribar | #1b4332 #f8f9fa #95d5b2 | lark (larks) | karachi: South Asia (lotus wheel) | italian (#3a8a4a) |
| SKY-022 Main Brace | the Schieble kin | guild -> canton | #582f0e #ede0d4 #7f4f24 | honeycomb (honey) | hk_neon_canyon: East Asian neon (wave lines) | german (#f4f1e8) |
| SKY-023 Kedge | the Barker kin | mother_house -> bordure | #0d3b66 #faf0ca #f95738 | bell (bells) | cycladic: the Mediterranean and Anatolia (bell tower) | anglo (#1f3a68) |
| SKY-024 Ratline | the Borsheim kin | guild -> canton | #3d5a80 #e0fbfc #ee6c4d | mitten (knitwear) | siam_khlong: Southeast Asia and Matera (seven lamp) | german (#303030) |
| SKY-025 Jollyboat | the English kin | plumb_rule -> pale | #0d3b66 #faf0ca #f95738 | snowflake (ice) | chongqing_cliff: the Himalaya and China (lantern) | anglo (#f4f1e8) |
| SKY-026 Aureole | the Doucet kin | lot -> bend | #1f4e5f #f2efe6 #d9b44a | knot cord (lore) | nouvelle_france: the Americas (terraced hill) | francophone (#2b5aa8) |
| SKY-027 Halcyon | the Cooney kin | council_elders -> tribar | #6b4f2a #faedcd #d4a373 | drying fish (dried) | hk_neon_canyon: East Asian neon (wave lines) | multi (#f4f1e8) |
| SKY-028 Evenstar | the Mangieri kin | mother_house -> bordure | #6b4f2a #faedcd #d4a373 | kite letter (courier) | japan_yokocho: East Asian neon (wave lines) | greek (#3a7cc0) |
| SKY-029 Hollow Bell | the Aziz kin | plumb_rule -> pale | #f0c9d6 #2a2a2a #9e2a5b | gas flask (gas) | jiangnan_water: the Himalaya and China (lantern) | arab (#1a7a6a) |
| SKY-030 Whisperwind | the Wirkkala kin | consensus -> disc | #f3e2c0 #4a3226 #b5651d | cloth (skycloth) | levantine_courtyard: North Africa and the Levant (rosette) | anglo (#1f3a68) |
| SKY-031 Sibyl's Rest | the Booth kin | consensus -> disc | #5b3a6e #efe7d2 #c9a0dc | lark (larks) | jiangnan_water: the Himalaya and China (lantern) | anglo (#f4f1e8) |
| SKY-032 Moonward | the Mueller kin | consensus -> disc | #3c1518 #f2f3ae #a44200 | plumb triangle (survey) | japan_yokocho: East Asian neon (wave lines) | german (#f4f1e8) |
| SKY-033 Vesper | the Monet kin | council_elders -> tribar | #2b2d42 #edf2f4 #d90429 | knot cord (lore) | taipei_tiepi: East Asian neon (wave lines) | multi (#8a4fb8) |
| SKY-034 Glimmerhold | the Begay kin | mother_house -> bordure | #f0c9d6 #2a2a2a #9e2a5b | perch (fish) | japan_yokocho: East Asian neon (wave lines) | indigenous (#9a4a2a) |
| SKY-035 Ninth Wave | the Pacis kin | guild -> canton | #582f0e #ede0d4 #7f4f24 | bell (bells) | jiangnan_water: the Himalaya and China (lantern) | east_asian (#c8302a) |
| SKY-036 Cloudhallow | the Mohammed kin | lot -> bend | #5b3a6e #efe7d2 #c9a0dc | mitten (knitwear) | cairene_mamluk: North Africa and the Levant (rosette) | arab (#1a7a6a) |
| SKY-037 Starwell | the Golinski kin | council_elders -> tribar | #4a4e69 #f2e9e4 #c9ada7 | feather (down) | caucasian_balcony: Northern Europe, Balkans, Caucasus (knot crown) | polish (#f4f1e8) |
| SKY-038 Elsewhen | the Kennerson kin | helm -> hoist triangle | #1d3557 #f1faee #7a1f2b | scale (trade) | taipei_tiepi: East Asian neon (wave lines) | black (#d07a1a) |
| SKY-039 Farsight | the Downing kin | consensus -> disc | #14213d #e5e5e5 #fca311 | feather (down) | creole_colonial: the Americas (terraced hill) | multi (#8a4fb8) |
| SKY-040 Silver Bough | the McNeil kin | council_elders -> tribar | #22303c #e7eef3 #7fa7c9 | plumb triangle (survey) | rajput_sandstone: South Asia (lotus wheel) | black_anglo (#2f7d3a) |
| SKY-041 Lumen | the Contreras kin | lot -> bend | #f0c9d6 #2a2a2a #9e2a5b | gas flask (gas) | persian_desert: Arabia, Persia, the Silk Road (compass star) | hispanic (#d9a521) |
| SKY-042 Quiet Choir | the Plante kin | lot -> bend | #3c1518 #f2f3ae #a44200 | feather (down) | nouvelle_france: the Americas (terraced hill) | francophone (#2b5aa8) |
| SKY-043 Augury | the Simmons kin | consensus -> disc | #264653 #e9c46a #f4a261 | moss (moss) | creole_colonial: the Americas (terraced hill) | black_anglo (#2f7d3a) |
| SKY-044 Mistcrown | the Ortega kin | helm -> hoist triangle | #1f4e5f #f2efe6 #d9b44a | honeycomb (honey) | latin_hillside: the Americas (terraced hill) | hispanic (#d9a521) |
| SKY-045 Gloaming | the Jorgensen kin | consensus -> disc | #14213d #e5e5e5 #fca311 | moss (moss) | newar: South Asia (lotus wheel) | scandinavian (#2a4a8a) |
| SKY-046 Hallowmere | the Hallowmerekin kin | consensus -> disc | #0d3b66 #faf0ca #f95738 | ram (wool) | chongqing_cliff: the Himalaya and China (lantern) | station_coined (#c0c0c8) |
| SKY-047 Wyrd Lantern | the Velazquez kin | plumb_rule -> pale | #e8dcc4 #2b3a55 #8c2f2b | mitten (knitwear) | korean_hillside: East Asian neon (wave lines) | hispanic (#1a1a1c) |
| SKY-048 Seventh Veil | the Sevilla kin | plumb_rule -> pale | #22303c #e7eef3 #7fa7c9 | ram (wool) | iberian_white: the Mediterranean and Anatolia (bell tower) | hispanic (#d9a521) |
| SKY-049 Saint Elmo | the Montes kin | consensus -> disc | #4a4e69 #f2e9e4 #c9ada7 | moss (moss) | iberian_white: the Mediterranean and Anatolia (bell tower) | hispanic (#d9a521) |
| SKY-050 Candlemoor | the Benton kin | council_elders -> tribar | #2b2d42 #edf2f4 #d90429 | scale (trade) | yemeni_tower: Arabia, Persia, the Silk Road (compass star) | anglo (#edf2f4) |
| SKY-051 Puddingstone | the Leduc kin | helm -> hoist triangle | #14213d #e5e5e5 #fca311 | mitten (knitwear) | ottoman_timber: the Mediterranean and Anatolia (bell tower) | francophone (#2b5aa8) |
| SKY-052 Thistledown | the McGowan kin | lot -> bend | #582f0e #ede0d4 #7f4f24 | scale (trade) | scots_lands: Northern Europe, Balkans, Caucasus (knot crown) | irish_scots (#2f8a5a) |
| SKY-053 Higgledy | the Gunther kin | helm -> hoist triangle | #2b2d42 #edf2f4 #d90429 | weather (weather) | siam_khlong: Southeast Asia and Matera (seven lamp) | german (#edf2f4) |
| SKY-054 Teacup Rise | the Highsmith kin | helm -> hoist triangle | #283618 #fefae0 #dda15e | scale (trade) | latin_hillside: the Americas (terraced hill) | black_anglo (#2f7d3a) |
| SKY-055 Mumblecrust | the Kapoor kin | lot -> bend | #582f0e #ede0d4 #7f4f24 | snowflake (ice) | andean_neo: the Americas (terraced hill) | south_asian (#e07a1a) |
| SKY-056 Pennywhistle | the Horton kin | council_elders -> tribar | #fff3b0 #9e2a2b #335c67 | feather (down) | mardin_terraces: Northern Europe, Balkans, Caucasus (knot crown) | greek (#3a7cc0) |
| SKY-057 Dandelion Clock | the Dandelionkin kin | plumb_rule -> pale | #22303c #e7eef3 #7fa7c9 | scale (trade) | andean_neo: the Americas (terraced hill) | station_coined (#c0c0c8) |
| SKY-058 Hobnob | the Bell kin | guild -> canton | #6b4f2a #faedcd #d4a373 | moss (moss) | ganga_ghat: South Asia (lotus wheel) | anglo (#f4f1e8) |
| SKY-059 Bumbleby | the Garner kin | consensus -> disc | #264653 #e9c46a #f4a261 | cloth (skycloth) | ottoman_timber: the Mediterranean and Anatolia (bell tower) | anglo (#f4f1e8) |
| SKY-060 Gooseberry Fool | the Amaro kin | council_elders -> tribar | #5f0f40 #fb8b24 #0f4c5c | lark (larks) | latin_hillside: the Americas (terraced hill) | hispanic (#d9a521) |
| SKY-061 Hullabaloo | the Caldwell kin | plumb_rule -> pale | #f0c9d6 #2a2a2a #9e2a5b | feather (down) | lusitanian_hill: the Americas (terraced hill) | anglo (#1f3a68) |
| SKY-062 Tumbledown | the Caron kin | council_elders -> tribar | #264653 #e9c46a #f4a261 | terraces seedling (gardens) | taipei_tiepi: East Asian neon (wave lines) | francophone (#f4f1e8) |
| SKY-063 Tiddlywink | the Mercier kin | mother_house -> bordure | #1d3557 #f1faee #7a1f2b | weather (weather) | manila_estero: Southeast Asia and Matera (seven lamp) | francophone (#2b5aa8) |
| SKY-064 Fiddlesticks | the Myrtil kin | helm -> hoist triangle | #1d3557 #f1faee #7a1f2b | bell (bells) | maghrebi_medina: North Africa and the Levant (rosette) | black (#d07a1a) |
| SKY-065 Marmalade Moon | the Poulin kin | council_elders -> tribar | #6b4f2a #faedcd #d4a373 | rope (cordage) | viet_tube: Southeast Asia and Matera (seven lamp) | francophone (#f4f1e8) |
| SKY-066 Cockleshell | the Ceja kin | council_elders -> tribar | #22303c #e7eef3 #7fa7c9 | perch (fish) | latin_hillside: the Americas (terraced hill) | hispanic (#d9a521) |
| SKY-067 Pipsqueak | the Barrios kin | mother_house -> bordure | #2b2d42 #edf2f4 #d90429 | honeycomb (honey) | knights_harbour: the Mediterranean and Anatolia (bell tower) | hispanic (#d9a521) |
| SKY-068 Wobblewick | the McKay kin | lot -> bend | #6b4f2a #faedcd #d4a373 | snowflake (ice) | korean_hillside: East Asian neon (wave lines) | irish_scots (#2f8a5a) |
| SKY-069 Merriweather | the Luong kin | guild -> canton | #14213d #e5e5e5 #fca311 | cloth (skycloth) | straits_shophouse: Southeast Asia and Matera (seven lamp) | se_asian (#e0b020) |
| SKY-070 Sixpence Spire | the Holland kin | council_elders -> tribar | #1d3557 #f1faee #7a1f2b | hop (brewing) | kulla_stone: Northern Europe, Balkans, Caucasus (knot crown) | anglo (#f1faee) |
| SKY-071 Lollygag | the Truong kin | council_elders -> tribar | #4a4e69 #f2e9e4 #c9ada7 | terraces seedling (gardens) | kowloon_walled: the Himalaya and China (lantern) | se_asian (#e0b020) |
| SKY-072 Hopscotch | the Kanter kin | plumb_rule -> pale | #582f0e #ede0d4 #7f4f24 | terraces seedling (gardens) | tibetan_lhasa: the Himalaya and China (lantern) | anglo (#f4f1e8) |
| SKY-073 Kerfuffle | the Roloff kin | consensus -> disc | #0b3954 #bfd7ea #ff5a5f | hop (brewing) | manila_estero: Southeast Asia and Matera (seven lamp) | slavic (#3a5aa8) |
| SKY-074 Crumpet Hill | the Martel kin | consensus -> disc | #fff3b0 #9e2a2b #335c67 | rope (cordage) | viet_tube: Southeast Asia and Matera (seven lamp) | francophone (#2b5aa8) |
| SKY-075 Ragamuffin | the Jeter kin | council_elders -> tribar | #fff3b0 #9e2a2b #335c67 | honeycomb (honey) | andean_neo: the Americas (terraced hill) | black_anglo (#2f7d3a) |
| SKY-076 Ophir | the Nation kin | consensus -> disc | #e8dcc4 #2b3a55 #8c2f2b | drying fish (dried) | karachi: South Asia (lotus wheel) | anglo (#1f3a68) |
| SKY-077 Tarshish | the Niemczyk kin | mother_house -> bordure | #50514f #ffe066 #f25f5c | moss (moss) | rupestrian_terraces: Southeast Asia and Matera (seven lamp) | polish (#c8203a) |
| SKY-078 Thule | the Barba kin | mother_house -> bordure | #fff3b0 #9e2a2b #335c67 | feather (down) | rajput_sandstone: South Asia (lotus wheel) | hispanic (#d9a521) |
| SKY-079 Dilmun | the Small kin | plumb_rule -> pale | #3c1518 #f2f3ae #a44200 | moss (moss) | cycladic: the Mediterranean and Anatolia (bell tower) | greek (#3a7cc0) |
| SKY-080 Punt | the Emmons kin | lot -> bend | #1d3557 #f1faee #7a1f2b | bell (bells) | mzab_ghadames: North Africa and the Levant (rosette) | anglo (#1f3a68) |
| SKY-081 Byblos | the Rosinski kin | lot -> bend | #6b4f2a #faedcd #d4a373 | mitten (knitwear) | mardin_terraces: Northern Europe, Balkans, Caucasus (knot crown) | polish (#c8203a) |
| SKY-082 Ugarit | the Clayberger kin | mother_house -> bordure | #e8dcc4 #2b3a55 #8c2f2b | cloth (skycloth) | mughal_walled: South Asia (lotus wheel) | multi (#8a4fb8) |
| SKY-083 Meroë | the Reams kin | helm -> hoist triangle | #6b4f2a #faedcd #d4a373 | terraces seedling (gardens) | mzab_ghadames: North Africa and the Levant (rosette) | multi (#f4f1e8) |
| SKY-084 Sardis | the Hemby kin | council_elders -> tribar | #e8dcc4 #2b3a55 #8c2f2b | knot cord (lore) | mzab_ghadames: North Africa and the Levant (rosette) | anglo (#1f3a68) |
| SKY-085 Hattusa | the Michaels kin | council_elders -> tribar | #4a4e69 #f2e9e4 #c9ada7 | snowflake (ice) | saharan_kasbah: North Africa and the Levant (rosette) | anglo (#f4f1e8) |
| SKY-086 Elam | the Gillette kin | consensus -> disc | #6b4f2a #faedcd #d4a373 | perch (fish) | mzab_ghadames: North Africa and the Levant (rosette) | anglo (#f4f1e8) |
| SKY-087 Arcady | the Ledesma kin | helm -> hoist triangle | #1b4332 #f8f9fa #95d5b2 | moss (moss) | levantine_courtyard: North Africa and the Levant (rosette) | hispanic (#d9a521) |
| SKY-088 Hyperborea | the Portillo kin | consensus -> disc | #1b4332 #f8f9fa #95d5b2 | feather (down) | yemeni_tower: Arabia, Persia, the Silk Road (compass star) | hispanic (#d9a521) |
| SKY-089 Avalon | the Gross kin | council_elders -> tribar | #5b3a6e #efe7d2 #c9a0dc | weather (weather) | silk_road: Arabia, Persia, the Silk Road (compass star) | anglo (#f4f1e8) |
| SKY-090 Ys | the Pinedo kin | guild -> canton | #1d3557 #f1faee #7a1f2b | perch (fish) | maghrebi_medina: North Africa and the Levant (rosette) | hispanic (#d9a521) |
| SKY-091 Nineveh | the Farley kin | guild -> canton | #e8dcc4 #2b3a55 #8c2f2b | drying fish (dried) | cairene_mamluk: North Africa and the Levant (rosette) | multi (#8a4fb8) |
| SKY-092 Ebla | the Washington kin | mother_house -> bordure | #1d3557 #f1faee #7a1f2b | mitten (knitwear) | saharan_kasbah: North Africa and the Levant (rosette) | black (#d07a1a) |
| SKY-093 Lothal | the Hinkle kin | council_elders -> tribar | #6b4f2a #faedcd #d4a373 | scale (trade) | omani_oasis: Arabia, Persia, the Silk Road (compass star) | anglo (#f4f1e8) |
| SKY-094 Akrotiri | the Rollins kin | plumb_rule -> pale | #a8c47a #3b2a1a #2e5e3a | knot cord (lore) | saharan_kasbah: North Africa and the Levant (rosette) | anglo (#1f3a68) |
| SKY-095 Uruk | the Bermudez kin | helm -> hoist triangle | #5b3a6e #efe7d2 #c9a0dc | moss (moss) | hejazi_roshan: Arabia, Persia, the Silk Road (compass star) | hispanic (#d9a521) |
| SKY-096 Kish | the Pinter kin | council_elders -> tribar | #a8c47a #3b2a1a #2e5e3a | plumb triangle (survey) | karachi: South Asia (lotus wheel) | hungarian (#6a8a3a) |
| SKY-097 Sheba | the Kobayashi kin | helm -> hoist triangle | #0d3b66 #faf0ca #f95738 | honeycomb (honey) | silk_road: Arabia, Persia, the Silk Road (compass star) | east_asian (#c8302a) |
| SKY-098 Colchis | the Munoz kin | consensus -> disc | #3c1518 #f2f3ae #a44200 | kite letter (courier) | omani_oasis: Arabia, Persia, the Silk Road (compass star) | hispanic (#d9a521) |
| SKY-099 Tyre | the Kaquatosh kin | plumb_rule -> pale | #50514f #ffe066 #f25f5c | drying fish (dried) | maghrebi_medina: North Africa and the Levant (rosette) | indigenous (#f4f1e8) |
| SKY-100 Ithaca | the Singleton kin | guild -> canton | #264653 #e9c46a #f4a261 | feather (down) | maghrebi_medina: North Africa and the Levant (rosette) | black_anglo (#2f7d3a) |

Each row reads as a sentence: *the Helm of Halyard's McFadden kin, flying a prow on the clan's plum and
rose, with the brokers' scale*. The meaning of every element is fixed by the grammar above, so a floor child
who knows the rules can read any island's flag.
