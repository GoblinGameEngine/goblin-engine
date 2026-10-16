"""p_local.py -- the local market: shed bays and their ends, roll shutters, day-vendor tables and pop-up canopies,
display furniture, goods clusters (goods atlas cards), the 9 m lot pole, lot paint and kerbs.

Every builder is b(q): q=1 the full piece, q=0 its MID (fewer sides, small parts dropped)."""
import math

from mk import B, Mesh, V, box2, card, festoon, flat_poly, piece, prism_zy, rot_y, sweep, place  # noqa: F401

# ------------------------------------------------------------------ the shed (12 m wide, 3 m bays along z)
SH_EAVE_X, SH_EAVE_Y, SH_RIDGE = 6.2, 3.6, 5.3
SH_SLOPE = (SH_RIDGE - SH_EAVE_Y) / SH_EAVE_X


def roof_under(x):
    """the shed roof's underside height at x"""
    return SH_RIDGE - SH_SLOPE * abs(x)


def _shed_roof(m, z0, z1, q):
    t = 0.07
    sec = [(-SH_EAVE_X - 0.05, SH_EAVE_Y - 0.014), (0.0, SH_RIDGE), (SH_EAVE_X + 0.05, SH_EAVE_Y - 0.014),
           (SH_EAVE_X + 0.05, SH_EAVE_Y - 0.014 + t), (0.0, SH_RIDGE + t), (-SH_EAVE_X - 0.05, SH_EAVE_Y - 0.014 + t)]
    m.prism_xy(sec, [], z0, z1, "roof")
    if q:
        top = lambda x: SH_RIDGE + t - SH_SLOPE * abs(x)  # noqa: E731
        for k in range(1, 12):                                  # standing seams down both slopes
            for sg in (-1, 1):
                xa, xb = sg * 0.5 * k, sg * (0.5 * k + 0.06)
                m.prism_xy([(xa, top(xa)), (xb, top(xb)), (xb, top(xb) + 0.035), (xa, top(xa) + 0.035)], [], z0 + 0.01, z1 - 0.01, "metal")
        m.prism_xy([(-0.25, SH_RIDGE + t - 0.25 * SH_SLOPE + 0.004), (0.0, SH_RIDGE + t + 0.004), (0.25, SH_RIDGE + t - 0.25 * SH_SLOPE + 0.004),
                    (0.25, SH_RIDGE + t - 0.25 * SH_SLOPE + 0.05), (0.0, SH_RIDGE + t + 0.07), (-0.25, SH_RIDGE + t - 0.25 * SH_SLOPE + 0.05)],
                   [], z0, z1, "trim")                          # the ridge cap
        for s in (-1, 1):                                       # gutters
            m.box((min(s * SH_EAVE_X, s * (SH_EAVE_X + 0.16)), SH_EAVE_Y - 0.16, z0), (max(s * SH_EAVE_X, s * (SH_EAVE_X + 0.16)), SH_EAVE_Y - 0.03, z1), "metal")


def _portal(m, z, q):
    """the steel portal frame at z: columns at the back walls and the stall fronts, a rafter under the roof"""
    d = 0.08
    for s in (-1, 1):
        for xc, w in ((4.92, 0.16), (2.0, 0.16)):
            x0, x1 = s * xc - w / 2, s * xc + w / 2
            top = roof_under(max(abs(x0), abs(x1))) - 0.26
            m.box((min(x0, x1), 0.0, z - d), (max(x0, x1), top, z + d), "steel")
    xr = 4.98                                                    # (the rafter ends on the back walls' inner face)
    sec = [(-xr, roof_under(xr) - 0.26), (0.0, SH_RIDGE - 0.26), (xr, roof_under(xr) - 0.26),
           (xr, roof_under(xr) - 0.004), (0.0, SH_RIDGE - 0.004), (-xr, roof_under(xr) - 0.004)]
    m.prism_xy(sec, [], z - d + 0.01, z + d - 0.01, "steel")
    if q:                                                        # haunch braces at the stall fronts
        for s in (-1, 1):
            m.tube((s * 2.12, 3.75, z), (s * 2.7, roof_under(2.7) - 0.3, z), 0.035, "steel", n=4)


def shed_bay(q):
    m = Mesh()
    _shed_roof(m, -1.5, 1.5, q)
    _portal(m, -1.5, q)
    for s in (-1, 1):
        def X(a, b):
            return (min(s * a, s * b), max(s * a, s * b))
        x0, x1 = X(5.0, 5.12)
        m.box((x0, 0.0, -1.5), (x1, 3.89, 1.5), "wall")                         # the outer (back) wall
        if q:
            x0, x1 = X(5.12, 5.15)
            m.box((x0, 0.0, -1.5), (x1, 0.45, 1.5), "dark")                     # the kick plate outside
        x0, x1 = X(4.95, 4.98)
        m.box((x0, 0.85, -1.25), (x1, 2.45, 1.25), "trim")                      # pegboard
        if q:
            for zz in (-0.9, 0.0, 0.9):                                         # peg rails
                x0, x1 = X(4.88, 4.95)
                m.box((x0, 1.95, zz - 0.3), (x1, 1.98, zz + 0.3), "metal")
        x0, x1 = X(2.1, 4.82)
        m.box((x0, 0.0, -1.42), (x1, 2.6, -1.37), "trim")                       # the partition from the next stall
        x0, x1 = X(2.25, 2.85)
        m.box((x0, 0.0, -1.3), (x1, 0.9, 0.3), "wood")                          # the counter
        x0, x1 = X(2.2, 2.9)
        m.box((x0, 0.9, -1.34), (x1, 0.95, 0.34), "trim")                       # its top
        x0, x1 = X(2.0, 2.2)
        m.box((x0, 2.6, -1.42), (x1, 2.85, 1.42), "metal")                      # the shutter housing
        x0, x1 = X(1.97, 2.0)
        m.box((x0, 2.88, -1.36), (x1, 3.3, 1.36), "cream")                      # the fascia (the stall's name board)
        # lights: an LED batten over the aisle and one in the stall, each hung on two rods
        for xc, yb in ((1.0, 4.62), (3.55, 3.86)):
            x = s * xc
            m.box((x - 0.05, yb, -0.65), (x + 0.05, yb + 0.07, 0.65), "metal")
            m.box((x - 0.035, yb - 0.02, -0.6), (x + 0.035, yb, 0.6), "lamp")
            if q:
                for zz in (-0.5, 0.5):
                    m.box((x - 0.006, yb + 0.07, zz - 0.006), (x + 0.006, roof_under(abs(x) + 0.05) - 0.003, zz + 0.006), "dark")
    return m


