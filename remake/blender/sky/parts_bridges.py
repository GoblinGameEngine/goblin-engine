"""parts_bridges.py -- the sky islands' retractable bridges: 10 styles x (walk 3.6 m, road 6 m).

Every bridge is built in the dock-face frame (game frame): origin on the face at deck level, +Y up, +Z out of the
island, X across.  Deployed, the walking surface runs from the face (z 0) to the nose at z = REACH (13 m), where it
meets the other island's bridge nose to nose (docked faces are 26 m apart).  The root node is the fixed housing;
the moving parts are child nodes whose rest transform in the glb is the STOWED pose (deploy 0).

pose(d) gives every moving node's local transform for deploy d in 0..1; it is sampled and written to
bridge_styles.json as piecewise-linear keys (pos lerp, rot slerp, scl lerp), so the game needs one generic animator.
Cables, chains and rams are 'stretch' nodes: a unit-length tube along local +Z, keyed with a rotation and a Z scale.
Colliders are boxes in their node's local frame (attach them to the moving node).
"""
import math

from mathutils import Matrix, Vector

from parts_lib import Node, T, Rx, Ry

REACH = 13.0
RAIL_H = 1.1


# ---------------------------------------------------------------- shared pieces
def railing(m, x, z0, z1, y0, mat, h=RAIL_H, every=1.6, post=0.07, rail=0.06, mid=True):
    n = max(1, round((z1 - z0) / every))
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        z = min(max(z, z0 + post / 2), z1 - post / 2)
        m.box((x - post / 2, y0, z - post / 2), (x + post / 2, y0 + h - rail, z + post / 2), mat)
    m.box((x - rail / 2, y0 + h - rail, z0), (x + rail / 2, y0 + h, z1), mat)
    if mid:
        m.box((x - rail * 0.4, y0 + h * 0.5 - rail * 0.4, z0 + post), (x + rail * 0.4, y0 + h * 0.5 + rail * 0.4, z1 - post), mat)


def rails_cols(node, hw, z0, z1, y0=0.0, h=RAIL_H):
    return [{"node": node, "center": [s * hw, y0 + h / 2, (z0 + z1) / 2], "size": [0.1, h, z1 - z0]} for s in (-1, 1)]


def deck_col(node, w, z0, z1, top=0.0, t=0.12):
    return {"node": node, "center": [0.0, top - t / 2, (z0 + z1) / 2], "size": [w, t, z1 - z0]}


def stretch_node(name, parent, r, mat, seg=6):
    n = Node(name, parent)
    n.mesh.tube((0, 0, 0), (0, 0, 1), r, mat, seg=seg)
    return n


def aim(a, b):
    """the local transform of a stretch node from a to b (parent frame)"""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = max(d.length, 0.01)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return Matrix.Translation(a) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((1, 1, L, 1))


def sill(m, hw, mat):
    """the face's lip (3 cm proud of the deck, so nothing is coplanar with the island's ground)"""
    m.box((-hw - 0.25, -0.35, -0.5), (hw + 0.25, 0.03, 0.0), mat)


def ramp(d, a, b):
    """0..1 as d runs a..b"""
    return min(1.0, max(0.0, (d - a) / (b - a)))


# ---------------------------------------------------------------- styles
class Style:
    """name, kind, root Node, nodes {name: Node}, pose(d) -> {name: local Matrix}, colliders, meta"""

    def __init__(self, name, kind, W):
        self.name, self.kind, self.W = name, kind, W
        self.hw = W / 2
        self.root = Node("bridge")
        self.nodes = {}
        self.cols = []
        self.meta = {"nose_y": 0.0, "clear": {}}

    def node(self, name, parent=None, xf=None):
        n = Node(name, parent or self.root, xf)
        self.nodes[name] = n
        return n

    def finish(self):
        for name, xf in self.pose(0.0).items():
            self.nodes[name].xf = xf
        return self


