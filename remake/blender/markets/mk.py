"""mk.py -- the flea-market kit's core: slots and material groups, the atlas cells, geometry helpers and the glb
exporter.  The geometry is the warren kit's (remake/blender/sky/warren_kit/geom.py: pure Python + shapely, flat-shaded
faces, a SLOT per triangle, a grey SHADE in COLOR_0) with the market kit's own slot list patched in, so the warren
kit's flicker cure (flicker.py) and MID helpers (mid.py) run on market pieces unchanged.

Frame (every piece): glTF / Godot, +Y up, metres; origin at the footprint centre on the ground (y 0 = the lot / lawn
surface or, for moving pieces, the cabin floor); the piece's FRONT faces +Z (the aisle, the road, the customer).

Slots are PALETTE CHANNELS (the runtime multiplies COLOR_0's grey shade by the palette colour of the slot); many slots
share one MATERIAL GROUP (one draw per group per merged chunk), see GROUP.
"""
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WK = os.path.join(ROOT, "remake", "blender", "sky", "warren_kit")
sys.path.insert(0, WK)
import geom  # noqa: E402

SLOTS = [
    # solid (vertex colour x palette): one draw
    "wall", "trim", "frame", "wood", "roof", "fabric", "accent", "accent2", "concrete", "ground", "paint", "paint2",
    "plant", "rope", "dark", "cream",
    # metal: one draw
    "metal", "steel", "brass",
    # canvas: tent cloth with the night lobe (lit through from inside; at most 0.9 HDR at full night)
    "canvas_a", "canvas_b", "canvas_c", "lining",
    # glass
    "glass",
    # glow: lit FACES (lantern glass and paper, lightbox faces, a cabin's lit ceiling panel): at most 0.9 HDR
    "glow", "glow_b",
    # emissive: bulbs, neon tubes and lamp lenses: 2.0 HDR at full night (over the 1.5 glow threshold: a thin halo)
    "bulb", "bulb_a", "bulb_b", "bulb_c", "bulb_d", "neon", "neon_b", "lamp", "warn",
    # textured (white palette; albedo + emit mask from the sign atlases): one draw per atlas
    "sign", "mascot", "stall", "goods", "text",
]
geom.SLOTS[:] = SLOTS             # (in place: geom, flicker, mid and passes all hold this list object)

from geom import Mesh, move, rot_y, mirror_x  # noqa: E402,F401
import flicker  # noqa: E402,F401
import mid as wmid  # noqa: E402,F401

GROUP = {s: "solid" for s in SLOTS[:16]}
GROUP.update({s: "metal" for s in ("metal", "steel", "brass")})
GROUP.update({s: "canvas" for s in ("canvas_a", "canvas_b", "canvas_c", "lining")})
GROUP.update({"glass": "glass", "glow": "glow", "glow_b": "glow"})
GROUP.update({s: "emissive" for s in ("bulb", "bulb_a", "bulb_b", "bulb_c", "bulb_d", "neon", "neon_b", "lamp", "warn")})
GROUP.update({"sign": "tex_markets", "mascot": "tex_mascots", "stall": "tex_stalls", "goods": "tex_goods", "text": "tex_text"})
TEX = {"sign": "markets", "mascot": "mascots", "stall": "stalls", "goods": "goods", "text": "kit_text"}
EMISSIVE = {s for s, g in GROUP.items() if g == "emissive"}
LIT = {"glow", "glow_b"}

# the night emissive scale (shared with the city and island signs, handoff_signs.md 6b)
NIGHT = {"emissive": 2.0, "glow": 0.9, "canvas": 0.35, "tex": 2.0, "glow_threshold": 1.5}

SIGNS_DIR = os.path.join(ROOT, "godot_project", "remake", "signs")
OUT_DIR = os.path.join(ROOT, "godot_project", "remake", "markets")
_cells = None


def cells():
    global _cells
    if _cells is None:
        d = json.load(open(os.path.join(SIGNS_DIR, "signs.json")))
        _cells = d["cells"]
        kt = os.path.join(OUT_DIR, "kit_text.json")
        if os.path.exists(kt):
            _cells.update(json.load(open(kt))["cells"])
    return _cells


