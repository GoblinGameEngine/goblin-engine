shader_type spatial;
// A building's window panes at full detail (RemakeBuilding: every glass surface of a LOD0 building).
//
// Up close (< NEAR_M) it is plain glass you see through into the real rooms -- their furniture (RemakeBuilding's
// interior mesh) is drawn only that near.  Further off the rooms behind are empty, so the pane turns into what a
// window looks like from the street (the user, 2026-10-14: "Use tricks like lens flare and reflections to hide
// building interiors, but only where necessary"):
//   * by day mostly a reflection: the sky's colour at a fresnel angle over a dim, tinted room;
//   * a fake room behind every pane (interior mapping: the view ray is followed into a box -- back wall, side walls,
//     floor, ceiling -- a storey high and a bay wide, in the mesh's own frame so it holds still), its walls and
//     curtains varying room to room;
//   * at night lit or dark by the hour (lit_share, by a per-room hash), lit rooms bright enough to bloom (the
//     environment's glow does the halo), the odd blue television.
render_mode blend_mix, depth_draw_opaque, cull_back, specular_schlick_ggx;

global uniform float daylight;
global uniform vec4 sky_color;
uniform vec3 tint : source_color = vec3(0.72, 0.8, 0.84);
uniform float alpha = 0.2;            // the pane's own see-through (the glass's alpha by day)
uniform bool lit = true;              // (this building's windows ever lit at night)
uniform float lit_share = 0.65;       // the share of rooms with a light on now (RemakeBuilding, by the hour)
uniform float near_m = 10.0;          // glass you see through within this ...
uniform float far_m = 16.0;           // ... a window from the street beyond this (RemakeBuilding.INTERIOR_M)

varying vec3 lpos;
varying vec3 lnrm;
varying vec3 lup;
varying vec3 lcam;
varying float dist;

void vertex() {
	lpos = VERTEX;
	lnrm = NORMAL;
	vec3 wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 upw = -normalize(vec3(0.0, wpos.y, wpos.z));
	lup = normalize((vec4(upw, 0.0) * MODEL_MATRIX).xyz);
	lcam = (inverse(MODEL_MATRIX) * vec4(CAMERA_POSITION_WORLD, 1.0)).xyz;
	dist = length(wpos - CAMERA_POSITION_WORLD);
}

float hash3(vec3 p) {
	p = fract(p * vec3(0.1031, 0.1030, 0.0973));
	p += dot(p, p.yxz + 33.33);
	return fract((p.x + p.y) * p.z);
}

vec3 wall_col(float h) {
	if (h < 0.25) return vec3(0.78, 0.70, 0.58);   // cream
	if (h < 0.45) return vec3(0.62, 0.68, 0.70);   // pale blue-grey
	if (h < 0.62) return vec3(0.74, 0.58, 0.48);   // terracotta
	if (h < 0.78) return vec3(0.60, 0.66, 0.52);   // sage
	if (h < 0.9) return vec3(0.80, 0.78, 0.74);    // white
	return vec3(0.55, 0.45, 0.40);                 // wood panelling
}

