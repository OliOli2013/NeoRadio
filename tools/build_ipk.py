#!/usr/bin/env python3
from __future__ import print_function
import hashlib
import os
import shutil
import sys
import tarfile
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKGROOT = os.path.join(ROOT, 'pkgroot')
CONTROL_DIR = os.path.join(ROOT, 'release', 'CONTROL')
OUTPUT_DIR = os.path.join(ROOT, 'releases')
PACKAGE = 'enigma2-plugin-extensions-neoradio'
VERSION = '3.0.0'
OUTPUT = os.path.join(OUTPUT_DIR, '%s_%s_all.ipk' % (PACKAGE, VERSION))


def tar_filter(info):
    parts = info.name.split('/')
    base = parts[-1] if parts else info.name
    if '__pycache__' in parts or base.endswith(('.pyc', '.pyo', '.orig', '.part', '.tmp')):
        return None
    return info


def add_tree(tf, base_dir):
    names = sorted(os.listdir(base_dir))
    for name in names:
        tf.add(os.path.join(base_dir, name), arcname=name, recursive=True, filter=tar_filter)


def write_ar_member(handle, name, data, mode=0o100644):
    # System V/GNU ar fixed-width header, sufficient for IPK member names used here.
    name_field = (name + '/').encode('ascii')
    if len(name_field) > 16:
        raise ValueError('ar member name too long: %s' % name)
    fields = [
        name_field.ljust(16, b' '),
        str(int(time.time())).encode('ascii').ljust(12, b' '),
        b'0'.ljust(6, b' '),
        b'0'.ljust(6, b' '),
        ('%o' % mode).encode('ascii').ljust(8, b' '),
        str(len(data)).encode('ascii').ljust(10, b' '),
        b'`\n',
    ]
    handle.write(b''.join(fields))
    handle.write(data)
    if len(data) & 1:
        handle.write(b'\n')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isdir(PKGROOT):
        raise SystemExit('pkgroot missing')
    if not os.path.isfile(os.path.join(CONTROL_DIR, 'control')):
        raise SystemExit('release/CONTROL/control missing')
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    tmp = tempfile.mkdtemp(prefix='neoradio-ipk-')
    try:
        control_tar = os.path.join(tmp, 'control.tar.gz')
        data_tar = os.path.join(tmp, 'data.tar.gz')
        with tarfile.open(control_tar, 'w:gz', format=tarfile.GNU_FORMAT) as tf:
            add_tree(tf, CONTROL_DIR)
        with tarfile.open(data_tar, 'w:gz', format=tarfile.GNU_FORMAT) as tf:
            add_tree(tf, PKGROOT)
        members = [
            ('debian-binary', b'2.0\n'),
            ('control.tar.gz', open(control_tar, 'rb').read()),
            ('data.tar.gz', open(data_tar, 'rb').read()),
        ]
        part = OUTPUT + '.part'
        with open(part, 'wb') as out:
            out.write(b'!<arch>\n')
            for name, data in members:
                write_ar_member(out, name, data)
        os.replace(part, OUTPUT)
        print(OUTPUT)
        print('size=%d' % os.path.getsize(OUTPUT))
        print('sha256=%s' % sha256(OUTPUT))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
