"""Brightwater (BRW) catalog spec -> brw.json for east_rec.py make.
Brightwater = the Jersey Shore boardwalk town (Wildwood / Ocean City / Seaside Heights), with the
Delmarva, Virginia Beach and Myrtle Beach boardwalks; East Coast examples only."""
import json
import os

B, R, H, L, HO = "e_brw_b:", "e_brw_rides:", "e_brw_hotels:", "e_brw_life:", "e_brw_houses:"
F6 = 6.0
out = []


def rec(i, photos, title, place, year, brief, traits, names, claim=None, expect=None):
    r = {"id": i, "photos": photos, "example": {"title": title, "place": place, "year": year},
         "brief": brief + (" Foundations taken deeper than needed (spec rule 4)." if "pile" not in brief else ""),
         "traits": traits, "names": names}
    if claim:
        r["claim"] = claim
    if expect:
        r["expect"] = expect
    out.append(r)


def cols(body, trim, accent, roof):
    return {"body": body, "trim": trim, "accent": accent, "roof": roof}


# ---------------------------------------------------------------- arcades (boardwalk frontage)
ARC = [
    ("BRW-001", [R + "48", R + "50", R + "51"], "Lucky Leo's arcade on the Seaside Heights boardwalk", "Seaside Heights, NJ", 2013,
     "A boardwalk arcade as rebuilt after Hurricane Sandy: a long low open-fronted hall under a flat roof, the whole front a lit marquee board of red letters on cream with bulb chasers, a glass-doored arcade half and an open games counter half hung with plush prizes. Three photos (2013, during the rebuilding).",
     {"open_front": True, "sign_style": "marquee", "use": "arcade", "colors": cols("#F4E9D2", "#C8202A", "#1D4F9A", "#D9D9D9")},
     {"name": "Lucky Lenny's Arcade", "sign": "LUCKY LENNY'S ARCADE"}),
    ("BRW-002", [R + "73", R + "74"], "Playland's Castaway Cove entrance building", "Ocean City, NJ", 2000,
     "The boardwalk front of an amusement park: a two-storey stucco block painted in bright tropical bands, a pirate-ship bow built out over the entrance with a pirate and a parrot on it, and an open arcade hall under the ship. Two photos; the year is estimated.",
     {"open_front": True, "sign_style": "painted_board", "use": "arcade", "colors": cols("#3FA7D6", "#FFFFFF", "#F2C12E", "#8C5A2B")},
     {"name": "Shipwreck Cove Arcade", "sign": "SHIPWRECK COVE"}),
    ("BRW-007", [R + "25", R + "45"], "Pirate's Hideaway arcade, Seaside Heights boardwalk", "Seaside Heights, NJ", 1990,
     "A boardwalk arcade in a plain blue corrugated-metal box, its whole front a huge painted board with the name in red and gold pirate lettering, roll-up shutters closing the open front. Two photos (2013); the year is estimated.",
     {"open_front": True, "sign_style": "painted_board", "use": "arcade", "colors": cols("#2B5AA8", "#FFFFFF", "#D93A2B", "#9A9A9A")},
     {"name": "Buccaneer's Den", "sign": "BUCCANEER'S DEN ARCADE"}),
    ("BRW-008", [B + "512"], "Boardwalk arcade and gift shops, Rehoboth Beach", "Rehoboth Beach, DE", 1990,
     "A single-storey boardwalk shop block with a pink-and-green striped standing-seam roof curving over a deep open front, a candy-coloured arcade and sweet shop, glass-fronted gift shops beside it. One photo; the year is estimated.",
     {"open_front": True, "sign_style": "painted_board", "use": "arcade", "colors": cols("#FFFFFF", "#E0457B", "#3BAA6E", "#E0457B")},
     {"name": "Sugar Tide Arcade", "sign": "SUGAR TIDE ARCADE & CANDY"}),
    ("BRW-013", [R + "5"], "Mariner's Landing pier entrance, Wildwood boardwalk", "Wildwood, NJ", 1980,
     "The boardwalk entrance to an amusement pier: a gable-ended arcade building with a painted arch of pier names over the walk, shopfronts and a games arcade either side, flags and bulb chasers. One photo; the year is estimated.",
     {"open_front": True, "sign_style": "neon", "use": "arcade", "colors": cols("#F7F2E4", "#1F6FB5", "#E6452E", "#6F7C86")},
     {"name": "Harbor Landing Pier", "sign": "HARBOR LANDING PIER"}),
    ("BRW-014", [B + "27"], "Surf Theatre building, Ocean City boardwalk", "Ocean City, NJ", 1980,
     "A boardwalk block that was a movie house, reused for shops and games: a flat-fronted two-storey front with a big name sign across the top, a marquee over open arcade bays. One photo; the year of its present front is estimated.",
     {"open_front": True, "sign_style": "marquee", "use": "games", "colors": cols("#E8DCC4", "#7A2B2B", "#2C5F8A", "#BDBDBD")},
     {"name": "Breakers Playhouse Games", "sign": "BREAKERS PLAYHOUSE - GAMES"}),
    ("BRW-019", [B + "510"], "Shops on Rehoboth Avenue at the boardwalk", "Rehoboth Beach, DE", 1985,
     "A long low shed-roofed row of boardwalk shops: a raking roof with its gable to the walk, a dark red painted sign band, racks of beach toys, flip-flops and souvenirs spilling out of open fronts. One photo; the year is estimated.",
     {"open_front": True, "sign_style": "painted_board", "use": "souvenir", "colors": cols("#EFE5CF", "#A32530", "#2D6BB0", "#8F8F8F")},
     {"name": "Cloud Nine Beach Shop", "sign": "CLOUD NINE - BEACH STUFF"}),
    ("BRW-020", [B + "572"], "Boardwalk shops at Worcester Street", "Ocean City, MD", 1980,
     "A two-storey boardwalk shop block of the 1970s-80s: concrete-block fronts with deep awnings and illuminated fascia signs, a games arcade and T-shirt shops at walk level, apartments above. One photo; the year is estimated.",
     {"open_front": True, "sign_style": "neon", "use": "arcade", "colors": cols("#F1EEE6", "#1C3E6E", "#E23A3A", "#9C9C9C")},
     {"name": "Worthington Fun Center", "sign": "FUN CENTER - SKEE-BALL - PRIZES"}),
]
for i, ph, t, p, y, br, tr, nm in ARC:
    tr.update({"width_m": 32.1, "year_built": y, "found_depth_m": F6})
    rec(i, ph, t, p, y, br, tr, nm)

