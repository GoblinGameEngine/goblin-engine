"""pieces_b9.py -- warren kit batch 4f: the generator's requests for mardin_terraces, ottoman_timber (extras),
rupestrian_terraces, scots_lands, siam_khlong (extras), straits_shophouse, tibetan_lhasa, tyrrhenian_canyon, viet_tube.
"""
import math
import random

from geom import Mesh, _dedupe, arch, rot_y
from pieces import BAY, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall
from pieces_b4 import _flat_prism, roof_seg, utility_pole
from pieces_b5 import _bell, _door_leaf, _fix_mirror, _frustum, _pot, _u_frame, ov_roller_shutter
from pieces_b6 import _arch_band, _checker, _octagon, _ribbed_dome, _voussoirs
from pieces_b7 import _bulb
from pieces_b8 import _grid
from pieces_marks import _beads, _corbel, _crest, _cumba_face, _diag, _hip, _lightbox, _off, _place, _ring


def _rot(k):
    return rot_y(90 * k)


def _laundry(m, x0, x1, y, z, n, slots=("fabric", "accent2", "trim", "accent")):
    """a sagging line along X with clothes pegged on it (two-sided quads)"""
    pts = [(x0 + (x1 - x0) * i / 6, y - 0.25 * math.sin(math.pi * i / 6), z) for i in range(7)]
    for a, c in zip(pts, pts[1:]):
        m.tube(a, c, 0.006, "frame", n=3)
    for k in range(n):
        f = (k + 0.5) / n
        x = x0 + (x1 - x0) * f
        yy = y - 0.25 * math.sin(math.pi * f)
        w, h = 0.18 + 0.1 * (k % 2), 0.35 + 0.2 * ((k * 7) % 3) / 2
        sl = slots[k % len(slots)]
        m.quad_facing((x - w / 2, yy, z), (x + w / 2, yy, z), (x + w / 2, yy - h, z), (x - w / 2, yy - h, z), (0, 0, 1), sl)
        m.quad_facing((x - w / 2, yy, z - 0.004), (x + w / 2, yy, z - 0.004), (x + w / 2, yy - h, z - 0.004), (x - w / 2, yy - h, z - 0.004), (0, 0, -1), sl, 0.85)


def _louvre_leaf(m, x0, y0, x1, y1, z, slot="accent", n=10, nrm=(0, 0, 1)):
    m.box((x0, y0, z - 0.03), (x1, y1, z), slot, 0.85)
    for j in range(n):
        y = y0 + 0.08 + (y1 - y0 - 0.16) * (j + 0.5) / n
        _strip(m, (x0 + 0.05, y, z + 0.004), (x1 - 0.05, y, z + 0.004), (y1 - y0) / n * 0.6, (0, 0.4, 1), slot)


# ------------------------------------------------------------------ Mardin (r3_mardin_terraces)
def wall_triple_arch_loggia():
    """MARDIN MARK: the triple-arched south loggia of an upper eyvan: three pointed arches the full storey on two slim
    columns, carved bands round the arches, a low carved stone balustrade"""
    def b():
        ops = [[(x + dx, y) for x, y in arch("pointed", 0.8, 2.75, 0.0, n=4)] for dx in (-0.95, 0.0, 0.95)]
        m = _wall(K, ops, reveal="trim")
        for o in ops:
            _arch_band(m, o, 0.1, -0.01, 0.035, "trim", 0.9)
        for x in (-0.475, 0.475):
            m.cyl(x, -0.3, 0.08, 0.0, 1.95, "trim", n=6, caps=False)
            m.box((x - 0.14, 1.95, -0.44), (x + 0.14, 2.1, -0.16), "trim", 0.85)
        m.box((-1.35, 0.0, -0.5), (1.35, 0.8, -0.4), "trim", 0.9, skip=("y-",))
        for k in range(6):
            x = -1.2 + k * 0.48
            m.quad_facing((x, 0.15, -0.395), (x + 0.3, 0.15, -0.395), (x + 0.3, 0.65, -0.395), (x, 0.65, -0.395), (0, 0, 1), "frame", 0.45)
            _diag(m, x, 0.15, x + 0.3, 0.65, -0.39, 0.12, 0.03, "trim")
        _beads(m, -HB, HB, ST - 0.2, ST - 0.08, 0.0, 0.04, 14, "trim", 0.85)
        return m
    return b


def edge_balustrade_carved():
    """MARDIN: the carved stone balustrade round a roof terrace: piers, panels of carved interlace (pierced, shown dark
    behind a lattice), a coping"""
    def b():
        m = Mesh()
        t = 0.25
        m.box((-HB, 0.0, -t), (HB, 0.15, 0.0), "wall", skip=("y-", "x-", "x+"))
        m.box((-HB, 0.85, -t - 0.03), (HB, 0.95, 0.03), "trim", skip=("x-", "x+"))
        for x in (-HB + 0.005, -0.04, HB - 0.085):
            m.box((x, 0.145, -t), (x + 0.08, 0.855, 0.0), "wall", 0.95, skip=("y-", "y+"))
        for x0 in (-1.415, 0.04):
            x1 = x0 + 1.37
            m.quad_facing((x0, 0.15, -t / 2), (x1, 0.15, -t / 2), (x1, 0.85, -t / 2), (x0, 0.85, -t / 2), (0, 0, 1), "frame", 0.35)
            m.quad_facing((x0, 0.15, -t / 2 - 0.004), (x1, 0.15, -t / 2 - 0.004), (x1, 0.85, -t / 2 - 0.004), (x0, 0.85, -t / 2 - 0.004), (0, 0, -1), "frame", 0.35)
            _diag(m, x0, 0.15, x1, 0.85, -t / 2 + 0.01, 0.22, 0.05, "trim")
        return m
    return b


def abbara_vault():
    """MARDIN MARK: the abbara -- a stone vault carrying a lane under a house (a cell along Z): the barrel overhead (seen
    from below, springing at 2.2 m), carved portal arches at both ends"""
    def b():
        m = Mesh()
        n = 8
        for k in range(n):
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            p0 = (HB * math.cos(a0), 2.2 + 0.9 * math.sin(a0))
            p1 = (HB * math.cos(a1), 2.2 + 0.9 * math.sin(a1))
            m.quad_facing((p0[0], p0[1], -HB), (p1[0], p1[1], -HB), (p1[0], p1[1], HB), (p0[0], p0[1], HB), (-math.cos((a0 + a1) / 2), -math.sin((a0 + a1) / 2), 0), "wall", 0.75)
        for s in (-1, 1):
            m.quad_facing((s * HB, 0.0, -HB), (s * HB, 0.0, HB), (s * HB, 2.2, HB), (s * HB, 2.2, -HB), (-s, 0, 0), "wall", 0.8)
        o = arch("pointed", 2.6, 3.0, 0.0, n=6)
        for z, sgn in ((-HB, -1), (HB, 1)):
            sub = Mesh()
            sub.wall_cut(_rect(-HB, 0.0, HB, ST), [o], -0.3, 0.0, "wall", reveal_slot="trim")
            _arch_band(sub, o, 0.12, -0.01, 0.04, "trim", 0.9)
            _place(m, sub, 0 if sgn > 0 else 180, dz=z + (0.0 if sgn > 0 else 0.0))
        return m
    return b


def wall_carved_frame():
    """MARDIN: a pointed window in a deeply carved stone frame (a bead band, an interlace band) with a geometric iron
    grille"""
    def b():
        o = arch("pointed", 0.8, 1.6, 0.9, n=6)
        m = _wall(K, [o])
        m.pane(-0.4, 0.9, 0.4, 2.5, -0.35)
        _diag(m, -0.38, 0.92, 0.38, 2.1, -0.12, 0.16, 0.025, "metal")
        _arch_band(m, o, 0.1, -0.01, 0.05, "trim", 0.95)
        _arch_band(m, _off(o, 0.1), 0.12, -0.01, 0.03, "trim", 0.8)
        m.box((-0.6, 0.72, 0.0), (0.6, 0.85, 0.1), "trim", 0.9, skip=("z-",))
        _beads(m, -0.6, 0.6, 0.74, 0.83, 0.1, 0.13, 8, "trim", 0.85)
        return m
    return b


