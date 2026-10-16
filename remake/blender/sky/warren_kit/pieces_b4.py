"""pieces_b4.py -- warren kit batch 4a: the generator's requests (research/sky_islands/warrens/kit_requests.md).

Shared first (skirted paving, a cheaper rounded parapet, gable-segment roofs every family can use), the two missing
palettes (latin_hillside, nouvelle_france), then the families' lists: yemeni_tower, japan_yokocho, hanseatic_gable,
chongqing_cliff, andean_neo.  Ordinary pieces keep to 30-300 tris; towers and marks to 400-900.
"""
import math
import random

import shapely
from shapely.geometry import Polygon

from geom import Mesh, _dedupe, rot_y
from pieces import BAY, BOTH, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall, pave
from pieces_marks import _beads, _chochin, _corbel, _diag, _hip, _lightbox, _off, _place, _ring


# ------------------------------------------------------------------ helpers
def _flat_prism(m, poly, z0, z1, slot, shade=1.0, open_edges=()):
    """a polygon (x-y) extruded z0..z1 with its sides, leaving out the sides along open_edges (indices: edges that
    sit on a roof or butt a neighbour) -- the cheap way to cut a silhouette"""
    poly = _dedupe(poly)
    for t in shapely.constrained_delaunay_triangles(Polygon(poly)).geoms:
        c = list(t.exterior.coords)[:3]
        m.tri_facing(*[(p[0], p[1], z1) for p in c], (0, 0, 1), slot, shade)
        m.tri_facing(*[(p[0], p[1], z0) for p in c], (0, 0, -1), slot, shade * 0.9)
    area = sum(poly[k][0] * poly[(k + 1) % len(poly)][1] - poly[(k + 1) % len(poly)][0] * poly[k][1] for k in range(len(poly)))
    for k in range(len(poly)):
        if k in open_edges:
            continue
        (ax, ay), (bx, by) = poly[k], poly[(k + 1) % len(poly)]
        en = (by - ay, -(bx - ax), 0) if area > 0 else (-(by - ay), bx - ax, 0)
        m.quad_facing((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1), en, slot, shade)


def _gable_seg(pitch, eave=0.45, ribs=7, end=False, rib_slot="roof", seam=0.06, ridge=True, wall_slot="wall"):
    """a gable roof SEGMENT over one cell, its ridge along Z (it tiles along Z into a run of any length): two slopes
    with eaves overhanging the walls by eave, tile ribs (or tin seams) down each slope, a ridge, the soffit; end:
    close the -Z end with a gable triangle"""
    m = Mesh()
    tn = math.tan(math.radians(pitch))
    h = HB * tn
    lx, ly = HB + eave, -eave * tn
    for s in (-1, 1):
        a, b = (s * lx, ly, -HB), (s * lx, ly, HB)
        c, d = (0.0, h, HB), (0.0, h, -HB)
        m.quad_facing(a, b, c, d, (s * tn, 1, 0), "roof")
        m.quad_facing((s * lx, ly - 0.06, -HB), (s * lx, ly - 0.06, HB), (s * HB, -0.02, HB), (s * HB, -0.02, -HB), (0, -1, 0), "frame", 0.55)
        m.quad_facing((s * lx, ly - 0.06, -HB), (s * lx, ly - 0.06, HB), (s * lx, ly, HB), (s * lx, ly, -HB), (s, 0, 0), "frame", 0.7)
        nl = math.hypot(tn, 1.0)
        off = (s * tn / nl * 0.03, 1.0 / nl * 0.03)               # 3 cm off the slope, along its normal
        for k in range(ribs):                                     # ribs / seams down the slope
            z = -HB + BAY * (k + 0.5) / ribs
            xa, xb = s * (lx - 0.02), s * 0.08
            ya, yb = ly + 0.02 * tn, h - 0.08 * tn
            _strip(m, (xa + off[0], ya + off[1], z), (xb + off[0], yb + off[1], z), seam, (s * tn, 1, 0), rib_slot)
    if ridge:
        m.box((-0.1, h - 0.04, -HB), (0.1, h + 0.1, HB), "roof", 0.8, skip=("y-", "z-", "z+"))
    if end:
        _flat_prism(m, [(-HB + 0.05, 0.0), (HB - 0.05, 0.0), (0.0, h - 0.07)], -HB, -HB + 0.25, wall_slot, open_edges=(0,))   # (tucked under the slopes)
    return m, h


def _rng(seed):
    return random.Random(seed)


# ------------------------------------------------------------------ shared
def pave_skirt(top=0.0):
    """a 0.6 m skirt down the four sides of a cell's deck (on sloping streets the step between two cells shows it, not
    the sky): 8 tris; or use the pave_*_skirt pieces"""
    def b():
        m = Mesh()
        for k in range(4):
            sub = Mesh()
            sub.quad_facing((-HB, -0.6, HB - 0.03), (HB, -0.6, HB - 0.03), (HB, top, HB - 0.03), (-HB, top, HB - 0.03), (0, 0, 1), "ground", 0.62)   # (3 cm in: off kerbs' faces)
            _place(m, sub, 90 * k)
        return m
    return b


def pave_with_skirt(kind):
    def b():
        m = pave(kind)() if kind != "garden" else PIECES["pave_garden"]["build"]()
        m.add(pave_skirt(-0.12 if kind == "garden" else 0.0)())
        return m
    return b


