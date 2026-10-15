"""Ottoman timber towns (r3_ottoman_timber.md: Safranbolu, Berat, Plovdiv, Ohrid, Gjirokaster's lower town).

The mark: a rubble stone ground storey, timber-framed upper storeys oversailing the lane on angled brackets, each
storey wider than the one below ('upside-down wedding cake'), with three-sided cumba oriels and ranks of 4-8 tall
sash windows wrapping the corners; ochre, oxblood, blue and sage plaster or silvered clapboard; low tile hips with
deep eaves; the carsi bazaar, the plane-tree square with its fountain, walled gardens."""
from civ.family import FamilyCiv


class OttomanTimber(FamilyCiv):
    id = "ottoman_timber"
    name = "Ottoman timber town"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (4, 8), "lane_spacing": 5, "lane_len": 15, "branch": 0.4, "loop": 0.35, "artery_share": 0.25,
            "block_cells": 11, "cut_turn": 3.5, "lot_cells": (4, 10), "courts": True, "court_min_lot": 9,
            "court_share": 0.15, "e1_levels": (2, 3), "max_levels": 4, "civic_levels": 2, "sabat_from": 1,
            "jetty_from": 1, "work_share": 0.15, "civic_min_cells": 10, "shop_share": 0.5,
            "epochs": {2: {"rise": 0.35, "setback": 0.1, "jetty": 0.3, "sabat": 0.06},
                       3: {"rise": 0.25, "setback": 0.1, "jetty": 0.35, "sabat": 0.06},
                       4: {"rise": 0.15, "setback": 0.15, "jetty": 0.3, "sabat": 0.04}},
            "plaza_cells": 5, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.45, "street_blades": 0.05,
            "shacks": 0.02,
        },
        "variants": (0.28, 0.26, 0.24, 0.22), "civic_variant": 3, "ground_variant": None,
        "thick": 0,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_window_grille", 0.25), ("wall_door", 0.2), ("wall_plain", 0.55)],
                       "lane": [("wall_window_grille", 0.2), ("wall_door", 0.12), ("wall_plain", 0.68)]},
            "upper": {"street": [("wall_jetty_t", 0.2), ("wall_cumba_t", 0.12), ("wall_kafes_t", 0.3), ("wall_window_m", 0.18),
                                 ("wall_himis_t", 0.2)],
                      "lane": [("wall_jetty_t", 0.18), ("wall_cumba_t", 0.08), ("wall_kafes_t", 0.25), ("wall_window_m", 0.19),
                               ("wall_himis_t", 0.3)],
                      "court": [("wall_window_pair", 0.5), ("wall_balcony_timber", 0.3), ("wall_plain", 0.2)]},
            "civic_ground": [("wall_arch_round", 0.5), ("wall_plain", 0.5)],
            "civic_upper": [("wall_window_s", 0.4), ("wall_plain", 0.6)],
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "eave_soffit_deep", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tile_red_low", "end": "roof_tile_red_low_end", "share": 0.95}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "minaret_top"], "storeys": 6},
                  {"type": "fountain"}, {"type": "stalls", "share": 0.12}],
        "overlay": {"face_items": [{"piece": "cesme_fountain", "p": 0.02}], "lantern": 0.4, "festoon": 0.25, "awning": 0.3, "cable": 0.15, "dish": 0.06, "laundry": 0.04},
        "foliage": {"plaza": ["oriental_plane", "linden"], "green": ["walnut", "mulberry", "linden", "oriental_plane"],
                    "bank": ["willow"], "court": ["grapevine_pergola", "rose_beds", "mulberry"],
                    "lane_wall": ["rose_climber"], "rates": {"plaza": 0.1, "court": 0.5}},
        "kit_requests": [
            ("wall_jetty_t (lighter)", "the jettied storey at <= 250 tris (622: the budget pass turns most into windows)", "wall_window_m_t when over budget"),
            ("wall_cumba_t", "the three-sided cumba oriel on brackets (wall)", "wall_jetty_t"),
            ("wall_kafes_t", "sash windows behind kafes lattice (wall)", "wall_window_pair_t"),
            ("wall_himis_t", "timber-frame bay with plaster infill (himis) or clapboard (wall)", "wall_plain_t"),
            ("eave_soffit_deep", "the 1.0-1.5 m eave with a boarded soffit under a low hip (edge)", "edge_eave_tin"),
            ("cesme_fountain", "the stone wall fountain with a trough (face overlay)", "wall_fountain_k"),
        ],
    }
