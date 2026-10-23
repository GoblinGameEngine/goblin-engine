extends RefCounted
class_name NpcWeaponPose

## How a person holds and uses a weapon: the weapon's own transform and both hands on it, keyed in
## the AIM frame (origin at the eyes, -Z where they look, +Y up; metres).  The player passes its
## camera, an NPC its head; the hands then reach the weapon by arm IK with their facing set
## (NpcAnimator.ride handL/handR + aimL/aimR), so the weapon is the master and the hands follow it.
##
## Reference (research/player/04_weapon_holds.md; frame sheets kept locally in reference/video_refs/weapons):
##   fists  -- a boxer's guard, both fists up low in view, knuckles forward; jab and cross
##             alternate, out fast (0.08 s) with the fist turning three-quarters over, home slower
##   bat    -- two hands low on the right, the bat up over the right shoulder; the swing cocks
##             back, whips flat across from right to left, holds the follow-through, recovers
##   pistol -- two-handed, low and right of centre, the barrel on the crosshair; a sharp kick up
##             and back on each shot and a slower settle
##
## The weapon models are built for this (scenes/weapons): the origin is the grip -- the pistol's
## grip with the barrel along -Z, the bat's handle between the hands with the bat along +Y.

const LEN := {"fists": 0.5, "bat": 0.8, "pistol": 0.26}

## The bat: [t, position, bat axis (toward the tip), hitting face]
const BAT_KEYS := [
	[0.00, Vector3(0.17, -0.25, -0.36), Vector3(0.35, 0.85, 0.35), Vector3(0, 0, -1)],
	[0.17, Vector3(0.25, -0.21, -0.17), Vector3(0.60, 0.50, 0.62), Vector3(0.3, 0, -1)],     # cocked back
	[0.21, Vector3(0.22, -0.21, -0.36), Vector3(0.55, 0.12, -0.83), Vector3(-0.8, 0, -0.5)], # coming through on the right
	[0.25, Vector3(0.04, -0.24, -0.45), Vector3(-0.40, 0.02, -0.92), Vector3(-1, 0, 0.3)],   # contact
	[0.32, Vector3(-0.20, -0.27, -0.33), Vector3(-1.0, 0.0, 0.10), Vector3(0.1, 0, 1)],      # whipping through
	[0.44, Vector3(-0.23, -0.22, -0.22), Vector3(-0.70, 0.30, 0.65), Vector3(0.6, 0, 0.8)],  # follow-through held
	[0.80, Vector3(0.17, -0.25, -0.36), Vector3(0.35, 0.85, 0.35), Vector3(0, 0, -1)],
]


static func pose(id: String, t: float, side: int, aim_to_skel: Transform3D, sway := Vector3.ZERO) -> Dictionary:
	## id: fists | bat | pistol; t: time into the attack (< 0: just holding); side: which fist
	## punches (+1 right, -1 left).  -> {"ride": NpcAnimator.ride entries (skeleton space),
	## "weapon": the weapon's transform in the aim frame}
	var hands := {}
	var weapon := Transform3D.IDENTITY
	match id:
		"pistol":
			weapon = _pistol(t)
			weapon.origin += sway
			hands = {
				"R": [weapon * Vector3(0.032, -0.012, 0.072), weapon.basis * Vector3(0, -0.12, -1), weapon.basis * Vector3(-1, 0, 0)],
				"L": [weapon * Vector3(-0.05, -0.03, 0.05), weapon.basis * Vector3(0.45, -0.35, -0.8), weapon.basis * Vector3(1, 0.1, 0.35)],
			}
		"bat":
			weapon = _bat(t)
			weapon.origin += sway
			var f := weapon.basis * Vector3(-0.7, 0, -0.7)          # the fingers wrap round the handle
			var p := (weapon.basis * Vector3(0.7, 0, -0.7)).normalized()
			hands = {
				"R": [weapon * Vector3(0, 0.045, 0) - f * 0.07 - p * 0.03, f, p],       # top hand, palm to the pitcher
				"L": [weapon * Vector3(0, -0.055, 0) - f * 0.07 + p * 0.03, f, -p],     # bottom hand
			}
		_:
			hands = _fists(t, side, sway)
	var ride := {"w": 1.0, "grip": {"pistol": 0.8, "bat": 0.92}.get(id, 1.0)}
	var poles := {"pistol": Vector3(0.75, -0.65, 0.1), "bat": Vector3(0.6, -0.8, 0.15)}
	for s in ["L", "R"]:
		var h: Array = hands[s]
		ride["hand" + s] = aim_to_skel * (h[0] as Vector3)
		ride["aim" + s] = [aim_to_skel.basis * (h[1] as Vector3), aim_to_skel.basis * (h[2] as Vector3)]
		ride["pole" + s] = poles.get(id, Vector3(0.45, -0.9, 0.1))
	return {"ride": ride, "weapon": weapon}


