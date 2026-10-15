# silk_road: the Central Asian Silk Road city (Bukhara, Khiva, Kashgar, Herat)

## Sources and examples
- **Lyab-i Hauz, Bukhara:**
  - A pool about 46 × 36 m (1620) ringed by madrasas, shaded by old **mulberry** trees, with stone steps for the
    water carriers.
  - Nearly every mosque, madrasa and palace had a hauz.
  - https://en.wikipedia.org/wiki/Lyab-i_Hauz · https://orexca.com/uzbekistan/bukhara/lyabi_khauz_ensemble.htm
- **Bolo-Hauz mosque:** an **aivan** porch on 20 slender carved wooden columns, reflected in the pool (the "forty
  columns"). https://welcome.kz/en/uzbekistan/info-cities-uz/buxara/bolo-hauz
- **Khiva, Itchan Kala:**
  - Mud-brick walls 8–10 m high and 5–6 m thick, towers every 30 m.
  - Courtyard houses with an aivan on carved posts.
  - The Juma Mosque's 112 wooden columns.
  - https://whc.unesco.org/en/list/543 · https://en.wikipedia.org/wiki/Itchan_Kala ·
    https://www.turkestantravel.com/en/useful/architecture-of-khiva/
- **Kashgar old city:**
  - Two-storey houses of poplar timber and mud brick, walls 70–90 cm thick (against earthquakes).
  - Roofs of reeds, straw and mud; plain outside, with carved balconies and courtyards inside.
  - Winding unplanned lanes; much of it demolished and rebuilt since 2009.
  - https://www.chinahighlights.com/kashgar/attraction/kashgar-old-town.htm · https://apjjf.org/?p=26937 ·
    https://goasia.cc/en/article/kashgar-old-city · https://uhrp.org/?p=2307
- **Herat:**
  - A 1.2 km square city quartered by four streets meeting at the Chahar Su; the bazaar once covered.
  - Chahar Suq cistern (1634) under a 20 m brick dome.
  - Mud-brick courtyard houses behind high walls.
  - https://www.lonelyplanet.com/points-of-interest/old-city/451139 · https://archnet.org/sites/6411 ·
    https://sitara.com/about/element/herat/

## Generator grammar
- **Cell and storeys:**
  - Grid 3.0 m.
  - Storeys 3.2 m.
  - Houses 1–2 storeys (Kashgar up to 3 with stacked additions).
  - Courts 8–15 m.
  - Monuments are huge: madrasa portals (pishtaq) 15–30 m tall; minarets 30–50 m (the Kalon minaret is 45 m).
- **Walls:**
  - Mud brick, 0.7–0.9 m thick, mud-plastered: warm tan `#c7a57c`, `#b8946a`; Kashgar redder `#b88a63`.
  - Fired-brick monuments `#c9a37a` with patterned bonding.
  - **Glazed tile** (turquoise `#2aa7b5`, cobalt `#1f4f9e`, white) on portals, minarets and domes.
  - Weathering: mud erosion, patched brick, sun-bleached tiles.
- **Mass:**
  - Courtyard houses in mahallas (neighbourhoods, each with its own mosque, a hauz and a teahouse).
  - Monuments in ensembles (a kosh: two madrasas facing across a square).
  - Kashgar: tighter, with **upper rooms bridging lanes** and **wooden balconies on posts** projecting over the
    street, stacked and crooked.
- **Streets:**
  - main bazaar streets 4–8 m with domed crossings (toki in Bukhara: domed bazaar junctions);
  - mahalla lanes 2–3 m, crooked;
  - dead ends 1.5 m;
  - Kashgar lanes paved in brick with a hexagonal pattern (signposting dead ends by paving direction; a local
    tradition, est.).
- **Growth:**
  - E1: the ark (citadel) and the Friday mosque.
  - E2: mahallas fill in; Kashgar stacks rooms and balconies over the lanes.
  - E3: Soviet- and Chinese-era concrete, tin roofs.
  - E4: turquoise LED tile; aivan columns lit; prefab balcony pods.
- **Openings:**
  - street walls blank except for **carved wooden double doors** (Khiva doors: deep relief carving, a rounded top
    panel);
  - courtyard side: the **aivan**, a tall flat-roofed porch on slender carved wooden columns (0.25 m, 4–8 m tall,
    with a stalactite capital and a carved base on a stone pad);
  - wooden lattice windows (panjara) in geometric grids;
  - Kashgar: painted wooden balcony railings, green and blue.
- **Roofs:**
  - **flat earth roofs** with low parapets (houses);
  - domes on bazaars and baths (brick, sometimes turquoise tile);
  - **ribbed turquoise domes** on monuments;
  - **round tapering minarets** of patterned brick with a lantern top;
  - Khiva's stubby tiled Kalta Minor.
- **Ornament:** tile (mosaic and majolica) on portals and minarets; carved wood on doors and columns; ganch (carved
  plaster) inside.
- **Public spaces:**
  - **the hauz square under mulberries** with a teahouse (chaikhana) and its raised wooden platforms (tapchan,
    carpeted daybeds);
  - Registan-type squares between monumental portals;
  - domed bazaar crossings;
  - caravanserais.
- **Water:**
  - hauz pools (stone-stepped square tanks 10–50 m);
  - irrigation ariks (open channels along the lanes);
  - cisterns (sardoba: a domed reservoir).
- **Plants:**
  - **mulberry** (broad spreading 8–12 m, by the pools);
  - **poplar** (tall columnar 20 m: the Kashgar timber, in rows);
  - **elm** (karagach: shady, rounded);
  - **grapevine** on courtyard pergolas;
  - **apricot**, pomegranate;
  - roses in the courts; willows by water.
- **Cyberpunk overlay:**
  - turquoise and cobalt tile as LED panel facades on the monuments;
  - aivan columns with ring lights up the shafts;
  - tapchan daybeds glowing under festoons;
  - Kashgar balconies stacked with glowing prefab pods;
  - dome oculi with light beams;
  - market lanes hung with Uyghur-script and Cyrillic neon;
  - teahouse screens.
- **Night:** turquoise domes glowing, pools reflecting lit aivans, festooned chaikhanas, dark mud lanes with
  lantern doors.

## Kit
- **Common pieces:**
  - `wall_panel` (mud, thick, tan), `column_round` (aivan preset: slender carved, muqarnas capital),
    `gallery_timber` (Kashgar balcony);
  - `door_studded` (Khiva carved, rounded top), `screen_lattice` (panjara);
  - `pishtaq_portal`, `dome_ribbed` (turquoise tile), `minaret_small` (round tapering preset), `tile_panel`;
  - `hauz_pool`, `falaj_channel` (arik preset), `bench_platform` (tapchan);
  - `sabat_bridge`, mulberry, poplar, elm, vine.
- **Parameters that make it Silk Road:**
  - low mud houses with flat roofs;
  - giant tiled monuments in pairs across squares;
  - turquoise on domes and portals;
  - aivans with forests of slender columns;
  - a hauz under mulberries in every mahalla;
  - Kashgar's crooked stacked balconies.
- **Unique pieces (2):**
  - `aivan_column` (carved slender column with a stalactite capital);
  - `tapchan` (raised daybed platform).
