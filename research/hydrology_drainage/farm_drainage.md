# Midwestern Farm Field Drainage — Ditches and Tile

## Two coexisting drainage systems

Real Midwestern row-crop land almost always combines **surface drainage** (visible ditches, field grading) with **subsurface drainage** (buried perforated tile pipe, invisible from above). A generator wanting "visible drainage patterns" should lean on the surface system and use the subsurface system only as a subtle texture cue.

### Subsurface tile drainage (mostly invisible, but leaves visual traces)

- Typical burial depth: **3–4 ft**, with an acceptable range of **3–6 ft**.
- Typical spacing between parallel tile lines: **30–100 ft**, though a synthesis of recent Midwest field studies found actual spacing ranging 6–36 m (≈20–118 ft) with a **median of about 13.7 m (~45 ft)**. Shallower tile requires tighter spacing; higher-permeability soils allow wider spacing.
- Drainage coefficient (how fast the system is designed to remove water): typically **0.25–0.75 in/day** across the Corn Belt.
- **Visible surface signature:** tile lines themselves aren't visible, but crops directly above a tile line often show a **subtle color/growth-stage difference** from the surrounding field — greener and more vigorous in wet periods (the tile is actively relieving waterlogging right there) or conversely slightly different shade in dry periods. On aerial/satellite imagery this shows up as faint **parallel striping across a field**, spaced at the tile interval, usually running perpendicular to the ditch or waterway the tile empties into. This is a good "hidden but discoverable" visual detail for a game map (e.g., visible from a higher zoom/overhead view, not obvious at ground level).

### Surface ditches

- Roadside and field-edge ditches carry water off the field surface, especially in flat, poorly-drained, low-slope land (under ~0.5% slope is called out specifically as needing vegetated surface ditches).
- Minimum ditch depth for a simple vegetated ditch: on the order of **6 inches** (obviously real drainage ditches serving larger areas are much deeper — this is the floor for a minimal swale).
- Design principle: **field ditches → carry to a small named creek → creek carries to the main river.** This is the routing hierarchy a farm zone should visually express: short field ditches feeding into slightly larger, more defined drainage channels/creeks, which then feed the main meandering river (possibly via one of the tributary ponds/creeks described in lakes_and_ponds.md).
- Ditches are very often laid out **on a grid aligned to the section/property lines** (the classic Midwest 1-mile section grid), i.e. straight, rectilinear, and running along field edges/road edges rather than following natural contours — this is a strong, distinctive visual signature that contrasts sharply with the organic curves of the river. That contrast (rigid ditch grid vs. sinuous river) is itself a good design tool: it reads as "farmland" at a glance.

## Design-relevant conclusion

For a game map, render farm-zone drainage as: (1) a light rectilinear grid of ditch lines paralleling field/road edges, spaced far more coarsely than the real 30–100 ft (that's invisible at map scale — see design-notes file for a game-appropriate spacing), (2) these ditches collecting into a handful of small named creeks that visibly run to and join the main river or one of its tributary ponds, and (3) an optional faint striping texture inside a few fields near the ditches to hint at subsurface tile, perpendicular to the ditch direction.

## Sources
- [Drain Spacing Calculator Guide, SDSU Climate Office](https://climate.sdstate.edu/water/drainspacingcalculatordocumentation.html)
- [Frequently Asked Questions About Subsurface (Tile) Drainage, NDSU Extension](https://www.ndsu.edu/agriculture/extension/publications/frequently-asked-questions-about-subsurface-tile-drainage)
- [Paired field and water measurements from drainage management practices in row-crop agriculture, NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9160221/)
- [2022 Ag Census reveals surprising trend in acreage of tile drainage in the Midwest, MSU CANR](https://www.canr.msu.edu/news/2022-ag-census-reveals-surprising-trend-in-acreage-of-tile-drainage-in-the-midwest)
- [Tile Depth and Tile Spacings?, MK Farm Drainage Specialists](https://www.mkdrainage.com/insights/2019/7/16/tile-depth-and-tile-spacings)
- [Basic Engineering Principles 2, Wisconsin Extension](https://fyi.extension.wisc.edu/drainage/files/2018/03/Basic_Eng_-Princ-2_2018.pdf)
- [Agricultural Drainage, MSU CANR (E3370)](https://www.canr.msu.edu/field_crops/uploads/files/E3370%20AgriculturalDrainage_Rev3.pdf)