# ---------------------------------------------------------------- stands (food and beach patrol)
ST = [
    ("BRW-003", [B + "11"], "Frozen custard stand at 10th Street", "Ocean City, NJ", 1975, "A boardwalk frozen-custard stand: a small white box with an open service counter across the front under an orange-and-white awning, a big illuminated name sign on the roof. One photo.", "food", "neon", ("Kessel Bros. Custard", "KESSEL BROS. FROZEN CUSTARD")),
    ("BRW-004", [B + "16"], "Pizza stand at 9th Street", "Ocean City, NJ", 1980, "A boardwalk pizza stand: counters open to the walk under a red awning, the ovens behind, a long painted name board and a slice-by-slice menu board. One photo; the year is estimated.", "food", "painted_board", ("Mancini & Mancini", "MANCINI & MANCINI PIZZA")),
    ("BRW-005", [R + "11"], "Soda and snack stand, Wildwood boardwalk", "Wildwood, NJ", 1985, "A boardwalk snack stand wrapped in a huge red soft-drink sign, serving counters on three sides with menu boards, a low striped awning. One photo; the year is estimated.", "food", "painted_board", ("Wally's Snack Bar", "WALLY'S - COLD DRINKS - FRIES")),
    ("BRW-006", [R + "26", R + "27"], "Ice-cream stand with a giant figure, Seaside Heights boardwalk", "Seaside Heights, NJ", 1990, "A little white ice-cream stand with blue trim, a giant fibreglass cone on the roof and a 'muffler man' giant beside it holding a cone -- a boardwalk landmark. Two photos (2013).", "food", "painted_board", ("Cone Island", "CONE ISLAND SOFT SERVE")),
    ("BRW-009", [B + "511"], "Salt-water taffy shop with a rooftop sign", "Rehoboth Beach, DE", 1980, "A small boardwalk-corner taffy and caramel-corn shop: a plain two-storey box whose roof carries a huge orange script sign on a steel frame, the sign being the building's whole identity. One photo; the year is estimated.", "food", "neon", ("Dahl's Salt Water Taffy", "DAHL'S")),
    ("BRW-010", ["File:Cape May beach patrol.jpg"], "Beach patrol stand, Cape May", "Cape May, NJ", 1990, "A small beach patrol headquarters shed at the head of the beach: board-and-batten walls, a hip roof, patrol boards and rescue cans racked outside, a flag mast. One photo; the year is estimated.", "shelter", "painted_board", ("Brightwater Beach Patrol - North Station", "BRIGHTWATER BEACH PATROL")),
    ("BRW-011", [B + "791", B + "792"], "Beach patrol headquarters on the promenade, Cape May", "Cape May, NJ", 1990, "A single-storey cream-painted patrol headquarters on the promenade: a low hip roof, a lookout mast beside it, benches along the sea wall in front. Two photos; the year is estimated.", "shelter", "painted_board", ("Brightwater Beach Patrol - Headquarters", "BRIGHTWATER BEACH PATROL - HQ")),
    ("BRW-012", [B + "567"], "Caramel popcorn stand on the boardwalk at Talbot Street", "Ocean City, MD", 1980, "A boardwalk popcorn stand lit up at night: a white front with a red script name sign and a big popcorn-box sign, open counter windows, a queue under the lights. One photo (night); the year of the present stand is estimated.", "food", "neon", ("Fletcher's Popcorn", "FLETCHER'S CARAMEL POPCORN")),
    ("BRW-015", [R + "53", R + "55"], "Clam bar on the Seaside Heights boardwalk", "Seaside Heights, NJ", 1990, "A boardwalk clam bar: an open counter with stools under a white fascia board painted with a menu of coconut shrimp, oysters and sandwiches, a raised name sign on the roof. Two photos (2013).", "food", "painted_board", ("Bay Breeze Clam Bar", "CLAM BAR - COCONUT SHRIMP - OYSTERS")),
    ("BRW-016", [R + "47"], "Corner stand on the Seaside Heights boardwalk", "Seaside Heights, NJ", 1990, "A small boardwalk-corner stand with a roll-down shutter front, a pitched sign frame on the roof and body-piercing and souvenir boards. One photo (2013).", "souvenir", "painted_board", ("The Corner Stand", "THE CORNER")),
    ("BRW-017", [B + "102"], "Boardwalk food stand, Wildwood", "Wildwood, NJ", 1985, "A boardwalk food stand: an open service front under a broad awning, a bold painted sign, a menu of pizza, sausage sandwiches and lemonade. One photo; the year is estimated.", "food", "painted_board", ("Johnny's on the Boards", "JOHNNY'S ON THE BOARDS")),
    ("BRW-018", [B + "469", B + "473"], "Circus Drive-In (sign and stand)", "Wall Township, NJ", 1954, "Older than 1970: no newer roadside stand has a sign like it. A drive-in food stand under a giant neon clown sign in a party hat, a marquee board beneath. Two photos.", "food", "neon", ("Big Top Drive-In", "BIG TOP DRIVE-IN")),
]
for i, ph, t, p, y, br, use, ss, (n, s) in ST:
    tr = {"width_m": 32.1, "open_front": use != "shelter", "sign_style": ss, "use": use, "year_built": y, "found_depth_m": F6}
    rec(i, ph, t, p, y, br, tr, {"name": n, "sign": s})

