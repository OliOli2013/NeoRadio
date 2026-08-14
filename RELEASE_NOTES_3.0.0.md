# NeoRadio 3.0.0

Major maintenance, security and UI release for Enigma2.

Highlights:

- fixed station-source handling so custom stations and Radio-Browser cache can coexist
- reduced Radio-Browser default load from an unsafe 100000 entries to 500, with a hard 2000 cap
- moved manual Radio-Browser downloads and update checks to background workers where threading is available
- added fallback Radio-Browser mirror discovery
- made remote picon downloads asynchronous and size/image validated
- replaced shell-built update downloads with HTTPS Python downloads
- added optional SHA-256 verification and IPK package/version validation before installation
- added atomic JSON writes for favorites/history/cache
- removed dead legacy screensaver code left by earlier hotfixes
- refreshed the complete NeoRadio visual identity to match the AIO family
- added the AIO project website and a scannable QR code in the About screen
- retained Polish/English UI and Python 2.7/Python 3 compatibility-oriented code

Project website: https://olioli2013.github.io/aio-iptv-projekt/
