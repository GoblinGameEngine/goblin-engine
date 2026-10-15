"""writer.py -- the placement file (<id>.bin.gz) and its readable twin (<id>.json); FORMAT.md."""
import gzip
import io
import json
import math
import struct

from lattice import CELL, LEVELS, PLAN_NAMES, STOREY
from pieces import catalogue

CHUNK = 8


def _str(b, s):
    e = s.encode("utf-8")
    b.write(struct.pack("<H", len(e)))
    b.write(e)


def foliage_instances(L, civ, items):
    """civ.foliage's (species, where, rot, scale) -> [species, x, y, z, rot, scale] in the island frame"""
    out = []
    for sp, where, rot, scale in items:
        if len(where) == 3:                               # on a roof (level given)
            i, j, k = where
            x, _, z = L.centre(i, j)
            y = k * STOREY
        else:
            i, j = where
            x, _, z = L.centre(i, j)
            y = L.deck_y(x, z)
        from pick import FACE, h01
        if isinstance(rot, int) and not isinstance(rot, bool):
            # a climber on a wall: rot is the face (pick.FACE); stand it on the face plane, yaw turning its +Z out
            # of the wall (yaw = atan2(nx, nz) about +Y), slid along the bay
            di, dj = FACE[rot]
            along = (h01(L.seed, "fa", i, j, sp) - 0.5) * 1.8
            x += di * 1.55 + dj * along
            z += dj * 1.55 + di * along
            yaw = math.atan2(di, dj)
        else:
            # (scatter inside the cell, hashed in the island frame)
            x += (h01(L.seed, "fx", i, j, sp) - 0.5) * 1.6
            z += (h01(L.seed, "fz", i, j, sp) - 0.5) * 1.6
            yaw = float(rot)
        out.append([sp, round(x, 2), round(y, 2), round(z, 2), round(yaw, 4), float(scale)])
    return out


