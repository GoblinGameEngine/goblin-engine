"""Red Sea coral-stone port (r1_hejazi_roshan.md: Jeddah al-Balad, Suakin, Mocha).

The mark: tall pale coral-stone tower houses 4-7 storeys whose street faces are 40-70% covered by stacked painted teak
roshans (oriels) running up 2-6 storeys in columns, mangour lattice parapets on the roofs, a souq spine and barha
squares under neem trees; LED-lit roshan lattices at night."""
from civ.family import FamilyCiv


class HejaziRoshan(FamilyCiv):
    id = "hejazi_roshan"
    name = "Red Sea coral-stone port"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (6, 12), "lane_spacing": 6, "lane_len": 20, "branch": 0.35, "loop": 0.4, "artery_share": 0.3,
            "block_cells": 11, "cut_turn": 3.0, "lot_cells": (4, 9), "courts": False,
            "e1_levels": (3, 4), "max_levels": 7, "civic_levels": 2, "tower_levels": (5, 7), "sabat_from": 2,
            "work_share": 0.2, "civic_min_cells": 8, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.55, "setback": 0.1, "sabat": 0.05, "tower": 0.25, "tower_levels": (4, 6)},
                       3: {"rise": 0.45, "setback": 0.15, "sabat": 0.05, "tower": 0.25, "tower_levels": (5, 7)},
                       4: {"rise": 0.3, "setback": 0.2, "sabat": 0.04, "tower": 0.15, "tower_levels": (6, 7)}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.5, "street_blades": 0.1,
            "shacks": 0.06,
        },
        "variants": (0.35, 0.3, 0.15, 0.2), "civic_variant": 0,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_window_s", 0.35), ("wall_door", 0.15), ("wall_plain", 0.5)],
                       "lane": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
            "upper": {"street": [("wall_roshan_k", 0.42), ("wall_window_m", 0.2), ("wall_screen", 0.08),
                                 ("wall_coral_bands_k", 0.3)],
                      "lane": [("wall_roshan_k", 0.3), ("wall_window_s", 0.25), ("wall_plain", 0.45)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "edge_street": [("edge_mangour_k", 1.0)],
                 "crown_civic": "dome_cap"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 7},
                  {"type": "stalls", "share": 0.12}],
        "overlay": {"face_items": [{"piece": "roshan_crest", "p": 0.25, "where": "top", "dk": 1}], "cable": 0.3, "dish": 0.2, "tank": 0.1, "lantern": 0.45, "festoon": 0.3, "ac": 0.1},
        "foliage": {"plaza": ["neem", "doum_palm"], "green": ["neem", "date_palm", "doum_palm"], "bank": ["date_palm"],
                    "lane_wall": ["bougainvillea"], "roof": ["herb_pots"], "rates": {"plaza": 0.1}},
        "kit_requests": [
            ("wall_roshan_k (lighter)", "the roshan at <= 250 tris: at 616 the budget pass turns most roshan columns back into windows", "wall_window_m_k when over budget"),
            ("edge_mangour_k", "the 1.8 m mangour lattice roof parapet of Jeddah (edge)", "edge_parapet_jali_k (one per house)"),
            ("roshan_crest", "the carved wooden crest crowning a roshan column (face overlay)", "none"),
            ("wall_coral_bands_k", "coral-stone bay with the timber tie-beam bands every 1 m (wall)", "wall_plain_k"),
        ],
    }
