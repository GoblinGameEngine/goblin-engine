"""parts_props.py -- the sky islands' shared props (game frame: +Y up; parts that stand at an island's edge face +Z out).

Each builder returns (root Node, meta): meta has "attach" {node: note}, "notes", optional "collision" boxes (local),
and the game places every part many times (MultiMesh for the small repeated ones: fence, moss, vines).
"""
import math

from mathutils import Matrix, Vector

from parts_lib import Node, T, Rx, Ry, Rz


def balloon(seg=24, bands=True, name="balloon"):
    """the lifting envelope: 100 m across, 1,000 m tall, rounded ends; origin at its lowest point, +Y up.
    Gores alternate two canvas tones; a few rigging bands girdle it (near variant only)."""
    root = Node(name)
    m = root.mesh
    Rb, H = 50.0, 1000.0
    prof = [(0.0, 0.0)]
    for t in (20, 40, 60, 75):
        a = math.radians(t)
        prof.append((Rb * math.sin(a), Rb - Rb * math.cos(a)))
    prof += [(Rb, Rb), (Rb, H - Rb)]
    for t in (75, 60, 40, 20):
        a = math.radians(t)
        prof.append((Rb * math.sin(a), H - Rb + Rb * math.cos(a)))
    prof.append((0.0, H))
    m.lathe(prof, (lambda k: "sky_canvas" if k % 2 == 0 else "sky_canvas_stripe") if bands else "sky_canvas", seg=seg)
    if bands:
        for y in (180.0, 420.0, 660.0, 880.0):
            m.lathe([(0.0, y - 1.5), (Rb + 0.6, y - 1.5), (Rb + 0.6, y + 1.5), (0.0, y + 1.5)], "sky_rope", seg=seg, smooth=False)
    meta = {"size": [100.0, 1000.0, 100.0], "attach": {"(origin)": "the envelope's lowest point: hang the hub here"},
            "notes": "unit envelope at real size (scale freely); 'balloon' near, 'balloon_far' for distance"}
    return root, meta


def balloon_hub():
    """the load ring under an envelope: a spider of struts from the envelope's foot to a ring; tether_0..7 on the
    ring, 'line' under it where the island's lines meet.  Origin at the top (the envelope's foot)."""
    root = Node("balloon_hub")
    m = root.mesh
    RR, DROP = 14.0, 22.0
    m.tube((0, -0.5, 0), (0, 0.5, 0), 3.0, "sky_iron", seg=12)                    # crown plate
    ring = []
    n = 8
    for k in range(n):
        a = 2 * math.pi * k / n
        ring.append(Vector((RR * math.cos(a), -DROP, -RR * math.sin(a))))
    for k in range(n):
        m.tube(ring[k], ring[(k + 1) % n], 0.35, "sky_iron", seg=6)
        m.tube((0, 0, 0), ring[k], 0.12, "sky_rope", seg=5)
        Node("tether_%d" % k, root, T(*ring[k]))
        m.tube(ring[k] + Vector((0, 0.5, 0)), ring[k] - Vector((0, 0.7, 0)), 0.5, "sky_brass", seg=8)
    for k in range(n):
        m.tube(ring[k], (0, -DROP - 8.0, 0), 0.1, "sky_rope", seg=5)
    Node("line", root, T(0, -DROP - 8.0, 0))
    m.lathe([(0.0, -DROP - 8.6), (0.7, -DROP - 8.3), (0.7, -DROP - 7.7), (0.0, -DROP - 7.4)], "sky_brass", seg=8)
    meta = {"attach": {"tether_0..7": "ring points (local) for rigging lines", "line": "where the island's tethers meet"},
            "notes": "hang from the balloon's origin; the game draws the tethers from 'line' (or the ring) to the deck anchors"}
    return root, meta


