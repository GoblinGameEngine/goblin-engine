# Structure catalog — research contract

Every structure on the map (remake/inventory/map_inventory.json: 547 lots, 34 farmsteads x 4
buildings, 82 crossings) gets **its own real-world example** (never reused), photographs of that
example, and a structured description the parametric builders turn into a model. Pruett (P-*) is
done by hand and is the quality bar: see remake/research/pruett.md and remake/reference/P-*.

## Output per structure (one worker owns an ID; never edit another worker's IDs)

    remake/reference/<ID>/            photos (+ measured drawings when HABS has them), sources.json
                                      (written by remake/tools/refs.py loc-fetch / commons-fetch)
    remake/catalog/<ID>.json          the record below

Farm buildings use IDs `FARM-01-house`, `FARM-01-barn`, `FARM-01-silo`, `FARM-01-shed`.
Crossings use their inventory ID (`MAJOR-01`, `SMALL-12`, `CULVERT-03`, `RAIL-02`).

```json
{
  "id": "HF-012",
  "settlement": "Harrow Falls",
  "kind": "house",
  "lot": {"w": 12.0, "d": 10.0},
  "example": {
    "title": "Smith House, 412 Oak Street",
    "place": "Galesburg, Knox County, IL",
    "year": 1892,
    "source": "HABS IL-1234",            // or "Wikimedia Commons"
    "url": "https://www.loc.gov/item/il0999/",
    "photos": ["photo_1.jpg", "photo_2.jpg", "photo_3.jpg"],   // files in remake/reference/<ID>/
    "drawings": ["sheet_1.png"]          // [] if none
  },
  "brief": "2-3 sentences: massing, roof, materials, porch, notable features, what's around it.",
  "traits": { ... kind-specific, see below ... },
  "names": { ... kind-specific ... }
}
```

## Rules

1. **One example per structure, never reused.** Keep your own claims list in
   `remake/catalog/_claims_<worker>.txt` (one source id per line) and check it before claiming.
   Each worker draws examples from its assigned states only (below) so workers can't collide.
2. **Photos:** at least 3 of the example when the source has them (HABS/HAER items usually do);
   measured drawings too when present (TIFF masters -> PNG via refs.py). Commons is the fallback.
3. **Fit the setting.** Match the settlement's tier, founding and archetype (inventory
   `settlements`), era, and the lot size (a house lot is ~10-13 m wide; the model must fit it).
   Declining rust-belt towns get some worn/shabby traits; growing exurban gets newer houses.
4. **Names are invented** and fit the town (no real companies or brands). Every business gets a
   name; signs must say something about that business.
5. **Traits must use the vocabularies below** — the builders only understand these words. If an
   example has a feature outside them, describe it in `brief` and pick the nearest trait.
6. Commit in batches with only your own files; `git pull --rebase` before pushing.

## Worker assignments (example source states / IDs)

