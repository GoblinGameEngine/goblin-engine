# Tier Summary: Small Cities, Population 30,000-50,000

Synthesis of numeric patterns from 12 real American cities researched for this tier, for
use as procedural-generator parameters. See individual city files for citations and
per-city detail.

**Cities researched:** Mankato MN (44,488), Jefferson City MO (43,228), Cape Girardeau MO
(39,540), Kearney NE (33,790), Salina KS (46,731), Hutchinson KS (~40,977), Fond du Lac WI
(43,021), Michigan City IN (31,479), Manitowoc WI (~31,895), Findlay OH (40,313), Bowling
Green OH (30,808), Danville IL (29,204, slightly under floor but included for the
multi-fork-river confluence pattern), plus Bartlesville OK (37,290, non-Midwest, included
for architectural/topographic variety) — 13 total city write-ups against a nominal target
of 12; treat Danville as a bonus/edge example. Supplementary generic planning-literature
figures are in `generic_planning_standards.md`.

## Assumptions and caveats (read before using these numbers)
- Not every city's zoning ordinance was fully extractable via web search (several PDFs
  were image/compressed and unreadable by the fetch tool). Where a city-specific number is
  missing, that city's file says so explicitly and falls back to the tier-wide range here.
- Numbers below are drawn from a mix of (a) actual current zoning-ordinance figures for
  several of the 12 cities, (b) general Midwestern small-city planning literature, and
  (c) direct observation of historic-district descriptions (block counts, building
  materials). Treat every range as a **generator parameter range to sample from**, not a
  precise average — real cities in this tier vary by roughly 2x on most dimensions.
- Where only one or two cities yielded a hard number for a category, that is noted; treat
  those figures as directional rather than a confirmed universal norm.

## Downtown / commercial core

