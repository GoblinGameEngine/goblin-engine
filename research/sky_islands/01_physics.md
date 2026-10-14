# 1. How the islands stay up

The canon numbers live in `tools/bible/canon_sky.py` (`physics()`), and make_bible writes them to
`godot_project/remake/bible/sky_islands.json` → `physics`. This page gives the reasoning behind them and its sources.

## Gravity at 750 m
- Columbia spins at ω = √(9.8 / 10,000) ≈ 0.0313 rad/s (a 201 s turn). The floor moves at 313 m/s.
- At the deck, 750 m up (radius 9,250 m), spin gravity is ω²r = **0.925 g**, and the air there moves at 290 m/s with
  the frame.
- The game's own gravity steps by bands (`StationGeo.gravity_at`, 1 km bands), so in game the deck is still in the
  1.0 g band. The canon uses the smooth physical value. The runtime can scale the player's gravity aboard (a hook in
  StationPlayer); that is the runtime stream's decision.

### The Eötvös effect, turned inside out
- On Earth, gravity is real and the spin subtracts from it. Moving east (with the spin) makes you lighter and moving
  west makes you heavier. Eötvös found this in gravity readings taken from ships, and a 1908 Black Sea experiment with
  two ships confirmed it [1][2][3].
- In a spin habitat, weight is the spin. Moving **spinward (east)** adds to your speed round the axis, so you get
  **heavier**. Moving **antispinward (west)** makes you **lighter**: g_eff = (ωr − v)² / r.
- An island drifting west at 6 m/s relative to the floor feels **0.887 g**. Its people live their whole lives at about
  0.89 g.
- Buoyancy is a ratio. Lift (ρ_air·V·g) and weight (m·g) scale with the same g, so a uniformly lighter g does not by
  itself float anything. What the Aloft exploit is **relative** motion:
  - The envelopes reach 1 km up into faster westerly air (the game's cloud layers run 15 m/s at 500 m and 21 m/s at
    1,400 m), and that drags the whole island west faster than the air round its deck.
  - Relative to the air it floats in, the island is running antispinward, so it is lighter against that air's
    buoyancy.
  - At 3 m/s of slip the gain is about 2 v/(ωr) ≈ 2%: some 600 t on a 30,000 t island.
  - The Aloft call it **the Lightening** and trim for it.
- The game's weather already uses the same convention. `cloud_system.gd` CORIOLIS_LIFT: "an antispinward wind is
  lifted (it weighs less)".
- What lower gravity really buys them is **lighter structure**. Loads scale with g, so frames, tethers, the stone crust
  and the bridges can all be about 8–11% lighter for the same strength. Every kilo saved is lift.

## Lift
- One envelope is a cylinder 100 m across and 1 km tall: 7.85 million m³.
- Air density at 810–1,810 m: the floor's air is about 1.20 kg/m³. A lower g means a longer scale height (about 9 km
  against Earth's 8.4 km), so the air thins slowly. The mean density over the envelope is about **1.06 kg/m³**.
- Hydrogen lifts ρ_air × (1 − 2.016/28.97) per m³, so the gross lift is **~7,750 t** an envelope. At sea level on
  Earth, hydrogen lifts about 1.2 kg/m³ and gives ~8% more lift than helium [4].
- The envelope:
  - 330,000 m² of skycloth at 220 g/m² is ~73 t, plus net, rigging and tether, for ~160 t;
  - net lift is **~7,600 t**.
- Hydrogen, not helium: helium cannot be made aboard, and hydrogen can (electrolysis).
- The fire risk is why the Aloft keep the **Flame Knot**: no open flame aloft.

## Mass budget per block (8,000 m² of deck)
| item | t | why |
|---|---|---|
| shell: a foamed stone crust 1.2–2 m thick over ribs and sealed cells | 3,600 | see below |
| the deck slab (lightweight) | 1,400 | |
| buildings: light frame, cloth and board, 5–8 storeys | 3,600 | ~0.15 t per m² of floor |
| soil, stores, goods | 1,300 | rooftop beds 0.3 m deep |
| ponds and lakes (ballast, trimmed) | 900 | see Water |
| people (~250) | 15 | |
| **total** | **~10,800** | |

- The contract gives `ceil(1.6 × blocks) + 1` envelopes:
  - a 1-block island has 3 envelopes (~22,800 t of lift for ~10,800 t). Small islands are buoyant and carry ballast
    water.
  - a 10-block island has 17 envelopes (~12,900 t a block): a 15–19% margin before the Lightening, and the ponds can be
    drained for ~900 t more a block.
