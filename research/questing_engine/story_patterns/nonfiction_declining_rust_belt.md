# Nonfiction Story Patterns — Declining Rust-Belt Industrial

Archetype recap (`_demographic_archetypes.md` §2): legacy manufacturing/shipping town whose core
economic driver has shrunk or left. Population declining -3% to -12%/decade (often -15% to -52%
long-run). Two severities: **Moderate** (income $45k-$60k, homeownership 48-60%, poverty
13-30%) and **Severe** (income below $35k, homeownership below 40%, poverty 40%+ — Benton Harbor
MI: income $31,117, poverty 40.1-42.6%, homeownership 36.7%). Health Care has often overtaken
manufacturing as #1 employer. Physical signature: vacant downtown storefronts (often
mall-preceded, e.g. Elyria's 1967 Midway Mall), un-redeveloped industrial waterfront (Ashtabula's
Superfund coal harbor, closed 2016). Examples: Danville IL, Elyria OH, Ashtabula OH, Benton
Harbor MI.

---

## 1. Factory closure via private-equity ownership churn
**Sources:** Brian Alexander's *Glass House: The 1% Economy and the Shattering of the All-
American Town* (2017) documents Anchor Hocking glassworks in Lancaster, Ohio: founded 1905,
still locally run and civically central through the mid-20th century (Forbes' 1947 30th
Anniversary issue was devoted to celebrating Lancaster's relationship with the company), then
hit by Newell Company's 1987 hostile takeover — executives fired, headquarters moved out of town,
leadership no longer living locally — followed by a chain of subsequent owners (Global Home
Products 2004, Monomoy Capital Partners 2006, Centre Lane Partners 2021) and two bankruptcy
filings (2006, 2015). Amy Goldstein's *Janesville: An American Story* (2017) documents the 2008
closure of the GM assembly plant in Janesville, Wisconsin, and the community's fractured,
unequal recovery from 2008-2013.
**Why it recurs here:** this is the archetype's defining mechanism — "core economic driver has
shrunk or left" is almost always, on inspection, a story about a factory changing hands (often to
an out-of-town financial owner) rather than simply vanishing overnight.
**Locations:** `small_factory_mill`, `warehouse`, `bank_branch` (financing/foreclosure angle).

## 2. Opioid epidemic arrival and entrenchment
**Sources:** Sam Quinones' *Dreamland: The True Tale of America's Opiate Epidemic* (2015, National
Book Critics Circle Award) traces how prescription-painkiller dependency (OxyContin-era
overprescription) created a market that Xalisco, Nayarit-origin black-tar-heroin distribution
networks then exploited — with small and mid-size Rust-Belt and Appalachian towns as the primary
targets, precisely because their existing economic distress and eroded institutional trust made
them easy markets. Beth Macy's *Dopesick: Dealers, Doctors, and the Drug Company that Addicted
America* (2018) documents the same mechanism centered on Purdue Pharma's marketing.
**Why it recurs here:** the combination of eroded local employment, a large disabled/injured
former-industrial-labor population (a documented on-ramp to prescription opioids), and declining
institutional capacity (fewer treatment resources, stretched police/EMS) is specific to towns that
have already lost their industrial base — distinguishing this from the meth-in-farm-country
pattern (`nonfiction_stable_ag_manufacturing.md` §7), which has a different economic driver
(agricultural/meatpacking labor consolidation rather than deindustrialization).
**Locations:** `pharmacy_drugstore`, `police_station`, `diner_cafe`, residential (`ranch`,
`mobile_home`).

