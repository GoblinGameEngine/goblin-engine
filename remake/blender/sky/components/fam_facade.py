"""Facade families: openings (every arch shape), lattices and grilles, oriels and bays, balconies and galleries,
eaves and brackets, parapets, relief bands.  Each family: fn(c) with c a Ctx (see __init__.py): c.g (G, the
component's frame), c.m (role -> material), c.w/c.h/c.d (size), c.v (variant), c.p (the id's params), c.sign /
c.glow / c.lights (anchors)."""
import math

from mathutils import Matrix

from .geo import arch_outline, grow

EPS = 0.004            # (proud of a surface: no coplanar faces)


# ------------------------------------------------------------------ openings
def opening(c):
    """A framed opening on a wall: shape rect|round|pointed|horseshoe|lobed|cusped|ogee|circle; fill glass|door|
    studded|stained|open|lattice|loading; a sill and a frame proud of the wall.  On a plain wall it reads as a
    window (the glass sits just proud); SC.panel cuts the wall's hole and recesses it."""
    g, m = c.g, c.m
    shape = c.p.get("shape", c.v if c.v in ("rect", "round", "pointed", "horseshoe", "lobed", "cusped", "ogee", "circle") else "rect")
    fill = c.p.get("fill", "glass")
    w, h = c.w, c.h
    fw = c.p.get("frame", 0.1)
    dp = c.p.get("frame_d", 0.07)
    recess = c.kw.get("recess", 0.0)               # (> 0: the wall has a hole, the fill sits that far back)
    n = 6
    if shape == "circle":
        inner = arch_outline("circle", w, h, n)
        outer = grow(inner, fw, radial=True)
    else:
        if c.p.get("sill", fill in ("glass", "stained", "lattice")):
            inner = arch_outline(shape, w, h, n)
            outer = [(x, z - fw) for x, z in arch_outline(shape, w + 2 * fw, h + 2 * fw, n)]     # (a rail under it too)
        else:
            # a door or a french window: no rail to trip on -- a 4 mm threshold band under the jambs
            inner = [(x, z + EPS if z < 1e-6 else z) for x, z in arch_outline(shape, w, h, n)]
            outer = arch_outline(shape, w + 2 * fw, h + fw, n)
    if fw > 0:
        g.ring_xz(outer, inner, EPS, dp, m("trim"))
    fy = EPS if recess <= 0 else -recess
    if fill in ("glass", "stained"):
        g.extrude_xz(inner, fy, fy + 0.012, m("glass") if fill == "glass" else m("glass"))
        if fill == "stained":
            # a fanlight's tracery: radial bars over the glass
            top = max(z for _, z in inner)
            for k in range(1, 6):
                t = math.pi * k / 6
                g.tube((0, fy + 0.02, top * 0.55), (0.45 * w * math.cos(t), fy + 0.02, top * 0.55 + 0.45 * h * math.sin(t)), 0.012, m("trim"), n=4)
        elif c.p.get("bars", True) and shape != "circle":
            # glazing bars: one upright, rails by height
            top = max(z for _, z in inner)
            g.box((-0.018, fy + 0.012, 0.0), (0.018, fy + 0.03, top - 0.02), m("trim"))
            k = max(1, int(h / 0.9))
            for i in range(1, k + 1):
                z = h * i / (k + 1) if shape == "rect" else min(h * i / (k + 1), top * 0.7)
                g.box((-w / 2 + 0.01, fy + 0.012, z - 0.018), (w / 2 - 0.01, fy + 0.03, z + 0.018), m("trim"))
    elif fill in ("door", "studded", "loading"):
        g.extrude_xz(inner, fy, fy + 0.05, m("dark_wood") if fill != "loading" else m("wood"))
        if fill == "studded":
            for iz in range(int(h / 0.35)):
                for ix in range(int(w / 0.3)):
                    x = -w / 2 + 0.15 + ix * 0.3
                    z = 0.2 + iz * 0.35
                    if z < h - 0.3:
                        g.box((x - 0.025, fy + 0.05, z - 0.025), (x + 0.025, fy + 0.075, z + 0.025), m("iron"))
        else:
            g.box((-w / 2 + 0.12, fy + 0.05, h * 0.25), (w / 2 - 0.12, fy + 0.07, h * 0.6), m("wood"))
        g.box((w * 0.3, fy + 0.05, 1.0), (w * 0.3 + 0.03, fy + 0.11, 1.08), m("metal"))        # (a handle)
    elif fill == "lattice":
        lat_rect(g, m, w, min(h, max(z for _, z in inner)) - 0.02, fy, c.p.get("pattern", "diag"))
    if c.p.get("sill", fill in ("glass", "stained", "lattice")) and shape != "circle":
        g.box((-w / 2 - fw - 0.04, EPS, -fw - 0.07), (w / 2 + fw + 0.04, dp + 0.06, -fw - 0.004), m("trim"))
    if c.p.get("lamp"):
        g.box((-0.08, EPS, h + fw + 0.12), (0.08, 0.22, h + fw + 0.3), m("lamp"))


