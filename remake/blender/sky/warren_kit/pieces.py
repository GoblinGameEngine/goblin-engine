"""pieces.py -- the warren kit v1 (research/sky_islands/warrens/r4_design.md section 4): shared pieces for the sky
islands' warren cities, plus the first two civilizations' mark pieces (maghrebi_medina with tower houses;
kowloon_walled).  The user, 2026-10-15: new buildings only by ADDING PIECES to the shared parts library; diversity
from common pieces (proportion, colour, rhythm, combination) plus a few civilization marks.

Frames (geom.py): WALL bays x -1.5..1.5, y 0..3.2, +Z out of the cell (the body inside, z -t..0); EDGE pieces the same
but standing on a roof (y 0 = roof top); CORNER pieces on a cell's vertical edge (the cell in -X/-Z); CELL pieces centred
on the cell, y 0 = the walking surface (or the roof top).  A cell is 3 m x 3 m x 3.2 m.

Each entry: id -> dict(group, kind, civs, build, lod1, collide, span, notes).  `build` returns a geom.Mesh.
lod1: "box" (the runtime draws a plain face/slab instead), "keep" (silhouette: keep at LOD1), "drop" (gone at LOD1).
collide: True (the piece's own triangles), False, or "ramp" (stairs: a sloped plane from the piece's ramp points).
"""
import math

from geom import Mesh, arch, move, rot_y

BAY = 3.0
ST = 3.2
T = 0.25            # thin wall (concrete, timber frame)
K = 0.6             # thick wall (rubble, mud brick, stone)
HB = BAY / 2


# ------------------------------------------------------------------ helpers
def _bay():
    return [(-HB, 0.0), (HB, 0.0), (HB, ST), (-HB, ST)]


def _wall(t, openings=(), reveal="trim"):
    m = Mesh()
    m.wall_cut(_bay(), list(openings), -t, 0.0, "wall", reveal_slot=reveal)
    return m


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _window(m, t, x0, y0, x1, y1, sill=True, frame=True, depth=None):
    """glass set back in an opening (already cut), a frame round it, a sill under it"""
    g = -(depth if depth is not None else min(t * 0.55, 0.3))
    if frame:
        f = 0.06
        m.box((x0, y0, g - 0.03), (x0 + f, y1, g + 0.03), "frame")
        m.box((x1 - f, y0, g - 0.03), (x1, y1, g + 0.03), "frame")
        m.box((x0 + f, y0, g - 0.03), (x1 - f, y0 + f, g + 0.03), "frame")
        m.box((x0 + f, y1 - f, g - 0.03), (x1 - f, y1, g + 0.03), "frame")
        if x1 - x0 > 0.9:
            mx = (x0 + x1) / 2
            m.box((mx - 0.025, y0 + f, g - 0.025), (mx + 0.025, y1 - f, g + 0.025), "frame")
        m.pane(x0 + f, y0 + f, x1 - f, y1 - f, g)
    else:
        m.pane(x0, y0, x1, y1, g)
    if sill:
        m.box((x0 - 0.08, y0 - 0.06, -0.02), (x1 + 0.08, y0, 0.07), "trim")


def _lattice(m, x0, y0, x1, y1, z0, z1, nx, ny, slot="screen", bar=0.035):
    """a screen of crossing bars in a frame (mashrabiya, jali, grille) -- cheap: the frame open at the back, the bars
    flat strips facing out (+Z), the cross bars a few mm proud of the uprights"""
    for lo, hi in (((x0, y0, z0), (x0 + 0.06, y1, z1)), ((x1 - 0.06, y0, z0), (x1, y1, z1)),
                   ((x0 + 0.06, y0, z0), (x1 - 0.06, y0 + 0.06, z1)), ((x0 + 0.06, y1 - 0.06, z0), (x1 - 0.06, y1, z1))):
        m.box(lo, hi, "frame", skip=("z-",))
    zc = (z0 + z1) / 2
    for i in range(1, nx):
        x = x0 + (x1 - x0) * i / nx
        _strip(m, (x, y0 + 0.06, zc), (x, y1 - 0.06, zc), bar, (0, 0, 1), slot)
    for j in range(1, ny):
        y = y0 + (y1 - y0) * j / ny
        _strip(m, (x0 + 0.06, y, zc + 0.004), (x1 - 0.06, y, zc + 0.004), bar, (0, 0, 1), slot)


def _bars(m, x0, y0, x1, y1, z, n, slot="metal", r=0.012):
    for i in range(1, n):                                  # (not at the ends: the posts stand there)
        x = x0 + (x1 - x0) * i / n
        m.tube((x, y0, z), (x, y1, z), r, slot, n=4)


def _rail(m, x0, x1, y, z, slot="metal", r=0.025):
    m.tube((x0, y, z), (x1, y, z), r, slot, n=5)


def _grow(outline, d):
    from shapely.geometry import Polygon
    g = Polygon(outline).buffer(d, join_style=2 if d > 0 else 1)
    return [tuple(p) for p in list(g.exterior.coords)[:-1]]


# ------------------------------------------------------------------ walls
def wall_plain(t):
    return lambda: _wall(t)


def wall_window(t, w, h, y0):
    def b():
        o = _rect(-w / 2, y0, w / 2, y0 + h)
        m = _wall(t, [o])
        _window(m, t, -w / 2, y0, w / 2, y0 + h)
        return m
    return b


def wall_window_pair(t):
    def b():
        a = _rect(-1.15, 0.9, -0.35, 2.3)
        c = _rect(0.35, 0.9, 1.15, 2.3)
        m = _wall(t, [a, c])
        _window(m, t, -1.15, 0.9, -0.35, 2.3)
        _window(m, t, 0.35, 0.9, 1.15, 2.3)
        return m
    return b


def wall_door(t):
    def b():
        m = _wall(t, [_rect(-0.5, 0.0, 0.5, 2.2)])
        g = -min(t * 0.6, 0.35)
        m.box((-0.5, 0.02, g - 0.05), (0.5, 2.2, g), "frame")                  # the leaf, set back
        m.box((-0.42, 0.9, g), (-0.34, 1.05, g + 0.04), "metal")               # a handle plate
        m.box((-0.62, 2.2, -0.02), (0.62, 2.34, 0.08), "trim")                 # lintel
        return m
    return b


def wall_door_portal():
    """MEDINA MARK: the horseshoe-arched studded cedar door in a zellige surround (thick walls only)"""
    def b():
        o = arch("horseshoe", 1.3, 2.7, 0.0, n=8)
        m = _wall(K, [o])
        # the cedar leaves, studded
        g = -0.38
        m.wall_cut(o, [], g - 0.08, g, "frame")
        for i in range(3):
            for j in range(5):
                m.cbox(-0.36 + i * 0.36, 0.3 + j * 0.42, g + 0.005, 0.06, 0.06, 0.03, "metal")
        # the tiled surround (a thin band round the arch on the face) and a carved stucco tympanum band
        ring_out = _grow(o, 0.28)
        m.wall_cut(ring_out, [o], 0.0, 0.035, "tile", reveal_slot="tile")
        m.box((-1.0, 3.0, -0.02), (1.0, 3.12, 0.12), "trim")
        return m
    return b


def wall_shopfront(t, kind):
    def b():
        if kind == "a":                                        # rolling shutter, half down
            m = _wall(t, [_rect(-1.3, 0.0, 1.3, 2.6)])
            m.box((-1.38, 2.6, -0.05), (1.38, 2.95, 0.28), "metal")             # the shutter box
            m.wall_cut(_rect(-1.25, 1.3, 1.25, 2.6), [], -0.05, -0.02, "metal")  # the shutter
            for k in range(8):
                y = 1.35 + k * 0.155
                m.box((-1.25, y, -0.02), (1.25, y + 0.03, 0.0), "metal")
            m.pane(-1.25, 0.05, 1.25, 1.3, -min(t * 0.6, 0.3))
            m.box((-1.3, 0.0, -0.02), (1.3, 0.12, 0.25), "trim")                 # a step
        else:                                                  # an open front under an awning
            m = _wall(t, [_rect(-1.2, 0.0, 1.2, 2.4)])
            m.pane(-1.2, 0.05, 1.2, 2.4, -min(t * 0.6, 0.3))
            m.box((-1.2, 0.0, -0.3), (1.2, 0.85, -0.1), "frame")                  # a counter in the opening
            # the awning: a sloping cloth with a valance
            m.quad_facing((-1.4, 2.65, 0.02), (1.4, 2.65, 0.02), (1.4, 2.25, 1.1), (-1.4, 2.25, 1.1), (0, 1, 0.3), "fabric")
            m.quad_facing((-1.4, 2.65, 0.0), (1.4, 2.65, 0.0), (1.4, 2.25, 1.08), (-1.4, 2.25, 1.08), (0, -1, -0.3), "fabric", 0.8)
            m.box((-1.4, 2.05, 1.08), (1.4, 2.25, 1.12), "fabric")
            m.tube((-1.35, 2.3, 1.08), (-1.35, 2.65, 0.0), 0.02, "metal")
            m.tube((1.35, 2.3, 1.08), (1.35, 2.65, 0.0), 0.02, "metal")
        return m
    return b


def wall_screen(t):
    """a window behind a timber lattice screen (mashrabiya / jali / shoji -- the palette and screen slot say which)"""
    def b():
        m = _wall(t, [_rect(-0.65, 0.8, 0.65, 2.5)])
        _window(m, t, -0.65, 0.8, 0.65, 2.5, sill=False)
        _lattice(m, -0.65, 0.8, 0.65, 2.5, -0.06, 0.0, 7, 9)
        m.box((-0.8, 0.7, -0.02), (0.8, 0.8, 0.1), "trim")
        return m
    return b


