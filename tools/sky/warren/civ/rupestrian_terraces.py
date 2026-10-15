"""Rupestrian terraces (r3_rupestrian_terraces.md: Matera's Sassi, Cappadocia's rock towns).

The mark: an inverted amphitheatre of rock-cut vault cells stepping down the slope in contour rows, each row's roof
the lane of the row above; deep arched doors with lunettes and small square windows; whitewashed vault humps and vine
pergolas on the roofs; straight stair-lanes downhill, belvederes, vicinato cistern courts; the cathedral on the
crest; lemon gardens under pergolas."""
from civ.family import FamilyCiv


class RupestrianTerraces(FamilyCiv):
    id = "rupestrian_terraces"
    name = "Rupestrian terraces"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 4, "lane_len": 18, "branch": 0.35, "loop": 0.4, "artery_share": 0.2,
            "block_cells": 9, "cut_turn": 2.5, "lot_cells": (3, 8), "courts": True, "court_min_lot": 8,
            "court_share": 0.15, "e1_levels": (1, 2), "max_levels": 4, "civic_levels": 3, "sabat_from": 1,
            "work_share": 0.15, "civic_min_cells": 10, "roof_walk": True, "shop_share": 0.4,
            "epochs": {2: {"rise": 0.35, "setback": 0.45, "sabat": 0.15},
                       3: {"rise": 0.3, "setback": 0.5, "sabat": 0.15},
                       4: {"rise": 0.2, "setback": 0.55, "sabat": 0.1}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.3, "street_blades": 0.0,
            "shacks": 0.02,
        },
        "variants": (0.35, 0.3, 0.1, 0.25), "civic_variant": 3,
        "thick": 1,
        "facade": {
            "door": "wall_cave_door_k",
            "shop": [("wall_arch_round", 0.6), ("wall_shopfront_arcade", 0.4)],
            "ground": {"street": [("wall_arch_round", 0.35), ("wall_window_s", 0.25), ("wall_plain", 0.4)],
                       "lane": [("wall_cave_door_k", 0.2), ("wall_window_s", 0.2), ("rock_face_cut", 0.3), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_arch_round", 0.25), ("wall_window_s", 0.3), ("wall_plain", 0.45)],
                      "lane": [("wall_arch_round", 0.2), ("wall_window_s", 0.25), ("wall_plain", 0.55)]},
        },
        "corner": "corner_round",
        "roof": {"field": "roof_terrace", "edge": "parapet_rounded", "crown_civic": "dome_cap",
                 "pitched": {"run": "vault_roof_hump", "end": "vault_roof_hump", "share": 0.55}},
        "marks": [{"type": "fountain", "piece": "cistern_well"}, {"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 6}],
        "overlay": {"roof_items": [("lemon_pergola", 0.05)], "lantern": 0.4, "festoon": 0.2, "dish": 0.05, "cable": 0.05, "spans": []},
        "foliage": {"green": ["lemon", "olive", "fig", "almond"], "bank": ["oleander", "reeds"],
                    "plaza": ["olive"], "court": ["fig"], "lane_wall": ["wisteria", "bougainvillea", "caper_plant"],
                    "lane": ["grapevine_pergola"], "roof": ["grapevine_pergola", "basil_pots"],
                    "rates": {"lane": 0.06, "roof": 0.08, "lane_wall": 0.08}},
        "kit_requests": [
            ("vault_roof_hump", "the whitewashed barrel/cross vault hump over a rock-cut cell (cell roof)", "dome_cap at 8%"),
            ("wall_cave_door_k", "deep arched door with a lunette into a rock-cut vault (wall, ground)", "wall_arch_round_k"),
            ("rock_face_cut", "the raw rock face the cells are cut into (wall, rock material)", "wall_plain_k"),
            ("cistern_well", "the vicinato cistern well head (cell decor)", "none"),
            ("lemon_pergola", "a vine/lemon pergola on posts over a roof terrace (roof decor)", "grapevine_pergola foliage"),
        ],
    }
