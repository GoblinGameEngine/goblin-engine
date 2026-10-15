"""Rajput desert sandstone city (r1_rajput_sandstone.md: Jaisalmer, Jodhpur's blue city, Bikaner).

The mark: golden sandstone havelis carved over 70-90% of their faces, each storey a different rhythm of canted
jharokhas and fine stone jali; 2-3 m lanes zigzagging between them up to the hill fort's round crenellated bastions;
chhatris everywhere on the roofs; the tank with its ghats; khejri and neem; backlit jali glowing at night."""
from civ.family import FamilyCiv


class RajputSandstone(FamilyCiv):
    id = "rajput_sandstone"
    name = "Rajput sandstone city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 7), "lane_spacing": 4, "lane_len": 14, "branch": 0.45, "loop": 0.35, "artery_share": 0.3,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (4, 11), "courts": True, "court_min_lot": 9,
            "court_share": 0.12, "e1_levels": (2, 3), "max_levels": 5, "civic_levels": 4, "sabat_from": 2,
            "work_share": 0.15, "civic_min_cells": 14, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.45, "setback": 0.15, "sabat": 0.06},
                       3: {"rise": 0.35, "setback": 0.2, "sabat": 0.06},
                       4: {"rise": 0.25, "setback": 0.25, "sabat": 0.05}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.35, "street_blades": 0.06,
            "shacks": 0.02,
        },
        "civic_court": True,
        "variants": (0.4, 0.3, 0.25, 0.05), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_arch_pointed",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_jali_carved_k", 0.25), ("wall_arch_pointed", 0.2), ("wall_door", 0.2),
                                  ("wall_window_s", 0.15), ("wall_plain", 0.2)],
                       "lane": [("wall_jali_carved_k", 0.2), ("wall_door", 0.15), ("wall_window_s", 0.2), ("wall_plain", 0.45)],
                       "court": [("wall_arch_pointed", 0.6), ("wall_jali_carved_k", 0.4)]},
            "upper": {"street": [("wall_jharokha_canted_k", 0.3), ("wall_jali_carved_k", 0.3), ("wall_arch_pointed", 0.15),
                                 ("wall_window_m", 0.15), ("wall_plain", 0.1)],
                      "lane": [("wall_jharokha_canted_k", 0.2), ("wall_jali_carved_k", 0.3), ("wall_window_s", 0.2), ("wall_plain", 0.3)],
                      "court": [("wall_jali_carved_k", 0.4), ("wall_arch_pointed", 0.3), ("wall_window_m", 0.3)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_jali", "crown_civic": "dome_cap"},
        "marks": [{"type": "roof_towers", "piece": "chhatri", "share": 0.02, "storeys": (1, 1)},
                  {"type": "civic_tower", "pieces": ["bastion_round_base", "bastion_round_shaft", "bastion_round_top"], "storeys": 4},
                  {"type": "bank_steps"}, {"type": "stalls", "share": 0.12}],
        "overlay": {"face_items": [{"piece": "edge_chhajja", "p": 0.35, "where": "upper", "dk": 1}], "festoon": 0.4, "lantern": 0.45, "dish": 0.1, "cable": 0.2, "awning": 0.25},
        "foliage": {"plaza": ["khejri", "neem"], "green": ["khejri", "neem", "kikar_acacia", "date_palm"],
                    "bank": ["neem", "date_palm"], "lane_wall": ["bougainvillea", "oleander"], "court": ["oleander"],
                    "rates": {"lane_wall": 0.06}},
        "kit_requests": [
            ("wall_jharokha_canted_k", "the canted octagonal carved sandstone jharokha with a domed top (wall)", "wall_bay_box_k"),
            ("wall_jali_carved_k", "a full-bay finely carved stone jali screen, backlit at night (wall)", "wall_screen_k"),
            ("chhatri", "the domed corner pavilion on four columns (roof crown)", "arcade_pier + dome_cap"),
            ("bastion_round", "the fort's round crenellated bastion (3 parts)", "minaret_base + dome_cap"),
            ("edge_parapet_jali_k (lighter)", "the jali parapet at <= 150 tris (456 now: the budget pass turns them plain)", "edge_parapet_plain_k when over budget"),
        ],
    }
