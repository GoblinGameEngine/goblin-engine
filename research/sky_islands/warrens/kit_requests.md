# Kit requests from the GENERATOR (warren families)

Written by `tools/sky/warren/kit_requests.py` from each civ module's SPEC (`tools/sky/warren/civ/`).
Frames as pieces.json (`wall`/`edge`: +Z out of the cell, face plane at z 0; `cell`: centred). The generator
uses the stand-in until the piece exists, then switches by id (tell it the id).

## All families

| piece | what | stand-in | status |
|---|---|---|---|
| `pave_*_skirt` | paving with a 0.6 m skirt down its four sides (or a riser piece): ground pieces stand flat at each cell's deck height, so on sloping streets the step between two cells shows a gap to the sky | none (gaps) | wanted |
| `edge_parapet_rounded_k (cheaper)` | the rounded merlon parapet at <= 60 tris; at 172 it is the first thing the budget pass sheds in every medina/Yemeni/M'zab chunk | edge_parapet_plain_k when over budget | wanted |

## andean_neo

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_inca_base_k` | an Inca polygonal fitted-stone ground bay, battered 5 deg, trapezoid doorway variant (wall) | wall_plain_k on the grey ground variant | in the kit |
| `wall_box_balcony_k` | Lima's carved enclosed box balcony (latticed, 1 m deep) (wall) | wall_balcony_timber_k / wall_bay_box_k | in the kit |
| `roof_tile_red_low` | a 25-30 deg red tile roof with wide eaves (cell roof) | flat roof | in the kit |
| `cholet_chalet_top` | the peaked chalet perched on a cholet's roof (crown) | none | in the kit |
| `ov_rebar_stubs` | rebar sticking up from an unfinished roof slab (roof decor) | none | in the kit |
| `cable_car` | Mi Teleférico gondola line and cabin (decor) | none | in the kit |

## cairene_mamluk

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_mashrabiya_box_k` | the turned-bead mashrabiya oriel stepping 0.25 m out per storey (wall) | wall_screen_k | in the kit |
| `wall_ablaq_portal_k` | striped ablaq pointed portal with a muqarnas hood (wall, door) | wall_arch_pointed_k | in the kit |
| `minaret_mamluk` | Mamluk minaret: square base, octagonal shaft, balconies, bulb top (3 parts) | minaret_base/shaft/top | wanted |
| `dome_ribbed` | ribbed carved stone dome on a drum (crown) | dome_cap | in the kit |
| `malqaf_scoop` | the roof wind scoop (roof decor) | minaret_base stub | in the kit |
| `pigeon_cote` | the mud pigeon tower on a roof (roof decor) | none | in the kit |
| `ov_mastaba` | the stone bench before a shop (face overlay, ground) | none | in the kit |

## caucasian_balcony

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_tbilisi_balcony_t (lighter)` | the carved balcony at <= 300 tris (692: shed to timber balconies when over budget) | wall_balcony_timber_t | wanted |
| `wall_shushabandi_t` | the small-pane stained-glass gallery (shushabandi) (wall, emissive glass) | wall_tbilisi_balcony_t | wanted |
| `svan_tower` | the Svan defensive stone tower 20-25 m with a slate gable top (base, shaft, top) | rooms (tower_cells 1) | wanted |
| `dome_bath_brick` | the low brick bath dome with a lantern (crown) | dome_cap | wanted |
| `stair_spiral_courtyard` | the spiral iron stair of an Italian courtyard (cell) | stair_spiral | wanted |

## chongqing_cliff

| piece | what | stand-in | status |
|---|---|---|---|
| `stair_street_long` | a stair street flight with a landing (Shibati), 3 m wide (stair, span [1, 2]) | steps + step_low | in the kit |
| `roof_tile_flying_eave` | grey tile roof with upturned eave corners, shallow pitch (cell roof) | green_hip + edge_eave_pagoda | in the kit |
| `wall_gallery_timber_t` | a continuous timber gallery with railings along a storey (wall) | wall_balcony_timber_t | in the kit |
| `skybridge_street` | a bridge from a street into a building's upper floor (cell) | none | in the kit |
| `ov_gold_eave_led` | the warm gold LED line traced along every eave (edge overlay, emissive) | none | in the kit |

## creole_colonial

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_window_medio_punto_k` | floor-to-ceiling window with turned bars, louvred shutters and a stained-glass medio punto lunette (emissive at night) | wall_window_l_k | in the kit |
| `wall_balcony_covered_k` | Cartagena's long covered timber balcony on corbels with turned balusters and a small roof | wall_balcony_timber_k | in the kit |
| `wall_door_carriage_k` | the zaguan carriage door with a small inset door, stone surround | wall_door_k | in the kit |
| `bell_tower_baroque` | a baroque bell tower (base, belfry, cupola crown) for the cathedral | minaret_base/shaft/top | wanted |
| `kiosco_gazebo` | the plaza bandstand gazebo (cell decor) | fountain_riad | in the kit |
| `edge_parapet_urns_k` | an azotea parapet with urns/balusters (edge) | edge_parapet_plain_k | in the kit |

