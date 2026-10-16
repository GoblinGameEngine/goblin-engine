"""p_island.py -- the islanders' side of a market: logistics and trading tents (bazaar pagodas, event marquees, the
Lantern Top, striped canopies) with their furniture, festoons and lanterns, and the ropeway: the 28-person gondola
cabin, the cargo cabin, the carriage, the crew's drop cage, rope units, ground anchor blocks, mooring masts (city,
town, village) and the ground station.  Builders are b(q): q=1 full, q=0 MID."""
import math

import numpy as np
import shapely
from shapely.geometry import Polygon

from mk import B, Mesh, V, card, festoon, bulb, lathe, piece, place, prism_zy, ring_torus, rot_y, sweep, rot_x, rot_z  # noqa: F401

SK = ("bulb_a", "bulb_b", "bulb_c", "bulb_d")


# ------------------------------------------------------------------ helpers
def poly_prism(m, pg, y0, y1, slot, shade=1.0, cap=True):
    """a shapely polygon (plan x, z) with holes extruded from y0 to y1: caps, outer sides facing out, hole sides in"""
    for g in getattr(pg, "geoms", [pg]):
        if g.geom_type != "Polygon" or g.area < 1e-6:
            continue
        if cap:
            for t in shapely.constrained_delaunay_triangles(g).geoms:
                c = list(t.exterior.coords)[:3]
                m.tri_facing(*[(p[0], y1, p[1]) for p in c], (0, 1, 0), slot, shade)
                m.tri_facing(*[(p[0], y0, p[1]) for p in c], (0, -1, 0), slot, shade * 0.85)
        for ring, inward in [(g.exterior, False)] + [(r, True) for r in g.interiors]:
            pts = list(ring.coords)[:-1]
            cen = np.array(ring.centroid.coords[0])
            for k in range(len(pts)):
                a, b = np.array(pts[k]), np.array(pts[(k + 1) % len(pts)])
                e = b - a
                n = np.array([e[1], -e[0]])
                mid = (a + b) / 2
                # outward = away from the polygon's inside: test a point a hair along n
                probe = shapely.geometry.Point(*(mid + n / max(np.linalg.norm(n), 1e-9) * 1e-4))
                if g.contains(probe):
                    n = -n
                m.quad_facing((a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1]), (a[0], y1, a[1]), (n[0], 0, n[1]), slot, shade)


def slab_xy(m, outline, z0, z1, slot, shade=1.0, holes=()):
    """a flat panel in the x-y plane (with holes) from z0 to z1 (a wall, a valance, a gable)"""
    if holes:
        m.wall_cut(outline, list(holes), z0, z1, slot)
    else:
        m.prism_xy(outline, [], z0, z1, slot, shade)


def on_side(m, src, yaw, d):
    """a part built facing +z at z 0, turned to face yaw and moved out d along its facing"""
    a = math.radians(yaw)
    place(m, src, d * math.sin(a), 0.0, d * math.cos(a), yaw)


def scallops(w, top, depth, n):
    """a valance outline (x-y): the top edge at `top`, n scallops hanging `depth`"""
    pts = [(-w / 2, top)]
    for k in range(n):
        x0 = -w / 2 + w * k / n
        for j in range(1, 6):
            t = j / 6
            pts.append((x0 + w / n * t, top - depth * 0.35 - depth * 0.65 * math.sin(math.pi * t)))
        pts.append((x0 + w / n, top - depth * 0.35))
    pts.append((w / 2, top))
    return pts


def eave_bulbs(m, half, y, z_out, n, slots=SK, r=0.045):
    """a bulb string along the four eaves of a square tent (hung just outside the valance)"""
    k = 0
    for yaw in (0, 90, 180, 270):
        t = Mesh()
        for i in range(n):
            x = -half + 2 * half * (i + 0.5) / n
            bulb(t, (x, y, z_out), r, slots[k % len(slots)])
            k += 1
        place(m, t, yaw=yaw)


# ------------------------------------------------------------------ the bazaar pagoda (6 x 6)
EAVE, PAGODA_RIDGE = 2.55, 5.6


def pagoda_roof(m, half, eave, ridge, q, cx=0.0, cz=0.0, sides=(0, 90, 180, 270)):
    """the concave pagoda roof: four faces in eight alternating gores, lined underneath; the apex closed by a cap"""
    rows = 6 if q else 3
    H = ridge - eave
    prof = [(half * (1 - (i / rows) * 0.97), eave + H * (i / rows) ** 1.6 * 0.985) for i in range(rows + 1)]
    for yaw in sides:
        f = Mesh()
        for i in range(rows):
            (r0, y0), (r1, y1) = prof[i], prof[i + 1]
            for hlf, slot in ((-1, "canvas_a"), (1, "canvas_b")):
                a0, b0 = (-r0, 0.0) if hlf < 0 else (0.0, r0)
                a1, b1 = (-r1, 0.0) if hlf < 0 else (0.0, r1)
                pa = [(a0, y0, r0), (b0, y0, r0), (b1, y1, r1), (a1, y1, r1)]
                n = (0, r0 - r1, y1 - y0)
                f.quad_facing(*pa, n, slot)
                li = [(x * 0.98, max(y - 0.035, eave + 0.002), z * 0.98) for x, y, z in pa]
                f.quad_facing(*li, (0, -(r0 - r1), -(y1 - y0)), "lining", 0.9)
        place(m, f, cx, 0.0, cz, yaw)
    # the crown cap: an open brass cone resting on the canvas round the apex, a knob on top
    rc = 0.26
    tc = (1 - rc / half) / 0.97
    yc = eave + H * tc ** 1.6 * 0.985 - 0.012
    cap = Mesh()                                                                # (square, aligned to the pyramid's hips)
    cap.cyl(0.0, 0.0, (rc + 0.02) * math.sqrt(2), yc + 0.03, prof[-1][1] + 0.45, "brass", n=4, r1=0.04 * math.sqrt(2), caps=False)
    place(m, cap, cx, 0.0, cz, 45.0)
    lathe(m, [(0.0, 0.0), (0.07, 0.04), (0.0, 0.12)], "brass", n=6, cx=cx, cz=cz, y0=prof[-1][1] + 0.45)
    return prof


def bazaar_frame(m, half, q, cx=0.0, cz=0.0, posts_at=None):
    p = half - 0.06
    pts = posts_at or [(sx * p, sz * p) for sx in (-1, 1) for sz in (-1, 1)]
    for x, z in pts:
        m.box((cx + x - 0.035, 0.0, cz + z - 0.035), (cx + x + 0.035, EAVE - 0.08, cz + z + 0.035), "steel")
    for yaw in (0, 90, 180, 270):                                                 # eave beams between the posts
        t = Mesh()
        t.box((-p + 0.035, EAVE - 0.08, p - 0.03), (p - 0.035, EAVE - 0.01, p + 0.03), "steel")
        place(m, t, cx, 0.0, cz, yaw)
    return pts


def valance(m, half, q, cx=0.0, cz=0.0, sides=(0, 90, 180, 270), slot="canvas_c"):
    for yaw in sides:
        t = Mesh()
        t.prism_xy(scallops(2 * half - 0.04, EAVE + 0.02, 0.32, 6 if q else 3), [], half + 0.012, half + 0.032, slot)
        place(m, t, cx, 0.0, cz, yaw)


def bazaar_walls(m, half, q, back=True, sides=True, cx=0.0, cz=0.0):
    """the back wall (two-faced cloth, kanat-lined), low side walls with the side cloth rolled up under the eave"""
    w = 2 * half - 0.04
    if back:
        t = Mesh()
        t.box((-w / 2, 0.04, -0.012), (w / 2, EAVE - 0.03, 0.012), "canvas_a")
        if q:
            for k in range(5):                                                    # kanat arches on the lining side
                x = -w / 2 + w * (k + 0.5) / 5
                t.prism_xy([(x - 0.42, 0.4), (x + 0.42, 0.4), (x + 0.42, 1.6), (x, 2.05), (x - 0.42, 1.6)], [], 0.012, 0.022, "lining")
        place(m, t, cx, 0.0, cz - half + 0.005, 0)
    if sides:
        for yaw in (90, 270):
            t = Mesh()
            t.box((-w / 2 + 0.05, 0.04, -0.012), (w / 2 - 0.05, 1.05, 0.012), "canvas_c")
            roll = Mesh()                                                         # the side cloth, rolled up
            roll.cyl(0.0, 0.0, 0.08, -w / 2 + 0.08, w / 2 - 0.08, "canvas_a", n=6 if q else 4)
            t.add(roll, lambda p: (p[1], 2.1 - p[0], p[2]))
            on_side(m, t, yaw, half - 0.005)


def hanging_lantern(m, x, y_hook, z, q, slot="glow"):
    """a paper lantern on a cord from y_hook (its globe's top 0.5 m under)"""
    m.box((x - 0.006, y_hook - 0.5, z - 0.006), (x + 0.006, y_hook, z + 0.006), "dark")
    lathe(m, [(0.0, 0.0), (0.13, 0.04), (0.2, 0.18), (0.13, 0.32), (0.0, 0.36)], slot, n=8 if q else 5, cx=x, cz=z, y0=y_hook - 0.86)
    m.cyl(x, z, 0.06, y_hook - 0.52, y_hook - 0.5, "brass", n=5)


def finial(m, x, y, z, q, pennant=True):
    m.cyl(x, z, 0.025, y, y + 0.7, "brass", n=5)
    lathe(m, [(0.0, 0.0), (0.09, 0.05), (0.1, 0.12), (0.0, 0.22)], "brass", n=8 if q else 5, cx=x, cz=z, y0=y + 0.7)
    if pennant:
        m.prism_xy([(x + 0.03, y + 0.62), (x + 0.03, y + 0.3), (x + 0.75, y + 0.48)], [], z - 0.005, z + 0.005, "canvas_c")


def bazaar_6(q):
    m = Mesh()
    h = 3.0
    bazaar_frame(m, h, q)
    bazaar_walls(m, h, q)
    valance(m, h, q)
    pagoda_roof(m, h, EAVE, PAGODA_RIDGE, q)
    finial(m, 0.0, PAGODA_RIDGE + 0.42, 0.0, q)
    hanging_lantern(m, 0.0, PAGODA_RIDGE - 0.8, 0.0, q)
    eave_bulbs(m, h - 0.2, EAVE - 0.06, h + 0.09, 10 if q else 4)
    for sx in (-1, 1):                                                                # water-barrel ballast in the corners
        for sz in (-1, 1):
            m.cyl(sx * (h - 0.35), sz * (h - 0.35), 0.22, 0.0, 0.62, "accent2", n=8 if q else 5)
    return m


BAZ_DRESS = [["tent_shelf", -1.4, 0.0, -2.55, 0], ["tent_shelf", 1.4, 0.0, -2.55, 0], ["tent_counter", -1.2, 0.0, 1.85, 0],
             ["tent_table", 1.95, 0.0, 0.2, -90], ["fm_goods_sky_knit", 1.95, 0.76, -0.35, -90], ["fm_goods_sky_lights", 1.95, 0.76, 0.6, -90],
             ["fm_goods_sky_food", -1.2, 1.0, 1.85, 0]]
BAZ_ANCHORS = {"vendor_0": [-1.2, 0.0, 1.2, 0], "vendor_1": [2.5, 0.0, 0.2, -90], "shelf_0": [-1.4, 0.0, -2.55, 0], "shelf_1": [1.4, 0.0, -2.55, 0],
               "counter": [-1.2, 0.0, 1.85, 0], "table_0": [1.95, 0.0, 0.2, -90], "sign": [0.0, 2.15, 3.06, 0]}
piece("tent_bazaar_6", "tent", bazaar_6, kind="tent", foot=[6.0, 6.0], lod1="keep",
      frame=[B(sx * 2.94 - 0.035, 0, sz * 2.94 - 0.035, sx * 2.94 + 0.035, 2.47, sz * 2.94 + 0.035) for sx in (-1, 1) for sz in (-1, 1)]
      + [B(-2.98, 0, -3.007, 2.98, 2.52, -2.983)] + [B(s * 3.007 if s < 0 else 2.983, 0, -2.88, s * 2.983 if s < 0 else 3.007, 1.05, 2.88) for s in (-1, 1)]
      + [B(sx * 2.65 - 0.22, 0, sz * 2.65 - 0.22, sx * 2.65 + 0.22, 0.62, sz * 2.65 + 0.22) for sx in (-1, 1) for sz in (-1, 1)],
      passes=[{"box": B(-2.3, 0, 2.6, 2.3, 2.22, 3.2), "kind": "open"}], walk=[[-0.5, -2.1, 1.3, 2.8, 0.0]],
      anchors=BAZ_ANCHORS, budget=1800, palette="skein", extra={"dress": BAZ_DRESS, "vendors": 2},
      notes="the islanders' bazaar pagoda (6 x 6 m, eave 2.55, peak 5.6): clan-coloured gores lined inside, a scalloped "
            "valance (clearance 2.25 m), a kanat-lined back wall, low side walls with the cloth rolled up, a paper "
            "lantern, eave bulbs, water-barrel ballast.  `dress`: its furniture and goods (shelves, counter, table: "
            "2 vendors at vendor_0/1).  Open front +z.")


