"""
sky.py -- a catalog record of kind "sky": one of the sky islands' style models (research/sky_islands/architecture/;
records written by tools/sky/style_models.py, remake/catalog/SKY-<style>-NN.json).

The user, 2026-10-14: "more variety in the buildings on the islands ... Arabic Old Town ... Hong Kong and Tokyo and
Delhi and Mumbai ... stacked warrens ... make shared components for the buildings, reusing as much as possible ... Each
island needs to be fascinating ... lots and lots of lights with billboards and flashing signs ... Each store has it's own
light up stylized sign. Each apartment complex has mood lighting and a stylish motif ... redo the buildings on each
island to match its style".

A model is one to four blocks (traits.blocks; plan frame: metres, origin the lot's centre, x east, +y the front, z up):
blocks of different heights touch to make the stacked warrens (gbhouse closes a taller block's wall over a lower one's
roof), each a real building inside -- floors, rooms, units, stairs, doors (so tools/rooms/make_rooms.py and the
occupancy keep working):
  slab    a double-loaded corridor of flats (as gen/coastal.build_apartments), stairs at both ends
  tower   a dogleg stair at the rear and one home a floor (Sana'a's tower houses, Tokyo's pencil buildings)
  hall    a market or workshop floor (stall / machine fit-outs) under flats
  ground  "dwelling" | "shops" (a storefront per bay, each its own shop: a fit-out, a glazed street door, a sign) |
          "hall"
The main block's roof is flat and reached by the fire escape on its +x wall (roofaccess.py): every building has roof
access.  Then the style dresses it from the shared kit (gen/sky_kit.py: bays, cages, screens, balconies, galleries,
shutters, arches, bands, jetties, crenels, gable and false fronts, domes, chhatris, towers, shacks, tanks, pergolas,
pagoda eaves; ceiling tiles in the shops and halls), as traits.dress lists.

Anchors for the island's lights (SkySigns, the brief's contract) are written to remake/sky_anchors/<ID>.json in the
GODOT frame of the building (x, y up, z = -plan y; yaw about y, the sign's +Z out of its face):
  sign_<kind>_<w>x<h>   a storefront's sign, a blade sign at a front corner, a rooftop billboard, upper-floor boards
  glow_<motif>_<L>      a mood-light run L m along the anchor's +X (floor lines, the parapet's crown)
  lights_<n>            string-light ends, paired in order
"""
import json
import math
import os
import random

from common import Palette, brick_for, clamp, hexcol, lib_building, rng, std_materials, g, ROOT
import gbhouse as gh
import institution as inst
import shopfit
import sky_kit as K

TE, TI = 0.3, 0.12
STAIR_W = 1.0
ANCHOR_DIR = os.path.join(ROOT, "remake", "sky_anchors")
_STYLES = None


def styles():
    global _STYLES
    if _STYLES is None:
        _STYLES = json.load(open(os.path.join(ROOT, "godot_project", "remake", "sky", "styles.json")))["styles"]
    return _STYLES


# ------------------------------------------------------------------ materials
WALL_WORDS = [  # (keyword in the style's wall materials, library texture, paintable)
    ("skystone", "stucco", True), ("earth", "stucco", True), ("mud", "stucco", True),
    ("corrugated", "corrugated", True), ("tin", "corrugated", True), ("sheet", "corrugated", True), ("zinc", "corrugated", True),
    ("brick", "brick", False), ("ashlar", "sandstone", False), ("sandstone", "sandstone", False), ("stone", "limestone", False),
    ("rubble", "fieldstone", False), ("fieldstone", "fieldstone", False), ("tufo", "sandstone", False),
    ("timber", "board_batten", True), ("clapboard", "clapboard", True), ("board", "board_batten", True), ("wood", "board_batten", True),
    ("concrete", "concrete", False), ("mosaic", "stucco", True), ("tile", "stucco", True), ("glass", "stucco", True),
    ("steel", "stucco", True), ("render", "stucco", True), ("stucco", "stucco", True), ("plaster", "stucco", True),
    ("lime", "stucco", True), ("wash", "stucco", True), ("gypsum", "stucco", True), ("earth", "stucco", True),
    ("mud", "stucco", True), ("skystone", "stucco", True), ("paint", "stucco", True)]


def _wall_tex(words):
    for w in words:
        for key, tex, paint in WALL_WORDS:
            if key in w:
                return tex, paint
    return "stucco", True


