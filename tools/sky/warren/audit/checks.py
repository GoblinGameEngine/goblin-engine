"""checks.py -- the warren client of meshlib + walksim: every check returns hotspots
{"check", "kind", "at": [x, y, z], "cell": [i, j, level], "pieces": [ids], "value"} (world = the island frame).

  holes        walk_floor: rays down at every walk node (5 points) must meet collision at the node's height
               roof: rays down over every column's top room (render mesh) must stop at its roof, not inside
  cracks       rays from 0.4 m outside every exterior room face toward the room (render mesh) must hit the facade;
               openings (doorways, arches, passages, shopfronts, gates) are skipped in their opening
  manifold     kit pieces' topology (open / non-manifold / inconsistent edges, inside-out parts) as placed here;
               duplicate triangles across placements (welded at 1 mm)
  zfight       same-facing coplanar overlapping render faces of different placements
  floating     cell- and corner-mounted pieces with nothing within 8 cm under their lowest points
  intrusion    pass: collision of other pieces inside a walk-through piece's pass volume
               clearance: collision inside the capsule's standing volume at a walk node
               render_clear: render triangles of other pieces inside that volume (visual clipping)
               pierce: render faces of one placement pierced > 2 cm by another's edges
  walk         walkcheck: edges blocked / risky / dropping, doors unreachable, with the blocking spot
"""
import collections

import numpy as np

import assemble as A
import common as C
import meshlib as M
import walkcheck as WC

OPENING_WORDS = ("door", "arch", "gate", "portal", "pend", "shopfront", "passage", "moon", "open", "arcade", "jetty",
                 "verandah", "veranda", "five_foot", "qilou", "loggia", "porch", "colonnade", "stall")


def hs(g, check, kind, at, pieces=(), value=None):
    at = [round(float(v), 2) for v in at]
    i, j = g.ij(at)
    return {"check": check, "kind": kind, "at": at, "cell": [i, j, int(np.floor((at[1] + 0.05) / C.STOREY))],
            "pieces": sorted(set(p for p in pieces if p)), "value": value}


def is_opening(pid, spec):
    if spec.get("pass") or spec.get("kind") == "passage":
        return True
    return any(w in pid for w in OPENING_WORDS)


def levels(side):
    """(i, j, k) room cells from the twin's level strings"""
    out = set()
    for lv in side.get("levels", []):
        k = lv["level"]
        for i, row in enumerate(lv["rows"]):
            for j, ch in enumerate(row):
                if ch == "#":
                    out.add((i, j, k))
    return out


# ------------------------------------------------------------------ holes
def holes_walk(g, R, W):
    N = W["nodes"]
    kinds = W["node_kind"]
    # (a stair core's nodes -- one a storey inside a house, joined by vertical "core" edges -- are the islanders'
    # virtual stairs: no floor is expected there)
    core = set()
    for (a, b), kd in zip(W["edges_all"], W["edge_kind"]):
        if kd == "core":
            for x in (int(a), int(b)):
                q = (N[x, 1] - 0.1) / C.STOREY
                if abs(q - round(q)) < 0.01:
                    core.add(x)              # (units.walk_graph: a core node stands at k * 3.2 + 0.1)
    sel = [k for k in range(len(N)) if kinds[k] in ("ground", "stair", "roof") and k not in core]
    off = np.array([[0, 0], [0.6, 0], [-0.6, 0], [0, 0.6], [0, -0.6]])
    pts = np.repeat(N[sel][:, None, [0, 2]], 5, 1) + off[None]
    y0 = np.repeat(N[sel][:, 1], 5)
    t, prim, n = R.cast(np.stack([pts[..., 0].ravel(), y0 + 0.5, pts[..., 1].ravel()], 1),
                        np.tile([0, -1.0, 0], (len(y0), 1)), 1.5)
    hy = 0.5 + y0 - t
    out = []
    for q, k in enumerate(sel):
        h = hy[q * 5:(q + 1) * 5]
        st = kinds[k] == "stair"
        tol = 0.9 if st else 0.12
        bad = ~np.isfinite(h) | (np.abs(h - N[k, 1]) > tol)
        if bad[0] or bad.sum() >= 3:
            j = int(np.argmax(bad))
            p = [pts[q, j, 0], N[k, 1], pts[q, j, 1]]
            if not np.isfinite(h[j]):
                out.append(hs(g, "holes", "no_floor", p, [], "nothing within 1 m under the walk node"))
            else:
                out.append(hs(g, "holes", "floor_off", p, [g.label(prim[q * 5 + j], p)],
                              round(float(h[j] - N[k, 1]), 2)))
    return out