def lat_rect(g, m, w, h, y, pattern="diag", pitch=0.14, frame=0.04, mat_role="dark_wood"):
    """a lattice in a w x h rectangle (bottom centre at z 0), front at y: a frame and a pattern of bars"""
    mt = m(mat_role)
    t = 0.035
    g.box((-w / 2, y, 0), (w / 2, y + t, frame), mt)
    g.box((-w / 2, y, h - frame), (w / 2, y + t, h), mt)
    g.box((-w / 2, y, frame), (-w / 2 + frame, y + t, h - frame), mt)
    g.box((w / 2 - frame, y, frame), (w / 2, y + t, h - frame), mt)
    x0, x1, z0, z1 = -w / 2 + frame, w / 2 - frame, frame, h - frame
    r = 0.011
    yy = y + t * 0.5
    if pattern in ("grid", "turned", "bars", "louvre"):
        if pattern != "louvre":
            nx = max(1, int((x1 - x0) / pitch))
            for i in range(1, nx):
                x = x0 + (x1 - x0) * i / nx
                g.tube((x, yy, z0), (x, yy, z1), r if pattern != "turned" else r * 1.6, mt, n=4)
        if pattern in ("grid", "turned", "louvre"):
            nz = max(1, int((z1 - z0) / (pitch if pattern != "louvre" else 0.09)))
            for i in range(1, nz):
                z = z0 + (z1 - z0) * i / nz
                if pattern == "louvre":
                    g.box((x0, yy - 0.02, z - 0.035), (x1, yy + 0.02, z), mt)
                else:
                    g.tube((x0, yy, z), (x1, yy, z), r if pattern != "turned" else r * 1.6, mt, n=4)
        if pattern == "turned":
            nx = max(1, int((x1 - x0) / pitch))
            nz = max(1, int((z1 - z0) / pitch))
            for i in range(1, nx):
                for j in range(1, nz):
                    g.box((x0 + (x1 - x0) * i / nx - 0.02, yy - 0.02, z0 + (z1 - z0) * j / nz - 0.02),
                          (x0 + (x1 - x0) * i / nx + 0.02, yy + 0.02, z0 + (z1 - z0) * j / nz + 0.02), mt)
        return
    # diagonals (diag) / a star-ish pattern (star: diagonals + a grid)
    W, H = x1 - x0, z1 - z0
    k = max(1, int((W + H) / pitch))
    for sgn in (1, -1):
        for i in range(1, k):
            d = (W + H) * i / k
            pts = _clip_diag(d, W, H, sgn)
            if pts:
                (ax, az), (bx, bz) = pts
                g.tube((x0 + ax, yy, z0 + az), (x0 + bx, yy, z0 + bz), r, mt, n=4)
    if pattern == "star":
        nx = max(1, int(W / (pitch * 2)))
        for i in range(1, nx):
            x = x0 + W * i / nx
            g.tube((x, yy, z0), (x, yy, z1), r, mt, n=4)


def _clip_diag(d, W, H, sgn):
    """the segment of the line x + sgn*z = d (sgn 1) / x - z = d - H (sgn -1) inside [0, W] x [0, H]"""
    pts = []
    if sgn > 0:                                  # x + z = d
        for x, z in ((d, 0), (d - H, H), (0, d), (W, d - W)):
            if -1e-6 <= x <= W + 1e-6 and -1e-6 <= z <= H + 1e-6:
                pts.append((min(max(x, 0), W), min(max(z, 0), H)))
    else:                                        # x - z = d - H
        e = d - H
        for x, z in ((e, 0), (e + H, H), (0, -e), (W, W - e)):
            if -1e-6 <= x <= W + 1e-6 and -1e-6 <= z <= H + 1e-6:
                pts.append((min(max(x, 0), W), min(max(z, 0), H)))
    pts = sorted(set((round(x, 5), round(z, 5)) for x, z in pts))
    if len(pts) < 2:
        return None
    return pts[0], pts[-1]


# ------------------------------------------------------------------ lattices, grilles, screens
def lattice(c):
    """a flat screen panel: pattern grid|diag|star|turned|bars|louvre; proud (on a wall) or projecting with a
    ledge (reja: a window grille standing off the wall on a pot ledge)"""
    g, m = c.g, c.m
    pattern = c.p.get("pattern", c.v or "diag")
    role = c.p.get("mat", "dark_wood")
    off = c.p.get("project", 0.0)
    if off > 0:
        lat_rect(g, m, c.w, c.h, off, pattern, mat_role=role, pitch=c.p.get("pitch", 0.12))
        # side cheeks and a pot ledge
        g.box((-c.w / 2, EPS, 0.0), (-c.w / 2 + 0.03, off + 0.035, c.h), m(role))
        g.box((c.w / 2 - 0.03, EPS, 0.0), (c.w / 2, off + 0.035, c.h), m(role))
        g.box((-c.w / 2, EPS, -0.05), (c.w / 2, off + 0.06, 0.0), m(role))
        if c.p.get("pots"):
            for i in range(3):
                x = -c.w / 3 + i * c.w / 3
                g.cyl(x, off * 0.5 + 0.02, 0.07, 0.0, 0.14, m("accent"), n=6, r1=0.09)
                g.cyl(x, off * 0.5 + 0.02, 0.1, 0.14, 0.3, m("plant"), n=5, r1=0.02)
    else:
        lat_rect(g, m, c.w, c.h, EPS, pattern, mat_role=role, pitch=c.p.get("pitch", 0.12))


