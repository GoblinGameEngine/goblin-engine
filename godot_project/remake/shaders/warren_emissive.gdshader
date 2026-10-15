shader_type spatial;
// A warren's lamps, lanterns and shop light-strips (SkyWarren's "emissive" slot): their palette colour by day, glowing
// at night (bright enough for the environment's glow to bloom them).
render_mode cull_back;

global uniform float daylight;

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	ALBEDO = COLOR.rgb * 0.6;
	EMISSION = COLOR.rgb * mix(0.15, 3.2, night);
	ROUGHNESS = 0.5;
}
