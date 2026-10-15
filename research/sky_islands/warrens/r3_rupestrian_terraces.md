# R3: Rupestrian terraces (Matera's Sassi, Amalfi, Positano)

**Island culture:** a city carved into and stacked down its own rock. Each house's roof is the street of the row above. Rooms are excavated into the cliff and closed by a built facade, and barrel vaults run everywhere. On the sea side, the town is a pyramid of white and pastel cubes with vaulted roofs and vine pergolas, terraced into lemon gardens. The mark is the inverted amphitheatre: the city descends in steps toward a ravine, and the paths run on the roofs.

## Examples
- Matera, the Sassi: dwellings dug into calcarenite (locally called *tufo*), soft to cut and hardening in air. The excavated stone built the front wall that closes each cave, the "cave-house". The houses descend in steps toward the Gravina ravine like theatre seating, and on the steep slope the streets run across the roofs of the houses below. UNESCO 1993. [Wikipedia](https://wikipedia.com/wiki/Sassi), [sassidimatera.it](https://sassidimatera.it/en/the-sassi-of-matera/)
- Amalfi vernacular: rough stone bound in lime and pozzolan, rendered with crushed-stone plaster so it matches the rock. Built against the cliff for labour and earthquake safety. Dry-stone terrace walls hold the gardens, with vaulted rooms (*revote*) built into the terrace walls. Flat or vaulted roofs carry a vine pergola for shade and airflow. Cisterns are cut into the rock. [UNESCO Amalfi Coast](https://www.unescoamalficoast.it/preserve-your-territory/the-characteristics-of-vernacular-architecture/?lang=en), [iris.unipa](https://iris.unipa.it/handle/10447/699525)
- Positano: a "pyramid of houses" of vaulted roofs, a Byzantine-derived tradition. [domusweb](https://domusweb.it/en/design/gallery/2021/08/02/proporzione-mediterranea-design-of-the-tradition.html)

## Generator grammar
- **Cell:** 4×6 m vault cells (span 3.5–4.5 m), storeys 3.0–3.6 m. Each terrace step is 1–2 cells deep.
- **Walls:** calcarenite blocks 0.5–0.8 m thick (Matera) or rubble with lime render.
  - Palette: Matera stone honey `#cbb48b`, sun-bleached `#e2d6bb`, shadow `#8a7a5c`; Amalfi whitewash `#f3eee2`, pastel peach `#efc9a4`, pale yellow `#f2dc8e`, sea-blue door `#2f6f8f`.
  - Weathering: lichen and dark stains at the cave mouths, soot over the old hearths.
- **Mass:** the whole island face is a terraced slope. Rows of cells are cut into the hill, each row's roof becoming the lane of the row above. Vault fronts are closed by a built wall with a door and a lunette window. Several rows step back and up, with stair ramps between them. A *vicinato* (shared court) groups 4–8 dwellings around a cistern.
- **Streets:** contour lanes 1.5–3 m wide on the roofs. Steep stair lanes go straight downhill (*gradinate*), 1.2–2.5 m wide. There are arched tunnels under the houses, and no vehicles.
- **Growth:**
  - Layer 0: caves and rock cisterns, with ancient churches cut into the rock (*chiese rupestri*).
  - Layer 1: built vault fronts and lamione rooms.
  - Layer 2: baroque palazzi on the rim, bell towers.
  - Layer 3: whitewashed vault houses with pergolas (Amalfi).
  - Layer 4: cyberpunk vault capsules bolted onto the rock.
- **Openings:** a deep arched door (1.0×2.2 m), a lunette fanlight over it, small square windows. The wall depth is shown: reveals 0.5 m or more.
- **Roofs:** barrel or cross vaults showing as rounded humps (*a botte* and *a schifo*), whitewashed. Pergolas of timber posts and wires on flat parts.
- **Ornament:** minimal. Carved door lintels, a bell gable, painted majolica house numbers.
- **Public space:**
  - A belvedere platform at each turn of the stair.
  - The cathedral piazza on the crest.
  - Cistern courts.
  - Lemon-garden terraces (green public steps).
- **Water:** rock-cut cisterns and runnels, and a pond at the foot (the ravine pool).

## Street hierarchy
- **Crest promenade (main street):** 6–8 m, paved, along the top rim.
- **Contour roof-lanes:** 2–3 m.
- **Gradinate:** stairs 1.5–2.5 m.
- **Plazas:** a belvedere every 40–60 m of descent, and the vicinato courts.

## Plants
- Lemon groves on terraces under dark-green pergolas (3 m, fruit `#f2d33c`).
- Grape vines over the roof pergolas.
- Bougainvillea and wisteria (`#9b7bd0`) on the facades.
- Carob and almond on the rocky slopes.
- Prickly pear and capers growing out of walls.
- Rosemary hedges.
- Cypress on the crest.

## Cyberpunk overlay
- Capsule vaults: composite pods socketed into new cuts in the rock face.
- Funicular and inclined lifts running down the stair lines, with LED strip rails.
- Server rooms in the deep caves, venting steam from the cave mouths.
- Holo-projection on the cliff (a vast fresco of saints and adverts).
- Solar film on the pergolas.
- **Night:** a starfield of small warm windows (`#ffcf7a`) over the whole slope, with stair handrails traced in cool LED (`#7fd8ff`). Cave mouths glow orange from inside.

## Kit
- **Shared pieces:**
  - `vault_cell`, `ghorfa_vault` (as a barrel-vault cell)
  - `arch_opening`, `door_room`, `qamariya_fanlight` (as a lunette), `window_small`
  - `stair_cut`, `stair_external_steep`, `beam_steps`, `tunnel_portal`
  - `terrace_parapet`, `terrace_rail`, `timber_pergola` (as a roof pergola), `planter_wall`
  - `bell_tower`, `funicular`, `light_shaft`, `water_channel`
- **Unique pieces:**
  - `rock_face_cut`: a carved cave mouth with a rough rock surround.
  - `vault_roof_hump`: an exposed whitewashed barrel or cross vault extrados.
  - `cistern_well`: a stone well head with a pulley.
  - `lemon_pergola`: posts and wires with a leaf canopy.
- **Parameters:**
  - Every roof is a walkable lane: parapet 0.6 m, roof stairs drawn from them.
  - Deep reveals of 0.5–0.8 m; wall to opening 85%.
  - Low, broad cells; no building above 4 storeys at any point on the slope.
  - Colour: stone-matched render (Matera) or whitewash and pastel (coast). The facades are smooth and soft-cornered, with corner radius 0.1–0.2 m.
