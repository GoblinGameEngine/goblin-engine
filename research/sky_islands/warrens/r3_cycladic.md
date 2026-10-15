# R3: Cycladic (Santorini, Mykonos, Hydra)

**Island culture:** a blinding-white maze of rounded cubes, lanes twisting against wind and raiders, blue doors, chapel domes, and houses dug into the caldera rim. Hydra's grey-stone captains' mansions stand above a car-free harbour where mules carry everything. The mark is the whitewashed, hand-made softness: no sharp corners, edges rounded by layers of lime. The paving is grey slate outlined in white.

## Examples
- Santorini, *yposkafa*: houses excavated into soft volcanic pumice, long narrow rooms under a barrel vault of volcanic ash and lime (there was no timber). The open face is closed with a thin stone wall, then rendered and limewashed. A rainwater cistern for each house. Wealthy captains built freestanding houses on the rim. [studiomatrx](https://www.studiomatrx.org/architecture-canon/santorini-cave-dwellings), [holeinthedonut](https://holeinthedonut.com/2018/08/21/cave-architecture-of-santorini-oia/), [i-escape](https://www.i-escape.com/the-architects-cave-house)
- Mykonos Chora: a labyrinth said to confuse 18th–19th-century raiders, or to break the Meltemi wind. Whitewashed cube houses wall to wall like a fortress, with thick walls, small windows and brightly painted balconies. [MSC](https://msccruisesusa.com/cruise/destinations/mediterranean/greece-greek-islands/mykonos), [eathealthy365](https://eathealthy365.com/a-guide-to-mykonian-house-architecture/), [iol](https://iol.co.za/travel/2014-06-20-the-magic-of-mykonos/)
- Hydra: about 30 *archontika* (captains' mansions) and 300 captains' houses, late 18th to early 19th century. Grey stone from Hydra and Dokos, wood and tile, white window frames, 3–4 storeys. Plain, high walls with narrow barred windows outside; frescoed interiors. No cars: mules. [greeka](https://www.greeka.com/saronic/hydra/sightseeing/hydra-mansions/), [hydra.gr](https://www.hydra.gr/meet/en_arxontika.html), [elxis](https://elxis.com/?p=207139)

## Generator grammar
- **Cell:** 3.5–5 m cubes, storeys 2.8–3.2 m, 1–3 storeys (Hydra mansions 3–4).
- **Walls:** 0.6–0.8 m rubble with lime, built up in many layers of whitewash. All edges are rounded (radius 0.15 m), parapets wavy.
  - Palette: lime white `#f7f5ef`, shadow white `#d9dde2`.
  - Accents: Aegean blue `#1f5fa8`, sky blue `#4da3d8`, oxblood `#7a2a24`, olive green `#5f7a3a`, yellow `#e8c547` on doors, shutters and balconies.
  - Hydra stone: grey `#8d8a84` with white frames `#ffffff` and tile roofs `#b5563a`.
  - Weathering: very light (rewhitewashed every spring); green-grey stains at the gutters.
- **Mass:**
  - Cubes clustered wall to wall into irregular blocks of 6–20.
  - External stairs climb house fronts to roof terraces.
  - Vaulted houses are dug into the island rim (caldera variant), stacked in terraces.
  - Small domed chapels everywhere: one per 20–40 houses, blue or white domes.
- **Streets:** 1.5–3 m lanes, deliberately crooked: at least one bend every 15–25 m, and many dead ends. Stepped ramps. Lanes go under houses (*stegasta*, covered passages). Paving is grey slate with white-painted joints `#ffffff` over `#6b6e70`.
- **Growth:**
  - Layer 0: the kastro, a fortified ring of houses whose outer walls are the town wall.
  - Layer 1: cubes filling outward.
  - Layer 2: captains' mansions and windmills on the ridge.
  - Layer 3: hotels with infinity pools.
  - Layer 4: cyberpunk.
- **Openings:** small, deep windows (0.6×0.9 m) with painted frames and shutters. Doors are 0.9×2.0 m, painted. There are wooden balconies on corbels, and blue-railed roof terraces.
- **Roofs:** flat with a curved lip, or barrel vaults. Chapel domes (r 1.5–3 m), bell gables with 1–3 bells.
- **Public space:** the harbour quay (the main public room), little church squares with a big tree, windmill ridge terraces, sea-view platforms.
- **Water:** cisterns, and a pond as the harbour basin (a stilled pool in the island's deck).

## Street hierarchy
- **Harbour quay (main promenade):** 10–15 m, paved, with café tables.
- **Market street:** 3–4 m, bending.
- **Lanes:** 1.5–2.5 m.
- **Stairs:** 1.5 m.
- **Squares:** a church square every 60–100 m; the quay; the windmill ridge.

## Plants
- Bougainvillea everywhere: magenta `#c2185b` and orange-red `#e2552b`, cascading over white.
- Tamarisk and pepper trees in squares (6 m, feathery).
- Olive.
- Geraniums and basil in olive-oil tins painted white.
- Hibiscus.
- Agave and prickly pear on the rim.
- A few tall Washingtonia palms on the quay.

## Cyberpunk overlay
- Glossy white composite pods mimicking the cubes, with rounded-rectangle windows.
- Blue LED outlining every edge (the kastro line glowing).
- Chapel domes as satellite dishes and projection domes.
- Wind turbines replacing the windmills, with neon blades.
- Water-recycling tanks painted white.
- Delivery-mule robots.
- **Night:** the white walls take on every colour (they bounce the neon). Warm windows are few and small; the blue edge-glow and chapel-dome uplights do the work. The lanes are lit by small wall lamps every 15 m (`#ffd6a0`).

## Kit
- **Shared pieces:**
  - `vault_cell`, `dome_small`, `bell_tower` (as a bell gable), `stair_external_steep`, `terrace_rail`, `parapet_rounded`
  - `window_small`, `shutters`, `door_room`, `balcony_timber_covered` (Hydra), `covered_alley`, `lantern_wall`
  - `market_stall`, `awning`, `water_tank`, `planter`, `saucer_terrace`
- **Unique pieces:**
  - `chapel_cycladic`: a small cube, a dome and a bell gable.
  - `windmill_round`: a stone drum with a conical roof and sails or turbine.
  - `rounded_parapet_lip`: a soft lime coping.
  - `slate_paving_whitejoint`: a decal or texture.
  - `dovecote_tinos`: a decorated pierced wall.
- **Parameters:**
  - Everything is low (1–2 storeys typical) and close-packed.
  - Openings are tiny: window to wall 8–12%. Corners are rounded.
  - One accent colour per house (doors, shutters, rails), on white.
  - Irregular block outlines: a 0.5–1 m jog every cube.
  - The hand-made wobble: no perfectly straight long edges (vertex jitter 0.03–0.06 m).