## cycladic

| piece | what | stand-in | status |
|---|---|---|---|
| `chapel_cycladic` | the little white chapel with a blue dome and bell gable (crown over 1-2 cells) | minaret_base x2 + dome_cap | wanted |
| `windmill_round` | the round white windmill with sails (cell, 3 storeys) | none | wanted |
| `edge_parapet_lip_k` | the rounded whitewashed roof lip (edge, cheaper than parapet_rounded) | edge_parapet_rounded_k | wanted |
| `pave_slate_whitejoint` | slate paving with whitewashed joints (ground) | pave_lane | wanted |
| `stair_external_white` | the external whitewashed stair up a house face to the roof (face overlay) | none | wanted |

## ganga_ghat

| piece | what | stand-in | status |
|---|---|---|---|
| `ghat_steps_wide` | broad stone ghat steps down into the water with a landing (stair, span [1, 2], water side) | steps_up on banks | wanted |
| `shikhara_spire` | the nagara temple spire (curvilinear tower with amalaka and finial; base, shaft, top) | minaret_base/shaft/top | wanted |
| `ghat_umbrella` | the cane umbrella over a priest's platform on the steps (cell decor) | none | wanted |
| `chhatri` | the domed corner pavilion (roof crown) | arcade_pier + dome_cap | wanted |
| `ov_marigold_garland` | marigold garlands over a door / along a balcony (face overlay) | none | wanted |
| `band_flood` | the dark flood-mark band on the lower storeys (face overlay) | none | wanted |

## hakka_tulou

| piece | what | stand-in | status |
|---|---|---|---|
| `tulou_ring_wall` | a curved rammed-earth ring segment (outer face, stone base, slits) for rings of R 15-35 m (wall, curved) | straight earth bays on a cell ring | wanted |
| `tulou_gallery_ring` | the inner timber gallery ring with lattice doors (wall, curved) | wall_gallery_timber_t | wanted |
| `roof_ring_tile` | the continuous ring roof with a 2-3 m outer eave (roof, curved run) | roof_kawara_low runs | wanted |
| `tulou_gate` | the single massive gate with a stone frame (wall, door) | wall_door_portal_k | wanted |
| `ancestral_hall` | the central ancestral hall pavilion (crown) | roof_tile_flying_eave | wanted |

## hanseatic_gable

| piece | what | stand-in | status |
|---|---|---|---|
| `edge_gable_step` | a stepped (crow-step) gable front over a 1-bay house (used on every street front) | - | in the kit |
| `edge_gable_neck` | a neck gable with sandstone scrolls | - | in the kit |
| `edge_gable_bell` | a bell gable | - | in the kit |
| `roof_pitched_pantile` | a 50-60 deg pantile/slate roof run behind the gable, ridge along the house depth (cell, span [1, n]); the hip-per-cell stand-in reads as a field of pyramids from above | green_hip per cell | in the kit |
| `hoist_beam` | the attic hoist beam with hook over the luiken hatch column (face overlay at the top storey) | none | in the kit |
| `wall_luiken_k` | the attic hatch column bay: stacked shutters, white frame (wall) | wall_window_m_k | in the kit |
| `church_spire_copper` | a verdigris copper spire over a brick tower (crown) | green_hip on a minaret shaft | in the kit |
| `bridge_humped_brick` | a humped brick canal bridge with bulb strings (cell, span [1, 3]) | none | in the kit |
| `quay_edge_stone` | a stone quay edge with mooring rings (water_edge) | kerb_straight | in the kit |