# ---------------------------------------------------------------- hotels, motels, convention hall
HT = [
    ("BRW-021", [H + "30", H + "33", H + "35"], "Bally's Atlantic City hotel tower", "Atlantic City, NJ", 1989,
     "A late-1980s casino hotel tower on the boardwalk: a sheer slab of mauve-pink reflective glass, about 30 storeys, rising behind a low boardwalk podium of shops and entrances. Three photos.",
     {"storeys": 18, "form": "slab", "balconies": "none", "walls": "glass_curtain", "roof": "flat", "ground_floor": "shops", "pool": "rooftop", "colors": cols("#9E6F86", "#E8E1E6", "#3A2E36", "#6B6B6B")},
     {"name": "The Brightwater Grand", "sign": "BRIGHTWATER GRAND"}),
    ("BRW-023", [H + "71", H + "72", H + "74"], "Showboat hotel tower", "Atlantic City, NJ", 1987,
     "A 1987 hotel tower stepping back in terraces toward the top, beige concrete with bands of windows, a tall vertical name blade and a streamlined curved podium on the boardwalk. Three photos.",
     {"storeys": 20, "form": "stepped", "balconies": "none", "walls": "concrete", "roof": "flat", "ground_floor": "lobby_restaurant", "pool": "deck", "colors": cols("#D9C3A0", "#F5EFE3", "#B0302A", "#8A8A8A")},
     {"name": "The Paddlewheel Hotel", "sign": "PADDLEWHEEL"}),
    ("BRW-025", [H + "77", H + "79"], "Hilton Virginia Beach Oceanfront", "Virginia Beach, VA", 2005,
     "A 2005 oceanfront hotel: a 21-storey tan tower with a stepped crown and balconies on the sea face, on a Mediterranean-style podium with arcades and a statue plaza on the boardwalk. Two photos.",
     {"storeys": 20, "form": "tower", "balconies": "per_room", "walls": "stucco", "roof": "flat", "ground_floor": "lobby_restaurant", "pool": "rooftop", "colors": cols("#D8C3A5", "#F3ECE0", "#8B6A45", "#A08A70")},
     {"name": "Brightwater Oceanfront Hotel", "sign": "BRIGHTWATER OCEANFRONT"}),
    ("BRW-027", [H + "81", H + "83", H + "85"], "Marriott's OceanWatch villas", "Myrtle Beach, SC", 2003,
     "A 2000s beach resort block: a 16-storey peach-and-cream stucco tower with continuous balconies on every floor, red-tile accents at the top, pools and a tiki bar on the dune side. Three photos.",
     {"storeys": 16, "form": "slab", "balconies": "continuous", "walls": "stucco", "roof": "hip_tile", "ground_floor": "lobby", "pool": "deck", "colors": cols("#EBCDB0", "#FFF8EE", "#5E8C7A", "#B8653F")},
     {"name": "Seawatch Villas", "sign": "SEAWATCH VILLAS"}),
    ("BRW-029", [H + "88", H + "89"], "Myrtle Beach Marriott Resort at Grande Dunes", "Myrtle Beach, SC", 2004,
     "A 2004 resort hotel: a long pale-stucco slab with a pyramid-roofed centre, rows of balconies facing the sea, and a big palm-lined pool deck between the hotel and the beach. Two photos.",
     {"storeys": 14, "form": "L", "balconies": "per_room", "walls": "stucco", "roof": "hip_tile", "ground_floor": "lobby_restaurant", "pool": "deck", "colors": cols("#EFE3CF", "#FFFFFF", "#2F6F8F", "#9E8D78")},
     {"name": "Grand Dunes Resort", "sign": "GRAND DUNES RESORT & SPA"}),
]
for i, ph, t, p, y, br, tr, nm in HT:
    tr.update({"year_built": y, "found_depth_m": F6, "sign": "roof_sign"})
    rec(i, ph, t, p, y, br, tr, nm)

MO = [
    ("BRW-024", [B + "577", B + "578"], "Executive Motel", "Ocean City, MD", 1975,
     "A resort motel of the 1970s: two long three-storey wings round a car court, rooms opening off open galleries with white rails, flat roofs, a slim vertical name sign. Two photos (night); the year is estimated.",
     {"storeys": 3, "plan": "L", "gallery": "front", "roof": "flat", "walls": "block", "signage": "neon_pylon", "pool": True, "style": "contemporary"},
     {"name": "Admiral Motor Inn", "sign": "ADMIRAL MOTOR INN - VACANCY"}),
    ("BRW-026", [B + "575"], "Flamingo Motel", "Ocean City, MD", 1972,
     "A three-storey block motel with a flat roof and rows of doors off galleries, its big red neon script name and pink flamingo sign on the roof -- the block itself plain. One photo (night); the year is estimated.",
     {"storeys": 3, "plan": "I", "gallery": "front", "roof": "flat", "walls": "block", "signage": "roof_sign", "pool": True, "style": "contemporary"},
     {"name": "Heron Motel", "sign": "HERON MOTEL"}),
    ("BRW-028", [B + "837", "File:Jetty Motel Cape May A.jpg"], "Jetty Motel", "Cape May, NJ", 1975,
     "A two-storey beachfront motel: white-sided blocks with blue doors, a continuous upper gallery, a low gable roof and a pool, across the street from the dune path. Two photos; the year is estimated.",
     {"storeys": 2, "plan": "U", "gallery": "front", "roof": "gable", "walls": "frame", "signage": "wall", "pool": True, "style": "contemporary"},
     {"name": "Breakwater Motel", "sign": "BREAKWATER MOTEL"}),
    ("BRW-030", [H + "146"], "Starlux (Doo Wop motel)", "Wildwood, NJ", 1953,
     "Older than 1970: the Wildwoods' Doo Wop motels are the type, and none is newer. A pool-court motel with a swooping upswept roof over a glass lobby, plastic palm trees, turquoise and white trim and aluminium gallery rails. One photo.",
     {"storeys": 2, "plan": "U", "gallery": "both", "roof": "butterfly", "walls": "block", "signage": "neon_pylon", "pool": True, "style": "doo_wop"},
     {"name": "Stardust Surf Motel", "sign": "STARDUST SURF"}),
]
for i, ph, t, p, y, br, tr, nm in MO:
    tr.update({"year_built": y, "found_depth_m": F6})
    rec(i, ph, t, p, y, br, tr, nm)

rec("BRW-022", [B + "93", "File:Wildwoods Convention Center.jpg", "File:Wildwood Tramcar at Wildwoods Convention Center.jpeg"],
    "Wildwoods Convention Center", "Wildwood, NJ", 2002,
    "The 2002 convention centre on the boardwalk: a long hall under a shallow barrel-vaulted roof, a glass entrance rotunda and colonnade on the boardwalk, big lettering and the boardwalk tram stopping out front. Three photos.",
    {"use": "Convention Hall", "style": "modern", "storeys": 2, "walls": "concrete", "dome_or_cupola": "none", "year_built": 2002, "found_depth_m": F6, "colors": cols("#E9E4DA", "#1F5E8C", "#C9A544", "#AAB4BA")},
    {"name": "Brightwater Convention Hall", "sign": "BRIGHTWATER CONVENTION HALL", "plaque": "Built 2002"})