def bascule(name, W, look):
    """a span hinged at the face, stowed straight up (-90 deg about X), lowered by cables from a portal"""
    s = Style(name, "bascule", W)
    hw = s.hw
    R = s.root.mesh
    span = s.node("span")
    m = span.mesh
    if look == "timber":
        m.box((-hw, -0.12, 0.0), (hw, 0.0, REACH), "sky_plank")
        for x in (-hw + 0.35, hw - 0.35):
            m.box((x - 0.12, -0.45, 0.0), (x + 0.12, -0.12, REACH), "sky_timber_dark")
        for i in range(7):
            z = 0.5 + i * (REACH - 1.0) / 6
            m.box((-hw, -0.30, z - 0.08), (hw, -0.12, z + 0.08), "sky_timber_dark")
        for x in (-hw + 0.05, hw - 0.05):
            railing(m, x, 0.0, REACH, 0.0, "sky_timber")
        for sx in (-1, 1):
            m.box((sx * hw, -0.25, 8.85), (sx * (hw + 0.2), 0.1, 9.15), "sky_iron")      # cable lug
        post_mat, cable_mat, beam = "sky_timber", "sky_rope", "sky_timber_dark"
    elif look == "iron":
        m.box((-hw, -0.10, 0.0), (hw, 0.0, REACH), "sky_steel")
        for sx in (-1, 1):
            m.box((sx * hw, -0.5, 0.0), (sx * (hw + 0.1), 1.0, REACH), "sky_iron_red")    # plate girder parapet
            m.box((sx * (hw + 0.1), 0.94, 0.0), (sx * (hw + 0.16), 1.1, REACH), "sky_iron_red")
            for i in range(9):
                z = 0.4 + i * (REACH - 0.8) / 8
                m.box((sx * (hw + 0.1), -0.5, z - 0.05), (sx * (hw + 0.16), 0.94, z + 0.05), "sky_iron")
            m.box((sx * (hw + 0.1), -0.25, 8.85), (sx * (hw + 0.25), 0.1, 9.15), "sky_iron")
        for i in range(6):
            z = 0.6 + i * (REACH - 1.2) / 5
            m.box((-hw, -0.45, z - 0.1), (hw, -0.10, z + 0.1), "sky_iron")
        post_mat, cable_mat, beam = "sky_iron_red", "sky_chain", "sky_iron_red"
    else:
        raise ValueError(look)
    # the portal: posts set back 1.4 m (a stowed span's rails reach 1.1 m in), a beam over the walk, hinge blocks
    for sx in (-1, 1):
        x = sx * (hw + 0.45)
        R.box((x - 0.15, 0.0, -1.55), (x + 0.15, 4.6, -1.25), post_mat)
        R.bar((x, 0.0, -3.2), (x, 4.0, -1.45), 0.22, 0.22, post_mat)
        R.box((sx * (hw + 0.2) - 0.12, -0.45, -0.25), (sx * (hw + 0.2) + 0.12, 0.2, 0.15), "sky_iron")
        R.tube((x, 4.45, -1.6), (x, 4.45, -1.2), 0.22, "sky_iron", seg=10)               # sheave
    R.box((-hw - 0.6, 4.6, -1.55), (hw + 0.6, 4.9, -1.25), beam)
    sill(R, hw, "sky_stone" if look == "timber" else "sky_iron")
    cables = [stretch_node("cable_%s" % k, s.root, 0.03, cable_mat) for k in ("l", "r")]
    for c in cables:
        s.nodes[c.name] = c
    anchors = {"cable_l": ((-hw - 0.45, 4.45, -1.4), (-hw - 0.12, 0.0, 9.0)),
               "cable_r": ((hw + 0.45, 4.45, -1.4), (hw + 0.12, 0.0, 9.0))}

    def pose(d):
        sp = Rx(-90.0 * (1.0 - d))
        out = {"span": sp}
        for k, (a, b) in anchors.items():
            out[k] = aim(a, sp @ Vector(b))
        return out
    s.pose = pose
    s.cols = [deck_col("span", W, 0, REACH)] + rails_cols("span", hw - 0.05 if look == "timber" else hw + 0.08, 0, REACH)
    s.meta["seconds"] = 25
    return s.finish()