def cell_aspect(cid):
    c = cells()[cid]
    x, y, w, h = c["content"]
    return w / h


def cell_uv(cid, sub=(0.0, 0.0, 1.0, 1.0), crop=True):
    """the atlas uv corners of a cell's content box (or a sub-rect of it, fractions of the content box, (x0, y0 top,
    x1, y1)): [BL, BR, TR, TL] in glTF's top-left uv origin"""
    c = cells()[cid]
    u0, v0, du, dv = c["uv"]
    px = 256.0
    x, y, w, h = c["content"] if crop else (0, 0, 256, 256)
    # (half a texel in: no bleeding from the neighbour cell under filtering)
    ax = u0 + du * (x + 0.5 + (w - 1) * sub[0]) / px
    bx = u0 + du * (x + 0.5 + (w - 1) * sub[2]) / px
    ty = v0 + dv * (y + 0.5 + (h - 1) * sub[1]) / px
    by = v0 + dv * (y + 0.5 + (h - 1) * sub[3]) / px
    return [(ax, by), (bx, by), (bx, ty), (ax, ty)]


# ------------------------------------------------------------------ helpers
def V(*a):
    return np.array(a, float)


def quad_uv(m, a, b, c, d, slot, uv, shade=1.0):
    """a, b, c, d counter-clockwise from the front, uv = [uv_a, uv_b, uv_c, uv_d]"""
    m.quad(tuple(a), tuple(b), tuple(c), tuple(d), slot, shade, uv=uv)


def card(m, slot, cid, centre, right, up, h, w=None, two=True, gap=0.02, sub=(0, 0, 1, 1), crop=True, shade=1.0):
    """an atlas cell standing as a card: centred at `centre` (its middle), `h` tall along `up`, its width from the
    content's aspect (or `w`), facing right x up; two=True adds a back card (reading the right way from behind)
    gap behind it.  Returns the four front corners."""
    right, up = V(*right), V(*up)
    right /= np.linalg.norm(right)
    up /= np.linalg.norm(up)
    n = np.cross(right, up)
    if w is None:
        c = cells()[cid]
        cw, ch = (c["content"][2], c["content"][3]) if crop else (256, 256)
        w = h * (cw * (sub[2] - sub[0])) / (ch * (sub[3] - sub[1]))
    o = V(*centre)
    a = o - right * w / 2 - up * h / 2
    b = o + right * w / 2 - up * h / 2
    cc = o + right * w / 2 + up * h / 2
    d = o - right * w / 2 + up * h / 2
    uv = cell_uv(cid, sub, crop)
    quad_uv(m, a, b, cc, d, slot, uv, shade)
    if two:
        g = -n * gap
        quad_uv(m, b + g, a + g, d + g, cc + g, slot, uv, shade)
    return a, b, cc, d, w


def box2(m, lo, hi, slot, shade=1.0, skip=(), slots=None):
    m.box(tuple(lo), tuple(hi), slot, shade, skip=skip, slots=slots)


def sweep(m, pts, r, slot, n=5, shade=1.0, caps=True):
    """a closed tube along a polyline (rings mitred by the averaged tangent)"""
    P = [V(*p) for p in pts]
    if len(P) < 2:
        return
    T = []
    for i in range(len(P)):
        if i == 0:
            t = P[1] - P[0]
        elif i == len(P) - 1:
            t = P[-1] - P[-2]
        else:
            t = (P[i + 1] - P[i]) / max(np.linalg.norm(P[i + 1] - P[i]), 1e-9) + (P[i] - P[i - 1]) / max(np.linalg.norm(P[i] - P[i - 1]), 1e-9)
        T.append(t / max(np.linalg.norm(t), 1e-9))
    ref = V(0, 1, 0) if abs(T[0][1]) < 0.9 else V(1, 0, 0)
    rings = []
    x = np.cross(T[0], ref)
    x /= np.linalg.norm(x)
    for i, p in enumerate(P):
        t = T[i]
        x = x - t * np.dot(x, t)                     # (parallel transport of the ring's frame)
        x /= max(np.linalg.norm(x), 1e-9)
        y = np.cross(t, x)
        rings.append([p + r * (math.cos(math.tau * k / n) * x + math.sin(math.tau * k / n) * y) for k in range(n)])
    for i in range(len(P) - 1):
        for k in range(n):
            j = (k + 1) % n
            m.quad(tuple(rings[i][k]), tuple(rings[i][j]), tuple(rings[i + 1][j]), tuple(rings[i + 1][k]), slot, shade)
    if caps:
        for k in range(1, n - 1):
            m.tri(tuple(rings[0][0]), tuple(rings[0][k + 1]), tuple(rings[0][k]), slot, shade)
            m.tri(tuple(rings[-1][0]), tuple(rings[-1][k]), tuple(rings[-1][k + 1]), slot, shade)


