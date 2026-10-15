"""pieces_b8.py -- warren kit batch 4e: the generator's requests for caucasian_balcony (incl. a lighter balcony),
cycladic, hakka_tulou, jiangnan_water, knights_harbour, korean_hillside, kulla_stone, lusitanian_hill, manila_estero.
"""
import math

from geom import Mesh, _dedupe, arch, rot_y
from pieces import BAY, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall, pave
from pieces_b4 import _flat_prism, _gable_seg, bridge_humped_brick, roof_seg
from pieces_b5 import _bell, _door_leaf, _fix_mirror, _frustum, _pot, _u_frame, stair_plex_outdoor
from pieces_b6 import _arch_band, _checker, _octagon, _ribbed_dome, _stud_grid
from pieces_marks import _beads, _chochin, _corbel, _crest, _diag, _hip, _lightbox, _off, _place, _ring


def _rot(k):
    return rot_y(90 * k)


def _grid(m, x0, y0, x1, y1, z, nx, ny, bar, slot, nrm=(0, 0, 1)):
    for i in range(1, nx):
        x = x0 + (x1 - x0) * i / nx
        _strip(m, (x, y0, z), (x, y1, z), bar, nrm, slot)
    for j in range(1, ny):
        y = y0 + (y1 - y0) * j / ny
        _strip(m, (x0, y, z + 0.003 * nrm[2]), (x1, y, z + 0.003 * nrm[2]), bar, nrm, slot)


def _facet(sub, R=22.0):
    """bend a straight 3 m bay about its middle into two facets for a ring of radius R (the bay's ends swing back)"""
    a = BAY / 2 / R
    out = Mesh()
    for s, ts in sub.tris.items():
        for tri in ts:
            pts = []
            for p in tri[:3]:
                x, y, z = p
                ang = a * x / HB
                pts.append((x * math.cos(ang) - 0.0, y, z - abs(x) * math.sin(abs(ang))))
            out.tris[s].append((pts[0], pts[1], pts[2], tri[3], tri[4]))
    return out


# ------------------------------------------------------------------ Caucasus (r3_caucasian_balcony)
def wall_tbilisi_balcony_lite():
    """the Tbilisi balcony at <= 300 tris (budget pass): 1 m out on two brackets, a painted fretwork apron (flat
    diamonds), the glazed gallery, a stained transom, a tin roof"""
    def b():
        m = _wall(T, [_rect(-0.5, 0.0, 0.5, 2.3)])
        d = 1.0
        m.box((-HB, -0.12, 0.004), (HB, 0.0, d), "accent", 0.85, skip=("z-", "x-", "x+"))
        m.box((-HB, -0.005, d - 0.05), (HB, 0.9, d), "accent", skip=("x-", "x+", "y-"))
        for k in range(8):
            cx = -HB + 0.19 + k * 0.375
            m.quad_facing((cx, 0.2, d + 0.004), (cx + 0.12, 0.45, d + 0.004), (cx, 0.7, d + 0.004), (cx - 0.12, 0.45, d + 0.004), (0, 0, 1), "frame", 0.5)
        m.pane(-HB + 0.05, 0.9, HB - 0.05, 2.25, d - 0.03)
        for k in range(1, 6):
            _strip(m, (-HB + k * 0.5, 0.9, d - 0.02), (-HB + k * 0.5, 2.6, d - 0.02), 0.04, (0, 0, 1), "accent")
        for k in range(6):
            x = -HB + 0.05 + k * 0.5
            m.quad_facing((x, 2.28, d - 0.03), (x + 0.4, 2.28, d - 0.03), (x + 0.4, 2.55, d - 0.03), (x, 2.55, d - 0.03), (0, 0, 1), ("emissive", "accent2", "fabric")[k % 3])
        m.quad_facing((-HB - 0.1, 3.05, 0.0), (HB + 0.1, 3.05, 0.0), (HB + 0.1, 2.65, d + 0.2), (-HB - 0.1, 2.65, d + 0.2), (0, 1, 0), "roof")
        m.quad_facing((-HB - 0.1, 3.02, 0.0), (HB + 0.1, 3.02, 0.0), (HB + 0.1, 2.62, d + 0.2), (-HB - 0.1, 2.62, d + 0.2), (0, -1, 0), "accent", 0.6)
        for x in (-1.0, 1.0):
            m.tube((x, -0.9, 0.02), (x, -0.12, d - 0.15), 0.05, "accent", n=4)
        return m
    return b


def wall_shushabandi():
    """TBILISI MARK: the shushabandi -- a shallow gallery 0.6 m out glazed edge to edge in small panes, the upper rows
    stained glass (glowing at night), a timber frame, a little roof"""
    def b():
        m = _wall(T, [_rect(-0.5, 0.0, 0.5, 2.3)])
        d = 0.6
        m.box((-HB, -0.12, 0.004), (HB, 0.0, d), "accent", 0.85, skip=("z-", "x-", "x+"))
        m.box((-HB, -0.005, d - 0.05), (HB, 0.7, d), "accent", skip=("x-", "x+", "y-"))
        m.pane(-HB + 0.04, 0.7, HB - 0.04, 2.0, d - 0.03)
        _grid(m, -HB, 0.7, HB, 2.0, d - 0.02, 10, 4, 0.03, "accent")
        cols = ("emissive", "accent2", "fabric", "tile")
        for i in range(10):
            for j in range(2):
                x = -HB + i * 0.3 + 0.02
                y = 2.02 + j * 0.3
                m.quad_facing((x, y, d - 0.03), (x + 0.26, y, d - 0.03), (x + 0.26, y + 0.26, d - 0.03), (x, y + 0.26, d - 0.03), (0, 0, 1), cols[(i + j * 2) % 4])
        _grid(m, -HB, 2.0, HB, 2.62, d - 0.02, 10, 2, 0.03, "accent")
        for side in (-HB, HB - 0.05):
            m.box((side, -0.005, 0.004), (side + 0.05, 2.65, d - 0.055), "accent", 0.85, skip=("y-",))
        m.quad_facing((-HB - 0.1, 3.05, 0.0), (HB + 0.1, 3.05, 0.0), (HB + 0.1, 2.65, d + 0.2), (-HB - 0.1, 2.65, d + 0.2), (0, 1, 0), "roof")
        m.quad_facing((-HB - 0.1, 3.02, 0.0), (HB + 0.1, 3.02, 0.0), (HB + 0.1, 2.62, d + 0.2), (-HB - 0.1, 2.62, d + 0.2), (0, -1, 0), "accent", 0.6)
        return m
    return b


def svan_tower(part):
    """CAUCASUS MARK: the Svan defensive tower, a cell a part: base (rubble stone, tapering; stack 4-6), shaft (a small
    window a storey), top (the machicolated crown under a slate gable roof)"""
    def b():
        m = Mesh()
        if part == "base":
            _frustum(m, 1.3, 1.25, 0.0, ST, "wall")
        elif part == "shaft":
            _frustum(m, 1.25, 1.2, 0.0, ST, "wall")
            for k in range(2):
                sub = Mesh()
                sub.quad_facing((-0.12, 1.5, 1.235), (0.12, 1.5, 1.235), (0.12, 2.0, 1.225), (-0.12, 2.0, 1.225), (0, 0.03, 1), "frame", 0.35)
                m.add(sub, _rot(k * 2 + 1))
        else:
            _frustum(m, 1.2, 1.18, 0.0, 0.6, "wall")
            for k in range(4):
                sub = Mesh()
                sub.box((-1.3, 0.6, 1.18), (1.3, 1.6, 1.38), "wall", 0.95, skip=("y-",))
                for x in (-0.6, 0.6):
                    sub.box((x - 0.07, 0.35, 1.18), (x + 0.07, 0.6, 1.36), "wall", 0.8, skip=("z-",))
                for x in (-0.9, -0.3, 0.3, 0.9):
                    sub.quad_facing((x - 0.1, 0.9, 1.385), (x + 0.1, 0.9, 1.385), (x + 0.1, 1.3, 1.385), (x - 0.1, 1.3, 1.385), (0, 0, 1), "frame", 0.35)
                m.add(sub, _rot(k))
            seg, h = _gable_seg(40, 0.25, 6)
            m.add(seg, lambda p: (p[0] * 0.95, p[1] + 1.6, p[2] * 0.95))
            _flat_prism(m, [(-1.3, 1.6), (1.3, 1.6), (0.0, 1.6 + h * 0.95 - 0.05)], -1.3, -1.25, "wall", 0.9, open_edges=(0,))
            _flat_prism(m, [(-1.3, 1.6), (1.3, 1.6), (0.0, 1.6 + h * 0.95 - 0.05)], 1.25, 1.3, "wall", 0.9, open_edges=(0,))
        return m
    return b


