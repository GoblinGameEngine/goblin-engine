extends Node

# Day/night cycle. Rate is loaded from config/game_settings.cfg so it can be
# tuned without touching code -- see [daynight] seconds_per_game_hour.
# Default: 60 real seconds per in-game hour (1 game-hour per real minute).

signal hour_changed(hour: float)
signal day_changed(day: int)

const CONFIG_PATH := "res://config/game_settings.cfg"
const SUN_GROUP := "sun_light"
const FILL_GROUP := "fill_light"
const ENV_GROUP := "world_environment"

var seconds_per_game_hour := 60.0
var hour: float = 8.0  # 0-24, wraps
var day: int = 1

## Dev/debug time control -- added so screenshots/testing at a specific
## time of day (dawn, noon, dusk, night) don't mean waiting out real
## minutes or hand-writing the same `root.get_node("/root/GameClock").hour
## = X` DevBridge `run` snippet every time. `frozen` short-circuits
## _process() entirely (lighting stays exactly where set_hour() left it,
## including across screenshot-capture frames), separate from just
## setting seconds_per_game_hour to something huge -- that would still
## drift a little and reads less clearly at the call site.
var frozen := false

## Jumps directly to `h` (0-24, wraps) and re-applies lighting
## immediately -- doesn't wait for the next _process() tick, so a
## `set_hour()` followed straight by a screenshot command shows the new
## time, not the old one.
func set_hour(h: float) -> void:
	hour = fmod(h, 24.0)
	if hour < 0.0:
		hour += 24.0
	_apply_lighting()

func freeze() -> void:
	frozen = true

func unfreeze() -> void:
	frozen = false

## Real seconds per in-game hour -- lower is faster. Same
## reload-vs-restart tradeoff as _load_config()'s other values: takes
## effect immediately, no relaunch needed.
func set_time_scale(seconds_per_hour: float) -> void:
	seconds_per_game_hour = max(0.01, seconds_per_hour)

# Warm dawn/dusk -> neutral midday -> cold dim night. Tunable in code for now;
# could be moved to the config file too if you want to tweak it without
# touching scripts.
const DAY_COLOR := Color(1.0, 0.97, 0.9)
const GOLDEN_COLOR := Color(1.0, 0.72, 0.45)
const NIGHT_COLOR := Color(0.35, 0.42, 0.65)

# Sky gradient keyframes -- the sun/ambient tint above handles the lighting,
# but the ProceduralSkyMaterial's own colors need to shift too or it reads
# as a permanent sunset no matter the hour.
const SKY_DAY_TOP := Color(0.30, 0.55, 0.85)
const SKY_DAY_HORIZON := Color(0.75, 0.85, 0.95)
const SKY_NIGHT_TOP := Color(0.03, 0.05, 0.12)
const SKY_NIGHT_HORIZON := Color(0.08, 0.10, 0.22)
const SKY_DUSK_TOP := Color(0.20, 0.28, 0.55)
const SKY_DUSK_HORIZON := Color(0.98, 0.55, 0.30)

func _ready() -> void:
	_load_config()
	_apply_lighting()

func _load_config() -> void:
	var cfg := ConfigFile.new()
	var err := cfg.load(CONFIG_PATH)
	if err == OK:
		seconds_per_game_hour = float(cfg.get_value("daynight", "seconds_per_game_hour", 60.0))
		hour = float(cfg.get_value("daynight", "start_hour", 8.0))
	else:
		push_warning("GameClock: could not load %s (err %d), using defaults" % [CONFIG_PATH, err])

func reload_config() -> void:
	_load_config()

func _process(delta: float) -> void:
	if frozen:
		return
	var prev_hour := hour
	hour += delta / seconds_per_game_hour
	if hour >= 24.0:
		hour = fmod(hour, 24.0)
		day += 1
		day_changed.emit(day)
	if int(prev_hour) != int(hour):
		hour_changed.emit(hour)
	_apply_lighting()

