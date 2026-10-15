"""Tyrrhenian canyon towns (r3_tyrrhenian_canyon.md: Naples' Spanish Quarters, Genoa's caruggi, Palermo).

The mark: 10:1 canyons: tuff and lime-render palazzi 5-8 storeys in ochre, oxblood, rose and sienna over vicoli 2-4 m;
bassi (one-room street-level homes with glazed doors) and shops below; tall french windows with a shallow iron
balcony on every opening and green louvred shutters; laundry lines across, wall shrines, lemon tubs on the lastrico
terraces, rooftop tin rooms; heavy damp at the base."""
from civ.family import FamilyCiv


class TyrrhenianCanyon(FamilyCiv):
    id = "tyrrhenian_canyon"
    name = "Tyrrhenian canyon town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (4, 7), "jog": 0.12, "blind": 0.08, "break": 0.04, "light_wells": 0.0,
            "lot_cells": (5, 12), "courts": True, "court_min_lot": 9, "court_share": 0.1,
            "flats_per_level": True, "roof_walk": False,
            "e1_levels": (4, 5), "max_levels": 8, "civic_levels": 3, "tower_levels": (6, 8),
            "sabat_from": 2, "jetty_from": 9, "work_share": 0.2, "civic_min_cells": 10, "shop_share": 0.7,
            "epochs": {2: {"rise": 0.45, "setback": 0.05, "sabat": 0.05},
                       3: {"rise": 0.4, "setback": 0.05, "sabat": 0.05, "tower": 0.05},
                       4: {"rise": 0.3, "setback": 0.1, "sabat": 0.04, "tower": 0.06}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.6, "street_blades": 0.15,
            "shacks": 0.15, "enter_doors": 0.25,
        },
        "variants": (0.28, 0.24, 0.24, 0.24), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_shopfront", 0.35), ("wall_door", 0.35), ("wall_window_l", 0.15), ("wall_plain", 0.15)],
                       "lane": [("wall_basso_t", 0.3), ("wall_door", 0.1), ("wall_shopfront", 0.15), ("wall_window_grille", 0.15), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_french_balcony_k", 0.6), ("wall_window_l", 0.25), ("wall_plain", 0.15)],
                      "lane": [("wall_french_balcony_k", 0.45), ("wall_window_l", 0.25), ("wall_plain", 0.3)],
                      "air": [("wall_window_m", 0.4), ("wall_plain", 0.6)]},
            "civic_ground": [("wall_arch_round", 0.5), ("wall_blind_arch", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_window_l", 0.5), ("wall_blind_arch", 0.2), ("wall_plain", 0.3)],
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tile_roman_low", "end": "roof_tile_roman_low_end", "share": 0.15}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "dome_cap"], "storeys": 6},
                  {"type": "fountain"}, {"type": "stalls", "share": 0.15}],
        "overlay": {"lane_laundry": 0.15, "spans": [("ov_laundry_line_lane", 0.3)],
                    "face_items": [{"piece": "band_damp", "p": 0.5}, {"piece": "ov_wall_shrine", "p": 0.03}], "laundry": 0.15, "cable": 0.3, "dish": 0.15, "tank": 0.08,
                    "antenna": 0.06, "lantern": 0.4, "ac": 0.12, "awning": 0.3},
        "foliage": {"plaza": ["umbrella_pine", "plane_tree"], "green": ["umbrella_pine", "lemon", "fig", "oleander"],
                    "bank": ["oleander"], "court": ["fig", "lemon"], "roof": ["lemon_tub", "bougainvillea_pot"],
                    "rates": {"roof": 0.1}},
        "kit_requests": [
            ("wall_basso_t", "the basso: a glazed street door into a one-room home, a chair outside (wall, ground)", "wall_door"),
            ("ov_wall_shrine", "a wall shrine (edicola) with a lamp and flowers at a corner (face overlay, emissive)", "none"),
            ("wall_french_balcony_k", "tall french window, green louvred shutters, shallow iron balcony (wall)", "wall_balcony_iron_k"),
            ("ov_laundry_line_lane", "laundry lines across a vicolo between opposite balconies (along X)", "ov_laundry"),
            ("band_damp", "the dark damp band 0-1.5 m on the ground storey (face overlay)", "none"),
        ],
    }
