"""
gbkit.py -- shared building parts (research/buildings/kit_design.md).

A repeated item (a window unit, a chair, a shelf of goods ...) is built once, at the origin in its own frame, into the
kit (<buildings>/kit/<piece>.glb + .mats.json), and each building only says where its copies stand
(<ID>.kit.json: [[piece, x, y, z, yaw], ...] in the building's frame, Blender axes).  The game puts them back with
MultiMeshes (remake/scripts/building_loader.gd).

How: the item functions are wrapped.  A top-level call is built as before; afterwards the faces it added are read back,
moved into the item's frame and hashed -- the hash IS the piece id, so two calls that made the same geometry share a
piece whatever their arguments were.  The faces are tagged (a face int layer "kit") and stay in the building until the
audit and the LODs have seen them; then strip() takes them out of the visual mesh.  Faces of a "-col" part keep
their collision (moved to a "-colonly" copy), so physics and the audit are unchanged.

An item is left in place (not kitted) when its frame isn't a pure turn about z, when it touches grade (the ground
sink moves those vertices), or when it builds into a special part (door leaves, ladders, lights) or a parented or
turned part.
"""
import hashlib
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector

import gblib

LAYER = "kit"
MIN_FACES = 6             # (a lone quad isn't worth an instance)


def enabled():
    return os.environ.get("SSC_KIT", "1") != "0"


# ------------------------------------------------------------------ frames: where an item stands
def _furn_frame(a, k):
    """(p, pos, yaw, ...) -> (origin, yaw radians)"""
    pos = a[1]
    yaw = a[2] if len(a) > 2 and isinstance(a[2], (int, float)) else k.get("yaw", 0.0)
    return Vector(tuple(pos)[:3]), math.radians(float(yaw))


def _window_frame(a, k):
    """window(b, part_name, frame, off, w, sill, head, ...): the opening's corner, facing along the wall"""
    o, u, w_in, up = a[2]
    off, sill = a[3], a[5]
    return Vector(o) + Vector(u) * off + Vector(up) * sill, (Vector(u), Vector(w_in), Vector(up))


def _basis_yaw(basis):
    u, v, w = basis
    if abs(w.z - 1) > 1e-6 or abs(u.z) > 1e-6:
        return None
    yaw = math.atan2(u.y, u.x)
    if (Vector((-math.sin(yaw), math.cos(yaw), 0)) - v).length > 1e-5:
        return None           # (a mirrored frame)
    return yaw


# ------------------------------------------------------------------ capture
class _State:
    depth = 0
    pieces = {}           # piece id -> {"faces": [(mat key name, [(x,y,z)...], [(u,v)...])], "defs": {...}}


def _tag_layer(bm):
    return bm.faces.layers.int.get(LAYER) or bm.faces.layers.int.new(LAYER)


def _snapshot(b):
    return {n: len(p.bm.faces) for n, p in b.objs.items() if getattr(p, "bm", None) is not None and p.bm.is_valid}


SKIP = {}


def _skip(why):
    SKIP[why] = SKIP.get(why, 0) + 1
    return None


def _capture(b, before, origin, yaw):
    """the faces added since `before`, in the item frame; None if the item can't be kitted"""
    c, s = math.cos(-yaw), math.sin(-yaw)
    faces = []
    touched = []
    for n, p in b.objs.items():
        bm = getattr(p, "bm", None)
        if bm is None or not bm.is_valid:
            continue
        f0 = before.get(n, 0)
        if len(bm.faces) <= f0:
            continue
        if n.startswith(("door_", "ladder_", "light_")) or p.parent is not None or p.rot_z:
            return _skip("special part " + n.split("_")[0])
        bm.faces.ensure_lookup_table()
        new = [bm.faces[i] for i in range(f0, len(bm.faces))]
        touched.append((p, f0, len(bm.faces)))
        for f in new:
            wv = [v.co + p.origin for v in f.verts]
            if any(abs(q.z) < 0.03 for q in wv) and b.sink_ground:
                return _skip("on grade")                      # (the ground sink would move it)
            loc = []
            for q in wv:
                d = q - origin
                loc.append((round(c * d.x - s * d.y, 4), round(s * d.x + c * d.y, 4), round(d.z, 4)))
            key = p.mat_keys[f.material_index]
            faces.append((p, key, loc))
    if sum(f1 - f0 for _, f0, f1 in touched) < MIN_FACES:
        return _skip("few faces")
    return faces, touched


