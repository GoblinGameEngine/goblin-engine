#!/usr/bin/env python3
"""
map_preview.py -- 2D overhead preview of the station ring's settlement /
water / road layout, generated straight from the research rules
(research/generator_rules.md) rather than from the running game.

Why a standalone script: the in-engine FlatMapRenderer tried to rasterise
the fully built 3D world and locked up the laptop (~7GB). A layout map only
needs the layout *rules*, so this computes them directly -- deterministic
(fixed seed), no Godot, a few hundred MB.

The ring is drawn unrolled: horizontal = arc length s (0..3,142 m, the left
and right edges join), vertical = axial x (-1,500 m port wall at the top,
+1,500 m starboard wall at the bottom). 1 px = 1 m.

Usage:  python3 tools/map_preview.py OUT.png      (needs pillow + numpy)
"""

import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ------------------------------------------------------------------ geometry
R = 500.0
C = 2 * math.pi * R          # 3,141.6 m circumference
W = 3000.0                   # wall to wall
HW = W / 2
CW, WH = int(round(C)), int(W)
OFFS = (-C, 0.0, C)          # draw every primitive three times so the seam wraps

# River harmonic stack -- identical to TerrainHeight.gd (generator_rules §10)
A1, A2, A3 = 150.0, 45.0, 25.0
PHI1, PHI2, PHI3, PHI4 = math.pi / 2, -math.pi / 4, -math.pi / 4, 0.0
CH_HALF = 22.5               # 45 m channel
# Lake per §10: 1,000 m x 300 m, necked 100-150 m at both ends
LAKE_S, LAKE_HALF_LEN, LAKE_HW, LAKE_NECK = math.pi / 4 * R, 500.0, 150.0, 130.0
H_BLUFF, Z1 = 18.0, 10.0     # §16

rng = random.Random(1234)


def rx(s):
    th = np.asarray(s, dtype=np.float64) / R
    env = A1 * (1 + 0.3 * np.sin(2 * th + PHI4))
    return env * np.sin(6 * th + PHI1) + A2 * np.sin(13 * th + PHI2) + A3 * np.sin(th + PHI3)


def rxf(s):
    return float(rx(s))


def rcx(s):
    """River centreline blended into the lake's centre where the lake is."""
    return float(lake_params(s)[1])


def wrap_d(ds):
    return (ds + C / 2) % C - C / 2


def lake_params(s):
    """-> (t taper 0..1, centre x, half-width toward -x, half-width toward +x)."""
    s = np.asarray(s, dtype=np.float64)
    d = wrap_d(s - LAKE_S)
    a = np.abs(d)
    t = np.clip((LAKE_HALF_LEN - a) / LAKE_NECK, 0, 1)
    t = t * t * (3 - 2 * t)
    cx = rx(s) * (1 - t)
    # one irregular marshy shore (-x), one cleaner bluff shore (+x) -- §16
    hw_top = CH_HALF + (LAKE_HW - CH_HALF + 22 * np.sin(d / 41.0) + 12 * np.sin(d / 17.0 + 1.3)) * t
    hw_bot = CH_HALF + (LAKE_HW - CH_HALF + 6 * np.sin(d / 63.0 + 0.4)) * t
    return t, cx, hw_top, hw_bot


def water_edges(s):
    """(top edge x, bottom edge x) of the river/lake at s."""
    t, cx, ht, hb = lake_params(s)
    r = cx                      # == rx(s) outside the lake
    top = np.where(t > 0, np.minimum(r - CH_HALF, cx - ht), r - CH_HALF)
    bot = np.where(t > 0, np.maximum(r + CH_HALF, cx + hb), r + CH_HALF)
    return top, bot


def rail_x(s):
    return 960.0 + 60.0 * math.sin(2 * s / R + 1.0)


# ------------------------------------------------------------------ helpers
def densify(pts, step=4.0):
    out = []
    for (a, b) in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n):
            f = k / n
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    out.append(pts[-1])
    return out


def chaikin(pts, it=3, closed=False):
    for _ in range(it):
        new = [] if closed else [pts[0]]
        rng_ = range(len(pts)) if closed else range(len(pts) - 1)
        for i in rng_:
            a, b = pts[i], pts[(i + 1) % len(pts)]
            new.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            new.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            new.append(pts[-1])
        pts = new
    return pts