def style_materials(b, st, tr):
    """the style's palette onto the library materials: ext / ext2 / ext3 (its body colours), trim, accent, roof_m, tin,
    wood, iron, glass, lattice, stone, tile, canvas, lamp, green, steel, ceiling_tile, tin_ceiling (+ the shop and
    furniture sets)"""
    pal = Palette(b)
    col = tr.get("colors", {})
    bodies = col.get("body") or st.get("walls", {}).get("palette", ["#d8cfbf"])
    trim = col.get("trim", "#ece6d8")
    accent = col.get("accent", "#2f6f8f")
    std_materials(pal, trim=trim, door=accent)
    shopfit.shop_materials(pal)
    tex, paint = _wall_tex(st.get("walls", {}).get("materials", []))
    from common import TILES
    for i, key in enumerate(("ext", "ext2", "ext3")):
        c = bodies[i % len(bodies)]
        if tex == "brick":
            pal.surf(key, brick_for(hexcol(c)), rough=0.85)
        elif tex == "corrugated":
            # (painted tin -- Valparaiso, La Boca: the library's paintable list leaves corrugated untinted, so the tint is
            # given here directly; the game multiplies any material's tint)
            b.mat(key, tex=tex, tile_m=TILES.get(tex, 1.0), tint=hexcol(c), rough=0.6)
        else:
            pal.surf(key, tex, hexcol(c) if paint else None, rough=0.82)
    pal.surf("plaster", "drywall", "#eeeae2", rough=0.85)
    pal.surf("roof", "metal_roof", hexcol(col.get("roof", "#6b6a66")), rough=0.6)
    pal.surf("roof_m", "concrete", rough=0.95)
    pal.surf("floor", "floor_oak" if tr.get("warm", True) else "vct", rough=0.5)
    pal.surf("ceiling", "plaster", "#f2efe8", rough=0.85)
    pal.surf("ceiling_tile", "acoustic", rough=0.85)
    pal.surf("tin_ceiling", "tin_ceiling", rough=0.4)
    pal.surf("found", "concrete", rough=0.9)
    pal.surf("deck", "floor_painted", "#8a8478", rough=0.8)
    pal.surf("tin", "corrugated", hexcol(col.get("tin", "#9aa0a4")), rough=0.6)
    pal.surf("wood", "wood_dark", rough=0.7)
    pal.solid("lattice", hexcol(col.get("lattice", "#6b4a32")), rough=0.75)
    pal.surf("stone", "limestone", rough=0.85)
    pal.surf("tile", "paint_gloss", hexcol(col.get("tile", accent)), rough=0.25)
    pal.solid("trim", hexcol(trim), rough=0.6)
    pal.solid("accent", hexcol(accent), rough=0.5)
    pal.solid("canvas", hexcol(col.get("canvas", accent)), rough=0.9)
    pal.solid("iron", (0.12, 0.12, 0.13), rough=0.5, metal=0.5)
    pal.solid("steel", (0.62, 0.64, 0.66), rough=0.4, metal=0.4)
    pal.solid("glass", (0.25, 0.33, 0.38), rough=0.05, metal=0.3)
    pal.solid("green", (0.25, 0.42, 0.2), rough=0.9)
    pal.solid("lamp", (0.95, 0.75, 0.42), rough=0.6, emission=(0.9, 0.62, 0.3))
    pal.solid("roof_under", (0.5, 0.5, 0.48), rough=0.8)
    pal.solid("curtain", (0.32, 0.3, 0.28), rough=0.9)
    pal.solid("sign_board", hexcol(accent), rough=0.5)
    pal.solid("awning", hexcol(col.get("canvas", accent)), rough=0.9)
    pal.solid("gold", (0.8, 0.62, 0.22), rough=0.3, metal=0.9)
    return pal


# ------------------------------------------------------------------ helpers
PITCH_WORDS = (("chalet", "roof_chalet"), ("hip_roof", "hip"), ("stone_slab", "stone_slab_roof"), ("gable_roof", "gable"),
               ("pitched", "gable"), ("slate", "gable"), ("tin_roof", "gable"), ("steep", "gable"), ("tiled_roof", "hip"))


def _pitched(st):
    """a pitched roof for the side blocks (the main block stays flat: the fire escape's platform, a lark's cradle):
    the roofpiece id or kind, or None"""
    words = " ".join(st.get("roof", []))
    for k, v in PITCH_WORDS:
        if k in words:
            return v
    return None

def _floors(storeys, sh, FL=0.3):
    floors = [(FL, FL + sh - 0.35)]
    for _ in range(1, storeys):
        fz = floors[-1][1] + 0.35
        floors.append((fz, fz + sh - 0.35))
    return floors


def _spec(blocks):
    return dict(t_ext=TE, t_int=TI, era="modern",
                mats=dict(ext="ext", int="plaster", roof="roof", roof_under="roof_under", found="found", floor="floor",
                          ceiling="ceiling", trim="trim", door="door", fascia="trim", porch="deck", post="trim", furn="furniture"),
                blocks=blocks, rooms=[], doors=[], windows=[], stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])


def _flat_roof(parapet=1.2):
    return dict(type="flat", thick=0.35, parapet=parapet, coping="stone")


def _rename(spec, before, prefix):
    """give the rooms a plan helper just added unique names (several blocks share a spec)"""
    ren = {}
    for r in spec["rooms"][before:]:
        nn = prefix + r["name"]
        ren[r["name"]] = nn
        r["name"] = nn
    for r in spec["rooms"][before:]:
        if r.get("open_plan_to") in ren:
            r["open_plan_to"] = ren[r["open_plan_to"]]
    return ren