def _strip(m, a, b, w, normal, slot="metal"):
    """a thin flat bar between two points, one quad facing `normal` (cheap welded bars; seen from the street)"""
    a, b = list(a), list(b)
    d = [b[i] - a[i] for i in range(3)]
    n = list(normal)
    # the bar's width direction: perpendicular to its length within the plane facing `normal`
    side = [d[1] * n[2] - d[2] * n[1], d[2] * n[0] - d[0] * n[2], d[0] * n[1] - d[1] * n[0]]
    ln = math.sqrt(sum(v * v for v in side)) or 1.0
    side = [v / ln * w / 2 for v in side]
    p0 = [a[i] - side[i] for i in range(3)]
    p1 = [a[i] + side[i] for i in range(3)]
    p2 = [b[i] + side[i] for i in range(3)]
    p3 = [b[i] - side[i] for i in range(3)]
    m.quad_facing(p0, p1, p2, p3, normal, slot)


def _cheap_window(t, x0, y0, x1, y1, sill=True):
    """one wall with one rectangular hole, a set-back pane and (unless something else is the sill) a sill: ~40 tris"""
    m = _wall(t, [_rect(x0, y0, x1, y1)])
    m.pane(x0, y0, x1, y1, -min(t * 0.55, 0.3))
    if sill:
        m.box((x0 - 0.06, y0 - 0.05, -0.02), (x1 + 0.06, y0, 0.06), "trim", skip=("z-", "y-"))
    return m


def wall_balcony_cage(t):
    """KOWLOON: a window with a welded mesh cage 0.8 m out (the 'cage home' balcony) -- bars as flat strips (budget)"""
    def b():
        m = _cheap_window(t, -0.7, 0.8, 0.7, 2.3, sill=False)          # (the cage floor is the sill)
        x0, x1, z1 = -1.0, 1.0, 0.8
        m.box((x0, 0.68, 0.0), (x1, 0.8, z1), "metal", skip=("z-",))      # the cage floor
        for k in range(1, 10):                                             # the front mesh
            x = x0 + (x1 - x0) * k / 10
            _strip(m, (x, 0.8, z1), (x, 2.6, z1), 0.02, (0, 0, 1), "screen")
        for y in (0.8, 1.7, 2.6):                                          # front rails (just proud of the mesh)
            _strip(m, (x0, y, z1 + 0.006), (x1, y, z1 + 0.006), 0.04, (0, 0, 1))
        for x, nx in ((x0, -1), (x1, 1)):                                  # the sides: corner posts, rails, a few bars
            _strip(m, (x + nx * 0.012, 0.8, z1), (x + nx * 0.012, 2.6, z1), 0.05, (nx, 0, 0))   # (posts just outside the rails)
            for y in (1.7, 2.6):
                _strip(m, (x + nx * 0.006, y, 0.0), (x + nx * 0.006, y, z1), 0.04, (nx, 0, 0))
            for k in (1, 2):
                z = z1 * k / 3
                _strip(m, (x, 0.8, z), (x, 2.6, z), 0.02, (nx, 0, 0), "screen")
        m.quad_facing((x0 - 0.1, 2.7, 0.0), (x1 + 0.1, 2.7, 0.0), (x1 + 0.1, 2.55, z1 + 0.15), (x0 - 0.1, 2.55, z1 + 0.15), (0, 1, 0), "roof")
        m.quad_facing((x0 - 0.1, 2.69, 0.0), (x1 + 0.1, 2.69, 0.0), (x1 + 0.1, 2.54, z1 + 0.15), (x0 - 0.1, 2.54, z1 + 0.15), (0, -1, 0), "roof", 0.7)
        return m
    return b


def wall_window_grille(t):
    """KOWLOON: a window behind a welded grille 0.25 m out -- bars as flat strips (budget)"""
    def b():
        m = _cheap_window(t, -0.6, 1.0, 0.6, 2.3)
        z = 0.25
        for k in range(1, 8):
            x = -0.65 + 1.3 * k / 8
            _strip(m, (x, 1.0, z), (x, 2.3, z), 0.018, (0, 0, 1), "screen")
        for y in (1.0, 1.65, 2.3):
            _strip(m, (-0.65, y, z + 0.006), (0.65, y, z + 0.006), 0.035, (0, 0, 1))
        for x, nx in ((-0.65, -1), (0.65, 1)):
            _strip(m, (x, 1.0, 0.0), (x, 1.0, z), 0.035, (nx, 0, 0))
            _strip(m, (x, 2.3, 0.0), (x, 2.3, z), 0.035, (nx, 0, 0))
            _strip(m, (x, 1.0, z), (x, 2.3, z), 0.035, (nx, 0, 0))
        return m
    return b


def wall_balcony(t, kind):
    def b():
        m = _wall(t, [_rect(-0.5, 0.0, 0.5, 2.3)])
        _window(m, t, -0.5, 0.0, 0.5, 2.3, sill=False)
        if kind == "iron":
            m.box((-1.0, -0.12, 0.0), (1.0, 0.0, 0.8), "trim")
            for k in range(11):
                x = -0.95 + k * 0.19
                m.tube((x, 0.0, 0.76), (x, 1.0, 0.76), 0.012, "metal", n=4)
            _rail(m, -1.0, 1.0, 1.0, 0.76)
            m.tube((-1.0, 1.0, 0.0), (-1.0, 1.0, 0.76), 0.02, "metal")
            m.tube((1.0, 1.0, 0.0), (1.0, 1.0, 0.76), 0.02, "metal")
            for x in (-0.8, 0.8):                                      # brackets
                m.quad_facing((x, -0.12, 0.0), (x, -0.12, 0.7), (x, -0.5, 0.0), (x, -0.5, 0.0), (1, 0, 0), "metal")
        else:                                                          # timber: covered, with a carved rail
            m.box((-1.3, -0.15, 0.0), (1.3, 0.0, 1.0), "frame")
            for x in (-1.25, 1.25):
                m.box((x - 0.06, 0.0, 0.88), (x + 0.06, 2.6, 1.0), "frame")
            m.box((-1.19, 0.85, 0.905), (1.19, 0.95, 0.985), "frame")
            for k in range(13):
                x = -1.15 + k * 0.19
                m.box((x - 0.03, 0.0, 0.92), (x + 0.03, 0.85, 0.98), "screen")
            m.quad_facing((-1.45, 2.95, 0.0), (1.45, 2.95, 0.0), (1.45, 2.6, 1.2), (-1.45, 2.6, 1.2), (0, 1, 0), "roof")
            m.quad_facing((-1.45, 2.95, 0.0), (1.45, 2.95, 0.0), (1.45, 2.6, 1.2), (-1.45, 2.6, 1.2), (0, -1, 0), "frame", 0.7)
            for x in (-1.0, 0.0, 1.0):                                 # corbels
                m.box((x - 0.06, -0.55, 0.0), (x + 0.06, -0.15, 0.25), "frame")
        return m
    return b


def wall_bay_box(t):
    """an oriel / mashrabiya box: a lattice-fronted timber bay 0.7 m out on corbels (Cairo, Jeddah, the medina's
    upper rooms)"""
    def b():
        m = _wall(t, [_rect(-0.6, 0.9, 0.6, 2.6)])
        _window(m, t, -0.6, 0.9, 0.6, 2.6, sill=False, depth=0.05)
        d = 0.7
        m.box((-0.9, 0.62, 0.0), (0.9, 0.8, d), "frame")                       # floor
        m.box((-0.95, 2.8, 0.0), (0.95, 2.95, d + 0.08), "frame")              # cornice
        for x in (-0.9, 0.84):
            m.box((x, 0.8, 0.0), (x + 0.06, 2.8, d), "frame")
        _lattice(m, -0.84, 0.8, 0.84, 2.8, d - 0.06, d, 8, 10)
        for x in (-0.7, 0.0, 0.7):                                             # stepped corbels
            m.box((x - 0.07, 0.42, 0.0), (x + 0.07, 0.62, 0.5), "frame")
            m.box((x - 0.06, 0.22, 0.0), (x + 0.06, 0.42, 0.28), "frame")
        return m
    return b


def wall_arch(t, shape):
    """an arched passage through (a lane under rooms; an arcade bay)"""
    def b():
        o = arch(shape, 2.2, 2.9, 0.0, n=8)
        m = _wall(t, [o])
        m.wall_cut(_grow(o, 0.18), [o], 0.0, 0.03, "trim", reveal_slot="trim")
        return m
    return b


def wall_blind_arch():
    def b():
        m = _wall(K)
        o = arch("horseshoe", 1.6, 2.6, 0.3, n=8)
        m.wall_cut(_grow(o, 0.15), [o], 0.0, 0.05, "trim", reveal_slot="trim")
        m.wall_cut(o, [], 0.0, 0.012, "tile")
        return m
    return b


def wall_zellij():
    """MEDINA: a blank street wall with a zellige dado and a small high grilled window"""
    def b():
        o = _rect(-0.3, 2.2, 0.3, 2.75)
        m = _wall(K, [o])
        _window(m, K, -0.3, 2.2, 0.3, 2.75, sill=False, depth=0.3)
        for k in range(5):
            m.tube((-0.25 + k * 0.125, 2.2, -0.08), (-0.25 + k * 0.125, 2.75, -0.08), 0.012, "metal", n=4)
        m.box((-HB, 0.0, 0.0), (HB, 0.6, 0.025), "tile", skip=("z-",))
        for r in range(2):                                     # a zellige checker over the base: two colours in squares
            for c in range(10):
                slot = "tile" if (r + c) % 2 else "trim"
                x = -HB + c * 0.3
                m.box((x + 0.01, 0.6 + r * 0.27, 0.0), (x + 0.29, 0.6 + r * 0.27 + 0.26, 0.03), slot, skip=("z-",))
        m.box((-HB, 1.14, 0.0), (HB, 1.22, 0.045), "trim", skip=("z-",))
        return m
    return b