## hejazi_roshan

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_roshan_k (lighter)` | the roshan at <= 250 tris: at 616 the budget pass turns most roshan columns back into windows | wall_window_m_k when over budget | wanted |
| `edge_mangour_k` | the 1.8 m mangour lattice roof parapet of Jeddah (edge) | edge_parapet_jali_k (one per house) | in the kit |
| `roshan_crest` | the carved wooden crest crowning a roshan column (face overlay) | none | in the kit |
| `wall_coral_bands_k` | coral-stone bay with the timber tie-beam bands every 1 m (wall) | wall_plain_k | in the kit |

## hk_neon_canyon

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_sign_arm_big` | a 2-6 storey neon sign on a steel arm over the street (face overlay, several storeys) | ov_sign_blade anchors | in the kit |
| `wall_verandah_t` | pre-war tong lau verandah bay: columns at the street edge, balcony over the pavement (wall) | wall_balcony_iron_t | in the kit |
| `wall_mosaic_t` | 1960s mosaic-tile panel bay (wall) | wall_plain_t | in the kit |
| `wall_window_casement_pair_t` | steel casement windows in pairs, green frames (wall) | wall_window_pair_t | in the kit |
| `ov_roller_shutter` | a half-down roller shutter over a shopfront (face overlay) | none | in the kit |

## iberian_white

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_reja_box_k` | window with a projecting box reja (iron grille 0.3 m out, pot shelf) in a thick white wall | wall_window_grille_t on a thick wall (leaves a reveal gap) | in the kit |
| `wall_door_studded_k` | iron-studded door in a stone or painted surround | wall_door_k | in the kit |
| `band_zocalo` | the ochre/blue painted base band 0.8 m (face overlay at ground) | none | in the kit |
| `ov_blue_pots` | blue pots hung on a white wall (face overlay) | ov_planter | in the kit |
| `roof_tile_roman_low` | low 15-20 deg Roman-tile roof (cell roof) | green_hip | in the kit |
| `tower_mudejar` | Mudejar brick tower with sebka lozenge panels and belfry (base, shaft, top) | minaret_base/shaft/top | wanted |
| `ov_toldo` | summer awning stretched across a shopping lane (along X) | ov_awning_cane | in the kit |

## japan_yokocho

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_sign_vertical_stack` | a column of lightbox signs, one per storey, on a zakkyo street face (face overlay spanning n storeys or one per storey) | ov_sign_blade anchors | in the kit |
| `ov_chochin_string` | lantern strings across alleys (used on 35% of lane spans) | - | in the kit |
| `wall_noren_t` | bar door with noren and lanterns (used on 40% of alley ground faces) | - | in the kit |
| `ov_vending_machine` | 1-3 glowing vending machines against a wall (face overlay, ground) | none | in the kit |
| `stair_steel_external` | the zakkyo's external steel stair (face overlay climbing one storey) | none | in the kit |
| `utility_pole` | concrete pole with transformer and wire bundles (cell decor) | ov_cables | in the kit |
| `torii` | a vermilion shrine gate (cell, span [1, 1]) | none | in the kit |
| `roof_kawara_low` | a low grey kawara tile roof for 2-storey machiya (cell roof with eaves) | green_hip on low roofs | in the kit |
| `wall_koshi_t` | a machiya bay with the koshi timber lattice (wall) | wall_screen_t | in the kit |

## jiangnan_water

| piece | what | stand-in | status |
|---|---|---|---|
| `edge_horsehead_wall` | the stepped horse-head firewall at a house end, white with black tile copings (edge, gable end) | none | wanted |
| `roof_black_tile_curved` | black double-pitched tile roof, gentle curve, upturned ridge ends (cell roof run + end) | roof_kawara_low | wanted |
| `wall_shopboards_t` | the full-width removable timber shop boards (wall, ground) | wall_screen_t | wanted |
| `wall_moon_gate` | a round moon gate in a garden wall (passage) | wall_arch_round | wanted |
| `bridge_humpback_stone` | the humpbacked stone canal bridge (bridge, span [1, 3]) | none | wanted |
| `water_steps_private` | the private stone steps from a house down into the canal (stair, water side) | step_low_4 | wanted |

