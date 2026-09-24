"""
gblod.py -- distance versions (LOD1..3) of a finished Building, exported beside its glb.

  <ID>.lod1.glb   60-200 m   the exterior as built, minus everything small or inside: no interior,
                             text, window sashes, door hardware or yard props; doors become boxes,
                             shutters and porch spindles their hulls, glass an opaque dark pane.
                             At most 3 textured materials survive (the biggest by area: walls, roof,
                             foundation); everything else goes to one vertex-coloured material.
  <ID>.lod2.glb  200-600 m   massing: each gbhouse block as a solid box to its wall top, each roof
                             part as its convex hull (closes gable ends), and every other exterior
                             piece as the hull of its mesh islands, thin members (posts, rails,
                             pickets) dropped.  One vertex-coloured material.
  <ID>.lod3.glb     600 m+   LOD2 with only the big pieces (blocks, roofs, towers, bins, spans);
                             merged per settlement at load time.

Vertex colours are each source material's mean albedo (its texture's average times the tint, or
its plain colour), so every LOD2/3 building shares one material and merges into one draw call.
The rules key off part names (see KEEP/DROP below); generators that build with gbhouse register
their blocks in Building.massing so LOD2/3 walls are solid, without window/door holes.
"""
import math
import os
import re

import bmesh
import bpy
import numpy as np
from mathutils import Vector

LOD_MAT = "LOD_VC"
GLASS_RGB = (0.09, 0.105, 0.12)            # opaque pane: about what sky-reflecting glass averages to (linear)

# parts that never appear beyond full detail: the interior, text, sashes, hardware, small yard props
DROP = re.compile(r"^(furn_|fit_|partitions|floor_finish|floors|stair|well_rails|stair_rail|thresholds|sign_|mailbox|"
                  r"ladder|barn_fittings|doorframe|windows|dormer_windows|walk|driveway|sidewalk|alley|parking|"
                  r"front_fence|chainlink|hedge|yard_|car|plate|namesign|extrasign|boards|light_|awning_rod)")
# kept at LOD1 as the hulls of their islands (louvred shutters, spindles, brackets)
HULL1 = re.compile(r"^(trim|porch_|door_)")
# LOD2/3: lattices (a truss is its members): LOD2 keeps the members, LOD3 an outline frame
LATTICE = re.compile(r"^(truss)")
# LOD3: landmark parts that survive whatever their size
LANDMARK = re.compile(r"^(tower|cupola|elevator|silo|spire|belfry|roof_tower|bins|stack|tank)")


def _base(name):
    return re.sub(r"(\.\d+)+$", "", name)


# ---------------------------------------------------------------- colours
_mean_cache = {}


def _srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat_rgb(b, mat):
    """Linear mean albedo of a Blender material made by Building.mat()."""
    if mat is None:
        return (0.5, 0.5, 0.5)
    if mat.name in _mean_cache:
        return _mean_cache[mat.name]
    d = b.mat_defs.get(mat.name, {})
    if d.get("alpha") is not None and d["alpha"] < 0.9:
        rgb = GLASS_RGB
    elif d.get("tex"):
        img = next((n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image
                    and n.image.name.endswith("_albedo.png")), None)
        rgb = (0.5, 0.5, 0.5)
        if img is not None:
            px = np.empty(len(img.pixels), dtype=np.float32)
            img.pixels.foreach_get(px)
            m = px.reshape(-1, 4)[::7, :3].mean(axis=0)            # sampled mean of the stored (sRGB) values
            rgb = tuple(_srgb_to_lin(float(c)) for c in m)
        if d.get("tint"):
            rgb = tuple(c * _srgb_to_lin(t) for c, t in zip(rgb, d["tint"]))
    else:
        rgb = tuple(d.get("color") or (0.5, 0.5, 0.5))
    _mean_cache[mat.name] = rgb
    return rgb


# ---------------------------------------------------------------- mesh helpers
def _islands(bm):
    """Face islands of a bmesh (lists of faces sharing edges)."""
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, isl = [f], []
        seen.add(f.index)
        while stack:
            g = stack.pop()
            isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        stack.append(h)
        out.append(isl)
    return out


