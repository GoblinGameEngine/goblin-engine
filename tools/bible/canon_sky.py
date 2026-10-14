"""Columbia game bible: the sky islands -- the Hundred, the Skein and the Aloft (2026-10-14).

The user's brief is in research/sky_islands/00_plan.md (the contract: 750 m deck, 100 m x 1 km envelopes, docking at
3 km, rafts of at most ten islands lashed for three days, one plumb (descender) per clan, two-person larks).
The research behind these choices is research/sky_islands/01-05; this module is the canon as data.  make_bible.py
calls build() and writes godot_project/remake/bible/sky_islands.json and research/bible/13_sky_islands.md.

Deterministic: every pick hashes (seed, island) -- no RNG state.
"""
import hashlib
import json
import math
import os

# each island's architectural style (tools/sky/styles.py assigns them from this canon's own fields, so it runs after a
# first pass: make_bible -> styles.py -> make_bible)
_STYLE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "godot_project", "remake", "sky", "style_assign.json")
_STYLES = json.load(open(_STYLE_FILE))["assign"] if os.path.exists(_STYLE_FILE) else {}

SEED = "sky-2026-10-14"

# --- the fixed numbers of the contract ---------------------------------------------------------------------------
DECK_H = 750.0                    # m above the floor
R = 10000.0
OMEGA = math.sqrt(9.8 / R)        # rad/s (0.0313: g 1.0 at the floor)
BLOCK_M2 = 8000.0
ENVELOPE = {"diameter_m": 100.0, "height_m": 1000.0, "base_above_deck_m": 60.0}
DOCK_RANGE_M = 3000.0
DOCK_GAP_M = 26.0
RAFT_MAX = 10
RAFT_DAYS = 3
BRIDGE_STYLES = ["bascule_timber", "bascule_iron", "telescope_truss", "rope_lowered", "jackknife", "swing_girder",
                 "rolling_lift", "scissor_lattice", "gangplank_rail", "chain_drawbridge"]


def h01(*parts):
    return int.from_bytes(hashlib.blake2b("|".join(map(str, (SEED,) + parts)).encode(), digest_size=8).digest(), "little") / 2 ** 64


def pick(seq, *key):
    return seq[int(h01(*key) * len(seq)) % len(seq)]


def wpick(weights, *key):
    tot = sum(weights.values())
    r = h01(*key) * tot
    for k, w in weights.items():
        r -= w
        if r <= 0:
            return k
    return k


def balloons(blocks):
    return math.ceil(1.6 * blocks) + 1


def larks(blocks):
    return 2 + blocks // 3


# --- physics (research/sky_islands/01_physics.md) ------------------------------------------------------------------
def physics():
    r = R - DECK_H
    rim = OMEGA * r
    g_deck = OMEGA ** 2 * r / 9.8
    v_drift = 6.0
    g_drift = (rim - v_drift) ** 2 / r / 9.8
    v_env = math.pi * 50.0 ** 2 * 1000.0
    rho = 1.06                    # kg/m3: mean air density over 810-1,810 m (floor 1.20; scale height ~9 km at <1 g)
    lift_h2 = rho * (1 - 2.016 / 28.97) * v_env / 1000.0     # t, gross
    env_area = math.pi * 100.0 * 1000.0 + 2 * math.pi * 50.0 ** 2
    env_mass = env_area * 0.22 / 1000.0 + 90.0              # t: skycloth 220 g/m2 + net, rigging, tether
    net = lift_h2 - env_mass
    return {
        "deck_radius_m": r, "rim_speed_ms": round(rim, 1), "g_deck": round(g_deck, 3),
        "g_drifting_west_6ms": round(g_drift, 3),
        "eotvos_rule": "an island running antispinward (west) at v m/s relative to the floor feels g x (1 - v/290)^2: at its 6 m/s drift ~0.887 g. "
                       "Lift and weight both scale with g, so a lighter g does not by itself float anything; what the Aloft exploit is that the envelopes "
                       "reach up 1 km into faster westerly air, which drags the whole island west faster than the air round its deck. Relative to the "
                       "air it sits in, the island is running antispinward, so it weighs less against that air's buoyancy: about 2% (2 x 3 m/s / 290 m/s), "
                       "which on a 30,000 t island is 600 t -- the weight of all its trade. They call it the Lightening.",
        "envelope_volume_m3": round(v_env), "air_density_kg_m3": rho, "lift_gross_t": round(lift_h2), "envelope_mass_t": round(env_mass),
        "lift_net_t": round(net), "gas": "hydrogen, made aboard by electrolysis of cloud water and snowmelt; skycloth loses about 0.3% of an envelope's gas a week (and air creeps in), "
               "~3,400 m3 a day an envelope, ~15 MWh of electrolysis (4.5 kWh/m3)",
        "power": "the sunskin: the Steward's envelopes were skinned in photovoltaic film; half an envelope's 314,000 m2 faces the Sunline at a time, and even "
                 "aged to a few per cent efficiency it makes ~40 MWh a day -- enough for the gas, the winches and the island. The Aloft can patch sunskin but not "
                 "make it: new envelopes of plain skycloth must be carried by the old, which is why an island's oldest envelope is its treasure; roofs add a little "
                 "from rationed floor cells",
        "mass_per_block_t": {"shell (foamed stone crust 1.2-2 m, ribs)": 3600, "deck slab (lightweight)": 1400, "buildings (light frame, cloth and board)": 3600,
                             "soil, stores, goods": 1300, "ponds and lakes (ballast, trimmed)": 900, "people (~250)": 15, "total": 10815},
        "lift_per_block_t": "balloons(N) x net lift / N: 1 block 3 envelopes (22,000 t of lift for ~10,500 t: small islands are buoyant and carry ballast water), "
                            "10 blocks 17 envelopes (~12,500 t a block: a 15% margin before the Lightening, and the ponds can be drained for 900 t more)",
        "foamed_stone": "the rock is 'skystone': foamed glass-ceramic the Steward cast from the Spindle's slag, 120-250 kg/m3 (real foam glass is 100-300 kg/m3), "
                        "a crust over a honeycomb of sealed cells; it looks like dark volcanic rock, floats on water, and moss roots in its pores",
        "cold": "about 5 C colder than the floor at the deck (environmental lapse ~6.5 C/km), more in the wind; the envelopes' tops near 1.8 km are ~11 C colder",
        "snow": "the Steward keeps the cloud interiors cold (since VY 212 it has made the floor's rain as snow aloft, melting on the way down -- the cold-rain "
                "process of real clouds); an island passing through a cloud is snowed on, and the snow lies till the sun and the dry air take it slowly",
        "water": "fog and cloud nets (real fog collectors yield 3-10 L/m2/day in fog; inside a Columbia cloud the nets run for hours) and snowmelt",
    }


