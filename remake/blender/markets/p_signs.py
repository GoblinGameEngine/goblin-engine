"""p_signs.py -- the market entrances and the 22 name-sign mounts (the markets' landmarks), dressed with the market
atlas cells (godot_project/remake/signs/markets.png: the Grok A1-A5 sheets cut by tools/signs/crop_sheets.py).

  fm_arch_{timber,truss,googie}   generic entrance arches (north / river / south), a name board at `board`
  fm_board_<market>               the market's main cell as a two-faced board (on an arch, a shed gable, a pole)
  sign_<market>                   the market's own pylon or landmark: a 3D structure with its cells mounted
"""
import math

import numpy as np

from mk import B, Mesh, V, card, cell_aspect, festoon, lathe, piece, place, prism_zy, ring_torus, rot_y, sweep, bulb  # noqa: F401

MARKETS = ["fm01_ropewalk", "fm02_lobster_pot", "fm03_tide_clock", "fm04_net_loft", "fm05_water_tower", "fm06_book_barn",
           "fm07_weathervane", "fm08_brannock_trade_days", "fm09_boathouse_swap", "fm10_four_corners_swap", "fm11_regatta_swap",
           "fm12_millwheel_market", "fm13_traders_landing", "fm14_iron_wheel", "fm15_red_granary", "fm16_tall_tamarack",
           "fm17_elevator_flea_days", "fm18_route30_swap_meet", "fm19_la_pulga_verde", "fm20_starlite_swap", "fm21_carousel_swap",
           "fm22_pelican_swap"]
BAND = {k: ("north" if i < 8 else "river" if i < 13 else "south") for i, k in enumerate(MARKETS)}


def face(m, cid, c, h, yaw=0.0, two=True, gap=0.03, slot="sign", w=None):
    """a cell card centred at c, h tall, facing +z turned by yaw"""
    a = math.radians(yaw)
    right = (math.cos(a), 0.0, -math.sin(a))
    return card(m, slot, cid, c, right, (0, 1, 0), h, w=w, two=two, gap=gap)


def cw(cid, h):
    return h * cell_aspect(cid)


def bulbs_line(m, p0, p1, n, slot="bulb", r=0.05):
    p0, p1 = V(*p0), V(*p1)
    for k in range(n):
        bulb(m, tuple(p0 + (p1 - p0) * (k + 0.5) / n), r, slot)


def bulbs_ring(m, c, R, n, slot="bulb", r=0.06, plane="xy", a0=0.0, a1=360.0):
    c = V(*c)
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n)
        d = V(math.cos(a), math.sin(a), 0) if plane == "xy" else V(math.cos(a), 0, math.sin(a))
        bulb(m, tuple(c + d * R), r, slot)


def post(m, x, z, w, h, slot, d=None, y0=0.0):
    d = d or w
    m.box((x - w / 2, y0, z - d / 2), (x + w / 2, y0 + h, z + d / 2), slot)


def plinth(m, w, d, h, slot="concrete", q=1):
    m.box((-w / 2, 0.0, -d / 2), (w / 2, h, d / 2), slot)
    if q:
        m.box((-w / 2 - 0.05, 0.0, -d / 2 - 0.05), (w / 2 + 0.05, 0.12, d / 2 + 0.05), "dark")


# ------------------------------------------------------------------ the generic entrance arches (span along x)
def arch_timber(q):
    """north: two square timber posts on granite bases, a moulded beam, a pediment board and finials (10 m clear)"""
    m = Mesh()
    for s in (-1, 1):
        x = s * 5.25
        m.box((x - 0.4, 0.0, -0.4), (x + 0.4, 0.7, 0.4), "concrete")
        m.box((x - 0.25, 0.7, -0.25), (x + 0.25, 5.4, 0.25), "cream")
        m.box((x - 0.32, 5.4, -0.32), (x + 0.32, 5.55, 0.32), "trim")
        if q:
            lathe(m, [(0.18, 0.0), (0.18, 0.12), (0.12, 0.3), (0.0, 0.5)], "brass", n=8, cx=x, y0=5.55)
            for yy in (2.0, 3.6):
                m.box((x - 0.27, yy, -0.27), (x + 0.27, yy + 0.08, 0.27), "trim")
    m.box((-5.0, 4.6, -0.2), (5.0, 5.0, 0.2), "cream")                            # the beam (between the posts)
    m.box((-5.0, 4.5, -0.24), (5.0, 4.6, 0.24), "trim")
    m.prism_xy([(-3.6, 5.0), (3.6, 5.0), (0.0, 6.0)], [], -0.12, 0.12, "trim")      # the pediment
    if q:
        bulbs_line(m, (-4.9, 4.47, 0.27), (4.9, 4.47, 0.27), 20)
        bulbs_line(m, (-4.9, 4.47, -0.27), (4.9, 4.47, -0.27), 20)
    return m


def arch_truss(q):
    """river: brick piers and a painted steel box truss (12 m clear) with a board in the middle"""
    m = Mesh()
    for s in (-1, 1):
        x = s * 6.4
        m.box((x - 0.4, 0.0, -0.5), (x + 0.4, 5.6, 0.5), "wall")
        m.box((x - 0.48, 5.6, -0.58), (x + 0.48, 5.8, 0.58), "trim")
        if q:
            m.box((x - 0.46, 0.0, -0.56), (x + 0.46, 0.5, 0.56), "concrete")
    y0, y1 = 4.8, 5.6
    for z in (-0.3, 0.3):
        for y in (y0, y1):
            m.box((-6.0, y - 0.06, z - 0.06), (6.0, y + 0.06, z + 0.06), "steel")
        if q:
            for k in range(8):
                xa, xb = -6.0 + 1.5 * k, -6.0 + 1.5 * (k + 1)
                ya, yb = (y0 + 0.06, y1 - 0.06) if k % 2 == 0 else (y1 - 0.06, y0 + 0.06)
                m.tube((xa + 0.05, ya, z), (xb - 0.05, yb, z), 0.03, "steel", n=4)
    if q:
        bulbs_line(m, (-5.9, 4.68, 0.4), (5.9, 4.68, 0.4), 22, "bulb")
        m.box((-0.06, 5.6, -0.04), (0.06, 6.4, 0.04), "steel")
        m.box((0.06, 6.0, -0.01), (0.9, 6.38, 0.01), "accent")                        # a pennant
    return m


def arch_googie(q):
    """south: two stucco pylons with a boomerang beam and a starburst, neon along the beam (12 m clear)"""
    m = Mesh()
    for s in (-1, 1):
        x = s * 6.5
        m.prism_xz([(x - 0.5, -0.6), (x + 0.5, -0.6), (x + 0.35, 0.6), (x - 0.35, 0.6)], 0.0, 6.6 if s < 0 else 5.6, "cream")
        if q:
            m.prism_xz([(x - 0.52, -0.62), (x + 0.52, -0.62), (x + 0.37, 0.62), (x - 0.37, 0.62)], 0.0, 0.5, "accent")
    pts = [(-6.0, 5.6), (0.0, 4.9), (6.0, 5.0), (6.0, 5.4), (0.0, 5.3), (-6.0, 6.0)]
    m.prism_xy(pts, [], -0.18, 0.18, "accent2")
    sweep(m, [(-5.9, 5.55 - 0.03, 0.22), (0.0, 4.88, 0.22), (5.9, 4.98, 0.22)], 0.03, "neon", n=4)
    if q:                                                                             # the starburst over the left pylon
        for k in range(8):
            a = math.tau * k / 8
            m.tube((-6.5 + 0.1 * math.cos(a), 7.2 + 0.1 * math.sin(a), 0.0), (-6.5 + 1.0 * math.cos(a), 7.2 + 1.0 * math.sin(a), 0.0), 0.04, "trim", n=4)
            bulb(m, (-6.5 + 1.08 * math.cos(a), 7.2 + 1.08 * math.sin(a), 0.0), 0.08, "bulb_a")
        m.box((-6.56, 6.6, -0.06), (-6.44, 7.04, 0.06), "trim")
        lathe(m, [(0.0, 0.0), (0.1, 0.1), (0.0, 0.2)], "brass", n=6, cx=-6.5, y0=7.1)
    return m


ARCH_PASS = {"fm_arch_timber": B(-4.8, 0, -0.6, 4.8, 4.35, 0.6), "fm_arch_truss": B(-5.95, 0, -0.6, 5.95, 4.6, 0.6),
             "fm_arch_googie": B(-5.95, 0, -0.6, 5.95, 4.8, 0.6)}
piece("fm_arch_timber", "sign", arch_timber, kind="landmark", foot=None, lod1="keep",
      frame=[B(-5.65, 0, -0.4, -4.85, 5.55, 0.4), B(4.85, 0, -0.4, 5.65, 5.55, 0.4), B(-5.0, 4.5, -0.24, 5.0, 6.0, 0.24)],
      passes=[{"box": ARCH_PASS["fm_arch_timber"], "kind": "open"}], anchors={"board": [0.0, 5.3, 0.3, 0], "board_back": [0.0, 5.3, -0.3, 180]},
      budget=900, palette="north", notes="NORTH entrance: painted timber posts on granite, pediment, finials, amber bulbs; 10 m x 4.45 m clear")
