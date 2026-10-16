"""pieces_b2.py -- warren kit batch 2: the kerb corner post and the first signature pieces of the other civilization
families (research/sky_islands/warrens r1 / r2 / r3), plus default palettes for every family from its researched
colours.  Registered into pieces.PIECES / PALETTES (pieces.py imports this at its end).

Marks (each true to its research doc):
  yemeni_tower      wall_gypsum_window_k (white gypsum-framed window + small qamariya), band_brick_relief (zigzag)
  hejazi_roshan     wall_roshan_t / _k (the full-storey teak oriel: lattice, louvred bands, a carved crown)
  ottoman_timber    wall_jetty_t (the timber upper storey oversailing 0.6 m on diagonal brackets, a rank of windows)
  newar             wall_newar_window_k (the black carved window: stepped frames, a lattice, the lintel run out
                    beyond the jambs), edge_eave_pagoda (struts and a deep tiled eave), roof_pagoda (a two-tier temple
                    roof with a gilt finial)
  japan_yokocho     ov_chochin_string (red paper lanterns across a lane), wall_noren_t (a door under a split curtain
                    and a lantern pair)
  chongqing_cliff   stilt_frame (posts and bracing under a cell, three storeys down)
  caucasian_balcony wall_tbilisi_balcony_t (the full-width carved and glazed timber balcony)
  hanseatic_gable   edge_gable_step / _neck / _bell (the gable over a narrow house front, its hoist beam and loading
                    door)
  andean_neo        wall_cholet_front_t (a cholet's mirror glass in coloured geometric frames, LED edges)
"""
import json
import math
import os

from geom import Mesh, arch
from pieces import BAY, BOTH, HB, K, PALETTES, PIECES, ST, T, _cheap_window, _grow, _lattice, _rect, _strip, _w, _wall, _window

HERE = os.path.dirname(os.path.abspath(__file__))
WARRENS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "research", "sky_islands", "warrens"))


# ------------------------------------------------------------------ shared
def kerb_post():
    """the kerb's corner post: origin on the cell corner, the land in -X/-Z, its body inside the land cell"""
    def b():
        m = Mesh()
        m.box((-0.42, -0.4, -0.42), (0.0, 0.3, 0.0), "trim", skip=("y-",))
        m.box((-0.36, 0.3, -0.36), (-0.06, 0.38, -0.06), "trim", 0.9, skip=("y-",))
        return m
    return b


# ------------------------------------------------------------------ Yemen (r1_yemeni_tower)
def wall_gypsum_window():
    """a small deep window in a heavy white gypsum frame, a little qamariya over it (Sana'a)"""
    def b():
        w, y0, h = 0.7, 1.0, 1.0
        sq = _rect(-w / 2, y0, w / 2, y0 + h)
        top = y0 + h + 0.18
        fan = [(-0.3, top), (0.3, top)] + [(0.3 * math.cos(math.pi * k / 8), top + 0.3 * math.sin(math.pi * k / 8)) for k in range(1, 8)]
        m = _wall(K, [sq, fan])
        _window(m, K, -w / 2, y0, w / 2, y0 + h, sill=False, depth=0.28)
        m.wall_cut(fan, [], -0.34, -0.3, "emissive")
        m.wall_cut(_grow(sq, 0.16), [sq], 0.0, 0.035, "trim", reveal_slot="trim")
        m.wall_cut(_grow(fan, 0.12), [fan], 0.0, 0.035, "trim", reveal_slot="trim")
        m.box((-0.62, y0 - 0.32, -0.02), (0.62, y0 - 0.2, 0.05), "trim", skip=("z-",))       # the white drip line under it
        return m
    return b