def wall_qamariya():
    """TOWER HOUSE (Sana'a): a window framed in white gypsum with a half-moon stained-glass fanlight that glows at
    night"""
    def b():
        w, y0, h = 0.9, 1.0, 1.2
        sq = _rect(-w / 2, y0, w / 2, y0 + h)
        fan = [(-w / 2, y0 + h + 0.12), (w / 2, y0 + h + 0.12)] + [(w / 2 * math.cos(math.pi * k / 10), y0 + h + 0.12 + w / 2 * math.sin(math.pi * k / 10)) for k in range(1, 10)]
        m = _wall(K, [sq, fan])
        _window(m, K, -w / 2, y0, w / 2, y0 + h, sill=False, depth=0.25)
        # the fanlight: stained glass (emissive) set back
        from geom import _dedupe
        m.wall_cut(_dedupe(fan), [], -0.32, -0.28, "emissive")
        # the white gypsum frames: a band round both openings
        m.wall_cut(_grow(sq, 0.13), [sq], 0.0, 0.03, "trim", reveal_slot="trim")
        m.wall_cut(_grow(_dedupe(fan), 0.12), [_dedupe(fan)], 0.0, 0.03, "trim", reveal_slot="trim")
        return m
    return b


def wall_cantilever_step():
    """KOWLOON: the storey stepped 0.6 m out over the alley -- the wall and the soffit under it"""
    def b():
        o = _rect(-0.6, 1.0, 0.6, 2.3)
        m = Mesh()
        m.wall_cut(_bay(), [o], 0.6 - T, 0.6, "wall", reveal_slot="trim")
        _window(m, T, -0.6, 1.0, 0.6, 2.3)
        m.box((-HB, -0.2, -T), (HB, 0.0, 0.6), "wall")                          # the soffit and slab edge
        m.box((-HB, -0.32, 0.4), (HB, -0.2, 0.6), "metal")                       # a rusted beam
        return m
    return b


def wall_tower_seam():
    """KOWLOON: where two towers meet: a recessed patched strip with downpipes"""
    def b():
        m = Mesh()
        m.wall_cut(_rect(-HB, 0, -0.4, ST), [], -T, 0.0, "wall")
        m.wall_cut(_rect(0.4, 0, HB, ST), [], -T, 0.0, "wall")
        m.wall_cut(_rect(-0.4, 0, 0.4, ST), [], -T - 0.35, -0.35, "wall", reveal_slot="wall")
        m.box((-0.4, 0.0, -0.35), (-0.39, ST, 0.0), "wall")
        m.box((0.39, 0.0, -0.35), (0.4, ST, 0.0), "wall")
        for x in (-0.2, 0.1):
            m.tube((x, 0.0, -0.22), (x, ST, -0.22), 0.06, "metal", n=6)
        m.box((-0.3, 1.1, -0.36), (0.3, 1.7, -0.33), "metal", 0.9)               # a patch plate
        return m
    return b


def wall_fountain():
    """MEDINA MARK: a zellige wall fountain -- a tiled niche with a basin"""
    def b():
        niche = arch("pointed", 1.4, 2.2, 0.4, n=8)
        m = Mesh()
        m.wall_cut(_bay(), [niche], -0.3, 0.0, "wall", reveal_slot="tile")        # the face, with the niche cut 0.3 deep
        m.wall_cut(_bay(), [], -K, -0.3, "tile")                                  # the body behind: its face is the niche's back
        m.wall_cut(_grow(niche, 0.2), [niche], 0.0, 0.03, "tile", reveal_slot="tile")
        m.box((-0.8, 0.0, 0.0), (0.8, 0.55, 0.5), "tile", skip=("z-",))            # the basin, in front of the wall
        m.box((-0.65, 0.555, 0.08), (0.65, 0.56, 0.42), "water", skip=("y-",))
        m.tube((0.0, 1.1, -0.3), (0.0, 1.0, -0.1), 0.03, "metal")
        return m
    return b


# ------------------------------------------------------------------ corners
def corner_quoin(t):
    def b():
        m = Mesh()
        for k in range(5):
            y = k * 0.64
            w = 0.45 if k % 2 else 0.3
            m.box((-w, y + 0.02, -0.05), (0.05, y + 0.6, 0.05), "trim")
            m.box((-0.05, y + 0.02, -(0.75 - w)), (0.05, y + 0.6, 0.05), "trim")
        return m
    return b


def corner_round():
    """MEDINA / MUD: the sharp corner softened into a rounded buttress"""
    def b():
        m = Mesh()
        m.cyl(-0.25, -0.25, 0.42, 0.0, ST, "wall", n=8, r1=0.36)    # (centred inside the cell's corner, bulging 0.17 m out)
        return m
    return b


def corner_chamfer():
    def b():
        m = Mesh()
        m.prism_xz([(-0.5, 0.0), (0.0, 0.0), (0.0, -0.5)], 0.0, ST, "wall")
        return m
    return b


def corner_column():
    def b():
        m = Mesh()
        m.cbox(0, 0, 0, 0.4, 0.3, 0.4, "trim")
        m.cyl(0, 0, 0.14, 0.3, ST - 0.35, "trim", n=8)
        m.cbox(0, ST - 0.35, 0, 0.4, 0.35, 0.4, "trim")
        return m
    return b


def plinth(t):
    """a base course under a wall bay: from y 0 down 2 m (most of it buried in the deck where it rises), so a floor
    standing above a sloping deck has no gap under it"""
    def b():
        m = Mesh()
        m.box((-HB, -2.0, -t), (HB, 0.0, 0.0), "wall", 0.78, skip=("y+",))
        return m
    return b


def corner_in(t):
    """a filler post in an inner corner (the empty cell in +X/+Z, walls along both faces): the t x t square the two
    walls' bodies leave at the vertex"""
    def b():
        m = Mesh()
        m.box((-t, 0.0, -t), (0.0, ST, 0.0), "wall", skip=("y-", "y+"))
        return m
    return b


def kerb(kind):
    """a pond's stone edge, on a cell edge like a wall bay: the kerb lies along x, the water on the +Z side"""
    def b():
        m = Mesh()
        if kind == "straight":
            m.box((-HB, -0.4, -0.35), (HB, 0.18, 0.0), "trim", skip=("y-",))
        elif kind == "out":                                    # the water wraps round outside this corner
            m.box((-HB, -0.4, -0.35), (0.0, 0.18, 0.0), "trim", skip=("y-",))
            m.box((0.0, -0.4, -HB), (0.35, 0.18, 0.0), "trim", skip=("y-",))
        else:                                                  # "in": the water's corner, the kerb turning inward
            m.box((-HB, -0.4, -0.35), (-0.35, 0.18, 0.0), "trim", skip=("y-",))
            m.box((-0.35, -0.4, -0.35), (0.0, 0.18, HB), "trim", skip=("y-",))
        return m
    return b


# ------------------------------------------------------------------ roofs, edges, crowns
def roof_terrace():
    def b():
        m = Mesh()
        m.box((-HB, -0.25, -HB), (HB, 0.0, HB), "wall", 0.92)             # (a lime / concrete terrace: the wall's colour)
        return m
    return b


def roof_tin():
    def b():
        m = Mesh()
        m.box((-HB, -0.25, -HB), (HB, -0.05, HB), "wall")
        for k in range(10):
            x = -HB + 0.15 + k * 0.3
            m.box((x - 0.06, -0.05, -HB), (x + 0.06, 0.0, HB), "metal")
        return m
    return b


def floor_slab():
    def b():
        m = Mesh()
        m.box((-HB, -0.25, -HB), (HB, 0.0, HB), "wall", slots={"y+": "ground"})
        return m
    return b


def edge_parapet(t, kind):
    def b():
        m = Mesh()
        h = 0.9 if kind != "rail" else 0.0
        if kind == "plain":
            tt = min(t, 0.4)                                   # (a parapet is thinner than the wall it stands on)
            hh = 0.75 if t > 0.3 else h
            m.box((-HB, 0.0, -tt), (HB, hh, 0.0), "wall")
            m.box((-HB, hh, -tt - 0.03), (HB, hh + 0.06, 0.03), "trim")
        elif kind == "crenel":                                 # stepped / triangular merlons (Almohad, Omani)
            m.box((-HB, 0.0, -t), (HB, 0.55, 0.0), "wall")
            for k in range(4):
                x = -HB + 0.375 + k * 0.75
                prof = [(x - 0.25, 0.55), (x + 0.25, 0.55), (x + 0.25, 0.85), (x + 0.12, 0.85), (x + 0.12, 1.05),
                        (x - 0.12, 1.05), (x - 0.12, 0.85), (x - 0.25, 0.85)]
                m.wall_cut(prof, [], -t, 0.0, "wall")
        elif kind == "rounded":                                # Shibam: soft white merlons
            m.box((-HB, 0.0, -t), (HB, 0.5, 0.0), "trim")
            for k in range(5):
                x = -HB + 0.3 + k * 0.6
                prof = [(x - 0.2, 0.5), (x + 0.2, 0.5)] + [(x + 0.2 * math.cos(math.pi * j / 6), 0.75 + 0.2 * math.sin(math.pi * j / 6)) for j in range(0, 7)]
                from geom import _dedupe
                m.wall_cut(_dedupe(prof), [], -t, 0.0, "trim")
        elif kind == "jali":                                   # a pierced stone screen parapet
            m.box((-HB, 0.0, -t), (HB, 0.3, 0.0), "wall")
            m.box((-HB, 0.9, -t - 0.03), (HB, 1.0, 0.03), "trim")
            for k in range(4):
                x0 = -HB + 0.05 + k * 0.75
                _lattice(m, x0, 0.3, x0 + 0.65, 0.9, -t, 0.0, 4, 3, slot="trim", bar=0.05)
        elif kind == "rail":                                   # Kowloon: a pipe railing on a low upstand
            m.box((-HB, 0.0, -0.2), (HB, 0.2, 0.0), "wall")
            for x in (-1.4, 0.0, 1.4):
                m.tube((x, 0.2, -0.1), (x, 1.05, -0.1), 0.025, "metal")
            _rail(m, -HB, HB, 1.05, -0.1)
            _rail(m, -HB, HB, 0.6, -0.1, r=0.018)
        return m
    return b