def dome_bath_brick():
    """TBILISI: the low brick dome of the Abanotubani baths with its little glazed lantern (crown)"""
    def b():
        m = Mesh()
        m.lathe([(1.45, 0.0), (1.4, 0.25), (1.15, 0.6), (0.7, 0.85), (0.3, 0.92)], "wall", n=12)
        m.cyl(0, 0, 0.3, 0.9, 1.25, "emissive", n=6, caps=False, shade=0.8)
        m.lathe([(0.38, 1.25), (0.3, 1.4), (0.0, 1.5)], "wall", n=6, shade=0.9)
        return m
    return b


def stair_spiral_courtyard():
    """TBILISI: the spiral iron stair of an Italian courtyard (cell): a full turn round a post up a storey, treads,
    a railing, a landing to -Z"""
    def b():
        m = Mesh()
        n, r0, r1 = 14, 0.1, 1.0
        a0, a1 = -math.pi / 2, -math.pi / 2 + 2 * math.pi
        for k in range(n):
            t0, t1 = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
            y = ST * 0.92 * (k + 1) / n
            p = [(r0 * math.cos(t0), r0 * math.sin(t0)), (r1 * math.cos(t0), r1 * math.sin(t0)), (r1 * math.cos(t1), r1 * math.sin(t1)), (r0 * math.cos(t1), r0 * math.sin(t1))]
            m.prism_xz(p, y - 0.04, y, "metal", 0.85)
        m.box((-1.0, ST - 0.05, -HB), (1.0, ST, -0.9), "metal", 0.85)
        m.cyl(0, 0, 0.07, 0.0, ST + 1.0, "metal", n=6)
        prev = None
        for k in range(n + 1):
            t = a0 + (a1 - a0) * k / n
            y = ST * 0.92 * k / n
            p = (r1 * math.cos(t), y + 0.95, r1 * math.sin(t))
            if prev:
                m.tube(prev, p, 0.02, "metal", n=3)
            if k % 3 == 0:
                m.tube((p[0], y, p[2]), p, 0.013, "metal", n=3)
            prev = p
        return m
    return b


# ------------------------------------------------------------------ Cyclades (r3_cycladic)
def chapel_cycladic():
    """CYCLADES MARK: the little white chapel (crown over a cell): a whitewashed box, a blue dome on a drum at its east
    end, a bell gable over its door at +Z"""
    def b():
        m = Mesh()
        m.box((-1.1, 0.0, -1.4), (1.1, 2.4, 1.4), "trim", skip=("y-",))
        m.cyl(0, -0.6, 0.75, 2.4, 2.8, "trim", n=10, caps=False)
        m.lathe([(0.8, 2.8), (0.72, 3.15), (0.5, 3.4), (0.0, 3.55)], "accent", n=10, cz=-0.6)
        m.box((-0.02, 3.55, -0.62), (0.02, 3.9, -0.58), "trim")
        m.box((-0.12, 3.75, -0.62), (0.12, 3.79, -0.58), "trim")
        g = [(-0.8, 2.4), (0.8, 2.4), (0.8, 3.0), (0.3, 3.2), (0.3, 3.4), (-0.3, 3.4), (-0.3, 3.2), (-0.8, 3.0)]
        o = arch("round", 0.35, 0.55, 2.55, n=4)
        m.wall_cut(g, [o], 1.15, 1.4, "trim", reveal_slot="trim")
        _bell(m, 0.0, 2.95, 1.27, 0.12)
        m.box((-0.35, 0.0, 1.38), (0.35, 1.8, 1.41), "accent", 0.9)
        m.box((-0.45, 1.8, 1.4), (0.45, 1.9, 1.48), "trim", 0.9)
        return m
    return b


def windmill_round():
    """CYCLADES MARK: the round white windmill (a cell, three storeys): the drum, a small door and windows, the conical
    thatched cap, the hub and eight spars with triangular sails turned to +Z"""
    def b():
        m = Mesh()
        m.cyl(0, 0, 1.4, 0.0, 7.0, "trim", n=12, r1=1.25)
        m.lathe([(1.35, 7.0), (1.2, 7.6), (0.6, 8.4), (0.0, 8.8)], "roof", n=12)
        m.box((-0.35, 0.0, 1.37), (0.35, 1.9, 1.42), "accent", 0.9)
        for y in (3.2, 5.4):
            m.quad_facing((-0.2, y, 1.33), (0.2, y, 1.33), (0.2, y + 0.5, 1.32), (-0.2, y + 0.5, 1.32), (0, 0, 1), "frame", 0.35)
        hub = (0.0, 7.4, 1.6)
        m.tube((0.0, 7.4, 0.9), hub, 0.1, "frame", n=6)
        for k in range(8):
            a = math.tau * k / 8
            tip = (3.8 * math.cos(a), 7.4 + 3.8 * math.sin(a), 1.65)
            m.tube(hub, tip, 0.03, "frame", n=3)
            b2 = (3.4 * math.cos(a + 0.3), 7.4 + 3.4 * math.sin(a + 0.3), 1.66)
            m.tri_facing((0.6 * math.cos(a), 7.4 + 0.6 * math.sin(a), 1.66), tip, b2, (0, 0, 1), "fabric")
            m.tri_facing((0.6 * math.cos(a), 7.4 + 0.6 * math.sin(a), 1.655), tip, b2, (0, 0, -1), "fabric", 0.85)
        return m
    return b


def edge_parapet_lip():
    """CYCLADES: the rounded whitewashed roof lip -- 0.35 m, soft-topped (edge, ~30 tris)"""
    def b():
        m = Mesh()
        prof = [(0.0, 0.0), (0.3, 0.0), (0.3, 0.25), (0.25, 0.33), (0.15, 0.36), (0.05, 0.33), (0.0, 0.25)]
        sub = Mesh()
        _flat_prism(sub, prof, -HB, HB, "trim", open_edges=(0,))
        m.add(sub, lambda p: (-p[2], p[1], p[0] - 0.3))
        return m
    return b


def pave_slate_whitejoint():
    """CYCLADES: slate paving with whitewashed joints: a white joint sheet and irregular slabs"""
    def b():
        m = Mesh()
        m.quad_facing((-HB, -0.01, -HB), (HB, -0.01, -HB), (HB, -0.01, HB), (-HB, -0.01, HB), (0, 1, 0), "trim")
        xs = [-HB, -0.6, 0.4, HB]
        zs = [[-HB, -0.4, 0.7, HB], [-HB, 0.1, HB], [-HB, -0.7, 0.5, HB]]
        for i in range(3):
            for j in range(len(zs[i]) - 1):
                x0, x1 = xs[i] + 0.05, xs[i + 1] - 0.05
                z0, z1 = zs[i][j] + 0.05, zs[i][j + 1] - 0.05
                m.quad_facing((x0, 0.0, z0), (x1, 0.0, z0 + 0.04), (x1, 0.0, z1), (x0, 0.0, z1 - 0.03), (0, 1, 0), "ground", 0.8 + 0.1 * ((i + j) % 3))
        return m
    return b


def stair_external_white():
    """CYCLADES: the external whitewashed stair climbing a house face to its roof (face overlay: up along +X, 0.9 m
    out, solid masonry with a rounded parapet)"""
    def b():
        m = Mesh()
        n = 14
        prof = [(-HB, 0.0), (HB, 0.0)]
        for k in range(n, 0, -1):                                             # the treads, top step first
            prof += [(-HB + BAY * k / n, ST * k / n), (-HB + BAY * (k - 1) / n, ST * k / n)]
        prof = _dedupe(prof)
        sub = Mesh()
        _flat_prism(sub, prof, 0.004, 0.85, "trim", open_edges=(0,))
        m.add(sub)
        _flat_prism(m, [(-HB, 0.0), (HB, ST), (HB, ST + 0.8), (-HB, 0.8)], 0.85, 0.97, "trim", 0.95)
        return m
    return b


# ------------------------------------------------------------------ Hakka tulou (r2_hakka_tulou)
def tulou_ring_wall():
    """HAKKA MARK: a rammed-earth ring segment (outer face; a bay bent for rings of R ~20 m): a granite base, the
    blank earth wall, small high slits; stack it, the top storey gets the slits"""
    def b():
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [], -K, 0.0, "wall")
        m.box((-HB, 0.0, -0.02), (HB, 1.1, 0.03), "ground", 0.85, skip=("z-", "x-", "x+"))
        for x in (-0.75, 0.75):
            m.quad_facing((x - 0.07, 2.0, 0.004), (x + 0.07, 2.0, 0.004), (x + 0.07, 2.6, 0.004), (x - 0.07, 2.6, 0.004), (0, 0, 1), "frame", 0.35)
        return _facet(m)
    return b


