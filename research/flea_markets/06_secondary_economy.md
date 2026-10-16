# 06 The secondary economy: the flea market and the bazaar, melded

This is the synthesis of 03 (American markets), 04 (economics) and 05 (bazaar history) into the game's second economy,
and how it plugs into the existing code.

The user, 2026-10-15: "We will be melding the two and this will form the backbone of our secondary economy."

## 1. The idea
- **The primary economy is already canon.** The Draw guarantees food, a home, air, water, power and clothing. Wages
  are in Columbia dollars (C$). Shops buy from the Chutes and sell at posted prices (`research/bible/01_world.md:108-114`).
- **The second economy is everything that is not:**
  - used things, handmade things, salvage from the Drops;
  - farm surplus;
  - and the Skein's goods.
  - It trades **face to face at haggled prices, mostly in cash, on reputation**.
- **The weekend flea markets are its American face:**
  - Trader's World's indoor rows and Rogers' sheds and daily ring (03 §1, §15);
  - Shipshewana's seasonal leases (01 §3);
  - Kobey's mix of permanent and day sellers (01 §3).
- **The island bazaars are its old-world face:**
  - the caravan as a mobile market (05 §4);
  - the Champagne fairs' rotation and wardens (05 §7);
  - Geertz's information economy (04 §4.1, 05 §8);
  - the muhtasib (05 §8).
- **Where they meet, the island moors and the market becomes a fair.**
- **Why it matters on a generation ship:**
  - New goods are scarce. The Steward's Chutes ration complex things; the Panel Board rations LCD panels, "cars never"
    (`01_world.md:115`).
  - So **reuse, repair and resale are not a hobby, they are how the ship keeps things working**.
  - The flea market is where a part, a tool or a lamp finds its next owner.

## 2. What is traded (item categories)
Prices are C$ (≈ present-day US$; floor median wage ≈ C$ 41k, `research/lives/02_money.md:22`).
- **Typical:** the band most items fall in.
- **Haggle:** the asking-price inflation over the vendor's reservation price (04 §6.5).
- **Source:** where vendors get it (04 §1.3).

| category | typical C$ | tail C$ | haggle | source | scarcity note |
|---|---|---|---|---|---|
| used household (kitchenware, lamps, linens) | 1–15 | 60 | 15–25 % | clear-outs, estates | common |
| clothing, used | 1–10 | 40 | 15–25 % | clear-outs, thrift | common; the Draw's clothing stock is plain, so style sells |
| clothing, new / knitwear | 8–60 | 200 | 10–20 % | makers, islands | islander ganseys are prized |
| furniture | 15–90 | 600 | 15–30 % | estates, makers | bulky: a hauling job |
| tools and hardware | 2–30 | 250 | 10–20 % | estates, trades, Drops | steady demand |
| salvage and parts (Drops scrap, fittings, cells) | 1–40 | 400 | 20–35 % | Drops, wrecks, pickers | grey edge (§7) |
| electronics and repairs | 10–120 | **2,000** | 10–15 % | rare; Panel Board leakage | **the scarce class**: panels and boards; the warden watches it |
| books, media, maps | 0.5–5 | 300 (old charts, first-generation books) | 10–20 % | estates | collectors |
| antiques and heirlooms (Earth-made "launch goods") | 10–200 | **5,000+** | ~10 % | estates, families | the long tail; information gaps make big wins |
| collectibles (badges, tram tokens, Draw-day cards) | 1–30 | 500 | 10–20 % | collectors | |
| toys and games | 1–20 | 80 | 15–25 % | clear-outs, makers | |
| crafts | 5–80 | 300 | 10–20 % | makers (4x cost) | |
| produce, eggs, honey, meat | 1–12 | 40 | 5–10 % | farms | near-posted prices (staple) |
| plants and seedlings | 2–25 | 120 | 10–15 % | growers | |
| food, cooked | 3–12 | — | 0 % (posted) | food trucks | posted |
| **sky goods** | 5–150 | 1,500 | 15–30 % | islands only | snow and ice (a wonder), sky honey, mead, knitwear, rope, bells, lanterns, moss remedies, forecasts, air post |

