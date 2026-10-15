"""Scots lands and closes (r3_scots_lands.md: Edinburgh's Old Town, the Royal Mile).

The mark: a broad ridge spine street of setts lined by continuous 6-12 storey 'lands' of soot-dark harled rubble and
sandstone, and every 10-20 m a close dropping away through an arched pend into a slot 1-2.5 m wide between tall
narrow ranges; small regular sash windows in rows; steep slate roofs with crowstepped gables, many-pot chimney stacks
and conical turret stairs; dark painted shopfronts with signboards; the crown-spired cathedral and the mercat cross."""
from civ.family import FamilyCiv


class ScotsLands(FamilyCiv):
    id = "scots_lands"
    name = "Scots lands and closes"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (3, 6), "jog": 0.08, "blind": 0.35, "break": 0.03, "light_wells": 0.0,
            "lot_cells": (3, 8), "courts": False, "flats_per_level": True, "roof_walk": False,
            "e1_levels": (5, 6), "max_levels": 12, "civic_levels": 4, "tower_levels": (8, 12),
            "sabat_from": 1, "jetty_from": 9, "work_share": 0.2, "civic_min_cells": 10, "shop_share": 0.8,
            "epochs": {2: {"rise": 0.45, "setback": 0.0, "sabat": 0.15, "tower": 0.15, "tower_levels": (7, 9)},
                       3: {"rise": 0.4, "setback": 0.0, "sabat": 0.2, "tower": 0.2, "tower_levels": (8, 11)},
                       4: {"rise": 0.25, "setback": 0.05, "sabat": 0.15, "tower": 0.15, "tower_levels": (9, 12)}},
            "plaza_cells": 6, "main_cells": 4, "garden_cells": (7, 6), "sign": 0.7, "street_blades": 0.12,
            "shacks": 0.0, "enter_doors": 0.15,
        },
        "variants": (0.25, 0.35, 0.25, 0.15), "civic_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.85), ("wall_door", 0.15)],
            "ground": {"street": [("wall_shopfront", 0.5), ("wall_arch_round", 0.15), ("wall_door", 0.2), ("wall_plain", 0.15)],
                       "lane": [("wall_door", 0.3), ("wall_window_s", 0.25), ("wall_plain", 0.45)]},
            "upper": {"street": [("wall_window_m", 0.55), ("wall_window_pair", 0.2), ("wall_plain", 0.25)],
                      "lane": [("wall_window_s", 0.45), ("wall_plain", 0.55)],
                      "air": [("wall_window_s", 0.3), ("wall_plain", 0.7)]},
            "civic_ground": [("wall_arch_pointed", 0.6), ("wall_plain", 0.4)],
            "civic_upper": [("wall_arch_pointed", 0.4), ("wall_plain", 0.6)],
        },
        "cull_slots": True,
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": None, "crown_civic": "green_hip",
                 "edge_street": [("edge_gable_step", 1.0)],
                 "pitched": {"run": "roof_pitched_pantile", "end": "roof_pitched_pantile_end", "civic": True}},
        "marks": [{"type": "civic_tower", "pieces": ["minaret_base", "minaret_shaft", "church_spire_copper"], "storeys": 6},
                  {"type": "roof_towers", "piece": "minaret_base", "share": 0.02, "storeys": (1, 1)}],
        "overlay": {"lantern": 0.45, "cable": 0.08, "dish": 0.06, "laundry": 0.02, "pipe": 0.15},
        "foliage": {"plaza": ["sycamore"], "green": ["rowan", "sycamore", "beech", "holly", "heather"],
                    "bank": ["willow", "heather"], "lane_wall": ["ivy_ferns"], "rates": {"lane_wall": 0.12}},
        "kit_requests": [
            ("roof_slate_steep", "steep 45-55 deg slate roof run (cell roof run + end)", "roof_pitched_pantile"),
            ("chimney_stack_pots", "the many-pot chimney stack on a gable (roof decor)", "minaret_base stubs"),
            ("turret_stair_conical", "the turnpike stair tower with a conical slate cap (corner tower)", "none"),
            ("wall_pend_k", "the arched pend: a close entering under a land (passage)", "wall_arch_round_k"),
            ("crown_spire", "St Giles' crown spire (crown)", "church_spire_copper"),
            ("mercat_cross", "the mercat cross on its octagonal base (cell decor)", "none"),
        ],
    }
