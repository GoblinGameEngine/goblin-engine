#!/usr/bin/env python3
"""West Coast candidate harvester for the coastal catalog (SOL / PEL / PLV / OCV).

  harvest_west.py collect GROUP        geotagged Commons files around GROUP's towns -> cand/GROUP.json
  harvest_west.py filter GROUP [RE]    keep building-like titles -> cand/GROUP_b.json
  harvest_west.py sheets GROUP_b A B   numbered 30-thumb contact sheets of entries A..B -> cand/sheets/
  harvest_west.py show GROUP_b N...    print title / date / licence of numbered entries

Wikimedia asks for slow clients: all requests go through refs.get (1.5 s spacing), thumbnails are
the small 240 px standard size."""
import io
import json
import os
import re
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "remake", "tools"))
import refs  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import west_net  # noqa: E402,F401  -- IPv4 + patient 429 handling for refs.get

CAND = os.path.join(HERE, "cand")
API = refs.API

# name, lat, lon  (each point is searched within RADIUS m, on a small grid around it)
GROUPS = {
    # Solana Point = Huntington Beach + Dana Point (+ neighbouring OC beach towns)
    "west_sol": [("Huntington Beach", 33.6557, -118.0005), ("Huntington Beach N", 33.6780, -118.0230),
                 ("Dana Point", 33.4623, -117.7050), ("Dana Point Capistrano Beach", 33.4630, -117.6720),
                 ("San Clemente", 33.4270, -117.6120), ("Newport Beach Balboa", 33.6010, -117.8990),
                 ("Newport Beach W", 33.6160, -117.9300), ("Seal Beach", 33.7410, -118.1050),
                 ("Laguna Beach", 33.5420, -117.7830), ("Sunset Beach", 33.7170, -118.0680)],
    # Pelican Cove = Cannery Row Monterey + Astoria (+ other working waterfronts)
    "west_pel": [("Cannery Row", 36.6160, -121.9010), ("Monterey wharf", 36.6030, -121.8920),
                 ("Pacific Grove", 36.6210, -121.9160), ("Astoria", 46.1880, -123.8310),
                 ("Astoria E", 46.1900, -123.8050), ("Moss Landing", 36.8040, -121.7870),
                 ("Newport OR bayfront", 44.6260, -124.0560), ("Westport WA", 46.9040, -124.1060),
                 ("Ilwaco", 46.3070, -124.0430), ("Morro Bay", 35.3650, -120.8500),
                 ("Bodega Bay", 38.3330, -123.0480), ("Garibaldi OR", 45.5580, -123.9110),
                 ("Crescent City", 41.7490, -124.1960), ("Port Townsend", 48.1170, -122.7600)],
    # Playa Verde = Oceanside + Pismo Beach
    "west_plv": [("Oceanside", 33.1940, -117.3830), ("Oceanside S", 33.1760, -117.3660),
                 ("Pismo Beach", 35.1420, -120.6410), ("Grover Beach", 35.1210, -120.6210),
                 ("Cayucos", 35.4430, -120.8920), ("Avila Beach", 35.1800, -120.7320),
                 ("Carlsbad", 33.1590, -117.3500), ("Encinitas", 33.0460, -117.2930),
                 ("Imperial Beach", 32.5800, -117.1330), ("Ventura", 34.2760, -119.2930)],
    # Pelican Cove houses: working fishing towns with post-1970 housing
    "west_pel2": [("Warrenton OR", 46.1651, -123.9237), ("Winchester Bay OR", 43.6801, -124.1790),
                  ("Charleston OR", 43.3401, -124.3290), ("Brookings-Harbor OR", 42.0526, -124.2840),
                  ("Port Orford OR", 42.7454, -124.4973), ("Depoe Bay OR", 44.8085, -124.0632),
                  ("Trinidad CA", 41.0593, -124.1431), ("King Salmon CA", 40.7390, -124.2176),
                  ("Princeton-by-the-Sea CA", 37.5030, -122.4866), ("La Push WA", 47.9090, -124.6360),
                  ("Sekiu WA", 48.2629, -124.2980), ("Neah Bay WA", 48.3682, -124.6250),
                  ("Westport WA town", 46.8890, -124.1040), ("Ilwaco WA town", 46.3090, -124.0410)],
    # --- laptop's second assignment: Great Lakes (MI/OH/WI/MN/IL/IN/PA-Erie/NY-GL) and East (Atlantic states)
    "gl_ptm": [("Petoskey", 45.3747, -84.9553), ("Bay View MI", 45.3860, -84.9380), ("Harbor Springs", 45.4317, -84.9920),
               ("Charlevoix", 45.3181, -85.2584), ("Traverse City", 44.7631, -85.6206), ("Mackinaw City", 45.7775, -84.7275),
               ("Frankfort MI", 44.6336, -86.2345), ("Leland MI", 45.0231, -85.7598)],
    "gl_vby": [("Put-in-Bay", 41.6531, -82.8157), ("Kelleys Island", 41.5957, -82.7082), ("Port Clinton", 41.5120, -82.9377),
               ("Marblehead OH", 41.5400, -82.7340), ("Lakeside OH", 41.5430, -82.7490), ("Middle Bass", 41.6860, -82.8050),
               ("Vermilion OH", 41.4220, -82.3646), ("Huron OH", 41.3950, -82.5550)],
    "gl_hfw": [("Grand Haven", 43.0631, -86.2284), ("St. Joseph MI", 42.1094, -86.4800), ("South Haven", 42.4031, -86.2736),
               ("Saugatuck", 42.6556, -86.2034), ("Navy Pier", 41.8917, -87.6086), ("Holland MI state park", 42.7727, -86.2090),
               ("Magee Marsh", 41.6250, -83.1880), ("Ottawa NWR", 41.6200, -83.2130), ("Erie PA Presque Isle", 42.1300, -80.0900)],
    "e_trn": [("Lubec", 44.8606, -66.9842), ("Eastport", 44.9062, -66.9900), ("Gloucester", 42.6159, -70.6620),
              ("Stonington ME", 44.1565, -68.6664), ("Rockland ME", 44.1037, -69.1089), ("Vinalhaven", 44.0480, -68.8330),
              ("Port Clyde", 43.9270, -69.2590), ("New Bedford", 41.6362, -70.9214), ("Point Judith RI", 41.3800, -71.5130),
              ("Jonesport", 44.5320, -67.5990), ("Portland Maine waterfront", 43.6560, -70.2500)],
    "e_hvn": [("Barnegat Light", 39.7590, -74.1060), ("Montauk harbor", 41.0730, -71.9360), ("Montauk village", 41.0360, -71.9540),
              ("Point Pleasant Beach", 40.0915, -74.0366), ("Cape May harbor", 38.9570, -74.8980), ("Sag Harbor", 41.0010, -72.2950),
              ("Greenport NY", 41.1030, -72.3590), ("Long Beach Island Beach Haven", 39.5593, -74.2432)],
    # Oceanview = Santa Cruz Beach Boardwalk + Venice + Santa Monica Pier
    "west_ocv": [("Santa Cruz boardwalk", 36.9640, -122.0180), ("Santa Cruz downtown", 36.9740, -122.0260),
                 ("Capitola", 36.9720, -121.9530), ("Venice", 33.9900, -118.4720),
                 ("Venice N", 34.0000, -118.4800), ("Santa Monica", 34.0100, -118.4960),
                 ("Santa Monica N", 34.0240, -118.5070), ("Hermosa Beach", 33.8620, -118.4000),
                 ("Redondo Beach", 33.8420, -118.3900), ("Manhattan Beach", 33.8850, -118.4110),
                 ("Mission Beach SD", 32.7710, -117.2520), ("Pacific Beach SD", 32.7960, -117.2560),
                 ("Long Beach", 33.7650, -118.1900), ("Seaside OR", 45.9930, -123.9290)],
}
RADIUS = 2500
GRID = [(0, 0), (0.018, 0), (-0.018, 0), (0, 0.022), (0, -0.022)]   # ~2 km steps

