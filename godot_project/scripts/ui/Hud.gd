extends CanvasLayer

# Always-on gameplay HUD (unlike GameMenu, this is never paused/hidden):
# a linear compass along the top, and a top-right toast for things like
# "Mission Complete!".
#
# Compass arrow rules for the tracked quest (QuestManager.tracked_quest_id):
#   - has an incomplete "kill" objective -> a red arrow per living target
#     found in that quest's target_group.
#   - otherwise, while active and not turned in -> one green arrow at the
#     quest's map_marker (the same point the overmap shows).
#   - turned in / no tracked quest -> nothing.

const VISIBLE_DEGREES := 140.0
const TICK_DEGREES := [0, 45, 90, 135, 180, 225, 270, 315]
const TICK_LABELS := {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}

var _compass: Control
var _toast: Label
var _toast_tween: Tween
var _health_bar: ProgressBar
var _health_label: Label
var _player_health: Health = null
var _fps_label: Label

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 5
	_build_ui()
	QuestManager.quest_completed.connect(func(_id): show_notification("Mission Complete!"))

func _build_ui() -> void:
	_compass = Control.new()
	_compass.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_compass.custom_minimum_size = Vector2(0, 46)
	_compass.offset_top = 14
	_compass.draw.connect(_draw_compass)
	add_child(_compass)

	var health_box := VBoxContainer.new()
	health_box.set_anchors_preset(Control.PRESET_TOP_LEFT)
	health_box.offset_left = 24
	health_box.offset_top = 74
	add_child(health_box)

	_health_bar = ProgressBar.new()
	_health_bar.min_value = 0
	_health_bar.max_value = 100
	_health_bar.value = 100
	_health_bar.show_percentage = false
	_health_bar.custom_minimum_size = Vector2(220, 22)
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0, 0, 0, 0.5)
	bg.set_corner_radius_all(4)
	var fill := StyleBoxFlat.new()
	fill.bg_color = Color(0.8, 0.18, 0.18)
	fill.set_corner_radius_all(4)
	_health_bar.add_theme_stylebox_override("background", bg)
	_health_bar.add_theme_stylebox_override("fill", fill)
	health_box.add_child(_health_bar)

	_health_label = Label.new()
	_health_label.text = "100 / 100"
	_health_label.add_theme_font_size_override("font_size", 16)
	_health_label.add_theme_color_override("font_color", Color(1, 1, 1))
	_health_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	_health_label.add_theme_constant_override("outline_size", 4)
	health_box.add_child(_health_label)

	_toast = Label.new()
	_toast.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_toast.offset_left = -320
	_toast.offset_top = 20
	_toast.offset_right = -20
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_toast.add_theme_font_size_override("font_size", 26)
	_toast.add_theme_color_override("font_color", Color(1, 1, 1))
	_toast.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	_toast.add_theme_constant_override("outline_size", 6)
	_toast.modulate.a = 0.0
	add_child(_toast)

	_fps_label = Label.new()
	_fps_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_fps_label.offset_left = -160
	_fps_label.offset_top = -140
	_fps_label.offset_right = -10
	_fps_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_fps_label.add_theme_font_size_override("font_size", 16)
	_fps_label.add_theme_color_override("font_color", Color(1, 1, 0.3))
	_fps_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	_fps_label.add_theme_constant_override("outline_size", 5)
	add_child(_fps_label)

func _process(_delta: float) -> void:
	_compass.queue_redraw()
	_fps_label.text = "%d fps\nobj %d\nprim %d\ndraw %d\nphys %d" % [
		Engine.get_frames_per_second(),
		Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		Performance.get_monitor(Performance.PHYSICS_3D_ACTIVE_OBJECTS),
	]
	if _player_health == null:
		_try_connect_health()

func _try_connect_health() -> void:
	var player := get_tree().get_first_node_in_group("player")
	if player == null:
		return
	var h: Health = player.get_node_or_null("Health")
	if h == null:
		return
	_player_health = h
	h.damaged.connect(func(_amount, _attacker): _update_health_bar())
	h.healed.connect(func(_amount): _update_health_bar())
	_update_health_bar()

func _update_health_bar() -> void:
	if _player_health == null:
		return
	_health_bar.max_value = _player_health.max_health
	_health_bar.value = _player_health.current
	_health_label.text = "%d / %d" % [int(round(_player_health.current)), int(_player_health.max_health)]

func show_notification(text: String) -> void:
	_toast.text = text
	if _toast_tween:
		_toast_tween.kill()
	_toast.modulate.a = 0.0
	_toast_tween = create_tween()
	_toast_tween.tween_property(_toast, "modulate:a", 1.0, 0.3)
	_toast_tween.tween_interval(2.6)
	_toast_tween.tween_property(_toast, "modulate:a", 0.0, 0.6)

