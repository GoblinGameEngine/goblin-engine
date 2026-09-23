# Real Elevation / Topographic Data for Reference Settlements

Companion data file to `_station_river_loop_design_notes.md`. Pulls real elevation numbers
and elevation-profile *shapes* for a sample of the settlements already categorized into the
three topographic archetypes in `generator_rules.md` §8 (bluff-and-river-valley, dead-flat
drained plain, rolling-hill/confluence). This file is cited real-world data; the synthesis
into a station heightfield proposal is in `_station_elevation_design_notes.md`.

**Method note:** live web search was unavailable for this pass (session search budget was
already exhausted by an earlier, interrupted attempt at this task), so all data below was
pulled by direct page fetch — primarily Wikipedia city-infobox elevations and geography-section
text, cross-checked against city-data.com's independently-sourced elevation figures, plus a
few regional-geology/hydrology Wikipedia pages (Great Black Swamp, Osage Hills, Minnesota
River) for slope and valley-depth figures. Where a settlement has two different elevation
citations from two different sources (Wikipedia infobox vs. city-data.com), that's not an
error — the two sites often report the elevation of two different reference points in the
same city (e.g. a downtown/river-terrace point vs. an upland/city-hall point), and the
**difference between them is used below as a lower-bound estimate of in-town local relief**,
flagged everywhere it's used this way. No USGS topoView/DEM imagery could be rendered or
described directly in this pass (no live map-tile access); figures below are the numeric
proxies available through text sources instead.

---

## Archetype 1: Bluff-and-river-valley

### Jefferson City, Missouri
- Wikipedia infobox elevation: **630 ft (192 m)**. City-data.com elevation: **702 ft (214 m)**.
  Difference: **~72 ft (~22 m)** — a lower-bound estimate of in-town relief between a
  lower/river-adjacent reference point and a higher one.
- Wikipedia geography text: the city sits "on the northern edge of the Ozark Plateau on the
  southern side of the Missouri River," with a "bluff overlooking the nearby Missouri River,"
  on which the State Capitol sits.
- **Shape:** classic one-sided bluff — flat floodplain directly on the river (oldest,
  historically industrial/commercial), a single bluff rising behind it, Capitol sited at the
  bluff crest, upland beyond.
- Sources: [Jefferson City, Missouri – Wikipedia](https://en.wikipedia.org/wiki/Jefferson_City,_Missouri); [city-data.com](https://www.city-data.com/city/Jefferson-City-Missouri.html)

### Cape Girardeau, Missouri
- Wikipedia infobox elevation: **371 ft (113 m)**. City-data.com elevation: **354 ft (108 m)**.
- Nearby reference point: **Trail of Tears State Park**, a Mississippi River bluff-top overlook
  immediately north of the city in Cape Girardeau County, sits at **486 ft (148 m)**.
  Using the city elevation (~354-371 ft) as a river-adjacent-ground proxy and the park's
  486 ft bluff-top as a nearby-bluff proxy gives an estimated **~115-130 ft (~35-40 m)**
  of local relief in the immediate area — consistent with the tier-summary's description of
  Cape Girardeau having "real local relief near the river."
- Wikipedia geography text: the city name comes from a "rock promontory overlooking the
  Mississippi River" (later partly destroyed by railroad construction; a remnant survives at
  Cape Rock Park). The 1993 flood photo and downtown floodwall/mural imagery both point to
  downtown sitting low, directly on the floodplain, with engineering (the floodwall) keeping
  it dry rather than natural elevation.
- **Shape:** one-sided bluff, similar family to Jefferson City, but the "cape"/rock-promontory
  language suggests a more abrupt, rockier bluff face than Jefferson City's broader Capitol
  bluff.
