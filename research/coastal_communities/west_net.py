"""Imported for its side effects by harvest_west.py / west_rec.py.

Wikimedia rate-limits this household's IPv6 address hard (429s on API calls and originals), so
resolve IPv4 only, space requests 2.5 s apart, and on a 429 wait out Retry-After (or a minute)
instead of failing the whole run."""
import json
import socket
import time
import urllib.error
import urllib.request

import refs

_orig_gai = socket.getaddrinfo


def _gai4(host, port, family=0, *a, **k):
    return _orig_gai(host, port, socket.AF_INET, *a, **k)


socket.getaddrinfo = _gai4
_last = [0.0]


def get(url, binary=False, tries=8):
    for k in range(tries):
        if "wikimedia.org" in url:
            wait = 2.5 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": refs.UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries - 1:
                raise
            ra = e.headers.get("Retry-After")
            time.sleep(min(600, int(ra)) if ra and ra.isdigit() else 60 * (k + 1))
        except Exception:  # noqa: BLE001 -- network flakiness
            if k == tries - 1:
                raise
            time.sleep(10 + 10 * k)


refs.get = get
