#!/bin/bash
# walk.sh BUILDING x y z yaw seconds [action]  -- place the player (feet at z, building-local), hold an action
B=$1; X=$2; Y=$3; Z=$4; YAW=$5; T=$6; A=${7:-move_forward}
G="python3 $(dirname "$0")/../../../tools/gcmd.py"
$G run "var s = root.get_node('PruettTest')
var b = s.get_node('$B')
var pl = s.get_node('TestPlayer')
pl.set_physics_process(true)
pl.velocity = Vector3.ZERO
pl.global_position = b.global_transform * Vector3($X, $Z + 0.05, -($Y))
pl.global_rotation = Vector3(0, b.global_rotation.y + deg_to_rad($YAW), 0)
pl.get_viewport().get_camera_3d().rotation.x = 0.0
Input.action_press('$A')
return 1" >/dev/null
python3 -c "import time; time.sleep($T)"
$G run "Input.action_release('$A')
var s = root.get_node('PruettTest')
var b = s.get_node('$B')
var pl = s.get_node('TestPlayer')
var l = b.global_transform.affine_inverse() * pl.global_position
return 'end (%.2f,%.2f,%.2f) on_floor=%s' % [l.x, -l.z, l.y, pl.is_on_floor()]" | python3 -c "import json,sys; r=json.load(sys.stdin); print(r.get('error') or r.get('result'))"
