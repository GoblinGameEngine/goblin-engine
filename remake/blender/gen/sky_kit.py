"""
sky_kit.py -- the sky islands' shared building components (research/sky_islands/architecture/00_brief.md, "Round-2
build contract"): the generator stream's own implementation of the contract's SC API, used by gen/sky.py until (and
unless) the components stream's package replaces it.

Every component is an item function `name(p, pos, yaw, ...)`: p a gblib Part, pos (x, y, z) its anchor in the building's
plan frame (metres; x east, y north = the building's front, z up), yaw in DEGREES about z (0: the component faces +y,
out of a front wall).  Each builds its geometry deterministically in its own frame, so gbkit (installed by
build_record.py) recognises two calls that make the same geometry as one shared piece: a facade of forty identical
bay windows costs one bay window.  Keep the arguments few and quantised (sizes rounded to 5 cm) so repeats really
repeat.

Materials are keys the generator defines (sky.py style_materials): ext, ext2, trim, accent, wood, iron, glass, roof_m,
tin, lattice, stone, tile, canvas, lamp.
"""
import math

from mathutils import Vector

Q = 0.05


def q(v):
    return round(round(v / Q) * Q, 3)


class F:
    """an item's frame: pos + yaw (degrees); local x right along the wall, y out of it, z up"""

    def __init__(self, pos, yaw):
        self.o = Vector(pos)
        a = math.radians(yaw)
        self.u = Vector((math.cos(a), math.sin(a), 0.0))
        self.v = Vector((-math.sin(a), math.cos(a), 0.0))
        self.w = Vector((0.0, 0.0, 1.0))

    def P(self, x, y, z):
        return tuple(self.o + self.u * x + self.v * y + self.w * z)

    def box(self, p, lo, hi, mat, mats=None):
        p.obox((self.o, self.u, self.v, self.w), lo, hi, mat, mats)

    def quad(self, p, pts, mat):
        p.face([self.P(*c) for c in pts], mat)

    def cyl(self, p, c, r, z0, z1, mat, n=12, r1=None, caps=True):
        """a vertical cylinder at local (c.x, c.y) (its axis is z, so the yaw doesn't matter but the centre does)"""
        cc = self.P(c[0], c[1], 0.0)
        p.cylinder((cc[0], cc[1]), r, cc[2] + z0, cc[2] + z1, mat, n=n, caps=caps, r1=r1)


def _dome(p, f, c, r, z0, mat, rings=5, n=14, onion=False):
    """a dome (or onion) of radius r on a drum top at z0, centred at local c"""
    cc = f.P(c[0], c[1], 0.0)
    prof = []
    for k in range(rings + 1):
        t = k / rings
        if onion:
            # bulges out past the drum, then draws in to a point
            rr = r * (1.0 + 0.35 * math.sin(math.pi * min(1.0, t * 1.6))) * (1.0 - t) ** 0.85
            zz = r * 1.6 * t
        else:
            rr = r * math.cos(t * math.pi / 2)
            zz = r * math.sin(t * math.pi / 2)
        prof.append((max(rr, 0.0), zz))
    for k in range(rings):
        (r0, z_0), (r1_, z_1) = prof[k], prof[k + 1]
        for j in range(n):
            a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            pts = [(cc[0] + r0 * math.cos(a0), cc[1] + r0 * math.sin(a0), cc[2] + z0 + z_0),
                   (cc[0] + r0 * math.cos(a1), cc[1] + r0 * math.sin(a1), cc[2] + z0 + z_0),
                   (cc[0] + r1_ * math.cos(a1), cc[1] + r1_ * math.sin(a1), cc[2] + z0 + z_1),
                   (cc[0] + r1_ * math.cos(a0), cc[1] + r1_ * math.sin(a0), cc[2] + z0 + z_1)]
            if r1_ < 1e-4:
                p.face(pts[:3], mat)
            else:
                p.face(pts, mat)


# ------------------------------------------------------------------ at a window (pos: the opening's centre on the wall face)
def shutters(p, pos, yaw, w, h, mat="accent"):
    """a pair of louvred shutters folded back beside a window"""
    f = F(pos, yaw)
    sw = q(w * 0.5)
    for s in (-1, 1):
        x0 = s * (w / 2 + 0.02)
        x1 = s * (w / 2 + 0.02 + sw)
        f.box(p, (min(x0, x1), 0.02, -h / 2), (max(x0, x1), 0.06, h / 2), mat)
        for k in range(1, 5):
            z = -h / 2 + h * k / 5
            f.box(p, (min(x0, x1) + 0.04, 0.06, z - 0.015), (max(x0, x1) - 0.04, 0.08, z + 0.015), mat)


