"""Nouvelle-France winter towns (r3_nouvelle_france.md: Quebec's Lower and Upper Town, Montreal's plex quarters).

The mark: grey rubble-stone houses with dressed quoins under steep standing-seam tin roofs (silver, red, green) with
dormer rows and massive chimney gables, packed under the cliff; and on the grid, brick plex rows with pressed-metal
cornices, each wearing a twisting outdoor iron stair up its front; tall paired windows, oriels, coloured doors;
maples and elms; snow on every horizontal."""
from civ.family import FamilyCiv


class NouvelleFrance(FamilyCiv):
    id = "nouvelle_france"
    name = "Nouvelle-France winter town"
    arch_mouth = "wall_arch_round"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (5, 8), "jog": 0.06, "blind": 0.08, "break": 0.03, "light_wells": 0.0,
            "lot_cells": (2, 5), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (2, 3), "max_levels": 4, "civic_levels": 3, "sabat_from": 9, "jetty_from": 9,
            "work_share": 0.2, "civic_min_cells": 8,
            "epochs": {2: {"rise": 0.3, "setback": 0.0}, 3: {"rise": 0.2, "setback": 0.0}, 4: {"rise": 0.1, "setback": 0.1}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.5, "street_blades": 0.06,
            "shacks": 0.0, "shop_share": 0.5,
        },
        "palettes": [
            {"wall": "#a39d90", "trim": "#c4bdae", "frame": "#3f6a4a", "glass": "#2a3440", "screen": "#3f6a4a",
             "roof": "#b8bcc0", "metal": "#1d1d1d", "fabric": "#a8322a", "emissive": "#ffd8a0", "tile": "#c4bdae",
             "water": "#4a6a7a", "ground": "#8a8680", "plant": "#3f6a3a"},
            {"wall": "#efebe2", "trim": "#c4bdae", "frame": "#a8322a", "glass": "#2a3440", "screen": "#a8322a",
             "roof": "#a8322a", "metal": "#1d1d1d", "fabric": "#2a5a3a", "emissive": "#ffd8a0", "tile": "#c4bdae",
             "water": "#4a6a7a", "ground": "#8a8680", "plant": "#3f6a3a"},
            {"wall": "#8a3e2c", "trim": "#d8d0c0", "frame": "#2a5a3a", "glass": "#2a3440", "screen": "#2a5a3a",
             "roof": "#3f6a4a", "metal": "#2a5a3a", "fabric": "#25b5b0", "emissive": "#ffd8a0", "tile": "#d8d0c0",
             "water": "#4a6a7a", "ground": "#8a8680", "plant": "#3f6a3a"},
            {"wall": "#9a968e", "trim": "#d8d0c0", "frame": "#6a2a28", "glass": "#2a3440", "screen": "#6a2a28",
             "roof": "#2a2a2c", "metal": "#6a2a28", "fabric": "#f28a1e", "emissive": "#ffd8a0", "tile": "#d8d0c0",
             "water": "#4a6a7a", "ground": "#8a8680", "plant": "#3f6a3a"},
        ],
        "variants": (0.3, 0.2, 0.32, 0.18), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.7), ("wall_window_l", 0.3)],
            "ground": {"street": [("wall_window_casement_k", 0.45), ("wall_door", 0.3), ("wall_plain", 0.25)],
                       "lane": [("wall_window_m", 0.4), ("wall_door", 0.2), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_window_pair", 0.35), ("wall_window_m", 0.25), ("wall_balcony_iron", 0.18),
                                 ("wall_bay_box", 0.06), ("wall_plain", 0.16)],
                      "lane": [("wall_window_m", 0.4), ("wall_balcony_timber", 0.15), ("wall_plain", 0.45)],
                      "air": [("wall_window_s", 0.35), ("wall_plain", 0.65)]},
            "civic_ground": [("wall_arch_round", 0.5), ("wall_plain", 0.5)],
            "civic_upper": [("wall_window_l", 0.5), ("wall_plain", 0.5)],
        },
        "cull_slots": True,
        "corner": "corner_quoin",
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "edge_street": [("edge_cornice_pressed", 1.0)],
                 "crown_civic": "green_hip",
                 "pitched": {"run": "roof_tin_steep", "end": "roof_tin_steep_end", "variants": [0, 1], "civic": True}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "green_hip"], "storeys": 5},
                  {"type": "fountain"}],
        "overlay": {"face_items": [{"piece": "ov_snow_cap", "p": 0.5, "where": "upper"}], "street_stair": 0.3, "street_stair_piece": "stair_plex_outdoor", "lantern": 0.4, "cable": 0.12, "dish": 0.04, "chimney": 0.0},
        "foliage": {"plaza": ["maple", "elm"], "green": ["maple", "elm", "spruce", "lilac"], "bank": ["willow", "spruce"],
                    "lane": ["lilac"], "lane_wall": ["ivy"], "rates": {"plaza": 0.08, "lane": 0.03}},
        "kit_requests": [
            ("roof_tin_steep", "a 50-60 deg standing-seam tin roof with a dormer row (cell roof, span along the house; stand-in green_hip)", "green_hip"),
            ("edge_firewall_gable_k", "the Quebec firewall gable with a massive chimney stack and corbels (edge, roof top)", "none"),
            ("edge_cornice_pressed", "the plex pressed-metal cornice and parapet (edge)", "edge_parapet_plain_k"),
            ("stair_plex_outdoor", "Montreal's twisting outdoor iron stair from the pavement to the 2nd-storey door (cell, span [1, 1])", "stair_spiral"),
            ("ov_snow_cap", "snow lying on a roof edge / sill (edge overlay)", "none"),
            ("wall_window_casement_k", "small many-paned casement with interior shutters in rubble stone (wall)", "wall_window_m_k"),
        ],
    }
