"""parts_build.py -- build the sky islands' shared parts and bridge styles.

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/remake/blender/sky/parts_build.py -- \
      <abs>/godot_project/remake/sky <abs render dir> [names...]

Writes OUT/bridges/<style>.glb and <style>_road.glb + OUT/bridges/bridge_styles.json, OUT/parts/<part>.glb +
OUT/parts/parts.json, and renders (stowed / half / deployed per style; one view per part) to the render dir
(remake/blender/sky/parts_sheets.py, run with the ssc-assets venv, composes them into research/sky_islands/img/).  Names limit the run (style or part names).
"""
import json
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parts_lib as PL  # noqa: E402
import parts_bridges as PB  # noqa: E402
import parts_props as PP  # noqa: E402
from mathutils import Vector  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, RENDER = argv[0], argv[1]
ONLY = set(argv[2:])
RES = "res://remake/sky"


def nonmanifold(objs):
    bad = 0
    for ob in objs.values():
        if ob.type != "MESH":
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bad += sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
    return bad


def load_json(path, key):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"version": 1, key: {}}


def build_bridges():
    path = os.path.join(OUT, "bridges", "bridge_styles.json")
    doc = load_json(path, "styles")
    doc["frame"] = ("dock-face frame: origin on the face at deck level, +Y up, +Z out of the island, X across. "
                    "Rest pose in the glb = stowed (deploy 0). Per node: keys [[deploy, {pos, rot (quaternion x,y,z,w), scl}]] "
                    "local to its parent, piecewise-linear (lerp pos/scl, slerp rot). Colliders: boxes in their node's local frame. "
                    "nose_y: the nose's deck top (two islands' noses meet at the same height). clear: room the layout must keep "
                    "free (inland: m behind the face along the bridge; along: [x0, x1] beside it on the face, out: m out from the face "
                    "while stowed; below: m under the deck behind the face).")
    doc["reach"] = PB.REACH
    os.makedirs(os.path.join(OUT, "bridges"), exist_ok=True)
    for style, make in PB.STYLES.items():
        if ONLY and style not in ONLY:
            continue
        for suffix, W in (("", 3.6), ("_road", 6.0)):
            PL.clear_scene()
            st = make(W)
            objs = PL.realise(st.root)
            glb = os.path.join(OUT, "bridges", style + suffix + ".glb")
            PL.export_glb(glb)
            ks = PB.keys(st)
            nodes = []
            for name, kk in ks.items():
                n = st.nodes[name]
                nodes.append({"node": name, "parent": n.parent.name,
                              "keys": [[round(d, 4), PL.xf_json(m)] for d, m in kk]})
            entry = {"glb": "%s/bridges/%s%s.glb" % (RES, style, suffix), "style": style, "kind": st.kind, "width": W,
                     "road": suffix == "_road", "reach": PB.REACH, "nose_y": round(st.meta["nose_y"], 3),
                     "seconds": st.meta.get("seconds", 25), "clear": st.meta.get("clear", {}),
                     "nodes": nodes, "colliders": [{"node": c["node"], "center": [round(v, 3) for v in c["center"]], "size": [round(v, 3) for v in c["size"]]} for c in st.cols], "tris": PL.tri_count(st.root),
                     "nonmanifold_edges": nonmanifold(objs)}
            doc["styles"][style + suffix] = entry
            print("BRIDGE %s%s tris %d keys %s nonmanifold %d" % (style, suffix, entry["tris"],
                  {k: len(v) for k, v in ks.items()}, entry["nonmanifold_edges"]))
            if suffix == "":
                render_bridge(st, objs, style)
    with open(path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))


def render_bridge(st, objs, style):
    # a stand-in for the island (not exported) and a post where the other island's nose will be
    stand = PL.Node("_island")
    stand.mesh.box((-9, -5, -16), (9, 0, 0), "sky_stone")
    stand.mesh.box((-0.1, -1.5, PB.REACH - 0.05), (0.1, 0.0, PB.REACH + 0.05), "sky_rocket")
    PL.realise(stand)
    cam = PL.render_setup()
    os.makedirs(RENDER, exist_ok=True)
    for tag, d in (("0", 0.0), ("5", 0.5), ("1", 1.0)):
        for name, xf in st.pose(d).items():
            objs[name].matrix_basis = PL.m_g2b(xf)
        bpy.context.view_layer.update()
        PL.render(os.path.join(RENDER, "bridge_%s_%s.png" % (style, tag)), cam, (0, 4.0, 4.0), (-20, 12, 24), w=640, h=480, lens=30)


def build_props():
    path = os.path.join(OUT, "parts", "parts.json")
    doc = load_json(path, "parts")
    doc["frame"] = "game frame (+Y up); edge parts face +Z out of the island. Materials are the shared sky_* palette."
    doc["palette"] = {k: {"rgb": v[0], "roughness": v[1], "metallic": v[2], "two_sided": k in PL.TWO_SIDED}
                      for k, v in PL.PALETTE.items()}
    os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
    for name, fn in PP.props():
        if ONLY and name not in ONLY:
            continue
        PL.clear_scene()
        root, meta = fn()
        objs = PL.realise(root)
        glb = os.path.join(OUT, "parts", name + ".glb")
        PL.export_glb(glb)
        mats = sorted({f[1] for n in root.walk() for f in n.mesh.faces})
        entry = dict(meta)
        entry.update({"path": "%s/parts/%s.glb" % (RES, name), "tris": PL.tri_count(root), "materials": mats,
                      "nonmanifold_edges": nonmanifold(objs)})
        doc["parts"][name] = entry
        print("PART %s tris %d nonmanifold %d" % (name, entry["tris"], entry["nonmanifold_edges"]))
        # one view
        pts = [n.world() @ v for n in root.walk() for v in n.mesh.verts]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        c = (lo + hi) / 2
        r = (hi - lo).length
        cam = PL.render_setup()
        PL.render(os.path.join(RENDER, "part_%s.png" % name), cam, tuple(c), tuple(c + Vector((0.55, 0.35, 0.75)) * r * 1.1),
                  w=480, h=360, lens=35)
    with open(path, "w") as f:
        json.dump(doc, f, separators=(",", ":"))


build_bridges()
build_props()
print("DONE")
