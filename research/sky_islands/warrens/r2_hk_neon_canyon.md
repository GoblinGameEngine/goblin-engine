# Hong Kong tong lau and the neon canyon (Mong Kok, Sham Shui Po, Yau Ma Tei)

**Mark:** A grid of narrow 6-12 storey walk-ups lining canyon streets, with verandahs over the pavement below and a storm of projecting signs over the street; the roofs carry a second, illegal village of huts.

Sources: Hong Kong tong lau (shophouses) 1900s-1960s; Mong Kok / Nathan Road; Sham Shui Po rooftop huts

## Examples and references
- [Gwulo: Tong Lau, the Hong Kong shophouse (Lee & DiStefano)](https://gwulo.com/node/34384)
- [CityUnseen: Ghost Buildings (1903 ordinance: 4 storeys, light wells, back alleys; verandahs over the footpath)](https://cityunseen.hk/?p=626)
- [SCMP: tong lau and composite buildings](https://m.scmp.com/news/hong-kong/health-environment/article/3014526/upstairs-downstairs-how-hong-kongs-historic-tong)
- [M+ / West Kowloon: neon signs of Hong Kong](https://artsandculture.google.com/story/ogWRMXUKqUGzJg)
- [Goldthread: Hong Kong's fading neon](https://goldthread2.com/travel/hong-kong-fading-neon-lights/article/3019495)
- [Rooftop slum (Wikipedia): 1950s-60s tenement roofs turned into housing](https://en.wikipedia.org/wiki/Rooftop_slum)
- [Hong Kong Memory: Sham Shui Po squatters](https://www.hkmemory.hk/en/collections-ssphousing-development-squatters.html)
- [Canadian Architect: Portraits from Above (rooftop communities)](https://staging7.canadianarchitect.com/portraits-from-above)
- [Planning Dept: Kowloon City urban renewal (tong lau loss)](https://www.pland.gov.hk/file/resources/durf/pdf/20120228/DURF_KC_01_2012_en.pdf)

## How it grew
- Pre-war tong lau: 3-4 storeys, 4.5 m frontage (est.), 12-15 m deep, ground shop, timber floors, pitched Chinese tile roofs, verandahs on columns over the five-foot way.
- Post-war tong lau: 6-9 storeys of concrete, flat roofs, cantilevered balconies instead of verandahs, a stair at the side, no lifts.
- 1950s-60s: refugees build huts on the flat roofs; balconies enclosed; signs grow out over the street on steel arms (up to 4.2 m out by the rules, often more).
- Composite buildings (1960s): a podium of shops with 12-20 storeys of flats above; tower blocks fill gaps.

## Generator grammar
- **Cell:** 4.5 x 3.0 m; storey 3.0 m; 4-12 storeys.
- **Walls:** rendered concrete and brick, painted; mosaic tiles on 1960s fronts; 0.25 m thick; palette #d9cdb4, #b9c4b0, #e6d9a8, #9fb3b8, #c98f6a, #7d7a73; weathering: stained render, rust from balcony rails, AC drip streaks.
- **Mass:** Terraces of identical-width buildings along a street grid (blocks 50-80 m x 20-30 m); back alleys 2-3 m between back-to-back rows; heights jump 4 -> 12 storeys within a row.
- **Streets:**
  - main road (Nathan Road): 24 m (trams/buses; sign canopy over it)
  - market street (Temple St, Fa Yuen St): 10 m (stalls fill the carriageway)
  - side street: 8 m (sign canyon, verandah arcades)
  - back lane: 2.5 m (kitchens, pipes, rubbish, back stairs)
- **Growth, in layers:**
  - pre-war: 3-4 storey verandah shophouses with tile roofs [brick, timber, clay tile]
  - post-war: 6-9 storey concrete walk-ups, balconies [concrete, mosaic tile, steel windows]
  - overgrowth: enclosed balconies, window cages, rooftop huts 2-3 storeys high, AC units, signs on arms [aluminium, corrugated iron, acrylic]
  - cyberpunk: LED walls, video boards on corners, sign forests to 6 storeys [LED, steel arms]
- **Openings:** Steel casement windows in pairs; balconies with green-painted rails; ground floor fully open to shops with roller shutters.
- **Roofs:** Flat roofs with water tanks, huts, aerials; pre-war: Chinese tile pitched roofs behind parapets.
- **Ornament:** Art Deco and modernist name plaques, mosaic tile panels, Chinese characters in relief.
- **Public spaces:** Market streets, a temple square (Tin Hau, Yau Ma Tei), small sitting-out areas, a rooftop playground on a resettlement block; on an island: one boulevard 18-24 m with tram, a temple square with banyans, a pond park.
- **Water:** Hydrants, rooftop tanks; harbour edge.
- **Street hierarchy:** boulevard 24 m > market street 10 m > side street 8 m > back lane 2.5 m

## Foliage
- Ficus microcarpa (Chinese banyan): huge spreading crown, aerial roots; grows out of old retaining walls (Hong Kong 'stone-wall trees'), 8-18 m, temple squares, walls (#3e6a35)
- Bombax ceiba (red cotton tree): tall, bare in spring with red flowers, 10-20 m, parks and boulevards (#b8322a)
- Delonix regia (flame tree): umbrella crown, scarlet in summer, 6-12 m, street edges (#d8432a)
- potted plants and polystyrene vegetable boxes: pots, 0.2-1.2 m, rooftops, window ledges, cage balconies (#4f7f3d)

## Cyberpunk overlay
- projecting neon/LED signs on steel arms 2-6 storeys up, overlapping across the street
- corner video boards
- AC boxes on every window
- lit rooftop huts
- **Night:** The classic: a canopy of red, magenta, blue and green neon over a yellow-white street; flats above dim warm; rooftop huts with single bulbs.

## Kit
Shared pieces:
- `wall_panel_render`: 4.5 m bay of 2 windows, 3 m storeys
- `balcony_cantilever`: 0.9 m, green rail, every bay above 3
- `arcade_pier`: verandah columns at the kerb, 3 m spacing (pre-war rows)
- `shopfront_shutter`: ground
- `sign_blade`: steel arm, 1.5-6 storeys, 1-3 per frontage
- `neon_frame`: on blades
- `video_board`: corners
- `ac_unit`: every window
- `window_grille`: lower floors
- `rooftop_shack`: 50% of roofs, 1-3 storeys of huts
- `water_tank`: roofs
- `barrel_tile_eave`: pre-war roofs
- `tile_panel`: mosaic spandrels

Pieces unique to this family:
- new: sign_arm (a steel gantry carrying a projecting sign out over the street)
- new: verandah_bay (a pre-war verandah bay: columns, balcony slab, shutters)

Parameters that make the common pieces read as this civilization:
- proportions: 4.5 m frontages, 3:1 to 6:1 height to width
- rhythm: regular bays within a building, jumps between buildings
- depth: balconies 0.9 m, signs 2-4 m out
- colours: pale greens, creams, faded blues; signs saturated
- materials: render, mosaic, steel
