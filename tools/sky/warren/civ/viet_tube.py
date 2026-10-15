"""Vietnamese tube houses and hem alleys (r2_viet_tube.md: Hanoi's Old Quarter, Saigon's alleys, Hoi An).

The mark: facades only 3-5 m wide but 4-6 storeys tall and deep, every one a different strong colour and height like
books on a shelf, with full-height french doors and louvred shutters onto narrow balconies full of plants, roller
shutters at the ground, blank side walls where a neighbour is lower; tangles of wires; rooftop gardens, tanks and
shrines; hem alleys behind; the lake with its red bridge."""
from civ.family import FamilyCiv


class VietTube(FamilyCiv):
    id = "viet_tube"
    name = "Vietnamese tube houses"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (5, 8), "jog": 0.1, "blind": 0.2, "break": 0.05, "light_wells": 0.03,
            "lot_cells": (2, 5), "courts": False, "flats_per_level": False, "roof_walk": False,
            "e1_levels": (2, 3), "max_levels": 7, "civic_levels": 2, "tower_levels": (4, 7),
            "sabat_from": 9, "jetty_from": 9, "work_share": 0.25, "civic_min_cells": 6, "shop_share": 0.9,
            "epochs": {2: {"rise": 0.45, "setback": 0.0, "tower": 0.2, "tower_levels": (4, 5)},
                       3: {"rise": 0.35, "setback": 0.0, "tower": 0.25, "tower_levels": (4, 6)},
                       4: {"rise": 0.3, "setback": 0.0, "tower": 0.25, "tower_levels": (5, 7)}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.9, "street_blades": 0.4,
            "shacks": 0.1, "enter_doors": 0.15,
        },
        "variants": (0.25, 0.25, 0.25, 0.25), "civic_variant": 3,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.9), ("wall_door", 0.1)],
            "ground": {"street": [("wall_shopfront", 0.75), ("wall_door", 0.25)],
                       "lane": [("wall_door", 0.35), ("wall_shopfront", 0.25), ("wall_window_grille", 0.15), ("wall_plain", 0.25)]},
            "upper": {"street": [("wall_french_door_balcony_t", 0.55), ("wall_window_l", 0.25), ("wall_plain", 0.2)],
                      "lane": [("wall_french_door_balcony_t", 0.3), ("wall_window_m", 0.25), ("wall_plain", 0.45)],
                      "air": [("wall_side_ad_t", 0.12), ("wall_plain", 0.78), ("wall_window_s", 0.1)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "roof_tile_flying_eave"},
        "marks": [{"type": "stalls", "share": 0.25}, {"type": "water_bridge", "piece": "bridge_red_lake", "max": 2}],
        "overlay": {"pole_piece": "ov_wire_tangle", "cable": 0.8, "pole": 0.3, "tank": 0.2, "antenna": 0.05, "laundry": 0.08, "roof_items": [("planter", 0.1), ("ov_roof_shrine", 0.04)],
                    "ac": 0.15, "festoon": 0.35, "lantern": 0.4, "awning": 0.3, "sign_column": 0.15},
        "foliage": {"plaza": ["dracontomelon", "banyan_tree"], "green": ["dracontomelon", "khaya", "banyan_tree"],
                    "bank": ["water_lily", "banyan_tree"], "roof": ["potted_plants", "kumquat_pot"],
                    "lane_wall": ["bougainvillea"], "rates": {"roof": 0.12}},
        "kit_requests": [
            ("wall_french_door_balcony_t", "full-height french doors with louvred shutters onto a narrow balcony full of pots (wall)", "wall_balcony_iron_t"),
            ("ov_wire_tangle", "the knotted wire tangles on the street poles (cell decor)", "utility_pole"),
            ("wall_side_ad_t", "a painted advertisement on a blank side wall (wall)", "wall_plain_t"),
            ("ov_roof_shrine", "the small rooftop ancestor shrine (roof decor, emissive)", "none"),
            ("bridge_red_lake", "the red wooden bridge to the lake island (bridge, span [1, 3])", "none"),
        ],
    }
