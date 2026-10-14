shader_type spatial;
// The Spindle, the light of the world (the user, 2026-10-14: "Light will come from the center axial cylinder ...
// emitted all along its shaft ... the spindle itself should be sky blue"; "a sleeve of brighter light travelling the
// light emitting central spindle ... yellow/white"; "the day starts in the South and ends in the North"; at night
// "starlight ... like in the day and a band of moonlight").  Its whole skin glows in the sky's colour (the global
// sky_color DaySkySystem sets: blue by day, red at dawn and dusk, near black at night, starlit); the Sunline's sleeve,
// SLEEVE m long, runs south (+x) to north (-x) over the day, and a pale moon sleeve the same way through the night.
// DaySkySystem sets sun_x / sun_k / moon_x / moon_k and lights the world from the same sleeves.
render_mode unshaded, cull_back, fog_disabled;

global uniform vec4 sky_color;
global uniform float daylight;
uniform float sun_x = 0.0;           // the sleeves' centres along the axis (m)
uniform float sun_k = 0.0;           // ... and how lit (0..1)
uniform float moon_x = 0.0;
uniform float moon_k = 0.0;
uniform float sleeve = 1000.0;       // m long
uniform vec3 sun_tint : source_color = vec3(1.0, 0.92, 0.64);
uniform vec3 moon_tint : source_color = vec3(0.78, 0.84, 1.0);

varying vec3 wpos;

void vertex() {
	wpos = VERTEX;                   // (the shell sits at the origin)
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float band(float x, float c) {
	// 1 over the sleeve, a soft edge either side of it
	float d = abs(x - c) / (sleeve * 0.5);
	return 1.0 - smoothstep(0.9, 1.15, d);
}

void fragment() {
	vec3 sky = sky_color.rgb;
	vec3 col = sky * 1.1;                                       // the skin's own glow
	// starlight at night: points scattered over the skin (40 m cells round and along it)
	float a = atan(wpos.z, wpos.y);
	vec2 g = vec2(wpos.x, a * 2000.0) / 40.0;
	vec2 cell = floor(g);
	vec2 at = vec2(hash(cell), hash(cell + 7.1)) * 0.8 + 0.1;
	float star = step(0.93, hash(cell + 3.3)) * smoothstep(0.12, 0.0, length(fract(g) - at));
	col += vec3(0.85, 0.9, 1.0) * star * (1.0 - daylight) * (0.6 + 0.8 * hash(cell + 1.7));
	// the sleeves, with a glow spilling along the skin
	float ds = (wpos.x - sun_x) / 1600.0;
	col += sun_tint * sun_k * 0.5 * exp(-ds * ds);
	col = mix(col, sun_tint * 1.12 + vec3(0.0, 0.0, 0.08), band(wpos.x, sun_x) * sun_k);   // (kept under white: yellow-white)
	float dm = (wpos.x - moon_x) / 1400.0;
	col += moon_tint * moon_k * 0.12 * exp(-dm * dm);
	col = mix(col, moon_tint * 1.3, band(wpos.x, moon_x) * moon_k);
	ALBEDO = col;
}
