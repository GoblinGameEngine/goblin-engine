extends CanvasLayer

# In-game map editor: an asset picker (category tabs + item list) plus a
# crosshair-following "ghost" placement system, built entirely in code
# (same approach as GameMenu.gd/Hud.gd). Terrain and the perimeter wall
# are baked Blender geometry and never touched here -- this only adds
# NEW instances of the existing building/scenery/vehicle/NPC library on
# top of the map, exactly per the request ("place the buildings and
# scenery", not edit what's already there).
#
# Asset source: most categories are standalone glb files exported by
# scratchpad/export_editor_assets.py (houses, trees, bushes, flowers,
# weeds, fences) -- see assets/editor_assets/manifest.json. Vehicles,
# doors/windows, and NPCs already exist as their own Godot scenes and are
# just referenced directly, no export needed.
#
# Controls (only active once F2 has turned editing on):
#   F2      toggle the whole editor on/off
#   Tab     open/close the asset picker (pick a category, then an item)
#   scroll  rotate the current ghost (15-degree steps)
#   click   place the current ghost (stays selected -- click again to
#           place more copies)
#   right-click   clear the current selection (no ghost, still editing)
#   X       aim at a previously-placed custom object and delete it
#
# Persistence: every placement/deletion is written straight to
# data/custom_placements.json (no separate save step), and Main.gd loads
# that file at boot (MapEditorUI.spawn_saved_placements()) right before
# the navigation mesh bakes, so placed objects with real collision
# (houses, fences, etc.) are accounted for by NPC pathfinding too.

const HAND_FONT := preload("res://fonts/PatrickHand-Regular.ttf")
const MANIFEST_PATH := "res://assets/editor_assets/manifest.json"
const PLACEMENTS_PATH := "res://data/custom_placements.json"
const EDITOR_ASSETS_DIR := "res://assets/editor_assets/"

const NPC_SCENES := {
	"Civilian": "res://scenes/npc/NPCBase.tscn",
	"Bedbug": "res://scenes/npc/Bedbug.tscn",
}
const VEHICLE_SCENES := {
	"Car": "res://scenes/VehicleCar.tscn",
	"Pickup": "res://scenes/VehiclePickup.tscn",
	"Minivan": "res://scenes/VehicleMinivan.tscn",
}
const DOOR_WINDOW_SCENES := {
	"Door": "res://scenes/Door.tscn",
	"Interior Door": "res://scenes/InteriorDoor.tscn",
	"Window": "res://scenes/Window.tscn",
}

const PAPER_COLOR := Color(0.94, 0.90, 0.78)
const INK_COLOR := Color(0.16, 0.13, 0.11)
const ROTATE_STEP := deg_to_rad(15.0)
const PLACE_RANGE := 60.0

var active := false  # true whenever F2 editing is on (Player.gd checks this to suppress shooting/weapon-cycling)

var _theme: Theme
var _picker_open := false
var _root_panel: Control
var _category_bar: HBoxContainer
var _item_list: VBoxContainer
var _hint_label: Label
var _toast_label: Label
var _toast_tween: Tween
var _categories: Dictionary = {}   # category name -> Array of {label, scene, extra}
var _current_category := ""

var _waypoint_markers: Array = []   # temporary, edit-mode-only flag meshes (see _spawn_waypoint_markers())

var _house_manifest: Dictionary = {}   # "house_3" -> {stories, wall_h, openings, ...}
var _manifest: Dictionary = {}

var _ghost: Node3D = null
var _ghost_entry: Dictionary = {}
var _ghost_rot := 0.0

var _placements: Array = []   # each: {id, category, item, scene, x,y,z, rot_y, faction (npcs only)}
var _next_placement_id := 1


