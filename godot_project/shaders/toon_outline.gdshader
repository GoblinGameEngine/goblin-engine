shader_type spatial;
// Classic inverted-hull outline, chained onto toon.gdshader via
// next_pass (see ToonShading.gd) -- renders a second, slightly enlarged
// copy of the same mesh with its front faces culled (cull_front), so
// only the enlarged BACK faces show, poking out just past the real
// mesh's silhouette from the camera's point of view. Unshaded flat
// color, no lighting math needed for a pure outline.
//
// Samples the SAME albedo texture as the main pass and discards the same
// cutout texels -- REAL BUG found live: this pass used to ignore alpha
// entirely and just paint every fragment black, so a hard-cutout mesh
// (porch railings, fences, window panes -- see toon.gdshader's own
// comment on why those are cutouts, not blends) got a solid black
// outline shape covering its WHOLE quad, gaps and all, not just the
// visible bars/frame -- on top of (and compounding) the main pass's own
// version of the same bug.
render_mode cull_front, unshaded, depth_draw_always;

uniform sampler2D albedo_texture : source_color, filter_nearest, repeat_enable;
uniform bool use_texture = true;
uniform float outline_width : hint_range(0.0, 0.2) = 0.01;
uniform vec4 outline_color : source_color = vec4(0.02, 0.02, 0.02, 1.0);

void vertex() {
	VERTEX += NORMAL * outline_width;
}

void fragment() {
	if (use_texture && texture(albedo_texture, UV).a < 0.5) {
		discard;
	}
	ALBEDO = outline_color.rgb;
}