def edge_eave(kind):
    def b():
        m = Mesh()
        if kind == "tile_green":                               # MEDINA: green glazed tile eave on cedar brackets
            m.box((-HB, 0.0, -0.3), (HB, 0.15, 0.0), "frame")
            m.quad_facing((-HB, 0.55, -0.3), (HB, 0.55, -0.3), (HB, 0.15, 0.55), (-HB, 0.15, 0.55), (0, 1, 0.5), "roof")
            m.quad_facing((-HB, 0.5, -0.3), (HB, 0.5, -0.3), (HB, 0.1, 0.55), (-HB, 0.1, 0.55), (0, -1, -0.5), "frame", 0.7)
            for k in range(12):
                x = -HB + 0.125 + k * 0.25
                m.tube((x, 0.56, -0.3), (x, 0.16, 0.55), 0.035, "roof", n=4)
            for x in (-1.2, -0.4, 0.4, 1.2):
                m.box((x - 0.05, -0.25, 0.0), (x + 0.05, 0.1, 0.4), "frame")
        else:                                                  # tin
            m.quad_facing((-HB, 0.35, -0.1), (HB, 0.35, -0.1), (HB, 0.1, 0.55), (-HB, 0.1, 0.55), (0, 1, 0.4), "metal")
            m.quad_facing((-HB, 0.33, -0.1), (HB, 0.33, -0.1), (HB, 0.08, 0.55), (-HB, 0.08, 0.55), (0, -1, -0.4), "metal", 0.7)
            m.tube((-HB, 0.08, 0.55), (HB, 0.08, 0.55), 0.05, "metal")
        return m
    return b


def crown_band():
    """a white band round a wall's top (Sana'a gypsum line; any civ's cornice)"""
    def b():
        m = Mesh()
        m.box((-HB, -0.45, 0.0), (HB, -0.3, 0.08), "trim")
        m.box((-HB, -0.18, 0.0), (HB, -0.05, 0.1), "trim")
        return m
    return b


def dome_cap():
    def b():
        m = Mesh()
        m.cyl(0, 0, 1.25, 0.0, 0.6, "wall", n=12)
        prof = [(1.3, 0.6)] + [(1.3 * math.cos(math.pi / 2 * k / 6), 0.6 + 1.3 * math.sin(math.pi / 2 * k / 6)) for k in range(1, 6)] + [(0.0, 1.9)]
        m.lathe(prof, "roof", n=12)
        m.lathe([(0.06, 1.88), (0.1, 2.05), (0.0, 2.4)], "metal", n=6)
        return m
    return b


def green_hip():
    """MEDINA (sacred): a green-tiled hip roof over a cell"""
    def b():
        m = Mesh()
        a, h = HB + 0.3, 1.5
        pts = [(-a, 0.0, -a), (a, 0.0, -a), (a, 0.0, a), (-a, 0.0, a)]
        apex = (0.0, h, 0.0)
        for k in range(4):
            p, q = pts[k], pts[(k + 1) % 4]
            mid = ((p[0] + q[0]) / 2, 0.5, (p[2] + q[2]) / 2)
            m.tri_facing(p, q, apex, mid, "roof")
        m.tri_facing(pts[0], pts[1], pts[2], (0, -1, 0), "frame", 0.7)
        m.tri_facing(pts[0], pts[2], pts[3], (0, -1, 0), "frame", 0.7)
        m.lathe([(0.05, h - 0.05), (0.08, h + 0.25), (0.0, h + 0.6)], "metal", n=6)
        return m
    return b


# ------------------------------------------------------------------ ground: paving, steps, stairs, bridges, passages
def pave(kind):
    """floor paving, cheap: a dark joint sheet at y -0.01 and one raised quad per stone (2 tris each) -- the joints
    read as lines between them; stones shaded by a hash for variety, the court a two-colour checker.  <= 20 tris."""
    def b():
        m = Mesh()
        m.quad_facing((-HB, -0.01, -HB), (HB, -0.01, -HB), (HB, -0.01, HB), (-HB, -0.01, HB), (0, 1, 0), "ground", 0.55)
        n = {"main": 2, "lane": 3, "plaza": 3, "court": 3}.get(kind, 2)
        g = {"main": 0.06, "lane": 0.05, "plaza": 0.05, "court": 0.03}.get(kind, 0.05)
        sz = BAY / n
        for i in range(n):
            for j in range(n):
                x0 = -HB + i * sz + g / 2
                z0 = -HB + j * sz + g / 2
                slot, sh = "ground", 0.86 + 0.14 * (((i * 7 + j * 13) % 5) / 4.0)
                if kind == "court":
                    slot, sh = ("tile" if (i + j) % 2 == 0 else "trim"), 1.0
                if kind == "plaza" and i == 1 and j == 1:
                    slot, sh = "trim", 1.0
                x1, z1 = x0 + sz - g, z0 + sz - g
                m.quad_facing((x0, 0.0, z0), (x1, 0.0, z0), (x1, 0.0, z1), (x0, 0.0, z1), (0, 1, 0), slot, sh)
        return m
    return b


def pave_garden():
    def b():
        m = Mesh()
        m.box((-HB + 0.15, -0.12, -HB + 0.15), (HB - 0.15, 0.0, HB - 0.15), "plant")
        for side in range(4):
            r = rot_y(90 * side)
            e = Mesh()
            e.box((-HB, -0.12, HB - 0.15), (HB - 0.15, 0.08, HB), "trim")
            m.add(e, r)
        return m
    return b


def steps_up():
    """half a storey (1.6 m) up across the cell, along +Z: ten steps (with a ramp for the walker)"""
    def b():
        m = Mesh()
        n = 10
        for k in range(n):
            z0 = -HB + k * BAY / n
            m.box((-1.4, -0.1, z0), (1.4, (k + 1) * 1.6 / n, z0 + BAY / n), "ground", 0.9 + 0.1 * (k % 2))
        return m
    return b


def step_low(n):
    """steps that sit flush in a ramped street: n risers of 0.2 m over the cell along +Z (n 1: one step at the cell's
    middle; n 4: 0.8 m in four treads of 0.75 m), each block reaching 0.3 m below its tread into the deck"""
    def b():
        m = Mesh()
        if n == 1:
            m.box((-HB, -0.3, -HB), (HB, 0.0, 0.0), "ground", 0.9, skip=("y-", "z+"))
            m.box((-HB, -0.3, 0.0), (HB, 0.2, HB), "ground", 1.0, skip=("y-",))
        else:
            for k in range(n):
                z0 = -HB + k * BAY / n
                m.box((-HB, -0.3, z0), (HB, 0.2 * (k + 1), z0 + BAY / n), "ground", 0.9 + 0.1 * (k % 2),
                      skip=("y-",) + (("z-",) if k > 0 else ()))
        return m
    return b


def stair_run():
    """a full storey up (3.2 m) over two cells (6 m along +Z from this cell's -Z edge): steps with stringers"""
    def b():
        m = Mesh()
        n = 18
        for k in range(n):
            z0 = -HB + k * 6.0 / n
            y = (k + 1) * ST / n
            m.box((-0.65, y - 0.1, z0), (0.65, y, z0 + 6.0 / n + 0.03), "ground")
        for x in (-0.7, 0.7):
            m.quad_facing((x, 0.0, -HB), (x, 0.0, -HB + 0.4), (x, ST, -HB + 6.0), (x, ST - 0.4, -HB + 6.0), (math.copysign(1, x), 0, 0), "metal")
            m.quad_facing((x - 0.04 * math.copysign(1, x), 0.0, -HB), (x - 0.04 * math.copysign(1, x), 0.0, -HB + 0.4),
                          (x - 0.04 * math.copysign(1, x), ST, -HB + 6.0), (x - 0.04 * math.copysign(1, x), ST - 0.4, -HB + 6.0),
                          (-math.copysign(1, x), 0, 0), "metal", 0.8)
            m.tube((x, 1.0, -HB), (x, ST + 1.0, -HB + 6.0), 0.025, "metal")
            for k in range(4):
                z = -HB + 0.3 + k * 1.8
                y = (z + HB) / 6.0 * ST
                m.tube((x, y, z), (x, y + 1.0, z), 0.02, "metal")
        return m
    return b


def stair_spiral():
    def b():
        m = Mesh()
        m.cyl(0, 0, 0.1, 0.0, ST + 1.0, "metal", n=6)
        n = 16
        for k in range(n):
            a0 = math.tau * k / n
            y = (k + 1) * ST / n
            r = 1.3
            p0 = (0.1 * math.cos(a0), y, -0.1 * math.sin(a0))
            a1 = a0 + math.tau / n * 0.92
            m.quad_facing((0.1 * math.cos(a0), y, -0.1 * math.sin(a0)), (r * math.cos(a0), y, -r * math.sin(a0)),
                          (r * math.cos(a1), y, -r * math.sin(a1)), (0.1 * math.cos(a1), y, -0.1 * math.sin(a1)), (0, 1, 0), "metal")
            m.quad_facing((0.1 * math.cos(a0), y - 0.04, -0.1 * math.sin(a0)), (r * math.cos(a0), y - 0.04, -r * math.sin(a0)),
                          (r * math.cos(a1), y - 0.04, -r * math.sin(a1)), (0.1 * math.cos(a1), y - 0.04, -0.1 * math.sin(a1)), (0, -1, 0), "metal", 0.7)
            m.tube((r * math.cos(a0), y, -r * math.sin(a0)), (r * math.cos(a0), y + 0.95, -r * math.sin(a0)), 0.012, "metal", n=4)
        return m
    return b


def ladder():
    def b():
        m = Mesh()
        for x in (-0.22, 0.22):
            m.tube((x, 0.0, -0.08), (x, ST + 0.9, -0.08), 0.02, "metal", n=4)
        for k in range(1, 14):
            m.tube((-0.22, k * 0.3, -0.08), (0.22, k * 0.3, -0.08), 0.014, "metal", n=4)
        return m
    return b