def telescope_truss(W):
    s = Style("telescope_truss", "telescope", W)
    hw = s.hw
    L, STEP = 4.6, 0.06
    sec = []
    parent = s.root
    for k in range(3):
        n = s.node("span_%s" % "abc"[k], parent)
        m = n.mesh
        top = -STEP * k
        xk = hw + 0.07 * k
        m.box((-(xk + 0.025), top - 0.05, 0.0), (xk + 0.025, top, L), "sky_steel")
        for sx in (-1, 1):
            x = sx * xk
            m.box((x - 0.025, top, 0.0), (x + 0.025, top + 0.1, L), "sky_paint_teal")             # bottom chord
            m.box((x - 0.025, top + 1.1, 0.0), (x + 0.025, top + 1.2, L), "sky_paint_teal")       # top chord
            pts = [0.0, L / 4, L / 2, 3 * L / 4, L]
            for i, z in enumerate(pts):
                zc = min(max(z, 0.03), L - 0.03)
                m.box((x - 0.02, top + 0.1, zc - 0.03), (x + 0.02, top + 1.1, zc + 0.03), "sky_paint_teal")
                if i < 4:
                    z2 = pts[i + 1]
                    ya, yb = (top + 0.1, top + 1.1) if i % 2 == 0 else (top + 1.1, top + 0.1)
                    m.bar((x, ya, zc), (x, yb, min(z2, L - 0.03)), 0.03, 0.03, "sky_paint_teal", up=(1, 0, 0))
        sec.append(n)
        parent = n
    # the shed the sections stow in
    R = s.root.mesh
    X = hw + 0.45
    for sx in (-1, 1):
        for z in (-5.3, -0.15):
            R.box((sx * X - 0.1, 0.0, z - 0.1), (sx * X + 0.1, 2.4, z + 0.1), "sky_iron")
        R.box((sx * X - 0.03, 0.9, -5.3), (sx * X + 0.03, 2.4, -0.15), "sky_paint_teal")   # cladding (open below)
    R.box((-X - 0.2, 2.4, -5.5), (X + 0.2, 2.55, 0.05), "sky_iron")                          # roof
    for sx in (-1, 1):
        R.box((sx * X - 0.15, -0.3, -5.4), (sx * X + 0.15, 0.03, 0.0), "sky_iron")            # skids

    def pose(d):
        a = ramp(d, 0.0, 1 / 3)
        return {"span_a": T(0, 0.04 * (1 - a), -4.8 + 4.8 * a),
                "span_b": T(0, 0, 4.2 * ramp(d, 1 / 3, 2 / 3)),
                "span_c": T(0, 0, 4.2 * ramp(d, 2 / 3, 1.0))}
    s.pose = pose
    for k, nm in enumerate(("span_a", "span_b", "span_c")):
        xk = hw + 0.07 * k
        s.cols.append(deck_col(nm, 2 * xk, 0.0, L, top=-STEP * k, t=0.05))
        s.cols += rails_cols(nm, xk, 0.0, L, y0=-STEP * k, h=1.2)
    s.meta["nose_y"] = -2 * STEP
    s.meta["clear"] = {"inland": 5.6}
    s.meta["seconds"] = 30
    return s.finish()


