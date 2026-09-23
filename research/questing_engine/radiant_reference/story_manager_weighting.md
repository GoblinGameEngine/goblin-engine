# The Story Manager: Selecting Which Quest Fires Next

Research focus: the decision layer that sits *above* the alias system (see
`alias_system.md`) — the piece of Radiant Story that decides **which** quest
or quest category gets a chance to start at all, in response to what the
player just did, how it weighs competing candidates, and how it avoids
staleness/repetition. Primary source: Bethesda's own Creation Kit
documentation (ck.uesp.net, the UESP-maintained copy of the original Skyrim
CK wiki) for `Story Manager` and `SM Event Node`.

---

## 1. What triggers the Story Manager at all: Events

The Story Manager is **event-driven**, not polled or ticked. It does nothing
until the game generates one of a fixed set of **Story Manager Events** —
documented events include: Actor Dialogue, Actor Hello, Arrest, Assault
Actor, Bribe, Cast Magic, **Change Location**, Change Relationship Rank,
Craft Item, Crime Gold, Dead Body, Escape Jail, Flatter, Increase Level,
Intimidate, Jail, **Kill Actor**, Lock Pick, New Voice Power, Pay Fine,
PickPocket, Player Activate Actor, Player Add Item, Player Cured, Player
Infected, Player Receives Favor, Player Remove Item, Script Event, Served
Time, Skill Increase, Trespass Actor.

Each event carries typed **Event Data** specific to what happened — e.g. the
Kill Actor event carries the victim, the killer, and whether the death is
flagged as a known murder; the Change Location event carries the old and new
Location. This event data is what feeds the alias-filling and node-condition
logic downstream (see `alias_system.md` Section 4 for `GetEventData`).

This event-driven design is itself a load-bearing choice: **the Story
Manager only ever gets a chance to act at a meaningful narrative moment**
(something changed — the player moved, someone died, a relationship
shifted), not on a fixed timer. Radiant content is reactive to player
behavior by construction, not merely randomized on a clock.

---

## 2. The decision tree: Event Nodes → Branch Nodes → Quest Nodes → Quests

The Story Manager is described as "a nested node tree that holds all of the
radiant story quests." Structurally, for each Event type there is one **SM
Event Node**, itself a decision tree of four node kinds:

1. **Event Node** (the root, one per event type) — processed first; if its
   own **Node Conditions** pass (or it has none), the Story Manager proceeds
   into its children.
2. **Branch Node** — a pure grouping/logic node: contains further Branch
   Nodes or Quest Nodes, gated by its own Node Conditions. Exists purely to
   let designers factor out shared conditions across a group of quests
   (e.g., "all of these only apply if it's currently in the Rift hold")
   without repeating that condition on every leaf.
3. **Quest Node** — a container of specific candidate **Quests**. When
   processed, it attempts to start exactly one (or more, see Section 4)
   quest from its contents.
4. **Quest** (leaf) — the actual quest asset, with its own Node Conditions
   and a **"Hours until reset"** cooldown value (Section 5).

Both Branch Nodes and Quest Nodes carry a **Random / Stacked** selection
mode:

- **Stacked**: children are evaluated strictly top-to-bottom, in the order
  the designer listed them. The first child whose Node Conditions pass is
  the one used.
- **Random**: children are evaluated in random order until one with passing
  conditions is found.

This is the whole of Bethesda's documented "weighting" mechanism, and it is
worth being precise about what it is *not*: there is no numeric weight field
on a node (no "40% chance of category A, 60% of category B"). Weighting is
achieved entirely through **(a) which mode a node uses (Random vs. Stacked)**
and **(b) how many eligible candidates exist at each node at evaluation
time**, which is itself controlled by how narrowly or broadly each
candidate's own Node Conditions are written. A designer who wants category A
to fire more often than category B doesn't set a probability — they either
put more distinct quest variants of category A into the pool (so it wins
more Random draws by sheer candidate count) or use Stacked ordering with
priority-ordered fallback (try the "special"/rare version first, fall
through to the generic version only if it's ineligible).

**This is a genuinely important finding for our own design**: Bethesda's
real, shipped weighting mechanism is closer to *"structured random draw over
whatever currently passes its eligibility filter, with author-controlled
tree shape and list order"* than to a general numeric-weight scheduler. The
"weighting" a category feels like it has, in practice, comes from world-state
eligibility (are there any valid candidates at all right now?) far more than
from any deliberately tuned probability curve.

If no child at a node has passing conditions, nothing starts from that node
— and Branch/Quest Nodes both have an optional **"Warn if no child quest
started"** flag for catching that case during development (a diagnostic, not
a runtime fallback).

