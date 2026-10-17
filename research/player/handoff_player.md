# Handoff — player body + FPS movement (job 3)

Updated: 2026-10-16 evening. Headless selftest (26 asserts) ALL PASS; npc_clip_test
55 clips x 12 bodies 0 failures; in-game M7 partially done (look-down + third-person
+ shadow-layer verified before the evening additions; re-verify after them).

## FINAL STATE (end of session): everything below implemented AND verified
- Headless: player_move_test 26 asserts ALL PASS; npc_clip_test 55 clips x 12 bodies
  0 failures; npc_corner_test 0 failures. `--import` run (new .uid files exist).
- In game (screenshots in research/player/img/): fp_pistol.png + fp_pistol_down.png
  (own arm holding the pistol along the aim), fp_punch.png (fist in view mid-jab),
  fp_lookdown_final.png (legs/chest/feet, dark collar, no head interior),
  weapon_hold_3p.png / bat_hold_3p.png (held weapons in third person),
  npc_punch/npc_bat_swing/npc_door_reach/npc_crouch/npc_jump_tuck/npc_land.png
  (the SAME clips/poses previewed in third person on a separate NPC body),
  ingame_thirdperson.png (whole person incl. head = the layer trick proven).
- WEAPON_GRIP rotations were SOLVED ANALYTICALLY in the live game against the prop
  bone's actual frame (see the method in "In-game verification notes"), then baked.
