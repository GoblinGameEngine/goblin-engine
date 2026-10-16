<!-- research/flea_markets/04_economics.md -- flea market and bazaar economics (web research, 2026-10-15). How the game uses it: 06_secondary_economy.md. -->

# Flea-market and bazaar economics: research report for a game design document

**About the sources.** Bracketed numbers point to the source list at the end. "≈" marks an approximate or rule-of-thumb figure. Three tags mark weaker evidence:
- **[snippet]**: I saw the figure only in a search-result extract and did not read the full page.
- **[mem]**: the citation or detail comes from my background knowledge and I could not check it online this session.
- **[anecdote]**: a single vendor, a blog post or a promotional source.

Hard, survey-based data on flea markets is scarce. The NFMA headline numbers are old and inconsistent. Treat the balancing numbers in §6 as plausible design ranges, not measured facts.

---

## 0. Executive summary for designers

- **Scale (US).** The most-quoted figure, credited to the National Flea Market Association (NFMA), is ≈1,100 markets, ≈2.25 million vendors and more than $30 billion in sales a year. Other counts run from 2,500–3,000 to 5,000 markets, and one outlier puts sales at ≈$5 billion [7][8][9][10]. IBISWorld estimates ≈$36.7 billion in 2024 revenue across ≈511k "businesses" (mostly sole-trader vendors). It describes the industry as highly fragmented, with no firm holding more than 5% [6].
- **Stall rent is cheap.** An outdoor space costs ≈$12–$60 a day. Monthly reserved outdoor spaces cost ≈$75–$520. Indoor shops at big markets cost ≈$400–$1,900 a month [14][15][16][17][19][20]. Monthly rent usually comes to about 5–10 daily rents, so regulars get roughly a 30–60% per-day discount.
- **Sell-through is low.** In the one vendor survey found, 46% of vendors sell 25% or less of the stock they bring, and a similar share sell 26–50% [5]. Inventory rotates slowly, and leftover stock is the vendor's main problem.
- **Customers spend little.** About half spend under $30 a visit and about a third spend $30–50. Most visit 21 or more booths. Over three-quarters say "bargain hunting" is their main reason for coming. About 90% of buying happens between 8 am and noon [5].
- **Haggling is expected.** Sellers build in a "haggle factor." Normal discounts are 10–30% off the asking price. About 20–25% is a common ceiling before the seller is offended, with more off for bundles or late in the day [33][34].
- **Information drives prices.** Geertz's bazaar model holds that information is poor, scarce, unevenly spread and highly valued. Two mechanisms manage it. *Clientelization* means repeat buyer-seller pairs. *Intensive bargaining* means probing one offer in depth rather than collecting many quotes [1].

---

## 1. Vendor economics

### 1.1 Stall rents: concrete published rate cards

**Shipshewana Trading Place (Indiana)** [14]
- Season and days: May–September, Tuesdays and Wednesdays.
- Space: ≈25 ft × 20 ft with a 20 A outlet.
- Daily and weekly: $45 a day or $65 a week.
- Monthly: $207–$242 depending on location, plus a $90 deposit.
- Holiday and "extended" dates: $27.50 a day extra.
- Vendors must show an Indiana Retail Merchant Certificate.

**Columbus Farmers Market (Columbus, NJ)** [15]
- Space: 12 × 30 ft, and the vendor's vehicle stays in the space.
- Used goods are charged less than new or mixed goods on Thursdays and Sundays:

| Day | Daily (used / new) | Monthly | Pavilion (monthly) |
|---|---|---|---|
| Thursday | $30 / $40 | $80 / $100 | $125+ plus deposit |
| Saturday | $30 | $75 | $80 |
| Sunday | $35 / $45 | $100 / $120 | $150+ plus deposit |

- Monthly vendors pay cash or check in advance; no cards.
- Photo ID is required.
- Counterfeits are banned, and brand-owner investigators work on site. Louis Vuitton goods are banned outright.

**Jamie's Flea Market (Amherst, OH)** [16]
- Open year-round, Wednesdays and Saturdays, 8 am–4 pm. Shoppers pay no admission or parking.
- Indoor spaces: $35–$36 a week. Rent is due each Wednesday, with a $20 late fee. Booths must be open every market day or the vendor may be fined.
- Outdoor reserved spaces: $15 a day, billed monthly, May–September.
- Outdoor first-come spaces: $12 front row, or $15 Wednesday and $17 Saturday.
- Winter rate: $5 a space.
- One-day indoor "pop-up" space: $20.
- Food concession fee: $25.
- Banned items include firearms, ammunition, fireworks, live animals, pornography, and Nazi or Confederate emblems.

**Mile High Flea Market (Denver)** [17]
- Outdoor 12 × 25 ft space: $20 Friday, $40 Saturday, $44 Sunday; reserving adds about $3. Weekly: $102, or $120 for a corner.
- Monthly outdoor: $444, or $522 for a corner, which also needs an annual bid fee.
- Indoor shops a month: studio $405, one door $509, two doors $856, three doors $1,128–$1,261, four to five doors $1,505–$1,880.
- Add-ons: table $5 a day, electricity $5 a day, storage container $160 a month, vehicle storage $85 a month, "facilities charge" $5 a day.
- "Service seller" (services rather than goods) pays $10 Friday, $30 Saturday, $60 Sunday.

**Other markets** [snippet]
- Beach Blvd Flea Market, Jacksonville: $42 a day for 10 × 10 ft with a table; $450 a month for 10 × 20 ft [19].
- Sacramento-area market (sjfm.com): $35 Saturday and $40 Sunday; $335 a month for weekends only [20].
- Great Smokies Flea Market (Tennessee): outdoor $15–$25 a day; indoor $75+ a weekend [21].
- Webster Westside (New York): $25–$40 a day [snippet].

**First Monday Trade Days, Canton TX** [11][12][13]
- Several rental tiers:
  - Civic Center (antiques only): monthly, 10 × 10 ft $125, 10 × 12 ft $150, 10 × 14 ft $175 [snippet].
  - Trade Center: monthly, ≈$175–$265, application only [snippet].
  - Dry Creek Landing: annual lease only, and the vendor must open every First Monday weekend.
  - Outdoor and unreserved lots: first come, first served.
- A main-building booth cost about $200 a weekend in 2014 [11].
- Renewal fees: ≈$30 per space per weekend for pre-reserved vendors and $10 for an absentee roll-over [snippet; from a Weatherford TX document].
- A Texas Sales Tax Permit is required.

**Other sources**
- A 2026 price guide gives typical US ranges of ≈$20–100 a day, $50–250 a weekend, $100–400 a week and $300–1,000+ a month [18, snippet].
- An encyclopedia entry gives ≈$10–20 a day as typical in the 1990s [49].
- A popular-press summary says high-end daily rates up to ≈$100 usually apply to permanent vendors selling new goods [10, snippet].

**Pattern for the game.** Rent tiers are:
1. Unreserved, first-come daily.
2. Reserved daily, with a small premium.
3. Weekly.
4. Monthly or seasonal reserved.
5. Annual lease or lock-and-leave indoor shop.

Corner and front-row spaces cost extra. Some markets charge new-goods vendors more than used-goods vendors. Services, food and electricity are priced separately. Regulars must show up every market day or lose the space.

