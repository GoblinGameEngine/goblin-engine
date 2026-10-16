#!/usr/bin/env python3
"""build.py -- build the warren kit: every piece in pieces.py into one glb library plus pieces.json (the contract the
GENERATOR and RUNTIME streams read), and per-civ preview glbs with the palettes baked (for the contact sheets).

  ~/.venvs/ssc-assets/bin/python remake/blender/sky/warren_kit/build.py [--previews]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom  # noqa: E402
from pieces import PALETTES, PIECES  # noqa: E402
import flicker  # noqa: E402
import mid  # noqa: E402
import passes  # noqa: E402
from ramps import RAMPS  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens")
KIT = os.path.join(OUT, "kit")
RES = "res://remake/sky/warrens/kit/"
PREV = os.path.join(ROOT, "reference", "tmp", "warren_kit")


def hex_rgb(h, linear=True):
    """a palette colour for a PREVIEW glb (Blender reads COLOR_0 as linear: convert the sRGB hex, or it renders pale)"""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    if linear:
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return tuple(c)


NOPASS = {"wall_luiken_k", "wall_cumba_t", "wall_cantilever_step_t"}   # (an attic hatch, an oriel's window, a stepped face)
H = 1.5


def _box(x0, y0, z0, x1, y1, z1):
    return [[x0, y0, z0], [x1, y1, z1]]


SPECIAL = {   # pieces whose walk-through runs other than straight through the wall plane
    "wall_qilou_t": dict(frame=[_box(1.1, 0, -0.4, 1.5, 2.85, 0.0), _box(-H, 0, -2.75, H, 3.2, -2.5), _box(-H, 2.85, -2.5, H, 3.2, 0.0)],
                         **{"pass": _box(-H, 0, -2.45, 1.08, 2.83, 0.0), "pass_kind": "open", "clear": [2.58, 2.83], "foot": 0.0}),
    "wall_five_foot_way_t": dict(frame=[_box(1.1, 0, -0.4, 1.5, 2.9, 0.0), _box(-H, 0, -1.85, H, 3.2, -1.6), _box(-H, 2.9, -1.6, H, 3.2, 0.0)],
                                 **{"pass": _box(-H, 0, -1.58, 1.08, 2.7, 0.0), "pass_kind": "open", "clear": [2.58, 2.7], "foot": 0.0}),
    "torii": dict(frame=[_box(-1.27, 0, -0.17, -0.93, 3.4, 0.17), _box(0.93, 0, -0.17, 1.27, 3.4, 0.17), _box(-1.95, 2.65, -0.17, 1.95, 3.85, 0.17)],
                  **{"pass": _box(-0.92, 0, -0.6, 0.92, 2.64, 0.6), "pass_kind": "open", "clear": [1.84, 2.64], "foot": 0.0}),
    "dome_bazaar_crossing": dict(frame=[_box(sx * 1.0 if sx > 0 else -1.5, 0, sz * 1.0 if sz > 0 else -1.5, 1.5 if sx > 0 else -1.0, 4.4, 1.5 if sz > 0 else -1.0)
                                        for sx in (-1, 1) for sz in (-1, 1)] + [_box(-1.5, 3.0, -1.5, 1.5, 6.8, 1.5)],
                                 **{"pass": _box(-0.7, 0, -1.5, 0.7, 2.6, 1.5), "pass_x": _box(-1.5, 0, -0.7, 1.5, 2.6, 0.7), "pass_kind": "open",
                                    "clear": [1.4, 2.6], "foot": 0.0}),
    "abbara_vault": dict(frame=[_box(-1.6, 0, -1.5, -1.45, 2.2, 1.5), _box(1.45, 0, -1.5, 1.6, 2.2, 1.5), _box(-1.6, 2.2, -1.5, 1.6, 3.2, 1.5)]
                         + [_box(sx * 1.3 if sx > 0 else -1.45, 0, sz * 1.2 if sz > 0 else -1.5, 1.45 if sx > 0 else -1.3, 2.2, 1.5 if sz > 0 else -1.2)
                            for sx in (-1, 1) for sz in (-1, 1)],                      # (the portal jambs)
                         **{"pass": _box(-0.9, 0, -1.5, 0.9, 2.18, 1.5), "pass_kind": "open", "clear": [1.8, 2.18], "foot": 0.0}),
}


def walk_frame(pid, d, m):
    """{"collide": "frame", "frame": [...], "pass": [lo, hi], "pass_kind", "clear", "foot"} for a walk-through piece"""
    if pid in SPECIAL:
        out = dict(SPECIAL[pid])
        out["collide"] = "frame"
        return out
    if d["group"] != "wall" or d["kind"] not in ("wall", "passage") or pid in NOPASS or d["collide"] is not True:
        return None
    a = passes.analyse(m)
    if not a["kind"] or not a["frame"] or a["clear"][0] > 2.9:
        return None
    w, h = a["clear"]
    ok = w >= passes.MIN_W - 1e-6 and h >= passes.MIN_H - 1e-6 and a["foot"] <= passes.MAX_STEP + 1e-6
    return {"collide": "frame", "frame": a["frame"], "pass": a["pass"], "pass_kind": a["kind"], "clear": [float(w), float(h)],
            "foot": float(a["foot"]), "pass_ok": ok}


def main(previews=False):
    os.makedirs(KIT, exist_ok=True)
    built, mids, undersized = [], [], []
    meta = {}
    fixes = {}
    for pid, d in PIECES.items():
        m, log = flicker.finish(pid, d, d["build"]())
        if log:
            fixes[pid] = log
        built.append((pid, m))
        lo, hi = m.bounds()
        meta[pid] = {"glb": RES + "kit.glb", "mesh": pid, "group": d["group"], "kind": d["kind"], "civs": d["civs"],
                     "bay": [3.0, 3.2], "span": d["span"], "lod1": d["lod1"], "collide": d["collide"],
                     "slots": [s for s in geom.SLOTS if m.tris[s]], "tris": m.count(),
                     "bounds": [[round(v, 3) for v in lo], [round(v, 3) for v in hi]], "notes": d["notes"]}
        mm, how = mid.mid_mesh(pid, d, m, RAMPS.get(pid))
        if how == "mid":
            mm, mlog = flicker.cure(mm)
            if mlog:
                fixes.setdefault(pid, []).append(("mid cured", "", len(mlog), ""))
        if how in ("mid", "ramp"):
            mids.append((pid, mm))
            meta[pid]["mid"] = {"glb": RES + "kit_mid.glb", "mesh": pid, "tris": mm.count(), "slots": [s for s in geom.SLOTS if mm.tris[s]]}
        elif how == "none":
            meta[pid]["mid"] = None
        else:
            meta[pid]["mid"] = {"glb": RES + "kit.glb", "mesh": pid, "tris": m.count(), "slots": meta[pid]["slots"]}
        fr = walk_frame(pid, d, m)
        if fr:
            meta[pid].update(fr)
            if not fr.get("pass_ok", True):
                undersized.append((pid, fr["clear"], fr.get("foot")))
            meta[pid].pop("pass_ok", None)
        if pid in RAMPS:
            meta[pid]["collide"] = "ramp"
            meta[pid]["ramp"] = RAMPS[pid]
    size = geom.export_glb(os.path.join(KIT, "kit.glb"), built)
    size_mid = geom.export_glb(os.path.join(KIT, "kit_mid.glb"), mids)
    doc = {
        "version": 1,
        "contract": "research/sky_islands/warrens/00_brief.md (milestone 1); built by remake/blender/sky/warren_kit/build.py",
        "frames": {
            "wall": "x -1.5..1.5 across the bay, y 0..3.2 up, +Z out of the cell; body inside the cell z -t..0 (t 0.25 thin _t, 0.6 thick _k); ornaments reach +Z",
            "edge": "as wall, standing on a roof top (y 0 = roof top)",
            "corner": "origin on the cell's vertical edge; the occupied cell in -X/-Z; exposed faces +X and +Z",
            "cell": "origin at the cell centre, y 0 = the walking surface / roof top / (ceiling pieces) the ceiling; spans x, z -1.5..1.5 (span [nx, nz] cells along +X/+Z from the first)",
        },
        "units": {"cell": [3.0, 3.2, 3.0]},
        "slots": geom.SLOTS,
        "slot_mechanism": "each piece mesh has one surface per slot (material 'wk_<slot>'); COLOR_0 is a grey SHADE (baked AO/variation); the runtime multiplies it by the civ palette colour of that slot (palette index from the placement) into the merged chunk's vertex colour; glass surfaces carry pane UV0 0..1 for interior mapping; emissive surfaces glow at night",
        "lod1_rules": {"box": "draw the cell face / slab plainly instead", "keep": "keep at LOD1 (silhouette)", "drop": "gone at LOD1"},
        "collide": {"true": "the piece's triangles", "false": "none",
                    "ramp": "stairs: collide ONLY with the quads in the piece's \"ramp\" list (piece frame, 4 points each, winding meaningless: collide both faces) -- smooth inclines over the treads, landings flat, spirals as a run of quads round the helix; never with the stair's triangles (the player has no step-up)"},
        "frame": "walk-through pieces collide as \"frame\": ONLY the boxes in their \"frame\" list ([lo, hi] in the piece frame: jambs, piers, lintel and wall mass), never their triangles; door leaves, grilles and screens inside the opening do not collide. \"pass\" is the clear volume [lo, hi] a walker passes through (>= 1.0 m wide, >= 2.2 m tall, its foot <= 0.25 m: a step, no ramp needed); \"pass_kind\": \"open\" (an archway, a gate, a moon gate, an arcade) or \"door\" (a doorway whose leaf is drawn: walk-through only where the generator puts a room or a lane behind it)",
        "mid": "the MID level of detail (medium distance, between the full piece and LOD1): {glb, mesh, tris, slots} -- same frame, same slot materials, merged like the full piece; it points into kit_mid.glb (a relief impostor for walls/edges: openings as inset panes, projections as plain boxes, signs as lit panels; turned/decimated parts for cells), or back into kit.glb when the full piece is already cheap; null = draw nothing at mid range (thin overlays: cables, wires, bars)",
        "palettes": PALETTES,
        "pieces": meta,
    }
    with open(os.path.join(PREV, "undersized_openings.json"), "w") as f:
        json.dump(undersized, f, indent=0)
    with open(os.path.join(PREV, "flicker_fixes.json"), "w") as f:
        json.dump({k: [[str(x) for x in e] for e in v] for k, v in fixes.items()}, f, indent=0)
    with open(os.path.join(OUT, "pieces.json"), "w") as f:
        json.dump(doc, f, indent=1)
    tris = sum(v["tris"] for v in meta.values())
    mt = sum((v["mid"] or {}).get("tris", 0) for v in meta.values())
    print(f"{len(meta)} pieces, {tris} tris, kit.glb {size / 1024:.0f} KB; mid {mt} tris ({100 * mt / tris:.0f}%), kit_mid.glb {size_mid / 1024:.0f} KB")
    if previews:
        os.makedirs(PREV, exist_ok=True)
        for civ, pals in PALETTES.items():
            cols = {k: hex_rgb(v) for k, v in pals[0].items()}
            sel = [(pid, m) for pid, m in built if "shared" in PIECES[pid]["civs"] or civ in PIECES[pid]["civs"]]
            # laid out on a grid (by group), facing the camera (+Z toward -Y in Blender = the front)
            cols_n = 9
            laid = []
            for k, (pid, m) in enumerate(sel):
                gm = geom.Mesh()
                r, c = divmod(k, cols_n)
                gm.add(m, geom.move(c * 4.5, 0.0, -r * 5.0))
                laid.append((pid, gm))
            geom.export_glb(os.path.join(PREV, f"kit_{civ}.glb"), laid, colours=cols)
            with open(os.path.join(PREV, f"kit_{civ}.txt"), "w") as f:
                f.write("\n".join(f"{k // cols_n},{k % cols_n} {pid}" for k, (pid, _) in enumerate(sel)))
        print("previews in", PREV)
        # per family: its own marks beside a few shared walls, in its palette (the family sheets)
        shared = ["wall_plain_t", "wall_window_m_t", "wall_door_t", "wall_shopfront_a_t", "wall_plain_k", "wall_window_s_k"]
        for civ, pals in PALETTES.items():
            marks = [pid for pid, d in PIECES.items() if civ in d["civs"] and "shared" not in d["civs"]]
            if not marks:
                continue
            cols = {k: hex_rgb(v) for k, v in pals[0].items()}
            laid, bm = [], dict(built)
            zrow = 7.0
            for ids in (marks, shared):                          # the marks in front (packed by size), shared behind
                x, zrow = 0.0, zrow - 7.0
                for pid in ids:
                    lo, hi = bm[pid].bounds()
                    if x > 15.0:
                        x, zrow = 0.0, zrow - 7.0
                    gm = geom.Mesh()
                    gm.add(bm[pid], geom.move(x - lo[0], 0.0, zrow))
                    laid.append((pid, gm))
                    x += hi[0] - lo[0] + 1.2
            geom.export_glb(os.path.join(PREV, f"fam_{civ}.glb"), laid, colours=cols)
            # full (front row) beside its mid (behind it), the family's own pieces: the LOD comparison sheets
            mm = dict(mids)
            cmp_, x, zrow = [], 0.0, 0.0
            for pid in marks:
                lo, hi = bm[pid].bounds()
                if x > 15.0:
                    x, zrow = 0.0, zrow - 14.0
                for tag, src, dz in (("", bm[pid], 0.0), ("_mid", mm.get(pid, bm[pid] if meta[pid]["mid"] else geom.Mesh()), -7.0)):
                    gm = geom.Mesh()
                    gm.add(src, geom.move(x - lo[0], 0.0, zrow + dz))
                    if gm.count():
                        cmp_.append((pid + tag, gm))
                x += hi[0] - lo[0] + 1.2
            geom.export_glb(os.path.join(PREV, f"cmp_{civ}.glb"), cmp_, colours=cols)
    return meta


if __name__ == "__main__":
    main("--previews" in sys.argv)
