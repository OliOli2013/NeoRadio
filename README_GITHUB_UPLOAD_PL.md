# NeoRadio 2.0 — pliki do aktualizacji GitHub

To jest paczka PATCH ONLY. Nie kasuj starych plików z repozytorium.
Kopiuj pliki na istniejące repo z nadpisaniem.

## Najważniejsze pliki

1. `manifest.json` — główny manifest aktualizacji, wersja 2.0.
2. `enigma2-plugin-extensions-neoradio_all.ipk` — paczka latest do linków aktualizacji.
3. `enigma2-plugin-extensions-neoradio_2.0_all.ipk` — paczka wersji 2.0.
4. `release/enigma2-plugin-extensions-neoradio_all.ipk` — kopia paczki w folderze `release`.
5. `release/enigma2-plugin-extensions-neoradio_2.0_all.ipk` — kopia wersji 2.0 w folderze `release`.
6. `releases/enigma2-plugin-extensions-neoradio_all.ipk` — dodatkowa kopia dla folderu `releases`, jeśli takiego używasz na GitHubie.
7. `releases/enigma2-plugin-extensions-neoradio_2.0_all.ipk` — dodatkowa kopia wersji 2.0 dla folderu `releases`.
8. `pkgroot/` — aktualne pliki wtyczki.

## Ważne

Jeżeli na GitHubie masz folder `release`, wrzuć pliki do `release`.
Jeżeli używasz folderu `releases`, wrzuć pliki do `releases`.
W tej paczce są oba warianty: `release/` i `releases/`, żeby niczego nie brakowało.

GitHub Releases, czyli zakładka „Releases” na stronie repo, nie uzupełnia się sama po skopiowaniu plików do repozytorium. Tam trzeba ręcznie utworzyć tag/release `v2.0` i dodać plik IPK jako asset, jeśli chcesz go mieć widocznego w zakładce Releases.

## Przed commitem sprawdź

W GitKraken nie może być czerwonego usunięcia plików typu:
- `README.txt`
- `README.md`
- `LICENSE`
- `.gitignore`
- `docs/`
- `build/`
- inne stare pliki repozytorium, których nie chcesz usuwać.

Commit przykładowy:

`NeoRadio 2.0 update`
