"""mats -- a style's palette as material roles (gblib Building.mat: content-hashed names, shared across buildings).

Roles: wall, wall2, trim, accent, accent2, wood, dark_wood, metal, iron, roof, tile, tile2, stone, fabric, fabric2,
glass (lit at night: alpha < 0.6 -- RemakeBuilding.lit_glass), lamp (warm, emissive), neon_tube (dark tube, the
runtime lights it), cloth, plant, water, ceiling, ceiling2, mirror, rope, canvas, concrete, render.
"""
import json
import os

import gblib

_HERE = os.path.dirname(os.path.abspath(__file__))
_STYLES = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "..", "research", "sky_islands", "architecture", "styles.json"))
_cache = {}

BASE = {
    "wall": "#d8cfbf", "wall2": "#b9ad98", "trim": "#f2ede2", "accent": "#b5452c", "accent2": "#2f6e8e",
    "wood": "#8a5a32", "dark_wood": "#4e3220", "metal": "#7b8188", "iron": "#2c2d30", "roof": "#6d4a3a",
    "tile": "#2e7d6b", "tile2": "#e8e2d0", "stone": "#a69a86", "fabric": "#c23b2a", "fabric2": "#e8c25a",
    "glass": "#3a4a58", "lamp": "#ffd08a", "neon_tube": "#2a2a33", "cloth": "#d9d2c3", "plant": "#4f7a3a",
    "water": "#30546a", "ceiling": "#ecebe6", "ceiling2": "#b7b3a8", "mirror": "#9fb6c8", "rope": "#8c7a5b",
    "canvas": "#e9e4d8", "concrete": "#9b9a96", "render": "#cfc6b4",
}
ROUGH = {"metal": 0.45, "iron": 0.6, "glass": 0.1, "mirror": 0.05, "tile": 0.3, "tile2": 0.3, "lamp": 0.4, "water": 0.1}
METAL = {"metal": 0.7, "iron": 0.5, "mirror": 0.9}


def styles():
    if "styles" not in _cache:
        try:
            d = json.load(open(_STYLES))
            _cache["styles"] = {s["id"]: s for s in d["styles"]}
        except OSError:
            _cache["styles"] = {}
    return _cache["styles"]


def palette_of(style_id):
    """the style's colours (styles.json: walls.palette, signage.palette, night.mood) mapped onto the roles"""
    st = styles().get(style_id or "", {})
    pal = dict(BASE)
    wp = [c for c in st.get("walls", {}).get("palette", []) if isinstance(c, str) and c.startswith("#")]
    roles = ["wall", "trim", "accent", "wall2", "accent2", "wood", "roof", "tile", "tile2", "stone"]
    for r, c in zip(roles, wp):
        pal[r] = c
    sp = [c for c in st.get("signage", {}).get("palette", []) if isinstance(c, str) and c.startswith("#")]
    if sp:
        pal["fabric"] = sp[0]
        if len(sp) > 1:
            pal["fabric2"] = sp[1]
    mood = [c for c in st.get("night", {}).get("mood", []) if isinstance(c, str) and c.startswith("#")]
    if mood:
        pal["lamp"] = mood[0]
    return pal


def lin(h):
    return tuple(gblib.srgb_to_linear(c) for c in gblib.hex_rgb(h))


class Mats:
    """role -> Building material key, for one palette"""

    def __init__(self, b, pal=None, override=None):
        self.b = b
        self.pal = dict(BASE)
        self.pal.update(pal or {})
        self.override = override or {}

    def __call__(self, role):
        if role in self.override:
            return self.override[role]
        h = self.pal.get(role) or BASE.get(role) or "#cccccc"
        key = "skc_%s_%s" % (role, h.lstrip("#").lower())
        if key in self.b.mats:
            return key
        kw = {}
        if role == "glass":
            kw["alpha"] = 0.45
        elif role == "mirror":
            kw["alpha"] = 0.55
        elif role == "water":
            kw["alpha"] = 0.7
        elif role == "lamp":
            kw["emission"] = lin(h)
        return self.b.mat(key, color=lin(h), rough=ROUGH.get(role, 0.85), metal=METAL.get(role, 0.0), **kw)