piece("fm_arch_truss", "sign", arch_truss, kind="landmark", foot=None, lod1="keep",
      frame=[B(-6.88, 0, -0.58, -6.0, 5.8, 0.58), B(6.0, 0, -0.58, 6.88, 5.8, 0.58), B(-6.0, 4.74, -0.36, 6.0, 5.66, 0.36)],
      passes=[{"box": ARCH_PASS["fm_arch_truss"], "kind": "open"}], anchors={"board": [0.0, 5.2, 0.45, 0], "board_back": [0.0, 5.2, -0.45, 180]},
      budget=1200, palette="river", notes="RIVER entrance: brick piers and a steel box truss with bulbs; 11.9 m x 4.6 m clear")
piece("fm_arch_googie", "sign", arch_googie, kind="landmark", foot=None, lod1="keep",
      frame=[B(-7.0, 0, -0.6, -6.0, 6.6, 0.6), B(6.0, 0, -0.6, 7.0, 5.6, 0.6), B(-6.0, 4.85, -0.2, 6.0, 6.0, 0.2)],
      passes=[{"box": ARCH_PASS["fm_arch_googie"], "kind": "open"}], anchors={"board": [0.0, 5.9, 0.3, 0], "board_back": [0.0, 5.9, -0.3, 180]},
      budget=900, palette="south", notes="SOUTH entrance: stucco pylons, a boomerang beam with a neon line, a bulb starburst; 11.9 m x 4.8 m clear")


def board(cid, h):
    def b(q):
        m = Mesh()
        face(m, cid, (0.0, 0.0, 0.0), h, gap=0.04)
        return m
    return b


for mk_ in MARKETS:
    cid = mk_ + "_main"
    h = 2.4 if cell_aspect(cid) < 1.6 else 1.6
    piece("fm_board_" + mk_, "sign", board(cid, h), kind="sign", foot=[round(cw(cid, h), 2), 0.04],
          lod1="keep", collide="none", mid="full", budget=8, palette="white",
          notes="%s's main cell as a two-faced board (%.1f m tall, centred on its anchor)" % (mk_, h))


# ------------------------------------------------------------------ the 22 landmarks
LANDMARKS = {}


def landmark(mk_, frame, budget, notes, passes=None, anchors=None, moving=None, foot=None):
    def deco(fn):
        LANDMARKS[mk_] = dict(build=fn, frame=frame, budget=budget, notes=notes, passes=passes or [], anchors=anchors or {},
                              moving=moving, foot=foot)
        return fn
    return deco


def front_back(m, cid, c, h, depth, w=None):
    """one card on the front face (z + depth) and one on the back (z - depth), each one-sided"""
    x, y, z = c
    face(m, cid, (x, y, z + depth), h, 0.0, two=False, w=w)
    face(m, cid, (x, y, z - depth), h, 180.0, two=False, w=w)


def laps(m, x0, x1, ys, z, holes=(), slot="trim", h=0.03, off=0.027):
    """clapboard / shingle lap lines: thin one-sided strips 2.7 cm proud of a +z face at z, split round holes
    [(hx0, hx1, top)] (doors: no strip over them below `top`)"""
    for y in ys:
        spans = [(x0, x1)]
        for hx0, hx1, top in holes:
            if y < top:
                spans = [(a, b) for a0, b0 in spans for a, b in ((a0, min(b0, hx0)), (max(a0, hx1), b0)) if b - a > 0.05]
        for a, b in spans:
            m.quad((a, y, z + off), (b, y, z + off), (b, y + h, z + off), (a, y + h, z + off), slot)


def backing(m, cid, c, h, t, pad=0.12, slot="wood"):
    w = cw(cid, h)
    x, y, z = c
    m.box((x - w / 2 - pad, y - h / 2 - pad, z - t / 2), (x + w / 2 + pad, y + h / 2 + pad, z + t / 2), slot)
    return w


@landmark("fm01_ropewalk", [B(-2.3, 0, -0.7, 2.3, 0.8, 0.7), B(-0.5, 0.8, -0.3, 0.5, 12.0, 0.3)], 4500,
          "a 12 m granite-and-timber pylon wrapped by a giant figure-eight rope with amber chase bulbs, the barn-red "
          "board both faces, Salty the gull on the plinth")
def lm_ropewalk(q):
    m = Mesh()
    m.box((-2.3, 0.0, -0.7), (2.3, 0.8, 0.7), "concrete")
    m.box((-0.5, 0.8, -0.3), (0.5, 12.0, 0.3), "wood")
    m.box((-0.6, 12.0, -0.4), (0.6, 12.25, 0.4), "trim")
    if q:
        for y in (3.0, 6.0, 9.0):
            m.box((-0.52, y, -0.32), (0.52, y + 0.12, 0.32), "dark")              # iron bands
    front_back(m, "fm01_ropewalk_main", (0.0, 9.8, 0.0), 1.9, 0.33)
    n = 64 if q else 28
    pts = []
    for k in range(n + 1):
        t = math.tau * k / n
        pts.append((2.3 * math.sin(t), 5.2 + 1.9 * math.sin(2 * t), 0.75 * math.cos(t)))
    sweep(m, pts, 0.17, "rope", n=7 if q else 5, caps=False)
    if q:
        for k in range(0, n, 2):
            t = math.tau * (k + 0.5) / n
            p = V(2.3 * math.sin(t), 5.2 + 1.9 * math.sin(2 * t), 0.75 * math.cos(t))
            bulb(m, tuple(p + V(0, 0, 0.25 if p[2] >= 0 else -0.25)), 0.08, "bulb")
    face(m, "fm01_ropewalk_mascot", (-1.62, 0.8 + 1.15, 0.45), 2.3, 12.0, gap=0.03, slot="sign")
    return m


@landmark("fm02_lobster_pot", [B(-1.95, 0, -0.35, -1.45, 2.6, 0.35), B(1.45, 0, -0.35, 1.95, 2.6, 0.35), B(-2.2, 2.6, -1.1, 2.2, 4.55, 1.1)], 3500,
          "a giant slatted lobster trap on two granite posts, strung with buoys, a red lobster weathervane on top, the oval "
          "gilt board hung between the posts")
def lm_lobster_pot(q):
    m = Mesh()
    for x in (-1.7, 1.7):
        m.box((x - 0.25, 0.0, -0.35), (x + 0.25, 2.6, 0.35), "concrete")
    m.box((-2.2, 2.6, -1.1), (2.2, 2.75, 1.1), "wood")                           # the trap's base
    nh = 5 if q else 3
    na = 9 if q else 5
    for k in range(nh):                                                            # hoops (half circles across z)
        x = -2.1 + 4.2 * k / (nh - 1)
        sweep(m, [(x, 2.75 + 1.7 * math.sin(math.pi * i / 8), 1.0 * math.cos(math.pi * i / 8)) for i in range(9)], 0.04, "wood", n=4)
    for i in range(1, na):                                                         # slats along x
        a = math.pi * i / na
        m.tube((-2.15, 2.75 + 1.7 * math.sin(a), 1.0 * math.cos(a) * 1.0), (2.15, 2.75 + 1.7 * math.sin(a), 1.0 * math.cos(a)), 0.035, "wood", n=4)
    # the weathervane: a pole and a red lobster cut-out
    m.box((-0.03, 4.49, -0.03), (0.03, 5.3, 0.03), "metal")
    lob = [(-0.7, 5.5), (-0.25, 5.35), (0.25, 5.38), (0.5, 5.3), (0.75, 5.55), (0.6, 5.6), (0.45, 5.48), (0.3, 5.6), (0.5, 5.75),
           (0.25, 5.72), (-0.25, 5.65), (-0.7, 5.6)]
    m.prism_xy(lob, [], -0.03, 0.03, "accent")
    if q:
        for k, (x, z) in enumerate(((-1.2, 1.05), (-0.4, 1.05), (0.4, 1.05), (1.2, 1.05), (-0.8, -1.05), (0.8, -1.05))):
            y = 1.9 - 0.15 * (k % 2)
            m.tube((x, y + 0.42, z), (x, 2.6, z), 0.012, "rope", n=3)
            lathe(m, [(0.0, 0.0), (0.12, 0.08), (0.17, 0.25), (0.15, 0.38), (0.06, 0.42), (0.0, 0.42)], ("accent", "accent2", "cream")[k % 3],
                  n=8, cx=x, cz=z, y0=y)
    m.box((-1.45, 2.5, -0.02), (1.45, 2.56, 0.02), "metal")                      # the board's hanger bar
    w = cw("fm02_lobster_pot_main", 1.75)
    face(m, "fm02_lobster_pot_main", (0.0, 1.55, 0.0), 1.75, gap=0.04)
    for x in (-w / 3, w / 3):
        m.box((x - 0.01, 2.42, -0.01), (x + 0.01, 2.5, 0.01), "metal")
    return m


@landmark("fm03_tide_clock", [B(-1.2, 0, -1.2, 1.2, 9.0, 1.2), B(-1.1, 0, 1.6, 1.1, 1.4, 1.95)], 1800,
          "a white clapboard tower (9 m + cap) with the giant one-handed tide clock both faces, a red lamp on top, the "
          "engraved slab board on a granite block in front")
