# Residential Building Catalog — Index

Procedural-generation reference catalog for residential (house + apartment) archetypes in the station's Midwestern-American-style neighborhood zones. Each archetype file is a reusable **template** — room list with size ranges, per-room furniture/fixture pools with count ranges, and placement rules — meant to be combined with runtime randomization to generate individual house/apartment instances on the fly, not to describe one specific pre-authored building.

Population tiers referenced below:
- **Rural** = rural village, pop. 500-5,000
- **Small town** = pop. 6,000-10,000
- **Small city** = pop. 30,000-50,000

## Single-family / small multi-family archetypes (14)

| Archetype | Typical era | Typical tier(s) | Footprint (m) | Stories | Room count range | File |
|---|---|---|---|---|---|---|
| American Foursquare | 1895-1935 | Small town, small city | 9-11 x 9-11 | 2.5 | 7-10 rooms, 3-4 BR | `foursquare.md` |
| Gable-Front Vernacular Farmhouse | 1870-1930 | Rural | 7.6-10 x 6.1-7.6 (+ell) | 2 (+1-story ell) | 6-9 rooms, 2-4 BR | `farmhouse_vernacular.md` |
| Shotgun House | 1880s-1920s | Small city (dense/industrial) | 3.7-4.3 x 12-18 | 1 (camelback: 1+2) | 3-5 rooms, 1-3 BR | `shotgun.md` |
| Bungalow / Craftsman | 1905-1935 | Small town, small city | 8.5-10.7 x 9.1-12.2 | 1-1.5 | 5-7 rooms, 2-3 BR | `bungalow_craftsman.md` |
| Ranch House | 1945-1975 | Small town, small city | 12.2-18.3 x 9.1-12.2 | 1 | 6-9 rooms, 2-4 BR | `ranch.md` |
| Split-Level / Split-Foyer | 1955-1980 | Small town, small city | 11-15.2 x 9.1-11 | 3-4 half-levels | 7-10 rooms, 3-4 BR | `split_level.md` |
| Cape Cod | 1930-1955 | Small town, small city | 7.6-10.7 x 7.6-9.1 | 1-1.5 | 5-7 rooms, 2-4 BR | `cape_cod.md` |
| Victorian / Queen Anne | 1875-1910 | Small city (historic core) | 11-15 x 11-15 | 2-3 | 9-14 rooms, 3-6 BR | `victorian_queen_anne.md` |
| Mobile / Manufactured Home | 1960-present | Rural | 4.3-9.8 x 17-24 | 1 | 4-9 rooms, 2-4 BR | `mobile_home.md` |
| Small Starter Home (Minimal Traditional) | 1935-1955 | Small town, small city | 7.3-9.1 x 7.6-9.8 | 1 | 4-6 rooms, 2-3 BR | `starter_home_minimal_traditional.md` |
| Colonial Revival | 1900-1950s | Small town, small city | 9.8-13.7 x 9.1-11 | 2-2.5 | 8-11 rooms, 3-4 BR | `colonial_revival.md` |
| Tudor Revival Cottage | 1910-1940 | Small city | 9.1-11.6 x 8.5-10.4 | 1.5-2 | 6-8 rooms, 2-3 BR | `tudor_revival_cottage.md` |
| Duplex (Two-Family House) | 1900-present | Small city | Stacked: 9.1-11 x 9.1-11; Side-by-side: 12.2-15.2 x 8.5-10.4 | 1-2 per unit | 4-6 rooms/unit, 1-3 BR/unit | `duplex.md` |
| Rowhouse / Townhouse | 1890-1920 & 1980-present | Small city only | 5.5-6.7 x 12.2-15.2 per unit | 2-3 | 6-8 rooms/unit, 2-3 BR/unit | `rowhouse_townhouse.md` |

## Apartment / multi-family archetypes (3)

| Archetype | Typical era | Typical tier(s) | Footprint (m) | Stories | Unit count | File |
|---|---|---|---|---|---|---|
| Small Apartment Building (Walk-Up) | 1900-1930 & 1960-1990 | Small city (also small-town edge) | 15.2-24.4 x 10.7-15.2 | 2-3, no elevator | 6-16 units | `apartment_small.md` |
| Garden-Style Apartment Complex | 1960-2000 | Small city | Multi-building complex, each 18.3-30.5 x 10.7-13.7 | 2-3 per building, no elevator | 6-12 units/building, multiple buildings | `apartment_garden_style.md` |
| Larger City Apartment Block (Mid-Rise) | 1910-1930 & 1990-present | Small city only (rare/landmark) | 30.5-45.7 x 18.3-24.4 | 4-6, elevator | 24-60+ units | `apartment_large.md` |

## Notes and assumptions

- All archetypes are written as **templates**: a room list with min-max size ranges and typical room-count ranges, plus a per-room content **pool** with plausible item counts (e.g. "1-2 nightstands") rather than a fixed furniture list, so the generator can sample varied but plausible instances.
- Room dimensions are given as width x depth in meters (feet noted in-line in each file's Overview section where sourced directly from feet-based real estate/historic data); these are walkable interior clear dimensions, not including wall thickness.
- Era ranges reflect original construction; per the brief's "mix of eras is fine and realistic" note, small towns and rural villages should skew toward older archetypes (farmhouse, foursquare, bungalow, Cape Cod, starter home, mobile home) while small cities have the full spread including postwar and modern types (ranch, split-level, Tudor/Colonial Revival, duplex, rowhouse, all three apartment types).
- Duplex and rowhouse/townhouse are included among the "house-scale" archetypes (per-unit room templates similar in scale to a starter home or Cape Cod) rather than under "apartment," since each unit is a small independent house-style floor plan rather than a corridor-served apartment unit.
- The three apartment archetypes escalate in scale and rarity: small walk-up (common, small city + small-town edge) -> garden-style complex (common, small city, site-plan-heavy) -> mid-rise block (rare, 1-3 per settlement max, small city only, the sole elevator-served type in the catalog).
- No true high-rise/tower apartment archetype is included — capped by the small-city (50,000 max) population ceiling and by the station's Midwestern-neighborhood setting; the mid-rise (`apartment_large.md`) is treated as the ceiling of residential density.
- Gaps/candidates for future expansion if more variety is later wanted: Prairie School / Frank-Lloyd-Wright-influenced houses (regionally apt, noted as a stylistic variant under `bungalow_craftsman.md`), accessory dwelling units (ADUs)/granny flats, group/boarding houses, and senior/assisted-living residential buildings — none were in scope for this pass.
- All room-size and furnishing data is grounded in the sources cited at the bottom of each individual file (Wikipedia architectural-style articles, National Register nominations, real-estate floor-plan sites, and general interior-design room-size guides); a few closely related archetypes (Colonial Revival, Tudor Revival, Rowhouse/Townhouse) extrapolate from the same source set used for their nearest researched cousin (Foursquare/Victorian/Duplex respectively) since dedicated period floor-plan sources were sparser for those specific styles.
