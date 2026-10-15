"""Tibetan Lhasa: the Barkhor and its whitewashed courtyard houses (r2_tibetan_lhasa.md).

The mark: battered whitewashed stone walls leaning inward, windows framed in black trapezoids (wider at the bottom)
with short pleated cloth valances, carved and painted timber lintels; courtyard blocks 3-4 storeys facing the kora
that circles the temple; flat earth roofs with parapets, prayer-flag poles at every corner and strings of flags across
the lanes; a maroon twig frieze under the parapets of the important buildings, gilded roof ornaments on the temple;
incense burners, a willow park (lingka) with a pond."""
from civ.family import FamilyCiv


class TibetanLhasa(FamilyCiv):
    id = "tibetan_lhasa"
    name = "Tibetan Lhasa"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (5, 10), "lane_spacing": 5, "lane_len": 16, "branch": 0.35, "loop": 0.45, "artery_share": 0.3,
            "block_cells": 12, "cut_turn": 3.0, "lot_cells": (8, 18), "courts": True, "court_min_lot": 8,
            "court_share": 0.2, "e1_levels": (2, 3), "max_levels": 5, "civic_levels": 4, "work_share": 0.15,
            "civic_min_cells": 14, "shop_share": 0.6,
            "epochs": {2: {"rise": 0.3, "setback": 0.25}, 3: {"rise": 0.2, "setback": 0.3}, 4: {"rise": 0.12, "setback": 0.35}},
            "plaza_cells": 7, "main_cells": 3, "garden_cells": (7, 6), "sign": 0.4, "street_blades": 0.05,
            "shacks": 0.02,
        },
        "civic_court": True,
        "variants": (0.45, 0.3, 0.1, 0.15), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.7), ("wall_shopfront_arcade", 0.3)],
            "ground": {"street": [("wall_shopfront", 0.3), ("wall_window_m", 0.2), ("wall_door", 0.2), ("wall_plain", 0.3)],
                       "lane": [("wall_window_s", 0.25), ("wall_door", 0.15), ("wall_plain", 0.6)],
                       "court": [("wall_window_m", 0.4), ("wall_door", 0.3), ("wall_plain", 0.3)]},
            "upper": {"street": [("wall_window_trapezoid_k", 0.45), ("wall_window_pair", 0.15), ("wall_plain", 0.4)],
                      "lane": [("wall_window_trapezoid_k", 0.3), ("wall_battered_k", 0.7)],
                      "court": [("wall_balcony_timber", 0.4), ("wall_window_m", 0.4), ("wall_plain", 0.2)]},
            "civic_ground": [("wall_plain", 0.6), ("wall_window_s", 0.4)],
            "civic_upper": [("wall_window_m", 0.4), ("wall_plain", 0.6)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "roof_gilded_temple"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_base", "roof_gilded_temple"], "storeys": 3},
                  {"type": "fountain", "piece": "incense_burner"}],
        "overlay": {"spans": [("ov_prayer_flags", 0.3)], "roof_items": [("stupa", 0.003), ("ov_prayer_flag_pole", 0.12)],
                    "face_items": [{"piece": "edge_pembe_frieze", "p": 0.25, "where": "top", "dk": 1}], "festoon": 0.5, "lantern": 0.4, "roof_items": [("antenna", 0.08)],
                    "dish": 0.06, "cable": 0.1},
        "foliage": {"plaza": ["willow", "white_poplar"], "green": ["willow", "white_poplar", "willow"],
                    "bank": ["willow"], "court": ["marigold_pots", "geranium_pots"], "roof": ["marigold_pots"],
                    "rates": {"green": 0.5, "court": 0.4}},
        "kit_requests": [
            ("wall_battered_k", "the battered (5-8 deg) whitewashed stone bay (wall)", "wall_plain_k"),
            ("wall_window_trapezoid_k", "the window in a black trapezoid surround with tiered painted lintels and a pleated valance (wall)", "wall_window_m_k"),
            ("edge_pembe_frieze", "the maroon twig (pembe) frieze under a parapet (edge band)", "crown_band"),
            ("ov_prayer_flag_pole", "the prayer-flag pole at a roof corner (corner decor)", "ov_antennas"),
            ("ov_prayer_flags", "prayer flag strings across lanes and roofs (along X)", "ov_festoon"),
            ("incense_burner", "the big whitewashed incense burner on the kora (cell decor)", "fountain_riad"),
            ("roof_gilded_temple", "the gilded temple roof with victory banners (crown)", "green_hip"),
        ],
    }
