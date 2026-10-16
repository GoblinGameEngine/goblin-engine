"""walknet.py -- the walk network, BUILT rather than repaired (2026-10-15, after the in-game walk: stairs are climbed only
along their axis, a lip of more than 0.3 m stops the player).

The ground is laid out path by path from the arrival point.  Every cell of the open ground is FREE until a path takes it;
then it is FIXED -- flat paving at q quarters (q >= its deck: fill, never cut), or a stair (steps_up: 2 quarters, rising
toward FACE[rot]) whose foot behind and landing before it are flat cells of the same path.  A path only ever takes free
cells or walks over fixed ones exactly as they are, so everything fixed stays joined to the arrival point: the network
is connected by construction.

  1. the doors, nearest the arrival first: from each lot's possible entrances (the cell outside a front face, flat at a
     storey's floor; or a stoop -- a stair on that cell rising to the door, its foot on the street behind) a search
     (Dijkstra over (cell, quarters), cost = length + fill) back to the fixed network; the path found is fixed
  2. the public ground no path took: joined the same way where it can be, cheaply; the rest is planted (off the walk)

Then L.q / L.stair / L.stoop / lot["door"] / lot["door_k"] as walk.py's, and walk.check / walk.physical verify it.
"""
import heapq
import os
from collections import deque

from lattice import ARTERY, CIVIC, COURT, GATE, GREEN, LANE, MAIN, PASTURE, PLAZA, RESERVED, RIM, BANK
from walk import FACE, OPP, PUBLIC_W, Q, ROT_OF, base_q, carve, check, rooms_of, walk_cells

MAXF = 8               # the most a path raises a cell over its deck (quarters: 6.4 m)
FILL_W = 0.6           # cost of a quarter of fill per cell
STAIR_C = 2.0          # a stair move's extra cost (a flight is worth some detour)
MAX_POPS = 40000
DOOR_P = float(os.environ.get("DOOR_P", 4.0))           # a path paving the street outside a house at none of its floors (or putting a stair there)


def fronts(L, lot):
    """(house cell, outside cell) pairs a door could open between (walk.doors' rules, without the grading)"""
    fr = [(c, m) for c, m in lot["front"] if m in L.W and L.plan[c] != COURT and rooms_of(L, lot, c)]
    if not fr:
        fr = [(c, (c[0] + d[0], c[1] + d[1])) for c in lot["cells"] for d in FACE.values()
              if (c[0] + d[0], c[1] + d[1]) in L.W and L.plan[c[0] + d[0], c[1] + d[1]] != COURT
              and L.plan[c] != COURT and rooms_of(L, lot, c)]
    if not fr and any(rooms_of(L, lot, c) for c in lot["cells"]):
        # an empty cell of the lot beside walkable ground becomes its entry yard
        for c in lot["cells"]:
            if L.occ[c[0], c[1], int(L.gk[c])] or c in L.W:
                continue
            if not any((c[0] + d[0], c[1] + d[1]) in L.W for d in FACE.values()):
                continue
            L.plan[c] = LANE
            L.W.add(c)
            fr = [(c2, (c2[0] + d[0], c2[1] + d[1])) for c2 in lot["cells"] for d in FACE.values()
                  if (c2[0] + d[0], c2[1] + d[1]) in L.W and L.plan[c2[0] + d[0], c2[1] + d[1]] != COURT
                  and L.plan[c2] != COURT and rooms_of(L, lot, c2)]
            if fr:
                break
    if not fr:
        own = set(lot.get("court") or [])
        fr = [(c, (c[0] + d[0], c[1] + d[1])) for c in lot["cells"] for d in FACE.values()
              if (c[0] + d[0], c[1] + d[1]) in own and (c[0] + d[0], c[1] + d[1]) in L.W
              and L.plan[c] != COURT and rooms_of(L, lot, c)]
    return fr


