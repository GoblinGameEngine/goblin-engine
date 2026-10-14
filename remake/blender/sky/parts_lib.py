"""parts_lib.py -- the sky-island parts' small geometry kit (Blender side).

Everything is written in the GAME's frame (Godot: +Y up, +Z out of the island at a dock face, +X across) and
converted to Blender's Z-up frame only when the objects are made (Blender (x, y, z) = game (x, -z, y); the glTF
exporter's +Y-up option turns it back).  A part is a tree of nodes; each node has a local transform (its pose at
deploy 0, for bridges) and a mesh in its own local frame.  Every primitive is a closed shell (boxes, capped tubes),
wound outward, so the house checks (manifold, winding) hold; curved shells are smooth-shaded, boxes flat.

Materials are a small shared palette (PALETTE): every part uses the same names, so the game can swap in one shared
material per name (parts.json lists it) -- no images in any glb.
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector

# name: (rgb, roughness, metallic)
PALETTE = {
    "sky_timber": ((0.47, 0.33, 0.20), 0.85, 0.0),
    "sky_timber_dark": ((0.30, 0.20, 0.12), 0.85, 0.0),
    "sky_plank": ((0.60, 0.46, 0.30), 0.9, 0.0),
    "sky_iron": ((0.22, 0.24, 0.27), 0.55, 0.6),
    "sky_iron_red": ((0.50, 0.17, 0.12), 0.6, 0.4),
    "sky_steel": ((0.55, 0.58, 0.60), 0.45, 0.7),
    "sky_paint_teal": ((0.18, 0.45, 0.45), 0.6, 0.1),
    "sky_paint_yellow": ((0.85, 0.66, 0.15), 0.6, 0.1),
    "sky_paint_white": ((0.86, 0.86, 0.82), 0.6, 0.0),
    "sky_stone": ((0.58, 0.55, 0.50), 0.95, 0.0),
    "sky_rope": ((0.66, 0.57, 0.40), 0.95, 0.0),
    "sky_chain": ((0.16, 0.16, 0.17), 0.5, 0.8),
    "sky_canvas": ((0.90, 0.88, 0.82), 0.8, 0.0),
    "sky_canvas_stripe": ((0.80, 0.70, 0.52), 0.8, 0.0),
    "sky_brass": ((0.70, 0.55, 0.25), 0.4, 0.8),
    "sky_net": ((0.30, 0.38, 0.36), 0.9, 0.0),
    "sky_moss": ((0.30, 0.42, 0.18), 1.0, 0.0),
    "sky_vine": ((0.22, 0.34, 0.14), 1.0, 0.0),
    "sky_leaf": ((0.33, 0.50, 0.20), 1.0, 0.0),
    "sky_crate": ((0.36, 0.42, 0.30), 0.7, 0.2),
    "sky_crate_band": ((0.80, 0.55, 0.15), 0.6, 0.3),
    "sky_pad": ((0.25, 0.27, 0.28), 0.9, 0.0),
    "sky_pad_mark": ((0.92, 0.85, 0.40), 0.8, 0.0),
    "sky_rocket": ((0.78, 0.22, 0.14), 0.5, 0.2),
}
TWO_SIDED = {"sky_moss", "sky_leaf"}           # thin cards: drawn from both sides
_mats = {}


def material(name):
    if name in _mats:
        return _mats[name]
    rgb, rough, metal = PALETTE[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1.0)                  # (workbench previews)
    m.use_backface_culling = name not in TWO_SIDED
    _mats[name] = m
    return m


def g2b(v):
    """game (x, y up, z out) -> Blender (x, -z, y)"""
    return Vector((v[0], -v[2], v[1]))


_C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))     # game -> Blender


def m_g2b(m):
    return _C @ m @ _C.inverted()


class Mesh:
    """Triangles/quads in a node's local game frame, per material, with a smooth flag per face."""

    def __init__(self):
        self.verts = []
        self.faces = []            # (indices, material, smooth)

    def _add(self, pts):
        i0 = len(self.verts)
        self.verts.extend(Vector(p) for p in pts)
        return i0

    def tris(self):
        return sum(len(f[0]) - 2 for f in self.faces)

    # ---------------------------------------------------------------- boxes
    def box(self, c0, c1, mat):
        """axis-aligned box between corners c0, c1 (game frame)"""
        x0, y0, z0 = (min(a, b) for a, b in zip(c0, c1))
        x1, y1, z1 = (max(a, b) for a, b in zip(c0, c1))
        self.obox(Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)), (x1 - x0, y1 - y0, z1 - z0), mat)

    def obox(self, m, size, mat):
        """a box of size (sx, sy, sz) placed by the 4x4 matrix m (centre + orientation)"""
        hx, hy, hz = (s / 2 for s in size)
        pts = [m @ Vector((sx * hx, sy * hy, sz * hz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        i = self._add(pts)
        # index = sx*4 + sy*2 + sz (0 = -, 1 = +); faces wound outward (counter-clockwise seen from outside)
        q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        for f in q:
            self.faces.append(([i + k for k in f], mat, False))

    def bar(self, a, b, w, h, mat, up=(0, 1, 0)):
        """a square-section beam from a to b (w across, h in the 'up' direction)"""
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        if L < 1e-6:
            return
        z = d / L
        upv = Vector(up)
        if abs(z.dot(upv)) > 0.99:
            upv = Vector((1, 0, 0))
        x = upv.cross(z).normalized()
        y = z.cross(x)
        m = Matrix((x, y, z)).transposed().to_4x4()
        m.translation = (a + b) / 2
        self.obox(m, (w, h, L), mat)

    # ---------------------------------------------------------------- round things
    def tube(self, a, b, r, mat, seg=8, r1=None, caps=True, smooth=True):
        """a capped cylinder (or cone frustum, r1 at b) from a to b"""
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        if L < 1e-6:
            return
        z = d / L
        t = Vector((1, 0, 0)) if abs(z.x) < 0.9 else Vector((0, 1, 0))
        x = t.cross(z).normalized()
        y = z.cross(x)
        r1 = r if r1 is None else r1
        ring0 = [a + (x * math.cos(2 * math.pi * k / seg) + y * math.sin(2 * math.pi * k / seg)) * r for k in range(seg)]
        ring1 = [b + (x * math.cos(2 * math.pi * k / seg) + y * math.sin(2 * math.pi * k / seg)) * r1 for k in range(seg)]
        i = self._add(ring0 + ring1)
        for k in range(seg):
            k1 = (k + 1) % seg
            self.faces.append(([i + k, i + k1, i + seg + k1, i + seg + k], mat, smooth))
        if caps:
            self.faces.append(([i + k for k in reversed(range(seg))], mat, False))
            self.faces.append(([i + seg + k for k in range(seg)], mat, False))

    def lathe(self, profile, mat, seg=16, axis_m=None, smooth=True):
        """a closed solid of revolution about local +Y: profile [(r, y), ...] from the bottom pole (r 0) to the top
        pole (r 0) -- poles collapse to single vertices so the shell is closed"""
        m = axis_m or Matrix.Identity(4)
        rings = []
        for r, y in profile:
            if r <= 1e-6:
                rings.append([self._add([m @ Vector((0, y, 0))])])
            else:
                pts = [m @ Vector((r * math.cos(2 * math.pi * k / seg), y, -r * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
                i = self._add(pts)
                rings.append([i + k for k in range(seg)])
        for ra, rb in zip(rings, rings[1:]):
            for k in range(seg):
                k1 = (k + 1) % seg
                mk = mat(k) if callable(mat) else mat
                if len(ra) == 1 and len(rb) == 1:
                    continue
                if len(ra) == 1:
                    self.faces.append(([ra[0], rb[k1], rb[k]][::-1], mk, smooth))
                elif len(rb) == 1:
                    self.faces.append(([ra[k], ra[k1], rb[0]][::-1], mk, smooth))
                else:
                    self.faces.append(([ra[k], ra[k1], rb[k1], rb[k]][::-1], mk, smooth))
        if len(rings[0]) > 1:
            self.faces.append(([k for k in rings[0]], mat if not callable(mat) else mat(0), False))
        if len(rings[-1]) > 1:
            self.faces.append(([k for k in reversed(rings[-1])], mat if not callable(mat) else mat(0), False))

    def prism(self, poly, y0, y1, mat, m=None):
        """a vertical prism: polygon [(x, z), ...] (counter-clockwise seen from above, +Y) extruded from y0 to y1"""
        m = m or Matrix.Identity(4)
        n = len(poly)
        bot = [m @ Vector((x, y0, z)) for x, z in poly]
        top = [m @ Vector((x, y1, z)) for x, z in poly]
        i = self._add(bot + top)
        # seen from +Y with x right and z DOWN the screen, game CCW about +Y is (x, -z) CCW: wind accordingly
        self.faces.append(([i + n + k for k in range(n)], mat, False))
        self.faces.append(([i + k for k in reversed(range(n))], mat, False))
        for k in range(n):
            k1 = (k + 1) % n
            self.faces.append(([i + k, i + k1, i + n + k1, i + n + k], mat, False))

    def slab(self, poly, t, mat, m):
        """a thin plate: polygon [(u, v), ...] in the plane of m's local X/Y, thickness t along local Z"""
        n = len(poly)
        a = [m @ Vector((u, v, -t / 2)) for u, v in poly]
        b = [m @ Vector((u, v, t / 2)) for u, v in poly]
        i = self._add(a + b)
        self.faces.append(([i + n + k for k in range(n)], mat, False))
        self.faces.append(([i + k for k in reversed(range(n))], mat, False))
        for k in range(n):
            k1 = (k + 1) % n
            self.faces.append(([i + k, i + k1, i + n + k1, i + n + k][::-1], mat, False))


class Node:
    def __init__(self, name, parent=None, xf=None):
        self.name = name
        self.parent = parent
        self.xf = xf if xf is not None else Matrix.Identity(4)     # local, game frame
        self.mesh = Mesh()
        self.children = []
        if parent:
            parent.children.append(self)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def world(self):
        return self.xf if self.parent is None else self.parent.world() @ self.xf


def fix_winding(me):
    """flip any face whose normal points into its own closed shell (cheap safety net for hand-wound faces)"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def realise(root, coll=None):
    """make the Blender objects for a node tree; returns {name: object}"""
    coll = coll or bpy.context.scene.collection
    objs = {}
    for n in root.walk():
        mesh = n.mesh
        if mesh.faces:
            me = bpy.data.meshes.new(n.name)
            mats = []
            for _, m, _ in mesh.faces:
                if m not in mats:
                    mats.append(m)
            me.from_pydata([g2b(v) for v in mesh.verts], [], [f[0] for f in mesh.faces])
            for m in mats:
                me.materials.append(material(m))
            for poly, f in zip(me.polygons, mesh.faces):
                poly.material_index = mats.index(f[1])
                poly.use_smooth = f[2]
            me.validate()
            fix_winding(me)
            me.update()
            ob = bpy.data.objects.new(n.name, me)
        else:
            ob = bpy.data.objects.new(n.name, None)
            ob.empty_display_size = 0.3
        coll.objects.link(ob)
        if n.parent is not None:
            ob.parent = objs[n.parent.name]
            ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = m_g2b(n.xf)
        objs[n.name] = ob
    return objs


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()


def export_glb(path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_apply=True,
                              export_image_format="NONE", export_animations=False)


def tri_count(root):
    return sum(n.mesh.tris() for n in root.walk())


# ---------------------------------------------------------------- transforms (game frame)
def T(x, y, z):
    return Matrix.Translation((x, y, z))


def Rx(deg):
    return Matrix.Rotation(math.radians(deg), 4, "X")


def Ry(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Y")


def Rz(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def xf_json(m):
    loc, rot, scl = m.decompose()
    return {"pos": [round(v, 4) for v in loc], "rot": [round(rot.x, 5), round(rot.y, 5), round(rot.z, 5), round(rot.w, 5)],
            "scl": [round(v, 4) for v in scl]}


# ---------------------------------------------------------------- renders
def render_setup(bg=(0.62, 0.70, 0.78)):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_shadows = True
    sc.display.shading.show_cavity = True
    sc.display.shading.show_object_outline = True
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    world.color = bg
    sc.world = world
    sc.display.shading.background_type = "WORLD"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def render(path, cam, target_g, loc_g, w=900, h=600, lens=35):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    cam.data.lens = lens
    cam.data.clip_end = 5000
    tgt, loc = g2b(target_g), g2b(loc_g)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
