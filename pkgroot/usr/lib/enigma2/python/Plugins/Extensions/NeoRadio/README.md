# NeoRadio 1.3.3

NeoRadio is a modern Enigma2 internet radio plugin focused on fast playback, readable metadata, SAT/IPTV picon support, bilingual Polish/English UI, and GitHub-based updates.

## What's new in 1.3.3

- cleaned up the main screen layout so the clock, station description, and live metadata no longer overlap
- moved the live metadata into a dedicated lower information block for better readability
- shortened overly long footer/source lines to keep RDS / ICY details visible on screen
- kept station description stable instead of mixing it with now-playing text near the clock
- retained the stronger **ICY metadata** parsing and optional station endpoint support from 1.3.x

## Metadata model

NeoRadio now uses the following priority chain:

1. Enigma2 service tags (`sTagTitle`, `sTagArtist`, `sTagAlbum`, `sTagComment`)
2. direct stream metadata via `Icy-MetaData: 1`
3. optional station endpoint defined per station in JSON

This gives much better results on streams that do not fully expose metadata through Enigma2 alone.

## Custom station example with external metadata endpoint

The plugin supports additional optional fields in `neoradio_user_stations.json`:

```json
[
  {
    "name": "Moja stacja",
    "url": "https://radio.example.com/live.mp3",
    "genre": "Custom",
    "country": "Polska",
    "bitrate": "128",
    "description": "Przykładowa stacja z zewnętrznymi metadanymi.",
    "homepage": "https://radio.example.com",
    "picon": "/usr/share/enigma2/picon/moja_stacja.png",
    "metadata_url": "https://radio.example.com/api/nowplaying",
    "metadata_type": "json",
    "metadata_title_key": "now_playing.song.title",
    "metadata_artist_key": "now_playing.song.artist",
    "metadata_album_key": "now_playing.song.album",
    "metadata_text_key": "now_playing.song.text",
    "metadata_program_key": "live.show.name",
    "metadata_cover_key": "now_playing.song.art"
  }
]
```

### Supported metadata fields

- `metadata_url`
- `metadata_type` = `auto`, `json`, `text`
- `metadata_title_key`
- `metadata_artist_key`
- `metadata_album_key`
- `metadata_text_key`
- `metadata_program_key`
- `metadata_cover_key`

Nested JSON paths are supported with dot notation.

## GitHub updates

The plugin checks `manifest.json` and expects a payload like this:

```json
{
  "name": "NeoRadio",
  "version": "1.3.3",
  "ipk": "https://github.com/OliOli2013/NeoRadio/releases/latest/download/enigma2-plugin-extensions-neoradio_all.ipk",
  "source": "https://github.com/OliOli2013/NeoRadio/releases/latest/download/neoradio_repo.tar.gz",
  "release_page": "https://github.com/OliOli2013/NeoRadio/releases/latest",
  "changelog": "Added stronger ICY metadata parsing, optional per-station JSON/text metadata endpoints, improved Now Playing fallback logic, refreshed default artwork, and cleaner metadata presentation in the UI."
}
```

## Repository layout

```text
pkgroot/                                 Files installed on the Enigma2 receiver
release/CONTROL/control                  Package metadata
release/build_ipk.sh                     Build helper for .ipk output
manifest.json                            GitHub update manifest
```
