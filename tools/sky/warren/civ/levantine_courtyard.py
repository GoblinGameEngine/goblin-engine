"""Levantine stone courtyard city (r1_levantine_courtyard.md: Damascus, Aleppo, Jerusalem's Old City).

The mark: blank stone lane walls on cul-de-sac clusters, timber jetties with shuttered lattice rows hanging over 2-3 m
lanes, rooms bridging them, ablaq striped portals; inside, a court with a liwan arch, a fountain and a bitter orange;
covered suqs; flat roofs and (Jerusalem) walkable stone domes; festoons and lit stalls at night."""
from civ.family import FamilyCiv


class LevantineCourtyard(FamilyCiv):
    id = "levantine_courtyard"
    name = "Levantine stone courtyard city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 8), "lane_spacing": 5, "lane_len": 14, "branch": 0.5, "loop": 0.25, "artery_share": 0.3,
            "block_cells": 11, "cut_turn": 4.0, "lot_cells": (7, 16), "courts": True, "court_min_lot": 8,
            "court_share": 0.22, "e1_levels": (2, 2), "max_levels": 3, "civic_levels": 2, "sabat_from": 1,
            "jetty_from": 1, "work_share": 0.15, "civic_min_cells": 12, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.35, "setback": 0.25, "sabat": 0.25, "jetty": 0.2},
                       3: {"rise": 0.25, "setback": 0.3, "sabat": 0.25, "jetty": 0.2},
                       4: {"rise": 0.12, "setback": 0.4, "sabat": 0.2, "jetty": 0.15}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.5, "street_blades": 0.06,
            "shacks": 0.02,
        },
        "civic_court": True,
        "variants": (0.35, 0.3, 0.05, 0.3), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_ablaq_portal_k",
            "shop": [("wall_shopfront_arcade", 0.7), ("wall_arch_pointed", 0.3)],
            "ground": {"street": [("wall_window_s", 0.25), ("wall_door", 0.15), ("wall_plain", 0.6)],
                       "lane": [("wall_window_s", 0.15), ("wall_plain", 0.85)],
                       "court": [("wall_liwan_k", 0.15), ("wall_arch_pointed", 0.4), ("wall_window_m", 0.25), ("wall_plain", 0.2)]},
            "upper": {"street": [("wall_jetty_t", 0.3), ("wall_screen", 0.15), ("wall_window_m", 0.2),
                                 ("wall_plain", 0.35)],
                      "lane": [("wall_jetty_t", 0.22), ("wall_screen", 0.15), ("wall_window_s", 0.13),
                               ("wall_plain", 0.5)],
                      "court": [("wall_window_m", 0.5), ("wall_qamariya", 0.2), ("wall_arch_pointed", 0.3)]},
            "civic_ground": [("wall_arch_pointed", 0.5), ("wall_blind_arch", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_blind_arch", 0.4), ("wall_plain", 0.6)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown": "dome_stone_low", "crown_share": 0.08,
                 "crown_civic": "dome_ribbed"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 7},
                  {"type": "fountain"}, {"type": "stalls", "share": 0.15}],
        "overlay": {"spans": [("ov_suq_canopy", 0.15)], "face_items": [{"piece": "ov_mastaba", "p": 0.4, "shops": True}],
                    "festoon": 0.5, "lantern": 0.5, "awning": 0.35, "cable": 0.2, "dish": 0.2, "laundry": 0.05,
                    "tank": 0.08},
        "foliage": {"court": ["bitter_orange", "lemon", "grapevine_pergola", "jasmine"],
                    "plaza": ["italian_cypress", "olive"], "green": ["olive", "pomegranate", "fig", "italian_cypress"],
                    "bank": ["italian_cypress", "reeds"], "lane_wall": ["jasmine"], "roof": ["herb_pots"],
                    "rates": {"court": 0.6}},
        "kit_requests": [
            ("wall_jetty_t (lighter)", "the timber jetty at <= 250 tris (622 now: the budget pass turns many into windows)", "wall_window_m_t when over budget"),
            ("wall_ablaq_portal_k", "black-and-white striped pointed portal with a muqarnas hood (wall, door)", "wall_arch_pointed_k"),
            ("wall_liwan_k", "the liwan: a tall pointed arch opening a whole storey and a half to the court (wall, 2 storeys)", "wall_arch_pointed_k"),
            ("dome_stone_low", "Jerusalem's low walkable stone roof dome (crown)", "dome_cap"),
            ("ov_suq_canopy", "a covered-suq vault/canopy across an artery (along X)", "ov_awning_cane"),
        ],
    }