BUILDING_RE = re.compile(
    r"hotel|motel|\binn\b|lodge|resort|suites|house|home|cottage|bungalow|residence|condo|apartment|"
    r"store|shop|restaurant|cafe|café|diner|grill|bar\b|taqueria|market|bakery|pizza|surf|"
    r"church|chapel|school|library|city hall|civic|post office|fire station|police|museum|theat|"
    r"cannery|warehouse|fish|boat|harbor|marina|wharf|lighthouse|lifeguard|pavilion|arcade|casino|"
    r"building|block|plaza|center|centre|bank|office|"
    r"\b\d{2,5} [A-Z][a-z]+ (st|street|ave|avenue|blvd|boulevard|dr|drive|rd|road|way|lane|ln|pl|place|walk|court|ct|hwy|highway)\b|"
    r"\b(st|street|ave|avenue|blvd|boulevard|dr|drive|way|walk)\b",
    re.I)
SKIP_RE = re.compile(r"\.(svg|pdf|tif|tiff|ogg|webm|mp3|ogv|gif)$|map|logo|diagram|panorama|sunset over|"
                     r"aerial|satellite|seal of|flag of|NARA|LCCN|postcard", re.I)


def _q(params):
    return refs.get(API + "?" + urllib.parse.urlencode(dict(params, format="json")))