def edge_parapet_rounded_cheap():
    """the soft white Shibam merlons at ~54 tris: one silhouette (a band and three rounded humps meeting in valleys)
    cut flat, its sides except the bottom"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.55)]
        for x in (1.0, 0.0, -1.0):
            p += [(x + 0.36, 0.8), (x, 0.93), (x - 0.36, 0.8), (x - 0.5, 0.55)]
        _flat_prism(m, p, -K * 0.6, 0.0, "trim", open_edges=(0,))
        return m
    return b


# ------------------------------------------------------------------ roofs (cell; the ridge along Z, tile into runs)
def roof_seg(pitch, eave, ribs, slot="roof", seam=0.06, end=False, dormer=False):
    def b():
        m, h = _gable_seg(pitch, eave, ribs, end=end, rib_slot=slot, seam=seam)
        if dormer:                                                  # a dormer on each slope, its window facing out
            tn = math.tan(math.radians(pitch))
            for s in (-1, 1):
                xf = 0.75
                yb = h - xf * tn
                sub = Mesh()                                        # built facing +Z, turned to face s*X
                sub.wall_cut(_rect(-0.4, 0.0, 0.4, 0.95), [_rect(-0.22, 0.2, 0.22, 0.8)], -0.08, 0.0, "trim", reveal_slot="frame")
                sub.pane(-0.22, 0.2, 0.22, 0.8, -0.05)
                sub.box((-0.39, 0.0, -0.75), (-0.35, 0.95, -0.075), "roof", 0.8, skip=("y-",))
                sub.box((0.35, 0.0, -0.75), (0.39, 0.95, -0.075), "roof", 0.8, skip=("y-",))
                sub.quad_facing((-0.5, 0.92, 0.08), (0.0, 1.3, 0.08), (0.0, 1.3, -0.8), (-0.5, 0.92, -0.8), (-1, 1, 0), "roof")
                sub.quad_facing((0.5, 0.92, 0.08), (0.0, 1.3, 0.08), (0.0, 1.3, -0.8), (0.5, 0.92, -0.8), (1, 1, 0), "roof")
                sub.tri_facing((-0.36, 0.96, -0.03), (0.36, 0.96, -0.03), (0.0, 1.26, -0.03), (0, 0, 1), "trim")
                _place(m, sub, 90 * s, dx=s * xf, dy=yb - 0.05)
        return m
    return b


def roof_tile_flying_eave():
    """grey tile roof over a cell, shallow, its four corners swept up (Chongqing / Bashu flying eaves), a ridge"""
    def b():
        m = Mesh()
        _hip(m, HB + 0.7, 0.6, 0.0, 1.0, lift=0.45, flare=0.3, body=HB, cap=False)
        m.box((-0.7, 0.95, -0.08), (0.7, 1.12, 0.08), "roof", 0.8, skip=("y-",))
        for x in (-0.7, 0.7):
            m.cyl(x, 0.0, 0.05, 1.05, 1.35, "roof", n=4, r1=0.0)
        return m
    return b


# ------------------------------------------------------------------ Yemen
def wall_door_carved():
    """the heavy carved door (1.2 x 2.2 m) in a white gypsum frame inside a dark basalt surround, studs and a small
    qamariya over it"""
    def b():
        m = _wall(K, [_rect(-0.6, 0.0, 0.6, 2.35)], reveal="wall")
        m.box((-0.6, 0.0, -0.36), (0.6, 2.35, -0.3), "frame", 0.8)
        for k, (y0, y1) in enumerate(((0.15, 1.0), (1.15, 2.2))):          # carved panels, two leaves
            for x0 in (-0.52, 0.04):
                m.box((x0, y0, -0.3), (x0 + 0.48, y1, -0.27), "frame", 0.95 - 0.1 * k, skip=("z-",))
                _beads(m, x0 + 0.04, x0 + 0.44, y1 - 0.12, y1 - 0.05, -0.27, -0.25, 5, "frame", 0.8)
        for x in (-0.4, -0.2, 0.2, 0.4):                                    # iron studs
            for y in (0.5, 1.5):
                m.box((x - 0.025, y - 0.025, -0.27), (x + 0.025, y + 0.025, -0.24), "metal", skip=("z-",))
        e = 0.005                                                           # U frames (no sill: a door)
        m.wall_cut(_rect(-0.74, 0.0, 0.74, 2.49), [_rect(-0.6 - e, -1.0, 0.6 + e, 2.35 + e)], -0.01, 0.04, "trim")
        m.wall_cut(_rect(-0.96, 0.0, 0.96, 2.66), [_rect(-0.74 - e, -1.0, 0.74 + e, 2.49 + e)], -0.01, 0.025, "wall", 0.55)
        r, top = 0.3, 2.78
        fan = [(-r, top), (r, top)] + [(r * math.cos(math.pi * k / 8), top + r * math.sin(math.pi * k / 8)) for k in range(1, 8)]
        m.wall_cut(fan, [], 0.0, 0.03, "emissive")
        m.wall_cut(_off(fan, 0.1), [_off(fan, 0.005)], -0.01, 0.06, "trim")
        return m
    return b


def wall_window_grille():
    """a small grilled window in the thick basalt ground storey: deep reveal, iron bars, a white gypsum frame"""
    def b():
        x0, y0, x1, y1 = -0.3, 1.3, 0.3, 2.1
        m = _wall(K, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.4)
        for k in range(1, 4):
            x = x0 + (x1 - x0) * k / 4
            _strip(m, (x, y0, -0.12), (x, y1, -0.12), 0.025, (0, 0, 1), "metal")
        for y in (y0 + 0.27, y0 + 0.54):
            _strip(m, (x0, y, -0.115), (x1, y, -0.115), 0.025, (0, 0, 1), "metal")
        _ring(m, x0, y0, x1, y1, 0.1, 0.0, 0.04, "trim")
        return m
    return b


def edge_parapet_crenel_white():
    """the stepped Sana'a merlons in white gypsum: one silhouette cut flat (four stepped merlons on a band)"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0)]
        for x in (1.125, 0.375, -0.375, -1.125):
            p += [(x + 0.28, 0.5), (x + 0.28, 0.72), (x + 0.14, 0.72), (x + 0.14, 0.92), (x - 0.14, 0.92), (x - 0.14, 0.72),
                  (x - 0.28, 0.72), (x - 0.28, 0.5)]
        _flat_prism(m, p, -0.4, 0.0, "trim", open_edges=(0,))
        return m
    return b


def minaret_brick_round(part):
    """the Sana'a minaret: a round brick shaft with relief bands (stack _shaft per storey) and the white gallery top"""
    def b():
        m = Mesh()
        if part == "shaft":
            m.cyl(0, 0, 1.1, 0.0, ST, "wall", n=12, caps=False)
            m.cyl(0, 0, 1.14, 2.6, 2.75, "trim", n=12, caps=False)
            m.cyl(0, 0, 1.14, 3.05, 3.2, "trim", n=12, caps=False)
            for k in range(12):                                   # the zigzag relief between the white bands
                a0, a1 = math.tau * k / 12, math.tau * (k + 1) / 12
                y0, y1 = (2.78, 3.02) if k % 2 == 0 else (3.02, 2.78)
                p0 = (1.13 * math.cos(a0), y0, -1.13 * math.sin(a0))
                p1 = (1.13 * math.cos(a1), y1, -1.13 * math.sin(a1))
                mid = (math.cos((a0 + a1) / 2), 0, -math.sin((a0 + a1) / 2))
                _strip(m, p0, p1, 0.05, mid, "wall")
        else:
            m.cyl(0, 0, 1.1, 0.0, 0.86, "wall", n=12, caps=False)
            m.lathe([(1.12, 0.8), (1.55, 1.0), (1.55, 1.12), (0.0, 1.12)], "trim", n=12)        # the gallery
            for k in range(12):
                a = math.tau * k / 12
                m.box((1.45 * math.cos(a) - 0.03, 1.12, -1.45 * math.sin(a) - 0.03), (1.45 * math.cos(a) + 0.03, 1.95, -1.45 * math.sin(a) + 0.03), "trim", skip=("y-",))
            m.cyl(0, 0, 1.52, 1.9, 2.0, "trim", n=12, caps=False)
            m.cyl(0, 0, 0.75, 1.12, 3.6, "trim", n=10, caps=False)
            for k in range(4):                                    # lit arched openings in the white top
                a = math.tau * k / 4
                c, s = math.cos(a), math.sin(a)
                sub = Mesh()
                sub.quad_facing((-0.18, 2.3, 0.0), (0.18, 2.3, 0.0), (0.18, 3.05, 0.0), (-0.18, 3.05, 0.0), (0, 0, 1), "emissive")
                sub.tri_facing((-0.18, 3.05, 0.0), (0.18, 3.05, 0.0), (0.0, 3.25, 0.0), (0, 0, 1), "emissive")
                _place(m, sub, math.degrees(a) + 90, dx=0.77 * c, dz=-0.77 * s)
            m.lathe([(0.8, 3.6), (0.82, 3.75), (0.7, 4.1), (0.4, 4.45), (0.0, 4.6)], "trim", n=10)
            m.lathe([(0.0, 4.55), (0.07, 4.7), (0.03, 5.0), (0.0, 5.2)], "metal", n=6)
        return m
    return b


