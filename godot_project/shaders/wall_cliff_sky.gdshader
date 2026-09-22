shader_type spatial;
// Wall: cliff rock (bottom cliff_frac of floor-to-ceiling height) blending
// into the same day/night sky as the ceiling (shaders/ceiling_sky.gdshader,
// scripts/world/DaySkySystem.gd drives both together) above it -- "the
// top of the cliff should look rugged and jagged like a mountain."
// A perfectly flat wall quad has one constant normal, so there's no real
// geometric edge to make jagged -- the boundary is instead a noise-
// perturbed blend THRESHOLD in the fragment shader (cheap value noise
// keyed on the wall's tangential angle, so it varies smoothly all the
// way around the ring and wraps seamlessly at the loop).
//
// The sky portion samples sky_day_texture/sky_night_texture at the SAME
// world-position-derived, whole-cylinder UV the ceiling uses (station_
// width for U, wrap angle for V) -- NOT tiled, matching the ceiling
// exactly rather than a separately-scaled crop, so the two surfaces read
// as one continuous sky instead of two different-looking ones.
//
// The cliff portion is toon cel-shaded like the rest of this project's
// world geometry (render_mode cull_disabled, banded light()); the sky
// portion is unshaded/self-lit via EMISSION instead (matching the
// ceiling's own unshaded treatment -- it should read the same
// regardless of scene lighting, same as a real sky) with ALBEDO zeroed
// there so light()'s banding doesn't also darken it.
render_mode cull_disabled;

uniform sampler2D cliff_texture : source_color, filter_nearest, repeat_enable;
// filter_linear_mipmap_anisotropic -- see ceiling_sky.gdshader's own
// comment on why (vanishing-point minification blur, standard fix).
uniform sampler2D sky_day_texture : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D sky_night_texture : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float wall_v_max = 25.0;       // UV.y at the ceiling -- CEILING_HEIGHT/TILE_WALL, set from GDScript
uniform float cliff_frac : hint_range(0.0, 1.0) = 0.6;
uniform float jag_amplitude : hint_range(0.0, 0.3) = 0.07;  // +/- fraction of height the boundary jags by
uniform float night_mix : hint_range(0.0, 1.0) = 0.0;
uniform vec4 day_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float loop_duration = 22.0;      // matches ceiling_sky.gdshader -- same animation, same period
uniform float drift_amplitude = 0.0018;
uniform float station_width = 1000.0;    // SpaceStation.WIDTH -- matches ceiling_sky.gdshader's own mapping exactly

varying float wall_angle;
varying float world_x;

void vertex() {
	// atan2(z, y), not a raw coordinate -- the wall follows the ring's
	// curve (VERTEX.y/.z both vary with the segment angle; there's no
	// single axis that's "tangential position" directly), and this
	// wraps correctly at the TAU seam for free.
	wall_angle = atan(VERTEX.z, VERTEX.y);
	world_x = VERTEX.x;
}

float hash1(float n) { return fract(sin(n * 127.1) * 43758.5453); }
float noise1(float x) {
	float i = floor(x);
	float f = fract(x);
	return mix(hash1(i), hash1(i + 1.0), smoothstep(0.0, 1.0, f));
}

void fragment() {
	float height_frac = clamp(UV.y / wall_v_max, 0.0, 1.0);

	float u = wall_angle * 12.0;  // radians -> a noise-friendly scale
	float jag = (noise1(u) * 2.0 - 1.0) * jag_amplitude
		+ (noise1(u * 3.3 + 91.0) * 2.0 - 1.0) * jag_amplitude * 0.4;
	float boundary = cliff_frac + jag;
	float sky_mix = smoothstep(boundary - 0.015, boundary + 0.015, height_frac);

	vec4 cliff_c = texture(cliff_texture, UV);

	float phase = TIME * TAU / loop_duration;
	vec2 wobble = vec2(sin(phase), cos(phase)) * drift_amplitude;
	vec2 sky_uv = vec2(
		(world_x + station_width * 0.5) / station_width,
		mod(wall_angle + PI, TAU) / TAU
	) + wobble;
	vec4 day_c = texture(sky_day_texture, sky_uv) * day_tint;
	vec4 night_c = texture(sky_night_texture, sky_uv);
	vec3 sky_c = mix(day_c.rgb, night_c.rgb, night_mix);

	ALBEDO = cliff_c.rgb * (1.0 - sky_mix);
	EMISSION = sky_c * sky_mix;
	NORMAL = FRONT_FACING ? NORMAL : -NORMAL;
}

void light() {
	float ndotl = dot(NORMAL, LIGHT);
	float band;
	if (ndotl > 0.6) {
		band = 1.05;
	} else if (ndotl > 0.25) {
		band = 0.78;
	} else {
		band = 0.5;
	}
	DIFFUSE_LIGHT += ALBEDO * band * LIGHT_COLOR * ATTENUATION;
}
