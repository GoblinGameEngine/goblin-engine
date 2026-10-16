#!/usr/bin/env python3
"""
bake_vendor_pool.py -- the flea markets' vendor pools (research/flea_markets/00_plan.md §2.3):
godot_project/remake/markets/vendor_pool.json, read by FleaVendors.

"Individuals from all walks of life": any adult can vend. Each person's weekend vendor propensity is a weight over
the traits they already have (no new trait layer). Every person belongs to ONE market's pool (so nobody is booked at
two markets on one day): their own settlement's market; the people between the towns (the "_country" shard) to the
nearest market; and a small market whose own town is too small to fill its stalls borrows a hashed share of the
people living within 8 km of it (taken out of their home market's pool).

From each market's candidates a weighted sample of POOL_K x stalls people is drawn without replacement
(Efraimidis-Spirakis keys from a hash of the world seed and the pid): the townsfolk who vend at some time. FleaVendors
draws season, permanent and day tenants from that sample, so the file stays small (~27k people) and stable.

Inputs: godot_project/remake/characters/lives/<Town>.json (bake_lives.gd), npc_place_index.json + npc_places.json (the
workplace's days), remake/markets/flea_markets.json (stalls, centres). Rerun after bake_lives or the market siting.
"""
import hashlib
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
import markets_spec as MS  # noqa: E402

GP = os.path.join(ROOT, "godot_project", "remake")
LIVES = os.path.join(GP, "characters", "lives")
OUT = os.path.join(GP, "markets", "vendor_pool.json")
CIRC = 2 * math.pi * 10000.0
POOL_K = 8                 # sample size per stall
BORROW_R = 8000.0          # m: a small market's catchment beyond its own town (00 §2.2)
SEED = 1
TRIP_P = 0.06              # an out-of-town market about once in 6 weekends (00 §6.3)
TRIP_K = 12                # trippers sampled per stall
CAT = {c: i for i, c in enumerate(MS.CATEGORIES)}

# who vends (00 §2.3): (weight x, categories)
TRADES = {"mechanic", "builder", "factory_hand", "dock_worker", "driver", "fisher", "janitor"}
FARM = {"farmer", "farmhand"}
ARCH_CATS = {
    "retired": ["antiques", "collectibles", "books", "tools", "crafts"],
    "homemaker": ["household", "clothing_used", "food", "crafts", "plants"],
    "struggling": ["household", "clothing_used", "salvage", "tools"],
    "owner": ["clothing_new", "household", "crafts", "food"],
    "trades": ["tools", "salvage", "electronics", "furniture"],
    "farm": ["produce", "plants", "food"],
    "student": ["clothing_used", "books", "toys", "food"],
    "lowliner": ["sky", "crafts", "clothing_new", "food", "electronics"],
    "any": list(CAT),
}
ARCH_ID = {k: i for i, k in enumerate(ARCH_CATS)}
SOUTH = {"south_shore", "southland"}


def h01(*parts):
    d = hashlib.blake2b("|".join(str(p) for p in parts).encode(), digest_size=8).digest()
    return (struct.unpack("<Q", d)[0] >> 11) / float(1 << 53)


def wrap_ds(d):
    return (d + CIRC / 2) % CIRC - CIRC / 2


def weight(p, work_days, region):
    """(weight, archetype) or (0, None) for someone who can't vend at weekends"""
    age = int(p.get("age", 0))
    if age < 18 or age > 85:
        return 0.0, None
    occ = p.get("occupation", "")
    if occ in ("student", "preschool"):
        return 0.0, None
    days = p.get("days") or work_days
    if p.get("work") and days not in ("mon-fri", None, ""):
        return 0.0, None                                  # (works weekends: never on a day they work, 00 §6.3)
    w, arch = 1.0, "any"
    fin = p.get("finances", "")
    if occ == "retired":
        w, arch = 3.0, "retired"
    elif occ == "homemaker":
        w, arch = 2.0, "homemaker"
    elif occ == "unemployed" or p.get("jobless") or fin in ("struggling", "in_debt"):
        w, arch = 2.0, "struggling"
    elif occ in FARM or p.get("pop") == "farm":
        w, arch = 2.0, "farm"
    elif occ in TRADES:
        w, arch = 1.5, "trades"
    elif occ == "shopkeeper":
        w, arch = 1.2, "owner"
    elif occ == "university_student":
        w, arch = 0.8, "student"
    # Lowliners (00 §9): heritage "lowliner" once the traits tools give it (plan step 4); weight by region
    if p.get("lineage") == "lowliner" or p.get("name_heritage") == "lowliner":
        w, arch = max(w, 3.0 if region in SOUTH else 2.0), "lowliner"
    return w, arch


