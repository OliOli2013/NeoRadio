# NeoRadio 2.0 — instrukcja aktualizacji GitHub

To jest paczka typu PATCH ONLY. Nie kasuj całego repozytorium.

## Co zrobić

1. Rozpakuj ZIP.
2. Skopiuj pliki do lokalnego repozytorium NeoRadio z nadpisaniem istniejących plików.
3. Nie usuwaj plików, których nie ma w tej paczce, np. `LICENSE`, `.gitignore`, `docs/`, `build/`, stare changelogi albo inne pliki pomocnicze.
4. W GitKraken sprawdź, czy nie ma czerwonych usunięć plików typu `README.txt`.
5. Jeżeli GitKraken pokazuje usunięcie `README.txt`, przywróć plik przed commitem.
6. Commit: `NeoRadio 2.0 update`.
7. Push na `main`.
8. Do GitHub Releases wrzuć jako assety:
   - `enigma2-plugin-extensions-neoradio_all.ipk`
   - `enigma2-plugin-extensions-neoradio_2.0_all.ipk`
   - `neoradio_repo.tar.gz`
   - `neoradio_repo_2.0.tar.gz`

## Najważniejsze pliki w repo

- `manifest.json`
- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py`
- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json`
- `release/CONTROL/control`
- `release/CONTROL/postinst`
- `release/enigma2-plugin-extensions-neoradio_all.ipk`
- `release/enigma2-plugin-extensions-neoradio_2.0_all.ipk`
- `README.md`
- `README.txt`

## Naprawa, jeśli GitKraken pokazuje usunięcie README.txt

W terminalu w katalogu repo:

```sh
git restore README.txt
```

albo, jeśli plik został już usunięty i nie wraca:

```sh
git checkout origin/main -- README.txt
```

Potem ponownie skopiuj `README.txt` z tej paczki.
