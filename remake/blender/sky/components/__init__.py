"""The sky islands' shared component library (research/sky_islands/architecture/00_brief.md, "Round-2 build
contract"; the ids: components.json; the map: ids.py).

    import sky_components as SC            (remake/blender/sky_components.py loads this package)
    SC.place(b, part, cid, frame, size=None, variant=None, mat=None, palette=None, **kw) -> [anchor empties]
    SC.panel(b, style_id, kind, frame, bay_w, storey_h, **kw)                          -> [anchor empties]
    SC.ceiling(b, part, rect, z, variant)                                              -> [anchor empties]
    SC.catalogue() -> {cid: {"family", "size_m", "anchor", "variants", "alias"}}

frame: a 4x4 Matrix (Blender, z up) at the component's anchor: the origin on the wall face at the component's
bottom centre (a free-standing piece: its base centre), +Z up, +Y OUT of the facade (toward the street; a free
piece's front), +X = Y x Z (that is, to the LEFT of someone facing the wall from the street).  Keep frames level
(a turn about z only) and a component becomes a shared kit piece (gbkit): the same call made twice is stored once.
A component never touching grade (z within 3 cm of 0 is "on grade": gbkit leaves those in the building) kits; the
ground-level pieces here start at z 0.035 so they still can.

palette: a style id (its styles.json colours) or a dict role -> '#hex' (roles: mats.py).  mat: {role: material
key} to force materials (e.g. {"wall": the building's own wall material}).

Anchors (empties for SkySigns, sky_signs.gd):  sign_<kind>_<w>x<h>_<n> (a face: origin at the face's bottom
centre, Godot +Z out of the face, +X the viewer's right);  glow_<motif>_<n>_<len> (a light run along Godot +X from
the origin, len metres);  lights_<n>_0 / lights_<n>_1 (a string of bulbs between the two).  Kinds are single
words (blade, lightbox, painted, brass, chochin, neon, dotmatrix, video, billboard, figure).
"""
import json
import math
import os

import bpy
from mathutils import Matrix, Vector

from . import fam_facade as FF
from . import fam_mass as FM
from . import fam_signs as FS
from .geo import G
from .ids import IDS
from .mats import Mats, palette_of, styles

CEILING_VARIANTS = FS.CEILINGS
FAMILIES = {
    "opening": FF.opening, "lattice": FF.lattice, "oriel": FF.oriel, "balcony": FF.balcony, "eave": FF.eave,
    "awning": FF.awning, "bracket": FF.bracket_fam, "parapet": FF.parapet, "band": FF.band,
    "dome": FM.dome, "chhatri": FM.chhatri, "tower": FM.tower, "gable": FM.gable, "roofpiece": FM.roofpiece,
    "stair": FM.stair, "ladder": FM.ladder, "bridge": FM.bridge, "clutter": FM.clutter, "column": FM.column,
    "cell": FM.cell, "court": FM.court,
    "sign": FS.sign, "lamp": FS.lamp, "lights": FS.lights, "shopfront": FS.shopfront, "ceiling_module": FS.ceiling_module,
}

_COMP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
                                      "research", "sky_islands", "architecture", "components.json"))
_comp_cache = {}

