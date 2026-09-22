shader_type spatial;
// Ceiling sky -- day/night cycle driven by scripts/world/DaySkySystem.gd,
// which updates the uniforms below every frame. unshaded: this IS the
// light source/environment backdrop, not a lit surface -- it should read
// the same regardless of the scene's own lighting state, same reasoning
// as a real sky/skybox never being "in shadow." cull_disabled matches
// this project's other flat-panel materials.
//
// sky_day_texture/sky_night_texture are TILED (StationRingBuilder.gd's
// TILE_CEILING=60m, both axes -- large on purpose, requested directly:
// "large fluffy clouds... a mosaic," not a densely-repeating small
// pattern). The SUN and MOON bands are separate, non-tiled features
// computed from world-space X (this station's RingBody never moves, so
// object space IS world space here), independent of the tiled UV the
// cloud/star/galaxy/panel-grid detail uses -- a band spanning the whole
// width can't be baked into a tiled texture without repeating every
// TILE_CEILING meters. No outline on either band (requested directly for
// the sun originally, same reasoning applies to the moon) -- both are
// pure color effects on an already-flat, single-normal surface, so the
// screen-space outline pass (depth/normal-edge based) was never going to
// draw one there anyway.
// fog_disabled: SpaceStation.gd's distance fog is meant to soften far
// FOREGROUND geometry (buildings, the ring's own curving-away floor) --
// applied to this too, it washed the sky out toward the fog's own dark
// color at any real distance, which is backwards for something meant to
// read as "the sky itself," not an object sitting IN front of it.
// Confirmed live: noon readback several dozen meters up read as a
// muted gray-blue instead of the texture's own bright, saturated colors.
render_mode unshaded, cull_disabled, fog_disabled;

uniform sampler2D sky_day_texture : source_color, filter_nearest, repeat_enable;
uniform sampler2D sky_night_texture : source_color, filter_nearest, repeat_enable;
uniform float night_mix : hint_range(0.0, 1.0) = 0.0;
uniform vec4 day_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float cloud_drift = 0.0;  // slow UV scroll on the day texture only -- "I would like it if [the clouds] did [move]"

uniform vec4 band_color : source_color = vec4(1.0, 0.95, 0.85, 1.0);
uniform float band_center = 0.0;
uniform float band_half_width = 25.0;
uniform float band_intensity = 1.0;

uniform vec4 moon_color : source_color = vec4(0.75, 0.8, 0.95, 1.0);
uniform float moon_center = 0.0;
uniform float moon_half_width = 25.0;
uniform float moon_intensity = 0.0;

varying float world_x;

void vertex() {
	world_x = VERTEX.x;
}

void fragment() {
	vec4 day_c = texture(sky_day_texture, UV + vec2(cloud_drift, 0.0)) * day_tint;
	vec4 night_c = texture(sky_night_texture, UV);
	vec3 base = mix(day_c.rgb, night_c.rgb, night_mix);

	float ds = abs(world_x - band_center);
	float band = 1.0 - smoothstep(band_half_width * 0.7, band_half_width, ds);
	base += band_color.rgb * band * band_intensity;

	// Dimmer than the sun band -- this is moonlight, not sunlight.
	float dm = abs(world_x - moon_center);
	float moon = 1.0 - smoothstep(moon_half_width * 0.7, moon_half_width, dm);
	base += moon_color.rgb * moon * moon_intensity * 0.55;

	ALBEDO = base;
}
