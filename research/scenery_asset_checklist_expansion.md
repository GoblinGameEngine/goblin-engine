SCENERY / ASSET CHECKLIST — EXPANSION PASS
Supplements `research/scenery_asset_checklist.txt` (146 exterior/infrastructure items) and
`research/interior_props_master_list.md` (265 interior items) with everything found missing
during a completeness audit conducted before Phase 2 (3D model production) begins. Per explicit
instruction, this pass errs heavily toward inclusion — a marginal item is kept and flagged lower
priority rather than omitted. Does NOT rewrite either existing file; this is additive only.

Style matches the existing checklist: `[NEW] Item name (why/zone)`.

================================================================================
RUNNING TOTAL (TOP)
================================================================================
Part A — Already-flagged-but-unresolved gaps (7 sub-sections): 23 items
Part B — Brainstormed new categories (7 sub-sections): 71 items
**TOTAL NEW ITEMS IN THIS EXPANSION: 94**
(Combined with the existing 146 exterior + 265 interior = 411, the station's total procedural
asset count becomes 411 + 94 = **505**.)

================================================================================
PART A — ALREADY-FLAGGED, NEVER-RESOLVED GAPS
================================================================================
Every item below was explicitly named as a gap somewhere in the research tree (grep-confirmed
via "gap," "not yet," "flagged," "no dedicated/matching") but never made it into either building
catalog or the scenery checklist. Citations point to the exact source passage.

--- A1. Hospital / clinic (civic-institutional building archetype) ---
Flagged in `questing_engine/story_patterns/_nonfiction_index.md` ("Documented building-catalog
gaps") and `questing_engine/story_patterns/nonfiction_stable_ag_manufacturing.md` §6: Health Care
& Social Assistance is a top-2 employment sector in 4 of 6 demographic archetypes, yet no
hospital/clinic exists anywhere in the catalog. Also blocks a quest-location alias per
`questing_engine/quest_engine_rules.md` §9.
[NEW] Rural hospital / critical-access hospital building (civic archetype, town/city tier —
      matches the rural-hospital-closure story pattern and the Health Care employment anchor;
      the small-town/village-scale counterpart is the standalone medical/dental clinic listed
      under Part B §1 below, kept separate rather than duplicated here since it's a distinct
      building scale)

--- A2. Harbor/industrial-waterfront and marina/ferry-dock infrastructure ---
Flagged in `questing_engine/story_patterns/_nonfiction_index.md` (needed for Rust Belt §6
Superfund waterfront, and Lake Resort §4/§8) and `demographics/_great_lakes_expansion_notes.md`
items 3, 10, 11, 13 (South Haven's 64-slip marina + pierhead lighthouse, Sandusky's Battery Park
Marina, Ashtabula's twin-core harbor split by a lift bridge, Ashtabula's remediated
coal-transshipment harbor).
[NEW] Industrial harbor/freight dock structure (crane/conveyor loading structure — Declining
      Rust-Belt archetype, Ashtabula-pattern working or remediated harbor)
[NEW] Marina building / harbormaster office (small footprint, Lake-Resort archetype downtown-
      adjacent — South Haven/Sandusky pattern)
[NEW] Fuel dock (marina infrastructure, pairs with harbormaster building)
[NEW] Boat slip / dock pier system (modular floating-dock sections, Lake-Resort marina)
[NEW] Chandlery-type marine-supply retail storefront (small commercial archetype — Lake-Resort
      downtown-adjacent, explicitly named alongside the marina cluster in the source finding)
[NEW] Pierhead lighthouse (small, non-walkable landmark — South Haven "Big Red"-style, Lake zone)
[NEW] Lift/drawbridge (mechanism variant of the bridge set — Ashtabula's twin-core harbor-mouth
      pattern, item 11; a literal ship-passage traffic chokepoint, distinct from the static
      river-channel bridges already in section 3 of the main checklist)

--- A3. Rail depot and founder's-mansion (+ the rail corridor they imply) ---
Flagged in `scenery_asset_checklist.txt`'s own NOTES section, sourced from
`population_tiers/villages_500_5000/_tier_summary.md`.
[NEW] Rail depot (historic small-town train station, often adaptively reused as museum/trail
      HQ — village/town tier, at most one per settlement)
[NEW] Founder's-mansion-style large house (oversized, deliberately unique flavor building, one
      per settlement max — distinct from the repeatable Victorian/Queen Anne template)