## karachi

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_tank_drum` | the black/blue plastic water-tank drum, clustered on roofs (roof overlay) | ov_tank | wanted |
| `wall_jharokha_k` | Gizri-stone jharokha bay on carved brackets (wall) | wall_bay_box | wanted |
| `wall_veranda_gothic_t` | colonial Indo-Gothic arcaded veranda storey (wall) | wall_arch_pointed | wanted |
| `ov_truck_art_panel` | a truck-art painted panel / shutter (face overlay, emissive) | none | wanted |
| `ov_wedding_curtain` | wedding fairy-light curtain down a facade (face overlay, emissive) | none | wanted |
| `edge_parapet_date_plaque` | a balustrade parapet with urns and a date plaque (edge) | edge_parapet_plain_t | wanted |

## knights_harbour

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_gallarija_k` | the gallarija: an enclosed painted timber balcony 1-1.4 m deep, glazed, stacked, wrapping corners (wall) | wall_balcony_timber_k | wanted |
| `corner_statue_niche` | a saint in a niche at a street corner, lit at night (corner) | corner_quoin_k | wanted |
| `stair_knight` | the knight's stair-street: low risers 0.1 m, deep treads, 3-5 m wide (stair, span [1, 2]) | steps | wanted |
| `bastion_wall_slope` | the sloped bastion wall at the island rim (wall, 2 storeys) | none | wanted |

## korean_hillside

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_jangdok_jars` | a cluster of brown soy-sauce jars on a roof (roof decor) | foliage stand-in | wanted |
| `roof_painted_green` | the green-painted waterproofed flat roof (cell roof) | roof_terrace | wanted |
| `oktapbang` | the rooftop room box with a small door and window (roof overlay) | E5 roof huts (ov_shack) | wanted |
| `wall_mural_t` | a mural-painted blank wall (wall) | wall_plain_t | in the kit |
| `stair_street_long` | the long straight stair street (exists: placed by the slope rule when it lands) | steps | in the kit |

## kulla_stone

| piece | what | stand-in | status |
|---|---|---|---|
| `roof_stone_slab_steep` | the 30-35 deg hip roof of stone slabs (mosaic, lichen) with deep timber eaves (cell roof run + end) | green_hip per cell | wanted |
| `wall_window_band_k` | the corbelled top storey: a continuous window band, 50% glass, timber, on corbels (wall) | wall_window_pair_k | wanted |
| `wall_arrow_slit_k` | an arrow-slit window in the fortress base (wall) | wall_window_s_k | wanted |
| `chimney_stone` | the tall stone chimney stack (roof decor) | none | wanted |
| `ov_machicolation` | a machicolation box over the door (face overlay) | none | wanted |

## latin_hillside

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_rebar_stubs` | rebar stubs sticking up at a laje's columns (roof decor) | none | in the kit |
| `ov_tank_round_blue` | the round blue fibreglass roof water tank (overlay; metal slot blue) | ov_tank | in the kit |
| `wall_brick_raw_t` | a hollow clay brick infill bay in a concrete frame (wall) | wall_plain_t raw-brick palette | in the kit |
| `wall_mural_t` | a mural-painted blank bay (wall, emissive-free) | wall_plain_t | in the kit |
| `stair_painted` | a concrete stair flight with each step a colour, handrails (stair) | stair_run | in the kit |
| `wall_tin_corrugated_t` | Valparaiso corrugated-iron cladding bay (wall) | wall_plain_t | in the kit |
| `cable_car` | cable car line + cabin over the hill (decor, later) | none | in the kit |

## levantine_courtyard

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_jetty_t (lighter)` | the timber jetty at <= 250 tris (622 now: the budget pass turns many into windows) | wall_window_m_t when over budget | wanted |
| `wall_ablaq_portal_k` | black-and-white striped pointed portal with a muqarnas hood (wall, door) | wall_arch_pointed_k | in the kit |
| `wall_liwan_k` | the liwan: a tall pointed arch opening a whole storey and a half to the court (wall, 2 storeys) | wall_arch_pointed_k | in the kit |
| `dome_stone_low` | Jerusalem's low walkable stone roof dome (crown) | dome_cap | in the kit |
| `ov_suq_canopy` | a covered-suq vault/canopy across an artery (along X) | ov_awning_cane | in the kit |

## lusitanian_hill

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_azulejo_k` | a facade bay fully clad in patterned azulejo tiles (tile slot), tall window with an iron cage balcony (wall) | wall_balcony_iron_k on the tile-coloured variants | wanted |
| `wall_granite_window_k` | a tall window in a granite frame (wall) | wall_window_l_k | wanted |
| `roof_dormer_attic` | the aguas-furtadas attic dormer on a tile roof (roof decor) | none | wanted |
| `pave_calcada` | calcada portuguesa black-and-white mosaic paving (ground) | pave_plaza | wanted |
| `tram_rail` | tram rails in the street with a tram (decor along X) | none | wanted |
| `miradouro_kiosk` | a miradouro kiosk with a pergola (cell decor) | none | wanted |

