"""glbmesh.py -- read a building .glb's meshes as numpy arrays (no Blender): the shared reader of tools/buildings'
model checker (check_models.py) and kit builder.

    from glbmesh import Glb
    g = Glb(path); for mesh, prim, P, N, U, I, mat in g.prims(): ...
"""
import json
import os
import struct

import numpy as np

CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


class Glb:
    def __init__(self, path):
        b = open(path, "rb").read()
        if b[:4] != b"glTF":
            raise ValueError("not a glb: %s" % path)
        L = struct.unpack("<I", b[12:16])[0]
        self.j = json.loads(b[20:20 + L])
        o = 20 + L
        BL = struct.unpack("<I", b[o:o + 4])[0]
        self.bin = b[o + 8:o + 8 + BL]
        self.path = path

    def acc(self, i):
        A = self.j["accessors"][i]
        V = self.j["bufferViews"][A["bufferView"]]
        dt = CT[A["componentType"]]
        n = NC[A["type"]]
        off = V.get("byteOffset", 0) + A.get("byteOffset", 0)
        stride = V.get("byteStride")
        if stride and stride != np.dtype(dt).itemsize * n:
            raw = np.frombuffer(self.bin, dtype=np.uint8, count=stride * A["count"], offset=off).reshape(A["count"], stride)
            a = raw[:, :np.dtype(dt).itemsize * n].copy().view(dt).reshape(A["count"], n)
        else:
            a = np.frombuffer(self.bin, dtype=dt, count=A["count"] * n, offset=off)
            a = a.reshape(A["count"], n) if n > 1 else a
        return a

    def mat_name(self, i):
        return self.j["materials"][i].get("name", str(i)) if i is not None and i >= 0 else ""

    def prims(self, mesh_filter=None):
        """(mesh name, primitive index, P, N, U, I (tris x 3), material name) for each triangle primitive"""
        for m in self.j.get("meshes", []):
            if mesh_filter and not mesh_filter(m.get("name", "")):
                continue
            for k, pr in enumerate(m["primitives"]):
                if pr.get("mode", 4) != 4:
                    continue
                at = pr["attributes"]
                P = self.acc(at["POSITION"]).astype(np.float64)
                N = self.acc(at["NORMAL"]).astype(np.float64) if "NORMAL" in at else None
                U = self.acc(at["TEXCOORD_0"]).astype(np.float64) if "TEXCOORD_0" in at else None
                I = self.acc(pr["indices"]).astype(np.int64).reshape(-1, 3) if "indices" in pr else np.arange(len(P)).reshape(-1, 3)
                yield m.get("name", ""), k, P, N, U, I, self.mat_name(pr.get("material"))


def _node_matrix(nd):
    if "matrix" in nd:
        return np.array(nd["matrix"], dtype=np.float64).reshape(4, 4).T
    t = np.array(nd.get("translation", [0, 0, 0]), dtype=np.float64)
    x, y, z, w = nd.get("rotation", [0, 0, 0, 1])
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    S = np.diag(nd.get("scale", [1, 1, 1]))
    M = np.eye(4)
    M[:3, :3] = R @ S
    M[:3, 3] = t
    return M


