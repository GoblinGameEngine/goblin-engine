#!/usr/bin/env python3
"""make_r2.py -- warren research stream 2 (East and Southeast Asia): one data table -> r2_<family>.md + r2_grammars.json.

  python3 research/sky_islands/warrens/make_r2.py

The user, 2026-10-14 (00_brief.md): actual warrens, each island its own twisting city built for centuries on top of
its earlier layers, beautiful and cyberpunk, with its civilization's own mark and plants; new buildings only by adding
pieces to the shared kit; dense, walkable, ponds and green space, large paved main streets.

Figures marked (est.) are working values where no source gives a number (most sources describe; few measure).
Kit ids are the shared vocabulary of research/sky_islands/architecture/components.json; "new:" ids are pieces this
family needs that the kit does not have yet.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

F = []          # the families


def fam(**kw):
    F.append(kw)


# ---------------------------------------------------------------------------------------------------------------
fam(
    id="kowloon_walled",
    name="Kowloon Walled City: the fused block",
    mark="One continuous 10-14 storey mass with no gaps: 350 buildings fused into a single block, its alleys tunnels "
         "under it, its roof a separate village of aerials, tanks, ladders and children, an aircraft skimming overhead.",
    sources=["Kowloon Walled City, Hong Kong (c.1945-1993)"],
    refs=[
        ("Kowloon Walled City (Wikipedia): area 210 x 120 m, ~350 buildings, 13-14 storey limit (Kai Tak), 23 m2 flats, "
         "alleys 1-2 m, 8 municipal water pipes, 77 wells, roofs with aerials/tanks/ladders",
         "https://en.wikipedia.org/wiki/Kowloon_Walled_City"),
        ("Greg Girard & Ian Lambot, City of Darkness (1993), interview: low dripping alleys, pipes overhead, rooftop air",
         "https://www.1854.photography/2015/03/kowloon-walled-city-greg-girard"),
        ("The Japanese survey cross-section (Kowloon City Expedition, H. Kani; drawn by H. Terasawa), annotated scan",
         "https://www.rioleo.org/kowloon"),
        ("Spoon & Tamago on the cross-section", "https://spoon-tamago.com/detailed-cross-section-of-the-kowloon-walled-city-created-by-japanese-researchers/"),
        ("Colossal: the illustrated cross-section", "https://www.thisiscolossal.com/2024/07/kowlooon-walled-city-illustration/"),
        ("Metropolis: how the vertical village came to be", "https://metropolismag.com/projects/how-hong-kongs-vertical-village-came-be/"),
        ("Rare historical photos of the Walled City", "https://rarehistoricalphotos.com/kowloon-walled-city-photos/"),
        ("Rooftop slums of Hong Kong (Wikipedia)", "https://en.wikipedia.org/wiki/Rooftop_slum"),
        ("Gwulo: Kowloon City, a brief history", "https://gwulo.com/node/19851"),
    ],
    history=[
        "1847: a Qing fort with a stone wall 4 m high and 4.6 m thick round ~2.6 ha (the yamen at its centre).",
        "1943: the wall pulled down for Kai Tak's runway; 1947 ~2,000 squatters in one-storey huts.",
        "1950: a fire destroys 2,500 huts; rebuilt as 2-4 storey brick and concrete.",
        "1960s-70s: developers combine plots and pour 10-14 storey reinforced-concrete towers without permits, each new "
        "tower built hard against the last, some on top of older ones; light only from the gaps between towers.",
        "late 1970s-80s: maximum size, the block fused; upper floors widen out over the alleys; caged balconies; "
        "rooftop huts, pigeon lofts and tanks; the roof a separate public level crossed by ladders and planks.",
        "Kai Tak's approach 800 m south capped it at 13-14 storeys: the roofline is almost flat -- one plateau.",
    ],
    grammar=dict(
        cell_m=[3.0, 3.0], storey_m=2.7, storeys=[10, 14],
        walls=dict(material="raw/rendered reinforced concrete, unpainted or once-painted; tile spandrels; patched",
                   thickness_m=0.2, palette=["#8e8a80", "#a9a497", "#6f6c63", "#c2bba9", "#5d6b66", "#b8a27a"],
                   weathering="black water streaks under every sill and pipe, rust bleed from cages, moss at the "
                              "base, blotchy repaint patches"),
        mass="Fill the plot almost completely; towers of 4-12 m frontage abut on every side; every storey above 3 "
             "steps out 0.3-0.8 m over the alleys; a single near-flat roof plane at 13-14 storeys (+/- 1). Light "
             "wells: a few 2-4 m shafts punched down through the mass.",
        streets=[
            dict(kind="perimeter street (outside the mass)", width_m=8, notes="the open edge; dentists' signs face it"),
            dict(kind="main alley (named, through the block)", width_m=2.0, notes="covered for most of its length by "
                 "the floors above; fluorescent tubes; open drain"),
            dict(kind="branch alley", width_m=1.2, notes="dead ends, steps, doglegs every 10-20 m"),
            dict(kind="upper passages", width_m=1.0, notes="corridors and stair links between towers at many levels: "
                 "one can cross the city without touching the ground"),
            dict(kind="roof level", width_m=None, notes="ladders and planks between roofs that differ by 0-2 m"),
        ],
        growth=[
            dict(layer="ground (oldest)", what="2-4 storey brick shops, workshops, temples (Tin Hau, Fuk Tak), the "
                 "yamen courtyard; wells", materials=["brick", "stone", "timber"]),
            dict(layer="towers", what="8-12 storey concrete slab towers, 1-2 flats a floor, open stairs",
                 materials=["concrete", "tile", "steel window frames"]),
            dict(layer="overgrowth", what="caged balconies, wider upper floors, infill over alleys, tower-to-tower "
                 "bridges, pipes and cables everywhere", materials=["steel mesh", "pipe", "plywood"]),
            dict(layer="roof village", what="huts, pigeon lofts, water tanks, TV aerial forest, clothes lines, a "
                 "playground", materials=["corrugated iron", "timber", "fibreglass tanks"]),
            dict(layer="cyberpunk (Aloft)", what="LED strips down the alley ceilings, signs crammed at every ground "
                 "door, screens, cable trays, dot-matrix boards, rooftop antennas turned dishes",
                 materials=["LED", "polycarbonate", "fibre"]),
        ],
        openings="Small sliding steel-framed windows, most behind welded grilles or cages; louvres; AC boxes through "
                 "walls; no ornament but signs.",
        roofs="Flat concrete roof slabs at slightly different heights, parapets 1 m, tanks on stilts, aerials 2-6 m.",
        ornament="None architectural; the signs are the ornament: dentists, doctors, fishball factories, temples.",
        public_spaces="Almost none inside: the yamen courtyard, two temples, a few widened alley junctions; the roof "
                      "is the plaza. On an island: keep the dense block but frame it with a broad paved perimeter "
                      "street, a market square and a pond garden outside one face (the park that replaced it).",
        water="Wells inside (77), standpipes; open drains down alleys; drips from every pipe.",
    ),
    foliage=[
        dict(species="Ficus microcarpa (Chinese banyan), self-sown", form="roots strangling walls and roof edges",
             height_m=[1, 6], where="roof parapets, old wall faces, light-well bottoms", colour="#3f6b3a"),
        dict(species="potted plants (bougainvillea, jade, chillies, aloe)", form="clusters of pots and polystyrene "
             "boxes", height_m=[0.3, 1.5], where="roof edges, cage balconies, ledges", colour="#4f7f3d / #c4307a"),
        dict(species="the park round it (perimeter)", form="Cantonese garden: willows, bamboo, pond, rockery",
             height_m=[3, 10], where="the green frame outside the block", colour="#5c8a4a"),
    ],
    cyberpunk=dict(
        elements=["fluorescent tube runs along alley ceilings", "pipe and cable bundles 20-60 per alley",
                  "projecting signs at every ground door (dentists, clinics, noodle makers)", "cage balconies lit "
                  "from inside", "rooftop dish forest", "LED strip edges on the roof plateau"],
        night="Dark mass with thousands of small lit windows; cold fluorescent green-white in the alleys; warm "
              "tungsten in flats; red/blue sign glow only at the edges and alley mouths; aircraft-warning lights on "
              "the roof plateau corners."),
    kit=dict(
        shared=[
            dict(id="wall_panel_concrete", params="3 m bay, 2.7 m storey, small window 0.9x1.0 off-centre"),
            dict(id="window_grille", params="welded bars, every window below storey 4"),
            dict(id="balcony_cage", params="0.6-0.9 m deep mesh cage, 40% of upper bays"),
            dict(id="ac_unit", params="1-2 per bay, randomly offset"),
            dict(id="pipe_run", params="vertical down every 2nd bay, horizontal along alley ceilings"),
            dict(id="cable_tray", params="alley ceilings"),
            dict(id="fluoro_tube", params="alley ceilings every 4 m"),
            dict(id="water_tank", params="roof, 1-3 per tower"),
            dict(id="antenna", params="roof, 3-8 per tower"),
            dict(id="rooftop_shack", params="roof, 20-40% of roofs"),
            dict(id="ladder_roof", params="between roof steps"),
            dict(id="plank_bridge", params="over light wells and roof gaps"),
            dict(id="laundry_line", params="cage fronts and roofs"),
            dict(id="sign_blade", params="every ground door, stacked 2-3 high"),
            dict(id="sign_board", params="door heads"),
            dict(id="light_shaft", params="2-4 m shafts through the mass"),
            dict(id="covered_alley", params="1.2-2 m, roofed by the floors above"),
        ],
        unique=[
            "new: cantilever_step (an upper storey stepped 0.3-0.8 m over an alley: the overhang band)",
            "new: tower_seam (the joint where two towers meet: a vertical patched strip with pipes)",
            "new: roof_playground (a fenced rooftop court with a swing and a basket)",
        ],
        params=dict(proportions="tall narrow towers 4-12 m wide, 10-14 storeys, one flat roof plane",
                    rhythm="irregular 3 m bays, no alignment between neighbours (each tower its own storey "
                           "heights: 2.6-3.0 m)",
                    depth="grilles and cages make the facade 0.6-0.9 m deep; alleys roofed over",
                    colours="concrete greys, faded tile pastels, rust",
                    materials="concrete, mesh, corrugated iron on the roof"),
    ),
    street_hierarchy="perimeter street 8 m (paved, the market edge) > main alleys 2 m (tunnels) > branch alleys "
                     "1.2 m > upper passages 1 m > roof ladders",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="hk_neon_canyon",
    name="Hong Kong tong lau and the neon canyon (Mong Kok, Sham Shui Po, Yau Ma Tei)",
    mark="A grid of narrow 6-12 storey walk-ups lining canyon streets, with verandahs over the pavement below and a "
         "storm of projecting signs over the street; the roofs carry a second, illegal village of huts.",
    sources=["Hong Kong tong lau (shophouses) 1900s-1960s", "Mong Kok / Nathan Road", "Sham Shui Po rooftop huts"],
    refs=[
        ("Gwulo: Tong Lau, the Hong Kong shophouse (Lee & DiStefano)", "https://gwulo.com/node/34384"),
        ("CityUnseen: Ghost Buildings (1903 ordinance: 4 storeys, light wells, back alleys; verandahs over the footpath)",
         "https://cityunseen.hk/?p=626"),
        ("SCMP: tong lau and composite buildings", "https://m.scmp.com/news/hong-kong/health-environment/article/3014526/upstairs-downstairs-how-hong-kongs-historic-tong"),
        ("M+ / West Kowloon: neon signs of Hong Kong", "https://artsandculture.google.com/story/ogWRMXUKqUGzJg"),
        ("Goldthread: Hong Kong's fading neon", "https://goldthread2.com/travel/hong-kong-fading-neon-lights/article/3019495"),
        ("Rooftop slum (Wikipedia): 1950s-60s tenement roofs turned into housing", "https://en.wikipedia.org/wiki/Rooftop_slum"),
        ("Hong Kong Memory: Sham Shui Po squatters", "https://www.hkmemory.hk/en/collections-ssphousing-development-squatters.html"),
        ("Canadian Architect: Portraits from Above (rooftop communities)", "https://staging7.canadianarchitect.com/portraits-from-above"),
        ("Planning Dept: Kowloon City urban renewal (tong lau loss)", "https://www.pland.gov.hk/file/resources/durf/pdf/20120228/DURF_KC_01_2012_en.pdf"),
    ],
    history=[
        "Pre-war tong lau: 3-4 storeys, 4.5 m frontage (est.), 12-15 m deep, ground shop, timber floors, pitched "
        "Chinese tile roofs, verandahs on columns over the five-foot way.",
        "Post-war tong lau: 6-9 storeys of concrete, flat roofs, cantilevered balconies instead of verandahs, a stair "
        "at the side, no lifts.",
        "1950s-60s: refugees build huts on the flat roofs; balconies enclosed; signs grow out over the street on steel "
        "arms (up to 4.2 m out by the rules, often more).",
        "Composite buildings (1960s): a podium of shops with 12-20 storeys of flats above; tower blocks fill gaps.",
    ],
    grammar=dict(
        cell_m=[4.5, 3.0], storey_m=3.0, storeys=[4, 12],
        walls=dict(material="rendered concrete and brick, painted; mosaic tiles on 1960s fronts",
                   thickness_m=0.25, palette=["#d9cdb4", "#b9c4b0", "#e6d9a8", "#9fb3b8", "#c98f6a", "#7d7a73"],
                   weathering="stained render, rust from balcony rails, AC drip streaks"),
        mass="Terraces of identical-width buildings along a street grid (blocks 50-80 m x 20-30 m); back alleys 2-3 m "
             "between back-to-back rows; heights jump 4 -> 12 storeys within a row.",
        streets=[
            dict(kind="main road (Nathan Road)", width_m=24, notes="trams/buses; sign canopy over it"),
            dict(kind="market street (Temple St, Fa Yuen St)", width_m=10, notes="stalls fill the carriageway"),
            dict(kind="side street", width_m=8, notes="sign canyon, verandah arcades"),
            dict(kind="back lane", width_m=2.5, notes="kitchens, pipes, rubbish, back stairs"),
        ],
        growth=[
            dict(layer="pre-war", what="3-4 storey verandah shophouses with tile roofs", materials=["brick", "timber", "clay tile"]),
            dict(layer="post-war", what="6-9 storey concrete walk-ups, balconies", materials=["concrete", "mosaic tile", "steel windows"]),
            dict(layer="overgrowth", what="enclosed balconies, window cages, rooftop huts 2-3 storeys high, AC units, "
                 "signs on arms", materials=["aluminium", "corrugated iron", "acrylic"]),
            dict(layer="cyberpunk", what="LED walls, video boards on corners, sign forests to 6 storeys",
                 materials=["LED", "steel arms"]),
        ],
        openings="Steel casement windows in pairs; balconies with green-painted rails; ground floor fully open to "
                 "shops with roller shutters.",
        roofs="Flat roofs with water tanks, huts, aerials; pre-war: Chinese tile pitched roofs behind parapets.",
        ornament="Art Deco and modernist name plaques, mosaic tile panels, Chinese characters in relief.",
        public_spaces="Market streets, a temple square (Tin Hau, Yau Ma Tei), small sitting-out areas, a rooftop "
                      "playground on a resettlement block; on an island: one boulevard 18-24 m with tram, a temple "
                      "square with banyans, a pond park.",
        water="Hydrants, rooftop tanks; harbour edge.",
    ),
    foliage=[
        dict(species="Ficus microcarpa (Chinese banyan)", form="huge spreading crown, aerial roots; grows out of "
             "old retaining walls (Hong Kong 'stone-wall trees')", height_m=[8, 18], where="temple squares, walls",
             colour="#3e6a35"),
        dict(species="Bombax ceiba (red cotton tree)", form="tall, bare in spring with red flowers", height_m=[10, 20],
             where="parks and boulevards", colour="#b8322a"),
        dict(species="Delonix regia (flame tree)", form="umbrella crown, scarlet in summer", height_m=[6, 12],
             where="street edges", colour="#d8432a"),
        dict(species="potted plants and polystyrene vegetable boxes", form="pots", height_m=[0.2, 1.2],
             where="rooftops, window ledges, cage balconies", colour="#4f7f3d"),
    ],
    cyberpunk=dict(
        elements=["projecting neon/LED signs on steel arms 2-6 storeys up, overlapping across the street",
                  "corner video boards", "AC boxes on every window", "lit rooftop huts"],
        night="The classic: a canopy of red, magenta, blue and green neon over a yellow-white street; flats above dim "
              "warm; rooftop huts with single bulbs."),
    kit=dict(
        shared=[
            dict(id="wall_panel_render", params="4.5 m bay of 2 windows, 3 m storeys"),
            dict(id="balcony_cantilever", params="0.9 m, green rail, every bay above 3"),
            dict(id="arcade_pier", params="verandah columns at the kerb, 3 m spacing (pre-war rows)"),
            dict(id="shopfront_shutter", params="ground"),
            dict(id="sign_blade", params="steel arm, 1.5-6 storeys, 1-3 per frontage"),
            dict(id="neon_frame", params="on blades"),
            dict(id="video_board", params="corners"),
            dict(id="ac_unit", params="every window"),
            dict(id="window_grille", params="lower floors"),
            dict(id="rooftop_shack", params="50% of roofs, 1-3 storeys of huts"),
            dict(id="water_tank", params="roofs"),
            dict(id="barrel_tile_eave", params="pre-war roofs"),
            dict(id="tile_panel", params="mosaic spandrels"),
        ],
        unique=["new: sign_arm (a steel gantry carrying a projecting sign out over the street)",
                "new: verandah_bay (a pre-war verandah bay: columns, balcony slab, shutters)"],
        params=dict(proportions="4.5 m frontages, 3:1 to 6:1 height to width", rhythm="regular bays within a "
                    "building, jumps between buildings", depth="balconies 0.9 m, signs 2-4 m out",
                    colours="pale greens, creams, faded blues; signs saturated", materials="render, mosaic, steel"),
    ),
    street_hierarchy="boulevard 24 m > market street 10 m > side street 8 m > back lane 2.5 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="chongqing_cliff",
    name="Chongqing: the mountain city (diaojiaolou stilt houses, Hongyadong, Shibati)",
    mark="A city poured down a cliff: stilted timber houses on tall poles, streets that enter a building at its "
         "11th floor and leave at its 1st, stairs instead of streets, monorails through buildings, mist.",
    sources=["Chongqing Yuzhong peninsula", "Hongyadong (11-13 storey stilt complex on a cliff)", "Shibati old town",
             "Ciqikou", "Liziba (monorail through a 19-storey block)"],
    refs=[
        ("Hongya Cave (Wikipedia): a stilt-house complex on the cliff above the Jialing", "https://en.wikipedia.org/wiki/Hongya_Cave"),
        ("Chongqing gov't: Hongyadong, 13-storey stilt cluster", "https://english.cq.gov.cn/specials/explore/PhotoPerfectSpots/202608/t20260810_15912600.html"),
        ("travelchina: enter on the 11th floor at Cangbai Rd, leave at Jiabin Rd", "https://www.travelchina.org.cn/en/article/NQ0zLwVYgSwN"),
        ("Liziba station (Wikipedia): the monorail stops inside a 19-storey residential building", "https://en.wikipedia.org/wiki/Liziba_station"),
        ("Asia Times: monorail runs through residential blocks", "https://asiatimes.com/2018/04/monorail-chinas-chongqing-runs-residential-blocks/"),
        ("Chinavigators: Chongqing at night (neon, cable cars)", "https://www.chinavigators.com/chongqing-at-night/"),
        ("Hongyadong night view", "https://chinafortravelers.com/guides/hongyadong-night-view/"),
    ],
    history=[
        "Diaojiaolou: Tujia/Ba stilt houses -- timber frames on tall wooden poles where the slope drops, the back "
        "resting on rock, the front on stilts 3-10 m high; galleries and hanging balconies.",
        "Dense riverside quarters of stilt houses until 1949; staircases (Shibati: 'eighteen steps') as streets.",
        "1990s-2010s: concrete towers built down the same slopes, with entrances at many levels and skybridges from "
        "streets above into upper floors; Hongyadong rebuilt (2006) as an 11-storey stilt-style complex.",
    ],
    grammar=dict(
        cell_m=[4.0, 4.0], storey_m=3.2, storeys=[3, 13],
        walls=dict(material="dark timber frame with plank/lath infill and grey brick; later concrete with timber "
                   "cladding", thickness_m=0.15,
                   palette=["#4a3324", "#6b4a32", "#8a8a84", "#3b3b38", "#c9a35a", "#a8322a"],
                   weathering="dark wet timber, moss in the mist, soot"),
        mass="Terraces stepping down the slope; each terrace's buildings stand on stilts on the downhill side; "
             "buildings span several terraces (an upper-street door and a lower-street door); towers on the ridge.",
        streets=[
            dict(kind="ridge road", width_m=12, notes="on top; buildings entered at their top floors"),
            dict(kind="contour street", width_m=5, notes="along the slope, shop-lined"),
            dict(kind="stair street", width_m=3, notes="straight down the slope, landings, 150-300 steps"),
            dict(kind="sky-bridge", width_m=2.5, notes="from a street into a building's upper floor"),
            dict(kind="stilt underdeck", width_m=None, notes="spaces beneath the stilts: workshops, stalls"),
        ],
        growth=[
            dict(layer="stilt village", what="2-4 storey diaojiaolou on poles, tile roofs, galleries",
                 materials=["fir timber", "bamboo", "grey tile", "stone footings"]),
            dict(layer="brick and concrete", what="5-9 storey blocks on the terraces, stairs everywhere",
                 materials=["grey brick", "concrete"]),
            dict(layer="vertical", what="towers to 30+ storeys on the ridge, skybridges, a monorail through a block",
                 materials=["concrete", "glass"]),
            dict(layer="cyberpunk", what="golden outline lighting on every eave, LED-lit stairs, cable cars, "
                 "screens on tower crowns", materials=["LED", "steel cable"]),
        ],
        openings="Timber lattice windows, sliding panels; wide galleries with timber railings on every storey.",
        roofs="Grey tile, shallow pitch, upturned eave corners (flying eaves), stacked tier on tier down the slope.",
        ornament="Red lanterns, carved railings, brackets; gold edge lighting at night.",
        public_spaces="Landings on the stair streets (tea houses), a riverside promenade at the bottom, temple "
                      "terraces; on an island: a broad ridge boulevard, terraced gardens, a pond at the bottom terrace.",
        water="The river at the foot; mist; rain runoff down the stairs.",
    ),
    foliage=[
        dict(species="Ficus virens / banyan", form="huge crowns over landings", height_m=[8, 16],
             where="stair landings, terraces", colour="#456f38"),
        dict(species="Cinnamomum camphora (camphor)", form="broad dense crown", height_m=[8, 15],
             where="ridge roads", colour="#3f6232"),
        dict(species="bamboo groves", form="clumps", height_m=[4, 9], where="steep gaps between terraces",
             colour="#6d9a46"),
        dict(species="Chongqing ivy and moss", form="wall cover", height_m=[0, 0], where="retaining walls",
             colour="#4f7a3a"),
    ],
    cyberpunk=dict(
        elements=["every eave traced in warm gold LED", "monorail tube through a tower", "cable car lines across",
                  "screens on ridge tower crowns", "lit stair streets"],
        night="A golden mountain of outlined eaves stacked down the cliff, reflected in water; towers above with "
              "colour-changing crowns; mist catching beams."),
    kit=dict(
        shared=[
            dict(id="gallery_timber", params="every storey, 1.2 m deep, timber rails"),
            dict(id="timber_eave", params="flying corners, 1 m overhang"),
            dict(id="eave_stack", params="tiers stacked down the slope"),
            dict(id="stair_external_steep", params="stair streets 3 m wide"),
            dict(id="skybridge", params="street to upper floors"),
            dict(id="lantern_cn", params="red, under eaves"),
            dict(id="eave_bulbs", params="gold outline on every eave"),
            dict(id="screen_lattice", params="timber lattice windows"),
            dict(id="cantilever_beam", params="stilt/beam ends"),
        ],
        unique=["new: stilt_frame (a timber pole frame 3-10 m tall carrying a building's downhill side)",
                "new: hanging_balcony (diaojiaolou cantilevered gallery with a skirt)",
                "new: monorail_beam (a concrete track beam on piers, can pass through a block)"],
        params=dict(proportions="buildings span several terraces; storeys 3.2 m; stilts 3-10 m",
                    rhythm="tiered eaves every storey", depth="galleries 1.2 m, eaves 1 m",
                    colours="dark timber, grey tile, red lanterns, gold light",
                    materials="timber, tile, brick, concrete"),
    ),
    street_hierarchy="ridge boulevard 12 m > contour streets 5 m > stair streets 3 m > skybridges 2.5 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="jiangnan_water",
    name="Jiangnan water town and the Shanghai lilong (Zhouzhuang, Suzhou, Wuzhen, shikumen lanes)",
    mark="White walls and black tiles over canals: houses front a lane and back onto the water with private steps "
         "down to boats, humpbacked stone bridges, and dense lilong lane-quarters behind stone gates.",
    sources=["Zhouzhuang", "Suzhou Pingjiang", "Wuzhen", "Shanghai shikumen lilong"],
    refs=[
        ("Zhouzhuang: 井-shaped canal grid, 14 stone bridges, 60% original Ming-Qing houses, Double Bridge", "https://govt.chinadaily.com.cn/s/202202/17/WS620e1c44498e6a12c121f514/zhouzhuang-water-town.html"),
        ("Amusing Planet: the water town of Zhouzhuang", "https://www.amusingplanet.com/2014/08/the-water-town-of-zhouzhuang.html"),
        ("Google Arts: architectural features of Wuzhen", "https://artsandculture.google.com/story/cwUhm9yYS8-aIg"),
        ("Jiangnan families: houses backed by rivers, facing roads, private wharfs", "https://www.privatephotoreview.com/2024/12/09/recording-the-real-scene-of-families-in-the-ancient-town-of-jiangnan/"),
        ("Shikumen (Wikipedia): trunk lane, branch lanes, stone gateways, 2-3 storeys", "https://en.wikipedia.org/wiki/Shikumen"),
        ("SmartShanghai: walking into the lanes", "https://www.smartshanghai.com/articles/shanghai-life/walking-into-the-lanes-of-shanghai"),
        ("UNESCO tentative list: water towns", "https://whc.unesco.org/en/tentativelists/5328/"),
    ],
    history=[
        "Song-Qing: canal towns where the canal is the main street; houses 2 storeys, front shop on the lane, "
        "workshop and wharf on the water; courtyards (tianjing) inside.",
        "1860s-1930s Shanghai: shikumen lilong -- rows of 2-3 storey terraced houses behind stone-framed gates, on a "
        "trunk lane with branch lanes, the whole quarter behind a street-front shop row.",
        "Later: rooms added on top (tingzijian, rooftop terraces), sheds, laundry poles over the lanes, wires.",
    ],
    grammar=dict(
        cell_m=[4.0, 3.5], storey_m=3.2, storeys=[2, 4],
        walls=dict(material="whitewashed brick with grey-black tile copings; dark timber front panels and doors",
                   thickness_m=0.3, palette=["#ece8dc", "#d8d3c5", "#2f2f2f", "#5a4632", "#8c8a82", "#a03a2c"],
                   weathering="grey-green mildew streaks down the white, black lichen at the base"),
        mass="Long narrow houses (4 m x 15-30 m) in rows between a lane and a canal, with 1-3 small courtyards each; "
             "lilong quarters: rows of terraced houses in a comb off a trunk lane.",
        streets=[
            dict(kind="canal", width_m=8, notes="the main street; boats; stone revetments 1-2 m high"),
            dict(kind="canal-side street", width_m=4, notes="stone-paved, shops, covered loggias over the water"),
            dict(kind="lane (lilong trunk)", width_m=4, notes="behind a stone gate"),
            dict(kind="branch lane", width_m=2.5, notes="doorsteps, chairs, laundry poles overhead"),
            dict(kind="bridge", width_m=3, notes="humpbacked stone arch, steps"),
        ],
        growth=[
            dict(layer="water town", what="2-storey white houses with timber fronts on canals, bridges, temples",
                 materials=["brick", "whitewash", "timber", "black tile", "granite"]),
            dict(layer="lilong", what="3-storey shikumen rows with stone gate frames", materials=["grey/red brick", "stone"]),
            dict(layer="overgrowth", what="rooftop rooms, sheds over courtyards, laundry poles, wires, AC",
                 materials=["timber", "corrugated", "plastic"]),
            dict(layer="cyberpunk", what="red lantern strings over canals turned to LED, holographic shop "
                 "signs on timber fronts, lit boats", materials=["LED", "acrylic"]),
        ],
        openings="Full-width timber shop fronts of removable boards; lattice upper windows; round and leaf-shaped "
                 "moon-gates in garden walls; stone-framed shikumen doors with black lacquered leaves.",
        roofs="Black tile, double-pitched, gentle curve, ridges with upturned ends; stepped gable firewalls (horse-"
              "head walls in Huizhou-influenced towns).",
        ornament="Carved brick gate frames, timber lattice, red lanterns, ink calligraphy shop banners.",
        public_spaces="Canal junction squares, bridge landings, a temple, a classical garden (pond, rockery, "
                      "pavilions); on an island: a central canal loop with a broad stone quay street, a lotus pond "
                      "garden, a market square at a bridge.",
        water="Canals everywhere: the island has a grid of 2-3 canals round a central pond.",
    ),
    foliage=[
        dict(species="weeping willow (Salix babylonica)", form="drooping", height_m=[6, 12], where="canal edges",
             colour="#7fa64a"),
        dict(species="lotus (Nelumbo)", form="pads and pink flowers", height_m=[0.5, 1.5], where="ponds",
             colour="#5f9a3e / #e89ab0"),
        dict(species="osmanthus, plum, camellia", form="small round trees and shrubs", height_m=[2, 5],
             where="courtyards, gardens", colour="#3f6b36"),
        dict(species="bamboo", form="clumps behind white walls", height_m=[3, 7], where="gardens", colour="#6d9a46"),
    ],
    cyberpunk=dict(
        elements=["red LED lanterns strung across canals", "neon calligraphy banners", "lit boats", "projection on "
                  "white walls", "screens behind lattice windows"],
        night="White walls lit warm from below by lanterns and reflected in black water; red lanterns doubled in "
              "the canals; quiet, glowing, misty."),
    kit=dict(
        shared=[
            dict(id="wall_panel_white", params="whitewash, black tile coping, 4 m bays"),
            dict(id="shopfront_shutter", params="timber board fronts"),
            dict(id="screen_lattice", params="upper windows"),
            dict(id="lantern_cn", params="red, strings over canals"),
            dict(id="gable_step", params="horse-head firewalls on row ends"),
            dict(id="water_channel", params="canals"),
            dict(id="gate_portal", params="stone shikumen gate frames"),
            dict(id="laundry_line", params="bamboo poles over lanes"),
            dict(id="timber_eave", params="shallow, black tile"),
        ],
        unique=["new: hump_bridge (a single-arch stone bridge with steps)",
                "new: water_steps (stone steps down from a back door to the canal)",
                "new: moon_gate (a round opening in a garden wall)"],
        params=dict(proportions="low (2-3 storeys), long and narrow, roofs dominant", rhythm="repeated narrow fronts "
                    "with black roofs stepping", depth="shallow timber fronts, deep overhanging eaves 0.8 m",
                    colours="white / black / dark timber / red accents", materials="brick, whitewash, tile, granite"),
    ),
    street_hierarchy="canal 8 m (+ quay streets 4 m) > lilong trunk lane 4 m > branch lanes 2.5 m > bridges",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="hakka_tulou",
    name="Hakka tulou: earthen ring-houses (Fujian)",
    mark="Huge round or square rammed-earth fortresses, blank outside, open inside: 3-5 storeys of timber galleries "
         "ringing a courtyard with an ancestral hall at the centre; a clan in each ring; rings clustered in a valley.",
    sources=["Fujian tulou (UNESCO 2008): Chengqilou, Eryilou, Tianluokeng cluster"],
    refs=[
        ("Studio Matrx: Hakka roundhouses", "https://www.studiomatrx.org/architecture-canon/tulou-hakka-roundhouses"),
        ("National Geographic: the tulou", "https://www.nationalgeographic.com/travel/article/150102-hakka-china-tulou-fujian-world-heritage"),
        ("CGTN: Fujian tulou", "https://news.cgtn.com/news/3d3d514d3351444e34457a6333566d54/index.html"),
        ("Loongese: Chengqilou four rings, 288 rooms; Eryi walls 2.5 m, 73.4 m diameter", "https://loongese.com/blog/heritages/fujian_tulou"),
    ],
    history=[
        "12th-20th c.: Hakka clans build defensible communal houses: walls 1.5-2.5 m of rammed earth with bamboo and "
        "timber strips, round or square, 3-5 storeys, one gate.",
        "Ground floor kitchens, first floor granaries, upper floors bedrooms; galleries face the court.",
        "Inner rings (lower) and an ancestral hall at the centre; wells in the court.",
        "Clusters (Tianluokeng: one square and four round) sit together in valleys among tea terraces.",
    ],
    grammar=dict(
        cell_m=[3.0, 3.0], storey_m=2.8, storeys=[3, 5],
        walls=dict(material="rammed earth, ochre-yellow, smooth; stone base 1-2 m; few small windows only high up",
                   thickness_m=1.8, palette=["#c8a46a", "#b58d55", "#8a6a44", "#3a3a3a", "#6b4a2e", "#a03a2c"],
                   weathering="rain-streaked earth, darker band at the base"),
        mass="Rings of diameter 30-75 m (or squares 30-50 m), 3-5 storeys, one or two inner rings, a central hall; "
             "rings sit 20-60 m apart with lanes and terraces between; on an island: 5-12 rings of different sizes "
             "linked by lanes and later infill.",
        streets=[
            dict(kind="valley road", width_m=6, notes="between the rings, paved stone"),
            dict(kind="ring gate passage", width_m=3, notes="the single gate through the wall"),
            dict(kind="internal gallery", width_m=1.2, notes="each storey's circular walkway"),
            dict(kind="terrace path", width_m=1.5, notes="among tea terraces"),
        ],
        growth=[
            dict(layer="rings", what="the earthen rings and the ancestral halls", materials=["rammed earth", "timber", "tile"]),
            dict(layer="infill", what="lower outbuildings between rings, then 2-4 storey brick houses",
                 materials=["brick", "timber"]),
            dict(layer="bridges", what="timber and steel bridges from ring roof to ring roof (Aloft)",
                 materials=["timber", "steel"]),
            dict(layer="cyberpunk", what="each gallery ring traced in light, screens inside the court, lanterns",
                 materials=["LED", "paper"]),
        ],
        openings="Outside: tiny slit windows only on upper floors, one massive gate. Inside: continuous timber "
                 "galleries with lattice doors to every room.",
        roofs="One continuous grey tile roof round the ring with a wide eave (2-3 m) overhanging the outside wall.",
        ornament="Couplets on red paper at the gate, carved timber in the hall, lanterns.",
        public_spaces="The courtyard of each ring (shared by its clan), the ancestral hall, a valley market; on an "
                      "island: a central paved square between rings, a pond (the courtyard wells' source), tea "
                      "terraces as green space.",
        water="Wells in every court; a stream or pond between rings.",
    ),
    foliage=[
        dict(species="tea bushes on terraces", form="clipped rows", height_m=[0.8, 1.2], where="terraces", colour="#3e6a2e"),
        dict(species="Cunninghamia (China fir), camphor", form="tall conical/round", height_m=[10, 20],
             where="hillsides", colour="#2f5a2a"),
        dict(species="bamboo, banana", form="clumps", height_m=[3, 7], where="beside rings", colour="#6d9a46"),
    ],
    cyberpunk=dict(
        elements=["every gallery ring traced in warm light", "lanterns hung round the inner gallery", "holographic "
                  "ancestral tablets", "dish antennas on the ring roof"],
        night="From above: glowing rings like reactors in the dark; from the court: tiers of lit galleries."),
    kit=dict(
        shared=[
            dict(id="ring_segment", params="earth ring wall + gallery, diameters 30-75 m"),
            dict(id="gallery_timber", params="inner face, every storey"),
            dict(id="timber_eave", params="2-3 m overhang outside"),
            dict(id="gate_portal", params="one per ring"),
            dict(id="lantern_cn", params="galleries"),
            dict(id="window_small", params="outer slits, top storeys"),
        ],
        unique=["new: ring_roof (the continuous curved tile roof of a ring)",
                "new: ancestral_hall (a small central hall with an open front)"],
        params=dict(proportions="massive curved walls, small windows", rhythm="radial bays of 3 m",
                    depth="walls 1.8 m; galleries 1.2 m", colours="earth ochre, dark timber, grey tile, red",
                    materials="rammed earth, timber, tile"),
    ),
    street_hierarchy="valley road 6 m > gate passages 3 m > terrace paths 1.5 m > galleries 1.2 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="tibetan_lhasa",
    name="Tibetan Lhasa: the Barkhor and its whitewashed courtyard houses",
    mark="Battered whitewashed stone walls leaning inward, windows framed in black trapezoids with little cloth "
         "valances, flat roofs with prayer flags on every corner, a kora circling a temple.",
    sources=["Lhasa old city, the Barkhor", "Potala", "Gyantse", "Ladakh (Leh)"],
    refs=[
        ("Lhasa Archive / THF report: Lhasa's historic urban fabric", "https://asianart.com/associations/lhasa_restoration/report98/ch_02.htm"),
        ("Tibet Heritage Fund: Tibetan vernacular architecture", "https://www.tibetheritagefund.org/page/?r=120"),
        ("THF: a brief introduction to Tibetan architecture", "https://www.tibetheritagefund.org/old_web_2002/5_architecture/5_02/5_02_01_en.html"),
        ("hypersity: renovation of the Kyakashar courtyard, Barkhor", "https://www.gooood.cn/en/renovation-of-the-kyakashar-ancient-courtyard-in-barkhor-street-by-hypersity-architects.htm"),
        ("NPR: the Barkhor, Tibet's spiritual anchor", "https://www.npr.org/2006/09/24/6112107/the-barkhor-gives-tibet-a-spiritual-anchor"),
        ("Prayer flags (Wikipedia)", "https://en.wikipedia.org/wiki/Prayer_flag"),
        ("Charles Bell photographs: poplars and willows at Lukhang", "https://tibet.prm.ox.ac.uk/photo_1998.286.210.html"),
    ],
    history=[
        "7th c.-: the Jokhang and the Barkhor kora ring round it; noble houses of 3-4 storeys round courtyards.",
        "Walls of stone (granite) and mud brick, battered: thick at the base (>1 m), thinner above, the inner face "
        "vertical; flat roofs of earth (arga) on timber beams.",
        "Later: concrete houses in the same idiom; shop fronts in the ground floor; extra storeys.",
    ],
    grammar=dict(
        cell_m=[3.0, 3.0], storey_m=2.9, storeys=[2, 5],
        walls=dict(material="whitewashed stone and mud brick, battered (5-8 degrees); maroon-red (pembe-style "
                   "twig frieze) band under the parapet on important buildings", thickness_m=1.0,
                   palette=["#f1ede4", "#e5ddcd", "#7a2a24", "#2a2a2a", "#c9a33a", "#3d5f8f"],
                   weathering="whitewash poured from the roof leaves streaks; dust"),
        mass="Courtyard blocks (15-30 m) of 3-4 storeys facing a ring street round the temple; stepped back on the "
             "slope; a few great masses (a Potala-like palace up the hill).",
        streets=[
            dict(kind="kora (ring street)", width_m=8, notes="clockwise pilgrim circuit round the temple; stalls"),
            dict(kind="radial street", width_m=5, notes="from the kora outwards"),
            dict(kind="lane", width_m=2.5, notes="to courtyards"),
            dict(kind="courtyard gallery", width_m=1.5, notes="timber balconies round the court"),
        ],
        growth=[
            dict(layer="old", what="whitewashed courtyard houses, temples, chortens", materials=["stone", "mud brick", "timber", "arga"]),
            dict(layer="later", what="extra storeys, shopfronts, glazed sunrooms on roofs", materials=["concrete", "glass"]),
            dict(layer="cyberpunk", what="prayer flags of LED, mani walls of screens, lit window frames",
                 materials=["LED"]),
        ],
        openings="Trapezoidal black-painted window surrounds wider at the bottom; carved and painted timber lintels "
                 "in tiers; short pleated cloth valances (shambu) above windows and doors.",
        roofs="Flat, earth-packed, parapets; prayer-flag poles at the corners; gilded roof ornaments on temples.",
        ornament="Painted lintels (red, blue, green, gold), brass, the maroon frieze band.",
        public_spaces="The temple square and the kora; incense burners; a park with willows (lingka); on an island: "
                      "the kora as the large paved ring street, a temple square, a willow park with a pond.",
        water="A pond in a willow park; water carried in; snow.",
    ),
    foliage=[
        dict(species="willow (Salix)", form="pollarded rounded crowns", height_m=[5, 10], where="parks, lingka", colour="#7a9a4a"),
        dict(species="poplar (white poplar, ja-kar)", form="tall columnar", height_m=[10, 18], where="lanes, parks", colour="#9ab25a"),
        dict(species="potted marigolds and geraniums", form="pots on windowsills and roofs", height_m=[0.2, 0.5],
             where="window ledges, roof parapets", colour="#e88a2a / #c4304a"),
    ],
    cyberpunk=dict(
        elements=["LED prayer-flag strings in the five colours", "screens behind the black window frames",
                  "lit gold roof ornaments", "projected mantras on whitewash"],
        night="White walls glowing pale under the moon, gold temple roofs lit, strings of five-colour flags "
              "luminous, butter-lamp warmth inside windows."),
    kit=dict(
        shared=[
            dict(id="wall_panel_white", params="battered 5-8 deg, whitewash"),
            dict(id="window_small", params="with black trapezoid surround (new trim)"),
            dict(id="painted_motif", params="lintel tiers"),
            dict(id="terrace_parapet", params="flat roofs"),
            dict(id="lights_festoon", params="prayer flag strings, five colours"),
            dict(id="gallery_timber", params="courtyard galleries"),
        ],
        unique=["new: tibet_window_frame (the black trapezoid window surround + shambu valance)",
                "new: chorten (a stupa)", "new: flag_pole (prayer-flag pole on a roof corner)",
                "new: frieze_band (the maroon twig frieze under parapets)"],
        params=dict(proportions="squat massive, battered walls, small windows", rhythm="windows in regular rows, "
                    "growing larger with height", depth="deep reveals (walls 1 m)", colours="white, black, maroon, "
                    "gold, five-colour flags", materials="stone, mud brick, timber, whitewash"),
    ),
    street_hierarchy="kora ring 8 m > radial streets 5 m > lanes 2.5 m > courtyard galleries",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="japan_yokocho",
    name="Japanese backstreets: zakkyo towers, yokocho alleys and machiya (Tokyo, Osaka, Kyoto)",
    mark="Pencil-thin multi-tenant towers each with a vertical column of lit signboards, over alleys 1-2 m wide of "
         "tiny bars under red lanterns and noren curtains; wires overhead; machiya timber lattices at the low end.",
    sources=["Shinjuku Golden Gai (~250-280 bars, six alleys)", "Omoide Yokocho", "Osaka Ura-Namba / Dotonbori",
             "Kyoto machiya", "zakkyo buildings"],
    refs=[
        ("GO TOKYO: Shinjuku Golden Gai, around 280 bars", "https://www.gotokyo.org/en/spot/62/index.html"),
        ("Golden Gai: six alleys too narrow for a car, bars of five stools, flats above", "https://www.happyjappy.com/tokyo/shinjuku/golden-gai.html"),
        ("Japan Times: Emergent Tokyo (yokocho, zakkyo, how the city grows)", "https://japantimes.co.jp/culture/2022/06/09/books/emergent-tokyo"),
        ("The Creative Adventurer: Golden Gai", "https://thecreativeadventurer.com/golden-gai-tokyo/"),
    ],
    history=[
        "Edo-Meiji: machiya, deep narrow timber townhouses (5.5 m x 20-40 m) with lattice fronts and a courtyard garden.",
        "Post-war: black-market alleys of tiny 2-storey bars become yokocho; 1960s-80s zakkyo buildings: 5-10 storey "
        "thin concrete towers, one tenant per floor, each with a sign in a vertical column on the front.",
        "Pencil buildings on 3-5 m plots; external stairs; overhead wires on poles everywhere.",
    ],
    grammar=dict(
        cell_m=[3.5, 3.0], storey_m=3.0, storeys=[2, 10],
        walls=dict(material="tiled/rendered concrete (zakkyo), timber and plaster (machiya), corrugated sheet "
                   "(yokocho backs)", thickness_m=0.2,
                   palette=["#c9c4b8", "#8f8a80", "#5a4634", "#2c2c2c", "#d8cfbd", "#b23a2e"],
                   weathering="soot, rust on stairs, faded tiles"),
        mass="Blocks cut into very narrow plots; zakkyo towers 5-10 storeys on the street edges; inside the block "
             "low 2-storey yokocho clusters; machiya rows in the quiet streets.",
        streets=[
            dict(kind="shopping street (shotengai)", width_m=8, notes="arcade roof, banners"),
            dict(kind="side street", width_m=5, notes="zakkyo sign columns both sides, wires overhead"),
            dict(kind="yokocho alley", width_m=1.5, notes="bars both sides, red lanterns, noren"),
            dict(kind="roji (back path)", width_m=1.0, notes="potted plants, bicycles"),
        ],
        growth=[
            dict(layer="machiya", what="2-storey timber lattice townhouses", materials=["timber", "plaster", "tile"]),
            dict(layer="yokocho", what="2-storey bar shacks", materials=["timber", "corrugated"]),
            dict(layer="zakkyo", what="5-10 storey thin towers with sign columns and external stairs",
                 materials=["concrete", "tile", "steel"]),
            dict(layer="cyberpunk", what="giant 3D signs (a crab, a runner), video walls, vending machine rows, "
                 "dense overhead cable", materials=["LED", "acrylic"]),
        ],
        openings="Machiya: koshi timber lattices; zakkyo: aluminium windows, a stair door per floor; bars: sliding "
                 "doors with noren.",
        roofs="Machiya: grey kawara tile, low; zakkyo: flat with water tanks, AC units, a small rooftop shrine.",
        ornament="Signs, lanterns, noren, plastic flowers, rooftop torii.",
        public_spaces="A shrine with a precinct (torii, trees), small pocket parks, the shotengai; on an island: a "
                      "shrine forest and pond, a covered shopping arcade as the main street, a canal promenade.",
        water="Canals (Dotonbori), a shrine pond.",
    ),
    foliage=[
        dict(species="Japanese maple, pine (pruned)", form="sculpted", height_m=[2, 6], where="shrines, machiya gardens",
             colour="#a8322a / #2f5a2a"),
        dict(species="cherry (sakura)", form="spreading", height_m=[4, 8], where="canals, parks", colour="#f2c4d0"),
        dict(species="potted plants and bonsai", form="dense pot clusters at doors (roji gardens)", height_m=[0.2, 1.5],
             where="alley edges, doorsteps", colour="#4f7f3d"),
        dict(species="zelkova, ginkgo", form="street trees", height_m=[8, 15], where="avenues", colour="#d8b02a"),
    ],
    cyberpunk=dict(
        elements=["vertical sign columns on every zakkyo", "red paper lanterns and noren", "vending machines glowing",
                  "giant 3D figure signs", "overhead wire mesh", "video walls on corners"],
        night="Columns of lit signs climbing every building, alleys of red lantern glow, vending machine white light "
              "pools, black wire against a bright sky."),
    kit=dict(
        shared=[
            dict(id="sign_vertical_stack", params="a lightbox per floor, the whole height"),
            dict(id="lightbox_sign", params="stack members"),
            dict(id="lantern_paper", params="red chochin at bar doors"),
            dict(id="noren", params="bar doors"),
            dict(id="vending_machine", params="1-3 per block corner"),
            dict(id="stair_steel_external", params="zakkyo side stairs"),
            dict(id="wire_bundle", params="overhead between poles every 10 m"),
            dict(id="roof_shrine", params="1 in 5 roofs"),
            dict(id="screen_lattice", params="koshi timber lattice (machiya)"),
            dict(id="alley_bar", params="yokocho"),
            dict(id="sign_figure_3d", params="1-2 per island, on the main street"),
        ],
        unique=["new: utility_pole (concrete pole with transformer and wires)", "new: torii (a shrine gate)"],
        params=dict(proportions="very thin tall towers (3-5 m wide, 5-10 storeys); low bars", rhythm="each tower "
                    "different; sign columns regular", depth="signs 0.6-1 m out; lattices flush", colours="greys, "
                    "dark timber; saturated sign colours", materials="tile, concrete, timber, steel"),
    ),
    street_hierarchy="shotengai 8 m (covered) > side street 5 m > yokocho 1.5 m > roji 1 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="viet_tube",
    name="Vietnamese tube houses and hem (Hanoi Old Quarter, Saigon alleys, Hoi An)",
    mark="Facades only 3-5 m wide but 4-6 storeys tall and 20-60 m deep, every one a different colour and height "
         "like books on a shelf, balconies with plants, tangles of wires, and hem alleys threading behind.",
    sources=["Hanoi Old Quarter (the 36 guild streets)", "Ho Chi Minh City hem (~85% of residents live in alleys)",
             "Hoi An"],
    refs=[
        ("Local Vietnam: tube houses 2-4 m wide, up to 60-70 m deep, frontage taxes, inheritance", "https://localvietnam.com/culture/history/vietnamese-tube-houses/"),
        ("Hem (Wikipedia)", "https://en.wikipedia.org/wiki/H%E1%BA%BBm"),
        ("Saigon alley types: tricycle / car / tiny; 50-100 residents an alley", "https://vjol.vista.gov.vn/tcxd/en/article/view/59086"),
        ("Homage Project: the Vietnamese tube house", "https://www.homageproject.org/southeastasia/the-vietnamese-tube-house"),
        ("Hanoi 36 streets: Hang + the trade", "https://localvietnam.com/hanoi/hanoi-36-streets/"),
        ("Dennis Holloway: tube house", "https://dennisrhollowayarchitect.com/TubeHouse.html"),
        ("AIA: hem urban villages, community-driven urbanism", "https://www.aiainternational.org/online-lectures-calendar/2026/3/27/aia-oceania/-aia-southeast-asia-hm-urban-villages-in-ho-chi-minh-city-vietnam-a-model-for-community-driven-urbanism"),
    ],
    history=[
        "Old Quarter: guild streets (Hang Bac silver, Hang Ma paper...), timber-framed tube houses with courtyards.",
        "French era: brick and render fronts with shutters, balconies, pediments.",
        "1990s-: every family adds storeys on its own plot: 2 -> 4 -> 6 storeys, each a different colour; "
        "balconies, rooftop gardens and tanks.",
    ],
    grammar=dict(
        cell_m=[4.0, 3.5], storey_m=3.3, storeys=[2, 7],
        walls=dict(material="brick and concrete, rendered and painted in strong flat colours", thickness_m=0.22,
                   palette=["#e8c84a", "#7fb0a8", "#e8a07a", "#b9cfe0", "#f2eee4", "#9a4a3a", "#5a7f4a"],
                   weathering="mould streaks in the tropics, faded paint, peeling"),
        mass="Rows of 3-5 m wide plots of differing heights abutting; deep plots with 1-3 light-well courtyards; "
             "blank side walls (exposed when a neighbour is lower: painted ads on them).",
        streets=[
            dict(kind="guild street", width_m=8, notes="shops spill out, motorbikes parked on the pavement"),
            dict(kind="car hem", width_m=5, notes="alleys big enough for a car"),
            dict(kind="tricycle hem", width_m=3, notes="the usual alley"),
            dict(kind="tiny hem", width_m=1.5, notes="pedestrian, shrines, plants"),
        ],
        growth=[
            dict(layer="old", what="1-2 storey timber tube houses with tile roofs", materials=["timber", "tile"]),
            dict(layer="colonial", what="2-3 storey rendered fronts with shutters", materials=["brick", "render"]),
            dict(layer="growth", what="each plot grows 1-4 storeys at its own pace, colour by colour",
                 materials=["concrete", "paint", "steel balconies"]),
            dict(layer="cyberpunk", what="neon on every ground shop, LED on balconies, wire tangles thicken",
                 materials=["LED", "cable"]),
        ],
        openings="Full-height French doors with louvred shutters onto narrow balconies; roller shutters at ground.",
        roofs="Flat with rooftop gardens, tanks, a small shrine; old houses: tile roofs.",
        ornament="Painted pediments, balcony railings, Hoi An: yellow walls and silk lanterns.",
        public_spaces="Lake in the middle (Hoan Kiem), communal house (dinh), pagodas, night markets; on an island: "
                      "a central lake with a red bridge and a promenade, a market street, alley shrines.",
        water="A central lake; rain drains.",
    ),
    foliage=[
        dict(species="Dracontomelon (sấu), Khaya, banyan", form="big street trees", height_m=[12, 25], where="avenues, lake edge", colour="#3f6a35"),
        dict(species="bougainvillea", form="cascades from balconies", height_m=[1, 4], where="balconies", colour="#d8307a"),
        dict(species="potted plants, orchids, kumquats", form="rows of pots on balconies and roofs", height_m=[0.3, 1.5], where="balconies, roofs", colour="#4f7f3d"),
        dict(species="water lilies, lotus", form="pond", height_m=[0.2, 1], where="lake", colour="#5f9a3e"),
    ],
    cyberpunk=dict(
        elements=["wire tangles on every pole", "a neon sign per shop at street level", "LED balcony rails",
                  "silk lanterns (Hoi An) in LED"],
        night="Coloured slices lit at ground with neon, balconies with fairy lights, motorbike headlight rivers, a "
              "lake reflecting lantern bridges."),
    kit=dict(
        shared=[
            dict(id="wall_panel_render", params="3-5 m wide fronts, strong colours, each plot different"),
            dict(id="french_window", params="full-height with shutters"),
            dict(id="balcony_iron", params="narrow, every storey"),
            dict(id="shutters", params="louvred"),
            dict(id="shopfront_shutter", params="ground"),
            dict(id="wire_bundle", params="poles every 15 m"),
            dict(id="planter", params="balcony rows"),
            dict(id="lantern_cn", params="silk lanterns (Hoi An style)"),
            dict(id="water_tank", params="roofs"),
            dict(id="mural_wall", params="exposed party walls with painted ads"),
        ],
        unique=["new: party_wall_blank (the exposed side wall of a taller tube house)"],
        params=dict(proportions="extreme 1:4-1:6 width:height slices", rhythm="every 3-5 m a new colour and height",
                    depth="balconies 0.8 m", colours="saturated flat paints, each plot one colour", materials="render, steel, tile"),
    ),
    street_hierarchy="lake promenade 10 m > guild streets 8 m > car hem 5 m > tricycle hem 3 m > tiny hem 1.5 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="straits_shophouse",
    name="Straits shophouses (Penang, Malacca, Singapore)",
    mark="Arcaded rows of two-three storey shophouses with a continuous covered five-foot way, pastel stucco and "
         "Peranakan tiles, timber shutters and pintu pagar half-doors, Chinese temples and mosques side by side.",
    sources=["George Town, Penang", "Malacca Heeren St / Jonker", "Singapore Chinatown, Emerald Hill, Kampong Glam"],
    refs=[
        ("URA Singapore: understanding the shophouse (styles, roofs, Marseilles tiles)", "https://www.ura.gov.sg/Corporate/Guidelines/Conservation/Conservation-Guidelines/Part-1-Overview/Understanding-The-Shophouse"),
        ("Roots.gov.sg: Singapore shophouses (pintu pagar)", "https://www.roots.gov.sg/en/stories-landing/stories/singapore-shophouses/story"),
        ("Penang five-foot ways (1822 Raffles, 1887 ordinance)", "https://www.penang-traveltips.com/five-foot-ways.htm"),
        ("Zafigo: Penang shophouse styles", "https://zafigo.com/travel/zafigo-stories/20230216-penang-shophouse-styles/"),
        ("GTWHI: George Town shophouses", "https://gtwhi.com.my/?p=514"),
        ("Culturally: Peranakan shophouses", "https://www.culturally.co/blog/the-beauty-of-singapore-s-peranakan-shophouses"),
    ],
    history=[
        "Early (1790s-1850s): 1-2 storey plain, clay tiles, timber windows.",
        "Southern Chinese / Early Straits Eclectic (1840s-1900s): 2 storeys, carved timber, vents.",
        "Late Straits Eclectic (1900s-1940): 3 storeys, Peranakan tiles, pilasters, French windows, riot of colour.",
        "Art Deco (1930s-60s): geometric fronts, flagpoles, simpler.",
    ],
    grammar=dict(
        cell_m=[5.0, 3.5], storey_m=3.6, storeys=[2, 4],
        walls=dict(material="lime-plastered brick, painted pastels; glazed Peranakan tile dados; timber jack roofs",
                   thickness_m=0.3, palette=["#f2d7a8", "#a8d0c8", "#f0b8b0", "#c8d8a8", "#e8e2d4", "#4a6a8a", "#2f7a5a"],
                   weathering="mould on plaster, faded pastels, cracked tiles"),
        mass="Long terraces (40-100 m) of 5 m x 20-40 m shophouses back to back, with an air well halfway; a "
             "continuous covered walkway; temples and clan houses inserted.",
        streets=[
            dict(kind="main street", width_m=12, notes="two arcades facing"),
            dict(kind="five-foot way", width_m=1.8, notes="covered, tiled, continuous; public"),
            dict(kind="back lane", width_m=3, notes="service"),
            dict(kind="lorong", width_m=4, notes="side street"),
        ],
        growth=[
            dict(layer="early", what="low shophouses", materials=["brick", "clay tile", "timber"]),
            dict(layer="eclectic", what="3-storey ornate fronts", materials=["stucco", "tiles", "timber"]),
            dict(layer="overgrowth", what="rooftop additions, sheds over air wells, AC, signs", materials=["zinc", "aluminium"]),
            dict(layer="cyberpunk", what="neon calligraphy over the arcade, LED pilasters, hawker centre glow",
                 materials=["LED"]),
        ],
        openings="Pairs or triplets of full-height timber casements with louvres per upper bay; pintu pagar; "
                 "bat-motif vents.",
        roofs="Pitched clay (Marseilles) tile, gable firewalls between units; jack roofs.",
        ornament="Pilasters, Peranakan tiles, plaster festoons, Chinese name plaques, Malay timber fretwork.",
        public_spaces="Clan houses, temple squares, mosque courtyards, hawker centres; on an island: a hawker "
                      "square under rain trees, a temple court, a harbour/pond promenade.",
        water="The harbour edge, monsoon drains.",
    ),
    foliage=[
        dict(species="rain tree (Samanea saman)", form="huge umbrella", height_m=[15, 25], where="squares, avenues", colour="#3f6a35"),
        dict(species="frangipani (Plumeria)", form="small candelabra tree, white flowers", height_m=[3, 6], where="temples, courts", colour="#f2efe0"),
        dict(species="palms (coconut, areca)", form="palm", height_m=[5, 15], where="edges", colour="#5a8a3a"),
        dict(species="potted plants on the five-foot way", form="pots", height_m=[0.3, 1.5], where="arcades", colour="#4f7f3d"),
    ],
    cyberpunk=dict(
        elements=["neon calligraphy banners over the arcades", "LED-lit pilasters", "lit hawker stalls",
                  "projection on pastel fronts"],
        night="Arcades glowing like lantern tunnels, pastel fronts uplit, hawker centre steam and white strip light."),
    kit=dict(
        shared=[
            dict(id="arcade_pier", params="five-foot way piers every 5 m"),
            dict(id="french_window", params="timber casements with louvres, 2-3 per bay"),
            dict(id="tile_panel", params="Peranakan dados and pilaster panels"),
            dict(id="barrel_tile_eave", params="clay tile roofs"),
            dict(id="cornice", params="eclectic fronts"),
            dict(id="shutters", params="louvred"),
            dict(id="lantern_cn", params="arcade"),
            dict(id="painted_board", params="name plaques"),
        ],
        unique=["new: five_foot_way (the continuous covered arcade module)", "new: pintu_pagar (half-height swing doors)"],
        params=dict(proportions="5 m bays, 2-3 storeys, tall storeys 3.6 m", rhythm="perfectly regular bays",
                    depth="arcade 1.8 m deep", colours="pastels + tile colours", materials="plaster, tile, timber"),
    ),
    street_hierarchy="main street 12 m with arcades > lorong 4 m > back lane 3 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="siam_khlong",
    name="Bangkok: khlong canal life and Yaowarat (Thonburi, Chinatown)",
    mark="Teak houses on stilts with steep gabled roofs and curling finials lining canals of floating markets, and "
         "behind them a Chinatown of gold-shop neon over two-storey shophouses.",
    sources=["Thonburi khlongs", "Yaowarat Chinatown", "Talat Noi", "soi networks"],
    refs=[
        ("Soi-Lad morphological elements and urban transformation", "https://so05.tci-thaijo.org/index.php/sarasatr/article/view/253790"),
        ("From Klong Lat to Soi Lat: water-based to land-based Bangkok", "https://so04.tci-thaijo.org/index.php/NAJUA/article/view/244046"),
        ("Western-styled shophouses on Khlong Khu Mueang Doem", "https://so01.tci-thaijo.org/index.php/damrong/article/view/282766"),
        ("ArchDaily: rivers before roads, Southeast Asian waterway urbanism", "https://www.archdaily.com/es/1092399/rios-antes-que-carreteras-como-las-vias-fluviales-del-sudeste-asiatico-dieron-lugar-a-un-urbanismo-alternativo"),
        ("Hotels.com: the khlongs of Thonburi (stilted houses, teak homes, temples)", "https://www.hotels.com/go/thailand/thonburi-khlongs-bangkok"),
        ("PATA: Thonburi canal community award (Windsor House fretwork)", "https://www.tatnews.org/wp-content/uploads/2020/09/PATA-Gold-Awards-PDF-1.pdf"),
    ],
    history=[
        "Ayutthaya-Rattanakosin: settlements follow waterways; houses on stilts face the canals; temples (wat) "
        "on the banks; floating markets.",
        "Rama IV-VI: Sino-colonial shophouses along new roads (Yaowarat), 2-3 storeys.",
        "Later: concrete row-houses on sois, canals filled east of the river, kept in Thonburi.",
    ],
    grammar=dict(
        cell_m=[4.0, 4.0], storey_m=3.2, storeys=[1, 5],
        walls=dict(material="teak plank panels (stilt houses); stucco and concrete (shophouses)",
                   thickness_m=0.08, palette=["#6b4a2e", "#8a5f3a", "#e8d8b8", "#c8a040", "#2f6a8a", "#a8322a"],
                   weathering="silver-grey weathered teak, green water stains"),
        mass="Canal fronts of stilt houses 1-2 storeys on piles over the water, piers and steps; behind, rows of "
             "shophouses on sois; temples with tiered roofs.",
        streets=[
            dict(kind="main khlong", width_m=15, notes="boats, floating market"),
            dict(kind="road (Yaowarat)", width_m=14, notes="neon, gold shops"),
            dict(kind="soi", width_m=5, notes="market stalls"),
            dict(kind="canal walkway", width_m=1.5, notes="raised concrete/timber path along the houses"),
        ],
        growth=[
            dict(layer="stilt", what="teak houses on piles, piers, temples", materials=["teak", "piles", "tile"]),
            dict(layer="shophouse", what="Sino-colonial rows", materials=["stucco", "brick"]),
            dict(layer="overgrowth", what="tin extensions over water, rooftop sheds, wires", materials=["zinc", "concrete"]),
            dict(layer="cyberpunk", what="gold-shop neon, LED boats, screens", materials=["LED"]),
        ],
        openings="Wide timber panel windows hinged to swing out; shophouse shutters.",
        roofs="Steep (45 deg+) gable roofs with curling chofa finials on houses and tiered layered roofs with "
              "nagas on temples; shophouses flat or low tile.",
        ornament="Temple gold, mirror mosaics, naga finials; spirit houses on posts.",
        public_spaces="Temple courtyards, floating market basins, a riverside park; on an island: a canal ring with "
                      "a floating market basin, a temple plaza, a park with a pond.",
        water="Canals threading the island, a market basin.",
    ),
    foliage=[
        dict(species="banana, coconut palm", form="clumps and palms", height_m=[3, 15], where="canal banks", colour="#5f9a3e"),
        dict(species="bodhi tree (Ficus religiosa)", form="large, heart leaves, wrapped in coloured cloth", height_m=[10, 20], where="temples", colour="#3f6a35"),
        dict(species="lotus, water hyacinth", form="floating", height_m=[0, 1], where="canals, ponds", colour="#5f9a3e"),
        dict(species="potted bougainvillea, orchids", form="pots on piers", height_m=[0.5, 2], where="piers", colour="#d8307a"),
    ],
    cyberpunk=dict(
        elements=["gold-shop neon (red and gold characters)", "LED boats", "spirit houses lit", "screens on temples' edges"],
        night="Red and gold neon canyon of Yaowarat, canals of lanterns and boat lights, temples floodlit gold."),
    kit=dict(
        shared=[
            dict(id="water_channel", params="canals 8-15 m"),
            dict(id="plank_landing", params="piers and steps"),
            dict(id="sign_blade", params="gold-shop neon"),
            dict(id="eave_stack", params="temple tiered roofs"),
            dict(id="lantern", params="canal strings"),
            dict(id="shopfront_shutter", params="shophouses"),
        ],
        unique=["new: stilt_piles (a house platform on piles over water)", "new: steep_gable_finial (Thai roof with chofa)",
                "new: spirit_house (a shrine on a post)"],
        params=dict(proportions="low stilt houses, steep tall roofs", rhythm="houses with gaps along canals",
                    depth="piers 2-4 m out over water", colours="teak brown, gold, red", materials="teak, tile, stucco"),
    ),
    street_hierarchy="khlong 15 m / road 14 m > sois 5 m > canal walks 1.5 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="korean_hillside",
    name="Korean hillside villages: daldongne, Gamcheon and the rooftop room",
    mark="Terraced cubes of concrete stacked up a steep slope so every roof is a view, pastel boxes with blue and "
         "green flat roofs and water tanks, a rooftop room (oktapbang) on many, and long stairs with no streets.",
    sources=["Gamcheon Culture Village, Busan", "Seoul daldongne (Ihwa, Baeksa)", "oktapbang rooftop rooms"],
    refs=[
        ("Gamcheon: refugees' hillside terraces, every house with a view, 148-step 'Star Stairs'", "https://www.imperialtours.net/destinations/busan/gamcheon-village-2/"),
        ("Silversea: Gamcheon's colourful neighbourhood", "https://www.silversea.com/blog/destinations/asia/gamcheon-colorful-neighborhood"),
        ("U-Tokyo: charm of cities, Busan (Kim)", "https://www.www.urban.t.u-tokyo.ac.jp/charmofcities/Busan_Kim_eg.pdf"),
        ("JoongAng Daily: life in rooftop rooms (oktapbang)", "https://www.koreajoongangdaily.com/lifestyle/finding-happiness-and-great-views-on-the-roof/11809444"),
        ("Gamcheon guide", "https://guide-in-my-hand.expo.app/en/poi/gamcheon_village.html"),
    ],
    history=[
        "1950s: Korean War refugees build shacks of scrap wood, rocks and corrugated iron on steep hills.",
        "1970s-80s: rebuilt as 1-3 storey concrete-block and brick houses on the same terraces.",
        "2009-: artists paint them pastel; murals, sculptures; rooftop rooms and green-painted waterproofed roofs.",
    ],
    grammar=dict(
        cell_m=[5.0, 5.0], storey_m=2.8, storeys=[1, 4],
        walls=dict(material="concrete block and brick, rendered and painted", thickness_m=0.2,
                   palette=["#f2c8a8", "#a8d8e8", "#f8e8a0", "#c8e8b8", "#e8b8d0", "#6a9ad0", "#4a9a6a"],
                   weathering="peeling pastel, rust from railings"),
        mass="Rows of small cubic houses on narrow terraces following contours, each roof below the next row's "
             "street level; no gaps along a row; stair streets straight up the slope.",
        streets=[
            dict(kind="ridge road", width_m=7, notes="the one bus road along the top"),
            dict(kind="contour lane", width_m=2.5, notes="along each terrace"),
            dict(kind="stair", width_m=1.5, notes="straight up the slope, 50-150 steps, railings"),
        ],
        growth=[
            dict(layer="shacks", what="scrap huts", materials=["timber", "corrugated", "stone"]),
            dict(layer="houses", what="1-3 storey concrete cubes", materials=["concrete block", "brick"]),
            dict(layer="rooftop", what="oktapbang rooms, tanks, satellite dishes, chili drying, pot gardens",
                 materials=["panel", "plastic"]),
            dict(layer="cyberpunk", what="LED murals, neon crosses (churches), lit stairs", materials=["LED"]),
        ],
        openings="Aluminium sliding windows with security bars, small; metal doors.",
        roofs="Flat, painted green/blue waterproofing; blue/stainless water tanks; jangdok soy jars; laundry.",
        ornament="Murals, painted stairs, fish sculptures.",
        public_spaces="A viewpoint plaza at the top, a small market, a church, a pocket park; on an island: a "
                      "summit plaza and garden, a terraced park with a pond at the bottom.",
        water="Tanks; a pond at the foot.",
    ),
    foliage=[
        dict(species="persimmon trees", form="small, orange fruit in autumn", height_m=[3, 7], where="yards", colour="#e88a2a"),
        dict(species="pine (Korean red pine)", form="twisted", height_m=[6, 12], where="ridge", colour="#2f5a2a"),
        dict(species="potted peppers, lettuce in styrofoam boxes, jangdok jars", form="pots", height_m=[0.2, 1],
             where="rooftops", colour="#4f7f3d"),
        dict(species="cherry", form="spring blossom", height_m=[4, 8], where="stairs and lanes", colour="#f2c4d0"),
    ],
    cyberpunk=dict(
        elements=["red neon church crosses", "LED-lit stair risers", "screen murals", "lit rooftop rooms"],
        night="A hillside of tiny lit windows and red neon crosses, stair lights zigzagging up."),
    kit=dict(
        shared=[
            dict(id="box_module", params="5x5 m cubes, 2.8 m storeys"),
            dict(id="window_grille", params="every window"),
            dict(id="water_tank", params="blue, every roof"),
            dict(id="rooftop_shack", params="oktapbang on 30%"),
            dict(id="stair_cut", params="stair streets"),
            dict(id="mural_wall", params="painted walls"),
            dict(id="planter", params="styrofoam vegetable boxes"),
            dict(id="terrace_rail", params="roof edges"),
        ],
        unique=["new: jangdok_jars (clusters of earthenware jars)", "new: church_cross (neon cross on a pole)"],
        params=dict(proportions="small low cubes", rhythm="rows stepping up", depth="flat facades",
                    colours="pastels, green/blue roofs", materials="concrete block, paint"),
    ),
    street_hierarchy="ridge road 7 m > contour lanes 2.5 m > stairs 1.5 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="taipei_tiepi",
    name="Taipei alleys and the iron-sheet rooftop layer (tiepiwu)",
    mark="Four-to-six storey tiled walk-ups whose every window wears a steel cage and every roof a second house "
         "of corrugated iron sheet; arcaded ground floors (qilou) full of scooters and night-market stalls.",
    sources=["Taipei old districts (Wanhua, Datong)", "rooftop additions (頂樓加蓋)", "night markets"],
    refs=[
        ("Taiwan News: illegal rooftop additions (corrugated sheet walls and roofs)", "https://www.taiwannews.com.tw/en/news/4675723"),
        ("Taipei Times: clamping down on illegal structures, 20,000 households", "https://news.ltn.com.tw/news/focus/breakingnews/2264913"),
        ("Eyes on Place: Illegal Taipei", "https://eyesonplace.net/?p=6925"),
        ("Taiwan News: rooftop additions", "https://www.taiwannews.com.tw/news/6087795"),
    ],
    history=[
        "Japanese era and later: qilou arcaded shophouses (tingzijiao, covered walkways).",
        "1960s-80s: 4-6 storey apartment walk-ups clad in small ceramic tiles, iron window cages (tiechuang).",
        "1980s-: almost every roof gets an illegal corrugated iron-sheet addition; balconies enclosed; plants everywhere.",
    ],
    grammar=dict(
        cell_m=[5.0, 3.2], storey_m=3.2, storeys=[4, 7],
        walls=dict(material="concrete clad in small ceramic tiles (white, beige, pink, brown); iron-sheet rooftops "
                   "in blue/green/rust", thickness_m=0.2,
                   palette=["#e8e2d8", "#d8c8b0", "#c8a890", "#5a8aa8", "#4a8a6a", "#a85a3a"],
                   weathering="black streaks under cages, rust"),
        mass="Blocks of 4-6 storey walk-ups with arcaded ground floors, each topped by a 1-2 storey iron-sheet "
             "house; narrow alleys (xiang, nong) between.",
        streets=[
            dict(kind="road with qilou arcades", width_m=12, notes="scooters parked in the arcade"),
            dict(kind="lane (xiang)", width_m=6, notes=""),
            dict(kind="alley (nong)", width_m=3, notes="potted plants, scooters"),
            dict(kind="night market street", width_m=8, notes="stalls down the middle"),
        ],
        growth=[
            dict(layer="arcades", what="qilou shophouses", materials=["brick", "concrete"]),
            dict(layer="walk-ups", what="tiled 4-6 storeys with iron cages", materials=["tile", "iron"]),
            dict(layer="rooftop", what="iron-sheet houses on every roof, water tanks, gardens", materials=["corrugated iron"]),
            dict(layer="cyberpunk", what="night-market LED, temple neon, convenience-store white", materials=["LED"]),
        ],
        openings="Aluminium windows behind projecting iron cages full of plants and laundry.",
        roofs="Flat concrete with iron-sheet structures and stainless water towers.",
        ornament="Temple roofs (dragons, cut porcelain), signs.",
        public_spaces="A temple square with a night market, a small park; on an island: a temple plaza night "
                      "market, a pond park, an arcaded main road.",
        water="Tanks; a pond.",
    ),
    foliage=[
        dict(species="potted plants in window cages", form="dense green in every cage", height_m=[0.3, 1.5], where="cages", colour="#4f7f3d"),
        dict(species="banyan (Ficus microcarpa)", form="spreading", height_m=[8, 15], where="temple squares", colour="#3e6a35"),
        dict(species="Formosan sweetgum, camphor", form="street trees", height_m=[8, 15], where="roads", colour="#456f38"),
    ],
    cyberpunk=dict(
        elements=["night-market LED and steam", "convenience-store white light", "temple neon and dragon roofs",
                  "lit iron-sheet rooftops"],
        night="Warm cage-lit windows, a white-and-red night market, temple roofs glowing."),
    kit=dict(
        shared=[
            dict(id="window_grille", params="projecting iron cages 0.4 m on every window"),
            dict(id="corrugated_panel", params="rooftop houses"),
            dict(id="rooftop_shack", params="on 80% of roofs"),
            dict(id="arcade_pier", params="qilou"),
            dict(id="water_tank", params="stainless towers"),
            dict(id="market_stall", params="night market"),
            dict(id="planter", params="in cages"),
        ],
        unique=["new: tile_cladding (small ceramic tile wall texture panel)", "new: temple_roof_dragon (ridge dragons)"],
        params=dict(proportions="4-6 storey slabs with a light rooftop house", rhythm="regular", depth="cages 0.4 m",
                    colours="tile beige/pink, iron-sheet blue/green/rust", materials="tile, iron sheet"),
    ),
    street_hierarchy="arcaded road 12 m > night-market street 8 m > lane 6 m > alley 3 m",
)

# ---------------------------------------------------------------------------------------------------------------
fam(
    id="manila_estero",
    name="Manila: Binondo and the estero settlements (Tondo)",
    mark="Stone ground floors with timber upper storeys overhanging the street, capiz-shell sliding windows and "
         "ventanillas, Chinese arches of Binondo -- and beyond them dense stilt shanties of scrap over the esteros, "
         "jeepney colours everywhere.",
    sources=["Binondo (Chinatown)", "Intramuros / Vigan bahay na bato", "Tondo informal settlements", "esteros"],
    refs=[
        ("Bahay na bato (Wikipedia): stone ground floor, overhanging timber upper floor, capiz windows", "https://en.wikipedia.org/wiki/Bahay_na_bato"),
        ("Ventanilla (Wikipedia)", "https://en.wikipedia.org/wiki/Ventanilla_(Philippine_architecture)"),
        ("Lean Urbanism: bahay kubo and bahay na bato", "https://leanurbanism.org/lean-interpretations-from-philippine-vernacular-architecture/"),
        ("Slums in Metro Manila (Wikipedia)", "https://en.wikipedia.org/wiki/Slums_in_Metro_Manila"),
        ("Waterloo thesis: Manila's Other City (Barangay 105, warehouses turned live-work)", "https://uwspace.uwaterloo.ca/items/b5cb3528-20de-42bc-8c96-696885ffd36a/full"),
        ("The Guidon: situating slums", "https://theguidon.com/2024/10/situating-slums/"),
    ],
    history=[
        "Bahay kubo (stilt hut of bamboo and nipa) -> bahay na bato (stone below, timber above, capiz windows).",
        "Binondo: Chinese merchants' shophouses with arches, estero canals, a church plaza.",
        "20th c.: informal settlements of salvaged wood, plywood and galvanized iron on stilts along the esteros; "
        "jeepneys painted chrome and colour.",
    ],
    grammar=dict(
        cell_m=[4.0, 3.5], storey_m=3.0, storeys=[2, 4],
        walls=dict(material="adobe/stone ground floor, timber upper floor; shanties of plywood and galvanized iron",
                   thickness_m=0.4, palette=["#b8a48a", "#6b4a2e", "#e8e0c8", "#9a9a90", "#d84a2a", "#2a7ab8", "#e8c040"],
                   weathering="moss on stone, rust on GI sheets"),
        mass="Old core of 2-3 storey bahay na bato blocks round a church plaza with arcaded Chinese shophouses; "
             "edges of dense stilt shanties along canals, 1-3 storeys, packed.",
        streets=[
            dict(kind="plaza street", width_m=12, notes="jeepneys"),
            dict(kind="calle", width_m=7, notes="overhanging upper floors"),
            dict(kind="eskinita (alley)", width_m=1.2, notes="through the shanties, planks over water"),
            dict(kind="estero (canal)", width_m=8, notes="stilt houses on both banks"),
        ],
        growth=[
            dict(layer="stone and timber", what="bahay na bato and shophouses", materials=["adobe", "timber", "capiz"]),
            dict(layer="shanties", what="stilt shacks over the esteros", materials=["plywood", "GI sheet", "bamboo"]),
            dict(layer="overgrowth", what="extra storeys of GI, bridges, wires", materials=["GI", "cable"]),
            dict(layer="cyberpunk", what="jeepney-chrome LED, karaoke neon, sari-sari shop signs", materials=["LED"]),
        ],
        openings="Capiz-shell sliding window panels, ventanillas with balusters below, wide eaves.",
        roofs="Hipped tile or GI roofs with deep eaves; shanties flat GI held with tyres and stones.",
        ornament="Chinese arches (Binondo), church baroque, jeepney art.",
        public_spaces="Church plaza, a market, basketball courts everywhere; on an island: a plaza with a church/"
                      "temple, a basketball court in every quarter, a canal promenade, a mangrove pond.",
        water="Esteros; a mangrove pond.",
    ),
    foliage=[
        dict(species="acacia / narra / mango", form="big shade trees", height_m=[10, 20], where="plaza", colour="#3f6a35"),
        dict(species="banana, coconut", form="clumps, palms", height_m=[3, 15], where="yards", colour="#5f9a3e"),
        dict(species="bougainvillea, sampaguita in pots", form="pots", height_m=[0.5, 3], where="windows", colour="#d8307a"),
        dict(species="mangrove (Rhizophora)", form="stilt-rooted", height_m=[2, 6], where="estero edges", colour="#3e6a35"),
    ],
    cyberpunk=dict(
        elements=["karaoke neon", "jeepney chrome and LED", "sari-sari store signs", "Christmas parol star lanterns"],
        night="Capiz windows glowing amber, parol stars everywhere, neon over the shanties, canal reflections."),
    kit=dict(
        shared=[
            dict(id="balcony_timber_covered", params="overhanging upper floor, 0.8 m"),
            dict(id="shutters", params="capiz sliding panels (new variant)"),
            dict(id="corrugated_panel", params="GI shanties"),
            dict(id="plank_bridge", params="over esteros"),
            dict(id="arch_opening", params="Binondo shophouses"),
            dict(id="lantern_star", params="parol stars"),
            dict(id="water_channel", params="esteros"),
        ],
        unique=["new: capiz_window (sliding panels of translucent shell squares)", "new: ventanilla (baluster panel "
                "below a window)", "new: basketball_court"],
        params=dict(proportions="2-3 storey, upper floor wider than lower", rhythm="regular capiz bays",
                    depth="overhang 0.8 m", colours="stone, timber, jeepney brights", materials="adobe, timber, GI"),
    ),
    street_hierarchy="plaza street 12 m > calles 7 m > esteros 8 m > eskinitas 1.2 m",
)


# ---------------------------------------------------------------------------------------------------------------
def md(f):
    g = f["grammar"]
    L = [f"# {f['name']}", "", f"**Mark:** {f['mark']}", "", "Sources: " + "; ".join(f["sources"]), "",
         "## Examples and references"]
    for t, u in f["refs"]:
        L.append(f"- [{t}]({u})")
    L += ["", "## How it grew"] + [f"- {h}" for h in f["history"]]
    L += ["", "## Generator grammar",
          f"- **Cell:** {g['cell_m'][0]} x {g['cell_m'][1]} m; storey {g['storey_m']} m; {g['storeys'][0]}-{g['storeys'][1]} storeys.",
          f"- **Walls:** {g['walls']['material']}; {g['walls']['thickness_m']} m thick; palette "
          f"{', '.join(g['walls']['palette'])}; weathering: {g['walls']['weathering']}.",
          f"- **Mass:** {g['mass']}",
          "- **Streets:**"]
    for s in g["streets"]:
        w = f"{s['width_m']} m" if s["width_m"] else "-"
        L.append(f"  - {s['kind']}: {w}" + (f" ({s['notes']})" if s.get("notes") else ""))
    L.append("- **Growth, in layers:**")
    for y in g["growth"]:
        L.append(f"  - {y['layer']}: {y['what']} [{', '.join(y['materials'])}]")
    L += [f"- **Openings:** {g['openings']}", f"- **Roofs:** {g['roofs']}", f"- **Ornament:** {g['ornament']}",
          f"- **Public spaces:** {g['public_spaces']}", f"- **Water:** {g['water']}",
          f"- **Street hierarchy:** {f['street_hierarchy']}", "", "## Foliage"]
    for p in f["foliage"]:
        L.append(f"- {p['species']}: {p['form']}, {p['height_m'][0]}-{p['height_m'][1]} m, {p['where']} ({p['colour']})")
    c = f["cyberpunk"]
    L += ["", "## Cyberpunk overlay"] + [f"- {e}" for e in c["elements"]] + [f"- **Night:** {c['night']}"]
    k = f["kit"]
    L += ["", "## Kit", "Shared pieces:"] + [f"- `{s['id']}`: {s['params']}" for s in k["shared"]]
    L += ["", "Pieces unique to this family:"] + [f"- {u}" for u in k["unique"]]
    L += ["", "Parameters that make the common pieces read as this civilization:"]
    L += [f"- {a}: {b}" for a, b in k["params"].items()]
    return "\n".join(L) + "\n"


def main():
    for f in F:
        with open(os.path.join(HERE, f"r2_{f['id']}.md"), "w") as fh:
            fh.write(md(f))
    with open(os.path.join(HERE, "r2_grammars.json"), "w") as fh:
        json.dump({"stream": "r2 (East and Southeast Asia)", "version": 1, "date": "2026-10-15",
                   "count": len(F), "families": F}, fh, indent=1, ensure_ascii=False)
    print(f"{len(F)} families:", ", ".join(f["id"] for f in F))


if __name__ == "__main__":
    main()
