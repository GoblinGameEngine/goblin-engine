# B2. Tokyo (and Osaka, Kyoto): zakkyo, yokocho, capsules, machiya, danchi

## Zakkyo biru (雑居ビル): the multi-tenant signboard building
- **What it is:** a narrow commercial building holding **unrelated businesses on every floor**: bars, karaoke, clinics,
  restaurants, hookah bars and offices ([TKGJE](https://www.tkgje.jp/entries/18000/18092_zakkyobiru.html)).
  - Ginza examples run **6–8 storeys plus 1–2 basements**, with **one small lift**
    ([Varnelis, *The Zakkyo Biru of Ginza*](https://varnelis.net/works_and_projects/the-zakkyo-biru-of-ginza/)).
  - One narrow building can hold **up to 80 microbusinesses** ([Noahpinion](https://www.noahpinion.blog/p/a-better-way-to-build-a-downtown)).
- **Signage, the defining feature:**
  - **a backlit tenant directory** at the entrance, **one row per tenant, floor by floor**, sometimes wrapped round a pillar;
  - **a tall vertical projecting signboard (袖看板) up the corner**, one lit panel per floor and per tenant, stacked like the
    building;
  - **food replicas, lit menu boards and folding A-frames** on the pavement; mascot figures (a Pierrot on a silver ball);
    a vending machine beside the door.
- **Sizes:**
  - a typical internally lit projecting sign is about **2.6 m tall × 0.6 m wide × 0.2 m deep**, and stock sizes run 1–2 m;
  - it must hang **≥ 2.5 m above a footpath, ≥ 4.5 m over a roadway**
    ([biz.ne.jp](https://www.biz.ne.jp/matome/2007613/)).
- **Kit we take:**
  - `sign_vertical_stack` (per floor panels) and `directory_board`;
  - narrow tall massing (5–9 m wide, 6–10 storeys), a lift and stair core at the back;
  - a different window type on each floor (each tenant fitted out their own floor).

## Pencil buildings and kyōshō jūtaku (狭小住宅)
- Examples: Ginza **2.7 m wide, 4 storeys** ([designboom](https://www.designboom.com/architecture/so-co-thin-concrete-building-ginza-09-30-2019/));
  a Setagaya house **2.0 m wide on a 29 m deep plot**; Kumagaya **3.8 × 14 m, 3 storeys**
  ([realestate.co.jp](https://resources.realestate.co.jp/buy/unique-homes-in-japan-width-of-house-is-length-of-small-car/)).
- **Use:** a sliver filler between bigger blocks. It is perfect for islands, where every metre of deck is weighed.

## Yokochō (横丁): Golden Gai, Omoide Yokochō
- **Golden Gai** ([Wikipedia](https://en.wikipedia.com/wiki/Golden_Gai); [happyjappy](https://www.happyjappy.com/tokyo/shinjuku/golden-gai.html)):
  - **six alleys**, joined by passages **one person wide**;
  - **about 200–280 bars**, mostly **two-storey**, each **10–16 m²** (3–5 tsubo), seating **4–8 at one counter**;
  - buildings a few metres wide and nearly touching; steep stairs up to the second-floor bar.
- **Omoide Yokochō:** the same grain with yakitori stalls: smoke, red lanterns, plastic sheeting at night.
- **Kit we take:** the `alley_bar` building (a 3.0 × 4.5 m footprint on 2 storeys, with an external stair), alleys
  1.2–1.8 m wide, a **red chōchin over every door**, and **noren** in the doorways.

## Signs of the entertainment districts
- **Dōtonbori's Glico runner:** **20 m tall × 10.4 m wide**, LED since 2014. **Kani Dōraku's moving crab:** about **6.5 m**,
  with legs that move ([Wikipedia](https://en.wikipedia.org/wiki/D%C5%8Dtonbori);
  [muza-chan](https://muza-chan.net/japan/index.php/blog/the-story-of-the-glico-man-sign)).
  - These are **giant 3D figure signs** (a crab, a puffer fish, a dragon) mounted over shopfronts.
- **Midgar's Wall Market** was modelled on **Kabukichō**, the jumbled, eclectic Tokyo
  ([Square Enix](https://www.square-enix-games.com/news/final-fantasy-vii-remake-designing-midgar)).
- **Kit we take:** `sign_figure_3d` (an animated giant animal or object sign, e.g. a sky island's goat, bee, lark or bell),
  and `rooftop_billboard`.

## Chōchin and noren
- **Chōchin:**
  - the izakaya red lantern is about **33 cm dia × 67 cm** (vinyl, weatherproof)
    ([goodsfromjapan](https://goodsfromjapan.com/products/izakaya-lantern));
  - shapes run from **horizontal to spherical**, and "red chōchin" now *means* an izakaya
    ([Embassy of Japan](https://www.fr.emb-japan.go.jp/files/100548973.pdf)).
  - Aloft, chōchin are **electric** (no flame under hydrogen).
- **Noren:**
  - shop door curtains, usually **85 cm wide × 150 cm long**, split in 2–4 panels;
  - café-height ones are 85 × 90 cm; a long horizontal stall banner (yokomaku) is 180 × 45 cm
    ([Rakuten listings](https://www.rakuten.co.jp/category/100817/)).

## Machiya (町家): the Kyoto townhouse
- **Plan:**
  - frontage **5.4–6 m**, depth **20–30 m**, "the eel's bed" (unagi no nedoko), because the shop front was taxed
    ([Wikipedia](https://en.wikipedia.org/wiki/Machiya); [akiyajapan](https://www.akiyajapan.com/articles/machiya-kyoto-townhouse-guide));
  - an **earthen passage (tōri-niwa)** runs front to back along one side; the kitchen sits under a smoke void;
  - one or two **tsubo-niwa** courtyard gardens (some only 2 m²) light the middle;
  - a **koshi lattice** on the street front.
- **Kit we take:** `screen_lattice` (koshi), `tsuboniwa` (a lightwell with plants), and narrow deep lots.

## Nakagin Capsule Tower (1972), the plug-in capsule
([Wikipedia](https://en.wikipedia.org/wiki/Nakagin_Capsule_Tower))
- **Structure:**
  - **two concrete cores, 11 and 13 storeys** (47 and 53.5 m), linked by bridges at 6F, 9F and 12F;
  - **140 capsules**, each **2.5 × 2.5 × 4.0 m** with a **1.3 m round window** at one end;
  - each capsule is **bolted to a core by four high-tension bolts**, cantilevered, and replaceable one by one.
- **Fit-out:** a built-in appliance wall and an aircraft-style washroom.
- **Fit aloft:** a perfect match for the islands. Light steel boxes are **weighed, swapped and hoisted** like skyboxes. The
  **capsule stack** is a natural Aloft form (the "skybox stack").

## Danchi (団地)
([Wikipedia](https://en.wikipedia.org/wiki/Danchi))
- **Plan:** 1950s–70s public slab blocks, **4–5 storeys, walk-up**, in parallel rows with generous gaps. The standard **2DK**
  is about **43 m²**: two tatami rooms and an **8 m² dining-kitchen**; a danchi tatami is about 170 × 85 cm.
- **Face:** a continuous **balcony band on the sunny side** and **open access galleries** on the other.
- **Kit we take:** `gallery_access` and `balcony_band`, for the calmer residential islands.

## Rooftop shrines
- Many department stores keep an **Inari shrine on the roof** for business luck: a **small red torii, two lanterns and an
  altar** ([ginza.jp](https://www.ginza.jp/en/?p=19524); [fun-japan](https://www.fun-japan.jp/en/articles/11896)).
- **Aloft:** a **roof shrine to the Sunward or Our Lady of the Winds** with a little gate and bells (`roof_shrine`).

## Vending machines, wires and street clutter
- **Vending machines** sit everywhere and **glow at night**: a white-lit face with rows of coloured cans, 1.8 m tall
  *(general knowledge)*. Aloft they sell hot moss tea, warm cans, and hand warmers.
- **Overhead wires** sag across streets on concrete poles, with transformer drums *(general knowledge)*. Aloft, the
  **power lines run between roofs** from the sunskin envelopes and double as string-light runs.
