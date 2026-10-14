shader_type spatial;
// The dot-matrix LED boards (SkySigns; the station's plentiful dot-matrix LCDs): each board's message is a row of
// `msg` (SkyDotFont, one 8-pixel row each), scrolled across the board's dots.  Per vertex: UV in dots (x along the
// board, y down from the top row), UV2 = (message row, message length in dots), COLOR the LEDs' colour.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform sampler2D msg : filter_nearest, repeat_disable;
uniform float speed = 9.0;            // dots a second

varying vec4 col;
varying vec2 prm;

void vertex() {
	col = COLOR;
	prm = UV2;
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	vec2 sz = vec2(textureSize(msg, 0));
	float L = prm.y;
	float x = mod(UV.x + TIME * speed + prm.x * 37.0, L + 12.0);
	float on = 0.0;
	if (x < L && UV.y >= 0.0 && UV.y < 7.0) {
		on = texture(msg, vec2((floor(x) + 0.5) / sz.x, (prm.x * 8.0 + floor(UV.y) + 0.5) / sz.y)).r;
	}
	vec2 f = fract(vec2(x, UV.y)) - 0.5;
	float disc = smoothstep(0.45, 0.28, length(f));
	ALBEDO = col.rgb * disc * mix(0.05, 1.0, on) * mix(0.35, 3.2, night);
}
