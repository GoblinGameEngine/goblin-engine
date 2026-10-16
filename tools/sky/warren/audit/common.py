"""common.py -- shared readers for the offline warren audit (tools/sky/warren/audit).

Everything here mirrors what the game reads at runtime:
  * the warren file (FORMAT.md v3) with its chunk table (the runtime merges collision per chunk),
  * pieces.json + kit/kit.glb (the piece meshes as the runtime sees them: raw mesh vertices, no node transform),
  * islands.json (the deck height grid, faces, fence, bridges),
  * the island's rock.glb ("deck-col": the deck's drawn mesh AND its trimesh collision),
  * the bridge styles' glbs (sky_bridge.gd: every mesh of a bridge is a trimesh body named "solid").
"""
import gzip
import json
import math
import os
import struct

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
GP = os.path.join(ROOT, "godot_project")
WR = os.path.join(GP, "remake", "sky", "warrens")
ISL_DIR = os.path.join(GP, "remake", "sky", "islands")
PIECES_JSON = os.path.join(WR, "pieces.json")
KIT_GLB = os.path.join(WR, "kit", "kit.glb")
ISLANDS_JSON = os.path.join(GP, "remake", "sky", "islands.json")
BRIDGES_JSON = os.path.join(GP, "remake", "sky", "bridges", "bridge_styles.json")
OUT = os.path.join(ROOT, "reference", "tmp", "audit")
CACHE = os.path.join(OUT, "cache")

CELL = 3.0
STOREY = 3.2
CH = 8                      # chunk: 8 x 8 cells
SLAB_M = 0.4                # sky_warren.gd _floor_slabs
TUCK_M = 0.1                # sky_warren.gd deck tuck
TUCK_R = 2.2

# the player (scenes/StationPlayer.tscn, scripts/StationPlayer.gd)
CAP_R = 0.18
CAP_H = 1.45                # total height (Godot CapsuleShape3D height includes the caps)
CAP_OFF = -0.705            # collision shape offset from the body origin
ORIGIN_ABOVE_FEET = CAP_H / 2 - CAP_OFF   # 1.43 m: the body origin above the capsule's bottom
FLOOR_MAX_DEG = 55.0
FLOOR_SNAP = 0.5
WALK_SPEED = 4.2
GRAVITY = 9.8 * 0.89        # walktest.gd's fall


def res_path(p):
    """res://... -> a file path"""
    return os.path.join(GP, p[len("res://"):]) if p.startswith("res://") else p


# ------------------------------------------------------------------ glTF (a small general reader)
_CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8, 5122: np.int16, 5120: np.int8}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_gltf(path):
    """{'nodes': [{name, mesh, children, matrix(4x4 local)}], 'meshes': [[(material, tris (T,3,3) float64)]],
    'roots': [...]} -- node local matrices from TRS or matrix"""
    raw = open(path, "rb").read()
    jl, _ = struct.unpack_from("<II", raw, 12)
    js = json.loads(raw[20:20 + jl])
    bl, _ = struct.unpack_from("<II", raw, 20 + jl)
    b = raw[28 + jl:28 + jl + bl]

    def acc(i):
        a = js["accessors"][i]
        v = js["bufferViews"][a["bufferView"]]
        nc = _NC[a["type"]]
        dt = np.dtype(_CT[a["componentType"]])
        off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        st = v.get("byteStride")
        if st and st != nc * dt.itemsize:
            arr = np.lib.stride_tricks.as_strided(np.frombuffer(b, dt, offset=off), (a["count"], nc), (st, dt.itemsize))
            arr = np.array(arr)
        else:
            arr = np.frombuffer(b, dt, a["count"] * nc, off).reshape(a["count"], nc)
        return arr if nc > 1 else arr[:, 0]

    meshes = []
    for m in js.get("meshes", []):
        prims = []
        for p in m["primitives"]:
            if p.get("mode", 4) != 4:
                continue
            pos = acc(p["attributes"]["POSITION"]).astype(np.float64)
            ix = acc(p["indices"]).astype(np.int64) if "indices" in p else np.arange(len(pos))
            mat = js["materials"][p["material"]].get("name", "") if "material" in p else ""
            prims.append((mat, pos[ix.reshape(-1, 3)]))
        meshes.append(prims)
    nodes = []
    for nd in js.get("nodes", []):
        if "matrix" in nd:
            M = np.array(nd["matrix"], float).reshape(4, 4).T
        else:
            M = trs(nd.get("translation", [0, 0, 0]), nd.get("rotation", [0, 0, 0, 1]), nd.get("scale", [1, 1, 1]))
        nodes.append({"name": nd.get("name", ""), "mesh": nd.get("mesh"), "children": nd.get("children", []), "matrix": M})
    sc = js.get("scenes", [{}])[js.get("scene", 0)] if js.get("scenes") else {}
    roots = sc.get("nodes")
    if roots is None:
        kids = {c for n in nodes for c in n["children"]}
        roots = [i for i in range(len(nodes)) if i not in kids]
    return {"nodes": nodes, "meshes": meshes, "roots": roots}