def bay(p, pos, yaw, w, h, depth=0.7, kind="glass", roof="flat", mat="ext", trim="trim"):
    """a projecting box around a window: glass (a bay window, a galería), lattice (a roshan, a mashrabiya, a
    jharokha), or capsule (a bolted-on box with a round window); roof flat / sloped / dome (a jharokha's cap)"""
    f = F(pos, yaw)
    hw, hh, d = w / 2 + 0.25, h / 2 + 0.2, depth
    # floor plate and corbels under it
    f.box(p, (-hw - 0.08, 0.0, -hh - 0.18), (hw + 0.08, d + 0.08, -hh), trim)
    for s in (-1, 1):
        x = s * (hw - 0.15)
        f.box(p, (x - 0.08, 0.0, -hh - 0.7), (x + 0.08, d * 0.6, -hh - 0.18), trim)
    # cheeks
    for s in (-1, 1):
        x0, x1 = sorted((s * hw, s * (hw - 0.1)))
        f.box(p, (x0, 0.0, -hh), (x1, d, hh), mat if kind != "lattice" else "lattice")
    front = d
    if kind == "glass":
        f.box(p, (-hw + 0.1, front - 0.08, -hh), (hw - 0.1, front, -hh + 0.5), mat)
        f.box(p, (-hw + 0.1, front - 0.03, -hh + 0.5), (hw - 0.1, front - 0.01, hh - 0.15), "glass")
        n = max(2, int(w / 0.6))
        for k in range(n + 1):
            x = -hw + 0.1 + (2 * hw - 0.2) * k / n
            f.box(p, (x - 0.03, front - 0.06, -hh + 0.5), (x + 0.03, front, hh - 0.15), trim)
    elif kind == "lattice":
        f.box(p, (-hw + 0.1, front - 0.06, -hh), (hw - 0.1, front - 0.02, hh - 0.15), "lattice")
        n = max(4, int(w / 0.18))
        for k in range(n + 1):
            x = -hw + 0.1 + (2 * hw - 0.2) * k / n
            f.box(p, (x - 0.015, front - 0.02, -hh), (x + 0.015, front + 0.01, hh - 0.15), "wood")
        for k in range(1, 6):
            z = -hh + (2 * hh - 0.15) * k / 6
            f.box(p, (-hw + 0.1, front - 0.02, z - 0.015), (hw - 0.1, front + 0.01, z + 0.015), "wood")
    else:                                                     # capsule: a box with a porthole
        f.box(p, (-hw + 0.1, front - 0.08, -hh), (hw - 0.1, front, hh - 0.15), mat)
        f.cyl(p, (0.0, front + 0.01), 0.35, 0.0, 0.0, "glass", n=12, caps=False)
        f.box(p, (-0.3, front, -0.3), (0.3, front + 0.02, 0.3), "glass")
    # roof
    top = hh - 0.15
    if roof == "slope":
        f.quad(p, [(-hw - 0.15, d + 0.25, top), (hw + 0.15, d + 0.25, top), (hw + 0.15, 0.0, top + 0.45), (-hw - 0.15, 0.0, top + 0.45)], "roof_m")
        f.quad(p, [(-hw - 0.15, 0.0, top + 0.45), (hw + 0.15, 0.0, top + 0.45), (hw + 0.15, d + 0.25, top), (-hw - 0.15, d + 0.25, top)], "roof_m")
    elif roof == "dome":
        f.box(p, (-hw - 0.05, -0.0, top), (hw + 0.05, d + 0.05, top + 0.12), trim)
        _dome(p, f, (0.0, d / 2), min(hw, d / 2 + 0.1), top + 0.12, "accent", rings=4, n=10)
    else:
        f.box(p, (-hw - 0.1, 0.0, top), (hw + 0.1, d + 0.15, top + 0.15), trim)


def cage(p, pos, yaw, w, h, depth=0.6, mat="iron"):
    """a steel balcony cage round a window (Hong Kong's): bars, a floor plate, a roof sheet"""
    f = F(pos, yaw)
    hw = w / 2 + 0.3
    z0, z1 = -h / 2 - 0.5, h / 2 + 0.35
    f.box(p, (-hw, 0.0, z0 - 0.05), (hw, depth, z0), mat)
    f.box(p, (-hw - 0.05, 0.0, z1), (hw + 0.05, depth + 0.1, z1 + 0.04), "tin")
    n = max(3, int(2 * hw / 0.14))
    for k in range(n + 1):
        x = -hw + 2 * hw * k / n
        f.box(p, (x - 0.01, depth - 0.02, z0), (x + 0.01, depth, z1), mat)
    for s in (-1, 1):
        f.box(p, (s * hw - 0.01, 0.0, z0), (s * hw + 0.01, depth, z1), mat)
    for z in (z0 + 0.5, z0 + 1.0, z1 - 0.02):
        f.box(p, (-hw, depth - 0.03, z - 0.015), (hw, depth + 0.01, z + 0.015), mat)


