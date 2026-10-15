"""Bangkok: khlong canal life and Yaowarat (r2_siam_khlong.md: Thonburi's canals, Chinatown).

The mark: teak houses on stilts with steep gable roofs and curling finials lining the canal-ponds, piers and steps
down to the water, wide panel windows hinged to swing out; behind them sois of two-storey shophouses under a forest
of gold-shop neon; temples with tiered roofs and nagas; bananas, coconut palms, bodhi trees, lotus."""
from civ.family import FamilyCiv


class SiamKhlong(FamilyCiv):
    id = "siam_khlong"
    name = "Bangkok khlong town"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    kerb = "kerb_straight"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 5, "lane_len": 16, "branch": 0.35, "loop": 0.4, "artery_share": 0.3,
            "block_cells": 11, "cut_turn": 2.5, "lot_cells": (3, 7), "courts": False,
            "e1_levels": (2, 2), "max_levels": 5, "civic_levels": 2, "tower_levels": (4, 5), "work_share": 0.25,
            "civic_min_cells": 10, "shop_share": 0.8, "stilts": 0.7,
            "epochs": {2: {"rise": 0.3, "setback": 0.0, "tower": 0.04}, 3: {"rise": 0.25, "setback": 0.05, "tower": 0.06},
                       4: {"rise": 0.15, "setback": 0.05, "tower": 0.05}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (7, 6), "sign": 0.95, "street_blades": 0.5,
            "shacks": 0.04,
        },
        "stilt_piece": "stilt_frame",
        "variants": (0.35, 0.25, 0.25, 0.15), "civic_variant": 3,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.85), ("wall_door", 0.15)],
            "ground": {"street": [("wall_shopfront", 0.6), ("wall_door", 0.25), ("wall_plain", 0.15)],
                       "lane": [("wall_door", 0.3), ("wall_thai_teak_t", 0.3), ("wall_plain", 0.4)],
                       "green": [("wall_thai_teak_t", 0.5), ("wall_door", 0.2), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_window_pair", 0.35), ("wall_window_m", 0.25), ("wall_plain", 0.4)],
                      "lane": [("wall_thai_teak_t", 0.3), ("wall_window_m", 0.2), ("wall_plain", 0.5)],
                      "green": [("wall_thai_teak_t", 0.45), ("wall_balcony_timber", 0.25), ("wall_plain", 0.3)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_eave_pagoda", "crown_civic": "roof_pagoda",
                 "pitched": {"run": "roof_thai_gable", "end": "roof_thai_gable", "share": 0.75, "max_rel": 2}},
        "marks": [{"type": "bank_steps", "piece": "step_low_4"}, {"type": "stalls", "share": 0.25}],
        "overlay": {"sign_column": 0.35, "festoon": 0.45, "lantern": 0.5, "cable": 0.45, "pole": 0.25, "ac": 0.12,
                    "tank": 0.1},
        "foliage": {"bank": ["banana", "coconut_palm", "lotus", "water_hyacinth"], "green": ["bodhi_tree", "banana", "coconut_palm"],
                    "plaza": ["bodhi_tree"], "lane_wall": ["bougainvillea", "orchid_pot"], "rates": {"bank": 0.45}},
        "kit_requests": [
            ("roof_thai_gable", "the steep (45 deg+) teak-house gable roof with curling chofa finials (cell roof run + end)", "roof_pitched_pantile"),
            ("wall_teak_panel_t", "teak plank bay with a wide panel window hinged to swing out (wall)", "wall_screen_t"),
            ("pier_steps_khlong", "the pier and steps down from a stilt house into the canal (stair, water side)", "step_low_4 on banks"),
            ("temple_tiered_roof", "the wat's tiered layered roof with naga gables (crown)", "roof_pagoda"),
            ("ov_gold_shop_neon", "the big vertical gold-shop neon signs of Yaowarat (face overlay)", "wall_sign_column_t"),
        ],
    }
