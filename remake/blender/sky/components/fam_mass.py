"""Massing and roofscape families: domes and pavilions, towers and minarets, gables and small roofs, stairs and
ladders, bridges and passages, roof clutter, columns and piers, cells and modules, courts and planters."""
import math

from mathutils import Matrix

from .fam_facade import EPS, _dome_prof, bracket, lat_rect
from .geo import arch_outline


# ------------------------------------------------------------------ domes and pavilions
def dome(c):
    """a dome on a drum: kind hemi | onion | ribbed | pointed | skylight (glazed) | saucer (a thin round canopy on a
    post); finial; drum height"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "hemi")
    r = c.w / 2
    drum = c.p.get("drum", 0.3 * c.h if kind != "saucer" else 0.0)
    role = c.p.get("mat", "trim" if kind != "skylight" else "glass")
    if kind == "saucer":
        g.cyl(0, 0, 0.2, 0.0, c.h - 0.25, m("concrete"), n=8)
        g.lathe([(0.25, c.h - 0.25), (r, c.h - 0.08), (r, c.h), (0.0, c.h + 0.05)], m("trim"), n=16)
        c.glow("ring", (-r, 0.0, c.h - 0.08), 2 * r)
        return
    if drum > 0:
        g.cyl(0, 0, r * 0.96, 0.0, drum, m(c.p.get("drum_mat", "wall")), n=14)
        g.cyl(0, 0, r * 1.02, drum - 0.08, drum + 0.012, m("trim"), n=14)       # (proud of the drum's top: no shared plane)
    dh = c.h - drum
    sub = g.moved(z=drum)
    sub.lathe(_dome_prof(r * 0.96, dh * 0.82, {"ribbed": "hemi", "skylight": "hemi"}.get(kind, kind)), m(role), n=14 if kind != "onion" else 12)
    if kind == "ribbed":
        for k in range(8):
            a = math.tau * k / 8
            pts = _dome_prof(r * 0.99, dh * 0.84, "hemi")
            for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
                sub.tube((r0 * math.cos(a), r0 * math.sin(a), z0), (r1 * math.cos(a), r1 * math.sin(a), z1), 0.04 * r, m("accent"), n=4)
    if c.p.get("finial", kind != "skylight"):
        top = dh * 0.82 * (1.1 if kind == "onion" else 1.0)
        sub.lathe([(0.06, top - 0.02), (0.1, top + 0.12), (0.04, top + 0.3), (0.07, top + 0.42), (0.0, top + 0.62)], m("metal"), n=6)


def chhatri(c):
    """an umbrella pavilion: a platform, 4-8 columns, a chhajja ring and a dome (a stair head or a lark perch)"""
    g, m = c.g, c.m
    r = c.w / 2
    ncol = c.p.get("cols", 4)
    ch = c.h * 0.55
    g.cbox(0, 0, 0.0, c.w, c.w, 0.2, m("stone"))
    for k in range(ncol):
        a = math.tau * (k + 0.5) / ncol
        x, y = r * 0.78 * math.cos(a), r * 0.78 * math.sin(a)
        g.lathe([(0.12, 0.2), (0.1, 0.35), (0.09, ch - 0.15), (0.13, ch)], m("stone"), n=8, cx=x, cy=y)
    g.cbox(0, 0, ch, c.w + 0.5, c.w + 0.5, 0.12, m("trim"))
    g.moved(z=ch + 0.12).lathe(_dome_prof(r * 0.85, c.h - ch - 0.12, c.p.get("dome", "onion")), m("trim"), n=12)
    if c.p.get("glow", True):
        c.glow("outline", (-r - 0.25, -r - 0.25, ch + 0.06), c.w + 0.5)


# ------------------------------------------------------------------ towers
def tower(c):
    """a tower: kind minaret (slender round, balconies, cap) | pyramid (tapered square: a sign/watch tower) | round
    (crenellated drum) | square (ornamented, a pyramid cap) | tapered (a lean corner tower) | belfry (an open bell
    stage) | clock (clock faces) | menzeh (a little roof belvedere) | turnpike (a round stair tower, conical roof) |
    ziggurat (a stepped crown)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "minaret")
    w, h = c.w, c.h
    role = c.p.get("mat", "wall")
    if kind == "minaret":
        r = w / 2
        g.cyl(0, 0, r, 0.0, h * 0.82, m(role), n=12, r1=r * 0.85)
        for f in (0.45, 0.78):
            z = h * f
            g.cyl(0, 0, r * 1.45, z - 0.12, z, m("trim"), n=12)
            for k in range(12):
                a = math.tau * k / 12
                g.tube((r * 1.4 * math.cos(a), r * 1.4 * math.sin(a), z), (r * 1.4 * math.cos(a), r * 1.4 * math.sin(a), z + 0.9), 0.025, m("iron"), n=4)
            g.cyl(0, 0, r * 1.42, z + 0.88, z + 0.92, m("iron"), n=12, caps=True)
            c.glow("ring", (-r * 1.45, 0.0, z + 0.95), r * 2.9)
        g.moved(z=h * 0.82).lathe(_dome_prof(r * 0.9, h * 0.18, c.p.get("cap", "pointed")), m("trim"), n=10)
        c.sign("blade", 0.8, 3.0, (0.0, r + 0.1, h * 0.55))
    elif kind == "pyramid":
        b0, b1 = w / 2, w * 0.32
        g.extrude_xy([(-b0, -b0), (b0, -b0), (b0, b0), (-b0, b0)], 0.0, 0.01, m(role))
        _frustum(g, b0, b1, 0.0, h * 0.92, m(role))
        _frustum(g, b1 * 1.15, b1 * 1.15, h * 0.92, h, m("trim"))
        c.sign("lightbox", w * 0.6, 1.2, (0.0, b0 * 0.75 + 0.05, h * 0.6))
    elif kind in ("round", "turnpike"):
        r = w / 2
        g.cyl(0, 0, r, 0.0, h, m(role), n=14)
        if kind == "round":
            for k in range(10):
                a = math.tau * k / 10
                g.cbox(r * 0.92 * math.cos(a), r * 0.92 * math.sin(a), h, 0.5, 0.5, 0.6, m(role))
        else:
            g.moved(z=h).lathe([(r * 1.1, 0.0), (0.0, r * 1.5)], m("roof"), n=14)
            g.box((-0.45, r - 0.05, 0.035), (0.45, r + 0.08, 2.1), m("dark_wood"))
            for i in range(1, int(h / 3.0)):
                g.box((-0.18, r - 0.02, i * 3.0 + 1.0), (0.18, r + 0.06, i * 3.0 + 1.7), m("glass"))
    elif kind in ("square", "belfry", "clock", "tapered"):
        top = w * (0.7 if kind == "tapered" else 1.0)
        _frustum(g, w / 2, top / 2, 0.0, h * 0.8, m(role))
        stage = g.moved(z=h * 0.8)
        sh = h * 0.12
        if kind == "belfry":
            for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                for px in (-1, 1):
                    stage.cbox(sx * top / 2 * 0.9 + sy * px * top * 0.4, sy * top / 2 * 0.9 + sx * px * top * 0.4, 0.0, 0.25, 0.25, sh, m(role))
            stage.cbox(0, 0, sh * 0.2, top * 0.3, top * 0.3, top * 0.35, m("metal"))       # (the bell)
            stage.cbox(0, 0, sh, top + 0.2, top + 0.2, 0.15, m("trim"))
        else:
            stage.cbox(0, 0, 0.0, top, top, sh, m(role))
            stage.cbox(0, 0, sh, top + 0.25, top + 0.25, 0.15, m("trim"))
            if kind == "clock":
                for a in range(4):
                    f = stage.sub(Matrix.Rotation(a * math.pi / 2, 4, "Z") @ Matrix.Translation((0, top / 2, sh * 0.5)) @ Matrix.Rotation(-math.pi / 2, 4, "X"))
                    f.cyl(0, 0, top * 0.35, 0.0, 0.04, m("lamp"), n=16)
                    f.box((-0.03, -0.01, 0.04), (0.03, top * 0.3, 0.06), m("iron"))
        cap = g.moved(z=h * 0.8 + sh + 0.15, rz=math.pi / 4)        # (a 4-sided lathe: turned so its corners meet the tower's)
        cap.lathe([(top * 0.72, 0.0), (0.0, h - (h * 0.8 + sh + 0.15))], m("roof"), n=4) if kind != "tapered" else \
            cap.cbox(0, 0, 0.0, top * 0.6, top * 0.6, 0.6, m("trim"))
        if kind == "tapered":
            c.sign("blade", 0.7, 3.0, (0.0, w / 2 + 0.05, h * 0.5))
    elif kind == "menzeh":
        g.cbox(0, 0, 0.0, w, w, h - 0.6, m(role))
        for a in range(4):
            f = g.sub(Matrix.Rotation(a * math.pi / 2, 4, "Z") @ Matrix.Translation((0, w / 2, 0.9)))
            f.extrude_xz(arch_outline("horseshoe", 0.8, 1.4, 4), EPS, 0.02, m("glass"))
        g.moved(z=h - 0.6, rz=math.pi / 4).lathe([(w * 0.75, 0.0), (w * 0.75, 0.1), (0.0, 0.6)], m("tile"), n=4)
    elif kind == "ziggurat":
        steps = c.p.get("steps", 4)
        for i in range(steps):
            f = 1.0 - i / steps * 0.75
            g.cbox(0, 0, h * i / steps, w * f, w * f, h / steps, m(role if i % 2 == 0 else "trim"))
        c.glow("outline", (-w / 2, w / 2 + 0.01, h / steps), w)


