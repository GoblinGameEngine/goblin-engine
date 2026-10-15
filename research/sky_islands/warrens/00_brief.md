# Sky island warrens: brief (2026-10-14, round 3)

## The user, 2026-10-14
> You do realize that putting a dome on a western style building does not count as an Arabic Old Towne, right? I want
> arabic style architecture. I want actual warrens. I want each island to be it's own unique twisting city built for
> centuries ontop of the previous layers. It should be beautiful and cyberpunk and each island should have it's own
> architectural mark of it's origin civilization. We need better buildings for the islands. We need trees and other
> foliage as well. The foliage should match the civilization. I have not seen the Kowloon City nor have I seen
> Karachi. Do a lot of research and let's make some real diversity.

Earlier the same day:
> We need to work on the framerate again. Onboard the islands it is slow and there is really bad flickering at night.
> We will also need more detail on the islands. We need large paved paths and streets. This all needs to run
> smoothly. ... Be more granular about what gets LOD models. See where we don't need to render the interior of
> buildings. Use tricks like lens flare and reflections to hide building interiors, but only where necessary.

## What was wrong with round 2
Each island got 5 lot-based models per style: western blocks (gbhouse slabs and towers) wearing a style's ornament.
There was no warren, no layering, no twisting streets, and no true regional building language.

## The new direction
- **One island, one city:** a single connected urban mass grown over centuries, not buildings on lots.
  - The oldest layer is at the bottom: masonry, courtyards, a founding street pattern.
  - Each later layer accretes on top: rooms on roofs, bridges across lanes, cantilevers, infill, towers.
  - The newest layer is cyberpunk: neon, cables, screens, AC units, tin and plastic, rooftop shacks.
  - Lanes twist, tunnel under buildings and climb in stairs. Large paved main streets and plazas are kept open.
- **The civilization's mark:** each island is built in its origin civilization's own construction language: wall
  materials and thickness, openings, screens, roofs, ornament, colour, how rooms stack, how streets bend, and its
  plants. The mark must not be a dome stuck on a generic block.
- **Plants:** trees, shrubs, vines, roof gardens and planters that match the civilization (date palms and
  bougainvillea, bamboo and banyan, cypress and olive, and so on), as cheap MultiMesh foliage.
- **Real diversity:** at least 20 distinct civilization families across the 100 islands, each researched in depth
  with many examples. That includes Kowloon Walled City and Karachi (old town, Saddar, Lyari, Orangi), which the
  user named.
- **Performance (non-negotiable):** 60 fps aboard on the Deck.
  - The city is a generated mesh built from shared kit pieces per civilization, merged per chunk, with chunk LODs.
  - Interiors exist only where you can go in; elsewhere windows use reflection and lit-glass tricks.
  - Distant islands are cheap LODs.

## The user, later (2026-10-14)
> You're going to have to make new buildings, but you are only adding to the shared parts library. I want you to
> research how to use common pieces to make actual ethnic diversity. Finish your FPS work, document what you
> leartned, then remake the island buildings to make actual ethnic dense cityscapes with ponds and public green
> space. Research walkable cities. Use the techniques in your architecture. We need fast travel locations for each
> floating city.

### Rules that follow from this
- **Shared parts only:** new building geometry is new pieces in the shared kit library (remake/blender/sky/components
  and gbkit), reused across islands. There are no per-island unique meshes beyond the merged chunks made from kit
  pieces. Diversity comes from how common pieces are chosen, proportioned, coloured, combined and arranged
  (kit-of-parts, pattern language, vernacular grammars), plus a modest number of civilization-specific pieces.
- **Order:**
  1. Finish the frame-rate work (60 fps aboard), and document what was learnt (research/perf_learnings.md).
  2. Rebuild the island cityscapes.
- **The city must be:**
  - dense and of its own ethnicity;
  - walkable, using research on walkable cities (Gehl, Jacobs, Alexander's A Pattern Language, superblocks,
    traditional street hierarchies);
  - laid out with ponds and public green spaces, plazas, and large paved main streets.
- **Fast travel:** each floating city gets a fast-travel location, wired into the game's fast-travel system.

## Build, milestone 1 (2026-10-15)
Following r4_design.md §9, steps 1–3. Two civilizations on two test islands:
- `maghrebi_medina` (r1, Fez/Marrakesh, with tower houses) on SKY-100 "Ithaca" (3 blocks);
- `kowloon_walled` (r2) on SKY-071 "Lollygag" (7 blocks).

### Streams
- **GENERATOR:** `tools/sky/warren/`.
- **KIT:** shared pieces in remake/blender/sky/components, plus the piece export.
- **RUNTIME:** `godot_project/remake/scripts/sky/sky_warren.gd`, plus hooks in sky_island.gd.

### Contracts
- **Pieces:**
  - `godot_project/remake/sky/warrens/pieces.json` (written by KIT) maps
    `{piece_id: {"glb": res path, "mesh": name, "bay": [3, 3.2], "slots": [...], "lod1": "box|keep|drop",
    "collide": bool}}`.
  - Piece ids are stable strings; the binary format uses a u16 index into the `pieces` list, written by the
    generator from pieces.json.
  - KIT publishes a first pieces.json (ids and placeholder boxes) early so GENERATOR and RUNTIME can start.
- **Placements:** `godot_project/remake/sky/warrens/<SKY-id>.bin.gz`, as r4 §5, written by GENERATOR. GENERATOR also
  writes a readable `<SKY-id>.json` (debug: units, doors, travel, anchors, walk graph). RUNTIME reads both.
- **Frame:** the island's local frame (+X south, +Y up, +Z west; y 0 the deck at the faces). Lattice cell (i, j, k) has
  its centre at (x0 + 3i + 1.5, 3.2k, z0 + 3j + 1.5).
- **Shared:** the game lock (research/perf_islands_brief.md), and no commits; the coordinator integrates.
