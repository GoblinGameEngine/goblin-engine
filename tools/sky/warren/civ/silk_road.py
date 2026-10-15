"""Central Asian Silk Road city (r1_silk_road.md: Bukhara, Samarkand, Khiva, Kashgar).

The mark: low blank mud-brick mahallas of courtyard houses (carved doors the only thing on the street; aivan porches
on carved columns inside), lanes 2-3 m with balconies over them, domed bazaar crossings; and rising out of it, pairs
of monuments faced in turquoise and cobalt tile: tall portals, round tapering patterned minarets, turquoise domes;
the hauz pool under mulberries with its chaikhana and tapchan beds."""
from civ.family import FamilyCiv


class SilkRoad(FamilyCiv):
    id = "silk_road"
    name = "Central Asian Silk Road city"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 8), "lane_spacing": 5, "lane_len": 15, "branch": 0.4, "loop": 0.35, "artery_share": 0.3,
            "block_cells": 12, "cut_turn": 3.5, "lot_cells": (7, 16), "courts": True, "court_min_lot": 8,
            "court_share": 0.22, "e1_levels": (1, 2), "max_levels": 3, "civic_levels": 4, "sabat_from": 1,
            "jetty_from": 1, "work_share": 0.15, "civic_min_cells": 14, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.35, "setback": 0.35, "sabat": 0.2, "jetty": 0.1},
                       3: {"rise": 0.25, "setback": 0.4, "sabat": 0.2, "jetty": 0.12},
                       4: {"rise": 0.12, "setback": 0.45, "sabat": 0.15, "jetty": 0.1}},
            "plaza_cells": 7, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.35, "street_blades": 0.04,
            "shacks": 0.02,
        },
        "civic_court": True,
        "variants": (0.35, 0.3, 0.3, 0.05), "civic_variant": 3,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_arch_pointed",
            "shop": [("wall_shopfront_arcade", 0.7), ("wall_arch_pointed", 0.3)],
            "ground": {"street": [("wall_plain", 0.75), ("wall_door", 0.15), ("wall_window_s", 0.1)],
                       "lane": [("wall_plain", 0.88), ("wall_door", 0.06), ("wall_window_s", 0.06)],
                       "court": [("wall_arch_round", 0.35), ("wall_screen", 0.25), ("wall_window_m", 0.4)]},
            "upper": {"street": [("wall_balcony_timber", 0.18), ("wall_window_s", 0.22), ("wall_plain", 0.6)],
                      "lane": [("wall_balcony_timber", 0.15), ("wall_window_s", 0.15), ("wall_plain", 0.7)],
                      "court": [("wall_balcony_timber", 0.4), ("wall_screen", 0.2), ("wall_window_m", 0.4)]},
            "civic_ground": [("wall_arch_pointed", 0.45), ("wall_zellij_k", 0.35), ("wall_blind_arch", 0.2)],
            "civic_upper": [("wall_zellij_k", 0.45), ("wall_blind_arch", 0.35), ("wall_plain", 0.2)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_turquoise_ribbed"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_round_tapered_base", "minaret_round_tapered_shaft", "minaret_round_tapered_top"], "storeys": 10},
                  {"type": "door_face", "piece": "portal_pishtaq"}, {"type": "fountain", "piece": "tapchan"},
                  {"type": "stalls", "share": 0.15}],
        "overlay": {"festoon": 0.45, "lantern": 0.4, "dish": 0.12, "cable": 0.12, "awning": 0.3},
        "foliage": {"plaza": ["mulberry", "karagach_elm"], "green": ["mulberry", "poplar", "apricot", "karagach_elm"],
                    "bank": ["willow", "poplar"], "court": ["grapevine_pergola", "apricot", "rose_beds"],
                    "lane": ["grapevine_pergola"], "rates": {"court": 0.55, "plaza": 0.12, "lane": 0.04}},
        "kit_requests": [
            ("portal_pishtaq", "the monumental tiled portal 15-30 m (Registan): a tall pointed iwan in a tiled frame (wall, 3-5 storeys)", "wall_zellij_k + blind arches"),
            ("minaret_round_tapered", "round tapering brick minaret with tile bands and a lantern (base, shaft, top)", "minaret_base/shaft/top"),
            ("dome_turquoise_ribbed", "the ribbed turquoise tile dome on a drum (crown, tile slot)", "dome_cap"),
            ("aivan_column", "the carved wooden column of the aivan porch (corner/decor)", "corner_column"),
            ("tapchan", "the raised bed-platform of the chaikhana by the hauz (cell decor)", "none"),
            ("dome_bazaar_crossing", "the domed bazaar crossing (taq) over a lane junction (cell crown over a passage)", "none"),
        ],
    }