**Antique malls (consignment-style indoor booths)** [37, anecdote and blog]
- Rent: ≈$100–600 a month. An open shelf costs $50–75; a locked case costs $150–200.
- Commission on sales: usually 5–10%, up to about 15%.
- Card-processing fee: ≈2.6–5%, sometimes added on top of the commission for a 13–15% effective cut.
- Many dealers report sales barely covering rent. In one contested forum post, a 550-seller mall averaged ≈$2,181 a year in sales per seller, about $182 a month.

### 1.2 Markups and margins by category

| Category | Typical sourcing cost | Typical asking price | Notes |
|---|---|---|---|
| Garage-sale-sourced used goods | Garage sales price at ≈10–30% of original retail (25–30% if good condition, ≈10% if fair or poor) [41] | Resold at ≈2–3× cost | Thin per item; volume and luck matter |
| Thrift "flips" (clothing, housewares) | Rule of thumb: pay ≤15–25% of expected sale price, i.e. a target ≈3× multiple [42, blogs] | 3×+ | At low price points, labor wipes out profit: $3 → $14 nets ≈$0.64 after costs; $12 → $68 jacket nets ≈$36 (54%) [42] |
| Liquidation and returns pallets (new goods) | ≈20–50% of stated retail; ≈25¢ per retail $ is common [38] | Realised resale ≈25–50% of stated retail | Sellable share ≈80–90% (new), 60–80% (returns), 40–60% (salvage). Need ≥30% of retail to profit [38] |
| Storage-unit auctions | Winning bid ≈$75–425, average ≈$300 [39] | Highly variable | The highest-variance channel. Many units hold nothing of value. Cleanout deadlines apply [39] |
| Estate-sale leftovers and buy-outs | Estate companies take ≈30–40% (range 20–50%) commission on gross. Minimum estate ≈$5–10k [40] | Dealers buy early at the sale and resell | Professional "pickers" arrive at opening |
| Antiques and collectibles | Bought from estates, auctions and other dealers | Negotiated discounts ≈10% off ask [33] | Wide information gaps produce big wins (Brimfield: a $25 box of cameras held one camera worth ≈$2,000 [23]) |
| New wholesale goods (socks, phone cases, tools, imports) | Wholesale or closeout | Keystone (2× wholesale) is the retail norm [43] | The indoor swap-meet model. Margins described as "razor-thin" because of competition [26] |
| Handmade and crafts | Cost of goods = materials + labor + overhead | Wholesale = 2× cost; retail = 2× wholesale, i.e. 4× cost [43] | Many makers underprice by leaving out labor [43] |
| Food | Food cost ≈28–35% of revenue [44] | — | Net margin ≈5–15%. Event commissions of 10–25% of gross are common at festivals [44] |

### 1.3 Sourcing channels

