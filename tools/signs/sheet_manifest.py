"""The Grok sign sheets (research/flea_markets/08_signage_briefs.md): what is in every cell, in reading order.
One source for the prompts (B and C) and for crop_sheets.py's atlas index.

Each cell is a dict: id, kind, plus
  A (markets):  market (07 §2 number + slug), role (main | mascot | landmark | extra | shared), band, t
  B (islands):  family (pieces.json palettes key, or "shared"), slot (a fascia | b blade | c emblem | shared), desc
  C (business): band (north | south), biz (business type), desc (pictogram)
"""

# ---------------------------------------------------------------- A: markets (3 x 3, words painted in)
def _m(n, slug, band, t):
    return "fm%02d_%s" % (n, slug), band, t

ROPEWALK = _m(1, "ropewalk", "north", 0.00)
LOBSTER = _m(2, "lobster_pot", "north", 0.01)
TIDE = _m(3, "tide_clock", "north", 0.01)
NETLOFT = _m(4, "net_loft", "north", 0.01)
WATER = _m(5, "water_tower", "north", 0.24)
BOOK = _m(6, "book_barn", "north", 0.31)
VANE = _m(7, "weathervane", "north", 0.31)
BRANNOCK = _m(8, "brannock_trade_days", "north", 0.32)
BOATHOUSE = _m(9, "boathouse_swap", "river", 0.33)
FOURC = _m(10, "four_corners_swap", "river", 0.34)
REGATTA = _m(11, "regatta_swap", "river", 0.43)
MILL = _m(12, "millwheel_market", "river", 0.44)
TRADERS = _m(13, "traders_landing", "river", 0.58)
IRON = _m(14, "iron_wheel", "south", 0.68)
GRANARY = _m(15, "red_granary", "south", 0.68)
TAMARACK = _m(16, "tall_tamarack", "south", 0.69)
ELEVATOR = _m(17, "elevator_flea_days", "south", 0.71)
ROUTE30 = _m(18, "route30_swap_meet", "south", 0.72)
PULGA = _m(19, "la_pulga_verde", "south", 0.98)
STARLITE = _m(20, "starlite_swap", "south", 0.99)
CAROUSEL = _m(21, "carousel_swap", "south", 0.99)
PELICAN = _m(22, "pelican_swap", "south", 0.99)
SHARED = ("shared", "any", None)


def _a(m, role, what):
    return {"id": "%s_%s" % (m[0], role) if m[0] != "shared" else "shared_%s" % what,
            "kind": "market", "market": m[0], "role": role, "band": m[1], "t": m[2], "desc": what}


A = {
    "A1": [_a(ROPEWALK, "main", "barn-red board THE ROPEWALK"), _a(ROPEWALK, "mascot", "Salty the gull"),
           _a(LOBSTER, "main", "oval gilt board THE LOBSTER POT"), _a(LOBSTER, "landmark", "lobster trap + buoys"),
           _a(TIDE, "landmark", "tide clock face HIGH/LOW"), _a(TIDE, "main", "engraved slab THE TIDE CLOCK"),
           _a(NETLOFT, "main", "shingled gable THE NET LOFT"), _a(NETLOFT, "landmark", "net, floats, carved tern"),
           _a(WATER, "landmark", "water tower tank")],
    "A2": [_a(WATER, "main", "LOOMIS GROVE base board"), _a(BOOK, "landmark", "gilded open book THE BOOK BARN"),
           _a(BOOK, "main", "plaque FENWICK BOOK BARN & FLEA"), _a(VANE, "landmark", "bull weathervane"),
           _a(VANE, "main", "board THE WEATHERVANE"), _a(BRANNOCK, "main", "county fair arch"),
           _a(BRANNOCK, "extra", "bunting MARLOWE medallion"), _a(BOATHOUSE, "main", "boathouse gable Swap neon"),
           _a(BOATHOUSE, "mascot", "neon leaping fish")],
    "A3": [_a(FOURC, "main", "finger-post tree"), _a(REGATTA, "main", "sail pylon THE REGATTA SWAP"),
           _a(REGATTA, "extra", "regatta pennants"), _a(MILL, "landmark", "waterwheel with bulbs"),
           _a(MILL, "main", "oak slab MILLWHEEL MARKET"), _a(TRADERS, "main", "freighter bow TRADERS' Landing"),
           _a(TRADERS, "landmark", "lighthouse MARKET"), _a(TRADERS, "mascot", "Cap'n Harrow"),
           _a(SHARED, "shared", "island_fair_dotmatrix")],
    "A4": [_a(IRON, "main", "Moderne fin IRON WHEEL"), _a(IRON, "landmark", "locomotive wheel bulbs"),
           _a(GRANARY, "main", "granary gable Red Granary"), _a(TAMARACK, "landmark", "tamarack tree bulbs"),
           _a(TAMARACK, "main", "boomerang THE TALL TAMARACK"), _a(ELEVATOR, "main", "postcard ELEVATOR FLEA DAYS"),
           _a(ROUTE30, "landmark", "US 30 shield"), _a(ROUTE30, "main", "arrow SWAP MEET ROUTE 30"),
           _a(ROUTE30, "mascot", "Ozzie the mechanic")],
    "A5": [_a(PULGA, "main", "pier-palm pylon LA PULGA VERDE"), _a(STARLITE, "main", "screen tower STARLITE SWAP"),
           _a(STARLITE, "extra", "marquee THIS WEEKEND ISLAND FAIR"), _a(STARLITE, "mascot", "Sunny the sun"),
           _a(CAROUSEL, "landmark", "carousel horse"), _a(CAROUSEL, "main", "canopy THE CAROUSEL SWAP"),
           _a(PELICAN, "mascot", "pelican on piling"), _a(PELICAN, "main", "surfboard THE PELICAN SWAP"),
           _a(SHARED, "shared", "skein_banner")],
}

