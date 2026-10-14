# 3. The Aloft: how the society works

Canon data: sky_islands.json → `confederation`, `clans`, `governance`, `customs`, `faiths`, `physiology`, `plumb`,
`faction_stance`, and each island's `governance`, `customs`, `faith`, `heritage`, `clan`.

## The shape of it: a trade diaspora that flies
- The closest real models are maritime peoples who live on the move, and merchant networks with no capital.
- **Sea nomads.**
  - The Bajau Laut and the Moken live largely on boats. The Moken kabang is home, kitchen and bedroom; they spend the
    dry season at sea and shelter on land in the monsoon [1][2].
  - Generations of diving have even shaped the Bajau's bodies: larger spleens, with a genetic basis [3].
  - Lesson: a people can live on a moving home for generations, meet the land mostly to trade, and keep an identity
    sharply apart from the shore people.
- **The Uros of Lake Titicaca** live on islands they make. The reed floats rot from below and are re-laid from the top
  every few months, and an island lasts about thirty years [4].
  - Lesson: a home that needs constant upkeep makes upkeep the culture.
  - The Aloft's riggers, envelope wrights and gas makers are what the Uros' reed-cutters are.
- **The Hanseatic League** was a loose confederation of trading cities with no permanent administration, treasury or
  army. Its irregular Diet's decisions bound only the towns that accepted them, and its kontors abroad had their own
  law [5][6].
  - This is the model for **the Skein**: no capital, no flag, a moot when islands meet, and custom that binds only
    because everyone keeps it.
- **Trade diasporas.** Curtin describes merchants who live for generations among host peoples as cross-cultural
  brokers [7].
  - The **plumbs** are a trade diaspora of one: each clan's single broker to the floor.
- **Polynesian wayfinding** read swells, clouds, birds, sun and stars, with no instruments [8].
  - This is the model for the **weather readers**: the island goes where the wind goes, and the reader knows where that
    is.

## Why they live aloft (and rarely come down)
1. **They can't easily get back up.**
   - Since VY 301 the hulks are never lowered. Until VY 417, going up meant riding a cargo container up a 750 m hoist
     line.
   - Even now, the larks carry two people.
   - A child born aloft may never stand on the floor until they are carried down dead (the **Long Drop**, a custom on
     many islands).
2. **Weight is life.** Every person is ~70 kg of lift. An island can't take in more people than its lift allows, so
   people don't come and go lightly.
   - Births are counted against the weight book, as the floor counts birth shares: *a child is ballast, and a
     blessing*.
3. **Ground-weight.** On the floor the Aloft feel 12% heavier. The young get **ground-sickness**: heavy limbs,
   dizziness and homesickness.
4. **The bargain.** The hulks fly because people keep them flying. Abandon an island, and it and its Box come down.
5. **Pride and freedom.**
   - Aloft there is no Assembly, no Marshal, no Registry and no Draw: the Aloft are free and also on their own.
   - The floor's Draw guarantees food and a home. The Aloft have the weight book, the long kitchen and each other.

## The clan and the island
- **One island, one clan.** Each boarding group became a clan named for a founding surname: *the Okafor kin*.
  - Everyone born to the clan keeps its name.
  - Heritage mixes (Polish, Lake Spanish, Carrow French, Black Lakes English and more) come from the founders and drift
    across bridges.
  - A small share of clans have sky-coined names (*the Dandelionkin*).
- **Kin across islands.** Marriage happens at lashings, across a bridge. Every clan has cousin clans
  (`clans[].cousins`), and some have a feud (`clans[].feud`).
  - Whether husbands or wives cross depends on the clan: `matrilocal`, `patrilocal`, or `chosen_island` (at sixteen,
    anyone may cross).
  - So everyone has cousins on a dozen islands, and the Skein holds together by kinship, not law.
- **Governance differs by island** (`governance`). This is deliberate: the Aloft are not a monoculture.
  - **the Helm:** an elected yearly captain who steers the trim.
  - **council_elders:** the Old Lines.
  - **lot:** sortition.
  - **mother_house:** the eldest woman of each line.
  - **guild:** the work-crews.
  - **consensus:** the whole island in the long kitchen.
  - **plumb_rule:** the trading houses.
- **Customs differ by island** (`customs`, two each from 24): cord names, bell-speech, silent dusk, rope-mark tattoos,
  the snow feast, Weighing Day, the Long Drop, kite mail, cloud singing, rail dancing, tether-splice weddings, map
  walls, feather coats and more.

