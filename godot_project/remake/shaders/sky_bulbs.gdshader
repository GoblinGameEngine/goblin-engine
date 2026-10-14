shader_type spatial;
// String lights, lanterns and chase bulbs (SkySigns: one MultiMesh an island).  Each bulb is a little camera-facing
// sprite: a hot core and a soft halo, never smaller on screen than MIN_PX-ish (so a festoon 500 m off is still a
// string of sparks -- the Christmas tree).  INSTANCE COLOR is the bulb's colour; INSTANCE_CUSTOM.x its animation
// (0 steady, 1 twinkle, 2 chase, 3 flash), .y its phase, .z its size (m; 0 = 0.35).  Additive: never inked.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float px_k = 0.005;           // m of halo per m of distance at least (~3.5 px at 1080p)

varying vec4 col;
varying vec4 cus;
varying float dim;

void vertex() {
	col = COLOR;
	cus = INSTANCE_CUSTOM;
	vec3 centre = (MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float size = cus.z > 0.0 ? cus.z : 0.35;
	float grown = max(size, -centre.z * px_k);
	dim = pow(size / grown, 0.6);                              // (grown past its size far off: the same light spread wider)
	size = grown;
	VERTEX = VERTEX * size;                                   // (the quad is 1 x 1)
	POSITION = PROJECTION_MATRIX * vec4(centre + vec3(VERTEX.xy, 0.0), 1.0);
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	float m = cus.x;
	float t = TIME;
	float a = 1.0;
	if (m > 0.5 && m < 1.5) a = 0.6 + 0.4 * sin(t * 2.3 + cus.y * 40.0);
	else if (m > 1.5 && m < 2.5) a = mix(0.2, 1.0, step(mod(floor(cus.y * 50.0) - floor(t / 0.22), 3.0), 0.5));
	else if (m > 2.5) a = mix(0.1, 1.0, step(0.4, fract(t * 0.7 + cus.y)));
	float d = length(UV - 0.5) * 2.0;
	float core = smoothstep(0.32, 0.0, d);
	float halo = pow(max(1.0 - d, 0.0), 2.2) * 0.45;
	ALBEDO = col.rgb * (core * 3.2 + halo * 1.3) * a * mix(0.12, 1.6, night) * max(dim, 0.04);
}
