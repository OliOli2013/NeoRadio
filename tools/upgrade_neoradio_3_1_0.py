#!/usr/bin/env python3
# coding: utf-8
"""Upgrade the checked-out upstream NeoRadio 3.0.0 sources to the 3.1.0 UI release.
Works on a local clone; makes no network requests and does not touch user settings.
"""
from __future__ import print_function
import os
import re
import sys
import shutil
import xml.etree.ElementTree as ET

VERSION = '3.1.0'
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLUGIN = os.path.join(BASE, 'pkgroot', 'usr', 'lib', 'enigma2', 'python', 'Plugins', 'Extensions', 'NeoRadio', 'plugin.py')
CONTROL = os.path.join(BASE, 'release', 'CONTROL', 'control')
IPK_BUILDER = os.path.join(BASE, 'tools', 'build_ipk.py')
AUDIT = os.path.join(BASE, 'tools', 'static_audit.py')
CI = os.path.join(BASE, '.github', 'workflows', 'build.yml')
README = os.path.join(BASE, 'README.md')
GITIGNORE = os.path.join(BASE, '.gitignore')
MARKER = '<!-- NeoRadio 3.1.0 UI refresh -->'


def replace_exact(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise RuntimeError('%s: oczekiwano jednego miejsca, znaleziono %s. Nie nadpisuję pliku.' % (label, count))
    return src.replace(old, new, 1)


def new_plugin(source):
    if 'name="credits_footer"' in source and 'PLUGIN_VERSION = "3.1.0"' in source:
        return source
    source = replace_exact(source, 'PLUGIN_VERSION = "3.0.0"', 'PLUGIN_VERSION = "3.1.0"', 'plugin version')
    # New fixed, independent author signature. Existing dynamic footer_brand/label
    # are not touched: they display metadata origin and can change while playing.
    source = replace_exact(source,
        '        self["footer_brand"] = Label(text_type(""))',
        '        self["credits_footer"] = Label(u"NeoRadio %s   |   Paweł Pawełek   |   AIO Team   |   Enigma2" % PLUGIN_VERSION)\n'
        '        self["footer_brand"] = Label(text_type(""))',
        'credits footer init')

    # Add trims to existing navy cards without moving interactive elements.
    source = replace_exact(source,
        '            <eLabel position="22,20" size="500,840" backgroundColor="#00101a2d" zPosition="0" />',
        '            <eLabel position="22,20" size="500,840" backgroundColor="#00101a2d" zPosition="0" />\n'
        '            <eLabel position="22,20" size="4,840" backgroundColor="#004b9ac8" zPosition="1" />\n'
        '            <eLabel position="542,20" size="4,600" backgroundColor="#004b9ac8" zPosition="1" />\n'
        '            <eLabel position="542,644" size="790,3" backgroundColor="#003a81ac" zPosition="2" />',
        'FHD accent panels')
    source = replace_exact(source,
        '        <eLabel position="20,20" size="420,560" backgroundColor="#00101a2d" zPosition="0" />',
        '        <eLabel position="20,20" size="420,560" backgroundColor="#00101a2d" zPosition="0" />\n'
        '        <eLabel position="20,20" size="3,560" backgroundColor="#004b9ac8" zPosition="1" />\n'
        '        <eLabel position="460,20" size="3,400" backgroundColor="#004b9ac8" zPosition="1" />\n'
        '        <eLabel position="460,434" size="400,2" backgroundColor="#003a81ac" zPosition="1" />',
        'HD accent panels')

    fhd_anchor = '            <widget name="key_info" position="1362,882" size="296,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />'
    fhd_new = (fhd_anchor + '\n\n'
        '            <eLabel position="22,918" size="1636,2" backgroundColor="#003a81ac" zPosition="1" />\n'
        '            <widget name="credits_footer" position="28,922" size="1624,16" font="Regular;16" foregroundColor="#0096cceb" backgroundColor="#00081418" halign="center" transparent="0" zPosition="2" />')
    source = replace_exact(source, fhd_anchor, fhd_new, 'FHD footer')
    hd_anchor = '        <widget name="key_info" position="850,614" size="220,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />'
    hd_new = (hd_anchor + '\n\n'
        '        <eLabel position="20,642" size="1050,2" backgroundColor="#003a81ac" zPosition="1" />\n'
        '        <widget name="credits_footer" position="24,645" size="1042,14" font="Regular;12" foregroundColor="#0096cceb" backgroundColor="#00081418" halign="center" transparent="0" zPosition="2" />')
    source = replace_exact(source, hd_anchor, hd_new, 'HD footer')
    # Improve text contrast on the yellow remote key, without changing mappings.
    source = replace_exact(source,
        '<widget name="key_yellow" position="542,882" size="240,30" font="Regular;24" foregroundColor="#00000000"',
        '<widget name="key_yellow" position="542,882" size="240,30" font="Regular;24" foregroundColor="#00131b25"',
        'FHD yellow key contrast')
    source = replace_exact(source,
        '<widget name="key_yellow" position="320,614" size="140,24" font="Regular;18" foregroundColor="#00000000"',
        '<widget name="key_yellow" position="320,614" size="140,24" font="Regular;18" foregroundColor="#00131b25"',
        'HD yellow key contrast')
    # Xml validation on all literal embedded skins after modification.
    import ast
    tree = ast.parse(source)
    screens = []
    for node in ast.walk(tree):
        val = getattr(node, 'value', None)
        if isinstance(val, str) and '<screen ' in val:
            elem = ET.fromstring(val.strip())
            screens.append(elem)
    if len(screens) < 4:
        raise RuntimeError('Skin check: expected >= 4 XML screens')
    mains = [e for e in screens if e.attrib.get('name') == 'NeoRadioMain']
    if len(mains) != 2 or any(len(e.findall('.//widget[@name="credits_footer"]')) != 1 for e in mains):
        raise RuntimeError('Skin check: expected exactly one footer in HD and FHD')
    return source


def apply():
    required = (PLUGIN, CONTROL, IPK_BUILDER, AUDIT, CI)
    missing = [p for p in required if not os.path.isfile(p)]
    if missing:
        raise RuntimeError('To narzędzie uruchom w katalogu głównym sklonowanego repozytorium NeoRadio. Brakuje: %s' % missing)
    changes = {}
    old = open(PLUGIN, 'r', encoding='utf-8').read()
    changes[PLUGIN] = new_plugin(old)
    c = open(CONTROL, 'r', encoding='utf-8').read()
    if 'Version: 3.1.0' not in c:
        c = replace_exact(c, 'Version: 3.0.0', 'Version: 3.1.0', 'control version')
        c = c.replace('Description: NeoRadio 3.0.0', 'Description: NeoRadio 3.1.0')
    changes[CONTROL] = c
    b = open(IPK_BUILDER, 'r', encoding='utf-8').read()
    if "VERSION = '3.1.0'" not in b:
        b = replace_exact(b, "VERSION = '3.0.0'", "VERSION = '3.1.0'", 'IPK builder version')
    # Prevent safety copies from entering IPK/DEB payloads.
    if "'.tmp', '.bak'" not in b:
        b = replace_exact(b, "('.pyc', '.pyo', '.orig', '.part', '.tmp')", "('.pyc', '.pyo', '.orig', '.part', '.tmp', '.bak')", 'builder backup filter')
    changes[IPK_BUILDER] = b
    a = open(AUDIT, 'r', encoding='utf-8').read()
    if "check(version == '3.1.0'" not in a:
        a = replace_exact(a, "check(version == '3.0.0'", "check(version == '3.1.0'", 'audit version')
    if 'NeoRadio 3.1 footer verification' not in a:
        old_a = "    check(control.get('Version') == version, 'control/plugin version mismatch')"
        new_a = (old_a + "\n    # NeoRadio 3.1 footer verification\n"
            "    check('self[\"credits_footer\"] = Label' in src, 'missing fixed author footer Label')\n"
            "    check(src.count('name=\"credits_footer\"') == 2, 'footer must exist in HD and FHD skin')")
        a = replace_exact(a, old_a, new_a, 'audit footer assertion')
    changes[AUDIT] = a
    ci = open(CI, 'r', encoding='utf-8').read()
    if 'NeoRadio-3.1.0-IPK-DEB' not in ci:
        ci = ci.replace('3.0.0', '3.1.0')
        ci = replace_exact(ci, '      - name: Validate archive',
            '      - name: Build DEB\n        run: python tools/build_deb.py\n      - name: Validate archive', 'CI build deb')
        ci = replace_exact(ci, '          name: NeoRadio-3.1.0-IPK',
            '          name: NeoRadio-3.1.0-IPK-DEB', 'CI artifact name')
        ci = replace_exact(ci, '          path: releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk',
            '          path: |\n            releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk\n            releases/enigma2-plugin-extensions-neoradio_3.1.0_all.deb', 'CI artifact paths')
    changes[CI] = ci
    if os.path.isfile(README):
        readme = open(README, 'r', encoding='utf-8').read()
        if '## NeoRadio 3.1.0 — UI refresh' not in readme:
            readme = readme.replace('# NeoRadio 3.0.0 for Enigma2', '# NeoRadio 3.1.0 for Enigma2', 1)
            readme = readme.replace('releases/enigma2-plugin-extensions-neoradio_3.0.0_all.ipk', 'releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk', 1)
            readme += ('\n\n## NeoRadio 3.1.0 — UI refresh\n'
                '- A fixed, centered author/version credit beneath remote-control color buttons (HD and FHD).\n'
                '- Subtle cyan section accents; improved yellow-key label contrast.\n'
                '- Existing dynamic source-metadata footer remains unchanged.\n'
                '- Playback, Radio-Browser, favorites, picon lookup, screensaver, audio and settings logic unchanged.\n'
                '- Builds both IPK and DEB. See `README_UPGRADE_3_1_0_PL.md`.\n')
        changes[README] = readme
    if os.path.isfile(GITIGNORE):
        gi = open(GITIGNORE, 'r', encoding='utf-8').read()
        if 'releases/*.deb' not in gi:
            gi += '\nreleases/*.deb\n'
        if '*.before-3.1.0.bak' not in gi:
            gi += '*.before-3.1.0.bak\n'
        changes[GITIGNORE] = gi
    # All-or-none validation before writing. Validate source is compilable.
    compile(changes[PLUGIN], PLUGIN, 'exec')
    for path, updated in changes.items():
        current = open(path, 'r', encoding='utf-8').read()
        if current == updated:
            print('BEZ ZMIAN:', os.path.relpath(path, BASE))
            continue
        # Preserve previous original as a local safety backup (excluded from Git commits).
        bak = path + '.before-3.1.0.bak'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(updated)
        print('POPRAWIONO:', os.path.relpath(path, BASE))
    print('OK: NeoRadio 3.1.0 visual refresh; no playback functions changed.')


if __name__ == '__main__':
    try:
        apply()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