# --- jobs ---------------------------------------------------------------------------------------------------------
# id: (name, what, base weight per 1,000 workers, why it exists aloft)
JOBS = {
    "rigger": ("rigger", "climbs the tethers and the envelope nets; inspects, splices and trims the rigging", 60, "the envelopes are the island's life; every line is walked weekly"),
    "envelope_wright": ("envelope wright", "cuts, seams and patches skycloth; builds new envelopes over years", 35, "skycloth leaks and wears; an envelope lasts about 40 years"),
    "gas_maker": ("gas maker", "runs the electrolysis halls that split cloud water into hydrogen; keeps the gas books", 30, "the envelopes lose about 1% of their gas a week"),
    "winch_hand": ("winch hand", "runs the winches and capstans: hoists, lashings, the bridges", 40, "everything that comes aboard comes up a line"),
    "line_rocketeer": ("line rocketeer", "fires the cold (compressed-gas) line rockets that carry the first messenger lines across to another island", 8, "lashing begins with a 3 km shot"),
    "net_keeper": ("net keeper", "tends the cloud nets and snow troughs that are the island's water, and the cisterns", 30, "no river reaches 750 m"),
    "roof_grower": ("roof grower", "farms the roofs: greens, beans, berries, herbs, rooftop grain in boxes", 120, "every roof is a garden; every kilo of food grown aloft is a kilo not hoisted"),
    "beekeeper": ("beekeeper", "keeps the cold-hardy bees of the roof gardens; honey and wax", 8, "bees are the gardens' pollinators aloft"),
    "dove_keeper": ("dove keeper", "keeps pigeons and doves: eggs, meat, down, and messages between islands", 12, "birds carry word across the gap before the rockets fly"),
    "moss_grower": ("moss gatherer", "harvests the underside's moss and vines from cradles slung under the rim: dye, medicine, packing, bedding", 15, "the underside garden is the only wild place aloft"),
    "snow_hand": ("snow hand", "clears roofs and paths of snow after a cloud, packs it into the cisterns and the ice houses", 15, "a deep fall weighs hundreds of tonnes"),
    "weigher": ("weigher", "keeps the island's weight book: every load hoisted or dropped, every birth and death; trims ballast", 10, "weight is the first law aloft"),
    "cook": ("cook", "cooks in the long kitchens; electric only -- no flame under hydrogen", 55, "most islands eat together"),
    "healer": ("healer", "treats the sick and injured: falls, frost, line burns, ground-sickness", 15, "the floor's hospitals are a day away"),
    "teacher": ("teacher", "teaches the children: reading, figures, knots, weather, the weight book", 30, "children are the island's future weight"),
    "child_minder": ("child minder", "runs the crèche rooms while parents work the lines", 20, "the lines are no place for small children"),
    "mender": ("mender", "carpenter and fixer: light framing, panels, stairs, roofs, fences", 50, "everything aloft is light, so everything needs mending"),
    "sparks": ("sparks", "the electricians: Sunline collectors on the roofs, cells, the Thirty-Two boards that run the winches and books", 20, "power is light caught on the roofs"),
    "smith": ("smith", "light-metal work: aluminium and titanium from the floor, cold-worked and riveted (no forges)", 10, "a forge's flame is forbidden aloft"),
    "roper": ("roper", "spins and lays cordage: tethers, lashing hawsers, nets", 25, "the Skein is tied together with rope"),
    "weaver": ("weaver", "weaves skycloth for envelopes, and wool and down cloth for clothes", 30, "the Aloft dress warm and trade their cloth"),
    "knitter": ("knitter", "knits the island's colours: hats, mittens, ganseys, leggings", 20, "the cold is constant; the patterns say who you are"),
    "tailor": ("tailor", "cuts coats and the quilted down jackets", 12, "a coat aloft is a life"),
    "bridgewright": ("bridgewright", "keeps the island's bridges; rigs the bridges at a lashing", 8, "the bridges are each island's pride and style"),
    "fence_warden": ("fence warden", "walks the rim fences; rescue on the edge and in the nets", 12, "a fall from the rim is 750 m"),
    "hoist_master": ("hoist master", "runs the scheduled cargo drops: lines down, containers up, the floor-side manifest", 10, "trade hangs on the hoist schedule"),
    "factor": ("factor", "trader: buys and sells for the island, at lashings and by hoist; keeps the clan's accounts", 25, "the Aloft live by trade"),
    "plumb": ("plumb", "the clan's descender: flies the lark to the floor to trade, bargain and bring word back; one chosen at a time, with a second", 3, "someone has to go down"),
    "lark_wright": ("lark wright", "builds and keeps the larks (the clan's high-performance aerostats) and their mooring cradles", 6, "a lark that fails falls"),
    "weather_reader": ("weather reader", "reads the clouds, fronts and winds; plans the island's trim; sells forecasts to the floor", 8, "the island goes where the wind goes; the reader says where that is"),
    "knot_keeper": ("knot keeper", "keeps the island's law and records in knotted cords and books; arbitrates at lashings", 4, "the Skein has no courts; it has knot keepers"),
    "box_tender": ("box tender", "watches over the Steward's Box (the sealed cloud engine on the island's mast) and keeps people from it", 2, "the Box is the bargain the Hundred live by"),
    "brewer": ("brewer", "brews the cold beers, meads and berry wines", 6, "the lashing needs drink"),
    "musician": ("musician", "bell-ringer, singer, fiddler: bell-speech across the gap; the lashing dances", 6, "bells carry where voices don't"),
    "cleaner": ("compost hand", "keeps the compost works and the water closets: nothing is wasted or dropped", 25, "every gram of soil was hoisted"),
    "shopkeeper": ("shopkeeper", "keeps the island's stores and stalls", 20, "the island's own market"),
    "herder": ("herder", "keeps the goats and sheep on the hill pastures and roof paddocks; milking, shearing, slaughter", 30, "milk, wool and meat that never had to be hoisted"),
    "poultry_keeper": ("poultry keeper", "keeps hens, ducks, geese and rabbits in the roof coops and the pond margins", 18, "eggs every day, feathers for the down trade"),
    "pond_keeper": ("pond keeper", "keeps the ponds and lakes: water level (the island's ballast), the fish, the reeds, the ice in winter", 10, "the ponds are reservoir, ballast, fishery and the island's commons at once"),
    "elder_counsel": ("counsel", "elders who sit on the island's council and teach the young the lines", 6, "the old know the winds"),
}

# specialties: (id, name, job boosts, trade goods, needs)
SPECIALTIES = [
    ("skycloth", "skycloth weavers", {"weaver": 3.0, "envelope_wright": 2.0}, ["skycloth (envelope fabric)", "sailcloth", "tents"], ["linen and hemp fibre", "dyes"]),
    ("cordage", "rope makers", {"roper": 3.5, "rigger": 1.3}, ["rope and hawser", "nets", "lashing line"], ["hemp fibre", "tar"]),
    ("knitwear", "knitters and dyers", {"knitter": 4.0, "weaver": 1.5, "moss_grower": 1.5}, ["knitwear (ganseys, mittens, hats)", "moss dyes"], ["raw wool", "mordants"]),
    ("down", "down pluckers and quilters", {"dove_keeper": 3.5, "tailor": 2.0}, ["down quilts and jackets", "feathers", "dove eggs"], ["grain feed", "cotton ticking"]),
    ("honey", "beekeepers", {"beekeeper": 6.0, "roof_grower": 1.3, "brewer": 2.0}, ["sky honey", "mead", "beeswax candles (for the floor only)"], ["glass jars", "sugar"]),
    ("weather", "weather readers", {"weather_reader": 6.0, "dove_keeper": 1.5}, ["forecasts for farms and the Aerostat Guild", "barometers (assembled)"], ["Thirty-Two boards", "paper"]),
    ("ice", "ice cutters", {"snow_hand": 4.0, "net_keeper": 1.5}, ["snow and ice (a wonder on the floor since the Last Snow)", "ice cream"], ["insulated crates", "salt"]),
    ("moss", "moss gatherers and healers", {"moss_grower": 5.0, "healer": 2.0}, ["sky moss (wound packing, tea, dye)", "vine baskets", "remedies"], ["medicine from the Chutes", "glass"]),
    ("larks", "lark wrights", {"lark_wright": 6.0, "sparks": 1.5, "smith": 2.0}, ["lark repairs and parts", "fans and envelopes for the Aerostat Guild"], ["boards", "LFP cells", "aluminium"]),
    ("bells", "bell founders and music", {"musician": 5.0, "smith": 2.0}, ["cold-cast bells, chimes, fiddles", "songs"], ["bronze scrap", "wire"]),
    ("brewing", "brewers", {"brewer": 6.0, "roof_grower": 1.2}, ["cold beer", "berry wine", "mead"], ["barley", "hops", "bottles"]),
    ("survey", "map makers", {"weather_reader": 2.0, "knot_keeper": 2.0, "factor": 1.5}, ["aerial surveys and maps of the floor", "a view for hire"], ["paper", "ink", "lenses"]),
    ("courier", "air-post carriers", {"plumb": 2.0, "dove_keeper": 3.0, "lark_wright": 2.0}, ["air post: urgent letters and parcels by lark and dove"], ["cells", "paper"]),
    ("dried", "food driers", {"cook": 2.0, "roof_grower": 1.5}, ["freeze-dried berries and greens", "air-cured meats"], ["meat on the hoof (goats)", "salt"]),
    ("gas", "gas makers", {"gas_maker": 4.0, "sparks": 2.0}, ["hydrogen in bottles for other islands", "gas-making service"], ["electrodes", "cells"]),
    ("lore", "knot keepers and teachers", {"knot_keeper": 5.0, "teacher": 2.0}, ["arbitration", "teaching", "copied books"], ["paper", "books from the floor"]),
    ("gardens", "orchard keepers", {"roof_grower": 2.5, "beekeeper": 2.0}, ["dwarf apples, currants, gooseberries", "seed stock"], ["soil", "fertiliser"]),
    ("wool", "shepherds and spinners", {"herder": 4.0, "knitter": 1.5, "weaver": 1.5}, ["fleece and yarn", "felt", "goat cheese"], ["hay and feed", "salt licks"]),
    ("fish", "pond fishers", {"pond_keeper": 5.0, "cook": 1.3}, ["smoked-cold and air-dried perch", "crayfish", "fingerlings for other islands' ponds"], ["fish feed", "net twine"]),
    ("trade", "factors and brokers", {"factor": 4.0, "hoist_master": 2.5, "shopkeeper": 2.0}, ["brokerage between islands and the floor", "goods of the whole Skein"], ["everything"]),
]

GOVERNANCE = [
    ("helm", "the Helm: a captain chosen for a year by every adult, who steers the trim and speaks at lashings"),
    ("council_elders", "a council of elders (the Old Lines) by seniority on the ropes"),
    ("lot", "a council drawn by lot every season from all over sixteen (sortition)"),
    ("mother_house", "the mother house: the eldest woman of each line sits; descent and homes pass through mothers"),
    ("guild", "the work-crews govern: riggers, gas makers, growers and factors each send a voice"),
    ("consensus", "the whole island in the long kitchen until all agree (it can take days)"),
    ("plumb_rule", "the plumb and the weigher jointly: the trading houses run the island"),
]

