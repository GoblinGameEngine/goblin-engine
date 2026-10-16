#!/usr/bin/env python3
"""
markets_spec.py -- the 22 flea markets as numbers (research/flea_markets/00_plan.md §1.2, 07 §2, 06 §8).

One market per settlement: the 21 tools/settlegen/towns.py SPECS plus Calder. This module is the single source for
the sizes, tiers, names, sign cells, draws and fair dates. The generator (tools/settlegen/market.py, via
map_expanded --game-data) sites them; make_markets.py writes godot_project/remake/markets/flea_markets.json.

    import markets_spec as MS
    MS.MARKETS            -> [{id, town, prefix, name, sign, region, band, pop, tier, stalls, permanent, kinds, spaces,
                              mooring, tents_min, t, draw, great_fair_month}]
"""
import math

# (town, prefix, market name, sign cell key (remake/signs/signs.json cells "<key>_main"), region, draw tags)
# draw tags feed market_trip's specialty match (00 §6.3): books / livestock / antiques / sky / tools / crafts / ...
_TABLE = [
    ("Port Carrow", "PCR", "The Ropewalk", "fm01_ropewalk", "north_shore", ["antiques", "rope", "maritime"]),
    ("Brightwater", "BRW", "The Lobster Pot", "fm02_lobster_pot", "north_shore", ["antiques", "crafts", "food"]),
    ("Haven Point", "HVN", "The Tide Clock", "fm03_tide_clock", "north_shore", ["antiques", "collectibles", "maritime"]),
    ("Tern Harbor", "TRN", "The Net Loft", "fm04_net_loft", "north_shore", ["salvage", "tools", "food"]),
    ("Loomis Grove", "LG", "The Water Tower", "fm05_water_tower", "northland", ["tools", "salvage", "livestock"]),
    ("Fenwick", "F", "The Book Barn", "fm06_book_barn", "northland", ["books", "collectibles"]),
    ("Dunmore Crossing", "DC", "The Weathervane", "fm07_weathervane", "northland", ["livestock", "produce", "tools"]),
    ("Marlowe", "M", "Brannock County Trade Days", "fm08_brannock_trade_days", "northland", ["crafts", "antiques", "food"]),
    ("Port Tamsin", "PTM", "The Boathouse Swap", "fm09_boathouse_swap", "kettle_valley", ["tools", "maritime", "salvage"]),
    ("Haskins Corner", "HC", "Four Corners Swap", "fm10_four_corners_swap", "northland", ["household", "clothing", "toys"]),
    ("Victory Bay", "VBY", "The Regatta Swap", "fm11_regatta_swap", "kettle_valley", ["antiques", "clothing_new"]),
    ("Cedar Ford", "CF", "Millwheel Market", "fm12_millwheel_market", "kettle_valley", ["crafts", "produce", "food"]),
    ("Harrow Falls", "HF", "Traders' Landing", "fm13_traders_landing", "kettle_valley", ["sky", "antiques", "household"]),
    ("Kessler", "K", "Iron Wheel Trade Days", "fm14_iron_wheel", "southland", ["tools", "salvage", "collectibles"]),
    ("Bellhaven", "B", "The Red Granary", "fm15_red_granary", "southland", ["produce", "books", "collectibles"]),
    ("Tamarack", "T", "The Tall Tamarack", "fm16_tall_tamarack", "southland", ["furniture", "crafts"]),
    ("Pruett", "P", "Elevator Flea Days", "fm17_elevator_flea_days", "southland", ["tools", "produce", "livestock"]),
    ("Calder", "C", "Route 30 Swap Meet", "fm18_route30_swap_meet", "southland", ["salvage", "collectibles", "household"]),
    ("Playa Verde", "PLV", "La Pulga Verde", "fm19_la_pulga_verde", "south_shore", ["plants", "produce", "food", "crafts"]),
    ("Solana Point", "SOL", "The Starlite Swap", "fm20_starlite_swap", "south_shore", ["sky", "household", "clothing", "food"]),
    ("Oceanview", "OCV", "The Carousel Swap", "fm21_carousel_swap", "south_shore", ["toys", "clothing", "household"]),
    ("Pelican Cove", "PEL", "The Pelican Swap", "fm22_pelican_swap", "south_shore", ["food", "maritime", "salvage"]),
]

