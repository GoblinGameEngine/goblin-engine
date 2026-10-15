"""Hanseatic gable towns (r3_hanseatic_gable.md: Amsterdam, Tallinn, Bergen's Bryggen, Copenhagen's Nyhavn).

The mark: rows of narrow tall merchant houses, one plot each, packed gable to gable along quays and straight streets,
each a different colour and gable; 60% glass in big white-framed windows; trading doors and shops on the ground; steep
pantile roofs behind the gables (stand-in: a hip per cell, so a row reads as a saw of gables); a brick church tower;
lindens and elms along the water; warm windows doubled in the canals at night."""
from civ.family import FamilyCiv


class HanseaticGable(FamilyCiv):
    id = "hanseatic_gable"
    kerb = "quay_edge_stone"
    name = "Hanseatic gable town"
    arch_mouth = "wall_arch_pointed"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (4, 7), "jog": 0.08, "blind": 0.12, "break": 0.04, "light_wells": 0.0,
            "lot_cells": (2, 5), "courts": False, "flats_per_level": False, "roof_walk": False,
            "e1_levels": (3, 4), "max_levels": 5, "civic_levels": 3, "sabat_from": 9, "jetty_from": 9,
            "work_share": 0.3, "civic_min_cells": 8,
            "epochs": {2: {"rise": 0.45, "setback": 0.0, "sabat": 0.0},
                       3: {"rise": 0.35, "setback": 0.0, "sabat": 0.0},
                       4: {"rise": 0.2, "setback": 0.05, "sabat": 0.0}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.5, "street_blades": 0.06,
            "shacks": 0.0, "enter_doors": 0.15,
        },
        "palettes": [
            {"wall": "#8c3b2a", "trim": "#f5f3ee", "frame": "#f5f3ee", "glass": "#2a3440", "screen": "#2a4a32",
             "roof": "#5a3a2e", "metal": "#2a2a2a", "fabric": "#2a4a32", "emissive": "#ffd08a", "tile": "#4f8f78",
             "water": "#3b5a6a", "ground": "#8a5a44", "plant": "#4f7a3a"},
            {"wall": "#4a2a20", "trim": "#f5f3ee", "frame": "#f5f3ee", "glass": "#2a3440", "screen": "#2a4a32",
             "roof": "#4a3a34", "metal": "#2a2a2a", "fabric": "#b2402e", "emissive": "#ffd08a", "tile": "#4f8f78",
             "water": "#3b5a6a", "ground": "#8a5a44", "plant": "#4f7a3a"},
            {"wall": "#e7b84a", "trim": "#f5f3ee", "frame": "#f5f3ee", "glass": "#2a3440", "screen": "#2a4a32",
             "roof": "#5a3a2e", "metal": "#2a2a2a", "fabric": "#3f6fa8", "emissive": "#ffd08a", "tile": "#4f8f78",
             "water": "#3b5a6a", "ground": "#8a5a44", "plant": "#4f7a3a"},
            {"wall": "#ece6d6", "trim": "#f5f3ee", "frame": "#2a4a32", "glass": "#2a3440", "screen": "#2a4a32",
             "roof": "#3a3a3e", "metal": "#2a2a2a", "fabric": "#b2402e", "emissive": "#ffd08a", "tile": "#4f8f78",
             "water": "#3b5a6a", "ground": "#8a5a44", "plant": "#4f7a3a"},
        ],
        "variants": (0.32, 0.24, 0.24, 0.2), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.75), ("wall_window_l", 0.25)],
            "ground": {"street": [("wall_window_l", 0.55), ("wall_door", 0.2), ("wall_shopfront", 0.25)],
                       "lane": [("wall_window_m", 0.5), ("wall_door", 0.2), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_window_pair", 0.4), ("wall_window_l", 0.3), ("wall_window_m", 0.18),
                                 ("wall_luiken_k", 0.12)],
                      "lane": [("wall_window_pair", 0.3), ("wall_window_m", 0.4), ("wall_plain", 0.3)],
                      "air": [("wall_window_m", 0.4), ("wall_plain", 0.6)]},
            "civic_ground": [("wall_arch_pointed", 0.6), ("wall_plain", 0.4)],
            "civic_upper": [("wall_arch_pointed", 0.5), ("wall_plain", 0.5)],
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": None,
                 "pitched": {"run": "roof_pitched_pantile", "end": "roof_pitched_pantile_end", "civic": True},
                 "edge_street": [("edge_gable_step", 0.35), ("edge_gable_neck", 0.35), ("edge_gable_bell", 0.3)]},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "church_spire_copper"], "storeys": 5},
                  {"type": "stalls", "share": 0.08}],
        "overlay": {"face_items": [{"piece": "hoist_beam", "p": 0.25, "where": "top"}], "lantern": 0.4, "festoon": 0.45, "cable": 0.06, "dish": 0.02, "laundry": 0.0},
        "foliage": {"green": ["linden", "elm", "chestnut", "pear"], "bank": ["willow", "elm", "linden"],
                    "plaza": ["chestnut", "linden"], "lane_wall": ["hollyhock"], "rates": {"plaza": 0.06, "bank": 0.45}},
        "kit_requests": [
            ("edge_gable_step", "a stepped (crow-step) gable front over a 1-bay house (used on every street front)", "-"),
            ("edge_gable_neck", "a neck gable with sandstone scrolls", "-"),
            ("edge_gable_bell", "a bell gable", "-"),
            ("roof_pitched_pantile", "a 50-60 deg pantile/slate roof run behind the gable, ridge along the house depth (cell, span [1, n]); the hip-per-cell stand-in reads as a field of pyramids from above", "green_hip per cell"),
            ("hoist_beam", "the attic hoist beam with hook over the luiken hatch column (face overlay at the top storey)", "none"),
            ("wall_luiken_k", "the attic hatch column bay: stacked shutters, white frame (wall)", "wall_window_m_k"),
            ("church_spire_copper", "a verdigris copper spire over a brick tower (crown)", "green_hip on a minaret shaft"),
            ("bridge_humped_brick", "a humped brick canal bridge with bulb strings (cell, span [1, 3])", "none"),
            ("quay_edge_stone", "a stone quay edge with mooring rings (water_edge)", "kerb_straight"),
        ],
    }