def shed_end(far):
    def b(q):
        m = Mesh()
        if far:
            _portal(m, 0.0, q)
        z0, z1 = 0.08, 0.16
        for s in (-1, 1):
            xa, xb = sorted((s * 2.12, s * 5.12))
            # the end stall's closing wall up to the roof, cut to the slope
            pts = [(xa, 0.0), (xb, 0.0), (xb, roof_under(max(abs(xa), abs(xb))) - 0.02), (xa, roof_under(min(abs(xa), abs(xb))) - 0.02)]
            m.prism_xy(pts if s > 0 else [pts[0], pts[1], pts[2], pts[3]], [], z0, z1, "wall")
        # the gable over the aisle: the triangle-topped band between the stall fronts above the opening
        g = [(-2.11, 3.5), (2.11, 3.5), (2.11, roof_under(2.11) - 0.02), (0.0, SH_RIDGE - 0.02), (-2.11, roof_under(2.11) - 0.02)]
        m.prism_xy(g, [], z0, z1, "wall")
        m.box((-2.11, 3.36, z0 + 0.005), (2.11, 3.5, z1 + 0.02), "trim")             # the lintel
        m.box((-1.3, 3.7, z1 + 0.0), (1.3, 4.5, z1 + 0.05), "cream")                # the name-board backing
        if q:
            for s in (-1, 1):
                m.box((s * 1.36 - 0.03, 3.66, z1), (s * 1.36 + 0.03, 4.54, z1 + 0.08), "trim")
        return m
    return b


def shutter(q):
    m = Mesh()
    m.box((-1.42, 0.0, -0.02), (1.42, 2.6, 0.0), "metal", skip=("y+",))
    m.box((-1.42, 0.0, 0.0), (1.42, 0.06, 0.03), "dark")
    if q:
        for y in (0.7, 1.4, 2.1):
            m.quad((-1.4, y, 0.004), (1.4, y, 0.004), (1.4, y + 0.025, 0.004), (-1.4, y + 0.025, 0.004), "steel")
        m.box((-0.1, 0.06, 0.0), (0.1, 0.16, 0.03), "brass")
    return m


SHED_FRAME = ([B(-5.12, 0, -1.5, -5.0, 3.89, 1.5), B(5.0, 0, -1.5, 5.12, 3.89, 1.5)]
              + [B(s * 4.92 - 0.08, 0, -1.58, s * 4.92 + 0.08, 3.6, -1.42) for s in (-1, 1)]
              + [B(s * 2.0 - 0.08, 0, -1.58, s * 2.0 + 0.08, 4.4, -1.42) for s in (-1, 1)]
              + [B(min(s * 2.2, s * 2.9), 0, -1.34, max(s * 2.2, s * 2.9), 0.95, 0.34) for s in (-1, 1)]
              + [B(min(s * 2.1, s * 4.82), 0, -1.42, max(s * 2.1, s * 4.82), 2.6, -1.37) for s in (-1, 1)]
              + [B(-6.25, 3.55, -1.5, 6.25, 5.4, 1.5)])
piece("fm_shed_bay", "shed", shed_bay, kind="building", foot=[12.4, 3.0], lod1="keep", frame=SHED_FRAME,
      passes=[{"box": B(-1.9, 0, -1.5, 1.9, 3.4, 1.5), "kind": "open"}]
      + [{"box": B(min(s * 2.0, s * 2.9), 0, 0.36, max(s * 2.0, s * 2.9), 2.55, 1.4), "kind": "open"} for s in (-1, 1)],
      walk=[[-1.9, -1.5, 1.9, 1.5, 0.0]] + [[min(s * 2.95, s * 4.85), -1.35, max(s * 2.95, s * 4.85), 1.4, 0.0] for s in (-1, 1)],
      anchors={"shutter_R": [2.0, 2.6, 0.0, -90], "shutter_L": [-2.0, 2.6, 0.0, 90],
               "fascia_R": [1.96, 3.09, 0.0, -90], "fascia_L": [-1.96, 3.09, 0.0, 90],
               **{f"g{k}_R": [x, y, z, -90] for k, (x, y, z) in enumerate([(2.55, 0.95, -0.9), (2.55, 0.95, -0.2), (4.6, 0.0, -0.8),
                                                                          (4.6, 0.0, 0.6), (4.9, 1.98, -0.9), (4.9, 1.98, 0.9)])},
               **{f"g{k}_L": [-x, y, z, 90] for k, (x, y, z) in enumerate([(2.55, 0.95, -0.9), (2.55, 0.95, -0.2), (4.6, 0.0, -0.8),
                                                                          (4.6, 0.0, 0.6), (4.9, 1.98, -0.9), (4.9, 1.98, 0.9)])},
               "vendor_R": [3.6, 0.0, -0.4, -90], "vendor_L": [-3.6, 0.0, -0.4, 90]},
      budget=1500, palette="shed",
      notes="one 3 m bay of a 12 m open-sided steel shed: a permanent stall each side (back wall, pegboard, partition at "
            "z -1.5, counter, shutter housing, fascia), the 4 m covered aisle between, LED battens.  Bays tile along z "
            "(the portal frame at z -1.5); close a row with fm_shed_end_near (turned 180) and fm_shed_end_far.  Shutters "
            "are fm_shutter at shutter_R / shutter_L (down; scale y from the top to roll up).")
piece("fm_shed_end_near", "shed", shed_end(False), kind="building", foot=[12.4, 0.2], lod1="keep",
      frame=[B(-5.12, 0, 0.08, -2.1, 3.9, 0.16), B(2.1, 0, 0.08, 5.12, 3.9, 0.16), B(-2.12, 3.36, 0.06, 2.12, 5.3, 0.18)],
      passes=[{"box": B(-1.9, 0, -0.3, 1.9, 3.3, 0.5), "kind": "open"}],
      anchors={"board": [0.0, 4.1, 0.2, 0]}, budget=300, palette="shed",
      notes="the row's first end (no frame: the first bay has it): the end stalls' closing walls and the gable over the "
            "aisle entrance, a name board at `board` (a market's main cell card, fm_board_*); turn it 180 at the row start")
