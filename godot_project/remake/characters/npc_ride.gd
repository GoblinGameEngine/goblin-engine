extends RefCounted
class_name NpcRide

## Pose targets for riding in transit (NpcAnimator.ride), in the rider's own frame (-Z forward):
## sitting on a seat (hips on it, feet on the floor ahead, hands on the lap) and standing holding a
## strap (one hand up to it, the other loose). The character's own proportions set them, so a child
## dangles their feet and a tall man's knees come up.
##   animator.ride = NpcRide.seated(npc, seat_height)
##   animator.ride = NpcRide.strap(npc, strap_point_local)


static func _legs(npc: NpcCharacter) -> Vector2:
	var J: Dictionary = npc.built.joints
	var l1 := ((J.LowerLegL as Vector3) - (J.UpperLegL as Vector3)).length()
	var l2 := ((J.FootL as Vector3) - (J.LowerLegL as Vector3)).length()
	return Vector2(l1, l2)


static func seated(npc: NpcCharacter, seat_h: float, slouch := 0.0) -> Dictionary:
	var J: Dictionary = npc.built.joints
	var L := _legs(npc)
	var hips := Vector3(0.0, seat_h + 0.085, 0.04)
	var ank_y := float((J.FootL as Vector3).y)
	var knee_z := hips.z - L.x * 0.95                       # the thighs level, forward from the seat
	var reach := sqrt(maxf(0.0, L.y * L.y - pow(maxf(0.0, (seat_h + 0.02) - ank_y), 2.0)))
	var foot_z := knee_z + 0.05 - minf(reach * 0.25, 0.12)
	var foot_y := maxf(ank_y, seat_h + 0.02 - L.y)          # on the floor, or dangling
	var sep := absf(float((J.UpperLegL as Vector3).x)) * 1.1
	return {"hips": hips, "pitch": -0.05 + slouch, "w": 1.0, "grip": 0.25, "pole": Vector3(0.6, -0.6, -0.2),
		"footL": Vector3(-sep, foot_y, foot_z), "footR": Vector3(sep, foot_y, foot_z),
		"handL": Vector3(-0.13, seat_h + 0.16, knee_z * 0.55), "handR": Vector3(0.13, seat_h + 0.16, knee_z * 0.55)}


## -- movement poses (the player's slide, hang and mantle; any NPC human can use them too:
## research/player/00_plan.md C).  Same contract: targets in the character's own frame, -Z forward.

static func slide(npc: NpcCharacter, w := 1.0) -> Dictionary:
	## A baseball-style power slide: hips low and back, the legs out ahead, the trailing hand down
	## by the hip, the lead arm up for balance, leaning back.
	var J: Dictionary = npc.built.joints
	var L := _legs(npc)
	var reach := (L.x + L.y) * 0.92
	var ank_y := float((J.FootL as Vector3).y)
	var hips := Vector3(0.0, maxf(ank_y + 0.14, reach * 0.30), 0.10)
	var foot_z := -sqrt(maxf(0.01, reach * reach - pow(hips.y - ank_y, 2.0))) + hips.z
	var sep := absf(float((J.UpperLegL as Vector3).x)) * 1.2
	return {"hips": hips, "pitch": -0.38, "w": w, "grip": 0.5, "pole": Vector3(0.7, -0.4, 0.3),
		"footL": Vector3(-sep, ank_y + 0.03, foot_z), "footR": Vector3(sep, ank_y + 0.05, foot_z * 0.92),
		"handR": Vector3(0.30, hips.y + 0.02, hips.z + 0.18),      # trailing on the ground behind
		"handL": Vector3(-0.22, hips.y + 0.42, -0.25)}             # up and forward for balance


static func hang(npc: NpcCharacter, edge_local: Vector3, shimmy := 0.0, w := 1.0) -> Dictionary:
	## Hanging from a ledge edge (edge_local: the grip point between the hands, in the character's
	## frame -- the parkour places the body so this is at arm's reach).  The body hangs straight,
	## the feet tucked a little against the wall; shimmy (-1..1) staggers the hands sideways.
	var J: Dictionary = npc.built.joints
	var sep := absf(float((J.ShoulderL as Vector3).x)) + 0.09
	var ank_y := float((J.FootL as Vector3).y)
	var lsep := absf(float((J.UpperLegL as Vector3).x))
	return {"pitch": 0.10, "w": w, "grip": 1.0, "pole": Vector3(0.55, 0.75, -0.35),
		"handL": edge_local + Vector3(-sep + 0.06 * shimmy, 0.0, 0.0),
		"handR": edge_local + Vector3(sep + 0.06 * shimmy, 0.0, 0.0),
		"footL": Vector3(-lsep, ank_y + 0.16 + 0.03 * shimmy, -0.07),
		"footR": Vector3(lsep, ank_y + 0.13 - 0.03 * shimmy, -0.07)}


static func mantle(npc: NpcCharacter, edge_local: Vector3, k: float, w := 1.0) -> Dictionary:
	## Going up over an edge, k 0..1 along the climb (the parkour drives k and moves the body; this
	## shapes it): hands planted on the edge throughout, the trunk folding then rising, the lead leg
	## coming up onto the top late.
	var J: Dictionary = npc.built.joints
	var L := _legs(npc)
	var sep := absf(float((J.ShoulderL as Vector3).x)) + 0.07
	var ank_y := float((J.FootL as Vector3).y)
	var lsep := absf(float((J.UpperLegL as Vector3).x))
	var fold := sin(PI * clampf(k * 1.25, 0.0, 1.0))              # deepest mid-climb
	var out := {"pitch": 0.45 * fold, "w": w, "grip": 0.9, "pole": Vector3(0.6, 0.2 + 0.5 * fold, -0.4),
		"handL": edge_local + Vector3(-sep, 0.0, 0.0), "handR": edge_local + Vector3(sep, 0.0, 0.0)}
	if k > 0.45:
		# the lead knee comes up beside the hands and takes the weight
		var kk := smoothstep(0.45, 0.85, k)
		out["footR"] = Vector3(lsep + 0.06, lerpf(ank_y + 0.1, edge_local.y - 0.05, kk), lerpf(-0.05, edge_local.z + 0.04, kk))
		out["footL"] = Vector3(-lsep, ank_y + 0.12 * fold, -0.04)
	else:
		out["footL"] = Vector3(-lsep, ank_y + 0.10 * fold, -0.04)
		out["footR"] = Vector3(lsep, ank_y + 0.16 * fold, -0.10)
	return out


static func strap(npc: NpcCharacter, strap_local: Vector3, hand := "R") -> Dictionary:
	## Standing, one hand on a strap (strap_local in the rider's frame; out of reach -> as high as it goes).
	var J: Dictionary = npc.built.joints
	var sh: Vector3 = J["UpperArm" + hand]
	var reach := ((J["Hand" + hand] as Vector3) - sh).length() * 0.97
	var tgt := strap_local
	if (tgt - sh).length() > reach:
		tgt = sh + (tgt - sh).normalized() * reach
	return {"w": 1.0, "grip": 0.9, "pole": Vector3(0.8, -0.3, 0.3), "hand" + hand: tgt}
