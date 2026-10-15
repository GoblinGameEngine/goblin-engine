# Warren research 1: the Middle East, North Africa, Persia, Central Asia and South Asia

**Index and shared kit vocabulary (2026-10-15)**

Written for the warren generator in research/sky_islands/warrens/00_brief.md. Each family below is one island
culture: a construction language that grows as a city, not a facade style.

The user's rule is that new geometry only means new pieces in the shared parts library. So every family
specifies:
1. which **common pieces** it uses;
2. the **parameters** that make those common pieces read as that civilization: proportion, depth, rhythm, colour,
   material and weathering;
3. a small set of **unique pieces**, used only where nothing common can be bent to fit.

The machine-readable version is `r1_grammars.json`.

Measurements: where no source gives a number, a working value is marked `(est.)`. The estimates come from
standard dimensions of these building traditions, measured off typical photographs and plans.

## The families (15)

| id | Name | Sources (main) | One-line mark |
|---|---|---|---|
| yemeni_tower | Yemeni highland tower city | Sana'a, Shibam, Thula, Hadhramaut | 5–9 storey earth and brick towers, white gypsum frames, glowing qamariya fanlights, gardens inside the walls |
| hejazi_roshan | Red Sea coral-stone port | Jeddah al-Balad, Suakin (comparative) | white coral towers wrapped in stacked teak roshans, painted green, blue or brown |
| omani_oasis | Omani falaj oasis town | Bahla, Nizwa, al-Hamra, Misfat, Muttrah | ochre mud-brick harat behind a sur wall, palm-trunk roofs, falaj channels running down the lanes |
| levantine_courtyard | Levantine stone courtyard city | Old Damascus, Aleppo, Jerusalem | blank stone and ablaq ground floors, jettied timber upper storeys on brackets, citrus courtyards, domed and vaulted roofscape |
| cairene_mamluk | Cairene Mamluk–Ottoman quarter | al-Gamaliyya, Darb al-Asfar, Bab Zuwayla | mashrabiya oriels stacked over the street, malqaf wind scoops, minarets and ribbed stone domes, wikala blocks |
| maghrebi_medina | Maghrebi medina | Fez el-Bali, Marrakesh, Tunis | windowless derb walls, riad courtyards with orange trees, green-tiled roofs, sabat tunnels, zellige |
| mzab_ghadames | Saharan whitewash oasis (M'zab, Ghadames) | Ghardaïa, Beni Isguen, Ghadames | cubic houses climbing a cone to a pyramid minaret, roof-street for women, covered sabat ground lanes |
| saharan_kasbah | Pre-Saharan earth kasbah and ksar | Aït Benhaddou, Draa/Dades, Ksar Ouled Soltane, Siwa (Shali) | tapered pisé towers with relief at the top, stacked ghorfa vault cells, salt-mud kershef |
| persian_desert | Persian desert city | Yazd, Kashan, Abarkuh | sabat-covered kucheh, badgir forest, sunken courtyards, mud-brick domes and vaults, qanat water |
| silk_road | Central Asian Silk Road city | Bukhara, Khiva, Kashgar, Herat | flat earth roofs with aivan porches on carved columns, hauz pools under mulberries, turquoise domes, Uyghur balconies |
| karachi | Karachi (Sindhi port metropolis) | Kharadar, Mithadar, Saddar, Lyari, Orangi | yellow Gizri stone colonial blocks under concrete add-ons, jharokhas, truck-art neon, rooftop water tanks, cable canyons |
| mughal_walled | North Indian Mughal walled city | Shahjahanabad (Old Delhi), Lahore Walled City, Old Dhaka | haveli gates and courtyards, katra/kucha dead ends, chhajja eaves and jharokhas, bazaar arteries, wire nets |
| rajput_sandstone | Rajput desert sandstone city | Jaisalmer fort and town, Bikaner | honey-gold sandstone everything, carved stone jharokhas and jali, terraces under chhatri domes |
| ganga_ghat | River-ghat sacred city | Varanasi (Kashi), Maheshwar, Pushkar | the city as a cliff of stepped palaces down to water, ghats, galis 1–2 m wide, shrines in every wall |
| newar | Newar city of the Kathmandu valley | Bhaktapur, Patan, Kathmandu (Asan, Indra Chowk) | red brick with carved black-wood windows, tiered pagoda roofs, bahal courtyards, sunken hiti fountains, pati shelters |

## Shared kit vocabulary

Every family is built from these pieces. The ids reuse `research/sky_islands/architecture/components.json`
where possible.

- **Mass and walls**
  - `wall_panel`: a bay-wide wall slab. Parameters: material, thickness 0.3–1.5 m, batter (taper per metre of
    height), render (none, lime or mud), corner radius (soft earth corners), weathering mask.
  - `base_course`: a plinth or socle band. Parameters: material, height.
  - `band`: a horizontal string band. Parameters: kind (plaster, ablaq, brick relief, tile), height and colour.
  - `cornice` / `parapet_*`: plain, crenel (stepped merlons), rounded (sculpted earth), screen (pierced) and jali.
  - `tower_corner_tapered`: kasbah and Shibam corners. `tower_square`, `minaret_small`, `minaret_pyramid`,
    `bell_tower`.
- **Openings**
  - `arch_opening`: profiles rect, round, pointed, horseshoe, lobed, cusped, ogee, Tudor, flat lintel.
  - `door_*`: studded, plank, painted, shutter-front.
  - `shutters`, `window_small`, `window_arched`, `qamariya_fanlight`, `transom`.
- **Projections**
  - `bay_window_box`: the generic projecting box. Parameters: depth, height, roof shape, frame and lattice.
    `mashrabiya_box`, `roshan_bay` and `jharokha` are presets of it.
  - `balcony_cantilever` / `balcony_iron` / `balcony_timber_covered` / `gallery_timber`.
  - `chhajja` (a stone or timber eave on brackets), `bracket_corbel`, `jetty_upper` (a whole storey oversailing).
  - `awning`: tin, cloth or noren.
- **Screens:** `screen_lattice`, with patterns mashrabiya turned-bead, jali star or hex, roshan slat, brick
  honeycomb and Newar latticework.
- **Roofs**
  - `roof_flat_terrace` with drains (spouts).
  - `dome_small` (brick or stone), `dome_ribbed`, `dome_onion` (only where native).
  - `vault_barrel` (ghorfa, souk), `cross_vault_roof` (Jerusalem).
  - `roof_pagoda_tier` (Newar), `chhatri`.
  - `rooftop_shack`, `rooftop_stair_head`.
- **Climate pieces:**
  - `badgir` (windcatcher; parameters: plan square or octagonal, sides 1/2/4/8, height 3–30 m);
  - `malqaf` (a single-sided scoop);
  - `skylight_dome` (souk oculus).
- **Connections**
  - `sabat_bridge`: a room or passage over a lane.
  - `covered_alley`: a tunnel with an arch at each end.
  - `stair_external`, `stair_spiral_external`, `ladder_roof`, `plank_bridge`, `ghat_steps`.
- **Water:** `fountain_basin` (bahra), `hauz_pool`, `falaj_channel`, `qanat_ab_anbar` (a cistern dome with towers),
  `hiti_sunken` (stepped sunken spout), `pond_tank`.
- **Plants:** `tree_<species>`, `palm_<species>`, `vine_trellis`, `pot_cluster`, `planter_wall`, `roof_garden_bed`.
  The species are listed per family.
- **Street furniture:** `lantern` (wall or hanging), `market_stall`, `bench_platform` (dabali, mastaba),
  `wall_shrine`, `water_jar_stand` (sabil).
- **Cyberpunk overlay (shared):**
  - `cable_bundle` (catenary runs between facades), `ac_unit`, `satellite_dish`, `water_tank` (plastic drums,
    the Pakistan and India 500–1000 l black or blue tanks);
  - `solar_panel`, `antenna`, `rebar_stubs`, `tin_shack`, `scaffold`;
  - `led_screen`, `neon_frame`, `sign_blade`, `sign_board`, `lightbox`, `dot_matrix_board`, `festoon`, `fairy_lights`.

## How a family grows (the shared growth model)

Every family uses the same five-era accretion. Each era has its own material and colour palette and its own
probabilities for what gets added:

| Era | What happens |
|---|---|
| E0 founding | The founding street skeleton (arterials and gates), the oldest monuments, wells and channels. Native masonry at its thickest. |
| E1 classical | Courtyard or tower houses fill the blocks along the street pattern. Ornament peaks. |
| E2 dense | Upper storeys are added; rooms bridge lanes (sabat); courtyards are partly roofed or infilled; dead ends multiply as blocks subdivide. |
| E3 modern (20th century) | Concrete frame storeys on the old walls, iron balconies, shutters, shop fronts cut into ground floors, water tanks, wires. |
| E4 cyberpunk (the Aloft's own) | Light skystone panels, tin and plastic shacks on roofs, cantilevered boxes, bridges at roof level, LED screens, neon, cable canyons. |

The share of each era and the order of addition are family parameters (`growth` in the JSON). Earth cities keep
E1 dominant; Karachi and the Mughal walled cities are mostly E2 and E3; Kowloon-like density comes from E2 to E4.

## Street hierarchy (shared, after Islamic urban law)

The jurists' four classes are a usable generator rule (see the sources in `r1_levantine_courtyard.md` and
`r1_maghrebi_medina.md`):
1. **Arterial (shari'):** public right of way, at least two loaded animals wide (3.2–3.5 m, by decree), usually
   souk-lined, gate to gate.
2. **Secondary lanes (darb or zuqaq):** 2–3 m, linking quarters.
3. **Quarter lane:** 1.5–2.5 m, semi-private, often gated at its mouth.
4. **Cul-de-sac (impasse, kucha, katra):** 1–2 m, private to the houses it serves.

Two legal rules shape the form:
- **The fina' rule:** the owner of a house controls the space in front of it, up to half the width of a public
  street, and all of it in a cul-de-sac. That is what permits benches, projections and the **sabat** (a room
  built over a lane when one owner holds both sides, or on columns against the other wall).
- **Cul-de-sacs can be privatised and subdivided.** So E2 growth means more dead ends and more sabats.

The game additions: each island keeps 1–2 **grand paved axes** (the user's "large paved main streets"), 8–14 m,
running gate to gate through a plaza. Every family names its own type of public space (souk, maidan, chowk,
ghat, bahal, sahn).
