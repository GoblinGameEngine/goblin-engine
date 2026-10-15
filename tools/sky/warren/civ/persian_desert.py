"""Persian desert city (r1_persian_desert.md: Yazd, Kashan, Kerman).

The mark: a low continuous mass of mud-brick and kahgel, 1-2 storeys, blank street walls broken only by portals with
two knockers; covered sabats every 20-50 m; a roofscape of domes and vaults you can walk across, pierced by badgir
wind towers of every height; inside, sunken courts with a pool, an iwan (talar) and coloured orsi windows; the bazaar
a chain of domes; cypress, pomegranate and plane trees in the bagh."""
from civ.family import FamilyCiv


class PersianDesert(FamilyCiv):
    id = "persian_desert"
    name = "Persian desert city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 9), "lane_spacing": 5, "lane_len": 16, "branch": 0.4, "loop": 0.35, "artery_share": 0.3,
            "block_cells": 12, "cut_turn": 3.5, "lot_cells": (8, 18), "courts": True, "court_min_lot": 8,
            "court_share": 0.25, "e1_levels": (1, 2), "max_levels": 2, "civic_levels": 2, "sabat_from": 1,
            "work_share": 0.15, "civic_min_cells": 14, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.3, "setback": 0.4, "sabat": 0.2},
                       3: {"rise": 0.2, "setback": 0.45, "sabat": 0.25},
                       4: {"rise": 0.1, "setback": 0.5, "sabat": 0.15}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (7, 6), "sign": 0.25, "street_blades": 0.0,
            "shacks": 0.0,
        },
        "civic_court": True,
        "variants": (0.35, 0.3, 0.1, 0.25), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_portal_knockers_k", "door_civic": "wall_arch_pointed",
            "shop": [("wall_shopfront_arcade", 0.7), ("wall_arch_pointed", 0.3)],
            "ground": {"street": [("wall_plain", 0.85), ("wall_window_s", 0.15)],
                       "lane": [("wall_plain", 0.92), ("wall_window_s", 0.08)],
                       "court": [("wall_talar_k", 0.3), ("wall_arch_pointed", 0.2), ("wall_orsi_k", 0.3), ("wall_window_m", 0.2)]},
            "upper": {"street": [("wall_plain", 0.8), ("wall_window_s", 0.2)],
                      "lane": [("wall_plain", 0.88), ("wall_window_s", 0.12)],
                      "court": [("wall_orsi_k", 0.4), ("wall_arch_pointed", 0.3), ("wall_window_m", 0.3)]},
            "civic_ground": [("wall_blind_arch", 0.4), ("wall_arch_pointed", 0.3), ("wall_plain", 0.3)],
            "civic_upper": [("wall_blind_arch", 0.5), ("wall_plain", 0.5)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown": "dome_mud", "crown_share": 0.12,
                 "crown_civic": "dome_turquoise_ribbed",
                 "pitched": {"run": "roof_vault_barrel", "end": "roof_vault_barrel", "share": 0.3}},
        "marks": [{"type": "roof_towers", "piece": "badgir_shaft", "top": "badgir_crown", "share": 0.04, "storeys": (1, 3)},
                  {"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 6},
                  {"type": "fountain"}],
        "overlay": {"roof_items": [("malqaf_scoop", 0.03)], "lantern": 0.4, "festoon": 0.25, "fluoro": 0.4, "dish": 0.05, "cable": 0.05},
        "foliage": {"court": ["pomegranate", "fig", "grapevine_pergola", "rose_beds"],
                    "plaza": ["chenar_plane", "italian_cypress"], "green": ["italian_cypress", "chenar_plane",
                                                                            "pomegranate", "pine", "rose_beds"],
                    "bank": ["italian_cypress", "reeds"], "rates": {"court": 0.6, "green": 0.5}},
        "kit_requests": [
            ("badgir", "the wind tower: a square shaft 3-30 m with vertical slot vents and a crown; 1-, 2-, 4- or 8-sided (base, shaft, crown)", "minaret_base stacks 1-3 storeys"),
            ("roof_vault_barrel", "a walkable mud-brick barrel vault roof over a cell (cell roof)", "roof_terrace"),
            ("dome_mud", "a plain mud-brick dome with an oculus (crown)", "dome_cap"),
            ("wall_orsi_k", "the orsi: a sash window of coloured glass in a wooden grid, glowing (wall, court side)", "wall_screen_k"),
            ("wall_portal_knockers_k", "the street portal: a recessed door with two knockers and a bench niche (wall, door)", "wall_door_k"),
            ("wall_talar_k", "the iwan/talar opening a full storey to the court with two columns (wall)", "wall_arch_pointed_k"),
        ],
    }
