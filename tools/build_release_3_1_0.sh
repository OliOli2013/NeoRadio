#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"
python3 tools/upgrade_neoradio_3_1_0.py
python3 tools/static_audit.py
python3 tools/build_ipk.py
python3 tools/build_deb.py
python3 tools/verify_release_3_1_0.py
sha256sum releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk releases/enigma2-plugin-extensions-neoradio_3.1.0_all.deb