## manila_estero

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_capiz_t` | the capiz-shell sliding window storey over balustered ventanillas, timber, overhanging (wall) | wall_screen_t | wanted |
| `wall_adobe_ground_k` | the adobe/stone ground storey of a bahay na bato (wall) | wall_plain on the stone variant | wanted |
| `ov_shanty_gi` | a plywood and galvanized-iron shanty box on stilts with tyres on the roof (roof/cell overlay) | ov_shack + stilts | wanted |
| `basketball_court` | a half basketball court with hoop (cell decor, 2x3) | ov_playground | wanted |
| `ov_jeepney` | a parked jeepney (street decor) | none | wanted |

## mardin_terraces

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_triple_arch_loggia_k` | the triple-arched south loggia of an upper eyvan (wall) | wall_arch_pointed_k | wanted |
| `edge_balustrade_carved_k` | the carved stone balustrade round a roof terrace (edge) | edge_parapet_jali_k | wanted |
| `abbara_vault` | the vaulted tunnel carrying a lane under a house (ceiling + portal) | sabat_beams + arch mouth | wanted |
| `wall_carved_frame_k` | a pointed window in a carved frame with a geometric grille (wall) | wall_window_grille | wanted |
| `minaret_square_carved` | the square carved Artuqid minaret (3 parts) | minaret_base/shaft/top | wanted |

