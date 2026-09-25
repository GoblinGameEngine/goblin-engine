# Coastal catalog -- research contract (extends CATALOG_SPEC.md)

The expanded station's new structures (remake/inventory/coastal_inventory.json, from
`tools/map_expanded.py --coastal-inventory`): 831 buildings in ten new communities plus the Harrow
Falls and Cedar Ford waterfront pieces, 104 walks / decks (boardwalks, piers, wharves, docks,
breakwaters...), and 11 great bridges.  Same record format as CATALOG_SPEC.md
(`remake/catalog/<ID>.json`, photos in `remake/reference/<ID>/` via refs.py), with these rules:

## Rules (user, 2026-09-24)
1. **Every building is unique**: one real-world example per structure, never reused (claims list
   `remake/catalog/_claims_coastal.txt`, one Commons file / source id per line).
2. **1970 onward.** Pick buildings built (or wholly rebuilt) in 1970 or later; go older only when
   the kind has no newer real example (lighthouses, canneries, historic Charleston rows...), and say so
   in `brief`.
3. **Coast-matched regions** -- the example must come from the matching real coast:
   - `east` (North Sea towns): ME, NH, MA, RI, CT, NY (Long Island), NJ, DE, MD, VA, NC, SC, GA, FL (Atlantic)
   - `west` (South Sea towns): CA, OR, WA
   - `greatlakes` (Lake Tamsin, the Kettle River): MI, OH, WI, MN, IL, IN, PA (Erie), NY (Great Lakes shore)
4. **Deep foundations.** Everything is founded deeper than it needs to be so nothing ever floats:
   buildings FOUND_DEPTH x 1.5 (6 m); anything on or over water (piers, wharves, canneries on pilings,
   boardwalks, bridge piers and pile bents) carries its piles 10 m below the modelled bed.
5. Names invented, fitting the town (no real brands); every business named, every sign meaningful.
6. Full textures and interiors, as for the inland catalog (the parametric builders + shopfit).

## New kinds and their traits
**hotel** (mid/high-rise, oceanfront): `storeys` 3-20; `form`: slab | tower | stepped | L | courtyard;
`balconies`: none | continuous | per_room | corner; `walls`: stucco | concrete | brick | glass_curtain |
fiber_cement; `roof`: flat | parapet | mansard | hip_tile; `ground_floor`: lobby | lobby_restaurant |
shops; `pool`: none | deck | rooftop; `colors`; `sign`; names `{"name", "sign"}`.

**motel** (1-3 storeys, doors off exterior galleries): `storeys`; `plan`: I | L | U | court;
`gallery`: none | front | both; `roof`: flat | shed_angled | butterfly | gable; `walls`: block | stucco |
brick | frame; `signage`: neon_pylon | roof_sign | wall; `pool`: bool; `style`: doo_wop | ranch_motor_court |
contemporary; names.

**condo** (1970s+ beach condominium / townhouse block): `storeys`; `units`; `balconies`; `walls`
(house vocabulary + stucco, fiber_cement); `roof`; `parking`: under | surface | garage.

**house** gains archetypes for the coasts: `raised_beach_house` (on piles, flood code), `shingle_style`,
`nantucket_cape` (four-bay, central chimney, grey shingle, roof walk), `charleston_single` (one room wide,
side piazza), `lowcountry`, `california_bungalow`, `spanish_revival`, `contemporary_beach`
(1970s shed-roof modern), `a_frame`, `cottage_lake`.  (cottage, beachhouse, bungalow, singlehouse and
shingle in the inventory are all **house** records with these archetypes.)

**rowhouse**: house traits + `party_walls`: both | left | right; `ground_floor`: shop | residence.

**store** gains business types: surf_shop | taffy_fudge | ice_cream | souvenir | t_shirts | beachwear |
bike_rental | golf_cart_rental | kayak_rental | bait_tackle | fish_market | seafood_restaurant |
raw_bar | boardwalk_fries | pizza_slice | arcade | tattoo | art_gallery | wine_bar | brewpub | marina_store.

**arcade / stand** (boardwalk frontage): `width_m`; `open_front`: bool; `sign_style`: marquee | neon |
painted_board; `use`: arcade | food | games | souvenir; names.

**restaurant** (pier / waterfront): `storeys`; `deck`: bool; `walls`; `roof`; names.

**pavilion / kiosk / bandstand**: `form`: octagon | rectangle | round; `roof`: dome | pagoda | hip | canopy;
`open_sides`: bool; `iron_lace`: bool (UK pier style); `use`: theatre | cafe | shelter | bandstand | ticket.

**lifeguard** (stand / tower): `type`: chair | tower_hut; `material`: wood | aluminum | fiberglass; `paint`.

**lighthouse**: `type`: conical_tower | skeletal | pierhead_cylinder | fog_house; `height_m`; `paint`
(bands); `lantern`: bool; `keeper_house`: bool.  (Few post-1970 lighthouses exist -- older is allowed.)

**cannery / warehouse / fishhouse / icehouse / shed / boatyard** (industrial vocabulary): `use` adds
cannery | fish_processing | ice_plant | net_loft | boat_shed | marine_railway; `on_pilings`: bool;
`conveyor_crossover`: bool.

**monument**: `type`: column | obelisk | statue; `height_m`; `material`.

**ride** (amusement pier): `type`: ferris_wheel | coaster | carousel | drop_tower | swings | dark_ride.

**stack**: boiler chimney (`height_m`, `material`: brick | steel).

## Walks (remake/catalog/<PREFIX>-W##.json, -D## for decks)
`kind`: boardwalk | pier | wharf | dock | breakwater | promenade | catwalk | crossover | railway | bridge | ramp;
`example` (a real one, coast-matched; geotagged boardwalk photos in remake/reference/BOARDWALKS/);
traits: `deck`: timber_herringbone | timber_plank | concrete | composite; `substructure`: timber_piles |
concrete_piles | steel_screw_piles | rubble_mound; `rail`: none | timber | pipe | ornamental_iron;
`lighting`: none | lamp_posts | string; `benches`: bool; `width_m`; `pile_depth_m` (>= 10).

## Great bridges (remake/catalog/XBR-##.json, XRR-##.json)
One example each from research/coastal_communities/bridges.md (1970+): `type`: suspension |
cable_stayed | segmental_trestle | girder_trestle | twin_trestle | rail_trestle; `main_span_m`;
`towers`: {"material": "concrete|steel", "form": "portal|H|A|single_pylon"}; `approaches`:
{"type": "girder|segmental_box|pile_bent", "span_m": n}; `clearance_m`; `lanes`; `foundations`:
{"type": "caisson|drilled_shaft|pile_bent", "depth_below_bed_m": n (>= 20)}.
