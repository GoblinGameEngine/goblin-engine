# Real Documented Radiant Quest Categories: Skyrim and Fallout 4

Research focus: the actual, shipped list of radiant quest types in both
games — not a paraphrase, but the real quest names, which faction/questline
they belong to, what determines their eligible target locations/NPCs, and
what mechanism (per `alias_system.md` / `story_manager_weighting.md`) governs
when each becomes available. Sources: UESP's `Skyrim:Radiant` page (fan-
maintained but data-driven, cross-referencing every quest's own possible-
location/possible-NPC list) and the Fallout Wiki's `Fallout 4 quests` page
(which itemizes every quest, its giver, and its category as shipped).

---

## 1. Skyrim's radiant quest catalog

Skyrim's radiant system spans **far more than the well-known "innkeeper
rumors."** UESP's own framing: *"The Radiant quest system is a quest
generator that creates quests from a series of components such as location,
enemy type, and reward... it can create a near infinite number of quests
with a fraction of the time and effort required to create a traditional
one."* And, bluntly: *"This quest system cannot create large, complicated,
or particularly interesting quests"* — a fan-documentation source
independently arriving at the same limitation Bethesda's own designer states
in `known_limitations.md`.

### By questline/faction

**Companions** (the warriors' guild) — radiant "job board" contracts, largely
combat/retrieval-flavored:
- *Animal Extermination (B)* — clear a beast den (18+ eligible dungeons).
- *Trouble in Skyrim* — clear out a troublesome dungeon in general (115+
  eligible dungeons with a boss enemy — one of the broadest eligible-target
  pools in the game).
- *Family Heirloom* — retrieve a specific item from a dungeon's boss chest
  (75+ eligible dungeons).
- *Rescue Mission* — rescue a kidnapped citizen from a dungeon with both a
  boss enemy and a place to hold a captive (50+ eligible dungeons).
- *Escaped Criminal* / *Hired Muscle* — target-an-NPC contracts (the latter
  eligible against 400+ citizens — effectively "almost anyone").

**Thieves Guild** — property-crime radiant jobs, each keyed to a *building
type* rather than a specific building:
- *The Heist Job* — steal an item from a store with a strongbox (25+ stores).
- *The Numbers Job* — falsify a store's business ledger (25+ stores).
- *The Burglary Job* / *The Sweep Job* / *The Shill Job* — steal from, steal
  multiple items from, or plant evidence in a wealthy home (25+ homes each).
- *The Bedlam Job* — steal a target gold-value of items from *any major hold
  capital* (location-type eligibility at the broadest possible grain: "any
  city," not "any specific building").
- *The Fishing Job* — pickpocket a specific item from a citizen in a city.

**Dark Brotherhood** — assassination contracts:
- *The Dark Brotherhood Forever* — repeatable "yet another child has prayed
  to their mother" contract, drawn from a pool of ~10 possible NPC targets.

**Bounty quests** (generic, given by "any innkeeper, jarl, or steward" — the
broadest quest-giver eligibility category in the game) — this is the
category most players actually mean by "innkeeper rumors":
- *Bounty: Bandit Boss*, *Bounty: Dragon*, *Bounty: Forsworn*, *Bounty:
  Giant* — each keyed to a different eligible-location *type* (bandit
  hideouts with a named boss, dragon lairs, Reach dungeons with a Forsworn
  leader, giant camps respectively), each a "kill the boss of this location
  type" template with the location swapped per instance.

**Generic misc / "world interaction" quests** — the broadest, most
frequently-encountered radiant category, largely *reactive to player
behavior* rather than location-clearing:
- *A Few Words with You*, *Delivery*, *Rare Gifts*, *Some Light Theft* —
  small fetch/favor quests each drawn from a small pool (3-6) of eligible
  NPCs.
- *Inheritance* — triggers off a befriended NPC's death.
- *An enemy's gratitude* / *Revenge, Hired Thugs* / *Scare my Enemy* /
  *Steal, Thugs hunt player* — direct consequence-of-player-action quests:
  reward or retaliation content that fires off the player having killed an
  NPC's enemy, murdered an NPC's relative, assaulted someone, or stolen from
  someone. These map directly onto the Story Manager's event-driven design
  (`story_manager_weighting.md` Section 1) — Kill Actor and comparable
  events feeding directly into eligibility for these specific quest types.

**Faction-adjacent crafting/skill radiant content**: tutorial/repeatable
"activities" (Alchemy Tutorial, Blacksmithing Tutorial, Chop Wood, Mine Ore,
Gather Wheat) — UESP explicitly separates these from true "quests" (no quest
log entry) but they run on the same radiant targeting logic.

### A documented mutual-exclusion rule
UESP notes an explicit **category-level exclusivity constraint**: only *one*
of {A Few Words with You, Delivery, Dungeon Delving (Bandits), Dungeon
Delving (Caves), Kill the Bandit Leader, Rare Gifts, Some Light Theft} can be
active at a time — i.e. Bethesda deliberately capped concurrent exposure to
this specific radiant pool, rather than letting the Story Manager freely
stack multiple instances of near-identical "go fetch/kill/steal something
generic" content simultaneously. This is a hand-authored throttle layered on
top of the general Story Manager mechanisms in `story_manager_weighting.md`
— a concrete precedent for "even with cooldowns and round-robin pooling,
sometimes you still need a hard concurrency cap on a whole category," not
just per-node "Max concurrent quests."

---

## 2. Fallout 4's radiant quest catalog

Fallout 4's Creation Kit tags an explicit **"radiant quests"** section per
faction in the shipped quest list (confirmed directly from the Fallout Wiki's
quest index, which itemizes the game's 191 base-game / 272 with-DLC quests
by category as the game itself categorizes them, not a fan taxonomy).

### The Minutemen (largest radiant pool — tied to the settlement system)
Given by Preston Garvey, Radio Freedom, or "a local settler," almost always
scoped to **"Radiant [owned] settlement"** as the location type:
- *Defend (Location Name)* — settlement-defense (four separate quest
  variants: `MinRadiantOwned01/05/08/11`, plus a BoS-flavored artillery
  variant `MinRadiantOwned04_BOS`) — this is the specific, well-documented
  "settlement needs defending" quest family (see `known_limitations.md` for
  its reception).
- *Clearing the Way for (Location Name)* — clear a location to make it
  available as a new settlement.
- *Kidnapped Trader at (Location Name)* / *Kidnapping at (Location Name)* —
  rescue-flavored.
- *Raider Troubles / Stop the Raiding at (Location Name)* — clear-hostiles.
- *Ghoul Problem at (Location Name)* — Greenskins — creature-clear variants
  keyed to enemy type.
- *Rogue Courser at (Location Name)* — a specific enemy-type variant using a
  named unique enemy archetype rather than a generic pool.
- *Resettle Refugees* / *Taking Point* — settlement-growth/expansion
  flavored, rewarding a *new* settlement becoming available.
- *Suspected Synth at (Location Name)* — investigation-flavored.
- *(Resource Name) for (Location Name)* / *Power for (Location Name)* —
  resource-logistics flavored, tied to the settlement-building system.

### Brotherhood of Steel (smaller radiant pool, resource-supply flavored)
- *Cleansing the Commonwealth* — clear a radiant hostile location.
- *Feeding the Troops* — supply/fetch.
- *Leading by Example*, *Learning Curve*, *Quartermastery* — fetch/retrieve
  variants, each tied to a specific named quest-giver (Proctor Teagan,
  Lancer Captain Kells, Proctor Quinlan, Scribe Haylen respectively) rather
  than a random innkeeper-style pool — Brotherhood radiant content is
  explicitly gated by faction rank/quest-giver identity, not open to "any
  NPC of this type."

### The Railroad (investigation/retrieval flavored, P.A.M.-driven)
- *A Clean Equation*, *High Ground*, *Concierge*, *Jackpot*, *Lost Soul*,
  *Variable Removal*, *Weathervane* — each a fetch/rescue/assassination
  variant at a **"Random location,"** several explicitly given by the
  faction's analysis-computer NPC **P.A.M.** rather than a person — a
  distinctive Railroad framing device (an in-fiction "algorithm assigns your
  next job" quest-giver, which is a striking, on-the-nose parallel to what a
  radiant system actually is).

### The Institute
- *Appropriation*, *Hypothesis*, *Pest Control*, *Reclamation* — fetch/clear
  variants at "Radiant location," each again tied to a specific named
  quest-giver (faction scientists), not a random pool.
- *Political Leanings* — a Diamond City-specific radiant variant tied to
  Institute infiltration/politics rather than combat.

### DLC-added radiant pools (documented growth pattern)
- **Automatron**: *Rogue Robot* — a single radiant template instanced with
  three separate faction-flavored variants (`_Min`, `_Inst`, `_BOS`),
  demonstrating the same quest concept being cheaply re-skinned per faction
  via alias/condition branching rather than three separately authored
  quests.
- **Far Harbor**: *Condensers Down*, *Deadliest Catch*, *Super Mutants in
  the Fog*, *Trapper Attack* — settlement-defense analogues for the DLC's
  own settlement system, keyed to "a settlement on the Island."
- **Nuka-World** (raider-faction radiant content, a notably different flavor
  — the player runs raider gangs rather than defending settlers): *A Goods
  Defense*, *A Permanent Solution*, *Cache-ing In*, *Capture (Location
  Name)*, *Collaring Outside the Lines*, *Shake Down*, *Subdue*, *Taking out
  the Trash*, *Under the Collar* — a full parallel radiant catalog
  (protect/kill/steal/capture/extort) reusing the same underlying quest
  *shapes* (clear, retrieve, kill, protect) but reframed for an antagonist
  faction, given by named raider bosses (Mags Black, Mason, Nisha, Shank)
  rather than a generic settler pool.

### The real category taxonomy, abstracted across both games
Collapsing the concrete lists above, the actual recurring **quest shapes**
Bethesda reuses (confirmed as the same handful of templates re-skinned per
faction, exactly as the alias system in `alias_system.md` predicts) are:

| Shape | Skyrim examples | Fallout 4 examples |
|---|---|---|
| **Clear** (kill everything at a hostile location) | Trouble in Skyrim, Bounty: Bandit Boss/Forsworn/Giant | Raider Troubles, Cleansing the Commonwealth, Rogue Robot |
| **Retrieve** (fetch a specific/randomized item from a location) | Family Heirloom, Dungeon Delving, Fetch me that Book | Feeding the Troops, Learning Curve, Cache-ing In |
| **Kill** (assassinate/eliminate a specific named or type-matched target) | The Dark Brotherhood Forever, Striking the Heart | A Permanent Solution, Taking out the Trash, Rogue Courser |
| **Protect / Defend** (hold a location against an attack) | (less common in base Skyrim; Civil War quests use an analogous pattern) | Defend (Location Name) — the whole `MinRadiantOwned0x` family |
| **Rescue** (retrieve a captive NPC) | Rescue Mission, Bandit Attack (Hearthfire) | Kidnapped Trader, Kidnapping at (Location Name) |
| **Steal / Property crime** | The Heist/Sweep/Shill/Burglary/Bedlam/Numbers/Fishing Jobs (Thieves Guild) | Cache-ing In, Shake Down (Nuka-World raider variants) |
| **Investigate / Deliver / Favor** (low-stakes social fetch) | A Few Words with You, Delivery, Rare Gifts, Some Light Theft | Political Leanings, Concierge |
| **Settlement growth/logistics** (no direct FO equivalent in Skyrim) | — | Clearing the Way, Resettle Refugees, Power/Resource for (Location) |

This table is the single most directly reusable artifact in this research
pass for our own engine: **a small, fixed library of quest "shapes"
(clear/retrieve/kill/protect/rescue/steal/favor/logistics), each
independently re-skinnable per faction or per context by swapping which
aliases, conditions, and flavor text get plugged in** — not a large bespoke
catalog of unique quest designs. Both Skyrim and Fallout 4 ship dozens of
*named* radiant quests that are really a much smaller number of *shapes*
wearing different faction clothing.

---

## Sources

- [Skyrim:Radiant – UESP Wiki](https://en.uesp.net/wiki/Skyrim:Radiant) — full itemized list of Skyrim's radiant quests, their possible-location and possible-NPC pools (with counts), the "cannot create large, complicated, or particularly interesting quests" assessment, and the documented mutual-exclusion rule for the generic misc-quest pool.
- [Fallout 4 quests – Fallout Wiki (Fandom)](https://fallout.fandom.com/wiki/Fallout_4_quests) — the game's own as-shipped quest index, itemizing every faction's Main/Side/Radiant quest sections (Minutemen, Brotherhood of Steel, Railroad, Institute, and the Automatron/Far Harbor/Nuka-World DLC radiant pools), including quest givers and Editor IDs confirming the `MinRadiantOwned`/`_RQ_`/`Radiant` naming conventions used internally by Bethesda's own designers.
