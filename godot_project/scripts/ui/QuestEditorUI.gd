extends CanvasLayer

# In-game quest / quest-giver / dialogue editor, toggled with F3 (same
# pattern as MapEditorUI's F2). Three panes, switched by tab buttons:
#   Quests        -- create/edit entries in data/quests.json
#   Quest Givers  -- create/edit entries in data/quest_givers.json: speaker
#                    name, one dialogue tree per quest-state condition, and
#                    a routine (time-of-day) + conditional (quest-state)
#                    waypoint schedule (see QuestGiverGeneric.gd, which is
#                    the runtime that actually reads this data)
#   (Dialogue graph -- a full-screen GraphEdit overlay, opened from a
#    Quest Giver's dialogue-state row, not a tab of its own)
#
# Waypoints referenced by the schedule editor are placed spatially in the
# F2 map editor (MapEditorUI's "Waypoints" category) and stored in
# data/waypoints.json (Waypoints autoload) -- this editor only offers
# them in dropdowns, it doesn't place them.
#
# Every "Save" button writes straight back to the relevant JSON file and
# tells the matching runtime autoload to reload its cache (QuestManager,
# QuestGiverGeneric) so a still-running game picks up the change without a
# restart -- same "no separate publish step" spirit as the map editor.
#
# Dialogue tree on-disk format (matches DialogBox.gd's runtime format
# exactly -- this editor just builds/edits that dictionary):
#   { "start": { "speaker": "Name", "text": "...",
#                "choices": [ { "text": "...", "next": "node_id_or_empty",
#                               "actions": [ {"type": "...", ...}, ... ] } ] } }

const HAND_FONT := preload("res://fonts/PatrickHand-Regular.ttf")
const PAPER_COLOR := Color(0.94, 0.90, 0.78)
const INK_COLOR := Color(0.16, 0.13, 0.11)
const PANEL_BORDER := Color(0.16, 0.13, 0.11)

const QUESTS_PATH := "res://data/quests.json"
const GIVERS_PATH := "res://data/quest_givers.json"

const OBJECTIVE_TYPES := ["fetch", "kill", "action", "quest"]
const QUEST_STATES := ["not_started", "active", "completed", "turned_in"]
const ACTION_TYPES := ["start_quest", "mark_turned_in", "give_item", "spawn_npcs", "set_flag", "custom"]

var active := false

var _theme: Theme
var _root: Control
var _hint_label: Label
var _toast_label: Label
var _toast_tween: Tween

var _tab_bar: HBoxContainer
var _quests_pane: Control
var _givers_pane: Control
var _graph_overlay: Control

var _quests: Dictionary = {}       # id -> quest def dict (working copy)
var _givers: Dictionary = {}       # npc_id -> giver def dict (working copy)

var _current_quest_id := ""
var _current_giver_id := ""

# --- Quests pane widgets ---
var _quests_list_box: VBoxContainer
var _qf_id_label: Label
var _qf_title: LineEdit
var _qf_desc: TextEdit
var _qf_autostart: CheckBox
var _qf_prereq: LineEdit
var _qf_objectives_box: VBoxContainer
var _qf_objective_rows: Array = []   # [{type_btn, target_edit, count_spin}]
var _qf_rewards_box: VBoxContainer
var _qf_reward_rows: Array = []      # [{item_edit, count_spin}]
var _qf_marker_x: LineEdit
var _qf_marker_z: LineEdit
var _qf_marker_label: LineEdit

# --- Quest Givers pane widgets ---
var _givers_list_box: VBoxContainer
var _gf_id_label: Label
var _gf_speaker: LineEdit
var _gf_states_box: VBoxContainer
var _gf_routine_box: VBoxContainer
var _gf_conditional_box: VBoxContainer

# --- Dialogue graph editing state (see _open_dialogue_graph()) ---
var _graph_edit: GraphEdit
var _graph_giver_id := ""
var _graph_state_index := -1
var _graph_nodes: Dictionary = {}   # node_id -> {gnode, speaker_edit, text_edit, footer, choices: [{hbox, text_edit, actions_btn, actions, next}]}
var _graph_node_counter := 0
var _main_panel: PanelContainer

# --- Action-list popup state (see _open_action_popup()) ---
var _action_popup: PopupPanel
var _action_rows_box: VBoxContainer
var _action_popup_choice: Dictionary = {}
var _action_rows: Array = []

const ACTION_FIELD_SPECS := {
	"start_quest": ["quest_id", "", "", ""],
	"mark_turned_in": ["quest_id", "", "", ""],
	"give_item": ["item_id", "count", "", ""],
	"spawn_npcs": ["kind", "count", "radius", "group (optional, for kill-quest tracking)"],
	"set_flag": ["flag", "value (true/false)", "", ""],
	"custom": ["id", "", "", ""],
}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 10
	_load_quests()
	_load_givers()
	_build_theme()
	_build_ui()
	_set_visible(false)


func _build_theme() -> void:
	_theme = Theme.new()
	_theme.default_font = HAND_FONT
	_theme.default_font_size = 18
	_theme.set_color("font_color", "Label", INK_COLOR)
	_theme.set_color("font_color", "Button", INK_COLOR)
	_theme.set_color("font_color", "LineEdit", INK_COLOR)
	_theme.set_color("font_color", "OptionButton", INK_COLOR)
	_theme.set_color("font_color", "GraphNode", INK_COLOR)


# ---------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------

func _load_quests() -> void:
	_quests = _read_json_dict_of_list(QUESTS_PATH, "quests")


func _load_givers() -> void:
	_givers = _read_json(GIVERS_PATH)


func _read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	return data if typeof(data) == TYPE_DICTIONARY else {}


## quests.json is shaped as {"quests": [ {id: ..., ...}, ... ]} on disk
## (a list, for readable hand-editing) but this editor wants it keyed by
## id in memory -- converts both ways.
func _read_json_dict_of_list(path: String, list_key: String) -> Dictionary:
	var data := _read_json(path)
	var out := {}
	for entry in data.get(list_key, []):
		out[entry["id"]] = entry
	return out