def bridge(kind):
    """a walk across one empty cell (along Z), between two cells' floors at y 0"""
    def b():
        m = Mesh()
        if kind == "plank":
            for k in range(9):
                x = -0.45 + k * 0.1125
                m.box((x - 0.05, -0.06, -HB - 0.1), (x + 0.05, 0.0, HB + 0.1), "frame", 0.85 + 0.15 * (k % 3) / 2)
            for x in (-0.55, 0.55):
                m.tube((x, 0.9, -HB), (x, 0.75, 0.0), 0.012, "fabric", n=4)
                m.tube((x, 0.75, 0.0), (x, 0.9, HB), 0.012, "fabric", n=4)
                m.tube((x, 0.0, -HB + 0.1), (x, 0.9, -HB + 0.1), 0.03, "frame", n=4)
                m.tube((x, 0.0, HB - 0.1), (x, 0.9, HB - 0.1), 0.03, "frame", n=4)
        elif kind == "timber":
            m.box((-0.8, -0.3, -HB - 0.2), (0.8, 0.0, HB + 0.2), "frame")
            for x in (-0.8, 0.8):
                for k in range(5):
                    z = -HB + k * 0.75
                    m.box((x - 0.05, 0.0, z - 0.05), (x + 0.05, 1.0, z + 0.05), "frame")
                m.box((x - 0.06, 1.0, -HB), (x + 0.06, 1.1, HB), "frame")
        else:                                                    # steel
            m.box((-0.9, -0.08, -HB - 0.2), (0.9, 0.0, HB + 0.2), "metal")
            m.box((-0.9, -0.4, -HB - 0.2), (-0.8, -0.08, HB + 0.2), "metal")
            m.box((0.8, -0.4, -HB - 0.2), (0.9, -0.08, HB + 0.2), "metal")
            for x in (-0.88, 0.88):
                _rail_z(m, x, 1.05, -HB, HB)
                for k in range(5):
                    z = -HB + k * 0.75
                    m.tube((x, 0.0, z), (x, 1.05, z), 0.02, "metal", n=4)
        return m
    return b


def _rail_z(m, x, y, z0, z1, slot="metal", r=0.025):
    m.tube((x, y, z0), (x, y, z1), r, slot, n=5)


def sabat_beams():
    """MEDINA MARK: the cedar beams and slab under a room that bridges a lane (placed at the room's floor level, over
    the lane cell)"""
    def b():
        m = Mesh()
        m.box((-HB, -0.3, -HB), (HB, 0.0, HB), "wall")
        for k in range(7):
            x = -HB + 0.25 + k * 0.42
            m.box((x - 0.07, -0.48, -HB), (x + 0.07, -0.3, HB), "frame", 0.85)
        return m
    return b


def shoring_beam():
    """MEDINA MARK: a timber prop between the two walls of a lane (across x), with its wedges"""
    def b():
        m = Mesh()
        m.box((-HB, 2.4, -0.1), (HB, 2.6, 0.1), "frame", 0.8)
        for x in (-HB + 0.02, HB - 0.2):
            m.box((x, 2.3, -0.14), (x + 0.18, 2.7, 0.14), "frame", 0.7)
        return m
    return b


def alley_ceiling():
    """KOWLOON: the underside of the mass over a covered alley -- pipes, cable trays and a fluorescent tube (placed
    at the passage cell's ceiling: y 0 = the ceiling)"""
    def b():
        m = Mesh()
        m.box((-HB, -0.05, -HB), (HB, 0.0, HB), "wall", 0.6)
        for x, r in ((-1.1, 0.05), (-0.85, 0.035), (0.9, 0.06)):
            m.tube((x, -0.15, -HB), (x, -0.15, HB), r, "metal", n=6)
        m.box((-0.5, -0.3, -HB), (0.2, -0.25, HB), "metal")
        for k in range(6):
            m.tube((-0.45 + k * 0.12, -0.33, -HB), (-0.45 + k * 0.12, -0.33, HB), 0.012, "fabric", n=4)   # (hung under the tray)
        m.box((0.3, -0.42, -0.6), (0.38, -0.36, 0.6), "emissive")
        m.box((0.28, -0.36, -0.62), (0.4, -0.3, 0.62), "metal")
        return m
    return b


def arcade_pier():
    def b():
        m = Mesh()
        m.cbox(0, 0, 0, 0.55, 0.25, 0.55, "trim")
        m.cbox(0, 0.25, 0, 0.42, ST - 0.6, 0.42, "wall")
        m.cbox(0, ST - 0.35, 0, 0.6, 0.35, 0.6, "trim")
        return m
    return b


def fountain_riad():
    """MEDINA MARK: the riad's court fountain -- a tiled octagonal basin with a bowl and spout"""
    def b():
        m = Mesh()
        oct_ = [(1.1 * math.cos(math.tau * k / 8 + math.pi / 8), 1.1 * math.sin(math.tau * k / 8 + math.pi / 8)) for k in range(8)]
        inner = [(0.95 * x / 1.1, 0.95 * z / 1.1) for x, z in oct_]
        m.prism_xz(oct_, 0.0, 0.45, "tile", cap_slot="trim")
        m.prism_xz(inner, 0.35, 0.4, "water")
        m.lathe([(0.12, 0.4), (0.1, 0.85), (0.45, 0.95), (0.45, 1.02), (0.0, 1.02)], "trim", n=10)
        m.lathe([(0.04, 1.02), (0.03, 1.25), (0.0, 1.3)], "metal", n=6)
        return m
    return b


def minaret(part):
    """MEDINA MARK: the square Almohad minaret, stacked a cell a storey: base, shaft (tiled blind arches), top
    (crenels, lantern, green cap, brass finial)"""
    def b():
        m = Mesh()
        w = 1.4
        if part in ("base", "shaft"):
            m.box((-w, 0.0, -w), (w, ST, w), "wall")
            if part == "shaft":
                for side in range(4):
                    e = Mesh()
                    o = arch("lobed", 1.2, 2.2, 0.5, n=4)
                    e.wall_cut(_grow(o, 0.12), [o], 0.0, 0.03, "trim", reveal_slot="trim")
                    e.wall_cut(o, [], 0.0, 0.015, "tile")
                    e.box((-w, 2.9, 0.0), (w, 3.05, 0.04), "tile")
                    m.add(e, lambda p, s=side: rot_y(90 * s)((p[0], p[1], p[2] + w)))
        else:
            m.box((-w, 0.0, -w), (w, 0.6, w), "wall")
            for side in range(4):
                e = Mesh()
                for k in range(4):
                    x = -w + 0.35 + k * 0.7
                    e.wall_cut([(x - 0.22, 0.6), (x + 0.22, 0.6), (x + 0.22, 0.95), (x, 1.15), (x - 0.22, 0.95)], [], -0.25, 0.0, "trim")
                m.add(e, lambda p, s=side: rot_y(90 * s)((p[0], p[1], p[2] + w)))
            m.box((-0.6, 0.6, -0.6), (0.6, 2.2, 0.6), "wall")
            for side in range(4):
                e = Mesh()
                o = arch("round", 0.5, 1.0, 1.0, n=6)
                e.wall_cut(_grow(o, 0.08), [o], 0.0, 0.03, "tile", reveal_slot="tile")
                m.add(e, lambda p, s=side: rot_y(90 * s)((p[0], p[1], p[2] + 0.6)))
            a = 0.75
            apex = (0.0, 3.0, 0.0)
            pts = [(-a, 2.2, -a), (a, 2.2, -a), (a, 2.2, a), (-a, 2.2, a)]
            for k in range(4):
                p, q = pts[k], pts[(k + 1) % 4]
                m.tri_facing(p, q, apex, ((p[0] + q[0]) / 2, 0.3, (p[2] + q[2]) / 2), "roof")
            m.tri_facing(pts[0], pts[1], pts[2], (0, -1, 0), "wall", 0.7)
            m.tri_facing(pts[0], pts[2], pts[3], (0, -1, 0), "wall", 0.7)
            for k, r in enumerate((0.16, 0.13, 0.1)):
                m.lathe([(0.0, 3.0 + k * 0.35), (r, 3.1 + k * 0.35), (r, 3.2 + k * 0.35), (0.0, 3.32 + k * 0.35)], "metal", n=8)
            m.lathe([(0.025, 4.05), (0.025, 4.5), (0.0, 4.6)], "metal", n=5)
        return m
    return b


# ------------------------------------------------------------------ interiors (cells you can enter)
def int_floor():
    def b():
        m = Mesh()
        m.box((-HB, -0.04, -HB), (HB, 0.0, HB), "ground")
        return m
    return b


def int_ceiling():
    def b():
        m = Mesh()
        m.box((-HB, ST - 0.06, -HB), (HB, ST, HB), "trim", 0.9)
        for k in range(1, 5):
            v = -HB + k * 0.6
            m.box((v - 0.012, ST - 0.075, -HB), (v + 0.012, ST - 0.06, HB), "metal", 0.8)
            m.box((-HB, ST - 0.075, v - 0.012), (HB, ST - 0.06, v + 0.012), "metal", 0.8)
        return m
    return b


def int_counter():
    def b():
        m = Mesh()
        m.box((-1.2, 0.0, -0.5), (1.2, 0.9, 0.1), "frame")
        m.box((-1.25, 0.9, -0.55), (1.25, 0.95, 0.15), "trim")
        return m
    return b


def int_shelves():
    def b():
        m = Mesh()
        m.box((-1.3, 0.0, -HB + 0.05), (1.3, 2.2, -HB + 0.45), "frame", 0.8)
        for k in range(5):
            m.box((-1.25, 0.25 + k * 0.45, -HB + 0.45), (1.25, 0.28 + k * 0.45, -HB + 0.48), "trim")
            for j in range(6):
                m.cbox(-1.1 + j * 0.42, 0.28 + k * 0.45, -HB + 0.3, 0.25, 0.2, 0.22, ["fabric", "metal", "trim"][(j + k) % 3], 0.9)
        return m
    return b