piece("fm_shed_end_far", "shed", shed_end(True), kind="building", foot=[12.4, 0.2], lod1="keep",
      frame=[B(-5.12, 0, 0.08, -2.1, 3.9, 0.16), B(2.1, 0, 0.08, 5.12, 3.9, 0.16), B(-2.12, 3.36, 0.06, 2.12, 5.3, 0.18)]
      + [B(s * xc - 0.08, 0, -0.08, s * xc + 0.08, 4.4, 0.08) for s in (-1, 1) for xc in (2.0, 4.92)],
      passes=[{"box": B(-1.9, 0, -0.3, 1.9, 3.3, 0.5), "kind": "open"}],
      anchors={"board": [0.0, 4.1, 0.2, 0]}, budget=500, palette="shed",
      notes="the row's last end: a portal frame at z 0 plus the closing walls and gable (at the row's far boundary)")
piece("fm_shutter", "shed", shutter, kind="overlay", foot=[2.84, 0.05], lod1="drop",
      frame=[B(-1.42, 0, -0.02, 1.42, 2.6, 0.03)], budget=60, palette="shed",
      moving={"kind": "scale_y", "pivot": [0, 2.6, 0], "open": 0.02, "closed": 1.0},
      notes="a roll shutter, down; the front is +z.  Roll it up by scaling y about the pivot (2.6 m: the housing)")


# ------------------------------------------------------------------ day vendors: tables, canopies, pitches
def _table(m, x, z, L=1.83, D=0.76, H=0.76, yaw=0.0, cloth=True, q=1):
    t = Mesh()
    t.box((-L / 2, H - 0.04, -D / 2), (L / 2, H, D / 2), "trim")
    if q:
        for sx in (-1, 1):
            for sz in (-1, 1):
                t.box((sx * (L / 2 - 0.12) - 0.018, 0.0, sz * (D / 2 - 0.08) - 0.018), (sx * (L / 2 - 0.12) + 0.018, H - 0.04, sz * (D / 2 - 0.08) + 0.018), "metal")
    else:
        for sx in (-1, 1):
            t.box((sx * (L / 2 - 0.12) - 0.02, 0.0, -D / 2 + 0.06), (sx * (L / 2 - 0.12) + 0.02, H - 0.04, D / 2 - 0.06), "metal")
    if cloth:                                       # a cloth over the top and down the front (one closed L)
        prism_zy(t, [(-D / 2 - 0.01, H), (D / 2 + 0.002, H), (D / 2 + 0.002, 0.32), (D / 2 + 0.012, 0.32),
                     (D / 2 + 0.012, H + 0.008), (-D / 2 - 0.01, H + 0.008)], -L / 2 - 0.01, L / 2 + 0.01, "fabric")
        if q:                                       # a hem stripe
            t.box((-L / 2 - 0.01, 0.34, D / 2 + 0.012), (L / 2 + 0.01, 0.4, D / 2 + 0.017), "accent")
    place(m, t, x, 0.0, z, yaw)


def _crate(m, x, y, z, w=0.5, d=0.34, h=0.3, yaw=0.0, slot="wood", q=1):
    c = Mesh()
    t = 0.018
    c.box((-w / 2 + t, 0.0, -d / 2 + t), (w / 2 - t, t, d / 2 - t), slot)
    c.box((-w / 2, 0.0, d / 2 - t), (w / 2, h, d / 2), slot)
    c.box((-w / 2, 0.0, -d / 2), (w / 2, h, -d / 2 + t), slot)
    c.box((-w / 2, 0.0, -d / 2 + t + 0.002), (-w / 2 + t, h, d / 2 - t - 0.002), slot)
    c.box((w / 2 - t, 0.0, -d / 2 + t + 0.002), (w / 2, h, d / 2 - t - 0.002), slot)
    if q:                                           # slat gaps as dark strips on the long sides
        for s in (-1, 1):
            c.quad_facing((-w / 2 + 0.02, h * 0.48, s * (d / 2 + 0.002)), (w / 2 - 0.02, h * 0.48, s * (d / 2 + 0.002)),
                          (w / 2 - 0.02, h * 0.53, s * (d / 2 + 0.002)), (-w / 2 + 0.02, h * 0.53, s * (d / 2 + 0.002)), (0, 0, s), "dark")
    place(m, c, x, y, z, yaw)


def pitch_paint(m, w=3.0, d=3.0, y=0.012, lw=0.08):
    hw, hd = w / 2, d / 2
    flat_poly(m, [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)],
              [[(-hw + lw, -hd + lw), (hw - lw, -hd + lw), (hw - lw, hd - lw), (-hw + lw, hd - lw)]], y, "paint")


def pitch_open(q):
    m = Mesh()
    pitch_paint(m)
    _table(m, 0.0, 0.85, q=q)
    _crate(m, -0.9, 0.0, -0.45, q=q)
    _crate(m, -0.35, 0.0, -0.5, yaw=8, slot="frame", q=q)
    if q:
        _crate(m, -0.9, 0.3, -0.45, w=0.46, d=0.32, h=0.26, yaw=-6, q=q)
        m.box((0.6, 0.0, -0.9), (1.0, 0.42, -0.5), "dark")           # a folding stool
    return m


def pitch_long(q):
    """the clothing pitch: a 2.4 m table and a rolling rail"""
    m = Mesh()
    pitch_paint(m)
    _table(m, 0.0, 0.95, L=2.4, q=q)
    _rack(m, 0.0, -0.6, q)
    return m


def _rack(m, x, z, q, L=1.5):
    r = Mesh()
    hw = L / 2
    for s in (-1, 1):
        sweep(r, [(s * hw, 0.06, -0.3), (s * hw, 1.62, 0.0), (s * hw, 0.06, 0.3)], 0.015, "metal", n=4 if q else 3)
        r.box((s * hw - 0.03, 0.0, -0.32), (s * hw + 0.03, 0.06, -0.26), "dark")    # casters
        r.box((s * hw - 0.03, 0.0, 0.26), (s * hw + 0.03, 0.06, 0.32), "dark")
    r.tube((-hw + 0.016, 1.6, 0.0), (hw - 0.016, 1.6, 0.0), 0.012, "metal", n=4)
    n = 7 if q else 4
    for k in range(n):
        gx = -hw + 0.2 + (L - 0.4) * k / (n - 1)
        sl = ("fabric", "accent", "accent2", "cream")[k % 4]
        r.box((gx - 0.035, 0.85, -0.2), (gx + 0.035, 1.5, 0.2), sl)            # a garment, edge on
        if q:
            r.box((gx - 0.003, 1.5, -0.006), (gx + 0.003, 1.588, 0.006), "dark")  # its hanger hook
    place(m, r, x, 0.0, z)


