# B6. Ceiling tiles: the model spec

The user asked for "a model for ceiling tiles". One shared part, `ceiling_tile`, has variants all on the same grid, so a
room's ceiling is a MultiMesh or kit-piece grid. Variants:

| variant | source | module | pattern | relief | notes |
|---|---|---|---|---|---|
| `acoustic_grid` | dropped ceiling: T-bar grid with lay-in tiles. 2 × 2 ft (24", 610 mm) and 2 × 4 ft; metric 600 × 600 (tile 595); the main grid is 15/16" (24 mm) wide, "fine line" 9/16" (15 mm) ([Angi](https://angi.com/articles/ceiling-tile-sizes.htm); [Armstrong](https://ca.kanopibyarmstrong.com/blogs/news/what-are-the-sizes-of-ceiling-tiles)) | 0.6 × 0.6 (also 0.6 × 1.2) | fissured speckle; a 24 mm grid frame 10 mm deep | tile 15 mm thick, the grid T 32 mm tall | Offices, clinics, the Steward-era rooms. Variant: a **lit panel** (light troffer, emissive) in 1 of 4 cells. |
| `pressed_tin` | American and Spanish pressed-metal ceilings: 24 × 24" panels with 6", 12" or 24" pattern repeats; steel 0.010" thick; nail-up or snap-lock ([American Tin Ceilings](https://americantinceilings.com/pages/general-faqs)) | 0.6 × 0.6 | 12" repeat: a diamond and floral boss; 6" repeat: small squares; 24": a medallion | 8–15 mm embossing *(est.; no published figure)* | Shops, bars, the exposition style. Finishes: silver, copper, white, cream. Light enough for the Aloft (tin, not plaster). |
| `coffered` | gōtenjō, Japanese coffered: ribs 6–7.5 cm, 45–90 cm between ribs; coffers up to about 1 m; hung, not structural ([JAANUS](https://projects.mcah.columbia.edu/jaanus/record/g%C5%8Dtenj%C5%8D)) | 0.9 × 0.9 cell | square coffers with ribs 70 mm wide, 60 mm deep; option: fine lattice in the coffer (kogumi) | ribs 60 mm | Halls, the bathhouse, clan halls. |
| `batten` | sao-buchi tenjō: thin battens at 4 per ken (about 455 mm) over boards ([folko](https://www.folko.com.au/blog/japanese-minka-xcii-formal-areas-9)) | 0.455 × any | parallel battens 30 × 40 mm over a board field | 40 mm | Tea houses, machiya-style homes. |
| `azulejo` | glazed tile ceiling and soffit panels (Spanish and Portuguese; stream A covers the patterns) | 0.15 × 0.15 tiles in 0.6 panels | a blue and white star or interlace | flat | Soffits of arcades and porches; one texture atlas cell per pattern. |
| `corrugated` | warren reality: corrugated sheet ceilings in rooftop huts and lanes | 0.76 wide sheets | 76 mm pitch corrugation | 18 mm | The cheap look; also alley canopies. |

**Build spec** (for the components stream):
- One mesh per variant for a **0.6 × 0.6 m** cell; coffered is 0.9 and batten 0.455 × 0.9. The face is down (−Y), the origin
  at the cell centre on the plane of the ceiling.
- Low tris: acoustic 2–12, tin about 120 (bosses as low bumps), coffered about 40.
- Shared materials: `ceil_acoustic`, `ceil_tin_silver`, `ceil_tin_copper`, `ceil_wood`, `ceil_azulejo`, `ceil_corrugated`.
  Detail lives in **normals and texture**, but the house rule says **no normal maps** (the toon outline speckles them), so
  model the relief and use a small tileable albedo.
- A light-panel variant (`acoustic_grid_lit`) is emissive at night, and 1 in 4 cells in shops.
- **Generator use:** fill each room's ceiling rectangle with the style's tile (`components` includes `ceiling_tile` with a
  variant), as a kit piece repeated: one shared mesh, placed many times.