def bazaar_double(q):
    """two pagodas joined along x (6 x 12): one back wall, a shared middle (no posts in the way: a 12 m clear front)"""
    m = Mesh()
    h = 3.0
    pts = [(sx * 5.94, sz * 2.94) for sx in (-1, 1) for sz in (-1, 1)] + [(0.0, -2.94), (0.0, 2.94)]
    for x, z in pts:
        m.box((x - 0.035, 0.0, z - 0.035), (x + 0.035, EAVE - 0.08, z + 0.035), "steel")
    for z in (-2.94, 2.94):
        for xa, xb in ((-5.94, 0.0), (0.0, 5.94)):
            m.box((xa + 0.035, EAVE - 0.08, z - 0.03), (xb - 0.035, EAVE - 0.01, z + 0.03), "steel")
    for x in (-5.94, 0.0, 5.94):
        m.box((x - 0.03, EAVE - 0.08, -2.94 + 0.035), (x + 0.03, EAVE - 0.01, 2.94 - 0.035), "steel")
    for cx in (-3.0, 3.0):
        pagoda_roof(m, h, EAVE, PAGODA_RIDGE, q, cx=cx)
        finial(m, cx, PAGODA_RIDGE + 0.42, 0.0, q, pennant=True)
        hanging_lantern(m, cx, PAGODA_RIDGE - 0.8, 0.0, q)
    for cx, yaws in ((-3.0, (0, 180, 270)), (3.0, (0, 90, 180))):
        valance(m, h, q, cx=cx, sides=yaws)
    t = Mesh()
    t.box((-5.98, 0.04, -0.012), (5.98, EAVE - 0.03, 0.012), "canvas_a")
    if q:
        for k in range(10):
            x = -5.98 + 11.96 * (k + 0.5) / 10
            t.prism_xy([(x - 0.42, 0.4), (x + 0.42, 0.4), (x + 0.42, 1.6), (x, 2.05), (x - 0.42, 1.6)], [], 0.012, 0.022, "lining")
    place(m, t, 0.0, 0.0, -h + 0.005)
    for yaw, cx in ((90, 3.0), (270, -3.0)):
        t = Mesh()
        t.box((-2.88, 0.04, -0.012), (2.88, 1.05, 0.012), "canvas_c")
        a = math.radians(yaw)
        place(m, t, cx + (h - 0.005) * math.sin(a), 0.0, (h - 0.005) * math.cos(a), yaw)
    k = 0
    for i in range(20 if q else 8):                                                   # front and back eave bulbs
        x = -5.8 + 11.6 * (i + 0.5) / (20 if q else 8)
        for z in (h + 0.09, -h - 0.09):
            bulb(m, (x, EAVE - 0.06, z), 0.045, SK[k % 4])
            k += 1
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(sx * 5.65, sz * 2.65, 0.22, 0.0, 0.62, "accent2", n=8 if q else 5)
    return m


piece("tent_bazaar_6x12", "tent", bazaar_double, kind="tent", foot=[12.0, 6.0], lod1="keep",
      frame=[B(x - 0.035, 0, z - 0.035, x + 0.035, 2.47, z + 0.035) for x in (-5.94, 0.0, 5.94) for z in (-2.94, 2.94)]
      + [B(-5.98, 0, -3.007, 5.98, 2.52, -2.983), B(-6.007, 0, -2.88, -5.983, 1.05, 2.88), B(5.983, 0, -2.88, 6.007, 1.05, 2.88)]
      + [B(sx * 5.65 - 0.22, 0, sz * 2.65 - 0.22, sx * 5.65 + 0.22, 0.62, sz * 2.65 + 0.22) for sx in (-1, 1) for sz in (-1, 1)],
      passes=[{"box": B(-5.3, 0, 2.6, -0.1, 2.22, 3.2), "kind": "open"}, {"box": B(0.1, 0, 2.6, 5.3, 2.22, 3.2), "kind": "open"}],
      walk=[[-4.0, -2.1, 4.0, 2.8, 0.0]], budget=3000, palette="skein", extra={"vendors": 3,
      "dress": [["tent_shelf", x, 0.0, -2.55, 0] for x in (-4.4, -1.6, 1.6, 4.4)] + [["tent_counter", -3.6, 0.0, 1.85, 0],
               ["tent_counter", 3.6, 0.0, 1.85, 0], ["tent_table", 0.0, 0.0, 0.0, 0], ["tent_rail", -5.4, 0.0, -0.5, 90]]},
      anchors={"vendor_0": [-3.6, 0.0, 1.2, 0], "vendor_1": [3.6, 0.0, 1.2, 0], "vendor_2": [0.0, 0.0, -0.8, 0], "sign": [0.0, 2.15, 3.06, 0]},
      notes="two bazaar pagodas joined (6 x 12 m), one long kanat back wall, a 12 m open front with a post at the middle")


# ------------------------------------------------------------------ tent furniture
def tent_shelf(q):
    """a tall painted island shelf (1.3 x 0.45 x 2.0) with a carved crest and an LED edge under each shelf"""
    m = Mesh()
    w, d, h, t = 1.3, 0.45, 2.0, 0.035
    for s in (-1, 1):
        x0, x1 = (w / 2 - t, w / 2) if s > 0 else (-w / 2, -w / 2 + t)
        m.box((x0, 0.0, -d / 2), (x1, h, d / 2), "accent")
    ys = [0.1, 0.55, 1.0, 1.45, 1.9] if q else [0.1, 1.0, 1.9]
    for y in ys:
        m.box((-w / 2 + t + 0.002, y, -d / 2 + 0.015), (w / 2 - t - 0.002, y + 0.03, d / 2), "wood")
        if q and y > 0.2:
            m.box((-w / 2 + t + 0.02, y - 0.015, d / 2 - 0.04), (w / 2 - t - 0.02, y, d / 2 - 0.025), "glow")
    m.box((-w / 2 + t + 0.001, 0.0, -d / 2), (w / 2 - t - 0.001, h, -d / 2 + 0.015), "accent2", 0.85)
    m.prism_xy([(-w / 2, h), (w / 2, h), (w / 2, h + 0.12), (0.25, h + 0.12), (0.0, h + 0.3), (-0.25, h + 0.12), (-w / 2, h + 0.12)], [],
               -d / 2, -d / 2 + 0.05, "accent")
    return m


def tent_table(q):
    m = Mesh()
    L, D, H = 1.6, 0.75, 0.76
    m.box((-L / 2, H - 0.05, -D / 2), (L / 2, H, D / 2), "wood")
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx * (L / 2 - 0.1) - 0.03, 0.0, sz * (D / 2 - 0.08) - 0.03), (sx * (L / 2 - 0.1) + 0.03, H - 0.05, sz * (D / 2 - 0.08) + 0.03), "wood")
    prism_zy(m, [(-D / 2 - 0.01, H), (D / 2 + 0.002, H), (D / 2 + 0.002, 0.25), (D / 2 + 0.012, 0.25), (D / 2 + 0.012, H + 0.008),
                 (-D / 2 - 0.01, H + 0.008)], -L / 2 - 0.01, L / 2 + 0.01, "canvas_c")
    if q:                                                                          # a tasselled hem
        for k in range(8):
            x = -L / 2 + L * (k + 0.5) / 8
            m.prism_xy([(x - 0.05, 0.25), (x + 0.05, 0.25), (x, 0.17)], [], D / 2 + 0.002, D / 2 + 0.012, "canvas_b")
    return m


def tent_counter(q):
    """the lit counter: a box with a glowing front panel under a wood top"""
    m = Mesh()
    L, D, H = 1.8, 0.6, 1.0
    m.box((-L / 2, 0.0, -D / 2), (L / 2, H - 0.05, D / 2), "accent")
    m.box((-L / 2 - 0.04, H - 0.05, -D / 2 - 0.04), (L / 2 + 0.04, H, D / 2 + 0.04), "wood")
    m.box((-L / 2 + 0.1, 0.25, D / 2), (L / 2 - 0.1, H - 0.2, D / 2 + 0.02), "glow")
    if q:
        m.box((-L / 2 + 0.06, 0.08, D / 2), (L / 2 - 0.06, 0.16, D / 2 + 0.03), "canvas_b")
        m.box((-L / 2 + 0.06, H - 0.16, D / 2), (L / 2 - 0.06, H - 0.12, D / 2 + 0.03), "canvas_b")
    return m


def tent_rail(q):
    """a hanging rail on two posts (2.3 m) against a wall: rugs and two lanterns hung from it"""
    m = Mesh()
    for x in (-0.8, 0.8):
        m.box((x - 0.03, 0.0, -0.03), (x + 0.03, 2.3, 0.03), "wood")
    m.box((-0.77, 2.24, -0.02), (0.77, 2.28, 0.02), "wood")
    for k, (x, sl) in enumerate(((-0.4, "canvas_a"), (0.1, "canvas_b"))):
        m.box((x - 0.24, 0.95, -0.006), (x + 0.24, 2.235, 0.006), sl)
    if q:
        hanging_lantern(m, 0.555, 2.24, 0.0, q, "glow_b")
    return m


def tent_ballast(q):
    m = Mesh()
    m.cyl(0.0, 0.0, 0.25, 0.0, 0.7, "accent2", n=8 if q else 5)
    m.cyl(0.0, 0.0, 0.08, 0.7, 0.76, "dark", n=6)
    m.box((0.32, 0.0, -0.18), (0.72, 0.16, 0.18), "fabric")                      # a sandbag beside it
    return m


piece("tent_shelf", "tent_furniture", tent_shelf, kind="decor", foot=[1.3, 0.45], lod1="drop", frame=[B(-0.65, 0, -0.225, 0.65, 2.0, 0.225)],
      anchors={f"g{k}": [0.0, y + 0.03, 0.02, 0] for k, y in enumerate([0.1, 0.55, 1.0, 1.45])}, budget=250, palette="skein",
      notes="an island shelf: painted sides, lit shelf edges (glow), a carved crest; goods at g0..g3")
piece("tent_table", "tent_furniture", tent_table, kind="decor", foot=[1.6, 0.75], lod1="drop", frame=[B(-0.81, 0, -0.385, 0.81, 0.77, 0.385)],
      anchors={"g0": [-0.45, 0.768, 0.0, 0], "g1": [0.45, 0.768, 0.0, 0]}, budget=140, palette="skein", notes="a cloth-hung trading table")
piece("tent_counter", "tent_furniture", tent_counter, kind="decor", foot=[1.88, 0.68], lod1="drop", frame=[B(-0.94, 0, -0.34, 0.94, 1.0, 0.34)],
      anchors={"g0": [-0.5, 1.0, 0.0, 0], "g1": [0.4, 1.0, 0.0, 0]}, budget=200, palette="skein", notes="the lit counter: a glowing front panel")
piece("tent_rail", "tent_furniture", tent_rail, kind="decor", foot=[1.66, 0.1], lod1="drop", frame=[B(-0.83, 0, -0.03, 0.83, 2.3, 0.03)],
      budget=160, palette="skein", notes="a hanging rail of rugs and a lantern, against a wall")
piece("tent_ballast", "tent_furniture", tent_ballast, kind="decor", foot=[1.0, 0.5], lod1="drop", frame=[B(-0.25, 0, -0.25, 0.25, 0.76, 0.25)],
      budget=80, palette="skein", notes="a water barrel and a sandbag: paved-lot tent ballast")


# ------------------------------------------------------------------ the event marquee (9 x 9, 9 x 18)
EV_EAVE, EV_RIDGE, EV_HALF = 2.75, 4.75, 4.5