def tulou_gallery_ring():
    """HAKKA MARK: the inner timber gallery storey of a tulou ring (bent for R ~20 m): lattice doors, the gallery 1.2 m
    out, a plank rail, posts"""
    def b():
        m = _wall(T, [_rect(-1.2, 0.0, -0.35, 2.2), _rect(0.35, 0.0, 1.2, 2.2)], reveal="frame")
        for x0 in (-1.2, 0.35):
            m.pane(x0, 0.0, x0 + 0.85, 2.2, -0.16)
            _lattice(m, x0 + 0.005, 0.005, x0 + 0.845, 2.195, -0.12, -0.06, 4, 8, slot="frame")
        d = 1.2
        m.box((-HB, -0.12, 0.004), (HB, 0.0, d), "frame", 0.85, skip=("z-", "x-", "x+"))
        m.box((-HB, -0.005, d - 0.06), (HB, 0.85, d), "frame", 0.9, skip=("x-", "x+", "y-"))
        m.box((-HB, 0.85, d - 0.1), (HB, 0.95, d + 0.03), "frame", skip=("x-", "x+"))
        for x in (-1.44, 0.0, 1.44):
            m.box((x - 0.06, 0.0, d - 0.14), (x + 0.06, ST - 0.005, d - 0.02), "frame", 0.8, skip=("y-",))
        m.box((-HB, ST - 0.15, 0.004), (HB, ST - 0.005, d), "frame", 0.7, skip=("z-", "x-", "x+"))
        return _facet(m)
    return b


def roof_ring_tile():
    """HAKKA: the continuous ring roof (a cell of its run, ridge along Z = the ring's tangent): the outer slope (+X)
    reaches 2.5 m past the wall, the inner one 0.8 m; grey tile ribs"""
    def b():
        m = Mesh()
        tn = math.tan(math.radians(26))
        h = HB * tn
        for s, ev in ((1, 2.5), (-1, 0.8)):
            lx, ly = HB + ev, -ev * tn
            m.quad_facing((s * lx, ly, -HB), (s * lx, ly, HB), (0.0, h, HB), (0.0, h, -HB), (s * tn, 1, 0), "roof")
            m.quad_facing((s * lx, ly - 0.06, -HB), (s * lx, ly - 0.06, HB), (s * HB, -0.02, HB), (s * HB, -0.02, -HB), (0, -1, 0), "frame", 0.55)
            for k in range(7):
                z = -HB + BAY * (k + 0.5) / 7
                _strip(m, (s * (lx - 0.02), ly + 0.02, z), (s * 0.08, h - 0.04, z), 0.07, (s * tn, 1, 0), "roof")
        m.box((-0.1, h - 0.04, -HB), (0.1, h + 0.1, HB), "roof", 0.8, skip=("y-", "z-", "z+"))
        return m
    return b


def tulou_gate():
    """HAKKA MARK: the tulou's single massive gate: a granite frame in the thick earth wall, heavy timber doors, a
    name plaque over it, a small fire-water spout above"""
    def b():
        x0, x1, y1 = -0.8, 0.8, 2.6
        m = _wall(K, [_rect(x0, 0.0, x1, y1)], reveal="ground")
        m.box((x0 + 0.005, 0.0, -0.45), (x1 - 0.005, y1 - 0.005, -0.38), "frame", 0.8)
        _strip(m, (0.0, 0.0, -0.375), (0.0, y1, -0.375), 0.05, (0, 0, 1), "frame")
        _u_frame(m, x0, y1, x1, 0.3, 0.0, 0.08, "ground", 0.95)
        m.box((-0.75, y1 + 0.35, 0.0), (0.75, y1 + 0.55, 0.06), "accent", skip=("z-",))
        for k in range(4):
            x = -0.55 + k * 0.36
            _strip(m, (x, y1 + 0.39, 0.065), (x + 0.12, y1 + 0.51, 0.065), 0.05, (0, 0, 1), "accent2")
        return m
    return b


def ancestral_hall():
    """HAKKA MARK: the ancestral hall at the courtyard's centre (crown on a cell): a stone platform, red columns, a lit
    shrine wall at the back, a grey tile hip roof with its corners swept up"""
    def b():
        m = Mesh()
        m.box((-1.45, 0.0, -1.45), (1.45, 0.4, 1.45), "ground", 0.9, skip=("y-",))
        for x in (-1.2, 1.2):
            for z in (-1.2, 1.2):
                m.cyl(x, z, 0.1, 0.4, 2.8, "accent", n=6, caps=False)
        m.box((-1.2, 0.4, -1.25), (1.2, 2.8, -1.15), "frame", 0.8)
        m.quad_facing((-0.6, 0.9, -1.145), (0.6, 0.9, -1.145), (0.6, 2.2, -1.145), (-0.6, 2.2, -1.145), (0, 0, 1), "emissive", 0.7)
        _hip(m, 2.0, 0.5, 2.8, 3.9, lift=0.4, flare=0.25, body=1.3, cap=False)
        m.box((-0.8, 3.85, -0.08), (0.8, 4.02, 0.08), "roof", 0.8, skip=("y-",))
        for x in (-0.9, 0.9):
            _chochin(m, x, 2.3, 1.25, r=0.13, h=0.36)
        return m
    return b


# ------------------------------------------------------------------ Jiangnan (r2_jiangnan_water)
def edge_horsehead_wall():
    """JIANGNAN MARK: the stepped horse-head firewall at a house's gable end (edge on the roof top): white steps up to the
    ridge, each capped with a little black-tiled roof whose ends kick up"""
    def b():
        m = Mesh()
        p = _dedupe([(-HB, 0.0), (HB, 0.0), (HB, 0.6), (1.0, 0.6), (1.0, 1.3), (0.5, 1.3), (0.5, 2.0), (-0.5, 2.0), (-0.5, 1.3), (-1.0, 1.3), (-1.0, 0.6), (-HB, 0.6)])
        _flat_prism(m, p, -0.3, 0.0, "trim", open_edges=(0,))
        for (xa, xb, y) in ((1.0, 1.55, 0.6), (-1.55, -1.0, 0.6), (0.5, 1.05, 1.3), (-1.05, -0.5, 1.3), (-0.55, 0.55, 2.0)):
            m.quad_facing((xa, y + 0.18, -0.15), (xb, y + 0.18, -0.15), (xb, y, 0.08), (xa, y, 0.08), (0, 1, 0.5), "roof")
            m.quad_facing((xa, y + 0.18, -0.15), (xb, y + 0.18, -0.15), (xb, y, -0.38), (xa, y, -0.38), (0, 1, -0.5), "roof")
            for xe in (xa, xb):                                               # the outer ends kick up
                if abs(xe) > 0.56:
                    m.tube((xe, y + 0.18, -0.15), (xe + math.copysign(0.18, xe), y + 0.38, -0.15), 0.035, "roof", n=3)
        return m
    return b


def roof_black_tile(end):
    """JIANGNAN: the black double-pitched tile roof, its slopes gently concave, the ridge ends kicking up (a gable
    segment, ridge along Z; _end closes -Z)"""
    def b():
        m = Mesh()
        tn1, tn2 = math.tan(math.radians(22)), math.tan(math.radians(32))
        xm = 0.8
        ym = xm * tn2
        h = (HB - xm) * tn1 + xm * tn2
        lx, ly = HB + 0.5, -0.5 * tn1
        for s in (-1, 1):
            p_l, p_m, p_t = (s * lx, ly), (s * xm, h - xm * tn2), (0.0, h)
            for (a, c, sh) in ((p_l, p_m, 1.0), (p_m, p_t, 0.95)):
                m.quad_facing((a[0], a[1], -HB), (a[0], a[1], HB), (c[0], c[1], HB), (c[0], c[1], -HB), (s * 0.4, 1, 0), "roof", sh)
            m.quad_facing((s * lx, ly - 0.05, -HB), (s * lx, ly - 0.05, HB), (s * HB, -0.02, HB), (s * HB, -0.02, -HB), (0, -1, 0), "frame", 0.5)
            for k in range(8):
                z = -HB + BAY * (k + 0.5) / 8
                _strip(m, (s * (lx - 0.02), ly + 0.02, z), (s * xm, p_m[1] + 0.02, z), 0.08, (s * 0.4, 1, 0), "roof")
                _strip(m, (s * xm, p_m[1] + 0.02, z), (s * 0.06, h - 0.03, z), 0.08, (s * 0.6, 1, 0), "roof")
        m.box((-0.09, h - 0.04, -HB), (0.09, h + 0.12, HB), "roof", 0.75, skip=("y-", "z-", "z+"))
        if end:
            _flat_prism(m, [(-HB + 0.02, 0.0), (HB - 0.02, 0.0), (xm - 0.02, h - xm * tn2 - 0.03), (0.0, h - 0.05), (-xm + 0.02, h - xm * tn2 - 0.03)], -HB, -HB + 0.25, "trim", open_edges=(0,))
            m.tube((0.0, h + 0.1, -HB), (0.0, h + 0.4, -HB - 0.25), 0.05, "roof", n=4)
        return m
    return b


