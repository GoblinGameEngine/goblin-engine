# Meandering River Geomorphology — Reference Numbers

## Core empirical relationships

**Sinuosity.** A channel is formally classified as "meandering" once its sinuosity (channel length / down-valley straight-line length) reaches **1.5 or greater**. Below that it's "sinuous" or "straight."

**Meander wavelength vs. channel width.** This is the single most load-bearing number for a generator: across a wide range of studied rivers, **meander wavelength (λ) ≈ 10–14× bankfull channel width (W)**. This is the classic Leopold & Wolman-era finding, later confirmed across many independent studies with power-law fits (coefficients ranging roughly 6.3–12.3 depending on dataset and how "wavelength" is measured — distance between successive bend apexes on the same bank vs. distance between inflection points differs by convention). Practical takeaway: **λ ≈ 10–14×W is a solid design constant.**

**Radius of curvature of a bend.** Typically **2–3× channel width**. This is also fairly universal — it's essentially a hydraulic property of how tightly water can turn without massive energy loss, not primarily a function of scale.

**Meander belt width** (outer-bank-to-outer-bank envelope the channel wanders within over time): commonly cited as **~15–18× channel width**, though a more conservative empirical fit (Williams 1986, valid W=5–13,000 ft) gives belt width ≈ 3.7×W^1.12, which works out to roughly **6× channel width** for mid-sized rivers — i.e. sources disagree by close to 3x on this one, so treat 6–18× as the plausible envelope and 8–10× as a reasonable middle design value.

**Confined vs. free meanders.** Where a valley wall, terrace, or bedrock forces the river into a narrower corridor than it "wants," ratios run higher (λ/W ≈ 17, radius/W ≈ 4.1) than free meanders on an open floodplain (λ/W ≈ 8–14, radius/W ≈ 2–3). Not directly relevant to an open station floor, but useful if any zone (e.g. downtown, hemmed by buildings/embankments) should read as a locally "confined" reach with tighter, more elongated bends.

## Point bar / cut bank / oxbow process

- The outer bank of a bend is the **cut bank**: flow velocity is fastest there, causing erosion, often visible as a steeper, sometimes bare or slumping bank.
- The inner bank is the **point bar**: slower flow deposits sediment, producing a shallow, gently-sloping, often sandy/gravelly bar.
- Erosion on the cut bank and deposition on the point bar happen at roughly matched rates, which is *why* the channel migrates sideways (and slightly downstream) over time rather than just widening.
- Continued migration narrows the "neck" between two adjacent bends until a flood cuts through it (a **neck cutoff**), stranding the abandoned loop as an **oxbow lake**, which then gradually fills with sediment and vegetation.
- Migration rates vary enormously by river: from imperceptible (bedrock-confined) to extreme outliers like the Kosi River in India at ~730 m/year. Midwestern alluvial rivers on soft floodplain sediment migrate on the order of single-digit to a few tens of meters per year in active reaches — worth knowing for narrative/erosion-feature placement, though a static generated map doesn't need to simulate migration itself.

## Reference rivers (concrete numbers)

| River | Channel width | Notes | Source |
|---|---|---|---|
| Wabash River | ~200 ft (61 m) at Huntington, IN, widening to ~400 ft (122 m) at Covington, IN, up to ~1,200 ft (366 m) near its mouth | Classic Midwestern meandering river; large lower reaches are "requires a real bridge" scale | worldatlas.com/rivers/wabash-river |
| Wabash at Terre Haute | reported as meandering through a floodplain averaging roughly 1,000 ft wide, ~20 ft deep | Note: this figure likely describes the meander-belt/floodplain corridor width and channel depth together, not literally a 1,000-ft-wide channel — treat with caution, it's a compound description, not a clean single number | journals.indianapolis.iu.edu (Volume of the Ancient Wabash River) |
| Kankakee River (historical, pre-channelization) | Not numerically given in sources found, but qualitatively: **240+ miles long with over 2,000 meander bends** before being straightened in the 1880s–90s into a ~90-mile ditch | Illustrates how radically a wide marshy meandering river can be compressed — inverse-useful for understanding what "natural" density of bends looks like | ISWS Kankakee report; Grand Kankakee Marsh (Wikipedia) |
| Kankakee River (post-channelization ditch) | ~1.5–2 chains wide = ~99–132 ft (30–40 m) in its lower course | The straightened successor channel — useful as a "small/creek-scale" width anchor, i.e. what NOT to use for a "requires bridges" river | ISWS Kankakee report |
| Illinois River at Peoria | Widens to nearly **1 mile across** at Peoria Lake, a natural lake-like widening of the river itself | This is a real-world precedent for "a lake that straddles the river" — see lakes_and_ponds.md | USGS/general Illinois River sources |

**Design-relevant conclusion:** a river "wide enough to need real bridges downtown" in Midwestern terms is roughly in the **150–400 ft (45–120 m) channel-width class** (Wabash mid-reach territory), not the mile-wide big-river class (that's Mississippi/Illinois-at-the-lake scale, appropriate only for the lake feature, not the river channel itself).

## Sources
- [Meander wavelength/channel width discussion, ResearchGate](https://www.researchgate.net/figure/Relationship-between-the-meander-wavelength-l-and-the-channel-width-W-m-1-for_fig3_225521438)
- [MEANDER SHAPE AND THE DESIGN OF STABLE MEANDERS, USDA ARS](https://www.ars.usda.gov/ARSUserFiles/6112/meanderShapeAndTheDesign.pdf)
- [Vermont Stream Geomorphic Assessment — Appendix H Meander Geometry](https://dec.vermont.gov/sites/dec/files/wsm/rivers/docs/assessment-protocol-appendices/H-Appendix-H-04-Meander-Geometry.pdf)
- [Meander, Wikipedia](https://en.wikipedia.org/wiki/Meander)
- [Alluvial river, Wikipedia](https://en.wikipedia.org/wiki/Alluvial_river)
- [River channel migration, Wikipedia](https://en.wikipedia.org/wiki/River_channel_migration)
- [Fluvial Features — Meandering Stream, NPS](https://www.nps.gov/articles/meandering-stream.htm)
- [What Are Oxbow Lakes?, IERE](https://iere.org/what-are-oxbow-lakes/)
- [Wabash River, WorldAtlas](https://www.worldatlas.com/rivers/wabash-river.html)
- [Volume of the Ancient Wabash River, Wm. A. McBeth](https://journals.indianapolis.iu.edu/index.php/ias/article/download/14451/14556/20957)
- [The Kankakee River yesterday and today, Illinois State Water Survey](https://www.isws.illinois.edu/pubdoc/MP/ISWSMP-60.pdf)
- [Grand Kankakee Marsh, Wikipedia](https://en.wikipedia.org/wiki/Grand_Kankakee_Marsh)
- [Meander Width Ratio, Buffalo fluvial geomorphology reference](https://fgmorph.eng.buffalo.edu/fg_3_86.php)
- [TRCA Meander Belt Width Delineation Procedures](https://sustainabletechnologies.ca/app/uploads/2013/01/Belt-Width-Delineation-Procedures.pdf)
- [A Statistical Comparison of Meander Planforms in the Wabash Basin, Chang 1970](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/WR006i002p00557)
