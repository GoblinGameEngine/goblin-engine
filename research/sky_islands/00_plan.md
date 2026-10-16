# Sky islands: plan and contracts (2026-10-14)

## The user's brief, 2026-10-14
> We need floating islands the size of one to ten city blocks. They will be rocky bottoms with hanging moss and vines.
> They will be held aloft by large, tall cylindrical weather baloons that stretch a kilometer high by 100m in diameter.
> The number of ballons will be dictated by the size of the island. They will be irregularly shaped with flat tops or
> rolling hills. They will orbit 750m above the surface and float with the wind. When two islands get within 3km of one
> another, the occupants will shoot rockets towing long lines to lash the islands together. Each island is heavily
> developed and occupied. The people who occupy them will rarely ever go to the surface, most of them living their lives
> aboard the floating islands. They serve as roaming traders, with one representative from each island's clan descending
> to the surface with a special high performance two person aerostat capable of climbing to 1.5km in altitute and
> attaining a speed of 250km/hr. For scheduled trade, the island will drop long lines and draw up cargo containers.
> Likewise, they will drop cargo in these containers. The structures on the islands will be tall flat topped buildings.
> The perimeter of the island will have safety fences. There will be retractable bridges on all four sides, sometimes
> multiple bridges to a side, depending on the size of the island. When the islands dock, the bridges on the adjoining
> sides lower and NPCs, travel between the two. These islands are each a self sustained community existing within a
> wider, loose confederation of other floating islands. Write a backstory for the islands, determine the jobs and
> populations of each one, and make the islands. We will need 100 unique islands. The buildings can use the shared
> parts. There is no need to make very much new. The islands will have small foot paths. People will get around on
> bicycles. The bigger islands will have proper roads. They will each have a unique name. The names will be nautical,
> mystical, whymsical, and ancient. When you make the islands, use shared parts. The islands should be modular. The
> bridges will all be the same style on an island, but there will be many style bridges. We will need models for the
> island components and LOD models for the islands themselves. The people of the islands need to be a unique, rich,
> diverse divergent society. They will wear warm clothes from the cooler air at altitude. The buildings on the islands
> will all have roof access. Each island will have at least two of the high performance aerostats. Figurte out through
> research how this society will work, who will do what, and why they live they way they do. Gravity will be lower at
> their altitude which affects the natives as well as providing a way for them to keep their islands afloat. When an
> island goes through a cloud, it snows. We will need a snow texture and snow mechanic. We don't need to add a lot of
> models, I think we can do it with a slowly changing texture that leads to a blanket of snow. The snow melts very,
> very slowly when the island leaves a cloud.

> (follow-up) When the islands dock, they will stay together for 3days and break apart. They will not dock more than
> 10 islands together.

**Canon change, 2026-10-15** (the user, via research/flea_markets):
- The brief's "rarely ever go to the surface" is superseded. The islanders now come down **often**: islands moor at
  every town's flea market and run gondolas.
- They **settle on the surface in large numbers**: half of all island children, the Lowliners. Most settle on the South
  Sea shore.
- See `research/flea_markets/00_plan.md` §8–9 and `tools/bible/canon_sky.py` (`market_moorings`, `settled`).

## Fixed numbers (everyone uses these)
- Deck altitude: **750 m** above the nominal floor (StationGeo h = 750, radius 9,250 m).
- Spin gravity there: 9.8 × 9,250 / 10,000 = **0.925 g**. Drifting antispinward (west) lightens an island further
  (Eötvös: g_eff = (ωr − v)² / r; ω = 0.0313 rad/s, rim speed 290 m/s at 9,250 m). The canon uses both: the natives
  are a low-g people, and the islands ride the westerlies because the west wind lightens them.
- **City block = 100 m × 80 m (8,000 m²)** including its share of paths. An island of N blocks has a deck of about
  N × 8,000 m² (1 block ≈ 8,000 m², 10 blocks ≈ 80,000 m², about 280 m across).
- **Balloons:** cylinders **100 m diameter, 1,000 m tall**, base 60 m above the deck, so tops reach ~1,810 m above the
  floor. Count = `ceil(1.6 × blocks) + 1` (1 block: 3; 10 blocks: 17). They stand on splayed tethers in a
  cluster centred over the island; neighbours at least 112 m apart centre to centre (so a cluster may overhang the deck).
- **Aerostats:** at least 2 per island (`2 + blocks // 3`): the clan's two-person high-performance craft (ceiling
  1.5 km above the floor, 250 km/h). Fleet type id `sky_skiff`.
- **Docking:** islands within **3 km** fire line rockets, winch together and lash with their dock faces **26 m**
  apart. Bridges reach 13 m each and meet in the middle. Rafts hold at most **10 islands**; a raft stays together
  **3 in-game days** (3 × DaySkySystem.DAY_LENGTH_SECONDS) and then casts off.