class Net:
    def __init__(self, L):
        self.L = L
        self.base = {c: base_q(L, c) for c in L.W}
        # under a room (a covered lane, a passage): the paving keeps 2.4 m of headroom
        self.cap = {}
        L.opened = 0
        for c in L.W:
            ks = [k for k in range(int(L.gk[c]) + 1, L.L) if L.occ[c[0], c[1], k]]
            while ks and 4 * ks[0] - 3 < self.base[c] + 2:
                # (a room so low over the lane there is no headroom: the bridge room goes, the lane opens)
                L.clear(c[0], c[1], ks.pop(0))
                L.opened += 1
            if ks:
                self.cap[c] = 4 * ks[0] - 3
        self.fix = {}          # cell -> ("f", q) | ("s", q, rot)
        self.block = set()
        from lattice import WATER
        # (the bank cells beside the water: flat paving only)
        self.bank = set(c for c in L.W if int(L.plan[c]) == BANK or any(
            L.inb(c[0] + d[0], c[1] + d[1]) and int(L.plan[c[0] + d[0], c[1] + d[1]]) == WATER for d in FACE.values()))
        self.yards = []
        self.yard_meta = {}
        self.door_lv = {}      # cell outside a door that could be -> the levels its doors need it at
        # (cells whose paving must be at one height: the street strips behind the market moorings' stations,
        # moorings.py -- flat at the station's floor, or off the walk)
        self.pin = getattr(L, "pin_q", {})
        self.pin_s = getattr(L, "pin_s", {})       # (flat at that height, or a stair rising from it)

    def flat_ok(self, y, q):
        """can y be (or is it) flat paving at q?  -> extra cost, or None"""
        f = self.fix.get(y)
        if f is not None:
            return 0.0 if f == ("f", q) else None
        if y in self.block:
            return None
        if (y in self.pin and q != self.pin[y]) or (y in self.pin_s and q != self.pin_s[y]):
            return None
        b = self.base.get(y)
        if b is None or q < b or q > b + MAXF or q > self.cap.get(y, 99):
            return None
        lv = self.door_lv.get(y)
        # (a cell some house opens on: paved at one of its floors -- or a level a stoop climbs from -- not between)
        return 1.0 + FILL_W * (q - b) + (DOOR_P if lv and q not in lv else 0.0)

    def stair_ok(self, c, q, rot):
        """can c be (or is it) a stair from q rising toward FACE[rot]?"""
        f = self.fix.get(c)
        if f is not None:
            return 0.0 if f == ("s", q, rot) else None
        if c in self.block or c in self.bank or c in self.pin or (c in self.pin_s and q != self.pin_s[c]):
            return None                    # (no flight on a pond bank: kerbs and retaining walls box it in)
        b = self.base.get(c)
        if b is None or q < b or q > b + MAXF or q + 2 > self.cap.get(c, 99):
            return None
        return STAIR_C + FILL_W * (q - b) + (DOOR_P if c in self.door_lv else 0.0)

    def moves(self, x, q):
        """the moves from flat (x, q): (cost, (y, qy), assignment list)"""
        for rot, d in FACE.items():
            y = (x[0] + d[0], x[1] + d[1])
            if y not in self.base:
                continue
            c1 = self.flat_ok(y, q)
            if c1 is not None:
                yield c1, (y, q), ((y, ("f", q)),)
            n = (y[0] + d[0], y[1] + d[1])
            if n not in self.base:
                continue
            # up: x is the foot, y the stair, n the landing
            cs = self.stair_ok(y, q, rot)
            if cs is not None:
                cn = self.flat_ok(n, q + 2)
                if cn is not None:
                    yield cs + cn, (n, q + 2), ((y, ("s", q, rot)), (n, ("f", q + 2)))
            # down: x is the landing, y the stair rising toward x from q - 2, n its foot
            if q >= 2:
                cs = self.stair_ok(y, q - 2, OPP[rot])
                if cs is not None:
                    cn = self.flat_ok(n, q - 2)
                    if cn is not None:
                        yield cs + cn, (n, q - 2), ((y, ("s", q - 2, OPP[rot])), (n, ("f", q - 2)))

    def search(self, starts):
        """starts: [(cost, (cell, q), assignment)] -- Dijkstra until a fixed flat cell (the network) is reached;
        returns the assignments of the path (start's included) or None"""
        heap = []
        best = {}
        prev = {}
        k = 0
        for cost, st, asg in starts:
            if cost < best.get(st, 1e18):
                best[st] = cost
                prev[st] = (None, asg)
                heapq.heappush(heap, (cost, k, st))
                k += 1
        pops = 0
        while heap:
            cost, _, st = heapq.heappop(heap)
            if cost > best.get(st, 1e18):
                continue
            pops += 1
            if pops > MAX_POPS:
                self.why = "pops"
                return None
            x, q = st
            if self.fix.get(x) == ("f", q):
                # reached the network: the path's assignments, back to the start
                out = []
                s = st
                while s is not None:
                    p, asg = prev[s]
                    out.extend(asg)
                    s = p
                return out
            for c, nst, asg in self.moves(x, q):
                nc = cost + c
                if nc < best.get(nst, 1e18):
                    best[nst] = nc
                    prev[nst] = (st, asg)
                    heapq.heappush(heap, (nc, k, nst))
                    k += 1
        self.why = "exhausted %d" % pops
        return None

    def conflicts(self, asg):
        """the cells a path wants two ways"""
        want, bad = {}, set()
        for c, a in asg:
            if (c in want and want[c] != a) or (self.fix.get(c) not in (None, a)):
                bad.add(c)
            want[c] = a
        return bad

    def commit(self, asg):
        """fix a path's cells; False (nothing fixed) when the path wants one free cell two ways"""
        want = {}
        for c, a in asg:
            if c in want and want[c] != a:
                return False
            want[c] = a
        for c, a in want.items():
            f = self.fix.get(c)
            if f is not None and f != a:
                return False
        self.fix.update(want)
        return True


