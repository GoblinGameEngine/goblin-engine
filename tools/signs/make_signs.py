#!/usr/bin/env python3
"""Bitmap shop signs for every shop in the city and towns (the user, 2026-10-15: "I want bitmap signs on every shop if
possible. Simple ones you can make with the tools on this deck. Complicated ones you can use Grok.").

    ~/.venvs/ssc-assets/bin/python tools/signs/make_signs.py            # inventory, signs, atlases, index, docs
    ~/.venvs/ssc-assets/bin/python tools/signs/make_signs.py --only Calder

Each shop's sign is rendered with its actual NAME onto a background in one of 25 regional STYLES (5 per region, each
region's 5 sharing a heritage: research/flea_markets/09_sign_styles.md, written from STYLES below).

Where the signs go: every storefront sign that store.py built (its gold / neon lettering, kept as "T" rows in the model's
<model>.kit.json) is found, its board rectangle recovered from the lettering's size and place (store.py's sign_board
geometry), and the unit it belongs to matched (storefront i is unit <building>/i). The runtime (remake/scripts/
city_signs.gd) puts a textured quad over each board and drops the 3D lettering it replaces.

Out: godot_project/remake/signs/city/<Settlement>.png       RGBA (256-colour), signs shelf-packed at 48 px high
     godot_project/remake/signs/city/<Settlement>_emit.png  RGB, half res: albedo x night mask (the glow)
     godot_project/remake/signs/city_signs.json             building -> quads (frame, size, uv), model -> rows dropped
     research/flea_markets/09_sign_styles.md                the style catalogue + the inventory
     research/flea_markets/img/city_signs_<Settlement>.jpg  contact sheets (day | night)
Deterministic: every choice is a hash of (unit id, purpose).
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
GP = os.path.join(ROOT, "godot_project", "remake")
FONTS = os.path.join(ROOT, "reference", "fonts")
OUT = os.path.join(GP, "signs", "city")
IMG = os.path.join(ROOT, "research", "flea_markets", "img")
DOC = os.path.join(ROOT, "research", "flea_markets", "09_sign_styles.md")
H = 48                       # sign height in px (a 0.75 m board: 64 px / m)
SS = 3                       # supersampling
ATLAS_W = 2048
BOARD_H = 0.75               # store.py: band1 - band0 - 0.05


def h01(*parts):
    return int.from_bytes(hashlib.blake2b("|".join(map(str, parts)).encode(), digest_size=8).digest(), "little") / 2 ** 64


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


_fc = {}


def font(name, size):
    key = (name, size)
    if key not in _fc:
        p = os.path.join(FONTS, name + ".ttf")
        if not os.path.exists(p):
            p = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
        _fc[key] = ImageFont.truetype(p, size)
    return _fc[key]


# ================================================================================================ the style catalogue
# Per region: heritage (history, materials, palette, lettering) and 5 styles.  A style: fonts, palettes
# [(ground, letters, accent)], case, frame, letter treatment, night look, and assignment affinities:
#   cats: weight per place category; era: (from, to) years it suits; wealth: (lo, hi) on 0..1.
REGIONS = {
    "north_shore": {
        "name": "North Sea shore",
        "heritage": "Maritime New England on the cold sea: the chandlers, net lofts and ropewalks of Port Carrow, "
                    "Brightwater, Haven Point and Tern Harbor. Sign-painting learned from ship carvers: quarterboards, "
                    "gilt incised Roman capitals, rope and anchor ornament. Materials: painted pine, teak, brass, "
                    "enamelled iron, weathered shingle. Palette: navy, white, signal red, brass, sea green, tar black. "
                    "Lettering: Roman serif capitals (carved), slab stencils on the working waterfront. Lights: "
                    "goose-neck floodlamps and ship's lanterns, never neon.",
        "styles": {
            "quarterboard": dict(label="Ship's quarterboard", fonts=["Cinzel", "PlayfairDisplay"],
                pal=[("#f2eee2", "#c9a23a", "#1d2b45"), ("#1d2b45", "#d8b452", "#f2eee2"), ("#7c2420", "#e2c26a", "#f2eee2")],
                case="upper", frame="pointed", letters="incised", night="flood",
                cats={"retail": 1.2, "food": 1.0, "service": 1.0, "drink": 1.2}, era=(1800, 1960), wealth=(0.3, 1.0),
                note="a long carved board with pointed scroll ends, gilt incised capitals, like a ship's name board"),
            "chandlery": dict(label="Chandlery painted board", fonts=["IMFeENrm28P", "OldStandard-Bold"],
                pal=[("#2f5d50", "#f2eee2", "#c9a23a"), ("#24324a", "#f2eee2", "#b8402e"), ("#6e3b2a", "#f2e6c8", "#2f5d50")],
                case="upper", frame="rope", letters="shadow", night="flood", picto="north",
                cats={"retail": 1.4, "food": 1.2, "industry": 1.0}, era=(1820, 1940), wealth=(0.2, 0.8),
                note="a painted board with a rope border and the trade's pictogram at the left end (Grok blanks C1-C2)"),
            "signal_enamel": dict(label="Signal-flag enamel", fonts=["Oswald", "Arvo-Bold"],
                pal=[("#1b2a4a", "#f4f4f0", "#c8202a"), ("#f4f4f0", "#1b2a4a", "#e0b020"), ("#c8202a", "#f4f4f0", "#1b2a4a")],
                case="upper", frame="enamel", letters="flat", night="flood", stripe=True,
                cats={"service": 1.4, "health": 1.4, "office": 1.2, "retail": 0.8}, era=(1900, 2100), wealth=(0.2, 0.9),
                note="vitreous enamel with a white rim and a signal-flag stripe at the end"),
            "teak_brass": dict(label="Teak and brass", fonts=["Marcellus-Regular", "Cinzel"],
                pal=[("#5a3418", "#e0bc62", "#2b1a0c"), ("#3a2412", "#e8c878", "#1a0f06")],
                case="upper", frame="wood", letters="metal", night="flood",
                cats={"office": 1.6, "service": 1.3, "food": 1.0, "lodging": 1.6, "health": 1.0}, era=(1880, 2100), wealth=(0.55, 1.0),
                note="varnished teak with raised brass letters: the harbour's banks, hotels and better shops"),
            "cannery_stencil": dict(label="Cannery stencil", fonts=["AlfaSlabOne-Regular", "Oswald"],
                pal=[("#8a8c86", "#1e1e1c", "#b23a2a"), ("#5b6a66", "#ecebe4", "#c89b2a"), ("#9c4a32", "#f0e6d0", "#2a2a28")],
                case="upper", frame="planks", letters="stencil", night="none",
                cats={"industry": 2.0, "food": 1.0, "retail": 0.8, "service": 1.0}, era=(1880, 1990), wealth=(0.0, 0.45),
                note="stencilled slab letters on weathered planks: the working waterfront"),
        }},
    "northland": {
        "name": "North Land",
        "heritage": "The stately Midwest and New England interior: courthouse squares, county seats, college towns "
                    "(Marlowe, Fenwick, Dunmore Crossing). Federal and Victorian sign-painting, gold leaf on black "
                    "smalt, porcelain enamel from the 1900s, brass plaques on the professions, painted ghost signs "
                    "on the brick. Materials: painted wood, gold leaf, enamel, brass, brick. Palette: oxblood, navy, "
                    "forest green, cream, gold leaf, black. Lettering: Roman and Didone serifs, small caps, gilt with "
                    "a shade line. Lights: warm floodlamps; no neon.",
        "styles": {
            "federal_gilt": dict(label="Federal gilt on black", fonts=["PlayfairDisplay", "Cinzel"],
                pal=[("#141414", "#d6b04a", "#7a1f1f"), ("#1c2a1c", "#d6b04a", "#e8dcc0"), ("#26172a", "#d6b04a", "#e8dcc0")],
                case="upper", frame="gilt_rule", letters="gilt", night="flood",
                cats={"retail": 1.3, "service": 1.2, "office": 1.0, "food": 1.0, "drink": 1.1}, era=(1790, 2100), wealth=(0.4, 1.0),
                note="gold leaf letters with a dark shade line on a black smalt board, a gilt rule round it"),
            "painted_shingle": dict(label="Painted shingle with pictogram", fonts=["IMFeENrm28P", "PlayfairDisplay"],
                pal=[("#8e2b22", "#efe3c2", "#c9a23a"), ("#24324a", "#efe3c2", "#c9a23a"), ("#2f5034", "#efe3c2", "#c9a23a")],
                case="title", frame="carved", letters="shadow", night="flood", picto="north",
                cats={"retail": 1.4, "food": 1.4, "service": 1.0, "drink": 1.0}, era=(1800, 1950), wealth=(0.2, 0.8),
                note="Colonial Revival carved and painted board, the trade's gilt pictogram at the left (Grok blanks)"),
            "porcelain": dict(label="Porcelain enamel", fonts=["Oswald", "Arvo-Bold"],
                pal=[("#1f3f8a", "#f6f4ee", "#c8202a"), ("#a8201c", "#f6f4ee", "#1f3f8a"), ("#f6f4ee", "#1f3f8a", "#a8201c")],
                case="upper", frame="enamel", letters="flat", night="flood",
                cats={"retail": 1.2, "health": 1.4, "service": 1.2, "food": 0.9}, era=(1895, 1970), wealth=(0.2, 0.8),
                note="a curved-cornered enamel sign with a white rim and a chip or two"),
            "brass_plaque": dict(label="Brass plaque", fonts=["Marcellus-Regular", "OldStandard-Bold"],
                pal=[("#b8923e", "#2a1e10", "#e8cf86"), ("#9a7a34", "#1e160a", "#d8bc70")],
                case="upper", frame="riveted", letters="engraved", night="flood",
                cats={"office": 2.0, "health": 1.6, "service": 1.4, "lodging": 1.2}, era=(1800, 2100), wealth=(0.5, 1.0),
                note="polished brass, engraved and black-filled, four rivets: the professions"),
            "ghost_sign": dict(label="Mill-town ghost sign", fonts=["AlfaSlabOne-Regular", "AbrilFatface-Regular"],
                pal=[("#8d4a36", "#e8dcc4", "#5a2e20"), ("#7a4434", "#e6d6a8", "#3e2418")],
                case="upper", frame="brick", letters="faded", night="none",
                cats={"retail": 1.0, "industry": 1.6, "food": 0.9, "service": 0.8, "none": 3.0}, era=(1860, 1940), wealth=(0.0, 0.4),
                note="letters painted straight on the brick a century ago, half weathered away"),
        }},
    "kettle_valley": {
        "name": "the river towns",
        "heritage": "The Kettle Valley and its river cities (Harrow Falls, Port Tamsin, Victory Bay, Cedar Ford): the "
                    "gradient between the shores. Riverboat and rail brought both: the North's serifs and gilt meet the "
                    "South's neon and pastel, so a classic base wears one laid-back accent. Materials: brick, cast "
                    "iron, terracotta, enamel, painted steel, a neon tube. Palette: the North's reds, greens and creams "
                    "with a sunset trim (coral, turquoise). Lettering: slab and Victorian display faces, Deco caps, a "
                    "script word in neon. Lights: bulbs and one neon element.",
        "styles": {
            "riverboat": dict(label="Riverboat Victorian", fonts=["Rye-Regular", "Sancreek-Regular"],
                pal=[("#8e1e1e", "#f2e2b0", "#e0b040"), ("#f2ead8", "#8e1e1e", "#1d4a6a"), ("#1d4a6a", "#f2e2b0", "#e0b040")],
                case="upper", frame="scroll", letters="shadow", night="bulbs",
                cats={"drink": 1.8, "leisure": 1.8, "food": 1.2, "retail": 1.0, "lodging": 1.4}, era=(1840, 1930), wealth=(0.2, 0.9),
                note="ornate Victorian display letters, scroll corners and a row of bulbs, like a packet boat's"),
            "deco_terracotta": dict(label="Art Deco terracotta", fonts=["Limelight-Regular", "PoiretOne-Regular"],
                pal=[("#e8d8b8", "#2a5a4a", "#c87a3a"), ("#e8d0b0", "#7a2a2a", "#2a5a6a"), ("#2a3a3a", "#e8c870", "#c87a3a")],
                case="upper", frame="deco", letters="flat", night="flood_accent",
                cats={"retail": 1.2, "service": 1.4, "leisure": 1.6, "office": 1.2}, era=(1922, 1950), wealth=(0.4, 1.0),
                note="glazed terracotta with Deco sunburst corners and stepped caps, a neon line under the name"),
            "mainstreet_porcelain": dict(label="Main Street porcelain with neon", fonts=["Oswald", "Righteous-Regular"],
                pal=[("#245a3a", "#f4f0e2", "#ff7a52"), ("#7a1e2a", "#f4f0e2", "#3ac8c8"), ("#22385a", "#f4f0e2", "#ff8a3a")],
                case="upper", frame="enamel_neon", letters="flat", night="neon_frame",
                cats={"retail": 1.4, "food": 1.3, "health": 1.0, "service": 1.0}, era=(1925, 1975), wealth=(0.2, 0.8),
                note="classic enamel, outlined in a neon tube that lights at dusk"),
            "rail_depot": dict(label="Rail-depot board", fonts=["JosefinSlab", "Arvo-Bold"],
                pal=[("#141414", "#f2f0e8", "#c8a040"), ("#2a3a2a", "#f2f0e8", "#c8a040"), ("#3a2a22", "#f2e8d0", "#c86a3a")],
                case="upper", frame="double_rule", letters="flat", night="flood",
                cats={"office": 1.4, "industry": 1.4, "logistics": 2.0, "service": 1.1, "retail": 0.8}, era=(1850, 1960), wealth=(0.1, 0.8),
                note="a black depot board with spaced white slab capitals and a double rule"),
            "serif_neon_script": dict(label="Serif board with a neon word", fonts=["PlayfairDisplay", "Pacifico-Regular"],
                pal=[("#efe6cc", "#2a2a2a", "#ff4a8a"), ("#2a3a4a", "#efe6cc", "#3ae0d0"), ("#6a1e1e", "#efe6cc", "#ffb43a")],
                case="split", frame="plain_rule", letters="flat", night="neon_word",
                cats={"food": 1.6, "drink": 1.6, "retail": 1.2, "leisure": 1.2}, era=(1900, 2100), wealth=(0.2, 1.0),
                note="the name's first word in classic serif, the trade in glowing neon script: the river's signature"),
        }},
    "southland": {
        "name": "South Land",
        "heritage": "Inland California: the Central Valley and Route 30 (Kessler, Bellhaven, Tamarack, Pruett, Calder). "
                    "Roadside commerce read from a moving car: Streamline Moderne in the rail city, Googie on the "
                    "highway strip, Mission Revival in the old plazas, citrus-crate colour everywhere. Materials: "
                    "stucco, terracotta tile, porcelain steel, chrome, neon tube, chase bulbs. Palette: turquoise, "
                    "sunset orange, cream, chrome, red, palm green, night blue. Lettering: Deco and Streamline caps, "
                    "Googie script, slab marquee letters. Lights: neon and chase bulbs.",
        "styles": {
            "googie_neon": dict(label="Googie neon", fonts=["Righteous-Regular", "Monoton-Regular"],
                pal=[("#3ab8b0", "#fff6e0", "#ff6a2a"), ("#ff8a3a", "#fff6e0", "#2a6ab0"), ("#1a2a4a", "#ffe0a0", "#ff4a8a")],
                case="upper", frame="boomerang", letters="neon", night="neon", picto="south",
                cats={"food": 1.8, "leisure": 1.8, "lodging": 1.8, "retail": 1.2, "service": 1.0}, era=(1945, 1975), wealth=(0.2, 0.9),
                note="a boomerang board with a starburst, neon letters and the trade's roadside pictogram (Grok blanks)"),
            "streamline_channel": dict(label="Streamline Moderne channel letters", fonts=["Limelight-Regular", "PoiretOne-Regular"],
                pal=[("#d8dcd8", "#c8202a", "#2a2a2a"), ("#d8dcd8", "#1a4a8a", "#2a2a2a"), ("#2a2a2a", "#e8e8e0", "#3ac8c8")],
                case="upper", frame="speed_lines", letters="channel", night="halo",
                cats={"retail": 1.4, "leisure": 1.6, "service": 1.2, "office": 1.0}, era=(1930, 1955), wealth=(0.4, 1.0),
                note="raised chrome-edged letters with speed lines on a cream fascia; the letters glow at night"),
            "mission_tile": dict(label="Mission tile", fonts=["Sancreek-Regular", "Marcellus-Regular"],
                pal=[("#efe0c4", "#7a2e1a", "#b8562a"), ("#e8d4b0", "#2a4a3a", "#b8562a")],
                case="upper", frame="tile_cap", letters="flat", night="flood",
                cats={"food": 1.3, "service": 1.3, "retail": 1.0, "office": 1.0, "civic": 1.6}, era=(1890, 1940), wealth=(0.3, 1.0),
                note="stucco with a terracotta tile cap and painted Mission lettering"),
            "citrus_label": dict(label="Citrus-crate label", fonts=["Shrikhand-Regular", "Lobster-Regular"],
                pal=[("#1a3a6a", "#ffb02a", "#ff6a2a"), ("#2a5a2a", "#fff0c0", "#ff8a2a"), ("#8a1a2a", "#ffe08a", "#2a8a4a")],
                case="title", frame="label", letters="outline", night="flood",
                cats={"food": 2.0, "retail": 1.2, "drink": 1.0}, era=(1900, 1960), wealth=(0.1, 0.8),
                note="a crate label: sun rays, a bordered field and fat outlined script"),
            "drive_in_marquee": dict(label="Drive-in marquee", fonts=["Bungee-Regular", "Oswald"],
                pal=[("#f6f2e0", "#1a1a1a", "#ff3a3a"), ("#f6f2e0", "#c8202a", "#1a1a1a")],
                case="upper", frame="marquee", letters="flat", night="backlit_bulbs",
                cats={"leisure": 2.4, "lodging": 1.6, "food": 1.0, "retail": 0.8}, era=(1930, 1980), wealth=(0.1, 0.9),
                note="a backlit changeable-letter box with chase bulbs"),
        }},
    "south_shore": {
        "name": "South Sea shore",
        "heritage": "The laid-back beach towns (Solana Point, Oceanview, Playa Verde, Pelican Cove): surf, piers, "
                    "taco stands and boardwalks, with the Lowliners' lanterns among them. Hand-painted by locals, "
                    "bright and sun-faded; tiki bars; Mexican rótulo painters; 1970s surf-shop supergraphics; neon "
                    "script over the boardwalk at night. Materials: painted plywood and planks, bamboo, carved wood, "
                    "stucco, neon. Palette: turquoise, coral, sunset orange, pink, sand, palm green, night blue. "
                    "Lettering: brush script, fat 70s display, hand-shadowed rótulo letters. Lights: neon script, "
                    "string bulbs, tiki torches.",
        "styles": {
            "surf_handpaint": dict(label="Surf-shop hand-paint", fonts=["KaushanScript-Regular", "Satisfy-Regular"],
                pal=[("#3ac8c8", "#fff6e0", "#ff6a52"), ("#ff8a6a", "#1a3a5a", "#fff6e0"), ("#f6e6c0", "#1a6a8a", "#ff6a52")],
                case="title", frame="planks_bright", letters="shadow", night="flood",
                cats={"retail": 1.6, "food": 1.2, "leisure": 1.4, "service": 1.0}, era=(1950, 2100), wealth=(0.1, 0.7),
                note="brush script on painted planks, sun-faded"),
            "tiki_carved": dict(label="Tiki carved", fonts=["Sancreek-Regular", "Rye-Regular"],
                pal=[("#6a3a1a", "#f2d28a", "#2a1a0a"), ("#4a2a12", "#ff9a3a", "#1a0e06")],
                case="upper", frame="bamboo", letters="incised", night="flood_warm",
                cats={"drink": 2.4, "food": 1.6, "leisure": 1.6, "lodging": 1.2}, era=(1935, 1975), wealth=(0.2, 0.9),
                note="carved wood in a bamboo frame, lit by torches"),
            "rotulo": dict(label="Mexican rótulo", fonts=["Lobster-Regular", "Shrikhand-Regular"],
                pal=[("#ffd23a", "#c8202a", "#1a5a2a"), ("#2ab0a0", "#fff6e0", "#ff4a8a"), ("#ff5a8a", "#fff6e0", "#1a3a8a")],
                case="title", frame="flourish", letters="shadow", night="flood",
                cats={"food": 2.0, "retail": 1.4, "service": 1.2, "drink": 1.4}, era=(1900, 2100), wealth=(0.0, 0.7),
                note="hand-lettered in bright flat colours with a drop shade and flourishes"),
            "supergraphic": dict(label="1970s supergraphic", fonts=["Shrikhand-Regular", "Bungee-Regular"],
                pal=[("#f6e8c8", "#5a2a12", "#ff7a1a"), ("#f6e8c8", "#1a3a5a", "#2ab0a0")],
                case="lower", frame="stripes", letters="flat", night="backlit",
                cats={"retail": 1.6, "leisure": 1.4, "service": 1.0, "food": 1.0}, era=(1965, 1995), wealth=(0.2, 0.8),
                note="rainbow stripes and fat lower-case letters on a backlit box"),
            "beach_neon_script": dict(label="Boardwalk neon script", fonts=["Pacifico-Regular", "Sacramento-Regular"],
                pal=[("#141c3a", "#ff4a9a", "#3ae0e0"), ("#141c3a", "#3ae0e0", "#ffd23a"), ("#1a1a2a", "#ffb43a", "#ff4a9a")],
                case="title", frame="dark_backer", letters="neon", night="neon",
                cats={"drink": 2.0, "food": 1.6, "leisure": 2.0, "lodging": 1.4, "retail": 1.0}, era=(1925, 2100), wealth=(0.2, 1.0),
                note="neon script on a dark backer over the boardwalk"),
        }},
}
REGION_OF = {"north_shore": "north_shore", "northland": "northland", "kettle_valley": "kettle_valley",
             "southland": "southland", "south_shore": "south_shore"}

# place type -> the C-sheet pictogram key (signs.json biz_<band>_<key>)
PICTO = {"grocery": "grocery", "bakery": "bakery", "butcher": "butcher", "fish_market": "fish_market", "cafe": "cafe",
         "diner": "diner", "restaurant": "restaurant", "bar": "bar", "liquor_store": "liquor", "hardware": "hardware",
         "clothing": "clothing", "variety_store": "thrift", "thrift_store": "thrift", "bookstore": "bookstore",
         "jeweler": "jeweller", "florist": "florist", "furniture": "furniture", "sporting_goods": "sporting_goods",
         "gym": "sporting_goods", "charge_stop": "charge_stop", "newsagent": "newsagent", "drug_store": "drug_store",
         "doctor_office": "doctor", "dentist": "doctor", "barber": "barber", "beauty_salon": "beauty_salon",
         "laundromat": "laundromat", "bank": "bank", "insurance_office": "office", "law_office": "office",
         "accounting_office": "office", "architect_office": "office", "engineering_office": "office",
         "insurance_agency": "office", "registry_office": "office", "print_shop": "print_shop", "repair_shop": "repair",
         "auto_repair": "repair", "funeral_home": "funeral_home", "movie_theater": "movie_theatre", "arcade": "arcade",
         "amusement": "arcade", "hotel": "hotel", "motel": "hotel", "food_stand": "diner"}
# the short noun a sign uses for a place type
NOUN = {"grocery": "Market", "bakery": "Bakery", "butcher": "Meats", "fish_market": "Fish Market", "cafe": "Café",
        "diner": "Diner", "restaurant": "Kitchen", "bar": "Tavern", "liquor_store": "Liquors", "drug_store": "Drug",
        "hardware": "Hardware", "clothing": "Clothiers", "variety_store": "Variety", "thrift_store": "Thrift",
        "bookstore": "Books", "jeweler": "Jewelers", "florist": "Flowers", "furniture": "Furniture",
        "sporting_goods": "Outfitters", "charge_stop": "Charge & Go", "newsagent": "News", "barber": "Barber Shop",
        "beauty_salon": "Beauty Salon", "laundromat": "Laundry", "bank": "Savings Bank", "insurance_office": "Insurance",
        "law_office": "Attorneys", "print_shop": "Printing", "repair_shop": "Repairs", "auto_repair": "Garage",
        "funeral_home": "Funeral Home", "doctor_office": "Clinic", "dentist": "Dental", "post_office": "Post Office",
        "movie_theater": "Theatre", "arcade": "Arcade", "gym": "Gym", "hotel": "Hotel", "motel": "Motel",
        "accounting_office": "Accounts", "architect_office": "Architects", "engineering_office": "Engineering",
        "insurance_agency": "Assurance", "registry_office": "Registry", "dispatch_office": "Dispatch",
        "courier_office": "The Courier", "board_office": "Board Office", "wire_studio": "Wire Studio",
        "works_office": "Works Office", "college_extension": "Extension", "childcare": "Day Nursery",
        "community_hall": "Hall", "food_stand": "Snacks", "care_home": "Care Home", "library": "Library"}
TRADE_WORDS = {w.lower() for v in NOUN.values() for w in v.split()} | {
    "market", "store", "shop", "co", "co.", "company", "and", "&", "sons", "bros", "drug", "drugs", "pharmacy", "goods",
    "dry", "general", "supply", "supplies", "variety", "mercantile", "emporium", "the", "cafe", "café", "grill", "bar",
    "tavern", "inn", "hotel", "bank", "savings", "trust", "hardware", "books", "news", "barber", "salon", "dental",
    "office", "agency", "insurance", "law", "printing", "garage", "repair", "repairs", "theatre", "theater", "meats",
    "bakery", "florist", "flowers", "jewelers", "jeweler", "clothing", "clothiers", "furniture", "liquor", "liquors",
    "outfitters", "sporting", "diner", "kitchen", "restaurant", "laundry", "laundromat", "funeral", "home", "clinic",
    "parlor", "parlour", "lunch", "luncheonette", "five", "dime", "&co", "shop", "shops", "pizza", "pizzeria", "sporting",
    "clothes", "shoe", "shoes", "feed", "auto", "tax", "gallery", "cleaners", "dry-goods", "depot", "brewing", "infirmary",
    "southland", "main", "street", "ring", "line", "highway", "harrow", "merchants", "national", "first", "union",
    "farmers", "deli", "delicatessen", "seafood", "fish", "tackle", "bait", "marine", "motors", "service", "station",
    "studio", "photo", "apothecary", "chemist", "pawn", "cycle", "radio", "electric", "appliance", "appliances"}
CAT_MAP = {"food": "food", "drink": "drink", "retail": "retail", "service": "service", "health": "health",
           "office": "office", "leisure": "leisure", "lodging": "lodging", "industry": "industry", "civic": "civic",
           "logistics": "logistics", "none": "none", "education": "civic", "faith": "civic", "station": "civic",
           "farm": "industry", "residence": "none"}


# ================================================================================================ inputs
def load_inputs():
    pl = {b["id"]: b for b in json.load(open(os.path.join(GP, "placement.json")))["structures"]}
    idx = json.load(open(os.path.join(GP, "characters", "npc_place_index.json")))["units"]
    types = json.load(open(os.path.join(GP, "characters", "npc_places.json")))["types"]
    law = {s["name"]: s for s in json.load(open(os.path.join(GP, "law", "settlements.json")))["settlements"]}
    return pl, idx, types, law


def catalog(model):
    p = os.path.join(ROOT, "remake", "catalog", model + ".json")
    return json.load(open(p)) if os.path.exists(p) else {}


_mats_cache = {}


def text_kind(model, mat):
    """'gold' / 'neon' / 'other' for a T row's material (by its def in <model>.mats.json)."""
    if model not in _mats_cache:
        p = os.path.join(GP, "buildings", model + ".mats.json")
        _mats_cache[model] = json.load(open(p)) if os.path.exists(p) else {}
    d = _mats_cache[model].get(mat) or {}
    if d.get("emission"):
        return "neon"
    c = d.get("color") or [0, 0, 0]
    if float(d.get("metal", 0)) > 0.5 and c[0] > 0.6 and c[2] < 0.4:
        return "gold"
    return "other"