def fence(gate=False):
    """a 3 m safety-fence segment along +X from x 0 (its post at 0; the next segment brings the next post), 1.4 m tall,
    the outside at +Z.  The gate: a 1.2 m leaf 'leaf' hinged at x 0.9, swinging about +Y."""
    root = Node("fence_gate" if gate else "fence")
    m = root.mesh
    H, P = 1.4, 0.08
    m.box((-P / 2, 0.0, -P / 2), (P / 2, H + 0.05, P / 2), "sky_iron")
    spans = [(0.0, 3.0)] if not gate else [(0.0, 0.9), (2.1, 3.0)]
    for x0, x1 in spans:
        a, b = x0 + (P / 2 if x0 == 0 else 0.0), x1
        m.box((a, H - 0.05, -0.03), (b, H, 0.03), "sky_iron")
        for y in (0.45, 0.9):
            m.box((a, y - 0.02, -0.02), (b, y + 0.02, 0.02), "sky_iron")
        m.box((a, 0.0, -0.015), (b, 0.15, 0.015), "sky_paint_yellow")                    # toe board
    meta = {"size": [3.0, 1.4, 0.08], "attach": {}, "collision": [{"center": [1.5, 0.7, 0.0], "size": [3.0, 1.4, 0.1]}],
            "notes": "chain along the fence line; MultiMesh it"}
    if gate:
        for x in (0.9, 2.1):
            m.box((x - P / 2, 0.0, -P / 2), (x + P / 2, H + 0.05, P / 2), "sky_iron")
        leaf = Node("leaf", root, T(0.95, 0, 0))
        lm = leaf.mesh
        lm.box((0.0, 0.05, -0.02), (1.1, 0.09, 0.02), "sky_iron")
        lm.box((0.0, H - 0.09, -0.025), (1.1, H - 0.05, 0.025), "sky_iron")
        lm.box((0.0, 0.05, -0.02), (0.04, H - 0.05, 0.02), "sky_iron")
        lm.box((1.06, 0.05, -0.02), (1.1, H - 0.05, 0.02), "sky_iron")
        lm.bar((0.04, 0.09, 0), (1.06, H - 0.09, 0), 0.03, 0.03, "sky_iron", up=(0, 0, 1))
        meta["attach"] = {"leaf": "hinge at x 0.95; swing about +Y (0..+-100 deg)"}
        meta["collision"] = [{"center": [0.45, 0.7, 0.0], "size": [0.9, 1.4, 0.1]}, {"center": [2.55, 0.7, 0.0], "size": [0.9, 1.4, 0.1]}]
    return root, meta


def hoist():
    """a cargo davit at the deck's edge: plinth, mast, a slewing jib reaching 4.5 m out over +Z, winch drum;
    'slew' turns about +Y; 'hook' is where the line leaves the jib's sheave."""
    root = Node("hoist")
    m = root.mesh
    m.box((-0.9, 0.0, -0.9), (0.9, 0.4, 0.9), "sky_stone")
    slew = Node("slew", root, T(0, 0.4, 0))
    s = slew.mesh
    s.tube((0, 0, 0), (0, 0.3, 0), 0.7, "sky_iron", seg=12)
    s.tube((0, 0.3, 0), (0, 4.8, 0), 0.22, "sky_paint_yellow", seg=10)
    s.bar((0, 4.6, -0.8), (0, 4.6, 4.5), 0.3, 0.35, "sky_paint_yellow")                  # jib
    s.bar((0, 4.8, 0), (0, 4.75, 4.3), 0.05, 0.05, "sky_chain")
    s.bar((0, 1.6, 0.2), (0, 4.45, 2.6), 0.14, 0.14, "sky_paint_yellow")                 # strut
    s.tube((-0.45, 1.3, -0.45), (0.45, 1.3, -0.45), 0.35, "sky_iron", seg=12)           # winch drum
    s.box((-0.55, 0.3, -0.8), (0.55, 1.0, -0.15), "sky_iron")                            # motor house
    s.tube((-0.12, 4.3, 4.35), (0.12, 4.3, 4.35), 0.28, "sky_steel", seg=10)            # sheave
    s.box((-0.4, 4.4, -1.4), (0.4, 4.9, -0.8), "sky_stone")                              # counterweight
    Node("hook", slew, T(0, 4.0, 4.35))
    meta = {"size": [1.8, 5.3, 6.0], "attach": {"slew": "turns about +Y", "hook": "line exit; the game draws the line down to the container's 'bridle'"},
            "collision": [{"center": [0, 0.2, 0], "size": [1.8, 0.4, 1.8]}, {"center": [0, 2.6, 0], "size": [0.5, 4.4, 0.5]}],
            "notes": "stand at the deck edge with +Z out; the jib reaches 4.35 m past the plinth's centre"}
    return root, meta


