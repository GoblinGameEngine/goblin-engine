# R4: methods: how to generate and render warren cities (2026-10-14)

This is research stream 4 of the warrens round (see 00_brief.md). Streams 1–3 describe civilizations; this one is
about how to grow them and draw them at 60 fps on a Steam Deck. The concrete proposal is in r4_design.md.

## 1. Generating organic, layered cities

### Tile and module assembly (WFC / model synthesis / dual grid)
- **Model synthesis (Merrell 2007, i3D; PhD 2009) is the original of "wave function collapse".**
  - It fills a lattice with modules that satisfy adjacency constraints learned from an example.
  - Merrell & Manocha's *Continuous Model Synthesis* (2008) used it on office buildings.
  - Gumin's 2016 WFC popularised a variant.
  - Merrell himself now calls tile-based methods limited to "structures built from tiles" and has moved to graph
    grammars.
- **Townscaper / Bad North (Oskar Stålberg):**
  - An irregular quad grid made by splitting a hex grid into quads and relaxing it.
  - Marching-cubes style placement: pieces sit on the corners of cells, not inside them.
  - WFC checks adjacency, re-evaluating neighbours when a block changes. In real time it can fail silently, and a
    failed cell is simply left empty.
  - Decoration (windows, chimneys, gardens) is a separate pass after the hard placement; windows are cut with a
    stencil buffer.
  - Design lessons:
    - spend the effort where things *change*: where materials meet, where walls turn;
    - keep the large structure readable and vary the small detail;
    - irregularity breaks repetition.
- **The dual grid** (corner Wang tiling; Boris the Brave's marching-squares tutorial):
  - Choose each piece from the occupancy of the 4 (2D) or 8 (3D) cells around a lattice *corner*.
  - That cuts a 2D tileset from 47 blob tiles to about 15–16, and in 3D the number of unique corner configurations up
    to rotation is small.
  - This is the key to rounded mud-brick corners, buttresses and quoins without an explosion of pieces.
- **Limits:**
  - WFC needs backtracking or restarts on larger 3D lattices.
  - Pure WFC gives local consistency but no global intent (streets, history), so practitioners pair it with a
    higher-level plan: Caves of Qud's multi-pass ruins put coarse architecture first and finer detail after.
  - Recent work (WFCNUT, FDG 2024) lets tiles span several cells.

### Shape grammars
- **CGA shape (Müller, Wonka, Haegler, Ulmer, Van Gool, SIGGRAPH 2006):** a mass model first, then facade detail split
  rule by rule. Context-sensitive rules stop windows hitting walls and put doors on terraces and street level. It
  was used for Pompeii and later in CityEngine.
- Shape grammars are excellent for *one building's facade*, but weak for the fused, accreted mass of a warren, where
  "buildings" have no clear boundaries.

### Growth and accretion
- **Batty's cellular-automata and agent models** (*Cities and Complexity*, 2005; "Urban evolution on the desktop",
  1998): settlement form emerges from local rules repeated over time ("growing cities").
- **Watabou's road-centric generator:** roads grow organically like veins (after Parish & Müller, without the
  L-systems), and blocks fill in after. It adapts naturally to terrain.
- **Historical layering:** a TU Delft thesis notes that most urban generators are static, with no change in the
  generation process over time, so their results lack historical meaning. Time-stepped generation is the gap our
  "centuries of layers" idea fills.
  - Era-specific rule sets (Eurographics 2010 poster) and the historical procedural models (Besuievsky & Patow; Rome
    Reborn) show rules swapped per period.
- **Caves of Qud:** villages carry generated histories, cultures and architectural styles. Ruins are generated in
  passes from the culture that built them: coarse first, then detail.

### Level grammars
- **Spelunky:**
  - First guarantee a critical path (a 4×4 room grid walked from top to bottom).
  - Then fill each room from hand-made templates by its role on the path (8–16 templates per type, with
    probabilistic tiles).
- The lesson for warrens: **guarantee connectivity first** (streets, stairs, a route to every door and every bridge),
  then decorate.

### Kowloon-like levels in games
- A university project (RWU, "procedural realtime environment") assembles a Kowloon district from modular assets and
  modifiers.
- Phantasmal (2015) generates the walled city but repeats its elements visibly.
- Design writing on Kowloon stresses that single units stacked over time, with facades that don't need to align, are
  the generator's model.
- Grid generators look too regular, and practitioners suggest cellular automata or agent methods for the ad hoc
  growth.