def minaret_square_carved(part):
    """MARDIN MARK: the square carved Artuqid minaret, a cell a part: base (plain ashlar; stack), shaft (carved blind
    niches and bead bands), top (a balcony on corbels and a little ribbed dome)"""
    def b():
        m = Mesh()
        a = 1.2
        if part == "base":
            m.box((-a, 0.0, -a), (a, ST, a), "wall", skip=("y-", "y+"))
        elif part == "shaft":
            m.box((-a, 0.0, -a), (a, ST, a), "wall", skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                for dx in (0.0,):
                    o = [(x + dx, y) for x, y in arch("pointed", 0.9, 2.0, 0.5, n=4)]
                    sub.wall_cut(o, [], a, a + 0.008, "frame", 0.5)
                    _arch_band(sub, o, 0.08, a - 0.01, a + 0.04, "trim", 0.9)
                _beads(sub, -a, a, 2.75, 2.95, a, a + 0.05, 6, "trim", 0.85)
                sub.box((-a, 0.25, a - 0.01), (a, 0.35, a + 0.04), "trim", 0.85, skip=("z-", "x-", "x+"))
                m.add(sub, _rot(k))
        else:
            m.box((-a, 0.0, -a), (a, 0.6, a), "wall", skip=("y-",))
            for k in range(4):
                sub = Mesh()
                for x in (-0.8, 0.0, 0.8):
                    _corbel(sub, x, 0.6, 0.35, 0.4, 0.12, "trim", 0.85, z0=a)
                m.add(sub, _rot(k))
            m.box((-a - 0.35, 0.6, -a - 0.35), (a + 0.35, 0.72, a + 0.35), "trim", 0.9)
            for k in range(4):
                sub = Mesh()
                sub.box((-a - 0.35, 0.72, a + 0.27), (a + 0.35, 1.5, a + 0.35), "trim", 0.95, skip=("y-",))
                m.add(sub, _rot(k))
            m.cyl(0, 0, 0.7, 0.72, 2.2, "wall", n=8, caps=False)
            _ribbed_dome(m, 0.75, 2.2, 0.8, n=8, slot="trim")
        return m
    return b


# ------------------------------------------------------------------ Ottoman extras (r3_ottoman_timber)
def wall_cumba():
    """OTTOMAN MARK: the cumba alone -- a three-sided glazed oriel 0.6 m out of a plain storey on its brackets, a little
    hip roof"""
    def b():
        m = _wall(T, [_rect(-0.7, 0.15, 0.7, 2.95)])
        dz, wf = 0.6, 0.9
        ang = math.degrees(math.atan2(dz, 0.7 - wf / 2))
        side = math.hypot(dz, 0.7 - wf / 2)
        _place(m, _cumba_face(wf, 2.8, 0.15), 0.0, 0.0, 0.0, dz)
        for sgn in (-1, 1):
            _place(m, _cumba_face(side, 2.8, 0.15), sgn * ang, sgn * (0.7 + wf / 2) / 2, 0.0, dz / 2)
        plan = [(-0.7, 0.0), (0.7, 0.0), (wf / 2, dz), (-wf / 2, dz)]
        m.prism_xz(plan, 0.05, 0.15, "frame", 0.8)
        m.prism_xz(plan, 2.95, 3.05, "frame", 0.8)
        for x in (-0.45, 0.45):
            _corbel(m, x, 0.05, dz, 0.6, 0.12, "frame", 0.75)
        top = [(-0.85, 3.05, -0.1), (0.85, 3.05, -0.1), (wf / 2 + 0.15, 3.05, dz + 0.15), (-wf / 2 - 0.15, 3.05, dz + 0.15)]
        apex = [(-0.4, 3.3, 0.1), (0.4, 3.3, 0.1)]
        m.quad_facing(top[3], top[2], apex[1], apex[0], (0, 1, 1), "roof")
        m.tri_facing(top[0], top[3], apex[0], (-1, 1, 0), "roof", 0.9)
        m.tri_facing(top[1], top[2], apex[1], (1, 1, 0), "roof", 0.9)
        m.quad_facing(top[0], top[1], top[2], top[3], (0, -1, 0), "frame", 0.55)
        return m
    return b


def wall_kafes():
    """OTTOMAN: a pair of tall sash windows screened by kafes -- a diagonal timber lattice over their lower two thirds"""
    def b():
        ops = [(-1.15, 0.7, -0.35, 2.5), (0.35, 0.7, 1.15, 2.5)]
        m = _wall(T, [_rect(*o) for o in ops], reveal="frame")
        for x0, y0, x1, y1 in ops:
            m.pane(x0, y0, x1, y1, -0.15)
            _strip(m, (x0, 1.9, -0.13), (x1, 1.9, -0.13), 0.04, (0, 0, 1), "frame")
            m.quad_facing((x0 + 0.005, y0 + 0.005, -0.06), (x1 - 0.005, y0 + 0.005, -0.06), (x1 - 0.005, 1.85, -0.06), (x0 + 0.005, 1.85, -0.06), (0, 0, 1), "screen", 0.35)
            _diag(m, x0 + 0.005, y0 + 0.005, x1 - 0.005, 1.85, -0.05, 0.12, 0.025, "screen")
            m.box((x0 - 0.05, y0 - 0.06, 0.0), (x1 + 0.05, y0, 0.06), "trim", skip=("z-",))
        return m
    return b


def wall_himis():
    """OTTOMAN: the himis bay -- a timber frame (posts, rails, diagonal braces) proud of its plaster infill, a small window"""
    def b():
        m = _wall(T, [_rect(0.35, 1.0, 1.05, 2.1)])
        m.pane(0.35, 1.0, 1.05, 2.1, -0.12)
        for x in (-HB + 0.005, -0.2, 1.4):
            m.box((x, 0.005, 0.0), (x + 0.1, ST - 0.005, 0.05), "frame", skip=("z-",))
        for y in (0.005, 0.9, 2.15, ST - 0.105):
            m.box((-HB + 0.05, y, 0.0), (HB - 0.05, y + 0.1, 0.045), "frame", 0.9, skip=("z-",))
        for (a, c) in (((-1.4, 0.95), (-0.25, 2.1)), ((-1.4, 2.2), (-0.25, ST - 0.15)), ((0.25, 0.1), (1.35, 0.85))):
            _strip(m, (a[0], a[1], 0.03), (c[0], c[1], 0.03), 0.09, (0, 0, 1), "frame")
        return m
    return b


def eave_soffit_deep():
    """OTTOMAN: the deep eave (1.2 m) under a low hip, its soffit boarded and painted, a fascia (edge on the roof top)"""
    def b():
        m = Mesh()
        d = 1.2
        m.quad_facing((-HB, 0.55, -0.3), (HB, 0.55, -0.3), (HB, 0.05, d), (-HB, 0.05, d), (0, 1, 0.4), "roof")
        m.quad_facing((-HB, -0.1, 0.0), (HB, -0.1, 0.0), (HB, -0.1, d), (-HB, -0.1, d), (0, -1, 0), "trim", 0.75)
        for k in range(10):
            x = -HB + 0.15 + k * 0.3
            _strip(m, (x, -0.105, 0.02), (x, -0.105, d - 0.02), 0.03, (0, -1, 0), "frame")
        m.quad_facing((-HB, -0.1, d), (HB, -0.1, d), (HB, 0.05, d), (-HB, 0.05, d), (0, 0, 1), "frame", 0.85)
        return m
    return b


def cesme_fountain():
    """OTTOMAN: the cesme -- a marble wall fountain: a framed panel with an arched niche, a brass spout, an inscription
    band, a trough, a little canopy (face overlay)"""
    def b():
        m = Mesh()
        m.box((-0.8, 0.0, 0.0), (0.8, 2.4, 0.12), "trim", skip=("z-",))
        o = arch("pointed", 0.8, 1.4, 0.55, n=6)
        m.wall_cut(o, [], 0.12, 0.125, "trim", 0.75)
        _arch_band(m, o, 0.08, 0.11, 0.16, "trim", 0.9)
        m.box((-0.55, 2.05, 0.12), (0.55, 2.3, 0.15), "accent", skip=("z-",))
        for k in range(5):
            _strip(m, (-0.45 + k * 0.2, 2.1, 0.155), (-0.35 + k * 0.2, 2.25, 0.155), 0.04, (0, 0, 1), "accent2")
        m.tube((0.0, 1.0, 0.12), (0.0, 0.95, 0.3), 0.025, "metal", n=4)
        m.box((-0.75, 0.0, 0.12), (0.75, 0.5, 0.65), "trim", 0.9, skip=("y-", "z-"))
        m.quad_facing((-0.65, 0.42, 0.2), (0.65, 0.42, 0.2), (0.65, 0.42, 0.57), (-0.65, 0.42, 0.57), (0, 1, 0), "water")
        m.quad_facing((-0.95, 2.75, 0.0), (0.95, 2.75, 0.0), (0.95, 2.45, 0.6), (-0.95, 2.45, 0.6), (0, 1, 0.5), "roof")
        m.quad_facing((-0.95, 2.72, 0.0), (0.95, 2.72, 0.0), (0.95, 2.42, 0.6), (-0.95, 2.42, 0.6), (0, -1, -0.5), "frame", 0.6)
        return m
    return b


# ------------------------------------------------------------------ Matera (r3_rupestrian_terraces)
def vault_roof_hump():
    """MATERA: the whitewashed barrel vault hump over a rock-cut cell (cell roof along Z), a little chimney"""
    def b():
        m = Mesh()
        n = 8
        for k in range(n):
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            p0, p1 = (HB * math.cos(a0), 0.7 * math.sin(a0)), (HB * math.cos(a1), 0.7 * math.sin(a1))
            m.quad_facing((p0[0], p0[1], -HB), (p1[0], p1[1], -HB), (p1[0], p1[1], HB), (p0[0], p0[1], HB), (math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0), "trim", 0.95)
        end = [(-HB, 0.0), (HB, 0.0)] + [(HB * math.cos(math.pi * k / n), 0.7 * math.sin(math.pi * k / n)) for k in range(1, n)]
        _flat_prism(m, end, -HB, -HB + 0.01, "trim", 0.85, open_edges=tuple(range(len(end))))
        _flat_prism(m, end, HB - 0.01, HB, "trim", 0.85, open_edges=tuple(range(len(end))))
        m.box((0.6, 0.5, 0.4), (0.9, 1.2, 0.7), "trim", skip=("y-",))
        return m
    return b


def wall_cave_door():
    """MATERA MARK: the deep arched door into a rock-cut vault: a round arch in the tufa face, a lunette window over
    the door, the door deep in its reveal"""
    def b():
        o = arch("round", 1.6, 2.9, 0.0, n=8)
        m = _wall(K, [o], reveal="ground")
        m.box((-0.5, 0.0, -0.5), (0.5, 2.1, -0.45), "frame", 0.8)
        lun = [(-0.8, 2.1), (0.8, 2.1)] + [(0.8 * math.cos(math.pi * k / 8), 2.1 + 0.8 * math.sin(math.pi * k / 8)) for k in range(1, 8)]
        m.wall_cut(lun, [], -0.48, -0.44, "glass")
        for k in range(1, 4):
            a = math.pi * k / 4
            _strip(m, (0.0, 2.1, -0.43), (0.8 * math.cos(a), 2.1 + 0.8 * math.sin(a), -0.43), 0.03, (0, 0, 1), "frame")
        m.box((-0.8, 2.08, -0.5), (0.8, 2.14, -0.4), "frame", 0.9)
        _arch_band(m, o, 0.15, -0.01, 0.04, "ground", 0.9)
        return m
    return b


def rock_face_cut():
    """MATERA: the raw rock face the cells are cut into (a wall bay in the ground slot): faceted tufa, chisel-cut planes
    at random depths"""
    def b():
        m = Mesh()
        r = random.Random(5)
        nx, ny = 4, 4
        pts = {}
        for i in range(nx + 1):
            for j in range(ny + 1):
                jx = 0.0 if i in (0, nx) else r.uniform(-0.25, 0.25)
                jy = 0.0 if j in (0, ny) else r.uniform(-0.25, 0.25)
                dz = 0.0 if i in (0, nx) or j in (0, ny) else r.uniform(0.0, 0.18)
                pts[i, j] = (-HB + BAY * (i + jx) / nx, ST * (j + jy) / ny, dz)
        for i in range(nx):
            for j in range(ny):
                a, b_, c, d = pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]
                sh = 0.75 + 0.25 * r.random()
                m.tri_facing(a, b_, c, (0, 0, 1), "ground", sh)
                m.tri_facing(a, c, d, (0, 0, 1), "ground", sh * 0.93)
        m.quad_facing((-HB, 0.0, -K), (HB, 0.0, -K), (HB, ST, -K), (-HB, ST, -K), (0, 0, -1), "ground", 0.6)
        return m
    return b


