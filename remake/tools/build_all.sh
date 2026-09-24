#!/bin/bash
# build_all.sh [-j N] [PATTERN]  -- regenerate the remake's game assets from source:
#   1. procedural textures (texgen.py) for any set not generated yet
#   2. publish them to the shared library godot_project/remake/textures (texlib.py, webp)
#   3. run every Blender builder (remake/blender/buildings/*.py, and generated catalog builds)
#      -> godot_project/remake/buildings/<ID>.glb + <ID>.mats.json
# Outputs are gitignored build products; run this after a fresh clone, then open/import in Godot.
set -e
cd "$(dirname "$0")/../.."
J=3
if [ "$1" = "-j" ]; then J=$2; shift 2; fi
PAT="${1:-*}"
PY="${PYTHON:-python3}"
$PY remake/tools/texgen.py --missing
$PY remake/tools/texlib.py
BL="${BLENDER:-flatpak run org.blender.Blender}"
ls remake/blender/buildings/$PAT.py remake/blender/generated/$PAT.py 2>/dev/null | grep -v "/_" | \
  xargs -P "$J" -I{} sh -c "$BL -b --factory-startup --python \"\$(realpath {})\" 2>&1 | grep -E 'EXPORTED|Traceback|Error:' | head -3 || true"
