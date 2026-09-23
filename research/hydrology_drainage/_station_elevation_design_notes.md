# Station Elevation — Design Notes (Synthesis)

This file follows the exact same methodology as `_station_river_loop_design_notes.md` and is
its direct companion: everything below is **my own engineering proposal**, not a cited
real-world fact. There is no real precedent for a heightfield forced into an exact closed
loop, since real terrain exists on open, non-repeating ground — same caveat the river file
makes for the meander geometry. Real numbers cited below are drawn from
`real_elevation_data.md`. Station geometry recap: ring circumference **C = 3142 m**, floor
width **1000 m** (±500 m from the midline), four zones (Lake, Downtown, Residential, Farm) in
sequence around the loop.

---

## 1. Why elevation needs the same trick the river used

The river file's central insight: a heightfield (or any field) built as a sum of
`A_k·sin(k·θ + φ_k)` terms with **integer k**, where θ runs 0→2π once around the ring, is
*exactly* periodic by construction — it closes with zero seam, no manual stitching. Elevation
has the identical requirement: if h(θ=0) ≠ h(θ=2π), the loop closes with a visible cliff where
the floor meets itself. Every term proposed below is built to satisfy this by construction.

**A useful generalization, not used explicitly in the river file but central here:** since
the river's own centerline y(θ) is already exactly periodic, *any* smooth function of
`(x − y(θ))` for fixed x is automatically periodic in θ too — no extra `sin(kθ)` machinery
needed for that piece. This is exploited directly in §3 below to build the cross-section
(bluff) shape as a function of distance from the river rather than as its own harmonic series.

## 2. Cross-reference: the river's y(θ) formula

Quoting `_station_river_loop_design_notes.md` §2 directly, since elevation must be built to
correlate with it, not stand independently:

```
y(θ) = A1(θ)·sin(6θ + φ1)          -- primary meander bends
     + A2·sin(13θ + φ2)            -- secondary wiggle / bank irregularity
     + A3·sin(θ + φ3)              -- slow whole-loop drift (large-scale asymmetry)

where A1(θ) = A1_base · (1 + 0.3·sin(2θ + φ4))   -- makes the 6 main bends unequal in size
```

with A1_base ≈ 150 m, A2 ≈ 45 m, A3 ≈ 25 m, k=6 primary harmonic (λ = C/6 = 523.7 m, 12 bend
apexes total), capped combined excursion ≈ 250 m off midline. **This proposal reuses the
primary term's harmonic (k=6), phase (φ1), and bend-size envelope (the k=2, φ4 term) directly**
— elevation's along-loop harmonic choice is *derived* from the river's, not picked
independently, which is what makes cut-bank/point-bar correlation automatic rather than
something that has to be hand-tuned per bend.

## 3. The core cross-section: bluff tied to the river's own cut-bank side

**Real-world grounding (from `real_elevation_data.md`):** the bluff-river archetype
(Jefferson City, Cape Girardeau, Mankato) shows a consistent three-part cross-section —
flat low terrace directly on the river, one bluff rise, flat upland beyond — with town-specific
relief of roughly **70-180 ft (21-55 m)**, and a wider valley-wall ceiling of **250 ft (76 m)**
(Minnesota River valley, general figure). This is Shape 1 in `real_elevation_data.md`'s shape
catalog, and it's the shape the town-siting rule (generator_rules.md §6, river file §6) needs:
Downtown's core sits on the cut-bank (higher, firmer) side; the point-bar side stays low
floodplain/park.

**Convention (my proposal, not a physics derivation):** at any θ, the river's primary term
sign tells you which side is which. Where `sin(6θ+φ1) > 0` the channel bulges toward +x, and
the cut-bank (outer, eroding, higher/firmer) side sits at `x` slightly *beyond* the channel in
the +x direction; the point-bar (inner, depositional, low) side sits toward −x/midline. The
sign flips every half-wavelength, at exactly the same θ where the river's own centerline
crosses the midline (an inflection point) — which is also exactly where real river bends have
no cut-bank/point-bar asymmetry (banks are roughly symmetric at a crossover). Reusing
`sin(6θ+φ1)` itself (not a derivative or a separately-tuned term) as the asymmetry envelope
gets this behavior for free: envelope = 0 at inflections, envelope = ±1 (max asymmetry) exactly
at bend apexes — which is also where real cut-banks are steepest (max channel curvature).

**Cross-section formula:**

