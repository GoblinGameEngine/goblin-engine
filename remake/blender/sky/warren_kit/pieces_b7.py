"""pieces_b7.py -- warren kit batch 4d: the generator's requests for ganga_ghat, karachi, mughal_walled, omani_oasis,
persian_desert, rajput_sandstone and silk_road.
"""
import math

from geom import Mesh, _dedupe, arch
from pieces import BAY, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall
from pieces_b4 import _flat_prism
from pieces_b5 import _door_leaf, _fix_mirror, _frustum, _u_frame, edge_parapet_urns
from pieces_b6 import _arch_band, _octagon, _ribbed_dome, _stud_grid, _voussoirs
from pieces_marks import _beads, _corbel, _crest, _diag, _off, _place, _ring


# ------------------------------------------------------------------ shared Indic pieces
def _chhajja(m, x0, x1, y, d, slot="trim", brackets=3):
    """a deep thin stone eave sloping out d from the face at y, on brackets"""
    m.quad_facing((x0, y, 0.0), (x1, y, 0.0), (x1, y - 0.18, d), (x0, y - 0.18, d), (0, 1, 0.25), slot)
    m.quad_facing((x0, y - 0.06, 0.0), (x1, y - 0.06, 0.0), (x1, y - 0.22, d), (x0, y - 0.22, d), (0, -1, -0.3), slot, 0.6)
    m.quad_facing((x0, y - 0.22, d), (x1, y - 0.22, d), (x1, y - 0.18, d), (x0, y - 0.18, d), (0, 0, 1), slot, 0.85)
    for k in range(brackets):
        x = x0 + (x1 - x0) * (k + 0.5) / brackets
        _corbel(m, x, y - 0.06, d * 0.7, 0.45, 0.08, slot, 0.8)


def _bulb(m, r, y0, slot="trim", n=10, finial="accent2", h=None):
    """a bulbous (onion) dome: swelling past its base, drawn to a point, a lotus band and finial"""
    h = h or r * 1.6
    m.lathe([(r, y0), (r * 1.15, y0 + h * 0.25), (r * 1.08, y0 + h * 0.5), (r * 0.7, y0 + h * 0.75), (r * 0.25, y0 + h * 0.92), (0.0, y0 + h)], slot, n=n)
    m.lathe([(0.0, y0 + h - 0.05), (0.08, y0 + h + 0.05), (0.03, y0 + h + 0.25), (0.07, y0 + h + 0.32), (0.0, y0 + h + 0.55)], finial, n=6)


def chhatri():
    """the chhatri: a domed pavilion on four columns standing on a roof corner (crown): a plinth, columns, the chhajja
    round all four sides, a drum and a bulbous dome with its finial"""
    def b():
        m = Mesh()
        a = 1.1
        m.box((-a - 0.1, 0.0, -a - 0.1), (a + 0.1, 0.3, a + 0.1), "trim", 0.9, skip=("y-",))
        for x in (-a + 0.12, a - 0.12):
            for z in (-a + 0.12, a - 0.12):
                m.cyl(x, z, 0.09, 0.3, 2.0, "trim", n=6, caps=False)
                m.box((x - 0.14, 1.85, z - 0.14), (x + 0.14, 2.0, z + 0.14), "trim", 0.9)
        m.box((-a, 2.0, -a), (a, 2.15, a), "trim", skip=())
        for k in range(4):
            sub = Mesh()
            sub.quad_facing((-a - 0.35, 2.15, a + 0.35), (a + 0.35, 2.15, a + 0.35), (a, 2.25, a), (-a, 2.25, a), (0, 1, 0.5), "trim")
            sub.quad_facing((-a - 0.35, 2.12, a + 0.35), (a + 0.35, 2.12, a + 0.35), (a - 0.01, 2.01, a - 0.01), (-a + 0.01, 2.01, a - 0.01), (0, -1, 0.3), "trim", 0.6)
            from geom import rot_y
            m.add(sub, rot_y(90 * k))
        m.cyl(0, 0, 0.84, 2.25, 2.52, "trim", n=10, caps=False)
        _bulb(m, 0.85, 2.5, "trim", n=10)
        return m
    return b


# ------------------------------------------------------------------ Ganga ghat (r1_ganga_ghat)
def ghat_steps_wide():
    """GANGA MARK: broad stone ghat steps down into the water: 3 m wide over two cells along +Z (span [1, 2]), from the
    deck at z -1.5 down 3.2 m to the water side at +4.5, a landing halfway"""
    def b():
        m = Mesh()
        n = 8
        for k in range(n):                                           # first flight
            z0 = -HB + k * 0.3
            y = -0.2 * k
            m.box((-HB, y - 0.5, z0), (HB, y, z0 + 0.32), "ground", 0.9 + 0.1 * (k % 2), skip=("y-", "x-", "x+"))
        m.box((-HB, -1.6 - 0.5, 0.9), (HB, -1.6, 2.1), "ground", 0.95, skip=("y-", "x-", "x+"))      # landing
        for k in range(n):                                           # second flight
            z0 = 2.1 + k * 0.3
            y = -1.6 - 0.2 * (k + 1)
            m.box((-HB, y - 0.5, z0), (HB, y, z0 + 0.32), "ground", 0.9 + 0.1 * (k % 2), skip=("y-", "x-", "x+"))
        for x in (-1.2, 1.2):                                        # little shrines on the landing
            m.box((x - 0.2, -1.6, 1.3), (x + 0.2, -1.0, 1.7), "trim", skip=("y-",))
            m.lathe([(0.22, -1.0), (0.0, -0.6)], "accent", n=4, cx=x, cz=1.5)
        return m
    return b


