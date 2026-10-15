"""render_warren.py -- a warren city assembled from the REAL kit pieces on its island's rock, for review:
tools/sky/warren/assemble.py builds the triangles (the kit's own builders, the placement maths of FORMAT.md, the civ
palette variants baked into the colours) into an .npz; this script loads it into Blender with the rock and renders.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/assemble.py ISLAND_ID TRIS.npz [--box i0,j0,i1,j1]
  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_warren.py -- OUT_PREFIX ISLAND_ID TRIS.npz
      -- VIEW...

VIEW = "<az>:<elev>:<dist>[:<tx>:<ty>:<tz>][@lens]" -- about the island's centre (or a target in island metres); az 0
looks from the south (+X, Godot).  Godot -> Blender: (x, y, z) -> (x, -z, y).
"""
import json
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "godot_project")
argv = sys.argv[sys.argv.index("--") + 1:]
out, iid, npz = argv[0], argv[1], argv[2]
views = argv[argv.index("--", 3) + 1:] if "--" in argv[3:] else ["210:35:420"]
bpy.ops.wm.read_factory_settings(use_empty=True)
isl = next(i for i in json.load(open(os.path.join(GP, "remake", "sky", "islands.json")))["islands"] if i["id"] == iid)
d = np.load(npz)
tris, cols, emis = d["tris"], d["cols"], d["emis"]


def mesh_from(name, T, C, emissive=False):
    n = len(T)
    v = T.reshape(-1, 3)
    vb = np.stack([v[:, 0], -v[:, 2], v[:, 1]], 1)            # (Godot -> Blender)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(vb))
    me.vertices.foreach_set("co", vb.ravel())
    me.loops.add(len(vb))
    me.loops.foreach_set("vertex_index", np.arange(len(vb), dtype=np.int32))
    me.polygons.add(n)
    me.polygons.foreach_set("loop_start", np.arange(0, 3 * n, 3, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(n, 3, np.int32))
    ca = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
    rgba = np.concatenate([np.repeat(C, 3, 0), np.ones((3 * n, 1), np.float32)], 1)
    ca.data.foreach_set("color", rgba.ravel())
    me.update(calc_edges=True)
    me.validate()
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeVertexColor")
    a.layer_name = "col"
    nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    if emissive:
        nt.links.new(a.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 2.0
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)


mesh_from("warren", tris[~emis], cols[~emis])
if emis.any():
    mesh_from("warren_glow", tris[emis], cols[emis], True)

# foliage stand-ins (the species meshes are another stream's): a trunk and a crown, palms tall
GREEN = np.array([0.05, 0.16, 0.04], np.float32)
WOOD = np.array([0.10, 0.05, 0.02], np.float32)
FT, FC = [], []


def fbox(lo, hi, c):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    q = [((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)), ((x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)),
         ((x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)), ((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)),
         ((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1))]
    for a, b, c_, e in q:
        FT.extend([(a, b, c_), (a, c_, e)])
        FC.extend([c, c])


for (x, y, z, sc), sp in zip(d["foliage"], d["fol_sp"]):
    sp = str(sp)
    if "palm" in sp:
        fbox((x - .15, y, z - .15), (x + .15, y + 8 * sc, z + .15), WOOD)
        fbox((x - 1.8 * sc, y + 7.4 * sc, z - 1.8 * sc), (x + 1.8 * sc, y + 8.6 * sc, z + 1.8 * sc), GREEN)
    elif sp in ("reeds", "pot_mint_geranium", "potted_plants"):
        fbox((x - .4, y, z - .4), (x + .4, y + 1.0 * sc, z + .4), GREEN)
    elif sp in ("bougainvillea", "jasmine", "banyan_wall"):
        fbox((x - 1, y + .3, z - .3), (x + 1, y + 3.5 * sc, z + .3),
             np.array([0.5, 0.03, 0.2], np.float32) if sp == "bougainvillea" else GREEN)
    elif sp == "bamboo":
        fbox((x - .6, y, z - .6), (x + .6, y + 6 * sc, z + .6), np.array([0.1, 0.25, 0.05], np.float32))
    else:
        fbox((x - .2, y, z - .2), (x + .2, y + 2.5 * sc, z + .2), WOOD)
        fbox((x - 1.6 * sc, y + 2 * sc, z - 1.6 * sc), (x + 1.6 * sc, y + 5 * sc, z + 1.6 * sc), GREEN)
if FT:
    mesh_from("foliage", np.array(FT, np.float32), np.array(FC, np.float32))

# the island's rock and deck under it
rock = os.path.join(GP, "remake", "sky", "islands", iid + ".rock.glb")
if os.path.exists(rock) and not os.environ.get("NOROCK"):
    bpy.ops.import_scene.gltf(filepath=rock)
    for ob in bpy.context.selected_objects:
        if ob.type == "MESH":
            for slot in ob.material_slots:
                m = slot.material
                if m and m.use_nodes:
                    b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
                    a = m.node_tree.nodes.new("ShaderNodeVertexColor")
                    if b:
                        m.node_tree.links.new(a.outputs["Color"], b.inputs["Base Color"])
            if "-col" in ob.name:
                ob.hide_render = True

sc = bpy.context.scene
eng = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(48), 0, math.radians(200))
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 32
cam.data.clip_end = 5000
sc.collection.objects.link(cam)
sc.camera = cam
cxm = (isl["faces"]["N"] + isl["faces"]["S"]) / 2
czm = (isl["faces"]["E"] + isl["faces"]["W"]) / 2
for vi, v in enumerate(views):
    lens = 32.0
    if "@" in v:
        v, lens = v.split("@")
        lens = float(lens)
    cam.data.lens = lens
    p = [float(t) for t in v.split(":")]
    az, el, dist = math.radians(p[0]), math.radians(p[1]), p[2]
    tgt = (p[3], p[4], p[5]) if len(p) >= 6 else (cxm, 8.0, czm)
    tb = (tgt[0], -tgt[2], tgt[1])                    # (Godot -> Blender)
    # az 0: from the south (+X Godot = +X Blender)
    pos = (tb[0] + dist * math.cos(el) * math.cos(az), tb[1] + dist * math.cos(el) * math.sin(az),
           tb[2] + dist * math.sin(el))
    cam.location = pos
    d = (tb[0] - pos[0], tb[1] - pos[1], tb[2] - pos[2])
    import mathutils  # noqa: E402
    cam.rotation_euler = mathutils.Vector(d).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = "%s_%d.png" % (out, vi)
    bpy.ops.render.render(write_still=True)
print("RENDERED", len(tris), "triangles", len(FT), "foliage tris")