# ---------------------------------------------------------------- B: island families (4 x 4 blanks)
# (family id, label, (a), (b), (c))
B_FAM = {
    "B1": [
        ("maghrebi_medina", "Maghrebi medina", "a zellige-tile-bordered board in green, blue and white with a horseshoe-arch outline in LED",
         "a hanging pierced-brass lantern-style blade", "a glowing eight-point star emblem"),
        ("saharan_kasbah", "Saharan kasbah", "an ochre mud-plaster board with triangle-and-chevron relief and red LED edges",
         "a vertical board with a crenellated top", "a glowing Tuareg-cross-shaped lamp"),
        ("mzab_ghadames", "Mzab and Ghadames", "a whitewashed board with palm-rib framing and blue trim",
         "a palm-wood blade", "a glowing palm-tree motif"),
        ("cairene_mamluk", "Cairene Mamluk", "a striped ablaq (red and cream stone bands) board with a muqarnas top and gold LED",
         "a mashrabiya lattice blade", "a glowing coloured-glass fanous lantern"),
        ("levantine_courtyard", "Levantine courtyard", "a black-and-white stone board with a jasmine-vine border",
         "a wrought-iron bracket sign", "a glowing pomegranate emblem"),
        ("shared", "mooring_office", "a Mooring Office sign blank: white board, navy rope border, an anchor-and-gondola pictogram"),
    ],
    "B2": [
        ("hejazi_roshan", "Hejazi roshan", "a carved teak roshan-lattice frame board in turquoise and white",
         "a vertical lattice blade", "a glowing coffee-pot (dallah) emblem"),
        ("yemeni_tower", "Yemeni tower", "a brown board with white gypsum zigzag bands and a qamariya half-moon stained-glass window top",
         "a tall narrow tower-shaped blade", "a glowing qamariya rainbow-glass half-moon"),
        ("omani_oasis", "Omani oasis", "a sand-coloured board with a carved wooden door-stud border",
         "a frankincense-burner-shaped blade", "a glowing khanjar-curve emblem"),
        ("persian_desert", "Persian desert", "a turquoise-and-cobalt tile board with an arabesque border",
         "a windcatcher-shaped vertical sign", "a glowing tiled dome emblem"),
        ("silk_road", "Silk Road", "a blue majolica board with a carved wooden ivan frame",
         "a suzani-embroidered hanging banner", "a glowing camel-caravan emblem"),
        ("shared", "weigh_house", "a Weigh House sign blank: brass board, a balance-scale pictogram"),
    ],
    "B3": [
        ("mughal_walled", "Mughal walled city", "a red sandstone board with white marble inlay (pietra dura flowers) and gold LED",
         "a scalloped-arch blade", "a glowing lotus emblem"),
        ("rajput_sandstone", "Rajput sandstone", "a golden sandstone board with jharokha balcony carving and mirror-work sparkle",
         "a mirror-embroidered hanging banner", "a glowing peacock emblem"),
        ("ganga_ghat", "Ganga ghat", "a saffron-and-marigold board with marigold-garland LED",
         "a brass-bell blade", "a glowing oil-lamp (diya) emblem drawn as an electric bulb"),
        ("karachi", "Karachi", "a truck-art board, every inch painted with flowers, chains and borders in hot colours with chrome edges",
         "a truck-art hanging panel with chain fringe", "a glowing truck-art eye-and-flower motif"),
        ("newar", "Newar", "a carved dark-timber board with a torana arch and copper-gold trim",
         "a pagoda-roof blade", "a glowing plain stupa-dome emblem"),
        ("shared", "gondola_station", "a gondola station sign blank: sky blue board, a gondola-cabin-on-rope pictogram"),
    ],
    "B4": [
        ("tibetan_lhasa", "Tibetan Lhasa", "a black-framed window-shaped board with a red-and-white striped valance",
         "a prayer-flag strip blade with blank flags", "a glowing endless-knot emblem"),
        ("chongqing_cliff", "Chongqing cliff", "a stacked-signs board in red and yellow LED with a metal frame",
         "a vertical red lightbox", "a glowing chili-pepper emblem"),
        ("hakka_tulou", "Hakka tulou", "a round earthen-wall-coloured board with a black tile eave",
         "a red paper-lantern pair blade", "a glowing round tulou-ring emblem"),
        ("jiangnan_water", "Jiangnan water town", "a white-wall black-tile board with a grey horse-head gable",
         "a hanging cloth shop banner with an empty panel", "a glowing lotus-pond emblem"),
        ("kowloon_walled", "Kowloon walled city", "a dense cluster of mismatched small blank lightboxes on a steel frame",
         "a projecting arm sign", "a glowing dragon-silhouette emblem"),
        ("shared", "lowliner_line_hall", "a Lowliner Line Hall sign blank: knotted-rope border round an empty panel, a lantern hanging below"),
    ],
    "B5": [
        ("hk_neon_canyon", "Hong Kong neon canyon", "a big neon-tube-framed board in pink and cyan",
         "a two-storey neon arm-sign frame", "a glowing neon fish emblem"),
        ("taipei_tiepi", "Taipei tiepi", "a corrugated-metal board with green-and-red LED edging",
         "a vertical lightbox column", "a glowing bubble-tea-cup emblem"),
        ("japan_yokocho", "Japan yokocho", "a wooden noren-curtain board under a row of red paper chochin lanterns",
         "a vertical lit sign column panel", "a glowing red chochin lantern"),
        ("korean_hillside", "Korean hillside", "a pastel-blue board with dancheong-painted eave edges",
         "a vertical LED board", "a glowing round sun-and-cloud emblem"),
        ("shared", "tent_plank", "a tent plank sign blank: hand-painted wood with clan-colour stripes"),
        ("shared", "tent_plank_curved", "a second tent plank blank with a curved top and a bulb edge"),
        ("shared", "clan_pennants", "a clan pennant set: six blank pennants in different colours"),
        ("shared", "fare_board", "a fare board blank: a black board with a brass rope edge and an empty price list area"),
    ],
    "B6": [
        ("viet_tube", "Viet tube house", "a narrow yellow facade board with a green shutter frame",
         "a vertical red-and-yellow banner", "a glowing silk-lantern emblem"),
        ("siam_khlong", "Siam khlong", "a teak board with a gilded chofa gable flourish",
         "a boat-prow blade", "a glowing lotus-bud emblem"),
        ("manila_estero", "Manila estero", "a jeepney-style board with chrome edges and painted stripes",
         "a capiz-shell window blade", "a glowing parol star lantern"),
        ("straits_shophouse", "Straits shophouse", "a pastel shophouse fascia with a Peranakan tile border",
         "a vertical black-lacquer board with gold edge", "a glowing phoenix-and-peony tile emblem"),
        ("rupestrian_terraces", "Rupestrian terraces", "a tufa-stone board carved into rock with an iron lamp",
         "a wrought-iron blade", "a glowing bread-loaf emblem"),
        ("shared", "crew_tent", "a Crew Tent sign blank: white board, a rope coil and helmet pictogram"),
    ],
    "B7": [
        ("andean_neo", "Andean neo", "a cholet-style board with bright mirrored-glass colours and Andean step-pattern borders",
         "a vertical aguayo-weave banner", "a glowing condor-silhouette emblem"),
        ("latin_hillside", "Latin hillside", "a brightly painted favela-colour board with tile edges",
         "a hand-painted hanging sign", "a glowing hummingbird emblem"),
        ("creole_colonial", "Creole colonial", "a pastel board with wrought-iron lace corners",
         "a cast-iron bracket blade", "a glowing magnolia-flower emblem"),
        ("nouvelle_france", "Nouvelle-France", "a carved wooden board with a bell-cast roof flourish in red and white",
         "a wrought-iron blade", "a glowing maple-leaf emblem"),
        ("lusitanian_hill", "Lusitanian hill", "a blue-and-white azulejo tile board",
         "a tiled blade", "a glowing sardine emblem"),
        ("shared", "low_lashing_banner", "a Low Lashing banner blank: a long festival banner with lanterns and an empty centre"),
    ],
    "B8": [
        ("iberian_white", "Iberian white town", "a whitewashed board with a yellow-ochre border and a hand-painted tile panel",
         "a canvas awning blade", "a glowing flowerpot emblem"),
        ("cycladic", "Cycladic", "a white board with a blue dome-arch top",
         "a blue shutter blade", "a glowing windmill emblem"),
        ("tyrrhenian_canyon", "Tyrrhenian canyon", "a pastel-orange board with green shutters",
         "a ceramic lemon-painted blade", "a glowing lemon emblem"),
        ("knights_harbour", "Knights' harbour", "a honey-limestone board with a carved baroque frame",
         "a coloured enclosed-balcony (gallarija) blade", "a glowing eight-point star emblem"),
        ("ottoman_timber", "Ottoman timber", "a dark timber board with a projecting cumba bay and an Iznik tile inset",
         "a hanging carved blade", "a glowing tulip emblem"),
        ("shared", "market_warden", "a market warden's sign blank: green board, a balance and a key pictogram"),
    ],
    "B9": [
        ("hanseatic_gable", "Hanseatic gable", "a stepped-gable brick-red board with white trim",
         "a wrought-iron guild bracket sign with an empty hanging panel", "a glowing cog-ship emblem"),
        ("scots_lands", "Scots lands", "a dark-stone board with a crow-step gable top and a tartan stripe",
         "a painted pub-style hanging board", "a glowing thistle emblem"),
        ("kulla_stone", "Kulla stone", "a grey fieldstone board with a tiny arrow-slit window and red-black textile trim",
         "a carved wooden blade", "a glowing eagle-feather emblem"),
        ("caucasian_balcony", "Caucasian balcony", "a carved fretwork balcony-railing board in blue and white",
         "a grapevine iron blade", "a glowing grape-cluster emblem"),
        ("mardin_terraces", "Mardin terraces", "a carved honey-stone board with arched niches",
         "a copper-plate blade", "a glowing copper-coffee-pot emblem"),
        ("shared", "rope_steward", "a rope steward ground-station sign blank: orange safety board, a rope-and-hook pictogram"),
    ],
}


