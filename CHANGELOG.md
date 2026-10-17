# Changelog

Each entry gets its own screenshots in `docs/media/<date>/`.

## 0.8.3-beta.1 (2026-10-16): a player body, modern first-person movement, weapons in hand

**The body**
- The player is now a true first-person full body: the same generated person the NPC systems build, glued under the
  player capsule and posed by the shared animator. Look down and you see yourself (a dark collar seals the neck);
  your shadow and every other camera show the whole person with the head; only your own view culls it (the head and
  neck render on a layer the player camera skips — shadows ignore camera culling, so the shadow keeps its head).
  Camera pitch spreads down the spine, neck and head, and past ~35° down the body eases back so the chest never
  crosses the near plane. The bicycle rider's old collapsed-neck stopgap is replaced by the same split.

**Movement**
- Crouch toggled on C (pad B): capsule 1.45 → 0.95 m with its own squat animation and a ceiling check before
  standing.
- Sprint + crouch = slide, with a boost, slope gravity and a slide-hop; step-up to 0.36 m with eye smoothing;
  lean on Q/R (0.30 m + 10°, capped at walls).
- Vault low walls (≤ 0.55 m, speed kept) and mantle chest-high ledges (≤ 1.35 m) on jump; ledge hang with shimmy,
  climb up and drop.
- From the water: jump at a boat and the player hauls over the gunwale onto the deck.
- A real jump: push-off extension, lead-knee tuck in the air, a reach into the fall, and a landing knee pulse that
  recovers into the walk. Landing dips the eye.

**Weapons and actions**
- The equipped weapon rides in the hand (grip transforms solved against the live prop frame): the pistol follows
  the aim, the bat carries at the side. Fixed a weapon-manager leak on equip/unequip.
- New authored animation clips: punch, bat swing, pistol fire, door reach — wired to combat and door interactions.

**Shared with every NPC**
- All of it — jump, crouch, slide, mantles, combat clips, door opens — drives the NPC humans through the same rig
  and clip set, previewed and verified on NPC bodies in third person.

**Verification**
- New headless movement test with real physics and synthesized input: 26 assertions, all passing (body split and
  layers, walk/sprint/step-up, crouch including blocked stand, slide, vault, mantle, hang catch/climb/drop, jump
  phases, swim and water-to-boat, lean, clip presence).
- Animation clips: 55 clips × 12 body types, 0 failures.

**Known remaining:** the project-wide clipping/manifold fix campaign (the ship-blocker pass) is next — the audit
tools hold full-world baselines; the movement-critical cases (camera near-plane, mantle/hang destination checks,
lean caps) are handled by design and test.

## 0.8.2-beta.2 (2026-10-16): the flea markets — a weekend market in every town, and the islands come down to trade

**The markets (the ground side)**
- **All 22 towns and cities have a flea market**, built to a researched plan: 2,660 stalls in all. Each market has
  its gravel lot (striped bays, poles with lamps), covered shed rows, open back-to-back rows with fire lanes, a food
  truck row and court, an entrance arch, a lettered market board, a pylon sign, a bus stop, a vendor lane and
  an apron — in six layout variants fitted to each town's free land by a siting search (slope, roads, schools and
  hospitals kept clear; the market takes only free land).
- **Victory Bay's market floats**: The Regatta Swap stands on a pier deck over the water — gangway, mast and guys,
  clan-coloured tent raft, lit at night by strings over the deck — because its island has no free land.
- **A real market week.** Markets open Friday to Sunday (hours differ by tier), with setup, lantern-lit evening,
  teardown and after-hours phases. 21,280 townsfolk hold stalls as a weekend second job, drawn from the real
  population (the occupancy model's worst market runs 81 % full, the mean is 91 %). On a market Friday, hundreds of
  out-of-town shoppers travel in (Calder: 377).
- **New kit models**: food trucks (two variants), the market office, gate house and restroom — 162 pieces in the
  market kit, all audit-clean.
- **Holidays close the town.** When seven islands moor at a small town, it's a Sky Holiday: most shops shut (Loomis
  Grove: 91 of 105 units), the market rings with islander tents, overflow parking opens on the apron, and three
  quarters of the town holds a holiday fair stay.

**The moorings (the sky side)**
- **Every island got a mooring quarter** from the warren generator: 191 gondola stations (166 passenger, 25 cargo),
  255 line houses, 88 crew drop-cage davits, with station halls, plinths, signal masts and walks joined to each
  island's street net — 188 of 191 stations reachable on foot in the offline audit.
- **Islands now book, approach and moor.** A pure weekly calendar books islands to markets (no island at two
  markets, a month between visits). A moored stay runs TRIM → APPROACH (down to 600 m) → crew drop → anchor →
  logistics → rigging → SERVICE → strike → cast off. Hawsers run to deadmen, rafts lash together, banners furl,
  and winds over 9 m/s hold the descent.
- **Gondolas you can ride**: jig-back cabins at 8 m/s between the island and its ground station, with doors, dwell
  times and cabin wardens; a drop cage for the crew. Trading tents with lanterns, festoons and sky goods fill the
  mooring field; five islands in SERVICE make a Bright Week with strings of light over the whole lot.
- **It costs almost nothing per frame**: the whole drift step with mooring went from 15.0 ms to 2.8 ms, flat over
  long runs (a layout cache that thrashed, full work every step instead of once a second, and two pre-existing
  O(n²)/O(n³) raft checks replaced by a sort-sweep).

**World plumbing**
- The far side now shows the market lots by day and their lit poles and festoons by night (full far-side rebake,
  day and night, 400 tiles each).
- The daily-lives chain rebaked end to end for the pier and the markets: 214,356 people, 0 unplaced, 99 % of jobs
  staffed.
- Fixed: a terrain rewrite had invalidated six bake stamps (roads, walks, pads, far terrain, structures, trees), so
  every load silently rebuilt road bands; all six rebaked and verified.
- Fixed two generator regressions the audit caught: dressing pieces could block a walk choke point (now removed as
  a last resort), and stowed swing-girder bridges reach ~15 m along the dock face (mooring sites now keep
  directional clearance; a few line houses and davits that stood under girders were correctly dropped).

**Known issue:** standing at ground level inside a market during a celebration (town + market + moored raft all in
view) can dip to 32-38 fps on a Steam Deck; everywhere else holds 48-156. Queued for the next performance pass.

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