def balcony(p, pos, yaw, w, depth=1.0, rail="iron", mat="trim"):
    """a cantilevered balcony at a window's foot (pos: the floor level at the wall): slab, rail"""
    f = F(pos, yaw)
    hw = w / 2
    f.box(p, (-hw, 0.0, -0.15), (hw, depth, 0.0), mat)
    if rail == "solid":
        f.box(p, (-hw, depth - 0.1, 0.0), (hw, depth, 1.0), mat)
        for s in (-1, 1):
            x0, x1 = sorted((s * hw, s * (hw - 0.1)))
            f.box(p, (x0, 0.0, 0.0), (x1, depth, 1.0), mat)
        return
    rm = "iron" if rail == "iron" else "wood"
    f.box(p, (-hw, depth - 0.04, 0.95), (hw, depth, 1.0), rm)
    for s in (-1, 1):
        x0, x1 = sorted((s * hw, s * (hw - 0.04)))
        f.box(p, (x0, 0.0, 0.95), (x1, depth, 1.0), rm)
    n = max(3, int(w / 0.12))
    for k in range(n + 1):
        x = -hw + w * k / n
        f.box(p, (x - 0.01, depth - 0.03, 0.0), (x + 0.01, depth - 0.01, 0.95), rm)
    for k in range(1, max(2, int(depth / 0.12))):
        y = depth * k / max(2, int(depth / 0.12))
        for s in (-1, 1):
            f.box(p, (s * hw - 0.01, y - 0.01, 0.0), (s * hw + 0.01, y + 0.01, 0.95), rm)


def screen(p, pos, yaw, w, h, mat="lattice"):
    """a lattice screen over a window (jali, chebek, reja): a frame and a grid of slats"""
    f = F(pos, yaw)
    hw, hh = w / 2 + 0.05, h / 2 + 0.05
    f.box(p, (-hw - 0.06, 0.02, -hh - 0.06), (hw + 0.06, 0.07, -hh), mat)
    f.box(p, (-hw - 0.06, 0.02, hh), (hw + 0.06, 0.07, hh + 0.06), mat)
    for s in (-1, 1):
        x0, x1 = sorted((s * hw, s * (hw + 0.06)))
        f.box(p, (x0, 0.02, -hh), (x1, 0.07, hh), mat)
    n = max(3, int(w / 0.16))
    for k in range(1, n):
        x = -hw + 2 * hw * k / n
        f.box(p, (x - 0.012, 0.03, -hh), (x + 0.012, 0.06, hh), mat)
    m = max(3, int(h / 0.16))
    for k in range(1, m):
        z = -hh + 2 * hh * k / m
        f.box(p, (-hw, 0.03, z - 0.012), (hw, 0.06, z + 0.012), mat)


def arch_hood(p, pos, yaw, w, kind="round", mat="trim"):
    """an arch over an opening (pos: the opening's head centre): round, pointed or horseshoe -- a band of voussoirs"""
    f = F(pos, yaw)
    r = w / 2 + 0.12
    n = 9
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        pts = []
        for a, rr in ((a0, r), (a1, r), (a1, r + 0.18), (a0, r + 0.18)):
            x = rr * math.cos(a)
            z = rr * math.sin(a)
            if kind == "pointed":
                z *= 1.0 + 0.6 * (1 - abs(math.cos(a)))
            elif kind == "horseshoe":
                x *= 1.08
            pts.append((x, 0.04, z))
        pts2 = [(x, 0.1, z) for (x, _, z) in pts]
        f.quad(p, pts2, mat)
        for i in range(4):
            a_, b_ = pts[i], pts[(i + 1) % 4]
            f.quad(p, [a_, b_, (b_[0], 0.1, b_[2]), (a_[0], 0.1, a_[2])], mat)


def eyebrow(p, pos, yaw, w, depth=0.45, mat="trim"):
    """a chhajja / sunshade over a window (pos: just above its head): a sloped slab on two brackets"""
    f = F(pos, yaw)
    hw = w / 2 + 0.25
    f.quad(p, [(-hw, depth, -0.12), (hw, depth, -0.12), (hw, 0.0, 0.08), (-hw, 0.0, 0.08)], mat)
    f.quad(p, [(-hw, 0.0, 0.0), (hw, 0.0, 0.0), (hw, depth, -0.2), (-hw, depth, -0.2)], mat)
    for s in (-1, 1):
        x = s * (hw - 0.12)
        f.box(p, (x - 0.05, 0.0, -0.5), (x + 0.05, 0.2, -0.05), mat)


def awning(p, pos, yaw, w, depth=1.4, mat="canvas"):
    """a shopfront awning (pos: the top of the shop opening, at the wall): a sloped canvas with a valance"""
    f = F(pos, yaw)
    hw = w / 2
    f.quad(p, [(-hw, 0.0, 0.5), (hw, 0.0, 0.5), (hw, depth, 0.0), (-hw, depth, 0.0)], mat)
    f.quad(p, [(hw, 0.0, 0.48), (-hw, 0.0, 0.48), (-hw, depth, -0.02), (hw, depth, -0.02)], mat)
    f.box(p, (-hw, depth - 0.02, -0.3), (hw, depth, 0.0), mat)
    for s in (-1, 1):
        f.quad(p, [(s * hw, 0.0, 0.5), (s * hw, depth, 0.0), (s * hw, depth, -0.3)], mat)


def ac_unit(p, pos, yaw, mat="steel"):
    """an air-conditioner box on a bracket (pos: on the wall)"""
    f = F(pos, yaw)
    f.box(p, (-0.4, 0.0, 0.0), (0.4, 0.5, 0.55), mat)
    f.box(p, (-0.3, 0.5, 0.1), (0.3, 0.52, 0.45), "iron")
    f.box(p, (-0.4, 0.0, -0.08), (0.4, 0.45, -0.04), "iron")