# ------------------------------------------------------------------ plans
def slab_plan(spec, bl, rnd, pre, ground, shops, hall_kind):
    """a double-loaded corridor of flats (gen/coastal.build_apartments' plan) in block bl; the ground floor's front band
    as shops, or the whole ground floor as a hall"""
    x0, y0, x1, y1 = bl["rect"]
    floors = bl["floors"]
    storeys = len(floors)
    r0 = len(spec["rooms"])
    (c0, c1), _ = inst.corridor_plan(spec, (x0, y0, x1, y1), floors, [([], [])] * storeys, rnd, stairs=storeys > 1)
    _rename(spec, r0, pre)
    rooms, doors = spec["rooms"], spec["doors"]
    spans = []
    for st in spec["stairs"]:
        sx, sy = st["start"]
        if not (x0 - 0.1 <= sx <= x1 + 0.1 and y0 - 0.1 <= sy <= y1 + 0.1):
            continue
        L = st["n"] * st["run"]
        spans.append((min(sx, sx + st["dir"][0] * L) - 1.0, max(sx, sx + st["dir"][0] * L) + 1.0))
    W = x1 - x0
    side_n = max(1, int(W / 7.0))
    VEST = 2.6
    shop_out = []
    for k in range(storeys):
        if k == 0 and ground == "hall":
            # the whole ground floor one hall: the corridor joins it
            cor = next(r for r in rooms if r["name"] == f"{pre}COR0")
            cor["open_plan_to"] = f"{pre}HALL"
            rooms.append(dict(name=f"{pre}HALL", floor=0, rect=(x0, c1, x1, y1), type="shop",
                              fitout=shopfit.fitout_for(hall_kind, rnd)))
            rooms.append(dict(name=f"{pre}BACK", floor=0, rect=(x0, y0, x1, c0), type="stock", open_plan_to=f"{pre}COR0",
                              fitout=shopfit.fitout_for("stockroom", rnd)))
            doors.append(dict(name=f"{pre}hall_main", floor=0, at=((x0 + x1) / 2, y1), w=2.4, h=2.6, ext=True, leaves=2,
                              glazed=(0.05, 0.05, 0.95, 0.95)))
            shop_out.append(dict(name=f"{pre}HALL", x0=x0, x1=x1, kind=hall_kind, door=(x0 + x1) / 2))
            continue
        for band in ("F", "R"):
            yc, ye = (c1, y1) if band == "F" else (c0, y0)
            sg = 1.0 if band == "F" else -1.0
            if k == 0 and band == "F":
                rooms.append(dict(name=f"{pre}VEST", floor=0, rect=(-VEST / 2 + (x0 + x1) / 2, c1, VEST / 2 + (x0 + x1) / 2, y1),
                                  type="hall", open_plan_to=f"{pre}COR0"))
                mid = (x0 + x1) / 2
                segs = [(x0, mid - VEST / 2), (mid + VEST / 2, x1)]
                if ground == "shops":
                    # a shop per ~6 m of front, each with its own street door, sign and fit-out
                    for si, (sa, sb) in enumerate(segs):
                        n = max(1, int((sb - sa) / 5.5))
                        bw = (sb - sa) / n
                        for i in range(n):
                            ax0, ax1 = sa + i * bw, sa + (i + 1) * bw
                            spec_s = shops[len(shop_out) % len(shops)] if shops else {"kind": "variety_store"}
                            nm = f"{pre}SHOP{len(shop_out)}"
                            rooms.append(dict(name=nm, floor=0, rect=(ax0, c1, ax1, y1), type="shop",
                                              fitout=shopfit.fitout_for(spec_s["kind"], rnd)))
                            doors.append(dict(name=f"d{nm}", floor=0, at=((ax0 + ax1) / 2, y1), w=1.2, h=2.4, ext=True,
                                              glazed=(0.05, 0.05, 0.95, 0.95), swing_into=nm))
                            shop_out.append(dict(name=nm, x0=ax0, x1=ax1, kind=spec_s["kind"], door=(ax0 + ax1) / 2))
                    continue
                n_seg = [max(1, side_n // 2), max(1, side_n - side_n // 2)]
            else:
                segs = [(x0, x1)]
                n_seg = [side_n]
            Dd = abs(ye - yc)
            ds = clamp(Dd * 0.34, 2.3, 2.8)
            dh = 1.15
            for si_, ((sa, sb), n) in enumerate(zip(segs, n_seg)):
                bw = (sb - sa) / n
                for i in range(n):
                    bx0, bx1 = sa + i * bw, sa + (i + 1) * bw
                    u = f"{pre}A{k}{band}{si_}{i}"

                    def yr(a, c):
                        return (yc + sg * a, yc + sg * c) if sg > 0 else (yc + sg * c, yc + sg * a)
                    sy0, sy1 = yr(0.0, ds)
                    hy0, hy1 = yr(ds, ds + dh)
                    wy0, wy1 = yr(ds + dh, Dd)
                    kw = clamp(bw * 0.58, 2.4, bw - 1.8)
                    k_left = True
                    if band == "R":
                        mid_l, mid_r = bx0 + kw / 2, bx1 - kw / 2
                        if any(a_ < mid_l < b_ for a_, b_ in spans) and not any(a_ < mid_r < b_ for a_, b_ in spans):
                            k_left = False
                    kx = (bx0, bx0 + kw) if k_left else (bx1 - kw, bx1)
                    tx = (bx0 + kw, bx1) if k_left else (bx0, bx1 - kw)
                    nb = 1 if bw < 7.5 else 2
                    lw = max(3.4, bw * (0.45 if nb > 1 else 0.55))
                    while nb > 1 and (bw - lw) / nb < 2.7:
                        nb -= 1
                    rooms += [dict(name=f"{u}KIT", unit=u, floor=k, rect=(kx[0], sy0, kx[1], sy1), type="kitchen", floor_mat="lino"),
                              dict(name=f"{u}BATH", unit=u, floor=k, rect=(tx[0], sy0, tx[1], sy1), type="bath", floor_mat="hextile"),
                              dict(name=f"{u}HALL", unit=u, floor=k, rect=(bx0, hy0, bx1, hy1), type="hall"),
                              dict(name=f"{u}LR", unit=u, floor=k, rect=(bx0, wy0, bx0 + lw, wy1), type="living")]
                    bwid = (bw - lw) / nb
                    for j in range(nb):
                        rooms.append(dict(name=f"{u}BR{j + 1}", unit=u, floor=k, rect=(bx0 + lw + j * bwid, wy0, bx0 + lw + (j + 1) * bwid, wy1),
                                          type="bed"))
                    ex = (kx[0] + kx[1]) / 2
                    if band == "R" and any(a_ < ex < b_ for a_, b_ in spans):
                        ex = kx[1] - 0.7 if k_left else kx[0] + 0.7
                    e_hall, e_win = (hy0 if sg > 0 else hy1), (hy1 if sg > 0 else hy0)
                    doors += [dict(name=f"{u}entry", floor=k, at=(ex, yc), w=0.9, swing_into=f"{u}KIT", locked=True),
                              dict(name=f"{u}kit", floor=k, at=((kx[0] + kx[1]) / 2, e_hall), w=0.9, cased=True),
                              dict(name=f"{u}bath", floor=k, at=((tx[0] + tx[1]) / 2, e_hall), w=0.75, swing_into=f"{u}BATH"),
                              dict(name=f"{u}lr", floor=k, at=(bx0 + lw / 2, e_win), w=0.9, cased=True)]
                    for j in range(nb):
                        doors.append(dict(name=f"{u}br{j + 1}", floor=k, at=(bx0 + lw + (j + 0.5) * bwid, e_win), w=0.8,
                                          swing_into=f"{u}BR{j + 1}"))
    if ground != "hall":
        doors.append(dict(name=f"{pre}main", at=((x0 + x1) / 2, y1), w=1.8, h=2.4, ext=True, leaves=2, glazed=(0.05, 0.05, 0.95, 0.95)))
    return shop_out


def tower_plan(spec, bl, rnd, pre, ground, shops, hall_kind, west_free):
    """a dogleg stair against the rear wall, a stair hall on every floor, and one home a floor in front of it (the
    ground floor: a shop or a home, entered from the street; the stair hall from the side street door)"""
    x0, y0, x1, y1 = bl["rect"]
    floors = bl["floors"]
    storeys = len(floors)
    rooms, doors = spec["rooms"], spec["doors"]
    W, D = x1 - x0, y1 - y0
    sx = x0 + TE + 0.95
    yb = y0 + 2.95                        # the rear strip's front edge
    n_max = max([math.ceil((floors[k][0] - floors[k - 1][0]) / 0.18) for k in range(1, storeys)] or [18])
    hall_x1 = sx + ((n_max + 1) // 2) * 0.26 + 1.0 + 0.3      # the dogleg's two flights and its half landing
    for k in range(1, storeys):
        rise = floors[k][0] - floors[k - 1][0]
        n = math.ceil(rise / 0.18)
        spec["stairs"].append(dict(type="dogleg", start=(sx, y0 + TE + 0.05), dir=(1, 0), width=STAIR_W, n=n, run=0.26,
                                   floor=k - 1, to_floor=k, turn="left", landing=1.0))
    shop_out = []
    xm = x0 + max(hall_x1 - x0, W * 0.55)
    for k in range(storeys):
        rooms.append(dict(name=f"{pre}SH{k}", floor=k, rect=(x0, y0, hall_x1, yb), type="hall", no_furnish=True))
        if k == 0 and ground in ("shops", "hall"):
            spec_s = shops[0] if shops else {"kind": hall_kind}
            kind = hall_kind if ground == "hall" else spec_s["kind"]
            nm = f"{pre}SHOP0"
            rooms.append(dict(name=nm, floor=0, rect=(x0, yb, x1, y1), type="shop", fitout=shopfit.fitout_for(kind, rnd)))
            rooms.append(dict(name=f"{pre}STOCK", floor=0, rect=(hall_x1, y0, x1, yb), type="stock",
                              fitout=shopfit.fitout_for("stockroom", rnd)))
            doors.append(dict(name=f"d{nm}", floor=0, at=((x0 + x1) / 2, y1), w=1.4, h=2.4, ext=True, glazed=(0.05, 0.05, 0.95, 0.95),
                              swing_into=nm))
            doors.append(dict(name=f"{pre}stock", floor=0, at=((hall_x1 + x1) / 2, yb), w=0.9, swing_into=f"{pre}STOCK"))
            shop_out.append(dict(name=nm, x0=x0, x1=x1, kind=kind, door=(x0 + x1) / 2))
            continue
        u = f"{pre}T{k}"
        rooms.append(dict(name=f"{u}LR", unit=u, floor=k, rect=(x0, yb, xm, y1), type="living"))
        rooms.append(dict(name=f"{u}BR1", unit=u, floor=k, rect=(xm, yb, x1, y1), type="bed"))
        if x1 - hall_x1 >= 5.0:
            kx = hall_x1 + (x1 - hall_x1) * 0.55
            rooms.append(dict(name=f"{u}KIT", unit=u, floor=k, rect=(hall_x1, y0, kx, yb), type="kitchen", floor_mat="lino"))
            rooms.append(dict(name=f"{u}BATH", unit=u, floor=k, rect=(kx, y0, x1, yb), type="bath", floor_mat="hextile"))
            kd_x = (hall_x1 + min(kx, xm)) / 2 if xm > hall_x1 + 1.0 else None
            if kd_x is not None:
                doors.append(dict(name=f"{u}kit", floor=k, at=(kd_x, yb), w=0.9, cased=True))
            else:
                doors.append(dict(name=f"{u}kit", floor=k, at=((max(hall_x1, xm) + kx) / 2, yb), w=0.9, cased=True))
            doors.append(dict(name=f"{u}bath", floor=k, at=(kx, (y0 + yb) / 2), w=0.75, swing_into=f"{u}BATH"))
        else:
            rooms.append(dict(name=f"{u}BATH", unit=u, floor=k, rect=(hall_x1, y0, x1, yb), type="bath", floor_mat="hextile"))
            doors.append(dict(name=f"{u}bath", floor=k, at=((max(hall_x1, xm) + x1) / 2, yb), w=0.75, swing_into=f"{u}BATH"))
        doors.append(dict(name=f"{u}entry", floor=k, at=(x0 + 0.7, yb), w=0.9, swing_into=f"{u}LR", locked=True))
        doors.append(dict(name=f"{u}br", floor=k, at=(xm, (yb + y1) / 2), w=0.85, swing_into=f"{u}BR1"))
    # the street door into the stair hall: on the block's west side, or (another block against it) the rear
    if west_free:
        doors.append(dict(name=f"{pre}hall_door", floor=0, at=(x0, y0 + 1.95), w=1.0, ext=True))
    else:
        doors.append(dict(name=f"{pre}hall_door", floor=0, at=(x0 + 0.62, y0), w=0.85, ext=True))
    return shop_out


# ------------------------------------------------------------------ windows (and where they are, for the dressing)
SIDES = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}


def _edge(rect, side):
    x0, y0, x1, y1 = rect
    return {"S": ((x0, y0), (x1, y0)), "N": ((x1, y1), (x0, y1)), "E": ((x1, y0), (x1, y1)), "W": ((x0, y1), (x0, y0))}[side]


def _covered(blocks, bl, side, p, z):
    """is the wall at p (a point on bl's side), height z, against another block standing that high?"""
    for ob in blocks:
        if ob is bl:
            continue
        ox0, oy0, ox1, oy1 = ob["rect"]
        if z > ob["wall_top"]:
            continue
        if side in "NS" and abs(p[1] - (oy0 if side == "N" else oy1)) < 0.05 and ox0 - 0.3 < p[0] < ox1 + 0.3:
            return True
        if side in "EW" and abs(p[0] - (ox0 if side == "E" else ox1)) < 0.05 and oy0 - 0.3 < p[1] < oy1 + 0.3:
            return True
    return False


def add_windows(spec, blocks, wp, shops_by_block, avoid):
    """windows on every free wall: wp = {w, h, sill, spacing}; storefronts get wide shop windows.  Returns where each
    window is: [dict(block, side, floor, x, y, z (centre), w, h, out (dx, dy))]"""
    out = []
    for bl in blocks:
        for k, (fz, cz) in enumerate(bl["floors"]):
            for side, (dx, dy) in SIDES.items():
                a, c = _edge(bl["rect"], side)
                L = math.dist(a, c)
                shops = shops_by_block.get(bl["name"], []) if (k == 0 and side == "N") else []
                if shops:
                    for s in shops:
                        for xw in ((s["x0"] + s["door"]) / 2 - 0.3, (s["door"] + s["x1"]) / 2 + 0.3):
                            ww = min(2.6, abs(s["door"] - (s["x0"] if xw < s["door"] else s["x1"])) - 1.6)
                            if ww < 0.9:
                                continue
                            p = (xw, a[1])
                            spec["windows"].append(dict(at=p, floor=0, w=ww, sill=0.45, h=min(2.0, cz - fz - 0.7), kind="fixed",
                                                        cols=max(1, int(ww / 0.9)), head_cap=True))
                            out.append(dict(block=bl, side=side, floor=0, x=p[0], y=p[1], z=fz + 0.45 + 1.0, w=ww, h=2.0, out=(dx, dy), shop=True))
                    continue
                n = max(1, int((L - 1.6) / wp["spacing"]))
                for j in range(n):
                    t = (j + 0.5) / n
                    p = (a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
                    h = min(wp["h"], cz - fz - wp["sill"] - 0.3)
                    zc = fz + wp["sill"] + h / 2
                    if _covered(blocks, bl, side, p, zc + h / 2 + 0.3):
                        continue
                    if any(math.dist(p, q) < 1.6 for (q, fk) in avoid if fk == k):
                        continue
                    spec["windows"].append(dict(at=p, floor=k, w=wp["w"], sill=wp["sill"], h=h, kind="dh", cols=2, head_cap=True))
                    out.append(dict(block=bl, side=side, floor=k, x=p[0], y=p[1], z=zc, w=wp["w"], h=h, out=(dx, dy), shop=False))
    return out


def _yaw(out):
    """kit yaw (degrees) for a component facing out (dx, dy): 0 faces +y"""
    return round(math.degrees(math.atan2(-out[0], out[1])))


# ------------------------------------------------------------------ the build
def build(rec):
    rid, tr = rec["id"], rec.get("traits", {}) or {}
    st = styles()[tr["style"]]
    rnd = rng(rid)
    b = lib_building(rid)
    style_materials(b, st, tr)
    if os.environ.get("SSC_KIT", "1") != "0":
        K.install()
    sh = float(tr.get("storey_h", 3.2))
    blocks = []
    for i, bd in enumerate(tr["blocks"]):
        floors = _floors(int(bd["storeys"]), sh)
        pitched = i > 0 and _pitched(st) is not None
        bl = dict(name=bd.get("name", f"B{i}"), rect=tuple(bd["rect"]), floors=floors, wall_top=floors[-1][1] + 0.35,
                  found_top=0.25, roof=_flat_roof(1.2 if i == 0 else (0.15 if pitched else 0.9)),
                  ext=("ext", "ext2", "ext3")[bd.get("ext", 0) % 3], pitched=pitched)
        bl["_bd"] = bd
        blocks.append(bl)
    spec = _spec(blocks)
    shops = tr.get("shops", [])
    shops_by_block = {}
    for i, bl in enumerate(blocks):
        bd = bl.pop("_bd")
        pre = f"B{i}"
        x0, y0, x1, y1 = bl["rect"]
        plan = bd.get("plan", "slab")
        ground = bd.get("ground", "dwelling")
        if plan == "tower" or (x1 - x0) < 12.0 or (y1 - y0) < 12.5:     # (a slab needs two bands of flats and a corridor)
            west_free = not any(abs(ob["rect"][2] - x0) < 0.05 and ob["rect"][1] < y0 + 3.0 and ob["rect"][3] > y0 + 1.0
                                for ob in blocks if ob is not bl)
            so = tower_plan(spec, bl, rnd, pre, ground, shops, bd.get("hall_kind", "grocery"), west_free)
        else:
            so = slab_plan(spec, bl, rnd, pre, ground, shops, bd.get("hall_kind", "grocery"))
        shops_by_block[bl["name"]] = so
    avoid = [(d["at"], d.get("floor", 0)) for d in spec["doors"]]
    wins = add_windows(spec, blocks, tr.get("window", dict(w=1.0, h=1.5, sill=0.9, spacing=2.4)), shops_by_block, avoid)
    inst.add_stoops(spec, blocks[0]["floors"][0][0], skip=tuple(d["name"] for d in spec["doors"] if d.get("ext")))
    gh.House(b, spec).build()
    main = blocks[0]
    x0, y0, x1, y1 = main["rect"]
    # roof access: the fire escape up the main block's +x wall, from the street to a platform over the parapet
    import roofaccess
    roofaccess.fire_escape(b, "x", x1, 1, y0 + 0.6, y1 - 0.6, [f[0] for f in main["floors"][1:]], main["wall_top"],
                           main["roof"]["parapet"], TE)
    anchors = []
    if os.environ.get("SKY_DRESS", "v2") == "v1":
        dress(b, tr, st, blocks, wins, shops_by_block, anchors, rnd)
        ceilings(b, tr, spec, blocks)
    else:
        import sky_dress2 as D2
        D2.dress(b, tr, st, blocks, wins, shops_by_block, anchors, rnd)
        D2.ceilings(b, tr, st, spec, blocks)
    homes = len({r["unit"] for r in spec["rooms"] if r.get("unit")})
    _write_anchors(rid, tr, blocks, anchors, shops_by_block, getattr(b, "sky_pad", None), homes)
    return b


def _godot(x, y, z, out=None):
    yaw = math.atan2(out[0], -out[1]) if out else 0.0
    return [round(x, 2), round(z, 2), round(-y, 2), round(yaw, 4)]


def _write_anchors(rid, tr, blocks, anchors, shops_by_block, pad=None, homes=0):
    os.makedirs(ANCHOR_DIR, exist_ok=True)
    main = blocks[0]
    xs = [v for bl in blocks for v in (bl["rect"][0], bl["rect"][2])]
    ys = [v for bl in blocks for v in (bl["rect"][1], bl["rect"][3])]
    shops = [dict(name=s["name"], kind=s["kind"], x=round((s["x0"] + s["x1"]) / 2, 2)) for so in shops_by_block.values() for s in so]
    with open(os.path.join(ANCHOR_DIR, rid + ".json"), "w") as f:
        json.dump({"id": rid, "style": tr["style"], "anchors": anchors, "roof": round(main["wall_top"], 2),
                   "h": round(max(bl["wall_top"] for bl in blocks) + 1.2, 2),
                   "bbox": [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)],
                   "shops": shops, "storeys": len(main["floors"]), "homes": homes,
                   "pad": _godot(*pad)[:3] if pad else None,
                   "blocks": [[*[round(v, 2) for v in bl["rect"]], round(bl["wall_top"], 2), len(bl["floors"])] for bl in blocks]},
                  f, separators=(",", ":"))


# ------------------------------------------------------------------ the style's dressing
def dress(b, tr, st, blocks, wins, shops_by_block, anchors, rnd):
    dz = set(tr.get("dress", []))
    var = tr.get("variants", {})
    sg = tr.get("signage", {"kinds": ["lightbox"], "density": 0.5})
    dens = float(sg.get("density", 0.5))
    kinds = sg.get("kinds") or ["lightbox"]
    # (part names follow gblod's rules: "trim*" survives at LOD1 as the hulls of its pieces -- a cage as a box --, "windows*"
    # is gone past full detail; the roof's bigger pieces stand in "sky_roof-col" as built)
    deco = b.part("trim_sky-col")                 # bays, cages, balconies, galleries, bands, crenels, fronts: solid
    fine = b.part("windows_sky")                  # shutters, screens, hoods, planters, AC units, laundry: small
    b.sky_roof = b.part("sky_roof-col")           # domes, towers, chhatris, shacks, tanks, pergolas, eaves
    main = blocks[0]
    # ---- at the windows (upper floors; front first)
    for wi, w in enumerate(wins):
        if w["shop"]:
            continue
        yaw = _yaw(w["out"])
        pos = (w["x"] + w["out"][0] * 0.0, w["y"] + w["out"][1] * 0.0, w["z"])
        front = w["side"] == "N"
        upper = w["floor"] >= 1
        roll = (hash((tr["style"], round(w["x"], 1), round(w["y"], 1), w["floor"])) % 1000) / 1000.0
        ww, hh = K.q(w["w"]), K.q(w["h"])
        if "bay" in dz and upper and (front or w["side"] in var.get("bay_sides", "N")) and roll < var.get("bay_share", 0.5):
            K.bay(deco, pos, yaw, ww, hh, depth=var.get("bay_depth", 0.7), kind=var.get("bay", "glass"),
                  roof=var.get("bay_roof", "flat"), mat=main["ext"])
            continue
        if "cage" in dz and upper and roll < var.get("cage_share", 0.6):
            K.cage(deco, pos, yaw, ww, hh)
            if "ac" in dz and roll < 0.35:
                K.ac_unit(fine, (pos[0] + w["out"][0] * 0.0, pos[1], pos[2] - hh / 2 - 0.9), yaw)
            continue
        if "balcony" in dz and upper and front and roll < var.get("balcony_share", 0.45):
            fz = w["z"] - hh / 2 - tr.get("window", {}).get("sill", 0.9)
            K.balcony(deco, (pos[0], pos[1], fz + 0.15), yaw, K.q(ww + 1.2), depth=var.get("balcony_depth", 1.0),
                      rail=var.get("balcony_rail", "iron"))
        if "screen" in dz and roll < var.get("screen_share", 0.5):
            K.screen(fine, pos, yaw, ww, hh)
        elif "shutters" in dz:
            K.shutters(fine, pos, yaw, ww, hh)
        if "arch" in dz:
            K.arch_hood(fine, (pos[0], pos[1], pos[2] + hh / 2), yaw, ww, kind=var.get("arch", "round"))
        elif "eyebrow" in dz:
            K.eyebrow(fine, (pos[0], pos[1], pos[2] + hh / 2 + 0.12), yaw, ww)
        if "planter" in dz and front and roll > 0.7:
            K.planter(fine, (pos[0], pos[1], pos[2] - hh / 2 - 0.02), yaw, K.q(ww + 0.2))
        if "ac" in dz and not front and roll > 0.65:
            K.ac_unit(fine, (pos[0] + (0.9 if w["out"][1] else 0.0), pos[1] + (0.9 if w["out"][0] else 0.0), pos[2] - hh / 2 - 0.7), yaw)
    # ---- shops: awnings, signs
    sign_n = 0
    for bl in blocks:
        for s in shops_by_block.get(bl["name"], []):
            y1 = bl["rect"][3]
            fz, cz = bl["floors"][0]
            sw = K.q(min(s["x1"] - s["x0"] - 0.8, 7.0))
            if "awnings" in dz:
                K.awning(fine, ((s["x0"] + s["x1"]) / 2, y1, fz + 2.55), 0, K.q(s["x1"] - s["x0"] - 0.4), depth=1.4)
            kind = kinds[sign_n % len(kinds)]
            anchors.append([f"sign_{kind}_{sw}x1.1"] + _godot((s["x0"] + s["x1"]) / 2, y1 + 0.08, fz + 3.0, (0, 1)))
            sign_n += 1
    # ---- along the walls
    for bl in blocks:
        x0, y0, x1, y1 = bl["rect"]
        floors = bl["floors"]
        for side, out in SIDES.items():
            a, c = _edge(bl["rect"], side)
            L = K.q(math.dist(a, c))
            yaw = _yaw(out)
            # a run's start: the end its +x (the kit frame's u, along the wall) runs from
            ux, uy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            if (c[0] - a[0]) * ux + (c[1] - a[1]) * uy < 0:
                a, c = c, a
            for k, (fz, cz) in enumerate(floors):
                if k == 0:
                    continue
                z = fz - 0.2
                if _covered(blocks, bl, side, ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2), z + 0.5):
                    continue
                if "bands" in dz:
                    K.band(fine, (a[0], a[1], z), yaw, L, h=var.get("band_h", 0.25), depth=0.06,
                           mat=var.get("band_mat", "trim") if k % 2 or not var.get("ablaq") else "accent")
                if "jetty" in dz and side == "N":
                    K.band(deco, (a[0], a[1], z), yaw, L, h=0.35, depth=0.45, mat="wood")
                    K.corbels(fine, (a[0], a[1], z), yaw, L, step=1.4, mat="wood")
                if "gallery" in dz and side == var.get("gallery_side", "N") and bl is main:
                    K.gallery(deco, (a[0], a[1], fz), yaw, L, depth=1.3, rail=var.get("balcony_rail", "iron"))
            top = bl["wall_top"]
            par = bl["roof"]["parapet"]
            if "beam_ends" in dz:
                K.beam_ends(fine, (a[0], a[1], top - 0.4), yaw, L)
            if "crenel" in dz and not _covered(blocks, bl, side, ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2), top + 1.0):
                K.crenels(deco, (a[0], a[1], top + par), yaw, L, kind=var.get("crenel", "square"), mat=bl["ext"])
            if "parapet_screen" in dz and not _covered(blocks, bl, side, ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2), top + 1.0):
                K.parapet_screen(fine, (a[0], a[1], top + par), yaw, L)
            if bl is main and side == "N":
                if "false_front" in dz:
                    K.false_front(deco, (a[0], a[1] + 0.0, top + par), yaw, L, h=K.q(clamp(L * 0.25, 1.8, 3.4)), mat=main["ext"])
                elif "gable_front" in dz:
                    K.gable_front(deco, (a[0], a[1], top + par), yaw, L, kind=var.get("gable", "step"), h=K.q(min(L * 0.6, 7.0)),
                                  mat=main["ext"])
            # glow: a floor line on the front of every block, the crown on top
            if side == "N":
                for k, (fz, cz) in enumerate(floors):
                    if k and (k % max(1, int(3 - dens * 2)) == 0):
                        anchors.append([f"glow_floor_{L}"] + _godot(x1, y1 + 0.1, fz - 0.15, (0, 1)))
                anchors.append([f"glow_crown_{L}"] + _godot(x1, y1 + 0.1, top + par + 0.05, (0, 1)))
    # ---- signs on the facade: blades at the front corners, boards between upper windows, a rooftop billboard
    H = main["wall_top"]
    x0, y0, x1, y1 = main["rect"]
    nst = len(main["floors"])
    if nst >= 3 and dens >= 0.35:
        bh = K.q(min(nst * 1.4, 9.0))
        for s_, xs in enumerate((x0 + 0.5, x1 - 0.5)):
            if s_ == 1 and dens < 0.6:
                break
            anchors.append([f"sign_blade_1.0x{bh}"] + _godot(xs, y1 + 0.9, 3.4, (1 if s_ else -1, 0)))
    nb = int(dens * len([w for w in wins if w["side"] == "N" and w["floor"] >= 1 and w["block"] is main]) * 0.35)
    upper = [w for w in wins if w["side"] == "N" and w["floor"] >= 1 and w["block"] is main]
    rnd2 = random.Random(hash(tr["style"]) ^ len(wins))
    for w in rnd2.sample(upper, min(nb, len(upper))):
        kind = kinds[rnd2.randrange(len(kinds))]
        anchors.append([f"sign_{kind}_1.6x0.7"] + _godot(w["x"], w["y"] + 0.12, w["z"] + w["h"] / 2 + 0.55, (0, 1)))
    if "billboard" in dz or (dens >= 0.7 and nst >= 5):
        bw = K.q(min(x1 - x0 - 2.0, 10.0))
        anchors.append([f"sign_billboard_{bw}x{K.q(bw * 0.4)}"] + _godot((x0 + x1) / 2 - 2.0, y0 + 3.0, H + 1.5, (0, 1)))
    # string lights: across the front at the parapet, and from the front corners down to the street lamps' height
    n = 0
    anchors.append([f"lights_{n}"] + _godot(x0 + 0.3, y1 + 0.2, H + 1.1, (0, 1)))
    anchors.append([f"lights_{n}"] + _godot(x1 - 0.3, y1 + 0.2, H + 1.1, (0, 1)))
    n += 1
    if "lanterns" in dz or dens > 0.5:
        for k, (fz, cz) in enumerate(main["floors"][1:], start=1):
            if k % 2:
                anchors.append([f"lights_{n}"] + _godot(x0 + 0.2, y1 + 0.5, fz + 2.4, (0, 1)))
                anchors.append([f"lights_{n}"] + _godot(x1 - 0.2, y1 + 0.5, fz + 2.4, (0, 1)))
                n += 1
    # ---- the roof (clear of the escape's platform on +x and the middle of a big roof: the lark cradles)
    roof(b, tr, st, blocks, dz, var, b.sky_roof, fine, rnd)


