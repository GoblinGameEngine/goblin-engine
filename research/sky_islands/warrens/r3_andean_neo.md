# R3: Andean towns (Cusco, La Paz, El Alto)

**Island culture:** a high, cold city built on Inca walls. The lower metres are fitted polygonal stone; above it, white colonial stucco storeys carry carved wooden balconies under red tile. Climbing the slopes, self-built brick stacks of La Paz have, at the top, El Alto's *cholets*: mirror-glass, neon-coloured neo-Andean party palaces of shops, a ballroom, flats and a chalet on the roof, painted in Tiwanaku geometry. The mark is the layered age: Inca stone, then colonial white, then raw brick, then neon cholet, each one literally on top of the last.

## Examples
- Cusco:
  - In the historic centre only the bottom few feet of most walls are Inca, with adobe or rough stone above (Spanish builders reused the stones).
  - The Inca stonework survived the 1650, 1950 and 1986 earthquakes while colonial work above fell.
  - Spanish colonial Peru has a base of fitted Inca stones, white stucco walls, baroque stonework round doors, and intricately carved wooden balconies.
  - Sources: [UT Austin archive](https://exhibits.lib.utexas.edu/spotlight/peru-in-the-1920s/catalog/26-685), [smartcitiesdive](https://www.smartcitiesdive.com/ex/sustainablecitiescollective/three-architectural-periods-peru/1063941/), [planetware](https://planetware.com/tourist-attractions-/cusco-cuzco-qosqo-per-cs-cs.htm)
- El Alto, the cholets:
  - Freddy Mamani, self-taught Aymara architect, over 60–100 neo-Andean buildings since 2005.
  - Concrete and brick structure; the first part is monochrome, then colourful Andean-pattern elements are painted on site.
  - The ornament continues inside, especially in the ballroom, the signature space.
  - Clients are the new Aymara middle class: homes, businesses and community spaces.
  - Sources: [sensesatlas](https://www.sensesatlas.com/freddy-mamani-neo-andean-architecture/), [Wikipedia: Neo-Andean](https://wikipedia.com/wiki/Neo-Andean), [pym.de](https://pym.de/en/content/mamani-el-alto)
- Andean trees: queñua (*Polylepis*), about 27 species from 3,500 to 5,200 m, wind and altitude resistant; used in reforestation of La Paz green areas. [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12655902/), [Purcell PDF](https://ceiba.org/wp-content/uploads/Purcell-Polylepis2004.pdf)

## Generator grammar
- **Cell:** 4–5 m bays, storeys 3.0 m (cholet ballrooms 5–6 m double-height), 2–3 storeys colonial, 5–8 storeys cholet.
- **Walls:**
  - Inca base: polygonal fitted andesite or limestone blocks, battered inward 5°, 1.0–1.5 m high, 0.8 m thick, grey `#8a857a`, tight joints, no mortar.
  - Colonial: adobe or stone with white lime stucco `#f1ece0`, a blue or ochre dado.
  - Self-built: exposed brick `#a85a3a` and concrete frame `#9a958c`.
  - Cholet: mirror glass `#9ab8c8`, and painted fields: magenta `#d6337a`, lime `#9acd32`, turquoise `#25b5b0`, orange `#f28a1e`, purple `#6a3a9a`, gold `#e0b030`.
  - Balcony wood dark brown `#4a2e1e`, red roof tile `#a8442e`.
  - Weathering: thin-air UV bleaching, dust.
- **Mass:** colonial courtyard houses (*casonas*) with two-level arcaded patios, and continuous street frontages over Inca bases. On the slopes, irregular stacks of brick boxes with roof slabs left for the next storey (rebar stubs). Cholets: tall narrow towers on the plot, with a commercial ground floor, a ballroom floor, rental floors and a "chalet" penthouse house on the roof.
- **Streets:**
  - A Spanish grid in the core (Laws of the Indies) around the Plaza de Armas.
  - Inca narrow lanes (2.5–3.5 m) between the stone walls, with a water channel down the middle.
  - Very steep stair streets climbing the slopes.
  - Cable-car lines (Mi Teleférico style) overhead.
- **Growth:**
  - Layer 0: Inca walls and terraces (*andenes*).
  - Layer 1: colonial casonas and churches with towers.
  - Layer 2: 20th-century self-built brick.
  - Layer 3: cholets.
  - Layer 4: cyberpunk.
- **Openings:**
  - Trapezoidal Inca doorways and niches (wider at the bottom).
  - Colonial: carved wooden enclosed balconies (Lima-style box balconies, 1.0 m deep, latticed), tall doors with stone surrounds.
  - Cholets: big mirror-glass curtain bands and stepped zigzag frames.
- **Roofs:** red tile roofs at 25–30° with wide eaves; flat brick roofs with rebar; cholets with a peaked chalet on top.
- **Ornament:**
  - Inca stone niches and the twelve-angled stone.
  - Colonial baroque portals.
  - Cholet: Tiwanaku step-crosses (*chakana*), zigzags, condor and serpent motifs in paint and acrylic; chandeliers in the ballroom.
- **Public space:**
  - The Plaza de Armas (a large arcaded square with a fountain and gardens).
  - Market halls.
  - Terraced gardens (*andenes*) as public green.
  - Mirador terraces.
  - The cholet ballrooms: semi-public festival halls.
- **Water:** Inca stone channels and fountains (*paccha*), the plaza fountain, a terraced pond.

## Street hierarchy
- **Avenue round the plaza (main):** 10–15 m.
- **Grid streets:** 6–8 m.
- **Inca lanes:** 2.5–3.5 m.
- **Stair streets:** 2–3 m.
- **Squares:** the Plaza de Armas (60×80 m with arcades), small plazuelas at the churches, terrace gardens.

## Plants
- Queñua (*Polylepis*: twisted, papery red bark, 4–8 m).
- Eucalyptus (introduced, tall and blue-grey, 20 m).
- Molle (Peruvian pepper tree, weeping, 8 m).
- Kantuta flowers (`#c8102e`, the national flower) in the plazas.
- Agave and cactus on the dry slopes.
- Potato and quinoa plots on the terraces.
- Geraniums in tins.
- Very sparse at the upper levels (cold): ichu grass.

## Cyberpunk overlay
- Cholets as the cyberpunk norm: mirror glass, LED Andean geometry, ballroom light shows.
- Cable-car pods everywhere, lit.
- Inca walls with fibre in the joints, glowing outlines.
- Rooftop rebar stubs bristling with antennas.
- Holo-condors.
- **Night:** cholet facades pulse in saturated colour (`#ff2fa0`, `#30e0d0`). Colonial streets are warm amber lanterns. The slopes are a sea of small warm windows (La Paz at night) under cable-car lines of light.

## Kit
- **Shared pieces:**
  - `balcony_timber_covered` (main, Lima box), `screen_lattice`, `arcade_pier`, `patio_gallery`, `gate_portal`, `door_studded`, `barrel_tile_eave`, `bell_tower`
  - `frame_bay`, `frame_infill`, `rebar_stubs` (main), `water_tank`, `corrugated_panel`, `mirror_panel` (main), `geometric_panel` (main), `ballroom_window`, `roof_chalet` (main), `column_mirrored`
  - `funicular` (as a cable car), `fountain_kiosk`, `water_channel`, `market_stall`
- **Unique pieces:**
  - `inca_wall_base`: polygonal fitted stone, battered.
  - `inca_trapezoid_door`.
  - `chakana_relief`: the step cross.
  - `cholet_crown_chalet`.
  - `teleferico_pylon_cabin`.
- **Parameters:**
  - A mandatory stone base course (1–1.5 m) on old-core buildings.
  - Colour by era: grey stone, then white stucco, then raw brick, then saturated cholet.
  - Colonial fronts with 1–2 box balconies.
  - Cholets narrow and tall, symmetrical, with fully saturated paint.
  - The self-built zone is irregular boxes, 1 per plot, with every storey a different brick tone and rebar on top.
