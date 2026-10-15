"""Latin hillside self-built cities (r3_latin_hillside.md: Rio's favelas, Medellin's comunas, Valparaiso's cerros).

The mark: endless stepping self-built boxes, one room per cell, raw hollow brick or painted in every bright colour, a
new storey whenever money allows (smaller, cantilevered over the alley); flat laje roofs that are the true social
space, each with a blue water tank, laundry and rebar; becos 1-2 m and stairs everywhere; iron grilles on everything;
a concrete football court cut in; tangled cables; banana and papaya in the gaps."""
from civ.family import FamilyCiv


class LatinHillside(FamilyCiv):
    id = "latin_hillside"
    name = "Latin hillside self-built city"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (2, 5), "lane_spacing": 4, "lane_len": 10, "branch": 0.55, "loop": 0.35, "artery_share": 0.15,
            "block_cells": 9, "cut_turn": 4.0, "lot_cells": (2, 6), "courts": False,
            "e1_levels": (1, 2), "max_levels": 6, "civic_levels": 2, "tower_levels": (4, 6), "tower_cells": 2,
            "sabat_from": 2, "jetty_from": 2, "work_share": 0.15, "civic_min_cells": 8, "flats_per_level": False,
            "epochs": {2: {"rise": 0.7, "setback": 0.2, "sabat": 0.08, "jetty": 0.15, "tower": 0.06},
                       3: {"rise": 0.6, "setback": 0.25, "sabat": 0.1, "jetty": 0.2, "tower": 0.08},
                       4: {"rise": 0.5, "setback": 0.3, "sabat": 0.1, "jetty": 0.25, "tower": 0.1}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.5, "street_blades": 0.05,
            "shacks": 0.06,
        },
        "palettes": [
            {"wall": "#b2603e", "trim": "#8f8d88", "frame": "#5a5a58", "glass": "#2a3238", "screen": "#3a3a3a",
             "roof": "#8f8d88", "metal": "#2a6ab0", "fabric": "#f6cf3a", "emissive": "#ffe08a", "tile": "#5bb7e5",
             "water": "#3a6a7a", "ground": "#8f8d88", "plant": "#4f8a3a"},
            {"wall": "#f07ca8", "trim": "#f2efe6", "frame": "#3a3a3a", "glass": "#2a3238", "screen": "#3a3a3a",
             "roof": "#8f8d88", "metal": "#2a6ab0", "fabric": "#a8d14a", "emissive": "#ff6ad0", "tile": "#f6cf3a",
             "water": "#3a6a7a", "ground": "#8f8d88", "plant": "#4f8a3a"},
            {"wall": "#5bb7e5", "trim": "#f2efe6", "frame": "#3a3a3a", "glass": "#2a3238", "screen": "#3a3a3a",
             "roof": "#8f8d88", "metal": "#2a6ab0", "fabric": "#f08a2a", "emissive": "#6ad0ff", "tile": "#a8d14a",
             "water": "#3a6a7a", "ground": "#8f8d88", "plant": "#4f8a3a"},
            {"wall": "#f6cf3a", "trim": "#f2efe6", "frame": "#3a3a3a", "glass": "#2a3238", "screen": "#3a3a3a",
             "roof": "#8f8d88", "metal": "#2a6ab0", "fabric": "#c23a2e", "emissive": "#a8ff6a", "tile": "#f07ca8",
             "water": "#3a6a7a", "ground": "#8f8d88", "plant": "#4f8a3a"},
        ],
        "variants": (0.4, 0.2, 0.2, 0.2), "civic_variant": 3,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.7), ("wall_shopfront_arcade", 0.3)],
            "ground": {"street": [("wall_shopfront", 0.35), ("wall_window_grille", 0.3), ("wall_door", 0.15),
                                  ("wall_plain", 0.2)],
                       "lane": [("wall_window_grille", 0.35), ("wall_door", 0.15), ("wall_plain", 0.5)]},
            "upper": {"street": [("wall_window_s", 0.25), ("wall_window_grille", 0.2), ("wall_window_m", 0.15),
                                 ("wall_balcony_iron", 0.08), ("wall_plain", 0.32)],
                      "lane": [("wall_window_s", 0.3), ("wall_window_grille", 0.15), ("wall_brick_raw_t", 0.25),
                               ("wall_mural_t", 0.04), ("wall_plain", 0.26)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": None},
        "marks": [{"type": "playground"},
                  {"type": "civic_tower", "pieces": ["bell_tower_baroque_base", "bell_tower_baroque_base",
                                                     "bell_tower_baroque_belfry", "bell_tower_baroque_cupola"], "storeys": 3}],
        "overlay": {"roof_items": [("ov_rebar_stubs", 0.1), ("ov_tank_round_blue", 0.35)], "tank": 0.05, "laundry": 0.15, "dish": 0.08, "antenna": 0.03, "cable": 0.55, "lantern": 0.2,
                    "lane_laundry": 0.15, "ac": 0.04},
        "foliage": {"green": ["banana", "papaya", "mango", "banana"], "bank": ["banana", "reeds"],
                    "lane_wall": ["bougainvillea"], "roof": ["monstera_pot"], "plaza": ["mango"],
                    "rates": {"roof": 0.06, "lane_wall": 0.06}},
        "kit_requests": [
            ("ov_rebar_stubs", "rebar stubs sticking up at a laje's columns (roof decor)", "none"),
            ("ov_tank_round_blue", "the round blue fibreglass roof water tank (overlay; metal slot blue)", "ov_tank"),
            ("wall_brick_raw_t", "a hollow clay brick infill bay in a concrete frame (wall)", "wall_plain_t raw-brick palette"),
            ("wall_mural_t", "a mural-painted blank bay (wall, emissive-free)", "wall_plain_t"),
            ("stair_painted", "a concrete stair flight with each step a colour, handrails (stair)", "stair_run"),
            ("wall_tin_corrugated_t", "Valparaiso corrugated-iron cladding bay (wall)", "wall_plain_t"),
            ("cable_car", "cable car line + cabin over the hill (decor, later)", "none"),
        ],
    }

    def roof_field(self, i, j, level, epoch):
        from pick import h01
        return ("roof_tin" if h01("tin", i, j) < 0.2 else "roof_terrace", 0, 0)
