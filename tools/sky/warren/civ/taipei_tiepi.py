"""Taipei alleys and the iron-sheet rooftop layer (r2_taipei_tiepi.md).

The mark: four-to-six storey tiled walk-ups over qilou arcades full of scooters, every window wearing a projecting
iron cage full of plants and laundry, and on every roof a second house of corrugated iron (tiepiwu) with water towers;
a temple square night market; potted plants down every alley."""
from civ.family import FamilyCiv


class TaipeiTiepi(FamilyCiv):
    id = "taipei_tiepi"
    shack_pieces = ("ov_tiepi_house",)
    name = "Taipei iron-sheet alleys"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (4, 7), "jog": 0.12, "blind": 0.15, "break": 0.04, "light_wells": 0.0,
            "lot_cells": (3, 8), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (4, 5), "max_levels": 7, "civic_levels": 2, "tower_levels": (6, 7),
            "jetty_from": 9, "sabat_from": 9, "work_share": 0.3, "civic_min_cells": 6,
            "epochs": {2: {"rise": 0.35, "setback": 0.0, "tower": 0.06},
                       3: {"rise": 0.25, "setback": 0.0, "tower": 0.06},
                       4: {"rise": 0.15, "setback": 0.0}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.8, "street_blades": 0.35,
            "shacks": 0.45, "enter_doors": 0.12,
        },
        "variants": (0.3, 0.3, 0.25, 0.15), "civic_variant": 2,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.8), ("wall_shopfront", 0.2)],
            "ground": {"street": [("wall_qilou_t", 0.6), ("wall_shopfront_arcade", 0.2), ("wall_door", 0.2)],
                       "lane": [("wall_door", 0.3), ("wall_window_grille", 0.35), ("wall_plain", 0.35)]},
            "upper": {"street": [("wall_balcony_cage", 0.3), ("wall_tile_t", 0.3), ("wall_window_pair", 0.12),
                                 ("wall_plain", 0.28)],
                      "lane": [("wall_balcony_cage", 0.25), ("wall_window_s", 0.25), ("wall_plain", 0.5)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "roof_pagoda"},
        "marks": [{"type": "stalls", "share": 0.3}],
        "overlay": {"sign_column": 0.3, "roof_items": [("ov_water_tower_steel", 0.08)], "tank": 0.12, "antenna": 0.04, "ac": 0.2, "pipe": 0.1, "cable": 0.35, "lane_laundry": 0.1,
                    "lantern": 0.4, "festoon": 0.35, "wall_pots": 0.12},
        "foliage": {"plaza": ["banyan_tree"], "green": ["banyan_tree", "betel_palm", "bamboo"],
                    "bank": ["bamboo", "reeds"], "lane": ["potted_plants"], "lane_wall": ["potted_plants"],
                    "roof": ["potted_plants"], "rates": {"lane": 0.15, "lane_wall": 0.12, "roof": 0.08}},
        "kit_requests": [
            ("ov_tiepi_house", "the 1-2 storey corrugated iron rooftop house with a pent roof (roof overlay, bigger than ov_shack)", "ov_shack_a/b/c"),
            ("wall_qilou_t", "the qilou arcade bay: a column at the street edge, the arcade behind, a shopfront at the back (wall)", "wall_shopfront_b_t"),
            ("wall_tile_t", "small ceramic tile cladding bay (wall)", "wall_plain_t"),
            ("ov_water_tower_steel", "the stainless water tower on legs (roof)", "ov_tank"),
        ],
    }