def collect(group):
    os.makedirs(CAND, exist_ok=True)
    out_p = os.path.join(CAND, group + ".json")
    seen = {e["title"]: e for e in (json.load(open(out_p)) if os.path.exists(out_p) else [])}
    for name, lat, lon in GROUPS[group]:
        for dy, dx in GRID:
            d = _q({"action": "query", "list": "geosearch", "gsnamespace": 6, "gslimit": 500,
                    "gsradius": RADIUS, "gscoord": f"{lat + dy}|{lon + dx}"})
            new = [g for g in d.get("query", {}).get("geosearch", []) if g["title"] not in seen]
            for g in new:
                seen[g["title"]] = {"title": g["title"], "town": name, "lat": g["lat"], "lon": g["lon"]}
            print(f"{name} {dy:+.3f},{dx:+.3f}: +{len(new)} (total {len(seen)})", flush=True)
        json.dump(list(seen.values()), open(out_p, "w"), indent=0)


def catgroup(group, cats, depth=1):
    """files of Commons categories (and their subcategories to `depth`) -> cand/GROUP.json"""
    os.makedirs(CAND, exist_ok=True)
    es, seen, todo = [], set(), [(c, 0) for c in cats]
    while todo:
        c, dep = todo.pop(0)
        cont = {}
        while True:
            d = _q(dict({"action": "query", "list": "categorymembers", "cmtitle": c, "cmlimit": 500}, **cont))
            for m in d["query"]["categorymembers"]:
                t = m["title"]
                if t.startswith("Category:") and dep < depth:
                    todo.append((t, dep + 1))
                elif t.startswith("File:") and t not in seen and not SKIP_RE.search(t):
                    seen.add(t)
                    es.append({"title": t, "town": c[9:], "lat": 0.0, "lon": 0.0})
            if "continue" not in d:
                break
            cont = d["continue"]
    json.dump(es, open(os.path.join(CAND, group + ".json"), "w"), indent=0)
    print(f"{len(es)} files")


def filt(group, extra=None):
    es = json.load(open(os.path.join(CAND, group + ".json")))
    rx = re.compile(extra, re.I) if extra else BUILDING_RE
    keep = [e for e in es if rx.search(e["title"]) and not SKIP_RE.search(e["title"])]
    json.dump(keep, open(os.path.join(CAND, group + "_b.json"), "w"), indent=0)
    print(f"{len(keep)} of {len(es)} kept")


