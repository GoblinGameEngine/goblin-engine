# Station River Loop — Design Notes (Synthesis)

This file pulls the research in `meander_geometry.md`, `lakes_and_ponds.md`, `farm_drainage.md`, and `town_water_siting.md` into concrete numbers for the generator. Everything under **"Closed-loop adaptation"** below is **my own engineering proposal**, not a cited real-world fact — there is no real precedent for a meandering river forced into an exact closed loop, since real rivers exist on open, non-repeating terrain. Everything else summarizes cited research.

Station geometry recap: ring circumference **C = 3142 m**, floor width **1000 m** (so ±500 m from the midline to each zone edge), four zones (Lake, Downtown, Residential, Farm) in sequence around the loop.

---

## 1. River channel — recommended baseline numbers

- **Channel width: 45 m** (range 40–55 m is fine). This sits in the real Wabash River mid-reach class (61–122 m at Huntington/Covington, IN) scaled slightly down to leave more floor room, and is comfortably "needs a real bridge" scale — well above a creek (real creeks run 2–6 m), well below the mile-wide Illinois-at-Peoria-Lake scale (which is reserved for the lake feature, not the channel).
- **Meander wavelength: use the cited 10–14× channel-width ratio** → for 45 m width, λ = 450–630 m. This directly drives the closed-loop harmonic choice below.
- **Bend radius of curvature: 90–135 m** (2–3× channel width, per the cited ratio) — use this as the minimum turn radius when generating the spline/mesh through each bend apex, so bends don't read as unnaturally sharp kinks.
- **Depth:** not requested for rendering, but if needed for gameplay (wading/boat logic), treat as roughly W/15–W/20 (consistent with the cited Wabash-at-Terre-Haute width:depth relationship) → ~2–3 m typical channel depth, deeper in the lake.

## 2. Closed-loop adaptation (my proposal)

**The core trick: build the river centerline as a short Fourier series in the loop's angular coordinate, not as an open curve forced to stitch at a seam.**

Let θ run 0 → 2π once around the ring (arc length s = θ·C/2π, C = 3142 m). Let y(θ) be the river centerline's offset from the floor midline (y=0), measured across the 1000 m floor width (valid range roughly −500 to +500 m).

Any sum of terms `A_k · sin(k·θ + φ_k)` with **integer k** is *exactly* periodic over one full loop — sin(k·(θ+2π)) = sin(kθ) identically. That means a curve built this way closes seamlessly by construction, with zero manual stitching, gap-filling, or blending needed at the "seam." This is the single most important practical recommendation in this file.

**Recommended harmonic stack:**

```
y(θ) = A1(θ)·sin(6θ + φ1)          -- primary meander bends
     + A2·sin(13θ + φ2)            -- secondary wiggle / bank irregularity
     + A3·sin(θ + φ3)              -- slow whole-loop drift (large-scale asymmetry)

where A1(θ) = A1_base · (1 + 0.3·sin(2θ + φ4))   -- makes the 6 main bends unequal in size
```

- **k=6 (primary harmonic)** → wavelength λ = C/6 = **523.7 m**, which lands right in the middle of the cited 450–630 m target range for a 45 m channel (523.7/45 ≈ **11.6×** channel width — squarely inside the real 10–14× band). This gives **6 full meander wavelengths around the loop = 12 individual bend apexes** (6 swinging left, 6 swinging right, alternating) — a believable bend count for a ~3.1 km river.
- **k=13 secondary harmonic**, amplitude ≈30% of A1, adds the kind of smaller-scale bank irregularity real rivers have (natural meander trains are never a perfect single sine wave — the cited Wabash Basin planform studies and general fluvial literature both note real meander trains are irregular in wavelength/amplitude, which is exactly what stacking a second, non-harmonically-related integer frequency simulates).
- **k=1 slow drift term**, small amplitude (~20–30 m), breaks perfect 6-fold rotational symmetry so the six main bends don't all look identical/evenly spaced when viewed as a whole ring — e.g. it can be tuned so bends are visibly larger/lazier near the Lake zone and tighter near Downtown.
- **Amplitude-modulating the primary term** (the `(1 + 0.3·sin(2θ...))` envelope) is what kills the "obviously a perfect wave" look — it makes alternating bends different sizes, still exactly periodic since it's a product of periodic terms.

**Recommended amplitude budget:**

- A1_base ≈ **150 m** (so bends swing up to ~150–195 m off centerline with the envelope applied)
- A2 ≈ **45 m**
- A3 ≈ **25 m**
- **Cap the combined worst-case excursion (A1+A2+A3 ≈ 220 m) so it never exceeds ~250 m off midline.** With a 500 m half-floor-width, that guarantees at least ~250 m of clearance from the river's outermost swing to the zone edge at every point around the loop — enough room for the meander belt itself (see below) plus a building/road buffer.
- This gives an effective **meander belt width of roughly 8× channel width (≈360 m)** — deliberately compressed from the real 15–18× (or even the more conservative Williams-formula ~6×) ratio, because a full-realism belt width (675–810 m) would eat almost the entire 1000 m floor and leave no room for the four distinct zones to read separately. **This compression is a conscious realism-vs-gameplay trade-off, not an oversight** — flag it as such if a reviewer asks "why isn't this using the textbook 15–18× ratio."

