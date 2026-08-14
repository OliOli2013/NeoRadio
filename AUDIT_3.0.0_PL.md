# NeoRadio – pełny audyt 2.1 i zakres napraw 3.0.0

Data audytu: 14.08.2026  
Pakiet wejściowy: `enigma2-plugin-extensions-neoradio_2.1_all(3).ipk`  
Repozytorium: `OliOli2013/NeoRadio`

## 1. Zakres audytu

Sprawdzono strukturę IPK, plik `control`, kod `plugin.py`, zasoby graficzne, bazę stacji, logikę Radio-Browser, zapis konfiguracji, picony, metadata/ICY, audio, screensaver, mechanizm aktualizacji, zgodność składniową Python 3 i kompatybilność składniową projektowaną pod Python 2.7, skiny HD/FHD oraz spójność repozytorium.

Pakiet 2.1 miał około 11,5 MB. Sam katalog pluginu po rozpakowaniu miał około 15 MB. Największą część stanowi 1260 pre-renderowanych PNG regulatorów audio. Zestaw pozostawiono, ponieważ jego agresywne usunięcie byłoby oszczędnością miejsca kosztem ryzyka regresji na różnych odbiornikach.

## 2. Najważniejsze problemy wykryte w 2.1

### KRYTYCZNE / WYSOKIE

**A. Radio-Browser-only wyłączał inne źródła stacji**  
`RADIO_BROWSER_ONLY_MODE = True` powodował ładowanie wyłącznie `/etc/enigma2/neoradio_radiobrowser_stations.json`. Pakietowy `stations.json` i własny `neoradio_user_stations.json` były pomijane, mimo że dokumentacja opisywała ich obsługę. W paczce 2.1 `stations.json` był pusty (`[]`).

**Naprawa 3.0.0:** domyślnie łączone są baza pakietowa + stacje użytkownika + cache Radio-Browser, z deduplikacją URL/nazw.

**B. Limit Radio-Browser = 100000**  
Tak duży wynik jest nieuzasadniony dla GUI Enigma2 i może powodować duże zużycie RAM, długie sortowanie i wolną listę na słabszych tunerach.

**Naprawa 3.0.0:** 500 domyślnie, twardy limit 2000.

**C. Aktualizacja przez składany command shell + `--no-check-certificate`**  
URL aktualizacji był używany w poleceniu powłoki, a TLS był jawnie omijany. To zwiększało powierzchnię ataku i utrudniało wiarygodną walidację pobranego pakietu.

**Naprawa 3.0.0:** pobieranie bez shell, HTTPS, limit rozmiaru, opcjonalny SHA-256, odczyt `control` z IPK, weryfikacja nazwy pakietu i wersji przed `opkg`.

**D. Picon z sieci mógł blokować GUI i korzystał z zewnętrznego `wget`**  
Pobieranie logo było wykonywane w ścieżce wyboru/odświeżenia piconu. Przy wolnym hostingu użytkownik mógł odczuwać zamrożenie interfejsu.

**Naprawa 3.0.0:** pobieranie w tle, cache, limit 2 MiB, walidacja obrazu, bez shell.

### ŚREDNIE

**E. Nieatomowy zapis JSON**  
Ulubione, historia i cache były zapisywane bez pliku tymczasowego. Restart GUI lub utrata zasilania w złym momencie mogły zostawić uszkodzony JSON.

**Naprawa 3.0.0:** zapis `.tmp`, flush/fsync, rename.

**F. Martwa klasa `NeoRadioSaver`**  
W kodzie pozostawała niewykorzystywana klasa screensavera z metodami skopiowanymi z głównego okna. Odwoływała się do stanu/kontrolek, których sama nie posiadała. Nie była nigdzie instancjonowana, więc był to głównie problem jakości i ryzyka przyszłych regresji.

**Naprawa 3.0.0:** klasa usunięta; pozostawiono rzeczywiście używany overlay screensavera w `NeoRadioMain`.

**G. Monolityczny `plugin.py`**  
Kod przekracza 4 tys. linii i ma wiele szerokich `except Exception`, co utrudnia diagnostykę. Jednorazowe rozbicie całego pluginu na moduły byłoby jednak zmianą o wysokim ryzyku bez testów sprzętowych.

**Decyzja 3.0.0:** usunięto ewidentnie martwy kod i wyizolowano bezpieczne helpery, ale nie wykonano agresywnego pełnego refaktoru architektury. To celowa decyzja minimalizująca ryzyko regresji.