CUSTOMS = [
    ("cord_names", "each child is given a knotted cord at birth; a knot is added for every lashing they cross a bridge at"),
    ("bell_speech", "bell-speech: islands talk across the gap in rung patterns before the lines are shot"),
    ("silent_dusk", "no one speaks while the Sunline leaves the sky; the island watches it go north in silence"),
    ("long_kitchen", "every meal is eaten together in the long kitchen; eating alone is for the sick"),
    ("rope_marks", "rope marks: rigger lines tattoo a turn of rope round the wrist for each envelope they've walked"),
    ("snow_feast", "the snow feast: the first snow of every cloud is eaten with honey before it's swept"),
    ("weighing_day", "Weighing Day: every person is weighed at midwinter and the weight book read aloud"),
    ("dead_go_down", "the Long Drop: the dead go down in a hoist container to the floor's Return halls -- the only time most go to the floor"),
    ("matrilocal", "a husband crosses the bridge to his wife's island at a lashing; children are of their mother's clan"),
    ("patrilocal", "a wife crosses to her husband's island at a lashing; children take their father's clan"),
    ("chosen_island", "at sixteen every youth may choose to cross to any island at a lashing; most stay"),
    ("kite_mail", "kite mail: messages flown on kites to islands downwind"),
    ("no_birds", "they keep doves but never eat birds: a bird is a cousin who flies without help"),
    ("cloud_singing", "cloud singing: the whole island sings in a cloud, so no one is lost in the white"),
    ("rail_dancing", "the young dance on the rim rails at lashings (illegal on the floor; a rite aloft)"),
    ("guest_weight", "a guest brings their weight in gifts (in practice a token, weighed with ceremony)"),
    ("quiet_box", "no one says the Steward's name within sight of the Box; they call it 'the neighbour'"),
    ("lantern_vigil", "a night vigil with electric lanterns on the rim whenever an island is lost from sight"),
    ("down_debt", "a plumb who goes down owes the island a story at the long kitchen on return"),
    ("two_names", "everyone has a sky name and a floor name; the floor name is for dealing with groundfolk"),
    ("ballast_children", "children are 'ballast' -- a blessing: the island is steadier for them"),
    ("tether_vows", "marriages are vowed with a tether splice: the couple splice two ropes into one"),
    ("map_walls", "the walls of the long kitchen are painted with every island they've lashed with"),
    ("feather_coats", "feather-trimmed coats for elders; the more lashings, the more feathers"),
]

SKY_FAITHS = [
    ("sunward", "the Sunward: the soul rises toward the Sunline; the Aloft are halfway there", 0.30),
    ("waymakers", "the Waymakers (floor faith; strong aloft: 'the voyage is the pilgrimage, and we are on deck')", 0.18),
    ("catholic", "Catholic (the Columbian Rite), with Our Lady of the Winds", 0.14),
    ("lakes_union", "the Lakes Union Church", 0.07),
    ("full_gospel", "Full Gospel", 0.06),
    ("muslim", "Muslim (the qibla reckoned by the knot keepers' tables)", 0.05),
    ("dharmic", "Dharmic", 0.03),
    ("jewish", "Jewish", 0.02),
    ("none", "none in particular: 'the wind is enough'", 0.15),
]

HERITAGES = {"anglo": 22, "hispanic": 14, "polish": 7, "black_anglo": 9, "black": 5, "francophone": 6, "german": 5, "irish_scots": 6, "italian": 4,
             "east_asian": 6, "south_asian": 4, "se_asian": 3, "arab": 3, "scandinavian": 3, "slavic": 3, "indigenous": 3, "hungarian": 2, "greek": 2,
             "dutch": 2, "multi": 6, "station_coined": 6}

# the clans' colours: the knit palettes (outfit generator).  Hex: [main, second, accent]
PALETTES = [
    ["#8c2f2b", "#e8dcc4", "#2b3a55"], ["#1f4e5f", "#d9b44a", "#f2efe6"], ["#5b3a6e", "#c9a0dc", "#efe7d2"], ["#2e5e3a", "#a8c47a", "#3b2a1a"],
    ["#b5651d", "#f3e2c0", "#4a3226"], ["#22303c", "#7fa7c9", "#e7eef3"], ["#9e2a5b", "#f0c9d6", "#2a2a2a"], ["#3d5a80", "#ee6c4d", "#e0fbfc"],
    ["#6b4f2a", "#d4a373", "#faedcd"], ["#264653", "#e9c46a", "#f4a261"], ["#7a1f2b", "#1d3557", "#f1faee"], ["#4a4e69", "#c9ada7", "#f2e9e4"],
    ["#335c67", "#fff3b0", "#9e2a2b"], ["#283618", "#dda15e", "#fefae0"], ["#5f0f40", "#fb8b24", "#0f4c5c"], ["#2b2d42", "#d90429", "#edf2f4"],
    ["#3c1518", "#a44200", "#f2f3ae"], ["#0b3954", "#bfd7ea", "#ff5a5f"], ["#50514f", "#f25f5c", "#ffe066"], ["#1b4332", "#95d5b2", "#f8f9fa"],
    ["#6d597a", "#e56b6f", "#eaac8b"], ["#14213d", "#fca311", "#e5e5e5"], ["#582f0e", "#7f4f24", "#ede0d4"], ["#0d3b66", "#faf0ca", "#f95738"],
]

LANDMARKS = [
    "the Box mast, the Steward's sealed cloud engine, with its prayer flags", "a bell tower hung with forty bells", "the long kitchen with a glass roof",
    "a rim garden of dwarf apples that leans over the edge", "the oldest envelope in the Skein, patched in a hundred colours", "a rope-walk 200 m long on the roofs",
    "a windmill that turns only in the envelopes' shear (a kite turbine)", "the map wall, painted with every lashing since the boarding", "a hanging chapel slung under the rim",
    "an observatory roof where the Far Side is charted", "the ice houses, deep in the rock's cells", "the dove lofts, a tower of white birds",
    "a moss cradle you can ride down under the island", "a stair cut down through the rock to a window in the underside", "the lark cradles on the tallest roof",
    "a library of knotted cords", "a terraced hill of gardens", "the bridge house, where the bridges are kept and painted", "a frozen waterfall of cistern overflow on the rim",
    "a spiral of prayer kites flown from the roofs", "a weathervane taller than any building", "the old Warden service hatch, kept as a shrine",
    "a bathhouse warmed by the electrolysis halls", "the schoolhouse on stilts over the main path", "a carved figurehead on the east face",
]

CHARACTER_OPENERS = [
    "{name} is {size} island of {spec}, {gov_short}.", "On {name}, {size} {relief} island, {clan} are {spec}.",
    "{name} is {size} {relief} island; its people are {spec} and proud of it.", "Across the Skein, {clan} of {name} are the {spec} everyone knows.",
]

