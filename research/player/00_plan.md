# Player body + modern FPS movement — design & build plan (job 3, 2026-10-16)

The brief: the player gets the generated body (the bicycle rider person) with head and
neck back; modern FPS movement (crouch, slide, step-up, mantle/vault, ledge
hang/shimmy/climb, lean) with smooth expressive animations; the same animation set
drives all NPC humans; plus a scoped project-wide clipping / manifold-normals pass.

Research: 01_first_person_body.md (the chosen approach and why),
02_movement_reference.md (numbers). Status lives in handoff_player.md.

## A. The body (true first-person, layer-masked head)

1. `NpcCharacter.prepare(v, id, seed, occasion, split_head := false)`:
   when split, body arrays exclude the "head"+"neck" parts, which go to `d.head`
   (same material/skeleton); clothes surfaces whose garment slot is "head", plus the
   hair surface, are marked head-side.
2. `_assemble` builds `head_mesh` ("HeadM") and head-side clothes ("HeadWear") as
   extra MeshInstance3Ds on the same skeleton/skin, `layers = HEAD_LAYER (1 << 11)`.
3. `PlayerBody` (remake/characters/player_body.gd, Node3D under StationPlayer):
   - builds the same person as RemakeBicycle.take_seat (NpcTraits.person(seed,
     "player", ["L0","L1"], "", {age:30}), seed = NpcLife seed) with split_head,
     prepared on a worker thread at spawn;
   - camera cull_mask &= ~HEAD_LAYER;
   - every frame: feet glued to the capsule bottom, yaw = the controller's yaw,
     animator.speed = horizontal speed, aim pitch → spine curl + neck/head
     (shadow aims with you), crouch factor, slide/hang/mantle poses, lean roll;
   - look-down pull-back: above ~35° down the body slides back ≤ 0.12 m;
   - hidden while seated in a vehicle (the vehicle seats its own rider body, as the
     bicycle already does).
4. The bicycle's `_headless()` collapse is replaced: its rider is built with
   split_head and the same HEAD_LAYER, so the rider too keeps a head for its shadow.

## B. Movement (StationPlayer + player_parkour.gd)

All in the body's own frame (basis.y is the radial up — never world Y).
- **Crouch**: capsule 1.45→0.95, eye −0.51, 0.22 s smoothstep; hold "crouch" (Ctrl)
  or toggle (C; pad B); stand blocked by ceiling check. Speed 2.1.
- **Step-up**: 0.36 m, the test walker's try-raised-move port, with eye smoothing.
- **Slide**: sprint + crouch on the ground → boost, decay, weak steering, slope
  acceleration, ends slow/jump/stand. Slide uses the crouched capsule.
- **Mantle/vault**: jump at a face → ledge probe (blocked at chest, clear above,
  down-ray finds top, headroom check) → timed curve carries the capsule up and over
  (collision off during the curve, verified destination). Vault keeps speed.
- **Ledge hang**: falling past a valid edge within hand reach latches HANG (gravity
  off, body flush); A/D shimmy 0.7 m/s with continuous edge revalidation; W/jump
  climbs (mantle curve), S/crouch drops.
- **Lean**: Q/R, eye offset 0.30 m + 10° roll, spring-smoothed, shape-cast capped.
- New input actions: crouch (Ctrl, C, pad B), lean_left (Q), lean_right (R).

## C. Animations (NpcAnimator — shared with every NPC)

- `crouch` 0..1: hips drop ~0.26·T and shift back, forward lean, wider base, shorter
  stride; legs bend via the existing IK (no new clips needed), arms ride lower.
- `aim_pitch`: distributes camera pitch over spine/chest/neck/head (player; NPCs can
  aim too).
- `pose` overrides (the ride mechanism generalised): slide (low hips aft, legs
  forward, trailing hand down), hang (arms up to the edge targets, body straight,
  feet to the wall), mantle phases keyed by the parkour curve.
- Lean: trunk roll stays procedural from the controller's lean value.

## D. Verification

- Headless: `remake/tools/player_move_test.gd` — a flat floor + stair + low slab +
  1.2 m wall + 0.5 m vault box + a drop-edge built at the ring wall, inputs via
  Input.action_press, asserts each mechanic's outcome (heights reached, capsule
  sizes, states). Run after every change. `npc_corner_test` after any body change.
- In game via DevBridge (lock protocol, free -g first): spawn checks, screenshots of
  the look-down body, the shadow with a head, a mantle and a hang; third-person
  camera screenshot to prove the full body.

## D2. Evening additions (user, 2026-10-16; research in 03_action_animations.md)

- The equipped weapon is held IN THE HAND (PropR bone attachment, per-weapon grip
  transforms), first and third person alike; hold poses via animator.ride; the old
  camera view-model mount stays only as the mechanical parent before the body exists.
- Action clips, authored in npc_clips.json (group "action", shared with all NPCs):
  punch, bat_swing, pistol_fire, door_reach; played via WeaponManager -> body, and
  on door interacts.
- A REAL jump animation: push-off extension -> tuck (lead knee) -> reach into the
  fall -> land() knee pulse; crouch enter/exit/move are animated through the crouch
  factor (hips/lean/stride/base through the leg IK).
- Crouch binds to C as a TOGGLE (pad B); Ctrl remains swim-down.
- Water-to-boat: jump while swimming = the gunwale haul (a 1.0 s mantle) onto any
  boat deck, dock or bank the probe verifies.
- Quality bar: every animation must read well in third person on NPC bodies (the rig
  is shared by construction; verify visually on an NPC, not just the player).

## E. Clipping / manifold ship-blocker pass (scoped)

Movement-critical first: camera near-plane vs capsule (guaranteed by r 0.18 >
near 0.03 + margin), body-into-world during mantle/hang (destination verified with
shape tests before the curve runs), step/stair penetration (step-up uses test_move
only). Project-wide: run tools/sky/warren/audit and tools/buildings/check_models.py
over the current assets; extend check_models.py with non-manifold-edge and
inverted-normal checks if absent; fix what they flag or list the remainder in the
handoff with counts.
