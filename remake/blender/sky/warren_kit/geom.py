"""geom.py -- the warren kit's mesh builder (pure Python + shapely; no Blender needed).

A piece is built in the island's frame convention (glTF / Godot: +Y up), in metres:
  * a WALL bay: x across the bay (-1.5 .. 1.5), y up (0 .. 3.2), +Z out of the cell into the street; the wall body
    lies INSIDE the cell, from z = -thickness to z = 0 (the cell face).  Things that stand out of a facade (balconies,
    bays, grilles, signs) reach into +Z.
  * a CORNER: origin on the cell's vertical edge, the occupied cell in the -X / -Z quadrant, its two exposed faces
    facing +X and +Z.
  * a CELL piece (paving, slabs, roofs, stairs, interior, free props): origin at the cell's centre at the base of its
    level (y 0 = the walking surface), the cell spanning x and z -1.5 .. 1.5.
  * an EDGE piece (parapets, eaves, crowns): like a wall bay but sitting on the roof (y 0 = the roof top).

Every face is flat-shaded (vertices per face) for the game's toon look.  Each triangle carries a SLOT (one glTF
primitive per slot, its material named "wk_<slot>"), a SHADE in COLOR_0 (grey: baked ambient occlusion, edge wear,
variation -- the runtime multiplies it by the civ palette's colour for that slot), and UV0 (glass: the pane's own 0..1,
for the interior-mapping shader; everything else: planar metres / 3 for any detail texture).
"""
import json
import math
import struct

import numpy as np
import shapely
import shapely.geometry
from shapely.geometry import Polygon

SLOTS = ["wall", "trim", "frame", "glass", "screen", "roof", "metal", "fabric", "emissive", "tile", "water", "ground", "plant", "accent", "accent2"]


