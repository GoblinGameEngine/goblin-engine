shader_type spatial;
// Every building's distant forms (RemakeBuilding.lod_vc_material: LOD1 meshes, LOD2/3 meshes and the merged clusters
// of them, the sky islands' building LODs).  By day exactly the old StandardMaterial: albedo from the vertex colour,
// rough 0.9.  At night the windows light up (the user, 2026-10-14: "The buildings need to be nicely lit at night"):
//   * LOD1 keeps every pane, baked as the opaque GLASS_RGB (remake/blender/gblod.py): those fragments glow, a pane at a
//     time -- warm lamplight, some cooler, the odd blue television -- each pane lit or dark by its own hash, the lit
//     share following the night (lit_share: RemakeBuilding.set_night, by the hour), panes switching now and then;
//     ground-floor panes (shops) brighter and whiter;
//   * LOD2/3 (massing = true) have no panes (solid blocks, their walls darkened by their glass share): a window grid
//     is drawn on the walls instead -- storeys of 3.1 m by bays of 2.6 m.
render_mode cull_back, specular_schlick_ggx;

global uniform float daylight;
uniform bool massing = false;
uniform float lit_share = 0.65;
uniform float glow = 3.2;

const vec3 GLASS = vec3(0.09, 0.105, 0.12);

varying vec3 wpos;
varying vec3 wnrm;
varying float lh;                  // height in the mesh's own frame (LOD1: above the building's base)
varying vec3 lpos;                 // the mesh's own frame: which pane is lit is decided here, so a building that moves
varying vec3 lnrm;                 // (a sky island's) keeps its pattern -- hashed in world space, the panes of every
varying vec3 lup;                  // drifting island reshuffled each frame: a flicker all over the islands at night

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	lh = VERTEX.y;
	lpos = VERTEX;
	lnrm = NORMAL;
	vec3 upw = -normalize(vec3(0.0, wpos.y, wpos.z));
	lup = normalize((vec4(upw, 0.0) * MODEL_MATRIX).xyz);     // (the world's up in the mesh's frame)
}

float hash3(vec3 p) {
	p = fract(p * vec3(0.1031, 0.1030, 0.0973));
	p += dot(p, p.yxz + 33.33);
	return fract((p.x + p.y) * p.z);
}

vec3 lamp(float k) {
	if (k < 0.55) return vec3(1.0, 0.70, 0.40);        // warm lamps
	if (k < 0.80) return vec3(1.0, 0.82, 0.58);        // softer, whiter bulbs
	if (k < 0.92) return vec3(1.0, 0.60, 0.32);        // low amber
	if (k < 0.97) return vec3(0.55, 0.70, 1.0);        // a television
	return vec3(0.85, 1.0, 0.75);                      // a kitchen striplight
}

void fragment() {
	vec3 col = COLOR.rgb;
	ALBEDO = col;
	// a window bay's size on screen (taken here, in uniform control flow): one under ~4 pixels shimmers as the view
	// moves -- seen from the sky islands and across Calder at 200-300 m (research/sky_islands/warrens/flicker.md)
	float bay_px = 2.6 / max(length(fwidth(lpos)), 1e-5);
	ROUGHNESS = 0.9;
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	if (night > 0.001) {
		vec3 up = -normalize(vec3(0.0, wpos.y, wpos.z));
		float wall = 1.0 - smoothstep(0.25, 0.45, abs(dot(wnrm, up)));
		vec3 t = normalize(cross(lup, lnrm) + vec3(1e-5));   // (along the wall, in the mesh's frame)
		float h = dot(lpos, lup);                      // m up, in the mesh's frame
		vec3 cell;
		float pane = 0.0;
		bool shop = false;
		if (!massing) {
			// LOD1: its own panes
			if (distance(col, GLASS) < 0.012) {
				pane = 1.0;
				cell = floor(vec3(dot(lpos, t) / 1.4, h / 3.1, dot(lpos, lnrm) / 3.0));
				shop = lh < 3.6;
			}
		} else if (wall > 0.5) {
			// LOD2/3: a grid of windows on the walls
			vec2 g = vec2(dot(lpos, t) / 2.6, h / 3.1);
			vec2 f = fract(g);
			pane = step(0.14, f.x) * step(f.x, 0.86) * step(0.2, f.y) * step(f.y, 0.84);
			cell = vec3(floor(g), floor(dot(lpos, lnrm) / 3.0));
		}
		// far off, single panes go below a pixel and alias away: the walls take on their windows' average glow instead
		float far_k = smoothstep(350.0, 1400.0, length(wpos - CAMERA_POSITION_WORLD));
		far_k = max(far_k, 1.0 - smoothstep(3.0, 6.0, bay_px));
		if (far_k > 0.0 && wall > 0.5 && (massing || pane > 0.0)) {
			EMISSION += vec3(1.0, 0.72, 0.45) * glow * lit_share * 0.45 * far_k * night * wall;
			pane *= 1.0 - far_k;
		}
		if (pane > 0.0) {
			float hk = hash3(cell);
			float epoch = floor(TIME / 420.0 + hk * 9.0);           // panes change now and then
			float lit = step(hash3(cell + epoch * 1.37), shop ? 0.92 : lit_share);
			vec3 c = shop ? vec3(1.0, 0.92, 0.80) : lamp(hash3(cell + 7.1));
			float e = glow * (shop ? 1.5 : 1.0) * (0.75 + 0.5 * hash3(cell + 3.3));
			EMISSION += c * lit * pane * e * night;
			ALBEDO = mix(col, col * 0.5, lit * pane * night);
		}
	}
}
