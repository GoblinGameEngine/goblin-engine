"""
gbbridge.py -- crossings for the remake: local terrain (creek channel, banks, approach
grading, water), roads/track, and the structure types used by the real examples:
riveted Warren pony truss, masonry arch culvert under a railroad embankment, reinforced
concrete box culvert with solid railings.  Road/track runs along +Y, the creek along X.
"""
import math

from mathutils import Vector

import gblib as g


def creek_terrain(b, L, W, ch_w, depth, bank_w, top_z=0.0, embank=None, name="terrain", zfunc=None, extra_xs=(), extra_ys=()):
    """Ground patch x in [-W/2, W/2], y in [-L/2, L/2]: flat at top_z, a creek channel along X
    (bed ch_w wide at -depth, banks bank_w wide).  embank=(half_width, height): a road/rail
    embankment crest along Y (for the arch culvert).  Returns the height function."""
    def z_at(x, y):
        a = abs(y)
        if a <= ch_w / 2:
            z = top_z - depth
        elif a <= ch_w / 2 + bank_w:
            t = (a - ch_w / 2) / bank_w
            z = top_z - depth * (1 - t * t * (3 - 2 * t))
        else:
            z = top_z
        if embank:
            hw, h = embank
            ax = abs(x)
            if ax <= hw:
                z = max(z, top_z + h)
            elif ax <= hw + h * 1.5:
                z = max(z, top_z + h - (ax - hw) / 1.5)
        return z
    if zfunc:
        z_at = zfunc
    p = b.part(f"{name}-col")
    nx, ny = 24, 48
    xs = sorted(set([-W / 2 + W * i / nx for i in range(nx + 1)] + list(extra_xs)))
    ys = sorted(set([-L / 2 + L * j / ny for j in range(ny + 1)] + [s * (ch_w / 2 + k * bank_w / 4) for s in (-1, 1) for k in range(5)]
                    + list(extra_ys)))
    nx = len(xs) - 1
    for i in range(nx):
        for j in range(len(ys) - 1):
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            q = [(x0, y0, z_at(x0, y0)), (x1, y0, z_at(x1, y0)), (x1, y1, z_at(x1, y1)), (x0, y1, z_at(x0, y1))]
            ym = (y0 + y1) / 2
            mat = "creekbed" if abs(ym) < ch_w / 2 + 0.3 else ("bank" if abs(ym) < ch_w / 2 + bank_w else "grass")
            p.face(q, mat)
    return z_at


def water(b, x0, x1, y0, y1, z):
    p = b.part("water")
    p.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], "water")


def road(b, y0, y1, w, z=0.0, shoulder=1.0, name="road", centerline=True):
    p = b.part(f"{name}-col")
    p.box((-w / 2, y0, z - 0.3), (w / 2, y1, z + 0.02), "asphalt", mats={"z": "asphalt"})
    for s in (-1, 1):
        p.box((min(s * w / 2, s * (w / 2 + shoulder)), y0, z - 0.3), (max(s * w / 2, s * (w / 2 + shoulder)), y1, z), "ballast")
    if centerline:
        m = b.part("road_marks")
        y = y0 + 0.5
        while y < y1 - 3.0:
            m.box((-0.06, y, z + 0.021), (0.06, y + 3.0, z + 0.023), "paint_yellow")
            y += 12.0


def guardrail(b, pts, z=0.0, name="guardrail"):
    """W-beam guardrail on wood posts along a polyline."""
    p = b.part(f"{name}-col")
    for a, c in zip(pts, pts[1:]):
        A, C = Vector((a[0], a[1], 0)), Vector((c[0], c[1], 0))
        L = (C - A).length
        u = (C - A).normalized()
        v = Vector((-u.y, u.x, 0))
        F = (A, u, v, Vector((0, 0, 1)))
        p.obox(F, (0, -0.02, z + 0.45), (L, 0.02, z + 0.75), "guardrail")
        n = max(1, int(L / 1.9))
        for k in range(n + 1):
            s = L * k / n
            p.obox(F, (s - 0.08, 0.02, z - 0.6), (s + 0.08, 0.2, z + 0.7), "ties")