def canopy(w, d):
    def b(q):
        m = Mesh()
        hw, hd = w / 2, d / 2
        li = 0.07                                       # (legs inset: 5 cm behind the valance, no flush faces)
        legs = [(sx * (hw - li), sz * (hd - li)) for sx in (-1, 1) for sz in (-1, 1)]
        if d > 3.5:
            legs += [(sx * (hw - li), 0.0) for sx in (-1, 1)]
        for x, z in legs:
            m.box((x - 0.02, 0.0, z - 0.02), (x + 0.02, 2.47, z + 0.02), "metal")
            if x > 0:                                   # a sandbag on the foot, outside the leg
                m.box((x + 0.02, 0.0, z - 0.12), (x + 0.3, 0.16, z + 0.12), "dark")
            else:
                m.box((x - 0.3, 0.0, z - 0.12), (x - 0.02, 0.16, z + 0.12), "dark")
        # the valance: a band 2.25..2.48 round the top, outside the legs, lined inside
        for (a, c, nrm) in (((-hw, hd), (hw, hd), (0, 0, 1)), ((hw, hd), (hw, -hd), (1, 0, 0)), ((hw, -hd), (-hw, -hd), (0, 0, -1)), ((-hw, -hd), (-hw, hd), (-1, 0, 0))):
            pa, pc = V(a[0], 0, a[1]), V(c[0], 0, c[1])
            o = V(*nrm) * 0.005
            m.quad_facing(tuple(pa + o + V(0, 2.25, 0)), tuple(pc + o + V(0, 2.25, 0)), tuple(pc + o + V(0, 2.48, 0)), tuple(pa + o + V(0, 2.48, 0)), nrm, "accent")
            m.quad_facing(tuple(pa - o * 2 + V(0, 2.25, 0)), tuple(pc - o * 2 + V(0, 2.25, 0)), tuple(pc - o * 2 + V(0, 2.48, 0)), tuple(pa - o * 2 + V(0, 2.48, 0)),
                          tuple(-V(*nrm)), "fabric", 0.7)
        # the roof: a peak (3x3) or a ridge (3x6), from just over the valance, lined underneath (the lining inset)
        peak, e, y0 = 3.3, 0.02, 2.49
        r0, r1 = ((0.0, peak, -hd + 1.5), (0.0, peak, hd - 1.5)) if d > 3.5 else ((0.0, peak, 0.0), (0.0, peak, 0.0))
        c = [(-hw - e, y0, hd + e), (hw + e, y0, hd + e), (hw + e, y0, -hd - e), (-hw - e, y0, -hd - e)]
        faces = [(c[0], c[1], r1, None, (0, 0.6, 1)), (c[2], c[3], r0, None, (0, 0.6, -1))]
        if r0 != r1:
            faces += [(c[1], c[2], r0, r1, (1, 0.6, 0)), (c[3], c[0], r1, r0, (-1, 0.6, 0))]
        else:
            faces += [(c[1], c[2], r0, None, (1, 0.6, 0)), (c[3], c[0], r0, None, (-1, 0.6, 0))]

        def lin(p):                                     # the lining point: 1.2 cm under, drawn in 4 % toward the middle
            return (p[0] * 0.96, p[1] - 0.012, p[2] * 0.96 if abs(p[2]) > hd - 1.4 or d < 3.5 else p[2])
        for k, (a, bb, ee, f, nrm) in enumerate(faces):
            sl = "fabric" if k % 2 == 0 else "accent"
            pts = [a, bb, ee] + ([f] if f else [])
            if f is None:
                m.tri_facing(a, bb, ee, nrm, sl)
            else:
                m.quad_facing(a, bb, ee, f, nrm, sl)
            lp = [lin(p) for p in pts]
            if f is None:
                m.tri_facing(*lp, tuple(-V(*nrm)), sl, 0.65)
            else:
                m.quad_facing(*lp, tuple(-V(*nrm)), sl, 0.65)
        if q:                                        # the truss under the canopy: a top ring between the legs
            xs = sorted({x for x, _ in legs})
            zs = sorted({z for _, z in legs})
            for x in xs:
                for za, zb in zip(zs, zs[1:]):
                    m.box((x - 0.015, 2.33, za + 0.02), (x + 0.015, 2.36, zb - 0.02), "metal")
            for z in (zs[0], zs[-1]):
                m.box((xs[0] + 0.02, 2.37, z - 0.015), (xs[1] - 0.02, 2.4, z + 0.015), "metal")
        return m
    return b


piece("fm_pitch_open", "stall", pitch_open, kind="decor", foot=[3.0, 3.0], lod1="drop",
      frame=[B(-0.93, 0, 0.47, 0.93, 0.78, 1.23), B(-1.16, 0, -0.64, -0.08, 0.58, -0.26)],
      anchors={"g0": [-0.5, 0.768, 0.85, 0], "g1": [0.0, 0.768, 0.85, 0], "g2": [0.55, 0.768, 0.85, 0], "g3": [-0.9, 0.3, -0.45, 0],
               "g4": [-0.35, 0.3, -0.5, 0], "g5": [0.4, 0.0, 0.0, 0], "vendor_0": [0.3, 0.0, -0.2, 0], "canopy": [0, 0, 0, 0]},
      walk=[[0.0, -0.25, 1.4, 0.42, 0.0]], budget=320, palette="stall",
      notes="a painted 3x3 m open pitch with a folding table (cloth), two crates and a stool; goods clusters at g0..g5; "
            "an fm_canopy_3x3 goes on `canopy` when the vendor has one")
piece("fm_pitch_table_long", "stall", pitch_long, kind="decor", foot=[3.0, 3.0], lod1="drop",
      frame=[B(-1.21, 0, 0.57, 1.21, 0.78, 1.33), B(-0.78, 0, -0.92, 0.78, 1.62, -0.28)],
      anchors={"g0": [-0.7, 0.768, 0.95, 0], "g1": [0.0, 0.768, 0.95, 0], "g2": [0.7, 0.768, 0.95, 0], "vendor_0": [1.0, 0.0, 0.0, 0],
               "canopy": [0, 0, 0, 0]},
      walk=[[-1.4, -0.2, 1.4, 0.5, 0.0]], budget=360, palette="stall", notes="the clothing pitch: a 2.4 m table and a rolling rail of garments")
