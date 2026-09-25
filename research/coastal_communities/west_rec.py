#!/usr/bin/env python3
"""Write West Coast coastal catalog records (SOL / PEL / PLV / OCV) from a spec file.

  west_rec.py near "File:X.jpg" [R]     other geotagged Commons files within R m (default 40)
  west_rec.py cat "Category:X"          files in a Commons category (a building's own category)
  west_rec.py make spec.json            fetch each record's photos, write remake/catalog/<ID>.json,
                                        claim its source ids in remake/catalog/_claims_coastal_west.txt

spec.json is a list of {"id", "photos": ["File:..", ...], "claim": "source id" (default: first photo),
"example": {"title", "place", "year", "source"?, "url"?}, "brief", "traits", "names"}.
settlement / kind / lot / label come from remake/inventory/coastal_inventory.json.
A claim already in the west or east claims file is refused."""
import glob
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "remake", "tools"))
import refs  # noqa: E402
sys.path.insert(0, HERE)
import west_net  # noqa: E402,F401  -- IPv4 + patient 429 handling for refs.get

CAT = os.path.join(ROOT, "remake", "catalog")
CLAIMS = os.path.join(CAT, os.environ.get("COAST_CLAIMS", "_claims_coastal_west.txt"))
OTHER_CLAIMS = glob.glob(os.path.join(CAT, "_claims_coastal*.txt"))  # every worker's claims, re-read at start
INV = os.path.join(ROOT, "remake", "inventory", "coastal_inventory.json")


def _q(params):
    return refs.get(refs.API + "?" + urllib.parse.urlencode(dict(params, format="json")))


def near(title, r=40):
    d = _q({"action": "query", "prop": "coordinates", "titles": title})
    pg = next(iter(d["query"]["pages"].values()))
    c = pg["coordinates"][0]
    d = _q({"action": "query", "list": "geosearch", "gsnamespace": 6, "gslimit": 100, "gsradius": max(10, r),
            "gscoord": f"{c['lat']}|{c['lon']}"})
    for g in d["query"]["geosearch"]:
        print(f"{g['dist']:6.1f} m  {g['title']}")


def cat(c):
    d = _q({"action": "query", "list": "categorymembers", "cmtitle": c, "cmlimit": 200})
    for m in d["query"]["categorymembers"]:
        print(m["title"])


_groups = {}


def resolve(t):
    """"GROUP:n" -> the title of entry n of research/coastal_communities/cand/GROUP.json"""
    if t.startswith(("File:", "Category:")) or ":" not in t:
        return t
    g, n = t.rsplit(":", 1)
    if g not in _groups:
        _groups[g] = json.load(open(os.path.join(HERE, "cand", g + ".json")))
    return _groups[g][int(n)]["title"]


def claimed():
    s = set()
    for p in [CLAIMS] + OTHER_CLAIMS:
        if os.path.exists(p):
            s |= {ln.strip() for ln in open(p) if ln.strip()}
    return s


def make(spec_path):
    inv = {s["id"]: s for s in json.load(open(INV))["structures"]}
    inv.update({w["id"]: w for w in json.load(open(INV))["walks"]})
    taken = claimed()
    photo_owner = {}
    for p in glob.glob(os.path.join(ROOT, "remake", "reference", "*", "sources.json")):
        m = json.load(open(p))
        for f in m["files"]:
            photo_owner.setdefault(f.get("title"), m.get("structure"))
    for r in json.load(open(spec_path)):
        sid = r["id"]
        r["photos"] = [resolve(t) for t in r["photos"]]
        if r.get("claim"):
            base, _, pos = r["claim"].partition("#")
            r["claim"] = resolve(base) + ("#" + pos if pos else "")
        claim = r.get("claim") or r["photos"][0]
        out = os.path.join(CAT, sid + ".json")
        if claim in taken and not os.path.exists(out):
            print(f"{sid}: REFUSED, {claim} already claimed")
            continue
        s = inv[sid]
        if "#" not in claim:
            dup = [t for t in r["photos"] if photo_owner.get(t, sid) != sid]
            if dup:
                print(f"{sid}: REFUSED, photo already used by {photo_owner[dup[0]]}: {dup[0]}")
                continue
        if r.get("expect") and s["kind"] not in r["expect"]:
            print(f"{sid}: REFUSED, inventory kind {s['kind']} is not one of {r['expect']}")
            continue
        files = []
        for t in r["photos"]:
            try:
                files.append(refs.commons_fetch(t, sid))
            except Exception as e:  # noqa: BLE001
                print(f"{sid}: {t} failed: {e}")
        if not files:
            print(f"{sid}: no photos, skipped")
            continue
        ex = {"title": r["example"]["title"], "place": r["example"]["place"], "year": r["example"]["year"],
              "source": r["example"].get("source", "Wikimedia Commons"),
              "url": r["example"].get("url") or "https://commons.wikimedia.org/wiki/" + r["photos"][0].replace(" ", "_"),
              "photos": files, "drawings": []}
        rec = {"id": sid, "settlement": s["settlement"], "kind": s["kind"], "coast": s.get("coast", "west")}
        if "w" in s:
            rec["lot"] = {"w": s["w"], "d": s["d"]}
        else:
            rec["walk"] = {"width_m": s.get("width_m"), "length_m": s.get("length_m")}
        rec.update({"example": ex, "brief": r["brief"], "traits": r["traits"], "names": r.get("names", {})})
        if s.get("label"):
            rec["label"] = s["label"]
        json.dump(rec, open(out, "w"), indent=1)
        if claim not in taken:
            with open(CLAIMS, "a") as f:
                f.write(claim + "\n")
            taken.add(claim)
        print(f"{sid}: {len(files)} photos, {ex['title']}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "near":
        near(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 40)
    elif cmd == "cat":
        cat(sys.argv[2])
    elif cmd == "make":
        make(sys.argv[2])