- Cloudpunk's vertical city is voxel art, hand-built; no procedural pipeline is published.

### Conclusions for us
- Use a **3D occupancy lattice grown in epochs** (accretion, CA-like rules per civilization) for the mass. The
  history comes for free.
- Guarantee the network first: main streets, plazas, stairs and bridges.
- Pick pieces with the **dual grid / corner method** for walls, corners and roofs.
- Use **deterministic rule selection with local adjacency constraints**. Full WFC only for facade strips, if at all,
  so nothing fails silently.
- Decoration comes in a separate pass.

## 2. Rendering at scale

- **Draw calls:**
  - Godot's MultiMesh draws thousands of instances in one call. But a MultiMesh is one spatial unit (it always renders
    and needs a hand-set AABB), and it counts as one object for the per-object light limit in Forward+.
  - Merging static geometry that sits close together (SurfaceTool / ArrayMesh) is the usual alternative.
  - One report cut about 2,500 draws to about 45.
  - Our own measurement (memory: shared parts, 2026-10-13): a MultiMesh per kit piece cost Calder 17–21% more draws and
    10–14% fps against merging the pieces into each model's mesh. **Merge per chunk; MultiMesh only for scattered
    props and foliage.**
- **Merging on a worker:**
  - Old 3.x docs warn that `append_from` on a thread stalls on the GPU round-trip.
  - In 4.x we already run `RemakeBuilding.merge_kit` (SurfaceTool.append_from) on the WorkerThreadPool in production,
    and it works.
  - Safer still: keep the kit pieces' surface arrays cached in RAM (`Mesh.surface_get_arrays` once on the main
    thread) and concatenate PackedArrays on the worker, with only `ArrayMesh.add_surface_from_arrays` on the main
    thread.
- **HLOD:**
  - Forza Horizon's Tokyo used HLOD: merged, simplified stand-ins for groups of world content, with projection LOD
    for distant detail. That kept the skyline readable at low cost.
  - Unreal's octahedral impostors combined badly with HLOD proxies in reported cases.
  - City Sample fed collision proxies into the HLOD mesh approximation to close holes.
  - For us: chunk → chunk group → whole-island hull, plus the existing island lod1/lod2.
- **Interior mapping (van Dongen, 2008):** rooms behind flat windows, perspective-correct with parallax and no
  geometry. It's used in Spider-Man, Forza Horizon, SimCity 2013, and as an Unreal node; a Godot atlas version is on
  godotshaders.
  - It can be fully procedural: a box room with a floor, ceiling and back-wall colour, plus a furniture silhouette
    card, which needs no texture.
- **Reflections:**
  - Reflection probes are cheap only when set to update once, and they don't follow a moving island well.
  - SSR was reworked in 4.6 (Hi-Z, half-res).
  - On the Deck, a **fresnel term mixing in the sky colour** (the global `sky_color` already exists) on window glass
    is the cheapest believable reflection, and hides empty interiors by day.
- **Occlusion culling:**
  - Godot's occluders rasterise on the CPU (Embree), help most in dense small-room scenes, and cost CPU every frame.
  - **Moving occluders trigger a recomputation that takes several frames.** Our islands move every tick, so occluders
    are out for them; use chunk visibility ranges and LOD instead.
- **Physics interpolation:** move interpolated objects in the physics tick; parents carry children. It doesn't reduce
  the per-node cost of moving a large tree. **The real cost is node count**: we measured about 2.3 ms per tick to
  move the near islands' ~8k nodes. Fewer nodes (chunked meshes, RenderingServer instances, one body) is the fix.

## 3. Foliage
- **Space colonisation** (Runions, Lane & Prusinkiewicz 2007): attraction points shape the branching. It's good
  offline for a handful of hero meshes per species; at runtime we only instance.
- **Godot's "Making trees":**
  - vertex colour paints the sway mask;
  - the sway is a sine of world position and TIME in the vertex shader, so copies sway consistently;
  - a shared wind-noise texture keeps neighbours in step.
  - Per-instance random phase comes from the model matrix (godotshaders leaf shader).
- **Rule:** one material per species, with variation from instance data (INSTANCE_CUSTOM: colour, sway phase, scale),
  never separate materials.
- **Vines:** alpha-scissor cards along walls, from the decoration pass.
- **Hash in the island's frame:** a world-space hash on a moving island reshuffles every frame. That was our lod_vc
  flicker, fixed on 2026-10-14.

