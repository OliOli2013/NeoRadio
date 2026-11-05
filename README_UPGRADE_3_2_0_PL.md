# NeoRadio 3.2.0 — trzy skiny interfejsu

Pakiet dodaje trzy skiny do wyboru:
- domyślny
- retro radio
- radio przyszłości

## Co zostało przygotowane
- zaktualizowany `plugin.py`
- nowe tła skinów w katalogu `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/skins/`
- zaktualizowany plik `release/CONTROL/control`
- skrypty do budowy pakietów IPK/DEB i weryfikacji

## Wybór skinu we wtyczce
`Menu -> Skin interfejsu`

Po zapisaniu skinu należy zamknąć i ponownie uruchomić NeoRadio.

## Budowa pakietów
```bash
bash tools/build_release_3_2_0.sh
python3 tools/verify_release_3_2_0.py
```