func _save_quests() -> void:
	var list: Array = []
	var ids := _quests.keys()
	ids.sort()
	for id in ids:
		list.append(_quests[id])
	var f := FileAccess.open(QUESTS_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"quests": list}, "  "))
		f.close()
	QuestManager.definitions.clear()
	for id in _quests:
		QuestManager.definitions[id] = _quests[id]
	_show_toast()


func _save_givers() -> void:
	var f := FileAccess.open(GIVERS_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(_givers, "  "))
		f.close()   # must actually be closed before reload_cache() reads it back below, or it can read back empty/stale
	QuestGiverGeneric.reload_cache()
	_show_toast()


# ---------------------------------------------------------------
# Top-level UI shell + toggling
# ---------------------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_quest_editor"):
		_set_visible(not active)
		return
	if not active:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_S and event.ctrl_pressed:
			_save_current_pane()
			get_viewport().set_input_as_handled()


func _save_current_pane() -> void:
	if _graph_overlay.visible:
		_save_graph_to_giver()
	_save_quests()
	_save_givers()


func _set_visible(on: bool) -> void:
	active = on
	_root.visible = on
	get_tree().paused = on
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if on else Input.MOUSE_MODE_CAPTURED
	if on:
		_refresh_quests_list()
		_refresh_givers_list()


func _build_ui() -> void:
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.theme = _theme
	add_child(_root)

	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.45)
	_root.add_child(dim)

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = Vector2(-460, -320)
	panel.custom_minimum_size = Vector2(920, 640)
	var style := StyleBoxFlat.new()
	style.bg_color = PAPER_COLOR
	style.set_corner_radius_all(10)
	style.set_border_width_all(3)
	style.border_color = PANEL_BORDER
	style.set_content_margin_all(16)
	panel.add_theme_stylebox_override("panel", style)
	_root.add_child(panel)
	_main_panel = panel

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	panel.add_child(vbox)

	var title := Label.new()
	title.text = "Quest Editor"
	title.add_theme_font_size_override("font_size", 28)
	vbox.add_child(title)

	_tab_bar = HBoxContainer.new()
	vbox.add_child(_tab_bar)
	_add_tab_button("Quests", func(): _show_pane(_quests_pane))
	_add_tab_button("Quest Givers", func(): _show_pane(_givers_pane))

	var body := Control.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.custom_minimum_size = Vector2(0, 520)
	vbox.add_child(body)

	_quests_pane = _build_quests_pane()
	_givers_pane = _build_givers_pane()
	body.add_child(_quests_pane)
	body.add_child(_givers_pane)
	_show_pane(_quests_pane)

	_hint_label = Label.new()
	_hint_label.text = "[Ctrl+S] save   [F3] close"
	_hint_label.add_theme_font_size_override("font_size", 14)
	vbox.add_child(_hint_label)

	_toast_label = Label.new()
	_toast_label.text = "✓ Saved"
	_toast_label.add_theme_color_override("font_color", Color(0.15, 0.5, 0.15))
	_toast_label.modulate.a = 0.0
	vbox.add_child(_toast_label)

	_graph_overlay = _build_graph_overlay()
	_root.add_child(_graph_overlay)

	_action_popup = _build_action_popup()
	_root.add_child(_action_popup)


func _add_tab_button(text: String, on_press: Callable) -> void:
	var btn := Button.new()
	btn.text = text
	btn.pressed.connect(on_press)
	_tab_bar.add_child(btn)


func _show_pane(pane: Control) -> void:
	_quests_pane.visible = pane == _quests_pane
	_givers_pane.visible = pane == _givers_pane


func _show_toast() -> void:
	if _toast_tween:
		_toast_tween.kill()
	_toast_label.modulate.a = 1.0
	_toast_tween = create_tween()
	_toast_tween.tween_interval(0.6)
	_toast_tween.tween_property(_toast_label, "modulate:a", 0.0, 0.6)


## Small reusable "labeled row" builder used all over both panes -- an
## HBox with a fixed-width label followed by whatever control is passed.
func _labeled(label_text: String, control: Control, label_width: float = 110.0) -> HBoxContainer:
	var row := HBoxContainer.new()
	var lbl := Label.new()
	lbl.text = label_text
	lbl.custom_minimum_size = Vector2(label_width, 0)
	row.add_child(lbl)
	control.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(control)
	return row


func _remove_button() -> Button:
	var b := Button.new()
	b.text = "x"
	b.custom_minimum_size = Vector2(28, 0)
	return b


func _quest_ids_sorted() -> Array:
	var ids := _quests.keys()
	ids.sort()
	return ids


# ---------------------------------------------------------------
# Quests pane
# ---------------------------------------------------------------