def _uv(loc, tile):
    """gblib Part.face's projection, in the item's own frame (the piece's UVs are canonical)"""
    a, b_, c_ = (Vector(loc[1]) - Vector(loc[0])), (Vector(loc[2]) - Vector(loc[0])), None
    n = a.cross(b_)
    if n.length < 1e-12 and len(loc) > 3:
        n = a.cross(Vector(loc[3]) - Vector(loc[0]))
    ax = max(range(3), key=lambda i: abs(n[i]))
    out = []
    for w in loc:
        if ax == 0:
            uv = (w[1] * (1 if n.x > 0 else -1), w[2])
        elif ax == 1:
            uv = (w[0] * (-1 if n.y > 0 else 1), w[2])
        else:
            uv = (w[0], w[1])
        out.append((round(uv[0] / tile, 5), round(uv[1] / tile, 5)))
    return out


def _piece_id(b, faces):
    h = hashlib.sha1()
    for p, key, loc in faces:
        h.update(b.mats[key].name.encode())
        h.update(repr(loc).encode())
        h.update(repr(round(b.tile.get(key, 1.0), 4)).encode())
    return "K" + h.hexdigest()[:13]


def wrap(fn, frame_of):
    def kitted(*a, **k):
        b = gblib.CURRENT
        if b is None or _State.depth or not enabled() or not getattr(b, "kit_on", True):
            _State.depth += 1
            try:
                return fn(*a, **k)
            finally:
                _State.depth -= 1
        before = _snapshot(b)
        _State.depth += 1
        try:
            out = fn(*a, **k)
        finally:
            _State.depth -= 1
        try:
            origin, rot = frame_of(a, k)
            yaw = rot if isinstance(rot, float) else _basis_yaw(rot)
            if yaw is None:
                _skip("frame not a turn: " + getattr(fn, "__name__", "?"))
                return out
            got = _capture(b, before, origin, yaw)
            if got is None:
                return out
            faces, touched = got
            pid = _piece_id(b, faces)
            if pid not in _State.pieces and pid not in b.kit_new:
                b.kit_new[pid] = [(b.mats[key].name, loc, _uv(loc, b.tile.get(key, 1.0))) for _, key, loc in faces]
                for _, key, _ in faces:
                    b.kit_defs[b.mats[key].name] = b.mat_defs.get(b.mats[key].name)
            b.kit_inst.append([pid, round(origin.x, 4), round(origin.y, 4), round(origin.z, 4), round(math.degrees(yaw), 3)])
            tag = len(b.kit_inst)
            for p, f0, f1 in touched:
                lay = _tag_layer(p.bm)          # (adding a layer frees every BMFace reference: index afresh)
                p.bm.faces.ensure_lookup_table()
                for i in range(f0, f1):
                    p.bm.faces[i][lay] = tag
        except Exception as e:                                # (never break a build over the kit)
            print("KIT skip", getattr(fn, "__name__", "?"), e)
        return out
    kitted.__name__ = getattr(fn, "__name__", "kitted")
    kitted.__wrapped__ = fn
    return kitted


# ------------------------------------------------------------------ strip + write
def strip(b):
    """take the kitted faces out of the visual mesh (after the audit and the LODs); a -col part's go to -colonly"""
    for ob in list(bpy.data.objects):
        if ob.type != "MESH" or gblib._is_special(ob):
            continue
        att = ob.data.attributes.get(LAYER)
        if att is None:
            continue
        tags = [d.value for d in att.data]
        if not any(tags):
            ob.data.attributes.remove(att)
            continue
        if ob.name.endswith("-col"):
            dup = ob.copy()
            dup.data = ob.data.copy()
            bpy.context.scene.collection.objects.link(dup)
            dup.name = ob.name[:-4] + "_kit-colonly"
            _delete_faces(dup.data, [not t for t in tags])
            dup.data.attributes.remove(dup.data.attributes[LAYER])
        _delete_faces(ob.data, [bool(t) for t in tags])
        if LAYER in ob.data.attributes:
            ob.data.attributes.remove(ob.data.attributes[LAYER])


