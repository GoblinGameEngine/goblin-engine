extends CanvasLayer

# Spiral-notebook-styled pause menu: System / Map / Inventory / Quests.
# Built entirely in code (see Hud.gd/DialogBox.gd for the same approach) so
# the layout is easy to read and change in one place.

const HAND_FONT := preload("res://fonts/PatrickHand-Regular.ttf")
const OVERMAP_TEX := preload("res://textures/overmap_static.png")

const PAPER_COLOR := Color(0.94, 0.90, 0.78)
const INK_COLOR := Color(0.16, 0.13, 0.11)
const RULE_COLOR := Color(0.55, 0.62, 0.80, 0.4)
const MARGIN_LINE_COLOR := Color(0.82, 0.30, 0.28, 0.55)

var _is_open := false
var _theme: Theme

var _menu_root: Control
var _notebook_bg: Control
var _tab_bar: HBoxContainer
var _pages: Dictionary = {}       # name -> Control
var _current_page := "quests"

# System subpages
var _system_main: Control
var _system_settings: Control
var _system_keymap: Control

var _quest_list: VBoxContainer
var _item_list: VBoxContainer
var _map_overlay: Control

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 10
	_build_theme()
	_build_ui()
	_root_visible(false)
	QuestManager.quest_started.connect(func(_id): _refresh_quests())
	QuestManager.quest_updated.connect(func(_id): _refresh_quests())
	QuestManager.quest_completed.connect(func(_id): _refresh_quests())
	QuestManager.quest_turned_in.connect(func(_id): _refresh_quests())
	QuestManager.tracked_quest_changed.connect(func(_id): _refresh_quests())
	Inventory.changed.connect(_refresh_inventory)
	WeaponManager.loadout_changed.connect(_refresh_inventory)
	WeaponManager.weapon_equipped.connect(func(_id): _refresh_inventory())

func _build_theme() -> void:
	_theme = Theme.new()
	_theme.default_font = HAND_FONT
	_theme.default_font_size = 22
	_theme.set_color("font_color", "Label", INK_COLOR)
	_theme.set_color("font_color", "Button", INK_COLOR)
	_theme.set_color("default_color", "RichTextLabel", INK_COLOR)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_menu"):
		set_open(not _is_open)

func set_open(open: bool) -> void:
	_is_open = open
	_root_visible(open)
	get_tree().paused = open
	if open:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_refresh_quests()
		_refresh_inventory()
		_map_overlay.queue_redraw()
	else:
		var player := get_tree().get_first_node_in_group("player")
		if player and player.has_method("recapture_mouse"):
			player.recapture_mouse()
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _root_visible(v: bool) -> void:
	# `_menu_root` covers the full screen (it's what carries the notebook
	# margins) -- it MUST actually be hidden when closed, not just its
	# children, or its Control still eats every mouse-motion event on the
	# whole screen forever (this is what broke mouse-look after first
	# opening the menu: the pages were hidden but this root never was).
	_menu_root.visible = v
	for p in _pages.values():
		p.visible = v and p == _pages[_current_page]

# ---------------------------------------------------------------
# Layout
# ---------------------------------------------------------------
func _build_ui() -> void:
	var root_margin := MarginContainer.new()
	root_margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	root_margin.add_theme_constant_override("margin_left", 100)
	root_margin.add_theme_constant_override("margin_right", 100)
	root_margin.add_theme_constant_override("margin_top", 50)
	root_margin.add_theme_constant_override("margin_bottom", 50)
	root_margin.theme = _theme
	add_child(root_margin)
	_menu_root = root_margin

	_notebook_bg = Control.new()
	_notebook_bg.draw.connect(_draw_notebook)
	root_margin.add_child(_notebook_bg)

	var content_margin := MarginContainer.new()
	content_margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	content_margin.add_theme_constant_override("margin_left", 70)
	content_margin.add_theme_constant_override("margin_right", 40)
	content_margin.add_theme_constant_override("margin_top", 20)
	content_margin.add_theme_constant_override("margin_bottom", 30)
	root_margin.add_child(content_margin)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 16)
	content_margin.add_child(vbox)

	_tab_bar = HBoxContainer.new()
	_tab_bar.add_theme_constant_override("separation", 10)
	vbox.add_child(_tab_bar)
	for tab in ["System", "Map", "Inventory", "Quests"]:
		var btn := Button.new()
		btn.text = tab
		btn.add_theme_font_size_override("font_size", 24)
		btn.pressed.connect(_switch_page.bind(tab.to_lower()))
		_tab_bar.add_child(btn)

	var page_holder := Control.new()
	page_holder.set_anchors_preset(Control.PRESET_FULL_RECT)
	page_holder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(page_holder)

	_pages["system"] = _build_system_page()
	_pages["map"] = _build_map_page()
	_pages["inventory"] = _build_inventory_page()
	_pages["quests"] = _build_quests_page()
	for p in _pages.values():
		p.set_anchors_preset(Control.PRESET_FULL_RECT)
		page_holder.add_child(p)

	_switch_page("quests")

