# Chongqing: the mountain city (diaojiaolou stilt houses, Hongyadong, Shibati)

**Mark:** A city poured down a cliff: stilted timber houses on tall poles, streets that enter a building at its 11th floor and leave at its 1st, stairs instead of streets, monorails through buildings, mist.

Sources: Chongqing Yuzhong peninsula; Hongyadong (11-13 storey stilt complex on a cliff); Shibati old town; Ciqikou; Liziba (monorail through a 19-storey block)

## Examples and references
- [Hongya Cave (Wikipedia): a stilt-house complex on the cliff above the Jialing](https://en.wikipedia.org/wiki/Hongya_Cave)
- [Chongqing gov't: Hongyadong, 13-storey stilt cluster](https://english.cq.gov.cn/specials/explore/PhotoPerfectSpots/202608/t20260810_15912600.html)
- [travelchina: enter on the 11th floor at Cangbai Rd, leave at Jiabin Rd](https://www.travelchina.org.cn/en/article/NQ0zLwVYgSwN)
- [Liziba station (Wikipedia): the monorail stops inside a 19-storey residential building](https://en.wikipedia.org/wiki/Liziba_station)
- [Asia Times: monorail runs through residential blocks](https://asiatimes.com/2018/04/monorail-chinas-chongqing-runs-residential-blocks/)
- [Chinavigators: Chongqing at night (neon, cable cars)](https://www.chinavigators.com/chongqing-at-night/)
- [Hongyadong night view](https://chinafortravelers.com/guides/hongyadong-night-view/)

## How it grew
- Diaojiaolou: Tujia/Ba stilt houses -- timber frames on tall wooden poles where the slope drops, the back resting on rock, the front on stilts 3-10 m high; galleries and hanging balconies.
- Dense riverside quarters of stilt houses until 1949; staircases (Shibati: 'eighteen steps') as streets.
- 1990s-2010s: concrete towers built down the same slopes, with entrances at many levels and skybridges from streets above into upper floors; Hongyadong rebuilt (2006) as an 11-storey stilt-style complex.

## Generator grammar
- **Cell:** 4.0 x 4.0 m; storey 3.2 m; 3-13 storeys.
- **Walls:** dark timber frame with plank/lath infill and grey brick; later concrete with timber cladding; 0.15 m thick; palette #4a3324, #6b4a32, #8a8a84, #3b3b38, #c9a35a, #a8322a; weathering: dark wet timber, moss in the mist, soot.
- **Mass:** Terraces stepping down the slope; each terrace's buildings stand on stilts on the downhill side; buildings span several terraces (an upper-street door and a lower-street door); towers on the ridge.
- **Streets:**
  - ridge road: 12 m (on top; buildings entered at their top floors)
  - contour street: 5 m (along the slope, shop-lined)
  - stair street: 3 m (straight down the slope, landings, 150-300 steps)
  - sky-bridge: 2.5 m (from a street into a building's upper floor)
  - stilt underdeck: - (spaces beneath the stilts: workshops, stalls)
- **Growth, in layers:**
  - stilt village: 2-4 storey diaojiaolou on poles, tile roofs, galleries [fir timber, bamboo, grey tile, stone footings]
  - brick and concrete: 5-9 storey blocks on the terraces, stairs everywhere [grey brick, concrete]
  - vertical: towers to 30+ storeys on the ridge, skybridges, a monorail through a block [concrete, glass]
  - cyberpunk: golden outline lighting on every eave, LED-lit stairs, cable cars, screens on tower crowns [LED, steel cable]
- **Openings:** Timber lattice windows, sliding panels; wide galleries with timber railings on every storey.
- **Roofs:** Grey tile, shallow pitch, upturned eave corners (flying eaves), stacked tier on tier down the slope.
- **Ornament:** Red lanterns, carved railings, brackets; gold edge lighting at night.
- **Public spaces:** Landings on the stair streets (tea houses), a riverside promenade at the bottom, temple terraces; on an island: a broad ridge boulevard, terraced gardens, a pond at the bottom terrace.
- **Water:** The river at the foot; mist; rain runoff down the stairs.
- **Street hierarchy:** ridge boulevard 12 m > contour streets 5 m > stair streets 3 m > skybridges 2.5 m

## Foliage
- Ficus virens / banyan: huge crowns over landings, 8-16 m, stair landings, terraces (#456f38)
- Cinnamomum camphora (camphor): broad dense crown, 8-15 m, ridge roads (#3f6232)
- bamboo groves: clumps, 4-9 m, steep gaps between terraces (#6d9a46)
- Chongqing ivy and moss: wall cover, 0-0 m, retaining walls (#4f7a3a)

## Cyberpunk overlay
- every eave traced in warm gold LED
- monorail tube through a tower
- cable car lines across
- screens on ridge tower crowns
- lit stair streets
- **Night:** A golden mountain of outlined eaves stacked down the cliff, reflected in water; towers above with colour-changing crowns; mist catching beams.

## Kit
Shared pieces:
- `gallery_timber`: every storey, 1.2 m deep, timber rails
- `timber_eave`: flying corners, 1 m overhang
- `eave_stack`: tiers stacked down the slope
- `stair_external_steep`: stair streets 3 m wide
- `skybridge`: street to upper floors
- `lantern_cn`: red, under eaves
- `eave_bulbs`: gold outline on every eave
- `screen_lattice`: timber lattice windows
- `cantilever_beam`: stilt/beam ends

Pieces unique to this family:
- new: stilt_frame (a timber pole frame 3-10 m tall carrying a building's downhill side)
- new: hanging_balcony (diaojiaolou cantilevered gallery with a skirt)
- new: monorail_beam (a concrete track beam on piers, can pass through a block)

Parameters that make the common pieces read as this civilization:
- proportions: buildings span several terraces; storeys 3.2 m; stilts 3-10 m
- rhythm: tiered eaves every storey
- depth: galleries 1.2 m, eaves 1 m
- colours: dark timber, grey tile, red lanterns, gold light
- materials: timber, tile, brick, concrete
