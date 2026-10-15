"""Lusitanian hill towns (r3_lusitanian_hill.md: Lisbon's Alfama and Mouraria, Porto's Ribeira).

The mark: tight terraces of tall narrow houses 3-5 storeys stepping a storey down every plot or two along a steep
Moorish maze of becos and escadinhas; facades fully clad in blue, green and ochre azulejos or washed yellow and rose,
tall windows with iron cage balconies, granite frames, red tile roofs with attic dormers; miradouros, largo fountains,
calcada mosaics, the tram on its switchback; jacarandas and laundry."""
from civ.family import FamilyCiv


class LusitanianHill(FamilyCiv):
    id = "lusitanian_hill"
    name = "Lusitanian hill town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 6), "lane_spacing": 4, "lane_len": 14, "branch": 0.45, "loop": 0.35, "artery_share": 0.25,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (2, 5), "courts": False,
            "e1_levels": (3, 4), "max_levels": 5, "civic_levels": 3, "sabat_from": 2, "work_share": 0.15,
            "civic_min_cells": 8, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.35, "setback": 0.05, "sabat": 0.05},
                       3: {"rise": 0.25, "setback": 0.05, "sabat": 0.05},
                       4: {"rise": 0.15, "setback": 0.1, "sabat": 0.04}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.6, "street_blades": 0.12,
            "shacks": 0.04,
        },
        "variants": (0.28, 0.26, 0.26, 0.2), "civic_variant": 3,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.5), ("wall_arch_round", 0.5)],
            "ground": {"street": [("wall_arch_round", 0.25), ("wall_door", 0.3), ("wall_window_l", 0.25), ("wall_plain", 0.2)],
                       "lane": [("wall_door", 0.3), ("wall_window_m", 0.3), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_balcony_iron", 0.55), ("wall_window_l", 0.3), ("wall_plain", 0.15)],
                      "lane": [("wall_balcony_iron", 0.4), ("wall_window_l", 0.3), ("wall_plain", 0.3)],
                      "air": [("wall_window_m", 0.5), ("wall_plain", 0.5)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain",
                 "pitched": {"run": "roof_tile_roman_low", "end": "roof_tile_roman_low_end", "share": 0.85, "civic": True}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "dome_cap"], "storeys": 5},
                  {"type": "fountain"}],
        "overlay": {"lane_laundry": 0.3, "laundry": 0.06, "lantern": 0.45, "festoon": 0.35, "cable": 0.3,
                    "wall_pots": 0.06, "dish": 0.06},
        "foliage": {"plaza": ["jacaranda", "jacaranda"], "green": ["jacaranda", "lemon", "orange", "olive"],
                    "bank": ["reeds"], "lane_wall": ["bougainvillea", "geranium_tins"], "roof": ["basil_pots"],
                    "rates": {"plaza": 0.12, "lane_wall": 0.08}},
        "kit_requests": [
            ("wall_azulejo_k", "a facade bay fully clad in patterned azulejo tiles (tile slot), tall window with an iron cage balcony (wall)", "wall_balcony_iron_k on the tile-coloured variants"),
            ("wall_granite_window_k", "a tall window in a granite frame (wall)", "wall_window_l_k"),
            ("roof_dormer_attic", "the aguas-furtadas attic dormer on a tile roof (roof decor)", "none"),
            ("pave_calcada", "calcada portuguesa black-and-white mosaic paving (ground)", "pave_plaza"),
            ("tram_rail", "tram rails in the street with a tram (decor along X)", "none"),
            ("miradouro_kiosk", "a miradouro kiosk with a pergola (cell decor)", "none"),
        ],
    }