static func _ease(a: float, b: float, t: float) -> float:
	return smoothstep(0.0, 1.0, clampf((t - a) / maxf(b - a, 1e-4), 0.0, 1.0))


static func _pistol(t: float) -> Transform3D:
	# right of centre and a little low, so the slide shows its side; the barrel converges on the
	# crosshair 40 m out
	var at := Vector3(0.15, -0.165, -0.42)
	var b := Basis.looking_at((Vector3(0, 0, -40) - at).normalized(), Vector3.UP)
	var kick := 0.0
	if t >= 0.0:
		kick = _ease(0.0, 0.035, t) * (1.0 - _ease(0.035, LEN.pistol, t))
	b = b * Basis(Vector3.RIGHT, deg_to_rad(14.0) * kick)
	return Transform3D(b, at + Vector3(0, 0.015, 0.045) * kick)


static func _bat_key(k: Array) -> Transform3D:
	var y := (k[2] as Vector3).normalized()
	var z := -((k[3] as Vector3) - y * (k[3] as Vector3).dot(y)).normalized()
	return Transform3D(Basis(y.cross(z), y, z), k[1])


static func _bat(t: float) -> Transform3D:
	if t < 0.0:
		return _bat_key(BAT_KEYS[0])
	for i in range(1, BAT_KEYS.size()):
		var k1: Array = BAT_KEYS[i]
		if t <= float(k1[0]) or i == BAT_KEYS.size() - 1:
			var k0: Array = BAT_KEYS[i - 1]
			var u := clampf((t - float(k0[0])) / (float(k1[0]) - float(k0[0])), 0.0, 1.0)
			# the strike segments run at speed (no ease), the wind-up and recovery ease
			if i == 1 or i == BAT_KEYS.size() - 1:
				u = smoothstep(0.0, 1.0, u)
			elif i == 5:
				u = 1.0 - pow(1.0 - u, 2.0)
			var a := _bat_key(k0)
			var b := _bat_key(k1)
			return Transform3D(Basis(a.basis.get_rotation_quaternion().slerp(b.basis.get_rotation_quaternion(), u)),
				a.origin.lerp(b.origin, u))
	return _bat_key(BAT_KEYS[0])


static func _fists(t: float, side: int, sway: Vector3) -> Dictionary:
	var out := {}
	for s in ["L", "R"]:
		var k := -1.0 if s == "L" else 1.0
		# the guard: low in view, knuckles forward and up, palms in
		var pos := Vector3(0.13 * k, -0.235, -0.27) + sway
		var fing := Vector3(-0.1 * k, 0.45, -0.9)
		var palm := Vector3(-0.8 * k, -0.2, 0.2)
		if t >= 0.0 and ((side > 0) == (s == "R")):
			# out fast to full reach on the centre line, the fist turning three-quarters over; home slower
			var e := _ease(0.0, 0.08, t) * (1.0 - _ease(0.13, 0.42, t))
			pos = pos.lerp(Vector3(0.04 * k, -0.14, -0.50), e)
			fing = fing.lerp(Vector3(-0.05 * k, 0.1, -1), e)
			palm = palm.lerp(Vector3(-0.55 * k, -0.85, 0), e)
		elif t >= 0.0:
			# the other fist tucks in to guard the chin
			var e2 := _ease(0.0, 0.08, t) * (1.0 - _ease(0.2, 0.45, t))
			pos = pos.lerp(Vector3(0.09 * k, -0.17, -0.22), e2)
		out[s] = [pos, fing, palm]
	return out
