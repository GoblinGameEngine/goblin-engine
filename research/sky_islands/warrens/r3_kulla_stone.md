# R3: Balkan stone tower-houses (Gjirokastër, Mostar)

**Island culture:** a grey stone town clinging to a mountain slope below a fortress. Tall fortified tower-houses (*kulla*) have blank stone bases for storage and feud defence, and an upper storey that bursts out on stone corbels with wide windows and timber. They are capped by heavy roofs of stone slabs (*rrasa*) that make the town look scaled like a dragon. The mark is the stone-slab roofscape and the fortress-base, open-top house.

## Examples
- Gjirokastër:
  - Natural stone blocks and large limestone roof slates make the distinctive look.
  - Stone-slab roofs in Gjirokastër, against tiles in Berat.
  - Over 500 historic buildings. Tower-houses built by landowners for clan feuds; the stone lower parts are fortress and storehouse.
  - Typically 3–4 storeys: ground floor for animals and storage, thick walls and minimal windows below.
  - Upper floors expand outward on stone corbels, with larger windows and sometimes timber balconies; opulent upper rooms show status.
  - Mostly 17th–19th century. UNESCO 2005.
  - Sources: [Wikipedia: tower houses in the Balkans](https://en.wikipedia.org/wiki/Tower_houses_in_the_Balkans), [gjirokastra.org](https://gjirokastra.org/gjirokastra/architecture/), [UNESCO doc](https://whc.unesco.org/document/153783), [odessia](https://odessia.com/destinations/albania/gjirokaster)
- Mostar: stone roofs on Kujundžiluk, Ottoman residential clusters (Bišćević and Kajtaz houses), "roofing slate". [MIT DOME](https://dome.mit.edu/handle/1721.3/64980?show=full), [viatravelers](https://viatravelers.com/neighborhoods/old-town-mostar/)

## Generator grammar
- **Cell:** 6×8 m house footprints, storeys 3.2–3.6 m, 3–4 storeys. The top storey corbels out 0.5–0.9 m.
- **Walls:**
  - Grey limestone rubble 0.9–1.2 m at the base, thinning upward.
  - The upper storey is stone or lime-plastered timber frame (`#ece6d8`).
  - Palette: grey stone `#8f8b84`, light grey `#b3aea5`, dark joints `#55524c`; plaster white `#ece6d8`; timber `#6a4b33`; the roof slab mosaic `#76736d` to `#9a968e` (each slab a different shade).
  - Weathering: black lichen on the roofs, white lime streaks.
- **Mass:** detached tall houses on terraced plots along switchback lanes. Each house is an almost cube-shaped stone block. Courtyard walls carry the gates. A castle crowns the ridge.
- **Streets:**
  - Steep, cobbled switchbacks 2–4 m wide with a stone gutter down the middle.
  - Stone stairs.
  - Bazaar streets (*pazar*) with stone-arched shop cells.
  - Bridges over gorges (Mostar's arch).
- **Growth:**
  - Layer 0: the fortress (citadel walls).
  - Layer 1: early kulla.
  - Layer 2: Ottoman mansions with corbelled tops and painted rooms.
  - Layer 3: Communist-era blocks (sparse).
  - Layer 4: cyberpunk.
- **Openings:**
  - Base: arrow slits and tiny windows (0.3×0.6 m) and an iron-studded door.
  - Top floor: a continuous band of windows with timber frames and shutters (window to wall 50%).
  - A gun loophole box (*mashikull*, a projecting machicolation).
- **Roofs:** steep hip roofs at 30–35° of overlapping stone slabs, very heavy, with deep eaves of timber rafters. Chimneys are stone stacks with slab hats.
- **Ornament:** sparse outside (a decorated chimney, carved door lintel); rich painted interiors.
- **Public space:**
  - The bazaar crossroads (Qafa e Pazarit).
  - Mosque yards.
  - Fortress terraces.
  - Viewpoints.
- **Water:** stone fountains, cisterns in the castle, a pond below the bridge.

## Street hierarchy
- **Bazaar street (main):** 5–6 m, cobbled with white-stone patterns.
- **Switchback lanes:** 2–4 m.
- **Stairs:** 1.5–2 m.
- **Squares:** the bazaar crossroads, the castle forecourt.

## Plants
- Holm oak and Mediterranean cypress.
- Figs, walnuts and mulberries in the yards.
- Grapevines over the courtyard gates.
- Pomegranate.
- Lavender and sage on the walls.
- Plane trees at the fountains.
- Mountain grasses on the castle slope.

## Cyberpunk overlay
- Kulla bases as armoured server vaults (blast doors replacing the studded doors).
- Machicolation boxes as drone ports.
- Stone-slab roofs interleaved with solar slates, every fifth slab a dark-blue PV cell.
- Searchlights from the citadel.
- Zip-lines between towers.
- **Night:** dark stone bases with glowing top bands: rows of warm upper windows (`#ffc777`), like lanterns on stone pillars. The citadel is floodlit white.

## Kit
- **Shared pieces:**
  - `tower_square` (main), `stone_slab_roof` (main), `bracket_corbel`, `window_rank_row` (new: long ranked window band), `shutters`, `door_studded`, `gate_portal`
  - `chimney_stack`, `timber_eave`, `parapet_crenel`, `round_tower`, `fountain_kiosk`, `market_stall`, `souk_vault`, `stair_cut`, `window_small`
- **Unique pieces:**
  - `kulla_machicolation_box`.
  - `slab_roof_mosaic`: a heavy roof with per-slab shading.
  - `arrow_slit`.
  - `corbelled_top_storey`: a stone corbel course.
  - `stone_arch_bridge` (Mostar).
- **Parameters:**
  - Tall cube massing, height to width 1.5:1.
  - Openings grow with height (under 5% at the base, 50% at the top).
  - Everything grey stone and white plaster.
  - Roofs dominate the silhouette (eave depth 0.8 m, roof 30% of the height).
