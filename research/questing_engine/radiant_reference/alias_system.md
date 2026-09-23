# The Alias System: How Creation Engine Quests Avoid Hard References

Research focus: the mechanic at the center of Bethesda's Radiant Story — quests
in Skyrim/Fallout 4 do not point at specific NPCs, items, or places. They point
at abstract roles ("aliases"), and the engine fills those roles with real,
currently-eligible world objects at the moment the quest starts. This is the
single most important structural idea for a procedural quest engine to borrow,
independent of any narrative content.

Primary source for this file: Bethesda's own Creation Kit documentation for
Skyrim (mirrored by UESP at ck.uesp.net, "a copy of the original Skyrim CK wiki
created and maintained by the UESP.net") — specifically the `Quest Alias Tab`,
`Radiant Story`, and `Story Manager` pages. This is developer-authored
reference documentation, not fan inference — it is the literal tooltip/manual
text Bethesda shipped to its own designers and to modders.

---

## 1. The core idea, in Bethesda's own words

From the Creation Kit wiki's `Radiant Story` overview page:

> "An Alias is a Reference or a Location used by a Quest. It can be assigned a
> discrete value, or it can be 'filled' by picking from a random list of
> references and locations in the world, or it can create a brand new
> reference from a leveled list, or it can even grab the alias from another
> quest."

And the analogy Bethesda's own documentation uses to explain it to new
designers — this is worth preserving close to verbatim because it is exactly
the mental model our own engine should adopt:

> "If the game was a movie, then the Quest would be the screenplay, its
> aliases would be the roles, props, and locations, and the game would be a
> procrastinating producer who could decide just as the movie starts rolling,
> which actor to cast for each role, which item would become each prop, and
> which locations to use."

> "Dialogue can be conditioned for aliases rather than specific NPCs, and
> Packages can be given to aliases rather than specific NPCs, so that any
> actor can 'step into the role' of an alias in a quest."

This is the mechanism that makes the same quest *design* (screenplay) produce
a different concrete *playthrough* (cast) every time: nothing about the
quest's data references a specific NPC ID. Every script, every conditioned
dialogue line, every scheduling package is written against the alias name
("Bandit Leader," "Victim's Brother," "Questgiver") and the engine's
alias-filling logic decides at runtime which real actor/object/location
answers to that name. Design-time and runtime are cleanly separated: the
designer writes the role and its eligibility rules once; the engine casts it
fresh every time the quest instance starts.

The CK wiki explicitly notes that this isn't reserved for throwaway
content — "even in very controlled stories, like the Main Quest, or Guild
questlines, aspects of certain stories are dynamic." The alias system is not
a "cheap content" special case bolted onto hand-authored writing; it is the
same underlying plumbing used everywhere, dialed from "one specific NPC and no
alternatives" up through "any of eighteen eligible bandit bosses" as needed
per quest.

---

## 2. The two kinds of alias

Aliases are "names or tags assigned to actors, objects, and locations used by
the quest," letting quest data (scripts, packages, dialogue) be tagged to a
*role* rather than a specific object in the world. There are exactly two
alias types:

### Reference Aliases
Bound to an **Object Reference** at quest start — any actor or any physical
object (an NPC, an item, a container, a lootable corpse, a door). Reference
aliases can carry:
- **Factions** — the reference is treated as a member of the listed
  faction(s) *while it occupies the alias*, and the membership is
  automatically stripped when the alias clears, even if another still-running
  quest also has that same actor in a faction-granting alias. (This is a
  clean, engine-guaranteed cleanup rule worth copying directly — temporary
  faction membership tied to alias occupancy, not to a flag someone has to
  remember to unset.)
- **Spells** (including Shouts), added on entry and removed on exit.
- **Keywords**, held only while in the alias.
- **Inventory items** — added permanently when the reference fills the alias
  (these are *not* removed when the reference later leaves the alias).
- **Package Data** — an additional AI schedule "stack" layered on top of the
  actor's normal behavior packages, specifically so a generic NPC's normal
  daily routine can be temporarily overridden ("go stand at the quest
  marker and wait") only while it holds this quest role, and automatically
  revert once the quest alias clears.

### Location Aliases
Bound to a **Location** (Bethesda's location-graph object, roughly "a
tagged, boundaried place" — a dungeon, a hold, a city district) rather than a
physical reference. Used for "send the player to *a* bandit camp" without the
designer choosing which camp in the editor.

Aliases are filled **in a strict, designer-defined order** (top to bottom of
the alias list), and later aliases can be made conditionally dependent on
earlier ones — the CK wiki's own examples: *"Questgiver is Victim's Brother;
Treasure is Collector's Owned Item."* This ordering constraint is important
and easy to miss: an alias can only reference something *already filled*
earlier in the list, never something below it. This is effectively a
dependency-resolution pass with a fixed, author-controlled topological order
rather than a general constraint solver — a deliberately simpler, more
predictable design than a full constraint-satisfaction search.

---

## 3. Fill types — the actual mechanisms for "find something that fits"

For **Reference Aliases**, the CK wiki documents six fill types:

1. **Specific Reference** — a literal, hand-picked object (the escape hatch
   for genuinely unique content; the wiki warns this can pin the reference
   permanently into memory, a real performance cost worth flagging for our
   own engine too — don't make "just hardcode it" free).
2. **Unique Actor** — pick a specific *named/unique* actor (not a pool);
   requires that actor to have a "Persist Location" assigned.
3. **Location Alias Reference** — pull a reference *out of* a location
   already bound to a Location Alias higher in this quest's list (e.g. "the
   innkeeper of whichever inn the Location Alias resolved to").
4. **External Alias Reference** — reach into *another running quest's* alias
   and borrow whatever it currently holds. This is the mechanism for
   quest-to-quest continuity (e.g. a follow-up quest automatically inherits
   "the same bandit leader" or "the same rescued NPC" from the quest that
   preceded it) without either quest hardcoding the other's target.
5. **Create Reference to Object** — spawn a brand-new object instance (often
   from a leveled/randomized list) at another alias's location, or into
   another alias's inventory if that alias is a container. This is how
   "a randomized magical weapon appears in the boss chest of whichever
   dungeon got picked" works — the *item* is generated fresh, not selected
   from a pre-placed pool.
6. **Find Matching Reference** — the general-purpose "search the world" fill
   type: the Story Manager searches for **any** reference satisfying a
   **Match Conditions** list (arbitrary condition functions — see Section 4).
   Can be restricted to "In Loaded Area" (the player's currently-loaded
   cells — useful for "someone standing near the player right now"), can
   prefer the "Closest" match, can source its input from the triggering
   **Event**'s data, or can search only among references *linked to* another
   already-filled alias.

For **Location Aliases**, four fill types: **Specific Location**, **Reference
Alias Location** (derive the location from wherever a reference alias ended
up, optionally walking up to a parent location via a keyword), **External
Alias Location** (borrow from another quest, same pattern as reference
aliases), and **Find Matching Location** (search all Locations in the game
against a condition list, or validate a location supplied by a triggering
event).

**The load-bearing design point**: five of the six/four fill types are some
flavor of "point at something else, whether specific, inherited, or found by
search" — only one is a true blind random search of the whole world (Find
Matching Reference / Find Matching Location with no Near/Event/Loaded-Area
restriction). In practice, most radiant content is a **short chain of
narrower and narrower lookups** (find a location matching a condition → find
an NPC *at* that location matching a condition → find an item *owned by* that
NPC), not one global unconstrained search. This is a strong, concrete
argument for our engine: build alias-filling as a small library of
composable narrowing operations (by-location, by-relationship-to-existing-
alias, by-faction, by-condition-search), not a single monolithic "pick a
random valid NPC" function.

---

## 4. How conditions actually filter — "Match Conditions"

The "Find Matching Reference" / "Find Matching Location" fill types run an
arbitrary list of **condition functions** (the same condition-function system
Bethesda uses everywhere else in the engine — dialogue conditions, quest
stage conditions, AI package conditions) against every candidate. Documented
condition functions and patterns found in this research pass:

- `GetInCurrentLoc` — is the candidate physically inside a given Location.
- `GetInWorldspace` — is the candidate in a given worldspace (used, per the
  CK wiki's own worked example, to *exclude* a city's building interiors when
  you only want NPCs standing in the fields immediately outside its walls —
  a real documented gotcha: a location and its "inside a nearby building"
  space can both nominally satisfy `GetInCurrentLoc`, so a second condition
  is needed to disambiguate).
- `GetInFaction` — faction membership (used heavily for "any bandit," "any
  guard," "any member of the Thieves Guild" style eligibility).
- `LocationHasRefType` — does a Location contain an object of a given
  "location ref type" tag (explicitly documented to return false for dead or
  disabled ref types — dead NPCs and disabled objects don't silently pass).
- `GetEventData` — a special condition specifically for pulling typed fields
  (which actor, which location, whether a death was a witnessed murder,
  etc.) out of the Story Manager Event that triggered this quest attempt, so
  conditions can react to *this specific trigger* and not just static world
  state.
- Arbitrary Papyrus script conditions, including custom `GetIsAliasRef`-style
  checks for validating dialogue against a resolved alias's voice type.

Conditions can be layered on **any** fill type (not only "Find Matching"),
but which reference the condition actually runs against differs by fill type:
for *Specific Reference*, *External Alias Reference*, and *Find Matching
Reference*, the condition runs **against the candidate object itself**; for
*Unique Actor*, *Location Alias Reference*, and *Create Reference*, there is
no loaded candidate to test yet, so the condition instead runs **against the
player** (used for things like "only offer this alias if the player's level
is in range," since the object doesn't exist yet to be tested).

This is a genuinely important nuance for anyone implementing an equivalent
system: **"a condition on an alias" is not one uniform operation** — its
semantics (what it actually evaluates against) depend on *how* that alias is
being filled. A generic clone of this system needs to make that branch
explicit, not assume "conditions filter candidates" is always true.

---

## 5. Alias flags — the fine-grained control knobs

The Reference Alias checkboxes are effectively a small rules-engine for
edge cases that any "find something that fits" system runs into immediately.
Worth enumerating because each one maps to a real failure mode a naive
implementation would hit:

- **Optional** — if unchecked, failing to fill this alias fails the *entire
  quest's* start. This is the mechanism that prevents a Radiant Story quest
  from silently starting in a broken, half-cast state — a missing required
  role aborts the whole quest attempt rather than shipping a quest with a
  hole in it.
- **Allow Dead / Allow Disabled / Allow Destroyed** — by default, dead,
  disabled, or destroyed references are excluded from candidacy; each must
  be explicitly opted back in per-alias. This is a safe-by-default posture:
  the engine assumes you don't want a corpse cast as your quest's living
  bandit boss unless you say so.
- **Allow Reuse in Quest** — by default, the *same* quest will not fill two
  different aliases with the same reference (you can't have "Victim" and
  "Victim's Brother" silently resolve to the same NPC); must be explicitly
  allowed per-alias when that's actually desired.
- **Essential / Protected / Quest Object** — status flags applied *only
  while occupying the alias* (e.g., a randomly-selected quest-critical NPC
  is made unkillable/unsellable-item-holder only for the duration it's
  filling that role, then reverts).

### Cross-quest conflict resolution — "Reserves Reference" / "Allow Reserved"

This is the direct, documented answer to "what happens when multiple quests
want the same NPC":

- An alias can be flagged **Reserves Reference**. Once some quest fills a
  Reserved alias with a given reference, **no other quest's alias may claim
  that same reference** unless the *other* alias is explicitly flagged
  **Allow Reserved** (or is filled via an *External Alias Reference*, which
  bypasses reservation because it's deliberately borrowing a specific
  already-claimed alias on purpose, not searching blind).
- **Start Game Enabled** quests (ones that begin automatically at the start
  of a new game) implicitly treat *all* their own aliases as "Allow
  Reserved" — this exists specifically to avoid a race condition where the
  arbitrary order that different game-start quests initialize in would
  otherwise change which quest "wins" a shared NPC. The wiki flags a real
  caveat here too: this implicit exemption does *not* automatically apply
  if a Start-Game-Enabled quest is instead injected into an already-running
  save later (e.g., by a DLC/patch), and documents the manual keyboard
  workaround (Ctrl+Shift+R) designers use to force the flag on retroactively.
- Locations have the exact same **Reserves Location / Allow Reserved**
  pattern for Location Aliases.

**The general shape of the rule**: reservation is *opt-in per claim, and
opt-out (bypass) per consumer* — a quest doesn't get automatic exclusive
custody of an NPC just by using it; a designer has to actively mark "this
role should lock its occupant out of other quests," and other quests have to
actively mark "I'm allowed to ignore that lock." This keeps the default
behavior permissive (most alias fills don't fight over resources) while
giving designers an explicit tool for the cases where two quests
*shouldn't* be able to grab the same person (e.g., you don't want your
"protect this NPC" quest's target simultaneously cast as another quest's
disposable kill-target).

### Same-actor, multiple simultaneous roles

Reservation aside, the system explicitly supports one NPC filling aliases in
*several different running quests at once* — the Factions section documents
exactly this scenario: two quests both add the same actor to
`ThievesGuildFaction` via their respective aliases; when the first quest
stops, the engine removes that faction grant even though the second quest
(still running, still holding that actor in its own alias) also nominally
grants it. The system tracks grants *per-alias-occupancy*, not as a simple
reference-counted flag, so "quest A ends" cleanly retracts exactly what quest
A granted without clobbering what quest B independently granted to the same
actor.

---

## 6. Why this makes the same quest template produce a different concrete
   experience every playthrough

Putting Sections 1-5 together, the mechanism is:

1. A quest's *design* (aliases + fill rules + conditions + scripts/packages/
   dialogue keyed to alias names) is authored exactly once and is entirely
   free of specific-object references, except where a designer deliberately
   pins something (Specific Reference/Location — the escape hatch, used
   sparingly).
2. At the moment a quest instance actually starts, the Story Manager resolves
   every alias top-to-bottom, running each one's fill logic against the
   *current, live state of the world* — which NPCs are alive, where they
   currently are, what factions they currently belong to, what's already
   reserved by other running quests, what the player's own state is.
3. Because that live world state is different every playthrough (different
   NPCs died differently, different locations got cleared in a different
   order, different quests are mid-flight holding different reservations),
   the *same* quest template resolves to a genuinely different concrete cast
   and location set each time it's instanced — without any of that
   variation being hand-authored per-instance.
4. Packages and dialogue conditioned on the *alias* rather than the
   underlying actor mean the presentation layer (what the NPC does, what it
   says) automatically follows whichever actor got cast, with no per-actor
   authoring required beyond writing dialogue conditions that check the
   alias's resolved properties (voice type, faction, etc.) rather than a
   specific actor ID.

This is the mechanical answer to "how does the same screenplay produce a
different movie" — the casting call runs fresh, against the current state of
the company, every time the show goes up.

---

## Sources

- [Category:Radiant Story – the CreationKit Wiki (ck.uesp.net, a UESP-maintained copy of Bethesda's original Skyrim Creation Kit wiki)](https://ck.uesp.net/wiki/Category:Radiant_Story) — the movie-producer alias analogy, Scenes, Story Manager overview, and worked examples of radiant content quoted/summarized above.
- [Quest Alias Tab – the CreationKit Wiki](https://ck.uesp.net/wiki/Quest_Alias_Tab) — the primary source for Sections 2-5: Reference Alias vs. Location Alias data fields, all six/four fill types, Match Conditions semantics, and the Reserved/Allow Reserved/Allow Reuse conflict-resolution flags.
- [CreationKit:Quests – the CreationKit Wiki](https://ck.uesp.net/wiki/CreationKit:Quests) — index of the Quest editor's tabs (Alias Tab, Scenes Tab, etc.), confirming aliases are one part of a larger quest-authoring surface.
- [Five Changes from Oblivion to Skyrim – IGN (Charles Onyett, Apr 26 2011)](https://www.ign.com/articles/2011/04/26/five-changes-from-oblivion-to-skyrim) — Todd Howard, in his own words, describing alias-casting intent for a "bigger quest": *"We want somebody who you're enemies with. We want to use him in that quest in some way. We'll pick the closest person who hates the player. He fills in that role."*