func _build_quests_pane() -> Control:
	var pane := HBoxContainer.new()
	pane.add_theme_constant_override("separation", 12)

	var left := VBoxContainer.new()
	left.custom_minimum_size = Vector2(200, 0)
	pane.add_child(left)
	var new_btn := Button.new()
	new_btn.text = "+ New Quest"
	new_btn.pressed.connect(_on_new_quest)
	left.add_child(new_btn)
	var list_scroll := ScrollContainer.new()
	list_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(list_scroll)
	_quests_list_box = VBoxContainer.new()
	_quests_list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list_scroll.add_child(_quests_list_box)

	var right_scroll := ScrollContainer.new()
	right_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pane.add_child(right_scroll)
	var form := VBoxContainer.new()
	form.add_theme_constant_override("separation", 8)
	form.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_scroll.add_child(form)

	_qf_id_label = Label.new()
	form.add_child(_qf_id_label)

	_qf_title = LineEdit.new()
	_qf_title.placeholder_text = "Title"
	_qf_title.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Title:", _qf_title))

	_qf_desc = TextEdit.new()
	_qf_desc.custom_minimum_size = Vector2(0, 60)
	_qf_desc.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	_qf_desc.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Description:", _qf_desc))

	_qf_autostart = CheckBox.new()
	_qf_autostart.text = "Auto-start (active from launch, no quest-giver needed)"
	_qf_autostart.toggled.connect(func(_v): _commit_and_save_quest())
	form.add_child(_qf_autostart)

	_qf_prereq = LineEdit.new()
	_qf_prereq.placeholder_text = "comma-separated quest ids, or blank"
	_qf_prereq.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Prereq quests:", _qf_prereq))

	var obj_title := Label.new()
	obj_title.text = "Objectives"
	obj_title.add_theme_font_size_override("font_size", 20)
	form.add_child(obj_title)
	_qf_objectives_box = VBoxContainer.new()
	form.add_child(_qf_objectives_box)
	var add_obj := Button.new()
	add_obj.text = "+ Add Objective"
	add_obj.pressed.connect(func(): _add_objective_row({"type": "fetch", "target": "", "count": 1}))
	form.add_child(add_obj)

	var rew_title := Label.new()
	rew_title.text = "Rewards (items)"
	rew_title.add_theme_font_size_override("font_size", 20)
	form.add_child(rew_title)
	_qf_rewards_box = VBoxContainer.new()
	form.add_child(_qf_rewards_box)
	var add_rew := Button.new()
	add_rew.text = "+ Add Reward Item"
	add_rew.pressed.connect(func(): _add_reward_row({"id": "", "count": 1}))
	form.add_child(add_rew)

	var marker_title := Label.new()
	marker_title.text = "Map Marker"
	marker_title.add_theme_font_size_override("font_size", 20)
	form.add_child(marker_title)
	_qf_marker_x = LineEdit.new()
	_qf_marker_x.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Marker X:", _qf_marker_x))
	_qf_marker_z = LineEdit.new()
	_qf_marker_z.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Marker Z:", _qf_marker_z))
	_qf_marker_label = LineEdit.new()
	_qf_marker_label.focus_exited.connect(_commit_and_save_quest)
	form.add_child(_labeled("Marker Label:", _qf_marker_label))

	var del_btn := Button.new()
	del_btn.text = "Delete This Quest"
	del_btn.pressed.connect(_on_delete_quest)
	form.add_child(del_btn)

	return pane


func _refresh_quests_list() -> void:
	for c in _quests_list_box.get_children():
		c.queue_free()
	for id in _quest_ids_sorted():
		var btn := Button.new()
		btn.text = _quests[id].get("title", id)
		btn.pressed.connect(_select_quest.bind(id))
		_quests_list_box.add_child(btn)
	if _current_quest_id == "" and not _quest_ids_sorted().is_empty():
		_select_quest(_quest_ids_sorted()[0])
	elif _current_quest_id != "":
		_select_quest(_current_quest_id)


func _on_new_quest() -> void:
	var n := 1
	while _quests.has("quest_%d" % n):
		n += 1
	var id := "quest_%d" % n
	_quests[id] = {
		"id": id, "title": "New Quest", "description": "", "auto_start": false,
		"prereq": [], "objectives": [], "rewards": {"items": []},
		"map_marker": {"x": 0.0, "z": 0.0, "label": "?"},
	}
	_save_quests()
	_refresh_quests_list()
	_select_quest(id)


func _select_quest(id: String) -> void:
	_current_quest_id = id
	var q: Dictionary = _quests.get(id, {})
	_qf_id_label.text = "ID: %s" % id
	_qf_title.text = q.get("title", "")
	_qf_desc.text = q.get("description", "")
	_qf_autostart.button_pressed = q.get("auto_start", false)
	_qf_prereq.text = ", ".join(q.get("prereq", []))
	_qf_marker_x.text = str(q.get("map_marker", {}).get("x", 0.0))
	_qf_marker_z.text = str(q.get("map_marker", {}).get("z", 0.0))
	_qf_marker_label.text = q.get("map_marker", {}).get("label", "")

	for c in _qf_objectives_box.get_children():
		c.queue_free()
	_qf_objective_rows.clear()
	for o in q.get("objectives", []):
		_add_objective_row(o)

	for c in _qf_rewards_box.get_children():
		c.queue_free()
	_qf_reward_rows.clear()
	for r in q.get("rewards", {}).get("items", []):
		_add_reward_row(r)


func _add_objective_row(o: Dictionary) -> void:
	var row := HBoxContainer.new()
	var type_btn := OptionButton.new()
	for t in OBJECTIVE_TYPES:
		type_btn.add_item(t)
	var idx := OBJECTIVE_TYPES.find(o.get("type", "fetch"))
	type_btn.selected = max(idx, 0)
	type_btn.item_selected.connect(func(_i): _commit_and_save_quest())
	row.add_child(type_btn)
	var target_edit := LineEdit.new()
	target_edit.placeholder_text = "target (item/faction/action/quest id)"
	target_edit.text = str(o.get("target", ""))
	target_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	target_edit.focus_exited.connect(_commit_and_save_quest)
	row.add_child(target_edit)
	var count_spin := SpinBox.new()
	count_spin.min_value = 1
	count_spin.max_value = 999
	count_spin.value = float(o.get("count", 1))
	count_spin.value_changed.connect(func(_v): _commit_and_save_quest())
	row.add_child(count_spin)
	var rm := _remove_button()
	rm.pressed.connect(func():
		_qf_objective_rows.erase(_find_row(_qf_objective_rows, row))
		row.queue_free()
		_commit_and_save_quest()
	)
	row.add_child(rm)
	_qf_objectives_box.add_child(row)
	_qf_objective_rows.append({"row": row, "type_btn": type_btn, "target_edit": target_edit, "count_spin": count_spin})


