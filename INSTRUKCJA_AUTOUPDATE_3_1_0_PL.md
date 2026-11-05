# NeoRadio 3.0.0 → 3.1.0 — poprawka aktualizacji online

**Stan 05.11.2026:** kod 3.1.0 jest w gałęzi main, ale `manifest.json` nadal deklaruje 3.0.0 i w Releases nie ma tagu `v3.1.0` z pełnymi plikami. Ostatni workflow 3.1.0 przerwał audyt, bo baza stacji zawiera zewnętrzny adres Facebook. To adres znaleziony w danych stacji, nie w kodzie wtyczki.

**Cel:** odblokować generowanie pełnego IPK/DEB z bieżącej bazy, opublikować wersję i dopiero potem włączyć aktualizację wtyczkową przez właściwy manifest i SHA256.

## Krok 1 — aktualizacja repo i poprawka audytu

Uruchom terminal GitKraken w katalogu repozytorium NeoRadio:

```bash
git status --short
git pull --ff-only origin main
unzip -o "$HOME/Pobrane/NEORADIO_3_1_0_AUTOUPDATE_FIX.zip" -d .
python3 tools/fix_audit_3_1_0.py
python3 tools/static_audit.py
bash tools/build_release_3_1_0.sh
```

Jeżeli plik ZIP znajduje się w innym katalogu, zmień ścieżkę po `unzip`.

Skrypt `fix_audit_3_1_0.py` nie zmienia list stacji, piconów ani odtwarzania. W `tools/static_audit.py` pomija skan odnośników wyłącznie w `pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio/stations.json`.

## Krok 2 — commit / push poprawki

```bash
git diff --check
git status --short
git add tools/static_audit.py tools/fix_audit_3_1_0.py tools/finalize_release_3_1_0.py INSTRUKCJA_AUTOUPDATE_3_1_0_PL.md
git commit -m "NeoRadio 3.1.0: fix release audit and prepare verified updater manifest"
git push origin main
```

Po push w GitHub Actions (`NeoRadio build`) audyt oraz tworzenie IPK/DEB powinny się zakończyć powodzeniem. Jeśli workflow nadal nie przejdzie, nie publikuj wydania bez sprawdzenia logów.

## Krok 3 — publikacja pełnych pakietów 3.1.0

W katalogu `releases/` będą dwa pliki, ZBUDOWANE Z AKTUALNEGO REPO:

- `enigma2-plugin-extensions-neoradio_3.1.0_all.ipk`
- `enigma2-plugin-extensions-neoradio_3.1.0_all.deb`

Opublikuj GitHub Release z tagiem **v3.1.0**, tytułem **NeoRadio 3.1.0**, dodaj oba pliki o dokładnie tych nazwach.

Z terminala, gdy masz zainstalowane i zalogowane `gh` (GitHub CLI), możesz użyć:

```bash
gh auth status
gh release create v3.1.0 \
  releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk \
  releases/enigma2-plugin-extensions-neoradio_3.1.0_all.deb \
  --title "NeoRadio 3.1.0" \
  --notes-file CHANGELOG_3_1_0.md
```

Jeśli tag lub release już istnieje, nie twórz duplikatu. Sprawdź pliki na stronie wydania i prześlij poprawne paczki do tego samego wydania.

## Krok 4 — automatycznie przygotuj właściwy manifest

**Dopiero po udanej publikacji obu plików**:

```bash
python3 tools/finalize_release_3_1_0.py
cat manifest.json
git diff -- manifest.json
git add manifest.json
git commit -m "NeoRadio 3.1.0: enable verified in-plugin updates"
git push origin main
```

Skrypt `finalize_release_3_1_0.py` pobiera oba pliki z rzeczywistego adresu GitHub Releases, porównuje SHA256 z lokalnymi pakietami i dopiero przy pełnej zgodności zapisuje `manifest.json`. Jeśli plik nie istnieje, pobieranie się nie uda lub hashe są inne, nie modyfikuje manifestu. Dzięki temu starsi użytkownicy nie otrzymają błędnego komunikatu instalacji.

## Krok 5 — test na tunerze z NeoRadio 3.0.0

Menu → aktualizacje GitHub / sprawdź aktualizacje. Prawidłowa nowa wersja: 3.1.0. Potwierdź pobranie i instalację, po zakończeniu zrestartuj GUI.

W ustawieniach starej wtyczki URL manifestu ma wskazywać:

`https://raw.githubusercontent.com/OliOli2013/NeoRadio/main/manifest.json`

Jeżeli zapisałeś wcześniej niestandardowy URL manifestu, zmień go na ten adres. Jeśli manifest zgłasza wersję 3.1.0, ale instalacja nie dochodzi do końca, potrzebny jest dokładny komunikat z ekranu (np. problem HTTPS/SSL, hash lub opkg).

**Nie używaj SHA256 z wcześniej przygotowanych testowych IPK/DEB** — były budowane ze starszą, pustą bazą stacji. Skrypt obliczy SHA z pełnych plików, które rzeczywiście udostępnisz w Releases.
