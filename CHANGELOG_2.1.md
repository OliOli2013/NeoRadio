# NeoRadio v2.1

Zmiany względem v2.0:

- dodano moduł **Radio-Browser Online** w menu wtyczki,
- użytkownik może wybrać kraj i pobrać aktualną listę stacji z Radio-Browser,
- pobieranie wykorzystuje oficjalne API Radio-Browser z `countrycode`, `hidebroken=true`, `order=clickcount`, `reverse=true`, `limit=100000`,
- do odtwarzania preferowany jest `url_resolved`, a gdy go brak — `url`,
- loga/picony stacji pobierane są z pola `favicon` i zapisywane w lokalnym cache,
- inne kraje/stacje z obecnego `stations.json` pozostają zachowane,
- pobrane stacje Radio-Browser są zapisywane osobno w `/etc/enigma2/neoradio_radiobrowser_stations.json`,
- poprawiono obsługę klawiszy głośności `VolumeUp`, `VolumeDown`, `Mute` wewnątrz wtyczki,
- wyłączono ryzykowne automatyczne wymuszanie balansu przez `eDVBVolumecontrol.setVolume()`, które mogło blokować reakcję pilota na głośność,
- przy wyjściu zatrzymywane są wszystkie timery wtyczki i przywracany jest poprzedni serwis albo zatrzymywane odtwarzanie,
- usunięto błędne ścieżki piconów `/usr/share/engma2` i `/user/share/...`,
- `postinst` czyści pliki instalacyjne NeoRadio z `/tmp`,
- baza `stations.json` pozostaje bez zmiany wersji bazy: 5721 stacji.

Uwaga testowa: kod został sprawdzony składniowo i strukturalnie poza tunerem. Funkcje pilota/Volume trzeba potwierdzić na fizycznym Enigma2.
