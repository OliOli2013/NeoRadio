#!/usr/bin/env bash
set -euo pipefail
VERSION="${1:-1.2.7}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PKGROOT="$ROOT_DIR/pkgroot"
WORKDIR="$ROOT_DIR/release/out/build_${VERSION}"
OUTDIR="$ROOT_DIR/release/out"
OUTIPK="$OUTDIR/enigma2-plugin-extensions-neoradio_${VERSION}_all.ipk"
LATESTIPK="$OUTDIR/enigma2-plugin-extensions-neoradio_all.ipk"
LATESTSRC="$OUTDIR/neoradio_repo.tar.gz"
mkdir -p "$OUTDIR"
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
rm -f "$OUTIPK" "$LATESTIPK"
(
  cd "$WORKDIR"
  ar r "$OUTIPK" debian-binary control.tar.gz data.tar.gz >/dev/null 2>&1
)
cp -f "$OUTIPK" "$LATESTIPK"
tar --exclude="release/out" -czf "$LATESTSRC" -C "$ROOT_DIR" pkgroot README.md LICENSE .gitignore manifest.json release

echo "Built versioned IPK: $OUTIPK"
echo "Built latest IPK:    $LATESTIPK"
echo "Built latest source: $LATESTSRC"