- **Staples** (produce, cooked food) have near-posted prices and small spreads. **Unique goods** (antiques, salvage,
  electronics, sky goods) are haggled hard. This follows 05 §11.10: standardised goods are posted and unstandardised
  goods are bargained.
- **Each category has:**
  - a dressing list of kit pieces (`fm_goods_*`);
  - a condition range (poor/fair/good/fine) that scales the value ×0.3/0.6/1.0/1.6;
  - for some items, a **hidden true value** (§3.4).
- **Data:** `goods.json {category: {band, tail, haggle, sources, kit, staple, scarce}}`.

## 3. Price formation and haggling (the player's mechanic)

### 3.1 Every item has three numbers
- `V`: its true market value (category band × condition × hidden quality).
- `R`: the vendor's reservation price:
  - `V × k_vendor`;
  - k is 0.6–0.8 for a necessity seller, 0.9–1.3 for a sentimental hobbyist (the endowment effect: novices overvalue,
    04 §6.5), and 0.85–0.95 for a dealer.
- `A`: the asking price, `R × (1 + h)`, where h is the category's haggle factor ± the vendor's mood.

### 3.2 A haggle, in rounds (≤ 4)
- The player makes an offer `O`.
  - If `O ≥ A`, it is accepted (and the vendor thinks the player is a mark: the reputation for "easy" goes up).
  - If `O < R × 0.75`, the vendor is offended. Talks end and patience drops for the day (the 25–30 % ceiling, 04 §1.5).
  - Otherwise the vendor counters `C = A − (A − O) × s`, where s 0.3–0.5 is the vendor's patience.
- **Bonuses to the vendor's concession:**
  - a bundle: +5 percentage points per extra item;
  - late in the day (after 16:00, or on Sunday afternoon): +5–15 pp;
  - a regular (clientelization): the opening price drops by up to half of h;
  - paying cash vs card: +3 pp (card fees, 04 §1.4).
- **The vendor's opening anchors the deal.** If the player names a price first, the settlement moves toward it, but
  so does the risk of offence (04 §4.2).
- **Lexicon flavour:** islanders say "weigh it", and seal a deal with "cold hands".

### 3.3 Selling
- The same mechanic in reverse. Customers' budgets are log-normal with a median of C$ 30 a visit (04 §6.4).
- About 90 % of buying happens before noon (04 §6.6). In game time: 09:00–13:00 brings the trade, and afternoons
  thin out.
- **Sell-through:** 10–50 % of stock per day, median 25 % (04 §6.3), so stock turns slowly.

