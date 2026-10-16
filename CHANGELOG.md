# Changelog

Each entry gets its own screenshots in `docs/media/<date>/`.

## 0.8.2-beta.1 (2026-10-16): walkable floating cities, night light, signs everywhere, the offline audit

**Floating cities (the warrens)**
- **Walkable everywhere.**
  - The ground is graded in quarter storeys, and every door stands level with its street or has a stoop or porch up
    to it.
  - Upper flats are entered through an internal stair core.
  - Doors and shopfronts that led nowhere became windows.
  - A new path-by-path ground layout (`walknet.py`) keeps everything connected to the arrival point. Sealed houses
    were joined to a neighbour or became walled gardens.
- **Collision.**
  - Stairs collide as smooth ramps from the kit's explicit ramp quads.
  - Arches, doorways and gates collide as jamb, pier and lintel boxes around a clear opening of at least
    1.0 × 2.2 m; door leaves and screens don't block.
  - Floors are kept per height, so a lane under a bridging room keeps its floor.
  - Doors to rooms that aren't built are shut.
  - Bridge thresholds have ramps.
- **Result, measured by the offline audit:** 47,350 of 47,357 doors are reachable and enterable (was 36,511), with 0
  unreachable (was 3,145), 0 missing walls and 0 open roofs. 91 of 100 islands are fully walk-clean. In game, SKY-022
  went from 2/10 doors to 9/10.
- **Level of detail:** a new MID level for every kit piece (31k triangles against the full 84k), between the full
  pieces (under 45 m) and the boxes (to 520 m).
- **Grass** blades on greens, banks and beds, out to about 40 m.
- **Flicker, fixed at the cause.**
  - A kit load-order race had drawn placeholder boxes.
  - Coplanar faces were fixed in 246 pieces.
  - Shadows crawled aboard a moving island.
  - The dither cross-fade read as false edges.
  - The deck poked through the paving.
  - The far-side night twinkle and the ground clutter drawn on top of the far-side image while aloft.
  - Road paint and the window glow aliased.
- **Banners and flags.**
  - Banners 12–20 m wide and about 300 m long carry each island's name and wares; all of them cost 5 draws.
  - Flags, masts and pennants on near islands.
  - 100 provisional island flags blend each island's heritage with its architecture.

**Night**
- **Pools of light:** light builds up at lamps, shopfronts and lanterns and stays dark between them (an island lamp
  grid, plus Calder storefront pools).
- **Lit air:** light carried in the air (`LightField.gd`) fades as you leave town.
- **Signs:**
  - glow only on letters, neon and bulbs, on one emissive scale;
  - glow threshold 1.5, no bloom;
  - glare sprites trimmed.

**Signs**
- **Art:** 33 low-res Grok 2D sheets cut into atlases (`tools/signs/crop_sheets.py`): markets, island fascias, blades
  and emblems, business types, goods, mascots and adverts.
- **City shops:** 3,354 name boards in the 22 towns, in five regional styles each, plus about 870 office plaques.
- **Island shops:** each island's architecture sign blank, lettered in the islanders' heritage font.

**Time**
- `StationCalendar`: day 0 is Wednesday 24 May 2752 (VY 500).
- The Communicator's **Date & Time** app sets the time, weekday and date, and changes the clock speed. Everything
  follows the clock.
- Trips past midnight now advance the day.

**Tools**
- **`tools/sky/warren/audit/`:** the offline geometry audit.
  - It assembles an island's render and collision exactly as the game does.
  - Checks: holes, cracks, manifold and normals, z-fighting, floating pieces, bounds, intrusions, and a capsule walk
    simulation to every door.
  - Verified by 11/11 mutation tests, and its collision matches the game's at 453/453 contact points.
  - It renders offline views.
- **The kit's own checks:** flicker (coplanar), passes (walk-through frames) and ramps.

**Canon** (`tools/bible`, `research/sky_islands`, `research/flea_markets`)
- Islanders come down often; half their children settle on the surface as Lowliners (29,000).
- Every town keeps a mooring ground by its flea market. Bright Week comes at 5 or more islands, the Sky Holiday at 7
  or more at a small town.
- The cities are city-states.
- The research is done for the flea markets: American markets, flea-market economics, bazaar history, the secondary
  economy, names and signage.

**Fixes**
- The NPC daily-life code no longer errors on a place unit that isn't loaded.
- Sign data is now included in exports.