def rope_lowered(W):
    s = Style("rope_lowered", "bascule", W)
    hw = s.hw
    span = s.node("span")
    m = span.mesh
    m.box((-hw + 0.1, -0.08, 0.0), (hw - 0.1, 0.0, REACH), "sky_plank")
    for i in range(14):
        z = 0.45 + i * (REACH - 0.9) / 13
        m.box((-hw, -0.12, z - 0.07), (hw, 0.02, z + 0.07), "sky_timber_dark")        # battens
    for sx in (-1, 1):
        x = sx * (hw - 0.05)
        m.tube((x, -0.06, 0.0), (x, -0.06, REACH), 0.05, "sky_rope", seg=6)          # foot rope
        m.tube((x, 1.0, 0.0), (x, 1.0, REACH), 0.035, "sky_rope", seg=6)             # hand rope
        for i in range(9):
            z = 0.2 + i * (REACH - 0.4) / 8
            m.tube((x, -0.02, z), (x, 0.98, z), 0.018, "sky_rope", seg=4)            # hangers
    R = s.root.mesh
    for sx in (-1, 1):
        x = sx * (hw + 0.4)
        R.tube((x, -0.3, -1.4), (x, 6.2, -1.4), 0.17, "sky_timber", seg=8)
        R.tube((x, 6.2, -1.4), (x, 6.45, -1.4), 0.2, "sky_timber_dark", seg=8)
        R.box((sx * (hw + 0.15) - 0.15, -0.3, -0.3), (sx * (hw + 0.15) + 0.15, 0.15, 0.1), "sky_timber_dark")
        R.tube((x, 0.0, -1.4), (x, 0.0, -4.0), 0.03, "sky_rope", seg=4, caps=True)            # back stay, to a peg
        R.box((x - 0.1, -0.2, -4.1), (x + 0.1, 0.25, -3.9), "sky_timber_dark")
    sill(R, hw, "sky_timber_dark")
    for k in ("l", "r"):
        s.nodes["rope_" + k] = stretch_node("rope_" + k, s.root, 0.03, "sky_rope")
    anchors = {"rope_l": ((-hw - 0.4, 6.1, -1.4), (-hw - 0.05, 1.0, 8.0)),
               "rope_r": ((hw + 0.4, 6.1, -1.4), (hw - 0.05, 1.0, 8.0))}

    def pose(d):
        sp = Rx(-90.0 * (1.0 - d))
        out = {"span": sp}
        for k, (a, b) in anchors.items():
            out[k] = aim(a, sp @ Vector(b))
        return out
    s.pose = pose
    s.cols = [deck_col("span", W - 0.2, 0, REACH, t=0.08)] + rails_cols("span", hw - 0.05, 0, REACH, h=1.0)
    s.meta["seconds"] = 35
    return s.finish()


def jackknife(W):
    s = Style("jackknife", "jackknife", W)
    hw = s.hw
    H = REACH / 2

    def leaf(n, top):
        m = n.mesh
        m.box((-hw, top - 0.1, 0.0), (hw, top, H), "sky_steel")
        for sx in (-1, 1):
            m.box((sx * (hw - 0.3) - 0.1, top - 0.4, 0.0), (sx * (hw - 0.3) + 0.1, top - 0.1, H), "sky_paint_yellow")
            railing(m, sx * (hw - 0.05), 0.02, H - 0.02, top, "sky_paint_yellow")
    a = s.node("span_a")
    leaf(a, 0.0)
    for sx in (-1, 1):
        a.mesh.box((sx * hw, -0.4, 1.85), (sx * (hw + 0.22), -0.1, 2.15), "sky_iron")               # ram lug
    b = s.node("span_b", a)
    leaf(b, 0.4)
    R = s.root.mesh
    for sx in (-1, 1):
        x = sx * (hw + 0.35)
        R.box((x - 0.2, 0.0, -1.9), (x + 0.2, 1.2, -1.1), "sky_iron")                                 # ram mount
        R.box((sx * (hw + 0.2) - 0.12, -0.45, -0.25), (sx * (hw + 0.2) + 0.12, 0.2, 0.15), "sky_iron")
    sill(R, hw, "sky_iron")
    for k in ("l", "r"):
        s.nodes["ram_" + k] = stretch_node("ram_" + k, s.root, 0.08, "sky_steel", seg=8)
    anchors = {"ram_l": ((-hw - 0.35, 0.9, -1.5), (-hw - 0.11, -0.25, 2.0)),
               "ram_r": ((hw + 0.35, 0.9, -1.5), (hw + 0.11, -0.25, 2.0))}

    def pose(d):
        sa = Rx(-90.0 * (1.0 - ramp(d, 0.0, 0.5)))
        sb = T(0, -0.4, H) @ Rx(180.0 * (1.0 - ramp(d, 0.5, 1.0)))
        out = {"span_a": sa, "span_b": sb}
        for k, (p, q) in anchors.items():
            out[k] = aim(p, sa @ Vector(q))
        return out
    s.pose = pose
    s.cols = [deck_col("span_a", W, 0, H, t=0.1), deck_col("span_b", W, 0, H, top=0.4, t=0.1)]
    s.cols += rails_cols("span_a", hw - 0.05, 0, H) + rails_cols("span_b", hw - 0.05, 0, H, y0=0.4)
    s.meta["seconds"] = 30
    return s.finish()


