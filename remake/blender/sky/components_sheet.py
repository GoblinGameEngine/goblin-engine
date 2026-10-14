"""components_sheet.py -- every sky component family and variant laid out, exported and rendered (contact sheets).

  flatpak run org.blender.Blender -b --factory-startup --python <abs>/remake/blender/sky/components_sheet.py -- OUT_DIR [PAGE ...]

Writes OUT_DIR/components_<page>.png (and OUT_DIR/components_sheet.glb: every page's pieces, for check_models).
Pages: facade, mass, utility, signs, panels, ceilings.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BL = os.path.dirname(HERE)
sys.path.insert(0, BL)
sys.path.insert(0, os.path.join(BL, "gen"))
os.environ["SSC_KIT"] = "0"

import gblib  # noqa: E402
import sky_components as SC  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else os.path.join(BL, "..", "..", "research", "sky_islands", "img")
PAGES = argv[1:] or ["facade", "mass", "utility", "signs", "panels", "ceilings"]

WALL_FAMS = {"opening", "lattice", "oriel", "balcony", "eave", "awning", "bracket", "band", "sign", "lamp", "lights",
             "shopfront", "gable", "parapet"}

ROWS = {
    "facade": [("opening", None), ("lattice", None), ("oriel", None), ("balcony", None), ("eave", None),
               ("awning", None), ("parapet", None), ("band", None)],
    "mass": [("dome", None), ("chhatri", ["onion", "hemi"]), ("tower", None), ("gable", None), ("roofpiece", None)],
    "utility": [("stair", None), ("ladder", ["ladder"]), ("bridge", None), ("clutter", None), ("column", None),
                ("cell", None), ("court", None)],
    "signs": [("sign", None), ("lamp", None), ("lights", None), ("shopfront", None)],
}
PANEL_STYLES = ["qamariya_towers", "roshan_quarter", "riad_terraces", "pueblo_blanco", "haveli_bazaar", "chawl_galleries",
                "kowloon_warren", "zakkyo_signstacks", "machiya_lattice", "closes_lands", "hoist_gables", "cerro_tin",
                "plex_spirals", "marine_deco", "ghardaia_cascade", "bathhouse_tiers"]
PANEL_KINDS = ["plain", "window", "window_pair", "screen", "door", "arch", "balcony", "bay_box", "shopfront"]


def label(text, at, size=0.5):
    cu = bpy.data.curves.new("lbl", "FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new("lbl_" + text, cu)
    ob.location = at
    ob.rotation_euler = (math.radians(90), 0, math.radians(180))
    mat = bpy.data.materials.get("lblmat") or bpy.data.materials.new("lblmat")
    mat.diffuse_color = (0.05, 0.05, 0.05, 1)
    cu.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)


def build_page(b, page):
    """lays the page out along +X rows (one row per family) stepping back in -Z; returns the bounds"""
    import skycomp
    z_row = 0.0
    tris_rows = []
    if page in ROWS:
        for fam, only in ROWS[page]:
            variants = only or skycomp.VARIANTS.get(fam) or [None]
            w0, h0, d0 = skycomp.FAMILY_DEFAULT[fam]
            x = 0.0
            row_h = 0.0
            for v in variants:
                w, h, d = w0, h0, d0
                if fam == "tower":
                    h = 10.0
                if fam == "ceiling_module":
                    continue
                cid = fam
                fr = Matrix.Translation((x + w / 2, 0.0, z_row + 1.0))
                if fam in WALL_FAMS:
                    k = b.mat("sheet_wall", color=(0.55, 0.55, 0.57))
                    p = b.part("sheet_walls_" + fam)
                    if fam == "parapet":
                        p.box((x - 0.1, -0.6, z_row + 0.0), (x + w + 0.1, 0.0, z_row + 1.0 - 0.004), k)
                    else:
                        p.box((x - 0.1, -0.3, z_row + 1.0 - max(1.0, h * 0.3)), (x + w + 0.1, -0.004, z_row + 1.0 + h + 0.5), k)
                try:
                    SC.place(b, "sheet_" + fam, cid, fr, size=(w, h, d), variant=v, palette="riad_terraces" if fam not in ("sign", "lights") else "kowloon_warren")
                except Exception as e:  # noqa: BLE001
                    print("SHEET FAIL", fam, v, repr(e))
                    import traceback
                    traceback.print_exc()
                label(f"{fam}:{v}", (x + w / 2, 3.0, z_row + 0.3), 0.32)
                x += w + 1.6
                row_h = max(row_h, h)
            z_row += row_h + 3.5
    elif page == "panels":
        bay, sh = 3.0, 3.2
        for si, st in enumerate(PANEL_STYLES):
            for ki, kind in enumerate(PANEL_KINDS):
                fr = Matrix.Translation((ki * (bay + 0.0), 0.0, si * (sh + 0.0)))
                try:
                    SC.panel(b, st, kind, fr, bay, sh, part="sheet_panels")
                except Exception as e:  # noqa: BLE001
                    print("PANEL FAIL", st, kind, repr(e))
                    import traceback
                    traceback.print_exc()
            label(st, (-2.6, 1.0, si * sh + 1.4), 0.35)
        for ki, kind in enumerate(PANEL_KINDS):
            label(kind, (ki * bay, 1.0, len(PANEL_STYLES) * sh + 0.4), 0.4)
    elif page == "ceilings":
        for i, v in enumerate(skycomp.CEILING_VARIANTS):
            x0 = i * 3.6
            SC.ceiling(b, "sheet_ceilings", (x0, 0.0, x0 + 3.0, 3.0), 3.0, v, palette="mudejar_brickworks")
            label(v, (x0 + 1.5, -0.5, 2.0), 0.3)


def _setup():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.8, 0.88, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    sc.world = w
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(160))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    cam.data.clip_end = 2000
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc, cam, sun


def render_objs(obs, path, below=False, res=(1800, 520)):
    sc = bpy.context.scene
    cam = sc.camera
    lo = Vector((1e9, 1e9, 1e9))
    hi = -lo
    for ob in obs:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
    if lo.x > hi.x:
        return
    ctr = (lo + hi) / 2
    size = hi - lo
    sc.render.resolution_x, sc.render.resolution_y = res
    aspect = res[0] / res[1]
    if below:
        cam.location = ctr + Vector((0, 0, -60))
        cam.rotation_euler = (math.radians(180), 0, 0)
        sc.objects["sun"].rotation_euler = (math.radians(180 - 62), 0, math.radians(30))     # (a raking light: the relief shows)
        cam.data.ortho_scale = max(size.x, size.y * aspect) * 1.08
    else:
        az, el = math.radians(-20), math.radians(14)
        dvec = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
        cam.location = ctr + dvec * 300
        cam.rotation_euler = (dvec * -1).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = max(size.x * 1.02, size.z * aspect) * 1.08
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def main():
    os.makedirs(OUT, exist_ok=True)
    for page in PAGES:
        b = gblib.Building("SKYCOMP_" + page, os.path.join(BL, "..", "textures"))
        b.lods = False
        build_page(b, page)
        tris = 0
        for p in list(b.objs.values()):
            ob = p.to_object()
            tris += sum(len(poly.vertices) - 2 for poly in ob.data.polygons)
        print("PAGE", page, "tris", tris, "anchors", len(getattr(b, "sky_anchors", [])))
        glb = os.path.join(OUT, "..", "..", "..", "reference", "tmp", "sky_components", f"sheet_{page}.glb")
        os.makedirs(os.path.dirname(glb), exist_ok=True)
        bpy.ops.object.select_all(action="SELECT")
        for ob in bpy.data.objects:
            if ob.type == "FONT":
                ob.select_set(False)
        bpy.ops.export_scene.gltf(filepath=os.path.normpath(glb), export_format="GLB", export_yup=True, use_selection=True, export_image_format="NONE")
        _setup()
        groups = {}
        for ob in bpy.data.objects:
            if ob.type != "MESH":
                continue
            key = ob.name.replace("sheet_walls_", "sheet_")
            groups.setdefault(key, []).append(ob)
        for key, obs in sorted(groups.items()):
            render_objs(obs, os.path.join(OUT, "rows", f"components_{page}_{key}.png"), below=page == "ceilings",
                        res=(1800, 1100) if page == "panels" else (1800, 520))


main()