def planter(p, pos, yaw, w, mat="accent"):
    """a window box of greens (pos: under the sill)"""
    f = F(pos, yaw)
    hw = w / 2
    f.box(p, (-hw, 0.0, -0.25), (hw, 0.3, 0.0), mat)
    f.box(p, (-hw + 0.05, 0.03, 0.0), (hw - 0.05, 0.27, 0.18), "green")


# ------------------------------------------------------------------ along a wall (pos: the run's start on the wall face)
def band(p, pos, yaw, L, h=0.25, depth=0.06, mat="trim"):
    """a horizontal band (a plaster band, an ablaq stripe, a string course) L long"""
    f = F(pos, yaw)
    f.box(p, (0.0, 0.0, 0.0), (L, depth, h), mat)


def gallery(p, pos, yaw, L, depth=1.4, rail="iron", mat="trim"):
    """an access gallery along a wall at one floor (pos: the floor level at the wall, the run's start): a walkway
    deck, posts and a rail -- the chawl's, the plex's, the gard's"""
    f = F(pos, yaw)
    f.box(p, (0.0, 0.0, -0.18), (L, depth, 0.0), mat)
    rm = "iron" if rail == "iron" else "wood"
    f.box(p, (0.0, depth - 0.05, 0.95), (L, depth, 1.02), rm)
    f.box(p, (0.0, depth - 0.05, 0.45), (L, depth - 0.02, 0.5), rm)
    n = max(1, int(L / 2.4))
    for k in range(n + 1):
        x = min(L - 0.04, L * k / n)
        f.box(p, (x, depth - 0.06, 0.0), (x + 0.06, depth, 1.0), rm)


def corbels(p, pos, yaw, L, step=1.2, mat="trim"):
    """a run of corbels under a jetty or a cornice (pos: the run's start, at the underside)"""
    f = F(pos, yaw)
    n = max(1, int(L / step))
    for k in range(n + 1):
        x = L * k / n
        f.box(p, (x - 0.08, 0.0, -0.45), (x + 0.08, 0.35, 0.0), mat)
        f.box(p, (x - 0.08, 0.0, -0.7), (x + 0.08, 0.15, -0.45), mat)


def beam_ends(p, pos, yaw, L, step=0.9, mat="wood"):
    """palm-beam or joist ends poking out of a wall (pos: the run's start)"""
    f = F(pos, yaw)
    n = max(1, int(L / step))
    for k in range(n):
        x = L * (k + 0.5) / n
        f.box(p, (x - 0.07, 0.0, -0.07), (x + 0.07, 0.35, 0.07), mat)


# ------------------------------------------------------------------ parapets (pos: the parapet top's start, outer face)
def crenels(p, pos, yaw, L, kind="square", mat="ext"):
    """merlons along a parapet top: square, stepped (triangle-topped) or rounded"""
    f = F(pos, yaw)
    n = max(1, int(L / 0.9))
    for k in range(n):
        x0 = L * k / n + 0.15
        x1 = L * (k + 1) / n - 0.25
        if x1 - x0 < 0.2:
            continue
        if kind == "triangle":
            f.box(p, (x0, -0.3, 0.0), (x1, 0.0, 0.3), mat)
            xm = (x0 + x1) / 2
            for y in (-0.3, 0.0):
                f.quad(p, [(x0, y, 0.3), (x1, y, 0.3), (xm, y, 0.75)] if y == 0.0 else [(x1, y, 0.3), (x0, y, 0.3), (xm, y, 0.75)], mat)
            f.quad(p, [(x0, -0.3, 0.3), (x0, 0.0, 0.3), (xm, 0.0, 0.75), (xm, -0.3, 0.75)], mat)
            f.quad(p, [(x1, 0.0, 0.3), (x1, -0.3, 0.3), (xm, -0.3, 0.75), (xm, 0.0, 0.75)], mat)
        elif kind == "round":
            f.box(p, (x0, -0.3, 0.0), (x1, 0.0, 0.25), mat)
            f.cyl(p, ((x0 + x1) / 2, -0.15), (x1 - x0) / 2, 0.25, 0.45, mat, n=8, r1=(x1 - x0) / 4)
        else:
            f.box(p, (x0, -0.3, 0.0), (x1, 0.0, 0.55), mat)


def parapet_screen(p, pos, yaw, L, mat="lattice"):
    """a pierced screen on a parapet top (a jali parapet)"""
    f = F(pos, yaw)
    f.box(p, (0.0, -0.25, 0.55), (L, 0.0, 0.62), "trim")
    n = max(2, int(L / 0.3))
    for k in range(n + 1):
        x = L * k / n
        f.box(p, (x - 0.03, -0.18, 0.0), (x + 0.03, -0.07, 0.55), mat)


def false_front(p, pos, yaw, L, h=2.6, mat="ext", trim="trim"):
    """a boomtown false front rising over the roof line (pos: the front wall top's start): a board with a cornice"""
    f = F(pos, yaw)
    f.box(p, (0.0, -0.15, 0.0), (L, 0.0, h), mat)
    f.box(p, (-0.2, -0.2, h), (L + 0.2, 0.25, h + 0.25), trim)
    corbels(p, f.P(0.0, 0.0, h), yaw, L, step=1.0, mat=trim)


