"""pieces_b6.py -- warren kit batch 4c: the older families' marks brought up to the Newar standard (maghrebi_medina,
kowloon_walled, siam_khlong), and the generator's requests for cairene_mamluk, levantine_courtyard, saharan_kasbah,
newar and hejazi_roshan.
"""
import math

from geom import Mesh, _dedupe, arch
from pieces import BAY, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall
from pieces_b4 import _flat_prism, _gable_seg
from pieces_b5 import _bell, _door_leaf, _frustum, _u_frame
from pieces_marks import _beads, _chochin, _corbel, _crest, _diag, _hip, _lightbox, _off, _place, _ring, roof_pagoda


# ------------------------------------------------------------------ helpers
def _stud_grid(m, x0, y0, x1, y1, z, nx, ny, s=0.03):
    for i in range(nx):
        for j in range(ny):
            x = x0 + (x1 - x0) * (i + 0.5) / nx
            y = y0 + (y1 - y0) * (j + 0.5) / ny
            m.quad_facing((x - s, y - s, z), (x + s, y - s, z), (x + s, y + s, z), (x - s, y + s, z), (0, 0, 1), "metal")


def _checker(m, x0, y0, x1, y1, nx, ny, z, a="tile", b="trim"):
    """a zellige checker of flat squares (two slots)"""
    w, h = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            xa, ya = x0 + i * w + 0.01, y0 + j * h + 0.01
            m.quad_facing((xa, ya, z), (xa + w - 0.02, ya, z), (xa + w - 0.02, ya + h - 0.02, z), (xa, ya + h - 0.02, z), (0, 0, 1), a if (i + j) % 2 else b)


def _voussoirs(m, o, z, n, slot_a="accent", slot_b="trim", w=0.16):
    """alternating voussoir blocks round an arch outline's head (striped ablaq / Cordoban arch): flat quads"""
    pts = o[2:] if len(o) > 4 else o
    pts = [p for p in pts if p[1] > min(q[1] for q in o) + 0.4]
    ring = _off(o, w)
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        na = _nearest(ring, a)
        nb = _nearest(ring, b)
        m.quad_facing((a[0], a[1], z), (b[0], b[1], z), (nb[0], nb[1], z), (na[0], na[1], z), (0, 0, 1), slot_a if k % 2 else slot_b)


def _arch_band(m, o, w, z0, z1, slot, shade=1.0):
    """the moulded band round a door / passage arch, stopping at the threshold (y 0) instead of wrapping under it"""
    from shapely.geometry import Polygon, box as sbox
    g = Polygon(_off(o, w)).difference(Polygon(_off(o, 0.03))).intersection(sbox(-50, 0.0, 50, 50))   # (3 cm off the reveal)
    for q in getattr(g, "geoms", [g]):
        if q.geom_type == "Polygon" and q.area > 1e-4:
            m.wall_cut(_dedupe([tuple(p) for p in list(q.exterior.coords)[:-1]]), [], z0, z1, slot, shade)


def _nearest(ring, p):
    return min(ring, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)


def _ribbed_dome(m, r, y0, h, n=16, slot="wall", drum=0.0, sh=(1.0, 0.82)):
    """a dome whose gores alternate shade (reads as carved ribs / tile gores), on an optional drum"""
    if drum:
        m.cyl(0, 0, r, y0, y0 + drum, slot, n=n, caps=False)
        y0 += drum
    prof = [(r * math.cos(math.pi / 2 * k / 5), y0 + h * math.sin(math.pi / 2 * k / 5)) for k in range(6)]
    for i in range(len(prof) - 1):
        (r0, ya), (r1, yb) = prof[i], prof[i + 1]
        for k in range(n):
            a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
            p0 = (r0 * math.cos(a0), ya, -r0 * math.sin(a0))
            p1 = (r0 * math.cos(a1), ya, -r0 * math.sin(a1))
            q1 = (r1 * math.cos(a1), yb, -r1 * math.sin(a1))
            q0 = (r1 * math.cos(a0), yb, -r1 * math.sin(a0))
            out = (math.cos((a0 + a1) / 2), 0.4, -math.sin((a0 + a1) / 2))
            if r1 < 1e-6:
                m.tri_facing(p0, p1, (0.0, yb, 0.0), out, slot, sh[k % 2])
            else:
                m.quad_facing(p0, p1, q1, q0, out, slot, sh[k % 2])


def _octagon(r, rot=math.pi / 8):
    return [(r * math.cos(math.tau * k / 8 + rot), -r * math.sin(math.tau * k / 8 + rot)) for k in range(8)]


# ------------------------------------------------------------------ Maghrebi medina: the marks, upgraded
def wall_door_portal():
    """MEDINA MARK: the horseshoe-arched cedar door in its full Marinid frame: studded leaves, a voussoir band of
    alternating stucco and tile, a rectangular alfiz with zellige spandrels, a carved stucco frieze, zellige dado
    panels each side, and a little green-tiled canopy on carved corbels"""
    def b():
        o = arch("horseshoe", 1.3, 2.6, 0.0, n=8)
        m = _wall(K, [o])
        g = -0.38
        m.wall_cut(o, [], g - 0.08, g, "frame")
        _stud_grid(m, -0.55, 0.25, 0.55, 2.0, g + 0.005, 4, 6)
        m.cyl(0.0, g + 0.05, 0.06, 1.25, 1.29, "metal", n=6)
        alfiz = _rect(-0.95, 0.0, 0.95, 3.0)
        m.wall_cut(alfiz, [_off(o, 0.17)], -0.01, 0.025, "tile")                         # zellige spandrels
        _voussoirs(m, o, 0.03, 12)
        _arch_band(m, o, 0.17, -0.01, 0.028, "trim")
        _u_frame(m, -0.95, 3.0, 0.95, 0.08, 0.0, 0.05, "trim")
        _beads(m, -0.95, 0.95, 2.88, 2.98, 0.025, 0.05, 10, "trim", 0.85)
        for x0 in (-1.45, 1.05):                                                         # zellige dado
            _checker(m, x0, 0.0, x0 + 0.4, 1.1, 2, 5, 0.012)
        for x in (-0.8, 0.8):
            _corbel(m, x, 3.08, 0.38, 0.3, 0.1, "frame", 0.85)
        m.quad_facing((-1.05, 3.2, 0.0), (1.05, 3.2, 0.0), (1.05, 3.0, 0.45), (-1.05, 3.0, 0.45), (0, 1, 0.6), "roof")
        m.quad_facing((-1.05, 3.17, 0.0), (1.05, 3.17, 0.0), (1.05, 2.97, 0.45), (-1.05, 2.97, 0.45), (0, -1, -0.6), "frame", 0.55)
        for k in range(8):
            x = -0.95 + k * 0.27
            _strip(m, (x, 3.02, 0.43), (x, 3.19, 0.02), 0.08, (0, 1, 0.6), "roof")
        return m
    return b


