shader_type spatial;
// The pool of light under a street lamp (StreetLights: merged per cell).  A round falloff laid on the ground (the mesh
// follows the terrain), added to whatever is lit there -- the cheap stand-in for a real light at every lamp (a few real
// OmniLights follow the player for the lamps nearest, to light people, cars and walls).  Night only.
// UV: 0..1 across the pool; COLOR: its colour, alpha its strength.
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, fog_disabled, shadows_disabled;

global uniform float daylight;
uniform float gain = 1.0;          // (StreetLights.POOL_SHADER_GAIN: tuned on Calder's asphalt, 2026-10-16)
uniform float falloff = 1.7;       // the edge: higher = a tighter core, a darker rim

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night < 0.01) {
		discard;
	}
	float d = length(UV - 0.5) * 2.0;
	float f = pow(max(1.0 - d, 0.0), falloff);
	ALBEDO = COLOR.rgb * COLOR.a * f * night * gain;
}
