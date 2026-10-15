# saharan_kasbah: the pre-Saharan earth kasbah and ksar (Aït Benhaddou, Draa/Dades, Ksar Ouled Soltane, Siwa Shali)

## Sources and examples
- **Aït Benhaddou:**
  - Rammed earth up to the first floor, lighter adobe above to reduce the load.
  - Upper parts decorated with geometric motifs.
  - Thick windowless lower walls and angled corner towers for defence.
  - Dozens of tower-houses packed on a hill above the river.
  - https://en.wikipedia.org/wiki/A%C3%AFt_Benhaddou · https://archeyes.com/ksar-ait-benhaddou-in-morocco-unesco-world-heritage/ ·
    https://cairoscene.com/Home/The-Ageless-Mud-Brick-Fortress-of-A-t-Ben-Haddou
- **Ksar Ouled Soltane:**
  - Vaulted ghorfa granary cells, 4 storeys round two courtyards.
  - Steep external stairs climbing to single doors; about 400 cells, each owned by one family.
  - Later repaired in cement.
  - https://en.wikipedia.org/wiki/Ksar_Ouled_Soltane · https://www.amusingplanet.com/2014/11/ksar-ouled-soltane-fortified-granary.html
- **Siwa Shali:**
  - Kershef (salt crust and mud) blocks in salty mud mortar; palm trunks reinforcing walls and ceilings.
  - Melted by rain (1926); restored from 2018.
  - https://iwh.icesco.org/shali-village-in-siwa-oasis/ · https://next.archnet.org/sites/21598 ·
    https://iris.cnr.it/handle/20.500.14243/119082
- **Draa and Dades tighremt (my knowledge):** a square plan with four tapering corner towers 12–18 m, the upper
  third carved with relief patterns in the mud (chevrons, lozenges, blind arcades), windows tiny below and larger
  above.

## Generator grammar
- **Cell and storeys:**
  - Grid 3.0 m.
  - Storeys 2.8 m.
  - Tighremt 3–5 storeys (12–18 m), ksar houses 2–3.
  - **Ghorfa** cells: barrel vaults 2–3 m wide × 5–10 m deep × 2–2.5 m high, stacked 2–5 high.
  - Shali: an irregular mound of cells 2–4 storeys.
- **Walls:**
  - **Pisé** (rammed earth in 0.6–0.9 m lifts, showing horizontal lift lines and tie holes) at 0.6–1.0 m thick,
    battered strongly (towers taper 3–6%).
  - Upper walls in adobe with **relief decoration**: patterns cut by recessed and projecting bricks.
  - Colour: the earth itself, red-ochre `#b5653f` (Draa), `#c07a4c`, pink-buff `#cf9a6e`; Shali grey-buff `#a8957b`
    with salt-white glints; ghorfa whitewashed patches and earth `#c9a57a`.
  - Weathering: slumped tops, rain grooves, collapsed sections (ruins are native here, and suit the layering).
- **Mass:**
  - Clusters of towers on a slope, with a fortified granary (agadir/igherm) at the top.
  - **Ghorfa honeycomb blocks** round courtyards.
  - Shali: an organic mound with no straight lines.
- **Streets:**
  - steep lanes 1.5–3 m, often covered for stretches (passing under houses), stepped;
  - ghorfa courtyards (20–40 m) as the public rooms, with external stairs climbing the vault faces;
  - a single gate in the outer wall.
- **Growth:**
  - E1: a granary on the hilltop.
  - E2: tower-houses fill the slope; ghorfa rings added in new courtyards.
  - E3: cement patches, tin doors, cement-rendered vaults.
  - E4: ghorfa cells reused as capsule rooms with glowing round doors, tower tops as lookouts with lights.
- **Openings:**
  - tiny slit windows below (0.2 × 0.5 m) and **palm-wood-grilled** windows above (0.5 × 0.8 m), often in pairs;
  - doors of palm planks, 0.8 × 1.8 m;
  - ghorfa doors: a small rectangle at the vault end, with palm-trunk lintel and a painted surround (blue, white).
- **Roofs:**
  - flat earth roofs on palm trunks and reeds;
  - **crenellated tower tops** (stepped merlons with pinnacles on the corners);
  - ghorfa vault tops rounded, walkable;
  - no domes except on Siwa's small mosque.
- **Ornament:**
  - relief panels on the top third of towers: rhombuses, chevrons, ladders, blind arches;
  - occasional whitewash outlines.
- **Public spaces:**
  - the ghorfa courtyard (markets and festivals);
  - the threshing floor (a round stone floor);
  - the riverbank palm gardens;
  - the mosque terrace.
- **Water:**
  - the river with palm gardens on the bank (Ounila, Draa);
  - wells with shadufs;
  - Siwa's **salt lakes and springs** (Cleopatra's spring: a round stone pool).
- **Plants:**
  - **date palm** groves (dense);
  - **tamarisk** (feathery grey-green shrubs 2–4 m);
  - **olive** (Siwa: groves, grey-green rounded 5 m);
  - acacia;
  - almond trees (pink-white in spring) in the Dades.
  - Nothing on roofs.
- **Cyberpunk overlay:**
  - Pisé walls with embedded light lines along the lift joints.
  - Ghorfa vault doors as glowing capsule portals.
  - Tower tops with signal lamps and dishes.
  - Solar shade sails over courtyards.
  - Minimal neon: earth tones and amber, plus one bright colour per family (granary marks).
- **Night:** rose-red towers floodlit amber from below, small lamps in the window pairs, the ghorfa honeycomb
  glowing door by door.

## Kit
- **Common pieces:**
  - `wall_panel` (pisé with lift lines, strong batter), `tower_corner_tapered`, `parapet_crenel` (pinnacle corners);
  - `window_small` (paired, palm grille), `door_plank`;
  - `vault_barrel` / `ghorfa_vault` cells, `stair_external` (steep);
  - `covered_alley`, palms, tamarisk, olive.
- **Parameters that make it a kasbah:**
  - strong taper;
  - towers at corners;
  - relief decoration only on the top third;
  - windows grow with height;
  - all one earth colour;
  - cells stacked in honeycombs with external stairs;
  - ruins mixed in.
- **Unique pieces (2):**
  - `relief_panel_earth` (chevron and lozenge recessed brick);
  - `ghorfa_cell` (it exists as `ghorfa_vault`).