def drain_spout():
    """a 0.6 m timber roof spout on a roof edge (y 0 = the roof top, +Z out)"""
    def b():
        m = Mesh()
        m.box((0.6, -0.18, -0.2), (0.76, -0.06, 0.6), "frame", skip=("z-",))
        m.box((0.62, -0.06, -0.2), (0.64, 0.0, 0.6), "frame", 0.8)
        m.box((0.72, -0.06, -0.2), (0.74, 0.0, 0.6), "frame", 0.8)
        return m
    return b


def skybridge_timber():
    """a one-cell enclosed timber bridge between two towers at an upper storey (Shibam): it spans X across the cell
    (its open ends butt the towers' doors), a floor at y 0, latticed windows both sides, a flat white-edged roof"""
    def b():
        m = Mesh()
        d = 0.9
        m.box((-HB, -0.3, -d), (HB, 0.0, d), "frame", 0.8, skip=("x-", "x+"))
        for s in (-1, 1):
            sub = Mesh()
            sub.wall_cut(_rect(-HB, 0.0, HB, 2.5), [_rect(-1.1, 0.9, -0.3, 1.9), _rect(0.3, 0.9, 1.1, 1.9)], -0.12, 0.0, "wall", reveal_slot="trim")
            for x0 in (-1.1, 0.3):
                sub.pane(x0, 0.9, x0 + 0.8, 1.9, -0.08)
                _lattice(sub, x0, 0.9, x0 + 0.8, 1.9, -0.06, -0.01, 4, 5, slot="frame")
            sub.box((-HB, 2.3, 0.0), (HB, 2.4, 0.04), "trim", skip=("z-", "x-", "x+"))
            _place(m, sub, 0 if s > 0 else 180, dz=s * d)
        m.box((-HB, 2.5, -d - 0.1), (HB, 2.62, d + 0.1), "trim", skip=("x-", "x+"))
        for x in (-1.2, 0.0, 1.2):                                # timber joists under
            m.box((x - 0.08, -0.45, -d), (x + 0.08, -0.3, d), "frame", 0.7, skip=("y+",))
        return m
    return b


# ------------------------------------------------------------------ Japan
def ov_vending_machine():
    """two glowing vending machines against a wall at street level (face overlay: +Z out of the face)"""
    def b():
        m = Mesh()
        for k, x0 in enumerate((-1.25, -0.25)):
            x1 = x0 + 0.92
            m.box((x0, 0.0, 0.02), (x1, 1.83, 0.72), "trim" if k == 0 else "accent", skip=("y-", "z-"))
            m.quad_facing((x0 + 0.08, 0.95, 0.725), (x1 - 0.08, 0.95, 0.725), (x1 - 0.08, 1.72, 0.725), (x0 + 0.08, 1.72, 0.725), (0, 0, 1), "emissive")
            for j in range(3):                                    # rows of bottles
                y = 1.05 + j * 0.24
                for i in range(6):
                    x = x0 + 0.14 + i * 0.12
                    m.quad_facing((x, y, 0.73), (x + 0.06, y, 0.73), (x + 0.06, y + 0.15, 0.73), (x, y + 0.15, 0.73), (0, 0, 1), "accent2" if (i + j) % 2 else "fabric")
            m.box((x0 + 0.1, 0.15, 0.72), (x1 - 0.1, 0.32, 0.76), "frame", 0.5, skip=("z-",))
            m.box((x1 - 0.22, 0.6, 0.72), (x1 - 0.1, 0.85, 0.75), "metal", skip=("z-",))
        return m
    return b


def stair_steel_external():
    """the zakkyo's external steel stair: one storey up along +X across the bay face (y 0 -> 3.2 from x -1.45 to
    1.45), a landing at the top, stringers, railing (face overlay, 0.9 m out)"""
    def b():
        m = Mesh()
        n, z0, z1 = 12, 0.05, 0.9
        run = 2.3
        for k in range(n):
            x = -1.45 + run * k / n
            y = ST * (k + 1) / n
            m.box((x, y - 0.04, z0), (x + run / n + 0.02, y, z1), "metal", 0.85)
        m.box((-1.45 + run, ST - 0.06, z0), (1.5, ST, z1), "metal", 0.85)                     # landing
        for z in (z0 + 0.02, z1 - 0.02):                                                       # stringers
            m.quad_facing((-1.45, 0.0, z), (-1.45 + run, ST - 0.25, z), (-1.45 + run, ST, z), (-1.45, 0.25, z), (0, 0, 1 if z > 0.5 else -1), "metal", 0.7)
        m.tube((-1.45, 1.0, z1), (-1.45 + run, ST + 1.0, z1), 0.022, "metal", n=4)              # railing
        m.tube((-1.45 + run, ST + 1.0, z1), (1.5, ST + 1.0, z1), 0.022, "metal", n=4)
        for k in range(5):
            x = -1.45 + run * k / 4
            y = ST * k / 4
            m.tube((x, y, z1), (x, y + 1.0, z1), 0.015, "metal", n=3)
        m.tube((1.5, ST, z1), (1.5, ST + 1.0, z1), 0.015, "metal", n=3)
        return m
    return b


def utility_pole():
    """a concrete utility pole with crossarms, a pole transformer and wire bundles drooping off (cell decor)"""
    def b():
        m = Mesh()
        m.cyl(0, 0, 0.16, 0.0, 8.5, "trim", n=6, r1=0.11)
        for y, w in ((7.9, 1.2), (7.2, 0.9)):
            m.box((-w, y, -0.06), (w, y + 0.1, 0.06), "metal", 0.8)
            for x in (-w + 0.08, w - 0.08):
                m.cyl(x, 0, 0.04, y + 0.1, y + 0.22, "trim", n=4)
        m.cyl(0.0, 0.32, 0.22, 5.8, 6.6, "metal", n=6)                                          # transformer
        m.box((-0.05, 6.0, 0.1), (0.05, 6.1, 0.3), "metal")
        for x in (-1.12, -0.6, 0.6, 1.12):                                                      # wire stubs, drooping
            m.tube((x, 7.95, 0.0), (x * 1.6, 7.6, 1.5), 0.012, "frame", n=3)
            m.tube((x, 7.95, 0.0), (x * 1.6, 7.6, -1.5), 0.012, "frame", n=3)
        for y in (2.2, 2.6, 3.0):
            m.box((-0.17, y, -0.02), (0.17, y + 0.04, 0.17), "metal", 0.6)                     # step bolts
        return m
    return b