def wall_shopboards():
    """JIANGNAN: the full-width removable timber shop boards across a ground floor, two pulled out to open the shop, a
    lintel beam and a sign board"""
    def b():
        m = _wall(T, [_rect(-1.35, 0.0, 1.35, 2.6)], reveal="frame")
        m.pane(-1.35, 0.0, 1.35, 2.6, -0.2)
        for k in range(12):
            if k in (5, 6):
                continue
            x = -1.35 + k * 0.225
            m.box((x + 0.008, 0.25, -0.14), (x + 0.217, 2.55, -0.1), "frame", 0.8 + 0.08 * (k % 2))
        m.box((-1.4, 0.0, -0.18), (1.4, 0.25, 0.03), "frame", 0.7)
        m.box((-1.45, 2.6, 0.0), (1.45, 2.8, 0.14), "frame", 0.85, skip=("z-",))
        m.box((-0.7, 2.85, 0.0), (0.7, 3.15, 0.06), "accent", skip=("z-",))
        for k in range(3):
            _strip(m, (-0.45 + k * 0.45, 2.9, 0.065), (-0.35 + k * 0.45, 3.1, 0.065), 0.06, (0, 0, 1), "accent2")
        return m
    return b


def wall_moon_gate():
    """JIANGNAN MARK: a garden wall with its round moon gate (a passage), a black-tile coping, a leak window"""
    def b():
        r = 1.15
        o = [(r * math.cos(math.tau * k / 16 - math.pi / 2), 1.15 + r * math.sin(math.tau * k / 16 - math.pi / 2)) for k in range(16)]
        o = [(x, max(y, 0.0)) for x, y in o]
        o = _dedupe([(-0.45, 0.0), (0.45, 0.0)] + [p for p in o if p[1] > 0.0])
        m = _wall(T, [o])
        _arch_band(m, o, 0.1, -0.01, 0.03, "ground")
        m.quad_facing((-HB, ST, 0.15), (HB, ST, 0.15), (HB, ST + 0.25, -T / 2), (-HB, ST + 0.25, -T / 2), (0, 1, 0.5), "roof")
        m.quad_facing((-HB, ST, -T - 0.15), (HB, ST, -T - 0.15), (HB, ST + 0.25, -T / 2), (-HB, ST + 0.25, -T / 2), (0, 1, -0.5), "roof")
        return m
    return b


def bridge_humpback_stone():
    """JIANGNAN MARK: the humpbacked stone canal bridge over three cells along +Z: a high semicircular arch, its deck in
    steps, low stone balustrades (span [1, 3])"""
    def b():
        m = Mesh()
        L, n, w = 9.0, 14, 1.2
        zs = [-HB + L * i / n for i in range(n + 1)]
        ys = [2.0 * math.sin(math.pi * i / n) for i in range(n + 1)]
        for i in range(n):
            za, zb = zs[i], zs[i + 1]
            y = max(ys[i], ys[i + 1]) if i < n / 2 else max(ys[i], ys[i + 1])
            y = (ys[i] + ys[i + 1]) / 2
            m.box((-w, y - 0.15, za), (w, y, zb + 0.01), "ground", 0.9 + 0.1 * (i % 2), skip=("y-",))
            for s in (-1, 1):
                xa, xb = sorted((s * (w - 0.12), s * (w + 0.01)))
                m.box((xa, y - 0.005, za), (xb, y + 0.55, zb + 0.01), "trim", 0.9, skip=("y-",))
        arch_ = lambda z: -0.2 + 1.4 * math.sin(math.pi * min(max((z - 0.5) / 5.0, 0.0), 1.0))  # noqa: E731
        for i in range(n):
            za, zb = zs[i], zs[i + 1]
            for s in (-1, 1):
                ya, yb = (ys[i] + ys[i + 1]) / 2 - 0.15, (ys[i] + ys[i + 1]) / 2 - 0.15
                m.quad_facing((s * w, arch_(za), za), (s * w, arch_(zb), zb), (s * w, yb, zb), (s * w, ya, za), (s, 0, 0), "trim", 0.8)
            m.quad_facing((-w, arch_(za), za), (w, arch_(za), za), (w, arch_(zb), zb), (-w, arch_(zb), zb), (0, -1, 0), "trim", 0.55)
        return m
    return b


def water_steps_private():
    """JIANGNAN: a house's private stone steps down into the canal: 1.2 m wide against the -X side, 1.6 m down along +Z
    to the water (stair, water side)"""
    def b():
        m = Mesh()
        for k in range(8):
            z0 = -HB + k * 0.36
            y = -0.2 * k
            m.box((-HB + 0.02, y - 0.4, z0), (-0.28, y, z0 + 0.38), "ground", 0.88 + 0.1 * (k % 2), skip=("y-",))
        m.box((-HB + 0.02, -1.95, 1.4), (-0.28, -1.55, HB), "ground", 0.8, skip=("y-",))
        m.cyl(-0.2, 1.3, 0.08, -1.6, 0.4, "trim", n=6)
        return m
    return b


# ------------------------------------------------------------------ Knights' harbour (r3_knights_harbour)
def wall_gallarija():
    """MALTA MARK: the gallarija -- an enclosed painted timber balcony 1.2 m out on stone corbels, glazed sashes over
    panelled aprons, a little lead roof (stack it storey on storey)"""
    def b():
        m = _wall(K, [_rect(-0.6, 0.2, 0.6, 2.6)], reveal="accent")
        m.pane(-0.6, 0.2, 0.6, 2.6, -0.3)
        d, x0, x1 = 1.2, -1.2, 1.2
        for x in (-0.9, 0.0, 0.9):
            _corbel(m, x, 0.15, d - 0.05, 0.6, 0.15, "trim", 0.85)
        m.box((x0, 0.15, 0.004), (x1, 0.27, d), "trim", 0.9, skip=("z-",))
        m.box((x0, 0.265, d - 0.05), (x1, 0.95, d), "accent", skip=("z-",))
        for k in range(4):
            x = x0 + 0.08 + k * 0.6
            m.box((x, 0.37, d), (x + 0.44, 0.85, d + 0.02), "accent", 0.85, skip=("z-",))
        m.pane(x0 + 0.04, 0.95, x1 - 0.04, 2.55, d - 0.03)
        _grid(m, x0, 0.95, x1, 2.55, d - 0.02, 8, 4, 0.04, "accent")
        for side in (-1, 1):
            xa, xb = (0.05, d - 0.05) if side < 0 else (-(d - 0.05), -0.05)
            sub = Mesh()
            sub.box((xa, 0.27, -0.05), (xb, 0.95, 0.0), "accent", 0.85, skip=("z-",))
            sub.pane(xa, 0.95, xb, 2.55, -0.03)
            _grid(sub, xa, 0.95, xb, 2.55, -0.02, 3, 4, 0.04, "accent")
            _place(m, sub, 90 * side, dx=x1 if side > 0 else x0)
        m.box((x0 - 0.08, 2.55, 0.004), (x1 + 0.08, 2.7, d + 0.1), "accent", 0.9, skip=("z-",))
        m.quad_facing((x0 - 0.12, 3.0, 0.0), (x1 + 0.12, 3.0, 0.0), (x1 + 0.12, 2.7, d + 0.14), (x0 - 0.12, 2.7, d + 0.14), (0, 1, 0.5), "metal")
        return m
    return b


def corner_statue_niche():
    """MALTA: a saint in a niche on a street corner, at first-floor height, lit at night (corner piece: faces the corner
    diagonal +X+Z)"""
    def b():
        m = Mesh()
        sub = Mesh()
        sub.box((-0.45, 0.0, 0.0), (0.45, 0.25, 0.35), "trim", 0.85, skip=("z-",))
        o = arch("round", 0.6, 1.3, 0.25, n=6)
        sub.wall_cut(_rect(-0.5, 0.25, 0.5, 1.75), [o], 0.0, 0.2, "trim", reveal_slot="trim")
        sub.wall_cut(o, [], -0.02, 0.0, "accent", 0.8)
        sub.lathe([(0.14, 0.25), (0.11, 0.8), (0.13, 1.0), (0.07, 1.1), (0.09, 1.25), (0.0, 1.35)], "trim", n=6, cz=0.1)
        sub.lathe([(0.2, 1.75), (0.0, 2.0)], "trim", n=4, cz=0.1)
        sub.box((0.3, 0.4, 0.2), (0.38, 0.6, 0.45), "emissive")
        m.add(sub, lambda p: rot_y(45)((p[0], p[1] + 3.2, p[2] + 0.05)))
        return m
    return b


def stair_knight():
    """MALTA: the knight's stair-street -- low 0.1 m risers on deep treads, the full 3 m width, 1.6 m up over two cells
    along +Z (span [1, 2])"""
    def b():
        m = Mesh()
        n = 16
        for k in range(n):
            z0 = -HB + k * 6.0 / n
            y = 0.1 * (k + 1)
            m.box((-HB, y - 0.35, z0), (HB, y, z0 + 6.0 / n + 0.01), "ground", 0.9 + 0.08 * (k % 2), skip=("y-", "x-", "x+"))
        return m
    return b