def lm_tide_clock(q):
    m = Mesh()
    m.box((-1.2, 0.0, -1.2), (1.2, 9.0, 1.2), "cream")
    m.box((-1.32, 9.0, -1.32), (1.32, 9.2, 1.32), "trim")
    pyr = Mesh()
    pyr.lathe([(1.8, 0.0), (0.0, 1.6)], "roof", n=4)
    place(m, pyr, 0.0, 9.2, 0.0, 45.0)
    m.cyl(0.0, 0.0, 0.05, 10.8, 11.3, "metal", n=4)
    bulb(m, (0.0, 11.42, 0.0), 0.12, "warn")
    if q:
        ys = [0.32 * k for k in range(1, 28)]
        laps(m, -1.18, 1.18, ys, 1.2, holes=[(-0.55, 0.55, 2.3)])                 # clapboard lap lines, all four faces
        for yaw in (90, 180, 270):
            t = Mesh()
            laps(t, -1.18, 1.18, ys, 1.2)
            place(m, t, yaw=yaw)
        m.box((-0.5, 0.0, 1.2), (0.5, 2.2, 1.24), "dark")                          # the door
    front_back(m, "fm03_tide_clock_landmark", (0.0, 7.0, 0.0), 2.1, 1.28)
    m.box((-1.1, 0.0, 1.6), (1.1, 1.4, 1.95), "concrete")
    face(m, "fm03_tide_clock_main", (0.0, 0.78, 1.98), 0.95, two=False)
    return m


@landmark("fm04_net_loft", [B(-2.6, 0, -1.6, 2.6, 5.6, 1.6)], 2000,
          "the grey-shingled gable of an old net loft (5 m wide), the lettered gable cell on its front, a net with glass "
          "floats and the carved tern hung beside the door")
def lm_net_loft(q):
    m = Mesh()
    m.box((-2.5, 0.0, -1.5), (2.5, 3.4, 1.5), "wall")
    m.prism_xy([(-2.65, 3.4), (2.65, 3.4), (0.0, 5.55)], [], -1.6, 1.6, "roof")
    m.box((-2.55, 0.0, -1.55), (2.55, 0.4, 1.55), "concrete")
    if q:
        laps(m, -2.48, 2.48, [0.4 + 0.33 * k for k in range(1, 9)], 1.5, holes=[(-0.65, 0.65, 2.65)], slot="dark")
        m.box((-0.6, 0.4, 1.5), (0.6, 2.6, 1.55), "wood")                          # the loft door
    face(m, "fm04_net_loft_main", (0.0, 3.95, 1.63), 2.9, two=False)
    face(m, "fm04_net_loft_landmark", (1.7, 1.4, 1.63), 2.1, two=False)
    return m


@landmark("fm05_water_tower", [B(-2.4, 0, -2.4, 2.4, 10.0, 2.4), B(-2.5, 10.0, -2.5, 2.5, 16.0, 2.5)], 4000,
          "the village water tower: four splayed legs, a balcony ring, the silver tank lettered from the landmark cell, "
          "a floodlit LOOMIS GROVE board between the legs")
def lm_water_tower(q):
    m = Mesh()
    n = 16 if q else 10
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.tube((sx * 2.2, 0.0, sz * 2.2), (sx * 1.55, 10.0, sz * 1.55), 0.12, "steel", n=6 if q else 4)
            m.box((sx * 2.2 - 0.35, 0.0, sz * 2.2 - 0.35), (sx * 2.2 + 0.35, 0.3, sz * 2.2 + 0.35), "concrete")
    if q:
        for y0, y1 in ((0.6, 5.0), (5.0, 9.4)):                                  # cross braces on each face
            for s in (-1, 1):
                ra, rb = 2.2 - 0.65 * y0 / 10, 2.2 - 0.65 * y1 / 10
                m.tube((-ra + 0.12, y0, s * ra), (rb - 0.12, y1, s * rb), 0.035, "steel", n=4)
                m.tube((s * ra, y0, -ra + 0.12), (s * rb, y1, rb - 0.12), 0.035, "steel", n=4)
    m.cyl(0.0, 0.0, 2.75, 9.92, 10.0, "steel", n=n)                               # the balcony deck
    if q:
        ring_torus(m, (0.0, 11.0, 0.0), 2.72, 0.03, "steel", n=n)
        for k in range(8):
            a = math.tau * (k + 0.5) / 8
            m.box((2.72 * math.cos(a) - 0.02, 10.0, 2.72 * math.sin(a) - 0.02), (2.72 * math.cos(a) + 0.02, 10.97, 2.72 * math.sin(a) + 0.02), "steel")
    lathe(m, [(2.4, 10.0), (2.4, 14.0), (2.5, 14.05), (0.25, 15.6), (0.0, 15.7)], "metal", n=n)
    # the lettering: the landmark cell's tank band wrapped round the front 140 degrees, 2 cm off the tank
    cid = "fm05_water_tower_landmark"
    from mk import cell_uv
    segs = 8 if q else 5
    for i in range(segs):
        a0 = math.radians(90 + 70 - 140 * i / segs)
        a1 = math.radians(90 + 70 - 140 * (i + 1) / segs)
        sub = (0.08 + 0.84 * i / segs, 0.34, 0.08 + 0.84 * (i + 1) / segs, 0.78)
        uv = cell_uv(cid, sub)
        R = 2.5
        p = lambda a, y: (R * math.cos(a), y, R * math.sin(a))  # noqa: E731
        m.quad(p(a0, 10.9), p(a1, 10.9), p(a1, 13.4), p(a0, 13.4), "sign", 1.0, uv=uv)
    w = backing(m, "fm05_water_tower_main", (0.0, 2.6, 2.05), 1.5, 0.12, slot="steel")
    face(m, "fm05_water_tower_main", (0.0, 2.6, 2.14), 1.5, two=False)
    for s in (-1, 1):
        m.box((s * (w / 2 + 0.12) - 0.04, 0.0, 2.0), (s * (w / 2 + 0.12) + 0.04, 1.73, 2.1), "steel")
    return m


@landmark("fm06_book_barn", [B(-4.0, 0, -2.0, 4.0, 7.2, 2.0), B(-1.0, 0, 2.6, 1.0, 0.9, 3.0)], 2600,
          "a white classic barn front (8 m) with green trim and double doors; the carved, gilded open book over the doors "
          "(its two pages from the landmark cell, angled like an opened book), two brass gooseneck lamps, the plaque on a "
          "brick plinth in front")
def lm_book_barn(q):
    m = Mesh()
    m.box((-4.0, 0.0, -2.0), (4.0, 4.2, 2.0), "cream")
    gam = [(-4.15, 4.2), (4.15, 4.2), (3.2, 6.0), (0.0, 7.2), (-3.2, 6.0)]           # the gambrel gable
    m.prism_xy(gam, [], -2.1, 2.1, "roof")
    if q:
        m.box((-4.06, 0.0, 2.0), (-3.86, 4.2, 2.06), "accent")                       # green corner boards
        m.box((3.86, 0.0, 2.0), (4.06, 4.2, 2.06), "accent")
        m.box((-1.4, 0.0, 2.0), (1.4, 3.0, 2.05), "accent")                          # the double doors
        for s in (-1, 1):                                                            # their white X braces
            m.tube((s * 0.08, 0.15, 2.08), (s * 1.3, 2.85, 2.08), 0.045, "cream", n=4)
            m.tube((s * 1.3, 0.15, 2.08), (s * 0.08, 2.85, 2.08), 0.045, "cream", n=4)
    else:
        m.box((-1.4, 0.0, 2.0), (1.4, 3.0, 2.05), "accent")
    cid = "fm06_book_barn_landmark"
    from mk import cell_uv
    H, W = 2.3, cw(cid, 2.3)
    for side, sub, yaw in ((-1, (0.0, 0.0, 0.5, 1.0), 14.0), (1, (0.5, 0.0, 1.0, 1.0), -14.0)):
        a = math.radians(yaw)
        r = V(math.cos(a), 0, -math.sin(a))
        hinge = V(0.0, 4.95, 2.32)
        far = hinge + r * side * (W / 2)
        lo, hi = (far, hinge) if side < 0 else (hinge, far)
        uv = cell_uv(cid, sub)
        up = V(0, H / 2, 0)
        m.quad(tuple(lo - up), tuple(hi - up), tuple(hi + up), tuple(lo + up), "sign", 1.0, uv=uv)
        cover = Mesh()                                                               # the book's board cover behind
        cover.box((0.0 if side > 0 else -W / 2, -H / 2 - 0.06, -0.09), (W / 2 if side > 0 else 0.0, H / 2 + 0.06, -0.03), "accent2")
        place(m, cover, 0.0, 4.95, 2.32, yaw)
    for s in (-1, 1):                                                                # the gooseneck lamps
        sweep(m, [(s * 1.9, 6.3, 2.1), (s * 1.9, 6.6, 2.4), (s * 1.6, 6.55, 2.75)], 0.03, "brass", n=4)
        m.cyl(s * 1.6, 2.75, 0.18, 6.35, 6.5, "brass", n=8, r1=0.05)
        m.cyl(s * 1.6, 2.75, 0.15, 6.33, 6.35, "lamp", n=8)
    m.box((-1.0, 0.0, 2.6), (1.0, 0.9, 3.0), "wall")
    face(m, "fm06_book_barn_main", (0.0, 0.92 + 0.55, 2.8), 1.1, gap=0.03)
    return m


