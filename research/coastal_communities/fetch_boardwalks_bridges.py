#!/usr/bin/env python3
"""Geotagged boardwalk photos (Commons geosearch round each real boardwalk) and the bridge examples.

  remake/reference/BOARDWALKS/<east|west|greatlakes>/<place>/   photos + sources.json
  remake/reference/BOARDWALKS/boardwalks_geo.json               every photo: coast, place, lat, lon, file
  remake/reference/BRIDGES/<example>/                            photos + sources.json
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "remake", "tools"))
import refs  # noqa: E402

API = refs.API
OK = ("CC", "Public domain", "PD", "FAL", "CC0")
WORDS = ("boardwalk", "broadwalk", "pier", "promenade", "lakewalk", "riverwalk", "ocean front walk", "strand", "walk")

BOARDWALKS = {
    "east": [("AtlanticCity_NJ", 39.3557, -74.4378), ("OceanCity_NJ", 39.2776, -74.5746), ("Wildwood_NJ", 38.9918, -74.8149),
             ("SeasideHeights_NJ", 39.9443, -74.0729), ("AsburyPark_NJ", 40.2204, -73.9985), ("PointPleasant_NJ", 40.0915, -74.0366),
             ("CapeMay_NJ", 38.9302, -74.9179), ("ConeyIsland_NY", 40.5735, -73.9834), ("Rockaway_NY", 40.5830, -73.8200),
             ("JonesBeach_NY", 40.5883, -73.5076), ("RehobothBeach_DE", 38.7215, -75.0761), ("OceanCity_MD", 38.3365, -75.0849),
             ("VirginiaBeach_VA", 36.8529, -75.9780), ("MyrtleBeach_SC", 33.6891, -78.8867), ("CarolinaBeach_NC", 34.0352, -77.8936),
             ("HollywoodBeach_FL", 26.0112, -80.1149), ("DaytonaBeach_FL", 29.2270, -81.0055), ("MiamiBeach_FL", 25.7907, -80.1300),
             ("JacksonvilleBeach_FL", 30.2947, -81.3931), ("HamptonBeach_NH", 42.9087, -70.8120), ("OldOrchardBeach_ME", 43.5170, -70.3776),
             ("RevereBeach_MA", 42.4190, -70.9890), ("FollyBeach_SC", 32.6552, -79.9404), ("Nantucket_MA", 41.2850, -70.0930),
             ("Charleston_SC", 32.7785, -79.9260)],
    "west": [("SantaCruz_CA", 36.9641, -122.0178), ("SantaMonica_CA", 34.0100, -118.4962), ("VeniceBeach_CA", 33.9850, -118.4695),
             ("HermosaBeach_CA", 33.8622, -118.3995), ("ManhattanBeach_CA", 33.8847, -118.4109), ("RedondoBeach_CA", 33.8400, -118.3915),
             ("HuntingtonBeach_CA", 33.6553, -118.0035), ("Balboa_NewportBeach_CA", 33.6006, -117.9001), ("Oceanside_CA", 33.1934, -117.3861),
             ("MissionBeach_CA", 32.7707, -117.2525), ("PacificBeach_CA", 32.7970, -117.2570), ("PismoBeach_CA", 35.1386, -120.6432),
             ("SantaBarbara_CA", 34.4099, -119.6856), ("Ventura_CA", 34.2750, -119.2920), ("Capitola_CA", 36.9720, -121.9530),
             ("LagunaBeach_CA", 33.5420, -117.7850), ("DanaPoint_CA", 33.4600, -117.6980), ("MorroBay_CA", 35.3660, -120.8500),
             ("Monterey_CA", 36.6050, -121.8950), ("Seaside_OR", 45.9932, -123.9290), ("LongBeach_WA", 46.3520, -124.0550),
             ("CannonBeach_OR", 45.8918, -123.9615), ("ImperialBeach_CA", 32.5790, -117.1350)],
    "greatlakes": [("GrandHaven_MI", 43.0580, -86.2460), ("Duluth_CanalPark_MN", 46.7800, -92.0920), ("Petoskey_MI", 45.3760, -84.9550),
                   ("PutInBay_OH", 41.6526, -82.8196), ("TraverseCity_MI", 44.7650, -85.6200), ("StJoseph_MI", 42.1100, -86.4870),
                   ("SouthHaven_MI", 42.4030, -86.2840), ("MackinacIsland_MI", 45.8490, -84.6180), ("Chicago_NavyPier_IL", 41.8917, -87.6086),
                   ("Milwaukee_WI", 43.0360, -87.8960), ("Erie_Bayfront_PA", 42.1380, -80.0900), ("Sandusky_OH", 41.4570, -82.7110),
                   ("CedarPoint_OH", 41.4822, -82.6835), ("Kenosha_WI", 42.5850, -87.8150), ("MichiganCity_IN", 41.7300, -86.9050),
                   ("Marquette_MI", 46.5430, -87.3900), ("Ludington_MI", 43.9550, -86.4550), ("Saugatuck_MI", 42.6560, -86.2030),
                   ("HarborSprings_MI", 45.4310, -84.9920), ("PortClinton_OH", 41.5120, -82.9380), ("Cleveland_OH", 41.5090, -81.6950),
                   ("Toledo_Maumee_OH", 41.6528, -83.5379)],
}
BRIDGES = [("ChesapeakeBayBridge_1973", "Chesapeake Bay Bridge Maryland", 4),
           ("AlZampaMemorial_2003", "Alfred Zampa Memorial Bridge", 4),
           ("TacomaNarrows_2007", "Tacoma Narrows Bridge 2007", 4),
           ("SevenMileBridge_1982", "Seven Mile Bridge Florida", 4),
           ("I10TwinSpan_2011", "I-10 Twin Span Bridge Lake Pontchartrain", 3),
           ("AtchafalayaBasinBridge_1973", "Atchafalaya Basin Bridge", 3),
           ("ManchacSwamp_1979", "Manchac Swamp Bridge", 3),
           ("CBBT_trestle_1999", "Chesapeake Bay Bridge-Tunnel trestle", 3),
           ("GlassCitySkyway_2007", "Veterans Glass City Skyway", 4),
           ("LongBeachIntlGateway_2020", "Long Beach International Gateway bridge", 3),
           ("SunshineSkyway_1987", "Sunshine Skyway Bridge", 3),
           ("ArthurRavenel_2005", "Arthur Ravenel Jr. Bridge", 3),
           ("LakePontchartrainCauseway", "Lake Pontchartrain Causeway", 3),
           ("rail_trestle_modern", "concrete railroad trestle bridge", 3),
           ("PutInBay_town", "Put-in-Bay Ohio", 6),
           ("Petoskey_town", "Petoskey Michigan", 6),
           ("BarnegatLight", "Barnegat Light", 4),
           ("Montauk_harbor", "Montauk harbor", 4),
           ("SantaCruzBoardwalk", "Santa Cruz Beach Boardwalk", 5),
           ("Oceanside_pier", "Oceanside Pier California", 4)]
PER_PLACE = 5


def geosearch(lat, lon, radius=3000, limit=80):
    p = {"action": "query", "format": "json", "list": "geosearch", "gscoord": f"{lat}|{lon}", "gsradius": str(radius),
         "gsnamespace": "6", "gslimit": str(limit)}
    d = refs.get(API + "?" + urllib.parse.urlencode(p))
    return d.get("query", {}).get("geosearch", [])


def info(title):
    p = {"action": "query", "format": "json", "titles": title, "prop": "imageinfo", "iiprop": "size|extmetadata"}
    d = refs.get(API + "?" + urllib.parse.urlencode(p))
    ii = (next(iter(d["query"]["pages"].values())).get("imageinfo") or [{}])[0]
    return ii.get("width") or 0, ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")


geo_path = os.path.join(refs.REF, "BOARDWALKS", "boardwalks_geo.json")
geo = json.load(open(geo_path)) if os.path.exists(geo_path) else []
done = {(g["coast"], g["place"]) for g in geo}
for coast, places in BOARDWALKS.items():
    for place, lat, lon in places:
        if (coast, place) in done:
            continue
        sid = os.path.join("BOARDWALKS", coast, place)
        got = 0
        try:
            hits = geosearch(lat, lon)
        except Exception as e:  # noqa: BLE001
            print("geosearch failed", place, e)
            continue
        for h in hits:
            if got >= PER_PLACE:
                break
            t = h["title"]
            if not any(w in t.lower() for w in WORDS) or not t.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                continue
            try:
                w, lic = info(t)
                if w < 1000 or not lic.startswith(OK):
                    continue
                name = refs.commons_fetch(t, sid)
                geo.append({"coast": coast, "place": place, "lat": h["lat"], "lon": h["lon"], "file": os.path.join(sid, name), "title": t})
                got += 1
            except Exception as e:  # noqa: BLE001
                print("  fetch failed", t, e)
        if got == 0:
            geo.append({"coast": coast, "place": place, "lat": lat, "lon": lon, "file": None, "title": None})
        json.dump(geo, open(geo_path, "w"), indent=1)
        print(f"{coast}/{place}: {got}", flush=True)

for sid, q, n in BRIDGES:
    sid = os.path.join("BRIDGES", sid)
    if os.path.isdir(os.path.join(refs.REF, sid)):
        continue
    got = 0
    try:
        hits = refs.commons_search(q, 30)
    except Exception as e:  # noqa: BLE001
        print("search failed", sid, e)
        continue
    for h in hits:
        if got >= n:
            break
        if not h["license"] or not h["license"].startswith(OK) or (h["w"] or 0) < 1000:
            continue
        if not h["title"].lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
            continue
        try:
            refs.commons_fetch(h["title"], sid)
            got += 1
        except Exception as e:  # noqa: BLE001
            print("  fetch failed", h["title"], e)
    print(f"{sid}: {got}", flush=True)
print("FETCH_DONE")
