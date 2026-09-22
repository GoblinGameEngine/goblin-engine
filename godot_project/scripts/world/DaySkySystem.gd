extends Node
class_name DaySkySystem

# Drives the station's circadian sky cycle -- requested directly: a
# ceiling sky (shaders/ceiling_sky.gdshader) and wall cliff-to-sky blend
# (shaders/wall_cliff_sky.gdshader) sharing one time_of_day, plus a real
# shadow-casting DirectionalLight3D whose angle sweeps to match the
# visible sun band, a matching moon band at night, and bulk on/off
# toggling for every streetlight (StreetFurniture.gd's lamp posts).
#
# time_of_day: 0=midnight, 0.25=dawn ends/full day begins, 0.75=day ends/
# dusk begins, wraps at 1.0.

static var DAY_LENGTH_SECONDS := 600.0  # live-tunable, e.g. gcmd.py run "DaySkySystem.DAY_LENGTH_SECONDS = 120.0"
static var lamp_light_on: bool = false  # read by StreetFurniture.gd when a NEW lamp post spawns, so it starts in the right state

const SKY_DAY_TEX := preload("res://assets/textures/sky_day.png")
const SKY_NIGHT_TEX := preload("res://assets/textures/sky_night.png")
const CLIFF_TEX := preload("res://assets/textures/cliff_rock.png")

const CEILING_SKY_SHADER := preload("res://shaders/ceiling_sky.gdshader")
const WALL_CLIFF_SKY_SHADER := preload("res://shaders/wall_cliff_sky.gdshader")

const DAWN_START := 0.15
const DAY_START := 0.25
const DAY_END := 0.75
const DUSK_END := 0.85

# Color/night-mix only -- "blue during the day -> red at dusk -> night ->
# red at dawn -> blue" (day and night entries are pure white/night-
# texture; the ONLY place red shows up is the dawn/dusk entries in
# between). Interpolated with smoothstep easing, not raw linear, between
# entries -- requested directly ("make sure the transition from day to
# night is smooth"). Band POSITION is intentionally NOT in this table --
# see _sun_moon_state()'s own comment for why that has to be computed
# separately.
const COLOR_KEYFRAMES := [
	[0.0,  1.0, 1.0, 1.0, 1.0],
	[DAWN_START, 1.0, 1.0, 1.0, 1.0],
	[0.20, 0.5, 1.6, 0.6, 0.4],
	[DAY_START,  0.0, 1.0, 1.0, 1.0],
	[DAY_END,    0.0, 1.0, 1.0, 1.0],
	[0.80, 0.5, 1.6, 0.6, 0.4],
	[DUSK_END,   1.0, 1.0, 1.0, 1.0],
	[1.0,  1.0, 1.0, 1.0, 1.0],
]

var time_of_day: float = 0.27  # start mid-morning, already light out
var cloud_drift: float = 0.0
var ceiling_material: ShaderMaterial
var wall_material: ShaderMaterial
var sun: DirectionalLight3D
var station: Node3D
var env: Environment

