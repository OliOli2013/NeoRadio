# NeoRadio 2.0 - instrukcja aktualizacji GitHub

Ta paczka jest przygotowana na bazie pełnej wersji **NeoRadio 1.3.9**, a nie starej 1.3.3.

## Wrzucenie do repo

1. Rozpakuj ZIP.
2. Skopiuj zawartość do istniejącego repo `NeoRadio` z nadpisaniem plików.
3. Nie kasuj pozostałych starych plików repo.
4. Sprawdź w GitKraken, żeby nie było czerwonych usunięć typu `README.txt`, `LICENSE`, `docs/`, `build/` itd.
5. Commit: `NeoRadio 2.0 update from 1.3.9 base`.
6. Push do `main`.

## GitHub Releases

Po push utwórz nowy release:

- tag: `v2.0`
- title: `NeoRadio v2.0`
- target: `main`
- asset główny: `enigma2-plugin-extensions-neoradio_all.ipk`
- asset dodatkowy: `enigma2-plugin-extensions-neoradio_2.0_all.ipk`

## Dane techniczne

- baza startowa: `enigma2-plugin-extensions-neoradio_1.3.9_all.ipk`
- finalna wersja: `2.0`
- stacje po aktualizacji: `5843`
- dodane nowe stacje z bukietu: `148`
- postinst czyści tymczasowe pliki NeoRadio z `/tmp`