def quat_mat(q):
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / n, y / n, z / n, w / n
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def trs(t, r, s):
    M = np.eye(4)
    M[:3, :3] = quat_mat(r) * np.asarray(s, float)[None, :]
    M[:3, 3] = t
    return M


def xf_pts(M, p):
    return p @ M[:3, :3].T + M[:3, 3]


def rot_y(a):
    """Godot Basis(Vector3.UP, a)"""
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


# ------------------------------------------------------------------ the warren file (with the chunk table)
REC_DT = np.dtype([("p", "<u2"), ("i", "u1"), ("j", "u1"), ("k", "u1"), ("rf", "u1"), ("pe", "u1")])


def read_warren(iid, wdir=None):
    wdir = wdir or WR
    side = json.load(open(os.path.join(wdir, iid + ".json")))
    raw = gzip.open(os.path.join(wdir, iid + ".bin.gz")).read()
    assert raw[:4] == b"WRN1"
    o = [4]

    def rd(fmt):
        v = struct.unpack_from(fmt, raw, o[0])
        o[0] += struct.calcsize(fmt)
        return v

    def rs():
        (n,) = rd("<H")
        s = raw[o[0]:o[0] + n].decode()
        o[0] += n
        return s
    (ver,) = rd("<H")
    civ = rs()
    x0, z0, cell, storey = rd("<ffff")
    nx, nz, levels = rd("<HHB")
    (npal,) = rd("<B")
    o[0] += 3 * npal
    ids = [rs() for _ in range(rd("<H")[0])]
    for _ in range(rd("<H")[0]):
        rs()
    (nch,) = rd("<H")
    table = [rd("<BBII") for _ in range(nch)]
    (nrec,) = rd("<I")
    recs = np.frombuffer(raw, REC_DT, nrec, o[0]).copy()
    o[0] += 7 * nrec
    units = [rd("<BBBH") for _ in range(rd("<H")[0])]
    doors = [rd("<HBBBBB") for _ in range(rd("<H")[0])]
    travel = rd("<ffff")
    chunk = np.zeros(nrec, np.int32)
    for n, (ci, cj, first, cnt) in enumerate(table):
        chunk[first:first + cnt] = n
    return {"iid": iid, "side": side, "version": ver, "civ": civ, "x0": float(x0), "z0": float(z0), "nx": nx, "nz": nz,
            "levels": levels, "ids": ids, "table": table, "recs": recs, "chunk": chunk, "units": units,
            "doors": doors, "travel": travel}


