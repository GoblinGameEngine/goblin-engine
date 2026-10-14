shader_type spatial;
// Light thrown on a wall (SkySigns): uplights, spotlights on painted boards, a lightbox's spill.  Additive, night only.
// UV.y 0 at the lamp, 1 at the far end; UV.x 0..1 across; COLOR its colour (a: strength).
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night < 0.01) {
		discard;
	}
	float along = pow(1.0 - UV.y, 1.8);
	float across = pow(sin(3.14159 * UV.x), 1.5);
	ALBEDO = COLOR.rgb * COLOR.a * along * across * 0.9 * night;
}