def shikhara_spire(part):
    """GANGA MARK: the nagara temple spire, a cell a part: base (the sanctum, offset projections on each face, a doorway
    to +Z), shaft (the curving tower, a storey of horizontal bhumi bands; stack 2-4), top (the ribbed amalaka disc,
    the kalasha pot, a saffron flag)"""
    def b():
        m = Mesh()
        if part == "base":
            m.box((-1.3, 0.0, -1.3), (1.3, ST, 1.3), "wall", skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                sub.box((-0.5, 0.0, 1.3), (0.5, ST, 1.42), "wall", 0.95, skip=("z-", "y-"))
                sub.box((-1.3, ST - 0.3, 1.3), (1.3, ST - 0.15, 1.38), "trim", skip=("z-",))
                if k == 2:
                    sub.quad_facing((-0.3, 0.0, 1.425), (0.3, 0.0, 1.425), (0.3, 1.9, 1.425), (-0.3, 1.9, 1.425), (0, 0, 1), "frame", 0.35)
                    sub.wall_cut(_rect(-0.45, 0.0, 0.45, 2.05), [_rect(-0.305, -1.0, 0.305, 1.905)], 1.42, 1.46, "accent")
                m.add(sub, _rot(k))
            m.box((-1.45, ST - 0.02, -1.45), (1.45, ST + 0.1, 1.45), "trim", 0.9)
        elif part == "shaft":
            for j in range(4):                                       # four bhumi bands, curving in
                y0, y1 = j * 0.8, (j + 1) * 0.8
                a0 = 1.3 - 0.08 * j - 0.01 * j * j
                a1 = 1.3 - 0.08 * (j + 1) - 0.01 * (j + 1) ** 2
                _frustum(m, a0, a1, y0, y1 - 0.12, "wall", 0.95)
                _frustum(m, a1 + 0.05, a1 + 0.05, y1 - 0.12, y1, "trim", 0.85)
                for k in range(4):
                    sub = Mesh()
                    sub.quad_facing((-0.35, y0 + 0.1, a0 + 0.06), (0.35, y0 + 0.1, a0 + 0.06), (0.32, y1 - 0.15, a1 + 0.06), (-0.32, y1 - 0.15, a1 + 0.06), (0, 0.1, 1), "wall", 1.05)
                    m.add(sub, _rot(k))
        else:
            _frustum(m, 0.95, 0.6, 0.0, 0.8, "wall", 0.95, top=True)
            prof = [(0.35, 0.8), (0.95, 0.95), (1.0, 1.05), (0.9, 1.15), (0.3, 1.25)]
            _ribbed_lathe(m, prof, "trim", 20)
            m.lathe([(0.3, 1.25), (0.35, 1.4), (0.2, 1.6), (0.08, 1.65), (0.12, 1.75), (0.0, 1.95)], "accent2", n=8)
            m.cyl(0.0, 0.0, 0.02, 1.9, 2.8, "frame", n=3)
            m.quad_facing((0.0, 2.5, 0.0), (0.6, 2.62, 0.0), (0.0, 2.8, 0.0), (0.0, 2.8, 0.0), (0, 0, 1), "accent")
            m.tri_facing((0.0, 2.5, -0.003), (0.6, 2.62, -0.003), (0.0, 2.8, -0.003), (0, 0, -1), "accent", 0.85)
        return m
    return b


def _ribbed_lathe(m, prof, slot, n):
    """a lathe whose segments alternate shade (the amalaka's ribs)"""
    for i in range(len(prof) - 1):
        (r0, ya), (r1, yb) = prof[i], prof[i + 1]
        for k in range(n):
            a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
            p0, p1 = (r0 * math.cos(a0), ya, -r0 * math.sin(a0)), (r0 * math.cos(a1), ya, -r0 * math.sin(a1))
            q0, q1 = (r1 * math.cos(a0), yb, -r1 * math.sin(a0)), (r1 * math.cos(a1), yb, -r1 * math.sin(a1))
            dr = r1 - r0
            out = (math.cos((a0 + a1) / 2) * (yb - ya), -dr, -math.sin((a0 + a1) / 2) * (yb - ya))
            m.quad_facing(p0, p1, q1, q0, out, slot, 1.0 if k % 2 else 0.8)


def _rot(k):
    from geom import rot_y
    return rot_y(90 * k)


def ghat_umbrella():
    """GANGA: the cane umbrella over a priest's wooden platform on the steps (cell decor)"""
    def b():
        m = Mesh()
        m.box((-0.9, 0.0, -0.9), (0.9, 0.45, 0.9), "frame", 0.85, skip=("y-",))
        m.quad_facing((-0.8, 0.455, -0.8), (0.8, 0.455, -0.8), (0.8, 0.455, 0.8), (-0.8, 0.455, 0.8), (0, 1, 0), "fabric")
        m.cyl(0.4, 0.4, 0.035, 0.45, 2.6, "frame", n=4)
        m.lathe([(0.0, 2.35), (1.5, 2.15), (1.55, 2.2), (0.08, 2.75), (0.0, 2.8)], "screen", n=12)
        for k in range(12):
            a = math.tau * k / 12
            _strip(m, (0.1 * math.cos(a), 2.74, -0.1 * math.sin(a)), (1.5 * math.cos(a), 2.21, -1.5 * math.sin(a)), 0.04, (math.cos(a), 2.5, -math.sin(a)), "frame")
        return m
    return b


def ov_marigold_garland():
    """GANGA: marigold garlands swagged over a door and down its jambs (face overlay)"""
    def b():
        m = Mesh()
        for row, (y, sag, slot) in enumerate(((2.55, 0.35, "accent2"), (2.45, 0.25, "accent"))):
            pts = [(-0.9 + 1.8 * i / 6, y - sag * math.sin(math.pi * i / 6), 0.12 + 0.03 * row) for i in range(7)]
            for a, c in zip(pts, pts[1:]):
                m.tube(a, c, 0.045, slot, n=4)
        for x in (-0.9, 0.9):
            m.tube((x, 2.55, 0.12), (x, 1.2, 0.12), 0.045, "accent2", n=4)
            m.lathe([(0.0, 1.05), (0.06, 1.12), (0.0, 1.2)], "accent", n=4, cx=x, cz=0.12)
        return m
    return b


def band_flood():
    """GANGA: the dark flood-mark band on the lower storey: a stain to an uneven line at about 1.6 m (face overlay)"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 1.5)] + [(HB - BAY * i / 8, 1.6 + 0.12 * math.sin(i * 2.1)) for i in range(1, 8)] + [(-HB, 1.55)]
        m.wall_cut(p, [], 0.0, 0.006, "wall", 0.55)
        return m
    return b


# ------------------------------------------------------------------ Karachi (r1_karachi)
def ov_tank_drum():
    """KARACHI: a cluster of plastic water-tank drums on a roof, black and blue (roof overlay)"""
    def b():
        m = Mesh()
        for (x, z, r, h, slot) in ((-0.6, -0.4, 0.5, 1.1, "frame"), (0.55, -0.3, 0.45, 1.0, "accent"), (0.0, 0.6, 0.4, 0.9, "frame")):
            m.lathe([(r * 0.95, 0.0), (r, 0.15), (r, h - 0.15), (r * 0.9, h), (r * 0.3, h + 0.05), (0.0, h + 0.05)], slot, n=8, cx=x, cz=z)
            m.cyl(x, z, r * 0.25, h + 0.05, h + 0.13, slot, n=6, shade=0.8)
        return m
    return b


def wall_jharokha():
    """KARACHI MARK: the Gizri-stone jharokha -- a bay 0.6 m out on three carved brackets, three arched windows with
    carved spandrels, a chhajja, a parapet of little domes"""
    def b():
        m = _wall(K, [_rect(-0.7, 0.4, 0.7, 2.4)], reveal="trim")
        d, x0, x1 = 0.6, -0.95, 0.95
        for x in (-0.75, 0.0, 0.75):
            _corbel(m, x, 0.35, d, 0.75, 0.12, "trim", 0.85)
        m.box((x0, 0.25, 0.0), (x1, 0.4, d + 0.05), "trim", skip=("z-",))
        front = Mesh()
        ops = [arch("round", 0.42, 1.25, 0.75, n=6)]
        ops = [[(x + dx, y) for x, y in ops[0]] for dx in (-0.6, 0.0, 0.6)]
        front.wall_cut(_rect(x0, 0.4, x1, 2.3), ops, d - 0.12, d, "trim", reveal_slot="trim")
        for o in ops:
            front.pane(min(p[0] for p in o), 0.75, max(p[0] for p in o), 2.0, d - 0.1)
            _arch_band(front, o, 0.06, d - 0.01, d + 0.03, "trim", 0.85)
        _beads(front, x0, x1, 0.5, 0.65, d, d + 0.03, 10, "trim", 0.85)
        m.add(front)
        for side in (-1, 1):
            m.box((x0 if side < 0 else x1 - 0.06, 0.4, 0.0), (x0 + 0.06 if side < 0 else x1, 2.3, d - 0.12), "trim", 0.9, skip=("z-",))
        _chhajja(m, x0 - 0.15, x1 + 0.15, 2.5, d + 0.35, brackets=0)
        for x in (-0.7, 0.0, 0.7):
            m.lathe([(0.16, 2.32), (0.18, 2.45), (0.1, 2.6), (0.0, 2.72)], "trim", n=6, cx=x, cz=d * 0.6)
        return m
    return b


def wall_veranda_gothic():
    """KARACHI: a colonial Indo-Gothic veranda storey -- two pointed arches on slender columns at the front (1.8 m out),
    a pierced balustrade, louvred doors behind"""
    def b():
        m = _wall(T, [_rect(-1.1, 0.0, -0.3, 2.5), _rect(0.3, 0.0, 1.1, 2.5)], reveal="frame")
        for x0 in (-1.1, 0.3):
            m.box((x0 + 0.005, 0.0, -0.16), (x0 + 0.795, 2.495, -0.12), "accent", 0.85)
            for j in range(10):
                _strip(m, (x0 + 0.06, 0.15 + j * 0.22, -0.115), (x0 + 0.74, 0.15 + j * 0.22, -0.115), 0.06, (0, 0.4, 1), "accent")
        d = 1.8
        front = Mesh()
        ops = [[(x + dx, y) for x, y in arch("pointed", 1.2, 2.7, 0.0, n=6)] for dx in (-0.72, 0.72)]
        front.wall_cut(_rect(-HB, 0.0, HB, ST - 0.005), ops, d - 0.3, d, "trim", reveal_slot="trim")
        for o in ops:
            _arch_band(front, o, 0.08, d - 0.01, d + 0.03, "trim", 0.85)
        m.add(front)
        m.box((-HB, ST - 0.2, 0.004), (HB, ST - 0.005, d - 0.3), "trim", 0.75, skip=("z-", "x-", "x+"))
        for x0 in (-1.32, 0.12):
            m.box((x0, 0.0, d - 0.25), (x0 + 1.2, 0.9, d - 0.15), "trim", 0.95, skip=("y-",))
            for k in range(5):
                x = x0 + 0.12 + k * 0.22
                m.quad_facing((x, 0.15, d - 0.145), (x + 0.12, 0.15, d - 0.145), (x + 0.12, 0.75, d - 0.145), (x, 0.75, d - 0.145), (0, 0, 1), "frame", 0.45)
        return m
    return b


def ov_truck_art_panel():
    """KARACHI MARK: a truck-art painted shutter panel -- flowers, birds and borders in flat colour, a chrome-and-light
    frame of little lamps (face overlay, emissive)"""
    def b():
        m = Mesh()
        x0, y0, x1, y1, z = -1.25, 0.2, 1.25, 2.5, 0.06
        m.box((x0, y0, 0.0), (x1, y1, z), "accent", skip=("z-",))
        cols = ["accent2", "fabric", "tile", "trim"]
        for i in range(4):                                               # petals round two flowers
            for cx, cy in ((-0.6, 1.35), (0.6, 1.35)):
                a = math.tau * i / 4 + math.pi / 4
                pts = [(cx, cy), (cx + 0.45 * math.cos(a - 0.35), cy + 0.45 * math.sin(a - 0.35)), (cx + 0.45 * math.cos(a + 0.35), cy + 0.45 * math.sin(a + 0.35))]
                m.tri_facing(*[(p[0], p[1], z + 0.004) for p in pts], (0, 0, 1), cols[i])
        for k in range(10):                                              # border chevrons
            x = x0 + 0.1 + k * 0.23
            m.tri_facing((x, y1 - 0.25, z + 0.004), (x + 0.2, y1 - 0.25, z + 0.004), (x + 0.1, y1 - 0.08, z + 0.004), (0, 0, 1), cols[k % 4])
            m.tri_facing((x, y0 + 0.25, z + 0.004), (x + 0.2, y0 + 0.25, z + 0.004), (x + 0.1, y0 + 0.08, z + 0.004), (0, 0, 1), cols[(k + 2) % 4])
        for k in range(12):                                              # little lamps
            x = x0 + 0.1 + k * 0.21
            for y in (y0 - 0.02, y1 + 0.02):
                m.box((x - 0.025, y - 0.025, 0.0), (x + 0.025, y + 0.025, z + 0.03), "emissive", skip=("z-",))
        return m
    return b


def ov_wedding_curtain():
    """KARACHI: a wedding fairy-light curtain falling down a facade: twenty glowing strands over one storey (face
    overlay; stack it up the house)"""
    def b():
        m = Mesh()
        for k in range(20):
            x = -HB + 0.075 + k * 0.15
            _strip(m, (x, ST, 0.12), (x + 0.03 * math.sin(k), 0.0, 0.14), 0.025, (0, 0, 1), "emissive")
        return m
    return b


def edge_parapet_date_plaque():
    """KARACHI: the balustrade parapet with urns and, in the middle, a raised plaque with its date"""
    def b():
        m = edge_parapet_urns()()
        _flat_prism(m, [(-0.5, 0.95), (0.5, 0.95), (0.5, 1.35), (0.0, 1.55), (-0.5, 1.35)], -0.2, 0.0, "trim", open_edges=(0,))
        m.box((-0.35, 1.02, 0.0), (0.35, 1.28, 0.025), "accent", skip=("z-",))
        for k in range(4):
            x = -0.27 + k * 0.17
            _strip(m, (x, 1.07, 0.03), (x, 1.23, 0.03), 0.04, (0, 0, 1), "trim")
        return m
    return b


# ------------------------------------------------------------------ Mughal walled city (r1_mughal_walled)
def wall_jharokha_bangla():
    """MUGHAL MARK: the jharokha under a curved bangla roof -- a bay 0.7 m out on carved brackets, a jali front with a
    cusped arch, slim columns, and the roof bowing down to its corners"""
    def b():
        m = _wall(K, [_rect(-0.7, 0.4, 0.7, 2.3)], reveal="trim")
        d, x0, x1 = 0.7, -1.0, 1.0
        for x in (-0.8, 0.0, 0.8):
            _corbel(m, x, 0.35, d, 0.75, 0.1, "trim", 0.85)
        m.box((x0, 0.25, 0.0), (x1, 0.4, d + 0.05), "trim", skip=("z-",))
        m.box((x0 + 0.05, 0.4, d - 0.08), (x1 - 0.05, 0.95, d - 0.02), "trim", 0.95)
        _diag(m, x0 + 0.1, 0.45, x1 - 0.1, 0.9, d - 0.01, 0.12, 0.03, "trim")
        o = arch("lobed", 1.2, 1.25, 0.95, n=3)
        m.wall_cut(_rect(x0 + 0.05, 0.95, x1 - 0.05, 2.25), [o], d - 0.08, d - 0.02, "trim", reveal_slot="trim")
        m.pane(-0.6, 0.95, 0.6, 2.2, d - 0.3)
        for x in (x0 + 0.08, x1 - 0.08):
            m.cyl(x, d - 0.05, 0.05, 0.4, 2.25, "trim", n=6, caps=False)
        n = 8                                                            # the bangla roof: an arched ridge, drooping corners
        xs = [x0 - 0.2 + (x1 - x0 + 0.4) * i / n for i in range(n + 1)]
        ys = [2.25 + 0.35 * math.sin(math.pi * i / n) for i in range(n + 1)]
        for i in range(n):
            m.quad_facing((xs[i], ys[i] + 0.1, -0.05), (xs[i + 1], ys[i + 1] + 0.1, -0.05), (xs[i + 1], ys[i + 1] - 0.12, d + 0.3), (xs[i], ys[i] - 0.12, d + 0.3), (0, 1, 0.4), "trim", 0.95)
            m.quad_facing((xs[i], ys[i] + 0.06, -0.05), (xs[i + 1], ys[i + 1] + 0.06, -0.05), (xs[i + 1], ys[i + 1] - 0.16, d + 0.3), (xs[i], ys[i] - 0.16, d + 0.3), (0, -1, -0.4), "trim", 0.6)
            m.quad_facing((xs[i], ys[i] - 0.16, d + 0.3), (xs[i + 1], ys[i + 1] - 0.16, d + 0.3), (xs[i + 1], ys[i + 1] - 0.12, d + 0.3), (xs[i], ys[i] - 0.12, d + 0.3), (0, 0, 1), "trim", 0.8)
        m.lathe([(0.0, 2.65), (0.06, 2.72), (0.0, 2.95)], "accent2", n=5, cz=d * 0.4)
        return m
    return b


def edge_chhajja():
    """MUGHAL / RAJPUT: the deep stone chhajja eave over a storey (edge overlay; y 0 = the storey top), on brackets"""
    def b():
        m = Mesh()
        _chhajja(m, -HB, HB, 0.0, 0.85, brackets=3)
        return m
    return b


def wall_cusped_arch():
    """MUGHAL: the cusped (multifoil) arch bay -- a passage or a recess with the scalloped arch, a frame and spandrels"""
    def b():
        o = arch("lobed", 1.8, 2.8, 0.0, n=5)
        m = _wall(K, [o])
        _arch_band(m, o, 0.14, -0.01, 0.03, "trim")
        m.wall_cut(_rect(-1.25, 0.0, 1.25, 3.05), [_off(o, 0.14)], -0.01, 0.015, "accent", 0.95)
        _u_frame(m, -1.25, 3.05, 1.25, 0.08, 0.0, 0.04, "trim")
        for x in (-0.95, 0.95):
            m.wall_cut([(x + 0.12 * math.cos(math.tau * k / 8), 2.65 + 0.12 * math.sin(math.tau * k / 8)) for k in range(8)], [], 0.015, 0.035, "accent2")
        return m
    return b


def dome_bulbous_marble():
    """MUGHAL MARK: the bulbous white marble dome on its drum (crown), a lotus band and a gilt finial"""
    def b():
        m = Mesh()
        m.box((-1.4, 0.0, -1.4), (1.4, 0.4, 1.4), "trim", 0.9, skip=("y-",))
        m.cyl(0, 0, 1.1, 0.4, 1.3, "trim", n=12, caps=False)
        for k in range(12):
            a = math.tau * (k + 0.5) / 12
            sub = Mesh()
            sub.quad_facing((-0.12, 0.6, 0.0), (0.12, 0.6, 0.0), (0.12, 1.1, 0.0), (-0.12, 1.1, 0.0), (0, 0, 1), "frame", 0.45)
            _place(m, sub, math.degrees(a) + 90, dx=1.105 * math.cos(a), dz=-1.105 * math.sin(a))
        m.lathe([(1.15, 1.3), (1.2, 1.4), (0.0, 1.42)], "trim", n=12, shade=0.9)
        _bulb(m, 1.05, 1.42, "trim", n=12, h=2.0)
        return m
    return b


def ov_wire_net():
    """the overhead tangle of wires over a gali at storeys 2-3 (along X, y 6.4..8.5): sagging cables at many heights"""
    def b():
        m = Mesh()
        import random
        r = random.Random(11)
        for k in range(16):
            y = r.uniform(6.6, 8.4)
            z0, z1 = r.uniform(-1.4, 1.4), r.uniform(-1.4, 1.4)
            sag = r.uniform(0.2, 0.6)
            a, c = (-HB, y, z0), (HB, y + r.uniform(-0.3, 0.3), z1)
            mid = (0.0, (a[1] + c[1]) / 2 - sag, (z0 + z1) / 2)
            m.tube(a, mid, 0.012, "frame", n=3)
            m.tube(mid, c, 0.012, "frame", n=3)
        return m
    return b


# ------------------------------------------------------------------ Oman (r1_omani_oasis)
def edge_parapet_triangle():
    """OMAN: the parapet of triangular merlons"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.45)]
        for k in range(5):
            x = HB - 0.3 - k * 0.6
            p += [(x, 0.95), (x - 0.3, 0.45)]
        _flat_prism(m, p, -0.45, 0.0, "wall", open_edges=(0,))
        return m
    return b


def wall_beam_ends():
    """OMAN: an earth bay with the row of palm-trunk beam ends projecting at the floor line, a small shuttered window"""
    def b():
        m = _wall(K, [_rect(-0.3, 1.2, 0.3, 1.9)])
        m.box((-0.295, 1.205, -0.32), (0.295, 1.895, -0.28), "accent", 0.85)
        for k in range(8):
            x = -1.33 + k * 0.38
            sub = Mesh()
            sub.cyl(0.0, 0.0, 0.07, 0.0, 0.3, "frame", n=5)
            m.add(sub, lambda p, x=x: (x + p[0], 3.0 - p[2], p[1] - 0.02))      # (a rotation: the log points out)
        return m
    return b


def wall_door_omani():
    """OMAN MARK: the carved studded double door painted blue or green, in its heavy timber lintel frame with a carved
    panel over it"""
    def b():
        x0, x1, y1 = -0.65, 0.65, 2.3
        m = _wall(K, [_rect(x0, 0.0, x1, 2.85)], reveal="frame")
        m.box((x0 + 0.005, 0.0, -0.36), (x1 - 0.005, y1, -0.3), "accent")
        _strip(m, (0.0, 0.0, -0.295), (0.0, y1, -0.295), 0.05, (0, 0, 1), "frame")
        _stud_grid(m, x0 + 0.1, 0.3, x1 - 0.1, y1 - 0.2, -0.295, 4, 7)
        m.box((x0 + 0.005, y1, -0.4), (x1 - 0.005, 2.845, -0.3), "frame", 0.85)
        _beads(m, x0 + 0.05, x1 - 0.05, y1 + 0.1, 2.75, -0.3, -0.27, 7, "frame", 0.75)
        _u_frame(m, x0, 2.85, x1, 0.14, 0.0, 0.08, "frame", 0.8)
        for x in (-0.15, 0.15):
            m.cyl(x, -0.27, 0.04, 1.1, 1.15, "accent2", n=6)
        return m
    return b


def fort_round_tower(part):
    """OMAN MARK: the great round fort tower (Nizwa), a cell a part: base (battered drum; stack), shaft (drum with gun
    slits), top (the crenellated top with its parapet walk and a flag)"""
    def b():
        m = Mesh()
        if part == "base":
            m.cyl(0, 0, 1.5, 0.0, ST, "wall", n=14, r1=1.44, caps=False)
        elif part == "shaft":
            m.cyl(0, 0, 1.44, 0.0, ST, "wall", n=14, r1=1.4, caps=False)
            for k in range(6):
                a = math.tau * k / 6
                sub = Mesh()
                sub.quad_facing((-0.05, 1.3, 0.0), (0.05, 1.3, 0.0), (0.05, 1.9, 0.0), (-0.05, 1.9, 0.0), (0, 0, 1), "frame", 0.35)
                _place(m, sub, math.degrees(a) + 90, dx=1.425 * math.cos(a), dz=-1.425 * math.sin(a))
        else:
            m.cyl(0, 0, 1.4, 0.0, 0.72, "wall", n=14, caps=False)
            m.lathe([(1.4, 0.7), (1.48, 0.8), (0.0, 0.8)], "wall", n=14, shade=0.9)
            for k in range(14):
                a0 = math.tau * k / 14
                sub = Mesh()
                _flat_prism(sub, [(-0.2, 0.0), (0.2, 0.0), (0.2, 0.35), (0.0, 0.55), (-0.2, 0.35)], -0.3, 0.0, "wall", 0.95, open_edges=(0,))
                _place(m, sub, math.degrees(a0) + 90, dx=1.45 * math.cos(a0), dy=0.8, dz=-1.45 * math.sin(a0))
            m.cyl(0.0, 0.0, 0.03, 0.8, 3.0, "frame", n=3)
            m.quad_facing((0.0, 2.4, 0.0), (0.8, 2.4, 0.0), (0.8, 2.95, 0.0), (0.0, 2.95, 0.0), (0, 0, 1), "fabric")
            m.quad_facing((0.0, 2.4, -0.003), (0.8, 2.4, -0.003), (0.8, 2.95, -0.003), (0.0, 2.95, -0.003), (0, 0, -1), "fabric", 0.85)
        return m
    return b


def ground_falaj():
    """OMAN MARK: lane paving with the falaj channel running down its middle (along Z), its water flowing"""
    def b():
        m = Mesh()
        for x0, x1 in ((-HB, -0.25), (0.25, HB)):
            m.quad_facing((x0, 0.0, -HB), (x1, 0.0, -HB), (x1, 0.0, HB), (x0, 0.0, HB), (0, 1, 0), "ground")
        for x in (-0.25, 0.25):
            m.quad_facing((x, -0.3, -HB), (x, -0.3, HB), (x, 0.0, HB), (x, 0.0, -HB), (-x, 0, 0), "trim", 0.8)
        m.quad_facing((-0.25, -0.18, -HB), (0.25, -0.18, -HB), (0.25, -0.18, HB), (-0.25, -0.18, HB), (0, 1, 0), "water")
        for x in (-0.33, 0.33):
            m.box((x - 0.07 if x > 0 else x - 0.08, 0.0, -HB), (x + 0.08 if x > 0 else x + 0.07, 0.06, HB), "trim", 0.9, skip=("y-", "z-", "z+"))
        return m
    return b


def ov_arish_shade():
    """OMAN: the palm-frond arish shade on four poles over a lane or roof (overlay)"""
    def b():
        m = Mesh()
        for x in (-1.3, 1.3):
            for z in (-1.3, 1.3):
                m.cyl(x, z, 0.06, 0.0, 2.6, "frame", n=4, caps=False)
        for z in (-1.3, 1.3):
            m.box((-1.4, 2.5, z - 0.05), (1.4, 2.6, z + 0.05), "frame", 0.85)
        for k in range(14):
            x = -1.45 + k * 0.223
            _strip(m, (x, 2.62, -1.45), (x + 0.05, 2.64, 1.45), 0.2, (0, 1, 0), "screen")
            _strip(m, (x, 2.615, -1.45), (x + 0.05, 2.635, 1.45), 0.2, (0, -1, 0), "screen")
        return m
    return b


# ------------------------------------------------------------------ Persia (r1_persian_desert)
def badgir(part):
    """PERSIA MARK: the wind tower, a cell a part: base (a plain square shaft; stack it to height), shaft (the vent
    storey: deep vertical slots on all four faces between fins), crown (more slots, a cornice, a little cap)"""
    def b():
        m = Mesh()
        a = 1.0
        if part == "base":
            m.box((-a, 0.0, -a), (a, ST, a), "wall", skip=("y-", "y+"))
        else:
            h = ST if part == "shaft" else 2.2
            m.box((-a + 0.25, 0.0, -a + 0.25), (a - 0.25, h, a - 0.25), "frame", 0.35, skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                for i in range(6):                                       # the fins between the slots
                    x = -a + i * 0.4 - (0.0 if i else 0.0)
                    sub.box((min(x, a - 0.08), 0.0, a - 0.25), (min(x + 0.08, a), h, a), "wall", 0.95, skip=("y-", "y+", "z-"))
                m.add(sub, _rot(k))
            if part == "crown":
                m.box((-a - 0.08, h, -a - 0.08), (a + 0.08, h + 0.2, a + 0.08), "wall", skip=())
                m.box((-a + 0.2, h + 0.2, -a + 0.2), (a - 0.2, h + 0.5, a - 0.2), "wall", 0.9, skip=("y-",))
            else:
                m.box((-a, 0.0, -a), (a, 0.25, a), "wall", 0.9, skip=("y-", "y+"))
        return m
    return b


def roof_vault_barrel():
    """PERSIA: a walkable mud-brick barrel vault roof over a cell (along Z), its two ends arched"""
    def b():
        m = Mesh()
        n = 8
        for k in range(n):
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            p0, p1 = (HB * math.cos(a0), 0.9 * math.sin(a0)), (HB * math.cos(a1), 0.9 * math.sin(a1))
            m.quad_facing((p0[0], p0[1], -HB), (p1[0], p1[1], -HB), (p1[0], p1[1], HB), (p0[0], p0[1], HB), (math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0), "wall", 0.95)
        end = [(-HB, 0.0), (HB, 0.0)] + [(HB * math.cos(math.pi * k / n), 0.9 * math.sin(math.pi * k / n)) for k in range(1, n)]
        _flat_prism(m, end, -HB, -HB + 0.01, "wall", 0.85, open_edges=tuple(range(len(end))))
        _flat_prism(m, end, HB - 0.01, HB, "wall", 0.85, open_edges=tuple(range(len(end))))
        return m
    return b


def dome_mud():
    """PERSIA: a plain mud-brick dome with an oculus at its crown (crown on a cell)"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -HB), (HB, 0.3, HB), "wall", skip=("y-",))
        m.lathe([(1.4, 0.3), (1.3, 0.8), (1.0, 1.3), (0.6, 1.6), (0.25, 1.7), (0.2, 1.62)], "wall", n=12, shade=0.98)
        m.lathe([(0.2, 1.62), (0.0, 1.62)], "frame", n=12, shade=0.3)
        return m
    return b


def wall_orsi():
    """PERSIA MARK: the orsi -- a tall sash window of coloured glass in a fine wooden grid, glowing (court side)"""
    def b():
        x0, y0, x1, y1 = -1.15, 0.3, 1.15, 2.9
        m = _wall(K, [_rect(x0, y0, x1, y1)], reveal="frame")
        m.pane(x0, y0, x1, y1, -0.3)
        cols = ["emissive", "accent", "accent2", "fabric"]
        nx, ny = 8, 10
        for i in range(nx):
            for j in range(ny):
                xa = x0 + (x1 - x0) * i / nx + 0.02
                ya = y0 + (y1 - y0) * j / ny + 0.02
                xb = xa + (x1 - x0) / nx - 0.04
                yb = ya + (y1 - y0) / ny - 0.04
                if j >= 6 or (i + j) % 3 == 0:
                    m.quad_facing((xa, ya, -0.12), (xb, ya, -0.12), (xb, yb, -0.12), (xa, yb, -0.12), (0, 0, 1), cols[(i * 3 + j) % 4])
        _lattice(m, x0 + 0.005, y0 + 0.005, x1 - 0.005, y1 - 0.005, -0.11, -0.06, nx, ny, slot="frame")
        _strip(m, (x0, 2.0, -0.05), (x1, 2.0, -0.05), 0.07, (0, 0, 1), "frame")
        return m
    return b


def wall_portal_knockers():
    """PERSIA: the street portal -- a pointed niche 0.5 m deep, the door at its back with two knockers (a ring for men,
    a bar for women), a bench niche (sakku) each side"""
    def b():
        o = arch("pointed", 1.7, 2.9, 0.0, n=8)
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [o, _rect(-1.4, 0.0, -1.0, 0.9), _rect(1.0, 0.0, 1.4, 0.9)], -0.5, 0.0, "wall", reveal_slot="wall")
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [], -K, -0.5, "wall", 0.9)
        m.box((-0.5, 0.0, -0.5), (0.5, 2.2, -0.46), "frame", 0.85)
        _stud_grid(m, -0.4, 0.3, 0.4, 2.0, -0.455, 3, 5)
        m.cyl(-0.2, -0.43, 0.06, 1.3, 1.34, "metal", n=6)
        m.box((0.16, 1.15, -0.455), (0.24, 1.45, -0.42), "metal")
        _arch_band(m, o, 0.12, -0.01, 0.03, "trim")
        for x0 in (-1.4, 1.0):                                                # the benches in their niches
            m.box((x0 + 0.005, 0.0, -0.495), (x0 + 0.395, 0.45, -0.05), "wall", 0.8, skip=("y-",))
        return m
    return b


def wall_talar():
    """PERSIA: the talar -- a full storey opened to the court between two slim timber columns with carved capitals
    carrying a beam, a painted ceiling behind"""
    def b():
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.35, 0.0, 1.35, 2.85)], -K, 0.0, "wall", reveal_slot="trim")
        for x in (-0.7, 0.7):
            m.cyl(x, -0.2, 0.09, 0.0, 2.55, "frame", n=8, r1=0.07, caps=False)
            m.box((x - 0.12, 0.0, -0.32), (x + 0.12, 0.15, -0.08), "trim", skip=("y-",))
            for j in range(3):
                w = 0.12 + 0.06 * j
                m.box((x - w, 2.55 + j * 0.1, -0.2 - w), (x + w, 2.65 + j * 0.1, -0.2 + w), "frame", 0.85 + 0.05 * j)
        m.box((-1.35, 2.75, -0.35), (1.35, 2.85, -0.05), "frame", 0.8, skip=("x-", "x+"))
        m.quad_facing((-1.35, 2.849, -K), (1.35, 2.849, -K), (1.35, 2.849, 0.0), (-1.35, 2.849, 0.0), (0, -1, 0), "accent", 0.7)
        return m
    return b


# ------------------------------------------------------------------ Rajasthan (r1_rajput_sandstone)
def wall_jharokha_canted():
    """RAJPUT MARK: the canted octagonal sandstone jharokha -- three faces (front and two at 45 degrees) each with a jali
    and a cusped light, on stepped brackets, a chhajja and a little domed roof"""
    def b():
        m = _wall(K, [_rect(-0.7, 0.4, 0.7, 2.3)], reveal="trim")
        d, wf = 0.75, 1.0
        side = math.hypot(d, (1.5 * wf - wf) / 2 + 0.25)
        for x in (-0.5, 0.5):
            _corbel(m, x, 0.35, d, 0.8, 0.12, "trim", 0.85)
        plan = [(-0.9, 0.0), (0.9, 0.0), (wf / 2, d), (-wf / 2, d)]
        m.prism_xz(plan, 0.25, 0.4, "trim", 0.9)
        m.prism_xz([(x * 1.15, z * 1.15) for x, z in plan], 2.3, 2.42, "trim", 0.9)

        def face(w):
            f = Mesh()
            o = arch("lobed", w * 0.6, 1.1, 1.0, n=2)
            f.wall_cut(_rect(-w / 2, 0.4, w / 2, 2.3), [o], -0.06, 0.0, "trim", reveal_slot="trim")
            f.pane(-w * 0.3, 1.0, w * 0.3, 2.1, -0.04)
            f.quad_facing((-w / 2 + 0.05, 0.45, 0.004), (w / 2 - 0.05, 0.45, 0.004), (w / 2 - 0.05, 0.95, 0.004), (-w / 2 + 0.05, 0.95, 0.004), (0, 0, 1), "frame", 0.4)
            _diag(f, -w / 2 + 0.05, 0.45, w / 2 - 0.05, 0.95, 0.008, 0.1, 0.025, "trim")
            return f
        _place(m, face(wf), 0, dz=d)
        ang = math.degrees(math.atan2(d, 0.9 - wf / 2))
        sw = math.hypot(d, 0.9 - wf / 2)
        for s in (-1, 1):
            _place(m, face(sw), s * ang, dx=s * (0.9 + wf / 2) / 2, dz=d / 2)
        m.lathe([(0.75, 2.42), (0.8, 2.6), (0.6, 2.9), (0.25, 3.05), (0.0, 3.08)], "trim", n=8, cz=d * 0.45)
        m.lathe([(0.0, 3.05), (0.05, 3.12), (0.0, 3.25)], "accent2", n=5, cz=d * 0.45)
        return m
    return b


def wall_jali_carved():
    """RAJPUT MARK: a full bay of finely carved stone jali, backlit at night: a stone frame, the pierced screen of
    crossing bars over a glowing back"""
    def b():
        x0, y0, x1, y1 = -1.2, 0.3, 1.2, 2.8
        m = _wall(K, [_rect(x0, y0, x1, y1)], reveal="trim")
        m.quad_facing((x0, y0, -0.3), (x1, y0, -0.3), (x1, y1, -0.3), (x0, y1, -0.3), (0, 0, 1), "emissive", 0.6)
        _lattice(m, x0 + 0.005, y0 + 0.005, x1 - 0.005, y1 - 0.005, -0.12, -0.06, 8, 9, slot="trim")
        _diag(m, x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, -0.08, 0.3, 0.035, "trim")
        _ring(m, x0, y0, x1, y1, 0.1, 0.0, 0.05, "trim")
        return m
    return b


def bastion_round(part):
    """RAJPUT MARK: the fort's round bastion, a cell a part: base (battered sandstone drum; stack), shaft (with a band
    of corbelled machicolations at its top), top (the rounded crenels and a domed kiosk)"""
    def b():
        m = Mesh()
        if part == "base":
            m.cyl(0, 0, 1.5, 0.0, ST, "wall", n=14, r1=1.45, caps=False)
        elif part == "shaft":
            m.cyl(0, 0, 1.45, 0.0, ST, "wall", n=14, r1=1.42, caps=False)
            for k in range(14):
                a = math.tau * k / 14
                sub = Mesh()
                sub.box((-0.08, 2.6, 0.0), (0.08, 3.1, 0.25), "trim", 0.85, skip=("z-",))
                _place(m, sub, math.degrees(a) + 90, dx=1.42 * math.cos(a), dz=-1.42 * math.sin(a))
        else:
            m.cyl(0, 0, 1.42, 0.0, 0.62, "wall", n=14, caps=False)
            m.lathe([(1.42, 0.6), (1.48, 0.68), (0.0, 0.68)], "wall", n=14, shade=0.9)
            for k in range(14):
                a = math.tau * k / 14
                sub = Mesh()
                _flat_prism(sub, [(-0.2, 0.0), (0.2, 0.0), (0.2, 0.3)] + [(0.2 * math.cos(math.pi * i / 4), 0.3 + 0.2 * math.sin(math.pi * i / 4)) for i in range(1, 4)] + [(-0.2, 0.3)],
                            -0.3, 0.0, "wall", 0.95, open_edges=(0,))
                _place(m, sub, math.degrees(a) + 90, dx=1.45 * math.cos(a), dy=0.68, dz=-1.45 * math.sin(a))
            sub = chhatri()()
            m.add(sub, lambda p: (p[0] * 0.55, p[1] * 0.6 + 0.68, p[2] * 0.55))
        return m
    return b


# ------------------------------------------------------------------ Silk road (r1_silk_road)
def portal_pishtaq():
    """SILK ROAD MARK: the monumental tiled portal (Registan) -- 9 m wide (three bays, x -4.5..4.5) and four storeys
    (12.8 m): a tall pointed iwan recess with a muqarnas half-vault, a tile frame, an inscription band, corner shafts"""
    def b():
        m = Mesh()
        W, H = 4.5, 4 * ST
        o = arch("pointed", 5.0, 10.2, 0.0, n=10)
        m.wall_cut(_rect(-W, 0.0, W, H), [o], -1.2, 0.0, "tile", reveal_slot="tile")
        m.wall_cut(o, [], -2.4, -2.3, "wall", 0.85)
        for j in range(5):                                                # muqarnas tiers in the vault head
            yb = 7.0 + j * 0.6
            for i in range(7 - j):
                x = -1.8 + j * 0.25 + i * 0.6
                m.box((x, yb, -2.3), (x + 0.5, yb + 0.55, -2.3 + 0.4 + 0.25 * j), "trim", 0.75 + 0.07 * (i % 2), skip=("z-",))
        m.box((-1.0, 0.0, -2.3), (1.0, 3.0, -2.2), "frame", 0.85)
        _arch_band(m, o, 0.35, -0.01, 0.06, "accent2")
        for x0 in (-W, W - 0.6):
            m.box((x0 + 0.005, 0.0, -0.05), (x0 + 0.595, H, 0.25), "accent", 0.95, skip=("y-",))
        m.box((-W + 0.6, H - 1.0, 0.0), (W - 0.6, H - 0.2, 0.08), "accent2", skip=("z-",))
        for k in range(16):                                               # the inscription band's letters
            x = -W + 0.9 + k * 0.48
            _strip(m, (x, H - 0.9, 0.085), (x + 0.12, H - 0.3, 0.085), 0.07, (0, 0, 1), "trim")
        for x0 in (-W + 0.7, 2.6):                                        # tile panels in the spandrels
            for j in range(4):
                for i in range(2):
                    m.quad_facing((x0 + i * 0.6, 1.0 + j * 1.5, 0.006), (x0 + i * 0.6 + 0.5, 1.0 + j * 1.5, 0.006), (x0 + i * 0.6 + 0.5, 2.3 + j * 1.5, 0.006),
                                  (x0 + i * 0.6, 2.3 + j * 1.5, 0.006), (0, 0, 1), "accent" if (i + j) % 2 else "trim", 0.95)
        return m
    return b


def minaret_round_tapered(part):
    """SILK ROAD MARK: the round tapering brick minaret, a cell a part: base (stack), shaft (tapering, turquoise tile
    bands), top (a muqarnas gallery and the lantern of arches)"""
    def b():
        m = Mesh()
        if part == "base":
            m.cyl(0, 0, 1.2, 0.0, ST, "wall", n=12, r1=1.12, caps=False)
            m.cyl(0, 0, 1.16, 2.5, 2.75, "tile", n=12, r1=1.15, caps=False)
        elif part == "shaft":
            m.cyl(0, 0, 1.12, 0.0, ST, "wall", n=12, r1=1.04, caps=False)
            for y in (0.8, 2.2):
                m.cyl(0, 0, 1.11 - 0.025 * y, y, y + 0.35, "tile", n=12, caps=False)
            for k in range(12):
                a = math.tau * k / 12
                _strip(m, (1.12 * math.cos(a), 1.2, -1.12 * math.sin(a)), (1.08 * math.cos(a + 0.4), 2.0, -1.08 * math.sin(a + 0.4)), 0.05, (math.cos(a), 0, -math.sin(a)), "wall")
        else:
            m.cyl(0, 0, 1.04, 0.0, 0.5, "wall", n=12, caps=False)
            for j in range(3):
                m.cyl(0, 0, 1.08 + 0.12 * j, 0.5 + 0.15 * j, 0.65 + 0.15 * j, "trim", n=12, shade=0.85 + 0.05 * j)
            for k in range(8):
                a = math.tau * k / 8
                m.cyl(1.0 * math.cos(a), -1.0 * math.sin(a), 0.07, 0.95, 2.1, "wall", n=4, caps=False)
            m.cyl(0, 0, 0.75, 0.95, 2.1, "emissive", n=8, caps=False, shade=0.7)
            m.lathe([(1.1, 2.1), (1.15, 2.25), (0.6, 2.6), (0.0, 2.75)], "tile", n=12)
        return m
    return b


def dome_turquoise_ribbed():
    """SILK ROAD MARK: the ribbed turquoise tile dome on a high drum with its inscription band (crown)"""
    def b():
        m = Mesh()
        m.box((-1.45, 0.0, -1.45), (1.45, 0.5, 1.45), "wall", skip=("y-",))
        m.cyl(0, 0, 1.15, 0.5, 1.6, "wall", n=16, caps=False)
        m.cyl(0, 0, 1.16, 1.25, 1.55, "accent2", n=16, caps=False)
        _ribbed_dome(m, 1.2, 1.6, 1.9, n=20, slot="tile", drum=0.0, sh=(1.0, 0.75))
        m.lathe([(0.0, 3.45), (0.08, 3.55), (0.0, 3.85)], "accent2", n=6)
        return m
    return b


def aivan_column():
    """SILK ROAD: the carved wooden column of the aivan porch (decor, standing at a cell corner): a stone base, the
    slender fluted shaft, a stalactite capital carrying a bracket"""
    def b():
        m = Mesh()
        m.lathe([(0.25, 0.0), (0.25, 0.25), (0.15, 0.4)], "trim", n=8)
        m.cyl(0, 0, 0.12, 0.4, 2.7, "frame", n=8, r1=0.09, caps=False)
        for j in range(4):
            w = 0.1 + 0.06 * j
            m.box((-w, 2.7 + 0.12 * j, -w), (w, 2.82 + 0.12 * j, w), "frame", 0.8 + 0.06 * j)
        m.box((-0.5, 3.08, -0.12), (0.5, 3.18, 0.12), "frame", 0.9)
        return m
    return b


def tapchan():
    """SILK ROAD: the chaikhana's tapchan -- a raised timber bed-platform by the hauz, a carpet, cushions, a low table, a
    rail on three sides"""
    def b():
        m = Mesh()
        m.box((-1.1, 0.0, -1.1), (1.1, 0.5, 1.1), "frame", 0.85, skip=("y-",))
        m.quad_facing((-1.0, 0.505, -1.0), (1.0, 0.505, -1.0), (1.0, 0.505, 1.0), (-1.0, 0.505, 1.0), (0, 1, 0), "accent")
        m.quad_facing((-0.8, 0.51, -0.8), (0.8, 0.51, -0.8), (0.8, 0.51, 0.8), (-0.8, 0.51, 0.8), (0, 1, 0), "accent2")
        m.box((-0.35, 0.5, -0.35), (0.35, 0.75, 0.35), "frame", 0.9, skip=("y-",))
        for x, z in ((-0.85, -0.6), (-0.85, 0.2), (0.6, -0.85), (-0.2, -0.85)):
            m.box((x - 0.15, 0.5, z - 0.15), (x + 0.15, 0.62, z + 0.15), "fabric", skip=("y-",))
        for (a, c) in (((-1.05, 0.95, -1.05), (1.05, 0.95, -1.05)), ((-1.05, 0.95, -1.05), (-1.05, 0.95, 1.05)), ((1.05, 0.95, -1.05), (1.05, 0.95, 1.05))):
            m.tube(a, c, 0.03, "frame", n=4)
        for x, z in ((-1.05, -1.05), (1.05, -1.05), (-1.05, 1.05), (1.05, 1.05)):
            m.tube((x, 0.5, z), (x, 0.95, z), 0.03, "frame", n=4)
        return m
    return b


def dome_bazaar_crossing():
    """SILK ROAD MARK: the taq -- the domed bazaar crossing over a lane junction: four corner piers, a pointed arch
    open on every side, a drum and a dome with a lit lantern (a cell over the passage)"""
    def b():
        m = Mesh()
        o = arch("pointed", 2.0, 3.6, 0.0, n=6)
        for k in range(4):                                                # each side owns one corner pier
            sub = Mesh()
            sub.wall_cut(_rect(-HB + 0.4, 0.0, HB, 4.2), [o], HB - 0.4, HB, "wall", reveal_slot="wall")
            _arch_band(sub, [(x, y) for x, y in o], 0.1, HB - 0.01, HB + 0.03, "trim")
            m.add(sub, _rot(k))
        m.box((-HB, 4.2, -HB), (HB, 4.4, HB), "wall", 0.9, skip=())
        m.cyl(0, 0, 1.2, 4.4, 4.9, "wall", n=12, caps=False)
        _ribbed_dome(m, 1.25, 4.9, 1.3, n=12, slot="wall", sh=(1.0, 0.9))
        m.cyl(0, 0, 0.25, 6.15, 6.5, "emissive", n=6)
        m.lathe([(0.3, 6.5), (0.0, 6.75)], "wall", n=6)
        return m
    return b


# ------------------------------------------------------------------ register
INDIC = ["mughal_walled", "rajput_sandstone", "ganga_ghat", "karachi"]
PIECES["chhatri"] = _w("cell", chhatri(), INDIC, lod1="keep", kind="crown", notes="domed pavilion on four columns (roof corner crown)")
GG = ["ganga_ghat"]
PIECES["ghat_steps_wide"] = _w("cell", ghat_steps_wide(), GG, collide="ramp", kind="stair", span=(1, 2), notes="GANGA MARK: ghat steps 3.2 m down to +Z (water side)")
for p in ("base", "shaft", "top"):
    PIECES[f"shikhara_spire_{p}"] = _w("cell", shikhara_spire(p), GG, lod1="keep", kind="tower", notes=f"GANGA MARK: nagara spire {p} (base, shaft x2-4, top)")
PIECES["ghat_umbrella"] = _w("cell", ghat_umbrella(), GG, lod1="keep", notes="cane umbrella over a priest's platform")
PIECES["ov_marigold_garland"] = _w("wall", ov_marigold_garland(), GG + ["newar"], lod1="drop", collide=False, kind="overlay", notes="marigold garlands over a door")
PIECES["band_flood"] = _w("wall", band_flood(), GG, lod1="drop", collide=False, kind="overlay", notes="dark flood-mark band ~1.6 m")
KA = ["karachi"]
PIECES["ov_tank_drum"] = _w("cell", ov_tank_drum(), KA + ["latin_hillside"], lod1="drop", kind="overlay", notes="plastic tank drums (frame = black, accent = blue)")
PIECES["wall_jharokha_k"] = _w("wall", wall_jharokha(), KA, lod1="keep", notes="KARACHI MARK: Gizri-stone jharokha on brackets")
PIECES["wall_veranda_gothic_t"] = _w("wall", wall_veranda_gothic(), KA, lod1="keep", notes="Indo-Gothic veranda storey (1.8 m deep)")
PIECES["ov_truck_art_panel"] = _w("wall", ov_truck_art_panel(), KA, lod1="drop", kind="overlay", notes="KARACHI MARK: truck-art panel with little lamps")
PIECES["ov_wedding_curtain"] = _w("wall", ov_wedding_curtain(), KA + ["ganga_ghat", "mughal_walled"], lod1="keep", collide=False, kind="overlay",
                                  notes="fairy-light strands down a storey (stack)")
PIECES["edge_parapet_date_plaque"] = _w("edge", edge_parapet_date_plaque(), KA, lod1="keep", notes="balustrade parapet with urns and a date plaque")
MU = ["mughal_walled"]
PIECES["wall_jharokha_bangla_k"] = _w("wall", wall_jharokha_bangla(), MU + ["rajput_sandstone"], lod1="keep", notes="MUGHAL MARK: jharokha under a bangla roof")
PIECES["edge_chhajja"] = _w("edge", edge_chhajja(), MU + ["rajput_sandstone", "ganga_ghat"], lod1="keep", collide=False, kind="overlay",
                            notes="deep stone eave at a storey top (y 0 = the storey top)")
PIECES["wall_cusped_arch_k"] = _w("wall", wall_cusped_arch(), MU, notes="cusped multifoil arch bay")
PIECES["dome_bulbous_marble"] = _w("cell", dome_bulbous_marble(), MU, lod1="keep", kind="crown", notes="MUGHAL MARK: bulbous marble dome, gilt finial")
PIECES["ov_wire_net"] = _w("cell", ov_wire_net(), MU + KA + ["ganga_ghat"], lod1="drop", collide=False, kind="overlay", notes="wire tangle along X at y 6.6-8.4")
OM = ["omani_oasis"]
PIECES["edge_parapet_triangle_k"] = _w("edge", edge_parapet_triangle(), OM, lod1="keep", notes="triangle merlons")
PIECES["wall_beam_ends_k"] = _w("wall", wall_beam_ends(), OM + ["saharan_kasbah"], notes="palm beam ends at the floor line, small window")
PIECES["wall_door_omani_k"] = _w("wall", wall_door_omani(), OM, notes="OMAN MARK: carved studded painted door, lintel frame")
for p in ("base", "shaft", "top"):
    PIECES[f"fort_round_tower_{p}"] = _w("cell", fort_round_tower(p), OM, lod1="keep", kind="tower", notes=f"OMAN MARK: round fort tower {p} (base xN, shaft, top)")
PIECES["ground_falaj"] = _w("cell", ground_falaj(), OM, kind="ground", notes="OMAN MARK: lane paving with the falaj channel along Z")
PIECES["ov_arish_shade"] = _w("cell", ov_arish_shade(), OM, lod1="keep", collide=False, kind="overlay", notes="palm-frond shade on poles")
PE = ["persian_desert"]
for p in ("base", "shaft", "crown"):
    PIECES[f"badgir_{p}"] = _w("cell", badgir(p), PE, lod1="keep", kind="tower", notes=f"PERSIA MARK: wind tower {p} (base xN, shaft, crown)")
PIECES["roof_vault_barrel"] = _w("cell", roof_vault_barrel(), PE + OM, lod1="keep", kind="roof", notes="walkable barrel vault along Z")
PIECES["dome_mud"] = _w("cell", dome_mud(), PE, lod1="keep", kind="crown", notes="mud dome with an oculus")
PIECES["wall_orsi_k"] = _w("wall", wall_orsi(), PE, notes="PERSIA MARK: coloured-glass sash in a wooden grid, glowing")
PIECES["wall_portal_knockers_k"] = _w("wall", wall_portal_knockers(), PE, notes="street portal niche, two knockers, bench niches")
PIECES["wall_talar_k"] = _w("wall", wall_talar(), PE, lod1="keep", notes="talar: storey open to the court on two columns")
RJ = ["rajput_sandstone"]
PIECES["wall_jharokha_canted_k"] = _w("wall", wall_jharokha_canted(), RJ, lod1="keep", notes="RAJPUT MARK: canted octagonal jharokha, domed top")
PIECES["wall_jali_carved_k"] = _w("wall", wall_jali_carved(), RJ + MU, notes="RAJPUT MARK: full-bay carved jali, backlit")
for p in ("base", "shaft", "top"):
    PIECES[f"bastion_round_{p}"] = _w("cell", bastion_round(p), RJ, lod1="keep", kind="tower", notes=f"RAJPUT MARK: round bastion {p} (base xN, shaft, top)")
SR = ["silk_road"]
PIECES["portal_pishtaq"] = _w("wall", portal_pishtaq(), SR, lod1="keep", span=(3, 1), notes="SILK ROAD MARK: 9 m wide (x -4.5..4.5), 4 storeys tall tiled portal")
for p in ("base", "shaft", "top"):
    PIECES[f"minaret_round_tapered_{p}"] = _w("cell", minaret_round_tapered(p), SR, lod1="keep", kind="tower", notes=f"SILK ROAD MARK: tapered minaret {p}")
PIECES["dome_turquoise_ribbed"] = _w("cell", dome_turquoise_ribbed(), SR, lod1="keep", kind="crown", notes="SILK ROAD MARK: ribbed turquoise dome")
PIECES["aivan_column"] = _w("corner", aivan_column(), SR, lod1="keep", kind="decor", notes="carved wooden porch column (stands on the corner)")
PIECES["tapchan"] = _w("cell", tapchan(), SR, lod1="drop", notes="chaikhana bed-platform")
PIECES["dome_bazaar_crossing"] = _w("cell", dome_bazaar_crossing(), SR + PE, lod1="keep", kind="crown", notes="SILK ROAD MARK: domed bazaar crossing over a junction")

for civ, acc, extra in (("ganga_ghat", ("#e06a1a", "#f2a01e"), {}), ("karachi", ("#2a8a8a", "#f2c43a"), {}),
                        ("mughal_walled", ("#a8442e", "#c9a23a"), {}), ("omani_oasis", ("#2e5d8a", "#c9a23a"), {"fabric": "#b0322a"}),
                        ("persian_desert", ("#2a6ab0", "#c9a23a"), {"fabric": "#2a8a4a"}), ("rajput_sandstone", ("#c9a23a", "#b0322a"), {}),
                        ("silk_road", ("#2a4a9a", "#c9a23a"), {"tile": "#2aa0b0"})):
    for v in PALETTES.get(civ, []):
        v["accent"], v["accent2"] = acc
        v.update(extra)