## 4. One shared kit, real ethnic diversity (the user, 2026-10-14: "only adding to the shared parts library")
- **Bethesda's kits** (Burgess & Purkeypile, GDC 2013 Skyrim, GDC 2016 Fallout 4):
  - A kit is a family of pieces snapped to one grid. Two artists built and kept refining Skyrim's kits while level
    designers used them, and a small team built a huge world.
  - The lesson: a **shared grid and snapping contract** is what lets pieces recombine, and diversity comes from many
    kits on one grid, not one kit per building.
- **Assassin's Creed:**
  - Mirage's Baghdad started from 300+ placeholder modules drawn from Abbasid references (facades, windows, doors,
    shopfronts, mashrabiya), assembling both homes and military buildings.
  - Syndicate's industrial kit had hundreds of climbable modules, with roof modules joining wall modules to any size.
  - Regional identity comes from a **region-specific vocabulary on a common modular frame**.
- **Townscaper:** a small corner-based kit; the variety comes from *where things change* (corners, material meets,
  roof meets wall) and from a decoration pass.
- **Habraken's supports and infill** (Open Building, 1961):
  - A shared, durable base building (the support) is filled by each household with its own infill.
  - The built environment is a never-ending design process.
  - This is the exact model for our layers: the old masonry is the support; each epoch's rooms, screens, balconies
    and shacks are infill.
- **Alexander's *A Pattern Language*:** culture is a set of patterns, rules for how parts relate, not a set of shapes.
  The same pieces read differently under different patterns.
- **Our levers for diversity from common pieces**, in order of effect:
  1. **Massing grammar:** the plan type (courtyard house, tower house, shophouse, perimeter block, gallery tenement,
     fused megablock, cave-cut terrace), storey count, setbacks versus cantilevers, roofscape (terraces,
     pitched-tile, pagoda eaves, domes over halls only).
  2. **Street grammar:** a tree of cul-de-sacs (Islamic medina), a grid of narrow lanes (Kowloon), galis off a bazaar
     spine (Karachi and Delhi), terraced switchback stairs (Mediterranean hill towns), canals (Venice).
  3. **Proportion and rhythm:** bay width, storey height, the window-to-wall ratio, how openings stack (aligned rows
     or random), wall thickness (deep reveals in mud and stone, shallow in timber and concrete).
  4. **Material and colour:** wall finish (mud render, whitewash, ochre, brick, ashlar, tin, concrete, timber) and
     palettes from research. One kit piece takes many materials.
  5. **Ornament vocabulary and density:** screens, bands, brackets, eaves, gables, tiles. A small set of
     civilization-specific pieces carries the "mark".
  6. **The plants**, and the street furniture (lanterns, awnings, signs) of each culture.
  7. **The cyberpunk overlay,** shared by all but density-tuned per culture (Kowloon heavy, Ghadames light).

  A dome on a block fails because it changes only lever 5. Real difference needs levers 1–4 first.

## 5. Walkable cities, turned into layout rules
- **Jane Jacobs** (*Death and Life*, 1961), four conditions all needed together:
  - mixed primary uses;
  - short blocks;
  - buildings of mixed ages;
  - dense concentration.

  Our epochs give the mixed ages for free (old masonry beside new tin). Short blocks mean frequent corners and lanes.
- **Jan Gehl** (*Life Between Buildings*, *Cities for People*):
  - Active, open, lively edges matter more than anything else: soft, transparent, door-rich ground floors drew many
    times more lingering than blank walls.
  - Human scale for contact: you recognise people at about 50–70 m, see their feelings at about 22–25 m, and talk at
    about 7 m.
- **Christopher Alexander:**
  - Activity Nodes (30): about 300 yd (275 m) apart, at path junctions, with a small square at the centre.
  - Promenade (31).
  - Accessible Green (60): a green within a 3-minute walk (~230 m) of every home, at least 45 m across and about
    5,600 m² (scaled down for small islands).
  - Small Public Squares (61): 14–18 m across, never more than about 21 m, longer in one direction.
- **Barcelona superblocks:**
  - Traffic stays on the perimeter of 3×3 blocks.
  - Inside, streets are calm (10–20 km/h).
  - The crossings of green axes become plazas, and the space taken from roads becomes public space.
  - On our islands there are no cars: the main streets are the paved spine for carts and bicycles, and everything
    else is pedestrian.