def world_prims(g, mesh_filter=None):
    """Glb.prims() placed where the scene puts them: (node name, mesh name, P, N, U, I, material) in the glb frame"""
    nodes = g.j.get("nodes", [])
    scenes = g.j.get("scenes", [{"nodes": list(range(len(nodes)))}])
    roots = scenes[g.j.get("scene", 0)]["nodes"]
    stack = [(r, np.eye(4)) for r in roots]
    meshes = g.j.get("meshes", [])
    by_mesh = {}
    while stack:
        ni, M0 = stack.pop()
        nd = nodes[ni]
        M = M0 @ _node_matrix(nd)
        if "mesh" in nd:
            by_mesh.setdefault(nd["mesh"], []).append((nd.get("name", ""), M))
        for ch in nd.get("children", []):
            stack.append((ch, M))
    for mi, m in enumerate(meshes):
        if mesh_filter and not mesh_filter(m.get("name", "")):
            continue
        for node_name, M in by_mesh.get(mi, []):
            Rn = np.linalg.inv(M[:3, :3]).T
            for k, pr in enumerate(m["primitives"]):
                if pr.get("mode", 4) != 4:
                    continue
                at = pr["attributes"]
                P = g.acc(at["POSITION"]).astype(np.float64) @ M[:3, :3].T + M[:3, 3]
                N = g.acc(at["NORMAL"]).astype(np.float64) @ Rn.T if "NORMAL" in at else None
                U = g.acc(at["TEXCOORD_0"]).astype(np.float64) if "TEXCOORD_0" in at else None
                I = g.acc(pr["indices"]).astype(np.int64).reshape(-1, 3) if "indices" in pr else np.arange(len(P)).reshape(-1, 3)
                if np.linalg.det(M[:3, :3]) < 0:
                    I = I[:, ::-1]
                yield node_name, m.get("name", ""), P, N, U, I, g.mat_name(pr.get("material"))


_KIT = {}


def kit_prims(g, path):
    """The building's shared parts (<ID>.kit.json beside it, pieces in kit/: remake/blender/gbkit.py) as world_prims
    gives them: what the game draws once RemakeBuilding.merge_kit has folded them in.  A row [piece, x, y, z, yaw] is
    in the Blender frame (the glb's x, z, -y; a turn about Blender z is the same turn about glb y); [piece, node] is a
    door leaf drawn in that node's frame (the node's own mesh is a placeholder: leave out meshes named *_kit)."""
    kp = path[:-4] + ".kit.json"
    if not os.path.exists(kp):
        return
    node_m = {}
    nodes = g.j.get("nodes", [])
    stack = [(r, np.eye(4)) for r in g.j.get("scenes", [{"nodes": list(range(len(nodes)))}])[g.j.get("scene", 0)]["nodes"]]
    while stack:
        ni, M0 = stack.pop()
        M = M0 @ _node_matrix(nodes[ni])
        node_m[nodes[ni].get("name", "")] = M
        stack.extend((ch, M) for ch in nodes[ni].get("children", []))
    kd = os.path.join(os.path.dirname(path), "kit")
    for r in json.load(open(kp)):
        if r[0] not in _KIT:
            pp = os.path.join(kd, r[0] + ".glb")
            _KIT[r[0]] = list(world_prims(Glb(pp))) if os.path.exists(pp) else []
        if len(r) == 2:
            M = node_m.get(r[1])
            if M is None:
                continue
        else:
            c, s_ = np.cos(np.radians(r[4])), np.sin(np.radians(r[4]))
            M = np.array([[c, 0, s_, r[1]], [0, 1, 0, r[3]], [-s_, 0, c, -r[2]], [0, 0, 0, 1.0]])
        R = M[:3, :3]
        Rn = np.linalg.inv(R).T
        for node_name, mesh_name, P, N, U, I, mat in _KIT[r[0]]:
            yield (r[1] if len(r) == 2 else "kit_" + r[0]), mesh_name, P @ R.T + M[:3, 3], \
                (N @ Rn.T if N is not None else None), U, I, mat


def components(I, nv):
    """label per vertex: connected pieces through shared triangle vertices (label propagation, vectorised)"""
    lab = np.arange(nv)
    if len(I) == 0:
        return lab
    while True:
        m = np.minimum(np.minimum(lab[I[:, 0]], lab[I[:, 1]]), lab[I[:, 2]])
        new = lab.copy()
        for k in range(3):
            np.minimum.at(new, I[:, k], m)
        new = new[new]
        if np.array_equal(new, lab):
            return lab
        lab = new


def weld(P, tol=1e-4):
    """index of each vertex's welded position (glTF splits a vertex wherever its normal or UV changes)"""
    q = np.round(P / tol).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    return inv.reshape(-1)
