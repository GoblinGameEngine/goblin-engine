#!/bin/bash
# check_batch.sh REPORT ID [ID ...] -- launch catalog_test with these IDs, run the acceptance checks,
# quit, append the results to REPORT.  Needs the glbs built and imported.
REPORT=$1; shift
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
D="$ROOT/remake/tools/checks"
IDS=$(echo "$@" | tr ' ' ',')
SP=$(python3 -c "
import json,sys
sys.path.insert(0, '$ROOT/remake/tools')
from placement import glb_bounds
m=0
for i in sys.argv[1:]:
    try:
        l=json.load(open('$ROOT/remake/catalog/'+i+'.json')).get('lot') or {}
        m=max(m, l.get('w',20), l.get('d',20))
    except Exception: pass
    try:   # what's built can reach past the lot (elevator bins on their inventory parts)
        lo, hi = glb_bounds('$ROOT/godot_project/remake/buildings/'+i+'.glb')
        m=max(m, 2*max(abs(lo[0]), abs(hi[0]), abs(lo[2]), abs(hi[2])))
    except Exception: pass
print(int(max(24, m + 12)))" "$@")
python3 "$ROOT/tools/gcmd.py" quit >/dev/null 2>&1
sleep 1
cd "$ROOT/godot_project"
DISPLAY=:0 ../godot/godot4 --path . res://remake/scenes/catalog_test.tscn -- ids=$IDS cols=6 spacing=$SP > /tmp/check_batch_game.log 2>&1 &
GP=$!
sleep 3
{ echo "=== batch: $*"; "$D/run_checks.sh" 2>&1 | grep -v "^$"; grep -E "^(ERROR|SCRIPT ERROR)" /tmp/check_batch_game.log | grep -v "async function\|synchroniz" | sort | uniq -c | head -5; } >> "$REPORT"
python3 "$ROOT/tools/gcmd.py" quit >/dev/null 2>&1
sleep 2
kill $GP 2>/dev/null