def event_tent(L, logistics=False, sign=None):
    nb = int(round(L / 3.0))

    def b(q):
        m = Mesh()
        hz = L / 2
        p = EV_HALF - 0.06
        zs = [-hz + 0.06 + (L - 0.12) * k / nb for k in range(nb + 1)]
        slope = (EV_RIDGE - EV_EAVE) / EV_HALF

        def roof_y(x):
            return EV_RIDGE - abs(x) * slope
        for z in zs:                                                               # the bents: posts, rafters, a tie
            for s in (-1, 1):
                m.box((s * p - 0.04, 0.0, z - 0.04), (s * p + 0.04, EV_EAVE - 0.1, z + 0.04), "steel")
                xa, xb = sorted((s * p, s * 0.05))
                m.prism_xy([(xa, roof_y(xa) - 0.12), (xb, roof_y(xb) - 0.12), (xb, roof_y(xb) - 0.03), (xa, roof_y(xa) - 0.03)], [],
                           z - 0.035, z + 0.035, "steel")
            if q:
                m.box((-0.05, EV_RIDGE - 0.24, z - 0.04), (0.05, EV_RIDGE - 0.035, z + 0.04), "steel")
                m.box((-p + 0.04, EV_EAVE - 0.18, z - 0.02), (p - 0.04, EV_EAVE - 0.14, z + 0.02), "steel")
        for s in (-1, 1):                                                          # eave rails
            m.box((s * p - 0.03, EV_EAVE - 0.1, -hz + 0.1), (s * p + 0.03, EV_EAVE - 0.04, hz - 0.1), "steel")
        # the roof: stripes ridge-to-eave every 1.5 m (candy stripes; plain for logistics), 15 cm over the eave, lined
        ns = int(round(L / 1.5)) if q else int(round(L / 3.0))
        xe = EV_HALF + 0.15
        for s in (-1, 1):
            for k in range(ns):
                z0, z1 = -hz - 0.05 + (L + 0.1) * k / ns, -hz - 0.05 + (L + 0.1) * (k + 1) / ns
                sl = ("canvas_a" if k % 2 == 0 else "canvas_b") if not logistics else "canvas_a"
                m.quad_facing((s * xe, roof_y(xe), z0), (0.0, EV_RIDGE, z0), (0.0, EV_RIDGE, z1), (s * xe, roof_y(xe), z1), (s * slope, 1.0, 0.0), sl)
                za, zb = max(z0, -hz + 0.05), min(z1, hz - 0.05)
                xl = EV_HALF - 0.1
                m.quad_facing((s * xl, roof_y(xl) - 0.015, za), (0.0, EV_RIDGE - 0.015, za), (0.0, EV_RIDGE - 0.015, zb), (s * xl, roof_y(xl) - 0.015, zb),
                              (-s * slope, -1.0, 0.0), "lining", 0.9)
        # gable ends: the back closed; the front a triangle with a scalloped hem (open below), or (logistics) a door wall
        yb = EV_EAVE - 0.02
        for zf, front in ((-hz, False), (hz, True)):
            t = Mesh()
            t.prism_xy([(-EV_HALF + 0.03, yb), (EV_HALF - 0.03, yb), (0.0, EV_RIDGE - 0.03)], [], -0.012, 0.012, "canvas_c" if not logistics else "canvas_b")
            body = [(-EV_HALF + 0.05, 0.04), (EV_HALF - 0.05, 0.04), (EV_HALF - 0.05, yb), (-EV_HALF + 0.05, yb)]
            if front and not logistics:
                t.prism_xy(scallops(2 * EV_HALF - 0.1, yb, 0.38, 9 if q else 4), [], -0.012, 0.012, "canvas_b")
            elif front:
                t.wall_cut(body, [[(-1.2, 0.0), (1.2, 0.0), (1.2, 2.4), (-1.2, 2.4)]], -0.012, 0.012, "canvas_a")
            else:
                t.prism_xy(body, [], -0.012, 0.012, "canvas_a")
            place(m, t, 0.0, 0.0, zf)
        if logistics:                                                             # closed side walls with windows
            for s in (-1, 1):
                t = Mesh()
                wins = [[(z - 0.6, 1.0), (z + 0.6, 1.0), (z + 0.6, 1.9), (z - 0.6, 1.9)] for z in np.arange(-hz + 1.5, hz - 1.0, 3.0)]
                t.wall_cut([(-hz + 0.05, 0.04), (hz - 0.05, 0.04), (hz - 0.05, yb), (-hz + 0.05, yb)], wins, -0.012, 0.012, "canvas_a")
                for w_ in wins:
                    t.pane(w_[0][0], w_[0][1], w_[1][0], w_[2][1], 0.0)
                place(m, t, s * (EV_HALF + 0.005), 0.0, 0.0, 90 * s)
            for z in zs:                                                           # ballast blocks at the posts
                for s in (-1, 1):
                    x0 = EV_HALF + 0.05
                    m.box((-x0 - 0.25, 0.0, z - 0.25) if s < 0 else (x0, 0.0, z - 0.25), (-x0, 0.4, z + 0.25) if s < 0 else (x0 + 0.25, 0.4, z + 0.25),
                          "concrete")
        else:
            for s in (-1, 1):                                                      # bunting along both eaves
                nbt = int(L / 0.5) if q else int(L / 1.5)
                for k in range(nbt):
                    z = -hz + L * (k + 0.5) / nbt
                    tb = Mesh()
                    tb.prism_xy([(-0.15, EV_EAVE - 0.17), (0.15, EV_EAVE - 0.17), (0.0, EV_EAVE - 0.4)], [], -0.004, 0.004, ("canvas_a", "canvas_b", "canvas_c")[k % 3])
                    place(m, tb, s * (EV_HALF + 0.1), 0.0, z, 90)
                sweep(m, [(s * (EV_HALF + 0.1), EV_EAVE - 0.165, -hz), (s * (EV_HALF + 0.1), EV_EAVE - 0.165, hz)], 0.006, "dark", n=3)
            for x in ((-1.6, 0.0, 1.6) if q else (0.0,)):                         # festoons under the ridge
                y_end = roof_y(x) - 0.35
                festoon(m, (x, y_end, -hz + 0.25), (x, y_end, hz - 0.25), 0.25, 0.6 if q else 1.2, slots=SK, q=q)
        if sign:                                                                   # the logistics sign over the door
            card(m, "text", sign, (0.0, 3.0, hz + 0.05), (1, 0, 0), (0, 1, 0), 0.9, two=False)
            m.box((-0.95, 2.47, hz + 0.012), (0.95, 2.51, hz + 0.08), "steel")
        return m
    return b


def ev_frame(L, logistics=False):
    hz, p = L / 2, EV_HALF - 0.06
    nb = int(round(L / 3.0))
    zs = [-hz + 0.06 + (L - 0.12) * k / nb for k in range(nb + 1)]
    out = [B(s * p - 0.04, 0, z - 0.04, s * p + 0.04, EV_EAVE - 0.1, z + 0.04) for z in zs for s in (-1, 1)]
    out.append(B(-EV_HALF + 0.05, 0, -hz - 0.012, EV_HALF - 0.05, EV_EAVE - 0.02, -hz + 0.012))
    if logistics:
        out += [B(-EV_HALF + 0.05, 0, hz - 0.012, -1.2, EV_EAVE - 0.02, hz + 0.012), B(1.2, 0, hz - 0.012, EV_HALF - 0.05, EV_EAVE - 0.02, hz + 0.012)]
        out += [B(s * (EV_HALF + 0.005) - 0.012, 0, -hz + 0.05, s * (EV_HALF + 0.005) + 0.012, EV_EAVE - 0.02, hz - 0.05) for s in (-1, 1)]
    return out


for L in (9, 18):
    pid = "tent_event_9" if L == 9 else "tent_event_9x18"
    piece(pid, "tent", event_tent(float(L)), kind="tent", foot=[9.3, float(L) + 0.1], lod1="keep", frame=ev_frame(float(L)),
          passes=[{"box": B(-4.3, 0, L / 2 - 0.3, 4.3, 2.3, L / 2 + 0.3), "kind": "open"}]
          + [{"box": B(s * 4.5 - 0.3, 0, -L / 2 + 0.2, s * 4.5 + 0.3, 2.3, -L / 2 + 2.8) if s < 0 else B(4.2, 0, -L / 2 + 0.2, 4.8, 2.3, -L / 2 + 2.8),
              "kind": "open"} for s in (-1, 1)],
          walk=[[-4.3, -L / 2 + 0.2, 4.3, L / 2 - 0.2, 0.0]], budget=2200 if L == 9 else 3800, palette="skein",
          extra={"dress": [["fm_table_folding", x, 0.0, z, 0] for x in (-2.0, 2.0) for z in np.arange(-L / 2 + 2.0, L / 2 - 1.0, 3.0).round(2).tolist()],
                 "vendors": 3 if L == 9 else 5},
          anchors={"vendor_0": [-3.6, 0.0, -L / 2 + 1.0, 0], "vendor_1": [3.6, 0.0, -L / 2 + 1.0, 0], "vendor_2": [0.0, 0.0, -L / 2 + 0.8, 0],
                   "stage": [0.0, 0.0, -L / 2 + 1.5, 0]},
          notes="the event marquee (9 x %d m, eave 2.75, ridge 4.75): candy-striped roof, a scalloped front gable and a closed "
                "back, open sides with bunting (2.35 m clear), three festoon strings under the ridge; a food hall or a music tent" % L)
def with_scale(fn):
    """the Weigh House: a 2 x 2 m platform scale (5 cm) and its dial board inside the door"""
    def b(q):
        m = fn(q)
        m.box((-1.0, 0.0, 3.5), (1.0, 0.05, 5.5), "steel")
        m.box((1.25, 0.0, 4.4), (1.35, 1.6, 4.6), "steel")
        m.box((1.35, 1.25, 4.3), (1.4, 1.85, 4.7), "glow")
        return m
    return b


for kind, cid in (("office", "txt_mooring_office"), ("weigh", "txt_weigh_house"), ("crew", "txt_crew")):
    piece("tent_logistics_" + kind, "tent", (with_scale if kind == "weigh" else (lambda f: f))(event_tent(15.0, logistics=True, sign=cid)), kind="tent", foot=[10.2, 15.1], lod1="keep",
          frame=ev_frame(15.0, True) + [B(-4.8, 0, z - 0.25, -4.55, 0.4, z + 0.25) for z in (-7.44, -4.46, -1.48, 1.48, 4.46, 7.44)]
          + [B(4.55, 0, z - 0.25, 4.8, 0.4, z + 0.25) for z in (-7.44, -4.46, -1.48, 1.48, 4.46, 7.44)],
          passes=[{"box": B(-1.15, 0, 7.2, 1.15, 2.35, 7.8), "kind": "door"}],
          walk=[[-4.3, -7.2, 4.3, 3.4, 0.0], [-4.3, 3.4, 1.2, 7.2, 0.0], [1.45, 3.4, 4.3, 7.2, 0.0]] if kind == "weigh" else [[-4.3, -7.2, 4.3, 7.2, 0.0]],
          anchors={"desk_0": [-3.0, 0.0, 5.0, 90], "desk_1": [3.0, 0.0, 5.0, -90], "door": [0.0, 0.0, 7.5, 0]},
          budget=2000, palette="logistics",
          extra={"sign": cid, "dress": [["fm_table_folding", -3.0, 0.0, 5.0, 90], ["fm_table_folding", 3.0, 0.0, 5.0, -90],
                                         ["fm_shelf_unit", -3.8, 0.0, -6.0, 90], ["fm_shelf_unit", 3.8, 0.0, -6.0, -90]]},
          notes="the mooring crew's white frame tent (9 x 15 m): closed walls with windows, a door in the front gable, "
                "ballast blocks at every post, the %s sign over the door" % cid)


# ------------------------------------------------------------------ the Lantern Top (a 24 m round big top)
LT_R, LT_WALL, LT_KP, LT_KH = 12.0, 3.2, 3.0, 12.0


def lt_roof_y(r):
    """the big top's canvas height at radius r: a sweep from the side wall up to the king-pole ring"""
    r0, r1 = LT_R, 4.6
    t = min(1.0, max(0.0, (r0 - r) / (r0 - r1)))
    return LT_WALL + 0.15 + (LT_KH - 1.0 - LT_WALL) * (t ** 1.45)