def sign_slots(model):
    """The storefront signs a model carries: [(rows idx list, centre, right, up, normal, w, h, lines)] in kit order."""
    p = os.path.join(GP, "buildings", model + ".kit.json")
    if not os.path.exists(p):
        return []
    rows = json.load(open(p))
    groups = []                  # [key, [ri...]]
    for ri, r in enumerate(rows):
        if r[0] != "T":
            continue
        m = r[4]
        X = np.array([m[0], m[4], m[8]])
        Z = np.array([m[2], m[6], m[10]])
        sc = float(np.linalg.norm(X))
        y = m[7]
        if not (2.3 < y < 9.0 and 0.06 < sc < 0.5):
            continue
        if abs(X[1]) > 0.2 * sc or abs(Z[1]) > 0.2 * sc:
            continue                                 # (tilted: not a fascia)
        if text_kind(model, r[3]) == "other":
            continue
        key = (round(m[3], 1), round(m[11], 1))
        for g in groups:
            if abs(g[0][0] - key[0]) < 0.15 and abs(g[0][1] - key[1]) < 0.15:
                g[1].append(ri)
                break
        else:
            groups.append([key, [ri]])
    out = []
    for key, ris in groups:
        lines = sorted(ris, key=lambda ri: -rows[ri][4][7])
        n = len(lines)
        m0 = rows[lines[0]][4]
        X = np.array([m0[0], m0[4], m0[8]])
        Z = np.array([m0[2], m0[6], m0[10]])
        s0 = float(np.linalg.norm(X))
        right, normal = X / s0, Z / np.linalg.norm(Z)
        up = np.cross(normal, right)
        up = up / np.linalg.norm(up)
        if up[1] < 0:
            up = -up
        txt = rows[lines[0]][1]
        L = max(6, len(txt))
        if s0 >= 0.419:
            w = min(7.5, s0 * L / 1.35 * 1.5)
        elif s0 <= 0.141:
            w = 0.1 * len(txt)
        else:
            w = s0 * L / 1.35
        w = max(1.6, w)
        y0 = m0[7]
        band0 = y0 + s0 * 0.35 - BOARD_H * (1 - 0.5 / n)
        c = np.array([m0[3], band0 + BOARD_H / 2, m0[11]]) + normal * 0.012
        out.append(dict(rows=lines, c=c, right=right, up=up, normal=normal, w=w, h=BOARD_H,
                        lines=[rows[ri][1] for ri in lines], x=m0[3]))
    # neighbour spacing caps the width of clamped boards
    xs = sorted(o["x"] for o in out)
    for o in out:
        others = [abs(o["x"] - x) for x in xs if abs(o["x"] - x) > 0.5]
        if others:
            o["w"] = min(o["w"], max(1.6, min(others) - 0.6))
    return out