def _info(titles):
    """thumb url, date, licence for up to 50 titles"""
    d = _q({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
            "iiprop": "url|extmetadata", "iiurlwidth": 240})
    out = {}
    norm = {n["to"]: n["from"] for n in d.get("query", {}).get("normalized", [])}
    for pg in d.get("query", {}).get("pages", {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        t = norm.get(pg["title"], pg["title"])
        out[t] = {"thumb": ii.get("thumburl"),
                  "date": re.sub("<[^>]+>", "", md.get("DateTimeOriginal", {}).get("value", ""))[:10],
                  "license": md.get("LicenseShortName", {}).get("value"),
                  "cats": md.get("Categories", {}).get("value", "")}
    return out


def sheets(group, a, b):
    from PIL import Image, ImageDraw
    es = json.load(open(os.path.join(CAND, group + ".json")))
    os.makedirs(os.path.join(CAND, "sheets"), exist_ok=True)
    for start in range(a, min(b, len(es)), 30):
        chunk = es[start:start + 30]
        need = [e["title"] for e in chunk if "thumb" not in e]
        if need:
            info = _info(need)
            for e in chunk:
                e.update(info.get(e["title"], {}))
            json.dump(es, open(os.path.join(CAND, group + ".json"), "w"), indent=0)
        W, H = 240, 200
        sheet = Image.new("RGB", (W * 6, (H + 16) * 5), "white")
        dr = ImageDraw.Draw(sheet)
        for k, e in enumerate(chunk):
            x, y = (k % 6) * W, (k // 6) * (H + 16)
            try:
                im = Image.open(io.BytesIO(refs.get(e["thumb"], binary=True))).convert("RGB")
                im.thumbnail((W - 4, H - 4))
                sheet.paste(im, (x + 2, y + 2))
            except Exception:  # noqa: BLE001
                dr.text((x + 10, y + 90), "no thumb", fill="red")
            dr.rectangle([x, y + H, x + W, y + H + 16], fill="black")
            dr.text((x + 3, y + H + 2), f"{start + k} {e['title'][5:36]}", fill="yellow")
        p = os.path.join(CAND, "sheets", f"{group}_{start:04d}.jpg")
        sheet.save(p, quality=80)
        print(p, flush=True)


def look(group, ns, out):
    """a closer look: the numbered entries at 500 px, 3 across -> out"""
    from PIL import Image, ImageDraw
    es = json.load(open(os.path.join(CAND, group + ".json")))
    W, H = 500, 380
    rows = (len(ns) + 2) // 3
    sheet = Image.new("RGB", (W * 3, (H + 16) * rows), "white")
    dr = ImageDraw.Draw(sheet)
    for k, n in enumerate(ns):
        e = es[n]
        x, y = (k % 3) * W, (k // 3) * (H + 16)
        try:
            d = _q({"action": "query", "titles": e["title"], "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 500})
            url = next(iter(d["query"]["pages"].values()))["imageinfo"][0]["thumburl"]
            im = Image.open(io.BytesIO(refs.get(url, binary=True))).convert("RGB")
            im.thumbnail((W - 4, H - 4))
            sheet.paste(im, (x + 2, y + 2))
        except Exception:  # noqa: BLE001
            dr.text((x + 10, y + 90), "no image", fill="red")
        dr.rectangle([x, y + H, x + W, y + H + 16], fill="black")
        dr.text((x + 3, y + H + 2), f"{n} {e['title'][5:70]}", fill="yellow")
    sheet.save(out, quality=85)
    print(out)


def show(group, ns):
    es = json.load(open(os.path.join(CAND, group + ".json")))
    for n in ns:
        e = es[n]
        print(f"{n}: {e['title']}  [{e.get('town')}] {e.get('date', '')} {e.get('license', '')} "
              f"{e['lat']:.5f},{e['lon']:.5f}\n     cats: {e.get('cats', '')[:200]}")


if __name__ == "__main__":
    cmd, g = sys.argv[1], sys.argv[2]
    if cmd == "collect":
        collect(g)
    elif cmd == "catgroup":
        catgroup(g, sys.argv[3:])
    elif cmd == "filter":
        filt(g, sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "sheets":
        sheets(g, int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "look":
        look(g, [int(x) for x in sys.argv[4:]], sys.argv[3])
    elif cmd == "show":
        show(g, [int(x) for x in sys.argv[3:]])
