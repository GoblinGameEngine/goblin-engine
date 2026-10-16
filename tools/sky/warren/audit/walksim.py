"""walksim.py -- the player's capsule, approximated by ray bundles against the assembled collision, for many agents at
once (one Embree call per sub-step for the whole batch).

The model (StationPlayer: capsule r 0.18, height 1.45, floor_max_angle 55 deg, floor_snap 0.5, no step-up):
  * horizontal motion: a bundle of rays along the motion from the capsule's axis, at heights LIP .. 1.42 m over the
    feet and lateral offsets across the capsule's width at that height (the hemispheres narrow it); a ray stops the
    capsule at  t - sqrt(rh^2 - o^2)  when it hits a surface that is NOT a floor (facing normal y < cos 55 deg);
    the rest of the motion slides along the hit's horizontal normal (move_and_slide), up to 3 slides.
  * support: rays straight down from the capsule's top inside its footprint; each hit lifts a sphere of radius r to
    y + sqrt(r^2 - d^2) - r; the highest is where the feet rest.  A support higher than the last feet + LIP is an
    obstacle inside the capsule (a lip / a thin plate): the step is undone.  LIP = r (1 - cos 55 deg) = 7.7 cm: the
    tallest edge whose contact normal is still a floor -- anything taller is a wall to a capsule with no step-up.
  * vertical: on the floor and the support within FLOOR_SNAP below: snapped down; else falling (gravity), landing on
    the support.
Two clients: walk_edges (every walk-graph edge, both ways) and walk_paths (walktest.gd's door walks)."""
import math

import numpy as np

import common as C

R = C.CAP_R
H = C.CAP_H
COS_FLOOR = math.cos(math.radians(C.FLOOR_MAX_DEG))
LIP = R * (1.0 - COS_FLOOR)           # 0.0767 m
SKIN = 0.005
HS = np.array([LIP + 0.006, 0.12, 0.2, 0.32, 0.5, 0.75, 1.0, 1.2, 1.32, 1.42])
HS_HI = np.array([0.2, 0.32, 0.5, 0.75, 1.0, 1.2, 1.32, 1.42])   # the fixed layers over the per-agent low ones
SOFT = 0.06                            # lenient mode: an edge up to this over the floor's plane is taken (Godot's
                                       # slide + snap gets the capsule over ~5 cm lips at ramp heads most times)
NLAT = 7
LAT = np.linspace(-0.95, 0.95, NLAT)
TOP = 1.40                             # support rays start this far over the feet (inside the capsule)


def _ny(e, th):
    """the floor-ness (normal y) of a sphere's first contact with an edge e above the plane it rolls along at th"""
    t = math.tan(th)
    k = R / math.cos(th) - e
    a, b, c = 1 + t * t, 2 * t * k, k * k - R * R
    disc = b * b - 4 * a * c
    if disc < 0:
        return 1.0
    z = (-b - math.sqrt(disc)) / (2 * a)
    return 1.0 if z > 0 else (z * t + k) / R


def _estar(th):
    lo, hi = 0.0, R
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if _ny(m, th) >= COS_FLOOR else (lo, m)
    return lo


# the tallest edge a capsule rolling UP a slope of th can still take as floor, over the slope's plane, as a height
# over its feet (the sphere's bottom rides r (1/cos th - 1) over the plane): 7.7 cm on the flat, 3.7 cm at 15 deg,
# ~0 at 28 deg (a stair's ramp: a paving top even 2 cm above the ramp's head is a wall)
_TH = np.radians(np.arange(0, 56))
_H0 = np.array([max(_estar(t) - R * (1 / math.cos(t) - 1), 0.0) for t in _TH])


def lip_over_feet(slope):
    """per agent: the edge height over the feet a capsule moving at this slope (tan, + uphill) can climb"""
    th = np.arctan(np.clip(slope, 0.0, None))
    return np.interp(th, _TH, _H0)


def _rh(h):
    """the capsule's radius at height h over its bottom"""
    if h < R:
        return math.sqrt(max(R * R - (R - h) ** 2, 0.0))
    if h > H - R:
        return math.sqrt(max(R * R - (h - (H - R)) ** 2, 0.0))
    return R


