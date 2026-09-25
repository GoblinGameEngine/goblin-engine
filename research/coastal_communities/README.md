# Coastal communities -- research index and the map programme

The expanded station (tools/map_expanded.py) gets nine new coastal communities, a boardwalk and pier
at Harrow Falls, and a boardwalk at Cedar Ford.  Research per subject (layout, zoning, buildings,
amenities, flora, real examples, sources):

- [boardwalks_and_piers.md](boardwalks_and_piers.md) -- boardwalk construction and frontage; Florida
  and UK piers and their amenities; **the Harrow Falls pier programme**
- [boardwalk_towns.md](boardwalk_towns.md) -- Jersey Shore, Florida, Charleston-area and Virginia Beach
  layouts, zoning and building types
- [great_lakes_and_fishing.md](great_lakes_and_fishing.md) -- Great Lakes harbour towns; cannery /
  fishing villages (Lubec, Eastport, Astoria, Cannery Row, Gloucester)
- [beach_cities.md](beach_cities.md) -- Charleston + Nantucket (North Sea city), Dana Point +
  Huntington Beach (South Sea city)
- [flora_and_coast.md](flora_and_coast.md) -- plants by region; headland-bay coasts
- reference photos: `remake/reference/COAST-*/` (each with sources.json: licence, author, record)
  -- fetched by [fetch_refs.py](fetch_refs.py)

## Map rules (from the user, 2026-09-24)
- The Kettle River is **0.5 km wide in a wide basin** (the floodplain fills the rest of the 1 km
  widening); Lake Tamsin **expands north**; no existing building is moved or removed.
- The North and South Sea coasts are natural: **rocky headlands with cliffs and sandy bay beaches**.
- Nine new coastal communities; Harrow Falls gets a boardwalk and a pier with the researched amenities;
  Cedar Ford gets a boardwalk.

## The nine communities (working names -- the user can rename)
| Name | Where | Model | Programme |
|---|---|---|---|
| **Port Carrow** | North Sea, large city | Charleston + Nantucket | harbour of parallel wharves off a wharf street, compass-grid old town, Four Corners civic crossing, King St-style retail spine, cobbled Main St to the central wharf, Rainbow Row, City Market sheds, single houses and shingled houses, the Battery park on the point, ferry wharf, yacht club, ocean beach and pier |
| **Solana Point** | South Sea, large city | Huntington Beach + Dana Point | wide straight beach with a long pier, Pier Plaza and Main St inland from the coast highway, Pacific City mall; a rocky headland; Dana Point harbour in its lee (breakwater, two marina basins, island with bridge, boatyard, launch ramp, fishing pier, yacht clubs); bluff-top Lantern District |
| **Tern Harbor** | North Sea, fishing village | Lubec / Eastport / Gloucester | breakwater harbour, finger wharves with fish houses, cannery on pilings + warehouse + conveyor crossover + boiler stack, ice house, auction shed, net lofts, marine railway and boatyard, fuel dock, harbourmaster, Coast Guard station, village |
| **Pelican Cove** | South Sea, fishing village | Cannery Row / Astoria | a short cannery row (two canneries with crossovers to inland warehouses), wharves, the same harbour services, village |
| **Brightwater** | North Sea, boardwalk town | Jersey Shore (Ocean City, Wildwood, Seaside Heights) | beach-parallel grid, boardwalk with arcades and food, an amusement pier, doo-wop motels, convention hall, resort avenue, cottage blocks, lifeguard stands, beach patrol |
| **Haven Point** | North Sea, harbour town at Lost Creek's mouth | Great Lakes (Grand Haven, Saugatuck) | creek-mouth channel between twin piers with a lighthouse and catwalk, marina basin, riverwalk boardwalk, Coast Guard station, small downtown, bluff cottages, public beach |
| **Palmetto Beach** | South Sea, pier town | Florida (Naples, Daytona, Hollywood) | Main St ending at a fishing pier with Pier Plaza, restaurant and bait shop; a Broadwalk promenade with a bandshell; beach road hotels; bungalow blocks |
| **Oceanview** | South Sea, oceanfront resort | Virginia Beach | concrete boardwalk, a continuous oceanfront hotel wall, the resort avenue one block back, fishing pier, a stage plaza, condos and motels behind |
| **Port Tamsin** | Lake Tamsin's new north shore | Great Lakes lake town (Saugatuck, South Haven) | marina and breakwater with a pier light, public beach with dunes, small downtown, resort hotel, bluff cottages |

After the map is approved: find the real-world buildings for each (as for the inland towns), then model.
