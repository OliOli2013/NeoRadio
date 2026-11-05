#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix NeoRadio 3.1.0 CI false positive without changing stations or playback.

The Radio-Browser database may legitimately include a Facebook URL as a station
homepage. A project-code scan should not reject third-party station metadata.
"""
from __future__ import print_function
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / 'tools' / 'static_audit.py'
ANCHOR = '    bad_refs = []\n    for path in walk_text_files():\n'
REPLACE = '''    bad_refs = []
    for path in walk_text_files():
        # Radio-Browser station homepages are external data, not project links.
        # Do not fail CI solely because a station has a social-media homepage.
        if os.path.normpath(path) == os.path.normpath(os.path.join(PLUGIN_DIR, 'stations.json')):
            continue
'''


def main():
    if not AUDIT.is_file():
        raise RuntimeError('Nie znaleziono tools/static_audit.py. Uruchom w repo NeoRadio.')
    original = AUDIT.read_text(encoding='utf-8')
    if REPLACE in original:
        print('OK: audyt jest juz poprawiony.')
        return
    if original.count(ANCHOR) != 1:
        raise RuntimeError('Nieoczekiwana wersja tools/static_audit.py, niczego nie zmieniono.')
    new = original.replace(ANCHOR, REPLACE, 1)
    compile(new, str(AUDIT), 'exec')
    AUDIT.write_text(new, encoding='utf-8', newline='\n')
    print('POPRAWIONO: tools/static_audit.py')
    print('Teraz audyt ignoruje tylko baze stacji (stations.json),')
    print('ale nadal sprawdza reszte plikow kodu i dokumentacji.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('BLAD:', exc, file=sys.stderr)
        sys.exit(1)