def cistern_well():
    """MATERA: the vicinato's cistern well head -- a carved stone drum, a wrought-iron arch with its pulley"""
    def b():
        m = Mesh()
        m.lathe([(0.7, 0.0), (0.72, 0.75), (0.45, 0.8), (0.42, 0.65)], "trim", n=10)
        m.cyl(0, 0, 0.75, 0.0, 0.12, "trim", n=10, shade=0.85)
        pts = [(0.62 * math.cos(math.pi * k / 8), 0.8 + 1.0 * math.sin(math.pi * k / 8), 0.0) for k in range(9)]
        for a, c in zip(pts, pts[1:]):
            m.tube(a, c, 0.025, "metal", n=4)
        sub = Mesh()
        sub.cyl(0, 0, 0.12, -0.02, 0.02, "metal", n=8)
        m.add(sub, lambda p: (p[0], 1.65 + p[2], -p[1]))
        m.tube((0.12, 1.65, 0.0), (0.12, 0.9, 0.0), 0.008, "frame", n=3)
        return m
    return b


def lemon_pergola():
    """MATERA / AMALFI: a lemon and vine pergola on posts over a roof terrace: chestnut poles, cross poles, leaves, lemons"""
    def b():
        m = Mesh()
        for x in (-1.3, 1.3):
            for z in (-1.3, 1.3):
                m.cyl(x, z, 0.05, 0.0, 2.4, "frame", n=4, caps=False)
        for z in (-1.3, 0.0, 1.3):
            m.tube((-1.45, 2.4, z), (1.45, 2.4, z), 0.04, "frame", n=4)
        for x in (-0.9, -0.3, 0.3, 0.9):
            m.tube((x, 2.45, -1.45), (x, 2.45, 1.45), 0.03, "frame", n=3)
        r = random.Random(3)
        for k in range(9):
            x, z = r.uniform(-1.2, 1.2), r.uniform(-1.2, 1.2)
            s = r.uniform(0.35, 0.55)
            m.quad_facing((x - s, 2.5, z - s), (x + s, 2.52, z - s), (x + s, 2.5, z + s), (x - s, 2.48, z + s), (0, 1, 0), "plant", 0.85 + 0.15 * r.random())
            m.quad_facing((x - s, 2.495, z - s), (x + s, 2.515, z - s), (x + s, 2.495, z + s), (x - s, 2.475, z + s), (0, -1, 0), "plant", 0.6)
        for k in range(10):
            x, z = r.uniform(-1.2, 1.2), r.uniform(-1.2, 1.2)
            m.box((x - 0.05, 2.33, z - 0.05), (x + 0.05, 2.43, z + 0.05), "accent2")
        return m
    return b


# ------------------------------------------------------------------ Edinburgh (r3_scots_lands)
def chimney_stack_pots():
    """SCOTS MARK: the many-pot chimney stack on a gable: a long rubble stack, a moulded cope, a row of clay pots"""
    def b():
        m = Mesh()
        m.box((-0.95, 0.0, -0.35), (0.95, 1.4, 0.35), "wall", skip=("y-",))
        m.box((-1.0, 1.4, -0.4), (1.0, 1.52, 0.4), "trim", 0.9)
        for k in range(6):
            x = -0.75 + k * 0.3
            m.lathe([(0.11, 1.52), (0.09, 1.75), (0.1, 1.9), (0.07, 1.95)], "accent", n=6, cx=x, shade=0.9 + 0.1 * (k % 2))
        return m
    return b


def turret_stair(part):
    """SCOTS MARK: the turnpike stair turret at a corner (a corner piece: its drum centred on the cell's vertical edge):
    shaft (a storey of drum with a slit window; stack it), cap (a conical slate cap with a finial)"""
    def b():
        m = Mesh()
        r = 0.85
        if part == "shaft":
            m.cyl(0.25, 0.25, r, 0.0, ST, "wall", n=10, caps=False)
            sub = Mesh()
            sub.quad_facing((-0.05, 1.3, 0.0), (0.05, 1.3, 0.0), (0.05, 1.9, 0.0), (-0.05, 1.9, 0.0), (0, 0, 1), "frame", 0.35)
            _place(m, sub, 45, dx=0.25 + r * 0.707, dz=0.25 + r * 0.707)
        else:
            m.cyl(0.25, 0.25, r, 0.0, 0.5, "wall", n=10, caps=False)
            m.cyl(0.25, 0.25, r + 0.06, 0.5, 0.6, "trim", n=10, shade=0.9)
            m.lathe([(r + 0.1, 0.6), (0.0, 3.2)], "roof", n=10, cx=0.25, cz=0.25)
            m.lathe([(0.0, 3.1), (0.06, 3.2), (0.0, 3.6)], "metal", n=5, cx=0.25, cz=0.25)
        return m
    return b