func _ready() -> void:
	# Same reasoning as GameMenu.gd's own ALWAYS mode: this pauses the
	# tree while the picker is open (so the player doesn't wander off
	# mid-selection), which would otherwise ALSO stop this node's own
	# _unhandled_input/_process from running at all -- meaning nothing
	# (not even F2/Tab to close the picker again, not even the picker's
	# own buttons) would work once paused. ALWAYS keeps it responsive;
	# child Controls (the picker's buttons) inherit this from their
	# ancestor by default (PROCESS_MODE_INHERIT), same as GameMenu's.
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 9
	_load_manifest()
	_build_categories()
	_build_theme()
	_build_ui()
	_hint_label.visible = false
	_load_placements()


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH):
		push_warning("MapEditorUI: missing %s -- Houses/Trees/etc. categories will be empty" % MANIFEST_PATH)
		return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return
	_manifest = data
	for h in data.get("houses", []):
		_house_manifest[h["id"]] = h


func _build_categories() -> void:
	var houses: Array = []
	for id in _house_manifest.keys():
		houses.append({"label": id.capitalize().replace("_", " "), "scene": EDITOR_ASSETS_DIR + id + ".glb", "house_id": id})
	houses.sort_custom(func(a, b): return a["label"] < b["label"])
	_categories["Houses"] = houses

	var trees: Array = []
	for kind in _manifest.get("trees", []):
		trees.append({"label": kind.capitalize().replace("_", " "), "scene": EDITOR_ASSETS_DIR + "tree_" + kind + ".glb"})
	_categories["Trees"] = trees

	var bushes: Array = []
	for kind in _manifest.get("bushes", []):
		bushes.append({"label": kind.capitalize().replace("_", " "), "scene": EDITOR_ASSETS_DIR + "bush_" + kind + ".glb"})
	_categories["Bushes"] = bushes

	var fences: Array = []
	for style in _manifest.get("fences", []):
		fences.append({"label": style.capitalize().replace("_", " "), "scene": EDITOR_ASSETS_DIR + "fence_" + style + ".glb"})
	_categories["Fences"] = fences

	_categories["Flowers"] = [{"label": "Flowers", "scene": EDITOR_ASSETS_DIR + "flowers.glb"}]
	_categories["Weeds"] = [{"label": "Weeds", "scene": EDITOR_ASSETS_DIR + "weeds.glb"}]

	var vehicles: Array = []
	for label in VEHICLE_SCENES:
		vehicles.append({"label": label, "scene": VEHICLE_SCENES[label]})
	_categories["Vehicles"] = vehicles

	var doors_windows: Array = []
	for label in DOOR_WINDOW_SCENES:
		doors_windows.append({"label": label, "scene": DOOR_WINDOW_SCENES[label]})
	_categories["Doors & Windows"] = doors_windows

	var npcs: Array = []
	for label in NPC_SCENES:
		npcs.append({"label": label, "scene": NPC_SCENES[label], "is_npc": true, "faction": ("hostile" if label == "Bedbug" else "civilian")})
	_categories["NPCs"] = npcs

	# Waypoints aren't a spawned scene like everything else -- placing one
	# just records a named point (see Waypoints autoload) for the Quest
	# Editor's (F3) schedule dropdowns to reference. No "scene" key; see
	# _select_ghost()/_confirm_placement()'s is_waypoint branches.
	_categories["Waypoints"] = [{"label": "New Waypoint", "is_waypoint": true}]


func _build_theme() -> void:
	_theme = Theme.new()
	_theme.default_font = HAND_FONT
	_theme.default_font_size = 20
	_theme.set_color("font_color", "Label", INK_COLOR)
	_theme.set_color("font_color", "Button", INK_COLOR)


