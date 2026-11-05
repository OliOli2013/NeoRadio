#!/usr/bin/env python3
# coding: utf-8
"""Create an Enigma2 DEB from a validated ar-format IPK.
Both OPKG IPK (ar variant) and Debian DEB share the standard ar layout:
  debian-binary, control.tar.gz and data.tar.gz.
"""
import os
import sys
import shutil
import subprocess
import hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERSION = '3.1.0'
BASE = os.path.join(ROOT, 'releases', 'enigma2-plugin-extensions-neoradio_%s_all' % VERSION)
source = BASE + '.ipk'
target = BASE + '.deb'
if not os.path.isfile(source):
    sys.exit('Missing IPK: run python3 tools/build_ipk.py first')
with open(source, 'rb') as f:
    header = f.read(8)
if header != b'!<arch>\n':
    sys.exit('Input IPK must be a GNU ar archive, not tar/ipk.')
shutil.copyfile(source, target)
if shutil.which('dpkg-deb'):
    subprocess.check_call(['dpkg-deb', '--info', target], stdout=subprocess.DEVNULL)
h = hashlib.sha256()
with open(target, 'rb') as f:
    for block in iter(lambda: f.read(1024 * 1024), b''):
        h.update(block)
print('Created %s, SHA256: %s' % (target, h.hexdigest()))
