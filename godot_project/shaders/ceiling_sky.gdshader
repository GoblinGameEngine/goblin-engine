shader_type spatial;
// Ceiling sky -- day/night cycle driven by scripts/world/DaySkySystem.gd,
// which updates the uniforms below every frame. unshaded: this IS the
// light source/environment backdrop, not a lit surface -- it should read
// the same regardless of the scene's own lighting state, same reasoning
// as a real sky/skybox never being "in shadow." cull_disabled matches
// this project's other flat-panel materials.
//
// sky_day_texture/sky_night_texture are your own two upscaled reference
// photos (blender_scripts/upscale_sky_wallpapers.py). NOT tiled -- a real
// photo repeating across the ceiling read as an obvious, ugly seam every
// repeat (confirmed live, reported directly: "it looks terrible
// repeating like that"). Instead the UV is computed directly from world
// position to span the WHOLE cylinder in one single, non-repeating pass:
// U across the full width (station_width), V once fully around the
// circumference (0..1 via the wrap angle). This still has exactly ONE
// seam (where the angle wraps from 2*PI back to 0 -- a closed loop
// mapped from a rectangular photo always has at least one), but one seam
// beats fifteen-plus repeats. Both animate with a slow, small, exactly-
// periodic drift (loop_duration/drift_amplitude below) -- "the
// animations should last a minimum of 15 seconds and have minimal
// movement." Uses Godot's builtin TIME directly (sin/cos are exactly
// periodic, so this loops with NO seam or jump, every loop_duration
// seconds, forever). The SUN and MOON bands are separate, non-tiled
// features computed from the same world-space X (this station's
// RingBody never moves, so object space IS world space here) -- no
// outline on either band, both are pure color effects on an already-
// flat, single-normal surface, so the screen-space outline pass (depth/
// normal-edge based) was never going to draw one there anyway.
// fog_disabled: SpaceStation.gd's distance fog is meant to soften far
// FOREGROUND geometry (buildings, the ring's own curving-away floor) --
// applied to this too, it washed the sky out toward the fog's own dark
// color at any real distance, which is backwards for something meant to
// read as "the sky itself," not an object sitting IN front of it.
render_mode unshaded, cull_disabled, fog_disabled;

// filter_linear_mipmap_anisotropic, not plain filter_linear: stretching
// one 2048x2048 photo across the WHOLE cylinder means looking anywhere
// close to straight down the ring's own axis (a real, if uncommon,
// viewing angle -- confirmed live) puts the view nearly tangent to the
// curved ceiling, where ordinary filtering compresses many texels into
// very few pixels and washes out to a flat blur. Anisotropic filtering
// is the standard fix for exactly this "texture stretching toward a
// vanishing point" case (the same problem a flat floor stretching to
// the horizon has).
uniform sampler2D sky_day_texture : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D sky_night_texture : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float night_mix : hint_range(0.0, 1.0) = 0.0;
uniform vec4 day_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float loop_duration = 22.0;      // seconds -- >= the requested 15s minimum
uniform float drift_amplitude = 0.0018;  // UV units -- small on purpose ("very little movement"); UV now spans the WHOLE cylinder, not one small tile, so this is deliberately much smaller than the old tiled version's
uniform float station_width = 1000.0;    // SpaceStation.WIDTH, set from GDScript -- the U axis spans exactly this, no repeat

uniform vec4 band_color : source_color = vec4(1.0, 0.95, 0.85, 1.0);
uniform float band_center = 0.0;
uniform float band_half_width = 25.0;
uniform float band_intensity = 1.0;

uniform vec4 moon_color : source_color = vec4(0.75, 0.8, 0.95, 1.0);
uniform float moon_center = 0.0;
uniform float moon_half_width = 25.0;
uniform float moon_intensity = 0.0;

varying float world_x;
varying float world_angle;

void vertex() {
	world_x = VERTEX.x;
	world_angle = atan(VERTEX.z, VERTEX.y);
}

void fragment() {
	// A small circular drift, exactly periodic at loop_duration seconds
	// (sin/cos share that period, 90-degree phase apart) -- "animate
	// them both," both day and night textures get the same wobble.
	float phase = TIME * TAU / loop_duration;
	vec2 wobble = vec2(sin(phase), cos(phase)) * drift_amplitude;

	vec2 sky_uv = vec2(
		(world_x + station_width * 0.5) / station_width,
		mod(world_angle + PI, TAU) / TAU
	) + wobble;

	vec4 day_c = texture(sky_day_texture, sky_uv) * day_tint;
	vec4 night_c = texture(sky_night_texture, sky_uv);
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