```
u(θ, x) = x − y(θ)                              -- signed distance from channel, across floor width

step(u) = tanh( (|u| − d0) / L_bluff )          -- flat-terrace / bluff / flat-upland shape

h_bluff(θ, x) = H_bluff(θ) · sign(sin(6θ+φ1)) · step(u)

where H_bluff(θ) = H_bluff_base · (1 + 0.3·sin(2θ + φ4))   -- reuses the river's own
                                                                bend-size envelope (same φ4)
```

- `d0` (flat low-terrace setback from the channel edge to the base of the bluff): gives
  Downtown's riverside blocks genuine flat frontage before the ground starts climbing, matching
  the real "flat land directly along the river" observation.
- `L_bluff` (bluff transition run): controls how steep the climb is. `tanh` was chosen
  deliberately over another sine term here *because* it has genuinely flat asymptotic
  shoulders on both sides (unlike a sine bump, which would roll back down) — exactly the
  "terrace, then bluff, then flat upland" shape real data shows, not a wave.
- The `sign(sin(6θ+φ1))` factor (rather than reusing the raw envelope as its own sign source)
  keeps the bluff's *magnitude* driven by `H_bluff(θ)` and `step(u)` while a separate, cleaner
  sign flip marks which side is high — same information as using `sin(6θ+φ1)` directly, kept
  as two factors for clarity of tuning.

## 4. Zone-scale baseline: the broad Lake-low tilt

The bluff term above is a **local** effect — it only elevates ground near the river's cut-bank
at each bend, exactly like real Jefferson City doesn't have its *whole town* elevated, just the
Capitol bluff specifically. A second, much gentler whole-loop term sets the broader "this part
of the ring generally sits lower/higher" baseline the task requires (Lake zone low; ponds
low), using the same closed-form logic at the lowest useful harmonic:

```
h_zone(θ) = Z1 · ( 1 − cos(θ − θ_Lake) )   ×  (−1)
          = −Z1 · (1 − cos(θ − θ_Lake))
```

i.e. a single k=1 cosine term phased so its **minimum lands exactly at the Lake zone's angular
center** (θ_Lake). k=1 is the right (only sensible) choice here: it's the lowest harmonic
available, giving one broad low basin and one broad high region per loop with no additional
undulation — appropriate for a background tilt that shouldn't compete visually with the
bend-scale (k=6) bluff pulses. Because Lake and Downtown are only ~90° apart around the loop
(not 180°), a single k=1 term can't put its minimum at Lake **and** its maximum at Downtown
simultaneously — and that's fine by design: Downtown's elevation gain is supposed to come from
the local bluff term (§3), not from a zone-wide lift, matching the real pattern where only the
specific bluff-adjacent blocks are elevated, not the whole townsite. `Z1` should stay small
relative to `H_bluff_base` (see §5) so this term reads as "gentle regional low near the water,"
never competing with the bend-scale relief.

**Interaction worth flagging as a feature, not a bug:** the river file's lake siting rule
(§3) places the lake at a peak of the A1(θ) envelope — i.e. at a wide bend, which is also
where `sin(6θ+φ1)` is near its own extremum. That means the Lake zone *will* still see a local
bluff-term pulse on the shore matching its cut-bank side. This is realistic — many real lakes
have one bluffier shore and one flat marshy shore — and the zone-scale `h_zone` term keeps that
shore only moderately elevated (low baseline + local bump) rather than reading as tall as a
true Downtown bluff (high baseline + comparable local bump), so the two don't look identical
even though both get a local pulse from the same mechanism.

## 5. Amplitude budget — grounded in Part 1, then compressed for buildability

**Real range found (`real_elevation_data.md`):** town-specific bluff relief 70-180 ft
(21-55 m), with an 80 ft (24 m) engineered-bluff data point at Salina and a 250 ft (76 m)
regional valley-wall ceiling at Mankato.

**Naive "just use the real number" choice would be H_bluff_base ≈ 35-45 m** (the interior of
that range). Checking that against the floor's actual available room shows this doesn't fit
without compression — the same kind of check the river file ran on meander belt width:

- The river's own excursion is capped at ~250 m off midline (river file §2). At a bend apex
  directly under Downtown, the cut-bank side of the channel can already be sitting close to
  that 250 m cap, leaving as little as **~250 m of floor width** between the channel and the
  zone edge on that side.