def _frustum(g, b0, b1, z0, z1, mat):
    """a square frustum: half-width b0 at z0 to b1 at z1"""
    lo = [(-b0, -b0, z0), (b0, -b0, z0), (b0, b0, z0), (-b0, b0, z0)]
    hi = [(-b1, -b1, z1), (b1, -b1, z1), (b1, b1, z1), (-b1, b1, z1)]
    for k in range(4):
        j = (k + 1) % 4
        g.face([lo[k], lo[j], hi[j], hi[k]], mat)
    g.face(list(reversed(lo)), mat)
    g.face(hi, mat)


# ------------------------------------------------------------------ gables, false fronts and small roofs
def gable(c):
    """a gable wall crowning a narrow front (in the wall plane, t thick): step (crow steps) | neck | bell |
    cornice (a flat spout gable) | false (a boomtown false front) | pediment"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "step")
    w, h = c.w, c.h
    t = c.p.get("t", 0.3)
    r = w / 2
    if kind == "step":
        n = c.p.get("steps", 5)
        pts = [(-r, 0.0), (r, 0.0)]
        right = []
        for i in range(n):
            x0 = r - r * 0.8 * i / n
            z1 = h * (i + 1) / n
            right += [(x0, h * i / n), (x0, z1)]
        top = [(r * 0.2, h), (-r * 0.2, h)]
        left = [(-x, z) for x, z in reversed(right)]
        pts += right + top + left
        g.extrude_xz(_dedupe(pts), -t, 0.0, m(c.p.get("mat", "wall")))
    elif kind in ("neck", "bell"):
        n = 10
        right = []
        for i in range(n + 1):
            u = i / n
            if kind == "neck":
                x = r if u < 0.45 else r * 0.38
                z = h * u
                if 0.4 < u < 0.6:
                    x = r * (0.38 + 0.62 * (1 - (u - 0.4) / 0.2) ** 2)
            else:
                x = r * (1.0 - 0.62 * math.sin(u * math.pi / 2) ** 1.5)
                z = h * u
            right.append((x, z))
        right[0] = (r, 0.0)
        top_r = right[-1][0]
        pts = [(-r, 0.0)] + right[:-1] + [(top_r, h), (0.0, h + 0.4 * (kind == "bell")), (-top_r, h)] + [(-x, z) for x, z in reversed(right[:-1])][:-1]
        g.extrude_xz(_dedupe(pts), -t, 0.0, m(c.p.get("mat", "wall")))
        g.box((-top_r - 0.1, -t - 0.05, h - 0.1), (top_r + 0.1, 0.06, h), m("trim"))
    elif kind in ("cornice", "false"):
        g.box((-r, -t, 0.0), (r, 0.0, h), m(c.p.get("mat", "wall")))
        g.box((-r - 0.15, -t - 0.1, h - 0.25), (r + 0.15, 0.2, h), m("trim"))
        for i in range(int(w / 0.8)):
            x = -r + 0.4 + i * 0.8
            bracket(g.moved(x=x, z=h - 0.25), m, 0.08, 0.18, 0.3, "trim")
        if kind == "false":
            c.sign("painted", w * 0.8, h * 0.35, (0.0, EPS + 0.01, h * 0.55))
            c.glow("outline", (-r, 0.21, h), w)
    elif kind == "pediment":
        g.extrude_xz([(-r, 0.0), (r, 0.0), (0.0, h)], -t, 0.0, m(c.p.get("mat", "trim")))


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-5 or abs(out[-1][1] - p[1]) > 1e-5:
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < 1e-5 and abs(out[0][1] - out[-1][1]) < 1e-5:
        out.pop()
    return out


def roofpiece(c):
    """a small roof form: hip (a hipped roof of w x d, slabs) | gable (a pitched roof box) | dormer | bump (a five-
    sided Lunenburg dormer) | chalet (a little pitched house set on a flat roof) | altana (a timber roof deck on
    posts) | pergola | loggia (an arcade with a roof)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "gable")
    w, d, h = c.w, c.d, c.h
    if kind == "hip":
        rh = h
        g.extrude_xy([(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], 0.0, 0.15, m("roof"))
        lo = [(-w / 2, -d / 2, 0.15), (w / 2, -d / 2, 0.15), (w / 2, d / 2, 0.15), (-w / 2, d / 2, 0.15)]
        ridge = max(0.0, (w - d) / 2)
        a, b = (-ridge, 0.0, rh), (ridge, 0.0, rh)
        g.face([lo[0], lo[1], b, a], m("roof"))
        g.face([lo[1], lo[2], b], m("roof"))
        g.face([lo[2], lo[3], a, b], m("roof"))
        g.face([lo[3], lo[0], a], m("roof"))
    elif kind in ("gable", "chalet", "dormer"):
        bw, bh = w, (h * 0.55 if kind == "chalet" else h * 0.5)
        role = "wall2" if kind != "dormer" else "wall"
        g.cbox(0, 0, 0.0, bw, d, bh, m(role))
        sub = g.sub(Matrix.Translation((0, 0, bh)))
        sub.extrude_xz([(-bw / 2 - 0.25, 0.0), (bw / 2 + 0.25, 0.0), (0.0, h - bh)], -d / 2 - 0.2, d / 2 + 0.2, m("roof"))
        if kind != "dormer":
            g.box((-0.45, d / 2, 0.035), (0.45, d / 2 + 0.05, 2.1), m("dark_wood"))
            for x in (-bw / 2 + 0.9, bw / 2 - 0.9):
                g.box((x - 0.4, d / 2, 1.0), (x + 0.4, d / 2 + 0.04, 2.0), m("glass"))
        else:
            g.box((-bw * 0.3, d / 2, bh * 0.2), (bw * 0.3, d / 2 + 0.04, bh * 0.9), m("glass"))
    elif kind == "bump":
        g.extrude_xy([(-w / 2, -d / 2), (w / 2, -d / 2), (w * 0.35, d / 2), (-w * 0.35, d / 2)], 0.0, h * 0.6, m("wall"))
        g.moved(z=h * 0.6).extrude_xz([(-w / 2 - 0.1, 0.0), (w / 2 + 0.1, 0.0), (0.0, h * 0.4)], -d / 2 - 0.1, d / 2 + 0.15, m("roof"))
        g.box((-w * 0.25, d / 2 - 0.02, h * 0.15), (w * 0.25, d / 2 + 0.02, h * 0.5), m("glass"))
    elif kind in ("altana", "pergola"):
        top = h
        for x in (-w / 2 + 0.1, w / 2 - 0.1):
            for y in (-d / 2 + 0.1, d / 2 - 0.1):
                g.cyl(x, y, 0.07, 0.0, top, m("wood"), n=6)
        if kind == "altana":
            g.cbox(0, 0, top, w, d, 0.08, m("wood"))
            for x in (-w / 2, w / 2):
                g.tube((x, -d / 2, top + 1.0), (x, d / 2, top + 1.0), 0.03, m("wood"), n=4)
            g.tube((-w / 2, d / 2, top + 1.0), (w / 2, d / 2, top + 1.0), 0.03, m("wood"), n=4)
            for i in range(int(top / 0.25)):
                g.box((w / 2 - 0.7, -d / 2 + 0.1 + i * 0.25 * (d - 0.2) / top, i * 0.25), (w / 2 - 0.1, -d / 2 + 0.35 + i * 0.25 * (d - 0.2) / top, i * 0.25 + 0.04), m("wood"))
        else:
            for i in range(int(w / 0.45) + 1):
                x = -w / 2 + i * w / int(w / 0.45)
                g.box((x - 0.03, -d / 2, top), (x + 0.03, d / 2, top + 0.14), m("wood"))
            c.lights((-w / 2, -d / 2, top), (w / 2, d / 2, top))
    elif kind == "loggia":
        n = max(2, int(w / 2.2))
        aw = w / n
        g.box((-w / 2, -d, h - 0.5), (w / 2, 0.0, h), m("wall"))
        for i in range(n + 1):
            x = -w / 2 + i * aw
            g.cbox(x, -0.2, 0.0, 0.3, 0.3, h - 0.5, m("stone"))
        for i in range(n):
            x = -w / 2 + (i + 0.5) * aw
            inner = arch_outline("round", aw - 0.3, h - 0.65, 5)
            outer = arch_outline("rect", aw - 0.3 + 0.001, h - 0.5, 5)
            g.moved(x=x).ring_xz(outer, inner, -0.36, -0.04, m("wall"))
        g.box((-w / 2 - 0.1, -d - 0.1, h), (w / 2 + 0.1, 0.1, h + 0.12), m("trim"))


# ------------------------------------------------------------------ stairs and ladders
def stair(c):
    """an outside stair: kind steel (a bolt-on flight with a landing and rails) | spiral (round a pole) | steep (a
    plain flight against a wall) | beam (beam steps sticking out of a wall) | cut (a flight between two parapets) |
    core (an open stair core bay) | helix (a ramp tower).  Runs up along +X from z 0 to h, against the wall (y 0..d)."""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "steel")
    w, h, d = c.w, c.h, c.d
    if kind == "spiral":
        r = w / 2
        n = max(8, int(h / 0.19))
        g.cyl(0, 0, 0.07, 0.0, h + 1.0, m("iron"), n=8)
        for i in range(n):
            a = i * math.tau / 13
            z = (i + 1) * h / n
            s = g.sub(Matrix.Translation((0, 0, z)) @ Matrix.Rotation(a, 4, "Z"))
            s.extrude_xy([(0.06, -0.06), (r, -0.16), (r, 0.16), (0.06, 0.06)], -0.04, 0.0, m("iron"))
            s.tube((r, 0, 0.0), (r, 0, 0.95), 0.012, m("iron"), n=4)
        for i in range(n - 1):
            a0, a1 = i * math.tau / 13, (i + 1) * math.tau / 13
            g.tube((r * math.cos(a0), r * math.sin(a0), (i + 1) * h / n + 0.95), (r * math.cos(a1), r * math.sin(a1), (i + 2) * h / n + 0.95), 0.02, m("iron"), n=4)
        return
    if kind == "beam":
        n = max(3, int(h / 0.25))
        for i in range(n):
            g.box((i * w / n, EPS, i * h / n), (i * w / n + 0.25, d, i * h / n + 0.12), m("wood"))
        return
    if kind == "helix":
        r = w / 2
        g.cyl(0, 0, r * 0.3, 0.0, h, m("concrete"), n=12)
        turns = max(1, int(h / 3.2))
        n = turns * 16
        for i in range(n):
            a0, a1 = math.tau * i / 16, math.tau * (i + 1) / 16
            z0, z1 = h * i / n, h * (i + 1) / n
            ri, ro = r * 0.3, r
            p = [(ri * math.cos(a0), ri * math.sin(a0), z0), (ro * math.cos(a0), ro * math.sin(a0), z0),
                 (ro * math.cos(a1), ro * math.sin(a1), z1), (ri * math.cos(a1), ri * math.sin(a1), z1)]
            g.face(p, m("concrete"))
            g.face([(x, y, z - 0.2) for x, y, z in reversed(p)], m("concrete"))
            g.face([p[1], (p[1][0], p[1][1], p[1][2] - 0.2), (p[2][0], p[2][1], p[2][2] - 0.2), p[2]], m("concrete"))
            g.face([p[3], (p[3][0], p[3][1], p[3][2] - 0.2), (p[0][0], p[0][1], p[0][2] - 0.2), p[0]], m("concrete"))
            g.tube((ro * math.cos(a0), ro * math.sin(a0), z0 + 1.0), (ro * math.cos(a1), ro * math.sin(a1), z1 + 1.0), 0.02, m("iron"), n=4)
        return
    if kind == "core":
        g.cbox(0, 0, 0.0, w, d, 0.15, m("concrete"))
        for x in (-w / 2, w / 2 - 0.2):
            g.box((x, -d / 2, 0.0), (x + 0.2, d / 2, h), m("concrete"))
        _flight(g, m, -w / 2 + 0.2, w / 2 - 0.2, -d / 2, 0.0, 0.0, h / 2, "concrete", rails=False)
        _flight(g, m, w / 2 - 0.2, -w / 2 + 0.2, 0.0, d / 2, h / 2, h, "concrete", rails=False)
        g.box((-w / 2 + 0.2, -d / 2, h / 2 - 0.15), (-w / 2 + 1.0, d / 2, h / 2), m("concrete"))
        g.box((-w / 2, -d / 2, h - 0.04), (-w / 2 + 0.6, d / 2, h), m("lamp")) if c.p.get("lamp", True) else None
        return
    # straight flights: steel (stringers, rails, a top landing), steep, cut (parapets)
    role = {"steel": "iron", "steep": "stone", "cut": "stone"}.get(kind, "iron")
    run = w
    _flight(g, m, 0.0, run, EPS + 0.05, d, 0.0, h, role, rails=kind == "steel")
    if kind == "steel":
        g.box((run, EPS + 0.05, h - 0.05), (run + 1.0, d, h), m(role))
        g.tube((run + 1.0, d, h), (run + 1.0, d, h + 1.0), 0.02, m(role), n=4)
        g.tube((run, d, h + 1.0), (run + 1.0, d, h + 1.0), 0.02, m(role), n=4)
    if kind == "cut":
        for y in (EPS, d + 0.15):
            g.sub(Matrix.Translation((0, 0, 0))).extrude_xz([(0.0, 0.0), (run, h), (run, h + 0.9), (0.0, 0.9)], y, y + 0.15, m("stone"))