def bastion_wall_slope():
    """MALTA MARK: the sloped bastion wall at the island rim (two storeys, y 0..6.4): the talus leaning back 1.2 m, a
    rounded cordon, the parapet above with its rounded coping"""
    def b():
        m = Mesh()
        H = 2 * ST
        m.quad_facing((-HB, 0.0, 1.2), (HB, 0.0, 1.2), (HB, H - 1.0, 0.0), (-HB, H - 1.0, 0.0), (0, 0.3, 1), "wall")
        m.box((-HB, H - 1.0, -0.05), (HB, H - 0.85, 0.12), "trim", skip=("x-", "x+"))
        m.box((-HB, H - 0.85, -0.6), (HB, H, 0.0), "wall", 0.95, skip=("x-", "x+", "y-"))
        m.box((-HB, H, -0.65), (HB, H + 0.08, 0.05), "trim", 0.9, skip=("x-", "x+"))
        return m
    return b


# ------------------------------------------------------------------ Korea (r2_korean_hillside)
def ov_jangdok_jars():
    """KOREA MARK: the jangdokdae -- a cluster of brown soy and kimchi jars on a roof, on a little platform (roof decor)"""
    def b():
        m = Mesh()
        m.box((-1.1, 0.0, -0.8), (1.1, 0.15, 0.8), "trim", 0.8, skip=("y-",))
        for (x, z, r) in ((-0.7, -0.4, 0.3), (0.05, -0.45, 0.34), (0.75, -0.3, 0.26), (-0.35, 0.35, 0.26), (0.45, 0.4, 0.3)):
            m.lathe([(r * 0.6, 0.15), (r, 0.15 + r * 0.9), (r * 0.7, 0.15 + r * 1.6), (r * 0.55, 0.15 + r * 1.65)], "accent2", n=5, cx=x, cz=z)
            m.lathe([(r * 0.62, 0.15 + r * 1.65), (r * 0.3, 0.15 + r * 1.8), (0.0, 0.15 + r * 1.85)], "accent2", n=5, cx=x, cz=z, shade=0.8)
        return m
    return b


def roof_painted_green():
    """KOREA: the green-painted waterproofed flat roof (cell roof): the painted deck, a low lip, a drain"""
    def b():
        m = Mesh()
        m.quad_facing((-HB + 0.15, 0.0, -HB + 0.15), (HB - 0.15, 0.0, -HB + 0.15), (HB - 0.15, 0.0, HB - 0.15), (-HB + 0.15, 0.0, HB - 0.15), (0, 1, 0), "accent")
        for k in range(4):
            sub = Mesh()
            sub.box((-HB, 0.0, HB - 0.15), (HB - 0.15, 0.25, HB), "trim", 0.9, skip=("y-",))
            m.add(sub, _rot(k))
        m.cyl(HB - 0.3, HB - 0.3, 0.06, 0.0, 0.02, "metal", n=6)
        return m
    return b


def oktapbang():
    """KOREA MARK: the oktapbang -- the rooftop room box: a little door, a grilled window, an AC unit, a flat lid with a
    blue tank on it (roof overlay)"""
    def b():
        m = Mesh()
        m.box((-1.2, 0.0, -1.0), (1.2, 2.3, 1.0), "wall", skip=("y-",))
        m.box((-1.0, 0.0, 1.005), (-0.3, 1.9, 1.04), "accent", 0.9)
        m.pane(0.1, 1.0, 0.9, 1.7, 1.005)
        for k in range(1, 5):
            _strip(m, (0.1 + 0.8 * k / 5, 1.0, 1.06), (0.1 + 0.8 * k / 5, 1.7, 1.06), 0.02, (0, 0, 1), "metal")
        m.box((-1.3, 2.3, -1.1), (1.3, 2.42, 1.15), "trim", 0.85)
        m.box((1.2, 0.8, -0.4), (1.5, 1.25, 0.3), "trim", 0.9, skip=("x-",))
        m.lathe([(0.45, 2.42), (0.48, 2.5), (0.48, 3.1), (0.3, 3.2), (0.0, 3.22)], "tile", n=8, cx=-0.5, cz=-0.3)
        return m
    return b


# ------------------------------------------------------------------ Kosovo / Albania kulla (r3_kulla_stone)
def roof_stone_slab(end):
    """KULLA: the 32-degree roof of stone slabs (rows of overlapping slabs across the slope) on deep timber eaves (a
    gable segment, ridge along Z; _end closes -Z)"""
    def b():
        m, h = _gable_seg(32, eave=0.7, ribs=0, end=end, wall_slot="wall")
        tn = math.tan(math.radians(32))
        lx = HB + 0.7
        for s in (-1, 1):
            for j in range(5):
                f = (j + 0.5) / 5
                x = s * (lx - (lx - 0.1) * f)
                y = -0.7 * tn + (h + 0.7 * tn) * f
                _strip(m, (x, y + 0.03, -HB), (x, y + 0.03, HB), 0.12, (s * tn, 1, 0), "roof")
            for z in (-1.0, 0.0, 1.0):                                         # the eave beams
                xa, xb = sorted((s * (HB - 0.06), s * (lx - 0.05)))
                m.box((xa, -0.22, z - 0.06), (xb, -0.1, z + 0.06), "frame", 0.75)
        return m
    return b


def wall_window_band():
    """KULLA MARK: the corbelled top storey (the cardak): a timber band 0.4 m out on stone corbels, a continuous run of
    windows with timber mullions, half the face glass"""
    def b():
        m = Mesh()
        d = 0.4
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.3, 0.9, 1.3, 2.4)], d - T, d, "frame", reveal_slot="frame")
        m.pane(-1.3, 0.9, 1.3, 2.4, d - 0.12)
        for k in range(1, 6):
            x = -1.3 + 2.6 * k / 6
            m.box((x - 0.04, 0.9, d - 0.15), (x + 0.04, 2.4, d - 0.02), "frame", 0.8)
        _strip(m, (-1.3, 1.85, d - 0.1), (1.3, 1.85, d - 0.1), 0.04, (0, 0, 1), "frame")
        m.box((-HB, -0.15, -T), (HB, 0.0, d), "frame", 0.75, skip=("z-",))
        for x in (-1.2, -0.4, 0.4, 1.2):
            _corbel(m, x, -0.15, d, 0.6, 0.18, "wall", 0.85)
        return m
    return b


def chimney_stone():
    """KULLA / SCOTS: the tall stone chimney stack with its slab cap on little stone legs (roof decor)"""
    def b():
        m = Mesh()
        m.box((-0.35, 0.0, -0.35), (0.35, 2.3, 0.35), "wall", skip=("y-",))
        for x in (-0.28, 0.28):
            for z in (-0.28, 0.28):
                m.box((x - 0.06, 2.3, z - 0.06), (x + 0.06, 2.55, z + 0.06), "wall", 0.9)
        m.box((-0.5, 2.55, -0.5), (0.5, 2.65, 0.5), "roof", 0.85)
        return m
    return b


def ov_machicolation():
    """KULLA: a machicolation box over the door: stone, 0.5 m out on three corbels, a murder slot underneath and a
    loophole in front (face overlay, y 0 = the storey floor)"""
    def b():
        m = Mesh()
        m.box((-0.6, 2.6, 0.0), (0.6, 3.3, 0.5), "wall", 0.95, skip=("z-",))
        m.quad_facing((-0.4, 2.599, 0.15), (0.4, 2.599, 0.15), (0.4, 2.599, 0.4), (-0.4, 2.599, 0.4), (0, -1, 0), "frame", 0.3)
        m.quad_facing((-0.06, 2.85, 0.505), (0.06, 2.85, 0.505), (0.06, 3.15, 0.505), (-0.06, 3.15, 0.505), (0, 0, 1), "frame", 0.3)
        for x in (-0.5, 0.0, 0.5):
            _corbel(m, x, 2.6, 0.45, 0.45, 0.12, "wall", 0.85)
        return m
    return b


# ------------------------------------------------------------------ Lisbon / Porto (r3_lusitanian_hill)
def wall_azulejo():
    """LUSITANIA MARK: a facade bay clad edge to edge in patterned azulejos (tile slot, a two-tone pattern), a tall
    window with an iron cage balcony, stone sill and lintel"""
    def b():
        x0, y0, x1, y1 = -0.5, 0.3, 0.5, 2.6
        m = _wall(T, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.14)
        _ring(m, x0, y0, x1, y1, 0.1, 0.0, 0.03, "trim")
        from shapely.geometry import box as sbox
        hole = sbox(x0 - 0.12, y0 - 0.12, x1 + 0.12, y1 + 0.12)
        for i in range(10):
            for j in range(10):
                xa, ya = -HB + i * 0.3 + 0.01, j * 0.32 + 0.01
                if sbox(xa, ya, xa + 0.28, ya + 0.3).intersects(hole):
                    continue
                m.quad_facing((xa, ya, 0.005), (xa + 0.28, ya, 0.005), (xa + 0.28, ya + 0.3, 0.005), (xa, ya + 0.3, 0.005), (0, 0, 1), "tile", 1.0 if (i + j) % 2 else 0.86)
                if (i + j) % 2 == 0:
                    cx, cy = xa + 0.14, ya + 0.15
                    m.quad_facing((cx, cy - 0.1, 0.008), (cx + 0.09, cy, 0.008), (cx, cy + 0.1, 0.008), (cx - 0.09, cy, 0.008), (0, 0, 1), "accent")
        d = 0.4
        m.box((x0 - 0.15, y0 - 0.08, 0.0), (x1 + 0.15, y0, d + 0.05), "trim", 0.9, skip=("z-",))
        for k in range(6):
            x = x0 - 0.1 + (x1 - x0 + 0.2) * k / 5
            _strip(m, (x, y0, d), (x, y0 + 1.0, d), 0.025, (0, 0, 1), "metal")
        m.box((x0 - 0.12, y0 + 0.98, 0.0), (x1 + 0.12, y0 + 1.03, d + 0.02), "metal", 0.8)
        return m
    return b