def gable_front(p, pos, yaw, L, kind="step", h=None, mat="ext", trim="trim"):
    """a Flemish/Dutch gable front over the roof line (pos: the front wall top's start): stepped, neck or bell"""
    f = F(pos, yaw)
    h = h or L * 0.7
    if kind == "step":
        n = 4
        for k in range(n):
            inset = L * 0.5 * k / n
            f.box(p, (inset, -0.25, h * k / n), (L - inset, 0.0, h * (k + 1) / n), mat)
            f.box(p, (inset - 0.05, -0.3, h * (k + 1) / n), (inset + 0.3, 0.05, h * (k + 1) / n + 0.08), trim)
            f.box(p, (L - inset - 0.3, -0.3, h * (k + 1) / n), (L - inset + 0.05, 0.05, h * (k + 1) / n + 0.08), trim)
    else:
        # neck / bell: a broad base, a narrow tall neck, scrolls (as blocks) at the shoulders, a pediment cap
        f.box(p, (0.0, -0.25, 0.0), (L, 0.0, h * 0.4), mat)
        nk = L * (0.38 if kind == "neck" else 0.5)
        f.box(p, ((L - nk) / 2, -0.25, h * 0.4), ((L + nk) / 2, 0.0, h), mat)
        for s in (0, 1):
            x0 = (L - nk) / 2 - 0.9 if s == 0 else (L + nk) / 2
            f.box(p, (x0, -0.25, h * 0.4), (x0 + 0.9, 0.0, h * 0.4 + 0.6), mat)
        f.box(p, ((L - nk) / 2 - 0.15, -0.3, h), ((L + nk) / 2 + 0.15, 0.05, h + 0.2), trim)
        f.quad(p, [((L - nk) / 2, 0.05, h + 0.2), ((L + nk) / 2, 0.05, h + 0.2), (L / 2, 0.05, h + 0.2 + nk * 0.35)], trim)
    # a hoist beam out of the gable's top (canal houses: the cargo goes up outside)
    f.box(p, (L / 2 - 0.1, 0.0, h * 0.82), (L / 2 + 0.1, 1.2, h * 0.82 + 0.2), "wood")


def eave_stack(p, pos, yaw, w, d, tiers=2, overhang=0.9, mat="roof_m", under="trim"):
    """pagoda tiers: flared eaves stepping up (pos: the block's roof centre at the wall top)"""
    f = F(pos, yaw)
    for t in range(tiers):
        z = t * 1.5
        hw, hd = w / 2 + overhang - t * 0.6, d / 2 + overhang - t * 0.6
        iw, idp = max(0.5, hw - overhang - 0.4), max(0.5, hd - overhang - 0.4)
        # the eave's sloped skirt (four trapezoids) and its soffit
        ring_o = [(-hw, -hd, z), (hw, -hd, z), (hw, hd, z), (-hw, hd, z)]
        ring_i = [(-iw, -idp, z + 0.9), (iw, -idp, z + 0.9), (iw, idp, z + 0.9), (-iw, idp, z + 0.9)]
        for i in range(4):
            a, b_ = ring_o[i], ring_o[(i + 1) % 4]
            c, d_ = ring_i[(i + 1) % 4], ring_i[i]
            f.quad(p, [a, b_, c, d_], mat)
        f.quad(p, list(reversed(ring_o)), under)
        f.quad(p, ring_i, mat)
        # the drum between tiers
        if t < tiers - 1:
            f.box(p, (-iw * 0.9, -idp * 0.9, z + 0.9), (iw * 0.9, idp * 0.9, z + 1.5), "accent")
    # a finial
    f.cyl(p, (0.0, 0.0), 0.12, tiers * 1.5 - 0.6, tiers * 1.5 + 0.8, "brass", n=8, r1=0.02)


