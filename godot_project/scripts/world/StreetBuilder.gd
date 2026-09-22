extends Node
class_name StreetBuilder

# Road/footpath/stop-sign primitives shared by every zone generator.
# Follows StationRingBuilder.gd's own technique exactly (SurfaceTool +
# its _quad() winding-safe helper, reused directly rather than
# duplicated) with one addition specific to STREETS: a tangential
# (arc-direction) strip can span many segments, and the floor is a
# flat-chord polygon with a real ~3.75-degree crease at every segment
# boundary -- a single flat quad spanning multiple segments would float
# above the real floor away from whichever point it was calibrated to.
# build_tangential_strip()/build_curved_strip() walk every segment the
# strip crosses and emit one quad per segment, each snapped to
# RingCoords.floor_point()'s real flat-quad geometry.
#
# Axial (width-direction) strips -- cross streets, farm connectors --
# don't have this problem: they run perpendicular to the loop, and a
# cross street's own THICKNESS (its width) is far smaller than one
# segment's arc length in every zone this project uses, so all 4
# corners of an axial quad fall inside a single segment in the ordinary
# case. build_axial_strip() still goes through RingCoords.floor_point()
# per corner rather than assuming that, so it stays correct regardless.

const LIFT := 0.02  # meters, along "up" -- keeps road/sidewalk quads from z-fighting the base floor underneath

## One flat quad per ring-segment crossed, from arc length s_start to
## s_end, axial position LINEARLY interpolated from x_start to x_end
## across that span (equal, for a straight run; different, for a
## straight diagonal leg). `width` is the strip's own width; `uv_tile`
## is the material's tile size in meters (matches TILE_FLOOR/TILE_WALL's
## role in StationRingBuilder.gd).
static func build_tangential_strip(st: SurfaceTool, radius: float, segments: int,
		s_start: float, s_end: float, x_start: float, x_end: float, width: float, uv_tile: float) -> void:
	build_curved_strip(st, radius, segments, s_start, s_end, x_start, x_end, width, uv_tile, 0.0)

## Same as build_tangential_strip(), but `curviness` (0..1) eases the
## x(t) interpolation with smoothstep instead of a straight lerp:
## 0 = ordinary straight/diagonal leg (zero curvature, matches
## build_tangential_strip() exactly), 1 = full smoothstep easing, whose
## derivative is exactly zero at both endpoints -- i.e. the road runs
## parallel to s (locally "straight along the strip") right at each
## waypoint and curves through the middle of the leg. That's what
## "curving, with the only straight sections being at intersections"
## means geometrically: build a road from a chain of these legs
## (build_curved_road() below) and each waypoint -- each intersection --
## is automatically a zero-curvature point where two legs meet tangent
## to each other, with the bend happening mid-leg instead. Intermediate
## `curviness` values (e.g. the lake zone's "less curved" side streets)
## blend between the two.
static func build_curved_strip(st: SurfaceTool, radius: float, segments: int,
		s_start: float, s_end: float, x_start: float, x_end: float, width: float, uv_tile: float,
		curviness: float = 1.0) -> void:
	var hw := width * 0.5
	var seg_arc := (TAU / segments) * radius
	var i0 := int(floor(s_start / seg_arc))
	var i1 := int(ceil(s_end / seg_arc))
	var span := s_end - s_start
	for i in range(i0, i1):
		var seg_s0: float = max(s_start, float(i) * seg_arc)
		var seg_s1: float = min(s_end, float(i + 1) * seg_arc)
		if seg_s1 <= seg_s0:
			continue
		var x0 := _curved_x(x_start, x_end, s_start, span, seg_s0, curviness)
		var x1 := _curved_x(x_start, x_end, s_start, span, seg_s1, curviness)
		var up := RingCoords.floor_basis(radius, segments, (seg_s0 + seg_s1) * 0.5).y
		var offset := up * LIFT
		var p0 := RingCoords.floor_point(radius, segments, seg_s0, x0 - hw) + offset
		var p1 := RingCoords.floor_point(radius, segments, seg_s0, x0 + hw) + offset
		var p2 := RingCoords.floor_point(radius, segments, seg_s1, x1 + hw) + offset
		var p3 := RingCoords.floor_point(radius, segments, seg_s1, x1 - hw) + offset
		var v0 := seg_s0 / uv_tile
		var v1 := seg_s1 / uv_tile
		StationRingBuilder._quad(st, p0, p1, p2, p3, up,
			Vector2((x0 - hw) / uv_tile, v0), Vector2((x0 + hw) / uv_tile, v0),
			Vector2((x1 + hw) / uv_tile, v1), Vector2((x1 - hw) / uv_tile, v1))

static func _curved_x(x_start: float, x_end: float, s_start: float, span: float, s: float, curviness: float) -> float:
	if span <= 0.0:
		return x_start
	var t := (s - s_start) / span
	var eased: float = lerp(t, smoothstep(0.0, 1.0, t), curviness)
	return lerp(x_start, x_end, eased)

