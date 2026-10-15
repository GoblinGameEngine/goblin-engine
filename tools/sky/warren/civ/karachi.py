"""Karachi, the Sindhi port metropolis (r1_karachi.md: Saddar, Kharadar, Lyari, Orangi).

The mark: three cities at once: deep narrow merchant blocks of yellow Gizri stone with jharokhas and turned-baluster
balconies; colonial Indo-Gothic blocks with arcaded verandas; and the self-built concrete grid painted every colour,
grilled box balconies, water-tank drums, dishes, kites and tin shacks on the roofs; roller shutters below; cables in
canyons at two or three levels; stacked LED signboards, truck art and wedding-light curtains."""
from civ.family import FamilyCiv


class Karachi(FamilyCiv):
    id = "karachi"
    name = "Karachi port metropolis"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (4, 7), "jog": 0.15, "blind": 0.15, "break": 0.05, "light_wells": 0.03,
            "lot_cells": (3, 8), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (3, 4), "max_levels": 12, "civic_levels": 3, "tower_levels": (6, 10),
            "jetty_from": 2, "sabat_from": 9, "work_share": 0.3, "civic_min_cells": 8,
            "epochs": {2: {"rise": 0.5, "setback": 0.0, "tower": 0.08, "jetty": 0.12},
                       3: {"rise": 0.45, "setback": 0.0, "tower": 0.12, "jetty": 0.15},
                       4: {"rise": 0.35, "setback": 0.05, "tower": 0.15, "jetty": 0.15}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 1.0, "street_blades": 0.55,
            "shacks": 0.18, "enter_doors": 0.1,
        },
        "variants": (0.3, 0.2, 0.2, 0.3), "civic_variant": 0,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.85), ("wall_shopfront_arcade", 0.15)],
            "ground": {"street": [("wall_shopfront", 0.6), ("wall_arch_pointed", 0.15), ("wall_door", 0.25)],
                       "lane": [("wall_shopfront", 0.3), ("wall_door", 0.25), ("wall_window_grille", 0.2),
                                ("wall_plain", 0.25)]},
            "upper": {"street": [("wall_veranda_gothic_t", 0.08), ("wall_balcony_iron", 0.16), ("wall_jharokha_k", 0.08), ("wall_balcony_cage", 0.15),
                                 ("wall_window_m", 0.25), ("wall_plain", 0.3)],
                      "lane": [("wall_balcony_cage", 0.15), ("wall_window_s", 0.3), ("wall_plain", 0.55)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
            "civic_ground": [("wall_arch_pointed", 0.6), ("wall_plain", 0.4)],
            "civic_upper": [("wall_arch_pointed", 0.4), ("wall_window_l", 0.3), ("wall_plain", 0.3)],
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap",
                 "edge_street": [("edge_parapet_date_plaque", 1.0)]},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 7},
                  {"type": "stalls", "share": 0.2}, {"type": "playground"}],
        "overlay": {"face_items": [{"piece": "ov_truck_art_panel", "p": 0.35, "shops": True, "epoch": 5},
                               {"piece": "ov_wedding_curtain", "p": 0.07, "where": "upper", "epoch": 5},
                               {"piece": "ov_roller_shutter", "p": 0.3, "shops": True, "epoch": 5}],
                    "spans": [("ov_wire_net", 0.25), ("ov_festoon", 0.2)], "cable_levels": 3,
                    "roof_items": [("ov_tank_drum", 0.25), ("pigeon_cote", 0.02), ("chhatri", 0.004)],
                    "sign_column": 0.4, "cable": 0.85, "tank": 0.03, "dish": 0.2, "laundry": 0.1, "antenna": 0.05, "ac": 0.2, "pipe": 0.1,
                    "festoon": 0.6, "lantern": 0.4, "lane_laundry": 0.1},
        "foliage": {"plaza": ["neem", "gulmohar", "peepal"], "green": ["neem", "gulmohar", "banyan", "coconut_palm",
                                                                       "conocarpus"],
                    "bank": ["coconut_palm", "date_palm"], "lane_wall": ["bougainvillea"], "roof": ["tulsi_pots"],
                    "rates": {"roof": 0.05}},
        "kit_requests": [
            ("ov_tank_drum", "the black/blue plastic water-tank drum, clustered on roofs (roof overlay)", "ov_tank"),
            ("wall_jharokha_k", "Gizri-stone jharokha bay on carved brackets (wall)", "wall_bay_box"),
            ("wall_veranda_gothic_t", "colonial Indo-Gothic arcaded veranda storey (wall)", "wall_arch_pointed"),
            ("ov_truck_art_panel", "a truck-art painted panel / shutter (face overlay, emissive)", "none"),
            ("ov_wedding_curtain", "wedding fairy-light curtain down a facade (face overlay, emissive)", "none"),
            ("edge_parapet_date_plaque", "a balustrade parapet with urns and a date plaque (edge)", "edge_parapet_plain_t"),
        ],
    }