def _world_bm(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bm.faces.ensure_lookup_table()
    for i, f in enumerate(bm.faces):
        f.index = i
    return bm


def _dominant_mat(ob, faces):
    area = {}
    for f in faces:
        area[f.material_index] = area.get(f.material_index, 0.0) + f.calc_area()
    mi = max(area, key=area.get) if area else 0
    return ob.data.materials[mi] if mi < len(ob.data.materials) else None


class Out:
    """Accumulates triangles with a per-face linear RGB colour; builds one mesh object."""

    def __init__(self):
        self.verts, self.faces, self.cols = [], [], []

    def add_poly(self, pts, rgb):
        base = len(self.verts)
        self.verts += [tuple(p) for p in pts]
        self.faces.append(tuple(range(base, base + len(pts))))
        self.cols.append(rgb)

    def add_hull(self, pts, rgb, upright_rgb=None):
        if len(pts) < 4:
            return
        bm = bmesh.new()
        for p in pts:
            bm.verts.new(p)
        try:
            res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
            for v in res.get("geom_interior", []) + res.get("geom_unused", []):
                if isinstance(v, bmesh.types.BMVert) and v.is_valid:
                    bm.verts.remove(v)
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
        except Exception:
            bm.free()
            return
        for f in bm.faces:
            self.add_poly([v.co.copy() for v in f.verts], upright_rgb if upright_rgb and abs(f.normal.z) < 0.2 else rgb)
        bm.free()

    def add_ribbon(self, a, c, n, w, rgb):
        """A flat strip w wide from a to c, lying in the plane with normal n (both sides)."""
        d = (c - a).normalized()
        off = n.cross(d).normalized() * (w / 2)
        q = [a - off, c - off, c + off, a + off]
        self.add_poly(q, rgb)
        self.add_poly(list(reversed(q)), rgb)

    def add_box(self, lo, hi, rgb):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        c = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.add_poly([c[i] for i in q], rgb)

    def to_object(self, name):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
        for poly, rgb in zip(me.polygons, self.cols):
            for li in poly.loop_indices:
                attr.data[li].color = (*rgb, 1.0)
        mat = bpy.data.materials.get(LOD_MAT) or bpy.data.materials.new(LOD_MAT)
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


# ---------------------------------------------------------------- the three versions
def _lod1(b, objs, name):
    """Exterior as built: drop DROP parts, hull HULL1 islands, collapse materials."""
    # the textured materials that stay textured: the three biggest by area among kept parts
    area = {}
    for ob in objs:
        if DROP.match(_base(ob.name)) or HULL1.match(_base(ob.name)):
            continue
        for poly in ob.data.polygons:
            m = ob.data.materials[poly.material_index] if poly.material_index < len(ob.data.materials) else None
            if m is not None and b.mat_defs.get(m.name, {}).get("tex"):
                area[m.name] = area.get(m.name, 0.0) + poly.area
    keep_tex = set(sorted(area, key=area.get, reverse=True)[:3])
    vc = Out()
    parts = []
    for ob in objs:
        base = _base(ob.name)
        if DROP.match(base):
            # a dropped part's big panes stay (storefront display glass lives in "windows"): without
            # them the opening shows the emptied interior
            for poly in ob.data.polygons:
                m = ob.data.materials[poly.material_index] if poly.material_index < len(ob.data.materials) else None
                if m is not None and mat_rgb(b, m) == GLASS_RGB and poly.area > 0.3:
                    vc.add_poly([ob.matrix_world @ ob.data.vertices[i].co for i in poly.vertices], GLASS_RGB)
            continue
        if HULL1.match(base):
            bm = _world_bm(ob)
            for isl in _islands(bm):
                pts = [v.co.copy() for f in isl for v in f.verts]
                xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
                if sorted((max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))[1] < 0.07:
                    continue                            # spindles, knobs, hinges: sub-pixel beyond 60 m
                vc.add_hull(pts, mat_rgb(b, _dominant_mat(ob, isl)))
            bm.free()
            continue
        # copy as built; faces in collapsed materials move to the vertex-colour mesh
        bm = _world_bm(ob)
        tex_faces = [f for f in bm.faces if f.material_index < len(ob.data.materials)
                     and ob.data.materials[f.material_index] is not None
                     and ob.data.materials[f.material_index].name in keep_tex]
        tex_set = set(tex_faces)
        for f in bm.faces:
            if f in tex_set:
                continue
            m = ob.data.materials[f.material_index] if f.material_index < len(ob.data.materials) else None
            vc.add_poly([v.co.copy() for v in f.verts], mat_rgb(b, m))
        if tex_faces:
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f not in tex_set], context="FACES")
            me = bpy.data.meshes.new(name + "_" + base)
            bm.to_mesh(me)
            for m in ob.data.materials:
                me.materials.append(m)
            nob = bpy.data.objects.new(name + "_" + base, me)
            bpy.context.scene.collection.objects.link(nob)
            parts.append(nob)
        bm.free()
    parts.append(vc.to_object(name + "_vc"))
    return _join(parts, name)


