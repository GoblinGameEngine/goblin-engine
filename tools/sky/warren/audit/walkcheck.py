"""walkcheck.py -- the walk check: the player's capsule (walksim) along every walk-graph edge, both ways, then a BFS
from the travel point to every door over the edges the capsule passes, the way the game would experience it.

Edge kinds (the twin's walk graph, units.walk_graph):
  cell   neighbouring cells (3 m)                       -- tested
  long   longer than a cell: court edges (a door's outside node straight to the house's court) and roof planks
                                                        -- tested (they cross houses: they fail)
  core   a stair core (same x, z; a storey up)           -- islanders only: not walkable, not tested
  ladder a roof step a storey up                         -- islanders only (the player climbs ramps only)
Per directed edge: strict (sphere-contact physics) and, where strict fails, lenient (<= 6 cm lips over a ramp's plane
taken): ok | risky (lenient only) | blocked | fell | drop (a snap-down > 0.3 m) | height (arrived at the wrong level).
Doors: every (cell, face, storey) of the twin's doors; the node outside it (the outside cell's node at the door's
storey); the entry walk from that node 0.9 m into the room."""
import collections

import numpy as np

import common as C
import walksim

FACE_DIR = [(0, 1), (1, 0), (0, -1), (-1, 0)]          # door rot (face mount) -> (di, dj) out of the house cell


def edges_of(side):
    w = side["walk"]
    N = np.array([n[:3] for n in w["nodes"]], float)
    kinds = [n[3] for n in w["nodes"]]
    E = np.array(w["edges"], int).reshape(-1, 2)
    h = np.hypot(N[E[:, 0], 0] - N[E[:, 1], 0], N[E[:, 0], 2] - N[E[:, 1], 2])
    dy = np.abs(N[E[:, 0], 1] - N[E[:, 1], 1])
    kind = np.full(len(E), "cell", object)
    kind[h > 3.2] = "long"
    kind[(h < 0.5) & (dy > 0.5)] = "core"
    roofy = np.array([kinds[a].startswith("roof") or kinds[b].startswith("roof") for a, b in E], bool)
    kind[roofy & (dy > 1.5) & (h < 3.2)] = "ladder"
    return N, kinds, E, kind


def doors_of(side):
    fr = side["frame"]
    seen = {}
    for k, d in enumerate(side["doors"]):
        key = (int(d[1]), int(d[2]), int(d[3]), int(d[4]) & 3)
        seen.setdefault(key, k)
    out = []
    for (i, j, lv, rot), k in seen.items():
        di, dj = FACE_DIR[rot]
        c = np.array([fr["x0"] + 3.0 * i + 1.5, 3.2 * lv, fr["z0"] + 3.0 * j + 1.5])
        out.append({"door": k, "cell": (i, j, lv), "rot": rot, "out_cell": (i + di, j + dj), "centre": c,
                    "dir": np.array([di, 0.0, dj])})
    return out


