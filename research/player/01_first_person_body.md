# First-person bodies: how games keep you from seeing inside your own head

Research for the SSC player body (2026-10-16). The question: the player body (the
generated NpcCharacter, as already ridden on the bicycle) now needs its head and neck
back, and the player must NEVER see the inside of their own head, while the shadow,
third-person tools and any mirror still show a whole person.

## 1. The two families

**Separate first-person arms (Skyrim, Fallout 3/NV/4, most shooters).**
Bethesda games keep two rigs: a "1st person" skeleton with arms-only (and weapon)
meshes rendered in their own pass with their own FOV and depth range, and the full
3rd-person body that is hidden from the player camera but still used for shadows
(Skyrim renders your full-body shadow from the invisible world model — which is why
the vanilla shadow shows a head while the view has no body at all; looking down you
see nothing). Mods (Joy of Perspective, Improved Camera) convert this to a true body
by attaching the camera to the head bone of the world model and hiding head parts.
- Pros: no self-clipping ever, weapon alignment is authored, FOV freedom.
- Cons: two rigs to animate, the body you see on the bike/in shadows is not the body
  you play; looking down shows nothing (exactly the stopgap we have now).

**True first-person body (Mirror's Edge, Escape from Tarkov, Star Citizen,
Cyberpunk 2077, Alien: Isolation).** One full body; the camera sits at the eyes.
Each solves "the inside of the head" differently:
- **Head-bone shrink/hide:** the head (and sometimes shoulders' clothing) is scaled
  to ~0 or skinned to a hidden slot for the first-person view (Cyberpunk hides head +
  some torso parts per view config). Where the engine can't do per-camera bone poses,
  the shrink is permanent and a second shadow-only head is added.
- **Per-view mesh masks:** head geometry lives in its own mesh/section flagged
  "owner no see" (Unreal's `bOwnerNoSee`) — rendered for everyone except the owning
  camera; shadows render it regardless. This is the cleanest where available.
- **Near plane + head-bone placement:** some games just keep the camera slightly
  forward of the head geometry with a small near plane (0.02–0.05 m) — fragile alone
  (hair, hats, steep pitch all break it), always combined with one of the above.
- **Camera attachment:** either camera-follows-head-bone (full root-motion fidelity,
  needs heavy stabilisation to avoid motion sickness — Tarkov, and EA's Mirror's Edge
  with hand-tuned camera curves per animation) or body-follows-camera (the controller
  stays authoritative, the body is posed/IK'd under it — Star Citizen's "camera is
  boss" after their first attempt, most modern implementations). Body-follows-camera
  keeps aim exact and motion comfortable.
- **Look-down correction:** when pitching down, the body is bent (spine curl) and/or
  pushed back a few cm so the chest doesn't cross the near plane.

## 2. Godot 4 specifics

- `VisualInstance3D.layers` vs `Camera3D.cull_mask`: a mesh whose layer bit is
  excluded from the camera's cull mask is not drawn by that camera, **but it still
  renders into every light's shadow map** (shadow maps are per-light, not per-camera;
  Godot issue #70556 documents that even the *light's* cull mask does not remove a
  caster from the shadow pass). So "player-hidden layer" = invisible to the player
  camera, full shadow kept, visible to any other camera (tools, mirrors, cutscenes).
- There is no per-camera bone pose and no `bOwnerNoSee`, so the head must be a
  separate `MeshInstance3D` to get its own layer. NpcBody already builds the body as
  named parts ("head", "neck", torso, limbs) merged at assemble time — splitting at
  assemble time costs nothing and keeps one skeleton and one skinning source of truth.
- `GeometryInstance3D.cast_shadow = SHADOWS_ONLY` exists as a fallback (a duplicate
  full mesh for shadows), but it would double the skinning cost — not needed given
  the layer behaviour above.
- Default camera near plane is 0.05; the capsule radius 0.18 keeps walls at least
  ~0.13 m from the eye, so the camera never enters world geometry while the capsule
  is respected. Near plane 0.03 gives margin against the body's own arms during
  swings.

## 3. Decision for SSC

**True first-person body, body-follows-camera, layer-masked head.**
- The body is the same generated person the bicycle already seats
  (`NpcTraits.person(seed, "player", ...)`), so the bike, the shadow and the view all
  agree — and the bike's collapsed-neck stopgap is replaced by the same split body.
- `NpcCharacter.prepare(..., split_head=true)` assembles head+neck body geometry,
  hair, and head-slot garments into separate mesh instances on `HEAD_LAYER`
  (render layer 12, bit `1 << 11`; vehicles use bit 9 for INTERIOR_LAYER).
- The player `Camera3D.cull_mask` clears that bit. Lights keep it: the shadow has a
  head. Any other camera (DevBridge screenshots, future mirrors) sees the whole
  person.
- The controller (StationPlayer) stays authoritative: the body node is glued to the
  capsule (feet at the capsule's bottom, yaw = body yaw) and posed by NpcAnimator
  (speed-driven walk, crouch, poses); the animator gets the camera pitch so the
  spine/neck/head follow the aim — in the shadow and for everyone else.
- Look-down correction: above ~35° downward pitch the body slides back up to ~0.12 m
  so the chest stays behind the near plane; the spine also curls with pitch, which is
  what actually keeps the torso in frame ("look down, see yourself").

Why not separate FP arms: we have no authored arm meshes (everything is the
procedural NpcBody), the user's canon is already "the view is from that body's eyes,
so looking down you see yourself pedal", and one body means every animation written
for NPCs is automatically a player animation — requirement 5 of the brief.

Sources: [Godot issue #70556 (shadow casting ignores cull masks)](https://github.com/godotengine/godot/issues/70556),
[Godot Q&A on light cull masks and shadows](https://ask.godotengine.org/139894/how-stop-light-from-casting-shadows-objects-different-layers),
plus engine-community documentation of Bethesda's dual-rig setup (Joy of Perspective /
Improved Camera mod docs), Unreal's `bOwnerNoSee`, and the published Mirror's Edge /
Star Citizen first-person talks (GDC "Pushing the First-Person Perspective" line of
work).