void fragment() {
	float night = clamp((0.78 - daylight) / 0.45, 0.0, 1.0);
	float far_k = smoothstep(near_m, far_m, dist);
	vec3 n = normalize(lnrm);
	vec3 up = normalize(lup - n * dot(lup, n));
	vec3 t = normalize(cross(up, n));
	vec3 v = normalize(lpos - lcam);                    // the view ray, in the mesh's frame
	// fresnel: how much of the sky the pane reflects
	float cosv = clamp(dot(-v, n), 0.0, 1.0);
	float fres = 0.06 + 0.94 * pow(1.0 - cosv, 5.0);
	vec3 refl = mix(sky_color.rgb, vec3(0.85, 0.88, 0.92), 0.25) * mix(1.0, 0.25, night);
	vec3 col = tint * 0.25;
	float a = alpha;
	vec3 emit = vec3(0.0);
	if (far_k > 0.0) {
		// the room behind: a box a bay (3.2 m) wide, a storey (3.1 m) high, 4 m deep, entered at the pane
		const float W = 3.2;
		const float H = 3.1;
		const float D = 4.0;
		vec3 q = vec3(dot(lpos, t), dot(lpos, up), 0.0);
		vec3 d = vec3(dot(v, t), dot(v, up), max(dot(v, -n), 0.05));
		vec3 cell = vec3(floor(q.x / W), floor(q.y / H), floor(dot(lpos, n) / 3.0));
		vec3 lo = vec3(cell.x * W, cell.y * H, 0.0);
		vec3 hi = lo + vec3(W, H, D);
		vec3 tx = (mix(lo, hi, step(vec3(0.0), d)) - q) / d;
		float th = min(min(tx.x, tx.y), tx.z);
		vec3 hit = q + d * th;
		vec3 rel = (hit - lo) / vec3(W, H, D);           // 0..1 in the room
		float rh = hash3(cell + 7.1);
		vec3 wc = wall_col(rh);
		vec3 room;
		if (th == tx.z) {
			room = wc;                                       // the back wall: a picture, a dark sofa line
			room *= 1.0 - 0.45 * step(0.12, rel.y) * step(rel.y, 0.3) * step(0.25, rel.x) * step(rel.x, 0.75);
			room *= 1.0 - 0.3 * step(0.5, rel.y) * step(rel.y, 0.68) * step(0.42, rel.x) * step(rel.x, 0.58);
		} else if (th == tx.y) {
			room = d.y < 0.0 ? vec3(0.42, 0.32, 0.24) : vec3(0.9, 0.88, 0.84);   // floor (wood) or ceiling
		} else {
			room = wc * 0.82;                                // a side wall
		}
		// curtains or blinds in some rooms: near the pane, at the sides or half drawn
		float ch = hash3(cell + 3.3);
		vec2 pr = (q.xy - lo.xy) / vec2(W, H);
		vec3 curtain = mix(vec3(0.7, 0.2, 0.18), vec3(0.85, 0.8, 0.62), fract(ch * 7.0));
		float drawn = 0.0;
		if (ch < 0.35) {
			drawn = step(pr.x, 0.18) + step(0.82, pr.x);
		} else if (ch < 0.5) {
			drawn = step(0.55, pr.y);                       // blinds half down
		}
		drawn = clamp(drawn, 0.0, 1.0);
		room = mix(room, curtain, drawn);
		// light: by day a dim room under the sky's light; at night lit by the hour, or dark (a TV now and then)
		float on = (lit && hash3(cell + 1.7) < lit_share) ? 1.0 : 0.0;
		vec3 lamp = mix(vec3(1.0, 0.72, 0.42), vec3(0.95, 0.9, 0.8), step(0.8, hash3(cell + 9.1)));
		float depth_dim = mix(1.0, 0.65, rel.z);
		vec3 day_room = room * 0.32 * depth_dim;
		vec3 night_room = room * lamp * (on * 1.25 * depth_dim + 0.03);
		float tv = (on < 0.5 && hash3(cell + 5.5) > 0.9) ? 1.0 : 0.0;
		night_room += vec3(0.25, 0.4, 0.9) * tv * (0.6 + 0.4 * sin(TIME * 7.0 + rh * 20.0)) * 0.35;
		vec3 inside = mix(day_room, vec3(0.0), night);
		col = mix(col, inside, far_k);
		emit = night_room * night * far_k * (on > 0.5 ? 1.35 : 1.0);   // (over 1: the glow blooms round lit panes)
		a = mix(alpha, 1.0, far_k);
		fres *= mix(1.0, 0.55, night * on);
	}
	// near at night: the real room's lamp (only lit when you're inside) -- a soft glow on the pane from outside
	emit += tint * night * (lit ? 0.18 : 0.0) * (1.0 - far_k);
	ALBEDO = mix(col, refl, fres);
	EMISSION = emit;
	ROUGHNESS = 0.06;
	METALLIC = 0.0;
	SPECULAR = 0.8;
	ALPHA = clamp(a + fres * 0.6, 0.0, 1.0);
}