These are confirmed across the sources:
- garage and yard sales [41];
- estate sales [40];
- storage auctions [39];
- thrift stores [42];
- liquidation and returns pallets and closeouts [38];
- bankruptcy stock (Swedish example: a couple touring markets with a bankrupt firm's wool caps "did good profit") [4];
- downtown wholesale districts, the main source for LA indoor swap meets [25][26];
- import networks: Korean vendors' Asia trade links brought new cheap imports [25];
- handmade goods [43];
- commission or direct-sales products (teens selling cosmetics on commission) [4];
- one's own household clear-out: downsizing and decluttering is a named driver of supply [5].

Origin story: the term "flea market" comes from Paris's *marché aux puces*. Chiffonniers (rag pickers) combed through refuse for items to resell [5][49].

### 1.4 Cash vs card

- Flea markets have historically been cash-heavy. Operators often take rent in cash or check only [15]. Rose Bowl admission is "cash only, exact change" at the gate [22].
- Card acceptance is spreading. Square readers charge ≈2.6% + $0.10. A Chattanooga market reports the move from cash to "customers expect cards universally" is "largely complete" [45, anecdote]. Some organizers list cash, cards, Venmo, Apple Pay and PayPal QR codes [45].
- Game hook: cash supports informality (unreported sales) and haggling ("cash price"). Cards create a paper trail and a ≈3% fee.

### 1.5 Haggling norms

- Sellers expect to haggle and build in a "haggle factor." Paying the sticker price means overpaying [34, snippet].
- Discounts reported by sources:
  - Flea markets and garage sales: "a few dollars to 30% off" [33].
  - Vendors call 20–25% off reasonable; more than that offends [34, snippet].
  - Dutch flea-market guide: 10–20% [34].
  - Antiques and art: about 10% [33].
  - Used books: 10–20% on items over $100 [33].
  - Pawn shops: 10–15%, or about 25% for stale or scuffed items [33].
  - Oriental rugs: 20–30%, up to 50% (markups of 10% to 2,000%) [33].
- Discounts grow with bundling (15% off two items, 20% off three) and near closing time, when vendors don't want to repack stock [34].
- Survey attitudes [5]:
  - 36% of vendors strongly agree they'd rather take goods home than sell below cost.
  - 43% of customers would rather walk away than overpay.
  - About a third of customers "will continue to negotiate until I make a purchase."
- An economist's view on why fixed-price retail rarely haggles: "Bargaining takes time, and time is a resource we value highly" (Chamlee-Wright) [33].

### 1.6 Sales tax, licences and regulation

- **California.** CDTFA can require swap-meet operators to verify each vendor's seller's permit, or to collect a written statement that the vendor sells nothing taxable, before renting space. It can also demand vendor lists up to three times a year (Revenue & Taxation Code §6073). Operators keep the records for four years. Exempt sellers include occasional sellers and sellers of non-taxable goods (Publication 111) [35].
- **Texas.** The occasional-sale exemption does **not** cover flea markets or similar third-party events where the seller pays a fee [36]. The occasional-sale tests:
  - one or two taxable items in any 12-month period; or
  - personal-use items up to $3,000 in a calendar year.
- **Texas promoters.** A 1990 Comptroller ruling treats flea-market promoters as responsible for tax on sales by vendors who lack permits [36]. Permits are free [36].
- **Other states.** Indiana requires a Retail Merchant Certificate [14]. Canton requires a Texas Sales Tax Permit [12]. Britannica notes some states require a seller's permit or licence [7].
- **Vendor attitudes.** Only 2.5% of vendors (and 9.7% of customers) strongly agree that a licence should be required to sell at flea markets [5].
- **Counterfeits.** Counterfeit "gray market" goods (sunglasses, watches, T-shirts) are officially banned but common [49]. Brand investigators patrol some markets [15]. An NFMA executive director said there are "no agencies or regulations in place to police" flea markets; markets are self-regulated [66, snippet].

### 1.7 Informal and grey economy

- The flea market is a textbook site of the *informal economy*. Portes, Castells & Benton (1989) define this as income generation unregulated by the institutions of society, in a setting where similar activities are regulated [51]. Hart (1973) coined "informal income opportunities" from fieldwork with migrants in Accra and distinguished legitimate from illegitimate informal income [52].
- Grey elements include:
  - cash sales below the tax threshold, or unreported;
  - unpermitted occasional sellers;
  - counterfeit goods;
  - stolen-goods fencing, which markets explicitly ban [49];
  - unlicensed food.
- Morales argues that the standard formal/informal split is analytically flawed. In his account, Maxwell Street vendors mixed licensed and unlicensed, new and used, full-time and part-time trade [32].

### 1.8 Who the vendors are

- **Main motive is extra income.** In a southeastern US survey, 75% of vendors gave "additional income" as their main reason and 18% gave socializing. Over three-quarters had vended for fewer than 8 years, which points to high churn. 58% rent weekly and 42% monthly [5].
- **Two logics.** In a Gothenburg flea market, about half the vendors were temporary, there for a weekend or a single day. The rest were permanent, renting for the season [4]. The researchers saw two "logics":
  - *Scarcity*: people selling to pay for food and rent. Example: an elderly Venezuelan ex-shopkeeper supplementing a meagre pension. Permanent vendors complained that temporary vendors were "dumping prices." Their own stock rotated slowly ("the same objects week after week"), which made their stalls less attractive to regular bargain hunters.
  - *Entrepreneurship and leisure*: people selling for fun, sociability and a small profit, dreaming of "their own little shop" [4].
- **Professionals and pickers.** Antique dealers and pickers buy at dawn at the big shows. Brimfield has more than 20 shows over six days, some fields with 400+ dealers, and a "Dealer's Choice" opening where dealers flock early [23][24].
- **Immigrants and minorities:**
  - Maxwell Street (Chicago) was started by Jewish peddlers in the 1870s. By the 1990s it was a multiethnic market dominated by Black and Latino vendors with ≈340 (winter) to 850 (summer) vendors, or "1,000-vendor" Sundays, and more than 20,000 shoppers on good days [28][29].
  - Latino immigrants reshaped Southern California swap meets in the 1970s into tianguis-like markets [25][26].
  - Korean immigrant investors opened over 100 indoor swap meets in LA between 1983 and 1992, mostly in Black and Latino neighbourhoods, funded by Koreatown banks and Korean-language newspapers [26][27, snippet]. The first is credited to Seung-hyun "Johnny" Choi in November 1983, in a former car showroom [26].
  - Today's Latino *pulgas* (flea markets) are large. La Pulga de Alamo (Texas) covers ≈70 acres with ≈1,500 vendors [58]. Ledesma & Giusti studied four Latino flea markets and swap meets (198 surveys) and stress economic activity, sociability and place attachment [57].
- **Retirees and hobbyists.** These are widely reported but not quantified in the sources. The encyclopedia entry says "true" flea-market vendors are usually people earning extra money, not professional dealers [49].

### 1.9 Daily revenue and profit

- **Gross sales targets.** A popular-press guide (Entrepreneur) says aim for ≈$300–500 a day in gross sales [10, snippet]. Low-quality content farms repeat "$200–500 a day after costs" [anecdote, not reliable].
- **Successful full-timers.** Some Maxwell Street merchants made $800–1,000 in a single day as their livelihood. Some put children through private school and bought buildings (Morales) [29].
- **Antique-mall vendors.** Many barely cover rent [37].
- **Model for the game.** Daily profit = sales − rent − cost of goods sold − transport and fees. With 25–50% sell-through [5] and cost of goods at ≈30–50% of price, a casual vendor at a $30–45 space might clear ≈$50–200 a day [approx].

### 1.10 Turnover and churn

- More than 75% of vendors have vended for fewer than 8 years [5].
- About half of vendors are temporary on any given weekend [4].
- Markets lower fees when occupancy falls below 50% and offer free first months to disadvantaged newcomers (proposal for the New Maxwell Street Market) [30].
- Operators enforce attendance for reserved spaces, with fines or loss of the space [12][16].

---

## 2. Operator economics

### 2.1 Revenue mix

- **Vendor rent (dominant).** Daily, weekly, monthly and annual tiers, as in §1.1.
- **Add-on fees** [17]:
  - table rental, ≈$5 a day;
  - electricity, ≈$5 a day;
  - storage containers and vehicle storage, $85–200 a month;
  - "facilities" fees;
  - corner premiums and annual bid fees for prime spaces;
  - space-change fees;
  - late fees [16];
  - renewal and roll-over fees [11].
- **Admission.** Many markets are free [16][46]. Big destination markets charge. The Rose Bowl charges ≈$10–15 general admission and ≈$20–22 for VIP early entry from 5 am to 8:30 am [22]. Brimfield charges $5–10 only on opening day or for the first hours of paid fields [23][24].
- **Early-buyer premium.** Operators sell the dawn hours to dealers. This turns information advantage into revenue [22][24].
- **Parking.** $5–20 a car. At Canton, parking was $5 a car in 2007, and some neighbouring farms turned into parking lots that reportedly earned more than farming [11]. Brimfield charges $5–20 [23].
- **Concessions and food vendor fees** [16], **events** (Maxwell Street blues [28]), and anchor-tenant indoor shops [17].
- **Municipal case.** Canton's city-run market brought in enough that the town levied no city property tax until 2006 [11].

### 2.2 Scale, occupancy and waitlists

| Market | Scale |
|---|---|
| Traders Village (Grand Prairie TX) | ≈3,500 vendors every weekend (2014) [64] |
| Canton First Monday | ≈100+ acres, ≈6,000 vendors, up to 100,000 shoppers a weekend [11] |
| Kobey's (San Diego) | 1,000+ vendors Friday to Sunday [48] |
| La Pulga de Alamo (Texas) | ≈1,500 vendors [58] |
| Maxwell Street (Chicago) | 340–850 vendors [28] |

- A 2006 figure, cited secondhand, gives an average of ≈900 vending spaces per market across ≈2,500 US markets [5, citing Laibman 2006].
- Occupancy is seasonal. Maxwell Street's winter vendor count was ≈40% of its summer count [28]. Northern markets close or shrink in winter; southern markets sometimes close in midsummer [49]. Off-season pricing reflects this, such as Jamie's $5 winter rate [16].
- Waitlists. Prime reserved spaces are rationed:
  - First Monday Civic Center tenants get "first option to renew" [12].
  - Corner spaces require an annual bid [17].
  - Monthly regulars hold fixed spaces for the season [16].
  - Formal waitlists were not documented in the sources.

### 2.3 Land use

- Drive-in theatres rented their lots to daytime swap meets as movie revenue fell [25]. Examples:
  - The Roadium (Torrance) drive-in has hosted a swap meet since about 1955 [48].
  - Kobey's began in 1976 at the Midway drive-in, then moved to the Sports Arena parking lot [48].
- Other venues: fairgrounds, race tracks, parking lots [49]; farmland and county-court-day grounds (Canton grew out of 1850s horse-trading court days) [11]; and vacant retail space (LA indoor swap meets in old showrooms and department stores) [25][26].

### 2.4 Costs

The sources give no detailed cost breakdown. IBISWorld's summary says profit rose as revenue outpaced labor costs [6]. Typical cost lines include:
- land (rent or opportunity cost);
- restrooms, trash and sanitation;
- security and an on-site official;
- insurance;
- advertising;
- electricity.

Survey respondents want restrooms checked every two hours, better lighting, cleaner facilities, an official present and more advertising [5]. Chicago's withdrawal of toilets and trash pickup in the 1980s left vendors to handle sanitation themselves [28].

### 2.5 Why markets close

- **Land value is the main documented cause.**
  - Pecan Park Flea Market (Jacksonville, ≈40 years) sold its 20 acres for $8.55 million to become a car dealership. It closes in September 2026; vendors were notified by letter on their stall doors [46].
  - Azalea Flea Market (Richmond) sold its land for $8 million in January 2025 to a data-centre developer [47].
  - Maxwell Street lost its land to University of Illinois expansion in 1994 [28][30]. The Morales, Balkin & Persky (1995) study estimated the closure would cost vendors, customers and nearby businesses $49.3 million over seven years [31][28].
- **Online marketplaces and big-box retail** (Facebook Marketplace, Craigslist, OfferUp, eBay) are cited as competitive pressure [5][6]. I found no reliable source tying a specific closure to e-commerce.
- **Counter-trend.** Recessions and the post-COVID period push more people to buy cheaply or sell for extra income [6][29].

### 2.6 NFMA and industry figures

| Figure | Source | Note |
|---|---|---|
| ≈1,100 markets, 2.25 million vendors, >$30 billion a year | NFMA, via press [7][8][9] | Placer.ai observed in 2023 that these were the same statistics NFMA gave in 2019 [8, snippet] |
| ≈5,000 markets, $36.1 billion industry | NFMA member, via Axios 2023 [9] | |
| ≈2,500 regular markets × ≈900 spaces, ≈80,000 employed, ≈$30 billion | Laibman 2006, cited in [5] | |
| 2,500–3,000 weekly markets, ≈$5 billion | Older NFMA president quote [10] | Outlier |
| $36.7 billion (2024), ≈2.3% CAGR over five years, ≈511k businesses | IBISWorld [6] | |
| 237 public markets in 128 US cities in 1920; "peddler" a census occupation up to 1940 | Morales [29] | Historical |

---

## 3. Customer behaviour

### 3.1 Spend per visit

- 48.6% spend under $30 and 37.5% spend $30–50; implied average ≈$30–35 [5]. That survey had 70 customers, so it is small.
- Farmers-market comparison: ≈$55 average spend per visit in a 2023 British Columbia impact study [69].

### 3.2 Search breadth and dwell time

- 62.5% of customers visit 21 or more booths per visit [5].
- No published dwell-time figure was found. At about 1–3 minutes per booth, a 21+ booth visit implies ≈1–3 hours on site [approx].
- At Brimfield, buyers spread multi-day trips across 20+ shows [23].

### 3.3 Timing

- 95% of vendors and 90% of customers say most business happens 8 am–noon [5].
- Preferred opening hours: about 6 am to 1–4 pm [5].
- Dealers and serious buyers arrive at dawn or before, with flashlights at outdoor antique fields. Operators monetise this with VIP early entry from 5 am at the Rose Bowl [22][24].
- Selection "dwindles as the week goes on" [23].
- Late-day buyers get better haggles because vendors don't want to repack [34].

### 3.4 Motives

- **Bargain hunting** is the main motive for more than 75% of customers [5].
- **The treasure hunt.** Customers describe a "game of discovery" in a labyrinthine layout: thrift, bargains, "hunting for precious vintage" [4]. Sherry calls this festive, sensory quality "ambience" [2][4]. Pasadena press: "the hunt is the point" [22].
- **Sociability.** Markets are prized as places to mix with diverse people. A Maxwell Street shopper called it "one of the few places left in the city where I can mix with" other ethnicities [28]. A working-class shopper: "the working man can't afford the stores" [28]. UK car-boot research found bargaining doubles as socializing [56].

### 3.5 Shopper typology

- A factor analysis cited in [5] (Petrescu & Bhatli 2013) found shopper groups including value-oriented, variety-seeking, quality-oriented, convenience and recreational shoppers.
- UK car-boot buyers [56, secondhand blog summary]:
  - 40% employed, 16% part-time, 21% retired;
  - two-thirds aged 25–55;
  - an even gender split;
  - children's clothes the most popular purchase;
  - some buy to resell: baby equipment, videos, kitchenware, DIY tools.

### 3.6 Catchment and loyalty

- 76% of customers travel under 20 miles. Vendors come from further away, and 6% travel more than 60 miles [5].
- One in four customers has attended for 9–12 years [5].
- Big destination markets draw regionally: Canton from Texas, Oklahoma and Arkansas [11].

### 3.7 What buyers want

Vendors and customers agree the most sought-after categories are antiques (31% / 29%), clothing (23% / 28%) and tools (20% / 19%) [5]. About a third of vendors sell mostly new merchandise, while almost half of customers buy mostly new [5].

---

## 4. Market effects

### 4.1 Price formation without posted prices: Geertz's bazaar economy [1]

Geertz, "The Bazaar Economy: Information and Search in Peasant Marketing," *American Economic Review* 68(2), 1978, pp. 28–32. Fieldwork in Sefrou, Morocco, a town of 15,000–30,000 people with:
- a permanent bazaar of 600+ shops in ≈40 trades and ≈300 workshops in ≈30 crafts;
- a Thursday periodic market during which the town's population roughly doubles;
- two-thirds of the town's labor force employed in the bazaar.

Key concepts:

- **Information is the scarce good.** "In the bazaar information is poor, scarce, maldistributed, inefficiently communicated, and intensely valued." There is no advertising, no product standardisation and no fixed exchange partners. Ignorance about quality, going prices and costs is "very high," and the bazaar works by trying to "reduce such ignorance for someone, increase it for someone, or defend someone against it."
- **Known ignorance.** Participants know they don't know whether "a cow is sound or its price right." The game is "the search for information one lacks and the protection of information one has." Capital and skill pay off mainly by securing "an advantaged place in an enormously complicated, poorly articulated, and extremely noisy communication network." The main problem "is not balancing options but finding out what they are."
- **Linked features.** Extreme division of labor and localisation, heterogeneous products, intensive bargaining, small fragmented transactions, stable clientship, itinerant trading and hereditary occupations "imply one another."
- **Clientelization.** Repeat buyers form continuing relationships with particular sellers instead of searching widely each time. The relationships are "symmetrical, egalitarian, and oppositional": not patronage, but "familiar antagonists." They cut search costs and make search cumulative. Spatial and ethnic clustering of trades helps, because you know where to look and the seller "is going to be there for awhile."
- **Bargaining is multidimensional.** Besides price, buyer and seller can adjust quantity, quality, credit and bundling or splitting, "to an astonishing range and level of detail," where "little is packaged or regulated, and everything is approximative."
- **Bargaining is intensive, not extensive.** Following Rees [70]:
  - Intensive search explores one offer in depth; extensive search collects more quotes.
  - The bazaar is like a used-car market, with heterogeneous goods, not a new-car market. So "asking a large number of diagnostic questions of a handful of people" beats surveying many.
  - Bazaaris distinguish bargaining to test the waters, done with weak ties, from bargaining to close, done with firm clients.
  - Shops at the bazaar's edge are "rich in bargaining but poor in selling" (Khuri on Rabat [63]).
- **Bottom line.** "Most bazaar 'price negotiation' takes place to the right of the decimal point. But it is no less keen for that." Haggling margins are small relative to price, but intense.

**Design translation:**
- Each NPC carries a private estimate of value with noise.
- Asking prices are anchored high.
- Repeat dealings with the same vendor (client status) lower search cost and give better information and terms.
- Some vendors and edge stalls are "browse" stalls.
- Players can trade non-price terms: bundles, credit, "throw in X."

### 4.2 Bargaining theory and anchoring

- **First offers anchor.** Whoever makes the first offer, buyer or seller, tends to get the better outcome, and the first offer strongly predicts the settlement. The effect shrinks when the other side focuses on information that contradicts the anchor (Galinsky & Mussweiler 2001) [55]. *Implication:* vendor asking prices anchor buyers; buyers who open low pull the deal down.
- **Alternating offers.** Rubinstein's (1982) model: with impatience (discounting), the deal is struck immediately, and the more patient party gets more [61, mem]. *Implication:* tie patience to time of day. Vendors grow impatient near closing; dawn dealers are impatient to beat competitors.
- **Split the difference.** The Nash bargaining solution with equal power splits the surplus evenly. That fits the "meet in the middle" convention, also used in used-car advice [33].
- **Lemons.** Quality uncertainty (Akerlof 1970 [62], cited by Geertz) drives down prices for unverifiable goods. *Implication:* vendor reputation and the chance to inspect raise prices.
- **Experience removes the endowment effect.** List (2003) found at sportscard shows that experienced dealers and traders (≈6+ trades a month) show no significant endowment effect: no over-valuation of what they own. Novices do [53]. *Implication:* casual sellers overprice their own stuff; professionals price to move. This matches the Swedish complaint that permanent vendors' stock sat for weeks while temporary sellers "dumped prices" [4]. The original endowment-effect result is Kahneman, Knetsch & Thaler (1990) [65, mem].
- **Welfare of haggling.** Keniston's structural study of autorickshaw fares in Jaipur, India (2008–09) weighs bargaining as cheap price discrimination against the time and utility cost of haggling versus fixed prices [54].
- **Price dispersion.** In Mexico City craft markets, an unwary customer can pay ≈30% more for the same item at one stall than another [snippet, CSM 1987]. Cassady (1968) on negotiated pricing in Mexican markets is a classic source (as cited by Geertz) [63].

### 4.3 Reputation networks and repeat customers

- Clientelization [1].
- Permanent stalls with fixed locations let repeat customers find vendors again. Monthly rent buys a fixed space, and keeping a space is a reputational asset [12][16].
- Vendors and customers report mutual satisfaction with each other's attitudes: 68% of vendors and 47% of customers strongly agree [5].
- Belk, Sherry & Wallendorf's (1988) swap-meet study identifies four dialectical tensions: freedom vs rules, boundaries vs transitions, competition vs cooperation, and sacred vs profane [3]. Vendors compete for the same buyers but cooperate on watching stalls, sharing information and socialising.
- The Swedish ethnography shows vendor-to-vendor social support for those selling out of necessity [4].

### 4.4 Incubator for small business

- Morales calls markets "living laboratories" and a "socioeconomic interface, where people can incorporate themselves." Low entry barriers let immigrants and poor people test ideas. Ron Popeil and Phillips-Van Heusen trace roots to street markets [29].
- Balkin's "ladder" [30]:
  1. pack;
  2. push cart;
  3. table;
  4. shed;
  5. storefront;
  6. multiple stores.
- The Maxwell Street benefits study counted [30][31]:
  - vendor income;
  - consumer surplus;
  - businesses incubated outside the market;
  - reduced criminal-justice contact;
  - youth learning (children working alongside parents);
  - multiplier effects on wholesalers (several closed when the market moved);
  - cultural continuity.
- LA indoor swap meets offered cheaper rent than a storefront and appealed to independence-seeking immigrants [25][26].
- The Swedish permanent vendors dreamed of "their own little shop" [4].

### 4.5 Ethnic economies and conflict

- The LA swap meet involved Korean owners and vendors, Latino customers and Mexican-themed visuals [26].
- Thin margins made vendors slow to hire locally, and job ads in Korean-language papers were seen by Black shoppers as exclusionary. This tension sat around the 1992 unrest [26][27].
- The indoor model differs from outdoor flea markets: open 6–7 days a week, booths leased monthly, new goods from downtown wholesalers [26].

---

## 5. Academic sources: summaries

- **Sherry (1990)** [2]. Ethnography of a Midwestern US flea market. It looks at buyer and seller behavior, marketplace "ambience," the social embeddedness and experiential side of consumption, and how informal ("secondary") economic activity relates to formal ("primary") activity. It frames the flea market as both festive and commercial, and a "natural laboratory." I read the abstract only.
- **Belk, Sherry & Wallendorf (1988)** [3]. A naturalistic inquiry at a swap meet, the pilot for the Consumer Behavior Odyssey. Methods include triangulation, member checks and auditing. Its themes are freedom/rules, boundaries/transitions, competition/cooperation and sacred/profane. It describes swap meets as "functional anachronisms" [4].
- **Maisel (1974)**, "The Flea Market as an Action Scene," *Urban Life and Culture* 2(4) [60, mem; I could not find it online]. Caudill & Slater confirm it is cited for the flea market as an "action scene," meaning a place where people go for excitement and the play of the deal [5].
- **Herrmann.** Gretchen M. Herrmann (SUNY Cortland) is the leading garage-sale ethnographer:
  - Verified: "Reminiscence and Recompense: Reuse and the Garage Sale," *Worldwide Waste* 2(1), 2019. Garage-sale goods carry memories and personal histories. Participants frame reuse as morally praiseworthy alongside earning cash and finding bargains [59].
  - From memory, unverified this session:
    - "Women's Exchange in the U.S. Garage Sale," *Gender & Society* 10(6), 1996.
    - "Gift or Commodity: What Changes Hands in the U.S. Garage Sale?," *American Ethnologist* 24(4), 1997.
    - Herrmann & Soiffer, "For Fun and Profit: An Analysis of the American Garage Sale," *Urban Life* 12(4), 1984.
  - The core argument as I recall it: garage-sale exchange mixes gift and market logic. Sellers give discounts to people they like and to "worthy" buyers, and pricing is moral as well as economic.
- **Morales**:
  - "Peddling Policy: Street Vending in Historical and Contemporary Context," *International Journal of Sociology and Social Policy* 20(3/4):76–98, 2000. It covers Chicago street vending history, vending as Progressive-Era unemployment relief, and its later regulation [32].
  - Morales, Balkin & Persky, "The Value of Benefits of a Public Street Market: The Case of Maxwell Street," *Economic Development Quarterly*, November 1995. Closure losses estimated at $49.3 million over seven years [31].
  - Morales & Kettles, "Zoning for Public Markets and Street Vendors," *Zoning Practice* 2009 [snippet].
- **Hansson & Brembeck (2015)**, *Culture Unbound* 7:91–121. Actor-network-theory ethnography of Kommersen, Gothenburg: labyrinth layout, temporary vs permanent vendors, the scarcity vs entrepreneurship logics [4].
- **Caudill & Slater (2022)**, *International Journal of Business and Administrative Studies* 8(4):193–206. Surveys of 40 vendors and 70 customers at southeastern US markets; source of most survey numbers here [5].
- **Ledesma & Giusti (2021)**, *Journal of the American Planning Association* 87(3):341–353. Latino flea markets and swap meets in California and Texas: economic activity, social interaction, physical setting, place attachment [57].
- **Stewart (2020)**, UC Berkeley dissertation, "Meet Me at the Swap Meet: Architectures of Emergent Citizenship in Greater Los Angeles, 1983–2020" [26].
- **Gregson & Crewe (2003)**, *Second-Hand Cultures* (Berg). Car-boot sales, charity shops and retro shops in the UK [56].
- **McGrath, Sherry & Heisley (1993)**, "An Ethnographic Study of an Urban Periodic Marketplace," *Journal of Retailing* (a farmers' market) [68, cited in 4].
- **Informal economy.** Hart (1973), *Journal of Modern African Studies* 11(1):61–89 [52]. Portes, Castells & Benton (1989), *The Informal Economy*, Johns Hopkins [51].
- **Periodic markets: Skinner (1964–65)**, "Marketing and Social Structure in Rural China," *Journal of Asian Studies* 24(1–3) [50]:
  - Applies Christaller–Lösch central-place theory.
  - Markets are periodic: about every 10 days in remote areas, up to every other day in busy places [50].
  - Each market town is the centre of a "standard marketing area," the peasant's real social world rather than the village.
  - Skinner counted ≈65,200 rural standard markets in China in 1948 [50].
  - From memory, approximate: a typical standard marketing area holds ≈18 villages and ≈1,500 households in a roughly hexagonal area. Markets meet on interlocking schedules within a 10-day cycle (for example days 1-4-7 and 2-5-8 of each 10-day *xun*), so itinerant traders can make a circuit of neighbouring markets [mem].
  - The same idea, an itinerant vendor rotating among periodic markets, appears in Geertz's Thursday market cycle [1] and in Canton's monthly calendar [11].
  - Design use: put markets on staggered days so traveling vendors can follow a weekly circuit.
- **Experimental and behavioral:** List (2003) [53]; Galinsky & Mussweiler (2001) [55]; Keniston (2011) [54]; Rubinstein (1982) [61, mem]; Akerlof (1970) [62]; Khuri (1968) "The Etiquette of Bargaining in the Middle East" and Cassady (1968) [63, as cited by Geertz].
- **Not found.** I could not locate anything on "Kathleen Petrovic" or "Ruth Mamelak" in connection with flea markets. They may be wrong names, so I've left them out. Jeffrey Pilcher writes on Mexican food history and markets but has no flea-market economics work that I found.

---

## 6. Balancing numbers for a game

All figures are in present-day US dollars and approximate. Scale them to your in-game currency.

### 6.1 Market sizes

| Market type | Vendors | Shoppers |
|---|---|---|
| Small weekly market | 30–150 | a few hundred to 2,000 a day |
| Mid regional market | 300–1,000 (Maxwell Street 340–850; Kobey's 1,000+) [28][48] | 5,000–20,000 a day |
| Mega-market | 1,500–6,000 (Pulga de Alamo, Traders Village, Canton) [11][58][64] | up to ≈100,000 a weekend [11] |

- Seasonality: off-season vendor count ≈40–60% of peak [28].
- Temporary vendors make up ≈50% of vendors on any given day [4].

### 6.2 Rent

| Space type | Rent |
|---|---|
| Unreserved outdoor daily | $12–45; weekend days 10–20% higher than weekdays [16][17] |
| Reserved daily | +$3–10 premium [17][20] |
| Monthly outdoor | ≈5–10× the daily rate (e.g. $75–120 at Columbus [15]; $207–242 at Shipshewana [14]; $444 at Mile High [17]) |
| Indoor booth | $35 a week (cheap rural) up to $400–1,900 a month (big-city indoor shops) [16][17] |
| Premiums and extras | Corner +$6 a day or +18% a month; electricity $5 a day; table $5 a day [17] |
| New-goods surcharge | +$10–20 a day versus used goods (Columbus) [15] |
| Rent as share of sales | At $300–500 gross a day [10] and $30–45 rent, rent ≈6–15% of gross. Antique-mall booths often run 30–100%+ of sales for weak dealers [37] |

### 6.3 Inventory and sell-through

- Fraction of brought stock sold per market day: 10–50%. Median vendor ≈25% [5].
- Cost of goods as a share of selling price by sourcing channel:

| Channel | Cost of goods / selling price |
|---|---|
| Garage-sale sourced | ≈20–40% |
| Thrift-sourced | ≈15–33% (target 3×) [42] |
| Liquidation pallets | ≈50–80% of realised resale (pay ≈25% of retail, realise 25–50% of retail) [38] |
| New wholesale | ≈50% (keystone) [43] |
| Handmade | ≈25% (4× rule) [43] |
| Food | ≈30% [44] |

- Storage-unit lottery: buy at $50–425 [39]. Contents are a wide random distribution: many units worth roughly nothing, rare ones worth 5–10× the bid [anecdote].

### 6.4 Prices and transactions

- **Typical customer budget:** about $15–60 per visit (median ≈$30) [5]. Model it as a log-normal distribution, with a few dealers spending hundreds to thousands.
- **Implied average transaction:** ≈$5–20 per item [approx], from ≈$30 spend spread over one to four purchases.
- **Typical used-good asking prices** [41][approx]: ≈10–30% of new retail. Examples:
  - clothing $1–10;
  - books and DVDs $0.50–3;
  - tools $2–25;
  - small furniture $15–75;
  - small electronics $5–40.
- **Antiques and collectibles:** a long tail from $5 to $5,000+.

### 6.5 Haggling model

- Asking-price inflation (haggle factor): +10–30% above the vendor's reservation price.
- Typical accepted discount: 10–20%. Ceiling ≈25–30% before the seller is offended and may refuse further talks [33][34].
- Bundle bonus: about +5 percentage points of discount per extra item (15% for two items, 20% for three) [34].
- Late-day bonus: +5–15 percentage points in the last 1–2 hours [34][approx].
- Category-specific discounts [33]:
  - antiques ≈10%;
  - pawn 10–15% (25% for stale items);
  - rugs and "tourist" goods 20–50%.
- First-offer anchor: whoever opens first pulls the settlement toward their offer [55]. A sensible rule is settlement ≈ midpoint of the opening offers, weighted by patience.
- Expertise: novice sellers overvalue their own goods (endowment effect). Professionals don't [53].
- Clientelization: repeat customers get a smaller haggle factor and better information about quality [1].

### 6.6 Time of day

- Dawn (5–8 am): dealers and pickers; best stock; paid early access ≈1.5–2× general admission [22].
- 8 am–noon: ≈90% of transactions [5].
- After noon: thin traffic, deeper discounts, vendors packing up.

### 6.7 Operator revenue sketch (example, 500-space weekend market)

- Rent: 500 spaces × 80% occupancy × $35 × 2 days ≈ $28,000 a weekend.
- Parking: 10,000 cars × $5 ≈ $50,000 a weekend if charged. Large markets often make parking and admission free to attract crowds.

Parking can rival rent, as the Canton farms that became parking lots show [11]. These are illustrative numbers.

### 6.8 Vendor archetypes to simulate

1. **Necessity seller.** Slow-moving stock, low prices, sells to pay rent [4].
2. **Hobbyist or declutterer.** Occasional, overprices sentimental items, sells for fun [4][59].
3. **Professional picker or dealer.** Buys at dawn and from estates and storage units; good information; prices to market [23][53].
4. **New-goods merchant.** Wholesale, closeouts and imports; keystone markup; monthly rent; thin margins [25][26].
5. **Maker.** Handmade goods at 4× cost [43].
6. **Food vendor.** ≈30% food cost; pays a concession fee [16][44].
7. **Grey-market seller.** Counterfeits or untaxed sales; risk of investigators and bans [15][49].
8. **Incubator climber.** Moves up the pack → cart → table → shed → storefront ladder [30].

---

## Sources

1. Geertz, C. (1978). "The Bazaar Economy: Information and Search in Peasant Marketing." *American Economic Review* 68(2):28–32. https://www.gwern.net/doc/economics/mechanism-design/1978-geertz.pdf
2. Sherry, J. F., Jr. (1990). "A Sociocultural Analysis of a Midwestern American Flea Market." *Journal of Consumer Research* 17(1):13–30. doi:10.1086/208533. https://academic.oup.com/jcr/article-abstract/17/1/13/1798516
3. Belk, R. W., Sherry, J. F., & Wallendorf, M. (1988). "A Naturalistic Inquiry into Buyer and Seller Behavior at a Swap Meet." *Journal of Consumer Research* 14(4):449–470. doi:10.1086/209128. https://academic.oup.com/jcr/article-abstract/14/4/449/1814958
4. Hansson, N., & Brembeck, H. (2015). "Market Hydraulics and Subjectivities in the 'Wild': Circulations of the Flea Market." *Culture Unbound* 7:91–121. https://cultureunbound.ep.liu.se/article/view/2151
5. Caudill, D. W., & Slater, P. J. (2022). "Flea Markets in a Digital Era: Entrepreneur and Consumer Viewpoints Toward the Marketing Mix." *International Journal of Business and Administrative Studies* 8(4):193–206. https://kkgpublications.com/wp-content/uploads/2023/03/ijbas.8.10002-4.pdf
6. IBISWorld. "Flea Markets in the US" industry summary. https://www.ibisworld.com/united-states/industry/flea-markets-in-the-us/6305/
7. Britannica. "Flea market." https://www.britannica.com/topic/flea-market
8. Placer.ai. "The 2023 Flea Market Bonanza" [snippet]. https://anchor.placer.ai/the-anchor/the-2023-flea-market-bonanza
9. Axios Chicago (2023). "New podcast wants to make flea markets sexy" [snippet]. https://www.axios.com/local/chicago/2023/07/02/clothing-swap-chicago-swaporama/
10. Entrepreneur. "It's a Swapping Success" [snippet]. https://www.entrepreneur.com/business-news/business-retail-business-its-a-swapping-success/77894
11. Wikipedia. "First Monday Trade Days." https://en.wikipedia.org/wiki/First_Monday_Trade_Days
12. First Monday Canton. "Become a Vendor." https://firstmondaycanton.com/become-a-vendor
13. First Monday Canton. "Civic Center" [snippet]. https://www.firstmondaycanton.com/civic-center
14. Shipshewana Trading Place. "Become a Vendor." https://shipshewanatradingplace.com/flea-market/become-a-vendor/
15. Columbus Farmers Market (NJ). "How to Become a Flea Market Vendor." https://www.columbusfarmersmarket.com/how-to-become-a-flea-market-vendor
16. Jamie's Flea Market (Amherst, OH). "Rates." https://jamiesfleamarket.com/sell/
17. Mile High Flea Market. "Pricing / Book Your Space." https://milehighfleamarket.com/sell/pricing-book-your-space/
18. EuroSaleOnline. "How Much Does a Flea Market Booth Cost? 2026 Price Guide" [snippet]. https://eurosaleonline.com/logistics/how-much-does-flea-market-booth-cost
19. Beach Blvd Flea Market (Jacksonville). "Vendors" [snippet]. https://jaxfleamarket.com/vendors/
20. sjfm.com. "How to Become a Vendor" [snippet]. https://sjfm.com/vendor-howto/
21. Great Smokies Flea Market. "Vendor Pricing" [snippet]. https://greatsmokiesfleamarket.com/vendor-pricing/
22. Rose Bowl Flea Market admissions: Colorado Boulevard listing (2026) https://www.coloradoboulevard.net/events/rose-bowl-flea-market-2026-05-10/ ; WhereIsTheMarket https://whereisthemarket.com/market/rose-bowl-flea-market-pasadena/ ; Pasadena Now, "At Today's Rose Bowl Flea Market, the Hunt Is the Point" https://www.pasadenanow.com/weekendr/at-todays-rose-bowl-flea-market-the-hunt-is-the-point/
23. WBUR (2026). "Brimfield antique flea market insider shopping tips." https://www.wbur.org/news/2026/07/10/brimfield-antique-flea-market-massachusetts-insider-shopping-tips
24. Antiques and the Arts Weekly. "Brimfield Heats Up for July Visitors" [snippet]. https://antiquesandthearts.com/brimfield-heats-up-for-july-visitors/
25. Wikipedia. "Indoor swap meet." https://en.wikipedia.org/wiki/Indoor_swap_meet
26. Stewart, A. R. (2020). *Meet Me at the Swap Meet: Architectures of Emergent Citizenship in Greater Los Angeles, 1983–2020*. PhD dissertation, UC Berkeley. https://escholarship.org/uc/item/18r0k0m7
27. Christian Science Monitor (1993). "For Korean Shopkeepers, Unrest Dims Prospects" [snippet]. https://www.csmonitor.com/1993/0331/31111.html
28. Christian Science Monitor (1993). "Chicagoans Aim to Save Outdoor Market." https://csmonitor.com/1993/1207/07081.html
29. University of Wisconsin News. "Street markets are this professor's laboratory" (Alfonso Morales). https://news.wisc.edu/street-markets-are-this-professors-laboratory
30. Balkin, S. "Increasing Youth Opportunities To Reduce Urban Violence by Promulgating Street Markets" (Roosevelt University blog). https://blogs.roosevelt.edu/sbalkin/?p=1124
31. Morales, A., Balkin, S., & Persky, J. (1995). "The Value of Benefits of a Public Street Market: The Case of Maxwell Street." *Economic Development Quarterly* (November). Via [28][30].
32. Morales, A. (2000). "Peddling Policy: Street Vending in Historical and Contemporary Context." *International Journal of Sociology and Social Policy* 20(3/4):76–98. https://emerald.com/insight/publication/issn/0144-333X/vol/20/iss/3/4
33. Learner, N. (2001). "'Is that the best you can do?'" *Christian Science Monitor*. https://www.csmonitor.com/2001/0423/p11s1.html
34. Haggling guides [snippet]: Consumerist (2011), "Tips on Haggling at the Flea Market" https://consumerist.com/2011/05/24/tips-on-haggling-at-the-flea-market/ ; Chairish blog https://www.chairish.com/blog/flea-market-haggling/ ; Wikivoyage, "Haggling" https://en.wikivoyage.org/wiki/Haggling
35. California Department of Tax and Fee Administration (CDTFA). Publication 111, "Operators of Swap Meets, Flea Markets, or Special Events" https://cdtfa.ca.gov/formspubs/pub111 ; Revenue & Taxation Code §6073 https://cdtfa.ca.gov/lawguides/vol1/sutl/6073.html
36. Texas Comptroller. Occasional-sale guidance https://comptroller.texas.gov/taxes/publications/94-437.php and https://comptroller.texas.gov/taxes/publications/96-211.php ; 1990 ruling 9008L1037E01 (promoter responsibility) https://ezel.ai/tax-rulings/tx/9008l1037e01-flea-market-trade-day-estate-sale-promoter-responsibilities
37. Antique-mall booth economics [anecdote]: Underpriced, "Antique booth rental selling guide 2026" https://www.underpriced.app/blog/antique-booth-rental-selling-guide-2026 ; Girl in the Garage https://girlinthegarage.net/2014/06/thinking-rent-booth-space-sell-goods/ ; Scavenger Life forum, "Crazy antique mall numbers" https://www.scavengerlife.com/forums/topic/crazy-antique-mall-numbers/
38. Liquidation pallets [promotional]: Closo, "Walmart Liquidation Sale" https://closo.co/blogs/inventory-liquidation/walmart-liquidation-sale ; Nexscope, "Amazon Liquidation" https://www.nexscope.ai/blog/amazon-liquidation-how-to-buy-return-pallets
39. Storage auctions: StorageCafe, "8 Storage Auction Myths Debunked" https://www.storagecafe.com/blog/?p=18635 ; Closo, "Bidding on Storage Units" https://closo.co/blogs/inventory-liquidation/bidding-on-storage-units
40. HomeLight. "What Is an Estate Sale?" (commissions). https://www.homelight.com/blog/what-is-an-estate-sale/
41. Garage-sale pricing: The Dollar Stretcher https://thedollarstretcher.com/frugal-living/how-to-price-garage-sale-items/ ; Clark.com https://clark.com/make-money/how-to-price-garage-sale-items/
42. Thrift flipping [blog]: ItemValueChecker https://itemvaluechecker.com/blog/how-to-price-thrift-store-finds ; Voolist https://www.voolist.com/blog/thrift-flipping-for-profit-guide
43. Craftybase. "How to Price Handmade Items" / "Pricing Handmade Products Wholesale." https://craftybase.com/blog/how-to-price-handmade-items
44. Food cost [blog]: Lunchbox, "What Are Food Costs for a Concession Stand?" https://integrations.lunchbox.io/what-are-food-costs-for-a-concession-stands ; Beancount, food-truck bookkeeping guide (2026)
45. Payments: Chattanooga Market vendor forum https://vendors.chattanoogamarket.com/t/credit-card-acceptance/1366 ; Artists & Fleas shopper FAQ https://www.artistsandfleas.com/shopper-faqs/ ; TechCrunch on Square at craft fairs https://techcrunch.com/?p=547951
46. News4JAX (2026). "Pecan Park Flea Market … closing this fall after selling for $8.55 million." https://www.news4jax.com/news/local/2026/06/08/pecan-park-flea-market-a-40-year-northside-jacksonville-landmark-is-closing-this-fall-after-selling-for-85-million/
47. Richmond Free Press (2025). "Azalea Flea Market closure marks end of an era." https://m.richmondfreepress.com/news/2025/feb/13/azalea-flea-market-closure-marks-end-of-an-era
48. San Diego Reader, "Kobey's Swap Meet" https://www.sandiegoreader.com/places/kobeys-swap-meet/ ; Drive-ins.com, "Roadium Drive-In Theater" https://drive-ins.com/wiki/catroad/roadium-drive-in-theater
49. Woloson, W. "Flea Markets." *St. James Encyclopedia of Popular Culture*, via Encyclopedia.com. https://www.encyclopedia.com/media/encyclopedias-almanacs-transcripts-and-maps/flea-markets
50. Skinner, G. W. (1964–65). "Marketing and Social Structure in Rural China," Parts I–III. *Journal of Asian Studies* 24(1):3–43; 24(2):195–228; 24(3):363–399. https://resolve.cambridge.org/core/journals/journal-of-asian-studies/article/marketing-and-social-structure-in-rural-china-part-i/20071250B7BC9B70B1C47DF11B608FCA ; secondary summary in *Erdkunde* https://www.erdkunde.uni-bonn.de/article/download/2286/2275/2289
51. Portes, A., Castells, M., & Benton, L. (eds.) (1989). *The Informal Economy: Studies in Advanced and Less Developed Countries*. Johns Hopkins University Press. Via https://en.wikipedia.org/wiki/Informal_economy
52. Hart, K. (1973). "Informal Income Opportunities and Urban Employment in Ghana." *Journal of Modern African Studies* 11(1):61–89. Via https://en.wikipedia.org/wiki/Keith_Hart_(anthropologist)
53. List, J. A. (2003). "Does Market Experience Eliminate Market Anomalies?" *Quarterly Journal of Economics* 118(1):41–71. Summaries: https://www.psychologicalscience.org/observer/economic-field-experiments ; https://www.economics.ku.dk/research/publications/wp/dp_2009/0904.pdf
54. Keniston, D. (2011). "Bargaining and Welfare: A Dynamic Structural Analysis" (autorickshaws, Jaipur). MIT working paper. https://dspace.mit.edu/handle/1721.1/65488
55. Galinsky, A. D., & Mussweiler, T. (2001). "First Offers as Anchors: The Role of Perspective-Taking and Negotiator Focus." *Journal of Personality and Social Psychology* 81(4):657–669. https://www.kellogg.northwestern.edu/faculty/research/detail/2001/first-offers-as-anchors-the-role-of-perspective-taking
56. Gregson, N., & Crewe, L. (2003). *Second-Hand Cultures*. Oxford: Berg. Review: https://epress.lib.uts.edu.au/journals/index.php/csrj/article/view/3506/3649 ; buyer figures via secondhand blog https://we-english.co.uk/blog/2008/07/21/car-boot-sales/
57. Ledesma, E., & Giusti, C. (2021). Latino flea markets and swap meets in California and Texas. *Journal of the American Planning Association* 87(3):341–353. https://ideas.repec.org/a/taf/rjpaxx/v87y2021i3p341-353.html
58. Boston Globe (2024). "Not your average flea market: At La Pulga de Alamo, stars are born." https://www.bostonglobe.com/2024/06/15/nation/not-your-average-flea-market-la-pulga-de-alamo-stars-are-born ; Texas Senate Resolution 69 https://capitol.texas.gov/tlodocs/89R/billtext/pdf/SR00069F.pdf
59. Herrmann, G. M. (2019). "Reminiscence and Recompense: Reuse and the Garage Sale." *Worldwide Waste* 2(1). https://www.whp-journals.co.uk/WW/article/view/1039 . Also from memory, unverified: Herrmann (1996), *Gender & Society* 10(6); Herrmann (1997), *American Ethnologist* 24(4); Herrmann & Soiffer (1984), *Urban Life* 12(4).
60. Maisel, R. (1974). "The Flea Market as an Action Scene." *Urban Life and Culture* 2(4) [mem; cited in 5].
61. Rubinstein, A. (1982). "Perfect Equilibrium in a Bargaining Model." *Econometrica* 50(1):97–109 [mem].
62. Akerlof, G. A. (1970). "The Market for 'Lemons'." *Quarterly Journal of Economics* 84(3):488–500 (cited in 1).
63. Khuri, F. (1968). "The Etiquette of Bargaining in the Middle East." *American Anthropologist* 70:698–706. Cassady, R., Jr. (1968). "Negotiated Price Making in Mexican Traditional Markets." *América Indígena* 28:51–79. Both cited in 1.
64. Sun Outdoors blog. "Visit Traders Village for the ultimate flea market experience." https://www.sunoutdoors.com/blog/visit-traders-village-for-the-ultimate-flea-market-experience
65. Kahneman, D., Knetsch, J., & Thaler, R. (1990). "Experimental Tests of the Endowment Effect and the Coase Theorem." *Journal of Political Economy* 98(6) [mem].
66. Dayton Daily News. "Flea markets a loosely regulated industry" [snippet; NFMA quote]. https://www.daytondailynews.com/news/local/flea-markets-loosely-regulated-industry/c5Ct3n8VXvQe2c82BV4rcP
67. (Number not used.)
68. McGrath, M. A., Sherry, J. F., & Heisley, D. (1993). "An Ethnographic Study of an Urban Periodic Marketplace: Lessons from the Midville Farmers' Market." *Journal of Retailing* 69(3) (cited in 4).
69. BC Association of Farmers' Markets (2024). *Impact Assessment: Cedar Farmers Market Final Report*. https://bcfarmersmarket.org/app/uploads/2024/03/BCAFM_23_Final_Cedar-FM-1.pdf
70. Rees, A. (1971). "Information Networks in Labor Markets." In Lamberton (ed.), *Economics of Information and Knowledge* (cited in 1).
