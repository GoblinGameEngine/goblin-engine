"""Balkan stone tower-houses (r3_kulla_stone.md: Gjirokaster, Berat's upper town, the Kosovo kullas).

The mark: detached near-cube grey limestone towers 3-4 storeys on terraced switchbacks, the base a fortress of arrow
slits and a studded door, the top storey corbelled out as a continuous band of windows (half its face glass) under a
heavy steep hip of stone slabs with deep timber eaves and stone chimneys; courtyard walls with gates; the castle on
the ridge; white-stone patterns in the bazaar's cobbles."""
from civ.family import FamilyCiv


class KullaStone(FamilyCiv):
    id = "kulla_stone"
    name = "Balkan stone tower-houses"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 6), "lane_spacing": 5, "lane_len": 14, "branch": 0.35, "loop": 0.35, "artery_share": 0.2,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (6, 12), "courts": True, "court_min_lot": 6,
            "court_share": 0.4, "e1_levels": (3, 4), "max_levels": 4, "civic_levels": 2, "work_share": 0.12,
            "civic_min_cells": 10, "shop_share": 0.4,
            "epochs": {2: {"rise": 0.2, "setback": 0.1}, 3: {"rise": 0.12, "setback": 0.15}, 4: {"rise": 0.08, "setback": 0.2}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.3, "street_blades": 0.02,
            "shacks": 0.0,
        },
        "variants": (0.35, 0.3, 0.25, 0.1), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door_portal_k",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_window_s", 0.15), ("wall_plain", 0.85)],
                       "lane": [("wall_window_s", 0.1), ("wall_plain", 0.9)],
                       "court": [("wall_door", 0.3), ("wall_window_s", 0.2), ("wall_plain", 0.5)]},
            "upper": {"street": [("wall_window_s", 0.3), ("wall_plain", 0.7)],
                      "lane": [("wall_window_s", 0.25), ("wall_plain", 0.75)]},
            # the corbelled top storey: a band of windows
            "tower": [("wall_window_pair", 0.55), ("wall_window_l", 0.3), ("wall_plain", 0.15)], "tower_from": 2,
        },
        "corner": "corner_quoin",
        "roof": {"field": "roof_terrace", "edge": "edge_eave_tin", "crown": "green_hip", "crown_share": 1.0,
                 "crown_civic": "dome_cap"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 6}],
        "overlay": {"lantern": 0.35, "festoon": 0.15, "dish": 0.06, "cable": 0.08},
        "foliage": {"plaza": ["holm_oak"], "green": ["holm_oak", "cypress", "walnut", "fig"], "bank": ["cypress"],
                    "court": ["fig", "pomegranate", "grapevine_pergola"], "lane_wall": ["lavender"],
                    "rates": {"court": 0.5}},
        "kit_requests": [
            ("roof_stone_slab_steep", "the 30-35 deg hip roof of stone slabs (mosaic, lichen) with deep timber eaves (cell roof run + end)", "green_hip per cell"),
            ("wall_window_band_k", "the corbelled top storey: a continuous window band, 50% glass, timber, on corbels (wall)", "wall_window_pair_k"),
            ("wall_arrow_slit_k", "an arrow-slit window in the fortress base (wall)", "wall_window_s_k"),
            ("chimney_stone", "the tall stone chimney stack (roof decor)", "none"),
            ("ov_machicolation", "a machicolation box over the door (face overlay)", "none"),
        ],
    }