def swing_girder(W):
    s = Style("swing_girder", "swing", W)
    hw = s.hw
    px = -(hw + 0.5)
    span = s.node("span")
    m = span.mesh
    c = hw + 0.5                         # the deck's centre line, from the pivot
    m.box((c - hw, -0.12, 0.0), (c + hw, 0.0, REACH), "sky_steel")
    for sx in (-1, 1):
        x = c + sx * (hw - 0.3)
        m.box((x - 0.12, -0.6, 0.0), (x + 0.12, -0.12, REACH), "sky_iron")
        railing(m, c + sx * (hw - 0.05), 0.0, REACH, 0.0, "sky_iron")
    m.box((-0.3, -0.6, -0.3), (c - hw + 0.05, 0.0, 0.6), "sky_iron")                  # heel arm onto the pivot
    m.tube((0, -0.6, 0), (0, 4.6, 0), 0.16, "sky_iron", seg=10)                         # king post
    for z in (5.0, 9.0, REACH - 0.2):
        m.bar((0.0, 4.4, 0.0), (c - hw + 0.02, 0.0, z), 0.05, 0.05, "sky_chain")          # stays
    m.bar((0.0, 4.4, 0.0), (0.0, 0.0, -2.0), 0.05, 0.05, "sky_chain")                    # back stay
    m.box((-0.25, -0.2, -2.15), (0.25, 0.25, -1.85), "sky_stone")                         # its counterweight
    R = s.root.mesh
    R.tube((px, -1.4, 0.0), (px, -0.62, 0.0), 0.5, "sky_stone", seg=12)                   # pedestal on the face
    R.tube((px, -0.62, 0.0), (px, -0.6, 0.0), 0.42, "sky_brass", seg=12)
    sill(R, hw, "sky_stone")

    def pose(d):
        return {"span": T(px, 0, 0) @ Ry(-90.0 * (1.0 - d))}
    s.pose = pose
    s.cols = [{"node": "span", "center": [c, -0.06, REACH / 2], "size": [W, 0.12, REACH]}]
    s.cols += [{"node": "span", "center": [c + sx * (hw - 0.05), RAIL_H / 2, REACH / 2], "size": [0.1, RAIL_H, REACH]} for sx in (-1, 1)]
    s.meta["clear"] = {"along": [round(px - REACH - 0.3, 2), round(px + 0.6, 2)], "out": W + 1.0}
    s.meta["seconds"] = 25
    return s.finish()


