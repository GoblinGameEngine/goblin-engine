# 01 Research: tents, lights, flea-market layouts, ropeways, and the Roma/Traveller reference

Collected 2026-10-15 by web search. Numbers in [n] refer to the source list at the end. Most sources are vendor,
rental, travel or encyclopaedia pages, so treat their figures as indicative. Items marked **(GK)** are general
knowledge and were not sourced this pass; check them before they become canon. The deeper market profiles, economics
and bazaar history are in 03, 04 and 05.

---

## 1. Tents

### 1.1 Pop-up and frame tents (the unit of the Western flea market)
- **Footprints:** 10x10 ft (3x3 m) and 10x20 ft (3x6 m).
  - The legs of a high-peak 10x20 frame tent are 8 ft (2.4 m).
  - Pop-up peaks are 3.2–3.5 m [39].
- **Ballast:** about 23 kg (50 lb) per leg. A 6-leg pop-up "ideally" carries ~170 kg (370 lb).
  - On asphalt, stakes are impossible: sandbags or water weights on every leg, with guy straps at ~45° [39].
  - **Modelling cue:** a sandbag or water barrel at each leg, and ratchet straps. Paved-lot tents are frame tents,
    never pole tents.
- **Large frame tents (GK):** 6, 9 and 12 m wide, built in 3 m bays. Eaves are 2.1–2.4 m, and the peak sits about
  1/4–1/3 of the width above the eave.

### 1.2 Pagoda (high-peak) tents: the islanders' "bazaar tent" base
- **Heights:** eave 2.3 m at every size; ridge 3.9 m (3x3), 5.1 m (5x5), 5.6 m (6x6) [35].
- **Construction:** aluminium frame. The roof is 750–850 g/m² PVC and the walls 660 g/m² PVC, rated to 80–100 km/h
  [35][36].
- **Rule of thumb:** eave ≈ 2.3–2.5 m; ridge ≈ 2.3 + 0.55 × side.

### 1.3 Stretch ("Bedouin") tents
- **Size:** a 10x15 m tent has a high point of 3.65 m. Masts are 2 m at the corners, 3 m on the sides and 4–5 m in the
  middle [37].
- **Kit:** 8 + 6 + 3 poles and 30 pegs, 108 kg in all [38].
- **Fabric:** PU-coated four-way stretch polyester, ~560 g/m² [38].
- **Use here:** a sagging, free-form membrane. It suits the islanders' improvised shade between tents.

### 1.4 Circus and carnival big tops (the "event tent" at fair scale)
- **Typical:** a 35–40 m top has 4 king poles of 14–17 m and seats ~1,200–2,000 [94][95].
- **Largest:** Cirque du Soleil's touring top is 51 m across and 20 m high [96].
- **Use here:** one per fair at most, as a landmark (the "Lantern Top", §06).

### 1.5 Shamiana, kanat and mela tents (South Asian)
- **Shamiana:** a ceremonial flat or slightly domed canopy on poles, descended from Mughal camp tents [32].
- **Kanat:** printed or appliquéd wall panels with arch and flowering-vase motifs. The kalamkari and khatwa appliqué
  of Bihar are the references [33][34].
- **Use here:** the islanders' tents are lined like this. The pattern is on the inside, and it glows when lit.

### 1.6 Covered bazaars
- **Grand Bazaar, Istanbul:**
  - 61 covered streets, ~4,000 shops (3,000–4,500 by source), 18–22 gates, ~30,700 m² [30][31].
  - ~4,399 shops in 1890, which is roughly 7 m² gross a shop.
- **Shop and stall forms (GK):**
  - Souk shops are alcoves 1.5–3 m wide and 2–4 m deep.
  - Goods hang from the ceiling and door frame and spill into the lane.
  - Lanes are 2–4 m, shaded by slats or cloth.
- **Jemaa el-Fnaa:** 100+ night food stalls set up on a numbered grid every evening [98].

