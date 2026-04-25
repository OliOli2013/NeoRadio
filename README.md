# NeoRadio

![NeoRadio - główny ekran](docs/images/neoradio-main.jpg)

**NeoRadio** to wtyczka dla Enigma2 umożliwiająca słuchanie internetowych stacji radiowych z poziomu dekodera. Wtyczka zawiera uporządkowaną listę stacji, obsługę filtrów językowych oraz zapamiętywanie ostatnio używanych ustawień.

## Najważniejsze funkcje

- odtwarzanie internetowych stacji radiowych,
- uporządkowana lista stacji bez powtarzania tych samych kanałów w wielu bukietach,
- ujednolicone kategorie, np. `Polska` zamiast osobnych `Polska`, `Poland`, `Polen`,
- wybór stacji oddzielony od menu ustawień,
- osobny przycisk do wyboru bukietu / języka,
- osobny przycisk `Menu` do ustawień,
- zapamiętywanie ostatnio odtwarzanej stacji,
- zapamiętywanie ostatnio wybranego filtra,
- historia ostatnio odtwarzanych stacji,
- możliwość dodania własnych stacji użytkownika.

## Kategorie językowe

W wersji 1.3.4 dodano i uporządkowano filtry językowe:

- Polski,
- Arabski,
- Francuski,
- Niemiecki,
- Włoski,
- Inne.

Dzięki temu stacje nie są dublowane w podobnych kategoriach, np. `Polska` i `Poland`.

## Obsługa przycisków

- `OK` — uruchomienie wybranej stacji,
- `Niebieski` — wybór bukietu / języka / filtra stacji,
- `Menu` — ustawienia wtyczki,
- `Exit` — wyjście z wtyczki.

Menu nie znajduje się już na końcu listy stacji, więc nie trzeba przewijać całej listy, aby wejść do ustawień.

## Zapamiętywanie ustawień

NeoRadio zapamiętuje:

- ostatnio odtwarzaną stację,
- adres URL ostatnio odtwarzanej stacji,
- ostatnio użyty filtr,
- historię ostatnio odtwarzanych stacji.

Historia odtwarzania zapisywana jest w pliku:

```text
/etc/enigma2/neoradio_history.json
```

## Własne stacje użytkownika

Przykładowy plik własnych stacji znajduje się w repozytorium:

```text
pkgroot/etc/enigma2/neoradio_user_stations.json.example
```

Aby dodać własne stacje, można utworzyć plik:

```text
/etc/enigma2/neoradio_user_stations.json
```

Format przykładowy:

```json
[
  {
    "name": "Moja stacja",
    "url": "https://example.com/radio.mp3",
    "language": "Polski"
  }
]
```

## Instalacja z pliku IPK

Skopiuj plik `.ipk` do katalogu `/tmp` na dekoderze, a następnie wykonaj:

```sh
opkg install --force-reinstall /tmp/enigma2-plugin-extensions-neoradio_1.3.4_all.ipk
```

Po instalacji zrestartuj GUI Enigma2:

```sh
init 4
sleep 3
init 3
```

Można też wykonać restart GUI z menu dekodera.

## Struktura repozytorium

Najważniejsze katalogi i pliki:

```text
pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py
pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json
pkgroot/etc/enigma2/neoradio_user_stations.json.example
docs/images/neoradio-main.jpg
release/CONTROL/control
build_ipk.sh
```

## Budowanie paczki IPK z repozytorium

Jeżeli w repozytorium znajduje się skrypt `build_ipk.sh`, nadaj mu uprawnienia wykonywania:

```sh
chmod +x build_ipk.sh
```

Następnie uruchom:

```sh
./build_ipk.sh
```

Gotowa paczka `.ipk` powinna zostać utworzona zgodnie z ustawieniami skryptu budowania.

## Wersja

Aktualna wersja: **1.3.4**

Zmiany w wersji 1.3.4:

- dodano stacje z bukietu IPTV Radio,
- usunięto lub pominięto duplikaty stacji,
- ujednolicono nazwy kategorii językowych,
- dodano filtry językowe: Arabski, Francuski, Niemiecki, Włoski oraz Inne,
- poprawiono zapamiętywanie ostatniej stacji i ustawień,
- dodano historię ostatnio odtwarzanych stacji,
- rozdzielono wybór stacji od menu ustawień.

## Licencja

Projekt jest udostępniany zgodnie z licencją znajdującą się w pliku `LICENSE` lub `LICENSE.md`.