def rolling_lift(W):
    """a Scherzer rolling lift: quadrant girders beside the walk roll back on toothed tracks as the span rises"""
    s = Style("rolling_lift", "roll", W)
    hw = s.hw
    Rr, CY, CZ, TRACK = 2.0, 2.25, -0.6, 0.25
    span = s.node("span")
    m = span.mesh
    # the span frame's origin is the rolling circle's centre; the deck lies (CY) below it, from z 0 (-CZ) out
    z0, z1 = -CZ, REACH - CZ
    m.box((-hw, -CY - 0.12, z0), (hw, -CY, z1), "sky_steel")
    xs = hw + 0.25
    for sx in (-1, 1):
        x = sx * xs
        m.box((x - 0.06, -CY - 0.45, z0), (x + 0.06, -CY + 1.0, z1), "sky_paint_white")      # side girder / parapet
        arc = [(0.0, 0.0)] + [(-Rr * math.sin(math.radians(t)), -Rr * math.cos(math.radians(t))) for t in range(0, 91, 10)]
        m.slab([(zz, yy) for zz, yy in arc], 0.12, "sky_paint_white", T(x, 0, 0) @ Ry(-90))
        m.bar((x, 0.0, 0.0), (x, -CY + 0.9, z0 + 2.5), 0.12, 0.12, "sky_paint_white", up=(1, 0, 0))
        m.bar((x, -Rr, 0.0), (x, -CY - 0.3, z0 + 0.8), 0.12, 0.12, "sky_paint_white", up=(1, 0, 0))
    for sx in (-1, 1):
        railing(m, sx * (hw - 0.05), z0, z1, -CY, "sky_iron")
    m.box((-xs - 0.06, 0.15, -1.6), (xs + 0.06, 0.75, -0.4), "sky_stone")                     # counterweight, overhead
    R = s.root.mesh
    zt0, zt1 = CZ - Rr * math.pi / 2 - 0.4, CZ + 0.5
    for sx in (-1, 1):
        x = sx * xs
        R.box((x - 0.15, 0.0, zt0), (x + 0.15, TRACK, zt1), "sky_iron")
        for i in range(8):
            z = zt0 + 0.2 + i * (zt1 - zt0 - 0.4) / 7
            R.box((x - 0.17, TRACK - 0.02, z - 0.05), (x + 0.17, TRACK + 0.02, z + 0.05), "sky_steel")   # rack teeth
    sill(R, hw, "sky_stone")

    def pose(d):
        th = -90.0 * (1.0 - d)
        return {"span": T(0, CY, CZ + Rr * math.radians(th)) @ Rx(th)}
    s.pose = pose
    s.cols = [{"node": "span", "center": [0, -CY - 0.06, (z0 + z1) / 2], "size": [W, 0.12, REACH]}]
    s.cols += [{"node": "span", "center": [sx * (hw - 0.05), -CY + RAIL_H / 2, (z0 + z1) / 2], "size": [0.1, RAIL_H, REACH]} for sx in (-1, 1)]
    s.meta["clear"] = {"inland": 4.6}
    s.meta["seconds"] = 30
    return s.finish()


