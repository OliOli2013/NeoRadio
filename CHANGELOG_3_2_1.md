# NeoRadio 3.2.1 — Retro / Future UI rebuild

## Co zostało naprawione
- Dwa niezależne projekty ekranu Retro oraz Future — prawdziwe tła referencyjnych wizualizacji, a nie zmiana kolorów.
- Usunięto błąd czarnego tła: grafika jest pierwszą warstwą (`ePixmap` z `zPosition=0`); tekst jest rysowany powyżej na przezroczystych widgetach.
- Rzeczywiste, dynamiczne wartości stacji, metadanych ICY/RDS, piconów i regulatorów dźwięku zamiast informacji na stałe wpisanych do PNG.
- Wskaźniki balansu, wysokich i niskich tonów reagujące na wartości -10..+10.
- Niezależne, walidowane layouty HD oraz FHD dla obu nowych motywów.
- Zachowano skin domyślny z NeoRadio 3.2.0 i mechanizm wyboru skina w Menu.
- Nie zmieniono mechanizmów odtwarzania, Radio-Browser, ulubionych, ustawień, aktualizatora i funkcji klawiszy.

## Testowanie
- Walidacja Python 3, struktury XML, geometrii, kompletności PNG i obecności wymaganych komponentów.
- Brak testu na rzeczywistym tunerze z Python 2: zalecany test OpenPLi / OpenATV, HD / FHD.

## Użytkowanie
Menu → Skin interfejsu → Domyślny / Retro radio / Radio przyszłości.
Po zmianie skina zamknij i ponownie otwórz NeoRadio.