## Builds a road (and, if `sidewalk_st`/`sidewalk_width` are given, a
## matching pair of sidewalks alongside it) from a waypoint list
## ([s, x] as Vector2), one leg at a time, via build_curved_strip().
## `curviness` is forwarded to every leg -- see build_curved_strip()'s
## doc for what it means geometrically.
static func build_curved_road(st: SurfaceTool, radius: float, segments: int, waypoints: Array,
		road_width: float, uv_tile: float, curviness: float = 1.0,
		sidewalk_st: SurfaceTool = null, sidewalk_width: float = 0.0, sidewalk_uv_tile: float = 1.0) -> void:
	var road_hw := road_width * 0.5
	var sidewalk_gap := road_hw + sidewalk_width * 0.5
	for i in range(waypoints.size() - 1):
		var a: Vector2 = waypoints[i]
		var b: Vector2 = waypoints[i + 1]
		build_curved_strip(st, radius, segments, a.x, b.x, a.y, b.y, road_width, uv_tile, curviness)
		if sidewalk_st and sidewalk_width > 0.0:
			build_curved_strip(sidewalk_st, radius, segments, a.x, b.x,
				a.y - sidewalk_gap, b.y - sidewalk_gap, sidewalk_width, sidewalk_uv_tile, curviness)
			build_curved_strip(sidewalk_st, radius, segments, a.x, b.x,
				a.y + sidewalk_gap, b.y + sidewalk_gap, sidewalk_width, sidewalk_uv_tile, curviness)

## A single quad running axially (across the width) at a fixed arc
## length s_center, `width_of_street` wide in the arc direction (its own
## thickness), from x_start to x_end.
static func build_axial_strip(st: SurfaceTool, radius: float, segments: int,
		s_center: float, x_start: float, x_end: float, width_of_street: float, uv_tile: float) -> void:
	var hw := width_of_street * 0.5
	var up := RingCoords.floor_basis(radius, segments, s_center).y
	var offset := up * LIFT
	var p0 := RingCoords.floor_point(radius, segments, s_center - hw, x_start) + offset
	var p1 := RingCoords.floor_point(radius, segments, s_center - hw, x_end) + offset
	var p2 := RingCoords.floor_point(radius, segments, s_center + hw, x_end) + offset
	var p3 := RingCoords.floor_point(radius, segments, s_center + hw, x_start) + offset
	var u0 := x_start / uv_tile
	var u1 := x_end / uv_tile
	var v0 := (s_center - hw) / uv_tile
	var v1 := (s_center + hw) / uv_tile
	StationRingBuilder._quad(st, p0, p1, p2, p3, up,
		Vector2(u0, v0), Vector2(u1, v0), Vector2(u1, v1), Vector2(u0, v1))

const STOP_SIGN_TEXTURE := "res://assets/textures/stop_sign_sprite.png"
const STOP_SIGN_POST_HEIGHT := 2.1  # meters, standard-ish sign height
const STOP_SIGN_SIZE := 0.6

## A simple post + sign-face marker at (s, x), offset `x_offset` from
## the intersection center (to the right-hand shoulder of the
## approaching direction, like a real stop sign) and facing back along
## -tangent (toward oncoming traffic on that approach). No dedicated
## StopSign scene exists in this project yet (only the flat sprite
## texture, stop_sign_sprite.png, baked directly into the original
## neighborhood map's mesh rather than kept as a reusable prefab) --
## built fresh here as a thin post (a simple box) + a small billboard
## quad carrying that texture.
static func place_stop_sign(parent: Node3D, radius: float, segments: int, s: float, x: float, facing_yaw: float = 0.0) -> void:
	var sign := Node3D.new()
	sign.name = "StopSign"
	RingCoords.place_on_ring(sign, radius, segments, s, x, facing_yaw)
	# force_readable_name=true -- otherwise every StopSign after the
	# first (a name collision, since every one of these is created with
	# the same literal name) silently gets an opaque auto-generated
	# "@Node3D@N" name instead of "StopSign2", "StopSign3", etc.,
	# confirmed live counting them back out afterward.
	parent.add_child(sign, true)

	var post := MeshInstance3D.new()
	var post_mesh := BoxMesh.new()
	post_mesh.size = Vector3(0.08, STOP_SIGN_POST_HEIGHT, 0.08)
	post.mesh = post_mesh
	post.position = Vector3(0, STOP_SIGN_POST_HEIGHT * 0.5, 0)
	var post_mat := StandardMaterial3D.new()
	post_mat.albedo_color = Color(0.35, 0.35, 0.37)
	post.material_override = post_mat
	sign.add_child(post)

	var face := MeshInstance3D.new()
	var face_mesh := QuadMesh.new()
	face_mesh.size = Vector2(STOP_SIGN_SIZE, STOP_SIGN_SIZE)
	face.mesh = face_mesh
	face.position = Vector3(0, STOP_SIGN_POST_HEIGHT - STOP_SIGN_SIZE * 0.5, 0.05)
	face.rotate_y(PI)  # QuadMesh faces +Z by default; sign should face back along -Z (oncoming approach)
	var face_mat := StandardMaterial3D.new()
	face_mat.albedo_texture = load(STOP_SIGN_TEXTURE)
	face_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	sign.add_child(face)
	face.set_surface_override_material(0, face_mat)
