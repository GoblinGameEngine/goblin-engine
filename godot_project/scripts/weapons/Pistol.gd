extends WeaponBase

func _perform() -> void:
	recoil()
	if muzzle_ray == null:
		return
	muzzle_ray.force_raycast_update()
	if muzzle_ray.is_colliding():
		var target := muzzle_ray.get_collider()
		CombatSystem.apply_damage(user, target, float(data.get("damage", 10)))
		WeaponManager.show_hit_marker(muzzle_ray.get_collision_point())