**Bend count sanity check:** "given a channel width of 45 m and a meander wavelength of ~11.6× channel width (524 m), a 3,142 m loop fits almost exactly 6 meander wavelengths, i.e. 12 individual bend apexes around the full circumference." If a wider/narrower channel is chosen later, keep λ ≈ 10–14× the new width and pick the nearest integer k = C/λ so the loop still closes exactly — e.g. a 30 m channel (λ≈300–420m) would use k≈8–10 (10–13 wavelengths / 20–26 bend apexes), a 60 m channel (λ≈600–840m) would use k≈4–5 (8–10 bend apexes).

## 3. The lake

Site the one large lake within (or straddling the boundary of) the **Lake zone**, timed to coincide with a stretch where the primary harmonic bends are at their widest (i.e. near a peak of the A1 envelope) — this echoes how real river-widening lakes (Peoria Lake on the Illinois River) sit at a naturally broad point rather than an arbitrary spot.

- **Length: ~1,000 m** (roughly 1.5–2× the primary meander wavelength — i.e. the lake should visually swallow one to one-and-a-half bend cycles, similar to how Peoria Lake spans several km of what would otherwise be ordinary river).
- **Width: ~300 m** → **length:width ≈ 3.3:1**, inside the cited real range of 2:1–5:1 (Palgrave Pond 2.1:1, Arlington Mill Reservoir 4.3:1, Powder Mill Pond 5.2:1).
- **Inlet/outlet necking:** shoreline should pinch back down to channel width (45 m) over roughly **100–150 m** at both the upstream and downstream ends, so the river-to-lake and lake-to-river transitions read clearly rather than blending ambiguously.
- **Shape:** irregular, embayed shoreline (not a clean ellipse) with a subtly deeper trace running along the old channel line down the long axis — cheap to fake by keeping the deepest-water spline following the original centerline curve through the lake polygon.
- Because the lake sits inside the amplitude budget above, it doesn't need extra floor-width allowance beyond the ~250 m clearance already reserved.

## 4. The ponds

- **Count: 5–7 ponds** distributed around the rest of the loop (outside the lake reach), biased toward the Residential and Farm zones' floodplain-like low ground, with maybe one styled as a near-downtown oxbow remnant for variety.
- **Placement cadence:** roughly **one pond every 1–2 primary meander wavelengths (~500–1,000 m of river length)** — this deliberately echoes the primary bend spacing (real floodplain ponds/oxbows cluster near bend sequences), rather than being scattered independent of the river's rhythm.
- **Pond size:** **60–150 m** long axis, oval-to-crescent shaped. Style roughly half as crescent "oxbow remnants" hugging a bend's outer edge (no real tributary needed, or a very short stub connection) and half as rounder, tributary-fed ponds sitting further back in the floodplain.
- **Tributary creek connecting pond to river:** **4–10 m wide** (scaled up slightly from the cited real 1.8–6 m small-creek reference for map-scale visibility), **60–300 m long**, gently curved (a much smaller-amplitude echo of the main river's meander style keeps the visual language consistent).

## 5. Farm zone drainage

Real tile spacing (9–30 m) and even real ditch spacing are far too fine to render individually at this map scale — abstract upward for legibility:

- **Ditch grid:** rectilinear, aligned to a farm/property grid that's rotated independently of the river's meander direction (this rigid-grid-vs-sinuous-river contrast is itself the key "this is farmland" visual signal, per the cited Midwest section-line ditch pattern). Recommended spacing: **~120–200 m** between parallel ditch lines (a game-readable multiple of the real 30–100 ft/9–30 m spacing).
- **Ditch width:** ~2–4 m.
- **Routing hierarchy:** field ditches → 2–4 small named creeks per farm-zone stretch (reuse the tributary-creek spec above, 4–10 m wide) → main river or nearest pond. Don't route ditches directly into the main channel; always stage them through at least one creek, matching the cited real ditch→creek→river hierarchy.
- **Optional tile hint:** faint parallel striping inside a few fields, perpendicular to the ditch direction, spaced tighter than the ditch grid (e.g. every 20–40 m) — a subtle texture-only detail evoking the real greener/browner crop-line signature of buried tile, best reserved for close-up/overhead views.

## 6. Town-siting cross-check for the generator

- Site Downtown's oldest/densest core on the **outside of a bend** (cut-bank side — the higher, firmer, deep-water-adjacent ground), not the inside (point-bar side, which should stay low-density park/floodplain/farmland per the cited real pattern).
- Keep a visible **setback buffer** between the river's ordinary channel edge and building placement, wider on the point-bar/inside-bend side than the cut-bank/outside-bend side, echoing real floodplain-avoidance practice.
- Downtown can use either waterfront archetype cited in `town_water_siting.md` (industrial-legacy: rail/warehouses hugging the bank; or amenity: parkland/promenade) — a believable option is showing the transition from one to the other along the downtown riverfront, since that's a common real redevelopment pattern.

## Summary table

| Feature | Value |
|---|---|
| Channel width | 45 m |
| Meander wavelength | 524 m (k=6 harmonic, C/6) |
| Meander bends around loop | 12 apexes (6 wavelengths) |
| Bend radius of curvature | 90–135 m |
| Meander belt width (compressed) | ~360 m (±180 m + margin) |
| Max centerline excursion (capped) | ~250 m off midline |
| Lake length × width | 1,000 m × 300 m (3.3:1) |
| Lake inlet/outlet neck length | 100–150 m |
| Number of ponds | 5–7 |
| Pond size | 60–150 m long axis |
| Pond cadence along river | every 500–1,000 m |
| Tributary creek width / length | 4–10 m / 60–300 m |
| Farm ditch spacing / width | 120–200 m / 2–4 m |
| Ditch→creek→river hierarchy | field ditch → 2–4 creeks per farm stretch → river/pond |