def catenary(p0, p1, sag, n):
    """n + 1 points from p0 to p1 hanging `sag` m at the middle (a parabola: fine for 5-15 % sags)"""
    p0, p1 = V(*p0), V(*p1)
    return [tuple(p0 + (p1 - p0) * (i / n) - V(0, sag * 4 * (i / n) * (1 - i / n), 0)) for i in range(n + 1)]


def bulb(m, p, r, slot, shade=1.0):
    """an octahedron bulb (8 tris, closed)"""
    x, y, z = p
    pts = [(x + r, y, z), (x, y, z - r), (x - r, y, z), (x, y, z + r)]
    top, bot = (x, y + r, z), (x, y - r * 1.25, z)
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        m.tri(a, b, top, slot, shade)          # (a, b CCW seen from above -> b, a for outward) checked below
        m.tri(b, a, bot, slot, shade)


def festoon(m, p0, p1, sag, spacing, slots=("bulb",), r=0.045, wire=0.008, drop=0.1, q=1):
    """a catenary wire with bulbs hanging `drop` under it every `spacing` m; bulb slots cycle through `slots`"""
    L = float(np.linalg.norm(V(*p1) - V(*p0)))
    nb = max(1, int(round(L / spacing)))
    nw = max(4, min(12, nb)) if q else max(3, min(6, nb // 2))
    sweep(m, catenary(p0, p1, sag, nw), wire, "dark", n=3)
    pts = catenary(p0, p1, sag, nb * 2)
    # (a bulb's top touches the wire where the polyline passes: hung directly, cheap -- 8 tris a bulb)
    wp = catenary(p0, p1, sag, nw)
    k = 0
    for i in range(1, nb * 2, 2):
        x, y, z = pts[i]
        t = i / (nb * 2)
        j = min(int(t * nw), nw - 1)
        f = t * nw - j
        yw = wp[j][1] + (wp[j + 1][1] - wp[j][1]) * f
        bulb(m, (x, yw - wire - r, z), r, slots[k % len(slots)])
        k += 1
    return nb


def lathe(m, prof, slot, n=10, cx=0.0, cz=0.0, shade=1.0, y0=0.0):
    """geom's lathe takes its profile bottom to top: a profile written top-down (hanging lanterns) is reversed"""
    if prof[0][1] > prof[-1][1]:
        prof = list(reversed(prof))
    m.lathe([(r, y + y0) for r, y in prof], slot, n=n, cx=cx, cz=cz, shade=shade)


def ring_torus(m, c, R, r, slot, axis="y", n=10, k=4):
    """a closed torus ring centred at c, its axis along `axis`"""
    c = V(*c)
    pts = []
    for i in range(n):
        a = math.tau * i / n
        if axis == "y":
            pts.append(c + V(R * math.cos(a), 0, R * math.sin(a)))
        elif axis == "x":
            pts.append(c + V(0, R * math.cos(a), R * math.sin(a)))
        else:
            pts.append(c + V(R * math.cos(a), R * math.sin(a), 0))
    rings = []
    for i in range(n):
        p = pts[i]
        t = pts[(i + 1) % n] - pts[i - 1]
        t /= np.linalg.norm(t)
        out = p - c
        out /= np.linalg.norm(out)
        b = np.cross(t, out)
        rings.append([p + r * (math.cos(math.tau * j / k) * out + math.sin(math.tau * j / k) * b) for j in range(k)])
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(k):
            jj = (j + 1) % k
            m.quad_facing(tuple(a[j]), tuple(b[j]), tuple(b[jj]), tuple(a[jj]),
                          tuple((a[j] + a[jj]) / 2 - pts[i]), slot)


def sheet(m, grid, slot, slot_b=None, stripe=None, shade=1.0, back=None, back_off=0.0, normal_hint=None):
    """a surface from a grid of points (rows x cols): quads between neighbours; `stripe(i, j)` picks slot_b for a
    quad (alternating gores / candy stripes); `back` adds a second surface facing the other way (a lining) moved
    back_off along its normal hint"""
    G = [[V(*p) for p in row] for row in grid]
    for i in range(len(G) - 1):
        for j in range(len(G[0]) - 1):
            a, b, c, d = G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]
            s = slot_b if (slot_b and stripe and stripe(i, j)) else slot
            if normal_hint is not None:
                h = normal_hint((a + b + c + d) / 4)
                m.quad_facing(tuple(a), tuple(b), tuple(c), tuple(d), tuple(h), s, shade)
                if back:
                    o = -V(*h) / max(np.linalg.norm(h), 1e-9) * back_off
                    m.quad_facing(tuple(a + o), tuple(b + o), tuple(c + o), tuple(d + o), tuple(-V(*h)), back, shade * 0.9)
            else:
                m.quad(tuple(a), tuple(b), tuple(c), tuple(d), s, shade)


def xf_mesh(src, xf):
    out = Mesh()
    out.add(src, xf)
    return out


def place(m, src, x=0.0, y=0.0, z=0.0, yaw=0.0):
    r = rot_y(yaw)
    m.add(src, lambda p: (r(p)[0] + x, r(p)[1] + y, r(p)[2] + z))


def rot_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return lambda p: (p[0], c * p[1] - s * p[2], s * p[1] + c * p[2])


def rot_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return lambda p: (c * p[0] - s * p[1], s * p[0] + c * p[1], p[2])


def compose(*fs):
    def f(p):
        for g in fs:
            p = g(p)
        return p
    return f


def rounded_rect(w, d, r, n=3):
    """a plan outline (x, z) w x d with corners rounded by r (n segments a corner), CCW seen from +Y"""
    out = []
    hw, hd = w / 2, d / 2
    for cx, cz, a0 in ((hw - r, hd - r, 0.0), (-hw + r, hd - r, 90.0), (-hw + r, -hd + r, 180.0), (hw - r, -hd + r, 270.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    # (CCW seen from +Y = CCW in (x, -z))
    if geom._area([(x, -z) for x, z in out]) < 0:
        out.reverse()
    return out


# ------------------------------------------------------------------ export
def export_glb(path, pieces, colours=None, tex_uri=None):
    """pieces: [(name, Mesh)] -> one glb, a node per piece, a primitive per used slot (material "mk_<slot>").
    colours: {slot: (r, g, b)} bakes a palette into COLOR_0 (previews); else COLOR_0 = the grey shade.
    tex_uri: {atlas name: uri} for the textured slots' images (relative to the glb)."""
    bin_ = bytearray()
    views, accs, meshes, nodes, mats, mat_ix = [], [], [], [], [], {}
    images, textures, img_ix = [], [], {}

    def view(data, target):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(data)
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target:
            v["target"] = target
        views.append(v)
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

    def tex(name):
        if tex_uri is None or name not in tex_uri:
            return None
        if name not in img_ix:
            images.append({"uri": tex_uri[name], "name": name})
            textures.append({"source": len(images) - 1, "sampler": 0})
            img_ix[name] = len(textures) - 1
        return img_ix[name]

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
            mn = "mk_" + slot
            if mn not in mat_ix:
                g = GROUP[slot]
                rough = {"glass": 0.08, "metal": 0.45, "emissive": 0.6, "glow": 0.6}.get(g, 0.92)
                mt = {"name": mn, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.3 if g == "metal" else 0.0,
                                                           "roughnessFactor": rough},
                      "extras": {"group": g}}
                if g == "emissive":
                    mt["emissiveFactor"] = [1, 0.85, 0.6]
                if slot in TEX:
                    ti = tex(TEX[slot])
                    if ti is not None:
                        mt["pbrMetallicRoughness"]["baseColorTexture"] = {"index": ti}
                        et = tex(TEX[slot] + "_emit")
                        if et is not None:
                            mt["emissiveTexture"] = {"index": et}
                            mt["emissiveFactor"] = [1, 1, 1]
                    mt["alphaMode"] = "MASK"
                    mt["alphaCutoff"] = 0.5
                mat_ix[mn] = len(mats)
                mats.append(mt)
            prims.append({"attributes": attrs, "indices": ia, "material": mat_ix[mn]})
        if not prims:
            continue
        meshes.append({"name": name, "primitives": prims})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
    while len(bin_) % 4:
        bin_.append(0)
    gl = {"asset": {"version": "2.0", "generator": "remake/blender/markets"}, "scene": 0,
          "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes, "materials": mats,
          "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(bin_)}]}
    if images:
        gl["images"] = images
        gl["textures"] = textures
        gl["samplers"] = [{"magFilter": 9729, "minFilter": 9987}]
    js = json.dumps(gl, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    with open(path, "wb") as f:
        f.write(out)
    return len(out)


def hex_rgb(h, linear=True):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    if linear:
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return tuple(c)


# ------------------------------------------------------------------ the piece registry
PIECES = {}


def piece(pid, group, build, *, kind=None, foot=None, lod1="box", collide="frame", frame=None, passes=None, ramps=None,
          anchors=None, walk=None, budget=None, palette=None, notes="", moving=None, mid="auto", extra=None, ground=True):
    """register a piece.  build(q) -> Mesh (q=1 full, q=0 the MID).  frame: collision boxes [[lo], [hi]] (the
    runtime's only collision for "frame" pieces).  passes: walk-through volumes [{"box": [lo, hi], "kind": "open" |
    "door"}].  walk: [[x0, z0, x1, z1, y]] floor areas people stand on (checked for 2.2 m of head room).
    anchors: {name: [x, y, z, yaw_deg]}."""
    PIECES[pid] = dict(group=group, build=build, kind=kind or group, foot=foot, lod1=lod1, collide=collide,
                       frame=frame or [], passes=passes or [], ramps=ramps or [], anchors=anchors or {}, walk=walk or [],
                       budget=budget, palette=palette, notes=notes, moving=moving, mid=mid, extra=extra or {}, ground=ground)
    return PIECES[pid]


def B(x0, y0, z0, x1, y1, z1):
    return [[round(x0, 4), round(y0, 4), round(z0, 4)], [round(x1, 4), round(y1, 4), round(z1, 4)]]


def prism_zy(m, outline_zy, x0, x1, slot, shade=1.0, cap_slot=None):
    """a cross-section in the z-y plane (points (z, y)) extruded along x from x0 to x1"""
    tmp = Mesh()
    tmp.prism_xy([(-z, y) for z, y in outline_zy], [], x0, x1, slot, shade, cap_slot=cap_slot)
    m.add(tmp, rot_y(90))


def flat_poly(m, outer, holes, y, slot, shade=1.0, up=True):
    """a one-sided flat polygon (plan (x, z) points, holes) at height y facing up (paint, decals)"""
    import shapely
    from shapely.geometry import Polygon
    pg = Polygon(outer, holes)
    for t in shapely.constrained_delaunay_triangles(pg).geoms:
        c = list(t.exterior.coords)[:3]
        m.tri_facing(*[(p[0], y, p[1]) for p in c], (0, 1 if up else -1, 0), slot, shade)


def slope_box(m, x0, x1, ya0, ya1, t, z0, z1, slot, shade=1.0):
    """a sloped slab along x: its top runs from (x0, ya0) to (x1, ya1), t thick (vertical), z0..z1 deep"""
    prism_xy_ = [(x0, ya0 - t), (x1, ya1 - t), (x1, ya1), (x0, ya0)]
    m.prism_xy(prism_xy_, [], z0, z1, slot, shade)


def drop_ground(m, eps=0.002):
    """remove the downward faces lying on the ground (y <= eps): never seen, and they shimmer against each other"""
    out = Mesh()
    for s in SLOTS:
        for t in m.tris[s]:
            a, b, c = (np.array(p, float) for p in t[:3])
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            if ln > 1e-12 and n[1] / ln < -0.999 and max(a[1], b[1], c[1]) <= eps and min(a[1], b[1], c[1]) >= -eps:
                continue
            out.tris[s].append(t)
    return out
