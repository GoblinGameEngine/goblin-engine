# R3: Scots "lands" and closes (Edinburgh's Old Town)

**Island culture:** a ridge-top spine street, the Royal Mile, with a herringbone of steep, dark, narrow *closes* and *wynds* dropping off both sides at right angles. They pass through archways (pends) under tall rubble tenements (*lands*) up to 10–14 storeys, the "first skyscrapers". There are crow-stepped gables, turnpike (spiral) stair towers, harled walls and timber galleries. The mark is the vertical stone slab and the fishbone close: a canyon of soot-dark stone with a slot of sky.

## Examples
- Plots (tenements) on which "lands" were built; wynds and closes run down the ridge at right angles to the High Street. Gladstone's Land. [undiscoveredscotland](https://undiscoveredscotland.co.uk/edinburgh/gladstonesland/index.html)
- Height:
  - Tenements up to 12 storeys; some to 14 storeys with up to 30 people per floor (the Heave Awa' Hoose).
  - About 250 named closes, wynds and courts on the Royal Mile (another source says about a hundred closes).
  - Multi-storey tenements first appear in the late 16th century over paved closes.
  - Sources: [Atlas Obscura](https://atlasobscura.com/places/heave-awa-hoose-2), [edinburghexpert](https://www.edinburghexpert.com/blog/close-encounters-in-edinburghs-old-town), [SAIR excavation](https://journals.socantscot.org/index.php/sair/issue/view/122)
- Materials: harled rubble with chamfered margins and crowstepped chimney gables (Robertson's Close); snecked rubble with ashlar margins and Scots Baronial crowsteps (later). [British Listed Buildings](https://britishlistedbuildings.co.uk/200405346-16-18-20-robertsons-close-edinburgh-edinburgh), [HES LB29631](https://portal.historicenvironment.scot/designation/LB29631)

## Generator grammar
- **Cell:** frontage 6–10 m on the spine street, plots 50–150 m deep and very narrow, built solid with closes between. Storeys 3.0 m, 6–12 storeys on the downhill side (the ridge drop adds storeys: 6 on the spine street, 10–12 at the back).
- **Walls:**
  - Rubble 0.6–0.9 m with harl (a lime roughcast) `#cfc7b6`, or exposed sandstone darkened by soot `#4a4640` to `#6e675c`, ashlar margins `#9a907e`.
  - Painted shopfronts: Royal blue `#1f3a6a`, oxblood `#6a1f22`, bottle green `#1f4a33`, black `#1a1a1a` with gold letters.
  - Slate roofs `#4b4f55`.
  - Weathering: very heavy soot blackening, damp, moss in the closes.
- **Mass:** continuous slabs along the spine street; tall narrow ranges behind run downhill along each close; small courts open off the closes. The spine-street face has timber-fronted galleries (early) or ashlar fronts; projecting turnpike stair towers.
- **Streets:**
  - The spine street (High Street) 15–20 m, cobbled (setts `#5a5a58`).
  - Closes 1–2.5 m, entered through pends (arched passages 2–3 m wide, 3 m high), dropping steeply in long flights of steps.
  - Wynds slightly wider (3–4 m, carts).
  - Cross-ridge bridges at high level (South Bridge style).
- **Growth:**
  - Layer 0: the castle rock and the medieval burgage plots.
  - Layer 1: 16th–17th-century lands with timber galleries and crowsteps.
  - Layer 2: 18th–19th-century rebuilt tenements, Baronial turrets.
  - Layer 3: 19th-century bridges over the closes and vaulted under-street vaults (the South Bridge vaults).
  - Layer 4: cyberpunk.
- **Openings:** small sash windows (0.9×1.6 m) in regular rows, 2×2 or 6-over-6 panes; arched pends; projecting timber galleries on the street fronts; shopfront cornices with signboards.
- **Roofs:** steep slate roofs (45–55°) with crow-stepped gables, tall chimney stacks with many pots (8–16 pots per stack), dormers, conical-roofed corner turrets (Baronial).
- **Ornament:** crowsteps, marriage lintels (carved initials and dates), turrets on corbels, iron lamp brackets, close names painted over the pends.
- **Public space:**
  - The spine street with a mercat cross and the cathedral (St Giles style, with a crown spire).
  - Close courts.
  - Gardens on terraces down the slope.
  - A loch garden at the foot (Princes Street Gardens: a drained loch, now a park).
- **Water:** the loch garden pond at the foot of the slope, wells (pump wells) on the spine street.

## Street hierarchy
- **Spine street (main):** 15–20 m along the ridge crest.
- **Wynds:** 3–4 m.
- **Closes:** 1–2.5 m (fishbone, every 10–20 m).
- **Pends.**
- **High-level bridges** over the valleys.
- **Squares:** the market cross, the cathedral close, the gardens below.

## Plants
- Very little in the closes: ivy and ferns in the cracks, moss.
- Gardens on the terraced slope below: rowan (red berries `#c0302a`), sycamore, beech, holly, yew.
- Window-box heather (`#9a5a9a`).
- Thistles.
- The loch-garden lawns with elms and cherries.

## Cyberpunk overlay
- Closes roofed in glass and turned into vertical arcades of shops lit in cold neon.
- Tenement backs hung with exterior cable risers and heat exchangers.
- Chimney stacks recast as vent towers glowing at the cap.
- Gargoyle security cameras.
- Fog machines (the haar).
- Pends with holo-signs naming the close.
- **Night:** cold and moody. Dark stone slabs with scattered warm sash windows (`#ffcf86`). Wet setts reflecting sodium lamps on iron brackets. The closes are lit tunnels of colour going down into the fog.

## Kit
- **Shared pieces:**
  - `gable_step` (crowstep, main), `pend_passage` (main), `turnpike_stair` (main), `chimney_stack` (main: tall many-pot stacks)
  - `dormer_row`, `french_window` (as a sash), `gallery_timber`, `round_tower` (turret), `pinnacle`, `cornice`, `name_board_close`
  - `lantern_wall`, `stair_cut`, `beam_steps`, `bell_tower` (crown spire), `stone_slab_roof` (as slate)
- **Unique pieces:**
  - `harl_wall`: a roughcast texture.
  - `marriage_lintel`.
  - `corbelled_turret_cone`.
  - `close_mouth_pend_sign`.
  - `mercat_cross`.
- **Parameters:**
  - Extreme verticality: 6–12 storeys on narrow fronts, tallest on the downhill side.
  - Closes every 10–20 m along the spine, cut at right angles and descending.
  - Window to wall 25%, small regular sashes.
  - Soot-dark palette.
  - Roof clutter: chimney stacks every 6–8 m, crowstepped gable ends.