- WeaponManager.equip/unequip now also free _current_weapon wherever it lives (it
  moves into the hand, so freeing only WeaponMount's children leaked the old one).
- README controls table updated (crouch C toggle / pad B, lean Q/R, climb rows).
- M8 clipping/manifold pass: SCOPED (see below) — movement-critical items done by
  design and test; the project-wide fix campaign remains queued with baselines.

## M8 scope + state (the ship-blocker pass)
- Movement-critical, done & verified: camera near 0.03 < capsule r 0.18 margin;
  mantle/hang/swim-mantle destinations verified with capsule intersect_shape before
  the move; step-up only via test_move; stand-up ceiling check; lean shape-capped;
  look-down pull-back 0.30; the open-neck torso is sealed by the dark collar funnel
  (two coincident boundary rings, intentionally non-manifold, hidden inside).
- Tools are in place and healthy (spot-run 2026-10-16): tools/buildings/
  check_models.py (manifold/winding/zfight/degenerate; full-world report
  reference/tmp/model_check.json of 2026-10-13: 8,340 buildings — nonmanifold
  117,007 edges in 7,822 buildings, open_solid 5,633, flipped 94 in 17, inside_out
  24 in 3, zfight 28,769 visible) and tools/sky/warren/audit (100-island
  reference/tmp/audit/all_final.json: intrusion/pierce 249,780, zfight/coplanar
  168,892, manifold/kit_piece 791, walk 47,350/47,357 doors ok).
- REMAINING (the actual fix campaign — a job of its own): drive the counts down at
  the GENERATORS (remake/blender builders, the warren kit) category by category,
  re-running the two audits as the gate; start with the small-high-impact sets
  (flipped 94, inside_out 24, walk blockers 7+9) then the big cosmetic classes.

## EVENING ADDITIONS (user, via coordinator) — all implemented and verified above
1. Weapon held in the hand (FP+3P): equipped weapon visual reparents from the camera
   WeaponMount to a BoneAttachment3D on PropR (NpcProps frame: handle along +z);
   WEAPON_GRIP transforms in player_body.gd; fists show no mesh (the body has hands).
   Hold poses (pistol raised following aim, bat carried low) via animator.ride;
   suppressed while an action clip plays. Grip transforms tuned and baked.
2. Action clips in npc_clips.json group "action" (SHARED with NPCs): punch (0.5 s),
   bat_swing (0.8 s), pistol_fire (0.3 s recoil), door_reach (0.55 s). Wired:
   WeaponManager.try_use_equipped -> player.on_weapon_used -> body.weapon_used;
   _try_interact on a RemakeDoor -> body.reach. Timing per
   research/player/03_action_animations.md (reference research inside).
3. REAL jump animation (user emphasis): phased in NpcAnimator — push-off extension
   (legs straight, toes hard, arms swing back, 0.16 s), tuck (lead knee up, arms out),
   reach into the fall, land() knee pulse (0.3 s) recovering into the walk. Driven by
   air/air_v (any NPC can set them); landing via StationPlayer._land_dip -> body.landed.
4. Crouch is a TOGGLE on C (press again to stand), pad B; Ctrl stays swim_down only.
   project.godot updated. README controls table still to update.
5. Water-to-boat climb: jump while swimming probes a gunwale/dock/bank edge
   (eye-0.9..eye+0.5, reach 0.9) -> 1.0 s heavy mantle onto the verified deck
   (_try_swim_mantle). Tested headless with a mock Area3D water + deck box.
6. QUALITY BAR (user): all these animations must read well in third person on NPCs.
   The rig is literally shared (one generator; clips are proportion-relative), so no
   retarget exists; VISUAL 3P verification on an NPC body still to do in game.
Working tree had NO other changes at job start (v0.8.2-beta.2, commit 31e2c9b24).
DO NOT COMMIT — the coordinator commits after verification.

## State

- [x] Research + design docs: research/player/00_plan.md, 01_first_person_body.md,
      02_movement_reference.md.
- [x] M1: head split (NpcCharacter.prepare(..., split_head) -> HeadM/HeadWear meshes
      on HEAD_LAYER 1<<11, one shared skin material for the face) + PlayerBody node
      (remake/characters/player_body.gd) + camera cull mask & near 0.03; the bicycle
      rider now uses the split instead of collapsing the Neck (shadow has a head).
- [x] M2: crouch (capsule 1.45->0.95, eye 1.43->0.92, tap=toggle/hold=hold on
      Ctrl/C/pad B, ceiling-blocked stand-up) + step-up 0.36 with eye smoothing.
- [x] M3: slide (sprint+crouch, boost->decay, slope gravity, slide hop) and lean
      (Q/R, 0.30 m + 10°, wall-capped). Landing dip on hard landings.
- [x] M4: mantle ≤1.35 grounded / ≤1.0 airborne, vault ≤0.55 keeping speed (eased
      up-then-over curve), ledge hang (falling + jump/forward held), shimmy A/D 0.7
      m/s with edge revalidation, climb (W/jump), drop (S/crouch). All radial-up safe.
- [x] M5: animator: NpcAnimator.crouch (hips sink, lean, wide base, short quick
      stride via leg IK), aim_pitch spread over spine/chest/neck/head; NpcRide
      gained slide()/hang()/mantle() pose builders — same set for every NPC human.
- [x] M6: remake/tools/player_move_test.gd — 21 assertions, ALL PASS
      (split counts/layers/material, body build+scale+cull, walk, sprint, step-up,
      crouch enter/blocked/stand, slide start/boost/end, vault, mantle, hang
      catch/climb/drop, lean). Run:
      ../godot/godot4 --headless --path . --script res://remake/tools/player_move_test.gd
      Also npc_corner_test (300): 516 built, 0 failures.
- [x] M7 (see FINAL STATE above for the complete list): in-game verified: body built in game, camera culls HEAD_LAYER,
      look-down shows chest/legs/feet with the dark collar (0.30 pull-back past 35°),
      third person shows the whole person incl. head/hair/face (layer trick proven),
      ankle 0.068 above ground (feet planted). Screenshots in research/player/img/.
      Later the same evening: weapon-in-hand FP+3P, action clips in 3P on an NPC
      body, crouch/jump-tuck 3P — all done (FINAL STATE). Water-boat verified on a
      test gunwale headless; a live-boat check would be a nice extra.
- [x] M8: scoped (see "M8 scope + state" above): movement-critical done; the
      project-wide generator-level fix campaign queued with baselines and commands.
- [x] README controls table updated (C crouch toggle, Q/R lean, climb rows, pad B).

## In-game verification notes (how)
- Launch: cd godot_project && nohup ../godot/godot4 --path . remake/scenes/RemakeStation.tscn
  (lock protocol; wait for "LOAD complete" in the log, wait-ready is only the bridge).
- DaySkySystem: st.find_child('DaySkySystem', true, false).time_of_day = 0.5 (no _clock).
- The sun is ALWAYS radially overhead -> shadows pool under the feet; shadow-with-head
  needs a 3P camera looking at the ground under the player, not a long morning shadow.
- 3P camera: add Camera3D under the player, position + look_at, current = true.
- The game process reloads scripts only on restart; tune live via node fields
  (e.g. body.npc.position.z) then write the value into the script and restart.

## Files touched so far

- godot_project/remake/characters/npc_character.gd (split_head path, HEAD_LAYER)
- godot_project/remake/characters/npc_animator.gd (crouch, aim_pitch)
- godot_project/remake/characters/npc_ride.gd (slide/hang/mantle pose builders)
- godot_project/remake/characters/player_body.gd (NEW)
- godot_project/scripts/StationPlayer.gd (movement block before _physics_process,
  integration inside it, lean/eye in _process, crouch input, _clear_moves)
- godot_project/scripts/autoload/Controls.gd (pad B -> crouch)
- godot_project/project.godot ([input] crouch/lean_left/lean_right)
- godot_project/remake/scripts/vehicles/bicycle.gd (split head rider, _headless gone)
- godot_project/remake/tools/player_move_test.gd (NEW selftest)

## Gotchas found

- New class_names aren't in .godot's global class cache for --script runs: use
  preload for new scripts (StationPlayer preloads player_body.gd).
- Autoloads come up AFTER a SceneTree script's _init: await process_frame first.
- Input.action_press doesn't reach _unhandled_input; synthesize InputEventAction
  via Input.parse_input_event in tests.
- WeaponManager._build_hit_marker errors once headless (pre-existing: no HUD canvas).
- Holding forward at a hang auto-climbs (by design: Dying Light style).

## The chosen approach (detail in 01_first_person_body.md)

True first-person body: the SAME generated person the bicycle seats (seed =
NpcLife.seed, pid "player"), with head+neck split into separate MeshInstance3Ds on
render layer bit 1<<11 (HEAD_LAYER); the player camera's cull_mask clears that bit —
invisible to the player, still in every shadow map (Godot shadows ignore camera cull
masks) and visible to every other camera. Controller stays authoritative; the body is
glued under the capsule and posed by NpcAnimator. Look-down pulls the body back
≤0.12 m past 35° so the chest never crosses the near plane.

## Facts the next session needs

- Player: godot_project/scenes/StationPlayer.tscn + scripts/StationPlayer.gd.
  ORIGIN AT THE EYES; capsule r 0.18 h 1.45 at CollisionShape3D y −0.705 (feet at
  −1.43). Radial up: basis.y, up_direction set per tick; never use world Y.
- NPC body: remake/characters/npc_character.gd builds Body+Clothes MeshInstance3Ds
  from NpcBody parts (named "head", "neck", ...); npc_animator.gd is the shared
  animator (ride{} override mechanism = the pose-override hook to reuse).
- The bicycle (remake/scripts/vehicles/bicycle.gd) collapses the Neck bone
  (_headless()) — replace with the split so the rider's shadow has a head.
- Input: "swim_down" is already Ctrl; new actions crouch/lean_left/lean_right go in
  godot_project/project.godot [input].
- Vehicles use INTERIOR_LAYER = 1<<9 (vehicle_body.gd); 1<<11 is free (grep showed
  no other render-layer users).
- Tests: corner test after body changes (remake/tools/npc_corner_test.gd); lineup
  tool needs a display. Game lock: reference/tmp/game.lock (verify PID is the one
  godot4 whose /proc/<pid>/cwd is godot_project). free -g before launching anything
  heavy (14 GB machine).

## Remaining / open

Everything M1–M8. No fixes landed yet.
