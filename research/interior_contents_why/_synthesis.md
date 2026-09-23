# Synthesis — Applying the "Why" Layer to the Base Catalogs

This is the top-level index for `research/interior_contents_why/`. It ties together:
- `residential_demographic_framework.md` — Part 1: income tier, household structure, construction era, and their causal effects on the residential pools in `building_catalog/residential/`.
- `residential_why_notes.md` — Part 1 (continued): broader placement/existence logic (plumbing clustering, basements, mudrooms, formal/informal room splits, laundry location, garage-as-workshop, porch-vs-patio) that applies across most households regardless of demographic roll.
- `commercial_civic_farm_economic_condition.md` — Part 2: a community economic-condition roll and its effects on 10 priority archetypes in `building_catalog/commercial_civic_farm/`.

## The core principle: modify weights, don't replace pools

Every file in `building_catalog/` already defines the ground truth: a room list with size ranges and a per-room content **pool** (item + count range). Nothing in this `interior_contents_why/` layer invents a different set of rooms or a different set of items for the generator to place instead. Its entire job is to answer, for each generation call: **given who lives/works here, which end of the pool's stated range should this instance land near, which optional (0-1 / 0-2) items should actually be present, and what condition/quality/era descriptor should the renderer apply to each placed item?**

Concretely, the two-file (residential) and one-file (commercial) "why" layers are **weight modifiers layered on top of** — not substitutes for — the base pool sampling step.

## Recommended generation order

**Residential buildings:**
1. Pick the archetype (as today) — this fixes the room list, the base pool per room, and (per the archetype's Overview section) the default construction era.
2. Roll **household structure** (single / couple / family with kids / retiree-empty-nester / multigenerational-roommates) per `residential_demographic_framework.md` Dimension 2 — this determines room USE (which bedroom is a kid's room vs. a home office vs. a craft room vs. a second primary bedroom) before any item sampling happens, since room use gates which sub-pool applies to that room.
3. Roll **income tier** (low / middle / upper-middle) per Dimension 1, weighted by the settlement's population tier (rural villages skew low/middle; small cities carry the full spread) — this sets count-within-range bias, optional-item presence probability, and the quality/condition/clutter descriptor for every item placed in the house.
4. Confirm or adjust **effective construction era** per Dimension 3 — usually just the archetype's stated era, but allow a renovation roll (see `residential_why_notes.md` note on kitchen/bath remodels) to bump specific rooms to a later effective era independent of the shell.
5. Sample each room's items from the base catalog pool, applying the income-tier count/quality bias and the era-gated technology/norm rules (closets vs. wardrobes, AC presence, appliance types, dining-room/home-office presence) from Dimension 1 and 3's tables.
6. Roll the "new diagnostic items" table (chest freezer, home gym, iconography, kids'-room electronics, slipcovers, gun cabinet/safe, hobbyist workshop) against the conditions each item specifies — these sit alongside, not instead of, the base pool.
7. Apply the broader placement logic in `residential_why_notes.md` (plumbing-core clustering for retrofit bathrooms, focal-point furniture arrangement, front-porch-vs-rear-patio social-space bias by era, laundry location by era) as layout/arrangement rules once items are chosen.

**Commercial/civic/farm buildings:**
1. Pick the archetype (as today) — fixes the space list and base pool per space.
2. Roll **one community economic-condition value per settlement** (Thriving / Stable-but-plain / Struggling-Rust-Belt), optionally combined with the **Lake-resort/tourist-adjacent modifier flag** — this is a single settlement-level roll applied consistently to every commercial/civic building generated within that settlement, not re-rolled per building, since a town's economic condition is a shared, coherent fact about the whole place (see `commercial_civic_farm_economic_condition.md`'s framing: this is a reinforcing spiral, not independent per-building noise).
3. For the 10 priority archetypes in `commercial_civic_farm_economic_condition.md`, apply that archetype's condition-specific table: stock-mix/count bias within the base pool's range, item condition/era descriptors, and staffing/occupancy-implying set dressing.
4. For the other 22 archetypes not yet covered by a dedicated condition table, apply the same general logic by analogy — the cross-archetype summary table's pattern (thriving = fuller/newer/actively-maintained; struggling = thinner/older/deferred-maintenance; resort = seasonal-tourist stock layered on top) generalizes reasonably to retail, civic, and farm archetypes not explicitly written up, pending a future expansion pass.

## Why two dimensions (residential demographic, commercial economic) rather than one unified roll

They are correlated in the real world — a struggling town's households skew lower-income on average, and a thriving town's Main Street reflects a healthier local income base feeding it — but they are NOT the same roll, for a concrete generation reason: individual households vary in income/structure even within a single town (a struggling Rust Belt town still has some solidly middle-income households — a schoolteacher, a small-business owner; a thriving farm-service town still has some low-income households — a retired farmhand on fixed income), while a town's commercial economic condition is a genuinely shared, settlement-level fact that every business on its Main Street experiences together. Modeling them as two correlated-but-independent rolls (bias the residential income-tier distribution toward the settlement's economic-condition tier, without hard-locking every household to match it) produces more realistic variety than either a fully independent roll (which would produce implausible combinations, like a lavishly stocked hardware store on a visibly boarded-up Main Street) or a fully locked roll (which would make every household in a struggling town identically poor, erasing the real income variety documented in the demographic-framework sources).

**Suggested correlation weighting for the generator:** when a settlement rolls "Struggling," shift the household income-tier distribution roughly one step lower on average (more low, fewer upper-middle) versus a "Thriving" settlement's distribution, which shifts roughly one step higher — but keep the full three-tier spread available in both cases rather than eliminating any tier entirely.

## Population-tiers research as a related, not duplicated, resource

`research/population_tiers/` (real-town case studies: village, small-town, small-city tiers) and `research/demographics/` already exist in this research tree and cover **town layout/founding-type** facts (grid pattern, Main Street width, civic-anchor pattern, founding type — railroad/river-mill/county-seat) rather than the interior-contents-and-condition layer this file's companions cover. A given settlement's founding type is a plausible, though not required, input to its economic-condition roll — e.g., a river-mill town whose mill closed decades ago, or a railroad town on a since-abandoned line, are natural "Struggling/Rust-Belt" backstories, while a courthouse-square county-seat town with a diversified institutional economy (county government, a hospital, a small college) is a natural "Thriving" or "Stable" backstory — but this is a narrative-consistency suggestion for whoever authors settlement instances, not a hard mechanical dependency this research layer requires.

## File count and scope recap

Four files in this directory:
1. `residential_demographic_framework.md` — 3 demographic dimensions (income tier, household structure, construction era) with causal WHY per effect, plus a 7-item new-diagnostic-items table.
2. `residential_why_notes.md` — 10 broader causal placement notes not fully covered by the demographic framework.
3. `commercial_civic_farm_economic_condition.md` — a 3-tier (+1 modifier) economic-condition dimension applied to 10 priority archetypes (hardware store, diner/cafe, general store, small grocery, church, library, town hall, bank branch, gas station, bar/tavern), plus a cross-archetype summary table and generalization guidance for the remaining 22 archetypes.
4. `_synthesis.md` (this file) — ties the above together and states the apply-order/weight-modifier principle.
