#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 tools/validate_skins_3_2_1.py
python3 tools/build_packages_3_2_1.py