def wall_arch_medina(t):
    """MEDINA: the horseshoe passage arch with alternating voussoirs, an alfiz and zellige spandrels"""
    def b():
        o = arch("horseshoe", 2.0, 2.85, 0.0, n=8)
        m = _wall(t, [o])
        _arch_band(m, o, 0.2, -0.01, 0.03, "trim")
        _voussoirs(m, o, 0.034, 14, w=0.2)
        alf = _rect(-1.35, 0.0, 1.35, 3.12)
        m.wall_cut(alf, [_off(o, 0.2)], -0.01, 0.02, "tile", 0.9)
        _u_frame(m, -1.35, 3.12, 1.35, 0.06, 0.0, 0.045, "trim")
        return m
    return b


def minaret_shaft_medina():
    """MEDINA MARK: the Almohad minaret's shaft storey -- a lobed blind arch, a sebka lozenge net over it in relief, a
    glazed tile band, a slit window"""
    def b():
        m = Mesh()
        w = 1.4
        m.box((-w, 0.0, -w), (w, ST, w), "wall", skip=("y-", "y+"))
        for side in range(4):
            e = Mesh()
            o = arch("lobed", 1.0, 1.7, 0.35, n=2)
            e.wall_cut(_off(o, 0.1), [_off(o, 0.005)], -0.01, 0.03, "trim")
            e.wall_cut(o, [], 0.0, 0.012, "tile")
            for i in range(3):                                                          # the sebka net
                cx = -0.8 + i * 0.8
                pts = [(cx, 2.2), (cx + 0.3, 2.5), (cx, 2.8), (cx - 0.3, 2.5)]
                for p, q in zip(pts, pts[1:] + pts[:1]):
                    _strip(e, (p[0], p[1], 0.01), (q[0], q[1], 0.01), 0.05, (0, 0, 1), "trim")
            _checker(e, -w, 2.9, w, 3.08, 6, 1, 0.012)
            m.add(e, lambda p, s=side: _rot(s)((p[0], p[1], p[2] + w)))
        return m
    return b


def _rot(s):
    from geom import rot_y
    return rot_y(90 * s)


# ------------------------------------------------------------------ Kowloon: a dense hero bay
def wall_kowloon_stack():
    """KOWLOON MARK: the dense bay of the walled city -- a caged window, an AC unit on a bracket dripping down a pipe, a
    laundry pole with clothes, a down pipe and a cable run, a small lit sign, a tin canopy"""
    def b():
        m = _wall(T, [_rect(-0.9, 0.9, 0.4, 2.2)])
        m.pane(-0.9, 0.9, 0.4, 2.2, -0.12)
        d = 0.55
        for k in range(8):                                                              # the cage
            x = -1.0 + 1.5 * k / 7
            _strip(m, (x, 0.8, d), (x, 2.35, d), 0.02, (0, 0, 1), "metal")
        for y in (1.2, 1.8):
            _strip(m, (-1.0, y, d + 0.004), (0.5, y, d + 0.004), 0.02, (0, 0, 1), "metal")
        m.box((-1.03, 0.76, 0.0), (0.53, 0.82, d + 0.02), "metal", 0.8)
        m.box((-1.03, 2.33, 0.0), (0.53, 2.39, d + 0.02), "metal", 0.8)
        m.quad_facing((-1.15, 2.6, 0.0), (0.65, 2.6, 0.0), (0.65, 2.45, d + 0.2), (-1.15, 2.45, d + 0.2), (0, 1, 0.3), "roof")
        m.box((0.7, 1.9, 0.0), (1.4, 2.4, 0.5), "trim", 0.9, skip=("z-",))                 # AC unit
        m.wall_cut([(1.05 + 0.18 * math.cos(math.tau * k / 8), 2.15 + 0.18 * math.sin(math.tau * k / 8)) for k in range(8)], [], 0.5, 0.51, "metal")
        for x in (0.8, 1.3):
            m.tube((x, 1.9, 0.02), (x, 1.75, 0.45), 0.015, "metal", n=3)
        m.tube((1.35, 1.9, 0.3), (1.35, 0.0, 0.3), 0.015, "frame", n=3)
        m.tube((-1.4, 2.0, 0.0), (-1.4, 2.0, 1.4), 0.018, "metal", n=3)                  # laundry pole
        for k, slot in enumerate(("fabric", "accent2", "fabric", "trim")):
            z = 0.4 + k * 0.25
            m.quad_facing((-1.4 - 0.12, 2.0, z), (-1.4 + 0.12, 2.0, z), (-1.4 + 0.12, 1.45 + 0.08 * (k % 2), z), (-1.4 - 0.12, 1.45 + 0.08 * (k % 2), z), (0, 0, 1), slot)
            m.quad_facing((-1.4 - 0.12, 2.0, z - 0.005), (-1.4 + 0.12, 2.0, z - 0.005), (-1.4 + 0.12, 1.45 + 0.08 * (k % 2), z - 0.005), (-1.4 - 0.12, 1.45 + 0.08 * (k % 2), z - 0.005), (0, 0, -1), slot, 0.8)
        m.tube((0.6, 0.0, 0.08), (0.6, ST, 0.08), 0.05, "metal", n=5)                     # down pipe
        m.tube((-HB, 2.95, 0.05), (HB, 2.85, 0.05), 0.02, "frame", n=3)                    # cable run
        _lightbox(m, 0.75, 0.9, 1.4, 1.35, 0.02, 0.14, nchar=2)
        return m
    return b


# ------------------------------------------------------------------ Siam (r2_siam_khlong)
def roof_thai_gable():
    """SIAM MARK: the steep layered Thai gable roof over a cell (ridge along Z): two overlapping tiers, the lower one
    spreading wider, gilt naga barge boards on the gable ends rising to chofa horns, nok hang tips at the eaves"""
    def b():
        m = Mesh()
        for k, (pitch, eave, y0, z0, z1) in enumerate(((58, 0.7, 0.0, -HB, HB), (58, 0.25, 0.75, -1.1, 1.1))):
            tn = math.tan(math.radians(pitch))
            h = HB * tn * (0.75 if k else 1.0)
            half = (HB if k == 0 else 1.1)
            lx = half + eave
            ly = y0 - eave * tn
            for s in (-1, 1):
                m.quad_facing((s * lx, ly, z0), (s * lx, ly, z1), (0.0, y0 + half * tn, z1), (0.0, y0 + half * tn, z0), (s * tn, 1, 0), "roof", 1.0 - 0.06 * k)
                m.quad_facing((s * lx, ly - 0.05, z0), (s * lx, ly - 0.05, z1), (s * half, y0 - 0.02, z1), (s * half, y0 - 0.02, z0), (0, -1, 0), "frame", 0.55)
            for z in (z0, z1):                                                          # naga barge boards
                for s in (-1, 1):
                    _strip(m, (s * lx, ly + 0.05, z + (0.02 if z > 0 else -0.02)), (0.0, y0 + half * tn + 0.05, z + (0.02 if z > 0 else -0.02)), 0.09, (0, 0, 1 if z > 0 else -1), "accent")
                    m.tube((s * lx, ly + 0.05, z), (s * (lx + 0.15), ly + 0.3, z), 0.03, "accent", n=3)   # nok hang
                top = y0 + half * tn
                m.tube((0.0, top, z), (0.0, top + 0.35, z + (0.12 if z > 0 else -0.12)), 0.035, "accent", n=4)  # chofa
                m.tube((0.0, top + 0.35, z + (0.12 if z > 0 else -0.12)), (0.0, top + 0.45, z + (0.02 if z > 0 else -0.02)), 0.025, "accent", n=3)
        gab = [(-HB + 0.08, 0.0), (HB - 0.08, 0.0), (0.0, HB * math.tan(math.radians(58)) - 0.14)]
        _flat_prism(m, gab, -HB + 0.02, -HB + 0.15, "accent2", open_edges=(0,))
        _flat_prism(m, gab, HB - 0.15, HB - 0.02, "accent2", open_edges=(0,))
        return m
    return b


