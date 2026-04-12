# NeoRadio

NeoRadio is an Enigma2 internet radio plugin focused on online radio playback, country-based station browsing, SAT/IPTV picon support and a bilingual Polish/English UI.

## Key features

- automatic UI language: Polish only when the Enigma2 system language is Polish, otherwise English
- manual language switch in plugin settings
- main country selection for the default station list
- favorites, search and metadata display
- SAT/IPTV picon loading by station name and bouquet service reference
- fallback radio icon when no picon is available
- optional screensaver
- GitHub update check based on a remote `manifest.json`

## Repository layout

- `pkgroot/` – files installed on the Enigma2 receiver
- `release/CONTROL/control` – package metadata template
- `release/build_ipk.sh` – helper script to build the `.ipk`
- `manifest.json` – GitHub update manifest template

## Build

```bash
chmod +x release/build_ipk.sh
./release/build_ipk.sh 1.2.0
```

The build script creates an `.ipk` from `pkgroot/` without adding a hard Python package dependency, which keeps the package compatible with more Enigma2 images.

## GitHub updates

The plugin settings include a field for a GitHub manifest URL and a menu item to check updates. Leave the URL empty until you publish your own raw manifest file.