# the Hundred.  [name, kind, meaning]
NAMES = [
    # nautical
    ("Halyard", "nautical", "the line that hoists a sail"), ("Bowline", "nautical", "the knot that never slips"),
    ("Spindrift", "nautical", "spray blown off wave crests"), ("Gunwale", "nautical", "a boat's upper edge"),
    ("Mizzen", "nautical", "the mast aft of the main"), ("Topgallant", "nautical", "the high sail above the topsail"),
    ("Crow's Nest", "nautical", "the lookout at the masthead"), ("Fathom", "nautical", "six feet of sounding line; to understand"),
    ("Windlass", "nautical", "the winch that weighs the anchor"), ("Cat's Paw", "nautical", "a light breeze that ripples the water"),
    ("Capstan", "nautical", "the drum the crew walk round to haul"), ("Taffrail", "nautical", "the rail round a ship's stern"),
    ("Bosun's Chair", "nautical", "the sling a rigger is hoisted in"), ("Clove Hitch", "nautical", "the hitch that binds to a post"),
    ("Lee Rail", "nautical", "the downwind rail"), ("Sheet Bend", "nautical", "the knot that joins two ropes"),
    ("Weather Gauge", "nautical", "the windward position, the advantage"), ("Spritsail", "nautical", "a sail spread by a diagonal spar"),
    ("Dogwatch", "nautical", "the short evening watch"), ("Sounding Line", "nautical", "the weighted line that measures depth"),
    ("Fairlead", "nautical", "a ring that guides a line clear"), ("Main Brace", "nautical", "the brace of the main yard; 'splice the main brace'"),
    ("Kedge", "nautical", "a small anchor carried out to haul a ship along"), ("Ratline", "nautical", "the rungs of the shrouds"),
    ("Jollyboat", "nautical", "a ship's small boat"),
    # mystical
    ("Aureole", "mystical", "a halo of light"), ("Halcyon", "mystical", "the bird that calms the winds; calm days"),
    ("Evenstar", "mystical", "the evening star"), ("Hollow Bell", "mystical", "the bell that rings with no clapper"),
    ("Whisperwind", "mystical", "a wind that carries voices"), ("Sibyl's Rest", "mystical", "where the prophetess sleeps"),
    ("Moonward", "mystical", "toward the moon sleeve"), ("Vesper", "mystical", "evening; evening prayer"),
    ("Glimmerhold", "mystical", "a keep of faint light"), ("Ninth Wave", "mystical", "the greatest wave, the one that carries you"),
    ("Cloudhallow", "mystical", "a hallowed place in the cloud"), ("Starwell", "mystical", "a well that holds the stars"),
    ("Elsewhen", "mystical", "another time"), ("Farsight", "mystical", "the gift of seeing far"),
    ("Silver Bough", "mystical", "the branch that opens the otherworld"), ("Lumen", "mystical", "a unit of light"),
    ("Quiet Choir", "mystical", "the choir that sings without sound"), ("Augury", "mystical", "reading the birds"),
    ("Mistcrown", "mystical", "a crown of mist"), ("Gloaming", "mystical", "twilight"),
    ("Hallowmere", "mystical", "a holy lake"), ("Wyrd Lantern", "mystical", "the lantern of fate"),
    ("Seventh Veil", "mystical", "the last veil before the truth"), ("Saint Elmo", "mystical", "for Saint Elmo's fire on the rigging"),
    ("Candlemoor", "mystical", "a moor of candles"),
    # whimsical
    ("Puddingstone", "whimsical", "a lumpy conglomerate rock"), ("Thistledown", "whimsical", "the fluff that floats away"),
    ("Higgledy", "whimsical", "all in a muddle (its sister island is long lost)"), ("Teacup Rise", "whimsical", "a hill shaped like an upturned cup"),
    ("Mumblecrust", "whimsical", "an old nickname for a toothless beggar"), ("Pennywhistle", "whimsical", "the tin flute"),
    ("Dandelion Clock", "whimsical", "the seed head you blow to tell the time"), ("Hobnob", "whimsical", "to mix with company"),
    ("Bumbleby", "whimsical", "the place of the bumblebees"), ("Gooseberry Fool", "whimsical", "a pudding"),
    ("Hullabaloo", "whimsical", "an uproar"), ("Tumbledown", "whimsical", "falling to pieces (it isn't)"),
    ("Tiddlywink", "whimsical", "the counter flicked into a cup"), ("Fiddlesticks", "whimsical", "nonsense!"),
    ("Marmalade Moon", "whimsical", "an orange moon sleeve at harvest"), ("Cockleshell", "whimsical", "a tiny boat; the nursery rhyme"),
    ("Pipsqueak", "whimsical", "a small, noisy person"), ("Wobblewick", "whimsical", "a candle that won't stand straight"),
    ("Merriweather", "whimsical", "fair weather and good cheer"), ("Sixpence Spire", "whimsical", "a spire bought for sixpence"),
    ("Lollygag", "whimsical", "to dawdle"), ("Hopscotch", "whimsical", "the children's game"),
    ("Kerfuffle", "whimsical", "a fuss"), ("Crumpet Hill", "whimsical", "a round soft hill"),
    ("Ragamuffin", "whimsical", "a ragged child"),
    # ancient
    ("Ophir", "ancient", "the land of gold of the old scriptures"), ("Tarshish", "ancient", "the far port of the ships of Tarshish"),
    ("Thule", "ancient", "the northernmost land of the old geographers"), ("Dilmun", "ancient", "the Sumerian paradise of the dawn"),
    ("Punt", "ancient", "the Egyptians' land of incense"), ("Byblos", "ancient", "the city of the first books"),
    ("Ugarit", "ancient", "the city of the first alphabet"), ("Meroë", "ancient", "the island city of Kush"),
    ("Sardis", "ancient", "the city of the first coins"), ("Hattusa", "ancient", "the Hittite capital"),
    ("Elam", "ancient", "the highland kingdom east of Sumer"), ("Arcady", "ancient", "the shepherds' paradise"),
    ("Hyperborea", "ancient", "the land beyond the north wind"), ("Avalon", "ancient", "the isle of apples"),
    ("Ys", "ancient", "the drowned city"), ("Nineveh", "ancient", "the great city on the Tigris"),
    ("Ebla", "ancient", "the city of the clay library"), ("Lothal", "ancient", "the Harappan port"),
    ("Akrotiri", "ancient", "the painted town under the ash"), ("Uruk", "ancient", "the first city"),
    ("Kish", "ancient", "where kingship first came down from heaven"), ("Sheba", "ancient", "the queen's kingdom"),
    ("Colchis", "ancient", "the land of the golden fleece"), ("Tyre", "ancient", "the purple-dye city on its island"),
    ("Ithaca", "ancient", "the home the wanderer sails for"),
]

# --- water, livestock, wildlife (the user, 2026-10-14: "All islands will have ponds, the larger ones will have small lakes. There will be wildlife
# as well as livestock. We will create animals later") -- each animal a token the animal models will be built for
POND_M2 = (150, 600)             # a pond: m2 (1-2 m deep)
LAKE_FROM_BLOCKS = 6             # islands of 6+ blocks have a small lake too
LAKE_M2_PER_BLOCK = (300, 600)   # ... of this many m2 a block (1-3 m deep, 1.8 m mean)
WATER = ("the ponds and lakes are the island's reservoir and its ballast at once: filled by the cloud nets and snowmelt, drained by the weighers to trim "
         "(a 1,000 m2 pond a metre deep is 1,000 t of trim). Lined with skycloth over the foamed stone; reeds, frogs and stocked fish; they freeze "
         "over in a long white and are skated on. Every island has at least one pond; islands of six blocks or more have a small lake")
LIVESTOCK = {   # token: (name, where kept, why aloft, per-block typical, model notes)
    "goat": ("dwarf goat", "hill pastures, roof paddocks", "milk, cheese, meat, hair; light, sure-footed, eats anything", 6, "small (45 kg), shaggy, cold coat"),
    "sheep": ("sheep (small hill breed)", "hill pastures on rolling islands", "wool for the knitters", 4, "small, dense fleece; only on rolling islands as a flock"),
    "hen": ("hen", "roof coops", "eggs and meat", 30, "small chicken"),
    "duck": ("duck", "the ponds", "eggs, down, pest control in the gardens", 10, "on and round the ponds"),
    "goose": ("goose", "the ponds, the lake shore", "down (the down trade), watch-birds that shout at strangers", 4, "white or grey"),
    "rabbit": ("rabbit", "hutches", "meat, fur-felt, compost manure; no flight risk", 12, "in hutches; a few loose ones are a scandal"),
    "dove": ("dove (pigeon)", "the dove lofts", "messages, eggs, meat on some islands, down", 25, "flocks wheel round the lofts"),
    "bee": ("honeybee (cold-hardy)", "hives on the roofs", "pollination and honey", 8, "hives; insects as particles"),
    "pig": ("pig (small)", "sties on great islands only", "meat, eats scraps; heavy, so only where the lift allows", 0.6, "only islands of 6+ blocks"),
    "fish": ("pond fish: perch and pumpkinseed sunfish, crayfish", "the ponds and lakes", "food; the ponds' insect control", 0, "fish under the water surface"),
}
WILDLIFE = {   # token: (name, where, what it does)
    "swallow": ("barn swallow", "mud nests under the rim and on the rock's underside", "hunts insects round the island; the islanders' luck-bird"),
    "swift": ("swift", "crevices in the underside rock", "screaming flocks at dusk; never lands"),
    "starling": ("starling", "roofs and gutters", "murmurations round the envelopes"),
    "sparrow": ("house sparrow", "everywhere people are", "came up in the first boardings' baggage"),
    "gull": ("gull", "follows islands over the seas, nests on the rim of a few", "a thief at the long kitchen"),
    "tern": ("tern", "rides with islands over the North and South Seas", "dives into the ponds for fish"),
    "wren": ("wren", "the moss and vines under the rim", "lives its whole life in the hanging gardens"),
    "heron": ("heron", "the lakes of great islands, visiting", "flies up from the floor's marshes to fish the lakes; an omen"),
    "frog": ("frog", "the ponds", "came up as spawn in hoisted water; sings at night"),
    "dragonfly": ("dragonfly", "the ponds", "summer"),
    "ballooning_spider": ("ballooning spider", "everywhere; arrives on silk threads in the wind", "real: spiders sail on silk; their threads glitter on the fences after a white"),
    "moth": ("moth", "the underside moss", "drawn to the rim lanterns"),
    "snail": ("snail", "the moss and the gardens", "a pest; the ducks eat them"),
    "mouse": ("house mouse", "stowaway in hoisted cargo", "vermin; cats keep them down"),
    "cat": ("cat", "every island (half wild)", "the mousers; sleep on the warm electrolysis halls"),
    "lichen_moth": ("lichen moth", "the rock underside", "grey moths that live only aloft (a Columbia variety)"),
}


BLOCK_COUNTS = {1: 18, 2: 19, 3: 16, 4: 13, 5: 10, 6: 8, 7: 6, 8: 4, 9: 3, 10: 3}