def wall_pend():
    """SCOTS: the pend -- the arched passage taking a close in under a land: a round arch with dressed voussoirs, a
    carved lintel panel with the close's name"""
    def b():
        o = arch("round", 1.8, 2.7, 0.0, n=8)
        m = _wall(K, [o], reveal="trim")
        _voussoirs(m, o, 0.03, 10, "trim", "wall", w=0.2)
        _arch_band(m, o, 0.2, -0.01, 0.025, "trim", 0.9)
        m.box((-0.6, 2.85, 0.0), (0.6, 3.12, 0.04), "accent", skip=("z-",))
        for k in range(5):
            _strip(m, (-0.45 + k * 0.22, 2.92, 0.045), (-0.35 + k * 0.22, 3.05, 0.045), 0.04, (0, 0, 1), "trim")
        return m
    return b


def crown_spire():
    """SCOTS MARK: St Giles' crown spire (crown on a tower's top cell): a parapet with corner pinnacles, eight flying
    ribs rising from the corners and sides to a central lantern and its needle"""
    def b():
        m = Mesh()
        a = 1.3
        m.box((-a, 0.0, -a), (a, 0.6, a), "wall", skip=("y-",))
        for x in (-a, a):
            for z in (-a, a):
                _frustum(m, 0.14, 0.02, 0.6, 2.0, "wall", 0.95, cx=x, cz=z)
        top = (0.0, 4.0, 0.0)
        starts = [(x, 0.6, z) for x in (-a + 0.1, a - 0.1) for z in (-a + 0.1, a - 0.1)] + [(0.0, 0.6, a - 0.1), (0.0, 0.6, -a + 0.1), (a - 0.1, 0.6, 0.0), (-a + 0.1, 0.6, 0.0)]
        for s in starts:
            prev = s
            for k in range(1, 7):
                t = k / 6
                p = (s[0] * (1 - t), 0.6 + (top[1] - 0.6) * math.sin(t * math.pi / 2), s[2] * (1 - t))
                m.tube(prev, p, 0.07, "wall", n=4)
                prev = p
        m.box((-0.35, 3.9, -0.35), (0.35, 4.6, 0.35), "wall", 0.95)
        _frustum(m, 0.3, 0.02, 4.6, 6.6, "wall", 0.9)
        return m
    return b


def mercat_cross():
    """SCOTS: the mercat cross -- an octagonal drum with a parapet, its shaft and the unicorn on top (cell decor)"""
    def b():
        m = Mesh()
        m.prism_xz(_octagon(1.3), 0.0, 1.6, "wall")
        m.prism_xz(_octagon(1.38), 1.6, 1.75, "trim", 0.9)
        for k in range(8):
            a = math.tau * (k + 0.5) / 8
            sub = Mesh()
            o = arch("round", 0.5, 1.0, 0.3, n=4)
            sub.wall_cut(o, [], 0.0, 0.01, "frame", 0.5)
            _place(m, sub, math.degrees(a) + 90, dx=1.205 * math.cos(a), dz=-1.205 * math.sin(a))
        m.cyl(0, 0, 0.14, 1.75, 5.2, "trim", n=8, caps=False)
        m.box((-0.2, 5.2, -0.12), (0.2, 5.5, 0.12), "accent2")
        m.box((-0.05, 5.45, 0.1), (0.05, 5.55, 0.35), "accent2", 0.9)
        m.tube((0.0, 5.55, 0.1), (0.0, 5.8, 0.25), 0.02, "accent2", n=3)
        return m
    return b


# ------------------------------------------------------------------ Siam extras
def pier_steps_khlong():
    """SIAM: the timber pier and steps from a stilt house down into the canal (stair, water side): a landing on posts,
    steps down 2 m along +Z, a handrail"""
    def b():
        m = Mesh()
        m.box((-0.8, -0.1, -HB), (0.8, 0.0, -0.4), "frame", 0.85)
        for k in range(9):
            z0 = -0.4 + k * 0.22
            y = -0.22 * (k + 1)
            m.box((-0.7, y - 0.05, z0), (0.7, y, z0 + 0.25), "frame", 0.8 + 0.1 * (k % 2))
        for x in (-0.75, 0.75):
            m.tube((x, 0.9, -0.4), (x, -1.1, 1.6), 0.025, "frame", n=3)
            for z, y in ((-0.4, 0.0), (0.6, -1.0), (1.6, -2.0)):
                m.tube((x, y - 0.6, z), (x, y + 0.9, z), 0.05, "frame", n=4)
        for x in (-0.75, 0.75):
            for z in (-1.4, -0.45):
                m.tube((x, -2.5, z), (x, -0.1, z), 0.06, "frame", n=4)
        return m
    return b


def ov_gold_shop_neon():
    """SIAM MARK: the big vertical gold-shop sign of Yaowarat -- a tall red lit board standing out from the face, gold
    characters both sides, two storeys (face overlay, faces +-X)"""
    def b():
        m = Mesh()
        sub = Mesh()
        _lightbox(sub, 0.25, 0.3, 1.15, 6.0, -0.12, 0.12, nchar=5, vertical=True)
        mir = Mesh()
        mir.add(sub, lambda p: (p[2] + 1.0, p[1], p[0]))
        m.add(_fix_mirror(mir))
        for y in (1.0, 3.5, 5.6):
            m.box((0.95, y, 0.0), (1.05, y + 0.1, 0.3), "metal", skip=("z-",))
        for k in range(6):
            y = 0.6 + k * 0.92
            _strip(m, (1.125, y, 0.3), (1.125, y + 0.5, 1.1), 0.06, (1, 0, 0), "accent2")
            _strip(m, (0.875, y, 0.3), (0.875, y + 0.5, 1.1), 0.06, (-1, 0, 0), "accent2")
        return m
    return b


# ------------------------------------------------------------------ Straits (r2_straits_shophouse)
def wall_five_foot_way():
    """STRAITS MARK: the shophouse ground bay with its covered five-foot way: the column at the street edge (the bay's
    right end), the way 1.6 m deep with Peranakan floor tiles, the shopfront at its back with pintu pagar half-doors"""
    def b():
        m = Mesh()
        dz = -1.6
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.1, 0.0, 1.1, 2.7)], dz - T, dz, "wall", reveal_slot="trim")
        m.box((-1.095, 0.0, dz - 0.15), (1.095, 2.695, dz - 0.11), "frame", 0.8)
        for x0 in (-0.9, 0.0):                                                  # the pintu pagar
            m.box((x0 + 0.02, 0.4, dz + 0.02), (x0 + 0.88, 1.55, dz + 0.06), "accent", 0.95)
            for j in range(3):
                m.quad_facing((x0 + 0.1, 0.55 + j * 0.33, dz + 0.065), (x0 + 0.8, 0.55 + j * 0.33, dz + 0.065), (x0 + 0.8, 0.8 + j * 0.33, dz + 0.065), (x0 + 0.1, 0.8 + j * 0.33, dz + 0.065), (0, 0, 1), "accent2")
        m.box((-0.9, 2.75, dz + 0.005), (0.9, 3.05, dz + 0.08), "accent", skip=("z-",))
        for i in range(10):
            for j in range(5):
                x, z = -HB + i * 0.3 + 0.01, dz + j * 0.32 + 0.01
                m.quad_facing((x, 0.005, z), (x + 0.28, 0.005, z), (x + 0.28, 0.005, z + 0.3), (x, 0.005, z + 0.3), (0, 1, 0), "tile" if (i + j) % 2 else "trim", 0.95)
        m.box((-HB, ST - 0.3, dz), (HB, ST, 0.0), "trim", 0.9, skip=("z-", "x-", "x+", "y+"))
        m.box((1.1, 0.0, -0.4), (1.5, ST - 0.3, 0.0), "trim", skip=("y-", "y+"))
        m.box((1.06, 0.0, -0.44), (1.54, 0.35, 0.04), "wall", 0.85, skip=("y-",))
        m.box((1.06, ST - 0.55, -0.44), (1.54, ST - 0.3, 0.04), "wall", 0.9)
        return m
    return b


