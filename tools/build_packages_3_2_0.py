#!/usr/bin/env python3
from __future__ import print_function
import io, os, tarfile, hashlib, shutil, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKGROOT = ROOT / 'pkgroot'
CONTROL_DIR = ROOT / 'release' / 'CONTROL'
OUTDIR = ROOT / 'releases'
OUTDIR.mkdir(exist_ok=True)
PKGNAME = 'enigma2-plugin-extensions-neoradio'
VERSION = '3.2.0'
BASENAME = f'{PKGNAME}_{VERSION}_all'


def make_targz(source_dir, target_file):
    with tarfile.open(target_file, 'w:gz') as tar:
        for path in sorted(source_dir.rglob('*')):
            arcname = path.relative_to(source_dir)
            tar.add(path, arcname=str(arcname), recursive=False)


def build_ar_package(out_file):
    import subprocess, tempfile
    with tempfile.TemporaryDirectory(prefix='neoradio-ar-') as tmp:
        tmp = Path(tmp)
        debian_binary = tmp/'debian-binary'
        debian_binary.write_text('2.0\n', encoding='ascii')
        control_tar = tmp/'control.tar.gz'
        data_tar = tmp/'data.tar.gz'
        make_targz(CONTROL_DIR, control_tar)
        make_targz(PKGROOT, data_tar)
        # use system ar for compatibility
        cmd = ['ar', 'rc', str(out_file), str(debian_binary), str(control_tar), str(data_tar)]
        subprocess.check_call(cmd)


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ipk = OUTDIR / f'{BASENAME}.ipk'
    deb = OUTDIR / f'{BASENAME}.deb'
    for p in (ipk, deb):
        if p.exists():
            p.unlink()
        build_ar_package(p)
        print(str(p))
        print('size=%d' % p.stat().st_size)
        print('sha256=%s' % sha256(p))
    # upload-first manifest for manual publication
    ipk_url = f'https://github.com/OliOli2013/NeoRadio/releases/download/v{VERSION}/{ipk.name}'
    manifest = {
        'name': 'NeoRadio',
        'version': VERSION,
        'url': ipk_url,
        'ipk': ipk_url,
        'sha256': sha256(ipk),
        'changelog': 'Three selectable skins: default, retro radio, future radio. Reopen plugin after changing the skin.'
    }
    (OUTDIR / f'manifest_{VERSION}_UPLOAD_FIRST.json').write_text(__import__('json').dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Manifest created under releases/, upload release assets first.')

if __name__ == '__main__':
    main()
