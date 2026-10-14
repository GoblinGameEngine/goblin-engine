"""Signs, lights, shopfronts and ceilings.  A sign here is its mounting (a board, a bracket, a frame, a catwalk) and
an anchor: SkySigns (godot_project/remake/scripts/sky/sky_signs.gd) puts the lit face, the lettering and the
animation on it at run time.  Lamps are built (a warm emissive glass); strings of lights are anchors (lights_*)."""
import math

from mathutils import Matrix

from .fam_facade import EPS, bracket


# ------------------------------------------------------------------ sign mounts
def sign(c):
    """kind board (a fascia board) | blade (a bracketed vertical blade) | stack (a zakkyo column of lightboxes, one a
    floor) | lightbox | corner (a lightbox wrapping a corner) | neon (a dark frame for a tube outline) | painted (a
    painted board with a gooseneck lamp) | billboard (a rooftop frame with a catwalk and lamps) | letters (rooftop
    letters on a frame) | directory | dotmatrix | video | brass (halo-lit letters: a rail and the anchor) |
    nameboard | figure (a pedestal for a giant figure sign)"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "board")
    w, h = c.w, c.h
    if k == "board":
        g.box((-w / 2, EPS, 0.0), (w / 2, 0.06, h), m("dark_wood"))
        g.box((-w / 2 - 0.04, EPS, -0.04), (w / 2 + 0.04, 0.08, 0.0), m("trim"))
        c.sign("lightbox", w - 0.1, h - 0.1, (0.0, 0.065, 0.05))
    elif k == "blade":
        out = c.p.get("out", 0.25)
        for z in (h * 0.15, h * 0.85):
            g.box((-0.04, EPS, z - 0.04), (0.04, out + 0.05, z + 0.04), m("iron"))
        f = g.sub(Matrix.Translation((0, out + 0.05 + w / 2, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
        f.box((-w / 2, -0.06, 0.0), (w / 2, 0.06, h), m("neon_tube"))
        c.sign_at(f, "blade", w, h, (0.0, 0.065, 0.0))
    elif k == "stack":
        n = c.p.get("floors", max(1, int(h / 1.25)))
        g.box((-0.05, EPS, 0.0), (0.05, 0.4, h), m("iron"))
        f = g.sub(Matrix.Translation((0, 0.4 + w / 2, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
        ph = h / n
        for i in range(n):
            f.box((-w / 2, -0.1, i * ph + 0.04), (w / 2, 0.1, (i + 1) * ph - 0.04), m("neon_tube"))
            c.sign_at(f, "lightbox", w - 0.06, ph - 0.14, (0.0, 0.105, i * ph + 0.07))
    elif k in ("lightbox", "corner", "dotmatrix", "video", "directory"):
        dp = {"video": 0.3, "dotmatrix": 0.18}.get(k, 0.22)
        g.box((-w / 2, EPS, 0.0), (w / 2, dp, h), m("neon_tube"))
        if k == "corner":
            g.box((w / 2 - dp, EPS, 0.0), (w / 2, dp + w * 0.4, h), m("neon_tube"))
        c.sign({"lightbox": "lightbox", "corner": "lightbox", "dotmatrix": "dotmatrix", "video": "video", "directory": "lightbox"}[k],
               w - 0.08, h - 0.08, (0.0, dp + 0.005, 0.04))
    elif k == "neon":
        t = 0.06
        g.box((-w / 2, EPS, 0.0), (w / 2, 0.05, t), m("neon_tube"))
        g.box((-w / 2, EPS, h - t), (w / 2, 0.05, h), m("neon_tube"))
        g.box((-w / 2, EPS, t), (-w / 2 + t, 0.05, h - t), m("neon_tube"))
        g.box((w / 2 - t, EPS, t), (w / 2, 0.05, h - t), m("neon_tube"))
        c.sign("neon", w - 0.2, h - 0.2, (0.0, 0.055, 0.1))
    elif k == "painted":
        g.box((-w / 2, EPS, 0.0), (w / 2, 0.05, h), m("wood"))
        g.box((-w / 2 - 0.03, EPS, -0.03), (w / 2 + 0.03, 0.06, 0.0), m("dark_wood"))
        for x in (-w / 3, w / 3):
            g.tube((x, 0.05, h + 0.05), (x, 0.35, h + 0.25), 0.012, m("iron"), n=4)
            g.box((x - 0.09, 0.3, h + 0.15), (x + 0.09, 0.42, h + 0.25), m("lamp"))
        c.sign("painted", w - 0.06, h - 0.06, (0.0, 0.055, 0.03))
    elif k in ("billboard", "letters"):
        legs = max(2, int(w / 3) + 1)
        for i in range(legs):
            x = -w / 2 + 0.2 + (w - 0.4) * i / (legs - 1)
            g.box((x - 0.08, -1.2, 0.0), (x + 0.08, -1.04, 1.0), m("iron"))
            g.tube((x, -1.12, 1.0), (x, -0.05, h + 1.0), 0.05, m("iron"), n=4)
            g.box((x - 0.06, -0.12, 0.0), (x + 0.06, 0.0, h + 1.0), m("iron"))
        if k == "billboard":
            g.box((-w / 2, 0.0, 1.0), (w / 2, 0.1, h + 1.0), m("neon_tube"))
            g.box((-w / 2, 0.1, 0.9), (w / 2, 0.9, 0.96), m("iron"))
            for i in range(int(w / 2.5) + 1):
                x = -w / 2 + 0.3 + i * (w - 0.6) / max(1, int(w / 2.5))
                g.tube((x, 0.15, 0.95), (x, 0.9, 1.2), 0.02, m("iron"), n=4)
                g.box((x - 0.12, 0.85, 1.15), (x + 0.12, 1.0, 1.3), m("lamp"))
            c.sign("billboard", w - 0.2, h - 0.2, (0.0, 0.105, 1.1))
        else:
            g.box((-w / 2, -0.12, 1.0), (w / 2, 0.0, 1.1), m("iron"))
            c.sign("brass", w, h, (0.0, 0.02, 1.1))
    elif k == "brass":
        g.box((-w / 2, EPS, h * 0.45), (w / 2, 0.03, h * 0.55), m("metal"))
        c.sign("brass", w, h, (0.0, 0.035, 0.0))
    elif k == "nameboard":
        g.box((-w / 2, EPS, 0.0), (w / 2, 0.04, h), m("wood"))
        g.tube((0, 0.04, h + 0.05), (0, 0.3, h + 0.2), 0.012, m("iron"), n=4)
        g.box((-0.08, 0.24, h + 0.1), (0.08, 0.36, h + 0.22), m("lamp"))
        c.sign("painted", w - 0.04, h - 0.04, (0.0, 0.045, 0.02))
    elif k == "figure":
        g.cbox(0, 0, 0.0, w, max(0.8, c.d), 0.8, m("stone"))
        c.sign("figure", w, h, (0.0, 0.0, 0.8))


# ------------------------------------------------------------------ lamps
def lamp(c):
    """a lamp (built, warm emissive): kind lantern (a hanging lantern on a bracket) | paper (a paper lantern) | star
    (a pierced star lantern) | star_paper | wall (an iron wall lantern) | cn (a round silk lantern with a tassel) |
    post (a Victorian lamp post) | tube (a bare fluorescent tube) | shrine (a lit wall niche)"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "lantern")
    w, h = c.w, c.h
    if k in ("lantern", "paper", "cn", "star", "star_paper"):
        arm = c.p.get("arm", 0.45)
        g.box((-0.03, EPS, h + 0.15), (0.03, arm, h + 0.2), m("iron"))
        g.tube((0, arm - 0.03, h + 0.15), (0, arm - 0.03, h), 0.006, m("iron"), n=4)
        cy = arm - 0.03
        if k in ("paper", "cn"):
            g.moved(y=cy).lathe([(w * 0.25, h * 0.0), (w * 0.5, h * 0.25), (w * 0.52, h * 0.5), (w * 0.5, h * 0.75), (w * 0.25, h)], m("lamp"), n=10)
            if k == "cn":
                g.tube((0, cy, 0.0), (0, cy, -0.25), 0.02, m("accent"), n=4)
        elif k in ("star", "star_paper"):
            s = g.moved(y=cy, z=h * 0.5)
            for i in range(6):
                a = math.tau * i / 6
                s.tube((0, 0, 0), (math.cos(a) * w * 0.55, 0.0, math.sin(a) * w * 0.55), w * 0.12, m("lamp" if k == "star_paper" else "metal"), n=4)
            s.lathe([(0.0, -w * 0.25), (w * 0.25, 0.0), (0.0, w * 0.25)], m("lamp"), n=6)
        else:
            g.moved(y=cy).lathe([(w * 0.3, 0.0), (w * 0.45, h * 0.15), (w * 0.45, h * 0.75), (w * 0.15, h * 0.95), (0.0, h)], m("lamp"), n=6)
            g.moved(y=cy, z=h * 0.72).lathe([(w * 0.5, 0.0), (w * 0.2, h * 0.25), (0.0, h * 0.28)], m("iron"), n=6)
    elif k == "wall":
        g.box((-0.08, EPS, 0.0), (0.08, 0.04, h), m("iron"))
        g.box((-0.12, 0.08, h * 0.2), (0.12, 0.3, h * 0.75), m("lamp"))
        g.box((-0.15, 0.06, h * 0.75), (0.15, 0.32, h * 0.82), m("iron"))
    elif k == "post":
        g.lathe([(0.12, 0.035), (0.1, 0.3), (0.06, 0.45), (0.05, h - 0.6), (0.07, h - 0.5)], m("iron"), n=8)
        g.moved(z=h - 0.5).lathe([(0.12, 0.0), (0.2, 0.3), (0.18, 0.42), (0.0, 0.6)], m("lamp"), n=6)
    elif k == "tube":
        g.box((-w / 2, EPS, 0.0), (w / 2, 0.06, 0.05), m("metal"))
        g.tube((-w / 2 + 0.05, 0.06, 0.025), (w / 2 - 0.05, 0.06, 0.025), 0.016, m("lamp"), n=6)
    elif k == "shrine":
        g.box((-w / 2, EPS, 0.0), (w / 2, c.d, h), m("trim"))
        g.box((-w / 2 + 0.06, c.d - 0.02, 0.15), (w / 2 - 0.06, c.d + 0.004, h - 0.2), m("lamp"))
        g.moved(z=h).extrude_xz([(-w / 2 - 0.05, 0.0), (w / 2 + 0.05, 0.0), (0.0, 0.2)], EPS, c.d + 0.06, m("roof"))