@landmark("fm07_weathervane", [B(-0.8, 0, -0.8, 0.8, 0.6, 0.8), B(-0.18, 0.6, -0.18, 0.18, 8.0, 0.18)], 1500,
          "a tall post crowned by the copper bull weathervane (its cell, both faces) over a ball finial; the red auction "
          "board on a timber backing at eye height")
def lm_weathervane(q):
    m = Mesh()
    m.box((-0.8, 0.0, -0.8), (0.8, 0.6, 0.8), "concrete")
    m.box((-0.15, 0.6, -0.15), (0.15, 8.0, 0.15), "wood")
    lathe(m, [(0.0, 0.0), (0.2, 0.1), (0.25, 0.25), (0.2, 0.4), (0.0, 0.5)], "brass", n=10 if q else 6, y0=8.0)
    m.cyl(0.0, 0.0, 0.03, 8.5, 9.3, "metal", n=4)
    face(m, "fm07_weathervane_landmark", (0.0, 9.3 + 1.4 - 0.1, 0.0), 2.8, gap=0.03)
    cid = "fm07_weathervane_main"
    for zc, yaw in ((0.21, 0.0), (-0.21, 180.0)):                                 # a board each side of the post
        w = backing(m, cid, (0.0, 3.4, zc), 1.6, 0.1)
        face(m, cid, (0.0, 3.4, zc + (0.08 if zc > 0 else -0.08)), 1.6, yaw, two=False)
        if q:
            for s in (-1, 1):
                m.box((s * (w / 2 + 0.05) - 0.02, 4.32, zc - 0.02), (s * (w / 2 + 0.05) + 0.02, 4.58, zc + 0.02), "metal")
                bulb(m, (s * (w / 2 + 0.05), 4.665, zc), 0.07, "bulb")
    return m


@landmark("fm08_brannock_trade_days", [B(-5.6, 0, -0.35, -4.9, 6.0, 0.35), B(4.9, 0, -0.35, 5.6, 6.0, 0.35), B(-4.9, 4.6, -0.2, 4.9, 7.6, 0.2)],
          3000, "the county-fair arch: white timber posts, an arched top beam, the gilt eagle on the crown; the navy "
          "lettered board (the main cell's band) on the arch, bunting swags on the posts; 9.8 m x 4.55 m clear",
          passes=[{"box": B(-4.85, 0, -0.6, 4.85, 4.55, 0.6), "kind": "open"}])
def lm_brannock(q):
    m = Mesh()
    for s in (-1, 1):
        m.box((s * 5.25 - 0.35, 0.0, -0.35), (s * 5.25 + 0.35, 0.5, 0.35), "concrete")
        m.box((s * 5.25 - 0.25, 0.5, -0.25), (s * 5.25 + 0.25, 6.0, 0.25), "cream")
        lathe(m, [(0.0, 0.0), (0.2, 0.05), (0.14, 0.3), (0.0, 0.45)], "brass", n=8, cx=s * 5.25, y0=6.0)
    n = 16 if q else 8
    arc = [(-5.0 + 10.0 * i / n, 5.6 + 1.3 * math.sin(math.pi * i / n), 0.0) for i in range(n + 1)]
    sweep(m, arc, 0.16, "cream", n=4)
    m.box((-5.0, 4.6, -0.12), (5.0, 4.8, 0.12), "cream")                            # the lower tie beam
    for i in range(1, n):                                                          # the spandrel spindles (clear of the board)
        x = -5.0 + 10.0 * i / n
        if abs(x) > 3.3 and (q or i % 2 == 0):
            m.box((x - 0.035, 4.8, -0.035), (x + 0.035, 5.6 + 1.3 * math.sin(math.pi * i / n) - 0.15, 0.035), "cream")
    cid = "fm08_brannock_trade_days_main"
    from mk import cell_uv
    sub = (0.08, 0.36, 0.92, 0.66)
    h = 1.3
    w = h * cell_aspect(cid) * (sub[2] - sub[0]) / (sub[3] - sub[1])
    m.box((-w / 2 - 0.08, 4.85, -0.06), (w / 2 + 0.08, 4.85 + h + 0.12, 0.06), "dark")
    for zz, yaw in ((0.09, 0.0), (-0.09, 180.0)):
        a = math.radians(yaw)
        card(m, "sign", cid, (0.0, 4.91 + h / 2, zz), (math.cos(a), 0, -math.sin(a)), (0, 1, 0), h, w=w, two=False, sub=sub)
    # the eagle: a gilt body, spread wings
    m.cyl(0.0, 0.0, 0.18, 6.9, 7.5, "brass", n=6, r1=0.1)
    m.prism_xy([(-1.1, 7.55), (-0.1, 7.25), (0.1, 7.25), (1.1, 7.55), (0.9, 7.75), (0.0, 7.45), (-0.9, 7.75)], [], -0.04, 0.04, "brass")
    if q:
        for s in (-1, 1):
            face(m, "fm08_brannock_trade_days_extra", (s * 5.6, 3.6, 0.28), 1.3, two=False, w=1.3)
            face(m, "fm08_brannock_trade_days_extra", (s * 5.6, 3.6, -0.28), 1.3, 180.0, two=False, w=1.3)
    return m


@landmark("fm09_boathouse_swap", [B(-3.0, 0, -1.8, 3.0, 5.4, 1.8)], 2200,
          "a green-and-white boathouse front with a striped awning over its doors, the boathouse cell (the neon 'Swap' "
          "script) on its gable, the turquoise neon fish on the ridge")
def lm_boathouse(q):
    m = Mesh()
    m.box((-3.0, 0.0, -1.8), (3.0, 3.2, 1.8), "cream")
    m.prism_xy([(-3.2, 3.2), (3.2, 3.2), (0.0, 5.3)], [], -1.9, 1.9, "accent")
    m.box((-1.6, 0.0, 1.8), (1.6, 2.5, 1.84), "accent")                             # the boat doors
    n = 8 if q else 4                                                               # the striped awning
    for k in range(n):
        x0, x1 = -2.0 + 4.0 * k / n, -2.0 + 4.0 * (k + 1) / n
        m.quad_facing((x0, 2.6, 2.9), (x1, 2.6, 2.9), (x1, 3.15, 1.85), (x0, 3.15, 1.85), (0, 1, 1), "accent2" if k % 2 else "cream")
        m.quad_facing((x0, 2.58, 2.9), (x1, 2.58, 2.9), (x1, 3.13, 1.85), (x0, 3.13, 1.85), (0, -1, -1), "accent2" if k % 2 else "cream", 0.7)
    for s in (-1, 1):
        m.tube((s * 1.95, 2.55, 2.85), (s * 1.95, 2.96, 1.85), 0.02, "metal", n=3)
    face(m, "fm09_boathouse_swap_main", (0.0, 4.4, 1.93), 2.4, two=False)
    face(m, "fm09_boathouse_swap_mascot", (0.0, 5.3 + 0.75, 0.0), 1.5, gap=0.03)
    m.box((-0.03, 5.15, -0.03), (0.03, 5.29, 0.03), "metal")
    return m


@landmark("fm10_four_corners_swap", [B(-0.13, 0, -0.13, 0.13, 6.6, 0.13), B(1.3, 0, -0.1, 3.3, 3.0, 0.1)], 1600,
          "a white finger-post tree pointing to the other markets (eight arrow boards), the circuit board (its cell) "
          "on two legs beside it, a sunset SWAP plaque on top")
def lm_four_corners(q):
    m = Mesh()
    m.box((-0.12, 0.0, -0.12), (0.12, 6.4, 0.12), "cream")
    lathe(m, [(0.0, 0.0), (0.16, 0.04), (0.0, 0.25)], "cream", n=6, y0=6.4)
    k = 0
    for i, yaw in enumerate((0, 45, 90, 135, 180, 225, 270, 315) if q else (0, 90, 180, 270)):
        y = 2.6 + 0.42 * i
        arr = Mesh()
        arr.prism_xy([(0.12, -0.11), (1.25, -0.11), (1.45, 0.0), (1.25, 0.11), (0.12, 0.11)], [], -0.02, 0.02, "cream" if i % 2 else "trim")
        place(m, arr, 0.0, y, 0.0, yaw)
    for x in (1.4, 3.2):
        m.box((x - 0.05, 0.0, -0.05), (x + 0.05, 3.0, 0.05), "cream")
    face(m, "fm10_four_corners_swap_main", (2.3, 1.65, 0.08), 2.4, two=False)
    face(m, "fm10_four_corners_swap_main", (2.3, 1.65, -0.08), 2.4, 180.0, two=False)
    m.box((1.45, 0.4, -0.045), (3.15, 2.9, 0.045), "dark")
    return m


@landmark("fm11_regatta_swap", [B(-0.2, 0, -0.2, 0.2, 11.0, 0.2), B(-1.8, 0, -0.5, 1.8, 0.6, 0.5)], 2200,
          "a tall white racing-sail pylon: a 3D mast and cambered sail in pastel stripes, regatta pennants strung "
          "to the masthead, the sail-pylon board (its cell) on the plinth")
