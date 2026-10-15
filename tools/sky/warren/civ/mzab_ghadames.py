"""Saharan whitewash oasis (r1_mzab_ghadames.md: Ghardaia and the M'zab, Ghadames).

The mark: one soft hand-plastered mass -- pastel cubes (white, sky blue, pink, ochre: a colour per house) packed in a
cone round the hill to a single battered pyramid minaret, or roofed over into Ghadames' covered sabats (tunnels lit by
light-wells), the roofs joined into one walkable women's city; tiny rounded openings, corner horns on the parapets,
round-arched roof loggias; the palm grove below as the green belt."""
from civ.family import FamilyCiv


class MzabGhadames(FamilyCiv):
    id = "mzab_ghadames"
    name = "Saharan whitewash oasis"
    covered_ceiling = "lightwell_shaft"
    arch_mouth = "wall_arch_round"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (2, 5), "lane_spacing": 4, "lane_len": 12, "branch": 0.45, "loop": 0.3, "artery_share": 0.2,
            "block_cells": 9, "cut_turn": 4.0, "lot_cells": (5, 11), "courts": True, "court_min_lot": 9,
            "court_share": 0.08, "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 2, "sabat_from": 1,
            "work_share": 0.1, "civic_min_cells": 8, "roof_walk": True,
            "epochs": {2: {"rise": 0.5, "setback": 0.25, "sabat": 0.45},
                       3: {"rise": 0.35, "setback": 0.3, "sabat": 0.55},
                       4: {"rise": 0.2, "setback": 0.4, "sabat": 0.5}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.2, "street_blades": 0.0,
            "shacks": 0.0,
        },
        "palettes": [
            {"wall": "#f4f1ea", "trim": "#fbfaf5", "frame": "#3a7a8a", "glass": "#2a3a44", "screen": "#3a7a8a",
             "roof": "#ece6da", "metal": "#4a4440", "fabric": "#c8402a", "emissive": "#ffc070", "tile": "#2a8a4a",
             "water": "#3d7f8c", "ground": "#e6dccb", "plant": "#5b7f3a"},
            {"wall": "#9fc3d9", "trim": "#f4f1ea", "frame": "#2a5a8a", "glass": "#2a3a44", "screen": "#2a5a8a",
             "roof": "#ece6da", "metal": "#4a4440", "fabric": "#c8402a", "emissive": "#9fd0ff", "tile": "#2a8a4a",
             "water": "#3d7f8c", "ground": "#e6dccb", "plant": "#5b7f3a"},
            {"wall": "#e7c3b8", "trim": "#f4f1ea", "frame": "#7a3a2a", "glass": "#2a3a44", "screen": "#7a3a2a",
             "roof": "#ece6da", "metal": "#4a4440", "fabric": "#2a8a4a", "emissive": "#ffb0c0", "tile": "#c8402a",
             "water": "#3d7f8c", "ground": "#e6dccb", "plant": "#5b7f3a"},
            {"wall": "#d9b07a", "trim": "#f4f1ea", "frame": "#2a6a4a", "glass": "#2a3a44", "screen": "#2a6a4a",
             "roof": "#d9c09a", "metal": "#4a4440", "fabric": "#c8402a", "emissive": "#ffc070", "tile": "#2a8a4a",
             "water": "#3d7f8c", "ground": "#d8c4a4", "plant": "#5b7f3a"},
        ],
        "variants": (0.34, 0.24, 0.2, 0.22), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_triangles_k",
            "shop": [("wall_shopfront_arcade", 0.5), ("wall_arch_round", 0.5)],
            "ground": {"street": [("wall_plain", 0.8), ("wall_window_s", 0.2)],
                       "lane": [("wall_plain", 0.9), ("wall_window_s", 0.1)]},
            "upper": {"street": [("wall_plain", 0.7), ("wall_window_s", 0.25), ("wall_arch_round", 0.05)],
                      "lane": [("wall_plain", 0.78), ("wall_window_s", 0.22)],
                      "court": [("wall_arch_round", 0.6), ("wall_plain", 0.4)]},
            "tower": [("wall_arch_round", 0.55), ("wall_plain", 0.45)], "tower_from": 2,
        },
        "corner": "corner_round",
        "roof": {"field": "roof_terrace", "edge": "edge_parapet_horn_k"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_pyramid_base", "minaret_pyramid_shaft", "minaret_pyramid_top"], "storeys": 6},
                  {"type": "stalls", "share": 0.1}, {"type": "fountain", "piece": "well_pulley"}],
        "overlay": {"face_items": [{"piece": "dukkana_bench", "p": 0.12}], "lantern": 0.45, "festoon": 0.25, "fluoro": 0.4, "dish": 0.04, "laundry": 0.03, "cable": 0.02},
        "foliage": {"green": ["date_palm", "date_palm", "pomegranate", "fig"], "bank": ["date_palm", "reeds"],
                    "court": ["fig"], "roof": ["pot_herbs"], "rates": {"green": 0.55, "court": 0.3, "roof": 0.05}},
        "kit_requests": [
            ("edge_parapet_horn_k", "Ghadames/M'zab parapet with whitewashed triangular corner horns (trim slot)", "edge_parapet_rounded_k"),
            ("minaret_pyramid", "the M'zab minaret: square battered truncated pyramid 15-25 m, four corner horns on top (3 parts: base, shaft taper, horned top)", "minaret_base x5 + minaret_top"),
            ("dukkana_bench", "a mud bench along a covered-lane wall (face overlay at ground)", "none"),
            ("well_pulley", "a well with a timber pulley frame (cell decor)", "fountain_riad"),
            ("wall_triangles_k", "a door bay with painted red/green triangles and diamonds round it (Ghadames)", "wall_door_k"),
            ("lightwell_shaft", "the light-well opening in a covered-lane ceiling (ceiling piece with a lit hole)", "sabat_beams"),
        ],
    }