func _switch_page(name: String) -> void:
	_current_page = name
	for key in _pages.keys():
		_pages[key].visible = (key == name)

func _draw_notebook() -> void:
	var size: Vector2 = _notebook_bg.size
	if size.x <= 0:
		return
	_notebook_bg.draw_rect(Rect2(Vector2.ZERO, size), PAPER_COLOR, true)
	# ruled lines
	var y := 40.0
	while y < size.y:
		_notebook_bg.draw_line(Vector2(60, y), Vector2(size.x - 10, y), RULE_COLOR, 1.0)
		y += 34.0
	# red margin line
	_notebook_bg.draw_line(Vector2(58, 0), Vector2(58, size.y), MARGIN_LINE_COLOR, 2.0)
	# spiral binding down the left edge
	var sy := 24.0
	while sy < size.y:
		_notebook_bg.draw_circle(Vector2(24, sy), 9.0, Color(0.25, 0.22, 0.20))
		_notebook_bg.draw_circle(Vector2(24, sy), 4.0, PAPER_COLOR)
		sy += 30.0

func _section_title(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", 30)
	return l

# ---------------------------------------------------------------
# System / Settings / Keymap
# ---------------------------------------------------------------
func _build_system_page() -> Control:
	var root := Control.new()

	_system_main = VBoxContainer.new()
	_system_main.set_anchors_preset(Control.PRESET_FULL_RECT)
	_system_main.add_theme_constant_override("separation", 14)
	root.add_child(_system_main)
	_system_main.add_child(_section_title("System"))
	for entry in [["New Game", _on_new_game], ["Resume", func(): set_open(false)],
			["Settings", func(): _show_system_sub(_system_settings)],
			["Keymap", func(): _show_system_sub(_system_keymap)]]:
		var btn := Button.new()
		btn.text = entry[0]
		btn.add_theme_font_size_override("font_size", 26)
		btn.custom_minimum_size = Vector2(240, 44)
		btn.pressed.connect(entry[1])
		_system_main.add_child(btn)

	_system_settings = _build_settings_sub()
	_system_settings.set_anchors_preset(Control.PRESET_FULL_RECT)
	_system_settings.visible = false
	_system_settings.add_child(_back_button(_system_settings))
	root.add_child(_system_settings)

	_system_keymap = _build_keymap_sub()
	_system_keymap.set_anchors_preset(Control.PRESET_FULL_RECT)
	_system_keymap.visible = false
	_system_keymap.add_child(_back_button(_system_keymap))
	root.add_child(_system_keymap)

	return root

func _show_system_sub(sub: Control) -> void:
	_system_main.visible = false
	_system_settings.visible = (sub == _system_settings)
	_system_keymap.visible = (sub == _system_keymap)

func _back_button(sub: Control) -> Button:
	var b := Button.new()
	b.text = "< Back"
	b.pressed.connect(func():
		sub.visible = false
		_system_main.visible = true
	)
	return b

func _build_settings_sub() -> Control:
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 14)
	vbox.add_child(_section_title("Settings"))

	vbox.add_child(_slider_row("SFX Volume", 0.0, 1.0, Settings.sfx_volume, func(v): Settings.set_sfx_volume(v)))
	vbox.add_child(_slider_row("Music Volume", 0.0, 1.0, Settings.music_volume, func(v): Settings.set_music_volume(v)))
	vbox.add_child(_slider_row("Gamma", 0.5, 1.8, Settings.gamma, func(v): Settings.set_gamma(v)))
	vbox.add_child(_slider_row("Mouse Speed", 0.3, 3.0, Settings.mouse_sensitivity_mult, func(v): Settings.set_mouse_sensitivity(v)))
	return vbox

