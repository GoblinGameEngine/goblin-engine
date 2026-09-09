extends Node3D

# Alternating red/blue flasher for a parked police car (see
# build_police_car.py -- every car has a "LightRed"/"LightBlue" emissive
# mesh built in). Attach directly to PoliceCar.tscn's root.

@export var flash_interval := 0.28

var _red: MeshInstance3D
var _blue: MeshInstance3D
var _t := 0.0
var _on := false

func _ready() -> void:
	_red = find_child("LightRed", true, false) as MeshInstance3D
	_blue = find_child("LightBlue", true, false) as MeshInstance3D

func _process(delta: float) -> void:
	_t += delta
	if _t >= flash_interval:
		_t = 0.0
		_on = not _on
		if _red:
			_red.visible = _on
		if _blue:
			_blue.visible = not _on
