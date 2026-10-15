"""pieces_marks.py -- warren kit batch 3: the civilization MARK pieces, rebuilt to carry their culture at a glance.

Marks are used sparingly (a few per street front), so the budget goes here: 400-900 tris a piece, where shared walls
stay at 30-300.  Each is checked against its research doc (research/sky_islands/warrens r1 / r2 / r3):

  newar             wall_newar_window_k (tikijhya: diagonal lattice, three stepped frames, carved bead band, lintel
                    and sill run out into curled 'ears', a niche frieze), wall_newar_sanjhya_k (the three-panel
                    window under a torana), roof_pagoda (three hip tiers, upturned corners, carved struts, bells,
                    a gilt gajur), edge_eave_pagoda (tiled eave on carved struts, corners swept up)
  yemeni_tower      wall_gypsum_window_k (double white gypsum frame, the qamariya fanlight in gypsum tracery,
                    frieze lines and a triangle relief), wall_yemeni_mafraj_k (the top-floor row of three
                    qamariya windows), band_brick_relief (zigzag + chequer brick relief between frieze lines)
  hejazi_roshan     wall_roshan_t / _k (the painted teak oriel on three carved corbels: carved apron, lattice
                    panels front and sides, louvred band, cornice with manqabi cresting, hood)
  caucasian_balcony wall_tbilisi_balcony_t (posts, carved corbels, a fretwork apron cut with diamonds, the
                    shushabandi glazing with a stained-glass transom, a scalloped pelmet, a tin roof)
  hanseatic_gable   edge_gable_step / _neck / _bell (true outlines with a stone coping, gable windows with shutters,
                    the hatch column, hoist beam + pulley + hook, wall anchors, finials / scrolls / pediment)
  ottoman_timber    wall_jetty_t (the upper storey 0.9 m out on curved corbels, clapboard and timber bands, ranked
                    sash windows, a kafes, and the cumba: a three-sided glazed oriel 0.7 m further on its own corbels)
  japan_yokocho     wall_noren_t (koshi lattice door, split noren with a crest, a lit lightbox over the door, a pair
                    of ribbed chochin, an andon sign), wall_sign_column_t (the zakkyo's vertical stack of lit
                    signboards on a fin, a storey per piece), ov_chochin_string (ribbed red lanterns, black caps)
  chongqing_cliff   stilt_frame (round poles on stone footings, X-braced, tie beams, cantilevered joists carrying a
                    gallery), stilt_house (the diaojiaolou: timber house, lattice windows, gallery, flying eaves)
  andean_neo        wall_cholet_front_t (mirror glass in nested stepped zigzag frames of clashing colour, chakana
                    crosses, columns with stepped capitals, LED edges, a stepped crest)

Two new SLOTS, accent and accent2: a family's bright paint (roshan green, cholet magenta / lime, Tbilisi turquoise,
gilt) -- solid vertex colour like wall/trim, read from the palette like every other slot.
"""
import math

from geom import Mesh, _dedupe, rot_y
from pieces import BAY, HB, K, PALETTES, PIECES, ST, T, _lattice, _rect, _strip, _w, _wall


# ------------------------------------------------------------------ helpers
def _off(outline, d):
    """an outline grown (d > 0) or shrunk (d < 0) with MITRED corners (rounded ones cost a fan of points)"""
    from shapely.geometry import Polygon
    g = Polygon(outline).buffer(d, join_style=2, mitre_limit=3.0)
    if g.geom_type != "Polygon":
        g = max(g.geoms, key=lambda q: q.area)
    return _dedupe([tuple(p) for p in list(g.exterior.coords)[:-1]])


def _ring(m, x0, y0, x1, y1, w, z0, z1, slot, shade=1.0):
    """a rectangular frame w wide OUTSIDE the rect (x0, y0)-(x1, y1), standing z0..z1: one solid annulus; its hole a
    hair wider than the rect and its back sunk a centimetre (so it never shares an edge with the wall or a frame
    inside it)"""
    e = 0.005
    m.wall_cut(_rect(x0 - w, y0 - w, x1 + w, y1 + w), [_rect(x0 - e, y0 - e, x1 + e, y1 + e)], z0 - 0.01, z1, slot, shade)


def _beads(m, x0, x1, y0, y1, z0, z1, n, slot, shade=1.0):
    """a carved band: n blocks in a row with gaps (reads as carving from the lane)"""
    step = (x1 - x0) / n
    for k in range(n):
        a = x0 + k * step + step * 0.18
        m.box((a, y0, z0), (a + step * 0.64, y1, z1), slot, shade * (0.9 if k % 2 else 1.0), skip=("z-",))


def _diag(m, x0, y0, x1, y1, z, step, bar, slot):
    """a diagonal lattice (Newar tikijhya, kafes): two sets of 45-degree flat bars clipped to the rect"""
    w, h = x1 - x0, y1 - y0
    for sgn, dz in ((1, 0.0), (-1, 0.004)):
        c = -h + step / 2
        while c < w:
            xa, xb = max(0.0, c), min(w, c + h)
            if xb - xa > 0.02:
                pa, pb = (xa, xa - c), (xb, xb - c)
                if sgn < 0:
                    pa, pb = (w - pa[0], pa[1]), (w - pb[0], pb[1])
                _strip(m, (x0 + pa[0], y0 + pa[1], z + dz), (x0 + pb[0], y0 + pb[1], z + dz), bar, (0, 0, 1), slot)
            c += step


def _corbel(m, x, ytop, dep, h, w, slot, shade=1.0, z0=0.0):
    """a curved bracket under a projection: its back on the wall (z0), top at ytop reaching dep out, a cove beneath"""
    prof = [(0.0, ytop), (0.0, ytop - h)]
    for k in range(1, 6):
        a = math.pi / 2 * k / 6
        prof.append((dep - dep * math.cos(a), ytop - h + (h - 0.1) * math.sin(a)))   # sweeps out and up
    prof += [(dep, ytop - 0.1), (dep, ytop)]
    sub = Mesh()
    sub.prism_xy(_dedupe(prof), [], -w / 2, w / 2, slot, shade)
    m.add(sub, lambda p: (x - p[2], p[1], z0 + p[0]))          # profile x -> out (+Z); a rotation, not a mirror


def _place(m, sub, deg, dx=0.0, dy=0.0, dz=0.0):
    r = rot_y(deg)
    m.add(sub, lambda p: (lambda q: (q[0] + dx, q[1] + dy, q[2] + dz))(r(p)))


def _hip(m, a, b, y0, y1, lift=0.3, flare=0.2, body=None, cap=True, slot="roof", under="frame"):
    """a hip roof tier: the eave a half-wide at y0, its corners swept up by lift and out by flare, rising (concave) to a
    square b half-wide at y1; a soffit back to the body (half-width body) beneath"""
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    nrm = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def ring(hw, y, lf, fl):
        pts = []
        for k in range(4):
            (sx, sz), (tx, tz) = sq[k], sq[(k + 1) % 4]
            for f in (0.0, 0.3, 0.7):
                x, z = sx + (tx - sx) * f, sz + (tz - sz) * f
                pts.append((x * (hw + fl), y + lf, z * (hw + fl)) if f == 0.0 else (x * hw, y, z * hw))
        return pts
    o = ring(a, y0, lift, flare)
    mid = ring(a * 0.55 + b * 0.45, y0 + (y1 - y0) * 0.3, lift * 0.3, flare * 0.3)
    top = ring(b, y1, 0.0, 0.0)
    u = ring(body if body is not None else b, y0 + 0.08, 0.0, 0.0)
    for j in range(12):
        k, jn = j // 3, (j + 1) % 12
        nx, nz = nrm[k]
        m.quad_facing(o[j], o[jn], mid[jn], mid[j], (nx, 1.2, nz), slot)
        m.quad_facing(mid[j], mid[jn], top[jn], top[j], (nx, 1.6, nz), slot, 0.95)
        m.quad_facing(o[j], o[jn], u[jn], u[j], (0, -1, 0), under, 0.55)
    if cap and b > 0.01:
        m.quad_facing(top[0], top[3], top[6], top[9], (0, 1, 0), slot)
    return o


def _crest(m, x0, x1, y, h, z, n, slot):
    """a row of little triangles standing on a line (manqabi cresting, Yemeni relief)"""
    step = (x1 - x0) / n
    for k in range(n):
        a = x0 + k * step
        m.tri_facing((a, y, z), (a + step, y, z), (a + step / 2, y + h, z), (0, 0, 1), slot)


