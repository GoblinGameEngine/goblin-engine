"""render_marks.py -- a building's shipped glb rendered with check_models' findings drawn on it: gap edges as red
tubes, z-fighting spots as yellow balls (tools/buildings/check_models.py --explain ID writes reference/tmp/marks_ID.json).

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_marks.py -- ID OUT_PREFIX [az:elev ...]

Views orbit the model's centre (degrees); default four corners from 35 degrees up. The model is drawn half see-through
so marks inside it show. A close-up: add @X,Y,Z,R (a point in the glb frame, as check_models prints it, and a radius in
m) to orbit that point instead, --solid to draw the model opaque (each material a flat colour, no marks), and
dir=PATH to read the glb from another folder (a trial build).
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
argv = sys.argv[sys.argv.index("--") + 1:]
rid, out = argv[0], argv[1]
focus = next(([float(v) for v in a[1:].split(",")] for a in argv[2:] if a.startswith("@")), None)
solid = "--solid" in argv
GLBS = next((a[4:] for a in argv[2:] if a.startswith("dir=")), os.path.join(ROOT, "godot_project", "remake", "buildings"))
views = [tuple(float(v) for v in a.split(":")) for a in argv[2:] if ":" in a] or [(45, 35), (135, 35), (225, 35), (315, 35)]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(GLBS, rid + ".glb"))
for ob in list(bpy.data.objects):
    if ob.type == "MESH" and ("collision" in ob.name or ob.name.endswith("-colonly")):
        bpy.data.objects.remove(ob)
ghost = bpy.data.materials.new("ghost")
ghost.use_nodes = True
bsdf = ghost.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.78, 1)
bsdf.inputs["Alpha"].default_value = 1.0 if solid else 0.35
try:
    ghost.surface_render_method = "BLENDED"
except Exception:
    ghost.blend_method = "BLEND"
if solid:
    # opaque, each material a flat colour of its own (from the building's .mats.json: tint or colour, else a hash)
    mdefs = json.load(open(os.path.join(GLBS, rid + ".mats.json")))
    for m in bpy.data.materials:
        d = mdefs.get(m.name)
        if not d or not m.use_nodes or "Principled BSDF" not in m.node_tree.nodes:
            continue
        col = d.get("tint") or d.get("color")
        if not col:
            h = abs(hash(d.get("tex") or m.name))
            col = [0.25 + 0.6 * ((h >> s_) % 97) / 96 for s_ in (0, 8, 16)]
        bs = m.node_tree.nodes["Principled BSDF"]
        for l_ in list(bs.inputs["Base Color"].links):
            m.node_tree.links.remove(l_)
        bs.inputs["Base Color"].default_value = (*col[:3], 1)
else:
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(ghost)

mp = os.path.join(ROOT, "reference", "tmp", "marks_%s.json" % rid)
marks = json.load(open(mp)) if os.path.exists(mp) and not solid else {"gaps": [], "zfight": []}


def emit(name, col):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = col
    e.inputs[1].default_value = 4.0
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def g2b(p):                                                   # glTF (Y up) -> Blender (Z up)
    return Vector((p[0], -p[2], p[1]))


if marks["gaps"]:
    cu = bpy.data.curves.new("gaps", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = min(0.03, focus[3] * 0.004) if focus else 0.03
    for a, b in marks["gaps"]:
        sp = cu.splines.new("POLY")
        sp.points.add(1)
        sp.points[0].co = (*g2b(a), 1)
        sp.points[1].co = (*g2b(b), 1)
    ob = bpy.data.objects.new("gaps", cu)
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(emit("red", (1, 0.05, 0.05, 1)))
ylw = emit("yellow", (1, 0.9, 0.1, 1))
for p in marks["zfight"][:200]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=min(0.08, focus[3] * 0.01) if focus else 0.08, location=g2b(p))
    bpy.context.object.data.materials.append(ylw)

mn = Vector((1e9, 1e9, 1e9))
mx = -mn
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.name != "gaps":
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
ctr = (mn + mx) / 2
rad = (mx - mn).length / 2
if focus:
    ctr, rad = g2b(focus[:3]), focus[3]
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1100, 800
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.08, 0.09, 0.12, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sc.world = world
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.rotation_euler = (0.7, 0.2, 0.5)
sun.data.energy = 4.0
sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.clip_start = 0.01
sc.collection.objects.link(cam)
sc.camera = cam
for k, (az, el) in enumerate(views):
    a, e = math.radians(az), math.radians(el)
    d = rad * 2.4
    cam.location = ctr + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * d
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = "%s_%d.png" % (out, k)
    bpy.ops.render.render(write_still=True)
print("RENDERED", rid, len(views))
