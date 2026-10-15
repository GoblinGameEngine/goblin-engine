# persian_desert: the Persian desert city (Yazd, Kashan, Abarkuh)

## Sources and examples
- **Yazd (UNESCO 2017):**
  - Narrow streets and roofed alleys; clay, mud brick and adobe for insulation.
  - About 700 wind catchers, the oldest from the 14th century.
  - Dowlatabad's badgir is 33 m tall with an octagonal plan.
  - https://www.al-monitor.com/originals/2023/07/irans-ancient-wind-catchers-beat-heat-naturally ·
    https://surfiran.com/mag/dowlat-abad-garden
- **Badgir types:**
  - One-sided where the wind is steady; 4- or 8-sided where it varies; internal walls split the shaft into flues.
  - https://blog.ferrovial.com/en/2024/05/windcatchers/ · https://fieldstudyoftheworld.com/natural-ventilation-windcatchers-iran/ ·
    https://en.wikipedia.org/wiki/Aghazadeh_Mansion (Abarkuh: a two-storey windcatcher pavilion)
- **Yazd windcatcher reconstruction study:** https://smb.yazd.ac.ir/article_3997.html?lang=en
- **Tabatabaei House, Kashan:**
  - A sunken courtyard with pool and gardens, entered through a winding corridor to a hashti (an octagonal hall).
  - Biruni (outer), andaruni (inner) and servants' courts.
  - Cellars cooled by wind towers; about 1881.
  - https://archnet.org/sites/1483 · https://iranontour.com/?p=9848 · https://surfiran.com/tabatabaei-house-in-kashan/
- **Persian gardens:**
  - The chahar bagh: four parts, a central pool, cypress, plane (chenar), pine, elm, pomegranate, fig, vine.
  - Yazd's gardens are fed by qanats.
  - https://en.wikipedia.org/wiki/Paradise_garden · https://rashintravel.com/the-10-most-beautiful-persian-gardens-to-visit-in-iran/ ·
    https://iraniantours.com/?p=8644

## Generator grammar
- **Cell and storeys:**
  - Grid 3.3 m.
  - Storeys 3.5–4.5 m (vaulted rooms).
  - Houses 1–2 storeys above ground plus a cellar (sardab), with **sunken courtyards** 1–5 m below the lane.
  - Courts 10–25 m.
- **Walls:**
  - Mud brick and adobe, 0.6–1.0 m thick, finished in **kahgel** (mud-straw plaster), `#c9a87c`, `#bf9a6a`,
    `#d4b48a`: one uniform straw-flecked tan for the whole city.
  - Fired brick for important rooms and portals `#b98a5c`.
  - Weathering: straw texture, erosion at the base, rounded tops.
- **Mass:**
  - Introverted courtyard houses whose rooms are **vaulted and domed** (every room its own vault).
  - The roofscape is a sea of low domes and barrel vaults, punctuated by badgirs.
  - Big houses have several courts; ab anbar cisterns (a dome plus 2–6 badgirs) mark quarters.
- **Streets:**
  - Kucheh lanes 1.5–3.5 m, winding, between high blank mud walls.
  - Stretches covered by **sabats** (vaulted bridges and rooms over the lane, often every 20–50 m) and pointed arches
    buttressing the walls.
  - Portals (sar-dar) recessed with built-in benches (pirneshin) and two knockers (one per sex).
  - The bazaar: covered by brick domes in a row (a chain of domes, each with an oculus), 4–8 m wide, with
    **chaharsuq** crossings (a bigger dome at a crossroads) and **timcheh** (domed hall markets).
- **Growth:**
  - E1: qanat-fed gardens and courts.
  - E2: houses subdivided, rooms bridging lanes, more sabats, upper rooms (balakhaneh) on roofs.
  - E3: fired brick and steel-beam (jack-arch) houses, aluminium windows.
  - E4: badgirs refitted as glowing air towers, light domes, roof terraces with glass pavilions.
- **Openings:**
  - Street: blank, except portals (pointed arch with a brick muqarnas hood, wooden door with two knockers).
  - Court: the **iwan / talar** (a big pointed-arch porch, open on one side), five- and three-door rooms (orsi:
    sash windows with **coloured glass lattice**), arcades.
  - Rooftop **balakhaneh** with windows.
- **Roofs (the mark):**
  - **domes and vaults** everywhere (low brick domes 4–8 m across, plastered tan);
  - **badgirs**: square shafts 1.5–3 m across, 3–8 m above the roof (towers up to 33 m), with vertical slot
    openings on 1, 2, 4 or 8 sides and fin walls inside; their tops have small parapet caps;
  - parapets low; roofs walkable over the domes.
- **Ornament:**
  - brick patterns (hazarbaf) on portals;
  - tilework (blue and turquoise) on mosques and portals only;
  - plaster stalactites inside;
  - coloured glass in orsi windows.
- **Public spaces:**
  - the **Jameh mosque court** with its twin-minaret portal (the tall slender minarets of Yazd);
  - **Amir Chakhmaq**, a three-tiered takyeh facade (arcaded screen) on a large square: the model plaza;
  - the bazaar chaharsuqs;
  - the zurkhaneh (a domed gym);
  - gardens (bagh).
- **Water:**
  - **qanat** channels underground, surfacing in cisterns;
  - **ab anbar** (a domed cistern with badgirs and a deep stepped entrance);
  - courtyard pools (houz) in every house, reflecting the talar;
  - the garden's chahar bagh channels.
- **Plants:**
  - courtyards: a **pomegranate** pair, **fig**, grapevine, a central bed of roses and herbs, one **cypress**
    (tall flame shape 8–15 m) or **chenar** plane (massive, 20 m, in a big court or square);
  - gardens: cypress avenues, pine, elm and fruit orchards;
  - lanes: no trees;
  - roofs: none.
- **Cyberpunk overlay:**
  - badgirs become light towers (slots glowing, fans visible);
  - dome fields carry solar shells and small antennae;
  - sabats become lit skyways;
  - orsi colored glass as big emissive panels;
  - bazaar domes' oculi throw down light beams;
  - minarets carry LED rings;
  - signage restrained: tile-blue neon calligraphy in the bazaar.
- **Night:** a dark sea of domes, badgirs glowing like lanterns, jewel orsi windows in the courts, the bazaar a
  warm vaulted tunnel, the mosque portal tiles lit turquoise.

## Kit
- **Common pieces:**
  - `wall_panel` (kahgel, thick, rounded), `dome_small` (brick, low), `vault_barrel`;
  - `badgir` (plan, height, sides);
  - `arch_opening` (pointed iwan/talar), `door_studded` (two knockers);
  - `sabat_bridge`, `covered_alley`, `skylight_dome` (bazaar), `qanat_ab_anbar`, `hauz_pool`;
  - `screen_lattice` (orsi coloured glass), `minaret_small` (slender twin), `tile_panel` (portal);
  - cypress, plane, pomegranate.
- **Parameters that make it Persian:**
  - one tan kahgel colour for everything;
  - the roofscape is domes and vaults, not flat;
  - a badgir every 15–30 m;
  - sunken courtyards with a pool and a talar;
  - lanes bridged by sabats every 20–50 m;
  - tile only on sacred portals.
- **Unique pieces (2):**
  - `badgir` (windcatcher tower; plan square or octagonal, 1/2/4/8 sides);
  - `orsi_window` (sash with coloured-glass lattice; can be a `screen_lattice` preset).