def lantern_top(q):
    m = Mesh()
    n = 24 if q else 12
    rings = [LT_R + 0.15, 10.0, 8.0, 6.3, 4.6] if q else [LT_R + 0.15, 8.0, 4.6]
    # the roof: gores (alternating) between the rings, lined, then a cupola over the king poles
    for k in range(n):
        a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
        sl = "canvas_a" if k % 2 == 0 else "canvas_b"
        for i in range(len(rings) - 1):
            ra, rb = rings[i], rings[i + 1]
            ya, yb = lt_roof_y(ra), lt_roof_y(rb)
            P = lambda r, a, y: (r * math.cos(a), y, r * math.sin(a))  # noqa: E731
            quad = [P(ra, a0, ya), P(ra, a1, ya), P(rb, a1, yb), P(rb, a0, yb)]
            am = (a0 + a1) / 2
            nrm = ((yb - ya) * math.cos(am), (ra - rb), (yb - ya) * math.sin(am))
            m.quad_facing(*quad, nrm, sl)
            if ra <= LT_R:
                li = [(x * 0.995, y - 0.03, z * 0.995) for x, y, z in quad]
                m.quad_facing(*li, tuple(-np.array(nrm)), "lining", 0.9)
            else:
                rl = LT_R - 0.05
                li = [P(rl, a0, lt_roof_y(rl) - 0.03), P(rl, a1, lt_roof_y(rl) - 0.03), P(rb * 0.995, a1, yb - 0.03), P(rb * 0.995, a0, yb - 0.03)]
                m.quad_facing(*li, tuple(-np.array(nrm)), "lining", 0.9)
    y_ring = lt_roof_y(4.6)
    lathe(m, [(4.62, 0.0), (3.4, 0.55), (1.2, 1.05), (0.0, 1.25)], "canvas_c", n=n, y0=y_ring)   # the cupola
    # king poles, quarter poles, side poles
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(sx * LT_KP, sz * LT_KP, 0.13, 0.0, y_ring - 0.02, "wood", n=8 if q else 5, r1=0.1)
            if q:
                m.cyl(sx * LT_KP, sz * LT_KP, 0.02, y_ring + 0.16, y_ring + 2.4, "metal", n=4)
                m.prism_xy([(sx * LT_KP + 0.02, y_ring + 2.35), (sx * LT_KP + 0.02, y_ring + 1.85), (sx * LT_KP + 1.1, y_ring + 2.1)], [],
                           sz * LT_KP - 0.006, sz * LT_KP + 0.006, "canvas_c")                    # the pennants
    nq = 12 if q else 6
    for k in range(nq):
        a = math.tau * (k + 0.5) / nq
        r = 8.0                                                                   # (on a ring: the lining is exact there)
        m.cyl(r * math.cos(a), r * math.sin(a), 0.07, 0.0, lt_roof_y(r) - 0.2, "wood", n=6 if q else 4)
    nsd = 24 if q else 12
    for k in range(nsd):                                                            # side poles and the side wall
        a0, a1 = math.tau * k / nsd, math.tau * (k + 1) / nsd
        if k in (0, nsd // 2):                                                     # (no pole mid-entrance)
            continue
        m.cyl(LT_R * 0.995 * math.cos(a0), LT_R * 0.995 * math.sin(a0), 0.05, 0.0, LT_WALL + 0.1, "wood", n=4)
        if k in (nsd - 1, nsd // 2 - 1, nsd // 2):                               # the two entrances (along x), 6.2 m wide
            continue
        ro, ri = LT_R + 0.06, LT_R + 0.04
        P2 = lambda r, a, y: (r * math.cos(a), y, r * math.sin(a))  # noqa: E731
        sl = "canvas_a" if k % 2 == 0 else "canvas_b"
        am = (a0 + a1) / 2
        m.quad_facing(P2(ro, a0, 0.05), P2(ro, a1, 0.05), P2(ro, a1, LT_WALL), P2(ro, a0, LT_WALL), (math.cos(am), 0, math.sin(am)), sl)
        m.quad_facing(P2(ri, a0, 0.05), P2(ri, a1, 0.05), P2(ri, a1, LT_WALL), P2(ri, a0, LT_WALL), (-math.cos(am), 0, -math.sin(am)), "lining", 0.9)
    # the entrance canopies (two, on +x and -x), a lantern ring inside, bulbs down every other seam outside
    for s in (-1, 1):
        t = Mesh()
        t.quad_facing((LT_R - 0.2, 3.0, -2.2), (LT_R + 2.2, 2.7, -2.2), (LT_R + 2.2, 2.7, 2.2), (LT_R - 0.2, 3.0, 2.2), (0.15, 1, 0), "canvas_c")
        t.quad_facing((LT_R - 0.2, 2.98, -2.2), (LT_R + 2.2, 2.68, -2.2), (LT_R + 2.2, 2.68, 2.2), (LT_R - 0.2, 2.98, 2.2), (-0.15, -1, 0), "lining", 0.9)
        for z in (-2.1, 2.1):
            t.cyl(LT_R + 2.1, z, 0.05, 0.0, 2.66, "wood", n=4)
        place(m, t, yaw=0 if s > 0 else 180)
    nl = 12 if q else 6
    for k in range(nl):
        a = math.tau * (k + 0.5) / nl
        hanging_lantern(m, 6.3 * math.cos(a) * 0.98, lt_roof_y(6.3) - 0.06, 6.3 * math.sin(a) * 0.98, q, "glow" if k % 2 else "glow_b")
    if q:
        kk = 0
        for k in range(0, n, 2):
            a = math.tau * k / n
            for i in range(10):
                r = LT_R + 0.15 - (LT_R + 0.15 - 4.7) * (i + 0.5) / 10
                d = 0.07
                y = float(np.interp(r, rings[::-1], [lt_roof_y(x) for x in rings[::-1]]))   # (the planar gores)
                bulb(m, ((r + 0.02) * math.cos(a), y + d, (r + 0.02) * math.sin(a)), 0.06, SK[kk % 4])
                kk += 1
    return m


LT_FRAME = ([B(sx * LT_KP - 0.13, 0, sz * LT_KP - 0.13, sx * LT_KP + 0.13, lt_roof_y(4.6), sz * LT_KP + 0.13) for sx in (-1, 1) for sz in (-1, 1)]
            + [B(8.0 * math.cos(math.tau * (k + 0.5) / 12) - 0.07, 0, 8.0 * math.sin(math.tau * (k + 0.5) / 12) - 0.07,
                 8.0 * math.cos(math.tau * (k + 0.5) / 12) + 0.07, 3.5, 8.0 * math.sin(math.tau * (k + 0.5) / 12) + 0.07) for k in range(12)]
            + [B(LT_R * 0.995 * math.cos(math.tau * k / 24) - 0.05, 0, LT_R * 0.995 * math.sin(math.tau * k / 24) - 0.05,
                 LT_R * 0.995 * math.cos(math.tau * k / 24) + 0.05, LT_WALL, LT_R * 0.995 * math.sin(math.tau * k / 24) + 0.05) for k in range(24) if k not in (0, 12)])
piece("tent_lantern_top", "tent", lantern_top, kind="tent", foot=[29.2, 24.3], lod1="keep", frame=LT_FRAME,
      passes=[{"box": B(LT_R - 0.6, 0, -1.4, LT_R + 1.6, 2.5, 1.4), "kind": "open"}, {"box": B(-LT_R - 1.6, 0, -1.4, -LT_R + 0.6, 2.5, 1.4), "kind": "open"}],
      walk=[[-6.5, -2.6, 6.5, 2.6, 0.0], [-2.6, -6.5, 2.6, 6.5, 0.0]], budget=9000, palette="skein",
      extra={"vendors": 8},
      anchors={"ring": [0.0, 0.0, 0.0, 0], "beacon": [0.0, lt_roof_y(4.6) + 1.25, 0.0, 0]},
      notes="the Lantern Top: a 24 m round big top (one per fair of 5+ islands): 4 king poles, striped gores, a cupola, a "
            "3.2 m side wall with two entrance canopies (along x), a ring of lanterns inside, bulbs down every other seam")


def canopy_striped(q):
    """a 6 x 3 m striped trading awning on six poles: front valance at 2.25-2.5 m, back 2.9 m"""
    m = Mesh()
    xs = (-2.94, 0.0, 2.94)
    for x in xs:
        m.box((x - 0.03, 0.0, 1.41), (x + 0.03, 2.47, 1.47), "steel")
        m.box((x - 0.03, 0.0, -1.47), (x + 0.03, 2.86, -1.41), "steel")
    ns = 12 if q else 6
    for k in range(ns):
        x0, x1 = -3.05 + 6.1 * k / ns, -3.05 + 6.1 * (k + 1) / ns
        sl = "canvas_a" if k % 2 == 0 else "canvas_b"
        quad = [(x0, 2.48, 1.55), (x1, 2.48, 1.55), (x1, 2.9, -1.55), (x0, 2.9, -1.55)]
        m.quad_facing(*quad, (0, 1, 0.13), sl)
        m.quad_facing(*[(x, y - 0.015, z) for x, y, z in quad], (0, -1, -0.13), "lining", 0.9)
    t = Mesh()
    t.prism_xy(scallops(6.1, 2.475, 0.25, 10 if q else 5), [], 1.555, 1.575, "canvas_c")
    m.add(t)
    if q:
        for i in range(16):
            x = -2.9 + 5.8 * (i + 0.5) / 16
            bulb(m, (x, 2.32, 1.62), 0.045, SK[i % 4])
    return m


piece("tent_canopy_striped", "tent", canopy_striped, kind="tent", foot=[6.2, 3.2], lod1="keep",
      frame=[B(x - 0.03, 0, 1.41, x + 0.03, 2.47, 1.47) for x in (-2.94, 0.0, 2.94)] + [B(x - 0.03, 0, -1.47, x + 0.03, 2.86, -1.41) for x in (-2.94, 0.0, 2.94)],
      passes=[{"box": B(-2.85, 0, 1.2, -0.08, 2.2, 1.9), "kind": "open"}, {"box": B(0.08, 0, 1.2, 2.85, 2.2, 1.9), "kind": "open"}],
      walk=[[-2.8, -0.5, 2.8, 1.3, 0.0]], budget=600, palette="skein",
      extra={"dress": [["tent_shelf", -1.5, 0.0, -1.1, 0], ["tent_shelf", 1.5, 0.0, -1.1, 0], ["tent_table", 0.0, 0.0, 0.6, 0]], "vendors": 2},
      anchors={"vendor_0": [-1.0, 0.0, -0.3, 0], "vendor_1": [1.0, 0.0, -0.3, 0]},
      notes="a striped trading awning (6 x 3 m) for the tent ring: scalloped front valance at 2.25 m, bulbs under it; dress = 2 shelves + a table")


# ------------------------------------------------------------------ Skein lanterns (origin at the hook, hanging down)
def _hook(m, drop):
    m.box((-0.006, -drop, -0.006), (0.006, 0.0, 0.006), "dark")
    ring_torus(m, (0.0, -0.03, 0.0), 0.025, 0.006, "brass", axis="z", n=6, k=3)


def lantern_pierced(q):
    """Moroccan pierced brass: an onion body of brass ribs over a glowing core, a dome cap and a finial"""
    m = Mesh()
    _hook(m, 0.12)
    n = 8 if q else 6
    y0 = -0.12
    lathe(m, [(0.0, 0.0), (0.05, -0.04), (0.08, -0.08)], "brass", n=n, y0=y0)
    lathe(m, [(0.075, -0.08), (0.15, -0.18), (0.17, -0.3), (0.12, -0.42), (0.06, -0.47), (0.0, -0.5)], "glow", n=n, y0=y0)
    if q:
        for k in range(n):                                                         # the ribs, just proud of the core
            a = math.tau * (k + 0.5) / n
            pts = [((r + 0.012) * math.cos(a), y0 + y, (r + 0.012) * math.sin(a)) for r, y in
                   ((0.08, -0.085), (0.155, -0.18), (0.176, -0.3), (0.126, -0.42), (0.065, -0.47))]
            sweep(m, pts, 0.008, "brass", n=3)
    lathe(m, [(0.02, 0.0), (0.0, -0.08)], "brass", n=5, y0=y0 - 0.5)
    return m


def lantern_fanous(q):
    """the Egyptian fanous: an octagonal brass frame with coloured glass panels, a pointed hat and a crown"""
    m = Mesh()
    _hook(m, 0.1)
    n = 8 if q else 6
    y = -0.1
    lathe(m, [(0.0, 0.0), (0.06, -0.06), (0.16, -0.16), (0.16, -0.18)], "brass", n=n, y0=y)
    lathe(m, [(0.135, -0.18), (0.135, -0.48), (0.09, -0.6), (0.0, -0.62)], "glow_b", n=n, y0=y)
    if q:
        for k in range(n):
            a = math.tau * k / n
            m.box((0.14 * math.cos(a) - 0.008, y - 0.48, 0.14 * math.sin(a) - 0.008), (0.14 * math.cos(a) + 0.008, y - 0.19, 0.14 * math.sin(a) + 0.008), "brass")
    return m


def lantern_paper(q):
    m = Mesh()
    _hook(m, 0.06)
    n = 10 if q else 6
    m.cyl(0.0, 0.0, 0.05, -0.09, -0.06, "dark", n=6)
    lathe(m, [(0.0, 0.0), (0.16, -0.04), (0.24, -0.2), (0.24, -0.34), (0.16, -0.5), (0.0, -0.54)], "glow", n=n, y0=-0.09)
    lathe(m, [(0.0, 0.0), (0.04, -0.02), (0.0, -0.1)], "canvas_b", n=5, y0=-0.63)
    return m


def lantern_globe(q):
    m = Mesh()
    _hook(m, 0.08)
    n = 10 if q else 6
    m.cyl(0.0, 0.0, 0.07, -0.13, -0.08, "brass", n=n)
    prof = [(0.06, 0.0)] + [(0.2 * math.sin(math.pi * t), -0.2 + 0.2 * math.cos(math.pi * t)) for t in (0.25, 0.5, 0.75)] + [(0.0, -0.4)]
    lathe(m, prof, "glow", n=n, y0=-0.13)
    return m


def lantern_star(q):
    """the parol: a five-pointed star lantern (two-faced, glowing) with tassels"""
    m = Mesh()
    _hook(m, 0.1)
    R, r = 0.32, 0.14
    pts = [((R if k % 2 == 0 else r) * math.sin(math.pi * k / 5), -0.1 - R + (R if k % 2 == 0 else r) * math.cos(math.pi * k / 5)) for k in range(10)]
    m.prism_xy(pts, [], -0.04, 0.04, "glow")
    if q:
        for x in (-0.12, 0.12):
            m.box((x - 0.008, -0.1 - R - 0.38, -0.008), (x + 0.008, -0.1 - R - 0.1, 0.008), "canvas_b")
    return m


def lantern_bell(q):
    m = Mesh()
    _hook(m, 0.06)
    n = 10 if q else 6
    m.cyl(0.0, 0.0, 0.05, -0.1, -0.06, "brass", n=n)
    lathe(m, [(0.045, 0.0), (0.09, -0.08), (0.12, -0.22), (0.2, -0.34), (0.0, -0.345)], "glow_b", n=n, y0=-0.1)
    lathe(m, [(0.0, 0.0), (0.03, -0.05), (0.0, -0.09)], "brass", n=5, y0=-0.446)
    return m


LANTERNS = {"pierced": (lantern_pierced, "Moroccan pierced brass over a glowing core"), "fanous": (lantern_fanous, "the fanous: coloured glass in a brass frame"),
            "paper": (lantern_paper, "a round paper lantern"), "globe": (lantern_globe, "a glass globe on a brass collar"),
            "star": (lantern_star, "the parol star lantern with tassels"), "bell": (lantern_bell, "a bell-shaped glass lantern")}
for k, (fn, note) in LANTERNS.items():
    piece("skein_lantern_" + k, "light", fn, kind="lantern", foot=None, lod1="drop", collide="none", ground=False, budget=400, palette="skein",
          anchors={"hook": [0.0, 0.0, 0.0, 0]}, notes="a Skein lantern: " + note + "; origin at its hook, hanging down (-y)")


# ------------------------------------------------------------------ festoons (origin at the left hook; the span along +x)
def festoon_span(L, skein):
    def b(q):
        m = Mesh()
        festoon(m, (0.0, 0.0, 0.0), (L, 0.0, 0.0), L * 0.06, 0.6 if q else 1.2, slots=SK if skein else ("bulb",), q=q)
        return m
    return b


def festoon_bulb(q):
    m = Mesh()
    m.cbox(0.0, -0.055, 0.0, 0.016, 0.055, 0.016, "dark")
    bulb(m, (0.0, -0.1, 0.0), 0.045, "bulb")
    return m


def festoon_pole(q):
    """a 5 m festoon pole (strings hook on at 4.6 m), a weighted base"""
    m = Mesh()
    m.box((-0.25, 0.0, -0.25), (0.25, 0.25, 0.25), "concrete")
    m.cyl(0.0, 0.0, 0.06, 0.25, 5.0, "steel", n=6 if q else 4, r1=0.045)
    m.box((-0.02, 4.58, 0.04), (0.02, 4.62, 0.16), "dark")
    return m


for L in (6, 9, 12):
    for sk in (False, True):
        piece("festoon_%s_%d" % ("skein" if sk else "warm", L), "light", festoon_span(float(L), sk), kind="festoon", foot=None, lod1="drop",
              collide="none", ground=False, budget=30 * L, palette="skein" if sk else "white",
              anchors={"start": [0.0, 0.0, 0.0, 0], "end": [float(L), 0.0, 0.0, 0]},
              notes="a %d m festoon string (6 %% sag, a bulb every 0.6 m: %s), from its origin to +x; hang at >= 4.2 m over aisles" % (
                  L, "Skein multicolour, bulb_a..d" if sk else "market warm white"))
piece("festoon_bulb", "light", festoon_bulb, kind="festoon", foot=None, lod1="drop", collide="none", ground=False, mid="full", budget=20,
      palette="white", notes="one festoon bulb and its lead (MultiMesh it along the runtime's own catenaries: StreetLights._festoon)")
piece("festoon_pole", "light", festoon_pole, kind="lamp", foot=None, lod1="keep", frame=[B(-0.25, 0, -0.25, 0.25, 0.25, 0.25), B(-0.06, 0.25, -0.06, 0.06, 5.0, 0.06)],
      anchors={"hook": [0.0, 4.6, 0.1, 0]}, budget=80, palette="lot", notes="a 5 m pole for festoon strings across open aisles (hook at 4.6 m)")


# ------------------------------------------------------------------ the gondola cabin (28: 24 seated + 4 standing + the warden)
from mk import rounded_rect  # noqa: E402

CAB_L, CAB_W, CAB_T, CAB_R = 5.84, 2.94, 0.12, 0.45
CAB_WIN0, CAB_DOOR_H, CAB_CEIL = 0.95, 2.22, 2.42
DOOR_X = 0.6
PIVOT_Y = 5.2


def _outline(L, W, r, n, extra_x=(), extra_z=()):
    """a rounded-rect outline with extra vertices on its straight sides (window posts, door jambs)"""
    pts = rounded_rect(L, W, r, n)
    out = []
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        out.append(a)
        if abs(a[1] - b[1]) < 1e-6 and abs(a[0] - b[0]) > 1.0:              # a long side (constant z)
            xs = sorted([x for x in extra_x if min(a[0], b[0]) + 0.05 < x < max(a[0], b[0]) - 0.05], reverse=a[0] > b[0])
            out += [(x, a[1]) for x in xs]
        elif abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) > 1.0:            # an end (constant x)
            zs = sorted([z for z in extra_z if min(a[1], b[1]) + 0.05 < z < max(a[1], b[1]) - 0.05], reverse=a[1] > b[1])
            out += [(a[0], z) for z in zs]
    return out


def _in_door(p0, p1, W):
    mx, mz = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    return abs(mx) < DOOR_X and abs(mz) > W / 2 - 0.2


def cabin_shell(m, q, L=CAB_L, W=CAB_W, livery=True, doors=True):
    nc = 3 if q else 2
    ex_x = (-1.55, -DOOR_X, DOOR_X, 1.55) if doors else (-1.55, 1.55)
    ex_z = (0.0,)
    outer = _outline(L, W, CAB_R, nc, ex_x, ex_z)
    midl = _outline(L - CAB_T, W - CAB_T, CAB_R - CAB_T / 2, nc, ex_x, ex_z)
    Po = Polygon(rounded_rect(L, W, CAB_R, nc))
    Pi = Polygon(rounded_rect(L - 2 * CAB_T, W - 2 * CAB_T, CAB_R - CAB_T, nc))
    ring = Po.difference(Pi)
    door_boxes = shapely.geometry.MultiPolygon([shapely.geometry.box(-DOOR_X, s * W / 2 - 0.3 if s > 0 else -W / 2 - 0.1, DOOR_X,
                                                                    W / 2 + 0.1 if s > 0 else -W / 2 + 0.3) for s in (-1, 1)]) if doors else None
    lower = ring.difference(door_boxes) if doors else ring
    poly_prism(m, Polygon(rounded_rect(L - 0.004, W - 0.004, CAB_R - 0.002, nc)), -0.22, 0.0, "cream")   # the floor slab (its top is the floor)
    poly_prism(m, Polygon(rounded_rect(L - 0.6, W - 0.6, 0.3, nc)), -0.42, -0.22, "dark")   # the under-body
    poly_prism(m, lower, 0.0, CAB_WIN0, "cream")
    poly_prism(m, ring, CAB_DOOR_H, CAB_CEIL, "cream")
    poly_prism(m, Polygon(rounded_rect(L + 0.02, W + 0.02, CAB_R + 0.01, nc)), CAB_CEIL, CAB_CEIL + 0.1, "accent")   # the roof (1 cm eave)
    poly_prism(m, Polygon(rounded_rect(L - 0.5, W - 0.5, 0.3, nc)), CAB_CEIL + 0.1, CAB_CEIL + 0.22, "cream")
    # window posts at every mid-wall vertex (door jambs run full height), glass between them
    n = len(midl)
    for k in range(n):
        x, z = midl[k]
        jamb = doors and abs(abs(x) - DOOR_X) < 1e-6 and abs(z) > W / 2 - 0.3
        y0 = 0.002 if jamb else CAB_WIN0
        m.box((x - 0.04, y0, z - 0.04), (x + 0.04, CAB_DOOR_H, z + 0.04), "dark")
    for k in range(n):
        a, b = np.array(midl[k]), np.array(midl[(k + 1) % n])
        if doors and _in_door(a, b, W):
            continue
        e = b - a
        Le = np.linalg.norm(e)
        if Le < 0.12:
            continue
        u = e / Le
        a2, b2 = a + u * 0.06, b - u * 0.06
        nrm = np.array([u[1], -u[0]])
        if Po.contains(shapely.geometry.Point(*(a2 + b2) / 2 + nrm * 0.2)) and not Po.contains(shapely.geometry.Point(*(a2 + b2) / 2 - nrm * 0.2)):
            nrm = -nrm
        for off, sgn in ((0.006, 1), (-0.006, -1)):
            pa, pb = a2 + nrm * off, b2 + nrm * off
            m.quad_facing((pa[0], CAB_WIN0 + 0.004, pa[1]), (pb[0], CAB_WIN0 + 0.004, pb[1]), (pb[0], CAB_DOOR_H - 0.004, pb[1]),
                          (pa[0], CAB_DOOR_H - 0.004, pa[1]), (sgn * nrm[0], 0, sgn * nrm[1]), "glass")
    if livery:                                                                   # the clan livery: two bands 2.7 cm proud
        no = len(outer)
        for k in range(no):
            a, b = np.array(outer[k]), np.array(outer[(k + 1) % no])
            if doors and _in_door(a, b, W):
                continue
            e = b - a
            Le = np.linalg.norm(e)
            if Le < 1e-6:
                continue
            u = e / Le
            nrm = np.array([u[1], -u[0]])
            if Po.contains(shapely.geometry.Point(*((a + b) / 2 + nrm * 0.05))):
                nrm = -nrm
            for y0, y1, sl in ((0.5, 0.72, "accent"), (0.78, 0.84, "accent2")):
                pa, pb = a + nrm * 0.027, b + nrm * 0.027
                m.quad_facing((pa[0], y0, pa[1]), (pb[0], y0, pb[1]), (pb[0], y1, pb[1]), (pa[0], y1, pa[1]), (nrm[0], 0, nrm[1]), sl)
    return outer


def cabin_hanger(m, q, top=CAB_CEIL + 0.22):
    for s in (-1, 1):
        m.box((s * 0.7 - 0.12, top, -0.12), (s * 0.7 + 0.12, top + 0.04, 0.12), "steel")
        m.tube((s * 0.7, top + 0.04, 0.0), (s * 0.13, PIVOT_Y - 0.15, 0.0), 0.06, "steel", n=6 if q else 4)
    m.box((-0.16, PIVOT_Y - 0.15, -0.13), (0.16, PIVOT_Y + 0.15, 0.13), "metal")


def gondola_pax(q):
    m = Mesh()
    cabin_shell(m, q)
    zi = CAB_W / 2 - CAB_T                                                         # the inner wall line (1.35)
    xi = CAB_L / 2 - CAB_T                                                         # (2.8)
    seats = []
    for s in (-1, 1):                                                              # side benches, 4 seats each
        for xa, xb in ((-2.45, -0.68), (0.68, 2.45)):
            seats.append(("z", s, xa, xb))
    for s in (-1, 1):                                                              # end benches, 4 seats each
        seats.append(("x", s, -0.88, 0.88))
    for ax, s, a, b in seats:
        t = Mesh()                                                                 # built for the +z wall, then turned
        L = b - a
        t.box((a + 0.04, 0.0, -0.45), (b - 0.04, 0.4, -0.06), "dark")
        if q:
            for k in range(4):
                c0 = a + L * k / 4 + 0.012
                c1 = a + L * (k + 1) / 4 - 0.012
                t.box((c0, 0.4, -0.47), (c1, 0.47, -0.02), "fabric")
                t.box((c0, 0.5, -0.06), (c1, 0.92, 0.0), "fabric", 0.9)
        else:
            t.box((a, 0.4, -0.47), (b, 0.47, -0.02), "fabric")
            t.box((a, 0.5, -0.06), (b, 0.92, 0.0), "fabric", 0.9)
        if ax == "z":
            place(m, t, 0.0, 0.0, s * zi, 0 if s > 0 else 180)
        else:
            place(m, t, s * xi, 0.0, 0.0, 90 if s > 0 else -90)
    # the warden's console: a pedestal with a lit, sloped screen (faces -x, toward the warden)
    m.box((1.85, 0.0, -0.3), (2.25, 0.95, 0.3), "steel")
    m.prism_xy([(1.85, 0.95), (2.25, 1.15), (2.25, 1.2), (1.85, 1.0)], [], -0.29, 0.29, "steel")
    sc = Mesh()
    sc.quad_facing((1.88, 0.993, -0.25), (1.88, 0.993, 0.25), (2.2, 1.153, 0.25), (2.2, 1.153, -0.25), (-0.45, 1, 0), "glow")
    m.add(sc, lambda p: (p[0], p[1] + 0.03, p[2]))
    for x in (-1.2, 1.2):                                                          # grab poles, floor to ceiling
        m.cyl(x, 0.0, 0.025, 0.0, CAB_CEIL, "steel", n=6 if q else 4)
        if q:
            m.cyl(x, 0.0, 0.06, 0.0, 0.03, "steel", n=6)
    m.box((-1.0, CAB_CEIL - 0.03, -0.3), (1.0, CAB_CEIL, 0.3), "glow")            # the ceiling light (lit face)
    if q:
        m.box((-2.0, CAB_CEIL - 0.02, -0.12), (-1.3, CAB_CEIL, 0.12), "glow")
        m.box((1.3, CAB_CEIL - 0.02, -0.12), (2.0, CAB_CEIL, 0.12), "glow")
        bulb(m, (0.0, -0.47, 0.0), 0.06, "warn")                                 # the belly light
    cabin_hanger(m, q)
    return m


def gondola_door(q):
    """one sliding door leaf (1.24 x 2.2 m): framed glass; slides along +x outside the wall"""
    m = Mesh()
    w, h = 1.24, 2.2
    m.box((-w / 2, 0.0, -0.02), (w / 2, 0.95, 0.02), "cream")
    m.box((-w / 2, 0.952, -0.02), (-w / 2 + 0.06, h, 0.02), "dark")
    m.box((w / 2 - 0.06, 0.952, -0.02), (w / 2, h, 0.02), "dark")
    m.box((-w / 2 + 0.062, h - 0.06, -0.018), (w / 2 - 0.062, h - 0.002, 0.018), "dark")
    m.quad((-w / 2 + 0.064, 0.954, 0.004), (w / 2 - 0.064, 0.954, 0.004), (w / 2 - 0.064, h - 0.064, 0.004), (-w / 2 + 0.064, h - 0.064, 0.004), "glass")
    m.quad((w / 2 - 0.064, 0.954, -0.004), (-w / 2 + 0.064, 0.954, -0.004), (-w / 2 + 0.064, h - 0.064, -0.004), (w / 2 - 0.064, h - 0.064, -0.004), "glass")
    if q:
        m.box((-0.45, 0.6, 0.02), (-0.3, 0.64, 0.04), "steel")
        m.quad((-w / 2 + 0.002, 0.5, 0.047), (w / 2 - 0.002, 0.5, 0.047), (w / 2 - 0.002, 0.72, 0.047), (-w / 2 + 0.002, 0.72, 0.047), "accent")
    return m


CAB_FRAME = ([B(-2.92, -0.42, -1.47, 2.92, 0.0, 1.47), B(-2.92, 0, -1.47, -2.8, 2.42, 1.47), B(2.8, 0, -1.47, 2.92, 2.42, 1.47)]
             + [B(-2.8, 0, s * 1.35 if s > 0 else -1.47, -DOOR_X, 2.42, 1.47 if s > 0 else -1.35) for s in (-1, 1)]
             + [B(DOOR_X, 0, s * 1.35 if s > 0 else -1.47, 2.8, 2.42, 1.47 if s > 0 else -1.35) for s in (-1, 1)]
             + [B(-2.92, 2.42, -1.47, 2.92, 2.64, 1.47)]
             + [B(xa, 0, s * 0.88 if s > 0 else -1.35, xb, 0.47, 1.35 if s > 0 else -0.88) for s in (-1, 1) for xa, xb in ((-2.45, -0.68), (0.68, 2.45))]
             + [B(s * 2.33 if s > 0 else -2.8, 0, -0.88, 2.8 if s > 0 else -2.33, 0.47, 0.88) for s in (-1, 1)]
             + [B(1.85, 0, -0.3, 2.25, 1.2, 0.3)])
piece("gondola_cabin_pax", "ropeway", gondola_pax, kind="cabin", foot=[5.84, 2.94], lod1="keep", frame=CAB_FRAME, ground=False,
      passes=[{"box": B(-0.56, 0, s * 1.3 if s > 0 else -1.6, 0.56, 2.2, 1.6 if s > 0 else -1.3), "kind": "door"} for s in (-1, 1)],
      walk=[[-2.3, -0.86, 1.8, 0.86, 0.0], [-0.55, -1.34, 0.55, 1.34, 0.0]], budget=3500, palette="ropeway",
      anchors={"pivot": [0.0, PIVOT_Y, 0.0, 0], "door_n_closed": [0.0, 0.0, 1.52, 0], "door_n_open": [1.3, 0.0, 1.52, 0],
               "door_s_closed": [0.0, 0.0, -1.52, 180], "door_s_open": [1.3, 0.0, -1.52, 180], "warden": [1.5, 0.0, 0.0, 90],
               **{"seat_%d" % k: v for k, v in enumerate(
                   [[x, 0.47, s * 1.12, 180 if s > 0 else 0] for s in (-1, 1) for x in (-2.23, -1.79, -1.34, -0.9, 0.9, 1.34, 1.79, 2.23)]
                   + [[s * 2.57, 0.47, z, -90 if s > 0 else 90] for s in (-1, 1) for z in (-0.66, -0.22, 0.22, 0.66)])},
               **{"stand_%d" % k: [x, 0.0, z, 0] for k, (x, z) in enumerate(((-1.6, 0.4), (-1.6, -0.4), (-0.4, 0.4), (0.4, -0.4)))}},
      moving={"kind": "platform", "pivot": [0.0, PIVOT_Y, 0.0], "carried_by": "gondola_carriage"},
      notes="the passenger cabin (Peak 2 Peak class): 24 seats on four side and two end benches, 4 standing, the warden's "
            "lit console; panoramic glass all round, sliding doors both long sides (gondola_cabin_door, 1.2 x 2.2 m clear), "
            "2.42 m to the ceiling (the light panels at 2.39), clan livery bands, a hanger to the carriage pivot (5.2 m). "
            "Origin at the floor centre; ride it as a moving platform")
piece("gondola_cabin_door", "ropeway", gondola_door, kind="cabin", foot=[1.24, 0.05], lod1="drop", frame=[B(-0.62, 0, -0.02, 0.62, 2.2, 0.02)],
      ground=False, budget=120, palette="ropeway", moving={"kind": "slide", "axis": [1, 0, 0], "travel": 1.3},
      notes="a cabin's sliding door leaf: closed at door_*_closed, open at door_*_open (slides 1.3 m along +x)")


def gondola_cargo(q):
    """the cargo cabin: an open steel cradle carrying one skybox (2.4 x 2.4 x 3.0 m), its hanger to the pivot"""
    m = Mesh()
    L, W = 3.4, 2.7
    m.box((-L / 2, -0.3, -W / 2), (L / 2, 0.0, W / 2), "steel")                    # the cradle deck
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((sx * L / 2 - (0.12 if sx > 0 else 0), 0.0, sz * W / 2 - (0.12 if sz > 0 else 0)),
                  (sx * L / 2 + (0 if sx > 0 else 0.12), 2.598, sz * W / 2 + (0 if sz > 0 else 0.12)), "steel")
    for sx in (-1, 1):
        m.box((sx * L / 2 - (0.12 if sx > 0 else 0), 2.6, -W / 2), (sx * L / 2 + (0 if sx > 0 else 0.12), 2.75, W / 2), "steel")
    for sz in (-1, 1):
        m.box((-L / 2 + 0.12, 2.6, sz * W / 2 - (0.12 if sz > 0 else -0.002)), (L / 2 - 0.12, 2.75, sz * W / 2 + (-0.002 if sz > 0 else 0.12)), "steel")
    m.box((-1.5, 0.0, -1.2), (1.5, 2.4, 1.2), "accent")                             # the skybox
    if q:
        for k in range(1, 10):                                                     # its corrugation (strips 2.7 cm proud)
            x = -1.5 + 3.0 * k / 10
            for s in (-1, 1):
                m.quad_facing((x - 0.04, 0.1, s * 1.227), (x + 0.04, 0.1, s * 1.227), (x + 0.04, 2.3, s * 1.227), (x - 0.04, 2.3, s * 1.227), (0, 0, s), "accent2")
    cabin_hanger(m, q, top=2.75)
    return m


piece("gondola_cabin_cargo", "ropeway", gondola_cargo, kind="cabin", foot=[3.4, 2.7], lod1="keep", ground=False,
      frame=[B(-1.7, -0.3, -1.35, 1.7, 0.0, 1.35), B(-1.5, 0, -1.2, 1.5, 2.4, 1.2)], budget=2500, palette="ropeway",
      anchors={"pivot": [0.0, PIVOT_Y, 0.0, 0], "skybox": [0.0, 0.0, 0.0, 0]}, moving={"kind": "platform", "pivot": [0.0, PIVOT_Y, 0.0]},
      notes="the cargo cabin: an open cradle with one skybox (hoist_trade.container 2.4 x 2.4 x 3 m) or 3 pallets at `skybox`")


ROPE_Y, ROPE_DZ = 0.9, 0.3


def gondola_carriage(q):
    """the track-rope carriage: two bogies of four sheaves riding the two track ropes (z +-0.3, 0.9 m over the pivot),
    the haul-rope clamp, the hanger bearing at the origin (= the cabin's pivot)"""
    m = Mesh()
    m.box((-1.3, 0.45, -0.42), (1.3, 0.6, 0.42), "steel")                           # the carriage beam
    m.box((-0.18, 0.0, -0.16), (0.18, 0.45, 0.16), "steel")                         # the hanger bearing
    for s in (-1, 1):
        for bx in (-0.75, 0.75):
            plate = (s * ROPE_DZ - 0.11, s * ROPE_DZ - 0.05) if s > 0 else (s * ROPE_DZ + 0.05, s * ROPE_DZ + 0.11)
            m.box((bx - 0.45, 0.6, plate[0]), (bx + 0.45, 1.36, plate[1]), "metal")
            for wx in ((bx - 0.25, bx + 0.25) if q else (bx,)):
                wh = Mesh()
                wh.cyl(0.0, 0.0, 0.17, -0.025, 0.025, "dark", n=10 if q else 6)
                m.add(wh, lambda p, wx=wx, s=s: (rot_x(90)(p)[0] + wx, rot_x(90)(p)[1] + ROPE_Y + 0.03 + 0.17, rot_x(90)(p)[2] + s * ROPE_DZ))
    m.box((-0.2, 0.3, -0.06), (0.2, 0.45, 0.06), "dark")                             # the haul-rope clamp
    return m


piece("gondola_carriage", "ropeway", gondola_carriage, kind="cabin", foot=[2.6, 0.84], lod1="keep", collide="none", ground=False,
      budget=1200, palette="ropeway", anchors={"pivot": [0.0, 0.0, 0.0, 0], "track_l": [0.0, ROPE_Y, -ROPE_DZ, 0], "track_r": [0.0, ROPE_Y, ROPE_DZ, 0],
                                              "haul": [0.0, 0.37, 0.0, 0]},
      moving={"kind": "carriage", "rope_dir": [1, 0, 0]},
      notes="the carriage: origin at the hanger pivot; the track ropes run along x at (y 0.9, z +-0.3), the haul rope at y 0.37")


# ------------------------------------------------------------------ the crew's drop cage (24 standing, free-hanging)
CAGE_L, CAGE_W, CAGE_H, HOOK_Y = 3.8, 2.7, 2.4, 5.4


def drop_cage(q):
    m = Mesh()
    L, W = CAGE_L, CAGE_W
    m.box((-L / 2, -0.12, -W / 2), (L / 2, 0.0, W / 2), "steel")                    # the deck (grating)
    if q:
        for k in range(1, 12):
            x = -L / 2 + L * k / 12
            if abs(abs(x) - 1.3) < 0.12:
                continue
            m.quad((x - 0.015, -0.123, -W / 2 + 0.05), (x + 0.015, -0.123, -W / 2 + 0.05), (x + 0.015, -0.123, W / 2 - 0.05), (x - 0.015, -0.123, W / 2 - 0.05), "dark")
        for x in (-1.3, 1.3):                                                       # landing skids
            m.box((x - 0.06, -0.3, -W / 2 + 0.1), (x + 0.06, -0.12, W / 2 - 0.1), "dark")
    posts = [(sx * (L / 2 - 0.04), sz * (W / 2 - 0.04)) for sx in (-1, 1) for sz in (-1, 1)] + [(0.0, sz * (W / 2 - 0.04)) for sz in (-1, 1)]
    for x, z in posts:
        m.box((x - 0.04, 0.0, z - 0.04), (x + 0.04, CAGE_H, z + 0.04), "steel")
    for y in (1.05, CAGE_H - 0.06):                                                 # rails and the top frame
        for sz in (-1, 1):
            z = sz * (W / 2 - 0.04)
            for xa, xb in ((-L / 2 + 0.08, -0.04), (0.04, L / 2 - 0.08)):
                if y < 2 and sz > 0 and xa > 0:
                    continue                                                       # (the gate: no rail)
                m.box((xa, y, z - 0.025), (xb, y + 0.06, z + 0.025), "steel")
        for sx in (-1, 1):
            x = sx * (L / 2 - 0.04)
            m.box((x - 0.025, y, -W / 2 + 0.08), (x + 0.025, y + 0.06, W / 2 - 0.08), "steel")
    if q:                                                                          # mesh infill: vertical bars to 1.05 m
        for sz in (-1, 1):
            z = sz * (W / 2 - 0.04)
            for k in range(16):
                x = -L / 2 + 0.1 + (L - 0.2) * (k + 0.5) / 16
                if abs(x) < 0.08 or (sz > 0 and x > 0):
                    continue
                m.box((x - 0.008, 0.0, z - 0.008), (x + 0.008, 1.05, z + 0.008), "steel")
        for sx in (-1, 1):
            x = sx * (L / 2 - 0.04)
            for k in range(10):
                z = -W / 2 + 0.1 + (W - 0.2) * (k + 0.5) / 10
                m.box((x - 0.008, 0.0, z - 0.008), (x + 0.008, 1.05, z + 0.008), "steel")
    for sx in (-1, 1):                                                              # the bridle: four chains to the hook ring
        for sz in (-1, 1):
            m.tube((sx * (L / 2 - 0.04), CAGE_H, sz * (W / 2 - 0.04)), (sx * 0.12, HOOK_Y - 0.12, sz * 0.12), 0.025, "dark", n=4)
    m.box((-0.16, HOOK_Y - 0.12, -0.16), (0.16, HOOK_Y, 0.16), "metal")
    ring_torus(m, (0.0, HOOK_Y + 0.14, 0.0), 0.12, 0.03, "steel", axis="x", n=8, k=4)
    for sx in (-1, 1):
        for sz in (-1, 1):
            bulb(m, (sx * (L / 2 + 0.05), CAGE_H - 0.15, sz * (W / 2 + 0.05)), 0.05, "warn")
    return m


piece("gondola_drop_cage", "ropeway", drop_cage, kind="cabin", foot=[3.8, 2.7], lod1="keep", ground=False,
      frame=[B(-1.9, -0.12, -1.35, 1.9, 0.0, 1.35), B(-1.9, 0, -1.35, 1.9, 1.11, -1.27), B(-1.9, 0, 1.27, 0.04, 1.11, 1.35),
             B(-1.9, 0, -1.35, -1.82, 1.11, 1.35), B(1.82, 0, -1.35, 1.9, 1.11, 1.35)],
      passes=[{"box": B(0.06, 0, 1.15, 1.8, 2.3, 1.6), "kind": "open"}], walk=[[-1.8, -1.25, 1.8, 1.25, 0.0]], budget=2400, palette="ropeway",
      anchors={"hook": [0.0, HOOK_Y + 0.14, 0.0, 0], **{"stand_%d" % k: [-1.5 + 0.6 * (k % 6), 0.0, -0.9 + 0.6 * (k // 6), 0] for k in range(24)}},
      moving={"kind": "platform", "pivot": [0.0, HOOK_Y + 0.14, 0.0], "hangs_from": "hoist line (free, swinging)"},
      notes="the crew's drop cage: a 3.8 x 2.7 m steel cage for the first 24 down the hoist line (CREW_DOWN, before any "
            "track rope): a grating deck, a 1.05 m rail with bar infill, a gate on +z, a top frame at 2.4 m, a four-chain "
            "bridle to the hook ring, red corner lights.  Origin at the deck; 24 stand_* spots")


# ------------------------------------------------------------------ rope units (1 m along +x: scale x to the span)
def rope_unit(r, n, slot="rope"):
    def b(q):
        m = Mesh()
        for k in range(n):
            a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
            p = lambda x, a: (x, r * math.cos(a), r * math.sin(a))  # noqa: E731
            m.quad_facing(p(0.0, a0), p(1.0, a0), p(1.0, a1), p(0.0, a1), (0, math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2)), slot)
        return m
    return b


def rope_ribbon(q):
    m = Mesh()
    m.quad((0.0, -0.5, 0.0), (1.0, -0.5, 0.0), (1.0, 0.5, 0.0), (0.0, 0.5, 0.0), "rope")
    return m


for rid, r, n, note in (("rope_track", 0.03, 6, "a track rope (60 mm)"), ("rope_haul", 0.023, 5, "the haul rope (46 mm)"),
                        ("rope_hawser", 0.06, 6, "a mooring hawser (120 mm)"), ("rope_hoist", 0.018, 4, "a free hoist line")):
    piece(rid + "_unit", "rope", rope_unit(r, n, "steel" if rid != "rope_hawser" else "rope"), kind="rope", foot=None, lod1="keep", collide="none",
          ground=False, mid="full", budget=12, palette="ropeway",
          notes=note + ": a 1 m open tube along +x (scale x to the segment; chain segments for the sag)")
piece("rope_ribbon_unit", "rope", rope_ribbon, kind="rope", foot=None, lod1="keep", collide="none", ground=False, mid="full", budget=2,
      palette="ropeway", notes="a 1 x 1 m ribbon along +x facing +z: the far-range rope (scale y to the width, turn it to the camera)")


# ------------------------------------------------------------------ ground anchor blocks (deadmen)
def deadman(up):
    def b(q):
        m = Mesh()
        top = 0.03
        # the chamfered cap: top 1.1 m square at y 0.03 over the 1.2 m body at y 0.0
        cap = [(-0.6, 0.0, -0.6), (0.6, 0.0, -0.6), (0.6, 0.0, 0.6), (-0.6, 0.0, 0.6)]
        tops = [(-0.55, top, -0.55), (0.55, top, -0.55), (0.55, top, 0.55), (-0.55, top, 0.55)]
        for k in range(4):
            a, b2, c, d = cap[k], cap[(k + 1) % 4], tops[(k + 1) % 4], tops[k]
            mid = np.mean([a, b2], axis=0)
            m.quad_facing(a, b2, c, d, (mid[0], 0.5, mid[2]), "concrete")
        m.quad_facing(*tops, (0, 1, 0), "concrete")
        m.box((-0.16, top, -0.16), (0.16, top + 0.015, 0.16), "steel")
        if up:
            m.box((-0.012, top + 0.015, -0.06), (0.012, top + 0.14, 0.06), "steel")
            ring_torus(m, (0.0, top + 0.015 + 0.17 + 0.03, 0.0), 0.17, 0.028, "steel", axis="x", n=10 if q else 6)
        else:
            ring_torus(m, (0.0, top + 0.015 + 0.028, 0.0), 0.17, 0.028, "steel", axis="y", n=10 if q else 6)
        return m
    return b


for up in (False, True):
    piece("deadman_ring" + ("_up" if up else ""), "mooring", deadman(up), kind="anchor", foot=[1.2, 1.2], lod1="drop",
          frame=[B(-0.6, -0.6, -0.6, 0.6, 0.03, 0.6)], budget=200, palette="mooring",
          anchors={"hawser": [0.0, 0.3 if up else 0.07, 0.0, 0]},
          notes="a buried concrete deadman flush in the lawn (3 cm chamfered cap, its collision only the block) with its "
                + ("ring standing up, a hawser made fast" if up else "ring lying flat (no hawser)"))


# ------------------------------------------------------------------ mooring masts (city 30 m, town 22 m: lattice; village 12 m: guyed pole)
def lattice_mast(H, base, top, q, plats=()):
    m = Mesh()
    m.box((-base - 0.9, 0.0, -base - 0.9), (base + 0.9, 0.45, base + 0.9), "concrete")      # the plinth
    leg = lambda sx, sz, y: (sx * (base + (top - base) * y / H), y, sz * (base + (top - base) * y / H))  # noqa: E731
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.tube(leg(sx, sz, 0.45), leg(sx, sz, H), 0.09, "steel", n=6 if q else 4)
    step = 3.0
    ys = [0.45 + step * k for k in range(1, int((H - 0.45) / step) + 1)]
    for i, y in enumerate(ys):                                                     # horizontals (and X braces on each face)
        hw = base + (top - base) * y / H
        for yaw in (0, 90, 180, 270):
            t = Mesh()
            t.tube((-hw + 0.09, y, hw), (hw - 0.09, y, hw), 0.04, "steel", n=4)
            if q:
                y0 = ys[i - 1] if i else 0.45
                h0 = base + (top - base) * y0 / H
                t.tube((-h0 + 0.1, y0 + 0.06, h0), (hw - 0.1, y - 0.06, hw), 0.03, "steel", n=4)
                t.tube((h0 - 0.1, y0 + 0.06, h0), (-hw + 0.1, y - 0.06, hw), 0.03, "steel", n=4)
            place(m, t, yaw=yaw)
    # the ladder up the -z face's inside, with a cage hoop every 3 m
    lz = 0.0                                                                       # (up the core, through hatches)
    for x in (-0.22, 0.22):
        m.box((x - 0.025, 0.45, lz - 0.025 - 0.0), (x + 0.025, H, lz + 0.025), "metal")
    nr = int((H - 0.45) / (0.3 if q else 0.9))
    for k in range(1, nr):
        y = 0.45 + (H - 0.45) * k / nr
        m.box((-0.195, y - 0.015, lz - 0.015), (0.195, y + 0.015, lz + 0.015), "metal")
    for y in plats:                                                                # platforms with railings
        hw = base + (top - base) * y / H
        m.box((-hw - 0.7, y - 0.08, -hw - 0.7), (hw + 0.7, y, hw + 0.7), "steel")
        if q:
            ring = Mesh()
            ring.box((-hw - 0.68, y + 1.0, hw + 0.66), (hw + 0.62, y + 1.05, hw + 0.7), "accent")
            for x in np.linspace(-hw - 0.66, hw + 0.66, 5)[:-1]:
                ring.box((x - 0.02, y, hw + 0.66), (x + 0.02, y + 0.998, hw + 0.7), "accent")
            for yaw in (0, 90, 180, 270):
                place(m, ring, yaw=yaw)
    m.box((-top - 0.2, H, -top - 0.2), (top + 0.2, H + 0.3, top + 0.2), "steel")   # the head seat
    for sx in (-1, 1):                                                             # obstruction lights
        for sz in (-1, 1):
            bulb(m, (sx * (top + 0.15), H + 0.42, sz * (top + 0.15)), 0.09, "warn")
            if len(plats) > 1:
                hw = base + (top - base) * plats[0] / H
                bulb(m, (sx * (hw + 0.6), plats[0] + 1.15, sz * (hw + 0.6)), 0.08, "warn")
    return m


def mast_head(R, q):
    """the turning head: a turntable drum, the hawser cone pointing +z, a winch drum, a red light; spins about y"""
    m = Mesh()
    n = 12 if q else 8
    m.cyl(0.0, 0.0, R, 0.0, 0.5, "steel", n=n)
    m.cyl(0.0, 0.0, R * 0.7, 0.5, 1.3, "accent", n=n)
    cone = Mesh()
    lathe(cone, [(0.0, 0.0), (0.18, 0.05), (0.75, 1.6), (0.8, 1.7)], "trim", n=n)
    m.add(cone, lambda p: (rot_x(90)(p)[0], rot_x(90)(p)[1] + 0.9, rot_x(90)(p)[2] + R * 0.7 - 0.02))
    drum = Mesh()
    drum.cyl(0.0, 0.0, 0.32, -0.55, 0.55, "dark", n=n)
    m.add(drum, lambda p: (rot_z(90)(p)[0], rot_z(90)(p)[1] + 1.65, rot_z(90)(p)[2] - 0.2))
    for s in (-1, 1):
        m.box((s * 0.62 - 0.05, 1.3, -0.45), (s * 0.62 + 0.05, 1.95, 0.05), "steel")
    m.cyl(0.0, 0.0, 0.04, 1.3, 2.3, "metal", n=4)
    bulb(m, (0.0, 2.42, 0.0), 0.12, "warn")
    return m


for tier, H, base, top, plats in (("city", 30.0, 1.6, 0.6, (15.0, 27.0)), ("town", 22.0, 1.3, 0.55, (19.0,))):
    piece("mooring_mast_" + tier, "mooring", (lambda H, base, top, plats: (lambda q: lattice_mast(H, base, top, q, plats)))(H, base, top, plats),
          kind="mast", foot=None, lod1="keep", frame=[B(-base - 0.9, 0, -base - 0.9, base + 0.9, 0.45, base + 0.9),
                                                       B(-base - 0.1, 0.45, -base - 0.1, base + 0.1, H, base + 0.1)],
          budget=5000, palette="mooring", anchors={"head": [0.0, H + 0.3, 0.0, 0], "festoon_top": [0.0, H, 0.0, 0]},
          notes="the %s mooring mast: a %d m four-legged steel lattice on its plinth, ladder, %d platform(s), red "
                "obstruction lights; mooring_mast_head_%s turns on `head`; festoons run from festoon_top to the ground" % (tier, H, len(plats), tier))
    piece("mooring_mast_head_" + tier, "mooring", (lambda R: (lambda q: mast_head(R, q)))(top + 0.25), kind="mast", foot=None, lod1="keep",
          collide="none", ground=False, budget=600, palette="mooring", moving={"kind": "spin", "axis": [0, 1, 0], "pivot": [0, 0, 0], "follows": "the moored island"},
          anchors={"hawser": [0.0, 0.9, top + 0.25 + 1.6, 0]},
          notes="the %s mast's turning head: it swings to face the moored island; hawsers leave from `hawser` (the cone's mouth)" % tier)


def village_mast(q):
    """the village tier: a 12 m guyed steel pole with a small turning head and three guys to their blocks (r 7 m)"""
    m = Mesh()
    m.box((-0.8, 0.0, -0.8), (0.8, 0.45, 0.8), "concrete")
    m.cyl(0.0, 0.0, 0.28, 0.45, 12.0, "steel", n=10 if q else 6, r1=0.2)
    m.cyl(0.0, 0.0, 0.42, 12.0, 12.35, "accent", n=10 if q else 6)
    cone = Mesh()
    lathe(cone, [(0.0, 0.0), (0.12, 0.04), (0.45, 1.0), (0.5, 1.08)], "trim", n=8)
    m.add(cone, lambda p: (rot_x(90)(p)[0], rot_x(90)(p)[1] + 12.17, rot_x(90)(p)[2] + 0.4))
    bulb(m, (0.0, 12.5, 0.0), 0.1, "warn")
    for k in range(3):
        a = math.tau * k / 3 + math.pi / 2
        gx, gz = 7.0 * math.cos(a), 7.0 * math.sin(a)
        m.box((gx - 0.45, 0.0, gz - 0.45), (gx + 0.45, 0.4, gz + 0.45), "concrete")
        m.tube((gx * 0.995, 0.4, gz * 0.995), (0.25 * math.cos(a), 10.0, 0.25 * math.sin(a)), 0.016, "dark", n=4)
    return m


piece("mooring_mast_village", "mooring", village_mast, kind="mast", foot=None, lod1="keep",
      frame=[B(-0.8, 0, -0.8, 0.8, 0.45, 0.8), B(-0.28, 0.45, -0.28, 0.28, 12.35, 0.28)]
      + [B(7.0 * math.cos(math.tau * k / 3 + math.pi / 2) - 0.45, 0, 7.0 * math.sin(math.tau * k / 3 + math.pi / 2) - 0.45,
           7.0 * math.cos(math.tau * k / 3 + math.pi / 2) + 0.45, 0.4, 7.0 * math.sin(math.tau * k / 3 + math.pi / 2) + 0.45) for k in range(3)],
      budget=800, palette="mooring", anchors={"hawser": [0.0, 12.17, 1.5, 0]},
      notes="the village mooring post: a 12 m guyed pole at the centre of the 8-block ring, a hawser cone at 12 m (the "
            "village tier has no lattice mast; the host island makes fast to the ring and this post)")


# ------------------------------------------------------------------ the ground station (a jig-back's bottom station, two berths)
GS_PLAT_Y = 0.45
GS_BERTH_Z = 3.25
GS_PIVOT_Y = GS_PLAT_Y + PIVOT_Y
GS_ROPE_Y = GS_PIVOT_Y + ROPE_Y
GS_HAUL_Y = GS_PIVOT_Y + 0.37
GS_TOP = 7.6
GS_PLATS = [(-7.4, -4.85), (-1.6, 1.6), (4.85, 7.4)]
GS_RAMP_X = -4.4 - GS_PLAT_Y * 8.0
GS_WHEEL = (-4.6, GS_HAUL_Y, 0.0)
GS_BENTS = (-3.8, 4.2)


def ground_station(q):
    m = Mesh()
    py = GS_PLAT_Y
    from mk import card
    for z0, z1 in GS_PLATS:                                                     # platforms, yellow edge bands, ramps
        inner = [e for e in (z0, z1) if abs(e) < 7.0]
        za = z0 + (0.304 if z0 in inner else 0.0)
        zb = z1 - (0.304 if z1 in inner else 0.0)
        m.box((-4.4, 0.0, za), (4.4, py, zb), "concrete")
        for e in inner:
            lo, hi = (e - 0.3, e) if e == z1 else (e, e + 0.3)
            m.box((-4.4, 0.0, lo), (4.4, py, hi), "accent2")
        m.prism_xy([(-4.402, 0.0), (-4.402, py), (GS_RAMP_X, 0.0)], [], z0, z1, "concrete")
    for bx in GS_BENTS:                                                         # the two bents and their crossbeams
        for zc in (-7.25, 0.0, 7.25):
            m.box((bx - 0.15, py, zc - 0.15), (bx + 0.15, GS_TOP, zc + 0.15), "steel")
        m.box((bx - 0.15, GS_TOP, -7.42), (bx + 0.15, GS_TOP + 0.4, 7.42), "steel")
    m.box((-4.65, GS_TOP + 0.4, -7.6), (4.35, GS_TOP + 0.52, 7.6), "roof")        # the canopy roof
    if q:
        m.box((-4.67, GS_TOP + 0.3, -7.62), (4.37, GS_TOP + 0.4, -7.6), "accent")
        m.box((-4.67, GS_TOP + 0.3, 7.6), (4.37, GS_TOP + 0.4, 7.62), "accent")
    for zc in (-6.1, 0.0, 6.1):                                                 # platform lights under the roof
        m.box((-3.6, GS_TOP - 0.15, zc - 0.06), (3.6, GS_TOP - 0.08, zc + 0.06), "steel")
        m.box((-3.55, GS_TOP - 0.17, zc - 0.045), (3.55, GS_TOP - 0.15, zc + 0.045), "lamp")
        for x in (-3.0, 3.0):
            m.box((x - 0.012, GS_TOP - 0.08, zc - 0.012), (x + 0.012, GS_TOP + 0.4, zc + 0.012), "dark")
    m.box((-4.8, GS_TOP, -0.2), (GS_BENTS[0] - 0.15, GS_TOP + 0.3, 0.2), "steel")   # the bull wheel's bracket and shaft
    m.cyl(GS_WHEEL[0], 0.0, 0.12, GS_WHEEL[1] + 0.15, GS_TOP, "steel", n=6)
    for s in (-1, 1):
        zb = s * GS_BERTH_Z
        # the head frame (+x): two columns and a saddle shoe the track ropes ride over before they rise
        for dz in (-1.0, 1.0):
            m.box((5.45, 0.0, zb + dz - 0.15), (5.75, GS_ROPE_Y - 0.33, zb + dz + 0.15), "steel")
        m.box((5.44, GS_ROPE_Y - 0.33, zb - 1.17), (5.76, GS_ROPE_Y - 0.13, zb + 1.17), "steel")
        m.box((5.0, GS_ROPE_Y - 0.13, zb - 0.45), (6.2, GS_ROPE_Y - 0.032, zb + 0.45), "metal")
        # the rear deviation saddle (an A-frame at x -5.0) and the track-rope anchor block
        for dz in (-0.8, 0.8):
            m.box((-5.15, 0.0, zb + dz - 0.12), (-4.85, GS_ROPE_Y - 0.24, zb + dz + 0.12), "steel")
        m.box((-5.3, GS_ROPE_Y - 0.24, zb - 0.92), (-4.7, GS_ROPE_Y - 0.032, zb + 0.92), "metal")
        m.box((-11.5, 0.0, zb - 0.8), (-9.5, 1.2, zb + 0.8), "concrete")
        drum = Mesh()
        drum.cyl(0.0, 0.0, 0.35, -0.6, 0.6, "dark", n=8 if q else 6)
        m.add(drum, lambda p, zb=zb: (rot_x(90)(p)[0] - 10.2, rot_x(90)(p)[1] + 1.55, rot_x(90)(p)[2] + zb))
        m.box((-10.5, 1.2, zb - 0.7), (-9.9, 1.55, zb - 0.62), "dark")
        m.box((-10.5, 1.2, zb + 0.62), (-9.9, 1.55, zb + 0.7), "dark")
        for dz in (-ROPE_DZ, ROPE_DZ):                                         # the track ropes through the station
            sweep(m, [(-10.2, 1.9, zb + dz), (-5.0, GS_ROPE_Y, zb + dz), (6.2, GS_ROPE_Y, zb + dz)], 0.03, "steel", n=5)
        sweep(m, [(GS_WHEEL[0], GS_HAUL_Y, zb * 0.999), (6.2, GS_HAUL_Y, zb)], 0.023, "steel", n=4)    # the haul rope
        # platform railings along the berth edges, a gap at the cabin doors
        for ze in ((-1.6 + 0.08) if s < 0 else (1.6 - 0.08), (-4.85 - 0.08) if s < 0 else (4.85 + 0.08)):
            for xa, xb in ((-3.9, -0.85), (0.85, 3.9)):
                for x in (xa, xb):
                    m.box((x - 0.03, py, ze - 0.03), (x + 0.03, py + 1.1, ze + 0.03), "accent2")
                m.box((xa - 0.03, py + 1.1, ze - 0.035), (xb + 0.03, py + 1.16, ze + 0.035), "accent2")
                m.box((xa + 0.03, py + 0.55, ze - 0.015), (xb - 0.03, py + 0.59, ze + 0.015), "accent2")
            if q and abs(ze) < 2:
                card(m, "text", "txt_stand_clear", (-2.4, py + 0.83, ze + (0.05 if s > 0 else -0.05)), (-1, 0, 0) if s > 0 else (1, 0, 0), (0, 1, 0), 0.42, two=False)
    for z0, z1 in GS_PLATS:                                                     # the gates at the ramp heads
        for zp in (z0 + 0.15, z1 - 0.15):
            m.box((-4.35, py, zp - 0.06), (-4.23, py + 2.45, zp + 0.06), "steel")
        m.box((-4.36, py + 2.45, z0 + 0.09), (-4.22, py + 2.75, z1 - 0.09), "steel")
        cid = "txt_gondola" if z0 > -2 and z1 < 2 else "txt_tickets"
        card(m, "text", cid, (-4.38, py + 2.6 + 0.4, (z0 + z1) / 2), (0, 0, 1), (0, 1, 0), 0.75 if cid == "txt_gondola" else 0.5, two=False)
    # the operator's booth on side platform A
    m.box((1.4, py, -7.25), (3.6, py + 2.6, -5.5), "cream")
    m.box((1.3, py + 2.6, -7.35), (3.7, py + 2.75, -5.4), "accent")
    m.quad_facing((1.6, py + 1.0, -5.473), (3.4, py + 1.0, -5.473), (3.4, py + 2.2, -5.473), (1.6, py + 2.2, -5.473), (0, 0, 1), "glow")
    if q:
        card(m, "text", "txt_tickets", (2.5, py + 2.42, -5.47), (1, 0, 0), (0, 1, 0), 0.3, two=False)
    return m


def station_wheel(q):
    m = Mesh()
    n = 28 if q else 14
    ring_torus(m, (0.0, 0.0, 0.0), GS_BERTH_Z, 0.11, "dark", axis="y", n=n, k=5 if q else 4)
    m.cyl(0.0, 0.0, 0.4, -0.15, 0.15, "steel", n=8)
    for k in range(8 if q else 6):
        a = math.tau * k / (8 if q else 6)
        m.tube((0.4 * math.cos(a), 0.0, 0.4 * math.sin(a)), ((GS_BERTH_Z - 0.11) * math.cos(a), 0.0, (GS_BERTH_Z - 0.11) * math.sin(a)), 0.05, "steel", n=4)
    return m


def gs_frame():
    py = GS_PLAT_Y
    out = [B(-4.4, 0, z0, 4.4, py, z1) for z0, z1 in GS_PLATS]
    out += [B(bx - 0.15, py, zc - 0.15, bx + 0.15, GS_TOP, zc + 0.15) for bx in GS_BENTS for zc in (-7.25, 0.0, 7.25)]
    for s in (-1, 1):
        zb = s * GS_BERTH_Z
        out += [B(5.45, 0, zb + dz - 0.15, 5.75, GS_ROPE_Y - 0.33, zb + dz + 0.15) for dz in (-1.0, 1.0)]
        out += [B(-5.15, 0, zb + dz - 0.12, -4.85, GS_ROPE_Y - 0.24, zb + dz + 0.12) for dz in (-0.8, 0.8)]
        out.append(B(-11.5, 0, zb - 0.8, -9.5, 1.2, zb + 0.8))
        for ze in ((-1.6 + 0.08) if s < 0 else (1.6 - 0.08), (-4.85 - 0.08) if s < 0 else (4.85 + 0.08)):
            out += [B(xa - 0.035, py, ze - 0.035, xb + 0.035, py + 1.16, ze + 0.035) for xa, xb in ((-3.9, -0.85), (0.85, 3.9))]
    for z0, z1 in GS_PLATS:
        out += [B(-4.35, py, zp - 0.06, -4.23, py + 2.45, zp + 0.06) for zp in (z0 + 0.15, z1 - 0.15)]
    out.append(B(1.4, py, -7.25, 3.6, py + 2.75, -5.5))
    return out


piece("ground_station", "ropeway", ground_station, kind="station", foot=None, lod1="keep", frame=gs_frame(),
      ramps=[[[GS_RAMP_X, 0.0, z0], [-4.4, GS_PLAT_Y, z0], [-4.4, GS_PLAT_Y, z1], [GS_RAMP_X, 0.0, z1]] for z0, z1 in GS_PLATS],
      passes=[{"box": B(-4.5, GS_PLAT_Y, z0 + 0.22, -4.1, GS_PLAT_Y + 2.4, z1 - 0.22), "kind": "open"} for z0, z1 in GS_PLATS],
      walk=[[-4.0, -7.1, 1.3, -5.0, GS_PLAT_Y], [-4.0, -1.4, 4.0, 1.4, GS_PLAT_Y], [-4.0, 5.0, 4.0, 7.1, GS_PLAT_Y]],
      budget=6000, palette="ropeway",
      anchors={"berth_0": [0.0, GS_PLAT_Y, -GS_BERTH_Z, 0], "berth_1": [0.0, GS_PLAT_Y, GS_BERTH_Z, 0],
               "pivot_0": [0.0, GS_PIVOT_Y, -GS_BERTH_Z, 0], "pivot_1": [0.0, GS_PIVOT_Y, GS_BERTH_Z, 0],
               "rope_exit_0": [6.2, GS_ROPE_Y, -GS_BERTH_Z, 0], "rope_exit_1": [6.2, GS_ROPE_Y, GS_BERTH_Z, 0],
               "haul_exit_0": [6.2, GS_HAUL_Y, -GS_BERTH_Z, 0], "haul_exit_1": [6.2, GS_HAUL_Y, GS_BERTH_Z, 0],
               "bull_wheel": [GS_WHEEL[0], GS_WHEEL[1], GS_WHEEL[2], 0], "booth": [2.5, GS_PLAT_Y, -5.3, 0]},
      notes="the ground (bottom) station of an island's jig-back ropeway: two berths (cabins along x at berth_0/1, their "
            "floors level with three 0.45 m platforms), 1:8 ramps and gates at -x, a steel portal frame under a canopy roof, "
            "the head saddles at +x where the track ropes leave for the island (rope_exit_*: draw the span from there), the "
            "rear deviation saddles and rope anchor blocks, the bull wheel (ground_station_wheel at bull_wheel), the "
            "operator's booth, railings with a gap at each cabin door")
piece("ground_station_wheel", "ropeway", station_wheel, kind="station", foot=None, lod1="keep", collide="none", ground=False, budget=800,
      palette="ropeway", moving={"kind": "spin", "axis": [0, 1, 0], "pivot": [0, 0, 0], "with": "the haul rope (m/s = 8)"},
      notes="the station's horizontal bull wheel (r 3.25 m): the haul rope's return; spins with the haul rope")
