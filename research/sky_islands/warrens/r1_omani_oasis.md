# omani_oasis: the Omani falaj oasis town (Bahla, Nizwa, al-Hamra, Misfat; Muttrah for the port variant)

## Sources and examples
- **UNESCO, Bahla:**
  - The mud-brick harats (al-Aqr, al-Ghuzeili, al-Hawulya) with their mosques, sablas (audience halls) and baths
    show a settlement pattern tied to the falaj.
  - The sur wall with sentry walk and watchtowers encloses "the labyrinth of mud brick dwellings and cultivatable
    land".
  - https://whc.unesco.org/en/list/433
- **Al-Aqr:** 177 mud-brick buildings still in their original form. https://omanpocketguide.com/?p=4135
- **Falaj channels shaping lanes and house placement** (a tourism source, unverified):
  https://kupi.com/en-ae/explore/oman-sultanate-of/bahla/history
- **Muttrah:** white and pastel houses with balconies, carved wooden balconies on the waterfront, lattice fronts by
  the mosque. https://mashallahnews.com/strolling-in-old-muscat/ ·
  https://omanwanderlust.com/things-to-do-in-muttrah-oman-muscats-old-city
- **Comparatives (from photographs):** al-Hamra's 3–4 storey mud houses on a rock ledge; Misfat al-Abriyeen
  terraced over falaj gardens.

## Generator grammar
- **Cell and storeys:**
  - Grid 3.0 m.
  - Storeys 3.0 m.
  - Houses 2–3 storeys; towers (burj) 3–5.
  - Footprints 8–14 m.
- **Walls:**
  - Mud brick or rubble stone, mud-plastered: ochre to red-brown `#a5774a`, `#8f6440`, `#b98c5f`.
  - 0.5–0.8 m thick, with a slight batter.
  - Rounded tops and corners.
  - Wooden beam ends (palm trunk or *kandal* mangrove poles) project from walls at each floor line.
  - Weathering: rain gullies and eroded corners; ruined abandoned houses mixed in, which suits the game's layers.
- **Mass:**
  - Compact clusters of courtyard-less houses with roof terraces.
  - Lots of blank wall; small high windows.
  - A fort or castle (Bahla, Nizwa's round tower) dominates.
  - The sur wall rings everything, with gate towers.
- **Streets:**
  - Lanes 1.5–3 m, irregular, following the **falaj**: the channel (0.3–0.6 m wide, stone-lined, running water)
    runs along the lane edge or down its centre and branches into the gardens.
  - Arched gates (sabah) between quarters.
  - Covered passages under rooms.
- **Growth:**
  - E1: harats on a rise above the gardens.
  - E2: houses climb and add floors; towers are added.
  - E3: concrete houses outside the walls, AC units punched into mud walls.
  - E4: falaj-fed vertical gardens and light lattices.
- **Openings:**
  - small rectangular windows with timber lintels and painted shutters (blue, green);
  - **carved wooden doors**, studded and painted: the Omani signature;
  - pointed or scalloped arches in mosque prayer halls;
  - ventilation slits.
- **Roofs:**
  - flat roofs of palm trunks, palm-frond mats and mud;
  - parapets with stepped triangular merlons (the Omani crenel) and occasional corner pinnacles;
  - mosques have small domes and stepped minarets only rarely.
- **Public spaces:**
  - the souq (Nizwa's covered souq near the fort);
  - the fort square;
  - the falaj distribution point (a shared bathing place, for men and for women separately);
  - date gardens as the green heart: a great green mass of palms.
- **Water:** falaj channels everywhere, a stepped access well (shari'a), and small round cisterns.
- **Plants:**
  - date palm groves, the dominant species: 8–15 m with a crown of 30–40 fronds, under-planted with limes,
    bananas, mango and alfalfa;
  - **ghaf** and **sidr** trees in squares;
  - roof gardens are rare, but palm-frond shade structures (arish) stand on roofs.
- **Cyberpunk overlay:**
  - The falaj glows: channels with cold blue-white light strips under the water.
  - The fort walls are mapped with projections.
  - Palm-frond shades are replaced by solar shade sails.
  - Sparse neon.
  - Doors carry LED inlay in their studs.
  - The burj towers carry antennae.
- **Night:** low and calm. Warm lantern light in doorways, blue falaj light along the lanes, and the fort lit from
  below.

## Kit
- **Common pieces:**
  - `wall_panel` (mud, rounded corners, beam ends), `parapet_crenel` (triangular merlon variant);
  - `door_studded` (painted), `window_small` + `shutters`;
  - `tower_square` / `round_tower`, `covered_alley`, `falaj_channel`;
  - `roof_flat_terrace`, palm shade structure (`timber_pergola` with frond mat);
  - date palm, `fountain_basin`.
- **Parameters that make it Omani:**
  - low (2–3 storeys) under a big fort;
  - ochre earth with palm beam ends every storey;
  - triangular crenels;
  - few, small openings, but big ornate doors;
  - green and blue painted wood;
  - a sea of date palms;
  - water channels in every lane.
- **Unique pieces (2):**
  - `merlon_triangle` (the stepped triangular crenel);
  - `beam_end_row` (projecting palm-trunk or kandal ends).