func _slider_row(label_text: String, min_v: float, max_v: float, value: float, on_change: Callable) -> Control:
	var row := VBoxContainer.new()
	var lbl := Label.new()
	lbl.text = label_text
	row.add_child(lbl)
	var slider := HSlider.new()
	slider.min_value = min_v
	slider.max_value = max_v
	slider.step = 0.01
	slider.value = value
	slider.custom_minimum_size = Vector2(320, 24)
	slider.value_changed.connect(on_change)
	row.add_child(slider)
	return row

func _build_keymap_sub() -> Control:
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	vbox.add_child(_section_title("Keymap"))
	var actions := ["move_forward", "move_back", "move_left", "move_right", "jump",
		"shoot", "next_weapon", "prev_weapon", "weapon_slot_1", "weapon_slot_2",
		"weapon_slot_3", "interact", "toggle_menu"]
	var display_names := {
		"move_forward": "Move Forward", "move_back": "Move Back",
		"move_left": "Move Left", "move_right": "Move Right", "jump": "Jump",
		"shoot": "Attack / Fire", "next_weapon": "Next Weapon", "prev_weapon": "Previous Weapon",
		"weapon_slot_1": "Weapon Slot 1", "weapon_slot_2": "Weapon Slot 2", "weapon_slot_3": "Weapon Slot 3",
		"interact": "Talk / Loot / Pick Up / Use", "toggle_menu": "Open Menu",
	}
	for action in actions:
		var row := HBoxContainer.new()
		var name_lbl := Label.new()
		name_lbl.text = display_names.get(action, action)
		name_lbl.custom_minimum_size = Vector2(260, 0)
		row.add_child(name_lbl)
		var key_lbl := Label.new()
		key_lbl.text = _format_binding(action)
		key_lbl.add_theme_color_override("font_color", Color(0.35, 0.3, 0.5))
		row.add_child(key_lbl)
		vbox.add_child(row)
	return vbox

func _format_binding(action: String) -> String:
	var events := InputMap.action_get_events(action)
	if events.is_empty():
		return "(unbound)"
	var e = events[0]
	if e is InputEventKey:
		return OS.get_keycode_string(e.physical_keycode if e.physical_keycode != 0 else e.keycode)
	if e is InputEventMouseButton:
		match e.button_index:
			MOUSE_BUTTON_LEFT: return "Mouse Left"
			MOUSE_BUTTON_RIGHT: return "Mouse Right"
			MOUSE_BUTTON_WHEEL_UP: return "Mouse Wheel Up"
			MOUSE_BUTTON_WHEEL_DOWN: return "Mouse Wheel Down"
			_: return "Mouse Button %d" % e.button_index
	return "?"

func _on_new_game() -> void:
	QuestManager.active.clear()
	QuestManager.completed.clear()
	QuestManager.turned_in.clear()
	QuestManager.tracked_quest_id = ""
	Inventory.stacks.clear()
	WeaponManager.owned.clear()
	WeaponManager.equipped_index = -1
	set_open(false)
	get_tree().reload_current_scene()