## `ring_mesh` is StationRingBuilder's single "RingMesh" node -- floor/
## ceiling/wall are surfaces 0/1/2 of ONE ArrayMesh (see that file's own
## build() for the exact commit order this depends on), not separate
## nodes, so this sets per-SURFACE overrides rather than a whole-instance
## material_override. Must run AFTER ToonShading.apply_to_world(ring_mesh)
## -- that call overwrites every surface's material uniformly with its
## own toon.gdshader instance; these two custom shaders (already their
## own self-contained cel-banded/unshaded logic, not meant to go through
## that conversion at all) need to land last, or ToonShading clobbers them.
## `p_env` (optional) is the WorldEnvironment's Environment resource --
## ambient light tracks day/night here (bright by day -- "the station is
## too dark in the daytime," requested directly -- gently dimmer by
## night, still nowhere near the old near-black default that caused an
## earlier session's "shadow problem").
func setup(p_station: Node3D, p_sun: DirectionalLight3D, ring_mesh: MeshInstance3D,
		ceiling_height: float, wall_tile: float, radius: float, tile_ceiling: float,
		p_env: Environment = null) -> void:
	station = p_station
	sun = p_sun
	env = p_env

	ceiling_material = ShaderMaterial.new()
	ceiling_material.shader = CEILING_SKY_SHADER
	ceiling_material.set_shader_parameter("sky_day_texture", SKY_DAY_TEX)
	ceiling_material.set_shader_parameter("sky_night_texture", SKY_NIGHT_TEX)
	ring_mesh.set_surface_override_material(1, ceiling_material)

	wall_material = ShaderMaterial.new()
	wall_material.shader = WALL_CLIFF_SKY_SHADER
	wall_material.set_shader_parameter("cliff_texture", CLIFF_TEX)
	wall_material.set_shader_parameter("sky_day_texture", SKY_DAY_TEX)
	wall_material.set_shader_parameter("sky_night_texture", SKY_NIGHT_TEX)
	wall_material.set_shader_parameter("wall_v_max", ceiling_height / wall_tile)
	wall_material.set_shader_parameter("ring_radius", radius)
	wall_material.set_shader_parameter("sky_tile_scale", tile_ceiling)
	ring_mesh.set_surface_override_material(2, wall_material)

	_apply(0.0)  # first frame's worth, before _process() runs

static func _lerp_color_keyframes(t: float) -> Array:
	for i in range(COLOR_KEYFRAMES.size() - 1):
		var a: Array = COLOR_KEYFRAMES[i]
		var b: Array = COLOR_KEYFRAMES[i + 1]
		if t >= a[0] and t <= b[0]:
			var span: float = b[0] - a[0]
			var f: float = (t - a[0]) / span if span > 0.0001 else 0.0
			f = smoothstep(0.0, 1.0, f)  # eased, not linear -- smoother crossfade
			var out := []
			for k in range(1, a.size()):
				out.append(lerp(float(a[k]), float(b[k]), f))
			return out
	var last: Array = COLOR_KEYFRAMES[COLOR_KEYFRAMES.size() - 1]
	return last.slice(1)

## Sun position sweeps west->east across the DAY span (dawn->dusk); the
## moon sweeps the SAME west->east path across its own NIGHT span (dusk->
## midnight->dawn) -- "a band of moonlight that travels along the same
## path as the daylight," not literally the sun's own continuing
## position. Computed as explicit, continuous phases rather than read
## from a keyframe table sharing the day's own -- a real bug caught
## before it shipped: a single band_pos keyframe table wrapping at t=1->0
## had DIFFERENT values at those two endpoints (harmless for the sun,
## always zero-intensity at night regardless; NOT harmless for the moon,
## fully visible right through that exact wrap point -- it would have
## visibly teleported from one wall to the other at the stroke of
## midnight).
static func _sun_moon_state(t: float) -> Dictionary:
	var sun_intensity := 0.0
	var sun_pos := 0.0
	if t >= DAWN_START and t <= DUSK_END:
		sun_pos = (t - DAWN_START) / (DUSK_END - DAWN_START)
		if t < DAY_START:
			sun_intensity = smoothstep(DAWN_START, DAY_START, t)
		elif t > DAY_END:
			sun_intensity = 1.0 - smoothstep(DAY_END, DUSK_END, t)
		else:
			sun_intensity = 1.0

	var moon_intensity := 0.0
	var moon_pos := 0.0
	var night_len := (1.0 - DUSK_END) + DAWN_START
	var night_elapsed := -1.0
	if t >= DUSK_END:
		night_elapsed = t - DUSK_END
	elif t <= DAWN_START:
		night_elapsed = (1.0 - DUSK_END) + t
	if night_elapsed >= 0.0:
		moon_pos = night_elapsed / night_len
		var fade_len := night_len * 0.08
		var fade_in := smoothstep(0.0, fade_len, night_elapsed)
		var fade_out := smoothstep(0.0, fade_len, night_len - night_elapsed)
		moon_intensity = minf(fade_in, fade_out)

	return {
		"sun_intensity": sun_intensity, "sun_pos": sun_pos,
		"moon_intensity": moon_intensity, "moon_pos": moon_pos,
	}