def meander(pts, amp=14.0, seed=0.0):
    """Perpendicular sine wobble along a densified polyline (creeks)."""
    d = densify(pts, 4.0)
    out, acc = [], 0.0
    for i, p in enumerate(d):
        if i:
            acc += math.dist(d[i - 1], p)
        a = d[max(0, i - 1)]
        b = d[min(len(d) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        fade = min(1.0, acc / 60.0, (len(d) - i) * 4.0 / 60.0)
        o = fade * (amp * math.sin(acc / 47.0 + seed) + 0.45 * amp * math.sin(acc / 19.0 + 2 * seed))
        out.append((p[0] + nx * o, p[1] + ny * o))
    return out


def circle(s, x, r, n=14):
    return [(s + r * math.cos(2 * math.pi * k / n), x + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ellipse(s, x, a, b, n=28, rot=0.0):
    c, sn = math.cos(rot), math.sin(rot)
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        u, v = a * math.cos(t), b * math.sin(t)
        pts.append((s + u * c - v * sn, x + u * sn + v * c))
    return pts


def hull(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def grow(poly, d):
    cs = sum(p[0] for p in poly) / len(poly)
    cx = sum(p[1] for p in poly) / len(poly)
    out = []
    for p in poly:
        vx, vy = p[0] - cs, p[1] - cx
        L = math.hypot(vx, vy) or 1.0
        out.append((p[0] + vx / L * d, p[1] + vy / L * d))
    return out


def L(p):  # (s, x) -> layer pixel
    return (p[0], p[1] + HW)


def draw_poly(dr, poly, **kw):
    for o in OFFS:
        dr.polygon([(p[0] + o, p[1] + HW) for p in poly], **kw)


def draw_line(dr, pts, **kw):
    for o in OFFS:
        dr.line([(p[0] + o, p[1] + HW) for p in pts], **kw)


def draw_ellipse(dr, s, x, r, **kw):
    for o in OFFS:
        dr.ellipse([s + o - r, x + HW - r, s + o + r, x + HW + r], **kw)


def idx(s, x):
    return int(math.floor(s % C)) % CW, min(WH - 1, max(0, int(math.floor(x + HW))))


# ------------------------------------------------------------------ water
S = (np.arange(CW) + 0.5)[None, :]
X = (np.arange(WH) + 0.5 - HW)[:, None]
RX = rx(S)
T_L, CX_L, HT_L, HB_L = lake_params(S)
TOP_E, BOT_E = water_edges(S)

WCAT = np.zeros((WH, CW), np.uint8)             # 1 river 2 lake 3 creek 4 pond 5 ditch
WCAT[np.abs(X - CX_L) < CH_HALF] = 1
WCAT[(T_L > 0) & (X > CX_L - HT_L) & (X < CX_L + HB_L)] = 2

# Named tributary creeks: outer farmland -> (pond) -> river.  2-4 per stretch (§10)
CREEKS = [
    # name, waypoints (s, x) from the wall end toward the river, pond (s, x, long, half-w) or None
    ("Lost Creek", [(120, -1380), (200, -1150), (330, -900), (300, -560), (345, -150)], None),
    ("Mill Creek", [(980, -1300), (1060, -1080), (1120, -820), (1215, -600), (1238, -330)], (1238, -330, 110, 30)),
    ("Willow Run", [(1760, -1420), (1880, -1180), (1800, -900), (1870, -640), (1860, -470)], (1865, -420, 90, 26)),
    ("Tanner Creek", [(2330, -1250), (2440, -1060), (2390, -850), (2370, -700)], (2360, -520, 120, 34)),
    ("Brush Creek", [(2880, -1400), (2800, -1160), (2760, -930), (2680, -720), (2700, -520)], None),
    ("Cole Creek", [(700, 1350), (790, 1180), (860, 960), (830, 640)], None),
    ("Deer Creek", [(1420, 1400), (1330, 1220), (1290, 980), (1330, 760)], (1322, 500, 95, 28)),
    ("Sauk Creek", [(1780, 1260), (1840, 1100), (1880, 900), (1880, 800)], (1885, 640, 130, 36)),
    ("Heron Creek", [(3030, 1300), (3100, 1130), (3060, 880), (3065, 700)], (3055, 480, 80, 24)),
]
# Minor unnamed drainage spurs (§10: 1-2 per stretch, dead-end, pure crossing-density filler):
# (creek index, fraction along the creek where it forks, direction (ds, dx), length)
SPURS = [(0, 0.35, (1, -0.4), 220), (2, 0.3, (-1, -0.3), 260), (4, 0.4, (1, -0.5), 200),
         (5, 0.3, (-1, 0.5), 240), (7, 0.25, (1, 0.6), 200), (8, 0.35, (-1, 0.4), 180),
         (3, 0.5, (1, 0.2), 160)]
OXBOWS = [("Oxbow Lake", 1395.0, 0.0), ("Horseshoe Slough", 2620.0, 0.0), ("Crane Pond", 1985.0, 0.0)]

creek_img = Image.new("L", (CW, WH), 0)            # value = creek id (1-based)
cdr = ImageDraw.Draw(creek_img)
CREEK_PATHS = []
for ci, (name, wps, pond) in enumerate(CREEKS, start=1):
    wps = list(wps)
    if pond:
        wps.append((pond[0], pond[1]))
        s_end = pond[0] + 12
    else:
        s_end = wps[-1][0] + 10
    wps.append((s_end, rcx(s_end)))
    path = meander(chaikin(wps, 3), amp=13.0, seed=ci * 1.7)
    CREEK_PATHS.append((name, path, pond))
    draw_line(cdr, path, fill=ci, width=7)
    if pond:
        draw_poly(cdr, ellipse(pond[0], pond[1], pond[2] / 2, pond[3], rot=0.25), fill=ci)
SPUR_PATHS = []
for (k, frac, (ds, dx), length) in SPURS:
    base = CREEK_PATHS[k][1][int(len(CREEK_PATHS[k][1]) * frac)]
    n = math.hypot(ds, dx)
    end = (base[0] + ds / n * length, base[1] + dx / n * length)
    mid = ((base[0] + end[0]) / 2 + 25 * dx / n, (base[1] + end[1]) / 2 - 25 * ds / n)
    sp = meander(chaikin([base, mid, end], 2), amp=6.0, seed=k)
    SPUR_PATHS.append(sp)
    draw_line(cdr, sp, fill=k + 1, width=4)
CID = np.array(creek_img)
WCAT[(CID > 0) & (WCAT == 0)] = 3
# ponds are category 4 (drawn again so they read as ponds, not creek)
pond_img = Image.new("L", (CW, WH), 0)
pdr = ImageDraw.Draw(pond_img)
for name, path, pond in CREEK_PATHS:
    if pond:
        draw_poly(pdr, ellipse(pond[0], pond[1], pond[2] / 2, pond[3], rot=0.25), fill=1)
OXBOW_POLYS = []
for name, s_c, _ in OXBOWS:
    # cut-off meander loop sitting in the point-bar floodplain
    r_side = -1 if math.sin(6 * s_c / R + PHI1) > 0 else 1   # point bar = inside of the bend
    xc = rxf(s_c) + r_side * 95
    arc = []
    for k in range(13):
        a = math.pi * (0.15 + 0.7 * k / 12)
        arc.append((s_c + 62 * math.cos(a) * 1.4, xc + r_side * 55 * math.sin(a) - r_side * 30))
    inner = [(p[0] * 0.9 + s_c * 0.1, p[1] * 0.9 + xc * 0.1 - r_side * 3) for p in arc]
    poly = arc + list(reversed(inner))
    poly = [(p[0], p[1]) for p in chaikin(poly, 2, closed=True)]
    OXBOW_POLYS.append((name, poly))
    draw_poly(pdr, poly, fill=1)
PND = np.array(pond_img)
WCAT[(PND > 0) & (WCAT == 0)] = 4
WCAT[(PND > 0) & (WCAT == 3)] = 4


def is_water(s, x, buf=False):
    i, j = idx(s, x)
    return WBUF[j, i] if buf else WCAT[j, i] > 0


_wb = Image.fromarray(((WCAT > 0) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
WBUF = np.array(_wb) > 0


# ------------------------------------------------------------------ settlements
FT = 0.3048
B = 91.0          # 300 ft block (§3)


class Town:
    def __init__(self, name, tier, pop, founding, archetype, s0, x0, axis="s", flip=1, label="up"):
        self.name, self.tier, self.pop = name, tier, pop
        self.founding, self.archetype = founding, archetype
        self.s0, self.x0, self.axis, self.flip, self.label = s0, x0, axis, flip, label
        self.streets, self.bldgs, self.areas, self.marks = [], [], [], []
        self.extra_hull = []

    # local (u along main street, v across it) -> ring (s, x)
    def g(self, u, v):
        if self.axis == "s":
            return (self.s0 + u, self.x0 + self.flip * v)
        return (self.s0 + self.flip * v, self.x0 + u)

    def rect(self, u0, u1, v0, v1):
        return [self.g(u0, v0), self.g(u1, v0), self.g(u1, v1), self.g(u0, v1)]

    def rrect(self, uc, vc, w, d, ang):
        c, s = math.cos(ang), math.sin(ang)
        pts = []
        for du, dv in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)):
            pts.append(self.g(uc + du * c - dv * s, vc + du * s + dv * c))
        return pts

    def street(self, pts_uv, cls="street"):
        self.streets.append(([self.g(u, v) for u, v in pts_uv], cls))

    def bld(self, poly, kind, part=False):
        self.bldgs.append((poly, kind, part))

    def area(self, poly, kind):
        self.areas.append((poly, kind))

    def mark(self, u, v, text):
        self.marks.append((self.g(u, v), text))

    # --- building helpers --------------------------------------------------
    def grid(self, us, vs, mains=(), ext_u=None):
        ext_u = ext_u or {}
        for v in vs:
            u0, u1 = ext_u.get(v, (us[0], us[-1]))
            self.street([(u0, v), (u1, v)], "main" if v in mains else "street")
        for u in us:
            self.street([(u, vs[0]), (u, vs[-1])], "street")

    def stores(self, u0, u1, vf, dirn, n, half=7.0, dmin=20, dmax=28, kind="store", vacant=0.0):
        span = (u1 - u0 - 10) / n
        for k in range(n):
            a = u0 + 5 + span * k
            b = a + span - 0.9
            d = rng.uniform(dmin, dmax)
            va = vf + dirn * half
            kd = "vacant" if rng.random() < vacant else kind
            self.bld(self.rect(a, b, va, va + dirn * d), kd)

    def houses(self, u0, u1, vf, dirn, n, half=5.0, setback=7.0, kind="house"):
        span = (u1 - u0 - 12) / n
        for k in range(n):
            uc = u0 + 6 + span * (k + 0.5) + rng.uniform(-2.5, 2.5)
            w, d = rng.uniform(10, 13), rng.uniform(9, 12)
            va = vf + dirn * (half + setback + rng.uniform(0, 3))
            self.bld(self.rect(uc - w / 2, uc + w / 2, va, va + dirn * d), kind)

    def res_block(self, u0, u1, v0, v1, n, alley=False):
        self.houses(u0, u1, v0, 1, n)
        self.houses(u0, u1, v1, -1, n)
        if alley:
            vm = (v0 + v1) / 2
            self.street([(u0, vm), (u1, vm)], "alley")

    def civic(self, u0, u1, v0, v1, kind, w, d, text=None, lawn=None, vface=None):
        if lawn:
            self.area(self.rect(u0 + 4, u1 - 4, v0 + 4, v1 - 4), lawn)
        uc = (u0 + u1) / 2
        if vface is None:
            vc = (v0 + v1) / 2
        else:
            vc = vface
        self.bld(self.rect(uc - w / 2, uc + w / 2, vc - d / 2, vc + d / 2), kind)
        if text:
            self.mark(uc, vc, text)

    def school(self, u0, u1, v0, v1, text):
        self.area(self.rect(u0 + 4, u1 - 4, v0 + 4, v1 - 4), "schoolground")
        um = (u0 + u1) / 2
        self.bld(self.rect(u0 + 8, um - 2, v0 + 10, v0 + 42), "school")
        self.area(self.rect(um + 4, u1 - 8, v0 + 10, v1 - 10), "sportsfield")
        self.mark(u0 + 30, v0 + 26, text)

    def church(self, uc, vc, text=None):
        self.bld(self.rect(uc - 8, uc + 8, vc - 13, vc + 13), "church")
        if text:
            self.mark(uc, vc, text)

    def elevator(self, uc, vc, text="Grain Elev."):
        self.bld(self.rect(uc - 7, uc + 7, vc - 9, vc + 9), "industrial")
        for k in range(3):
            self.bld(circle(*self.g(uc + 13 + k * 11, vc), 5.5, 12), "silo", part=True)
        self.mark(uc, vc, text)

    def tower(self, uc, vc, text="Water Tower"):
        self.bld(circle(*self.g(uc, vc), 8, 14), "tower")
        self.mark(uc, vc, text)

    def subdivision(self, uc, vc, a, b, connect, spacing=40.0):
        """Postwar curvilinear loop (§1/§3) with one cul-de-sac, houses facing the loop."""
        n = 40
        loop = [(uc + a * math.cos(2 * math.pi * k / n), vc + b * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
        self.street(loop, "street")
        near = min(loop, key=lambda p: math.dist(p, connect))
        self.street([connect, near], "street")
        per = sum(math.dist(loop[k], loop[k + 1]) for k in range(n))
        m = int(per / spacing)
        for k in range(m):
            t = 2 * math.pi * (k + 0.5) / m
            du, dv = -a * math.sin(t), b * math.cos(t)
            ang = math.atan2(dv, du)
            nu_, nv_ = math.cos(t) / a, math.sin(t) / b
            nl = math.hypot(nu_, nv_)
            nu_, nv_ = nu_ / nl, nv_ / nl
            for side in (1, -1):
                if side == -1 and min(a, b) < 70:
                    continue
                off = 19 * side
                pu, pv = uc + a * math.cos(t) + nu_ * off, vc + b * math.sin(t) + nv_ * off
                if math.dist((pu, pv), connect) < 20 or math.dist((pu, pv), near) < 16:
                    continue
                self.bld(self.rrect(pu, pv, 12, 10, ang), "house")
        # cul-de-sac stub off the far side
        t = math.pi * 0.25
        p0 = (uc + a * math.cos(t), vc + b * math.sin(t))
        p1 = (p0[0] + 45 * math.cos(t), p0[1] + 45 * math.sin(t))
        self.street([p0, p1], "street")
        self.area(circle(*self.g(*p1), 11, 12), "culdesac")
        for dt in (-1.2, 0.0, 1.2):
            q = (p1[0] + 24 * math.cos(t + dt), p1[1] + 24 * math.sin(t + dt))
            self.bld(self.rrect(q[0], q[1], 12, 10, t + dt), "house")

    def geometry_points(self):
        pts = []
        for p, _ in self.streets:
            pts += p
        for p, _, _ in self.bldgs:
            pts += p
        for p, _ in self.areas:
            pts += p
        return pts + self.extra_hull


def build_harrow_falls():
    # City, water/mill-founded on Lake Tamsin's bluff shore -- §7 downtown directly on the
    # water, elongated along the bank; §8 bluff-and-river-valley: industrial terrace on the
    # water, prestige civic on the bluff top, postwar residential on the upland beyond.
    s0 = 395.0
    _, cx, _, hb = lake_params(s0)
    shore = float(cx + hb)
    t = Town("Harrow Falls", "City", 41800, "Water/mill-founded", "Stable county seat (Tamsin Co.)",
             s0, shore + 42, "s", 1, "down")
    us = [-227.5 + B * i for i in range(6)]
    vs = [0, 91, 182, 273, 364, 455]
    t.grid(us, vs, mains=(0, 91), ext_u={455: (-420, 420)})
    # waterfront strip (between shore and Front St): legacy warehouses + revitalized promenade
    t.area(t.rect(-227.5, 227.5, -40, -6), "promenade")
    for u in (-215, -175):
        t.bld(t.rect(u, u + 30, -34, -9), "industrial")
    t.bld(t.rect(150, 205, -36, -8), "industrial")
    t.mark(177, -22, "Old Mill Lofts")
    t.mark(0, -24, "Riverfront Promenade")
    for i in range(5):
        u0, u1 = us[i], us[i + 1]
        if 1 <= i <= 3:
            t.stores(u0, u1, 0, 1, 4)          # Front St
            t.stores(u0, u1, 91, -1, 4)        # Main St, lake side
            t.stores(u0, u1, 91, 1, 4)         # Main St, bluff side
            t.street([(u0, 45), (u1, 45)], "alley")
        elif i == 0:
            t.civic(u0, u1, 0, 91, "civic", 34, 30, "City Hall", "lawn")
            t.church((u0 + u1) / 2, 140, "St. Brendan's")
            t.houses(u0, u1, 182, -1, 3)
        else:
            t.civic(u0, u1, 0, 91, "civic", 30, 26, "Post Office", "lawn")
            t.civic(u0, u1, 91, 182, "civic", 36, 28, "Carnegie Library", "lawn")
        if 1 <= i <= 3:
            t.houses(u0, u1, 182, -1, 3)
        # bluff rows: pre-war houses with alleys
        if i == 2:
            t.school(u0, u1, 182, 273, "Lincoln Elem.")
        else:
            t.res_block(u0, u1, 182, 273, 3, alley=True)
        if i == 0:
            t.church((u0 + u1) / 2, 318, "First Methodist")
        else:
            t.res_block(u0, u1, 273, 364, 3, alley=True)
    # bluff top: courthouse square (county seat, once per county), hospital, high school
    t.area(t.rect(us[2] + 4, us[3] - 4, 368, 451), "square")
    t.bld(t.rect(-22, 22, 388, 432), "civic")
    t.mark(0, 440, "Tamsin Co. Courthouse")
    t.civic(us[0], us[1], 364, 455, "civic", 45, 62, "Mercy Hospital", "lawn")
    t.school(us[3], us[4] + 91, 364, 455, "HF High")
    t.houses(us[1], us[2], 364, 1, 4)
    t.tower(-330, 420, "Water Tower")
    t.area(t.rect(-420, -300, 180, 330), "cemetery")
    t.mark(-360, 250, "Oakwood Cemetery")
    # postwar upland subdivisions beyond the bluff-top street (= US 30)
    t.subdivision(-120, 560, 115, 58, (-120, 455))
    t.subdivision(150, 555, 95, 52, (150, 455))
    # arterial strip on US 30 east of downtown (§2: small-city tier only)
    t.area(t.rect(265, 380, 470, 570), "parking")
    t.bld(t.rect(275, 370, 510, 575), "bigbox")
    t.mark(322, 545, "Big-box")
    t.area(t.rect(265, 360, 360, 440), "parking")
    t.bld(t.rect(270, 355, 360, 382), "strip")
    t.bld(t.rect(385, 405, 470, 488), "strip")      # gas station
    t.bld(t.rect(385, 400, 425, 440), "strip")      # drive-thru
    t.bld(t.rect(300, 330, 470, 485), "strip")      # drive-thru
    t.mark(330, 380, "Strip mall")
    return t


def build_kessler():
    # City, rail-founded, dead-flat drained plain: rail-corridor spine (§6), no square;
    # water (Sauk Creek + pond) at middle distance as a residential amenity (§7).
    s0 = 2130.0
    x_main = rail_x(s0) - 95
    t = Town("Kessler", "City", 34500, "Rail-founded", "Stable ag / manufacturing",
             s0, x_main, "s", -1, "up")
    us = [-227.5 + B * i for i in range(6)]
    vs = [-70, 0, 91, 182, 273, 364]
    t.grid(us, vs, mains=(0,), ext_u={0: (-430, 330), 91: (-330, 227.5), 273: (-330, 227.5)})
    for i in range(5):
        u0, u1 = us[i], us[i + 1]
        if 1 <= i <= 3:
            t.stores(u0, u1, 0, -1, 4)
            t.stores(u0, u1, 0, 1, 4)
            t.stores(u0, u1, 91, -1, 3, dmin=18, dmax=24)
            t.street([(u0, 45), (u1, 45)], "alley")
        elif i == 0:
            t.civic(u0, u1, -70, 0, "civic", 30, 24, "Fire / Police", vface=-35)
            t.church((u0 + u1) / 2, 45, "St. Adalbert's")
        else:
            t.elevator(u0 + 20, -40)
            t.church((u0 + u1) / 2, 45, "Trinity Lutheran")
    # rail side: depot within one block of Main (§9), elevator already on the side street
    t.bld(t.rect(-18, 18, -78, -90), "civic")
    t.mark(0, -84, "Depot")
    # industry beyond the tracks: the #1 employer (§15)
    t.area(t.rect(-200, 60, -110, -250), "lot")
    t.bld(t.rect(-185, -40, -125, -215), "industrial")
    t.mark(-112, -170, "Kessler Works")
    for u in (80, 125, 170):
        t.bld(t.rect(u, u + 34, -120, -175), "industrial")
    for i in range(5):
        u0, u1 = us[i], us[i + 1]
        if i == 2:
            t.civic(u0, u1, 91, 182, "civic", 40, 30, "City Hall", "lawn")
        elif i == 1:
            t.civic(u0, u1, 91, 182, "civic", 32, 26, "Library", "lawn")
        else:
            t.res_block(u0, u1, 91, 182, 3, alley=True)
        if i == 3:
            t.school(u0, u1, 182, 273, "Kessler High")
        else:
            t.res_block(u0, u1, 182, 273, 3, alley=True)
        if i == 0:
            t.civic(u0, u1, 273, 364, "civic", 44, 60, "St. Luke's Hospital", "lawn")
        else:
            t.res_block(u0, u1, 273, 364, 3, alley=i != 2)
    # Sauk Park: creek + pond on the west edge (streets cross the creek -- §10 rule)
    t.area(t.rect(-320, -240, 20, 360), "park")
    t.mark(-270, 300, "Sauk Park")
    t.tower(260, 150, "Water Tower")
    t.subdivision(-40, 450, 150, 55, (-40, 364))
    # arterial strip along US 30 west approach
    t.area(t.rect(-425, -340, 14, 100), "parking")
    t.bld(t.rect(-422, -345, 55, 118), "bigbox")
    t.mark(-383, 86, "Big-box")
    t.bld(t.rect(-425, -380, -14, -36), "strip")
    t.bld(t.rect(-370, -352, -14, -30), "strip")
    t.area(t.rect(-425, -380, -36, -90), "lot")
    t.mark(-400, -62, "Auto dealer")
    return t


def build_town(name, pop, founding, arche, s0, x0, axis, flip, layout, label, vacant=0.0):
    t = Town(name, "Town", pop, founding, arche, s0, x0, axis, flip, label)
    us = [-182 + B * i for i in range(5)]           # 4 blocks of Main Street
    if layout == "rail":
        vs = [-70, 0, 91, 182, 273]
        t.grid(us, vs, mains=(0,))
        for i in range(4):
            u0, u1 = us[i], us[i + 1]
            if i in (1, 2):
                t.stores(u0, u1, 0, -1, 4, vacant=vacant)
                t.stores(u0, u1, 0, 1, 4, vacant=vacant)
            elif i == 0:
                t.elevator(u0 + 18, -40)
                t.church((u0 + u1) / 2, 45, None)
            else:
                t.civic(u0, u1, -70, 0, "civic", 26, 22, "Post Office", vface=-35)
                t.civic(u0, u1, 0, 91, "civic", 30, 24, "Town Hall", "lawn")
        t.bld(t.rect(-15, 15, -78, -90), "civic")
        t.mark(0, -84, "Depot")
        res_rows = [(91, 182), (182, 273)]
    else:
        vs = [-182, -91, 0, 91, 182]
        t.grid(us, vs, mains=(0,))
        for i in range(4):
            u0, u1 = us[i], us[i + 1]
            if i == 2:
                # the square block sits on the main-street side; storefronts face it
                kind = "courthouse" if layout == "courthouse" else "green"
                t.area(t.rect(u0 + 4, u1 - 4, 4, 87), "square")
                if kind == "courthouse":
                    t.bld(t.rect(u0 + 26, u1 - 26, 24, 66), "civic")
                    t.mark((u0 + u1) / 2, 45, f"{t.name.split()[0]} Co. Courthouse" if False else "Courthouse")
                else:
                    t.bld(circle(*t.g((u0 + u1) / 2, 45), 6, 10), "civic")
                    t.mark((u0 + u1) / 2, 45, "Town Green")
                t.stores(u0, u1, 0, -1, 4)
                t.stores(u0, u1, 91, 1, 4)
            elif i == 1:
                t.stores(u0, u1, 0, -1, 4)
                t.stores(u0, u1, 0, 1, 4)
            elif i == 3:
                t.stores(u0, u1, 0, -1, 3)
                t.civic(u0, u1, 0, 91, "civic", 28, 24, "Library" if layout == "green" else "Opera House", "lawn")
            else:
                t.civic(u0, u1, -91, 0, "civic", 26, 22, "Post Office", "lawn")
                t.church((u0 + u1) / 2, 45, None)
        res_rows = [(-182, -91), (91, 182)]
    for (v0, v1) in res_rows:
        for i in range(4):
            u0, u1 = us[i], us[i + 1]
            if (v0, i) == (res_rows[0][0], 3):
                t.church((u0 + u1) / 2, (v0 + v1) / 2, None)
                t.houses(u0, u1, v1, -1, 2)
            elif (v0, i) == (res_rows[-1][0], 0):
                t.school(u0, u1, v0, v1, "School")
            else:
                t.houses(u0, u1, v0, 1, 3 if abs(v0) < 100 else 2)
                t.houses(u0, u1, v1, -1, 3 if abs(v1) < 100 else 2)
                if layout != "rail":
                    t.street([(u0, (v0 + v1) / 2), (u1, (v0 + v1) / 2)], "alley")
    return t


def build_marlowe():
    t = build_town("Marlowe", 9100, "Inland / trail", "Stable county seat (Brannock Co.)",
                   1500.0, -760.0, "x", 1, "courthouse", "up")
    t.marks = [(p, "Brannock Co. Courthouse" if txt == "Courthouse" else txt) for p, txt in t.marks]
    t.subdivision(-262, 10, 55, 105, (-182, 10))
    t.tower(-230, 60, "Water Tower")
    return t


def build_fenwick():
    t = build_town("Fenwick", 6400, "Inland / trail", "College town",
                   2150.0, -800.0, "s", 1, "green", "up")
    # Fenwick College: the settlement's one unmistakable landmark (§17)
    t.area(t.rect(190, 330, -182, 20), "campus")
    for (u, v) in ((210, -160), (270, -160), (210, -60), (275, -60), (240, -10)):
        t.bld(t.rect(u, u + 38, v, v + 26), "civic")
    t.mark(260, -110, "Fenwick College")
    t.street([(182, -91), (330, -91)], "street")
    return t


def build_bellhaven():
    s0 = 1050.0
    return build_town("Bellhaven", 7200, "Rail-founded", "Stable ag / manufacturing",
                      s0, rail_x(s0) - 95, "s", -1, "rail", "up")


def build_tamarack():
    s0 = 2820.0
    t = build_town("Tamarack", 8300, "Rail-founded", "Declining rust-belt",
                   s0, rail_x(s0) - 95, "s", -1, "rail", "up", vacant=0.4)
    t.area(t.rect(60, 230, -110, -230), "lot")
    t.bld(t.rect(75, 200, -125, -200), "vacant")
    t.mark(137, -165, "Closed foundry")
    return t


def build_village(name, pop, founding, arche, s0, x0, axis, flip, n_stores, label, vs=(-91, 0, 91),
                  blocks=2, school=None, elevator=False, depot=False, vacant=0.0, carnegie=False):
    """Village tier (§1): 1-3 block Main Street or bare crossroads, 2-10 residential streets,
    freestanding church/post office within a block of Main (§9)."""
    t = Town(name, "Village", pop, founding, arche, s0, x0, axis, flip, label)
    us = [-B * blocks / 2 + B * i for i in range(blocks + 1)]
    vs = list(vs)
    t.grid(us, vs, mains=(0,))
    core = (blocks - 1) // 2
    two_sided = vs[0] < 0
    n_up = n_stores - n_stores // 2 if two_sided else n_stores
    t.stores(us[core], us[core + 1], 0, 1, n_up, vacant=vacant)
    if two_sided:
        t.stores(us[core], us[core + 1], 0, -1, n_stores // 2, vacant=vacant)
    used = {(core, 0), (core, -91)}
    other = [i for i in range(blocks) if i != core]
    ch = other[0]
    t.church((us[ch] + us[ch + 1]) / 2, 45, None)
    used.add((ch, 0))
    po = other[-1] if len(other) > 1 else ch
    if po != ch:
        t.civic(us[po], us[po + 1], 0, 91, "civic", 16, 14, "Post Office", vface=22)
        used.add((po, 0))
    elif two_sided:
        t.civic(us[po], us[po + 1], -91, 0, "civic", 16, 14, "Post Office", vface=-22)
        used.add((po, -91))
    else:
        t.civic(us[po], us[po + 1], 91, 182, "civic", 16, 14, "Post Office", vface=113)
        used.add((po, 91))
    if carnegie:
        t.civic(us[0], us[1], vs[0], vs[1], "civic", 22, 18, "Carnegie Library", "lawn")
        used.add((0, vs[0]))
    if school:
        a, b_ = us[-2], us[-1]
        t.school(a, b_, vs[-1], vs[-1] + 91, school)
        t.street([(a, vs[-1] + 91), (b_, vs[-1] + 91)], "street")
        t.street([(a, vs[-1]), (a, vs[-1] + 91)], "street")
        t.street([(b_, vs[-1]), (b_, vs[-1] + 91)], "street")
    for i in range(blocks):
        for (v0, v1) in zip(vs, vs[1:]):
            if (i, v0) in used:
                if v0 == 0 and (i, v0) != (po, 0) or (i, v0) == (ch, 0):
                    t.houses(us[i], us[i + 1], v1, -1, 2)
                elif v1 == 0 and v0 != vs[0] or v1 == 0 and not carnegie:
                    t.houses(us[i], us[i + 1], v0, 1, 2)
                continue
            if v1 - v0 < 80:
                continue
            inner = abs(v0) < 100 and abs(v1) < 100
            t.houses(us[i], us[i + 1], v0, 1, 2 if inner else 1)
            t.houses(us[i], us[i + 1], v1, -1, 2 if inner else 1)
    if elevator:
        t.elevator(us[0] + 18, -118, "Grain Elev. (tallest)")
    if depot:
        t.bld(t.rect(-12, 12, -62, -72), "civic")
        t.mark(0, -67, "Depot (museum)")
    return t


def build_all():
    towns = [build_harrow_falls(), build_kessler(), build_marlowe(), build_bellhaven(),
             build_fenwick(), build_tamarack()]
    # villages -------------------------------------------------------------
    s_cf = 1250.0
    # Cedar Ford: mill village, core within one block of the Kettle (§7 village rule, 1-in-3/4
    # villages are water-founded); "Water St." is the first street back from the bank (§8)
    top_edge = float(water_edges(s_cf)[0])
    cf = build_village("Cedar Ford", 1150, "Water/mill-founded", "Stable ag / manufacturing",
                       s_cf, top_edge - 62, "s", -1, 4, "up", vs=(0, 91, 182),
                       school="Cedar Ford-Pruett Consol.")
    cf.stores(-91, 0, 0, -1, 2)
    cf.bld(cf.rect(20, 52, -12, -42), "industrial")
    cf.mark(36, -27, "Grist Mill")
    cf.mark(-60, 0, "Water St.")
    pr = build_village("Pruett", 820, "Rail-founded", "Stable ag / manufacturing",
                       1500.0, rail_x(1500) - 80, "s", -1, 4, "down", vs=(-55, 0, 91),
                       elevator=True, depot=True)
    du = build_village("Dunmore Crossing", 480, "Inland / crossroads", "Stable ag / manufacturing",
                       650.0, -800.0, "x", 1, 3, "up")
    lo = build_village("Loomis Grove", 390, "Inland / crossroads", "Declining rust-belt",
                       2580.0, -1250.0, "s", 1, 3, "down", vacant=0.5)
    ha = build_village("Haskins Corner", 2600, "Inland / trail", "Growing exurban",
                       2955.0, -640.0, "s", 1, 8, "up", vs=(-182, -91, 0, 91, 182), blocks=3,
                       school="Haskins Elem. + Jr. High", carnegie=True)
    ha.subdivision(0, -290, 105, 48, (0, -182))
    return towns + [cf, pr, du, lo, ha]


TOWNS = build_all()

# ------------------------------------------------------------------ global roads
ROADS = []   # (pts, cls, name)


def road(pts, cls, name="", smooth=2, closed=False):
    if smooth:
        pts = chaikin(pts, smooth, closed)
    if closed:
        pts = pts + [pts[0]]
    ROADS.append((densify(pts, 6.0), cls, name))


T = {t.name: t for t in TOWNS}
# SR 14 -- port-side loop through the port-side settlements' main streets
sr14 = [T["Dunmore Crossing"].g(0, 0), (900, -780), T["Marlowe"].g(0, 0), (1830, -760),
        T["Fenwick"].g(-182, 0), T["Fenwick"].g(182, 0), (2600, -720), T["Haskins Corner"].g(0, 0),
        (3142 + 250, -700)]
road([(p[0], p[1]) for p in sr14] + [(T["Dunmore Crossing"].g(0, 0)[0] + C, -800)], "hwy", "SR 14", smooth=2)
# US 30 -- starboard loop; bypasses Harrow Falls' downtown along the bluff-top street
hf = T["Harrow Falls"]
us30 = [hf.g(-420, 455), hf.g(420, 455), (820, 770), T["Bellhaven"].g(-182, 0), T["Bellhaven"].g(182, 0),
        T["Pruett"].g(-91, 0), T["Pruett"].g(91, 0), T["Kessler"].g(-430, 0), T["Kessler"].g(330, 0),
        (2520, 880), T["Tamarack"].g(-182, 0), T["Tamarack"].g(182, 0), (3142 - 80, 900),
        (hf.g(-420, 455)[0] + C, hf.g(-420, 455)[1])]
road(us30, "hwy", "US 30", smooth=2)
# river crossings -- a handful of big bridges (§10: small crossings must outnumber these)
road([hf.g(-227.5, 91), (80, 380), (-160, 340), (-160, -300), (-200, -620)], "county", "Lakeshore Rd", 2)
road([(650, -700), (930, -380), (930, 380), (900, 740)], "county", "Outlet Rd", 2)
road([T["Cedar Ford"].g(0, 0), (1250, 300), (1150, 700), T["Bellhaven"].g(-182, 91)], "county", "Ford Rd", 2)
road([T["Marlowe"].g(182, 0), (1610, 200), T["Pruett"].g(0, 91)], "county", "Brannock Pike", 2)
road([T["Fenwick"].g(91, 182), (2270, 250), T["Kessler"].g(91, 364)], "county", "College Rd", 2)

# settlement footprints (for clipping section roads / farmland)
# Built-up area = the settlement's own streets/buildings/lots grown by ~25 m (organic edge,
# unlike a convex hull that swallows farmland between an L-shaped layout's arms).
FOOT, TMASK = {}, {}
fp_acc = np.zeros((WH, CW), bool)
for t in TOWNS:
    m = Image.new("L", (CW, WH), 0)
    md = ImageDraw.Draw(m)
    for p, cls in t.streets:
        draw_line(md, p, fill=255, width=12)
    for p, _, _ in t.bldgs:
        draw_poly(md, p, fill=255)
    for p, _ in t.areas:
        draw_poly(md, p, fill=255)
    tm = np.array(m.filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.MinFilter(21))) > 0
    TMASK[t.name] = tm
    fp_acc |= tm
    FOOT[t.name] = t.geometry_points()
FP = fp_acc
fp_buf = np.array(Image.fromarray(FP.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(61))) > 0

# floodplain / bluff terrain (§8/§16) -----------------------------------------
th = S / R
b = np.tanh(1.5 * np.sin(6 * th + PHI1)) / np.tanh(1.5)
b = b * (1 - T_L) + 1.0 * T_L                 # lake: bluff on the +x (Harrow Falls) shore
side = np.where(X < CX_L, -1.0, 1.0)
dist = np.where(X < TOP_E, TOP_E - X, np.where(X > BOT_E, X - BOT_E, 0.0))
w_cut = 0.5 * (1 + b * side)
d0_cut = 60 * (1 - T_L) + 140 * T_L
d0 = 230 - (230 - d0_cut) * w_cut
Lb = 160 - 85 * w_cut
H = H_BLUFF * (1 + 0.3 * np.sin(2 * th + PHI4))
ELEV = (H * np.maximum(0, np.tanh((dist - d0) / Lb)) - Z1 * np.cos(th - math.pi / 4)
        + 1.2 * np.sin(S / 97 + X / 131) + 0.8 * np.sin(X / 53 - S / 211)).astype(np.float32)
WATER = WCAT > 0
FLOOD = (~WATER) & (dist < d0 * 0.85) & (w_cut < 0.5) & (dist > 0)


def in_blocked(s, x, buf=False):
    i, j = idx(s, x)
    if abs(x) > HW - 30:
        return True
    return (fp_buf if buf else FP)[j, i]


# Section-line county roads (Midwest PLSS grid, compressed ~3.5x per the KCD "adjusted
# realistic map" rule, §17).  They stop at the bluff/floodplain unless they're a bridge road.
SECTION_S = [180, 650, 1100, 1560, 2010, 2580, 3000]
SECTION_X = [-1250, 1300]


def clip_runs(pts, bad):
    runs, cur = [], []
    for p in pts:
        if bad(p):
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    return runs


def near_river(p):
    top, bot = water_edges(p[0])
    return float(top) - 150 < p[1] < float(bot) + 150


for s in SECTION_S:
    pts = densify([(s, -HW + 25), (s, HW - 25)], 3.0)
    for run in clip_runs(pts, lambda p: near_river(p) or in_blocked(*p) or is_water(*p) and False):
        if math.dist(run[0], run[-1]) > 60:
            ROADS.append((run, "gravel", ""))
for x in SECTION_X:
    pts = densify([(0, x), (C, x)], 3.0)
    for run in clip_runs(pts, lambda p: in_blocked(*p)):
        if math.dist(run[0], run[-1]) > 60:
            ROADS.append((run, "gravel", ""))

# Rail -- one closed loop on the starboard side (rail-spine towns + Pruett + Kessler sit on it)
RAIL = [(s, rail_x(s)) for s in np.arange(0, C + 5, 5.0)]

# ------------------------------------------------------------------ road mask / building filter
ROAD_W = {"hwy": 12, "county": 8, "gravel": 6, "main": 11, "street": 7, "alley": 3}
rm_img = Image.new("L", (CW, WH), 0)
rmd = ImageDraw.Draw(rm_img)
for pts, cls, _ in ROADS:
    draw_line(rmd, pts, fill=1, width=ROAD_W[cls] + 2)
draw_line(rmd, RAIL, fill=1, width=8)
RMASK = np.array(rm_img) > 0


def bld_ok(poly):
    cs = sum(p[0] for p in poly) / len(poly)
    cx = sum(p[1] for p in poly) / len(poly)
    for p in poly + [(cs, cx)]:
        i, j = idx(*p)
        if WBUF[j, i] or RMASK[j, i] or abs(p[1]) > HW - 20:
            return False
    return True


dropped = 0
for t in TOWNS:
    keep = []
    for (poly, kind, part) in t.bldgs:
        if bld_ok(poly):
            keep.append((poly, kind, part))
        else:
            dropped += 1
    t.bldgs = keep

# ------------------------------------------------------------------ farmland: fields, ditches, farmsteads
FARM = (~FP) & (~WATER) & (~FLOOD)
rng_np = np.random.default_rng(7)
fs = np.floor((S + 37 * np.floor((X + HW) / 160.0)) / 210.0)
fx = np.floor((X + HW) / 160.0)
fid = (fs * 7919 + fx * 104729).astype(np.int64) % 97
FIELD_COLS = np.array([[205, 220, 143], [179, 212, 137], [226, 226, 166], [196, 220, 174],
                       [227, 214, 173], [190, 214, 150]], np.uint8)
FIELDC = FIELD_COLS[(fid % 6).astype(np.int64)]

# ditches: parallel to the ring (along s) at the field-band edges, each draining into the
# nearest named creek (field ditch -> creek -> river, never ditch straight into the river)
dt_img = Image.new("L", (CW, WH), 0)
ddr = ImageDraw.Draw(dt_img)
DITCHES = []
for name, path, pond in CREEK_PATHS:
    xs = [p[1] for p in path]
    lo, hi = min(xs), max(xs)
    for xb in np.arange(-HW + 160, HW, 160.0):
        if not (lo + 30 < xb < hi - 30):
            continue
        near = min(path, key=lambda p: abs(p[1] - xb))
        for dirn in (-1, 1):
            if rng.random() < 0.15:
                continue
            length = rng.uniform(170, 380)
            pts = densify([(near[0] + dirn * 8, xb), (near[0] + dirn * length, xb)], 3.0)
            run = []
            for p in pts:
                i, j = idx(*p)
                if not FARM[j, i] or RMASK[j, i] and len(run) > 40:
                    break
                run.append(p)
            if len(run) > 20:
                DITCHES.append(run)
                draw_line(ddr, run, fill=1, width=3)
DT = np.array(dt_img) > 0
WCAT[DT & (WCAT == 0)] = 5

FARMSTEADS = []
tries = 0
while len(FARMSTEADS) < 34 and tries < 4000:
    tries += 1
    pts, cls, _ = rng.choice([r for r in ROADS if r[1] in ("gravel", "county", "hwy")])
    p = rng.choice(pts)
    horiz = abs(pts[-1][1] - pts[0][1]) < abs(pts[-1][0] - pts[0][0])
    off = rng.choice((-1, 1)) * rng.uniform(30, 45)
    c = (p[0], p[1] + off) if horiz else (p[0] + off, p[1])
    if any(math.dist(c, f) < 260 for f in FARMSTEADS):
        continue
    ok = True
    for ds in (-45, 0, 45):
        for dx in (-45, 0, 45):
            i, j = idx(c[0] + ds, c[1] + dx)
            if not FARM[j, i] or fp_buf[j, i] or WBUF[j, i] or (RMASK[j, i] and (ds or dx) == 0):
                ok = False
    if ok:
        FARMSTEADS.append(c)


def farmstead_polys(c):
    s, x = c
    sg = 1 if rng.random() < 0.5 else -1
    return [
        ([(s - 6, x - 5), (s + 6, x - 5), (s + 6, x + 5), (s - 6, x + 5)], "house"),
        ([(s + 18, x - 9 * sg), (s + 40, x - 9 * sg), (s + 40, x + 18 * sg), (s + 18, x + 18 * sg)], "barn"),
        (circle(s + 48, x + 4 * sg, 4.5, 10), "silo"),
        ([(s - 30, x + 12 * sg), (s - 12, x + 12 * sg), (s - 12, x + 32 * sg), (s - 30, x + 32 * sg)], "shed"),
    ]


# ------------------------------------------------------------------ raster composite
print("compositing terrain...", file=sys.stderr)
img = np.zeros((WH, CW, 3), np.uint8)
img[:] = FIELDC
img[FLOOD] = (212, 230, 195)
# woods: riparian strips along creeks, steep bluff faces, never on settlements/fields' roads
gy, gx = np.gradient(ELEV)
slope = np.hypot(gx, gy)
creek_band = np.array(Image.fromarray(((WCAT == 3) | (WCAT == 4)).astype(np.uint8) * 255)
                      .filter(ImageFilter.MaxFilter(19))) > 0
WOODS = (((slope > 0.11) & (w_cut > 0.5)) | creek_band) & ~WATER & ~FP & ~RMASK
img[WOODS] = (134, 173, 109)
speck = rng_np.random((WH, CW)) < 0.10
img[WOODS & speck] = (96, 140, 78)
img[FP] = (236, 231, 221)
wcols = {1: (93, 159, 216), 2: (79, 147, 210), 3: (90, 154, 214), 4: (91, 155, 213), 5: (104, 160, 214)}
for k, col in wcols.items():
    img[WCAT == k] = col
# hillshade (NW light, 5x vertical exaggeration) + 4 m contours
ex = 5.0
nx, ny = -gx * ex, -gy * ex
nz = np.ones_like(nx)
nl = np.sqrt(nx * nx + ny * ny + nz * nz)
lx, ly, lz = -0.5, -0.5, 0.707
shade = (nx * lx + ny * ly + nz * lz) / nl
shade = np.clip(0.80 + 0.55 * (shade - 0.707), 0.55, 1.12)
shade[WATER] = 1.0
img = np.clip(img * shade[..., None], 0, 255).astype(np.uint8)
band = np.floor(ELEV / 4.0)
cont = np.zeros_like(WATER)
cont[:, 1:] |= band[:, 1:] != band[:, :-1]
cont[1:, :] |= band[1:, :] != band[:-1, :]
cont &= ~WATER & ~FP
img[cont] = (img[cont] * 0.6 + np.array([140, 110, 70]) * 0.4).astype(np.uint8)

layer = Image.fromarray(img, "RGB")
dr = ImageDraw.Draw(layer)

# ------------------------------------------------------------------ vector layers
AREA_COL = {"park": (170, 214, 145), "square": (190, 226, 165), "lawn": (205, 229, 186),
            "promenade": (178, 220, 150), "schoolground": (214, 232, 196), "sportsfield": (150, 200, 118),
            "parking": (200, 200, 200), "lot": (212, 210, 204), "cemetery": (190, 212, 170),
            "campus": (208, 230, 190), "culdesac": (250, 250, 250)}
for t in TOWNS:
    for poly, kind in t.areas:
        draw_poly(dr, poly, fill=AREA_COL[kind], outline=(150, 150, 140) if kind in ("parking", "lot") else None)
        if kind == "cemetery":
            cs = sum(p[0] for p in poly) / 4
            cx = sum(p[1] for p in poly) / 4
            for k in range(24):
                a, b_ = cs + rng.uniform(-45, 45), cx + rng.uniform(-60, 60)
                draw_line(dr, [(a - 2, b_), (a + 2, b_)], fill=(110, 120, 100), width=1)
                draw_line(dr, [(a, b_ - 3), (a, b_ + 3)], fill=(110, 120, 100), width=1)
for c in FARMSTEADS:   # windbreak grove behind each farmstead
    draw_ellipse(dr, c[0] - 8, c[1], 26, fill=(120, 160, 98))

# roads: casing pass, bridge pass, fill pass
CASE = {"hwy": (140, 88, 20), "county": (150, 130, 80), "gravel": (176, 156, 108), "main": (130, 130, 130),
        "street": (160, 160, 160), "alley": (185, 180, 170)}
FILL = {"hwy": (245, 180, 60), "county": (255, 240, 190), "gravel": (234, 220, 180), "main": (255, 255, 255),
        "street": (252, 252, 250), "alley": (222, 218, 210)}
ALL_ROADS = [(pts, cls) for pts, cls, _ in ROADS]
for t in TOWNS:
    ALL_ROADS += [(densify(p, 3.0), c) for p, c in t.streets]
order = ["alley", "gravel", "street", "county", "main", "hwy"]
ALL_ROADS.sort(key=lambda r: order.index(r[1]))

# --- bridge / culvert detection: walk every road and the rail over the water raster
BRIDGES = {"major": [], "small": [], "culvert": [], "rail": []}
CREEK_XING = {name: 0 for name, _, _ in CREEK_PATHS}


def scan(pts, cls, is_rail=False):
    d = densify(pts, 1.0)
    run = []
    for p in d + [None]:
        cat = 0
        if p is not None:
            i, j = idx(*p)
            cat = WCAT[j, i]
        if cat:
            run.append((p, cat, CID[j, i] if cat in (3, 4) else 0))
        elif run:
            cats = {r[1] for r in run}
            a, b_ = run[0][0], run[-1][0]
            if is_rail:
                BRIDGES["rail"].append((a, b_))
            elif cats & {1, 2}:
                BRIDGES["major"].append((a, b_, cls))
            elif cats & {3, 4}:
                BRIDGES["small"].append((a, b_, cls))
            else:
                BRIDGES["culvert"].append((a, b_, cls))
            for cid in {r[2] for r in run if r[2]}:
                CREEK_XING[CREEK_PATHS[cid - 1][0]] += 1
            run = []


for pts, cls in ALL_ROADS:
    if cls != "alley":
        scan(pts, cls)
scan(RAIL, "rail", is_rail=True)

for pts, cls in ALL_ROADS:
    draw_line(dr, pts, fill=CASE[cls], width=ROAD_W[cls] + (2 if cls != "alley" else 0), joint="curve")
for a, b_, cls in BRIDGES["major"]:
    draw_line(dr, [a, b_], fill=(25, 25, 25), width=ROAD_W[cls] + 8)
for a, b_, cls in BRIDGES["small"]:
    draw_line(dr, [a, b_], fill=(60, 60, 60), width=ROAD_W[cls] + 5)
for pts, cls in ALL_ROADS:
    draw_line(dr, pts, fill=FILL[cls], width=ROAD_W[cls], joint="curve")
for a, b_, cls in BRIDGES["culvert"]:
    m = ((a[0] + b_[0]) / 2, (a[1] + b_[1]) / 2)
    draw_ellipse(dr, m[0], m[1], 2.2, fill=(40, 70, 120))
# rail: black line with white dashes
draw_line(dr, RAIL, fill=(40, 40, 40), width=5)
for k in range(0, len(RAIL) - 1, 2):
    draw_line(dr, [RAIL[k], RAIL[k + 1]], fill=(250, 250, 250), width=2)
for a, b_ in BRIDGES["rail"]:
    draw_line(dr, [a, b_], fill=(20, 20, 20), width=11)
    draw_line(dr, [a, b_], fill=(40, 40, 40), width=5)

# buildings
BCOL = {"house": (118, 100, 84), "store": (165, 70, 58), "vacant": (222, 212, 205), "civic": (47, 85, 151),
        "church": (111, 66, 160), "school": (217, 130, 43), "industrial": (88, 88, 88), "silo": (150, 160, 165),
        "tower": (61, 111, 143), "bigbox": (192, 96, 58), "strip": (200, 120, 80), "barn": (168, 50, 42),
        "shed": (138, 138, 122)}
for t in TOWNS:
    for poly, kind, _ in t.bldgs:
        draw_poly(dr, poly, fill=BCOL[kind], outline=(40, 30, 25) if kind != "vacant" else (140, 70, 60))
FS_POLYS = []          # what was drawn, per farmstead (farmstead_polys draws its side at random)
for c in FARMSTEADS:
    FS_POLYS.append(farmstead_polys(c))
    for poly, kind in FS_POLYS[-1]:
        draw_poly(dr, poly, fill=BCOL[kind], outline=(40, 30, 25))

# ------------------------------------------------------------------ labels (on the layer)
FD = "/usr/share/fonts/noto/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_CITY, F_TOWN, F_VIL = font("NotoSerif-Bold.ttf", 62), font("NotoSerif-Bold.ttf", 46), font("NotoSerif-Bold.ttf", 34)
F_SUB = font("NotoSans-Italic.ttf", 22)
F_MARK = font("NotoSans-Regular.ttf", 17)
F_WATER = font("NotoSerif-Italic.ttf", 30)
F_CREEK = font("NotoSans-Italic.ttf", 19)


def text(dr_, xy, s, f, fill, anchor="mm", halo=(255, 255, 255), sw=4):
    for o in OFFS:
        dr_.text((xy[0] + o, xy[1] + HW), s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=halo)


for t in TOWNS:
    for (p, txt) in t.marks:
        text(dr, p, txt, F_MARK, (30, 30, 30), sw=3)

for name, path, pond in CREEK_PATHS:
    p = path[len(path) // 4]
    text(dr, (p[0] + 14, p[1]), name, F_CREEK, (30, 80, 150), anchor="lm", sw=3)
for name, poly in OXBOW_POLYS:
    cs = sum(p[0] for p in poly) / len(poly)
    cx = sum(p[1] for p in poly) / len(poly)
    text(dr, (cs, cx + (40 if cx > rxf(cs) else -40)), name, F_CREEK, (30, 80, 150), sw=3)
text(dr, (LAKE_S, -10), "LAKE TAMSIN", F_WATER, (25, 70, 140), halo=(200, 225, 245))
for s in (1150, 1700, 2450, 2900):
    text(dr, (s, rxf(s) + (48 if s % 2 else -48)), "Kettle River", F_WATER, (25, 70, 140), halo=(225, 238, 250))
text(dr, (1060, 1080), "C&NW Railroad", F_CREEK, (40, 40, 40), sw=3)
text(dr, (2400, -660), "SR 14", F_SUB, (140, 88, 20), sw=3)
text(dr, (2560, 915), "US 30", F_SUB, (140, 88, 20), sw=3)

for t in TOWNS:
    xs = [p[0] for p in FOOT[t.name]]
    ys = [p[1] for p in FOOT[t.name]]
    cs = (min(xs) + max(xs)) / 2
    f = {"City": F_CITY, "Town": F_TOWN, "Village": F_VIL}[t.tier]
    sub = f"{t.tier} · pop. {t.pop:,} · {t.founding}"
    if t.label == "up":
        y = min(ys) - 44
        text(dr, (cs, y), t.name.upper() if t.tier == "City" else t.name, f, (20, 20, 20), sw=6)
        text(dr, (cs, y + f.size * 0.62 + 6), sub, F_SUB, (60, 60, 60), sw=4)
    else:
        y = max(ys) + 34
        text(dr, (cs, y), t.name.upper() if t.tier == "City" else t.name, f, (20, 20, 20), sw=6)
        text(dr, (cs, y + f.size * 0.62 + 6), sub, F_SUB, (60, 60, 60), sw=4)

# ------------------------------------------------------------------ page: title, frame, legend
M_L, M_T, M_B, LEG = 70, 200, 150, 820
page = Image.new("RGB", (M_L + CW + 40 + LEG, M_T + WH + M_B), (246, 243, 236))
page.paste(layer, (M_L, M_T))
pd = ImageDraw.Draw(page)
F_T = font("NotoSerif-Bold.ttf", 64)
F_T2 = font("NotoSans-Regular.ttf", 26)
F_L = font("NotoSans-Regular.ttf", 24)
F_LB = font("NotoSans-Bold.ttf", 26)
F_S = font("NotoSans-Regular.ttf", 21)
pd.text((M_L, 40), "Goblin Engine — Station Ring Overhead Map (layout preview)", font=F_T, fill=(25, 25, 25))
pd.text((M_L, 125), "Ring unrolled: 3,142 m circumference (left/right edges join) × 3,000 m wall to wall · "
        "1 px = 1 m · generated from research/generator_rules.md (tools/map_preview.py)", font=F_T2, fill=(70, 70, 70))
pd.rectangle([M_L - 2, M_T - 2, M_L + CW + 1, M_T + WH + 1], outline=(30, 30, 30), width=3)
# walls + seam annotations
pd.text((M_L + CW / 2, M_T - 22), "PORT WALL  (x = −1,500 m)", font=F_LB, fill=(90, 90, 90), anchor="mm")
pd.text((M_L + CW / 2, M_T + WH + 26), "STARBOARD WALL  (x = +1,500 m)", font=F_LB, fill=(90, 90, 90), anchor="mm")
for k in range(0, 3200, 500):
    xx = M_L + k
    if k <= CW:
        pd.line([xx, M_T + WH, xx, M_T + WH + 10], fill=(30, 30, 30), width=2)
        pd.text((xx, M_T + WH + 58), f"s={k:,} m", font=F_S, fill=(90, 90, 90), anchor="mm")
pd.text((M_L - 10, M_T + WH / 2), "◀ seam", font=F_S, fill=(90, 90, 90), anchor="rm")
# scale bar
sx, sy = M_L + 40, M_T + WH + 95
pd.rectangle([sx, sy, sx + 500, sy + 12], outline=(20, 20, 20), width=2)
pd.rectangle([sx, sy, sx + 250, sy + 12], fill=(20, 20, 20))
pd.text((sx + 520, sy + 6), "500 m", font=F_S, fill=(20, 20, 20), anchor="lm")

# legend ----------------------------------------------------------------------
lx, ly = M_L + CW + 50, M_T
pd.text((lx, ly), "Legend", font=F_T2, fill=(20, 20, 20))
ly += 50


def leg_line(label, fill, case, w):
    global ly
    pd.line([lx, ly + 12, lx + 70, ly + 12], fill=case, width=w + 2)
    pd.line([lx, ly + 12, lx + 70, ly + 12], fill=fill, width=w)
    pd.text((lx + 90, ly + 12), label, font=F_L, fill=(30, 30, 30), anchor="lm")
    ly += 38


def leg_box(label, fill, outline=(40, 30, 25)):
    global ly
    pd.rectangle([lx + 20, ly + 2, lx + 50, ly + 24], fill=fill, outline=outline)
    pd.text((lx + 90, ly + 12), label, font=F_L, fill=(30, 30, 30), anchor="lm")
    ly += 38


leg_line("US / State highway", FILL["hwy"], CASE["hwy"], 12)
leg_line("County road (paved)", FILL["county"], CASE["county"], 8)
leg_line("Section road (gravel)", FILL["gravel"], CASE["gravel"], 6)
leg_line("Main Street", FILL["main"], CASE["main"], 10)
leg_line("Local street / alley", FILL["street"], CASE["street"], 6)
pd.line([lx, ly + 12, lx + 70, ly + 12], fill=(40, 40, 40), width=5)
for k in range(0, 70, 10):
    pd.line([lx + k, ly + 12, lx + k + 5, ly + 12], fill=(250, 250, 250), width=2)
pd.text((lx + 90, ly + 12), "Railroad", font=F_L, fill=(30, 30, 30), anchor="lm")
ly += 38
leg_line("Major bridge (river / lake)", FILL["county"], (25, 25, 25), 14)
leg_line("Small bridge (creek / pond)", FILL["street"], (60, 60, 60), 11)
pd.ellipse([lx + 30, ly + 7, lx + 40, ly + 17], fill=(40, 70, 120))
pd.text((lx + 90, ly + 12), "Culvert (road over farm ditch)", font=F_L, fill=(30, 30, 30), anchor="lm")
ly += 44
leg_box("River / lake / pond", wcols[1], None)
leg_line("Creek (named) / farm ditch", wcols[3], wcols[5], 5)
leg_box("Floodplain (park, not buildable)", (212, 230, 195), None)
leg_box("Woods (bluff faces, creek banks)", (134, 173, 109), None)
leg_box("Cropland (field patchwork)", (205, 220, 143), None)
leg_box("Built-up area", (236, 231, 221), (180, 180, 170))
leg_box("Park / square / promenade", AREA_COL["park"], None)
pd.text((lx + 90, ly + 12), "Contours every 4 m, hillshade 5×", font=F_L, fill=(30, 30, 30), anchor="lm")
pd.line([lx + 10, ly + 12, lx + 60, ly + 12], fill=(160, 130, 90), width=2)
ly += 50
for label, k in (("House", "house"), ("Storefront", "store"), ("Vacant / derelict", "vacant"),
                 ("Civic (hall, courthouse, library...)", "civic"), ("Church", "church"), ("School", "school"),
                 ("Industrial / mill / elevator", "industrial"), ("Highway commercial", "bigbox"),
                 ("Barn (farmstead)", "barn")):
    leg_box(label, BCOL[k], (140, 70, 60) if k == "vacant" else (40, 30, 25))

# stats
ly += 20
pd.text((lx, ly), "Settlements (lore population)   structures", font=F_LB, fill=(20, 20, 20))
ly += 44
total = 0
for t in sorted(TOWNS, key=lambda t: ("City", "Town", "Village").index(t.tier)):
    n = sum(1 for _, _, part in t.bldgs if not part)
    total += n
    pd.text((lx, ly), f"{t.name}", font=F_LB, fill=(20, 20, 20))
    pd.text((lx + LEG - 70, ly), f"{n}", font=F_LB, fill=(20, 20, 20), anchor="ra")
    ly += 30
    pd.text((lx + 16, ly), f"{t.tier}, {t.pop:,} — {t.archetype}", font=F_S, fill=(80, 80, 80))
    ly += 32
nfs = len(FARMSTEADS)
pd.text((lx, ly + 6), f"Farmsteads: {nfs} (x4 bldgs)   Total structures: {total + nfs * 4}", font=F_LB, fill=(20, 20, 20))
ly += 50
pd.text((lx, ly), f"Bridges: {len(BRIDGES['major'])} major · {len(BRIDGES['small'])} small creek "
        f"· {len(BRIDGES['rail'])} rail", font=F_S, fill=(60, 60, 60))
ly += 30
pd.text((lx, ly), f"Culverts: {len(BRIDGES['culvert'])} · Named creeks: {len(CREEK_PATHS)} · "
        f"Ponds/oxbows: {sum(1 for c in CREEK_PATHS if c[2]) + len(OXBOWS)}", font=F_S, fill=(60, 60, 60))

out = sys.argv[1] if len(sys.argv) > 1 else "station_map.png"
page.save(out)

# ------------------------------------------------------------------ validation report
print(f"saved {out}  {page.size}")
print(f"structures: {total} in settlements + {nfs} farmsteads; dropped {dropped} (water/road conflicts)")
for t in TOWNS:
    n = sum(1 for _, _, part in t.bldgs if not part)
    xs = [p[0] for p in FOOT[t.name]]
    ys = [p[1] for p in FOOT[t.name]]
    print(f"  {t.name:17s} {t.tier:8s} {n:4d} bldgs  s {min(xs):7.0f}..{max(xs):7.0f}  x {min(ys):6.0f}..{max(ys):6.0f}")
names = list(FOOT)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        ov = int((TMASK[names[i]] & TMASK[names[j]]).sum())
        if ov:
            print(f"  OVERLAP {names[i]} / {names[j]}: {ov} m^2")
print("bridges:", {k: len(v) for k, v in BRIDGES.items()})
for a, b_, cls in BRIDGES["major"]:
    print(f"  major {cls:7s} s={a[0]:.0f} x={a[1]:.0f} len={math.dist(a, b_):.0f}")
print("creek crossings (roads+rail, need >=2):", CREEK_XING)

# ------------------------------------------------------------------ inventory export
# `--inventory FILE`: every structure on the map as JSON, the master list the building /
# bridge research works from (remake/inventory/).
if "--inventory" in sys.argv:
    import json

    def rect_info(poly):
        cs = sum(p[0] for p in poly) / len(poly)
        cx = sum(p[1] for p in poly) / len(poly)
        if len(poly) == 4:
            w = math.dist(poly[0], poly[1])
            d = math.dist(poly[1], poly[2])
            ang = math.degrees(math.atan2(poly[1][1] - poly[0][1], poly[1][0] - poly[0][0]))
        else:
            r = max(math.dist((cs, cx), p) for p in poly)
            w = d = 2 * r
            ang = 0.0
        return {"s": round(cs, 1), "x": round(cx, 1), "w": round(w, 1), "d": round(d, 1),
                "angle_deg": round(ang, 1), "front_edge": [list(map(lambda v: round(v, 1), poly[0])),
                                                            list(map(lambda v: round(v, 1), poly[1]))]
                if len(poly) == 4 else None}

    inv = {"settlements": [], "structures": [], "farmsteads": [], "crossings": []}
    for t in TOWNS:
        inv["settlements"].append({"name": t.name, "tier": t.tier, "pop": t.pop, "founding": t.founding,
                                   "archetype": t.archetype})
        mains = [(p, txt) for p, txt in t.marks]
        n = 0
        parents = [b for b in t.bldgs if not b[2]]
        for poly, kind, part in t.bldgs:
            info = rect_info(poly)
            if part:
                continue
            n += 1
            label = None
            best = 35.0
            for p, txt in mains:
                dd = math.dist(p, (info["s"], info["x"]))
                if dd < best and txt not in ("Water St.", "Riverfront Promenade", "Sauk Park", "Town Green",
                                             "Oakwood Cemetery", "Strip mall", "Big-box", "Auto dealer"):
                    best, label = dd, txt
            sid = f"{''.join(w[0] for w in t.name.split()).upper()}-{n:03d}"
            parts = [rect_info(pp) for pp, kk, pt in t.bldgs if pt
                     and math.dist((rect_info(pp)["s"], rect_info(pp)["x"]), (info["s"], info["x"])) < 50]
            inv["structures"].append({"id": sid, "settlement": t.name, "kind": kind, "label": label,
                                      **info, "parts": parts})
    for k, c in enumerate(FARMSTEADS, 1):
        parts = []
        for poly, kind in FS_POLYS[k - 1]:
            ss, xs = [q[0] for q in poly], [q[1] for q in poly]
            parts.append({"part": {"house": "house", "barn": "barn", "silo": "silo", "shed": "shed"}[kind],
                          "s": round((min(ss) + max(ss)) / 2, 1), "x": round((min(xs) + max(xs)) / 2, 1),
                          "w": round(max(ss) - min(ss), 1), "d": round(max(xs) - min(xs), 1)})
        inv["farmsteads"].append({"id": f"FARM-{k:02d}", "s": round(c[0], 1), "x": round(c[1], 1),
                                  "structures": ["farmhouse", "barn", "silo", "machine shed"], "parts": parts})
    for kind in ("major", "small", "culvert", "rail"):
        for k, item in enumerate(BRIDGES[kind], 1):
            a, b_ = item[0], item[1]
            cls = item[2] if len(item) > 2 else "rail"
            s_m, x_m = (a[0] + b_[0]) / 2, (a[1] + b_[1]) / 2
            i, j = idx(s_m, x_m)
            cid = CID[j, i]
            over = {1: "Kettle River", 2: "Lake Tamsin"}.get(int(WCAT[j, i]), None)
            if not over and cid:
                over = CREEK_PATHS[cid - 1][0]
            inv["crossings"].append({"id": f"{kind.upper()}-{k:02d}", "type": kind, "road_class": cls,
                                     "s": round(s_m, 1), "x": round(x_m, 1),
                                     "span_m": round(math.dist(a, b_), 1), "over": over or "farm ditch",
                                     "ends": [[round(a[0], 1), round(a[1], 1)], [round(b_[0], 1), round(b_[1], 1)]]})
    if "--terrain" in sys.argv:
        # the terrain model's data for the game (MapTerrain.gd): its closed-form parameters, and the
        # water features this preview draws from polylines -- creeks, spurs, ponds, oxbows, ditches
        ter = {"R": R, "W": W,
               "river": {"A": [A1, A2, A3], "phi": [PHI1, PHI2, PHI3, PHI4], "ch_half": CH_HALF, "bed_half": 12.0, "depth": 2.5},
               "lake": {"s": LAKE_S, "half_len": LAKE_HALF_LEN, "hw": LAKE_HW, "neck": LAKE_NECK, "depth": 4.5, "shelf": 20.0},
               "bluff": {"H": H_BLUFF, "Z1": Z1},
               "creeks": [{"name": n, "hw": 3.5, "depth": 1.1, "pts": [[round(a, 1), round(b_, 1)] for a, b_ in path]}
                          for n, path, pond in CREEK_PATHS]
                         + [{"name": "spur", "hw": 2.0, "depth": 0.7, "pts": [[round(a, 1), round(b_, 1)] for a, b_ in sp]}
                            for sp in SPUR_PATHS],
               "ponds": [{"name": n, "s": pond[0], "x": pond[1], "a": pond[2] / 2, "b": pond[3], "rot": 0.25, "depth": 1.8}
                         for n, path, pond in CREEK_PATHS if pond],
               "oxbows": [{"name": n, "depth": 1.5, "poly": [[round(a, 1), round(b_, 1)] for a, b_ in poly]} for n, poly in OXBOW_POLYS],
               "ditches": [{"s0": round(min(p_[0] for p_ in run), 1), "s1": round(max(p_[0] for p_ in run), 1),
                            "x": round(run[0][1], 1), "hw": 1.5, "depth": 0.6} for run in DITCHES]}
        with open(sys.argv[sys.argv.index("--terrain") + 1], "w") as f:
            json.dump(ter, f, indent=0)
        print(f"terrain: {len(ter['creeks'])} creeks/spurs, {len(ter['ponds'])} ponds, {len(ter['oxbows'])} oxbows, "
              f"{len(ter['ditches'])} ditches")
    out_inv = sys.argv[sys.argv.index("--inventory") + 1]
    with open(out_inv, "w") as f:
        json.dump(inv, f, indent=1)
    print(f"inventory: {len(inv['structures'])} structures, {len(inv['farmsteads'])} farmsteads, "
          f"{len(inv['crossings'])} crossings -> {out_inv}")
