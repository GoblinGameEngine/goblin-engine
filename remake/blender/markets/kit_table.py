#!/usr/bin/env python3
"""kit_table.py -- print the kit's piece table (id, group, tris full / MID, budget, collision, notes head) as Markdown"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
pj = json.load(open(os.path.join(ROOT, "godot_project", "remake", "markets", "pieces.json")))
rows = ["| piece | group | tris | MID | budget | collide | what |", "|---|---|---|---|---|---|---|"]
tot = mt = 0
for pid, r in pj["pieces"].items():
    tot += r["tris"]
    mt += r["mid"]["tris"]
    note = r["notes"].split(":")[0] if len(r["notes"]) > 90 else r["notes"]
    rows.append("| `%s` | %s | %d | %s | %s | %s | %s |" % (pid, r["group"], r["tris"], r["mid"]["tris"] if "kit_mid" in r["mid"]["glb"] else "=",
                                                       r.get("budget", ""), r["collide"], note[:110].replace("|", "/")))
print("\n".join(rows))
print("\n%d pieces, %d tris full, %d MID" % (len(pj["pieces"]), tot, mt))
