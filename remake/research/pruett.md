# Pruett: building and bridge research (vertical slice #1)

Pruett is a village of 820 in Brannock County. It was founded on the railroad and sits on
US 30 beside the C&NW main line. It is the first settlement to be rebuilt from scratch: every
structure below is modelled from a real building and nothing from the old asset set is reused.

Reference files live in `remake/reference/<FOLDER>/`. Each folder has a `sources.json` that
records the source, record URL, license and author of every file. HABS/HAER material from the
Library of Congress is public domain. Wikimedia Commons files keep the license listed per file.
Measured drawings are stored as ~4000 px PNGs converted from the LOC TIFF masters, which is
large enough to read dimensions from.

Map IDs refer to `remake/inventory/map_inventory.json`. The map's rough 11 m boxes are replaced
by the real footprints below, and the layout is adjusted to fit the buildings rather than the
other way round.

---

## 1. Real-world examples chosen

| Folder | Map ID | Pruett role and name | Real example | Record | Refs |
|---|---|---|---|---|---|
| P-ELEV | P-008 | **Pruett Farmers Co-operative Elevator**: grain elevator, the tallest structure in the village (village research §9) | Penfield Elevators, East Elevator, Front St, Penfield, Champaign Co., IL (village of about 400). Crib-built 1919, corrugated-metal sheathing, cupola headhouse, wagon-scale shed added c.1930 | HAER IL-? `il0569` (+ site plan `il0476`) | 9 measured drawing sheets: site plan, basement/1st/loft/headhouse plans, 4 elevations, 2 sections |
| P-DEPOT | P-009 | **Pruett Depot Museum**: former C&NW passenger depot, now the village museum | Rock Island RR Seneca Passenger Depot, Seneca, IL. Wood frame, 1911-12, 50'×17', hipped roof, asbestos-shingle siding | HAER IL-44 `il0609` | 2 HAER photos + 1 Commons photo + report. Alternate kept for a town: Marseilles depot (`_pool/`) |
| P-CHURCH | P-002 | **St. Olaf Evangelical Lutheran Church** (Norwegian immigrant congregation) | First Evangelical (Norwegian) Lutheran Church, Sheldahl, IA. One-room white frame church, belfry, pot-bellied stove, raised pulpit with railed chancel | HABS IA-62 `ia0043` | 4 photos (incl. 3 interior), 1 colour Commons photo, 3 drawing sheets (plan, 4 elevations, pulpit/rail details) |
| P-TAVERN | P-001 (half) | **Deer Creek Tavern**: bar and fish-fry supper room, rooms upstairs | Hassler Tavern, U.S. Route 6, DePue, Bureau Co., IL. Two-storey brick stagecoach tavern (c.1840s), Greek Revival door surround, one-storey frame wing | HABS IL-14 `il0262` | 3 photos, 3 sheets (1st/2nd floor plans, section, 3 elevations, fireplace details) |
| P-STORE | P-001 (half) | **Pruett Mercantile**: groceries, hardware, feed, with the owner's flat upstairs | Thompson Store, 109 W Grant Hwy, Marengo, IL. Two-storey frame store c.1845 with multi-pane shop windows either side of the entrance, 1½-storey rear wing | HABS IL-143 `il0169` | 3 photos, 3 sheets (plans, 4 elevations, shop-front and entrance details at full size) |
| P-PO | P-003 | **U.S. Post Office, Pruett** | Harvel, IL post office (primary): 1960s one-storey brick box with gabled entry, flag pole, blue collection box. Elliott, IL post office (secondary: same era, gable front, stone-faced) | Commons (CC BY-SA 4.0 / CC BY 2.5) | 3 photos + Harvel skyline for village context. **Gap: no plan exists**, so the interior follows `building_catalog/post_office.md` |
| P-HOUSE1 | P-004 | House, Haugen family | Horace Paine House, Grand Detour, IL. 1½-storey Greek Revival frame house with a lower wing, shuttered 6/6 windows, sidelight entrance | HABS IL-175 `il0076` | 9 photos (incl. 4 interior), 3 sheets (both floor plans, front elevation, mouldings) |
| P-HOUSE2 | P-005 | House, Lindqvist family | "Representative Bungalow", 1506 Thompson Ave, Des Moines, IA (c.1920). Clapboard over a brick foundation, twin front gables, open porch, detached garage | HABS IA-91 `ia0063` | 1 photo + architectural data form. **Gap: 1 photo only**, so the plan follows the data form plus `residential/bungalow_craftsman.md` |
| P-HOUSE3 | P-006 | House, Brandt family | John H. Donahue House, 98 Southern Ave, Dubuque, IA. American foursquare 22'×24', 2 storeys, hipped roof and dormer, full front porch on panelled piers, rear enclosed porch, **20'×20' hip-roof garage with cupola** | HABS IA-159-A `ia0227` | 5 photos + data form with dimensions |
| P-HOUSE4 | P-007 | House, Kowalski family | 2019 Woodland Ave (cottage), Des Moines, IA. 1½-storey side-gabled cottage with cross gable, rear shed addition, **chain-link yard fence** | HABS IA-194 `ia0415` | 6 photos + long report |
| P-BR-US30 | SMALL-45 | US 30 over Deer Creek | Hill Creek Bridge, State Route 100, Pearl, IL. Riveted steel Warren pony truss on concrete abutments, W-beam guardrail approaches | HAER IL-118 `il0713` | 10 photos (incl. underside, bearings, gusset details) |
| P-BR-RAIL | RAIL-03 | C&NW over Deer Creek | Norfolk & Western Stony Creek Arch (N-647.74), Pride, OH. Stone-masonry railway arch culvert extended in concrete, with the railway's own plan and section drawings | HAER `oh2030` | 16 photos + 3 original railway drawings (extracted from the report PDF) |
| P-CULVERT-L2194 | CULVERT-22 | US 30 over a farm ditch | MN Bridge L2194, 200th Ave, Magnolia, MN. Single-cell reinforced-concrete box culvert by local builder P. N. Gillham: solid railings with moulded coping, cylindrical end posts, builder's inscription | HAER `mn0632` | Report only. **Gap: no photos.** Concrete detailing is taken from P-CULVERT-5722 (MN Bridge 5722, US 63, 1932 state-standard box culvert: 2 photos + report) |