def _flight(g, m, x0, x1, y0, y1, z0, z1, role, rails=True):
    n = max(2, int(abs(z1 - z0) / 0.19))
    dx = (x1 - x0) / n
    for i in range(n):
        xa = x0 + dx * i
        za = z0 + (z1 - z0) * (i + 1) / n
        g.box((min(xa, xa + dx), y0, za - 0.04), (max(xa, xa + dx), y1, za), m(role))
    if rails:
        for y in (y0, y1):
            g.tube((x0, y, z0 + 0.95), (x1, y, z1 + 0.95), 0.02, m(role), n=4)
            g.tube((x0, y, z0), (x1, y, z1), 0.03, m(role), n=4)
            for i in range(0, n + 1, 3):
                x = x0 + dx * i
                z = z0 + (z1 - z0) * i / n
                g.tube((x, y, z), (x, y, z + 0.95), 0.015, m(role), n=4)


def ladder(c):
    """a climbable ladder (a part named ladder_*: the game makes it a climb zone), with safety hoops if tall"""
    b = c.b
    name = "ladder_sky_%d" % c.next_id("ladder")
    lp = b.part(name)
    from .geo import G
    g = G(lp, c.g.M)
    h = c.h
    for x in (-0.22, 0.22):
        g.box((x - 0.025, 0.12, 0.0), (x + 0.025, 0.17, h + 1.0), c.m("iron"))
    for i in range(1, int(h / 0.3) + 1):
        g.tube((-0.22, 0.145, i * 0.3), (0.22, 0.145, i * 0.3), 0.012, c.m("iron"), n=4)
    for x in (-0.22, 0.22):
        g.box((x - 0.02, EPS, h * 0.5), (x + 0.02, 0.12, h * 0.5 + 0.05), c.m("iron"))
    if h > 3.0 and c.p.get("hoops", True):
        for i in range(int((h - 2.2) / 0.9)):
            z = 2.2 + i * 0.9
            for k in range(6):
                a0, a1 = math.pi * k / 6, math.pi * (k + 1) / 6
                g.tube((0.38 * math.cos(a0), 0.15 + 0.38 * math.sin(a0), z), (0.38 * math.cos(a1), 0.15 + 0.38 * math.sin(a1), z), 0.012, c.m("iron"), n=4)


