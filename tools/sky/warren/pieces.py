"""pieces.py -- the piece ids the generator places (r4_design §4).  The KIT stream publishes the real catalogue as
godot_project/remake/sky/warrens/pieces.json (schema: {piece_id: {glb, mesh, bay, slots, lod1, collide}}); until it
does, this placeholder list (same schema, no glb) stands in.  Ids the kit doesn't have yet are reported, not dropped:
the placements still name them and the runtime draws a box for an unknown piece.

`tris` is a planning estimate per placement (for chunk budgets), not the kit's real count.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KIT_JSON = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens", "pieces.json")

# id: (kind, slots, lod1, collide, tris)   kind: face | corner | cell | ground | overlay | mark
_P = {
    # walls (a 3 m bay x 3.2 m storey, on the cell's -Z face); variant 0 thin, 1 thick
    "wall_plain": ("face", ["wall", "trim"], "box", True, 40),
    "wall_window_s": ("face", ["wall", "trim", "frame", "glass"], "box", True, 120),
    "wall_window_m": ("face", ["wall", "trim", "frame", "glass"], "box", True, 140),
    "wall_window_l": ("face", ["wall", "trim", "frame", "glass"], "box", True, 150),
    "wall_window_pair": ("face", ["wall", "trim", "frame", "glass"], "box", True, 220),
    "wall_window_grille": ("face", ["wall", "trim", "frame", "glass", "metal"], "box", True, 260),
    "wall_door": ("face", ["wall", "trim", "frame"], "box", True, 120),
    "wall_door_studded": ("face", ["wall", "trim", "frame", "metal"], "box", True, 220),
    "wall_shopfront": ("face", ["wall", "trim", "frame", "glass", "metal"], "box", True, 220),
    "wall_shopfront_arcade": ("face", ["wall", "trim", "frame", "glass"], "box", True, 300),
    "wall_screen": ("face", ["wall", "trim", "screen"], "box", True, 380),
    "wall_balcony_cage": ("face", ["wall", "trim", "frame", "glass", "metal"], "box", True, 420),
    "wall_balcony_timber": ("face", ["wall", "trim", "frame", "glass", "screen"], "box", True, 360),
    "wall_balcony_iron": ("face", ["wall", "trim", "frame", "glass", "metal"], "box", True, 340),
    "wall_bay": ("face", ["wall", "trim", "frame", "glass"], "box", True, 300),
    "wall_oriel": ("face", ["wall", "trim", "frame", "screen"], "box", True, 420),
    "wall_arch_round": ("face", ["wall", "trim"], "box", True, 160),
    "wall_arch_pointed": ("face", ["wall", "trim"], "box", True, 170),
    "wall_arch_horseshoe": ("face", ["wall", "trim"], "box", True, 180),
    "wall_blind_arch": ("face", ["wall", "trim"], "box", True, 120),
    "wall_gallery": ("face", ["wall", "trim", "frame", "screen"], "box", True, 320),
    "arch_mouth": ("face", ["wall", "trim"], "keep", False, 120),        # a lane's tunnel mouth, at ground
    # corners (at the cell's (-X, -Z) corner)
    "corner_out": ("corner", ["wall", "trim"], "drop", False, 16),
    "corner_in": ("corner", ["wall", "trim"], "drop", False, 12),
    "corner_column": ("corner", ["trim"], "drop", True, 40),
    "corner_round": ("corner", ["wall"], "drop", False, 48),
    "corner_chamfer": ("corner", ["wall", "trim"], "drop", False, 20),
    # roofs and the shell's top and underside
    "roof_terrace": ("cell", ["roof"], "box", True, 8),
    "roof_tile": ("cell", ["roof"], "box", True, 24),
    "parapet_plain": ("face", ["wall", "trim"], "keep", True, 24),
    "parapet_crenel": ("face", ["wall", "trim"], "keep", True, 90),
    "parapet_stepped": ("face", ["wall", "trim"], "keep", True, 60),
    "parapet_jali": ("face", ["wall", "screen"], "keep", True, 160),
    "eave_tile": ("face", ["roof", "trim"], "keep", False, 60),
    "eave_green_tile": ("face", ["roof", "trim"], "keep", False, 80),
    "eave_tin": ("face", ["roof", "metal"], "keep", False, 30),
    "gable_front": ("face", ["wall", "roof", "trim"], "keep", True, 60),
    "dome_cap": ("cell", ["roof", "trim"], "keep", True, 320),
    "pagoda_tier": ("cell", ["roof", "trim"], "keep", True, 260),
    "soffit": ("cell", ["wall"], "drop", True, 8),
    "plinth": ("cell", ["wall", "trim"], "box", True, 20),
    # interiors (enter cells only)
    "interior_floor": ("cell", ["floor"], "drop", True, 8),
    "interior_ceiling": ("cell", ["ceiling"], "drop", False, 60),
    "counter": ("cell", ["trim", "metal"], "drop", True, 80),
    "shelves": ("cell", ["trim"], "drop", True, 120),
    "table_set": ("cell", ["trim", "fabric"], "drop", False, 160),
    "bed": ("cell", ["fabric", "trim"], "drop", False, 120),
    "lamp": ("cell", ["metal", "emissive"], "drop", False, 40),
    # ground (DECK pieces follow the deck)
    "pave_main": ("ground", ["paving"], "keep", False, 4),
    "pave_lane": ("ground", ["paving"], "keep", False, 4),
    "pave_plaza": ("ground", ["paving"], "keep", False, 4),
    "pave_garden": ("ground", ["grass"], "keep", False, 4),
    "pave_court": ("ground", ["paving"], "keep", False, 4),
    "steps": ("ground", ["paving"], "keep", True, 40),
    "stair_int": ("cell", ["trim", "metal"], "drop", True, 120),
    "stair_ext": ("face", ["metal", "trim"], "keep", True, 160),
    "stair_spiral": ("cell", ["metal"], "keep", True, 200),
    "ladder": ("face", ["metal"], "drop", True, 40),
    "bridge_plank": ("cell", ["trim", "fabric"], "keep", True, 60),
    "bridge_timber": ("cell", ["trim"], "keep", True, 90),
    "bridge_steel": ("cell", ["metal"], "keep", True, 80),
    "arcade_pier": ("corner", ["wall", "trim"], "keep", True, 60),
    "market_stall": ("ground", ["fabric", "trim"], "drop", False, 160),
    "awning": ("face", ["fabric", "metal"], "drop", False, 40),
    "planter": ("ground", ["trim", "grass"], "drop", False, 40),
    "bench": ("ground", ["trim"], "drop", True, 40),
    "well": ("ground", ["wall", "trim"], "keep", True, 90),
    "fountain_basin": ("ground", ["wall", "trim"], "keep", True, 160),
    # the newest layer (E5)
    "cable_span": ("cell", ["metal"], "drop", False, 24),
    "ac_unit": ("face", ["metal"], "drop", False, 24),
    "pipe_run": ("face", ["metal"], "drop", False, 24),
    "water_tank": ("cell", ["metal"], "keep", True, 80),
    "antenna": ("cell", ["metal"], "keep", False, 30),
    "satellite_dish": ("cell", ["metal"], "drop", False, 40),
    "shack_panel": ("face", ["metal", "trim"], "keep", True, 40),
    "laundry": ("cell", ["fabric"], "drop", False, 40),
    "lantern": ("cell", ["metal", "emissive"], "drop", False, 30),
    "festoon": ("cell", ["emissive"], "drop", False, 30),
    "fluoro_tube": ("cell", ["emissive"], "drop", False, 12),
    "sign_blade": ("face", ["metal", "emissive"], "keep", False, 24),
    "sign_box": ("face", ["metal", "emissive"], "keep", False, 16),
    "sign_board": ("face", ["metal", "emissive"], "keep", False, 12),
    "shoring_beam": ("cell", ["trim"], "drop", False, 16),
    # civilisation marks
    "zellige_fountain": ("ground", ["wall", "tile"], "keep", True, 260),
    "minaret_square": ("cell", ["wall", "trim", "tile"], "keep", True, 140),
    "minaret_top": ("cell", ["wall", "trim", "roof"], "keep", True, 220),
    "cantilever_step": ("face", ["wall"], "keep", True, 40),
    "tower_seam": ("face", ["wall", "metal"], "keep", False, 30),
    "roof_playground": ("cell", ["metal", "paving"], "drop", False, 120),
    "warning_light": ("cell", ["emissive"], "keep", False, 12),
}


def catalogue():
    """{id: {...}} -- the kit's pieces.json if published (the KIT stream), else the placeholders"""
    out = {k: {"kind": v[0], "slots": v[1], "lod1": v[2], "collide": v[3], "tris": v[4], "bay": [3.0, 3.2],
               "glb": None, "mesh": None} for k, v in _P.items()}
    if os.path.exists(KIT_JSON):
        kit = json.load(open(KIT_JSON))
        kit = kit.get("pieces", kit)
        for k, v in kit.items():
            out.setdefault(k, {"kind": "?", "tris": 100})
            out[k].update(v)
            out[k]["from_kit"] = True
    return out


def missing_from_kit(used):
    if not os.path.exists(KIT_JSON):
        return sorted(used)
    kit = json.load(open(KIT_JSON))
    kit = kit.get("pieces", kit)
    return sorted(u for u in used if u not in kit)
