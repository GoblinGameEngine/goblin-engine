# Stream C plans: stacked warrens as generator data (Europe, South America, Canada)

All dimensions are in metres. `st` is the storey height. **(est.)** values are working values. Each plan names the style
ids in styles_c.json that use it. Coordinates: x is along the frontage, y is depth into the lot, and z is up.

## C-P1 the Edinburgh land (tall slab on a slope) -- `closes_lands`
```
lot:        frontage 7-9, depth 18-22; lands shoulder to shoulder in a row; a CLOSE (1.2-2.0 wide, steps every 4-8 m
            down the slope) between every 1-3 lands, a PEND (2.4 high, rooms above) where a close goes under a land
storeys:    front 6-8 at the path; back +2..+5 more down the slope (the same floors, the ground falls); st 2.8 (ground 3.6)
ground:     arcade 2.5 deep behind the front piers (shops in the back of the arcade); a basso/booth in each bay
stair:      TURNPIKE: a round tower 3.0 dia on the close side, door from the close; landings serve 2-4 flats per floor
            (2 for the rich, 4-6 'single ends' 3.5 x 4.5 for the poor)
upper:      front room | rear room per flat, timber GALLERY 1.2 deep cantilevered from floors 2-4 on the street side
top:        2 gable floors in a crow-stepped gable, an altana or roof walk between chimney stacks; hoist at the gable
signs:      name board + lamp at every close mouth; blade signs on iron brackets from the arcade piers
```

## C-P2 the jettied stack -- `jetty_lanes`, `bridge_street`
```
lot:        frontage 5-8, depth 8-14; rows on both sides of a 2.5-3.5 lane
storeys:    3-5 timber over a stone ground floor; st 2.6 (ground 3.2)
jetty:      each upper floor projects 0.4-0.6 on the lane side (and on a corner lot, both sides via a dragon beam);
            bressummer 0.25 x 0.3 at each jetty line; curved brackets under the corner posts
            -> at floor 4 the facade is 1.6-2.4 out over the lane: opposite eaves 0.3-0.8 apart
roof:       55 deg, ridge parallel to the lane (or gable to the lane: hoist door + beam in the gable), 2 rows of
            dormers; an altana deck between two roofs for roof access
inside:     one room front + one back per floor, stair (winder) in the back corner 0.8 wide
signs:      wrought-iron bracket blade sign at floor 1; lantern under the jetty
```

## C-P3 the bridge street (houses on a span) -- `bridge_street`
```
span:       between two lobes (or two lashed islands, permanent only on big islands): 40-125 long, carriage way 4-6
houses:     3-storey, 4-6 frontage, 6-8 deep, both sides; their back thirds (retrobotteghe) hang off the span on
            timber brackets 0.6 deep at 1.2 centres; a covered corridor (2.4 wide) on one row's roofline (Vasari)
middle:     a gate-house spanning the street (Nonsuch: 4 storeys, onion-domed corner turrets)
signs:      every shop: blade sign + lightbox over the counter; bulb strings across the street every 6 m
```

## C-P4 the terrace stack (roofs are streets) -- `sassi_terraces`, `vault_cells`
```
slope:      the deck's rolling hill or the rim rock; terraces every 3.5-4.5 vertical
level k:    a row of cells cut/built into the slope: cell 4-6 wide x 6-12 deep (cave part behind), vaulted facade
            (barrel vault rise 1.0-1.5); the strip in front (2-3 deep) is the ROOF of level k-1 = the path of level k
stairs:     zig-zag stairs 1.2 wide between terraces every 20-30 m along the row; parapet 1.0 at each path edge
upper:      some cells get a built storey on top (a box 4 x 5) reached from the next path up
under-rim:  (sky island special) 1-2 levels of cells cut into the rock FLANK below the deck edge, windows out over the
            void, reached by a stair down from the promenade through a gate in the fence
signs:      painted boards beside doors; a lamp per door; luminarie (bulb arches) over each stair
```