def roof(b, tr, st, blocks, dz, var, deco, fine, rnd):
    main = blocks[0]
    for bi, bl in enumerate(blocks):
        x0, y0, x1, y1 = bl["rect"]
        z = bl["wall_top"]
        W, D = x1 - x0, y1 - y0
        big = W >= 14 and D >= 14
        corners = [(x0 + 2.0, y0 + 2.0), (x0 + 2.0, y1 - 2.0), (x1 - 3.0, y1 - 2.0), (x1 - 3.0, y0 + 2.0)]
        if bl is main:
            corners = corners[:2]                    # (+x: the fire escape's platform)
        r = random.Random(f"{tr['style']}:{bi}:{W:.1f}:{D:.1f}")
        # a big main roof stays clear: a lark's cradle (the canon: larks sit on the islands' tallest roofs)
        if bl is main and W >= 15.0 and D >= 15.0 and not ("dome" in dz and len(blocks) == 1) and "eaves" not in dz:
            b.sky_pad = ((x0 + x1) / 2 - 2.0, (y0 + y1) / 2, z)
            continue
        if "eaves" in dz and bl is main:
            K.eave_stack(deco, ((x0 + x1) / 2, (y0 + y1) / 2, z + 1.25), 0, K.q(W - 1.0), K.q(D - 1.0),
                         tiers=var.get("eave_tiers", 2))
            continue
        if "corner_towers" in dz and bi == 0:
            for (cx, cy) in ((x0 + 1.4, y0 + 1.4), (x0 + 1.4, y1 - 1.4), (x1 - 1.4, y1 - 1.4)):
                K.tapered_tower(deco, (cx, cy, z), 0, r=1.6, h=K.q(3.0 + len(bl["floors"]) * 0.4), mat=bl["ext"])
        if "dome" in dz and bi == len(blocks) - 1 and W >= 6:
            K.dome(deco, ((x0 + x1) / 2, (y0 + y1) / 2, z), 0, r=K.q(min(W, D) * 0.3), onion=var.get("onion", False))
            continue
        if "tower" in dz and bl is main:
            cx, cy = corners[1]
            K.tower(deco, (cx, cy, z), 0, r=1.4, h=K.q(4.0 + len(bl["floors"]) * 0.3), cap=var.get("tower_cap", "dome"),
                    round_=var.get("tower_round", False), mat=bl["ext"])
            corners = corners[:1]
        if "chhatri" in dz:
            for (cx, cy) in corners[:2]:
                K.chhatri(deco, (cx, cy, z), 0, r=1.1)
            corners = []
        stuff = [t for t in ("shacks", "tanks", "antennas", "laundry", "pergola", "chimneys") if t in dz]
        for t in stuff:
            if not corners:
                break
            cx, cy = corners.pop(r.randrange(len(corners)))
            if t == "shacks":
                K.shack(deco, (cx + 0.5, cy, z), r.choice((0, 90)), w=3.0, d=2.6, h=2.4, kind=var.get("shack", "shack"))
            elif t == "tanks":
                K.tank(fine, (cx, cy, z), 0, r=0.8, h=1.6)
            elif t == "antennas":
                K.antenna(fine, (cx, cy, z), 0, h=4.0)
            elif t == "laundry":
                K.laundry(fine, (cx - 1.5, cy, z), 0, L=3.6)
            elif t == "pergola":
                K.pergola(deco, (cx + 0.5, cy, z), 0, w=3.6, d=3.0, h=2.5)
            elif t == "chimneys":
                K.chimney(deco, (cx, cy, z), 0, w=0.8, h=2.0, kind=var.get("chimney", "stack"))


