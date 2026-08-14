# NeoRadio 3.0.0 – co wgrać na GitHub

Najbezpieczniej potraktować katalog z tej paczki jako nową czystą zawartość gałęzi `main` (z pozostawieniem katalogu `.git` lokalnego repozytorium).

## Zostaw / wgraj

- `.github/workflows/build.yml`
- `pkgroot/`
- `release/CONTROL/control`
- `release/build_ipk.sh`
- `tools/build_ipk.py`
- `tools/static_audit.py`
- `README.md`
- `README.txt`
- `CHANGELOG_3.0.0.md`
- `AUDIT_3.0.0_PL.md`
- `manifest.json`
- `github_manifest_example.json`
- `LICENSE.md`
- `.gitignore`

## Plik IPK

Gotowego IPK **nie polecam commitować do `main`**, bo binaria niepotrzebnie powiększają historię Git. Wgraj `enigma2-plugin-extensions-neoradio_3.0.0_all.ipk` jako asset do GitHub Release z tagiem `v3.0.0`. `manifest.json` już wskazuje dokładnie na ten asset. Workflow buduje IPK automatycznie i udostępnia go także jako artifact CI.

## Stare pliki, które można usunąć z `main`

Po upewnieniu się, że historia jest w Git, nie są potrzebne równolegle jako aktualna dokumentacja:

- `CHANGELOG_1.3.4.md`
- `CHANGELOG_2.0.md`
- `CHANGELOG_2.1.md`
- wszystkie osobne `CHANGELOG_2.1_*HOTFIX*.md`
- `NeoRadio_2.0_CHANGELOG.txt`
- stare `README_v2.1_PL.md`, `README_GITHUB_*`
- stare przykłady manifestów 1.x/2.0
- stare patch files `neoradio_1.3.5.patch`
- stare build/release copies poprzednich IPK, jeśli nie chcesz przechowywać binariów historycznych na `main`

Nie usuwaj historycznych **GitHub Releases** – historia wydań może pozostać w sekcji Releases nawet jeśli `main` jest uporządkowany.