func get_time_string() -> String:
	var h := int(hour)
	var m := int((hour - h) * 60.0)
	return "%02d:%02d" % [h, m]

func is_night() -> bool:
	return hour < 5.5 or hour > 20.0

## 0 at midnight, 1 at noon -- a smooth day/night blend factor.
func day_factor() -> float:
	return (cos((hour / 24.0) * TAU + PI) + 1.0) * 0.5

func _apply_lighting() -> void:
	var sun := get_tree().get_first_node_in_group(SUN_GROUP)
	var fill := get_tree().get_first_node_in_group(FILL_GROUP)
	var env_node := get_tree().get_first_node_in_group(ENV_GROUP)

	# Sun sweeps a full circle over 24h; only meaningfully lit while above
	# the horizon (roughly 6:00-19:00), matching a stylized short winter-ish day.
	var angle := (hour / 24.0) * TAU
	var elevation := sin(angle - PI / 2.0)  # -1 at midnight, +1 at noon
	var df := day_factor()
	var near_horizon: float = 1.0 - abs(elevation)

	if sun:
		sun.rotation.x = -deg_to_rad(10) - elevation * deg_to_rad(70)
		sun.rotation.y = deg_to_rad(-50)
		sun.light_color = GOLDEN_COLOR.lerp(DAY_COLOR, clamp(elevation, 0.0, 1.0)).lerp(GOLDEN_COLOR, clamp(near_horizon, 0.0, 1.0) * 0.5)
		sun.light_energy = clamp(elevation * 1.8, 0.05, 1.8)
		sun.visible = elevation > -0.35

	if fill:
		fill.light_color = NIGHT_COLOR.lerp(Color(0.45, 0.55, 0.85), clamp(df, 0.0, 1.0))
		fill.light_energy = lerp(0.12, 0.3, clamp(df, 0.0, 1.0))

	if env_node and env_node.environment:
		var environment: Environment = env_node.environment
		# REAL BUG found live: this used to lerp up to 1.1 at full daylight --
		# comparable in magnitude to the direct sun's own contribution (up to
		# 1.8, but split into toon.gdshader's shade_dark/mid/lit bands of
		# 0.5/0.78/1.05). Sky ambient is a smooth per-pixel function of surface
		# normal (Godot samples it from the sky's own irradiance, not
		# quantized the way light() is), so once it got that strong it didn't
		# just brighten shadows -- it became a big enough share of the final
		# pixel that the whole image read as smoothly lit, with the
		# cel-shaded bands still technically there underneath but no longer
		# visible. Confirmed live: zeroing ambient_light_energy outright made
		# the 3-band tree/roof banding snap back immediately. Capped well
		# under the bands' own range instead of removing the fill entirely --
		# still enough to keep shadow sides off pure black, not enough to
		# compete with them.
		environment.ambient_light_energy = lerp(0.12, 0.35, clamp(df, 0.0, 1.0))
		environment.background_energy_multiplier = lerp(0.35, 1.0, clamp(df, 0.0, 1.0))

		var sky_mat := environment.sky.sky_material if environment.sky else null
		if sky_mat is ProceduralSkyMaterial:
			var dusk_weight: float = clamp(near_horizon * 1.6, 0.0, 1.0)
			var base_top := SKY_NIGHT_TOP.lerp(SKY_DAY_TOP, clamp(df, 0.0, 1.0))
			var base_horizon := SKY_NIGHT_HORIZON.lerp(SKY_DAY_HORIZON, clamp(df, 0.0, 1.0))
			sky_mat.sky_top_color = base_top.lerp(SKY_DUSK_TOP, dusk_weight)
			sky_mat.sky_horizon_color = base_horizon.lerp(SKY_DUSK_HORIZON, dusk_weight)
			sky_mat.ground_horizon_color = sky_mat.sky_horizon_color