def run(g, R, soft=walksim.SOFT, log=None):
    side = g.W["side"]
    N, nkind, E, kind = edges_of(side)
    test = np.nonzero((kind == "cell") | (kind == "long"))[0]
    A = np.concatenate([N[E[test, 0]], N[E[test, 1]]])
    B = np.concatenate([N[E[test, 1]], N[E[test, 0]]])
    eid = np.concatenate([test, test])
    fwd = np.concatenate([np.ones(len(test), bool), np.zeros(len(test), bool)])
    r1 = walksim.walk_edges(R, A, B, soft=0.0)
    res = {k: np.array(v, copy=True) for k, v in r1.items()}
    status = np.where(res["ok"], "ok", res["why"]).astype(object)
    fail = np.nonzero(~res["ok"])[0]
    if len(fail):
        r2 = walksim.walk_edges(R, A[fail], B[fail], soft=soft)
        ok2 = r2["ok"]
        status[fail[ok2]] = "risky"
        # (what the strict model stopped on stays the reported spot; a lenient failure replaces it)
        bad = fail[~ok2]
        for key in ("why", "where", "prim", "block_why"):
            res[key][bad] = r2[key][~ok2]
        status[bad] = r2["why"][~ok2]
    # directed passability
    nn = len(N)
    adj = [[] for _ in range(nn)]
    adj_safe = [[] for _ in range(nn)]
    for q in range(len(eid)):
        a, b = (E[eid[q], 0], E[eid[q], 1]) if fwd[q] else (E[eid[q], 1], E[eid[q], 0])
        if status[q] in ("ok", "risky", "drop"):
            adj[a].append(b)
        if status[q] in ("ok", "drop"):
            adj_safe[a].append(b)
    tr = np.array(side["travel"][:3], float)
    start = int(np.argmin(np.hypot(N[:, 0] - tr[0], N[:, 2] - tr[2]) + np.abs(N[:, 1] - tr[1]) * 10))
    reach = _bfs(adj, start)
    reach_safe = _bfs(adj_safe, start)
    # the graph's own reach (every edge), for "unreachable because of geometry" vs "not on the graph"
    gadj = [[] for _ in range(nn)]
    for a, b in E:
        gadj[a].append(b)
        gadj[b].append(a)
    reach_graph = _bfs(gadj, start)
    # doors
    doors = doors_of(side)
    cell_nodes = collections.defaultdict(list)
    for k in range(nn):
        if nkind[k] in ("ground", "stair", "blocked") or True:
            cell_nodes[g.ij(N[k])].append(k)
    entryA, entryB, dmeta = [], [], []
    for d in doors:
        cands = [k for k in cell_nodes.get(d["out_cell"], []) if abs(N[k, 1] - d["centre"][1]) < 0.9]
        if not cands:
            d["node"] = None
            continue
        k = min(cands, key=lambda k: abs(N[k, 1] - d["centre"][1]))
        d["node"] = k
        entryA.append(N[k])
        entryB.append(d["centre"] + d["dir"] * 0.8)
        dmeta.append(d)
    if entryA:
        re = walksim.walk_edges(R, np.array(entryA), np.array(entryB), soft=soft, tol_y=0.35)
        for q, d in enumerate(dmeta):
            # through the doorway = the capsule's axis got 0.5 m past the face (the room behind may have no floor:
            # interiors are shed by kitmap.budget -- reported apart as floor_missing)
            sdep = float(np.dot(re["end"][q] - d["centre"], d["dir"]))
            through = sdep <= 1.0
            d["entry"] = "ok" if through else re["why"][q]
            d["floor_missing"] = bool(through and re["why"][q] == "fell")
            d["entry_where"] = re["where"][q]
            d["entry_prim"] = int(re["prim"][q])
    edges = []
    for q in np.nonzero(status != "ok")[0]:
        e = eid[q]
        a, b = (E[e, 0], E[e, 1]) if fwd[q] else (E[e, 1], E[e, 0])
        edges.append({"edge": int(e), "from": int(a), "to": int(b), "kind": kind[e], "status": status[q],
                      "where": res["where"][q], "prim": int(res["prim"][q]), "block_why": int(res["block_why"][q])})
    door_rows = []
    for d in doors:
        k = d.get("node")
        if k is None:
            st = "no node outside"
        elif k not in reach:
            st = "unreachable (graph)" if k not in reach_graph else "unreachable"
        elif d.get("entry") not in ("ok", None):
            st = "entry " + d["entry"]
        elif k not in reach_safe:
            st = "risky"
        else:
            st = "ok"
        d["status"] = st
        door_rows.append(d)
    return {"nodes": N, "node_kind": nkind, "edges_all": E, "edge_kind": kind, "tested": len(test),
            "edge_status": status, "edge_id": eid, "edge_fwd": fwd, "bad_edges": edges, "doors": door_rows,
            "start": start, "reach": reach, "reach_safe": reach_safe, "reach_graph": reach_graph,
            "edge_where": res["where"], "edge_prim": res["prim"]}


def _bfs(adj, s):
    seen = {s: -1}
    q = [s]
    h = 0
    while h < len(q):
        u = q[h]
        h += 1
        for v in adj[u]:
            if v not in seen:
                seen[v] = u
                q.append(v)
    return seen


def blocking_spot(W, d):
    """for an unreachable door: the first failed edge on the graph's own route from the travel point"""
    reach_graph = W["reach_graph"]
    k = d.get("node")
    if k is None or k not in reach_graph:
        return None
    path = []
    u = k
    while u != -1:
        path.append(u)
        u = reach_graph[u]
    path.reverse()
    bad = {(e["from"], e["to"]): e for e in W["bad_edges"]}
    for a, b in zip(path, path[1:]):
        e = bad.get((a, b))
        if e and e["status"] not in ("drop", "risky"):
            return e
    return None
