# hejazi_roshan: the Red Sea coral-stone port (Jeddah al-Balad)

## Sources and examples
- **Nasseef House:** coral limestone tied by teak beams; four storeys at the front and seven at the back; once
  Jeddah's tallest building; about 50 rooms.
  - https://perceptivetravel.com/blog/2012/09/05/discovering-jeddahs-old-town/
  - https://daughterofthewind.org/?p=8022
- **Coral tower houses:** five to seven storeys of coral limestone ("al-Mangabi") cut from the Red Sea; teak
  imported from India and Indonesia. https://houseofsaud.com/?p=30756
- **Rawashin:**
  - Natural brown is the oldest colour; green has been widespread since 1932; blue appears too.
  - Carved designs include circles, crescents, arrows and stars.
  - https://traveltomorrow.com/discovering-jeddahs-rawashin-a-heritage-that-defies-history/
- **Roshan vs mashrabiya:** https://archup.net/roshan-vs-mashrabiya-and-mashrabiya-a-dialogue-of-light-and-shadow-in-islamic-architecture/
- **Revival work:** Jeddah Culture Square, with white render, timber roshan and Manqabi panelling.
  https://www.ribaj.com/buildings/jeddah-culture-square-urko-sanchez-saudi-arabia/
- **Municipal colour rule (2001):** white, light blue, light beige, light yellow and light green.
  https://www.arabnews.com/node/216900
- **Overview:**
  - https://edition.cnn.com/travel/article/jeddah-al-balad-saudi-arabia
  - Google Arts & Culture story: https://artsandculture.google.com/story/zgVRYNXqDHVuCg

## Generator grammar
- **Cell and storeys:**
  - Grid 3.2 m (est.).
  - Storeys 3.2–3.6 m (high rooms for air).
  - Towers 4–7 storeys.
  - Footprint 10–16 × 10–18 m.
  - The tower is tall and slender; rooms ring a central stair, and often there's no courtyard at all.
- **Walls:**
  - Coral blocks set in courses, about 0.6 m thick at the base and 0.4 m above (est.).
  - Horizontal **teak tie-beams** (takaliel) every 0.6–1.0 m, set in the face and visible as dark lines.
  - Lime render, white to cream (`#efe9dc`, `#e3d6bd`).
  - Weathering: salt-grey streaks, and render falling off to show the grey coral (`#bcb5a5`) and brown beams
    (`#6b4a2e`).
- **Mass:**
  - Free-standing towers along lanes; their facades are almost entirely roshan.
  - Back elevations are taller where the ground falls (as at Nasseef).
  - Rooftop terraces are walled with **mangour** (a wooden lattice parapet) for sleeping in the sea breeze.
- **Streets:**
  - Lanes 3–6 m wide, chosen to funnel the sea breeze (est.), with small plazas at the mosques.
  - The souq al-'Alawi is a long covered spine.
  - Lanes are fairly straight compared with a Maghrebi medina: a semi-regular grid bent to the old wall and the
    gates.
- **Growth:**
  - E1: tower houses of merchants.
  - E2: upper floors added and roshans stacked into full-height columns, joining across floors.
  - E3: concrete annexes, AC units hung in roshan openings.
  - E4: roshan screens made into LED-lit kinetic panels.
- **Openings (the mark): the roshan.**
  - A projecting timber oriel 0.5–0.9 m deep, 1.5–3 m wide, one storey tall (2.8–3.4 m).
  - Stacked vertically into **columns 2–6 storeys tall**, sometimes merged side by side across a whole facade.
  - Lower panels are solid carved boards; the middle is louvred shutters and lattice; the top is a carved
    cresting or canopy.
  - Each roshan stands on carved brackets and carries a little hood.
  - Colour: natural teak brown `#6b4a2e`, green `#2f6b4f`, blue `#2e5d8a`, sometimes white trim.
  - Lesser windows are small and square, with wooden shutters painted the same.
- **Roofs:** flat terraces with wooden mangour screens 1.5–2 m tall (est.), a stair house, and water tanks.
- **Ornament:**
  - The wood carries it all: the roshan cresting, pierced star and crescent cut-outs, door panels.
  - Masonry is plain; doors are big, carved teak, double-leaved.
- **Public spaces:**
  - small squares (barha) at each quarter mosque, the souq spine, the Gate of Mecca square;
  - a waterfront.
  - The game adds a grand paved axis on the old wall line to a harbour plaza.
- **Water:**
  - historic cisterns (sahrij) and water sellers' jars;
  - a few wall fountains (sabil) with brass taps.
- **Plants:**
  - sparse in the lanes, but neem trees (*Azadirachta indica*, a dense rounded crown 8–10 m) and doum and date
    palms in squares;
  - bougainvillea spilling from rooftop terraces;
  - potted herbs on roshan sills.
- **Cyberpunk overlay:**
  - Roshans become giant LED lattice screens, each panel pixel-lit and playing slow patterns (stars, crescents).
  - Neon Arabic calligraphy runs along the souq.
  - Container-like boxes sit on roofs.
  - Fibre bundles run up the takaliel beams; AC units nest in the roshan bottoms.
  - Port cranes and hoist arms stand at the island's rim.
- **Night:** warm amber light glows through roshan lattice and casts patterned shadows on the lanes; the green and
  blue roshans are backlit. The souq has string lights.

## Kit
- **Common pieces:**
  - `wall_panel` (coral stone, lime render), `band` (timber tie-beam line, dark);
  - `bay_window_box` (preset `roshan_bay`: deep, full storey, louvred, crested, column stacking);
  - `screen_lattice` (slat and louvre patterns);
  - `door_plank` (carved), `parapet_screen` (mangour), `roof_flat_terrace`;
  - `awning`, `water_tank`, `ac_unit`, `led_screen`, palms and neem.
- **Parameters that make it Hejazi:**
  - Roshans cover 40–70% of the street facade and stack vertically into continuous columns.
  - A dark timber line every 0.8 m in the masonry.
  - White and cream walls with green, blue or brown woodwork.
  - Towers twice as tall as wide; rooms 3.4 m high.
- **Unique pieces (2):**
  - `roshan_crest` (the carved canopy top of a roshan column);
  - `mangour_panel` (the rooftop wooden lattice wall).