func _process(delta: float) -> void:
	time_of_day = fposmod(time_of_day + delta / DAY_LENGTH_SECONDS, 1.0)
	cloud_drift += delta * 0.0015  # slow -- "I would like it if [the clouds] did [move]," but gently
	_apply(delta)

func _apply(_delta: float) -> void:
	if ceiling_material == null:
		return
	var c := _lerp_color_keyframes(time_of_day)
	var night_mix: float = c[0]
	var tint := Color(c[1], c[2], c[3])

	var sm := _sun_moon_state(time_of_day)
	var sun_intensity: float = sm["sun_intensity"]
	var sun_pos: float = sm["sun_pos"]
	var moon_intensity: float = sm["moon_intensity"]
	var moon_pos: float = sm["moon_pos"]

	var width: float = SpaceStation.WIDTH
	var sun_center: float = lerp(-width * 0.5, width * 0.5, sun_pos)
	var moon_center: float = lerp(-width * 0.5, width * 0.5, moon_pos)
	var half_width: float = width * 0.025  # 5% of the ceiling's width, requested directly

	var sun_color := Color(tint.r, tint.g * 0.95, tint.b * 0.85)
	var moon_color := Color(0.75, 0.8, 0.95)  # pale, cool moonlight -- distinct from the sun's warm arc

	ceiling_material.set_shader_parameter("night_mix", night_mix)
	ceiling_material.set_shader_parameter("day_tint", tint)
	ceiling_material.set_shader_parameter("cloud_drift", cloud_drift)
	ceiling_material.set_shader_parameter("band_color", sun_color)
	ceiling_material.set_shader_parameter("band_center", sun_center)
	ceiling_material.set_shader_parameter("band_half_width", half_width)
	ceiling_material.set_shader_parameter("band_intensity", sun_intensity)
	ceiling_material.set_shader_parameter("moon_color", moon_color)
	ceiling_material.set_shader_parameter("moon_center", moon_center)
	ceiling_material.set_shader_parameter("moon_half_width", half_width)
	ceiling_material.set_shader_parameter("moon_intensity", moon_intensity)

	wall_material.set_shader_parameter("night_mix", night_mix)
	wall_material.set_shader_parameter("day_tint", tint)
	wall_material.set_shader_parameter("cloud_drift", cloud_drift)

	if sun:
		# The light's own direction sweeps the same west->east arc the
		# visible band does, so shadows fall consistently with what's
		# painted on the ceiling. -35/40 (pitch/base yaw) matches this
		# project's original static "noon" sun; the sweep just adds/
		# subtracts yaw around that. Rotation isn't updated at night
		# (sun_pos holds its last day value) -- harmless, since
		# sun_intensity/shadow_enabled are both off by then.
		var sweep_deg: float = lerp(-55.0, 55.0, sun_pos)
		sun.rotation_degrees = Vector3(-35.0, 40.0 + sweep_deg, 0.0)
		sun.light_color = Color(tint.r, tint.g * 0.97, tint.b * 0.9)
		sun.light_energy = 0.15 + sun_intensity * 1.15
		sun.shadow_enabled = sun_intensity > 0.05

	if env:
		# Requested directly ("the station is too dark in the daytime"):
		# 2.0 by day (up from 1.2), 1.0 by night -- both still well above
		# the original near-black 0.6 default that caused an earlier
		# session's "shadow problem" in the first place.
		env.ambient_light_energy = lerp(1.0, 2.0, 1.0 - night_mix)

	var should_lights_be_on := night_mix > 0.5
	if should_lights_be_on != lamp_light_on:
		lamp_light_on = should_lights_be_on
		if is_inside_tree():
			get_tree().call_group("lamp_lights", "set_visible", lamp_light_on)