# ------------------------------------------------------------------ bridges and passages
def bridge(c):
    """a span along +Y from y 0 to L (c.d): kind sky (a covered footbridge: deck, rails, roof, lamps) | plank (planks
    on ropes with rope rails) | room (a room bridging a lane: the sabat) | corridor (an enclosed corridor) | tunnel
    (a covered alley / pend passage: a box with an arched mouth) | backshop (a box hung off brackets)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "sky")
    w, L, h = c.w, c.d, c.h
    if kind == "plank":
        n = max(2, int(L / 0.3))
        for i in range(n):
            y = L * i / n
            sag = 0.25 * math.sin(math.pi * (i + 0.5) / n)
            g.box((-w / 2, y + 0.02, -sag - 0.05), (w / 2, y + L / n - 0.02, -sag), m("wood"))
        for x in (-w / 2, w / 2):
            prev = None
            for i in range(9):
                y = L * i / 8
                p = (x, y, 0.9 - 0.25 * math.sin(math.pi * i / 8))
                if prev:
                    g.tube(prev, p, 0.015, m("rope"), n=4)
                prev = p
        return
    if kind in ("sky", "corridor", "room"):
        g.box((-w / 2, 0.0, -0.2), (w / 2, L, 0.0), m("concrete" if kind == "sky" else "wood"))
        if kind == "sky":
            for x in (-w / 2, w / 2):
                g.tube((x, 0.0, 1.05), (x, L, 1.05), 0.03, m("metal"), n=4)
                for i in range(int(L / 1.5) + 1):
                    y = L * i / max(1, int(L / 1.5))
                    g.tube((x, y, 0.0), (x, y, h), 0.035, m("metal"), n=4)
            g.box((-w / 2 - 0.15, -0.1, h), (w / 2 + 0.15, L + 0.1, h + 0.08), m("roof"))
            for i in range(int(L / 3) + 1):
                g.box((-0.15, L * i / max(1, int(L / 3)) - 0.15, h - 0.08), (0.15, L * i / max(1, int(L / 3)) + 0.15, h), m("lamp"))
            c.lights((-w / 2, 0.0, h), (-w / 2, L, h))
            c.lights((w / 2, 0.0, h), (w / 2, L, h))
        else:
            for x in (-w / 2, w / 2 - 0.2):
                g.box((x, 0.0, 0.0), (x + 0.2, L, h), m("wall" if kind == "room" else "wood"))
            g.box((-w / 2, 0.0, h), (w / 2, L, h + 0.2), m("roof"))
            for i in range(int(L / 2.5)):
                y = 1.0 + i * 2.5
                for x in (-w / 2 - 0.01, w / 2 + 0.01):
                    g.box((x - 0.012, y, 1.0), (x + 0.012, y + 1.0, 2.0), m("glass"))
        return
    if kind == "tunnel":
        inner = arch_outline("round", w, h, 5)
        outer = arch_outline("rect", w + 0.6, h + 0.5, 5)
        g.ring_xz(outer, inner, -L, 0.0, m("wall"))
        c.glow("tube", (-w / 2 + 0.1, -0.4, h - 0.15), w - 0.2)
        return
    if kind == "backshop":
        g.box((-w / 2, EPS, 0.0), (w / 2, L, h), m("wood"))
        g.box((-w / 2 + 0.3, L, 0.9), (w / 2 - 0.3, L + 0.03, h - 0.4), m("glass"))
        for x in (-w / 2 + 0.2, w / 2 - 0.2):
            bracket(g.moved(x=x), m, 0.12, L * 0.9, 1.2, "dark_wood", curve=False)


# ------------------------------------------------------------------ roof clutter
def clutter(c):
    """the stuff on roofs and walls: tank (a water tank on a stand) | drum | ac (a heat exchanger box) | antenna |
    shack (a lean-to room) | stall (a market stall) | loft (a pigeon loft on legs) | chimney | vent | trencadis (a
    mosaic chimney) | rebar | vending | shrine (a little gate, two lanterns, an altar) | stairhead (the roof
    bulkhead with its door) | lightshaft (a rail round a shaft) | laundry | scaffold | pipes | tray | wires |
    statue_sign (a pedestal for a giant figure sign) | gantry | crane (a jib on a gable) | hangar_door"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "tank")
    w, h, d = c.w, c.h, c.d
    if k == "tank":
        for x in (-w * 0.35, w * 0.35):
            for y in (-w * 0.35, w * 0.35):
                g.box((x - 0.04, y - 0.04, 0.0), (x + 0.04, y + 0.04, h * 0.4), m("iron"))
        g.cyl(0, 0, w / 2, h * 0.4, h, m(c.p.get("mat", "metal")), n=12)
        g.moved(z=h).lathe([(w / 2, 0.0), (0.0, 0.25)], m(c.p.get("mat", "metal")), n=12)
    elif k == "drum":
        g.cyl(0, 0, w / 2, 0.0, h, m("iron"), n=10)
    elif k == "ac":
        g.box((-w / 2, EPS, 0.0), (w / 2, d, h), m("trim"))
        g.sub(Matrix.Translation((0, d, h / 2)) @ Matrix.Rotation(-math.pi / 2, 4, "X")).cyl(0, 0, min(w, h) * 0.38, 0.0, 0.015, m("iron"), n=12)
        g.box((-w / 2, EPS, -0.06), (w / 2, d + 0.05, 0.0), m("iron"))
    elif k == "antenna":
        g.cyl(0, 0, 0.03, 0.0, h, m("metal"), n=6)
        for i in range(4):
            z = h * (0.55 + 0.1 * i)
            g.tube((-0.4 + 0.06 * i, 0, z), (0.4 - 0.06 * i, 0, z), 0.01, m("metal"), n=4)
    elif k == "shack":
        g.box((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h * 0.85), m(c.p.get("mat", "wall2")))
        g.sub(Matrix.Translation((0, 0, h * 0.85))).extrude_xz([(-w / 2 - 0.15, 0.0), (w / 2 + 0.15, 0.0), (w / 2 + 0.15, 0.05), (-w / 2 - 0.15, 0.32)], -d / 2 - 0.15, d / 2 + 0.15, m("metal"))
        g.box((-0.4, d / 2, 0.035), (0.4, d / 2 + 0.04, 1.95), m("dark_wood"))
        g.box((0.6, d / 2, 1.0), (1.1, d / 2 + 0.04, 1.6), m("glass"))
        c.glow("tube", (-0.5, d / 2 + 0.06, 2.05), 1.0)
    elif k == "stall":
        g.box((-w / 2, -d / 2 + 0.2, 0.0), (w / 2, -d / 2 + 0.8, 0.95), m("wood"))
        for x in (-w / 2, w / 2 - 0.08):
            for y in (-d / 2, d / 2 - 0.08):
                g.box((x, y, 0.0), (x + 0.08, y + 0.08, h), m("wood"))
        for i in range(max(1, int(w / 0.5))):
            x0 = -w / 2 + w * i / max(1, int(w / 0.5))
            x1 = -w / 2 + w * (i + 1) / max(1, int(w / 0.5))
            mat = m("fabric" if i % 2 == 0 else "fabric2")
            q = [(x0, -d / 2 - 0.4, h - 0.3), (x1, -d / 2 - 0.4, h - 0.3), (x1, d / 2, h), (x0, d / 2, h)]
            g.face(q, mat)
            g.face(list(reversed(q)), mat)
        g.box((-w / 2 + 0.1, d / 2 - 0.4, 1.2), (w / 2 - 0.1, d / 2 - 0.1, 1.25), m("wood"))
        c.sign("painted", w * 0.7, 0.4, (0.0, -d / 2 - 0.42, h - 0.35))
        c.lights((-w / 2, -d / 2 - 0.4, h - 0.3), (w / 2, -d / 2 - 0.4, h - 0.3))
    elif k == "loft":
        for x in (-w / 2 + 0.1, w / 2 - 0.1):
            for y in (-d / 2 + 0.1, d / 2 - 0.1):
                g.box((x - 0.04, y - 0.04, 0.0), (x + 0.04, y + 0.04, h * 0.4), m("wood"))
        g.cbox(0, 0, h * 0.4, w, d, h * 0.45, m("wood"))
        g.moved(z=h * 0.85).extrude_xz([(-w / 2 - 0.1, 0.0), (w / 2 + 0.1, 0.0), (0.0, h * 0.15)], -d / 2 - 0.1, d / 2 + 0.1, m("roof"))
        for i in range(4):
            for j in range(2):
                g.box((-w / 2 + 0.25 + i * (w - 0.5) / 3 - 0.07, d / 2, h * 0.5 + j * h * 0.17), (-w / 2 + 0.25 + i * (w - 0.5) / 3 + 0.07, d / 2 + 0.02, h * 0.5 + j * h * 0.17 + 0.12), m("iron"))
    elif k == "chimney":
        g.cbox(0, 0, 0.0, w, d, h, m(c.p.get("mat", "wall2")))
        g.cbox(0, 0, h - 0.15, w + 0.1, d + 0.1, 0.12, m("trim"))
        for x in (-w / 4, w / 4):
            g.cyl(x, 0, 0.1, h, h + 0.45, m("accent"), n=6)
    elif k == "vent":
        g.cyl(0, 0, w / 2, 0.0, h, m("metal"), n=8)
        g.moved(z=h).lathe([(w * 0.9, 0.0), (w * 0.9, 0.1), (0.0, 0.3)], m("metal"), n=8)
    elif k == "trencadis":
        prof = [(w / 2, 0.0), (w * 0.42, h * 0.3), (w * 0.52, h * 0.55), (w * 0.3, h * 0.8), (w * 0.4, h * 0.9), (0.0, h)]
        g.lathe(prof, m("tile"), n=7)
        g.moved(z=h * 0.55, rz=0.4).lathe([(w * 0.53, 0.0), (w * 0.55, 0.12), (0.0, 0.13)], m("accent"), n=7)
    elif k == "rebar":
        for x in (-0.06, 0.06):
            for y in (-0.06, 0.06):
                g.tube((x, y, 0.0), (x * 1.3, y * 1.3, h), 0.008, m("iron"), n=4)
    elif k == "vending":
        g.box((-w / 2, -d / 2, 0.0), (w / 2, d / 2, h), m(c.p.get("mat", "accent")))
        g.box((-w / 2 + 0.08, d / 2, 0.8), (w / 2 - 0.08, d / 2 + 0.02, h - 0.1), m("lamp"))
        g.box((-w / 2 + 0.08, d / 2, 0.2), (w / 2 - 0.08, d / 2 + 0.03, 0.45), m("iron"))
    elif k == "shrine":
        for x in (-w * 0.3, w * 0.3):
            g.cyl(x, d * 0.4, 0.06, 0.0, h, m("accent"), n=6)
        g.box((-w * 0.45, d * 0.4 - 0.06, h - 0.25), (w * 0.45, d * 0.4 + 0.06, h - 0.15), m("accent"))
        g.box((-w * 0.5, d * 0.4 - 0.08, h - 0.05), (w * 0.5, d * 0.4 + 0.08, h + 0.05), m("dark_wood"))
        g.cbox(0, -d * 0.2, 0.0, w * 0.5, d * 0.4, 0.8, m("wood"))
        g.moved(z=0.8).extrude_xz([(-w * 0.32, 0.0), (w * 0.32, 0.0), (0.0, 0.35)], -d * 0.42, 0.02, m("roof"))
        for x in (-w * 0.45, w * 0.45):
            g.cyl(x, d * 0.4, 0.04, 0.0, 1.1, m("stone"), n=6)
            g.cbox(x, d * 0.4, 1.1, 0.22, 0.22, 0.28, m("lamp"))
    elif k == "stairhead":
        g.cbox(0, 0, 0.0, w, d, h, m(c.p.get("mat", "wall")))
        g.cbox(0, 0, h, w + 0.2, d + 0.2, 0.12, m("trim"))
        g.box((-0.45, d / 2, 0.035), (0.45, d / 2 + 0.05, 2.1), m("dark_wood"))
        g.box((-0.12, d / 2, 2.25), (0.12, d / 2 + 0.12, 2.4), m("lamp"))
        c.sign("painted", min(w * 0.6, 1.2), 0.35, (0.0, d / 2 + 0.01, 2.45))
    elif k == "lightshaft":
        r = w / 2
        for (ax, ay), (bx, by) in (((-r, -r), (r, -r)), ((r, -r), (r, r)), ((r, r), (-r, r)), ((-r, r), (-r, -r))):
            g.tube((ax, ay, 1.0), (bx, by, 1.0), 0.025, m("iron"), n=4)
            g.tube((ax, ay, 0.0), (ax, ay, 1.0), 0.025, m("iron"), n=4)
        g.cbox(0, 0, 0.0, w + 0.3, w + 0.3, 0.04, m("trim"))
    elif k == "laundry":
        for x in (-w / 2, w / 2):
            g.cyl(x, 0, 0.03, 0.0, h + 0.2, m("metal"), n=6)
        for j in range(2):
            y = -0.15 + 0.3 * j
            g.tube((-w / 2, y, h), (w / 2, y, h), 0.006, m("rope"), n=4)
            n = int(w / 0.55)
            for i in range(n):
                x = -w / 2 + 0.3 + i * (w - 0.6) / max(1, n - 1)
                cw, chh = 0.35 + 0.1 * ((i * 7 + j) % 3), 0.45 + 0.15 * ((i * 5 + j) % 3)
                col = m(["fabric", "fabric2", "accent2", "cloth"][(i + j) % 4])
                q = [(x - cw / 2, y, h - chh), (x + cw / 2, y, h - chh), (x + cw / 2, y, h), (x - cw / 2, y, h)]
                g.face(q, col)
                g.face(list(reversed(q)), col)
    elif k == "scaffold":
        for i in range(int(w / 1.5) + 1):
            x = -w / 2 + i * 1.5
            for y in (0.4, 1.2):
                g.tube((x, y, 0.0), (x, y, h), 0.03, m("wood"), n=4)
        for j in range(int(h / 2.0) + 1):
            z = j * 2.0
            for y in (0.4, 1.2):
                g.tube((-w / 2, y, z), (w / 2, y, z), 0.025, m("wood"), n=4)
        q = [(-w / 2, 1.3, 0.0), (w / 2, 1.3, 0.0), (w / 2, 1.3, h), (-w / 2, 1.3, h)]
        g.face(q, m("tile"))
        g.face(list(reversed(q)), m("tile"))
    elif k in ("pipes", "tray", "wires"):
        n = {"pipes": 3, "tray": 1, "wires": 4}[k]
        for i in range(n):
            r = {"pipes": 0.06 - 0.012 * i, "tray": 0.05, "wires": 0.012}[k]
            z = 0.1 + i * 0.13
            if k == "wires":
                prev = None
                for s in range(9):
                    x = -w / 2 + w * s / 8
                    p = (x, d + 0.05 * i, z - 0.35 * math.sin(math.pi * s / 8))
                    if prev:
                        g.tube(prev, p, r, m("iron"), n=4)
                    prev = p
            else:
                g.tube((-w / 2, 0.15 + 0.08 * i, z), (w / 2, 0.15 + 0.08 * i, z), r, m("metal" if k == "pipes" else "iron"), n=6)
        if k != "wires":
            for x in [(-w / 2 + 0.3) + (w - 0.6) * i / max(1, int(w / 1.2)) for i in range(int(w / 1.2) + 1)]:
                g.box((x - 0.02, EPS, 0.02), (x + 0.02, 0.3, 0.06), m("iron"))
    elif k == "statue_sign":
        g.cbox(0, 0, 0.0, w, d, 0.8, m("stone"))
        c.sign("figure", w, h - 0.8, (0.0, 0.0, 0.8))
    elif k == "gantry":
        for x in (-w / 2, w / 2):
            for y in (-d / 2, d / 2):
                g.box((x - 0.15, y - 0.15, 0.0), (x + 0.15, y + 0.15, h), m("accent"))
            g.box((x - 0.15, -d / 2, h - 0.4), (x + 0.15, d / 2, h), m("accent"))
        g.box((-w / 2, -0.2, h - 0.6), (w / 2, 0.2, h - 0.3), m("accent"))
        g.box((-0.4, -0.3, h - 1.0), (0.4, 0.3, h - 0.6), m("iron"))
    elif k == "crane":
        g.cyl(0, 0, 0.12, 0.0, h, m("dark_wood"), n=6)
        g.tube((0, 0, h - 0.2), (0, d, h - 0.2), 0.09, m("dark_wood"), n=4)
        g.tube((0, 0, h * 0.4), (0, d * 0.7, h - 0.25), 0.06, m("dark_wood"), n=4)
        g.tube((0, d - 0.05, h - 0.3), (0, d - 0.05, h - 1.6), 0.008, m("rope"), n=4)
        g.box((-0.06, d - 0.11, h - 1.75), (0.06, d + 0.01, h - 1.6), m("iron"))
    elif k == "hangar_door":
        n = max(2, int(w / 2.0))
        for i in range(n):
            x0 = -w / 2 + w * i / n
            g.box((x0 + 0.02, EPS, 0.035), (x0 + w / n - 0.02, 0.12 + 0.05 * (i % 2), h), m("metal" if i % 2 == 0 else "wall2"))
        g.box((-w / 2 - 0.2, EPS, h), (w / 2 + 0.2, 0.3, h + 0.3), m("iron"))
        c.sign("painted", w * 0.6, h * 0.3, (0.0, 0.18, h * 0.55))


