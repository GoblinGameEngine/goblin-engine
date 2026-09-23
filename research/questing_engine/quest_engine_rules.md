# Procedural Quest/NPC Engine — Rules & Weights

Sibling file to `research/generator_rules.md`, same convention: every number below is a
**deterministic weight to sample from a seeded PRNG**, not a fixed constant — same seed + same
world state must always produce the same quest-selection output. This file is what a future
quest-generation system should actually read weights from. Full sourcing lives in
`research/questing_engine/radiant_reference/` (Bethesda's Radiant Story architecture, its
documented deficiencies, and 12 concrete workarounds) and `research/questing_engine/
story_patterns/` (66 real documented story patterns — 50 nonfiction, 16 fiction/folklore —
mapped to the 6 community demographic archetypes in `research/demographics/
_demographic_archetypes.md`). **No dialogue or quest text is written here or anywhere in this
research phase** — this is the structural/weighting framework only, per explicit instruction;
dialogue is a later, separate phase.

---

## 1. Core design principle (confirmed against Bethesda's own architecture)

A quest is authored as a **role with eligibility conditions, never as a reference to a specific
world object**. The role is resolved — cast — only at the moment the quest actually starts,
against whatever the world currently, actually contains. This is precisely the property the
project's design brief asked for: *"a questing engine that does not need to know its
destination or its beginning to function seamlessly to the player — it only needs to go from
path to path while affecting other characters in predicted ways."* A character can only ever be
pulled into a role whose conditions it currently satisfies, so "affecting characters in
predicted ways" falls directly out of the eligibility-matching mechanism — nothing needs to be
planned per-character in advance, because the eligibility conditions themselves are the
prediction.

Two layered systems implement this (full detail: `radiant_reference/_summary.md`):
1. **Alias resolution** (casting) — §3 below.
2. **Selection/weighting** (which quest even gets a chance to cast itself) — §4-6 below.

---

## 2. Quest shape taxonomy

Both Skyrim's and Fallout 4's large radiant catalogs collapse into a small fixed set of
**shapes**, each independently re-skinned per context by swapping aliases/conditions/flavor —
not a large bespoke catalog (`radiant_reference/radiant_quest_categories.md`). Our engine
should do the same. The 8 Bethesda shapes are generalized below into 9 shapes, deliberately
worded to not assume the game has a combat system (none is confirmed yet) — "Clear/Confront/
Protect" should read as combat, social confrontation, or bureaucratic/legal resolution
depending on what verbs the game actually ships with; this file defines the *slot structure*,
not the resolution mechanic.

| Shape | Radiant equivalent | Description | Alias roles typically needed |
|---|---|---|---|
| Clear/Resolve | Clear | Resolve a location-tagged problem | Location alias (problem-tagged) |
| Retrieve | Retrieve | Fetch a specific/randomized item from a location | Location alias + Item alias |
| Confront | Kill | Directly confront a specific NPC target | Actor alias (target) |
| Protect/Defend | Protect | Defend a location/NPC against a recurring threat | Location or Actor alias (defended) — **must carry the D2 recurring-category flag, §6** |
| Rescue | Rescue | Retrieve a missing/captive NPC | Actor alias (missing) + Location alias (holds them) |
| Acquire Covertly | Steal | Obtain an item/information without consent | Actor alias (owner) + Item alias + Location alias |
| Favor/Errand | Favor-Fetch | Low-stakes social fetch/delivery/message | 2 Actor aliases (requester, recipient) + optional Item alias |
| Investigate | *(new — synthesized from Fallout 4's "Suspected Synth"/Railroad investigation flavor + the fiction research's Town-Wide-Secret pattern)* | Gather testimony/evidence toward a revealed truth | Multiple Actor aliases (witnesses) + Location alias (site of the secret) |
| Logistics/Growth | Logistics | Community resource/expansion task | Location alias (beneficiary) + Item/resource alias |

**Rule (from `_summary.md` §1):** author each shape once. All context/archetype variation is
an alias-and-condition-filling problem, not a new shape design.

---

## 3. Alias system — mapped onto our own existing data

Bethesda's alias conditions test faction/location-keyword/relationship state
(`radiant_reference/alias_system.md`). We don't have factions; we have the taxonomies already
built across the map-research phase. Map alias types onto them directly:

| Alias type | Bethesda equivalent | Our condition source |
|---|---|---|
| Location Alias | Location Alias, tag-matched | `generator_rules.md` zone (§1) + settlement demographic archetype (§15) + building_catalog archetype tag (§11) + building condition state (occupied/modernized/vacant-derelict, §15) |
| Actor Alias (resident) | Reference Alias, faction-matched | Household roll: income tier + household structure + construction era (`generator_rules.md` §14) |
| Actor Alias (business owner/staff) | Reference Alias, faction-matched | Settlement economic-condition roll (Thriving/Stable/Struggling + resort modifier, §14) applied to the business's archetype |
| Item Alias | Item Alias, keyword-matched | `research/interior_props_master_list.md` (265 items) or `research/lot_contents/` yard props — matched by room/building type the Location Alias resolved to |
| Reward Alias | (Bethesda hardcodes per-quest) | New — see §7 below |

**Resolution order (from `alias_system.md` §3):** resolve as a **chain of narrowing lookups**,
not one flat search — location matching archetype/tag → actor at that location matching
condition → item owned by/at that actor. Implement as composable primitives: find-location-
by-tag, find-actor-by-relationship-to-filled-alias, find-actor-by-condition, find-item-by-
container, inherit-from-another-quest's-alias, create-new-instance-from-template.

**Conflict resolution (from `alias_system.md` §5):** default permissive (most fills don't need
exclusivity); explicit per-role "Reserved" flag for cases that do. Avoids both "always
exclusive" (quests fail to start in a small NPC pool — directly relevant, see §5's pool-size
finding) and "never exclusive" (incoherent double-booked NPCs).

---

## 4. Story-pattern weighting by demographic archetype

This is the layer that answers the brief's core ask: **weights that put quest content where it
belongs.** Two independent weight axes per settlement, both keyed to the settlement's already-
rolled demographic archetype (`generator_rules.md` §15):

### 4a. Quest-shape weight bias by archetype

Base shape eligibility (§2) is uniform; these are **multipliers** applied on top, derived from
which shapes the real story-pattern research actually found material for per archetype.

| Archetype | Weighted up | Weighted down | Why |
|---|---|---|---|
| Stable Ag/Manufacturing | Broadest, most even distribution across all 9 shapes | none notably suppressed | Richest source material of any archetype — 9 nonfiction + 6 fiction patterns, the only archetype with real coverage of nearly every shape |
| Declining Rust-Belt Industrial | Investigate, Clear/Resolve, Protect/Defend | Logistics/Growth | Decline/decay/danger-coded real patterns dominate (factory collapse, water crisis, ruin storytelling); nothing in the real research is growth-flavored |
| Growing Exurban/Bedroom Community | Logistics/Growth, Favor/Errand | Investigate | Thinnest story material of any archetype (no dedicated literary tradition, weakest nonfiction single-source coverage) — bias toward the two lowest-drama, most genuinely-attested shapes (growth/development friction, HOA-style favors) rather than forcing mystery content the real research doesn't support |
| Stable County-Seat/Administrative Center | Investigate, Logistics | Rescue, Confront | Accountability/bureaucratic-process journalism (courthouse preservation, news-desert coverage, open-records stories) dominates; government-as-institution stories skew procedural, not combat/rescue-flavored |
| College Town | Investigate, Favor/Errand | Protect/Defend | Campus-ghost/town-gown/academic-calendar patterns are social and investigative, not defense-flavored; the archetype's real material has zero defend/protect precedent |
| Lake-Resort/Tourism-and-Retiree | Retrieve, Favor/Errand | Confront | Seasonal-economy errands and tourism/hospitality-workforce stories dominate; real material is socioeconomic tension, not confrontation |

### 4b. Nonfiction-vs-fiction weight split by archetype

Nonfiction patterns are the *routine* quest-content majority (plausible, grounded, repeatable
without straining credulity); fiction/folklore patterns are *rare capstone/flavor* content —
this mirrors the fiction research's own finding that patterns like the Town-Wide-Secret
template are explicitly "usable cross-archetype as rare capstone," not routine filler, and
directly implements RimWorld's Story-Richness principle (§6 below): rare content should read as
rare, not diluted into the everyday pool.