# ------------------------------------------------------------------ oriels, bays, boxes
def oriel(c):
    """a closed projecting bay on brackets: box w x d x h, faces glass|lattice|panel|porthole; roof flat|chhatri|
    bangla|cornice|pent.  roshan: tall, lattice faces, a carved crown; jharokha: brackets, jali and a little dome."""
    g, m = c.g, c.m
    w, h, d = c.w, c.h, c.d
    face = c.p.get("face", "lattice")
    roof = c.p.get("roof", "flat")
    base = c.p.get("base", 0.25)
    role = c.p.get("mat", "wood")
    # floor slab and the brackets under it
    g.box((-w / 2, EPS, 0.0), (w / 2, d, base), m(role))
    nb = max(2, int(w / 0.7) + 1)
    for i in range(nb):
        x = -w / 2 + 0.08 + (w - 0.16) * i / (nb - 1)
        bracket(g.moved(x=x), m, 0.1, d * 0.85, 0.55, role)
    # corner posts and the faces
    pw = 0.07
    for x in (-w / 2, w / 2 - pw):
        g.box((x, d - pw, base), (x + pw, d, h), m(role))
    for x in (-w / 2, w / 2 - pw):
        g.box((x, EPS, base), (x + pw, pw, h), m(role))
    fz0, fz1 = base + 0.45, h - 0.15
    # a solid apron to the sill
    g.box((-w / 2 + pw, d - 0.05, base), (w / 2 - pw, d - EPS, fz0), m(role))
    g.box((-w / 2, pw, base), (-w / 2 + 0.05, d - pw, fz0), m(role))
    g.box((w / 2 - 0.05, pw, base), (w / 2, d - pw, fz0), m(role))
    if face in ("lattice", "jali"):
        front = g.sub(Matrix.Translation((0, d - 0.05, fz0)))
        lat_rect(front, m, w - 2 * pw, fz1 - fz0, 0.0, "diag" if face == "lattice" else "star", mat_role="dark_wood" if face == "lattice" else "stone")
        for sx in (-1, 1):
            side = g.sub(Matrix.Translation((sx * (w / 2 - 0.025), d / 2, fz0)) @ Matrix.Rotation(sx * math.pi / 2, 4, "Z"))
            lat_rect(side, m, d - 2 * pw, fz1 - fz0, -0.017, "diag" if face == "lattice" else "star", mat_role="dark_wood" if face == "lattice" else "stone")
        g.box((-w / 2 + pw, pw, fz0), (w / 2 - pw, d - 0.1, fz1), m("glass"))       # (glazed behind the screen)
    elif face == "porthole":
        g.box((-w / 2 + pw, d - 0.05, fz0), (w / 2 - pw, d - EPS, fz1), m(role))
        r = min(w, fz1 - fz0) * 0.32
        g.sub(Matrix.Translation((0, d - EPS, (fz0 + fz1) / 2)) @ Matrix.Rotation(-math.pi / 2, 4, "X")).cyl(0, 0, r, 0.0, 0.03, m("glass"), n=12)
        g.box((-w / 2, pw, fz0), (-w / 2 + 0.05, d - pw, fz1), m(role))
        g.box((w / 2 - 0.05, pw, fz0), (w / 2, d - pw, fz1), m(role))
    elif face == "panel":
        g.box((-w / 2 + pw, d - 0.05, fz0), (w / 2 - pw, d - EPS, fz1), m(role))
        g.box((-w / 2, pw, fz0), (-w / 2 + 0.05, d - pw, fz1), m(role))
        g.box((w / 2 - 0.05, pw, fz0), (w / 2, d - pw, fz1), m(role))
    else:                                         # glass: a glazed bay with mullions
        g.box((-w / 2 + pw, d - 0.045, fz0), (w / 2 - pw, d - 0.03, fz1), m("glass"))
        nm = max(1, int(w / 0.6))
        for i in range(1, nm):
            x = -w / 2 + w * i / nm
            g.box((x - 0.025, d - 0.05, fz0), (x + 0.025, d - EPS, fz1), m("trim"))
        g.box((-w / 2, pw, fz0), (-w / 2 + 0.03, d - pw, fz1), m("glass"))
        g.box((w / 2 - 0.03, pw, fz0), (w / 2, d - pw, fz1), m("glass"))
    g.box((-w / 2, EPS, fz1), (w / 2, d, h), m(role))                                  # (head)
    # roof
    if roof == "chhatri":
        g.box((-w / 2 - 0.1, EPS, h), (w / 2 + 0.1, d + 0.1, h + 0.08), m("stone"))
        g.sub(Matrix.Translation((0, d / 2, h + 0.08))).lathe(_dome_prof(min(w, d) * 0.42, min(w, d) * 0.5, "onion"), m("trim"), n=10)
    elif roof == "bangla":
        prof = [(-w / 2 - 0.15, 0.0), (w / 2 + 0.15, 0.0)] + [((w / 2 + 0.15) * math.cos(math.pi * k / 8), 0.12 + 0.35 * math.sin(math.pi * k / 8)) for k in range(9)]
        g.sub(Matrix.Translation((0, 0, h))).extrude_xz(prof[:2] + prof[2:], EPS, d + 0.15, m("roof"))
    elif roof == "cornice":
        g.box((-w / 2 - 0.12, EPS, h), (w / 2 + 0.12, d + 0.12, h + 0.12), m("trim"))
        g.box((-w / 2 - 0.06, EPS, h + 0.12), (w / 2 + 0.06, d + 0.06, h + 0.22), m("trim"))
        if c.p.get("crown"):
            for i in range(int(w / 0.25)):
                x = -w / 2 + 0.12 + i * 0.25
                g.box((x - 0.05, d - 0.05, h + 0.22), (x + 0.05, d + 0.05, h + 0.42), m("trim"))
    elif roof == "pent":
        g.extrude_xz([(-w / 2 - 0.15, 0.0), (w / 2 + 0.15, 0.0), (w / 2 + 0.15, 0.06), (-w / 2 - 0.15, 0.06)], EPS, d + 0.2, m("roof"))
    else:
        g.box((-w / 2 - 0.05, EPS, h), (w / 2 + 0.05, d + 0.05, h + 0.1), m(role))