## Undoes the space station ring's own current spin, when there is one,
## so the compass reads relative to the STATION instead of the fixed
## world frame. Without this, a player standing still inside a rotating
## station gets correctly carried around by the spin (see
## StationPlayer.gd's co-rotation fix) and their world-frame heading
## drifts steadily in one direction for it -- confirmed live as "keeps
## drifting North" even with no input -- even though, relative to the
## floor they're actually standing on, they haven't turned at all. A
## real station's compass would be calibrated to the station, not the
## stars, for exactly this reason. Identity (no correction) outside a
## space station, so the normal game's compass is unaffected.
func _compass_basis() -> Basis:
	var station := get_tree().get_first_node_in_group("space_station")
	if station == null:
		return Basis.IDENTITY
	var ring_body: Node3D = station.get_node("RingBody")
	return ring_body.global_transform.basis.inverse()

func _player_heading() -> float:
	var player := get_tree().get_first_node_in_group("player") as Node3D
	if player == null:
		return 0.0
	var fwd := _compass_basis() * (-player.global_transform.basis.z)
	return rad_to_deg(atan2(fwd.x, -fwd.z))

func _bearing_to(pos: Vector3) -> float:
	var player := get_tree().get_first_node_in_group("player") as Node3D
	if player == null:
		return 0.0
	var d := _compass_basis() * (pos - player.global_position)
	return rad_to_deg(atan2(d.x, -d.z))

func _wrap180(deg: float) -> float:
	var d := fmod(deg + 180.0, 360.0)
	if d < 0:
		d += 360.0
	return d - 180.0

func _get_targets() -> Array:
	# Returns [{pos: Vector3, color: Color}] for whatever the tracked quest
	# wants shown right now.
	var out := []
	var qid := QuestManager.tracked_quest_id
	if qid == "" or not (QuestManager.is_active(qid) or QuestManager.is_completed(qid)):
		return out

	if QuestManager.is_completed(qid) and not QuestManager.is_turned_in(qid):
		var marker: Dictionary = QuestManager.get_map_marker(qid)
		if not marker.is_empty():
			out.append({"pos": Vector3(marker.get("x", 0.0), 0.0, marker.get("z", 0.0)), "color": Color(0.25, 1.0, 0.35)})
		return out

	if QuestManager.is_active(qid):
		var has_kill_objective := false
		for obj in QuestManager.get_objectives(qid):
			if obj.type == "kill":
				has_kill_objective = true
		var group := QuestManager.get_target_group(qid)
		if has_kill_objective and group != "":
			for node in get_tree().get_nodes_in_group(group):
				if is_instance_valid(node) and node is Node3D:
					var h = node.get_node_or_null("Health")
					if h == null or h.is_alive():
						out.append({"pos": node.global_position, "color": Color(1.0, 0.25, 0.2)})
			return out
		var marker: Dictionary = QuestManager.get_map_marker(qid)
		if not marker.is_empty():
			out.append({"pos": Vector3(marker.get("x", 0.0), 0.0, marker.get("z", 0.0)), "color": Color(0.25, 1.0, 0.35)})
	return out

func _draw_compass() -> void:
	var size: Vector2 = _compass.size
	if size.x <= 0:
		return
	var heading := _player_heading()
	var mid := size.x * 0.5

	_compass.draw_rect(Rect2(Vector2.ZERO, size), Color(0, 0, 0, 0.35), true)

	for deg in TICK_DEGREES:
		var rel := _wrap180(float(deg) - heading)
		if abs(rel) > VISIBLE_DEGREES * 0.5:
			continue
		var x := mid + (rel / VISIBLE_DEGREES) * size.x
		var is_cardinal: bool = int(deg) % 90 == 0
		_compass.draw_line(Vector2(x, size.y - (14 if is_cardinal else 8)), Vector2(x, size.y), Color(1, 1, 1, 0.8), 2.0)
		if is_cardinal:
			_compass.draw_string(ThemeDB.fallback_font, Vector2(x - 6, size.y - 18), TICK_LABELS[deg], HORIZONTAL_ALIGNMENT_CENTER, -1, 16, Color.WHITE)

	for t in _get_targets():
		var rel: float = _wrap180(_bearing_to(t.pos) - heading)
		var clamped: float = clamp(rel, -VISIBLE_DEGREES * 0.5, VISIBLE_DEGREES * 0.5)
		var x: float = mid + (clamped / VISIBLE_DEGREES) * size.x
		var points := PackedVector2Array([Vector2(x, 4), Vector2(x - 7, 16), Vector2(x + 7, 16)])
		_compass.draw_colored_polygon(points, t.color)

	# center marker (player's forward direction)
	_compass.draw_line(Vector2(mid, 0), Vector2(mid, size.y), Color(1, 1, 1, 0.9), 2.0)
