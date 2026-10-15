"""Korean hillside villages (r2_korean_hillside.md: daldongne, Busan's Gamcheon, Seoul's Ihwa).

The mark: terraced pastel concrete cubes stacked up a steep slope so every roof is a view and the street of the row
above; flat roofs painted green and blue with stainless and blue water tanks, jangdok soy jars and laundry, a rooftop
room (oktapbang) on many; small barred aluminium windows and metal doors; long straight stair streets, no roads;
murals; persimmons and potted peppers."""
from civ.family import FamilyCiv


class KoreanHillside(FamilyCiv):
    id = "korean_hillside"
    name = "Korean hillside village"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 4, "lane_len": 16, "branch": 0.35, "loop": 0.4, "artery_share": 0.15,
            "block_cells": 9, "cut_turn": 2.5, "lot_cells": (2, 5), "courts": False,
            "e1_levels": (1, 2), "max_levels": 4, "civic_levels": 2, "work_share": 0.1, "civic_min_cells": 6,
            "shop_share": 0.4,
            "epochs": {2: {"rise": 0.4, "setback": 0.2}, 3: {"rise": 0.35, "setback": 0.25}, 4: {"rise": 0.2, "setback": 0.3}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.4, "street_blades": 0.05,
            "shacks": 0.15,
        },
        "variants": (0.25, 0.25, 0.25, 0.25), "civic_variant": 0,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.8), ("wall_door", 0.2)],
            "ground": {"street": [("wall_window_grille", 0.35), ("wall_door", 0.2), ("wall_plain", 0.45)],
                       "lane": [("wall_window_grille", 0.3), ("wall_door", 0.15), ("wall_plain", 0.55)]},
            "upper": {"street": [("wall_window_grille", 0.3), ("wall_window_s", 0.15), ("wall_plain", 0.55)],
                      "lane": [("wall_window_grille", 0.25), ("wall_window_s", 0.1), ("wall_mural_t", 0.06), ("wall_plain", 0.59)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_rail", "crown_civic": "green_hip"},
        "marks": [{"type": "playground"}],
        "overlay": {"tank": 0.3, "laundry": 0.15, "roof_items": [("satellite_dish", 0.05)], "cable": 0.4, "pole": 0.3,
                    "lantern": 0.25},
        "foliage": {"green": ["persimmon", "korean_red_pine", "cherry"], "bank": ["willow", "cherry"],
                    "plaza": ["persimmon"], "roof": ["pepper_boxes", "jangdok_jars"], "lane_wall": ["potted_plants"],
                    "rates": {"roof": 0.12, "lane_wall": 0.08}},
        "kit_requests": [
            ("ov_jangdok_jars", "a cluster of brown soy-sauce jars on a roof (roof decor)", "foliage stand-in"),
            ("roof_painted_green", "the green-painted waterproofed flat roof (cell roof)", "roof_terrace"),
            ("oktapbang", "the rooftop room box with a small door and window (roof overlay)", "E5 roof huts (ov_shack)"),
            ("wall_mural_t", "a mural-painted blank wall (wall)", "wall_plain_t"),
            ("stair_street_long", "the long straight stair street (exists: placed by the slope rule when it lands)", "steps"),
        ],
    }