func _build_ui() -> void:
	_root_panel = Control.new()
	_root_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root_panel.theme = _theme
	_root_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root_panel)

	_hint_label = Label.new()
	_hint_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hint_label.position.y = -34
	_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint_label.add_theme_font_size_override("font_size", 16)
	_hint_label.add_theme_color_override("font_color", Color(1, 1, 1, 0.85))
	_hint_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	_hint_label.add_theme_constant_override("shadow_offset_x", 1)
	_hint_label.add_theme_constant_override("shadow_offset_y", 1)
	_root_panel.add_child(_hint_label)

	_toast_label = Label.new()
	_toast_label.text = "✓ Saved"
	_toast_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_toast_label.position.y = -58
	_toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast_label.add_theme_font_size_override("font_size", 16)
	_toast_label.add_theme_color_override("font_color", Color(0.55, 1.0, 0.55))
	_toast_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	_toast_label.add_theme_constant_override("shadow_offset_x", 1)
	_toast_label.add_theme_constant_override("shadow_offset_y", 1)
	_toast_label.modulate.a = 0.0
	_root_panel.add_child(_toast_label)

	var picker := PanelContainer.new()
	picker.name = "Picker"
	picker.set_anchors_preset(Control.PRESET_CENTER)
	picker.position = Vector2(-320, -260)
	picker.custom_minimum_size = Vector2(640, 480)
	picker.mouse_filter = Control.MOUSE_FILTER_STOP
	var picker_style := StyleBoxFlat.new()
	picker_style.bg_color = PAPER_COLOR
	picker_style.set_corner_radius_all(10)
	picker_style.set_border_width_all(3)
	picker_style.border_color = INK_COLOR
	picker.add_theme_stylebox_override("panel", picker_style)
	picker.visible = false
	_root_panel.add_child(picker)
	_root_panel.set_meta("picker", picker)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", 10)
	picker.add_child(vbox)

	var title := Label.new()
	title.text = "Place an asset"
	title.add_theme_font_size_override("font_size", 26)
	vbox.add_child(title)

	var cat_scroll := ScrollContainer.new()
	cat_scroll.custom_minimum_size = Vector2(0, 40)
	cat_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	cat_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vbox.add_child(cat_scroll)
	_category_bar = HBoxContainer.new()
	cat_scroll.add_child(_category_bar)
	for cat_name in _categories.keys():
		var btn := Button.new()
		btn.text = cat_name
		btn.pressed.connect(_on_category_pressed.bind(cat_name))
		_category_bar.add_child(btn)

	var item_scroll := ScrollContainer.new()
	item_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(item_scroll)
	_item_list = VBoxContainer.new()
	_item_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	item_scroll.add_child(_item_list)

	if not _categories.is_empty():
		_on_category_pressed(_categories.keys()[0])


func _on_category_pressed(cat_name: String) -> void:
	_current_category = cat_name
	for c in _item_list.get_children():
		c.queue_free()
	for entry in _categories.get(cat_name, []):
		var btn := Button.new()
		btn.text = entry["label"]
		btn.pressed.connect(_on_item_pressed.bind(cat_name, entry))
		_item_list.add_child(btn)


func _on_item_pressed(cat_name: String, entry: Dictionary) -> void:
	_select_ghost(cat_name, entry)
	_set_picker_open(false)


# ---------------------------------------------------------------
# Mode toggling
# ---------------------------------------------------------------
func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_editor"):
		_set_editing(not active)
		return
	if not active:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_TAB:
			_set_picker_open(not _picker_open)
		elif event.physical_keycode == KEY_X and not _picker_open:
			_try_delete_aimed()
		elif event.keycode == KEY_S and event.ctrl_pressed:
			# Everything here already saves to disk the instant it happens
			# (see _save_placements()/Waypoints.add()) -- Ctrl+S doesn't
			# need to DO anything extra, it's just an explicit "confirm
			# it's saved" for anyone who doesn't trust that on faith.
			_show_saved_toast()
			get_viewport().set_input_as_handled()
	if _picker_open:
		return
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			_confirm_placement()
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			_clear_ghost()
			get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_ghost_rot += ROTATE_STEP
			_apply_ghost_rotation()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_ghost_rot -= ROTATE_STEP
			_apply_ghost_rotation()


func _set_editing(on: bool) -> void:
	active = on
	if on:
		_spawn_waypoint_markers()
	else:
		_set_picker_open(false)
		_clear_ghost()
		_clear_waypoint_markers()
	_hint_label.visible = on
	_update_hint()


