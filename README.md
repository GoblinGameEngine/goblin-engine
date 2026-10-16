# Goblin Game Engine

**The goal: a living, breathing alternative world that anybody can explore and make their own.**

The Goblin Game Engine is a Godot 4 engine and toolchain for building very large, inhabited, procedurally generated
worlds, and for building them with AI agents. Every part of the world comes from research and from tools that can be
rerun:
- generators for terrain, towns and floating cities;
- modular building, vehicle and character pipelines;
- a living population with daily lives;
- offline checkers that can see and test all the geometry without launching the game.

Its sample game, **Space Station Columbia**, is that world.

![Night lane on a floating city: pools of light at the shopfronts, a lit blade sign](docs/media/2026-10-16/island_neon_night.jpg)

## Space Station Columbia

An ark ship 500 years into a 1,500-year voyage: an O'Neill cylinder 20 km across and 22.4 km long, launched in 2252.
The game year is 2752. Its floor holds a research-derived American landscape at full scale:
- 22 towns and cities; the cities are self-contained city-states, each with its own customs, diplomacy and sphere
  of influence;
- farms, rivers, a lake, two seas, roads and a railway;
- a rocky New England north, a sandy California south, and river towns that blend the two.

The Sunline, travelling the central Spindle, lights it. You can walk it, drive its electric vehicles, ride its road
trams or fly its aerostats. The menu is the NYNEX Communicator, a mid-90s PDA running "The System".

750 m overhead drift **the Skein**: 100 floating cities, home to 97,070 Aloft islanders across 44 architectural
traditions. They are the world's mixing engine. An island's people and its architecture often come from different
heritages (Black Anglo families in a Maghrebi medina, Irish-Scots in a Scots close town), and new customs grow out
of the blend. The islands dock into rafts, trail 300 m banners advertising their names and wares, fly their own
flags, and come down to trade.