def write(L, civ, o, units, doors, foliage, out_bin, out_json, stats, kit):
    cat = catalogue()
    kpal = kit["palettes"].get(civ.id) or [{"wall": "#cccccc"}]
    mounts = {}
    for r in o.recs:
        mounts[r[0]] = r[6]
    # doors in the kit's rot (+Z, +X, -Z, -X for 0..3; the generator's FACE map + 2)
    doors = [(u, c, k, (rot + 2) & 3, e) for (u, c, k, rot, e) in doors]
    used = sorted(set(r[0] for r in o.recs))
    pid = {p: n for n, p in enumerate(used)}
    species = sorted(set(f[0] for f in foliage))
    sid = {s: n for n, s in enumerate(species)}
    # chunks
    by = {}
    for r in o.recs:
        key = (r[1] // CHUNK, r[2] // CHUNK)
        by.setdefault(key, []).append(r)
    keys = sorted(by)
    b = io.BytesIO()
    b.write(b"WRN1")
    b.write(struct.pack("<H", 2))
    _str(b, civ.id)
    b.write(struct.pack("<ffff", L.x0, L.z0, CELL, STOREY))
    b.write(struct.pack("<HHB", L.nx, L.nz, LEVELS))
    pal = [v.get("wall", "#cccccc") for v in kpal][:16]      # (each variant's wall colour; the runtime reads all
    b.write(struct.pack("<B", len(pal)))                     #  the slots from pieces.json palettes[civ][variant])
    for hx in pal:
        hx = hx.lstrip("#")
        b.write(bytes([int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)]))
    b.write(struct.pack("<H", len(used)))
    for p in used:
        _str(b, p)
    b.write(struct.pack("<H", len(species)))
    for s in species:
        _str(b, s)
    b.write(struct.pack("<H", len(keys)))
    first = 0
    chunk_stats = []
    for k in keys:
        n = len(by[k])
        b.write(struct.pack("<BBII", k[0], k[1], first, n))
        tris = sum(int(cat.get(r[0], {}).get("tris", 100)) for r in by[k])
        chunk_stats.append({"chunk": list(k), "placements": n, "tris_est": tris})
        first += n
    b.write(struct.pack("<I", len(o.recs)))
    for k in keys:
        for (p, i, j, lv, rot, flags, mnt, pal_v, ep) in by[k]:
            b.write(struct.pack("<HBBBBB", pid[p], i, j, lv, (rot & 3) | (flags & 12) | ((mnt & 15) << 4),
                                (pal_v & 15) | ((ep & 15) << 4)))
    b.write(struct.pack("<H", len(units)))
    for u in units:
        b.write(struct.pack("<BBBH", u["use"], min(u["homes"], 255), min(u["floors"], 255), min(u["cells"], 65535)))
    b.write(struct.pack("<H", len(doors)))
    for (u, c, k, rot, e) in doors:
        b.write(struct.pack("<HBBBBB", u, c[0], c[1], k, rot, e))
    t = L.travel
    b.write(struct.pack("<ffff", t[0], t[1], t[2], t[3]))
    b.write(struct.pack("<I", len(foliage)))
    for (sp, x, y, z, rot, sc) in foliage:
        b.write(struct.pack("<BhhBBB", sid[sp], int(round(x * 10)), int(round(z * 10)),
                            max(0, min(255, int(round(y * 4)))), int(round(rot / math.tau * 256)) & 255,
                            max(0, min(255, int(round(sc * 64))))))
    raw = b.getvalue()
    gz = gzip.compress(raw, 9, mtime=0)
    open(out_bin, "wb").write(gz)
    stats["bin_raw"] = len(raw)
    stats["bin_gz"] = len(gz)
    stats["chunks"] = len(keys)
    stats["max_chunk_placements"] = max(c["placements"] for c in chunk_stats)
    stats["max_chunk_tris_est"] = max(c["tris_est"] for c in chunk_stats)
    stats["pieces_used"] = len(used)
    # the readable twin
    lv = []
    for k in range(LEVELS):
        if not L.occ[:, :, k].any():
            continue
        rows = []
        for i in range(L.nx):
            rows.append("".join("#" if L.occ[i, j, k] else "." for j in range(L.nz)))
        lv.append({"level": k, "rows": rows})
    plan_rows = ["".join("o.,~bgpMPGLCrhA"[int(L.plan[i, j])] for j in range(L.nz)) for i in range(L.nx)]
    doc = {
        "version": 2, "island": L.isl["id"], "name": L.isl.get("name"), "civ": civ.id, "civ_name": civ.name,
        "variant": getattr(civ, "city", None), "seed": L.seed,
        "frame": {"x0": L.x0, "z0": L.z0, "cell": CELL, "storey": STOREY, "nx": L.nx, "nz": L.nz, "levels": LEVELS,
                  "chunk": CHUNK},
        "palettes": kpal, "pieces": used, "mounts": {p: ["cell", "face", "corner"][mounts[p]] for p in used}, "foliage_species": species,
        "palette_mode": "kit_variant", "lights": getattr(L, "lights", []),
        "travel": L.travel, "landmark": list(getattr(L, "landmark", ()) or ()),
        "units": units, "doors": [[u, c[0], c[1], k, rot, e] for (u, c, k, rot, e) in doors],
        "anchors": o.anchors, "walk": L.walk,
        "pads": [{"x": p["x"], "z": p["z"], "yaw": p.get("yaw", 0.0), "y": round(L.deck_y(p["x"], p["z"]), 2)}
                 for p in L.isl.get("pads", [])],
        "stats": stats, "chunks": chunk_stats, "notes": L.notes,
        "plan_legend": dict(zip("o.,~bgpMPGLCrhA", PLAN_NAMES)), "plan": plan_rows, "levels": lv,
    }
    json.dump(doc, open(out_json, "w"), separators=(",", ":"), default=lambda v: v.item() if hasattr(v, "item") else str(v))