## The Skein and its law
- **The Five Knots** are the only laws every island keeps:
  - the **Weight Knot**;
  - the **Flame Knot** (hydrogen: no open flame; setting a fire is the one crime punished by being put down to the floor
    for good, into the Marshals' hands);
  - the **Line Knot** (no island refuses a lashing to one in distress);
  - the **Ten Knot**;
  - the **Three-Day Knot**.
- Everything else is each island's **knot-law**. Knot keepers keep it in knotted cords and in books, and argue it at
  lashings.
- The Inca's khipukamayuq kept censuses, tribute and genealogies in knotted cords, in a tiered system from local
  keepers up to Cusco, and cord colour, ply and placement carried meaning [9][10].
  - The Aloft's cords are simpler: weight books, lineages and verdicts. But the idea of law and records held in rope
    suits a people who live by rope.

## The lashing (docking) and the moot
- **The sequence:** two islands within 3 km, then bell-speech and doves, then the rockets.
  - Cold rockets (compressed gas: the Flame Knot) carry messenger lines across.
  - Hawsers follow, and winches haul the islands together over an hour or two until the dock faces are 26 m apart.
  - The bridges come down on the facing sides.
- **The Lashing** lasts **three days**. It is a market, a moot, a fair and a wedding season:
  - knot keepers hear disputes;
  - factors trade;
  - the young court, marry and cross;
  - the dead are mourned;
  - plumbs trade the floor's news;
  - the lashing stew is cooked in one pot in the middle.
- **The Casting Off** ("the knives") comes at dusk on the third day. The bridges go up, and the eldest of each island
  cuts the lines with a knife.
- **Why three days:** long enough to trade and marry. Short enough that no island grows used to ruling another, that
  the raft's slower drift doesn't carry it into weather, and that the weight crossing doesn't unbalance anyone.
- **Why ten:** the Great Tangle (VY 388). A raft holds up to ten islands, and a new island may join a raft already
  lashed.

## The plumb
- One per clan at a time, for about seven years, with a **second** who flies behind and learns.
  - A plumb is a trader, a diplomat and a pilot.
  - They book the hoists, buy what the factors ask for, carry letters and bring back news and stories.
- **Aloft** the plumb is honoured and a little pitied: they carry the ground-weight for everyone.
- **Below**, plumbs are glamorous and aloof, with cold hands. Floor children chase their larks.
- **The lark** is the clan's two-person high aerostat: 1.5 km ceiling, 250 km/h. Each island keeps at least two, in
  cradles on its tallest roofs.

## Faith
- **the Sunward** (sky-born): the soul rises toward the Sunline, and the Aloft are halfway there. Its rites are the
  silent dusk and lantern vigils.
- **Floor faiths** are carried up and changed:
  - the Waymakers are strong aloft ("we are on deck");
  - Catholics keep Our Lady of the Winds;
  - Muslims reckon the qibla by the knot keepers' tables;
  - many say "the wind is enough".

## The body (`physiology`)
- **Partial gravity and muscle:** mice kept at 0.67 g on the ISS lost no muscle, and muscle loss scales nearly
  linearly below that [11].
- **Bone:** partial loading reduces bone loss but does not prevent it at 1/6–1/3 g [12].
- At 0.89 g the effect is mild. The Aloft are healthy and only slightly unloaded, so the canon keeps the drift modest:
  - ~3 cm taller on average;
  - lighter-boned and longer-limbed;
  - they feel 12% heavier on the floor;
  - young people get ground-sickness for the first days.
- **The rest is habit:** a head for heights, ease in the cold, wonder and fear at open flame.

## The floor's factions (`faction_stance`)
| faction | stance | why |
|---|---|---|
| Aerostat Pilots' Guild | −0.3 | the Lark Quarrel |
| Marshals | −0.2 | no reach aloft |
| Charter League | −0.25 | "the Charter covers them" |
| Open Hand | +0.3 | fair trade; count them |
| Waymakers | +0.35 | |
| Wardens' circle | +0.25 | Warden blood and books aloft |
| Homeward | ≈ 0 | |
| Grange | +0.2 | forecasts for grain |
| Cannery Union | +0.1 | dock hands at the hoist grounds |

## How the player meets them (hooks, short)
- A plumb at a hoist ground needs a courier, which ties into the Dispatch core loop. The floor end of the air post is
  a rival or a partner.
- A lark crashes in the countryside: rescue the pilot and get invited up.
- Piggledy's wreck in the North Sea.
- The Box: what the Steward's cloud engines really do, and who has opened one.
- The VY 500 Notice raft: the Skein debates the voyage, and a Wardens' circle contact is aboard.
- A youth runs away to the floor, or a floor youth stows away in a skybox.
- A fire-setter is handed down to the Marshals: an innocent?

## Sources
1. [Survival International: the Moken](https://survivalinternational.org/galleries/moken-sea-gypsies)
2. [Learning from the Moken](https://andamandiscoveries.com/learning-from-the-moken/)
3. [National Geographic: Bajau sea nomads and the spleen](https://nationalgeographic.com/science/article/bajau-sea-nomads-free-diving-spleen-science)
4. [Amusing Planet: the floating islands of Lake Titicaca](https://www.amusingplanet.com/2011/10/floating-islands-of-lake-titicaca.html)
5. [History Today: the Hanseatic League](https://www.historytoday.com/archive/feature/hanseatic-league-europes-first-common-market)
6. [New World Encyclopedia: Hanseatic League](https://www.newworldencyclopedia.org/entry/Hanseatic_League)
7. [Curtin, Cross-cultural trade in world history (review, World History Connected)](https://worldhistoryconnected.press.uillinois.edu/3.1/br_fahey.html)
8. [Sciencealert: how Polynesian voyagers navigated](https://www.sciencealert.com/were-still-slowly-learning-how-polynesian-voyagers-navigated-entire-oceans)
9. [World History Encyclopedia: Quipu](https://www.worldhistory.org/Quipu/)
10. [Urton: tying the archive in knots](https://www.ingentaconnect.com/content/routledg/cjsa/2011/00000032/00000001/art00002)
11. [JAXA: MARS artificial gravity mice](https://iss.jaxa.jp/en/kiboexp/news/170926_mars_en.html); [Gizmodo on the 0.67 g result](https://gizmodo.com/mars-doesnt-have-enough-gravity-to-keep-humans-healthy-study-suggests-2000733286)
12. [Partial weight bearing does not prevent musculoskeletal losses](https://scholars.uky.edu/en/publications/partial-weight-bearing-does-not-prevent-musculoskeletal-losses-as/)