def pony_truss(b, span, width, height, panels, z_deck=0.0, name="truss"):
    """Riveted Warren pony truss with verticals (HAER IL-118 type): two trusses at x=+-width/2,
    inclined end posts, top/bottom chords, alternating diagonals, verticals, gusset plates,
    floor beams + concrete deck with curbs, bearings."""
    p = b.part(f"{name}-col")
    pl = span / panels
    y0 = -span / 2
    for sx in (-1, 1):
        x = sx * width / 2
        bot = [(x, y0 + k * pl, z_deck) for k in range(panels + 1)]
        top = [(x, y0 + k * pl, z_deck + height) for k in range(1, panels)]
        # bottom chord (channel box)
        p.box((x - 0.15, y0, z_deck - 0.35), (x + 0.15, -y0, z_deck + 0.05), "truss")
        # top chord between the first and last upper panel points
        p.box((x - 0.18, top[0][1], top[0][2] - 0.1), (x + 0.18, top[-1][1], top[0][2] + 0.22), "truss")
        # end posts (inclined)
        for (lo, hi) in ((bot[0], top[0]), (bot[-1], top[-1])):
            strut(p, lo, hi, 0.34, 0.26, "truss")
        # verticals at every inner panel point, Warren diagonals between
        for k in range(1, panels):
            strut(p, (x, y0 + k * pl, z_deck), (x, y0 + k * pl, z_deck + height), 0.14, 0.18, "truss")
        for k in range(1, panels - 1):
            if k % 2 == 1:
                strut(p, (x, y0 + k * pl, z_deck + height), (x, y0 + (k + 1) * pl, z_deck), 0.16, 0.16, "truss")
            else:
                strut(p, (x, y0 + k * pl, z_deck), (x, y0 + (k + 1) * pl, z_deck + height), 0.16, 0.16, "truss")
        # gusset plates at panel points (slightly proud, both faces)
        for k in range(panels + 1):
            yy = y0 + k * pl
            for zz in ((z_deck,) + ((z_deck + height,) if 0 < k < panels else ())):
                p.box((x - 0.2, yy - 0.35, zz - 0.3), (x + 0.2, yy + 0.35, zz + 0.3), "truss")
    # floor beams + deck + curbs
    for k in range(panels + 1):
        yy = y0 + k * pl
        p.box((-width / 2, yy - 0.15, z_deck - 0.75), (width / 2, yy + 0.15, z_deck - 0.3), "truss")
    p.box((-width / 2 + 0.2, y0, z_deck - 0.3), (width / 2 - 0.2, -y0, z_deck), "concrete", mats={"z": "asphalt"})
    for sx in (-1, 1):
        p.box((sx * (width / 2 - 0.2) - (0.3 if sx > 0 else 0), y0, z_deck), (sx * (width / 2 - 0.2) + (0 if sx > 0 else 0.3), -y0, z_deck + 0.25), "concrete")
    return pl


def strut(p, a, c, w, d, mat):
    """Rectangular member from a to c (w across the truss plane normal X, d in-plane)."""
    A, C = Vector(a), Vector(c)
    ax = (C - A)
    L = ax.length
    u = ax.normalized()
    side = Vector((1, 0, 0))
    v = u.cross(side).normalized()
    o = A
    F = (o, u, side, v)
    p.obox(F, (0, -w / 2, -d / 2), (L, w / 2, d / 2), mat)


def abutment(b, y, s, width, top_z, bed_z, name):
    """Concrete abutment + flared wingwalls at y (s = +1 north end, -1 south end)."""
    p = b.part(f"{name}-col")
    p.box((-width / 2 - 0.6, min(y, y + s * 1.2), bed_z - 0.3), (width / 2 + 0.6, max(y, y + s * 1.2), top_z - 0.3), "concrete_old")
    for sx in (-1, 1):
        p.box((sx * (width / 2 + 0.6) - (0.35 if sx > 0 else 0), min(y, y + s * 4.0), bed_z - 0.3),
              (sx * (width / 2 + 0.6) + (0 if sx > 0 else 0.35), max(y, y + s * 4.0), top_z + 0.3), "concrete_old")