def torii():
    """a vermilion shrine gate over a lane (cell): two pillars, the nuki tie beam, the kasagi lintel with upturned
    ends and its black top"""
    def b():
        m = Mesh()
        for x in (-1.1, 1.1):
            m.cyl(x, 0, 0.16, 0.0, 3.4, "accent", n=8, r1=0.14, caps=False)
            m.cyl(x, 0, 0.2, 0.0, 0.25, "frame", n=8, caps=False)
        m.box((-1.45, 2.65, -0.08), (1.45, 2.85, 0.08), "accent")                               # nuki
        m.box((-0.07, 2.85, -0.06), (0.07, 3.35, 0.06), "accent", 0.9)                          # gakuzuka
        prof = [(-1.85, 3.62), (-1.5, 3.42), (1.5, 3.42), (1.85, 3.62), (1.85, 3.72), (1.5, 3.56), (-1.5, 3.56), (-1.85, 3.72)]
        _flat_prism(m, prof, -0.14, 0.14, "accent")
        top = [(-1.95, 3.72), (-1.85, 3.62), (-1.5, 3.56), (1.5, 3.56), (1.85, 3.62), (1.95, 3.72), (1.95, 3.82), (1.5, 3.68), (-1.5, 3.68), (-1.95, 3.82)]
        _flat_prism(m, top, -0.17, 0.17, "frame")
        m.box((-1.45, 3.35, -0.12), (1.45, 3.42, 0.12), "accent", 0.85)
        return m
    return b


def wall_koshi():
    """a machiya bay: the koshi timber lattice across the ground floor (glass behind), a small pent eave of grey tile,
    the mushiko window above (plaster with vertical slats)"""
    def b():
        m = _wall(T, [_rect(-1.35, 0.25, 1.35, 2.0), _rect(-0.7, 2.45, 0.7, 2.95)])
        m.pane(-1.35, 0.25, 1.35, 2.0, -0.15)
        m.box((-1.4, 0.0, 0.0), (1.4, 0.25, 0.12), "frame", 0.7, skip=("z-",))
        for k in range(1, 24):                                                                  # koshi
            x = -1.35 + 2.7 * k / 24
            _strip(m, (x, 0.25, -0.03), (x, 2.0, -0.03), 0.035, (0, 0, 1), "frame")
        for y in (0.3, 1.95):
            _strip(m, (-1.35, y, -0.025), (1.35, y, -0.025), 0.06, (0, 0, 1), "frame")
        m.pane(-0.7, 2.45, 0.7, 2.95, -0.18)
        for k in range(1, 10):                                                                  # mushiko
            x = -0.7 + 1.4 * k / 10
            _strip(m, (x, 2.45, -0.05), (x, 2.95, -0.05), 0.06, (0, 0, 1), "trim")
        m.quad_facing((-HB, 2.35, 0.0), (HB, 2.35, 0.0), (HB, 2.05, 0.75), (-HB, 2.05, 0.75), (0, 1, 0.4), "roof")
        m.quad_facing((-HB, 2.31, 0.0), (HB, 2.31, 0.0), (HB, 2.01, 0.75), (-HB, 2.01, 0.75), (0, -1, -0.4), "frame", 0.55)
        for k in range(10):
            x = -HB + 0.15 + k * 0.3
            _strip(m, (x, 2.07, 0.73), (x, 2.33, 0.02), 0.07, (0, 1, 0.4), "roof")
        return m
    return b


# ------------------------------------------------------------------ Hanseatic
def hoist_beam():
    """the attic hoist beam over the luiken hatch column: beam 1 m out, pulley, rope and hook (face overlay at the top
    storey, y 0 = that storey's floor)"""
    def b():
        m = Mesh()
        m.box((-0.08, 2.6, -0.1), (0.08, 2.78, 1.0), "frame", skip=("z-",))
        m.tube((0.0, 2.25, 0.02), (0.0, 2.6, 0.55), 0.04, "frame", n=4)
        m.cyl(0.0, 0.92, 0.08, 2.46, 2.6, "metal", n=6)
        m.tube((0.0, 2.46, 0.92), (0.0, 0.9, 0.92), 0.008, "metal", n=3)
        m.box((-0.05, 0.78, 0.87), (0.05, 0.9, 0.97), "metal")
        return m
    return b


def wall_luiken():
    """the attic hatch column bay: a tall hatch in the middle in a white frame, closed by stacked painted shutters
    (luiken), a small window each side (thick brick wall)"""
    def b():
        ops = [_rect(-0.45, 0.2, 0.45, 2.75), _rect(-1.25, 1.2, -0.85, 2.0), _rect(0.85, 1.2, 1.25, 2.0)]
        m = _wall(K, ops)
        for k, (y0, y1) in enumerate(((0.2, 1.45), (1.5, 2.75))):                              # two pairs of shutters
            for x0 in (-0.45, 0.0):
                m.box((x0 + 0.01, y0, -0.2), (x0 + 0.44, y1, -0.14), "accent", 0.95 - 0.08 * k)
                _strip(m, (x0 + 0.06, y0 + 0.08, -0.135), (x0 + 0.39, y1 - 0.08, -0.135), 0.05, (0, 0, 1), "accent2")
                _strip(m, (x0 + 0.39, y0 + 0.08, -0.13), (x0 + 0.06, y1 - 0.08, -0.13), 0.05, (0, 0, 1), "accent2")
        _ring(m, -0.45, 0.2, 0.45, 2.75, 0.08, 0.0, 0.05, "trim")
        for x0 in (-1.25, 0.85):
            m.pane(x0, 1.2, x0 + 0.4, 2.0, -0.3)
            _strip(m, (x0 + 0.2, 1.2, -0.29), (x0 + 0.2, 2.0, -0.29), 0.03, (0, 0, 1), "trim")
            _ring(m, x0, 1.2, x0 + 0.4, 2.0, 0.05, 0.0, 0.04, "trim")
        return m
    return b


def church_spire_copper():
    """a verdigris copper spire over the brick tower's top storey (crown on the tower's top cell): the belfry with
    louvred lit openings and clock faces, an octagonal needle spire, a gilt ball and cock"""
    def b():
        m = Mesh()
        m.box((-1.4, 0.0, -1.4), (1.4, 3.0, 1.4), "wall", skip=("y-",))
        for k in range(4):
            sub = Mesh()
            sub.quad_facing((-0.35, 0.9, 1.41), (0.35, 0.9, 1.41), (0.35, 2.3, 1.41), (-0.35, 2.3, 1.41), (0, 0, 1), "frame", 0.5)
            for j in range(5):
                y = 1.05 + j * 0.25
                _strip(sub, (-0.35, y, 1.42), (0.35, y, 1.42), 0.1, (0, 0.4, 1), "tile")
            sub.wall_cut([(0.32 * math.cos(math.tau * i / 10), 2.65 + 0.32 * math.sin(math.tau * i / 10)) for i in range(10)], [], 1.4, 1.45, "trim")
            _place(m, sub, 90 * k)
        m.box((-1.5, 3.0, -1.5), (1.5, 3.15, 1.5), "trim", skip=())
        m.lathe([(1.15, 3.15), (1.0, 3.6), (0.75, 4.0), (0.55, 4.0), (0.55, 4.9), (0.62, 5.0), (0.3, 6.5), (0.08, 9.5), (0.0, 10.4)], "tile", n=8)
        for k in range(8):                                       # lit lantern stage openings
            a = math.tau * (k + 0.5) / 8
            sub = Mesh()
            sub.quad_facing((-0.12, 4.15, 0.0), (0.12, 4.15, 0.0), (0.12, 4.75, 0.0), (-0.12, 4.75, 0.0), (0, 0, 1), "emissive")
            _place(m, sub, math.degrees(a) + 90, dx=0.53 * math.cos(a), dz=-0.53 * math.sin(a))
        m.lathe([(0.0, 10.2), (0.14, 10.35), (0.0, 10.5)], "accent2", n=6)
        m.box((-0.15, 10.7, -0.01), (0.15, 10.85, 0.01), "accent2")
        m.cyl(0, 0, 0.012, 10.45, 11.0, "metal", n=3)
        return m
    return b