def porch_starts(L, N, lot, fr):
    """search starts through a porch: (c house front cell -> porch, m the street, c2 the house behind, door storey s)
    up: the porch a stair from 4s-2 (the street m at 4s-2, its foot) rising to the door; down: the porch a stair from
    the door's floor 4s rising out to the street m at 4s+2"""
    starts, meta = [], {}
    for c, m in fr:
        dv = (c[0] - m[0], c[1] - m[1])
        c2 = (c[0] + dv[0], c[1] + dv[1])
        if not L.inb(*c2) or int(L.lot[c2]) != lot["id"] or c in L.W:
            continue
        if not any(rooms_of(L, lot, x) for x in lot["cells"] if x != c):
            continue
        rot_in = ROT_OF[dv]
        bc = base_q(L, c)
        for s in rooms_of(L, lot, c2):
            for down in (False, True):
                qs = 4 * s if down else 4 * s - 2           # the stair's foot level
                top_k = s + 1 if down else s                 # rooms cleared up to here (headroom)
                if qs < bc or qs > bc + MAXF or top_k >= L.L or any(
                        L.block[c[0], c[1], k] for k in range(int(L.gk[c]), top_k + 1)):
                    continue
                qm = 4 * s + 2 if down else 4 * s - 2
                cm = N.flat_ok(m, qm)
                if cm is None:
                    continue
                a = (c, ("s", qs, OPP[rot_in] if down else rot_in))
                starts.append((cm + STAIR_C + 3.0, (m, qm), (a, (m, ("f", qm)))))
                meta[(c, a[1][2])] = (c2, OPP[rot_in], s, down)
    return starts, meta


