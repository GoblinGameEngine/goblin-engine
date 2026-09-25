#!/usr/bin/env python3
"""Candidate real buildings for the coastal catalog: Commons photos geosearched round real resort
towns of one coast, then numbered contact sheets to pick from by eye (era, kind, uniqueness).

  harvest.py collect GROUP                  -> research/coastal_communities/candidates/GROUP.json
  harvest.py sheets GROUP [start] [count]   -> .../candidates/GROUP_sheet_NN.png (30 per sheet)
"""
import io
import json
import os
import sys
import urllib.parse

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "remake", "tools"))
import refs  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "candidates")
API = refs.API
GROUPS = {"east_jersey_b": [],
         
    # Jersey Shore and nearby resorts (Brightwater)
    "east_jersey": [("OceanCity_NJ", 39.2776, -74.5746), ("Wildwood_NJ", 38.9918, -74.8149), ("SeasideHeights_NJ", 39.9443, -74.0729),
                    ("CapeMay_NJ", 38.9352, -74.9060), ("PointPleasantBeach_NJ", 40.0915, -74.0366), ("Belmar_NJ", 40.1784, -74.0154),
                    ("BeachHaven_NJ", 39.5593, -74.2432), ("SeaIsleCity_NJ", 39.1534, -74.6929), ("Avalon_NJ", 39.1010, -74.7177),
                    ("Margate_NJ", 39.3279, -74.5035), ("Brigantine_NJ", 39.4101, -74.3646), ("AtlanticCity_NJ", 39.3557, -74.4378),
                    ("WildwoodCrest_NJ", 38.9749, -74.8338), ("NorthWildwood_NJ", 39.0007, -74.7996)],
}
BAD = ("map", "logo", "coat_of_arms", "seal", "flag", ".svg", "diagram", "chart", "graph", "sign_", "plaque", "menu")


def collect(group):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, group + ".json")
    cands = json.load(open(path)) if os.path.exists(path) else []
    seen = {c["title"] for c in cands}
    for place, lat, lon in GROUPS[group]:
        p = {"action": "query", "format": "json", "list": "geosearch", "gscoord": f"{lat}|{lon}", "gsradius": "4000",
             "gsnamespace": "6", "gslimit": "500"}
        hits = refs.get(API + "?" + urllib.parse.urlencode(p)).get("query", {}).get("geosearch", [])
        n = 0
        for h in hits:
            t = h["title"]
            tl = t.lower()
            if t in seen or not tl.endswith((".jpg", ".jpeg")) or any(b in tl for b in BAD):
                continue
            seen.add(t)
            cands.append({"title": t, "place": place, "lat": h["lat"], "lon": h["lon"]})
            n += 1
        print(place, n, flush=True)
        json.dump(cands, open(path, "w"), indent=0)
    print("candidates:", len(cands))


def sheets(group, start=0, count=300):
    cands = json.load(open(os.path.join(OUT, group + ".json")))
    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", 16)
    for s0 in range(start, min(len(cands), start + count), 30):
        batch = cands[s0:s0 + 30]
        titles = "|".join(c["title"] for c in batch)
        p = {"action": "query", "format": "json", "titles": titles, "prop": "imageinfo", "iiprop": "url|extmetadata",
             "iiurlwidth": "320"}
        pages = refs.get(API + "?" + urllib.parse.urlencode(p))["query"]["pages"].values()
        info = {pg["title"]: (pg.get("imageinfo") or [{}])[0] for pg in pages}
        sheet = Image.new("RGB", (6 * 330, 5 * 280), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for k, c in enumerate(batch):
            ii = info.get(c["title"], {})
            c["license"] = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value")
            c["date"] = ii.get("extmetadata", {}).get("DateTimeOriginal", {}).get("value", "")[:10]
            try:
                im = Image.open(io.BytesIO(refs.get(ii["thumburl"], binary=True))).convert("RGB")
                im.thumbnail((320, 240))
                sheet.paste(im, ((k % 6) * 330 + 5, (k // 6) * 280 + 5))
            except Exception:  # noqa: BLE001
                pass
            d.text(((k % 6) * 330 + 8, (k // 6) * 280 + 250), f"{s0 + k}  {c['place'][:18]}", font=font, fill=(255, 230, 90))
        sheet.save(os.path.join(OUT, f"{group}_sheet_{s0 // 30:03d}.png"))
        json.dump(cands, open(os.path.join(OUT, group + ".json"), "w"), indent=0)
        print("sheet", s0 // 30, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "collect":
        collect(sys.argv[2])
    else:
        sheets(sys.argv[2], *(int(a) for a in sys.argv[3:]))
