shader_type spatial;
// The islands' balloons (SkyIslands: two MultiMeshes over all islands), 100 m x 1 km, origin at the bottom, +Y up.
// By day: canvas gores, every other one in the clan's colour, and rope bands.  At night they glow from within in the
// clan's colours, like paper lanterns a kilometre tall -- and some carry the Skein's advertising: a vertical
// dot-matrix banner down two sides, scrolling (ads, SkyDotFont rows), readable across the station.
// INSTANCE_CUSTOM: rgb the clan's colour, a = (ad row + 1) / 128 (0: no ad).
render_mode diffuse_lambert, specular_disabled;

global uniform float daylight;
uniform sampler2D ads : filter_nearest, repeat_disable;
uniform vec3 canvas : source_color = vec3(0.93, 0.92, 0.88);
uniform float gores = 16.0;
uniform float dot_m = 4.6;            // m a dot of the banners
uniform float scroll = 2.0;           // dots a second

varying vec3 lp;
varying vec4 cus;

void vertex() {
	lp = VERTEX;
	cus = INSTANCE_CUSTOM;
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	float ang = atan(lp.x, lp.z);                       // -pi..pi round the envelope
	float g = (ang / 6.28318 + 0.5) * gores;
	float seam = smoothstep(0.0, 0.06, fract(g)) * smoothstep(1.0, 0.94, fract(g));
	float alt = mod(floor(g), 2.0);
	vec3 clan = cus.rgb;
	float band = step(abs(fract(lp.y / 250.0) - 0.5), 0.012);     // rope bands
	vec3 day = mix(canvas, mix(canvas, clan, 0.55), alt);
	day = mix(day * 0.82, day, seam);
	day = mix(day, vec3(0.25, 0.22, 0.18), band);
	ALBEDO = day;
	// the glow within: brightest at the middle of each gore and mid-height, the seams and bands dark
	float yk = (0.45 + 0.55 * smoothstep(0.0, 160.0, lp.y)) * (0.45 + 0.55 * smoothstep(1000.0, 840.0, lp.y));   // (dimmer at the domes)
	// (a paper lantern: the gore's middle bright, its seams dark; a little warmer than the cloth)
	float gore_mid = pow(sin(3.14159 * fract(g)), 0.6);
	vec3 glow = mix(clan, vec3(1.0, 0.8, 0.55), 0.3) * (0.25 + 0.75 * gore_mid) * (1.0 - band) * yk * 0.75;
	// an ad: two banners, 7 dots wide, down opposite sides; letters stacked top to bottom
	float row = floor(cus.a * 128.0 + 0.5) - 1.0;
	vec3 ad = vec3(0.0);
	if (row >= 0.0) {
		float arc = ang * 50.0;                                         // m round from the banner's centre
		float side = abs(arc) < 60.0 ? arc : (abs(abs(arc) - 157.08) < 60.0 ? (abs(arc) - 157.08) * sign(arc) : 999.0);
		float cx = floor(side / dot_m + 3.5);                           // 0..6 across the banner (5 dot columns + margins)
		if (cx >= 0.0 && cx <= 6.0) {
			float yy = (900.0 - lp.y) / dot_m + TIME * scroll;          // dots down from the top
			vec2 sz = vec2(textureSize(ads, 0));
			float n_chars = floor(sz.x / 6.0);
			float per = 9.0;                                            // 7 dot rows + a gap of 2
			float ci = mod(floor(yy / per), n_chars + 3.0);
			float r = floor(mod(yy, per));
			float on = 0.0;
			if (cx >= 1.0 && cx <= 5.0 && r < 7.0 && ci < n_chars && lp.y > 140.0 && lp.y < 900.0) {
				on = texture(ads, vec2((ci * 6.0 + cx - 1.0 + 0.5) / sz.x, (row * 8.0 + r + 0.5) / sz.y)).r;
			}
			vec2 f = fract(vec2(side / dot_m + 3.5, yy)) - 0.5;
			float disc = smoothstep(0.45, 0.25, length(f));
			vec3 led = mix(vec3(1.0, 0.95, 0.75), clan, 0.35);
			ad = led * on * disc * 2.2;
			if (lp.y > 140.0 && lp.y < 900.0) {
				ALBEDO = mix(ALBEDO, vec3(0.12), 0.85);                  // the banner's dark board
			}
		}
	}
	EMISSION = (glow * 1.6 + ad) * night * 1.4 + ad * 0.25;
	ALBEDO *= mix(1.0, 0.35, night);                  // (lit from inside, the cloth's own shading fades)
}