for w, d in ((3.0, 3.0), (3.0, 6.0)):
    pid = "fm_canopy_%dx%d" % (w, d)
    piece(pid, "stall", canopy(w, d), kind="decor", foot=[w, d], lod1="keep",
          frame=[B(sx * (w / 2 - 0.07) - 0.02, 0, sz - 0.02, sx * (w / 2 - 0.07) + 0.02, 2.47, sz + 0.02)
                 for sx in (-1, 1) for sz in ([-(d / 2 - 0.07), d / 2 - 0.07] + ([0.0] if d > 3.5 else []))],
          passes=[{"box": B(-w / 2 + 0.1, 0, -d / 2 + 0.1, w / 2 - 0.1, 2.24, d / 2 - 0.1), "kind": "open"}],
          walk=[[-w / 2 + 0.1, -d / 2 + 0.1, w / 2 - 0.1, d / 2 - 0.1, 0.0]], budget=200 if d < 4 else 300, palette="stall",
          notes="a pop-up canopy (the US 10 x %d ft): legs with sandbags (paved lots take no stakes), a striped valance "
                "at 2.25-2.5 m, the peaked top to 3.3 m" % (10 if d < 4 else 20))


# ------------------------------------------------------------------ display furniture
def shelf_unit(q, w=1.2, d=0.4, h=1.8, n=4, slot="wood"):
    m = Mesh()
    t = 0.025
    for s in (-1, 1):
        m.box((s * w / 2 - (t if s > 0 else 0), 0.0, -d / 2) if s > 0 else (-w / 2, 0.0, -d / 2),
              (w / 2, h, d / 2) if s > 0 else (-w / 2 + t, h, d / 2), slot)
    for k in range(n):
        y = 0.08 + (h - 0.12) * k / (n - 1)
        m.box((-w / 2 + t, y, -d / 2 + 0.012), (w / 2 - t, y + 0.022, d / 2), slot, 0.95)
    m.box((-w / 2 + t, 0.0, -d / 2), (w / 2 - t, h - 0.02, -d / 2 + 0.012), "trim", 0.85)   # the back
    return m


def shelf_heights(h=1.8, n=4):
    return [round(0.08 + (h - 0.12) * k / (n - 1) + 0.022, 3) for k in range(n)]


def table_folding(q):
    m = Mesh()
    _table(m, 0.0, 0.0, cloth=False, q=q)
    return m


def crate_stack(q):
    m = Mesh()
    _crate(m, -0.29, 0.0, 0.0, q=q)
    _crate(m, 0.29, 0.0, 0.02, yaw=4, slot="frame", q=q)
    _crate(m, -0.02, 0.3, 0.0, w=0.48, d=0.33, h=0.28, yaw=-5, q=q)
    return m


def rack_clothes(q):
    m = Mesh()
    _rack(m, 0.0, 0.0, q)
    return m


def bin_produce(q):
    """a tilted three-bin produce stand: bins on a frame, fronts low toward the customer (+z)"""
    m = Mesh()
    for k, x in enumerate((-0.55, 0.0, 0.55)):
        y0 = 0.62
        sec = [(-0.3, y0), (0.3, y0 - 0.12), (0.3, y0 + 0.05), (0.27, y0 + 0.05), (0.27, y0 - 0.09), (-0.27, y0 + 0.03), (-0.27, y0 + 0.25), (-0.3, y0 + 0.25)]
        prism_zy(m, sec, x - 0.26, x + 0.26, "wood")
        if q:
            m.box((x - 0.2, y0 - 0.1, 0.33), (x + 0.2, y0 + 0.02, 0.345), "accent", 0.95)     # the price board
    for x in (-0.84, 0.84):
        for z in (-0.25, 0.25):
            m.box((x - 0.025, 0.0, z - 0.025), (x + 0.025, 0.62 if z < 0 else 0.5, z + 0.025), "wood")
    return m


def tarp_ground(q):
    """a blanket vendor's tarp on the ground, its corners weighted"""
    m = Mesh()
    flat_poly(m, [(-1.2, -0.9), (1.2, -0.9), (1.25, 0.9), (-1.15, 0.92)], [], 0.015, "accent2")
    if q:
        for x, z in ((-1.15, -0.85), (1.15, -0.85), (1.2, 0.85), (-1.1, 0.87)):
            m.box((x - 0.06, 0.015, z - 0.06), (x + 0.06, 0.07, z + 0.06), "concrete")
    return m


piece("fm_table_folding", "display", table_folding, kind="decor", foot=[1.83, 0.76], lod1="drop",
      frame=[B(-0.915, 0, -0.38, 0.915, 0.76, 0.38)], anchors={"g0": [-0.5, 0.76, 0, 0], "g1": [0.0, 0.76, 0, 0], "g2": [0.5, 0.76, 0, 0]},
      budget=120, palette="stall", notes="a bare 6 ft folding table (the islanders' tents and the sheds use it too)")
piece("fm_shelf_unit", "display", lambda q: shelf_unit(q), kind="decor", foot=[1.2, 0.4], lod1="drop",
      frame=[B(-0.6, 0, -0.2, 0.6, 1.8, 0.2)],
      anchors={f"g{k}": [0.0, y, 0.02, 0] for k, y in enumerate(shelf_heights())}, budget=250, palette="stall",
      notes="a 1.2 m four-shelf unit, open front (+z); goods clusters on g0..g3 (shelf tops)")
piece("fm_shelf_low", "display", lambda q: shelf_unit(q, w=1.2, d=0.45, h=0.95, n=3), kind="decor", foot=[1.2, 0.45], lod1="drop",
      frame=[B(-0.6, 0, -0.225, 0.6, 0.95, 0.225)],
      anchors={f"g{k}": [0.0, y, 0.02, 0] for k, y in enumerate(shelf_heights(0.95, 3))}, budget=200, palette="stall",
      notes="a low three-shelf stand (a counter front)")
piece("fm_crate_stack", "display", crate_stack, kind="decor", foot=[1.04, 0.36], lod1="drop",
      frame=[B(-0.52, 0, -0.18, 0.54, 0.58, 0.2)], anchors={"g0": [-0.29, 0.018, 0.0, 0], "g1": [0.29, 0.018, 0.02, 0], "g2": [-0.02, 0.318, 0.0, 0]},
      budget=200, palette="stall", notes="three crates, two on the ground and one on top; goods inside at g0..g2")
piece("fm_rack_clothes", "display", rack_clothes, kind="decor", foot=[1.56, 0.64], lod1="drop",
      frame=[B(-0.78, 0, -0.32, 0.78, 1.62, 0.32)], budget=300, palette="stall", notes="a rolling garment rail with seven garments")