func _add_reward_row(r: Dictionary) -> void:
	var row := HBoxContainer.new()
	var item_edit := LineEdit.new()
	item_edit.placeholder_text = "item id"
	item_edit.text = str(r.get("id", ""))
	item_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	item_edit.focus_exited.connect(_commit_and_save_quest)
	row.add_child(item_edit)
	var count_spin := SpinBox.new()
	count_spin.min_value = 1
	count_spin.max_value = 999
	count_spin.value = float(r.get("count", 1))
	count_spin.value_changed.connect(func(_v): _commit_and_save_quest())
	row.add_child(count_spin)
	var rm := _remove_button()
	rm.pressed.connect(func():
		_qf_reward_rows.erase(_find_row(_qf_reward_rows, row))
		row.queue_free()
		_commit_and_save_quest()
	)
	row.add_child(rm)
	_qf_rewards_box.add_child(row)
	_qf_reward_rows.append({"row": row, "item_edit": item_edit, "count_spin": count_spin})


## Rows are removed from a live scene AND a parallel data array together
## (queue_free() is deferred, so the array can't just filter on
## is_instance_valid() immediately after) -- this finds the data entry
## that wraps a given already-being-freed row Control.
func _find_row(rows: Array, row_control: Control) -> Dictionary:
	for r in rows:
		if r["row"] == row_control:
			return r
	return {}


func _commit_and_save_quest() -> void:
	if _current_quest_id == "" or not _quests.has(_current_quest_id):
		return
	var objectives := []
	for r in _qf_objective_rows:
		objectives.append({
			"type": OBJECTIVE_TYPES[r["type_btn"].selected],
			"target": r["target_edit"].text,
			"count": int(r["count_spin"].value),
		})
	var rewards := []
	for r in _qf_reward_rows:
		rewards.append({"id": r["item_edit"].text, "count": int(r["count_spin"].value)})
	var prereq: Array = []
	for p in _qf_prereq.text.split(","):
		var s := p.strip_edges()
		if s != "":
			prereq.append(s)
	var def := {
		"id": _current_quest_id,
		"title": _qf_title.text,
		"description": _qf_desc.text,
		"auto_start": _qf_autostart.button_pressed,
		"prereq": prereq,
		"objectives": objectives,
		"rewards": {"items": rewards},
		"map_marker": {
			"x": float(_qf_marker_x.text) if _qf_marker_x.text.is_valid_float() else 0.0,
			"z": float(_qf_marker_z.text) if _qf_marker_z.text.is_valid_float() else 0.0,
			"label": _qf_marker_label.text,
		},
	}
	# Preserve any hand-authored fields this editor doesn't expose yet
	# (e.g. "target_group") rather than silently dropping them on save.
	var old: Dictionary = _quests.get(_current_quest_id, {})
	for key in old:
		if not def.has(key):
			def[key] = old[key]
	_quests[_current_quest_id] = def
	_save_quests()
	_refresh_quests_list()


func _on_delete_quest() -> void:
	if _current_quest_id == "":
		return
	_quests.erase(_current_quest_id)
	_current_quest_id = ""
	_save_quests()
	_refresh_quests_list()


# ---------------------------------------------------------------
# Quest Givers pane
# ---------------------------------------------------------------

func _giver_ids_sorted() -> Array:
	var ids := _givers.keys()
	ids.sort()
	return ids


## condition == null ("always") is a valid, useful catch-all -- put it
## first in every condition dropdown.
func _quest_condition_option_button(selected_quest_id: String) -> OptionButton:
	var btn := OptionButton.new()
	btn.add_item("(always)")
	var ids := _quest_ids_sorted()
	for id in ids:
		btn.add_item(id)
	var idx := ids.find(selected_quest_id)
	btn.selected = idx + 1 if idx >= 0 else 0
	return btn


func _quest_state_option_button(selected_state: String) -> OptionButton:
	var btn := OptionButton.new()
	for s in QUEST_STATES:
		btn.add_item(s)
	var idx := QUEST_STATES.find(selected_state)
	btn.selected = max(idx, 0)
	return btn


func _waypoint_option_button(selected_id: String) -> OptionButton:
	var btn := OptionButton.new()
	var ids: Array = Waypoints.all_ids()
	if ids.is_empty():
		btn.add_item("(no waypoints placed -- use F2's Waypoints category)")
		btn.disabled = true
		return btn
	for id in ids:
		btn.add_item(Waypoints.get_label(id))
	var idx := ids.find(selected_id)
	btn.selected = max(idx, 0)
	btn.set_meta("waypoint_ids", ids)
	return btn


func _selected_waypoint_id(btn: OptionButton) -> String:
	var ids: Array = btn.get_meta("waypoint_ids", [])
	if ids.is_empty() or btn.selected < 0 or btn.selected >= ids.size():
		return ""
	return ids[btn.selected]


