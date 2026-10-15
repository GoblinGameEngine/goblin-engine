# Japanese backstreets: zakkyo towers, yokocho alleys and machiya (Tokyo, Osaka, Kyoto)

**Mark:** Pencil-thin multi-tenant towers each with a vertical column of lit signboards, over alleys 1-2 m wide of tiny bars under red lanterns and noren curtains; wires overhead; machiya timber lattices at the low end.

Sources: Shinjuku Golden Gai (~250-280 bars, six alleys); Omoide Yokocho; Osaka Ura-Namba / Dotonbori; Kyoto machiya; zakkyo buildings

## Examples and references
- [GO TOKYO: Shinjuku Golden Gai, around 280 bars](https://www.gotokyo.org/en/spot/62/index.html)
- [Golden Gai: six alleys too narrow for a car, bars of five stools, flats above](https://www.happyjappy.com/tokyo/shinjuku/golden-gai.html)
- [Japan Times: Emergent Tokyo (yokocho, zakkyo, how the city grows)](https://japantimes.co.jp/culture/2022/06/09/books/emergent-tokyo)
- [The Creative Adventurer: Golden Gai](https://thecreativeadventurer.com/golden-gai-tokyo/)

## How it grew
- Edo-Meiji: machiya, deep narrow timber townhouses (5.5 m x 20-40 m) with lattice fronts and a courtyard garden.
- Post-war: black-market alleys of tiny 2-storey bars become yokocho; 1960s-80s zakkyo buildings: 5-10 storey thin concrete towers, one tenant per floor, each with a sign in a vertical column on the front.
- Pencil buildings on 3-5 m plots; external stairs; overhead wires on poles everywhere.

## Generator grammar
- **Cell:** 3.5 x 3.0 m; storey 3.0 m; 2-10 storeys.
- **Walls:** tiled/rendered concrete (zakkyo), timber and plaster (machiya), corrugated sheet (yokocho backs); 0.2 m thick; palette #c9c4b8, #8f8a80, #5a4634, #2c2c2c, #d8cfbd, #b23a2e; weathering: soot, rust on stairs, faded tiles.
- **Mass:** Blocks cut into very narrow plots; zakkyo towers 5-10 storeys on the street edges; inside the block low 2-storey yokocho clusters; machiya rows in the quiet streets.
- **Streets:**
  - shopping street (shotengai): 8 m (arcade roof, banners)
  - side street: 5 m (zakkyo sign columns both sides, wires overhead)
  - yokocho alley: 1.5 m (bars both sides, red lanterns, noren)
  - roji (back path): 1.0 m (potted plants, bicycles)
- **Growth, in layers:**
  - machiya: 2-storey timber lattice townhouses [timber, plaster, tile]
  - yokocho: 2-storey bar shacks [timber, corrugated]
  - zakkyo: 5-10 storey thin towers with sign columns and external stairs [concrete, tile, steel]
  - cyberpunk: giant 3D signs (a crab, a runner), video walls, vending machine rows, dense overhead cable [LED, acrylic]
- **Openings:** Machiya: koshi timber lattices; zakkyo: aluminium windows, a stair door per floor; bars: sliding doors with noren.
- **Roofs:** Machiya: grey kawara tile, low; zakkyo: flat with water tanks, AC units, a small rooftop shrine.
- **Ornament:** Signs, lanterns, noren, plastic flowers, rooftop torii.
- **Public spaces:** A shrine with a precinct (torii, trees), small pocket parks, the shotengai; on an island: a shrine forest and pond, a covered shopping arcade as the main street, a canal promenade.
- **Water:** Canals (Dotonbori), a shrine pond.
- **Street hierarchy:** shotengai 8 m (covered) > side street 5 m > yokocho 1.5 m > roji 1 m

## Foliage
- Japanese maple, pine (pruned): sculpted, 2-6 m, shrines, machiya gardens (#a8322a / #2f5a2a)
- cherry (sakura): spreading, 4-8 m, canals, parks (#f2c4d0)
- potted plants and bonsai: dense pot clusters at doors (roji gardens), 0.2-1.5 m, alley edges, doorsteps (#4f7f3d)
- zelkova, ginkgo: street trees, 8-15 m, avenues (#d8b02a)

## Cyberpunk overlay
- vertical sign columns on every zakkyo
- red paper lanterns and noren
- vending machines glowing
- giant 3D figure signs
- overhead wire mesh
- video walls on corners
- **Night:** Columns of lit signs climbing every building, alleys of red lantern glow, vending machine white light pools, black wire against a bright sky.

## Kit
Shared pieces:
- `sign_vertical_stack`: a lightbox per floor, the whole height
- `lightbox_sign`: stack members
- `lantern_paper`: red chochin at bar doors
- `noren`: bar doors
- `vending_machine`: 1-3 per block corner
- `stair_steel_external`: zakkyo side stairs
- `wire_bundle`: overhead between poles every 10 m
- `roof_shrine`: 1 in 5 roofs
- `screen_lattice`: koshi timber lattice (machiya)
- `alley_bar`: yokocho
- `sign_figure_3d`: 1-2 per island, on the main street

Pieces unique to this family:
- new: utility_pole (concrete pole with transformer and wires)
- new: torii (a shrine gate)

Parameters that make the common pieces read as this civilization:
- proportions: very thin tall towers (3-5 m wide, 5-10 storeys); low bars
- rhythm: each tower different; sign columns regular
- depth: signs 0.6-1 m out; lattices flush
- colours: greys, dark timber; saturated sign colours
- materials: tile, concrete, timber, steel