FAMILY_DEFAULT = {      # (w, h, d) when neither the id nor components.json gives them
    "opening": (1.0, 1.8, 0.1), "lattice": (1.0, 1.4, 0.05), "oriel": (1.6, 2.4, 0.8), "balcony": (2.4, 1.0, 1.0),
    "eave": (3.0, 0.4, 0.8), "awning": (3.0, 1.2, 1.2), "bracket": (0.25, 0.5, 0.4), "parapet": (3.0, 1.1, 0.25),
    "band": (3.0, 0.3, 0.03), "dome": (3.0, 3.0, 3.0), "chhatri": (3.0, 4.0, 3.0), "tower": (2.5, 12.0, 2.5),
    "gable": (6.0, 4.0, 0.3), "roofpiece": (4.0, 3.0, 3.0), "stair": (3.0, 3.0, 0.9), "ladder": (0.5, 3.0, 0.2),
    "bridge": (1.6, 2.4, 6.0), "clutter": (1.2, 1.6, 1.2), "column": (0.4, 3.2, 0.4), "cell": (2.8, 2.6, 4.0),
    "court": (2.0, 2.0, 2.0), "sign": (2.0, 0.8, 0.2), "lamp": (0.3, 0.5, 0.3), "lights": (3.0, 0.3, 0.1),
    "shopfront": (3.0, 3.2, 0.3), "ceiling_module": (0.6, 0.0, 0.6),
}
VARIANTS = {
    "opening": ["rect", "round", "pointed", "horseshoe", "lobed", "cusped", "ogee", "circle"],
    "lattice": ["grid", "diag", "star", "turned", "bars", "louvre"],
    "eave": ["slab", "tile", "green_tile", "timber", "fretwork", "eyebrow", "cornice", "stack", "crest"],
    "awning": ["straight", "scalloped", "tarp", "shed"],
    "parapet": ["crenel", "rounded", "screen", "jali", "rail", "plain"],
    "band": ["plain", "ablaq", "brick", "inlay", "tiles", "stucco", "motif", "dado", "wave", "chevron", "sunburst",
             "timber", "clapboard", "corrugated", "geometric", "mirror", "mural", "merchant"],
    "dome": ["hemi", "onion", "ribbed", "pointed", "skylight", "saucer"],
    "tower": ["minaret", "pyramid", "round", "square", "tapered", "belfry", "clock", "menzeh", "turnpike", "ziggurat"],
    "gable": ["step", "neck", "bell", "cornice", "false", "pediment"],
    "roofpiece": ["hip", "gable", "chalet", "dormer", "bump", "altana", "pergola", "loggia"],
    "stair": ["steel", "spiral", "steep", "beam", "cut", "core", "helix"],
    "bridge": ["sky", "plank", "room", "corridor", "tunnel", "backshop"],
    "clutter": ["tank", "drum", "ac", "antenna", "shack", "stall", "loft", "chimney", "vent", "trencadis", "rebar",
                "vending", "shrine", "stairhead", "lightshaft", "laundry", "scaffold", "pipes", "tray", "wires",
                "statue_sign", "gantry", "crane", "hangar_door"],
    "column": ["round", "turned", "pier", "cluster", "bone", "inverted", "mirrored", "girder", "frame"],
    "cell": ["vault", "souk", "box", "capsule", "ring", "bar", "basso", "pit"],
    "court": ["planter", "planter_wall", "palm", "fountain", "channel", "charbagh", "plinth", "pit_rim", "gate",
              "pishtaq", "iwan", "muqarnas"],
    "sign": ["board", "blade", "stack", "lightbox", "corner", "neon", "painted", "billboard", "letters", "directory",
             "dotmatrix", "video", "brass", "nameboard", "figure"],
    "lamp": ["lantern", "paper", "star", "star_paper", "wall", "cn", "post", "tube", "shrine"],
    "lights": ["festoon", "fairy", "jhalar", "outline", "projection", "led", "chaser", "eave", "marquee", "bunting",
               "luminarie", "neon"],
    "shopfront": ["shutter", "glass", "noren", "open", "stall"],
    "ceiling_module": list(FS.CEILINGS),
    "balcony": ["bars", "solid", "iron", "cage", "timber", "glass", "none"],
    "oriel": ["glass", "lattice", "jali", "porthole", "panel"],
}
# variants that live in a different param than "kind"
VARIANT_PARAM = {"opening": "shape", "lattice": "pattern", "balcony": "rail", "oriel": "face"}


def _components():
    if not _comp_cache:
        try:
            _comp_cache.update(json.load(open(_COMP))["components"])
        except OSError:
            pass
    return _comp_cache


# ------------------------------------------------------------------ anchors
_TO_FACE = Matrix.Rotation(math.pi, 4, "Z")      # (local +Y out of the face -> the empty's -Y: glTF/Godot +Z out)


def _count(b, key):
    n = getattr(b, "_skc_n", None)
    if n is None:
        n = b._skc_n = {}
    n[key] = n.get(key, 0) + 1
    return n[key]


def anchor(b, name, frame, local=(0, 0, 0), basis=None):
    """an empty for SkySigns at local (in frame), turned by basis (a 4x4 rotation in the frame)"""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    bpy.context.scene.collection.objects.link(e)
    e.parent = b.root
    e.matrix_world = frame @ Matrix.Translation(local) @ (basis if basis is not None else Matrix.Identity(4))
    out = getattr(b, "sky_anchors", None)
    if out is None:
        out = b.sky_anchors = []
    out.append(e.name)
    return e


