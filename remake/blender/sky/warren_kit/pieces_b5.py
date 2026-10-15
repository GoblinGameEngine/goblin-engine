"""pieces_b5.py -- warren kit batch 4b: the generator's requests for creole_colonial, hk_neon_canyon, iberian_white,
latin_hillside, mzab_ghadames, nouvelle_france, taipei_tiepi; and the budget pass's LITE marks (wall_roshan_lite_*,
wall_jetty_lite_t <= 250 tris; edge_parapet_jali_k rebuilt <= 150).
"""
import math

from geom import Mesh, _dedupe, arch
from pieces import BAY, BOTH, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall
from pieces_b4 import _flat_prism, _gable_seg
from pieces_marks import _beads, _corbel, _crest, _diag, _hip, _lightbox, _off, _place, _ring


# ------------------------------------------------------------------ helpers
def _frustum(m, a0, a1, y0, y1, slot, shade=1.0, top=False, cx=0.0, cz=0.0):
    """a square frustum (battered tower): half-width a0 at y0 to a1 at y1, four sides (and the top)"""
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    lo = [(cx + x * a0, y0, cz + z * a0) for x, z in sq]
    hi = [(cx + x * a1, y1, cz + z * a1) for x, z in sq]
    for k in range(4):
        j = (k + 1) % 4
        nx, nz = [(0, -1), (1, 0), (0, 1), (-1, 0)][k]
        m.quad_facing(lo[k], lo[j], hi[j], hi[k], (nx, 0.1, nz), slot, shade)
    if top:
        m.quad_facing(*hi, (0, 1, 0), slot, shade)


def _u_frame(m, x0, y1, x1, w, z0, z1, slot, shade=1.0):
    """a door's surround: up the jambs and over the head, nothing at the threshold"""
    e = 0.005
    m.wall_cut(_rect(x0 - w, 0.0, x1 + w, y1 + w), [_rect(x0 - e, -1.0, x1 + e, y1 + e)], z0 - 0.01, z1, slot, shade)


def _door_leaf(m, x0, y1, x1, z, slot="frame", studs=0, shade=0.85):
    """a door leaf set in its reveal (a hair inside the opening), with optional stud rows (flat quads)"""
    m.box((x0 + 0.005, 0.0, z - 0.05), (x1 - 0.005, y1 - 0.005, z), slot, shade)
    for i in range(studs):
        for j in range(studs + 2):
            x = x0 + (x1 - x0) * (i + 0.5) / studs
            y = 0.25 + (y1 - 0.45) * j / (studs + 1)
            m.quad_facing((x - 0.025, y - 0.025, z + 0.004), (x + 0.025, y - 0.025, z + 0.004), (x + 0.025, y + 0.025, z + 0.004),
                          (x - 0.025, y + 0.025, z + 0.004), (0, 0, 1), "metal")


def _pot(m, x, y, z, r=0.13, h=0.22, slot="accent", flower="fabric"):
    m.lathe([(r * 0.7, y), (r, y + h * 0.7), (r * 1.05, y + h)], slot, n=5, cx=x, cz=z)
    m.cyl(x, z, r * 1.1, y + h, y + h + 0.16, "plant", n=4, r1=r * 0.5, caps=False)
    m.box((x - 0.04, y + h + 0.1, z - 0.04), (x + 0.04, y + h + 0.18, z + 0.04), flower, skip=("y-",))


def _bell(m, x, y, z, r=0.25):
    m.lathe([(0.0, y - 0.45), (r, y - 0.45), (r * 0.7, y - 0.25), (r * 0.55, y), (0.0, y + 0.05)], "metal", n=8, cx=x, cz=z)


# ------------------------------------------------------------------ Creole colonial (r3_creole_colonial)
def wall_window_medio_punto():
    """the floor-to-ceiling window: a stone surround, turned bars, louvred shutters folded back, and over it the medio
    punto -- a stained-glass lunette that glows at night"""
    def b():
        w, y0, yh = 1.1, 0.12, 2.35
        lun = [(-w / 2, yh), (w / 2, yh)] + [(w / 2 * math.cos(math.pi * k / 8), yh + w / 2 * math.sin(math.pi * k / 8)) for k in range(1, 8)]
        m = _wall(K, [_rect(-w / 2, y0, w / 2, yh), lun])
        m.pane(-w / 2, y0, w / 2, yh, -0.45)
        m.wall_cut(lun, [], -0.18, -0.14, "emissive")
        for k in range(1, 4):                                                       # the lunette's leading
            a = math.pi * k / 4
            _strip(m, (0.0, yh, -0.12), (w / 2 * math.cos(a), yh + w / 2 * math.sin(a), -0.12), 0.03, (0, 0, 1), "accent")
        _strip(m, (-w / 2, yh, -0.11), (w / 2, yh, -0.11), 0.05, (0, 0, 1), "accent")
        for k in range(1, 8):                                                       # turned bars
            x = -w / 2 + w * k / 8
            m.cyl(x, 0.08, 0.018, y0, yh, "frame", n=4, caps=False)
        for y in (y0 + 0.05, yh - 0.05):
            m.box((-w / 2 - 0.05, y - 0.03, 0.03), (w / 2 + 0.05, y + 0.03, 0.13), "frame", 0.8)
        for s in (-1, 1):                                                           # shutters folded back
            x0 = s * (w / 2 + 0.12)
            m.box((min(x0, x0 + s * 0.55), y0, 0.0), (max(x0, x0 + s * 0.55), yh, 0.05), "accent", skip=("z-",))
            for j in range(8):
                y = y0 + 0.2 + j * 0.25
                _strip(m, (x0 + s * 0.05, y, 0.055), (x0 + s * 0.5, y, 0.055), 0.08, (0, 0.4, 1), "accent")
        full = [(-w / 2, y0), (w / 2, y0), (w / 2, yh)] + lun[2:] + [(-w / 2, yh)]      # one surround: jambs + arch
        m.wall_cut(_off(full, 0.12), [_off(full, 0.005)], -0.01, 0.04, "trim")
        return m
    return b


def wall_balcony_covered():
    """Cartagena's long covered balcony: timber, 1 m out on corbels the whole bay, turned balusters, three posts, a
    small tile roof; a tall door behind"""
    def b():
        m = _wall(K, [_rect(-0.55, 0.0, 0.55, 2.4)], reveal="frame")
        _door_leaf(m, -0.55, 2.4, 0.55, -0.3, "accent")
        d = 1.0
        for x in (-1.1, 0.0, 1.1):
            _corbel(m, x, 0.0, d - 0.05, 0.7, 0.12, "accent", 0.85)
        m.box((-HB, -0.1, 0.004), (HB, 0.0, d), "accent", 0.85, skip=("z-", "x-", "x+"))
        m.box((-HB, 0.9, d - 0.08), (HB, 0.98, d), "accent", skip=("x-", "x+"))
        m.box((-HB, -0.005, d - 0.08), (HB, 0.08, d), "accent", 0.9, skip=("x-", "x+", "y-"))
        for k in range(14):
            x = -HB + 0.11 + k * 0.215
            m.lathe([(0.025, 0.08), (0.045, 0.3), (0.025, 0.5), (0.04, 0.75), (0.025, 0.9)], "accent", n=4, cx=x, cz=d - 0.04)
        for x in (-1.44, 0.0, 1.44):
            m.box((x - 0.05, 0.0, d - 0.1), (x + 0.05, 2.75, d), "accent", 0.85, skip=("y-",))
        m.quad_facing((-HB - 0.05, 3.1, 0.0), (HB + 0.05, 3.1, 0.0), (HB + 0.05, 2.75, d + 0.2), (-HB - 0.05, 2.75, d + 0.2), (0, 1, 0.5), "roof")
        m.quad_facing((-HB - 0.05, 3.07, 0.0), (HB + 0.05, 3.07, 0.0), (HB + 0.05, 2.72, d + 0.2), (-HB - 0.05, 2.72, d + 0.2), (0, -1, -0.5), "accent", 0.6)
        for k in range(10):
            x = -HB + 0.15 + k * 0.3
            _strip(m, (x, 2.77, d + 0.18), (x, 3.09, 0.02), 0.07, (0, 1, 0.5), "roof")
        return m
    return b