def container():
    """a sky-trade crate, 3.0 x 2.4 x 2.4 m, ribbed, doors at +X, a four-leg bridle to 'bridle' 2 m over its top.
    Origin bottom centre."""
    root = Node("container")
    m = root.mesh
    L, W, H = 3.0, 2.4, 2.4
    m.box((-L / 2 + 0.06, 0.06, -W / 2 + 0.03), (L / 2 - 0.06, H - 0.06, W / 2 - 0.03), "sky_crate")
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * (L / 2 - 0.06), sz * (W / 2 - 0.06)
            m.box((x - 0.06, 0.0, z - 0.06), (x + 0.06, H, z + 0.06), "sky_crate_band")
    for y in (0.03, H - 0.03):
        for sz in (-1, 1):
            m.box((-L / 2 + 0.12, y - 0.03, sz * (W / 2 - 0.04)), (L / 2 - 0.12, y + 0.03, sz * W / 2), "sky_crate_band")
    for i in range(1, 6):
        x = -L / 2 + i * L / 6
        for sz in (-1, 1):
            m.box((x - 0.04, 0.12, sz * (W / 2 - 0.03) - 0.02), (x + 0.04, H - 0.12, sz * (W / 2 - 0.03) + 0.02), "sky_crate")
    m.box((L / 2 - 0.06, 0.15, -0.02), (L / 2 - 0.02, H - 0.15, 0.02), "sky_crate_band")   # door seam
    top = Vector((0, H + 2.0, 0))
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.tube((sx * (L / 2 - 0.06), H, sz * (W / 2 - 0.06)), top, 0.03, "sky_rope", seg=4)
    m.lathe([(0.0, H + 1.9), (0.18, H + 1.95), (0.18, H + 2.15), (0.0, H + 2.2)], "sky_brass", seg=8)
    Node("bridle", root, T(*top))
    meta = {"size": [L, H + 2.2, W], "attach": {"bridle": "the hoist line's hook"},
            "collision": [{"center": [0, H / 2, 0], "size": [L, H, W]}], "notes": "a RigidBody/AnimatableBody in the game (it moves)"}
    return root, meta


def launcher():
    """the line-rocket launcher: a pedestal, 'yaw' (about +Y), 'pitch' (about +X at the trunnions), twin tubes along
    +Z with 'muzzle' at the upper tube's mouth; a line reel on the side."""
    root = Node("launcher")
    m = root.mesh
    m.tube((0, 0, 0), (0, 0.2, 0), 0.6, "sky_iron", seg=10)
    m.tube((0, 0.2, 0), (0, 1.0, 0), 0.18, "sky_iron", seg=8)
    yaw = Node("yaw", root, T(0, 1.0, 0))
    ym = yaw.mesh
    ym.tube((0, 0, 0), (0, 0.15, 0), 0.4, "sky_paint_teal", seg=10)
    for sx in (-1, 1):
        ym.box((sx * 0.38 - 0.05, 0.15, -0.15), (sx * 0.38 + 0.05, 0.7, 0.15), "sky_paint_teal")
    ym.tube((0.5, 0.5, -0.4), (0.8, 0.5, -0.4), 0.3, "sky_rope", seg=10)                 # the line reel
    pitch = Node("pitch", yaw, T(0, 0.55, 0))
    pm = pitch.mesh
    pm.tube((-0.33, 0, 0), (0.33, 0, 0), 0.08, "sky_steel", seg=8)
    for y in (0.0, 0.26):
        pm.tube((0, y, -0.6), (0, y, 1.3), 0.11, "sky_paint_teal", seg=10)
    pm.box((-0.16, -0.1, -0.2), (0.16, 0.36, 0.2), "sky_paint_teal")
    Node("muzzle", pitch, T(0, 0.26, 1.35))
    meta = {"size": [1.2, 1.9, 2.0], "attach": {"yaw": "about +Y", "pitch": "about +X (raise: negative angle lifts +Z)", "muzzle": "the rocket leaves here, trailing the line"},
            "collision": [{"center": [0, 0.5, 0], "size": [1.2, 1.0, 1.2]}]}
    return root, meta


def rocket():
    root = Node("rocket")
    m = root.mesh
    m.lathe([(0.0, 0.0), (0.06, 0.02), (0.06, 0.95), (0.045, 1.08), (0.0, 1.2)], "sky_rocket", seg=8, axis_m=Rx(90))
    for k in range(3):
        a = 120 * k
        m.obox(Rz(a) @ T(0.12, 0, 0.12), (0.14, 0.012, 0.24), "sky_iron")
    Node("tail", root, T(0, 0, 0))
    meta = {"size": [0.4, 0.4, 1.2], "attach": {"tail": "the line's end"}, "notes": "points +Z; fly it along the line's arc"}
    return root, meta


