# NeoRadio 3.1.0 for Enigma2

**NeoRadio** is an internet-radio plugin for Enigma2 receivers. Version 3.0.0 is a maintenance, security and interface release built from NeoRadio 2.1 after a full static/package audit.

The plugin keeps compatibility-oriented code for **Python 2.7 and Python 3 Enigma2 images**, while improving network handling, Radio-Browser integration, picon caching, update validation and the visual identity used by the AIO projects.

Project website: **https://olioli2013.github.io/aio-iptv-projekt/**  
Repository: **https://github.com/OliOli2013/NeoRadio**  
Author: **Paweł Pawełek**

## Main features

- internet radio playback through Enigma2 service reference 4097
- Radio-Browser station download by country (background worker where available)
- fallback mirror discovery if the configured Radio-Browser endpoints fail
- automatic first-run Radio-Browser cache population (system country, with PL fallback)
- local/custom station support through `/etc/enigma2/neoradio_user_stations.json`
- favorites and recently played history
- station filters, search and language grouping
- Enigma2 / ICY / optional JSON-text endpoint metadata
- SAT/IPTV/local picon lookup and remote logo cache
- album/cover artwork support
- optional screensaver overlay
- audio balance, treble and bass controls where supported by the receiver/audio stack
- Polish and English user interface
- GitHub update checking with package validation
- AIO-family dark navy / cyan / gold visual identity
- built-in About screen with project website and QR code

## Remote control

- **OK / Green** – play selected station
- **Red / Exit** – close NeoRadio
- **Yellow** – favorite on/off
- **Blue** – filters/bouquets
- **Menu** – settings and tools
- **Info** – station details
- **1 / 3** – balance left/right
- **4 / 6** – treble down/up
- **7 / 9** – bass down/up
- **5** – reset audio controls
- **0** – change audio-control visual theme
- **Volume +/- / Mute** – receiver volume controls

## Station sources in 3.0.0

NeoRadio merges and deduplicates the following sources instead of forcing the Radio-Browser cache to replace everything:

1. packaged `stations.json`
2. `/etc/enigma2/neoradio_user_stations.json`
3. `/etc/enigma2/neoradio_radiobrowser_stations.json`

The packaged database may remain intentionally small/empty. On a normal network-connected receiver NeoRadio populates the Radio-Browser cache automatically. Custom stations remain available and are no longer ignored by the Radio-Browser mode used in 2.1.

## Safe update model

The updater now:

- accepts an HTTPS manifest
- downloads the IPK without a shell-built `wget` command
- limits update size
- supports SHA-256 verification from `manifest.json`
- reads the IPK `control` archive before installation
- verifies package name and expected version
- installs only after validation
- uses Enigma2 `TryQuitMainloop` for GUI restart when available

## Build

On Linux with Python 3:

```bash
./release/build_ipk.sh
```

Output is written to `releases/enigma2-plugin-extensions-neoradio_3.1.0_all.ipk`.

Run the static audit:

```bash
python3 tools/static_audit.py
```

## Important compatibility note

Static validation cannot replace testing on real Enigma2 hardware. Before publishing the release broadly, test at minimum one Python 2 image and one Python 3 image, both HD and Full HD GUI layouts, stream playback, metadata, picons, Radio-Browser download and self-update.

See `AUDIT_3.0.0_PL.md` for the detailed audit and `CHANGELOG_3.0.0.md` for the release changes.


## NeoRadio 3.1.0 — UI refresh
- A fixed, centered author/version credit beneath remote-control color buttons (HD and FHD).
- Subtle cyan section accents; improved yellow-key label contrast.
- Existing dynamic source-metadata footer remains unchanged.
- Playback, Radio-Browser, favorites, picon lookup, screensaver, audio and settings logic unchanged.
- Builds both IPK and DEB. See `README_UPGRADE_3_1_0_PL.md`.
