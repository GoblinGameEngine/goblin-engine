#!/bin/bash
# build_catalog.sh [-j N] [PREFIX ...]  -- build catalog records into glbs, N Blender processes
# in parallel (each takes a slice of the IDs).  PREFIX filters IDs (e.g. HF- FARM-); default: all.
cd "$(dirname "$0")/../.."
J=3
if [ "$1" = "-j" ]; then J=$2; shift 2; fi
BL="${BLENDER:-flatpak run org.blender.Blender}"
IDS=$(ls remake/catalog/*.json | xargs -n1 basename | grep -v "^_" | sed 's/\.json$//')
if [ $# -gt 0 ]; then IDS=$(for p in "$@"; do echo "$IDS" | grep "^$p"; done); fi
N=$(echo "$IDS" | wc -w)
echo "building $N records with $J processes"
LOG=$(mktemp -d)
i=0
for k in $(seq 0 $((J - 1))); do
  SLICE=$(echo "$IDS" | awk -v j=$J -v k=$k 'NR % j == k')
  [ -z "$SLICE" ] && continue
  $BL -b --factory-startup --python "$(realpath remake/blender/build_record.py)" -- $SLICE > $LOG/$k.log 2>&1 &
done
wait
grep -h "^BUILT\|^FAILED\|WARNING stair" $LOG/*.log