### NISKIE / REPOZYTORIUM

**H. Dokumentacja 2.x była niespójna**  
W repozytorium występowały równoległe changelogi/hotfixy, a przykłady manifestu i README miały stare wersje. Utrudniało to stwierdzenie, który plik jest źródłem prawdy.

**Naprawa 3.0.0:** czysty zestaw README, changelog, audit, manifest, build helper i CI.

**I. Informacje Facebook**  
W dostarczonym IPK 2.1 nie znaleziono rzeczywistego adresu Facebook ani opisu grupy Facebook. Nie usuwano więc danych, których tam nie było.

**Zmiana 3.0.0:** oficjalnym punktem informacji w UI jest strona `https://olioli2013.github.io/aio-iptv-projekt/` wraz z kodem QR.

## 3. Usprawnienia dodatkowe wykonane w 3.0.0

- asynchroniczne sprawdzanie manifestu aktualizacji
- asynchroniczne ręczne pobieranie list krajów/stacji Radio-Browser
- zapasowe odkrywanie aktywnych mirrorów Radio-Browser po awarii skonfigurowanych hostów
- asynchroniczne zliczenie kliknięcia Radio-Browser przy odtwarzaniu stacji z UUID
- `PLUGIN_PATH` ustalany z `__file__`
- bezpieczniejsze rozpoznawanie zdalnego PNG/JPEG bez Pillow
- zredukowane timeouty i limity danych JSON
- zachowana obsługa `url_resolved`
- zachowana obsługa Python 2.7/Python 3 w kodzie bez f-stringów i konstrukcji wymagających nowego Pythona
- nowy ekran About PL/EN i QR
- AIO branding: granat + błękit + złoty akcent
- optymalizacja PNG bez zmiany wymiarów/nazw wymaganych przez kod audio

## 4. Testy statyczne 3.0.0

W pakiecie źródłowym uruchamiany jest `tools/static_audit.py`, który kontroluje m.in.:

- kompilację składniową `plugin.py` w Python 3
- spójność wersji plugin/control
- parsowanie wszystkich XML skinów HD/FHD
- brak zdublowanych nazw widgetów w skinach
- obecność zasobów wymaganych przez UI
- integralność PNG przez Pillow, jeśli jest dostępne
- brak odwołań Facebook i `--no-check-certificate`
- poprawność JSON `stations.json`

Po zbudowaniu IPK należy dodatkowo sprawdzić strukturę `ar`, `control.tar.gz`, `data.tar.gz`, wersję i sumę SHA-256.

## 5. Testy sprzętowe wymagane przed szerokim wydaniem

Statyczny audyt nie uruchamia Enigma2. Przed oznaczeniem wydania jako finalnego zalecane są realne testy:

1. OpenATV Python 3 – HD GUI
2. OpenATV/OpenPLi Python 3 – Full HD GUI
3. co najmniej jeden starszy image Python 2.7
4. start bez istniejącego cache Radio-Browser
5. start bez internetu z zachowanym cache
6. własny `/etc/enigma2/neoradio_user_stations.json`
7. MP3/AAC/HLS oraz playlisty PLS/M3U
8. ICY metadata i stacja bez metadata
9. lokalny picon + zdalny favicon + błędny URL logo
10. ulubione/historia po restarcie GUI
11. screensaver
12. balance/treble/bass na tunerze z `amixer` i na tunerze bez obsługi odpowiedniego control
13. update check 3.0.0 -> nowszy testowy manifest
14. odrzucenie IPK z inną nazwą pakietu/wchodzącą wersją
15. restart GUI po aktualizacji

## 6. Ocena końcowa

Wersja 2.1 była funkcjonalnie rozbudowana, ale nosiła ślady szybkich hotfixów: martwy kod, zbyt agresywny tryb Radio-Browser, ekstremalny limit API i mechanizmy sieciowe wykonywane zbyt ryzykownie lub synchronicznie. 3.0.0 usuwa najpoważniejsze problemy bez niepotrzebnego przepisywania działającej części playera i audio.

Największym pozostałym długiem technicznym jest monolityczny `plugin.py`. Jego dalszy podział na `core/`, `ui/`, `network/` i `audio/` ma sens dopiero po przejściu powyższej matrycy na rzeczywistych odbiornikach, żeby refaktor można było porównywać z wersją 3.0.0 jako stabilną bazą.