def wall_door_carriage():
    """the zaguan carriage door: two tall leaves (2.2 x 3.0 m) with a small inset door, studs, a stone surround with a
    keystone"""
    def b():
        x0, x1, y1 = -1.1, 1.1, 2.95
        m = _wall(K, [_rect(x0, 0.0, x1, y1)], reveal="trim")
        m.box((x0 + 0.005, 0.0, -0.36), (x1 - 0.005, y1 - 0.005, -0.3), "accent", 0.85)
        _strip(m, (0.0, 0.0, -0.295), (0.0, y1, -0.295), 0.05, (0, 0, 1), "frame")
        for xa in (-0.95, 0.1):
            for ya, yb in ((0.2, 1.3), (1.5, 2.8)):
                m.box((xa, ya, -0.3), (xa + 0.85, yb, -0.27), "accent", 0.95, skip=("z-",))
        m.box((-0.8, 0.0, -0.27), (-0.2, 1.9, -0.24), "accent", 0.75, skip=("z-",))               # the inset door
        for y in (0.6, 1.4, 2.2):
            for x in (-0.9, -0.55, 0.3, 0.65, 0.95):
                m.quad_facing((x - 0.03, y - 0.03, -0.265), (x + 0.03, y - 0.03, -0.265), (x + 0.03, y + 0.03, -0.265), (x - 0.03, y + 0.03, -0.265), (0, 0, 1), "metal")
        _u_frame(m, x0, y1, x1, 0.18, 0.0, 0.07, "trim")
        m.box((-0.14, y1 - 0.05, 0.0), (0.14, ST - 0.02, 0.12), "trim", 0.9, skip=("z-",))       # keystone
        return m
    return b