Extra material collected for later settlements, kept in `_pool/`: the Marseilles and Utica depots
and the Smith Farmhouse at La Moille (with measured drawings), intended for a farmstead.

---

## 2. Site furniture, fences and signs, per structure

Every sign's text relates to its building. Names are fictional; nothing reuses a real business name.

- **Co-op elevator (P-ELEV)**
  - Painted headhouse sign, modelled on the "GIFFORD ELEVATOR CO." sign in the Penfield west-elevation drawing: **PRUETT FARMERS CO-OP · GRAIN · SEED · FEED**.
  - Wagon scale shed with a **SCALE: ALL TRUCKS STOP** sign.
  - Scale house / office with a door sign **OFFICE · CO-OP MEMBERS WELCOME**.
  - Truck scale deck, grain pit grate, loading spout, manlift/ladder, and a lightning rod on the cupola.
  - Chain-link yard gate with **NO TRESPASSING: PRUETT FARMERS CO-OP**.
- **Depot museum (P-DEPOT)**
  - Station name board on each gable end: **PRUETT**.
  - Museum sign on posts: **PRUETT DEPOT MUSEUM · C&NW 1912 · Open Sat–Sun 1–4**.
  - Brick platform, baggage cart, train-order signal mast.
  - Railroad crossbucks and a **RAILROAD CROSSING** sign where Main St crosses the tracks.
- **St. Olaf church (P-CHURCH)**
  - Belfry with bell.
  - Notice board: **ST. OLAF EV. LUTHERAN CHURCH · Est. 1874 · Worship Sunday 9:30 · All Welcome**.
  - Cornerstone **1874**, woven-wire fence along the lot line, iron hitching post.
- **Deer Creek Tavern (P-TAVERN)**
  - Projecting board sign: **DEER CREEK TAVERN · EST. 1851**.
  - Window signs: **FISH FRY FRIDAY**, **COLD BEER**, **OPEN**, using fictional brands only.
  - Split-rail fence at the side lot, bench on the porch.
- **Pruett Mercantile (P-STORE)**
  - Cornice sign: **PRUETT MERCANTILE**.
  - Window lettering: **GROCERIES · HARDWARE · FEED & SEED**, plus a hours card on the door.
  - Porch bench, galvanised feed-sack stack, and a hitching rail.