def bracket(g, m, t, d, h, role="wood", curve=True):
    """a bracket under a projection: from the wall (y 0) out to d, h tall, hanging under z 0 (its top at 0)"""
    if curve:
        pts = [(0.0, -h), (0.0, 0.0), (d, 0.0), (d, -0.08)] + [(d * (1 - math.sin(math.pi / 2 * k / 5)), -0.08 - (h - 0.08) * (1 - math.cos(math.pi / 2 * k / 5))) for k in range(1, 5)]
    else:
        pts = [(0.0, -h), (0.0, 0.0), (d, 0.0), (d, -0.08), (0.06, -h)]
    # profile in the y-z plane: extrude along x
    sub = g.sub(Matrix.Rotation(math.pi / 2, 4, "Z"))           # (local x -> y)
    sub.extrude_xz(pts[::-1], -t / 2, t / 2, m(role))          # (pts run clockwise: reversed, counter-clockwise)


def _dome_prof(r, h, kind="hemi", n=7):
    if kind == "onion":
        prof = [(r * 0.75, 0.0), (r * 1.02, h * 0.25), (r * 0.95, h * 0.45), (r * 0.62, h * 0.65), (r * 0.25, h * 0.85), (r * 0.06, h * 0.98), (0.0, h * 1.1)]
    elif kind == "pointed":
        prof = [(r * math.cos(0.5 * math.pi * k / n) ** 0.8, h * math.sin(0.5 * math.pi * k / n) ** 1.3) for k in range(n)] + [(0.0, h * 1.05)]
    elif kind == "saucer":
        prof = [(r, 0.0), (r * 0.8, h * 0.6), (r * 0.4, h * 0.9), (0.0, h)]
    else:
        prof = [(r * math.cos(0.5 * math.pi * k / n), h * math.sin(0.5 * math.pi * k / n)) for k in range(n)] + [(0.0, h)]
    return prof