def bell_tower_baroque(part):
    """the baroque cathedral bell tower, a storey a cell: base (pilasters, a cornice; stack it), belfry (an arched lit
    opening each side, a bell, urns at the corners), cupola (octagonal drum, dome, lantern, cross)"""
    def b():
        m = Mesh()
        a = 1.4
        if part == "base":
            m.box((-a, 0.0, -a), (a, ST, a), "wall", skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                for x in (-1.2, 1.2):
                    sub.box((x - 0.15, 0.0, a), (x + 0.15, ST - 0.3, a + 0.08), "trim", skip=("z-", "y-"))
                sub.box((-a - 0.08, ST - 0.3, a), (a + 0.08, ST - 0.12, a + 0.15), "trim", skip=("z-",))
                sub.pane(-0.3, 1.2, 0.3, 2.3, a + 0.01)
                _ring(sub, -0.3, 1.2, 0.3, 2.3, 0.08, a, a + 0.05, "trim")
                _place(m, sub, 90 * k)
        elif part == "belfry":
            m.box((-a - 0.1, 0.0, -a - 0.1), (a + 0.1, 0.2, a + 0.1), "trim", skip=("y-",))
            op = arch("round", 1.4, 2.3, 0.4, n=5)
            for k in range(4):
                sub = Mesh()
                sub.wall_cut(_rect(-a, 0.2, a, ST - 0.24), [op], a - 0.3, a, "wall", reveal_slot="trim")
                sub.wall_cut(_off(op, 0.12), [_off(op, 0.005)], a - 0.01, a + 0.05, "trim")
                for x in (-1.15, 1.15):
                    sub.box((x - 0.12, 0.2, a), (x + 0.12, ST - 0.25, a + 0.08), "trim", 0.9, skip=("z-",))
                _place(m, sub, 90 * k)
            m.box((-a + 0.3, 0.2, -a + 0.3), (a - 0.3, 0.25, a - 0.3), "ground", 0.6)
            _bell(m, 0.0, 2.3, 0.0, 0.4)
            m.box((-a - 0.15, ST - 0.25, -a - 0.15), (a + 0.15, ST, a + 0.15), "trim")
            for x in (-a, a):
                for z in (-a, a):
                    m.lathe([(0.12, ST), (0.2, ST + 0.25), (0.14, ST + 0.45), (0.04, ST + 0.55), (0.0, ST + 0.7)], "trim", n=6, cx=x, cz=z)
        else:
            m.cyl(0, 0, 1.05, 0.0, 1.2, "wall", n=8, caps=False)
            for k in range(8):
                ang = math.tau * (k + 0.5) / 8
                sub = Mesh()
                sub.quad_facing((-0.15, 0.35, 0.0), (0.15, 0.35, 0.0), (0.15, 0.95, 0.0), (-0.15, 0.95, 0.0), (0, 0, 1), "emissive")
                _place(m, sub, math.degrees(ang) + 90, dx=0.98 * math.cos(ang), dz=-0.98 * math.sin(ang))
            m.cyl(0, 0, 1.15, 1.2, 1.35, "trim", n=8)
            m.lathe([(1.05, 1.35), (0.95, 1.9), (0.65, 2.35), (0.3, 2.55), (0.22, 2.55)], "tile", n=8)
            m.cyl(0, 0, 0.22, 2.55, 3.05, "trim", n=6, caps=False)
            m.lathe([(0.3, 3.05), (0.2, 3.25), (0.0, 3.4)], "tile", n=6)
            m.box((-0.02, 3.4, -0.02), (0.02, 4.0, 0.02), "metal")
            m.box((-0.15, 3.75, -0.02), (0.15, 3.8, 0.02), "metal")
        return m
    return b


def kiosco_gazebo():
    """the plaza bandstand: an octagonal stone platform, eight slender iron columns, a railing, an octagonal roof with
    a lantern finial (cell decor, its own cell)"""
    def b():
        m = Mesh()
        r = 1.35
        oct_ = [(r * math.cos(math.tau * k / 8 + math.pi / 8), -r * math.sin(math.tau * k / 8 + math.pi / 8)) for k in range(8)]
        m.prism_xz(oct_, 0.0, 0.7, "trim", 0.9)
        for k, (x, z) in enumerate(oct_):
            m.cyl(x * 0.93, z * 0.93, 0.04, 0.7, 3.1, "metal", n=4, caps=False)
            x2, z2 = oct_[(k + 1) % 8]
            if k != 0:
                m.tube((x * 0.93, 1.6, z * 0.93), (x2 * 0.93, 1.6, z2 * 0.93), 0.02, "metal", n=3)
            m.tube((x * 0.93, 2.85, z * 0.93), (x2 * 0.93, 2.85, z2 * 0.93), 0.03, "metal", n=3)
        m.lathe([(1.6, 3.05), (1.0, 3.6), (0.2, 4.1), (0.0, 4.15)], "roof", n=8)
        m.lathe([(0.0, 3.0), (1.6, 3.0)], "frame", n=8)
        m.cyl(0, 0, 0.12, 4.05, 4.35, "emissive", n=6)
        m.lathe([(0.15, 4.35), (0.0, 4.6)], "metal", n=6)
        return m
    return b


def edge_parapet_urns():
    """an azotea parapet: a low wall with a balustrade of turned balusters between piers, an urn on each pier"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -0.3), (HB, 0.25, 0.0), "wall", skip=("y-", "x-", "x+"))
        m.box((-HB, 0.85, -0.33), (HB, 0.95, 0.03), "trim", skip=("x-", "x+"))
        for x in (-1.35, 1.35):
            m.box((x - 0.15, 0.24, -0.3), (x + 0.15, 0.86, 0.0), "wall", 0.95, skip=("y-", "y+"))
            m.lathe([(0.1, 0.95), (0.16, 1.1), (0.12, 1.25), (0.05, 1.32), (0.0, 1.42)], "trim", n=6, cx=x, cz=-0.15)
        for k in range(9):
            x = -1.05 + k * 0.2625
            m.lathe([(0.04, 0.25), (0.07, 0.45), (0.035, 0.7), (0.04, 0.85)], "trim", n=4, cx=x, cz=-0.15)
        return m
    return b


# ------------------------------------------------------------------ Hong Kong (r2_hk_neon_canyon)
def ov_sign_arm_big():
    """the big neon sign on a steel arm over the street: a two-storey (6.4 m) lit box hung 1.2-2.6 m out from the face,
    read along the street (its faces to +-X); stack two for four storeys (face overlay)"""
    def b():
        m = Mesh()
        m.box((-0.06, 5.9, 0.0), (0.06, 6.1, 2.9), "metal", skip=("z-",))
        m.tube((0.0, 4.6, 0.02), (0.0, 5.9, 2.6), 0.035, "metal", n=4)
        sub = Mesh()
        _lightbox(sub, 1.2, 0.4, 2.7, 5.8, -0.15, 0.15, nchar=4, vertical=True)
        mir = Mesh()
        mir.add(sub, lambda p: (p[2], p[1], p[0]))               # a reflection: re-wound by _fix_mirror
        m.add(_fix_mirror(mir))
        return m
    return b


def _fix_mirror(m):
    """re-wind every triangle after a mirroring transform (swap two corners)"""
    out = Mesh()
    for s, ts in m.tris.items():
        for a, b, c, sh, uv in ts:
            out.tris[s].append((a, c, b, sh, (uv[0], uv[2], uv[1]) if uv else uv))
    return out


def wall_verandah():
    """a pre-war tong lau verandah storey: the floor slab cantilevered 2 m over the pavement on the street-edge columns,
    a balustrade at its edge, timber french windows behind (stack it storey on storey)"""
    def b():
        m = _wall(T, [_rect(-1.25, 0.0, -0.35, 2.5), _rect(0.35, 0.0, 1.25, 2.5)], reveal="frame")
        for x0 in (-1.25, 0.35):
            m.pane(x0, 0.0, x0 + 0.9, 2.5, -0.14)
            _strip(m, (x0 + 0.45, 0.05, -0.12), (x0 + 0.45, 2.45, -0.12), 0.04, (0, 0, 1), "accent")
            for y in (0.9, 1.7):
                _strip(m, (x0, y, -0.115), (x0 + 0.9, y, -0.115), 0.035, (0, 0, 1), "accent")
        d = 2.0
        m.box((-HB, ST - 0.25, 0.004), (HB, ST - 0.004, d), "trim", 0.9, skip=("z-", "x-", "x+"))
        for x in (-1.3, 1.3):
            m.box((x - 0.17, 0.0, d - 0.34), (x + 0.17, ST - 0.25, d), "trim", skip=("y-", "y+"))
            m.box((x - 0.21, ST - 0.55, d - 0.38), (x + 0.21, ST - 0.25, d + 0.04), "trim", 0.9, skip=("y+",))
        m.box((-1.13, 0.0, d - 0.12), (1.13, 0.95, d - 0.04), "trim", 0.95, skip=("y-", "x-", "x+"))
        for k in range(6):                                               # balustrade openings
            x = -1.0 + k * 0.4
            m.quad_facing((x, 0.2, d - 0.035), (x + 0.22, 0.2, d - 0.035), (x + 0.22, 0.75, d - 0.035), (x, 0.75, d - 0.035), (0, 0, 1), "frame", 0.5)
        return m
    return b


def wall_mosaic():
    """a 1960s mosaic-tile bay: a field of small glazed tiles (shade-varied squares on the tile slot), a pair of steel
    windows with a concrete hood"""
    def b():
        ops = [_rect(-1.15, 0.9, -0.15, 2.2), _rect(0.15, 0.9, 1.15, 2.2)]
        m = _wall(T, ops)
        for x0 in (-1.15, 0.15):
            m.pane(x0, 0.9, x0 + 1.0, 2.2, -0.12)
            _strip(m, (x0 + 0.5, 0.9, -0.1), (x0 + 0.5, 2.2, -0.1), 0.04, (0, 0, 1), "accent")
            _strip(m, (x0, 1.6, -0.095), (x0 + 1.0, 1.6, -0.095), 0.04, (0, 0, 1), "accent")
        from shapely.geometry import Polygon, box as sbox
        holes = [Polygon(_off(o, 0.03)) for o in ops]
        n = 0
        for i in range(10):
            for j in range(10):
                x0, y0 = -HB + i * 0.3 + 0.015, j * 0.32 + 0.015
                cell = sbox(x0, y0, x0 + 0.27, y0 + 0.29)
                if any(cell.intersects(h) for h in holes):
                    continue
                n += 1
                sh = 0.78 + 0.22 * (((i * 5 + j * 3) % 4) / 3)
                m.quad_facing((x0, y0, 0.006), (x0 + 0.27, y0, 0.006), (x0 + 0.27, y0 + 0.29, 0.006), (x0, y0 + 0.29, 0.006), (0, 0, 1), "tile", sh)
        m.box((-1.25, 2.25, 0.0), (1.25, 2.35, 0.35), "trim", 0.9, skip=("z-",))
        return m
    return b


def wall_window_casement_pair():
    """steel casement windows in pairs (green frames), one leaf ajar, a concrete sill"""
    def b():
        ops = [_rect(-1.1, 0.9, -0.2, 2.2), _rect(0.2, 0.9, 1.1, 2.2)]
        m = _wall(T, ops)
        for x0 in (-1.1, 0.2):
            m.pane(x0, 0.9, x0 + 0.9, 2.2, -0.12)
            for k in range(1, 3):
                _strip(m, (x0 + 0.9 * k / 3, 0.9, -0.1), (x0 + 0.9 * k / 3, 2.2, -0.1), 0.035, (0, 0, 1), "accent")
            for y in (1.35, 1.8):
                _strip(m, (x0, y, -0.095), (x0 + 0.9, y, -0.095), 0.03, (0, 0, 1), "accent")
            m.box((x0 - 0.05, 0.84, -0.02), (x0 + 0.95, 0.9, 0.08), "trim", skip=("z-",))
        sub = Mesh()                                                     # a leaf ajar, swung out 35 degrees
        sub.pane(0.03, 0.03, 0.27, 1.27, -0.012)
        _ring(sub, 0.03, 0.03, 0.27, 1.27, 0.03, -0.015, 0.0, "accent")
        _place(m, sub, -35, dx=0.8, dy=0.9, dz=0.0)
        return m
    return b


def ov_roller_shutter():
    """a roller shutter half down over a shopfront: its housing box at 2.6 m, the slats down to 1.4 m, a padlock
    (face overlay)"""
    def b():
        m = Mesh()
        m.box((-1.35, 2.6, 0.0), (1.35, 2.85, 0.28), "metal", 0.85, skip=("z-",))
        m.quad_facing((-1.3, 1.4, 0.18), (1.3, 1.4, 0.18), (1.3, 2.6, 0.18), (-1.3, 2.6, 0.18), (0, 0, 1), "metal")
        for k in range(10):
            y = 1.45 + k * 0.115
            _strip(m, (-1.3, y, 0.185), (1.3, y, 0.185), 0.02, (0, 0, 1), "metal")
        m.box((-1.3, 1.36, 0.14), (1.3, 1.42, 0.22), "metal", 0.6)
        for x in (-1.33, 1.33):
            m.box((x - 0.03, 0.0, 0.08), (x + 0.03, 2.6, 0.24), "metal", 0.7, skip=("y-",))
        return m
    return b


# ------------------------------------------------------------------ Iberian white (r3_iberian_white)
def wall_reja_box():
    """a window in a thick white wall with its box reja: an iron grille cage 0.3 m out, a pot shelf with geraniums, a
    painted surround"""
    def b():
        x0, y0, x1, y1 = -0.5, 0.95, 0.5, 2.25
        m = _wall(K, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.35)
        _ring(m, x0, y0, x1, y1, 0.12, 0.0, 0.015, "accent")
        d, xa, xb = 0.32, -0.65, 0.65
        for k in range(7):
            x = xa + (xb - xa) * k / 6
            _strip(m, (x, y0 - 0.12, d), (x, y1 + 0.08, d), 0.022, (0, 0, 1), "metal")
        for y in (y0 + 0.4, y0 + 0.9):
            _strip(m, (xa, y, d + 0.004), (xb, y, d + 0.004), 0.022, (0, 0, 1), "metal")
        for x in (xa, xb):
            for y in (y0 + 0.4, y0 + 0.9, y1 + 0.08):
                _strip(m, (x, y, 0.0), (x, y, d), 0.022, (math.copysign(1, x), 0, 0), "metal")
        m.box((xa - 0.04, y1 + 0.08, 0.0), (xb + 0.04, y1 + 0.16, d + 0.04), "metal", 0.8, skip=("z-",))
        m.box((xa - 0.04, y0 - 0.2, 0.0), (xb + 0.04, y0 - 0.14, d + 0.04), "metal", 0.8, skip=("z-",))
        for x in (-0.35, 0.0, 0.35):
            _pot(m, x, y0 - 0.14, d * 0.55, r=0.1, h=0.18, slot="tile")
        return m
    return b


def wall_door_studded():
    """an iron-studded door in a stone surround with a lintel and a knocker"""
    def b():
        x0, x1, y1 = -0.6, 0.6, 2.4
        m = _wall(K, [_rect(x0, 0.0, x1, y1)], reveal="trim")
        _door_leaf(m, x0, y1, x1, -0.3, "frame", studs=4)
        _u_frame(m, x0, y1, x1, 0.2, 0.0, 0.06, "ground", 0.9)
        m.box((x0 - 0.3, y1 + 0.2, 0.0), (x1 + 0.3, y1 + 0.34, 0.12), "ground", 0.8, skip=("z-",))
        m.cyl(0.0, -0.22, 0.07, 1.3, 1.34, "metal", n=6)
        return m
    return b


def band_zocalo():
    """the painted base band, 0.8 m, ochre or blue (accent), with its line (face overlay at ground)"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, 0.0), (HB, 0.8, 0.015), "accent", skip=("z-", "y-", "x-", "x+"))
        m.box((-HB, 0.8, 0.0), (HB, 0.84, 0.02), "accent2", skip=("z-", "x-", "x+"))
        return m
    return b


def ov_blue_pots():
    """blue pots hung on a white wall, geraniums in them (Cordoba patios) -- face overlay"""
    def b():
        m = Mesh()
        for k, (x, y) in enumerate(((-1.1, 1.6), (-0.55, 2.2), (0.0, 1.5), (0.55, 2.3), (1.1, 1.7))):
            m.box((x - 0.02, y + 0.05, 0.0), (x + 0.02, y + 0.25, 0.04), "metal")
            _pot(m, x, y, 0.13, r=0.11, h=0.18, slot="accent")
        return m
    return b


def tower_mudejar(part):
    """the Mudejar brick tower, a storey a cell: shaft (sebka lozenge net in brick relief, a glazed tile column band;
    stack it), belfry (two arched lit openings a side, bells), top (a pyramid of green-glazed tile, a ball and vane)"""
    def b():
        m = Mesh()
        a = 1.3
        if part == "shaft":
            m.box((-a, 0.0, -a), (a, ST, a), "roof", skip=("y-", "y+"))
            for k in range(4):
                sub = Mesh()
                for i in range(3):                                      # the sebka lozenges
                    for j in range(3):
                        cx, cy = -0.7 + i * 0.7, 0.7 + j * 0.8
                        pts = [(cx, cy - 0.38), (cx + 0.2, cy), (cx, cy + 0.38), (cx - 0.2, cy)]
                        for p, q in zip(pts, pts[1:] + pts[:1]):
                            _strip(sub, (p[0], p[1], a + 0.005), (q[0], q[1], a + 0.005), 0.04, (0, 0, 1), "roof")
                for y in (ST - 0.25,):
                    for i in range(8):
                        x = -a + 0.05 + i * 0.325
                        sub.quad_facing((x, y, a + 0.008), (x + 0.28, y, a + 0.008), (x + 0.28, y + 0.12, a + 0.008), (x, y + 0.12, a + 0.008), (0, 0, 1),
                                        "tile" if i % 2 else "trim")
                _place(m, sub, 90 * k)
        elif part == "belfry":
            for k in range(4):
                sub = Mesh()
                ops = [arch("round", 0.7, 2.0, 0.5, n=4), [(x + 0.75, y) for x, y in arch("round", 0.7, 2.0, 0.5, n=4)]]
                ops = [[(x - 0.375, y) for x, y in ops[0]], [(x - 0.375, y) for x, y in ops[1]]]
                sub.wall_cut(_rect(-a, 0.0, a, ST), ops, a - 0.3, a, "roof", reveal_slot="roof")
                for o in ops:
                    sub.wall_cut(_off(o, 0.1), [_off(o, 0.005)], a - 0.01, a + 0.04, "tile")
                _place(m, sub, 90 * k)
            m.box((-a + 0.3, 0.3, -a + 0.3), (a - 0.3, 0.35, a - 0.3), "ground", 0.6)
            for x in (-0.4, 0.4):
                _bell(m, x, 2.2, 0.0, 0.28)
            m.box((-a - 0.12, ST - 0.2, -a - 0.12), (a + 0.12, ST, a + 0.12), "roof", 0.9)
        else:
            m.box((-a, 0.0, -a), (a, 0.4, a), "roof", skip=("y-",))
            m.lathe([(a * 1.414, 0.4), (0.0, 3.6)], "tile", n=4)
            m.lathe([(0.0, 3.5), (0.15, 3.65), (0.0, 3.8)], "accent2", n=6)
            m.box((-0.02, 3.8, -0.02), (0.02, 4.4, 0.02), "metal")
            m.box((0.0, 4.15, -0.01), (0.35, 4.3, 0.01), "metal")
        return m
    return b


def ov_toldo():
    """the summer toldo: canvas sheets stretched across a shopping lane at 4.5 m (along X), sagging, with their ropes"""
    def b():
        m = Mesh()
        xs = [-HB + BAY * i / 4 for i in range(5)]
        ys = [4.6 - 0.35 * math.sin(math.pi * i / 4) for i in range(5)]
        for i in range(4):
            for zs, sh in (((-1.3, -0.1), 1.0), ((0.1, 1.3), 0.92)):
                m.quad_facing((xs[i], ys[i], zs[0]), (xs[i + 1], ys[i + 1], zs[0]), (xs[i + 1], ys[i + 1], zs[1]), (xs[i], ys[i], zs[1]), (0, -1, 0), "fabric", sh)
                m.quad_facing((xs[i], ys[i] + 0.004, zs[0]), (xs[i + 1], ys[i + 1] + 0.004, zs[0]), (xs[i + 1], ys[i + 1] + 0.004, zs[1]), (xs[i], ys[i] + 0.004, zs[1]), (0, 1, 0), "fabric", sh * 0.8)
        for z in (-1.35, 0.0, 1.35):
            m.tube((-HB, 4.62, z), (HB, 4.62, z), 0.008, "metal", n=3)
        return m
    return b


# ------------------------------------------------------------------ Latin hillside (r3_latin_hillside)
def ov_tank_round_blue():
    """the round blue fibreglass roof tank on its little stand (accent slot = the blue)"""
    def b():
        m = Mesh()
        m.box((-0.6, 0.0, -0.6), (0.6, 0.25, 0.6), "trim", 0.75, skip=("y-",))
        m.lathe([(0.55, 0.25), (0.62, 0.35), (0.65, 1.05), (0.6, 1.15), (0.25, 1.25), (0.25, 1.32), (0.0, 1.33)], "accent", n=10)
        return m
    return b


def wall_brick_raw():
    """hollow clay brick infill in a grey concrete frame (a favela bay): course lines, a window hole with no frame"""
    def b():
        m = Mesh()
        op = _rect(0.1, 1.0, 0.9, 1.9)
        m.wall_cut(_rect(-1.3, 0.0, 1.3, ST - 0.25), [op], -T, -0.02, "tile", reveal_slot="tile")
        m.pane(0.1, 1.0, 0.9, 1.9, -0.15)
        for k in range(1, 15):
            y = k * 0.2
            for xa, xb in ((-1.3, 0.1), (0.9, 1.3)) if 1.0 < y < 1.9 else ((-1.3, 1.3),):
                _strip(m, (xa, y, -0.018), (xb, y, -0.018), 0.02, (0, 0, 1), "trim")
        for x in (-HB, 1.3):
            m.box((x, 0.0, -T), (x + 0.2, ST, 0.0), "trim", 0.8, skip=("y-", "y+"))
        m.box((-HB, ST - 0.25, -T), (HB, ST, 0.0), "trim", 0.8, skip=("y-", "x-", "x+"))
        return m
    return b


def wall_mural():
    """a blank bay painted with a mural: a sun, a hillside of houses, a wave, a figure (flat colour shapes)"""
    def b():
        m = _wall(T)
        z = 0.006
        sun = [(-0.8 + 0.45 * math.cos(math.tau * k / 10), 2.3 + 0.45 * math.sin(math.tau * k / 10)) for k in range(10)]
        m.wall_cut(sun, [], 0.0, z, "accent2")
        hill = [(-HB, 0.0), (HB, 0.0), (HB, 1.4), (0.8, 1.7), (0.0, 1.3), (-0.9, 1.5), (-HB, 1.1)]
        m.wall_cut(hill, [], 0.0, z, "fabric")
        for k, x in enumerate((-1.1, -0.5, 0.2, 0.8)):
            m.wall_cut(_rect(x, 0.6 + 0.1 * (k % 2), x + 0.35, 1.0 + 0.15 * (k % 2)), [], z, z * 2, ("accent", "accent2", "tile", "trim")[k])
        wave = [(-HB, 0.0), (HB, 0.0), (HB, 0.35)] + [(HB - BAY * i / 8, 0.35 + 0.12 * math.sin(i * 1.6)) for i in range(1, 8)] + [(-HB, 0.4)]
        m.wall_cut(wave, [], z, z * 2, "accent")
        fig = [(0.75, 1.75), (1.05, 1.75), (1.0, 2.5), (1.15, 2.5), (0.9, 2.95), (0.65, 2.5), (0.8, 2.5)]
        m.wall_cut(fig, [], 0.0, z, "frame")
        return m
    return b


def stair_painted():
    """a concrete stair flight up the hill with each step painted a different colour: 1.6 m up across the cell along
    +Z, iron handrails"""
    def b():
        m = Mesh()
        n = 9
        cols = ["accent", "accent2", "fabric", "tile", "trim", "wall"]
        for k in range(n):
            z0 = -HB + k * BAY / n
            y = 1.6 * (k + 1) / n
            m.box((-1.3, y - 0.18, z0), (1.3, y, z0 + BAY / n + 0.02), cols[k % len(cols)], skip=("y-",) + (("z-",) if k else ()))
        for x in (-1.25, 1.25):
            m.tube((x, 0.9, -HB), (x, 2.5, HB), 0.02, "metal", n=4)
            for z, y in ((-HB, 0.0), (0.0, 0.8), (HB, 1.6)):
                m.tube((x, y, z), (x, y + 0.9, z), 0.018, "metal", n=3)
        return m
    return b


def wall_tin_corrugated():
    """Valparaiso: a timber house bay clad in painted corrugated iron (ribs as shade-alternating strips), a sash window
    in a white frame"""
    def b():
        m = _wall(T, [_rect(-0.45, 1.0, 0.45, 2.3)])
        m.pane(-0.45, 1.0, 0.45, 2.3, -0.12)
        _ring(m, -0.45, 1.0, 0.45, 2.3, 0.08, 0.0, 0.04, "trim")
        _strip(m, (-0.45, 1.65, -0.1), (0.45, 1.65, -0.1), 0.04, (0, 0, 1), "trim")
        for k in range(30):
            x = -HB + 0.05 + k * 0.1
            if -0.6 < x < 0.6:
                for ya, yb in ((0.0, 0.88), (2.42, ST)):
                    _strip(m, (x, ya, 0.006), (x, yb, 0.006), 0.045, (0, 0, 1), "wall")
            else:
                _strip(m, (x, 0.0, 0.006), (x, ST, 0.006), 0.045, (0, 0, 1), "wall")
        return m
    return b


# ------------------------------------------------------------------ M'zab / Ghadames (r1_mzab_ghadames)
def edge_parapet_horn():
    """the whitewashed parapet with triangular horns at its ends and middle (Ghadames, M'zab)"""
    def b():
        m = Mesh()
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.95), (HB - 0.35, 0.45), (0.25, 0.45), (0.0, 0.85), (-0.25, 0.45), (-HB + 0.35, 0.45), (-HB, 0.95)]
        _flat_prism(m, p, -0.4, 0.0, "trim", open_edges=(0,))
        return m
    return b