def wall_casement_louvre():
    """STRAITS: the upper storey's three full-height timber casements with louvred panels, open, in a stucco frame with
    a little balustrade"""
    def b():
        ops = [(-1.25, 0.3, -0.55, 2.6), (-0.35, 0.3, 0.35, 2.6), (0.55, 0.3, 1.25, 2.6)]
        m = _wall(T, [_rect(*o) for o in ops], reveal="trim")
        for x0, y0, x1, y1 in ops:
            m.pane(x0, y0, x1, y1, -0.18)
            for s, xh in ((-1, x0), (1, x1)):
                xa, xb = (xh - 0.34, xh - 0.02) if s < 0 else (xh + 0.02, xh + 0.34)
                _louvre_leaf(m, xa, y0 + 0.005, xb, y1 - 0.005, 0.035, "accent", n=12)
            _ring(m, x0, y0, x1, y1, 0.06, 0.0, 0.04, "trim")
        m.box((-HB, ST - 0.2, 0.0), (HB, ST - 0.005, 0.12), "trim", 0.9, skip=("z-",))
        return m
    return b


def band_peranakan_tile():
    """STRAITS MARK: the glazed Peranakan tile dado (face overlay, 1 m): rows of square tiles, each with a flower set in
    a two-colour field, a border line"""
    def b():
        m = Mesh()
        for i in range(10):
            for j in range(3):
                x, y = -HB + i * 0.3 + 0.01, 0.08 + j * 0.3
                m.quad_facing((x, y, 0.008), (x + 0.28, y, 0.008), (x + 0.28, y + 0.28, 0.008), (x, y + 0.28, 0.008), (0, 0, 1), "tile")
                cx, cy = x + 0.14, y + 0.14
                m.quad_facing((cx, cy - 0.1, 0.011), (cx + 0.1, cy, 0.011), (cx, cy + 0.1, 0.011), (cx - 0.1, cy, 0.011), (0, 0, 1), "accent" if (i + j) % 2 else "accent2")
        m.box((-HB, 0.98, 0.0), (HB, 1.03, 0.015), "trim", skip=("z-", "x-", "x+"))
        return m
    return b


