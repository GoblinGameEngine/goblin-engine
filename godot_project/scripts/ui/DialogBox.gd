extends CanvasLayer

# Minimal branching dialog runner. Tree format:
#   { "start": { "speaker": "Name", "text": "...",
#                "choices": [ { "text": "...", "next": "node_id_or_null",
#                               "actions": [ {"type": "...", ...}, ... ] } ] } }
# "actions" (a list of generic action dicts -- see
# QuestGiverGeneric._execute_action() for the vocabulary) is just forwarded
# on the `dialog_action` signal so quest-giving NPCs can hook it up without
# this script needing to know about quests or items specifically. The
# older single-string "action" field (no list, no structure) still works
# too, forwarded as-is, for scripts written before the generic action
# system existed (scripts/npc/QuestGiver.gd).

signal dialog_started(npc: Node)
signal dialog_ended(npc: Node)
signal dialog_action(action: String, npc: Node)

const BLUR_SHADER := preload("res://shaders/ui_blur.gdshader")

var _root: Control
var _speaker_label: Label
var _text_label: RichTextLabel
var _choice_box: VBoxContainer

var _tree: Dictionary = {}
var _npc: Node = null
var _was_captured := false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 15
	_build_ui()
	_root.visible = false

func _build_ui() -> void:
	# Bottom half of the screen, dark/translucent/blurred backdrop, white
	# handwritten-adjacent text -- distinct from the notebook menu.
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_root.anchor_top = 0.5
	_root.offset_top = 0
	add_child(_root)

	var blur := ColorRect.new()
	blur.set_anchors_preset(Control.PRESET_FULL_RECT)
	var mat := ShaderMaterial.new()
	mat.shader = BLUR_SHADER
	blur.material = mat
	_root.add_child(blur)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 180)
	margin.add_theme_constant_override("margin_right", 180)
	margin.add_theme_constant_override("margin_top", 40)
	margin.add_theme_constant_override("margin_bottom", 50)
	_root.add_child(margin)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 14)
	margin.add_child(vbox)

	_speaker_label = Label.new()
	_speaker_label.add_theme_font_size_override("font_size", 24)
	_speaker_label.add_theme_color_override("font_color", Color(1, 1, 1))
	_speaker_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.6))
	_speaker_label.add_theme_constant_override("outline_size", 4)
	vbox.add_child(_speaker_label)

	_text_label = RichTextLabel.new()
	_text_label.fit_content = true
	_text_label.scroll_active = false
	_text_label.custom_minimum_size = Vector2(0, 80)
	_text_label.add_theme_font_size_override("normal_font_size", 22)
	_text_label.add_theme_color_override("default_color", Color(1, 1, 1))
	vbox.add_child(_text_label)

	_choice_box = VBoxContainer.new()
	_choice_box.add_theme_constant_override("separation", 6)
	vbox.add_child(_choice_box)

func is_open() -> bool:
	return _root.visible

func start(npc: Node, tree: Dictionary, start_node: String = "start") -> void:
	_npc = npc
	_tree = tree
	_was_captured = Input.mouse_mode == Input.MOUSE_MODE_CAPTURED
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_root.visible = true
	if npc and npc.has_method("begin_dialog"):
		npc.begin_dialog()
	dialog_started.emit(npc)
	_show_node(start_node)

func _show_node(node_id: String) -> void:
	if node_id == "" or not _tree.has(node_id):
		_end()
		return
	var node: Dictionary = _tree[node_id]
	_speaker_label.text = node.get("speaker", "")
	_text_label.text = node.get("text", "")
	for c in _choice_box.get_children():
		c.queue_free()
	var choices: Array = node.get("choices", [])
	if choices.is_empty():
		var ok := Button.new()
		ok.text = "[End]"
		_style_choice_button(ok)
		ok.pressed.connect(_end)
		_choice_box.add_child(ok)
		return
	for choice in choices:
		var btn := Button.new()
		btn.text = choice.get("text", "...")
		_style_choice_button(btn)
		btn.pressed.connect(_on_choice.bind(choice))
		_choice_box.add_child(btn)

func _style_choice_button(btn: Button) -> void:
	btn.add_theme_color_override("font_color", Color(1, 1, 1))
	btn.add_theme_color_override("font_hover_color", Color(1.0, 0.85, 0.3))
	btn.add_theme_color_override("font_pressed_color", Color(1.0, 0.85, 0.3))
	btn.add_theme_font_size_override("font_size", 20)
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	var flat := StyleBoxFlat.new()
	flat.bg_color = Color(1, 1, 1, 0.08)
	flat.set_content_margin_all(10)
	flat.set_corner_radius_all(4)
	btn.add_theme_stylebox_override("normal", flat)
	var hover := flat.duplicate()
	hover.bg_color = Color(1, 1, 1, 0.18)
	btn.add_theme_stylebox_override("hover", hover)

func _on_choice(choice: Dictionary) -> void:
	if choice.has("actions") and choice.actions is Array and not choice.actions.is_empty():
		dialog_action.emit(choice.actions, _npc)
	elif choice.has("action") and choice.action != null and choice.action != "":
		dialog_action.emit(choice.action, _npc)
	_show_node(choice.get("next", ""))

func _end() -> void:
	_root.visible = false
	if _npc and is_instance_valid(_npc) and _npc.has_method("end_dialog"):
		_npc.end_dialog()
	if _was_captured:
		var player := get_tree().get_first_node_in_group("player")
		if player and player.has_method("recapture_mouse"):
			player.recapture_mouse()
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	else:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	dialog_ended.emit(_npc)
	_npc = null