class Ctx:
    def __init__(self, b, g, m, cid, fam, params, w, h, d, v, kw):
        self.b, self.g, self.m, self.cid, self.fam, self.p = b, g, m, cid, fam, params
        self.w, self.h, self.d, self.v, self.kw = w, h, d, v, kw
        self.made = []

    def next_id(self, key):
        return _count(self.b, key)

    def sign(self, kind, w, h, at):
        return self.sign_at(self.g, kind, w, h, at)

    def sign_at(self, g, kind, w, h, at):
        name = "sign_%s_%.1fx%.1f_%d" % (kind, w, h, _count(self.b, "sign"))
        e = anchor(self.b, name, g.M, at, _TO_FACE)
        self.made.append(e)
        return e

    def glow(self, motif, at, length, along=None, vertical=False):
        """a light run from `at` along local +X (or toward `along`), length m"""
        d = Vector((1, 0, 0))
        if along is not None:
            d = Vector(along) - Vector(at)
            d.z = 0.0
            d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
        if vertical:
            e = self.lights(at, (at[0], at[1], at[2] - length))
            return e
        x, z = d, Vector((0, 0, 1))
        y = z.cross(x)
        R = Matrix((x, y, z)).transposed().to_4x4()
        name = "glow_%s_%d_%.1f" % (motif, _count(self.b, "glow"), length)
        e = anchor(self.b, name, self.g.M, at, R)
        self.made.append(e)
        return e

    def lights(self, a, b_):
        n = _count(self.b, "lights")
        e0 = anchor(self.b, "lights_%d_0" % n, self.g.M, a)
        e1 = anchor(self.b, "lights_%d_1" % n, self.g.M, b_)
        self.made += [e0, e1]
        return e0


# ------------------------------------------------------------------ place
def _resolve(cid, size, variant):
    fam, params = IDS.get(cid, (None, None))
    if fam is None:
        if cid in FAMILIES:                       # (a family name works too: SC.place(b, p, "dome", f, variant=...))
            fam, params = cid, {}
        else:
            raise KeyError("sky_components: unknown component %r" % cid)
    params = dict(params)
    dw, dh, dd = FAMILY_DEFAULT.get(fam, (1.0, 1.0, 1.0))
    sm = _components().get(cid, {}).get("size_m")
    if isinstance(sm, (list, tuple)) and len(sm) >= 2:
        dw, dh = float(sm[0]), float(sm[1])
        if len(sm) >= 3:
            dd = float(sm[2])
    w, h, d = params.pop("w", dw), params.pop("h", dh), params.pop("d", dd)
    if size:
        w = size[0]
        if len(size) > 1 and size[1] is not None:
            h = size[1]
        if len(size) > 2 and size[2] is not None:
            d = size[2]
    v = variant or params.get("variant") or params.get("kind") or params.get(VARIANT_PARAM.get(fam, "kind"))
    if variant and fam in VARIANT_PARAM:
        params[VARIANT_PARAM[fam]] = variant
    elif variant:
        params["kind"] = variant
    return fam, params, w, h, d, v


def _place(b, part, cid, frame, size=None, variant=None, mat=None, palette=None, **kw):
    fam, params, w, h, d, v = _resolve(cid, size, variant)
    params.update(kw.pop("params", {}))
    if part is None:
        part = "sky_components"
    p = b.part(part) if isinstance(part, str) else part
    pal = palette_of(palette) if isinstance(palette, str) else (palette or {})
    m = Mats(b, pal, mat)
    c = Ctx(b, G(p, frame), m, cid, fam, params, w, h, d, v, kw)
    FAMILIES[fam](c)
    return c.made


def _frame_of(a, k):
    fr = k.get("frame") if "frame" in k else a[3]
    return fr.to_translation(), (fr.col[0].to_3d().normalized(), fr.col[1].to_3d().normalized(), fr.col[2].to_3d().normalized())


def _kitted(fn):
    try:
        import gbkit
    except ImportError:
        return fn
    return gbkit.wrap(fn, _frame_of)


place = _kitted(_place)


