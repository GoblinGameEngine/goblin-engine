import json, struct, numpy as np
def read(path):
    raw = open(path, "rb").read()
    jl, _ = struct.unpack_from("<II", raw, 12)
    js = json.loads(raw[20:20 + jl])
    bl, _ = struct.unpack_from("<II", raw, 20 + jl)
    b = raw[28 + jl:28 + jl + bl]
    T = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    D = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
    def acc(i):
        a = js["accessors"][i]; v = js["bufferViews"][a["bufferView"]]
        n = a["count"] * T[a["type"]]
        st = v.get("byteStride")
        arr = np.frombuffer(b, D[a["componentType"]], n, v.get("byteOffset", 0) + a.get("byteOffset", 0)) if not st else None
        return arr.reshape(a["count"], T[a["type"]]) if T[a["type"]] > 1 else arr
    out = {}
    for nd in js["nodes"]:
        if "mesh" not in nd: continue
        m = js["meshes"][nd["mesh"]]
        prims = []
        for p in m["primitives"]:
            pos = acc(p["attributes"]["POSITION"]).astype(float)
            ix = acc(p["indices"]).astype(int) if "indices" in p else np.arange(len(pos))
            mat = js["materials"][p["material"]]["name"] if "material" in p else ""
            prims.append((mat, pos[ix.reshape(-1, 3)]))
        out[nd["name"]] = (prims, nd.get("translation"), nd.get("rotation"), nd.get("scale"))
    return out