---

## 3. World-state gating: eligibility as the *real* selection mechanism

Every level of the tree — Event Node, Branch Node, Quest Node, and the
individual Quest — carries its own **Node Conditions**, and a node's entire
subtree is skipped if its own conditions fail. This is exactly the mechanism
the user's brief calls out by name: *"don't offer a 'clear out bandits'
quest if no eligible bandit-type location exists nearby."*

Concretely, this is implemented the same way alias Match Conditions are (see
`alias_system.md` Section 4) — arbitrary condition functions, including
`GetEventData` to react to specifics of the triggering event, and (per the
alias documentation) conditions like `LocationHasRefType` that explicitly
return false for dead/disabled candidates rather than silently matching
anything. In practice this means "is there an eligible target for this
quest type" is answered the same way a specific alias asks "is there an
eligible NPC for this role" — a condition-filtered search, not a hardcoded
assumption that the content always exists somewhere.

A quest that has *no* eligible alias fills at all will fail to start
entirely (see `alias_system.md` Section 5, the "Optional" flag) — so even if
a Quest Node's own Node Conditions pass, the Story Manager can still end up
starting nothing if the chosen quest can't actually cast its required roles.
The system therefore has **two independent layers of eligibility checking**:
tree-level Node Conditions (should this quest even be attempted) and
alias-level Match Conditions/fill logic (can this quest, once attempted,
actually find everything it needs). Both must pass for content to appear.

---

## 4. Starting more than one quest from a single event

By default, once the Story Manager starts a quest in response to an event,
**that event is considered "consumed"** and processing stops — one event,
at most one quest. Two documented ways to deliberately break that default:

- **"Shares Event"** (a Quest Node flag): if checked, after this node is
  processed the Story Manager *continues* on to the next node in the list
  instead of stopping, allowing several different Quest Nodes to each get a
  shot at starting something off the same single triggering event. The CK
  wiki's own "Known Issues" note is an explicit compatibility warning: nodes
  *without* "Shares Event" must be placed *after* all "Shares Event" nodes in
  a shared event tree, or one mod's non-sharing node will silently swallow
  the event before other content (including other mods') gets a chance to
  react to it. This is a real, documented pitfall of chaining reactive
  systems on a shared event bus — worth taking seriously if our own engine
  lets multiple independent quest generators subscribe to the same world
  event.
- **"Num quests to run"** (a Quest Node field): if checked, the Story
  Manager attempts to start *every* quest inside that specific node, up to
  the given count — starting as many as it validly can if there aren't
  enough eligible quests to hit the target number.
- **"Max concurrent quests"** (a Quest Node field): a hard cap on how many
  quests *from this node specifically* may be simultaneously running at
  once — the Story Manager will refuse to start another from that node once
  the cap is reached, independent of whether new triggering events keep
  arriving.

---

## 5. Avoiding staleness and repetition

Two distinct, separately documented anti-repetition mechanisms exist at the
Quest Node / Quest level, and they solve two different problems:

### "Hours until reset" — per-quest cooldown
A field on the individual **Quest** node: once this quest has been started,
the Story Manager will not attempt to start it again until the given number
of **in-game hours** has passed (a value of 0 disables the check). This is
the direct cooldown-period mechanism: it prevents the *same specific radiant
quest asset* from re-firing back-to-back, independent of anything else in
the tree.

### "Do all before repeating" — round-robin exhaustion, not just cooldown
A field on the **Quest Node** (the container, not the individual quest): if
checked, the Story Manager will attempt to start *every quest in the node
at least once* before it will start any quest in that node a second time.
This is meaningfully different from a per-quest cooldown timer — it's a
**round-robin exhaustion policy** that guarantees variety across the *whole
pool* rather than merely spacing out any one specific quest. A pool of, say,
five miscellaneous "innkeeper job" quest variants with this flag set will
visibly cycle through all five before any one repeats, regardless of how the
random draw would otherwise weight them.

Taken together, these give Bethesda's designers two independently tunable
anti-repetition knobs: *how long before this exact thing can happen again*
(cooldown) and *how much of the pool must be seen before anything repeats*
(round-robin). Neither is "already completed with this NPC" tracking in the
literal sense the brief asks about — that specific behavior is instead
implemented at the **alias-reservation** layer (see `alias_system.md`
Section 5's Reserves Reference / Allow Reserved mechanism, plus the
`External Alias Reference` fill type used for direct quest-to-quest
continuity) and via ordinary condition functions checking relationship rank
or quest-completion global variables against a candidate NPC before it's
allowed to fill an alias — i.e., "don't offer this quest with this NPC
again" is authored as an ordinary eligibility condition on the *alias*, not
as a separate bespoke history-tracking subsystem bolted onto the Story
Manager.

---

## 6. Putting it together: what "the Story Manager decides" actually means

Collapsing Sections 1-5 into the shape a procedural quest engine should
copy:

1. **React to events, don't poll.** Only evaluate the decision tree when
   something narratively meaningful just happened, carrying typed data
   about what happened.
2. **Structure candidates as a tree of increasingly specific eligibility
   filters**, not a single flat weighted table. Shared conditions get
   factored into Branch Nodes; the leaf-level choice is a *shallow* random
   or ordered pick among whatever's left standing after filtering.
3. **Let "how many eligible candidates survive filtering" do most of the
   weighting work**, rather than authoring explicit probabilities.
   Stacked/priority ordering is reserved for genuine "prefer the special
   version, fall back to generic" cases.
4. **Gate eligibility twice**: once at the tree level (should this category
   even be attempted, given current world state) and once at the alias
   level (can this specific instance actually cast everything it needs).
   A quest category can pass the first check and still silently fail to
   produce content if the second check comes up empty — this is a feature,
   not a bug, and prevents ever surfacing a quest that can't actually be
   completed.
5. **Separate the two different anti-repetition needs**: a *time-based*
   cooldown per specific piece of content, and a *pool-exhaustion* policy
   that forces variety across a category before anything in it repeats.
   Track "already did this with this specific NPC" as an ordinary
   eligibility condition on the alias-filling step, not as a separate
   system.
6. **Make "no eligible content" a legitimate, expected outcome** at every
   level, with a diagnostic warning available for designers/generators to
   catch categories that silently never produce anything — never assume a
   category's content always exists somewhere in the world.

---

## Sources

- [Category:Story Manager – the CreationKit Wiki (ck.uesp.net)](https://ck.uesp.net/wiki/Category:Story_Manager) — Overview, node types, "How the Story Manager Works" (Triggering an Event / Starting a Quest / Starting Multiple Quests), and the full list of 24+ documented Story Manager Events.
- [SM Event Node – the CreationKit Wiki](https://ck.uesp.net/wiki/SM_Event_Node) — full node-property reference: Random/Stacked, Num quests to run, Max concurrent quests, Do all before repeating, Shares Event, Hours until reset, and the documented mod-compatibility "Known Issue" around Shares Event ordering.
- [Category:Radiant Story – the CreationKit Wiki](https://ck.uesp.net/wiki/Category:Radiant_Story) — Story Manager summary description ("a nested node tree... used to determine which quest or quests are started as a result of receiving a Story Manager Event").
- Cross-reference: `alias_system.md` in this same directory — Section 4 (Match Conditions / condition functions) and Section 5 (Reserves Reference / Allow Reserved) for the alias-level eligibility and reservation mechanics this file builds on.
