#!/usr/bin/env python3
"""The deck's candidate harvester (Brightwater BRW, Port Carrow PCR): harvest_west.py's tools with East
Coast groups.  Same commands:  east_harvest.py collect|filter|sheets|look|show GROUP ...
(Output in cand/ as harvest_west's; group names start e_brw / e_pcr.)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest_west as hw  # noqa: E402

hw.GROUPS.update({
    # Brightwater = the Jersey Shore boardwalk town (+ the Delmarva, Virginia and Carolina boardwalks)
    "e_brw": [("Ocean City NJ", 39.2776, -74.5746), ("Wildwood NJ", 38.9918, -74.8149),
              ("North Wildwood", 39.0010, -74.7990), ("Seaside Heights", 39.9440, -74.0730),
              ("Point Pleasant Beach", 40.0910, -74.0420), ("Belmar", 40.1780, -74.0180),
              ("Ship Bottom / LBI", 39.6430, -74.1800), ("Rehoboth Beach", 38.7210, -75.0760),
              ("Ocean City MD", 38.3365, -75.0849), ("Virginia Beach", 36.8529, -75.9780),
              ("Myrtle Beach", 33.6891, -78.8867), ("Cape May", 38.9351, -74.9060)],
    # Port Carrow = Charleston SC (the new neo-traditional towns build Charleston singles today) + Nantucket
    "e_pcr": [("Charleston downtown", 32.7765, -79.9311), ("Mount Pleasant I'On", 32.8180, -79.8710),
              ("Daniel Island", 32.8620, -79.9060), ("Isle of Palms", 32.7868, -79.7948),
              ("Sullivan's Island", 32.7632, -79.8367), ("Folly Beach", 32.6552, -79.9403),
              ("Kiawah Island", 32.6080, -80.0850), ("Mount Pleasant Shem Creek", 32.7950, -79.8830),
              ("Nantucket town", 41.2835, -70.0995), ("Siasconset", 41.2630, -69.9660),
              ("Edgartown", 41.3890, -70.5130), ("Oak Bluffs", 41.4540, -70.5620)],
})

if __name__ == "__main__":
    cmd, g = sys.argv[1], sys.argv[2]
    if cmd == "collect":
        hw.collect(g)
    elif cmd == "cat":
        hw.catgroup(g, sys.argv[3:])
    elif cmd == "filter":
        hw.filt(g, sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "sheets":
        hw.sheets(g, int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == "look":
        hw.look(g, [int(x) for x in sys.argv[4:]], sys.argv[3])
    elif cmd == "show":
        hw.show(g, [int(x) for x in sys.argv[3:]])
