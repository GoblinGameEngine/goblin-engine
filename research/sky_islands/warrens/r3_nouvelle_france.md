# R3: Nouvelle-France winter towns (Québec City, Montréal plexes)

**Island culture:** a cold-climate city. In the Lower Town, grey rubble-stone houses with very steep roofs (up to a third of the elevation), dormers and tin, crowded under a cliff and joined to the Upper Town by breakneck stairs and a funicular. In the plex quarters, rows of 2–3 storey brick walk-ups each wear a twisting outdoor iron staircase, the city's most iconic symbol, with balconies stacked over a front garden. The mark is the steep snow-shedding roof and the exterior spiral stair: a city that wears its stairs and roofs outside.

## Examples
- Québec City:
  - The style comes from 17th–18th-century Normandy and northern France, adapted to cold: a very tall, steep roof (likely to shed snow), up to a third of the elevation.
  - Early hipped roofs were later replaced by gables; dormers stud the slopes.
  - Rubble walls, mansard roofs, small casement windows. Place Royale: steep pitched roofs, dormers, unrendered stone.
  - Petit-Champlain was almost demolished in the 1960s and restored from the 1970s.
  - Sources: [Wikipedia: Architecture of Quebec City](https://en.wikipedia.org/wiki/Architecture_of_Quebec_City), [UVic overview](https://web.uvic.ca/~hist66/vicvic/student/st_ann_architect/architectureandculture/frenchcanadianarchitecture/frenchcanadianarchitectureoverview.html), [archiseek](https://archiseek.com/2009/place-royal-quebec-city-quebec/), [patriquin](https://www.patriquinarchitects.com/the-traveling-architect-quebec-city-canada)
- Montréal plexes:
  - Mid-19th century onward, with a boom from the 1870s.
  - Setback rules (green front space, keeping falling snow off pedestrians) pushed the stairs outside to save space and heating; also a fire escape.
  - Squeezed between the street and the front door, they became steep and twisting.
  - Voted Montréal's most iconic symbol (2012); "deathtraps" in winter.
  - Sources: [Atlas Obscura](https://atlasobscura.com/articles/montreal-plexes-outdoor-staircases), [themain](https://themain.com/articles/history-lesson-montreal-spiral-staircases), [Bloomberg](https://www.bloomberg.com/news/features/2021-08-04/looking-to-rent-in-montreal-get-to-know-the-plex), [stickymangorice](https://stickymangorice.com/2023/06/14/montreal-stairs/)

## Generator grammar
- **Cell:**
  - Québec: houses 8–10 m wide, storeys 3.0 m, 2–3 storeys plus a 1–2 storey roof (the roof height is 40–60% of the wall height).
  - Plex: frontage 7.5 m (25 ft), depth 18–20 m, storeys 3.0 m, 2–3 storeys, a front setback of 2–4 m holding the stairs and a garden.
- **Walls:**
  - Québec: grey-beige rubble stone 0.7–0.9 m `#a39d90` with dressed quoins `#c4bdae`, sometimes limewashed white `#efebe2`. Roofs in standing-seam tin: silver `#b8bcc0`, red `#a8322a`, green `#3f6a4a`, black.
  - Plex: brick `#8a3e2c` to `#b06040` or greystone `#9a968e`. Painted iron stairs and balconies: black `#1d1d1d`, green `#2a5a3a`, oxblood `#6a2a28`, and some bright (turquoise, orange). Wooden balcony floors, cornices `#d8d0c0`.
  - Weathering: winter grime, salt stains at the base, snow on every horizontal (permanent snow caps here).
- **Mass:**
  - Lower Town: terraced stone houses packed under a cliff, a narrow lane between them; the Upper Town on the cliff top with fortifications.
  - Plex quarters: continuous rows of identical-width units with shared party walls, each with 2–3 front doors (one per flat).
  - A back lane (*ruelle*) behind each row, with sheds, tangled rear balconies and wooden back stairs.
- **Streets:**
  - Narrow cobbled lanes in the Lower Town (4–6 m).
  - Breakneck stairs (long straight flights down the cliff).
  - A funicular.
  - Plex streets on a strict grid, 12–15 m with tree lines; back ruelles 4–5 m (green alleys: *ruelles vertes*, planted community spaces).
- **Growth:**
  - Layer 0: the fortification walls and the citadel.
  - Layer 1: New France stone houses with steep roofs.
  - Layer 2: British-era mansards and Second Empire.
  - Layer 3: plex rows with outdoor stairs.
  - Layer 4: back-lane additions (wooden galleries, sheds).
  - Layer 5: cyberpunk.
- **Openings:**
  - Small casement windows (0.9×1.5 m) with many panes and interior shutters; dormers in rows (2–4 per roof).
  - Plex: tall paired windows, a bay window (*oriel*) on some, front doors in pairs at each level reached by the external stair.
- **Roofs:**
  - Québec: steep gables at 50–60° in tin or wood shingle, with dormers; massive chimney stacks at the gable ends (firewall gables with corbel brackets).
  - Plex: flat roofs with an ornate pressed-metal cornice and parapet.
- **Ornament:** sparse on the stone houses (sign brackets, painted shutters); plex cornices with brackets, iron stair filigree, coloured doors.
- **Public space:**
  - The Place Royale square (a church and a small stone square).
  - The cliff-top boardwalk terrace (Dufferin style) with kiosks.
  - Parks with ponds (a skating pond in winter).
  - Green ruelles.
  - Church squares.
- **Water:** the river quay at the foot, a park pond, frozen.

## Street hierarchy
- **Cliff-top terrace promenade (main):** 15 m boardwalk.
- **Lower Town main street:** 6 m.
- **Breakneck stairs and the funicular.**
- **Plex avenues:** 12–15 m.
- **Ruelles:** 4–5 m.
- **Squares:** Place Royale, a park and pond, ruelle gardens.

## Plants
- Sugar maple (red and orange in autumn `#d8401a`; 15–20 m).
- Silver maple and elm lines on the plex streets.
- Lilacs (`#b48ad0`) and hydrangeas in the front gardens.
- Climbing ivy (Boston ivy, red in autumn).
- Birch and spruce on the cliff.
- Window-box petunias.
- Vegetable beds in the ruelles.
- Snow on every branch (permanent, cold aloft).

## Cyberpunk overlay
- Outdoor stairs heated (glowing orange treads in the snow).
- Tin roofs with solar seams.
- Funicular glass pods.
- Ruelles roofed with greenhouse glass and LED grow-lights (a magenta glow from the backs).
- Dormers as stacked capsule rooms.
- Cliff stairs with neon handrails.
- **Night:** warm windows in steep roofs, and snow reflecting everything (`#ffd8a0`). Iron stairs silhouetted against lit doors. Strings of white bulbs along the terrace boardwalk. The ruelles glow magenta.

## Kit
- **Shared pieces:**
  - `stair_spiral_external` (main), `stair_steel_external`, `balcony_iron`, `gallery_iron`, `dormer_row` (main), `dormer_bump`
  - `chimney_stack` (main: gable-end stacks), `firewall_ladder`, `cornice_bracketed` (main: plex), `bay_window_box`, `french_window`, `shutters`
  - `clapboard_panel`, `funicular`, `terrace_rail`, `lights_festoon`, `bell_tower`, `stone_slab_roof` (as tin)
- **Unique pieces:**
  - `steep_tin_roof`: a 55° standing seam with snow guards.
  - `firewall_gable_corbels`.
  - `plex_twist_stair`: an iron stair with a quarter-turn and landings.
  - `ruelle_shed_gallery`.
  - `snow_cap`: a decal or mesh on horizontals.
- **Parameters:**
  - Québec: roofs about 45% of the building height; low walls, small windows (window to wall 15%).
  - Plex: a strict 7.5 m rhythm, with an outdoor stair on every unit (alternating mirror image) and a balcony stacked per storey.
  - Colours mostly sober (grey stone, red brick) with coloured doors and stairs.
  - Snow on every top surface.
