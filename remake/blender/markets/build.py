#!/usr/bin/env python3
"""build.py -- build the flea-market kit: every piece into one glb library (kit.glb), the MID versions (kit_mid.glb)
and pieces.json (the contract MARKETS-WORLD's runtime reads), plus palette-baked preview glbs for the contact sheets.

  ~/.venvs/ssc-assets/bin/python remake/blender/markets/textsigns.py     (the kit's lettered boards, once)
  ~/.venvs/ssc-assets/bin/python remake/blender/markets/build.py [--previews]
  ~/.venvs/ssc-assets/bin/python remake/blender/markets/check.py         (the offline audit; fix everything it flags)

Pure Python (the warren kit's geom.py); Blender renders the contact sheets (render.py)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mk  # noqa: E402
import p_local  # noqa: E402,F401
import p_signs  # noqa: E402,F401
import p_island  # noqa: E402,F401
import p_world  # noqa: E402,F401   (MARKETS-WORLD: food trucks, office, gate house, restrooms, bike rack, the floating pier)
from palettes import PALETTES  # noqa: E402

OUT = mk.OUT_DIR
RES = "res://remake/markets/"
PREV = os.path.join(mk.ROOT, "reference", "tmp", "markets_kit")
TEX_REL = {"markets": "../signs/markets.png", "markets_emit": "../signs/markets_emit.png", "mascots": "../signs/mascots.png",
           "mascots_emit": "../signs/mascots_emit.png", "stalls": "../signs/stalls.png", "stalls_emit": "../signs/stalls_emit.png",
           "goods": "../signs/goods.png", "goods_emit": "../signs/goods_emit.png", "kit_text": "kit_text.png", "kit_text_emit": "kit_text_emit.png"}


def _r(v, n=3):
    return [round(float(x), n) for x in v]


def build_all(only=None):
    built, mids, meta, fixes = [], [], {}, {}
    for pid, d in mk.PIECES.items():
        if only and pid not in only:
            continue
        m = d["build"](1)
        if d["ground"]:
            m = mk.drop_ground(m)
        m, log = mk.flicker.cure(m)
        if log:
            fixes[pid] = [[str(x) for x in e] for e in log]
        lo, hi = m.bounds()
        built.append((pid, m))
        slots = [s for s in mk.SLOTS if m.tris[s]]
        rec = {"glb": RES + "kit.glb", "mesh": pid, "group": d["group"], "kind": d["kind"], "foot": d["foot"], "tris": m.count(),
               "bounds": [_r(lo), _r(hi)], "slots": slots, "groups": sorted({mk.GROUP[s] for s in slots}), "lod1": d["lod1"],
               "collide": d["collide"], "palette": d["palette"], "notes": d["notes"]}
        if not d["foot"]:
            rec["foot"] = [round(hi[0] - lo[0], 2), round(hi[2] - lo[2], 2)]
            rec["foot_from_mesh"] = True
        for k in ("frame", "passes", "ramps", "anchors", "walk"):
            if d[k]:
                rec[k] = d[k]
        if d["frame"]:                                   # (collision never past the visible model)
            rec["frame"] = [[_r([max(b[0][k], lo[k]) for k in range(3)]), _r([min(b[1][k], hi[k]) for k in range(3)])] for b in d["frame"]]
        if d["moving"]:
            rec["moving"] = d["moving"]
        rec.update(d["extra"])
        if d["budget"]:
            rec["budget"] = d["budget"]
        # the MID
        how = d["mid"]
        mm = None
        if how == "auto":
            mm = d["build"](0)
            if d["ground"]:
                mm = mk.drop_ground(mm)
            mm, mlog = mk.flicker.cure(mm)
            if mlog:
                fixes.setdefault(pid, []).append(["mid cured", len(mlog)])
            if mm.count() > 0.85 * m.count() or mm.count() == 0:
                mm = None
        if mm is None:
            rec["mid"] = {"glb": RES + "kit.glb", "mesh": pid, "tris": m.count()}
        else:
            mids.append((pid, mm))
            rec["mid"] = {"glb": RES + "kit_mid.glb", "mesh": pid, "tris": mm.count(), "slots": [s for s in mk.SLOTS if mm.tris[s]]}
        meta[pid] = rec
    return built, mids, meta, fixes


def main(previews=False):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    built, mids, meta, fixes = build_all()
    size = mk.export_glb(os.path.join(OUT, "kit.glb"), built, tex_uri=TEX_REL)
    size_mid = mk.export_glb(os.path.join(OUT, "kit_mid.glb"), mids, tex_uri=TEX_REL)
    doc = {
        "version": 1,
        "contract": "research/flea_markets/requests.md (K1) + handoff_kit.md; built by remake/blender/markets/build.py",
        "frame": "glTF / Godot: +Y up, metres; origin at the footprint centre on the ground (cabins: the cabin floor centre); "
                 "the FRONT faces +Z (the aisle / road / customer side); anchors [x, y, z, yaw_deg] in the piece frame "
                 "(yaw: a right-handed turn about +Y, Godot's Basis(UP, deg_to_rad(yaw)))",
        "slots": mk.SLOTS,
        "slot_group": mk.GROUP,
        "slot_mechanism": "a glTF primitive per slot (material mk_<slot>); COLOR_0 = a grey SHADE (baked AO); the runtime "
                          "multiplies it by the palette colour of the slot (palettes[key][variant][slot], sRGB) into the merged "
                          "chunk's vertex colour, and merges by GROUP (one draw per group per chunk). Textured groups sample "
                          "their atlas with UV0 (alpha scissor 0.5, back faces culled: two-faced cards carry their own back).",
        "textures": {"tex_markets": "res://remake/signs/markets.png", "tex_mascots": "res://remake/signs/mascots.png",
                     "tex_stalls": "res://remake/signs/stalls.png", "tex_goods": "res://remake/signs/goods.png",
                     "tex_text": "res://remake/markets/kit_text.png"},
        "night": {"emissive": "palette colour x 2.0 HDR x night (bulbs, neon, lamp lenses, obstruction lights)",
                  "glow": "palette colour x 0.9 x night at most (lit faces: lantern glass and paper, lightboxes, cabin ceiling panels)",
                  "canvas": "albedo + albedo x 0.35 x night (tent cloth read through from inside; never over 0.9)",
                  "tex": "emit mask (the atlas _emit.png, L) x albedo x 2.0 x night (letters/neon 255 -> 2.0, faces 115 -> <= 0.9, boards 0)",
                  "glow_threshold": 1.5, "day": "emissive and glow groups show their palette colour x 0.85 as albedo"},
        "collide": {"frame": "ONLY the boxes in `frame` ([lo, hi], piece frame), never the triangles",
                    "none": "no collision (decals, goods, overhead strings)",
                    "ramps": "extra walking quads (4 points each, both faces collide), e.g. a station platform's ramps"},
        "passes": "walk-through volumes [{box: [lo, hi], kind: open|door}] (>= 2.2 m tall, >= 1 m wide; the check proves no "
                  "triangle or frame box is inside)",
        "walk": "[[x0, z0, x1, z1, y]] floor areas people stand on: the check proves >= 2.2 m of head room over them",
        "mid": "{glb, mesh, tris}: the MID level (fewer sides, small parts gone) in kit_mid.glb, or kit.glb when the full "
               "piece is already cheap",
        "lod1": {"keep": "keep the MID at LOD1 (silhouettes: tents, landmarks, sheds, poles)", "drop": "gone at LOD1",
                 "box": "a plain box"},
        "palettes": PALETTES,
        "pieces": meta,
    }
    with open(os.path.join(OUT, "pieces.json"), "w") as f:
        json.dump(doc, f, indent=1)
    with open(os.path.join(PREV, "flicker_fixes.json"), "w") as f:
        json.dump(fixes, f, indent=0)
    tris = sum(v["tris"] for v in meta.values())
    mt = sum(v["mid"]["tris"] for v in meta.values())
    print(f"{len(meta)} pieces, {tris} tris, kit.glb {size / 1024:.0f} KB; mid {mt} tris ({100 * mt / max(tris, 1):.0f}%), "
          f"kit_mid.glb {size_mid / 1024:.0f} KB; flicker fixes in {len(fixes)} pieces")
    if previews:
        write_previews(built, mids, meta)
    return meta


SHEETS = {   # contact sheet -> piece id prefixes / ids (laid out in rows)
    "local": ["fm_shed", "fm_shutter", "fm_pitch", "fm_canopy", "fm_table", "fm_shelf", "fm_crate", "fm_rack", "fm_bin", "fm_tarp",
              "fm_lot_pole"],
    "lot": ["fm_kerb", "fm_wheel", "fm_lot_island", "fm_paint", "festoon_pole"],
    "goods": ["fm_goods"],
    "signs_a": ["fm_arch", "sign_fm01", "sign_fm02", "sign_fm03", "sign_fm04", "sign_fm05", "sign_fm06", "sign_fm07", "sign_fm08",
                "sign_fm09", "sign_fm10", "sign_fm11"],
    "signs_b": ["sign_fm12", "sign_fm13", "sign_fm14", "sign_fm15", "sign_fm16", "sign_fm17", "sign_fm18", "sign_fm19", "sign_fm20",
                "sign_fm21", "sign_fm22", "fm_board_island", "fm_skein"],
    "tents": ["tent_bazaar", "tent_event", "tent_logistics", "tent_canopy", "tent_lantern"],
    "furniture": ["tent_shelf", "tent_table", "tent_counter", "tent_rail", "tent_ballast"],
    "lights": ["festoon_warm", "festoon_skein", "festoon_bulb", "skein_lantern"],
    "ropeway": ["gondola", "rope_", "ground_station", "deadman", "mooring_mast"],
    "world": ["fm_food_truck", "fm_office", "fm_gatehouse", "fm_restroom", "fm_bike_rack", "fm_pier"],
}


def sheet_ids(meta, key):
    out = []
    for pre in SHEETS[key]:
        for pid in meta:
            if pid.startswith(pre) and pid not in out and not (key == "local" and pid.startswith("fm_board")):
                out.append(pid)
    # (small and low in front, tall at the back: the rows run away from the camera)
    def size(p):
        lo, hi = meta[p]["bounds"]
        return (round((hi[0] - lo[0]) * (hi[2] - lo[2]) * max(hi[1] - lo[1], 1.0), 0), p)
    return sorted(out, key=size)


def dressed(pid, m, built):
    """a tent with its furniture and goods placed (the `dress` list) for the contact sheets"""
    d = mk.PIECES[pid]["extra"].get("dress")
    if not d:
        return m
    out = mk.Mesh()
    out.add(m)
    for sub, x, y, z, yaw in d:
        if sub in built:
            mk.place(out, built[sub], x, y, z, yaw)
    return out


def write_previews(built, mids, meta):
    """per sheet: a glb with every piece laid out in a row-packed grid (palette variant 0 baked), full and mid"""
    bm, mm = dict(built), dict(mids)
    uri = {k: os.path.relpath(os.path.join(OUT, v), PREV) for k, v in TEX_REL.items()}
    layout = {}
    for key in SHEETS:
        ids = sheet_ids(meta, key)
        if not ids:
            continue
        for tag, src in (("full", bm), ("mid", mm)):
            laid, x, zrow, rowdepth = [], 0.0, 0.0, 0.0
            width = 34.0 if key not in ("goods",) else 6.0
            pos = {}
            for kk, pid in enumerate(ids):
                m = src.get(pid, bm[pid])
                if key == "tents" and tag == "full":
                    m = dressed(pid, m, bm)
                lo, hi = bm[pid].bounds()
                w = hi[0] - lo[0]
                if x > 0 and x + w > width:
                    x, zrow, rowdepth = 0.0, zrow - rowdepth - 2.0, 0.0
                vs = PALETTES.get(meta[pid]["palette"], PALETTES["white"])
                pal = vs[kk % len(vs)]
                cols = {s: mk.hex_rgb(pal.get(s, "#bbbbbb")) for s in mk.SLOTS}
                g = mk.Mesh()
                g.add(m, mk.move(x - lo[0], 0.0, zrow - hi[2]))
                laid.append((pid, g, cols))
                pos[pid] = [x - lo[0], zrow - hi[2], w, hi[1]]
                x += w + 1.5
                rowdepth = max(rowdepth, hi[2] - lo[2])
            _export_with_tables(os.path.join(PREV, f"sheet_{key}_{tag}.glb"), [(p, g) for p, g, _ in laid],
                                {p: c for p, _, c in laid}, uri)
            layout[f"{key}_{tag}"] = pos
    json.dump(layout, open(os.path.join(PREV, "layout.json"), "w"), indent=0)
    print("previews in", PREV)


def _export_with_tables(path, pieces, tables, uri):
    """mk.export_glb with a colour table per piece (previews only)"""
    import json as _j
    import struct
    bin_ = bytearray()
    views, accs, meshes, nodes, mats, mat_ix, images, textures, img_ix = [], [], [], [], [], {}, [], [], {}

    def view(data, target):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(data)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(views) - 1

    def acc(arr, comp, typ, target, norm=False, minmax=False):
        a = {"bufferView": view(arr.tobytes(), target), "componentType": comp, "count": int(arr.shape[0]), "type": typ}
        if norm:
            a["normalized"] = True
        if minmax:
            a["min"] = [float(v) for v in arr.min(axis=0)]
            a["max"] = [float(v) for v in arr.max(axis=0)]
        accs.append(a)
        return len(accs) - 1

    def tex(name):
        if name not in uri:
            return None
        if name not in img_ix:
            images.append({"uri": uri[name]})
            textures.append({"source": len(images) - 1})
            img_ix[name] = len(textures) - 1
        return img_ix[name]

    for name, m in pieces:
        cols = tables[name]
        prims = []
        for slot in mk.SLOTS:
            ts = m.tris[slot]
            if not ts:
                continue
            pos, nrm, col, uvs = [], [], [], []
            for a, b, c, sh, uv in ts:
                a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
                n = np.cross(b - a, c - a)
                ln = np.linalg.norm(n)
                if ln < 1e-12:
                    continue
                n /= ln
                pos += [a, b, c]
                nrm += [n, n, n]
                rgb = np.array(cols.get(slot, (0.7, 0.7, 0.7))) * sh
                col += [list(rgb) + [1.0]] * 3
                uvs += [uv[0], uv[1], uv[2]] if uv is not None else [(0, 0)] * 3
            P = np.array(pos, np.float32)
            attrs = {"POSITION": acc(P, 5126, "VEC3", 34962, minmax=True), "NORMAL": acc(np.array(nrm, np.float32), 5126, "VEC3", 34962),
                     "COLOR_0": acc(np.clip(np.array(col, np.float32), 0, 1), 5126, "VEC4", 34962),
                     "TEXCOORD_0": acc(np.array(uvs, np.float32), 5126, "VEC2", 34962)}
            ia = acc(np.arange(P.shape[0], dtype=np.uint32), 5125, "SCALAR", 34963)
            mn = "mk_" + slot
            if mn not in mat_ix:
                g = mk.GROUP[slot]
                mt = {"name": mn, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0, "roughnessFactor": 0.8},
                      "extras": {"group": g}}
                if slot in mk.TEX:
                    ti = tex(mk.TEX[slot])
                    if ti is not None:
                        mt["pbrMetallicRoughness"]["baseColorTexture"] = {"index": ti}
                        et = tex(mk.TEX[slot] + "_emit")
                        if et is not None:
                            mt["emissiveTexture"] = {"index": et}
                            mt["emissiveFactor"] = [1, 1, 1]
                    mt["alphaMode"] = "MASK"
                    mt["alphaCutoff"] = 0.5
                mat_ix[mn] = len(mats)
                mats.append(mt)
            prims.append({"attributes": attrs, "indices": ia, "material": mat_ix[mn]})
        if prims:
            meshes.append({"name": name, "primitives": prims})
            nodes.append({"name": name, "mesh": len(meshes) - 1})
    while len(bin_) % 4:
        bin_.append(0)
    gl = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes,
          "materials": mats, "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(bin_)}]}
    if images:
        gl["images"], gl["textures"] = images, textures
    js = _j.dumps(gl, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    open(path, "wb").write(out)


if __name__ == "__main__":
    main("--previews" in sys.argv)
