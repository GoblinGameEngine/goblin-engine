# B1. Hong Kong: tong lau, composite towers, the Walled City, and neon

Stream B research for the sky islands (00_brief.md). The numbers here are measured or reported; the ones marked *(est.)* are
working values I chose for the generator.

## Tong lau (唐樓), the shophouse tenement
- **Origin:** 19th-century South Chinese shophouse, reshaped by Hong Kong's plague-era law. The **1903 Public Health and
  Buildings Ordinance** capped them at **4 storeys** and required **light wells and rear lanes**. Developers then pushed deep,
  pillared **verandahs out over the public footpath** to gain floor space
  ([cityunseen](https://cityunseen.hk/?p=626); [HKU hub](https://hub.hku.hk/handle/10722/235630)).
- **Pre-war plan** ([URA, Queen's Road East](https://ura.org.hk/en/project/heritage-preservation-and-revitalisation/186-190-queen-s-road-east);
  [URA, 18 Ship Street](https://ura.org.hk/en/project/heritage-preservation-and-revitalisation/18-ship-street)):
  - narrow frontage, about **4–5 m** *(est., 13–15 ft lots)*;
  - units of **42–65 m²** (450–700 ft²), deep;
  - shop on the ground floor, living rooms above with **French windows onto the verandah**;
  - a light well between the front rooms and the rear kitchen;
  - a shared stair, split down the middle by the lot line.
- **Roofs:**
  - before about 1935, pitched, on timber beams;
  - after, flat concrete roofs, which became the place for rooftop huts, laundry and water tanks
    ([cityunseen](https://cityunseen.hk/?p=626)).
- **Post-war:** the **1955 Buildings Ordinance** allowed walk-ups of **up to 9 storeys** and taller lift buildings by street
  width. Cantilevers replaced the pillars, so upper floors **jut over the street with no columns**. Arcade verandahs were
  effectively banned by the 1960s ([Shanghai Street](https://en.wikipedia.org/wiki/Nos._600%E2%80%93626_Shanghai_Street)).
- **Kit we take:**
  - verandah arcade (`arcade_colonnade`), cantilevered upper floors (`stack: overhang`);
  - **light well** (`lightwell`), shared split stair, flat roof with a rooftop shack;
  - shop shutters (`shutters`, rolling steel), and window bars and grilles (`window_grille`).

## Composite towers: Chungking Mansions and the Monster Building
- **Chungking Mansions** ([Wikipedia](https://en.wikipedia.org/wiki/Chungking_Mansions)):
  - **17 storeys, five blocks A–E** on a shared **3-storey podium**: shopping arcade on G/1F, a terrace on 3F, and the towers
    rising from it;
  - each block has **2 lifts**, one for odd floors and one for even;
  - **360 shops of 4.6–46 m²** (50–500 ft²) on one floor;
  - over 110 guesthouses with about 1,200 rooms, many **windowless or opening on dim light wells**, every room with an AC unit;
  - the 2010 refit added **multicolour LED bands** to the facade.
  - Model for a **"podium bazaar + towers"** style.
- **Monster Building, Quarry Bay** ([Wikipedia](https://en.wikipedia.org/wiki/Monster_Building);
  [Docomomo HK](https://www.uglybuildings.docomomo.hk/copy-of-state-theatre-north-point)):
  - **five linked blocks in an E-shape** of **18–19 storeys**, 2,243 flats, **23–32 flats per floor**;
  - **two inner courtyards** walled by gridded facades of AC units, laundry poles and window boxes.
  - Model for a **"courtyard canyon"**: you look up from a slot into a wall of hundreds of tiny lit windows.

## Kowloon Walled City (九龍城寨)
([Wikipedia](https://en.wikipedia.org/wiki/Kowloon_Walled_City);
[ICACI map](https://mapdesign.icaci.org/?p=1574);
[Colossal on the cross-section](https://www.thisiscolossal.com/2024/07/kowlooon-walled-city-illustration/))
- **Site:** about **210 × 120 m (2.6 ha)**, almost exactly a 3-block sky island.
  - **About 350 buildings** (300–500 by source), most **10–14 storeys** by the 1970s.
  - **Capped at 13–14 storeys** by the Kai Tak flight path, so the roofline is a **near-flat plateau**.
  - **33,000 people** (1987), about 1.26 million per km².
- **Growth:**
  - squatter huts (1947: 2,000 people), then a **fire in 1950** (2,500 huts);
  - in the 1960s–70s, **modular structures built on top of older ones**;
  - it reached its maximum by about 1980.
  - Buildings are built **back to back**, sharing walls. Upper floors are **wider than lower ones**, extended with
    **caged balconies** and **rooftop additions**.
- **Circulation:**
  - **dozens of alleys 1–2 m wide**, dark, lit by **bare fluorescent tubes**, dripping pipes and wiring down the walls;
  - an **upper network of stairs and passages** let you **cross the whole city north to south without touching the ground**.
  - Many units were about **23 m²**.
- **Roofs:**
  - **a forest of TV aerials**, clothes lines, water tanks and rubbish;
  - roofs **linked by ladders**, a **social space** where children played and did homework.
  - Planes passed just overhead (our analogue: balloons and larks).
- **Businesses:** food factories, many unlicensed **dentists and doctors with signs crowding the outer edge**, small
  workshops, schools and clinics.
- **Kit we take:** the warren itself (see `plans/b_kowloon_block.md`):
  - a flat **height cap**, buildings **fused into one mass**, alleys 1.2–2 m;
  - **internal bridges and stairs** at every level, roofs joined by ladders;
  - a ring of **dense signs on the outer face**, and caged balconies.

## Rooftops and add-ons
- **Rooftop squatter huts:** about 27,000 people lived on rooftops in 1971, and 47,000 in 2011 by one census measure
  ([Rooftop slum](https://en.wikipedia.org/wiki/Rooftop_slum)). They are tin-and-timber shacks on tenement roofs, often two
  storeys, with their own little stairs, plants and water drums.
- **Caged balconies:** steel-bar enclosures hung on the face, now illegal and mostly gone
  ([City of Darkness](https://cityofdarkness.co.uk/?p=542)). Older balconies stand on **wall brackets with timber joists and
  thin iron columns** between levels ([HKU photo](https://digitalrepository.lib.hku.hk/catalog/2r36v027f)).
- **Window AC units, laundry poles and bamboo scaffolding** are ubiquitous. Bamboo scaffold sheathed in green or blue netting
  appears on every renovation *(general knowledge)*.

## Neon
- **Making it** ([Gigazine](https://www.gigazine.net/gsc_news/en/20170104-making-of-neon-sign);
  [SCMP](https://scmp.com/lifestyle/travel-leisure/article/3197396/hong-kong-neon-artist-teaching-his-craft-new-generation-can-he-help-it-survive-onslaught-leds)):
  - glass tube heated above 800 °C, bent by hand, evacuated and filled;
  - **pure neon glows red-orange; argon with mercury glows blue**; other colours come from **phosphor-coated or tinted glass**;
  - **Chinese characters are harder to bend** than Latin letters.
- **Rules:** Hong Kong's projecting signs may extend **at most 4.2 m from the wall** and hang **at least 3.5 m above the
  footpath** ([China Daily](https://www.chinadailyhk.com/article/366790)). The 1932 Phoebus Neon ad offered letters from
  **10 cm to 3 m** ([Industrial History HK](https://industrialhistoryhk.org/?p=70954)).
- **The look:**
  - Nathan Road was a **dense, overlapping canopy of glowing glass tubes** casting a **wash of crimson, emerald and amber** over
    the crowds ([Blue Lotus](https://bluelotus-gallery.com/blog/2026/7/8/city-of-lights-keith-macgregor-on-documenting-hong-kongs-lost-neon-nightscapes));
  - signs **overhang corners** so the whole corner glows, and rain doubles them in reflections
    ([Time Out](https://www.timeout.com/hong-kong/things-to-do/hong-kong-neon-signs)).
- **Decline:** about 400 neon signs are left; the city has turned to LED.
- **Our canon fit:** neon is cold-cathode with no open flame, so it is **allowed aloft** (the Five Knots: "No flame, no fall").
  Gas tubes are light. The Aloft would love it.
