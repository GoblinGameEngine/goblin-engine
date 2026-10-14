"""geo -- local-frame geometry over a gblib Part (everything closed, outward-wound, deterministic).

A component is built in its own frame (frame: a 4x4 Matrix, Blender z up): origin on the wall face at the bottom
centre (or the base centre of a free-standing piece), +Z up, +Y out of the facade (toward the street; a free piece's
front), +X = Y x Z.  G maps local points through the frame into the Part (world coordinates).
"""
import math

from mathutils import Matrix, Vector

TAU = math.tau


class G:
    def __init__(self, part, frame):
        self.part = part
        self.M = frame

    def at(self, x, y, z):
        return tuple(self.M @ Vector((x, y, z)))

    def sub(self, local):
        """a child frame (local Matrix in this frame)"""
        return G(self.part, self.M @ local)

    def moved(self, x=0.0, y=0.0, z=0.0, rz=0.0):
        return self.sub(Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, "Z"))

    # ------------------------------------------------------------ faces
    def face(self, pts, mat):
        return self.part.face([self.at(*p) for p in pts], mat)

    def box(self, lo, hi, mat, mats=None):
        x0, x1 = sorted((lo[0], hi[0]))
        y0, y1 = sorted((lo[1], hi[1]))
        z0, z1 = sorted((lo[2], hi[2]))
        if x1 - x0 < 1e-5 or y1 - y0 < 1e-5 or z1 - z0 < 1e-5:
            return
        m = mats or {}
        self.face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], m.get("x", mat))
        self.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], m.get("X", mat))
        self.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], m.get("y", mat))
        self.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], m.get("Y", mat))
        self.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], m.get("z", mat))
        self.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], m.get("Z", mat))

    def cbox(self, cx, cy, z0, w, d, h, mat, mats=None):
        """a box centred on (cx, cy), from z0 up h"""
        self.box((cx - w / 2, cy - d / 2, z0), (cx + w / 2, cy + d / 2, z0 + h), mat, mats)

    def cyl(self, cx, cy, r, z0, z1, mat, n=10, r1=None, caps=True):
        r1 = r if r1 is None else r1
        a = [(cx + r * math.cos(TAU * k / n), cy + r * math.sin(TAU * k / n), z0) for k in range(n)]
        b = [(cx + r1 * math.cos(TAU * k / n), cy + r1 * math.sin(TAU * k / n), z1) for k in range(n)]
        for k in range(n):
            j = (k + 1) % n
            self.face([a[k], a[j], b[j], b[k]], mat)
        if caps:
            if r > 1e-5:
                self.face(list(reversed(a)), mat)
            if r1 > 1e-5:
                self.face(b, mat)

    def tube(self, p0, p1, r, mat, n=6):
        """a closed cylinder between two local points"""
        p0, p1 = Vector(p0), Vector(p1)
        ax = p1 - p0
        L = ax.length
        if L < 1e-5:
            return
        z = ax / L
        x = z.orthogonal().normalized()
        y = z.cross(x)
        R = Matrix((x, y, z)).transposed().to_4x4()
        self.sub(Matrix.Translation(p0) @ R).cyl(0, 0, r, 0, L, mat, n=n)

    def lathe(self, prof, mat, n=12, cx=0.0, cy=0.0):
        """revolve a profile [(r, z), ...] (bottom to top) about local z.  r = 0 at an end closes it to a point;
        otherwise that end is capped flat."""
        rings = [[(cx + r * math.cos(TAU * k / n), cy + r * math.sin(TAU * k / n), z) for k in range(n)] for r, z in prof]
        for i in range(len(prof) - 1):
            r0, r1 = prof[i][0], prof[i + 1][0]
            if r0 < 1e-6 and r1 < 1e-6:
                continue
            for k in range(n):
                j = (k + 1) % n
                if r0 < 1e-6:
                    self.face([(cx, cy, prof[i][1]), rings[i + 1][j], rings[i + 1][k]], mat)
                elif r1 < 1e-6:
                    self.face([rings[i][k], rings[i][j], (cx, cy, prof[i + 1][1])], mat)
                else:
                    self.face([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]], mat)
        if prof[0][0] > 1e-6:
            self.face(list(reversed(rings[0])), mat)
        if prof[-1][0] > 1e-6:
            self.face(rings[-1], mat)

    def extrude_xz(self, poly, y0, y1, mat, cap_mat=None):
        """a profile in the x-z plane (counter-clockwise with x right and z up) extruded along y from y0 to y1"""
        poly = list(reversed(poly))            # (the faces below are wound for a clockwise list)
        n = len(poly)
        cm = cap_mat or mat
        cap = _no_collinear(poly)              # (a straight run of points makes zero-area triangles in a cap)
        self.face([(x, y1, z) for x, z in cap], cm)                        # front (+Y)
        self.face([(x, y0, z) for x, z in reversed(cap)], cm)              # back
        for k in range(n):
            (xa, za), (xb, zb) = poly[k], poly[(k + 1) % n]
            self.face([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], mat)

    def extrude_xy(self, poly, z0, z1, mat, cap_mat=None):
        """a plan outline (CCW seen from above) extruded up from z0 to z1"""
        n = len(poly)
        cm = cap_mat or mat
        self.face([(x, y, z1) for x, y in poly], cm)
        self.face([(x, y, z0) for x, y in reversed(poly)], cm)
        for k in range(n):
            (xa, ya), (xb, yb) = poly[k], poly[(k + 1) % n]
            self.face([(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)], mat)

    def ring_xz(self, outer, inner, y0, y1, mat, cap_mat=None):
        """a frame: the band between two closed x-z outlines with the same vertex count,
        extruded along y -- closed and manifold (a surround with its hole).  Both counter-clockwise (x right, z up)."""
        outer, inner = list(reversed(outer)), list(reversed(inner))
        n = len(outer)
        cm = cap_mat or mat
        for k in range(n):
            j = (k + 1) % n
            oa, ob, ia, ib = outer[k], outer[j], inner[k], inner[j]
            self.face([(oa[0], y1, oa[1]), (ob[0], y1, ob[1]), (ib[0], y1, ib[1]), (ia[0], y1, ia[1])], cm)   # front
            self.face([(ia[0], y0, ia[1]), (ib[0], y0, ib[1]), (ob[0], y0, ob[1]), (oa[0], y0, oa[1])], cm)   # back
            self.face([(oa[0], y0, oa[1]), (ob[0], y0, ob[1]), (ob[0], y1, ob[1]), (oa[0], y1, oa[1])], mat)  # outer side
            self.face([(ib[0], y0, ib[1]), (ia[0], y0, ia[1]), (ia[0], y1, ia[1]), (ib[0], y1, ib[1])], mat)  # inner side

    def slab(self, poly_xz, y0, y1, mat):
        return self.extrude_xz(poly_xz, y0, y1, mat)


