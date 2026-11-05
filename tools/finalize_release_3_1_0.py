#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enable in-plugin NeoRadio 3.0 -> 3.1.0 update ONLY after verifying public release.

The locally built IPK and DEB must be published under the exact release tag and
filenames. Both remote assets are downloaded through HTTPS, streaming into SHA256.
The root manifest.json is replaced atomically only when the hashes match.
"""
from __future__ import print_function
import hashlib
import io
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPO = 'OliOli2013/NeoRadio'
VERSION = '3.1.0'
TAG = 'v' + VERSION
PACKAGE = 'enigma2-plugin-extensions-neoradio'
BASENAME = '%s_%s_all' % (PACKAGE, VERSION)
RELEASE = 'https://github.com/%s/releases/download/%s/' % (REPO, TAG)
RELEASE_PAGE = 'https://github.com/%s/releases/tag/%s' % (REPO, TAG)
MAX_BYTES = 64 * 1024 * 1024


def sha256_and_size(path):
    h = hashlib.sha256()
    size = 0
    with open(path, 'rb') as stream:
        while True:
            chunk = stream.read(128 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValueError('Zbyt duzy pakiet: %s' % path)
            h.update(chunk)
    if size < 1024:
        raise ValueError('Plik jest pusty lub zbyt maly: %s' % path)
    return h.hexdigest(), size


def check_control_ar(path):
    import tarfile
    entries = {}
    with open(path, 'rb') as handle:
        if handle.read(8) != b'!<arch>\n':
            raise ValueError('Brak naglowka archiwum ar: %s' % path)
        while True:
            header = handle.read(60)
            if not header:
                break
            if len(header) != 60 or header[58:] != b'`\n':
                raise ValueError('Uszkodzony naglowek ar: %s' % path)
            name = header[:16].decode('ascii').strip().rstrip('/')
            length = int(header[48:58].decode('ascii').strip())
            if length > MAX_BYTES:
                raise ValueError('Za duzy element ar: %s' % name)
            data = handle.read(length)
            if len(data) != length:
                raise ValueError('Niekompletny element: %s' % name)
            if length % 2:
                handle.read(1)
            entries[name] = data
    if entries.get('debian-binary') != b'2.0\n':
        raise ValueError('Niepoprawna wersja archiwum')
    if 'data.tar.gz' not in entries or 'control.tar.gz' not in entries:
        raise ValueError('Brakuje control.tar.gz lub data.tar.gz')
    with tarfile.open(fileobj=io.BytesIO(entries['control.tar.gz']), mode='r:gz') as tf:
        matches = [x for x in tf.getmembers() if os.path.basename(x.name) == 'control' and x.isfile()]
        if len(matches) != 1:
            raise ValueError('Brak pliku control w archiwum')
        control = tf.extractfile(matches[0]).read().decode('utf-8')
        if ('Package: ' + PACKAGE) not in control or ('Version: ' + VERSION) not in control:
            raise ValueError('Pakiet ma niezgodna nazwe lub wersje')


def remote_sha_and_size(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': 'NeoRadio-Release-Verification/3.1.0',
        'Accept': 'application/octet-stream',
    })
    digest = hashlib.sha256()
    size = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            final_url = resp.geturl()
            if not final_url.startswith('https://'):
                raise ValueError('Pobieranie nie zostalo zakonczone przez HTTPS')
            while True:
                chunk = resp.read(128 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError('Zdalny plik przekracza 64 MiB')
    except urllib.error.HTTPError as e:
        raise RuntimeError('GitHub HTTP %s: %s; czy wydanie %s i zalaczniki sa publiczne?' % (e.code, url, TAG))
    except urllib.error.URLError as e:
        raise RuntimeError('Blad pobierania GitHub: %s' % e)
    return digest.hexdigest(), size


def main():
    results = {}
    for extension in ('.ipk', '.deb'):
        name = BASENAME + extension
        local = os.path.join(ROOT, 'releases', name)
        if not os.path.isfile(local):
            raise ValueError('Brak lokalnego pakietu: %s' % local)
        check_control_ar(local)
        local_sha, local_size = sha256_and_size(local)
        url = RELEASE + name
        print('Sprawdzam zdalny plik:', url)
        remote_sha, remote_size = remote_sha_and_size(url)
        if remote_sha != local_sha or remote_size != local_size:
            raise ValueError('ROZNICA SHA256/WIELKOSCI: %s\n  lokalny:  %s (%d B)\n  GitHub:   %s (%d B)' %
                             (name, local_sha, local_size, remote_sha, remote_size))
        print('OK:', name, 'SHA256:', local_sha)
        results[extension] = {'url': url, 'sha256': local_sha, 'size': local_size}
    info = {
        'name': 'NeoRadio',
        'version': VERSION,
        'ipk': results['.ipk']['url'],
        'deb': results['.deb']['url'],
        'release_page': RELEASE_PAGE,
        'project_page': 'https://github.com/OliOli2013/NeoRadio',
        'sha256': results['.ipk']['sha256'],
        'changelog': ('NeoRadio 3.1.0: niezalezna stopka Paweł Pawełek | AIO Team, '
                      'odswiezony interfejs HD/FHD, bez zmian w funkcjach radia.'),
    }
    manifest_path = os.path.join(ROOT, 'manifest.json')
    fd, tmp = tempfile.mkstemp(prefix='.manifest-neoradio-', suffix='.tmp', dir=ROOT)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, manifest_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print('GOTOWE: manifest.json wskazuje opublikowane i zweryfikowane IPK 3.1.0.')
    print('Teraz wykonaj commit/push manifest.json. Stara wtyczka odczyta go z raw.githubusercontent.com.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('BLAD:', e, file=sys.stderr)
        print('Nie zmieniono manifest.json. Najpierw opublikuj pelne IPK/DEB w GitHub Releases.', file=sys.stderr)
        sys.exit(1)