- **Rules for 1–10 block islands:**
  1. A main street (8–12 m paved, lined with arcades or shops) runs from the main bridges to the central plaza. Big
     islands get a loop or cross.
  2. The central plaza is the activity node (a Pattern-61 small square of 14–21 m, or a larger civic forecourt on
     10-block islands). Add one more node per ~275 m.
  3. A green within ~230 m of everything:
     - the pond with its banks is a public green, always reached by a lane;
     - at least one more green or garden court per 3 blocks;
     - roof gardens count in the dense civs.
  4. Lanes, 2–4 m, branch from the main street in the civ's own grammar. Blocks between lanes stay short: at most
     ~45 m without a lane or passage (an arch tunnel counts).
  5. Edges: ground floors on the main street and plazas are at least 70% "soft" (shopfronts, doors, stalls). Blank
     walls go only on lanes, in courtyard civs (whose life faces inward), and on the island rim.
  6. Every door, stair, bridge, pad, hoist, pond bank and plaza is on one connected walk graph, including the upper
     levels: roof terraces linked by stairs and bridges count as streets.

## 6. Fast travel to the floating cities
- The PDA Navigator's Travel page lists a "Floating Cities" group (scripts/ui/GameMenu.gd `_sky_dests`, about line
  1755).
- `SkyIslands.fast_travel(i)` (remake/scripts/sky/sky_islands.gd, about line 301) holds the player over the drifting
  city until its deck has loaded, then sets them down at `travel_local(i)`.
- The generator only has to name each city's **arrival point**: its gate plaza by the main bridge, or the central
  plaza. That goes in the layout as `"travel": [x, y, z]`, with a clear 6 m disc and a landmark in view.