## 3. Municipal water/infrastructure crisis under fiscal collapse
**Sources:** Benton Harbor, Michigan — one of this archetype's four named examples — had elevated
lead levels discovered in its tap water in 2018, testing at 22 ppb (above both the federal action
level of 15 ppb and Flint's contemporaneous levels), caused by aging lead service lines; $10
million was budgeted for line replacement in 2021, completed December 2023. Flint's better-known
2014-19 water crisis (lead contamination following a cost-cutting water-source switch under
state-appointed emergency management) is the reference case nationally for this pattern in a
Michigan Rust-Belt city.
**Why it recurs here:** severe-tier poverty and an eroded tax base mean deferred infrastructure
maintenance is not a hypothetical risk but a realized one — the same fiscal collapse that produces
this archetype's income/homeownership signature also starves the water/sewer utility.
**Locations:** `water_tower`, `town_hall`.

## 4. State/emergency financial-manager takeover of municipal government
**Sources:** Benton Harbor's city government was placed under a state-appointed Emergency
Financial Manager starting April 2010, after a 2009 Michigan Treasury investigation found the
city's budgets "effectively meaningless as a financial management tool" and identified a $10
million pension-fund deficit. This is the same Michigan emergency-management statute later
applied to Flint and Detroit.
**Why it recurs here:** severe-severity towns in this archetype (poverty 40%+, homeownership
below 40%) generate exactly the kind of structural budget collapse that triggers state
receivership — a distinctly Rust-Belt-severe-tier story beat, not seen in the moderate tier or in
other archetypes.
**Locations:** `town_hall`, `courthouse`.

## 5. Dead mall / vacant downtown retail exodus
**Sources:** Elyria, Ohio's 1967 Midway Mall preceding and accelerating its downtown's decline is
cited directly in `_demographic_archetypes.md` as this archetype's physical signature; Benton
Harbor shows the same mechanism on a compressed timeline (Fairplain Plaza 1958, The Orchards Mall
1979, downtown population falling from 19,136 in 1960 to 14,707 by 1980). The broader "dead mall"
genre is a well-established journalism/urban-studies beat (regional business press, urban-studies
academic coverage of retail geography) documenting the general pattern of enclosed shopping malls
hollowing out downtowns and then themselves failing a generation later.
**Why it recurs here:** this archetype's downtown vacancy is explicitly named as part of its
"physical/building-condition signature" in the source demographic research — it is the visible,
walkable evidence of the underlying economic decline.
**Locations:** `general_store`, `clothing_store`, `movie_theater`, `pharmacy_drugstore`.

## 6. Industrial waterfront/Superfund contamination left un-redeveloped
**Sources:** Ashtabula, Ohio's coal-handling harbor, a Superfund site closed in 2016, is cited
directly in `_demographic_archetypes.md`; the broader EPA Superfund program and its associated
"legacy industrial contamination" reporting genre (regional environmental-beat journalism,
periodic national coverage of Great Lakes industrial-waterfront cleanup funding fights) documents
the same pattern across dozens of Rust-Belt port/mill towns.
**Why it recurs here:** unlike a resort town's waterfront (which gets redeveloped into tourist
amenity, see `nonfiction_lake_resort.md`), a Rust-Belt town's industrial waterfront typically sits
contaminated and undeveloped for decades because there's no capital or economic driver to justify
cleanup, which is itself a marker of the archetype's severity level.
**Locations:** `warehouse`, `water_tower` — no dedicated harbor/dock building type currently
exists in `building_catalog/`, a gap worth flagging.

## 7. Out-migration and "who gets left behind" divide
**Sources:** George Packer's *The Unwinding: An Inner History of the New America* (2013 National
Book Award) profiles Tammy Thomas in Youngstown, Ohio, whose population fell from 140,000 (1970)
to ~67,000 (2010) as the steel industry collapsed — documenting both the exodus of the upwardly
mobile and the harder economic position of those who stayed. `_demographic_archetypes.md` notes
this archetype's age skew is genuinely bimodal: Benton Harbor's severe-tier variant skews young
(32.2% under 18, only 10.6% 65+) because out-migration selectively removes retirees and the
upwardly mobile, leaving a younger, poorer population behind — the opposite of the moderate-tier
towns (Elyria, Ashtabula, Danville), which skew toward the Stable-Town norm (median age 38-41).
**Why it recurs here:** this is the demographic mechanism underneath the archetype's income/
poverty numbers, and it produces two visibly different "kinds" of Rust-Belt town depending on
severity.
**Locations:** residential (`foursquare`, `victorian_queen_anne`, deteriorating stock), `church`.

## 8. Political realignment / "why this town turned" narrative
**Sources:** A defining journalism genre of the 2016-2024 election cycles — the "diner interview"
trope in national political reporting (NYT/WaPo/Politico dispatches from Rust-Belt diners and
bars) explaining industrial decline's connection to political shift. J.D. Vance's *Hillbilly
Elegy* (2016) — while centered on Middletown, Ohio and Appalachian Kentucky migration rather than
a pure company-town collapse — is the most commercially prominent book-length version of this
narrative, connecting economic deterioration, family instability, and a political shift "from
voting Democratic to a strong Republican affiliation" (a reading later contested by critics who
argue Vance under-weights structural/economic causes relative to cultural ones — a critique worth
noting for anyone treating the book as pure economic documentation rather than a contested memoir).
**Why it recurs here:** national political journalism treats Rust-Belt towns as the paradigmatic
site for this narrative precisely because of the archetype's visible economic before/after.
**Locations:** `diner_cafe`, `bar_tavern`, `town_hall`.

## 9. School-district fiscal distress and building closures
**Sources:** Parallel to municipal fiscal collapse (§3-4) — regional education-beat reporting on
Rust-Belt districts facing state fiscal oversight, building closures, and program cuts tracks the
same towns' broader financial collapse.
**Why it recurs here:** the same eroded tax base that produces water-infrastructure and municipal-
finance crises also starves the school district, and enrollment decline compounds it (unlike
archetype 1's slower consolidation-driven version, this is fiscally forced, not merely
demographically driven).
**Locations:** `school`.
