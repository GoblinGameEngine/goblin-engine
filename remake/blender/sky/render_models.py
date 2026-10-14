"""render_models.py -- previews of the sky islands' building models with their real materials (the generator stream's;
render_glb.py shows untextured glbs).

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render_models.py -- OUT_PREFIX GLB [GLB...] -- VIEW...

Each glb's materials are rebuilt from its <ID>.mats.json (the shared library textures, tinted, or plain colours;
emissive ones glow).  Several glbs: laid out in a row along x, GAP m apart, so a style's models show side by side.
VIEW = "<az_deg>:<elev_deg>:<dist>[:ortho_scale]" about the bounds' centre (az 0 looks from -Y toward +Y: the backs;
az 180 the fronts).  Build the models with SSC_KIT=0 first: kitted pieces live in the shared kit, not in the glb.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "textures", "lib")
GAP = 6.0

argv = sys.argv[sys.argv.index("--") + 1:]
out = argv[0]
rest = argv[1:]
cut = rest.index("--")
glbs, views = rest[:cut], rest[cut + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
_imgs = {}


def _img(tex):
    if tex not in _imgs:
        p = os.path.join(LIB, os.path.basename(tex) + "_albedo.png")
        _imgs[tex] = bpy.data.images.load(p) if os.path.exists(p) else None
    return _imgs[tex]


def dress(mat, d):
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    bsdf.inputs["Roughness"].default_value = d.get("rough", 0.6)
    bsdf.inputs["Metallic"].default_value = d.get("metal", 0.0)
    if d.get("tex") and _img(d["tex"]) is not None:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = _img(d["tex"])
        if d.get("tint"):
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = 1.0
            nt.links.new(tn.outputs["Color"], mix.inputs[6])
            mix.inputs[7].default_value = (*[(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in d["tint"]], 1.0)
            nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
        else:
            nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
    elif d.get("color"):
        bsdf.inputs["Base Color"].default_value = (*d["color"], 1.0)
    if d.get("emission"):
        bsdf.inputs["Emission Color"].default_value = (*d["emission"], 1.0)
        bsdf.inputs["Emission Strength"].default_value = 3.0
    if d.get("alpha") is not None and d["alpha"] < 0.9:
        bsdf.inputs["Base Color"].default_value = (0.08, 0.1, 0.12, 1.0)


x = 0.0
for gp in glbs:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=gp)
    new = [o for o in bpy.data.objects if o not in before]
    side = os.path.splitext(gp)[0] + ".mats.json"
    defs = json.load(open(side)) if os.path.exists(side) else {}
    for ob in new:
        if "-colonly" in ob.name:
            ob.hide_render = True
        if ob.type == "MESH":
            for slot in ob.material_slots:
                m = slot.material
                if m and m.name.split(".")[0] in defs and not m.get("_dressed"):
                    dress(m, defs[m.name.split(".")[0]])
                    m["_dressed"] = 1
    lo = min((ob.matrix_world @ Vector(c)).x for ob in new if ob.type == "MESH" for c in ob.bound_box)
    hi = max((ob.matrix_world @ Vector(c)).x for ob in new if ob.type == "MESH" for c in ob.bound_box)
    for ob in new:
        if ob.parent is None:
            ob.location.x += x - lo
    x += (hi - lo) + GAP
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.74, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.2
sun.rotation_euler = (math.radians(55), 0, math.radians(200))
sc.collection.objects.link(sun)
bpy.context.view_layer.update()
lo = Vector((1e9, 1e9, 1e9))
hi = -lo
for ob in sc.objects:
    if ob.type == "MESH" and not ob.hide_render:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
ctr = (lo + hi) / 2
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 20000
for i, v in enumerate(views):
    f = [float(t) for t in v.split(":")]
    az, el, dist = math.radians(f[0]), math.radians(f[1]), f[2]
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = ctr + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    if len(f) > 3 and f[3] > 0:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = f[3]
    else:
        cam.data.type = "PERSP"
    sc.render.filepath = f"{out}_{i}.png"
    bpy.ops.render.render(write_still=True)