# ================================================================================================ naming
def proprietor(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'\.-]*", text)
    def base(t):
        t = t.lower().rstrip(".")
        return t[:-2] if t.endswith("'s") else t[:-1] if t.endswith("'") else t
    keep = []
    for t in toks:
        b = base(t)
        if b in TRADE_WORDS or b.rstrip("s") in TRADE_WORDS or b + "s" in TRADE_WORDS:
            if keep:
                break                       # (the name ends where the trade begins)
            continue
        if t.lower() not in (k.lower() for k in keep):
            keep.append(t)
    return re.sub(r"'s$", "", " ".join(keep[:2]).title().replace("'S", "'s"))


def shop_name(u, cat_rec, slot, types, surnames):
    """The name on the sign. The catalog's own sign text is kept when the unit is what the sign says; otherwise the
    proprietor's name (from the old sign, or a local surname) with the new trade's noun."""
    t = u["type"]
    old = (slot["lines"][0] if slot else "") or ""
    if t == "vacant":
        return old.title() if old else "", "FOR LEASE"
    if old and u.get("hint") in (t, None):
        return old.title(), (slot["lines"][1].title() if slot and len(slot["lines"]) > 1 else "")
    noun = NOUN.get(t) or types.get(t, {}).get("name", "Shop").split("/")[0].strip()
    prop = proprietor(old) if old else ""
    if not prop:
        prop = surnames[int(h01(u["uid"], "surname") * len(surnames))] if surnames else "Main Street"
    r = h01(u["uid"], "pattern")
    if t in ("bank", "insurance_agency", "law_office", "accounting_office", "architect_office", "engineering_office"):
        name = "%s %s" % (prop, noun) if r < 0.6 else "%s & Co. %s" % (prop.split()[0], noun)
    elif r < 0.45:
        last = re.sub(r"'s$", "", prop.split()[-1])
        name = "%s%s %s" % (last, "'" if last.endswith("s") else "'s", noun)
    elif r < 0.85:
        name = "%s %s" % (prop, noun)
    else:
        name = "The %s %s" % (prop.split()[0], noun)
    return name, ""


# ================================================================================================ style assignment
def wealth_of(u, rec, types, tier):
    cond = (rec.get("traits") or {}).get("condition", "kept")
    w = {"pristine": 0.85, "kept": 0.6, "worn": 0.35, "shabby": 0.2, "derelict": 0.05}.get(cond, 0.5)
    w += 0.08 * (types.get(u["type"], {}).get("price", 1) - 1)
    w += {"city": 0.08, "town": 0.04, "village": 0.0, "hamlet": -0.05}.get(tier, 0)
    return min(1.0, max(0.0, w))


def pick_style(u, rec, types, region, t_axis, tier, block_key, prev):
    """Weighted by business category, the street's age and the area's wealth; a block's lead style is favoured so the
    street reads as one place, the next-door shop's style is avoided so neighbours vary."""
    fams = [region]
    if region == "kettle_valley":                     # the river: borrow from both shores by the gradient
        fams += ["northland", "southland"]
    elif region == "northland" and t_axis > 0.3:
        fams += ["kettle_valley"]
    elif region == "southland" and t_axis < 0.7:
        fams += ["kettle_valley"]
    cat = CAT_MAP.get(types.get(u["type"], {}).get("category", "retail"), "retail")
    year = (rec.get("traits") or {}).get("year_built", 1925)
    wealth = wealth_of(u, rec, types, tier)
    lead = None
    cands = []
    for fam in fams:
        fw = 1.0 if fam == region else (0.45 * (1 - t_axis) if fam == "northland" else 0.45 * t_axis if fam == "southland" else 0.35)
        for sid, st in REGIONS[fam]["styles"].items():
            w = fw * st["cats"].get(cat, 0.5)
            e0, e1 = st["era"]
            w *= 1.0 if e0 <= year <= e1 else 0.25
            w0, w1 = st["wealth"]
            w *= 1.0 if w0 <= wealth <= w1 else 0.3
            if u["type"] == "vacant":
                w = 3.0 if sid == "ghost_sign" else (1.0 if st["frame"] in ("planks", "brick") else 0.15)
            cands.append([(fam, sid), w])
    lead_r = h01(block_key, "lead")
    tot = sum(w for _, w in cands)
    acc = 0
    for c in cands:
        acc += c[1] / tot
        if lead_r <= acc:
            lead = c[0]
            break
    for c in cands:
        if c[0] == lead:
            c[1] *= 2.6
        if prev and c[0] == prev:
            c[1] *= 0.15
    tot = sum(w for _, w in cands)
    r = h01(u["uid"], "style")
    acc = 0
    for c, w in cands:
        acc += w / tot
        if r <= acc:
            return c
    return cands[-1][0]


# ================================================================================================ rendering
def fit_font(d, text, name, maxw, maxh):
    size = int(maxh)
    while size > 6:
        f = font(name, size)
        b = d.textbbox((0, 0), text, font=f, anchor="ls")
        if b[2] - b[0] <= maxw and (b[3] - b[1]) <= maxh * 1.05:
            return f
        size = int(size * 0.92)
    return font(name, 6)


def case_of(text, case):
    if case == "upper":
        return text.upper()
    if case == "lower":
        return text.lower()
    return text


def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


_picto = {}


def picto_img(band, ptype):
    key = PICTO.get(ptype)
    if not key:
        return None
    if (band, key) not in _picto:
        idx = json.load(open(os.path.join(GP, "signs", "signs.json")))
        c = idx["cells"].get("biz_%s_%s" % (band, key))
        if c is None:
            _picto[(band, key)] = None
        else:
            at = Image.open(os.path.join(GP, "signs", "biz.png")).convert("RGBA")
            x, y, w, h = c["region"]
            ox, oy, cw, ch = c["content"]
            cell = at.crop((x + ox, y + oy, x + ox + cw, y + oy + ch))
            # the pictogram is the left ~38 % of the blank (C sheets: "a pictogram of its trade at the left end")
            _picto[(band, key)] = cell.crop((0, int(ch * 0.08), int(cw * 0.4), int(ch * 0.92)))
    return _picto[(band, key)]


def render(style, fam, text, sub, ptype, seed, wpx):
    """-> (RGBA image wpx x H, emit level L image) at final size."""
    W, Hh = wpx * SS, H * SS
    st = REGIONS[fam]["styles"][style]
    pal = st["pal"][int(h01(seed, "pal") * len(st["pal"]))]
    bg, fg, ac = hx(pal[0]), hx(pal[1]), hx(pal[2])
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    emit = Image.new("L", (W, Hh), 0)
    d, e = ImageDraw.Draw(img), ImageDraw.Draw(emit)
    fr = st["frame"]
    m = int(Hh * 0.08)
    inner = [m, m, W - m, Hh - m]
    # ---- ground and frame
    if fr == "pointed":
        pts = [(Hh * 0.35, 0), (W - Hh * 0.35, 0), (W, Hh / 2), (W - Hh * 0.35, Hh), (Hh * 0.35, Hh), (0, Hh / 2)]
        d.polygon(pts, fill=bg + (255,))
        d.line(pts + [pts[0]], fill=ac + (255,), width=SS * 2)
        inner = [int(Hh * 0.45), m, W - int(Hh * 0.45), Hh - m]
    elif fr in ("rope", "carved"):
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        if fr == "rope":
            for x in range(0, W, SS * 6):
                d.ellipse((x, 0, x + SS * 6, SS * 5), fill=(196, 170, 120, 255))
                d.ellipse((x, Hh - SS * 5, x + SS * 6, Hh), fill=(196, 170, 120, 255))
        else:
            d.rectangle((SS * 2, SS * 2, W - SS * 2, Hh - SS * 2), outline=ac + (255,), width=SS * 2)
            d.rectangle((SS * 6, SS * 6, W - SS * 6, Hh - SS * 6), outline=tuple(int(v * 0.7) for v in bg) + (255,), width=SS)
    elif fr in ("enamel", "enamel_neon"):
        rounded(d, (0, 0, W - 1, Hh - 1), Hh // 5, fill=(246, 244, 238, 255))
        rounded(d, (SS * 3, SS * 3, W - SS * 3, Hh - SS * 3), Hh // 6, fill=bg + (255,))
        if st.get("stripe"):
            sw = Hh // 2
            for k, col in enumerate([ac, fg, ac]):
                d.rectangle((W - SS * 3 - sw + k * sw // 3, SS * 3, W - SS * 3 - sw + (k + 1) * sw // 3, Hh - SS * 3), fill=col + (255,))
            inner[2] -= sw
        if fr == "enamel_neon":
            rounded(d, (SS * 6, SS * 6, W - SS * 6, Hh - SS * 6), Hh // 7, fill=None, outline=ac + (255,), width=SS * 2)
            e.rounded_rectangle((SS * 6, SS * 6, W - SS * 6, Hh - SS * 6), Hh // 7, outline=255, width=SS * 3)
        # a chip in the enamel
        if h01(seed, "chip") < 0.35:
            cx = int(h01(seed, "cx") * W)
            d.ellipse((cx, Hh - SS * 7, cx + SS * 5, Hh - SS * 2), fill=(40, 36, 34, 255))
    elif fr == "wood":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        for y in range(0, Hh, SS * 4):
            d.line((0, y, W, y + SS), fill=tuple(int(v * 0.85) for v in bg) + (255,), width=SS)
        d.rectangle((0, 0, W - 1, Hh - 1), outline=ac + (255,), width=SS * 2)
    elif fr == "planks" or fr == "planks_bright":
        n = 3
        for k in range(n):
            sh = 0.9 + 0.2 * h01(seed, "pl", k)
            col = tuple(min(255, int(v * sh)) for v in bg)
            d.rectangle((0, k * Hh // n, W, (k + 1) * Hh // n - SS), fill=col + (255,))
        if fr == "planks_bright":
            d.rectangle((0, 0, W - 1, Hh - 1), outline=ac + (255,), width=SS * 2)
    elif fr == "gilt_rule":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        d.rectangle((SS * 3, SS * 3, W - SS * 3, Hh - SS * 3), outline=fg + (255,), width=SS)
        for cx, cy in ((SS * 3, SS * 3), (W - SS * 3, SS * 3), (SS * 3, Hh - SS * 3), (W - SS * 3, Hh - SS * 3)):
            d.ellipse((cx - SS * 2, cy - SS * 2, cx + SS * 2, cy + SS * 2), fill=fg + (255,))
    elif fr == "riveted":
        g = np.linspace(0.8, 1.15, Hh)[:, None]
        base = np.clip(np.array(bg)[None, None, :] * g[..., None], 0, 255).astype(np.uint8)
        img.paste(Image.fromarray(np.repeat(base, W, 1), "RGB").convert("RGBA"), (0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle((SS * 2, SS * 2, W - SS * 2, Hh - SS * 2), outline=fg + (255,), width=SS)
        for cx in (SS * 6, W - SS * 6):
            for cy in (SS * 6, Hh - SS * 6):
                d.ellipse((cx - SS * 2, cy - SS * 2, cx + SS * 2, cy + SS * 2), fill=fg + (255,))
    elif fr == "brick":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        bh = SS * 5
        for j, y in enumerate(range(0, Hh, bh)):
            d.line((0, y, W, y), fill=tuple(int(v * 0.75) for v in bg) + (255,), width=SS)
            off = (j % 2) * SS * 8
            for x in range(off, W, SS * 16):
                d.line((x, y, x, y + bh), fill=tuple(int(v * 0.75) for v in bg) + (255,), width=SS)
    elif fr == "scroll":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        d.rectangle((SS * 3, SS * 3, W - SS * 3, Hh - SS * 3), outline=ac + (255,), width=SS * 2)
        for cx in (SS * 10, W - SS * 10):
            d.arc((cx - SS * 8, SS * 4, cx + SS * 8, Hh - SS * 4), 0, 360, fill=ac + (255,), width=SS * 2)
        inner = [SS * 20, m, W - SS * 20, Hh - m]
    elif fr == "deco":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        for cx, sgn in ((0, 1), (W, -1)):
            for k in range(6):
                a = math.radians(-80 + k * 32)
                d.line((cx, Hh, cx + sgn * math.cos(a) * Hh * 0.9, Hh - abs(math.sin(a)) * Hh * 0.9), fill=ac + (255,), width=SS)
        d.rectangle((0, 0, W, SS * 3), fill=fg + (255,))
        d.rectangle((0, Hh - SS * 3, W, Hh), fill=fg + (255,))
        inner = [int(Hh * 0.9), m, W - int(Hh * 0.9), Hh - m]
    elif fr == "double_rule":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        d.rectangle((SS * 2, SS * 2, W - SS * 2, Hh - SS * 2), outline=fg + (255,), width=SS)
        d.rectangle((SS * 5, SS * 5, W - SS * 5, Hh - SS * 5), outline=fg + (255,), width=SS)
    elif fr == "plain_rule":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        d.rectangle((SS * 3, SS * 3, W - SS * 3, Hh - SS * 3), outline=fg + (255,), width=SS)
    elif fr == "boomerang":
        d.rectangle((0, 0, W, Hh), fill=(0, 0, 0, 0))
        pts = [(0, Hh * 0.15), (W * 0.5, 0), (W, Hh * 0.15), (W - Hh * 0.2, Hh), (Hh * 0.2, Hh)]
        d.polygon(pts, fill=bg + (255,))
        cx, cy, R = int(W - Hh * 0.45), int(Hh * 0.3), int(Hh * 0.28)
        for k in range(8):
            a = k * math.pi / 4
            d.line((cx, cy, cx + math.cos(a) * R, cy + math.sin(a) * R), fill=ac + (255,), width=SS * 2)
            e.line((cx, cy, cx + math.cos(a) * R, cy + math.sin(a) * R), fill=255, width=SS * 3)
        inner = [m, int(Hh * 0.18), W - int(Hh * 0.8), Hh - m]
    elif fr == "speed_lines":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        for k in range(3):
            y = int(Hh * (0.3 + 0.2 * k))
            d.line((W * 0.82, y, W - SS * 3, y), fill=ac + (255,), width=SS * 2)
        inner = [m, m, int(W * 0.8), Hh - m]
    elif fr == "tile_cap":
        d.rectangle((0, int(Hh * 0.22), W, Hh), fill=bg + (255,))
        for x in range(0, W, SS * 7):
            d.ellipse((x, 0, x + SS * 8, int(Hh * 0.3)), fill=ac + (255,))
        inner = [m, int(Hh * 0.28), W - m, Hh - m]
    elif fr == "label":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        cx, cy = W // 2, Hh * 1.4
        for k in range(18):
            a = math.pi + k * math.pi / 17
            d.polygon([(cx, cy), (cx + math.cos(a) * W, cy + math.sin(a) * W),
                       (cx + math.cos(a + 0.06) * W, cy + math.sin(a + 0.06) * W)], fill=tuple(min(255, int(v * 1.25)) for v in bg) + (255,))
        d.rectangle((SS * 2, SS * 2, W - SS * 2, Hh - SS * 2), outline=ac + (255,), width=SS * 3)
    elif fr == "marquee":
        rounded(d, (0, 0, W - 1, Hh - 1), SS * 3, fill=(30, 30, 30, 255))
        d.rectangle((SS * 7, SS * 7, W - SS * 7, Hh - SS * 7), fill=bg + (255,))
        for x in range(SS * 4, W - SS * 2, SS * 9):
            for y in (SS * 3, Hh - SS * 4):
                d.ellipse((x - SS * 2, y - SS * 2, x + SS * 2, y + SS * 2), fill=(255, 226, 150, 255))
                e.ellipse((x - SS * 3, y - SS * 3, x + SS * 3, y + SS * 3), fill=255)
        inner = [SS * 9, SS * 9, W - SS * 9, Hh - SS * 9]
    elif fr == "bamboo":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        for x in (0, W - SS * 6):
            d.rectangle((x, 0, x + SS * 6, Hh), fill=(196, 160, 90, 255))
            for y in range(SS * 6, Hh, SS * 10):
                d.line((x, y, x + SS * 6, y), fill=(120, 90, 40, 255), width=SS)
        d.rectangle((0, 0, W, SS * 4), fill=(196, 160, 90, 255))
        d.rectangle((0, Hh - SS * 4, W, Hh), fill=(196, 160, 90, 255))
        inner = [SS * 9, SS * 6, W - SS * 9, Hh - SS * 6]
    elif fr == "flourish":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        d.rectangle((SS * 2, SS * 2, W - SS * 2, Hh - SS * 2), outline=ac + (255,), width=SS * 2)
        for cx in (SS * 8, W - SS * 8):
            d.ellipse((cx - SS * 4, Hh // 2 - SS * 4, cx + SS * 4, Hh // 2 + SS * 4), fill=ac + (255,))
        inner = [SS * 14, m, W - SS * 14, Hh - m]
    elif fr == "stripes":
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
        cols = [(255, 122, 26), (255, 176, 42), (255, 214, 90), (200, 80, 30)] if "5a2a12" in pal[1] else \
               [(42, 176, 160), (58, 200, 200), (255, 176, 42), (26, 58, 90)]
        sw = Hh // 6
        for k, col in enumerate(cols):
            d.rectangle((0, Hh - (k + 1) * sw, int(W * 0.18), Hh - k * sw), fill=col + (255,))
            d.rectangle((int(W * 0.18), Hh - (k + 1) * sw, W, Hh - k * sw - sw // 2), fill=col + (255,)) if k == 0 else None
        inner = [int(W * 0.2), m, W - m, Hh - sw * 2]
    elif fr == "dark_backer":
        rounded(d, (0, 0, W - 1, Hh - 1), SS * 4, fill=bg + (255,))
    else:
        d.rectangle((0, 0, W, Hh), fill=bg + (255,))
    # ---- pictogram badge at the left end (the Grok C-sheet pictograms)
    if st.get("picto") and ptype:
        pi = picto_img(st["picto"], ptype)
        if pi is not None:
            ph = inner[3] - inner[1]
            pw = int(pi.width * ph / max(1, pi.height))
            pim = pi.resize((max(1, pw), max(1, ph)), Image.LANCZOS)
            img.alpha_composite(pim, (inner[0], inner[1]))
            inner[0] += pw + SS * 3
    # ---- lettering
    txt = case_of(text, st["case"] if st["case"] != "split" else "title")
    fname = st["fonts"][0]
    box = inner[:]
    lines = [(txt, fname)]
    if st["case"] == "split" and " " in txt:
        first, rest = txt.split(" ", 1)
        lines = [(first, st["fonts"][0]), (rest, st["fonts"][1])]
    if sub:
        lines = [(txt, fname), (case_of(sub, "upper" if st["case"] == "upper" else "title"), st["fonts"][1])]
    bw, bh = box[2] - box[0], box[3] - box[1]
    if "\n" in text:                       # a tenant plaque: one small line per office
        rows_ = text.split("\n")[:4]
        n = len(rows_)
        for k, t in enumerate(rows_):
            f = fit_font(d, t.upper(), st["fonts"][0], bw * 0.94, bh / n * 0.78)
            cy = box[1] + bh * (k + 0.5) / n
            d.text(((box[0] + box[2]) / 2 + SS * 0.5, cy + SS * 0.5), t.upper(), font=f, fill=(250, 236, 190, 200), anchor="mm")
            d.text(((box[0] + box[2]) / 2, cy), t.upper(), font=f, fill=fg + (255,), anchor="mm")
        lines = []
    elif len(lines) == 2 and st["case"] == "split" and not sub:
        # side by side: the serif word, then the neon script
        f1 = fit_font(d, lines[0][0], lines[0][1], bw * 0.45, bh * 0.62)
        f2 = fit_font(d, lines[1][0], lines[1][1], bw * 0.5, bh * 0.8)
        w1 = d.textlength(lines[0][0], font=f1)
        w2 = d.textlength(lines[1][0], font=f2)
        x = box[0] + (bw - w1 - w2 - SS * 4) / 2
        cy = (box[1] + box[3]) / 2
        d.text((x, cy), lines[0][0], font=f1, fill=fg + (255,), anchor="lm")
        draw_neon(img, emit, (x + w1 + SS * 4, cy), lines[1][0], f2, ac)
    else:
        n = max(1, len(lines))
        for k, (t, fn) in enumerate(lines):
            hh = bh * (0.62 if n == 2 and k == 0 else 0.34 if n == 2 else 0.78)
            f = fit_font(d, t, fn, bw * 0.96, hh)
            cy = box[1] + (bh * (0.38 if k == 0 else 0.82) if n == 2 else bh / 2)
            pos = ((box[0] + box[2]) / 2, cy)
            col = fg if k == 0 else ac if st["letters"] not in ("neon",) else fg
            treat = st["letters"]
            if treat in ("shadow", "incised", "gilt", "outline", "engraved", "metal"):
                sh = {"shadow": (0, 0, 0), "incised": tuple(int(v * 0.45) for v in bg), "gilt": (90, 60, 20),
                      "outline": ac, "engraved": (250, 236, 190), "metal": (30, 18, 8)}[treat]
                off = SS if treat != "outline" else 0
                if treat == "outline":
                    d.text(pos, t, font=f, fill=sh + (255,), anchor="mm", stroke_width=SS * 2, stroke_fill=sh + (255,))
                else:
                    d.text((pos[0] + off, pos[1] + off), t, font=f, fill=sh + (200,), anchor="mm")
                d.text(pos, t, font=f, fill=col + (255,), anchor="mm")
            elif treat == "faded":
                layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(layer).text(pos, t, font=f, fill=col + (255,), anchor="mm")
                a = np.array(layer)
                noise = np.random.default_rng(int(h01(seed, "fade") * 1e9)).random(a.shape[:2])
                a[..., 3] = (a[..., 3] * (0.35 + 0.45 * (noise > 0.35))).astype(np.uint8)
                img.alpha_composite(Image.fromarray(a))
            elif treat == "stencil":
                d.text(pos, t, font=f, fill=col + (255,), anchor="mm")
                bb = d.textbbox(pos, t, font=f, anchor="mm")
                for x in range(int(bb[0]), int(bb[2]), SS * 9):
                    d.line((x, bb[1], x, bb[3]), fill=bg + (255,), width=SS)
            elif treat == "neon":
                draw_neon(img, emit, pos, t, f, fg if k == 0 else ac, anchor="mm")
            elif treat == "channel":
                d.text((pos[0] + SS * 2, pos[1] + SS * 2), t, font=f, fill=(40, 40, 40, 255), anchor="mm")
                d.text(pos, t, font=f, fill=col + (255,), anchor="mm", stroke_width=SS, stroke_fill=(230, 230, 230, 255))
                if st["night"] == "halo":
                    e.text(pos, t, font=f, fill=255, anchor="mm")
            else:
                d.text(pos, t, font=f, fill=col + (255,), anchor="mm")
            if st["night"] == "neon_word" and k == 0 and n == 1:
                pass
            if st["night"] in ("backlit", "backlit_bulbs"):
                pass
    # ---- night: floodlit boards glow softly; bulbs and neon already drawn into the mask
    a = np.array(img)
    al = a[..., 3] > 0
    em = np.array(emit)
    night = st["night"]
    # Night (the user, 2026-10-16: "I cannot read the illuminated signs. They are washed out at night"): only the
    # LIT PARTS emit -- neon tubes, bulbs, lit letters (255, drawn above) and the letters of lamp-lit and backlit
    # boards (LETTER_EMIT, found by the letters' own colour) -- never the ground, so letters keep their contrast.
    if night != "none":
        lb = np.array(box_mask(img.size, inner))
        rgbf = a[..., :3].astype(np.int32)
        for colr in (fg, ac):
            dist = np.abs(rgbf - np.array(colr)).sum(-1)
            near = (dist < 70) & al & lb & (np.abs(np.array(colr) - np.array(bg)).sum() > 90)
            em = np.maximum(em, (near * LETTER_EMIT).astype(np.uint8))
        if night in ("backlit", "backlit_bulbs"):
            em = np.maximum(em, (al & lb.astype(bool)) * np.uint8(FACE_EMIT))
    if night == "bulbs":
        dd = ImageDraw.Draw(img)
        ee = Image.fromarray(em)
        de = ImageDraw.Draw(ee)
        for x in range(SS * 5, W - SS * 3, SS * 10):
            for y in (SS * 2, Hh - SS * 3):
                dd.ellipse((x - SS * 2, y - SS * 2, x + SS * 2, y + SS * 2), fill=(255, 226, 150, 255))
                de.ellipse((x - SS * 3, y - SS * 3, x + SS * 3, y + SS * 3), fill=255)
        a = np.array(img)
        em = np.array(ee)
    if night == "flood_accent":
        y = int(Hh * 0.84)
        ImageDraw.Draw(img).line((W * 0.2, y, W * 0.8, y), fill=hx(st["pal"][0][2]) + (255,), width=SS * 2)
        ee = Image.fromarray(em)
        ImageDraw.Draw(ee).line((W * 0.2, y, W * 0.8, y), fill=255, width=SS * 3)
        a, em = np.array(img), np.array(ee)
    out = Image.fromarray(a).resize((wpx, H), Image.LANCZOS)
    em_out = Image.fromarray(em).resize((wpx, H), Image.BILINEAR)
    return out, em_out


LETTER_EMIT = 255           # lit letters (shared night scale 2026-10-16: letters and neon 2.0 HDR = mask 255 x EMIT_SCALE 2.0)
FACE_EMIT = 115             # a lightbox face (backlit styles only): 2.0 x 115/255 (sRGB) <= 0.9 HDR; ground and backings 0


def box_mask(size, box):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rectangle(tuple(int(v) for v in box), fill=255)
    return m.point(lambda v: v > 0 and 1)


def draw_neon(img, emit, pos, text, f, col, anchor="lm"):
    W, Hh = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(pos, text, font=f, fill=col + (255,), anchor=anchor)
    glow = layer.filter(ImageFilter.GaussianBlur(SS * 2))
    img.alpha_composite(glow)
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(core).text(pos, text, font=f, fill=tuple(min(255, int(v * 0.5 + 128)) for v in col) + (255,), anchor=anchor)
    img.alpha_composite(layer)
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(SS * 0.5)))
    ImageDraw.Draw(emit).text(pos, text, font=f, fill=255, anchor=anchor, stroke_width=SS)


_rooms = None


def rooms_of(bid):
    global _rooms
    if _rooms is None:
        _rooms = {}
        d = os.path.join(GP, "rooms")
        for fn in os.listdir(d):
            if fn.endswith(".json") and not fn.startswith("_"):
                _rooms.update(json.load(open(os.path.join(d, fn))).get("buildings", {}))
    return _rooms.get(bid)


def tenant_plaque(bid, st, slots, uppers, types, surnames):
    """A brass directory plaque by the upper floors' street door: one line per office upstairs."""
    r = rooms_of(bid)
    if not r:
        return None
    door = next((d for d in r["doors"] if d.get("ext") and "STAIRHALL" in d.get("rooms", []) and d["at"][1] < 0), None)
    if door is None:
        return None
    s0 = slots[0]
    plane = float(s0["c"][2] - s0["normal"][2] * 0.012)
    side = 1.0 if door["at"][0] < s0["x"] else -1.0                    # (away from the shop's own door)
    c = np.array([door["at"][0] - s0["right"][0] * side * 0.95, 1.55, plane]) + s0["normal"] * 0.02
    lines = []
    for u in sorted(uppers, key=lambda u: u["uid"]):
        nm, _ = shop_name(u, {}, None, types, surnames)
        fl = re.fullmatch(r"O(\d+)_\d+", u["uid"].split("/")[-1]).group(1)
        lines.append("%s  %s" % (int(fl) + 1, nm))
    slot = dict(rows=[], c=c, right=s0["right"], up=s0["up"], normal=s0["normal"], w=0.96, h=0.48, lines=lines, x=c[0])
    u0 = dict(uppers[0], uid=bid + "/plaque", type="plaque")
    return (bid, slot, u0, "\n".join(lines), "", ("northland", "brass_plaque"))


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    pl, idx, types, law = load_inputs()
    units_of = defaultdict(list)
    for u in idx:
        units_of[u["building"]].append(u)
    # surnames for new proprietors: the catalog's business names, per settlement
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    inv = Counter()
    inv_reg = defaultdict(Counter)
    per_settle = defaultdict(list)       # settlement -> [(bid, slot, unit, name, sub, style)]
    models_rows = {}
    slot_cache = {}
    surn = defaultdict(list)
    recs = {}
    for bid, b in pl.items():
        rec = catalog(b["model"])
        recs[bid] = rec
        for sf in ((rec.get("traits") or {}).get("storefronts") or []):
            p = proprietor(sf.get("business") or "")
            if p:
                surn[b.get("settlement") or ""].append(p.split()[0])
    shop_shells = {"storefront", "strip_unit", "big_box", "restaurant_building", "kiosk", "motel"}
    for bid, us in sorted(units_of.items()):
        b = pl.get(bid)
        if b is None:
            continue
        st = us[0]["settlement"]
        if a.only and st != a.only:
            continue
        reg = law.get(st, {}).get("region", "northland")
        shops = [u for u in us if u["shell"] in shop_shells and u["type"] != "residence"]
        for u in us:
            cat = CAT_MAP.get(types.get(u["type"], {}).get("category", "none"), "none")
            inv["units"] += 1
            inv_reg[reg]["units"] += 1
            if u["shell"] in shop_shells and u["type"] != "residence":
                inv_reg[reg]["shop_units"] += 1
                inv_reg[reg]["cat_" + cat] += 1
        if not shops:
            continue
        model = b["model"]
        if model not in slot_cache:
            slot_cache[model] = sign_slots(model)
        slots = slot_cache[model]
        inv_reg[reg]["sign_slots"] += len(slots)
        # storefront i (store.py's sign_front<i>) is unit <bid>/B<i> (room manifests) or <bid>/<i> (procedural units);
        # the upper floors' offices (<bid>/O<floor>_<n>) get a tenant plaque by their street door instead
        byk = {}
        for u in shops:
            sfx = u["uid"].split("/")[-1]
            mm = re.fullmatch(r"B?(\d+)", sfx)
            if mm:
                byk[int(mm.group(1))] = u
        uppers = [u for u in shops if re.fullmatch(r"O(\d+)_(\d+)", u["uid"].split("/")[-1])]
        prev = None
        for k, slot in enumerate(slots):
            u = byk.get(k)
            if u is None and byk:                      # a wide shop's second board: the same shop again
                u = byk[max([kk for kk in byk if kk <= k] or [min(byk)])]
            if u is None:
                continue
            rec = recs[bid]
            surnames = surn.get(st) or surn.get("") or ["Main Street"]
            name, sub = shop_name(u, rec, slot, types, surnames)
            if not name:
                name, sub = "For Lease", ""
            tier = law.get(st, {}).get("tier", "town")
            tax = (law.get(st, {}).get("centre", [0, 0])[1] + 5600) / 11200
            block = "%s|%d|%d" % (st, int(b["s"] // 90), int(b["x"] // 90))
            style = pick_style(u, rec, types, reg, tax, tier, block, prev)
            prev = style
            per_settle[st].append((bid, slot, u, name, sub, style, model))
            models_rows.setdefault(model, set()).update(slot["rows"])
            inv_reg[reg]["signed"] += 1
            inv_reg[reg]["style_" + style[1]] += 1
        signed_here = sum(1 for k in range(len(slots)) if k in byk)
        if uppers and slots:
            plaque = tenant_plaque(bid, st, slots, uppers, types, surn.get(st) or ["Main Street"])
            if plaque:
                per_settle[st].append(plaque + (b["model"],))
                inv_reg[reg]["plaques"] += 1
                inv_reg[reg]["plaque_tenants"] += len(uppers)
                signed_here += len(uppers)
        inv_reg[reg]["unsigned_shop_units"] += max(0, len(shops) - signed_here)
    # ---------------- render + pack per settlement
    index = {"_about": "City shop signs (tools/signs/make_signs.py): per building, quads in the building root's frame "
                       "(the placement transform) over each storefront sign board; rows = the model's kit T rows they "
                       "replace (drop them).",
             "px_per_m": H / BOARD_H, "settlements": {}, "buildings": {},
             "models_drop_rows": {m: sorted(v) for m, v in models_rows.items()}}
    total_bytes = 0
    for st, items in sorted(per_settle.items()):
        slug = re.sub(r"[^A-Za-z0-9]+", "_", st)
        cells = []
        for (bid, slot, u, name, sub, (fam, style), model) in items:
            aspect = slot["w"] / slot["h"]
            wpx = int(min(576, max(96, round(H * aspect))))
            im, em = render(style, fam, name, sub, u["type"], u["uid"], wpx)
            cells.append((bid, slot, u, name, sub, fam, style, im, em))
        # shelf pack
        x = y = 0
        pos = []
        for c in cells:
            w = c[7].width
            if x + w > ATLAS_W:
                x, y = 0, y + H
            pos.append((x, y))
            x += w
        AH = y + H
        AH = 1 << (AH - 1).bit_length() if AH > 64 else 64
        atlas = Image.new("RGBA", (ATLAS_W, AH), (0, 0, 0, 0))
        emitA = Image.new("RGB", (ATLAS_W // 2, AH // 2), (0, 0, 0))
        night = Image.new("RGB", (ATLAS_W, AH), (12, 14, 22))
        day = Image.new("RGB", (ATLAS_W, AH), (100, 102, 108))
        for (bid, slot, u, name, sub, fam, style, im, em), (px, py) in zip(cells, pos):
            atlas.paste(im, (px, py))
            day.paste(im, (px, py), im)
            alb = np.array(im)[..., :3].astype(np.float32)
            emv = np.array(em).astype(np.float32)[..., None] / 255.0
            glow = np.clip(alb * emv * 1.0, 0, 255).astype(np.uint8)
            emitA.paste(Image.fromarray(glow).resize((im.width // 2, H // 2), Image.BILINEAR), (px // 2, py // 2))
            nt = np.clip(alb * 0.15 + alb * emv * 1.4, 0, 255).astype(np.uint8)
            night.paste(Image.fromarray(nt), (px, py), im)
            q = index["buildings"].setdefault(bid, {"settlement": st, "model": slot and items[0][6] or "", "quads": []})
            q["model"] = [it for it in items if it[0] == bid][0][6]
            q["quads"].append({"uid": u["uid"], "type": u["type"], "name": name, "sub": sub, "style": style, "region": fam,
                               "c": [round(float(v), 3) for v in slot["c"]],
                               "r": [round(float(v), 4) for v in slot["right"]],
                               "u": [round(float(v), 4) for v in slot["up"]],
                               "w": round(slot["w"], 3), "h": slot["h"],
                               "uv": [px / ATLAS_W, py / AH, im.width / ATLAS_W, H / AH]})
        ap_ = os.path.join(OUT, slug + ".png")
        ep_ = os.path.join(OUT, slug + "_emit.png")
        atlas.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(ap_, optimize=True)
        emitA.quantize(128, method=Image.Quantize.MEDIANCUT).convert("RGB").save(ep_, optimize=True)
        total_bytes += os.path.getsize(ap_) + os.path.getsize(ep_)
        index["settlements"][st] = {"png": "res://remake/signs/city/%s.png" % slug,
                                    "emit": "res://remake/signs/city/%s_emit.png" % slug,
                                    "size": [ATLAS_W, AH], "signs": len(cells)}
        cs = Image.new("RGB", (ATLAS_W, min(AH, 1024) * 2 + 8), (30, 30, 34))
        cs.paste(day.crop((0, 0, ATLAS_W, min(AH, 1024))), (0, 0))
        cs.paste(night.crop((0, 0, ATLAS_W, min(AH, 1024))), (0, min(AH, 1024) + 8))
        cs.save(os.path.join(IMG, "city_signs_%s.jpg" % slug), quality=82)
        print("%-16s %4d signs  atlas %dx%d  %4d KB" % (st, len(cells), ATLAS_W, AH,
                                                     (os.path.getsize(ap_) + os.path.getsize(ep_)) // 1024))
    if not a.only:
        json.dump(index, open(os.path.join(GP, "signs", "city_signs.json"), "w"), separators=(",", ":"))
        write_doc(inv_reg)
    print("total %.1f MB; signs %d" % (total_bytes / 1e6, sum(len(v) for v in per_settle.values())))


def write_doc(inv_reg):
    L = ["# 09 Sign styles: five families with a shared heritage per region", "",
         "The user, 2026-10-15: bitmap signs on every shop; \"come up with ... styles for each region that share a",
         "common heritage. It will add diversity to the world\" (5 per region, corrected). Regions as 07 §1.2.", "",
         "Each style below is a parameter set in `tools/signs/make_signs.py` (`REGIONS`): fonts (OFL / Apache, fetched",
         "by `tools/signs/fetch_fonts.sh`), palettes (ground, letters, accent), frame, letter treatment, night look and the",
         "affinities that assign it. Grok made what PIL can't: the trade pictograms on the painted and Googie styles",
         "(C sheets), and the island blanks (B sheets).", "",
         "**Assignment** (deterministic, `pick_style`): each candidate style's weight = its region family's weight",
         "(river towns also draw on the North and South by the gradient t) x its affinity for the business's category x",
         "1 if the building's year suits the style's era (else 0.25) x 1 if the area's wealth (building condition, the",
         "trade's price level, the town's tier) is in its range (else 0.3). A **block lead style** (hashed per 90 m",
         "block) gets x2.6, so the street reads as one place; the next-door shop's style gets x0.15, so neighbours",
         "vary. Vacant units get ghost signs and FOR LEASE boards.", ""]
    for rid, R in REGIONS.items():
        L += ["## %s" % R["name"], "", "**Heritage.** " + R["heritage"], "",
              "| style | fonts | palette (ground / letters / accent) | frame | letters | night | suits |", "|---|---|---|---|---|---|---|"]
        for sid, s in R["styles"].items():
            pal = "; ".join("/".join(p) for p in s["pal"])
            suits = ", ".join("%s" % k for k, v in sorted(s["cats"].items(), key=lambda kv: -kv[1])[:3]) + \
                    "; %d-%s; wealth %.1f-%.1f" % (s["era"][0], "" if s["era"][1] > 2050 else s["era"][1], *s["wealth"])
            L.append("| **%s** (`%s`): %s | %s | %s | %s | %s | %s | %s |" % (
                s["label"], sid, s["note"], ", ".join(s["fonts"]), pal, s["frame"], s["letters"], s["night"], suits))
        L.append("")
    L += ["## Islands", "",
          "Island shops are the RUNTIME's (`sky_signs.gd`, names drawn procedurally). Their art is the B-sheet blanks",
          "(`sky_a.png`, `sky_b.png`: per warren family a fascia, a blade and an emblem), grouped in nine broad cultural",
          "groups, five styles each (`ISLAND_STYLES` in this file) and the request in",
          "`research/sky_islands/warrens/runtime_requests.md`.", ""]
    for g, (name, sts) in ISLAND_STYLES.items():
        L.append("- **%s (%s):** %s" % (name, g, "; ".join("**%s** (%s)" % (k, v) for k, v in sts.items())))
    L += ["", "## Inventory (2026-10-15)", "",
          "Place units from `npc_place_index.json` (every building's units), sign boards found in the models' lettering.", "",
          "| region | all units | shop units | sign boards | signed | shop units without a board |", "|---|---|---|---|---|---|"]
    for rid in REGIONS:
        c = inv_reg.get(rid, Counter())
        L.append("| %s | %d | %d | %d | %d | %d |" % (REGIONS[rid]["name"], c["units"], c["shop_units"], c["sign_slots"],
                                                    c["signed"], c["unsigned_shop_units"]))
    L += ["", "Shop units by category and region:", "", "| region | " + " | ".join(sorted(CAT_MAP.values() - {"none"} if False else set(CAT_MAP.values()))) + " |",
          "|---" * (1 + len(set(CAT_MAP.values()))) + "|"]
    for rid in REGIONS:
        c = inv_reg.get(rid, Counter())
        L.append("| %s | " % REGIONS[rid]["name"] + " | ".join(str(c["cat_" + k]) for k in sorted(set(CAT_MAP.values()))) + " |")
    L += ["", "Styles used:", ""]
    for rid in REGIONS:
        c = inv_reg.get(rid, Counter())
        L.append("- %s: %s" % (REGIONS[rid]["name"], ", ".join("%s %d" % (k[6:], v) for k, v in c.most_common() if k.startswith("style_"))))
    open(DOC, "w").write("\n".join(L) + "\n")


ISLAND_STYLES = {
    "B1": ("North Africa and the Levant", {"zellige LED fascia": "tile border, horseshoe arch in LED",
            "pierced-brass lantern blade": "brass and coloured glass, warm bulbs", "kufic neon": "angular kufic-style Latin in green and gold neon",
            "ablaq lightbox": "red and cream bands, gold LED", "jasmine stone board": "black and white stone, vine border, floodlit"}),
    "B2": ("Arabia, Persia, the Silk Road", {"roshan lattice": "turquoise and white lattice frame", "qamariya glass": "rainbow half-moon top, backlit",
            "tile arabesque": "cobalt and turquoise tile, gold LED", "suzani banner": "embroidered hanging cloth with lamps",
            "brass coffee-house": "brass plaque with a glowing dallah"}),
    "B3": ("South Asia", {"pietra dura": "red sandstone with marble inlay, gold LED", "mirror-work banner": "mirror embroidery catching the bulbs",
            "marigold garland": "saffron board in a marigold LED garland", "truck art": "every inch painted, chrome edge, chains",
            "torana timber": "dark carved timber arch, copper trim"}),
    "B4": ("the Himalaya and China", {"stacked lightboxes": "red and yellow LED boxes stacked up a wall", "vertical red lightbox": "stacked letters, gold edge",
            "lantern pair": "red paper lanterns either side", "horse-head gable board": "white wall, black tiles", "prayer-flag strip": "five colours, endless knot"}),
    "B5": ("East Asian neon", {"neon canyon": "pink and cyan tube frames", "tiepi LED": "corrugated metal, green and red LED", "noren and chochin": "cloth curtain under paper lanterns",
            "dancheong eave": "pastel blue with painted eaves", "vertical LED column": "stacked letters in white LED"}),
    "B6": ("Southeast Asia and Matera", {"tube-house facade": "yellow board, green shutters", "chofa gilt": "teak with a gilded gable flourish",
            "jeepney chrome": "chrome edges, painted stripes, parol star", "Peranakan tile": "pastel fascia with tile border",
            "tufa and iron": "carved stone with an iron lamp"}),
    "B7": ("the Americas", {"cholet mirror-glass": "bright mirrored colours, step borders", "favela hand-paint": "bright painted board, tile edges",
            "iron lace": "pastel board, cast-iron lace corners", "bell-cast wood": "red and white carved board, maple leaf", "azulejo": "blue and white tile"}),
    "B8": ("the Mediterranean and Anatolia", {"whitewash and tile": "yellow ochre border, tile panel", "Cycladic dome": "white with a blue dome arch",
            "lemon ceramic": "painted ceramic plaque", "baroque limestone": "honey stone, carved frame, gallarija", "Iznik timber": "dark timber, tile inset, tulips"}),
    "B9": ("Northern Europe, the Balkans, the Caucasus", {"stepped gable": "brick red with white trim", "guild bracket": "wrought-iron bracket, hanging board",
            "tartan crow-step": "dark stone with a tartan stripe", "fretwork balcony": "blue and white carved railing", "copper plate": "Mardin copper, glowing coffee pot"}),
}

if __name__ == "__main__":
    main()