### 3.4 Information is the edge (Geertz)
- An item's `V` is only fully visible with **knowledge**: the category skill or a trusted vendor's word.
- **Extensive search** (asking many stalls) costs time. Market hours are scarce, at 2 real minutes a game hour.
- **Intensive search** (going deep with one vendor) works better with regulars.
- **The big win:** a box of junk with one treasure (Brimfield's $25 box with a $2,000 camera, 04 §1.2). There is a
  1-in-60 chance on estate lots.

### 3.5 NPC-to-NPC trades
- These are not simulated item by item.
- A stall's daily takings are drawn from its category, footfall and mode:

  | mode | stall gross |
  |---|---|
  | local weekend | C$ 150–500 a day (04 §6.2: rent ≈ 6–15 % of gross) |
  | island fair | ×1.6 |
  | after hours | 0 |

- Takings feed the vendor's `money_reasons` hooks (§10) through the journal only when the story asks.

## 4. Reputation and clientelization
- **Per player–vendor pair:** `trust` from −1 to 1. It rises with completed fair deals and repeat visits. It falls
  with offence, being caught in a bad-weight deal, or reneging on credit.
  - At trust ≥ 0.4 the player is a **client**: better first offers, first look at new stock ("I kept this back for
    you"), and honest grading.
- **Per player–clan (island):** `standing`, shared across the clan's islands. It spreads **with delay**: news travels
  only when islands lash (05 §11.9, the Maghribi coalition).
  - Cheat one Halyard stall at Kessler, and every McFadden stall knows by the next lashing.
- **Per market:** a public `name` (the warden's book): fines, disputes won and lost.
- **NPC vendors' reputations** are seeded per vendor (`honest 0.0–1.0`, hidden). Low-honesty vendors use short weights
  and pass off fakes, which the warden can catch (§5).

## 5. The market warden (the muhtasib / gardes des foires)
- **Each market has a market warden** (an occupation; posts in the market office, Fri–Sun plus island days). Each fair
  adds one **knot keeper** from the islands. Together they hold the **fair court** (piepowder: same-day justice,
  05 §7).
- **Duties:**
  - checking weights and scales (Weigh House calibration);
  - inspecting the scarce class (electronics, cells, Panel goods);
  - settling disputes;
  - fining short weight or fakes;
  - keeping the fire lanes clear;
  - assigning day pitches at dawn from the waiting list.
- **Mechanics:**
  - Patrols carry a detection chance against rigged scales and fakes.
  - **Penalties are public** (posted on the market board, a reputation hit visible to everyone).
  - The warden can be bribed: lower detection, but a scandal risk.
  - Disputes go warden → town magistrate.
- **Story:** the warden is a quest-giver for stolen goods, counterfeits and Panel leakage.

## 6. Credit and trust
- **Cash** is the norm. The Commons Bank's C$ notes and coins are the "cash price".
- **Tabs:** a vendor lets a client run a tab of up to C$ 50 × trust, due by the next market weekend.
- **Fair letters** (the bill of exchange, "payable at the next fair", 05 §8):
  - An island's **factor** sells a letter: pay C$ X now at Port Carrow, and collect goods or cash worth X × 1.04 at the
    clan's next mooring anywhere.
  - It is safe from theft and earns a little interest.
  - Risk: the clan's island might not come back for weeks.
  - The player can also **buy** goods on a letter, and must settle at the next mooring or lose standing.
- **Line Hall savings club** (the settled Aloft, 00 §9.4): a rotating savings and credit association. Members pay in
  weekly and take the pot in turn. It is open to the player at high standing.

## 7. The grey edge (the informal economy, 04 §1.7)
- Cash sales go unreported. That is tolerated: the Assembly taxes shops, not tables.
- **Salvage from the Drops** is legal if it is logged at the Drop's gate. Unlogged parts are grey.
- **Panel goods** outside the Panel Board's lists are illegal. That is the Marshals' line.
- **Counterfeit sky goods** (fake skeinfolk knitwear) bring the clans' anger and the warden's fines.
- **The player can deal grey.** The risk scales with the warden's patrols and the trust of the buyer.

## 8. Rotating periodic markets: the fair circuit
- **Every weekend:** all **22** markets run Fri–Sun, one in every town (the local weekly cycle, like Skinner's standard
  markets meeting on set days, 05 §6).
- **People circulate:** the weekend trips (00 §6.3) send ~6 % of adults to another town's market each market day, by
  gravity: stalls, distance² and each market's **draw** (07 §2).
  - Each market is known for something: Fenwick's books, Dunmore's Friday livestock auction, Cedar Ford's mill crafts,
    Kessler's tools and parts, Oceanview's toys and surf gear.
  - So goods and people flow along the circuit, as on Skinner's market rings.
- **The caravans:** islands visit by booking (00 §5.1): a city about 2 weekends in 5, a town 1 in 4, a village 1 in 7.
  On most weekends some market somewhere is an island fair.
- **The Great Fairs** (the Champagne cycle, 05 §7): one per city per year, staggered by season.

  | city | month | fair |
  |---|---|---|
  | Port Carrow | April | the Ropewalk Spring Fair |
  | Harrow Falls | June | **the Low Lashing** (the Lowliners' reunion) |
  | Solana Point | August | Starlite Midsummer Swap |
  | Kessler | October | Iron Wheel Harvest Trade Days |

  - In a Great Fair week: host p 1.0 and follower chain q 0.75, so about a third of Great Fairs become a Bright Week.
  - **Every town also has its own Market Day** once a year: a hashed weekend, host p 0.8, trip weight ×3. It is the
    town's pride.
- **Bright Week** (≥ 5 islands, ~20 a year on the map, about 5 a season):
  - the whole market opens every day, with an evening lantern market;
  - footfall ×2;
  - sky goods' prices soften ×0.9 (supply), while local crafts and food sell ×1.2 (demand);
  - the best week of a vendor's season, and when the player should rent a stall.
- **The Sky Holiday** (≥ 7 islands at a town or village, ~1.8 a year):
  - the district stops work and comes to the fair, and trippers come from 25 km;
  - footfall ×4; stall day rents ×2 (day pitches at the market office's discretion);
  - sky goods at their cheapest and the islands' rarest goods come down (snow and ice, bells, lark parts);
  - story and trade peaks: weddings, kin reunions, the year's big deals.
- **Phases within a fair:** the first day is the **goods** day. The last day is **settlement day**: fair letters and tabs
  fall due, and defaulters are banned from the next fair (05 §11.4).
- **Movers:** NPC dealers and pickers (archetype 3) and the player can ride the circuit. Buy at one town's market
  and sell at the next, where that category is scarce: sky goods sell ×1.3 where no island is moored, books ×1.2 away
  from Fenwick, and so on.

## 9. Player opportunities
- **Shopping and haggling** at any open stall (§3).
- **Renting a stall:**
  - a **day pitch** (C$ 30 Fri/Sat/Sun, C$ 25 on island weekdays; dawn queue at the market office);
  - a **season lease** (C$ 220 a month, 8–16 weeks, joins the waiting list);
  - a **permanent shed bay** (C$ 480 a month, a year's lease, needs a reference from a vendor at trust ≥ 0.5).
  - The player sets prices and haggles with NPC customers. Stock comes from estates, the Drops, crafting, buying at
    other markets, or the islands.
- **Trading the circuit** (§8): buy sky goods at a fair and sell them at markets without an island that weekend.
  Prices for sky goods are ×1.3 where no island is moored.
- **Hauling:**
  - Contracts to move furniture from stall to car.
  - Running **cargo cabins** as a ground steward: C$ 18 an hour plus 2 % of the freight.
  - Delivering skyboxes to buyers in town (Dispatch core loop).
- **Guiding tourists:** escorted island visits sold at the Mooring Office (C$ 25 a head, the player keeps 60 %).
- **Joining the Lines:**
  - Late game, at high clan standing, the player can be taken on as a greenline: an apprenticeship to a mooring crew.
  - This is the rare surface → island path (00 §9.3).
- **Gondola fares:**
  - up and back: C$ 12 (children C$ 6);
  - one way with a skybox slot: C$ 40;
  - the night run: C$ 8.

## 10. Plugging into the existing code
- **There is no player wallet or trade code yet.** New pieces:
  - `PlayerWallet` (cash, bank, letters, tabs; save-game fields);
  - `TradeSession` (the haggle state machine);
  - `MarketLedger` (pure: per day, per stall takings, seeded);
  - `Reputation` (pair, clan and market stores, which may belong to deck-ea's affinity store: agree the schema with
    the story engine, `research/lives/07_occupancy.md` "Who owns what").
- **NpcLife money** (`npc_traits.json` wage, savings, debt, `money_style`, `money_reasons`, finances;
  `research/lives/02_money.md`):
  - **Spend per visit** = log-normal(median C$ 30) × the finances band (struggling 0.5, getting by 0.9, comfortable
    1.4, wealthy 2.5).
  - `money_style` sets haggle behaviour: tight NPCs haggle hard, generous ones round up, anxious ones walk away.
  - **The vendor pool weights** (00 §2.3) read finances and `money_reasons` (two_jobs, sends_money_home,
    raising_kids_alone, laid_off, owns_business), plus Lowliner status: ×3.0 in the South, ×2.0 in the north.
    Lowliners' `money_reasons` often carry `sends_money_home` (kin aloft).
  - A vendor's market income is **not** written back into traits each day (they stay static and seeded). The journal
    records a delta only when the story makes it matter, for example "her stall paid off the payday loan".
- **NpcPlaces / NpcLife:**
  - the purposes `flea` (per week 0.35), `browse` and `vending` (00 §6.1);
  - the Draw Day effect: the first weekend after Draw Day, flea visits ×1.2 (`06_culture.md:125`).
- **NpcOccupancy:** market office posts, permanent stall posts (role `market_trader`), Lines ground stewards. Season
  and day vendors are FleaVendors draws, not posts.
- **Sky canon:** each island's `market_goods` (from `trade`), and `factor` counts set its stalls and tents.

## 11. Money flows: the surface and the islands
- **Up the lines (the islands buy):** grain, hay and feed, metals (aluminium, titanium), cells, boards, glass, paper,
  medicine, salt, sugar, bottles, books (`canon_sky.py` SPECIALTIES needs). Also tourist cash and fares.
- **Down the lines (the islands sell):** knitwear, skycloth, rope, down, honey and mead, snow and ice, moss remedies,
  bells, lanterns, forecasts, surveys, air post, and lights work.
- **The balance (per island at a mooring, a design target):**
  - a 4-block island of ~1,000 people sells ~C$ 60–90k over a 3-day weekend:
    - 40 islander stalls/tents × C$ 600–900 a day × 3;
    - plus fares and tours ~C$ 8k;
  - and buys ~C$ 50–70k of floor goods.
  - Net, the Skein runs a small surplus, which explains why the Aloft are prosperous and happy (hyper-capitalist,
    "in a good way").
  - The **line toll**: 20 % of fares and freight goes to the Lines' purse (00 §8.3).
- **The weight book:** every load up is balanced by goods or water down. Trade is literally balanced.
- **Kin money:** with half of every island's children settled below (canon `settled`), much of the trade runs
  through family.
  - Lowliners send goods and cash up the lines to parents, and islands send knitwear, honey and news down.
  - A Lowliner vendor at a fair often sells their home island's goods on commission: the bazaar's clientelization
    by kin.
  - The Line Halls' savings clubs carry it.

## 12. Jobs the economy creates

| where | job | who | count (per city market) |
|---|---|---|---|
| floor | market_trader (permanent stall) | town residents | ~100–130 posts (35 %) |
| floor | season and day vendors | the vendor pool | ~200–240 each weekend (draws, not posts) |
| floor | market manager, warden, clerks, cleaners, car-park attendants | the office | 8–12 posts |
| floor | food-truck cooks | town | 10–16 |
| floor | Lines ground stewards (dock hands) | Cannery Union | 2 per station while moored |
| floor | haulers and porters | informal | the player and NPC day labour |
| floor | festoon riggers and sign makers | many Lowliners | in the electricians' trade |
| floor | Line Hall staff, Lowliner cookshops and stall arcades in the Line Rows | Lowliners | South Sea cities (00 §9.5) |
| sky | the mooring crew (24 per island), line ranks (00 §8.3) | islanders | per island |
| sky | factors, shopkeepers, tour guides, cabin wardens | islanders | per island |

## 13. Balancing numbers (start values; tune in play)
- **Rent:** day pitch C$ 30 (≈ 6–15 % of a C$ 200–500 day), season C$ 220 a month, shed bay C$ 480 a month. No
  admission. Parking is free, except Great Fairs at C$ 5.
- **Shopper:** a median spend of C$ 30 a visit, 1–4 items, an average transaction of C$ 8–15. Dealers spend 10–50x.
- **Haggle:**
  - h 10–30 %;
  - accepted discounts 10–20 %;
  - offence below 0.75 R;
  - bundle +5 pp an item;
  - late day +5–15 pp;
  - client −h/2.
- **Vendor archetypes** (04 §6.8): necessity 25 %, hobbyist 25 %, picker/dealer 12 %, new-goods 15 %, maker 13 %,
  food 5 %, grey 3 %, climber 2 % (they move up the tenure ladder: day → season → shed).
- **Player income targets:**

  | activity | target |
  |---|---|
  | early day pitch with junk | C$ 40–120 net a day |
  | a skilled circuit trader | C$ 300–800 a weekend |
  | a shed bay | C$ 1.5–3k a month, more in fair months |
  | hauling | C$ 18–30 an hour |

  For scale, a floor median wage is ~C$ 790 a week.
- **Treasures:** 1 in 60 estate boxes holds an item worth 20–80× its price. The rare launch-goods antique is worth
  C$ 2–8k.
- **Seasonality:** occupancy target `T(day)` 0.80 in Dec–Feb up to 0.97 in May–Sep (00 §2.2). Footfall ×0.6 in winter.
