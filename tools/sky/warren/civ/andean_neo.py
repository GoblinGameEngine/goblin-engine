"""Andean layered towns (r3_andean_neo.md: Cusco, La Paz / El Alto, Lima's balconies).

The mark: layers you can read: Inca polygonal grey stone bases, white colonial storeys with carved box balconies and
red tile roofs round arcaded patios on the Laws-of-the-Indies grid and the Plaza de Armas; raw-brick self-built stacks
with rebar; and the cholets -- mirror glass in loud geometric colour, a chalet on top."""
from civ.family import FamilyCiv


class AndeanNeo(FamilyCiv):
    id = "andean_neo"
    name = "Andean layered town"
    arch_mouth = "wall_arch_round"
    SPEC = {
        "lanes": "grid",
        "params": {
            "grid_cells": (5, 8), "jog": 0.1, "blind": 0.08, "break": 0.04, "light_wells": 0.0,
            "lot_cells": (5, 12), "courts": True, "court_min_lot": 9, "court_share": 0.15,
            "flats_per_level": False, "roof_walk": False,
            "e1_levels": (2, 2), "max_levels": 7, "civic_levels": 3, "tower_levels": (4, 7), "tower_cells": 4,
            "sabat_from": 9, "jetty_from": 2, "work_share": 0.2, "civic_min_cells": 10,
            "epochs": {2: {"rise": 0.3, "setback": 0.2, "tower": 0.05},
                       3: {"rise": 0.4, "setback": 0.2, "tower": 0.08, "jetty": 0.08},
                       4: {"rise": 0.4, "setback": 0.25, "tower": 0.1, "jetty": 0.1}},
            "plaza_cells": 7, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.6, "street_blades": 0.1,
            "shacks": 0.04, "shop_share": 0.6,
        },
        "civic_court": True,
        "variants": (0.42, 0.33, 0.1, 0.15), "civic_variant": 0, "ground_variant": 2,
        "thick": 1,
        "facade": {
            "door": "wall_door", "door_civic": "wall_inca_door_k",
            "shop": [("wall_shopfront_arcade", 0.6), ("wall_shopfront", 0.4)],
            "ground": {"street": [("wall_inca_base_k", 0.35), ("wall_arch_round", 0.2), ("wall_window_s", 0.2),
                                  ("wall_door", 0.1), ("wall_plain", 0.15)],
                       "lane": [("wall_inca_base_k", 0.4), ("wall_window_s", 0.15), ("wall_door", 0.1),
                                ("wall_plain", 0.35)],
                       "court": [("wall_arch_round", 0.85), ("wall_plain", 0.15)]},
            "upper": {"street": [("wall_balcony_timber", 0.18), ("wall_box_balcony_k", 0.08), ("wall_window_m", 0.35),
                                 ("wall_plain", 0.35)],
                      "lane": [("wall_window_m", 0.35), ("wall_balcony_timber", 0.1), ("wall_plain", 0.55)],
                      "court": [("wall_arch_round", 0.5), ("wall_balcony_timber", 0.25), ("wall_window_m", 0.25)]},
            # the self-built brick stacks and the cholets
            "variant_upper": {1: [("wall_window_s", 0.35), ("wall_window_grille", 0.15), ("wall_plain", 0.5)],
                              3: [("wall_cholet_front_t", 0.4), ("wall_window_l", 0.3), ("wall_plain", 0.3)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "parapet_plain", "crown_civic": "dome_cap",
                 "pitched": {"run": "roof_tile_red_low", "end": "roof_tile_red_low_end", "variants": [0]}},
        "marks": [{"type": "civic_tower", "pieces": ["bell_tower_baroque_base", "bell_tower_baroque_base", "bell_tower_baroque_belfry", "bell_tower_baroque_cupola"], "storeys": 3},
                  {"type": "fountain"}, {"type": "stalls", "share": 0.12}],
        "overlay": {"cable": 0.3, "tank": 0.15, "dish": 0.08, "laundry": 0.06, "lantern": 0.35, "festoon": 0.25},
        "foliage": {"plaza": ["molle", "queuna"], "green": ["eucalyptus", "molle", "queuna"], "court": ["geranium_pot"],
                    "bank": ["totora_reeds"], "lane_wall": ["geranium_pot"], "roof": ["geranium_pot"],
                    "rates": {"court": 0.4}},
        "kit_requests": [
            ("wall_inca_base_k", "an Inca polygonal fitted-stone ground bay, battered 5 deg, trapezoid doorway variant (wall)", "wall_plain_k on the grey ground variant"),
            ("wall_box_balcony_k", "Lima's carved enclosed box balcony (latticed, 1 m deep) (wall)", "wall_balcony_timber_k / wall_bay_box_k"),
            ("roof_tile_red_low", "a 25-30 deg red tile roof with wide eaves (cell roof)", "flat roof"),
            ("cholet_chalet_top", "the peaked chalet perched on a cholet's roof (crown)", "none"),
            ("ov_rebar_stubs", "rebar sticking up from an unfinished roof slab (roof decor)", "none"),
            ("cable_car", "Mi Teleférico gondola line and cabin (decor)", "none"),
        ],
    }

    def roof_extra(self, L, i, j, lv):
        """red tile roofs on the white colonial houses (stand-in: a hip per cell); flat brick roofs elsewhere"""
        lot = L.lots[L.lot[i, j]] if L.lot[i, j] >= 0 else None
        if lot is None:
            return []
        if lot.get("use") == 3:
            cs = sorted(lot["cells"])
            return ["dome_cap"] if (i, j) == cs[len(cs) // 2] else ["green_hip"]
        from pick import h01
        v = self.lot_palette(lot)
        cs = sorted(c for c in lot["cells"])
        if v == 3 and (i, j) == cs[len(cs) // 2]:
            return ["cholet_chalet_top"]                  # (the chalet on the cholet's roof)
        if v == 1 and h01(L.seed, "rebar", i, j) < 0.15:
            return ["ov_rebar_stubs"]
        return []
