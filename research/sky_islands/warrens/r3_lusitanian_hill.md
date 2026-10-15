# R3: Lusitanian hill towns (Lisbon's Alfama and Mouraria, Porto's Ribeira)

**Island culture:** a city tumbling down a steep hill to the water, with a Moorish-age tangle of lanes (*becos*) and stair streets (*escadinhas*). Narrow, tall houses wear 19th-century tiles: whole facades of blue, green and yellow *azulejos*. Iron balconies hang over the lanes, and laundry crosses them. Iron-railed lookouts (*miradouros*) sit at every bend, and trams grind uphill. The mark is the tiled facade: a pattern repeated on every surface, with a gloss that catches the light.

## Examples
- Alfama: medieval, and it survived the 1755 earthquake, so it keeps the 12th–14th-century maze of narrow alleys, blind corners and stairs.
  - The layout was shaped by terrain, not a plan, and reads "more North African than Western European".
  - Lanes are called *becos* and *travessas*. Whitewashed houses, azulejo facades, iron-railed *miradouros*.
  - Sources: [lisbontourism](https://www.lisbontourism.org/alfama-lisbon-guide/), [viatravelers](https://viatravelers.com/neighborhoods/alfama-lisbon/), [thetraveler](https://www.thetraveler.org/alfama-old-town-guide-history-alleys-and-landmarks/)
- Facade azulejos: mid-to-late 1800s tiles covering thousands of buildings.
  - In the old quarters the patterns lean to blues, greens and grey, sometimes beige or red. Also yellow, beige, white, green and blue.
  - Example: the Santa Clara building (1860) in blue, yellow and white. The Viúva Lamego factory in Mouraria has figure murals.
  - Sources: [lisbonlux](https://www.lisbonlux.com/magazine/the-10-most-beautifully-tiled-facades-in-lisbon), [visitlisboa](https://visitlisboa.com/en/places/lisbon-s-azulejos), [LNEC decay study](https://repositorio.lnec.pt/jspui/handle/123456789/1007961)
- Porto, Ribeira: UNESCO 1996. Pastel townhouses with azulejos and a granite quay.
  - "The slope is covered with houses, the houses draw streets ... granite on granite" (Saramago).
  - Rabelo boats moored along the bank.
  - Sources: [viatravelers](https://viatravelers.com/neighborhoods/ribeiraporto/), [Livraria Lello](https://fundacaolivrarialello.pt/en/ribeira-and-port-cellars), [ontheluce](https://www.ontheluce.com/getting-lost-in-portos-old-town/)

## Generator grammar
- **Cell:** narrow plots 4–6 m wide, 10–15 m deep, storeys 3.0–3.3 m, 3–5 storeys. Porto is tall and thin, 1–2 windows per floor.
- **Walls:** 0.5–0.7 m rubble masonry or granite, rendered; facades often tiled in full (Porto: granite frames at doors, windows and corners `#9a958c`).
  - Render: pastel yellow `#e9cd6e`, pink `#e3a6a0`, ochre `#c78b45`, white `#f2efe6`.
  - Tile fields: cobalt `#1f4e9c` on white, green `#2e7d5b`, mustard `#d4a72c`, grey `#7d8b95`.
  - Roofs: Roman tile `#b8603d`.
  - Weathering: missing tiles in patches (show render or brick), green damp at the base, rust streaks from the balconies.
- **Mass:** tight terraces of tall narrow houses following the contours, stepping a full storey down the slope. Block depth varies, with tiny back yards. On the main stair-streets, houses lean and corbel slightly forward.
- **Streets:**
  - *Becos* 1.2–2.5 m, bending, with dead ends.
  - *Escadinhas* (stairs) 2–3 m, with iron handrails up the middle.
  - Tram streets 5–7 m, with rails following the contour.
  - Paving: *calçada portuguesa*, black and white limestone mosaic patterns (`#f0ede4` on `#2b2b2b`).
- **Growth:**
  - Layer 0: Moorish wall fragments and arches.
  - Layer 1: medieval houses.
  - Layer 2: 18th–19th-century raised storeys with tiled facades and iron balconies.
  - Layer 3: 20th-century attic additions in tin, and rooftop terraces.
  - Layer 4: cyberpunk.
- **Openings:** tall windows (0.9×2.2 m) with wrought-iron balcony cages 0.3–0.6 m deep. Ground-floor shop doors are arched. Porto has stacked full-height window columns.
- **Roofs:** tile pitch 20–25°, with small dormers and mansard attics (*águas-furtadas*) and chimney pots.
- **Ornament:** azulejo fields with tile borders, saints panels over doors, iron balcony scrolls, granite frames.
- **Public space:**
  - *Miradouros* (lookout terraces with railings, benches and a kiosk).
  - The *largo* at a fountain.
  - The riverside quay (*cais*).
  - Fado-tavern lanes.
- **Water:** a river quay with moored boats (a canal or pond at the foot), stone fountains (*chafarizes*).

## Street hierarchy
- **Tram avenue (main street):** 6–8 m, switching back up the hill.
- **Quay boulevard:** 15 m along the water.
- **Becos:** 1.5–2.5 m.
- **Escadinhas:** 2–3 m.
- **Squares:** a largo at each tram bend, a miradouro at every ridge turn.

## Plants
- Jacaranda: violet canopy `#8d6cc8`, 10 m (a Lisbon street tree).
- Bougainvillea.
- Lemon and orange trees in back yards.
- Geraniums in tin pots on every balcony.
- Basil pots (for Santo António).
- Strelitzia.
- Washingtonia palms at the miradouros.
- Vines over the yard pergolas.

## Cyberpunk overlay
- Azulejo LED: tile-sized pixels making whole facades into slow video murals.
- Retrofitted trams as autonomous funicular pods.
- Iron balconies hung with AC units and coolant lines.
- Fado bars with holographic singers.
- Rooftop terraces with micro-wind turbines.
- **Night:** glazed tiles pick up reflected neon (high specular). The calçada mosaics glow under warm lanterns (`#ffd08a`). Miradouros are lit outlines.

## Kit
- **Shared pieces:**
  - `tile_panel` (main: facade fields), `glazed_inlay_band`, `balcony_iron`, `french_window`, `window_arched`
  - `shutters`, `dormer_row`, `dormer_bump`, `barrel_tile_eave`, `chimney_stack`, `stair_external_steep`, `beam_steps`
  - `terrace_rail` (miradouro), `fountain_kiosk`, `lantern_wall`, `laundry_line`, `wall_shrine`, `funicular`
- **Unique pieces:**
  - `azulejo_facade_field`: tileable patterns as a texture atlas.
  - `granite_window_frame`: a Porto cut-stone surround.
  - `calcada_mosaic`: a ground decal with waves and stars.
  - `tram_rail`: a ground decal plus wire posts.
  - `miradouro_kiosk`.
- **Parameters:**
  - Tall, narrow fronts (width 4–6 m, height-to-width 3:1).
  - Tiled walls with gloss (roughness 0.25) against matte render (0.9).
  - Every upper window gets a shallow iron balcony.
  - A colour change for each house, alternating tiled and rendered.
  - Houses step down a full storey every 1–2 plots.
