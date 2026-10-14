# Floor plans as generator data (stream A)

Units are metres. "Grid" is the structural bay. "Core" is the stair, or stair plus lift-shaft-free well (no lifts:
the Floor's tech; stairs and hoists). Every plan ends at a **roof access** (the canon: every building has one).
Rooms list what the room manifests should get (research/lives/07_occupancy.md).

## A-P1 Tower house (Sana'a / Shibam / Jeddah) — `tower_house`
```
footprint: 9 x 10 (Shibam 90 m2) .. 12 x 14 (Sana'a merchant); storey 3.2; storeys 5-9
core: one stair, 1.2 wide, against the back wall (quarter-turn, wraps the core); thick walls taper 0.5 -> 0.3
floors:
  0: store + workshop (shop front on the lane side, 1-2 bays 3 m)        # Shibam: blind; sky version: shop
  1: store / stable for goats & fowl (the canon's livestock) + water jars
  2: diwan (reception, the whole front) + guest wc
  3: family hall + kitchen (kitchen at the TOP of the family floors in Sana'a: smoke)
  4..n-1: bedrooms 2-3 per floor (3.5 x 4) + bath
  n: mafraj (whole floor, windows 3 sides, low sills 0.4) -> roof terrace (parapet 1.2, crenellated) + rooftop stair head
openings: column of windows per facade bay (bay 2.4-3 m), each = rect light 0.8x1.2 + qamariya fanlight r 0.4
          roshan_bay stacked on floors 2..n (Jeddah variant), takhrima box on 1-2 floors (Sana'a)
bridges: from floor 4-6 to a neighbouring tower (Shibam), 1.5 wide, roofed
```

## A-P2 Riad / dar (Fez, Marrakesh) — `courtyard`
```
footprint: 14 x 14 .. 22 x 22; storeys 2-3 (Fez up to 4); storey 3.6 ground, 3.2 above
court: centred, 6x6 .. 10x12, open to sky; riad = 4 beds + fountain at cross; dar = paved + wall fountain
gallery: 1.6-2.4 deep round the court on every floor, arcaded (piers at court corners: 1 or 3 per corner)
rooms: on 2-4 sides, long & shallow (3.0 deep x court-side length), each with 2 tall double doors (1.2x3.2) on the court
entry: BENT: street door -> 2 m vestibule -> 90 deg turn -> gallery (no line of sight)
roof: terrace on all sides of the court opening, menzeh (3x3 belvedere) on one corner, stair head
shops: none inside (the street front is blank but for the door) -> in the sky version the street face gets a strip
       of 2.5 m-deep shop bays (the "funduq" ring: see A-P3)
```

## A-P3 Wikala / funduq / khan + rab' (Cairo) — `market_court`
```
footprint: 24 x 30 .. 40 x 50; storeys 4-6; storey 3.5 (stores) / 3.0 (flats)
court: 10x16 .. 18x24, paved, with a central kiosk/fountain (sabil)
floors 0-1: shops/stores 3 x 5 bays all round the court behind a 2-storey arcade (pier spacing 3.0)
floors 2-4(5): rab' = DUPLEX/TRIPLEX flats, each 1 bay wide x 2-3 storeys (living below, sleeping above, own stair),
               opening on a gallery facing the court; ~1 flat per 3 m of court perimeter per level
gate: one monumental portal (pishtaq / muqarnas hood) on the street side, 4 m wide, 8 m tall
roof: terrace + laundry + pigeon lofts; a rooftop sign mast over the gate
```

## A-P4 Haveli (Delhi) — `haveli`
```
footprint: 16 x 20 .. 28 x 36; storeys 2-4; storey 3.4
entry: darwaza (carved gate 3 x 4.5) -> deorhi (vestibule 3 x 4) -> outer court (mardana)
courts: outer 8x8 (men, business), inner 8x10 (zenana, family); 1.5 m verandas (dalan) with cusped-arch colonnades
rooms: around each court, 3.5-4.5 deep
street face: ground = 4-8 shop bays 3 m wide (the modern haveli), upper floors = jharokhas every bay on brackets,
             chhajja over every storey (0.8 deep), jali parapet
roof: terrace with chhatris at corners (one = stair head), kite-flying deck, water tank
```

## A-P5 Chawl (Mumbai) — `gallery_block`
```
footprint: long slab 6.5-9 deep x 30-60 long; storeys 3-5; storey 3.0
bay: 3.0 wide (one room 3.0 x 5.0 + 1.0 nahani wash corner) ; 20 rooms per floor in a 60 m block
gallery: 1.8 deep along one long side (single-loaded) or 2.0 central corridor (double-loaded, BDD)
cores: stair at each end + one mid; shared wc block at each end (2-4 cubicles)
ground: shops in the street-facing bays (3 m each)
roof: terrace (washing lines, terrace parties, kite deck), water tanks on the core tops
night: one door lamp per room + paper lanterns along the gallery rail
```

## A-P6 Tool-house stack (Dharavi) — `warren_stack`
```
plot: 3.5 x 6 .. 6 x 9 (tiny); built G+1..G+4 over time; storey 2.7 (low!)
0: workshop / shop, open front with rolling shutter
1..n: dwelling 1 room + kitchen corner; each level may cantilever 0.3-0.6 over the lane on one side
stairs: external mild-steel stair bolted on per level, position random (front / side), 0.8 wide, ladder-steep at top
roofs: corrugated/tarp sheds, water drums, antennas, pigeon coop
variation rule: every storey re-rolls material + colour + window type (see styles_a.json "dharavi_stack")
```

## A-P7 Two-level town (Ghadames) — `roof_street`
```
grid of 6x8 .. 8x10 houses, terraced (shared party walls), storeys 2-3
ground: covered alleys (sabat) 2-3 wide running UNDER the houses, light shafts every 15-20 m
roofs: all terraces joined; low parapet walls 0.6 with stepped crenels; small bridges over the light shafts;
       stair heads every house; this IS the main street of the island (the lark cradles, the gardens, the markets)
```

## A-P8 Chamfered block (Barcelona Eixample) — `chamfer_block`
```
block: square 40..60 m on the island scale (not 113 - islands are small), 45-degree chamfers 6-10 m
ring building: 12-15 deep, storeys 5-7, storey 3.0 (principal floor 3.6)
inner court: garden/pond (the canon's ponds!) with galeria facades (glazed enclosed balconies) facing in
street face: iron balcony every opening every floor (1.2 x 0.6), shops on the ground floor, a corner shop on each chamfer
cores: 2-4 stair cores, each with a central lightwell 3x3
```

## A-P9 Hanging house (Cuenca) — `rim_hanger`
```
sits on the island edge: back 2/3 on the deck, front 1/3 cantilevered past the fence over the drop
storeys 3-4, storey 3.0; masonry base on the deck side, timber upper storeys
balconies: full-width timber galleries on the cantilevered face, 1.0-1.2 deep, on 2-3 levels, timber brackets
safety: the balcony rails are the island fence here (1.4 m, close-boarded)
```
