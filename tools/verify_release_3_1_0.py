#!/usr/bin/env python3
# coding: utf-8
import os
import tarfile
import subprocess
import hashlib
import json
import io
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VERS = '3.1.0'
FNAME = 'enigma2-plugin-extensions-neoradio_%s_all' % VERS
BASE = os.path.join(ROOT, 'releases', FNAME)

def inspect_ar(path):
    with open(path, 'rb') as f:
        assert f.read(8) == b'!<arch>\n', 'Not a valid ar'
        entries = {}
        while 1:
            h = f.read(60)
            if not h:
                break
            assert len(h) == 60 and h[58:60] == b'`\n', 'Damaged ar'
            name = h[:16].decode('ascii').strip().rstrip('/')
            size = int(h[48:58].decode('ascii').strip())
            data = f.read(size)
            if size % 2:
                f.read(1)
            entries[name] = data
    assert entries.get('debian-binary') == b'2.0\n'
    assert 'control.tar.gz' in entries and 'data.tar.gz' in entries
    with tarfile.open(fileobj=io.BytesIO(entries['control.tar.gz']),mode='r:gz') as t:
        ctrl = next(x for x in t.getmembers() if os.path.basename(x.name) == 'control')
        data = t.extractfile(ctrl).read().decode('utf-8')
        assert 'Version: 3.1.0' in data and 'Package: enigma2-plugin-extensions-neoradio' in data
    with tarfile.open(fileobj=io.BytesIO(entries['data.tar.gz']),mode='r:gz') as t:
        names = t.getnames()
        assert any(x.endswith('/NeoRadio/plugin.py') for x in names)
        assert any(x.endswith('/NeoRadio/stations.json') for x in names)
        assert any(x.endswith('/NeoRadio/plugin.png') for x in names)
    return len(entries['data.tar.gz'])

for ext in ('.ipk','.deb'):
    path = BASE + ext
    size = inspect_ar(path)
    print('VALIDATED',os.path.basename(path),'size=',os.stat(path).st_size,'compressed_data=',size)
manifest = {
    'name':'NeoRadio', 'version':VERS,
    'ipk':'https://github.com/OliOli2013/NeoRadio/releases/download/v%s/%s.ipk' % (VERS,FNAME),
    'deb':'https://github.com/OliOli2013/NeoRadio/releases/download/v%s/%s.deb' % (VERS,FNAME),
    'release_page':'https://github.com/OliOli2013/NeoRadio/releases/tag/v'+VERS,
    'project_page':'https://github.com/OliOli2013/NeoRadio',
    'sha256':hashlib.sha256(open(BASE+'.ipk','rb').read()).hexdigest(),
    'changelog':'NeoRadio 3.1.0: new independent author/version footer in HD and FHD, modern AIO styling, improved key contrast; playback features unchanged.'
}
with open(os.path.join(ROOT,'releases','manifest_3.1.0_UPLOAD_FIRST.json'),'w',encoding='utf-8') as f:
    json.dump(manifest,f,ensure_ascii=False,indent=2)
print('Manifest created under releases/, DO NOT replace root manifest.json until GitHub release v3.1.0 assets are online.')