# ------------------------------------------------------------------ columns, piers, posts, frames
def column(c):
    """a column: kind round (base, shaft, capital) | turned (a turned timber post) | pier (square, an arcade pier) |
    cluster | bone (a bulging organic pier) | inverted (narrowing toward its foot) | mirrored (faceted mirror) |
    girder (an exposed red steel frame bay: column + beam + brace) | frame (a concrete frame bay)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "round")
    r = c.w / 2
    h = c.h
    if kind == "round":
        g.cbox(0, 0, 0.035, c.w * 1.3, c.w * 1.3, 0.2, m("stone"))
        g.lathe([(r, 0.235), (r * 0.9, h - 0.35), (r * 1.2, h - 0.2)], m(c.p.get("mat", "stone")), n=12)
        g.cbox(0, 0, h - 0.2, c.w * 1.4, c.w * 1.4, 0.2, m("stone"))
    elif kind == "turned":
        g.lathe([(r, 0.035), (r, 0.2), (r * 0.6, 0.35), (r * 0.8, h * 0.3), (r * 0.6, h * 0.5), (r * 0.85, h * 0.7), (r * 0.55, h - 0.3), (r, h - 0.15), (r, h)], m("wood"), n=8)
    elif kind in ("pier", "cluster"):
        g.cbox(0, 0, 0.035, c.w, c.w, h - 0.035, m(c.p.get("mat", "stone")))
        if kind == "cluster":
            for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                g.cyl(sx * r * 0.7, sy * r * 0.7, r * 0.35, 0.035, h, m("stone"), n=8)
        g.cbox(0, 0, h - 0.25, c.w * 1.25, c.w * 1.25, 0.25, m("trim"))
    elif kind == "bone":
        g.lathe([(r * 0.7, 0.035), (r * 1.1, h * 0.12), (r * 0.65, h * 0.35), (r * 0.9, h * 0.55), (r * 0.6, h * 0.75), (r * 1.15, h * 0.95), (r * 1.2, h)], m("stone"), n=9)
    elif kind == "inverted":
        g.lathe([(r * 0.45, 0.035), (r * 0.6, h * 0.3), (r * 1.0, h * 0.9), (r * 1.3, h)], m("stone"), n=8)
    elif kind == "mirrored":
        g.lathe([(r, 0.035), (r, h)], m("mirror"), n=6)
        g.cbox(0, 0, h - 0.15, c.w * 1.3, c.w * 1.3, 0.15, m("metal"))
    elif kind == "girder":
        w, d = c.w, c.d
        g.box((-w / 2, -0.15, 0.0), (-w / 2 + 0.3, 0.15, h), m("accent"))
        g.box((w / 2 - 0.3, -0.15, 0.0), (w / 2, 0.15, h), m("accent"))
        g.box((-w / 2, -0.15, h - 0.4), (w / 2, 0.15, h), m("accent"))
        g.tube((-w / 2 + 0.3, 0.0, 0.3), (w / 2 - 0.3, 0.0, h - 0.4), 0.06, m("accent"), n=4)
        for x in (-w / 2 + 0.15, w / 2 - 0.15):
            for z in (0.3, h - 0.2):
                g.box((x - 0.06, 0.15, z - 0.06), (x + 0.06, 0.18, z + 0.06), m("iron"))
    elif kind == "frame":
        w, d = c.w, c.d
        for x in (-w / 2, w / 2 - 0.35):
            g.box((x, -0.175, 0.0), (x + 0.35, 0.175, h), m("concrete"))
        g.box((-w / 2, -0.175, h - 0.25), (w / 2, 0.175, h), m("concrete"))
        infill = c.p.get("infill", c.v if c.v in ("brick", "tin", "glass", "open") else "brick")
        if infill != "open":
            role = {"brick": "accent", "tin": "metal", "glass": "glass"}.get(infill, "wall")
            g.box((-w / 2 + 0.35, -0.1, 0.0), (w / 2 - 0.35, 0.05, h - 0.25), m(role))


# ------------------------------------------------------------------ cells and modules
def cell(c):
    """a stackable cell: kind vault (a barrel-vaulted cell, door and vent on its face: the ghorfa) | souk (a vaulted
    souk bay with two shop cells) | box (a Habitat box: glazed end, door, roof rail) | capsule (a skybox with a
    porthole) | ring (a ring-house sector: a room bay and a gallery) | bar (a tiny two-storey bar unit) | basso (a
    one-room ground floor shop-home opening on the lane) | pit (a vaulted pit room)"""
    g, m = c.g, c.m
    kind = c.p.get("kind", c.v or "vault")
    w, h, d = c.w, c.h, c.d
    role = c.p.get("mat", "wall")
    if kind in ("vault", "souk", "pit"):
        outer = arch_outline("round", w, h, 5)
        g.extrude_xz(outer, -d, 0.0, m(role))
        g.extrude_xz(arch_outline("rect" if kind != "souk" else "round", 0.9 if kind != "souk" else w * 0.7, 1.9 if kind != "souk" else h * 0.75, 5), EPS, 0.03, m("dark_wood" if kind != "souk" else "glass"))
        if kind == "vault":
            g.box((-0.2, EPS, h * 0.7), (0.2, 0.03, h * 0.82), m("dark_wood"))
            c.glow("door", (-0.45, 0.04, 2.0), 0.9)
        else:
            c.sign("lightbox", w * 0.6, 0.45, (0.0, 0.04, h * 0.78))
    elif kind in ("box", "capsule"):
        g.box((-w / 2, -d, 0.0), (w / 2, 0.0, h), m(role if kind == "box" else "trim"))
        if kind == "box":
            g.box((-w / 2 + 0.15, EPS, 0.2), (w / 2 - 0.15, 0.03, h - 0.25), m("glass"))
            for i in range(1, int(w / 1.2)):
                g.box((-w / 2 + i * w / int(w / 1.2) - 0.03, 0.03, 0.2), (-w / 2 + i * w / int(w / 1.2) + 0.03, 0.06, h - 0.25), m("trim"))
            for x in (-w / 2, w / 2):
                g.tube((x, -d, h + 1.0), (x, 0.0, h + 1.0), 0.025, m("metal"), n=4)
        else:
            g.sub(Matrix.Translation((0, 0.0, h / 2)) @ Matrix.Rotation(-math.pi / 2, 4, "X")).cyl(0, 0, min(w, h) * 0.3, 0.0, 0.04, m("glass"), n=14)
            c.glow("ring", (-min(w, h) * 0.3, 0.05, h / 2), min(w, h) * 0.6)
    elif kind == "ring":
        r0 = c.p.get("radius", 12.0)
        ang = w / r0
        n = 6
        pts_o = [((r0 + d) * math.sin(-ang / 2 + ang * k / n), (r0 + d) * math.cos(-ang / 2 + ang * k / n) - r0) for k in range(n + 1)]
        pts_i = [(r0 * math.sin(-ang / 2 + ang * k / n), r0 * math.cos(-ang / 2 + ang * k / n) - r0) for k in range(n + 1)]
        g.extrude_xy(pts_i + list(reversed(pts_o)), 0.0, h, m(role))
        g.extrude_xy(pts_i + list(reversed([(x * (r0 - 1.5) / r0, (y + r0) * (r0 - 1.5) / r0 - r0) for x, y in pts_i])), h - 0.2, h, m("wood"))
    elif kind == "bar":
        g.box((-w / 2, -d, 0.0), (w / 2, 0.0, h), m(role))
        g.box((-w / 2 + 0.3, EPS, 0.035), (w / 2 - 0.3, 0.03, 2.0), m("glass"))
        g.box((-w / 2, EPS, 2.0), (w / 2, 0.6, 2.1), m("roof"))
        g.box((-w / 2 + 0.4, EPS, 2.6), (w / 2 - 0.4, 0.03, 3.6), m("glass"))
        c.sign("chochin", 0.4, 0.6, (w / 2 - 0.4, 0.62, 2.4))
        c.sign("painted", w * 0.7, 0.35, (0.0, 0.62, 2.15))
    elif kind == "basso":
        g.box((-w / 2, -d, 0.0), (w / 2, 0.0, h), m(role))
        g.extrude_xz(arch_outline("rect", w * 0.6, 2.4, 4), EPS, 0.03, m("dark_wood"))
        c.glow("door", (-w * 0.3, 0.04, 2.45), w * 0.6)
        c.sign("lightbox", w * 0.5, 0.4, (0.0, 0.05, 2.7))


# ------------------------------------------------------------------ courts, planters, water, plinths, gates
def court(c):
    """ground pieces: planter | planter_wall (pots hung on a wall) | palm | fountain (a basin and a kiosk) |
    channel (a falaj trough) | charbagh (a quartered court with channels) | plinth (a raised base with steps) |
    pit_rim (a parapet and a fabric canopy round a pit) | gate (a monumental portal) | pishtaq | iwan | muqarnas"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "planter")
    w, h, d = c.w, c.h, c.d
    if k == "planter":
        g.cyl(0, 0, w / 2 * 0.8, 0.035, h * 0.6, m("accent"), n=8, r1=w / 2)
        g.lathe([(w / 2 * 0.9, h * 0.6), (w / 2 * 1.1, h * 0.85), (w * 0.2, h), (0.0, h * 1.05)], m("plant"), n=6)
    elif k == "planter_wall":
        for i in range(5):
            x, z = -w / 2 + 0.15 + (i % 3) * (w - 0.3) / 2, 0.2 + (i // 3) * 0.45 + 0.1 * (i % 2)
            g.box((x - 0.06, EPS, z - 0.02), (x + 0.06, 0.08, z), m("iron"))
            g.cyl(x, 0.13, 0.08, z, z + 0.16, m(["accent", "accent2", "tile"][i % 3]), n=6, r1=0.1)
            g.cyl(x, 0.13, 0.1, z + 0.16, z + 0.3, m("plant"), n=5, r1=0.02)
    elif k == "palm":
        g.cyl(0, 0, w * 0.3, 0.035, 0.5, m("accent"), n=8, r1=w * 0.4)
        g.cyl(0, 0, 0.08, 0.5, h, m("wood"), n=6, r1=0.06)
        for i in range(7):
            a = math.tau * i / 7
            tip = (math.cos(a) * w * 0.8, math.sin(a) * w * 0.8, h - 0.4)
            q = [(0, 0, h), (tip[0] - math.sin(a) * 0.15, tip[1] + math.cos(a) * 0.15, tip[2]), (tip[0] + math.sin(a) * 0.15, tip[1] - math.cos(a) * 0.15, tip[2])]
            g.face(q, m("plant"))
            g.face(list(reversed(q)), m("plant"))
    elif k == "fountain":
        g.cyl(0, 0, w / 2, 0.035, 0.5, m("stone"), n=12)
        g.cyl(0, 0, w / 2 - 0.15, 0.5, 0.52, m("water"), n=12)
        g.cyl(0, 0, 0.12, 0.52, 1.2, m("stone"), n=8)
        g.moved(z=1.2).lathe([(0.45, 0.0), (0.45, 0.08), (0.0, 0.15)], m("stone"), n=10)
    elif k == "channel":
        g.box((-w / 2, -d / 2, 0.035), (w / 2, -d / 2 + 0.1, h), m("stone"))
        g.box((-w / 2, d / 2 - 0.1, 0.035), (w / 2, d / 2, h), m("stone"))
        g.box((-w / 2, -d / 2 + 0.1, 0.035), (w / 2, d / 2 - 0.1, h * 0.6), m("water"))
    elif k == "charbagh":
        g.cbox(0, 0, 0.035, w, w, 0.1, m("stone"))
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.cbox(sx * w / 4, sy * w / 4, 0.135, w / 2 - 0.8, w / 2 - 0.8, 0.12, m("plant"))
        g.cbox(0, 0, 0.135, w, 0.4, 0.04, m("water"))
        g.cbox(0, 0, 0.135, 0.4, w, 0.041, m("water"))
    elif k == "plinth":
        g.box((-w / 2, -d, 0.035), (w / 2, 0.0, h), m("stone"))
        for i in range(int(h / 0.18)):
            g.box((-1.0, 0.0, 0.035), (1.0, 0.3 * (int(h / 0.18) - i), 0.035 + 0.18 * (i + 1)), m("stone"))
    elif k == "pit_rim":
        r = w / 2
        for i in range(16):
            a0, a1 = math.tau * i / 16, math.tau * (i + 1) / 16
            g.tube((r * math.cos(a0), r * math.sin(a0), 0.5), (r * math.cos(a1), r * math.sin(a1), 0.5), 0.12, m("wall"), n=4)
            if i % 4 == 0:
                g.cyl(r * math.cos(a0), r * math.sin(a0), 0.06, 0.035, h, m("wood"), n=6)
        for i in range(4):
            a = math.tau * i / 4
            q = [(r * math.cos(a), r * math.sin(a), h), (r * math.cos(a + math.pi / 2), r * math.sin(a + math.pi / 2), h), (0, 0, h + 0.8)]
            g.face(q, m("fabric"))
            g.face(list(reversed(q)), m("fabric"))
    elif k in ("gate", "pishtaq", "iwan"):
        aw = w * (0.45 if k != "iwan" else 0.7)
        ah = h * (0.62 if k != "iwan" else 0.8)
        inner = arch_outline("pointed" if k != "gate" else "round", aw, ah, 6)
        outer = arch_outline("rect", w, h, 6)
        g.ring_xz(outer, inner, -0.6, 0.0, m(c.p.get("mat", "wall")))
        g.ring_xz(arch_outline("rect", w + 0.4, h + 0.3, 6), arch_outline("rect", w, h, 6), -0.6, 0.12, m("trim"))
        if k == "pishtaq":
            for x in (-w / 2 - 0.4, w / 2 + 0.1):
                g.box((x, -0.6, 0.035), (x + 0.3, 0.14, h + 1.2), m("trim"))
            g.box((-w / 2 - 0.1, EPS, h - 0.9), (w / 2 + 0.1, 0.03, h - 0.1), m("tile"))
        if k == "iwan":
            g.box((-aw / 2, -3.0, 0.035), (aw / 2, -2.9, ah), m("tile"))
        c.glow("outline", (-aw / 2, 0.02, ah + 0.05), aw)
        c.sign("brass", w * 0.6, 0.5, (0.0, 0.13, ah + (h - ah) * 0.35))
    elif k == "muqarnas":
        rows = 5
        for i in range(rows):
            z = h * i / rows
            n = rows - i + 2
            cw = w / n * (1 - i / rows * 0.5)
            for j in range(n):
                x = -cw * n / 2 + (j + 0.5) * cw
                g.moved(x=x, z=z).extrude_xz(arch_outline("pointed", cw * 0.9, h / rows, 2), EPS, d * (1 - i / rows), m("trim" if (i + j) % 2 == 0 else "stone"))
