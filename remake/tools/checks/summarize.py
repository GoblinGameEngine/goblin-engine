#!/usr/bin/env python3
"""summarize.py REPORT -- condense check_batch reports: per building, real failures only.
Doorway-pass hits beyond 0.9 of the sweep (furniture/cars behind a clear doorway) are ignored."""
import re
import sys
fails = {}
rooms = tot = 0
section = None
for ln in open(sys.argv[1]):
    ln = ln.rstrip()
    if ln.startswith("---"):
        section = ln
        continue
    m = re.match(r"(\S+) (\d+) rooms/lights, (\d+) unreachable", ln)
    if m:
        rooms += int(m.group(2))
        tot += 1
        if int(m.group(3)):
            fails.setdefault(m.group(1), []).append(f"{m.group(3)}/{m.group(2)} rooms unreachable")
        continue
    m = re.match(r"(\S+) (\S+) frac ([0-9.]+)", ln)
    if m and section and "pass" in section and float(m.group(3)) < 0.9:
        fails.setdefault(m.group(1), []).append(f"doorway {m.group(2)} blocked at {m.group(3)}")
        continue
    m = re.match(r"(\S+) DoorBody_(\S+) hinge", ln)
    if m and section and "swing" in section:
        fails.setdefault(m.group(1), []).append(f"door {m.group(2)} swing clash")
print(f"{tot} buildings, {rooms} rooms checked; {len(fails)} with problems")
for k in sorted(fails):
    print(" ", k, "; ".join(fails[k]))