def bridge_humped_brick():
    """a humped brick canal bridge over three cells along +Z (span [1, 3]: z -1.5 .. 7.5), its deck rising 1.1 m to the
    middle, a brick arch beneath, parapets with stone coping and bulb strings"""
    def b():
        m = Mesh()
        L, n, w = 9.0, 10, 1.4
        zs = [-HB + L * i / n for i in range(n + 1)]
        ys = [1.1 * math.sin(math.pi * i / n) ** 0.8 for i in range(n + 1)]
        for i in range(n):
            za, zb, ya, yb = zs[i], zs[i + 1], ys[i], ys[i + 1]
            m.quad_facing((-w, ya, za), (w, ya, za), (w, yb, zb), (-w, yb, zb), (0, 1, 0), "ground", 0.9 + 0.1 * (i % 2))
            for s in (-1, 1):                                    # parapets
                m.quad_facing((s * w, ya, za), (s * w, yb, zb), (s * w, yb + 0.9, zb), (s * w, ya + 0.9, za), (-s, 0, 0), "wall", 0.9)
                m.quad_facing((s * (w + 0.3), ya - 1.4, za), (s * (w + 0.3), yb - 1.4, zb),
                              (s * (w + 0.3), yb + 0.9, zb), (s * (w + 0.3), ya + 0.9, za), (s, 0, 0), "wall")
                m.quad_facing((s * w, ya + 0.9, za), (s * (w + 0.3), ya + 0.9, za), (s * (w + 0.3), yb + 0.9, zb), (s * w, yb + 0.9, zb), (0, 1, 0), "trim")
            arch = lambda z: -1.4 + 1.0 * math.sin(math.pi * min(max((z - 0.0) / 6.0, 0.0), 1.0))  # noqa: E731
            m.quad_facing((-w - 0.3, arch(za) if 0.0 <= za <= 6.0 else ya - 1.4, za), (w + 0.3, arch(za) if 0.0 <= za <= 6.0 else ya - 1.4, za),
                          (w + 0.3, arch(zb) if 0.0 <= zb <= 6.0 else yb - 1.4, zb), (-w - 0.3, arch(zb) if 0.0 <= zb <= 6.0 else yb - 1.4, zb), (0, -1, 0), "wall", 0.6)
        for s in (-1, 1):                                        # bulb strings on the coping
            for i in range(1, n):
                m.box((s * (w + 0.15) - 0.03, ys[i] + 0.93, zs[i] - 0.03), (s * (w + 0.15) + 0.03, ys[i] + 0.99, zs[i] + 0.03), "emissive")
        return m
    return b


def quay_edge_stone():
    """a stone quay edge (water_edge, like kerb_straight: along x, the water on +Z): the quay wall falls 1.5 m to the
    water, a coping, iron mooring rings, a bollard"""
    def b():
        m = Mesh()
        m.box((-HB, -1.6, -0.5), (HB, 0.0, 0.0), "wall", 0.75, skip=("y-", "x-", "x+"))
        m.box((-HB, 0.0, -0.55), (HB, 0.14, 0.06), "trim", skip=("y-", "x-", "x+"))
        for x in (-0.8, 0.8):                                    # mooring rings
            pts = [(x + 0.12 * math.cos(math.tau * k / 6), -0.55 + 0.12 * math.sin(math.tau * k / 6), 0.05) for k in range(7)]
            for a, c in zip(pts, pts[1:]):
                m.tube(a, c, 0.015, "metal", n=3)
        m.cyl(0.0, -0.25, 0.14, 0.14, 0.6, "metal", n=8, r1=0.12)
        m.lathe([(0.17, 0.6), (0.17, 0.66), (0.0, 0.7)], "metal", n=8, cz=-0.25)
        return m
    return b


# ------------------------------------------------------------------ Chongqing
def stair_street_long():
    """a Shibati stair street: 3 m wide, a full storey up over two cells along +Z (span [1, 2]): two flights of 9
    steps with a landing between, rough stone treads, iron handrails"""
    def b():
        m = Mesh()
        steps = []
        for k in range(9):
            steps.append((-HB + k * 0.3, 0.178 * (k + 1)))
        for k in range(9):
            steps.append((-HB + 2.7 + 1.2 + k * 0.3, 1.6 + 0.178 * (k + 1)))
        for k, (z0, y) in enumerate(steps):
            m.box((-HB, y - 0.4, z0), (HB, y, z0 + 0.32), "ground", 0.88 + 0.12 * ((k * 7) % 3) / 2, skip=("y-", "x-", "x+"))
        m.box((-HB, 1.2, 1.2), (HB, 1.6, 2.4), "ground", 0.95, skip=("y-", "x-", "x+"))          # the landing
        for x in (-1.35, 1.35):
            m.tube((x, 0.95, -HB), (x, 1.6 + 0.95, 1.2), 0.022, "metal", n=4)
            m.tube((x, 1.6 + 0.95, 1.2), (x, 1.6 + 0.95, 2.4), 0.022, "metal", n=4)
            m.tube((x, 1.6 + 0.95, 2.4), (x, ST + 0.95, 4.5), 0.022, "metal", n=4)
            for z, y in ((-HB, 0.0), (1.2, 1.6), (2.4, 1.6), (4.5, ST)):
                m.tube((x, y, z), (x, y + 0.95, z), 0.02, "metal", n=3)
        return m
    return b


def wall_gallery_timber():
    """a storey of timber gallery: the deck 1 m out along the whole bay, posts, a carved rail with balusters, a plank
    door and a lattice window behind"""
    def b():
        m = _wall(T, [_rect(-1.25, 0.0, -0.2, 2.3), _rect(0.15, 0.9, 1.2, 2.2)], reveal="frame")   # (door 1.05 x 2.3)
        m.box((-1.245, 0.0, -0.2), (-0.205, 2.295, -0.16), "frame", 0.75)
        m.pane(0.15, 0.9, 1.2, 2.2, -0.16)
        _lattice(m, 0.155, 0.905, 1.195, 2.195, -0.12, -0.06, 6, 5, slot="frame")
        d = 1.0
        m.box((-HB, -0.1, 0.004), (HB, 0.0, d), "frame", 0.85, skip=("z-", "x-", "x+"))
        m.box((-HB, 0.95, d - 0.07), (HB, 1.03, d), "frame", skip=("x-", "x+"))
        for k in range(14):
            x = -HB + 0.11 + k * 0.215
            m.box((x - 0.02, 0.0, d - 0.05), (x + 0.02, 0.95, d - 0.02), "frame", 0.85, skip=("y-", "y+"))
        for x in (-1.44, 0.0, 1.44):
            m.box((x - 0.05, 0.0, d - 0.11), (x + 0.05, ST - 0.15, d + 0.01), "frame", 0.8, skip=("y-",))
        m.box((-HB, ST - 0.15, 0.004), (HB, ST - 0.004, d), "frame", 0.7, skip=("z-", "x-", "x+"))
        for x in (-1.2, 0.0, 1.2):
            m.tube((x, -0.9, 0.0), (x, -0.1, d - 0.15), 0.04, "frame", n=4)
        return m
    return b