func _set_picker_open(on: bool) -> void:
	_picker_open = on
	var picker: Control = _root_panel.get_meta("picker")
	picker.visible = on
	get_tree().paused = on
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if on else Input.MOUSE_MODE_CAPTURED
	_update_hint()


func _update_hint() -> void:
	if not active:
		return
	if _picker_open:
		_hint_label.text = "Pick a category, then an item"
	elif _ghost:
		_hint_label.text = "Editing: [Tab] menu  [scroll] rotate  [click] place  [right-click] cancel  [X] delete aimed  [F2] exit"
	else:
		_hint_label.text = "Editing: [Tab] to choose something to place  [X] delete aimed  [F2] exit"


# ---------------------------------------------------------------
# Ghost preview + placement
# ---------------------------------------------------------------
const GHOST_MATERIAL_COLOR := Color(0.4, 0.85, 0.5, 0.55)

func _select_ghost(cat_name: String, entry: Dictionary) -> void:
	_clear_ghost()
	if entry.get("is_waypoint", false):
		_ghost = _build_waypoint_marker()
	else:
		var scene: PackedScene = load(entry["scene"])
		if scene == null:
			push_warning("MapEditorUI: could not load %s" % entry["scene"])
			return
		_ghost = scene.instantiate()
	_ghost_entry = entry.duplicate()
	_ghost_entry["category"] = cat_name
	_ghost_rot = 0.0
	_make_ghosty(_ghost)
	get_tree().current_scene.add_child(_ghost)
	_update_hint()


## Waypoints have no model of their own (see data/waypoints.json,
## Waypoints autoload) -- just a name and a position referenced by the
## Quest Editor's schedule dropdowns -- so this builds a small flag-on-a-
## pole marker purely as something to see and aim at while editing.
## Never shown during normal play (see _spawn_waypoint_markers()/
## _clear_waypoint_markers(), called from _set_editing()).
func _build_waypoint_marker() -> Node3D:
	var root := Node3D.new()

	var pole := MeshInstance3D.new()
	var pole_mesh := CylinderMesh.new()
	pole_mesh.top_radius = 0.03
	pole_mesh.bottom_radius = 0.03
	pole_mesh.height = 1.6
	pole.mesh = pole_mesh
	pole.position.y = 0.8
	root.add_child(pole)

	var flag := MeshInstance3D.new()
	var flag_mesh := BoxMesh.new()
	flag_mesh.size = Vector3(0.45, 0.3, 0.02)
	flag.mesh = flag_mesh
	flag.position = Vector3(0.22, 1.35, 0.0)
	root.add_child(flag)

	# Colored now (not ghost-colored) so a CONFIRMED marker still reads as
	# "a flag" rather than plain white -- _make_ghosty() (called right
	# after this, for the preview) replaces these with its own translucent
	# green regardless, since it always overrides an existing surface
	# material rather than only filling in a missing one.
	var pole_mat := StandardMaterial3D.new()
	pole_mat.albedo_color = Color(0.35, 0.25, 0.15)
	pole.set_surface_override_material(0, pole_mat)
	var flag_mat := StandardMaterial3D.new()
	flag_mat.albedo_color = Color(1.0, 0.55, 0.1)
	flag_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	flag.set_surface_override_material(0, flag_mat)

	# A raycast target for aim+X delete (see _delete_by_hit()) -- meshes
	# alone are invisible to PhysicsRayQueryParameters3D. Kept off the
	# player's own collision layer (layer 1) via a dedicated bit so a
	# planted flag never becomes a physical obstacle to walk into; the
	# default aim-ray mask (0xFFFFFFFF, every layer) still finds it.
	var body := StaticBody3D.new()
	body.collision_layer = 1 << 19
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.5, 1.6, 0.5)
	shape.shape = box
	shape.position.y = 0.8
	body.add_child(shape)
	root.add_child(body)

	return root


