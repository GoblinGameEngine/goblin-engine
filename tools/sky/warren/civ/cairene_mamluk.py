"""Cairene Mamluk-Ottoman quarter (r1_cairene_mamluk.md: al-Muizz, Darb al-Ahmar, Gamaliya).

The mark: the qasaba spine of shops under arches with stone benches; gated haras of courtyard houses 3-5 storeys
stepping out in mashrabiya oriels storey by storey over 2-4 m lanes, rooms bridging the lanes; wikala courts; ablaq
striped portals; a forest of minarets and ribbed domes; roofs cluttered with pigeon cotes and shacks; festoons and
lane cables at every storey."""
from civ.family import FamilyCiv


class CaireneMamluk(FamilyCiv):
    id = "cairene_mamluk"
    name = "Cairene Mamluk quarter"
    arch_mouth = "wall_arch_pointed"
    covered_ceiling = "sabat_beams"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (3, 8), "lane_spacing": 5, "lane_len": 16, "branch": 0.45, "loop": 0.3, "artery_share": 0.35,
            "block_cells": 11, "cut_turn": 4.0, "lot_cells": (6, 16), "courts": True, "court_min_lot": 10,
            "court_share": 0.15, "e1_levels": (3, 3), "max_levels": 5, "civic_levels": 3, "sabat_from": 1,
            "jetty_from": 1, "work_share": 0.25, "civic_min_cells": 12,
            "epochs": {2: {"rise": 0.5, "setback": 0.1, "sabat": 0.15, "jetty": 0.25},
                       3: {"rise": 0.4, "setback": 0.15, "sabat": 0.15, "jetty": 0.3},
                       4: {"rise": 0.25, "setback": 0.2, "sabat": 0.12, "jetty": 0.3}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (5, 4), "sign": 0.6, "street_blades": 0.15,
            "shacks": 0.12,
        },
        "civic_court": True,
        "variants": (0.3, 0.3, 0.2, 0.2), "civic_variant": 3,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_ablaq_portal_k",
            "shop": [("wall_shopfront_arcade", 0.75), ("wall_arch_pointed", 0.25)],
            "ground": {"street": [("wall_shopfront_arcade", 0.3), ("wall_window_s", 0.25), ("wall_door", 0.15),
                                  ("wall_plain", 0.3)],
                       "lane": [("wall_window_s", 0.25), ("wall_door", 0.1), ("wall_plain", 0.65)],
                       "court": [("wall_arch_pointed", 0.6), ("wall_plain", 0.4)]},
            "upper": {"street": [("wall_mashrabiya_box_k", 0.22), ("wall_screen", 0.1), ("wall_roshan_k", 0.15), ("wall_window_m", 0.18),
                                 ("wall_plain", 0.35)],
                      "lane": [("wall_screen", 0.3), ("wall_roshan_k", 0.08), ("wall_window_s", 0.17),
                               ("wall_plain", 0.45)],
                      "court": [("wall_screen", 0.35), ("wall_arch_pointed", 0.2), ("wall_window_m", 0.45)]},
            "civic_ground": [("wall_blind_arch", 0.5), ("wall_arch_pointed", 0.3), ("wall_plain", 0.2)],
            "civic_upper": [("wall_window_s", 0.3), ("wall_blind_arch", 0.3), ("wall_plain", 0.4)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_ribbed"},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_mamluk_base", "minaret_mamluk_shaft", "minaret_mamluk_top"], "storeys": 7},
                  {"type": "stalls", "share": 0.15}],
        "overlay": {"roof_items": [("malqaf_scoop", 0.04), ("pigeon_cote", 0.015)],
                    "face_items": [{"piece": "ov_mastaba", "p": 0.5, "shops": True}],
                    "spans": [("ov_suq_canopy", 0.1)], "cable": 0.45, "festoon": 0.5, "lantern": 0.45, "dish": 0.25, "laundry": 0.08, "tank": 0.05,
                    "ac": 0.08, "lane_laundry": 0.08},
        "foliage": {"plaza": ["sycamore_fig", "neem"], "green": ["sycamore_fig", "date_palm", "mango", "neem"],
                    "bank": ["date_palm", "reeds"], "court": ["henna", "jasmine", "date_palm"], "roof": ["herb_pots"],
                    "rates": {"court": 0.4}},
        "kit_requests": [
            ("wall_mashrabiya_box_k", "the turned-bead mashrabiya oriel stepping 0.25 m out per storey (wall)", "wall_screen_k"),
            ("wall_ablaq_portal_k", "striped ablaq pointed portal with a muqarnas hood (wall, door)", "wall_arch_pointed_k"),
            ("minaret_mamluk", "Mamluk minaret: square base, octagonal shaft, balconies, bulb top (3 parts)", "minaret_base/shaft/top"),
            ("dome_ribbed", "ribbed carved stone dome on a drum (crown)", "dome_cap"),
            ("malqaf_scoop", "the roof wind scoop (roof decor)", "minaret_base stub"),
            ("pigeon_cote", "the mud pigeon tower on a roof (roof decor)", "none"),
            ("ov_mastaba", "the stone bench before a shop (face overlay, ground)", "none"),
        ],
    }