def route_lot(L, N, lot, fr, state):
    """lay the path from one lot's entrance to the network -> True (door set), False, None (no front at all)"""
    from pick import h01
    stoops, doors_of, whys, porches = state["stoops"], state["doors"], state["whys"], N.porches
    if not fr and not any(rooms_of(L, lot, c) for c in lot["cells"]):
        return None
    pref = (LANE, ARTERY, RIM, GATE, RESERVED, MAIN, PLAZA, GREEN, BANK, PASTURE) if lot["use"] != CIVIC else \
        (PLAZA, MAIN, LANE, ARTERY, GATE, RIM, RESERVED, GREEN, BANK, PASTURE)
    def build(frx):
        starts = []
        meta = {}
        for c, m in frx:
            rot = ROT_OF[(m[0] - c[0], m[1] - c[1])]          # house -> street
            pi = (pref.index(L.plan[m]) if L.plan[m] in pref else 9) * 0.3 + h01(L.seed, "door", c, m) * 0.1
            for s in rooms_of(L, lot, c):
                up = (s - int(L.gk[c])) * 1.5
                # flat: the street outside at the floor
                cf = N.flat_ok(m, 4 * s)
                if cf is not None:
                    st = (m, 4 * s)
                    starts.append((cf + pi + up, st, ((m, ("f", 4 * s)),)))
                    meta.setdefault(st, []).append((c, rot, s, None))
                # a stoop: the stair on m rising to the door, its foot b on the street behind
                b = (2 * m[0] - c[0], 2 * m[1] - c[1])
                if b in N.base and 4 * s >= 2:
                    cs = N.stair_ok(m, 4 * s - 2, OPP[rot])
                    cb = N.flat_ok(b, 4 * s - 2)
                    if cs is not None and cb is not None:
                        st = (b, 4 * s - 2)
                        starts.append((cs + cb + pi + up + 1.0, st, ((m, ("s", 4 * s - 2, OPP[rot])),
                                                                     (b, ("f", 4 * s - 2)))))
                        meta.setdefault(st, []).append((c, rot, s, m))
        return starts, meta
    starts, meta = build(fr)
    if not starts:
        N.why = "no starts"
    N.block = set()
    path = None
    for _ in range(4):
        path = N.search(starts) if starts else None
        if path is None:
            break
        bad = N.conflicts(path)
        if not bad:
            break
        N.block |= bad                      # (a path wanting a cell two ways: again, round it)
        N.why = "conflict"
        path = None
    N.block = set()
    if path is None:
        # every face of the house on open ground (a side or back door), not only its front
        ext = [(c, (c[0] + d[0], c[1] + d[1])) for c in lot["cells"] if rooms_of(L, lot, c) for d in FACE.values()
               if (c[0] + d[0], c[1] + d[1]) in L.W and (c, (c[0] + d[0], c[1] + d[1])) not in fr]
        if ext:
            fr = fr + ext
            starts, meta = build(fr)
            path = N.search(starts) if starts else None
            if path is not None and N.conflicts(path):
                path = None
    if path is None:
        # a recessed entry: the house gives its front room cell to a porch holding the stair (up from the street
        # to the floor, or down from the street to it)
        pst, pmeta = porch_starts(L, N, lot, fr)
        path = N.search(pst) if pst else None
        if path is not None and not N.conflicts(path):
            pc, srot = next((c, a[2]) for c, a in path if a[0] == "s" and (c, a[2]) in pmeta)
            c2, rot_d, _, down = pmeta[(pc, srot)]
            N.commit(path)
            qs = N.fix[pc][1]
            s = qs // 4 if down else (qs + 2) // 4
            porches.append((lot["id"], pc, c2, s, down))
            doors_of[lot["id"]] = ((c2, rot_d), s)
            stoops[pc] = (N.fix[pc][2], 2)
            return True
        # a yard: one cell of the lot (beside open ground) given up, paved at a floor of the house beside it, the
        # door from the yard (a side or back door)
        ys = []
        for y in lot["cells"]:
            if y in L.W or not any((y[0] + d[0], y[1] + d[1]) in L.W for d in FACE.values()):
                continue
            if not any(rooms_of(L, lot, x) for x in lot["cells"] if x != y):
                continue
            by = base_q(L, y)
            for rot, d in FACE.items():
                c2 = (y[0] + d[0], y[1] + d[1])
                if not L.inb(*c2) or int(L.lot[c2]) != lot["id"]:
                    continue
                for s in rooms_of(L, lot, c2):
                    if by <= 4 * s <= by + MAXF and s + 1 < L.L and not any(
                            L.block[y[0], y[1], k] for k in range(int(L.gk[y]), s + 1)):
                        ys.append((1.0 + FILL_W * (4 * s - by) + 4.0, (y, 4 * s), ((y, ("f", 4 * s)),)))
                        N.yard_meta[(y, 4 * s)] = (c2, OPP[rot], s)
        if ys:
            added = [st[1][0] for st in ys if st[1][0] not in N.base]
            for y in added:
                N.base[y] = base_q(L, y)
            path = N.search(ys)
            if path is not None and not N.conflicts(path):
                hit = [(c, a) for c, a in path if c in added and a[0] == "f" and (c, a[1]) in N.yard_meta]
                if not hit:
                    for x in added:
                        N.base.pop(x, None)
                    whys.append(("yard?", lot["id"], len(ys)))
                    return False
                y, a = hit[-1]
                c2, rot_d, s = N.yard_meta[(y, a[1])]
                N.commit(path)
                N.yards.append((lot["id"], y, c2, s))
                doors_of[lot["id"]] = ((c2, rot_d), s)
                for x in added:
                    if x != y:
                        N.base.pop(x, None)
                return True
            for y in added:
                N.base.pop(y, None)
        whys.append((N.why, lot["id"], len(starts)))
        return False
    N.commit(path)
    # which entrance the path began at: the start state among its assignments
    fixed = set(c for c, a in path)
    done = False
    for st, opts in meta.items():
        for (c, rot, s, sm) in opts:
            m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
            if sm is None and N.fix.get(m) == ("f", 4 * s) and m in fixed:
                doors_of[lot["id"]] = ((c, rot), s)
                done = True
            elif sm is not None and N.fix.get(m) == ("s", 4 * s - 2, OPP[rot]) and m in fixed:
                doors_of[lot["id"]] = ((c, rot), s)
                stoops[m] = (OPP[rot], 2)
                done = True
            if done:
                break
        if done:
            break
    if not done:
        # (the path ended on an entrance already fixed: any entrance that now meets the network)
        for c, m in fr:
            rot = ROT_OF[(m[0] - c[0], m[1] - c[1])]
            for s in rooms_of(L, lot, c):
                if N.fix.get(m) == ("f", 4 * s):
                    doors_of[lot["id"]] = ((c, rot), s)
                    done = True
                    break
            if done:
                break
    return done


def reached_fix(N, travel):
    """the fixed cells the arrival reaches (flat at one level, stairs along their axis)"""
    fix = N.fix
    seen = {travel}
    dq = deque([travel])

    def edge(c, rot):
        a = fix[c]
        if a[0] == "f":
            return (a[1], a[1])
        if rot == a[2]:
            return (a[1] + 2, a[1] + 2)
        if rot == OPP[a[2]]:
            return (a[1], a[1])
        return None                                          # (a stair's side: a lip)
    while dq:
        c = dq.popleft()
        for rot, d in FACE.items():
            n = (c[0] + d[0], c[1] + d[1])
            if n in seen or n not in fix:
                continue
            ea, eb = edge(c, rot), edge(n, OPP[rot])
            if ea is not None and ea == eb:
                seen.add(n)
                dq.append(n)
    return seen


def ripup(L, N, lot, fr_of, state, travel):
    """a lot hemmed in by its neighbours' paths: the paving round its front taken up (2 cells), its own path laid
    first, then the paths of every door that lost its way laid again -- kept only if every door still reached"""
    fr = fr_of[lot["id"]]
    if not fr:
        return False
    for rad in (2, 4):
        if ripup_r(L, N, lot, fr_of, state, travel, rad):
            return True
    return False