def wall_thai_teak():
    """SIAM: a teak house wall of fa pakon raised panels in a timber frame, a window with its shutters swung open, the
    whole wall leaning in a little"""
    def b():
        m = Mesh()
        op = _rect(-0.45, 1.0, 0.45, 2.1)
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [op], -T, 0.0, "wall", reveal_slot="frame")
        m.pane(-0.45, 1.0, 0.45, 2.1, -0.12)
        for x in (-HB + 0.005, -0.55, 0.55, HB - 0.085):
            m.box((x, 0.005, 0.0), (x + 0.08, ST - 0.005, 0.05), "frame", skip=("z-",))
        for y in (0.005, 0.95, 2.15, ST - 0.085):
            m.box((-HB + 0.07, y, 0.0), (HB - 0.07, y + 0.08, 0.04), "frame", 0.9, skip=("z-",))
        for xa, xb in ((-1.42, -0.55), (0.63, 1.42)):                                   # raised panels
            for ya, yb in ((0.08, 0.95), (1.03, 2.15), (2.23, ST - 0.08)):
                m.box((xa + 0.08, ya + 0.08, 0.0), (xb - 0.08, yb - 0.08, 0.025), "wall", 1.08, skip=("z-",))
        for s in (-1, 1):
            m.box((0.47 if s > 0 else -0.92, 1.01, 0.0), (0.92 if s > 0 else -0.47, 2.09, 0.045), "frame", 0.8, skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ Cairo (r1_cairene_mamluk)
def wall_mashrabiya_box():
    """CAIRO MARK: the turned-bead mashrabiya oriel, two tiers each stepping further out (0.5 then 0.75 m), fine bead
    lattice front and sides, carved corbels, a crest"""
    def b():
        m = _wall(K, [_rect(-0.8, 0.3, 0.8, 2.9)], reveal="frame")
        m.pane(-0.8, 0.3, 0.8, 2.9, -0.3)
        x0, x1 = -1.0, 1.0
        for x in (-0.8, 0.0, 0.8):
            _corbel(m, x, 0.2, 0.45, 0.7, 0.12, "frame", 0.85)
        for k, (ya, yb, d) in enumerate(((0.2, 1.55, 0.5), (1.55, 2.95, 0.75))):
            m.box((x0 - 0.05 * k, ya - 0.08, 0.0), (x1 + 0.05 * k, ya + 0.04, d), "frame", 0.85, skip=("z-",))
            m.pane(x0 + 0.06, ya + 0.1, x1 - 0.06, yb - 0.06, d - 0.06)
            _lattice(m, x0 - 0.05 * k, ya + 0.04, x1 + 0.05 * k, yb, d - 0.05, d, 12, 9)
            for side in (-1, 1):
                xa, xb = (0.06, d - 0.06) if side < 0 else (-(d - 0.06), -0.06)
                sub = Mesh()
                _lattice(sub, xa, ya + 0.04, xb, yb, -0.05, 0.0, 4, 9)
                _place(m, sub, 90 * side, dx=(x1 + 0.05 * k) if side > 0 else (x0 - 0.05 * k))
        m.box((x0 - 0.15, 2.95, 0.0), (x1 + 0.15, 3.07, 0.85), "frame", skip=("z-",))
        _crest(m, x0 - 0.15, x1 + 0.15, 3.07, 0.12, 0.85, 12, "frame")
        return m
    return b


def wall_ablaq_portal():
    """CAIRO / LEVANT MARK: the ablaq portal -- a pointed arch door recessed in a tall frame of alternating dark and light
    stone courses, a joggled voussoir lintel, a stepped muqarnas hood in the arch head"""
    def b():
        o = arch("pointed", 1.4, 3.05, 0.0, n=8)
        m = _wall(K, [o])
        _door_leaf(m, -0.7, 2.3, 0.7, -0.45, "frame", studs=0)                          # (1.4 x 2.3 m clear)
        m.wall_cut(o, [_rect(-0.7, -1.0, 0.7, 2.35)], -0.47, -0.43, "trim", 0.9)        # the tympanum over the door
        for j in range(3):                                                             # muqarnas tiers
            yb = 2.38 + j * 0.2
            for i in range(5 - j):
                x = -0.55 + j * 0.12 + i * 0.25
                m.box((x, yb, -0.43), (x + 0.2, yb + 0.18, -0.43 + 0.08 + 0.06 * j), "trim", 0.8 + 0.06 * (i % 2), skip=("z-",))
        frame = _rect(-1.2, 0.0, 1.2, 3.2)
        n = 8
        for k in range(n):                                                             # ablaq courses
            ya, yb = k * (ST - 0.12) / n, (k + 1) * (ST - 0.12) / n
            band = _rect(-1.2, ya, 1.2, yb)
            from shapely.geometry import Polygon
            g = Polygon(band).difference(Polygon(_off(o, 0.18)))
            for q in getattr(g, "geoms", [g]):
                if q.geom_type == "Polygon" and q.area > 1e-3:
                    m.wall_cut(_dedupe([tuple(p) for p in list(q.exterior.coords)[:-1]]), [], 0.0, 0.015, "accent" if k % 2 else "trim")
        _voussoirs(m, o, 0.02, 12, "accent", "trim", w=0.18)
        _arch_band(m, o, 0.18, -0.01, 0.017, "trim", 0.85)
        m.box((-1.25, ST - 0.12, 0.0), (1.25, ST, 0.08), "trim", skip=("z-",))
        return m
    return b


def minaret_mamluk(part):
    """CAIRO MARK: the Mamluk minaret, a cell a part: base (square, ablaq bands, a keel-arched niche; stack it), shaft
    (octagonal, keel niches, a muqarnas balcony with its railing), top (a columned pavilion and the bulb finial)"""
    def b():
        m = Mesh()
        if part == "base":
            a = 1.3
            m.box((-a, 0.0, -a), (a, ST, a), "wall", skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                for j in range(4):
                    y = 0.4 + j * 0.75
                    sub.quad_facing((-a, y, a + 0.005), (a, y, a + 0.005), (a, y + 0.18, a + 0.005), (-a, y + 0.18, a + 0.005), (0, 0, 1), "accent")
                o = arch("pointed", 0.6, 1.4, 0.9, n=6)
                sub.wall_cut(_off(o, 0.08), [o], a - 0.01, a + 0.03, "trim")
                sub.wall_cut(o, [], a - 0.1, a - 0.06, "frame", 0.6)
                _place(m, sub, 90 * k)
        elif part == "shaft":
            r = 1.05
            oc = _octagon(r)
            m.prism_xz(oc, 0.0, 2.4, "wall")
            for k in range(8):
                a0 = math.tau * k / 8 + math.pi / 8
                a1 = a0 + math.tau / 8
                mid = (a0 + a1) / 2
                c = r * math.cos(math.pi / 8)
                sub = Mesh()
                o = arch("pointed", 0.3, 1.2, 0.6, n=4)
                sub.wall_cut(o, [], 0.004, 0.01, "frame", 0.5)
                _place(m, sub, -math.degrees(mid) + 90, dx=c * math.cos(mid), dz=-c * math.sin(mid))
            for j in range(3):                                                         # muqarnas corbel tiers
                rr = r + 0.12 * (j + 1)
                m.prism_xz(_octagon(rr), 2.4 + j * 0.18, 2.58 + j * 0.18, "trim", 0.85 + 0.05 * j)
            m.prism_xz(_octagon(1.5), 2.94, 3.0, "trim")
            oc2 = _octagon(1.45)
            for k in range(8):
                p, q = oc2[k], oc2[(k + 1) % 8]
                m.tube((p[0], 3.55, p[1]), (q[0], 3.55, q[1]), 0.025, "frame", n=3)
                m.tube((p[0], 3.0, p[1]), (p[0], 3.55, p[1]), 0.02, "frame", n=3)
        else:
            for k in range(8):
                a = math.tau * k / 8 + math.pi / 8
                m.cyl(0.7 * math.cos(a), -0.7 * math.sin(a), 0.07, 0.0, 1.6, "trim", n=4, caps=False)
            m.prism_xz(_octagon(0.85), 1.6, 1.8, "trim")
            m.cyl(0, 0, 0.45, 0.0, 1.6, "wall", n=8, caps=False)
            m.lathe([(0.55, 1.8), (0.62, 2.1), (0.5, 2.4), (0.25, 2.7), (0.08, 2.85), (0.0, 2.9)], "trim", n=10)
            m.lathe([(0.0, 2.85), (0.07, 3.0), (0.0, 3.1), (0.06, 3.2), (0.0, 3.5)], "accent2", n=6)
        return m
    return b


def dome_ribbed():
    """CAIRO MARK: the carved stone dome of a Mamluk tomb on its drum, its gores carved in alternating ribs, a finial"""
    def b():
        m = Mesh()
        m.box((-1.4, 0.0, -1.4), (1.4, 0.5, 1.4), "wall", skip=("y-",))
        m.prism_xz(_octagon(1.3), 0.5, 1.1, "wall", 0.95)
        _ribbed_dome(m, 1.15, 1.1, 1.6, n=16, slot="trim", drum=0.3, sh=(1.0, 0.78))
        m.lathe([(0.0, 2.95), (0.08, 3.05), (0.03, 3.25), (0.06, 3.35), (0.0, 3.6)], "accent2", n=6)
        return m
    return b


def malqaf_scoop():
    """the malqaf: the roof wind scoop, its slanted mouth to +Z (the prevailing wind), lattice in the mouth"""
    def b():
        m = Mesh()
        p = [(-0.6, 0.0), (0.6, 0.0), (0.6, 1.4), (-0.6, 1.4)]
        m.box((-0.6, 0.0, -0.5), (0.6, 1.4, 0.3), "wall", skip=("y-", "z+"))
        m.quad_facing((-0.65, 1.4, -0.55), (0.65, 1.4, -0.55), (0.65, 1.9, 0.35), (-0.65, 1.9, 0.35), (0, 1, -0.6), "wall", 0.9)
        _flat_prism(m, [(0.0, 1.4), (0.9, 1.4), (0.0, 1.9)], -0.6, -0.55, "wall", 0.85)
        sub = Mesh()
        _flat_prism(sub, [(0.0, 1.4), (0.9, 1.4), (0.0, 1.9)], 0.55, 0.6, "wall", 0.85)
        m.add(sub)
        m.wall_cut(_rect(-0.6, 0.2, 0.6, 1.9), [_rect(-0.5, 0.3, 0.5, 1.75)], 0.3, 0.36, "wall")
        _lattice(m, -0.5, 0.3, 0.5, 1.75, 0.28, 0.33, 4, 6, slot="frame")
        return m
    return b


def pigeon_cote():
    """the mud pigeon tower on a roof: a tapering whitewashed cone, rows of clay-pot holes, perch sticks"""
    def b():
        m = Mesh()
        m.lathe([(0.95, 0.0), (0.85, 1.2), (0.6, 2.4), (0.35, 3.1), (0.0, 3.3)], "wall", n=10)
        for j in range(4):
            y = 0.5 + j * 0.6
            r = 0.95 - (0.95 - 0.35) * y / 3.1 + 0.01
            for k in range(10):
                a = math.tau * (k + 0.5 * (j % 2)) / 10
                c, s = math.cos(a), -math.sin(a)
                sub = Mesh()
                sub.quad_facing((-0.05, 0.0, 0.0), (0.05, 0.0, 0.0), (0.05, 0.1, 0.0), (-0.05, 0.1, 0.0), (0, 0, 1), "frame", 0.35)
                _place(m, sub, math.degrees(a) + 90, dx=r * c, dy=y, dz=r * s)
            m.tube((-r - 0.25, y - 0.05, 0.0), (r + 0.25, y - 0.05, 0.0), 0.012, "frame", n=3)
        return m
    return b


def ov_mastaba():
    """the stone mastaba bench before a shop (face overlay at ground)"""
    def b():
        m = Mesh()
        m.box((-1.3, 0.0, 0.004), (1.3, 0.45, 0.6), "trim", 0.9, skip=("y-", "z-"))
        m.box((-1.35, 0.45, 0.0), (1.35, 0.52, 0.65), "trim", skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ Levant (r1_levantine_courtyard)
def wall_liwan():
    """LEVANT MARK: the liwan -- a tall pointed arch opening a storey and a half to the court (2 storeys: y 0..6.4),
    ablaq voussoirs, a moulded impost"""
    def b():
        o = arch("pointed", 2.5, 5.0, 0.0, n=8)
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, 2 * ST), [o], -K, 0.0, "wall", reveal_slot="trim")
        _voussoirs(m, o, 0.02, 14, "accent", "trim", w=0.22)
        _arch_band(m, o, 0.22, -0.01, 0.018, "trim", 0.85)
        for x in (-1.3, 1.3):
            m.box((-1.495, 2.8, 0.0), (-1.3, 2.95, 0.08), "trim", skip=("z-",)) if x < 0 else m.box((1.3, 2.8, 0.0), (1.495, 2.95, 0.08), "trim", skip=("z-",))
        m.box((-HB + 0.005, 2 * ST - 0.15, 0.0), (HB - 0.005, 2 * ST - 0.005, 0.1), "trim", skip=("z-",))
        return m
    return b


def dome_stone_low():
    """LEVANT: Jerusalem's low walkable stone roof dome over a cell, on its square bed, a little vent at the top"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -HB), (HB, 0.3, HB), "wall", skip=("y-",))
        m.lathe([(1.45, 0.3), (1.35, 0.55), (1.05, 0.85), (0.55, 1.05), (0.0, 1.1)], "wall", n=12, shade=1.02)
        m.cyl(0, 0, 0.15, 1.05, 1.25, "trim", n=6)
        return m
    return b


def ov_suq_canopy():
    """LEVANT: a covered-suq vault across an artery (along X): a shallow barrel of stone between arch ribs at 4.2 m,
    lit openings in its crown"""
    def b():
        m = Mesh()
        n = 6
        zs = [-HB + BAY * i / n for i in range(n + 1)]
        ys = [4.2 + 0.9 * math.sin(math.pi * i / n) for i in range(n + 1)]
        for i in range(n):
            for x0, x1, sh in ((-HB, -0.3, 1.0), (0.3, HB, 1.0)):
                m.quad_facing((x0, ys[i], zs[i]), (x1, ys[i], zs[i]), (x1, ys[i + 1], zs[i + 1]), (x0, ys[i + 1], zs[i + 1]), (0, -1, 0), "wall", 0.75)
                m.quad_facing((x0, ys[i] + 0.15, zs[i]), (x1, ys[i] + 0.15, zs[i]), (x1, ys[i + 1] + 0.15, zs[i + 1]), (x0, ys[i + 1] + 0.15, zs[i + 1]), (0, 1, 0), "wall", sh)
            m.quad_facing((-0.3, ys[i], zs[i]), (0.3, ys[i], zs[i]), (0.3, ys[i + 1], zs[i + 1]), (-0.3, ys[i + 1], zs[i + 1]), (0, -1, 0), "emissive" if i in (2, 3) else "wall", 0.75)
            m.quad_facing((-0.3, ys[i] + 0.15, zs[i]), (0.3, ys[i] + 0.15, zs[i]), (0.3, ys[i + 1] + 0.15, zs[i + 1]), (-0.3, ys[i + 1] + 0.15, zs[i + 1]), (0, 1, 0), "emissive" if i in (2, 3) else "wall")
        for x in (-HB + 0.1, HB - 0.1):
            for i in range(n):
                m.quad_facing((x, ys[i] - 0.25, zs[i]), (x, ys[i + 1] - 0.25, zs[i + 1]), (x, ys[i + 1] + 0.15, zs[i + 1]), (x, ys[i] + 0.15, zs[i]), (1, 0, 0), "trim", 0.9)
                m.quad_facing((x - 0.001, ys[i] - 0.25, zs[i]), (x - 0.001, ys[i + 1] - 0.25, zs[i + 1]), (x - 0.001, ys[i + 1] + 0.15, zs[i + 1]), (x - 0.001, ys[i] + 0.15, zs[i]), (-1, 0, 0), "trim", 0.8)
        return m
    return b


# ------------------------------------------------------------------ Sahara (r1_saharan_kasbah)
def tower_kasbah_corner(part):
    """SAHARA MARK: the kasbah's tapering earth corner tower, a cell a part: base (battered; stack), shaft (battered,
    relief panels of chevrons and lozenges in its top), top (the pinnacled crenel crown)"""
    def b():
        m = Mesh()
        if part == "base":
            _frustum(m, 1.5, 1.42, 0.0, ST, "wall")
            for k in range(4):
                sub = Mesh()
                sub.quad_facing((-0.05, 1.4, 1.46), (0.05, 1.4, 1.46), (0.05, 2.1, 1.445), (-0.05, 2.1, 1.445), (0, 0.03, 1), "frame", 0.35)
                _place(m, sub, 90 * k)
        elif part == "shaft":
            _frustum(m, 1.42, 1.34, 0.0, ST, "wall")
            for k in range(4):
                sub = Mesh()
                z = 1.36
                for i in range(6):                                                     # chevrons
                    x = -1.05 + i * 0.42
                    _strip(sub, (x - 0.18, 2.1, z + 0.02), (x, 2.4, z + 0.02), 0.06, (0, 0, 1), "wall")
                    _strip(sub, (x, 2.4, z + 0.02), (x + 0.18, 2.1, z + 0.02), 0.06, (0, 0, 1), "wall")
                for i in range(5):                                                     # lozenges
                    cx = -0.84 + i * 0.42
                    sub.quad_facing((cx, 2.55, z + 0.02), (cx + 0.12, 2.72, z + 0.02), (cx, 2.89, z + 0.02), (cx - 0.12, 2.72, z + 0.02), (0, 0, 1), "frame", 0.45)
                sub.box((-1.3, 1.9, z - 0.02), (1.3, 1.96, z + 0.03), "wall", 0.85, skip=("z-",))
                _place(m, sub, 90 * k)
        else:
            _frustum(m, 1.34, 1.32, 0.0, 0.5, "wall", top=True)
            for x in (-1.1, 1.1):
                for z in (-1.1, 1.1):
                    _frustum(m, 0.24, 0.05, 0.5, 1.6, "wall", 0.95, cx=x, cz=z)
            for k in range(4):
                sub = Mesh()
                for i in range(4):
                    x = -0.75 + i * 0.5
                    sub.wall_cut([(x - 0.15, 0.5), (x + 0.15, 0.5), (x + 0.15, 0.75), (x + 0.07, 0.75), (x + 0.07, 0.92), (x - 0.07, 0.92), (x - 0.07, 0.75), (x - 0.15, 0.75)], [], 1.05, 1.3, "wall", 0.92)
                _place(m, sub, 90 * k)
        return m
    return b


def wall_earth_relief():
    """SAHARA: a thick earth wall bay with chevron and lozenge relief in its top third, a slit or two below"""
    def b():
        m = _wall(K)
        for i in range(7):
            x = -1.35 + i * 0.45
            _strip(m, (x - 0.2, 2.2, 0.025), (x, 2.55, 0.025), 0.07, (0, 0, 1), "wall")
            _strip(m, (x, 2.55, 0.025), (x + 0.2, 2.2, 0.025), 0.07, (0, 0, 1), "wall")
        for i in range(6):
            cx = -1.125 + i * 0.45
            m.quad_facing((cx, 2.65, 0.01), (cx + 0.14, 2.85, 0.01), (cx, 3.05, 0.01), (cx - 0.14, 2.85, 0.01), (0, 0, 1), "frame", 0.45)
        m.box((-HB, 2.05, 0.0), (HB, 2.12, 0.04), "wall", 0.85, skip=("z-", "x-", "x+"))
        for x in (-0.7, 0.7):
            m.quad_facing((x - 0.05, 1.2, 0.004), (x + 0.05, 1.2, 0.004), (x + 0.05, 1.8, 0.004), (x - 0.05, 1.8, 0.004), (0, 0, 1), "frame", 0.35)
        return m
    return b


def ghorfa_cell():
    """SAHARA: the vaulted ghorfa granary cell, stackable 3-6 high round a court: an earth box under a barrel vault
    (along Z), a small painted door to +Z, palm beam ends"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -HB), (HB, 2.0, HB - 0.29), "wall", skip=("y-", "y+", "z+"))
        n = 6
        for k in range(n):
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            p0, p1 = (HB * math.cos(a0), 2.0 + 1.0 * math.sin(a0)), (HB * math.cos(a1), 2.0 + 1.0 * math.sin(a1))
            m.quad_facing((p0[0], p0[1], -HB), (p1[0], p1[1], -HB), (p1[0], p1[1], HB - 0.29), (p0[0], p0[1], HB - 0.29), (math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0), "wall", 0.95)
        front = [(-HB, 0.0), (HB, 0.0), (HB, 2.0)] + [(HB * math.cos(math.pi * k / n), 2.0 + math.sin(math.pi * k / n)) for k in range(1, n)] + [(-HB, 2.0)]
        m.wall_cut(front, [_rect(-0.35, 0.5, 0.35, 1.6)], HB - 0.3, HB, "wall", reveal_slot="wall")
        m.box((-0.345, 0.505, HB - 0.25), (0.345, 1.595, HB - 0.2), "accent")
        for x in (-1.1, -0.4, 0.4, 1.1):
            m.box((x - 0.05, 2.0, HB), (x + 0.05, 2.1, HB + 0.25), "frame", skip=("z-",))      # beam ends
        return m
    return b


