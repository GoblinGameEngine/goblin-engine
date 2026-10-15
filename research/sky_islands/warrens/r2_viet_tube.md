# Vietnamese tube houses and hem (Hanoi Old Quarter, Saigon alleys, Hoi An)

**Mark:** Facades only 3-5 m wide but 4-6 storeys tall and 20-60 m deep, every one a different colour and height like books on a shelf, balconies with plants, tangles of wires, and hem alleys threading behind.

Sources: Hanoi Old Quarter (the 36 guild streets); Ho Chi Minh City hem (~85% of residents live in alleys); Hoi An

## Examples and references
- [Local Vietnam: tube houses 2-4 m wide, up to 60-70 m deep, frontage taxes, inheritance](https://localvietnam.com/culture/history/vietnamese-tube-houses/)
- [Hem (Wikipedia)](https://en.wikipedia.org/wiki/H%E1%BA%BBm)
- [Saigon alley types: tricycle / car / tiny; 50-100 residents an alley](https://vjol.vista.gov.vn/tcxd/en/article/view/59086)
- [Homage Project: the Vietnamese tube house](https://www.homageproject.org/southeastasia/the-vietnamese-tube-house)
- [Hanoi 36 streets: Hang + the trade](https://localvietnam.com/hanoi/hanoi-36-streets/)
- [Dennis Holloway: tube house](https://dennisrhollowayarchitect.com/TubeHouse.html)
- [AIA: hem urban villages, community-driven urbanism](https://www.aiainternational.org/online-lectures-calendar/2026/3/27/aia-oceania/-aia-southeast-asia-hm-urban-villages-in-ho-chi-minh-city-vietnam-a-model-for-community-driven-urbanism)

## How it grew
- Old Quarter: guild streets (Hang Bac silver, Hang Ma paper...), timber-framed tube houses with courtyards.
- French era: brick and render fronts with shutters, balconies, pediments.
- 1990s-: every family adds storeys on its own plot: 2 -> 4 -> 6 storeys, each a different colour; balconies, rooftop gardens and tanks.

## Generator grammar
- **Cell:** 4.0 x 3.5 m; storey 3.3 m; 2-7 storeys.
- **Walls:** brick and concrete, rendered and painted in strong flat colours; 0.22 m thick; palette #e8c84a, #7fb0a8, #e8a07a, #b9cfe0, #f2eee4, #9a4a3a, #5a7f4a; weathering: mould streaks in the tropics, faded paint, peeling.
- **Mass:** Rows of 3-5 m wide plots of differing heights abutting; deep plots with 1-3 light-well courtyards; blank side walls (exposed when a neighbour is lower: painted ads on them).
- **Streets:**
  - guild street: 8 m (shops spill out, motorbikes parked on the pavement)
  - car hem: 5 m (alleys big enough for a car)
  - tricycle hem: 3 m (the usual alley)
  - tiny hem: 1.5 m (pedestrian, shrines, plants)
- **Growth, in layers:**
  - old: 1-2 storey timber tube houses with tile roofs [timber, tile]
  - colonial: 2-3 storey rendered fronts with shutters [brick, render]
  - growth: each plot grows 1-4 storeys at its own pace, colour by colour [concrete, paint, steel balconies]
  - cyberpunk: neon on every ground shop, LED on balconies, wire tangles thicken [LED, cable]
- **Openings:** Full-height French doors with louvred shutters onto narrow balconies; roller shutters at ground.
- **Roofs:** Flat with rooftop gardens, tanks, a small shrine; old houses: tile roofs.
- **Ornament:** Painted pediments, balcony railings, Hoi An: yellow walls and silk lanterns.
- **Public spaces:** Lake in the middle (Hoan Kiem), communal house (dinh), pagodas, night markets; on an island: a central lake with a red bridge and a promenade, a market street, alley shrines.
- **Water:** A central lake; rain drains.
- **Street hierarchy:** lake promenade 10 m > guild streets 8 m > car hem 5 m > tricycle hem 3 m > tiny hem 1.5 m

## Foliage
- Dracontomelon (sấu), Khaya, banyan: big street trees, 12-25 m, avenues, lake edge (#3f6a35)
- bougainvillea: cascades from balconies, 1-4 m, balconies (#d8307a)
- potted plants, orchids, kumquats: rows of pots on balconies and roofs, 0.3-1.5 m, balconies, roofs (#4f7f3d)
- water lilies, lotus: pond, 0.2-1 m, lake (#5f9a3e)

## Cyberpunk overlay
- wire tangles on every pole
- a neon sign per shop at street level
- LED balcony rails
- silk lanterns (Hoi An) in LED
- **Night:** Coloured slices lit at ground with neon, balconies with fairy lights, motorbike headlight rivers, a lake reflecting lantern bridges.

## Kit
Shared pieces:
- `wall_panel_render`: 3-5 m wide fronts, strong colours, each plot different
- `french_window`: full-height with shutters
- `balcony_iron`: narrow, every storey
- `shutters`: louvred
- `shopfront_shutter`: ground
- `wire_bundle`: poles every 15 m
- `planter`: balcony rows
- `lantern_cn`: silk lanterns (Hoi An style)
- `water_tank`: roofs
- `mural_wall`: exposed party walls with painted ads

Pieces unique to this family:
- new: party_wall_blank (the exposed side wall of a taller tube house)

Parameters that make the common pieces read as this civilization:
- proportions: extreme 1:4-1:6 width:height slices
- rhythm: every 3-5 m a new colour and height
- depth: balconies 0.8 m
- colours: saturated flat paints, each plot one colour
- materials: render, steel, tile
