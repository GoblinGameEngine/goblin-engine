# Nonfiction Story Patterns — Lake-Resort/Tourism-and-Retiree

Archetype recap (`_demographic_archetypes.md` §6): a town whose built environment and economy are
sized for a seasonal tourist/second-home population much larger than its year-round resident base
— the archetype the original 36-settlement sample almost entirely missed. Flat-to-declining
year-round population (-6% to -13%/decade) can coexist with a *growing* tourism economy. Age skew
bimodal by scale: small resort villages (under 5,000) skew very old (median age 53-62); larger
resort-and-working cities (10,000-30,000, e.g. Sandusky OH) skew moderate (36.5-39.5) because a
real hospitality workforce lives there year-round. Income is bimodal, not one band — small
gentrified art-colony resorts (Saugatuck ~$121k-124k) skew very high; larger tourism-and-retiree
cities (Sandusky $51k) show only moderate income *alongside* high poverty (25.6%), because the
wealthy seasonal-homeowner population and low-wage hospitality workforce are demographically
separate groups in the same town. Homeownership nominally high (70-84%) but this counts vacation
homes — the more diagnostic figure is housing-unit vacancy (South Haven 45.6%). Household size
small (1.8-2.3). Accommodation & Food Services, Retail, Arts/Entertainment lead employment, with a
manufacturing base often persisting underneath. Examples: South Haven MI, Saugatuck MI, Sandusky
OH, Rice Lake WI, Put-in-Bay OH (extreme micro sub-variant, ~65-70x seasonal population
multiplier).

---

## 1. Second-home/gentrification displacement of year-round working residents
**Sources:** Door County, Wisconsin (the "Cape Cod of the Midwest") generated over $600 million in
tourism economic impact in 2023, with tourist arrivals growing from ~1,000/year (1909) to 1.9
million/year (1995) — a scale of second-home and vacation demand that Wisconsin regional press
(Wisconsin Public Radio, Milwaukee Journal Sentinel) has documented as driving housing costs beyond
what the year-round hospitality/retail workforce can afford. This is the general national pattern
(also extensively documented in non-Midwest resort towns like those on Cape Cod and Martha's
Vineyard) applied to Great Lakes resort counties.
**Why it recurs here:** this is the direct social consequence of the archetype's core bimodal-
income signature — wealthy seasonal homeowners and low-wage hospitality workers sharing one small
housing market inevitably produces displacement pressure on the latter.
**Locations:** residential (`cape_cod`, `bungalow_craftsman`) converted to vacation use,
`general_store`.

## 2. Short-term rental (Airbnb/Vrbo) regulation fight
**Sources:** A well-documented national regulatory-conflict pattern — critics argue short-term
rentals reduce long-term affordable housing supply and let investors outbid local buyers/renters
for housing stock, while platforms and some economists counter that the housing-supply problem is
structural rather than STR-caused; cities nationally have responded with day-limit caps,
owner-occupancy requirements, licensing regimes, and (in extreme cases) outright bans. This
conflict recurs in essentially every US lake/beach resort town with a meaningful vacation-rental
market, documented continuously in local-government-beat coverage of city-council ordinance fights.
**Why it recurs here:** the archetype's defining vacancy signature (up to 45.6% of housing units
vacant/seasonal in South Haven) is largely produced by exactly this kind of short-term/seasonal-use
housing, making STR policy a uniquely high-stakes local political fight in this archetype
specifically.
**Locations:** `town_hall`, residential broadly.

## 3. Seasonal/H-2B guest-worker labor shortage for hospitality
**Sources:** A well-documented national pattern (extensively covered around Cape Cod, Mackinac
Island, and other seasonal-tourism economies) where hospitality and food-service employers rely on
H-2B temporary-visa workers to staff a summer season that the local year-round population cannot
fill alone, and annual H-2B visa-cap shortfalls or processing delays generate recurring "will we
have enough staff this summer" local-business-press stories.
**Why it recurs here:** the archetype's Accommodation & Food Services-dominant employment mix,
combined with a small and often aging year-round population, structurally requires imported
seasonal labor that no other archetype in this set depends on at this scale.
**Locations:** `hotel_inn_small`, `restaurant`.

