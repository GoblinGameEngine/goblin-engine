shader_type spatial;
// Road markings (MapRoads "paint_w" / "paint_y": thin strips of geometry).  A 12 cm line is under a pixel wide beyond
// ~60 m and its pixels pop on and off as the view moves -- a shimmer across every road at middle distance
// (research/sky_islands/warrens/flicker.md).  So the paint fades into the asphalt's own tone by the line's size on
// screen (how many pixels its width covers), and wholly by fade_to m: the lines are there near, quiet far.
render_mode cull_disabled;

uniform vec3 paint : source_color = vec3(0.93, 0.93, 0.9);
uniform vec3 asphalt : source_color = vec3(0.24, 0.24, 0.25);
uniform float line_m = 0.12;
uniform float fade_to = 160.0;

varying float dist;

void vertex() {
	dist = length((MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz);
}

void fragment() {
	// metres a pixel spans here (the view's own derivative): a line under ~1.5 px fades out
	float m_px = length(fwidth(VERTEX));
	float px = line_m / max(m_px, 1e-5);
	float k = smoothstep(0.8, 2.5, px) * (1.0 - smoothstep(fade_to * 0.5, fade_to, dist));
	ALBEDO = mix(asphalt, paint, k);
	ROUGHNESS = 0.7;
}
