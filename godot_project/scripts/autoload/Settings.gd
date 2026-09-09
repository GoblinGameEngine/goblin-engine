extends Node

# Player-facing settings, persisted to user://settings.cfg. Read by
# Player.gd (mouse sensitivity), the audio buses (sfx/music), and
# WorldEnvironment (gamma, via Environment.adjustment_brightness -- Godot
# has no literal "gamma" property, brightness is the standard stand-in).

signal changed()

const SAVE_PATH := "user://settings.cfg"

var sfx_volume: float = 0.8
var music_volume: float = 0.6
var gamma: float = 1.0
var mouse_sensitivity_mult: float = 1.0

func _ready() -> void:
	_ensure_bus("SFX")
	_ensure_bus("Music")
	load_settings()
	_apply_all()

func _ensure_bus(bus_name: String) -> void:
	if AudioServer.get_bus_index(bus_name) != -1:
		return
	var idx := AudioServer.bus_count
	AudioServer.add_bus(idx)
	AudioServer.set_bus_name(idx, bus_name)
	AudioServer.set_bus_send(idx, "Master")

func load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		sfx_volume = cfg.get_value("audio", "sfx_volume", sfx_volume)
		music_volume = cfg.get_value("audio", "music_volume", music_volume)
		gamma = cfg.get_value("video", "gamma", gamma)
		mouse_sensitivity_mult = cfg.get_value("controls", "mouse_sensitivity", mouse_sensitivity_mult)

func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio", "sfx_volume", sfx_volume)
	cfg.set_value("audio", "music_volume", music_volume)
	cfg.set_value("video", "gamma", gamma)
	cfg.set_value("controls", "mouse_sensitivity", mouse_sensitivity_mult)
	cfg.save(SAVE_PATH)

func set_sfx_volume(v: float) -> void:
	sfx_volume = v
	_apply_audio()
	save_settings()
	changed.emit()

func set_music_volume(v: float) -> void:
	music_volume = v
	_apply_audio()
	save_settings()
	changed.emit()

func set_gamma(v: float) -> void:
	gamma = v
	_apply_gamma()
	save_settings()
	changed.emit()

func set_mouse_sensitivity(v: float) -> void:
	mouse_sensitivity_mult = v
	save_settings()
	changed.emit()

func _apply_all() -> void:
	_apply_audio()
	_apply_gamma()

func _apply_audio() -> void:
	_set_bus_volume("SFX", sfx_volume)
	_set_bus_volume("Music", music_volume)

func _set_bus_volume(bus_name: String, linear: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return
	AudioServer.set_bus_volume_db(idx, linear_to_db(clamp(linear, 0.0001, 1.0)))

func _apply_gamma() -> void:
	var env_node := get_tree().get_first_node_in_group("world_environment")
	if env_node and env_node.environment:
		var environment: Environment = env_node.environment
		environment.adjustment_enabled = true
		environment.adjustment_brightness = clamp(gamma, 0.5, 1.8)