## mughal_walled

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_jharokha_bangla_k` | the jharokha with a curved bangla roof on carved brackets (wall) | wall_bay_box_k | wanted |
| `edge_chhajja` | the deep stone chhajja eave over every storey (edge overlay at the storey top) | none | wanted |
| `chhatri` | the domed corner pavilion on four columns (roof crown) | arcade_pier + dome_cap | wanted |
| `wall_cusped_arch_k` | the cusped (multifoil) arch bay (wall) | wall_arch_pointed_k | wanted |
| `dome_bulbous_marble` | the bulbous white marble dome with finial (crown) | dome_cap | wanted |
| `ov_wire_net` | the overhead tangle of wires over a gali at storey 2-3 (along X) | ov_cables | wanted |

## mzab_ghadames

| piece | what | stand-in | status |
|---|---|---|---|
| `edge_parapet_horn_k` | Ghadames/M'zab parapet with whitewashed triangular corner horns (trim slot) | edge_parapet_rounded_k | in the kit |
| `minaret_pyramid` | the M'zab minaret: square battered truncated pyramid 15-25 m, four corner horns on top (3 parts: base, shaft taper, horned top) | minaret_base x5 + minaret_top | wanted |
| `dukkana_bench` | a mud bench along a covered-lane wall (face overlay at ground) | none | in the kit |
| `well_pulley` | a well with a timber pulley frame (cell decor) | fountain_riad | in the kit |
| `wall_triangles_k` | a door bay with painted red/green triangles and diamonds round it (Ghadames) | wall_door_k | in the kit |
| `lightwell_shaft` | the light-well opening in a covered-lane ceiling (ceiling piece with a lit hole) | sabat_beams | in the kit |

## newar

| piece | what | stand-in | status |
|---|---|---|---|
| `pagoda_temple_tiers` | a 3-5 tier pagoda temple on a stepped plinth (the roof_pagoda over a multi-storey base) | roof_pagoda on the civic lot | in the kit |
| `hiti_sunken` | the sunken stone water spout court (ground, below deck) | none | in the kit |
| `stupa` | a whitewashed stupa with painted eyes (cell decor) | none | in the kit |
| `roof_tile_hip_struts` | clay-tile hip roof on carved struts over a row house (cell roof) | green_hip + edge_eave_pagoda | in the kit |
| `wall_brick_herringbone` | the herringbone brick paving (ground) | pave_lane | in the kit |
| `ov_prayer_flags` | prayer flag strings across lanes and squares (along X) | ov_festoon | in the kit |

## nouvelle_france

| piece | what | stand-in | status |
|---|---|---|---|
| `roof_tin_steep` | a 50-60 deg standing-seam tin roof with a dormer row (cell roof, span along the house; stand-in green_hip) | green_hip | in the kit |
| `edge_firewall_gable_k` | the Quebec firewall gable with a massive chimney stack and corbels (edge, roof top) | none | in the kit |
| `edge_cornice_pressed` | the plex pressed-metal cornice and parapet (edge) | edge_parapet_plain_k | in the kit |
| `stair_plex_outdoor` | Montreal's twisting outdoor iron stair from the pavement to the 2nd-storey door (cell, span [1, 1]) | stair_spiral | in the kit |
| `ov_snow_cap` | snow lying on a roof edge / sill (edge overlay) | none | in the kit |
| `wall_window_casement_k` | small many-paned casement with interior shutters in rubble stone (wall) | wall_window_m_k | in the kit |

## omani_oasis

| piece | what | stand-in | status |
|---|---|---|---|
| `edge_parapet_triangle_k` | Omani triangle merlons along a parapet (edge) | edge_parapet_crenel_k | wanted |
| `wall_beam_ends_k` | earth bay with a row of projecting palm-beam ends at the floor line (wall) | wall_plain_k | wanted |
| `wall_door_omani_k` | carved studded double door painted blue/green in a lintel frame (wall) | wall_door_k | wanted |
| `fort_round_tower` | Nizwa's great round fort tower, battered, crenellated (3 parts) | minaret_base x6 + minaret_top | wanted |
| `ground_falaj` | lane paving with the falaj channel down its middle (ground; water slot) | pave_lane | wanted |
| `ov_arish_shade` | palm-frond arish shade on poles (roof/lane overlay) | ov_awning_cane | wanted |

## ottoman_timber

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_jetty_t (lighter)` | the jettied storey at <= 250 tris (622: the budget pass turns most into windows) | wall_window_m_t when over budget | wanted |
| `wall_cumba_t` | the three-sided cumba oriel on brackets (wall) | wall_jetty_t | wanted |
| `wall_kafes_t` | sash windows behind kafes lattice (wall) | wall_window_pair_t | wanted |
| `wall_himis_t` | timber-frame bay with plaster infill (himis) or clapboard (wall) | wall_plain_t | wanted |
| `eave_soffit_deep` | the 1.0-1.5 m eave with a boarded soffit under a low hip (edge) | edge_eave_tin | wanted |
| `cesme_fountain` | the stone wall fountain with a trough (face overlay) | wall_fountain_k | wanted |

## persian_desert

| piece | what | stand-in | status |
|---|---|---|---|
| `badgir` | the wind tower: a square shaft 3-30 m with vertical slot vents and a crown; 1-, 2-, 4- or 8-sided (base, shaft, crown) | minaret_base stacks 1-3 storeys | wanted |
| `roof_vault_barrel` | a walkable mud-brick barrel vault roof over a cell (cell roof) | roof_terrace | wanted |
| `dome_mud` | a plain mud-brick dome with an oculus (crown) | dome_cap | wanted |
| `wall_orsi_k` | the orsi: a sash window of coloured glass in a wooden grid, glowing (wall, court side) | wall_screen_k | wanted |
| `wall_portal_knockers_k` | the street portal: a recessed door with two knockers and a bench niche (wall, door) | wall_door_k | wanted |
| `wall_talar_k` | the iwan/talar opening a full storey to the court with two columns (wall) | wall_arch_pointed_k | wanted |