# the confederation
SKEIN = {
    "name": "the Skein",
    "formal": "the Skein of the Hundred",
    "why_the_name": "a skein is a flight of wild geese in the air and a loose hank of yarn; the Hundred are both -- free-flying, and tied together only loosely, by lines that are always being cut and tied again",
    "people": "the Aloft (their own word; they call themselves 'skeinfolk' to outsiders); the floor calls them highfolk, balloon people or, rudely, 'cloudies'",
    "they_call_the_floor": "the floor, the Ground; floor people are 'groundfolk' or 'heavies'",
    "islands": 100, "seat": "none: the Skein has no capital, no standing council and no flag; its law travels with the knot keepers",
    "law": "knot-law: custom kept by each island's knot keepers in knotted cords and in books, argued at lashings; the Five Knots are the only laws every island keeps",
    "five_knots": [
        "the Weight Knot: no island may take on more than its lift; the weigher's word on weight is final",
        "the Flame Knot: no open flame aloft (hydrogen); fire is the only crime punished by putting a person down to the floor for good",
        "the Line Knot: a line shot across must be made fast; no island refuses a lashing from one in distress",
        "the Ten Knot: no raft of more than ten islands (since the Great Tangle, VY 388)",
        "the Three-Day Knot: a raft casts off at the end of the third day; no island may rule another",
    ],
    "lashing": "when two islands come within 3 km, bell-speech and doves go first; if both agree (they almost always do), line rocketeers fire cold rockets "
               "trailing messenger lines across, heavier lines and hawsers follow, and the winch hands haul the islands together over an hour or two "
               "until their dock faces are 26 m apart; then the bridges come down on the facing sides and the islands become a raft. More islands may join a "
               "raft till it holds ten",
    "the_moot": "the three days lashed are the Lashing: a market, a moot, a fair and a wedding season at once. The knot keepers hear disputes; factors trade; "
                "young people cross to court, marry and move; the dead are mourned together; news of the floor is traded by the plumbs",
    "casting_off": "at dusk on the third day the Casting Off: bridges up, every lashing line cut with a knife by the eldest of each island, and the islands drift "
                   "apart on the wind. 'Three days lashed and then the knives.'",
    "why_three_days": "long enough to trade, settle disputes and marry; short enough that no island grows used to ruling another, that the raft's slower drift "
                      "doesn't carry it into weather, and that the weight that crosses doesn't unbalance anyone",
    "why_ten": "the Great Tangle (VY 388): seventeen islands lashed for a jubilee were caught by a squall line; the raft twisted, lines parted, Higgledy's sister "
               "island Piggledy was torn loose, holed on Tumbledown's rim and fell into the North Sea (212 lost). Ten is what the lines and the winches hold in a squall",
    "between_islands": "kin: marriage across bridges means everyone has cousins on a dozen islands; clan feuds and alliances follow the kin",
}

HISTORY = [
    {"vy": 214, "id": "the_hundred_launched", "what": "the Hundred: after the Last Snow (VY 212) the Steward launches a hundred cloud engines -- platforms of foamed stone under great "
     "cylindrical envelopes, each with a sealed Box -- to make the floor's rain as snow aloft. To the floor they are 'the weather hulks' for sixty years", "known": "legend"},
    {"vy": 271, "id": "regression_aloft", "what": "the Third Lockdown and the Regression; in the Gray Years people look up at the hulks, which the Steward still lowers to "
     "the Mooring Fields every few years for its tenders", "known": "schooled"},
    {"vy": 273, "id": "the_first_boarding", "what": "the First Boarding: forty-one families of dissolved Warden lines, who knew the hulks' service routine, climb the tethers "
     "of a hulk moored near Bellhaven and refuse to come down. The Steward, bound not to cause death, raises the hulk to its height with them aboard and stops "
     "servicing it -- it leaves its Box running and lets the people keep the rest. The hulk is named Halyard", "known": "ritual", "island": "SKY-001"},
    {"vy": 275, "id": "the_boardings", "what": "the Boardings: Gray Years families, Returner remnants after the Reconciliation (VY 280), debtors, dreamers and Waymakers "
     "take hulk after hulk at the Mooring Fields; each boarding group becomes a clan", "known": "ritual"},
    {"vy": 301, "id": "mooring_fields_closed", "what": "the Mooring Fields close: the Steward stops lowering the hulks; from now on the only way up is a line", "known": "schooled"},
    {"vy": 318, "id": "first_lashing", "what": "the First Lashing: Halyard and Bowline lash with ropes fired from spring guns; the three-day custom begins (the first lashing broke "
     "on the fourth day in a quarrel over water)", "known": "ritual"},
    {"vy": 350, "id": "lockout_aloft", "what": "the Lockout: the Floor is set; the Aloft lose little (they had little) and gain trade: the floor now needs what they make", "known": "schooled"},
    {"vy": 362, "id": "the_hundredth_boarding", "what": "the Hundredth Boarding: the last hulk (Ragamuffin) is taken, by children of other islands sent to found it", "known": "ritual"},
    {"vy": 371, "id": "skein_named", "what": "the Skein named at a raft of nine; the Five Knots set down by the knot keepers", "known": "ritual"},
    {"vy": 388, "id": "the_great_tangle", "what": "the Great Tangle: seventeen islands lashed for a jubilee meet a squall line; Piggledy falls into the North Sea with 212 aboard. "
     "The Ten Knot", "known": "living"},
    {"vy": 405, "id": "gift_of_the_air_aloft", "what": "the Gift of the Air: the Chutes release the floor's first aerostats; the Aloft trade for them within a year and "
     "strip them for parts", "known": "living"},
    {"vy": 417, "id": "the_first_lark", "what": "the first lark: Topgallant's wrights build a two-person aerostat from Gift parts, skycloth and a winch motor that climbs "
     "from the floor to an island in four minutes; the plumbs stop riding containers down the hoist lines", "known": "living", "island": "SKY-006"},
    {"vy": 446, "id": "air_post", "what": "the air post: Fathom and Dogwatch start carrying urgent letters for the floor by lark", "known": "living"},
    {"vy": 471, "id": "guild_quarrel", "what": "the Lark Quarrel: the Aerostat Pilots' Guild tries to bar larks from the Kettle Cup; the Aloft win three of the next five", "known": "living"},
    {"vy": 500, "id": "notice_aloft", "what": "the Launch Day Notice (VOYAGE ONE THIRD COMPLETE) reaches the Skein by dove in two days; the knot keepers call a raft to talk of it", "known": "living"},
]

PHYSIOLOGY = [
    "born and raised at about 0.89 g (0.925 g at the deck, less drifting west): taller by ~3 cm on average, lighter-boned and longer-limbed than the floor's (low-gravity "
    "bone and muscle unloading, over 8-9 generations of slight selection and every childhood at 89% weight -- modest, but visible in a crowd)",
    "ground-weight: on the floor they feel 12% heavier; a day's walking leaves them sore, and the young get ground-sickness (dizziness, heavy limbs, homesickness) in the first days",
    "cold-adapted habits rather than bodies: layered clothes, hot food, short exposure; frostnip on ears and fingers is common and treated without fuss",
    "a head for heights: vertigo is taught out of children on the rim rails; floor people's fear of the edge amuses them",
    "thin skin for flame: they have almost never seen open fire; candles on the floor fascinate and frighten them",
]

GIVEN_SKY = {"F": ["Wren", "Lark", "Skye", "Rime", "Halcyon", "Brume", "Nimbus", "Aura", "Zephyr", "Cirrus", "Mistral", "Haley", "Willa", "Selah", "Isolde",
                   "Fennel", "Juniper", "Linnet", "Tamsin", "Marisol", "Ondine", "Perpetua", "Vesna", "Yara", "Ayo", "Mirela"],
             "M": ["Corwin", "Gale", "Haldor", "Ferris", "Tamber", "Hollis", "Brandt", "Teodor", "Anselm", "Kestrel", "Rook", "Tarn", "Oriel", "Emeric",
                   "Lazlo", "Ignatius", "Bram", "Cyprian", "Darius", "Matteo", "Kwame", "Joaquín", "Piotr", "Hiro", "Ravi", "Solomon"]}


BAD_CLAN = {"marvel", "bills", "sandusky", "christmas", "money", "king", "black", "white", "young", "love", "wise", "rich", "ford", "dick", "gay", "pope", "lord", "god", "pass", "head", "card", "beaver"}


def _surnames(names):
    # one founding surname per clan, spread over heritages; never a major bible lineage, never a common given name or a word
    given = set()
    for pool in names["given_pools"].values():
        for sx in pool.values():
            for row in sx[:400]:
                given.add(row[0].lower())
    rows = [r for r in names["surnames"][60:2600] if r[2] in HERITAGES and len(r[0]) >= 4 and r[0].lower() not in given and r[0].lower() not in BAD_CLAN]
    by = {}
    for r in rows:
        by.setdefault(r[2], []).append(r[0])
    return by


