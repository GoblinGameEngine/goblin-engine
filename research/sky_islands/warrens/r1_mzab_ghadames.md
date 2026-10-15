# mzab_ghadames: the Saharan whitewash oasis (Ghardaïa and the M'zab, Ghadames)

## Sources and examples
- **Ghardaïa:**
  - The mosque and minaret at the centre, houses radiating round it in concentric rings; the minaret doubles as a
    watchtower; each walled village a "miniature citadel".
  - A truncated-pyramid minaret.
  - White, pink and red houses of sand, clay and gypsum rising in terraces and arcades.
  - Each ksar has a summer palm-grove town (wahat).
  - https://en.wikipedia.org/wiki/Gharda%C3%AFa · https://cales.arizona.edu/oals/ALN/aln28/solieman.html ·
    https://kupi.com/en/explore/algeria/ghardaia/history
- **Ghadames:**
  - Streets entirely covered; the ground-level sabats (dark covered lanes) are the men's routes.
  - Rooftop walkways let women move across connected terraces unseen.
  - Mud, lime and palm trunks; white walls with splashes of colour.
  - Interiors with mirrors, palm-straw ornaments, brass and copper, carpets.
  - https://en.wikipedia.org/wiki/Old_town_of_Ghadames · https://www.amusingplanet.com/2013/03/the-old-town-of-ghadames.html ·
    https://earth-auroville.com/ghadames_libya_en.php · https://www.temehu.com/Cities_sites/Ghadames.htm
- **Comparatives (my knowledge):**
  - Beni Isguen: the holy city of the M'zab, a tower of the same truncated-pyramid form, its market an open
    triangle at the gate.
  - Le Corbusier's study of the M'zab.

## Generator grammar
- **Cell and storeys:**
  - Grid 3.0 m.
  - Storeys 2.8 m (M'zab houses are compact).
  - Houses 2 storeys plus a roof terrace with arcades (M'zab); in Ghadames, 2–3 storeys over covered lanes.
  - House footprint 8–12 m with a small central opening (chebek: a grilled roof opening over the core).
- **Walls:**
  - Earth, gypsum and lime, hand-plastered with soft irregular edges, 0.4–0.6 m thick.
  - Colours: **M'zab** pastel layering: white `#f4f1ea`, sky blue `#9fc3d9`, pale pink `#e7c3b8`, ochre
    `#d9b07a`, often 2–3 per street. **Ghadames** outside: whitewash and mud `#ede7da` / `#c8a77c`; inside the
    covered lanes the walls are white with red and green painted triangles near the doors.
  - Weathering: soft erosion, hand marks, rain streaks.
- **Mass:**
  - **The cone:** the M'zab town climbs a hill in concentric rings of houses to the mosque at the summit.
    Streets spiral and radiate. Each house is a cube with a roof terrace and an arcaded loggia on the top floor.
  - **The roof-net:** Ghadames is a single continuous mass. The ground floor is a network of covered lanes
    lit by light-wells. The roofs are joined into one connected women's city with low walls, little bridges and
    steps between levels.
- **Streets:**
  - M'zab: 2–3 m lanes spiralling up, with stepped ramps and small market squares at the gates.
  - Ghadames: **covered sabats** 2–3 m wide and 2.5 m high, mostly tunnels with shafts of light every 10–20 m.
    Built-in mud benches (dukkana) line the walls where the men sit. The darkness is cool.
- **Growth:**
  - E1: the hill cone or the covered core.
  - E2: rings added outward (M'zab) or rooms over the remaining open lanes (Ghadames).
  - E3: concrete blocks below the hill.
  - E4: roof catwalks extended into a lit high-level city; light-wells fitted with light pipes.
- **Openings:**
  - small, few, rounded: windows 0.4–0.6 m;
  - doors 0.9 × 2 m in painted wood with a carved lintel;
  - M'zab arcade loggias on the roof: 2–4 round arches 1.2–1.8 m wide;
  - Ghadames triangles: little triangular niches in the parapets.
- **Roofs:**
  - flat roofs with **pointed corner horns** (Ghadames: triangular merlons at the parapet corners, whitewashed)
    and low walls;
  - arcaded loggias (M'zab);
  - **the truncated-pyramid minaret**: square, battered (tapering), 15–25 m, with four pointed corner horns at the
    top;
  - no domes.
- **Ornament:** minimal. Painted triangles and diamonds in red and green around doors (Ghadames), interior
  mirrors and brass, and the shape itself.
- **Public spaces:**
  - the market square at the foot (M'zab: a triangular square ringed with arcades);
  - the mosque terrace at the summit;
  - Ghadames: small covered squares (where two sabats widen, lit by an opening) and the spring pool (Ain el-Faras);
  - **palm-grove gardens** below as the green belt.
- **Water:**
  - wells with wooden pulley frames;
  - Ghadames' spring distributed through channels with a water clock (a timed share).
- **Plants:**
  - the palm grove (date palms 10–15 m, dense, with pomegranate and fig beneath, and vegetable plots);
  - roof terraces with **potted herbs** and a single small tree;
  - no street trees.
- **Cyberpunk overlay:**
  - The covered sabats become glowing tunnels: LED strips along the dukkana benches and in the light-wells.
  - The rooftop city carries festoons, prayer-time light rings on the minaret horns, solar film on parapets, and
    pastel neon matching the wall colours.
  - Sparse screens: quiet and devout. Cables are hidden in the walls.
- **Night:** the pastel cone glows softly; the minaret top is lit; the tunnels are lit warm amber; the roof
  walkways are traced in small lights like a constellation.

## Kit
- **Common pieces:**
  - `wall_panel` (soft earth, pastel colour per house), `parapet_rounded` + corner horns;
  - `arch_opening` (round arcade), `door_plank` (painted), `window_small`;
  - `covered_alley` (long, with light-well openings), `roof_flat_terrace`, `plank_bridge` (roof links);
  - `minaret_pyramid`, `bench_platform` (dukkana), `well` frame, palms.
- **Parameters that make it M'zab or Ghadames:**
  - the whole island as **one cone** (M'zab) or **one roofed slab** (Ghadames);
  - soft rounded edges everywhere;
  - pastel per-house colours;
  - tiny openings;
  - corner horns on every parapet;
  - a single pyramid minaret on top;
  - the roof as the public walkway.
- **Unique pieces (2):**
  - `parapet_horn` (a triangular corner merlon);
  - `minaret_pyramid` (it exists in components_a).
