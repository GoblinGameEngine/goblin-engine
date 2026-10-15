"""Upper Mesopotamian stone terraces (r3_mardin_terraces.md: Mardin, Midyat, Hasankeyf).

The mark: a honey limestone cascade down the slope, every roof a terrace for the house above; avlu courtyard houses
with an upper eyvan and triple-arched south loggias, carved window frames with geometric grilles, carved portals with
stone benches; abbara vaulted tunnels carrying the lanes under houses; carved balustrades on the terraces; square
carved minarets and ribbed domes; pomegranates, figs and vines."""
from civ.family import FamilyCiv


class MardinTerraces(FamilyCiv):
    id = "mardin_terraces"
    name = "Mardin stone terraces"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 4, "lane_len": 18, "branch": 0.35, "loop": 0.4, "artery_share": 0.25,
            "block_cells": 10, "cut_turn": 2.5, "lot_cells": (5, 12), "courts": True, "court_min_lot": 8,
            "court_share": 0.2, "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 3, "sabat_from": 1,
            "work_share": 0.15, "civic_min_cells": 10, "roof_walk": True, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.3, "setback": 0.5, "sabat": 0.25},
                       3: {"rise": 0.2, "setback": 0.55, "sabat": 0.25},
                       4: {"rise": 0.12, "setback": 0.6, "sabat": 0.2}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.35, "street_blades": 0.03,
            "shacks": 0.02,
        },
        "civic_court": True,
        "variants": (0.4, 0.3, 0.2, 0.1), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_arch_pointed",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_arch_pointed", 0.4)],
            "ground": {"street": [("wall_window_grille", 0.3), ("wall_door", 0.15), ("wall_arch_pointed", 0.15), ("wall_plain", 0.4)],
                       "lane": [("wall_window_grille", 0.25), ("wall_door", 0.1), ("wall_plain", 0.65)],
                       "court": [("wall_arch_pointed", 0.6), ("wall_window_m", 0.4)]},
            "upper": {"street": [("wall_arch_pointed", 0.2), ("wall_carved_frame_k", 0.4), ("wall_screen", 0.1), ("wall_plain", 0.3)],
                      "lane": [("wall_window_grille", 0.3), ("wall_arch_pointed", 0.15), ("wall_plain", 0.55)],
                      "court": [("wall_triple_arch_loggia_k", 0.15), ("wall_arch_pointed", 0.4), ("wall_window_m", 0.45)]},
            "civic_ground": [("wall_arch_pointed", 0.5), ("wall_blind_arch", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_blind_arch", 0.4), ("wall_window_s", 0.2), ("wall_plain", 0.4)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_balustrade_carved_k", "crown_civic": "dome_ribbed"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_square_carved_base", "minaret_square_carved_shaft", "minaret_square_carved_top"], "storeys": 5},
                  {"type": "stalls", "share": 0.12}],
        "overlay": {"covered_piece": ("abbara_vault", 0.6), "lantern": 0.4, "festoon": 0.25, "awning": 0.25, "dish": 0.1, "cable": 0.1},
        "foliage": {"plaza": ["plane_tree", "mulberry"], "green": ["pomegranate", "fig", "walnut", "pistachio"],
                    "bank": ["willow", "reeds"], "court": ["pomegranate", "fig", "grapevine_pergola"],
                    "roof": ["grapevine_pergola", "basil_pots"], "lane_wall": ["jasmine", "oleander"],
                    "rates": {"court": 0.55, "roof": 0.06}},
        "kit_requests": [
            ("wall_triple_arch_loggia_k", "the triple-arched south loggia of an upper eyvan (wall)", "wall_arch_pointed_k"),
            ("edge_balustrade_carved_k", "the carved stone balustrade round a roof terrace (edge)", "edge_parapet_jali_k"),
            ("abbara_vault", "the vaulted tunnel carrying a lane under a house (ceiling + portal)", "sabat_beams + arch mouth"),
            ("wall_carved_frame_k", "a pointed window in a carved frame with a geometric grille (wall)", "wall_window_grille"),
            ("minaret_square_carved", "the square carved Artuqid minaret (3 parts)", "minaret_base/shaft/top"),
        ],
    }
