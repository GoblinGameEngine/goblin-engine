# Plan B-KWC: the Kowloon warren block (accretion to a cap)

Source: Kowloon Walled City (b_hong_kong.md, b_warrens.md). Units are metres. A generator follows the steps in order.

```
site:          one island block, 100 x 80 (or a part of one)
lot grid:      lots 4-8 wide x 6-12 deep, back to back; NO side gaps (party walls shared)
alleys:        keep a 1.2-2.0 slot every 2-4 lots in each direction; 30% of alley length roofed (canopy_alley) at 2F-3F
cap:           a flat height cap for the block: 6-12 storeys (the island's balloons set it, as Kai Tak did); storey 2.8
growth:        round 0: every lot gets 2-4 storeys
               rounds 1..R (R = 3-5): each lot +0..3 storeys (never past the cap); if it grows, it may
                 - overhang an alley or the promenade by 0.6-1.5 (one side) from the new storey up
                 - add a caged balcony (balcony_cage) on 1-3 bays of the new storeys
               last round: 40% of roofs get a rooftop shack (rooftop_shack) 1-2 storeys, the rest water tanks,
               aerials, laundry, roof gardens
links:         lots of equal height side by side share a roof deck; height steps of 1-3 storeys get
               stair_external or a ladder; across an alley: a skybridge at a random storey (1 per 4 lots)
ground (G):    every lot: a shop 3-6 wide behind shutters; a stair door between some shops (1 per 2 lots)
1F-2F:         workshops, clinics (dentists on the OUTER face), food makers
upper:         flats of 15-30 m2 off a corridor or stair landing; windows 0.9x1.2 with window_grille
outer face:    the sign band: neon_blade stacks every 3-5 m, signs overlapping to 4F
roof network:  roofs linked by ladders + plank bridges; every roof reachable from every other (roof access rule)
night:         bare fluorescent tubes in the alleys (cold white #e8f4ff), warm windows, neon on the outer face
```