# ---------------------------------------------------------------
# Map
# ---------------------------------------------------------------
# Widened west (MIN_X) to fit Summit Lake (built out to Godot x=-115.48,
# see build_neighborhood.py's LAKE_FAR_X) -- keeping the render square
# meant growing the whole frame, not just shifting it, so MIN_Z/MAX_Z
# grew too even though the lake itself doesn't extend that way. When
# Lakeshore's own perimeter later pushed out to the street model's true
# north/south end (build_neighborhood.py's N_LS/S_LS, now 58/-108 in
# Blender terms -> Godot z -58/108), these SAME -90/140 bounds already
# had enough margin to cover it (checked directly: -90<=-58 and
# 140>=108) -- a first attempt at "fixing" this for real recentered
# these anyway, from a sign slip (treating N_LS/S_LS as if they were
# already in Godot terms, when build_neighborhood.py's constants are
# Blender-space and need the z=-y flip like everything else there),
# which pushed the render mostly off both edges' actual content -- caught
# by measuring the rendered PNG's black margin rows directly (top-heavy,
# not the expected roughly-even split) rather than trusting the math
# alone. Left as the original values since they were already correct;
# see render_overmap.py's camera comment for the exact numbers these
# must match.
const MAP_WORLD_MIN_X := -126.0
const MAP_WORLD_MAX_X := 104.0
const MAP_WORLD_MIN_Z := -90.0
const MAP_WORLD_MAX_Z := 140.0

func _world_to_map_uv(x: float, z: float) -> Vector2:
	var u := (x - MAP_WORLD_MIN_X) / (MAP_WORLD_MAX_X - MAP_WORLD_MIN_X)
	var v := 1.0 - (z - MAP_WORLD_MIN_Z) / (MAP_WORLD_MAX_Z - MAP_WORLD_MIN_Z)
	return Vector2(u, v)

func _build_map_page() -> Control:
	var root := Control.new()
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(center)

	var frame := Control.new()
	frame.custom_minimum_size = Vector2(560, 560)
	center.add_child(frame)

	var tex_rect := TextureRect.new()
	tex_rect.texture = OVERMAP_TEX
	tex_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	tex_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	frame.add_child(tex_rect)

	_map_overlay = Control.new()
	_map_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_map_overlay.draw.connect(_draw_map_overlay)
	frame.add_child(_map_overlay)
	return root

func _draw_map_overlay() -> void:
	var size: Vector2 = _map_overlay.size
	if size.x <= 0:
		return
	var player := get_tree().get_first_node_in_group("player") as Node3D
	if player:
		var uv := _world_to_map_uv(player.global_position.x, player.global_position.z)
		_map_overlay.draw_circle(uv * size, 7.0, Color(0.2, 0.6, 1.0))

	var qid := QuestManager.tracked_quest_id
	if qid == "":
		return
	if QuestManager.is_active(qid):
		var group := QuestManager.get_target_group(qid)
		var drew_targets := false
		if group != "":
			for node in get_tree().get_nodes_in_group(group):
				if is_instance_valid(node) and node is Node3D:
					var h = node.get_node_or_null("Health")
					if h == null or h.is_alive():
						var uv2 := _world_to_map_uv(node.global_position.x, node.global_position.z)
						_map_overlay.draw_circle(uv2 * size, 6.0, Color(1.0, 0.25, 0.2))
						drew_targets = true
		if not drew_targets:
			_draw_marker(size, qid)
	elif QuestManager.is_completed(qid) and not QuestManager.is_turned_in(qid):
		_draw_marker(size, qid)

func _draw_marker(size: Vector2, qid: String) -> void:
	var marker: Dictionary = QuestManager.get_map_marker(qid)
	if marker.is_empty():
		return
	var uv := _world_to_map_uv(marker.get("x", 0.0), marker.get("z", 0.0))
	var p := uv * size
	_map_overlay.draw_circle(p, 8.0, Color(0.25, 1.0, 0.35))
	_map_overlay.draw_string(HAND_FONT, p + Vector2(10, 4), marker.get("label", qid), HORIZONTAL_ALIGNMENT_LEFT, -1, 20, INK_COLOR)

# ---------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------
func _build_inventory_page() -> Control:
	var scroll := ScrollContainer.new()
	var vbox := VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_theme_constant_override("separation", 10)
	scroll.add_child(vbox)

	vbox.add_child(_section_title("Weapons"))
	var weapons_box := VBoxContainer.new()
	weapons_box.name = "WeaponsBox"
	vbox.add_child(weapons_box)

	vbox.add_child(HSeparator.new())
	vbox.add_child(_section_title("Items"))
	_item_list = VBoxContainer.new()
	vbox.add_child(_item_list)

	return scroll

