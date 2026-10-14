"""render_island.py -- a sky island as laid out (godot_project/remake/sky/islands.json): its rock and deck glb, and
every building at its place, the models' materials rebuilt from their mats.json (render_models.dress).

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_island.py -- OUT_PREFIX ISLAND_ID MODEL_DIR -- VIEW...

MODEL_DIR holds the models' glbs built with SSC_KIT=0 (the kit's pieces inline, so windows and dressing show).
Godot -> Blender: (x, y, z) -> (x, -z, y); a building's yaw about +Y -> about +Z.
VIEW = "<az>:<elev>:<dist>" about the island's centre (az 0: from the south... -Y in Blender = +Z in Godot = west).
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "godot_project")
argv = sys.argv[sys.argv.index("--") + 1:]
out, iid, mdir = argv[0], argv[1], argv[2]
views = argv[argv.index("--", 3) + 1:]
sys.argv = [sys.argv[0], "--", "x", "x", "--"]          # (render_models parses its own argv: give it a dummy)
bpy.ops.wm.read_factory_settings(use_empty=True)

import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("rm_dress", os.path.join(HERE, "render_models.py"))
src = open(os.path.join(HERE, "render_models.py")).read()
dress_src = src[src.index("_imgs = {}"):src.index("x = 0.0\nfor gp in glbs:")]
LIB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "textures", "lib")
exec(dress_src)                                           # (_img, dress)

isl = next(i for i in json.load(open(os.path.join(GP, "remake", "sky", "islands.json")))["islands"] if i["id"] == iid)
# the rock and deck (vertex colours)
bpy.ops.import_scene.gltf(filepath=os.path.join(GP, "remake", "sky", "islands", iid + ".rock.glb"))
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for slot in ob.material_slots:
            m = slot.material
            if m and m.use_nodes:
                bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                attr = m.node_tree.nodes.new("ShaderNodeVertexColor")
                if bsdf:
                    m.node_tree.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
cache = {}
for b in isl["buildings"]:
    gp = os.path.join(mdir, b["model"] + ".glb")
    if not os.path.exists(gp):
        continue
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=gp)
    new = [o for o in bpy.data.objects if o not in before]
    side = os.path.splitext(gp)[0] + ".mats.json"
    defs = json.load(open(side)) if os.path.exists(side) else {}
    root = bpy.data.objects.new("B_" + b["id"], None)
    bpy.context.scene.collection.objects.link(root)
    for ob in new:
        if "-colonly" in ob.name:
            ob.hide_render = True
        if ob.type == "MESH":
            for slot in ob.material_slots:
                m = slot.material
                if m and m.name.split(".")[0] in defs and not m.get("_dressed"):
                    dress(m, defs[m.name.split(".")[0]])
                    m["_dressed"] = 1
        if ob.parent is None:
            ob.parent = root
    root.location = (b["x"], -b["z"], b["y"])
    root.rotation_euler = (0.0, 0.0, b["yaw"])
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.85
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.2
sun.rotation_euler = (math.radians(50), 0, math.radians(210))
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 20000
cam.data.lens = 35
for i, v in enumerate(views):
    f = [float(t) for t in v.split(":")]
    az, el, dist = math.radians(f[0]), math.radians(f[1]), f[2]
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    ctr = Vector((0.0, 0.0, 15.0))
    cam.location = ctr + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)
