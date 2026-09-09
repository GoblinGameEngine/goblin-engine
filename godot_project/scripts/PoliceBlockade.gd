extends Node3D

# One parked police car blocks each open arm of the neighborhood (Lloyd
# east, Ira east, Ira west, Lakeshore north, Lakeshore south -- see
# scenes/Main.tscn). Each car's resting transform already faces outward
# along its own street arm, so depart() just drives every car forward
# along its own current heading, out past the map edge -- no per-car
# direction bookkeeping needed here.

var _departed := false

func _ready() -> void:
	add_to_group("police_blockade")

func depart() -> void:
	if _departed:
		return
	_departed = true
	for car in get_children():
		if car is Node3D:
			_drive_away(car as Node3D)

func _drive_away(car: Node3D) -> void:
	var forward: Vector3 = -car.global_transform.basis.z
	var tw := create_tween()
	tw.tween_property(car, "position", car.position + forward * 180.0, 8.0) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
