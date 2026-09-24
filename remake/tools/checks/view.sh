#!/bin/bash
# view.sh BUILDING lx ly lz yaw_deg pitch_deg out.png   (building-local Blender coords; yaw 0 = looking +Y north)
B=$1; X=$2; Y=$3; Z=$4; YAW=$5; P=$6; OUT=$7
python3 $(dirname "$0")/../../../tools/gcmd.py run "var s = root.get_tree().current_scene
var b = s.get_node('$B')
var pl = s.get_node('TestPlayer')
pl.set_physics_process(false)
pl.velocity = Vector3.ZERO
var lp = Vector3($X, $Z - 1.62, -($Y))
pl.global_position = b.global_transform * lp
pl.global_rotation = Vector3(0, b.global_rotation.y + deg_to_rad($YAW), 0)
var cam = pl.get_viewport().get_camera_3d()
cam.rotation.x = deg_to_rad($P)
return str(pl.global_position)" >/dev/null
python3 -c "import time; time.sleep(0.2)"
python3 $(dirname "$0")/../../../tools/gcmd.py screenshot $OUT >/dev/null && echo $OUT
