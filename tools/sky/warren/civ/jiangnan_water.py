"""Jiangnan water towns and the Shanghai lilong (r2_jiangnan_water.md: Zhouzhuang, Suzhou, Wuzhen, Tongli).

The mark: white walls and black tiles over water: long narrow houses fronting a lane and backing onto the canal-ponds
with private steps down to the water and stone quays; full-width timber shop fronts of boards, lattice upper windows,
moon gates; black double-pitched tile roofs with upturned ridge ends and stepped horse-head firewalls; humpbacked
bridges; weeping willows, lotus, osmanthus; red lanterns along the quays."""
from civ.family import FamilyCiv


class JiangnanWater(FamilyCiv):
    id = "jiangnan_water"
    name = "Jiangnan water town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    kerb = "quay_edge_stone"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 5, "lane_len": 18, "branch": 0.3, "loop": 0.45, "artery_share": 0.3,
            "block_cells": 10, "cut_turn": 2.5, "lot_cells": (3, 8), "courts": True, "court_min_lot": 6,
            "court_share": 0.15, "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 2, "work_share": 0.2,
            "civic_min_cells": 8, "shop_share": 0.75,
            "epochs": {2: {"rise": 0.3, "setback": 0.1}, 3: {"rise": 0.2, "setback": 0.15}, 4: {"rise": 0.1, "setback": 0.2}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.5, "street_blades": 0.08,
            "shacks": 0.0,
        },
        "variants": (0.45, 0.35, 0.1, 0.1), "civic_variant": 0,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_screen", 0.4)],
            "ground": {"street": [("wall_shopboards_t", 0.4), ("wall_shopfront", 0.3), ("wall_door", 0.15), ("wall_plain", 0.15)],
                       "lane": [("wall_door", 0.2), ("wall_screen", 0.2), ("wall_plain", 0.6)],
                       "green": [("wall_screen", 0.25), ("wall_moon_gate", 0.1), ("wall_door", 0.2), ("wall_plain", 0.45)]},
            "upper": {"street": [("wall_screen", 0.4), ("wall_window_m", 0.25), ("wall_plain", 0.35)],
                      "lane": [("wall_screen", 0.2), ("wall_window_s", 0.2), ("wall_plain", 0.6)],
                      "green": [("wall_screen", 0.4), ("wall_balcony_timber", 0.2), ("wall_plain", 0.4)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": None, "crown_civic": "roof_tile_flying_eave",
                 "edge_street": [("edge_horsehead_wall", 1.0)],
                 "pitched": {"run": "roof_black_tile_curved", "end": "roof_black_tile_curved_end", "share": 0.95}},
        "marks": [{"type": "bank_steps", "piece": "water_steps_private", "toward_water": True}, {"type": "stalls", "share": 0.1}],
        "overlay": {"lantern": 0.6, "festoon": 0.45, "cable": 0.15, "dish": 0.03, "lane_laundry": 0.06},
        "foliage": {"bank": ["weeping_willow", "weeping_willow", "lotus"], "green": ["osmanthus", "plum", "camellia", "bamboo"],
                    "plaza": ["weeping_willow"], "court": ["osmanthus", "bamboo"], "rates": {"bank": 0.5, "court": 0.4}},
        "kit_requests": [
            ("edge_horsehead_wall", "the stepped horse-head firewall at a house end, white with black tile copings (edge, gable end)", "none"),
            ("roof_black_tile_curved", "black double-pitched tile roof, gentle curve, upturned ridge ends (cell roof run + end)", "roof_kawara_low"),
            ("wall_shopboards_t", "the full-width removable timber shop boards (wall, ground)", "wall_screen_t"),
            ("wall_moon_gate", "a round moon gate in a garden wall (passage)", "wall_arch_round"),
            ("bridge_humpback_stone", "the humpbacked stone canal bridge (bridge, span [1, 3])", "none"),
            ("water_steps_private", "the private stone steps from a house down into the canal (stair, water side)", "step_low_4"),
        ],
    }
