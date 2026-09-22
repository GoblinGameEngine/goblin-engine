shader_type spatial;
// Ceiling sky -- day/night cycle driven by scripts/world/DaySkySystem.gd,
// which updates the uniforms below every frame. unshaded: this IS the
// light source/environment backdrop, not a lit surface -- it should read
// the same regardless of the scene's own lighting state, same reasoning
// as a real sky/skybox never being "in shadow." cull_disabled matches
// this project's other flat-panel materials (the ceiling is only ever
// seen from below anyway, but costs nothing to leave permissive).
//
// sky_day_texture/sky_night_texture are TILED (StationRingBuilder.gd's
// TILE_CEILING=8m, both axes) -- see gen_sky_textures.scm's own header
// comment for why a single wide band can't be baked into a tiled texture
// (it would repeat every 8m along the width) -- the BAND below is
// instead computed from actual world-space X (this station's RingBody
// never moves, so object space IS world space here), entirely
// independent of the tiled UV the cloud/star/panel-grid detail uses.
// Deliberately no outline on the band (requested directly) -- it's a
// pure color effect on an already-flat, single-normal surface, so the
// screen-space outline pass (shaders/screen_outline.gdshader, depth/
// normal-edge based) was never going to draw one there anyway.
render_mode unshaded, cull_disabled;

uniform sampler2D sky_day_texture : source_color, filter_nearest, repeat_enable;
uniform sampler2D sky_night_texture : source_color, filter_nearest, repeat_enable;
uniform float night_mix : hint_range(0.0, 1.0) = 0.0;
uniform vec4 day_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 band_color : source_color = vec4(1.0, 0.95, 0.85, 1.0);
uniform float band_center = 0.0;       // world X (meters) -- the band's current west<->east position
uniform float band_half_width = 25.0;  // meters -- DaySkySystem.gd sets this to 5% of SpaceStation.WIDTH
uniform float band_intensity = 1.0;    // 0 at night (no sun), ramps with dawn/dusk

varying float world_x;

void vertex() {
	world_x = VERTEX.x;
}

void fragment() {
	vec4 day_c = texture(sky_day_texture, UV) * day_tint;
	vec4 night_c = texture(sky_night_texture, UV);
	vec3 base = mix(day_c.rgb, night_c.rgb, night_mix);

	float d = abs(world_x - band_center);
	float band = 1.0 - smoothstep(band_half_width * 0.7, band_half_width, d);
	base += band_color.rgb * band * band_intensity;

	ALBEDO = base;
}