# ---------------------------------------------------------------- stores (69 m frontage: blocks of shops)
SB = [
    ("BRW-031", [B + "486"], "Surf shop, Ship Bottom", "Ship Bottom, NJ", 1990, "A big two-storey surf shop: a sky-blue and yellow stucco box with a gabled glass-and-arched entry pavilion, surfboards racked in the windows.", 2, "stucco", [("Tide Line Surf", "surf_shop"), ("Tide Line Kids", "beachwear")], cols("#6BB7E0", "#F2D16B", "#FFFFFF", "#6E6E6E")),
    ("BRW-032", [B + "514", B + "515"], "Shops on Rehoboth Avenue", "Rehoboth Beach, DE", 1985, "A row of shingled shop houses: a teal-painted fishscale-shingle gable front with a restaurant, white porches and pink trim beside it.", 2, "shingle", [("Rock Pool Cafe", "seafood_restaurant"), ("Dune Grass Gifts", "souvenir")], cols("#4BA3A0", "#FFFFFF", "#D66A8A", "#5E6A6A")),
    ("BRW-033", [B + "518"], "Beach shop on Rehoboth Avenue", "Rehoboth Beach, DE", 1990, "A single-storey beach shop with a big blue metal mansard roof and a white fascia with the name in bold letters, beachwear racks outside.", 1, "block", [("Brightwater Beachwear", "beachwear"), ("Sandy Toes", "t_shirts")], cols("#FFFFFF", "#1D5FB2", "#F0A92C", "#1D5FB2")),
    ("BRW-034", [B + "523"], "Two-storey bar and restaurant with a roof deck", "Rehoboth Beach, DE", 2000, "A red-brick two-storey corner restaurant with a wraparound upper deck under a striped awning, bunting and a tall name sign on the roof.", 2, "brick", [("Skipper Brown's", "seafood_restaurant"), ("Skipper's Raw Bar", "raw_bar")], cols("#9A4B35", "#FFFFFF", "#1E3F76", "#6E6E6E")),
    ("BRW-035", [B + "527"], "The Shops at Rehoboth Mews", "Rehoboth Beach, DE", 1990, "A little shopping lane of cedar-shingled shop fronts with striped awnings and flower pots, a brick pavement leading back from the avenue.", 2, "shingle", [("The Mews Book Nook", "art_gallery"), ("Spin Bikes", "bike_rental"), ("Harbor Candles", "souvenir")], cols("#8C7A62", "#FFFFFF", "#2B6E57", "#555555")),
    ("BRW-036", [B + "528", B + "529"], "Shop fronts on Rehoboth Avenue", "Rehoboth Beach, DE", 1980, "A single-storey run of shops behind a shared covered walk, green-and-white striped awnings, benches along the kerb.", 1, "frame", [("Seaglass Jewelers", "art_gallery"), ("Salty Dog Treats", "ice_cream"), ("Coastline Tees", "t_shirts")], cols("#F2EDE2", "#2E7D4F", "#D8B24A", "#6B6B6B")),
    ("BRW-037", [B + "517"], "Pizza restaurant with a striped awning", "Rehoboth Beach, DE", 1985, "A brick two-storey pizza restaurant with a red-and-yellow striped awning and a projecting box sign.", 2, "brick", [("Nicolo's Pizza", "pizza_slice")], cols("#8C3B2A", "#F5E6C4", "#E6B42A", "#555555")),
    ("BRW-038", [B + "513"], "Fish and chip shop with English red-phone-box details", "Rehoboth Beach, DE", 2010, "A tall narrow white fish-and-chip shop with a Union Jack painted front, a red phone box by the door and black lettering.", 2, "stucco", [("Cod Almighty", "seafood_restaurant")], cols("#FFFFFF", "#1A2F6E", "#C8202A", "#4A4A4A")),
    ("BRW-039", [B + "520"], "Shop on Rehoboth Avenue", "Rehoboth Beach, DE", 1990, "A brick shop with a green-trimmed front, a painted round sign and café tables on the pavement.", 2, "brick", [("Sweet Surrender Bakery", "taffy_fudge")], cols("#9A5A42", "#FFFFFF", "#2F7A52", "#5A5A5A")),
    ("BRW-040", [B + "715", B + "716", B + "712"], "Convenience store and gas station, Cape May", "Cape May, NJ", 2012, "A 2010s convenience store in shore style: grey siding, a white railed roof walk, a square corner tower with a round window, a gas canopy.", 1, "fiber_cement", [("QuickWave Market", "marina_store")], cols("#9C9585", "#FFFFFF", "#C8202A", "#5A5A5A")),
    ("BRW-041", [B + "104", B + "106", B + "107"], "Supermarket, Wildwood", "Wildwood, NJ", 1995, "A supermarket: a long low block with a gabled entrance bay, a big fascia name sign and a parking lot in front.", 1, "block", [("Shore Fresh Market", "fish_market")], cols("#EDE6D8", "#C8202A", "#1F4F8C", "#7A7A7A")),
    ("BRW-042", [B + "555"], "Supermarket at Rehoboth Marketplace", "Rehoboth Beach, DE", 2000, "A shopping-centre supermarket with a tall red name tower and a covered walk of smaller shops beside it.", 1, "block", [("Harbor Grocers", "fish_market"), ("Paint & Hardware", "marina_store")], cols("#E8DFCF", "#B8262B", "#FFFFFF", "#7A7A7A")),
    ("BRW-043", [B + "65"], "Pancake house, Ocean City", "Ocean City, NJ", 1980, "A single-storey pancake house with a mansard of cedar shingles, a long row of windows and a big roadside sign.", 1, "shingle", [("Uncle Walt's Pancake House", "cafe")], cols("#EEE2CC", "#8A3A2A", "#F2C04A", "#6B5A48")),
    ("BRW-044", [B + "797"], "Pancake house and restaurant, West Cape May", "West Cape May, NJ", 1990, "A long low grey-sided restaurant with white trim, a red roof sign and a lawn in front.", 1, "frame", [("Doc Marty's Pancakes", "cafe")], cols("#B7B8B2", "#FFFFFF", "#B32A2A", "#4A4A4A")),
    ("BRW-045", [B + "800", B + "803"], "Restaurant in a former gas station, West Cape May", "West Cape May, NJ", 2010, "A former gas station reused as a restaurant: the canopy kept as a covered terrace, a grey board-and-batten barn-like dining hall beside it.", 1, "frame", [("Last Exit Kitchen", "brewpub")], cols("#6F7275", "#FFFFFF", "#D7A13A", "#3F3F3F")),
    ("BRW-046", [B + "794"], "Bakery and café in an old garage, West Cape May", "West Cape May, NJ", 2012, "A timber-sided garage turned bakery-café: a stepped false front, big glass doors, umbrellas and café tables on a gravel forecourt.", 1, "frame", [("West End Bakehouse", "cafe")], cols("#5C4B3B", "#FFFFFF", "#2F6E57", "#3F3F3F")),
    ("BRW-047", [B + "316"], "Neighbourhood shopping centre", "Spring Lake Heights, NJ", 1975, "A 1970s strip shopping centre: a long single-storey block with a shingled mansard fascia, a row of shopfronts behind a covered walk, parking in front.", 1, "brick", [("Heights Pharmacy", "store"), ("Cindy's Nails", "store"), ("Bagel Wave", "cafe")], cols("#C9B79A", "#FFFFFF", "#2D5E7A", "#6E5E4E")),
    ("BRW-048", [B + "757"], "Washington Street Mall shops", "Cape May, NJ", 1971, "The 1971 pedestrian mall: a brick-paved street closed to cars, lined with two-storey shops in brick and clapboard under striped awnings, planters and benches down the middle.", 2, "frame", [("Cape Light Gallery", "art_gallery"), ("Fudge Ahoy", "taffy_fudge"), ("Mall Toy Chest", "souvenir")], cols("#F0E6D4", "#2E4E7A", "#B84A3A", "#5A5A5A")),
    ("BRW-049", [B + "732"], "Corner bar and restaurant, Cape May", "Cape May, NJ", 1990, "A small two-storey corner restaurant in yellow siding with a gable front, a shed-roof addition and a big hanging sign.", 2, "frame", [("Sea View Tavern", "seafood_restaurant")], cols("#E8CF7A", "#FFFFFF", "#3A5E7A", "#4A4A4A")),
    ("BRW-050", [B + "44"], "Convenience store, Ocean City", "Ocean City, NJ", 2005, "A shore-town convenience store: a single storey of beige siding with a steep hipped roof, a cupola and a railed widow's walk.", 1, "fiber_cement", [("QuickWave Market (34th St)", "marina_store")], cols("#D9CBB0", "#FFFFFF", "#C8202A", "#5A5A5A")),
]
for i, ph, t, p, y, br, st, fac, fronts, c in SB:
    tr = {"storeys": st, "facade": fac, "cornice": "parapet_flat", "upper_use": "apartments" if st > 1 else None,
          "storefronts": [{"business": n, "type": ty, "sign": n.upper(), "sign_style": "flat_board", "awning": True, "extra_signs": []} for n, ty in fronts],
          "condition": "kept", "year_built": y, "found_depth_m": F6, "colors": c}
    rec(i, ph, t, p, y, br + (" One photo; the year is estimated." if len(ph) == 1 else f" {len(ph)} photos; the year is estimated."), tr, {"name": fronts[0][0], "sign": fronts[0][0].upper()})

