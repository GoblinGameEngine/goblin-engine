extends StaticBody3D
class_name Door

# A door is a flat sprite plane (see gen_door_window_sprites.py, scratchpad
# -- a wood-panel bitmap with a small chroma-keyed transom pane) hinged at
# its own origin (OpeningsSetup.gd places that origin at the actual hinge
# edge of the wall opening, not the opening's center). Opening it is just
# a rotation around local Y from here -- no baked animation needed, and
# since the CollisionShape3D is a child of this same body, the doorway's
# actual walkable collision moves with it (the old, since-removed Openable
# system had a real bug where the collision stayed at the closed footprint
# regardless of the visual door's rotation -- this can't happen here,
# there's only one transform to move).

const OPEN_ANGLE := -deg_to_rad(100.0)
const OPEN_TIME := 0.6

var _open := false
var _base_rot_y := 0.0
var _tween: Tween

func _ready() -> void:
	_base_rot_y = rotation.y

## Player.gd's single-button interact contract: any collider with an
## interact(by) method becomes usable by E. See Player.gd's _try_interact().
func interact(_by: Node) -> void:
	_open = not _open
	var target_y := _base_rot_y + (OPEN_ANGLE if _open else 0.0)
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "rotation:y", target_y, OPEN_TIME).set_trans(Tween.TRANS_SINE)