## C-P5 the canal/gable house with hoist -- `hoist_gables`
```
lot:        frontage 5.1-7.3 (18-26 Amsterdam ft), depth 15-20 (voorhuis 10-12, court 3-4, achterhuis 4-6)
storeys:    ground 3.6-4.0 (shop), 3-4 uppers st 2.9, attic + loft in the gable (2 levels)
facade:     3 bays, tall windows; leans OUT 1:25-1:50 so hoisted loads clear it
gable:      step | neck | bell | cornice (pick per house), 4-6 above the eaves line
hoist:      HOIST_BEAM from the top gable, 1.2-1.5 out, hook + pulley; a loading door per floor under it
stair:      steep (55-60 deg) straight stair along a party wall, 0.7 wide -> the reason goods go up outside
roof:       ridge perpendicular to the street; altana or a roof hatch behind the gable for roof access
signs:      a lit sign in the ground-floor window; gilt lettering on the gable; bulb strings outline the gables
```

## C-P6 the gård (wharf row) -- `gard_wharf`
```
gard:       two parallel timber rows 6-8 deep, 30-60 long, facing each other across a plank passage 2.5-4 wide that runs
            perpendicular to a dock face / the rim; gable ends to the edge
storeys:    2-3, st 2.7; ground: storerooms; upper: rooms and offices off EXTERNAL GALLERIES on the passage side
links:      plank bridges across the passage at each upper floor every 8-12 (goods move floor to floor across)
edge:       at the rim end, each row's gable carries a CRANE / hoist over the void (the island's cargo hoists)
hall:       a schotstue (assembly hall, single storey, long table) at the inland end
signs:      painted merchant marks on the gables, lanterns along the galleries
```

## C-P7 the plex row with outside stairs -- `plex_spirals`
```
lot:        frontage 7.5 (single) or 14-15 (double), depth 26-29; setback 3.0 from the path
storeys:    3 (triplex) or 2 (duplex) + flat roof; st 3.0; one flat per floor (two on a double lot)
stairs:     OUTSIDE in the setback: SPIRAL (dia 1.6) on narrow lots, straight/L/S on wide; to a GALLERY 1.5 deep on
            floors 2-3 (each upper flat's own front door); and on the sky islands the stair goes on up to the roof
flat:       long plan: front double parlour | corridor along one party wall | bedrooms | kitchen at the back
roof:       flat, cornice 0.6 on brackets; a rooftop terrace with rail
signs:      a corner depanneur (shop) at each block end with a lightbox + neon in the window; bulb strings on the galleries
```

## C-P8 the box pile (Habitat) -- `box_pile`
```
module:     one box 11.7 x 5.3 x 3.0 (shared part), door + glazed end + roof terrace rail
pile:       12 levels max; each level's boxes offset 1/2-1 box from the level below (both axes) so every box's roof is
            the terrace of the one above-and-beside; units of 1-4 boxes (L, Z, bar)
streets:    an open pedestrian street through the pile every 4 levels (2.5 wide, covered by the boxes above); lift/stair
            cores every 30-40 m
roofs:      terrace gardens, glass-domed sunrooms (half-sphere skylight), balloon tether anchors on the top boxes
signs:      sparse in the pile; a lit band at each pedestrian street; shops at the base street
```

## C-P9 the laje stack (favela) -- `laje_stack`
```
lot:        4-6 x 6-10, packed edge to edge on a slope; becos 1.0-2.0 between, stairs where steep
growth:     storey 1 = full lot; each further storey (2..6) = the slab above, +0..1.0 cantilever over the beco, sometimes
            a smaller box leaving a terrace; colour per storey (different owners)
frame:      concrete columns 0.25 at corners showing; brick infill; rebar stubs 0.6 sticking up from the top slab
stair:      outside straight flight along one side wall up to each storey's door (roof rights sold upward)
roof:       flat slab: WATER_TANK (blue, 1.0 dia) + laundry + satellite dish; a rooftop shack on 40%
signs:      hand-painted shop boards on ground floors; bars with bulb strings; wire bundles overhead
```

