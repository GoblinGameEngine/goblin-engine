# Action animations: weapon holds, attacks, doors, water-to-boat climbs

Added 2026-10-16 evening (the user's additions to job 3). Reference notes gathered from
published animation analyses and GDC first-person animation talks; we recreate look and
timing by hand in our own clip format (npc_clips.json) — no animation data or assets
are taken from any game.

## 1. What the references say

**Attack phasing.** Game melee attacks split into anticipation (wind-up) → apex
(contact) → recoil/recovery. Player-character wind-ups are kept short to avoid input
lag, NPC wind-ups longer so players can react; too much recovery feels "sticky".
Heavier weapons get slower anticipation AND recovery, with the swing itself always
fast; holding the follow-through a beat adds weight. Hit-stop of 2–5 frames sells
impact. (Sources: [gameanim.com on attack balancing](https://www.gameanim.com/?p=115),
[Slynyrd Pixelblog 9: melee attacks](https://slynyrd.com/blog/2018/9/8/pixelblog-9-melee-attacks),
[Pixelblog 56: attack animation](https://www.slynyrd.com/blog/2025/5/23/pixelblog-56-top-down-character-attack-animation),
[wayline.io on indie melee combat](https://www.wayline.io/blog/level-up-indie-game-melee-combat).)

**First-person animation.** The arms, weapon and camera are the most persistent
motions in an FPS; responsiveness beats flourish, and the camera must stay stable
(motion-sick otherwise). The GDC line of talks —
[Destiny: The Art of First Person](https://gdcvault.com/play/1022297/The-Art-of-First-Person),
[Overwatch first-person animation](https://www.gameanim.com/2017/04/29/first-person-animation-overwatch),
[Ryan Duffin's Giving Purpose to First-Person Animation](https://gdcvault.com/play/1017633/Animation-Bootcamp-Giving-Purpose-to) —
all land on: animate the arms/weapon, never the aim; recoil as a quick out, slower
spring home (our WeaponBase.recoil already does 0.03 s out / 0.09 s back on the
view model — we keep that curve but move it into the hand).

**Climbing out of water onto a boat.** Sea of Thieves hangs ladders on ship sides and
the climb is grab → body up over the rail → settle on deck
([ladders wiki](https://seaofthieves.wiki.gg/wiki/Ladders)); our 20 km ring's boats are
small craft, so the reference is the gunwale haul: hands to the rail, a strong pull
with the trunk folding over the rail, one knee up, then rise — the same shape as our
mantle with a deeper fold and a slower, heavier tempo out of the water.

## 2. Our clips (authored in npc_clips.json, group "action" — shared with every NPC)

All at 24 "frames" nominal; `w` is the clip's blend envelope; hand targets are IK in
the chest/hips frames, so every body proportions itself.

| clip | length | phases |
|---|---|---|
| punch | 0.5 s | guard up 0.12 (tsume) → jab out 0.07 to full reach at shoulder line, fist, slight hip/chest twist → hold 0.05 → retract 0.26 (smooth) |
| bat_swing | 0.8 s | two-hand wind-up high over the right shoulder 0.2 (tsume, trunk twists back) → swing across to the low left 0.14 (the fast part) → follow-through held 0.1 → recover 0.36 |
| pistol_fire | 0.3 s | wrist and forearm kick up/back 0.06 → settle home 0.24; the head/eyes never move |
| door_reach | 0.55 s | right hand out to handle height (hips frame, forward) 0.22 → grip 0.1 → release and retract 0.23 |

Weapon HOLD poses are not clips (they persist): PlayerBody feeds NpcAnimator.ride
hand targets while a weapon is out — pistol: right hand raised ahead of the chest,
following the aim; bat: right hand low at the side, bat resting; fists: loose guard
only when recently used. A playing clip suppresses the hold so attacks read fully.

## 3. The weapon itself moves into the hand

Today each weapon is a view-model under Head/Camera3D/WeaponMount (WeaponBase;
data/weapons.json). The equipped weapon's visual now re-parents to a
BoneAttachment3D on the body's HandR bone with a per-weapon grip transform, so it is
in the hand in first person, third person, mirrors and shadows. Mechanics stay as
they are (camera muzzle ray, cooldowns, damage) — the brief's integration point.

## 4. Water-to-boat (and bank) climbs

While swimming, jump probes for a gunwale/deck/bank edge between roughly chest height
below and half a metre above the eyes, within 0.9 m ahead; a hit runs the normal
mantle curve (slower: 1.0 s, the heavy out-of-water pull) onto the verified deck
space. Same NpcRide.mantle pose with a deeper fold. Boats' decks and any dock or
river bank work alike — the probe only cares about a wall face with a standable top.
