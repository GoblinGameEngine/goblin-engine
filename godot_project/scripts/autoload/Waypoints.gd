extends Node

# Named points on the map, placed via the map editor's "Waypoints" category
# (see MapEditorUI._place_waypoint()/_delete_waypoint()) and referenced by
# id from quest-giver schedules (data/quest_givers.json, read by
# QuestGiverGeneric.gd) -- e.g. "Lloyd stands at lloyd_porch from 6:00 to
# 20:00". Kept in their own file/registry rather than folded into
# custom_placements.json's "spawn a scene" model, since a waypoint has no
# visual representation in actual play -- just a name and a position.

const DATA_PATH := "res://data/waypoints.json"

var _by_id: Dictionary = {}   # id -> {x, y, z, label}

func _ready() -> void:
	if not FileAccess.file_exists(DATA_PATH):
		return
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return
	for w in data.get("waypoints", []):
		_by_id[w["id"]] = w

func has(id: String) -> bool:
	return _by_id.has(id)

func get_position(id: String) -> Variant:
	if not _by_id.has(id):
		return null
	var w: Dictionary = _by_id[id]
	return Vector3(w["x"], w["y"], w["z"])

func get_label(id: String) -> String:
	return _by_id.get(id, {}).get("label", id)

## Sorted for stable UI listing (dropdowns in the quest-giver schedule
## editor, etc.) -- insertion order from a hand-edited JSON file would be
## fine too, but sorted is easier to scan once there are a dozen of these.
func all_ids() -> Array:
	var ids := _by_id.keys()
	ids.sort()
	return ids

## Auto-numbered id (waypoint_1, waypoint_2, ...) offered as a default when
## placing a new one in the map editor -- the name prompt lets the user
## override it, but most waypoints don't need a memorable name.
func next_default_id() -> String:
	var n := 1
	while _by_id.has("waypoint_%d" % n):
		n += 1
	return "waypoint_%d" % n

func add(id: String, pos: Vector3, label: String = "") -> void:
	_by_id[id] = {"id": id, "x": pos.x, "y": pos.y, "z": pos.z, "label": label if label != "" else id}
	_save()

func remove(id: String) -> void:
	if _by_id.erase(id):
		_save()

func _save() -> void:
	var list: Array = []
	for id in all_ids():
		list.append(_by_id[id])
	var f := FileAccess.open(DATA_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"waypoints": list}, "  "))
		f.close()
	else:
		push_warning("Waypoints: could not write %s" % DATA_PATH)
