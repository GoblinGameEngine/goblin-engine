"""Newar city of the Kathmandu valley (r1_newar.md: Bhaktapur, Patan, Kathmandu's Asan).

The mark: red brick rows 3-5 storeys ringing bahal courts, entered through low passages; shop shutters on a plinth
below, then carved black timber windows widening storey by storey -- the latticed tikijhya, the three-panel sanjhya
under its torana, a lattice bay at the top; clay-tile hip roofs on carved struts with a deep eave; Durbar squares of
pagoda temples in tiers with gilded finials, stone shikharas, sunken hiti water spouts, the pokhari pond; prayer flags,
drying chillies, moss and ferns on the roofs."""
from civ.family import FamilyCiv


class Newar(FamilyCiv):
    id = "newar"
    name = "Newar city"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (5, 10), "lane_spacing": 5, "lane_len": 16, "branch": 0.35, "loop": 0.4, "artery_share": 0.3,
            "block_cells": 12, "cut_turn": 3.0, "lot_cells": (3, 7), "courts": True, "court_min_lot": 6,
            "court_share": 0.2, "e1_levels": (3, 4), "max_levels": 5, "civic_levels": 3, "sabat_from": 1,
            "work_share": 0.2, "civic_min_cells": 8, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.35, "setback": 0.05, "sabat": 0.1},
                       3: {"rise": 0.25, "setback": 0.05, "sabat": 0.1},
                       4: {"rise": 0.2, "setback": 0.1, "sabat": 0.08}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.55, "street_blades": 0.15,
            "shacks": 0.04,
        },
        "variants": (0.35, 0.3, 0.1, 0.25), "civic_variant": 1,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.7), ("wall_shopfront_arcade", 0.3)],
            "ground": {"street": [("wall_shopfront", 0.45), ("wall_door", 0.2), ("wall_window_s", 0.15),
                                  ("wall_plain", 0.2)],
                       "lane": [("wall_door", 0.2), ("wall_window_s", 0.25), ("wall_plain", 0.55)],
                       "court": [("wall_door", 0.3), ("wall_newar_window_k", 0.3), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_newar_window_k", 0.45), ("wall_newar_sanjhya_k", 0.12), ("wall_window_m", 0.13),
                                 ("wall_plain", 0.3)],
                      "lane": [("wall_newar_window_k", 0.35), ("wall_window_s", 0.2), ("wall_plain", 0.45)],
                      "court": [("wall_newar_window_k", 0.5), ("wall_plain", 0.5)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_eave_pagoda", "crown_civic": "roof_pagoda",
                 "pitched": {"run": "roof_tile_hip_struts", "end": "roof_tile_hip_struts", "share": 0.9}},
        "pave": {"pave_lane": "wall_brick_herringbone", "pave_plaza": "wall_brick_herringbone"},
        "marks": [{"type": "stalls", "share": 0.12}, {"type": "fountain", "piece": "pagoda_temple_tiers"}],
        "overlay": {"spans": [("ov_prayer_flags", 0.15)], "roof_items": [("stupa", 0.004)],
                    "face_items": [{"piece": "ov_marigold_garland", "p": 0.1}], "festoon": 0.5, "lantern": 0.4, "cable": 0.4, "dish": 0.06, "tank": 0.08, "lane_laundry": 0.06},
        "foliage": {"plaza": ["peepal", "banyan"], "green": ["peepal", "bamboo", "rhododendron", "jacaranda", "mandarin"],
                    "bank": ["bamboo", "banana"], "court": ["marigold_pots", "mandarin"], "lane_wall": ["roof_moss_ferns"],
                    "roof": ["drying_chilli_corn"], "rates": {"court": 0.4}},
        "kit_requests": [
            ("pagoda_temple_tiers", "a 3-5 tier pagoda temple on a stepped plinth (the roof_pagoda over a multi-storey base)", "roof_pagoda on the civic lot"),
            ("hiti_sunken", "the sunken stone water spout court (ground, below deck)", "none"),
            ("stupa", "a whitewashed stupa with painted eyes (cell decor)", "none"),
            ("roof_tile_hip_struts", "clay-tile hip roof on carved struts over a row house (cell roof)", "green_hip + edge_eave_pagoda"),
            ("wall_brick_herringbone", "the herringbone brick paving (ground)", "pave_lane"),
            ("ov_prayer_flags", "prayer flag strings across lanes and squares (along X)", "ov_festoon"),
        ],
    }
