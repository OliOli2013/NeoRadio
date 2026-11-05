#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 tools/verify_release_3_2_0.py
python3 tools/build_packages_3_2_0.py