## C-P10 the cholet -- `cholet_ballroom`
```
lot:        10-14 x 18-25 (a corner lot best)
floors:     G shops (2-4 units, roll shutters, st 4.0) | 1-2 BALLROOM double height (7.0), tall windows across the
            front, a mirrored-column hall inside | 3-4 flats (st 2.8) | ROOF: the owner's CHALET (pitched-roof house
            8 x 10 on the roof terrace, set back 2)
facade:     bold Andean-geometric panels (stepped crosses, zig-zags) in coloured glass + mirror glass; symmetric
signs:      the ballroom name in neon across the facade; LED outline of the geometric panels; lightboxes at the shops
night:      the ballroom windows glow pink/green/gold (party nights flash)
```

## C-P11 the cerro with ascensor -- `cerro_tin`
```
hill:       the deck's main rolling hill (or a built terrace mound) 15-30 high; lanes contour round it every 4-6 rise
houses:     timber + corrugated tin, 5-7 front x 8-10 deep; 2 storeys on the uphill lane, +1..3 storeys down the slope
            behind; bay windows/balconies over the drop; every house a different ship colour
ascensor:   a funicular: two cars (3 x 2 x 2.5) on a 30 deg track 40-80 long from the foot to a top station
            (Polanco type: a vertical lift tower + footbridge)
stairs:     stair lanes 1.5 wide with painted risers straight up the slope between house groups
signs:      murals on blank walls; painted boards; a bowl of window lights at night, bulbs along the stair lanes
```

## C-P12 the infilled frame (Torre David) -- `infilled_frame`
```
frame:      a concrete skeleton 20 x 30, 8-16 storeys (on a sky island 6-12), columns 6 m grid, open floors
infill:     each bay (6 x 6 x 3.2) filled differently: brick | tin | glass | left open as a terrace; random colours
access:     a helical RAMP tower (cart/bike) on one side; an open stair core; balconies are just the slab edges
uses:       ground: market hall; lower: shops, gym, chapel; upper: homes; top: rooftop shacks + lark pad
signs:      vertical stack of lightboxes and bulb strings on the ramp tower; a big rooftop billboard
```

## C-P13 the false-front row -- `false_fronts`
```
lot:        6-9 front x 12-20 deep; 1-2 storey gable-roofed timber shop, gable to the street
front:      a flat timber false front 1-3 m taller than the ridge, square or with a stepped/curved top and a cornice
            on brackets; the front IS the sign board (painted letters full width; at night neon outline)
walk:       a boardwalk 2.5 deep under a shed awning on posts
signs:      the false front; a blade sign; neon in the windows
```

## C-P14 the stone-and-gallery tower house (kulle / Bryggen hybrid) -- `kulle_galleries`
```
base:       stone body 10 x 12, 2 storeys (storage, cistern, kitchen), few small windows
top:        1-2 timber storeys oversailing the base 0.5-0.8 on brackets, ringed by a glazed GALLERY (a window wall)
roof:       hipped, heavy stone slabs (or skystone slates), wide eaves 1.0
signs:      lantern at the door; the window wall glows at night (the 'thousand windows')
```

## C-P15 the spiral high street (fortress hill) -- `spiral_high_street`
```
street:     one street 3-4 wide spirals up the island's central hill (1-1.5 turns), through 2-3 GATES (arched
            gatehouses spanning it); stair cuts link the turns
houses:     3-4 storey stone + gallarija (enclosed timber balconies on corbels) on both sides, tiered so each row's roofs
            sit below the next row's doors; hidden gardens behind on suspended stairs
summit:     clan hall / temple / tower
signs:      iron-bracket blade signs every shop; lanterns at the gates; bulb arches (luminarie) over the street at gates
```