## rajput_sandstone

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_jharokha_canted_k` | the canted octagonal carved sandstone jharokha with a domed top (wall) | wall_bay_box_k | wanted |
| `wall_jali_carved_k` | a full-bay finely carved stone jali screen, backlit at night (wall) | wall_screen_k | wanted |
| `chhatri` | the domed corner pavilion on four columns (roof crown) | arcade_pier + dome_cap | wanted |
| `bastion_round` | the fort's round crenellated bastion (3 parts) | minaret_base + dome_cap | wanted |
| `edge_parapet_jali_k (lighter)` | the jali parapet at <= 150 tris (456 now: the budget pass turns them plain) | edge_parapet_plain_k when over budget | wanted |

## rupestrian_terraces

| piece | what | stand-in | status |
|---|---|---|---|
| `vault_roof_hump` | the whitewashed barrel/cross vault hump over a rock-cut cell (cell roof) | dome_cap at 8% | wanted |
| `wall_cave_door_k` | deep arched door with a lunette into a rock-cut vault (wall, ground) | wall_arch_round_k | wanted |
| `rock_face_cut` | the raw rock face the cells are cut into (wall, rock material) | wall_plain_k | wanted |
| `cistern_well` | the vicinato cistern well head (cell decor) | none | wanted |
| `lemon_pergola` | a vine/lemon pergola on posts over a roof terrace (roof decor) | grapevine_pergola foliage | wanted |

## saharan_kasbah

| piece | what | stand-in | status |
|---|---|---|---|
| `tower_kasbah_corner` | the tapering earth corner tower with pinnacled crenel top and relief panels (base, shaft, top) | rooms + edge_parapet_crenel_k | wanted |
| `wall_earth_relief_k` | earth wall bay with chevron/lozenge relief in the top third (wall) | band_brick_relief overlay | in the kit |
| `ghorfa_cell` | the vaulted ghorfa granary cell with a small painted door, stackable 3-6 high round a court (cell) | rooms | in the kit |
| `wall_slit_k` | a defensive slit window in a thick earth wall (wall) | wall_window_s_k | in the kit |
| `edge_parapet_pinnacle_k` | crenel parapet with pinnacle corners (edge) | edge_parapet_crenel_k | in the kit |

## scots_lands

| piece | what | stand-in | status |
|---|---|---|---|
| `roof_slate_steep` | steep 45-55 deg slate roof run (cell roof run + end) | roof_pitched_pantile | wanted |
| `chimney_stack_pots` | the many-pot chimney stack on a gable (roof decor) | minaret_base stubs | wanted |
| `turret_stair_conical` | the turnpike stair tower with a conical slate cap (corner tower) | none | wanted |
| `wall_pend_k` | the arched pend: a close entering under a land (passage) | wall_arch_round_k | wanted |
| `crown_spire` | St Giles' crown spire (crown) | church_spire_copper | wanted |
| `mercat_cross` | the mercat cross on its octagonal base (cell decor) | none | wanted |

## siam_khlong

| piece | what | stand-in | status |
|---|---|---|---|
| `roof_thai_gable` | the steep (45 deg+) teak-house gable roof with curling chofa finials (cell roof run + end) | roof_pitched_pantile | in the kit |
| `wall_teak_panel_t` | teak plank bay with a wide panel window hinged to swing out (wall) | wall_screen_t | wanted |
| `pier_steps_khlong` | the pier and steps down from a stilt house into the canal (stair, water side) | step_low_4 on banks | wanted |
| `temple_tiered_roof` | the wat's tiered layered roof with naga gables (crown) | roof_pagoda | wanted |
| `ov_gold_shop_neon` | the big vertical gold-shop neon signs of Yaowarat (face overlay) | wall_sign_column_t | wanted |

## silk_road

| piece | what | stand-in | status |
|---|---|---|---|
| `portal_pishtaq` | the monumental tiled portal 15-30 m (Registan): a tall pointed iwan in a tiled frame (wall, 3-5 storeys) | wall_zellij_k + blind arches | wanted |
| `minaret_round_tapered` | round tapering brick minaret with tile bands and a lantern (base, shaft, top) | minaret_base/shaft/top | wanted |
| `dome_turquoise_ribbed` | the ribbed turquoise tile dome on a drum (crown, tile slot) | dome_cap | wanted |
| `aivan_column` | the carved wooden column of the aivan porch (corner/decor) | corner_column | wanted |
| `tapchan` | the raised bed-platform of the chaikhana by the hauz (cell decor) | none | wanted |
| `dome_bazaar_crossing` | the domed bazaar crossing (taq) over a lane junction (cell crown over a passage) | none | wanted |

## straits_shophouse

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_five_foot_way_t` | the shophouse ground bay with the covered five-foot way (column at the street edge, arcade behind, pintu pagar shopfront) (wall) | wall_shopfront_b_t | wanted |
| `wall_casement_louvre_t` | a pair/triplet of full-height timber casements with louvres, stucco frame (wall) | wall_window_pair_t | wanted |
| `band_peranakan_tile` | the glazed Peranakan tile dado (face overlay, tile slot) | none | wanted |
| `edge_firewall_gable` | the stepped gable firewall between units (edge on the roof) | none | wanted |
| `temple_chinese_roof` | the Chinese temple roof with swallowtail ridges and porcelain dragons (crown) | roof_tile_flying_eave | wanted |