def wall_slit():
    """SAHARA: a defensive slit in a thick earth wall, its reveal splayed inward"""
    def b():
        m = _wall(K, [_rect(-0.07, 1.3, 0.07, 2.3)])
        m.pane(-0.07, 1.3, 0.07, 2.3, -0.5)
        return m
    return b


def edge_parapet_pinnacle():
    """SAHARA: the stepped crenel parapet with pinnacle corners"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0)]
        for x in (1.0, 0.33, -0.33, -1.0):
            p += [(x + 0.18, 0.55), (x + 0.18, 0.8), (x + 0.08, 0.8), (x + 0.08, 0.95), (x - 0.08, 0.95), (x - 0.08, 0.8), (x - 0.18, 0.8), (x - 0.18, 0.55)]
        _flat_prism(m, p, -0.45, 0.0, "wall", open_edges=(0,))
        _frustum(m, 0.2, 0.04, 0.0, 1.4, "wall", 0.95, cx=HB - 0.2, cz=-0.22)
        return m
    return b


# ------------------------------------------------------------------ Newar requests
def pagoda_temple_tiers():
    """NEWAR MARK: the pagoda temple whole -- a stepped brick plinth of three stages with a stair up the front, then the
    three-tier roof_pagoda (one cell; the plinth 2.4 m)"""
    def b():
        m = Mesh()
        for k, (a, y0, y1) in enumerate(((1.5, 0.0, 0.8), (1.38, 0.8, 1.6), (1.26, 1.6, 2.4))):
            m.box((-a, y0, -a), (a, y1, a), "wall", 0.9 + 0.05 * k, skip=("y-",) + (() if k == 2 else ()))
            m.box((-a - 0.02, y1 - 0.09, -a - 0.02), (a + 0.02, y1 - 0.015, a + 0.02), "trim", 0.85)
        for j in range(8):                                                             # the front stair
            y = (j + 1) * 0.3
            m.box((-0.45 + 0.002 * j, y - 0.31, 1.2), (0.45 - 0.002 * j, y, 2.3 - j * 0.1), "trim", 0.9, skip=("y-",))
        for x in (-0.6, 0.6):                                                          # guardian lions
            m.box((x - 0.12, 0.0, 2.2), (x + 0.12, 0.5, 2.45), "trim", 0.8, skip=("y-",))
        top = roof_pagoda()()
        m.add(top, lambda p: (p[0] * 0.95, p[1] + 2.4, p[2] * 0.95))
        return m
    return b


def hiti_sunken():
    """NEWAR: the hiti -- a sunken stone court below the deck (1.8 m down in four steps from +Z, -X and +X), its back
    wall (-Z) with three gilt makara spouts pouring into a pool"""
    def b():
        m = Mesh()
        from shapely.geometry import Polygon
        import shapely
        aa = [HB, 1.2, 0.9, 0.6, 0.3]
        for j in range(4):                                                             # each level: a U, its top
            ao, ai, y = aa[j], aa[j + 1], -0.45 * j
            g = Polygon([(-ao, -HB), (ao, -HB), (ao, ao), (-ao, ao)]).difference(Polygon([(-ai, -HB - 1), (ai, -HB - 1), (ai, ai), (-ai, ai)]))
            for q in getattr(g, "geoms", [g]):
                for t in shapely.constrained_delaunay_triangles(q).geoms:
                    c = list(t.exterior.coords)[:3]
                    m.tri_facing(*[(p[0], y, p[1]) for p in c], (0, 1, 0), "ground", 0.95 - 0.04 * j)
            yb = y - 0.45                                                              # its risers (inner sides)
            m.quad_facing((-ai, yb, ai), (ai, yb, ai), (ai, y, ai), (-ai, y, ai), (0, 0, -1), "ground", 0.8)
            m.quad_facing((ai, yb, -HB), (ai, yb, ai), (ai, y, ai), (ai, y, -HB), (-1, 0, 0), "ground", 0.82)
            m.quad_facing((-ai, yb, -HB), (-ai, yb, ai), (-ai, y, ai), (-ai, y, -HB), (1, 0, 0), "ground", 0.82)
        m.quad_facing((-0.3, -1.8, -HB), (0.3, -1.8, -HB), (0.3, -1.8, 0.3), (-0.3, -1.8, 0.3), (0, 1, 0), "water")
        m.quad_facing((-HB, -1.8, -HB + 0.005), (HB, -1.8, -HB + 0.005), (HB, 0.0, -HB + 0.005), (-HB, 0.0, -HB + 0.005), (0, 0, 1), "trim", 0.85)
        for x in (-0.2, 0.0, 0.2):                                                     # makara spouts
            m.box((x - 0.06, -1.0, -HB + 0.006), (x + 0.06, -0.88, -HB + 0.3), "accent", skip=("z-",))
            m.tube((x, -1.0, -HB + 0.28), (x, -1.78, -HB + 0.33), 0.015, "water", n=3)
        return m
    return b


def stupa():
    """NEWAR MARK: a whitewashed stupa (cell decor): square plinth, the dome, the harmika painted with Buddha eyes,
    thirteen gilt rings, a parasol"""
    def b():
        m = Mesh()
        m.box((-1.4, 0.0, -1.4), (1.4, 0.35, 1.4), "trim", 0.85, skip=("y-",))
        m.lathe([(1.2, 0.35), (1.18, 0.6), (1.0, 1.1), (0.7, 1.45), (0.35, 1.6), (0.0, 1.62)], "trim", n=12, shade=1.05)
        m.box((-0.35, 1.55, -0.35), (0.35, 2.05, 0.35), "trim", skip=("y-",))
        for k in range(4):
            sub = Mesh()
            for x in (-0.15, 0.15):
                sub.quad_facing((x - 0.09, 1.78, 0.355), (x + 0.09, 1.78, 0.355), (x + 0.07, 1.86, 0.355), (x - 0.07, 1.86, 0.355), (0, 0, 1), "frame")
                sub.quad_facing((x - 0.04, 1.8, 0.358), (x + 0.04, 1.8, 0.358), (x + 0.03, 1.84, 0.358), (x - 0.03, 1.84, 0.358), (0, 0, 1), "accent")
            sub.quad_facing((-0.03, 1.62, 0.357), (0.03, 1.62, 0.357), (0.03, 1.74, 0.357), (-0.03, 1.74, 0.357), (0, 0, 1), "frame")
            _place(m, sub, 90 * k)
        m.box((-0.42, 2.05, -0.42), (0.42, 2.12, 0.42), "trim", 0.9)
        m.lathe([(0.32, 2.12), (0.06, 3.3)], "accent", n=8)
        for k in range(13):
            y = 2.15 + k * 0.088
            r = 0.33 - 0.26 * (y - 2.12) / 1.18 + 0.02
            m.cyl(0, 0, r, y, y + 0.03, "accent", n=8, caps=False, shade=0.8)
        m.lathe([(0.0, 3.3), (0.35, 3.33), (0.0, 3.5)], "accent", n=8)
        m.lathe([(0.0, 3.45), (0.06, 3.55), (0.0, 3.75)], "accent", n=6)
        return m
    return b


def roof_tile_hip_struts():
    """NEWAR: a clay-tile roof over a row house on carved struts -- a 30-degree gable segment (tiles along Z) with its
    eaves out 0.9 m on diagonal struts both sides"""
    def b():
        m, h = _gable_seg(30, eave=0.9, ribs=8)
        for s in (-1, 1):
            for z in (-1.0, 0.0, 1.0):
                m.tube((s * HB, -1.2, z), (s * (HB + 0.6), -0.3, z), 0.05, "frame", n=4)
                m.box((s * HB - 0.07, -1.35, z - 0.07), (s * HB + 0.07, -1.15, z + 0.07), "frame", 0.75)
        return m
    return b


def pave_herringbone():
    """NEWAR: herringbone brick paving (ground; the wall slot = Newar brick): a joint sheet and alternating brick
    strips at 45 degrees"""
    def b():
        m = Mesh()
        m.quad_facing((-HB, -0.01, -HB), (HB, -0.01, -HB), (HB, -0.01, HB), (-HB, -0.01, HB), (0, 1, 0), "wall", 0.55)
        for i in range(10):
            for j in range(5):
                x = -HB + 0.15 + i * 0.3
                z = -HB + 0.3 + j * 0.6
                if i % 2 == 0:
                    pts = ((x - 0.13, z - 0.13), (x + 0.13, z + 0.13))
                else:
                    pts = ((x - 0.13, z + 0.13), (x + 0.13, z - 0.13))
                (ax, az), (bx, bz) = pts
                _strip(m, (ax, 0.0, az), (bx, 0.0, bz), 0.1, (0, 1, 0), "wall")
        return m
    return b


def ov_prayer_flags():
    """NEWAR / TIBET: prayer flag strings across a lane (along X), sagging, five colours"""
    def b():
        m = Mesh()
        cols = ["accent2", "trim", "fabric", "tile", "accent"]
        for row, (y0, z) in enumerate(((4.2, -0.6), (3.9, 0.6))):
            pts = [(-HB + BAY * i / 10, y0 - 0.5 * math.sin(math.pi * i / 10), z) for i in range(11)]
            for a, c in zip(pts, pts[1:]):
                m.tube(a, c, 0.006, "frame", n=3)
            for i in range(10):
                x0, x1 = pts[i][0] + 0.03, pts[i + 1][0] - 0.03
                ya, yb = pts[i][1], pts[i + 1][1]
                sl = cols[(i + row) % 5]
                m.quad_facing((x0, ya - 0.02, z), (x1, yb - 0.02, z), (x1, yb - 0.24, z), (x0, ya - 0.24, z), (0, 0, 1), sl)
                m.quad_facing((x0, ya - 0.02, z - 0.003), (x1, yb - 0.02, z - 0.003), (x1, yb - 0.24, z - 0.003), (x0, ya - 0.24, z - 0.003), (0, 0, -1), sl, 0.85)
        return m
    return b


# ------------------------------------------------------------------ Hejaz requests
def edge_mangour():
    """HEJAZ: the mangour -- the 1.8 m painted timber lattice screen walling a Jeddah roof terrace (edge)"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -0.3), (HB, 0.3, 0.0), "wall", skip=("y-", "x-", "x+"))
        for k in range(3):
            x0 = -HB + k * 1.0
            _lattice(m, x0 + 0.1, 0.3, x0 + 0.9, 1.8, -0.18, -0.12, 5, 10, slot="screen")
        for xa in (-HB, -0.54, 0.46, HB - 0.08):                                      # posts between the panels
            m.box((xa, 0.29, -0.2), (xa + 0.08, 1.95, -0.1), "accent", skip=("y-",))
        m.box((-HB, 1.8, -0.22), (HB, 1.88, -0.08), "accent", 0.9, skip=("x-", "x+"))
        return m
    return b


