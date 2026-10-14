shader_type spatial;
// A sky island far off at night (SkyIsland: the overlay of its mid and far LODs): its walls a grid of lit windows in
// warm and neon colours, its roofs dotted with signs, its rim a necklace of bulbs -- sub-pixel from across the ring, so it
// glitters like a lit Christmas tree.  Local frame: y 0 the deck's edge, buildings above, the rock below.
render_mode unshaded, blend_add, depth_draw_never, cull_back, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float seed = 0.0;
uniform vec3 mood : source_color = vec3(1.0, 0.6, 0.3);

varying vec3 lp;
varying vec3 ln;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453);
}

vec3 tint(float k) {
	if (k < 0.55) return vec3(1.0, 0.72, 0.38);          // lamp-lit rooms
	if (k < 0.7) return mood;
	if (k < 0.8) return vec3(1.0, 0.25, 0.55);
	if (k < 0.9) return vec3(0.25, 0.9, 1.0);
	return vec3(0.6, 1.0, 0.4);
}

void vertex() {
	lp = VERTEX;
	ln = NORMAL;
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night < 0.01) {
		discard;
	}
	vec3 c = vec3(0.0);
	if (abs(ln.y) < 0.5 && lp.y > 1.0) {
		vec2 t = normalize(vec2(-ln.z, ln.x));
		float s = dot(lp.xz, t);
		vec2 g = vec2(s / 2.8, (lp.y - 1.0) / 3.0);
		vec2 cell = floor(g) + floor(dot(lp.xz, ln.xz)) * 7.31;
		float r = hash(cell);
		vec2 f = fract(g);
		float pane = step(0.18, f.x) * step(f.x, 0.82) * step(0.28, f.y) * step(f.y, 0.78);
		c = tint(hash(cell + 3.7)) * step(r, 0.62) * pane * 1.6;
		// a few big signs blinking on the walls
		vec2 big = floor(g / vec2(3.0, 2.0));
		float hb = hash(big + 11.0);
		if (hb > 0.9) {
			c += tint(hash(big)) * step(0.3, fract(TIME * 0.5 + hb * 9.0)) * 2.5;
		}
	} else if (ln.y > 0.6 && lp.y > 3.0) {
		vec2 cell = floor(lp.xz / 3.5);
		float r = hash(cell + 5.0);
		vec2 f = fract(lp.xz / 3.5) - 0.5;
		c = tint(hash(cell)) * step(0.9, r) * step(length(f), 0.18) * (0.6 + 0.4 * sin(TIME * 2.0 + r * 30.0)) * 3.0;
	} else if (lp.y < 0.6 && lp.y > -2.5 && abs(ln.y) < 0.8) {
		// the rim's bulbs, every ~2.5 m
		float a = atan(lp.z, lp.x) * length(lp.xz) / 2.5;
		vec2 f = vec2(fract(a) - 0.5, (lp.y + 1.0) / 1.2);
		c = vec3(1.0, 0.82, 0.5) * step(length(f), 0.22) * 2.0;
	}
	ALBEDO = c * night * 1.4;
}