def build(names, faction_ids, settlement_ids, lineage_surnames):
    by_her = _surnames(names)
    taken = set(s.lower() for s in lineage_surnames)
    # blocks: exact counts, dealt by a hash order
    order = sorted(range(100), key=lambda i: h01("blocks", i))
    sizes = []
    for b, n in BLOCK_COUNTS.items():
        sizes += [b] * n
    blocks = [0] * 100
    for k, i in enumerate(order):
        blocks[i] = sizes[k]
    # bridge styles: ten of each, dealt by a hash order
    bord = sorted(range(100), key=lambda i: h01("bridge", i))
    bstyle = [None] * 100
    for k, i in enumerate(bord):
        bstyle[i] = BRIDGE_STYLES[k % len(BRIDGE_STYLES)]
    islands, clans, all_jobs_total = [], [], {}
    used_surnames = set()
    for i, (name, kind, meaning) in enumerate(NAMES):
        iid = "SKY-%03d" % (i + 1)
        b = blocks[i]
        if name == "Halyard":
            b = max(b, 6)
        relief = "rolling" if h01("relief", i) < (0.15 + 0.06 * b) else "flat"
        spec = SPECIALTIES[int(h01("spec", i) * len(SPECIALTIES))]
        if name == "Halyard":
            spec = next(s for s in SPECIALTIES if s[0] == "trade")
        if name == "Topgallant":
            spec = next(s for s in SPECIALTIES if s[0] == "larks")
        if name in ("Fathom", "Dogwatch"):
            spec = next(s for s in SPECIALTIES if s[0] == "courier")
        dens = 180 + int(h01("dens", i) * 140)
        if spec[0] in ("trade", "lore", "skycloth"):
            dens += 20
        dens = min(dens, 320)
        pop = int(round(b * dens / 10.0) * 10)
        # ages: more children aloft ('ballast'), fewer very old
        working = int(round(pop * (0.56 + 0.06 * h01("work", i))))
        weights = {j: v[2] * spec[2].get(j, 1.0) * (0.75 + 0.5 * h01("jw", i, j)) for j, v in JOBS.items()}
        weights["plumb"] = 0.0
        weights["lark_wright"] *= 1.0
        tot = sum(weights.values())
        jobs = {j: int(working * w / tot) for j, w in weights.items()}
        nl = larks(b) + (1 if spec[0] in ("courier", "larks") else 0)
        jobs["plumb"] = 2 + (1 if spec[0] == "courier" else 0) + (1 if b >= 7 else 0)   # the plumb and seconds
        jobs["lark_wright"] = max(jobs["lark_wright"], 1 + nl // 2)
        jobs["line_rocketeer"] = max(jobs["line_rocketeer"], 2)
        jobs["knot_keeper"] = max(jobs["knot_keeper"], 1)
        jobs["box_tender"] = max(jobs["box_tender"], 1)
        jobs["weigher"] = max(jobs["weigher"], 1)
        jobs["healer"] = max(jobs["healer"], 1)
        jobs["bridgewright"] = max(jobs["bridgewright"], 1)
        jobs["hoist_master"] = max(jobs["hoist_master"], 1)
        jobs["pond_keeper"] = max(jobs["pond_keeper"], 1)
        jobs["herder"] = max(jobs["herder"], 1)
        diff = working - sum(jobs.values())
        jobs["roof_grower"] += diff                 # the rest grow food
        jobs = {k: v for k, v in sorted(jobs.items(), key=lambda kv: -kv[1]) if v > 0}
        for k, v in jobs.items():
            all_jobs_total[k] = all_jobs_total.get(k, 0) + v
        # water, livestock, wildlife
        ponds = 1 + b // 2 + (1 if h01("pond", i) < 0.4 else 0)
        pond_m2 = [int(POND_M2[0] + h01("pondm", i, k) * (POND_M2[1] - POND_M2[0])) for k in range(ponds)]
        lake_m2 = int(b * (LAKE_M2_PER_BLOCK[0] + h01("lake", i) * (LAKE_M2_PER_BLOCK[1] - LAKE_M2_PER_BLOCK[0]))) if b >= LAKE_FROM_BLOCKS else 0
        stock = {}
        for a, v in LIVESTOCK.items():
            if a == "pig" and b < 6 or a == "sheep" and relief != "rolling" and spec[0] != "wool":
                continue
            k = v[3] * b * (0.6 + 0.8 * h01("stock", i, a))
            if a in ("sheep", "goat") and spec[0] == "wool":
                k *= 3
            if a == "dove" and spec[0] in ("courier", "down", "weather"):
                k *= 2.5
            if a == "bee" and spec[0] in ("honey", "gardens"):
                k *= 3
            if a in ("duck", "goose") and spec[0] == "down":
                k *= 2.5
            if a == "fish":
                stock[a] = "stocked"
            elif round(k) > 0:
                stock[a] = int(round(k))
        wild = ["swallow", "sparrow", "frog", "ballooning_spider", "snail", "mouse", "cat", "wren", "moth"]
        for a, pr in (("swift", 0.6), ("starling", 0.5), ("gull", 0.3), ("tern", 0.25), ("dragonfly", 0.7), ("lichen_moth", 0.5), ("heron", 0.6 if lake_m2 else 0.0)):
            if h01("wild", i, a) < pr:
                wild.append(a)
        heritage = wpick(HERITAGES, "her", i)
        pool = by_her.get(heritage) or by_her["anglo"]
        sn = None
        for t in range(50):
            c = pick(pool, "sn", i, t)
            if c.lower() not in taken and c not in used_surnames:
                sn = c
                break
        if heritage == "station_coined" or sn is None:
            sn = name.replace("'", "").split()[0] + "kin"
        used_surnames.add(sn)
        clan_id = "clan_" + sn.lower().replace(" ", "_").replace("'", "").replace("-", "_")
        clan = "the %s kin" % sn
        gov = GOVERNANCE[int(h01("gov", i) * len(GOVERNANCE))]
        c1 = int(h01("cust", i, 0) * len(CUSTOMS))
        c2 = (c1 + 1 + int(h01("cust", i, 1) * (len(CUSTOMS) - 1))) % len(CUSTOMS)
        customs = [CUSTOMS[c1][0], CUSTOMS[c2][0]]
        if {"matrilocal", "patrilocal"} <= set(customs):
            customs = [CUSTOMS[c1][0], "long_kitchen"]
        faith = wpick({f[0]: f[2] for f in SKY_FAITHS}, "faith", i)
        pal = PALETTES[int(h01("pal", i) * len(PALETTES))]
        landmark = LANDMARKS[int(h01("lm", i) * len(LANDMARKS))]
        founded = 273 if name == "Halyard" else 362 if name == "Ragamuffin" else int(275 + h01("found", i) ** 1.6 * 86)
        size = "a one-block" if b == 1 else "a small" if b <= 2 else "a middling" if b <= 5 else "a great"
        nl_rel = "rolling" if relief == "rolling" else "flat-topped"
        open_ = CHARACTER_OPENERS[int(h01("open", i) * len(CHARACTER_OPENERS))].format(
            name=name, size=size, spec=spec[1], relief=nl_rel, clan=clan, gov_short="governed by " + gov[1].split(":")[0].split(" (")[0])
        cust_txt = dict(CUSTOMS)
        mood = pick(["warm to strangers and loud at lashings", "reserved, proud and exacting about weight", "quarrelsome among themselves and loyal to outsiders",
                     "devout and quiet", "famous for their music", "shrewd traders who never give the first price", "the Skein's best riggers, and they know it",
                     "gentle, slow-spoken and stubborn", "restless: their youth cross bridges more than any", "old-fashioned: they keep floor ways the floor forgot",
                     "superstitious about the Box", "curious about the floor, and send their plumb down more than most"], "mood", i)
        character = "%s They are %s. %s; and %s. Founded VY %d by %s. Faith: %s. Landmark: %s." % (
            open_, mood, cust_txt[customs[0]][0].upper() + cust_txt[customs[0]][1:], cust_txt[customs[1]], founded,
            pick(["Gray Years families from the Northland", "Warden lines from Bellhaven", "Returner families after the Reconciliation", "debtors from Port Carrow",
                  "Waymakers from Oceanview", "cannery families from Tern Harbor", "Solano families from Playa Verde", "children of other islands sent to found it",
                  "Kessler clerks who walked out of the Registry", "Marlowe orchard families", "Harrow Falls millworkers", "Côte families from Port Carrow"],
                 "founders", i) if name not in ("Halyard", "Ragamuffin") else ("forty-one Warden families from Bellhaven (the First Boarding)" if name == "Halyard"
                                                                             else "children of other islands sent to found it (the Hundredth Boarding)"),
            dict((f[0], f[1]) for f in SKY_FAITHS)[faith].split(":")[0].split(" (")[0], landmark)
        islands.append({
            "id": iid, "name": name, "name_kind": kind, "name_meaning": meaning, "clan": clan, "clan_id": clan_id, "blocks": b, "relief": relief,
            "deck_m2": int(b * BLOCK_M2), "balloons": balloons(b), "population": pop, "working": working, "jobs": jobs,
            "water": {"ponds_m2": pond_m2, "lake_m2": lake_m2}, "livestock": stock, "wildlife": wild,
            "specialty": spec[0], "trade": spec[3], "needs": spec[4] + ["metal", "grain", "medicine"],
            "bridge_style": bstyle[i], "aerostats": nl, "founded_vy": founded, "governance": gov[0], "customs": customs, "faith": faith,
            "heritage": heritage, "colors": pal, "landmark": landmark, "character": character, "seed": int(h01("seed", i) * 2 ** 31),
            "style": _STYLES.get(iid),          # its architecture (tools/sky/styles.py; research/sky_islands/architecture)
        })
        clans.append({"id": clan_id, "name": clan, "surname": sn, "island": iid, "heritage": heritage, "colors": pal, "governance": gov[0],
                      "customs": customs, "faith": faith})
    # kin ties: each clan has 2-4 cousin clans and maybe a feud
    for i, c in enumerate(clans):
        k = 2 + int(h01("kin", i) * 3)
        c["cousins"] = sorted({clans[int(h01("cous", i, t) * 100)]["id"] for t in range(k)} - {c["id"]})
        c["feud"] = clans[int(h01("feud", i) * 100)]["id"] if h01("hasfeud", i) < 0.18 else None
        if c["feud"] == c["id"] or c["feud"] in c["cousins"]:
            c["feud"] = None
    # validation
    errs = []
    if len({x["name"] for x in islands}) != 100:
        errs.append("sky: duplicate island names")
    lower_sett = {s.replace("_", " ") for s in settlement_ids}
    for x in islands:
        if x["name"].lower() in lower_sett:
            errs.append("sky: %s reuses a settlement name" % x["name"])
        if x["bridge_style"] not in BRIDGE_STYLES:
            errs.append("sky: bridge style %s" % x["bridge_style"])
        if x["aerostats"] < 2:
            errs.append("sky: %s has %d larks" % (x["id"], x["aerostats"]))
        if sum(x["jobs"].values()) != x["working"]:
            errs.append("sky: %s jobs %d != working %d" % (x["id"], sum(x["jobs"].values()), x["working"]))
        for j in x["jobs"]:
            if j not in JOBS:
                errs.append("sky: job %s" % j)
    for f in FACTION_STANCE:
        if f not in faction_ids:
            errs.append("sky: faction %s" % f)
    data = {
        "version": 1,
        "contract": {"deck_h_m": DECK_H, "block_m2": BLOCK_M2, "envelope": ENVELOPE, "balloons": "ceil(1.6 x blocks) + 1", "aerostats": "2 + blocks // 3 (or more)",
                     "dock_range_m": DOCK_RANGE_M, "dock_gap_m": DOCK_GAP_M, "raft_max": RAFT_MAX, "raft_days": RAFT_DAYS, "bridge_styles": BRIDGE_STYLES},
        "confederation": SKEIN, "physics": physics(), "history": HISTORY, "physiology": PHYSIOLOGY,
        "water": WATER, "livestock": {k: dict(zip(("name", "where", "why", "per_block", "model"), v)) for k, v in LIVESTOCK.items()},
        "wildlife": {k: dict(zip(("name", "where", "what"), v)) for k, v in WILDLIFE.items()},
        "lark": LARK, "plumb": PLUMB, "hoist_trade": HOIST,
        "jobs": {k: {"name": v[0], "what": v[1], "why": v[3]} for k, v in JOBS.items()},
        "specialties": {s[0]: {"name": s[1], "trade": s[3], "needs": s[4]} for s in SPECIALTIES},
        "governance": dict(GOVERNANCE), "customs": dict(CUSTOMS), "faiths": {f[0]: f[1] for f in SKY_FAITHS},
        "faction_stance": FACTION_STANCE, "lexicon": [dict(zip(("term", "meaning", "example"), l)) for l in LEXICON],
        "sayings": SAYINGS, "foods": [dict(zip(("id", "name", "what"), f)) for f in FOODS], "clothing": CLOTHING,
        "names": {"convention": NAMING, "given_sky": GIVEN_SKY},
        "clans": clans, "islands": islands,
        "totals": {"islands": 100, "blocks": sum(x["blocks"] for x in islands), "population": sum(x["population"] for x in islands),
                   "working": sum(x["working"] for x in islands), "balloons": sum(x["balloons"] for x in islands),
                   "larks": sum(x["aerostats"] for x in islands), "jobs": dict(sorted(all_jobs_total.items(), key=lambda kv: -kv[1]))},
    }
    return data, errs


LARK = {
    "name": "the lark", "fleet_type": "sky_skiff", "crew": 2, "seats": "tandem: the plumb forward, the second (navigator, trade clerk) behind",
    "ceiling_m": 1500, "top_speed_kmh": 250, "climb_ms": 8,
    "how": "a slim 14 m hydrogen envelope (a cigar, not a ball) over a light keel; four ducted fans on tilting pylons; a winch motor for the mooring line; "
           "low weight and a hard trim let it out-climb and out-run any floor aerostat (the floor's top out near 90 km/h)",
    "mooring": "larks sit in cradles on the island's tallest roofs; a lark docks by flying up a dropped line",
    "per_island": "at least two: one for the plumb, one spare and for rescue; great islands keep more",
    "first": "VY 417, Topgallant",
}
PLUMB = {
    "name": "the plumb", "plural": "plumbs", "why": "a plumb line drops straight down",
    "who": "one chosen from the clan, usually for seven years: a trader, a diplomat and a pilot; with a second who flies behind and learns",
    "does": "goes down by lark to trade at the floor's markets and the Chutes, books the hoist schedule, carries letters and news, buys what the factors ask for, "
            "and brings back stories; most of the Aloft meet groundfolk only through their plumb",
    "how_seen_aloft": "honoured and a little pitied: the plumb carries the ground-weight for everyone",
    "how_seen_below": "glamorous, aloof, cold-handed; floor children chase their larks",
}
HOIST = {
    "what": "scheduled trade by hoist: the island trims to pass over an agreed spot (the floor's 'hoist grounds' at Drops, Chutes and market towns) at an agreed hour; "
            "the hoist masters drop long lines -- 750 m and more -- and the floor's dock hands hook on cargo containers; the winches draw them up. Down go the "
            "island's goods in the same containers",
    "container": "the skybox: a light aluminium-framed container, about 2.4 x 2.4 x 3 m, at most 2 t loaded (the hoist lines' limit)",
    "schedule": "booked by the plumb a week or more ahead; the weather reader picks the drift; an island makes a hoist every few days",
    "weight": "every hoist is weighed both ways: what comes up must be balanced by what goes down, or by gas",
}
FACTION_STANCE = {
    "aerostat_guild": [-0.3, "rivals: the Lark Quarrel; but the Guild's pilots respect the larks"],
    "marshals": [-0.2, "the Marshals have no reach aloft and resent it; fire-setters put down are handed to them"],
    "charter_league": [-0.25, "the League says the Charter covers the Aloft; the Aloft never signed it"],
    "open_hand": [0.3, "the Open Hand trades with them fairly and argues they should be counted"],
    "waymakers_assembly": [0.35, "the Waymakers see the Aloft as nearer the pilgrimage's deck"],
    "wardens_circle": [0.25, "the Aloft are partly Warden lines; they keep Warden books in their knot libraries"],
    "homeward": [0.05, "some clans descend from Returners; most want nothing to do with the Homeward"],
    "grange": [0.2, "the Grange buys forecasts and sells grain by hoist"],
    "cannery_union": [0.1, "dock hands work the hoist grounds"],
}
LEXICON = [
    ("the floor / the Ground", "the land below", "'She went to the Ground for a week and came back walking like a heavy.'"),
    ("groundfolk, heavies", "floor people", "'Mind the heavy, he's never seen the edge.'"),
    ("a lashing", "the three days two or more islands are lashed together; the market and moot", "'We'll marry at the next lashing.'"),
    ("a raft", "islands lashed together (ten at most)", "'A raft of eight, and the Ophir bells in it.'"),
    ("the knives", "the Casting Off at the end of a lashing", "'Three days lashed and then the knives.'"),
    ("plumb", "the clan's descender", "'Who's plumb on Halyard now?'"),
    ("lark", "the two-person high aerostat", "'The lark's down at Calder for the hoist.'"),
    ("skybox", "a hoist container", "'Two skyboxes of grain, one of nails.'"),
    ("lift", "the island's spare buoyancy; also wealth, room, permission", "'We haven't the lift for a goat.'"),
    ("to weigh", "to judge whether something is worth its weight", "'I weighed him and found him light.'"),
    ("ground-weight", "the heaviness on the floor; ground-sickness", "'Three days of ground-weight and I'm done.'"),
    ("the Lightening", "running west faster than the deck air; the extra lift it gives", "'Trim for the Lightening, we've a hoist at noon.'"),
    ("the neighbour", "the Steward (in sight of the Box)", "'The neighbour's humming tonight.'"),
    ("the Box", "the Steward's sealed cloud engine on each island's mast", ""),
    ("a white", "a cloud you're inside", "'We were in a white all morning; the roofs are deep.'"),
    ("the rim", "the island's edge and its fence", "'Off the rim with you!' (go away)"),
    ("a heavy word", "a promise", "'That's a heavy word, keep it.'"),
    ("cold hands", "an honest trader (the plumbs' handshake is always cold)", ""),
    ("downwind", "in the future; later", "'We'll see downwind.'"),
    ("upwind", "the past", "'That's upwind now.'"),
]
SAYINGS = [
    ("Three days lashed and then the knives.", "everything ends; enjoy it"),
    ("Every kilo is a person's breath.", "don't waste lift"),
    ("No flame, no fall.", "the two great dangers"),
    ("The wind keeps no promises; the knot does.", "keep your word"),
    ("Light hands, long lines.", "patience in trade"),
    ("The Ground is for the dead and the plumbs.", "on going down"),
]
FOODS = [
    ("cloud_porridge", "cloud porridge", "oats boiled in snowmelt with honey and moss-berry jam; breakfast in the long kitchen"),
    ("dove_pie", "dove pie", "on islands that eat their doves; a lashing dish"),
    ("roof_greens", "roof greens", "kale, chard, cress and mustard from the roofs, wilted with vinegar"),
    ("air_cured_goat", "air-cured goat", "dried in the cold wind on the rim racks; the only meat most islands raise"),
    ("snow_honey", "snow honey", "fresh snow eaten with honey -- the snow feast"),
    ("hoist_bread", "hoist bread", "loaves baked from floor grain the day a hoist comes up"),
    ("berry_wine", "berry wine", "currant and gooseberry wine"),
    ("moss_tea", "moss tea", "bitter, warming, said to keep off ground-sickness"),
    ("lashing_stew", "lashing stew", "every island at a raft adds something to one pot in the middle bridge's square"),
]
CLOTHING = {
    "principle": "warm, layered, light (every gram counts), knitted in the clan's colours so a stranger's island can be read at a glance; wind-proof shells over wool and down. "
                 "Divergent by clan: knit patterns, coat cut and trims differ island to island (Sámi gákti and Inuit parkas are the closest real cousins: "
                 "colour and trim as identity, layers for cold)",
    "for_the_outfit_generator": {
        "climate_tag": "cold",
        "layers": ["base: wool or down-cotton long underwear (unseen)", "mid: a knitted gansey or patterned jumper in the clan colours", "outer: a coat or anorak (below)"],
        "outer": [
            ["rigger_anorak", "hip-length pullover anorak, hood, drawstring hem; waxed skycloth", "colours: clan main or grey; reflective? no -- hi-vis is clan accent bands on the arms"],
            ["long_coat", "knee-length quilted down coat, toggles, high collar", "clan main; trim in second"],
            ["gakti_tunic", "a tunic-coat with a broad contrasting band at hem, cuffs and collar (gákti-like), worn belted over the gansey", "clan main with accent bands"],
            ["parka", "deep-hooded parka with a fur-like fleece ruff (the ruff is down-felt, no fur aloft)", "elders and plumbs; clan main"],
            ["cape_coat", "a short caped coat (a shoulder cape over a jacket), for factors and knot keepers", "second colour"],
            ["vest_quilted", "quilted down vest over the gansey, for indoor and roof work", "accent"],
        ],
        "headwear": [["knit_cap", "knitted cap with ear flaps and a tassel; clan pattern band"], ["balaclava", "rolled down in a white"],
                     ["hood", "from the anorak"], ["fur_hat", "a tall felted hat (ushanka shape) for elders"], ["headband", "a wide knitted headband for the young"]],
        "hands": [["mittens", "knitted mittens, patterned palms (grip); clan colours"], ["fingerless", "fingerless gloves for riggers and knitters"]],
        "neck": [["scarf_long", "a very long striped scarf (stripe order = clan)"], ["cowl", "a knitted cowl"]],
        "legs": [["wool_trousers", "heavy wool or felt trousers"], ["leggings_knit", "patterned knit leggings under a skirt or tunic"],
                 ["skirt_quilted", "a quilted wrap skirt over leggings"]],
        "feet": [["felt_boots", "felted wool boots with soft soles (quiet, light, grip on wet roofs)"], ["rigger_boots", "light laced boots with sticky soles"]],
        "harness": [["rim_harness", "a webbing harness with a short tether and clip, worn by riggers, fence wardens and children near the rim"]],
        "patterns": ["stripes (the clan order)", "Fair Isle-like peerie bands", "snowflake/star yokes", "rope (cable) knit", "chevrons (the island's bridge style drawn as a zigzag)",
                     "checks", "bird (dove) borders"],
        "palette_rule": "each island's clan colours (islands[].colors: [main, second, accent]); undyed wool greys and creams (#e8e2d0, #b8b0a0, #6f6a60) go with any; "
                        "moss-dyed greens and lichen yellows are common; floor-bought bright synthetics are a plumb's show of wealth",
        "age_and_role": {"children": "brightest, harnessed, many layers", "riggers": "anorak + harness + fingerless gloves + knit cap",
                         "elders": "parka or long coat, feathers on the collar (one per lashing remembered in some clans)",
                         "plumbs": "a tailored parka in clan main with a floor-made jacket under it", "knot_keepers": "cape coat with a cord of knots worn as a sash"},
    },
}
NAMING = ("a given name, the clan (a founding surname, kept by all born to the clan) and the island: 'Wren Okafor of Halyard'. Sky given names mix the floor's pools "
          "with weather and bird words (given_sky). Everyone has a sky name and, in some clans, a floor name for dealing with groundfolk. A person who crosses at a "
          "lashing to marry takes the new island ('of Bowline') but keeps the clan unless the clan's custom says otherwise.")


def doc_lines(d):
    """research/bible/13_sky_islands.md"""
    from collections import Counter
    t = d["totals"]
    L = ["# 13. The sky islands: the Hundred, the Skein and the Aloft", "",
         "_Generated by tools/bible/make_bible.py from tools/bible/canon_sky.py. Engine file: godot_project/remake/bible/sky_islands.json. "
         "Research and sources: research/sky_islands/._", "",
         "**%d islands, %d blocks, %d people (%d working), %d envelopes, %d larks.**" % (t["islands"], t["blocks"], t["population"], t["working"], t["balloons"], t["larks"]), "",
         "## The Skein", ""]
    for k, v in d["confederation"].items():
        if isinstance(v, list):
            L.append("- **%s:**" % k.replace("_", " "))
            L += ["  - " + x for x in v]
        else:
            L.append("- **%s:** %s" % (k.replace("_", " "), v))
    L += ["", "## History", ""] + ["- **VY %d** -- %s" % (h["vy"], h["what"]) for h in d["history"]]
    L += ["", "## Physics", ""] + ["- **%s:** %s" % (k.replace("_", " "), v) for k, v in d["physics"].items()]
    L += ["", "## The people", ""] + ["- " + p for p in d["physiology"]]
    L += ["", "## The plumb and the lark", ""] + ["- **%s:** %s" % (k, v) for k, v in d["plumb"].items()] + ["- **lark %s:** %s" % (k, v) for k, v in d["lark"].items()]
    L += ["", "## Hoist trade", ""] + ["- **%s:** %s" % (k, v) for k, v in d["hoist_trade"].items()]
    L += ["", "## Jobs (all islands)", "", "| job | workers | what | why aloft |", "|---|---|---|---|"]
    for k, n in t["jobs"].items():
        j = d["jobs"][k]
        L.append("| %s | %d | %s | %s |" % (j["name"], n, j["what"], j["why"]))
    L += ["", "## Governance, customs, faiths", ""] + ["- **%s:** %s" % kv for kv in d["governance"].items()] + [""] + ["- **%s:** %s" % kv for kv in d["customs"].items()] + [""] \
        + ["- **%s:** %s" % kv for kv in d["faiths"].items()]
    L += ["", "## Lexicon and sayings", ""] + ["- **%s** -- %s %s" % (l["term"], l["meaning"], l["example"]) for l in d["lexicon"]] + [""] + ["- _%s_ (%s)" % s for s in d["sayings"]]
    L += ["", "## Water, livestock, wildlife", "", d["water"], "", "| livestock | name | kept | why | per block | model |", "|---|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %s | %s | %s |" % (k, v["name"], v["where"], v["why"], v["per_block"], v["model"]) for k, v in d["livestock"].items()]
    L += ["", "| wildlife | name | where | what |", "|---|---|---|---|"] + ["| %s | %s | %s | %s |" % (k, v["name"], v["where"], v["what"]) for k, v in d["wildlife"].items()]
    L += ["", "## Food", ""] + ["- **%s:** %s" % (f["name"], f["what"]) for f in d["foods"]]
    L += ["", "## Clothing", "", d["clothing"]["principle"], ""]
    for k, v in d["clothing"]["for_the_outfit_generator"].items():
        L.append("- **%s:** %s" % (k, v if isinstance(v, str) else "; ".join(x if isinstance(x, str) else " -- ".join(x) for x in v) if isinstance(v, list) else "; ".join("%s: %s" % kv for kv in v.items())))
    L += ["", "## Names", "", d["names"]["convention"], ""]
    L += ["## Relations with the floor's factions", ""] + ["- **%s** (%+.2f): %s" % (k, v[0], v[1]) for k, v in d["faction_stance"].items()]
    L += ["", "## The hundred islands", "", "| id | name | kind | blocks | relief | people | specialty | bridges | larks | clan | founded |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in d["islands"]:
        L.append("| %s | %s | %s | %d | %s | %d | %s | %s | %d | %s | %d |" % (x["id"], x["name"], x["name_kind"], x["blocks"], x["relief"], x["population"], x["specialty"],
                                                                         x["bridge_style"], x["aerostats"], x["clan"], x["founded_vy"]))
    L += ["", "### Each island", ""]
    for x in d["islands"]:
        L += ["**%s %s** (%s: %s) -- %s" % (x["id"], x["name"], x["name_kind"], x["name_meaning"], x["character"]),
              "Water: %d pond(s) %s m2%s. Livestock: %s. Wildlife: %s." % (len(x["water"]["ponds_m2"]), "/".join(map(str, x["water"]["ponds_m2"])),
                  ", a lake of %d m2" % x["water"]["lake_m2"] if x["water"]["lake_m2"] else "", ", ".join("%s %s" % kv for kv in x["livestock"].items()), ", ".join(x["wildlife"])),
              "Trade: %s. Needs: %s. Top jobs: %s." % (", ".join(x["trade"]), ", ".join(x["needs"]),
                                                       ", ".join("%s %d" % (d["jobs"][k]["name"], v) for k, v in list(x["jobs"].items())[:5])), ""]
    return L