def track(b, y0, y1, z, name="track"):
    """Ballasted single track along Y: ballast prism, ties at 0.5 m, two rails."""
    p = b.part(f"{name}-col")
    p.box((-1.8, y0, z - 0.4), (1.8, y1, z), "ballast")
    t = b.part(f"{name}_ties")
    y = y0 + 0.25
    while y < y1 - 0.2:
        t.box((-1.3, y - 0.11, z), (1.3, y + 0.11, z + 0.17), "ties")
        y += 0.5
    for sx in (-0.72, 0.72):
        t.box((sx - 0.035, y0, z + 0.17), (sx + 0.035, y1, z + 0.32), "rail")
        t.box((sx - 0.07, y0, z + 0.17), (sx + 0.07, y1, z + 0.19), "rail")


def arch_barrel(b, span, rise_z, length, bed_z, name="arch", ring_mat="ashlar", face_mat="ashlar"):
    """Semicircular masonry barrel along X (creek direction), springing at bed_z+0.9, with its
    voussoir face ring and headwalls at both ends (x = +-length/2)."""
    p = b.part(f"{name}-col")
    r = span / 2
    spring = bed_z + 0.9
    n = 16
    # barrel intrados (inside surface), faces pointing inward
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        ya, yb = r * math.cos(a0), r * math.cos(a1)
        za, zb = spring + r * math.sin(a0), spring + r * math.sin(a1)
        q = [(-length / 2, ya, za), (length / 2, ya, za), (length / 2, yb, zb), (-length / 2, yb, zb)]
        p.face(q[::-1], ring_mat)
    # side walls below the springing
    for s in (-1, 1):
        p.box((-length / 2, min(s * r, s * (r + 0.6)), bed_z),
              (length / 2, max(s * r, s * (r + 0.6)), spring), ring_mat)
    # headwalls (with the arch opening) at both ends, voussoir rings, coping
    for sx in (-1, 1):
        x = sx * length / 2
        ring = b.part(f"{name}_face-col")
        for k in range(n):
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            pts_in = [(r * math.cos(a0), spring + r * math.sin(a0)), (r * math.cos(a1), spring + r * math.sin(a1))]
            pts_out = [((r + 0.55) * math.cos(a0), spring + (r + 0.55) * math.sin(a0)), ((r + 0.55) * math.cos(a1), spring + (r + 0.55) * math.sin(a1))]
            q = [(x, pts_in[0][0], pts_in[0][1]), (x, pts_in[1][0], pts_in[1][1]), (x, pts_out[1][0], pts_out[1][1]), (x, pts_out[0][0], pts_out[0][1])]
            ring.face(q if sx > 0 else q[::-1], "arch_brick" if face_mat == "brick" else ring_mat)
        # spandrel wall up to the parapet, left and right of the ring (built as vertical strips)
        top = rise_z
        m = 12
        for k in range(m):
            y_a = -(r + 0.55) - 3.0 + (2 * (r + 0.55) + 6.0) * k / m
            y_b = -(r + 0.55) - 3.0 + (2 * (r + 0.55) + 6.0) * (k + 1) / m
            ym = (y_a + y_b) / 2
            if abs(ym) < r + 0.55:
                zb_ = spring + math.sqrt(max(0.0, (r + 0.55) ** 2 - ym ** 2))
            else:
                zb_ = bed_z - 0.3
            q = [(x, y_a, zb_), (x, y_b, zb_), (x, y_b, top), (x, y_a, top)]
            ring.face(q if sx > 0 else q[::-1], face_mat)
        ring.box((min(x, x + sx * 0.5), -(r + 3.6), top), (max(x, x + sx * 0.5), r + 3.6, top + 0.3), "concrete_old")
    return spring