def _no_collinear(poly, eps=1e-6):
    out = []
    n = len(poly)
    for i in range(n):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % n]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) > eps and (abs(b[0] - a[0]) + abs(b[1] - a[1])) > 1e-7:
            out.append(b)
    return out if len(out) >= 3 else poly


# ------------------------------------------------------------------ 2D outlines (x-z, CCW seen from +Y)
def arch_outline(shape, w, h, n=6):
    """An opening's outline: width w, height h to the crown, bottom at z 0, centred on x 0; CCW seen from +Y:
    bottom-left, bottom-right, then the head from the right jamb over to the left.  Always 2*n + 4 points, so
    two outlines of one shape and n can be ringed into a frame."""
    r = w / 2
    m = 2 * n + 2                                  # head points
    pts = [(-r, 0.0), (r, 0.0)]
    head = []
    if shape == "rect":
        for k in range(m):
            head.append((r - w * k / (m - 1), h))
    elif shape in ("round", "lobed", "cusped"):
        rise = min(r, h * 0.6)
        sp = h - rise
        lobes = {"lobed": 5, "cusped": 9}.get(shape, 0)
        for k in range(m):
            t = math.pi * k / (m - 1)
            rr = 1.0 - ((0.13 if shape == "lobed" else 0.06) * abs(math.sin(lobes * t)) if lobes and 0 < k < m - 1 else 0.0)
            head.append((r * rr * math.cos(t), sp + rise * rr * math.sin(t)))
    elif shape == "horseshoe":
        R = r * 1.2
        cz = h - R
        t0 = -math.acos(r / R)
        for k in range(m):
            t = t0 + (math.pi - 2 * t0) * k / (m - 1)
            head.append((R * math.cos(t), max(cz + R * math.sin(t), 0.05)))
    elif shape == "pointed":
        rho = w * 0.9
        rise = math.sqrt(max(rho * rho - (rho - r) ** 2, 0.0))
        rise = min(rise, h * 0.7)
        sp = h - rise
        k_ = rise / math.sqrt(max(rho * rho - (rho - r) ** 2, 1e-9))
        for k in range(m):
            x = r - w * k / (m - 1)
            ax = abs(x)
            z = sp + k_ * math.sqrt(max(rho * rho - (ax + rho - r) ** 2, 0.0))
            head.append((x, z))
    elif shape == "ogee":
        # an ogee: convex at the shoulders, concave into a point at the crown (an S each side)
        rise = min(r * 1.2, h * 0.55)
        sp = h - rise
        for k in range(m):
            x = r - w * k / (m - 1)
            u = abs(x) / r if r else 0.0
            f = 0.5 + 0.5 * math.cos(math.pi * u)           # (a bell: 1 at the crown, 0 at the jambs)
            head.append((x, sp + rise * (f ** 0.55 * 0.85 + (1 - u) ** 2.2 * 0.15)))
    elif shape == "circle":
        cz, rz = h / 2, h / 2
        q = 2 * n + 4
        return [(r * math.cos(TAU * k / q - math.pi / 2), cz + rz * math.sin(TAU * k / q - math.pi / 2)) for k in range(q)]
    else:
        return arch_outline("rect", w, h, n)
    return pts + head


def grow(outline, d, radial=False):
    """An outline pushed out by d, same vertex count (for ring_xz).  The two bottom corners go out sideways (a
    surround stands on the sill/ground line); the head's points go out along the direction from the head's centre
    (the spring line's middle).  radial=True: every point out from the centroid (a circle)."""
    if radial:
        cx = sum(x for x, _ in outline) / len(outline)
        cz = sum(z for _, z in outline) / len(outline)
        out = []
        for x, z in outline:
            dx, dz = x - cx, z - cz
            L = math.hypot(dx, dz) or 1.0
            out.append((x + dx / L * d, z + dz / L * d))
        return out
    head = outline[2:]
    sp = min(z for _, z in head)
    out = [(outline[0][0] - d, outline[0][1]), (outline[1][0] + d, outline[1][1])]
    for i, (x, z) in enumerate(head):
        dx, dz = x, z - sp
        L = math.hypot(dx, dz)
        if L < 1e-6 or i in (0, len(head) - 1):
            out.append((x + math.copysign(d, x if abs(x) > 1e-6 else (1 if i == 0 else -1)), z + (d if dz > 0.3 * max(L, 1e-6) else 0.0) * 0))
        else:
            out.append((x + dx / L * d, z + dz / L * d))
    return out
