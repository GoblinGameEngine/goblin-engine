# Hakka tulou: earthen ring-houses (Fujian)

**Mark:** Huge round or square rammed-earth fortresses, blank outside, open inside: 3-5 storeys of timber galleries ringing a courtyard with an ancestral hall at the centre; a clan in each ring; rings clustered in a valley.

Sources: Fujian tulou (UNESCO 2008): Chengqilou, Eryilou, Tianluokeng cluster

## Examples and references
- [Studio Matrx: Hakka roundhouses](https://www.studiomatrx.org/architecture-canon/tulou-hakka-roundhouses)
- [National Geographic: the tulou](https://www.nationalgeographic.com/travel/article/150102-hakka-china-tulou-fujian-world-heritage)
- [CGTN: Fujian tulou](https://news.cgtn.com/news/3d3d514d3351444e34457a6333566d54/index.html)
- [Loongese: Chengqilou four rings, 288 rooms; Eryi walls 2.5 m, 73.4 m diameter](https://loongese.com/blog/heritages/fujian_tulou)

## How it grew
- 12th-20th c.: Hakka clans build defensible communal houses: walls 1.5-2.5 m of rammed earth with bamboo and timber strips, round or square, 3-5 storeys, one gate.
- Ground floor kitchens, first floor granaries, upper floors bedrooms; galleries face the court.
- Inner rings (lower) and an ancestral hall at the centre; wells in the court.
- Clusters (Tianluokeng: one square and four round) sit together in valleys among tea terraces.

## Generator grammar
- **Cell:** 3.0 x 3.0 m; storey 2.8 m; 3-5 storeys.
- **Walls:** rammed earth, ochre-yellow, smooth; stone base 1-2 m; few small windows only high up; 1.8 m thick; palette #c8a46a, #b58d55, #8a6a44, #3a3a3a, #6b4a2e, #a03a2c; weathering: rain-streaked earth, darker band at the base.
- **Mass:** Rings of diameter 30-75 m (or squares 30-50 m), 3-5 storeys, one or two inner rings, a central hall; rings sit 20-60 m apart with lanes and terraces between; on an island: 5-12 rings of different sizes linked by lanes and later infill.
- **Streets:**
  - valley road: 6 m (between the rings, paved stone)
  - ring gate passage: 3 m (the single gate through the wall)
  - internal gallery: 1.2 m (each storey's circular walkway)
  - terrace path: 1.5 m (among tea terraces)
- **Growth, in layers:**
  - rings: the earthen rings and the ancestral halls [rammed earth, timber, tile]
  - infill: lower outbuildings between rings, then 2-4 storey brick houses [brick, timber]
  - bridges: timber and steel bridges from ring roof to ring roof (Aloft) [timber, steel]
  - cyberpunk: each gallery ring traced in light, screens inside the court, lanterns [LED, paper]
- **Openings:** Outside: tiny slit windows only on upper floors, one massive gate. Inside: continuous timber galleries with lattice doors to every room.
- **Roofs:** One continuous grey tile roof round the ring with a wide eave (2-3 m) overhanging the outside wall.
- **Ornament:** Couplets on red paper at the gate, carved timber in the hall, lanterns.
- **Public spaces:** The courtyard of each ring (shared by its clan), the ancestral hall, a valley market; on an island: a central paved square between rings, a pond (the courtyard wells' source), tea terraces as green space.
- **Water:** Wells in every court; a stream or pond between rings.
- **Street hierarchy:** valley road 6 m > gate passages 3 m > terrace paths 1.5 m > galleries 1.2 m

## Foliage
- tea bushes on terraces: clipped rows, 0.8-1.2 m, terraces (#3e6a2e)
- Cunninghamia (China fir), camphor: tall conical/round, 10-20 m, hillsides (#2f5a2a)
- bamboo, banana: clumps, 3-7 m, beside rings (#6d9a46)

## Cyberpunk overlay
- every gallery ring traced in warm light
- lanterns hung round the inner gallery
- holographic ancestral tablets
- dish antennas on the ring roof
- **Night:** From above: glowing rings like reactors in the dark; from the court: tiers of lit galleries.

## Kit
Shared pieces:
- `ring_segment`: earth ring wall + gallery, diameters 30-75 m
- `gallery_timber`: inner face, every storey
- `timber_eave`: 2-3 m overhang outside
- `gate_portal`: one per ring
- `lantern_cn`: galleries
- `window_small`: outer slits, top storeys

Pieces unique to this family:
- new: ring_roof (the continuous curved tile roof of a ring)
- new: ancestral_hall (a small central hall with an open front)

Parameters that make the common pieces read as this civilization:
- proportions: massive curved walls, small windows
- rhythm: radial bays of 3 m
- depth: walls 1.8 m; galleries 1.2 m
- colours: earth ochre, dark timber, grey tile, red
- materials: rammed earth, timber, tile