### Sources for §4–6
- [Modular Level Design for Skyrim (GDC 2013 slides)](https://www.slideshare.net/slideshow/gdc2013-kit-buildingfinal/17728576) · [Fallout 4's Modular Level Design (GDC 2016)](https://gdcvault.com/play/1022930/-Fallout-4-s-Modular) · [PC Games write-up](https://www.pcgames.de/Spiele-Entwicklung-Thema-35261/Specials/So-entstehen-Skyrim-Fallout-und-Co-Das-modulare-Level-Design-von-Bethesda-erklaert-Teil-2-1067744/)
- [AC Mirage modular Baghdad (artist profile)](https://fr.linkedin.com/in/cristel-mrowka) · [AC Syndicate industrial kit (Polycount)](https://polycount.com/discussion/comment/2387992)
- [Habraken, introduction](https://habraken.com/html/introduction.htm) · [Open Building (TU Delft)](https://tudelft.nl/en/architecture-and-the-built-environment/research/research-stories/would-you-buy-a-design-it-yourself-apartment)
- [Jacobs' four conditions](https://www.sindark.com/2015/01/02/jacobs-four-top-requirements-for-cities/) · [On Jane Jacobs (New Geography)](https://mail.newgeography.com/content/002711-on-jane-jacobs-generating-and-preserving-diversity)
- [Gehl, Life Between Buildings / Cities for People (alevin.com)](https://www.alevin.com/?m=201301) · [Gehl review (Englewood)](https://englewoodreview.org/featured-cities-for-people-jan-gehl/6/) · [Public life and human scale](https://www.studiomatrx.org/students/urban-design-and-planning/public-life-and-human-scale)
- [Pattern 30, Activity Nodes](https://urbigenous.net/a-pattern-language/pattern-030.html) · [Pattern 61, Small Public Squares](https://urbigenous.net/a-pattern-language/pattern-061.html) · [Pattern digest (Cottage Grove)](https://www.cottagegroveor.gov/sites/default/files/fileattachments/community_development/page/415/app20m.pdf)
- [Barcelona superblocks (99% Invisible)](https://99percentinvisible.org/article/civic-superblocks-barcelonas-urban-redesign-returns-streets-residents/) · [ULI](https://urbanland.uli.org/planning-design/barcelonas-experiment-superblocks?p=8) · [Cities Forum](https://citiesforum.org/news/superblock-superilla-barcelona-a-city-redefined)

## Sources
- [How Townscaper works: a story four games in the making (Game Developer)](https://www.gamedeveloper.com/game-platforms/how-townscaper-works-a-story-four-games-in-the-making)
- [Math and Art, with Oskar Stålberg (podcast)](https://etao.blog/2020/10/13/podcast-94/)
- [WFC Experiments 2 (on Stålberg's "Beyond Townscapers" talk and the dual grid)](https://yadu.itch.io/wfc-experiments-2)
- [Model synthesis (Wikipedia)](https://en.wikipedia.org/wiki/Model_synthesis)
- [Merrell & Manocha, Continuous Model Synthesis (2008)](https://www.cs.princeton.edu/courses/archive/spring11/cos598A/pdfs/Merrell08.pdf)
- [Graduate seminar: Paul Merrell (BYU)](https://cs.byu.edu/news/graduate-seminar-paul-merrell)
- [Boris the Brave: marching squares / dual grid (Sylves)](https://www.boristhebrave.com/docs/sylves/1/articles/tutorials/marching_squares.html)
- [Dual-grid tilesets explained](https://www.spritecook.ai/blog/dual-grid-tilesets-explained)
- [WFC with non-uniform tiles (FDG 2024)](https://graphics.tudelft.nl/Publications-new/2024/PB24/FDG24.Rolf.demo.Final.pdf)
- [Müller et al., Procedural Modeling of Buildings (SIGGRAPH 2006)](https://course.ccs.neu.edu/cs5150f13/readings/muller_buildings.pdf)
- [Batty, Cities and Complexity](https://www.tenlong.com.tw/products/9780262025836)
- [Watabou, experimenting with road-centric generation](https://watabou.itch.io/medieval-fantasy-city-generator/devlog/31287/experimenting)
- [TU Delft thesis on temporal urban generation](https://repository.tudelft.nl/file/File_869cdf34-a987-4836-8a6c-b7f22154c8ab)
- [Procedural modeling historical buildings for serious games](https://polipapers.upv.es/index.php/var/article/view/4268)
- [Caves of Qud: Village (wiki)](https://wiki.cavesofqud.com/wiki/Village) · [GDC: Caves of Qud](https://gdcvault.com/play/1025914)
- [Spelunky Generator Lessons (Kazemi)](https://www.tinysubversions.com/spelunkyGen2/index.html)
- [Procedural realtime environment (RWU)](https://www.rwu.de/en/projects/procedural-realtime-environment)
- [Kowloon Walled City lives on in videogames (Rhizome)](https://old.rhizome.org/editorial/2011/sep/14/kowloon-walled-city-lives-videogames)
- [Cloudpunk (80.lv)](https://80.lv/articles/cloudpunk-new-voxel-indie-game)
- [Interior mapping (80.lv)](https://80.lv/articles/interior-mapping-rendering-real-rooms-without-geometry) · [UDK gem](https://docs.unrealengine.com/udk/Three/DevelopmentKitGemsInteriorMapping.html) · [Godot fake interior shader](https://godotshaders.com/shader/fake-3d-interior-projection-shader-fixed-adjustable/)
- [Godot: occlusion culling](https://godot.readthedocs.io/uk/4.x/tutorials/3d/occlusion_culling.html) · [Optimizing 3D performance](https://docs.godotengine.org/en/4.4/tutorials/performance/optimizing_3d_performance.html)
- [Godot: MultiMesh](https://docs.godotengine.org/es/4.x/classes/class_multimesh.html) · [itch.io merged-instances report](https://itch.io/post/11110997)
- [Godot: physics interpolation](https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/using_physics_interpolation.html)
- [Godot: reflection probes](https://godot.readthedocs.io/en/stable/tutorials/3d/reflection_probes.html) · [Godot 4.6 SSR deep dive](https://www.strayspark.studio/blog/godot-46-rendering-deep-dive-ssr-lightmapper-performance)
- [Simplygon: HLODs in Forza Horizon's Tokyo](https://simplygon.com/blog/f2a10dde-4ca7-44e1-9ee3-eaa8286f4d4e) · [UE ImpostorBaker](https://dev.epicgames.com/documentation/unreal-engine/API/PluginIndex/ImpostorBaker) · [HLOD impostors thread](https://forums.unrealengine.com/t/hlod-impostors/222909)
- [Runions et al., Modeling trees with a space colonization algorithm](https://www.algorithmicbotany.org/papers/colonization.egwnp2007.pdf)
- [Godot: Making trees](https://godot.readthedocs.io/en/4.0/tutorials/shaders/making_trees.html) · [Leaf shader](https://godotshaders.com/shader/leaf-shader-flower/) · [Wind area effect](https://godotshaders.com/shader/wind-area-effect/)
- [Godot: SurfaceTool](https://docs.godotengine.org/en/4.2/classes/class_surfacetool.html)