def wall_granite_window():
    """PORTO: a tall window in a dressed granite frame (ground slot = granite), a projecting sill, an eared lintel"""
    def b():
        x0, y0, x1, y1 = -0.5, 0.25, 0.5, 2.5
        m = _wall(K, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.3)
        _strip(m, (0.0, y0, -0.28), (0.0, y1, -0.28), 0.04, (0, 0, 1), "trim")
        for k in range(1, 4):
            _strip(m, (x0, y0 + (y1 - y0) * k / 4, -0.275), (x1, y0 + (y1 - y0) * k / 4, -0.275), 0.03, (0, 0, 1), "trim")
        _ring(m, x0, y0, x1, y1, 0.16, 0.0, 0.05, "ground")
        m.box((x0 - 0.25, y0 - 0.25, 0.0), (x1 + 0.25, y0 - 0.16, 0.14), "ground", 0.9, skip=("z-",))
        m.box((x0 - 0.3, y1 + 0.16, 0.0), (x1 + 0.3, y1 + 0.3, 0.1), "ground", 0.9, skip=("z-",))
        return m
    return b


def roof_dormer_attic():
    """LUSITANIA: the agua-furtada attic dormer (roof decor standing on a tile roof, facing +Z): a timber box with a
    sash window and its own little tiled gable"""
    def b():
        m = Mesh()
        m.box((-0.6, -0.3, -1.0), (0.6, 1.2, 0.0), "trim", skip=("y-",))
        m.pane(-0.4, 0.15, 0.4, 1.0, 0.005)
        _ring(m, -0.4, 0.15, 0.4, 1.0, 0.05, 0.0, 0.04, "accent")
        _strip(m, (-0.4, 0.58, 0.045), (0.4, 0.58, 0.045), 0.03, (0, 0, 1), "accent")
        for s in (-1, 1):
            m.quad_facing((s * 0.75, 1.15, 0.15), (s * 0.75, 1.15, -1.0), (0.0, 1.65, -1.0), (0.0, 1.65, 0.15), (s, 1.2, 0), "roof")
        _flat_prism(m, [(-0.58, 1.205), (0.58, 1.205), (0.0, 1.6)], -0.05, 0.0, "trim", 0.9, open_edges=(0,))
        return m
    return b


def pave_calcada():
    """LISBON MARK: calcada portuguesa -- white limestone paving with a black basalt wave running through it"""
    def b():
        m = Mesh()
        m.quad_facing((-HB, 0.0, -HB), (HB, 0.0, -HB), (HB, 0.0, HB), (-HB, 0.0, HB), (0, 1, 0), "trim")
        n = 12
        for band in (-0.6, 0.6):
            for i in range(n):
                x0, x1 = -HB + BAY * i / n, -HB + BAY * (i + 1) / n
                z0 = band + 0.35 * math.sin(i / n * math.tau * 1.5)
                z1 = band + 0.35 * math.sin((i + 1) / n * math.tau * 1.5)
                m.quad_facing((x0, 0.004, z0 - 0.12), (x1, 0.004, z1 - 0.12), (x1, 0.004, z1 + 0.12), (x0, 0.004, z0 + 0.12), (0, 1, 0), "frame", 0.8)
        return m
    return b


def tram_rail():
    """LISBON MARK: tram rails along X in the street, with a yellow electrico standing on them (its body 8 m: the cell
    and half a cell each side), its trolley pole on the wire"""
    def b():
        m = Mesh()
        for z in (-0.5, 0.5):
            m.box((-HB, -0.01, z - 0.03), (HB, 0.015, z + 0.03), "metal", 0.8, skip=("y-", "x-", "x+"))
        L, w, h = 4.0, 1.15, 2.4
        m.box((-L, 0.45, -w), (L, 1.2, w), "accent", skip=())
        m.box((-L + 0.005, 1.205, -w + 0.005), (L - 0.005, 2.245, w - 0.005), "glass", 0.9, skip=("y-", "y+"))
        for k in range(9):
            x = -L + 0.1 + k * (2 * L - 0.2) / 8
            for z in (-w - 0.005, w + 0.005):
                m.box((x - 0.05, 1.2, z - 0.005), (x + 0.05, 2.25, z + 0.005), "accent", 0.9)
        m.box((-L - 0.05, 2.25, -w - 0.05), (L + 0.05, h, w + 0.05), "trim", 0.95)
        for x in (-2.8, 2.8):
            for z in (-0.5, 0.5):
                sub = Mesh()
                sub.cyl(0, 0, 0.35, -0.08, 0.08, "metal", n=8)
                m.add(sub, lambda p, x=x, z=z: (x + p[0], 0.35 + p[2], z - p[1]))
        m.tube((2.0, h, 0.0), (-0.5, h + 2.0, 0.0), 0.02, "metal", n=3)
        return m
    return b


def miradouro_kiosk():
    """LISBON: a miradouro kiosk under a pergola (cell decor): an octagonal glazed kiosk, the pergola beams with a vine
    over them, two cafe tables"""
    def b():
        m = Mesh()
        oc = _octagon(0.7)
        m.prism_xz(oc, 0.0, 0.8, "accent", 0.9)
        m.prism_xz(_octagon(0.68), 0.8, 2.0, "glass", 0.9)
        m.lathe([(0.85, 2.0), (0.75, 2.2), (0.0, 2.5)], "accent", n=8)
        for x in (-1.3, 1.3):
            for z in (-1.3, 1.3):
                m.cyl(x, z, 0.06, 0.0, 2.6, "trim", n=4, caps=False)
        for z in (-1.3, 1.3):
            m.box((-1.45, 2.6, z - 0.05), (1.45, 2.7, z + 0.05), "frame", 0.85)
        for k in range(7):
            x = -1.3 + k * 0.43
            m.box((x - 0.03, 2.7, -1.45), (x + 0.03, 2.76, 1.45), "frame", 0.8)
            _strip(m, (x + 0.2, 2.78, -1.4), (x + 0.2, 2.78, 1.4), 0.25, (0, 1, 0), "plant")
        for (x, z) in ((-0.9, 1.0), (0.9, 1.0)):
            m.cyl(x, z, 0.03, 0.0, 0.72, "metal", n=4)
            m.cyl(x, z, 0.32, 0.72, 0.75, "trim", n=8)
        return m
    return b


# ------------------------------------------------------------------ Manila (r2_manila_estero)
def wall_capiz():
    """MANILA MARK: the bahay na bato's timber upper storey, overhanging 0.5 m: sliding capiz-shell windows (a fine grid
    of pale translucent panes) over the ventanillas (low balustered openings at the floor)"""
    def b():
        m = Mesh()
        z = 0.5
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.4, 0.15, 1.4, 0.65), _rect(-1.4, 0.8, 1.4, 2.55)], z - T, z, "frame", 1.15, reveal_slot="frame")
        m.pane(-1.4, 0.15, 1.4, 0.65, z - 0.2)
        for k in range(14):
            x = -1.35 + k * 0.207
            m.lathe([(0.025, 0.155), (0.045, 0.35), (0.025, 0.645)], "frame", n=4, cx=x, cz=z - 0.1)
        for x0 in (-1.4, -0.7, 0.0, 0.7):                                    # capiz sashes
            m.quad_facing((x0 + 0.02, 0.82, z - 0.12), (x0 + 0.68, 0.82, z - 0.12), (x0 + 0.68, 2.53, z - 0.12), (x0 + 0.02, 2.53, z - 0.12), (0, 0, 1), "trim", 0.95)
            _grid(m, x0 + 0.02, 0.82, x0 + 0.68, 2.53, z - 0.11, 6, 12, 0.02, "frame")
        m.box((-HB, -0.15, -T), (HB, 0.0, z), "frame", 0.75, skip=("z-",))
        for x in (-1.2, 0.0, 1.2):
            m.tube((x, -0.8, 0.02), (x, -0.15, z - 0.1), 0.05, "frame", n=4)
        m.box((-HB, ST - 0.12, z), (HB, ST, z + 0.05), "frame", 0.85, skip=("z-",))
        return m
    return b