func _spawn_waypoint_markers() -> void:
	_clear_waypoint_markers()
	var parent := get_tree().current_scene
	if parent == null:
		return
	for id in Waypoints.all_ids():
		var pos = Waypoints.get_position(id)
		if pos == null:
			continue
		var marker := _build_waypoint_marker()
		marker.set_meta("waypoint_id", id)
		parent.add_child(marker)
		marker.global_position = pos
		_waypoint_markers.append(marker)


func _clear_waypoint_markers() -> void:
	for m in _waypoint_markers:
		if is_instance_valid(m):
			m.queue_free()
	_waypoint_markers.clear()


## Strips collision and slaps a translucent green material on every mesh
## in the ghost, recursively -- so it reads clearly as "preview, not
## real" and never blocks the placement raycast or physics.
func _make_ghosty(node: Node) -> void:
	if node is CollisionObject3D:
		(node as CollisionObject3D).collision_layer = 0
		(node as CollisionObject3D).collision_mask = 0
	if node is MeshInstance3D:
		var mi := node as MeshInstance3D
		var mat := StandardMaterial3D.new()
		mat.albedo_color = GHOST_MATERIAL_COLOR
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		for i in mi.get_surface_override_material_count():
			mi.set_surface_override_material(i, mat)
		if mi.get_surface_override_material_count() == 0 and mi.mesh:
			for i in mi.mesh.get_surface_count():
				mi.set_surface_override_material(i, mat)
	if node.has_method("set_process"):
		node.set_process(false)
		node.set_physics_process(false)
	for c in node.get_children():
		_make_ghosty(c)


func _clear_ghost() -> void:
	if _ghost:
		_ghost.queue_free()
		_ghost = null
	_ghost_entry = {}
	_update_hint()


func _apply_ghost_rotation() -> void:
	if _ghost:
		_ghost.rotation.y = _ghost_rot


func _player_camera() -> Camera3D:
	var player := get_tree().get_first_node_in_group("player")
	if player == null:
		return null
	return player.get_node_or_null("Head/Camera3D")


func _aim_point() -> Variant:
	var cam := _player_camera()
	if cam == null:
		return null
	var from := cam.global_position
	var to := from + (-cam.global_transform.basis.z) * PLACE_RANGE
	var space_state := get_viewport().get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(from, to)
	var player := get_tree().get_first_node_in_group("player")
	if player:
		query.exclude = [player.get_rid()]
	return space_state.intersect_ray(query)


## When the aim ray hits nothing (open sky, a gap between buildings, empty
## street at eye height) this is where the ghost/placement lands instead --
## a fixed spot a few meters ahead of the camera, so a miss still puts the
## object somewhere the player can see and adjust, rather than silently
## dropping it at world origin (0,0,0), which could be anywhere on the map
## and was the previous (undiscovered until live-tested) behavior.
const FALLBACK_DISTANCE := 8.0

func _aim_or_fallback() -> Vector3:
	var hit = _aim_point()
	if hit:
		return hit.position
	var cam := _player_camera()
	if cam:
		return cam.global_position + (-cam.global_transform.basis.z) * FALLBACK_DISTANCE
	return Vector3.ZERO


func _process(_delta: float) -> void:
	if not active or _picker_open or _ghost == null:
		return
	_ghost.global_position = _aim_or_fallback()
	_apply_ghost_rotation()


func _confirm_placement() -> void:
	if _ghost == null:
		return
	var pos: Vector3 = _aim_or_fallback()
	if _ghost_entry.get("is_waypoint", false):
		_confirm_waypoint_placement(pos)
		return
	var entry := {
		"id": _next_placement_id,
		"category": _ghost_entry["category"],
		"scene": _ghost_entry["scene"],
		"x": pos.x, "y": pos.y, "z": pos.z, "rot_y": _ghost_rot,
	}
	_next_placement_id += 1
	if _ghost_entry.has("house_id"):
		entry["house_id"] = _ghost_entry["house_id"]
	if _ghost_entry.get("is_npc", false):
		entry["faction"] = _ghost_entry["faction"]
	_placements.append(entry)
	_spawn_entry(entry, _neighborhood_parent())
	_save_placements()


