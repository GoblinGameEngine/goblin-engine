#!/usr/bin/env python3
"""style_models.py -- the sky islands' building models, ~6 per architectural style (research/sky_islands/architecture/
styles.json, 67 styles; the user, 2026-10-14: "Generate a wealth of styles and assign each to an island ... redo the
buildings on each island to match its style").

  python3 tools/sky/style_models.py           -> remake/catalog/SKY-<style>-NN.json (+ tools/sky/style_models.json)

Each model is a catalog record of kind "sky", built by remake/blender/gen/sky.py with the shared kit
(gen/sky_kit.py; SSC_KIT=1).  Per style:
  01 home      the style's own typology at middling height (its ground floor shops where the style trades at street level)
  02 tall      as high as the style goes; warrens / piles / overhangs as two or three blocks of different heights
  03 row       a shop row: a storefront per bay, each its own shop and sign
  04 hall      a market (or souk, eatery, bar) hall under flats, crowned (a dome, a minaret, a pagoda's eaves)
  05 landmark  the island's tallest: a narrow tower with the style's crown and a rooftop billboard
  06 works     a workshop / gas works / loft: a machine floor, chimneys and tanks
The style's own data decides the massing (storeys, footprint, stacking), the walls (texture from its materials, colours
from its palette), the windows, and -- from its component and roof lists -- the dressing tokens gen/sky.py turns into
kit pieces.  Deterministic.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CAT = os.path.join(ROOT, "remake", "catalog")
STYLES = os.path.join(ROOT, "godot_project", "remake", "sky", "styles.json")
OUT = os.path.join(HERE, "style_models.json")

# component / roof id substrings -> gen/sky.py dressing tokens
TOKENS = [
    (("bay_window", "galeria", "box_module", "capsule_box", "roshan", "mashrabiya", "jharokha", "bay"), "bay"),
    (("balcony_cage", "window_grille"), "cage"),
    (("balcony_cantilever", "balcony_iron", "balcony_curved", "balcony_fretwork", "balcony_timber", "balcony_band"), "balcony"),
    (("gallery", "verandah", "plank_landing", "boardwalk"), "gallery"),
    (("shutter",), "shutters"),
    (("screen_lattice", "jali", "chebek", "reja", "grille_geometric", "lattice"), "screen"),
    (("plaster_band", "ablaq", "inlay_band", "relief_band", "wave_band", "timber_band", "motif_relief", "led_band", "band"), "bands"),
    (("jetty", "cantilever_beam", "hanging_backshop"), "jetty"),
    (("parapet_crenel", "crenel"), "crenel"),
    (("parapet_rounded",), "crenel_round"),
    (("parapet_screen", "jali_parapet"), "parapet_screen"),
    (("false_front",), "false_front"),
    (("gable_step", "gable_neck", "gable_bell", "gable_cornice", "crane_gable"), "gable_front"),
    (("eave_stack", "pagoda", "dragon_back"), "eaves"),
    (("chhajja", "eyebrow", "timber_eave", "green_tile_eave", "barrel_tile_eave", "fretwork_eave"), "eyebrow"),
    (("arch_", "iwan", "pishtaq", "window_arched", "gate_portal"), "arch"),
    (("beam_ends", "palm_beam"), "beam_ends"),
    (("dome",), "dome"),
    (("chhatri",), "chhatri"),
    (("minaret", "bell_tower", "clock_tower", "tower_square", "round_tower", "menzeh", "turret", "spire", "gate_tower"), "tower"),
    (("tower_corner", "corner_towers"), "corner_towers"),
    (("rooftop_shack", "roof_chalet", "pigeon_loft", "roof_shrine", "rooftop_stall", "roof_pavilion", "loggia", "rooftop_shacks"), "shacks"),
    (("water_tank", "water_drum", "water_tanks"), "tanks"),
    (("antenna",), "antennas"),
    (("laundry",), "laundry"),
    (("pergola", "altana", "roof_garden", "rooftop_garden", "terrace_garden"), "pergola"),
    (("chimney", "vent_stack"), "chimneys"),
    (("awning", "shopfront_shutter", "noren"), "awnings"),
    (("ac_unit",), "ac"),
    (("planter",), "planter"),
    (("lantern", "lights_", "festoon", "bunting", "luminarie", "marquee"), "lanterns"),
    (("rooftop_billboard", "rooftop_letters", "billboard"), "billboard"),
]
SHOP_GROUNDS = ("shops", "arcade", "bars", "eateries", "souk", "market_stalls", "corner_shops", "cafes", "bassi", "rim")
SHOP_KINDS = {
    "eateries": ["restaurant", "cafe", "diner", "bakery", "pizza"],
    "bars": ["bar", "wine_bar", "brewpub", "tavern_hotel", "cafe"],
    "cafes": ["cafe", "bakery", "ice_cream", "diner"],
    "souk": ["dry_goods", "clothing", "jeweler", "bakery", "florist", "souvenir"],
    "market_stalls": ["grocery", "fish_market", "bakery", "butcher", "food"],
    "workshops": ["hardware", "print_shop", "appliance_repair", "shoe_repair"],
    "warehouses": ["hardware", "dry_goods", "marina_store"],
}
DEFAULT_SHOPS = ["cafe", "clothing", "bakery", "grocery", "bookstore", "hardware", "music_store", "florist", "jeweler",
                 "drug_store", "barber", "shoe_store", "art_gallery", "dry_goods", "games", "tattoo", "pet"]
HALL_KIND = {"souk": "dry_goods", "eateries": "restaurant", "bars": "bar", "workshops": "machine_floor", "market_stalls": "grocery",
             "warehouses": "stockroom", "civic": "council", "long_kitchen": "cafeteria", "market_hall": "grocery"}
SIGN_KIND = [("neon_blade", "blade"), ("blade", "blade"), ("video", "dotmatrix"), ("dot_matrix", "dotmatrix"), ("led", "dotmatrix"),
             ("neon", "neon"), ("lightbox", "lightbox"), ("tile", "lightbox"), ("mosaic", "lightbox"), ("clock", "lightbox"),
             ("brass", "brass"), ("letters", "brass"), ("gilt", "brass"), ("lantern", "chochin"), ("chochin", "chochin"),
             ("fanous", "chochin"), ("noren", "painted"), ("banner", "painted"), ("painted", "painted"), ("iron", "painted"),
             ("mural", "painted"), ("billboard", "billboard"), ("marquee", "neon"), ("luminarie", "chochin")]


def h01(*parts):
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def tokens(st):
    words = list(st.get("components", [])) + list(st.get("roof", [])) + list(st.get("openings", []))
    out = []
    for keys, tok in TOKENS:
        if any(k in w for w in words for k in keys):
            out.append(tok)
    # (a few tokens are mutually exclusive or crowd each other)
    if "cage" in out and "bay" in out and st.get("region") not in ("hongkong",):
        out.remove("cage")
    return out


def variants(st, toks):
    comps = " ".join(st.get("components", []) + st.get("roof", []) + st.get("openings", []))
    reg = st.get("region")
    v = {}
    v["bay"] = "lattice" if any(k in comps for k in ("roshan", "mashrabiya", "jharokha", "lattice")) else \
        ("capsule" if any(k in comps for k in ("capsule", "box_module")) else "glass")
    v["bay_roof"] = "dome" if "jharokha" in comps else ("slope" if reg in ("europe", "canada", "spanish") else "flat")
    v["bay_share"] = 0.75 if st.get("typology") in ("tower_house",) or "roshan" in comps else 0.45
    v["balcony_rail"] = "timber" if any(k in comps for k in ("timber", "wood", "fretwork")) else "iron"
    v["cage_share"] = 0.75 if reg == "hongkong" else 0.4
    v["crenel"] = "triangle" if "triangle" in comps or reg == "arabian" and "tighremt" in st["id"] else ("round" if "crenel_round" in toks else "square")
    if "crenel_round" in toks and "crenel" not in toks:
        toks.append("crenel")
    v["arch"] = "horseshoe" if "horseshoe" in comps else ("pointed" if any(k in comps for k in ("pointed", "cusped", "lobed", "iwan")) else "round")
    v["onion"] = "onion" in comps
    v["tower_cap"] = "onion" if "onion" in comps else ("pyramid" if "pyramid" in comps else
                                                       ("spire" if any(k in comps for k in ("spire", "pinnacle", "bell_tower", "clock")) else
                                                        ("flat" if "crenel" in comps else "dome")))
    v["tower_round"] = "round_tower" in comps or "minaret" in comps
    v["gable"] = "neck" if "gable_neck" in comps else ("bell" if "gable_bell" in comps else "step")
    v["shack"] = "chalet" if "roof_chalet" in comps else ("loft" if "pigeon" in comps else ("shrine" if "shrine" in comps else "shack"))
    v["chimney"] = "mosaic" if "trencadis" in comps or "mosaic_chimney" in comps else "stack"
    v["ceiling"] = "tin" if "pressed_tin" in comps else ("coffer" if any(k in comps for k in ("artesonado", "coffer")) else
                                                      ("batten" if "batten" in comps or reg == "tokyo" else "grid"))
    v["ablaq"] = "ablaq" in comps
    v["eave_tiers"] = 3 if "bathhouse" in st["id"] else 2
    v["gallery_side"] = "N"
    return v


def window_params(st):
    t = st.get("typology", "")
    reg = st.get("region")
    if reg in ("hongkong", "tokyo") or t in ("tong_lau", "zakkyo", "warren"):
        return dict(w=1.2, h=1.4, sill=0.9, spacing=1.9)
    if t in ("tower_house", "fortified_house", "hill_cone", "pit_court") or reg == "arabian":
        return dict(w=0.8, h=1.2, sill=1.0, spacing=2.0)
    if t in ("canal_house", "jettied_row", "plex_row") or st["id"] in ("hoist_gables", "closes_lands"):
        return dict(w=1.1, h=1.9, sill=0.6, spacing=1.8)
    if t in ("civic_block", "civic_fair") or "deco" in st["id"]:
        return dict(w=1.4, h=1.9, sill=0.7, spacing=2.8)
    return dict(w=1.0, h=1.5, sill=0.9, spacing=2.3)


def sign_kinds(st):
    out = []
    for k in st.get("signage", {}).get("kinds", []):
        for key, tok in SIGN_KIND:
            if key in k:
                if tok not in out:
                    out.append(tok)
                break
    return out or ["lightbox", "painted"]


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# the style's massing archetype (v2, 2026-10-14: each island must read as its style from across the sky -- silhouette
# first): tower clusters, piles of small boxes, pagoda tiers, court houses round a court, gable rows, slabs
ARCH = {
    "tower_cluster": ["qamariya_towers", "shibam_stack", "roshan_quarter", "tighremt_towers", "jharokha_towers",
                      "zakkyo_signstacks", "capsule_skybox", "closes_lands", "kulle_galleries", "lamp_city",
                      "hanging_houses", "rim_cliffhangers", "spiral_high_street", "mudejar_brickworks", "cholet_ballroom"],
    "pile": ["kowloon_warren", "cantilever_tenement", "laje_stack", "cerro_tin", "box_pile", "toolhouse_stack",
             "patchwork_conventillo", "infilled_frame", "junk_castle", "ghorfa_honeycomb", "ghardaia_cascade",
             "chefchaouen_blue", "medina_warren", "sassi_terraces", "girder_market", "retrofit_noir", "yokocho_lanes"],
    "pagoda": ["bathhouse_tiers", "garden_terraces", "machiya_lattice"],
    "court": ["riad_terraces", "haveli_bazaar", "wikala_market", "falaj_forts", "tulou_ring", "courtyard_canyon",
              "roofstreet_oasis", "matmata_pits", "ablaq_lanes", "pueblo_blanco", "mughal_crown"],
    "gable_row": ["hoist_gables", "jetty_lanes", "gard_wharf", "false_fronts", "cliff_town", "plex_spirals",
                  "bridge_street", "balcon_canario", "konkan_cottages", "canyon_grid"],
}
ARCH_OF = {sid: a for a, ids in ARCH.items() for sid in ids}


def arch_of(sid):
    return ARCH_OF.get(sid, "slab")


def _layout(cols):
    """cols: [[front block, (back block)], ...] from the east end westward; each block dict(w, d, storeys, ground, ...,
    dy).  Columns touch along x; a back block stands right behind its column's front one.  The main block (the first
    column's front) is first.  Returns blocks with rects (plan frame, the front +y)."""
    out = []
    xr = 0.0
    for ci, col in enumerate(cols):
        cw = max(round(bd["w"] * 2) / 2 for bd in col)
        f = col[0]
        d = round(f["d"] * 2) / 2
        y1 = round((d / 2 + f.get("dy", 0.0)) * 2) / 2
        y0 = y1 - d
        for k, bd in enumerate(col):
            w = round(bd["w"] * 2) / 2
            if k == 0:
                rect = [xr - w, y0, xr, y1]
            else:
                bdd = round(bd["d"] * 2) / 2
                rect = [xr - w, y0 - bdd, xr, y0]
                y0 = y0 - bdd
            out.append(dict(name=f"B{len(out)}", rect=[round(v, 2) for v in rect], storeys=int(bd["storeys"]),
                            plan=bd.get("plan", "auto"), ground=bd["ground"], hall_kind=bd.get("hall_kind", "grocery"),
                            ext=len(out)))
        xr -= cw
    return out


