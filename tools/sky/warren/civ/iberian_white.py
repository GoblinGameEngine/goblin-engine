"""Iberian white towns (r3_iberian_white.md: Andalusian pueblos blancos, Cordoba, Toledo, Cuenca).

The mark: introverted whitewashed courtyard houses packed into irregular blocks along 1.5-3.5 m lanes that bend every
10-20 m and climb in ramps, walls straight up with few openings: box rejas (projecting iron grilles), studded doors,
blue pots on white walls, an ochre or blue zocalo; cobertizos bridging the lanes; patios with horseshoe arches and
orange trees; low Roman-tile roofs; a Mudejar brick tower over the plaza mayor."""
from civ.family import FamilyCiv


class IberianWhite(FamilyCiv):
    id = "iberian_white"
    name = "Iberian white town"
    arch_mouth = "wall_arch_horseshoe"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 6), "lane_spacing": 5, "lane_len": 15, "branch": 0.4, "loop": 0.35, "artery_share": 0.25,
            "block_cells": 11, "cut_turn": 4.0, "lot_cells": (6, 16), "courts": True, "court_min_lot": 9,
            "court_share": 0.18, "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 2, "sabat_from": 1,
            "work_share": 0.15, "civic_min_cells": 10, "tower_levels": (4, 5), "tower_cells": 2,
            "epochs": {2: {"rise": 0.35, "setback": 0.35, "sabat": 0.18},
                       3: {"rise": 0.25, "setback": 0.4, "sabat": 0.2, "tower": 0.01},
                       4: {"rise": 0.15, "setback": 0.5, "sabat": 0.12}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.4, "street_blades": 0.04,
            "shacks": 0.01, "shop_share": 0.45,
        },
        "civic_court": True,
        "variants": (0.3, 0.25, 0.25, 0.2), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door_studded_k",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_reja_box_k", 0.4), ("wall_door", 0.15), ("wall_plain", 0.45)],
                       "lane": [("wall_reja_box_k", 0.32), ("wall_plain", 0.68)],
                       "court": [("wall_arch_horseshoe", 0.7), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_reja_box_k", 0.3), ("wall_balcony_iron", 0.18), ("wall_bay_box", 0.05),
                                 ("wall_plain", 0.47)],
                      "lane": [("wall_reja_box_k", 0.25), ("wall_balcony_iron", 0.08), ("wall_plain", 0.67)],
                      "court": [("wall_arch_horseshoe", 0.3), ("wall_balcony_iron", 0.2), ("wall_window_m", 0.5)]},
            "civic_ground": [("wall_blind_arch", 0.5), ("wall_plain", 0.5)],
            "civic_upper": [("wall_blind_arch", 0.4), ("wall_plain", 0.6)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain",
                 "pitched": {"run": "roof_tile_roman_low", "end": "roof_tile_roman_low_end", "share": 0.5, "civic": True}},
        "marks": [{"type": "civic_tower", "pieces": ["tower_mudejar_shaft", "tower_mudejar_shaft", "tower_mudejar_belfry", "tower_mudejar_top"], "storeys": 5},
                  {"type": "fountain"}],
        "overlay": {"face_items": [{"piece": "band_zocalo", "p": 0.6}, {"piece": "ov_blue_pots", "p": 0.12, "where": "upper"}],
                    "spans": [("ov_toldo", 0.12)], "wall_pots": 0.0, "lantern": 0.45, "awning": 0.4, "cable": 0.08, "dish": 0.1, "laundry": 0.05},
        "foliage": {"court": ["bitter_orange", "pot_geranium", "jasmine"], "plaza": ["bitter_orange", "date_palm"],
                    "green": ["bitter_orange", "cypress", "date_palm", "olive"], "bank": ["cypress", "reeds"],
                    "lane_wall": ["bougainvillea", "jasmine"], "roof": ["pot_geranium"],
                    "rates": {"court": 0.6, "plaza": 0.1, "lane_wall": 0.08}},
        "kit_requests": [
            ("wall_reja_box_k", "window with a projecting box reja (iron grille 0.3 m out, pot shelf) in a thick white wall", "wall_window_grille_t on a thick wall (leaves a reveal gap)"),
            ("wall_door_studded_k", "iron-studded door in a stone or painted surround", "wall_door_k"),
            ("band_zocalo", "the ochre/blue painted base band 0.8 m (face overlay at ground)", "none"),
            ("ov_blue_pots", "blue pots hung on a white wall (face overlay)", "ov_planter"),
            ("roof_tile_roman_low", "low 15-20 deg Roman-tile roof (cell roof)", "green_hip"),
            ("tower_mudejar", "Mudejar brick tower with sebka lozenge panels and belfry (base, shaft, top)", "minaret_base/shaft/top"),
            ("ov_toldo", "summer awning stretched across a shopping lane (along X)", "ov_awning_cane"),
        ],
    }
