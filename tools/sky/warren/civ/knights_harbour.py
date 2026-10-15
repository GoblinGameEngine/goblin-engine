"""Knights' harbour cities (r3_knights_harbour.md: Valletta, Mdina, Dubrovnik, Rhodes).

The mark: honey Globigerina limestone on a strict grid of continuous terraced frontages, stair-streets with low risers
down to the harbour, and on every upper storey the gallarija -- enclosed timber balconies painted green, red, blue
and ochre, stacked and wrapping the corners; arched shop fanlights, green shutters, corner statue niches; a polished
stone main street on the ridge; flat stone roofs (red tile hips in Dubrovnik); bastion gardens of oranges."""
from civ.family import FamilyCiv


class KnightsHarbour(FamilyCiv):
    id = "knights_harbour"
    name = "Knights' harbour city"
    arch_mouth = "wall_arch_round"
    kerb = "quay_edge_stone"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (6, 8), "jog": 0.02, "blind": 0.03, "break": 0.02, "light_wells": 0.03,
            "lot_cells": (4, 10), "courts": True, "court_min_lot": 10, "court_share": 0.08,
            "flats_per_level": False, "roof_walk": False,
            "e1_levels": (3, 4), "max_levels": 5, "civic_levels": 3, "sabat_from": 9, "jetty_from": 9,
            "work_share": 0.2, "civic_min_cells": 10, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.35, "setback": 0.05}, 3: {"rise": 0.25, "setback": 0.1}, 4: {"rise": 0.15, "setback": 0.3}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.6, "street_blades": 0.1,
            "shacks": 0.02,
        },
        "variants": (0.35, 0.3, 0.2, 0.15), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_arch_round", 0.4)],
            "ground": {"street": [("wall_arch_round", 0.3), ("wall_door", 0.25), ("wall_window_m", 0.25), ("wall_plain", 0.2)],
                       "lane": [("wall_door", 0.25), ("wall_window_m", 0.3), ("wall_plain", 0.45)]},
            "upper": {"street": [("wall_gallarija_k", 0.5), ("wall_window_m", 0.3), ("wall_plain", 0.2)],
                      "lane": [("wall_gallarija_k", 0.35), ("wall_window_m", 0.35), ("wall_plain", 0.3)],
                      "air": [("wall_window_m", 0.4), ("wall_plain", 0.6)]},
            "civic_ground": [("wall_arch_round", 0.5), ("wall_blind_arch", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_window_l", 0.4), ("wall_blind_arch", 0.3), ("wall_plain", 0.3)],
        },
        "cull_slots": True,
        "corner": "corner_quoin",
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tile_roman_low", "end": "roof_tile_roman_low_end", "share": 0.2}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "church_spire_copper"], "storeys": 4},
                  {"type": "fountain"}],
        "overlay": {"lantern": 0.45, "festoon": 0.3, "awning": 0.3, "dish": 0.08, "cable": 0.08, "laundry": 0.05},
        "foliage": {"plaza": ["aleppo_pine", "date_palm"], "green": ["orange", "aleppo_pine", "oleander", "date_palm"],
                    "bank": ["date_palm", "oleander"], "lane_wall": ["bougainvillea"], "roof": ["geranium_pot"],
                    "rates": {"plaza": 0.08}},
        "kit_requests": [
            ("wall_gallarija_k", "the gallarija: an enclosed painted timber balcony 1-1.4 m deep, glazed, stacked, wrapping corners (wall)", "wall_balcony_timber_k"),
            ("corner_statue_niche", "a saint in a niche at a street corner, lit at night (corner)", "corner_quoin_k"),
            ("stair_knight", "the knight's stair-street: low risers 0.1 m, deep treads, 3-5 m wide (stair, span [1, 2])", "steps"),
            ("bastion_wall_slope", "the sloped bastion wall at the island rim (wall, 2 storeys)", "none"),
        ],
    }
