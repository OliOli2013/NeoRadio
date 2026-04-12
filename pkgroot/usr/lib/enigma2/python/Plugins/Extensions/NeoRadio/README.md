# NeoRadio

NeoRadio is an Enigma2 internet radio plugin with:
- Polish and English UI with automatic fallback to English when the system language is not Polish
- manual UI language switching
- country-based station filtering and main country selection
- favorites and search
- ICY/RDS now playing info
- SAT/IPTV picons from channel name and service reference
- custom picon paths
- fallback radio icon when no picon exists
- optional screensaver
- GitHub update check via remote manifest URL

## GitHub update manifest

The plugin expects a JSON document at the configured GitHub manifest URL.

```json
{
  "version": "1.2.0",
  "ipk": "https://example.com/enigma2-plugin-extensions-neoradio_1.2.0_all.ipk",
  "source": "https://example.com/neoradio_repo_1.2.0.tar.gz",
  "changelog": "Expanded country station set, improved picon matching, cleaner UI"
}
```

Leave the URL empty for now and add your GitHub raw link later.
