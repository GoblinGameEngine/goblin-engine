#!/usr/bin/env python3
"""assign.py -- every sky island its warren family (research/sky_islands/warrens r1/r2/r3: 44 families), written to
godot_project/remake/sky/warrens/assign.json (canon_sky reads it into the bible: run tools/bible/make_bible.py after).

Hints, strongest first: the island's old architecture style (style_assign.json, research/sky_islands/architecture) ->
the families it was drawn from; the clan's heritage (canon) -> the families of that world; size -> dense tower
families on the big islands, villages on the small.  Every family is used once where some island fits it (scarcest
first), the rest of the islands take their best family with a penalty for repeats (at most 4 each).  Deterministic.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/assign.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CANON = os.path.join(ROOT, "godot_project", "remake", "bible", "sky_islands.json")
STYLES = os.path.join(ROOT, "godot_project", "remake", "sky", "style_assign.json")
WR = os.path.join(ROOT, "research", "sky_islands", "warrens")
OUT = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens", "assign.json")

FIXED = {"SKY-100": "maghrebi_medina", "SKY-071": "kowloon_walled",     # milestone 1
         "SKY-007": "hakka_tulou"}          # (a big east-Asian island: the rings need room; 2026-10-15 review)
MIN_BLOCKS = {"hakka_tulou": 4}             # families that only fit on islands this big
CAP = 4

STYLE_HINT = {
    "closes_lands": ["scots_lands"], "gard_wharf": ["hanseatic_gable"], "pueblo_blanco": ["iberian_white"],
    "hoist_gables": ["hanseatic_gable"], "cliff_town": ["tyrrhenian_canyon", "chongqing_cliff", "cycladic"],
    "podium_bazaar": ["hk_neon_canyon"], "hanging_houses": ["chongqing_cliff", "caucasian_balcony"],
    "sassi_terraces": ["rupestrian_terraces"], "false_fronts": ["nouvelle_france", "creole_colonial"],
    "balcon_canario": ["creole_colonial", "iberian_white"], "tong_lau_arcade": ["straits_shophouse", "hk_neon_canyon"],
    "plex_spirals": ["nouvelle_france"], "hangar_quarter": ["taipei_tiepi"], "cantilever_tenement": ["hk_neon_canyon"],
    "capsule_skybox": ["japan_yokocho", "hk_neon_canyon"], "festoon_bazaar": ["karachi", "ganga_ghat"],
    "canyon_grid": ["hk_neon_canyon"], "jetty_lanes": ["siam_khlong", "manila_estero", "jiangnan_water"],
    "rim_cliffhangers": ["chongqing_cliff", "rupestrian_terraces", "cycladic"],
    "lamp_city": ["hk_neon_canyon", "japan_yokocho"], "yokocho_lanes": ["japan_yokocho"],
    "machiya_lattice": ["japan_yokocho", "jiangnan_water"], "courtyard_canyon": ["levantine_courtyard", "cairene_mamluk"],
    "girder_market": ["taipei_tiepi", "hk_neon_canyon"], "zakkyo_signstacks": ["japan_yokocho"],
    "tulou_ring": ["hakka_tulou"], "retrofit_noir": ["hk_neon_canyon", "cairene_mamluk"],
    "exposition_fair": ["creole_colonial", "straits_shophouse"], "jharokha_towers": ["rajput_sandstone"],
    "bathhouse_tiers": ["persian_desert", "caucasian_balcony"], "marine_deco": ["straits_shophouse", "creole_colonial"],
    "patchwork_conventillo": ["latin_hillside"], "garden_terraces": ["korean_hillside", "newar"],
    "danchi_terraces": ["korean_hillside"], "moorish_deco": ["iberian_white", "creole_colonial"],
    "mudejar_brickworks": ["iberian_white"], "qamariya_towers": ["yemeni_tower"],
    "infilled_frame": ["ottoman_timber", "caucasian_balcony"], "cholet_ballroom": ["andean_neo"],
    "spiral_high_street": ["mardin_terraces", "knights_harbour", "lusitanian_hill"],
    "cerro_tin": ["latin_hillside", "andean_neo"], "konkan_cottages": ["ganga_ghat", "creole_colonial"],
    "modernista_reef": ["lusitanian_hill", "iberian_white", "knights_harbour"],
    "toolhouse_stack": ["taipei_tiepi", "viet_tube"], "junk_castle": ["manila_estero", "taipei_tiepi"],
    "chefchaouen_blue": ["maghrebi_medina", "iberian_white", "cycladic"], "box_pile": ["viet_tube", "taipei_tiepi"],
    "laje_stack": ["latin_hillside"], "kulle_galleries": ["kulla_stone"], "kowloon_warren": ["kowloon_walled"],
    "saracenic_gothic": ["karachi", "mughal_walled"], "haveli_bazaar": ["rajput_sandstone", "mughal_walled"],
    "roofstreet_oasis": ["mzab_ghadames"], "mughal_crown": ["mughal_walled"], "ghardaia_cascade": ["mzab_ghadames"],
    "matmata_pits": ["saharan_kasbah", "rupestrian_terraces"], "ablaq_lanes": ["levantine_courtyard", "cairene_mamluk"],
    "shibam_stack": ["yemeni_tower"], "wikala_market": ["cairene_mamluk", "silk_road"], "riad_terraces": ["maghrebi_medina"],
    "falaj_forts": ["omani_oasis"], "tighremt_towers": ["saharan_kasbah"], "roshan_quarter": ["hejazi_roshan"],
    "chawl_galleries": ["karachi"], "ghorfa_honeycomb": ["saharan_kasbah", "silk_road"],
    "medina_warren": ["maghrebi_medina"],
}
ARAB = ["yemeni_tower", "hejazi_roshan", "omani_oasis", "levantine_courtyard", "cairene_mamluk", "maghrebi_medina",
        "mzab_ghadames", "saharan_kasbah", "persian_desert", "silk_road"]
HERITAGE_HINT = {
    "irish_scots": ["scots_lands"], "german": ["hanseatic_gable"], "scandinavian": ["hanseatic_gable"],
    "dutch": ["hanseatic_gable"], "polish": ["caucasian_balcony", "kulla_stone", "ottoman_timber"],
    "slavic": ["kulla_stone", "caucasian_balcony", "ottoman_timber"], "hungarian": ["ottoman_timber", "kulla_stone"],
    "greek": ["cycladic", "ottoman_timber", "mardin_terraces"], "italian": ["tyrrhenian_canyon", "rupestrian_terraces"],
    "hispanic": ["iberian_white", "latin_hillside", "andean_neo", "creole_colonial", "lusitanian_hill", "knights_harbour"],
    "francophone": ["nouvelle_france", "creole_colonial"],
    "east_asian": ["hk_neon_canyon", "chongqing_cliff", "jiangnan_water", "hakka_tulou", "japan_yokocho",
                   "korean_hillside", "taipei_tiepi", "kowloon_walled"],
    "se_asian": ["viet_tube", "siam_khlong", "straits_shophouse", "manila_estero"],
    "south_asian": ["karachi", "mughal_walled", "rajput_sandstone", "ganga_ghat", "newar"],
    "arab": ARAB, "indigenous": ["andean_neo", "tibetan_lhasa"],
    "black_anglo": ["creole_colonial", "latin_hillside"], "black": ["creole_colonial", "latin_hillside"],
}
DENSE = {"kowloon_walled", "hk_neon_canyon", "yemeni_tower", "scots_lands", "karachi", "chongqing_cliff", "japan_yokocho",
         "taipei_tiepi", "cairene_mamluk", "mughal_walled"}
VILLAGE = {"cycladic", "omani_oasis", "mzab_ghadames", "hakka_tulou", "rupestrian_terraces", "saharan_kasbah",
           "tibetan_lhasa", "kulla_stone", "siam_khlong", "jiangnan_water"}


def h01(*a):
    return int(hashlib.sha1(":".join(map(str, a)).encode()).hexdigest()[:8], 16) / 2 ** 32


def families():
    out = []
    for f in ("r1_grammars.json", "r2_grammars.json", "r3_grammars.json"):
        out += [x["id"] for x in json.load(open(os.path.join(WR, f)))["families"]]
    return out


def score(isl, style, fam):
    if int(isl["blocks"]) < MIN_BLOCKS.get(fam, 0):
        return -99.0
    s = 0.0
    sh = STYLE_HINT.get(style or "", [])
    if fam in sh:
        s += (6, 4, 3)[min(sh.index(fam), 2)]
    hh = HERITAGE_HINT.get(isl["heritage"], [])
    if fam in hh:
        s += 2.5 if hh.index(fam) == 0 else 1.5
    b = int(isl["blocks"])
    if fam in DENSE:
        s += 0.8 if b >= 5 else (-0.8 if b <= 2 else 0)
    if fam in VILLAGE:
        s += 0.8 if b <= 3 else (-0.8 if b >= 6 else 0)
    return s + h01("tie", isl["id"], fam) * 0.05


def main():
    canon = json.load(open(CANON))["islands"]
    styles = json.load(open(STYLES))["assign"]
    fams = families()
    sc = {(i["id"], f): score(i, styles.get(i["id"]), f) for i in canon for f in fams}
    out = dict(FIXED)
    used = {f: list(FIXED.values()).count(f) for f in fams}
    # every family once where an island fits it (score > 2), the scarcest family first
    fits = {f: [i["id"] for i in canon if sc[(i["id"], f)] > 2.0] for f in fams}
    for f in sorted(fams, key=lambda f: (len(fits[f]), f)):
        if used[f]:
            continue
        cand = [iid for iid in fits[f] if iid not in out]
        if cand:
            best = max(cand, key=lambda iid: sc[(iid, f)])
            out[best] = f
            used[f] += 1
    # the rest: each its best family, repeats penalised
    rest = sorted((i for i in canon if i["id"] not in out),
                  key=lambda i: -max(sc[(i["id"], f)] for f in fams))
    for i in rest:
        f = max((f for f in fams if used[f] < CAP), key=lambda f: sc[(i["id"], f)] - 1.2 * used[f])
        out[i["id"]] = f
        used[f] += 1
    doc = {"version": 1, "about": "warren family per sky island (tools/sky/warren/assign.py; research/sky_islands/warrens)",
           "assign": dict(sorted(out.items())),
           "families_used": {f: n for f, n in sorted(used.items()) if n},
           "families_unused": [f for f in fams if not used[f]]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=1)
    print(len(doc["families_used"]), "families used;", "unused:", doc["families_unused"])
    print(doc["families_used"])


if __name__ == "__main__":
    main()