# ------------------------------------------------------------------ Newar (r1_newar)
def _newar_frames(m, x0, y0, x1, y1):
    """three stepped frames round an opening, the innermost standing proudest, a bead band in the middle one"""
    _ring(m, x0, y0, x1, y1, 0.07, 0.0, 0.14, "frame")
    _ring(m, x0 - 0.07, y0 - 0.07, x1 + 0.07, y1 + 0.07, 0.09, 0.0, 0.09, "frame", 0.85)
    _ring(m, x0 - 0.16, y0 - 0.16, x1 + 0.16, y1 + 0.16, 0.06, 0.0, 0.05, "frame", 0.7)
    _beads(m, x0 - 0.12, x1 + 0.12, y1 + 0.085, y1 + 0.145, 0.09, 0.12, 9, "frame", 0.9)


def _newar_lintel(m, xl, xr, y, z=0.18, ears=0.22, up=True, slot="frame"):
    """a lintel (or sill) run out well past the jambs, its ends curled into carved 'ears' (up for the lintel)"""
    s = 1 if up else -1
    m.box((xl, y - 0.09, 0.0), (xr, y + 0.09, z), slot, skip=("z-",))
    for x0, x1, xc0, xc1 in ((xl, xl + 0.16, xl, xl + 0.08), (xr - 0.16, xr, xr - 0.08, xr)):
        ya, yb = sorted((y + s * 0.09, y + s * (0.09 + ears * 0.6)))
        m.box((x0, ya, 0.0), (x1, yb, z * 0.9), slot, 0.9, skip=("z-",))
        ya, yb = sorted((y + s * (0.09 + ears * 0.6), y + s * (0.09 + ears)))
        m.box((xc0, ya, 0.0), (xc1, yb, z * 0.75), slot, 0.8, skip=("z-",))


def wall_newar_window():
    """the tikijhya: the carved black window of the Kathmandu valley -- a fine diagonal lattice, three stepped frames,
    a carved bead band, lintel and sill run out into curled ears, a niche frieze over it"""
    def b():
        x0, y0, x1, y1 = -0.5, 1.0, 0.5, 2.15
        m = _wall(K, [_rect(x0, y0, x1, y1)], reveal="frame")
        m.pane(x0, y0, x1, y1, -0.34)
        _diag(m, x0, y0, x1, y1, -0.08, 0.13, 0.03, "frame")
        _newar_frames(m, x0, y0, x1, y1)
        _newar_lintel(m, -1.3, 1.3, y1 + 0.35, up=True)
        _newar_lintel(m, -1.15, 1.15, y0 - 0.3, z=0.15, up=False)
        m.box((-0.95, y1 + 0.44, 0.0), (0.95, y1 + 0.74, 0.04), "frame", 0.6, skip=("z-",))      # the niche frieze
        _beads(m, -0.9, 0.9, y1 + 0.48, y1 + 0.7, 0.04, 0.1, 7, "frame", 0.85)
        m.box((-1.05, y1 + 0.74, 0.0), (1.05, y1 + 0.82, 0.13), "frame", skip=("z-",))
        return m
    return b


def wall_newar_sanjhya():
    """the sanjhya: the three-panel window (a taller middle light), carved columns between, a torana tympanum over the
    middle, one long lintel with ears; diagonal lattices in all three"""
    def b():
        ops = [(-1.05, 1.0, -0.6, 2.0), (-0.38, 1.0, 0.38, 2.25), (0.6, 1.0, 1.05, 2.0)]
        m = _wall(K, [_rect(*o) for o in ops], reveal="frame")
        for x0, y0, x1, y1 in ops:
            m.pane(x0, y0, x1, y1, -0.34)
            _diag(m, x0, y0, x1, y1, -0.08, 0.13, 0.03, "frame")
            _ring(m, x0, y0, x1, y1, 0.06, 0.0, 0.12, "frame")
        for x in (-0.6, 0.38):                                                            # carved columns
            m.box((x + 0.06, 0.95, 0.0), (x + 0.16, 2.3, 0.16), "frame", 0.8, skip=("z-",))
            _beads(m, x + 0.06, x + 0.16, 1.3, 1.4, 0.16, 0.19, 1, "frame")
            _beads(m, x + 0.06, x + 0.16, 1.85, 1.95, 0.16, 0.19, 1, "frame")
        _ring(m, -1.17, 0.88, 1.17, 2.37, 0.06, 0.0, 0.06, "frame", 0.7)
        ty = 2.43                                                                         # the torana over the middle
        fan = [(-0.5, ty), (0.5, ty)] + [(0.5 * math.cos(math.pi * k / 8), ty + 0.42 * math.sin(math.pi * k / 8)) for k in range(1, 8)]
        m.wall_cut(fan, [], 0.0, 0.08, "frame", 0.75)
        m.wall_cut(_off(fan, 0.06), [_off(fan, -0.01)], 0.0, 0.11, "frame")
        m.cyl(0.0, 0.09, 0.07, ty + 0.12, ty + 0.3, "accent", n=6)                         # the gilt boss
        _newar_lintel(m, -1.45, 1.45, 2.37, z=0.18, ears=0.24, up=True)
        _newar_lintel(m, -1.3, 1.3, 0.72, z=0.15, ears=0.2, up=False)
        _beads(m, -1.2, 1.2, 0.58, 0.63, 0.0, 0.08, 12, "frame", 0.8)
        return m
    return b


