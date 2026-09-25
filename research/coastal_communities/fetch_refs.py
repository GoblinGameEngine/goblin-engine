#!/usr/bin/env python3
"""Reference photos for the coastal-communities research (remake/reference/COAST-*), via refs.py.
Each subject: a Commons search, the first N freely licensed photos fetched with their sources.json."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "remake", "tools"))
import refs  # noqa: E402

SUBJECTS = [
    ("COAST-boardwalk-OceanCityNJ", "Ocean City New Jersey boardwalk", 4),
    ("COAST-boardwalk-AtlanticCity", "Atlantic City boardwalk", 3),
    ("COAST-boardwalk-Wildwood", "Wildwood New Jersey boardwalk", 3),
    ("COAST-doowop-motel-Wildwood", "Wildwood doo-wop motel", 3),
    ("COAST-CasinoPier-SeasideHeights", "Casino Pier Seaside Heights", 3),
    ("COAST-CapeMay-victorian", "Cape May New Jersey Victorian house", 3),
    ("COAST-AsburyPark", "Asbury Park Convention Hall boardwalk", 3),
    ("COAST-VirginiaBeach-boardwalk", "Virginia Beach boardwalk oceanfront", 3),
    ("COAST-Hollywood-Broadwalk", "Hollywood Florida Broadwalk", 3),
    ("COAST-Daytona-pier", "Daytona Beach Main Street Pier", 3),
    ("COAST-Naples-pier", "Naples Florida pier", 3),
    ("COAST-Clearwater-Pier60", "Pier 60 Clearwater Beach", 2),
    ("COAST-FollyBeach", "Folly Beach pier South Carolina", 3),
    ("COAST-UKpier-Brighton", "Brighton Palace Pier", 3),
    ("COAST-UKpier-Southend", "Southend Pier", 3),
    ("COAST-UKpier-Llandudno", "Llandudno Pier", 3),
    ("COAST-UKpier-Eastbourne", "Eastbourne Pier", 2),
    ("COAST-GreatLakes-GrandHaven", "Grand Haven lighthouse pier catwalk", 3),
    ("COAST-GreatLakes-Saugatuck", "Saugatuck Michigan", 3),
    ("COAST-GreatLakes-SouthHaven", "South Haven Michigan lighthouse", 2),
    ("COAST-cannery-Lubec", "Lubec Maine sardine cannery", 3),
    ("COAST-cannery-Eastport", "Eastport Maine waterfront", 2),
    ("COAST-cannery-Astoria", "Astoria Oregon cannery pilings", 3),
    ("COAST-cannery-CanneryRow", "Cannery Row Monterey conveyor", 3),
    ("COAST-fishing-Gloucester", "Gloucester Massachusetts harbor fishing boats wharf", 3),
    ("COAST-Charleston-RainbowRow", "Rainbow Row Charleston", 3),
    ("COAST-Charleston-singlehouse", "Charleston single house piazza", 3),
    ("COAST-Charleston-Battery", "Charleston Battery White Point Garden", 2),
    ("COAST-Charleston-KingStreet", "King Street Charleston", 2),
    ("COAST-Nantucket-MainStreet", "Main Street Nantucket", 3),
    ("COAST-Nantucket-wharf", "Straight Wharf Nantucket", 2),
    ("COAST-Nantucket-shingle", "Nantucket shingle house", 2),
    ("COAST-DanaPoint-harbor", "Dana Point Harbor", 3),
    ("COAST-DanaPoint-headlands", "Dana Point headlands", 2),
    ("COAST-HuntingtonBeach-pier", "Huntington Beach Pier", 3),
    ("COAST-HuntingtonBeach-MainSt", "Main Street Huntington Beach", 2),
    ("COAST-flora-beachgrass", "Ammophila breviligulata dune", 2),
    ("COAST-flora-seaoats", "Uniola paniculata sea oats dune", 2),
    ("COAST-flora-liveoak", "Quercus virginiana Spanish moss Charleston", 2),
    ("COAST-flora-sabal", "Sabal palmetto beach", 2),
    ("COAST-flora-rugosa", "Rosa rugosa dune", 2),
    ("COAST-flora-fanpalm", "Washingtonia robusta Pacific Coast Highway", 2),
    ("COAST-flora-coastalsage", "coastal sage scrub bluff California", 2),
    ("COAST-flora-GreatLakesDunes", "Lake Michigan dunes marram grass", 2),
    ("COAST-geo-headland-bay", "pocket beach headland cliffs", 2),
    ("COAST-geo-seacliff", "sea cliffs sandy cove", 2),
]
OK = ("CC", "Public domain", "PD", "FAL", "CC0")
for sid, q, n in SUBJECTS:
    if os.path.isdir(os.path.join(refs.REF, sid)):
        print("have", sid)
        continue
    try:
        hits = refs.commons_search(q, 25)
    except Exception as e:  # noqa: BLE001
        print("search failed", sid, e)
        continue
    got = 0
    for h in hits:
        if got >= n:
            break
        if not h["license"] or not h["license"].startswith(OK) or not h["title"].lower().endswith((".jpg", ".jpeg", ".tif", ".tiff", ".png")):
            continue
        if (h["w"] or 0) < 900:
            continue
        try:
            refs.commons_fetch(h["title"], sid)
            got += 1
        except Exception as e:  # noqa: BLE001
            print("  fetch failed", h["title"], e)
    print(f"{sid}: {got} of {n}", flush=True)
print("REFS_DONE")
