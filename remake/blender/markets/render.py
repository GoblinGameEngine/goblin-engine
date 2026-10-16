"""render.py -- the market kit's contact sheets (Blender), lit like the game: a low sun with shadows, slot materials
(glass glossy, metal metallic, emissive glowing at night, canvas glowing through, atlas cards alpha-cut), Freestyle
outlines, each piece labelled with its id:

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/render.py -- OUT_PNG GLB [night] [W H] [az el]
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out, glb = argv[0], argv[1]
night = len(argv) > 2 and argv[2] == "night"
W, H = (int(argv[3]), int(argv[4])) if len(argv) > 4 else (1800, 1100)
AZ, EL = (float(argv[5]), float(argv[6])) if len(argv) > 6 else (-24.0, 26.0)
bpy.ops.wm.read_factory_settings(use_empty=True)
for g in glb.split(";"):
    bpy.ops.import_scene.gltf(filepath=g)
sc = bpy.context.scene
names = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in names else "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.view_settings.view_transform = "Standard"
try:
    sc.eevee.use_shadows = True
except AttributeError:
    pass
EMI = {"bulb", "bulb_a", "bulb_b", "bulb_c", "bulb_d", "neon", "neon_b", "lamp", "warn", "emissive"}
GLOW = {"glow", "glow_b"}
CANVAS = {"canvas_a", "canvas_b", "canvas_c", "lining"}
TEX = {"sign", "mascot", "stall", "goods", "text"}

for mat in list(bpy.data.materials):
    slot = mat.name.replace("mk_", "").replace("wk_", "").split(".")[0]
    mat.use_nodes = True
    nt = mat.node_tree
    img = emit_img = None
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image is not None:
            if "emit" in n.image.name:
                emit_img = n.image
            else:
                img = n.image
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    nt.links.new(bs.outputs[0], o.inputs[0])
    bs.inputs["Roughness"].default_value = 0.85
    if slot in TEX and img is not None:
        ti = nt.nodes.new("ShaderNodeTexImage")
        ti.image = img
        ti.interpolation = "Closest" if False else "Linear"
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs["Factor"].default_value = 1.0
        nt.links.new(ti.outputs["Color"], mul.inputs[6])
        nt.links.new(ca.outputs["Color"], mul.inputs[7])
        nt.links.new(mul.outputs[2], bs.inputs["Base Color"])
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        nt.links.new(ti.outputs["Alpha"], gt.inputs[0])
        nt.links.new(gt.outputs[0], bs.inputs["Alpha"])
        try:
            mat.surface_render_method = "DITHERED"
        except AttributeError:
            mat.blend_method = "CLIP"
        if night and emit_img is not None:
            te = nt.nodes.new("ShaderNodeTexImage")
            te.image = emit_img
            m2 = nt.nodes.new("ShaderNodeMix")
            m2.data_type = "RGBA"
            m2.blend_type = "MULTIPLY"
            m2.inputs["Factor"].default_value = 1.0
            nt.links.new(te.outputs["Color"], m2.inputs[6])
            nt.links.new(ti.outputs["Color"], m2.inputs[7])
            nt.links.new(m2.outputs[2], bs.inputs["Emission Color"])
            bs.inputs["Emission Strength"].default_value = 2.0
        mat.use_backface_culling = True
        continue
    nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
    if slot == "glass":
        bs.inputs["Roughness"].default_value = 0.12
        bs.inputs["Metallic"].default_value = 0.35
    elif slot in ("metal", "steel", "brass"):
        bs.inputs["Metallic"].default_value = 0.55
        bs.inputs["Roughness"].default_value = 0.45
    elif slot in EMI:
        nt.links.new(ca.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = 6.0 if night else 0.3
    elif slot in GLOW:
        nt.links.new(ca.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = 2.2 if night else 0.15
    elif slot in CANVAS and night:
        nt.links.new(ca.outputs["Color"], bs.inputs["Emission Color"])
        bs.inputs["Emission Strength"].default_value = 0.35

w = bpy.data.worlds.new("w")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.03, 0.04, 0.08, 1) if night else (0.55, 0.68, 0.88, 1)
bg.inputs[1].default_value = 0.2 if night else 0.75
sc.world = w
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 0.25 if night else 4.0
sun.data.angle = math.radians(2)
sun.rotation_euler = (math.radians(52), 0, math.radians(-38))
sc.collection.objects.link(sun)

meshes = [ob for ob in sc.objects if ob.type == "MESH"]
lo = Vector((1e9, 1e9, 1e9))
hi = -lo
label_size = 0.0
for ob in meshes:
    blo = Vector((1e9, 1e9, 1e9))
    bhi = -blo
    for c in ob.bound_box:
        p = ob.matrix_world @ Vector(c)
        blo = Vector(map(min, blo, p))
        bhi = Vector(map(max, bhi, p))
    lo = Vector(map(min, lo, blo))
    hi = Vector(map(max, hi, bhi))
ext0 = hi - lo
size = max(0.12, min(1.2, max(ext0.x, ext0.z) / 48.0))
for ob in meshes:
    blo = Vector((1e9, 1e9, 1e9))
    bhi = -blo
    for c in ob.bound_box:
        p = ob.matrix_world @ Vector(c)
        blo = Vector(map(min, blo, p))
        bhi = Vector(map(max, bhi, p))
    cu = bpy.data.curves.new(ob.name + "_lbl", "FONT")
    cu.body = ob.name.split(".")[0]
    cu.size = size
    cu.align_x = "CENTER"
    tx = bpy.data.objects.new(ob.name + "_lbl", cu)
    tx.location = ((blo.x + bhi.x) / 2, blo.y - size * 1.4, 0.02)
    sc.collection.objects.link(tx)
    tm = bpy.data.materials.new("lbl")
    tm.use_nodes = True
    pb = tm.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1)
    if night:
        pb.inputs["Emission Color"].default_value = (0.9, 0.9, 0.9, 1)
        pb.inputs["Emission Strength"].default_value = 1.0
    cu.materials.append(tm)
lo.y -= size * 2.5

pl = bpy.data.meshes.new("ground")
g0, g1 = lo - Vector((4, 4, 0)), hi + Vector((4, 4, 0))
pl.from_pydata([(g0.x, g0.y, -0.01), (g1.x, g0.y, -0.01), (g1.x, g1.y, -0.01), (g0.x, g1.y, -0.01)], [], [(0, 1, 2, 3)])
gob = bpy.data.objects.new("ground", pl)
gm = bpy.data.materials.new("ground")
gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.06, 0.07, 1) if night else (0.5, 0.5, 0.48, 1)
pl.materials.append(gm)
sc.collection.objects.link(gob)

sc.render.use_freestyle = True
sc.render.line_thickness_mode = "ABSOLUTE"
sc.render.line_thickness = 0.9
vl = sc.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
fs.crease_angle = math.radians(140)
ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("lines")
ls.select_by_visibility = True
ls.select_silhouette = ls.select_border = ls.select_crease = True
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("ink")
ls.linestyle.color = (0.08, 0.06, 0.05)
ls.linestyle.thickness = 0.9
ls.linestyle.chaining = "PLAIN"
ls.linestyle.use_same_object = True

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 5000
ctr = (lo + hi) / 2
ext = hi - lo
az, el = math.radians(AZ), math.radians(EL)
d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
cam.data.type = "ORTHO"
cam.location = ctr + d * (ext.length + 30)
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()
inv = cam.matrix_world.inverted()
pts = [inv @ (ob.matrix_world @ Vector(c)) for ob in meshes for c in ob.bound_box]
pts += [inv @ Vector((lo.x, lo.y, 0.0)), inv @ Vector((hi.x, lo.y, 0.0))]
x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
aspect = sc.render.resolution_x / sc.render.resolution_y
cam.data.ortho_scale = max(x1 - x0, (y1 - y0) * aspect) * 1.03
cam.location = cam.matrix_world @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0.0))
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