def band_brick_relief():
    """a zigzag brick-relief band across a facade (place on a wall bay at any height): Yemeni tower floors"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, 0.0), (HB, 0.06, 0.04), "trim", skip=("z-",))
        m.box((-HB, 0.34, 0.0), (HB, 0.4, 0.04), "trim", skip=("z-",))
        for k in range(12):
            x = -HB + 0.125 + k * 0.25
            up = k % 2 == 0
            y0, y1 = (0.08, 0.32) if up else (0.32, 0.08)
            _strip(m, (x - 0.1, y0, 0.03), (x + 0.1, y1, 0.03), 0.05, (0, 0, 1), "wall")
        return m
    return b


# ------------------------------------------------------------------ Hejaz (r1_hejazi_roshan)
def wall_roshan(t):
    """the roshan: a teak oriel the height of the storey, 1.9 m wide and 0.9 m out -- a solid apron, a lattice middle,
    louvred bands, a carved crown; stacked storey on storey it covers the street front"""
    def b():
        m = _wall(t, [_rect(-0.8, 0.3, 0.8, 2.9)])
        m.pane(-0.8, 0.3, 0.8, 2.9, -min(t * 0.5, 0.25))
        d, x0, x1 = 0.9, -0.95, 0.95
        m.box((x0, 0.15, 0.0), (x1, 0.3, d), "frame", skip=("z-",))                         # floor
        m.box((x0, 0.3, d - 0.06), (x1, 0.95, d), "frame", skip=("z-",))                    # the apron
        for k in range(4):                                                                # carved apron panels
            x = x0 + 0.15 + k * 0.425
            m.box((x, 0.42, d), (x + 0.3, 0.83, d + 0.02), "screen", skip=("z-",))
        _lattice(m, x0, 0.95, x1, 2.25, d - 0.06, d, 8, 7)
        for k in range(3):                                                                # louvred band
            y = 2.32 + k * 0.17
            _strip(m, (x0, y, d - 0.02), (x1, y, d - 0.02), 0.12, (0, 0.3, 1), "screen")
        m.box((x0 - 0.08, 2.85, -0.0), (x1 + 0.08, 3.05, d + 0.12), "frame", skip=("z-",))    # the crown
        for k in range(9):
            x = x0 + 0.1 + k * 0.21
            m.box((x - 0.04, 3.05, d - 0.02), (x + 0.04, 3.17, d + 0.06), "frame", skip=("y-",))
        for xx in (x0, x1 - 0.06):                                                        # sides
            m.box((xx, 0.3, 0.0), (xx + 0.06, 2.85, d), "frame")
        return m
    return b


# ------------------------------------------------------------------ Ottoman (r3_ottoman_timber)
def wall_jetty():
    """the oversailing timber upper storey: the face 0.6 m out over the street on diagonal brackets, a rank of three
    windows, the soffit under it"""
    def b():
        z = 0.6
        o = [_rect(-1.15, 0.9, -0.55, 2.3), _rect(-0.3, 0.9, 0.3, 2.3), _rect(0.55, 0.9, 1.15, 2.3)]
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), o, z - T, z, "wall", reveal_slot="frame")
        for x0, y0, x1, y1 in ((-1.15, 0.9, -0.55, 2.3), (-0.3, 0.9, 0.3, 2.3), (0.55, 0.9, 1.15, 2.3)):
            m.pane(x0, y0, x1, y1, z - T * 0.5)
            m.box((x0 - 0.04, y0 - 0.05, z - 0.02), (x1 + 0.04, y0, z + 0.05), "trim", skip=("z-",))
        m.box((-HB, -0.22, -T), (HB, 0.0, z), "frame", skip=())                           # the soffit and joists
        for x in (-1.25, 0.0, 1.25):                                                      # diagonal brackets
            m.tube((x, -1.0, 0.0), (x, -0.22, z - 0.05), 0.06, "frame", n=4)
        m.box((-HB, ST - 0.12, z - 0.02), (HB, ST, z + 0.06), "trim", skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ Newar (r1_newar)
def wall_newar_window():
    """the carved black window of the Kathmandu valley: stepped frames, a lattice in the middle, the lintel and sill
    run out well past the jambs with carved ends"""
    def b():
        w, y0, h = 1.0, 1.0, 1.15
        m = _wall(K, [_rect(-w / 2, y0, w / 2, y0 + h)])
        m.pane(-w / 2, y0, w / 2, y0 + h, -0.35)
        _lattice(m, -w / 2, y0, w / 2, y0 + h, -0.12, -0.04, 5, 5, slot="frame")
        for k, (dx, dz) in enumerate(((0.12, 0.04), (0.24, 0.08))):                       # stepped frames
            m.box((-w / 2 - dx, y0 - dx * 0.5, 0.0), (-w / 2 - dx + 0.1, y0 + h + dx * 0.5, dz), "frame", skip=("z-",))
            m.box((w / 2 + dx - 0.1, y0 - dx * 0.5, 0.0), (w / 2 + dx, y0 + h + dx * 0.5, dz), "frame", skip=("z-",))
        m.box((-1.1, y0 + h + 0.12, 0.0), (1.1, y0 + h + 0.3, 0.12), "frame", skip=("z-",))   # lintel, run out
        m.box((-1.0, y0 - 0.25, 0.0), (1.0, y0 - 0.1, 0.1), "frame", skip=("z-",))           # sill, run out
        for x in (-1.1, 0.95):                                                            # carved ends
            m.box((x, y0 + h + 0.3, 0.0), (x + 0.15, y0 + h + 0.45, 0.1), "frame", skip=("z-",))
        return m
    return b


def edge_eave_pagoda():
    """a deep tiled eave on carved struts (Newar, Chinese, Japanese temple fronts): stands on the roof edge"""
    def b():
        m = Mesh()
        m.box((-HB, 0.0, -0.3), (HB, 0.2, 0.0), "frame", skip=("y-",))
        m.quad_facing((-HB - 0.1, 0.75, -0.3), (HB + 0.1, 0.75, -0.3), (HB + 0.25, 0.1, 1.2), (-HB - 0.25, 0.1, 1.2), (0, 1, 0.6), "roof")
        m.quad_facing((-HB - 0.1, 0.71, -0.3), (HB + 0.1, 0.71, -0.3), (HB + 0.25, 0.06, 1.2), (-HB - 0.25, 0.06, 1.2), (0, -1, -0.6), "frame", 0.6)
        m.box((-HB - 0.25, 0.04, 1.15), (HB + 0.25, 0.14, 1.25), "roof", 0.85)                # the tile edge
        for x in (-1.2, -0.4, 0.4, 1.2):                                                  # struts
            m.tube((x, -1.2, 0.02), (x, 0.3, 0.9), 0.05, "frame", n=4)
        return m
    return b


def roof_pagoda():
    """a two-tier temple roof over a cell with a gilt finial (Newar / East Asian temples)"""
    def b():
        m = Mesh()

        def tier(y0, a, h):
            pts = [(-a, y0, -a), (a, y0, -a), (a, y0, a), (-a, y0, a)]
            b_ = a * 0.45
            top = [(-b_, y0 + h, -b_), (b_, y0 + h, -b_), (b_, y0 + h, b_), (-b_, y0 + h, b_)]
            for k in range(4):
                p, q, r, s = pts[k], pts[(k + 1) % 4], top[(k + 1) % 4], top[k]
                c = ((p[0] + q[0]) / 2, 0.4, (p[2] + q[2]) / 2)
                m.quad_facing(p, q, r, s, c, "roof")
            m.quad_facing(pts[0], pts[1], pts[2], pts[3], (0, -1, 0), "frame", 0.6)
            return top
        tier(0.0, HB + 0.6, 0.9)
        m.box((-1.0, 0.9, -1.0), (1.0, 1.7, 1.0), "wall", skip=("y-",))
        top = tier(1.7, 1.6, 0.8)
        m.quad_facing(*top, (0, 1, 0), "roof")
        m.lathe([(0.0, 2.5), (0.22, 2.6), (0.16, 2.85), (0.2, 3.0), (0.06, 3.3), (0.0, 3.6)], "metal", n=8)
        return m
    return b


# ------------------------------------------------------------------ Japan (r2_japan_yokocho)
def _lantern(m, x, y, z, r=0.17, h=0.42):
    m.lathe([(0.0, y - h / 2), (r * 0.75, y - h / 2 + 0.03), (r, y), (r * 0.75, y + h / 2 - 0.03), (0.0, y + h / 2)], "emissive", n=6, cx=x, cz=z)
    m.cyl(x, z, r * 0.6, y + h / 2 - 0.03, y + h / 2 + 0.04, "frame", n=6, shade=0.6)


def ov_chochin_string():
    """red paper lanterns (chochin) strung across a lane at 2.8 m (along X)"""
    def b():
        m = Mesh()
        pts = [(-HB + BAY * i / 6, 3.0 - 0.3 * (1 - (2 * i / 6 - 1) ** 2), 0.0) for i in range(7)]
        for a, c in zip(pts, pts[1:]):
            m.tube(a, c, 0.008, "metal", n=3)
        for p in pts[1:-1:2]:
            m.tube(p, (p[0], p[1] - 0.15, p[2]), 0.006, "metal", n=3)
            _lantern(m, p[0], p[1] - 0.4, p[2])
        return m
    return b


def wall_noren():
    """a bar door under a split cloth curtain (noren) with a lantern each side (yokocho)"""
    def b():
        m = _wall(T, [_rect(-0.6, 0.0, 0.6, 2.1)])
        m.box((-0.6, 0.02, -0.16), (0.6, 2.1, -0.12), "frame", skip=())                   # a sliding lattice door
        _lattice(m, -0.55, 0.9, 0.55, 2.0, -0.112, -0.095, 4, 1, slot="frame")
        m.box((-0.7, 2.1, 0.0), (0.7, 2.2, 0.12), "frame", skip=("z-",))
        for k in range(3):                                                                # the split curtain
            x0 = -0.66 + k * 0.44
            m.quad_facing((x0, 2.12, 0.1), (x0 + 0.42, 2.12, 0.1), (x0 + 0.42, 1.55, 0.1), (x0, 1.55, 0.1), (0, 0, 1), "fabric")
            m.quad_facing((x0, 2.12, 0.098), (x0 + 0.42, 2.12, 0.098), (x0 + 0.42, 1.55, 0.098), (x0, 1.55, 0.098), (0, 0, -1), "fabric", 0.7)
        for x in (-0.95, 0.95):
            _lantern(m, x, 2.15, 0.22, r=0.14, h=0.36)
            m.box((x - 0.02, 2.36, 0.0), (x + 0.02, 2.4, 0.22), "metal")
        return m
    return b


# ------------------------------------------------------------------ Chongqing (r2_chongqing_cliff)
def stilt_frame():
    """the stilts under a cell hung over a slope: four posts three storeys down, cross bracing (diaojiaolou)"""
    def b():
        m = Mesh()
        dn = 3 * ST
        for x in (-1.35, 1.35):
            for z in (-1.35, 1.35):
                m.box((x - 0.1, -dn, z - 0.1), (x + 0.1, 0.0, z + 0.1), "frame", skip=("y+",))
        for k in range(3):
            y0, y1 = -dn + k * ST, -dn + (k + 1) * ST
            for z in (-1.35, 1.35):
                m.tube((-1.35, y0 + 0.2, z), (1.35, y1 - 0.2, z), 0.05, "frame", n=4)
                m.box((-1.35, y1 - 0.15, z - 0.07), (1.35, y1 - 0.02, z + 0.07), "frame", 0.85)
            for x in (-1.35, 1.35):
                m.tube((x, y1 - 0.2, -1.35), (x, y0 + 0.2, 1.35), 0.05, "frame", n=4)
        return m
    return b


# ------------------------------------------------------------------ Tbilisi (r3_caucasian_balcony)
def wall_tbilisi_balcony():
    """the full-width carved wooden balcony of old Tbilisi: 1 m out on brackets, a carved fretwork apron, glazed
    above in thin muntins, a roof over it"""
    def b():
        m = _cheap_window(T, -0.5, 0.0, 0.5, 2.3, sill=False)
        d, x0, x1 = 1.0, -HB, HB
        m.box((x0, -0.15, 0.0), (x1, 0.0, d), "frame", skip=("z-",))                       # floor
        m.box((x0, 0.0, d - 0.05), (x1, 0.9, d), "frame", skip=("z-",))                    # apron
        for k in range(10):                                                               # fretwork (carved panels, flat)
            x = x0 + 0.15 + k * 0.3
            m.quad_facing((x - 0.1, 0.15, d + 0.01), (x + 0.1, 0.15, d + 0.01), (x + 0.1, 0.75, d + 0.01), (x - 0.1, 0.75, d + 0.01), (0, 0, 1), "screen")
            m.quad_facing((x - 0.03, 0.75, d + 0.01), (x + 0.03, 0.75, d + 0.01), (x, 0.85, d + 0.01), (x, 0.85, d + 0.01), (0, 0, 1), "screen")
        m.pane(x0 + 0.05, 0.9, x1 - 0.05, 2.6, d - 0.03)                                  # glazed above
        for k in range(1, 10):
            x = x0 + k * 0.3
            _strip(m, (x, 0.9, d - 0.02), (x, 2.6, d - 0.02), 0.04, (0, 0, 1), "frame")
        _strip(m, (x0, 1.75, d - 0.02), (x1, 1.75, d - 0.02), 0.04, (0, 0, 1), "frame")
        for x in (x0, x1 - 0.06):
            m.box((x, 0.0, 0.0), (x + 0.06, 2.75, d), "frame")
        m.quad_facing((x0 - 0.1, 3.0, 0.0), (x1 + 0.1, 3.0, 0.0), (x1 + 0.1, 2.7, d + 0.2), (x0 - 0.1, 2.7, d + 0.2), (0, 1, 0), "roof")
        m.quad_facing((x0 - 0.1, 2.97, 0.0), (x1 + 0.1, 2.97, 0.0), (x1 + 0.1, 2.67, d + 0.2), (x0 - 0.1, 2.67, d + 0.2), (0, -1, 0), "frame", 0.7)
        for x in (-1.2, 0.0, 1.2):                                                        # brackets
            m.tube((x, -0.9, 0.0), (x, -0.15, d - 0.1), 0.05, "frame", n=4)
        return m
    return b


# ------------------------------------------------------------------ Hanseatic (r3_hanseatic_gable)
def edge_gable(kind):
    """the gable over a narrow house front (stands on the roof top above its wall bay): stepped, neck (with scroll
    shoulders) or bell; a hoist beam with its hook at the top, a loading door below it"""
    def b():
        m = Mesh()
        t = T + 0.05
        if kind == "step":
            prof = [(-HB, 0.0), (HB, 0.0), (HB, 0.8), (1.0, 0.8), (1.0, 1.6), (0.5, 1.6), (0.5, 2.4), (0.15, 2.4), (0.15, 3.1),
                    (-0.15, 3.1), (-0.15, 2.4), (-0.5, 2.4), (-0.5, 1.6), (-1.0, 1.6), (-1.0, 0.8), (-HB, 0.8)]
        elif kind == "neck":
            prof = [(-HB, 0.0), (HB, 0.0), (HB, 0.4)] + [(0.7 + 0.8 * math.cos(math.pi / 2 * k / 4), 0.4 + 1.0 * math.sin(math.pi / 2 * k / 4)) for k in range(1, 5)] + \
                   [(0.7, 2.6), (0.5, 3.1), (-0.5, 3.1), (-0.7, 2.6)] + \
                   [(-0.7 - 0.8 * math.cos(math.pi / 2 * (4 - k) / 4), 0.4 + 1.0 * math.sin(math.pi / 2 * (4 - k) / 4)) for k in range(0, 4)] + [(-HB, 0.4)]
        else:                                                    # bell
            prof = [(-HB, 0.0), (HB, 0.0)] + [(HB * math.copysign(abs(math.cos(math.pi * k / 12)) ** 0.6, math.cos(math.pi * k / 12)),
                                                3.0 * math.sin(math.pi * k / 12)) for k in range(1, 12)]
        from geom import _dedupe
        prof = _dedupe(prof)
        door = _rect(-0.4, 0.3, 0.4, 1.7)
        m.wall_cut(prof, [door], -t, 0.0, "wall", reveal_slot="trim")
        m.box((-0.4, 0.3, -t + 0.05), (0.4, 1.7, -t + 0.1), "frame")                         # the loading door
        m.box((-0.07, 2.1, -t), (0.07, 2.25, 0.9), "frame", skip=("z-",))                    # the hoist beam
        m.tube((0.0, 2.1, 0.8), (0.0, 1.2, 0.8), 0.01, "metal", n=3)
        m.box((-0.05, 1.12, 0.75), (0.05, 1.2, 0.85), "metal")
        return m
    return b


# ------------------------------------------------------------------ Andes (r3_andean_neo)
def wall_cholet_front():
    """a cholet's front (El Alto): mirror glass in bold coloured geometric frames, LED strips on the edges"""
    def b():
        m = Mesh()
        m.wall_cut(_rect(-HB, 0.0, HB, ST), [_rect(-1.3, 0.25, 1.3, 2.95)], -T, 0.0, "tile", reveal_slot="trim")
        m.pane(-1.3, 0.25, 1.3, 2.95, -0.08)                                               # mirror glass
        for x0, y0, x1, y1, slot in ((-1.3, 1.5, 1.3, 1.62, "trim"), (-0.06, 0.25, 0.06, 2.95, "trim")):
            m.box((x0, y0, -0.08), (x1, y1, 0.02), slot, skip=("z-",))
        tri = [(-1.3, 2.95), (0.0, 2.4), (1.3, 2.95)]                                      # the chevron crest
        m.wall_cut(tri, [], 0.0, 0.05, "fabric")
        m.wall_cut([(-1.3, 0.25), (1.3, 0.25), (0.0, 0.8)], [], 0.0, 0.05, "fabric")
        for x in (-HB + 0.04, HB - 0.04):                                                  # LED edges
            m.box((x - 0.03, 0.1, 0.0), (x + 0.03, ST - 0.1, 0.04), "emissive", skip=("z-",))
        return m
    return b


