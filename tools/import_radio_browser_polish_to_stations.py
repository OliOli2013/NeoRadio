#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeoRadio - import polskich stacji z Radio-Browser bez zmiany wersji wtyczki.

Skrypt:
- pobiera maksymalnie dużą bazę polskich stacji z Radio-Browser API,
- bierze stacje po języku: polish oraz po kraju: PL,
- pomija wpisy bez URL i duplikaty,
- preferuje url_resolved, gdy jest dostępny,
- aktualizuje WYŁĄCZNIE stations.json,
- NIE zmienia manifest.json, control, plugin.py ani wersji wtyczki.

Uruchomienie w katalogu repo NeoRadio:
python3 tools/import_radio_browser_polish_to_stations.py

Albo bezpośrednio:
python3 import_radio_browser_polish_to_stations.py --input pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json --output pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json
"""

from __future__ import print_function

import argparse
import gzip
import json
import os
import re
import sys
import time

try:
    # Python 3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
except ImportError:
    # Python 2 fallback, gdyby ktoś odpalił na starszym systemie PC
    from urllib import urlencode
    from urllib2 import Request, urlopen

DEFAULT_STATIONS_PATH = os.path.join(
    "pkgroot", "usr", "lib", "enigma2", "python", "Plugins", "Extensions", "NeoRadio", "stations.json"
)

API_SERVERS = [
    "https://de1.api.radio-browser.info",
    "https://de2.api.radio-browser.info",
    "https://nl1.api.radio-browser.info",
    "https://at1.api.radio-browser.info",
]

USER_AGENT = "NeoRadio/2.0 GitHub stations import by Pawel-Pawelek"

# Enigma2 zwykle lepiej radzi sobie z bezpośrednim HTTP/HTTPS niż z technicznymi/playlistowymi wpisami.
BAD_URL_PARTS = (
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "hdfradio",
)

SUPPORTED_CODECS = set(["MP3", "AAC", "AAC+", "OGG", "OPUS", "WMA", "FLAC", ""])


def fetch_json(url, timeout=45):
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urlopen(req, timeout=timeout) as response:
        raw = response.read()
    if url.endswith(".gz"):
        raw = gzip.decompress(raw)
    if not isinstance(raw, str):
        raw = raw.decode("utf-8", "replace")
    return json.loads(raw)


def build_url(server, params):
    return server.rstrip("/") + "/json/stations/search?" + urlencode(params)


def fetch_radio_browser_polish(limit):
    queries = [
        {
            "language": "polish",
            "hidebroken": "true",
            "order": "clickcount",
            "reverse": "true",
            "limit": str(limit),
        },
        {
            "countrycode": "PL",
            "hidebroken": "true",
            "order": "clickcount",
            "reverse": "true",
            "limit": str(limit),
        },
    ]

    all_items = []
    errors = []

    for params in queries:
        done = False
        for server in API_SERVERS:
            url = build_url(server, params)
            try:
                print("Pobieram:", url)
                items = fetch_json(url)
                print("  OK:", len(items), "wpisów")
                all_items.extend(items)
                done = True
                time.sleep(0.5)
                break
            except Exception as e:
                errors.append("%s -> %s" % (url, e))
                print("  Błąd:", e)
                time.sleep(1)
        if not done:
            print("Nie udało się pobrać zapytania:", params)

    if not all_items:
        print("\nNie pobrano żadnych danych z API. Błędy:")
        for e in errors:
            print(" -", e)
        raise SystemExit(2)

    return all_items


def clean_text(value):
    if value is None:
        return ""
    value = str(value).replace("\x00", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def norm_url(url):
    url = clean_text(url)
    url = url.replace("%20", " ").strip()
    while url.endswith("/") and not re.match(r"^https?://[^/]+/$", url):
        url = url[:-1]
    return url.lower()


def norm_name(name):
    return re.sub(r"\s+", " ", clean_text(name)).strip().lower()


def is_bad_url(url):
    low = url.lower()
    if not (low.startswith("http://") or low.startswith("https://")):
        return True
    for bad in BAD_URL_PARTS:
        if bad in low:
            return True
    return False


def parse_tags(tags):
    tags = clean_text(tags)
    if not tags:
        return []
    out = []
    for tag in tags.split(","):
        tag = clean_text(tag)
        if tag and tag.lower() not in ("polish", "polska", "poland"):
            out.append(tag)
    return out[:5]


def map_station(rb):
    name = clean_text(rb.get("name"))
    url = clean_text(rb.get("url_resolved")) or clean_text(rb.get("url"))
    codec = clean_text(rb.get("codec", ""))

    if not name or not url or is_bad_url(url):
        return None

    # Nie odrzucam HLS automatycznie, bo część obrazów Enigma2 z ServiceApp/ffmpeg je obsłuży.
    # Jeżeli chcesz wycinać HLS, odkomentuj poniższe linie:
    # if int(rb.get("hls") or 0) == 1 or ".m3u8" in url.lower():
    #     return None

    if codec.upper() not in SUPPORTED_CODECS:
        # Nie zabijamy wpisu, tylko oznaczamy kodek w opisie. Radio-Browser nie zawsze rozpoznaje kodek idealnie.
        pass

    tags = parse_tags(rb.get("tags"))
    genre = tags[0] if tags else "Radio-Browser"
    countrycode = clean_text(rb.get("countrycode"))
    country = "Polska" if countrycode.upper() == "PL" else (clean_text(rb.get("country")) or "Polska")
    state = clean_text(rb.get("state"))
    bitrate = rb.get("bitrate", "")
    try:
        bitrate = str(int(bitrate)) if int(bitrate or 0) > 0 else ""
    except Exception:
        bitrate = ""

    desc_parts = ["Źródło: Radio-Browser"]
    if country:
        desc_parts.append(country)
    if state:
        desc_parts.append(state)
    if codec:
        desc_parts.append("codec: %s" % codec)
    if bitrate:
        desc_parts.append("%s kbps" % bitrate)
    votes = rb.get("votes")
    clicks = rb.get("clickcount")
    if votes is not None:
        desc_parts.append("votes: %s" % votes)
    if clicks is not None:
        desc_parts.append("clicks: %s" % clicks)

    return {
        "name": name,
        "url": url,
        "genre": genre,
        "group": "Radio-Browser Polska",
        "country": country,
        "language": "Polski",
        "bitrate": bitrate,
        "description": "; ".join(desc_parts) + ".",
        "homepage": clean_text(rb.get("homepage")),
        "picon": "",
        "picon_url": clean_text(rb.get("favicon")),
        "metadata_album_key": "",
        "metadata_artist_key": "",
        "metadata_cover_key": "",
        "metadata_program_key": "",
        "metadata_text_key": "",
        "metadata_title_key": "",
        "metadata_type": "auto",
        "metadata_url": "",
    }


def load_existing(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("stations.json musi być listą JSON")
    return data


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(description="Import polskich stacji z Radio-Browser do NeoRadio stations.json")
    parser.add_argument("--input", default=DEFAULT_STATIONS_PATH, help="ścieżka do obecnego stations.json")
    parser.add_argument("--output", default=None, help="ścieżka wyjściowa; domyślnie nadpisuje input")
    parser.add_argument("--limit", type=int, default=100000, help="maksymalny limit API Radio-Browser")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path

    if not os.path.exists(input_path):
        raise SystemExit("Nie znaleziono pliku: %s" % input_path)

    existing = load_existing(input_path)
    before = len(existing)

    url_keys = set()
    name_url_keys = set()
    name_keys = set()
    for st in existing:
        u = norm_url(st.get("url", ""))
        n = norm_name(st.get("name", ""))
        if u:
            url_keys.add(u)
        if n and u:
            name_url_keys.add((n, u))
        if n:
            name_keys.add(n)

    rb_items = fetch_radio_browser_polish(args.limit)

    added = []
    skipped_no_url = 0
    skipped_duplicate = 0
    skipped_bad = 0

    seen_rb_uuid_or_url = set()
    for rb in rb_items:
        uuid = clean_text(rb.get("stationuuid"))
        raw_url = clean_text(rb.get("url_resolved")) or clean_text(rb.get("url"))
        unique_rb = uuid or norm_url(raw_url)
        if unique_rb in seen_rb_uuid_or_url:
            continue
        seen_rb_uuid_or_url.add(unique_rb)

        mapped = map_station(rb)
        if not mapped:
            if not raw_url:
                skipped_no_url += 1
            else:
                skipped_bad += 1
            continue

        n = norm_name(mapped.get("name"))
        u = norm_url(mapped.get("url"))

        if not u:
            skipped_no_url += 1
            continue

        # Najważniejsza blokada duplikatów: ten sam stream albo ta sama para nazwa+URL.
        if u in url_keys or (n, u) in name_url_keys:
            skipped_duplicate += 1
            continue

        url_keys.add(u)
        name_url_keys.add((n, u))
        name_keys.add(n)
        added.append(mapped)

    # Sortowanie dodanych: czytelnie po nazwie, bez ruszania starej kolejności.
    added.sort(key=lambda s: norm_name(s.get("name")))
    result = existing + added

    write_json(output_path, result)

    report_path = os.path.splitext(output_path)[0] + "_radio_browser_import_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("NeoRadio Radio-Browser Polish import report\n")
        f.write("=========================================\n")
        f.write("Plik wejściowy: %s\n" % input_path)
        f.write("Plik wyjściowy: %s\n" % output_path)
        f.write("Stacje przed: %s\n" % before)
        f.write("Pobrane wpisy Radio-Browser: %s\n" % len(rb_items))
        f.write("Dodane nowe stacje: %s\n" % len(added))
        f.write("Duplikaty pominięte: %s\n" % skipped_duplicate)
        f.write("Pominięte bez URL: %s\n" % skipped_no_url)
        f.write("Pominięte techniczne/błędne: %s\n" % skipped_bad)
        f.write("Stacje po imporcie: %s\n" % len(result))

    print("\nGotowe.")
    print("Stacje przed:", before)
    print("Dodane nowe stacje:", len(added))
    print("Stacje po imporcie:", len(result))
    print("Raport:", report_path)


if __name__ == "__main__":
    main()