func _build_givers_pane() -> Control:
	var pane := HBoxContainer.new()
	pane.add_theme_constant_override("separation", 12)
	pane.visible = false

	var left := VBoxContainer.new()
	left.custom_minimum_size = Vector2(200, 0)
	pane.add_child(left)
	var new_btn := Button.new()
	new_btn.text = "+ New Quest Giver"
	new_btn.pressed.connect(_on_new_giver)
	left.add_child(new_btn)
	var list_scroll := ScrollContainer.new()
	list_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(list_scroll)
	_givers_list_box = VBoxContainer.new()
	_givers_list_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list_scroll.add_child(_givers_list_box)

	var right_scroll := ScrollContainer.new()
	right_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pane.add_child(right_scroll)
	var form := VBoxContainer.new()
	form.add_theme_constant_override("separation", 8)
	form.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_scroll.add_child(form)

	_gf_id_label = Label.new()
	form.add_child(_gf_id_label)

	_gf_speaker = LineEdit.new()
	_gf_speaker.placeholder_text = "Speaker name (shown in dialogue)"
	_gf_speaker.focus_exited.connect(_commit_and_save_giver_fields)
	form.add_child(_labeled("Speaker:", _gf_speaker))

	var note := Label.new()
	note.text = "Set this NPC's `npc_id` export field (in its .tscn) to match the ID above so it uses this data."
	note.autowrap_mode = TextServer.AUTOWRAP_WORD
	form.add_child(note)

	var states_title := Label.new()
	states_title.text = "Dialogue States (checked top to bottom, first match wins)"
	states_title.add_theme_font_size_override("font_size", 20)
	form.add_child(states_title)
	_gf_states_box = VBoxContainer.new()
	form.add_child(_gf_states_box)
	var add_state := Button.new()
	add_state.text = "+ Add Dialogue State"
	add_state.pressed.connect(_on_add_dialogue_state)
	form.add_child(add_state)

	var routine_title := Label.new()
	routine_title.text = "Routine Schedule (time of day)"
	routine_title.add_theme_font_size_override("font_size", 20)
	form.add_child(routine_title)
	_gf_routine_box = VBoxContainer.new()
	form.add_child(_gf_routine_box)
	var add_routine := Button.new()
	add_routine.text = "+ Add Routine Entry"
	add_routine.pressed.connect(func(): _add_routine_row({"start_hour": 8.0, "end_hour": 20.0, "waypoint_id": ""}))
	form.add_child(add_routine)

	var cond_title := Label.new()
	cond_title.text = "Conditional Schedule (overrides routine when the condition holds)"
	cond_title.add_theme_font_size_override("font_size", 20)
	form.add_child(cond_title)
	_gf_conditional_box = VBoxContainer.new()
	form.add_child(_gf_conditional_box)
	var add_cond := Button.new()
	add_cond.text = "+ Add Conditional Entry"
	add_cond.pressed.connect(func(): _add_conditional_row({"condition": {"quest_id": "", "state": "active"}, "waypoint_id": ""}))
	form.add_child(add_cond)

	var del_btn := Button.new()
	del_btn.text = "Delete This Quest Giver"
	del_btn.pressed.connect(_on_delete_giver)
	form.add_child(del_btn)

	return pane


func _refresh_givers_list() -> void:
	for c in _givers_list_box.get_children():
		c.queue_free()
	for id in _giver_ids_sorted():
		var btn := Button.new()
		btn.text = _givers[id].get("speaker_name", id)
		btn.pressed.connect(_select_giver.bind(id))
		_givers_list_box.add_child(btn)
	if _current_giver_id == "" and not _giver_ids_sorted().is_empty():
		_select_giver(_giver_ids_sorted()[0])
	elif _current_giver_id != "":
		_select_giver(_current_giver_id)


func _on_new_giver() -> void:
	var n := 1
	while _givers.has("giver_%d" % n):
		n += 1
	var id := "giver_%d" % n
	_givers[id] = {
		"speaker_name": "New NPC",
		"dialogue_states": [
			{"condition": null, "tree": {"start": {"speaker": "New NPC", "text": "...", "choices": []}}}
		],
		"schedule": {"routine": [], "conditional": []},
	}
	_save_givers()
	_refresh_givers_list()
	_select_giver(id)


func _select_giver(id: String) -> void:
	_current_giver_id = id
	var g: Dictionary = _givers.get(id, {})
	_gf_id_label.text = "npc_id: %s" % id
	_gf_speaker.text = g.get("speaker_name", "")

	for c in _gf_states_box.get_children():
		c.queue_free()
	for idx in range(g.get("dialogue_states", []).size()):
		_add_dialogue_state_row(idx)

	for c in _gf_routine_box.get_children():
		c.queue_free()
	for r in g.get("schedule", {}).get("routine", []):
		_add_routine_row(r)

	for c in _gf_conditional_box.get_children():
		c.queue_free()
	for r in g.get("schedule", {}).get("conditional", []):
		_add_conditional_row(r)


func _commit_and_save_giver_fields() -> void:
	if _current_giver_id == "" or not _givers.has(_current_giver_id):
		return
	_givers[_current_giver_id]["speaker_name"] = _gf_speaker.text
	_save_givers()
	_refresh_givers_list()


func _on_delete_giver() -> void:
	if _current_giver_id == "":
		return
	_givers.erase(_current_giver_id)
	_current_giver_id = ""
	_save_givers()
	_refresh_givers_list()


## Dialogue state rows mutate _givers[...] directly and immediately
## (rather than being collected on a separate commit step) since the
## dialogue TREE itself is only ever edited through the graph overlay,
## which already operates on this same nested dictionary by reference --
## keeping the condition editing on the same immediate-write footing
## avoids a second, inconsistent "when does this actually save" rule.
func _add_dialogue_state_row(idx: int) -> void:
	var states: Array = _givers[_current_giver_id]["dialogue_states"]
	var entry: Dictionary = states[idx]
	var cond = entry.get("condition")
	var row := HBoxContainer.new()
	var quest_btn := _quest_condition_option_button(cond["quest_id"] if cond else "")
	row.add_child(quest_btn)
	var state_btn := _quest_state_option_button(cond["state"] if cond else "active")
	state_btn.disabled = cond == null
	row.add_child(state_btn)
	var apply := func():
		if quest_btn.selected == 0:
			entry["condition"] = null
			state_btn.disabled = true
		else:
			var qid: String = _quest_ids_sorted()[quest_btn.selected - 1]
			entry["condition"] = {"quest_id": qid, "state": QUEST_STATES[state_btn.selected]}
			state_btn.disabled = false
		_save_givers()
	quest_btn.item_selected.connect(func(_i): apply.call())
	state_btn.item_selected.connect(func(_i): apply.call())
	var edit_btn := Button.new()
	edit_btn.text = "Edit Dialogue"
	edit_btn.pressed.connect(_open_dialogue_graph.bind(_current_giver_id, idx))
	row.add_child(edit_btn)
	var rm := _remove_button()
	rm.pressed.connect(func():
		states.erase(entry)
		row.queue_free()
		_save_givers()
		call_deferred("_select_giver", _current_giver_id)
	)
	row.add_child(rm)
	_gf_states_box.add_child(row)