## taipei_tiepi

| piece | what | stand-in | status |
|---|---|---|---|
| `ov_tiepi_house` | the 1-2 storey corrugated iron rooftop house with a pent roof (roof overlay, bigger than ov_shack) | ov_shack_a/b/c | in the kit |
| `wall_qilou_t` | the qilou arcade bay: a column at the street edge, the arcade behind, a shopfront at the back (wall) | wall_shopfront_b_t | in the kit |
| `wall_tile_t` | small ceramic tile cladding bay (wall) | wall_plain_t | in the kit |
| `ov_water_tower_steel` | the stainless water tower on legs (roof) | ov_tank | in the kit |

## tibetan_lhasa

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_battered_k` | the battered (5-8 deg) whitewashed stone bay (wall) | wall_plain_k | wanted |
| `wall_window_trapezoid_k` | the window in a black trapezoid surround with tiered painted lintels and a pleated valance (wall) | wall_window_m_k | wanted |
| `edge_pembe_frieze` | the maroon twig (pembe) frieze under a parapet (edge band) | crown_band | wanted |
| `ov_prayer_flag_pole` | the prayer-flag pole at a roof corner (corner decor) | ov_antennas | wanted |
| `ov_prayer_flags` | prayer flag strings across lanes and roofs (along X) | ov_festoon | in the kit |
| `incense_burner` | the big whitewashed incense burner on the kora (cell decor) | fountain_riad | wanted |
| `roof_gilded_temple` | the gilded temple roof with victory banners (crown) | green_hip | wanted |

## tyrrhenian_canyon

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_basso_t` | the basso: a glazed street door into a one-room home, a chair outside (wall, ground) | wall_door | wanted |
| `ov_wall_shrine` | a wall shrine (edicola) with a lamp and flowers at a corner (face overlay, emissive) | none | wanted |
| `wall_french_balcony_k` | tall french window, green louvred shutters, shallow iron balcony (wall) | wall_balcony_iron_k | wanted |
| `ov_laundry_line_lane` | laundry lines across a vicolo between opposite balconies (along X) | ov_laundry | wanted |
| `band_damp` | the dark damp band 0-1.5 m on the ground storey (face overlay) | none | wanted |

## viet_tube

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_french_door_balcony_t` | full-height french doors with louvred shutters onto a narrow balcony full of pots (wall) | wall_balcony_iron_t | wanted |
| `ov_wire_tangle` | the knotted wire tangles on the street poles (cell decor) | utility_pole | wanted |
| `wall_side_ad_t` | a painted advertisement on a blank side wall (wall) | wall_plain_t | wanted |
| `ov_roof_shrine` | the small rooftop ancestor shrine (roof decor, emissive) | none | wanted |
| `bridge_red_lake` | the red wooden bridge to the lake island (bridge, span [1, 3]) | none | wanted |

## yemeni_tower

| piece | what | stand-in | status |
|---|---|---|---|
| `wall_door_carved_k` | heavy carved wooden door 1.2 x 2.2 m in a white gypsum frame, basalt surround | wall_door_k | in the kit |
| `wall_window_grille_k` | small grilled window in a thick (0.6 m) basalt ground storey | wall_window_s_k | in the kit |
| `edge_parapet_crenel_white_k` | the stepped Sana'a merlon in white gypsum (trim slot) | edge_parapet_rounded_k | in the kit |
| `band_brick_relief` | brick relief band per storey (used: 45% of upper faces from the 2nd storey) | - | in the kit |
| `wall_gypsum_window_k` | gypsum-framed window with small qamariya (used) | - | in the kit |
| `minaret_brick_round` | Sana'a minaret: round brick shaft with relief bands, gallery and white top | minaret_base/shaft/top | wanted |
| `drain_spout` | a 0.6 m timber roof spout (decor on a roof edge) | none | in the kit |
| `skybridge_timber` | a 1-cell enclosed bridge between towers at an upper storey (Shibam) | sabat rooms | in the kit |

