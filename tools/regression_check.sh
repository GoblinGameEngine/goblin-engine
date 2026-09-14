#!/bin/bash
# regression_check.sh -- one-command headless sanity check for the
# Goblins project, in place of the same manual "kill any running
# instance, reimport, boot headless, grep the log" sequence run by hand
# dozens of times over the course of this project's development.
#
# Usage: tools/regression_check.sh [godot4_binary]
#   (defaults to looking for `godot4` on PATH, then
#   ~/newtons-garden/tools/godot4 as a fallback -- this project's own
#   dev-machine convention.)
#
# Exit code 0 = clean; non-zero = something below failed. Prints a
# clear PASS/FAIL per check either way, not just a final verdict, so a
# failure is diagnosable from this script's own output alone.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../godot_project" && pwd)"
LOG="$(mktemp /tmp/goblins_regression_XXXXXX.log)"
FAIL=0

GODOT="${1:-}"
if [ -z "$GODOT" ]; then
    if command -v godot4 >/dev/null 2>&1; then
        GODOT="godot4"
    elif [ -x "$HOME/newtons-garden/tools/godot4" ]; then
        GODOT="$HOME/newtons-garden/tools/godot4"
    else
        echo "FAIL: no godot4 binary found on PATH or at ~/newtons-garden/tools/godot4 -- pass one explicitly"
        exit 1
    fi
fi

check() {
    # $1 = description, $2 = 0 for pass / nonzero for fail
    if [ "$2" -eq 0 ]; then
        echo "PASS: $1"
    else
        echo "FAIL: $1"
        FAIL=1
    fi
}

echo "== Goblins regression check =="
echo "Godot binary: $GODOT"
echo "Project dir:  $PROJECT_DIR"
echo "Log:          $LOG"
echo

# Any running dev instance holds the DevBridge port and can interfere
# with a fresh headless launch's own port binding -- clean slate first.
pkill -f "godot4 --path $PROJECT_DIR" 2>/dev/null
sleep 1

echo "-- Reimporting (picks up any changed assets/shaders/new class_name scripts) --"
cd "$PROJECT_DIR" || exit 1
"$GODOT" --headless --import > "$LOG.import" 2>&1
IMPORT_EXIT=$?
check "reimport exits 0" "$IMPORT_EXIT"
if grep -qiE "error" "$LOG.import"; then
    check "reimport log has no ERROR lines" 1
    grep -iE "error" "$LOG.import" | sed 's/^/    /'
else
    check "reimport log has no ERROR lines" 0
fi

echo
echo "-- Headless boot (300 frames) --"
timeout 60 "$GODOT" --headless --path . scenes/Main.tscn --quit-after 300 > "$LOG" 2>&1
BOOT_EXIT=$?
check "headless boot exits 0" "$BOOT_EXIT"

if grep -qiE "^ERROR|SCRIPT ERROR" "$LOG"; then
    check "boot log has no ERROR lines" 1
    grep -iE "^ERROR|SCRIPT ERROR" "$LOG" | sed 's/^/    /'
else
    check "boot log has no ERROR lines" 0
fi

# Sanity lines every clean boot has printed since early in this
# project's history -- their absence means something upstream silently
# stopped running (a script error swallowed before it could push_error,
# a node renamed/moved so a get_node_or_null() call started returning
# null, etc.), even if nothing above technically errored.
declare -A EXPECT=(
    ["scenery optimize"]="Main: scenery optimize"
    ["doors/windows placed"]="Main: placed .* doors"
    ["cel shading applied"]="Main: cel-shaded .* materials"
    ["distance culling applied"]="Main: distance culling"
    ["occlusion culling applied"]="Main: occlusion culling"
)
for desc in "${!EXPECT[@]}"; do
    if grep -qE "${EXPECT[$desc]}" "$LOG"; then
        check "$desc" 0
    else
        check "$desc" 1
    fi
done

echo
echo "Full log: $LOG"
echo "Import log: $LOG.import"
if [ "$FAIL" -eq 0 ]; then
    echo "== ALL CHECKS PASSED =="
else
    echo "== SOME CHECKS FAILED -- see above =="
fi
exit "$FAIL"