PAT_H = []
PAT_O = []
PAT_RH = []
for _h in HS:
    rh = _rh(_h)
    for _o in np.linspace(-0.95 * rh, 0.95 * rh, NLAT):
        PAT_H.append(_h)
        PAT_O.append(_o)
        PAT_RH.append(rh)
PAT_H = np.array(PAT_H)
PAT_O = np.array(PAT_O)
PAT_BACK = np.sqrt(np.maximum(np.array(PAT_RH) ** 2 - PAT_O ** 2, 0.0))   # the capsule's front ahead of the axis
NP = len(PAT_H)
# footprint: centre, a ring at 0.55 r, a ring at 0.95 r
_FP = [(0.0, 0.0)] + [(0.55 * R * math.cos(a), 0.55 * R * math.sin(a)) for a in np.arange(6) * math.pi / 3] + \
      [(0.95 * R * math.cos(a), 0.95 * R * math.sin(a)) for a in (np.arange(8) + 0.5) * math.pi / 4]
FP = np.array(_FP)
FP_LIFT = np.sqrt(R * R - (FP ** 2).sum(1)) - R        # sphere: a point at d lifts the bottom by sqrt(r^2-d^2) - r
NF = len(FP)


class Batch:
    """N agents: feet p (N,3), vertical speed, on_floor; the last blocking triangle and why"""

    def __init__(self, rays, p, on_floor=True, soft=0.0):
        self.rays = rays
        self.soft = soft
        self.p = np.array(p, float).reshape(-1, 3)
        n = len(self.p)
        self.vy = np.zeros(n)
        self.floor = np.full(n, bool(on_floor))
        self.fn = np.tile([0.0, 1.0, 0.0], (n, 1))      # the floor's normal (motion follows its plane)
        self.hz_n = np.zeros(n, int)                     # lenient mode: edges taken that the strict model refuses
        self.hz_prim = np.full(n, -1, np.int64)
        self.hz_at = np.full((n, 3), np.nan)
        self.hz_list = []                                # (agent, prim, feet) every hazard met
        self.block_prim = np.full(n, -1, np.int64)       # the last thing that stopped the agent
        self.block_at = np.full((n, 3), np.nan)
        self.block_why = np.zeros(n, np.int8)            # 1 wall, 2 lip/intrusion, 3 steep
        self.fell = np.zeros(n, bool)                    # ever left the floor by more than FLOOR_SNAP
        self.fell_at = np.full((n, 3), np.nan)
        self.max_drop = np.zeros(n)                      # largest snap-down while on the floor
        self.drop_at = np.full((n, 3), np.nan)
        self.drop_prim = np.full(n, -1, np.int64)

    # ---------------------------------------------------------------- horizontal
    def _sweep(self, idx, m):
        """agents idx move by horizontal m (k,3) as far as the walls allow: returns the moved distance, the limit
        normal (k,3) (zero: free) and the limiting prim.  On a floor the rays follow the floor's plane (as
        move_and_slide's motion does: up a ramp they rise with it); the lowest layers sit at the tallest edge the
        capsule can take at that slope (lip_over_feet) -- in lenient mode at least SOFT over the plane, the edges
        between the two recorded as hazards"""
        k = len(idx)
        L = np.linalg.norm(m, axis=1)
        dirn = m / np.maximum(L, 1e-12)[:, None]
        perp = np.stack([-dirn[:, 2], np.zeros(k), dirn[:, 0]], 1)
        fn = np.where(self.floor[idx][:, None], self.fn[idx], [0.0, 1.0, 0.0])
        slope = -(fn[:, 0] * dirn[:, 0] + fn[:, 2] * dirn[:, 2]) / np.maximum(fn[:, 1], 0.2)
        h_strict = lip_over_feet(slope) + 0.004
        if self.soft > 0:
            th = np.arctan(np.clip(slope, 0.0, None))
            h_soft = self.soft - R * (1 / np.cos(th) - 1) + 0.004
            h_use = np.maximum(h_strict, h_soft)
        else:
            h_use = h_strict
        hs = np.concatenate([h_use[:, None], h_use[:, None] + 0.03, h_use[:, None] + 0.06,
                             np.repeat(HS_HI[None, :], k, 0), h_strict[:, None]], 1)       # (k, nl); last: hazard
        nl = hs.shape[1]
        rh = np.where(hs < R, np.sqrt(np.maximum(R * R - (R - hs) ** 2, 1e-8)),
                      np.where(hs > H - R, np.sqrt(np.maximum(R * R - (hs - (H - R)) ** 2, 1e-8)), R))
        lat = LAT[None, None, :] * rh[:, :, None]                                          # (k, nl, NLAT)
        back = np.sqrt(np.maximum(rh[:, :, None] ** 2 - lat ** 2, 0.0)).reshape(k, -1)
        o = self.p[idx][:, None, None, :] + perp[:, None, None, :] * lat[..., None]
        o[..., 1] += hs[:, :, None]
        d3 = dirn.copy()
        d3[:, 1] = slope
        sc = np.linalg.norm(d3, axis=1)
        d3 /= sc[:, None]
        npk = nl * NLAT
        d = np.repeat(d3[:, None, :], npk, 1)
        L = L * sc
        tmax = (L[:, None] + back + SKIN + 0.02).reshape(-1)
        t, prim, n = self.rays.cast(o.reshape(-1, 3), d.reshape(-1, 3), tmax)
        t = t.reshape(k, npk)
        prim = prim.reshape(k, npk)
        n = n.reshape(k, npk, 3)
        wall = np.isfinite(t) & (n[..., 1] < COS_FLOOR)
        adv = np.where(wall, t - back - SKIN, np.inf)
        hz = adv[:, -NLAT:]
        adv = adv[:, :-NLAT]
        j = np.argmin(adv, 1)
        a = adv[np.arange(k), j]
        mv = np.clip(np.minimum(a, L), 0.0, None)
        if self.soft > 0:
            # (hazards: an edge the strict layer meets within this step that the lenient layers let through)
            hj = np.argmin(hz, 1)
            ha = hz[np.arange(k), hj]
            got = (ha < mv) & (h_strict < h_use - 0.002)
            if got.any():
                gi = idx[got]
                self.hz_n[gi] += 1
                self.hz_prim[gi] = prim[got, npk - NLAT + hj[got]]
                self.hz_at[gi] = self.p[gi]
                for a_, p_, x_ in zip(gi, self.hz_prim[gi], self.p[gi]):
                    self.hz_list.append((int(a_), int(p_), x_.copy()))
        mv = mv / sc
        lim = a < L
        nn = n[np.arange(k), j].copy()
        nn[:, 1] = 0.0
        ln = np.linalg.norm(nn, axis=1)
        nn = np.where((ln > 1e-6)[:, None], nn / np.maximum(ln, 1e-6)[:, None], -dirn)
        nn[~lim] = 0.0
        lp = np.where(lim, prim[np.arange(k), j], -1)
        return mv, dirn, nn, lp

    def move(self, idx, m, slides=3):
        """horizontal motion m (k,3) for agents idx, with sliding; then support / snap / fall over dt"""
        idx = np.asarray(idx)
        m = np.array(m, float)
        m[:, 1] = 0.0
        want = m.copy()
        p0 = self.p[idx].copy()
        for s in range(slides):
            L = np.linalg.norm(m, axis=1)
            act = L > 1e-5
            if not act.any():
                break
            ia = idx[act]
            mv, dirn, nn, lp = self._sweep(ia, m[act])
            self.p[ia] += dirn * mv[:, None]
            hit = lp >= 0
            if hit.any():
                hi = ia[hit]
                self.block_prim[hi] = lp[hit]
                self.block_at[hi] = self.p[hi]
                self.block_why[hi] = 1
            rem = m[act] - dirn * mv[:, None]
            rem = rem - nn * np.einsum("ij,ij->i", rem, nn)[:, None]
            rem[~hit] = 0.0
            # (never slide back against the wish)
            back = np.einsum("ij,ij->i", rem, want[act]) <= 0
            rem[back] = 0.0
            m[act] = rem
        return p0

    # ---------------------------------------------------------------- vertical
    def support(self, idx, depth, cap):
        """the highest sphere-corrected support under each agent's footprint at or below cap (k,), from the capsule's
        top down: (y | nan, prim, facing normal, intrusion prim | -1).  A first hit above cap is something inside
        the capsule (an intrusion); the ray is cast again from under it (twice) to find the floor"""
        k = len(idx)
        p = self.p[idx]
        o = np.repeat(p[:, None, :], NF, 1)
        o[..., 0] += FP[None, :, 0]
        o[..., 2] += FP[None, :, 1]
        o[..., 1] += TOP
        o = o.reshape(-1, 3)
        d = np.tile([0.0, -1.0, 0.0], (k * NF, 1))
        bottom = np.repeat(p[:, 1] - np.asarray(depth, float), NF)
        capr = np.repeat(np.asarray(cap, float), NF)
        lift = np.tile(FP_LIFT, k)
        y = np.full(k * NF, -np.inf)
        pr = np.full(k * NF, -1, np.int64)
        nn = np.zeros((k * NF, 3))
        intr = np.full(k * NF, -1, np.int64)
        todo = np.arange(k * NF)
        oy = o[:, 1].copy()
        for _ in range(3):
            if not len(todo):
                break
            oo = o[todo].copy()
            oo[:, 1] = oy[todo]
            t, pq, nq = self.rays.cast(oo, d[todo], np.maximum(oy[todo] - bottom[todo], 0.0) + 1e-4)
            hy = oo[:, 1] - t
            sy = hy + lift[todo]
            hit = np.isfinite(t)
            over = hit & (sy > capr[todo])
            okh = hit & ~over
            y[todo[okh]] = sy[okh]
            pr[todo[okh]] = pq[okh]
            nn[todo[okh]] = nq[okh]
            first = over & (intr[todo] < 0)
            intr[todo[first]] = pq[first]
            oy[todo[over]] = hy[over] - 0.003
            todo = todo[over]
        y = y.reshape(k, NF)
        j = np.argmax(y, 1)
        s = y[np.arange(k), j]
        s = np.where(np.isfinite(s), s, np.nan)
        prk = pr.reshape(k, NF)[np.arange(k), j]
        nnk = nn.reshape(k, NF, 3)[np.arange(k), j]
        it = intr.reshape(k, NF)
        ik = np.where((it >= 0).any(1), it.max(1), -1)
        return s, prk, nnk, ik

    def step(self, idx, m, dt):
        """one tick: horizontal m, then the floor"""
        idx = np.asarray(idx)
        if not len(idx):
            return
        p0 = self.move(idx, m)
        fl = self.floor[idx]
        dxz = self.p[idx] - p0
        fn = self.fn[idx]
        plane = np.where(fl, -(fn[:, 0] * dxz[:, 0] + fn[:, 2] * dxz[:, 2]) / np.maximum(fn[:, 1], 0.2), 0.0)
        depth = np.where(fl, C.FLOOR_SNAP + 0.02, np.maximum(-self.vy[idx] * dt, 0) + 0.3) + 0.5
        y0 = p0[:, 1]
        hor = np.linalg.norm(dxz[:, [0, 2]], axis=1)
        lim = np.maximum(lip_over_feet(np.where(hor > 1e-6, np.maximum(plane, 0.0) / np.maximum(hor, 1e-6), 0.0)) + 0.004,
                         0.10 if self.soft > 0 else 0.0)
        cap = y0 + np.maximum(plane, 0.0) + lim
        s, pr, nn, intr = self.support(idx, depth, cap)
        rise = s - y0 - np.maximum(plane, 0.0)
        steep = np.isfinite(s) & (nn[:, 1] < COS_FLOOR) & (rise > 0.005)
        moved = hor > 1e-6
        bad = moved & ((intr >= 0) | steep)
        if bad.any():
            # an obstacle inside the capsule (a lip, a plate, a steep face): the step is undone
            bi = idx[bad]
            self.block_prim[bi] = np.where(intr[bad] >= 0, intr[bad], pr[bad])
            self.block_at[bi] = self.p[bi]
            self.block_why[bi] = np.where(steep[bad], 3, 2)
            self.p[bi] = p0[bad]
            s2, pr2, nn2, _ = self.support(bi, depth[bad], y0[bad] + LIP + 0.004)
            s[bad], pr[bad], nn[bad] = s2, pr2, nn2
        y = self.p[idx, 1]
        has = np.isfinite(s)
        on = fl & has & (s >= y - C.FLOOR_SNAP) & (s <= y + LIP + 0.12)
        # snapped (on the floor): record drops
        drop = np.where(on, y - s, 0.0)
        big = drop > self.max_drop[idx]
        if big.any():
            bi = idx[big]
            self.max_drop[bi] = drop[big]
            self.drop_at[bi] = self.p[bi]
            self.drop_prim[bi] = pr[big]
        self.p[idx[on], 1] = s[on]
        self.vy[idx[on]] = 0.0
        okn = on & (nn[:, 1] >= COS_FLOOR)
        self.fn[idx[okn]] = nn[okn]
        # falling
        fall = ~on
        if fall.any():
            fi = idx[fall]
            newly = self.floor[fi]
            if newly.any():
                ni = fi[newly]
                first = ~self.fell[ni]
                self.fell_at[ni[first]] = self.p[ni[first]]
                self.fell[ni] = True
            self.vy[fi] -= C.GRAVITY * dt
            ny = self.p[fi, 1] + self.vy[fi] * dt
            sf = s[fall]
            land = np.isfinite(sf) & (ny <= sf)
            ny = np.where(land, sf, ny)
            self.p[fi, 1] = ny
            self.floor[fi] = land
            self.vy[fi[land]] = 0.0
        self.floor[idx[on]] = True

    def settle(self, idx, steps=60, dt=1 / 60):
        """let agents fall onto whatever is below them"""
        idx = np.asarray(idx)
        self.floor[idx] = False
        for _ in range(steps):
            self.step(idx, np.zeros((len(idx), 3)), dt)
        self.fell[idx] = False
        self.fell_at[idx] = np.nan
        self.max_drop[idx] = 0
        self.block_prim[idx] = -1
        self.block_why[idx] = 0


