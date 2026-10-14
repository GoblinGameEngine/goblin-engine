"""glb.py -- a minimal glTF 2.0 binary writer for the sky islands' generated meshes (no Blender needed: the islands are
plain vertex-coloured meshes made in numpy).

write(path, nodes): nodes = [{"name": str, "positions": (N,3) float, "normals": (N,3) float or None,
"colors": (N,3|4) float 0..1 or None, "indices": (M*3,) int}], every node at the origin, sharing one material per
`material` name (default "sky_rock", vertex colour as albedo).  Godot import hints work as usual: a node named
"<x>-col" gets trimesh collision, "<x>-colonly" collision only.  Positions are in the glTF frame (Y up), which is
the islands' local frame (research/sky_islands/00_plan.md).
"""
import json
import struct

import numpy as np


def smooth_normals(pos, idx):
    pos = np.asarray(pos, np.float64)
    tri = np.asarray(idx, np.int64).reshape(-1, 3)
    fn = np.cross(pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]])
    n = np.zeros_like(pos)
    for k in range(3):
        np.add.at(n, tri[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return n / ln


def write(path, nodes, materials=None):
    materials = materials or {}
    bin_ = bytearray()
    views, accs, meshes, gnodes, mats, mat_ix = [], [], [], [], [], {}

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

    for nd in nodes:
        pos = np.asarray(nd["positions"], np.float32).reshape(-1, 3)
        idx = np.asarray(nd["indices"], np.uint32).reshape(-1)
        if pos.shape[0] == 0 or idx.shape[0] == 0:
            continue
        attrs = {"POSITION": acc(pos, 5126, "VEC3", 34962, minmax=True)}
        nrm = nd.get("normals")
        if nrm is None:
            nrm = smooth_normals(pos, idx)
        attrs["NORMAL"] = acc(np.asarray(nrm, np.float32).reshape(-1, 3), 5126, "VEC3", 34962)
        col = nd.get("colors")
        if col is not None:
            c = np.asarray(col, np.float32)
            if c.shape[1] == 3:
                c = np.concatenate([c, np.ones((c.shape[0], 1), np.float32)], axis=1)
            attrs["COLOR_0"] = acc(np.clip(np.round(c * 255), 0, 255).astype(np.uint8), 5121, "VEC4", 34962, norm=True)
        small = pos.shape[0] < 65536
        ia = acc(idx.astype(np.uint16) if small else idx, 5123 if small else 5125, "SCALAR", 34963)
        mname = nd.get("material", "sky_rock")
        if mname not in mat_ix:
            m = {"name": mname, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0,
                                                         "roughnessFactor": materials.get(mname, {}).get("rough", 0.9)},
                 "doubleSided": bool(materials.get(mname, {}).get("double", False))}
            mat_ix[mname] = len(mats)
            mats.append(m)
        meshes.append({"name": nd["name"], "primitives": [{"attributes": attrs, "indices": ia, "material": mat_ix[mname]}]})
        gnodes.append({"name": nd["name"], "mesh": len(meshes) - 1})
    while len(bin_) % 4:
        bin_.append(0)
    gl = {"asset": {"version": "2.0", "generator": "tools/sky/glb.py"}, "scene": 0,
          "scenes": [{"nodes": list(range(len(gnodes)))}], "nodes": gnodes, "meshes": meshes, "materials": mats,
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
