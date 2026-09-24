extends StaticBody3D
class_name RemakeVehicleSeat

## The pilot's seat of a RemakeAirVehicle: E on it takes the controls.

var vehicle: RemakeAirVehicle


func interact(by: Node = null) -> String:
	if by is StationPlayer and vehicle.pilot == null:
		vehicle.take_seat(by)
		return "seated"
	return ""


func interact_prompt() -> String:
	return "Take the controls" if vehicle.pilot == null else ""