## 4. Lake water-quality crisis threatening the tourism economy
**Sources:** Western Lake Erie's recurring harmful-algal-bloom crisis — most acutely the 2014
Toledo water crisis, when a bloom-driven microcystin toxin contaminated the city's drinking-water
supply for roughly two days — is the reference case for this pattern in the Great Lakes region;
Sandusky OH (one of this archetype's four named examples) sits on the same western Lake Erie basin
affected by these recurring blooms, and regional environmental-beat journalism (Ohio and Michigan
outlets) covers algal-bloom forecasts and beach closures as an annual seasonal story.
**Why it recurs here:** a resort town's entire economic proposition depends on the lake itself
being usable and attractive — water quality is not an abstract environmental concern here but a
direct, immediate threat to the tourism revenue this archetype's economy is built on, distinct
from a Rust-Belt town's industrial-contamination story (`nonfiction_declining_rust_belt.md` §6),
where the contaminated site is a liability rather than the core economic asset.
**Locations:** `water_tower` — no dedicated marina/waterfront-amenity building type currently
exists in `building_catalog/`, a gap worth flagging.

## 5. Retiree in-migration reshaping local politics
**Sources:** No single iconic book, but a well-documented structural pattern reflected directly in
the archetype's own demographic signature: small resort villages' median age of 53-62 (South Haven
56.2-61.7, Saugatuck 53.3-53.9) means a retiree-heavy electorate increasingly outnumbers families
with school-age children, a dynamic widely covered nationally (and specifically in Michigan/
Wisconsin lakeshore-community local press) wherever school-funding referenda fail in aging resort
towns because most voters no longer have children in the district.
**Why it recurs here:** the archetype's bimodal age structure by scale is one of its most
distinctive demographic features (`_demographic_archetypes.md` §6), and local political outcomes
(school funding, land-use policy favoring low-density/scenic preservation over workforce housing)
follow directly from who actually votes.
**Locations:** `school`, `church`, `town_hall`.

## 6. Boom-bust seasonal small-business survival story
**Sources:** A recurring local-business-feature genre — "how does a business make a year's income
in a 12-16 week season" profiles of shop owners, restaurateurs, and innkeepers, a staple of
regional tourism-beat and small-business journalism in every seasonal resort economy.
**Why it recurs here:** unlike a college town's academic-calendar seasonality
(`nonfiction_college_town.md` §8), this archetype's seasonality is driven by weather/tourism
season and can be far more extreme at the small end (Put-in-Bay's ~65-70x seasonal population
multiplier is the most extreme seasonal swing of any archetype in this dataset).
**Locations:** `diner_cafe`, `general_store`, `hotel_inn_small`.

## 7. Art-colony gentrification of a small resort town
**Sources:** Saugatuck, Michigan's income profile ($121k-124k, the highest in the entire 46-
settlement dataset) reflects second-home-driven gentrification of what `_demographic_archetypes.md`
describes as a small "gentrified art-colony" resort — a well-recognized sub-pattern nationally
(comparable small art-colony resort towns exist around the country) where an artist/gallery
community's earlier cultural cachet attracts wealthy second-home buyers who then price out both
the artists and the original working-class lakefront community.
**Why it recurs here:** this is the most extreme version of the general second-home-displacement
pattern (§1) specific to the small, high-income end of this archetype's income bimodality.
**Locations:** `general_store`, `clothing_store` (boutique conversion), `bar_tavern`.

## 8. Ferry/transportation-dependent micro-economy
**Sources:** Put-in-Bay, Ohio's extreme micro-scale case (year-round population under 500, a
~65-70x seasonal multiplier to 10,000+ peak-summer visitors) depends structurally on ferry and
golf-cart infrastructure rather than road access — `_demographic_archetypes.md` notes standard ACS
demographic data isn't reliably available at this scale, and the town should be modeled primarily
via the population-multiplier mechanic and ferry-scaled infrastructure rather than the numeric
demographic bands used for the rest of the archetype.
**Why it recurs here:** island/peninsula resort towns nationally generate a recognizable "the ferry
schedule is the town's circulatory system" story genre — ferry breakdowns, winter-isolation
features, and ice-bridge-safety stories (a genuinely recurring Lake Erie island-community news
category) — unique to this most-extreme sub-variant.
**Locations:** no dedicated marina/ferry-dock building type currently exists in
`building_catalog/`, a gap worth flagging if this sub-variant is used.