## Waypoints aren't "placements" -- they go straight to the Waypoints
## autoload/data/waypoints.json (already-showing_saved via its own write),
## not custom_placements.json, and a real marker replaces the ghost right
## away so it's visible/deletable for the rest of this editing session.
## Auto-named (waypoint_1, waypoint_2, ...) -- no rename UI yet; the Quest
## Editor's dropdowns show whatever label a waypoint has, id by default.
func _confirm_waypoint_placement(pos: Vector3) -> void:
	var id := Waypoints.next_default_id()
	Waypoints.add(id, pos)
	_show_saved_toast()
	var marker := _build_waypoint_marker()
	marker.set_meta("waypoint_id", id)
	get_tree().current_scene.add_child(marker)
	marker.global_position = pos
	_waypoint_markers.append(marker)


## Deletion is keyed on the "placement_id" meta stamped on every node a
## placement spawns (the house/tree/NPC root AND, for houses, each attached
## Door/Window -- see _spawn_entry/_spawn_house_openings) rather than
## world-position proximity: a house's door can easily sit 2-3m from the
## house's own origin (further than any reasonable fixed radius), so
## position-matching silently deleted just the door/window nearest the aim
## point and left the house itself standing. A shared id set at placement
## time has no such distance limit and can't mismatch two separate objects
## that happen to be close together.
func _try_delete_aimed() -> void:
	var hit = _aim_point()
	if hit:
		_delete_by_hit(hit)


## Split out from _try_delete_aimed so the walk-up/removal logic can be
## exercised by a headless test with a synthetic hit dict (no camera, no
## player, no real raycast needed) -- see scratchpad/test_delete_logic.gd.
func _delete_by_hit(hit: Dictionary) -> bool:
	var col = hit.get("collider")
	var node: Node = col
	while node and not (node.has_meta("placement_id") or node.has_meta("waypoint_id")):
		node = node.get_parent()
	if node == null:
		return false
	if node.has_meta("waypoint_id"):
		var wp_id: String = node.get_meta("waypoint_id")
		Waypoints.remove(wp_id)
		_waypoint_markers.erase(node)
		node.queue_free()
		_show_saved_toast()
		return true
	var id = node.get_meta("placement_id")
	var kept: Array = []
	for entry in _placements:
		if entry.get("id", -1) != id:
			kept.append(entry)
	_placements = kept
	for n in get_tree().get_nodes_in_group("user_placed"):
		if n.has_meta("placement_id") and n.get_meta("placement_id") == id:
			n.queue_free()
	_save_placements()
	return true


func _neighborhood_parent() -> Node3D:
	var main := get_tree().current_scene
	return main.get_node_or_null("NavRegion/Neighborhood") if main else null


# ---------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------
func _load_placements() -> void:
	if not FileAccess.file_exists(PLACEMENTS_PATH):
		return
	var f := FileAccess.open(PLACEMENTS_PATH, FileAccess.READ)
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) == TYPE_ARRAY:
		_placements = data
	# Migrate any entry saved before "id" existed, and seed the counter past
	# whatever ids are already in use so new placements never collide.
	var max_id := 0
	for entry in _placements:
		if entry.has("id"):
			max_id = max(max_id, int(entry["id"]))
	_next_placement_id = max_id + 1
	for entry in _placements:
		if not entry.has("id"):
			entry["id"] = _next_placement_id
			_next_placement_id += 1


func _save_placements() -> void:
	var f := FileAccess.open(PLACEMENTS_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(_placements, "  "))
		f.close()
	else:
		push_warning("MapEditorUI: could not write %s" % PLACEMENTS_PATH)
	_show_saved_toast()