def int_table_set():
    def b():
        m = Mesh()
        m.cyl(0, 0, 0.5, 0.72, 0.76, "frame", n=10)
        m.cyl(0, 0, 0.05, 0.0, 0.72, "metal", n=6)
        for k in range(4):
            a = math.tau * k / 4
            cx, cz = 0.85 * math.cos(a), 0.85 * math.sin(a)
            m.cbox(cx, 0.42, cz, 0.4, 0.05, 0.4, "fabric")
            for dx in (-0.16, 0.16):
                for dz in (-0.16, 0.16):
                    m.tube((cx + dx, 0.0, cz + dz), (cx + dx, 0.42, cz + dz), 0.015, "metal", n=4)
        return m
    return b


def int_bed():
    def b():
        m = Mesh()
        m.box((-0.8, 0.0, -1.3), (0.8, 0.45, 0.8), "frame")
        m.box((-0.75, 0.45, -1.25), (0.75, 0.6, 0.75), "fabric")
        m.box((-0.6, 0.6, -1.2), (0.6, 0.72, -0.85), "trim")
        m.box((-0.8, 0.0, -1.35), (0.8, 1.0, -1.25), "frame")
        return m
    return b


def int_lamp():
    def b():
        m = Mesh()
        m.tube((0, ST, 0), (0, ST - 0.7, 0), 0.008, "metal", n=4)
        m.lathe([(0.0, ST - 0.95), (0.25, ST - 0.95), (0.05, ST - 0.7)], "emissive", n=8)
        return m
    return b


# ------------------------------------------------------------------ overlay: the cyberpunk layer and street furniture
def ov_ac():
    def b():
        m = Mesh()
        m.box((-0.4, 0.0, 0.0), (0.4, 0.55, 0.3), "trim", 0.95)
        m.cyl(0.0, 0.31, 0.2, 0.08, 0.47, "metal", n=8)          # (a fan grille facing +Z: drawn as a disc)
        m.tube((0.3, 0.0, 0.15), (0.3, -0.6, 0.15), 0.015, "metal", n=4)
        return m
    return b


def ov_tank():
    def b():
        m = Mesh()
        for x in (-0.5, 0.5):
            m.box((x - 0.05, 0.0, -0.6), (x + 0.05, 0.6, 0.6), "metal")
        m.cyl(0, 0, 0.75, 0.6, 2.0, "trim", n=10)
        m.lathe([(0.75, 2.0), (0.4, 2.25), (0.0, 2.3)], "trim", n=10)
        return m
    return b


def ov_pipe_run():
    def b():
        m = Mesh()
        m.tube((0.9, 0.0, 0.12), (0.9, ST, 0.12), 0.07, "metal", n=6)
        m.tube((1.1, 0.0, 0.08), (1.1, ST, 0.08), 0.035, "metal", n=5)
        for y in (0.6, 1.6, 2.6):
            m.box((0.82, y, 0.0), (1.18, y + 0.05, 0.2), "metal")
        return m
    return b


def ov_cables():
    """cables sagging across a lane (along X, at about 3 m)"""
    def b():
        m = Mesh()
        for k, (z, sag) in enumerate(((-0.6, 0.35), (-0.2, 0.5), (0.3, 0.25), (0.8, 0.45))):
            pts = [(-HB + 3.0 * i / 6, 2.9 + 0.1 * k - sag * (1 - (2 * i / 6 - 1) ** 2), z) for i in range(7)]
            for a, c in zip(pts, pts[1:]):
                m.tube(a, c, 0.012, "fabric", n=4)
        return m
    return b


def ov_sign_blade():
    """a vertical blade sign sticking out of a facade (+Z), lit both faces"""
    def b():
        m = Mesh()
        m.box((-0.05, 0.3, 0.0), (0.05, 2.9, 0.15), "metal")
        m.box((-0.04, 0.2, 0.15), (0.04, 3.0, 0.85), "metal")
        m.box((-0.06, 0.3, 0.2), (0.06, 2.9, 0.8), "emissive")
        return m
    return b


def ov_sign_box():
    def b():
        m = Mesh()
        m.box((-1.0, 0.0, 0.0), (1.0, 0.6, 0.25), "metal")
        m.box((-0.95, 0.05, 0.25), (0.95, 0.55, 0.27), "emissive")
        return m
    return b


def ov_sign_board():
    def b():
        m = Mesh()
        m.box((-1.2, 0.0, 0.0), (1.2, 0.5, 0.06), "fabric")
        m.box((-1.25, -0.03, 0.0), (1.25, 0.0, 0.08), "frame")
        return m
    return b


def ov_sign_arm():
    """KOWLOON MARK: a steel arm 2.5 m over the street holding a big lightbox"""
    def b():
        m = Mesh()
        m.box((-0.15, 0.0, 0.0), (0.15, 0.4, 0.1), "metal")
        m.tube((0.0, 0.2, 0.05), (0.0, 0.2, 1.6), 0.045, "metal")
        m.tube((0.0, 0.8, 0.05), (0.0, 0.25, 1.3), 0.03, "metal")
        m.box((-0.08, -0.95, 0.45), (0.08, 0.15, 1.6), "metal")
        m.box((-0.1, -0.88, 0.52), (0.1, 0.08, 1.53), "emissive")
        return m
    return b


def ov_lantern():
    """MEDINA: a pierced brass lantern on a wall bracket (emissive core)"""
    def b():
        m = Mesh()
        m.tube((0, 0.0, 0.0), (0, 0.0, 0.5), 0.02, "metal", n=4)
        m.tube((0, 0.0, 0.5), (0, -0.15, 0.5), 0.01, "metal", n=4)
        m.lathe([(0.0, -0.75), (0.1, -0.7), (0.15, -0.45), (0.12, -0.3), (0.05, -0.2), (0.0, -0.15)], "metal", n=8, cz=0.5)
        m.lathe([(0.0, -0.66), (0.1, -0.6), (0.11, -0.45), (0.0, -0.35)], "emissive", n=6, cz=0.5)
        return m
    return b


def ov_festoon():
    def b():
        m = Mesh()
        pts = [(-HB + 3.0 * i / 8, 3.0 - 0.45 * (1 - (2 * i / 8 - 1) ** 2), 0.0) for i in range(9)]
        for a, c in zip(pts, pts[1:]):
            m.tube(a, c, 0.008, "metal", n=3)
        for p in pts[1:-1]:
            m.lathe([(0.0, p[1] - 0.12), (0.05, p[1] - 0.08), (0.0, p[1] - 0.02)], "emissive", n=5, cx=p[0], cz=p[2])
        return m
    return b


def ov_laundry():
    def b():
        m = Mesh()
        m.tube((-1.2, 2.4, 0.55), (1.2, 2.4, 0.55), 0.008, "metal", n=3)
        for k, w in enumerate((0.5, 0.35, 0.6, 0.4)):
            x = -1.0 + k * 0.6
            m.quad_facing((x, 2.4, 0.55), (x + w, 2.4, 0.55), (x + w, 1.7 + 0.1 * k, 0.55), (x, 1.7 + 0.1 * k, 0.55), (0, 0, 1), "fabric", 0.8 + 0.06 * k)
            m.quad_facing((x, 2.4, 0.548), (x + w, 2.4, 0.548), (x + w, 1.7 + 0.1 * k, 0.548), (x, 1.7 + 0.1 * k, 0.548), (0, 0, -1), "fabric", 0.7)
        return m
    return b


def ov_shack(kind):
    """KOWLOON / any roof: a rooftop shack of corrugated sheet"""
    def b():
        m = Mesh()
        w, d, h = {"a": (2.4, 2.0, 2.3), "b": (2.8, 1.6, 2.1), "c": (1.6, 1.6, 2.4)}[kind]
        m.box((-w / 2, 0.0, -d / 2), (w / 2, h, d / 2), "metal", 0.85)
        m.quad_facing((-w / 2 - 0.15, h + 0.25, -d / 2 - 0.15), (w / 2 + 0.15, h + 0.25, -d / 2 - 0.15),
                      (w / 2 + 0.15, h, d / 2 + 0.2), (-w / 2 - 0.15, h, d / 2 + 0.2), (0, 1, 0.2), "roof")
        m.quad_facing((-w / 2 - 0.15, h + 0.23, -d / 2 - 0.15), (w / 2 + 0.15, h + 0.23, -d / 2 - 0.15),
                      (w / 2 + 0.15, h - 0.02, d / 2 + 0.2), (-w / 2 - 0.15, h - 0.02, d / 2 + 0.2), (0, -1, -0.2), "metal", 0.7)
        m.box((-0.4, 0.0, d / 2), (0.4, 1.95, d / 2 + 0.03), "frame")
        m.pane(0.55, 1.1, w / 2 - 0.2, 1.7, d / 2 + 0.01)
        return m
    return b


def ov_antennas():
    def b():
        m = Mesh()
        for k, (x, z, h) in enumerate(((-0.8, -0.6, 4.5), (0.5, 0.2, 3.2), (1.0, -0.9, 5.5), (-0.2, 0.9, 2.6))):
            m.tube((x, 0.0, z), (x, h, z), 0.025, "metal", n=4)
            for j in range(3):
                y = h - 0.3 - j * 0.45
                m.tube((x - 0.5, y, z), (x + 0.5, y, z), 0.01, "metal", n=3)
        return m
    return b


def ov_dish():
    def b():
        m = Mesh()
        m.tube((0, 0.0, 0), (0, 1.0, 0), 0.03, "metal", n=4)
        m.lathe([(0.0, 0.0), (0.35, 0.05), (0.55, 0.18)], "metal", n=10)
        return m
    return b


def ov_awning_cane():
    """MEDINA: a cane-slat shade over a souk lane (across the cell, at 3 m)"""
    def b():
        m = Mesh()
        for x in (-HB + 0.05, HB - 0.05):
            m.box((x - 0.04, 2.9, -HB), (x + 0.04, 3.0, HB), "frame")
        for k in range(20):
            z = -HB + 0.075 + k * 0.15
            m.box((-HB, 3.0, z - 0.04), (HB, 3.03, z + 0.04), "fabric", 0.8 + 0.2 * (k % 2))
        return m
    return b


