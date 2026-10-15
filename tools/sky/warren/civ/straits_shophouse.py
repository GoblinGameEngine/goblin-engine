"""Straits shophouses (r2_straits_shophouse.md: Penang's George Town, Malacca, Singapore's Chinatown).

The mark: long arcaded terraces of 2-3 storey shophouses with a continuous covered five-foot way, pastel stucco over
glazed Peranakan tile dados, pairs and triplets of full-height timber casements with louvres on every upper bay,
pintu pagar half-doors, pitched clay tile roofs with gable firewalls between units; Chinese temples, clan houses and
mosques side by side; rain trees over the hawker square."""
from civ.family import FamilyCiv


class StraitsShophouse(FamilyCiv):
    id = "straits_shophouse"
    name = "Straits shophouses"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (6, 10), "jog": 0.02, "blind": 0.05, "break": 0.02, "light_wells": 0.04,
            "lot_cells": (3, 7), "courts": False, "flats_per_level": False, "roof_walk": False,
            "e1_levels": (2, 3), "max_levels": 4, "civic_levels": 2, "sabat_from": 9, "jetty_from": 9,
            "work_share": 0.25, "civic_min_cells": 8, "shop_share": 0.95,
            "epochs": {2: {"rise": 0.25, "setback": 0.0}, 3: {"rise": 0.15, "setback": 0.05}, 4: {"rise": 0.08, "setback": 0.1}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.85, "street_blades": 0.15,
            "shacks": 0.02,
        },
        "variants": (0.25, 0.25, 0.25, 0.25), "civic_variant": 3,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.85), ("wall_arch_round", 0.15)],
            "ground": {"street": [("wall_shopfront_arcade", 0.6), ("wall_arch_round", 0.3), ("wall_door", 0.1)],
                       "lane": [("wall_door", 0.3), ("wall_window_m", 0.3), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_window_pair", 0.7), ("wall_window_l", 0.2), ("wall_plain", 0.1)],
                      "lane": [("wall_window_pair", 0.4), ("wall_window_m", 0.25), ("wall_plain", 0.35)]},
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": None, "crown_civic": "roof_tile_flying_eave",
                 "pitched": {"run": "roof_tile_red_low", "end": "roof_tile_red_low_end", "share": 0.9}},
        "marks": [{"type": "stalls", "share": 0.3}, {"type": "fountain"}],
        "overlay": {"lantern": 0.6, "festoon": 0.45, "cable": 0.2, "ac": 0.12, "dish": 0.05, "sign_column": 0.08,
                    "wall_pots": 0.06},
        "foliage": {"plaza": ["rain_tree", "rain_tree"], "green": ["rain_tree", "frangipani", "coconut_palm", "areca_palm"],
                    "bank": ["coconut_palm"], "lane_wall": ["potted_plants"], "rates": {"plaza": 0.12, "lane_wall": 0.1}},
        "kit_requests": [
            ("wall_five_foot_way_t", "the shophouse ground bay with the covered five-foot way (column at the street edge, arcade behind, pintu pagar shopfront) (wall)", "wall_shopfront_b_t"),
            ("wall_casement_louvre_t", "a pair/triplet of full-height timber casements with louvres, stucco frame (wall)", "wall_window_pair_t"),
            ("band_peranakan_tile", "the glazed Peranakan tile dado (face overlay, tile slot)", "none"),
            ("edge_firewall_gable", "the stepped gable firewall between units (edge on the roof)", "none"),
            ("temple_chinese_roof", "the Chinese temple roof with swallowtail ridges and porcelain dragons (crown)", "roof_tile_flying_eave"),
        ],
    }
