# rajput_sandstone: the Rajput desert sandstone city (Jaisalmer fort and town, Bikaner)

## Sources and examples
- **Patwon ki Haveli:**
  - A cluster of 5 interconnected mansions (from 1805, Guman Chand Patwa), the first five storeys tall.
  - Yellow sandstone, about 60 jharokhas, latticed carving; each storey a different design (a boat-shaped
    entrance feature, rectangular arched balconies, octagonal balconies).
  - A narrow lane; a fusion of Rajput and Mughal.
  - https://www.outlooktraveller.com/see/havelis-the-many-architectural-marvels-of-jaisalmer ·
    https://incredibleindia.gov.in/en/rajasthan/jaisalmer/patwon-ki-haveli · https://museumsofindia.org/museum/1647/kothari-s-patwon-ki-haveli-museum ·
    https://magikindia.com/en/patwon-ki-haveli-a-golden-poem-engraved-in-stone/
- **Jaisalmer Fort:**
  - A living fort with about 3,000 residents, honeycombed with narrow winding lanes of houses, temples, shops and
    guesthouses.
  - Yellow sandstone glowing honey-gold.
  - Bada Bagh royal chhatris (cenotaphs, 16th–20th century).
  - https://www.lonelyplanet.com/india/rajasthan/jaisalmer/attractions · https://odessia.com/destinations/india/jaisalmer ·
    https://www.travelwithjan.com/node/257

## Generator grammar
- **Cell and storeys:**
  - Grid 2.7 m.
  - Storeys 3.0 m.
  - Havelis 3–5 storeys; frontages 5–12 m.
  - Fort houses 2–3 storeys stacked against the bastions.
- **Walls:**
  - **Everything is yellow sandstone** (`#d6aa5f`, `#c99a52`, `#e1bb76`), dry-laid or limed ashlar in thin
    courses.
  - Carved stone screens and panels as cladding; no render.
  - Monolithic sandstone slabs for floors, roofs and chhajjas.
  - Weathering: a darker honey patina, soot, pigeon streaks, cracks in the bastions.
- **Mass:**
  - Haveli rows packed along lanes, each a deep house round a small court with a carved facade.
  - The **fort**: a ring of 99 rounded bastions (round towers) crowning a hill, the town spilling down the slope.
  - Temple clusters (Jain) with intricately carved spires (shikharas) inside the fort.
- **Streets:**
  - Fort lanes 2–4 m, stepped, winding, with the fort wall as one side.
  - Town bazaars 4–6 m.
  - Haveli lanes 2–3 m with facades meeting overhead in jharokhas.
  - Gates (pol) in zigzag sequences up the ramp.
- **Growth:**
  - E1: the fort and palace.
  - E2: havelis of merchants in the town; houses stacked on the bastions.
  - E3: guesthouse rooftop restaurants, concrete patched in yellow wash.
  - E4: rooftop pavilions of glass and stone lattice, jharokhas as lit pods, bastions with lookout lights.
- **Openings (the mark): the carved stone facade itself.**
  - **Jharokhas** in every bay, stacked over 3–5 storeys with each floor different (canted bays, octagonal bays,
    arched).
  - Projections 0.6–1.0 m on carved brackets, with **jali** screens of stone so fine they look like lace.
  - Chhajjas and **bangla** and domed caps on top.
  - The street facade is 70–90% carved projections.
  - Doors: carved stone frames with wooden doors painted blue or green.
- **Roofs:**
  - flat terraces with **chhatris** (sandstone domes on 4–8 columns: a roofscape of little domes);
  - parapets of jali;
  - rooftop restaurants with cushions and awnings (modern);
  - fort bastions rounded with crenellations.
- **Ornament:** carving everywhere on facades (floral, geometric, figurative bands, bells and lotus brackets);
  restrained in interiors except for mirror work.
- **Public spaces:**
  - the fort's Dussehra Chowk (the palace square);
  - temple courts;
  - **Gadisar Lake** (a big tank with ghats and chhatri pavilions in the water: the model pond);
  - bazaar squares;
  - Bada Bagh cenotaph gardens.
- **Water:**
  - **Gadisar-type tanks** with stone ghats and island pavilions;
  - stepwells;
  - rooftop rainwater tanks;
  - matkas (clay pots) at street water stands.
- **Plants:**
  - sparse desert planting: **khejri** (*Prosopis cineraria*: a thin open crown, 5–8 m), **neem**, **kikar**/acacia
    (flat-topped);
  - **bougainvillea** on rooftops;
  - **date palms** by the tank;
  - roof pots of tulsi and flowers;
  - pink and magenta oleander.
- **Cyberpunk overlay:**
  - The stone jali screens are backlit: entire facades glow through their lace, gold or cyan.
  - Chhatri domes ring-lit.
  - Rooftop restaurants with festoons and neon menu boards in Hindi.
  - The fort bastions carry searchlights and banner screens.
  - Mirror-work (sheesh) reflective panels sparkle.
- **Night:** the whole fort floodlit gold on its hill, havelis glowing through jali lace, the lake reflecting chhatri
  pavilions, rooftop lantern light.

## Kit
- **Common pieces:**
  - `wall_panel` (yellow ashlar), `jharokha` (canted, octagonal and arched presets, stacked), `screen_lattice` (stone jali, fine);
  - `chhajja`, `bracket_corbel`, `chhatri`, `parapet_screen`, `round_tower` (bastion preset), `gate_portal` (pol);
  - `pond_tank` + `ghat_steps` + pavilion (`chhatri` on a plinth in the water);
  - khejri, kikar, date palms, bougainvillea.
- **Parameters that make it Rajput:**
  - ONE colour (honey sandstone) for everything;
  - street facades 70–90% carved jharokhas, stacked and varied per storey;
  - chhatri-studded roofs;
  - the fort ring of round bastions on the island's high point;
  - a big tank with ghats.
- **Unique pieces (2):**
  - `jharokha_canted` (a three-sided stone bay with jali and a bangla or dome cap; a `jharokha` preset);
  - `bastion_round` (a battered round tower with crenellation; a `round_tower` preset).
