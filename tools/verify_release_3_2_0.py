#!/usr/bin/env python3
from __future__ import print_function
import hashlib, os, py_compile, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py'
SKINS = ROOT / 'pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/skins'
REQUIRED = ['skin_future_fhd.png','skin_future_hd.png','skin_retro_fhd.png','skin_retro_hd.png']

py_compile.compile(str(PLUGIN), doraise=True)
text = PLUGIN.read_text(encoding='utf-8', errors='ignore')
assert 'PLUGIN_VERSION = "3.2.0"' in text
assert 'choose_skin_theme' in text
assert 'menu_skin_theme' in text
for name in REQUIRED:
    path = SKINS / name
    assert path.exists(), 'Missing %s' % name
print('NeoRadio 3.2.0 verify: PASS')
print('plugin=', PLUGIN)
print('skin_assets=', len(REQUIRED))
