# Weapon holds and attacks, redone from video reference (2026-10-23)

The user (2026-10-23): "The player holds the gun, the bat and his fists all wrong. Fix them. Find reference
videos and use them to make the animations better."

## What was wrong (0.8.3)

- **Pistol:** one hand, gripped low on a 35 cm box "barrel", pointing up-left like a flashlight. The hand
  override placed the wrist by IK but left the wrist straight, so the gun hung off whatever angle the forearm
  had (a grip transform "solved" for one pose).
- **Bat:** carried hanging at the side in one hand; in third person it floated beside the body.
- **Fists:** one fist low in a corner, no guard.

## Reference videos (frames studied locally: reference/video_refs/weapons, gitignored; index.tsv lists them)

| clip | what we took |
|---|---|
| [Fallout 4 10mm anims by CADAVVER](https://www.youtube.com/watch?v=rYJkp87DP9g), [10mm mod review](https://www.youtube.com/watch?v=87-XNNKLYhw) | pistol upright and right of centre so the slide shows its side; the barrel parallel to the view; a short sharp kick and a slower settle |
| [Dying Light baseball bat challenge](https://www.youtube.com/watch?v=Ed78Tbz9HXE), [Dying Light super melee](https://www.youtube.com/watch?v=hIoSC5AqCNw) | bat held low on the right, angled up past the shoulder; the swing whips flat right-to-left across the whole view in ~0.1 s, then recovers |
| [Fallout 4 baseball bat](https://www.youtube.com/watch?v=VEG1kEpn2OQ), [kill](https://www.youtube.com/watch?v=D90ZH7x8YjA) | the idle bat upright on the right edge of view, two hands on the handle |
| [SIGMA unarmed animations (Skyrim)](https://www.youtube.com/watch?v=sUkopJ4XTc0), [Skyrim fists](https://www.youtube.com/watch?v=WI68mRBpa4A) | the guard: both fists low-centre, knuckles forward; jab and cross alternate, each out in ~2 frames at 6 fps (~0.08-0.1 s) to the centre line and back in ~0.25 s; the idle fist tucks to the chin |
| [Dying Light fist combat](https://www.youtube.com/watch?v=p9lmk1IKl6Q), [fist to fist](https://www.youtube.com/watch?v=TGuktuxQnW0) | punches enter from the lower edges; the fist turns over as it lands |
| [DayZ two-handed idles](https://www.youtube.com/watch?v=AD1ADV3Bavc), [AK showcase](https://www.youtube.com/watch?v=_DJctOK6K3M) | idle breathing and sway: tiny, slow; the weapon lags a fast turn and springs back |

We recreate the look and timing by hand; no animation data or assets are taken from any game.

## The design

- **The weapon is the master, the hands follow** (how full-body FPS rigs do it). `NpcWeaponPose`
  (remake/characters/npc_weapon_pose.gd) keys the weapon's transform in the AIM frame (eyes, -Z forward) and
  gives each hand a wrist target plus a facing (fingers and palm directions). The player passes its camera;
  an NPC can pass its head frame and get the same hold.
- **NpcAnimator.ride** gained `aimL`/`aimR` ([fingers, palm] in skeleton space -- the hand bone's rotation is
  solved against the forearm the IK produced; `hand_basis()`) and per-arm `poleL`/`poleR` elbow directions.
- **Weapon models** are real-size with the grip at the origin: a 1911-sized pistol (barrel -Z, 18 deg raked
  grip) and an 84 cm bat (handle between the hands, the bat along +Y, taped handle).
- `WeaponBase.held_by_body` turns off the old view-model tweens (recoil, swing) once the body holds the weapon.
- PlayerBody sets the hold every frame (the animator poses after it, same frame), plus a little sway when you
  turn. Fists show the guard while fighting (4 s after a punch), otherwise the arms swing with the walk.

| weapon | hold | attack |
|---|---|---|
| pistol | two-handed, aim frame (0.15, -0.165, -0.42); barrel converges on the crosshair at 40 m; the left hand wraps the grip's left side | 0.26 s: 14 deg kick up and 4.5 cm back in 0.035 s, eased settle |
| bat | both hands low right, bat up past the right shoulder | 0.8 s: cock back 0.17, come through on the right 0.21, contact centre 0.25, whip left 0.32, follow-through held to 0.44, recover to 0.8 |
| fists | guard: fists at (+-0.13, -0.235, -0.27), knuckles up and forward, palms in | 0.5 s: alternate jab/cross, out 0.08, held to 0.13, home by 0.42; the other fist tucks to the chin |

Screenshots: research/player/img/fp_pistol_two_hand.jpg, pistol_two_hand_side.jpg, fp_bat_swing_sheet.jpg,
bat_swing_3p_sheet.jpg, fp_fists_guard.jpg, fists_guard_3p.jpg, punch_side.jpg.

## Open

- NPCs don't fight yet; when they do, call `NpcWeaponPose.pose(id, t, side, head_to_skel)` for their ride.
  The old authored clips (punch, bat_swing, pistol_fire in npc_clips.json) are still there for them.
- A trigger finger (index straight along the frame) needs per-finger grip curls in the ride.
- Hit timing still applies on the click; moving melee damage to the contact key (bat 0.25 s, punch 0.08 s)
  would match the animation.
