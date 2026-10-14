"""models.py -- the sky islands' building models (research/sky_islands/00_plan.md).

The user, 2026-10-14: "The structures on the islands will be tall flat topped buildings ... The buildings can use the
shared parts. There is no need to make very much new ... The buildings on the islands will all have roof access ...
We are going to use all the tricks we've learned to reduce the footprint of this addition."

So the islands' ~3,000 buildings are placed copies of a small library of models (SKY-M-NN), each an ordinary catalog
record built by the normal pipeline from the shared kit (tools/build_library.py --ids; SSC_KIT=1): walk-up apartment
blocks (gen/coastal.py condo), office-block bodies with a ground floor fitted for the island's trades and halls
(gen/store.py office_block), and works (gen/works.py industrial) for the gas works and envelope lofts.  Every one has
traits.roof_access (gen/roofaccess.py: an iron fire escape to a platform over a raised parapet).

Each model's lot (w across its front, d deep) includes its fire escape and a passage; its front (the door side) is the
lot's +d edge.  write() writes remake/catalog/SKY-M-NN.json.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAT = os.path.join(ROOT, "remake", "catalog")

# body colours of the islands' render: limewash, sky-faded ochre, slate, rust, sea-green, plum (cold-climate paint)
BODIES = ["#e9e3d6", "#d8a95b", "#7d8c99", "#a5553a", "#6f9a8b", "#7f5a6e", "#c9b79c", "#4f6273"]
ACCENTS = ["#2b4a6b", "#8a2f2a", "#2f5b3c", "#c78a22", "#3a3a48", "#6b3b5c"]

# condo lots: W = w - 4, D = d - 7 (gen/coastal.build_apartments); the fire escape climbs the rear wall
CONDO = {"S": (22.0, 21.0), "M": (30.0, 23.0), "L": (40.0, 24.0)}
# office-block lots: W = w - 4.6, D = d - 3.5 (gen/store.build with roof_access); the escape climbs a side wall
BLOCK = {"S": (22.0, 20.0), "L": (30.0, 24.0), "XL": (40.0, 28.0)}
WORKS = (34.0, 30.0)                 # W = w - 6, D = d - 8 (gen/works.build_works); escape on the +x wall
WORKS_S = (22.0, 23.0)               # (the small islands' gas works and lofts)

# use -> ground-floor storefronts (shopfit recipes) and signs
FRONTS = {
    "workshop": [("machine_floor", "WORKSHOP"), ("hardware", "CHANDLERY")],
    "market": [("grocery", "MARKET"), ("butcher", "LARDER"), ("bakery", "BAKERY")],
    "hall": [("council", "CLAN HALL"), ("library", "LOG ROOM")],
    "school": [("classroom", "SCHOOL"), ("classroom", "SCHOOL")],
    "infirmary": [("ward", "INFIRMARY"), ("nurse_station", "INFIRMARY")],
    "shops": [("cafe", "TEA ROOM"), ("clothing", "WOOLLENS"), ("bakery", "BAKERY")],
}


def _models():
    out = []
    n = 0

    def add(kind, use, size, storeys, lot, traits, fronts=None, name=""):
        nonlocal n
        n += 1
        mid = "SKY-M-%02d" % n
        tr = dict(storeys=storeys, roof_access="fire_escape", condition="kept", year_built=2700,
                  colors={"body": BODIES[n % len(BODIES)], "accent": ACCENTS[n % len(ACCENTS)], "trim": "#efeae0"})
        tr.update(traits)
        if fronts:
            tr["storefronts"] = [{"business": s.title(), "type": t, "sign": s, "sign_style": "flat_board"} for t, s in fronts]
        if kind == "condo":
            homes = traits["units"]
        elif kind == "store" and traits.get("upper_use") == "apartments":
            homes = (storeys - 1) * max(1, int((lot[0] - 4.6 - 2.75) / 5.0))
        else:
            homes = 0
        out.append({"id": mid, "settlement": "Sky islands", "generated": "tools/sky/models.py", "kind": kind,
                    "lot": {"w": lot[0], "d": lot[1]}, "traits": tr, "names": {"name": name},
                    "sky": {"use": use, "size": size, "storeys": storeys, "homes": homes},
                    "brief": f"sky island {use} ({size}, {storeys} storeys): a shared model"})

    # dwellings: walk-up apartment blocks, two colourings of each form
    # (one of each form: a second colouring of the same block would double its whole mesh -- the game tints an island's
    # stucco to the clan's colours instead; brick on every third form for a change of texture)
    v_ = 0
    for size, storeys_list in (("S", (5, 6, 7)), ("M", (5, 6, 7, 8)), ("L", (4, 6, 8))):
        for st in storeys_list:
            v_ += 1
            for v in ((1,) if v_ % 3 == 0 else (0,)):
                w, d = CONDO[size]
                units = max(4, int((w - 4) / 5.5) * 2 * st)
                add("condo", "dwelling", size, st, (w, d),
                    {"form": "slab", "units": units, "balconies": "none", "ground_floor": "apartments",
                     "walls": "stucco" if v == 0 else "brick", "roof": {"type": "flat"}})
    # trades and halls: office-block bodies, the ground floor fitted for the use
    for use, size, st in (("hall", "S", 5), ("infirmary", "S", 4), ("school", "S", 4), ("workshop", "S", 5), ("workshop", "L", 4), ("workshop", "L", 6), ("market", "S", 4),
                          ("market", "L", 5), ("hall", "L", 6), ("hall", "XL", 5), ("school", "XL", 4), ("school", "L", 5),
                          ("infirmary", "L", 5), ("infirmary", "XL", 6), ("shops", "S", 6), ("shops", "L", 7)):
        upper = {"hall": "offices", "school": "offices", "infirmary": "hotel_rooms"}.get(use, "apartments")
        if size == "S":
            upper = "apartments"           # (the small islands' halls, schools and infirmaries have homes upstairs)
        add("store", use, size, st, BLOCK[size],
            {"form": "office_block", "upper_use": upper, "facade": "stucco", "cornice": "parapet_stepped"},
            fronts=FRONTS[use])
    # works: the gas works (a tank on the roof) and the envelope lofts (a roof monitor)
    for use, size, st, comps in (("gasworks", "W", 4, ["tank"]), ("envelope_loft", "W", 5, ["monitor"]), ("ropewalk", "W", 4, []),
                                 ("gasworks", "WS", 4, ["tank"]), ("envelope_loft", "WS", 4, ["monitor"])):
        add("industrial", use, size, st, WORKS if size == "W" else WORKS_S,
            {"use": "machine_shop", "walls": "brick", "components": comps},
            name={"gasworks": "GAS WORKS", "envelope_loft": "ENVELOPE LOFT", "ropewalk": "ROPE WALK"}[use])
    return out


MODELS = _models()


def write():
    for m in MODELS:
        with open(os.path.join(CAT, m["id"] + ".json"), "w") as f:
            json.dump(m, f, indent=1)
    return [m["id"] for m in MODELS]


if __name__ == "__main__":
    ids = write()
    print(len(ids), "models:", " ".join(ids))