def _delete_faces(me, mask):
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    gone = [bm.faces[i] for i, m in enumerate(mask) if m]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bm.to_mesh(me)
    bm.free()


def kit_dir(out_glb):
    return os.path.join(os.path.dirname(out_glb), "kit")


def write(b, out_glb):
    """<ID>.kit.json, and every piece this building made first (if the kit doesn't have it yet)"""
    base = os.path.splitext(out_glb)[0]
    if not b.kit_inst:
        if os.path.exists(base + ".kit.json"):
            os.remove(base + ".kit.json")
        return
    with open(base + ".kit.json", "w") as f:
        json.dump(b.kit_inst, f, separators=(",", ":"))
    kd = kit_dir(out_glb)
    os.makedirs(kd, exist_ok=True)
    for pid, faces in b.kit_new.items():
        _State.pieces[pid] = True
        path = os.path.join(kd, pid + ".glb")
        if os.path.exists(path):
            continue
        _export_piece(b, pid, faces, path)


def _export_piece(b, pid, faces, path):
    by_name = {m.name: m for m in bpy.data.materials}
    names = []
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    for mname, loc, uvs in faces:
        if mname not in names:
            names.append(mname)
        vs = [bm.verts.new(q) for q in loc]
        try:
            f = bm.faces.new(vs)
        except ValueError:
            continue
        f.material_index = names.index(mname)
        for lp, uv in zip(f.loops, uvs):
            lp[uvl].uv = uv
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    me = bpy.data.meshes.new(pid)
    bm.to_mesh(me)
    bm.free()
    for n in names:
        me.materials.append(by_name[n])
    ob = bpy.data.objects.new(pid, me)
    bpy.context.scene.collection.objects.link(ob)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    tmp = path + ".%d.tmp.glb" % os.getpid()
    bpy.ops.export_scene.gltf(filepath=tmp, export_format="GLB", export_yup=True, use_selection=True,
                              export_apply=True, export_image_format="NONE")
    os.replace(tmp, path)                                     # (atomic: parallel builds may race to the same piece)
    mp = os.path.splitext(path)[0] + ".mats.json"
    with open(mp + ".%d.tmp" % os.getpid(), "w") as f:
        json.dump({n: b.kit_defs.get(n) for n in names}, f, indent=0)
    os.replace(mp + ".%d.tmp" % os.getpid(), mp)
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)


# ------------------------------------------------------------------ install
def install():
    """wrap the item functions (after build_record's recorder, so the recorder still logs every call) and hook
    Building.finish: strip before the meshes merge, write after the export"""
    if getattr(gblib, "_kit_installed", False):
        return
    gblib._kit_installed = True
    import inspect
    import gbfurn
    import gbhouse
    import shopfit
    for mod in (gbfurn, shopfit):
        for n, fn in list(vars(mod).items()):
            if not inspect.isfunction(fn):
                continue
            inner = getattr(fn, "__wrapped__", fn)
            if inner.__module__ != mod.__name__:
                continue
            ps = list(inspect.signature(inner).parameters)
            if len(ps) >= 2 and ps[0] == "p" and ps[1] == "pos":
                setattr(mod, n, wrap(fn, _furn_frame))
    for n in ("tv_stand", "tub", "vanity", "appliance", "base_cabinets"):
        if hasattr(gbhouse, n):
            setattr(gbhouse, n, wrap(getattr(gbhouse, n), _furn_frame))
    gblib.window = wrap(gblib.window, _window_frame)

    init = gblib.Building.__init__

    def __init__(self, *a, **k):
        init(self, *a, **k)
        self.kit_inst, self.kit_new, self.kit_defs = [], {}, {}
    gblib.Building.__init__ = __init__

    merge = gblib.Building.merge_meshes

    def merge_meshes(self):
        if self.kit_inst:
            strip(self)
        return merge(self)
    gblib.Building.merge_meshes = merge_meshes

    finish = gblib.Building.finish

    def finish_(self, out_glb):
        r = finish(self, out_glb)
        write(self, out_glb)
        print("KIT %s %d instances, %d new pieces  skipped %s" % (os.path.basename(out_glb), len(self.kit_inst), len(self.kit_new), SKIP))
        SKIP.clear()
        return r
    gblib.Building.finish = finish_
