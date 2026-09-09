extends Node

# Loads data/factions.json and tracks faction-vs-faction disposition, plus
# per-faction default AI behavior ("player" / "flee" / "aggressive").
# Disposition is symmetric and stored once per unordered pair.

signal disposition_changed(faction_a: String, faction_b: String, new_value: float)

const DATA_PATH := "res://data/factions.json"

var behaviors: Dictionary = {}       # faction_id -> "player"/"flee"/"aggressive"
var names: Dictionary = {}           # faction_id -> display name
var _disposition: Dictionary = {}    # "a|b" (sorted) -> float

var hostile_threshold := -20.0
var ally_threshold := 40.0

func _ready() -> void:
	_load_config()
	_load_data()

func _load_config() -> void:
	var cfg := ConfigFile.new()
	if cfg.load("res://config/game_settings.cfg") == OK:
		hostile_threshold = float(cfg.get_value("combat", "hostile_threshold", -20.0))
		ally_threshold = float(cfg.get_value("combat", "ally_threshold", 40.0))

func _load_data() -> void:
	var text := _read_file(DATA_PATH)
	if text.is_empty():
		push_error("FactionManager: failed to read %s" % DATA_PATH)
		return
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("FactionManager: malformed JSON in %s" % DATA_PATH)
		return
	for f in data.get("factions", []):
		behaviors[f.id] = f.get("behavior", "aggressive")
		names[f.id] = f.get("name", f.id)
	for r in data.get("relations", []):
		_set_key(r.a, r.b, float(r.disposition))

func _read_file(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	return text

func _pair_key(a: String, b: String) -> String:
	return "%s|%s" % [a, b] if a <= b else "%s|%s" % [b, a]

func _set_key(a: String, b: String, value: float) -> void:
	_disposition[_pair_key(a, b)] = value

func get_disposition(a: String, b: String) -> float:
	if a == b:
		return 100.0
	return _disposition.get(_pair_key(a, b), 0.0)

func set_disposition(a: String, b: String, value: float) -> void:
	value = clamp(value, -100.0, 100.0)
	_set_key(a, b, value)
	disposition_changed.emit(a, b, value)

func adjust_disposition(a: String, b: String, delta: float) -> void:
	set_disposition(a, b, get_disposition(a, b) + delta)

func is_hostile(a: String, b: String) -> bool:
	return a != b and get_disposition(a, b) <= hostile_threshold

func is_ally(a: String, b: String) -> bool:
	return a == b or get_disposition(a, b) >= ally_threshold

func get_behavior(faction_id: String) -> String:
	return behaviors.get(faction_id, "aggressive")