def lm_regatta(q):
    m = Mesh()
    m.box((-1.8, 0.0, -0.5), (1.8, 0.6, 0.5), "cream")
    m.cyl(0.0, 0.0, 0.12, 0.6, 11.0, "metal", n=8 if q else 5, r1=0.07)
    rows, cols = (8, 5) if q else (4, 3)
    grid = []
    for i in range(rows + 1):                                                      # the sail: luff up the mast, foot at 1.6 m
        t = i / rows
        y = 1.8 + 8.8 * t
        L = 4.2 * (1.0 - t) + 0.15
        grid.append([(0.13 + L * j / cols, y + 0.5 * (j / cols) * (1 - t), 0.35 * math.sin(math.pi * j / cols) * (1 - 0.6 * t)) for j in range(cols + 1)])
    from mk import sheet
    sheet(m, grid, "cream", "accent", stripe=lambda i, j: i % 3 == 1, normal_hint=lambda p: (0, 0, 1))
    gb = [[(x, y, z - 0.03) for x, y, z in row] for row in grid]
    sheet(m, gb, "cream", "accent", stripe=lambda i, j: i % 3 == 1, normal_hint=lambda p: (0, 0, -1))
    m.tube((0.12, 1.75, 0.0), (4.4, 2.1, 0.0), 0.05, "metal", n=4)                   # the boom
    if q:
        from mk import catenary
        pts = catenary((0.0, 10.9, 0.0), (-3.5, 0.6, 0.0), 0.0, 10)
        for k in range(1, 10):
            x, y, z = pts[k]
            m.prism_xy([(x - 0.18, y), (x + 0.18, y), (x, y - 0.4)], [], -0.01, 0.01, ("accent", "accent2", "fabric")[k % 3])
        sweep(m, pts, 0.008, "rope", n=3)
        m.box((-3.55, 0.0, -0.05), (-3.45, 0.6, 0.05), "metal")                     # the pennant line's stake
    m.box((-1.7, 0.6, 0.35), (-0.25, 2.5, 0.45), "cream")
    face(m, "fm11_regatta_swap_main", (-0.97, 1.55, 0.48), 1.8, two=False)
    return m


WHEEL_R, WHEEL_Y = 2.5, 2.75


@landmark("fm12_millwheel_market", [B(-0.35, 0, -1.1, 0.35, 3.0, -0.75), B(-0.35, 0, 0.75, 0.35, 3.0, 1.1), B(3.6, 0, -0.2, 6.6, 2.4, 0.2),
                                    B(-3.0, 0, -1.2, 3.0, 0.35, 1.2)], 1800,
          "the mill's timber frame and race for a 5 m waterwheel that really turns (sign_fm12_millwheel_market_wheel at "
          "`wheel`, turning about local z), the carved oak slab board on posts beside it",
          anchors={"wheel": [0.0, WHEEL_Y, 0.0, 0]})
def lm_millwheel(q):
    m = Mesh()
    m.box((-3.0, 0.0, -1.2), (3.0, 0.35, 1.2), "concrete")                          # the stone pit (the wheel clears it)
    for z in (-0.92, 0.92):                                                        # A-frames carrying the axle
        for s in (-1, 1):
            m.tube((s * 1.6, 0.35, z), (s * 0.18, WHEEL_Y - 0.2, z), 0.1, "wood", n=4)
        m.box((-0.3, WHEEL_Y - 0.2, z - 0.17), (0.3, WHEEL_Y + 0.25, z + 0.17), "wood")
    # the race: a trough on trestles feeding the wheel's top from -x
    m.box((-5.5, WHEEL_Y + WHEEL_R + 0.2, -0.45), (-0.4, WHEEL_Y + WHEEL_R + 0.28, 0.45), "wood")
    for z in (-0.44, 0.40):
        m.box((-5.49, WHEEL_Y + WHEEL_R + 0.28, z), (-0.41, WHEEL_Y + WHEEL_R + 0.55, z + 0.04), "wood")
    for x in (-5.2, -3.2):
        for z in (-0.4, 0.4):
            m.box((x - 0.06, 0.0, z - 0.06), (x + 0.06, WHEEL_Y + WHEEL_R + 0.2, z + 0.06), "wood")
    if q:
        m.box((-1.6, WHEEL_Y + WHEEL_R + 0.285, -0.38), (-0.45, WHEEL_Y + WHEEL_R + 0.3, 0.38), "glow_b")  # the water sheet (lit)
    w = backing(m, "fm12_millwheel_market_main", (5.1, 1.4, 0.0), 1.4, 0.14)
    front_back(m, "fm12_millwheel_market_main", (5.1, 1.4, 0.0), 1.4, 0.1)
    for s in (-1, 1):
        m.box((5.1 + s * (w / 2 + 0.05) - 0.07, 0.0, -0.07), (5.1 + s * (w / 2 + 0.05) + 0.07, 2.3, 0.07), "wood")
    return m


def millwheel_wheel(q):
    m = Mesh()
    n = 16 if q else 10
    for z in (-0.5, 0.5):
        ring_torus(m, (0.0, 0.0, z), WHEEL_R - 0.08, 0.08, "wood", axis="z", n=n * 2 if q else n, k=4)
        for k in range(8 if q else 6):
            a = math.tau * k / (8 if q else 6)
            m.tube((0.24 * math.cos(a), 0.24 * math.sin(a), z), ((WHEEL_R - 0.17) * math.cos(a), (WHEEL_R - 0.17) * math.sin(a), z), 0.05, "wood", n=4)
    hub = Mesh()
    hub.cyl(0.0, 0.0, 0.26, -0.75, 0.75, "dark", n=8)
    from mk import rot_x
    m.add(hub, rot_x(90))
    for k in range(n):                                                             # paddles between the rims
        a = math.tau * (k + 0.5) / n
        c, s_ = math.cos(a), math.sin(a)
        r0, r1 = WHEEL_R - 0.55, WHEEL_R + 0.12
        pts = [(r0 * c - 0.03 * -s_, r0 * s_ - 0.03 * c), (r1 * c - 0.03 * -s_, r1 * s_ - 0.03 * c), (r1 * c + 0.03 * -s_, r1 * s_ + 0.03 * c),
               (r0 * c + 0.03 * -s_, r0 * s_ + 0.03 * c)]
        m.prism_xy(pts, [], -0.42, 0.42, "wood", 0.95)
        if q:
            for z in (-0.3, 0.3):
                bulb(m, ((r1 + 0.07) * c, (r1 + 0.07) * s_, z), 0.06, "bulb")
    return m


LANDMARK_EXTRA = {"sign_fm12_millwheel_market_wheel": dict(build=millwheel_wheel, frame=[], budget=2400, collide="none",
                                                          moving={"kind": "spin", "axis": [0, 0, 1], "rpm": 3.0, "pivot": [0, 0, 0]},
                                                          notes="the Millwheel's turning wheel (5 m, 16 paddles edged with bulbs): spin about +z at its origin; placed at sign_fm12's `wheel` anchor",
                                                          foot=[5.4, 1.1])}


@landmark("fm13_traders_landing", [B(-6.1, 0, -1.5, -4.9, 6.5, 1.5), B(4.9, 0, -1.5, 6.1, 6.5, 1.5), B(-4.9, 4.6, -1.2, 4.9, 6.5, 1.2)], 5000,
          "the bow of a lake freighter as the entrance arch: red-over-black hull-plate pylons, the forecastle beam with "
          "its rail, the anchor, the TRADERS' Landing cell on both faces; Cap'n Harrow by the left pylon; 9.8 x 4.6 m clear "
          "(the lighthouse pylon is sign_fm13_traders_landing_lighthouse)",
          passes=[{"box": B(-4.85, 0, -1.6, 4.85, 4.55, 1.6), "kind": "open"}])
def lm_traders(q):
    m = Mesh()
    for s in (-1, 1):
        x0, x1 = sorted((s * 4.9, s * 6.1))
        prism_zy(m, [(-1.4, 0.0), (1.2, 0.0), (1.5, 2.2), (1.5, 6.5), (-1.5, 6.5), (-1.5, 2.2)], x0, x1, "dark")
        prism_zy(m, [(-1.53, 2.2), (1.53, 2.2), (1.53, 6.53), (-1.53, 6.53)], x0 - 0.03, x1 + 0.03, "accent")
    # the forecastle beam: the bow seen end-on, a raked stem toward +z
    prism_zy(m, [(-1.2, 4.6), (1.2, 4.6), (1.2, 6.5), (-1.2, 6.5)], -4.9, 4.9, "accent")
    m.box((-4.88, 6.5, -1.18), (4.88, 6.62, 1.18), "trim")
    if q:
        for x in (-4.6 + 0.92 * k for k in range(11)):                             # the forecastle rail
            m.box((x - 0.025, 6.62, 1.05), (x + 0.025, 7.45, 1.1), "cream")
        m.box((-4.7, 7.45, 1.03), (4.7, 7.52, 1.12), "cream")
        for s in (-1, 1):                                                          # portholes
            for k in range(3):
                x, y = s * (5.5), 3.1 + 1.0 * k
                bulb(m, (x, y, 1.53 + 0.12), 0.12, "lamp")
        anchor = [(-0.1, 5.2), (0.1, 5.2), (0.1, 4.75), (0.45, 4.95), (0.5, 4.85), (0.0, 4.55), (-0.5, 4.85), (-0.45, 4.95), (-0.1, 4.75)]
        t = Mesh()
        t.prism_xy(anchor, [], 0.0, 0.06, "metal")
        place(m, t, -3.6, 0.0, 1.2)
    front_back(m, "fm13_traders_landing_main", (0.0, 5.72, 0.0), 2.2, 1.25)
    face(m, "fm13_traders_landing_mascot", (-7.5, 1.25, 0.6), 2.5, gap=0.03)
    return m