def roshan_crest():
    """HEJAZ: the carved crest crowning a stack of roshans (face overlay over the top roshan; y 0 = its top at 3.2)"""
    def b():
        m = Mesh()
        m.box((-1.15, 0.0, 0.0), (1.15, 0.18, 1.05), "accent", skip=("z-",))
        _crest(m, -1.15, 1.15, 0.18, 0.3, 1.05, 9, "accent")
        for x in (-1.1, 0.0, 1.1):
            m.lathe([(0.07, 0.18), (0.09, 0.3), (0.0, 0.55)], "accent", n=5, cx=x, cz=0.95)
        _beads(m, -1.15, 1.15, 0.04, 0.14, 1.05, 1.08, 14, "accent", 0.8)
        return m
    return b


def wall_coral_bands():
    """HEJAZ: a coral-stone bay with its timber tie-beam bands every metre and a small shuttered window"""
    def b():
        m = _wall(K, [_rect(-0.35, 1.25, 0.35, 1.95)])
        m.box((-0.345, 1.255, -0.32), (0.345, 1.945, -0.28), "accent", 0.85)
        _ring(m, -0.35, 1.25, 0.35, 1.95, 0.06, 0.0, 0.03, "trim")
        for y in (0.95, 2.05, 3.05):
            m.box((-HB, y, 0.0), (HB, y + 0.12, 0.035), "frame", 0.85, skip=("z-", "x-", "x+"))
        for i in range(6):                                                             # coral blocks between
            for j, (ya, yb) in enumerate(((0.1, 0.9), (2.2, 3.0))):
                x = -HB + 0.05 + i * 0.5 + 0.12 * (j % 2)
                m.quad_facing((x, ya, 0.004), (x + 0.36, ya, 0.004), (x + 0.36, yb, 0.004), (x, yb, 0.004), (0, 0, 1), "wall", 0.9 + 0.05 * ((i + j) % 2))
        return m
    return b