# ------------------------------------------------------------------ on the roof (pos: on the roof deck)
def shack(p, pos, yaw, w=3.0, d=2.6, h=2.4, kind="shack", mat="tin"):
    """a rooftop shack (a squatter hut, a pigeon loft, a roof shrine, a chalet): walls, a door, a pent roof"""
    f = F(pos, yaw)
    hw, hd = w / 2, d / 2
    wall = mat if kind != "chalet" else "accent"
    f.box(p, (-hw, -hd, 0.0), (hw, hd, h), wall)
    f.box(p, (-0.45, hd, 0.0), (0.45, hd + 0.04, 2.0), "door")
    if kind == "loft":
        for k in range(3):
            f.box(p, (-hw + 0.3 + k * 0.8, hd, h - 0.6), (-hw + 0.8 + k * 0.8, hd + 0.05, h - 0.3), "iron")
    if kind == "shrine":
        f.box(p, (-hw - 0.4, hd, h - 0.1), (hw + 0.4, hd + 0.8, h), "accent")
    if kind == "chalet":
        f.quad(p, [(-hw - 0.4, -hd - 0.3, h), (hw + 0.4, -hd - 0.3, h), (hw + 0.4, 0.0, h + 1.6), (-hw - 0.4, 0.0, h + 1.6)], "roof_m")
        f.quad(p, [(hw + 0.4, hd + 0.3, h), (-hw - 0.4, hd + 0.3, h), (-hw - 0.4, 0.0, h + 1.6), (hw + 0.4, 0.0, h + 1.6)], "roof_m")
        for s in (-1, 1):
            f.quad(p, [(s * hw, -hd, h), (s * hw, hd, h), (s * hw, 0.0, h + 1.6)] if s > 0 else
                   [(s * hw, hd, h), (s * hw, -hd, h), (s * hw, 0.0, h + 1.6)], "accent")
        f.box(p, (-0.6, hd, 1.0), (0.6, hd + 0.05, 1.8), "glass")
        return
    f.quad(p, [(-hw - 0.2, -hd - 0.3, h), (hw + 0.2, -hd - 0.3, h), (hw + 0.2, hd + 0.4, h + 0.35), (-hw - 0.2, hd + 0.4, h + 0.35)], "tin")
    f.quad(p, [(hw + 0.2, -hd - 0.3, h - 0.03), (-hw - 0.2, -hd - 0.3, h - 0.03), (-hw - 0.2, hd + 0.4, h + 0.32), (hw + 0.2, hd + 0.4, h + 0.32)], "tin")
    f.box(p, (hw, -0.4, 1.0), (hw + 0.04, 0.4, 1.6), "glass")


