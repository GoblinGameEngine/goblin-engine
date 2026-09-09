extends Sprite3D
class_name DirectionalSprite

# Generalized version of the bedbug's Doom-style billboard for sprite
# SHEETS that already draw all 8 viewing angles distinctly (these were
# generated per-direction, unlike Freedoom's hand-optimized 5-unique-plus-
# mirroring economy) -- every frame, picks one of 8 per-column images based
# on the angle between the camera and the actor's own facing direction. A
# "sequential" clip (Death) ignores viewing angle entirely and just plays
# its frame list through once, holding the last frame -- a falling/dying
# pose doesn't need to re-orient to the camera the way a walk cycle does.
#
# Expects assets/sprites/<character>/<character>_<row>_<col>.png, columns
# 1-8 (col 1 = facing the viewer, going clockwise), rows named per the
# clip dictionaries below. Mimics AnimationPlayer's play()/stop()/
# is_playing()/current_animation surface so NPCBase.gd can drive it the
# same way regardless of which character it is.

const SPRITE_ROOT := "res://assets/sprites/"

@export var character := "bedbug"
@export var sprite_height := 0.85  # world-space height of the tallest frame
@export var directional_fps := 6.0
@export var sequential_fps := 8.0

@export var directional_clips: Dictionary = {
	"Idle": ["idle"],
	"Walk": ["walka", "walkb"],
	"Run": ["run"],
	"Attack": ["attacka", "attackb"],
}
@export var sequential_clips: Dictionary = {
	"Death": ["deatha", "deathb"],
}

var playback_default_blend_time := 0.0
var current_animation := ""

var _dir_textures: Dictionary = {}   # "<row>_<col>" -> Texture2D
var _seq_textures: Dictionary = {}   # clip name -> Array[Texture2D]
var _frame_index := 0
var _frame_timer := 0.0
var _playing := false
var _max_px_height := 1.0

func _ready() -> void:
	billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	shaded = true
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_load_textures()
	pixel_size = sprite_height / max(_max_px_height, 1.0)
	play("Idle")

func _load_textures() -> void:
	var dir_path := SPRITE_ROOT + character + "/"
	var dir := DirAccess.open(dir_path)
	if dir == null:
		push_error("DirectionalSprite: can't open " + dir_path)
		return
	dir.list_dir_begin()
	var fname := dir.get_next()
	while fname != "":
		if fname.ends_with(".png"):
			var tex: Texture2D = load(dir_path + fname)
			_max_px_height = max(_max_px_height, float(tex.get_height()))
			var stem: String = fname.trim_suffix(".png").trim_prefix(character + "_")
			_dir_textures[stem] = tex
		fname = dir.get_next()
	dir.list_dir_end()
	for clip_name in sequential_clips.keys():
		var frames: Array = []
		for row in sequential_clips[clip_name]:
			var c := 1
			while _dir_textures.has("%s_%d" % [row, c]):
				frames.append(_dir_textures["%s_%d" % [row, c]])
				c += 1
		_seq_textures[clip_name] = frames

func play(anim_name: String, _a: float = -1.0, _b: float = 1.0, _c: bool = false) -> void:
	if not (directional_clips.has(anim_name) or sequential_clips.has(anim_name)):
		return
	current_animation = anim_name
	_frame_index = 0
	_frame_timer = 0.0
	_playing = true

func stop(_keep_state: bool = false) -> void:
	_playing = false
	current_animation = ""

func is_playing() -> bool:
	return _playing

func _process(delta: float) -> void:
	if current_animation == "":
		return
	if sequential_clips.has(current_animation):
		_process_sequential(delta)
	else:
		_process_directional(delta)

func _process_sequential(delta: float) -> void:
	var frames: Array = _seq_textures.get(current_animation, [])
	if frames.is_empty():
		return
	if _playing:
		_frame_timer += delta
		if _frame_timer >= 1.0 / sequential_fps:
			_frame_timer = 0.0
			_frame_index += 1
			if _frame_index >= frames.size():
				_frame_index = frames.size() - 1
				_playing = false
	texture = frames[_frame_index]
	flip_h = false

func _process_directional(delta: float) -> void:
	var rows: Array = directional_clips.get(current_animation, [])
	if rows.is_empty():
		return
	if _playing and rows.size() > 1:
		_frame_timer += delta
		if _frame_timer >= 1.0 / directional_fps:
			_frame_timer = 0.0
			_frame_index = (_frame_index + 1) % rows.size()
	var row: String = rows[_frame_index % rows.size()]
	var col := _facing_column()
	var tex: Texture2D = _dir_textures.get("%s_%d" % [row, col])
	if tex:
		texture = tex
	flip_h = false

func _facing_column() -> int:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return 1
	var fwd: Vector3 = -global_transform.basis.z
	fwd.y = 0.0
	if fwd.length_squared() < 0.0001:
		return 1
	fwd = fwd.normalized()
	var to_cam: Vector3 = cam.global_position - global_position
	to_cam.y = 0.0
	if to_cam.length_squared() < 0.0001:
		return 1
	to_cam = to_cam.normalized()
	var deg: float = rad_to_deg(fwd.signed_angle_to(to_cam, Vector3.UP))
	if deg < 0.0:
		deg += 360.0
	return (int(round(deg / 45.0)) % 8) + 1