# ------------------------------------------------------------------ register
Y, H, O, N, J, C, G, A, HS = (["yemeni_tower"], ["hejazi_roshan"], ["ottoman_timber"], ["newar"], ["japan_yokocho"],
                              ["chongqing_cliff"], ["caucasian_balcony"], ["andean_neo"], ["hanseatic_gable"])
PIECES["kerb_post"] = _w("corner", kerb_post(), BOTH, lod1="box", kind="water_edge", notes="kerb corner post: origin on the cell corner, land in -X/-Z")
PIECES["wall_gypsum_window_k"] = _w("wall", wall_gypsum_window(), Y, notes="YEMEN MARK: gypsum-framed window, small qamariya")
PIECES["band_brick_relief"] = _w("wall", band_brick_relief(), Y + ["saharan_kasbah"], lod1="drop", collide=False, kind="overlay",
                                 notes="zigzag relief band (0.4 m high) on a facade at any height")
PIECES["wall_roshan_t"] = _w("wall", wall_roshan(T), H + ["cairene_mamluk"], lod1="keep", notes="HEJAZ MARK: full-storey teak oriel; stack it")
PIECES["wall_roshan_k"] = _w("wall", wall_roshan(K), H + ["cairene_mamluk"], lod1="keep", notes="HEJAZ MARK: full-storey teak oriel; stack it")
PIECES["wall_jetty_t"] = _w("wall", wall_jetty(), O + ["levantine_courtyard"], lod1="keep", notes="OTTOMAN MARK: storey oversailing 0.6 m on brackets")
PIECES["wall_newar_window_k"] = _w("wall", wall_newar_window(), N, notes="NEWAR MARK: carved black window, lintel run out")
PIECES["edge_eave_pagoda"] = _w("edge", edge_eave_pagoda(), N + ["siam_khlong", "taipei_tiepi"], lod1="keep", notes="deep tiled eave on struts")
PIECES["roof_pagoda"] = _w("cell", roof_pagoda(), N + ["siam_khlong"], lod1="keep", kind="crown", notes="two-tier temple roof, gilt finial")
PIECES["ov_chochin_string"] = _w("cell", ov_chochin_string(), J, lod1="drop", collide=False, kind="overlay", notes="JAPAN MARK: lanterns across a lane (along X)")
PIECES["wall_noren_t"] = _w("wall", wall_noren(), J, notes="JAPAN MARK: bar door, noren curtain, lantern pair")
PIECES["stilt_frame"] = _w("cell", stilt_frame(), C, lod1="keep", collide=False, kind="slab", notes="CHONGQING MARK: stilts 3 storeys down under a cell")
PIECES["wall_tbilisi_balcony_t"] = _w("wall", wall_tbilisi_balcony(), G, lod1="keep", notes="TBILISI MARK: carved glazed full-width balcony")
for k in ("step", "neck", "bell"):
    PIECES[f"edge_gable_{k}"] = _w("edge", edge_gable(k), HS, lod1="keep", kind="crown", notes="HANSEATIC MARK: gable over a house front, hoist beam")