def wall_adobe_ground():
    """MANILA: the stone / adobe ground storey of a bahay na bato: coursed blocks, an arched zaguan doorway, a small
    grilled window"""
    def b():
        o = arch("round", 1.4, 2.6, 0.0, n=6)
        m = _wall(K, [o, _rect(0.8, 1.2, 1.25, 1.9)], reveal="ground")
        m.box((-0.69, 0.0, -0.45), (0.69, 1.9, -0.4), "frame", 0.8)
        m.pane(0.8, 1.2, 1.25, 1.9, -0.35)
        for k in range(1, 4):
            _strip(m, (0.8 + 0.45 * k / 4, 1.2, -0.12), (0.8 + 0.45 * k / 4, 1.9, -0.12), 0.02, (0, 0, 1), "metal")
        _arch_band(m, o, 0.12, -0.01, 0.03, "ground", 0.9)
        for y in (0.6, 1.2, 1.8, 2.4, 3.0):                                   # the coursing, round the openings
            cuts = ([(-0.85, 0.85)] if y < 2.75 else []) + ([(0.75, 1.3)] if 1.15 < y < 1.95 else [])
            xs = [-HB] + [v for c in cuts for v in c] + [HB]
            for xa, xb in zip(xs[0::2], xs[1::2]):
                if xb - xa > 0.05:
                    _strip(m, (xa, y, 0.004), (xb, y, 0.004), 0.02, (0, 0, 1), "ground")
        return m
    return b


def ov_shanty_gi():
    """MANILA MARK: a shanty over the estero: plywood and galvanized-iron box on thin stilts, patched walls, a window
    flap, tyres holding down its roof (roof / cell overlay, y 0 = the stilts' footing)"""
    def b():
        m = Mesh()
        for x in (-1.1, 1.1):
            for z in (-1.0, 1.0):
                m.cyl(x, z, 0.05, 0.0, 1.6, "frame", n=4, caps=False)
        m.box((-1.25, 1.6, -1.1), (1.25, 1.7, 1.2), "frame", 0.8)
        m.box((-1.2, 1.7, -1.05), (1.2, 3.6, 1.05), "metal", skip=("y-", "y+"))
        for k, (xa, ya, xb, yb, slot) in enumerate(((-1.2, 1.7, -0.3, 2.9, "wall"), (0.3, 2.3, 1.2, 3.6, "accent"), (-0.6, 2.9, 0.2, 3.6, "frame"))):
            m.quad_facing((xa, ya, 1.055), (xb, ya, 1.055), (xb, yb, 1.055), (xa, yb, 1.055), (0, 0, 1), slot, 0.9)
        m.pane(0.4, 2.0, 1.0, 2.6, 1.06)
        m.quad_facing((0.4, 2.62, 1.06), (1.0, 2.62, 1.06), (1.0, 2.75, 1.45), (0.4, 2.75, 1.45), (0, -1, 1), "metal", 0.8)
        m.quad_facing((-1.4, 3.75, -1.25), (1.4, 3.75, -1.25), (1.4, 3.55, 1.3), (-1.4, 3.55, 1.3), (0, 1, 0.1), "metal", 1.05)
        m.quad_facing((-1.4, 3.72, -1.25), (1.4, 3.72, -1.25), (1.4, 3.52, 1.3), (-1.4, 3.52, 1.3), (0, -1, 0), "metal", 0.6)
        for (x, z) in ((-0.6, -0.4), (0.5, 0.5)):
            m.lathe([(0.2, 3.66), (0.32, 3.7), (0.32, 3.82), (0.2, 3.86)], "frame", n=8, cx=x, cz=z, shade=0.5)
        return m
    return b


def basketball_court():
    """MANILA: a half basketball court (cell decor over 2 x 3 cells: x -1.5..4.5, z -1.5..7.5): painted lines, the hoop on
    its pole and backboard at the -Z end"""
    def b():
        m = Mesh()
        m.quad_facing((-HB, 0.005, -HB), (4.5, 0.005, -HB), (4.5, 0.005, 7.5), (-HB, 0.005, 7.5), (0, 1, 0), "ground", 0.85)
        lines = [((-1.3, -1.3), (4.3, -1.3)), ((-1.3, -1.3), (-1.3, 7.3)), ((4.3, -1.3), (4.3, 7.3)), ((-1.3, 7.3), (4.3, 7.3)),
                 ((0.5, -1.3), (0.5, 3.5)), ((2.5, -1.3), (2.5, 3.5)), ((0.5, 3.5), (2.5, 3.5))]
        for (a, c) in lines:
            _strip(m, (a[0], 0.01, a[1]), (c[0], 0.01, c[1]), 0.06, (0, 1, 0), "accent2")
        for k in range(10):
            a0, a1 = math.pi * k / 10, math.pi * (k + 1) / 10
            _strip(m, (1.5 + 2.6 * math.cos(a0), 0.01, -1.0 + 2.6 * math.sin(a0)), (1.5 + 2.6 * math.cos(a1), 0.01, -1.0 + 2.6 * math.sin(a1)), 0.06, (0, 1, 0), "accent2")
        m.cyl(1.5, -1.45, 0.07, 0.0, 3.3, "metal", n=6)
        m.box((1.5 - 0.06, 3.0, -1.45), (1.5 + 0.06, 3.1, -0.9), "metal")
        m.box((0.95, 2.9, -0.92), (2.05, 3.65, -0.88), "trim")
        ring = [(1.5 + 0.23 * math.cos(math.tau * k / 8), 3.05, -0.65 + 0.23 * math.sin(math.tau * k / 8)) for k in range(9)]
        for a, c in zip(ring, ring[1:]):
            m.tube(a, c, 0.012, "accent", n=3)
        return m
    return b


def ov_jeepney():
    """MANILA MARK: a parked jeepney along X (street decor): the long bench body with its chrome hood and bonnet
    ornaments, painted panels, a roof rack, wheels"""
    def b():
        m = Mesh()
        m.box((-2.3, 0.45, -0.85), (1.3, 1.3, 0.85), "accent", skip=())
        m.box((-2.295, 1.305, -0.845), (1.295, 1.945, 0.845), "glass", 0.8, skip=("y-", "y+"))
        for k in range(6):
            x = -2.25 + k * 0.7
            for z in (-0.855, 0.855):
                m.box((x - 0.04, 1.3, z - 0.004), (x + 0.04, 1.95, z + 0.004), "accent", 0.9)
        m.box((-2.35, 1.95, -0.9), (1.35, 2.08, 0.9), "accent2")
        m.box((1.3, 0.5, -0.75), (2.4, 1.15, 0.75), "metal", 1.2)
        m.box((1.3, 1.15, -0.8), (1.6, 1.95, 0.8), "glass", 0.8, skip=("y-", "y+"))
        for k in range(5):
            _strip(m, (2.41, 0.6 + k * 0.1, -0.5), (2.41, 0.6 + k * 0.1, 0.5), 0.04, (1, 0, 0), "trim")
        m.lathe([(0.0, 1.15), (0.06, 1.2), (0.0, 1.45)], "metal", n=4, cx=2.2)
        for k in range(8):
            _strip(m, (-2.2 + k * 0.45, 2.1, -0.85), (-2.2 + k * 0.45, 2.1, 0.85), 0.05, (0, 1, 0), "metal")
        for x in (-1.5, 1.7):
            for z in (-0.85, 0.85):
                sub = Mesh()
                sub.cyl(0, 0, 0.38, -0.12, 0.12, "frame", n=8)
                m.add(sub, lambda p, x=x, z=z: (x + p[0], 0.38 + p[2], z - p[1]))
        return m
    return b


# ------------------------------------------------------------------ register
CC = ["caucasian_balcony"]
PIECES["wall_tbilisi_balcony_lite_t"] = _w("wall", wall_tbilisi_balcony_lite(), CC, lod1="keep", notes="Tbilisi balcony <= 300 tris (budget pass)")
PIECES["wall_shushabandi_t"] = _w("wall", wall_shushabandi(), CC, lod1="keep", notes="TBILISI MARK: stained-glass gallery 0.6 m out")
for p in ("base", "shaft", "top"):
    PIECES[f"svan_tower_{p}"] = _w("cell", svan_tower(p), CC, lod1="keep", kind="tower", notes=f"CAUCASUS MARK: Svan tower {p} (base xN, shaft, top)")
