# NeoRadio v2.1 — gotowe pliki do GitHub

1. Rozpakuj tę paczkę.
2. Skopiuj zawartość do głównego katalogu repozytorium NeoRadio.
3. Nadpisz istniejące pliki, ale nie kasuj plików repo, których nie ma w tej paczce.
4. Zrób commit i push na `main`.
5. Utwórz GitHub Release z tagiem `v2.1`.
6. Do release dodaj jako asset:
   - `enigma2-plugin-extensions-neoradio_all.ipk`
   - opcjonalnie `enigma2-plugin-extensions-neoradio_2.1_all.ipk`
   - opcjonalnie `neoradio_repo.tar.gz`

Najważniejsze pliki:

- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py`
- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json`
- `release/CONTROL/control`
- `release/CONTROL/postinst`
- `manifest.json`
- `release/enigma2-plugin-extensions-neoradio_all.ipk`
- `releases/enigma2-plugin-extensions-neoradio_all.ipk`

Nie twórz release na starym tagu. Nowy tag ma być: `v2.1`.