def box_culvert(b, cells, cell_w, cell_h, barrel, deck_w, bed_z, wall_t=0.25, name="culvert"):
    """Reinforced-concrete multi-cell box culvert, barrel along X (creek), road on top along Y."""
    p = b.part(f"{name}-col")
    total = cells * cell_w + (cells + 1) * wall_t
    y0 = -total / 2
    top = bed_z + cell_h + 0.3
    p.box((-barrel / 2, y0, bed_z - 0.3), (barrel / 2, -y0, bed_z), "concrete")               # floor slab
    p.box((-barrel / 2, y0, bed_z + cell_h), (barrel / 2, -y0, top), "concrete")              # top slab
    for k in range(cells + 1):
        yw = y0 + k * (cell_w + wall_t)
        p.box((-barrel / 2, yw, bed_z), (barrel / 2, yw + wall_t, bed_z + cell_h), "concrete")
    # headwalls + wingwalls at both ends
    for sx in (-1, 1):
        x = sx * barrel / 2
        p.box((min(x, x + sx * 0.3), y0 - 0.2, top - 0.05), (max(x, x + sx * 0.3), -y0 + 0.2, top + 0.35), "concrete")
        for s in (-1, 1):
            yy = s * (total / 2)
            p.box((min(x, x + sx * 2.2), min(yy, yy + s * 0.3), bed_z - 0.3), (max(x, x + sx * 2.2), max(yy, yy + s * 0.3), top), "concrete")
    return top, total


def bridge_materials(b, texdir_names=("truss", "concrete", "concrete_old", "ashlar", "arch_brick", "ballast", "asphalt", "ties",
                                      "creekbed", "bank", "guardrail", "grass")):
    # grass is the site's own texture (copied from p-site) at the site's tiling, so the creek
    # patches meet the village ground without a colour seam
    tiles = {"asphalt": 3.0, "ballast": 2.0, "creekbed": 2.0, "bank": 2.0, "ashlar": 2.0, "ties": 2.6, "concrete": 2.0,
             "concrete_old": 2.0, "grass": 4.0}
    for n in texdir_names:
        b.mat(n, tex=n, tile_m=tiles.get(n, 1.0))
    for k, c, r, m in (("rail", (0.35, 0.3, 0.27), 0.4, 0.9),
                       ("paint_yellow", (0.9, 0.72, 0.12), 0.6, 0.0), ("sign_green", (0.05, 0.35, 0.18), 0.4, 0.0),
                       ("sign_white", (0.95, 0.95, 0.93), 0.4, 0.0), ("sign_black", (0.04, 0.04, 0.04), 0.5, 0.0),
                       ("post_steel", (0.6, 0.62, 0.64), 0.4, 0.9), ("plate_bronze", (0.5, 0.36, 0.18), 0.35, 0.9)):
        b.mat(k, color=c, rough=r, metal=m)
    b.mat("water", color=(0.18, 0.28, 0.25), rough=0.05, alpha=0.75)
    b.mat("glass", color=(0.7, 0.8, 0.85), rough=0.05, alpha=0.2)


def post_sign(b, name, x, y, face_yaw, lines, board=(1.0, 0.6), board_mat="sign_white", text_mat="sign_black", height=2.1,
              font_bold=True):
    """Road sign on a steel post: board + lettering lines [(text, size), ...] facing face_yaw (0 = facing -Y)."""
    p = b.part(f"{name}-col")
    ca, sa = math.cos(face_yaw), math.sin(face_yaw)
    p.box((x - 0.04, y - 0.04, 0.0), (x + 0.04, y + 0.04, height + board[1] / 2), "post_steel")
    bw, bh = board
    nrm = Vector((sa, -ca, 0))              # outward normal of the board face
    side = Vector((ca, sa, 0))
    o = Vector((x, y, height)) + nrm * 0.05
    F = (o, side, -nrm, Vector((0, 0, 1)))
    p.obox(F, (-bw / 2, -0.02, -bh / 2), (bw / 2, 0.0, bh / 2), board_mat)
    total = sum(sz * 1.3 for _, sz in lines)
    z = height + total / 2
    font = "/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf" if font_bold else None
    for i, (t, sz) in enumerate(lines):
        z -= sz * 1.3
        loc = o + nrm * 0.003 + Vector((0, 0, z - height + sz * 0.15))
        g.text_mesh(b, f"sign_{name}_{i}", t, sz, tuple(loc), face_yaw, text_mat, extrude=0.002, font=font)