def skybridge_street():
    """a street bridge into a building's upper floor (cell, spanning along +Z): concrete deck on two beams, steel
    railings, LED edge strip"""
    def b():
        m = Mesh()
        m.box((-1.2, -0.25, -HB), (1.2, 0.0, HB), "ground", 0.9, skip=("z-", "z+"))
        for x in (-0.8, 0.8):
            m.box((x - 0.15, -0.75, -HB), (x + 0.15, -0.25, HB), "trim", 0.7, skip=("z-", "z+", "y+"))
        for s in (-1, 1):
            x = s * 1.15
            m.tube((x, 1.05, -HB), (x, 1.05, HB), 0.03, "metal", n=4)
            for z in (-1.2, 0.0, 1.2):
                m.tube((x, 0.0, z), (x, 1.05, z), 0.02, "metal", n=3)
            _strip(m, (x, 0.5, -HB), (x, 0.5, HB), 0.6, (s, 0, 0), "screen")
            m.box((x - 0.02, -0.05, -HB), (x + 0.02, -0.01, HB), "emissive", skip=("z-", "z+"))
        return m
    return b


def ov_gold_eave_led():
    """the warm gold LED line traced along an eave (edge overlay: a 3 m emissive bar along x at the eave lip; offset it
    with the eave piece's lip: edge_eave_pagoda's is at y 0.12, z 1.25)"""
    def b():
        m = Mesh()
        m.box((-HB, -0.02, -0.02), (HB, 0.02, 0.02), "emissive", skip=("x-", "x+"))
        return m
    return b


# ------------------------------------------------------------------ Andes
def _inca_stones(seed, x0, y0, x1, y1, nx, ny, cut=None):
    """fitted polygonal stones: a jittered grid of shared corners (each joint shared by its neighbours), each stone
    shrunk for the joint; cut: an opening polygon to leave out"""
    r = _rng(seed)
    pts = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            jx = 0.0 if i in (0, nx) else r.uniform(-0.3, 0.3)
            jy = 0.0 if j in (0, ny) else r.uniform(-0.3, 0.3)
            pts[i, j] = (x0 + (x1 - x0) * (i + jx) / nx, y0 + (y1 - y0) * (j + jy) / ny)
    out = []
    for i in range(nx):
        for j in range(ny):
            g = Polygon([pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]])
            if cut is not None:
                g = g.difference(Polygon(cut))
            g = g.buffer(-0.018, join_style=2)
            for q in getattr(g, "geoms", [g]):
                if q.geom_type == "Polygon" and q.area > 0.02:
                    out.append(_dedupe([tuple(p) for p in list(q.exterior.coords)[:-1]]))
    return out


def wall_inca_base(door):
    """an Inca polygonal fitted-stone ground bay (Cusco): irregular stones pillowed out of a dark joint, battered back
    5 degrees; door: the trapezoid doorway (narrower at the top)"""
    def b():
        trap = [(-0.65, 0.0), (0.65, 0.0), (0.55, 2.4), (-0.55, 2.4)]   # (1.1 m clear at the top, 2.4 m: walk-through)
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [trap] if door else [], -K, -0.04, "wall", 0.45, reveal_slot="ground")
        tilt = math.tan(math.radians(5))
        stones = _inca_stones(7 if door else 3, -HB, 0.0, HB, ST, 5, 5, trap if door else None)
        for k, s in enumerate(stones):
            sub = Mesh()
            _flat_prism(sub, s, -0.05, 0.0, "ground", 0.82 + 0.18 * ((k * 37) % 7) / 6)
            m.add(sub, lambda p: (p[0], p[1], p[2] + (ST - p[1]) * tilt * 0.4))
        if door:
            m.box((-0.72, 2.4, -0.06), (0.72, 2.65, 0.05), "ground", 0.75, skip=("z-",))          # the lintel stone
            m.box((-0.55, 0.0, -0.4), (0.55, 2.4, -0.36), "frame", 0.7)
        return m
    return b


def wall_box_balcony():
    """Lima's enclosed box balcony: dark carved timber 1 m deep on corbels, closed lattice panels front and sides, a
    carved apron, a cornice and a small hood (thick colonial wall behind)"""
    def b():
        m = _wall(K, [_rect(-0.7, 0.2, 0.7, 2.6)], reveal="frame")
        m.pane(-0.7, 0.2, 0.7, 2.6, -0.3)
        d, x0, x1 = 1.0, -1.3, 1.3
        for x in (-1.0, 0.0, 1.0):
            _corbel(m, x, 0.15, d - 0.05, 0.8, 0.14, "frame", 0.85)
        m.box((x0, 0.15, 0.0), (x1, 0.27, d), "frame", 0.85, skip=("z-",))
        m.box((x0, 0.27, d - 0.05), (x1, 0.85, d), "frame", skip=("z-",))
        for k in range(5):
            x = x0 + 0.08 + k * 0.51
            m.box((x, 0.36, d), (x + 0.42, 0.76, d + 0.02), "frame", 0.75, skip=("z-",))
        for k in range(4):
            xa = x0 + 0.05 + k * 0.65
            sub = Mesh()
            _lattice(sub, xa, 0.85, xa + 0.6, 2.35, d - 0.05, d, 6, 12, slot="frame")
            sub.pane(xa + 0.06, 0.91, xa + 0.54, 2.29, d - 0.07)
            m.add(sub)
        for side in (-1, 1):
            xa, xb = (0.06, d - 0.06) if side < 0 else (-(d - 0.06), -0.06)
            sub = Mesh()
            _lattice(sub, xa, 0.85, xb, 2.35, -0.05, 0.0, 5, 12, slot="frame")
            sub.box((xa, 0.27, -0.05), (xb, 0.85, 0.0), "frame", 0.8, skip=("z-",))
            _place(m, sub, 90 * side, dx=x1 if side > 0 else x0)
        m.box((x0 - 0.1, 2.35, 0.0), (x1 + 0.1, 2.5, d + 0.1), "frame", skip=("z-",))
        _beads(m, x0, x1, 2.38, 2.47, d + 0.1, d + 0.13, 16, "frame", 0.8)
        m.quad_facing((x0 - 0.15, 2.85, 0.0), (x1 + 0.15, 2.85, 0.0), (x1 + 0.15, 2.5, d + 0.15), (x0 - 0.15, 2.5, d + 0.15), (0, 1, 0.5), "roof")
        return m
    return b