- **Post office (P-PO)**
  - Wall letters **U.S. POST OFFICE / PRUETT** (styled on Harvel's).
  - Flag pole with flag, blue collection box, and **NO PARKING: MAIL VEHICLES ONLY**.
- **Houses**
  - Mailboxes lettered **HAUGEN**, **LINDQVIST**, **BRANDT** and **KOWALSKI**, plus house numbers.
  - Fences:
    - P-HOUSE4: chain-link, as in its photos.
    - P-HOUSE1: white picket.
    - P-HOUSE3: garage with cupola, as in its photos.
    - P-HOUSE2: detached garage, as in its photo.
  - Clothesline at one house. Village-tier lot research gives clotheslines about 35–45% odds, so one of four fits.
- **Village**
  - Entrance signs on US 30 each way: **PRUETT · Pop. 820 · Home of the Pruett Co-op**.
  - Street name signs (Main St, Depot St, Elevator St), US 30 route shields, and a **Deer Creek** creek sign at the bridge.
- **Bridges**
  - US 30 truss: builder's plate **BRANNOCK COUNTY · 1931 · DEER CREEK** and a **WEIGHT LIMIT 15 TONS** sign.
  - Rail arch: date stone **C&NW 1893** and milepost plate **MP 214**.
  - Culvert: inscription on the railing, **E. OSTLIE BUILDER 1913**, echoing L2194's builder inscription.

---

## 3. What has to be modelled: the full checklist

This is the checklist every structure goes through, for Pruett and later settlements. Items
marked (lib) are built once as reusable code: the *code* is shared, but each building's
geometry, dimensions and materials come from its own real example.

**A. Reference to spec**
1. Read the floor plans for room names and sizes, wall thickness, and the position and swing of each door and window.
2. Read the elevations for storey heights, sill and head heights, roof pitch and overhangs, porch and column sizes, chimney positions, and sign positions.
3. Read sections and details for stair runs and rises, floor build-up, cornice and mouldings, and door and window casings.
4. Take materials and colour from the photos. HABS photos are black and white, so colour comes from colour photos where they exist, otherwise from period-typical colours for the material.
5. Adapt what has to change: modern uses (the depot museum, the tavern's bar), plus accessibility and game-scale adjustments.
6. Write the spec file `remake/specs/<id>.json`. It must record where every number came from.

**B. Shell**
1. Foundation: rubble stone, brick or concrete, plus the basement where the plan shows one.
2. Exterior walls with real thickness, with openings cut for every door and window. (lib)
3. Wall finish: clapboard, brick, corrugated metal, asbestos shingle or stucco, with corner boards and skirt.
4. Floors and ceilings per storey. Ceiling heights come from the section drawings.
5. Roof by type (gable, hip, pyramidal, shed, gambrel), with the real pitch, overhangs, fascia, soffit, gutters and downspouts, and ridge caps. (lib)
6. Chimneys, stove pipes, dormers, cupola or belfry, and the elevator headhouse.
7. Porches: deck, steps, columns or piers, railing and roof.

**C. Openings**
1. Windows: frame, sash split (6/6, 2/2 or 1/1), muntins, glass with a transparent material, sill, casing, and shutters where the photos show them. (lib)
2. Exterior doors: frame, panel pattern taken from the photo or detail, hardware, threshold, and storm/screen door where shown.
3. Interior doors: frame, casing, and a panel door matching the building's era.
4. Every door is its own node with its pivot on the hinge line, so Godot can swing it. Each gets:
   - a named trigger;
   - a collision body that moves with the door;
   - a swing direction taken from the plan;
   - locked or unlocked state (for example the co-op grain pit door is locked);
   - double doors where the plan shows them (church front, tavern front, elevator driveway).

**D. Interior**
1. Partition walls taken from the floor plan.
2. Stairs with real rise and run, stringers, handrail and balusters, and a stair hole cut in the floor above.
3. Floor finish (plank, linoleum, tile, concrete), wall finish (plaster, wainscot, beadboard), baseboards and ceilings.
4. Fixed fixtures: kitchen cabinets, sink, tub, toilet, radiators or stove, fireplace (the tavern's two mantels are drawn in the HABS details), bar counter, store counters and shelving, post-office service counter, PO box wall and lobby, church pews, pulpit and chancel rail (all in the drawings), and elevator bins, leg, boot pit and manlift.
5. Furniture per room from `building_catalog` furniture pools, sized from the photos where interior photos exist.
6. Lighting: fixture meshes plus Godot light positions, marked with named empties.

**E. Site**
1. Lot grading, walks, driveways (materials follow the lot-contents research), and parking.
2. Outbuildings from the real example's photos and drawings: garages, the elevator's scale shed and office, the depot platform, and a privy where period-appropriate.
3. Fences and gates, with gates that open and use the same door system.
4. Signs: the board or sign mesh, lettering rendered to texture, and mounting posts and brackets.
5. Utility and street furniture: mailbox, meter, utility pole drop, flag pole, collection box, crossbucks, street signs.

**F. Materials and textures (clean sheet)**
1. New textures are generated by script (Python/numpy, touched up in GIMP), one set per material and building: clapboard, brick bond, corrugated metal, asbestos shingle, cedar and asphalt shingle, standing seam, stone, concrete, plaster, wood floor, linoleum, and sign boards.
2. Each material gets albedo, normal and roughness maps, with weathering varied per building. That covers the co-op's rust streaks, the church's fresh paint and the tavern's soot.
3. Nothing is copied from the old `godot_project/assets`.

**G. Bridges**
1. Abutments and wingwalls, deck, bearings, the truss or arch or box itself, and railings or guardrail.
2. The creek channel under the bridge and the approach grading.
3. Name and date plates, and signs.

**H. Export, integration and verification**
1. Each structure exports as one `.glb` from Blender with a node naming scheme:
   - `*-col` for static collision;
   - `door_*` for hinged doors;
   - `light_*` for lights;
   - `sign_*` for signs.
2. A Godot loader wires up doors (interact to open or close, animated swing, moving collision) and lights.
3. Checks before a structure counts as done:
   - walk in through every exterior door;
   - open every interior door;
   - use every staircase;
   - no gaps or z-fighting;
   - the collision matches the visible mesh;
   - a performance check.