| Parameter | Range | Why |
|---|---|---|
| Downtown block size | **~250-330 ft per side** (with a 300 ft "standard" reference point commonly cited) | 19th-century township-and-range-influenced platting converged on a small number of standard block sizes nationwide; towns in this tier are old enough (usually platted 1850s-1880s) to follow the common pattern rather than a modern superblock. |
| Downtown building setback from sidewalk | **0 ft (build-to-sidewalk)** for historic storefronts | Pedestrian retail needs direct sidewalk frontage for foot traffic and window shopping; zero setback is universal in every historic downtown examined (Mankato, Jefferson City, Cape Girardeau, Manitowoc, Findlay, Bartlesville). |
| Downtown building height | **2-4 stories** typical, with rare 1 outlier "prestige" tower (e.g. Bartlesville's 19-story Price Tower) | Small-city downtown economics support only low-rise construction; a single dominant local employer/corporation can occasionally fund one dramatically taller tower as a civic/corporate statement — a good rare-event generator rule (roughly 1-in-12 downtowns in this tier has a genuine high-rise outlier). |
| Building-to-building spacing downtown | **0 ft (party-wall/zero-lot-line)** | Confirmed directly in Mankato's North Front Street district and implied by every other historic downtown described as "brick commercial buildings" in a contiguous row. |
| Downtown/CBD as distinct zoning tier | Confirmed as its own zoning district (B-3/CB/Central Business) separate from general commercial (B-2) in Findlay, Bowling Green, and implied elsewhere | Historic core needs different bulk/setback/parking rules than auto-oriented arterial commercial; nearly universal two-tier commercial zoning (core vs. strip) across the tier. |
| Downtown street width (post-traffic-calming reconstructions) | Being **narrowed** in recent (2010s-2020s) projects (Mankato's Riverfront Drive) | Downtown streets were historically over-built for cars during mid-20th-century "urban renewal" and are now being narrowed for pedestrian comfort — model older/legacy downtown streets as wider than truly necessary, narrowing over time in "revitalized" variants. |

## Residential zoning

| Parameter | Range | Why |
|---|---|---|
| Front yard setback | **20-30 ft** (Bartlesville and Michigan City 20 ft; Salina 25-30 ft; Fond du Lac 30 ft; Jefferson City reducing 25→20 ft) | Standard mid-20th-century suburban-influenced zoning norm across nearly every city checked; remarkably consistent regardless of region. |
| Side yard setback | **6-15 ft**, with **7-7.5 ft** as the most common single value (Michigan City 7 ft, Salina 7.5 ft; Jefferson City proposing 10→6 ft; Cape Girardeau 15-20 ft as an outlier on the high end) | Enough gap for maintenance access and fire separation without wasting buildable lot width; Cape Girardeau's higher figure shows real city-to-city variation exists. |
| Minimum lot area (standard single-family) | **6,000-8,000 sq ft** (Salina confirmed 6,000 sq ft) | Produces the classic ~50-65 ft x 120-140 ft Midwest residential lot once setbacks are applied. |
| Older/pre-war platted lot width | **40-50 ft** (Michigan City confirmed for older grid neighborhoods) — narrower than what later citywide zoning assumes, producing routine variance requests / non-conformity near downtown | Pre-automobile-era platting favored narrow, deep lots to maximize street frontage per block; later 20th-century zoning updates raised minimums without retrofitting older neighborhoods — model near-downtown residential rings with narrower lots (and correspondingly more frequent small setback violations/variances) than outer postwar subdivisions. |
| Street pattern (near downtown / pre-1940) | **Grid**, sidewalks, alley access common | Confirmed in Mankato's Lincoln Park district and implied by "historic district" residential zones in every city checked. |
| Street pattern (postwar/outer subdivisions) | **Curvilinear / cul-de-sac** | Confirmed directly for Mankato's post-1960s bluff-top growth; standard nationwide postwar pattern, expected but not separately confirmed for the other 11 cities. |
| Local residential street width (curb-to-curb) | **22-40 ft**, with **28 ft** as the most frequently cited practical minimum (20 ft for two-way traffic + 8 ft for one-side parking) | Balances two-way vehicle movement, on-street parking, and emergency-vehicle access; narrower (22-26 ft) increasingly favored by traffic-calming-oriented codes, wider (32-40 ft) still common in older/more conservative codes. |
| Local street right-of-way (property line to property line) | **50-65 ft** | Standard allowance for street width plus sidewalks/utility verge/tree lawn on both sides. |

## Street/road hierarchy (generic, cross-checked against literature)

| Class | Right-of-way | Travel lane width | Building type clustering |
|---|---|---|---|
| Local street | 50-65 ft | n/a (residential, low volume) | Single-family houses, small multifamily |
| Collector | ~66 ft (up to 80 ft near an arterial junction) | 11 ft/lane | Duplexes/small multifamily, churches, elementary schools, small neighborhood commercial |
| Arterial | 60-100+ ft (up to 200 ft for a principal arterial) | 12 ft/lane | Big-box retail, strip malls, drive-throughs, auto dealerships, hotels — businesses needing high visibility/traffic access and large parcels (2+ acres), explicitly zoned this way since the 1920s-30s to separate them from both downtown pedestrian retail and residential neighborhoods |
| Downtown core | Often narrower than arterials despite higher building density | n/a | Pedestrian storefront retail, civic buildings (courthouse, post office, capitol), offices, restaurants/hospitality — land value/prestige clustering plus foot-traffic dependence keeps these off arterials and in the walkable core |

**Why the arterial/core split holds:** arterial-sited businesses (big-box, strip retail)
need vehicle visibility and large single-story footprints with abundant parking, which the
tight, expensive, pedestrian-scaled downtown core cannot supply; core-sited businesses
(storefront retail, civic buildings, offices) depend on foot traffic, land-value prestige,
and proximity to government/other businesses, which arterial strip parcels cannot supply.
The zoning code itself enforces this split explicitly in the ordinances reviewed (separate
CBD/B-3 vs. highway-commercial/B-2 districts).

## Parking

| Parameter | Range | Why |
|---|---|---|
| Retail parking ratio | **3-5 spaces per 1,000 sq ft** of floor area (up to 5-10/1,000 sq ft for "investment grade" standalone commercial) | ITE-derived industry standard; scales roughly with expected peak-hour customer volume per square foot of retail. |
| Parking lot placement, downtown | **Rear or side lots**, small, shared/consolidated between buildings | Downtown parcels are too narrow and valuable for private front lots; front-of-building parking would break the zero-setback storefront pattern universal in every downtown examined. |
| Parking lot placement, arterial/big-box | **Front lot**, large, single-tenant | Visibility from the arterial road is itself a marketing/access requirement; front lots also simplify large-footprint big-box site planning versus rear lots. |
| Parking lot size relative to building footprint (big-box/arterial) | Commonly **1x-2x the building footprint** or more, per the 3-5 space/1,000 sq ft ratio applied at typical space+aisle allotments of ~300-350 sq ft per space | Matches observed real-world big-box site plans; consistent with literature ratios above. |

## River/lake, property value, and commercial intensity correlation

**Core pattern (near-universal across this tier):** industrial/transport use of the
waterfront historically preceded, and in nearly every case examined has since been
partially or fully superseded by, park/promenade/residential-amenity redevelopment of the
same frontage, once the industrial/shipping rationale declined.

- **River-bend/river-bluff downtowns** (Mankato, Jefferson City, Cape Girardeau) show the
  clearest version: downtown is physically pinned against the water by a bluff, producing
  an elongated rather than square downtown grid, with the historic core built directly on
  the (often engineered/flood-controlled) riverfront.
- **Lake-mouth/river-confluence downtowns** (Fond du Lac at the foot of Lake Winnebago,
  Manitowoc at the Manitowoc River's mouth on Lake Michigan) show a two-part water edge:
  an inland river/harbor segment (historically industrial, now the site of new
  condos/riverwalk redevelopment) plus an open lake shoreline treated as a separate,
  usually lower-intensity amenity zone.
- **Plains-river towns without bluffs** (Kearney on the Platte, Salina near the Smoky
  Hill/Saline confluence) show the weakest river-downtown linkage: the river bounds the
  edge of the built-up area rather than constraining or defining the downtown core
  directly, because flat terrain gave the original platters room to build the grid
  wherever they liked, not just along the bank.
- **Quantified property-value effect** (general US data, not small-city-specific but
  indicative): riverfront park investment correlates with roughly **2x the property
  appreciation rate** of the surrounding city overall (Pittsburgh case: +60% near
  riverfront parks vs. +32% citywide over a 14-year window), and a **~20:1 private-to-
  public investment leverage ratio** once a credible riverfront amenity project is
  underway.
- **Generator rule of thumb:** if a river/lake touches the map, (1) prefer siting downtown
  directly against it if any bluff/high-ground constraint exists nearby, elongating the
  downtown grid along the water; (2) place a legacy "industrial/warehouse" zone directly
  on the oldest riverfront blocks; (3) allow a fraction of that industrial zone to have
  been "converted" to park/promenade/condo use in a more developed or revitalized variant
  of the map, with property values (and building height/density) increasing near that
  converted stretch specifically, not uniformly along the whole waterfront.

## Topography / drainage patterns observed

Three recurring topographic archetypes emerged across the 12-13 cities, useful as
selectable generator "presets" for this tier:

1. **Bluff-and-river-valley** (Jefferson City, Cape Girardeau, Mankato): flat/lowest land
   directly along the river (oldest, most flood-exposed, historically industrial/
   commercial), rising bluff immediately behind carrying the most prestigious civic
   buildings and, further back, postwar residential subdivisions on the flood-free
   terrace/upland.
2. **Dead-flat drained plain** (Bowling Green OH in the Great Black Swamp, Findlay OH to a
   lesser degree, Kearney NE on the open Platte plain): minimal natural relief; drainage
   handled by an artificial or heavily-modified ditch/tributary network rather than
   naturally-incised creeks; no natural constraint on the shape of the downtown grid, so
   it tends toward a regular square rather than an elongated river-hugging shape.
3. **Rolling hill country at a river/creek confluence** (Bartlesville OK in the Osage
   Hills; Salina KS in the Smoky Hills; Danville IL at the multi-fork Vermilion
   confluence): genuine local relief, often with parkland/preserved natural land
   clustering specifically around the rougher terrain near the confluence or hills
   (ravines, bluffs unsuitable for row-crop farming), while the surrounding farm country
   remains flat and fully cultivated right up to the town edge.

**Drainage/floodplain-as-park pattern:** every river town examined that has an oxbow,
relict channel, or floodplain segment near downtown treats that low-lying land as
park/greenway rather than buildable lots (explicit for Salina's abandoned Smoky Hill
channel, implied by floodplain zoning language in Cape Girardeau and Findlay). **Generator
rule:** mark floodplain/relict-channel polygons near any river as park/undevelopable by
default, not as ordinary buildable residential or commercial land.

## Distinctive building types/architecture for this tier
- **Storefront commercial (downtown):** 2-3 story brick Italianate, Late Victorian, or
  Classical Revival commercial blocks, built 1870s-1920s, zero lot line, zero setback,
  large ground-floor display windows, more modest upper-floor fenestration. (Cape
  Girardeau, Mankato's North Front St., Manitowoc's Eighth Street, Bartlesville.)
- **Civic anchor buildings:** county courthouse or, for capital cities, a state capitol,
  sited on the highest local ground near downtown (Jefferson City's Capitol on its bluff);
  federal post office/courthouse buildings also common downtown anchors in county seats
  (Danville's 1911 Post Office and Court House).
- **Rare corporate/prestige high-rise outlier:** a single modern tower funded by one
  dominant local employer, wildly taller than the surrounding downtown fabric —
  Bartlesville's 19-story Frank Lloyd Wright-designed Price Tower (1956) is the clearest
  example in this dataset; treat as a low-probability special-case building for company
  towns.
- **Pre-WWII single-family residential (near downtown):** narrow-lot (40-50 ft) wood-frame
  or brick houses on a tight grid with alleys, contributing to large historic residential
  districts (Mankato's Lincoln Park district, 177 contributing properties — unusually
  large for this city size).
- **Flood-control infrastructure as public art/amenity:** Cape Girardeau's downtown
  floodwall doubles as an 18,000 sq ft, 24-panel public mural — a distinctive way this
  tier repurposes utilitarian infrastructure as civic identity/tourism asset.