def minaret_pyramid(part):
    """the M'zab minaret: a battered truncated pyramid, a storey a cell (base 3.0 m tapering 0.12 m a storey; stack
    _base then _shaft), little slit windows; the top with its four tall corner horns"""
    def b():
        m = Mesh()
        if part in ("base", "shaft"):
            a0 = 1.5 if part == "base" else 1.38
            _frustum(m, a0, a0 - 0.12, 0.0, ST, "wall")
            for k in range(4):
                sub = Mesh()
                sub.quad_facing((-0.06, 1.2, a0 - 0.05), (0.06, 1.2, a0 - 0.05), (0.06, 1.8, a0 - 0.065), (-0.06, 1.8, a0 - 0.065), (0, 0.05, 1), "frame", 0.4)
                _place(m, sub, 90 * k)
        else:
            a = 1.26
            _frustum(m, a, a - 0.08, 0.0, 1.2, "wall", top=True)
            for x in (-1.0, 1.0):
                for z in (-1.0, 1.0):
                    _frustum(m, 0.2, 0.02, 1.2, 2.7, "trim", cx=x, cz=z)
            for k in range(4):
                sub = Mesh()
                sub.quad_facing((-0.25, 0.4, a - 0.03), (0.25, 0.4, a - 0.03), (0.25, 0.9, a - 0.06), (-0.25, 0.9, a - 0.06), (0, 0.05, 1), "frame", 0.4)
                _place(m, sub, 90 * k)
        return m
    return b


