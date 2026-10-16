shader_type spatial;
// Sky-island signs and mood lights (SkySigns): every glowing tube, letter, lightbox face and LED strip of an island in
// one additive mesh.  Additive and depth-draw-never, so the screen outline never inks a tube black, and HDR bright at
// night for the bloom.  Per vertex: COLOR rgb is the light, a its strength; UV2.x the animation, UV2.y its phase;
// UV.x runs 0..1 along the sign (for chases and spell-outs).
//   0 steady   1 flash   2 chase   3 flicker (a failing tube)   4 spell out, then blink   5 breathe   6 colour wheel
//   7 video board (UV.x / UV.y across / up its face)
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float day_k = 0.22;          // how much of it shows by day (an unlit tube's colour)
uniform float night_k = 2.0;         // SIGN_EMIT (2026-10-16): letters 2.0 at night, just over the glow threshold (1.5)
                                      // for a thin halo; lit faces at alpha <= 0.45 stay under it (no wash)

varying vec4 col;
varying vec2 prm;
varying float u;
varying float v;

void vertex() {
	col = COLOR;
	prm = UV2;
	u = UV.x;
	v = UV.y;
}

float h1(float n) {
	return fract(sin(n * 91.3458) * 47453.5453);
}

float anim(float mode, float ph, float x) {
	float t = TIME;
	if (mode < 0.5) return 1.0;
	if (mode < 1.5) return mix(0.08, 1.0, step(0.32, fract(t * 0.6 + ph)));
	if (mode < 2.5) return mix(0.25, 1.0, step(fract(x * 5.0 - t * 0.9 + ph), 0.38));
	if (mode < 3.5) {
		float off = step(0.94, h1(floor(t * 13.0 + ph * 97.0))) + step(0.97, h1(floor(t * 1.7 + ph * 13.0)));
		return 1.0 - clamp(off, 0.0, 1.0) * 0.88;
	}
	if (mode < 4.5) {
		float c = fract(t * 0.18 + ph);
		return c < 0.7 ? step(x, c / 0.62) : mix(0.15, 1.0, step(0.5, fract(t * 2.6)));
	}
	if (mode < 5.5) return 0.55 + 0.45 * sin(t * 1.6 + ph * 6.283);
	return 1.0;
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	float a = anim(prm.x, prm.y, u);
	vec3 c = col.rgb;
	if (prm.x > 5.5) {                        // a slow colour wheel
		float hu = fract(TIME * 0.05 + prm.y + u * 0.3);
		c = clamp(abs(fract(hu + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
	}
	if (prm.x > 6.5) {                        // a video board: blocky frames of colour, 6 a second
		vec2 cell = floor(vec2(u * 16.0, v * 9.0));
		float fr = floor(TIME * 6.0 + prm.y * 50.0);
		float s1 = fract(sin(dot(cell, vec2(12.9898, 78.233)) + fr * 0.37) * 43758.5);
		float s2 = fract(sin(dot(floor(cell / 4.0), vec2(39.3, 11.1)) + floor(fr / 12.0)) * 9123.7);
		vec3 pal = clamp(abs(fract(s2 + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
		c = mix(pal, col.rgb, 0.3) * (0.4 + 0.6 * s1);
		vec2 f = fract(vec2(u * 16.0, v * 9.0)) - 0.5;
		c *= smoothstep(0.5, 0.42, max(abs(f.x), abs(f.y)));     // (the tiles' seams)
	}
	ALBEDO = c * mix(day_k, night_k, night) * col.a * a;
}