# ------------------------------------------------------------------ register
MED = ["maghrebi_medina"]
PIECES["wall_door_portal_k"] = _w("wall", wall_door_portal(), MED, notes="MEDINA MARK: horseshoe door, voussoirs, alfiz, zellige, canopy")
PIECES["wall_arch_horseshoe_t"] = _w("wall", wall_arch_medina(T), MED, notes="MEDINA MARK: horseshoe passage, voussoirs, alfiz")
PIECES["wall_arch_horseshoe_k"] = _w("wall", wall_arch_medina(K), MED, notes="MEDINA MARK: horseshoe passage, voussoirs, alfiz")
PIECES["minaret_shaft"] = _w("cell", minaret_shaft_medina(), MED, kind="tower", lod1="keep", notes="MEDINA MARK: minaret shaft, lobed arch, sebka net, tile band")
PIECES["wall_kowloon_stack_t"] = _w("wall", wall_kowloon_stack(), ["kowloon_walled", "hk_neon_canyon"], notes="KOWLOON MARK: dense hero bay (cage, AC, laundry, pipes, sign)")
SI = ["siam_khlong"]
PIECES["roof_thai_gable"] = _w("cell", roof_thai_gable(), SI, lod1="keep", kind="roof", notes="SIAM MARK: layered Thai gable, naga boards, chofa (ridge along Z)")
PIECES["wall_thai_teak_t"] = _w("wall", wall_thai_teak(), SI, notes="SIAM: teak fa pakon panel wall, shutters open")
CA = ["cairene_mamluk"]
PIECES["wall_mashrabiya_box_k"] = _w("wall", wall_mashrabiya_box(), CA, lod1="keep", notes="CAIRO MARK: two-tier bead mashrabiya oriel")
PIECES["wall_ablaq_portal_k"] = _w("wall", wall_ablaq_portal(), CA + ["levantine_courtyard"], notes="CAIRO/LEVANT MARK: ablaq portal, muqarnas hood")
for p in ("base", "shaft", "top"):
    PIECES[f"minaret_mamluk_{p}"] = _w("cell", minaret_mamluk(p), CA, lod1="keep", kind="tower", notes=f"CAIRO MARK: Mamluk minaret {p} (base xN, shaft, top)")