def write_warren_records(src_iid, dst_dir, recs, wdir=None, side=None):
    """(mutation tests) a copy of an island's files in dst_dir with its records replaced -- re-chunked and sorted by
    chunk like writer.py; the twin json copied (or `side`)"""
    wdir = wdir or WR
    raw = gzip.open(os.path.join(wdir, src_iid + ".bin.gz")).read()
    o = [4]

    def rd(fmt):
        v = struct.unpack_from(fmt, raw, o[0])
        o[0] += struct.calcsize(fmt)
        return v

    def rs():
        (n,) = rd("<H")
        o[0] += n
    rd("<H")
    rs()
    rd("<ffff")
    rd("<HHB")
    (npal,) = rd("<B")
    o[0] += 3 * npal
    for _ in range(rd("<H")[0]):
        rs()
    for _ in range(rd("<H")[0]):
        rs()
    head_end = o[0]
    (nch,) = rd("<H")
    o[0] += 10 * nch
    (nrec,) = rd("<I")
    tail = raw[o[0] + 7 * nrec:]
    recs = np.asarray(recs, REC_DT)
    ck = (recs["i"].astype(np.int64) // CH) * 1000 + recs["j"].astype(np.int64) // CH
    order = np.argsort(ck, kind="stable")
    recs = recs[order]
    ck = ck[order]
    out = bytearray(raw[:head_end])
    keys, first, cnt = np.unique(ck, return_index=True, return_counts=True)
    out += struct.pack("<H", len(keys))
    for k, f, c in zip(keys, first, cnt):
        out += struct.pack("<BBII", int(k // 1000), int(k % 1000), int(f), int(c))
    out += struct.pack("<I", len(recs))
    out += recs.tobytes()
    out += tail
    os.makedirs(dst_dir, exist_ok=True)
    with gzip.open(os.path.join(dst_dir, src_iid + ".bin.gz"), "wb") as f:
        f.write(bytes(out))
    js = side if side is not None else json.load(open(os.path.join(wdir, src_iid + ".json")))
    json.dump(js, open(os.path.join(dst_dir, src_iid + ".json"), "w"))


# ------------------------------------------------------------------ islands.json
_ISL = {}


def island(iid):
    if not _ISL:
        for d in json.load(open(ISLANDS_JSON))["islands"]:
            _ISL[d["id"]] = d
    return _ISL[iid]


class Deck:
    """sky_island.gd deck_y: the layout's height grid, bilinear (vectorised)"""

    def __init__(self, isl):
        import base64
        H = isl.get("height") or {}
        self.ok = bool(H)
        if not self.ok:
            return
        self.g = np.frombuffer(base64.b64decode(H["data"]), "<i2").reshape(H["nz"], H["nx"]).astype(np.float64) * 0.01
        self.x0, self.z0, self.step, self.nx, self.nz = float(H["x0"]), float(H["z0"]), float(H["step"]), H["nx"], H["nz"]

    def y(self, x, z):
        if not self.ok:
            return np.zeros(np.shape(x))
        x = np.asarray(x, float)
        z = np.asarray(z, float)
        fx = (x - self.x0) / self.step
        fz = (z - self.z0) / self.step
        ix = np.clip(np.floor(fx).astype(int), 0, self.nx - 2)
        iz = np.clip(np.floor(fz).astype(int), 0, self.nz - 2)
        tx = np.clip(fx - ix, 0, 1)
        tz = np.clip(fz - iz, 0, 1)
        g = self.g
        a = g[iz, ix] * (1 - tx) + g[iz, ix + 1] * tx
        b = g[iz + 1, ix] * (1 - tx) + g[iz + 1, ix + 1] * tx
        return a * (1 - tz) + b * tz


# ------------------------------------------------------------------ the kit, as the runtime loads it
class Kit:
    """per piece id: the mesh triangles (local), slot per triangle, the AABB of its vertices, and the runtime's
    collision rule (sky_warren.gd _load_pieces): cmode in ramp | frames | top | mesh | box | '' and its data"""

    def __init__(self):
        self.pj = json.load(open(PIECES_JSON))
        self.P = self.pj["pieces"]
        g = read_gltf(KIT_GLB)
        by_name = {}
        for nd in g["nodes"]:
            if nd["mesh"] is not None:
                by_name[nd["name"]] = g["meshes"][nd["mesh"]]
        self.mesh = {}
        self.slot = {}
        self.aabb = {}
        self.rule = {}
        for pid, spec in self.P.items():
            prims = by_name.get(spec.get("mesh", pid))
            if prims is None:
                continue
            tris = np.concatenate([t for _, t in prims]) if prims else np.zeros((0, 3, 3))
            mats = np.concatenate([np.full(len(t), m, object) for m, t in prims]) if prims else np.zeros(0, object)
            self.mesh[pid] = tris
            self.slot[pid] = mats
            v = tris.reshape(-1, 3)
            lo, hi = (v.min(0), v.max(0)) if len(v) else (np.zeros(3), np.zeros(3))
            self.aabb[pid] = (lo, hi)
            self.rule[pid] = self._rule(pid, spec, tris, lo, hi)

    @staticmethod
    def _rule(pid, spec, tris, lo, hi):
        col = spec.get("collide", True)
        collide = (col is True) or col in ("ramp", "frame")
        kind = str(spec.get("kind", ""))
        cmode, cdata = ("box" if collide else ""), (lo.copy(), hi.copy())
        if col == "ramp":
            q = np.array([p for quad in spec.get("ramp", []) for p in quad], float).reshape(-1, 4, 3)
            if len(q):
                return "ramp", q
            return "top", Kit._top(lo, hi)            # (an old kit's fitted ramp: not needed, every ramp has quads)
        if col == "frame":
            return "frames", [(np.array(b[0], float), np.array(b[1], float)) for b in spec.get("frame", [])]
        if not collide:
            return "", None
        if kind in ("ground", "slab", "roof") or (kind == "interior" and hi[1] - lo[1] < 0.3):
            return "top", Kit._top(lo, hi)
        if kind in ("passage", "bridge") or ("arch" in pid and "blind" not in pid):
            return "mesh", tris
        if kind in ("wall", "edge") and hi[2] > 0.12:
            h2 = hi.copy()
            h2[2] = 0.12
            return "box", (lo.copy(), h2)
        return cmode, cdata

    @staticmethod
    def _top(lo, hi):
        y = hi[1]
        return np.array([[lo[0], y, lo[2]], [hi[0], y, lo[2]], [hi[0], y, hi[2]], [lo[0], y, hi[2]]], float)

    def whole_cell(self, pid):
        lo, hi = self.aabb[pid]
        return lo[0] <= -1.45 and hi[0] >= 1.45 and lo[2] <= -1.45 and hi[2] >= 1.45


def box_tris(lo, hi, R=None, t=None):
    """sky_warren.gd _box_faces: 12 triangles of a box (local lo..hi), turned by R and moved by t"""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    k = np.arange(8)
    p = lo + (hi - lo) * np.stack([k & 1, (k >> 1) & 1, (k >> 2) & 1], 1)
    if R is not None:
        p = p @ R.T
    if t is not None:
        p = p + t
    q = np.array([[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]])
    tri = np.concatenate([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
    return p[tri]


def quads_tris(q):
    """(n,4,3) quads -> (2n,3,3) as the runtime splits them: [0,1,2], [0,2,3]"""
    q = np.asarray(q).reshape(-1, 4, 3)
    return np.concatenate([q[:, [0, 1, 2]], q[:, [0, 2, 3]]], 0) if len(q) else np.zeros((0, 3, 3))


# ------------------------------------------------------------------ placements
def placements(W, deck):
    """per record: origin (cell centre at its y), rotation index, mount, the world matrix pieces (R, t) with the
    mount offset folded into t -- sky_warren.gd _rec_xf"""
    r = W["recs"]
    i = r["i"].astype(np.float64)
    j = r["j"].astype(np.float64)
    k = r["k"].astype(np.float64)
    fl = r["rf"].astype(np.int64)
    x = W["x0"] + CELL * i + 1.5
    z = W["z0"] + CELL * j + 1.5
    dk = (fl & 4) != 0
    y = STOREY * k + STOREY * 0.25 * (fl >> 6)
    if dk.any():
        y[dk] = deck.y(x[dk], z[dk])
    rot = fl & 3
    mount = (fl >> 4) & 3
    mirror = (fl >> 3) & 1
    a = rot * (math.pi / 2)
    c, s = np.cos(a), np.sin(a)
    off = np.zeros((len(r), 3))
    off[mount == 1] = (0, 0, 1.5)
    off[mount == 2] = (1.5, 0, 1.5)
    # R * off with R = Basis(UP, a): x' = x c + z s, z' = -x s + z c
    tx = x + off[:, 0] * c + off[:, 2] * s
    tz = z - off[:, 0] * s + off[:, 2] * c
    return {"x": x, "y": y, "z": z, "rot": rot, "mount": mount, "deck": dk, "mirror": mirror,
            "t": np.stack([tx, y, tz], 1), "c": c, "s": s}


def apply(P, n, pts):
    """local points (..., 3) of placement n -> world"""
    c, s = P["c"][n], P["s"][n]
    p = np.array(pts, float)
    if P["mirror"][n]:
        p[..., 0] = -p[..., 0]
    out = np.empty_like(p)
    out[..., 0] = p[..., 0] * c + p[..., 2] * s
    out[..., 1] = p[..., 1]
    out[..., 2] = -p[..., 0] * s + p[..., 2] * c
    return out + P["t"][n]


def apply_many(P, idx, pts):
    """the same local points (m, 3) for many placements -> (len(idx), m, 3)"""
    c = P["c"][idx][:, None]
    s = P["s"][idx][:, None]
    p = np.asarray(pts, float)
    px = p[None, :, 0] * np.where(P["mirror"][idx][:, None] == 1, -1, 1)
    out = np.empty((len(idx), len(p), 3))
    out[..., 0] = px * c + p[None, :, 2] * s
    out[..., 1] = p[None, :, 1]
    out[..., 2] = -px * s + p[None, :, 2] * c
    return out + P["t"][idx][:, None, :]


def snap_mm(v):
    """Godot Vector3.snapped(0.001): floor(x / step + 0.5) * step"""
    return np.floor(np.asarray(v) * 1000.0 + 0.5) / 1000.0


def roundi(x):
    """GDScript roundi: half away from zero"""
    return int(math.copysign(math.floor(abs(x) + 0.5), x))