def edge_eave_pagoda():
    """a deep tiled eave on carved struts, its ends swept up (Newar houses, Chinese and Thai fronts): on a roof edge"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -0.3), (HB, 0.22, 0.0), "frame", skip=("y-", "x-", "x+"))
        lo, hi = (-HB - 0.25, HB + 0.25)
        e0 = [(lo, 0.38, 1.25), (-HB + 0.5, 0.12, 1.2), (HB - 0.5, 0.12, 1.2), (hi, 0.38, 1.25)]     # the eave lip, ends up
        top = [(lo + 0.05, 0.85, -0.3), (-HB + 0.5, 0.8, -0.3), (HB - 0.5, 0.8, -0.3), (hi - 0.05, 0.85, -0.3)]
        for k in range(3):
            m.quad_facing(e0[k], e0[k + 1], top[k + 1], top[k], (0, 1, 0.6), "roof")
            m.quad_facing(e0[k], e0[k + 1], (top[k + 1][0], top[k + 1][1] - 0.05, -0.3), (top[k][0], top[k][1] - 0.05, -0.3), (0, -1, -0.4), "frame", 0.55)
        for k in range(12):                                                               # tile ribs down the slope
            f = (k + 0.5) / 12
            x = lo + (hi - lo) * f
            y_lip = 0.12 + (0.26 if f < 0.17 or f > 0.83 else 0.0) * (1 - min(f, 1 - f) / 0.17 if (f < 0.17 or f > 0.83) else 0)
            _strip(m, (x, y_lip + 0.03, 1.2), (x, 0.83, -0.28), 0.07, (0, 1, 0.6), "roof")
        m.box((lo, 0.06, 1.18), (hi, 0.16, 1.28), "frame", 0.7, skip=("x-", "x+"))           # the fascia
        for x in (-1.15, -0.4, 0.4, 1.15):                                                # carved struts
            m.tube((x, -1.25, 0.02), (x, 0.25, 0.95), 0.05, "frame", n=4)
            m.box((x - 0.08, -0.75, 0.25), (x + 0.08, -0.35, 0.5), "frame", 0.8)           # the carved figure
            m.box((x - 0.07, -1.35, 0.0), (x + 0.07, -1.2, 0.1), "frame", 0.7, skip=("z-",))
        return m
    return b


def roof_pagoda():
    """a three-tier Newar temple roof over a cell: hip tiers stepping in, corners swept up, carved struts under the
    lower two, bells at the corners, lit lattice panels in the drums, a gilt gajur pinnacle"""
    def b():
        m = Mesh()
        tiers = [(1.25, 0.0, 1.5, 2.05, 1.0, 2.2), (0.95, 2.2, 3.15, 1.6, 0.68, 3.75), (0.65, 3.75, 4.55, 1.15, 0.12, 5.35)]
        for i, (bh, yb, ye, a, b_, yt) in enumerate(tiers):
            m.box((-bh, yb, -bh), (bh, ye, bh), "wall", skip=("y-", "y+"))                    # the drum
            m.box((-bh - 0.04, ye - 0.22, -bh - 0.04), (bh + 0.04, ye - 0.08, bh + 0.04), "frame", 0.8, skip=("y-", "y+"))
            for k in range(4):                                                            # lit lattice panels
                sub = Mesh()
                w = bh * 0.55
                sub.quad_facing((-w, yb + 0.35, bh + 0.01), (w, yb + 0.35, bh + 0.01), (w, ye - 0.35, bh + 0.01), (-w, ye - 0.35, bh + 0.01), (0, 0, 1), "emissive")
                for j in range(1, 4):
                    x = -w + 2 * w * j / 4
                    _strip(sub, (x, yb + 0.35, bh + 0.02), (x, ye - 0.35, bh + 0.02), 0.03, (0, 0, 1), "frame")
                _strip(sub, (-w, (yb + ye) / 2, bh + 0.025), (w, (yb + ye) / 2, bh + 0.025), 0.03, (0, 0, 1), "frame")
                _place(m, sub, 90 * k)
            o = _hip(m, a, b_, ye, yt, lift=0.32 - 0.06 * i, flare=0.22, body=bh, cap=(i < 2))
            if i < 2:                                                                     # carved struts
                for k in range(4):
                    sub = Mesh()
                    for x in (-bh * 0.6, 0.0, bh * 0.6):
                        sub.tube((x, ye - 1.0, bh), (x, ye + 0.04, bh + (a - bh) * 0.62), 0.045, "frame", n=3)
                    _place(m, sub, 90 * k)
                for p in o[0::3]:                                                         # bells at the swept corners
                    m.cyl(p[0] * 0.97, p[2] * 0.97, 0.05, p[1] - 0.24, p[1] - 0.06, "accent", n=4, r1=0.02)
        m.lathe([(0.0, 5.25), (0.2, 5.3), (0.24, 5.45), (0.1, 5.6), (0.17, 5.78), (0.13, 5.95), (0.05, 6.05),
                 (0.08, 6.2), (0.0, 6.45)], "accent", n=8)                                  # the gajur
        return m
    return b


# ------------------------------------------------------------------ Yemen (r1_yemeni_tower)
def _qamariya(m, cx, top, r, slot_glow="emissive"):
    """a semicircular fanlight in gypsum tracery over a window: lit panes, a white outer band, radiating ribs and an
    inner ring"""
    fan = [(cx - r, top), (cx + r, top)] + [(cx + r * math.cos(math.pi * k / 10), top + r * math.sin(math.pi * k / 10)) for k in range(1, 10)]
    m.wall_cut(fan, [], -0.14, -0.1, slot_glow)
    m.wall_cut(_off(fan, 0.12), [fan], 0.0, 0.05, "trim", reveal_slot="trim")
    for k in range(1, 6):                                                                  # radiating ribs
        a = math.pi * k / 6
        _strip(m, (cx + r * 0.38 * math.cos(a), top + r * 0.38 * math.sin(a), -0.07), (cx + r * math.cos(a), top + r * math.sin(a), -0.07), 0.035, (0, 0, 1), "trim")
    for k in range(6):                                                                     # the inner ring
        a0, a1 = math.pi * k / 6, math.pi * (k + 1) / 6
        _strip(m, (cx + r * 0.38 * math.cos(a0), top + r * 0.38 * math.sin(a0), -0.065), (cx + r * 0.38 * math.cos(a1), top + r * 0.38 * math.sin(a1), -0.065), 0.035, (0, 0, 1), "trim")
    _strip(m, (cx - r, top + 0.015, -0.07), (cx + r, top + 0.015, -0.07), 0.04, (0, 0, 1), "trim")
    return fan


def _gypsum_window(m, x0, y0, x1, y1):
    m.pane(x0, y0, x1, y1, -0.34)
    _ring(m, x0, y0, x1, y1, 0.13, 0.0, 0.04, "trim")
    _ring(m, x0 + 0.05, y0 + 0.05, x1 - 0.05, y1 - 0.05, 0.03, -0.3, -0.2, "trim", 0.9)
    _strip(m, ((x0 + x1) / 2, y0 + 0.05, -0.19), ((x0 + x1) / 2, y1 - 0.05, -0.19), 0.04, (0, 0, 1), "trim")


def _yemeni_frieze(m, y, n=12):
    """the white frieze lines with a triangle relief between them (Sana'a storeys)"""
    m.box((-HB, y, 0.0), (HB, y + 0.05, 0.04), "trim", skip=("z-", "x-", "x+"))
    m.box((-HB, y + 0.25, 0.0), (HB, y + 0.3, 0.04), "trim", skip=("z-", "x-", "x+"))
    _crest(m, -HB, HB, y + 0.05, 0.2, 0.02, n, "trim")


def wall_gypsum_window():
    """a deep window in a heavy double white gypsum frame, crowned by its qamariya (gypsum tracery, lit glass that
    glows jewel-coloured at night), white frieze lines and a triangle relief over the storey"""
    def b():
        x0, y0, x1, y1 = -0.38, 0.75, 0.38, 1.85
        r, top = 0.38, y1 + 0.16
        fan = [(-r, top), (r, top)] + [(r * math.cos(math.pi * k / 10), top + r * math.sin(math.pi * k / 10)) for k in range(1, 10)]
        m = _wall(K, [_rect(x0, y0, x1, y1), fan])
        _gypsum_window(m, x0, y0, x1, y1)
        _qamariya(m, 0.0, top, r)
        m.box((-0.62, y0 - 0.3, -0.02), (0.62, y0 - 0.2, 0.05), "trim", skip=("z-",))       # the drip line
        _yemeni_frieze(m, 2.82, 14)
        return m
    return b


def wall_yemeni_mafraj():
    """the mafraj's front (the top-floor sitting room): a row of three windows each crowned by a qamariya, the middle
    one taller, white frames and a frieze over"""
    def b():
        ops = [(-1.15, 0.7, -0.65, 1.55, 0.25), (-0.3, 0.7, 0.3, 1.7, 0.3), (0.65, 0.7, 1.15, 1.55, 0.25)]
        cut, fans = [], []
        for x0, y0, x1, y1, r in ops:
            cx, top = (x0 + x1) / 2, y1 + 0.14
            fan = [(cx - r, top), (cx + r, top)] + [(cx + r * math.cos(math.pi * k / 10), top + r * math.sin(math.pi * k / 10)) for k in range(1, 10)]
            cut += [_rect(x0, y0, x1, y1), fan]
            fans.append((cx, top, r))
        m = _wall(K, cut)
        for (x0, y0, x1, y1, r), (cx, top, _) in zip(ops, fans):
            _gypsum_window(m, x0, y0, x1, y1)
            _qamariya(m, cx, top, r)
        m.box((-1.35, 0.42, -0.02), (1.35, 0.5, 0.05), "trim", skip=("z-",))
        _yemeni_frieze(m, 2.75, 14)
        return m
    return b


def band_brick_relief():
    """the brick-relief band between storeys (Sana'a): a zigzag and a chequer of projecting brick between two white
    frieze lines (0.6 m high; place on a wall bay at any height)"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, 0.0), (HB, 0.05, 0.04), "trim", skip=("z-", "x-", "x+"))
        m.box((-HB, 0.55, 0.0), (HB, 0.6, 0.04), "trim", skip=("z-", "x-", "x+"))
        for k in range(12):                                                               # zigzag
            x = -HB + 0.125 + k * 0.25
            ya, yb = (0.1, 0.3) if k % 2 == 0 else (0.3, 0.1)
            _strip(m, (x - 0.125, ya, 0.03), (x + 0.125, yb, 0.03), 0.06, (0, 0, 1), "wall")
        for k in range(15):                                                               # chequer of brick ends
            x = -HB + 0.05 + k * 0.2
            m.box((x, 0.36, 0.0), (x + 0.1, 0.48, 0.05), "wall", 1.1 if k % 2 else 0.8, skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ Hejaz (r1_hejazi_roshan)
def _panel_lattice(x0, y0, x1, y1, z, nx, ny):
    sub = Mesh()
    _lattice(sub, x0, y0, x1, y1, z - 0.05, z, nx, ny)
    sub.pane(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, z - 0.08)
    return sub


def wall_roshan(t):
    """the roshan: a painted teak oriel the height of the storey, 1.9 m wide and 0.85 m out on three carved corbels --
    a carved apron, lattice panels front and sides, a louvred band, a cornice with manqabi cresting under a hood;
    stacked storey on storey it covers the street front"""
    def b():
        m = _wall(t, [_rect(-0.8, 0.3, 0.8, 2.9)], reveal="accent")
        m.pane(-0.8, 0.3, 0.8, 2.9, -min(t * 0.5, 0.25))
        d, x0, x1 = 0.85, -0.95, 0.95
        for x in (-0.75, 0.0, 0.75):
            _corbel(m, x, 0.2, d - 0.05, 0.75, 0.14, "accent", 0.85)
        m.box((x0, 0.2, 0.0), (x1, 0.32, d), "accent", 0.9, skip=("z-",))                  # floor
        m.box((x0, 0.32, d - 0.06), (x1, 0.95, d), "accent", skip=("z-",))                 # the apron
        for k in range(4):                                                                 # carved apron panels
            x = x0 + 0.12 + k * 0.435
            m.box((x, 0.42, d), (x + 0.33, 0.85, d + 0.025), "screen", skip=("z-",))
            m.tri_facing((x + 0.06, 0.5, d + 0.03), (x + 0.27, 0.5, d + 0.03), (x + 0.165, 0.77, d + 0.03), (0, 0, 1), "accent")
        for k in range(3):                                                                 # lattice panels, front
            xa = x0 + 0.06 + k * 0.613
            m.add(_panel_lattice(xa, 0.95, xa + 0.6, 2.25, d, 5, 8))
        for side in (-1, 1):                         # lattice panels, sides (local +Z turned to face -X / +X)
            xa, xb = (0.08, d - 0.08) if side < 0 else (-(d - 0.08), -0.08)
            sub = _panel_lattice(xa, 0.95, xb, 2.25, 0.0, 4, 8)
            sub.box((xa - 0.08, 0.32, -0.06), (xb + 0.08, 0.95, 0.0), "accent", 0.9, skip=("z-",))
            _place(m, sub, 90 * side, dx=x1 if side > 0 else x0)
        for k in range(3):                                                                 # the louvred band
            y = 2.33 + k * 0.15
            _strip(m, (x0, y, d - 0.02), (x1, y, d - 0.02), 0.11, (0, 0.35, 1), "screen")
        for x in (x0, -0.33, 0.33, x1 - 0.07):                                             # mullion posts
            m.box((x, 0.32, d - 0.08), (x + 0.07, 2.75, d + 0.01), "accent", 0.85)
        m.box((x0 - 0.1, 2.75, 0.0), (x1 + 0.1, 2.95, d + 0.12), "accent", skip=("z-",))   # the cornice
        m.box((x0 - 0.05, 2.7, d), (x1 + 0.05, 2.75, d + 0.06), "trim", skip=("z-",))
        _crest(m, x0 - 0.1, x1 + 0.1, 2.95, 0.16, d + 0.12, 10, "accent")                  # manqabi cresting
        m.quad_facing((x0 - 0.15, 3.15, 0.0), (x1 + 0.15, 3.15, 0.0), (x1 + 0.15, 2.95, d + 0.05), (x0 - 0.15, 2.95, d + 0.05), (0, 1, 0.5), "accent", 0.8)
        return m
    return b


# ------------------------------------------------------------------ Tbilisi (r3_caucasian_balcony)
def wall_tbilisi_balcony():
    """the carved timber balcony of old Tbilisi, full width and 1.2 m out: posts and carved corbels, a fretwork apron
    cut with diamonds, the shushabandi glazing with a stained-glass transom, a scalloped pelmet, a red tin roof"""
    def b():
        m = _wall(T, [_rect(-0.5, 0.0, 0.5, 2.3)])
        m.box((-0.5, 0.0, -0.18), (0.5, 2.3, -0.14), "accent", 0.7)                         # the double door
        d, x0, x1 = 1.2, -HB, HB
        m.box((x0, -0.14, 0.0), (x1, 0.0, d), "accent", 0.85, skip=("z-",))                 # floor
        for x in (-1.2, 0.0, 1.2):
            _corbel(m, x, -0.14, d - 0.1, 0.8, 0.12, "accent", 0.8)
        dia = []                                                                            # fretwork apron
        for k in range(10):
            cx = x0 + 0.15 + k * 0.3
            dia.append([(cx, 0.22), (cx + 0.1, 0.45), (cx, 0.68), (cx - 0.1, 0.45)])
        m.wall_cut(_rect(x0, 0.0, x1, 0.9), dia, d - 0.04, d, "accent")
        m.box((x0, 0.9, d - 0.06), (x1, 0.98, d + 0.02), "accent", 0.9, skip=("z-",))       # the rail
        for side in (x0, x1 - 0.04):                                                        # side aprons
            m.box((side, 0.0, 0.0), (side + 0.04, 0.9, d - 0.04), "accent", 0.85)
        posts = [x0 + 0.04, -0.75, 0.0, 0.75, x1 - 0.04]
        for x in posts:                                                                     # turned posts
            m.cyl(x, d - 0.03, 0.045, 0.98, 2.6, "accent", n=6, caps=False)
            m.box((x - 0.07, 2.5, d - 0.1), (x + 0.07, 2.6, d + 0.04), "accent", 0.8)
        for a, c in zip(posts, posts[1:]):                                                  # the glazing between posts
            xa, xc = a + 0.05, c - 0.05
            m.pane(xa, 0.98, xc, 2.15, d - 0.05)
            n = 3
            for j in range(1, n):
                x = xa + (xc - xa) * j / n
                _strip(m, (x, 0.98, d - 0.04), (x, 2.15, d - 0.04), 0.035, (0, 0, 1), "accent")
            _strip(m, (xa, 1.6, d - 0.04), (xc, 1.6, d - 0.04), 0.035, (0, 0, 1), "accent")
            _strip(m, (xa, 2.17, d - 0.04), (xc, 2.17, d - 0.04), 0.05, (0, 0, 1), "accent")
            for j in range(4):                                                              # the stained transom
                xs = xa + (xc - xa) * j / 4
                slot = ("accent2", "emissive", "fabric", "emissive")[j]
                m.quad_facing((xs + 0.02, 2.2, d - 0.05), (xs + (xc - xa) / 4 - 0.02, 2.2, d - 0.05),
                              (xs + (xc - xa) / 4 - 0.02, 2.48, d - 0.05), (xs + 0.02, 2.48, d - 0.05), (0, 0, 1), slot)
        scal = [(x0, 2.6), (x1, 2.6), (x1, 2.82)]                                            # scalloped pelmet
        for k in range(12, 0, -1):
            xa = x0 + BAY * k / 12
            scal += [(xa, 2.82), (xa - BAY / 24, 2.7)]
        scal += [(x0, 2.82)]
        m.wall_cut(_dedupe(scal), [], d + 0.02, d + 0.06, "accent", 0.95)
        m.quad_facing((x0 - 0.1, 3.1, 0.0), (x1 + 0.1, 3.1, 0.0), (x1 + 0.1, 2.82, d + 0.25), (x0 - 0.1, 2.82, d + 0.25), (0, 1, 0), "roof")
        m.quad_facing((x0 - 0.1, 3.07, 0.0), (x1 + 0.1, 3.07, 0.0), (x1 + 0.1, 2.79, d + 0.25), (x0 - 0.1, 2.79, d + 0.25), (0, -1, 0), "accent", 0.6)
        return m
    return b


# ------------------------------------------------------------------ Hanseatic (r3_hanseatic_gable)
def _gable_profile(kind):
    if kind == "step":
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.9)]
        for k, (x, y) in enumerate(((1.15, 0.9), (1.15, 1.65), (0.8, 1.65), (0.8, 2.4), (0.45, 2.4), (0.45, 3.15))):
            p.append((x, y))
        p += [(0.25, 3.15), (0.25, 3.7), (-0.25, 3.7), (-0.25, 3.15)]
        p += [(-x, y) for x, y in reversed(((1.15, 0.9), (1.15, 1.65), (0.8, 1.65), (0.8, 2.4), (0.45, 2.4), (0.45, 3.15)))]
        p += [(-HB, 0.9)]
        return p
    if kind == "neck":
        p = [(-HB, 0.0), (HB, 0.0), (HB, 0.6)]
        p += [(0.65 + 0.85 * math.cos(math.pi / 2 * k / 5), 0.6 + 1.15 * math.sin(math.pi / 2 * k / 5)) for k in range(1, 6)]
        p += [(0.65, 3.0), (0.0, 3.7), (-0.65, 3.0)]
        p += [(-0.65 - 0.85 * math.cos(math.pi / 2 * (5 - k) / 5), 0.6 + 1.15 * math.sin(math.pi / 2 * (5 - k) / 5)) for k in range(0, 5)]
        p += [(-HB, 0.6)]
        return p
    p = [(-HB, 0.0), (HB, 0.0), (HB, 0.35)]                                                 # bell: an ogee to a crown
    for k in range(1, 9):
        f = k / 9
        x = HB - (HB - 0.55) * f
        y = 0.35 + 2.75 * (0.5 - 0.5 * math.cos(math.pi * f)) ** 0.8
        p.append((x, y))
    p += [(0.55, 3.25)] + [(0.55 * math.cos(math.pi * k / 6), 3.25 + 0.4 * math.sin(math.pi * k / 6)) for k in range(1, 6)] + [(-0.55, 3.25)]
    for k in range(8, 0, -1):
        f = k / 9
        p.append((-(HB - (HB - 0.55) * f), 0.35 + 2.75 * (0.5 - 0.5 * math.cos(math.pi * f)) ** 0.8))
    p += [(-HB, 0.35)]
    return p


def edge_gable(kind):
    """the gable over a narrow house front (stands on the roof top above its wall bay): a true stepped / neck / bell
    outline with a stone coping, two shuttered windows, the hatch column (loading door, upper hatch), the hoist beam
    with its pulley and hook, iron wall anchors, and the crown: a pinnacle (step), scrolls and a pediment (neck), a
    round crown (bell)"""
    def b():
        m = Mesh()
        t = T + 0.05
        prof = _dedupe(_gable_profile(kind))
        body = _off(prof, -0.06)
        ops = [_rect(-1.05, 0.35, -0.6, 1.2), _rect(0.6, 0.35, 1.05, 1.2), _rect(-0.3, 0.3, 0.3, 1.55), _rect(-0.22, 1.95, 0.22, 2.55)]
        if kind != "step":
            ops = ops[:3] + [_rect(-0.22, 1.95, 0.22, 2.55)]
        m.wall_cut(body, ops, -t, 0.0, "wall", reveal_slot="trim")
        m.wall_cut(prof, [_off(prof, -0.07)], -t - 0.03, 0.05, "trim", 0.95)               # the stone coping
        for x0, x1 in ((-1.05, -0.6), (0.6, 1.05)):                                         # windows + shutters
            m.pane(x0, 0.35, x1, 1.2, -t * 0.5)
            _strip(m, ((x0 + x1) / 2, 0.35, -t * 0.5 + 0.01), ((x0 + x1) / 2, 1.2, -t * 0.5 + 0.01), 0.03, (0, 0, 1), "trim")
            _strip(m, (x0, 0.8, -t * 0.5 + 0.01), (x1, 0.8, -t * 0.5 + 0.01), 0.03, (0, 0, 1), "trim")
            m.box((x0 - 0.04, 0.3, 0.0), (x1 + 0.04, 0.35, 0.06), "trim", skip=("z-",))
            for xs in (x0 - 0.24, x1 + 0.02):
                m.box((xs, 0.35, 0.0), (xs + 0.22, 1.2, 0.04), "accent", skip=("z-",))
        m.box((-0.3, 0.3, -t * 0.6), (0.3, 1.55, -t * 0.45), "accent", 0.85)                 # the loading door
        m.box((-0.22, 1.95, -t * 0.6), (0.22, 2.55, -t * 0.45), "accent", 0.85)              # the upper hatch
        _ring(m, -0.3, 0.3, 0.3, 1.55, 0.05, 0.0, 0.04, "trim")
        hy = 2.85 if kind != "step" else 3.25                                               # the hoist beam
        m.box((-0.08, hy, -t), (0.08, hy + 0.16, 1.0), "frame", skip=("z-",))
        m.cyl(0.0, 0.92, 0.07, hy - 0.12, hy, "metal", n=6)
        m.tube((0.0, hy - 0.12, 0.92), (0.0, 1.85, 0.92), 0.008, "metal", n=3)
        m.box((-0.04, 1.75, 0.88), (0.04, 1.85, 0.96), "metal")
        for x in (-1.2, 1.2):                                                               # wall anchors
            _strip(m, (x, 0.1, 0.01), (x, 0.55, 0.01), 0.05, (0, 0, 1), "metal")
            _strip(m, (x - 0.1, 0.33, 0.012), (x + 0.1, 0.33, 0.012), 0.04, (0, 0, 1), "metal")
        if kind == "step":
            for x, y in ((-1.15, 1.65), (1.15, 1.65), (-0.8, 2.4), (0.8, 2.4), (-0.45, 3.15), (0.45, 3.15), (-HB, 0.9), (HB, 0.9)):
                m.cyl(x - math.copysign(0.08, x), -t / 2, 0.06, y, y + 0.28, "trim", n=4, r1=0.0)
            m.cyl(0.0, -t / 2, 0.1, 3.7, 4.15, "trim", n=4, r1=0.0)
        elif kind == "neck":
            for x in (-1.12, 1.12):                                                         # the scrolls
                m.tube((x, 1.45, -t - 0.03), (x, 1.45, 0.1), 0.12, "trim", n=8)
            m.box((-0.75, 2.95, -t + 0.02), (0.75, 3.02, 0.08), "trim", skip=("y-",))
            m.lathe([(0.0, 3.7), (0.08, 3.75), (0.04, 3.95), (0.0, 4.05)], "trim", n=6, cz=-t / 2)
        else:
            m.tube((0.0, 3.3, -t - 0.02), (0.0, 3.3, 0.08), 0.16, "glass", n=8)             # the oculus
            m.lathe([(0.0, 3.65), (0.1, 3.68), (0.05, 3.9), (0.0, 4.0)], "trim", n=6, cz=-t / 2)
        return m
    return b


# ------------------------------------------------------------------ Ottoman (r3_ottoman_timber)
def _cumba_face(w, h, y0):
    """one face of the cumba (in its own frame: x across, +Z out): a sash window under a timber band"""
    sub = Mesh()
    sub.wall_cut(_rect(-w / 2, y0, w / 2, y0 + h), [_rect(-w / 2 + 0.08, y0 + 0.65, w / 2 - 0.08, y0 + h - 0.35)], -0.06, 0.0, "wall", reveal_slot="frame")
    sub.pane(-w / 2 + 0.08, y0 + 0.65, w / 2 - 0.08, y0 + h - 0.35, -0.03)
    _strip(sub, (-w / 2 + 0.08, y0 + h * 0.5 + 0.2, -0.02), (w / 2 - 0.08, y0 + h * 0.5 + 0.2, -0.02), 0.04, (0, 0, 1), "frame")
    sub.box((-w / 2, y0 + 0.58, 0.0), (w / 2, y0 + 0.65, 0.05), "trim", skip=("z-",))
    sub.box((-w / 2, y0 + h - 0.35, 0.0), (w / 2, y0 + h - 0.28, 0.05), "trim", skip=("z-",))
    for k in range(3):
        _strip(sub, (-w / 2, y0 + 0.15 + k * 0.15, 0.005), (w / 2, y0 + 0.15 + k * 0.15, 0.005), 0.03, (0, 0, 1), "frame")
    return sub


def wall_jetty():
    """the oversailing timber upper storey: the face 0.9 m out on curved corbels, clapboard and timber bands, a sash
    window each side (a kafes lattice on one), and the cumba -- a three-sided glazed oriel 0.6 m further out on its
    own corbels with a little hip roof"""
    def b():
        z = 0.9
        m = Mesh()
        win = [(-1.25, 0.85, -0.8, 2.45), (0.8, 0.85, 1.25, 2.45)]
        cum = (-0.7, 0.15, 0.7, 2.95)
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(*w) for w in win] + [_rect(*cum)], z - T, z, "wall", reveal_slot="frame")
        for k, (x0, y0, x1, y1) in enumerate(win):
            m.pane(x0, y0, x1, y1, z - T * 0.5)
            _strip(m, (x0, (y0 + y1) / 2, z - T * 0.5 + 0.01), (x1, (y0 + y1) / 2, z - T * 0.5 + 0.01), 0.04, (0, 0, 1), "frame")
            m.box((x0 - 0.05, y0 - 0.06, z), (x1 + 0.05, y0, z + 0.06), "trim", skip=("z-",))
            if k == 1:
                _diag(m, x0, y0, x1, (y0 + y1) / 2, z - 0.05, 0.12, 0.025, "screen")          # the kafes
        for y in (0.0, 0.7, 2.6, ST - 0.1):                                                # timber bands
            for xa, xb in ((-HB, cum[0]), (cum[2], HB)):
                m.box((xa, y, z), (xb, y + 0.08, z + 0.04), "frame", 0.85, skip=("z-",))
        for y in (0.3, 0.5, 2.85, 2.95):                                                   # clapboard lines
            for xa, xb in ((-HB, cum[0]), (cum[2], HB)):
                _strip(m, (xa, y, z + 0.005), (xb, y, z + 0.005), 0.025, (0, 0, 1), "frame")
        m.box((-HB, -0.18, -T), (HB, 0.0, z), "frame", 0.8, skip=("z-",))                  # soffit + joist ends
        for x in (-1.3, 0.0, 1.3):
            _corbel(m, x, -0.18, z - 0.05, 1.0, 0.15, "frame", 0.85)
        dz, wf = 0.6, 0.9                                                                   # the cumba
        ang = math.degrees(math.atan2(dz, 0.7 - wf / 2))
        side = math.hypot(dz, 0.7 - wf / 2)
        _place(m, _cumba_face(wf, 2.8, 0.15), 0.0, 0.0, 0.0, z + dz)
        for sgn in (-1, 1):
            mx = sgn * (0.7 + wf / 2) / 2
            _place(m, _cumba_face(side, 2.8, 0.15), sgn * ang, mx, 0.0, z + dz / 2)
        plan = [(-0.7, z), (0.7, z), (wf / 2, z + dz), (-wf / 2, z + dz)]
        m.prism_xz(plan, 0.05, 0.15, "frame", 0.8)
        m.prism_xz(plan, 2.95, 3.05, "frame", 0.8)
        for x in (-0.45, 0.45):
            _corbel(m, x, 0.05, dz, 0.6, 0.12, "frame", 0.75, z0=z)
        top = [(-0.85, 3.05, z - 0.1), (0.85, 3.05, z - 0.1), (wf / 2 + 0.15, 3.05, z + dz + 0.15), (-wf / 2 - 0.15, 3.05, z + dz + 0.15)]
        apex = [(-0.4, 3.35, z + 0.1), (0.4, 3.35, z + 0.1)]
        m.quad_facing(top[3], top[2], apex[1], apex[0], (0, 1, 1), "roof")
        m.tri_facing(top[0], top[3], apex[0], (-1, 1, 0), "roof", 0.9)
        m.tri_facing(top[1], top[2], apex[1], (1, 1, 0), "roof", 0.9)
        m.quad_facing(top[0], top[1], top[2], top[3], (0, -1, 0), "frame", 0.55)
        return m
    return b


# ------------------------------------------------------------------ Japan (r2_japan_yokocho)
def _chochin(m, x, y, z, r=0.17, h=0.44):
    """a red paper lantern: ribbed body (lit), black caps top and bottom, a tassel"""
    prof = [(r * 0.55, y - h / 2), (r * 0.85, y - h / 2 + 0.06), (r, y - 0.06), (r, y + 0.06), (r * 0.85, y + h / 2 - 0.06), (r * 0.55, y + h / 2)]
    m.lathe(prof, "emissive", n=6, cx=x, cz=z)
    m.cyl(x, z, r * 0.6, y + h / 2, y + h / 2 + 0.05, "frame", n=6, shade=0.6)
    m.cyl(x, z, r * 0.6, y - h / 2 - 0.05, y - h / 2, "frame", n=6, shade=0.6)
    m.cyl(x, z, 0.025, y - h / 2 - 0.2, y - h / 2 - 0.05, "accent", n=4, r1=0.01)


def ov_chochin_string():
    """red paper lanterns (chochin) strung across a lane at about 3 m (along X): ribbed, capped, tasselled"""
    def b():
        m = Mesh()
        pts = [(-HB + BAY * i / 6, 3.1 - 0.3 * (1 - (2 * i / 6 - 1) ** 2), 0.0) for i in range(7)]
        for a, c in zip(pts, pts[1:]):
            m.tube(a, c, 0.008, "metal", n=3)
        for p in pts[1:-1]:
            m.tube(p, (p[0], p[1] - 0.12, p[2]), 0.006, "metal", n=3)
            _chochin(m, p[0], p[1] - 0.37, p[2], r=0.13, h=0.34)
        return m
    return b


def _lightbox(m, x0, y0, x1, y1, z0, z1, nchar=3, vertical=False):
    """a lit sign box: glowing faces front and back, a dark frame, a few dark 'characters'"""
    m.box((x0, y0, z0), (x1, y1, z1), "emissive")
    for zz, nz in ((z1 + 0.004, 1), (z0 - 0.004, -1)):
        _strip(m, (x0, y0 + 0.02, zz), (x1, y0 + 0.02, zz), 0.04, (0, 0, nz), "frame")
        _strip(m, (x0, y1 - 0.02, zz), (x1, y1 - 0.02, zz), 0.04, (0, 0, nz), "frame")
        for k in range(nchar):
            if vertical:
                cy = y1 - (y1 - y0) * (k + 0.5) / nchar
                cx = (x0 + x1) / 2
                s = min(x1 - x0, (y1 - y0) / nchar) * 0.32
            else:
                cx = x0 + (x1 - x0) * (k + 0.5) / nchar
                cy = (y0 + y1) / 2
                s = min((x1 - x0) / nchar, y1 - y0) * 0.32
            _strip(m, (cx - s, cy + s * 0.5, zz), (cx + s, cy + s * 0.5, zz), s * 0.3, (0, 0, nz), "frame")
            _strip(m, (cx, cy + s, zz), (cx, cy - s, zz), s * 0.3, (0, 0, nz), "frame")
            _strip(m, (cx - s * 0.8, cy - s * 0.6, zz), (cx + s * 0.8, cy - s * 0.6, zz), s * 0.3, (0, 0, nz), "frame")


def wall_noren():
    """a yokocho bar front: the koshi lattice sliding door under a split noren curtain with a crest, a lit lightbox
    over the door, a pair of ribbed chochin, a little andon sign standing at the threshold"""
    def b():
        m = _wall(T, [_rect(-0.6, 0.0, 0.6, 2.1)])
        m.box((-0.6, 0.02, -0.16), (0.6, 2.1, -0.12), "frame", skip=())                     # the sliding door
        m.pane(-0.5, 0.95, 0.5, 2.0, -0.115)
        for k in range(1, 12):                                                             # koshi: dense uprights
            x = -0.5 + k / 12
            _strip(m, (x, 0.95, -0.105), (x, 2.0, -0.105), 0.022, (0, 0, 1), "frame")
        for y in (1.3, 1.65):
            _strip(m, (-0.5, y, -0.1), (0.5, y, -0.1), 0.022, (0, 0, 1), "frame")
        m.box((-0.7, 2.1, 0.0), (0.7, 2.2, 0.12), "frame", skip=("z-",))
        m.tube((-0.72, 2.16, 0.14), (0.72, 2.16, 0.14), 0.015, "frame", n=4)                # the noren rod
        for k in range(4):                                                                 # the split curtain
            x0 = -0.66 + k * 0.33
            m.quad_facing((x0, 2.15, 0.16), (x0 + 0.31, 2.15, 0.16), (x0 + 0.31, 1.45, 0.16), (x0, 1.45, 0.16), (0, 0, 1), "fabric")
            m.quad_facing((x0, 2.15, 0.155), (x0 + 0.31, 2.15, 0.155), (x0 + 0.31, 1.45, 0.155), (x0, 1.45, 0.155), (0, 0, -1), "fabric", 0.7)
        cr = [(0.0 + 0.13 * math.cos(math.tau * k / 8), 1.85 + 0.13 * math.sin(math.tau * k / 8)) for k in range(8)]
        m.wall_cut(cr, [], 0.16, 0.17, "accent")                                            # the crest (mon)
        _lightbox(m, -0.75, 2.3, 0.75, 2.75, 0.02, 0.18, nchar=4)
        for x in (-0.95, 0.95):
            _chochin(m, x, 2.05, 0.24, r=0.15, h=0.42)
            m.box((x - 0.02, 2.3, 0.0), (x + 0.02, 2.36, 0.24), "metal")
        m.box((1.0, 0.0, 0.35), (1.05, 0.25, 0.4), "frame")                                 # the andon on its foot
        _lightbox(m, 0.85, 0.25, 1.2, 0.95, 0.3, 0.45, nchar=2, vertical=True)
        return m
    return b


def wall_sign_column():
    """the zakkyo's sign column: a vertical stack of lit signboards on a fin at the bay's right edge, one storey per
    piece (stack them up the tower), boxed at 90 degrees to the facade so the lane reads them both ways"""
    def b():
        m = Mesh()
        x = HB - 0.25
        m.box((x - 0.03, 0.0, 0.0), (x + 0.03, ST, 0.1), "metal", skip=("y-", "y+"))
        for k in range(3):                                                                 # three boxes a storey
            y0 = 0.08 + k * 1.04
            sub = Mesh()
            _lightbox(sub, 0.12, y0, 0.98, y0 + 0.94, -0.13, 0.13, nchar=2, vertical=True)
            m.add(sub, lambda p, x=x: (x - p[2], p[1], p[0]))     # a rotation: the box's +X runs out of the wall
        return m
    return b


# ------------------------------------------------------------------ Chongqing (r2_chongqing_cliff)
def stilt_frame():
    """the diaojiaolou's stilts under a cell hung over the slope: round fir poles three storeys down on stone footings,
    X-braced on every face, tie beams, joists cantilevered out front carrying a railed gallery"""
    def b():
        m = Mesh()
        dn = 3 * ST
        for x in (-1.3, 1.3):
            for z in (-1.3, 1.3):
                m.cyl(x, z, 0.11, -dn + 0.4, 0.0, "frame", n=6, caps=False)
                m.box((x - 0.22, -dn, z - 0.22), (x + 0.22, -dn + 0.4, z + 0.22), "ground", 0.8, skip=("y-",))
        for k in range(3):
            y0, y1 = -dn + 0.4 + k * (dn - 0.4) / 3, -dn + 0.4 + (k + 1) * (dn - 0.4) / 3
            for z in (-1.3, 1.3):
                for a, c in (((-1.3, y0), (1.3, y1)), ((1.3, y0), (-1.3, y1))):
                    m.tube((a[0], a[1] + 0.15, z), (c[0], c[1] - 0.15, z), 0.04, "frame", n=4)
                m.box((-1.4, y1 - 0.14, z - 0.06), (1.4, y1, z + 0.06), "frame", 0.85)
            for x in (-1.3, 1.3):
                for a, c in (((-1.3, y0), (1.3, y1)), ((1.3, y0), (-1.3, y1))):
                    m.tube((x, a[1] + 0.15, a[0]), (x, c[1] - 0.15, c[0]), 0.04, "frame", n=4)
        for x in (-1.3, -0.45, 0.45, 1.3):                                                  # cantilevered joists
            m.box((x - 0.06, -0.22, -1.4), (x + 0.06, -0.08, 2.3), "frame", 0.8)
            m.tube((x, -1.6, 1.3), (x, -0.22, 2.2), 0.045, "frame", n=4)
        m.box((-HB, -0.08, 1.5), (HB, 0.0, 2.35), "frame", 0.9)                             # the gallery deck
        m.box((-HB, 0.95, 2.3), (HB, 1.02, 2.38), "frame", skip=())                         # its rail
        for k in range(13):
            x = -HB + 0.05 + k * 0.242
            m.box((x - 0.02, 0.0, 2.32), (x + 0.02, 0.95, 2.36), "frame", 0.85, skip=("y-", "y+"))
        return m
    return b


def stilt_house():
    """the diaojiaolou itself, on a cell (sits on stilt_frame or rock): a timber house with lattice windows, a railed
    gallery round the front, grey tile flying eaves with corners swept up, red lanterns under them"""
    def b():
        m = Mesh()
        h = 2.9
        m.box((-1.35, 0.0, -1.35), (1.35, h, 1.32), "wall", skip=("y-", "y+", "z+"))
        ops = [_rect(-1.1, 0.0, -0.4, 2.1), _rect(0.0, 0.95, 1.1, 2.1)]
        m.wall_cut(_rect(-1.36, 0.0, 1.36, h), ops, 1.31, 1.35, "wall", reveal_slot="frame")
        m.box((-1.1, 0.0, 1.2), (-0.4, 2.1, 1.24), "frame", 0.75)                           # a plank door
        m.pane(0.0, 0.95, 1.1, 2.1, 1.25)
        _lattice(m, 0.0, 0.95, 1.1, 2.1, 1.27, 1.33, 6, 5, slot="frame")
        for x in (-1.38, 1.31):                                                             # posts
            m.box((x, 0.0, 1.33), (x + 0.07, h, 1.41), "frame", 0.8)
        for y in (0.0, h - 0.12):
            m.box((-1.4, y, 1.35), (1.4, y + 0.12, 1.42), "frame", 0.85, skip=("z-",))
        sub = Mesh()                                                                        # side lattice windows
        sub.pane(-0.5, 1.0, 0.5, 2.0, 0.005)
        _lattice(sub, -0.5, 1.0, 0.5, 2.0, 0.01, 0.05, 5, 4, slot="frame")
        for deg in (90, -90):
            _place(m, sub, deg, dx=1.35 if deg == 90 else -1.35)
        m.box((-1.6, -0.1, 1.42), (1.6, 0.0, 2.2), "frame", 0.9, skip=())                   # the gallery
        m.box((-1.6, 0.95, 2.14), (1.6, 1.02, 2.22), "frame", skip=())
        for k in range(14):
            x = -1.55 + k * 0.238
            m.box((x - 0.02, 0.0, 2.16), (x + 0.02, 0.95, 2.2), "frame", 0.85, skip=("y-", "y+"))
        for x in (-1.55, 1.55):
            m.box((x - 0.05, 0.0, 2.12), (x + 0.05, h, 2.22), "frame", 0.8)
        _hip(m, 2.25, 0.5, h, h + 1.3, lift=0.4, flare=0.25, body=1.4, cap=False)
        m.box((-0.9, h + 1.25, -0.08), (0.9, h + 1.42, 0.08), "roof", 0.8, skip=("y-",))     # the ridge
        for x in (-1.15, 1.15):
            _chochin(m, x, h - 0.4, 2.1, r=0.14, h=0.38)
        return m
    return b


# ------------------------------------------------------------------ Andes (r3_andean_neo)
def _chakana(cx, cy, a, b):
    """the Andean step cross: arms a, steps b"""
    p = [(a, b), (a, -b), (b, -b), (b, -a), (-b, -a), (-b, -b), (-a, -b), (-a, b), (-b, b), (-b, a), (b, a), (b, b)]
    q = []
    for x, y in p:
        q.append((cx + x, cy + y))
    return q


def _zig_frame(x0, y0, x1, y1, step, n):
    """a rectangle whose top edge rises in n steps to the middle and back (a stepped Tiwanaku crest)"""
    cx = (x0 + x1) / 2
    w = (x1 - x0) / 2
    pts = [(x0, y0), (x1, y0), (x1, y1)]
    for k in range(1, n + 1):
        x = x1 - w * k / (n + 1)
        pts += [(x, y1 + step * (k - 1)), (x, y1 + step * k)]
    pts += [(cx, y1 + step * n)]
    for k in range(n, 0, -1):
        x = x0 + w * k / (n + 1)
        pts += [(x, y1 + step * k), (x, y1 + step * (k - 1))]
    pts += [(x0, y1)]
    return _dedupe(pts)


def wall_cholet_front():
    """a cholet's front (El Alto): mirror glass inside nested stepped frames of clashing colour, chakana crosses,
    columns with stepped capitals, LED edges, a stepped crest over the bay"""
    def b():
        m = Mesh()
        glass = _zig_frame(-0.85, 0.35, 0.85, 2.15, 0.12, 3)
        f1 = _off(glass, 0.1)
        f2 = _off(glass, 0.2)
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [f2], -T, 0.0, "tile", reveal_slot="tile")
        m.wall_cut(glass, [], -0.1, -0.07, "glass")
        m.wall_cut(f2, [f1], -0.1, 0.03, "accent")
        m.wall_cut(f1, [_off(glass, -0.005)], -0.1, 0.07, "accent2")
        for x in (-0.3, 0.3):                                                               # mullions
            _strip(m, (x, 0.35, -0.06), (x, 2.2, -0.06), 0.05, (0, 0, 1), "accent2")
        _strip(m, (-0.85, 1.25, -0.055), (0.85, 1.25, -0.055), 0.05, (0, 0, 1), "accent2")
        for x in (-1.32, 1.32):                                                             # columns + capitals
            m.box((x - 0.12, 0.0, 0.0), (x + 0.12, 2.6, 0.12), "trim", skip=("z-",))
            m.box((x - 0.16, 2.6, 0.0), (x + 0.16, 2.72, 0.16), "fabric", skip=("z-",))
            m.box((x - 0.2, 2.72, 0.0), (x + 0.2, 2.82, 0.2), "accent", skip=("z-",))
            m.box((x - 0.16, 0.0, 0.0), (x + 0.16, 0.12, 0.16), "fabric", skip=("z-", "y-"))
            m.wall_cut(_chakana(x, 1.5, 0.11, 0.04), [], 0.12, 0.16, "accent")              # chakana on the shaft
        for x in (-1.0, 1.0):                                                               # chakanas over the frame
            m.wall_cut(_chakana(x, 2.62, 0.17, 0.06), [], 0.0, 0.05, "fabric")
        crest = [(-HB, 2.85), (HB, 2.85), (HB, 2.95), (1.1, 2.95), (1.1, 3.05), (0.7, 3.05), (0.7, 3.12), (-0.7, 3.12),
                 (-0.7, 3.05), (-1.1, 3.05), (-1.1, 2.95), (-HB, 2.95)]
        m.wall_cut(crest, [], 0.0, 0.08, "fabric")
        ring = list(f2) + [f2[0]]
        for a, c in zip(ring, ring[1:]):                                                    # LED edges
            _strip(m, (a[0], a[1], 0.035), (c[0], c[1], 0.035), 0.025, (0, 0, 1), "emissive")
        return m
    return b


# ------------------------------------------------------------------ register (replacing batch 2's plainer marks)
Y, H, O, N, J, C, G, A, HS = (["yemeni_tower"], ["hejazi_roshan"], ["ottoman_timber"], ["newar"], ["japan_yokocho"],
                              ["chongqing_cliff"], ["caucasian_balcony"], ["andean_neo"], ["hanseatic_gable"])
PIECES["wall_gypsum_window_k"] = _w("wall", wall_gypsum_window(), Y, notes="YEMEN MARK: gypsum-framed window under a lit qamariya, frieze")
PIECES["wall_yemeni_mafraj_k"] = _w("wall", wall_yemeni_mafraj(), Y, notes="YEMEN MARK: top-floor mafraj, three qamariya windows")
PIECES["band_brick_relief"] = _w("wall", band_brick_relief(), Y + ["saharan_kasbah"], lod1="drop", collide=False, kind="overlay",
                                 notes="brick-relief band (0.6 m high, zigzag + chequer between white lines) on a facade at any height")
PIECES["wall_roshan_t"] = _w("wall", wall_roshan(T), H + ["cairene_mamluk"], lod1="keep", notes="HEJAZ MARK: painted teak oriel on corbels; stack it")
PIECES["wall_roshan_k"] = _w("wall", wall_roshan(K), H + ["cairene_mamluk"], lod1="keep", notes="HEJAZ MARK: painted teak oriel on corbels; stack it")
PIECES["wall_jetty_t"] = _w("wall", wall_jetty(), O + ["levantine_courtyard"], lod1="keep", notes="OTTOMAN MARK: storey 0.9 m out on corbels, cumba oriel")
PIECES["wall_newar_window_k"] = _w("wall", wall_newar_window(), N, notes="NEWAR MARK: tikijhya lattice window, stepped frames, eared lintel")
PIECES["wall_newar_sanjhya_k"] = _w("wall", wall_newar_sanjhya(), N, notes="NEWAR MARK: three-panel sanjhya under a torana (use on the 2nd floor)")
PIECES["edge_eave_pagoda"] = _w("edge", edge_eave_pagoda(), N + ["siam_khlong", "taipei_tiepi", "chongqing_cliff"], lod1="keep",
                                notes="deep tiled eave on carved struts, ends swept up")
PIECES["roof_pagoda"] = _w("cell", roof_pagoda(), N + ["siam_khlong"], lod1="keep", kind="crown", notes="NEWAR MARK: three-tier temple roof, struts, gajur")
PIECES["ov_chochin_string"] = _w("cell", ov_chochin_string(), J, lod1="drop", collide=False, kind="overlay", notes="JAPAN MARK: chochin across a lane (along X)")
PIECES["wall_noren_t"] = _w("wall", wall_noren(), J, notes="JAPAN MARK: koshi door, noren, lightbox, chochin pair, andon")
PIECES["wall_sign_column_t"] = _w("wall", wall_sign_column(), J + ["hk_neon_canyon", "taipei_tiepi"], lod1="keep", collide=False, kind="overlay",
                                  notes="JAPAN MARK: a storey of the vertical lit sign stack on a fin (stack up a tower)")
PIECES["stilt_frame"] = _w("cell", stilt_frame(), C, lod1="keep", collide=False, kind="slab", notes="CHONGQING MARK: X-braced stilts 3 storeys down, gallery out front")
PIECES["stilt_house"] = _w("cell", stilt_house(), C, lod1="keep", kind="crown", notes="CHONGQING MARK: diaojiaolou house with gallery and flying eaves (on stilt_frame)")
PIECES["wall_tbilisi_balcony_t"] = _w("wall", wall_tbilisi_balcony(), G, lod1="keep", notes="TBILISI MARK: carved balcony, fretwork, stained glass")
for k in ("step", "neck", "bell"):
    PIECES[f"edge_gable_{k}"] = _w("edge", edge_gable(k), HS, lod1="keep", kind="crown", notes=f"HANSEATIC MARK: {k} gable, coping, hatch column, hoist beam")
PIECES["wall_cholet_front_t"] = _w("wall", wall_cholet_front(), A, notes="ANDES MARK: mirror glass in stepped colour frames, chakanas, columns")


# ------------------------------------------------------------------ accent colours (the families' paint and gilt)
ACCENTS = {
    "newar": [("#c9a23a", "#7a2a1e")] * 4,                                    # gilt repoussé, sindoor red
    "yemeni_tower": [("#f4efe4", "#b0283a")] * 4,
    "hejazi_roshan": [("#6b4a2e", "#efe9dc"), ("#2f6b4f", "#efe9dc"), ("#2e5d8a", "#efe9dc"), ("#4f7a5a", "#efe9dc")],
    "caucasian_balcony": [("#3a9a9a", "#b0283a"), ("#6aa6cf", "#2a4a9a"), ("#7a8a4a", "#e0a030"), ("#6b4a2e", "#2a8a4a")],
    "hanseatic_gable": [("#2a4a32", "#f5f3ee"), ("#7a2a22", "#f5f3ee"), ("#2a3a5a", "#f5f3ee"), ("#2a4a32", "#d8b25a")],
    "ottoman_timber": [("#6b4a2e", "#efe6d2")] * 4,
    "japan_yokocho": [("#b02a24", "#1e1c1a")] * 4,
    "chongqing_cliff": [("#b02a24", "#d8a83a")] * 4,
    "andean_neo": [("#d6337a", "#9acd32"), ("#6a3a9a", "#f28a1e"), ("#25b5b0", "#d6337a"), ("#e0b030", "#6a3a9a")],
}
GLOW = {                                                                       # the emissive colour per variant
    "yemeni_tower": ["#ffb347", "#ff4a5a", "#4ade80", "#4a7aff"],             # amber, ruby, emerald, cobalt qamariya
    "caucasian_balcony": ["#ffb347", "#ff5a5a", "#5a8aff", "#7adf6a"],
    "japan_yokocho": ["#ff6a4a", "#ffe2b0", "#ff6a4a", "#fff0d0"],             # red chochin / warm lightbox
    "andean_neo": ["#ff4ad0", "#4affea", "#c8ff4a", "#ffb84a"],
    "newar": ["#ffb24a"] * 4,
}
CURATED = {                                                                    # wall / roof / frame / trim per variant
    "yemeni_tower": dict(wall=["#8a5a3c", "#9c6a45", "#a07850", "#4a4743"], roof=["#a07850"], trim=["#f2efe6"]),
    "hejazi_roshan": dict(wall=["#efe9dc", "#e3d6bd", "#bcb5a5", "#f0e6c8"], roof=["#d8cfbd"]),
    "ottoman_timber": dict(wall=["#d9a441", "#9a3b2e", "#4f74a8", "#8fa58a"], roof=["#a8543a"], frame=["#5a3a26"]),
    "japan_yokocho": dict(wall=["#c9c4b8", "#8f8a80", "#5a4634", "#a8a49a"], roof=["#4a4a4e"], frame=["#2c2620"]),
    "chongqing_cliff": dict(wall=["#6b4a32", "#4a3324", "#7a5a3e", "#8a8a84"], roof=["#5a5a58"], frame=["#3a2a1e"]),
    "caucasian_balcony": dict(wall=["#a65a3a", "#efe9dc", "#d8c8a8", "#8a5a44"], roof=["#9a3a2a", "#6a6e72"]),
    "hanseatic_gable": dict(wall=["#7a3a2a", "#8c3b2a", "#ece6d6", "#d8b25a"], roof=["#5a3a2e"], trim=["#f5f3ee"]),
}
for civ, cur in CURATED.items():
    for i, v in enumerate(PALETTES.get(civ, [])):
        for k, cs in cur.items():
            v[k] = cs[i % len(cs)]
FAB = {"andean_neo": ["#25b5b0", "#9acd32", "#f28a1e", "#d6337a"]}
for civ, vs in PALETTES.items():
    for i, v in enumerate(vs):
        acc = ACCENTS.get(civ)
        v.setdefault("accent", acc[i % len(acc)][0] if acc else v.get("frame", "#4a3a2a"))
        v.setdefault("accent2", acc[i % len(acc)][1] if acc else v.get("trim", "#efe9dc"))
        if civ in GLOW:
            v["emissive"] = GLOW[civ][i % 4]
        if civ in FAB:
            v["fabric"] = FAB[civ][i % 4]
        if civ == "andean_neo":
            v["tile"] = ["#f28a1e", "#d6337a", "#6a3a9a", "#25b5b0"][i % 4]
            v["glass"] = "#9ab8c8"
