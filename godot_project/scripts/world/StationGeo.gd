extends RefCounted
class_name StationGeo

## The remake station's geometry: an O'Neill cylinder spun about the x axis -- a true cylinder, no
## facets.  Map coordinates are (s, x): s the arc length round the floor (0..CIRC), x along the axis
## (-HALF_LEN..HALF_LEN, 0 midway between the end caps).  Height h is measured up from the nominal
## floor, toward the axis.  Pure leaf: calls no other class_name script.
##
##   radius 500 m (the floor), length 3,000 m wall to wall, central shaft radius 50 m (the
##   "ceiling", 450 m above the floor); the far side of the floor is 1 km overhead.
##
## Conventions (the same as the earlier RingCoords, so yaws and the player's gravity carry over):
## point(s, x, 0) = (x, R cos th, R sin th) with th = s / R; up points at the axis; forward is +s;
## basis(s) = (right = +x, up, -forward).

const R := 500.0
const LENGTH := 3000.0
const HALF_LEN := 1500.0
const SHAFT_R := 50.0
const CIRC := TAU * R


static func point(s: float, x: float, h: float = 0.0) -> Vector3:
	var th := s / R
	var r := R - h
	return Vector3(x, r * cos(th), r * sin(th))


static func up(s: float) -> Vector3:
	var th := s / R
	return Vector3(0.0, -cos(th), -sin(th))


static func forward(s: float) -> Vector3:
	var th := s / R
	return Vector3(0.0, -sin(th), cos(th))


static func basis(s: float, yaw: float = 0.0) -> Basis:
	## (right = +x, up, back = -forward), turned by yaw about up (a front at local -z then faces
	## (x: -sin yaw, s: cos yaw) on the map).
	var b := Basis(Vector3.RIGHT, up(s), -forward(s))
	return b if yaw == 0.0 else b.rotated(up(s), yaw)


static func s_of(p: Vector3) -> float:
	return fposmod(atan2(p.z, p.y), TAU) * R


static func h_of(p: Vector3) -> float:
	return R - Vector2(p.y, p.z).length()


static func wrap_ds(ds: float) -> float:
	return fposmod(ds + CIRC * 0.5, CIRC) - CIRC * 0.5
