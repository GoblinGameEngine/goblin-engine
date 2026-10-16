#!/usr/bin/env python3
"""Island flags and trailing banners for the 100 sky islands (the user, 2026-10-15: "Each Island should be trailing
large colorful banners that stretch 300m below the islands advertising its name and its wares. Each Island will need
its own ethno/political flag.").  PROVISIONAL designs until the political work.

    ~/.venvs/ssc-assets/bin/python tools/signs/make_flags.py

In:  godot_project/remake/bible/sky_islands.json (canon: clan colours, governance, specialty, trade, warren, faith)
     reference/grok/signs/E1, E2 (emblem silhouettes), BN1, BN2 (banner caps/tails per island cultural group)
     reference/fonts/ (tools/signs/fetch_fonts.sh)
Out: godot_project/remake/signs/flags.png             10 x 10 flags of 128 x 80 (forked fly: alpha), + flags_emit.png
     godot_project/remake/signs/sky/banners/SKY-xxx.png   the island's 4 banners, 64 x 1024 each, side by side
                                                    (256 x 1024), + SKY-xxx_emit.png (half res)
     godot_project/remake/signs/signs.json           "flags" and "banners" sections (other sections kept)
     research/sky_islands/flags.md                  every flag and what it means
     research/flea_markets/img/flags.jpg, banners_*.jpg   contact sheets

Flag grammar (vexillology: simple, 2-3 colours, one emblem, readable at a distance; never a copy of a real flag):
- Every Skein flag has a FORKED FLY (a swallowtail, "flown like a skein of geese"): the confederation's shared mark.
- The FIELD LAYOUT is the island's governance (helm: a hoist triangle like a prow; plumb rule: a central pale, the
  plumb line; council of elders: three bands, the Old Lines; consensus: a disc, the ring; mother house: a bordure,
  the house; lot: a diagonal, chance's cut; guild: a canton, the guild hall).
- The COLOURS are the clan's (bible clans[].colors), ordered for contrast.
- The EMBLEM is the island's specialty (what it makes), in the colour of best contrast.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from sheet_manifest import B_FAM  # noqa: E402

SRC = os.path.join(ROOT, "reference", "grok", "signs")
FONTS = os.path.join(ROOT, "reference", "fonts")
OUT = os.path.join(ROOT, "godot_project", "remake", "signs")
BOUT = os.path.join(OUT, "sky", "banners")
IMG = os.path.join(ROOT, "research", "flea_markets", "img")
DOC = os.path.join(ROOT, "research", "sky_islands", "flags.md")
FW, FH = 128, 80
BW, BH = 64, 1024
SS = 4

E1 = ["cloth", "rope", "mitten", "feather", "honeycomb", "weather", "snowflake", "moss", "lark", "bell",
      "hop", "plumb_triangle", "kite_letter", "drying_fish", "gas_flask", "knot_cord", "terraces_seedling", "ram",
      "perch", "scale", "geese", "aerostat", "swallow", "anchor_hook", "bridge"]
E2 = ["helm_wheel", "ring_dots", "lot_pebbles", "mother_house", "hammer_needle", "three_rings", "plumb_line",
      "rising_sun", "compass_star", "wind_star", "wave_lines", "dove", "lotus_wheel", "rosette", "seven_lamp",
      "open_hand", "dove_tower", "bell_tower", "glass_hall", "lark_cradle", "frozen_fall", "terraced_hill", "lantern",
      "rock_stair", "knot_crown"]
SPECIALTY_EMBLEM = {"skycloth": "cloth", "cordage": "rope", "knitwear": "mitten", "down": "feather",
                    "honey": "honeycomb", "weather": "weather", "ice": "snowflake", "moss": "moss", "larks": "lark",
                    "bells": "bell", "brewing": "hop", "survey": "plumb_triangle", "courier": "kite_letter",
                    "dried": "drying_fish", "gas": "gas_flask", "lore": "knot_cord", "gardens": "terraces_seedling",
                    "wool": "ram", "fish": "perch", "trade": "scale"}
GOV = {"helm": ("hoist triangle", "the Helm: a prow-shaped triangle at the hoist, the captain's bow"),
       "plumb_rule": ("pale", "plumb rule: a central upright band, the plumb line"),
       "council_elders": ("tribar", "council of elders: three bands, the Old Lines"),
       "consensus": ("disc", "consensus: a disc, the ring where everyone speaks"),
       "mother_house": ("bordure", "the mother house: a border enclosing the field, the house"),
       "lot": ("bend", "sortition by lot: a diagonal cut, chance's division"),
       "guild": ("canton", "the guild: a canton, the guild hall in the corner")}
# trade words -> pictograms for the wares banner
WARE_PICT = [("fish", "perch"), ("perch", "perch"), ("crayfish", "perch"), ("eel", "perch"), ("yarn", "ram"),
             ("fleece", "ram"), ("wool", "ram"), ("felt", "ram"), ("cheese", "lot_pebbles"), ("honey", "honeycomb"),
             ("wax", "honeycomb"), ("mead", "hop"), ("beer", "hop"), ("ale", "hop"), ("rope", "rope"),
             ("hawser", "rope"), ("net", "rope"), ("cloth", "cloth"), ("sail", "cloth"), ("tent", "cloth"),
             ("knit", "mitten"), ("mitten", "mitten"), ("down", "feather"), ("quilt", "feather"), ("feather", "feather"),
             ("forecast", "weather"), ("barometer", "weather"), ("ice", "snowflake"), ("snow", "snowflake"),
             ("moss", "moss"), ("dye", "moss"), ("lark", "lark"), ("fan", "lark"), ("envelope", "aerostat"),
             ("bell", "bell"), ("map", "compass_star"), ("survey", "plumb_triangle"), ("letter", "kite_letter"),
             ("mail", "kite_letter"), ("courier", "kite_letter"), ("dried", "drying_fish"), ("smoked", "drying_fish"),
             ("gas", "gas_flask"), ("hydrogen", "gas_flask"), ("story", "knot_cord"), ("lore", "knot_cord"),
             ("cord", "knot_cord"), ("seed", "terraces_seedling"), ("herb", "terraces_seedling"),
             ("fruit", "terraces_seedling"), ("green", "terraces_seedling"), ("goods", "scale"), ("broker", "scale"),
             ("egg", "lot_pebbles"), ("dove", "dove"), ("lantern", "lantern"), ("music", "bell")]
# island cultural group (the B sheets) -> fonts, East Asian stacking, banner blank columns (BN1 / BN2 index)
GROUP = {"B1": (["ReemKufi", "ArefRuqaa-Bold"], False, 0, 0), "B2": (["ArefRuqaa-Bold", "ReemKufi"], False, 1, 1),
         "B3": (["YatraOne-Regular", "RozhaOne-Regular"], False, 2, 2), "B4": (["DelaGothicOne-Regular", "PottaOne-Regular"], True, 3, 3),
         "B5": (["PottaOne-Regular", "Bungee-Regular"], True, 4, 4), "B6": (["Chonburi-Regular", "Kalam-Bold"], False, 5, 5),
         "B7": (["Sancreek-Regular", "CarterOne"], False, 6, 6), "B8": (["Marcellus-Regular", "Cinzel"], False, 7, 7),
         "B9": (["UncialAntiqua-Regular", "UnifrakturMaguntia-Book"], False, 8, 8)}
GROUP_NAME = {"B1": "North Africa and the Levant", "B2": "Arabia, Persia, the Silk Road", "B3": "South Asia",
              "B4": "the Himalaya and China", "B5": "East Asian neon", "B6": "Southeast Asia and Matera",
              "B7": "the Americas", "B8": "the Mediterranean and Anatolia", "B9": "Northern Europe, Balkans, Caucasus"}
WARREN_GROUP = {r[0]: g for g, rows in B_FAM.items() for r in rows if r[0] != "shared"}
# The user (2026-10-16): an island's people (heritage) and its architecture (warren style) often differ -- "it shows how
# cultures mixed" -- so flags and banners carry BOTH, plus the island's own emergent traits (clan, trade, governance).
# The warren culture's motif (the architecture's ornament, an E2 silhouette) per island cultural group:
WARREN_MOTIF = {"B1": "rosette", "B2": "compass_star", "B3": "lotus_wheel", "B4": "lantern", "B5": "wave_lines",
                "B6": "seven_lamp", "B7": "terraced_hill", "B8": "bell_tower", "B9": "knot_crown"}
# The people's heritage: an accent colour (invented, not any nation's) and a lettering family for the clan banner
HERITAGE = {"anglo": ("#1f3a68", "Cinzel"), "hispanic": ("#d9a521", "Lobster-Regular"),
            "francophone": ("#2b5aa8", "PlayfairDisplay"), "multi": ("#8a4fb8", "Righteous-Regular"),
            "black_anglo": ("#2f7d3a", "AlfaSlabOne-Regular"), "german": ("#303030", "OldStandard-Bold"),
            "east_asian": ("#c8302a", "DelaGothicOne-Regular"), "irish_scots": ("#2f8a5a", "UncialAntiqua-Regular"),
            "greek": ("#3a7cc0", "Marcellus-Regular"), "polish": ("#c8203a", "Oswald"), "black": ("#d07a1a", "Shrikhand-Regular"),
            "italian": ("#3a8a4a", "PlayfairDisplay"), "arab": ("#1a7a6a", "ArefRuqaa-Bold"), "indigenous": ("#9a4a2a", "CarterOne"),
            "station_coined": ("#c0c0c8", "Bungee-Regular"), "se_asian": ("#e0b020", "Chonburi-Regular"),
            "scandinavian": ("#2a4a8a", "JosefinSlab"), "south_asian": ("#e07a1a", "YatraOne-Regular"),
            "slavic": ("#3a5aa8", "RuslanDisplay-Regular"), "hungarian": ("#6a8a3a", "Arvo-Bold")}
WHITE, BLACK = (244, 241, 232), (26, 26, 28)


def h01(*parts):
    return int.from_bytes(hashlib.blake2b("|".join(map(str, parts)).encode(), digest_size=8).digest(), "little") / 2 ** 64


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def font(name, size):
    for fn in (name + ".ttf", name):
        p = os.path.join(FONTS, fn)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)


# ------------------------------------------------------------------------------------------------ emblems
def load_emblems():
    out = {}
    for sheet, names, rows, row0 in (("E1", E1, 5, 0), ("E2", E2, 6, 1)):
        im = np.array(Image.open(os.path.join(SRC, sheet, sheet + "_img1.jpg")).convert("L").resize((1024, 1024)))
        ch = 1024 / rows
        cw = 1024 / 5
        for k, nm in enumerate(names):
            r, c = divmod(k, 5)
            r += row0
            cell = im[int(r * ch) + 4:int((r + 1) * ch) - 4, int(c * cw) + 4:int((c + 1) * cw) - 4]
            m = cell < 120
            lab, n = ndimage.label(m)
            if n == 0:
                continue
            sz = ndimage.sum(m, lab, range(1, n + 1))
            m = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > 30])
            ys, xs = np.nonzero(m)
            a = (255 - cell[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).astype(np.float32)
            a = np.clip((a - 100) * 2.2, 0, 255).astype(np.uint8)       # dark = ink, soft edge
            out[nm] = Image.fromarray(a, "L")
    return out


def paste_emblem(dst, emb, box, colour):
    x0, y0, x1, y1 = box
    w, h = emb.size
    k = min((x1 - x0) / w, (y1 - y0) / h)
    e = emb.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    ox, oy = x0 + ((x1 - x0) - e.width) // 2, y0 + ((y1 - y0) - e.height) // 2
    layer = Image.new("RGBA", e.size, colour + (255,))
    dst.paste(layer, (ox, oy), e)


# ------------------------------------------------------------------------------------------------ flags
def flag_colours(cols):
    """Field colours (two, the most different clan colours) and the third for the device; light/dark ordered."""
    cs = [rgb(c) for c in cols][:3]
    while len(cs) < 3:
        cs.append(WHITE if lum(cs[0]) < 0.4 else BLACK)
    best = max(((i, j) for i in range(3) for j in range(3) if i < j), key=lambda p: contrast(cs[p[0]], cs[p[1]]))
    a, b = cs[best[0]], cs[best[1]]
    c = cs[3 - best[0] - best[1]]
    return a, b, c


def best_on(bg, cands):
    return max(cands, key=lambda c: contrast(c, bg))


def make_flag(isl, emblems):
    W, H = FW * SS, FH * SS
    a, b, c = flag_colours(isl["colors"])
    gov = isl["governance"]
    layout = GOV.get(gov, ("pale", ""))[0]
    flip = h01(isl["id"], "flip") < 0.5
    im = Image.new("RGBA", (W, H), a + (255,))
    d = ImageDraw.Draw(im)
    emb = emblems.get(SPECIALTY_EMBLEM.get(isl["specialty"], "scale"))
    ebg = a                                     # what the emblem sits on
    ebox = (int(W * 0.30), int(H * 0.18), int(W * 0.62), int(H * 0.82))
    if layout == "hoist triangle":
        d.rectangle((0, 0, W, H // 2), fill=a)
        d.rectangle((0, H // 2, W, H), fill=b)
        d.polygon([(0, 0), (int(W * 0.42), H // 2), (0, H)], fill=c if contrast(c, a) > 1.3 and contrast(c, b) > 1.3 else WHITE)
        tri = c if contrast(c, a) > 1.3 and contrast(c, b) > 1.3 else WHITE
        ebox = (int(W * 0.03), int(H * 0.33), int(W * 0.24), int(H * 0.67))
        ebg = tri
    elif layout == "pale":
        d.rectangle((int(W * 0.36), 0, int(W * 0.64), H), fill=b)
        ebg = b
        ebox = (int(W * 0.38), int(H * 0.22), int(W * 0.62), int(H * 0.78))
    elif layout == "tribar":
        d.rectangle((0, H // 3, W, 2 * H // 3), fill=b)
        if contrast(c, a) > 1.4:
            d.rectangle((0, H // 3 - SS * 3, W, H // 3), fill=c)
            d.rectangle((0, 2 * H // 3, W, 2 * H // 3 + SS * 3), fill=c)
        ebg = b
        ebox = (int(W * 0.34), int(H * 0.36), int(W * 0.58), int(H * 0.64))
    elif layout == "disc":
        r = int(H * 0.34)
        cx, cy = int(W * 0.42), H // 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=b)
        ebg = b
        ebox = (cx - int(r * 0.7), cy - int(r * 0.7), cx + int(r * 0.7), cy + int(r * 0.7))
    elif layout == "bordure":
        t = int(H * 0.13)
        d.rectangle((0, 0, W, H), fill=b)
        d.rectangle((t, t, W - t * 2, H - t), fill=a)
        ebox = (int(W * 0.26), int(H * 0.24), int(W * 0.58), int(H * 0.76))
    elif layout == "bend":
        if flip:
            d.polygon([(0, H), (W, 0), (W, H)], fill=b)
        else:
            d.polygon([(0, 0), (W, 0), (0, H)], fill=b)
            ebg = b
        ebox = (int(W * 0.06), int(H * 0.08), int(W * 0.34), int(H * 0.5)) if not flip else (int(W * 0.06), int(H * 0.08), int(W * 0.34), int(H * 0.5))
        ebg = b if not flip else a
    elif layout == "canton":
        d.rectangle((0, H // 2, W, H), fill=b)
        d.rectangle((0, 0, int(W * 0.4), H // 2), fill=c if contrast(c, a) > 1.3 else WHITE)
        ebg = c if contrast(c, a) > 1.3 else WHITE
        ebox = (int(W * 0.06), int(H * 0.05), int(W * 0.34), int(H * 0.45))
    ecol = best_on(ebg, [a, b, c, WHITE, BLACK])
    if emb is not None:
        paste_emblem(im, emb, ebox, ecol)
    # the architecture's motif (warren culture) in the upper fly, in the people's colour (heritage): the mix
    grp = WARREN_GROUP.get(isl["warren"], "B9")
    mot = emblems.get(WARREN_MOTIF.get(grp, "knot_crown"))
    hcol = rgb(HERITAGE.get(isl.get("heritage"), ("#c0c0c8", ""))[0])
    mbox = (int(W * 0.64), int(H * 0.05), int(W * 0.80), int(H * 0.31))
    under = im.getpixel(((mbox[0] + mbox[2]) // 2, mbox[1] + 2))[:3]
    mcol = hcol if contrast(hcol, under) >= 1.8 else best_on(under, [hcol, WHITE, BLACK, a, b, c])
    if mot is not None:
        paste_emblem(im, mot, mbox, mcol)
    # the Skein's forked fly (swallowtail): cut a notch at the fly
    mask = Image.new("L", (W, H), 255)
    md = ImageDraw.Draw(mask)
    md.polygon([(W, 0), (int(W * 0.82), H // 2), (W, H)], fill=0)
    im.putalpha(mask)
    im = im.resize((FW, FH), Image.LANCZOS)
    meaning = {"layout": layout, "layout_meaning": GOV.get(gov, ("", ""))[1],
               "colours": ["#%02x%02x%02x" % a, "#%02x%02x%02x" % b, "#%02x%02x%02x" % c],
               "emblem": SPECIALTY_EMBLEM.get(isl["specialty"], "scale"), "emblem_colour": "#%02x%02x%02x" % ecol,
               "warren_motif": WARREN_MOTIF.get(grp), "warren": isl["warren"], "heritage": isl.get("heritage"),
               "motif_colour": "#%02x%02x%02x" % mcol}
    return im, meaning


# ------------------------------------------------------------------------------------------------ banners
def load_banner_blanks():
    """BN1/BN2: nine banners each in the lower half of the sheet -> [(cap RGBA, tail RGBA, side strip RGBA, panel rgb)]"""
    out = {}
    for sheet in ("BN1", "BN2"):
        a = np.array(Image.open(os.path.join(SRC, sheet, sheet + "_img1.jpg")).convert("RGB").resize((1024, 1024)))
        r, g, b = (a[..., k].astype(np.int16) for k in range(3))
        bgm = (np.minimum(r, b) - g > 60) & (r > 150)
        fg = ~bgm
        fg[:520] = False
        fg = ndimage.binary_opening(fg, iterations=2)
        cols = fg.sum(0) > 120
        lab, n = ndimage.label(cols)
        spans = [np.nonzero(lab == i)[0] for i in range(1, n + 1)]
        spans = [s for s in spans if len(s) > 40][:9]
        res = []
        for s in spans:
            x0, x1 = s.min(), s.max() + 1
            sub = fg[:, x0:x1]
            ys = np.nonzero(sub.any(1))[0]
            y0, y1 = ys.min(), ys.max() + 1
            rgba = np.dstack([a[y0:y1, x0:x1], (fg[y0:y1, x0:x1] * 255).astype(np.uint8)])
            hgt = y1 - y0
            cap = Image.fromarray(rgba[:int(hgt * 0.24)], "RGBA")
            tail = Image.fromarray(rgba[int(hgt * 0.80):], "RGBA")
            mid = rgba[int(hgt * 0.40):int(hgt * 0.60)]
            side = Image.fromarray(mid[:, :max(4, (x1 - x0) // 7)], "RGBA")
            pc = np.median(mid[mid.shape[0] // 4:-mid.shape[0] // 4, (x1 - x0) // 3:2 * (x1 - x0) // 3, :3].reshape(-1, 3), 0)
            res.append((cap, tail, side, tuple(int(v) for v in pc)))
        out[sheet] = res
    return out


def vtext(img, text, font_name, box, colour, stacked, glow=None):
    """Lettering down a vertical strip: rotated (reads top to bottom) or stacked letters (East Asian manner)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    text = text.strip()
    if stacked:
        chars = [ch for ch in text.upper() if ch != " "]
        size = int(min(w * 0.82, h / max(1, len(chars)) * 0.9))
        f = font(font_name, size)
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(layer)
        step = h / max(1, len(chars))
        for i, ch in enumerate(chars):
            dd.text((w / 2, step * (i + 0.5)), ch, font=f, fill=colour + (255,), anchor="mm")
    else:
        size = int(w * 0.78)
        f = font(font_name, size)
        L = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f)
        if L > h * 0.96:
            size = int(size * h * 0.96 / L)
            f = font(font_name, max(8, size))
        tmp = Image.new("RGBA", (h, w), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((h / 2, w / 2), text, font=f, fill=colour + (255,), anchor="mm")
        layer = tmp.rotate(-90, expand=True)
    if glow is not None:
        al = layer.split()[3].filter(ImageFilter.GaussianBlur(w * 0.06))
        g = Image.new("RGBA", layer.size, glow + (0,))
        g.putalpha(al.point(lambda v: min(255, v * 2)))
        img.alpha_composite(g, (x0, y0))
    img.alpha_composite(layer, (x0, y0))
    return layer


def strip_body(W, H, panel, side):
    body = Image.new("RGBA", (W, H), panel + (255,))
    if side is not None:
        sw = max(3, W // 8)
        s = side.resize((sw, max(4, int(side.height * sw / max(1, side.width)))), Image.LANCZOS)
        for y in range(0, H, s.height):
            body.alpha_composite(s, (0, y))
            body.alpha_composite(s.transpose(Image.FLIP_LEFT_RIGHT), (W - sw, y))
    return body


def bulbs(img, emit, colour, every=26, inset=3):
    d, e = ImageDraw.Draw(img), ImageDraw.Draw(emit)
    W, H = img.size
    for y in range(every, H - every, every):
        for x in (inset, W - inset - 1):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=colour + (255,))
            e.ellipse((x - 3, y - 3, x + 3, y + 3), fill=255)


def emit_of(img):
    a = np.array(img).astype(np.float32) / 255
    mx, mn = a[..., :3].max(-1), a[..., :3].min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    lit = ((mx > 0.86) & (s > 0.55)) & (a[..., 3] > 0.5)
    return Image.fromarray((lit * 255).astype(np.uint8))


def make_banners(isl, flag_mean, blanks, emblems):
    """Four 64 x 1024 banners: 0 the name, 1 the wares, 2 the flag streamer, 3 the clan."""
    grp = WARREN_GROUP.get(isl["warren"], "B9")
    fonts, stacked, i1, i2 = GROUP[grp]
    cols = [rgb(c) for c in flag_mean["colours"]]
    out, info = [], []
    W, H = BW * 2, BH * 2                    # (drawn at 2x)
    for k in range(4):
        sheet = "BN1" if k in (0, 3) else "BN2"
        cap, tail, side, panel = blanks[sheet][i1 if sheet == "BN1" else i2]
        if k == 2:
            panel = cols[0]
        if k == 3:
            panel = cols[1]
            hacc = rgb(HERITAGE.get(isl.get("heritage"), ("#c0c0c8", ""))[0])
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        capH = int(cap.height * W / cap.width)
        tailH = int(tail.height * W / tail.width)
        body = strip_body(W, H - capH // 2 - tailH // 2, panel, side if k in (0, 1) else None)
        img.alpha_composite(body, (0, capH // 2))
        if k == 2:      # flag streamer: bands of the flag's colours with the emblem repeated
            d = ImageDraw.Draw(img)
            bh = (H - capH) // 9
            for j in range(9):
                d.rectangle((0, capH // 2 + j * bh, W, capH // 2 + (j + 1) * bh), fill=cols[j % 2] + (255,))
            em = emblems.get(flag_mean["emblem"])
            for j in range(1, 9, 2):
                if em is not None:
                    paste_emblem(img, em, (W // 6, capH // 2 + j * bh + bh // 8, W - W // 6, capH // 2 + (j + 1) * bh - bh // 8),
                                 best_on(cols[j % 2], cols + [WHITE, BLACK]))
        img.alpha_composite(cap.resize((W, capH), Image.LANCZOS), (0, 0))
        img.alpha_composite(tail.resize((W, tailH), Image.LANCZOS), (0, H - tailH))
        emit = emit_of(img)
        lbox = (W // 7, capH + 16, W - W // 7, H - tailH - 16)
        tcol = best_on(panel, [WHITE, BLACK, (255, 214, 120)] + cols)
        glow = (255, 255, 255) if lum(tcol) > 0.4 else None
        if k == 0:
            lay = vtext(img, isl["name"].upper(), fonts[0], lbox, tcol, stacked, glow)
            emit.paste(255, (lbox[0], lbox[1]), lay.split()[3].point(lambda v: 255 if v > 90 else 0))
            info.append({"kind": "name", "text": isl["name"]})
        elif k == 1:
            em_names = []
            for t in isl.get("trade", []):
                for key, em in WARE_PICT:
                    if key in t.lower() and em not in em_names:
                        em_names.append(em)
                        break
            sp = SPECIALTY_EMBLEM.get(isl["specialty"])
            if sp and sp not in em_names:
                em_names.insert(0, sp)
            em_names = em_names[:3]
            def short(t):
                t = t.split(" (")[0].split(",")[0].split(":")[0]
                for cut in (" between ", " for ", " of the ", " by ", " to "):
                    t = t.split(cut)[0]
                return " ".join(t.split()[:3]).upper()
            words = " \u00b7 ".join(short(t) for t in isl.get("trade", [])[:2])
            ph = int(W * 0.95)
            y = lbox[1]
            for em in em_names:
                paste_emblem(img, emblems[em], (W // 6, y, W - W // 6, y + ph), tcol)
                y += ph + 10
            lay = vtext(img, words, fonts[0] if "Unifraktur" in fonts[1] else fonts[1], (lbox[0], y + 6, lbox[2], lbox[3]), tcol, False, glow)
            emit.paste(255, (lbox[0], y + 6), lay.split()[3].point(lambda v: 255 if v > 90 else 0))
            info.append({"kind": "wares", "text": words, "pictograms": em_names})
        elif k == 2:
            info.append({"kind": "flag_streamer", "emblem": flag_mean["emblem"]})
        else:
            clan = (isl.get("clan") or "").replace("the ", "").replace("The ", "").upper()
            hfont = HERITAGE.get(isl.get("heritage"), ("", fonts[0]))[1]
            d3 = ImageDraw.Draw(img)                    # the people's colour: a band down each edge of the clan banner
            d3.rectangle((W // 8, capH, W // 8 + W // 10, H - tailH), fill=hacc + (255,))
            d3.rectangle((W - W // 8 - W // 10, capH, W - W // 8, H - tailH), fill=hacc + (255,))
            lay = vtext(img, clan, hfont, lbox, tcol, False, glow)
            emit.paste(255, (lbox[0], lbox[1]), lay.split()[3].point(lambda v: 255 if v > 90 else 0))
            info.append({"kind": "clan", "text": isl.get("clan")})
        bulbs(img, emit, (255, 226, 150) if k != 2 else WHITE, every=40 if k != 2 else 64, inset=5)
        out.append((img.resize((BW, BH), Image.LANCZOS), emit.resize((BW // 2, BH // 2), Image.BILINEAR)))
    return out, info, grp


# ------------------------------------------------------------------------------------------------ main
def main():
    bible = json.load(open(os.path.join(ROOT, "godot_project", "remake", "bible", "sky_islands.json")))
    isl = bible["islands"]
    emblems = load_emblems()
    blanks = load_banner_blanks()
    os.makedirs(BOUT, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    atlas = Image.new("RGBA", (FW * 10, FH * 10), (0, 0, 0, 0))
    flags_idx, ban_idx, doc = {}, {}, []
    seen = {}
    contact_b = []
    for n, it in enumerate(isl):
        im, mean = make_flag(it, emblems)
        i, j = n % 10, n // 10
        atlas.paste(im, (i * FW, j * FH))
        key = (mean["layout"], tuple(mean["colours"]), mean["emblem"])
        if key in seen:
            raise SystemExit("flags of %s and %s are the same" % (seen[key], it["id"]))
        seen[key] = it["id"]
        flags_idx[it["id"]] = dict(mean, i=i, j=j, region=[i * FW, j * FH, FW, FH],
                                   uv=[i / 10, j / 10, 0.1, 0.1], name=it["name"], clan=it.get("clan"), provisional=True)
        bans, binfo, grp = make_banners(it, mean, blanks, emblems)
        strip = Image.new("RGBA", (BW * 4, BH), (0, 0, 0, 0))
        estrip = Image.new("L", (BW * 2, BH // 2), 0)
        for k, (b, e) in enumerate(bans):
            strip.paste(b, (k * BW, 0))
            estrip.paste(e, (k * BW // 2, 0))
        strip.quantize(256, method=Image.Quantize.FASTOCTREE).save(os.path.join(BOUT, it["id"] + ".png"), optimize=True)
        estrip.save(os.path.join(BOUT, it["id"] + "_emit.png"), optimize=True)
        ban_idx[it["id"]] = {"png": "res://remake/signs/sky/banners/%s.png" % it["id"],
                             "emit": "res://remake/signs/sky/banners/%s_emit.png" % it["id"],
                             "size": [BW * 4, BH], "banner_px": [BW, BH], "group": grp,
                             "banners": [dict(b, uv=[k / 4, 0, 0.25, 1]) for k, b in enumerate(binfo)]}
        contact_b.append(strip)
        doc.append((it, mean, grp))
    atlas.save(os.path.join(OUT, "flags.png"), optimize=True)
    # signs.json: add/replace our sections only
    sp = os.path.join(OUT, "signs.json")
    idx = json.load(open(sp)) if os.path.exists(sp) else {}
    idx["flags"] = {"png": "res://remake/signs/flags.png", "flag_px": [FW, FH], "cols": 10, "size": [FW * 10, FH * 10],
                    "provisional": True, "islands": flags_idx}
    idx["banners"] = {"length_m": 300, "islands": ban_idx}
    json.dump(idx, open(sp, "w"), indent=1, ensure_ascii=False)
    # contact sheets
    bg = Image.new("RGB", atlas.size, (120, 124, 130))
    bg.paste(atlas, (0, 0), atlas)
    bg.resize((atlas.width * 2, atlas.height * 2), Image.NEAREST).save(os.path.join(IMG, "flags.jpg"), quality=88)
    for part in range(4):
        sub = contact_b[part * 25:(part + 1) * 25]
        cs = Image.new("RGB", (BW * 4 * 13 + 12 * 8, BH * 2 + 8), (40, 42, 48))
        for k, s in enumerate(sub):
            x, y = (k % 13) * (BW * 4 + 8), (k // 13) * (BH + 8)
            cs.paste(s, (x, y), s)
        cs.resize((cs.width // 2, cs.height // 2), Image.LANCZOS).save(os.path.join(IMG, "banners_%d.jpg" % part), quality=80)
    idx["banner_atlas"] = pack_banner_atlases([it["id"] for it in isl])
    json.dump(idx, open(sp, "w"), indent=1, ensure_ascii=False)
    write_doc(doc)
    tot = sum(os.path.getsize(os.path.join(BOUT, f)) for f in os.listdir(BOUT))
    print("flags: 100 -> %s (%d KB); banners: 400 in 100 strips, %d KB" % (
        os.path.relpath(os.path.join(OUT, "flags.png"), ROOT), os.path.getsize(os.path.join(OUT, "flags.png")) // 1024, tot // 1024))


def pack_banner_atlases(ids, cols=32):
    """For SkyBanners (one material for the whole sky): two grid atlases of 64 x 1024 cells, 32 a row.
    banners_a holds every island's name (cell 2i) and wares (2i + 1) banners; banners_b its flag streamer (2i) and
    clan (2i + 1) banners, so an island's cells are the same in both.  Emit atlases at half resolution."""
    n = len(ids) * 2
    rows = (n + cols - 1) // cols
    out = {"cell_px": [BW, BH], "grid": [cols, rows], "length_m": 300, "islands": {}}
    for part, ks in (("a", (0, 1)), ("b", (2, 3))):
        A = Image.new("RGBA", (cols * BW, rows * BH), (0, 0, 0, 0))
        E = Image.new("L", (cols * BW // 2, rows * BH // 2), 0)
        for i, iid in enumerate(ids):
            strip = Image.open(os.path.join(BOUT, iid + ".png")).convert("RGBA")
            es = Image.open(os.path.join(BOUT, iid + "_emit.png")).convert("L")
            for j, k in enumerate(ks):
                c = 2 * i + j
                x, y = (c % cols) * BW, (c // cols) * BH
                A.paste(strip.crop((k * BW, 0, (k + 1) * BW, BH)), (x, y))
                E.paste(es.crop((k * BW // 2, 0, (k + 1) * BW // 2, BH // 2)), (x // 2, y // 2))
        A.quantize(256, method=Image.Quantize.FASTOCTREE).save(os.path.join(OUT, "banners_%s.png" % part), optimize=True)
        E.save(os.path.join(OUT, "banners_%s_emit.png" % part), optimize=True)
        out["png_" + part] = "res://remake/signs/banners_%s.png" % part
        out["emit_" + part] = "res://remake/signs/banners_%s_emit.png" % part
    for i, iid in enumerate(ids):
        out["islands"][iid] = {"index": i, "name": 2 * i, "wares": 2 * i + 1, "flag_streamer": 2 * i, "clan": 2 * i + 1,
                               "atlas": {"name": "a", "wares": "a", "flag_streamer": "b", "clan": "b"}}
    return out


def write_doc(doc):
    L = ["# Island flags (PROVISIONAL)", "",
         "One flag per sky island, made by `tools/signs/make_flags.py` from the canon (`remake/bible/sky_islands.json`).",
         "**Provisional** until the political work: the designs are invented here and may change.", "",
         "## The grammar", "",
         "Real vexillology rules (simple enough to draw from memory, 2-3 colours, one emblem, readable at a distance, no",
         "lettering, distinctive), and no copy of any real national flag.", "",
         "- **The forked fly** (a swallowtail cut into the fly) is on every Skein flag: the confederation's shared mark,",
         "  \"flown like a skein of geese\". It is also what makes them read as sky flags from the floor.",
         "- **The field layout is the island's governance:**"]
    for g, (lay, m) in GOV.items():
        L.append("  - %s" % m)
    L += ["- **The colours are the clan's**, its three colours (bible `clans[].colors`), the two most contrasting as the",
          "  field and the third as the device or fimbriation.",
          "- **The emblem is the island's specialty**, what it makes and trades, in whichever colour contrasts best:",
          "  " + ", ".join("%s %s" % (k, v.replace("_", " ")) for k, v in SPECIALTY_EMBLEM.items()) + ".",
          "- **The mix (the user, 2026-10-16):** an island's people and its architecture often differ (Ithaca: Black",
          "  Anglo people in a Maghrebi medina), \"it shows how cultures mixed\". So the **upper fly carries the warren",
          "  culture's motif** (the architecture's ornament: " + ", ".join("%s %s" % (GROUP_NAME[g], m.replace("_", " ")) for g, m in WARREN_MOTIF.items()) + ")",
          "  **in the heritage's colour** (an invented accent per heritage, e.g. black_anglo green, hispanic gold). On the",
          "  banners the name and wares banners letter in the warren culture's manner, the clan banner in the heritage's.",
          "- Emblem art: Grok silhouette sheets `reference/grok/signs/E1`, `E2` (also governance, faith and landmark",
          "  motifs, kept for later charges).", "",
          "Atlas: `godot_project/remake/signs/flags.png`, 10 x 10 flags of 128 x 80 px, alpha in the fork; index in",
          "`signs.json` `flags.islands`.", "",
          "## Banners", "",
          "Four 64 x 1024 banners per island (`remake/signs/sky/banners/SKY-xxx.png`, side by side; `_emit.png` the night",
          "mask): **0** the island's name in its cultural group's lettering, **1** its wares (pictograms and words from the",
          "canon trades), **2** a streamer of the flag's colours with the emblem, **3** the clan. Caps, tails and borders",
          "are Grok blanks per cultural group (`BN1`, `BN2`); East Asian groups stack their letters. Made to trail about",
          "300 m below the island (the runtime request is in `research/sky_islands/warrens/runtime_requests.md`).", "",
          "## The flags", "",
          "| island | clan | governance -> layout | colours | emblem (specialty) | architecture (motif) | people (colour) |", "|---|---|---|---|---|---|---|"]
    for it, m, grp in doc:
        L.append("| %s %s | %s | %s -> %s | %s | %s (%s) | %s: %s (%s) | %s (%s) |" % (
            it["id"], it["name"], it.get("clan", ""), it["governance"], m["layout"], " ".join(m["colours"]),
            m["emblem"].replace("_", " "), it["specialty"], it["warren"], GROUP_NAME.get(grp, grp),
            (m.get("warren_motif") or "").replace("_", " "), it.get("heritage"), m.get("motif_colour")))
    L += ["", "Each row reads as a sentence: *the Helm of Halyard's McFadden kin, flying a prow on the clan's plum and",
          "rose, with the brokers' scale*. The meaning of every element is fixed by the grammar above, so a floor child",
          "who knows the rules can read any island's flag."]
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    open(DOC, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
