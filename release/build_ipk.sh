#!/bin/sh
set -eu
HERE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 "$HERE/tools/static_audit.py"
python3 "$HERE/tools/build_ipk.py"