def ov_fluoro():
    def b():
        m = Mesh()
        m.box((-0.65, 0.0, 0.0), (0.65, 0.08, 0.08), "metal")
        m.box((-0.6, -0.04, 0.02), (0.6, 0.0, 0.06), "emissive")
        return m
    return b


def ov_playground():
    """KOWLOON MARK: the fenced rooftop court -- a swing and a hoop"""
    def b():
        m = Mesh()
        for x in (-HB + 0.05, HB - 0.05):
            for z in (-HB + 0.05, HB - 0.05):
                m.tube((x, 0.0, z), (x, 2.0, z), 0.025, "metal", n=4)
        for z in (-HB + 0.05, HB - 0.05):
            _rail(m, -HB + 0.05, HB - 0.05, 2.0, z)
            _bars(m, -HB + 0.05, 0.0, HB - 0.05, 2.0, z, 14, "screen", r=0.008)
        for x in (-HB + 0.05, HB - 0.05):
            _rail_z(m, x, 2.0, -HB + 0.05, HB - 0.05)
        for x in (-0.9, 0.3):                                     # the swing frame
            m.tube((x, 0.0, -0.9), (x, 1.8, -0.9), 0.03, "metal", n=4)
        m.tube((-0.9, 1.8, -0.9), (0.3, 1.8, -0.9), 0.03, "metal", n=4)
        for x in (-0.5, -0.1):
            m.tube((x, 1.8, -0.9), (x, 0.5, -0.9), 0.008, "metal", n=3)
        m.box((-0.55, 0.45, -1.0), (-0.05, 0.5, -0.8), "fabric")
        m.tube((1.0, 0.0, 1.0), (1.0, 2.6, 1.0), 0.04, "metal", n=5)   # the hoop
        m.box((0.7, 2.6, 0.9), (1.3, 3.1, 0.95), "trim")
        m.tube((1.0, 2.7, 0.95), (1.0, 2.7, 0.75), 0.015, "metal", n=4)
        return m
    return b


def ov_stall():
    def b():
        m = Mesh()
        m.box((-1.2, 0.0, -0.6), (1.2, 0.85, 0.6), "frame")
        for x in (-1.15, 1.15):
            for z in (-0.55, 0.55):
                m.tube((x, 0.85, z), (x, 2.3, z), 0.03, "frame", n=4)
        m.quad_facing((-1.4, 2.5, -0.8), (1.4, 2.5, -0.8), (1.4, 2.2, 0.9), (-1.4, 2.2, 0.9), (0, 1, 0), "fabric")
        m.quad_facing((-1.4, 2.48, -0.8), (1.4, 2.48, -0.8), (1.4, 2.18, 0.9), (-1.4, 2.18, 0.9), (0, -1, 0), "fabric", 0.7)
        for k in range(8):
            m.cbox(-1.0 + k * 0.28, 0.85, -0.1 + 0.2 * (k % 2), 0.22, 0.18, 0.3, ["fabric", "trim", "plant"][k % 3], 0.9)
        return m
    return b


def ov_planter():
    def b():
        m = Mesh()
        m.box((-0.5, 0.0, 0.0), (0.5, 0.45, 0.45), "trim")
        m.box((-0.45, 0.45, 0.05), (0.45, 0.5, 0.4), "ground", 0.6)
        for k in range(5):
            m.lathe([(0.0, 0.5), (0.16, 0.7), (0.12, 0.95), (0.0, 1.05)], "plant", n=6, cx=-0.36 + k * 0.18, cz=0.22)
        return m
    return b


# ------------------------------------------------------------------ the catalogue
def _w(group, b, civs, lod1="box", collide=True, kind=None, notes="", span=(1, 1)):
    return {"group": group, "build": b, "civs": civs, "lod1": lod1, "collide": collide, "kind": kind or group, "notes": notes,
            "span": list(span)}


BOTH = ["shared"]
MED = ["maghrebi_medina"]
KOW = ["kowloon_walled"]
TOW = ["yemeni_tower", "maghrebi_medina"]

PIECES = {}
for th, t in (("t", T), ("k", K)):
    PIECES[f"wall_plain_{th}"] = _w("wall", wall_plain(t), BOTH)
    PIECES[f"wall_window_s_{th}"] = _w("wall", wall_window(t, 0.6, 0.8, 1.9), BOTH, notes="small and high (a narrow lane, privacy)")
    PIECES[f"wall_window_m_{th}"] = _w("wall", wall_window(t, 1.0, 1.4, 0.9), BOTH)
    PIECES[f"wall_window_l_{th}"] = _w("wall", wall_window(t, 1.4, 1.8, 0.7), BOTH)
    PIECES[f"wall_window_pair_{th}"] = _w("wall", wall_window_pair(t), BOTH)
    PIECES[f"wall_door_{th}"] = _w("wall", wall_door(t), BOTH, notes="a plain door: the generator marks enterable ones")
    PIECES[f"wall_shopfront_a_{th}"] = _w("wall", wall_shopfront(t, "a"), BOTH, notes="rolling shutter half down")
    PIECES[f"wall_shopfront_b_{th}"] = _w("wall", wall_shopfront(t, "b"), BOTH, notes="open front, counter, awning")
    PIECES[f"wall_screen_{th}"] = _w("wall", wall_screen(t), BOTH, notes="lattice screen: mashrabiya / jali / shoji by the screen slot")
    PIECES[f"wall_balcony_iron_{th}"] = _w("wall", wall_balcony(t, "iron"), BOTH)
    PIECES[f"wall_balcony_timber_{th}"] = _w("wall", wall_balcony(t, "timber"), BOTH, notes="covered timber gallery bay (riad galleries, Ottoman)")
    PIECES[f"wall_bay_box_{th}"] = _w("wall", wall_bay_box(t), BOTH, notes="oriel / mashrabiya box 0.7 m out on corbels")
    for sh in ("round", "pointed", "horseshoe"):
        PIECES[f"wall_arch_{sh}_{th}"] = _w("wall", wall_arch(t, sh), BOTH if sh != "horseshoe" else MED, kind="passage",
                                             notes="a passage through: a lane under rooms, an arcade bay")
PIECES["wall_balcony_cage_t"] = _w("wall", wall_balcony_cage(T), KOW, notes="KOWLOON: the welded cage balcony")
PIECES["wall_window_grille_t"] = _w("wall", wall_window_grille(T), KOW, notes="KOWLOON: window behind a grille box")
PIECES["wall_cantilever_step_t"] = _w("wall", wall_cantilever_step(), KOW, notes="KOWLOON MARK: storey stepped 0.6 m out over the alley")
PIECES["wall_tower_seam_t"] = _w("wall", wall_tower_seam(), KOW, notes="KOWLOON MARK: the joint between two towers")
PIECES["wall_door_portal_k"] = _w("wall", wall_door_portal(), MED, lod1="keep", notes="MEDINA MARK: horseshoe studded cedar door, zellige surround")
PIECES["wall_zellij_k"] = _w("wall", wall_zellij(), MED, notes="MEDINA: blank street wall, zellige dado, small high grilled window")
PIECES["wall_blind_arch_k"] = _w("wall", wall_blind_arch(), MED)
PIECES["wall_fountain_k"] = _w("wall", wall_fountain(), MED, lod1="keep", notes="MEDINA MARK: zellige wall fountain")
PIECES["wall_qamariya_k"] = _w("wall", wall_qamariya(), TOW, notes="TOWER HOUSE: gypsum-framed window, glowing fanlight")

for th, t in (("t", T), ("k", K)):
    PIECES[f"corner_quoin_{th}"] = _w("corner", corner_quoin(t), BOTH, lod1="drop", collide=False)
for th, t in (("t", T), ("k", K)):
    PIECES[f"plinth_{th}"] = _w("wall", plinth(t), BOTH, lod1="box", notes="base course: y 0 down 2 m, fills the gap over a sloping deck")
    PIECES[f"corner_in_{th}"] = _w("corner", corner_in(t), BOTH, lod1="drop", notes="inner corner filler: the EMPTY cell in +X/+Z")
for k in ("straight", "out", "in"):
    PIECES[f"kerb_{k}"] = _w("edge", kerb(k), BOTH, lod1="box", kind="water_edge",
                             notes="pond kerb on a cell edge, water on +Z; y 0 = the deck; the runtime draws the water")
PIECES["corner_round_k"] = _w("corner", corner_round(), MED, lod1="keep", notes="rounded mud corner (cell in -X/-Z)")
PIECES["corner_chamfer_k"] = _w("corner", corner_chamfer(), BOTH, lod1="keep")
PIECES["corner_column"] = _w("corner", corner_column(), BOTH, lod1="keep")

PIECES["roof_terrace"] = _w("cell", roof_terrace(), BOTH, kind="roof")
PIECES["roof_tin"] = _w("cell", roof_tin(), KOW, kind="roof")
PIECES["floor_slab"] = _w("cell", floor_slab(), BOTH, kind="slab", notes="the floor under an overhang / between storeys where seen")
for th, t in (("t", T), ("k", K)):
    PIECES[f"edge_parapet_plain_{th}"] = _w("edge", edge_parapet(t, "plain"), BOTH)
PIECES["edge_parapet_crenel_k"] = _w("edge", edge_parapet(K, "crenel"), TOW, lod1="keep", notes="stepped merlons")
PIECES["edge_parapet_rounded_k"] = _w("edge", edge_parapet(K, "rounded"), TOW, lod1="keep", notes="Shibam soft white merlons")
PIECES["edge_parapet_jali_k"] = _w("edge", edge_parapet(K, "jali"), BOTH, lod1="keep")
PIECES["edge_rail_t"] = _w("edge", edge_parapet(T, "rail"), KOW, lod1="drop")
PIECES["edge_eave_tile_green"] = _w("edge", edge_eave("tile_green"), MED, lod1="keep", notes="sacred buildings only")
PIECES["edge_eave_tin"] = _w("edge", edge_eave("tin"), BOTH, lod1="keep")
PIECES["crown_band"] = _w("edge", crown_band(), TOW, lod1="keep", notes="white gypsum line under a roof (y -0.45..0)")
PIECES["dome_cap"] = _w("cell", dome_cap(), BOTH, lod1="keep", kind="crown", notes="civic only (mosque, bath)")
PIECES["green_hip"] = _w("cell", green_hip(), MED, lod1="keep", kind="crown", notes="sacred roof")