### 1.7 How goods are shown
- **Western:**
  - folding tables of 6–8 ft x 30 in (1.8–2.4 x 0.76 m);
  - rolling clothes racks, ropes between the legs, grid-wall panels;
  - tarps on the ground;
  - bins under the tables, and the van behind.
- **Bazaar:**
  - floor-to-ceiling shelving;
  - lanterns, rugs and bags hung overhead;
  - open spice sacks at the front.
- **The game's islanders mix both.** A tent has 2 shelf units, 1–2 tables, an overhead hanging rail and a lit counter.

## 2. Lighting

### 2.1 Festoons
- **UK commercial:** 50 m runs with 50 E27 holders at 1 m spacing; 0.5 m spacing looks richer [23].
- **US commercial S14:** 14.6 m strings with 24 sockets at 0.6 m, bulbs hanging 15 cm below the cable. LED bulbs are
  0.8–2 W; the old incandescent was 11 W [97].
- **Rigging:**
  - Spans over ~3 m hang from a catenary wire, with 10–20 % slack for the drape [24][25].
  - Rigs sit 3–5 m above walkways, and above 4.3–4.6 m where trucks pass (GK).
  - The classic market look is a zig-zag across the aisle.
- **Game use:**
  - Bulbs every 0.6–1.0 m along a catenary of 5–10 % sag.
  - Use the existing `StreetLights._festoon` maths (`StreetLights.gd:299`) and the `sky_bulbs` shader.

### 2.2 Lanterns
- **Egyptian fanous:** tin, then coloured glass in soldered tin, copper or brass frames [79][80].
  - A few workshops still make them by hand; most sold today are cheap plastic imports.
  - This gives a ready "authentic vs mass-made" split for the market economy.
- **Moroccan pierced lanterns (GK):** they throw patterned light and hang in dense clusters. This is the set piece of
  an islander lantern tent.

### 2.3 Night markets
- **Shilin, Taipei:** 539 stalls in the food court (500–600+ with the lanes), open 16:00–24:00 [29].
- **The look (GK):** each stall has its own bare tube or bulb, giving bright pools against a dark street.

### 2.4 Parking-lot lighting
- **Standard:** IES RP-20 covers parking (RP-8 covers roads) [27].
- **Levels:** typically 1.5–3.0 fc (16–32 lux) average, with uniformity max:min under 4:1 [26]. Municipal minimums go
  as low as 0.5 fc (5 lux) at 15:1 [28].
- **Pole spacing:** about 2–3x the mounting height: 6–7.6 m poles at 15–20 m, and 7.6–9 m poles at 18–24 m [26].
- **Game use:** lamp kind 5 is a 9 m pole spaced 22–25 m, at ~20 lux.

## 3. Flea markets and swap meets (layout numbers; profiles in 03)

| market | vendors | area | schedule |
|---|---|---|---|
| Rose Bowl, Pasadena [1][2] | ~2,500 (≈200 in 1968) | stadium lots | 2nd Sunday; early entry 5 am, general 9–15; ~20k buyers |
| Brimfield, MA [8][9] | 4,000–6,000 | ~20 private fields, ~150 acres | 3 shows a year |
| First Monday, Canton TX [10][11] | 4,500–6,000+ | 100–450 acres | Thu–Sun before the 1st Monday; ~620k visitors a year |
| Chatuchak, Bangkok [12] | 8,000–15,000 | 11–14 ha, 27 sections by goods | weekends, ~200k visitors |
| Saint-Ouen, Paris [13][14] | ~1,700 | ~7 ha, 12–14 sub-markets | weekends and Monday |
| El Rastro, Madrid [15] | up to ~3,500 | streets | Sundays 9–15 |
| Mauerpark, Berlin [77][78] | ~500 | ~7,000 m² | Sun 10–18, park karaoke |
| Alameda Point [84] | 800+ | former runway | 1st Sunday, 6–15 |
| Kobey's, San Diego [16] | 1,000+/week | ~15 acres of arena parking | 25k+ shoppers a weekend |