def lighthouse(q):
    m = Mesh()
    n = 12 if q else 8
    m.cyl(0.0, 0.0, 1.6, 0.0, 0.6, "concrete", n=n)
    bands = [(1.25, 0.6), (1.15, 2.6), (1.05, 4.6), (0.95, 6.6), (0.85, 8.6), (0.8, 9.6)]
    for k in range(len(bands) - 1):
        (r0, y0), (r1, y1) = bands[k], bands[k + 1]
        m.cyl(0.0, 0.0, r0, y0 + 0.002 * k, y1 + 0.002 * k, "accent" if k % 2 == 0 else "cream", n=n, r1=r1)
    m.cyl(0.0, 0.0, 1.3, 9.612, 9.75, "dark", n=n)                               # the gallery
    if q:
        ring_torus(m, (0.0, 10.55, 0.0), 1.25, 0.025, "dark", n=n)
        for k in range(8):
            a = math.tau * (k + 0.5) / 8
            m.box((1.25 * math.cos(a) - 0.02, 9.75, 1.25 * math.sin(a) - 0.02), (1.25 * math.cos(a) + 0.02, 10.53, 1.25 * math.sin(a) + 0.02), "dark")
    m.cyl(0.0, 0.0, 0.7, 9.75, 11.0, "glass", n=8, caps=False)
    m.cyl(0.0, 0.0, 0.32, 9.95, 10.65, "lamp", n=6)
    m.cyl(0.0, 0.0, 0.78, 11.0, 11.12, "accent", n=8)
    lathe(m, [(0.74, 0.0), (0.0, 0.9)], "accent", n=8, y0=11.12)
    m.cyl(0.0, 0.0, 0.04, 12.0, 12.4, "metal", n=4)
    m.box((-0.5, 0.6, 0.95), (0.5, 2.6, 1.42), "cream")                            # the door porch
    m.box((-0.38, 0.6, 1.42), (0.38, 2.3, 1.45), "dark")
    m.prism_xy([(-0.6, 2.6), (0.6, 2.6), (0.0, 3.0)], [], 0.95, 1.46, "accent")
    m.box((-0.75, 6.5, 1.0), (0.75, 7.1, 1.06), "cream")                          # the MARKET band
    from mk import cell_uv
    uv = cell_uv("fm13_traders_landing_landmark", (0.38, 0.40, 0.62, 0.46))
    m.quad((-0.7, 6.55, 1.09), (0.7, 6.55, 1.09), (0.7, 7.05, 1.09), (-0.7, 7.05, 1.09), "sign", 1.0, uv=uv)
    return m


LANDMARK_EXTRA["sign_fm13_traders_landing_lighthouse"] = dict(build=lighthouse, frame=[B(-1.6, 0, -1.6, 1.6, 0.6, 1.6), B(-1.25, 0.6, -1.25, 1.25, 12.4, 1.25)],
                                                              budget=1800, collide="frame", moving=None, foot=[3.2, 3.2],
                                                              notes="Traders' Landing's lighthouse pylon (12.4 m): red and white bands, a gallery, the lit lantern room; `beacon` is the lamp",
                                                              anchors={"beacon": [0.0, 10.3, 0.0, 0]})


@landmark("fm14_iron_wheel", [B(-4.5, 0, -1.3, 4.5, 1.2, 1.3), B(-2.05, 1.2, -0.45, -1.15, 7.4, 0.45), B(2.0, 1.2, -0.15, 4.4, 9.0, 0.15)], 5500,
          "a 6 m locomotive driving wheel (tyre, 12 spokes with chase bulbs, counterweight, hub) on a Streamline "
          "Moderne plinth with speed lines, the IRON WHEEL fin (its cell, both faces) beside it")
def lm_iron_wheel(q):
    from mk import rounded_rect, rot_x
    m = Mesh()
    m.prism_xz(rounded_rect(9.0, 2.6, 1.1 if q else 0.9, 4 if q else 2), 0.0, 1.2, "cream")
    if q:
        for y in (0.35, 0.6, 0.85):                                                # speed lines (strips 2.7 cm proud)
            for sz in (-1, 1):
                t = Mesh()
                laps(t, -3.4, 3.4, [y], 1.3, slot="accent", h=0.06)
                place(m, t, yaw=0 if sz > 0 else 180)
    R, Y, X = 3.0, 4.35, -1.6
    nw = 32 if q else 16
    ring_torus(m, (X, Y, 0.0), R - 0.14, 0.14, "dark", axis="z", n=nw, k=6 if q else 4)
    ns = 12 if q else 8
    for k in range(ns):
        a = math.tau * k / ns
        c, sn = math.cos(a), math.sin(a)
        m.tube((X + 0.45 * c, Y + 0.45 * sn, 0.0), (X + (R - 0.27) * c, Y + (R - 0.27) * sn, 0.0), 0.07, "dark", n=4)
        if q:
            for t in (0.4, 0.6, 0.8):
                rr = 0.45 + (R - 0.72) * t
                for z in (0.135, -0.135):
                    bulb(m, (X + rr * c, Y + rr * sn, z), 0.055, "bulb")
    hub = Mesh()
    hub.cyl(0.0, 0.0, 0.45, -0.35, 0.35, "steel", n=10 if q else 6)
    m.add(hub, lambda p: (rot_x(90)(p)[0] + X, rot_x(90)(p)[1] + Y, rot_x(90)(p)[2]))
    arc0 = [(X + 1.0 * math.cos(math.radians(a)), Y + 1.0 * math.sin(math.radians(a))) for a in range(200, 341, 20)]
    arc1 = [(X + 2.45 * math.cos(math.radians(a)), Y + 2.45 * math.sin(math.radians(a))) for a in range(340, 199, -20)]
    m.prism_xy(arc0 + arc1, [], 0.08, 0.2, "dark", 0.85)                          # the counterweight (front)
    m.box((X - 0.4, 1.2, -0.42), (X + 0.4, Y - 0.46, 0.42), "steel")               # the axle-box pedestal
    fin = [(2.0, 1.2), (4.4, 1.2), (4.4, 7.6), (3.9, 8.6), (2.9, 9.0), (2.0, 9.0)]
    m.prism_xy(fin, [], -0.15, 0.15, "accent2")
    if q:
        for y in (2.0, 2.4, 2.8):
            m.box((1.95, y, -0.17), (4.45, y + 0.08, 0.17), "trim")
    front_back(m, "fm14_iron_wheel_main", (3.2, 5.6, 0.0), 2.0, 0.18)
    return m


@landmark("fm15_red_granary", [B(-3.0, 0, -2.0, 3.0, 6.2, 2.0)], 1800,
          "a red granary with its gable cell (the white sunburst and the Googie 'Red Granary' script) across the front, "
          "chase bulbs up both rakes of the roof")
def lm_red_granary(q):
    m = Mesh()
    m.box((-3.0, 0.0, -2.0), (3.0, 3.6, 2.0), "accent")
    m.prism_xy([(-3.2, 3.6), (3.2, 3.6), (0.0, 6.1)], [], -2.1, 2.1, "roof")
    m.box((-3.05, 0.0, -2.05), (3.05, 0.5, 2.05), "concrete")
    if q:
        m.box((-1.0, 0.5, 2.0), (1.0, 2.8, 2.04), "cream")                       # the doors' white frame
        m.box((-0.9, 0.5, 2.04), (0.9, 2.7, 2.07), "accent2")
    face(m, "fm15_red_granary_main", (0.0, 4.1, 2.14), 3.8, two=False)
    if q:
        for s in (-1, 1):
            bulbs_line(m, (s * 3.1, 3.72, 2.18), (s * 0.08, 6.12, 2.18), 12, "bulb_a")
    return m


@landmark("fm16_tall_tamarack", [B(-0.5, 0, -0.5, 0.5, 14.0, 0.5), B(-2.6, 0, 2.4, 2.6, 2.6, 2.7), B(-2.6, 0, -2.6, 2.6, 0.4, 2.6)], 4000,
          "a 14 m fibreglass tamarack (tiered golden foliage over a trunk) wound with coloured bulbs, the 1950s "
          "boomerang board on two posts in front")
