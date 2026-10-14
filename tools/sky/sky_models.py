"""sky_models.py -- the style models (tools/sky/style_models.py -> remake/catalog/SKY-<style>-NN.json, built by
remake/blender/gen/sky.py) as make_islands.py lays them out: which model serves which use, their sizes, the lark
cradles on their roofs, their anchors (remake/sky_anchors/<ID>.json: the generator's sign and light anchors), the
shops' names, and the warrens' links (skybridges, planks, covered alleys) between neighbouring buildings.
"""
import glob
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CAT = os.path.join(ROOT, "remake", "catalog")
ANCH = os.path.join(ROOT, "remake", "sky_anchors")
STYLES = os.path.join(ROOT, "godot_project", "remake", "sky", "styles.json")

MODELS = []
for _f in sorted(glob.glob(os.path.join(CAT, "SKY-*-0[0-9].json"))):
    if os.path.basename(_f).startswith("SKY-M-"):
        continue
    MODELS.append(json.load(open(_f)))
MODEL = {m["id"]: m for m in MODELS}
BY_STYLE = {}
for _m in MODELS:
    BY_STYLE.setdefault(_m["traits"]["style"], []).append(_m)
STYLE = json.load(open(STYLES))["styles"] if os.path.exists(STYLES) else {}

# an island's use -> the model types that serve it (gen/sky.py's five per style)
USE_MODELS = {"dwelling": ("home", "tall"), "hall": ("landmark",), "infirmary": ("row", "home"), "school": ("hall",),
              "market": ("hall",), "gasworks": ("hall",), "envelope_loft": ("hall",), "ropewalk": ("hall", "row"),
              "workshop": ("row",), "shops": ("row",)}
WARREN = ("warren", "accretion", "self_built_stack", "vertical_village", "module_stack", "hill_stack", "terrace_stack",
          "alley_cluster", "tong_lau", "zakkyo")


