# Modern FPS movement reference

Numbers and feel notes gathered for the SSC player (2026-10-16), from the games that
define the modern standard (Mirror's Edge, Titanfall 2, Apex Legends, Call of Duty
MW2019+, Dying Light, Half-Life: Alyx's sliding predecessors F.E.A.R./Crysis) and from
the human-movement data already in research/animation (gait_reference.md).

Our scale: capsule r 0.18, standing h 1.45 (eye 1.43 above the feet, origin at the
eyes); warren openings ≥ 1.0 wide × 2.2 m tall; historic stairs to 52°; step-up 0.36 m
already proven in the test walker.

## Sprint
- Industry: sprint ≈ 1.6–1.9 × walk; ours exists (4.2 → 7.5 m/s, 1.79×). Keep.

## Crouch
- Typical: capsule to ~60–65 % of standing, eye to ~55–65 %, transition 0.2–0.3 s,
  smooth (lerped eye, never snapped), crouch-walk ≈ 0.45–0.55 × walk.
- Ours: capsule 1.45 → 0.95 (66 %), eye 1.43 → 0.92, 0.22 s smoothstep, speed 2.1 m/s.
  Hold Ctrl or toggle C (pad: B). Un-crouch is blocked while a ceiling is within the
  standing capsule (test_move up), and re-checked every frame.

## Slide (F.E.A.R./Apex/MW lineage)
- Trigger: crouch while sprinting on the ground (speed above ~0.9 × sprint).
- An initial boost (~1.15–1.25 × entry speed, capped), friction ~3.5–5 m/s² on the
  flat, gravity-along-slope added so downhill slides run on; steering heavily damped
  (~15–25 % authority); ends below ~2.2 m/s or on jump (slide-hop) or when crouch is
  released and headroom exists. Camera drops with the crouch eye and tilts ~3–6°.
- Ours: boost to min(entry × 1.2, 9.0), decel 4.0 + slope term, steer 20 %, end < 2.2.

## Step-up
- Smooth 0.2–0.4 m automatic steps (every modern FPS; Source's 18 units = 0.457).
- Ours: 0.36 m (matches the test walker and the exterior stone steps), grounded only,
  implemented as "would collide → try from STEP higher → settle down", then the eye
  smooths the vertical jump out over ~0.1 s.

## Mantle / vault (Dying Light, Titanfall, MW)
- Reach: mantle onto ledges up to about chest/eye height from the feet while
  grounded, and up to ~1 m above the feet mid-air; vault = low mantle (≤ ~0.9 m) that
  keeps horizontal speed and can be crossed over.
- Detection: forward blocked at knee/chest, clear at head + step; find the ledge top
  with a down-ray from ahead/above; require standing (or crouched) headroom on top.
- Timing: vault ~0.45 s, mantle ~0.7–0.9 s, driven by an eased curve (fast hands-on,
  slower weight-up, settle), with the camera carried along the curve.
- Ours: triggered by jump (held or pressed) facing the obstacle, grounded or airborne;
  vault ≤ 0.55 m above feet (0.45 s), mantle ≤ 1.35 m above feet grounded / ≤ 1.0 m
  airborne (0.8 s). On top we land crouched if only 1.0 m of headroom exists.

## Ledge grab / hang / shimmy / climb (Dying Light, Mirror's Edge, Tomb Raider)
- While airborne and falling, a ledge passing within hand reach (hands ≈ eye + 0.25,
  i.e. the capsule's top) in front latches a hang: body pressed to the wall, hands on
  the edge, gravity off.
- From the hang: forward/jump climbs (a mantle from hanging, ~1.0 s), back/crouch
  drops, strafe shimmies sideways at ~0.7 m/s while the edge continues and the wall
  stays flush.
- Edge validity: a near-horizontal top surface (slope < ~35°), a wall face in front,
  enough room for the hanging capsule below the edge.

## Lean (Rainbow Six, Tarkov, MW)
- Peek sideways around cover: camera translates 0.25–0.4 m and rolls 8–15°, body
  stays; blocked by walls (the lean shortens against geometry). Q / R held.
- Ours: 0.30 m, 10°, spring-smoothed, shape-cast capped.

## Camera feel ("nice smooth expressive")
- Every vertical state change is smoothed through the eye (crouch, step-up, mantle
  curve, landing dip ~0.05–0.1 m on hard landings).
- The body is the expressive channel (the animator's walk/crouch/slide/hang poses,
  springs and follow-through are already built for the NPCs); the camera stays firm —
  aim is never animated sideways, which is what keeps a true-FPS body comfortable.

## Who else uses these animations
All of it goes through NpcAnimator (crouch factor, slide/hang poses as ride-style
overrides, mantle as a timed pose curve), so every NPC human can crouch, slide,
mantle and hang with the same motion the player sees of themselves — the brief's
requirement that one animation set drives all humans.