| worker | structures | example states |
|---|---|---|
| laptop session (Goblin Engine lockup) | Harrow Falls (HF-*), Kessler (K-*), Marlowe (M-*) | IL, IN, OH |
| deck helper A | Bellhaven (B-*), Fenwick (F-*) | IA, MO |
| deck helper B | Tamarack (T-*), Cedar Ford, Dunmore Crossing, Loomis Grove, Haskins Corner | WI, MN, MI |
| deck helper C | farmsteads FARM-* (all four buildings each) | NE, KS, ND, SD, plus any state for barns/silos not in the list above |
| deck helper D | crossings (all except Pruett's SMALL-45, RAIL-03, CULVERT-22) | any state (HAER) |

## Traits vocabularies

**house** (also `FARM-*-house`)
- `archetype`: i_house | gable_front | upright_and_wing | foursquare | bungalow | workers_cottage |
  queen_anne | italianate | cape_cod | ranch | minimal_traditional | side_gable_cottage | shotgun |
  dutch_colonial | tudor_revival | split_level | american_small_house | prairie_box
- `storeys`: 1 | 1.5 | 2 | 2.5;  `main_w_ft`, `main_d_ft` (footprint of the main block, fit the lot)
- `wing`: null | {"side": "left|right|rear", "w_ft": n, "d_ft": n, "storeys": n}
- `roof`: {"type": "gable|hip|gambrel|cross_gable|pyramid|shed|flat", "pitch_deg": n, "material": "asphalt_shingle|wood_shingle|slate|metal|tile"}
- `dormers`: [] | [{"type": "gable|shed|hip|eyebrow", "side": "front|rear|left|right"}]
- `porch`: {"type": "none|stoop|front_full|front_partial|wrap|enclosed|side|recessed", "posts": "turned|square|tapered_on_piers|iron|columns", "rail": "none|spindle|solid|lattice"}
- `walls`: clapboard | drop_siding | wood_shingle | brick | stone | stucco | half_timber | asbestos_shingle | aluminum | vinyl | board_and_batten | log
- `foundation`: fieldstone | brick | concrete_block | poured_concrete | cut_stone
- `colors`: {"body": "#rrggbb", "trim": "#rrggbb", "accent": "#rrggbb", "roof": "#rrggbb"}
- `windows`: {"type": "1over1|2over2|6over6|4over1|3over1_craftsman|casement|picture|sliding", "shutters": bool}
- `chimneys`: [ "center|left_end|right_end|rear|exterior_left|exterior_right" ]
- `garage`: none | detached_1 | detached_2 | attached_1 | attached_2 | carport
- `yard`: {"fence": "none|picket|chainlink|iron|split_rail|hedge|privacy", "extras": ["shed","clothesline","swing_set","garden","doghouse","flagpole","birdbath","tire_swing","above_ground_pool","woodpile"]}
- `condition`: kept | worn | shabby | boarded
- `year_built`: n
- names: `{"family": "Surname", "house_number": "412", "street": "Oak St"}`

**store** (a commercial block on the lot; 1-3 storefronts)
- `storeys`: 1 | 2 | 3;  `facade`: brick | stone | cast_iron_front | frame_false_front | stucco | glass_modern | block
- `cornice`: bracketed_metal | corbelled_brick | parapet_stepped | parapet_flat | pediment | none
- `upper_use`: none | apartments | offices | lodge_hall | storage | hotel_rooms
- `storefronts`: [{"business": "Name", "type": <business type>, "sign": "main sign text", "sign_style": "painted_wall|projecting|flat_board|neon|awning_lettering|window_lettering", "awning": bool, "extra_signs": ["hours text", ...]}]
- business types: diner | cafe | bar | bank | hardware | grocery | drug_store | barber | beauty_salon |
  dry_goods | clothing | shoe_store | jeweler | furniture | appliance_repair | bakery | butcher |
  feed_seed | auto_parts | insurance_office | law_office | doctor_office | dentist | newspaper |
  movie_theater | variety_store | bookstore | laundromat | florist | pizza | pool_hall |
  sporting_goods | thrift_store | video_rental | gas_station | auto_repair | motel | funeral_home |
  tavern_hotel | vacant_storefront | music_store | print_shop | shoe_repair | real_estate
- `condition`, `year_built` as for houses

**church**: `style`: gothic_revival | carpenter_gothic | romanesque | greek_revival | colonial_revival |
  modern_a_frame | prairie;  `walls` (house vocabulary), `tower`: {"position": "front_center|front_corner|side|none", "top": "spire|belfry_cupola|crenellated|none"},
  `plan`: rectangle | cruciform | l_shape;  names: `{"name": "St. Brendan's Catholic Church", "denomination": "...", "sign": "..."}`

**civic** (label says what it is: City Hall, Courthouse, Library, Post Office, Hospital, Fire / Police,
Town Hall, Opera House, Depot, ...): `use` (from the label), `style`: romanesque | beaux_arts |
classical_revival | art_deco | italianate | prairie | modern | vernacular;  `storeys`, `walls`,
`dome_or_cupola`: none | dome | cupola | clock_tower;  names: `{"name": "...", "sign": "...", "plaque": "year / motto"}`

**school**: `era` (year), `storeys`, `style` (civic vocabulary), `walls`, `wings`: n;
names: `{"name": "Lincoln Elementary", "mascot": "...", "sign": "..."}`

**industrial**: `use`: grain_elevator | flour_mill | foundry | machine_works | creamery | brewery |
lumber_yard | cannery | brickworks | power_plant | factory;  `components`: [...free words];
`walls`: brick | metal | concrete | frame;  `storeys`;  names: `{"name": "...", "sign": "..."}`

**tower** (water tower): `type`: tin_man | multi_leg_tank | spheroid | fluted_column | standpipe;
`paint`: {"color": "#...", "lettering": "TOWN NAME"}

**bigbox / strip**: `stores`: [{"business": "...", "type": "grocery|discount|pharmacy|hardware|pet|dollar|video_rental|pizza|laundromat|nail_salon|tax_office|vacant", "sign": "..."}], `era`

**vacant**: what it used to be (`former`: a store/industrial trait set) + `condition`: boarded | fire_damaged | shell

**farm**: barn `type`: bank_barn | gambrel_dairy | english_three_bay | round_barn | pole_barn | tobacco |
crib_barn;  silo `type`: concrete_stave | brick | tile | harvestore_blue | wood_stave;  shed `type`:
pole_shed | quonset | frame_machine_shed | corn_crib;  plus `colors`, `condition`

**crossing**: `bridge_type`: pony_truss | through_truss_pratt | through_truss_parker | warren_pony |
steel_stringer | concrete_slab | concrete_t_beam | concrete_arch | stone_arch | box_culvert |
pipe_culvert | steel_girder_rail | timber_trestle | deck_girder;  `spans`: n;  `year`;
`railing`: lattice | concrete_balustrade | guardrail | pipe_rail | open_parapet;  names: `{"plate": "builder plate text", "sign": "creek name sign"}`