- **Trim:**
  - **lighter:** drain ballast water, drop cargo, make gas;
  - **heavier:** take on water from the cloud nets, vent gas (rarely: gas is power).
  - Weighers keep the books. The Weight Knot is the first law.

### Skystone: the "rock"
- A rock bottom of real stone is impossible: 10 m of basalt under a block weighs about 240,000 t.
- The islands' rock is **skystone**: foamed glass-ceramic the Steward cast from the Spindle's slag.
  - Commercial cellular glass is 95–220 kg/m³, mostly 100–130 [5][6]. Foam glass aggregate is 110–250 kg/m³ [5].
  - It absorbs almost no water and is fire-proof [6].
- Skystone is a 1.2–2 m crust of 150–250 kg/m³ foam over a honeycomb of sealed cells.
  - The cells hold a little gas, and the ice houses and cisterns are cut into them.
  - It looks like dark, pitted volcanic rock (a pumice look).
  - Moss and vines root in its pores.
  - It would float on water.

## Power and gas
- **Leakage:** goldbeater's-skin gas cells lost "only a few litres of hydrogen per m² in 24 hours" [7].
  - Skycloth is worse: **~0.3% of an envelope's gas a week**, and air creeps in as gas creeps out.
  - That is ~3,400 m³ a day per envelope, or about 15 MWh of electrolysis a day (4.5 kWh/m³).
- **The sunskin:** the Steward skinned its envelopes in photovoltaic film.
  - Half of an envelope's 314,000 m² faces the Sunline.
  - Even aged to a few per cent efficiency, it makes ~40 MWh a day.
- The Aloft can patch sunskin but cannot make it. New plain-skycloth envelopes have to be carried by the old ones,
  which is why an island's oldest envelope is its treasure.

## Water
- Cloud and fog nets yield 2–5 L per m² a day on average and up to ~10 L on good sites in real fog-collection
  projects [8][9].
  - Inside a Columbia cloud, the nets run for hours.
  - Snowmelt from the decks adds more.
- **Ponds (every island) and small lakes (6 or more blocks)** are the reservoir and the ballast at once:
  - a 1,000 m² pond a metre deep is 1,000 t of trim;
  - they are lined with skycloth over the stone.

## Cold and snow
- **Temperature:**
  - The environmental lapse rate is ~6.5 °C/km, so the deck is ~5 °C colder than the floor. The envelope tops at 1.8 km
    are ~11 °C colder. There is wind on every exposed roof.
  - Spring days at the deck: 8–12 °C. Winter nights: near or below freezing.
- **Snow aloft and rain below:**
  - In real clouds most precipitation begins as ice. In the Bergeron–Findeisen process, ice crystals grow at the
    expense of supercooled droplets between 0 and −20 °C and fall as snow, which melts into rain if the air below is
    warm [10][11].
  - Since **the Last Snow (VY 212)**, the Steward has kept the floor above freezing and made its rain this way, with
    cloud interiors kept cold.
  - So an island passing **through** a cloud is snowed on, and the snow lies. Out of the cloud it melts and sublimes
    only slowly, in cold, dry, moving air.
  - The Aloft are the only people aboard who know snow. The floor's grandmothers' "snow stories" are true.

## Sources
1. [Eötvös effect](https://en.wikipedia.org/wiki/E%C3%B6tv%C3%B6s_effect) (Wikipedia)
2. [Roland Eötvös: scientist, statesman, educator](https://arxiv.org/pdf/2002.05743) (arXiv)
3. [mezzacotta: Eötvös and the Black Sea ships](https://www.mezzacotta.net/100proofs/archives/482)
4. [Bring back hydrogen lifting gas](https://www.thecgo.org/benchmark/bring-back-hydrogen-lifting-gas/) (CGO)
5. [US12312270B2 Cellular glass product](https://patents.google.com/patent/US12312270)
6. [Owens Corning FOAMGLAS F](https://owenscorning.com/insulation/products/foamglas-f)
7. [Airship fabrics](https://www.globalsecurity.org/military/world/airship-fabrics.htm) (GlobalSecurity, quoting Chollet)
8. [Fog collection](https://en.wikipedia.org/wiki/Fog_collection) (Wikipedia)
9. [Munich Re Foundation fog nets FAQ](https://www.munichre-foundation.org/en/climate-adaptation/archive/fognets/fognets_FAQ.html)
10. [Bergeron–Findeisen process](https://glossary.ametsoc.org/wiki/bergeron-findeisen-process/) (AMS Glossary)
11. [UCI ESS5 ch. 7: precipitation](https://www.ess.uci.edu/~yu/class/ess5/Chapter.7.precipitation.2008.pdf)
