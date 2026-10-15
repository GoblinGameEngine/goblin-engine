# Jiangnan water town and the Shanghai lilong (Zhouzhuang, Suzhou, Wuzhen, shikumen lanes)

**Mark:** White walls and black tiles over canals: houses front a lane and back onto the water with private steps down to boats, humpbacked stone bridges, and dense lilong lane-quarters behind stone gates.

Sources: Zhouzhuang; Suzhou Pingjiang; Wuzhen; Shanghai shikumen lilong

## Examples and references
- [Zhouzhuang: 井-shaped canal grid, 14 stone bridges, 60% original Ming-Qing houses, Double Bridge](https://govt.chinadaily.com.cn/s/202202/17/WS620e1c44498e6a12c121f514/zhouzhuang-water-town.html)
- [Amusing Planet: the water town of Zhouzhuang](https://www.amusingplanet.com/2014/08/the-water-town-of-zhouzhuang.html)
- [Google Arts: architectural features of Wuzhen](https://artsandculture.google.com/story/cwUhm9yYS8-aIg)
- [Jiangnan families: houses backed by rivers, facing roads, private wharfs](https://www.privatephotoreview.com/2024/12/09/recording-the-real-scene-of-families-in-the-ancient-town-of-jiangnan/)
- [Shikumen (Wikipedia): trunk lane, branch lanes, stone gateways, 2-3 storeys](https://en.wikipedia.org/wiki/Shikumen)
- [SmartShanghai: walking into the lanes](https://www.smartshanghai.com/articles/shanghai-life/walking-into-the-lanes-of-shanghai)
- [UNESCO tentative list: water towns](https://whc.unesco.org/en/tentativelists/5328/)

## How it grew
- Song-Qing: canal towns where the canal is the main street; houses 2 storeys, front shop on the lane, workshop and wharf on the water; courtyards (tianjing) inside.
- 1860s-1930s Shanghai: shikumen lilong -- rows of 2-3 storey terraced houses behind stone-framed gates, on a trunk lane with branch lanes, the whole quarter behind a street-front shop row.
- Later: rooms added on top (tingzijian, rooftop terraces), sheds, laundry poles over the lanes, wires.

## Generator grammar
- **Cell:** 4.0 x 3.5 m; storey 3.2 m; 2-4 storeys.
- **Walls:** whitewashed brick with grey-black tile copings; dark timber front panels and doors; 0.3 m thick; palette #ece8dc, #d8d3c5, #2f2f2f, #5a4632, #8c8a82, #a03a2c; weathering: grey-green mildew streaks down the white, black lichen at the base.
- **Mass:** Long narrow houses (4 m x 15-30 m) in rows between a lane and a canal, with 1-3 small courtyards each; lilong quarters: rows of terraced houses in a comb off a trunk lane.
- **Streets:**
  - canal: 8 m (the main street; boats; stone revetments 1-2 m high)
  - canal-side street: 4 m (stone-paved, shops, covered loggias over the water)
  - lane (lilong trunk): 4 m (behind a stone gate)
  - branch lane: 2.5 m (doorsteps, chairs, laundry poles overhead)
  - bridge: 3 m (humpbacked stone arch, steps)
- **Growth, in layers:**
  - water town: 2-storey white houses with timber fronts on canals, bridges, temples [brick, whitewash, timber, black tile, granite]
  - lilong: 3-storey shikumen rows with stone gate frames [grey/red brick, stone]
  - overgrowth: rooftop rooms, sheds over courtyards, laundry poles, wires, AC [timber, corrugated, plastic]
  - cyberpunk: red lantern strings over canals turned to LED, holographic shop signs on timber fronts, lit boats [LED, acrylic]
- **Openings:** Full-width timber shop fronts of removable boards; lattice upper windows; round and leaf-shaped moon-gates in garden walls; stone-framed shikumen doors with black lacquered leaves.
- **Roofs:** Black tile, double-pitched, gentle curve, ridges with upturned ends; stepped gable firewalls (horse-head walls in Huizhou-influenced towns).
- **Ornament:** Carved brick gate frames, timber lattice, red lanterns, ink calligraphy shop banners.
- **Public spaces:** Canal junction squares, bridge landings, a temple, a classical garden (pond, rockery, pavilions); on an island: a central canal loop with a broad stone quay street, a lotus pond garden, a market square at a bridge.
- **Water:** Canals everywhere: the island has a grid of 2-3 canals round a central pond.
- **Street hierarchy:** canal 8 m (+ quay streets 4 m) > lilong trunk lane 4 m > branch lanes 2.5 m > bridges

## Foliage
- weeping willow (Salix babylonica): drooping, 6-12 m, canal edges (#7fa64a)
- lotus (Nelumbo): pads and pink flowers, 0.5-1.5 m, ponds (#5f9a3e / #e89ab0)
- osmanthus, plum, camellia: small round trees and shrubs, 2-5 m, courtyards, gardens (#3f6b36)
- bamboo: clumps behind white walls, 3-7 m, gardens (#6d9a46)

## Cyberpunk overlay
- red LED lanterns strung across canals
- neon calligraphy banners
- lit boats
- projection on white walls
- screens behind lattice windows
- **Night:** White walls lit warm from below by lanterns and reflected in black water; red lanterns doubled in the canals; quiet, glowing, misty.

## Kit
Shared pieces:
- `wall_panel_white`: whitewash, black tile coping, 4 m bays
- `shopfront_shutter`: timber board fronts
- `screen_lattice`: upper windows
- `lantern_cn`: red, strings over canals
- `gable_step`: horse-head firewalls on row ends
- `water_channel`: canals
- `gate_portal`: stone shikumen gate frames
- `laundry_line`: bamboo poles over lanes
- `timber_eave`: shallow, black tile

Pieces unique to this family:
- new: hump_bridge (a single-arch stone bridge with steps)
- new: water_steps (stone steps down from a back door to the canal)
- new: moon_gate (a round opening in a garden wall)

Parameters that make the common pieces read as this civilization:
- proportions: low (2-3 storeys), long and narrow, roofs dominant
- rhythm: repeated narrow fronts with black roofs stepping
- depth: shallow timber fronts, deep overhanging eaves 0.8 m
- colours: white / black / dark timber / red accents
- materials: brick, whitewash, tile, granite
