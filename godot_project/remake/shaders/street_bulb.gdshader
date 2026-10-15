shader_type spatial;
// Street lamp heads, festoon bulbs, palm lights and the coastal walks' lamps (StreetLights: MultiMeshes).  Each bulb is a
// camera-facing sprite, a hot core and a soft halo, never smaller on screen than px_k m per m of distance -- so a town's
// streets read as strings of light kilometres off.  Lit at night only (fading in at dusk).  The near cells draw their
// bulbs nearer than cut_max, the far (coarser) cells only beyond cut_min, so none is drawn twice.
// INSTANCE COLOR: the bulb's colour; INSTANCE_CUSTOM.x its animation (0 steady, 1 twinkle, 2 chase, 3 slow pulse),
// .y its phase, .z its size (m), .w its brightness (0 = 1).  Adapted from sky_bulbs.gdshader.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float px_k = 0.0026;
uniform float cut_min = 0.0;
uniform float cut_max = 1.0e9;

varying vec4 col;
varying vec4 cus;
varying float dim;

void vertex() {
	col = COLOR;
	cus = INSTANCE_CUSTOM;
	vec3 centre = (MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float d = length(centre);
	float size = cus.z > 0.0 ? cus.z : 0.4;
	float grown = max(size, d * px_k);
	dim = pow(size / grown, 0.55);
	size = grown;
	VERTEX = VERTEX * size;
	// (pulled toward the eye: a bulb sits inside its lamp's head or lantern, which would hide it)
	vec3 c2 = centre + normalize(-centre) * min(0.45, d * 0.5);
	POSITION = PROJECTION_MATRIX * vec4(c2 + vec3(VERTEX.xy, 0.0), 1.0);
	if (d < cut_min || d > cut_max) {
		POSITION = vec4(2.0, 2.0, 2.0, 1.0);           // (outside the clip volume: not drawn)
	}
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night < 0.01) {
		discard;
	}
	float m = cus.x;
	float t = TIME;
	float a = 1.0;
	if (m > 0.5 && m < 1.5) a = 0.55 + 0.45 * sin(t * 2.1 + cus.y * 40.0);
	else if (m > 1.5 && m < 2.5) a = mix(0.25, 1.0, step(mod(floor(cus.y * 50.0) - floor(t / 0.3), 3.0), 0.5));
	else if (m > 2.5) a = 0.7 + 0.3 * sin(t * 0.8 + cus.y * 6.0);
	float d = length(UV - 0.5) * 2.0;
	float core = smoothstep(0.3, 0.0, d);
	float halo = pow(max(1.0 - d, 0.0), 2.0) * 0.8;
	float k = cus.w > 0.0 ? cus.w : 1.0;           // (a festoon's bulbs dimmer than a street lamp's)
	ALBEDO = col.rgb * (core * 4.0 + halo * 1.6) * a * k * night * max(dim, 0.05);
}