piece("fm_bin_produce", "display", bin_produce, kind="decor", foot=[1.74, 0.66], lod1="drop",
      frame=[B(-0.87, 0, -0.33, 0.87, 0.87, 0.33)], anchors={f"g{k}": [x, 0.6, 0.0, 0] for k, x in enumerate((-0.55, 0.0, 0.55))},
      budget=200, palette="stall", notes="a tilted three-bin produce stand; produce clusters at g0..g2")
piece("fm_tarp_ground", "display", tarp_ground, kind="decor", foot=[2.5, 1.85], lod1="drop", collide="none",
      anchors={f"g{k}": [x, 0.015, z, 0] for k, (x, z) in enumerate(((-0.6, -0.3), (0.0, 0.2), (0.6, -0.3), (-0.4, 0.5), (0.5, 0.5)))},
      budget=60, palette="stall", notes="a blanket vendor's ground tarp (no collision: walk over it)")


# ------------------------------------------------------------------ goods clusters (goods atlas cards on a container)
# id: (container, [(cell, card height, x, z, yaw)], note).  Cards stand on the container floor, face +z, two-faced.
GOODS = {
    "household": ("tray", [("brass_lamp", 0.46, -0.2, -0.08, 0), ("vase_flowers", 0.38, 0.05, -0.12, 0), ("tea_set", 0.2, 0.12, 0.06, 0),
                           ("plates", 0.22, -0.12, 0.1, 0)], "lamps, a tea set, plates, a vase"),
    "antiques": ("tray", [("mantel_clock", 0.36, -0.18, -0.1, 0), ("framed_painting", 0.42, 0.14, -0.14, 0), ("radio", 0.24, -0.02, 0.06, 0),
                          ("barometer", 0.24, 0.2, 0.1, 0)], "a clock, a painting, a radio, a barometer"),
    "machines": ("tray", [("sewing_machine", 0.3, -0.13, -0.06, 0), ("typewriter", 0.24, 0.15, 0.06, 0)], "a sewing machine and a typewriter"),
    "books": ("crate", [("old_books", 0.3, -0.1, -0.04, 0), ("records", 0.3, 0.1, 0.06, 0)], "books and a box of records"),
    "maps": ("tray", [("map_scroll", 0.32, -0.08, -0.06, 0), ("old_books", 0.22, 0.16, 0.08, 0)], "charts and old books"),
    "tools": ("crate", [("tools", 0.3, 0.0, 0.0, 0)], "a crate of tools"),
    "clothing": ("tray", [("knit_sweater", 0.26, -0.14, -0.08, 0), ("boots", 0.2, 0.14, 0.04, 0), ("felt_hat", 0.14, -0.05, 0.12, 0)],
                 "sweaters, boots, a hat"),
    "toys": ("tray", [("toy_robot", 0.32, -0.18, -0.06, 0), ("guitar", 0.62, 0.1, -0.15, 0), ("box_kite", 0.24, 0.16, 0.1, 0)],
             "a tin robot, a guitar, a kite"),
    "produce": ("crate", [("apple_crate", 0.24, -0.02, 0.02, 0), ("bananas", 0.2, 0.14, 0.1, 0)], "apples and bananas"),
    "eggs_honey": ("tray", [("egg_basket", 0.22, -0.15, -0.04, 0), ("honey_jar", 0.18, 0.1, 0.06, 0), ("berries", 0.18, 0.2, -0.1, 0)],
                   "eggs, honey, berries"),
    "plants": ("tray", [("fern", 0.5, -0.14, -0.06, 0), ("vase_flowers", 0.42, 0.16, 0.04, 0)], "a fern and cut flowers"),
    "quilts": ("tray", [("quilt", 0.26, -0.1, -0.05, 0), ("down_quilt", 0.24, 0.12, 0.08, 0)], "folded quilts"),
    "sky_knit": ("tray", [("knit_sweater", 0.28, -0.16, -0.06, 0), ("dyed_yarn", 0.22, 0.12, -0.1, 0), ("sailcloth", 0.2, 0.06, 0.1, 0)],
                 "island knitwear, dyed yarn, sailcloth"),
    "sky_rope": ("tray", [("rope_coil", 0.3, -0.12, -0.05, 0), ("knotted_cord", 0.26, 0.15, 0.07, 0)], "rope coils and knotted cord"),
    "sky_lights": ("tray", [("glass_lantern", 0.42, -0.16, -0.08, 0), ("lantern", 0.36, 0.08, -0.12, 0), ("brass_bell", 0.26, 0.18, 0.08, 0),
                            ("beeswax_candles", 0.22, -0.02, 0.1, 0)], "lanterns, a bell, beeswax candles"),
    "sky_food": ("tray", [("goat_cheese", 0.18, -0.16, 0.04, 0), ("honey_dipper", 0.22, 0.02, -0.08, 0), ("mead", 0.28, 0.2, -0.04, 0),
                          ("pickled_greens", 0.22, -0.04, 0.12, 0)], "cheese, sky honey, mead, pickles"),
    "sky_smoked": ("tray", [("dried_fish", 0.3, -0.12, -0.06, 0), ("smoked_ham", 0.3, 0.16, 0.04, 0)], "dried fish and a smoked ham"),
    "sky_wonders": ("tray", [("ice_blocks", 0.24, -0.15, 0.02, 0), ("moss_bundle", 0.24, 0.14, -0.08, 0), ("woven_basket", 0.16, 0.12, 0.12, 0)],
                    "snow-ice from aloft, moss remedies, baskets"),
    "sky_pets": ("tray", [("dove_cage", 0.42, -0.08, -0.04, 0), ("lark_fan", 0.3, 0.2, 0.08, 0)], "a dove cage and a lark fan"),
}
FLOOR_GOODS = {   # big things that stand on the ground beside a table
    "bicycle": [("bicycle", 0.95, 0.0, 0.0, 0)],
    "rocking_chair": [("rocking_chair", 0.95, 0.0, 0.0, 0)],
    "rolled_rug": [("rolled_rug", 0.7, 0.0, 0.0, 0)],
}