## A brief "✓ Saved" flash after every placement/deletion -- everything
## here already wrote to disk instantly before this ever existed; this is
## purely so that's visible instead of an invisible article of faith.
## Ctrl+S triggers the same flash on demand without changing anything.
func _show_saved_toast() -> void:
	if _toast_tween:
		_toast_tween.kill()
	_toast_label.modulate.a = 1.0
	_toast_tween = create_tween()
	_toast_tween.tween_interval(0.6)
	_toast_tween.tween_property(_toast_label, "modulate:a", 0.0, 0.6)


## Called once by Main.gd during its own _ready(), BEFORE the navigation
## mesh bakes -- so any collision on placed houses/fences/etc. is
## accounted for by NPC pathfinding, same as everything Blender built.
func spawn_saved_placements(parent: Node3D) -> int:
	for entry in _placements:
		_spawn_entry(entry, parent)
	return _placements.size()


func _spawn_entry(entry: Dictionary, parent: Node3D) -> void:
	if parent == null:
		return
	var scene: PackedScene = load(entry["scene"])
	if scene == null:
		push_warning("MapEditorUI: could not load %s, skipping a saved placement" % entry["scene"])
		return
	var inst = scene.instantiate()
	parent.add_child(inst)
	if inst is Node3D:
		inst.global_position = Vector3(entry["x"], entry["y"], entry["z"])
		inst.rotation.y = entry.get("rot_y", 0.0)
	inst.add_to_group("user_placed")
	inst.set_meta("placement_id", entry.get("id", -1))
	if entry.has("faction") and ("faction_id" in inst):
		inst.faction_id = entry["faction"]
	if entry.has("house_id"):
		_spawn_house_openings(entry, parent)


## Placed houses need their own door/window sprites attached separately
## (see Door.tscn/Window.tscn, scripts/world/OpeningsSetup.gd for the
## main map's version of this) -- the manifest's per-house "openings"
## list is in that house's OWN local space (it was built and recorded at
## the origin with no rotation, see export_editor_assets.py), so unlike
## the main map (whose exported openings are already-rotated WORLD
## coordinates, computed once at map-build time for houses that never
## move again), this has to compose the rotation itself here, since the
## SAME house asset gets placed at whatever angle the user rotated it to.
func _spawn_house_openings(entry: Dictionary, parent: Node3D) -> void:
	var meta: Dictionary = _house_manifest.get(entry.get("house_id", ""), {})
	var openings: Array = meta.get("openings", [])
	if openings.is_empty():
		return
	var theta: float = entry.get("rot_y", 0.0)
	var base := Vector3(entry["x"], entry["y"], entry["z"])
	var id = entry.get("id", -1)
	var door_scene: PackedScene = load(DOOR_WINDOW_SCENES["Door"])
	var interior_door_scene: PackedScene = load(DOOR_WINDOW_SCENES["Interior Door"])
	var window_scene: PackedScene = load(DOOR_WINDOW_SCENES["Window"])
	for o in openings:
		var is_door: bool = o["kind"] == "door" or o["kind"] == "door_int"
		var lx: float = o["hinge_x"] if is_door else o["x"]
		var ly: float = o["hinge_y"] if is_door else o["y"]
		var dx := lx * cos(theta) - ly * sin(theta)
		var dz := -lx * sin(theta) - ly * cos(theta)
		var plane_rot: float = theta + o["plane_rot"]
		if is_door:
			var inst: Door = (interior_door_scene if o["kind"] == "door_int" else door_scene).instantiate()
			parent.add_child(inst)
			inst.global_position = base + Vector3(dx, o["z"], dz)
			inst.rotation.y = plane_rot
			inst.add_to_group("user_placed")
			inst.set_meta("placement_id", id)
		else:
			var inst2: Node3D = window_scene.instantiate()
			parent.add_child(inst2)
			var height: float = o["height"]
			inst2.global_position = base + Vector3(dx, o["z"] + height / 2.0, dz)
			inst2.rotation.y = plane_rot
			inst2.scale = Vector3(o["width"], height, 1.0)
			inst2.add_to_group("user_placed")
			inst2.set_meta("placement_id", id)