def dukkana_bench():
    """the mud bench along a covered lane's wall (face overlay at ground), its edge rounded"""
    def b():
        m = Mesh()
        _flat_prism(m, [(0.0, 0.0), (0.5, 0.0), (0.5, 0.36), (0.44, 0.44), (0.0, 0.46)], -HB, HB, "wall", 0.92, open_edges=(0, 4))
        out = Mesh()
        out.add(m, lambda p: (p[2], p[1], p[0]))
        return _fix_mirror(out)
    return b


def well_pulley():
    """a well with its timber pulley frame: a round whitewashed kerb, two posts and a beam, the wheel, rope and bucket"""
    def b():
        m = Mesh()
        m.lathe([(0.8, 0.0), (0.78, 0.6), (0.45, 0.62), (0.43, 0.45)], "trim", n=10)
        m.cyl(0, 0, 0.44, 0.4, 0.5, "water", n=10, caps=True)
        for x in (-0.85, 0.85):
            m.box((x - 0.07, 0.0, -0.07), (x + 0.07, 2.2, 0.07), "frame", skip=("y-",))
        m.box((-1.0, 2.2, -0.08), (1.0, 2.35, 0.08), "frame")
        sub = Mesh()
        sub.cyl(0, 0, 0.22, -0.04, 0.04, "frame", n=8)
        m.add(sub, lambda p: (p[0], 2.0 + p[2], -p[1]))
        m.tube((0.0, 2.2, 0.0), (0.0, 2.0, 0.0), 0.02, "frame", n=3)
        m.tube((0.2, 2.0, 0.0), (0.2, 1.0, 0.0), 0.01, "fabric", n=3)
        m.lathe([(0.1, 0.8), (0.13, 1.0)], "metal", n=6, cx=0.2)
        return m
    return b


def wall_triangles():
    """the Ghadames door bay: a low door in a thick whitewashed wall, painted red and green triangles and diamonds
    round it"""
    def b():
        x0, x1, y1 = -0.5, 0.5, 2.0
        m = _wall(K, [_rect(x0, 0.0, x1, y1)])
        _door_leaf(m, x0, y1, x1, -0.3, "frame")
        z = 0.006
        for k in range(7):                                                   # a row of triangles over the door
            x = -0.98 + k * 0.28
            m.tri_facing((x, y1 + 0.15, z), (x + 0.28, y1 + 0.15, z), (x + 0.14, y1 + 0.45, z), (0, 0, 1), "accent" if k % 2 else "accent2")
        for s in (-1, 1):                                                    # diamonds up the jambs
            for j in range(4):
                cx, cy = s * 0.72, 0.4 + j * 0.42
                m.quad_facing((cx, cy - 0.16, z), (cx + 0.1, cy, z), (cx, cy + 0.16, z), (cx - 0.1, cy, z), (0, 0, 1), "accent2" if j % 2 else "accent")
        m.box((-1.0, y1 + 0.5, 0.0), (1.0, y1 + 0.56, z + 0.004), "accent", skip=("z-",))
        return m
    return b


def lightwell_shaft():
    """the light well in a covered lane's ceiling (a ceiling piece: y 0 = the ceiling): the slab with a square hole,
    sky light filling it, palm beams round it"""
    def b():
        m = Mesh()
        m.wall_cut(_rect(-HB, -HB, HB, HB), [_rect(-0.55, -0.55, 0.55, 0.55)], 0.0, 0.3, "wall", 0.85)
        out = Mesh()
        out.add(m, lambda p: (p[0], p[2], -p[1]))                          # the slab turned to lie flat (a rotation)
        out.quad_facing((-0.55, 0.28, -0.55), (0.55, 0.28, -0.55), (0.55, 0.28, 0.55), (-0.55, 0.28, 0.55), (0, -1, 0), "emissive")
        for z in (-0.75, 0.75):
            out.box((-HB, -0.12, z - 0.07), (HB, 0.0, z + 0.07), "frame", 0.8, skip=("y+", "x-", "x+"))
        return out
    return b


# ------------------------------------------------------------------ Nouvelle-France (r3_nouvelle_france)
def edge_firewall_gable():
    """the Quebec firewall gable: the stone end wall rising above a 55-degree roof, corbelled out at the eaves, a massive
    chimney stack at the apex with its pots (edge on the roof top; the roof runs along -Z behind it)"""
    def b():
        m = Mesh()
        h = HB * math.tan(math.radians(55))
        p = [(-1.75, 0.0), (1.75, 0.0), (1.75, 0.5), (1.5, 0.55), (0.5, 0.55 + (1.0) * math.tan(math.radians(55))),
             (-0.5, 0.55 + (1.0) * math.tan(math.radians(55))), (-1.5, 0.55), (-1.75, 0.5)]
        _flat_prism(m, p, -0.7, 0.0, "wall", open_edges=(0,))
        for x in (-1.6, 1.6):
            m.box((x - 0.17, 0.4, -0.75), (x + 0.17, 0.62, 0.06), "trim", 0.9)
        top = 0.55 + math.tan(math.radians(55))
        m.box((-0.55, top - 0.1, -0.75), (0.55, h + 1.6, 0.05), "wall", 0.95, skip=("y-",))
        m.box((-0.62, h + 1.6, -0.82), (0.62, h + 1.75, 0.12), "trim", 0.9)
        for x in (-0.3, 0.0, 0.3):
            m.cyl(x, -0.35, 0.09, h + 1.75, h + 2.1, "accent", n=6, caps=True)
        return m
    return b


