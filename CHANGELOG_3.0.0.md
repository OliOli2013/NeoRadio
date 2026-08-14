## Poprawki końcowe v3.0

- Naprawiono obsługę przycisku INFO na różnych image Enigma2 (OpenATV/OpenPLi i zgodne mapowania).
- Naprawiono otwieranie `Menu → Informacje / strona projektu` i dodano bezpieczny fallback.
- Dodano automatyczne usuwanie plików instalacyjnych i IPK NeoRadio z `/tmp` po instalacji.

# NeoRadio 3.0.0 – changelog

## Stability and station database

- fixed the 2.1 Radio-Browser-only logic so packaged, custom and downloaded stations can coexist
- custom `/etc/enigma2/neoradio_user_stations.json` stations are no longer excluded by default
- reduced the Radio-Browser default request from 100000 entries to 500
- added a hard maximum of 2000 entries per country request to protect RAM and GUI responsiveness on weaker receivers
- retained `url_resolved` as the preferred Radio-Browser playback URL
- preserved Radio-Browser station UUIDs and added best-effort asynchronous click counting when a downloaded station is played
- retained automatic country detection and PL fallback for first-run station population

## Network and picons

- manual Radio-Browser country/station downloads now run in a background worker when threading is available
- added best-effort dynamic Radio-Browser mirror discovery after the configured mirrors fail

- remote station logos are downloaded outside the GUI thread
- removed shell-based remote picon downloads
- remote picon payload is capped at 2 MiB
- downloaded images are validated/convered with Pillow when available
- PNG/JPEG magic bytes are checked in the non-Pillow fallback path
- retained local SAT/IPTV picon lookup and remote cache behavior

## Configuration safety

- JSON configuration/cache writes are now atomic (`.tmp` + flush/fsync + rename)
- reduced risk of corrupt favorites, history or Radio-Browser cache after power loss/restart during a write
- plugin installation path is derived from `__file__` instead of being hard-coded

## GitHub updater hardening

- update manifest must use HTTPS
- update check is performed in a background worker when threading is available
- IPK download no longer uses an interpolated shell `wget` command
- removed `--no-check-certificate`
- added update download size limit (64 MiB)
- added optional SHA-256 validation from `manifest.json`
- added direct IPK/ar control parsing before installation
- package name must be `enigma2-plugin-extensions-neoradio`
- package version must match the version advertised by the manifest
- GUI restart uses Enigma2 `TryQuitMainloop` when available, with a legacy fallback only when required

## Code cleanup

- removed the unused legacy `NeoRadioSaver` class left behind by earlier hotfixes
- removed duplicated/dead screensaver/network/Radio-Browser methods carried by that class
- kept the active screensaver overlay inside `NeoRadioMain`
- refreshed repository structure and build tooling
- added automated static audit tooling

## Visual redesign / AIO identity

- new NeoRadio plugin icon
- new default cover and fallback radio artwork
- new dark navy / cyan / gold visual language consistent with AIO projects
- new dedicated About screen
- added project website: `https://olioli2013.github.io/aio-iptv-projekt/`
- added a high-error-correction QR code linking directly to the project website
- footer identifies Paweł Pawełek and the project website
- no Facebook-group reference is used in the 3.0.0 package

## Package optimization

- losslessly re-optimized all 1260 pre-rendered audio-control PNG assets
- retained the complete audio-control asset set for compatibility instead of removing receiver-tested variants

## Documentation / release engineering

- replaced stale 2.x README/version references
- added clean 3.0.0 manifest format with SHA-256 support
- added a reproducible Python build helper and shell wrapper
- added GitHub Actions static validation/build workflow
- added full audit and test matrix documentation