PIECES["dome_bath_brick"] = _w("cell", dome_bath_brick(), CC, lod1="keep", kind="crown", notes="low brick bath dome with a lit lantern")
PIECES["stair_spiral_courtyard"] = _w("cell", stair_spiral_courtyard(), CC, lod1="keep", kind="stair", notes="spiral iron stair, a storey, landing to -Z")
CY = ["cycladic"]
PIECES["chapel_cycladic"] = _w("cell", chapel_cycladic(), CY, lod1="keep", kind="crown", notes="CYCLADES MARK: white chapel, blue dome, bell gable to +Z")
PIECES["windmill_round"] = _w("cell", windmill_round(), CY, lod1="keep", kind="tower", notes="CYCLADES MARK: round windmill, 3 storeys, sails to +Z")
PIECES["edge_parapet_lip_k"] = _w("edge", edge_parapet_lip(), CY, lod1="keep", notes="rounded whitewashed roof lip (~30 tris)")
PIECES["pave_slate_whitejoint"] = _w("cell", pave_slate_whitejoint(), CY, kind="ground", notes="slate slabs, white joints")
PIECES["stair_external_white"] = _w("wall", stair_external_white(), CY, kind="stair", notes="external masonry stair up a face along +X, 0.85 m out")
HK2 = ["hakka_tulou"]
PIECES["tulou_ring_wall"] = _w("wall", tulou_ring_wall(), HK2, notes="HAKKA MARK: rammed-earth ring bay (bent for R ~20 m), granite base, slits")
PIECES["tulou_gallery_ring"] = _w("wall", tulou_gallery_ring(), HK2, lod1="keep", notes="HAKKA MARK: inner gallery storey (bent for R ~20 m)")
PIECES["roof_ring_tile"] = _w("cell", roof_ring_tile(), HK2, lod1="keep", kind="roof", notes="ring roof segment: ridge along Z, outer eave 2.5 m to +X")
PIECES["tulou_gate"] = _w("wall", tulou_gate(), HK2, notes="HAKKA MARK: granite-framed gate, plaque")
PIECES["ancestral_hall"] = _w("cell", ancestral_hall(), HK2 + ["jiangnan_water"], lod1="keep", kind="crown", notes="ancestral hall pavilion")
JN = ["jiangnan_water"]
PIECES["edge_horsehead_wall"] = _w("edge", edge_horsehead_wall(), JN + ["hakka_tulou"], lod1="keep", kind="crown", notes="JIANGNAN MARK: stepped horse-head firewall")
PIECES["roof_black_tile_curved"] = _w("cell", roof_black_tile(False), JN, lod1="keep", kind="roof", notes="black tile gable segment, concave, ridge along Z")
PIECES["roof_black_tile_curved_end"] = _w("cell", roof_black_tile(True), JN, lod1="keep", kind="roof", notes="its end segment (gable at -Z, kicked-up ridge end)")
PIECES["wall_shopboards_t"] = _w("wall", wall_shopboards(), JN + ["hakka_tulou", "viet_tube"], notes="removable timber shop boards, sign")
PIECES["wall_moon_gate"] = _w("wall", wall_moon_gate(), JN, notes="JIANGNAN MARK: round moon gate, tile coping")
PIECES["bridge_humpback_stone"] = _w("cell", bridge_humpback_stone(), JN, lod1="keep", kind="bridge", span=(1, 3), notes="JIANGNAN MARK: humpbacked stone bridge along +Z")
PIECES["water_steps_private"] = _w("cell", water_steps_private(), JN + ["siam_khlong"], collide="ramp", kind="stair", notes="private steps down 1.6 m along +Z on the -X side")
KN = ["knights_harbour"]
PIECES["wall_gallarija_k"] = _w("wall", wall_gallarija(), KN, lod1="keep", notes="MALTA MARK: enclosed painted timber balcony 1.2 m")
PIECES["corner_statue_niche"] = _w("corner", corner_statue_niche(), KN + ["tyrrhenian_canyon"], lod1="drop", collide=False, kind="decor",
                                   notes="saint in a lit niche at y 3.2, facing the corner diagonal")
PIECES["stair_knight"] = _w("cell", stair_knight(), KN, collide="ramp", kind="stair", span=(1, 2), notes="low-riser stair street, 1.6 m over 6 m along +Z")
PIECES["bastion_wall_slope"] = _w("wall", bastion_wall_slope(), KN, lod1="keep", notes="MALTA MARK: sloped bastion wall, 2 storeys, cordon, parapet")
KO = ["korean_hillside"]
PIECES["ov_jangdok_jars"] = _w("cell", ov_jangdok_jars(), KO, lod1="drop", kind="overlay", notes="KOREA MARK: jangdokdae jars (accent = brown)")
PIECES["roof_painted_green"] = _w("cell", roof_painted_green(), KO, kind="roof", notes="green-painted flat roof (accent), lip")
PIECES["oktapbang"] = _w("cell", oktapbang(), KO, lod1="keep", kind="crown", notes="KOREA MARK: rooftop room with a tank")
KU = ["kulla_stone"]
PIECES["roof_stone_slab_steep"] = _w("cell", roof_stone_slab(False), KU + ["scots_lands"], lod1="keep", kind="roof", notes="32-deg stone-slab gable segment, deep eaves")
PIECES["roof_stone_slab_steep_end"] = _w("cell", roof_stone_slab(True), KU + ["scots_lands"], lod1="keep", kind="roof", notes="its end segment (gable at -Z)")
PIECES["wall_window_band_k"] = _w("wall", wall_window_band(), KU, lod1="keep", notes="KULLA MARK: corbelled window-band top storey")
PIECES["wall_arrow_slit_k"] = _w("wall", PIECES["wall_slit_k"]["build"], KU, notes="= wall_slit_k")
PIECES["chimney_stone"] = _w("cell", chimney_stone(), KU + ["scots_lands", "nouvelle_france"], lod1="keep", kind="overlay", notes="stone chimney stack with slab cap")
PIECES["ov_machicolation"] = _w("wall", ov_machicolation(), KU + ["omani_oasis"], lod1="keep", kind="overlay", notes="machicolation box over a door")
LU = ["lusitanian_hill"]
PIECES["wall_azulejo_k"] = _w("wall", wall_azulejo(), LU, notes="LISBON MARK: azulejo-clad bay, iron cage balcony")
PIECES["wall_granite_window_k"] = _w("wall", wall_granite_window(), LU, notes="tall window in a granite frame (ground slot)")
PIECES["roof_dormer_attic"] = _w("cell", roof_dormer_attic(), LU, lod1="keep", kind="overlay", notes="attic dormer facing +Z")
PIECES["pave_calcada"] = _w("cell", pave_calcada(), LU, kind="ground", notes="LISBON MARK: black-and-white calcada")
PIECES["tram_rail"] = _w("cell", tram_rail(), LU, lod1="keep", kind="overlay", notes="LISBON MARK: rails along X with an 8 m tram")
PIECES["miradouro_kiosk"] = _w("cell", miradouro_kiosk(), LU, lod1="keep", notes="kiosk under a vine pergola")
MA = ["manila_estero"]
PIECES["wall_capiz_t"] = _w("wall", wall_capiz(), MA, lod1="keep", notes="MANILA MARK: capiz sashes over ventanillas, 0.5 m overhang")
PIECES["wall_adobe_ground_k"] = _w("wall", wall_adobe_ground(), MA, notes="stone ground storey, arched zaguan, grilled window")
PIECES["ov_shanty_gi"] = _w("cell", ov_shanty_gi(), MA + ["latin_hillside"], lod1="keep", kind="crown", notes="MANILA MARK: shanty on stilts, tyres on the roof")
PIECES["basketball_court"] = _w("cell", basketball_court(), MA + ["korean_hillside"], lod1="keep", kind="ground", span=(2, 3), notes="half court over 2 x 3 cells")
PIECES["ov_jeepney"] = _w("cell", ov_jeepney(), MA, lod1="keep", kind="overlay", notes="MANILA MARK: parked jeepney along X")

for civ, acc, extra in (("cycladic", ("#2a5aa8", "#e8e2d2"), {"trim": "#f4f4ef"}), ("hakka_tulou", ("#a8322a", "#c9a23a"), {}),
                        ("jiangnan_water", ("#2a2622", "#c9a23a"), {"roof": "#3a3a3c"}), ("knights_harbour", ("#2a6a4a", "#c9a23a"), {}),
                        ("korean_hillside", ("#3f8a5a", "#3a7ab0"), {}), ("kulla_stone", ("#5a3a26", "#e8e2d2"), {}),
                        ("lusitanian_hill", ("#2a4a9a", "#c9a23a"), {"tile": "#3a6ab0", "accent": "#e0b030"}), ("manila_estero", ("#6b4a2e", "#f2c43a"), {}),
                        ("caucasian_balcony", None, {})):
    for i, v in enumerate(PALETTES.get(civ, [])):
        if acc:
            v["accent"], v["accent2"] = acc
        v.update(extra)
for i, v in enumerate(PALETTES.get("manila_estero", [])):
    v["accent"] = ["#b0322a", "#2a6ab0", "#f2c43a", "#3f8a5a"][i % 4]                 # (jeepney / shanty paint)
for v in PALETTES.get("korean_hillside", []):
    v["accent"], v["accent2"], v["tile"] = "#3f8a5a", "#6b4a2e", "#3a7ab0"         # green roofs, brown jars, blue tanks
