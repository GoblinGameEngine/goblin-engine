"""
institution.py -- catalog records of kind 'civic', 'school' and 'church' -> Building.

Plans (x across the lot, +y = street, origin at the lot centre):
  * CORRIDOR plan (city/town hall, courthouse, hospital, school, fire/police): a lobby behind the
    centre front door opens onto a 2.4 m corridor along x; rooms fill a front band and a rear
    band; straight stairs lie along the corridor's rear edge near both ends (passage 1.3 m beside
    them) with 0.9 m landings.  Big rooms (courtroom, council, auditorium, gym, cafeteria, fire
    bays) take whole bands or wings.
  * HALL plan (library, post office, depot, opera house ground floor, church): one or two big rooms
    with small rooms at the back.
"""
import math

from common import (Palette, WALL_TEX, brick_for, clamp, hexcol, lib_building, rng, std_materials, darken, g, FONT_SANS,
                    FONT_SERIF, sign_board)
import gbhouse as gh
import shopfit

TE, TI = 0.35, 0.15
COR_W = 2.4
STAIR_W = 1.1


def materials(b, tr):
    pal = Palette(b)
    col = tr.get("colors", {}) or {}
    body = col.get("body") or "#9a5a42"
    std_materials(pal, trim=col.get("trim") or "#e9e4d6", door=col.get("accent") or "#3a2a1e")
    shopfit.shop_materials(pal)
    walls = tr.get("walls", "brick")
    tex = WALL_TEX.get(walls, "brick_red")
    if walls == "brick":
        tex = brick_for(hexcol(body))
    pal.surf("ext", tex, hexcol(body), rough=0.85)
    pal.surf("stone", "limestone", rough=0.85)
    pal.surf("roof", "roof_slate" if (tr.get("roof") or {}).get("material") == "slate" else "roof_asphalt",
             hexcol(col.get("roof") or "#5a5a58"), rough=0.85)
    pal.surf("roof_m", "concrete", rough=0.95)
    pal.surf("floor", "terrazzo" if tr.get("year_built", tr.get("era", 1920)) > 1925 else "floor_oak", rough=0.4)
    pal.surf("plaster", "plaster", "#eee8da", rough=0.85)
    pal.surf("ceiling", "acoustic" if tr.get("year_built", tr.get("era", 1920)) > 1940 else "plaster", rough=0.8)
    pal.surf("found", "limestone", rough=0.9)
    pal.solid("roof_under", (0.5, 0.5, 0.48), rough=0.8)
    pal.solid("copper", (0.35, 0.55, 0.45), rough=0.5, metal=0.3)
    pal.solid("sign_board", hexcol(col.get("accent") or "#1e2a3a"), rough=0.5)
    pal.solid("gold", (0.8, 0.62, 0.22), rough=0.3, metal=0.9)
    pal.solid("bell", (0.55, 0.42, 0.2), rough=0.3, metal=1.0)
    pal.solid("flag_red", (0.7, 0.08, 0.1), rough=0.8)
    pal.solid("stained", (0.45, 0.2, 0.55), rough=0.2, alpha=0.6)
    return pal