def cats_mask(arch, pid):
    cs = ARCH_CATS[arch]
    # two or three of the archetype's categories, hashed per person (a person's stall sells what they have)
    n = 2 + int(h01(SEED, pid, "ncat") * 2)
    pick = sorted(cs, key=lambda c: h01(SEED, pid, "cat", c))[:n]
    m = 0
    for c in pick:
        m |= 1 << CAT[c]
    return m


def main():
    fm = json.load(open(os.path.join(GP, "markets", "flea_markets.json")))["markets"]
    by_town = {m["town"]: m for m in fm}
    centre = {}
    for m in fm:
        f = m["frame"]
        centre[m["id"]] = (float(f["s"]), float(f["x"]))
    places = json.load(open(os.path.join(GP, "characters", "npc_places.json")))["types"]
    unit_type = {}
    for u in json.load(open(os.path.join(GP, "characters", "npc_place_index.json")))["units"]:
        unit_type[u["uid"]] = u.get("type")
    cand = {m["id"]: [] for m in fm}                     # market -> [(pid, w, arch, door)]
    away = []                                            # people with no market of their own town
    for fn in sorted(os.listdir(LIVES)):
        if not fn.endswith(".json") or fn.startswith("_index"):
            continue
        town = fn[:-5].replace("_", " ")
        mk = by_town.get(town)
        region = mk["region"] if mk else ""
        for pid, p in sorted(json.load(open(os.path.join(LIVES, fn)))["people"].items()):
            t = places.get(unit_type.get(p.get("work", ""), ""), {})
            wd = (t.get("hours") or {}).get("days")
            w, arch = weight(p, wd, region)
            if w <= 0:
                continue
            door = p.get("door") or [0.0, 0.0]
            e = (pid, w, arch, (float(door[0]), float(door[1])))
            if mk:
                cand[mk["id"]].append(e)
            else:
                away.append(e)
    for e in away:                                        # the country between the towns: the nearest market
        mid = min(centre, key=lambda k: math.hypot(wrap_ds(centre[k][0] - e[3][0]), centre[k][1] - e[3][1]))
        cand[mid].append(e)
    # small markets borrow from within 8 km (smallest first), out of markets with people to spare
    need = {m["id"]: POOL_K * len(m["stalls"]) for m in fm}
    home = {e[0]: mid for mid, es in cand.items() for e in es}
    for m in sorted(fm, key=lambda m: len(cand[m["id"]]) / max(1, need[m["id"]])):
        mid = m["id"]
        short = need[mid] * 1.25 - len(cand[mid])
        if short <= 0:
            continue
        c = centre[mid]
        near = []
        for oid, es in cand.items():
            if oid == mid or len(cand[oid]) < need[oid] * 2:
                continue
            for e in es:
                if math.hypot(wrap_ds(e[3][0] - c[0]), e[3][1] - c[1]) <= BORROW_R:
                    near.append((oid, e))
        if not near:
            continue
        f = min(0.5, short / len(near))
        moved = [(oid, e) for oid, e in near if h01(SEED, e[0], "borrow", mid) < f]
        ids = {e[0] for _, e in moved}
        for oid in {o for o, _ in moved}:
            cand[oid] = [e for e in cand[oid] if e[0] not in ids]
        cand[mid] += [e for _, e in moved]
        for _, e in moved:
            home[e[0]] = mid
    # -- the trippers (00 §6.3, market_trip): every adult not vending keeps one usual out-of-town market, drawn by gravity
    #    (stalls x draw / max(d, 2 km)^2 over the other markets); a market's trippers are a weighted sample of TRIP_K x
    #    stalls of the people who chose it, each with a per-market-day chance p that keeps the expected trips the plan's
    #    (0.06 a market day, x1.5 retired or struggling, x0.5 without a car). NpcLife and the destination draw the same.
    in_pool = set()
    trip_c = {m["id"]: [] for m in fm}
    ids = [m["id"] for m in fm if m.get("sited", True)]
    cs = np.array([centre[i] for i in ids])
    st = np.array([float(len(next(m for m in fm if m["id"] == i)["stalls"])) for i in ids])
    expect = {i: 0.0 for i in ids}
    everyone = []
    for fn in sorted(os.listdir(LIVES)):
        if not fn.endswith(".json") or fn.startswith("_index"):
            continue
        town = fn[:-5].replace("_", " ")
        own = by_town.get(town, {}).get("id")
        for pid, p in sorted(json.load(open(os.path.join(LIVES, fn)))["people"].items()):
            if int(p.get("age", 0)) < 18 or p.get("occupation") in ("student", "preschool"):
                continue
            mod = (1.5 if p.get("occupation") == "retired" or p.get("finances") in ("struggling", "in_debt") else 1.0) * \
                (0.5 if p.get("car") == "none" else 1.0)
            everyone.append((pid, own, (float(p["door"][0]), float(p["door"][1])), mod, fn[:-5]))
    for pid, own, door, mod, shard in everyone:
        ds = (cs[:, 0] - door[0] + CIRC / 2) % CIRC - CIRC / 2
        d = np.maximum(2.0, np.hypot(ds, cs[:, 1] - door[1]) / 1000.0)
        w = st / (d * d)
        for k, i in enumerate(ids):
            if i == own:
                w[k] = 0.0
        tot = float(w.sum())
        if tot <= 0:
            continue
        r = h01(SEED, pid, "trip_market") * tot
        k = int(np.searchsorted(np.cumsum(w), r, side="right"))
        k = min(k, len(ids) - 1)
        expect[ids[k]] += TRIP_P * mod
        trip_c[ids[k]].append((pid, mod, shard))
    out = {}
    tot = 0
    for m in fm:
        mid = m["id"]
        es = cand[mid]
        k = min(len(es), need[mid])
        keyed = sorted(es, key=lambda e: -math.log(max(1e-12, h01(SEED, e[0], "pool"))) / e[1])[:k]
        keyed.sort(key=lambda e: e[0])
        out[mid] = {"pids": [e[0] for e in keyed], "cats": [cats_mask(e[2], e[0]) for e in keyed],
                    "arch": [ARCH_ID[e[2]] for e in keyed], "candidates": len(es)}
        tc = trip_c.get(mid, [])
        kt = min(len(tc), TRIP_K * len(m["stalls"]))
        tk = sorted(tc, key=lambda e: -math.log(max(1e-12, h01(SEED, e[0], "trip_pool"))) / e[1])[:kt]
        tk.sort(key=lambda e: e[0])
        msum = sum(e[1] for e in tk) or 1.0
        # each sampled tripper's chance a market day: the market's expected trips shared by their weights (capped 0.5)
        out[mid]["trippers"] = [e[0] for e in tk]
        out[mid]["trip_p"] = [round(min(0.5, expect.get(mid, 0.0) * e[1] / msum), 4) for e in tk]
        out[mid]["trip_shard"] = [e[2] for e in tk]
        out[mid]["trips_expected"] = round(expect.get(mid, 0.0), 1)
        tot += k
        print("%-7s stalls %3d  candidates %6d  pool %5d  trippers %5d (%.0f trips a market day)" % (
            mid, len(m["stalls"]), len(es), k, kt, expect.get(mid, 0.0)))
    doc = {"_about": "Flea-market vendor pools (00_plan §2.3): per market the townsfolk who vend at some time, a weighted "
                     "sample by their traits; every person in at most one pool. Written by tools/markets/bake_vendor_pool.py "
                     "from the lives bake; read by FleaVendors.",
           "seed": SEED, "categories": MS.CATEGORIES, "archetypes": list(ARCH_CATS), "markets": out}
    with open(OUT + ".tmp", "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    os.replace(OUT + ".tmp", OUT)
    print("%s: %d vendors in %d pools" % (OUT, tot, len(out)))


if __name__ == "__main__":
    main()