def edge_cornice_pressed():
    """the Montreal plex cornice: a parapet with a deep pressed-metal cornice on brackets, dentils, a raised panel with
    its date in the middle"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -0.35), (HB, 0.85, 0.0), "wall", skip=("y-", "x-", "x+"))
        m.box((-HB, 0.3, 0.0), (HB, 0.62, 0.35), "accent", skip=("z-", "x-", "x+"))
        m.box((-HB, 0.62, -0.05), (HB, 0.72, 0.42), "accent", 0.9, skip=("x-", "x+"))
        _beads(m, -HB, HB, 0.32, 0.4, 0.35, 0.39, 16, "accent", 0.8)
        for x in (-1.35, -0.45, 0.45, 1.35):
            _corbel(m, x, 0.3, 0.32, 0.45, 0.1, "accent", 0.85)
        _flat_prism(m, [(-0.6, 0.72), (0.6, 0.72), (0.6, 1.05), (0.0, 1.25), (-0.6, 1.05)], 0.0, 0.3, "accent", 0.95, open_edges=(0,))
        m.box((-0.3, 0.8, 0.3), (0.3, 1.0, 0.32), "accent2", skip=("z-",))
        return m
    return b


def stair_plex_outdoor():
    """Montreal's twisting outdoor iron stair: from the pavement (+Z side of the cell) a three-quarter turn up to a
    landing at the 2nd storey door (3.2 m, against the -Z face), treads, an outer stringer and railing"""
    def b():
        m = Mesh()
        n, r0, r1 = 16, 0.15, 1.25
        a0, a1 = math.pi / 2, math.pi / 2 + 1.5 * math.pi
        cx, cz = 0.0, 0.1
        for k in range(n):
            t0, t1 = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
            y = ST * 0.9 * (k + 1) / n
            p = [(cx + r0 * math.cos(t0), cz + r0 * math.sin(t0)), (cx + r1 * math.cos(t0), cz + r1 * math.sin(t0)),
                 (cx + r1 * math.cos(t1), cz + r1 * math.sin(t1)), (cx + r0 * math.cos(t1), cz + r0 * math.sin(t1))]
            m.prism_xz(p, y - 0.05, y, "metal", 0.85)
        m.box((-1.4, ST - 0.06, -HB), (1.4, ST, -0.6), "metal", 0.85)
        m.cyl(cx, cz, 0.08, 0.0, ST + 1.0, "metal", n=6)
        prev = None
        for k in range(n + 1):
            t = a0 + (a1 - a0) * k / n
            y = ST * 0.9 * k / n
            p = (cx + r1 * math.cos(t), y + 0.95, cz + r1 * math.sin(t))
            if prev:
                m.tube(prev, p, 0.022, "metal", n=3)
            if k % 4 == 0:
                m.tube((p[0], y, p[2]), p, 0.015, "metal", n=3)
            prev = p
        m.tube((-1.4, ST + 0.95, -0.6), (1.4, ST + 0.95, -0.6), 0.022, "metal", n=3)
        return m
    return b


def ov_snow_cap():
    """snow lying along a roof edge or sill: a soft white ridge 3 m long (edge overlay; the trim slot, brightened)"""
    def b():
        m = Mesh()
        prof = [(0.0, 0.0), (0.38, 0.0), (0.4, 0.06), (0.3, 0.13), (0.12, 0.16), (0.0, 0.14)]
        sub = Mesh()
        _flat_prism(sub, prof, -HB, HB, "trim", 1.15, open_edges=(0,))       # (trim, brightened: white in the snowy families)
        m.add(sub, lambda p: (-p[2], p[1], p[0] - 0.3))
        return m
    return b


def wall_window_casement():
    """a small many-paned casement in thick rubble stone, dressed quoin surround, interior shutters folded in the
    reveal"""
    def b():
        x0, y0, x1, y1 = -0.4, 1.1, 0.4, 2.2
        m = _wall(K, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.3)
        for k in range(1, 3):
            _strip(m, (x0 + 0.8 * k / 3, y0, -0.28), (x0 + 0.8 * k / 3, y1, -0.28), 0.025, (0, 0, 1), "trim")
        for k in range(1, 4):
            _strip(m, (x0, y0 + 1.1 * k / 4, -0.275), (x1, y0 + 1.1 * k / 4, -0.275), 0.025, (0, 0, 1), "trim")
        for xa in (-0.395, 0.365):                                          # interior shutters folded to the jambs
            m.box((xa, y0 + 0.005, -0.5), (xa + 0.03, y1 - 0.005, -0.32), "accent", 0.9)
        for j in range(4):                                                  # quoin blocks
            y = y0 - 0.15 + j * 0.36
            for s in (-1, 1):
                w = 0.22 if j % 2 else 0.32
                xa = s * 0.4
                m.box((min(xa, xa + s * w), y, 0.0), (max(xa, xa + s * w), y + 0.32, 0.03), "trim", 0.9 + 0.05 * j % 2, skip=("z-",))
        m.box((x0 - 0.1, y1 + 0.05, 0.0), (x1 + 0.1, y1 + 0.3, 0.03), "trim", skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ Taipei (r2_taipei_tiepi)
def ov_tiepi_house():
    """the tiepi: a corrugated-iron house on a roof (roof overlay on a cell): ribbed walls, a pent roof, a door, a grilled
    window, potted plants"""
    def b():
        m = Mesh()
        w, d, h = 1.35, 1.3, 2.5
        m.box((-w, 0.0, -d), (w, h, d), "metal", skip=("y-", "y+"))
        for s in (-1, 1):
            for k in range(13):
                x = -w + 0.1 + k * 0.2
                _strip(m, (x, 0.0, s * (d + 0.005)), (x, h - 0.1 if s > 0 else h + 0.3, s * (d + 0.005)), 0.06, (0, 0, s), "metal")
        m.quad_facing((-w - 0.2, h + 0.35, -d - 0.2), (w + 0.2, h + 0.35, -d - 0.2), (w + 0.2, h - 0.05, d + 0.3), (-w - 0.2, h - 0.05, d + 0.3), (0, 1, 0), "roof")
        m.quad_facing((-w - 0.2, h + 0.32, -d - 0.2), (w + 0.2, h + 0.32, -d - 0.2), (w + 0.2, h - 0.08, d + 0.3), (-w - 0.2, h - 0.08, d + 0.3), (0, -1, 0), "metal", 0.6)
        for s in (-1, 1):
            m.tri_facing((s * w, h, -d), (s * w, h, d), (s * w, h + 0.35, -d), (s, 0, 0), "metal", 0.9)
        m.box((-1.0, 0.0, d + 0.01), (-0.3, 2.0, d + 0.05), "frame", 0.8)
        m.pane(0.2, 1.0, 1.0, 1.8, d + 0.012)
        _ring(m, 0.2, 1.0, 1.0, 1.8, 0.04, d + 0.01, d + 0.04, "frame")
        for k in range(1, 5):
            _strip(m, (0.2 + 0.8 * k / 5, 1.0, d + 0.07), (0.2 + 0.8 * k / 5, 1.8, d + 0.07), 0.02, (0, 0, 1), "metal")
        for x in (0.3, 0.7, 1.1):
            m.cyl(x, d + 0.35, 0.14, 0.0, 0.3, "fabric", n=6)
            m.cyl(x, d + 0.35, 0.2, 0.3, 0.6, "plant", n=5, r1=0.05)
        return m
    return b


def wall_qilou():
    """the qilou arcade bay: a square column at the street edge (the bay's right end, shared down the street), the
    arcade 2.5 m deep behind it, a shopfront at its back with a lit sign, a fluorescent tube in its ceiling (the bay
    uses the cell's front 2.5 m)"""
    def b():
        m = Mesh()
        dz = -2.5
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.2, 0.0, 1.2, 2.55)], dz - T, dz, "wall", reveal_slot="trim")
        m.pane(-1.2, 0.0, 1.2, 2.2, dz - 0.1)
        _lightbox(m, -1.2, 2.25, 1.2, 2.55, dz - 0.1, dz + 0.05, nchar=4)
        m.box((-HB, ST - 0.35, dz), (HB, ST, 0.0), "wall", 0.9, skip=("z-", "x-", "x+", "y+"))
        m.box((-0.8, ST - 0.38, -1.3), (0.8, ST - 0.35, -1.2), "emissive")
        m.box((1.1, 0.0, -0.4), (1.5, ST - 0.35, 0.0), "wall", skip=("y-", "y+"))
        m.box((1.06, 0.0, -0.44), (1.54, 0.35, 0.04), "trim", 0.85, skip=("y-",))
        m.box((-HB, ST - 0.45, -0.06), (HB, ST, 0.04), "trim", 0.9, skip=("x-", "x+"))
        return m
    return b


