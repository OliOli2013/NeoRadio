# NeoRadio v2.0 — automatyczne dodanie polskich stacji z Radio-Browser

Ta paczka jest przygotowana tak, aby **dodać ją do GitHuba bez ręcznego uruchamiania skryptu lokalnie**.

## Co zawiera

- `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json`  
  Aktualny plik bazy stacji jako punkt startowy. Zawiera wcześniejsze poprawki ręczne, m.in. Radio Piekary / śląskie radia.

- `tools/import_radio_browser_polish_to_stations.py`  
  Importer polskich stacji z Radio-Browser.

- `.github/workflows/update-neoradio-radiobrowser-pl.yml`  
  GitHub Action, która po wrzuceniu plików na `main` sama pobierze maksymalnie dużą bazę polskich stacji i dopisze je do `stations.json`.

## Co zrobić

1. Rozpakuj ZIP do głównego katalogu repo NeoRadio.
2. Skopiuj pliki z nadpisaniem.
3. Nie kasuj żadnych starych plików repozytorium.
4. Zrób commit i push na `main`.
5. GitHub Actions uruchomi import i zrobi drugi commit z finalnym `stations.json`.

## Czego to nie zmienia

Nie zmienia:

- wersji wtyczki,
- `manifest.json`,
- `control`,
- `plugin.py`,
- paczek IPK,
- stacji z innych krajów.

Importer tylko dopisuje nowe polskie stacje i pomija duplikaty po URL oraz po parze nazwa + URL.

## Gdy workflow nie zrobi commita

Wejdź w GitHub → repo NeoRadio → **Actions** → wybierz workflow:

`NeoRadio - import polskich stacji Radio-Browser`

Kliknij **Run workflow**.

Jeśli GitHub zapyta o uprawnienia, w repo ustaw:

`Settings → Actions → General → Workflow permissions → Read and write permissions`
