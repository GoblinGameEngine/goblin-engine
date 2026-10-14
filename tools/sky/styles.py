#!/usr/bin/env python3
"""styles.py -- merge the three research streams' style catalogues and assign a style to every sky island.

  python3 tools/sky/styles.py

Reads research/sky_islands/architecture/styles_{a,b,c}.json and components_{a,b,c}.json, writes
  research/sky_islands/architecture/styles.json      every style (67), with its region
  research/sky_islands/architecture/components.json  the shared component vocabulary (union; used_by merged)
  godot_project/remake/sky/styles.json               the same styles for the game (signs, night moods)
  godot_project/remake/sky/style_assign.json         island id -> style id

The user, 2026-10-14: "Generate a wealth of styles and assign each to an island."  Every style is used at least once
(67 styles, 100 islands: none more than twice); each island gets the style that suits it best -- its name's kind
(ancient names lean to the Arabian and Indian styles, mystical to the fantasy and Tokyo ones, nautical to the wharf
and gable towns, whimsical to the colourful ones), its founding clan's heritage, and its size (the warrens and towers
on the big islands, the low lanes and cottages on the small ones).  Deterministic.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ARCH = os.path.join(ROOT, "research", "sky_islands", "architecture")
CANON = os.path.join(ROOT, "godot_project", "remake", "bible", "sky_islands.json")
GAME = os.path.join(ROOT, "godot_project", "remake", "sky")

REGIONS = {
    "arabian": ["qamariya_towers", "shibam_stack", "roshan_quarter", "wikala_market", "falaj_forts", "ablaq_lanes",
                "roofstreet_oasis", "riad_terraces", "medina_warren", "ghorfa_honeycomb", "tighremt_towers",
                "ghardaia_cascade", "matmata_pits", "chefchaouen_blue"],
    "spanish": ["pueblo_blanco", "mudejar_brickworks", "hanging_houses", "modernista_reef", "balcon_canario", "moorish_deco"],
    "indian": ["haveli_bazaar", "mughal_crown", "chawl_galleries", "marine_deco", "saracenic_gothic", "toolhouse_stack",
               "konkan_cottages", "festoon_bazaar", "jharokha_towers"],
    "hongkong": ["kowloon_warren", "tong_lau_arcade", "cantilever_tenement", "podium_bazaar", "courtyard_canyon", "tulou_ring"],
    "tokyo": ["zakkyo_signstacks", "yokocho_lanes", "capsule_skybox", "machiya_lattice", "danchi_terraces"],
    "fantasy": ["bathhouse_tiers", "junk_castle", "garden_terraces", "exposition_fair", "retrofit_noir", "lamp_city",
                "hangar_quarter", "girder_market", "rim_cliffhangers"],
    "europe": ["closes_lands", "jetty_lanes", "bridge_street", "sassi_terraces", "hoist_gables", "gard_wharf",
               "kulle_galleries", "spiral_high_street", "canyon_grid"],
    "samerica": ["laje_stack", "cholet_ballroom", "cerro_tin", "infilled_frame", "patchwork_conventillo"],
    "canada": ["plex_spirals", "box_pile", "false_fronts", "cliff_town"],
}
REGION_OF = {s: r for r, ids in REGIONS.items() for s in ids}

NAME_KIND = {   # name kind -> {region or style id: bonus}
    "ancient": {"arabian": 3, "indian": 2, "sassi_terraces": 1, "spiral_high_street": 1, "mughal_crown": 1},
    "mystical": {"fantasy": 3, "tokyo": 2, "hongkong": 1, "lamp_city": 1, "qamariya_towers": 1},
    "nautical": {"hoist_gables": 3, "gard_wharf": 3, "cliff_town": 2, "hanging_houses": 2, "balcon_canario": 2,
                 "tong_lau_arcade": 1, "hangar_quarter": 2, "rim_cliffhangers": 1, "bridge_street": 1, "canada": 1},
    "whimsical": {"samerica": 3, "junk_castle": 3, "garden_terraces": 2, "modernista_reef": 3, "chefchaouen_blue": 3,
                  "konkan_cottages": 2, "false_fronts": 2, "exposition_fair": 2, "box_pile": 2, "bathhouse_tiers": 1},
}
HERITAGE = {
    "hispanic": {"spanish": 3, "samerica": 3},
    "francophone": {"canada": 3, "plex_spirals": 1, "cliff_town": 1},
    "german": {"jetty_lanes": 3, "hoist_gables": 3, "europe": 1},
    "east_asian": {"hongkong": 3, "tokyo": 3},
    "irish_scots": {"closes_lands": 4, "europe": 1},
    "greek": {"sassi_terraces": 2, "spiral_high_street": 2, "europe": 1},
    "italian": {"canyon_grid": 3, "sassi_terraces": 2, "bridge_street": 2},
    "polish": {"europe": 2},
    "black_anglo": {"samerica": 1, "indian": 1, "festoon_bazaar": 1},
    "black": {"samerica": 1, "festoon_bazaar": 1},
}


def h01(*parts):
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def load(stream):
    s = json.load(open(os.path.join(ARCH, f"styles_{stream}.json")))["styles"]
    c = json.load(open(os.path.join(ARCH, f"components_{stream}.json")))["components"]
    return s, c


def merge():
    styles, comps = [], {}
    for stream in "abc":
        s, c = load(stream)
        for st in s:
            st = dict(st)
            st["stream"] = stream
            st["region"] = REGION_OF.get(st["id"], "other")
            styles.append(st)
        items = c.items() if isinstance(c, dict) else ((x["id"], x) for x in c)
        for cid, cd in items:
            cd = dict(cd)
            cd.setdefault("id", cid)
            if cid in comps:
                old = comps[cid]
                old["used_by"] = sorted(set(old.get("used_by", [])) | set(cd.get("used_by", [])))
                old.setdefault("streams", []).append(stream)
            else:
                cd["streams"] = [stream]
                comps[cid] = cd
    ids = [s["id"] for s in styles]
    assert len(ids) == len(set(ids)), "duplicate style ids"
    missing = [s["id"] for s in styles if s["region"] == "other"]
    assert not missing, f"styles without a region: {missing}"
    return styles, comps


def tall(st):
    m = st.get("massing", {})
    hi = (m.get("storeys") or [3, 5])[-1]
    return st.get("typology") in ("warren", "tower_house") or m.get("stack") in ("pile", "overhang", "cantilever") or hi >= 8


def low(st):
    hi = (st.get("massing", {}).get("storeys") or [3, 5])[-1]
    return hi <= 4


def score(isl, st):
    sc = 0.0
    for table, key in ((NAME_KIND, isl.get("name_kind")), (HERITAGE, isl.get("heritage"))):
        bon = table.get(key, {})
        sc += bon.get(st["region"], 0) + bon.get(st["id"], 0)
    b = isl["blocks"]
    if tall(st):
        sc += 2.0 if b >= 6 else (-2.0 if b <= 2 else 0.0)
    if low(st):
        sc += 1.5 if b <= 3 else (-1.5 if b >= 7 else 0.0)
    return sc + h01("tie", isl["id"], st["id"]) * 0.9        # (a little chance in it)


def assign(islands, styles):
    out, used = {}, {s["id"]: 0 for s in styles}
    # every style once: the styles in a fixed shuffled order each take the free island that suits them best
    for st in sorted(styles, key=lambda s: h01("order", s["id"])):
        best = max((i for i in islands if i["id"] not in out), key=lambda i: score(i, st))
        out[best["id"]] = st["id"]
        used[st["id"]] += 1
    # the rest: each its best style used fewer than twice
    for isl in islands:
        if isl["id"] in out:
            continue
        st = max((s for s in styles if used[s["id"]] < 2), key=lambda s: score(isl, s))
        out[isl["id"]] = st["id"]
        used[st["id"]] += 1
    return out


def main():
    styles, comps = merge()
    canon = json.load(open(CANON))
    islands = canon["islands"]
    asg = assign(islands, styles)
    json.dump({"version": 1, "count": len(styles), "regions": REGIONS, "styles": styles},
              open(os.path.join(ARCH, "styles.json"), "w"), indent=1)
    json.dump({"version": 1, "count": len(comps), "components": comps},
              open(os.path.join(ARCH, "components.json"), "w"), indent=1)
    os.makedirs(GAME, exist_ok=True)
    json.dump({"version": 1, "styles": {s["id"]: s for s in styles}}, open(os.path.join(GAME, "styles.json"), "w"))
    json.dump({"version": 1, "assign": asg}, open(os.path.join(GAME, "style_assign.json"), "w"), indent=1)
    by = {}
    for i in islands:
        by.setdefault(asg[i["id"]], []).append(f'{i["name"]}({i["blocks"]})')
    print(f"{len(styles)} styles, {len(comps)} components, {len(asg)} islands assigned")
    for s in styles:
        print(f'  {s["region"]:9s} {s["id"]:22s} {", ".join(by.get(s["id"], []))}')


if __name__ == "__main__":
    main()
