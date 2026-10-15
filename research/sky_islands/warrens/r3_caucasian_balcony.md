# R3: Caucasian balcony towns (Tbilisi's Kala, Abanotubani and Sololaki; Svaneti towers)

**Island culture:** a brick-and-timber city hung on cliffs over a river gorge. Houses wear deep carved wooden balconies, some glazed in stained glass (*shushabandi*). The balconies run the full width of the facade and stack 2–3 high, often over the cliff edge. Courtyards ("Italian courtyards", *italiuri ezo*) are ringed with shared galleries and spiral stairs. Persian-style brick domes of sulphur baths sit at the bottom. On the heights, Svan stone defence towers rise 20–25 m. The mark is the carved, layered timber balcony, and the tower skyline.

## Examples
- Tbilisi:
  - Kala, the old town: narrow winding streets, brightly painted multi-storey houses, ornate wooden balconies, stained glass over courtyards.
  - Sololaki: 19th-century townhouses with carved balconies, alleys into courtyards.
  - Abanotubani: houses with carved balconies "hanging precariously on cliffs", and the brick domes of Persian-style baths (17th century).
  - Metekhi church on its cliff above the Mtkvari. A blend of Georgian, Persian, Russian and Art Nouveau.
  - Sources: [inyourpocket](https://www.inyourpocket.com/georgia/tbilisi/venues/old-town), [National Geographic](https://www.nationalgeographic.com/travel/destinations/asia/georgia/partner-content-georgia-tbilisi-bohemian-city/), [caucasianhouse.ge](https://caucasianhouse.ge/?p=3331), [storiesbysoumya](https://www.storiesbysoumya.com/old-town-tbilisi/), [theabroadguide](https://theabroadguide.com/tbilisi-dive-into-the-past/)
- Svaneti, Ushguli:
  - Towers of 3–5 storeys, 20–25 m, of schist or slate rubble with lime, walls thinning and tapering upward, gabled slate roofs, machicolated tops.
  - Attached to a *machubi* (a family house of two storeys, 80–130 m², with a ground-floor hall shared with animals).
  - Ushguli's church and remnants of a 37-tower fortress.
  - Sources: [UNESCO doc](https://whc.unesco.org/document/154075), [theartbog](https://theartbog.com/stone-sentinels-the-architecture-of-svaneti/), [National Geographic](https://www.nationalgeographic.com/magazine/article/svanetia-georgia-caucasus-mountains)

## Generator grammar
- **Cell:** 4.5 m bays, storeys 3.4–4.0 m, 2–4 storeys. Balconies 1.5–2.5 m deep, running the full facade width. Svan towers 5×5 m in plan, 20–25 m tall.
- **Walls:**
  - Brick (thin Persian-style bricks `#a65a3a`, often limewashed), rubble on the cliffs, painted stucco on the townhouses.
  - Balconies in timber: turquoise `#3a9a9a`, sky blue `#6aa6cf`, olive `#7a8a4a`, natural brown `#6b4a2e`, white trim `#efe9dc`.
  - Stained glass: ruby `#b0283a`, amber `#e0a030`, cobalt `#2a4a9a`, green `#2a8a4a`.
  - Towers: grey schist `#6f6d68`.
  - Weathering: balconies sagging, paint flaking to silver timber, a leaning tilt of 1–3°.
- **Mass:**
  - Perimeter houses wrapping inner courtyards. The court is ringed by 2–3 levels of open timber galleries reached by external spiral and straight stairs, with laundry and vines.
  - On cliffs, houses project over the drop on timber posts.
  - Svan towers attach to low stone houses in clusters on the upper terraces.
- **Streets:** winding lanes 3–5 m, cobbled, climbing to the fortress; stairs. A river or gorge cuts through, crossed by bridges, with bathhouse domes in the lowest bowl.
- **Growth:**
  - Layer 0: the Narikala fortress, sulphur baths (brick domes) and churches.
  - Layer 1: brick houses with flat roofs (Persian era).
  - Layer 2: 19th-century courtyard tenements with carved balconies, Art Nouveau facades.
  - Layer 3: Soviet additions (enclosed balconies in mismatched glass and tin).
  - Layer 4: cyberpunk.
- **Openings:** balconies with turned or fretwork balusters and carved pelmets; shushabandi glazed galleries (small-pane, stained glass); tall double doors onto the balconies.
- **Roofs:** low tin roofs at 15–20° (painted red `#9a3a2a` or grey), flat brick roofs with domes (the baths), slate gables on the towers.
- **Ornament:** fretwork (lacy cut timber), carved posts and brackets, stained glass, tiled bath portals (blue mosaics).
- **Public space:**
  - Courtyards: semi-public, shared by the families.
  - Bath-quarter squares with domes.
  - A riverside promenade.
  - Church yards.
  - Fortress terraces with a cable-car station.
- **Water:** the river gorge and waterfall (a pond with a waterfall), sulphur pools in the domes.

## Street hierarchy
- **Riverside avenue (main):** 8–10 m, along the gorge.
- **Old-town lanes:** 3–5 m.
- **Courtyard passages.**
- **Stairs.**
- **Squares:** the bath square, church squares, fortress terrace.

## Plants
- Grapevines everywhere: on the balconies, courtyard pergolas and wires across the lanes. A Georgian signature (Rkatsiteli; the city of gardens).
- Persimmon, fig and pomegranate in the courts.
- Plane trees (*chinar*) on the avenue.
- Walnut.
- Roses and geraniums on the balconies.
- Cypress at churches.
- Mountain birch and fir around the Svan towers.

## Cyberpunk overlay
- Balconies multiplied into stacked gallery-pods with stained-glass LED panes; every courtyard a glowing well of stacked galleries.
- Vines on fibre trellises.
- Svan towers as comms masts with antennas on their roofs.
- Cable-car pods over the gorge.
- Sulphur steam vents lit purple.
- **Night:** balconies glow from inside through stained glass (jewel colours), and courtyards are warm wells. The gorge is crossed by lit bridges, the domes glow from steam. The towers' tops blink with red aviation lamps (`#ff3030`).

## Kit
- **Shared pieces:**
  - `balcony_timber_covered` (main), `gallery_timber` (main), `galeria_glazed` (shushabandi), `fretwork_eave`, `turned_post`, `stair_spiral_external`
  - `patio_gallery`, `bracket_corbel`, `cantilever_beam`, `dome_small`, `dome_ribbed`, `tower_square` (Svan), `stone_slab_roof`, `corrugated_panel`
  - `laundry_line`, `lantern_wall`, `bell_tower`, `door_room`
- **Unique pieces:**
  - `shushabandi_gallery`: a small-pane stained-glass enclosed balcony.
  - `fretwork_balustrade`.
  - `svan_tower`: tapered, slate gable, machicolated top.
  - `bath_dome_cluster`: low brick domes with skylight nubs.
  - `cliff_post_frame`: posts holding a house over a drop.
- **Parameters:**
  - Balconies on 60–90% of facades, full width, depth 1.5–2.5 m, stacked.
  - Timber in strong colours against brick or stucco.
  - Lean and sag jitter.
  - Courtyard galleries on every inner face.
  - Towers 4–6× the height of the houses, spaced 25–60 m apart on the upper terraces.