- Sources: [Cape Girardeau, Missouri – Wikipedia](https://en.wikipedia.org/wiki/Cape_Girardeau,_Missouri); [city-data.com](https://www.city-data.com/city/Cape-Girardeau-Missouri.html); [Trail of Tears State Park – Wikipedia](https://en.wikipedia.org/wiki/Trail_of_Tears_State_Park)

### Mankato, Minnesota
- Wikipedia infobox elevation: **1,007 ft (307 m)**. City-data.com elevation: **830 ft (253 m)**.
  Difference: **~177 ft (~54 m)** — read as downtown/river-terrace (830 ft, city-data) vs.
  upland/bluff-top reference (1,007 ft, Wikipedia infobox), matching the tier-summary's
  description of newer subdivisions "on the upland terrace above the river bluff."
- Regional check: the **Minnesota River – Wikipedia** article states the valley the river
  flows in "is up to five miles (8 km) wide and 250 feet (80 m) deep" — an independent,
  larger-scale figure for the same valley, giving an upper-bound relief figure of
  **~250 ft (~76 m)** for the valley wall generally (not town-specific, but the same
  landform Mankato's downtown sits against).
- **Shape:** the most dramatic and clearly one-sided bluff of the three — tier-summary
  language ("bluff wall pins it against the water," downtown "long and narrow") plus the
  177-250 ft relief range make this the upper-bound reference case for the archetype.
- Sources: [Mankato, Minnesota – Wikipedia](https://en.wikipedia.org/wiki/Mankato,_Minnesota); [city-data.com](https://www.city-data.com/city/Mankato-Minnesota.html); [Minnesota River – Wikipedia](https://en.wikipedia.org/wiki/Minnesota_River)

**Archetype 1 summary:** real bluff-river local relief clusters roughly **70-180 ft (21-55 m)**
town-specific, with the wider regional valley-wall figure (Minnesota River, 250 ft/76 m)
as a plausible upper ceiling. Shape is consistently: flat low ground directly on the river →
one dominant bluff → flat upland beyond.

---

## Archetype 2: Dead-flat drained plain

### Bowling Green, Ohio
- Wikipedia infobox elevation: **689 ft (210 m)**.
- Regional slope figure (from the **Great Black Swamp** Wikipedia article, which covers the
  region including Bowling Green and Findlay): historic accounts describe streams as
  "sluggish... their bed having little inclination," with an average regional slope of
  **~4 ft per mile (~0.076%)** — essentially flat by any gameplay-relevant standard. Terrain
  consists of glacial till plains with minor "knob and kettle" micro-relief and scattered dry
  moraine ridges (a few feet to a few tens of feet of local relief at most, not town-scale
  bluffs).
- **Shape:** dead flat, sub-0.1% regional grade; no bluff feature at all.
- Sources: [Bowling Green, Ohio – Wikipedia](https://en.wikipedia.org/wiki/Bowling_Green,_Ohio); [Great Black Swamp – Wikipedia](https://en.wikipedia.org/wiki/Great_Black_Swamp)

### Findlay, Ohio
- Wikipedia infobox elevation: **781 ft (238 m)**.
- Blanchard River flood record: the 2007 flood crested at **18.46 ft** (river gauge stage, not
  ground elevation) and caused ~$100M damage — a useful indirect confirmation of just how
  flat/floodplain-dominated the surrounding ground is: an 18+ ft rise in river stage was able
  to spread across a huge area of the town rather than being contained in a narrow, deep-cut
  channel, which is exactly what "no relief to contain the water" looks like.
- **Shape:** same dead-flat, ex-Great-Black-Swamp family as Bowling Green; Blanchard River
  floodplain sits essentially at town grade.
- Sources: [Findlay, Ohio – Wikipedia](https://en.wikipedia.org/wiki/Findlay,_Ohio)

### Kearney, Nebraska (bonus comparator, open Platte plain rather than ex-swamp)
- Wikipedia infobox elevation: **2,152 ft (656 m)**, sited historically "a mile north of the
  Platte River." No natural-relief language in the geography section at all — the article's
  only terrain-relevant content is interstate/market-access framing, itself a proxy for "flat
  enough that road access, not topography, defines the town's development story."
- **Shape:** dead-flat, open high-plains river terrace — same functional archetype as
  Bowling Green/Findlay despite being climatically/regionally distinct (glacial till plain vs.
  high plains alluvium), confirming "dead-flat drained plain" is a landform-shape category, not
  a single-region phenomenon.
- Sources: [Kearney, Nebraska – Wikipedia](https://en.wikipedia.org/wiki/Kearney,_Nebraska)

**Archetype 2 summary:** real local relief is negligible — effectively 0-15 ft of
non-engineered relief at town scale, with the only cited hard slope number (Great Black
Swamp, ~4 ft/mile ≈ 0.076%) confirming "flat" is not an exaggeration here. Any drainage relief
present is artificial (ditches, tile), matching generator_rules.md §8's existing note that
this archetype relies on an artificial/engineered drainage network rather than natural
incised creeks.

---

## Archetype 3: Rolling hill country / confluence

### Bartlesville, Oklahoma
- Wikipedia infobox elevation: **702 ft (214 m)**.
- **Osage Hills** regional article (the hill region Bartlesville sits at the eastern edge of):
  highest elevations in the region reach **~1,300 ft (400 m)**; Tulsa, near the region's
  eastern/southern edge, sits at **636 ft (194 m)** — a regional relief spread of roughly
  **664 ft** across the *whole* Osage Hills region (this is a broad-region figure, not a
  single-town figure — flagged as such). The article characterizes the terrain as "broad
  rolling hills" with only shallow soil over limestone/shale/chert outcrops, explicitly
  *not* dramatic/steep relief — the shallow soil and rolling character (rather than height)
  is what kept the land in native tallgrass prairie instead of row-crop cultivation.
- **In-town estimate:** given the "broad rolling hills" characterization (not "bluffs" or
  "cliffs"), local relief within Bartlesville itself is almost certainly a small fraction of
  the 664 ft regional spread — treat that regional number as a ceiling, not a town figure.
  No town-specific relief number was recoverable in this pass; this is flagged as an estimate
  gap, best resolved later with a direct topoView/DEM check if more precision is needed.
- **Shape:** rolling, multi-directional, no single dominant bluff face — contrasts directly
  with Archetype 1's one-sided-bluff shape.
- Sources: [Bartlesville, Oklahoma – Wikipedia](https://en.wikipedia.org/wiki/Bartlesville,_Oklahoma); [Osage Hills – Wikipedia](https://en.wikipedia.org/wiki/Osage_Hills)

### Salina, Kansas
- Wikipedia infobox elevation: **1,227 ft (374 m)**, with a secondary citation in the same
  article of **1,224 ft (373 m)**.
- Specific local relief feature: **Indian Rock Park** is cited as "the tallest point in the
  area" (a hill within the Wellington Formation). Separately, in the late 1950s flood-control
  excavation created **"80-foot steep shale bluffs"** along the riverbank — this is the single
  most concrete real bluff-height number found in this research pass, though it's an
  *engineered/excavated* bluff rather than a natural one (flagged accordingly — still a useful
  scale reference even if the origin story differs from Archetype 1's natural bluffs).
- Regional character: Salina sits in the Smoky Hills sub-region, described in the tier-summary
  research as a "subtle mountainous or hilly plateau" — gentler than the Osage Hills but
  clearly not flat like Archetype 2.
- **Shape:** rolling upland with at least one sharp, localized engineered bluff feature (80 ft)
  near the river — a hybrid of "broad rolling" background relief plus one concentrated bluff
  accent, useful as a middle case between the pure-rolling Bartlesville pattern and the
  pure-bluff Archetype 1 pattern.
- Sources: [Salina, Kansas – Wikipedia](https://en.wikipedia.org/wiki/Salina,_Kansas)

### Danville, Illinois
- Wikipedia infobox elevation: **637 ft (194 m)**.
- Geography: sits at the confluence of the Salt Fork, Middle Fork, and North Fork of the
  Vermilion River (part of the Wabash River Valley); borders the 1,000-acre Lake Vermilion
  reservoir on its northwest side.
- **No specific bluff-height or relief number was recoverable from the Wikipedia article** in
  this pass — this settlement's topographic detail in this dataset remains qualitative only
  (the tier-summary's existing note that "the multi-fork river confluence and its associated
  bluffs/ravines created [park-worthy rough terrain]" is the best available source, already
  captured in generator_rules.md §8). Flagged as a data gap rather than filled with an invented
  number.
- **Shape:** confluence-driven, multiple ravines cutting otherwise-flat farmland from three
  converging fork valleys, rather than one single dominant bluff line — structurally different
  from both Archetype 1 (one bluff) and Bartlesville/Salina (broad regional rolling).
- Sources: [Danville, Illinois – Wikipedia](https://en.wikipedia.org/wiki/Danville,_Illinois)

**Archetype 3 summary:** real relief is present but diffuse/rolling rather than concentrated
in one dominant bluff face, *except* where a river has cut a specific local feature (Salina's
80 ft engineered bluff, Danville's confluence ravines) — in which case a concentrated local
relief feature of roughly the same 70-180 ft scale as Archetype 1 can still appear, just
embedded in a broader rolling-hill or multi-valley context rather than standing alone against
flat ground on all sides.

---

## Elevation profile shapes (for Part 2 synthesis)

Four distinct real shapes emerge from the above, each needing a different periodic-function
treatment in the station design proposal:

1. **One-sided bluff** (Jefferson City, Cape Girardeau, Mankato): flat low terrace at the
   river → one rise (bluff) → flat upland. Asymmetric across the valley — only one side has
   the bluff, matching the cut-bank/point-bar asymmetry of the river itself.
2. **Dead flat** (Bowling Green, Findlay, Kearney): no rise at all, <0.1% regional grade.
3. **Broad rolling, no dominant bluff** (Bartlesville): multi-directional, moderate, spread
   over a wide area rather than concentrated.
4. **Rolling background + one concentrated local bluff/ravine accent** (Salina, Danville):
   hybrid — mostly gentle relief, with one sharper feature (excavated bluff, confluence ravine)
   at a specific location tied to a river/creek feature.

Shape 1 is the one directly relevant to the station's town-siting cross-check (river cut-bank
= high, firm Downtown ground; point-bar = low floodplain/park) and is therefore the primary
target of the closed-loop proposal in `_station_elevation_design_notes.md`. Shapes 3-4 inform
why the proposal adds a broad, low-amplitude "rolling" term on top of the main bluff term
rather than leaving Residential/Farm perfectly flat everywhere.
