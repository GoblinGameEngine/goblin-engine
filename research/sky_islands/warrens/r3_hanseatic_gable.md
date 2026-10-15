# R3: Hanseatic gable towns (Amsterdam, Tallinn, Bergen's Bryggen, Copenhagen's Nyhavn)

**Island culture:** a merchant town of tall, narrow brick and timber houses lined up gable-end to the water. Hoist beams jut from every gable to lift goods into attic warehouses, and some facades lean forward on purpose. The town is cut by canals and wharves. Bryggen's timber rows are split by narrow plank passages with galleries. The mark is the gable rhythm: stepped, neck, bell and spout gables in a row, each house a different colour, reflected in a canal.

## Examples
- Amsterdam:
  - Hoist beams lift goods through big windows because the stairs are too steep and narrow; many canal houses doubled as small warehouses.
  - A deliberate forward lean of a few centimetres stops goods scraping the facade; other tilts come from rotting piles.
  - Narrow frontages taxed less; wider double-fronted merchant houses from the 17th century, with attics and cellars for goods brought by boat.
  - Sources: [dutchreview](https://dutchreview.com/cities/amsterdam/amsterdam-canal-houses/), [amsterdamian](https://amsterdamian.com/see/amsterdam/why-dutch-houses-have-those-hooks-on-the-facades/), [forgottengalicia](https://forgottengalicia.com/hoisting-beams-amsterdam/), [thetravelbunny](https://thetravelbunny.com/canal-leaning-houses-amsterdam/)
- Tallinn:
  - Gothic merchant houses with granaries, hoist beams and cargo hatches (Vene 17).
  - Peppersack (1370) with its high gable and hoist beam; the Great Guild Hall (1417); stepped-gable merchant houses (Hopner House).
  - The *diele-dornse* plan: a front business hall, living space behind.
  - Sources: [asergeev](https://www.asergeev.com/pictures/k/Trade_building.htm), [asergeev rows](https://www.asergeev.com/pictures/k/Rows_of_houses.htm)
- Bergen, Bryggen:
  - Rows (*gård*) 2–3 storeys with gables to the harbour, on one or both sides of narrow passages that act as private courts.
  - Log construction, with galleries on a post-and-beam frame clad in horizontal boards. Fireproof stone storerooms at the back. A crane for each building.
  - Rebuilt after every fire on the same plan; about 62 buildings survive.
  - Sources: [UNESCO](https://whc.unesco.org/en/list/59), [Riksantikvaren](https://riksantikvaren.no/en/world-heritage/bryggen-in-bergen/)
- Copenhagen, Nyhavn: a 1670s canal. Brightly coloured 17th–18th-century townhouses in reds, yellows and blues, in timber, brick and plaster; the oldest is No. 9 (1681). [Wikipedia](https://en.wikipedia.org/wiki/Nyhavn), [alle.travel](https://alle.travel/en/copenhagen/pages/colourful-houses-of-copenhagen)

## Generator grammar
- **Cell:** frontages 4–8 m (a 6 m standard), depth 15–20 m, storeys 3.0–3.5 m, 4–6 storeys including a 2–3 storey gable attic. Bryggen: timber gables 2–3 storeys, plank passages 1.2–2 m.
- **Walls:**
  - Brick 0.35–0.5 m (Amsterdam dark `#4a2a20`, red `#8c3b2a`).
  - Limestone-plastered Gothic (Tallinn white `#ece6d6`, ochre `#d8b25a`).
  - Timber clapboard (Bryggen ochre `#d39b3a`, oxblood `#7a2a22`, white `#f0ebe0`).
  - Nyhavn plaster: red `#b2402e`, yellow `#e7b84a`, blue `#3f6fa8`, green `#4f7a52`.
  - Window frames white `#f5f3ee`, shutters dark green `#2a4a32`.
  - Weathering: soot and brick efflorescence, mossy wharves, a lean of 1–3 cm per storey.
- **Mass:** rows of narrow gabled houses packed side by side, each a full plot depth, with back yards (*hof*). Warehouse attics run the full length with hatches. Bryggen: parallel timber rows at right angles to the quay, with galleries facing the passage.
- **Streets:**
  - Canal streets with a quay on each side (each 6–8 m) plus the canal (12–25 m wide).
  - Humped bridges every 80–120 m.
  - Narrow alleys (*stegen*) 1–2 m between houses.
  - Bryggen's passages 1.5 m with plank decks.
  - Brick paving `#8a5a44`, quay edges of stone.
- **Growth:**
  - Layer 0: timber wharves, the Gothic guild hall and church.
  - Layer 1: Gothic brick merchant houses with stepped gables.
  - Layer 2: 17th-century Golden Age facades (neck and bell gables), raised storeys.
  - Layer 3: 19th-century cornice-top replacements and attic dormers.
  - Layer 4: cyberpunk.
- **Openings:**
  - Large windows (60% of the facade) in white frames, small-paned.
  - The attic hatch column (*luiken*) at the gable centre with a hoist beam above.
  - Ground floor: a trading hall door, raised over cellar steps (*stoep*).
- **Roofs:** steep gable roofs at 50–60° behind the gable fronts, in pantiles (`#5a3a2e` glazed dark) or slate. Dormers. Copper spires on churches and guild halls (`#4f8f78` verdigris).
- **Ornament:**
  - Gable types: stepped (`gable_step`), neck (`gable_neck`), bell (`gable_bell`), spout, cornice.
  - Sandstone scrolls, wall plaques (*gevelstenen*), iron tie-ends (anchors) shaped as dates and figures.
- **Public space:**
  - The market square (Raekoja plats) with a town hall and a tall spire.
  - Canal quays with trees and benches.
  - Guild halls.
  - The harbour wharf with cranes.
  - Small hidden courtyard gardens (*hofjes*: almshouse courts with a lawn).
- **Water:** canals everywhere (on the island, long ponds), the harbour basin, boats.

## Street hierarchy
- **Canal quays (main streets):** 6–8 m each side, with trees.
- **Market street:** 8–10 m from the harbour to the square.
- **Alleys and passages:** 1–2 m.
- **Bridges:** every 80–120 m.
- **Squares:** the market square (40×60 m), hofjes, the harbour wharf.

## Plants
- Elm and linden lines along the canals (15–20 m, regular spacing 8 m).
- Hollyhocks against the facades (`#d84a8a`).
- Geraniums and ivy in window boxes.
- Courtyard lawns with pear trees.
- Chestnuts in the squares.
- Bryggen: rowan and birch, moss on the roofs.
- Willows at the water.

## Cyberpunk overlay
- Hoist beams as cargo-drone docks with LED landing rings.
- Attic warehouses as data lofts.
- Gable silhouettes traced in neon (each gable type a different colour).
- Canal barges as floating markets and server boats.
- Bryggen galleries as stacked capsule hostels.
- Bike racks to the horizon, now e-bikes with charging glow.
- **Night:** rows of big warm windows reflected in the canals (doubling the light). Bridge arches lit with bulb strings (`#ffd08a`). Gable outlines in coloured neon. Fog over the water.

## Kit
- **Shared pieces:**
  - Gables: `gable_step`, `gable_neck`, `gable_bell` (all main), `gable_cornice`.
  - Hoisting: `hoist_beam` (main), `loading_door`, `crane_gable`.
  - Facade: `french_window`, `shutters`, `dormer_row`, `chimney_stack`, `clapboard_panel`, `cornice`.
  - Bryggen and waterside: `gallery_timber`, `plank_bridge`, `plank_landing`.
  - Other: `bell_tower`, `lantern_wall`, `lights_festoon`.
- **Unique pieces:**
  - `luiken_hatch_column`: stacked attic shutters.
  - `gevelsteen_plaque`.
  - `humped_canal_bridge`: brick, bulb-lined.
  - `wall_anchor_iron`.
  - `bryggen_row_passage`: two timber rows facing a plank passage with galleries.
  - `canal_edge`: a stone quay with mooring rings.
- **Parameters:**
  - Very narrow frontage (4–8 m), height to width 3:1.
  - A gable on every house, its type changing for each house.
  - Window to wall 50–65%.
  - A forward lean of 0.5° on 30% of houses.
  - One strong colour per house in Nyhavn and Bryggen; brick in Amsterdam.
  - Canals as the backbone: a ribbon of water every 120–200 m.
