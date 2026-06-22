# NeoRadio 2.0

Baza: NeoRadio 1.3.9 z pliku `enigma2-plugin-extensions-neoradio_1.3.9_all.ipk`.

Zmiany w 2.0:
- zachowano rozbudowaną wersję 1.3.9, w tym potencjometry audio, skróty pilota, historię, filtry, picony, metadane i aktualizacje GitHub,
- zaktualizowano wbudowaną bazę stacji na podstawie `userbouquet.iptv_radio.radio`,
- dodano 148 nowych unikalnych stacji z przesłanego bukietu,
- pominięto 75 technicznych placeholderów z bukietu typu `127.0.0.1/hdfradio`,
- usunięto 2 stare placeholdery `127.0.0.1/hdfradio` obecne w bazie 1.3.9,
- dodano `postinst`, który po instalacji czyści tymczasowe pliki instalacyjne NeoRadio z `/tmp`,
- poprawiono mechanizm aktualizacji GitHub tak, aby usuwał tymczasowy IPK z `/tmp` także po aktualizacji z poziomu wtyczki,
- podniesiono numer wersji we wtyczce, control i manifestach do 2.0,
- usunięto `__pycache__` z paczki, aby nie przenosić bajtkodu z innej wersji Pythona.

Dane kontrolne:
- stacji w bazie 1.3.9 przed aktualizacją: 5697,
- stacji w bazie 2.0 po aktualizacji: 5843,
- unikalnych URL w bazie 2.0: 5843,
- źródło bukietu: Update 20.06.2026 09:57 by Team www.hdfreaks.cc.

Pliki release:
- `release/enigma2-plugin-extensions-neoradio_2.0_all.ipk`
- `release/enigma2-plugin-extensions-neoradio_all.ipk`
- `releases/enigma2-plugin-extensions-neoradio_2.0_all.ipk`
- `releases/enigma2-plugin-extensions-neoradio_all.ipk`