def lm_tall_tamarack(q):
    m = Mesh()
    n = 10 if q else 6
    m.cyl(0.0, 0.0, 2.6, 0.0, 0.4, "concrete", n=n)
    m.cyl(0.0, 0.0, 0.45, 0.4, 13.5, "wood", n=6, r1=0.12)
    tiers = [(2.3, 2.2, 5.0), (2.0, 4.2, 6.6), (1.7, 6.0, 8.2), (1.35, 7.8, 9.8), (1.0, 9.5, 11.4), (0.65, 11.2, 13.2), (0.35, 12.8, 14.0)]
    for k, (r, y0, y1) in enumerate(tiers):
        lathe(m, [(0.4, 0.0), (r, 0.25), (r * 0.7, (y1 - y0) * 0.55), (0.0, y1 - y0)], "plant" if k % 2 == 0 else "accent", n=n, y0=y0)
    if q:
        slots = ("bulb_a", "bulb_b", "bulb_c", "bulb_d")
        nb = 46
        for k in range(nb):
            t = k / nb
            y = 2.4 + 11.0 * t
            # the tier's radius at y, just outside it
            r = 0.0
            for (rr, y0, y1) in tiers:
                if y0 <= y <= y1:
                    f = (y - y0) / (y1 - y0)
                    r = max(r, rr if f < 0.12 else rr - (rr - rr * 0.7) * min(1.0, (f - 0.12) / 0.43) if f < 0.55 else rr * 0.7 * (1 - (f - 0.55) / 0.45))
            a = 5.5 * math.tau * t
            bulb(m, ((r + 0.12) * math.cos(a), y, (r + 0.12) * math.sin(a)), 0.08, slots[k % 4])
    face(m, "fm16_tall_tamarack_main", (0.0, 1.7, 2.55), 1.7, gap=0.04)
    for s in (-1, 1):
        m.box((s * 1.6 - 0.06, 0.0, 2.43), (s * 1.6 + 0.06, 1.0, 2.49), "metal")
    return m


@landmark("fm17_elevator_flea_days", [B(-3.0, 0, -2.5, 3.0, 18.0, 2.5), B(-7.2, 0, -6.95, 7.2, 16.0, -2.55)], 3000,
          "the town's grain elevator: three concrete silos behind a tall headhouse whose front carries the giant "
          "pastel postcard ELEVATOR FLEA DAYS (its cell)")
def lm_elevator(q):
    m = Mesh()
    n = 12 if q else 8
    for x in (-5.0, 0.0, 5.0):
        lathe(m, [(2.2, 0.0), (2.2, 15.0), (0.4, 15.9), (0.0, 16.0)], "concrete", n=n, cx=x, cz=-4.75)
    m.box((-3.0, 0.0, -2.5), (3.0, 17.0, 2.5), "cream")
    m.prism_xy([(-3.2, 17.0), (3.2, 17.0), (0.0, 18.0)], [], -2.6, 2.6, "roof")
    if q:
        m.box((-1.0, 0.0, 2.5), (1.0, 2.8, 2.54), "dark")                         # the bin door
        m.box((-2.6, 16.2, 2.5), (2.6, 16.5, 2.53), "trim")
    face(m, "fm17_elevator_flea_days_main", (0.0, 8.8, 2.56), 5.6, two=False)
    return m


@landmark("fm18_route30_swap_meet", [B(-1.7, 0, -0.25, -1.3, 7.5, 0.25), B(1.3, 0, -0.25, 1.7, 7.5, 0.25), B(-2.2, 7.5, -0.3, 2.2, 12.3, 0.3)], 4000,
          "a giant US 30 shield cabinet (its cell both faces, turquoise neon round it) on twin legs with a bulb starburst, "
          "the boomerang SWAP MEET arrow below, Ozzie the mechanic at the foot")
def lm_route30(q):
    m = Mesh()
    for s in (-1, 1):
        m.box((s * 1.5 - 0.2, 0.0, -0.2), (s * 1.5 + 0.2, 7.6, 0.2), "accent2")
        m.box((s * 1.5 - 0.3, 0.0, -0.3), (s * 1.5 + 0.3, 0.45, 0.3), "concrete")
    cid = "fm18_route30_swap_meet_landmark"
    h = 4.6
    w = cw(cid, h)
    shield = [(-w / 2, 7.6 + h * 0.86), (-w / 2 * 0.92, 7.6 + h * 0.98), (-w * 0.2, 7.6 + h * 0.92), (0.0, 7.6 + h), (w * 0.2, 7.6 + h * 0.92),
              (w / 2 * 0.92, 7.6 + h * 0.98), (w / 2, 7.6 + h * 0.86), (w / 2 * 0.92, 7.6 + h * 0.35), (0.0, 7.6), (-w / 2 * 0.92, 7.6 + h * 0.35)]
    m.prism_xy([(x * 0.94, 7.6 + (y - 7.6) * 0.94 + h * 0.03) for x, y in shield], [], -0.22, 0.22, "cream")
    front_back(m, cid, (0.0, 7.6 + h / 2, 0.0), h, 0.25)
    if q:
        m0 = ((shield[0][0] + shield[-1][0]) * 0.5, (shield[0][1] + shield[-1][1]) * 0.5)
        m1 = (m0[0] * 0.96 + shield[-1][0] * 0.04, m0[1] * 0.96 + shield[-1][1] * 0.04)
        sweep(m, [(m0[0], m0[1], 0.3)] + [(x, y, 0.3) for x, y in shield] + [(m1[0], m1[1], 0.3)], 0.035, "neon", n=4)
        for k in range(10):                                                        # the starburst
            a = math.tau * k / 10
            m.tube((3.3 + 0.1 * math.cos(a), 12.9 + 0.1 * math.sin(a), 0.0), (3.3 + 0.9 * math.cos(a), 12.9 + 0.9 * math.sin(a), 0.0), 0.035, "trim", n=4)
            bulb(m, (3.3 + 0.98 * math.cos(a), 12.9 + 0.98 * math.sin(a), 0.0), 0.08, "bulb_a")
        m.box((3.25, 9.1, -0.05), (3.35, 12.78, 0.05), "trim")
        m.box((2.0, 9.0, -0.05), (3.4, 9.1, 0.05), "trim")
        lathe(m, [(0.0, 0.0), (0.12, 0.12), (0.0, 0.24)], "brass", n=6, cx=3.3, y0=12.78)
    m2 = "fm18_route30_swap_meet_main"
    face(m, m2, (0.0, 5.7, 0.28), 1.9, two=False)
    face(m, m2, (0.0, 5.7, -0.28), 1.9, 180.0, two=False)
    face(m, "fm18_route30_swap_meet_mascot", (2.9, 1.25, 0.6), 2.5, gap=0.03)
    return m


@landmark("fm19_la_pulga_verde", [B(-1.0, 0, -0.5, 1.0, 9.6, 0.5), B(3.7, 0, -0.35, 4.3, 7.6, 0.35)], 3000,
          "a stucco pier pylon under a mission-tile cap with the neon pier-and-palm cell both faces, a palm beside it")
def lm_pulga(q):
    m = Mesh()
    m.box((-1.0, 0.0, -0.5), (1.0, 9.0, 0.5), "cream")
    m.box((-1.15, 0.0, -0.6), (1.15, 0.6, 0.6), "accent2")
    m.prism_xy([(-1.25, 9.0), (1.25, 9.0), (0.0, 9.6)], [], -0.65, 0.65, "roof")
    front_back(m, "fm19_la_pulga_verde_main", (0.0, 5.4, 0.0), 4.6, 0.53)
    # the palm: a curved trunk and a crown of fronds
    pts = [(4.0, 0.0, 0.0), (4.1, 2.0, 0.05), (4.35, 4.0, 0.1), (4.7, 6.0, 0.1), (5.1, 7.6, 0.05)]
    sweep(m, pts, 0.2 if q else 0.18, "wood", n=6 if q else 4)
    nf = 9 if q else 5
    top = V(5.1, 7.6, 0.05)
    for k in range(nf):
        a = math.tau * k / nf
        d = V(math.cos(a), 0, math.sin(a))
        p1 = top + d * 1.2 + V(0, 0.3, 0)
        p2 = top + d * 2.2 + V(0, -0.6, 0)
        side = V(-math.sin(a), 0, math.cos(a)) * 0.35
        m.quad_facing(tuple(top + V(0, 0.15, 0)), tuple(p1 + side), tuple(p2), tuple(p1 - side), (0, 1, 0), "plant")
        m.quad_facing(tuple(top + V(0, 0.13, 0)), tuple(p1 + side + V(0, -0.02, 0)), tuple(p2 + V(0, -0.02, 0)), tuple(p1 - side + V(0, -0.02, 0)),
                      (0, -1, 0), "plant", 0.7)
    return m


@landmark("fm20_starlite_swap", [B(-9.0, 0, -1.6, 9.0, 1.2, 1.6), B(-9.0, 1.2, -0.4, 9.0, 13.0, 0.4)], 6000,
          "the old 20 m drive-in screen tower: a stepped stucco base, the screen in sunset bands with the 1950s neon "
          "STARLITE SWAP script, Sunny on the top corner, steel bracing behind, the marquee board in front "
          "(THIS WEEKEND ISLAND FAIR)", anchors={"marquee": [6.0, 0.0, 3.0, 0]})