func _add_routine_row(entry: Dictionary) -> void:
	var routine: Array = _givers[_current_giver_id]["schedule"]["routine"]
	if not routine.has(entry):
		routine.append(entry)
	var row := HBoxContainer.new()
	var start_spin := SpinBox.new()
	start_spin.min_value = 0
	start_spin.max_value = 24
	start_spin.step = 0.5
	start_spin.value = float(entry.get("start_hour", 0.0))
	row.add_child(_labeled("From hour:", start_spin, 80))
	var end_spin := SpinBox.new()
	end_spin.min_value = 0
	end_spin.max_value = 24
	end_spin.step = 0.5
	end_spin.value = float(entry.get("end_hour", 24.0))
	row.add_child(_labeled("to:", end_spin, 30))
	var wp_btn := _waypoint_option_button(entry.get("waypoint_id", ""))
	row.add_child(wp_btn)
	var apply := func():
		entry["start_hour"] = start_spin.value
		entry["end_hour"] = end_spin.value
		entry["waypoint_id"] = _selected_waypoint_id(wp_btn)
		_save_givers()
	start_spin.value_changed.connect(func(_v): apply.call())
	end_spin.value_changed.connect(func(_v): apply.call())
	wp_btn.item_selected.connect(func(_i): apply.call())
	var rm := _remove_button()
	rm.pressed.connect(func():
		routine.erase(entry)
		row.queue_free()
		_save_givers()
	)
	row.add_child(rm)
	_gf_routine_box.add_child(row)


func _add_conditional_row(entry: Dictionary) -> void:
	var conditional: Array = _givers[_current_giver_id]["schedule"]["conditional"]
	if not conditional.has(entry):
		conditional.append(entry)
	var cond: Dictionary = entry.get("condition", {})
	var row := HBoxContainer.new()
	var quest_btn := _quest_condition_option_button(cond.get("quest_id", ""))
	row.add_child(quest_btn)
	var state_btn := _quest_state_option_button(cond.get("state", "active"))
	row.add_child(state_btn)
	var wp_btn := _waypoint_option_button(entry.get("waypoint_id", ""))
	row.add_child(wp_btn)
	var apply := func():
		if quest_btn.selected == 0:
			entry["condition"] = null
		else:
			entry["condition"] = {"quest_id": _quest_ids_sorted()[quest_btn.selected - 1], "state": QUEST_STATES[state_btn.selected]}
		entry["waypoint_id"] = _selected_waypoint_id(wp_btn)
		_save_givers()
	quest_btn.item_selected.connect(func(_i): apply.call())
	state_btn.item_selected.connect(func(_i): apply.call())
	wp_btn.item_selected.connect(func(_i): apply.call())
	var rm := _remove_button()
	rm.pressed.connect(func():
		conditional.erase(entry)
		row.queue_free()
		_save_givers()
	)
	row.add_child(rm)
	_gf_conditional_box.add_child(row)


func _on_add_dialogue_state() -> void:
	var states: Array = _givers[_current_giver_id]["dialogue_states"]
	states.append({"condition": null, "tree": {"start": {"speaker": _gf_speaker.text, "text": "...", "choices": []}}})
	_save_givers()
	_add_dialogue_state_row(states.size() - 1)


# ---------------------------------------------------------------
# Dialogue graph overlay (GraphEdit) -- edits ONE tree at a time, the one
# opened via a dialogue-state row's "Edit Dialogue" button. Each GraphNode
# is one dialogue node (dict key in the tree); each choice is a row inside
# that node with an output slot, connected to the target node's single
# input slot (always slot/child index 0, the speaker row) -- the
# connection itself IS the choice's "next" field, so there's no separate
# "next node id" text field to keep in sync by hand.
# ---------------------------------------------------------------

func _build_graph_overlay() -> Control:
	var overlay := Control.new()
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	overlay.visible = false

	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.7)
	overlay.add_child(dim)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_%s" % side, 36)
	overlay.add_child(margin)

	var vbox := VBoxContainer.new()
	margin.add_child(vbox)

	var toolbar := HBoxContainer.new()
	toolbar.add_theme_constant_override("separation", 12)
	vbox.add_child(toolbar)
	var title := Label.new()
	title.text = "Dialogue Editor"
	title.add_theme_font_size_override("font_size", 24)
	title.add_theme_color_override("font_color", Color(1, 1, 1))
	toolbar.add_child(title)
	var add_node_btn := Button.new()
	add_node_btn.text = "+ Node"
	add_node_btn.pressed.connect(_on_add_graph_node)
	toolbar.add_child(add_node_btn)
	var close_btn := Button.new()
	close_btn.text = "Save && Close"
	close_btn.pressed.connect(_close_dialogue_graph)
	toolbar.add_child(close_btn)

	var hint := Label.new()
	hint.text = "Drag from a choice's right-side dot to another node's left-side dot to link it. Select a node and press Delete to remove it (not \"start\")."
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.8))
	hint.add_theme_font_size_override("font_size", 14)
	vbox.add_child(hint)

	_graph_edit = GraphEdit.new()
	_graph_edit.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_graph_edit.right_disconnects = true
	_graph_edit.connection_request.connect(_on_graph_connection_request)
	_graph_edit.disconnection_request.connect(_on_graph_disconnection_request)
	_graph_edit.delete_nodes_request.connect(_on_graph_delete_nodes_request)
	vbox.add_child(_graph_edit)

	return overlay


func _open_dialogue_graph(giver_id: String, state_index: int) -> void:
	_graph_giver_id = giver_id
	_graph_state_index = state_index
	var tree: Dictionary = _givers[giver_id]["dialogue_states"][state_index]["tree"]
	_load_tree_into_graph(tree)
	_main_panel.visible = false
	_graph_overlay.visible = true


func _close_dialogue_graph() -> void:
	_save_graph_to_giver()
	_graph_overlay.visible = false
	_main_panel.visible = true
	_refresh_givers_list()


