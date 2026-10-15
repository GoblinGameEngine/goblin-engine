"""Cycladic islands (r3_cycladic.md: Oia, Mykonos' Chora, Naxos' kastro, Hydra).

The mark: rounded whitewashed cubes packed wall to wall in a deliberate maze of 1.5-2.5 m lanes (slate paving with
white joints), small deep windows with blue-painted frames and doors, external stairs to roof terraces with rounded
lips, timber balconies on corbels; a little chapel with a blue dome and bell gable every 20-40 houses; windmills on
the ridge; bougainvillea over white walls."""
from civ.family import FamilyCiv


class Cycladic(FamilyCiv):
    id = "cycladic"
    name = "Cycladic island town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 7), "lane_spacing": 4, "lane_len": 12, "branch": 0.55, "loop": 0.25, "artery_share": 0.15,
            "block_cells": 9, "cut_turn": 4.5, "lot_cells": (3, 8), "courts": False,
            "e1_levels": (1, 2), "max_levels": 3, "civic_levels": 2, "sabat_from": 1, "work_share": 0.12,
            "civic_min_cells": 6, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.35, "setback": 0.35, "sabat": 0.08},
                       3: {"rise": 0.25, "setback": 0.4, "sabat": 0.08},
                       4: {"rise": 0.15, "setback": 0.45, "sabat": 0.05}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.35, "street_blades": 0.02,
            "shacks": 0.0,
        },
        "variants": (0.6, 0.15, 0.15, 0.1), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_window_s", 0.3), ("wall_door", 0.2), ("wall_plain", 0.5)],
                       "lane": [("wall_window_s", 0.25), ("wall_door", 0.15), ("wall_plain", 0.6)]},
            "upper": {"street": [("wall_window_s", 0.3), ("wall_balcony_timber", 0.12), ("wall_plain", 0.58)],
                      "lane": [("wall_window_s", 0.28), ("wall_balcony_timber", 0.08), ("wall_plain", 0.64)]},
            "civic_ground": [("wall_arch_round", 0.4), ("wall_plain", 0.6)],
            "civic_upper": [("wall_plain", 1.0)],
        },
        "corner": "corner_round",
        "roof": {"field": "roof_terrace", "edge": "parapet_rounded", "crown_civic": "dome_cap",
                 "crown": "dome_cap", "crown_share": 0.015},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_base", "dome_cap"], "storeys": 2},
                  {"type": "stalls", "share": 0.06}],
        "overlay": {"lantern": 0.45, "festoon": 0.25, "awning": 0.3, "wall_pots": 0.08, "dish": 0.03, "cable": 0.04},
        "foliage": {"plaza": ["tamarisk", "pepper_tree"], "green": ["olive", "tamarisk", "fig"],
                    "bank": ["tamarisk", "reeds"], "lane_wall": ["bougainvillea", "bougainvillea", "hibiscus"],
                    "roof": ["geranium_tins", "basil_pots"], "rates": {"lane_wall": 0.12, "roof": 0.08}},
        "kit_requests": [
            ("chapel_cycladic", "the little white chapel with a blue dome and bell gable (crown over 1-2 cells)", "minaret_base x2 + dome_cap"),
            ("windmill_round", "the round white windmill with sails (cell, 3 storeys)", "none"),
            ("edge_parapet_lip_k", "the rounded whitewashed roof lip (edge, cheaper than parapet_rounded)", "edge_parapet_rounded_k"),
            ("pave_slate_whitejoint", "slate paving with whitewashed joints (ground)", "pave_lane"),
            ("stair_external_white", "the external whitewashed stair up a house face to the roof (face overlay)", "none"),
        ],
    }
