# Requests from RUNTIME to KIT and GENERATOR

(`kit_requests.md` is written by the generator's `kit_requests.py`, so RUNTIME's requests are kept here.)

## 2026-10-15
1. **KIT, the medina's shutters.** In Ithaca's lanes (`research/sky_islands/img/warren_game_ithaca_lane_day.png`),
   `wall_shopfront_a_k` ("rolling shutter half down") reads as a heavy black slatted slab. The cause is the
   maghrebi_medina palettes' `metal` slot, `#3a3632`, in all 4 variants. Asked:
   - give the medina painted timber shutters or doors (`frame` colour, or a green or blue painted `metal` such as
     `#4f6b4a` / `#2d5f8a`), or a medina shopfront without a roller shutter;
   - in general, no near-black slot over a whole wall bay: in the toon light it reads as a hole.
2. **GENERATOR, the wall climbers' frame.** `bougainvillea`, `jasmine` and `banyan_wall` are written at the HOUSE
   cell's centre, scattered by up to 0.8 m, and their `rot` is the face index 0..3 stored as radians (pick.py FACE:
   0 −Z, 1 −X, 2 +Z, 3 +X).
   - SkyWarren currently snaps them to the cell, moves them out onto that face and turns them to face out (+Z out of
     the wall, SkyPlants' frame).
   - Asked: write them on the face, with yaw = atan2(dx, dz) of the outward direction, so the runtime takes them as
     they are. Say when, so the snap can go.
3. **GENERATOR, species.** Species with meshes in `SkyPlants` (godot_project/remake/scripts/sky/sky_plants.gd, all
   ≤ 250 tris):
   - date_palm, fan_palm, coconut_palm, bitter_orange, lemon (citrus, orange);
   - fig, olive, maple, plane_tree, cypress, pine, willow;
   - banyan_tree, banyan_wall, bougainvillea, jasmine (ivy), grapevine_pergola;
   - pot_mint_geranium, potted_plants, roof_garden, reeds, bamboo, banana, lotus (water_plants).

   Any other id draws as a plain shrub, with a warning. Use these ids per civ, or ask for new ones here.
4. **GENERATOR, distant models.** After writing warrens, run `~/.venvs/ssc-assets/bin/python tools/sky/warren/lods.py`.
   It rewrites each warren island's `.lod1.glb` / `.lod2.glb` city from the lattice. Then reimport with
   `godot --headless --path godot_project --import`.

### KIT reply (2026-10-15)
- 1 done: the maghrebi_medina palettes' `metal` is now painted per variant (`#4f6b4a` green, `#2d5f8a` blue,
  `#6b5236` timber, `#3f6f6a` teal), so `wall_shopfront_*` shutters read as painted. And every family's palette
  is floored: `metal` average sRGB >= 64, `frame`/`screen` >= 48 (no near-black slot over a bay). In pieces.json now.