def massing(st, model, r):
    """the model's blocks: [dict(rect, storeys, plan, ground, ext)], plan frame, the front +y; centred later"""
    m = st.get("massing", {})
    s_lo, s_hi = (m.get("storeys") or [3, 6])[:2]
    s_lo, s_hi = int(_clamp(s_lo, 2, 10)), int(_clamp(s_hi, 2, 11))
    if s_hi < s_lo:
        s_lo, s_hi = s_hi, s_lo
    g = st.get("ground", "")
    shops = any(k in g for k in SHOP_GROUNDS) or "shop" in g
    gr = "shops" if shops else "dwelling"
    hall_kind = HALL_KIND.get(g, "grocery")
    S = int(round((s_lo + s_hi) / 2))
    A = arch_of(st["id"])
    ri = lambda lo, hi: int(round(lo + (hi - lo) * r()))
    B = lambda w, d, n, ground=gr, **k: dict(w=w, d=d, storeys=int(_clamp(n, 2, 11)), ground=ground, **k)
    hall = lambda: B(_clamp(16.0 + 4.0 * r(), 16.0, 22.0), 14.0, max(2, min(s_lo, 3)), "hall", hall_kind=hall_kind)
    if A == "tower_cluster":
        tw = lambda: 8.0 + r() * 1.0
        td = lambda: 9.5 + r() * 2.0
        cols = {
            "home": [[B(tw(), td(), S + 1)], [B(tw(), td(), S - 1, dy=-1.2)]],
            "tall": [[B(tw(), td(), s_hi + 1)], [B(tw(), td(), s_hi - 2, dy=1.0), B(8.0, 9.5, s_hi - 3, "dwelling")],
                     [B(tw(), td(), s_hi - 1, dy=-0.8)]],
            "row": [[B(tw(), td(), s_lo + 1, "shops")], [B(tw(), td(), s_lo, "shops", dy=0.5)], [B(tw(), td(), s_lo + 2, "shops", dy=-0.5)]],
            "hall": [[B(8.5, 10.5, s_hi)], [hall()]],
            "landmark": [[B(8.5, 10.0, s_hi + 2, plan="tower")], [B(tw(), td(), s_hi - 2, dy=1.5)], [B(8.0, 9.5, s_lo, dy=-1.0)]],
        }[model]
    elif A == "pile":
        bw = lambda: 8.0 + r() * 1.5
        bd_ = lambda: 9.5 + r() * 1.5
        h = lambda lo=s_lo, hi=s_hi: ri(max(2, lo - 1), hi)
        cols = {
            "home": [[B(bw(), bd_(), h(S, s_hi))], [B(bw(), bd_(), h(), dy=0.8), B(8.0, 9.5, h(), "dwelling")], [B(bw(), bd_(), h(), dy=-0.6)]],
            "tall": [[B(bw(), bd_(), s_hi + 1)], [B(bw(), bd_(), h(), dy=1.0), B(8.0, 9.5, h(S, s_hi), "dwelling")],
                     [B(bw(), bd_(), h(), dy=-0.8), B(8.0, 9.5, h(), "dwelling")], [B(bw(), bd_(), h(), dy=0.4)]],
            "row": [[B(bw(), bd_(), h(2, S), "shops")], [B(bw(), bd_(), h(2, S), "shops", dy=0.6)], [B(bw(), bd_(), h(2, S), "shops", dy=-0.4)],
                    [B(bw(), bd_(), h(2, S), "shops", dy=0.3)]],
            "hall": [[B(8.5, 10.0, h(S, s_hi))], [hall()], [B(bw(), bd_(), h(), dy=0.5)]],
            "landmark": [[B(8.5, 10.0, s_hi + 2, plan="tower")], [B(bw(), bd_(), h(), dy=1.0), B(8.0, 9.5, h(), "dwelling")],
                         [B(bw(), bd_(), h(), dy=-0.5)]],
        }[model]
    elif A == "pagoda":
        cols = {
            "home": [[B(14.0, 13.0, S)], [B(9.0, 10.0, max(2, S - 2), dy=-1.0)]],
            "tall": [[B(14.5, 13.5, s_hi + 1)], [B(10.0, 11.0, max(2, s_hi - 3), dy=-1.0)]],
            "row": [[B(16.0, 12.5, max(2, s_lo), "shops")], [B(9.0, 10.0, max(2, s_lo - 1), "shops", dy=0.5)]],
            "hall": [[B(12.5, 12.5, S)], [hall()]],
            "landmark": [[B(12.5, 12.5, s_hi + 2)], [B(9.0, 10.0, s_lo, dy=1.0)]],
        }[model]
    elif A == "court":
        n = lambda d_=0: max(2, S + d_)
        cols = {
            "home": [[B(8.5, 10.0, n()), B(8.5, 10.0, n(), "dwelling")], [B(8.0, 9.5, max(2, S - 1))],
                     [B(8.5, 10.0, n()), B(8.5, 10.0, n(), "dwelling")]],
            "tall": [[B(9.0, 10.5, s_hi), B(9.0, 10.0, s_hi - 1, "dwelling")], [B(8.0, 9.5, S)],
                     [B(9.0, 10.5, s_hi - 1), B(9.0, 10.0, s_hi - 2, "dwelling")]],
            "row": [[B(8.5, 10.0, max(2, s_lo), "shops")], [B(8.0, 10.0, max(2, s_lo), "shops", dy=0.4)], [B(8.5, 10.0, max(2, s_lo + 1), "shops")]],
            "hall": [[B(9.0, 10.0, S), B(9.0, 10.0, S, "dwelling")], [hall()]],
            "landmark": [[B(9.0, 10.0, s_hi + 2, plan="tower"), B(9.0, 10.0, S, "dwelling")], [B(8.0, 9.5, S)],
                         [B(9.0, 10.0, S + 1), B(9.0, 10.0, S, "dwelling")]],
        }[model]
    elif A == "gable_row":
        gw = lambda: 8.0 + r() * 1.0
        gd = lambda: 12.5 + r() * 2.0
        cols = {
            "home": [[B(gw(), gd(), S + 1)], [B(gw(), gd(), S, dy=0.4)], [B(gw(), gd(), S + 2, dy=-0.3)]],
            "tall": [[B(gw(), gd(), s_hi + 1)], [B(gw(), gd(), s_hi, dy=0.5)], [B(gw(), gd(), s_hi - 1, dy=-0.4)], [B(gw(), gd(), s_hi + 1, dy=0.2)]],
            "row": [[B(gw(), gd(), S, "shops")], [B(gw(), gd(), S - 1, "shops", dy=0.3)], [B(gw(), gd(), S + 1, "shops", dy=-0.3)]],
            "hall": [[B(gw(), gd(), S + 1)], [hall()]],
            "landmark": [[B(9.0, 13.0, s_hi + 2)], [B(gw(), gd(), s_hi, dy=0.6)], [B(gw(), gd(), S, dy=-0.4)]],
        }[model]
    else:   # slab
        fp = m.get("footprint_m") or [[10, 10], [16, 14]]
        W = _clamp(fp[0][0] + (fp[-1][0] - fp[0][0]) * r(), 14.0, 24.0)
        D = _clamp(fp[0][1] + (fp[-1][1] - fp[0][1]) * r(), 12.5, 16.0)
        cols = {
            "home": [[B(W, D, S)]],
            "tall": [[B(_clamp(W, 14.0, 18.0), D, s_hi)], [B(10.0, 12.5, max(2, s_hi - 3), dy=1.0)]],
            "row": [[B(_clamp(W * 1.3, 18.0, 26.0), _clamp(D, 12.5, 15.0), max(2, s_lo), "shops")]],
            "hall": [[hall()]],
            "landmark": [[B(10.0, 12.5, s_hi + 2, plan="tower")], [B(_clamp(W, 14.0, 18.0), D, S, dy=1.0)]],
        }[model]
    out = _layout(cols)
    # the main block first (the fire escape's), at the east end: move every block so the lot centres them
    x_lo = min(b["rect"][0] for b in out) - 0.6
    x_hi = max(b["rect"][2] for b in out) + 2.8        # (the fire escape: two 1 m lanes and their rails)
    y_lo = min(b["rect"][1] for b in out) - 0.6
    y_hi = max(b["rect"][3] for b in out) + 1.6        # (the street side: stoops, awnings)
    cx, cy = (x_lo + x_hi) / 2, (y_lo + y_hi) / 2
    for b in out:
        b["rect"] = [round(b["rect"][0] - cx, 2), round(b["rect"][1] - cy, 2), round(b["rect"][2] - cx, 2), round(b["rect"][3] - cy, 2)]
    return out, dict(w=round(x_hi - x_lo, 2), d=round(y_hi - y_lo, 2))


