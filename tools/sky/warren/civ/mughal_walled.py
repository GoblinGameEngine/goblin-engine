"""North Indian Mughal walled city (r1_mughal_walled.md: Shahjahanabad/Old Delhi, Lahore's walled city, Old Dhaka).

The mark: a canal bazaar axis and chowks, gated mohallas of havelis and katras on 1.5-3 m galis; shop rows below;
above, jharokha bays and chhajja eaves on every floor, jali screens, cusped arches and spiked sandstone doors; flat
roofs with jali parapets, chhatri corner pavilions, kites, tanks and pigeon lofts; the Jama Masjid's bulbous domes and
minarets on its plinth court; the wire net over every gali, lit with permanent festival strings."""
from civ.family import FamilyCiv


class MughalWalled(FamilyCiv):
    id = "mughal_walled"
    name = "Mughal walled city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 7), "lane_spacing": 4, "lane_len": 14, "branch": 0.5, "loop": 0.3, "artery_share": 0.35,
            "block_cells": 10, "cut_turn": 4.0, "lot_cells": (5, 14), "courts": True, "court_min_lot": 10,
            "court_share": 0.15, "e1_levels": (2, 3), "max_levels": 5, "civic_levels": 3, "sabat_from": 1,
            "jetty_from": 1, "work_share": 0.25, "civic_min_cells": 14,
            "epochs": {2: {"rise": 0.5, "setback": 0.15, "sabat": 0.15, "jetty": 0.15},
                       3: {"rise": 0.45, "setback": 0.15, "sabat": 0.15, "jetty": 0.2},
                       4: {"rise": 0.3, "setback": 0.2, "sabat": 0.12, "jetty": 0.2}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.9, "street_blades": 0.35,
            "shacks": 0.08,
        },
        "civic_court": True,
        "variants": (0.3, 0.25, 0.25, 0.2), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_arch_pointed",
            "shop": [("wall_shopfront", 0.7), ("wall_shopfront_arcade", 0.3)],
            "ground": {"street": [("wall_shopfront", 0.45), ("wall_arch_pointed", 0.15), ("wall_door", 0.2),
                                  ("wall_plain", 0.2)],
                       "lane": [("wall_door", 0.2), ("wall_window_grille", 0.25), ("wall_shopfront", 0.15),
                                ("wall_plain", 0.4)],
                       "court": [("wall_cusped_arch_k", 0.6), ("wall_window_m", 0.4)]},
            "upper": {"street": [("wall_jharokha_bangla_k", 0.18), ("wall_jali_carved_k", 0.15), ("wall_balcony_iron", 0.12),
                                 ("wall_window_m", 0.25), ("wall_plain", 0.3)],
                      "lane": [("wall_jharokha_bangla_k", 0.1), ("wall_jali_carved_k", 0.12), ("wall_window_s", 0.25),
                               ("wall_plain", 0.53)],
                      "court": [("wall_arch_pointed", 0.4), ("wall_jali_carved_k", 0.25), ("wall_window_m", 0.35)]},
            "civic_ground": [("wall_arch_pointed", 0.6), ("wall_plain", 0.4)],
            "civic_upper": [("wall_arch_pointed", 0.4), ("wall_jali_carved_k", 0.3), ("wall_plain", 0.3)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "edge_street": [("edge_parapet_jali_k", 1.0)],
                 "crown_civic": "dome_bulbous_marble"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 9},
                  {"type": "roof_towers", "piece": "chhatri", "share": 0.012, "storeys": (1, 1)},
                  {"type": "stalls", "share": 0.2}],
        "overlay": {"face_items": [{"piece": "edge_chhajja", "p": 0.45, "where": "upper", "dk": 1},
                               {"piece": "ov_wedding_curtain", "p": 0.05, "where": "upper", "epoch": 5}],
                    "spans": [("ov_wire_net", 0.3)], "cable": 0.7, "festoon": 0.6, "lantern": 0.45, "tank": 0.2, "dish": 0.15, "laundry": 0.1,
                    "lane_laundry": 0.08, "ac": 0.12},
        "foliage": {"plaza": ["peepal", "neem"], "green": ["mango", "neem", "ashoka", "italian_cypress", "gulmohar"],
                    "bank": ["coconut_palm", "banana"], "court": ["tulsi_pots", "banana"], "roof": ["marigold_pots"],
                    "rates": {"court": 0.4, "roof": 0.05}},
        "kit_requests": [
            ("wall_jharokha_bangla_k", "the jharokha with a curved bangla roof on carved brackets (wall)", "wall_bay_box_k"),
            ("edge_chhajja", "the deep stone chhajja eave over every storey (edge overlay at the storey top)", "none"),
            ("chhatri", "the domed corner pavilion on four columns (roof crown)", "arcade_pier + dome_cap"),
            ("wall_cusped_arch_k", "the cusped (multifoil) arch bay (wall)", "wall_arch_pointed_k"),
            ("dome_bulbous_marble", "the bulbous white marble dome with finial (crown)", "dome_cap"),
            ("ov_wire_net", "the overhead tangle of wires over a gali at storey 2-3 (along X)", "ov_cables"),
        ],
    }