def scissor_lattice(W):
    """lazy tongs under four nested deck plates, stowed in a slot below the deck"""
    s = Style("scissor_lattice", "scissor", W)
    hw = s.hw
    N, Lc, BASE = 5, 3.4, -3.0
    PL, STEP = 3.5, 0.06
    plates = []
    for k in range(4):
        n = s.node("plate_%d" % k)
        m = n.mesh
        half = hw + 0.08 * k
        top = -STEP * k
        m.box((-half, top - 0.05, 0.0), (half, top, PL), "sky_steel")
        for sx in (-1, 1):
            railing(m, sx * (half - 0.03), 0.02, PL - 0.02, top, "sky_paint_yellow", every=1.2, mid=False)
        plates.append(n)
    arms = []
    for i in range(N):
        for j, y in ((0, -0.40), (1, -0.50)):
            n = s.node("arm_%d_%d" % (i, j))
            n.mesh.box((-0.04, -0.04, -Lc / 2), (0.04, 0.04, Lc / 2), "sky_iron")
            n.mesh.tube((0, -0.05, -Lc / 2), (0, 0.05, -Lc / 2), 0.07, "sky_steel", seg=6)
            arms.append((n, i, j, y))
    R = s.root.mesh
    for sx in (-1, 1):
        R.box((sx * (hw + 0.5) - 0.1, -0.6, -0.15), (sx * (hw + 0.5) + 0.1, 1.2, 0.15), "sky_paint_yellow")
    R.box((-hw - 0.6, -0.65, -0.12), (hw + 0.6, -0.55, 0.12), "sky_iron")                     # slot lintel, under
    R.box((-0.3, -0.6, BASE - 0.2), (0.3, -0.3, BASE + 0.1), "sky_iron")                      # the tongs' anchor

    def pose(d):
        ext = 3.0 + (REACH + 3.0 - 3.0) * d
        phi = math.acos(min(0.999, ext / (N * Lc)))
        out = {}
        for n, i, j, y in arms:
            zc = BASE + (i + 0.5) * Lc * math.cos(phi)
            out[n.name] = T(0, y, zc) @ Ry(math.degrees(phi if j == 0 else -phi))
        for k, n in enumerate(plates):
            start = (REACH - PL) * k / 3
            out[n.name] = T(0, -0.02 * (1 - d), -PL + (start + PL) * d)
        return out
    s.pose = pose
    for k in range(4):
        half = hw + 0.08 * k
        s.cols.append(deck_col("plate_%d" % k, 2 * half, 0, PL, top=-STEP * k, t=0.05))
        s.cols += rails_cols("plate_%d" % k, half - 0.03, 0, PL, y0=-STEP * k)
    s.meta["nose_y"] = -3 * STEP
    s.meta["clear"] = {"inland": 3.8, "below": 0.7}
    s.meta["seconds"] = 25
    return s.finish()


def gangplank_rail(W):
    s = Style("gangplank_rail", "plank", W)
    hw = s.hw
    p = s.node("plank")
    m = p.mesh
    m.box((-hw, -0.15, 0.0), (hw, 0.0, REACH), "sky_plank")
    for i in range(10):
        z = 0.3 + i * (REACH - 0.6) / 9
        m.box((-hw - 0.02, -0.25, z - 0.06), (hw + 0.02, -0.15, z + 0.06), "sky_timber_dark")
    for sx in (-1, 1):
        railing(m, sx * (hw - 0.05), 0.02, REACH - 0.02, 0.0, "sky_rope", every=1.3)
    R = s.root.mesh
    LIFT = 0.5
    for z in (-0.4, -5.0, -10.0):
        for sx in (-1, 1):
            R.box((sx * (hw + 0.15) - 0.1, 0.0, z - 0.1), (sx * (hw + 0.15) + 0.1, LIFT - 0.15, z + 0.1), "sky_timber_dark")
        R.tube((-hw - 0.1, LIFT - 0.25 - 0.1, z), (hw + 0.1, LIFT - 0.25 - 0.1, z), 0.1, "sky_steel", seg=8)   # roller

    def pose(d):
        a = ramp(d, 0.0, 0.75)
        return {"plank": T(0, LIFT * (1 - ramp(d, 0.75, 1.0)), -12.8 * (1 - a))}
    s.pose = pose
    s.cols = [deck_col("plank", W, 0, REACH, t=0.15)] + rails_cols("plank", hw - 0.05, 0, REACH)
    s.meta["clear"] = {"inland": 13.2}
    s.meta["seconds"] = 30
    return s.finish()


