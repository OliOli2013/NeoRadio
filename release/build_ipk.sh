#!/usr/bin/env bash
set -euo pipefail
VERSION="${1:-1.2.0}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PKGROOT="$ROOT_DIR/pkgroot"
WORKDIR="$ROOT_DIR/release/out/build_${VERSION}"
OUTIPK="$ROOT_DIR/release/out/enigma2-plugin-extensions-neoradio_${VERSION}_all.ipk"
mkdir -p "$ROOT_DIR/release/out"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/control"
cp "$ROOT_DIR/release/CONTROL/control" "$WORKDIR/control/control"
sed -i "s/^Version: .*/Version: ${VERSION}/" "$WORKDIR/control/control"
(
  cd "$WORKDIR/control"
  tar -czf "$WORKDIR/control.tar.gz" ./control
)
(
  cd "$PKGROOT"
  tar -czf "$WORKDIR/data.tar.gz" .
)
printf '2.0
' > "$WORKDIR/debian-binary"
rm -f "$OUTIPK"
(
  cd "$WORKDIR"
  ar r "$OUTIPK" debian-binary control.tar.gz data.tar.gz >/dev/null 2>&1
)
echo "Built: $OUTIPK"