def wall_tile():
    """a Taipei bay clad in small ceramic tiles (grout lines), an aluminium window inside an iron security cage"""
    def b():
        x0, y0, x1, y1 = -0.8, 1.0, 0.8, 2.2
        m = _wall(T, [_rect(x0, y0, x1, y1)])
        m.pane(x0, y0, x1, y1, -0.12)
        _strip(m, (0.0, y0, -0.1), (0.0, y1, -0.1), 0.04, (0, 0, 1), "metal")
        for k in range(1, 16):
            y = k * 0.2
            if y0 - 0.05 < y < y1 + 0.05:
                for xa, xb in ((-HB, x0), (x1, HB)):
                    _strip(m, (xa, y, 0.004), (xb, y, 0.004), 0.012, (0, 0, 1), "trim")
            else:
                _strip(m, (-HB, y, 0.004), (HB, y, 0.004), 0.012, (0, 0, 1), "trim")
        d = 0.35
        for k in range(9):
            x = x0 - 0.1 + (x1 - x0 + 0.2) * k / 8
            _strip(m, (x, y0 - 0.1, d), (x, y1 + 0.1, d), 0.02, (0, 0, 1), "metal")
        for y in (y0 - 0.1, y1 + 0.1):
            m.box((x0 - 0.12, y - 0.02, 0.0), (x1 + 0.12, y + 0.02, d + 0.02), "metal", 0.85, skip=("z-",))
        return m
    return b


def ov_water_tower_steel():
    """the stainless steel water tower on four braced legs, a ladder up its side (roof)"""
    def b():
        m = Mesh()
        for x in (-0.55, 0.55):
            for z in (-0.55, 0.55):
                m.box((x - 0.04, 0.0, z - 0.04), (x + 0.04, 1.3, z + 0.04), "metal", 0.8, skip=("y-",))
        for z in (-0.55, 0.55):
            m.tube((-0.55, 0.1, z), (0.55, 1.2, z), 0.015, "metal", n=3)
            m.tube((0.55, 0.1, z), (-0.55, 1.2, z), 0.015, "metal", n=3)
        m.cyl(0, 0, 0.75, 1.3, 1.36, "metal", n=10)
        m.lathe([(0.72, 1.36), (0.72, 2.9), (0.4, 3.15), (0.0, 3.2)], "metal", n=10, shade=1.1)
        for k in range(3):
            _strip(m, (-0.72, 1.6 + k * 0.5, 0.0), (0.0, 1.6 + k * 0.5, -0.725), 0.03, (-1, 0, -1), "metal")
        for x in (0.68, 0.84):
            m.tube((x, 0.0, 0.25), (x, 3.0, 0.25), 0.012, "metal", n=3)
        for k in range(8):
            m.tube((0.68, 0.3 + k * 0.35, 0.25), (0.84, 0.3 + k * 0.35, 0.25), 0.01, "metal", n=3)
        return m
    return b


# ------------------------------------------------------------------ LITE marks for the budget pass
def wall_roshan_lite(t):
    """the roshan at <= 250 tris (for the budget pass; the full wall_roshan_* stays for near/hero use): the painted oriel
    on two brackets, a carved apron, one lattice band across the front, plain sides, louvres, the crest"""
    def b():
        m = _wall(t, [_rect(-0.8, 0.3, 0.8, 2.9)], reveal="accent")
        d, x0, x1 = 0.85, -0.95, 0.95
        m.box((x0, 0.2, 0.0), (x1, 0.95, d), "accent", skip=("z-",))
        for x in (-0.6, 0.6):
            m.tube((x, -0.45, 0.02), (x, 0.2, d - 0.1), 0.06, "accent", n=4)
        for k in range(4):
            x = x0 + 0.12 + k * 0.435
            m.quad_facing((x, 0.4, d + 0.005), (x + 0.33, 0.4, d + 0.005), (x + 0.33, 0.82, d + 0.005), (x, 0.82, d + 0.005), (0, 0, 1), "screen")
        m.pane(x0 + 0.06, 0.95, x1 - 0.06, 2.25, d - 0.06)
        _lattice(m, x0, 0.95, x1, 2.25, d - 0.05, d, 9, 8)
        for side in (x0, x1 - 0.06):
            m.box((side, 0.94, 0.0), (side + 0.06, 2.76, d - 0.05), "accent", 0.85, skip=("z-", "y-"))
        for k in range(3):
            _strip(m, (x0, 2.33 + k * 0.15, d - 0.02), (x1, 2.33 + k * 0.15, d - 0.02), 0.11, (0, 0.35, 1), "screen")
        m.box((x0 - 0.1, 2.75, 0.0), (x1 + 0.1, 2.95, d + 0.12), "accent", skip=("z-",))
        _crest(m, x0 - 0.1, x1 + 0.1, 2.95, 0.16, d + 0.12, 8, "accent")
        return m
    return b


def wall_jetty_lite():
    """the Ottoman jetty at <= 250 tris: the storey 0.9 m out, two sash windows and a shallow cumba box, timber bands,
    two angled struts"""
    def b():
        z = 0.9
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.25, 0.85, -0.8, 2.45), _rect(0.8, 0.85, 1.25, 2.45), _rect(-0.6, 0.6, 0.6, 2.7)], z - T, z, "wall", reveal_slot="frame")
        for x0 in (-1.25, 0.8):
            m.pane(x0, 0.85, x0 + 0.45, 2.45, z - 0.12)
            _strip(m, (x0, 1.65, z - 0.1), (x0 + 0.45, 1.65, z - 0.1), 0.04, (0, 0, 1), "frame")
        m.box((-0.595, 0.605, z - T), (0.595, 2.695, z + 0.46), "frame", 0.85, skip=("z+", "z-"))
        m.wall_cut(_rect(-0.6, 0.6, 0.6, 2.7), [_rect(-0.5, 1.2, 0.5, 2.5)], z + 0.45, z + 0.5, "wall", reveal_slot="frame")
        m.pane(-0.5, 1.2, 0.5, 2.5, z + 0.47)
        for y in (0.7, ST - 0.1):
            m.box((-HB, y, z), (HB, y + 0.08, z + 0.04), "frame", 0.85, skip=("z-",))
        m.box((-HB, -0.18, -T), (HB, 0.0, z), "frame", 0.8, skip=("z-",))
        for x in (-1.1, 1.1):
            m.tube((x, -1.0, 0.02), (x, -0.18, z - 0.1), 0.06, "frame", n=4)
        return m
    return b


def edge_parapet_jali_lite():
    """the jali parapet at <= 150 tris: a base, piers, a coping, and in each of four panels a screen with a diagonal
    lattice cut across it (flat strips)"""
    def b():
        m = Mesh()
        t = 0.3
        m.box((-HB, 0.0, -t), (HB, 0.3, 0.0), "wall", skip=("y-", "x-", "x+"))
        m.box((-HB, 0.9, -t - 0.03), (HB, 1.0, 0.03), "trim", skip=("x-", "x+"))
        for x in (-HB, -0.75, 0.0, 0.75):
            xa = x + (0.0 if x == -HB else -0.04)
            m.box((xa, 0.29, -t), (xa + 0.08, 0.91, 0.0), "wall", 0.95, skip=("y-", "y+"))
        for k in range(4):
            x0 = -HB + 0.08 + k * 0.75 - (0.0 if k == 0 else 0.04)
            x1 = x0 + 0.67 - (0.0 if k in (0, 3) else -0.0)
            m.quad_facing((x0, 0.3, -t / 2), (x1, 0.3, -t / 2), (x1, 0.9, -t / 2), (x0, 0.9, -t / 2), (0, 0, 1), "frame", 0.35)
            _diag(m, x0, 0.3, x1, 0.9, -t / 2 + 0.01, 0.2, 0.05, "trim")
        return m
    return b


# ------------------------------------------------------------------ register
CR = ["creole_colonial"]
PIECES["wall_window_medio_punto_k"] = _w("wall", wall_window_medio_punto(), CR, notes="CREOLE MARK: tall window, turned bars, shutters, lit stained lunette")
PIECES["wall_balcony_covered_k"] = _w("wall", wall_balcony_covered(), CR, lod1="keep", notes="CREOLE MARK: Cartagena covered timber balcony")
PIECES["wall_door_carriage_k"] = _w("wall", wall_door_carriage(), CR + ["iberian_white"], notes="zaguan carriage door, inset door, keystone")
for p in ("base", "belfry", "cupola"):
    PIECES[f"bell_tower_baroque_{p}"] = _w("cell", bell_tower_baroque(p), CR + ["andean_neo", "latin_hillside"], lod1="keep", kind="tower",
                                           notes=f"baroque bell tower {p} (stack: base xN, belfry, cupola)")
PIECES["kiosco_gazebo"] = _w("cell", kiosco_gazebo(), CR + ["latin_hillside", "iberian_white"], lod1="keep", notes="plaza bandstand")
PIECES["edge_parapet_urns_k"] = _w("edge", edge_parapet_urns(), CR + ["karachi"], lod1="keep", notes="azotea balustrade with urns")
HK = ["hk_neon_canyon"]
PIECES["ov_sign_arm_big"] = _w("wall", ov_sign_arm_big(), HK + ["kowloon_walled"], lod1="keep", collide=False, kind="overlay",
                               notes="HK MARK: 2-storey neon sign on a steel arm, faces +-X (stack for 4)")