| Archetype | Nonfiction weight | Fiction/folklore weight | Notes |
|---|---|---|---|
| Stable Ag/Manufacturing | 80% | 20% | Highest fiction allocation — richest literary tradition (Anderson/Lewis/Keillor/Cather), including a routine-tone overlay (Keillor's "Gentle Anecdote Cycle," pattern 3) that can apply to *any* generated quest's flavor text, not just a rare event |
| Declining Rust-Belt Industrial | 88% | 12% | Fiction allocation reserved almost entirely for the Town-Wide-Secret capstone (pattern 7) and Ruin-Storytelling as a *presentation/tone* layer (pattern 9, not a discrete quest — see content note below) |
| Growing Exurban/Bedroom Community | 95% | 5% | No dedicated fiction tradition exists (fiction index's own finding) — keep fiction allocation minimal, leaning on cross-archetype patterns (Grotesque-in-Plain-Sight, Our-Town framing) rather than forcing archetype-unique folklore that doesn't exist |
| Stable County-Seat/Administrative | 90% | 10% | Fiction allocation mostly the Booster-Culture-Satire tone overlay (pattern 2) and Our-Town sacred-framing (pattern 5) as presentation devices, not discrete quests |
| College Town | 85% | 15% | Campus Ghost-Legend (pattern 12) and Town-Gown Conflict (pattern 13) are both archetype-exclusive and well-documented — higher fiction allocation than County-Seat/Exurban is warranted |
| Lake-Resort/Tourism-and-Retiree | 85% | 15% | Lake Monster/Cryptid (pattern 11) as a rare capstone, Summer-People-vs-Locals (pattern 15) as more-routine social tension — genuinely archetype-exclusive material on both sides |

**Content-sensitivity note:** pattern 6 (Jackson's "The Lottery" — Normalized Ritual Atrocity)
should be adapted **structurally only** if used at all — a town tradition/secret vote/social-
exclusion ritual with genuine stakes, not literal ritual violence — given the game's
established family-neighborhood tone (residential interiors include kids' bedrooms, etc.). Flag
this pattern's weight at effectively zero by default, adjustable later, rather than silently
including it at parity with the other 65 patterns.

---

## 5. Cross-archetype patterns needing per-archetype re-skinning, not reuse

The nonfiction index identifies 5 patterns that recur across 3+ archetypes but must NOT share
one template — treat each archetype's version as a **separate weighted variant of the same
shape**, not one shared instance:

| Pattern | Shape | Per-archetype variant weight driver |
|---|---|---|
| Single-institution dependency | Investigate/Logistics | Institution type = building_catalog archetype matching the settlement's dominant employer (factory→small_factory_mill/warehouse; college→school/library; county govt→town_hall/courthouse; farm economy→grain_elevator/barn_dairy); severity weight = settlement economic-condition roll (§14) |
| Outside-money displacement | Logistics/Favor | Driver variable = permanent household formation (Exurban) vs. seasonal/vacation demand (Lake-Resort) vs. academic-calendar cyclical (College Town) — same shape, different recurrence-cadence weight |
| Water infrastructure crisis | Clear/Resolve or Logistics | Causal frame = municipal poverty (Rust-Belt, `water_tower`/`town_hall`) vs. environmental threat (Lake-Resort) vs. growth-outpacing-capacity (Exurban) — **tone weight, not just cause weight**: crisis-of-poverty, crisis-of-environment, and crisis-of-abundance should read as different emotional registers even reusing the same building |
| School enrollment crisis | Investigate/Logistics | Direction weight: consolidation-from-decline (Ag/Manufacturing, Rust-Belt) vs. overcrowding-from-growth (Exurban) vs. levy-failure-from-aging-electorate (Lake-Resort) — four archetypes, opposite drivers, same `school` building |
| Local business closure | Favor/Investigate | Emotional-register weight: generational-succession/"end of an era" (Ag/Manufacturing) vs. terminal-decline evidence (Rust-Belt) vs. contested-retail-competition (Exurban) vs. accountability-infrastructure-loss (County-Seat) vs. routine-seasonal-stress (Lake-Resort) — the single most reusable-with-variation pattern found; five archetypes, five distinct tones, same surface event |

---

## 6. Anti-repetition / pacing weight structure

Directly encodes the 12 workarounds from `radiant_reference/deficiencies_and_workarounds.md`,
which map Bethesda's documented failure modes to precedents from RimWorld's storyteller system,
Left 4 Dead's AI Director, "Talk of the Town," and other cited systems. **These weight rules
apply on top of §4-5's content weights, as a second, independent multiplier layer** — exactly
RimWorld's own separation of "which incident" from "how much incident pacing right now."

| # | Rule | Precedent | What it weights |
|---|---|---|---|
| 1 | Shape-level recency-decay, keyed to `(shape, NPC_or_location)` — continuous decay toward 1.0 over N days, not a hard cooldown gate | RimWorld recency-decay pattern; Bethesda's own "Hours until reset" generalized one abstraction level up | Prevents the *shape* (not just the specific quest instance) from feeling repeated at one NPC/location |
| 2 | Sub-variant pool exhaustion for flavor/dressing, one layer below shape | Bethesda's "Do all before repeating" | Cheap perceived variety without new mechanical content (RimWorld's "Hair Complexity") |
| 3 | Cumulative-completion escalation — past a threshold, a recurring category's weight is *replaced* by a graduated/resolution variant, not just decayed | Left 4 Dead's build/sustain/peak/**relax** phase model | Gives Protect/Defend-shape categories (§2, flagged "no natural end state") a designed exit ramp — directly avoids the documented Fallout 4 "Another Settlement Needs Our Help" failure |
| 4 | Hard concurrency cap at the category level, independent of per-instance cooldowns | Bethesda's own misc-quest mutual-exclusion rule | One flagged recurring category active per neighborhood/settlement at a time |
| 5 | Quest-giver least-recently-used rotation for high-frequency categories | Preston Garvey case study (the specific failure of pinning a recurring category to one NPC) | Prevents any single NPC from absorbing a whole category's perceived repetition |
| 6 | Inverse pool-size weight scaling — small alias-candidate pools get lower base weight AND longer decay windows than a fixed constant | RimWorld's wealth/population-adaptive incident scaling | **Directly targets our station's own exposure**: a bounded ring habitat has a far smaller NPC/location census than an open-world RPG, so pool-size-blind cooldowns (Bethesda's own, sized for 400-NPC pools) would exhaust almost immediately here |
| 7 | Relational-combination variety — weight keyed to *which relationship* between two small-pool members is surfaced, not just which individual | "Talk of the Town" relationship-graph variety | Makes a 5-NPC neighborhood support more distinguishable draws than "5 choose 1" |
| 8 | Persistent per-NPC/per-location event-history log, additive to live-state Match Conditions | Left 4 Dead's tracked-challenge-history; "Talk of the Town" causal diffusion; Dwarf Fortress's Legends persistence | Fixes "quest amnesia" — the world should remember what the player already caused here |
| 9 | Long-duration negative weight on re-offering the same shape where a relevant history entry exists (longer than rule 1's window — this is about plausibility, not fatigue) | Same as 8 | Stops "this already got resolved here" repeats specifically |
| 10 | Positive weight spike-then-decay on shapes that are thematic consequences of a logged event | Bethesda's own event-driven "consequence" categories (An enemy's gratitude, Revenge), formalized into an explicit decay curve | Turns Bethesda's binary fire-once reaction into a tunable curve |
| 11 | Single global "pacing state" (calm/build/peak/relax) multiplying every category's *final* weight, applied after all content weights | Left 4 Dead's phase model; RimWorld's storytellers as swappable policies over one unchanged pool | Separates "which category" (rules 1-10) from "how much radiant content right now, in aggregate" |
| 12 | Swappable pacing-policy object (transition speed, peak-hold duration, relax-aggressiveness as named, interchangeable policies) | RimWorld's Cassandra/Phoebe/Randy | Lets the same content weight tables produce a different overall play *feel* by swapping one policy, not redesigning content |

**RimWorld's Story-Richness target, adopted directly:** optimize the weight system for *the
percentage of selected content that lands as interesting*, not maximum volume or maximum
randomness (Tynan Sylvester, "The Simulation Dream," cited in `deficiencies_and_workarounds.md`
§2.1).

---

## 7. Reward-tier weighting (structure only — items and currency values deferred)

Per direct instruction: define the **weight axis** now; specific item names and monetary
amounts are a later phase. Reward tier is a third independent weight dimension, layered
alongside §4 (content) and §6 (pacing):

| Reward-tier driver | Effect on weight toward Money vs. High-Power-Item vs. Low-tier |
|---|---|
| Quest shape "stakes" | Rescue, Investigate (capstone-chain variant), Protect/Defend, Confront weight toward higher tier; Favor/Errand, routine Retrieve weight toward lower tier |
| Story-pattern rarity (§4b) | Fiction/folklore capstone patterns (Town-Wide-Secret, Lake Monster, Campus Ghost) weight toward the highest tier available — directly implements RimWorld's Story-Richness correlation: rare content should both *feel* rare and *pay* rare, which doubles as an anti-farming/anti-repetition economic signal (§6), not just a narrative one |
| Settlement economic-condition roll (`generator_rules.md` §14) | **Thriving** settlements weight toward Money rewards (a functioning cash economy); **Struggling/Rust-Belt** settlements weight toward High-Power-Item rewards instead — heirlooms, tools, inherited knowledge, barter goods — reflecting the real economic-condition research's own finding that a struggling town's institutions are cash-poor but not necessarily asset-poor; **Lake-Resort** settlements weight bimodally, matching §15's own bimodal-income finding (gentrified small resorts → money-heavy, larger tourism-and-retiree cities → item-heavy) |
| Alias-pool rarity (§6 rule 6) | A quest resolved against an unusually small/hard-to-match candidate pool weights toward higher reward tier — scarcity of *matching content* is itself a legitimate difficulty signal, independent of the shape's inherent stakes |
| Anti-repetition state (§6 rules 1, 6, 8-9) | A quest instance that survived heavy recency/pool-size/history penalties to still get selected (i.e., a genuinely rare draw) should weight toward higher tier — makes the reward legible to the player as "this doesn't happen often," reinforcing rather than fighting the pacing system |

**Determinism requirement (restated, applies to every table in this file):** every weighted roll
in §4-7 must be a pure function of `(seed, settlement_id, NPC/location_id, in-game timestamp,
persistent event-history state)` — same inputs, same output, every time, consistent with the
project's whole architecture (`generator_rules.md`'s own opening principle).

---

## 8. What this file is FOR (per the user's own framing)

This file — and the research it's built on — is meant to function as **a tool a person uses
together with an AI to generate the actual weight values** for a specific station's quest
engine, not a hardcoded final answer. The tables above define the *shape* of every weight
(what varies, on what axis, correlated with what) with real research grounding for the
*direction* of each bias (why Rust-Belt weights toward Investigate, why Exurban weights away
from it) — the exact numeric values are intentionally left as tunable parameters. This
structure is what should eventually generate the default station shipped with the game, and the
same structure/tool is what a player generating their own station later would use to produce a
different, internally-consistent set of weights for their own version.

---

## 9. Open questions / flagged for the next phase

- The game's actual verb set (combat vs. social/legal resolution vs. something else entirely)
  is not defined yet — §2's shape names are deliberately generic pending that decision.
- §7's reward-tier axis needs the actual item/currency catalog (a future research or design
  pass) before it's implementable — this file only defines *when* a quest should roll toward a
  higher tier, not what that tier concretely contains.
- The building-catalog gaps the nonfiction research flagged (hospital/clinic, harbor/dock
  industrial-waterfront, marina/ferry dock — `story_patterns/_nonfiction_index.md`) block a
  handful of specific story-pattern location aliases from resolving until those building
  archetypes exist.
- No dialogue/text-generation design has been started — deliberately deferred per instruction,
  planned as a distinct future phase once this weighting framework is validated.
- §6's 12 workaround rules are specified as rule *shapes*; actual decay-curve constants,
  cooldown-day counts, and pacing-policy parameters all need numeric tuning once the engine is
  implementable and playtestable — consistent with how `generator_rules.md`'s own numeric
  ranges are described as "ranges to sample from," not final constants.
