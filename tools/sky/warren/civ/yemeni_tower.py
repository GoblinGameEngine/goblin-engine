"""Yemeni highland tower city (r1_yemeni_tower.md: Sana'a, Shibam, Thula).

The mark: free-standing family tower houses 5-9 storeys packed edge to edge, a dark basalt ground storey, brick
above, every opening framed in white gypsum and crowned by a glowing qamariya fanlight in vertical columns, white
crenellated roof edges, gypsum bands; lanes 2-4 m bending to sarhah squares; walled maqshama gardens between blocks;
domes only on the mosque.  At night: dark towers dotted with jewel-coloured semicircles."""
from civ.family import FamilyCiv


class YemeniTower(FamilyCiv):
    id = "yemeni_tower"
    name = "Yemeni highland tower city"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 9), "lane_spacing": 5, "lane_len": 16, "branch": 0.35, "loop": 0.45, "artery_share": 0.3,
            "block_cells": 10, "cut_turn": 3.0, "lot_cells": (4, 9), "courts": False,
            "e1_levels": (3, 4), "max_levels": 9, "civic_levels": 2, "tower_levels": (6, 9), "sabat_from": 3,
            "work_share": 0.15, "civic_min_cells": 10,
            "epochs": {2: {"rise": 0.65, "setback": 0.15, "sabat": 0.1, "tower": 0.35, "tower_levels": (5, 7)},
                       3: {"rise": 0.55, "setback": 0.2, "sabat": 0.1, "tower": 0.3, "tower_levels": (6, 8)},
                       4: {"rise": 0.4, "setback": 0.3, "sabat": 0.08, "tower": 0.2, "tower_levels": (7, 9)}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.3, "street_blades": 0.04,
            "shacks": 0.04, "shop_share": 0.3,
        },
        "palettes": [
            {"wall": "#8a5a3c", "trim": "#f2efe6", "frame": "#5a3a24", "glass": "#2a2e3a", "screen": "#6b4a30",
             "roof": "#7a5a40", "metal": "#3a3632", "fabric": "#a8322a", "emissive": "#ffb347", "tile": "#2bd96b",
             "water": "#3d6f7c", "ground": "#6b665f", "plant": "#4f7a3a"},
            {"wall": "#9c6a45", "trim": "#f2efe6", "frame": "#5a3a24", "glass": "#2a2e3a", "screen": "#6b4a30",
             "roof": "#7a5a40", "metal": "#3a3632", "fabric": "#2f6bff", "emissive": "#ff3b3b", "tile": "#2f6bff",
             "water": "#3d6f7c", "ground": "#6b665f", "plant": "#4f7a3a"},
            {"wall": "#a07850", "trim": "#ece6d6", "frame": "#5a3a24", "glass": "#2a2e3a", "screen": "#6b4a30",
             "roof": "#8a6a48", "metal": "#3a3632", "fabric": "#2bd96b", "emissive": "#2bd96b", "tile": "#ffb347",
             "water": "#3d6f7c", "ground": "#6b665f", "plant": "#4f7a3a"},
            {"wall": "#4a4743", "trim": "#f2efe6", "frame": "#3a2a1c", "glass": "#2a2e3a", "screen": "#5a3a24",
             "roof": "#5a5650", "metal": "#3a3632", "fabric": "#a8322a", "emissive": "#ffb347", "tile": "#2bd96b",
             "water": "#3d6f7c", "ground": "#4a4743", "plant": "#4f7a3a"},
        ],
        "variants": (0.0, 0.4, 0.35, 0.25), "ground_variant": 0, "civic_variant": 1,
        "thick": 1,
        "facade": {
            "door": "wall_door_carved_k", "door_civic": "wall_door_carved_k",
            "shop": [("wall_shopfront", 0.6), ("wall_shopfront_arcade", 0.4)],
            # the basalt ground storey: small grilled windows, carved doors; framed windows from the 1st storey up
            "ground": {"street": [("wall_window_grille_k", 0.45), ("wall_door_carved_k", 0.1), ("wall_plain", 0.45)],
                       "lane": [("wall_window_grille_k", 0.35), ("wall_door_carved_k", 0.06), ("wall_plain", 0.59)]},
            "upper": {"street": [("wall_gypsum_window_k", 0.4), ("wall_qamariya", 0.3), ("wall_screen", 0.1),
                                 ("wall_plain", 0.2)],
                      "lane": [("wall_gypsum_window_k", 0.35), ("wall_qamariya", 0.25), ("wall_screen", 0.05),
                               ("wall_plain", 0.35)],
                      "air": [("wall_qamariya", 0.3), ("wall_window_s", 0.2), ("wall_plain", 0.5)]},
        },
        "corner": "corner_column",          # (the white gypsum lines climbing the corners)
        "roof": {"field": "roof_terrace", "edge": "edge_parapet_crenel_white_k", "crown_civic": "dome_cap", "crown_band": True},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_brick_round_shaft", "minaret_brick_round_shaft", "minaret_brick_round_top"], "storeys": 8},
                  {"type": "stalls", "share": 0.12}],
        "overlay": {"face_items": [{"piece": "drain_spout", "p": 0.15, "where": "top", "dk": 1}], "band": {"piece": "band_brick_relief", "p": 0.6, "from": 1}, "dish": 0.3, "tank": 0.1, "laundry": 0.03, "cable": 0.15, "lantern": 0.3, "ac": 0.03},
        "foliage": {"green": ["fig", "pomegranate", "sidr_ziziphus", "qat_shrub", "grapevine_pergola",
                              "maqshama_vegetable_beds"],
                    "bank": ["date_palm", "date_palm", "pomegranate"], "plaza": ["sidr_ziziphus"],
                    "roof": ["basil_pots"], "rates": {"green": 0.5, "roof": 0.05}},
        "kit_requests": [
            ("wall_door_carved_k", "heavy carved wooden door 1.2 x 2.2 m in a white gypsum frame, basalt surround", "wall_door_k"),
            ("wall_window_grille_k", "small grilled window in a thick (0.6 m) basalt ground storey", "wall_window_s_k"),
            ("edge_parapet_crenel_white_k", "the stepped Sana'a merlon in white gypsum (trim slot)", "edge_parapet_rounded_k"),
            ("band_brick_relief", "brick relief band per storey (used: 45% of upper faces from the 2nd storey)", "-"),
            ("wall_gypsum_window_k", "gypsum-framed window with small qamariya (used)", "-"),
            ("minaret_brick_round", "Sana'a minaret: round brick shaft with relief bands, gallery and white top", "minaret_base/shaft/top"),
            ("drain_spout", "a 0.6 m timber roof spout (decor on a roof edge)", "none"),
            ("skybridge_timber", "a 1-cell enclosed bridge between towers at an upper storey (Shibam)", "sabat rooms"),
        ],
    }
