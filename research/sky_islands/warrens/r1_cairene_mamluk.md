# cairene_mamluk: the Cairene Mamluk–Ottoman quarter (al-Gamaliyya, al-Mu'izz, Darb al-Asfar)

## Sources and examples
- **Bayt al-Suhaymi (1648 and 1796):**
  - A sahn courtyard; the qa'a with a domed vent; a malqaf wind catcher; mashrabiya screens over the court.
  - Salamlik and haramlik; a maq'ad loggia on the second floor.
  - https://en.wikipedia.org/wiki/Bayt_al-Suhaymi · https://archnet.org/sites/2195 ·
    https://egymonuments.gov.eg/monuments/bayt-al-suhaymi-house-of-suhaymi/
- **Mashrabiya construction:** turned wooden bobbins jointed in polygonal grids; bars from 10 cm to 1 m depending
  on scale. https://architecturecourses.org/design/mashrabiya-designs · https://www.metmuseum.org/art/collection/search/456339
- **Street-type terms in Cairo:** used inconsistently, except sharʿi' for the main road.
  https://ntnu.no/trykk/publikasjoner/hosiar_nooraddin/HTML/files/assets/basic-html/page-191.html
- **Wikala and rab' (comparative, from my own knowledge):**
  - Ground-floor storerooms round a court, with rental apartments (rab') stacked above in duplex units.
  - Examples: Wikala of al-Ghuri, Bab al-Wazir rab'.
- **Hisba manual of Ibn al-Ukhuwwa:** roofing over alleys is an infraction (restricting movement), so sabats are
  argued over (via the NTNU study above).

## Generator grammar
- **Cell and storeys:**
  - Grid 3.0 m.
  - Ground 4.0 m (shops and storage); qa'a halls double height (6–8 m); upper floors 3.2 m.
  - Houses 3–4 storeys; rab' blocks 4–5.
- **Walls:**
  - Dressed limestone ground floors `#cfbf9f`, `#d8c8a6`, often with ablaq-striped portals (red/white
    `#a3523b`/`#e8dcc4`, or black and white).
  - Upper floors brick and timber, plastered ochre and pink-buff `#c9a77d`, `#d4b48f`.
  - Weathering: thick dust, soot, plaster loss; Cairo's general patina is ochre-grey.
- **Mass:**
  - Courtyard houses with L-shaped rooms round a sahn.
  - Commercial blocks (wikala) as big stone boxes with an inner court.
  - Mosque-madrasa complexes with a dome and minaret at street corners, angled to the street ("the street wall
    follows the street, the qibla turns inside").
- **Streets:**
  - Qasaba (al-Mu'izz): the 6–10 m spine, lined with monuments.
  - Darb: 2–4 m, gated quarters (harat).
  - 'Atfa: cul-de-sacs 1–2 m.
  - Mashrabiyas overhang the street 0.5–1 m at each upper storey, stepping outward ("corbelled stacking"), so the
    sky narrows to a strip.
- **Growth:**
  - E1: Fatimid gates, Mamluk monuments.
  - E2: Ottoman houses and wikalas; upper floors stack, mashrabiyas multiply.
  - E3: 19th–20th-century apartment blocks with iron balconies, shops cut into everything, informal storeys on
    roofs (Cairo's "rooftop city" of shacks, pigeon towers and goat pens).
  - E4: a cyberpunk bazaar layer.
- **Openings (the mark): the mashrabiya.**
  - A projecting box oriel 0.5–0.9 m deep, 1–2.5 m wide, 1.6–2.4 m tall, often with a small kiosk on its sill (a
    water-jar niche).
  - Turned-wood lattice in fine beads: 3–4 cm bead pitch near eye level, coarser above.
  - On the street facade, mashrabiyas stack at 1st–3rd floor in vertical runs, each storey projecting a little
    further on corbels.
  - Ground floor: shop arches with shutters and wooden benches (mastaba).
  - Portals: tall recessed pointed arches with muqarnas hoods.
- **Roofs:**
  - flat terraces with low parapets;
  - the **malqaf** (wind scoop): a slanted timber or brick hood 1–2 m above the roof, facing north;
  - small domes over the qa'a (a lantern with windows);
  - **minarets**, tall (30–50 m), of stacked octagonal and cylindrical shafts with balconies and a bulb finial;
  - **stone domes** (ribbed and carved with arabesques) over mausolea.
  - The roof clutter of E3: pigeon cotes (tall timber cages), sheds.
- **Ornament:**
  - carved stone bands of calligraphy on monuments, ablaq, muqarnas;
  - houses: wood (mashrabiya, carved ceilings).
- **Public spaces:**
  - the qasaba itself;
  - mosque courtyards (sahn of al-Azhar, ibn Tulun);
  - small squares at gates (Bab Zuwayla);
  - wikala courtyards (public by day);
  - sabil-kuttab corners (a fountain below, a Qur'an school above).
- **Water:**
  - the **sabil** (a public water dispenser) with bronze grilles at corners;
  - courtyard fountains (fasqiya);
  - cisterns under the sabils.
- **Plants:**
  - sparse; a single tree in a courtyard, typically a **sycamore fig** (*Ficus sycomorus*, a massive spreading
    crown) or **date palm**;
  - **henna** and **jasmine**;
  - pots on roofs; **mango** and **neem** in later gardens;
  - vines over the maq'ad.
- **Cyberpunk overlay:**
  - The mashrabiya becomes the city's display: backlit, LED in its lattice, cycling text in the beads.
  - Minarets carry ring lights and antennas.
  - Pigeon cotes and rooftop shacks are lit with fluorescent tubes.
  - Shops spill with LED lightboxes, and festoons hang across the qasaba.
  - Cable bundles cross the lanes at every storey.
- **Night:**
  - Gold lattice glow from the mashrabiyas, green-lit minarets (Cairo's mosques use green light), the bright qasaba.
  - Rooftops dotted with blue TV light.

## Kit
- **Common pieces:**
  - `wall_panel` (stone ground floor, plaster uppers), `band` (ablaq, calligraphy band);
  - `bay_window_box` (preset `mashrabiya_box`: corbelled, fine turned lattice, sill kiosk);
  - `arch_opening` (pointed portal with muqarnas), `door_*`, `shutters`, `awning`, `market_stall`;
  - `malqaf` (scoop), `dome_ribbed`, `minaret_small` (tall Mamluk preset);
  - `rooftop_shack`, `pigeon_loft`, `vault_barrel`.
- **Parameters that make it Cairene:**
  - mashrabiya runs on 40–60% of the upper street facades, stepping out per storey;
  - narrow sky between them;
  - the ochre-dust palette;
  - tall minarets every 80–150 m along the spine;
  - a stone ground floor and plastered upper floors;
  - a thick roof clutter of cotes and shacks.
- **Unique pieces (3):**
  - `malqaf_scoop`;
  - `minaret_mamluk` (stacked octagon + cylinder + bulb, with balconies; built from `minaret_small` stages if
    possible);
  - `pigeon_cote` (a tall lattice tower; exists as `pigeon_loft`).
