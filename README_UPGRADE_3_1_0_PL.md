# NeoRadio 3.1.0 — aktualizacja ze sprawdzonego repozytorium

Punktem wyjścia jest gałąź `main` projektu https://github.com/OliOli2013/NeoRadio, wersja 3.0.0.

## Cel
- zachowanie aktualnych mechanizmów odtwarzania, Radio-Browser, wyszukiwania, historii, ulubionych, RDS/ICY, piconów, audio i wygaszacza;
- oddzielna, czytelna stopka w HD i FHD: `NeoRadio 3.1.0 | Paweł Pawełek | AIO Team | Enigma2`;
- dyskretne cyjanowe akcenty sekcji i czytelniejsza etykieta Żółty/Fav;
- pełne pakiety IPK i DEB budowane z całej oryginalnej zawartości repozytorium.

## 1. Pobierz / otwórz repo w GitKraken

W terminalu GitKrakena wejdź do katalogu projektu lub sklonuj repo:

```bash
git clone https://github.com/OliOli2013/NeoRadio.git
cd NeoRadio
git status --short
git pull --ff-only origin main
```

Repozytorium musi być czyste przed nakładaniem zmian.

## 2. Wypakuj paczkę z poprawkami

Umieść ZIP w `~/Pobrane` i wykonaj w głównym katalogu `NeoRadio`:

```bash
unzip -o "$HOME/Pobrane/NEORADIO_3.1.0_GITKRAKEN.zip" -d .
```

Wymagania: `python3`, `unzip`; opcjonalnie `pillow` dla kontroli PNG.

## 3. Modyfikacja i pełna budowa

```bash
python3 tools/test_refresh_offline.py
bash tools/build_release_3_1_0.sh
```

Skrypt sprawdza niezmienioną strukturę kodu, modyfikuje wyłącznie potrzebne linie, kompiluje składnię, parsuje 4 skiny XML, uruchamia dotychczasowy audyt i tworzy dwa pakiety. Pliki użytkownika w /etc/enigma2 pozostają poza pakietem.

Gotowe pakiety:

- `releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk`
- `releases/enigma2-plugin-extensions-neoradio_3.1.0_all.deb`

Obydwa pakiety mają te same pliki programu, a różnią się tylko rozszerzeniem: oba to poprawne archiwa `ar` z `debian-binary`, `control.tar.gz`, `data.tar.gz`. `verify_release_3_1_0.py` weryfikuje ich strukturę.

## 4. GitKraken commit

Sprawdź zmiany:

```bash
git diff --stat
git status --short
```

Następnie wykonaj:

```bash
git add README.md README_UPGRADE_3_1_0_PL.md CHANGELOG_3_1_0.md .gitignore .github/workflows/build.yml release/CONTROL/control \
  pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/plugin.py \
  tools/upgrade_neoradio_3_1_0.py tools/build_release_3_1_0.sh tools/build_deb.py \
  tools/build_ipk.py tools/static_audit.py tools/verify_release_3_1_0.py tools/test_refresh_offline.py

git commit -m "NeoRadio 3.1.0: modernize HD/FHD UI and add author footer"
git push origin main
```

Pliki `.bak` pozostają lokalne i nie powinny być commitowane. Skrypt aktualizuje `.gitignore` o `releases/*.deb` i kopie `.bak`; gotowe paczki dodaje się ręcznie do GitHub Releases, nie do głównej historii Git.

## 5. Publikacja w GitHub Releases

Po weryfikacji na tunerach utwórz nowy Release z tagiem `v3.1.0` i załącz pełne IPK oraz DEB z `releases/`.

**Dopiero gdy oba pliki są publicznie dostępne**: zastąp główny `manifest.json` treścią `releases/manifest_3.1.0_UPLOAD_FIRST.json`, wykonaj osobny commit, push. To chroni użytkowników przed komunikatem aktualizacji prowadzącym do nieistniejącego pliku.

## 6. Testy na odbiornikach Enigma2

- Python 2 oraz Python 3: uruchomienie/wyjście, brak crasha;
- HD i FHD: czytelna stopka, widoczne wszystkie przyciski, poprawne picony;
- odtwarzanie, RDS/ICY, Radio-Browser, szukanie i ulubione;
- regulacja balansu/wysokich/niskich, wygaszacz, powrót do TV;
- lokalny DEB/IPK instalowany w testowym image; sprawdź zatrzymanie/powrót GUI;
- po publikacji test actual self-update przez manifest.

Nie publikuj nowej wersji wyłącznie na podstawie poprawnego audytu statycznego. Nie można uruchomić prawdziwego GUI Enigma2 na zwykłym komputerze Linux bez środowiska odbiornika.

## Różnica między pakietami testowymi a kompilacją z `main`

Do zestawu dołączono gotowe pakiety IPK i DEB zbudowane na bazie ostatniego **udanego workflow GitHub Actions z 14.08.2026**. Zawierają dokładnie ten sam `plugin.py` co obecne `main` (potwierdzony identyczny SHA Git blob) i 1349 oryginalnych PNG. Istnieje jednak jedna późniejsza zmiana w repo: `stations.json` został rozwinięty do większej bazy stacji. Pakiety dołączone do tej odpowiedzi mają starą, pustą bazę (`[]`), lecz pozostaje w nich mechanizm automatycznego pobierania stacji przez Radio-Browser oraz zachowania cache w `/etc/enigma2`.

**Do publikacji zalecane są nowe pakiety zbudowane lokalnie z najnowszego `main`** za pomocą `bash tools/build_release_3_1_0.sh`, ponieważ zawierają również nową bazę `stations.json`. Nie kopiuj hasha SHA256 testowych IPK/DEB do manifestu, jeśli zbudujesz nowe pliki lokalnie.