# ------------------------------------------------------------------ facade bays
SHAPE_FROM = [("arch_horseshoe", "horseshoe"), ("arch_lobed", "lobed"), ("arch_cusped", "cusped"),
              ("arch_pointed", "pointed"), ("window_organic", "ogee"), ("window_arched", "round"), ("arch_opening", "round")]
ORIEL_FROM = [("roshan_bay", "roshan_bay"), ("mashrabiya_box", "mashrabiya_box"), ("jharokha", "jharokha"),
              ("galeria_glazed", "galeria_glazed"), ("capsule_box", "capsule_box"), ("bay_window_box", "bay_window_box"),
              ("window_wall_gallery", "galeria_glazed")]
BALC_FROM = [("balcony_cage", "balcony_cage"), ("balcony_iron", "balcony_iron"), ("balcony_timber_covered", "balcony_timber_covered"),
             ("balcony_curved", "balcony_curved"), ("gallery_iron", "gallery_iron"), ("gallery_timber", "gallery_timber"),
             ("balcony_band", "balcony_band"), ("gallery_rail", "gallery_rail"), ("balcony_cantilever", "balcony_cantilever")]
BAND_FROM = [("ablaq_band", "ablaq_band"), ("glazed_inlay_band", "glazed_inlay_band"), ("plaster_band", "plaster_band"),
             ("inlay_band", "inlay_band"), ("timber_band", "timber_band"), ("motif_relief_band", "motif_relief_band"),
             ("wave_band", "wave_band"), ("painted_motif", "painted_motif")]
SCREEN_FROM = [("jali_screen", "jali_screen"), ("mashrabiya_box", "screen_lattice"), ("screen_lattice", "screen_lattice"),
               ("grille_geometric", "grille_geometric")]


def recipe(style_id):
    """what a style's bays are made of (from its styles.json components and openings)"""
    st = styles().get(style_id or "", {})
    comps = set(st.get("components", [])) | set(st.get("openings", []))
    pick = lambda table, default=None: next((v for k, v in table if k in comps), default)
    return {
        "shape": pick(SHAPE_FROM, "rect"),
        "oriel": pick(ORIEL_FROM, "bay_window_box"),
        "balcony": pick(BALC_FROM, "balcony_cantilever"),
        "band": pick(BAND_FROM),
        "screen": pick(SCREEN_FROM, "screen_lattice"),
        "shutters": "shutters" in comps,
        "grille": "reja_grille" if "reja_grille" in comps else ("window_grille" if "window_grille" in comps or "balcony_cage" in comps else None),
        "eave": "chhajja" if "chhajja" in comps else ("eyebrow_shade" if "eyebrow_shade" in comps else None),
        "cladding": "corrugated_panel" if "corrugated_panel" in comps else ("clapboard_panel" if "clapboard_panel" in comps else None),
        "ac": "ac_unit" in comps,
        "led": "led_band" in comps or "lights_outline" in comps,
        "shopfront": "noren" if "noren" in comps else "shutter",
    }


