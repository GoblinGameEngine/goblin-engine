# 4. Jobs, economy, water and animals

Canon data: sky_islands.json → `jobs` (descriptions), `specialties`, `hoist_trade`, `lark`, `water`, `livestock`,
`wildlife`, and per island `jobs` (counts), `specialty`, `trade`, `needs`, `water`, `livestock`, `wildlife`. The
totals are in `totals.jobs` and in research/bible/13_sky_islands.md.

## Who works
- **Working people:** 56–62% of each island's population. The rest are children (more than on the floor: children are
  "ballast"), elders past the lines, and the sick.
- **How counts are set:**
  - every job has a base weight per 1,000 workers;
  - the island's **specialty** multiplies the jobs it lives by;
  - a hash varies each island ±25%;
  - minimums guarantee every island its plumb and second (2–4), lark wrights, two line rocketeers, a knot keeper, a box
    tender, a weigher, a healer, a bridgewright, a hoist master, a pond keeper and a herder;
  - whatever is left over grows food.

## The jobs, by what they keep alive
- **Keeping it up:**
  - riggers (walk the tethers and nets);
  - envelope wrights (skycloth, patching sunskin);
  - gas makers (electrolysis);
  - weighers (the weight book, trim);
  - fence wardens (the rim, rescue).
- **Tying it to others:**
  - winch hands;
  - line rocketeers (cold rockets);
  - bridgewrights;
  - ropers.
- **Water:**
  - net keepers (cloud nets, cisterns);
  - snow hands (clearing snow: a deep fall weighs hundreds of tonnes);
  - pond keepers (ponds and lakes: reservoir, ballast, fishery).
- **Food:**
  - roof growers (the biggest trade: every roof is a garden);
  - herders (goats, sheep);
  - poultry keepers;
  - beekeepers;
  - dove keepers;
  - moss gatherers (the underside garden, worked from cradles slung under the rim);
  - cooks (electric only: the long kitchen);
  - brewers.
- **Making:** weavers, knitters, tailors, menders, sparks (electricians), smiths (cold-worked light metal, no forges).
- **People:** teachers, child minders, healers, counsel (elders), musicians (bell-speech), knot keepers, box tenders,
  compost hands, shopkeepers.
- **Trade:** factors, hoist masters, the plumb, lark wrights, weather readers.

## Specialties: what each island sells
- There are 20 specialties: skycloth, cordage, knitwear, down, honey, weather, ice, moss, larks, bells, brewing, survey,
  courier, dried foods, gas, lore, gardens, wool, fish and trade.
- Each island has one. Its `trade` list is what it sells to other islands and the floor; its `needs` list is what it
  buys.
- **Every island needs** metal, grain and medicine.
- **The floor prizes** most:
  - **snow and ice**: a wonder since the Last Snow;
  - forecasts (the Grange, the Aerostat Guild);
  - knitwear and down;
  - sky honey;
  - moss remedies;
  - the air post.

## Hoist trade
- Hoists are scheduled. The plumb books an hour over a **hoist ground**: a Drop, a Chute or a market town. The weather
  reader picks the drift, and the island trims to pass over at that hour.
- **Lines:** 750 m and more, dropped from the hoist cranes on the rim.
- **The skybox:** a 2.4 × 2.4 × 3 m aluminium-framed container, at most 2 t loaded.
- Goods go down in the same boxes. Every hoist is weighed both ways, because what comes up must be balanced by what
  goes down, or by gas.
- An island makes a hoist every few days. It is a set piece for the game: the line comes down, the floor's dock hands
  hook on, and the box rises through the trees.

## The lark (fleet type `sky_skiff`)
- **Crew:** two, in tandem: the plumb forward and the second behind.
- **Performance:** 1.5 km ceiling, 250 km/h, ~8 m/s climb.
- **Build:** a slim 14 m hydrogen cigar over a light keel, four ducted fans on tilting pylons, and a mooring winch.
- **Docking:** larks sit in cradles on the tallest roofs. A lark docks by flying up a dropped line.
- **Numbers:** at least two per island (`2 + blocks // 3`, plus one for courier and lark-wright islands).

## Water
- **Every island has ponds; islands of six or more blocks also have a small lake** (the user, 2026-10-14).
  - Ponds: 150–600 m², 1–2 m deep, one per two blocks plus one.
  - Lakes: 300–600 m² per block, 1–3 m deep.
- **Fed by** the cloud nets and snowmelt.
- **They are the island's ballast as well as its reservoir and fishery.** Weighers drain them to trim: a 1,000 m² pond a
  metre deep is 1,000 t.
- Lined with skycloth over the stone. In a long white they freeze over and are skated on.
- Pond fish: perch and pumpkinseed sunfish, plus crayfish. Frogs came up as spawn in hoisted water.

## Livestock (`livestock`: counts per island)
Livestock is chosen for low weight, cold, small decks and a 0.89 g life. **Models are needed later.** Each token is
one animal model:

| token | animal | kept | typical per block | notes for the model |
|---|---|---|---|---|
| goat | dwarf goat | hill pastures, roof paddocks | 6 | small (45 kg), shaggy |
| sheep | small hill sheep | rolling islands only (or wool islands) | 4 | dense fleece |
| hen | hen | roof coops | 30 | |
| duck | duck | ponds | 10 | |
| goose | goose | ponds, lake shores | 4 | the down trade; watch-birds |
| rabbit | rabbit | hutches | 12 | |
| dove | dove (pigeon) | dove lofts | 25 | flocks wheel round the lofts |
| bee | honeybee | roof hives | 8 hives | particles |
| pig | small pig | great islands (6+ blocks) only | <1 | heavy: only where the lift allows |
| fish | perch, sunfish, crayfish | ponds and lakes | "stocked" | |

There are no cattle and no horses aloft: too heavy for the lift.

## Wildlife (`wildlife`: a list per island)
- **Every island:**
  - swallow (mud nests under the rim);
  - sparrow (came up with the first boarders);
  - frog;
  - ballooning spider (real: spiders sail on silk, and silk has been sampled at ~5 km [1][2]);
  - snail;
  - mouse (a stowaway in cargo);
  - cat (the mousers);
  - wren (lives in the hanging moss);
  - moth.
- **Some islands:**
  - swift (underside crevices);
  - starling (murmurations round the envelopes);
  - gull and tern (follow islands over the seas);
  - dragonfly;
  - lichen moth (a grey moth found only aloft);
  - heron (visits the lakes of great islands).
- All of these are already canon on the floor (research/bible/01_world: wildlife), except the cats, mice, spiders and
  moths, which any human settlement has.

## Sources
1. [Ballooning (spider)](https://en.wikipedia.org/wiki/Ballooning_(spider)) (Wikipedia)
2. [Morley & Robert 2018, Electric fields elicit ballooning in spiders](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6065530/)
