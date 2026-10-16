#!/usr/bin/env python3
"""
write_limits.py -- each settlement's city limits (the 48-point polygon, 00_plan §1.1) and its flea market id into
godot_project/remake/law/settlements.json, from remake/markets/flea_markets.json, in place (tools/law/make_law.py
does the same on its own runs). Run after tools/markets/site_markets.py (it calls this).
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LAW = os.path.join(ROOT, "godot_project", "remake", "law", "settlements.json")
FM = os.path.join(ROOT, "godot_project", "remake", "markets", "flea_markets.json")


def main():
    law = json.load(open(LAW))
    fm = {m["town"]: m for m in json.load(open(FM))["markets"]}
    n = 0
    for r in law["settlements"]:
        m = fm.get(r["name"])
        if not m:
            continue
        r["market"] = m["id"]
        if m.get("limits_sx"):
            r["limits"] = m["limits_sx"]
            n += 1
    with open(LAW + ".tmp", "w") as f:
        json.dump(law, f, indent=1, ensure_ascii=False)
    os.replace(LAW + ".tmp", LAW)
    print("law/settlements.json: %d settlements with limits, %d with a market" % (n, sum(1 for r in law["settlements"] if r.get("market"))))


if __name__ == "__main__":
    main()