func _load_tree_into_graph(tree: Dictionary) -> void:
	for c in _graph_edit.get_children():
		if c is GraphNode:
			c.queue_free()
	_graph_edit.clear_connections()
	_graph_nodes.clear()
	_graph_node_counter = 0

	var ids: Array = tree.keys()
	ids.sort()
	if ids.has("start"):
		ids.erase("start")
		ids.push_front("start")
	if not ids.has("start"):
		# Every tree needs a "start" node (DialogBox.start() always enters
		# there) -- guarantee one exists even for a brand new tree.
		ids.push_front("start")
		tree["start"] = {"speaker": "", "text": "...", "choices": []}

	var col := 0
	var row := 0
	for id in ids:
		var node_data: Dictionary = tree[id]
		var gn := _create_graph_node(id, node_data.get("speaker", ""), node_data.get("text", ""))
		gn.position_offset = Vector2(col * 320, row * 260)
		col += 1
		if col > 2:
			col = 0
			row += 1
		for choice in node_data.get("choices", []):
			_add_choice_row(id, choice.get("text", ""), choice.get("actions", []), choice.get("next", ""))

	for id in _graph_nodes:
		for c in _graph_nodes[id].choices:
			if c["next"] != "" and _graph_nodes.has(c["next"]):
				_graph_edit.connect_node(id, c["hbox"].get_index(), c["next"], 0)


func _create_graph_node(id: String, speaker: String, text: String) -> GraphNode:
	var gn := GraphNode.new()
	gn.name = id
	gn.title = id
	gn.custom_minimum_size = Vector2(280, 0)

	var speaker_edit := LineEdit.new()
	speaker_edit.placeholder_text = "Speaker"
	speaker_edit.text = speaker
	speaker_edit.set_meta("row_kind", "input")
	gn.add_child(speaker_edit)

	var text_edit := TextEdit.new()
	text_edit.text = text
	text_edit.custom_minimum_size = Vector2(260, 70)
	text_edit.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	text_edit.set_meta("row_kind", "none")
	gn.add_child(text_edit)

	var footer := HBoxContainer.new()
	footer.set_meta("row_kind", "none")
	var add_choice_btn := Button.new()
	add_choice_btn.text = "+ Choice"
	add_choice_btn.pressed.connect(func(): _add_choice_row(id, "...", [], ""))
	footer.add_child(add_choice_btn)
	if id != "start":
		var del_node_btn := Button.new()
		del_node_btn.text = "Delete Node"
		del_node_btn.pressed.connect(func(): _delete_graph_node(id))
		footer.add_child(del_node_btn)
	gn.add_child(footer)

	_graph_edit.add_child(gn)
	_graph_nodes[id] = {"gnode": gn, "speaker_edit": speaker_edit, "text_edit": text_edit, "footer": footer, "choices": []}
	_refresh_slots(id)

	if id.begins_with("node_"):
		var n := id.substr(5).to_int()
		_graph_node_counter = max(_graph_node_counter, n)

	return gn


## Re-applies left/right slot flags to every direct child of the node, in
## its CURRENT child order -- GraphNode associates slot info with a child
## INDEX, not a specific child node, so this has to be redone any time a
## choice row is added, removed, or the footer gets shuffled back to last.
func _refresh_slots(id: String) -> void:
	var gn: GraphNode = _graph_nodes[id].gnode
	for i in range(gn.get_child_count()):
		var child := gn.get_child(i)
		match child.get_meta("row_kind", "none"):
			"input":
				gn.set_slot(i, true, 0, Color(0.85, 0.85, 0.85), false, 0, Color.WHITE)
			"choice":
				gn.set_slot(i, false, 0, Color.WHITE, true, 1, Color(1.0, 0.8, 0.3))
			_:
				gn.set_slot(i, false, 0, Color.WHITE, false, 0, Color.WHITE)


func _add_choice_row(id: String, text: String, actions: Array, next: String) -> void:
	var n: Dictionary = _graph_nodes[id]
	var gn: GraphNode = n.gnode
	var hbox := HBoxContainer.new()
	hbox.set_meta("row_kind", "choice")

	var text_edit := LineEdit.new()
	text_edit.text = text
	text_edit.placeholder_text = "choice text"
	text_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(text_edit)

	var choice := {"hbox": hbox, "text_edit": text_edit, "actions_btn": null, "actions": actions.duplicate(true), "next": next}

	var actions_btn := Button.new()
	actions_btn.text = "Actions (%d)" % choice["actions"].size()
	actions_btn.pressed.connect(_open_action_popup.bind(choice))
	hbox.add_child(actions_btn)
	choice["actions_btn"] = actions_btn

	var rm := _remove_button()
	rm.pressed.connect(func(): _remove_choice_row(id, choice))
	hbox.add_child(rm)

	n.choices.append(choice)
	gn.add_child(hbox)
	gn.move_child(hbox, n.footer.get_index())
	_refresh_slots(id)


func _remove_choice_row(id: String, choice: Dictionary) -> void:
	var n: Dictionary = _graph_nodes[id]
	if choice["next"] != "":
		_graph_edit.disconnect_node(id, choice["hbox"].get_index(), choice["next"], 0)
	n.choices.erase(choice)
	choice["hbox"].queue_free()
	call_deferred("_refresh_slots", id)


func _delete_graph_node(id: String) -> void:
	if id == "start" or not _graph_nodes.has(id):
		return
	for other_id in _graph_nodes:
		if other_id == id:
			continue
		for c in _graph_nodes[other_id].choices:
			if c["next"] == id:
				c["next"] = ""
				_graph_edit.disconnect_node(other_id, c["hbox"].get_index(), id, 0)
	_graph_nodes[id].gnode.queue_free()
	_graph_nodes.erase(id)


func _on_graph_delete_nodes_request(nodes: Array) -> void:
	for n in nodes:
		_delete_graph_node(str(n))


func _choice_by_port(id: String, port: int) -> Dictionary:
	if not _graph_nodes.has(id):
		return {}
	for c in _graph_nodes[id].choices:
		if c["hbox"].get_index() == port:
			return c
	return {}


