# NeoRadio 2.0

NeoRadio is a modern Enigma2 internet radio plugin for Python 2/3 images.

## What's new in 2.0

- refreshed station database from the supplied `userbouquet.iptv_radio.radio` file,
- added 565 new unique stations,
- removed invalid local/placeholder technical entries,
- added post-install cleanup of NeoRadio installation files from `/tmp`,
- hardened GitHub IPK update cleanup before and after installation,
- corrected minor translation and picon-path issues,
- kept the existing NeoRadio logic and layout unchanged from the prepared 2.0 package.

## GitHub update manifest

The plugin checks:

```json
{
  "name": "NeoRadio",
  "version": "2.0",
  "ipk": "https://github.com/OliOli2013/NeoRadio/releases/latest/download/enigma2-plugin-extensions-neoradio_all.ipk",
  "source": "https://github.com/OliOli2013/NeoRadio/releases/latest/download/neoradio_repo.tar.gz",
  "release_page": "https://github.com/OliOli2013/NeoRadio/releases/latest",
  "changelog": "Station database refreshed from HDF radio bouquet update 20.06.2026, added 565 new stations, removed invalid local placeholder entries, added post-install /tmp cleanup, hardened GitHub IPK update cleanup, and minor translation/path cleanup fixes."
}
```

## Repository layout

```text
pkgroot/                                 Files installed on the Enigma2 receiver
release/CONTROL/control                  Package metadata
release/CONTROL/postinst                 Post-install cleanup script
release/*.ipk                            IPK packages
manifest.json                            GitHub update manifest
```

## Installation from shell

```sh
wget -O /tmp/enigma2-plugin-extensions-neoradio_all.ipk https://github.com/OliOli2013/NeoRadio/releases/latest/download/enigma2-plugin-extensions-neoradio_all.ipk
opkg install /tmp/enigma2-plugin-extensions-neoradio_all.ipk
```

After installation, NeoRadio removes its temporary installation files from `/tmp`.

## Author

by Paweł Pawełek