[NEW] Rail corridor track segment (straight/curved, at-grade — the rail depot and the
      rail-corridor-parallel commercial street segment already in the main checklist's section 4
      both imply a through rail line exists, not just the grain-elevator siding spur already
      listed)
[NEW] Railroad grade-crossing signal (standard US crossbuck + flashing light + gate arm — needed
      anywhere a road crosses the rail corridor from the item above)

--- A4. Hand-cranked pedestrian chain ferry ---
Flagged in `demographics/_great_lakes_expansion_notes.md` item 4 (Saugatuck's chain ferry across
the Kalamazoo River to Mount Baldhead/Oval Beach) — "not present anywhere in the original
36-settlement sample... worth a distinctive small building/mechanism type for resort-village
variants."
[NEW] Hand-cranked chain ferry mechanism/platform (small pedestrian ferry, Lake-Resort
      micro/village-tier variant — low-tech water crossing distinct from any bridge type)
[NEW] Ferry landing dock (small, one per bank — companion prop to the mechanism above)

--- A5. Cemetery ---
Flagged conditionally in `lot_contents/expanded_trees_and_fences.md` (perimeter fence, "if a
cemetery is ever added to the civic building catalog") and directly in
`questing_engine/story_patterns/fiction_smalltown_literary_tradition.md` line 160 ("A town
cemetery (not yet a catalogued building type, but implied by church.md as an attached
institution)") and echoed in `_fiction_index.md` pattern 5 (Our Town's cemetery framing device).
[NEW] Cemetery grounds (civic-institutional archetype, church-adjacent per the source finding —
      village/town/city tier; specific headstone/mausoleum/gate props are listed under Part B §6
      below rather than duplicated here)

--- A6. Fairground / exhibition hall ---
Flagged independently in two files, not named in the task brief but a genuine, twice-repeated
gap: `questing_engine/story_patterns/_fiction_index.md` pattern 14 ("no dedicated fairground
building yet catalogued — gap noted") and `questing_engine/story_patterns/
fiction_regional_folklore.md` ("No dedicated fairground building yet exists in the catalog...
worthwhile future catalog addition").
[NEW] Fairground exhibition hall / 4-H building (Stable Ag/Manufacturing archetype primary,
      county-fair pattern)
[NEW] Fairground livestock judging barn (open-sided, companion to the exhibition hall)
[NEW] Fairground grandstand (bleacher seating — racing/rodeo/demolition-derby events per the
      county-fair research)
[NEW] Fairground midway ride prop (Ferris wheel or carousel silhouette — seasonal/temporary
      set-dressing, low placement frequency)
[NEW] Fair judging tent / pavilion (temporary structure, pie/livestock judging per the folklore
      research's "judged-competition rivalry" beat)

--- A7. Downtown building-condition variant props (vacant/derelict vs. modernized-adaptive-reuse) ---
Flagged as a "next phase" concept in `generator_rules.md` §15 and §20, and grounded in
`demographics/_great_lakes_expansion_notes.md` item 1 (Elyria's genuinely vacant/boarded
storefronts vs. Manitowoc's "modernized storefront below, preserved historic facade above"
pattern). Not a new building archetype — a condition-state prop/decal set applied to the
existing downtown storefront models, same category as the existing plastic-slipcover
material-variant entry in the interior props list.
[NEW] Plywood-boarded storefront window/door panel (vacant-derelict condition prop, Rust-Belt-
      archetype-biased)
[NEW] "For Lease" / "Closed" storefront signage decal (companion to the boarding above)
[NEW] Modernized-storefront ground-floor signage/awning set (adaptive-reuse condition variant,
      pairs with the existing "preserved historic facade above" pattern)

================================================================================
PART B — BRAINSTORMED CATEGORIES (genuinely absent from the current catalogs)
================================================================================

--- B1. Additional small-town business/civic archetypes (11) ---
Checked against the nonfiction story-pattern research and general well-established small-town/
Midwest business convention; all 11 are genuinely well-precedented small-town fixtures, not
invented. Live web search hit this session's query budget partway through grounding this
section, so several entries below rely on general well-established convention (explicitly
permitted by the task brief) rather than a fresh citation — the ones with an in-tree citation are
noted as such.
[NEW] Dollar store / bare-bones discount store (village/small-town — the explicit "last business
      standing" survival-retail case documented in
      `interior_contents_why/commercial_civic_farm_economic_condition.md`; also independently
      the single most common rural-retail chain format in the real US)
[NEW] Feed store / farm supply store (farm-town — distinct from general_store/hardware_store:
      sells livestock feed, seed, fencing/fence-post supplies, farm chemicals; a genuinely
      farm-town-specific fixture, not a hardware-store reskin)
[NEW] Veterinary clinic (farm-town/small-town — large-and-small-animal combined rural practice;
      ties directly to the Health Care employment-sector finding and to the existing
      barn_dairy/chicken_coop farm-animal implications)
[NEW] Newspaper office (small weekly/biweekly paper storefront — directly grounded in the
      "news desert" finding, `questing_engine/story_patterns/nonfiction_stable_county_seat.md`
      §7, which cites Medill School of Journalism's State of Local News research)
[NEW] Local radio station (small AM/FM station building + antenna tower — same local-media
      research thread as the newspaper office above; a well-precedented small-town institution)
[NEW] Funeral home (near-universal small-town fixture, historically often a converted large
      house — pairs naturally with the Victorian/Queen Anne or Colonial Revival archetypes as an
      adaptive-reuse building)
[NEW] Law office (small storefront or converted house — near-universal Main Street fixture,
      especially clustered near the courthouse in the Stable County-Seat archetype)
[NEW] Insurance agency (small storefront office — near-universal Main Street fixture across all
      archetypes)
[NEW] Real estate office (small storefront office — near-universal fixture, especially
      prominent signage-wise in the Growing Exurban archetype's housing-boom pattern)
[NEW] Laundromat (near-universal small-town/small-city fixture — biased toward apartment/
      rowhouse-dense blocks and lower-income tiers)
[NEW] Medical/dental clinic (small stand-alone primary-care or dental office, village/small-town
      scale — distinct from the full hospital added in Part A1; the more common, smaller-footprint
      Health Care building most settlements would actually have)

--- B2. Vehicles (13) ---
Existing set: car, minivan, pickup, police_car (exterior checklist) + patrol car, fire truck/
pumper, non-running/derelict car, boat/camper/ATV trailer, vehicle-in-repair (interior props
list) — patrol car and fire truck/pumper are NOT duplicated below since they already exist.
[NEW] School bus (standard yellow — near-universal small-town/rural fixture, school archetype)
[NEW] Delivery van / box truck (small commercial delivery vehicle — general_store/small_grocery/
      post_office/warehouse delivery)
[NEW] Ambulance (EMS vehicle — pairs with the new hospital/clinic archetypes in Part A1/B1 and
      with fire_department, which commonly co-houses EMS in small-town Midwest fire departments)
[NEW] Tow truck (auto_repair_shop / gas_station companion vehicle)
[NEW] Motorcycle (general residential/rural vehicle variety)
[NEW] Bicycle (near-universal, all zones — pairs with the bike rack added in B3)
[NEW] Semi-truck / tractor-trailer (grain_elevator, warehouse, small_factory_mill logistics —
      the vehicle scale those buildings' loading-dock/truck-scale fixtures already imply)
[NEW] Combine harvester (farm-zone, large-farm implement — distinct from the smaller "combine/
      large implement" already listed as an interior-farm-equipment prop; a standalone
      exterior-scale vehicle for field scenes)
[NEW] Grain truck (farm-zone, hauls to grain_elevator — pairs with the existing truck scale
      fixture already in the interior props list)
[NEW] Snowmobile (genuine Great Lakes winter-recreation vehicle — same climate-identity thread
      as the existing snow-fence and snowblower items)
[NEW] ATV (standalone farm/rural utility vehicle, distinct from the existing ATV-trailer combo
      item which only covers the trailer)
[NEW] Boat / pontoon boat (standalone, Lake zone — distinct from the existing boat/camper/ATV
      trailer item, which is the trailer only, not the boat itself)
[NEW] Municipal snowplow / dump truck (Great Lakes winter-climate municipal vehicle — same
      climate-identity thread as snow fence/snowblower/salt storage; also a general public-works
      utility vehicle)

--- B3. Street/park furniture and public infrastructure (15) ---
Genuinely absent category — the existing street-furniture section has lamp posts, fire hydrants,
and a few Main-Street-specific items, but no generic municipal street furniture at all.
[NEW] Park/street bench (public, municipal-scale — distinct from the existing residential porch
      rocking chair/swing)
[NEW] Public trash can (municipal downtown/park-scale — distinct from the existing residential
      trash/recycling bin)
[NEW] Bike rack (downtown/park/school — pairs with the new bicycle vehicle in B2)
[NEW] Newspaper vending box (street-corner — ties to the newspaper-office addition and the
      news-desert research finding)
[NEW] Parking meter (Main Street — companion to the existing angled-parking curb/striping detail
      already in the checklist, which covers the pavement marking but not the meter itself)
[NEW] Utility/power pole with overhead lines (near-universal small-town street infrastructure,
      not currently modeled anywhere in the catalog)
[NEW] Pad-mounted transformer box (utility infrastructure, residential/downtown)
[NEW] Manhole cover (ground decal/prop — ties to the existing hydrology/drainage research thread
      even though not explicitly named there)
[NEW] Storm drain grate (ground decal/prop — same drainage-infrastructure logic as above)
[NEW] Traffic light (signal head — downtown 4-way intersection)
[NEW] Stop sign (near-universal — T-intersections, residential/farm grid)
[NEW] Street name sign (blade sign, intersection-mounted)
[NEW] Crosswalk marking (ground decal — downtown/school-zone streets)
[NEW] Rural route / speed-limit sign (farm-road and highway-adjacent)
[NEW] Yield sign (minor intersections, cul-de-sac feeders)

--- B4. Park/recreation equipment (10) ---
The existing yard-props list has residential-scale playground/swing-set items; this is the
distinct park-scale/public equipment the existing entries explicitly are NOT (per the task
brief's framing).
[NEW] Playground slide (park-scale, public — distinct from the residential swing set/playset)
[NEW] Jungle gym / climbing structure (park-scale, public)
[NEW] Swing set (park-scale, public — larger multi-bay version distinct from the residential
      single-unit swing set already in the yard-props list)
[NEW] Baseball diamond backstop + bleachers (park/school-adjacent — near-universal small-town
      fixture)
[NEW] Basketball court (outdoor, full court + hoops — distinct from the existing driveway-
      mounted residential basketball hoop)
[NEW] Gazebo / bandstand (genuine common small-town park/town-square fixture — pairs with the
      courthouse-square and campus-green civic-anchor patterns already documented in the
      research)
[NEW] War memorial / veteran monument (near-universal small-town civic-square fixture)
[NEW] Park/civic flagpole (general park, school, and war-memorial-adjacent flagpole — distinct
      from the existing courthouse-square-specific civic monument/flagpole combo piece, since
      most flagpole placements aren't at the courthouse square)
[NEW] Picnic shelter / pavilion (park fixture)
[NEW] Park drinking fountain (park fixture)

--- B5. Animals/wildlife (10) ---
Completely absent from the current checklist despite barns/coops/farms and a Lake zone
implying livestock and wildlife throughout.
[NEW] Cow (dairy/beef cattle — barn_dairy tie-in, the building's namesake function currently has
      no matching animal model)
[NEW] Chicken (chicken_coop tie-in — the coop building exists but not the animal itself)
[NEW] Pig (farm zone — general livestock variety)
[NEW] Horse (farm zone — the existing interior props list already implies horses via "saddle
      stand — barn tack room, if horses present"; this is the actual animal model that
      implication was missing)
[NEW] Dog (residential/farm — the existing yard-props list already has a doghouse/dog run/kennel
      with no dog model to put in it)
[NEW] Cat (residential — common small-town pet, low-cost ambient prop)
[NEW] Bird flock (generic songbird/pigeon, ambient — downtown/park/farm scatter prop)
[NEW] Deer (wildlife, farm-edge/woodlot — ties directly to the deer fencing already flagged in
      `expanded_trees_and_fences.md`'s orchard/vineyard-perimeter entry)
[NEW] Squirrel (residential/park ambient wildlife — near-universal Midwest yard/park animal)
[NEW] Canada goose (Lake zone/park — a strongly Great-Lakes-regionally-iconic bird, same
      regional-identity logic already used to justify the snow fence and dead-ash-stump items)

--- B6. Cemetery-specific props (7) ---
Companion props for the cemetery civic archetype added in Part A5 and the perimeter fence
already flagged (conditionally) in `expanded_trees_and_fences.md`.
[NEW] Headstone, upright slab style (common era, all periods)
[NEW] Headstone, obelisk/monument style (Victorian-era wealthy-family-plot variant)
[NEW] Headstone, flat/flush-to-ground style (modern/postwar-era cemetery-section variant)
[NEW] Mausoleum, small family-scale (upper-income/historic variant)
[NEW] Cemetery gate/entrance arch (pairs with the low iron/masonry perimeter fence already
      flagged as conditional in the fence research)
[NEW] Cemetery access lane (gravel interior path/road, grounds-scale)
[NEW] Cemetery memorial bench

--- B7. Downtown-scale seasonal decoration (5) ---
The existing yard-props list explicitly covers residential-scale seasonal decor only ("Lawn
ornament / seasonal decoration set... skew seasonal rather than permanent"); this is the
distinct Main-Street/civic-square scale it excludes.
[NEW] String lights spanning Main Street (pole-to-pole festive lighting, downtown-scale)
[NEW] Banner pole + seasonal banner (lamp-post-mounted, downtown-scale — distinct from any
      residential decor)
[NEW] Town Christmas tree (large, civic-square/courthouse-square scale)
[NEW] Wreath (lamp-post-mounted, downtown-scale)
[NEW] Holiday parade bunting/storefront decoration set (Main Street-scale, ties to the
      county-fair/parade civic-event research thread)

================================================================================
CONSIDERED, NOT INCLUDED
================================================================================
Items searched for or discussed while drafting this pass but not confidently grounded to this
specific research tree/region, so deliberately left out rather than forced in:
- Amish horse-drawn buggy/wagon — genuinely common in parts of the broader Great Lakes region
  (e.g. Holmes County, OH) but none of the 46 researched settlements in `population_tiers/` or
  `demographics/community_profiles/` are documented Amish-settlement towns; would need its own
  research pass to ground properly rather than being assumed.
- Permanent amusement-park/theme-park structures (e.g. a Cedar Point-style coaster) — Sandusky's
  Cedar Point is real and cited in the Great Lakes expansion notes, but it's a singular,
  enormous, real-named landmark, not a repeatable procedural-generation asset category; out of
  scope for a generic asset checklist.
- Airport / small municipal airfield — no mention anywhere in the research tree; no grounding
  found to justify adding it in this pass.
- Dedicated county-jail building — county-jail conditions reporting is cited
  (`nonfiction_stable_county_seat.md` §3, Marshall Project), but the functional fixtures (holding
  cell bench/bunk, barred cell door) already exist in the interior props list under
  courthouse/police_station; a full separate jail building would duplicate rather than fill a
  gap.
- Big-box retail (Walmart-scale store) — explicitly excluded by the residential catalog's own
  "no true high-rise" density cap logic and the small-city (50,000 max) population ceiling;
  consistent with the existing catalog's restraint here, not added.

================================================================================
RUNNING TOTAL (BOTTOM)
================================================================================
Part A (already-flagged gaps): A1=1, A2=7, A3=4, A4=2, A5=1, A6=5, A7=3 → **23 items**
Part B (brainstormed categories): B1=11, B2=13, B3=15, B4=10, B5=10, B6=7, B7=5 → **71 items**
**TOTAL NEW ITEMS IN THIS EXPANSION: 94**
Combined project total (146 existing exterior + 265 existing interior + 94 this pass): **505**
Largest-growing category in this pass: **B3 (street/park furniture and public infrastructure),
15 items** — the single largest completely-unaddressed category found, since the existing
checklist had essentially no generic municipal street furniture (traffic control, utilities,
public seating/trash) despite extensive road/intersection/bridge coverage.
