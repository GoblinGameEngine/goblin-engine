extends "res://scripts/weapons/MeleeWeapon.gd"

# Overrides just the visual: a real batter's swing is a horizontal rotation
# through the shoulders/hips (wind up over the back shoulder, whip level
# through the strike zone, follow through past centerline) rather than a
# vertical chop -- hit detection/damage stays exactly as MeleeWeapon does it.

func _swing_animation() -> void:
	var base_rot := rotation
	var base_pos := position
	var tw := create_tween()

	# Wind up: bat drawn back and up over the shoulder.
	tw.tween_property(self, "rotation:y", base_rot.y + deg_to_rad(75), 0.10)
	tw.parallel().tween_property(self, "rotation:x", base_rot.x - deg_to_rad(15), 0.10)

	# The swing: fast horizontal whip through the strike zone, with a slight
	# forward weight-transfer lunge, dropping to a level follow-through.
	tw.tween_property(self, "rotation:y", base_rot.y - deg_to_rad(95), 0.11)\
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(self, "rotation:x", base_rot.x + deg_to_rad(10), 0.11)
	tw.parallel().tween_property(self, "position", base_pos + Vector3(0, -0.02, 0.05), 0.11)

	# Recover back to the ready stance.
	tw.tween_property(self, "rotation", base_rot, 0.22).set_trans(Tween.TRANS_SINE)
	tw.parallel().tween_property(self, "position", base_pos, 0.22).set_trans(Tween.TRANS_SINE)
