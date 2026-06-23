# NeoRadio v2.1 — hotfix Radio-Browser Only

- wersja pozostaje 2.1,
- wtyczka działa teraz w trybie Radio-Browser Online jako główne źródło stacji,
- wbudowany `stations.json` został wyczyszczony i nie jest już ładowany jako stała baza,
- po instalacji usuwany jest stary cache Radio-Browser z `/etc/enigma2`, aby pierwsze uruchomienie pobrało świeżą listę,
- przy pierwszym uruchomieniu po instalacji wtyczka pobiera listę kraju zgodnie z językiem/locale tunera, np. PL dla polskiego języka,
- po ręcznym wyborze kraju z menu zapisywana jest lista tego kraju,
- usunięto przedrostki typu `[Polska]` z listy stacji,
- poprawiono obsługę `favicon`/piconów z Radio-Browser, w tym małe favikony i szerokie logotypy stacji,
- poprawiono fallback piconu, aby błędny/nieobsługiwany obraz nie blokował domyślnej grafiki NeoRadio,
- zachowano poprawki Volume/klawiszy głośności z v2.1.
