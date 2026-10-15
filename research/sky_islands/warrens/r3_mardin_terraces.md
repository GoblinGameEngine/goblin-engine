# R3: Upper Mesopotamian stone terraces (Mardin, Midyat)

**Island culture:** a honey-to-pink limestone city cascading down a steep south slope. Every house's roof is the terrace of the house above, and every window looks out over the plain. Arched passages (*abbaras*) carry houses over the lanes for shade. South facades are carved in dense stone lace of tulips, grapes and geometry. Artuqid minarets and domes are cut from the same stone. The mark is the carved stone facade and the terrace cascade: one material, sculpted.

## Examples
- Mardin:
  - Local limestone ranging pink to yellow to creamy white, easy to carve (the Belsik quarry was exhausted in 1925, and similar beige stone comes from Midyat).
  - The houses sit on an inclined, terraced topography; the roof of one is the terrace of another, so every window views the Mesopotamian plain.
  - Late Ottoman mansions (mid-19th to early 20th century) carry exquisite stone carving on their south facades: tulips, grapes, geometry.
  - Abbaras are arched passages linking streets beneath houses, giving shade; the town was planned for summer shade.
  - Artuqid limestone architecture from the 1100s.
  - Sources: [ITU JFA article](https://www.az.itu.edu.tr/jfa/article/download/817/701/14293), [Columbia MCID](https://mcid.mcah.columbia.edu/mapping-mesopotamian-monuments/mardin), [flypgs](https://www.flypgs.com/en/blog/mardin-historic-culture/), [sailingstonetravel](https://sailingstonetravel.com/mardin-guide/)

## Generator grammar
- **Cell:** 4×5 m stone cross-vault or barrel bays, storeys 3.5–4.0 m (vaulted), 2–3 storeys per house. Each house steps back one full house depth up the slope.
- **Walls:** 0.7–1.0 m cut limestone ashlar, no render.
  - Palette: honey `#d8b77e`, pale cream `#eadcb8`, pinkish `#d9b39a`, carved-shadow `#9d8255`, window frames the same stone, doors and shutters turquoise `#2e8a86` or brown `#5b3a24`.
  - Weathering: warm patina darkening low, white salt efflorescence.
- **Mass:** courtyard houses (*avlu*) with an *eyvan* (an open vaulted hall facing the court) on the upper level, terraced in rows along the contours. Rows are linked vertically by stair lanes and abbaras. The roof terraces (flat, with parapets) of row N are the yards of row N+1.
- **Streets:**
  - Contour streets 3–5 m: the main bazaar street is the long contour.
  - Very steep stair lanes 1.5–2.5 m.
  - Abbaras: vaulted tunnels 2.5–3 m wide and 3–4 m high, some 10–30 m long, built under a house.
- **Growth:**
  - Layer 0: the citadel rock and rock-cut cisterns.
  - Layer 1: Artuqid madrasas, mosques and minarets (12th–15th century).
  - Layer 2: Ottoman courtyard houses with eyvans.
  - Layer 3: late-Ottoman carved mansions.
  - Layer 4: concrete storeys added on roofs.
  - Layer 5: cyberpunk.
- **Openings:**
  - Pointed and segmental arched windows in carved frames, with iron grilles.
  - Triple-arched loggias on the south faces.
  - Doors with a carved arch and a stone bench.
- **Roofs:** flat terraces with stone parapets (balustrade with carved panels), water spouts. Ribbed domes on mosques; square minarets with carved bands.
- **Ornament:** dense relief panels (tulip, grape, star), muqarnas hoods over portals, inscription bands, carved balustrades.
- **Public space:**
  - The contour bazaar street (*çarşı*) with covered sections.
  - Madrasa courtyards with pools.
  - Viewing terraces facing the plain.
  - Plane-tree squares.
- **Water:** cisterns, madrasa courtyard pools (rectangular, with a rill), a terrace pond.

## Street hierarchy
- **Bazaar contour street (main):** 5–7 m, paved, along mid-slope, partly vaulted.
- **Upper and lower contour streets:** 3–4 m.
- **Stair lanes:** 1.5–2.5 m.
- **Abbara tunnels.**
- **Squares:** a viewing terrace every ~80 m, madrasa courts.

## Plants
- Pomegranate (4 m, red fruit `#c2272d`).
- Fig, mulberry and walnut in the courtyards.
- Grape vines on terrace pergolas.
- Pistachio (Midyat).
- Oleander.
- Jasmine.
- Basil and roses in pots on the terraces.
- A few cypress and plane trees.
- Sparse: the slope is mostly stone.

## Cyberpunk overlay
- Carved panels inlaid with fibre-optic lines, so the tulip reliefs glow.
- Laser-cut stone screens.
- Abbaras as lit transit tubes and markets.
- Rooftop terraces as solar farms and holo-cinemas facing the plain.
- New storeys in sintered stone-printed blocks matching the honey colour.
- **Night:** the whole cascade glows honey under warm floodlight (`#ffbf6b`). Carved facades take raking light from below, which makes the relief vivid. Abbaras are lit tunnels of light in the hill.

## Kit
- **Shared pieces:**
  - `vault_cell`, `iwan_arch` (eyvan), `arch_pointed`, `window_arched`, `muqarnas_hood`, `carved_stucco_panel` (in stone)
  - `motif_relief_band`, `grille_geometric`, `terrace_parapet`, `parapet_screen`, `covered_alley` (abbara), `tunnel_portal`
  - `minaret_small`, `dome_ribbed`, `souk_vault`, `fountain_kiosk`, `water_channel`, `stair_cut`
- **Unique pieces:**
  - `carved_balustrade_stone`: pierced panels.
  - `abbara_vault`: a long barrel passage under a house.
  - `triple_arch_loggia`.
  - `artuqid_minaret_square`.
- **Parameters:**
  - One material for everything: limestone, with colour varying only ±8%.
  - The terrace cascade: each row 3–6 m higher than the one below and set back a full house.
  - Openings arched with carved frames.
  - South faces heavily ornamented, north faces blank.
  - Walls 0.8 m deep reveals.