# -------------------------------------------------------------------- client: every walk-graph edge
def walk_edges(rays, A, B, ds=0.05, slack=1.6, tol_xz=0.12, tol_y=0.3, drop_max=0.3, soft=0.0):
    """agents from A[k] to B[k] (feet points: graph nodes) straight along xz, sliding allowed; -> dict of arrays:
    ok, why ('ok', 'blocked', 'fell', 'drop', 'height'), where, prim"""
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = len(A)
    bt = Batch(rays, A + [0, 0.05, 0], soft=soft)
    bt.settle(np.arange(n), steps=8)
    start_y = bt.p[:, 1].copy()
    L = np.linalg.norm((B - A)[:, [0, 2]], axis=1)
    budget = np.ceil(L / ds * slack).astype(int) + 12
    done = np.zeros(n, bool)
    reached = np.zeros(n, bool)
    last_d = L.copy()
    still = np.zeros(n, int)
    for it in range(int(budget.max()) if n else 0):
        act = np.nonzero(~done & (it < budget))[0]
        if not len(act):
            break
        dv = B[act] - bt.p[act]
        dv[:, 1] = 0
        dl = np.linalg.norm(dv, axis=1)
        arr = dl < tol_xz
        if arr.any():
            reached[act[arr]] = True
            done[act[arr]] = True
        act = act[~arr]
        dv = dv[~arr]
        dl = dl[~arr]
        if not len(act):
            continue
        step = np.minimum(dl, ds)
        bt.step(act, dv / dl[:, None] * step[:, None], ds / C.WALK_SPEED)
        nd = np.linalg.norm((B[act] - bt.p[act])[:, [0, 2]], axis=1)
        prog = last_d[act] - nd > ds * 0.2
        still[act] = np.where(prog, 0, still[act] + 1)
        last_d[act] = np.minimum(last_d[act], nd)
        stuck = still[act] > 12
        done[act[stuck]] = True
        fallen = bt.fell[act] & (bt.p[act, 1] < np.minimum(A[act, 1], B[act, 1]) - 1.0)
        done[act[fallen]] = True
    why = np.full(n, "ok", object)
    dy = bt.p[:, 1] - B[:, 1]
    hfail = reached & (np.abs(dy) > tol_y)
    why[~reached] = "blocked"
    why[~reached & bt.fell] = "fell"
    why[reached & bt.fell] = "fell"
    why[hfail & ~bt.fell] = "height"
    dropf = (why == "ok") & (bt.max_drop > drop_max)
    why[dropf] = "drop"
    where = bt.p.copy()
    where[bt.fell] = bt.fell_at[bt.fell]
    blk = (why == "blocked") & np.isfinite(bt.block_at[:, 0])
    where[blk] = bt.block_at[blk]
    where[dropf] = bt.drop_at[dropf]
    prim = bt.block_prim.copy()
    prim[dropf] = bt.drop_prim[dropf]
    return {"hz_n": bt.hz_n.copy(), "hz_prim": bt.hz_prim.copy(), "hz_at": bt.hz_at.copy(),
            "ok": why == "ok", "why": why, "where": where, "prim": prim, "block_why": bt.block_why.copy(),
            "end": bt.p.copy(), "start_y": start_y, "max_drop": bt.max_drop.copy()}