# ---------------------------------------------------------------- cottages (1970s-2020s shore houses)
CT = [
    (HO + "4", None, "Raised 1970s beach house, Wildwood", "Wildwood, NJ", 1975, "A two-storey 1970s beach house raised over a carport: brown wood siding, a full-width upper deck under a shed roof, an outside stair to the deck.", 2, "shed", "wood", ("#8A6A4A", "#F0E6D2", "#3A3A3A", "#5A4A3A")),
    (HO + "5", None, "New beach house with a stone base", "New Jersey shore", 2010, "A 2010s shingle-style beach house: sage-green siding, a stone-veneer ground floor with a double garage door, a front gable with a round window and a railed upper porch.", 2.5, "gable", "fiber_cement", ("#7C9A86", "#FFFFFF", "#9C8C78", "#4E5A5E")),
    (HO + "11", None, "Three-storey raised house, Wildwood", "Wildwood, NJ", 2005, "A narrow three-storey house on a corner lot: blue siding, stacked white-railed porches on every floor, parking under.", 3, "gable", "vinyl", ("#4E7FA8", "#FFFFFF", "#2F3F4F", "#5A5A5A")),
    (HO + "12", None, "Three-storey duplex with porches, Wildwood", "Wildwood, NJ", 2000, "A tall duplex: pale yellow siding, a steep front gable with fishscale shingles, three storeys of white-railed porches across the front.", 3, "gable", "vinyl", ("#E8D89A", "#FFFFFF", "#6E8C9E", "#5A5A5A")),
    (HO + "10", None, "Small house in Miami Beach, Lower Township", "Lower Township, NJ", 1975, "A small single-storey shore cottage with a low gable roof and a white picket fence along a sandy lane.", 1, "gable", "vinyl", ("#9FB7C8", "#FFFFFF", "#3A5E7A", "#6A6A6A")),
    (HO + "23", None, "Bayfront raised house with boat slips", "Beach Haven West, NJ", 2005, "A three-storey bayfront house raised on piles over the bulkhead: dark grey siding, a red roof, big decks on every floor, boats moored at the slip in front. The piles taken 10 m into the bed.", 3, "hip", "fiber_cement", ("#4A5058", "#FFFFFF", "#B03A2E", "#A83A2E")),
    (HO + "38", None, "Bayside townhouses, Mystic Island", "Mystic Island, NJ", 2000, "A row of three-storey townhouses facing the marsh: grey siding, three steep front gables, stacked balconies and garages under.", 3, "gable", "vinyl", ("#C9C7BF", "#FFFFFF", "#6F7E8A", "#5A5A5A")),
    (HO + "39", None, "Rebuilt shore cottage", "New Jersey shore", 2014, "A small single-storey cottage rebuilt after Hurricane Sandy: white siding, a gabled porch roof on posts, raised on a new block foundation with steps up.", 1, "gable", "vinyl", ("#F2F2EE", "#FFFFFF", "#4A6A8A", "#6A6A6A")),
    (B + "5", "L1", "Raised modern house on Atlantic Avenue", "Ocean City, NJ", 2015, "A three-storey modern beach house: white siding, glassy corner decks with glass rails, parking under.", 3, "flat", "fiber_cement", ("#F5F5F2", "#FFFFFF", "#4A4A4A", "#9A9A9A")),
    (B + "5", "R1", "Grey house with stacked porches on Atlantic Avenue", "Ocean City, NJ", 2008, "A three-storey grey-sided house with stacked white-railed porches and a stair to the first floor.", 3, "gable", "vinyl", ("#8C9092", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "75", "L1", "Three-storey townhouses on Magnolia Avenue", "Wildwood, NJ", 2010, "A row of three-storey townhouses in beige siding with gabled bays and garages under.", 3, "gable", "vinyl", ("#D8CDB8", "#FFFFFF", "#6A6A6A", "#5A5A5A")),
    (B + "75", "R2", "Blue three-storey house on Magnolia Avenue", "Wildwood, NJ", 2005, "A three-storey blue-sided house with a steep gable and an outside stair.", 3, "gable", "vinyl", ("#355E9E", "#FFFFFF", "#E8E0D0", "#4A4A4A")),
    (B + "76", "R1", "Two-storey house with a dormer on CR 614", "Wildwood, NJ", 1975, "A two-storey white and grey house with a big front dormer and a small porch.", 2, "gable", "vinyl", ("#D9D9D4", "#FFFFFF", "#5A6A7A", "#4A4A4A")),
    (B + "76", "R2", "Cape Cod house on CR 614", "Wildwood, NJ", 1972, "A one-and-a-half-storey Cape Cod house in cream siding with a front porch.", 1.5, "gable", "vinyl", ("#E8DDB8", "#FFFFFF", "#6A4A3A", "#5A5A5A")),
    (B + "78", "L1", "Raised house with white stairs at Lake Avenue", "Wildwood, NJ", 2012, "A raised house in blue-grey siding with a white stair and railed landing to a first-floor door, a boat in the yard.", 2, "gable", "vinyl", ("#6F8499", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "78", "R1", "Beige raised house at Lake Avenue", "Wildwood, NJ", 2008, "A two-storey beige raised house with a hip roof and a fenced yard with a boat.", 2, "hip", "vinyl", ("#D9CBB0", "#FFFFFF", "#5A5A5A", "#6A5A4A")),
    (B + "79", "R1", "Raised house with a long stair, Lake Avenue", "Wildwood, NJ", 2014, "A white raised house with a long straight stair to a first-floor porch, garage and storage beneath.", 2, "gable", "vinyl", ("#F2F2EE", "#FFFFFF", "#6A7A8A", "#5A5A5A")),
    (B + "79", "L1", "Grey cottage at Lake Avenue", "Wildwood, NJ", 1975, "A single-storey grey cottage with a low gable and a small front stoop.", 1, "gable", "vinyl", ("#9A9C9E", "#FFFFFF", "#3A3A3A", "#5A5A5A")),
    (B + "80", "L1", "Three-storey condominium house on Pacific Avenue", "Wildwood, NJ", 2006, "A three-storey grey and white two-unit house with stacked glass-railed balconies across the front.", 3, "gable", "vinyl", ("#A4A7A8", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "494", "R1", "Yellow three-storey house on Long Beach Boulevard", "Long Beach Island, NJ", 2012, "A tall yellow three-storey house with a white privacy fence and a flat-topped roof.", 3, "flat", "vinyl", ("#EDE19A", "#FFFFFF", "#6A6A6A", "#9A9A9A")),
    (B + "494", "L1", "Beige duplex on Long Beach Boulevard", "Long Beach Island, NJ", 1985, "A two-storey beige duplex with a low roof and a white rail fence.", 2, "gable", "vinyl", ("#D9CDB5", "#FFFFFF", "#5A5A5A", "#5A5A5A")),
    (B + "499", "L1", "Grey and white house with balconies, Division Avenue", "Surf City, NJ", 2010, "A three-storey grey house with white trim, big glass-railed balconies on two floors and parking under.", 3, "hip", "fiber_cement", ("#8E9396", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "499", "R1", "White raised house with wrap balconies, Division Avenue", "Surf City, NJ", 2012, "A white-trimmed grey raised house with wraparound railed balconies on the upper floors and a garage under.", 3, "hip", "fiber_cement", ("#B9BDBF", "#FFFFFF", "#3A4A5A", "#4A4A4A")),
    (B + "499", "R2", "Blue-grey house further down Division Avenue", "Surf City, NJ", 2005, "A two-and-a-half-storey blue-grey house with a front gable and a railed porch.", 2.5, "gable", "vinyl", ("#7D93A8", "#FFFFFF", "#3A4A5A", "#4A4A4A")),
    (B + "500", "R1", "Blue-grey three-storey house on CR 89", "Surf City, NJ", 2014, "A three-storey blue-grey house with white trim, a hip roof and stacked decks.", 3, "hip", "fiber_cement", ("#6C8499", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "500", "R2", "White raised house on CR 89", "Surf City, NJ", 2013, "A white raised house with an outside stair and decks.", 2, "gable", "vinyl", ("#F0F0EC", "#FFFFFF", "#5A6A7A", "#6A6A6A")),
    (B + "500", "L1", "Grey duplex on CR 89", "Surf City, NJ", 2000, "A grey two-and-a-half-storey duplex with twin gables and a covered stair.", 2.5, "gable", "vinyl", ("#A9ACAE", "#FFFFFF", "#3A3A3A", "#5A5A5A")),
    (B + "501", "L1", "White raised house on CR 89 north", "Surf City, NJ", 2011, "A white raised beach house with a hip roof, decks and a garage under.", 2.5, "hip", "vinyl", ("#F3F3EF", "#FFFFFF", "#4A5A6A", "#6A6A6A")),
    (B + "806", "L1", "Grey and white house on Third Avenue", "West Cape May, NJ", 2005, "A two-storey grey house with white trim, two dormers and a front porch.", 2, "gable", "fiber_cement", ("#9FA3A6", "#FFFFFF", "#2F3F4F", "#4A4A4A")),
    (B + "806", "R1", "Single-storey grey house on Third Avenue", "West Cape May, NJ", 1978, "A low single-storey grey ranch house with a wide window and a lawn.", 1, "gable", "vinyl", ("#A8AAAC", "#FFFFFF", "#4A4A4A", "#5A5A5A")),
]
STREETS = ["Pier Ave", "Oak Ave", "Heron Ave", "Magnolia Ave", "Surf Ave", "Pacific Ave", "Dune Rd", "Bay Ave"]
FAM = ["Albanese", "Kowalczyk", "DiMarco", "O'Rourke", "Whitfield", "Pagano", "Brennan", "Szabo", "Lombardi", "Hughes",
       "Ferraro", "Nguyen", "McAllister", "Castellano", "Gallagher", "Rinaldi", "Patel", "Doyle", "Mazur", "Sullivan",
       "Russo", "Kim", "Delaney", "Moretti", "Fitzgerald", "Bianchi", "Walsh", "Esposito", "Carroll", "Romano"]
for k, (src, pos, t, p, y, br, st, roof, walls, c) in enumerate(CT):
    i = f"BRW-{51 + k:03d}"
    raised = y >= 1990 and st >= 2
    tr = {"archetype": "raised_beach_house" if raised else "contemporary_beach" if y >= 1985 else "cottage_lake",
          "storeys": st, "main_w_ft": 30 if st >= 3 else 28, "main_d_ft": 32, "wing": None,
          "roof": {"type": roof, "pitch_deg": 0 if roof == "flat" else 30, "material": "asphalt_shingle" if roof != "flat" else "membrane"},
          "dormers": [], "porch": {"type": "stacked" if st >= 3 else "front", "posts": "square", "rail": "picket"},
          "walls": walls, "foundation": "piles" if raised or "piles" in br else "concrete_block",
          "colors": cols(*c), "windows": {"type": "1over1", "shutters": False}, "chimneys": [],
          "garage": "under" if raised else "none", "yard": {"fence": "picket", "extras": ["outdoor_shower"]},
          "condition": "kept", "year_built": y, "found_depth_m": 10.0 if raised else F6}
    photos = [src]
    claim = src + ("#" + pos if pos else "")
    b2 = br + (f" From a street photo: the house at position {pos} ('L' left, 'R' right side of the street, counted from the camera)." if pos else " One photo.") + " The year is estimated."
    rec(i, photos, t, p, y, b2, tr, {"family": FAM[k], "house_number": str(100 + 7 * k), "street": STREETS[k % len(STREETS)]}, claim=claim)

# ---------------------------------------------------------------- church, post office, school
rec("BRW-081", [B + "503"], "St. Francis of Assisi Church, Long Beach Township", "Brant Beach, Long Beach Island, NJ", 1975,
    "A modern island parish church: a broad low brick nave under a sweeping shallow roof, a slim detached bell frame, a big parking court; shore-modern rather than historic. One photo (2024); the year is estimated.",
    {"style": "modern", "walls": "brick", "tower": {"position": "detached", "top": "open_frame"}, "plan": "fan", "roof": {"type": "gable", "pitch_deg": 20, "material": "asphalt_shingle"}, "colors": cols("#A86A4E", "#F2EEE6", "#3A3A3A", "#5E5E5E"), "condition": "kept", "year_built": 1975, "found_depth_m": F6},
    {"name": "St. Brendan-by-the-Sea", "denomination": "Roman Catholic", "sign": "ST. BRENDAN-BY-THE-SEA - Masses Sat 5:00 - Sun 8:00 10:30"})
rec("BRW-082", [B + "247"], "Point Pleasant post office", "Point Pleasant, NJ", 1980,
    "A single-storey post office of the 1970s-80s: buff brick walls, a flat roof with a deep fascia, a glass entrance under a canopy and a flagpole on the lawn. One photo (2024); the year is estimated.",
    {"use": "Post Office", "style": "modern", "storeys": 1, "walls": "brick", "dome_or_cupola": "none", "year_built": 1980, "found_depth_m": F6, "colors": cols("#C9A87E", "#FFFFFF", "#1F3F7A", "#7A7A7A")},
    {"name": "Brightwater Post Office", "sign": "UNITED STATES POST OFFICE - BRIGHTWATER, N.J. 08260"})
rec("BRW-083", [B + "479"], "Communications High School", "Wall Township, NJ", 1995,
    "A county magnet high school of the 1990s: a long low building of brick and blue metal panels, a glazed entry, ribbon windows, a monument sign at the drive. One photo; the year is estimated.",
    {"era": 1995, "storeys": 2, "style": "modern", "walls": "brick", "wings": 2, "towers": 0, "dome_or_cupola": "none", "roof": {"type": "flat", "pitch_deg": 0, "material": "membrane"}, "colors": cols("#A5704F", "#FFFFFF", "#2E5E9E", "#8A8A8A"), "condition": "kept", "found_depth_m": F6},
    {"name": "Brightwater School", "mascot": "Gulls", "sign": "BRIGHTWATER SCHOOL - Home of the Gulls"})

# ---------------------------------------------------------------- lifeguard stands
LG = [
    ("BRW-084", [B + "283"], "Jersey lifeguard chairs", "Belmar, NJ", 2015, "chair", "wood", "The Jersey-shore lifeguard chair: a tall white-painted timber chair on a sled base with a sun umbrella socket, the beach name stencilled on the back.", "#FFFFFF"),
    ("BRW-085", [B + "108", B + "110"], "Lifeguard stand, North Wildwood", "North Wildwood, NJ", 2010, "chair", "wood", "A white timber lifeguard stand on a wide sled base with a seat for two and a ladder, dragged out each morning.", "#FFFFFF"),
    ("BRW-086", [L + "1"], "Lifeguard stand, Ocean City beach", "Ocean City, MD", 2015, "chair", "wood", "A tall white Ocean City beach stand with a red-cross back and a big umbrella, on the wide beach below the high-rises.", "#FFFFFF"),
    ("BRW-087", [L + "24", L + "25", L + "26", L + "27"], "Lifeguard tower, Cocoa Beach", "Cocoa Beach, FL", 2010, "tower_hut", "wood", "A square white lifeguard hut with a red pyramid roof and blue rails, on a braced platform with a ramp, a pickup parked by it.", "#FFFFFF"),
    ("BRW-088", [L + "7", L + "8"], "Lifeguard tower, Fort Lauderdale beach", "Fort Lauderdale, FL", 2005, "tower_hut", "fiberglass", "A blue-and-white Fort Lauderdale tower: a cabin with a broad overhanging roof on a steel platform, a stair with steel rails.", "#E8F2FA"),
    ("BRW-089", [L + "21", L + "23"], "Lifeguard station 8, Pompano Beach", "Pompano Beach, FL", 2010, "tower_hut", "wood", "A white lifeguard station with a big black number on the sea face and a posted conditions board on the stair.", "#FFFFFF"),
    ("BRW-090", [L + "38", L + "39"], "Lifeguard tower with the 'Miami Beach' sign", "Miami Beach, FL", 2002, "tower_hut", "wood", "One of Miami Beach's architect-designed towers of the 1990s-2000s: a white cabin with a blue wave roundel, yellow cross-braced legs and a blue name board on the front.", "#FFFFFF"),
    ("BRW-091", [L + "44", L + "48"], "Striped 'lighthouse' lifeguard tower, Miami Beach", "Miami Beach, FL", 2002, "tower_hut", "wood", "A red-and-white striped round tower like a little lighthouse, with a lantern-like cabin and a gallery, on a railed platform.", "#FFFFFF"),
    ("BRW-092", [L + "40"], "Purple lifeguard tower, Miami Beach", "Miami Beach, FL", 2002, "tower_hut", "wood", "A purple and orange cabin with a jagged star-burst roof on a pink platform with orange rails.", "#7A4FA8"),
    ("BRW-093", [L + "33", L + "63"], "Green-roofed curved lifeguard tower, Miami Beach", "Miami Beach, FL", 2002, "tower_hut", "wood", "A teal cabin under a cantilevered surfboard-shaped green roof, on yellow legs with a curved stair.", "#3FB3A8"),
    ("BRW-094", [L + "67", L + "75"], "Stars-and-stripes lifeguard tower, Miami Beach", "Miami Beach, FL", 2002, "tower_hut", "wood", "A cabin painted in red and white stripes with a blue star-spangled band, on blue-and-red cross-braced legs.", "#FFFFFF"),
]
for n, (i, ph, t, p, y, ty, mat, br, paint) in enumerate(LG):
    rec(i, ph, t, p, y, br + (" One photo" if len(ph) == 1 else f" {len(ph)} photos") + "; the year is estimated. Legs piled 10 m into the sand (spec rule 4).",
        {"type": ty, "material": mat, "paint": {"cabin": paint, "trim": "#1F3F7A", "number": "#1A1A1A", "legs": "#FFFFFF"},
         "tower_number": str(n + 1), "ramp": ty == "tower_hut", "pile_depth_m": 10.0, "year_built": y},
        {"sign": f"BRIGHTWATER BEACH PATROL - STAND {n + 1}", "notice": "SWIM NEAR A LIFEGUARD"})

# ---------------------------------------------------------------- rides (amusement pier, over water)
RD = [
    ("BRW-095", [R + "0", R + "1", R + "7", R + "8"], "Giant Wheel, Morey's Mariner's Landing Pier", "Wildwood, NJ", 1985, "ferris_wheel", "A 156 ft Ferris wheel of 1985 on the amusement pier: a white steel wheel on an A-frame of trusses, enclosed gondolas, lit at night in changing LED colours."),
    ("BRW-096", [R + "80"], "GaleForce roller coaster, Playland's Castaway Cove", "Ocean City, NJ", 2015, "coaster", "A 2015 launched steel coaster: a white track climbing a vertical 125 ft tower and diving in a beyond-vertical drop, tight twisted layout over the pier deck."),
    ("BRW-097", [R + "67", R + "69", R + "70", R + "71"], "Wave swinger, Playland's Castaway Cove", "Ocean City, NJ", 2005, "swings", "A wave-swinger chair ride: a canopied rotating crown on a central mast, chairs on chains flying out, a carnival-bright canopy of lights."),
    ("BRW-098", [R + "119", R + "120"], "AtmosFEAR drop tower, Morey's Piers", "Wildwood, NJ", 2006, "drop_tower", "A 2006 drop tower: a tall lattice mast lit in red, white and blue, a ring of outward-facing seats rising and dropping round it."),
    ("BRW-099", [R + "77", R + "82", R + "83", R + "85"], "Haunted House at Trimper's Rides", "Ocean City, MD", 1964, "dark_ride", "Older than 1970: the dark ride type has no newer boardwalk example. A two-storey dark-ride building whose front is a giant painted scene -- a grinning cat, a crooked roof, jagged orange letters -- and the car track in and out of it."),
    ("BRW-100", [R + "98", R + "110"], "Carousel, Gillian's Wonderland Pier", "Ocean City, NJ", 1926, "carousel", "Older than 1970: the pier carousel is by nature an antique. A hand-carved carousel under a round canopy of mirrors and bulbs, housed in the pier's open-sided hall."),
]
for i, ph, t, p, y, ty, br in RD:
    rec(i, ph, t, p, y, br + (f" {len(ph)} photos." if len(ph) > 1 else " One photo.") + " Over the water: its foundations are the pier deck's pile bents, 10 m below the bed.",
        {"type": ty, "year_built": y, "pile_depth_m": 10.0, "lights": "led_chase"}, {"name": t.split(",")[0], "sign": t.split(",")[0].upper()})

# ---------------------------------------------------------------- walks
WK = [
    ("BRW-W01", [B + "9", B + "12", B + "14"], "Ocean City boardwalk, 8th-12th Streets", "Ocean City, NJ", 2015, "The main boardwalk: a 12 m wide timber deck of planks laid across the walk on timber stringers and pile bents, a white pipe rail on the beach side, lamp posts, benches facing the sea, shops on the land side. Sections rebuilt 2010s.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "pipe", "lighting": "lamp_posts", "benches": True, "width_m": 12}),
    ("BRW-W02", [B + "257", B + "262"], "Belmar boardwalk (rebuilt 2013)", "Belmar, NJ", 2013, "A beach-access ramp off the boardwalk, as on Belmar's post-Sandy boardwalk: composite decking on concrete-footed piles, galvanised rails.", {"deck": "composite", "substructure": "concrete_piles", "rail": "pipe", "lighting": "none", "benches": False, "width_m": 4}),
    ("BRW-W03", [B + "303"], "Avon-by-the-Sea boardwalk", "Avon-by-the-Sea, NJ", 2013, "A beach entrance through the Avon boardwalk: timber planks, a white rail, a gate with the beach-badge checker's post.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "timber", "lighting": "none", "benches": False, "width_m": 4}),
    ("BRW-W04", [B + "364", B + "365"], "Ocean Grove boardwalk", "Ocean Grove, NJ", 2013, "A ramp to the sand off a red-stained timber boardwalk with white benches and a rail.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "timber", "lighting": "lamp_posts", "benches": True, "width_m": 4}),
    ("BRW-W05", [B + "521", B + "522"], "Rehoboth Beach boardwalk", "Rehoboth Beach, DE", 2000, "A beach access off the Rehoboth boardwalk: timber planks, lamp posts, a sand fence either side through the dune.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "none", "lighting": "lamp_posts", "benches": True, "width_m": 4}),
    ("BRW-W06", [B + "531"], "Rehoboth Beach boardwalk at Delaware Avenue", "Rehoboth Beach, DE", 2000, "A wide set of timber steps down from the boardwalk to the beach with a flagpole at the top.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "timber", "lighting": "lamp_posts", "benches": False, "width_m": 4}),
    ("BRW-W07", [B + "568"], "Ocean City boardwalk at 12th Street", "Ocean City, MD", 1990, "A crossover from the Ocean City boardwalk down through the dune, timber with a rail, the condominium wall behind.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "timber", "lighting": "none", "benches": False, "width_m": 4}),
    ("BRW-W08", [B + "588"], "Virginia Beach boardwalk at 29th Street", "Virginia Beach, VA", 1990, "A concrete ramp from Virginia Beach's concrete boardwalk to the sand, a timber rail along the dune.", {"deck": "concrete", "substructure": "concrete_piles", "rail": "timber", "lighting": "lamp_posts", "benches": True, "width_m": 4}),
    ("BRW-W09", [R + "16", R + "17"], "Casino Pier boardwalk (under repair, 2016)", "Seaside Heights, NJ", 2016, "A new section of Seaside's boardwalk in fresh yellow-pine planks laid in a herringbone, on new piles.", {"deck": "timber_herringbone", "substructure": "timber_piles", "rail": "none", "lighting": "none", "benches": False, "width_m": 4}),
    ("BRW-W10", [R + "57"], "Seaside Heights boardwalk", "Seaside Heights, NJ", 2013, "A ramp down from Seaside's rebuilt boardwalk between the stands, lamp standards and a pipe rail.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "pipe", "lighting": "lamp_posts", "benches": False, "width_m": 4}),
    ("BRW-W11", [B + "840"], "Sunset Pavilion on the Cape May promenade", "Cape May, NJ", 2000, "A beach access beside a small open pavilion on the promenade: timber deck, white rails, a shingled hip roof over benches.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "timber", "lighting": "none", "benches": True, "width_m": 4}),
    ("BRW-W12", [B + "303"], "", "", 0, "", {}),  # placeholder, replaced below
    ("BRW-D01", [R + "12", R + "13", R + "6"], "Morey's Mariner's Landing Pier", "Wildwood, NJ", 1980, "The amusement pier: a broad timber deck on pile bents running out over the beach and surf, carrying the rides, games and a water flume, fenced, lit at night.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "ornamental_iron", "lighting": "string", "benches": True, "width_m": 90}),
]
WK[11] = ("BRW-W12", [B + "58"], "Ocean City boardwalk at 4th Street", "Ocean City, NJ", 2015, "A ramp to the beach at the quiet north end of the boardwalk, by the condominium blocks, timber with a pipe rail.", {"deck": "timber_plank", "substructure": "timber_piles", "rail": "pipe", "lighting": "lamp_posts", "benches": True, "width_m": 4})
for i, ph, t, p, y, br, tr in WK:
    tr.update({"pile_depth_m": 12.0 if i == "BRW-D01" else 10.0, "year_built": y})
    rec(i, ph, t, p, y, br + (" One photo." if len(ph) == 1 else f" {len(ph)} photos.") + " Year estimated where not stated; piles 10 m or more below the modelled bed.", tr, {})

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "brw.json"), "w"), indent=1)
print(len(out), "records")