def _b_cells(rows):
    out = []
    for r in rows:
        if r[0] == "shared":
            out.append({"id": "sky_shared_%s" % r[1], "kind": "island", "family": "shared", "slot": "shared",
                        "desc": r[2]})
            continue
        fam, label = r[0], r[1]
        for slot, desc, word in zip("abc", r[2:], ("fascia", "blade", "emblem")):
            out.append({"id": "sky_%s_%s" % (fam, word), "kind": "island", "family": fam, "slot": slot,
                        "label": label, "desc": desc})
    return out


B = {k: _b_cells(v) for k, v in B_FAM.items()}

# ---------------------------------------------------------------- C: city business (4 x 4 blanks)
BIZ = [
    ("grocery", "a produce crate"), ("bakery", "a wheat sheaf and loaf"), ("butcher", "a cleaver and steer"),
    ("fish_market", "a fish on ice"), ("cafe", "a steaming cup"), ("diner", "a pie slice"),
    ("restaurant", "a fork, knife and plate"), ("bar", "a tankard"), ("liquor", "a bottle and glass"),
    ("hardware", "a hammer and saw"), ("clothing", "a coat on a hanger"), ("thrift", "a teapot and lamp"),
    ("bookstore", "an open book"), ("jeweller", "a ring and gem"), ("florist", "a bouquet"),
    ("furniture", "an armchair"),
    ("sporting_goods", "a baseball and racquet"), ("charge_stop", "a plug and lightning bolt"),
    ("newsagent", "a folded newspaper"), ("drug_store", "a mortar and pestle"),
    ("doctor", "a plain cross and a tooth"), ("barber", "a striped barber pole"),
    ("beauty_salon", "scissors and comb"), ("laundromat", "a washing tub"),
    ("bank", "a classical columned facade"), ("office", "a quill and ledger"), ("print_shop", "a press roller"),
    ("repair", "a wrench and gear"), ("funeral_home", "a laurel wreath"), ("movie_theatre", "a film reel"),
    ("arcade", "a pinball flipper"), ("hotel", "a key and bed"),
]