def _panel(b, style_id, kind, frame, bay_w, storey_h, **kw):
    """One facade bay, bay_w wide and storey_h high, as a whole kit piece: the wall (from y -t to 0, with its hole)
    and what fills and dresses the hole, in the style's vocabulary.  kind: plain | window | window_pair | door |
    shopfront | balcony | bay_box | screen | arch.  kw: part, wall_t (0.25), palette (style id default), mat,
    shape (override), wall_role ("wall").  Returns the anchors."""
    from .geo import arch_outline
    part = kw.get("part", "sky_facade")
    p = b.part(part) if isinstance(part, str) else part
    pal = palette_of(kw.get("palette", style_id)) if isinstance(kw.get("palette", style_id), str) else kw.get("palette")
    m = Mats(b, pal, kw.get("mat"))
    g = G(p, frame)
    rc = recipe(style_id)
    t = kw.get("wall_t", 0.25)
    wall = m(kw.get("wall_role", "wall"))
    shape = kw.get("shape", rc["shape"])
    n = 6
    made = []
    sub = lambda cid, at, size=None, variant=None, **k2: made.extend(_place(b, p, cid, frame @ Matrix.Translation(at), size=size, variant=variant, palette=pal, mat=kw.get("mat"), **k2))

    def wall_with(op_shape, ow, oh, sill):
        outer = arch_outline("rect", bay_w, storey_h, n)
        inner = [(x, z + sill) for x, z in arch_outline(op_shape, ow, oh, n)]
        g.ring_xz(outer, inner, -t, 0.0, wall)
        # the reveal's floor (a sill board inside) is the ring's own inner face

    if kind == "plain":
        g.box((-bay_w / 2, -t, 0.0), (bay_w / 2, 0.0, storey_h), wall)
        if rc["cladding"]:
            sub(rc["cladding"], (0, 0, 0.1), size=(bay_w, storey_h - 0.2))
    elif kind in ("window", "screen", "window_pair"):
        ow = min(bay_w * (0.3 if kind == "window_pair" else 0.45), 1.4)
        oh = storey_h * 0.5
        sill = storey_h * 0.3
        if kind == "window_pair":
            # two openings: two half-bays side by side (each its own ring)
            for sx in (-1, 1):
                gh = G(p, frame @ Matrix.Translation((sx * bay_w / 4, 0, 0)))
                outer = arch_outline("rect", bay_w / 2, storey_h, n)
                inner = [(x, z + sill) for x, z in arch_outline(shape, ow, oh, n)]
                gh.ring_xz(outer, inner, -t, 0.0, wall)
                made.extend(_place(b, p, "window_arched" if shape != "rect" else "window_small",
                                   frame @ Matrix.Translation((sx * bay_w / 4, 0, sill)), size=(ow, oh), variant=shape,
                                   palette=pal, mat=kw.get("mat"), recess=t * 0.6, params={"frame": 0.08}))
        else:
            wall_with(shape, ow, oh, sill)
            if kind == "screen":
                sub(rc["screen"], (0, 0, sill), size=(ow, oh * (0.85 if shape != "rect" else 1.0)))
                g.box((-ow / 2, -t * 0.6, sill), (ow / 2, -t * 0.6 + 0.012, sill + oh * 0.8), m("glass"))
            else:
                sub("window_arched" if shape != "rect" else "window_small", (0, 0, sill), size=(ow, oh), variant=shape,
                    recess=t * 0.6, params={"frame": 0.09})
                if rc["grille"]:
                    sub(rc["grille"], (0, 0.075 if rc["grille"] == "window_grille" else 0.0, sill), size=(ow + 0.1, oh * 0.92))
                if rc["shutters"]:
                    for sx in (-1, 1):
                        sub("shutters", (sx * (ow / 2 + 0.25), 0.0, sill), size=(ow / 2, oh * 0.9))
            if rc["eave"]:
                sub(rc["eave"], (0, 0, sill + oh + 0.25), size=(ow + 0.6, 0.3, 0.5))
            if rc["ac"] and (hash(style_id or "") & 1):
                sub("ac_unit", (ow / 2 + 0.55, 0, sill - 0.2), size=(0.7, 0.5, 0.3))
    elif kind == "door":
        ow, oh = min(bay_w * 0.5, 1.2), min(2.4, storey_h - 0.5)
        wall_with(shape, ow, oh, 0.035)
        sub("door_studded" if shape != "rect" else "door_room", (0, 0, 0.035), size=(ow, oh), variant=shape, recess=t * 0.5)
    elif kind == "arch":
        ow, oh = bay_w * 0.7, storey_h * 0.85
        wall_with(shape if shape != "rect" else "round", ow, oh, 0.035)
        sub("arch_opening", (0, 0, 0.035), size=(ow, oh), variant=shape if shape != "rect" else "round")
    elif kind == "shopfront":
        ow, oh = bay_w - 0.4, storey_h - 0.9
        wall_with("rect", ow, oh, 0.035)
        sub("shopfront_shutter", (0, 0, 0.0), size=(bay_w - 0.2, storey_h - 0.1), variant=kw.get("front", rc["shopfront"]))
    elif kind == "balcony":
        ow, oh = min(bay_w * 0.55, 1.6), min(storey_h * 0.78, 2.4)
        wall_with(shape, ow, oh, 0.035)
        sub("french_window", (0, 0, 0.035), size=(ow, oh), variant=shape, recess=t * 0.6)
        sub(rc["balcony"], (0, 0, 0.031), size=(bay_w * 0.85, None, 1.1))          # (just under the window's threshold)
    elif kind == "bay_box":
        ow, oh = min(bay_w * 0.6, 1.6), storey_h * 0.62
        sill = storey_h * 0.22
        wall_with("rect", ow, oh, sill)
        sub(rc["oriel"], (0, 0, sill - 0.25), size=(ow + 0.4, oh + 0.45, 0.8))
    if rc["band"]:
        sub(rc["band"], (0, 0, storey_h - 0.3), size=(bay_w, 0.25))
    if kw.get("led", rc["led"]) and kind != "plain":
        c = Ctx(b, g, m, "panel", "panel", {}, bay_w, storey_h, t, None, {})
        c.glow("led", (-bay_w / 2, 0.035, storey_h - 0.02), bay_w)
        made += c.made
    return made