- **Drift:** with the wind, west (antispinward, −s), ~4–9 m/s; slow meander along the axis. Islands keep
  |x| ≤ 9,000 m (well off the end caps' mountains).
- **Bridge:** deck **3.6 m wide** (pedestrians and bicycles; the big islands' road bridges are 6 m), reach **13 m**.
- Footpaths **2.5 m** wide; roads (islands of 6 or more blocks) **6 m** wide; perimeter safety fence 1.4 m high, set 1 m
  in from the edge.

## Island local frame
Every island is one Node3D placed at `Transform3D(StationGeo.basis(s), StationGeo.point(s, x, 750))`:
local **+X = south** (+x along the axis), **+Y = up** (toward the axis), **−Z = east** (spinward, +s), **+Z = west**.
Local y = 0 is the deck's base level (the dock faces' top surface). Rolling-hill islands rise above 0 inland but are
y = 0 along every dock face.

Sides: **N** = −X face, **S** = +X face, **E** = −Z face, **W** = +Z face. Each side has a straight **dock face**: the
island's outline touches that plane but never crosses it, and the side's bridges are mounted on it. A bridge's
`along` is its offset along the face (local Z for N/S, local X for E/W). Islands do not turn: N always faces north.
Two islands dock E-to-W (the usual case, along the drift) or N-to-S, and line up one bridge of each.

## Files (who writes what)
| File | Writer | Contents |
|---|---|---|
| `tools/bible/canon_sky.py` → `godot_project/remake/bible/sky_islands.json`, `research/bible/NN_sky_islands.md` | canon | the 100 islands' identities, society |
| `research/sky_islands/01..` | canon | research: physics, history, society, jobs, economy, clothing, language, customs |
| `tools/sky/make_islands.py` → `godot_project/remake/sky/islands.json` | layout | every island's layout (below) |
| `remake/catalog/SKY-*.json` → `godot_project/remake/buildings/SKY-*.glb` | layout | the islands' buildings, built by the normal library pipeline (shared kit) |
| `godot_project/remake/sky/islands/<id>.{rock,lod1,lod2}.glb` | layout | the rock underside (moss, vines) and the island's LODs |
| `godot_project/remake/sky/parts/*.glb` + `parts.json` | parts | balloon, fence, hoist, cargo container, line rocket launcher, pad, roof hatch, moss/vine cards |
| `godot_project/remake/sky/bridges/<style>.glb` + `bridge_styles.json` | parts | the bridge styles |
| fleet type `sky_skiff` | aerostat | the two-person high-performance aerostat |
| `godot_project/remake/characters/npc_outfits.json` (cold-weather outfits) | clothes | warm clothes |
| `godot_project/remake/scripts/sky/*.gd` | runtime | SkyIslands: drift, docking, rafts, bridges, cargo lines, snow, people, LOD, player |

### `remake/bible/sky_islands.json` (canon)
```
{"version": 1, "confederation": {...}, "clans": [...], "jobs": {job_id: {...}},
 "islands": [{"id": "SKY-001", "name": "...", "name_kind": "nautical|mystical|whimsical|ancient",
   "name_meaning": "...", "clan": "...", "blocks": 1..10, "relief": "flat|rolling",
   "population": int, "jobs": {job_id: count}, "trade": ["goods it makes/sells"], "needs": [...],
   "bridge_style": "<style id>", "aerostats": int, "founded_vy": int, "character": "a paragraph",
   "landmark": "...", "seed": int}, ...]}
```
The bridge style ids are fixed here: `bascule_timber`, `bascule_iron`, `telescope_truss`, `rope_lowered`,
`jackknife`, `swing_girder`, `rolling_lift`, `scissor_lattice`, `gangplank_rail`, `chain_drawbridge`.

### `remake/sky/islands.json` (layout)
```
{"version": 1, "islands": [{"id": "SKY-001",
   "outline": [[x, z], ...],          # deck edge, CCW seen from above, local metres
   "faces": {"N": -x0, "S": x1, "E": -z0, "W": z1},
   "relief": {"kind": "flat|rolling", "hills": [[x, z, radius, height], ...]},   # deck_y(x, z) = sum of smooth bumps
   "depth": m,                          # rock underside depth below the deck at the centre
   "buildings": [{"id": "SKY-001-03", "x":, "z":, "yaw":, "w":, "d":, "h":, "y":}],   # y = ground under it
   "paths": [[[x, z], ...], ...], "roads": [[[x, z], ...], ...],
   "fence": [[x, z], ...],
   "bridges": [{"side": "N|S|E|W", "along": m, "width": m}],
   "balloons": [{"x":, "z":, "anchor": [x, y, z]}],
   "pads": [{"x":, "z":, "yaw":}], "hoists": [{"x":, "z":, "yaw":}], "launchers": [{"side":, "x":, "z":}],
   "lod": {"rock": "res://...rock.glb", "lod1": "...", "lod2": "..."}}]}
```

## Added by the user, 2026-10-14 (mid-job)
> All islands will have ponds, the larger ones will have small lakes. There will be wildlife as well as livestock. We
> will create animals later, just bear that in mind for your layout. We are going to use all the tricks we've learned
> to reduce the footprint of this addition.

- Layout: every island has at least one **pond** (the larger islands also have a small **lake**), as
  `"water": [{"outline": [[x, z], ...], "level": y, "depth": m, "kind": "pond|lake"}]`, plus land set aside for
  animals later: `"pastures": [{"outline": [...], "kind": "pen|pasture|coop|wild"}]` (fenced pens and pastures for
  livestock, and unbuilt wild corners, hedges and pond margins for wildlife) and `"animal_spawns": [[x, z, "kind"], ...]`.
- Footprint (memory: ssc-size-reduction-plan): the buildings are built from shared kit pieces (SSC_KIT=1), and the import
  flags tool must be run for them. Parts are shared glbs placed many times, not baked into each island. Repeated things
  (fence runs, paths, balloons, moss) are made at runtime or with MultiMesh from data. LOD glbs stay small. Data is
  gzip-packed through DataFile/pack_data. Textures are small and tileable.