for k in ("main", "lane", "plaza", "court"):
    PIECES[f"pave_{k}"] = _w("cell", pave(k), BOTH, kind="ground")
PIECES["pave_garden"] = _w("cell", pave_garden(), BOTH, kind="ground", notes="lawn bed with a kerb (public green)")
PIECES["step_low_1"] = _w("cell", step_low(1), BOTH, collide="ramp", kind="stair", notes="one 0.2 m riser at the cell's middle, along +Z (ramped streets)")
PIECES["step_low_4"] = _w("cell", step_low(4), BOTH, collide="ramp", kind="stair", notes="0.8 m in four 0.2 m risers along +Z (ramped streets)")
PIECES["steps_up"] = _w("cell", steps_up(), BOTH, collide="ramp", kind="stair", notes="1.6 m up along +Z")
PIECES["stair_run"] = _w("cell", stair_run(), BOTH, collide="ramp", kind="stair", span=(1, 2), notes="3.2 m up over 6 m along +Z (two cells)")
PIECES["stair_spiral"] = _w("cell", stair_spiral(), KOW, collide=False, kind="stair", notes="decor; no walk")
PIECES["ladder"] = _w("wall", ladder(), KOW, lod1="drop", collide=False, kind="stair")
for k in ("plank", "timber", "steel"):
    PIECES[f"bridge_{k}"] = _w("cell", bridge(k), KOW if k == "plank" else BOTH, kind="bridge", lod1="keep")
PIECES["sabat_beams"] = _w("cell", sabat_beams(), MED, kind="slab", lod1="keep", notes="MEDINA MARK: under a room bridging a lane")
PIECES["shoring_beam"] = _w("cell", shoring_beam(), MED, kind="decor", lod1="drop", collide=False, notes="MEDINA MARK: across a lane")
PIECES["alley_ceiling"] = _w("cell", alley_ceiling(), KOW, kind="ceiling", lod1="drop", collide=False, notes="KOWLOON: y 0 = the ceiling")
PIECES["arcade_pier"] = _w("cell", arcade_pier(), BOTH, kind="decor")
PIECES["fountain_riad"] = _w("cell", fountain_riad(), MED, kind="decor", lod1="drop", notes="MEDINA MARK")
for part in ("base", "shaft", "top"):
    PIECES[f"minaret_{part}"] = _w("cell", minaret(part), MED, kind="tower", lod1="keep", notes="MEDINA MARK: square Almohad minaret")

PIECES["int_floor"] = _w("cell", int_floor(), BOTH, kind="interior", lod1="drop")
PIECES["int_ceiling"] = _w("cell", int_ceiling(), BOTH, kind="interior", lod1="drop", collide=False)
PIECES["int_counter"] = _w("cell", int_counter(), BOTH, kind="interior", lod1="drop")
PIECES["int_shelves"] = _w("cell", int_shelves(), BOTH, kind="interior", lod1="drop")
PIECES["int_table_set"] = _w("cell", int_table_set(), BOTH, kind="interior", lod1="drop", collide=False)
PIECES["int_bed"] = _w("cell", int_bed(), BOTH, kind="interior", lod1="drop")
PIECES["int_lamp"] = _w("cell", int_lamp(), BOTH, kind="interior", lod1="drop", collide=False)

PIECES["ov_ac"] = _w("wall", ov_ac(), BOTH, kind="overlay", lod1="drop", collide=False, notes="hung on a face at any height")
PIECES["ov_tank"] = _w("cell", ov_tank(), BOTH, kind="overlay", lod1="keep", collide=False)
PIECES["ov_pipe_run"] = _w("wall", ov_pipe_run(), BOTH, kind="overlay", lod1="drop", collide=False)
PIECES["ov_cables"] = _w("cell", ov_cables(), BOTH, kind="overlay", lod1="drop", collide=False)
PIECES["ov_sign_blade"] = _w("wall", ov_sign_blade(), BOTH, kind="sign", lod1="keep", collide=False)
PIECES["ov_sign_box"] = _w("wall", ov_sign_box(), BOTH, kind="sign", lod1="drop", collide=False)
PIECES["ov_sign_board"] = _w("wall", ov_sign_board(), BOTH, kind="sign", lod1="drop", collide=False)
PIECES["ov_sign_arm"] = _w("wall", ov_sign_arm(), KOW, kind="sign", lod1="keep", collide=False, notes="KOWLOON MARK")
PIECES["ov_lantern"] = _w("wall", ov_lantern(), MED, kind="overlay", lod1="drop", collide=False)
PIECES["ov_festoon"] = _w("cell", ov_festoon(), BOTH, kind="overlay", lod1="drop", collide=False)
PIECES["ov_laundry"] = _w("wall", ov_laundry(), BOTH, kind="overlay", lod1="drop", collide=False)
for k in ("a", "b", "c"):
    PIECES[f"ov_shack_{k}"] = _w("cell", ov_shack(k), KOW, kind="overlay", lod1="keep", collide=True)
PIECES["ov_antennas"] = _w("cell", ov_antennas(), KOW, kind="overlay", lod1="drop", collide=False)
PIECES["ov_dish"] = _w("cell", ov_dish(), BOTH, kind="overlay", lod1="drop", collide=False)
PIECES["ov_awning_cane"] = _w("cell", ov_awning_cane(), MED, kind="overlay", lod1="drop", collide=False)
PIECES["ov_fluoro"] = _w("wall", ov_fluoro(), KOW, kind="overlay", lod1="drop", collide=False)
PIECES["ov_playground"] = _w("cell", ov_playground(), KOW, kind="overlay", lod1="keep", collide=False, notes="KOWLOON MARK")
PIECES["ov_stall"] = _w("cell", ov_stall(), BOTH, kind="overlay", lod1="drop", collide=True)
PIECES["ov_planter"] = _w("wall", ov_planter(), BOTH, kind="overlay", lod1="drop", collide=False)


# civ palettes (linear-ish sRGB hex per slot; variants = the placement's palette index, 0..3) -- research r1 / r2
PALETTES = {
    "maghrebi_medina": [
        {"wall": "#d6c19c", "trim": "#f3eee0", "frame": "#6b4a2f", "glass": "#26343c", "screen": "#7a5634", "roof": "#2f7d4f",
         "metal": "#3a3632", "fabric": "#b8573d", "emissive": "#ffd890", "tile": "#2d6fb0", "water": "#3d7f8c", "ground": "#b9a37f", "plant": "#5b7f3a"},
        {"wall": "#c46a4f", "trim": "#e8d9c0", "frame": "#5c3d26", "glass": "#26343c", "screen": "#6b4a2f", "roof": "#2f7d4f",
         "metal": "#3a3632", "fabric": "#d9a441", "emissive": "#ffcf7a", "tile": "#1f8a70", "water": "#3d7f8c", "ground": "#b88a6a", "plant": "#5b7f3a"},
        {"wall": "#f3f1ea", "trim": "#2d6fb0", "frame": "#3d5a7a", "glass": "#26343c", "screen": "#2d6fb0", "roof": "#2f7d4f",
         "metal": "#3a3632", "fabric": "#2d6fb0", "emissive": "#ffe2a8", "tile": "#2d6fb0", "water": "#3d7f8c", "ground": "#d8d2c4", "plant": "#5b7f3a"},
        {"wall": "#c9a978", "trim": "#f3eee0", "frame": "#6b4a2f", "glass": "#26343c", "screen": "#7a5634", "roof": "#2f7d4f",
         "metal": "#3a3632", "fabric": "#8a3a3a", "emissive": "#ffd890", "tile": "#c9a34a", "water": "#3d7f8c", "ground": "#a89070", "plant": "#5b7f3a"},
    ],
    "kowloon_walled": [
        {"wall": "#8a8f86", "trim": "#b9b0a0", "frame": "#6e6a60", "glass": "#3b4a50", "screen": "#5d6460", "roof": "#77736a",
         "metal": "#8c3f2a", "fabric": "#a3c2b5", "emissive": "#ff4a2a", "tile": "#c8d8d0", "water": "#3b5a5a", "ground": "#6e6b64", "plant": "#4f7a3a"},
        {"wall": "#a3c2b5", "trim": "#d8d0bc", "frame": "#5d6460", "glass": "#3b4a50", "screen": "#4a5050", "roof": "#6e6a60",
         "metal": "#7a4a30", "fabric": "#e0c05a", "emissive": "#3fe0ff", "tile": "#e8e0d0", "water": "#3b5a5a", "ground": "#6e6b64", "plant": "#4f7a3a"},
        {"wall": "#b9b0a0", "trim": "#8a8f86", "frame": "#4a4a46", "glass": "#3b4a50", "screen": "#5d6460", "roof": "#77736a",
         "metal": "#8c3f2a", "fabric": "#c85a5a", "emissive": "#ff3fa4", "tile": "#d0c4a8", "water": "#3b5a5a", "ground": "#6e6b64", "plant": "#4f7a3a"},
        {"wall": "#6e6a60", "trim": "#a3a59a", "frame": "#3e3c38", "glass": "#3b4a50", "screen": "#5d6460", "roof": "#5e5a52",
         "metal": "#9a5a32", "fabric": "#7aa0c8", "emissive": "#2bff88", "tile": "#b8c8c0", "water": "#3b5a5a", "ground": "#5e5b54", "plant": "#4f7a3a"},
    ],
}


# batch 2: the kerb post and the other families' first marks, default palettes for every family
import pieces_b2  # noqa: E402,F401