PIECES["dome_ribbed"] = _w("cell", dome_ribbed(), CA, lod1="keep", kind="crown", notes="CAIRO MARK: carved ribbed stone dome on a drum")
PIECES["malqaf_scoop"] = _w("cell", malqaf_scoop(), CA + ["persian_desert"], lod1="keep", kind="overlay", notes="roof wind scoop, mouth to +Z")
PIECES["pigeon_cote"] = _w("cell", pigeon_cote(), CA, lod1="keep", kind="overlay", notes="mud pigeon tower on a roof")
PIECES["ov_mastaba"] = _w("wall", ov_mastaba(), CA + ["levantine_courtyard"], lod1="drop", kind="overlay", notes="stone bench before a shop")
LV = ["levantine_courtyard"]
PIECES["wall_liwan_k"] = _w("wall", wall_liwan(), LV, lod1="keep", span=(1, 1), notes="LEVANT MARK: liwan arch, TWO storeys tall (y 0..6.4)")
PIECES["dome_stone_low"] = _w("cell", dome_stone_low(), LV, lod1="keep", kind="crown", notes="low walkable stone roof dome")
PIECES["ov_suq_canopy"] = _w("cell", ov_suq_canopy(), LV + CA, lod1="keep", collide=False, kind="overlay", notes="covered-suq vault along X at 4.2 m, lit crown")
SA = ["saharan_kasbah"]
for p in ("base", "shaft", "top"):
    PIECES[f"tower_kasbah_corner_{p}"] = _w("cell", tower_kasbah_corner(p), SA, lod1="keep", kind="tower", notes=f"SAHARA MARK: corner tower {p} (base xN, shaft, top)")
