"""Pre-Saharan earth kasbah and ksar (r1_saharan_kasbah.md: Ait Benhaddou, the Draa and Dades, Ksar Ouled Soltane).

The mark: rammed-earth clusters stepping up a slope, crowned by tapering corner towers 12-18 m with crenellated
pinnacle tops and relief panels of chevrons and lozenges in their upper third; slits low, paired grilled windows
higher; narrow covered lanes and stairs; ghorfa honeycombs of vaulted granary cells round a court; palms at the
river; at night, light lines at the lift joints and signal lamps on the towers."""
from civ.family import FamilyCiv


class SaharanKasbah(FamilyCiv):
    id = "saharan_kasbah"
    name = "Pre-Saharan earth kasbah"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (2, 6), "lane_spacing": 4, "lane_len": 12, "branch": 0.5, "loop": 0.3, "artery_share": 0.15,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (5, 12), "courts": True, "court_min_lot": 9,
            "court_share": 0.12, "e1_levels": (2, 3), "max_levels": 3, "civic_levels": 2, "sabat_from": 1,
            "tower_levels": (4, 6), "tower_cells": 1, "work_share": 0.15, "civic_min_cells": 10, "shop_share": 0.4,
            "epochs": {2: {"rise": 0.4, "setback": 0.25, "sabat": 0.2, "tower": 0.3},
                       3: {"rise": 0.3, "setback": 0.3, "sabat": 0.25, "tower": 0.25},
                       4: {"rise": 0.2, "setback": 0.35, "sabat": 0.2, "tower": 0.15}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.15, "street_blades": 0.0,
            "shacks": 0.02,
        },
        "variants": (0.3, 0.3, 0.25, 0.15), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.5), ("wall_arch_round", 0.5)],
            "ground": {"street": [("wall_window_s", 0.2), ("wall_door", 0.15), ("wall_plain", 0.65)],
                       "lane": [("wall_slit_k", 0.25), ("wall_plain", 0.75)],
                       "court": [("wall_door", 0.4), ("wall_window_s", 0.3), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_window_grille", 0.3), ("wall_window_s", 0.2), ("wall_plain", 0.5)],
                      "lane": [("wall_window_grille", 0.2), ("wall_window_s", 0.15), ("wall_plain", 0.65)],
                      "court": [("wall_door", 0.35), ("wall_window_s", 0.25), ("wall_plain", 0.4)],
                      "air": [("wall_beam_ends_k", 0.2), ("wall_slit_k", 0.2), ("wall_plain", 0.6)]},
            "tower": [("wall_earth_relief_k", 0.5), ("wall_window_grille", 0.2), ("wall_plain", 0.3)], "tower_from": 3,
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_parapet_pinnacle_k", "crown_civic": None},
        "marks": [{"type": "civic_tower", "pieces": ["tower_kasbah_corner_base", "tower_kasbah_corner_shaft",
                                                     "tower_kasbah_corner_top"], "storeys": 5},
                  {"type": "roof_towers", "piece": "tower_kasbah_corner_shaft", "top": "tower_kasbah_corner_top",
                   "share": 0.02, "storeys": (1, 2)},
                  {"type": "plan_piece", "cls": "court", "piece": "ghorfa_cell", "share": 0.12, "max": 16, "epoch": 1},
                  {"type": "stalls", "share": 0.08}],
        "overlay": {"band": {"piece": "band_brick_relief", "p": 0.4, "from": 2}, "lantern": 0.35, "dish": 0.1,
                    "cable": 0.05, "awning": 0.3},
        "foliage": {"green": ["date_palm", "date_palm", "tamarisk", "olive", "almond"], "bank": ["date_palm", "tamarisk"],
                    "plaza": ["acacia"], "court": ["date_palm"], "rates": {"green": 0.55, "court": 0.2}},
        "kit_requests": [
            ("tower_kasbah_corner", "the tapering earth corner tower with pinnacled crenel top and relief panels (base, shaft, top)", "rooms + edge_parapet_crenel_k"),
            ("wall_earth_relief_k", "earth wall bay with chevron/lozenge relief in the top third (wall)", "band_brick_relief overlay"),
            ("ghorfa_cell", "the vaulted ghorfa granary cell with a small painted door, stackable 3-6 high round a court (cell)", "rooms"),
            ("wall_slit_k", "a defensive slit window in a thick earth wall (wall)", "wall_window_s_k"),
            ("edge_parapet_pinnacle_k", "crenel parapet with pinnacle corners (edge)", "edge_parapet_crenel_k"),
        ],
    }