def ceilings(b, tr, spec, blocks):
    """THE CEILING TILES in the shops and halls (sky_kit.ceiling_tiles): a module per 1.2 m, under the ceiling"""
    variant = tr.get("variants", {}).get("ceiling", "grid")
    p = b.part("fit_sky_ceiling")                 # (an interior fitting: never past full detail)
    for r in spec["rooms"]:
        if r.get("type") not in ("shop",) or r.get("floor", 0) != 0:
            continue
        x0, y0, x1, y1 = r["rect"]
        bl = next((bl for bl in blocks if bl["rect"][0] - 0.05 <= (x0 + x1) / 2 <= bl["rect"][2] + 0.05
                   and bl["rect"][1] - 0.05 <= (y0 + y1) / 2 <= bl["rect"][3] + 0.05), blocks[0])
        cz = bl["floors"][0][1] - 0.05
        nx, ny = int((x1 - x0 - 0.4) / 1.2), int((y1 - y0 - 0.4) / 1.2)
        ox = (x0 + x1) / 2 - nx * 0.6 + 0.6
        oy = (y0 + y1) / 2 - ny * 0.6 + 0.6
        for i in range(nx):
            for j in range(ny):
                K.ceiling_tiles(p, (round(ox + i * 1.2, 3), round(oy + j * 1.2, 3), cz), 0, variant=variant)