def ripup_r(L, N, lot, fr_of, state, travel, rad):
    fr = fr_of[lot["id"]]
    keep = (dict(N.fix), {k: dict(v) if isinstance(v, dict) else list(v) for k, v in state.items()}, list(N.porches),
            list(N.yards))
    near = set()
    for c, m in fr:
        for di in range(-rad, rad + 1):
            for dj in range(-rad, rad + 1):
                x = (m[0] + di, m[1] + dj)
                if abs(di) + abs(dj) <= rad and x in N.fix and x != travel and x not in N.pin and x not in N.pin_s:
                    near.add(x)
    for x in near:
        del N.fix[x]
    def door_ok(lid, R):
        (c, rot), s = state["doors"][lid]
        m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
        a = N.fix.get(m)
        if m not in R or a is None:
            return False
        if a == ("f", 4 * s):
            return True
        # a stoop rising to the door, or a porch stair (up to it, or down from it out to the street)
        return a[0] == "s" and ((a[1] == 4 * s - 2 and a[2] == OPP[rot]) or (a[1] == 4 * s and a[2] == rot))

    ok = route_lot(L, N, lot, fr, state)
    if ok:
        # the doors cut off by the taking-up (or whose step it changed): their paths again
        R = reached_fix(N, travel)
        for lid, ((c, rot), s) in list(state["doors"].items()):
            m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
            if door_ok(lid, R):
                continue
            del state["doors"][lid]
            state["stoops"].pop(m, None)
            if not route_lot(L, N, L.lots[lid], fr_of[lid], state):
                ok = False
                break
    if ok:
        R = reached_fix(N, travel)
        ok = all(door_ok(lid, R) for lid in state["doors"])
    if not ok:
        N.fix = keep[0]
        for k, v in keep[1].items():
            state[k] = v
        N.porches[:] = keep[2]
        for yd in N.yards[len(keep[3]):]:
            N.base.pop(yd[1], None)
        N.yards[:] = keep[3]
        return False
    return True


def run_round(L, travel_cell, order, fr_of):
    """one laying-out of the doors' paths in this order -> (net, stoops, failed lot ids, {lot: (door, storey)}, why)"""
    from pick import h01
    N = Net(L)
    N.door_lv = L.door_lv
    N.fix[travel_cell] = ("f", N.base[travel_cell])
    st = {"stoops": {}, "doors": {}, "whys": []}
    N.porches = []
    failed = []
    for lot in order:
        ok = route_lot(L, N, lot, fr_of[lot["id"]], st)
        if ok is False and os.environ.get("WALK_RIPUP", "1") == "1":
            ok = ripup(L, N, lot, fr_of, st, travel_cell)
        if ok is False:
            failed.append(lot["id"])
    return N, st["stoops"], failed, st["doors"], st["whys"]


