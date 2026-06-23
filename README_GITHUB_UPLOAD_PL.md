# NeoRadio v2.1 — paczka do GitHuba

Ta paczka jest hotfixem wersji 2.1. Numer wersji pozostaje 2.1.

## Co wrzucić

Skopiuj zawartość tej paczki do głównego katalogu repo NeoRadio z nadpisaniem plików. Nie kasuj ręcznie innych plików repo.

Najważniejsze pliki:

- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py`
- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json` — pusty, bo baza ma być pobierana online
- `release/CONTROL/postinst`
- `manifest.json`
- `release/enigma2-plugin-extensions-neoradio_all.ipk`
- `release/enigma2-plugin-extensions-neoradio_2.1_all.ipk`

## Działanie

Po instalacji `postinst` czyści `/tmp` oraz usuwa stary cache Radio-Browser z `/etc/enigma2`. Przy pierwszym uruchomieniu NeoRadio pobiera świeżą listę stacji z Radio-Browser zgodnie z językiem/locale tunera.
