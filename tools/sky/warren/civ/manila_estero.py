"""Manila: Binondo and the estero settlements (r2_manila_estero.md: Intramuros, Binondo, Tondo).

The mark: the old core of bahay na bato -- stone or adobe ground floors with timber upper storeys overhanging the
street, capiz-shell sliding windows over balustered ventanillas, hipped tile roofs with deep eaves -- round a church
plaza with arcaded Chinese shophouses; and at the edges, dense stilt shanties of plywood and galvanized iron packed
along the esteros, 1-3 storeys, roofs held down with tyres; basketball courts in every quarter; jeepney colours."""
from civ.family import FamilyCiv


class ManilaEstero(FamilyCiv):
    id = "manila_estero"
    name = "Manila estero city"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 8), "lane_spacing": 4, "lane_len": 14, "branch": 0.5, "loop": 0.35, "artery_share": 0.3,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (3, 9), "courts": False,
            "e1_levels": (2, 2), "max_levels": 4, "civic_levels": 3, "sabat_from": 1, "jetty_from": 1,
            "work_share": 0.2, "civic_min_cells": 12, "shop_share": 0.7, "stilts": 0.6,
            "epochs": {2: {"rise": 0.35, "setback": 0.1, "jetty": 0.25, "sabat": 0.05},
                       3: {"rise": 0.3, "setback": 0.15, "jetty": 0.3, "sabat": 0.05},
                       4: {"rise": 0.25, "setback": 0.15, "jetty": 0.3, "sabat": 0.05}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.7, "street_blades": 0.15,
            "shacks": 0.2,
        },
        "stilt_piece": "stilt_frame",
        "variants": (0.3, 0.25, 0.25, 0.2), "civic_variant": 0, "ground_variant": 0,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_arch_round", 0.25), ("wall_shopfront", 0.3), ("wall_door", 0.2), ("wall_plain", 0.25)],
                       "lane": [("wall_door", 0.3), ("wall_window_grille", 0.2), ("wall_plain", 0.5)]},
            "upper": {"street": [("wall_screen", 0.45), ("wall_window_m", 0.2), ("wall_balcony_timber", 0.1), ("wall_plain", 0.25)],
                      "lane": [("wall_screen", 0.3), ("wall_window_s", 0.25), ("wall_plain", 0.45)],
                      "green": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
            "civic_ground": [("wall_arch_round", 0.6), ("wall_plain", 0.4)],
            "civic_upper": [("wall_window_l", 0.4), ("wall_blind_arch", 0.3), ("wall_plain", 0.3)],
        },
        "corner": None,
        "roof": {"field": "roof_tin", "edge": "edge_eave_tin", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tile_red_low", "end": "roof_tile_red_low_end", "share": 0.5}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 5},
                  {"type": "playground"}, {"type": "stalls", "share": 0.2}],
        "overlay": {"cable": 0.6, "pole": 0.25, "laundry": 0.15, "lane_laundry": 0.15, "tank": 0.15, "dish": 0.1,
                    "festoon": 0.4, "lantern": 0.35, "roof_items": [("ov_rebar_stubs", 0.04)]},
        "foliage": {"plaza": ["acacia", "narra"], "green": ["mango", "acacia", "banana", "coconut_palm"],
                    "bank": ["mangrove", "banana"], "lane_wall": ["bougainvillea", "sampaguita_pot"], "rates": {"bank": 0.4}},
        "kit_requests": [
            ("wall_capiz_t", "the capiz-shell sliding window storey over balustered ventanillas, timber, overhanging (wall)", "wall_screen_t"),
            ("wall_adobe_ground_k", "the adobe/stone ground storey of a bahay na bato (wall)", "wall_plain on the stone variant"),
            ("ov_shanty_gi", "a plywood and galvanized-iron shanty box on stilts with tyres on the roof (roof/cell overlay)", "ov_shack + stilts"),
            ("basketball_court", "a half basketball court with hoop (cell decor, 2x3)", "ov_playground"),
            ("ov_jeepney", "a parked jeepney (street decor)", "none"),
        ],
    }
