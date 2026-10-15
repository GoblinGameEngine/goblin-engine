# R3: Knights' harbour cities (Valletta, Dubrovnik, Malta's towns)

**Island culture:** a planned fortress city of honey limestone on a steep peninsula. A rigid grid of streets is so steep that many become stairs. Houses are tall and flat-roofed, and every corner and upper storey carries a coloured, enclosed wooden balcony (the *gallarija*). A polished limestone main street runs between gates (Dubrovnik's Stradun). The mark is the stone grid made vivid by stacked, painted timber balconies over pale, polished limestone.

## Examples
- Malta, the *gallarija*: an enclosed timber balcony descended from the Maltese *muxrabija* and related to the mashrabiya. Widespread from the 17th century; an early one rounds the Old Theatre Street corner of the Grandmaster's Palace (about 1675), and a 1657 permit asks for "a balcony of three saliature".
  - It rests on carved stone corbels (*saljaturi*) and has hinged glass flaps (*purtelli*) and blinds (*tendini*).
  - The Knights required sculptural ornament on corners, so wrap-around balconies met that rule.
  - Painted in bold colours to match the door below; bright emerald green is common.
  - Sources: [Wikipedia](https://en.wikipedia.org/wiki/Gallarija), [culture-malta](https://culture-malta.org/mysteries-of-the-maltese-gallarija/), [pilgrimaps](https://www.pilgrimaps.com/the-maltese-balconies-sanctuaries-of-secrets-and-whispers/), [guidememalta](https://www.guidememalta.com/en/maltese-architectural-icons-wooden-balconies)
- Dubrovnik:
  - Stradun is limestone-paved (commonly dated 1468) and 300 m long, between the Pile and Ploče gates.
  - After the 1667 earthquake the Republic regulated uniform two-storey buildings, with shops below, homes above and green shutters.
  - Red-tile roofs; narrow, stepped side streets climb at right angles.
  - Sources: [absolute-croatia](https://www.absolute-croatia.com/dubrovnik/attractions/stradun), [worldatlas](https://www.worldatlas.com/cities/8-croatia-towns-with-unforgettable-main-streets.html)

## Generator grammar
- **Cell:** a 5×5 m bay. Storeys are 4.0 m at the ground floor and 3.6 m above, 3–5 storeys. Streets run on a strict grid, 18–22 m between parallel streets.
- **Walls:** 0.7–1.0 m Globigerina limestone ashlar, honey coloured.
  - Palette: `#d9b77a` honey, `#e8d3a6` pale, `#b8925a` weathered; Dubrovnik limestone `#e6dfd0`; terracotta roof `#b24a2c`.
  - Balcony colours: emerald `#1f7a4c`, oxblood `#7d1f24`, navy `#1f3557`, ochre `#c9932f`, turquoise `#2f8f8a`.
  - Weathering: limestone soft-eroded at street level (the salt), honeycomb pitting `#a88a57`.
- **Mass:** continuous terraced frontages along the grid. Blocks are 18–22 m deep around small light wells. Gates and bastions sit at the edges (the island rim is the bastion wall).
- **Streets:** a straight grid running along and across the slope. Cross-slope streets turn into long stairs: shallow risers (0.10–0.12 m) and deep treads (0.6–0.8 m), so knights in armour could climb them. Main streets are 6–8 m, side streets 3–5 m. A polished limestone main street (Stradun) is 12 m wide.
- **Growth:**
  - Layer 0: bastion walls and cisterns.
  - Layer 1: 16th–17th-century grid palazzi with corner statues.
  - Layer 2: 18th–19th-century gallarija on every upper storey, closed-in loggias.
  - Layer 3: rooftop penthouses set back.
  - Layer 4: cyberpunk.
- **Openings:**
  - The gallarija: 1.0–1.4 m deep, 2.5–5 m wide, often 2–3 stacked per facade. Some wrap the corner.
  - Ground-floor shop doors with arched fanlights.
  - Green louvred shutters (Dubrovnik).
  - Large door knockers.
- **Roofs:** flat stone roofs (Valletta) with low parapets and roof terraces; Dubrovnik's red Roman-tile hip roofs.
- **Ornament:** corner niches with statues, carved corbels, baroque door surrounds, the corner balcony wrap.
- **Public space:**
  - The main street with café terraces.
  - Grid squares in front of churches and auberges.
  - Bastion gardens on the walls (Upper Barrakka style: an arcaded terrace garden).
- **Water:** the harbour, fountains, cisterns, a pond in the bastion garden.

## Street hierarchy
- **Main street (Stradun or Republic Street):** 10–12 m, polished stone, no stairs, along the ridge.
- **Grid streets:** 4–8 m.
- **Stair streets:** 3–5 m, about 1:5 slope in shallow steps.
- **Squares:** in front of each church; bastion gardens at the rim.

## Plants
- Bougainvillea on the bastions.
- Oleander and hibiscus in planters.
- Citrus trees (orange) in the bastion gardens.
- Aleppo pine and date palm in the squares.
- Geraniums on the gallarija sills.
- Carob trees.
- Agave on the walls.

## Cyberpunk overlay
- Gallarija retrofitted as screen boxes: LCD panes in the purtelli, each balcony a different glowing colour.
- Corner statues as hologram saints.
- Fibre trunks run along the cornices.
- Shutters with e-ink slats.
- Bastions hold drone landing pads and big dish arrays.
- **Night:** the stone glows amber under sodium uplights (`#ffb062`). Balconies are lit lanterns of colour from inside. The polished main-street paving reflects everything like water: a mirror strip (roughness 0.15).

## Kit
- **Shared pieces:**
  - `bay_window_box` (as the gallarija base), `galeria_glazed`, `balcony_timber_covered`, `bracket_corbel`
  - `shutters`, `louvre`, `window_arched`, `door_studded`, `gate_portal`, `cornice`, `wall_shrine` (corner niche)
  - `terrace_parapet`, `parapet_crenel` (bastion), `round_tower`, `stone_slab_roof`, `barrel_tile_eave`, `beam_steps`
- **Unique pieces:**
  - `gallarija`: an enclosed balcony box with a panelled base, glazed purtelli, a cornice, and corner-wrap and stacked variants.
  - `corner_statue_niche`.
  - `bastion_wall_slope`: a battered rim wall with an embrasure.
  - `knight_stair`: low, deep risers.
- **Parameters:**
  - A strictly orthogonal grid; facades flat and symmetrical.
  - A gallarija on 40–70% of upper bays, each painted in a strong single colour.
  - Honey stone everywhere, and almost no render.
  - Ground-floor openings arched; upper openings rectangular, 1.1×2.4 m.