def goods_cluster(spec, floor=False):
    def b(q):
        m = Mesh()
        if floor:
            base, cards = 0.0, spec
        else:
            kind, cards, _ = spec
            if kind == "tray":
                m.box((-0.3, 0.0, -0.2), (0.3, 0.012, 0.2), "wood")
                if q:
                    for z in (-0.195, 0.183):
                        m.box((-0.29, 0.012, z), (0.29, 0.045, z + 0.012), "wood")
                base = 0.012
            else:
                _crate(m, 0.0, 0.0, 0.0, w=0.56, d=0.36, h=0.22, q=q)
                base = 0.018
        for k, (cell, h, x, z, yaw) in enumerate(cards):
            cid = "goods_" + cell
            if not floor and spec[0] == "crate":           # (inside the crate's walls: no card through them)
                from mk import cell_aspect
                hw = h * cell_aspect(cid) / 2
                lim = 0.28 - 0.018 - 0.01
                if hw > lim:
                    h *= lim / hw
                    hw = lim
                x = max(-lim + hw, min(lim - hw, x))
            a = math.radians(yaw)
            right = (math.cos(a), 0.0, -math.sin(a))
            card(m, "goods", cid, (x, base + h / 2 + 0.002, z), right, (0, 1, 0), h, gap=0.012)
        return m
    return b


for gid, spec in GOODS.items():
    piece("fm_goods_" + gid, "goods", goods_cluster(spec), kind="decor", foot=[0.6, 0.4], lod1="drop", collide="none", mid="full",
          budget=120, palette="stall", notes="goods: " + spec[2] + " (goods atlas cards; stand on a g* anchor)")
for gid, spec in FLOOR_GOODS.items():
    piece("fm_goods_" + gid, "goods", goods_cluster(spec, floor=True), kind="decor", foot=[1.0, 0.1], lod1="drop", collide="none",
          mid="full", budget=40, palette="stall", notes="a big goods card standing on the ground (beside a table)")


# ------------------------------------------------------------------ the 9 m lot pole (lamp kind 5)
POLE_H = 9.0


def lot_pole(heads):
    dirs = {1: [0], 2: [0, 180], 4: [0, 90, 180, 270]}[heads]

    def b(q):
        m = Mesh()
        n = 8 if q else 6
        m.cyl(0.0, 0.0, 0.32, -0.3, 0.6, "concrete", n=n)                      # the pier (0.6 m proud: bumpers)
        if q:
            m.box((-0.2, 0.6, -0.2), (0.2, 0.625, 0.2), "steel")              # the base plate
            for sx in (-1, 1):
                for sz in (-1, 1):
                    m.cyl(sx * 0.15, sz * 0.15, 0.022, 0.625, 0.67, "dark", n=4)
        m.cyl(0.0, 0.0, 0.11, 0.625 if q else 0.6, POLE_H - 0.1, "steel", n=n, r1=0.065)
        m.cyl(0.0, 0.0, 0.075, POLE_H - 0.1, POLE_H + 0.05, "steel", n=n)        # the top tenon
        for yaw in dirs:
            h = Mesh()
            h.box((-0.04, POLE_H - 0.07, 0.07), (0.04, POLE_H + 0.02, 0.85), "steel")          # the arm
            h.box((-0.22, POLE_H - 0.1, 0.85), (0.22, POLE_H + 0.05, 1.55), "steel")            # the shoebox head
            h.box((-0.18, POLE_H - 0.13, 0.9), (0.18, POLE_H - 0.1, 1.5), "lamp")               # the LED lens
            if q:
                h.box((-0.235, POLE_H + 0.05, 0.84), (0.235, POLE_H + 0.075, 1.565), "steel", 0.9)   # the lid
            place(m, h, yaw=yaw)
        if q:                                                                      # the market's banner arms
            m.box((-0.03, 6.0, 0.07), (0.03, 6.06, 0.75), "steel")
            m.box((-0.03, 4.2, 0.08), (0.03, 4.26, 0.75), "steel")
        return m
    return b


def _head_bulbs(heads):
    out = []
    for yaw in {1: [0], 2: [0, 180], 4: [0, 90, 180, 270]}[heads]:
        a = math.radians(yaw)
        x, z = 1.2 * math.sin(a), 1.2 * math.cos(a)
        out.append([round(x, 3), POLE_H - 0.13, round(z, 3)])
    return out


for hn in (1, 2, 4):
    piece("fm_lot_pole_%d" % hn, "lot", lot_pole(hn), kind="lamp", foot=[3.2 if hn == 4 else 0.64, 3.2], lod1="keep",
          frame=[B(-0.3, 0, -0.3, 0.3, 0.6, 0.3), B(-0.11, 0.6, -0.11, 0.11, POLE_H, 0.11)],
          anchors={"banner_0": [0.0, 4.2, 0.75, 0], "banner_1": [0.0, 6.0, 0.75, 0]}, budget=400, palette="lot",
          extra={"head_bulbs": _head_bulbs(hn), "lamp_kind": 5, "pool_r": 14.0},
          notes="the 9 m lot pole (StreetLights lamp kind 5) with %d LED shoebox head(s) on 0.85 m arms; its pier stands "
                "0.6 m proud as a bumper in the landscape island; head_bulbs are the lens centres (bulb sprites / pools)" % hn)


# ------------------------------------------------------------------ lot paint and kerbs (decals at 12 mm, kerbs as meshes)
LINE = 0.1
BAY_W, BAY_L, AISLE = 2.75, 5.5, 7.3


def paint_bays(n, double=True):
    """a row of n 90-degree bays (2.75 x 5.5 m) along x, nose to nose with another row when double; the aisle at +z"""
    def b(q):
        m = Mesh()
        L = n * BAY_W
        rows = (1, -1) if double else (1,)
        for r in rows:
            z0, z1 = (0.0, BAY_L) if r > 0 else (-BAY_L, 0.0)
            for k in range(n + 1):
                x = -L / 2 + k * BAY_W
                flat_poly(m, [(x - LINE / 2, z0), (x + LINE / 2, z0), (x + LINE / 2, z1), (x - LINE / 2, z1)], [], 0.012, "paint")
        if double:                                  # the nose line between the rows
            flat_poly(m, [(-L / 2 - LINE / 2, -LINE / 2), (L / 2 + LINE / 2, -LINE / 2), (L / 2 + LINE / 2, LINE / 2), (-L / 2 - LINE / 2, LINE / 2)],
                      [], 0.011, "paint")
        return m
    return b


def paint_arrow(q):
    m = Mesh()
    flat_poly(m, [(-0.18, -1.6), (0.18, -1.6), (0.18, 0.3), (0.55, 0.3), (0.0, 1.4), (-0.55, 0.3), (-0.18, 0.3)], [], 0.012, "paint")
    return m


