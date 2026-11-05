# NeoRadio 3.2.1 — pełna naprawa skinów do GitKraken

## Co poprawiono
Poprzednie retro/future 3.2.0 nakładały obrazy pod nieprzezroczystymi widgetami, przez co na ekranie były głównie czarne prostokąty. W 3.2.1 są osobne skiny Enigma2 z oryginalną estetyką referencyjnych grafik, osobno HD/FHD. Dane stacji, picony, przyciski i wskaźniki pozostają dynamiczne.

## Instalacja plików do repozytorium (terminal GitKrakena)
W katalogu `~/AIO projekt/NeoRadio`:

```bash
unzip -o "$HOME/Pobrane/NEORADIO_3.2.1_KOMPLET_GITKRAKEN.zip" -d .
python3 tools/validate_skins_3_2_1.py
bash tools/build_release_3_2_1.sh
git diff --check
git status --short
```

**Commit i Push wykonaj ręcznie w GitKrakenie.** Proponowany commit:
`NeoRadio 3.2.1: rebuild Retro and Future UI with real Enigma2 layouts`

## Pliki instalacyjne
Pakiety zbudowane z bieżącego lokalnego repozytorium znajdują się w `releases/`:
- `enigma2-plugin-extensions-neoradio_3.2.1_all.ipk`
- `enigma2-plugin-extensions-neoradio_3.2.1_all.deb`

Po pomyślnych testach w tunerze utwórz GitHub Release `v3.2.1` i dodaj oba pliki **bez zmiany ich nazw**.

**Dopiero gdy pliki Release są opublikowane**, możesz skopiować wygenerowany `releases/manifest_3.2.1_UPLOAD_AFTER_RELEASE.json` do głównego `manifest.json`, sprawdzić URL i sumę SHA256, zatwierdzić zmianę w GitKrakenie i wykonać Push ręcznie.

## Uwagi bezpieczeństwa
- Nowe pliki źródłowe nie modyfikują `stations.json`, `favorites.json`, historii ani lokalnych stacji.
- Po zmianie skina zamknij i ponownie otwórz wtyczkę.
- Nie publikuj aktualizacji jako stabilnej, dopóki nie sprawdzisz obu skórek na prawdziwym odbiorniku Enigma2.