panel = _kitted(_panel)


# ------------------------------------------------------------------ ceilings
def ceiling(b, part, rect, z, variant="suspended_grid_600", palette=None, mat=None):
    """A room's ceiling: rect (x0, y0, x1, y1) in the building's frame, hung from z down.  Laid in modules (each a
    kit piece: one 1.2 x 1.2 m module of four 0.6 tiles, or a 0.9 coffer ...) from the rect's corner; the part
    modules at the far edges are cut to fit."""
    v = variant if variant in FS.CEILINGS else "suspended_grid_600"
    mod = {"suspended_grid_600": 0.6, "pressed_tin": 0.6, "artesonado_coffer": 1.2, "batten": 0.91, "coffered": 0.9,
           "painted_plaster": 2.4}[v]
    x0, y0, x1, y1 = rect
    made = []
    nx = max(1, int(math.ceil((x1 - x0) / mod - 1e-6)))
    ny = max(1, int(math.ceil((y1 - y0) / mod - 1e-6)))
    for i in range(nx):
        for j in range(ny):
            ax, ay = x0 + i * mod, y0 + j * mod
            w, d = min(mod, x1 - ax), min(mod, y1 - ay)
            if w < 0.02 or d < 0.02:
                continue
            fr = Matrix.Translation((ax + w / 2, ay + d / 2, z - 0.004))
            made += place(b, part, "ceiling_tile", fr, size=(w, 0.0, d), variant=v, palette=palette, mat=mat)
    return made


# ------------------------------------------------------------------ the catalogue
ANCHOR_DOC = {
    "opening": "bottom centre of the opening on the wall face; the frame stands proud +Y",
    "lattice": "bottom centre on the wall face", "oriel": "the bay's floor at the wall face (brackets hang below)",
    "balcony": "the slab's top at the wall face (the slab hangs below z 0)", "eave": "the eave's root on the wall",
    "awning": "the awning's top edge on the wall", "bracket": "the top of the bracket at the wall",
    "parapet": "the roof edge (the wall's outer face) at roof level; it stands on the wall top, inward (-Y)",
    "band": "bottom centre on the wall face", "dome": "base centre", "chhatri": "base centre", "tower": "base centre",
    "gable": "bottom centre of the gable on the wall face (in the wall plane, -Y thick)", "roofpiece": "base centre",
    "stair": "the bottom step's corner at the wall: runs up along +X", "ladder": "bottom centre at the wall",
    "bridge": "the near end's deck centre: spans along +Y", "clutter": "base centre (wall pieces: bottom centre on the face)",
    "column": "base centre", "cell": "the cell's front face, bottom centre (it runs back along -Y)", "court": "base centre",
    "sign": "the mount's bottom centre on the wall", "lamp": "the bracket's foot on the wall", "lights": "the run's centre on the wall",
    "shopfront": "bottom centre of the bay on the wall face", "ceiling_module": "the module's centre at the ceiling plane (hangs below)",
}


def catalogue():
    out = {}
    comp = _components()
    for cid, (fam, params) in IDS.items():
        out[cid] = {"family": fam, "params": {k: v for k, v in params.items() if k != "alias"},
                    "size_m": comp.get(cid, {}).get("size_m") or list(FAMILY_DEFAULT.get(fam, (1, 1, 1))),
                    "anchor": ANCHOR_DOC.get(fam, ""), "variants": VARIANTS.get(fam, []), "alias": params.get("alias")}
    return out