def lights(c):
    """strings and runs of light (anchors only, plus their little fixings): kind festoon (a bulb catenary between
    two points) | fairy (along a rail) | jhalar (a curtain of bulbs down a facade: several drops) | outline (a run
    along an edge) | projection (an uplight) | led (an LED strip) | chaser | eave (bulbs along an eave) | marquee (a
    bulb border) | bunting | luminarie (a bulb arch on a timber frame) | neon (a neon run)"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "festoon")
    w, h = c.w, c.h
    if k in ("festoon", "fairy", "bunting"):
        for x in (-w / 2, w / 2):
            g.box((x - 0.03, EPS, -0.03), (x + 0.03, 0.08, 0.03), m("iron"))
        c.lights((-w / 2, 0.08, 0.0), (w / 2, 0.08, 0.0))
    elif k == "jhalar":
        n = max(2, int(w / 0.4))
        g.box((-w / 2, EPS, -0.02), (w / 2, 0.05, 0.02), m("iron"))
        for i in range(n):
            x = -w / 2 + (i + 0.5) * w / n
            c.glow("drop", (x, 0.06, 0.0), h, vertical=True)
    elif k in ("outline", "led", "chaser", "eave", "marquee", "neon"):
        g.box((-w / 2, EPS, -0.02), (w / 2, 0.025, 0.02), m("neon_tube" if k in ("neon", "led", "chaser") else "iron"))
        c.glow({"outline": "outline", "led": "led", "chaser": "chase", "eave": "eave", "marquee": "marquee", "neon": "neon"}[k],
               (-w / 2, 0.03, 0.0), w)
    elif k == "projection":
        g.box((-0.15, EPS, 0.0), (0.15, 0.2, 0.2), m("iron"))
        g.box((-0.12, 0.2, 0.03), (0.12, 0.22, 0.17), m("lamp"))
        c.glow("uplight", (0.0, 0.25, 0.2), h)
    elif k == "luminarie":
        for x in (-w / 2, w / 2):
            g.box((x - 0.06, -0.06, 0.035), (x + 0.06, 0.06, h * 0.75), m("wood"))
        prev = None
        for i in range(13):
            t = math.pi * i / 12
            p = (w / 2 * math.cos(t), 0.0, h * 0.75 + h * 0.25 * math.sin(t))
            if prev:
                g.tube(prev, p, 0.04, m("wood"), n=4)
                c.glow("arch", prev, math.dist(prev, p), along=p)
            prev = p


# ------------------------------------------------------------------ shopfronts
def shopfront(c):
    """a shop bay on the ground floor: an opening, its frame, a fascia with the sign anchor, and a front: shutter (a
    rolling steel shutter, half up) | glass | noren (split cloth curtains over the door) | open (a basso: the room
    open to the lane) | stall (a counter out front)"""
    g, m = c.g, c.m
    k = c.p.get("kind", c.v or "shutter")
    w, h = c.w, c.h
    oh = h - 0.9
    fr = 0.12
    z0 = 0.035                                   # (just off grade: the kit can share it)
    g.box((-w / 2, EPS, z0), (-w / 2 + fr, 0.1, oh), m("trim"))
    g.box((w / 2 - fr, EPS, z0), (w / 2, 0.1, oh), m("trim"))
    g.box((-w / 2, EPS, oh), (w / 2, 0.14, h), m("dark_wood"))
    c.sign(c.p.get("sign", "lightbox"), w - 0.3, h - oh - 0.2, (0.0, 0.145, oh + 0.1))
    ow = w - 2 * fr
    if k in ("shutter", "glass", "noren", "stall"):
        g.box((-ow / 2, -0.06, z0), (ow / 2, -0.045, oh - 0.02), m("glass"))
        g.box((-0.02, -0.045, z0), (0.02, -0.02, oh - 0.02), m("trim"))
    if k == "shutter":
        up = c.p.get("up", 0.55)
        sz = z0 + (oh - z0) * up
        g.box((-ow / 2, 0.02, oh - 0.35), (ow / 2, 0.16, oh), m("metal"))
        for i in range(int((oh - 0.35 - sz) / 0.09)):
            z = sz + i * 0.09
            g.box((-ow / 2, 0.06, z), (ow / 2, 0.075, z + 0.08), m("metal"))
    elif k == "noren":
        n = 3
        for i in range(n):
            x0 = -0.45 + 0.9 * i / n
            q = [(x0 + 0.01, 0.12, oh - 0.9), (x0 + 0.3 - 0.01, 0.12, oh - 0.9), (x0 + 0.3 - 0.01, 0.12, oh - 0.05), (x0 + 0.01, 0.12, oh - 0.05)]
            g.face(q, m("fabric"))
            g.face(list(reversed(q)), m("fabric"))
        g.tube((-0.5, 0.12, oh - 0.05), (0.5, 0.12, oh - 0.05), 0.015, m("wood"), n=4)
    elif k == "stall":
        g.box((-ow / 2, 0.1, z0), (ow / 2, 0.7, 0.9), m("wood"))
        g.box((-ow / 2 - 0.05, 0.1, 0.9), (ow / 2 + 0.05, 0.75, 0.95), m("wood"))
    elif k == "open":
        g.box((-ow / 2, -2.4, z0), (ow / 2, -2.38, oh), m("wall2"))
        c.glow("door", (-ow / 2, 0.02, oh - 0.05), ow)


# ------------------------------------------------------------------ ceilings
CEILINGS = ("suspended_grid_600", "pressed_tin", "artesonado_coffer", "batten", "coffered", "painted_plaster")


def ceiling_module(c):
    """one ceiling module, hung from z 0 down (the room's ceiling height): w x d.  variants:
       suspended_grid_600  0.6 m mineral tiles in a T-bar grid (the tiles 6 mm above the tees' faces)
       pressed_tin         0.6 m tin tiles: a raised border, a raised centre boss and four petals, a cornice ledge
       artesonado_coffer   interlaced timber: a lattice of beams, an eight-point star boss in each coffer
       batten              sao-buchi: boards along d with battens across every 0.455 m
       coffered            goutenjou: 0.9 m coffers between deep crossed beams
       painted_plaster     a plaster slab with a painted rosette and a moulded border"""
    g, m = c.g, c.m
    v = c.v if c.v in CEILINGS else "suspended_grid_600"
    w, d = c.w, c.d
    if v == "suspended_grid_600":
        g.box((-w / 2, -d / 2, -0.016), (w / 2, d / 2, 0.0), m("ceiling"))            # the tile (in the grid's frame)
        for x in (-w / 2, w / 2 - 0.024):
            g.box((x, -d / 2, -0.022), (x + 0.024, d / 2, -0.016), m("metal"))
        for y in (-d / 2, d / 2 - 0.024):
            g.box((-w / 2 + 0.024, y, -0.022), (w / 2 - 0.024, y + 0.024, -0.016), m("metal"))
    elif v == "pressed_tin":
        # a 0.6 tin tile: a raised rim, a sunk field, a raised inner square on the diagonal, a boss and four petals
        g.box((-w / 2, -d / 2, -0.012), (w / 2, d / 2, 0.0), m("ceiling2"))
        b = 0.06
        for (x0, y0, x1, y1) in ((-w / 2, -d / 2, w / 2, -d / 2 + b), (-w / 2, d / 2 - b, w / 2, d / 2),
                                 (-w / 2, -d / 2 + b, -w / 2 + b, d / 2 - b), (w / 2 - b, -d / 2 + b, w / 2, d / 2 - b)):
            g.box((x0, y0, -0.032), (x1, y1, -0.012), m("ceiling2"))
        s_ = g.moved(z=-0.012, rz=math.pi / 4)
        q = min(w, d) * 0.28
        for (x0, y0, x1, y1) in ((-q, -q, q, -q + 0.03), (-q, q - 0.03, q, q), (-q, -q + 0.03, -q + 0.03, q - 0.03), (q - 0.03, -q + 0.03, q, q - 0.03)):
            s_.box((x0, y0, -0.022), (x1, y1, 0.0), m("ceiling2"))
        g.moved(z=-0.012).lathe([(0.0, -0.06), (0.07, -0.045), (0.11, -0.015), (0.12, 0.0)], m("ceiling2"), n=10)
        for a in range(4):
            p_ = g.moved(z=-0.012, rz=a * math.pi / 2)
            p_.extrude_xy([(0.13, 0.0), (0.2, -0.045), (0.26, 0.0), (0.2, 0.045)], -0.028, 0.0, m("ceiling2"))
    elif v == "artesonado_coffer":
        g.box((-w / 2, -d / 2, -0.02), (w / 2, d / 2, 0.0), m("dark_wood"))
        bw = 0.09
        for x in (-w / 2, w / 2 - bw):
            g.box((x, -d / 2, -0.12), (x + bw, d / 2, -0.02), m("wood"))
        for y in (-d / 2, d / 2 - bw):
            g.box((-w / 2 + bw, y, -0.12), (w / 2 - bw, y + bw, -0.02), m("wood"))
        s = g.moved(z=-0.02)
        for a in (0.0, math.pi / 4):
            s.sub(Matrix.Rotation(a, 4, "Z")).box((-0.13, -0.13, -0.05), (0.13, 0.13, 0.0), m("accent"))
        s.lathe([(0.0, -0.09), (0.05, -0.05), (0.06, -0.03)], m("metal"), n=8)
    elif v == "batten":
        g.box((-w / 2, -d / 2, -0.015), (w / 2, d / 2, 0.0), m("wood"))
        for i in range(max(1, int(round(d / 0.455)))):
            y = -d / 2 + (i + 0.5) * d / max(1, int(round(d / 0.455)))
            g.box((-w / 2, y - 0.02, -0.055), (w / 2, y + 0.02, -0.015), m("dark_wood"))
    elif v == "coffered":
        g.box((-w / 2, -d / 2, -0.02), (w / 2, d / 2, 0.0), m("wood"))
        bw = 0.06
        for x in (-w / 2, w / 2 - bw):
            g.box((x, -d / 2, -0.16), (x + bw, d / 2, -0.02), m("dark_wood"))
        for y in (-d / 2, d / 2 - bw):
            g.box((-w / 2 + bw, y, -0.16), (w / 2 - bw, y + bw, -0.02), m("dark_wood"))
        for x in (-w / 4, 0.0, w / 4):
            g.box((x - 0.012, -d / 2 + bw, -0.045), (x + 0.012, d / 2 - bw, -0.02), m("dark_wood"))
    elif v == "painted_plaster":
        g.box((-w / 2, -d / 2, -0.02), (w / 2, d / 2, 0.0), m("ceiling"))
        g.moved(z=-0.02).lathe([(0.0, -0.004), (0.3, -0.004), (0.32, 0.0)], m("accent"), n=12)
        for x in (-w / 2, w / 2 - 0.05):
            g.box((x, -d / 2, -0.06), (x + 0.05, d / 2, -0.02), m("ceiling"))