def solve(L, civ, travel_cell):
    from pick import h01
    L.W = walk_cells(L)
    L.walk_fail = []
    if travel_cell not in L.W:
        travel_cell = min(L.W, key=lambda c: abs(c[0] - travel_cell[0]) + abs(c[1] - travel_cell[1]))
    L.travel_cell = travel_cell
    # the lots' fronts first (entry yards join the open ground)
    fr_of = {lot["id"]: fronts(L, lot) for lot in L.lots}
    # shut-in ground (a court or a scrap of plaza walled round by houses): a passage carved to the open ground
    L.q = {}
    L.carved = 0
    for _ in range(60):
        seen = {travel_cell}
        dq = deque([travel_cell])
        while dq:
            c = dq.popleft()
            for d in FACE.values():
                n = (c[0] + d[0], c[1] + d[1])
                if n in L.W and n not in seen:
                    seen.add(n)
                    dq.append(n)
        rest = [c for c in L.W if c not in seen]
        if not rest:
            break
        # the shut-in pocket nearest the open ground first
        pocket = {rest[0]}
        dq = deque([rest[0]])
        while dq:
            c = dq.popleft()
            for d in FACE.values():
                n = (c[0] + d[0], c[1] + d[1])
                if n in L.W and n not in pocket:
                    pocket.add(n)
                    dq.append(n)
        k = carve(L, list(pocket), lambda n: n in seen, max_len=8)
        if not k:
            # (no passage short enough: the pocket stays off the walk -- planted, its doors elsewhere)
            for c in pocket:
                L.W.discard(c)
            continue
        L.carved += k
    fr_of = {lot["id"]: fronts(L, lot) for lot in L.lots}
    # a house sunk below its street (every floor under the deck outside): it gains a storey (or two) on a front cell,
    # its door at the street
    L.grown = 0
    for lot in L.lots:
        fr = fr_of[lot["id"]]
        if not fr or any(4 * s >= base_q(L, m) for c, m in fr for s in rooms_of(L, lot, c)):
            continue
        need = sorted(((base_q(L, m) + 3) // 4 - max(rooms_of(L, lot, c)), c) for c, m in fr)
        for k_add, c in need:
            top = max(rooms_of(L, lot, c))
            if k_add > 2 or not all(L.free_at(c[0], c[1], k) for k in range(top + 1, top + 1 + k_add)):
                continue
            u = int(L.unit[c[0], c[1], top])
            for k in range(top + 1, top + 1 + k_add):
                L.set_room(c[0], c[1], k, u, 4)
                L.grown += 1
            break
    # the lots in the order of their distance from the arrival
    dist = {travel_cell: 0}
    dq = deque([travel_cell])
    while dq:
        c = dq.popleft()
        for d in FACE.values():
            n = (c[0] + d[0], c[1] + d[1])
            if n in L.W and n not in dist:
                dist[n] = dist[c] + 1
                dq.append(n)
    door_lv = {}
    for lot in L.lots:
        for c, m in fr_of[lot["id"]]:
            for s in rooms_of(L, lot, c):
                door_lv.setdefault(m, set()).add(4 * s)
                b = (2 * m[0] - c[0], 2 * m[1] - c[1])
                if b in L.W:
                    door_lv.setdefault(b, set()).add(4 * s - 2)      # (a stoop's foot)
    L.door_lv = door_lv
    order0 = sorted(L.lots, key=lambda lot: min([dist.get(m, 10 ** 6) for _, m in fr_of[lot["id"]]] or [10 ** 6]))
    # rounds: the lots that found no way in go first next time (a door hemmed in by the paths of its neighbours)
    best = None
    prio = []
    for rnd in range(int(os.environ.get("WALK_ROUNDS", 4))):
        pset = set(prio)
        order = [lot for lot in order0 if lot["id"] in pset] + [lot for lot in order0 if lot["id"] not in pset]
        res = run_round(L, travel_cell, order, fr_of)
        if best is None or len(res[2]) < len(best[2]):
            best = res
        if not res[2]:
            break
        prio = prio + [i for i in res[2] if i not in pset]
    N, stoops, failed, doors_of, why = best
    if os.environ.get("WALK_DEBUG"):
        for lid, ((c, rot), s) in doors_of.items():
            m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
            a = N.fix.get(m)
            if not (a == ("f", 4 * s) or (a and a[0] == "s" and ((a[1] == 4 * s - 2 and a[2] == OPP[rot]) or (a[1] == 4 * s and a[2] == rot)))):
                print("BAD DOOR", lid, c, rot, s, m, a, "porch" if any(p[0] == lid for p in N.porches) else "")
    L.door_feet = set()
    for (lid, pc, c2, s, down) in N.porches:
        # the porch: its rooms cleared up to the stair's headroom, open paving (a court of the house)
        for k in range(int(L.gk[pc]), min(s + (2 if down else 1), L.L)):
            if L.occ[pc[0], pc[1], k]:
                L.clear(pc[0], pc[1], k)
        L.plan[pc] = COURT
        L.W.add(pc)
        N.base[pc] = base_q(L, pc)
        lot = L.lots[lid]
        lot["shop_cells"] = set(lot.get("shop_cells", ())) - {pc}
        if down:
            L.door_feet.add(pc)
    L.porches = len(N.porches)
    for (lid, y, c2, s) in N.yards:
        for k in range(int(L.gk[y]), min(s + 1, L.L)):
            if L.occ[y[0], y[1], k]:
                L.clear(y[0], y[1], k)
        L.plan[y] = COURT
        L.W.add(y)
        lot = L.lots[lid]
        lot["shop_cells"] = set(lot.get("shop_cells", ())) - {y}
    L.yards = len(N.yards)
    if os.environ.get("WALK_DEBUG"):
        for lid in failed[:8]:
            lot = L.lots[lid]
            print("FAILED lot", lid, "use", lot["use"], "cells", len(lot["cells"]))
            for c, m in fr_of[lid][:6]:
                b = (2 * m[0] - c[0], 2 * m[1] - c[1])
                print("   front", c, "->", m, "plan", int(L.plan[m]), "rooms", rooms_of(L, lot, c), "m fix", N.fix.get(m),
                      "m base", N.base.get(m), "b", b, N.fix.get(b), N.base.get(b),
                      "nbrs", [(x, N.fix.get(x), N.base.get(x)) for x in ((m[0] + d[0], m[1] + d[1]) for d in FACE.values()) if x != c])
    for lot in L.lots:
        lot["door"], lot["door_k"] = doors_of.get(lot["id"], (None, None))
    L.walk_fail += why
    L.walk_rounds = rnd + 1
    # the public ground no door path took: joined where it is cheap (nearest first), else planted
    left = sorted((c for c in L.W if c not in N.fix and L.plan[c] in PUBLIC_W), key=lambda c: dist.get(c, 10 ** 6))
    for c in left:
        if c in N.fix:
            continue
        b = N.base[c]
        starts = [(N.flat_ok(c, q), (c, q), ((c, ("f", q)),)) for q in range(b, b + 5, 2)]
        starts = [s for s in starts if s[0] is not None]
        path = N.search(starts)
        if path is not None:
            N.commit(path)
    # the stoops, from the doors as laid (a stair on the step rising to the door; a porch's stair)
    stoops = {}
    for lid, ((c, rot), s) in doors_of.items():
        m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
        a = N.fix.get(m)
        if a and a[0] == "s":
            stoops[m] = (a[2], 2)
    # (a stair whose landing or foot a taking-up removed: flat, at the end that is still there)
    for c, a in list(N.fix.items()):
        if a[0] != "s" or c in stoops:
            continue
        f = FACE[a[2]]
        top, foot = (c[0] + f[0], c[1] + f[1]), (c[0] - f[0], c[1] - f[1])
        if N.fix.get(top) is None:
            N.fix[c] = ("f", a[1])
        elif N.fix.get(foot) is None:
            N.fix[c] = ("f", a[1] + 2)
    for c in [c for c in N.fix if c not in L.W]:
        del N.fix[c]                     # (a porch or yard of a laying-out that was taken back)
    for c in N.fix:
        if c not in N.base:
            N.base[c] = base_q(L, c)
    # everything into the walk.py form
    L.q = {}
    L.stair = {}
    for c, a in N.fix.items():
        L.q[c] = a[1]
        if a[0] == "s":
            L.stair[c] = (a[2], 2)
    L.stoop = stoops
    planted = [c for c in L.W if c not in N.fix]
    for c in planted:
        L.W.discard(c)
        L.plan[c] = PASTURE
    L.planted = len(planted)
    # the shops: where the street meets the shop floor
    for lot in L.lots:
        ok = set()
        for c in lot.get("shop_cells", ()):
            g = int(L.gk[c])
            for rot, d in FACE.items():
                m = (c[0] + d[0], c[1] + d[1])
                if m in L.W and L.plan[m] in (MAIN, PLAZA, ARTERY) and L.q.get(m) == 4 * g and m not in L.stair:
                    ok.add(c)
                    break
        lot["shop_cells"] = ok
    # (a door left over from a laying-out that a later one changed: dropped, the lot goes on below)
    for lot in L.lots:
        if not lot.get("door"):
            continue
        (c, rot), s = lot["door"], lot["door_k"]
        m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
        st_ = L.stair.get(m)
        good = c not in L.W and m in L.q and (
            (not st_ and L.q[m] == 4 * s) or
            (st_ and ((L.q[m] == 4 * s - 2 and st_[0] == OPP[rot]) or (L.q[m] == 4 * s and st_[0] == rot))))
        if not good:
            lot["door"] = lot["door_k"] = None
            L.stoop.pop(m, None)
            L.door_feet.discard(m)
    # (a stair climbing into a wall -- its door dropped: flat at its foot)
    heads = set()
    for lot in L.lots:
        if lot.get("door"):
            c, rot = lot["door"]
            heads.add((c[0] + FACE[rot][0], c[1] + FACE[rot][1]))
    for c, (r0, r) in list(L.stair.items()):
        top = (c[0] + FACE[r0][0], c[1] + FACE[r0][1])
        foot = (c[0] - FACE[r0][0], c[1] - FACE[r0][1])
        if (top not in L.W and c not in heads) or (foot not in L.W and c not in L.door_feet):
            del L.stair[c]
            L.stoop.pop(c, None)
            if top in L.W and foot not in L.W:
                L.q[c] += r
    # (a stair whose foot or head no longer meets it -- a run whose other flight was flattened above: flat at the end
    # that still meets it, again until nothing changes)
    from walk import connected
    for _ in range(6):
        moved = False
        for c, (r0, r) in list(L.stair.items()):
            if c in L.stoop or c in L.door_feet:
                continue
            top = (c[0] + FACE[r0][0], c[1] + FACE[r0][1])
            foot = (c[0] - FACE[r0][0], c[1] - FACE[r0][1])
            fo = foot in L.W and connected(L, foot, c)
            to = top in L.W and connected(L, c, top)
            if fo and to:
                continue
            del L.stair[c]
            if to and not fo:
                L.q[c] += r
            moved = True
        if not moved:
            break
    # (and what the arrival cannot reach after all: its doors dropped, its ground planted)
    check(L, travel_cell)
    for lot in L.lots:
        if lot.get("door"):
            c, rot = lot["door"]
            m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
            if m not in L.reached:
                lot["door"] = lot["door_k"] = None
    for c in [c for c in L.W if c not in L.reached]:
        L.W.discard(c)
        L.q.pop(c, None)
        L.stair.pop(c, None)
        L.stoop.pop(c, None)
        L.plan[c] = PASTURE
        L.planted += 1
    # the houses still without a way in: an annex of the neighbouring house they touch (an inner door between rooms
    # at one storey) -- else taken down to a walled garden (planted, off the walk).  No unit is made for a lot
    # without a door, so nobody lives sealed in.
    L.annexed = L.gardens = 0
    for lot in L.lots:
        if lot.get("door") or not any(rooms_of(L, lot, c) for c in lot["cells"]):
            continue
        host = None
        for c in lot["cells"]:
            for d in FACE.values():
                n = (c[0] + d[0], c[1] + d[1])
                if not L.inb(*n) or int(L.lot[n]) < 0 or int(L.lot[n]) == lot["id"]:
                    continue
                o = L.lots[int(L.lot[n])]
                if o.get("door") and set(rooms_of(L, lot, c)) & set(rooms_of(L, o, n)):
                    host = o
                    break
            if host:
                break
        if host:
            for c in lot["cells"]:
                L.lot[c] = host["id"]
            host["cells"] = list(host["cells"]) + list(lot["cells"])
            lot["cells"] = []
            lot["front"] = []
            lot["annex_of"] = host["id"]
            L.annexed += 1
        else:
            for c in lot["cells"]:
                for k in range(L.L):
                    if L.occ[c[0], c[1], k] and int(L.lot[c]) == lot["id"]:
                        L.clear(c[0], c[1], k)
                if c not in L.W:
                    L.plan[c] = PASTURE
            lot["garden"] = True
            L.gardens += 1
    # rooms left hanging by the porches, yards and opened lanes (the lattice's support rule: a room under it, a
    # cantilever of a cell, a span of three): taken down, from the bottom up, until everything stands
    L.unhung = 0
    import numpy as np
    for _ in range(L.L):
        bad = [(int(i), int(j), k) for k in range(1, L.L) for i, j in zip(*np.nonzero(L.occ[:, :, k]))
               if not L.supported(int(i), int(j), k)]
        if not bad:
            break
        for (i, j, k) in bad:
            L.clear(i, j, k)
            L.unhung += 1
    L.raised = sum(1 for c in L.q if L.q[c] > N.base.get(c, 0))
    fails = check(L, travel_cell)
    pub = [c for c in L.W if L.plan[c] in PUBLIC_W]
    doors_n = sum(1 for lot in L.lots if lot.get("door"))
    shops_n = sum(len(lot.get("shop_cells", ())) for lot in L.lots)
    noentry = [lot["id"] for lot in L.lots if not lot.get("door") and any(rooms_of(L, lot, c) for c in lot["cells"])]
    stats = {
        "doors": doors_n, "doors_reached": doors_n - len(fails["doors"]),
        "shop_cells": shops_n, "shops_reached": shops_n - len(fails["shops"]),
        "public_cells": len(pub), "public_reached": len(pub) - len(fails["cells"]),
        "stairs": len(L.stair), "stairs_both_ends": len(L.stair) - len(fails["stairs"]),
        "stoops": len(L.stoop), "porches": L.porches, "yards": L.yards, "storeys_added": L.grown, "annexed": L.annexed, "unsupported_removed": L.unhung, "gardens": L.gardens, "carved": L.carved, "raised_cells": L.raised, "planted_cells": L.planted,
        "fill_mean_m": round(sum(L.q[c] - N.base[c] for c in L.q) * Q / max(len(L.q), 1), 2),
        "fill_max_m": round(max([L.q[c] - N.base[c] for c in L.q] or [0]) * Q, 1),
        "iterations": 1, "lots_without_entrance": len(noentry), "no_entrance_why": sorted(set(str(w[0])[:12] for w in L.walk_fail)), "no_entrance_n": len(L.walk_fail),
        "failures": {k: v[:8] for k, v in fails.items() if v},
        "pass": not (fails["doors"] or fails["cells"] or fails["stairs"] or fails["shops"] or noentry),
    }
    if os.environ.get("WALK_DEBUG"):
        for c in fails["stairs"]:
            r0 = L.stair[c][0]
            print("BAD STAIR", c, L.q[c], L.stair[c], "stoop", c in L.stoop, "door_foot", c in L.door_feet,
                  "plan", int(L.plan[c]), [(x, L.q.get(x), L.stair.get(x), x in L.W) for x in
                   ((c[0] + FACE[r0][0], c[1] + FACE[r0][1]), (c[0] - FACE[r0][0], c[1] - FACE[r0][1]))])
    L.walk_stats = stats
    kc = set()
    for lot in L.lots:
        if lot.get("door"):
            c, rot = lot["door"]
            kc.add((c[0] + FACE[rot][0], c[1] + FACE[rot][1]))
    for c, (r0, r) in L.stair.items():
        kc.update((c, (c[0] + FACE[r0][0], c[1] + FACE[r0][1]), (c[0] - FACE[r0][0], c[1] - FACE[r0][1])))
    L.keep_clear = kc
    return stats