# the Great Fairs (06 §8): one per city, its month; the fair is the month's second weekend
GREAT_FAIR = {"Port Carrow": 4, "Harrow Falls": 6, "Solana Point": 8, "Kessler": 10}

# the 16 stall categories (00 §2.3, 06 §2) -- their order is the bitmask's bit order in the vendor pool
CATEGORIES = ["antiques", "collectibles", "household", "furniture", "clothing_used", "clothing_new", "tools", "salvage",
              "electronics", "books", "toys", "crafts", "produce", "plants", "food", "sky"]

# mooring ground by tier (00 §1.2, §5.3): deadmen, masts, the islands that make fast to the ground, field size (m)
MOORING = {"city": {"deadmen": 24, "masts": 2, "ground_islands": 6, "field": (120.0, 100.0)},
           "town": {"deadmen": 12, "masts": 1, "ground_islands": 4, "field": (90.0, 70.0)},
           "village": {"deadmen": 8, "masts": 0, "ground_islands": 3, "field": (70.0, 60.0)}}
TENTS_MIN = {"city": 60, "town": 36, "village": 24}
SPACES_PER_STALL = 1.8
# towns whose market floats on a pier when their limits have no free land (the coordinator, 2026-10-16: Victory Bay)
PIER_TOWNS = {"Victory Bay"}


def _pop_of(town):
    if town == "Calder":
        return 7000
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settlegen"))
    import towns as TS
    return next(s["pop"] for s in TS.SPECS if s["name"] == town)


def tier_of(pop):
    return "city" if pop > 30000 else ("town" if pop >= 5000 else "village")


def stalls_of(pop):
    """00 §1.2: cities round(pop / 120, -1); everywhere else ceil((40 + pop / 140) / 10) * 10 (at least 40)."""
    if pop > 30000:
        return int(round(pop / 120.0, -1))
    return max(40, int(math.ceil((40.0 + pop / 140.0) / 10.0) * 10))


def kinds_of(n):
    """the stall kinds (00 §2.1): food ~4 % (half permanent), open_double ~6 %, shed = the rest of the 35 % permanent,
    open the remainder. Returns {shed, open, open_double, food, permanent}."""
    perm = int(math.floor(0.35 * n + 0.5 + 1e-9))
    food = max(2, int(round(0.04 * n)))
    dbl = max(2, int(round(0.06 * n)))
    shed = perm - food // 2
    return {"shed": shed, "open": n - shed - food - dbl, "open_double": dbl, "food": food, "permanent": perm}


def style_t(x):
    return round(min(1.0, max(0.0, (x + 5600.0) / 11200.0)), 2)


def band_of(t):
    return "north" if t < 0.35 else ("river" if t <= 0.65 else "south")


def _build():
    out = []
    for town, pfx, name, sign, region, draw in _TABLE:
        pop = _pop_of(town)
        tier = tier_of(pop)
        n = stalls_of(pop)
        k = kinds_of(n)
        out.append({"id": "FM-" + pfx, "town": town, "prefix": pfx, "name": name, "sign": sign, "region": region,
                    "pop": pop, "tier": tier, "stalls": n, "permanent": k["permanent"], "kinds": k,
                    "spaces": int(math.ceil(n * SPACES_PER_STALL)), "mooring": dict(MOORING[tier], tier=tier),
                    "tents_min": TENTS_MIN[tier], "draw": draw, "great_fair_month": GREAT_FAIR.get(town, 0),
                    "pier": town in PIER_TOWNS})
    return out


MARKETS = _build()
BY_TOWN = {m["town"]: m for m in MARKETS}

if __name__ == "__main__":
    tot = 0
    for m in MARKETS:
        tot += m["stalls"]
        print("%-7s %-17s %-28s %-8s %6d %4d %4d %4d" % (m["id"], m["town"], m["name"], m["tier"], m["pop"], m["stalls"],
                                                       m["permanent"], m["spaces"]), m["kinds"])
    print("total stalls", tot)
