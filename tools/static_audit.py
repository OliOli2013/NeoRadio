#!/usr/bin/env python3
from __future__ import print_function
import ast
import json
import os
import py_compile
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLUGIN_DIR = os.path.join(ROOT, 'pkgroot', 'usr', 'lib', 'enigma2', 'python', 'Plugins', 'Extensions', 'NeoRadio')
PLUGIN = os.path.join(PLUGIN_DIR, 'plugin.py')
CONTROL = os.path.join(ROOT, 'release', 'CONTROL', 'control')
ERRORS = []
NOTES = []


def check(condition, message):
    if not condition:
        ERRORS.append(message)


def parse_control(path):
    out = {}
    for raw in open(path, 'r', encoding='utf-8').read().splitlines():
        if ':' in raw:
            k, v = raw.split(':', 1)
            out[k.strip()] = v.strip()
    return out


def walk_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
        for name in files:
            if name.lower().endswith(('.py', '.md', '.txt', '.json', '.sh', '.yml', '.yaml')) or name == 'control':
                yield os.path.join(base, name)


def main():
    check(os.path.isfile(PLUGIN), 'plugin.py missing')
    check(os.path.isfile(CONTROL), 'control missing')
    if ERRORS:
        finish()

    try:
        fd, compile_target = tempfile.mkstemp(prefix='neoradio-audit-', suffix='.pyc')
        os.close(fd)
        try:
            py_compile.compile(PLUGIN, cfile=compile_target, doraise=True)
        finally:
            try:
                os.unlink(compile_target)
            except Exception:
                pass
    except Exception as e:
        ERRORS.append('Python 3 compile failed: %s' % e)

    src = open(PLUGIN, 'r', encoding='utf-8').read()
    tree = ast.parse(src)
    version_match = re.search(r'^PLUGIN_VERSION\s*=\s*[\"\']([^\"\']+)', src, re.M)
    version = version_match.group(1) if version_match else ''
    control = parse_control(CONTROL)
    check(version == '3.1.0', 'unexpected PLUGIN_VERSION: %s' % version)
    check(control.get('Version') == version, 'control/plugin version mismatch')
    # NeoRadio 3.1 footer verification
    check('self["credits_footer"] = Label' in src, 'missing fixed author footer Label')
    check(src.count('name="credits_footer"') == 2, 'footer must exist in HD and FHD skin')
    check(control.get('Package') == 'enigma2-plugin-extensions-neoradio', 'unexpected package name')
    check('RADIO_BROWSER_ONLY_MODE = False' in src, 'Radio-Browser-only mode must be disabled')
    m = re.search(r'^RADIO_BROWSER_DEFAULT_LIMIT\s*=\s*(\d+)', src, re.M)
    check(bool(m) and int(m.group(1)) <= 2000, 'Radio-Browser default limit too large')
    check('class NeoRadioSaver' not in src, 'legacy NeoRadioSaver class still present')
    check('--no-check-certificate' not in src, 'insecure TLS bypass still present')
    check('wget ' not in src and "wget\\n" not in src, 'shell wget reference still present in plugin.py')

    # Parse every embedded Enigma2 skin XML string.
    skins = []
    for node in ast.walk(tree):
        value = getattr(node, 'value', None)
        if isinstance(value, str) and '<screen ' in value:
            value = value.strip()
            if value not in skins:
                skins.append(value)
    check(len(skins) >= 4, 'expected HD/FHD main + About skins')
    for idx, xml_text in enumerate(skins):
        try:
            root = ET.fromstring(xml_text)
            names = [w.attrib.get('name') for w in root.findall('.//widget') if w.attrib.get('name')]
            dups = sorted(set(n for n in names if names.count(n) > 1))
            check(not dups, 'duplicate widget names in skin %s: %s' % (idx, ', '.join(dups)))
        except Exception as e:
            ERRORS.append('skin XML parse failed %s: %s' % (idx, e))

    required = ['plugin.png', 'icon.png', 'cover_default.png', 'visualradio.png', 'radio_fallback.png', 'website_qr.png', 'stations.json']
    for name in required:
        check(os.path.isfile(os.path.join(PLUGIN_DIR, name)), 'required asset missing: %s' % name)

    try:
        data = json.load(open(os.path.join(PLUGIN_DIR, 'stations.json'), 'r', encoding='utf-8'))
        check(isinstance(data, list), 'stations.json must contain a JSON list')
    except Exception as e:
        ERRORS.append('stations.json invalid: %s' % e)

    # Optional but useful image integrity check.
    try:
        from PIL import Image
        png_count = 0
        for base, dirs, files in os.walk(PLUGIN_DIR):
            for name in files:
                if name.lower().endswith('.png'):
                    path = os.path.join(base, name)
                    try:
                        im = Image.open(path)
                        im.verify()
                        png_count += 1
                    except Exception as e:
                        ERRORS.append('invalid PNG %s: %s' % (os.path.relpath(path, ROOT), e))
        NOTES.append('verified_png=%d' % png_count)
    except Exception:
        NOTES.append('Pillow not available; PNG verification skipped')

    bad_refs = []
    for path in walk_text_files():
        # Radio-Browser station homepages are external data, not project links.
        # Do not fail CI solely because a station has a social-media homepage.
        if os.path.normpath(path) == os.path.normpath(os.path.join(PLUGIN_DIR, 'stations.json')):
            continue
        try:
            text = open(path, 'r', encoding='utf-8', errors='ignore').read().lower()
        except Exception:
            continue
        # Audit file is allowed to mention what was removed.
        if os.path.basename(path) in ('AUDIT_3.0.0_PL.md', 'static_audit.py'):
            continue
        if 'facebook.com' in text or 'fb.com' in text or 'facebook group' in text or 'grupa facebook' in text:
            bad_refs.append(os.path.relpath(path, ROOT))
    check(not bad_refs, 'Facebook reference(s) remain: %s' % ', '.join(bad_refs))

    finish(version)


def finish(version=''):
    if ERRORS:
        print('NeoRadio static audit: FAIL')
        for item in ERRORS:
            print(' -', item)
        raise SystemExit(1)
    print('NeoRadio static audit: PASS')
    if version:
        print('version=%s' % version)
    for item in NOTES:
        print(item)


if __name__ == '__main__':
    main()