def _massing(b, objs, name, lod):
    """LOD2 (lod=2) / LOD3 (lod=3): gbhouse blocks as solid boxes, roofs as hulls, the rest as
    island hulls; thin and (for LOD3) small pieces dropped."""
    out = Out()
    thin = 0.35 if lod == 2 else 0.8
    small = 0.0 if lod == 2 else 3.0
    # the walls' colour, darkened by their share of window glass (solid massing has no windows, so
    # without this a building visibly brightens when it switches to LOD2)
    shell_rgb, wall_area, glass_area = None, 0.0, 0.0
    for ob in objs:
        base = _base(ob.name)
        if base.startswith("shell"):
            bm = _world_bm(ob)
            shell_rgb = mat_rgb(b, _dominant_mat(ob, bm.faces))
            wall_area += sum(f.calc_area() for f in bm.faces if abs(f.normal.z) < 0.3) / 2    # inside + outside faces
            bm.free()
        elif base.startswith("glass") or base.endswith("_glass"):
            glass_area += sum(p_.area for p_ in ob.data.polygons) / 2
    glass_k = min(0.5, glass_area / max(1.0, wall_area + glass_area))

    def walls(rgb):
        return tuple(c * (1 - glass_k) + g_ * glass_k for c, g_ in zip(rgb, GLASS_RGB))
    for blk in getattr(b, "massing", []):
        x0, y0, x1, y1 = blk["rect"]
        rgb = mat_rgb(b, b.mats.get(blk["mat"])) if blk.get("mat") in b.mats else (shell_rgb or (0.5, 0.5, 0.5))
        out.add_box((x0, y0, blk.get("z0", -0.5)), (x1, y1, blk["top"]), walls(rgb))
    have_blocks = bool(getattr(b, "massing", []))
    for ob in objs:
        base = _base(ob.name)
        if DROP.match(base) or base.startswith("glass") or base.endswith("_glass") or base.startswith("door_"):
            continue
        if have_blocks and (base.startswith("shell") or base.startswith("trim")):
            continue                                   # the solid blocks stand in for the walls
        bm = _world_bm(ob)
        if base.startswith("roof"):
            # the whole roof part as one hull: a closed prism / hip / slab, gable ends included
            pts = [v.co.copy() for v in bm.verts]
            span = (max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))
            if lod == 2 or max(span) >= small or LANDMARK.match(base):
                # sloped faces in the roof's colour, upright ones (gable ends, parapets) in the walls'
                out.add_hull(pts, mat_rgb(b, _dominant_mat(ob, bm.faces)), upright_rgb=walls(shell_rgb) if shell_rgb else None)
            bm.free()
            continue
        if LATTICE.match(base):
            rgb = mat_rgb(b, _dominant_mat(ob, bm.faces))
            if lod == 2:
                # the members themselves (hulls would fill every X-brace into a panel), gussets dropped
                for isl in _islands(bm):
                    pts = [v.co for f in isl for v in f.verts]
                    if max(max(p[k] for p in pts) - min(p[k] for p in pts) for k in range(3)) >= 1.0:
                        for f in isl:
                            out.add_poly([v.co.copy() for v in f.verts], rgb)
            else:
                # the truss's outline: the upright faces of its hull (two side walls and the portals)
                hb = bmesh.new()
                for v in bm.verts:
                    hb.verts.new(v.co)
                bmesh.ops.convex_hull(hb, input=hb.verts[:])
                bmesh.ops.dissolve_limit(hb, angle_limit=math.radians(1.0), verts=hb.verts[:], edges=hb.edges[:])
                # as a frame: ~1 px ribbons (1.2 m at 600 m) along the edges of its upright hull faces
                # -- a filled panel reads far heavier than the open lattice it replaces
                for f in hb.faces:
                    if abs(f.normal.z) < 0.3:
                        for e in f.edges:
                            out.add_ribbon(e.verts[0].co.copy(), e.verts[1].co.copy(), f.normal.copy(), 1.2, rgb)
                hb.free()
            bm.free()
            continue
        for isl in _islands(bm):
            pts = [v.co.copy() for f in isl for v in f.verts]
            xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
            dims = sorted((max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))
            if dims[1] < thin:                      # posts, rails, pickets, pipes: two thin dimensions
                continue
            if dims[2] < small and not LANDMARK.match(base):
                continue
            out.add_hull(pts, mat_rgb(b, _dominant_mat(ob, isl)))
        bm.free()
    return out.to_object(name)


def _join(objs, name):
    objs = [o for o in objs if o is not None]
    if not objs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[-1]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    return ob


def export_lods(b, out_glb):
    """Build LOD1..3 from the finished parts (objects, before merge) and export each beside out_glb.
    Returns {lod: triangle count}."""
    src = [o for o in bpy.data.objects if o.type == "MESH" and "colonly" not in o.name and o.data.polygons]
    stem = os.path.splitext(out_glb)[0]
    rid = os.path.basename(stem)
    counts = {}
    for lod in (1, 2, 3):
        name = f"{rid}_lod{lod}"
        ob = _lod1(b, src, name) if lod == 1 else _massing(b, src, name, lod)
        if ob is None:
            continue
        me = ob.data
        me.calc_loop_triangles()
        counts[lod] = len(me.loop_triangles)
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.ops.export_scene.gltf(filepath=f"{stem}.lod{lod}.glb", export_format="GLB", export_yup=True, use_selection=True,
                                  export_apply=True, export_extras=False, export_image_format="NONE",
                                  export_vertex_color="ACTIVE", export_all_vertex_colors=False)
        bpy.data.objects.remove(ob, do_unlink=True)
    return counts