def pad():
    """an aerostat pad marking: a 12 m disc 3 cm proud of the deck with a yellow ring and two landing bars along +Z"""
    root = Node("pad")
    m = root.mesh
    m.lathe([(0.0, 0.0), (6.0, 0.0), (6.0, 0.03), (0.0, 0.03)], "sky_pad", seg=32, smooth=False)
    # ring: 16 short raised blocks round r 5.2 (no coplanar faces: 1 cm proud)
    for k in range(16):
        a = 2 * math.pi * k / 16
        mm = T(5.2 * math.cos(a), 0.035, -5.2 * math.sin(a)) @ Ry(math.degrees(a))
        m.obox(mm, (0.35, 0.012, 1.8), "sky_pad_mark")
    for x in (-0.9, 0.9):                                                        # two landing bars
        m.box((x - 0.25, 0.03, -2.2), (x + 0.25, 0.042, 2.2), "sky_pad_mark")
    meta = {"size": [12.0, 0.04, 12.0], "attach": {}, "notes": "lay on flat deck"}
    return root, meta


def roof_hatch():
    """a standalone roof bulkhead hatch: a 1.2 m curb with a lid 'lid' hinged at its -Z edge"""
    root = Node("roof_hatch")
    m = root.mesh
    for c0, c1 in (((-0.65, 0, -0.65), (0.65, 0.5, -0.55)), ((-0.65, 0, 0.55), (0.65, 0.5, 0.65)),
                   ((-0.65, 0, -0.55), (-0.55, 0.5, 0.55)), ((0.55, 0, -0.55), (0.65, 0.5, 0.55))):
        m.box(c0, c1, "sky_iron")
    lid = Node("lid", root, T(0, 0.5, -0.65))
    lid.mesh.box((-0.7, 0.0, 0.0), (0.7, 0.06, 1.3), "sky_paint_teal")
    lid.mesh.box((-0.1, 0.06, 1.1), (0.1, 0.12, 1.25), "sky_brass")
    meta = {"size": [1.4, 0.6, 1.4], "attach": {"lid": "hinged about +X at the -Z edge (open: rotate -100 deg)"},
            "collision": [{"center": [0, 0.28, 0], "size": [1.3, 0.56, 1.3]}]}
    return root, meta


def cloud_net():
    """a rooftop cloud net (water catcher): two 5 m masts, an 8 x 4 m net, a gutter trough and a tank"""
    root = Node("cloud_net")
    m = root.mesh
    W, Y0, Y1 = 8.0, 1.0, 5.0
    for x in (-W / 2, W / 2):
        m.tube((x, 0, 0), (x, Y1 + 0.2, 0), 0.08, "sky_timber_dark", seg=6)
        m.tube((x, Y1, 0), (x * 1.2, 0.0, -1.5), 0.02, "sky_rope", seg=4)                 # guys
        m.tube((x, Y1, 0), (x * 1.2, 0.0, 1.5), 0.02, "sky_rope", seg=4)
    m.box((-W / 2, Y1 - 0.04, -0.04), (W / 2, Y1 + 0.04, 0.04), "sky_timber_dark")
    for i in range(1, 20):
        x = -W / 2 + i * W / 20
        m.box((x - 0.006, Y0, -0.006), (x + 0.006, Y1 - 0.04, 0.006), "sky_net")
    for j in range(1, 10):
        y = Y0 + j * (Y1 - Y0) / 10
        m.box((-W / 2 + 0.08, y - 0.006, -0.006), (W / 2 - 0.08, y + 0.006, 0.006), "sky_net")
    m.box((-W / 2, Y0 - 0.2, -0.2), (W / 2, Y0, 0.2), "sky_steel")                           # trough
    m.box((-W / 2 + 0.3, 0.0, -0.05), (-W / 2 + 0.4, Y0 - 0.2, 0.05), "sky_steel")
    m.box((W / 2 - 0.4, 0.0, -0.05), (W / 2 - 0.3, Y0 - 0.2, 0.05), "sky_steel")
    m.lathe([(0.0, 0.0), (0.7, 0.0), (0.7, 1.4), (0.0, 1.4)], "sky_steel", seg=12, axis_m=T(W / 2 + 1.0, 0, 0))   # tank
    meta = {"size": [10.0, 5.2, 3.0], "attach": {}, "collision": [{"center": [W / 2 + 1.0, 0.7, 0], "size": [1.4, 1.4, 1.4]}],
            "notes": "rooftops and ridges; face it across the wind (the net's plane is X-Y)"}
    return root, meta