def edge_firewall_gable_straits():
    """STRAITS: the gable firewall between two units, standing on the roof above the party wall (edge): the wall's top
    rises in a curved 'wind and fire' outline over the roof slopes"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.35)]
        for k in range(1, 8):
            t = k / 8
            p.append((HB - BAY / 2 * t, 0.35 + 1.4 * t + 0.25 * math.sin(t * math.pi * 3)))
        p += [(0.0, 2.0)]
        for k in range(7, 0, -1):
            t = k / 8
            p.append((-(HB - BAY / 2 * t), 0.35 + 1.4 * t + 0.25 * math.sin(t * math.pi * 3)))
        p += [(-HB, 0.35)]
        _flat_prism(m, p, -0.25, 0.0, "wall", open_edges=(0,))
        ring = [q for q in p[2:]]
        for a, c in zip(ring, ring[1:]):
            _strip(m, (a[0], a[1] - 0.04, 0.004), (c[0], c[1] - 0.04, 0.004), 0.08, (0, 0, 1), "trim")
        return m
    return b


def temple_chinese_roof():
    """STRAITS MARK: the Chinese temple roof (crown on a cell): two eaves, the swallowtail ridge splitting and curling
    up at both ends, porcelain-shard dragons on the ridge, a pearl"""
    def b():
        m = Mesh()
        _hip(m, 2.1, 1.2, 0.0, 0.7, lift=0.35, flare=0.2, body=1.4, cap=True)
        m.box((-1.0, 0.7, -1.0), (1.0, 1.3, 1.0), "wall", skip=("y-", "y+"))
        _hip(m, 1.6, 0.25, 1.3, 2.3, lift=0.25, flare=0.15, body=1.0, cap=False)
        m.box((-1.0, 2.2, -0.1), (1.0, 2.45, 0.1), "roof", 0.8)
        for s in (-1, 1):                                                       # swallowtails
            for dz in (-0.1, 0.1):
                m.tube((s * 1.0, 2.35, dz), (s * 1.45, 2.65, dz * 3), 0.06, "roof", n=4)
                m.tube((s * 1.45, 2.65, dz * 3), (s * 1.6, 3.0, dz * 4), 0.045, "roof", n=4)
        for s in (-1, 1):                                                       # dragons on the ridge
            prev = (s * 0.9, 2.45, 0.0)
            for k in range(1, 6):
                p = (s * (0.9 - 0.15 * k), 2.6 + 0.12 * math.sin(k * 1.4), 0.0)
                m.tube(prev, p, 0.05, "accent", n=4)
                prev = p
        m.lathe([(0.0, 2.45), (0.12, 2.6), (0.0, 2.75)], "accent2", n=6)
        return m
    return b


# ------------------------------------------------------------------ Lhasa (r2_tibetan_lhasa)
def wall_battered():
    """TIBET: the battered whitewashed stone bay: its face leaning back 0.35 m over the storey (stack them: each storey
    starts flush again, as the old houses step in)"""
    def b():
        m = Mesh()
        lean = 0.35
        m.quad_facing((-HB, 0.0, 0.0), (HB, 0.0, 0.0), (HB, ST, -lean), (-HB, ST, -lean), (0, 0.1, 1), "wall")
        for s in (-1, 1):
            m.quad_facing((s * HB, 0.0, -K), (s * HB, 0.0, 0.0), (s * HB, ST, -lean), (s * HB, ST, -K), (s, 0, 0), "wall", 0.9)
        m.quad_facing((-HB, ST, -K), (HB, ST, -K), (HB, ST, -lean), (-HB, ST, -lean), (0, 1, 0), "wall", 0.85)
        m.quad_facing((-HB, 0.0, -K), (HB, 0.0, -K), (HB, ST, -K), (-HB, ST, -K), (0, 0, -1), "wall", 0.8)
        return m
    return b


def wall_window_trapezoid():
    """TIBET MARK: the window in its black trapezoid surround (wider at the foot), tiered painted lintels stepping out
    above it, a pleated cloth valance, a white face around"""
    def b():
        x0, y0, x1, y1 = -0.45, 1.0, 0.45, 2.1
        m = _wall(K, [_rect(x0, y0, x1, y1)], reveal="frame")
        m.pane(x0, y0, x1, y1, -0.3)
        _grid(m, x0, y0, x1, y1, -0.28, 3, 3, 0.03, "accent")
        trap = [(-0.85, y0 - 0.25), (0.85, y0 - 0.25), (0.6, y1 + 0.1), (-0.6, y1 + 0.1)]
        from shapely.geometry import Polygon
        g = Polygon(trap).difference(Polygon(_rect(x0 - 0.005, y0 - 0.005, x1 + 0.005, y1 + 0.005)))
        m.wall_cut(_dedupe([tuple(p) for p in list(g.exterior.coords)[:-1]]), [_dedupe([tuple(p) for p in list(h.coords)[:-1]]) for h in g.interiors], -0.01, 0.015, "frame", 0.5)
        for k in range(3):                                                    # the tiered lintels
            w = 0.6 + 0.08 * k
            y = y1 + 0.12 + k * 0.1
            m.box((-w, y, 0.0), (w, y + 0.09, 0.08 + 0.06 * k), ("accent", "accent2", "fabric")[k], skip=("z-",))
            _beads(m, -w, w, y + 0.01, y + 0.08, 0.08 + 0.06 * k, 0.1 + 0.06 * k, 10, ("accent2", "accent", "trim")[k], 0.9)
        for k in range(10):                                                   # the pleated valance
            x = x0 + (x1 - x0) * k / 10
            m.quad_facing((x, y1 + 0.1, 0.05 + 0.03 * (k % 2)), (x + 0.09, y1 + 0.1, 0.05 + 0.03 * ((k + 1) % 2)), (x + 0.09, y1 - 0.15, 0.05 + 0.03 * ((k + 1) % 2)), (x, y1 - 0.15, 0.05 + 0.03 * (k % 2)), (0, 0, 1), "fabric", 0.9 + 0.1 * (k % 2))
        return m
    return b


def edge_pembe_frieze():
    """TIBET MARK: the pembe frieze -- the deep maroon band of stacked tamarisk twigs under a parapet, set with gilt
    medallions (edge band: y 0..0.6 under the parapet line, on the face)"""
    def b():
        m = Mesh()
        m.box((-HB, -0.65, 0.0), (HB, 0.0, 0.08), "accent", skip=("z-", "x-", "x+"))
        for k in range(30):
            x = -HB + 0.05 + k * 0.1
            _strip(m, (x, -0.62, 0.084), (x, -0.03, 0.084), 0.02, (0, 0, 1), "accent")
        for x in (-0.9, 0.9):
            m.wall_cut([(x + 0.16 * math.cos(math.tau * k / 8), -0.32 + 0.16 * math.sin(math.tau * k / 8)) for k in range(8)], [], 0.08, 0.11, "accent2")
        m.box((-HB, -0.71, -0.02), (HB, -0.65, 0.12), "trim", 0.9, skip=("x-", "x+"))
        return m
    return b


def ov_prayer_flag_pole():
    """TIBET: the prayer-flag pole at a roof corner (corner decor): a tall pole wrapped in a long vertical flag, a
    juniper-sprig top"""
    def b():
        m = Mesh()
        m.box((0.05, 0.0, 0.05), (0.45, 0.3, 0.45), "trim", 0.85, skip=("y-",))
        m.cyl(0.25, 0.25, 0.04, 0.3, 4.5, "frame", n=4)
        for k, sl in enumerate(("accent", "accent2", "fabric", "trim", "tile")):
            y0 = 1.2 + k * 0.6
            m.quad_facing((0.29, y0, 0.25), (0.29, y0 + 0.55, 0.25), (0.29, y0 + 0.55, 0.85), (0.29, y0, 0.85), (1, 0, 0), sl)
            m.quad_facing((0.285, y0, 0.25), (0.285, y0 + 0.55, 0.25), (0.285, y0 + 0.55, 0.85), (0.285, y0, 0.85), (-1, 0, 0), sl, 0.85)
        m.cyl(0.25, 0.25, 0.15, 4.5, 4.8, "plant", n=5, r1=0.0)
        return m
    return b


def incense_burner():
    """TIBET: the big whitewashed sang-khang incense burner on the kora: a stepped base, the stove with its fire mouth,
    a chimney"""
    def b():
        m = Mesh()
        m.box((-0.9, 0.0, -0.9), (0.9, 0.3, 0.9), "trim", 0.85, skip=("y-",))
        m.lathe([(0.75, 0.3), (0.7, 1.2), (0.5, 1.5), (0.3, 1.6)], "trim", n=8)
        m.cyl(0, 0, 0.18, 1.55, 2.7, "trim", n=6)
        m.quad_facing((-0.2, 0.5, 0.715), (0.2, 0.5, 0.715), (0.2, 0.85, 0.705), (-0.2, 0.85, 0.705), (0, 0, 1), "emissive", 0.8)
        m.lathe([(0.25, 2.7), (0.0, 2.95)], "accent2", n=6)
        return m
    return b


def roof_gilded_temple():
    """TIBET MARK: the gilded temple roof (Jokhang) as a crown: a gilt hip roof with its corners swept up, the gyaltsen
    victory banners (gilt cylinders) at the corners, a gilt ganjira finial"""
    def b():
        m = Mesh()
        m.box((-1.2, 0.0, -1.2), (1.2, 0.8, 1.2), "accent", skip=("y-", "y+"))
        _hip(m, 1.9, 0.5, 0.8, 1.9, lift=0.4, flare=0.2, body=1.2, cap=True, slot="accent2", under="accent")
        for x in (-1.25, 1.25):
            for z in (-1.25, 1.25):
                m.lathe([(0.0, 0.8), (0.12, 0.85), (0.14, 1.25), (0.08, 1.4), (0.0, 1.55)], "accent2", n=6, cx=x, cz=z)
        m.lathe([(0.0, 1.9), (0.2, 1.95), (0.25, 2.2), (0.12, 2.45), (0.15, 2.6), (0.0, 2.95)], "accent2", n=8)
        return m
    return b


# ------------------------------------------------------------------ Naples / Amalfi (r3_tyrrhenian_canyon)
def wall_basso():
    """NAPLES MARK: the basso -- a glazed street door into a one-room home (the door is its window), a lace curtain, a
    chair set out by the door"""
    def b():
        m = _wall(T, [_rect(-0.6, 0.0, 0.6, 2.4)], reveal="frame")
        m.pane(-0.6, 0.0, 0.6, 2.4, -0.16)
        _grid(m, -0.6, 0.0, 0.6, 2.4, -0.14, 2, 4, 0.05, "accent")
        m.quad_facing((-0.55, 0.9, -0.17), (0.55, 0.9, -0.17), (0.55, 2.3, -0.17), (-0.55, 2.3, -0.17), (0, 0, 1), "trim", 0.9)
        _u_frame(m, -0.6, 2.4, 0.6, 0.1, 0.0, 0.03, "trim")
        m.box((0.85, 0.42, 0.35), (1.25, 0.46, 0.75), "accent2")
        for x in (0.87, 1.23):
            for z in (0.37, 0.73):
                m.box((x - 0.02, 0.0, z - 0.02), (x + 0.02, 0.42, z + 0.02), "accent2", 0.85)
        m.box((0.85, 0.46, 0.35), (1.25, 0.95, 0.39), "accent2", 0.9)
        return m
    return b


def ov_wall_shrine():
    """NAPLES MARK: the edicola -- a wall shrine: a framed painted image under a little canopy, a lamp, plastic flowers
    and a votive shelf (face overlay, lit)"""
    def b():
        m = Mesh()
        m.box((-0.5, 1.5, 0.0), (0.5, 2.6, 0.12), "trim", skip=("z-",))
        m.quad_facing((-0.35, 1.65, 0.125), (0.35, 1.65, 0.125), (0.35, 2.45, 0.125), (-0.35, 2.45, 0.125), (0, 0, 1), "accent")
        m.quad_facing((-0.15, 1.85, 0.13), (0.15, 1.85, 0.13), (0.15, 2.3, 0.13), (-0.15, 2.3, 0.13), (0, 0, 1), "accent2")
        m.quad_facing((-0.6, 2.85, 0.0), (0.6, 2.85, 0.0), (0.6, 2.6, 0.35), (-0.6, 2.6, 0.35), (0, 1, 0.5), "roof")
        m.quad_facing((-0.6, 2.82, 0.0), (0.6, 2.82, 0.0), (0.6, 2.57, 0.35), (-0.6, 2.57, 0.35), (0, -1, -0.5), "trim", 0.6)
        m.box((-0.55, 1.35, 0.0), (0.55, 1.5, 0.3), "trim", 0.9, skip=("z-",))
        m.box((-0.06, 2.5, 0.15), (0.06, 2.62, 0.27), "emissive")
        for k, x in enumerate((-0.4, -0.25, 0.25, 0.4)):
            m.cyl(x, 0.18, 0.05, 1.5, 1.62, "trim", n=5)
            m.box((x - 0.06, 1.62, 0.12), (x + 0.06, 1.75, 0.24), "fabric" if k % 2 else "accent2")
        m.box((-0.03, 1.5, 0.12), (0.03, 1.6, 0.18), "emissive")
        return m
    return b


def wall_french_balcony():
    """NAPLES / AMALFI: the tall french window with green louvred shutters folded back and a shallow iron balcony"""
    def b():
        x0, y0, x1, y1 = -0.55, 0.0, 0.55, 2.6
        m = _wall(K, [_rect(x0, y0, x1, y1)], reveal="trim")
        m.pane(x0, y0, x1, y1, -0.3)
        _grid(m, x0, y0, x1, y1, -0.28, 2, 4, 0.04, "trim")
        for xa, xb in ((x0 - 0.58, x0 - 0.02), (x1 + 0.02, x1 + 0.58)):
            _louvre_leaf(m, xa, y0 + 0.05, xb, y1, 0.04, "accent", n=12)
        _u_frame(m, x0, y1, x1, 0.12, 0.0, 0.035, "trim")
        d = 0.35
        m.box((x0 - 0.2, -0.08, 0.004), (x1 + 0.2, 0.0, d), "trim", 0.9, skip=("z-",))
        m.box((x0 - 0.2, 0.98, 0.0), (x1 + 0.2, 1.02, d), "metal", 0.8)
        for k in range(9):
            x = x0 - 0.15 + (x1 - x0 + 0.3) * k / 8
            _strip(m, (x, 0.0, d - 0.01), (x, 0.98, d - 0.01), 0.02, (0, 0, 1), "metal")
        return m
    return b


def ov_laundry_line_lane():
    """NAPLES MARK: laundry lines strung across a vicolo between opposite balconies (along X), sheets and shirts"""
    def b():
        m = Mesh()
        _laundry(m, -HB, HB, 5.2, -0.5, 6)
        _laundry(m, -HB, HB, 7.6, 0.6, 5)
        return m
    return b


def band_damp():
    """NAPLES: the dark damp band rising 0-1.5 m up the ground storey, its top edge uneven (face overlay)"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 1.2)] + [(HB - BAY * i / 8, 1.3 + 0.2 * math.sin(i * 1.7)) for i in range(1, 8)] + [(-HB, 1.4)]
        m.wall_cut(p, [], 0.0, 0.006, "wall", 0.6)
        return m
    return b