| | |
|---|---|
| ![Island banners seen from below](docs/media/2026-10-16/banners_from_below.jpg) | ![Calder's shop street at night](docs/media/2026-10-16/calder_signs_night.jpg) |
| Island banners from below: each island's name and wares | Calder at night: bitmap shop signs and lamp pools |
| ![An island lane by day](docs/media/2026-10-16/island_lane_day.jpg) | ![The Communicator's Date & Time app](docs/media/2026-10-16/datetime_app.jpg) |
| A medina lane on a floating city | The Communicator's new Date & Time app |

### What's new (2026-10-16)
- **Floating cities you can walk all of.**
  - 47,350 of 47,357 doors on the 100 islands can be reached and entered on foot from the arrival point, with no
    jumping. That is checked by an offline audit that agrees with in-game walks.
  - Stairs are smooth ramps, arches and doorways are clear openings of at least 1.0 × 2.2 m, and every lane has a
    floor.
  - Paved paths cross the greens, and grass blades sway in the wind.
- **No more flicker.**
  - The kit's overlapping faces are fixed at the source (0 left).
  - Island shadows and the station floor seen from aloft are steady.
- **Smoother level of detail:** a new middle level of detail, about 39 % of the full triangles, between the full pieces
  and the distant boxes.
- **Night:**
  - pools of light at lamps and shopfronts, dark between them, with light carried in the air that fades as you
    leave town;
  - signs that glow only where they should, readable at night.
- **Signs everywhere:**
  - 3,354 shop name boards and about 870 office plaques across the 22 towns;
  - island shopfront signs in each island's own style;
  - 100 island flags;
  - five sign styles per region, sharing a regional heritage.
- **A calendar:** day 0 is Wednesday, 24 May 2752. The Communicator's Date & Time app sets the time, day and date, and
  the sky, lights, people and traffic follow.
- **The canon grows:**
  - Islanders now come down often, and half their children settle on the surface as **Lowliners**. Lowliners are
    liked in the North and meet real friction in the poorer South.
  - Every town keeps a mooring ground by its weekend **flea market**.
  - Five moored islands make a Bright Week; seven at a small town make a Sky Holiday. The market build is next.

![Offline render of SKY-022 from the audit toolkit, no game running](docs/media/2026-10-16/audit_SKY-022_aerial.png)
*Offline render of SKY-022 from the audit toolkit, with no game running.*

## The tools that build it

Each tool is a script you can rerun. The world is regenerated, not hand-placed.

| Tool | What it does |
|---|---|
| `tools/map_expanded.py`, `road_network.py`, `road_fix.py`, `terrain_relief.py` | The map: terrain, rivers, seas and graded roads built to a researched road standard |
| `tools/settlegen/` | Towns and cities at 1:1: lots, centres, buildings, populations, jobs |
| `tools/sky/warren/` | The floating-city generator: it grows each island on a 3 × 3 × 3.2 m lattice in epochs, then a walk network, doors, paths, chunks and LODs |
| `remake/blender/sky/warren_kit/` | The 402-piece warren kit, plus its middle-detail versions, ramp and frame collision, and its own flicker and bounds checks |
| **`tools/sky/warren/audit/`** | **The offline geometry audit.** It assembles an island exactly as the game builds it (render and collision), then checks for holes, cracks, non-manifold and bad-normal meshes, z-fighting, floating pieces, pieces outside their bounds, and intrusions. Its walk simulation sweeps the player's capsule along every route to every door. It is verified by 11/11 mutation tests and against in-game walks, and renders offline views |
| `tools/signs/` | Sign sheets from 2D reference art, cut into atlases. It also renders each shop's real name in its region's style |
| `tools/bible/` | The game bible: canon for the world, its people, history and the islands, generated into `remake/bible` |
| `.claude/skills/ssc-asset`, `tools/assets/` | The asset pipeline. Grok makes 2D reference images only; every model is built in Blender from them, reproducibly |
| `tools/gcmd.py` and `DevBridge.gd` | Agent tooling: drive and inspect the running game from a shell |
| `Prof` / `PerfProbe` | Per-system frame profiling (60 fps on a Steam Deck is the budget; lessons in `research/perf_learnings.md`) |

`research/` holds the research everything is built from: urban layout, buildings, roads and traffic law,
demographics, daily lives, the sky islands, flea markets and bazaars, and more.

## Download

Earlier builds are on the [Releases](https://github.com/GoblinGameEngine/space-station-columbia/releases) page of
the old game repo. The latest is [0.7.9 alpha 2](https://github.com/GoblinGameEngine/space-station-columbia/releases/tag/v0.7.9-alpha.2):
- **Windows (x86_64):** `SpaceStationColumbia-windows.zip`. Unzip it, keep the `.pck` beside the `.exe`, and run
  `SpaceStationColumbia.exe`. It's unsigned, so SmartScreen may warn you: choose More info, then Run anyway.

To build the current version from source:
1. Run `python3 tools/pack_data.py`.
2. Export from `godot_project/` with Godot 4.7: `godot4 --headless --path . --export-release Linux build/space-station-columbia.x86_64`.

The game data pack is now about 3 GB.

You need a Vulkan-capable graphics card. The NPCs talk through Groq: paste your own free key in the Communicator's
NPC AI app.

**Testing?** Please report bugs and impressions on the [Issues](https://github.com/GoblinGameEngine/goblin-engine/issues)
page. Say what you were doing, what you expected and what happened; include your graphics card and a screenshot if
you can.

## Controls

Keyboard and mouse, or a controller: any gamepad, or the built-in controls of the Steam Deck, ROG Ally, Legion Go
and similar handhelds.

| | Keyboard / mouse | Controller |
|---|---|---|
| Move / look | WASD / mouse | left stick / right stick |
| Jump (swim up) / swim down | Space / Ctrl | A / B |
| Use, talk, board, leave a vehicle | E | X |
| Attack / change weapon | left click / wheel | RT / LB, RB |
| Sprint | hold Shift | click the left stick (stays on until you stop) |
| Communicator | Tab | Menu |
| Drive: throttle / brake, reverse / steer | W / S / A, D | RT / LT / left stick |
| Aerostat: climb / descend | Space / Ctrl | RT or A / LT or B |

**Getting around:**
- The Communicator's Summon menus bring aerostats, boats, cars, trucks, farm vehicles, small vehicles and trains to
  you.
- Fast travel lists the towns and the Floating Cities.
- Crashes count: a hit at 10 km/h or more is loud, and from 15 km/h it does damage.

In the Communicator, a controller moves a stylus: A taps, B goes back, LB and RB change tabs, the right stick scrolls
and Y opens the System menu. On a Steam Deck the touchscreen works too. Stick speed and invert-look are in Control
Panel > Controls.

**Handhelds:**
- **Steam Deck:** add the game to Steam with *Add a Non-Steam Game* and play it in Game Mode. Steam's on-screen
  keyboard comes up for text boxes.
- **ROG Ally and Legion Go:** run it on Windows as it is. The controls work as a gamepad, and Windows' touch keyboard
  comes up for text boxes.

## Roadmap

In this order:
1. **The flea markets:** a weekend market in every town, island moorings and gondolas, trading tents, Bright Weeks and
   Sky Holidays, a secondary economy that melds the American swap meet with the bazaar, and Lowliner neighbourhoods
   in the South Sea cities.
2. **A player body:** a full body with a head (never seen from inside), crouch, ledge hang and climb, and modern
   first-person movement. The same animations drive every human NPC.
3. **The ship-blocker pass:** every clipping, non-manifold and bad-normal problem found and fixed project-wide, with
   the audit grown into a general geometry toolkit.
4. **Animals:** the ark's larger land mammals, wild and domestic, 500 years on.
5. Then the city-states' politics, the story, and shipping.

## License

All rights reserved for now (see `LICENSE`). This repo is public so it's visible and testable, not because it's open
source yet. A permissive license is planned once the project reaches a usable state.

## Version

**Current: `0.8.2-beta.1`** (beta). It is tracked in the `VERSION` file at the repo root and mirrored into
`godot_project/project.godot`'s `config/version`. The change history is in [CHANGELOG.md](CHANGELOG.md).

The scheme is `MAJOR.MINOR.PATCH-phase.N`, where the phase is one of `prealpha`, `alpha`, `beta` or `rc`. The phase is
dropped at `1.0.0`, the first real release.
- `MAJOR.MINOR.PATCH` bumps like normal SemVer.
- `N` counts tagged pushes within a phase.
- Advancing a phase resets `N` to 1 and is a deliberate call. The project moved to alpha at 0.7.9 (2026-09-29) and to
  beta at 0.8.1 (2026-10-09).

Each versioned push is tagged as `v<version>`.

## Repo layout

- `godot_project/`: the Godot 4.7 project. The main scene is `remake/scenes/RemakeStation.tscn`.
  - `remake/` holds the station's data (terrain, placement, roads, vehicles), buildings, the sky islands and warrens,
    signs, and the bible.
  - `scripts/world/` holds the world systems: MapTerrain, MapRoads, DaySkySystem, StationCalendar, LightField,
    StreetLights and the rest.
- `remake/`: the building and kit pipelines (catalog records, Blender generators, checks).
- `tools/`: the generators, the audit and sign tools, and `gcmd.py` (the DevBridge client).
- `research/`: the research behind the map, the buildings, the road standard, the people, the islands and the
  markets.
- `docs/media/<date>/`: the screenshots for each update.

`.gitignore` excludes, on purpose:
- `/reference/`: source photos and reference images, kept local;
- `godot_project/.godot/`: the editor cache;
- `godot_project/build/`: export outputs;
- Blender autosaves and generated build products.

Pushed with the `gh` CLI as the `GoblinGameEngine` account. Commits use
`GoblinGameEngine <GoblinGameEngine@users.noreply.github.com>`, set locally for this repo.