def tank(p, pos, yaw, r=0.8, h=1.6, mat="tin"):
    """a water tank (or drum) on a steel stand"""
    f = F(pos, yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(p, (sx * r * 0.6 - 0.05, sy * r * 0.6 - 0.05, 0.0), (sx * r * 0.6 + 0.05, sy * r * 0.6 + 0.05, 1.0), "iron")
    f.cyl(p, (0.0, 0.0), r, 1.0, 1.0 + h, mat, n=12)
    f.cyl(p, (0.0, 0.0), r * 1.03, 1.0 + h, 1.15 + h, mat, n=12, r1=0.1)


def antenna(p, pos, yaw, h=4.0):
    """a mast with crossbars"""
    f = F(pos, yaw)
    f.box(p, (-0.04, -0.04, 0.0), (0.04, 0.04, h), "iron")
    for k in range(3):
        z = h * (0.55 + 0.15 * k)
        L = 0.9 - 0.2 * k
        f.box(p, (-L, -0.02, z), (L, 0.02, z + 0.04), "iron")


def laundry(p, pos, yaw, L=4.0):
    """two poles and a line of laundry between them"""
    f = F(pos, yaw)
    for x in (0.0, L):
        f.box(p, (x - 0.04, -0.04, 0.0), (x + 0.04, 0.04, 2.0), "iron")
    f.box(p, (0.0, -0.01, 1.92), (L, 0.01, 1.94), "iron")
    cols = ("accent", "canvas", "trim", "green")
    n = max(2, int(L / 0.7))
    for k in range(n):
        x = L * (k + 0.25) / n
        f.box(p, (x, -0.01, 1.2 + 0.1 * (k % 3)), (x + L / n * 0.55, 0.01, 1.92), cols[k % len(cols)])


def pergola(p, pos, yaw, w=4.0, d=3.0, h=2.5):
    """a timber pergola (an altana, a roof garden's shade)"""
    f = F(pos, yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(p, (sx * w / 2 - 0.08, sy * d / 2 - 0.08, 0.0), (sx * w / 2 + 0.08, sy * d / 2 + 0.08, h), "wood")
    for k in range(int(w / 0.5) + 1):
        x = -w / 2 + w * k / max(1, int(w / 0.5))
        f.box(p, (x - 0.04, -d / 2 - 0.2, h), (x + 0.04, d / 2 + 0.2, h + 0.15), "wood")
    f.box(p, (-w / 2, -0.25, 0.0), (w / 2, 0.25, 0.4), "green")


def chimney(p, pos, yaw, w=0.8, h=2.0, kind="stack", mat="stone"):
    """a chimney stack (with pots) or a mosaic chimney (Gaudí: a twisted, capped cone)"""
    f = F(pos, yaw)
    if kind == "mosaic":
        f.cyl(p, (0.0, 0.0), w * 0.6, 0.0, h, "tile", n=8, r1=w * 0.35)
        _dome(p, f, (0.0, 0.0), w * 0.45, h, "accent", rings=3, n=8)
        return
    f.box(p, (-w / 2, -w / 3, 0.0), (w / 2, w / 3, h), mat)
    f.box(p, (-w / 2 - 0.05, -w / 3 - 0.05, h), (w / 2 + 0.05, w / 3 + 0.05, h + 0.12), "trim")
    for s in (-1, 1):
        f.cyl(p, (s * w / 4, 0.0), 0.11, h + 0.12, h + 0.5, "tile", n=8)


def dome(p, pos, yaw, r=2.0, drum=0.8, onion=False, mat="accent"):
    """a dome on a drum (onion: Mughal / Russian)"""
    f = F(pos, yaw)
    f.cyl(p, (0.0, 0.0), r * 0.92, 0.0, drum, "trim", n=14)
    _dome(p, f, (0.0, 0.0), r * 0.92, drum, mat, rings=6, n=14, onion=onion)
    top = drum + r * (1.6 if onion else 1.0) * 0.92
    f.cyl(p, (0.0, 0.0), 0.08, top - 0.1, top + 0.9, "brass", n=6, r1=0.02)


def chhatri(p, pos, yaw, r=1.2):
    """a chhatri: four posts under a small dome, on a plinth"""
    f = F(pos, yaw)
    f.box(p, (-r, -r, 0.0), (r, r, 0.3), "trim")
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(p, (sx * (r - 0.2) - 0.1, sy * (r - 0.2) - 0.1, 0.3), (sx * (r - 0.2) + 0.1, sy * (r - 0.2) + 0.1, 2.1), "trim")
    f.box(p, (-r - 0.15, -r - 0.15, 2.1), (r + 0.15, r + 0.15, 2.3), "trim")
    _dome(p, f, (0.0, 0.0), r * 0.9, 2.3, "accent", rings=4, n=10)
    f.cyl(p, (0.0, 0.0), 0.05, 2.3 + r * 0.85, 2.3 + r * 0.85 + 0.6, "brass", n=6)


def tower(p, pos, yaw, r=1.6, h=6.0, cap="dome", round_=False, mat="ext"):
    """a small tower on a roof: a minaret, a bell or clock tower, a menzeh, a turret -- square or round, with a
    gallery and a cap (dome, pyramid, cone, spire)"""
    f = F(pos, yaw)
    if round_:
        f.cyl(p, (0.0, 0.0), r, 0.0, h, mat, n=14)
        f.cyl(p, (0.0, 0.0), r + 0.25, h, h + 0.2, "trim", n=14)
    else:
        f.box(p, (-r, -r, 0.0), (r, r, h), mat)
        f.box(p, (-r - 0.2, -r - 0.2, h), (r + 0.2, r + 0.2, h + 0.2), "trim")
        # a lantern storey of arched openings (dark slots)
        for s in (-1, 1):
            f.box(p, (-r * 0.5, s * r - 0.01, h - 1.6), (r * 0.5, s * r + 0.01, h - 0.4), "lamp")
            f.box(p, (s * r - 0.01, -r * 0.5, h - 1.6), (s * r + 0.01, r * 0.5, h - 0.4), "lamp")
    z = h + 0.2
    if cap == "dome":
        _dome(p, f, (0.0, 0.0), r * 0.95, z, "accent", rings=5, n=12)
        f.cyl(p, (0.0, 0.0), 0.06, z + r * 0.9, z + r * 0.9 + 0.8, "brass", n=6)
    elif cap == "onion":
        _dome(p, f, (0.0, 0.0), r * 0.95, z, "accent", rings=6, n=12, onion=True)
    elif cap in ("pyramid", "spire", "cone"):
        hh = r * (1.4 if cap == "pyramid" else 3.2)
        if round_ or cap == "cone":
            f.cyl(p, (0.0, 0.0), r + 0.1, z, z + hh, "roof_m", n=12, r1=0.03)
        else:
            rr = r + 0.15
            for (a, b_) in (((-rr, -rr), (rr, -rr)), ((rr, -rr), (rr, rr)), ((rr, rr), (-rr, rr)), ((-rr, rr), (-rr, -rr))):
                f.quad(p, [(a[0], a[1], z), (b_[0], b_[1], z), (0.0, 0.0, z + hh)], "roof_m")
    else:                                                    # a flat top with merlons
        crenels(p, f.P(-r - 0.2, r + 0.2, z), yaw, 2 * r + 0.4, mat=mat)


def tapered_tower(p, pos, yaw, r=1.6, h=8.0, mat="ext"):
    """a kasbah corner tower: square, tapering, crenellated with stepped merlons"""
    f = F(pos, yaw)
    r1 = r * 0.78
    pts0 = [(-r, -r), (r, -r), (r, r), (-r, r)]
    pts1 = [(-r1, -r1), (r1, -r1), (r1, r1), (-r1, r1)]
    for i in range(4):
        a0, b0 = pts0[i], pts0[(i + 1) % 4]
        a1, b1 = pts1[i], pts1[(i + 1) % 4]
        f.quad(p, [(a0[0], a0[1], 0.0), (b0[0], b0[1], 0.0), (b1[0], b1[1], h), (a1[0], a1[1], h)], mat)
    f.quad(p, [(x, y, h) for x, y in pts1], mat)
    for (x0, y0), yaw2 in (((-r1, r1), 0), ((r1, -r1), 180), ((r1, r1), 270), ((-r1, -r1), 90)):
        pass
    # stepped merlons on the top edge
    for k in range(3):
        x = -r1 + 2 * r1 * (k + 0.5) / 3
        for y in (-r1, r1):
            f.box(p, (x - 0.2, y - 0.1, h), (x + 0.2, y + 0.1, h + 0.5), mat)
        for xx in (-r1, r1):
            f.box(p, (xx - 0.1, x - 0.2, h), (xx + 0.1, x + 0.2, h + 0.5), mat)
    # relief: a band of lozenges (as inset dark squares) near the top
    for k in range(3):
        x = -r1 * 0.6 + r1 * 0.6 * k
        f.box(p, (x - 0.15, -r1 - 0.05 - (r - r1) * 0.15, h - 1.6), (x + 0.15, -r1 + 0.02, h - 1.3), "accent")


def spiral_stair(p, pos, yaw, h, r=0.9, mat="iron"):
    """an outside spiral stair (Montréal's plexes) round a post, from grade to h, with a rail; walkable as steps"""
    f = F(pos, yaw)
    rise = 0.2
    n = max(4, int(h / rise))
    f.cyl(p, (0.0, 0.0), 0.06, 0.0, h + 1.0, mat, n=8)
    for k in range(n):
        a = k * (2 * math.pi / 14)
        z = (k + 1) * h / n
        c, s_ = math.cos(a), math.sin(a)
        c2, s2 = math.cos(a + 2 * math.pi / 14 * 1.15), math.sin(a + 2 * math.pi / 14 * 1.15)
        pts = [(0.08 * c, 0.08 * s_, z), (r * c, r * s_, z), (r * c2, r * s2, z), (0.08 * c2, 0.08 * s2, z)]
        f.quad(p, pts, mat)
        f.quad(p, [(x, y, z - 0.04) for (x, y, _) in reversed(pts)], mat)
        f.box(p, (r * c - 0.02, r * s_ - 0.02, z), (r * c + 0.02, r * s_ + 0.02, z + 0.95), mat)


def ceiling_tiles(p, pos, yaw, variant="grid"):
    """THE CEILING TILE MODEL (the user, 2026-10-14: "Make a model for ceiling tiles"; research b_ceiling_tiles.md):
    a 1.2 x 1.2 m module hung with its face at pos (z the ceiling's underside): four tiles in their grid.
      grid    a suspended acoustic grid: 600 mm tiles, 24 mm T-bars, tiles set 10 mm up into the grid
      tin     a pressed-tin panel: 600 mm squares with a raised boss and a bead border
      coffer  a coffered timber panel: a deep frame of beams with a sunken painted field (artesonado)
      batten  timber battens across the module (a Japanese / Nordic slatted ceiling)"""
    f = F(pos, yaw)
    S = 0.6
    if variant == "batten":
        for k in range(8):
            x = -S + 1.2 * (k + 0.5) / 8
            f.box(p, (x - 0.035, -S, -0.06), (x + 0.035, S, 0.0), "wood")
        f.box(p, (-S, -S, 0.0), (S, S, 0.01), "trim")
        return
    for i in (-1, 0):
        for j in (-1, 0):
            x0, y0 = i * S, j * S
            if variant == "grid":
                f.box(p, (x0 + 0.012, y0 + 0.012, 0.0), (x0 + S - 0.012, y0 + S - 0.012, 0.012), "ceiling_tile")
            elif variant == "tin":
                f.box(p, (x0, y0, 0.0), (x0 + S, y0 + S, 0.01), "tin_ceiling")
                f.box(p, (x0 + 0.1, y0 + 0.1, -0.025), (x0 + S - 0.1, y0 + S - 0.1, 0.0), "tin_ceiling")
                f.box(p, (x0 + 0.24, y0 + 0.24, -0.045), (x0 + S - 0.24, y0 + S - 0.24, -0.025), "tin_ceiling")
            else:                                             # coffer
                f.box(p, (x0 + 0.08, y0 + 0.08, 0.06), (x0 + S - 0.08, y0 + S - 0.08, 0.07), "accent")
                f.box(p, (x0 + 0.2, y0 + 0.2, 0.05), (x0 + S - 0.2, y0 + S - 0.2, 0.06), "brass")
    if variant == "grid":
        for k in range(3):
            x = -S + S * k
            f.box(p, (x - 0.012, -S, -0.02), (x + 0.012, S, 0.0), "trim")
            f.box(p, (-S, x - 0.012, -0.02), (S, x + 0.012, 0.0), "trim")
    elif variant == "coffer":
        for k in range(3):
            x = -S + S * k
            f.box(p, (x - 0.08, -S, -0.12), (x + 0.08, S, 0.06), "wood")
            f.box(p, (-S, x - 0.08, -0.12), (S, x + 0.08, 0.06), "wood")


# ------------------------------------------------------------------ registry (the contract's names) + gbkit
ITEMS = [shutters, bay, cage, balcony, screen, arch_hood, eyebrow, awning, ac_unit, planter, band, gallery, corbels,
         beam_ends, crenels, parapet_screen, false_front, gable_front, eave_stack, shack, tank, antenna, laundry, pergola,
         chimney, dome, chhatri, tower, tapered_tower, spiral_stair, ceiling_tiles]


def install():
    """wrap every item for gbkit (as build_record.py does gbfurn's), once"""
    import gbkit
    g = globals()
    if g.get("_installed"):
        return
    g["_installed"] = True
    for fn in ITEMS:
        g[fn.__name__] = gbkit.wrap(fn, gbkit._furn_frame)


def catalogue():
    return {fn.__name__: {"doc": (fn.__doc__ or "").strip().split("\n")[0]} for fn in ITEMS}