def anchors(mid):
    p = os.path.join(ANCH, mid + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def serves(m, use):
    return m["sky"]["model"] in USE_MODELS.get(use, ("home",))


def dims(m):
    """(lot w, lot d, height to the parapet top, main storeys)"""
    tr = m["traits"]
    sh = tr.get("storey_h", 3.2)
    top = max(0.3 + b["storeys"] * sh for b in tr["blocks"])
    return m["lot"]["w"], m["lot"]["d"], top + 1.2, tr["blocks"][0]["storeys"]


def roof_top(m):
    tr = m["traits"]
    return 0.3 + tr["blocks"][0]["storeys"] * tr.get("storey_h", 3.2)


def body_color(m):
    h = m["traits"]["colors"]["body"][0].lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def cell_sizes(pool, warren):
    """the island's cells, sized to its models' lots (either way round) -- tight for the warrens.  Mostly the homes'
    (they fill the island); none smaller than the smallest home, so every cell can take one"""
    pad = 0.4 if warren else 1.0
    homes = [m for m in pool if m["sky"]["model"] in ("home", "tall")] or pool
    lo = min(min(m["lot"]["w"], m["lot"]["d"]) for m in homes) + pad
    dims = [v for m in pool for v in (m["lot"]["w"], m["lot"]["d"])]
    xs = sorted({round(v + pad, 1) for v in dims if v + pad >= lo})
    # (the homes' own sizes twice over: most cells are theirs)
    xs += sorted({round(v + pad, 1) for m in homes for v in (m["lot"]["w"], m["lot"]["d"])})
    return xs, xs


def is_warren(style_id):
    st = STYLE.get(style_id, {})
    return st.get("typology") in WARREN or st.get("massing", {}).get("stack") in ("pile", "overhang")


def to_world(b, x, z):
    """a point in a model's Godot frame (x, z) -> the island's, for placed building b (x, z, yaw)"""
    c, s = math.cos(b["yaw"]), math.sin(b["yaw"])
    return b["x"] + x * c + z * s, b["z"] - x * s + z * c


def pad_of(b, m):
    """the lark cradle on b's roof: (x, y, z) in the island's frame, or None"""
    a = anchors(m["id"])
    if not a or not a.get("pad"):
        return None
    x, y, z = a["pad"]
    wx, wz = to_world(b, x, z)
    return round(wx, 2), round(b["y"] + y, 2), round(wz, 2)


def blocks_world(b, m):
    """the model's blocks placed: [(x0, z0, x1, z1, top y, storeys)] in the island's frame (axis-aligned: yaws are
    quarter turns)"""
    a = anchors(m["id"])
    out = []
    blocks = a["blocks"] if a and a.get("blocks") else [[*bd["rect"], 0.3 + bd["storeys"] * m["traits"].get("storey_h", 3.2),
                                                        bd["storeys"]] for bd in m["traits"]["blocks"]]
    for x0, y0, x1, y1, top, n in blocks:
        pts = [to_world(b, x, -y) for x, y in ((x0, y0), (x1, y1))]
        out.append((min(pts[0][0], pts[1][0]), min(pts[0][1], pts[1][1]), max(pts[0][0], pts[1][0]),
                    max(pts[0][1], pts[1][1]), b["y"] + top, n))
    return out


# ------------------------------------------------------------------ shop names (b_signs_and_light.md, section 4)
ADJ = ["Light", "Weighed", "Honest", "High", "Cold", "Quiet", "Last", "First", "Lucky", "Lashed", "Drifting", "Patched",
       "Silver", "Warm", "White", "Westward"]
THING = ["Kettle", "Kilo", "Knot", "Line", "Hook", "Skybox", "Lark", "Bell", "Envelope", "Cloud", "Snow", "Gust", "Drift",
         "Raft", "Rim", "Plumb", "Hoist", "Winch", "Gansey", "Mitten", "Hive", "Dove", "Goat"]
KNOTS = ["Bowline", "Hitch", "Sheet Bend", "Clove", "Reef", "Halyard", "Sheepshank", "Carrick", "Figure Eight"]
OWNERS = ["Ama", "Old Petra", "Ines", "Tomas", "Bel", "Kofi", "Yusuf", "Mei", "Ravi", "Noor", "Oskar", "Lupe", "Aiko",
          "Dov", "Marta", "Jun", "Femi", "Zara", "Hal", "Wren"]
PUNS = ["Weigh More", "Heavier Than You'd Think", "Ground Floor", "The Lightening Rod", "Knot Bad", "Hitch & Brew",
        "Gust Come In", "Lift & Shift", "The Snow Must Go On", "Mind the Edge", "Bee Line", "Cloud Nine Teas",
        "Three Days Lashed", "The Knives", "Heavies Welcome", "Light Fingers", "Rim Shots", "Up & Away", "The Plumb Line",
        "Kilo for Kilo", "Dove Tales", "Fan Club", "Mitten Kitten", "Hot Can Machine", "Long Drop Funerals"]
GOODS = {"cafe": "Teas", "restaurant": "Eating House", "diner": "Kitchen", "bakery": "Bakery", "bar": "Bar",
         "wine_bar": "Berry Wine", "brewpub": "Cold Beer", "clothing": "Ganseys", "dry_goods": "Cloth", "jeweler": "Silver",
         "grocery": "Stores", "fish_market": "Perch & Crayfish", "butcher": "Air-Cured Goat", "hardware": "Chandlery",
         "print_shop": "Charts", "bookstore": "Copied Books", "music_store": "Bells & Fiddles", "florist": "Moss & Fern",
         "drug_store": "Remedies", "barber": "Barber", "shoe_store": "Boots", "art_gallery": "Pictures", "games": "Arcade",
         "tattoo": "Ink", "pet": "Doves", "souvenir": "Keepsakes", "food": "Noodles", "pizza": "Pies", "ice_cream": "Snow Cream",
         "machine_floor": "Works", "tavern_hotel": "Inn", "appliance_repair": "Cells & Boards", "shoe_repair": "Cobbler",
         "marina_store": "Lark Parts", "stockroom": "Warehouse", "council": "Hall", "cafeteria": "Long Kitchen"}


def _h(*p):
    return int(hashlib.sha1("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def shop_name(bid, i, kind, island):
    h = _h(bid, i, kind)
    goods = GOODS.get(kind, "Goods")
    t = h % 7
    if t == 0:
        return f"{OWNERS[(h >> 3) % len(OWNERS)]}'s {goods}"
    if t == 1:
        return f"The {ADJ[(h >> 3) % len(ADJ)]} {THING[(h >> 7) % len(THING)]}"
    if t == 2:
        return f"{KNOTS[(h >> 3) % len(KNOTS)]} & {KNOTS[(h >> 7) % len(KNOTS)]}"
    if t == 3:
        return PUNS[(h >> 3) % len(PUNS)]
    if t == 4:
        n = ["Two", "Three", "Seven", "Ten", "Hundred"][(h >> 3) % 5]
        return f"{n} {THING[(h >> 7) % len(THING)]}s"
    if t == 5:
        return f"{island} {goods} House"
    return f"{ADJ[(h >> 3) % len(ADJ)]} {goods}"


def shops_of(b, m, island):
    a = anchors(m["id"])
    out = []
    for i, s in enumerate((a or {}).get("shops", [])):
        out.append({"name": shop_name(b["id"], i, s["kind"], island), "kind": s["kind"]})
    return out


# ------------------------------------------------------------------ the warrens' links
def links(bout, style_id, rnd):
    """skybridges, planks and covered alleys between neighbouring buildings' blocks facing each other across a lane:
    [{a, b, kind, from, to, width}] (island frame; y the height).  Warrens get many, others a few."""
    warren = is_warren(style_id)
    want = 0.6 if warren else 0.12
    blocks = [(b["id"], bw) for b in bout for bw in b["_blocks"]]
    out = []
    seen = set()
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            ida, A = blocks[i]
            idb, B = blocks[j]
            if ida == idb or (ida, idb) in seen:
                continue
            # facing across x (A's east to B's west, or the reverse) or across z
            for axis in (0, 1):
                lo_a, hi_a = (A[0], A[2]) if axis == 0 else (A[1], A[3])
                lo_b, hi_b = (B[0], B[2]) if axis == 0 else (B[1], B[3])
                o0 = max(A[1], B[1]) if axis == 0 else max(A[0], B[0])
                o1 = min(A[3], B[3]) if axis == 0 else min(A[2], B[2])
                if o1 - o0 < 3.0:
                    continue
                gap = lo_b - hi_a if lo_b >= hi_a else (lo_a - hi_b if lo_a >= hi_b else -1)
                if not (1.8 <= gap <= 9.0):
                    continue
                if rnd.random() > want:
                    continue
                ea = hi_a if lo_b >= hi_a else lo_a
                eb = lo_b if lo_b >= hi_a else hi_b
                mid = (o0 + o1) / 2 + rnd.uniform(-1.0, 1.0) * max(0.0, (o1 - o0) / 2 - 2.0)
                ya, yb = A[4], B[4]
                if abs(ya - yb) <= 3.2:
                    kind = "skybridge" if warren and rnd.random() < 0.5 else "plank"
                    h0, h1 = ya, yb
                else:
                    # between the two at a floor both have: a covered alley bridging the lane (Ghadames, Fez, Venice)
                    n = min(A[5], B[5])
                    if n < 2:
                        continue
                    k = 1 + rnd.randrange(max(1, n - 1))
                    base = max(ya - A[5] * 3.2, yb - B[5] * 3.2)        # (each block's ground floor level, + 0.3)
                    h0 = h1 = base + k * 3.2 + 0.05
                    kind = "covered_alley"
                pa = (ea, mid) if axis == 0 else (mid, ea)
                pb = (eb, mid) if axis == 0 else (mid, eb)
                out.append({"a": ida, "b": idb, "kind": kind, "from": [round(pa[0], 2), round(h0, 2), round(pa[1], 2)],
                            "to": [round(pb[0], 2), round(h1, 2), round(pb[1], 2)],
                            "width": 0.9 if kind == "plank" else (2.4 if kind == "covered_alley" else 1.8)})
                seen.add((ida, idb))
                break
    return out