# -------------------------------------------------------------------- client: walktest.gd's door walks
def walk_paths(rays, start, paths, dt=1 / 60, t_stuck=5.0, max_t=400.0, spawn_lift=1.6, soft=0.0):
    """walktest.gd: every agent spawned at start + spawn_lift (body origin; feet ORIGIN_ABOVE_FEET lower), walking
    at WALK_SPEED straight at each waypoint of its path; a waypoint is passed within 0.8 m (the last 1.3 m); stuck =
    t_stuck s without getting 0.5 m nearer.  -> per agent ('ok', time) or ('stuck', feet, waypoint index, origin y)"""
    n = len(paths)
    p = np.tile(np.asarray(start, float) + [0, spawn_lift - C.ORIGIN_ABOVE_FEET, 0], (n, 1))
    bt = Batch(rays, p, on_floor=False, soft=soft)
    wp = np.zeros(n, int)
    best = np.full(n, np.inf)
    tb = np.zeros(n)
    td = np.zeros(n)
    res = [None] * n
    steps = int(max_t / dt)
    trace = [[] for _ in range(n)]
    for it in range(steps):
        act = np.array([k for k in range(n) if res[k] is None], int)
        if not len(act):
            break
        tg = np.array([paths[k][wp[k]] for k in act], float)
        dv = tg - bt.p[act]
        dv[:, 1] = 0
        flat = np.linalg.norm(dv, axis=1)
        last = np.array([wp[k] == len(paths[k]) - 1 for k in act])
        td[act] += dt
        tb[act] += dt
        near = flat < np.where(last, 1.3, 0.8)
        movers = []
        for q, k in enumerate(act):
            if near[q]:
                if last[q]:
                    res[k] = ("ok", round(td[k], 1))
                    continue
                wp[k] += 1
                best[k] = np.inf
                tb[k] = 0.0
                continue
            if flat[q] < best[k] - 0.5:
                best[k] = flat[q]
                tb[k] = 0.0
            elif tb[k] > t_stuck:
                res[k] = ("stuck", np.round(bt.p[k], 2).tolist(), int(wp[k]),
                          round(float(bt.p[k, 1] + C.ORIGIN_ABOVE_FEET), 2))
                continue
            movers.append(q)
        if not movers:
            continue
        mq = np.array(movers)
        ia = act[mq]
        m = dv[mq] / np.maximum(flat[mq], 1e-9)[:, None] * (C.WALK_SPEED * dt)
        bt.step(ia, m, dt)
        if it % 15 == 0:
            for k in ia:
                trace[k].append(np.round(bt.p[k], 2).tolist())
    for k in range(n):
        if res[k] is None:
            res[k] = ("timeout", np.round(bt.p[k], 2).tolist(), int(wp[k]))
    return res, bt, trace
