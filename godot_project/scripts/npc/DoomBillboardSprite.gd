extends Sprite3D
class_name DoomBillboardSprite

# Classic Doom-style monster rendering: a handful of hand-drawn 2D frames,
# each covering one 45-degree slice of viewing angle around the actor (5
# unique images per animation frame -- front, front-3/4, side, back-3/4,
# back -- with the other 3 slices reusing those same images horizontally
# flipped, since a walking creature is left/right symmetric). The sprite
# itself billboards to face the camera; separately, every frame this picks
# WHICH of the 5 images to show based on the angle between the camera and
# the way the actor is actually facing, so circling around it reveals the
# correct side.
#
# Deliberately mimics just enough of AnimationPlayer's interface
# (play/stop/is_playing/current_animation/playback_default_blend_time)
# that BedbugEnemy.gd didn't need to change beyond which node it looks up.
#
# Sprites: Freedoom's SARG set (assets/sprites/bedbug_freedoom/), BSD-
# licensed original artwork -- see reference/memory.txt for why this
# replaced both the ripped-Doom-asset request and the real-person-likeness
# request earlier in the project.

const SPRITE_DIR := "res://assets/sprites/bedbug_freedoom/"

# clip name -> ordered list of Doom frame letters. Death holds its last
# frame forever once played through (no loop).
const CLIPS := {
	"Walk": ["a", "b", "c", "d"],
	"Run": ["a", "b", "c", "d"],
	"Attack": ["e", "f", "g"],
	"Death": ["i", "j", "k", "l", "m", "n"],
}
const LOOPING := {"Walk": true, "Run": true, "Attack": true, "Death": false}
const CLIP_FPS := {"Walk": 6.0, "Run": 10.0, "Attack": 8.0, "Death": 6.0}

# rotation slot (1-8, Doom convention) -> (file suffix, needs horizontal flip).
# 1 and 5 (front/back) are drawn symmetric, no flip needed; 2/3/4 mirror
# onto 8/7/6.
const ROTATIONS := {
	1: {"suffix": "1", "flip": false},
	2: {"suffix": "2a8", "flip": false},
	3: {"suffix": "3a7", "flip": false},
	4: {"suffix": "4a6", "flip": false},
	5: {"suffix": "5", "flip": false},
	6: {"suffix": "4a6", "flip": true},
	7: {"suffix": "3a7", "flip": true},
	8: {"suffix": "2a8", "flip": true},
}

@export var pixel_size_world := 0.006  # tunes the sprite's rendered size -- bedbugs are small

var playback_default_blend_time := 0.0  # unused, kept so BedbugEnemy.gd's assignment doesn't error
var current_animation := ""

var _textures: Dictionary = {}      # "<letter><suffix>" -> Texture2D
var _frame_index := 0
var _frame_timer := 0.0
var _playing := false

func _ready() -> void:
	billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST  # keep the pixel-art look crisp, not blurry
	shaded = true  # respects the scene's day/night lighting like the old 3D model did
	pixel_size = pixel_size_world
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF  # a flat cutout's shadow is a hard edge, not worth the cost for a bug-sized creature
	_load_textures()
	_set_frame(CLIPS["Walk"][0], 1)

func _load_textures() -> void:
	var dir := DirAccess.open(SPRITE_DIR)
	if dir == null:
		push_error("DoomBillboardSprite: can't open " + SPRITE_DIR)
		return
	dir.list_dir_begin()
	var fname := dir.get_next()
	while fname != "":
		if fname.ends_with(".png"):
			var key := fname.substr(4, fname.length() - 8)  # strip "sarg" prefix and ".png"
			_textures[key] = load(SPRITE_DIR + fname)
		fname = dir.get_next()
	dir.list_dir_end()

func play(anim_name: String, _custom_blend: float = -1.0, _custom_speed: float = 1.0, _from_end: bool = false) -> void:
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
	if _playing and CLIPS.has(current_animation):
		var letters: Array = CLIPS[current_animation]
		_frame_timer += delta
		var fps: float = CLIP_FPS.get(current_animation, 8.0)
		if _frame_timer >= 1.0 / fps:
			_frame_timer = 0.0
			_frame_index += 1
			if _frame_index >= letters.size():
				if LOOPING.get(current_animation, true):
					_frame_index = 0
				else:
					_frame_index = letters.size() - 1
					_playing = false
	var letter := "a"
	if CLIPS.has(current_animation):
		var letters: Array = CLIPS[current_animation]
		letter = letters[_frame_index]
	_set_frame(letter, _rotation_slot())

func _rotation_slot() -> int:
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
	var signed: float = fwd.signed_angle_to(to_cam, Vector3.UP)
	var deg: float = rad_to_deg(signed)
	var bucket: int = int(round(abs(deg) / 45.0))
	bucket = clampi(bucket, 0, 4)
	# bucket 0 = front (slot 1), 4 = back (slot 5); 1/2/3 pick a side based
	# on which way `deg` leaned, mirrored via ROTATIONS' flip flag for the
	# 6/7/8 slots.
	if bucket == 0:
		return 1
	if bucket == 4:
		return 5
	var slot: int = 1 + bucket  # 2, 3, or 4
	if signed < 0.0:
		slot = 10 - slot  # mirror to 8, 7, or 6
	return slot

func _set_frame(letter: String, slot: int) -> void:
	# Death frames (i0..n0) only exist as single un-rotated images.
	var rot: Dictionary = ROTATIONS.get(slot, ROTATIONS[1])
	var suffix: String = "0" if letter in ["i", "j", "k", "l", "m", "n"] else rot["suffix"]
	var key := letter + suffix
	var tex: Texture2D = _textures.get(key)
	if tex:
		texture = tex
		flip_h = false if suffix == "0" else rot["flip"]