MODELS = ["home", "tall", "row", "hall", "landmark"]          # (works: the halls and rows serve -- disk)
USES = {"home": "dwelling", "tall": "dwelling", "row": "shops", "hall": "market", "landmark": "hall", "works": "workshop"}


def records():
    styles = json.load(open(STYLES))["styles"]
    out = []
    for sid, st in sorted(styles.items()):
        toks0 = tokens(st)
        var = variants(st, toks0)
        pal = st.get("walls", {}).get("palette", ["#d8cfbf", "#b9a98f", "#8a7a66"])
        sig = st.get("signage", {})
        g = st.get("ground", "")
        kinds = SHOP_KINDS.get(g, DEFAULT_SHOPS)
        moods = st.get("night", {}).get("mood", ["#ffb35c"])
        for mi, model in enumerate(MODELS):
            rid = f"SKY-{sid}-{mi + 1:02d}"

            def r(_n=[0], rid=rid):
                _n[0] += 1
                return h01(rid, _n[0])
            blocks, lot = massing(st, model, r)
            toks = list(toks0)
            if model == "landmark":
                toks += [t for t in ("billboard",) if t not in toks]
                if not any(t in toks for t in ("tower", "dome", "eaves", "chhatri", "corner_towers", "gable_front", "false_front")):
                    toks.append("tower")
            if model == "works":
                toks += [t for t in ("chimneys", "tanks") if t not in toks]
            if model == "hall" and not any(t in toks for t in ("dome", "eaves", "tower", "chhatri")):
                toks.append("dome" if st.get("region") in ("arabian", "indian", "spanish") else "lanterns")
            n_shop = sum(1 for b in blocks if b["ground"] == "shops") * 4
            shops = [{"kind": kinds[(mi * 3 + k) % len(kinds)]} for k in range(max(1, n_shop))]
            body = [pal[(mi + k) % len(pal)] for k in range(3)]
            light = sorted(pal, key=lambda c: -sum(int(c[i:i + 2], 16) for i in (1, 3, 5)))[0]
            dark = sorted(pal, key=lambda c: sum(int(c[i:i + 2], 16) for i in (1, 3, 5)))[0]
            sp = sig.get("palette") or [dark]
            rec_arch = arch_of(sid)
            rec = {"id": rid, "settlement": "Sky islands", "generated": "tools/sky/style_models.py", "kind": "sky",
                   "lot": lot,
                   "traits": {"style": sid, "arch": rec_arch, "model_kind": model, "storeys": blocks[0]["storeys"], "storey_h": 3.4 if model == "hall" else 3.2,
                              "blocks": blocks, "window": window_params(st), "dress": toks, "variants": var,
                              "colors": {"body": body, "trim": light if light not in body[:1] else "#ece6d8", "accent": dark if model != "landmark" else sp[0],
                                         "canvas": sp[(mi) % len(sp)], "tile": sp[(mi + 1) % len(sp)]},
                              "signage": {"kinds": sign_kinds(st), "density": float(sig.get("density", 0.5))},
                              "mood": moods[mi % len(moods)], "shops": shops, "roof_access": "fire_escape",
                              "condition": "kept", "year_built": 2700},
                   "names": {"name": ""},
                   "sky": {"style": sid, "model": model, "use": USES[model], "storeys": max(b["storeys"] for b in blocks),
                           "homes": 0},
                   "brief": f"sky island {model} in the {st.get('name', sid)} style: a shared model"}
            out.append(rec)
    return out


def main():
    recs = records()
    os.makedirs(CAT, exist_ok=True)
    for rec in recs:
        with open(os.path.join(CAT, rec["id"] + ".json"), "w") as f:
            json.dump(rec, f, indent=1)
    with open(OUT, "w") as f:
        json.dump([{"id": r["id"], "style": r["traits"]["style"], "model": r["sky"]["model"], "use": r["sky"]["use"],
                    "lot": r["lot"], "storeys": r["sky"]["storeys"]} for r in recs], f, indent=0)
    print(f"{len(recs)} records")


if __name__ == "__main__":
    main()