# ------------------------------------------------------------------ plans
def corridor_plan(spec, rect, floors, bands, rnd, stairs=True):
    """bands[k] = (front_rooms, rear_rooms) for floor k; each a list of (weight, room_type, recipe).
    Returns the corridor y range and the lobby x range."""
    x0, y0, x1, y1 = rect
    cy = (y0 + y1) / 2 - 0.5
    c0, c1 = cy - COR_W / 2, cy + COR_W / 2
    rooms, doors = spec["rooms"], spec["doors"]
    L = x1 - x0
    lob_w = 4.0
    lx0, lx1 = -lob_w / 2, lob_w / 2
    stair_spans = []
    if stairs and len(floors) > 1:
        for k in range(1, len(floors)):
            rise = floors[k][0] - floors[k - 1][0]
            n = math.ceil(rise / 0.18)
            run = 0.27
            Ls = n * run
            for end in (0, 1):
                if end == 0:
                    st = dict(start=(x0 + TE + 1.0, c0 + 0.05), dir=(1, 0), width=STAIR_W, n=n, run=run, floor=k - 1, to_floor=k,
                              rail_side="left")
                    span = (x0 + TE + 0.1, x0 + TE + 1.0 + Ls + 1.0)
                else:
                    st = dict(start=(x1 - TE - 1.0, c0 + 0.05 + STAIR_W), dir=(-1, 0), width=STAIR_W, n=n, run=run, floor=k - 1,
                              to_floor=k, rail_side="right")
                    span = (x1 - TE - 1.0 - Ls - 1.0, x1 - TE - 0.1)
                spec["stairs"].append(st)
                stair_spans.append((k - 1, span))
                stair_spans.append((k, span))
    for k, (front, rear) in enumerate(bands):
        rooms.append(dict(name=f"COR{k}", floor=k, rect=(x0, c0, x1, c1), type=None, no_light=False, no_furnish=True))
        spans_here = [sp for (fk, sp) in stair_spans if fk == k]
        for band, (b0, b1), rlist in (("F", (c1, y1), front), ("R", (y0, c0), rear)):
            if not rlist:
                continue
            if k == 0 and band == "F":
                # the lobby behind the main door splits the ground-floor front band
                segs = [(x0, lx0), (lx1, x1)]
                rooms.append(dict(name="LOBBY", floor=0, rect=(lx0, c1, lx1, y1), type="lobby", open_plan_to=f"COR{k}",
                                  fitout=shopfit.fitout_for("lobby", rnd)))
            else:
                segs = [(x0, x1)]
            dy = c1 if band == "F" else c0
            for si, (sa, sb) in enumerate(segs):
                items = rlist[si::len(segs)] or [(1.0, "office", "office")]
                tot = sum(w for w, _, _ in items)
                cuts = [sa]
                for (w, _, _) in items:
                    cuts.append(cuts[-1] + (sb - sa) * w / tot)
                slots = [[cuts[i], cuts[i + 1], items[i]] for i in range(len(items))]
                # a rear-band slot whose whole corridor wall lies behind a stair can't have a door:
                # fold it into its neighbour (the stair occupies the corridor's rear edge there)
                merged = []
                for sl in slots:
                    ok = [x for x in (sl[0] + 0.7, (sl[0] + sl[1]) / 2, sl[1] - 0.7)
                          if band == "F" or not any(s0 - 0.6 < x < s1 + 0.6 for (s0, s1) in spans_here)]
                    if not ok and merged:
                        merged[-1][1] = sl[1]
                    else:
                        merged.append(sl)
                if len(merged) > 1 and band == "R":
                    first = merged[0]
                    if not [x for x in (first[0] + 0.7, (first[0] + first[1]) / 2, first[1] - 0.7)
                            if not any(s0 - 0.6 < x < s1 + 0.6 for (s0, s1) in spans_here)]:
                        merged[1][0] = first[0]
                        merged = merged[1:]
                for ri, (ra, rb, (w, rtype, recipe)) in enumerate(merged):
                    name = f"R{k}{band}{si}_{ri}"
                    room = dict(name=name, floor=k, rect=(ra, b0, rb, b1), type=rtype, entry="S" if band == "F" else "N")
                    if recipe:
                        room["fitout"] = shopfit.fitout_for(recipe, rnd)
                    rooms.append(room)
                    cands = [x for x in ((ra + rb) / 2, ra + 0.9, rb - 0.9)
                             if ra + 0.6 < x < rb - 0.6 and (band == "F" or not any(s0 - 0.6 < x < s1 + 0.6 for (s0, s1) in spans_here))]
                    if not cands:
                        continue
                    wide = (rb - ra) >= 6.0
                    doors.append(dict(name=f"d{name}", floor=k, at=(cands[0], dy), w=1.6 if wide else 0.95, leaves=2 if wide else 1,
                                      swing_into=name))
    return (c0, c1), (lx0, lx1)


