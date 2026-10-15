"""Creole colonial port cities (r3_creole_colonial.md: Havana, Cartagena, Willemstad, New Orleans, Guanajuato).

The mark: a Laws-of-the-Indies grid of contiguous thick-walled courtyard houses in candy pastels with white trim,
floor-to-ceiling windows with turned bars and shutters, timber and iron balconies, arcaded portales on the main
streets and round the plaza mayor (royal palms, flame trees, a fountain), patios with two-level galleries, flat
azoteas with parapets, a baroque bell tower; bougainvillea on every balcony."""
from civ.family import FamilyCiv


class CreoleColonial(FamilyCiv):
    id = "creole_colonial"
    name = "Creole colonial port city"
    arch_mouth = "wall_arch_round"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (6, 9), "jog": 0.03, "blind": 0.05, "break": 0.02, "light_wells": 0.0,
            "lot_cells": (8, 16), "courts": True, "court_min_lot": 8, "court_share": 0.2,
            "flats_per_level": False, "roof_walk": False,
            "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 3, "sabat_from": 9, "jetty_from": 9,
            "work_share": 0.2, "civic_min_cells": 12,
            "epochs": {2: {"rise": 0.25, "setback": 0.3, "sabat": 0.0},
                       3: {"rise": 0.2, "setback": 0.3, "sabat": 0.0},
                       4: {"rise": 0.08, "setback": 0.4, "sabat": 0.0}},
            "plaza_cells": 7, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.5, "street_blades": 0.05,
            "shacks": 0.03,
        },
        "civic_court": True,
        "palettes": [
            {"wall": "#f29aa8", "trim": "#fbf7ee", "frame": "#2e7a4a", "glass": "#2a3440", "screen": "#2e7a4a",
             "roof": "#b8603a", "metal": "#2a2a2a", "fabric": "#2a5aa8", "emissive": "#ffd890", "tile": "#c8202a",
             "water": "#3a8a9a", "ground": "#b8a890", "plant": "#3f7a3a"},
            {"wall": "#f6b03c", "trim": "#fbf7ee", "frame": "#2a5aa8", "glass": "#2a3440", "screen": "#2a5aa8",
             "roof": "#b8603a", "metal": "#2a2a2a", "fabric": "#c8202a", "emissive": "#ffd890", "tile": "#2050b0",
             "water": "#3a8a9a", "ground": "#b8a890", "plant": "#3f7a3a"},
            {"wall": "#3ac0c0", "trim": "#fbf7ee", "frame": "#5a3a28", "glass": "#2a3440", "screen": "#5a3a28",
             "roof": "#b8603a", "metal": "#2a2a2a", "fabric": "#f6b03c", "emissive": "#ffd890", "tile": "#e8a020",
             "water": "#3a8a9a", "ground": "#b8a890", "plant": "#3f7a3a"},
            {"wall": "#b8a0d8", "trim": "#fbf7ee", "frame": "#2e7a4a", "glass": "#2a3440", "screen": "#2e7a4a",
             "roof": "#b8603a", "metal": "#2a2a2a", "fabric": "#f29aa8", "emissive": "#ffd890", "tile": "#2a9a4a",
             "water": "#3a8a9a", "ground": "#b8a890", "plant": "#3f7a3a"},
        ],
        "variants": (0.28, 0.26, 0.24, 0.22), "civic_variant": 1,
        "thick": 1,
        "facade": {
            "door": "wall_door_carriage_k", "door_civic": "wall_door_carriage_k",
            "shop": [("wall_shopfront_arcade", 0.65), ("wall_arch_round", 0.35)],
            "ground": {"street": [("wall_arch_round", 0.35), ("wall_window_medio_punto_k", 0.45), ("wall_door", 0.2)],
                       "lane": [("wall_window_medio_punto_k", 0.55), ("wall_plain", 0.25), ("wall_door", 0.2)],
                       "court": [("wall_arch_round", 0.85), ("wall_plain", 0.15)]},
            "upper": {"street": [("wall_balcony_iron", 0.3), ("wall_balcony_covered_k", 0.12), ("wall_window_medio_punto_k", 0.4),
                                 ("wall_plain", 0.1)],
                      "lane": [("wall_window_medio_punto_k", 0.5), ("wall_balcony_iron", 0.15), ("wall_plain", 0.35)],
                      "court": [("wall_arch_round", 0.45), ("wall_balcony_timber", 0.25), ("wall_window_medio_punto_k", 0.3)],
                      "air": [("wall_window_medio_punto_k", 0.4), ("wall_plain", 0.6)]},
            "civic_ground": [("wall_arch_round", 0.5), ("wall_blind_arch", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_window_medio_punto_k", 0.4), ("wall_blind_arch", 0.3), ("wall_plain", 0.3)],
        },
        "corner": "corner_column",
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "edge_street": [("edge_parapet_urns_k", 1.0)], "crown_civic": "dome_cap", "crown_band": True,
                 "pitched": {"run": "roof_tile_red_low", "end": "roof_tile_red_low_end", "share": 0.2}},
        "marks": [{"type": "civic_tower", "pieces": ["bell_tower_baroque_base", "bell_tower_baroque_base", "bell_tower_baroque_belfry", "bell_tower_baroque_cupola"], "storeys": 4},
                  {"type": "fountain", "piece": "kiosco_gazebo"}, {"type": "stalls", "share": 0.06}],
        "overlay": {"lantern": 0.45, "festoon": 0.3, "cable": 0.25, "dish": 0.06, "laundry": 0.05, "ac": 0.08,
                    "lane_laundry": 0.05},
        "foliage": {"plaza": ["royal_palm", "royal_palm", "flamboyant", "ceiba"], "court": ["banana", "hibiscus", "royal_palm"],
                    "green": ["royal_palm", "flamboyant", "ficus"], "bank": ["royal_palm", "reeds"],
                    "lane_wall": ["bougainvillea"], "roof": ["fern_pot"],
                    "rates": {"plaza": 0.12, "lane_wall": 0.1, "court": 0.5}},
        "kit_requests": [
            ("wall_window_medio_punto_k", "floor-to-ceiling window with turned bars, louvred shutters and a stained-glass medio punto lunette (emissive at night)", "wall_window_l_k"),
            ("wall_balcony_covered_k", "Cartagena's long covered timber balcony on corbels with turned balusters and a small roof", "wall_balcony_timber_k"),
            ("wall_door_carriage_k", "the zaguan carriage door with a small inset door, stone surround", "wall_door_k"),
            ("bell_tower_baroque", "a baroque bell tower (base, belfry, cupola crown) for the cathedral", "minaret_base/shaft/top"),
            ("kiosco_gazebo", "the plaza bandstand gazebo (cell decor)", "fountain_riad"),
            ("edge_parapet_urns_k", "an azotea parapet with urns/balusters (edge)", "edge_parapet_plain_k"),
        ],
    }