def holes_roof(g, RR):
    side = g.W["side"]
    rooms = levels(side)
    top = {}
    for i, j, k in rooms:
        top[(i, j)] = max(top.get((i, j), -1), k)
    if not top:
        return []
    cells = np.array([(i, j, k) for (i, j), k in top.items()])
    g4 = np.array([(a, b) for a in (-1.1, -0.37, 0.37, 1.1) for b in (-1.1, -0.37, 0.37, 1.1)])
    x = g.x0 + C.CELL * cells[:, 0] + 1.5
    z = g.z0 + C.CELL * cells[:, 1] + 1.5
    roof_y = C.STOREY * (cells[:, 2] + 1)
    o = np.stack([np.repeat(x, 16) + np.tile(g4[:, 0], len(x)), np.repeat(roof_y + 6.0, 16),
                  np.repeat(z, 16) + np.tile(g4[:, 1], len(x))], 1)
    t, prim, _ = RR.cast(o, np.tile([0, -1.0, 0], (len(o), 1)), 30.0)
    hy = o[:, 1] - t
    lowest = np.repeat(roof_y - 0.6, 16)
    bad = ~np.isfinite(hy) | (hy < lowest)
    out = []
    bc = collections.Counter(np.nonzero(bad)[0] // 16)
    for c, n in bc.items():
        if n < 1:
            continue
        q = c * 16 + int(np.argmax(bad[c * 16:(c + 1) * 16]))
        p = [o[q, 0], roof_y[c], o[q, 2]]
        gq = int(g.gp[prim[q]]) if prim[q] >= 0 else -1
        lab = g.pid(gq) if gq >= 0 else ("deck" if prim[q] >= 0 else None)
        out.append(hs(g, "holes", "roof_open", p, [lab], "%d/16 rays fall into the room" % n))
    return out


# ------------------------------------------------------------------ cracks
FACE = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def cracks(g, RR, K):
    side = g.W["side"]
    rooms = levels(side)
    recs = g.recs
    walls = collections.defaultdict(list)                   # (i, j, k, rot) -> piece ids on that face
    for n in np.nonzero(g.P["mount"] == 1)[0]:
        pid = g.pid(n)
        walls[(int(recs["i"][n]), int(recs["j"][n]), int(recs["k"][n]), int(recs["rf"][n] & 3))].append(pid)
    O, D, L_, meta = [], [], [], []
    lat = np.array([-1.47, -1.0, -0.5, 0.0, 0.5, 1.0, 1.47])
    hts = np.array([0.35, 1.2, 2.0, 2.9])
    for (i, j, k) in rooms:
        for rot, (di, dj) in enumerate(FACE):
            if (i + di, j + dj, k) in rooms:
                continue
            allp = walls.get((i, j, k, rot), [])
            # (only walls close a face: an overlay or sign hung there alone leaves it bare)
            pcs = [p for p in allp if K.P.get(p, {}).get("kind") in ("wall", "passage")]
            openf = any(is_opening(p, K.P.get(p, {})) for p in pcs)
            # (rays start outside what the face's pieces put out over it -- a jetty storey, an oriel, a bay window --
            # not inside it)
            out_z = max([0.4] + [float(K.aabb[p][1][2]) + 0.1 for p in allp if p in K.aabb])
            out_z = min(out_z, 2.4)
            cx = g.x0 + C.CELL * i + 1.5
            cz = g.z0 + C.CELL * j + 1.5
            nrm = np.array([di, 0.0, dj])
            tang = np.array([dj, 0.0, -di])
            for h in hts:
                for l in lat:
                    if openf and abs(l) < 1.2 and h < 2.6:
                        continue
                    p = np.array([cx, C.STOREY * k + h, cz]) + nrm * (1.5 + out_z) + tang * l
                    O.append(p)
                    D.append(-nrm)
                    L_.append(out_z + 1.0)
                    meta.append((i, j, k, rot, l, h, tuple(pcs), out_z))
    if not O:
        return []
    O = np.array(O)
    D = np.array(D)
    t, prim, _ = RR.cast(O, D, np.array(L_))
    miss = ~np.isfinite(t)
    by = collections.defaultdict(list)
    for q in np.nonzero(miss)[0]:
        i, j, k, rot, l, h, pcs, oz = meta[q]
        by[(i, j, k, rot)].append((l, h, pcs, O[q] + D[q] * oz))
    out = []
    for key, v in by.items():
        pcs = v[0][2]
        seam = all(abs(l) > 1.4 for l, *_ in v)
        kind = "missing_wall" if not pcs else ("seam" if seam else "see_through")
        if kind == "missing_wall":
            i, j, k, rot = key
            di, dj = FACE[rot]
            if (i + 2 * di, j + 2 * dj, k) in rooms:
                kind = "culled_slot"            # (a 1-cell slot between two rooms: civ SPEC cull_slots leaves it bare)
            elif any((i + di, j + dj, kk) in rooms for kk in range(k + 1, k + 12)):
                kind = "culled_shaft"           # (into a light well / under rooms: e.g. kowloon_walled.facade "shaft")
        if kind == "missing_wall":
            # (pick.py leaves a face bare where the room is below the next column's ground level -- "buried": but
            # the deck is a surface, not rock: the room looks into the island's hollow under the deck)
            p0 = v[0][3]
            if g.deck.y(p0[0] + FACE[key[3]][0] * 0.5, p0[2] + FACE[key[3]][1] * 0.5) > p0[1]:
                kind = "buried_face"
        out.append(hs(g, "cracks", kind, v[0][3], list(pcs), "%d rays through" % len(v)))
    return out


# ------------------------------------------------------------------ manifold / duplicates
_TOPO = {}


def manifold(g, K):
    out = []
    used = collections.Counter(g.ids[p] for p in g.recs["p"])
    for pid, n in used.items():
        if pid not in K.mesh:
            continue
        if pid not in _TOPO:
            _TOPO[pid] = M.topology(K.mesh[pid])
        t = _TOPO[pid]
        if t["nonmanifold_edges"] or t["inconsistent_edges"] or t["inside_out"] or t["dup_faces"]:
            n0 = int(np.nonzero(np.array([g.ids[p] for p in g.recs["p"]]) == pid)[0][0])
            out.append(hs(g, "manifold", "kit_piece", g.P["t"][n0], [pid],
                          {"placements": n, "nonmanifold": t["nonmanifold_edges"], "inconsistent": t["inconsistent_edges"],
                           "inside_out": t["inside_out"], "dup_faces": t["dup_faces"], "open": t["open_edges"]}))
    return out


STRUCT = ("wall", "corner", "edge", "roof", "slab", "ground", "crown", "tower", "water_edge", "ceiling")


def piece_pairs(g, K, RS, gp):
    """duplicates, z-fighting and piercing between placements whose boxes overlap (pairs.py: once per
    configuration).  z-fights count only where they can be seen (a view ray from 0.3 m in front meets nothing
    but the pair); piercing counts where it shows AND a non-structural piece is involved (wall/corner/roof joints
    overlap by construction -- counted in stats as joints)"""
    import pairs as PR
    r = PR.run(g, K)
    out = []
    kind = lambda n: K.P.get(g.pid(n), {}).get("kind", "")
    for a, b, n in r["dup"]:
        out.append(hs(g, "manifold", "dup_across", g.P["t"][a], [g.pid(a), g.pid(b)], {"tris": int(n)}))
    zf = r["zf"]
    vis = M.visible([z[2] for z in zf], [z[3] for z in zf], RS, gp, [{z[0], z[1]} for z in zf]) if zf else []
    seen = {}
    zagg = collections.defaultdict(lambda: [0, 0.0])
    pe = g.recs["pe"] & 15
    same_look = 0
    for z, v in zip(zf, vis):
        if not v:
            continue
        if z[5] == z[6] and pe[z[0]] == pe[z[1]]:
            same_look += 1                      # (one material, one palette: the fight can't be seen)
            continue
        k = (z[0], z[1])
        if k not in seen:
            seen[k] = z
        e = zagg[tuple(sorted((g.pid(z[0]), g.pid(z[1]))))]
        e[0] += 1
        e[1] += z[4]
    for (a, b), z in seen.items():
        out.append(hs(g, "zfight", "coplanar", z[2], [g.pid(a), g.pid(b)], round(float(z[4]), 3)))
    pi = r["pi"]
    # (an overlay or sign hung on a wall sits in it by construction: into_room catches one that shows inside)
    HUNG = ("overlay", "sign")
    cand = [p for p in pi if (kind(p[0]) not in STRUCT or kind(p[1]) not in STRUCT)
            and not (kind(p[0]) in HUNG and kind(p[1]) in STRUCT or kind(p[1]) in HUNG and kind(p[0]) in STRUCT)]
    joints = len(pi) - len(cand)          # (structural joints + hung overlays)
    vis = M.visible([p[2] for p in cand], [p[3] for p in cand], RS, gp, [{p[0], p[1]} for p in cand]) if cand else []
    pseen = {}
    pagg = collections.defaultdict(int)
    for p, v in zip(cand, vis):
        if not v:
            continue
        k = (p[0], p[1])
        if k not in pseen:
            pseen[k] = p
            pagg[tuple(sorted((g.pid(p[0]), g.pid(p[1]))))] += 1
    for (a, b), p in pseen.items():
        out.append(hs(g, "intrusion", "pierce", p[2], [g.pid(a), g.pid(b)],
                      {"pierced": g.pid(p[5]), "edges": round(float(p[4]), 1)}))
    stats = {"pairs": r["pairs"], "configs": r["configs"], "back_to_back_faces": r["b2b"], "zfight_samples": len(zf), "zfight_visible_pairs": len(seen),
             "zfight_same_look_samples": same_look,
             "zfight_by_pieces": sorted(([list(k), v[0], round(v[1], 2)] for k, v in zagg.items()),
                                        key=lambda x: -x[2])[:25],
             "pierce_samples": len(pi), "pierce_joint_samples": joints, "pierce_visible_pairs": len(pseen),
             "pierce_by_pieces": sorted(([list(k), v] for k, v in pagg.items()), key=lambda x: -x[1])[:25]}
    return out, stats


# ------------------------------------------------------------------ floating
GROUNDED = ("stair", "decor", "cell", "tower", "water_edge")   # (paving: see cracks/riser_gap)


def floating(g, K, RS, gp, RI):
    """isolated: a placement touching nothing (its box grown 3 cm meets no other piece's render triangle, nor the
    deck) -- hanging in the air; unsupported: a piece standing on the ground (kinds GROUNDED, cell mount) with
    nothing within 8 cm under its lowest vertices"""
    P = g.P
    out = []
    lo_all = np.full((len(g.recs), 3), np.inf)
    hi_all = np.full((len(g.recs), 3), -np.inf)
    v = g.rtri.reshape(-1, 3)
    src = np.repeat(g.rsrc, 3)
    np.minimum.at(lo_all, src, v)
    np.maximum.at(hi_all, src, v)
    # (by boxes: a placement whose box, grown 3 cm, meets no other placement's box and not the deck can touch
    # nothing -- conservative: a piece whose box overlaps a neighbour's but whose triangles don't is not caught)
    from scipy.spatial import cKDTree
    okb = np.isfinite(lo_all[:, 0])
    ids = np.nonzero(okb)[0]
    lo, hi = lo_all[ids] - 0.03, hi_all[ids] + 0.03
    cen = (lo + hi) / 2
    rad = np.linalg.norm(hi - lo, axis=1).max() / 2 + 0.01
    tree = cKDTree(cen)
    pairs = tree.query_pairs(2 * rad, output_type="ndarray")
    a_, b_ = pairs[:, 0], pairs[:, 1]
    ov = np.all((lo[a_] <= hi[b_]) & (lo[b_] <= hi[a_]), 1)
    touched = np.zeros(len(ids), bool)
    touched[a_[ov]] = True
    touched[b_[ov]] = True
    dy = g.deck.y(np.r_[cen[:, 0], lo[:, 0], hi[:, 0]], np.r_[cen[:, 2], lo[:, 2], hi[:, 2]]).reshape(3, -1)
    on_deck = ((dy >= lo[:, 1] - 0.12) & (dy <= hi[:, 1])).any(0)
    for q in np.nonzero(~touched & ~on_deck)[0]:
        n = ids[q]
        out.append(hs(g, "floating", "isolated", cen[q], [g.pid(n)], "its box touches nothing within 3 cm"))
    # standing pieces: something under their lowest vertices
    sel = [n for n in range(len(g.recs)) if P["mount"][n] == 0 and K.P.get(g.pid(n), {}).get("kind") in GROUNDED
           and g.pid(n) in K.mesh]
    O, who = [], []
    for n in sel:
        pid = g.pid(n)
        m = K.mesh[pid]
        vv = m.reshape(-1, 3)
        low = m[(m[:, :, 1].min(1) < vv[:, 1].min() + 0.02)]
        if not len(low):
            continue
        c = low.mean(1)                          # (the lowest faces' centres: on the geometry, not in a gap)
        if len(c) > 6:
            c = c[np.linspace(0, len(c) - 1, 6).astype(int)]
        c[:, 1] = vv[:, 1].min()
        O.append(A._nomirror(P, n, c))
        who.append(np.full(len(c), n))
    if O:
        O = np.concatenate(O)
        who = np.concatenate(who)
        O[:, 1] -= 0.004
        t, prim, _ = RS.cast(O, np.tile([0, -1.0, 0], (len(O), 1)), 0.08)
        hit = np.isfinite(t)
        got = collections.Counter()
        tot = collections.Counter()
        for n, h in zip(who, hit):
            got[n] += int(h)
            tot[n] += 1
        for n in tot:
            if got[n] == 0:
                out.append(hs(g, "floating", "unsupported", O[who == n][0], [g.pid(n)], "nothing within 8 cm below"))
    return out


# ------------------------------------------------------------------ intrusion
def _box_rays(lo, hi, axis, n=5):
    """rays through an axis-aligned box along `axis`, on an n x n grid of its cross-section (inset 1 cm)"""
    o = [k for k in range(3) if k != axis]
    u = np.linspace(lo[o[0]] + 0.01, hi[o[0]] - 0.01, n)
    v = np.linspace(lo[o[1]] + 0.01, hi[o[1]] - 0.01, n)
    U, V = np.meshgrid(u, v, indexing="ij")
    O = np.zeros((n * n, 3))
    O[:, o[0]] = U.ravel()
    O[:, o[1]] = V.ravel()
    O[:, axis] = lo[axis]
    D = np.zeros((n * n, 3))
    D[:, axis] = 1.0
    return O, D, hi[axis] - lo[axis]


def intrusions(g, K, W, R, RS, gp):
    """rays through each pass volume (along the piece's own z) and through the capsule's standing volume at every
    ground walk node (down from its top, and across): any hit is something inside (collision: blocks; render:
    shows through the player)"""
    out = []
    P = g.P
    O, D, L, who, kind = [], [], [], [], []
    for n in range(len(g.recs)):
        pid = g.pid(n)
        ps = K.P.get(pid, {}).get("pass")
        if not ps:
            continue
        lo, hi = np.array(ps[0], float) + 0.02, np.array(ps[1], float) - 0.02
        lo[1] = max(lo[1], 0.10)                 # (a step's foot is allowed)
        c = A._nomirror(P, n, np.array([lo, hi]))
        wlo, whi = c.min(0), c.max(0)
        ax = 0 if (int(P["rot"][n]) & 1) else 2
        o, d, ln = _box_rays(wlo, whi, ax)
        O.append(o)
        D.append(d)
        L.append(np.full(len(o), ln))
        who.append(np.full(len(o), n))
        kind.append(np.zeros(len(o), int))
    N = W["nodes"]
    for k in np.nonzero(np.array([x == "ground" for x in W["node_kind"]]))[0]:
        lo = N[k] + [-0.16, 0.12, -0.16]
        hi = N[k] + [0.16, 1.42, 0.16]
        for ax in (1, 0, 2):
            o, d, ln = _box_rays(lo, hi, ax, 3)
            if ax == 1:
                o[:, 1], d[:, 1] = hi[1], -1.0
            O.append(o)
            D.append(d)
            L.append(np.full(len(o), ln))
            who.append(np.full(len(o), k))
            kind.append(np.ones(len(o), int))
    if not O:
        return out
    O, D, L, who, kind = (np.concatenate(x) for x in (O, D, L, who, kind))
    t, prim, _ = R.cast(O, D, L)
    tr, primr, _ = RS.cast(O, D, L)
    hits = collections.defaultdict(collections.Counter)
    rhits = collections.defaultdict(collections.Counter)
    for q in np.nonzero(np.isfinite(t))[0]:
        src = int(g.csrc[prim[q]])
        if kind[q] == 0 and src == who[q]:
            continue
        hits[(kind[q], who[q])][g.label(prim[q], O[q] + D[q] * t[q])] += 1
    for q in np.nonzero(np.isfinite(tr) & (kind == 1))[0]:
        gq = int(gp[primr[q]])
        rhits[who[q]][g.pid(gq) if gq >= 0 else "deck"] += 1
    for (kd, w), c in hits.items():
        if kd == 0:
            pid = g.pid(w)
            ps = K.P[pid]["pass"]
            cc = A._nomirror(P, w, np.array(ps)).mean(0)
            out.append(hs(g, "intrusion", "pass", cc, [pid] + list(c), dict(c)))
        else:
            out.append(hs(g, "intrusion", "clearance", N[w] + [0, 0.7, 0], list(c), dict(c)))
    for w, c in rhits.items():
        out.append(hs(g, "intrusion", "render_clear", N[w] + [0, 0.7, 0], list(c), dict(c)))
    return out


# ------------------------------------------------------------------ walk
def walk(g, W):
    out = []
    for e in W["bad_edges"]:
        lab = g.label(e["prim"], e["where"]) if e["prim"] >= 0 else None
        if e["kind"] == "long":
            out.append(hs(g, "walk", "virtual_" + e["status"], e["where"], [lab],
                          {"edge": e["edge"], "from": W["nodes"][e["from"]].round(2).tolist(),
                           "to": W["nodes"][e["to"]].round(2).tolist(), "kind": e["kind"]}))
            continue
        out.append(hs(g, "walk", "edge_" + e["status"], e["where"], [lab],
                      {"edge": e["edge"], "from": W["nodes"][e["from"]].round(2).tolist(),
                       "to": W["nodes"][e["to"]].round(2).tolist(), "kind": e["kind"]}))
    for d in W["doors"]:
        st = d["status"]
        if st == "ok":
            continue
        spot = WC.blocking_spot(W, d) if st.startswith("unreachable") else None
        at = spot["where"] if spot else (d.get("entry_where") if st.startswith("entry") else d["centre"])
        lab = g.label(spot["prim"], spot["where"]) if spot and spot["prim"] >= 0 else (
            g.label(d["entry_prim"], d["entry_where"]) if st.startswith("entry") and d.get("entry_prim", -1) >= 0
            else None)
        out.append(hs(g, "walk", "door_" + st.replace(" ", "_").replace("(", "").replace(")", ""), at, [lab],
                      {"door": d["door"], "cell": list(d["cell"]), "rot": d["rot"]}))
    for d in W["doors"]:
        if d.get("floor_missing"):
            out.append(hs(g, "holes", "room_floor_missing", d["centre"] + d["dir"] * 0.5, [],
                          {"door": d["door"], "cell": list(d["cell"])}))
    return out


# ------------------------------------------------------------------ into rooms / riser gaps
def into_room(g, K, RS, gp):
    """something poking through a wall into the room behind it: rays along each exterior wall's inner face (3 cm
    inside it, 5 heights) meeting a piece that is neither the room's furniture nor its walls/floor/ceiling"""
    side = g.W["side"]
    rooms = levels(side)
    recs = g.recs
    wall_t = {}
    for n in np.nonzero(g.P["mount"] == 1)[0]:
        pid = g.pid(n)
        if K.P.get(pid, {}).get("kind") == "wall" and pid in K.aabb:
            key = (int(recs["i"][n]), int(recs["j"][n]), int(recs["k"][n]), int(recs["rf"][n] & 3))
            wall_t[key] = max(wall_t.get(key, 0.0), -float(K.aabb[pid][0][2]))
    O, D, L, meta = [], [], [], []
    for (i, j, k, rot), t in wall_t.items():
        if (i, j, k) not in rooms:
            continue
        di, dj = FACE[rot]
        nrm = np.array([di, 0.0, dj])
        tang = np.array([dj, 0.0, -di])
        cx = g.x0 + C.CELL * i + 1.5
        cz = g.z0 + C.CELL * j + 1.5
        ins = 1.5 - t - 0.03
        side_t = 0.65
        for h in (0.3, 1.0, 1.7, 2.4, 2.95):
            o = np.array([cx, C.STOREY * k + h, cz]) + nrm * ins - tang * (1.5 - side_t)
            O.append(o)
            D.append(tang)
            L.append(2 * (1.5 - side_t))
            meta.append((i, j, k, rot))
    if not O:
        return []
    O, D, L = np.array(O), np.array(D), np.array(L)
    t, prim, _ = RS.cast(O, D, L)
    out = {}
    OK_KINDS = ("interior", "wall", "slab", "ceiling", "corner", "ground", "roof", "stair")
    for q in np.nonzero(np.isfinite(t))[0]:
        gq = int(gp[prim[q]])
        if gq < 0:
            continue
        pid = g.pid(gq)
        if K.P.get(pid, {}).get("kind") in OK_KINDS:
            continue
        key = meta[q] + (pid,)
        if key not in out:
            out[key] = hs(g, "intrusion", "into_room", O[q] + D[q] * t[q], [pid],
                          "pokes into room (%d,%d,%d) through its wall" % meta[q][:3])
    return list(out.values())


def riser_gaps(g, RS, W):
    """where a walk cell stands higher than its neighbour (> 6 cm), the face between them must be closed (a skirt,
    a plinth, a riser): a ray from the lower cell toward the higher one, under its top, must hit"""
    N = W["nodes"]
    kinds = W["node_kind"]
    cell = {}
    for k in range(len(N)):
        if kinds[k] == "ground":
            cell.setdefault(g.ij(N[k]), []).append(k)
    O, D, meta = [], [], []
    for (i, j), ks in cell.items():
        for di, dj in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            for a in ks:
                for b in cell.get((i + di, j + dj), []):
                    dy = N[b, 1] - N[a, 1]
                    if dy < 0.06 or dy > 3.0:
                        continue
                    for l in (-1.0, 0.0, 1.0):
                        p = np.array([g.x0 + C.CELL * i + 1.5 + di * 1.1 + dj * l, N[a, 1] + min(dy * 0.5, 0.3),
                                      g.z0 + C.CELL * j + 1.5 + dj * 1.1 + di * l])
                        O.append(p)
                        D.append([di, 0.0, dj])
                        meta.append((i, j, i + di, j + dj, round(float(dy), 2)))
    if not O:
        return []
    t, prim, _ = RS.cast(np.array(O), np.array(D), 0.8)
    out = {}
    for q in np.nonzero(~np.isfinite(t))[0]:
        k = meta[q][:4]
        if k not in out:
            out[k] = hs(g, "cracks", "riser_gap", np.array(O[q]) + np.array(D[q]) * 0.4, [],
                        "open %.2f m step from (%d,%d) up to (%d,%d)" % ((meta[q][4],) + meta[q][:4]))
    return list(out.values())