def _c_cells(band, part):
    return [{"id": "biz_%s_%s" % (band, b), "kind": "business", "band": band, "biz": b, "desc": d}
            for b, d in BIZ[part * 16:(part + 1) * 16]]


C = {"C1": _c_cells("north", 0), "C2": _c_cells("north", 1), "C3": _c_cells("south", 0), "C4": _c_cells("south", 1)}

SHEETS = {}
for d, grid in ((A, 3), (B, 4), (C, 4)):
    for k, cells in d.items():
        assert len(cells) == grid * grid, (k, len(cells))
        SHEETS[k] = {"grid": grid, "cells": cells}

ATLAS_OF = {"A": "markets", "B": "sky", "C": "biz"}

# ---------------------------------------------------------------- G: street-life sheets (phase 2, 2026-10-15)
def _g(sheet, kind, names, band="any"):
    return [{"id": "%s_%s" % (kind, n), "kind": kind, "band": band, "desc": n.replace("_", " "), "sheet_item": n}
            for n in names]


G = {
    "G1": (4, 4, _g("G1", "mascot", ["pocket_watch", "boot", "key", "spectacles", "tooth", "anvil", "coffee_pot", "teapot",
                                     "scissors", "horseshoe", "pretzel", "codfish", "top_hat", "mortar_pestle",
                                     "pawn_balls", "ship_in_bottle"], "north")),
    "G2": (4, 4, _g("G2", "mascot", ["donut", "hot_dog", "ice_cream", "taco", "hamburger", "coffee_cup", "surfboard_palm",
                                     "flamingo", "cactus", "cowboy_boot", "googie_rocket", "orange", "chili", "pelican",
                                     "car_wash", "milkshake"], "south")),
    "G3": (3, 2, _g("G3", "billboard", ["soda_family", "tram_bridge", "oranges_sun", "armchair_lamp", "noodles",
                                        "sky_island"])),
    "G4": (2, 4, _g("G4", "poster", ["lantern_festival", "county_fair", "big_band", "regatta", "circus", "harvest",
                                     "night_market", "lighthouse"])),
    "G5": (4, 4, _g("G5", "small", ["a_frame_chalk", "menu_chalkboard", "menu_bracket", "menu_lightbox", "open_neon",
                                    "hours_brass", "open_closed_placard", "sandwich_board", "flag_banner", "feather_banner",
                                    "pennant_string", "price_tag", "sale_burst", "arrow_sign", "oval_cameo",
                                    "round_bracket"])),
    "G6": (4, 4, _g("G6", "stall", ["striped_valance", "scalloped_pelmet", "clan_plank", "rope_board", "tent_flag",
                                    "knot_badge", "lantern_banner", "paper_lantern_marker", "rug_sign", "kite_sign",
                                    "crate_end", "goose_wing", "bell_sign", "balloon_sign", "rope_round",
                                    "bamboo_streamers"], "island")),
    "G7": (5, 5, _g("G7", "goods", ["brass_lamp", "mantel_clock", "apple_crate", "rolled_rug", "old_books", "radio",
                                    "tea_set", "framed_painting", "rocking_chair", "records", "bicycle", "tools",
                                    "vase_flowers", "boots", "honey_jar", "egg_basket", "toy_robot", "quilt",
                                    "sewing_machine", "bananas", "lantern", "guitar", "plates", "typewriter", "fern"], "floor")),
    "G8": (5, 5, _g("G8", "goods", ["knit_sweater", "rope_coil", "honey_dipper", "goat_cheese", "dried_fish", "down_quilt",
                                    "dyed_yarn", "brass_bell", "barometer", "sailcloth", "ice_blocks", "moss_bundle",
                                    "berries", "mead", "beeswax_candles", "dove_cage", "map_scroll", "box_kite",
                                    "smoked_ham", "pickled_greens", "woven_basket", "felt_hat", "lark_fan",
                                    "glass_lantern", "knotted_cord"], "island")),
    "G9": (4, 4, _g("G9", "festoon", ["red_lantern", "white_lantern", "brass_lantern", "fanous", "bulb_string",
                                      "pennant_string", "lantern_string", "parol", "chochin", "lotus_lantern", "led_star",
                                      "led_snowflake", "prayer_flags", "tiki_torch", "balloons", "neon_flower"], "island")),
    "G10": (4, 4, _g("G10", "decal", ["gold_scroll", "gilt_arch", "flourish", "laurel_crest", "neon_coffee",
                                      "neon_cocktail", "neon_pizza", "neon_note", "neon_star", "neon_heart", "neon_arrow",
                                      "neon_palm", "mural_sunset", "mural_lighthouse", "ghost_frame", "mural_oranges"])),
}
for k, (r, c, cells) in G.items():
    assert len(cells) == r * c, (k, len(cells))
    SHEETS[k] = {"grid": c, "rows": r, "cols": c, "cells": cells}
