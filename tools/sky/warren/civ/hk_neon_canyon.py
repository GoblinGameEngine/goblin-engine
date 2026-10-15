"""Hong Kong tong lau and the neon canyon (r2_hk_neon_canyon.md: Mong Kok, Sham Shui Po, Yau Ma Tei).

The mark: a street grid of identical-width walk-ups 4-12 storeys, heights jumping within a row; ground floors wide open
to shops with roller shutters; steel casement windows in pairs, green-railed balconies, enclosed balconies and window
cages; back lanes of pipes and AC; flat roofs with tanks, huts and aerials; a canyon of signs on arms out over the
street to six storeys; a temple square and a rooftop playground."""
from civ.family import FamilyCiv


class HkNeonCanyon(FamilyCiv):
    id = "hk_neon_canyon"
    name = "Hong Kong neon canyon"
    arch_mouth = None
    covered_ceiling = "alley_ceiling"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (5, 8), "jog": 0.05, "blind": 0.12, "break": 0.03, "light_wells": 0.02,
            "lot_cells": (3, 8), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (3, 4), "max_levels": 12, "civic_levels": 2, "tower_levels": (6, 12),
            "jetty_from": 2, "sabat_from": 9, "work_share": 0.3, "civic_min_cells": 6,
            "epochs": {2: {"rise": 0.5, "setback": 0.0, "tower": 0.2, "tower_levels": (6, 8), "jetty": 0.15},
                       3: {"rise": 0.45, "setback": 0.0, "tower": 0.3, "tower_levels": (7, 10), "jetty": 0.2},
                       4: {"rise": 0.35, "setback": 0.0, "tower": 0.3, "tower_levels": (9, 12), "jetty": 0.2}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 1.0, "street_blades": 0.75,
            "shacks": 0.12, "enter_doors": 0.1,
        },
        "variants": (0.3, 0.25, 0.25, 0.2), "civic_variant": 2,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.85), ("wall_door", 0.15)],
            "ground": {"street": [("wall_shopfront", 0.75), ("wall_door", 0.25)],
                       "lane": [("wall_door", 0.25), ("wall_window_grille", 0.3), ("wall_plain", 0.45)]},
            "upper": {"street": [("wall_window_casement_pair_t", 0.25), ("wall_balcony_cage", 0.15), ("wall_verandah_t", 0.1),
                                 ("wall_mosaic_t", 0.12), ("wall_kowloon_stack_t", 0.05), ("wall_window_m", 0.1),
                                 ("wall_plain", 0.23)],
                      "lane": [("wall_window_s", 0.3), ("wall_balcony_cage", 0.08), ("wall_plain", 0.62)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "green_hip"},
        "marks": [{"type": "playground"}, {"type": "stalls", "share": 0.12}],
        "overlay": {"face_items": [{"piece": "ov_sign_arm_big", "p": 0.12, "where": "upper", "epoch": 5},
                               {"piece": "ov_roller_shutter", "p": 0.25, "shops": True, "epoch": 5}],
                    "sign_column": 0.35, "ac": 0.25, "pipe": 0.25, "tank": 0.12, "antenna": 0.15, "laundry": 0.05, "cable": 0.3,
                    "lane_laundry": 0.1, "fluoro": 0.6, "lantern": 0.3},
        "foliage": {"plaza": ["banyan_tree", "bauhinia"], "green": ["banyan_tree", "bauhinia", "palm_fan"],
                    "bank": ["banyan_tree", "reeds"], "roof": ["potted_plants"], "lane_wall": ["banyan_wall"],
                    "rates": {"roof": 0.05, "lane_wall": 0.02}},
        "kit_requests": [
            ("ov_sign_arm_big", "a 2-6 storey neon sign on a steel arm over the street (face overlay, several storeys)", "ov_sign_blade anchors"),
            ("wall_verandah_t", "pre-war tong lau verandah bay: columns at the street edge, balcony over the pavement (wall)", "wall_balcony_iron_t"),
            ("wall_mosaic_t", "1960s mosaic-tile panel bay (wall)", "wall_plain_t"),
            ("wall_window_casement_pair_t", "steel casement windows in pairs, green frames (wall)", "wall_window_pair_t"),
            ("ov_roller_shutter", "a half-down roller shutter over a shopfront (face overlay)", "none"),
        ],
    }