def cholet_chalet_top():
    """the peaked chalet perched on a cholet's roof (crown): mirror-glass walls in coloured frames, a steep gable to
    the front (+Z), LED edges along the roof"""
    def b():
        m = Mesh()
        w, d, h = 1.3, 1.2, 2.4
        m.box((-w, 0.0, -d), (w, h, d), "glass", skip=("y-",))
        for x in (-w, -0.4, 0.4, w):
            m.box((x - 0.06, 0.0, d), (x + 0.06, h - 0.12, d + 0.06), "accent", skip=("z-",))
        m.box((-w - 0.05, h - 0.12, d), (w + 0.05, h, d + 0.08), "accent2", skip=("z-",))
        _flat_prism(m, [(-w, h), (w, h), (0.0, h + 1.6)], d - 0.05, d + 0.02, "fabric", open_edges=(0,))
        _flat_prism(m, [(-w, h), (w, h), (0.0, h + 1.6)], -d - 0.02, -d + 0.05, "fabric", open_edges=(0,))
        for s in (-1, 1):
            m.quad_facing((s * (w + 0.25), h - 0.18, -d - 0.2), (s * (w + 0.25), h - 0.18, d + 0.25), (0.0, h + 1.65, d + 0.25), (0.0, h + 1.65, -d - 0.2), (s, 1, 0), "roof")
            _strip(m, (s * (w + 0.25), h - 0.17, d + 0.26), (0.0, h + 1.66, d + 0.26), 0.05, (0, 0, 1), "emissive")
        m.wall_cut([(0.0, h + 0.3), (0.35, h + 0.7), (0.0, h + 1.1), (-0.35, h + 0.7)], [], d + 0.02, d + 0.05, "accent")
        return m
    return b


def ov_rebar_stubs():
    """rebar sticking up from an unfinished roof slab: four column stubs, each with four bent bars (roof decor)"""
    def b():
        m = Mesh()
        for cx in (-1.3, 1.3):
            for cz in (-1.3, 1.3):
                m.box((cx - 0.12, 0.0, cz - 0.12), (cx + 0.12, 0.15, cz + 0.12), "trim", 0.75, skip=("y-",))
                for dx, dz in ((-0.07, -0.07), (0.07, -0.07), (0.07, 0.07), (-0.07, 0.07)):
                    top = (cx + dx * 1.8, 0.95, cz + dz * 1.8)
                    for nrm in ((1, 0, 0), (0, 0, 1)):
                        _strip(m, (cx + dx, 0.15, cz + dz), top, 0.02, nrm, "metal")
        return m
    return b


def cable_car():
    """a Mi Teleferico gondola line over a cell (along X at 7 m) with a cabin hanging off it (decor, no collision)"""
    def b():
        m = Mesh()
        for z in (-0.25, 0.25):
            m.tube((-HB, 7.0, z), (HB, 7.0, z), 0.02, "metal", n=3)
        m.box((-0.12, 6.75, -0.3), (0.12, 7.1, 0.3), "metal", 0.7)
        m.tube((0.0, 6.75, 0.0), (0.0, 5.6, 0.0), 0.04, "metal", n=4)
        m.box((-0.9, 3.7, -0.75), (0.9, 5.6, 0.75), "accent", skip=())
        for s in (-1, 1):
            sub = Mesh()
            sub.pane(-0.75, 4.3, 0.75, 5.3, 0.0)
            _place(m, sub, 0 if s > 0 else 180, dz=s * 0.76)
        m.lathe([(0.95, 5.6), (0.5, 5.8), (0.0, 5.85)], "accent2", n=8)
        return m
    return b


# ------------------------------------------------------------------ register
SH = BOTH
PIECES["pave_skirt"] = _w("cell", pave_skirt(), SH, lod1="drop", collide=False, kind="ground", notes="0.6 m skirt down a deck's four sides (under any pave_*)")
for k in ("main", "lane", "plaza", "court", "garden"):
    PIECES[f"pave_{k}_skirt"] = _w("cell", pave_with_skirt(k), SH, kind="ground", notes=f"pave_{k} with its 0.6 m skirt (sloping streets)")
PIECES["edge_parapet_rounded_k"] = _w("edge", edge_parapet_rounded_cheap(), ["yemeni_tower", "maghrebi_medina", "mzab_ghadames"], lod1="keep",
                                      notes="Shibam soft white merlons (cheap silhouette)")
ROOFS = {   # id: (pitch, eave, ribs, slot, seam, dormer, civs, notes)
    "roof_pitched_pantile": (55, 0.3, 8, "roof", 0.08, False, ["hanseatic_gable", "scots_lands"], "50-60 deg pantile run behind a gable"),
    "roof_tile_red_low": (27, 0.7, 8, "roof", 0.07, False, ["andean_neo", "iberian_white", "creole_colonial", "latin_hillside"], "25-30 deg red tile, wide eaves"),
    "roof_kawara_low": (24, 0.6, 10, "roof", 0.07, False, ["japan_yokocho", "korean_hillside"], "low grey kawara tile roof"),
    "roof_tile_roman_low": (17, 0.35, 9, "roof", 0.09, False, ["iberian_white", "tyrrhenian_canyon", "cycladic", "lusitanian_hill"], "15-20 deg Roman tile"),
    "roof_tin_steep": (55, 0.35, 10, "metal", 0.025, True, ["nouvelle_france", "caucasian_balcony"], "standing-seam tin, a dormer each slope"),
}
for rid, (p, e, n, sl, sm, dm, civs, note) in ROOFS.items():
    PIECES[rid] = _w("cell", roof_seg(p, e, n, sl, sm, False, dm), civs, lod1="keep", kind="roof",
                     notes=f"{note}; a gable SEGMENT: ridge along Z, tiles into a run (y 0 = wall top)")
    PIECES[rid + "_end"] = _w("cell", roof_seg(p, e, n, sl, sm, True, dm), civs, lod1="keep", kind="roof",
                              notes=f"{note}; the run's end segment, gable wall closing -Z (turn it 180 for the far end)")
PIECES["roof_tile_flying_eave"] = _w("cell", roof_tile_flying_eave(), ["chongqing_cliff", "jiangnan_water", "taipei_tiepi"], lod1="keep", kind="roof",
                                     notes="grey tile hip, corners swept up, ridge")