func _refresh_inventory() -> void:
	if _pages.is_empty():
		return
	var inv_page: Control = _pages["inventory"]
	var weapons_box: VBoxContainer = inv_page.find_child("WeaponsBox", true, false)
	for c in weapons_box.get_children():
		c.queue_free()
	for weapon_id in WeaponManager.owned:
		var def: Dictionary = WeaponManager.definitions.get(weapon_id, {})
		var row := HBoxContainer.new()
		var lbl := Label.new()
		lbl.text = def.get("name", weapon_id)
		lbl.custom_minimum_size = Vector2(220, 0)
		row.add_child(lbl)
		var btn := Button.new()
		var equipped := WeaponManager.is_equipped(weapon_id)
		btn.text = "Equipped" if equipped else "Equip"
		btn.disabled = equipped
		btn.pressed.connect(WeaponManager.equip.bind(weapon_id))
		row.add_child(btn)
		weapons_box.add_child(row)

	for c in _item_list.get_children():
		c.queue_free()
	var stacks := Inventory.all_stacks()
	if stacks.is_empty():
		var none := Label.new()
		none.text = "Nothing yet."
		_item_list.add_child(none)
	for item_id in stacks.keys():
		var def := Inventory.get_definition(item_id)
		var line := Label.new()
		line.text = "%s x%d" % [def.get("name", item_id), stacks[item_id]]
		_item_list.add_child(line)

# ---------------------------------------------------------------
# Quests
# ---------------------------------------------------------------
func _build_quests_page() -> Control:
	var scroll := ScrollContainer.new()
	_quest_list = VBoxContainer.new()
	_quest_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_quest_list.add_theme_constant_override("separation", 10)
	scroll.add_child(_quest_list)
	return scroll

func _refresh_quests() -> void:
	if _quest_list == null:
		return
	for c in _quest_list.get_children():
		c.queue_free()

	_quest_list.add_child(_section_title("Active"))
	var active_ids := QuestManager.get_active_quests()
	if active_ids.is_empty():
		var none := Label.new()
		none.text = "No active quests."
		_quest_list.add_child(none)
	for quest_id in active_ids:
		_quest_list.add_child(_quest_entry(quest_id, true))

	_quest_list.add_child(HSeparator.new())
	_quest_list.add_child(_section_title("Completed"))
	for quest_id in QuestManager.get_completed_quests():
		var lbl := Label.new()
		lbl.text = "- " + QuestManager.get_quest_title(quest_id)
		_quest_list.add_child(lbl)

func _quest_entry(quest_id: String, show_track: bool) -> Control:
	var box := VBoxContainer.new()
	var header := HBoxContainer.new()
	var title := Label.new()
	title.text = QuestManager.get_quest_title(quest_id)
	title.add_theme_font_size_override("font_size", 24)
	header.add_child(title)
	if show_track:
		var track_btn := Button.new()
		var is_tracked := QuestManager.tracked_quest_id == quest_id
		track_btn.text = "Tracked" if is_tracked else "Track"
		track_btn.disabled = is_tracked
		track_btn.pressed.connect(QuestManager.set_tracked_quest.bind(quest_id))
		header.add_child(track_btn)
	box.add_child(header)

	var desc := Label.new()
	desc.text = QuestManager.get_quest_description(quest_id)
	desc.autowrap_mode = TextServer.AUTOWRAP_WORD
	box.add_child(desc)
	for obj in QuestManager.get_objectives(quest_id):
		var line := Label.new()
		line.text = "  - %s: %d / %d" % [_objective_label(obj), obj.progress, obj.count]
		box.add_child(line)
	box.add_child(HSeparator.new())
	return box

func _objective_label(obj: Dictionary) -> String:
	match obj.type:
		"fetch":
			return "Collect %s" % obj.target
		"kill":
			return "Defeat %s" % obj.target
		"quest":
			return "Complete '%s'" % QuestManager.get_quest_title(obj.target)
		_:
			return String(obj.type)
