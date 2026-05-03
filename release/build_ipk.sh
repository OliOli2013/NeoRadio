#!/bin/sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUT_VERSIONED="$ROOT/enigma2-plugin-extensions-neoradio_1.3.9_all.ipk"
OUT_LATEST="$ROOT/enigma2-plugin-extensions-neoradio_all.ipk"
BUILD_DIR="$ROOT/build"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
tar --numeric-owner --owner=0 --group=0 -C "$ROOT/release/CONTROL" -czf "$BUILD_DIR/control.tar.gz" .
tar --numeric-owner --owner=0 --group=0 -C "$ROOT/pkgroot" -czf "$BUILD_DIR/data.tar.gz" .
printf '2.0\n' > "$BUILD_DIR/debian-binary"
( cd "$BUILD_DIR" && ar r "$OUT_VERSIONED" debian-binary control.tar.gz data.tar.gz )
cp "$OUT_VERSIONED" "$OUT_LATEST"
echo "Built: $OUT_VERSIONED"
echo "Built: $OUT_LATEST"
