# R3: Iberian white towns (Andalusian *pueblos blancos*, Toledo, Cuenca)

**Island culture:** a whitewashed Moorish-Christian hill town. Narrow lanes twist for shade under covered passages (*cobertizos*). Each house turns inward to a flower-filled patio behind iron grilles (*rejas*). Brick Mudéjar towers rise over tile roofs, and timber houses hang over the gorge on the rim (Cuenca). The mark is the inward-facing house: blank white street walls broken only by grilled windows, flower pots and the glimpse of a tiled patio.

## Examples
- *Pueblos blancos* (Vejer, Arcos, Frigiliana):
  - Lime whitewash (*cal*), said to date from the Moorish period, keeps the interiors cool.
  - Vejer is a labyrinth of narrow alleys, arches, patios and steep steps with tight turns for shade.
  - Arcos is a semicircle on a cliff top.
  - Frigiliana has cobbled lanes with flower pots and tiles.
  - Sources: [Wikipedia](https://www.wikipedia.com/wiki/Pueblo_blanco), [tourtailors](https://blog.tourtailors.com/a-tale-of-timeless-beauty-the-allure-of-spains-pueblos-blancos), [islands.com](https://www.islands.com/1816274/prettiest-village-andalusia-whitewashed-spanish-town-frigiliana-perchced-cliff-over-sea/)
- Toledo: a maze of narrow, winding lanes and staircases. In Mudéjar work, brick is both structure and decoration (Visigothic plus Islamic plus Christian). Bécquer describes a massive flat, dark arch giving a covered passage over a street. [archnet](https://www.archnet.org/sites/180), [UNESCO](https://whc.unesco.org/document/163275), [albalearning (Bécquer)](https://albalearning.com/Capitulo.aspx?id=7876)
- Cuenca, the *Casas Colgadas*: on the Huécar gorge. Heavy beams anchored in the cliff rock carry timber balconies and rooms over the drop. Proven by the 15th century and added to until the 18th; only three remain. [amusingplanet](https://www.amusingplanet.com/2017/06/the-hanging-houses-of-cuenca.html), [theculturetrip](https://www.theculturetrip.com/europe/spain/articles/heres-why-you-need-to-visit-the-amazing-hanging-houses-of-cuenca-spain-at-least-once)

## Generator grammar
- **Cell:** 4–5 m, storeys 3.2 m, 2–3 storeys (4–5 on the cliff rim). Patios 4×4 to 8×8 m.
- **Walls:** 0.5–0.7 m rubble or rammed earth, lime-washed. Toledo-style Mudéjar brick (`#a8603e`) with stone-and-brick banding (*aparejo toledano*).
  - Palette: whitewash `#f6f3ea`, ochre bands at the base (zócalo) `#d8a85a` or blue `#2f5f9a`.
  - Reja black `#1d1d1d`; doors oxblood `#6b2a24` or green `#2f5a3a`; tile roof `#b5643a`.
  - Cuenca timber `#7a5434` with blue or ochre fronts `#3d6fa6`, `#d0a04a`.
  - Weathering: dirt splash at the base (hence the painted zócalo), soft shadows.
- **Mass:** introverted courtyard houses packed into irregular blocks. Walls go straight up from the street, with few openings. The house is reached through a *zaguán* (entrance passage) to the patio. Cliff rim: cantilevered timber rooms on beams (Cuenca).
- **Streets:**
  - 1.5–3.5 m lanes curving constantly (one bend per 10–20 m) and climbing in ramps.
  - *Cobertizos* (rooms bridging a lane) 4–12 m long.
  - Cobbles with pebble mosaics (*empedrado*).
  - Awnings (*toldos*) stretched across shopping lanes in summer.
- **Growth:**
  - Layer 0: Roman and Moorish walls, cisterns and *aljibes*.
  - Layer 1: Moorish courtyard houses and lanes.
  - Layer 2: Mudéjar churches with brick towers.
  - Layer 3: baroque palaces.
  - Layer 4: cyberpunk.
- **Openings:**
  - Windows with projecting box *rejas* (iron grilles standing 0.3 m out, with pot shelves), 0.8×1.4 m.
  - Doors with stone or painted surrounds, iron-studded.
  - A *mirador* (a glazed balcony) on the upper floor.
  - Horseshoe arches inside the patios.
- **Roofs:** low Roman-tile roofs (`#b5643a`) at 15–20°, roof terraces (*azoteas*), chimneys with little hoods.
- **Ornament:** tiled door frames, house-name tiles, Mudéjar brick lozenge panels (*sebka*) on towers, wall-mounted pots (blue pots on white walls, the Córdoba patio).
- **Public space:**
  - The *plaza mayor* (an arcaded square) with a fountain and orange trees.
  - A church square at the summit.
  - A *mirador* terrace over the cliff.
  - A public patio garden with a pond.
- **Water:** the patio fountain and pool, *aljibe* cisterns, a pond in the plaza, an irrigation rill (*acequia*).

## Street hierarchy
- **Main street (*calle Real*):** 6–8 m, from the gate to the plaza mayor.
- **Lanes:** 2–3.5 m.
- **Cobertizo passages:** under bridging rooms.
- **Steps and ramps (*cuestas*).**
- **Squares:** the plaza mayor (30×40 m, arcaded), small *plazuelas* at junctions.

## Plants
- Seville orange trees (bitter orange) in rows in the plazas (5 m, round, fruit `#f28c28`).
- Blue pots of red geraniums on the walls (`#d1323b`).
- Bougainvillea, jasmine and *dama de noche*.
- Cypress pairs at the church.
- Date palms in the patios.
- Olive trees on the outskirts.
- Grapevine trellises (*parras*) over the patios.
- Ivy on the Mudéjar towers.

## Cyberpunk overlay
- Rejas as LED grilles with screens behind them.
- Patios roofed with ETFE domes and hydroponic walls.
- Cobertizos turned into data bridges, glazed and glowing.
- Mudéjar brick patterns lit in pulsing lines (sebka circuits).
- Solar-film toldos over the lanes, glowing at night.
- **Night:** the white walls go blue-grey. Pools of warm light at each reja (`#ffcf86`). The patios glow from inside, seen through the zaguán. The plaza is lit by iron lanterns in the orange trees.

## Kit
- **Shared pieces:**
  - `reja_grille` (main), `arch_horseshoe`, `arch_pointed`, `door_studded`, `window_small`, `shutters`, `galeria_glazed` (mirador)
  - `patio_gallery`, `fountain_kiosk`, `covered_alley` and `sabat_bridge` (cobertizo), `planter_wall`, `brick_relief_panel`
  - `glazed_inlay_band`, `bell_tower`, `barrel_tile_eave`, `chimney_stack`, `awning`, `hanging_backshop` (Cuenca), `cantilever_beam`
  - `lantern_wall`, `arcade_pier`
- **Unique pieces:**
  - `zocalo_band`: a painted dado decal.
  - `pot_bracket_wall`: a row of blue pots on hooks.
  - `sebka_brick_panel`: a Mudéjar lozenge lattice.
  - `casa_colgada_balcony`: a long timber gallery on cliff beams.
  - `patio_pool_tiled`.
- **Parameters:**
  - Window to wall 10–15% on the street, 40% on the patio.
  - Walls 98% white, accents on door, reja and zócalo only.
  - Blocks are courtyard-hollow: every house has a 15–25% patio.
  - Lanes bend continually, block edges jog 0.5–1.5 m.
  - Rooftops are terraced, with chimney hoods.
