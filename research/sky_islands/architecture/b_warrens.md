# B3. Stacked warrens and megastructures

The user asked: "When an architecture style does have tall buildings, find examples of stacked warrens." Here is what
each example does, and the rule a generator can take from it.

Scope: Asian warrens and megastructures. European, South American and Canadian examples (Habitat 67, Torre David and
others) are stream C's, in c_*.md. Per the user, African examples are left out.

| Place | Facts | The rule we take |
|---|---|---|
| **Kowloon Walled City** | 210 × 120 m, about 350 buildings at 10–14 storeys, a flat cap from the flight path, alleys 1–2 m wide, upper-level crossings, roofs linked by ladders ([Wikipedia](https://en.wikipedia.org/wiki/Kowloon_Walled_City)) | **Accrete to a cap.** Start with small blocks and add storeys and annexes on top until a height cap. Party walls are shared, upper floors widen, and alleys survive as slots. Bridges join neighbours at random levels. |
| **Chungking Mansions** | a 3-storey podium bazaar with 5 towers of 17 storeys, odd and even lifts, 360 tiny shops, guesthouse rooms on light wells ([Wikipedia](https://en.wikipedia.org/wiki/Chungking_Mansions)) | **Podium + towers.** The ground is all shops (a market maze), with a roof terrace on the podium, and slim towers rise from the terrace. |
| **Monster Building** | an E-shape of 5 blocks at 18–19 storeys, 23–32 flats per floor, two inner courtyards ([Wikipedia](https://en.wikipedia.org/wiki/Monster_Building)) | **Courtyard canyon.** Wrap a deep narrow court with a continuous wall of small units, AC boxes and laundry. |
| **Hakka tulou (Chengqi Lou)** | 62.6 m across, 4 concentric rings; the outer ring has 4 storeys of 72 rooms, kitchens on the ground floor, grain on 1F, living on 2–3F; inner rings of 2 and 1 storeys; an ancestral hall in the centre ([Fujian gov](https://fujian.gov.cn/english/services/travel/placetovisit/201701/t20170125_1869537.htm); [transindus](https://transindus.co.uk/highlights/tulou-houses-of-yongding-county)) | **The ring house.** A clan in one round building: a continuous gallery facing the court, uses stacked by floor, a shrine at the centre. One clan, one island, one ring: a natural Aloft "clan hall". |
| **Nakagin Capsule Tower** | 140 capsules of 2.5 × 2.5 × 4 m bolted to 2 cores ([Wikipedia](https://en.wikipedia.org/wiki/Nakagin_Capsule_Tower)) | **Core + plug-ins.** A stair and lift core with boxes bolted on at angles, each with a porthole. For the Aloft these are "skybox" homes. |
| **Hanging Temple (Xuankong Si)** | about 75 m up a cliff, halls on 27 timber beams driven 2/3 into the rock, with the posts below added for reassurance ([Wikipedia](https://en.wikipedia.org/wiki/Hanging_Temple); [China Daily](https://shanxi.chinadaily.com.cn/2020-12/25/c_577454.htm)) | **The rim gallery.** Rooms cantilevered off the island's edge on beams over the void, with a walkway clinging to the rock. |
| **Rooftop slums, HK** | huts on tenement roofs, 27,000 people in 1971 ([Wikipedia](https://en.wikipedia.org/wiki/Rooftop_slum)) | **Second town on the roofs.** Huts, gardens and stairs fill every roof. |

## How generators can build warrens (for stream 3, the sky building generator)
- **Unit grammar:**
  - the **cell** is a box of 2.5–4 m × 3–6 m × 2.8 m storey;
  - a **building** is a column of cells on a lot;
  - a **warren** is a lot grid where each lot's column grows by random increments (+1–3 storeys) in rounds up to a cap;
  - each round can **overhang** the street by 0.6–1.5 m (`stack: overhang`), or set back (`setback`; for stepped piles see
    stream C).
- **Joins:**
  - neighbouring columns of equal height on a round merge their roof;
  - columns with a height difference of 1–3 storeys get a **ladder or stair** (`stair_external`);
  - columns across an alley get a **skybridge** (`skybridge`) at a random storey, about one bridge per 4 columns.
- **Alleys:** keep a 1.2–2 m slot every 2–4 lots, and roof some of them with **plastic or corrugated canopies**
  (`canopy_alley`).
- **The outer face** (the island's promenade side) gets the **dense sign band** (Kowloon's dentists).
- **Ground floor:** shops with shutters; roll the shutters up and the shop spills out with stalls.
- **Weight (the canon):** every kilo is weighed. Warrens are built of light frames: corrugated sheet, skycloth awnings,
  timber, aluminium. There is no masonry. The look is **light and patched**, not concrete brutalism.

Plans as data: `plans/b_kowloon_block.md`, `plans/b_podium_towers.md`, `plans/b_tulou_ring.md`,
`plans/b_capsule_core.md`, `plans/b_tong_lau.md`, `plans/b_zakkyo.md`, `plans/b_yokocho.md`.