def lm_starlite(q):
    m = Mesh()
    m.box((-9.0, 0.0, -1.6), (9.0, 1.2, 1.6), "accent2")
    if q:
        m.box((-9.2, 0.0, -1.8), (9.2, 0.4, 1.8), "cream")
    bands = ["accent", "fabric", "trim", "cream", "accent2"]
    y0, y1 = 1.2, 13.0
    m.box((-9.0, y0, -0.4), (9.0, y1, 0.4), "cream")
    for k, sl in enumerate(bands):                                                  # the screen face in sunset bands
        ya = y0 + (y1 - y0) * k / len(bands)
        yb = y0 + (y1 - y0) * (k + 1) / len(bands)
        m.quad((-8.98, ya, 0.4 + 0.027), (8.98, ya, 0.4 + 0.027), (8.98, yb, 0.4 + 0.027), (-8.98, yb, 0.4 + 0.027), sl)
    m.box((-9.2, 13.0, -0.5), (9.2, 13.3, 0.5), "dark")
    face(m, "fm20_starlite_swap_main", (0.0, 7.2, 0.48), 10.5, two=False)
    face(m, "fm20_starlite_swap_mascot", (7.6, 13.3 + 1.6, 0.0), 3.2, gap=0.04)
    if q:                                                                          # the bracing behind
        for x in (-7.5, -2.5, 2.5, 7.5):
            m.tube((x, 1.2, -1.55), (x, 12.6, -0.45), 0.09, "steel", n=4)
            m.box((x - 0.1, 1.2, -0.45), (x + 0.1, 12.8, -0.4), "steel")
    return m


def starlite_marquee(q):
    t = Mesh()
    w = cw("fm20_starlite_swap_extra", 2.4)
    face(t, "fm20_starlite_swap_extra", (0.0, 1.9, 0.0), 2.4, gap=0.04)
    for s in (-1, 1):
        t.box((s * w * 0.33 - 0.06, 0.0, -0.08), (s * w * 0.33 + 0.06, 0.75, -0.06), "dark")
    return t


_mw = cw("fm20_starlite_swap_extra", 2.4)
LANDMARK_EXTRA["sign_fm20_starlite_swap_marquee"] = dict(build=starlite_marquee, frame=[B(-_mw / 2, 0, -0.1, _mw / 2, 3.1, 0.1)], budget=60,
                                                         collide="frame", moving=None, foot=[round(_mw, 2), 0.2],
                                                         notes="the Starlite's marquee board (the extra cell) on two legs; at sign_fm20's `marquee`")


@landmark("fm21_carousel_swap", [B(-0.2, 0, -0.2, 0.2, 6.6, 0.2), B(-3.4, 0, -3.4, 3.4, 0.35, 3.4)], 4000,
          "a carousel canopy (16 candy-striped gores, scalloped valance, a bulb ring) on a striped centre pole, the giant "
          "carousel horse (its cell, both faces) on its brass pole, THE CAROUSEL SWAP board on the canopy front")
def lm_carousel(q):
    m = Mesh()
    n = 16 if q else 8
    m.cyl(0.0, 0.0, 3.4, 0.0, 0.35, "cream", n=n)
    for k in range(9):                                                            # the striped centre pole (open ends: hidden)
        m.cyl(0.0, 0.0, 0.18, 0.35 + 0.672 * k, 0.35 + 0.672 * (k + 1), "accent" if k % 2 == 0 else "cream", n=8, caps=False)
    R, ye, yp = 3.3, 4.55, 6.6
    for k in range(n):
        a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
        p0 = (R * math.cos(a0), ye, R * math.sin(a0))
        p1 = (R * math.cos(a1), ye, R * math.sin(a1))
        mid_ = ((p0[0] + p1[0]) / 2, 0.6, (p0[2] + p1[2]) / 2)
        sl = "accent" if k % 2 == 0 else "cream"
        m.tri_facing(p0, p1, (0.0, yp, 0.0), mid_, sl)
        m.tri_facing((p0[0] * 0.96, ye - 0.03, p0[2] * 0.96), (p1[0] * 0.96, ye - 0.03, p1[2] * 0.96), (0.0, yp - 0.05, 0.0),
                     (-mid_[0], -1.0, -mid_[2]), sl, 0.7)
        # the valance scallop under the eave
        m.quad_facing(p0, p1, (p1[0], ye - 0.45, p1[2]), (p0[0], ye - 0.45, p0[2]), (mid_[0], 0, mid_[2]), "accent2")
        m.quad_facing((p0[0] * 0.995, ye, p0[2] * 0.995), (p1[0] * 0.995, ye, p1[2] * 0.995), (p1[0] * 0.995, ye - 0.45, p1[2] * 0.995),
                      (p0[0] * 0.995, ye - 0.45, p0[2] * 0.995), (-mid_[0], 0, -mid_[2]), "accent2", 0.7)
        if q:
            am = (a0 + a1) / 2
            bulb(m, ((R + 0.08) * math.cos(am), ye - 0.5, (R + 0.08) * math.sin(am)), 0.07, ("bulb_a", "bulb_b", "bulb_c", "bulb_d")[k % 4])
    m.cyl(0.0, 0.0, 0.08, yp - 0.05, yp + 0.4, "brass", n=6)
    lathe(m, [(0.0, 0.0), (0.18, 0.15), (0.0, 0.35)], "brass", n=6, y0=yp + 0.4)
    # the horse on its brass pole (the pole stops at the horse's back and belly: no pole through the card)
    cid = "fm21_carousel_swap_landmark"
    hz = 1.35
    m.cyl(0.0, hz, 0.04, 0.35, 0.95, "brass", n=6)
    m.cyl(0.0, hz, 0.04, 3.25, ye - 0.45, "brass", n=6)
    face(m, cid, (0.0, 0.95 + 1.15, hz), 2.3, gap=0.04)
    face(m, "fm21_carousel_swap_main", (0.0, ye + 0.55, R + 0.12), 2.2, two=False)
    return m


@landmark("fm22_pelican_swap", [B(-2.2, 0, -1.0, 2.2, 0.5, 1.0), B(0.6, 0.5, -0.15, 2.0, 5.0, 0.15)], 1500,
          "the fibreglass pelican in a sun hat on its piling (its cell, both faces) on a sand plinth, beside the "
          "surfboard board (THE PELICAN SWAP) standing in a rack")
def lm_pelican(q):
    m = Mesh()
    m.box((-2.2, 0.0, -1.0), (2.2, 0.5, 1.0), "cream")
    face(m, "fm22_pelican_swap_mascot", (-0.9, 0.5 + 1.4, 0.0), 2.8, gap=0.04)
    face(m, "fm22_pelican_swap_main", (1.3, 0.5 + 2.25, 0.0), 4.5, gap=0.05)
    for s in (-1, 1):                                                              # the rack: two uprights, a rail each side
        x = 1.3 + s * 0.62
        m.box((x - 0.05, 0.5, -0.16), (x + 0.05, 1.45, -0.09), "wood")
        m.box((x - 0.05, 0.5, 0.04), (x + 0.05, 1.45, 0.11), "wood")
    return m


# ------------------------------------------------------------------ the shared island-fair boards
def dotmatrix(q):
    m = Mesh()
    cid = "shared_island_fair_dotmatrix"
    w = cw(cid, 1.5)
    m.box((-w / 2 - 0.08, 2.2, -0.08), (w / 2 + 0.08, 3.86, 0.08), "dark")
    front_back(m, cid, (0.0, 3.03, 0.0), 1.5, 0.11)
    for s in (-1, 1):
        m.box((s * w * 0.35 - 0.06, 0.0, -0.06), (s * w * 0.35 + 0.06, 2.2, 0.06), "steel")
    return m


def skein_banner(q):
    m = Mesh()
    cid = "shared_skein_banner"
    for s in (-1, 1):
        m.box((s * 3.0 - 0.07, 0.0, -0.07), (s * 3.0 + 0.07, 4.6, 0.07), "steel")
    for x in (-1.4, 1.4):
        face(m, cid, (x, 3.4, 0.0), 2.2, w=2.78, gap=0.03)
    return m


for mk_, d in LANDMARKS.items():
    fr = d["frame"]
    lo = [min(b[0][k] for b in fr) for k in range(3)]
    hi = [max(b[1][k] for b in fr) for k in range(3)]
    piece("sign_" + mk_, "sign", d["build"], kind="landmark", foot=None, lod1="keep",
          frame=fr, passes=d["passes"], anchors=d["anchors"], budget=d["budget"], palette=mk_, notes=d["notes"])
for pid, d in LANDMARK_EXTRA.items():
    piece(pid, "sign", d["build"], kind="landmark", foot=None, lod1="keep", collide=d["collide"], frame=d["frame"],
          anchors=d.get("anchors"), budget=d["budget"], palette=pid[5:].rsplit("_", 1)[0] if pid.count("_") > 2 else pid,
          moving=d["moving"], notes=d["notes"])
piece("fm_board_island_fair", "sign", dotmatrix, kind="sign", foot=[2.6, 0.2], lod1="keep", frame=[B(-1.4, 0, -0.12, 1.4, 3.9, 0.12)],
      budget=80, palette="skein", notes="the lit ISLAND FAIR dot-matrix board on two legs (any market while islands are moored)")
piece("fm_skein_banner", "sign", skein_banner, kind="sign", foot=[6.14, 0.14], lod1="keep",
      frame=[B(-3.07, 0, -0.07, -2.93, 4.6, 0.07), B(2.93, 0, -0.07, 3.07, 4.6, 0.07)],
      passes=[{"box": B(-2.9, 0, -0.5, 2.9, 2.25, 0.5), "kind": "open"}], budget=60, palette="skein",
      notes="the Skein banner (clan pennants and lanterns) strung on two posts across an entrance while an island is moored")