# ------------------------------------------------------------------ Hanoi (r2_viet_tube)
def wall_french_door_balcony():
    """VIET MARK: the tube house's upper storey: full-height french doors with louvred shutters opening onto a narrow
    balcony crowded with pots, an iron railing, a little pent awning"""
    def b():
        x0, y0, x1, y1 = -0.75, 0.0, 0.75, 2.5
        m = _wall(T, [_rect(x0, y0, x1, y1)], reveal="frame")
        m.pane(x0, y0, x1, y1, -0.14)
        for xa, xb in ((x0 - 0.75, x0 - 0.02), (x1 + 0.02, x1 + 0.75)):
            _louvre_leaf(m, xa, 0.05, xb, y1, 0.04, "accent", n=12)
        d = 0.7
        m.box((-HB, -0.12, 0.004), (HB, 0.0, d), "trim", 0.85, skip=("z-",))
        m.box((-HB, 0.98, d - 0.04), (HB, 1.02, d), "metal", 0.8)
        for k in range(13):
            x = -HB + 0.12 + k * 0.23
            _strip(m, (x, 0.0, d - 0.02), (x, 0.98, d - 0.02), 0.02, (0, 0, 1), "metal")
        for x in (-1.2, -0.5, 0.3, 1.0):
            _pot(m, x, 0.0, 0.4, r=0.13, h=0.22, slot="tile")
        m.quad_facing((-HB, 2.95, 0.0), (HB, 2.95, 0.0), (HB, 2.7, d + 0.15), (-HB, 2.7, d + 0.15), (0, 1, 0.3), "metal")
        m.quad_facing((-HB, 2.93, 0.0), (HB, 2.93, 0.0), (HB, 2.68, d + 0.15), (-HB, 2.68, d + 0.15), (0, -1, -0.3), "metal", 0.6)
        return m
    return b


def ov_wire_tangle():
    """VIET MARK: the knotted wire tangle on a street pole (cell decor): the pole, a great snarl of looping cables at
    the crossarm, drooping runs off to every side"""
    def b():
        m = utility_pole()()
        r = random.Random(9)
        cx, cy = 0.0, 6.9
        prev = (cx, cy, 0.0)
        for k in range(26):
            p = (cx + r.uniform(-0.55, 0.55), cy + r.uniform(-0.5, 0.4), r.uniform(-0.45, 0.45))
            m.tube(prev, p, 0.018, "frame", n=3)
            prev = p
        for a in range(6):
            ang = math.tau * a / 6
            m.tube((cx, cy, 0.0), (1.5 * math.cos(ang), cy - 0.6, 1.5 * math.sin(ang)), 0.015, "frame", n=3)
        return m
    return b


def wall_side_ad():
    """VIET: a painted advertisement on a blank side wall: a big colour field, a product shape, lettering"""
    def b():
        m = _wall(T)
        z = 0.006
        m.wall_cut(_rect(-1.3, 0.4, 1.3, 2.9), [], 0.0, z, "accent")
        m.wall_cut(_rect(-1.2, 2.2, 1.2, 2.8), [], z, z * 2, "accent2")
        for k in range(8):
            x = -1.1 + k * 0.28
            _strip(m, (x, 2.3, z * 2 + 0.002), (x + 0.12, 2.7, z * 2 + 0.002), 0.06, (0, 0, 1), "frame")
        bottle = [(0.3, 0.6), (0.8, 0.6), (0.8, 1.6), (0.65, 1.8), (0.65, 2.05), (0.45, 2.05), (0.45, 1.8), (0.3, 1.6)]
        m.wall_cut(bottle, [], z, z * 2, "fabric")
        for k in range(4):
            _strip(m, (-1.1, 0.8 + k * 0.3, z * 2 + 0.002), (-0.1, 0.8 + k * 0.3, z * 2 + 0.002), 0.1, (0, 0, 1), "trim")
        return m
    return b


def ov_roof_shrine():
    """VIET: the small rooftop ancestor shrine (roof decor): a red-painted little house on a stand, lit inside, its
    curled roof, incense sticks"""
    def b():
        m = Mesh()
        m.box((-0.3, 0.0, -0.3), (0.3, 0.8, 0.3), "trim", 0.85, skip=("y-",))
        m.box((-0.4, 0.8, -0.35), (0.4, 1.3, 0.35), "accent", skip=())
        m.quad_facing((-0.32, 0.88, 0.355), (0.32, 0.88, 0.355), (0.32, 1.22, 0.355), (-0.32, 1.22, 0.355), (0, 0, 1), "emissive", 0.9)
        for s in (-1, 1):
            m.quad_facing((s * 0.55, 1.25, -0.5), (s * 0.55, 1.25, 0.5), (0.0, 1.55, 0.5), (0.0, 1.55, -0.5), (s, 1, 0), "roof")
            m.tube((s * 0.55, 1.25, 0.5), (s * 0.7, 1.4, 0.55), 0.02, "roof", n=3)
        for x in (-0.06, 0.0, 0.06):
            m.tube((x, 0.8, 0.45), (x, 1.0, 0.45), 0.005, "accent2", n=3)
        return m
    return b


def bridge_red_lake():
    """VIET MARK: the red wooden bridge to the lake island (The Huc) over three cells along +Z (span [1, 3]): an arched
    plank deck on posts, red railings with posts"""
    def b():
        m = Mesh()
        L, n, w = 9.0, 10, 1.1
        zs = [-HB + L * i / n for i in range(n + 1)]
        ys = [0.9 * math.sin(math.pi * i / n) for i in range(n + 1)]
        for i in range(n):
            za, zb, ya, yb = zs[i], zs[i + 1], ys[i], ys[i + 1]
            m.quad_facing((-w, ya, za), (w, ya, za), (w, yb, zb), (-w, yb, zb), (0, 1, 0), "frame", 0.9 + 0.1 * (i % 2))
            m.quad_facing((-w, ya - 0.12, za), (w, ya - 0.12, za), (w, yb - 0.12, zb), (-w, yb - 0.12, zb), (0, -1, 0), "accent", 0.55)
            for s in (-1, 1):
                m.quad_facing((s * w, ya - 0.12, za), (s * w, yb - 0.12, zb), (s * w, yb, zb), (s * w, ya, za), (s, 0, 0), "accent", 0.8)
                for hh, ww in ((0.95, 0.08), (0.5, 0.05)):                       # rails (flat, both faces)
                    _strip(m, (s * w, ya + hh, za), (s * w, yb + hh, zb), ww, (s, 0, 0), "accent")
                    _strip(m, (s * (w - 0.004), ya + hh, za), (s * (w - 0.004), yb + hh, zb), ww, (-s, 0, 0), "accent")
                if i % 2 == 0:
                    m.box((s * w - 0.04, ya, za - 0.04), (s * w + 0.04, ya + 1.0, za + 0.04), "accent", 0.9, skip=("y-",))
            if i % 2 == 0:
                for s in (-1, 1):
                    m.tube((s * (w - 0.1), ya - 0.12, za), (s * (w - 0.1), -1.5, za), 0.07, "accent", n=4)
        return m
    return b


# ------------------------------------------------------------------ register
MR = ["mardin_terraces"]
PIECES["wall_triple_arch_loggia_k"] = _w("wall", wall_triple_arch_loggia(), MR, lod1="keep", notes="MARDIN MARK: triple-arched loggia, carved balustrade")
PIECES["edge_balustrade_carved_k"] = _w("edge", edge_balustrade_carved(), MR, lod1="keep", notes="carved stone balustrade round a terrace")
PIECES["abbara_vault"] = _w("cell", abbara_vault(), MR, lod1="keep", kind="passage", notes="MARDIN MARK: vault over a lane along Z, portals at both ends")
PIECES["wall_carved_frame_k"] = _w("wall", wall_carved_frame(), MR, notes="pointed window in a carved frame, iron grille")
for p in ("base", "shaft", "top"):
    PIECES[f"minaret_square_carved_{p}"] = _w("cell", minaret_square_carved(p), MR, lod1="keep", kind="tower", notes=f"MARDIN MARK: carved square minaret {p}")
