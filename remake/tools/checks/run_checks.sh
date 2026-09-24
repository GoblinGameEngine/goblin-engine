#!/bin/bash
# run_checks.sh [BUILDING] -- the remake's in-game acceptance checks, against a RUNNING test scene
# (res://remake/scenes/pruett_test.tscn or any scene with a 'PruettTest'-style root of RemakeBuilding children):
#   1. door_swing   -- every leaf's swing arc (half and fully open) is free of walls/furniture/roofs
#   2. doorway_pass -- with all doors open, a player capsule (r 0.25, h 1.75) sweeps through each doorway
#   3. room_reach   -- per building, bake a navmesh (player size, 0.36 m climb, 52 deg slope) and path from
#                      outside to every light_* (one per room)
# Locked doors are expected to fail 2/3 for the rooms behind them.
D="$(cd "$(dirname "$0")" && pwd)"
G="python3 $D/../../../tools/gcmd.py"
ONLY="${1:-}"
show() { python3 -c "import json,sys; r=json.load(sys.stdin); e=r.get('error'); print(e) if e else None; [print(x) for x in (r.get('result') or [])]"; }
$G wait-ready >/dev/null
echo "--- door swing"; $G run "$(cat $D/door_swing.gd)" | show
$G run "$(cat $D/open_all_doors.gd)" >/dev/null
$G run "await root.get_tree().physics_frame
return 1" >/dev/null
python3 -c "import time; time.sleep(0.3)"
echo "--- doorway pass"; $G run "$(cat $D/doorway_pass.gd)" | show
echo "--- room reach"; $G run "$(sed "s/ONLY_BUILDING/'$ONLY'/" $D/room_reach.gd)" | show
