"""River-ghat sacred city (r1_ganga_ghat.md: Varanasi, Haridwar, Pushkar).

The mark: a cliff of palaces and houses 3-8 storeys standing over broad stone steps down to the water, with
jharokhas, loggias and turrets; behind them a warren of 1-2 m galis bending every 12 m, colour-washed houses in
saffron, sky blue, pink and lime with iron balconies, shrine niches and painted ads; nagara temple spires above the
roofs; peepal trees with their platforms; marigolds, saffron pennants and lamps on the steps at night."""
from civ.family import FamilyCiv


class GangaGhat(FamilyCiv):
    id = "ganga_ghat"
    name = "River-ghat sacred city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (2, 5), "lane_spacing": 4, "lane_len": 12, "branch": 0.5, "loop": 0.35, "artery_share": 0.2,
            "block_cells": 9, "cut_turn": 4.5, "lot_cells": (3, 9), "courts": True, "court_min_lot": 10,
            "court_share": 0.08, "e1_levels": (3, 4), "max_levels": 7, "civic_levels": 3, "sabat_from": 1,
            "jetty_from": 2, "tower_levels": (6, 8), "work_share": 0.2, "civic_min_cells": 10, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.5, "setback": 0.15, "sabat": 0.2, "jetty": 0.15, "tower": 0.05},
                       3: {"rise": 0.4, "setback": 0.2, "sabat": 0.2, "jetty": 0.2, "tower": 0.06},
                       4: {"rise": 0.3, "setback": 0.25, "sabat": 0.15, "jetty": 0.2, "tower": 0.05}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.6, "street_blades": 0.2,
            "shacks": 0.05,
        },
        "variants": (0.25, 0.25, 0.25, 0.25), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.7), ("wall_shopfront_arcade", 0.3)],
            "ground": {"street": [("wall_shopfront", 0.35), ("wall_door", 0.25), ("wall_window_grille", 0.2),
                                  ("wall_plain", 0.2)],
                       "lane": [("wall_door", 0.25), ("wall_window_grille", 0.2), ("wall_plain", 0.55)],
                       "green": [("wall_arch_pointed", 0.4), ("wall_jharokha_bangla_k", 0.2), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_balcony_iron", 0.25), ("wall_window_m", 0.25), ("wall_jharokha_bangla_k", 0.08),
                                 ("wall_plain", 0.42)],
                      "lane": [("wall_balcony_iron", 0.15), ("wall_window_s", 0.25), ("wall_plain", 0.6)],
                      "green": [("wall_jharokha_bangla_k", 0.2), ("wall_arch_pointed", 0.25), ("wall_balcony_iron", 0.15),
                                ("wall_window_m", 0.2), ("wall_plain", 0.2)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap"},
        "marks": [{"type": "bank_steps", "piece": "ghat_steps_wide", "toward_water": True},
                  {"type": "civic_tower", "pieces": ["shikhara_spire_base", "shikhara_spire_shaft", "shikhara_spire_top"],
                   "storeys": 4},
                  {"type": "roof_towers", "piece": "chhatri", "share": 0.015, "storeys": (1, 1)},
                  {"type": "stalls", "share": 0.2}],
        "overlay": {"face_items": [{"piece": "ov_marigold_garland", "p": 0.15}, {"piece": "band_flood", "p": 0.35},
                               {"piece": "ov_wedding_curtain", "p": 0.03, "where": "upper", "epoch": 5}],
                    "spans": [("ov_wire_net", 0.08)], "festoon": 0.6, "lantern": 0.6, "cable": 0.35, "dish": 0.12, "laundry": 0.08, "lane_laundry": 0.08,
                    "awning": 0.35},
        "foliage": {"plaza": ["peepal", "banyan"], "green": ["peepal", "neem", "bel", "ashoka"], "bank": ["lotus", "peepal"],
                    "lane_wall": ["marigold"], "roof": ["tulsi_stand"], "rates": {"bank": 0.25, "roof": 0.05}},
        "kit_requests": [
            ("ghat_steps_wide", "broad stone ghat steps down into the water with a landing (stair, span [1, 2], water side)", "steps_up on banks"),
            ("shikhara_spire", "the nagara temple spire (curvilinear tower with amalaka and finial; base, shaft, top)", "minaret_base/shaft/top"),
            ("ghat_umbrella", "the cane umbrella over a priest's platform on the steps (cell decor)", "none"),
            ("chhatri", "the domed corner pavilion (roof crown)", "arcade_pier + dome_cap"),
            ("ov_marigold_garland", "marigold garlands over a door / along a balcony (face overlay)", "none"),
            ("band_flood", "the dark flood-mark band on the lower storeys (face overlay)", "none"),
        ],
    }