def windows_all(spec, rect, floors, avoid, sill=0.9, h=2.2, spacing=2.6, arched=False, rear=True):
    x0, y0, x1, y1 = rect
    for k, (fz, cz) in enumerate(floors):
        for (a, c) in (((x1, y1), (x0, y1)), ((x0, y0), (x1, y0)), ((x0, y1), (x0, y0)), ((x1, y0), (x1, y1))):
            if not rear and a[1] == y0 and c[1] == y0:
                continue
            Lw = math.dist(a, c)
            n = max(1, int((Lw - 1.0) / spacing))
            for j in range(n):
                t = (j + 0.5) / n
                p = (a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
                if any(math.dist(p, q) < 1.5 for (q, fk) in avoid if fk == k):
                    continue
                spec["windows"].append(dict(at=p, floor=k, w=1.0, sill=sill, h=min(h, cz - fz - sill - 0.25), kind="dh", cols=2,
                                            head_cap=True))


def add_stoops(spec, FL, skip=("main_entry",)):
    """A landing with steps down to grade outside every exterior door but the main entrance (whose
    steps are part of the facade); the door sits FL above the ground."""
    if FL < 0.2:
        return
    for d in spec["doors"]:
        if not d.get("ext") or d["name"] in skip:
            continue
        x, y = d["at"]
        bl = [b_ for b_ in spec["blocks"] if b_["rect"][0] - 0.01 <= x <= b_["rect"][2] + 0.01 and b_["rect"][1] - 0.01 <= y <= b_["rect"][3] + 0.01]
        if not bl:
            continue
        bx0, by0, bx1, by1 = bl[0]["rect"]
        dist = {(-1, 0): abs(x - bx0), (1, 0): abs(x - bx1), (0, -1): abs(y - by0), (0, 1): abs(y - by1)}
        ox, oy = min(dist, key=dist.get)
        hw = d["w"] / 2 + 0.4
        if ox:
            rect = (min(x, x + ox * 1.2), y - hw, max(x, x + ox * 1.2), y + hw)
            at = (x + ox * 1.2, y)
        else:
            rect = (x - hw, min(y, y + oy * 1.2), x + hw, max(y, y + oy * 1.2))
            at = (x, y + oy * 1.2)
        spec["porches"].append(dict(rect=rect, z=FL - 0.02, post_top=FL, posts=[], beam=False, skirt_mat="stone",
                                    steps=dict(at=at, dir=(ox, oy), width=d["w"] + 0.6, mat="stone")))


# ------------------------------------------------------------------ uses
def program(kind, use, storeys, W, D):
    """(bands per floor, big wing or None).  Each band list item: (weight, room type, recipe)."""
    off = (1.0, "office", "office")
    if kind == "school":
        cls = (1.3, "classroom", "classroom")
        bands = [([cls, (0.8, "office", "office"), cls], [cls, (1.0, "bath", None), cls, cls])]
        for _ in range(1, storeys):
            bands.append(([cls, cls, cls], [cls, (1.0, "bath", None), cls]))
        return bands, ("gym", "gym")
    if use in ("city_hall", "town_hall"):
        bands = [([off, off, off], [off, (1.0, "bath", None), off])]
        if storeys > 1:
            bands.append(([(3.0, "council", "council")], [off, off, off]))
            return bands, None
        return bands, ("council", "council")
    if use == "courthouse":
        bands = [([off, off, off], [off, (1.0, "bath", None), off, off])]
        for k in range(1, storeys):
            bands.append(([(3.0, "courtroom", "courtroom")], [off, off, (0.8, "bath", None)]) if k == storeys - 1
                         else ([off, off, off], [off, off, off]))
        return bands, None if storeys > 1 else ("courtroom", "courtroom")
    if use == "hospital":
        ward = (1.2, "ward", "ward")
        bands = [([(1.0, "nurse", "nurse_station"), off], [ward, (0.8, "bath", None), ward])]
        for _ in range(1, storeys):
            bands.append(([ward, ward], [ward, (0.8, "bath", None), ward]))
        return bands, None
    if use in ("fire_police", "fire_station", "police"):
        bands = [([off], [(1.0, "jail", "jail"), (0.8, "bath", None), off])]
        for _ in range(1, storeys):
            bands.append(([(1.0, "bed", None), (1.0, "bed", None)], [(1.0, "kitchen", None), (0.8, "bath", None)]))
        return bands, ("fire_bay", "fire_bay")
    if use == "opera_house":
        bands = [([off, off], [off, (0.8, "bath", None)])]
        return bands, ("auditorium", "auditorium")
    return [([off, off], [off, (0.8, "bath", None), off])] + [([off, off], [off, off]) for _ in range(1, storeys)], None


def build(rec):
    rid = rec["id"]
    kind = rec.get("kind", "civic")
    tr = rec.get("traits", {}) or {}
    names = rec.get("names", {}) or {}
    rnd = rng(rid)
    lot = rec.get("lot", {"w": 30.0, "d": 30.0})
    lot_w, lot_d = lot["w"], lot["d"]
    b = lib_building(rid)
    materials(b, tr)
    if kind == "church":
        return build_church(b, rec, tr, names, lot_w, lot_d, rnd)
    use = (tr.get("use") or (rec.get("label") or "office")).lower().replace(" ", "_").replace("/", "_").replace(".", "")
    use = {"fire___police": "fire_police", "post_office": "post_office", "library": "library", "carnegie_library": "library",
           "city_hall": "city_hall", "town_hall": "town_hall", "courthouse": "courthouse", "depot": "depot"}.get(use, use)
    if "courthouse" in use:
        use = "courthouse"
    if "hospital" in use:
        use = "hospital"
    if "library" in use:
        use = "library"
    if "fire" in use or "police" in use:
        use = "fire_police"
    if "opera" in use:
        use = "opera_house"
    storeys = int(clamp(tr.get("storeys") or (2 if kind == "school" else 1), 1, 3))
    year = tr.get("year_built", tr.get("era", 1920))
    style = tr.get("style", "vernacular")
    W = clamp(lot_w - 4.0, 9.0, 60.0)
    D = clamp(lot_d - 6.0, 8.0, 40.0)
    if use in ("post_office", "library", "depot") or (W < 14 and kind != "school"):
        return build_hall(b, rec, tr, names, use, W, D, lot_w, lot_d, storeys, rnd)
    # wing for the big room
    bands, wing = program(kind, use, storeys, W, D)
    wing_d = 0.0
    if wing and D >= 22:
        wing_d = min(14.0, D * 0.42)
    main_d = D - wing_d
    y1 = lot_d / 2 - 3.0
    y0 = y1 - main_d
    x0, x1 = -W / 2, W / 2
    FL = 0.9 if year < 1940 else 0.45
    if use == "fire_police":
        FL = 0.15                       # apparatus bays open at street level
    H = 3.9 if year < 1940 else 3.4
    floors = [(FL, FL + H)]
    for k in range(1, storeys):
        fz = floors[-1][1] + 0.4
        floors.append((fz, fz + H))
    wall_top = floors[-1][1] + 0.35
    flat = style in ("classical_revival", "beaux_arts", "art_deco", "modern") or kind == "school" and year > 1915
    roof = dict(type="flat", thick=0.35, parapet=0.9, coping="stone") if flat else dict(type="hip", pitch=30, eave_oh=0.6, thick=0.2)
    if style == "prairie":
        roof = dict(type="hip", pitch=18, eave_oh=1.2, thick=0.2)
    spec = dict(t_ext=TE, t_int=TI, era="old" if year < 1940 else "modern",
                mats=dict(ext="ext", int="plaster", roof="roof" if not flat else "roof_m", roof_under="roof_under", found="found",
                          floor="floor", ceiling="ceiling", trim="trim", door="door", fascia="trim", porch="stone", post="stone",
                          furn="furniture"),
                blocks=[dict(name="main", rect=(x0, y0, x1, y1), floors=floors, wall_top=wall_top, found_top=FL - 0.05, roof=roof)],
                rooms=[], doors=[], windows=[], stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
    (c0, c1), (lx0, lx1) = corridor_plan(spec, (x0, y0, x1, y1), floors, bands, rnd)
    # front entrance (double doors with transom) + rear exit at each corridor end
    spec["doors"].append(dict(name="main_entry", at=(0.0, y1), w=1.8, h=2.5, ext=True, leaves=2, glazed=(0.12, 0.45, 0.88, 0.92),
                              transom=0.8))
    spec["doors"].append(dict(name="exit_w", at=(x0, (c0 + c1) / 2 + 0.6), w=1.0, ext=True, out=True))
    spec["doors"].append(dict(name="exit_e", at=(x1, (c0 + c1) / 2 + 0.6), w=1.0, ext=True, out=True))
    if wing and wing_d > 0:
        wrect = (x0 + W * 0.2, y0 - wing_d, x1 - W * 0.2, y0)
        spec["blocks"].append(dict(name="wing", rect=wrect, floors=[(FL, FL + max(H, 6.0) - 0.4)], wall_top=FL + max(H, 6.0),
                                   found_top=FL - 0.05, roof=dict(type="flat", thick=0.35, parapet=0.6, coping="stone")))
        spec["rooms"].append(dict(name="BIG", rect=wrect, type=wing[0], fitout=shopfit.fitout_for(wing[1], rnd)))
        # connect through the rear band room in the middle: replace it with a vestibule
        mid = [r for r in spec["rooms"] if r.get("floor", 0) == 0 and r["rect"][3] <= c0 + 0.01 and r["rect"][0] <= 0 <= r["rect"][2]]
        for r in mid:
            spec["rooms"].remove(r)
            spec["doors"] = [d for d in spec["doors"] if d["name"] != f"d{r['name']}"]
            spec["rooms"].append(dict(name="VEST", rect=r["rect"], type=None, open_plan_to="COR0"))
        spec["doors"].append(dict(name="big", at=(0.0, y0), w=1.8, leaves=2, swing_into="BIG"))
        spec["doors"].append(dict(name="big_exit", at=(wrect[2], (wrect[1] + wrect[3]) / 2), w=1.6, ext=True, leaves=2, out=True))
        if wing[0] == "fire_bay":
            for kx in range(2):
                spec["doors"].append(dict(name=f"bay{kx}", at=(wrect[0] + (wrect[2] - wrect[0]) * (0.3 + 0.4 * kx), wrect[1]), w=3.2, h=3.6,
                                          ext=True, leaves=2, out=True, panels=[(0.1, 0.5, 0.9, 0.9), (0.1, 0.08, 0.9, 0.45)]))
    avoid = [(d["at"], d.get("floor", 0)) for d in spec["doors"]]
    windows_all(spec, (x0, y0, x1, y1), floors, avoid)
    add_stoops(spec, FL)
    gh.House(b, spec).build()
    exterior(b, rec, tr, names, (x0, y0, x1, y1), floors, wall_top, flat, style, lot_d, rnd, kind)
    return b


def build_hall(b, rec, tr, names, use, W, D, lot_w, lot_d, storeys, rnd):
    """Post office, library, depot and small civic buildings: big front room, small rooms behind."""
    year = tr.get("year_built", 1920)
    style = tr.get("style", "vernacular")
    W = min(W, 24.0)
    D = min(D, 22.0)
    y1 = lot_d / 2 - 3.0
    y0 = y1 - D
    x0, x1 = -W / 2, W / 2
    FL = 0.9 if year < 1940 else 0.45
    H = 4.2 if year < 1940 else 3.6
    floors = [(FL, FL + H)]
    flat = style in ("classical_revival", "beaux_arts", "art_deco", "modern")
    roof = dict(type="flat", thick=0.35, parapet=0.9, coping="stone") if flat else dict(type="hip", pitch=28, eave_oh=0.6, thick=0.2)
    front_type = {"post_office": ("po_lobby", "po_lobby"), "library": ("library", "library"),
                  "depot": ("waiting_room", "waiting_room")}.get(use, ("office", "office"))
    back_type = {"post_office": ("sorting_room", "sorting_room"), "library": ("office", "office"),
                 "depot": ("stock", "stockroom")}.get(use, ("office", "office"))
    yb = y0 + D * (0.45 if use != "library" else 0.3)
    spec = dict(t_ext=TE, t_int=TI, era="old" if year < 1940 else "modern",
                mats=dict(ext="ext", int="plaster", roof="roof" if not flat else "roof_m", roof_under="roof_under", found="found",
                          floor="floor", ceiling="ceiling", trim="trim", door="door", fascia="trim", porch="stone", post="stone",
                          furn="furniture"),
                blocks=[dict(name="main", rect=(x0, y0, x1, y1), floors=floors, wall_top=FL + H + 0.35, found_top=FL - 0.05, roof=roof)],
                rooms=[dict(name="FRONT", rect=(x0, yb, x1, y1), type=front_type[0], fitout=shopfit.fitout_for(front_type[1], rnd)),
                       dict(name="BACK", rect=(x0, y0, x1 - 3.0, yb), type=back_type[0], fitout=shopfit.fitout_for(back_type[1], rnd)),
                       dict(name="OFF", rect=(x1 - 3.0, y0 + 2.2, x1, yb), type="office", fitout=shopfit.fitout_for("office", rnd)),
                       dict(name="WC", rect=(x1 - 3.0, y0, x1, y0 + 2.2), type="bath", floor_mat="hextile")],
                doors=[dict(name="main_entry", at=(0.0, y1), w=1.8, h=2.5, ext=True, leaves=2, glazed=(0.12, 0.45, 0.88, 0.92),
                            transom=0.8),
                       dict(name="front_back", at=((x0 + x1 - 3.0) / 2, yb), w=0.95, swing_into="BACK"),
                       dict(name="front_off", at=(x1 - 1.5, yb), w=0.9, swing_into="OFF"),
                       dict(name="wc", at=(x1 - 3.0, y0 + 1.1), w=0.75, swing_into="WC"),
                       dict(name="back", at=((x0 + x1 - 3.0) / 2 - 1.5, y0), w=1.6, ext=True, leaves=2, out=True)],
                windows=[], stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
    if use == "post_office":
        spec["doors"][4]["locked"] = True
    avoid = [(d["at"], d.get("floor", 0)) for d in spec["doors"]]
    windows_all(spec, (x0, y0, x1, y1), floors, avoid, spacing=2.8)
    add_stoops(spec, FL)
    gh.House(b, spec).build()
    exterior(b, rec, tr, names, (x0, y0, x1, y1), floors, FL + H + 0.35, flat, style, lot_d, rnd, rec.get("kind", "civic"))
    return b


def exterior(b, rec, tr, names, rect, floors, wall_top, flat, style, lot_d, rnd, kind):
    x0, y0, x1, y1 = rect
    p = b.part("institution_trim-col")
    FL = floors[0][0]
    portico = style in ("classical_revival", "beaux_arts", "greek_revival")
    # front steps up to the entrance: they start at the portico's front edge (its floor is the landing)
    y_st = y1 + (1.9 if portico else 0.0)
    nst = max(1, round(FL / 0.17))
    for k in range(nst):
        z = FL - k * FL / nst
        p.box((-2.2 - k * 0.1, y_st + k * 0.32, 0.0), (2.2 + k * 0.1, y_st + (k + 1) * 0.32, z), "stone")
    # classical portico: columns + pediment over the entrance
    if portico:
        top = floors[-1][1] if len(floors) > 1 else floors[0][1] + 0.3
        for cx in (-2.4, -0.8, 0.8, 2.4):
            g.column(p, cx, y1 + 1.4, FL, top, 0.28, "stone")
        p.box((-3.0, y1, top), (3.0, y1 + 1.9, top + 0.6), "stone")
        p.face([(-3.1, y1 + 1.9, top + 0.6), (3.1, y1 + 1.9, top + 0.6), (0.0, y1 + 1.9, top + 1.8)], "stone")
        p.box((-2.9, y1, 0.0), (2.9, y1 + 1.9, FL), "stone")              # the portico's plinth (landing)
    elif style == "romanesque":
        p.box((-2.2, y1, FL), (-1.6, y1 + 0.5, FL + 3.4), "stone")
        p.box((1.6, y1, FL), (2.2, y1 + 0.5, FL + 3.4), "stone")
        p.box((-2.2, y1, FL + 3.0), (2.2, y1 + 0.5, FL + 3.6), "stone")
    # cupola / clock tower / dome
    dc = tr.get("dome_or_cupola", "none")
    cz = wall_top + (0.9 if flat else 1.6)
    if dc == "cupola":
        p.box((-1.2, (y0 + y1) / 2 - 1.2, cz), (1.2, (y0 + y1) / 2 + 1.2, cz + 2.4), "trim")
        gh.hip_roof(p, -1.4, 1.4, (y0 + y1) / 2 - 1.4, (y0 + y1) / 2 + 1.4, cz + 2.4, 45, 0.1, 0.1, "copper", "trim", "trim")
    elif dc == "clock_tower":
        p.box((-1.8, (y0 + y1) / 2 - 1.8, cz), (1.8, (y0 + y1) / 2 + 1.8, cz + 5.0), "ext")
        p.cylinder((0.0, (y0 + y1) / 2 + 1.82), 0.9, cz + 3.3, cz + 3.35, "white_text", n=20)
        gh.hip_roof(p, -2.0, 2.0, (y0 + y1) / 2 - 2.0, (y0 + y1) / 2 + 2.0, cz + 5.0, 50, 0.15, 0.15, "copper", "trim", "trim")
    elif dc == "dome":
        for k in range(8):
            r = 3.0 * math.cos(k / 8 * math.pi / 2)
            p.cylinder((0.0, (y0 + y1) / 2), r, cz + 3.0 * math.sin(k / 8 * math.pi / 2), cz + 3.0 * math.sin((k + 1) / 8 * math.pi / 2),
                       "copper", n=24)
    # name over the door, plaque, flagpole
    nm = (names.get("name") or rec.get("label") or "").upper()
    frame = (g.Vector((0.0, y1 + 0.02, floors[0][1] - 0.05)), g.Vector((-1, 0, 0)), g.Vector((0, -1, 0)), g.Vector((0, 0, 1)))
    if nm:
        size = clamp(min(8.0, x1 - x0 - 1.0) / max(8, len(nm)) * 1.4, 0.16, 0.4)
        g.text_mesh(b, "sign_name", nm[:40], size, (0.0, y1 + 0.03 + (1.95 if style in ("classical_revival", "beaux_arts", "greek_revival") else 0),
                                                       (floors[-1][1] if len(floors) > 1 else floors[0][1]) + 0.1), math.pi,
                    "stone" if flat else "gold", extrude=0.04, font=FONT_SERIF)
    plaque = names.get("plaque")
    if plaque:
        p.box((2.6, y1, FL + 1.2), (3.4, y1 + 0.04, FL + 1.8), "bell")
        g.text_mesh(b, "sign_plaque", str(plaque)[:26], 0.045, (3.0, y1 + 0.045, FL + 1.55), math.pi, "black_text", extrude=0.002,
                    font=FONT_SERIF)
    if kind in ("civic", "school"):
        fx = x0 + 2.0
        p.cylinder((fx, lot_d / 2 - 1.2), 0.07, 0.0, 9.0, "steel", n=8, r1=0.04)
        p.box((fx + 0.05, lot_d / 2 - 1.22, 7.8), (fx + 1.6, lot_d / 2 - 1.18, 8.8), "flag_red")
    if kind == "school":
        sg = names.get("sign") or nm
        parts = [t.strip() for t in sg.replace("·", "-").split(" - ") if t.strip()]
        mx = x1 - 3.0
        p.box((mx - 1.4, lot_d / 2 - 1.6, 0.0), (mx + 1.4, lot_d / 2 - 1.3, 1.4), "ext")
        for i, t in enumerate(parts[:3]):
            g.text_mesh(b, f"sign_school_{i}", t.upper()[:30], 0.14 if i == 0 else 0.08,
                        (mx, lot_d / 2 - 1.29, 1.05 - i * 0.25), math.pi, "white_text", extrude=0.005, font=FONT_SANS)
    # sidewalk + walk
    w = b.part("walk-col")
    w.box((-1.2, y_st + nst * 0.32, -0.02), (1.2, lot_d / 2, 0.03), "sidewalk", sides="Z")


# ------------------------------------------------------------------ churches
def build_church(b, rec, tr, names, lot_w, lot_d, rnd):
    year = tr.get("year_built", 1900)
    style = tr.get("style", "gothic_revival")
    W = clamp(lot_w - 3.0, 8.0, 16.0)
    D = clamp(lot_d - 5.0, 14.0, 30.0)
    y1 = lot_d / 2 - 3.0
    y0 = y1 - D
    x0, x1 = -W / 2, W / 2
    FL = 0.9
    wall_top = FL + (6.0 if style not in ("modern_a_frame",) else 1.2)
    pitch = (tr.get("roof") or {}).get("pitch_deg") or (52 if style in ("gothic_revival", "carpenter_gothic") else 38)
    narthex = 3.0
    spec = dict(t_ext=0.3, t_int=0.15, era="old" if year < 1940 else "modern",
                mats=dict(ext="ext", int="plaster", roof="roof", roof_under="furn_dark", found="found", floor="floor",
                          ceiling="furn_dark", trim="trim", door="door", fascia="trim", porch="stone", post="stone", furn="furn_dark"),
                blocks=[dict(name="nave", rect=(x0, y0, x1, y1), floors=[(FL, wall_top + 3.0)], wall_top=wall_top, found_top=FL - 0.05,
                             roof=dict(type="gable", ridge="y", pitch=pitch, eave_oh=0.4, rake_oh=0.3, thick=0.2), habitable_attic=True)],
                rooms=[dict(name="NAVE", rect=(x0, y0, x1, y1 - narthex), type="nave", fitout=shopfit.fitout_for("nave", rnd)),
                       dict(name="NARTHEX", rect=(x0, y1 - narthex, x1, y1), type="lobby", fitout=shopfit.fitout_for("lobby", rnd))],
                doors=[dict(name="main_entry", at=(0.0, y1), w=1.8, h=2.6, ext=True, leaves=2, panels=[(0.1, 0.08, 0.9, 0.92)]),
                       dict(name="narthex_nave", at=(0.0, y1 - narthex), w=1.8, leaves=2, swing_into="NAVE"),
                       dict(name="side", at=(x1, y0 + 2.0), w=0.95, ext=True, out=True)],
                windows=[], stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
    # tall windows along the nave sides (stained glass), a rose/lancet over the entrance
    n = max(3, int((D - narthex - 1.0) / 3.0))
    for j in range(n):
        yy = y0 + 1.5 + j * (D - narthex - 2.0) / max(1, n - 1)
        for xx in (x0, x1):
            if abs(yy - (y0 + 2.0)) < 1.3 and xx == x1:
                continue
            spec["windows"].append(dict(at=(xx, yy), w=1.0, sill=1.4, h=min(3.6, wall_top - FL - 2.0), kind="fixed", cols=2))
    # L-plan: fellowship hall wing
    if tr.get("plan") in ("l_shape", "cruciform") and lot_w - W > 1.0 or tr.get("plan") in ("l_shape", "cruciform") and D > 20:
        hw = min(10.0, D * 0.45)
        hx1 = x0
        hx0 = max(-lot_w / 2 + 0.5, x0 - 7.0)
        if hx1 - hx0 >= 5.0:
            spec["blocks"].append(dict(name="hall", rect=(hx0, y0, hx1, y0 + hw), floors=[(FL, FL + 3.2)], wall_top=FL + 3.4,
                                       found_top=FL - 0.05, roof=dict(type="gable", ridge="x", pitch=30, eave_oh=0.4, rake_oh=0.3,
                                                                      thick=0.18)))
            spec["rooms"].append(dict(name="HALL", rect=(hx0, y0, hx1, y0 + hw), type="fellowship", fitout=shopfit.fitout_for("fellowship", rnd)))
            spec["doors"].append(dict(name="nave_hall", at=(x0, y0 + hw * 0.5), w=0.95, swing_into="HALL"))
            spec["doors"].append(dict(name="hall_out", at=((hx0 + hx1) / 2, y0), w=0.95, ext=True))
    # tower: a real block (walls, doors), belfry and steeple dressed on top of its shaft
    tw = tr.get("tower") or {"position": "front_center", "top": "spire"}
    pos = tw.get("position", "front_center")
    ts = 3.4
    th = wall_top + W / 2 * math.tan(math.radians(pitch)) + 2.5
    trect = None
    if pos == "front_center" and y1 + ts < lot_d / 2 - 1.0:
        trect = (-ts / 2, y1, ts / 2, y1 + ts)
    elif pos in ("front_corner", "front_center"):
        trect = (x1 - ts + 0.6, y1, x1 + 0.6, y1 + ts) if x1 + 0.6 < lot_w / 2 else (x1 - ts, y1, x1, y1 + ts)
        if trect[0] < 1.0:
            trect = None
    elif pos == "side" and x1 + ts < lot_w / 2:
        trect = (x1, y0 + D * 0.55, x1 + ts, y0 + D * 0.55 + ts)
    entry_y = y1
    if trect:
        spec["blocks"].append(dict(name="tower", rect=trect, floors=[(FL, FL + 3.4)], wall_top=th, found_top=FL - 0.05,
                                   roof=dict(type="flat", thick=0.3, parapet=0.0)))
        tx0, ty0, tx1, ty1 = trect
        if pos == "side":
            spec["rooms"].append(dict(name="TOWER", rect=trect, type=None))
            spec["doors"].append(dict(name="tower_nave", at=(x1, (ty0 + ty1) / 2), w=0.95, swing_into="TOWER"))
        else:
            spec["rooms"].append(dict(name="TOWER", rect=trect, type=None, open_plan_to="NARTHEX"))
            if pos == "front_center" and abs((tx0 + tx1) / 2) < 0.01:
                # the main entrance moves to the tower's front face
                spec["doors"] = [d for d in spec["doors"] if d["name"] != "main_entry"]
                spec["doors"].append(dict(name="main_entry", at=(0.0, ty1), w=1.8, h=2.6, ext=True, leaves=2,
                                          panels=[(0.1, 0.08, 0.9, 0.92)]))
                entry_y = ty1
            else:
                spec["doors"].append(dict(name="tower_door", at=((tx0 + tx1) / 2, ty1), w=0.95, ext=True))
    add_stoops(spec, FL)
    gh.House(b, spec).build()
    p = b.part("church_trim-col")
    if trect:
        tx, ty = (trect[0] + trect[2]) / 2, (trect[1] + trect[3]) / 2
        for sx, sy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ox, oy = sx * (ts / 2 + 0.01), sy * (ts / 2 + 0.01)
            hx, hy = (0.5 if sy else 0.02), (0.5 if sx else 0.02)
            p.box((tx + ox - hx, ty + oy - hy, th - 2.2), (tx + ox + hx, ty + oy + hy, th - 0.6), "black")      # louvred belfry openings
        p.cylinder((tx, ty), 0.45, th - 1.8, th - 1.0, "bell", n=12, r1=0.25)
        top = tw.get("top", "spire")
        if top == "spire":
            sp_h = ts / 2 * math.tan(math.radians(78))
            gh.hip_roof(p, tx - ts / 2 - 0.1, tx + ts / 2 + 0.1, ty - ts / 2 - 0.1, ty + ts / 2 + 0.1, th, 78, 0.05, 0.1, "roof", "trim", "trim")
            p.box((tx - 0.03, ty - 0.03, th + sp_h), (tx + 0.03, ty + 0.03, th + sp_h + 1.2), "gold")
            p.box((tx - 0.35, ty - 0.03, th + sp_h + 0.8), (tx + 0.35, ty + 0.03, th + sp_h + 0.86), "gold")
        elif top == "crenellated":
            for k in range(4):
                for sx in (-1, 1):
                    p.box((tx + sx * ts / 2 - 0.25, ty - ts / 2 + k * ts / 4, th), (tx + sx * ts / 2 + 0.25, ty - ts / 2 + k * ts / 4 + 0.4, th + 0.6), "ext")
        else:
            gh.hip_roof(p, tx - ts / 2 - 0.2, tx + ts / 2 + 0.2, ty - ts / 2 - 0.2, ty + ts / 2 + 0.2, th, 35, 0.2, 0.12, "roof", "trim", "trim")
    # church sign board on the lawn with the name, denomination and service times
    sg = names.get("sign") or names.get("name") or ""
    parts = [t.strip() for t in sg.replace("·", "-").split(" - ") if t.strip()]
    sx0 = x1 - 1.0
    sy = lot_d / 2 - 1.3
    p.box((sx0 - 1.3, sy - 0.08, 0.3), (sx0 + 1.3, sy + 0.08, 1.4), "white_text")
    for px_ in (sx0 - 1.2, sx0 + 1.2):
        p.box((px_ - 0.06, sy - 0.06, 0.0), (px_ + 0.06, sy + 0.06, 1.5), "furn_dark")
    for i, t in enumerate(parts[:3]):
        g.text_mesh(b, f"sign_church_{i}", t.upper()[:30], 0.11 if i == 0 else 0.07, (sx0, sy + 0.09, 1.2 - i * 0.28), math.pi,
                    "black_text", extrude=0.004, font=FONT_SERIF)
    # front steps and walk
    nst = max(1, round(FL / 0.17))
    for k in range(nst):
        z = FL - k * FL / nst
        p.box((-1.6 - k * 0.1, entry_y + k * 0.32, 0.0), (1.6 + k * 0.1, entry_y + (k + 1) * 0.32, z), "stone")
    b.part("walk-col").box((-1.0, entry_y + nst * 0.32, -0.02), (1.0, lot_d / 2, 0.03), "sidewalk", sides="Z")
    return b