Y = ["yemeni_tower"]
PIECES["wall_door_carved_k"] = _w("wall", wall_door_carved(), Y, notes="carved door, gypsum frame, basalt surround, fanlight")
PIECES["wall_window_grille_k"] = _w("wall", wall_window_grille(), Y + ["mzab_ghadames", "omani_oasis"], notes="small grilled window, thick ground storey")
PIECES["edge_parapet_crenel_white_k"] = _w("edge", edge_parapet_crenel_white(), Y, lod1="keep", notes="stepped Sana'a merlons, white (trim slot)")
PIECES["minaret_brick_round_shaft"] = _w("cell", minaret_brick_round("shaft"), Y, lod1="keep", kind="tower", notes="YEMEN: round brick minaret, one storey (stack)")
PIECES["minaret_brick_round_top"] = _w("cell", minaret_brick_round("top"), Y, lod1="keep", kind="tower", notes="YEMEN: gallery + white top on the shaft")
PIECES["drain_spout"] = _w("edge", drain_spout(), Y + ["saharan_kasbah", "mzab_ghadames"], lod1="drop", collide=False, kind="overlay", notes="timber roof spout")
PIECES["skybridge_timber"] = _w("cell", skybridge_timber(), Y + ["saharan_kasbah"], lod1="keep", notes="enclosed bridge spanning X between towers")
J = ["japan_yokocho"]
PIECES["ov_sign_vertical_stack"] = _w("wall", PIECES["wall_sign_column_t"]["build"], J + ["hk_neon_canyon", "taipei_tiepi"], lod1="keep", collide=False,
                                      kind="overlay", notes="= wall_sign_column_t (one storey of the lit sign column; stack)")
PIECES["ov_vending_machine"] = _w("wall", ov_vending_machine(), J + ["taipei_tiepi"], lod1="drop", kind="overlay", notes="two glowing vending machines at the foot of a face")
PIECES["stair_steel_external"] = _w("wall", stair_steel_external(), J + ["hk_neon_canyon", "taipei_tiepi"], lod1="keep", kind="overlay",
                                    notes="one storey of external steel stair along +X, 0.9 m out")
PIECES["utility_pole"] = _w("cell", utility_pole(), J + ["taipei_tiepi", "korean_hillside", "latin_hillside"], lod1="keep", notes="concrete pole, transformer, wires")
PIECES["torii"] = _w("cell", torii(), J, lod1="keep", notes="JAPAN MARK: vermilion shrine gate over a lane (along X)")
PIECES["wall_koshi_t"] = _w("wall", wall_koshi(), J, notes="machiya bay: koshi lattice, pent eave, mushiko window")
HS = ["hanseatic_gable"]
PIECES["hoist_beam"] = _w("wall", hoist_beam(), HS, lod1="drop", collide=False, kind="overlay", notes="attic hoist beam, pulley, hook")
PIECES["wall_luiken_k"] = _w("wall", wall_luiken(), HS, notes="attic hatch column, stacked shutters")
PIECES["church_spire_copper"] = _w("cell", church_spire_copper(), HS + ["nouvelle_france", "scots_lands"], lod1="keep", kind="tower",
                                   notes="belfry + verdigris copper spire (tile slot = copper)")
PIECES["bridge_humped_brick"] = _w("cell", bridge_humped_brick(), HS, lod1="keep", kind="bridge", span=(1, 3), notes="humped brick canal bridge along +Z, bulb strings")
PIECES["quay_edge_stone"] = _w("edge", quay_edge_stone(), HS + ["knights_harbour", "jiangnan_water"], lod1="box", kind="water_edge",
                               notes="stone quay edge, 1.5 m to the water, rings, bollard")
C = ["chongqing_cliff"]
PIECES["stair_street_long"] = _w("cell", stair_street_long(), C + ["korean_hillside", "latin_hillside"], collide="ramp", kind="stair", span=(1, 2),
                                 notes="3 m wide stair street, 3.2 m up over two cells along +Z, landing")
PIECES["wall_gallery_timber_t"] = _w("wall", wall_gallery_timber(), C, lod1="keep", notes="timber gallery 1 m deep along a storey")
PIECES["skybridge_street"] = _w("cell", skybridge_street(), C + ["hk_neon_canyon"], lod1="keep", kind="bridge", notes="street bridge along +Z into an upper floor")
PIECES["ov_gold_eave_led"] = _w("edge", ov_gold_eave_led(), C, lod1="keep", collide=False, kind="overlay", notes="gold LED line along an eave lip")
A = ["andean_neo"]
PIECES["wall_inca_base_k"] = _w("wall", wall_inca_base(False), A, notes="ANDES: Inca polygonal fitted stone, battered")
PIECES["wall_inca_door_k"] = _w("wall", wall_inca_base(True), A, notes="ANDES: Inca stone with the trapezoid doorway")
PIECES["wall_box_balcony_k"] = _w("wall", wall_box_balcony(), A + ["creole_colonial"], lod1="keep", notes="ANDES MARK: Lima enclosed box balcony")
PIECES["cholet_chalet_top"] = _w("cell", cholet_chalet_top(), A, lod1="keep", kind="crown", notes="ANDES MARK: the chalet on a cholet roof")
PIECES["ov_rebar_stubs"] = _w("cell", ov_rebar_stubs(), A + ["latin_hillside", "karachi"], lod1="drop", collide=False, kind="overlay", notes="rebar on an unfinished slab")
PIECES["cable_car"] = _w("cell", cable_car(), A + ["latin_hillside"], lod1="keep", collide=False, notes="gondola line along X at 7 m with a cabin")


# ------------------------------------------------------------------ the two missing palettes
def _pal(wall, trim, frame, roof, accent, accent2, glow, fabric, ground, metal="#4a4744", tile=None):
    return {"wall": wall, "trim": trim, "frame": frame, "glass": "#2c3a42", "screen": frame, "roof": roof, "metal": metal,
            "fabric": fabric, "emissive": glow, "tile": tile or trim, "water": "#3d7f8c", "ground": ground, "plant": "#5b7f3a",
            "accent": accent, "accent2": accent2}


PALETTES["latin_hillside"] = [
    _pal("#a8d14a", "#efe9dc", "#3a3a38", "#8f8d88", "#2a6ab0", "#f08a2a", "#e8f4ff", "#f07ca8", "#8f8d88"),
    _pal("#5bb7e5", "#efe9dc", "#3a3a38", "#8f8d88", "#2a6ab0", "#f6cf3a", "#ffcf7a", "#f08a2a", "#8f8d88"),
    _pal("#b2603e", "#8f8d88", "#3a3a38", "#8f8d88", "#2a6ab0", "#c23a2e", "#ffcf7a", "#5bb7e5", "#7a6a5a"),
    _pal("#f07ca8", "#efe9dc", "#3a3a38", "#c23a2e", "#2a55a8", "#3a9a5a", "#e8f4ff", "#f6cf3a", "#8f8d88"),
]
PALETTES["nouvelle_france"] = [
    _pal("#a39d90", "#c4bdae", "#2a2622", "#b8bcc0", "#1d1d1d", "#d8d0c0", "#ffd8a0", "#3f6a4a", "#8a8478"),
    _pal("#efebe2", "#c4bdae", "#2a2622", "#a8322a", "#2a5a3a", "#d8d0c0", "#ffd8a0", "#a8322a", "#8a8478"),
    _pal("#8a3e2c", "#d8d0c0", "#2a2622", "#3f6a4a", "#6a2a28", "#d8d0c0", "#ffd8a0", "#2a5a3a", "#8a8478"),
    _pal("#9a968e", "#d8d0c0", "#2a2622", "#1d1d1d", "#2a8a8a", "#f08a2a", "#ffd8a0", "#6a2a28", "#8a8478"),
]
for v in PALETTES.get("hanseatic_gable", []):
    v["tile"] = "#4f8f78"                                           # copper verdigris (spires)