- A 35-45 m bluff graded at a walkable/driveable 10-20% street grade needs a transition run
  `L_bluff = H_bluff / grade` of roughly 175-450 m, plus the `d0` flat-terrace setback on top
  — comfortably **exceeding** the tightest 250 m clearance.
- Forcing the full transition into that clearance instead would require grades over 60%,
  which reads as a cliff face, not a climbable street — unusable for the block/lot system
  (generator_rules.md §3: Downtown blocks are ~300-400 ft/91-122 m per side and need genuinely
  flat ground, not a 60% slope, to hold a grid).

**Compression (my proposal, same move as the river file's belt-width compression):**

- **H_bluff_base = 18 m** (~59 ft) — toward the low end of the real 21-55 m range, closest to
  the Jefferson City-scale case rather than the dramatic Mankato-scale case. Flag this
  explicitly if a reviewer wants more Mankato-style drama: it's a deliberate
  realism-vs-buildable-street-grade trade-off, not an oversight.
- **d0 = 80 m** flat low-terrace setback — enough for roughly one Downtown block width of
  genuinely flat riverside frontage before the ground starts climbing.
- **L_bluff = 75 m** — gives a characteristic grade of 18/75 ≈ 24% at the steepest point,
  easing to near-flat within about 3×L_bluff (~225 m) of the transition's center. Steep by
  ordinary-street standards but plausible for a short "climb to the civic bluff" street
  (stairs/switchbacks allowed, same way real hill towns handle their steepest blocks) —
  the through-street grid itself stays on the flat terrace and flat upland on either side of
  this one steep stretch, not on the slope itself.
- **Total footprint** (d0 + ~3×L_bluff ≈ 80 + 225 = 305 m) fits inside even the tightest
  ~250-300 m worst-case clearance only loosely — flag this as genuinely tight, and note real
  towns are tight here too (Jefferson City's Capitol bluff sits close behind the riverfront
  commercial blocks, not set far back). Where the transition doesn't fully resolve before the
  zone edge, it simply continues into the neighboring Residential zone's upland terrace, which
  is the real-world pattern anyway (postwar residential sits *on* the upland terrace above the
  bluff, not beyond a separate flat gap).
- **Z1 (zone-scale Lake-low tilt) = 10 m** — kept well under half of H_bluff_base so it reads
  as a background tilt, not a competing relief feature.
- **Bend-to-bend variability envelope:** reusing the river's own `(1 + 0.3·sin(2θ+φ4))` term
  means individual bends' bluffs range from **~0.7×H_bluff_base to ~1.3×H_bluff_base**, i.e.
  roughly **13-23 m (43-77 ft)** bend-to-bend — enough spread that the six bluff pulses don't
  read as identical stamped copies, echoing the real spread found between Jefferson City-scale
  and Salina/Mankato-scale relief without needing a separate hand-authored variability system.

**Optional micro-relief texture:** a small secondary term reusing the river's own k=13
secondary harmonic, amplitude ~2 m, added to `h_zone` purely for surface texture (echoes the
"knob and kettle" glacial micro-relief noted even in the dead-flat archetype's real data) —
small enough to be invisible to the block/lot system, cosmetic only, safe to omit if not
needed.

## 6. Flat-buildable-ground check (per zone)

Following the river file's own compression logic (§5 there: "a full-realism belt width would
eat almost the entire 1000 m floor... this compression is a conscious trade-off"), the same
check applies here:

- **Downtown:** flat low terrace (d0 ≈ 80 m width) on the cut-bank riverside, wide enough for
  roughly one block row (91-122 m blocks per generator_rules.md §3 need slightly more —
  treat d0 as a *minimum*, tunable upward at the cost of a taller/longer bluff run elsewhere);
  flat upland beyond the bluff transition for civic/prestige buildings and the start of
  Residential. Point-bar side of the same bend stays low floodplain/park per the existing
  setback rule (generator_rules.md §6) — not lost buildable land, since it was never meant to
  be buildable.
- **Residential:** predominantly flat upland terrace (beyond the bluff transitions), the
  intended real-world siting for "postwar residential subdivisions on the flood-free
  terrace/upland" — this zone should see the *least* relief-driven land loss of the four.
- **Farm:** since ponds/creeks are deliberately biased toward Residential and Farm zones'
  floodplain-like low ground (river file §4), Farm zone will still see some bend apexes and
  their bluff pulses pass through it. With H_bluff_base compressed to 18 m and d0+3L_bluff
  ≈ 305 m, this leaves the majority of each ~524 m bend wavelength (along-loop) and the
  majority of the ±500 m floor half-width (cross-loop, away from the active bend) genuinely
  flat for the farm/ditch grid (generator_rules.md §10: 120-200 m ditch spacing needs
  multi-hundred-meter flat runs, which this preserves).
- **Lake:** flat low ground dominates by construction (Z1 tilt's minimum sits here), with only
  a moderate local bluff pulse on one shore per §4's interaction note — leaves the lake's
  shoreline park/promenade land flat as needed.

**Verdict: no further compression needed beyond the H_bluff_base = 18 m already chosen** — the
305 m worst-case transition footprint is tight only in the narrow band directly at a bend
apex under Downtown, which is both expected (that's where the real-world analogy says the
steepest streets belong) and self-limiting (each bend apex is a brief, ~524 m-wavelength
event, not a sustained condition around the whole loop).

## 7. Bend-count / harmonic sanity check

Reusing the river's own numbers directly: **k = 6 primary harmonic → λ = C/6 = 523.7 m → 12
bend apexes around the loop (6 swinging toward +x, 6 toward −x, alternating)**. Because the
elevation bluff term is phase-locked to this same k=6, φ1 term, the station produces **exactly
6 cut-bank "high pulses" (bluff crests) and 6 point-bar "low pulses" (floodplain crests) per
full circuit, one-to-one with the river's 6 primary meander wavelengths** — terrain and river
stay mutually consistent everywhere around the loop by construction, not by manual placement.

Checking the along-loop footprint: the half-wavelength (apex-to-inflection distance) is
`C/(2×6) = 262 m`. The cross-section transition's along-loop "active zone" (where
`|sin(6θ+φ1)|` stays close enough to its peak for the bluff to read as present, roughly the
middle third of each half-wavelength, ≈ 85-90 m) is well under this 262 m spacing, leaving
clear, unambiguous flat-to-bluff-to-flat gaps between consecutive pulses — comfortably enough
room for several of the ~91-122 m Downtown blocks (generator_rules.md §3) to read as distinct
before the next pulse begins. If a future revision changes the river's channel width (and
therefore its k), this elevation proposal's k=6 term must be re-locked to whatever the new
primary harmonic is — it is not an independent choice (see §2).

## Summary table

| Parameter | Value | Grounding |
|---|---|---|
| Primary bluff harmonic | k = 6 (reused from river's y(θ), same φ1) | Required, not chosen — keeps cut-bank correlation automatic |
| Bend-size variability envelope | reused `(1 + 0.3·sin(2θ+φ4))` from river's A1(θ), same φ4 | Same mechanism as river's unequal-bend-size term |
| Zone-scale tilt harmonic | k = 1, phased to trough at Lake zone center | Lowest available harmonic; background-only, doesn't compete with k=6 |
| Optional micro-relief harmonic | k = 13 (reused from river's A2 term) | Cosmetic texture only, ~2 m amplitude |
| H_bluff_base (bluff height) | **18 m (~59 ft)** | Compressed from real 21-55 m (70-180 ft) range for buildable street grades |
| Bend-to-bend bluff range | ~13-23 m (43-77 ft) | From reused (1±0.3) envelope |
| d0 (flat low-terrace setback) | **80 m** | Gives Downtown riverside genuine flat frontage before the climb |
| L_bluff (bluff transition run) | **75 m** | ~24% max grade, eases to flat within ~225 m |
| Total bluff footprint (d0 + 3×L_bluff) | ~305 m | Tight vs. worst-case 250-300 m cut-bank clearance; flagged, accepted as realistic |
| Z1 (zone-scale Lake-low tilt) | **10 m** | Kept < H_bluff_base/2 so it reads as background, not competing relief |
| Real-world relief range this is grounded in | 70-180 ft (21-55 m) town-specific; 250 ft (76 m) regional ceiling (Mankato/Minnesota R. valley); 80 ft (24 m) engineered bluff (Salina) | See `real_elevation_data.md` |
| Bend apexes / bluff pulses per loop | 12 apexes total → 6 bluff (cut-bank) + 6 low (point-bar) pulses | Locked to river's k=6 |
| Half-wavelength (apex-to-inflection) | 262 m | Comfortably exceeds the ~85-90 m active bluff footprint per pulse |
| Dead-flat archetype real slope reference | ~4 ft/mile (~0.076%) (Great Black Swamp) | Used to confirm Farm/Lake baseline should read as visually flat, not just "flatter" |
