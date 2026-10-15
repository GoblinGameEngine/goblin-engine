"""Omani falaj oasis town (r1_omani_oasis.md: Nizwa, Al Hamra, Misfat al Abriyeen, Birkat al Mouz).

The mark: a compact mud cluster under its fort: 2-3 storey houses of brown earth with rows of beam ends, triangle
merlons on every parapet, carved studded doors painted blue and green, small shuttered windows; narrow gated lanes
with the falaj water channel running down them; the palm garden all round (dates over limes and bananas); the souq
and the fort square."""
from civ.family import FamilyCiv


class OmaniOasis(FamilyCiv):
    id = "omani_oasis"
    name = "Omani falaj oasis town"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 6), "lane_spacing": 4, "lane_len": 12, "branch": 0.45, "loop": 0.3, "artery_share": 0.2,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (5, 11), "courts": False,
            "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 4, "sabat_from": 1, "work_share": 0.15,
            "civic_min_cells": 14, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.35, "setback": 0.3, "sabat": 0.15},
                       3: {"rise": 0.25, "setback": 0.35, "sabat": 0.15},
                       4: {"rise": 0.12, "setback": 0.4, "sabat": 0.1}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (7, 6), "sign": 0.2, "street_blades": 0.0,
            "shacks": 0.02,
        },
        "variants": (0.35, 0.3, 0.15, 0.2), "civic_variant": 1,
        "thick": 1,
        "facade": {
            "door": "wall_door_omani_k",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_arch_pointed", 0.4)],
            "ground": {"street": [("wall_window_s", 0.3), ("wall_door", 0.2), ("wall_plain", 0.5)],
                       "lane": [("wall_window_s", 0.22), ("wall_door", 0.08), ("wall_plain", 0.7)]},
            "upper": {"street": [("wall_beam_ends_k", 0.35), ("wall_window_s", 0.2), ("wall_window_m", 0.1), ("wall_plain", 0.35)],
                      "lane": [("wall_beam_ends_k", 0.25), ("wall_window_s", 0.2), ("wall_slit_k", 0.1), ("wall_plain", 0.45)]},
            "civic_ground": [("wall_plain", 0.8), ("wall_window_s", 0.2)],
            "civic_upper": [("wall_window_s", 0.25), ("wall_plain", 0.75)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_parapet_triangle_k"},
        "pave": {"pave_lane": "ground_falaj"},
        "marks": [{"type": "civic_tower", "pieces": ["fort_round_tower_base", "fort_round_tower_shaft", "fort_round_tower_top"], "storeys": 5},
                  {"type": "stalls", "share": 0.12}],
        "overlay": {"roof_items": [("ov_arish_shade", 0.05)], "awning": 0.4, "lantern": 0.35, "dish": 0.1, "cable": 0.05},
        "foliage": {"green": ["date_palm", "date_palm", "date_palm", "lime_tree", "banana", "alfalfa_beds"],
                    "bank": ["date_palm", "banana"], "plaza": ["ghaf", "sidr_ziziphus"], "roof": [],
                    "rates": {"green": 0.7, "bank": 0.5, "plaza": 0.08}},
        "kit_requests": [
            ("edge_parapet_triangle_k", "Omani triangle merlons along a parapet (edge)", "edge_parapet_crenel_k"),
            ("wall_beam_ends_k", "earth bay with a row of projecting palm-beam ends at the floor line (wall)", "wall_plain_k"),
            ("wall_door_omani_k", "carved studded double door painted blue/green in a lintel frame (wall)", "wall_door_k"),
            ("fort_round_tower", "Nizwa's great round fort tower, battered, crenellated (3 parts)", "minaret_base x6 + minaret_top"),
            ("ground_falaj", "lane paving with the falaj channel down its middle (ground; water slot)", "pave_lane"),
            ("ov_arish_shade", "palm-frond arish shade on poles (roof/lane overlay)", "ov_awning_cane"),
        ],
    }
