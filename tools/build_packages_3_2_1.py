#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build real OPKG ar/IPK and Debian .deb from the complete pkgroot checkout."""
from __future__ import print_function
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PKGROOT=ROOT/'pkgroot'
CONTROL_DIR=ROOT/'release/CONTROL'
DEST=ROOT/'releases'
VERSION='3.2.1'
NAME='enigma2-plugin-extensions-neoradio_%s_all'%VERSION


def include(path):
    if any(name in ('__pycache__','.git','.dist') for name in path.parts):return False
    if path.name.endswith(('.pyc','.pyo','.tmp','.part','.orig','.bak','.swp')):return False
    return True


def tar_bytes(base):
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w:gz',format=tarfile.GNU_FORMAT) as tf:
        for item in sorted(base.rglob('*')):
            if not include(item.relative_to(base)):continue
            arc=item.relative_to(base).as_posix()
            info=tf.gettarinfo(str(item),arcname=arc)
            info.uid=0;info.gid=0;info.uname='root';info.gname='root'
            if item.name=='postinst':info.mode=0o755
            if item.is_file():
                with open(item,'rb') as f:tf.addfile(info,f)
            else:tf.addfile(info)
    return buffer.getvalue()


def ar_member(out,name,blob):
    # GNU ar format: constant-size ASCII header + content + odd-byte padding.
    name_field=(name+'/').encode('ascii').ljust(16,b' ')
    header=(name_field+
            b'0'.ljust(12,b' ')+
            b'0'.ljust(6,b' ')+
            b'0'.ljust(6,b' ')+
            b'100644'.ljust(8,b' ')+
            str(len(blob)).encode('ascii').ljust(10,b' ')+
            b'`\n')
    assert len(header)==60
    out.write(header);out.write(blob)
    if len(blob)%2:out.write(b'\n')


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    if not (PKGROOT/'usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py').exists():
        raise SystemExit('Brak pkgroot/plugin.py')
    DEST.mkdir(exist_ok=True)
    control_blob=tar_bytes(CONTROL_DIR)
    data_blob=tar_bytes(PKGROOT)
    ipk=DEST/(NAME+'.ipk');deb=DEST/(NAME+'.deb')
    for path in (ipk,deb):
        with open(str(path)+'.part','wb') as out:
            out.write(b'!<arch>\n')
            ar_member(out,'debian-binary',b'2.0\n')
            ar_member(out,'control.tar.gz',control_blob)
            ar_member(out,'data.tar.gz',data_blob)
        os.replace(str(path)+'.part',path)
        print('%s, size=%s, SHA256=%s'%(path,path.stat().st_size,sha(path)))
        if shutil.which('dpkg-deb'):
            subprocess.check_call(['dpkg-deb','--info',str(path)],stdout=subprocess.DEVNULL)
    upload={
        'name':'NeoRadio','version':VERSION,
        'ipk':'https://github.com/OliOli2013/NeoRadio/releases/download/v%s/%s'%(VERSION,ipk.name),
        'release_page':'https://github.com/OliOli2013/NeoRadio/releases/tag/v%s'%VERSION,
        'sha256':sha(ipk),
        'changelog':'NeoRadio 3.2.1: restored real Retro/Future interface artwork, independent HD/FHD layouts, functional EQ indicators and dynamic metadata. Default skin retained.'
    }
    manifest=DEST/('manifest_%s_UPLOAD_AFTER_RELEASE.json'%VERSION)
    manifest.write_text(json.dumps(upload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['%s  %s'%(sha(p),p.name) for p in (ipk,deb)]
    (DEST/('SHA256_%s.txt'%VERSION)).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Manifest przygotowany, nie podmieniaj pliku manifest.json przed publikacją GitHub Release.')

if __name__=='__main__':main()
