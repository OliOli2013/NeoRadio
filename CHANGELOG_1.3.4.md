# NeoRadio 1.3.4

Zmiany przygotowane z paczki `enigma2-plugin-extensions-neoradio_1.3.3_all.ipk`.

## Zmienione pliki

- `usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py`
- `usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json`
- `usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/README.md`
- `usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/README.txt`
- `usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/github_manifest_example.json`
- `control/control`

## Najważniejsze zmiany

- dodane stacje radiowe
- usunięte duplikaty po URL oraz po nazwie stacji w obrębie języka
- ujednolicone kraje/bukiety, m.in. Polska/Poland/Polen -> Polska
- dodane filtry języków stacji: Polski, Arabski, Francuski, Niemiecki, Włoski, Inne
- Niebieski przycisk otwiera filtry/bukiety, a przycisk Menu otwiera ustawienia bez przewijania długiej listy filtrów
- zapamiętywany jest ostatni filtr, ostatnia stacja, URL ostatniej stacji i historia ostatnio odtwarzanych stacji
- historia odtwarzania zapisywana jest w `/etc/enigma2/neoradio_history.json`