class Mesh:
    def __init__(self):
        self.tris = {s: [] for s in SLOTS}           # slot -> [(p0, p1, p2, shade, uv0, uv1, uv2)]

    # -------------------------------------------------------------- primitives
    def tri(self, a, b, c, slot, shade=1.0, uv=None):
        self.tris[slot].append((tuple(a), tuple(b), tuple(c), shade, uv))

    def quad(self, a, b, c, d, slot, shade=1.0, uv=None):
        """a, b, c, d counter-clockwise seen from the front"""
        if uv is None:
            self.tri(a, b, c, slot, shade)
            self.tri(a, c, d, slot, shade)
        else:
            self.tri(a, b, c, slot, shade, (uv[0], uv[1], uv[2]))
            self.tri(a, c, d, slot, shade, (uv[0], uv[2], uv[3]))

    def box(self, lo, hi, slot, shade=1.0, skip=(), slots=None):
        """an axis-aligned closed box; skip: faces to leave out ("x-", "x+", "y-", "y+", "z-", "z+") where they're buried"""
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        if x1 - x0 < 1e-5 or y1 - y0 < 1e-5 or z1 - z0 < 1e-5:
            return
        s = slots or {}
        f = {
            "x-": [(x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (x0, y0, z0)],
            "x+": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
            "y-": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
            "y+": [(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)],
            "z-": [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)],
            "z+": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        }
        for k, q in f.items():
            if k not in skip:
                self.quad(*q, s.get(k, slot), shade * (0.82 if k == "y-" else 1.0))

    def cbox(self, cx, cy, cz, w, h, d, slot, shade=1.0, **kw):
        """a box centred on (cx, cz) in plan, from y = cy up h; w along x, d along z"""
        self.box((cx - w / 2, cy, cz - d / 2), (cx + w / 2, cy + h, cz + d / 2), slot, shade, **kw)

    def tri_facing(self, a, b, c, want, slot, shade=1.0):
        """a triangle wound to face roughly along want (a direction)"""
        n = np.cross(np.subtract(b, a), np.subtract(c, a))
        if float(np.dot(n, want)) < 0:
            b, c = c, b
        self.tri(a, b, c, slot, shade)

    def quad_facing(self, a, b, c, d, want, slot, shade=1.0):
        self.tri_facing(a, b, c, want, slot, shade)
        self.tri_facing(a, c, d, want, slot, shade)

    def prism_xy(self, outer, holes, z0, z1, slot, shade=1.0, cap_slot=None, side_slot=None, hole_slot=None):
        """a polygon in the x-y plane with holes, extruded along z from z0 to z1 -- a wall with its openings cut
        through: the front (+Z) and back (-Z) faces triangulated around the holes, the outer sides facing out, and
        the holes' reveals facing into the hole"""
        poly = Polygon(outer, holes)
        cs = cap_slot or slot
        for t in shapely.constrained_delaunay_triangles(poly).geoms:
            c = list(t.exterior.coords)[:3]
            self.tri_facing(*[(p[0], p[1], z1) for p in c], (0, 0, 1), cs, shade)
            self.tri_facing(*[(p[0], p[1], z0) for p in c], (0, 0, -1), cs, shade * 0.9)
        self._sides(outer, z0, z1, side_slot or slot, shade, inward=False)
        for h in holes:
            self._sides(h, z0, z1, hole_slot or slot, shade * 0.85, inward=True)

    def wall_cut(self, outer, openings, z0, z1, slot, shade=1.0, reveal_slot=None):
        """a slab in the x-y plane, minus its openings (holes, or notches where an opening reaches an edge), extruded
        along z from z0 to z1: faces front and back, its outline's sides, and the openings' reveals"""
        geo = Polygon(outer)
        for o in openings:
            geo = geo.difference(Polygon(o))
        geo = shapely.make_valid(geo)
        polys = [g for g in getattr(geo, "geoms", [geo]) if g.geom_type == "Polygon" and g.area > 1e-6]
        for pg in polys:
            for t in shapely.constrained_delaunay_triangles(pg).geoms:
                c = list(t.exterior.coords)[:3]
                self.tri_facing(*[(p[0], p[1], z1) for p in c], (0, 0, 1), slot, shade)
                self.tri_facing(*[(p[0], p[1], z0) for p in c], (0, 0, -1), slot, shade * 0.9)
            ext = list(pg.exterior.coords)[:-1]
            self._sides(ext, z0, z1, slot, shade, inward=False, reveal_slot=reveal_slot, outer_box=Polygon(outer))
            for h in pg.interiors:
                self._sides(list(h.coords)[:-1], z0, z1, reveal_slot or slot, shade * 0.85, inward=True)

    def _sides(self, ring, z0, z1, slot, shade, inward, reveal_slot=None, outer_box=None):
        ring = [tuple(p) for p in ring]
        a2 = _area(ring)
        n = len(ring)
        for k in range(n):
            (ax, ay), (bx, by) = ring[k], ring[(k + 1) % n]
            ex, ey = bx - ax, by - ay
            en = (ey, -ex, 0) if a2 > 0 else (-ey, ex, 0)       # the edge's outward normal
            if inward:
                en = (-en[0], -en[1], 0)
            sl = slot
            if reveal_slot and outer_box is not None and not outer_box.exterior.buffer(1e-4).contains(
                    shapely.geometry.LineString([(ax, ay), (bx, by)])):
                sl = reveal_slot                          # (a notch's edge: a reveal, not the bay's own side)
            self.quad_facing((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1), en, sl, shade)

    def prism_xz(self, outline, y0, y1, slot, shade=1.0, cap_slot=None):
        """a plan outline (x, z) extruded up from y0 to y1"""
        cs = cap_slot or slot
        for t in shapely.constrained_delaunay_triangles(Polygon(outline)).geoms:
            c = list(t.exterior.coords)[:3]
            self.tri_facing(*[(p[0], y1, p[1]) for p in c], (0, 1, 0), cs, shade)
            self.tri_facing(*[(p[0], y0, p[1]) for p in c], (0, -1, 0), cs, shade * 0.85)
        ring = [tuple(p) for p in outline]
        a2 = _area(ring)
        n = len(ring)
        for k in range(n):
            (ax, az), (bx, bz) = ring[k], ring[(k + 1) % n]
            ex, ez = bx - ax, bz - az
            en = (ez, 0, -ex) if a2 > 0 else (-ez, 0, ex)
            self.quad_facing((ax, y0, az), (bx, y0, bz), (bx, y1, bz), (ax, y1, az), en, slot, shade)

    def cyl(self, cx, cz, r, y0, y1, slot, n=8, shade=1.0, r1=None, caps=True):
        r1 = r if r1 is None else r1
        a = [(cx + r * math.cos(math.tau * k / n), y0, cz - r * math.sin(math.tau * k / n)) for k in range(n)]
        b = [(cx + r1 * math.cos(math.tau * k / n), y1, cz - r1 * math.sin(math.tau * k / n)) for k in range(n)]
        for k in range(n):
            j = (k + 1) % n
            self.quad(a[k], a[j], b[j], b[k], slot, shade)
        if caps:
            if r > 1e-5:
                for k in range(1, n - 1):
                    self.tri(a[0], a[k + 1], a[k], slot, shade * 0.85)
            if r1 > 1e-5:
                for k in range(1, n - 1):
                    self.tri(b[0], b[k], b[k + 1], slot, shade)

    def tube(self, p0, p1, r, slot, n=5, shade=1.0):
        """a closed rod between two points"""
        p0, p1 = np.array(p0, float), np.array(p1, float)
        ax = p1 - p0
        L = np.linalg.norm(ax)
        if L < 1e-5:
            return
        z = ax / L
        x = np.cross(z, [0, 1, 0] if abs(z[1]) < 0.9 else [1, 0, 0])
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        ring0 = [p0 + r * (math.cos(math.tau * k / n) * x + math.sin(math.tau * k / n) * y) for k in range(n)]
        ring1 = [p + ax for p in ring0]
        for k in range(n):
            j = (k + 1) % n
            self.quad(ring0[k], ring0[j], ring1[j], ring1[k], slot, shade)
        for k in range(1, n - 1):
            self.tri(ring0[0], ring0[k + 1], ring0[k], slot, shade)
            self.tri(ring1[0], ring1[k], ring1[k + 1], slot, shade)

    def lathe(self, prof, slot, n=10, cx=0.0, cz=0.0, shade=1.0):
        """revolve [(r, y), ...] (bottom to top) about the vertical through (cx, cz); r 0 closes to a point"""
        rings = [[(cx + r * math.cos(math.tau * k / n), y, cz - r * math.sin(math.tau * k / n)) for k in range(n)]
                 for r, y in prof]
        for i in range(len(prof) - 1):
            r0, r1 = prof[i][0], prof[i + 1][0]
            for k in range(n):
                j = (k + 1) % n
                if r0 < 1e-6 and r1 < 1e-6:
                    continue
                if r0 < 1e-6:
                    self.tri((cx, prof[i][1], cz), rings[i + 1][j], rings[i + 1][k], slot, shade)
                elif r1 < 1e-6:
                    self.tri(rings[i][k], rings[i][j], (cx, prof[i + 1][1], cz), slot, shade)
                else:
                    self.quad(rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k], slot, shade)
        if prof[0][0] > 1e-6:
            for k in range(1, n - 1):
                self.tri(rings[0][0], rings[0][k + 1], rings[0][k], slot, shade * 0.85)
        if prof[-1][0] > 1e-6:
            for k in range(1, n - 1):
                self.tri(rings[-1][0], rings[-1][k], rings[-1][k + 1], slot, shade)

    def pane(self, x0, y0, x1, y1, z, slot="glass", shade=1.0):
        """a glass pane in the x-y plane facing +Z, with its own 0..1 UVs (interior mapping); one-sided"""
        self.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), slot, shade, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])

    def add(self, other, xf=None):
        """another Mesh, transformed by xf (a function point -> point)"""
        for s in SLOTS:
            for a, b, c, sh, uv in other.tris[s]:
                if xf:
                    a, b, c = xf(a), xf(b), xf(c)
                self.tris[s].append((a, b, c, sh, uv))

    def count(self):
        return sum(len(v) for v in self.tris.values())

    def bounds(self):
        pts = [p for v in self.tris.values() for t in v for p in t[:3]]
        if not pts:
            return [0, 0, 0], [0, 0, 0]
        a = np.array(pts)
        return a.min(axis=0).tolist(), a.max(axis=0).tolist()