def chain_drawbridge(W):
    s = Style("chain_drawbridge", "bascule", W)
    hw = s.hw
    span = s.node("span")
    m = span.mesh
    m.box((-hw, -0.18, 0.0), (hw, 0.0, REACH), "sky_timber")
    for i in range(8):
        z = 0.4 + i * (REACH - 0.8) / 7
        m.box((-hw - 0.01, -0.2, z - 0.06), (hw + 0.01, 0.01, z + 0.06), "sky_iron")             # iron bands
    for sx in (-1, 1):
        railing(m, sx * (hw - 0.05), 0.0, REACH, 0.0, "sky_timber_dark")
        m.box((sx * hw, -0.18, 5.85), (sx * (hw + 0.18), 0.1, 6.15), "sky_iron")
    R = s.root.mesh
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (hw + 0.3), sx * (hw + 1.5)))
        R.box((x0, 0.0, -2.6), (x1, 6.0, 0.0), "sky_stone")
        for k in range(2):                                                                         # merlons
            z = -2.3 + k * 1.6
            R.box((x0 + 0.1, 6.0, z), (x1 - 0.1, 6.6, z + 0.7), "sky_stone")
        R.box((sx * (hw + 0.2) - 0.1, -0.4, -0.2), (sx * (hw + 0.2) + 0.1, 0.25, 0.1), "sky_iron")
    R.box((-hw - 0.3, 4.2, -2.6), (hw + 0.3, 5.2, -1.4), "sky_stone")                            # lintel
    sill(R, hw, "sky_stone")
    for k in ("l", "r"):
        s.nodes["chain_" + k] = stretch_node("chain_" + k, s.root, 0.045, "sky_chain")
    anchors = {"chain_l": ((-hw - 0.35, 5.4, -0.05), (-hw - 0.1, 0.0, 6.0)),
               "chain_r": ((hw + 0.35, 5.4, -0.05), (hw + 0.1, 0.0, 6.0))}

    def pose(d):
        sp = Rx(-90.0 * (1.0 - d))
        out = {"span": sp}
        for k, (a, b) in anchors.items():
            out[k] = aim(a, sp @ Vector(b))
        return out
    s.pose = pose
    s.cols = [deck_col("span", W, 0, REACH, t=0.18)] + rails_cols("span", hw - 0.05, 0, REACH)
    s.meta["seconds"] = 30
    return s.finish()


STYLES = {
    "bascule_timber": lambda W: bascule("bascule_timber", W, "timber"),
    "bascule_iron": lambda W: bascule("bascule_iron", W, "iron"),
    "telescope_truss": telescope_truss,
    "rope_lowered": rope_lowered,
    "jackknife": jackknife,
    "swing_girder": swing_girder,
    "rolling_lift": rolling_lift,
    "scissor_lattice": scissor_lattice,
    "gangplank_rail": gangplank_rail,
    "chain_drawbridge": chain_drawbridge,
}


# ---------------------------------------------------------------- keys
def _lerp_xf(a, b, t):
    la, ra, sa = a.decompose()
    lb, rb, sb = b.decompose()
    return Matrix.LocRotScale(la.lerp(lb, t), ra.slerp(rb, t), sa.lerp(sb, t))


def _xf_err(a, b, probe=6.0):
    """the largest distance a few probe points move between two transforms"""
    pts = [Vector((0, 0, 0)), Vector((0, 0, probe)), Vector((0, probe, 0)), Vector((probe, 0, 0))]
    return max(((a @ p) - (b @ p)).length for p in pts)


def keys(style, samples=41, tol=0.03):
    """piecewise-linear keys per moving node: greedy -- drop a sample while straight interpolation between the kept
    neighbours stays within tol metres (probe points up to 13 m out) at every dropped sample"""
    ds = [i / (samples - 1) for i in range(samples)]
    poses = [style.pose(d) for d in ds]
    out = {}
    for name in poses[0]:
        xs = [p[name] for p in poses]
        stretch = any(abs(x.to_scale().z - 1.0) > 1e-3 for x in xs)
        probe = 1.0 if stretch else REACH          # (a stretch node's local +Z is the whole cable: its tip is (0, 0, 1))
        kept = [0]
        i = 0
        while i < samples - 1:
            j = i + 1
            while j + 1 < samples:
                ok = True
                for k in range(i + 1, j + 2):
                    t = (ds[k] - ds[i]) / (ds[j + 1] - ds[i])
                    if _xf_err(_lerp_xf(xs[i], xs[j + 1], t), xs[k], probe) > tol:
                        ok = False
                        break
                if not ok:
                    break
                j += 1
            kept.append(j)
            i = j
        out[name] = [(ds[k], xs[k]) for k in kept]
    return out