PIECES["wall_cholet_front_t"] = _w("wall", wall_cholet_front(), A, notes="ANDES MARK: cholet mirror glass in coloured geometric frames, LED edges")


# ------------------------------------------------------------------ default palettes for every family (researched colours)
def _fam_palettes():
    out = {}
    for f in ("r1_grammars.json", "r2_grammars.json", "r3_grammars.json"):
        p = os.path.join(WARRENS, f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        fams = d.get("families", d) if isinstance(d, dict) else d
        fams = list(fams.values()) if isinstance(fams, dict) else fams
        for fam in fams:
            if not isinstance(fam, dict) or "id" not in fam:
                continue
            w = fam.get("wall") or fam.get("walls") or (fam.get("grammar") or {}).get("walls") or {}
            ok = lambda c: isinstance(c, str) and len(c) == 7 and c[0] == "#" and all(ch in "0123456789abcdefABCDEF" for ch in c[1:])  # noqa: E731
            pal = [c for c in (w.get("palette") or []) if ok(c)]
            trim = [c for c in (w.get("trim") or []) if ok(c)] if isinstance(w.get("trim"), list) else []
            if not pal:                                                 # r3 style: colours listed per material
                for k, v in w.items():
                    vs_ = [v] if isinstance(v, str) else v if isinstance(v, list) else []
                    cs = [c for c in vs_ if ok(c)]
                    if k in ("frames", "trim", "shutters"):
                        trim += [c for c in cs if c not in trim]
                    elif k not in ("roof", "copper"):
                        pal += cs
            if not pal:
                continue
            lum = lambda h: sum(int(h[i:i + 2], 16) for i in (1, 3, 5))       # noqa: E731
            light = max(pal + trim, key=lum)
            dark = min(pal + trim, key=lum)
            vs = []
            for i in range(4):
                wall = pal[i % len(pal)]
                tr = trim[i % len(trim)] if trim else (light if wall != light else "#f0ece2")
                vs.append({"wall": wall, "trim": tr, "frame": dark if lum(dark) < 300 else "#4a3a2a", "glass": "#2c3a42",
                           "screen": dark if lum(dark) < 300 else "#5a4632", "roof": pal[(i + 2) % len(pal)], "metal": "#4a4744",
                           "fabric": pal[(i + 3) % len(pal)], "emissive": "#ffd890", "tile": trim[0] if trim else pal[-1],
                           "water": "#3d7f8c", "ground": pal[(i + 1) % len(pal)], "plant": "#5b7f3a"})
            if ok(w.get("roof")):
                for v in vs:
                    v["roof"] = w["roof"]
            out[fam["id"]] = vs
    return out


for fid, vs in _fam_palettes().items():
    PALETTES.setdefault(fid, vs)

import pieces_marks  # noqa: E402,F401  (batch 3: the rebuilt marks + accent slots)
import pieces_b4  # noqa: E402,F401  (batch 4a: the generator's requests)
import pieces_b5  # noqa: E402,F401  (batch 4b)
import pieces_b6  # noqa: E402,F401  (batch 4c)
import pieces_b7  # noqa: E402,F401  (batch 4d)
import pieces_b8  # noqa: E402,F401  (batch 4e)
import pieces_b9  # noqa: E402,F401  (batch 4f)
import pieces_moor  # noqa: E402,F401  (the market moorings: line house, top stations, davit, signal mast)