PIECES["wall_earth_relief_k"] = _w("wall", wall_earth_relief(), SA, notes="SAHARA: chevron/lozenge relief in the top third")
PIECES["ghorfa_cell"] = _w("cell", ghorfa_cell(), SA, lod1="keep", notes="SAHARA MARK: vaulted granary cell, door to +Z, stackable")
PIECES["wall_slit_k"] = _w("wall", wall_slit(), SA + ["kulla_stone", "omani_oasis"], notes="defensive slit")
PIECES["edge_parapet_pinnacle_k"] = _w("edge", edge_parapet_pinnacle(), SA, lod1="keep", notes="stepped crenels, pinnacle at +X end (mirror by turning)")
NW = ["newar"]
PIECES["pagoda_temple_tiers"] = _w("cell", pagoda_temple_tiers(), NW, lod1="keep", kind="tower", notes="NEWAR MARK: stepped plinth + three-tier pagoda")
PIECES["hiti_sunken"] = _w("cell", hiti_sunken(), NW, lod1="box", kind="ground", notes="NEWAR: sunken spout court 1.8 m down, steps from +Z")
PIECES["stupa"] = _w("cell", stupa(), NW + ["tibetan_lhasa"], lod1="keep", notes="NEWAR MARK: whitewashed stupa with eyes")
PIECES["roof_tile_hip_struts"] = _w("cell", roof_tile_hip_struts(), NW, lod1="keep", kind="roof", notes="30-deg tile segment (ridge along Z) on carved struts")
PIECES["wall_brick_herringbone"] = _w("cell", pave_herringbone(), NW, kind="ground", notes="herringbone brick paving (wall slot)")
PIECES["ov_prayer_flags"] = _w("cell", ov_prayer_flags(), NW + ["tibetan_lhasa"], lod1="drop", collide=False, kind="overlay", notes="prayer flags across a lane (along X)")
HJ = ["hejazi_roshan"]
PIECES["edge_mangour_k"] = _w("edge", edge_mangour(), HJ, lod1="keep", notes="HEJAZ MARK: 1.8 m lattice roof screen")
PIECES["roshan_crest"] = _w("wall", roshan_crest(), HJ + CA, lod1="keep", collide=False, kind="overlay", notes="crest over the top roshan (place at the stack's top)")
PIECES["wall_coral_bands_k"] = _w("wall", wall_coral_bands(), HJ, notes="coral stone, timber tie-beam bands")

for civ, acc in (("cairene_mamluk", ("#4a4440", "#c9a23a")), ("levantine_courtyard", ("#4a4440", "#c9a23a")), ("saharan_kasbah", ("#3f6f8a", "#c9a23a")),
                 ("siam_khlong", ("#c9a23a", "#b0322a")), ("maghrebi_medina", ("#b0723a", "#3f6f6a"))):
    for v in PALETTES.get(civ, []):
        v["accent"], v["accent2"] = acc
for v in PALETTES.get("newar", []):
    v["tile"], v["fabric"] = "#2a8a4a", "#b0322a"                              # (prayer flag colours)
