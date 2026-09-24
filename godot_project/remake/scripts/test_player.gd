extends CharacterBody3D
class_name RemakeTestPlayer

## Minimal first-person walker for testing remake buildings on flat ground:
## WASD, mouse look, jump, sprint, E = interact (doors).  Not the game's player.

const SPEED := 4.2
const SPRINT := 7.5
const JUMP := 4.5
const GRAVITY := 9.8
const REACH := 2.6
const STEP := 0.36          # tallest step climbed without a ramp (exterior stone steps, thresholds)

@onready var cam: Camera3D = $Camera3D
@onready var ray: RayCast3D = $Camera3D/RayCast3D
var prompt: Label
var last_interact := ""
var ladders := 0
var ladder_axis := Vector3.ZERO     # centre of the last ladder zone entered (x/z used)


func set_ladder(delta: int, zone: Node3D = null) -> void:
	ladders = max(0, ladders + delta)
	if delta > 0 and zone:
		ladder_axis = zone.global_position


func _ready() -> void:
	# historic stairs run 48-51 deg (tavern: 15 risers in 10'); treat them as walkable floor
	floor_max_angle = deg_to_rad(52.0)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	var ui := CanvasLayer.new()
	add_child(ui)
	prompt = Label.new()
	prompt.position = Vector2(20, 20)
	prompt.add_theme_font_size_override("font_size", 22)
	ui.add_child(prompt)
	var cross := Label.new()
	cross.text = "+"
	cross.set_anchors_preset(Control.PRESET_CENTER)
	cross.add_theme_font_size_override("font_size", 22)
	ui.add_child(cross)


func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-e.relative.x * 0.003)
		cam.rotation.x = clampf(cam.rotation.x - e.relative.y * 0.003, -1.5, 1.5)
	if e.is_action_pressed("interact"):
		interact()
	if e is InputEventKey and e.pressed and e.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func interact() -> String:
	var t := target()
	if t:
		last_interact = t.interact(self)
		return last_interact
	return ""


func target() -> Object:
	ray.force_raycast_update()
	var c := ray.get_collider()
	if c and c.has_method("interact"):
		return c
	return null


func _physics_process(dt: float) -> void:
	var climb := Input.get_axis("move_back", "move_forward")
	if ladders > 0 and not (is_on_floor() and climb < 0.0):
		# on a ladder: forward climbs, back descends, no gravity; sideways steps off.  At the foot
		# (standing on the floor) backing away walks off it normally.
		velocity = transform.basis * Vector3(Input.get_axis("move_left", "move_right") * 1.5, 0, 0)
		velocity.y = climb * 2.2
		if climb != 0.0 and Input.get_axis("move_left", "move_right") == 0.0:
			# draw the climber in onto the ladder's line so that, from a floor at the top, going
			# down drops into the shaft instead of pressing against the floor's edge
			var to := Vector3(ladder_axis.x - global_position.x, 0, ladder_axis.z - global_position.z)
			if to.length() > 0.05:
				velocity += to.normalized() * minf(1.2, to.length() * 4.0)
		move_and_slide()
		var tl := target()
		prompt.text = ("[E] " + tl.interact_prompt()) if tl else "[W/S] climb"
		return
	if not is_on_floor():
		velocity.y -= GRAVITY * dt
	elif Input.is_action_just_pressed("jump"):
		velocity.y = JUMP
	var dir2 := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var dir := (transform.basis * Vector3(dir2.x, 0, dir2.y)).normalized()
	var sp := SPRINT if Input.is_action_pressed("sprint") else SPEED
	velocity.x = dir.x * sp
	velocity.z = dir.z * sp
	_step_up(dt)
	move_and_slide()
	var t := target()
	prompt.text = ("[E] " + t.interact_prompt()) if t else ""


## Climb a single step: if the horizontal move is blocked but the same move from STEP
## higher is clear, lift the body onto the step; floor snap then settles it.
func _step_up(dt: float) -> void:
	var h := Vector3(velocity.x, 0, velocity.z) * dt
	if h.length() < 0.0005 or not is_on_floor():
		return
	var t := global_transform
	if not test_move(t, h):
		return
	var up := Vector3(0, STEP, 0)
	if test_move(t, up):
		return
	var raised := t.translated(up)
	if test_move(raised, h):
		return
	var col := KinematicCollision3D.new()
	var moved := raised.translated(h)
	if test_move(moved, -up, col):
		moved = moved.translated(col.get_travel())
	global_transform = moved
