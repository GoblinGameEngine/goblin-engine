extends Node
class_name VehiclePilot

## An NPC at the controls of any vehicle (2026-10-05: every vehicle takes a player's controls and an NPC's): a child
## of the vehicle that, each physics tick, steers it toward its target through the same inputs a player's keys give --
## drive_input (throttle, steer, handbrake) for a ground vehicle, fly_input (fwd, turn, lift) for one that flies or
## floats. Air: it climbs to its cruise height above the ground first, flies over, and lets down at the target.
## A boat keeps to the water (its own physics refuse land). A trailer has no controls: hitch it to what tows it.
##
##   var p := VehiclePilot.drive(vehicle, target, 40.0)    # start (cruise 40 m up, if it flies)
##   p.arrived  -> emitted on reaching the target (within arrive_r); the vehicle is then left stopped
## A flier's target may be up in the air -- a sky island's pad, 750 m up (2026-10-14) -- and may move: give it a node
## and an offset in that node's frame (VehiclePilot.fly_to) and the target is followed each tick. It climbs off its
## start straight up before going anywhere, cruises at cruise m over the ground or ARRIVE_OVER m over the target,
## whichever is higher, and settles onto the target's own height; near a moving target it matches its speed.

signal arrived

var vehicle: RemakeAirVehicle
var target := Vector3.ZERO
var cruise := 40.0                   # m above the ground (fliers)
var arrive_r := 6.0                  # m
var speed_kmh := 0.0                 # a ground vehicle's cruising speed; 0: its own (60 % of its top)
var done := false
var target_node: Node3D = null       # a moving target (an island): target = target_node.global_transform * target_local
var target_local := Vector3.ZERO
var _start_h := NAN                  # the flier's height (above the floor) where it took off
var _last_target := Vector3.INF
var _target_v := Vector3.ZERO        # the moving target's velocity (m/s)
var _start_p := Vector3.ZERO
var _start_aerial := false
var _cleared := false
const LEAVE_R := 250.0               # m from an aerial start it stays up over (an island's roofs)
const ARRIVE_OVER := 25.0            # m over an aerial target it comes in at, before letting down onto it


static func drive(v: RemakeAirVehicle, to: Vector3, cruise_m := 40.0) -> VehiclePilot:
	var old := v.get_node_or_null("VehiclePilot")
	if old:
		old.queue_free()
	var p := VehiclePilot.new()
	p.name = "VehiclePilot"
	p.vehicle = v
	p.target = to
	p.cruise = cruise_m
	v.add_child(p)
	return p


static func fly_to(v: RemakeAirVehicle, node: Node3D, local: Vector3, cruise_m := 60.0) -> VehiclePilot:
	## Fly to a point on a moving node (a sky island's pad): followed every tick till it's down on it.
	var p := drive(v, node.global_transform * local, cruise_m)
	p.target_node = node
	p.target_local = local
	return p


func stop() -> void:
	done = true
	if vehicle is RemakeGroundVehicle:
		(vehicle as RemakeGroundVehicle).drive_input = {"throttle": 0.0, "steer": 0.0, "handbrake": true}
	else:
		vehicle.fly_input = {"fwd": 0.0, "turn": 0.0, "lift": 0.0}


func _physics_process(_delta: float) -> void:
	if done or vehicle == null or vehicle.pilot != null:   # (a player took the seat: theirs to drive)
		return
	if target_node != null and is_instance_valid(target_node):
		target = target_node.global_transform * target_local
		if _last_target != Vector3.INF:
			_target_v = (target - _last_target) / maxf(_delta, 1e-4)
		_last_target = target
	var p := vehicle.global_position
	var s := StationGeo.s_of(p)
	var up := StationGeo.up(s)
	var to := target - p
	var flat := to - up * to.dot(up)
	var dist := flat.length()
	var fwd := -vehicle.global_transform.basis.z
	fwd = (fwd - up * fwd.dot(up)).normalized()
	var ang := fwd.signed_angle_to(flat.normalized(), up) if dist > 0.1 else 0.0   # + : the target is to the left
	var ground_h := MapTerrain.elevation(s, p.x)
	var h := StationGeo.h_of(p) - ground_h                  # m above the ground
	if vehicle is RemakeGroundVehicle:
		var gv := vehicle as RemakeGroundVehicle
		if dist < arrive_r:
			stop()
			arrived.emit()
			return
		var top := float(gv.phys.get("top_kmh", 100.0)) / 3.6
		var cruise_v := (speed_kmh / 3.6) if speed_kmh > 0.0 else top * 0.6
		var want_v := minf(cruise_v, maxf(2.0, dist * 0.5)) * (0.4 if absf(ang) > 0.8 else 1.0)
		gv.drive_input = {"throttle": clampf((want_v - gv._speed) * 0.4, -1.0, 1.0), "steer": clampf(-ang * 2.5, -1.0, 1.0)}
		return
	# it flies or floats
	var lift := 0.0
	var fwd_in := 0.0
	var h_abs := StationGeo.h_of(p)                             # m above the floor (the target's height is in these)
	var t_abs := StationGeo.h_of(target)
	var t_over := t_abs - MapTerrain.elevation(StationGeo.s_of(target), target.x)
	var aerial := t_over > 3.0                                  # (a target up in the air: an island's pad)
	if is_nan(_start_h):
		_start_h = h_abs
		_start_p = p
		_start_aerial = h > 3.0                                 # (taking off from up in the air: an island's pad)
	var over_t := h_abs - t_abs                                 # m over the target's height (<= ~0: down on it)
	if vehicle.can_climb:
		var near := dist <= arrive_r * 3.0
		var want_abs := maxf(ground_h + cruise, t_abs + ARRIVE_OVER if aerial else -INF) if not near else t_abs
		if _start_aerial and not near and p.distance_to(_start_p) < LEAVE_R:
			want_abs = maxf(want_abs, _start_h + 15.0)          # (off an island: up over its roofs before going down)
		lift = clampf((want_abs - h_abs) / 6.0, -1.0, 1.0)
		if near and over_t < 1.0:
			lift = -0.3
		# forward once it's up (or near): never through the treetops -- or an island's roofs -- on the way up
		if _start_aerial and h_abs - _start_h > 12.0:
			_cleared = true                                     # (up off the pad: from here it may go down again)
		var clear := _cleared if _start_aerial else h > minf(cruise * 0.6, 15.0)
		fwd_in = clampf(dist / 30.0, 0.15, 1.0) if (clear or near) else 0.0
		if target_node != null and _target_v.length() > 0.2:  # (a moving target: keep up with it, closing at what's left)
			var fwd_v := -vehicle.global_transform.basis.z
			var keep := (_target_v - vehicle.frame_velocity()).dot(fwd_v) / maxf(vehicle.max_speed, 1.0)   # (over the island its air moves with it already)
			fwd_in = clampf(maxf(fwd_in if dist > arrive_r * 3.0 else dist / 40.0, 0.0) + keep, -1.0, 1.0)
	else:
		fwd_in = clampf(dist / 20.0, 0.2, 1.0)
	fwd_in *= clampf(1.2 - absf(ang), 0.0, 1.0)                   # (turn first, then go)
	if dist < arrive_r and (not vehicle.can_climb or (over_t < 1.5 if aerial else h < 1.5)):
		stop()
		arrived.emit()
		return
	vehicle.fly_input = {"fwd": fwd_in, "turn": clampf(-ang * 2.0, -1.0, 1.0), "lift": lift}