def paint_crosswalk(q):
    m = Mesh()
    for k in range(6):
        x = -1.5 + 0.25 + k * 0.5
        flat_poly(m, [(x - 0.2, -1.5), (x + 0.2, -1.5), (x + 0.2, 1.5), (x - 0.2, 1.5)], [], 0.012, "paint")
    return m


def paint_fire_lane(q):
    m = Mesh()
    flat_poly(m, [(-1.5, -0.075), (1.5, -0.075), (1.5, 0.075), (-1.5, 0.075)], [], 0.012, "paint2")
    for k in range(3):
        x = -1.0 + k
        flat_poly(m, [(x - 0.3, 0.4), (x + 0.3, 0.4), (x + 0.3, 0.55), (x - 0.3, 0.55)], [], 0.012, "paint2")
    return m


def paint_pitch(q):
    m = Mesh()
    pitch_paint(m)
    flat_poly(m, [(-0.3, 1.1), (0.3, 1.1), (0.3, 1.35), (-0.3, 1.35)], [], 0.012, "paint")    # the number plate
    return m


def kerb(kind):
    def b(q):
        m = Mesh()
        slot = "paint2" if kind == "fire" else "concrete"
        sec = [(-0.15, 0.0), (0.12, 0.0), (0.12, 0.13), (0.09, 0.15), (-0.15, 0.15)]    # (z, y): the face toward +z
        if kind == "corner":
            ring_o, ring_i = [], []
            for k in range(7 if q else 4):
                a = math.radians(90.0 * k / (6 if q else 3))
                ring_o.append((-1.5 + 1.62 * math.cos(a), -1.5 + 1.62 * math.sin(a)))
            for p in reversed([(-1.5 + 1.35 * math.cos(math.radians(90.0 * k / (6 if q else 3))), -1.5 + 1.35 * math.sin(math.radians(90.0 * k / (6 if q else 3))))
                               for k in range(7 if q else 4)]):
                ring_i.append(p)
            m.prism_xz(ring_o + ring_i, 0.0, 0.15, slot)
        else:
            prism_zy(m, sec, -1.5, 1.5, slot)
        return m
    return b


def wheel_stop(q):
    m = Mesh()
    prism_zy(m, [(-0.1, 0.0), (0.1, 0.0), (0.06, 0.11), (-0.06, 0.11)], -0.9, 0.9, "paint")
    return m


def lot_island_end(q):
    """the rounded end of a landscape island between bay rows: a kerb half-ring with grass inside (the pole goes in it)"""
    m = Mesh()
    n = 10 if q else 6
    outer = [(1.35 * math.cos(math.pi * k / n), 1.35 * math.sin(math.pi * k / n)) for k in range(n + 1)]
    inner = [(1.12 * math.cos(math.pi * k / n), 1.12 * math.sin(math.pi * k / n)) for k in range(n + 1)]
    m.prism_xz(outer + list(reversed(inner)), 0.0, 0.15, "concrete")
    flat_poly(m, [(x * 0.99, z * 0.99 + 0.005) for x, z in inner], [], 0.12, "plant")
    return m


for n in (4, 8):
    piece("fm_paint_bays_%d" % n, "lot", paint_bays(n), kind="decal", foot=[n * BAY_W, 2 * BAY_L], lod1="drop", collide="none", mid="full",
          budget=100, palette="lot", notes="%d double-loaded 90-degree bays (2.75 x 5.5 m) along x, nose line at z 0" % n)
piece("fm_paint_bays_row_8", "lot", paint_bays(8, False), kind="decal", foot=[8 * BAY_W, 2 * BAY_L], lod1="drop", collide="none", mid="full",
      budget=60, palette="lot", notes="a single row of 8 bays (z 0..5.5 m; the aisle side at +z)")
piece("fm_paint_arrow", "lot", paint_arrow, kind="decal", foot=[1.1, 3.0], lod1="drop", collide="none", mid="full", budget=12,
      palette="lot", notes="a one-way arrow pointing +z")
piece("fm_paint_crosswalk", "lot", paint_crosswalk, kind="decal", foot=[3.0, 3.0], lod1="drop", collide="none", mid="full", budget=24,
      palette="lot", notes="a 3 m crossing (bars along z): tile along x")
piece("fm_paint_fire_lane", "lot", paint_fire_lane, kind="decal", foot=[3.0, 0.6], lod1="drop", collide="none", mid="full", budget=24,
      palette="lot", notes="a red fire-lane edge line with dash marks (3 m, tile along x)")
piece("fm_paint_pitch", "lot", paint_pitch, kind="decal", foot=[3.0, 3.0], lod1="drop", collide="none", mid="full", budget=40,
      palette="lot", notes="an open-air pitch outline (3 x 3 m) with its number plate at the aisle edge (+z)")
piece("fm_kerb_3m", "lot", kerb("plain"), kind="kerb", foot=[3.0, 0.27], lod1="keep", frame=[B(-1.5, 0, -0.12, 1.5, 0.15, 0.15)],
      budget=24, palette="lot", notes="a 150 mm concrete kerb, its face toward +z, 3 m (tile along x)")
piece("fm_kerb_fire_3m", "lot", kerb("fire"), kind="kerb", foot=[3.0, 0.27], lod1="keep", frame=[B(-1.5, 0, -0.12, 1.5, 0.15, 0.15)],
      budget=24, palette="lot", notes="the kerb painted red (fire lane)")
piece("fm_kerb_corner", "lot", kerb("corner"), kind="kerb", foot=[3.0, 3.0], lod1="keep",
      frame=[B(-1.5, 0, -1.5, 0.12, 0.15, 0.12)], budget=60, palette="lot", notes="a quarter-round kerb corner (radius 1.35-1.62 m about (-1.5, -1.5))")
piece("fm_wheel_stop", "lot", wheel_stop, kind="kerb", foot=[1.8, 0.2], lod1="drop", frame=[B(-0.9, 0, -0.1, 0.9, 0.11, 0.1)],
      budget=16, palette="lot", notes="a 1.8 m wheel stop (yellow paint slot)")
piece("fm_lot_island_end", "lot", lot_island_end, kind="kerb", foot=[2.7, 2.7], lod1="keep", frame=[B(-1.35, 0, 0, 1.35, 0.15, 1.35)],
      anchors={"pole": [0.0, 0.0, 0.55, 0]}, budget=120, palette="lot",
      notes="the rounded end of a landscape island (kerb half ring + grass at 12 cm); a lot pole stands at `pole`")
