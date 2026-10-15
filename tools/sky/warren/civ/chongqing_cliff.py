"""Chongqing, the mountain city (r2_chongqing_cliff.md: diaojiaolou stilt houses, Hongyadong, Shibati).

The mark: a city poured down a slope: dark timber stilt houses whose downhill backs stand on tall poles, galleries
with timber railings on every storey, lattice windows, grey tile roofs with flying eaves stacked tier on tier;
concrete towers on the ridge; stair streets with landings and tea houses; red lanterns and gold-lit eaves at night;
banyans over the landings, bamboo in the gaps."""
from civ.family import FamilyCiv


class ChongqingCliff(FamilyCiv):
    id = "chongqing_cliff"
    name = "Chongqing mountain city"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 7), "lane_spacing": 5, "lane_len": 14, "branch": 0.4, "loop": 0.35, "artery_share": 0.25,
            "block_cells": 10, "cut_turn": 3.0, "lot_cells": (4, 10), "courts": False,
            "e1_levels": (2, 4), "max_levels": 11, "civic_levels": 2, "tower_levels": (7, 11), "tower_cells": 4,
            "sabat_from": 2, "jetty_from": 2, "work_share": 0.2, "civic_min_cells": 8, "stilts": 0.6,
            "flats_per_level": False,
            "epochs": {2: {"rise": 0.45, "setback": 0.1, "sabat": 0.12, "jetty": 0.2, "tower": 0.04},
                       3: {"rise": 0.4, "setback": 0.1, "sabat": 0.15, "jetty": 0.25, "tower": 0.08},
                       4: {"rise": 0.3, "setback": 0.15, "sabat": 0.12, "jetty": 0.25, "tower": 0.1}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.7, "street_blades": 0.25,
            "shacks": 0.04, "shop_share": 0.7,
        },
        "stilt_piece": "stilt_frame",
        "variants": (0.35, 0.3, 0.2, 0.15), "civic_variant": 3,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_shopfront", 0.35), ("wall_screen", 0.3), ("wall_door", 0.15),
                                  ("wall_plain", 0.2)],
                       "lane": [("wall_screen", 0.3), ("wall_door", 0.15), ("wall_plain", 0.55)]},
            "upper": {"street": [("wall_gallery_timber_t", 0.38), ("wall_screen", 0.22), ("wall_window_m", 0.15),
                                 ("wall_plain", 0.25)],
                      "lane": [("wall_gallery_timber_t", 0.25), ("wall_screen", 0.2), ("wall_plain", 0.55)],
                      "green": [("wall_gallery_timber_t", 0.45), ("wall_screen", 0.25), ("wall_plain", 0.3)],
                      "air": [("wall_screen", 0.25), ("wall_plain", 0.75)]},
            "tower": [("wall_window_pair", 0.35), ("wall_window_s", 0.25), ("wall_plain", 0.4)], "tower_from": 5,
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_eave_pagoda", "crown_civic": "roof_pagoda",
                 "pitched": {"run": "roof_tile_flying_eave", "end": "roof_tile_flying_eave", "max_rel": 4}},
        "marks": [{"type": "stalls", "share": 0.15}],
        "overlay": {"face_items": [{"piece": "ov_gold_eave_led", "p": 0.5, "where": "top", "dk": 1}], "lantern": 0.7, "festoon": 0.45, "cable": 0.3, "ac": 0.1, "lane_laundry": 0.1, "tank": 0.05,
                    "antenna": 0.05},
        "foliage": {"plaza": ["banyan_tree", "camphor"], "green": ["camphor", "banyan_tree", "bamboo", "bamboo"],
                    "bank": ["bamboo", "willow"], "lane_wall": ["ivy_moss"], "roof": ["potted_plants"],
                    "rates": {"green": 0.5, "lane_wall": 0.05}},
        "kit_requests": [
            ("stair_street_long", "a stair street flight with a landing (Shibati), 3 m wide (stair, span [1, 2])", "steps + step_low"),
            ("roof_tile_flying_eave", "grey tile roof with upturned eave corners, shallow pitch (cell roof)", "green_hip + edge_eave_pagoda"),
            ("wall_gallery_timber_t", "a continuous timber gallery with railings along a storey (wall)", "wall_balcony_timber_t"),
            ("skybridge_street", "a bridge from a street into a building's upper floor (cell)", "none"),
            ("ov_gold_eave_led", "the warm gold LED line traced along every eave (edge overlay, emissive)", "none"),
        ],
    }

    def roof_edge(self, ctx):
        """flying eaves on the low timber houses; plain parapets on the concrete towers"""
        L = self.L
        if ctx["level"] - int(L.gk[ctx["i"], ctx["j"]]) <= 4:
            return ("edge_eave_pagoda", 0, 0)
        return ("parapet_plain", 0, 0)