def _area(ring):
    return sum(ring[k][0] * ring[(k + 1) % len(ring)][1] - ring[(k + 1) % len(ring)][0] * ring[k][1] for k in range(len(ring))) / 2


def _ccw(ring):
    ring = [tuple(p) for p in ring]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    return ring if _area(ring) > 0 else list(reversed(ring))


def _area_xz(ring):
    # CCW seen from +Y means CCW in (x, -z)
    return _area([(x, -z) for x, z in ring])


def mirror_x(p):
    return (-p[0], p[1], p[2])


def rot_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return lambda p: (c * p[0] + s * p[2], p[1], -s * p[0] + c * p[2])


def move(dx=0.0, dy=0.0, dz=0.0):
    return lambda p: (p[0] + dx, p[1] + dy, p[2] + dz)


# ------------------------------------------------------------------ arches (outlines in x-y, the opening's bottom at y0)
def arch(shape, w, h, y0=0.0, n=8):
    """an opening outline (CCW, x-y): rect | round | pointed | horseshoe | lobed; w wide, h tall to the crown"""
    hw = w / 2
    if shape == "rect":
        return [(-hw, y0), (hw, y0), (hw, y0 + h), (-hw, y0 + h)]
    pts = [(-hw, y0), (hw, y0)]
    if shape == "round":
        spring = y0 + h - hw
        pts.append((hw, spring))
        for k in range(1, n):
            a = math.pi * k / n
            pts.append((hw * math.cos(a), spring + hw * math.sin(a)))
        pts.append((-hw, spring))
    elif shape == "pointed":
        spring = y0 + h - w * 0.75
        r = w * 0.8                                  # two arcs from centres inside the span
        for side in (1, -1):
            cx = -side * (r - hw)
            seg = []
            a0 = math.atan2(0, side * hw - cx)
            a1 = math.atan2(h - (spring - y0), -cx)
            for k in range(n // 2 + 1):
                a = a0 + (a1 - a0) * k / (n // 2)
                seg.append((cx + r * math.cos(a), spring + r * math.sin(a)))
            if side == 1:
                pts += seg[:-1] + [(0.0, y0 + h)]
            else:
                pts += list(reversed(seg))[1:]
        pts = [(-hw, y0), (hw, y0)] + [p for p in pts[2:]]
        pts.append((-hw, spring))
    elif shape == "horseshoe":
        # the circle continues past the springing: wider than the opening at its widest
        r = hw * 1.15
        cy = y0 + h - r
        a_spring = math.asin(min(1.0, hw / r))       # where the circle meets the jambs (below its centre)
        start = -math.pi / 2 + a_spring
        end = math.pi * 1.5 - a_spring
        pts.append((hw, cy - r * math.cos(a_spring)))
        for k in range(1, n * 2):
            a = start + (end - start) * k / (n * 2)
            pts.append((r * math.cos(a), cy + r * math.sin(a)))
        pts.append((-hw, cy - r * math.cos(a_spring)))
    elif shape == "lobed":
        spring = y0 + h - hw
        for k in range(1, n * 3):
            a = math.pi * k / (n * 3)
            rr = hw * (1.0 - 0.12 * abs(math.sin(a * 5)))
            pts.append((rr * math.cos(a), spring + rr * math.sin(a)))
        pts = [(-hw, y0), (hw, y0), (hw, spring)] + pts[2:] + [(-hw, spring)]
    return _dedupe(pts)


def _dedupe(pts, eps=1e-4):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if abs(out[0][0] - out[-1][0]) < eps and abs(out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


# ------------------------------------------------------------------ export
def export_glb(path, pieces, colours=None):
    """pieces: [(name, Mesh)] -> one glb, a node per piece, a primitive per used slot (material "wk_<slot>").
    colours: optional {slot: (r, g, b)} to bake a palette into COLOR_0 (previews); else COLOR_0 = the grey shade."""
    bin_ = bytearray()
    views, accs, meshes, nodes, mats, mat_ix = [], [], [], [], [], {}

    def view(data, target):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(data)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(views) - 1

    def acc(arr, comp, typ, target, norm=False, minmax=False):
        a = {"bufferView": view(arr.tobytes(), target), "componentType": comp, "count": int(arr.shape[0]), "type": typ}
        if norm:
            a["normalized"] = True
        if minmax:
            a["min"] = [float(v) for v in arr.min(axis=0)]
            a["max"] = [float(v) for v in arr.max(axis=0)]
        accs.append(a)
        return len(accs) - 1

    for name, m in pieces:
        prims = []
        for slot in SLOTS:
            ts = m.tris[slot]
            if not ts:
                continue
            pos, nrm, col, uvs = [], [], [], []
            for a, b, c, sh, uv in ts:
                a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
                n = np.cross(b - a, c - a)
                ln = np.linalg.norm(n)
                if ln < 1e-12:
                    continue
                n /= ln
                pos += [a, b, c]
                nrm += [n, n, n]
                if colours:
                    rgb = np.array(colours.get(slot, (0.7, 0.7, 0.7))) * sh
                    col += [list(rgb) + [1.0]] * 3
                else:
                    col += [[sh, sh, sh, 1.0]] * 3
                if uv is not None:
                    uvs += [uv[0], uv[1], uv[2]]
                else:
                    # planar metres / 3 on the face's dominant plane
                    ax = int(np.argmax(np.abs(n)))
                    ij = [k for k in range(3) if k != ax]
                    uvs += [(p[ij[0]] / 3.0, p[ij[1]] / 3.0) for p in (a, b, c)]
            if not pos:
                continue
            P = np.array(pos, np.float32)
            attrs = {"POSITION": acc(P, 5126, "VEC3", 34962, minmax=True),
                     "NORMAL": acc(np.array(nrm, np.float32), 5126, "VEC3", 34962),
                     "COLOR_0": acc(np.clip(np.round(np.array(col, np.float32) * 255), 0, 255).astype(np.uint8), 5121, "VEC4", 34962, norm=True),
                     "TEXCOORD_0": acc(np.array(uvs, np.float32), 5126, "VEC2", 34962)}
            idx = np.arange(P.shape[0], dtype=np.uint32)
            small = P.shape[0] < 65536
            ia = acc(idx.astype(np.uint16) if small else idx, 5123 if small else 5125, "SCALAR", 34963)
            mn = "wk_" + slot
            if mn not in mat_ix:
                rough = {"glass": 0.08, "metal": 0.45, "water": 0.05, "emissive": 0.6}.get(slot, 0.92)
                mt = {"name": mn, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0, "roughnessFactor": rough}}
                if slot == "emissive":
                    mt["emissiveFactor"] = [1, 0.85, 0.6]
                mat_ix[mn] = len(mats)
                mats.append(mt)
            prims.append({"attributes": attrs, "indices": ia, "material": mat_ix[mn]})
        if not prims:
            continue
        meshes.append({"name": name, "primitives": prims})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
    while len(bin_) % 4:
        bin_.append(0)
    gl = {"asset": {"version": "2.0", "generator": "remake/blender/sky/warren_kit"}, "scene": 0,
          "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes, "materials": mats,
          "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(bin_)}]}
    js = json.dumps(gl, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    with open(path, "wb") as f:
        f.write(out)
    return len(out)
