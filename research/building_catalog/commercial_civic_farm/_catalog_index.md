# Commercial / Civic / Farm Building Catalog — Index

Procedural-generation template catalog for the station's Midwestern-American neighborhood floor. Each row links to a template file specifying: overview (tier/footprint/stories/materials), a room/space list with size ranges, a per-space furniture/fixture pool with count ranges, and placement notes. This index covers everything in scope EXCEPT houses/apartments (see the separate `residential/` catalog).

Population tiers: **V** = rural village (500-5,000), **T** = small town (6,000-10,000), **C** = small city (30,000-50,000).

## Downtown Retail / Commercial

| Archetype | Category | Tiers | Footprint (W x D, m) | Space Count | File |
|---|---|---|---|---|---|
| General Store | Retail | V, T | 9-15 x 15-25 | 6 | `general_store.md` |
| Hardware Store | Retail | V, T, C | 9-15 x 18-30 | 6 | `hardware_store.md` |
| Diner / Cafe | Retail | V, T, C | 6-10 x 12-20 | 6 | `diner_cafe.md` |
| Small Grocery | Retail | V, T, C | 12-20 x 20-35 | 9 | `small_grocery.md` |
| Pharmacy / Drugstore | Retail | T, C | 8-13 x 15-22 | 6 | `pharmacy_drugstore.md` |
| Clothing Store | Retail | T, C | 7-12 x 15-25 | 6 | `clothing_store.md` |
| Bank Branch | Retail/Civic | V, T, C | 7-18 x 12-20 | 7 | `bank_branch.md` |
| Barber Shop / Salon | Retail | V, T, C | 4-7 x 8-14 | 3 | `barber_salon.md` |
| Bar / Tavern | Retail | V, T, C | 6-10 x 12-20 | 5 | `bar_tavern.md` |
| Movie Theater (single-screen) | Retail | T, C | 10-22 x 25-50 | 8 | `movie_theater.md` |
| Small Hotel / Inn | Retail | T, C | 12-20 x 20-30 | 9 | `hotel_inn_small.md` |
| Restaurant (sit-down) | Retail | T, C | 8-14 x 15-25 | 7 | `restaurant.md` |

## Civic / Institutional

| Archetype | Category | Tiers | Footprint (W x D, m) | Space Count | File |
|---|---|---|---|---|---|
| Post Office | Civic | V, T, C | 5-22 x 8-35 | 6 | `post_office.md` |
| Town Hall / Municipal Building | Civic | V, T, C | 8-25 x 10-40 | 7 | `town_hall.md` |
| Library | Civic | V, T, C | 8-30 x 10-40 | 7 | `library.md` |
| Small Church (multi-denominational template) | Civic | V, T, C | 10-24 x 18-45 | 9 | `church.md` |
| School (one-room rural / consolidated) | Civic | V (one-room), T, C (consolidated) | 6-9 (one-room) / 30-120 (consolidated) x 8-150 | 3 (one-room) / 9 (consolidated) | `school.md` |
| Volunteer Fire Department | Civic | V, T, C | 8-28 x 10-35 | 8 | `fire_department.md` |
| Police Station | Civic | C (T at reduced scale) | 15-25 x 20-35 | 11 | `police_station.md` |
| Courthouse | Civic | C only (1 per county seat) | 25-35 x 30-45 | 9 | `courthouse.md` |

## Industrial / Utility-Adjacent

| Archetype | Category | Tiers | Footprint (W x D, m) | Space Count | File |
|---|---|---|---|---|---|
| Grain Elevator | Industrial | V, T, C | 9-15 x 12-20 (+height) | 6 | `grain_elevator.md` |
| Gas Station | Industrial | V, T, C | 8-14 x 10-16 (+forecourt) | 5 | `gas_station.md` |
| Auto Repair Shop | Industrial | T, C | 12-20 x 15-25 | 6 | `auto_repair_shop.md` |
| Warehouse | Industrial | T, C | 15-25 x 30-60 | 6 | `warehouse.md` |
| Small Factory / Mill | Industrial | T, C | 15-45 x 25-80 | 7 | `small_factory_mill.md` |
| Water Tower | Structure (no interior) | V, T, C | 8-15 diameter (+25-45m height) | 0 (landmark only) | `water_tower.md` |

## Farm Structures

| Archetype | Category | Tiers | Footprint (W x D, m) | Space Count | File |
|---|---|---|---|---|---|
| Barn (gambrel-roof dairy/general) | Farm | V, T, C (farm zone) | 11-13 x 12-14 (+lean-tos) | 6 | `barn_dairy.md` |
| Pole Building / Machine Shed | Farm | V, T, C (farm zone) | 9-12 x 12-24 | 3 | `pole_building_machine_shed.md` |
| Grain Silo (farm-scale) | Farm/Structure | V, T, C (farm zone) | 4-9 diameter (+8-20m height) | 1 (landmark, non-walkable) | `grain_silo.md` |
| Chicken Coop | Farm | V, T, C (farm zone) | 3-6 x 4-8 | 3 | `chicken_coop.md` |
| Corn Crib | Farm | V, T, C (farm zone) | 8-9 x 8-12 (double-crib) | 3 | `corn_crib.md` |
| Farm Equipment Shed | Farm | V, T, C (farm zone) | 6-9 x 9-15 | 1 (often open-sided) | `farm_equipment_shed.md` |

## Notes / Assumptions

- **32 archetypes total** across 4 categories, exceeding the 15-20 minimum target.
- **Church** covers denominational variation (Catholic/Lutheran/Episcopal vs. Baptist/Methodist/non-denominational) as generation-time bias rules within a single template rather than separate files, since the room list is structurally the same across denominations — only proportions and a few fixtures differ.
- **School** covers both the one-room rural schoolhouse and the larger consolidated school as two labeled sub-templates within one file, since they share almost no structural overlap but are the same functional archetype at different tiers.
- **Police Station** and **Courthouse** are flagged city-tier-only (or reduced-scale-at-town-tier for police); smaller settlements should route the "law and order" function through `town_hall.md` (a clerk's office / sheriff's substation) rather than generating a full dedicated building.
- **Courthouse** should be generated at most once per station/region (per county seat), not once per settlement — it is the one archetype in this catalog that is NOT per-settlement-repeatable.
- **Water Tower** and farm-scale **Grain Silo** are non-interior "landmark structures" — included per the task brief's request to note structure types even without full interiors, and useful for skyline/wayfinding generation.
- **Pole Building/Machine Shed** vs. **Farm Equipment Shed**: intentionally overlapping archetypes representing "larger enclosed modern shed" vs. "smaller/older open-sided shelter" — the generator should pick one per farmstead based on farm-size tier rather than placing both.
- Farm structures are tagged with all three settlement tiers because farmsteads populate the farm zone surrounding every settlement size in this game's map, not because a single farmstead scales with the nearest town — farm building sizing instead scales with an independent farm-size parameter (not modeled here; assume small/mid family-farm scale throughout, consistent with the size ranges cited).
- All size ranges are grounded in real reference data (National Register nomination forms, NPS preservation briefs, agricultural extension publications, and general architectural/typological sources) cited at the bottom of each individual file; where no single authoritative dimensioned source was found (e.g. chicken coop, farm equipment shed), this is noted explicitly in that file's Sources section and figures reflect widely corroborated general practice rather than a single citation.
- Companion catalog: house/apartment archetypes are covered separately in `research/building_catalog/residential/`.