func _on_graph_connection_request(from_node: StringName, from_port: int, to_node: StringName, to_port: int) -> void:
	var from_id := str(from_node)
	var to_id := str(to_node)
	var choice := _choice_by_port(from_id, from_port)
	if choice.is_empty():
		return
	if choice["next"] != "":
		_graph_edit.disconnect_node(from_id, from_port, choice["next"], 0)
	choice["next"] = to_id
	_graph_edit.connect_node(from_id, from_port, to_id, 0)


func _on_graph_disconnection_request(from_node: StringName, from_port: int, to_node: StringName, to_port: int) -> void:
	var from_id := str(from_node)
	_graph_edit.disconnect_node(from_id, from_port, str(to_node), to_port)
	var choice := _choice_by_port(from_id, from_port)
	if not choice.is_empty():
		choice["next"] = ""


func _on_add_graph_node() -> void:
	_graph_node_counter += 1
	var id := "node_%d" % _graph_node_counter
	var gn := _create_graph_node(id, "", "...")
	gn.position_offset = _graph_edit.scroll_offset + Vector2(240, 200)


func _save_graph_to_giver() -> void:
	if _graph_giver_id == "" or _graph_state_index < 0:
		return
	var tree := {}
	for id in _graph_nodes:
		var n: Dictionary = _graph_nodes[id]
		var choices := []
		for c in n.choices:
			choices.append({"text": c["text_edit"].text, "next": c["next"], "actions": c["actions"]})
		tree[id] = {"speaker": n.speaker_edit.text, "text": n.text_edit.text, "choices": choices}
	_givers[_graph_giver_id]["dialogue_states"][_graph_state_index]["tree"] = tree
	_save_givers()


# ---------------------------------------------------------------
# Per-choice action-list popup
# ---------------------------------------------------------------

func _build_action_popup() -> PopupPanel:
	var pop := PopupPanel.new()
	pop.title = "Choice Actions"
	pop.size = Vector2(560, 380)
	var style := StyleBoxFlat.new()
	style.bg_color = PAPER_COLOR
	style.set_border_width_all(3)
	style.border_color = PANEL_BORDER
	style.set_content_margin_all(14)
	pop.add_theme_stylebox_override("panel", style)
	pop.theme = _theme

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	pop.add_child(vbox)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)
	_action_rows_box = VBoxContainer.new()
	scroll.add_child(_action_rows_box)

	var add_btn := Button.new()
	add_btn.text = "+ Add Action"
	add_btn.pressed.connect(func(): _add_action_row({"type": "start_quest"}))
	vbox.add_child(add_btn)

	var done_btn := Button.new()
	done_btn.text = "Done"
	done_btn.pressed.connect(_on_action_popup_done)
	vbox.add_child(done_btn)

	return pop


func _open_action_popup(choice: Dictionary) -> void:
	_action_popup_choice = choice
	for c in _action_rows_box.get_children():
		c.queue_free()
	_action_rows.clear()
	for a in choice["actions"]:
		_add_action_row(a)
	_action_popup.popup_centered()


func _add_action_row(a: Dictionary) -> void:
	var row := HBoxContainer.new()
	var type_btn := OptionButton.new()
	for t in ACTION_TYPES:
		type_btn.add_item(t)
	var idx := ACTION_TYPES.find(a.get("type", "start_quest"))
	type_btn.selected = max(idx, 0)
	row.add_child(type_btn)

	var f1 := LineEdit.new()
	f1.custom_minimum_size = Vector2(90, 0)
	var f2 := LineEdit.new()
	f2.custom_minimum_size = Vector2(60, 0)
	var f3 := LineEdit.new()
	f3.custom_minimum_size = Vector2(60, 0)
	var f4 := LineEdit.new()
	f4.custom_minimum_size = Vector2(90, 0)
	row.add_child(f1)
	row.add_child(f2)
	row.add_child(f3)
	row.add_child(f4)

	var rm := _remove_button()
	row.add_child(rm)
	_action_rows_box.add_child(row)

	var entry := {"row": row, "type_btn": type_btn, "f1": f1, "f2": f2, "f3": f3, "f4": f4}
	_action_rows.append(entry)
	type_btn.item_selected.connect(func(_i): _apply_action_field_labels(entry, {}))
	rm.pressed.connect(func():
		_action_rows.erase(entry)
		row.queue_free()
	)
	_apply_action_field_labels(entry, a)


func _apply_action_field_labels(entry: Dictionary, initial_data: Dictionary) -> void:
	var t: String = ACTION_TYPES[entry["type_btn"].selected]
	var specs: Array = ACTION_FIELD_SPECS.get(t, ["", "", "", ""])
	var fields := [entry["f1"], entry["f2"], entry["f3"], entry["f4"]]
	for i in range(4):
		fields[i].visible = specs[i] != ""
		fields[i].placeholder_text = specs[i]
		if not initial_data.is_empty() and specs[i] != "":
			var key: String = specs[i].split(" ")[0]
			fields[i].text = str(initial_data.get(key, ""))


func _on_action_popup_done() -> void:
	var actions := []
	for entry in _action_rows:
		var t: String = ACTION_TYPES[entry["type_btn"].selected]
		var specs: Array = ACTION_FIELD_SPECS.get(t, ["", "", "", ""])
		var a := {"type": t}
		var fields := [entry["f1"], entry["f2"], entry["f3"], entry["f4"]]
		for i in range(4):
			if specs[i] == "":
				continue
			var key: String = specs[i].split(" ")[0]
			var val: String = fields[i].text
			match key:
				"count":
					a[key] = int(val) if val.is_valid_int() else 0
				"radius":
					a[key] = float(val) if val.is_valid_float() else 0.0
				"value":
					a[key] = val.strip_edges().to_lower() == "true"
				_:
					a[key] = val
		actions.append(a)
	_action_popup_choice["actions"] = actions
	_action_popup_choice["actions_btn"].text = "Actions (%d)" % actions.size()
	_action_popup.hide()
	_save_graph_to_giver()