def moss_card(seed, w=2.0, h=3.0, name="moss"):
    """a hanging moss card: a ragged curtain from y 0 down to -h, a thin double-sided plate (sky_moss, two-sided)"""
    import random
    rnd = random.Random(seed)
    root = Node(name)
    m = root.mesh
    n = 9
    poly = [(-w / 2, 0.0), (w / 2, 0.0)]
    pts = []
    for i in range(n + 1):
        x = w / 2 - w * i / n
        y = -h * (0.35 + 0.65 * rnd.random()) if i % 2 == 0 else -h * (0.15 + 0.35 * rnd.random())
        pts.append((x, y))
    poly += pts
    m.slab(poly, 0.01, "sky_moss", Matrix.Identity(4))
    meta = {"size": [w, h, 0.01], "attach": {}, "notes": "hang under the rock's rim, origin at the top edge; MultiMesh, random yaw/scale"}
    return root, meta


def vine(seed, length=6.0, name="vine"):
    """a vine strand hanging from y 0: a tapered, gently wandering stem with leaf blades"""
    import random
    rnd = random.Random(seed)
    root = Node(name)
    m = root.mesh
    p = Vector((0, 0, 0))
    segs = 6
    r = 0.035
    for i in range(segs):
        q = p + Vector((rnd.uniform(-0.25, 0.25), -length / segs, rnd.uniform(-0.25, 0.25)))
        r1 = r * 0.8
        m.tube(p, q, r, "sky_vine", seg=5, r1=r1)
        for _ in range(2):
            c = p.lerp(q, rnd.random())
            a = rnd.uniform(0, 360)
            leaf = T(*c) @ Ry(a) @ Rx(rnd.uniform(-40, 10)) @ T(0, 0, 0.14)
            m.slab([(0.0, -0.14), (0.07, -0.05), (0.0, 0.14), (-0.07, -0.05)], 0.008, "sky_leaf", leaf @ Rx(90))
        p, r = q, r1
    meta = {"size": [0.6, length, 0.6], "attach": {}, "notes": "hang from the rock's rim; MultiMesh, random yaw/scale 0.5..2"}
    return root, meta


def pond_edge():
    """a 2 m pond-edge kerb piece (stones in a gentle curve) for the runtime to chain round water outlines"""
    import random
    rnd = random.Random(7)
    root = Node("pond_edge")
    m = root.mesh
    x = 0.0
    while x < 2.0:
        w = rnd.uniform(0.3, 0.5)
        m.lathe([(0.0, -0.1), (w * 0.5, -0.1), (w * 0.55, 0.08), (w * 0.35, 0.18), (0.0, 0.2)], "sky_stone", seg=6,
                axis_m=T(x + w / 2, 0, rnd.uniform(-0.08, 0.08)), smooth=True)
        x += w * 0.9
    meta = {"size": [2.0, 0.2, 0.5], "attach": {}, "notes": "chain along a pond outline (MultiMesh)"}
    return root, meta


def props():
    """(file name, builder) for every prop"""
    return [
        ("balloon", lambda: balloon()),
        ("balloon_far", lambda: balloon(seg=12, bands=False, name="balloon_far")),
        ("balloon_hub", balloon_hub),
        ("fence", lambda: fence(False)),
        ("fence_gate", lambda: fence(True)),
        ("hoist", hoist),
        ("container", container),
        ("launcher", launcher),
        ("rocket", rocket),
        ("pad", pad),
        ("roof_hatch", roof_hatch),
        ("cloud_net", cloud_net),
        ("moss_a", lambda: moss_card(1, 2.0, 3.0, "moss_a")),
        ("moss_b", lambda: moss_card(2, 1.6, 4.5, "moss_b")),
        ("vine_a", lambda: vine(3, 6.0, "vine_a")),
        ("vine_b", lambda: vine(4, 9.0, "vine_b")),
        ("pond_edge", pond_edge),
    ]
