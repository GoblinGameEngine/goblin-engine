"""Caucasian balcony towns (r3_caucasian_balcony.md: Tbilisi's Old Town and Sololaki, Sighnaghi, Svaneti).

The mark: limewashed thin-brick houses whose street and courtyard faces are hung full-width with carved timber
balconies and stained-glass galleries (turquoise, sky blue, olive, brown) stacked 2-3 deep, leaning, over cliffs and
'Italian courtyards' ringed with galleries and spiral stairs; low red tin roofs; brick bath domes in the bath quarter;
Svan stone towers on the upper terraces; vines across the lanes."""
from civ.family import FamilyCiv


class CaucasianBalcony(FamilyCiv):
    id = "caucasian_balcony"
    name = "Caucasian balcony town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 8), "lane_spacing": 5, "lane_len": 15, "branch": 0.4, "loop": 0.35, "artery_share": 0.25,
            "block_cells": 11, "cut_turn": 3.5, "lot_cells": (6, 14), "courts": True, "court_min_lot": 9,
            "court_share": 0.2, "e1_levels": (2, 3), "max_levels": 4, "civic_levels": 2, "tower_levels": (6, 7),
            "tower_cells": 1, "sabat_from": 9, "jetty_from": 1, "work_share": 0.15, "civic_min_cells": 10,
            "shop_share": 0.5, "stilts": 0.25,
            "epochs": {2: {"rise": 0.35, "setback": 0.1, "jetty": 0.2, "tower": 0.03},
                       3: {"rise": 0.25, "setback": 0.15, "jetty": 0.25, "tower": 0.03},
                       4: {"rise": 0.15, "setback": 0.2, "jetty": 0.2, "tower": 0.02}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.45, "street_blades": 0.05,
            "shacks": 0.03,
        },
        "stilt_piece": "stilt_frame",
        "variants": (0.4, 0.3, 0.15, 0.15), "civic_variant": 0,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_door", 0.25), ("wall_window_m", 0.3), ("wall_plain", 0.45)],
                       "lane": [("wall_door", 0.2), ("wall_window_m", 0.25), ("wall_plain", 0.55)],
                       "court": [("wall_arch_round", 0.4), ("wall_door", 0.3), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_tbilisi_balcony_t", 0.35), ("wall_balcony_timber", 0.2), ("wall_window_m", 0.25),
                                 ("wall_plain", 0.2)],
                      "lane": [("wall_tbilisi_balcony_t", 0.22), ("wall_balcony_timber", 0.18), ("wall_window_m", 0.25),
                               ("wall_plain", 0.35)],
                      "green": [("wall_tbilisi_balcony_t", 0.45), ("wall_balcony_timber", 0.25), ("wall_plain", 0.3)],
                      "court": [("wall_shushabandi_t", 0.35), ("wall_balcony_timber", 0.35), ("wall_tbilisi_balcony_t", 0.15),
                                ("wall_window_m", 0.15)]},
            "tower": [("wall_window_s", 0.25), ("wall_plain", 0.75)], "tower_from": 4,
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tin_steep", "end": "roof_tin_steep_end", "share": 0.55}},
        "marks": [{"type": "civic_tower", "pieces": ["svan_tower_base", "svan_tower_shaft", "svan_tower_top"], "storeys": 6},
                  {"type": "roof_towers", "piece": "dome_bath_brick", "share": 0.01, "storeys": (1, 1)}],
        "overlay": {"spans": [("laundry", 0.15)], "lantern": 0.4, "festoon": 0.3, "cable": 0.3, "dish": 0.1},
        "foliage": {"plaza": ["chinar_plane"], "green": ["persimmon", "fig", "pomegranate", "chinar_plane"],
                    "bank": ["willow"], "court": ["grapevine_pergola", "persimmon", "fig"], "lane": ["grapevine_pergola"],
                    "rates": {"court": 0.55, "lane": 0.08}},
        "kit_requests": [
            ("wall_tbilisi_balcony_t (lighter)", "the carved balcony at <= 300 tris (692: shed to timber balconies when over budget)", "wall_balcony_timber_t"),
            ("wall_shushabandi_t", "the small-pane stained-glass gallery (shushabandi) (wall, emissive glass)", "wall_tbilisi_balcony_t"),
            ("svan_tower", "the Svan defensive stone tower 20-25 m with a slate gable top (base, shaft, top)", "rooms (tower_cells 1)"),
            ("dome_bath_brick", "the low brick bath dome with a lantern (crown)", "dome_cap"),
            ("stair_spiral_courtyard", "the spiral iron stair of an Italian courtyard (cell)", "stair_spiral"),
        ],
    }