- **Permanent vs transient (Kobey's) [16]:** ~250 permanent sellers with fixed spaces, ~250 new-goods sellers a day and
  ~500 used-goods "garage" sellers a day.
  - That is about **25 % permanent**. The brief's 35 % sits a little above it, which suits a market with covered sheds.
- **Geometry:**
  - The 10x10 ft pitch is universal; 10x20 is the drive-in "car and space".
  - Alamo, TX code requires 12 ft (3.7 m) paved access behind booths, 12 ft walkways in front, and painted booth lines
    [19].
  - IFC fire lanes are 20 ft (6.1 m) wide with 13'6" (4.1 m) of clearance, and every structure within 150 ft (45 m)
    [17][18]. **So every few rows one aisle must be a clear 6 m lane.**
  - Parking: 90° stalls of 2.6–2.7 x 5.5 m with a 7.3 m aisle; a module of 18.3–19.5 m; ~150 spaces an acre (~370 a
    hectare) [89][90].
- **Leasing (Shipshewana) [81][82]:**
  - $35 a day, $55 a week, $163–198 a month, plus a deposit.
  - Holding the same spot next season means renting the whole season. Otherwise the spot goes to a waiting list.
  - No-shows are resold daily, first come first served.
- **Small events:** $15–25 a day for a 10x10 with your own tent [83].
- **The day's rhythm:** early-bird entry at dawn (dealers and pickers), general entry ~9:00, closing ~15:00–16:00
  [2][84].
- **Vendors:**
  - Mexican immigrant vendors transformed California swap meets [20].
  - LA indoor swap meets (often Korean-owned, serving Latino shoppers) were livelihoods and social halls [21][22].
  - The rest of the mix: retirees and hobby collectors, dealers and pickers, new-goods importers, household sellers.

## 4. Ropeways, cableways, aerostats

### 4.1 Monocable detachable gondola (MGD)
- ≤ 10 people a cabin, ≤ 6 m/s, ≤ 4,500 pph [41].
- Awana Skyway: 10-person cabins, 6 m/s, 3,600 pph, 60 mm haul rope, 22 towers over 630 m of rise [40].
- Mechanics (GK):
  - Cabins detach in the stations and crawl at ~0.3 m/s to load.
  - Bull wheels are 4–6 m across.
  - Drive is at one end and tension at the other.

### 4.2 Tricable (3S)
- **Peak 2 Peak:** a **3,024 m unsupported span**, 436 m above the ground, 28 cabins of 28, 7.5 m/s, 2,050 pph, a
  46 mm haul rope [3][4].
- Two fixed track ropes and one haul rope make it very wind-stable.
- **This is the model for the islands' line: a single span with no towers.**

### 4.3 Aerial tramway (reversible "jig-back")
- Two cabins on track ropes counterbalance each other, one up while the other comes down [44].
- **Vanoise Express:** 200-person double-deck cabins, ~1.8 km span, 380 m up, ~12.5 m/s, ~4 min [43][44].
- **Roosevelt Island:** 109 + 1 attendant a cabin, 960 m, 7.6 m/s [45].
- **Every tram cabin carries an attendant** [45]. This is the islanders' "cabin warden" post.

### 4.4 Cargo ropeways
- Holcim Dotternhausen: 2.3 km, 138 buckets, 450 t/h [51].
- Buriticá: 1.4 km bicable, 175 t/h [52].
- Mining tramways move 50–500 t/h [100].
- **The skybox (2 t) on a cargo jig-back fits this world.**

### 4.5 Crews, inspection, rescue
- **Regulation:** ANSI B77.1 as adopted by each state, e.g. Massachusetts 526 CMR 10 [49]:
  - certified inspectors;
  - non-destructive testing;
  - "attendants" aged 16 or over under an Operator.
- **Rope testing:** magnetic rope testing under EN 12927-8 [50].
- **Evacuation:**
  - Germany: everyone off within 3.5 h [47]; Colorado: 2 h on a chairlift [48].
  - Methods: lower riders from the rope, or send a rescuer out on a traverse trolley [48].
  - Kicking Horse 2025: a manual evacuation of 184 guests took ~5.5 h [46].
  - The rule is restart first (a backup drive), rope rescue second.
- **Crews (GK):** each station has an operator in a booth and 1–2 attendants; there are maintenance mechanics and
  electricians, and patrol/rescue. A daily inspection run comes before opening.

### 4.6 Airships and aerostats
- **Hindenburg at Lakehurst:** a 200+ ground crew. The "flying moor" drops lines from altitude to be winched in, which
  needs fewer hands [53].
- **Goodyear blimp:** a field crew of 16–20 (pilots, crew chiefs, mechanics, broadcast), with a hydraulic mast truck
  [54].
- **TARS:** a single tether rated to 26,000 lb, 7.6 km on a winch, flying up to 4.6 km [55][56].
- **What this means for the islands:** the first gondola's crew of 24 is about one blimp field crew plus a shift of
  riggers. That is a believable number to rig a mooring, set the ground anchors and open the station.

### 4.7 Physics check for an anchored island (my own estimate)
- **Drag per balloon:** a balloon is 100 m across and 1,000 m tall, so ~1e5 m² frontal. In a 6.5 m/s wind with
  Cd ≈ 0.6–0.8, drag = 0.5·1.1·6.5²·0.7·1e5 ≈ **1.6 MN, ~165 t-force per balloon**.
- **Per island:** 3–17 balloons, so 0.5–2.8 kt-force.
- **Holding it:**
  - **many hawsers to buried deadmen** (16–24 of them; each ≥ 2 MN breaking load, like a big ship's mooring line);
  - a **wind window**: an island moors only below a set wind speed;
  - the islands' own trim: in the canon they choose their altitude for the wind.
- **The game's rule:** mooring fields have permanent ground anchors (the cities built them by treaty), and the islands
  moor only when the forecast is light. The weather reader decides (§00 §5).
- **Altitude:** a moored island descends to the low end of its band (600 m) to shorten the lines.

## 5. The Roma and Traveller reference (for the settled Aloft, handled respectfully)

### 5.1 History
- **Origins (GK):** groups left northern India about 1,000+ years ago; Romani is an Indo-Aryan language.
- **The 1971 First World Romani Congress:** the flag (blue sky over green earth, a red chakra) and the anthem
  "Gelem, Gelem" [85].
- **Slavery:** Roma were enslaved in Wallachia and Moldavia for ~5 centuries until 1855–56. The owners, not the
  enslaved, were compensated [87][88].
- **The Porajmos:** estimates of 150,000–500,000+ dead, and late recognition [86].

### 5.2 Forced sedentarisation (the pattern the settled Aloft echo)
- **Habsburgs (18th century):** forced settlement; bans on dress, language and customs; renaming; children
  removed [57].
- **Czechoslovakia:** Law 74/1958 "On Permanent Settlement of Nomadic People", repealed only in 1998 [57][58][59].
- **Ireland:**
  - The 1963 Commission on Itinerancy aimed to absorb Travellers; settlement committees were set up from 1969.
  - The Commission itself found that nomadic Travellers earned well while settled ones struggled [60][61].
  - Traveller ethnicity was recognised only in 2017.
- **Scotland:** the Nawken were driven to settle by camp closures, school laws and mass-made goods that undercut their
  trades [74][75].
- **The structural pattern:** imposed settlement → lost trades → stigma → dependence, which is then blamed on the
  community. It is **not a cultural trait**.

### 5.3 Discrimination today (EU FRA 2025) [68]
- 31 % report discrimination.
- 70 % live in poverty, ~4x the general rate.
- 47 % live in poor housing and 83 % in overcrowded homes.
- 32 % finish upper secondary school, against 84 % generally.
- 46 % of children are in segregated schools.

### 5.4 Trades and institutions
- **Kalderash:** coppersmiths, today often in auto-body work; subgroups (vitsa) form by trade [67].
- **Scottish Travellers:**
  - tinsmiths, hawkers, horse dealers, pearl fishers;
  - berry-picking seasons that doubled as gatherings;
  - a great ballad and story tradition [74][75].
- **The Showmen's Guild of Great Britain** (1889, ~4,700 members) [62][63]:
  - an occupational community with winter-quarter yards;
  - **the model for the settled Aloft's "Line Hall" guild.**
- **Appleby Horse Fair:** ~10,000 Gypsies and Travellers plus ~30,000 visitors; reunion, trade and pride [64][65].
  - **The model for the settled Aloft's annual "Low Lashing" fair.**

### 5.5 Naming
- **Endonyms:** Rom/Roma, Sinti, Romanichal, Kale, Manouche, Nawken; Irish Travellers are Pavee/Minceir (GK).
- **Outsiders:** gadje (non-Roma) [66].
- **"Gypsy"** is contested: some groups embrace it and many reject it, so use the group's own name [91][92][93].

### 5.6 Guidance and pitfalls
- **The Council of Europe (2024) [5], ERIO [6] and antigypsyism.eu [7] say:**
  - no dehumanising language;
  - not a monolith;
  - give members agency;
  - not only crime and poverty, but contributions too;
  - explain hardship by structural causes;
  - involve community experts.
- **Avoid:**
  - thieves, child-snatchers;
  - curses and mystic powers, fortune-teller crones;
  - the "exotic" seductress;
  - dirt and scrap as identity;
  - welfare cheats;
  - campfire romanticism;
  - "they choose poverty".
- **Games:** the fortune-teller trope recurs [69]. D&D's Vistani needed two revisions with a Romani consultant [70]–[72].
  A Dutch thesis built its characters through community interviews [73].
- **This plan applies it** (§00 §9):
  - an invented culture (the Aloft already have their own lexicon, customs and faiths), with no borrowed Romani words or
    symbols;
  - hardship comes from the institutions (the Registry, housing, hiring), not from the people;
  - individuals of every trade and view;
  - their own institutions (the Line Hall, the Low Lashing);
  - a sensitivity read recommended before the story uses them.

---

## Sources
1. Pasadena Now, Rose Bowl Flea Market turns 58 – https://www.pasadenanow.com/weekendr/rose-bowl-flea-market-turns-58-this-year-and-still-fills-a-stadium-parking-lot-every-month/
2. Fleamapket, Rose Bowl – https://www.fleamapket.com/listing/rose-bowl-flea-market
3. Wikipedia, Peak 2 Peak Gondola – https://en.wikipedia.org/wiki/Peak_2_Peak_Gondola
4. Doppelmayr, record ropeway for Whistler – https://newsroom.doppelmayr.com/tr/doppelmayr/press/doppelmayr-builds-record-setting-ropeway-for-whistler-mountain
5. Council of Europe, Roma/Traveller discrimination in broadcasting – https://coe.int/en/web/roma-and-travellers/-/council-of-europe-study-outlines-recommendations-to-stop-discrimination-against-roma-and-traveller-communities-in-broadcasting
6. Romea, ERIO ethical journalism – https://romea.cz/en/world/erio-calls-for-an-ethical-journalism-free-of-stereotypes-and-prejudices/
7. antigypsyism.eu, Media Representation – https://antigypsyism.eu/wp-content/uploads/2026/03/VII.-Media-Representation-1.pdf
8. New England Today, Brimfield – https://newengland.com/travel/massachusetts/brimfield-antique-show/
9. Antiques and the Arts, Brimfield spring – https://www.antiquesandthearts.com/spring-antiques-season-explodes-in-brimfield
10. Wikipedia, First Monday Trade Days – https://en.wikipedia.org/wiki/First_Monday_Trade_Days
11. D Magazine 1996, First Monday Madness – https://www.dmagazine.com/publications/d-magazine/1996/august/day-trips-first-monday-madness/
12. Thai Holiday Guide, Chatuchak – https://www.thaiholidayguide.com/bangkok/chatuchak-weekend-market
13. Saint-Ouen map PDF – https://www.fleamarketinsiders.com/wp-content/uploads/2014/10/Paris-St-Ouen-flea-market-MAP.pdf
14. Puces de Paris Saint-Ouen – https://www.pucesdeparissaintouen.com/en/?p=40
15. Wikipedia, El Rastro – https://en.wikipedia.org/wiki/El_Rastro
16. San Diego Magazine, Kobey's Swap Meet – https://sandiegomagazine.com/everything-sd/living-design/inside-the-icon-kobeys-swap-meet-2/
17. OnePlan, fair fire-lane requirements (IFC) – https://www.oneplan.io/articles/?p=446
18. Albuquerque Fire Marshal, craft show application – https://www.cabq.gov/fire/documents/fire-marshal-office-community-arts-craft-show-application.pdf
19. Alamo TX code, flea markets – https://codelibrary.amlegal.com/codes/alamo/latest/alamo_tx/0-0-0-15924
20. Nock, swap meets (Human Organization) – https://research-portal.najah.edu/migrant/32335/
21. Meet Me at the Swap Meet (eScholarship) – https://escholarship.org/uc/item/18r0k0m7
22. Dumbarton Oaks, Markets in a Cosmopolitan City – https://www.doaks.org/newsletter/markets-in-a-cosmopolitan-city
23. Essential Supplies, 50 m festoon – https://www.essentialsupplies.co.uk/black-belt-festoon-50m-with-50-es-lampholders-1m-spacing.html
24. STLS Events, festoon hire – https://stlsevents.co.uk/equipment/lighting-hire/festoon-lighting/
25. Aqualux AQF-C datasheet – https://cdn.shopify.com/s/files/1/2129/3845/files/AQUALUX_AQF-C.pdf
26. FSG, parking lot lighting calculator – https://fsg.com/resources/parking-lot-lighting-calculator/
27. ParkingBOXX, lighting standards – https://parkingboxx.com/blog/operations/parking-lot-lighting-standards/
28. City of Richmond, Lighting Standards – https://Rva.gov/sites/default/files/2020-01/Lighting%20Standards.pdf
29. Wikipedia, Shilin Night Market – https://en.wikipedia.org/wiki/Shilin_Night_Market
30. Wikipedia, Grand Bazaar Istanbul – https://en.wikipedia.org/wiki/Grand_Bazaar,_Istanbul
31. IBB, Grand Bazaar – https://istanbulseninhaber.ibb.istanbul/haber-detay/grand-bazaar-the-shopaholics-paradise
32. Wikipedia, Shamiana – https://en.wikipedia.org/wiki/Shamiana
33. Wikipedia, Khatwa – https://en.wikipedia.org/wiki/Khatwa
34. V&A, Textiles and architecture in India – https://www.vam.ac.uk/blog/fabric-of-india/textiles-and-architecture-in-india
35. Pagoda tent listing – https://china.org.ru/product/60344941771
36. Averto, Pagoda 6x6 – https://averto.lt/en/event-tents-pvc-pe/pagoda-tents/pagoda-pag6250-6x6-m-full/
37. Borovka Rental, stretch tent 10x15 – https://borovkarental.com/stretch-tent-10x15-m_z1763
38. Sisoluzioni, Bedouinflex (the search returned a garbled URL; re-find before citing)
39. Programming Insider, 10x20 canopy weights – https://programminginsider.com/how-much-weight-is-needed-to-hold-down-a-10x20-canopy-tent/
40. Wikipedia, Awana Skyway – https://en.wikipedia.org/wiki/Awana_Skyway
41. Leitner, detachable gondolas – https://www.leitner.com/en/products/ropeway-systems/detail/detachable-gondola-lifts/
42. Leitner, types of ropeway – https://www.leitner.com/en/company/useful-information/types-of-ropeway/
43. Skiresort.info, Vanoise Express – https://www.skiresort.info/ski-resort/les-arcs-peisey-vallandry-paradiski/ski-lifts/l95343/
44. Remontees-mecaniques.net, téléphérique bicâble – https://www.remontees-mecaniques.net/dossier/page-le-telepherique-bicable-45.html
45. Wikipedia, Roosevelt Island Tramway – https://en.wikipedia.org/wiki/Roosevelt_Island_Tramway
46. Technical Safety BC, Appendix Q evacuation – https://files.technicalsafetybc.ca/v3/assets/bltdec2ded849740f4d/bltbcb17fc17f72f74b/698a72285d2e570eb939239e/Appendix_Q_-_Evacuation_and_Emergency_Response.pdf
47. DGUV, rescue on aerial railways – https://www.dguv.de/ifa/forschung/projektverzeichnis/bgia_5103-2.jsp
48. US Patent 4934277, aerial rescue – https://patents.google.com/patent/US4934277
49. 526 CMR 10.00 (Cornell LII) – https://www.law.cornell.edu/regulations/massachusetts/department-526-CMR/title-526-CMR-10.00
50. TÜV Austria, magnetic rope testing – https://en.tuv.at/?p=5420
51. Bartholet, Dotternhausen material lift – https://www.bartholet.swiss/en/ropeways/material-lifts/material-lift-dotternhausen-germany
52. E&MJ, Buriticá ropeway – https://www.e-mj.com/departments/suppliers-report/buritica-commissions-1-4-km-ropeway/
53. Wikipedia, Hindenburg disaster – https://en.wikipedia.org/wiki/Hindenburg_disaster
54. AviationPros, Goodyear airship operations – https://www.aviationpros.com/aircraft-maintenance-technology/aircraft-technology/business-general-aviation/blog/10754567/goodyear-airship-operations
55. Wikipedia, TARS – https://en.wikipedia.org/wiki/Tethered_Aerostat_Radar_System
56. USAF, TARS fact sheet – https://www.acc.af.mil/About-Us/Fact-Sheets/Display/Article/199137/tethered-aerostat-radar-system/
57. Wikipedia, Romani people in Slovakia – https://en.wikipedia.org/wiki/Romani_people_in_Slovakia
58. Romea, Czechoslovakia sedentarisation – https://romea.cz/en/world/february-marks-the-62nd-anniversary-of-communist-czechoslovakia-forcibly-sedentarizing-romani-people
59. ERRC, nomadic ban lifted – https://www.errc.org/cikk.php?cikk=1789
60. Al Jazeera, Irish Travellers – https://www.aljazeera.com/features/2017/2/24/the-long-road-towards-acceptance-for-irish-travellers
61. Minority Rights Group, Travellers – https://minorityrights.org/minorities/travellers
62. Wikipedia, Showmen's Guild of Great Britain – https://en.wikipedia.org/wiki/Showmen%27s_Guild_of_Great_Britain
63. Herefordshire Council, travelling showpeople's sites – https://www.herefordshire.gov.uk/downloads/file/14107/ps07---travelling-showpeoples-sites---a-planning-focus-model-standard-package-revised-september-2007
64. Visit Appleby, Horse Fair – https://visitappleby.com/?p=2250
65. National Geographic, Appleby Fair – https://www.nationalgeographic.com/premium/article/appleby-fair-gypsy-traveler-romany-gathering
66. Wikipedia, Gadjo – https://en.wikipedia.org/wiki/Gadjo
67. Wikipedia, Kalderash – https://en.wikipedia.org/wiki/Kalderash
68. FRA, Roma and Travellers survey 2025 – https://fra.europa.eu/sites/default/files/fra_uploads/fra-pr-roma_and_travellers_survey-2025.pdf
69. UCL Discovery, fortune-telling Romani characters – https://discovery.ucl.ac.uk/id/eprint/10207224
70. Vistani in D&D (2024) – https://yadda.icm.edu.pl/cejsh/element/bwmeta1.element.ojs-doi-10_15804_em_2024_04_12
71. Wikipedia, Vistani – https://en.wikipedia.org/wiki/Vistani
72. TheGamer, Curse of Strahd Vistani changes – https://www.thegamer.com/curse-of-strahd-revamped-what-changes-vistani/
73. Saxion thesis, Roma representation – https://hbo-kennisbank.nl/details/saxion_scripties:8367153e-3f0e-4f36-b707-2575c3aa854c
74. Tobar an Dualchais, travelling folk – https://tobarandualchais.co.uk/blog/travelling-folk-and-a-rich-well-of-tradition?l=en
75. Books from Scotland, Going to the Berries – https://booksfromscotland.com/book/going-to-the-berries-voices-of-perthshire-and-angus-seasonal-workers/
76. Flea Market Insiders, Portobello Road – https://www.fleamarketinsiders.com/portobello-road/
77. berlin.de, Mauerpark – https://www.berlin.de/en/shopping/markets/flea-markets/1998222-2983302-flohmarkt-am-mauerpark.en.html
78. Fleamapket, Mauerpark – https://www.fleamapket.com/listing/mauerpark-flea-market
79. The National, the fanous – https://thenational-the-national-prod.cdn.arcpublishing.com/mena/egypt/2022/04/01/the-history-of-the-fanous-cairos-traditional-ramadan-lantern
80. The New Arab, Fanoos history – https://www.newarab.com/features/fanoos-ramadan-history-holy-months-iconic-lanterns
81. Shipshewana vendor application – https://shipshewanatradingplace.com/wp-content/uploads/2025/03/flea-market-vendor-application.pdf
82. Shipshewana 2018 rules – https://shipshewanatradingplace.com/uploads/downloads/2018_Flea_Market_Rules__Regulations.pdf
83. MPT flea market space fee – https://mptevents.regfox.com/2019-flea-market-bazaar-space-fee
84. Alameda Point Antiques Faire – https://alamedapointantiquesfaire.com/about/
85. Wikipedia, World Romani Congress – https://en.wikipedia.org/wiki/World_Romani_Congress
86. Wikipedia, Romani Holocaust – https://en.wikipedia.org/wiki/Porajmos
87. Radio Romania International, Roma slavery – https://rri.ro/en/features-and-reports/the-history-show/slavery-and-emancipation-of-the-roma-in-romania-2-id724379.html
88. ERRC, 170 years after slavery – https://www.errc.org/news/170-years-after-slavery-roma-did-not-gain-freedom-from-racism
89. LearnArchitecture, parking dimensions – https://learnarchitecture.net/landscape-architecture/urban-design/35635-standard-parking-space-dimensions.html
90. Univ. of Tennessee CPA-222, event parking – https://utia.tennessee.edu/cpa/wp-content/uploads/sites/106/2020/10/CPA-222.pdf
91. Wikipedia, Gypsy, Roma and Traveller – https://en.wikipedia.org/wiki/Gypsy,_Roma_and_Traveller
92. Devon County Council, GRT support – https://www.devon.gov.uk/support-schools-settings/?p=20639
93. East Sussex, GRT advice – https://thestoppingplace.eastsussex.gov.uk/assets/documents/Advice__Information_-_Gypsy%2C_Roma_and_Traveller_Groups.pdf
94. Kranzberg Arts Foundation, Big Top – https://kranzbergartsfoundation.org/wp-content/uploads/2023/03/Big-Top-Handout_23.pdf
95. V&A, Chipperfield big top – https://collections.vam.ac.uk/item/O195646/
96. Palisadian-Post, Cirque Totem – https://www.palipost.com/circus-comes-town
97. Novelty Lights, S14 commercial string – https://www.noveltylights.com/15-led-s14-warm-white-commercial-grade-suspended-light-string-set-on-48-of-black-wire
98. Eating the World, Djemaa el Fna – https://eatingtheworld.net/2012/12/11/food-and-life-in-the-djemaa-el-fna/
99. Snow Industry News, Obergurgl Rosskarbahn – https://snowindustrynews.com/articles/obergurgls-new-10-seater-rosskarbahn-gondola-ready-for-winter
100. Firgelli, rope tramway mechanism – https://www.firgelliauto.com/blogs/mechanisms/rope-tramway

Gaps: souk alcove sizes, Moroccan lantern sizes, TARS crew size and rope-test intervals were not found with sources.