OT = ["ottoman_timber"]
PIECES["wall_cumba_t"] = _w("wall", wall_cumba(), OT + ["levantine_courtyard"], lod1="keep", notes="OTTOMAN MARK: cumba oriel 0.6 m out on brackets")
PIECES["wall_kafes_t"] = _w("wall", wall_kafes(), OT, notes="sash pair behind kafes lattice")
PIECES["wall_himis_t"] = _w("wall", wall_himis(), OT + ["caucasian_balcony"], notes="himis timber frame with braces, plaster infill")
PIECES["eave_soffit_deep"] = _w("edge", eave_soffit_deep(), OT, lod1="keep", notes="1.2 m eave, boarded soffit")
PIECES["cesme_fountain"] = _w("wall", cesme_fountain(), OT, lod1="keep", kind="overlay", notes="marble wall fountain, trough, canopy")
RU = ["rupestrian_terraces"]
PIECES["vault_roof_hump"] = _w("cell", vault_roof_hump(), RU, lod1="keep", kind="roof", notes="whitewashed vault hump along Z, walkable")
PIECES["wall_cave_door_k"] = _w("wall", wall_cave_door(), RU, notes="MATERA MARK: deep arched door with a lunette")
PIECES["rock_face_cut"] = _w("wall", rock_face_cut(), RU, notes="raw faceted rock face (ground slot)")
PIECES["cistern_well"] = _w("cell", cistern_well(), RU, lod1="keep", notes="carved well head with iron arch")
PIECES["lemon_pergola"] = _w("cell", lemon_pergola(), RU + ["tyrrhenian_canyon"], lod1="keep", collide=False, kind="overlay", notes="lemon/vine pergola (accent2 = lemons)")
SC = ["scots_lands"]
PIECES["roof_slate_steep"] = _w("cell", roof_seg(50, 0.2, 8, "roof", 0.035), SC, lod1="keep", kind="roof", notes="50-deg slate gable segment, ridge along Z")
PIECES["roof_slate_steep_end"] = _w("cell", roof_seg(50, 0.2, 8, "roof", 0.035, True), SC, lod1="keep", kind="roof", notes="its end segment (gable at -Z)")
PIECES["chimney_stack_pots"] = _w("cell", chimney_stack_pots(), SC + ["hanseatic_gable"], lod1="keep", kind="overlay", notes="SCOTS MARK: long stack with six pots")
PIECES["turret_stair_shaft"] = _w("corner", turret_stair("shaft"), SC, lod1="keep", kind="tower", notes="SCOTS MARK: stair turret storey at a corner (stack)")
PIECES["turret_stair_conical"] = _w("corner", turret_stair("cap"), SC, lod1="keep", kind="tower", notes="SCOTS MARK: the turret's conical slate cap")
PIECES["wall_pend_k"] = _w("wall", wall_pend(), SC, notes="arched pend into a close, name panel")
PIECES["crown_spire"] = _w("cell", crown_spire(), SC, lod1="keep", kind="crown", notes="SCOTS MARK: St Giles' crown spire")
PIECES["mercat_cross"] = _w("cell", mercat_cross(), SC, lod1="keep", notes="octagonal mercat cross with unicorn")
SI = ["siam_khlong"]
PIECES["pier_steps_khlong"] = _w("cell", pier_steps_khlong(), SI, collide="ramp", kind="stair", notes="timber pier steps 2 m down along +Z")
PIECES["ov_gold_shop_neon"] = _w("wall", ov_gold_shop_neon(), SI + ["straits_shophouse"], lod1="keep", collide=False, kind="overlay", notes="SIAM MARK: 2-storey gold-shop sign, faces +-X")
ST2 = ["straits_shophouse"]
PIECES["wall_five_foot_way_t"] = _w("wall", wall_five_foot_way(), ST2, lod1="keep", notes="STRAITS MARK: five-foot way bay (front 1.6 m of the cell), pintu pagar")
PIECES["wall_casement_louvre_t"] = _w("wall", wall_casement_louvre(), ST2, notes="three casements with louvred leaves")
PIECES["band_peranakan_tile"] = _w("wall", band_peranakan_tile(), ST2, lod1="drop", collide=False, kind="overlay", notes="STRAITS MARK: Peranakan tile dado 1 m")
PIECES["edge_firewall_gable"] = _w("edge", edge_firewall_gable_straits(), ST2, lod1="keep", kind="crown", notes="curved firewall gable between units (on the party wall)")
PIECES["temple_chinese_roof"] = _w("cell", temple_chinese_roof(), ST2 + ["taipei_tiepi", "hk_neon_canyon"], lod1="keep", kind="crown", notes="STRAITS MARK: temple roof, swallowtails, dragons")
TB = ["tibetan_lhasa"]
PIECES["wall_battered_k"] = _w("wall", wall_battered(), TB, notes="battered whitewashed bay (leans back 0.35 m a storey)")
PIECES["wall_window_trapezoid_k"] = _w("wall", wall_window_trapezoid(), TB, notes="TIBET MARK: black trapezoid surround, tiered lintels, valance")
PIECES["edge_pembe_frieze"] = _w("edge", edge_pembe_frieze(), TB, lod1="keep", kind="overlay", notes="TIBET MARK: maroon pembe band under a parapet (y -0.7..0)")
PIECES["ov_prayer_flag_pole"] = _w("corner", ov_prayer_flag_pole(), TB, lod1="keep", collide=False, kind="decor", notes="prayer-flag pole at a roof corner")
PIECES["incense_burner"] = _w("cell", incense_burner(), TB, lod1="keep", notes="whitewashed sang-khang, lit mouth")
PIECES["roof_gilded_temple"] = _w("cell", roof_gilded_temple(), TB, lod1="keep", kind="crown", notes="TIBET MARK: gilt roof, victory banners")
TY = ["tyrrhenian_canyon"]
PIECES["wall_basso_t"] = _w("wall", wall_basso(), TY, notes="NAPLES MARK: glazed basso door, chair outside")
PIECES["ov_wall_shrine"] = _w("wall", ov_wall_shrine(), TY + ["knights_harbour"], lod1="keep", collide=False, kind="overlay", notes="NAPLES MARK: lit edicola")
PIECES["wall_french_balcony_k"] = _w("wall", wall_french_balcony(), TY, notes="french window, green shutters, shallow iron balcony")
PIECES["ov_laundry_line_lane"] = _w("cell", ov_laundry_line_lane(), TY + ["viet_tube", "kowloon_walled"], lod1="drop", collide=False, kind="overlay", notes="laundry lines along X at 5.2 / 7.6 m")
PIECES["band_damp"] = _w("wall", band_damp(), TY, lod1="drop", collide=False, kind="overlay", notes="damp band 0-1.5 m")
VT = ["viet_tube"]
PIECES["wall_french_door_balcony_t"] = _w("wall", wall_french_door_balcony(), VT, lod1="keep", notes="VIET MARK: french doors, louvred shutters, balcony of pots")
PIECES["ov_wire_tangle"] = _w("cell", ov_wire_tangle(), VT, lod1="keep", collide=False, notes="VIET MARK: pole with a knotted wire tangle")
PIECES["wall_side_ad_t"] = _w("wall", wall_side_ad(), VT, notes="painted advertisement on a side wall")
PIECES["ov_roof_shrine"] = _w("cell", ov_roof_shrine(), VT, lod1="drop", kind="overlay", notes="rooftop ancestor shrine, lit")
PIECES["bridge_red_lake"] = _w("cell", bridge_red_lake(), VT, lod1="keep", kind="bridge", span=(1, 3), notes="VIET MARK: red arched timber bridge along +Z")

for civ, acc, extra in (("mardin_terraces", ("#c9a23a", "#e8dcc0"), {}), ("ottoman_timber", None, {}), ("rupestrian_terraces", ("#6b4a2e", "#f2d03a"), {"trim": "#f2efe6"}),
                        ("scots_lands", ("#a8542e", "#c9a23a"), {}), ("straits_shophouse", ("#3f7a5a", "#e8c43a"), {"tile": "#3a8aa8"}),
                        ("tibetan_lhasa", ("#7a1e1e", "#d8a83a"), {"fabric": "#d8c8a8", "tile": "#2a6ab0"}), ("tyrrhenian_canyon", ("#3f6a4a", "#2a55a8"), {}),
                        ("viet_tube", ("#3f6a4a", "#f2c43a"), {})):
    for v in PALETTES.get(civ, []):
        if acc:
            v["accent"], v["accent2"] = acc
        v.update(extra)