# ------------------------------------------------------------------ balconies, galleries, verandahs
def balcony(c):
    """a slab and its rail.  rail bars|solid|iron|cage|timber|glass|none; roof none|posts (a covered timber
    gallery)|pent; plan rect|curved; brackets yes/no; posts down to the ground (verandah)"""
    g, m = c.g, c.m
    w, d = c.w, c.d
    rail = c.p.get("rail", "bars")
    plan = c.p.get("plan", "rect")
    slab_t = c.p.get("slab", 0.14)
    role = c.p.get("mat", "concrete")
    rh = c.p.get("rail_h", 1.05)
    if plan == "curved":
        poly = [(w / 2 * math.cos(math.pi * k / 10), EPS + d * math.sin(math.pi * k / 10)) for k in range(11)]
        g.extrude_xy(poly, -slab_t, 0.0, m(role))
        edge = poly
    else:
        g.box((-w / 2, EPS, -slab_t), (w / 2, d, 0.0), m(role))
        edge = [(w / 2, EPS), (w / 2, d), (-w / 2, d), (-w / 2, EPS)]
    if c.p.get("brackets"):
        for x in (-w / 2 + 0.2, w / 2 - 0.2) if w < 2.5 else [(-w / 2 + 0.2) + (w - 0.4) * i / 3 for i in range(4)]:
            bracket(g.moved(x=x, z=-slab_t), m, 0.1, d * 0.8, 0.45, c.p.get("bracket_mat", "wood"))
    rm = m({"iron": "iron", "cage": "iron", "timber": "wood", "glass": "glass", "solid": role}.get(rail, "metal"))
    if rail == "solid":
        for (ax, ay), (bx, by) in zip(edge, edge[1:]):
            _wall_seg(g, (ax, ay), (bx, by), 0.0, rh, 0.1, m(role))
    elif rail != "none":
        for (ax, ay), (bx, by) in zip(edge, edge[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < 0.05:
                continue
            g.tube((ax, ay, rh), (bx, by, rh), 0.025, rm, n=4)
            g.tube((ax, ay, 0.12), (bx, by, 0.12), 0.015, rm, n=4)
            k = max(1, int(L / (0.11 if rail in ("bars", "cage", "iron") else 0.5)))
            for i in range(k + 1):
                t = i / k
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                if rail == "iron" and i % 2 == 1:
                    g.tube((x, y, 0.12), (x, y, rh * 0.55), 0.008, rm, n=4)
                    g.tube((x, y, rh * 0.55), (x + (bx - ax) / L * 0.04, y + (by - ay) / L * 0.04, rh * 0.75), 0.008, rm, n=4)
                    continue
                g.tube((x, y, 0.0), (x, y, rh), 0.012 if rail != "timber" else 0.035, rm, n=4)
            if rail == "glass":
                _wall_seg(g, (ax, ay), (bx, by), 0.12, rh - 0.05, 0.02, m("glass"))
    if rail == "cage":
        top = c.p.get("cage_h", 2.4)
        for x in [(-w / 2) + w * i / max(1, int(w / 0.12)) for i in range(int(w / 0.12) + 1)]:
            g.tube((x, d, rh), (x, d, top), 0.01, rm, n=4)
        for y in [EPS + (d - EPS) * i / max(1, int(d / 0.12)) for i in range(int(d / 0.12) + 1)]:
            for x in (-w / 2, w / 2):
                g.tube((x, y, rh), (x, y, top), 0.01, rm, n=4)
        g.box((-w / 2, EPS, top), (w / 2, d, top + 0.04), m("metal"))
    roof = c.p.get("roof", "none")
    if roof in ("posts", "pent"):
        top = c.p.get("roof_h", 2.6)
        if roof == "posts":
            for x in [(-w / 2 + 0.06) + (w - 0.12) * i / max(1, int(w / 1.5)) for i in range(int(w / 1.5) + 1)]:
                g.lathe([(0.06, 0.0), (0.06, 0.15), (0.045, 0.3), (0.05, top * 0.5), (0.04, top - 0.2), (0.06, top - 0.1), (0.06, top)], m("wood"), n=6, cx=x, cy=d - 0.07)
        g.sub(Matrix.Translation((0, 0, top))).extrude_xz([(-w / 2 - 0.1, 0.0), (w / 2 + 0.1, 0.0), (w / 2 + 0.1, 0.07), (-w / 2 - 0.1, 0.07)], EPS, d + 0.2, m("roof"))
    if c.p.get("ground_posts"):
        for x in (-w / 2 + 0.1, w / 2 - 0.1):
            g.cyl(x, d - 0.1, 0.07, -c.p["ground_posts"], -slab_t, m("wood"), n=6)
    if c.p.get("fairy"):
        c.lights((-w / 2, d, rh + 0.02), (w / 2, d, rh + 0.02))


def _wall_seg(g, a, b, z0, z1, t, mat):
    ax, ay = a
    bx, by = b
    L = math.hypot(bx - ax, by - ay)
    if L < 1e-4:
        return
    ang = math.atan2(by - ay, bx - ax)
    g.sub(Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(ang, 4, "Z")).box((0, -t / 2, z0), (L, t / 2, z1), mat)


# ------------------------------------------------------------------ eaves, awnings, brackets, cornices
def eave(c):
    """a projecting eave along a wall: kind slab (chhajja) | tile (barrel ribs) | green_tile | timber (deep, on
    brackets) | fretwork (a valance) | eyebrow (a thin shade) | cornice | stack (a pagoda ring storey) | crest"""
    g, m = c.g, c.m
    w, d = c.w, c.d
    kind = c.p.get("kind", c.v or "slab")
    slope = c.p.get("slope", 0.25)
    t = 0.06
    if kind in ("slab", "tile", "green_tile", "timber", "stack"):
        role = {"slab": "stone", "tile": "roof", "green_tile": "tile", "timber": "wood", "stack": "roof"}[kind]
        prof = [(0.0, 0.0), (d, -d * slope), (d, -d * slope + t), (0.0, t)]
        sub = g.sub(Matrix.Rotation(math.pi / 2, 4, "Z"))
        sub.extrude_xz(prof, -w / 2, w / 2, m(role))
        if kind in ("tile", "green_tile", "stack"):
            k = int(w / 0.22)
            for i in range(k):
                x = -w / 2 + 0.11 + i * 0.22
                g.tube((x, 0.0, t + 0.035), (x, d, -d * slope + t + 0.035), 0.045, m(role), n=5)
        if kind in ("slab", "timber", "stack"):
            nb = max(2, int(w / 1.0) + 1)
            for i in range(nb):
                x = -w / 2 + 0.1 + (w - 0.2) * i / (nb - 1)
                bracket(g.moved(x=x), m, 0.09, d * 0.7, 0.4 if kind != "timber" else 0.6, "wood" if kind != "slab" else "stone", curve=kind != "slab")
        if kind == "stack":
            c.glow("eave", (-w / 2, d + 0.01, -d * slope - 0.02), w)
            g.box((-w / 2, d - 0.05, -d * slope - 0.12), (w / 2, d + 0.02, -d * slope + 0.02), m("accent"))
    elif kind == "fretwork":
        g.box((-w / 2, EPS, -0.05), (w / 2, d, 0.0), m("wood"))
        k = int(w / 0.18)
        for i in range(k):
            x = -w / 2 + 0.09 + i * 0.18
            g.box((x - 0.035, d - 0.03, -c.h + 0.05 * (i % 2)), (x + 0.035, d, -0.05), m("wood"))
        g.box((-w / 2, d - 0.03, -c.h - 0.04), (w / 2, d, -c.h + 0.0), m("wood"))
    elif kind == "eyebrow":
        g.box((-w / 2, EPS, -0.05), (w / 2, d, 0.0), m("trim"))
    elif kind == "cornice":
        steps = [(0.0, 0.0, 0.12), (0.1, 0.12, 0.22), (0.2, 0.22, 0.3), (d, 0.3, 0.38)]
        for dd, z0, z1 in steps:
            g.box((-w / 2, EPS, z0), (w / 2, max(dd, 0.05) + EPS, z1), m("trim"))
        if c.p.get("brackets"):
            for i in range(int(w / 0.6)):
                x = -w / 2 + 0.3 + i * 0.6
                bracket(g.moved(x=x, z=0.3), m, 0.08, d * 0.9, 0.3, "trim")
    elif kind == "crest":
        hump = c.h
        prof = [(-w / 2, 0.0), (w / 2, 0.0)] + [(w / 2 - w * k / 12, 0.15 + hump * abs(math.sin(math.pi * 3 * k / 12)) * (0.6 + 0.4 * math.sin(math.pi * k / 12))) for k in range(13)]
        g.extrude_xz(prof, EPS, d, m("roof"))


def awning(c):
    """a fabric awning: kind straight|scalloped|tarp|shed (a boardwalk shed on posts); stripes in two fabrics"""
    g, m = c.g, c.m
    w, d = c.w, c.d
    kind = c.p.get("kind", c.v or "straight")
    drop = c.p.get("drop", 0.6)
    if kind == "shed":
        top = c.h
        g.sub(Matrix.Translation((0, 0, top))).extrude_xz([(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.06), (-w / 2, 0.06)], EPS, d, m("roof"))
        for x in [(-w / 2 + 0.1) + (w - 0.2) * i / max(1, int(w / 2.5)) for i in range(int(w / 2.5) + 1)]:
            g.cyl(x, d - 0.1, 0.07, 0.035, top, m("wood"), n=6)
        g.box((-w / 2, EPS, 0.035), (w / 2, d, 0.08), m("wood"))
        return
    k = max(1, int(w / 0.5))
    for i in range(k):
        x0 = -w / 2 + w * i / k
        x1 = -w / 2 + w * (i + 1) / k
        mat = m("fabric" if i % 2 == 0 else "fabric2" if kind != "tarp" else "fabric")
        g.face([(x0, EPS, 0.0), (x1, EPS, 0.0), (x1, d, -drop), (x0, d, -drop)], mat)
        g.face([(x0, d, -drop), (x1, d, -drop), (x1, EPS, 0.0), (x0, EPS, 0.0)], mat)
        # valance
        vz = -drop - (0.22 if kind == "straight" else 0.0)
        if kind == "scalloped":
            g.face([(x0, d, -drop), (x1, d, -drop), ((x0 + x1) / 2, d, -drop - 0.22)], mat)
            g.face([((x0 + x1) / 2, d, -drop - 0.22), (x1, d, -drop), (x0, d, -drop)], mat)
        elif kind == "straight":
            g.face([(x0, d, vz), (x1, d, vz), (x1, d, -drop), (x0, d, -drop)], mat)
            g.face([(x0, d, -drop), (x1, d, -drop), (x1, d, vz), (x0, d, vz)], mat)
    for x in (-w / 2, w / 2):
        g.tube((x, EPS, 0.0), (x, d, -drop), 0.012, m("iron"), n=4)


def bracket_fam(c):
    """a lone bracket / corbel / beam end / cantilever beam / hoist beam (with its hook)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "corbel")
    if kind == "corbel":
        for i in range(3):
            g.box((-c.w / 2 + 0.03 * i, EPS, -c.h + 0.15 * i), (c.w / 2 - 0.03 * i, c.d - 0.08 * (2 - i), -c.h + 0.15 * (i + 1)), m(c.p.get("mat", "stone")))
    elif kind == "beam_end":
        g.box((-c.w / 2, EPS, -c.h), (c.w / 2, c.d, 0.0), m("wood"))
    elif kind == "cantilever":
        g.box((-c.w / 2, EPS, -c.h), (c.w / 2, c.d, 0.0), m("dark_wood"))
        bracket(g.moved(z=-c.h), m, c.w * 0.8, c.d * 0.6, 1.2, "dark_wood", curve=False)
    elif kind == "hoist":
        g.box((-c.w / 2, EPS, -c.h), (c.w / 2, c.d, 0.0), m("dark_wood"))
        g.tube((0, c.d - 0.1, -c.h), (0, c.d - 0.1, -c.h - 0.5), 0.01, m("rope"), n=4)
        g.box((-0.04, c.d - 0.14, -c.h - 0.62), (0.04, c.d - 0.06, -c.h - 0.5), m("iron"))
    elif kind == "post":
        g.lathe([(0.07, 0.0), (0.07, 0.12), (0.05, 0.25), (0.06, 0.6), (0.045, c.h - 0.4), (0.065, c.h - 0.25), (0.05, c.h - 0.12), (0.07, c.h)], m("wood"), n=8)


# ------------------------------------------------------------------ parapets
def parapet(c):
    """a parapet run along a roof edge: crenel (square/stepped/triangle merlons) | rounded (a soft wavy clay top)
    | screen (timber lattice) | jali (pierced stone) | rail (a roof terrace rail with planters) | plain"""
    g, m = c.g, c.m
    w, h = c.w, c.h
    t = c.p.get("t", 0.25)
    kind = c.p.get("kind", c.v or "crenel")
    base = h * (0.55 if kind == "crenel" else 1.0 if kind in ("plain", "rounded") else 0.3)
    role = c.p.get("mat", "wall")
    if kind == "rounded":
        n = max(4, int(w / 0.5))
        prof = [(-w / 2, 0.0), (w / 2, 0.0)] + [(w / 2 - w * k / n, h * (0.8 + 0.2 * math.sin(k * 2.3) * math.sin(k * 0.7))) for k in range(n + 1)]
        g.extrude_xz(prof, -t, 0.0, m(role))
        return
    g.box((-w / 2, -t, 0.0), (w / 2, 0.0, base), m(role))
    if kind == "crenel":
        style = c.p.get("merlon", "square")
        mw = c.p.get("merlon_w", 0.5)
        k = max(1, int(w / (mw * 2)))
        for i in range(k):
            x = -w / 2 + (i + 0.5) * w / k
            if style == "stepped":
                g.box((x - mw / 2, -t, base), (x + mw / 2, 0.0, base + (h - base) * 0.5), m(role))
                g.box((x - mw / 4, -t, base + (h - base) * 0.5), (x + mw / 4, 0.0, h), m(role))
            elif style == "triangle":
                g.extrude_xz([(x - mw / 2, base), (x + mw / 2, base), (x, h)], -t, 0.0, m(role))
            else:
                g.box((x - mw / 2, -t, base), (x + mw / 2, 0.0, h), m(role))
    elif kind in ("screen", "jali"):
        lat_rect(g.moved(z=base), m, w, h - base, -t / 2 - 0.017, "diag" if kind == "screen" else "star", mat_role="dark_wood" if kind == "screen" else role)
        g.box((-w / 2, -t, h - 0.06), (w / 2, 0.0, h), m(role if kind == "jali" else "wood"))
    elif kind == "rail":
        for x in [(-w / 2) + w * i / max(1, int(w / 1.2)) for i in range(int(w / 1.2) + 1)]:
            g.tube((x, -t / 2, base), (x, -t / 2, h), 0.02, m("iron"), n=4)
        g.tube((-w / 2, -t / 2, h), (w / 2, -t / 2, h), 0.025, m("iron"), n=4)
        if c.p.get("planters"):
            g.box((-w / 2 + 0.1, -t - 0.3, base), (w / 2 - 0.1, -t, base + 0.35), m("wood"))
            g.box((-w / 2 + 0.15, -t - 0.27, base + 0.35), (w / 2 - 0.15, -t - 0.03, base + 0.42), m("plant"))
    if c.p.get("led"):
        c.glow("led", (-w / 2, EPS, h - 0.05), w)


# ------------------------------------------------------------------ relief bands and panels (shallow, on a wall)
def band(c):
    """a shallow band or panel on a wall (proud by EPS..depth): plain | ablaq (alternating blocks) | brick
    (raised brick lozenges) | inlay (a row of glazed tiles) | tiles (a checker panel) | stucco (diamond relief) |
    motif (a painted triangle chain) | dado | wave | chevron | sunburst | timber | clapboard | corrugated |
    geometric (stepped crosses) | mirror | mural (blocks of colour) | merchant (a painted mark)"""
    g, m = c.g, c.m
    w, h = c.w, c.h
    kind = c.p.get("kind", c.v or "plain")
    dp = c.p.get("depth", 0.025)
    a, b = m(c.p.get("a", "trim")), m(c.p.get("b", "accent"))
    if kind == "plain":
        g.box((-w / 2, EPS, 0.0), (w / 2, dp, h), a)
    elif kind == "ablaq":
        k = max(2, int(w / 0.45))
        for i in range(k):
            x0 = -w / 2 + w * i / k
            g.box((x0, EPS, 0.0), (x0 + w / k - 0.004, dp, h), a if i % 2 == 0 else b)
    elif kind in ("tiles", "inlay"):
        s = c.p.get("tile", 0.15 if kind == "tiles" else h)
        kx, kz = max(1, int(w / s)), max(1, int(h / s))
        g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.006, h), m(c.p.get("ground", "tile2")))
        for i in range(kx):
            for j in range(kz):
                if (i + j) % 2 == 0:
                    x0, z0 = -w / 2 + i * w / kx, j * h / kz
                    g.box((x0 + 0.008, EPS + 0.006, z0 + 0.008), (x0 + w / kx - 0.008, dp, z0 + h / kz - 0.008), b if (i // 2 + j) % 2 == 0 else a)
    elif kind in ("brick", "stucco"):
        g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.006, h), a)
        s = 0.25
        for i in range(int(w / s)):
            for j in range(int(h / s)):
                x, z = -w / 2 + (i + 0.5) * w / int(w / s), (j + 0.5) * h / int(h / s)
                if (i + j) % 2 == 0:
                    g.extrude_xz([(x, z - s * 0.4), (x + s * 0.4, z), (x, z + s * 0.4), (x - s * 0.4, z)], EPS + 0.006, dp, b if kind == "brick" else a)
    elif kind == "motif":
        k = max(2, int(w / 0.3))
        for i in range(k):
            x = -w / 2 + (i + 0.5) * w / k
            g.extrude_xz([(x - 0.12, 0.0), (x + 0.12, 0.0), (x, h)], EPS, EPS + 0.008, b)
    elif kind == "dado":
        g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.006, h), b)
        g.box((-w / 2, EPS, h - 0.06), (w / 2, dp, h), a)
    elif kind == "wave":
        n = max(6, int(w / 0.25))
        top = [(w / 2 - w * k / n, h * (0.6 + 0.4 * math.sin(k * math.pi / 3))) for k in range(n + 1)]
        bot = [(-w / 2 + w * k / n, h * 0.4 * (0.5 + 0.5 * math.sin(k * math.pi / 3 + 1.0))) for k in range(n + 1)]
        g.extrude_xz(bot + top, EPS, dp, a)
    elif kind == "chevron":
        k = max(2, int(w / 0.4))
        for i in range(k):
            x = -w / 2 + i * w / k
            g.extrude_xz([(x, 0.0), (x + w / k / 2, h * 0.5), (x + w / k, 0.0), (x + w / k, h * 0.3), (x + w / k / 2, h * 0.8), (x, h * 0.3)], EPS, dp, a if i % 2 == 0 else b)
    elif kind == "sunburst":
        g.extrude_xz([(-w / 2, 0.0), (w / 2, 0.0)] + [(w / 2 * math.cos(math.pi * k / 10), h * math.sin(math.pi * k / 10)) for k in range(11)], EPS, EPS + 0.01, a)
        for k in range(1, 10, 2):
            t = math.pi * k / 10
            g.extrude_xz([(0.0, 0.0), (w / 2 * math.cos(t - 0.06), h * math.sin(t - 0.06)), (w / 2 * math.cos(t + 0.06), h * math.sin(t + 0.06))], EPS + 0.01, dp, b)
    elif kind == "timber":
        g.box((-w / 2, EPS, 0.0), (w / 2, dp + 0.02, h), m("dark_wood"))
    elif kind in ("clapboard", "corrugated"):
        step = 0.2 if kind == "clapboard" else 0.08
        for j in range(int(h / step)):
            z0 = j * step
            if kind == "clapboard":
                g.sub(Matrix.Rotation(-0.06, 4, "X")).box((-w / 2, EPS, z0), (w / 2, EPS + 0.02, z0 + step + 0.02), a)
        if kind == "corrugated":
            g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.005, h), m(c.p.get("a", "metal")))
            for i in range(int(w / 0.076)):
                x = -w / 2 + 0.038 + i * 0.076
                g.tube((x, EPS + 0.005, 0.0), (x, EPS + 0.005, h), 0.016, m(c.p.get("a", "metal")), n=4)
    elif kind == "geometric":
        g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.006, h), a)
        s = min(w, h) / 3
        for (cx, cz, col) in ((0.0, h / 2, b), (-w / 3, h / 4, m("accent2")), (w / 3, h * 0.75, m("fabric2"))):
            for dx, dz, ww, hh in ((0, 0, s, s / 3), (0, 0, s / 3, s)):
                g.box((cx - ww / 2, EPS + 0.006, cz - hh / 2), (cx + ww / 2, dp, cz + hh / 2), col)
    elif kind == "mirror":
        g.box((-w / 2, EPS, 0.0), (w / 2, dp, h), m("mirror"))
        g.box((-w / 2, dp, h / 2 - 0.02), (w / 2, dp + 0.01, h / 2 + 0.02), m("metal"))
    elif kind in ("mural", "merchant"):
        g.box((-w / 2, EPS, 0.0), (w / 2, EPS + 0.006, h), a)
        cols = [m("accent"), m("accent2"), m("fabric"), m("fabric2"), m("tile")]
        k = 5 if kind == "mural" else 2
        for i in range(k):
            x0 = -w / 2 + w * (0.1 + 0.8 * ((i * 0.37) % 1.0))
            z0 = h * (0.1 + 0.7 * ((i * 0.61) % 1.0))
            g.extrude_xz([(x0, z0), (x0 + w * 0.25, z0 + h * 0.05), (x0 + w * 0.18, z0 + h * 0.3), (x0 - w * 0.02, z0 + h * 0.22)], EPS + 0.006, EPS + 0.012, cols[i % len(cols)])
