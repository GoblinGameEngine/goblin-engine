# Warren flicker: causes, fixes, evidence (RUNTIME, 2026-10-15)

## Method
`reference/tmp/flick.sh` holds a camera fixed in an island's frame and screenshots two consecutive frames, then diffs
them. It reports the share of pixels changing by more than 40/255, and the share changing inside areas that are flat
in the first frame. A change inside a flat area is depth fighting or crawling shading, not an edge or silhouette
moving.
- **Views:** on SKY-099, a plaza, a lane, the roofs, and the city from 100 and 150 m; day and night.
- **Island moving:** the island drifts at about 5.5 m/s with the camera riding it.
- **Island frozen:** the island stopped, and the camera nudged 1–2 cm between the two frames.
- **Animated content:** plants, grass, flares, signs and islanders are hidden in some runs so that they don't count.

## Causes found
1. **Placeholder boxes.** A race in SkyWarren's kit loading: the "loaded" flag was set before the kit was in. With
   100 warrens, several islands prepare at once at start-up, and some got every piece as a placeholder box:
   `SkyWarren.missing` held 55 ids on SKY-099, and LOD0 dropped from 1.04 M to 0.31 M triangles.
   - Those boxes overlap coplanar everywhere, including lamp boxes.
   - Moving island, roofs at night: 1,433 flat pixels changed per frame with placeholders, against 0–4 with the kit.
   - **Fixed:** `_ensure_kit()` is double-checked and sets the flag after loading; `_piece()` waits for the kit.
     `missing` is now 0.
2. **Shadow crawl.** Aboard, the camera always moves with the island, so the sun's cascades re-snap and every shadow
   edge crawls.
   - Same view, consecutive frames: 0.06 % (and 0.014 %) of pixels changed with shadows, against 0.001 % (and
     0.004 %) without. With the shadow blurred (`shadow_blur` 2.5): 0.001 %. With 4 splits: 0.003 %.
   - **Fixed:** SkyIslands softens the sun's shadows while the player is aboard (`_sun_soft`) and restores them on
     leaving.
3. **Dithered LOD cross-fade.** `VISIBILITY_RANGE_FADE_SELF`, which I had just added, is drawn as a per-pixel
   stipple. The screen outline pass reads that as a band of false edges at each switch distance; the same defect
   is recorded in `scripts/world/DistanceCulling.gd`.
   - **Fixed:** the ranges are hard and exclusive (LOD0 < 45 m, MID < 200 m, boxes < 520 m). The MID pieces keep
     the switch quiet.
4. **Coplanar faces of different colours inside kit pieces.** 138 of 402 pieces have overlapping faces within 4 mm:
   trim on accent, wall on tile, frame on emissive, and so on. The full list is in `kit_coplanar_faces.txt`, from
   `tools/sky/warren/check/coplanar.py`.
   - **Runtime mitigation:** each overlay slot is lifted off along its normals by a few mm, in a fixed order (wall
     0 < trim 3 < tile and glass 6 < frame, screen, metal and fabric 9 < accent 12 < accent2 15 < emissive 18 mm),
     so the overlay meant to be in front always wins. This is `SkyWarren.SLOT_LIFT`.
   - **KIT:** offset coplanar overlays by at least 5 mm, or cut the face under them.
   - **KIT:** fix the same-slot overlaps (tower_mudejar_belfry 12 m², bell_tower_baroque_belfry, roof_*_end,
     badgir_*, roof_ring_tile, ov_sign_arm_big and others) and the 3-face fight on wall_talar_k's mid.
5. **The island's deck against the graded paving.** About 30 % of paved cells lie within 2 cm of the island's own
   deck mesh somewhere, and the deck pokes through the paving in about 20 % (`tools/sky/warren/check/deck.py`:
   SKY-099 258 and 176 of 871, SKY-071 495 and 295 of 2,024, SKY-078 482 and 250 of 1,354).
   - **Fixed:** the deck's drawn mesh and its collision are tucked 10 cm under the lowest paving within 2.2 m
     (`_tuck_deck`: 864 drawn vertices and 4,556 collision vertices moved on SKY-099).
6. **Duplicate placements** of the same piece in the same cell at the same height:
   - SKY-071: 149 (int_counter, int_floor, int_ceiling, int_shelves, bridge_plank);
   - SKY-078: 55;
   - SKY-099: 5 (pave_lane_skirt with sabat_beams, int_ceiling with roof_terrace).

   Identical faces fight when their palette variants differ (`tools/sky/warren/check/placed.py`).
   **GENERATOR:** de-duplicate.

## Not a cause
- **Depth precision:** reverse-Z, near 0.05 m. With everything animated hidden and the island moving, the island's own
  geometry changes in 0–0.0009 % of flat pixels a frame (plaza, lane, roofs, 100 m).
- **TAA/FSR:** off. MSAA 2x and 4x made no difference to the ground shimmer and cost 10–40 fps.

## Left over
The station floor seen from an island (far-side images and Calder's roads and blocks) shimmers as the island drifts
over it: 0.4–1 % of pixels a frame at 100–150 m. That is the floor really moving under thin, high-contrast detail
(roads one pixel wide) with no anti-aliasing. It belongs to the far-side and terrain owners: mip bias, or wider roads
in the far-side bake.
