extends RemakeAirVehicle
class_name RemakeSkyGondola

## The sky gondola (remake/blender/vehicles/sky_gondola.py): a cabin under a lift balloon, four
## tilting ducted fans.  Flies as every RemakeAirVehicle does; this gives its model and hull.
## Local frame (glTF): x right, y up (0 = the casters' contact), -z the nose.

const MODEL := "res://remake/vehicles/sky_gondola.glb"
const FLOOR := 0.35
const H := 2.45


func _init() -> void:
	stand_point = Vector3(0.45, FLOOR + 1.45, 0.55)      # behind the seats, on the floor


func _build_hull() -> void:
	load_model(MODEL)
	# floor and belly
	add_box(Vector3(2.0, 0.1, 3.3), Vector3(0, FLOOR - 0.05, 0))
	add_box(Vector3(1.9, 0.26, 3.0), Vector3(0, 0.15, 0))
	# walls, leaving each side's doorway (z -0.65..0.65) to the door leaves
	var wall_h := H - 0.15 - FLOOR
	for sx in [-1.0, 1.0]:
		for sz in [-1.0, 1.0]:
			add_box(Vector3(0.1, wall_h, 0.9), Vector3(sx * 1.13, FLOOR + wall_h * 0.5, sz * 1.15))
	add_box(Vector3(2.0, wall_h, 0.1), Vector3(0, FLOOR + wall_h * 0.5, -1.72))
	add_box(Vector3(2.0, wall_h, 0.1), Vector3(0, FLOOR + wall_h * 0.5, 1.72))
	add_box(Vector3(2.2, 0.12, 3.4), Vector3(0, H - 0.1, 0))
	# boarding ramps up to each doorway (the model's step; the player can't climb a 35 cm sill)
	for sx in [-1.0, 1.0]:
		add_box(Vector3(0.72, 0.05, 1.0), Vector3(sx * 1.45, FLOOR * 0.5, 0.0), -sx * atan2(FLOOR, 0.6))
	# furniture: the dash, the two front seats, the rear bench
	add_box(Vector3(2.0, 0.78, 0.38), Vector3(0, FLOOR + 0.39, -1.5))
	for sx in [-0.5, 0.5]:
		add_box(Vector3(0.56, 0.55, 0.52), Vector3(sx, FLOOR + 0.27, -0.25))
	add_box(Vector3(1.8, 0.52, 0.48), Vector3(0, FLOOR + 0.26, 1.34))
	# the fans (as upright cylinders) and the balloon
	for sx in [-1.0, 1.0]:
		for sz in [-1.0, 1.0]:
			add_cylinder(0.62, 0.46, Vector3(sx * 1.8, 0.39, sz * 1.38))
	add_sphere(2.4, Vector3(0, H + 0.62 + 2.4, 0))


func door_slide() -> float:
	return 0.62
