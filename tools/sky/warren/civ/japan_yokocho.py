"""Japanese backstreets (r2_japan_yokocho.md: Tokyo, Osaka, Kyoto) -- zakkyo towers, yokocho alleys and machiya.

The mark: blocks cut into very narrow plots; pencil-thin 5-10 storey multi-tenant towers on the street edges, each
a column of lit signs, over 1-2 m alleys of tiny bars under red lanterns and noren; low 2-storey timber-lattice
machiya with grey tile roofs inside the blocks; overhead wire webs; vending machines; a shrine with its trees."""
from civ.family import FamilyCiv


class JapanYokocho(FamilyCiv):
    id = "japan_yokocho"
    name = "Japanese backstreets"
    arch_mouth = None
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (3, 5), "jog": 0.2, "blind": 0.3, "break": 0.05, "light_wells": 0.0,
            "lot_cells": (2, 5), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (2, 2), "max_levels": 10, "civic_levels": 2, "tower_levels": (5, 8), "tower_cells": 2,
            "sabat_from": 9, "jetty_from": 9, "work_share": 0.35, "civic_min_cells": 6,
            "epochs": {2: {"rise": 0.35, "setback": 0.0, "tower": 0.18, "tower_levels": (4, 6)},
                       3: {"rise": 0.25, "setback": 0.0, "tower": 0.25, "tower_levels": (5, 8)},
                       4: {"rise": 0.2, "setback": 0.0, "tower": 0.25, "tower_levels": (6, 10)}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 1.0, "street_blades": 0.6,
            "shacks": 0.03, "enter_doors": 0.2,
        },
        "palettes": [
            {"wall": "#c9c4b8", "trim": "#e8e4da", "frame": "#5a4634", "glass": "#2a3238", "screen": "#5a4634",
             "roof": "#4a4a4c", "metal": "#6a6a6a", "fabric": "#2a3a6a", "emissive": "#ff5a3a", "tile": "#d8cfbd",
             "water": "#3a5a6a", "ground": "#6e6b64", "plant": "#2f5a2a"},
            {"wall": "#8f8a80", "trim": "#c9c4b8", "frame": "#3a3a3a", "glass": "#2a3238", "screen": "#3a3a3a",
             "roof": "#3e3e40", "metal": "#5a5a5a", "fabric": "#b23a2e", "emissive": "#3fe0ff", "tile": "#c9c4b8",
             "water": "#3a5a6a", "ground": "#6e6b64", "plant": "#2f5a2a"},
            {"wall": "#5a4634", "trim": "#d8cfbd", "frame": "#3a2a1c", "glass": "#2a3238", "screen": "#4a3624",
             "roof": "#3a3a3e", "metal": "#4a4a4a", "fabric": "#2a3a6a", "emissive": "#ff7a3a", "tile": "#d8cfbd",
             "water": "#3a5a6a", "ground": "#6e6b64", "plant": "#2f5a2a"},
            {"wall": "#d8cfbd", "trim": "#f0ece2", "frame": "#5a4634", "glass": "#2a3238", "screen": "#5a4634",
             "roof": "#4a4a4c", "metal": "#6a6a6a", "fabric": "#b23a2e", "emissive": "#ff3fa4", "tile": "#c9c4b8",
             "water": "#3a5a6a", "ground": "#6e6b64", "plant": "#2f5a2a"},
        ],
        "variants": (0.3, 0.3, 0.25, 0.15), "civic_variant": 2,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.75), ("wall_shopfront_arcade", 0.25)],
            "ground": {"street": [("wall_shopfront", 0.5), ("wall_door", 0.2), ("wall_koshi_t", 0.3)],
                       "lane": [("wall_noren_t", 0.4), ("wall_shopfront_arcade", 0.15), ("wall_koshi_t", 0.25),
                                ("wall_door", 0.1), ("wall_plain", 0.1)]},
            "upper": {"street": [("wall_window_l", 0.3), ("wall_window_m", 0.25), ("wall_window_pair", 0.15),
                                 ("wall_plain", 0.3)],
                      "lane": [("wall_window_s", 0.3), ("wall_screen", 0.15), ("wall_plain", 0.55)],
                      "air": [("wall_window_s", 0.25), ("wall_plain", 0.75)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "green_hip",
                 "pitched": {"run": "roof_kawara_low", "end": "roof_kawara_low_end", "max_rel": 2, "civic": True}},
        "marks": [{"type": "stalls", "share": 0.05}, {"type": "gate_piece", "piece": "torii"}],
        "overlay": {"spans": [("ov_chochin_string", 0.35)], "sign_column": 0.55, "vending": 0.04, "pole": 0.35,
                    "cable": 0.45, "ac": 0.15, "tank": 0.12, "antenna": 0.05, "lantern": 0.75, "festoon": 0.2,
                    "pipe": 0.2, "fluoro": 0.5},
        "foliage": {"plaza": ["zelkova", "ginkgo"], "green": ["japanese_maple", "pine_pruned", "sakura", "sakura"],
                    "bank": ["sakura", "willow"], "lane": ["potted_plants"], "lane_wall": ["potted_plants"],
                    "roof": ["potted_plants"], "rates": {"lane": 0.15, "lane_wall": 0.1, "green": 0.5}},
        "kit_requests": [
            ("ov_sign_vertical_stack", "a column of lightbox signs, one per storey, on a zakkyo street face (face overlay spanning n storeys or one per storey)", "ov_sign_blade anchors"),
            ("ov_chochin_string", "lantern strings across alleys (used on 35% of lane spans)", "-"),
            ("wall_noren_t", "bar door with noren and lanterns (used on 40% of alley ground faces)", "-"),
            ("ov_vending_machine", "1-3 glowing vending machines against a wall (face overlay, ground)", "none"),
            ("stair_steel_external", "the zakkyo's external steel stair (face overlay climbing one storey)", "none"),
            ("utility_pole", "concrete pole with transformer and wire bundles (cell decor)", "ov_cables"),
            ("torii", "a vermilion shrine gate (cell, span [1, 1])", "none"),
            ("roof_kawara_low", "a low grey kawara tile roof for 2-storey machiya (cell roof with eaves)", "green_hip on low roofs"),
            ("wall_koshi_t", "a machiya bay with the koshi timber lattice (wall)", "wall_screen_t"),
        ],
    }