PIECES["wall_verandah_t"] = _w("wall", wall_verandah(), HK + ["straits_shophouse"], lod1="keep", notes="tong lau verandah storey: 2 m slab on street-edge columns")
PIECES["wall_mosaic_t"] = _w("wall", wall_mosaic(), HK, notes="1960s mosaic tile bay, window pair")
PIECES["wall_window_casement_pair_t"] = _w("wall", wall_window_casement_pair(), HK, notes="steel casements in pairs (accent = green), one ajar")
PIECES["ov_roller_shutter"] = _w("wall", ov_roller_shutter(), HK + ["taipei_tiepi", "karachi"], lod1="drop", kind="overlay", notes="roller shutter half down")
IB = ["iberian_white"]
PIECES["wall_reja_box_k"] = _w("wall", wall_reja_box(), IB + CR, notes="IBERIAN MARK: box reja, pot shelf, painted surround")
PIECES["wall_door_studded_k"] = _w("wall", wall_door_studded(), IB + ["yemeni_tower", "omani_oasis"], notes="studded door, stone surround")
PIECES["band_zocalo"] = _w("wall", band_zocalo(), IB + CR, lod1="drop", collide=False, kind="overlay", notes="painted base band 0.8 m (accent)")
PIECES["ov_blue_pots"] = _w("wall", ov_blue_pots(), IB, lod1="drop", collide=False, kind="overlay", notes="blue pots with geraniums on a wall")
for p in ("shaft", "belfry", "top"):
    PIECES[f"tower_mudejar_{p}"] = _w("cell", tower_mudejar(p), IB, lod1="keep", kind="tower", notes=f"IBERIAN MARK: Mudejar tower {p} (stack shaft xN, belfry, top)")
PIECES["ov_toldo"] = _w("cell", ov_toldo(), IB + ["levantine_courtyard"], lod1="drop", collide=False, kind="overlay", notes="canvas awnings across a lane at 4.5 m (along X)")
LA = ["latin_hillside"]
PIECES["ov_tank_round_blue"] = _w("cell", ov_tank_round_blue(), LA + ["karachi"], lod1="drop", kind="overlay", notes="round blue fibreglass tank (accent = blue)")
PIECES["wall_brick_raw_t"] = _w("wall", wall_brick_raw(), LA + ["karachi"], notes="hollow brick infill in a concrete frame (tile slot = brick)")
PIECES["wall_mural_t"] = _w("wall", wall_mural(), LA, notes="mural-painted blank bay")
PIECES["stair_painted"] = _w("cell", stair_painted(), LA, collide="ramp", kind="stair", notes="1.6 m up along +Z, each step a colour")
PIECES["wall_tin_corrugated_t"] = _w("wall", wall_tin_corrugated(), LA, notes="Valparaiso corrugated iron cladding, sash window")
MZ = ["mzab_ghadames"]
PIECES["edge_parapet_horn_k"] = _w("edge", edge_parapet_horn(), MZ + ["omani_oasis"], lod1="keep", notes="MZAB MARK: whitewashed parapet with triangular horns")
for p in ("base", "shaft", "top"):
    PIECES[f"minaret_pyramid_{p}"] = _w("cell", minaret_pyramid(p), MZ, lod1="keep", kind="tower", notes=f"MZAB MARK: battered pyramid minaret {p} (base, shaft xN, top)")
PIECES["dukkana_bench"] = _w("wall", dukkana_bench(), MZ + ["saharan_kasbah", "omani_oasis"], lod1="drop", kind="overlay", notes="mud bench along a wall")
PIECES["well_pulley"] = _w("cell", well_pulley(), MZ + ["saharan_kasbah", "omani_oasis", "persian_desert"], lod1="keep", notes="well with pulley frame")
PIECES["wall_triangles_k"] = _w("wall", wall_triangles(), MZ, notes="MZAB MARK: Ghadames door, red/green triangles and diamonds")
PIECES["lightwell_shaft"] = _w("cell", lightwell_shaft(), MZ + ["maghrebi_medina"], lod1="keep", kind="ceiling", notes="ceiling piece: light-well hole, lit")
NF = ["nouvelle_france"]
PIECES["edge_firewall_gable_k"] = _w("edge", edge_firewall_gable(), NF + ["scots_lands"], lod1="keep", kind="crown", notes="NF MARK: Quebec firewall gable + chimney stack")
PIECES["edge_cornice_pressed"] = _w("edge", edge_cornice_pressed(), NF, lod1="keep", notes="plex pressed-metal cornice, brackets, date panel")
PIECES["stair_plex_outdoor"] = _w("cell", stair_plex_outdoor(), NF, lod1="keep", kind="stair", notes="NF MARK: twisting iron stair to the 2nd storey (-Z face)")
PIECES["ov_snow_cap"] = _w("edge", ov_snow_cap(), NF + ["scots_lands", "tibetan_lhasa"], lod1="drop", collide=False, kind="overlay", notes="snow on a roof edge / sill")
PIECES["wall_window_casement_k"] = _w("wall", wall_window_casement(), NF + ["scots_lands"], notes="many-paned casement in rubble stone, quoins")
TP = ["taipei_tiepi"]
PIECES["ov_tiepi_house"] = _w("cell", ov_tiepi_house(), TP + ["kowloon_walled", "manila_estero"], lod1="keep", kind="crown", notes="TAIPEI MARK: corrugated iron rooftop house")
PIECES["wall_qilou_t"] = _w("wall", wall_qilou(), TP + ["straits_shophouse"], lod1="keep", notes="TAIPEI MARK: qilou arcade bay (uses the cell's front 2.5 m)")
PIECES["wall_tile_t"] = _w("wall", wall_tile(), TP, notes="small-tile cladding, window in an iron cage")
PIECES["ov_water_tower_steel"] = _w("cell", ov_water_tower_steel(), TP, lod1="keep", kind="overlay", notes="stainless water tower on legs")
PIECES["wall_roshan_lite_t"] = _w("wall", wall_roshan_lite(T), ["hejazi_roshan", "cairene_mamluk"], lod1="keep", notes="roshan <= 250 tris (budget pass)")
PIECES["wall_roshan_lite_k"] = _w("wall", wall_roshan_lite(K), ["hejazi_roshan", "cairene_mamluk"], lod1="keep", notes="roshan <= 250 tris (budget pass)")
PIECES["wall_jetty_lite_t"] = _w("wall", wall_jetty_lite(), ["ottoman_timber", "levantine_courtyard"], lod1="keep", notes="jetty <= 250 tris (budget pass)")
PIECES["edge_parapet_jali_k"] = _w("edge", edge_parapet_jali_lite(), ["rajput_sandstone", "mughal_walled"], lod1="keep", notes="jali parapet (cheap lattice)")

# palette touches for the new families' slots
for civ, acc in (("mzab_ghadames", ("#b0322a", "#2f7a4a")), ("iberian_white", ("#2a55a8", "#d8a03a")), ("creole_colonial", ("#3f7a5a", "#d8a03a")),
                 ("hk_neon_canyon", ("#3f6a4a", "#e8e2d2")), ("taipei_tiepi", ("#3a6a8a", "#e8e2d2"))):
    for v in PALETTES.get(civ, []):
        v["accent"], v["accent2"] = acc
for v in PALETTES.get("iberian_white", []):
    v["tile"] = "#3f7a5a"                                           # green glaze (Mudejar towers, court tiles)
for v in PALETTES.get("latin_hillside", []):
    v["tile"] = "#b2603e"
for v in PALETTES.get("nouvelle_france", []):
    v["accent2"] = "#f4f6f8"


# ------------------------------------------------------------------ runtime_requests.md 2026-10-15 #1: no near-black slot over a bay
# The medina's roller shutters (wall_shopfront_*: metal slot) read as a black hole in the toon light: paint them
# (green / blue / timber / teal per variant), and lift every family's near-black metal / frame / screen to a dark but
# readable tone (average sRGB channel >= 64 for metal, >= 48 for frame and screen).
for v, c in zip(PALETTES.get("maghrebi_medina", []), ("#4f6b4a", "#2d5f8a", "#6b5236", "#3f6f6a")):
    v["metal"] = c


def _lift(h, floor, toward=(0x8a, 0x86, 0x80)):
    r, g, b_ = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    avg = (r + g + b_) / 3
    if avg >= floor:
        return h
    t = (floor - avg) / max(1.0, sum(toward) / 3 - avg)
    return "#%02x%02x%02x" % tuple(round(c + (w - c) * t) for c, w in zip((r, g, b_), toward))


for vs in PALETTES.values():
    for v in vs:
        for slot, floor in (("metal", 64), ("frame", 48), ("screen", 48)):
            if slot in v:
                v[slot] = _lift(v[slot], floor)
