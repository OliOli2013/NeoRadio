# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import io
import re
import json
import time
import unicodedata
import glob
import hashlib
try:
    import socket
except Exception:
    socket = None
try:
    import ssl
except Exception:
    ssl = None
try:
    import threading
except Exception:
    threading = None
try:
    from PIL import Image
except Exception:
    Image = None
try:
    from urllib2 import Request, urlopen
    from urlparse import urlparse, urljoin
except Exception:
    from urllib.request import Request, urlopen
    from urllib.parse import urlparse, urljoin


from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
try:
    from Screens.VirtualKeyBoard import VirtualKeyBoard
except Exception:
    VirtualKeyBoard = None

from Components.ActionMap import ActionMap
try:
    from Components.Console import Console as ComponentsConsole
except Exception:
    ComponentsConsole = None
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo, configfile
try:
    from Components.Language import language
except Exception:
    language = None
from enigma import eServiceReference, eTimer, getDesktop, iServiceInformation, ePoint
from Tools.Directories import resolveFilename, SCOPE_CONFIG

PLUGIN_VERSION = "1.3.4"
PLUGIN_NAME = "NeoRadio"
PLUGIN_TITLE = "NeoRadio Online"
PLUGIN_DESC = "NeoRadio Online"
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio"
CONFIG_DIR = resolveFilename(SCOPE_CONFIG)
FAV_FILE = os.path.join(CONFIG_DIR, "neoradio_favorites.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, "neoradio_history.json")
USER_STATIONS_FILE = os.path.join(CONFIG_DIR, "neoradio_user_stations.json")
BASE_STATIONS_FILE = os.path.join(PLUGIN_PATH, "stations.json")
COVER_DIR = os.path.join(PLUGIN_PATH, "covers")
DEFAULT_COVER = os.path.join(PLUGIN_PATH, "cover_default.png")
DEFAULT_PICON = os.path.join(PLUGIN_PATH, "visualradio.png")
DEFAULT_PICON_DIRS = [
    "/usr/share/enigma2/picon",
    "/usr/share/enigma2/piconlcd",
    "/usr/share/engma2/picon",
    "/usr/share/engma2/piconlcd",
    "/user/share/enigma2/picon",
    "/user/share/enigma2/piconlcd",
    "/user/share/engma2/picon",
    "/user/share/engma2/piconlcd",
    "/picon",
    "/data/picon",
    "/media/hdd/picon",
    "/media/hdd/piconlcd",
    "/media/usb/picon",
    "/media/usb/piconlcd",
    "/media/mmc/picon",
    "/media/mmc/piconlcd",
]
REMOTE_PICON_CACHE_DIR = os.path.join(CONFIG_DIR, "neoradio_picon_cache")
NETWORK_META_POLL_SECS = 18
NETWORK_META_TIMEOUT = 7
NETWORK_META_READ_LIMIT = 262144


PICON_ALIASES = {
    "polskie_radio_24": ["pr24", "polskieradio24", "polskie_radio24"],
    "radio_poland": ["polskieradiodlazagranicy", "radio_poland"],
    "radio_zet": ["radiozet", "radio_zet"],
    "rmf_fm": ["rmffm", "rmf_fm"],
    "rmf_classic": ["rmfclassic", "rmf_classic"],
    "rmf_maxx": ["rmfmaxx", "rmfmaxxx", "rmf_maxx", "rmfmax"],
    "polskie_radio_chopin": ["prchopin", "polskie_radio_chopin"],
    "polskie_radio_kierowcow": ["prkierowcow", "polskie_radio_kierowcow"],
    "polskie_radio_dzieciom": ["prdzieciom", "polskie_radio_dzieciom"],
    "radio_nowy_swiat": ["nowyswiat", "radio_nowy_swiat"],
    "radio_357": ["radio357", "radio_357"],
    "antyradio": ["antyradio_warszawa"],
    "melo": ["meloradio", "melo_radio"],
    "radio_plus": ["radioplus", "radio_plus"],
    "radio_pogoda": ["radiopogoda", "radio_pogoda"],
    "vox_fm": ["voxfm", "vox_fm"],
    "vox_dance": ["voxdance", "vox_dance", "voxdancefm"],
    "tok_fm": ["tokfm", "radiotok", "tok_fm"],
    "trojka": ["program3", "pr3", "polskieradio3", "trojka", "trujka"],
    "jedynka": ["program1", "pr1", "polskieradio1", "jedynka"],
    "dwojka": ["program2", "pr2", "polskieradio2", "dwojka"],
    "czworka": ["program4", "pr4", "polskieradio4", "czworka"],
    "zlote_przeboje_bialystok_101_fm": ["zloteprzeboje", "zlote_przeboje", "zloteprzebojebialystok"],
}

try:
    text_type = unicode
    binary_type = str
except NameError:
    text_type = str
    binary_type = bytes

if not hasattr(config.plugins, "neoradio"):
    config.plugins.neoradio = ConfigSubsection()
if not hasattr(config.plugins.neoradio, "last_filter"):
    config.plugins.neoradio.last_filter = ConfigText(default="All", fixed_size=False)
if not hasattr(config.plugins.neoradio, "last_station"):
    config.plugins.neoradio.last_station = ConfigText(default="", fixed_size=False)
if not hasattr(config.plugins.neoradio, "last_url"):
    config.plugins.neoradio.last_url = ConfigText(default="", fixed_size=False)
if not hasattr(config.plugins.neoradio, "keep_playing"):
    config.plugins.neoradio.keep_playing = ConfigYesNo(default=False)
if not hasattr(config.plugins.neoradio, "autoplay_last"):
    config.plugins.neoradio.autoplay_last = ConfigYesNo(default=False)
if not hasattr(config.plugins.neoradio, "picon_paths"):
    config.plugins.neoradio.picon_paths = ConfigText(default="", fixed_size=False)
if not hasattr(config.plugins.neoradio, "default_country"):
    config.plugins.neoradio.default_country = ConfigText(default="Polska", fixed_size=False)
if not hasattr(config.plugins.neoradio, "ui_language"):
    config.plugins.neoradio.ui_language = ConfigText(default="auto", fixed_size=False)
if not hasattr(config.plugins.neoradio, "screensaver_timeout"):
    config.plugins.neoradio.screensaver_timeout = ConfigText(default="0", fixed_size=False)
if not hasattr(config.plugins.neoradio, "github_manifest_url"):
    config.plugins.neoradio.github_manifest_url = ConfigText(default="https://raw.githubusercontent.com/OliOli2013/NeoRadio/main/manifest.json", fixed_size=False)

DEFAULT_GITHUB_MANIFEST_URL = "https://raw.githubusercontent.com/OliOli2013/NeoRadio/main/manifest.json"
UPDATE_TEMP_IPK = "/tmp/neoradio_update.ipk"


def to_text(value):
    if value is None:
        return text_type("")
    try:
        if isinstance(value, text_type):
            return value
    except Exception:
        pass
    try:
        if isinstance(value, binary_type):
            try:
                return value.decode("utf-8")
            except Exception:
                return value.decode("latin-1", "ignore")
    except Exception:
        pass
    try:
        return text_type(value)
    except Exception:
        try:
            return text_type(str(value), "utf-8", "ignore")
        except Exception:
            return text_type("")


def slugify(value):
    value = to_text(value)
    try:
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
    except Exception:
        try:
            value = value.encode("ascii", "ignore")
        except Exception:
            pass
    value = re.sub(r"[^a-zA-Z0-9]+", "_", to_text(value)).strip("_").lower()
    return value or "station"


def load_json_file(path, default_value):
    try:
        if os.path.exists(path):
            handle = io.open(path, "r", encoding="utf-8")
            data = json.load(handle)
            handle.close()
            return data
    except Exception:
        pass
    return default_value


def save_json_file(path, data):
    try:
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        handle = io.open(path, "w", encoding="utf-8")
        handle.write(to_text(payload))
        handle.close()
        return True
    except Exception:
        return False



COUNTRY_ALIASES = {
    "polska": u"Polska", "poland": u"Polska", "polen": u"Polska",
    "niemcy": u"Niemcy", "germany": u"Niemcy", "deutschland": u"Niemcy",
    "francja": u"Francja", "france": u"Francja", "frankreich": u"Francja",
    "wlochy": u"Włochy", "włochy": u"Włochy", "italy": u"Włochy", "italien": u"Włochy", "italia": u"Włochy",
    "arabic": u"Arabskie", "arab": u"Arabskie", "arabskie": u"Arabskie",
    "hiszpania": u"Hiszpania", "spain": u"Hiszpania", "spanien": u"Hiszpania",
    "szwajcaria": u"Szwajcaria", "switzerland": u"Szwajcaria", "schweiz": u"Szwajcaria",
    "austria": u"Austria", "osterreich": u"Austria", "oesterreich": u"Austria",
    "czechy": u"Czechy", "czechia": u"Czechy", "tschechien": u"Czechy",
    "usa": u"USA", "niederlande": u"Holandia", "netherlands": u"Holandia", "holandia": u"Holandia",
    "belgien": u"Belgia", "belgia": u"Belgia", "griechenland": u"Grecja", "grecja": u"Grecja",
    "slowakei": u"Słowacja", "slowacja": u"Słowacja", "portugal": u"Portugalia", "portugalia": u"Portugalia",
    "mexiko": u"Meksyk", "meksyk": u"Meksyk", "finland": u"Finlandia", "finlandia": u"Finlandia",
    "turkey": u"Turcja", "turcja": u"Turcja", "grossbritannien": u"Wielka Brytania", "gro_britannien": u"Wielka Brytania", "united_kingdom": u"Wielka Brytania", "uk": u"Wielka Brytania", "schottland": u"Wielka Brytania",
    "online": u"Online", "other": u"Inne", "inne": u"Inne",
}
STATION_LANGUAGE_ORDER = [u"Polski", u"Arabski", u"Francuski", u"Niemiecki", u"Włoski", u"Inne"]
LANGUAGE_BY_COUNTRY = {
    u"Polska": u"Polski",
    u"Arabskie": u"Arabski",
    u"Francja": u"Francuski",
    u"Niemcy": u"Niemiecki",
    u"Austria": u"Niemiecki",
    u"Szwajcaria": u"Niemiecki",
    u"Włochy": u"Włoski",
}
LANGUAGE_ALIASES = {
    "polski": u"Polski", "polish": u"Polski", "pl": u"Polski",
    "arabski": u"Arabski", "arabic": u"Arabski", "arab": u"Arabski", "ar": u"Arabski",
    "francuski": u"Francuski", "french": u"Francuski", "fr": u"Francuski",
    "niemiecki": u"Niemiecki", "german": u"Niemiecki", "de": u"Niemiecki",
    "wloski": u"Włoski", "wlochy": u"Włoski", "italian": u"Włoski", "it": u"Włoski",
    "inne": u"Inne", "other": u"Inne", "misc": u"Inne",
}


def normalize_country(value):
    raw = to_text(value).strip()
    if not raw:
        return u"Online"
    key = slugify(raw)
    return COUNTRY_ALIASES.get(key, raw)


def normalize_station_language(value, country=None, name=None, group=None, url=None):
    raw = to_text(value).strip()
    if raw:
        key = slugify(raw)
        if key in LANGUAGE_ALIASES:
            return LANGUAGE_ALIASES[key]
        if raw in STATION_LANGUAGE_ORDER:
            return raw
    country = normalize_country(country or u"")
    if country in LANGUAGE_BY_COUNTRY:
        return LANGUAGE_BY_COUNTRY[country]
    blob = u" %s %s %s " % (slugify(group or u""), slugify(name or u""), to_text(url or u"").lower())
    if u"arabic" in blob or u" arab " in blob or u"quran" in blob or u"koran" in blob:
        return u"Arabski"
    if u"france" in blob or u"frankreich" in blob or u"hotmix" in blob or u"prysm" in blob or u".fr/" in blob:
        return u"Francuski"
    if u"italy" in blob or u"italien" in blob or u"italia" in blob or u".it/" in blob:
        return u"Włoski"
    if u"deutschland" in blob or u"germany" in blob or u"antenne" in blob or u"hitradio" in blob or u"radio_bob" in blob or u"schlager" in blob or u".de/" in blob:
        return u"Niemiecki"
    if u"polska" in blob or u"poland" in blob or u"polen" in blob or u" rmf" in blob or u"radio_zet" in blob or u"polskie_radio" in blob or u"eska" in blob:
        return u"Polski"
    return u"Inne"


def normalize_stream_url_key(url):
    url = to_text(url).strip().lower()
    url = url.replace(u"%3a", u":").replace(u"%3A", u":").replace(u"%2f", u"/").replace(u"%2F", u"/")
    try:
        url = re.sub(r"[\?#].*$", "", url)
    except Exception:
        pass
    return url.rstrip(u"/")


def station_identity_key(station):
    if not station:
        return text_type("")
    url_key = normalize_stream_url_key(station.get("url", u""))
    if url_key:
        return u"url:" + url_key
    return u"name:" + slugify(station.get("name", u"")) + u"|" + normalize_station_language(station.get("language", u""), station.get("country", u""))

def normalize_station(entry):
    name = to_text(entry.get("name", "Unknown")).strip()
    url = to_text(entry.get("url", "")).strip()
    genre = to_text(entry.get("genre", "Other")).strip() or u"Other"
    group = to_text(entry.get("group", entry.get("genre", ""))).strip() or genre
    country = normalize_country(entry.get("country", "Online"))
    lang = normalize_station_language(entry.get("language", ""), country, name, group, url)
    return {
        "name": name,
        "url": url,
        "genre": genre,
        "country": country,
        "language": lang,
        "bitrate": to_text(entry.get("bitrate", "?")),
        "description": to_text(entry.get("description", "")),
        "homepage": to_text(entry.get("homepage", "")),
        "picon": to_text(entry.get("picon", "")),
        "picon_url": to_text(entry.get("picon_url", "")),
        "metadata_url": to_text(entry.get("metadata_url", "")),
        "metadata_type": to_text(entry.get("metadata_type", "auto")),
        "metadata_title_key": to_text(entry.get("metadata_title_key", "")),
        "metadata_artist_key": to_text(entry.get("metadata_artist_key", "")),
        "metadata_album_key": to_text(entry.get("metadata_album_key", "")),
        "metadata_text_key": to_text(entry.get("metadata_text_key", "")),
        "metadata_program_key": to_text(entry.get("metadata_program_key", "")),
        "metadata_cover_key": to_text(entry.get("metadata_cover_key", "")),
        "group": group,
    }


def load_stations():
    stations = []
    seen_urls = {}
    seen_names = {}
    for src in (BASE_STATIONS_FILE, USER_STATIONS_FILE):
        for item in load_json_file(src, []):
            try:
                norm = normalize_station(item)
                if not norm.get("url"):
                    continue
                url_key = normalize_stream_url_key(norm.get("url", ""))
                name_key = slugify(norm.get("name", "")) + u"|" + normalize_station_language(norm.get("language", ""), norm.get("country", ""))
                if (url_key and url_key in seen_urls) or (name_key and name_key in seen_names):
                    continue
                stations.append(norm)
                if url_key:
                    seen_urls[url_key] = True
                if name_key:
                    seen_names[name_key] = True
            except Exception:
                pass
    def sort_key(item):
        lang = normalize_station_language(item.get("language", ""), item.get("country", ""))
        try:
            lang_idx = STATION_LANGUAGE_ORDER.index(lang)
        except Exception:
            lang_idx = 99
        return (lang_idx, to_text(item.get("country", "")).lower(), to_text(item.get("group", item.get("genre", ""))).lower(), to_text(item.get("name", "")).lower())
    stations.sort(key=sort_key)
    return stations


def load_favorites():
    return [to_text(x) for x in load_json_file(FAV_FILE, []) if to_text(x)]




def load_history():
    result = []
    seen = {}
    for item in load_json_file(HISTORY_FILE, []):
        try:
            norm = normalize_station(item)
            key = station_identity_key(norm)
            if key and key not in seen:
                result.append(norm)
                seen[key] = True
        except Exception:
            pass
    return result[:30]


def remember_played_station(station):
    if not station:
        return False
    try:
        norm = normalize_station(station)
        norm["played_at"] = int(time.time())
        key = station_identity_key(norm)
        clean = [norm]
        seen = {key: True}
        for item in load_history():
            item_key = station_identity_key(item)
            if item_key and item_key not in seen:
                clean.append(item)
                seen[item_key] = True
            if len(clean) >= 30:
                break
        return save_json_file(HISTORY_FILE, clean)
    except Exception:
        return False

def save_favorites(favorites):
    clean = []
    seen = {}
    for item in favorites:
        item = to_text(item)
        if item and item not in seen:
            clean.append(item)
            seen[item] = True
    return save_json_file(FAV_FILE, clean)


def unique_text_list(items):
    result = []
    seen = {}
    for item in items:
        item = to_text(item).strip()
        if item and item not in seen:
            result.append(item)
            seen[item] = True
    return result


def split_picon_paths(raw_value):
    raw_value = to_text(raw_value)
    if not raw_value:
        return []
    parts = re.split(r"[;,:\n]+", raw_value)
    return unique_text_list(parts)


def discover_mount_picon_dirs():
    result = []
    patterns = ["/media/*", "/autofs/*", "/mnt/*"]
    suffixes = [
        "picon",
        "piconlcd",
        "usr/share/enigma2/picon",
        "usr/share/enigma2/piconlcd",
        "enigma2/picon",
        "enigma2/piconlcd",
    ]
    for pattern in patterns:
        for base in glob.glob(pattern):
            for suffix in suffixes:
                result.append(os.path.join(base, suffix))
    return unique_text_list(result)


def normalize_lookup_name(value):
    value = slugify(value).replace("_", "")
    value = value.replace("polskieradio", "pr")
    return value


def country_to_filter_label(country):
    country = to_text(country).strip()
    return u"Kraj: %s" % country if country else u"Kraj: Online"


I18N = {
    "en": {
        "plugin_desc": u"Modern internet radio for Enigma2 / Python 2/3",
        "stations_online": u"Online stations",
        "header_title": u"NeoRadio Online",
        "help": u"OK/Green=Play  Yellow=Fav  Blue=Filters  Menu=Settings  Info=Details",
        "status_ready": u"Status: ready",
        "by_author": u"by Paweł Pawełek",
        "station_desc_title": u"Station description",
        "spectrum_title": u"Audio spectrum",
        "np_header": u"RDS / ICY / Now playing",
        "np_title": u"Title: -",
        "np_artist": u"Artist: -",
        "np_album": u"Album/Source: -",
        "np_wait": u"Metadata: waiting",
        "red_exit": u"Red: Exit",
        "green_play": u"Green: Play",
        "yellow_fav": u"Yellow: Fav",
        "blue_search": u"Blue: Search",
        "blue_filter": u"Blue: Filters",
        "menu_cfg": u"Menu: Filters/Settings",
        "info_details": u"Info: Details",
        "picon_title": u"Station logo",
        "all": u"All",
        "favorites": u"Favorites",
        "recent": u"Recently played",
    "online": u"Online",
    "other": u"Inne",
    "equalizer_visual": u"Wizualny EQ",
        "online": u"Online",
        "other": u"Other",
        "equalizer_visual": u"Visual EQ",
        "country_filter": u"Country: %s",
        "genre_filter": u"Genre: %s",
        "language_filter": u"Language: %s",
        "main_country": u"Main country",
        "all_countries": u"All countries",
        "filter": u"filter",
        "search": u"Search",
        "none": u"-",
        "no_stations": u"(no stations for selected filter)",
        "summary": u"Main country: %s | filter: %s | total: %d",
        "no_station": u"No station",
        "add_or_change": u"Add stations or change filter.",
        "nothing_to_show": u"No entries to display.",
        "fav_yes": u"YES",
        "fav_no": u"NO",
        "fav_label": u"Favorite: %s",
        "meta_line": u"%s | %s | %s kbps | Favorite: %s",
        "extra_line": u"WWW: %s\nUser stations file: %s",
        "removed_fav": u"Removed from favorites: %s",
        "added_fav": u"Added to favorites: %s",
        "status_prefix": u"Status: %s",
        "search_station": u"Search station",
        "no_keyboard": u"No on-screen keyboard in this Enigma2 image.",
        "title_fmt": u"Title: %s",
        "artist_fmt": u"Artist: %s",
        "album_fmt": u"Album/Source: %s",
        "metadata_active": u"Metadata: active (ICY/RDS from stream)",
        "metadata_missing": u"Metadata: not available in this stream or image does not expose it",
        "metadata_network_active": u"Metadata: active (Enigma2/network)",
        "metadata_source_service": u"Source: Enigma2 service",
        "metadata_source_icy": u"Source: ICY stream",
        "metadata_source_endpoint": u"Source: station endpoint",
        "metadata_source_hybrid": u"Source: ICY + endpoint",
        "details_title": u"Details",
        "details_text": u"NeoRadio Online %s\n\nName: %s\nGenre: %s\nCountry: %s\nBitrate: %s kbps\n\nDescription:\n%s\n\nURL:\n%s\n\nWWW:\n%s",
        "menu_title": u"NeoRadio - Menu",
        "menu_filter": u"Filter: %s",
        "menu_clear_search": u"Clear search",
        "menu_search": u"Search station",
        "menu_choose_filter": u"Choose station filter / bouquet",
        "menu_station_language": u"Station language: %s",
        "filter_title": u"NeoRadio - Filters / bouquets",
        "choose_station_language": u"Choose station language",
        "station_language_set": u"station language = %s",
        "menu_keep": u"Toggle: Keep playing after exit = %s",
        "menu_autoplay": u"Toggle: Autoplay last station = %s",
        "yes": u"YES",
        "no": u"NO",
        "menu_country": u"Main country: %s",
        "menu_lang": u"Language: %s",
        "menu_saver": u"Screensaver: %s",
        "menu_picons": u"Picon paths: %s",
        "menu_reload": u"Reload station list",
        "menu_github_url": u"GitHub update URL: %s",
        "menu_github_check": u"Check / install updates from GitHub",
        "menu_about": u"Plugin information",
        "no_keyboard_settings": u"No on-screen keyboard. You can also set the path manually in Enigma2 settings.",
        "picon_paths_title": u"Picon paths (separate with ;) ",
        "reloaded": u"station list refreshed",
        "about_text": u"NeoRadio Online %s\n\nModern Enigma2 plugin for internet radio.\nFeatures:\n- internet radio\n- favorite stations\n- search and filters\n- country and station language selection\n- picons from SAT/IPTV\n- RDS/ICY metadata\n- UI PL/EN\n- optional screensaver\n- GitHub update support\n\nConfiguration files:\n%s\n%s",
        "choose_country": u"Choose main country",
        "country_set": u"main country = %s",
        "country_all": u"main country = all",
        "auto": u"Auto",
        "polish": u"Polish",
        "english": u"English",
        "choose_language": u"Choose UI language",
        "lang_set": u"language = %s",
        "screensaver_off": u"Off",
        "screensaver_min": u"%s min",
        "choose_saver": u"Choose screensaver timeout",
        "saver_set": u"screensaver = %s",
        "saved_picons": u"saved custom picon paths",
        "auto_picons": u"automatic picon search enabled",
        "play_missing": u"No station to play.",
        "play_resolve_fail": u"Could not resolve stream URL for this station.",
        "playing": u"playing - %s",
        "playlist_resolved": u"Metadata: playing after playlist resolve (PLS/M3U/ASX)",
        "metadata_waiting": u"Metadata: waiting for ICY/RDS...",
        "github_not_set": u"GitHub update URL is not configured yet.",
        "github_checking": u"Checking GitHub updates...",
        "github_up_to_date": u"NeoRadio is up to date.",
        "github_new_version": u"New version available: %s",
        "github_install_prompt": u"New version available: %s\n\nChangelog:\n%s\n\nDownload and install now?",
        "github_installing": u"installing update %s",
        "github_install_ok": u"Update %s installed successfully.\n\nRestart Enigma2 GUI now?",
        "github_install_fail": u"Update %s failed.\n\n%s",
        "github_missing_ipk": u"Manifest does not contain an IPK download URL.",
        "github_restarting": u"restarting Enigma2 GUI...",
        "github_restart_later": u"update installed - restart GUI later",
        "github_error": u"Could not check GitHub updates.",
        "screensaver_hint": u"Press any key to return",
        "screensaver_title": u"NeoRadio screensaver",
    },
    "pl": {}
}
I18N["pl"] = {
    "plugin_desc": u"Nowoczesne radio internetowe dla Enigma2 / Python 2/3",
    "stations_online": u"Stacje online",
    "header_title": u"NeoRadio Online",
    "help": u"OK/Green=Play  Yellow=Fav  Blue=Filtry  Menu=Ustawienia  Info=Szczegóły",
    "status_ready": u"Stan: gotowy",
    "by_author": u"by Paweł Pawełek",
    "station_desc_title": u"Opis stacji",
    "spectrum_title": u"Widmo audio",
    "np_header": u"RDS / ICY / Teraz gra",
    "np_title": u"Tytuł: -",
    "np_artist": u"Wykonawca: -",
    "np_album": u"Album/Źródło: -",
    "np_wait": u"Metadane: oczekiwanie",
    "red_exit": u"Czerwony: Wyjdź",
    "green_play": u"Zielony: Play",
    "yellow_fav": u"Żółty: Fav",
    "blue_search": u"Niebieski: Szukaj",
    "blue_filter": u"Niebieski: Filtry",
    "menu_cfg": u"Menu: Filtr/Ustawienia",
    "info_details": u"Info: Szczegóły",
    "picon_title": u"Logo stacji",
    "all": u"Wszystkie",
    "favorites": u"Ulubione",
    "recent": u"Ostatnio odtwarzane",
    "online": u"Online",
    "other": u"Inne",
    "equalizer_visual": u"Wizualny EQ",
    "country_filter": u"Kraj: %s",
    "genre_filter": u"Gatunek: %s",
    "language_filter": u"Język: %s",
    "main_country": u"Kraj główny",
    "all_countries": u"Wszystkie kraje",
    "filter": u"filtr",
    "search": u"Szukaj",
    "none": u"-",
    "no_stations": u"(brak stacji dla wybranego filtra)",
    "summary": u"Kraj główny: %s | filtr: %s | razem: %d",
    "no_station": u"Brak stacji",
    "add_or_change": u"Dodaj stacje lub zmień filtr.",
    "nothing_to_show": u"Brak pozycji do wyświetlenia.",
    "fav_yes": u"TAK",
    "fav_no": u"NIE",
    "fav_label": u"Ulubione: %s",
    "meta_line": u"%s | %s | %s kbps | Ulubione: %s",
    "extra_line": u"WWW: %s\nPlik własnych stacji: %s",
    "removed_fav": u"Usunięto z ulubionych: %s",
    "added_fav": u"Dodano do ulubionych: %s",
    "status_prefix": u"Stan: %s",
    "search_station": u"Szukaj stacji",
    "no_keyboard": u"Brak klawiatury ekranowej w tym obrazie Enigma2.",
    "title_fmt": u"Tytuł: %s",
    "artist_fmt": u"Wykonawca: %s",
    "album_fmt": u"Album/Źródło: %s",
    "metadata_active": u"Metadane: aktywne (ICY/RDS ze streamu)",
    "metadata_missing": u"Metadane: brak w tym strumieniu lub image ich nie udostępnia",
    "metadata_network_active": u"Metadane: aktywne (Enigma2/sieć)",
    "metadata_source_service": u"Źródło: usługa Enigma2",
    "metadata_source_icy": u"Źródło: strumień ICY",
    "metadata_source_endpoint": u"Źródło: endpoint stacji",
    "metadata_source_hybrid": u"Źródło: ICY + endpoint",
    "details_title": u"Szczegóły",
    "details_text": u"NeoRadio Online %s\n\nNazwa: %s\nGatunek: %s\nKraj: %s\nBitrate: %s kbps\n\nOpis:\n%s\n\nURL:\n%s\n\nWWW:\n%s",
    "menu_title": u"NeoRadio - Menu",
    "menu_filter": u"Filtr: %s",
    "menu_clear_search": u"Wyczyść wyszukiwanie",
    "menu_search": u"Szukaj stacji",
    "menu_choose_filter": u"Wybierz filtr / bukiet stacji",
    "menu_station_language": u"Język stacji: %s",
    "filter_title": u"NeoRadio - filtry / bukiety",
    "choose_station_language": u"Wybierz język stacji",
    "station_language_set": u"język stacji = %s",
    "menu_keep": u"Przełącz: Odtwarzaj po wyjściu = %s",
    "menu_autoplay": u"Przełącz: Autoplay ostatniej stacji = %s",
    "yes": u"TAK",
    "no": u"NIE",
    "menu_country": u"Kraj główny: %s",
    "menu_lang": u"Język: %s",
    "menu_saver": u"Wygaszacz: %s",
    "menu_picons": u"Ścieżki piconów: %s",
    "menu_reload": u"Przeładuj listę stacji",
    "menu_github_url": u"URL aktualizacji GitHub: %s",
    "menu_github_check": u"Sprawdź / zainstaluj aktualizacje z GitHub",
    "menu_about": u"Informacje o wtyczce",
    "no_keyboard_settings": u"Brak klawiatury ekranowej. Ścieżkę możesz też ustawić ręcznie w ustawieniach Enigma2.",
    "picon_paths_title": u"Ścieżki piconów (oddzielaj średnikiem ;)",
    "reloaded": u"lista stacji odświeżona",
    "about_text": u"NeoRadio Online %s\n\nNowoczesna wtyczka Enigma2 do radia internetowego.\nFunkcje:\n- radio internetowe\n- ulubione\n- wyszukiwanie i filtry\n- wybór kraju i języka stacji\n- picony z SAT/IPTV\n- metadane RDS/ICY\n- interfejs PL/EN\n- opcjonalny wygaszacz\n- obsługa aktualizacji z GitHub\n\nPliki konfiguracyjne:\n%s\n%s",
    "choose_country": u"Wybierz kraj główny",
    "country_set": u"kraj główny = %s",
    "country_all": u"kraj główny = wszystkie",
    "auto": u"Auto",
    "polish": u"Polski",
    "english": u"English",
    "choose_language": u"Wybierz język interfejsu",
    "lang_set": u"język = %s",
    "screensaver_off": u"Wyłączony",
    "screensaver_min": u"%s min",
    "choose_saver": u"Wybierz czas wygaszacza",
    "saver_set": u"wygaszacz = %s",
    "saved_picons": u"zapisano własne ścieżki piconów",
    "auto_picons": u"włączono automatyczne szukanie piconów",
    "play_missing": u"Brak stacji do odtworzenia.",
    "play_resolve_fail": u"Nie udało się ustalić adresu strumienia dla tej stacji.",
    "playing": u"odtwarzanie - %s",
    "playlist_resolved": u"Metadane: odtwarzanie po rozwiązaniu playlisty (PLS/M3U/ASX)",
    "metadata_waiting": u"Metadane: oczekiwanie na ICY/RDS...",
    "github_not_set": u"URL aktualizacji GitHub nie jest jeszcze ustawiony.",
    "github_checking": u"Sprawdzanie aktualizacji GitHub...",
    "github_up_to_date": u"NeoRadio jest aktualne.",
    "github_new_version": u"Dostępna nowa wersja: %s",
    "github_install_prompt": u"Dostępna nowa wersja: %s\n\nLista zmian:\n%s\n\nPobrać i zainstalować teraz?",
    "github_installing": u"instalacja aktualizacji %s",
    "github_install_ok": u"Aktualizacja %s została zainstalowana.\n\nZrestartować teraz GUI Enigma2?",
    "github_install_fail": u"Aktualizacja %s nie powiodła się.\n\n%s",
    "github_missing_ipk": u"Manifest nie zawiera linku do pliku IPK.",
    "github_restarting": u"restart GUI Enigma2...",
    "github_restart_later": u"aktualizacja zainstalowana - zrestartuj GUI później",
    "github_error": u"Nie udało się sprawdzić aktualizacji GitHub.",
    "screensaver_hint": u"Naciśnij dowolny klawisz, aby wrócić",
    "screensaver_title": u"Wygaszacz NeoRadio",
}

def detect_system_language():
    try:
        if language is not None and hasattr(language, 'getLanguage'):
            code = to_text(language.getLanguage()).lower()
            if code.startswith('pl'):
                return 'pl'
    except Exception:
        pass
    return 'en'

def get_active_language():
    value = to_text(getattr(config.plugins.neoradio.ui_language, 'value', 'auto')).strip().lower()
    if value in ('pl', 'en'):
        return value
    return detect_system_language()


WEEKDAY_NAMES = {
    'en': [u'Monday', u'Tuesday', u'Wednesday', u'Thursday', u'Friday', u'Saturday', u'Sunday'],
    'pl': [u'poniedziałek', u'wtorek', u'środa', u'czwartek', u'piątek', u'sobota', u'niedziela'],
}

def localized_weekday_name(ts=None):
    if ts is None:
        ts = time.localtime()
    try:
        idx = int(time.strftime('%w', ts))
    except Exception:
        idx = 0
    # Python strftime %w => Sunday=0
    idx = (idx - 1) % 7
    lang = get_active_language()
    return WEEKDAY_NAMES.get(lang, WEEKDAY_NAMES['en'])[idx]


def format_ui_date(ts=None, with_weekday=True):
    if ts is None:
        ts = time.localtime()
    base = to_text(time.strftime('%d.%m.%Y', ts))
    if with_weekday:
        return u'%s  •  %s' % (base, localized_weekday_name(ts))
    return base


def format_ui_stamp(ts=None):
    if ts is None:
        ts = time.localtime()
    return to_text(time.strftime('%Y-%m-%d  %H:%M:%S', ts))

def tr(key, *args):
    lang = get_active_language()
    payload = I18N.get(lang, {}).get(key, I18N['en'].get(key, key))
    try:
        if args:
            return payload % args
    except Exception:
        pass
    return payload

def format_country_filter(country):
    country = to_text(country).strip()
    return tr('country_filter', country if country else tr('online'))

def format_genre_filter(genre):
    genre = to_text(genre).strip()
    return tr('genre_filter', genre if genre else tr('other'))

def format_language_filter(lang):
    lang = normalize_station_language(lang)
    return tr('language_filter', lang if lang else tr('other'))

def language_label(value):
    value = to_text(value).strip().lower()
    if value == 'pl':
        return tr('polish')
    if value == 'en':
        return tr('english')
    return tr('auto')

def get_screensaver_timeout_minutes():
    raw = to_text(getattr(config.plugins.neoradio.screensaver_timeout, 'value', '0')).strip()
    try:
        return max(0, int(raw))
    except Exception:
        return 0

def screensaver_timeout_label(value=None):
    minutes = get_screensaver_timeout_minutes() if value is None else int(value)
    if minutes <= 0:
        return tr('screensaver_off')
    return tr('screensaver_min', to_text(minutes))


def parse_version_tuple(value):
    numbers = re.findall(r'\d+', to_text(value))
    if not numbers:
        return (0,)
    try:
        return tuple([int(x) for x in numbers[:6]])
    except Exception:
        return (0,)


def is_remote_version_newer(remote_version, local_version):
    return parse_version_tuple(remote_version) > parse_version_tuple(local_version)


def extract_manifest_ipk_url(info):
    for key in ('ipk', 'ipk_url', 'download', 'url'):
        value = to_text(info.get(key, u'')).strip()
        if value:
            return value
    return text_type('')


def is_playlist_like_url(url):
    lower = to_text(url).strip().lower()
    parsed = urlparse(lower)
    path = parsed.path or lower
    for ext in ('.pls', '.m3u', '.m3u8', '.asx', '.xspf'):
        if path.endswith(ext) or ext + '?' in lower:
            return True
    return False


def fetch_text_url(url, timeout=8):
    try:
        request = Request(to_text(url), headers={"User-Agent": "NeoRadio/1.0"})
        handle = urlopen(request, timeout=timeout)
        data = handle.read(65535)
        try:
            handle.close()
        except Exception:
            pass
        if isinstance(data, binary_type):
            try:
                return data.decode("utf-8")
            except Exception:
                return data.decode("latin-1", "ignore")
        return to_text(data)
    except Exception:
        return text_type("")


def parse_playlist_content(text):
    text = to_text(text).strip()
    if not text:
        return None
    for line in text.splitlines():
        line = to_text(line).strip()
        if not line:
            continue
        if line.lower().startswith('file') and '=' in line:
            candidate = line.split('=', 1)[1].strip()
            if candidate.startswith('http'):
                return candidate
    for line in text.splitlines():
        line = to_text(line).strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('http'):
            return line
    match = re.search(r"href\s*=\s*['\"]([^'\"]+)['\"]", text, re.I)
    if match:
        return to_text(match.group(1)).strip()
    match = re.search(r"(https?://[^\s'\"<>()]+)", text, re.I)
    if match:
        return to_text(match.group(1)).strip()
    return None

def shorten_text(value, limit):
    value = to_text(value).strip()
    if len(value) <= int(limit):
        return value
    return value[:max(0, int(limit) - 3)].rstrip() + u"..."


def safe_int(value, default=0):
    try:
        return int(to_text(value).strip())
    except Exception:
        return default


def bytes_to_text(payload):
    if payload is None:
        return text_type("")
    try:
        if isinstance(payload, binary_type):
            try:
                return payload.decode('utf-8')
            except Exception:
                return payload.decode('latin-1', 'ignore')
    except Exception:
        pass
    return to_text(payload)


def first_byte_value(payload):
    if payload is None:
        return 0
    try:
        if isinstance(payload, int):
            return int(payload)
    except Exception:
        pass
    try:
        return ord(payload[:1])
    except Exception:
        return 0


def read_exact_bytes(handle, size):
    size = max(0, safe_int(size, 0))
    if size <= 0:
        return b''
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = handle.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    if not chunks:
        return b''
    try:
        return b''.join(chunks)
    except Exception:
        output = b''
        for item in chunks:
            output += item
        return output


def parse_icy_metadata_blob(blob):
    text = bytes_to_text(blob).replace(u'\x00', u' ').strip()
    if not text:
        return {}
    result = {}
    for key, value in re.findall(r"([A-Za-z0-9_]+)='([^']*)'", text):
        result[to_text(key).strip().lower()] = to_text(value).strip()
    if not result and u'StreamTitle=' in text:
        match = re.search(r"StreamTitle='([^']*)'", text)
        if match:
            result['streamtitle'] = to_text(match.group(1)).strip()
    return result


def split_artist_title(value):
    value = to_text(value).strip()
    if not value:
        return text_type(''), text_type('')
    separators = [u' - ', u' – ', u' — ', u' | ']
    for sep in separators:
        if sep in value:
            left, right = value.split(sep, 1)
            left = left.strip()
            right = right.strip()
            if left and right:
                return left, right
    return text_type(''), value


def extract_nested_value(data, key_path):
    key_path = to_text(key_path).strip()
    if not key_path or data is None:
        return text_type('')
    current = data
    for part in [p for p in key_path.split('.') if p]:
        if isinstance(current, dict):
            if part in current:
                current = current.get(part)
                continue
            lowered = {}
            try:
                lowered = dict((to_text(k).lower(), v) for k, v in current.items())
            except Exception:
                lowered = {}
            current = lowered.get(part.lower())
        elif isinstance(current, list):
            idx = safe_int(part, -1)
            if idx < 0 or idx >= len(current):
                return text_type('')
            current = current[idx]
        else:
            return text_type('')
    if isinstance(current, (dict, list)):
        try:
            return to_text(json.dumps(current, ensure_ascii=False))
        except Exception:
            return text_type('')
    return to_text(current).strip()


def first_present_value(data, keys):
    for key in keys:
        value = extract_nested_value(data, key)
        if value:
            return value
    return text_type('')


def open_stream_request(url, timeout=NETWORK_META_TIMEOUT):
    if socket is None:
        raise Exception('socket unavailable')
    parsed = urlparse(to_text(url))
    scheme = to_text(parsed.scheme or 'http').lower()
    host = to_text(parsed.hostname or '')
    if not host:
        raise Exception('missing host')
    port = parsed.port or (443 if scheme == 'https' else 80)
    path = to_text(parsed.path or '/')
    if parsed.query:
        path += '?' + to_text(parsed.query)
    sock = socket.create_connection((host, port), timeout)
    try:
        if scheme == 'https':
            if ssl is None:
                raise Exception('ssl unavailable')
            try:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            except Exception:
                sock = ssl.wrap_socket(sock)
        request = (
            'GET %s HTTP/1.0\r\n'
            'Host: %s\r\n'
            'User-Agent: NeoRadio/%s\r\n'
            'Icy-MetaData: 1\r\n'
            'Accept: */*\r\n'
            'Connection: close\r\n\r\n'
        ) % (path, host, PLUGIN_VERSION)
        try:
            sock.sendall(request.encode('utf-8'))
        except Exception:
            sock.sendall(binary_type(request))
        handle = sock.makefile('rb')
        status_line = bytes_to_text(handle.readline()).strip()
        headers = {}
        while True:
            raw_line = handle.readline()
            if not raw_line or raw_line in (b'\r\n', b'\n'):
                break
            line = bytes_to_text(raw_line).strip()
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            headers[to_text(key).strip().lower()] = to_text(value).strip()
        return sock, handle, status_line, headers
    except Exception:
        try:
            sock.close()
        except Exception:
            pass
        raise


def parse_status_code(status_line):
    match = re.search(r'(\d{3})', to_text(status_line))
    if match:
        return safe_int(match.group(1), 0)
    return 0


def fetch_icy_stream_metadata(url, timeout=NETWORK_META_TIMEOUT, redirects=2):
    current_url = to_text(url).strip()
    attempt = 0
    while current_url and attempt <= redirects:
        attempt += 1
        sock = None
        handle = None
        try:
            sock, handle, status_line, headers = open_stream_request(current_url, timeout=timeout)
            status_code = parse_status_code(status_line)
            if status_code in (301, 302, 303, 307, 308):
                redirect_url = to_text(headers.get('location', '')).strip()
                if redirect_url:
                    current_url = urljoin(current_url, redirect_url)
                    try:
                        handle.close()
                    except Exception:
                        pass
                    try:
                        sock.close()
                    except Exception:
                        pass
                    continue
            meta = {
                'source_kind': 'icy',
                'stream_name': to_text(headers.get('icy-name', '')).strip(),
                'stream_description': to_text(headers.get('icy-description', '')).strip(),
                'stream_genre': to_text(headers.get('icy-genre', '')).strip(),
                'stream_homepage': to_text(headers.get('icy-url', '')).strip(),
                'stream_bitrate': to_text(headers.get('icy-br', '')).strip(),
                'metaint': safe_int(headers.get('icy-metaint', '0'), 0),
                'stream_url': current_url,
            }
            metaint = meta.get('metaint', 0)
            if metaint > 0 and metaint <= NETWORK_META_READ_LIMIT:
                read_exact_bytes(handle, metaint)
                size_byte = handle.read(1)
                block_len = first_byte_value(size_byte) * 16
                if block_len > 0 and block_len <= NETWORK_META_READ_LIMIT:
                    payload = parse_icy_metadata_blob(read_exact_bytes(handle, block_len))
                    raw_title = to_text(payload.get('streamtitle', '')).strip()
                    raw_url = to_text(payload.get('streamurl', '')).strip()
                    if raw_title:
                        artist, title = split_artist_title(raw_title)
                        meta['raw_title'] = raw_title
                        meta['radio_text'] = raw_title
                        meta['title'] = title or raw_title
                        meta['artist'] = artist
                    if raw_url:
                        meta['info_url'] = raw_url
            try:
                handle.close()
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass
            if meta.get('title') or meta.get('radio_text') or meta.get('stream_name') or meta.get('stream_description'):
                return meta
            return None
        except Exception:
            try:
                if handle is not None:
                    handle.close()
            except Exception:
                pass
            try:
                if sock is not None:
                    sock.close()
            except Exception:
                pass
            return None
    return None


def fetch_station_endpoint_metadata(station, timeout=NETWORK_META_TIMEOUT):
    if not station:
        return None
    metadata_url = to_text(station.get('metadata_url', '')).strip()
    if not metadata_url:
        return None
    try:
        request = Request(metadata_url, headers={'User-Agent': 'NeoRadio/%s' % PLUGIN_VERSION, 'Accept': 'application/json,text/plain,*/*'})
        handle = urlopen(request, timeout=timeout)
        payload = handle.read(65535)
        content_type = to_text(handle.info().get('Content-Type', '')).lower()
        try:
            handle.close()
        except Exception:
            pass
    except Exception:
        return None
    metadata_type = to_text(station.get('metadata_type', 'auto')).strip().lower()
    text_payload = bytes_to_text(payload).strip()
    info = {
        'source_kind': 'endpoint',
        'stream_url': metadata_url,
    }
    if metadata_type in ('json', 'auto') or 'json' in content_type:
        try:
            data = json.loads(text_payload)
            title = extract_nested_value(data, station.get('metadata_title_key', '')) or first_present_value(data, ['title', 'song.title', 'song.name', 'song', 'now_playing.song.title', 'now_playing.song.text', 'now_playing.title', 'currentSong.title', 'current.title'])
            artist = extract_nested_value(data, station.get('metadata_artist_key', '')) or first_present_value(data, ['artist', 'song.artist', 'now_playing.song.artist', 'currentSong.artist', 'current.artist'])
            album = extract_nested_value(data, station.get('metadata_album_key', '')) or first_present_value(data, ['album', 'song.album', 'now_playing.song.album', 'currentSong.album'])
            radio_text = extract_nested_value(data, station.get('metadata_text_key', '')) or first_present_value(data, ['text', 'radio_text', 'now_playing.song.text', 'song.text', 'message'])
            program = extract_nested_value(data, station.get('metadata_program_key', '')) or first_present_value(data, ['program', 'show', 'audycja', 'current_show', 'now_playing.show'])
            cover_url = extract_nested_value(data, station.get('metadata_cover_key', '')) or first_present_value(data, ['art', 'artwork', 'cover', 'cover_url', 'image', 'song.art'])
            if title:
                info['title'] = title
            if artist:
                info['artist'] = artist
            if album:
                info['album'] = album
            if radio_text:
                info['radio_text'] = radio_text
            if program:
                info['program'] = program
            if cover_url:
                info['cover_url'] = cover_url
            if info.get('title') or info.get('artist') or info.get('program') or info.get('radio_text'):
                return info
        except Exception:
            pass
    cleaned = re.sub(r'\s+', ' ', text_payload).strip()
    if cleaned:
        artist, title = split_artist_title(cleaned)
        info['raw_title'] = cleaned
        info['radio_text'] = cleaned
        info['title'] = title or cleaned
        if artist:
            info['artist'] = artist
        return info
    return None


def merge_metadata_payloads(primary, secondary):
    primary = dict(primary or {})
    secondary = dict(secondary or {})
    merged = {}
    for key in set(list(primary.keys()) + list(secondary.keys())):
        merged[key] = primary.get(key) or secondary.get(key)
    return merged


def fetch_station_network_metadata(station, stream_url):
    endpoint_meta = fetch_station_endpoint_metadata(station, timeout=NETWORK_META_TIMEOUT) or {}
    icy_meta = fetch_icy_stream_metadata(stream_url, timeout=NETWORK_META_TIMEOUT) or {}
    if endpoint_meta and icy_meta:
        merged = merge_metadata_payloads(endpoint_meta, icy_meta)
        merged['source_kind'] = 'hybrid'
        return merged
    if endpoint_meta:
        return endpoint_meta
    if icy_meta:
        return icy_meta
    return None


def service_ref_to_picon_key(service_ref):
    ref = to_text(service_ref).strip()
    if not ref:
        return text_type("")
    ref = ref.split('::', 1)[0].split('#', 1)[0].strip()
    ref = ref.replace(':', '_').strip('_')
    return ref


def image_size_tuple(path):
    if not Image:
        return (0, 0)
    try:
        img = Image.open(path)
        return img.size
    except Exception:
        return (0, 0)


def is_usable_picon_image(path):
    width, height = image_size_tuple(path)
    if width <= 0 or height <= 0:
        return True
    ratio = float(width) / float(height)
    if ratio > 2.35 or ratio < 0.45:
        return False
    if width < 60 or height < 30:
        return False
    if width > 900 or height > 600:
        return False
    return True


def get_skin():
    width = getDesktop(0).size().width()
    if width >= 1920:
        return """
        <screen name="NeoRadioMain" position="center,center" size="1680,940" title="NeoRadio Online" backgroundColor="#00081418">
            <eLabel position="0,0" size="1680,940" backgroundColor="#00081418" zPosition="0" />
            <eLabel position="22,20" size="500,840" backgroundColor="#00101a2d" zPosition="0" />
            <eLabel position="542,20" size="1116,600" backgroundColor="#00101a2d" zPosition="0" />
            <eLabel position="736,404" size="520,132" backgroundColor="#00111d31" zPosition="1" />
            <eLabel position="1412,164" size="224,224" backgroundColor="#00121f36" zPosition="1" />
            <eLabel position="1412,402" size="224,96" backgroundColor="#00121f36" zPosition="1" />
            <eLabel position="542,644" size="790,196" backgroundColor="#000d1626" zPosition="1" />
            <eLabel position="1344,644" size="292,196" backgroundColor="#00121f36" zPosition="1" />
            <eLabel position="1460,22" size="162,76" backgroundColor="#00131d2f" zPosition="1" />
            <eLabel position="22,880" size="240,34" backgroundColor="#00a32020" zPosition="0" />
            <eLabel position="282,880" size="240,34" backgroundColor="#001c7f39" zPosition="0" />
            <eLabel position="542,880" size="240,34" backgroundColor="#00b99211" zPosition="0" />
            <eLabel position="802,880" size="240,34" backgroundColor="#001d4fc9" zPosition="0" />
            <eLabel position="1062,880" size="280,34" backgroundColor="#00303a4d" zPosition="0" />
            <eLabel position="1362,880" size="296,34" backgroundColor="#00434b5b" zPosition="0" />

            <widget name="list_title" position="42,34" size="440,38" font="Regular;30" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_list" position="42,82" size="460,656" scrollbarMode="showOnDemand" itemHeight="40" font="Regular;30" foregroundColor="#00ffffff" foregroundColorSelected="#00081418" backgroundColor="#00101a2d" backgroundColorSelected="#0065c4ff" transparent="0" zPosition="2" />
            <widget name="filter_label" position="42,748" size="460,28" font="Regular;22" foregroundColor="#0065c4ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="search_label" position="42,778" size="460,26" font="Regular;22" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="help_label" position="42,808" size="460,44" font="Regular;20" foregroundColor="#00d7deeb" backgroundColor="#00101a2d" transparent="0" zPosition="2" />

            <widget name="header_title" position="570,34" size="360,40" font="Regular;34" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="clock_label" position="1090,34" size="340,34" font="Regular;24" foregroundColor="#0065c4ff" backgroundColor="#00101a2d" halign="right" transparent="0" zPosition="2" />
            <widget name="status_label" position="570,82" size="620,32" font="Regular;26" foregroundColor="#001eff6b" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="visualizer_label" position="1200,82" size="224,32" font="Regular;24" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" halign="right" transparent="0" zPosition="2" />
            <widget name="picon" position="1468,28" size="146,64" alphatest="blend" zPosition="2" />

            <widget name="station_name" position="570,136" size="770,48" font="Regular;40" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_meta" position="570,192" size="770,34" font="Regular;26" foregroundColor="#008fd3ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_url" position="570,232" size="770,28" font="Regular;20" foregroundColor="#00b5bfd1" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_desc_title" position="570,270" size="220,30" font="Regular;28" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_desc" position="570,308" size="760,78" font="Regular;22" foregroundColor="#00edf2fa" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="station_extra" position="570,390" size="760,24" font="Regular;18" foregroundColor="#008fd3ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
            <widget name="hero_clock" position="752,426" size="488,70" font="Regular;68" foregroundColor="#00f3fbff" backgroundColor="#00111d31" halign="center" transparent="0" zPosition="3" />
            <widget name="hero_date" position="752,500" size="488,30" font="Regular;23" foregroundColor="#00ffd27d" backgroundColor="#00111d31" halign="center" transparent="0" zPosition="3" />
            <widget name="cover" position="1418,170" size="212,206" alphatest="blend" zPosition="2" />
            <widget name="spectrum_title" position="1434,406" size="180,24" font="Regular;22" foregroundColor="#00ffd27d" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />
            <widget name="spectrum_label" position="1428,438" size="192,46" font="Regular;36" foregroundColor="#0075e59b" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />

            <widget name="np_header" position="570,660" size="300,30" font="Regular;28" foregroundColor="#00ffd27d" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="np_title" position="570,700" size="730,32" font="Regular;25" foregroundColor="#00ffffff" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="np_artist" position="570,734" size="730,30" font="Regular;23" foregroundColor="#008fd3ff" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="np_album" position="570,768" size="730,30" font="Regular;23" foregroundColor="#00c4d5ee" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="np_status" position="570,802" size="730,26" font="Regular;21" foregroundColor="#001eff6b" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="footer_brand" position="570,832" size="230,24" font="Regular;20" foregroundColor="#00ffd27d" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="footer_label" position="808,832" size="492,24" font="Regular;18" foregroundColor="#00b5bfd1" backgroundColor="#000d1626" transparent="0" zPosition="2" />
            <widget name="picon_large_title" position="1362,660" size="256,24" font="Regular;22" foregroundColor="#00ffd27d" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />
            <widget name="picon_large" position="1372,696" size="236,128" alphatest="blend" zPosition="2" />

            <widget name="key_red" position="22,882" size="240,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00a32020" halign="center" valign="center" zPosition="2" />
            <widget name="key_green" position="282,882" size="240,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#001c7f39" halign="center" valign="center" zPosition="2" />
            <widget name="key_yellow" position="542,882" size="240,30" font="Regular;24" foregroundColor="#00000000" backgroundColor="#00b99211" halign="center" valign="center" zPosition="2" />
            <widget name="key_blue" position="802,882" size="240,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#001d4fc9" halign="center" valign="center" zPosition="2" />
            <widget name="key_menu" position="1062,882" size="280,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00303a4d" halign="center" valign="center" zPosition="2" />
            <widget name="key_info" position="1362,882" size="296,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />

            <widget name="saver_bg" position="0,0" size="1680,940" font="Regular;1" foregroundColor="#00000000" backgroundColor="#00060d16" transparent="0" zPosition="10" />
            <widget name="saver_picon" position="1260,690" size="260,120" alphatest="blend" zPosition="12" />
            <widget name="saver_station" position="160,764" size="1040,52" font="Regular;40" foregroundColor="#00ffffff" backgroundColor="#00060d16" halign="left" transparent="0" zPosition="12" />
            <widget name="saver_hint" position="160,822" size="1040,28" font="Regular;22" foregroundColor="#00ffd27d" backgroundColor="#00060d16" halign="left" transparent="0" zPosition="12" />
            <widget name="saver_clock" position="620,250" size="460,86" font="Regular;72" foregroundColor="#00d8ecff" backgroundColor="#00060d16" halign="center" transparent="0" zPosition="12" />
            <widget name="saver_date" position="620,346" size="460,34" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00060d16" halign="center" transparent="0" zPosition="12" />
        </screen>
        """
    return """
    <screen name="NeoRadioMain" position="center,center" size="1180,660" title="NeoRadio Online" backgroundColor="#00081418">
        <eLabel position="0,0" size="1180,660" backgroundColor="#00081418" zPosition="0" />
        <eLabel position="20,20" size="420,560" backgroundColor="#00101a2d" zPosition="0" />
        <eLabel position="460,20" size="700,400" backgroundColor="#00101a2d" zPosition="0" />
        <eLabel position="606,220" size="340,110" backgroundColor="#00111d31" zPosition="1" />
        <eLabel position="934,104" size="176,176" backgroundColor="#00121f36" zPosition="1" />
        <eLabel position="934,294" size="176,74" backgroundColor="#00121f36" zPosition="1" />
        <eLabel position="882,444" size="258,134" backgroundColor="#00121f36" zPosition="1" />
        <eLabel position="962,16" size="138,62" backgroundColor="#00131d2f" zPosition="1" />
        <eLabel position="20,614" size="140,24" backgroundColor="#00a32020" zPosition="0" />
        <eLabel position="170,614" size="140,24" backgroundColor="#001c7f39" zPosition="0" />
        <eLabel position="320,614" size="140,24" backgroundColor="#00b99211" zPosition="0" />
        <eLabel position="470,614" size="140,24" backgroundColor="#001d4fc9" zPosition="0" />
        <eLabel position="620,614" size="220,24" backgroundColor="#00303a4d" zPosition="0" />
        <eLabel position="850,614" size="220,24" backgroundColor="#00434b5b" zPosition="0" />

        <widget name="list_title" position="36,28" size="320,24" font="Regular;22" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_list" position="36,64" size="388,430" scrollbarMode="showOnDemand" itemHeight="28" font="Regular;22" foregroundColor="#00ffffff" foregroundColorSelected="#00081418" backgroundColor="#00101a2d" backgroundColorSelected="#0065c4ff" transparent="0" zPosition="2" />
        <widget name="filter_label" position="36,500" size="388,20" font="Regular;17" foregroundColor="#0065c4ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="search_label" position="36,522" size="388,20" font="Regular;17" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="help_label" position="36,544" size="388,30" font="Regular;15" foregroundColor="#00d7deeb" backgroundColor="#00101a2d" transparent="0" zPosition="2" />

        <widget name="header_title" position="486,26" size="250,28" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="clock_label" position="780,26" size="216,24" font="Regular;18" foregroundColor="#0065c4ff" backgroundColor="#00101a2d" halign="right" transparent="0" zPosition="2" />
        <widget name="status_label" position="486,56" size="346,24" font="Regular;20" foregroundColor="#001eff6b" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="visualizer_label" position="834,56" size="120,24" font="Regular;18" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" halign="right" transparent="0" zPosition="2" />
        <widget name="picon" position="972,20" size="118,50" alphatest="blend" zPosition="2" />

        <widget name="station_name" position="486,92" size="404,32" font="Regular;28" foregroundColor="#00ffffff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_meta" position="486,126" size="404,22" font="Regular;20" foregroundColor="#008fd3ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_url" position="486,152" size="404,18" font="Regular;14" foregroundColor="#00b5bfd1" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_desc_title" position="486,176" size="160,22" font="Regular;20" foregroundColor="#00ffd27d" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_desc" position="486,202" size="404,48" font="Regular;16" foregroundColor="#00edf2fa" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="station_extra" position="486,254" size="404,18" font="Regular;13" foregroundColor="#008fd3ff" backgroundColor="#00101a2d" transparent="0" zPosition="2" />
        <widget name="hero_clock" position="590,266" size="344,38" font="Regular;40" foregroundColor="#00f3fbff" backgroundColor="#00111d31" halign="center" transparent="0" zPosition="3" />
        <widget name="hero_date" position="590,306" size="344,18" font="Regular;16" foregroundColor="#00ffd27d" backgroundColor="#00111d31" halign="center" transparent="0" zPosition="3" />
        <widget name="cover" position="940,112" size="164,160" alphatest="blend" zPosition="2" />
        <widget name="spectrum_title" position="954,304" size="136,16" font="Regular;15" foregroundColor="#00ffd27d" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />
        <widget name="spectrum_label" position="946,326" size="152,28" font="Regular;24" foregroundColor="#0075e59b" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />

        <widget name="np_header" position="486,440" size="220,20" font="Regular;19" foregroundColor="#00ffd27d" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="np_title" position="486,468" size="396,20" font="Regular;17" foregroundColor="#00ffffff" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="np_artist" position="486,492" size="396,20" font="Regular;17" foregroundColor="#008fd3ff" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="np_album" position="486,516" size="396,20" font="Regular;17" foregroundColor="#00c4d5ee" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="np_status" position="486,540" size="396,18" font="Regular;15" foregroundColor="#001eff6b" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="footer_brand" position="486,560" size="136,16" font="Regular;13" foregroundColor="#00ffd27d" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="footer_label" position="626,560" size="256,16" font="Regular;12" foregroundColor="#00b5bfd1" backgroundColor="#000d1626" transparent="0" zPosition="2" />
        <widget name="picon_large_title" position="904,440" size="214,16" font="Regular;16" foregroundColor="#00ffd27d" backgroundColor="#00121f36" halign="center" transparent="0" zPosition="2" />
        <widget name="picon_large" position="918,466" size="186,100" alphatest="blend" zPosition="2" />

        <widget name="key_red" position="20,614" size="140,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#00a32020" halign="center" valign="center" zPosition="2" />
        <widget name="key_green" position="170,614" size="140,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#001c7f39" halign="center" valign="center" zPosition="2" />
        <widget name="key_yellow" position="320,614" size="140,24" font="Regular;18" foregroundColor="#00000000" backgroundColor="#00b99211" halign="center" valign="center" zPosition="2" />
        <widget name="key_blue" position="470,614" size="140,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#001d4fc9" halign="center" valign="center" zPosition="2" />
        <widget name="key_menu" position="620,614" size="220,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#00303a4d" halign="center" valign="center" zPosition="2" />
        <widget name="key_info" position="850,614" size="220,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />

        <widget name="saver_bg" position="0,0" size="1180,660" font="Regular;1" foregroundColor="#00000000" backgroundColor="#00060d16" transparent="0" zPosition="10" />
        <widget name="saver_picon" position="870,476" size="180,90" alphatest="blend" zPosition="12" />
        <widget name="saver_station" position="80,544" size="720,28" font="Regular;22" foregroundColor="#00ffffff" backgroundColor="#00060d16" halign="left" transparent="0" zPosition="12" />
        <widget name="saver_hint" position="80,576" size="720,20" font="Regular;16" foregroundColor="#00ffd27d" backgroundColor="#00060d16" halign="left" transparent="0" zPosition="12" />
        <widget name="saver_clock" position="368,176" size="300,40" font="Regular;34" foregroundColor="#00d8ecff" backgroundColor="#00060d16" halign="center" transparent="0" zPosition="12" />
        <widget name="saver_date" position="368,222" size="300,18" font="Regular;16" foregroundColor="#00ffffff" backgroundColor="#00060d16" halign="center" transparent="0" zPosition="12" />
    </screen>
    """



class NeoRadioSaver(Screen):
    skin = """
    <screen name="NeoRadioSaver" position="0,0" size="1920,1080" title="NeoRadio screensaver" backgroundColor="#00000000">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#00060d16" zPosition="0" />
        <eLabel position="120,120" size="1680,840" backgroundColor="#00101826" zPosition="1" />
        <eLabel position="170,170" size="540,540" backgroundColor="#00131d2f" zPosition="1" />
        <eLabel position="780,170" size="960,220" backgroundColor="#00131d2f" zPosition="1" />
        <eLabel position="780,422" size="960,180" backgroundColor="#00131d2f" zPosition="1" />
        <eLabel position="780,636" size="960,180" backgroundColor="#00131d2f" zPosition="1" />
        <widget name="cover" position="182,182" size="516,516" alphatest="blend" zPosition="2" />
        <widget name="clock" position="812,196" size="896,72" font="Regular;58" foregroundColor="#00c5ddff" backgroundColor="#00131d2f" halign="center" transparent="0" zPosition="2" />
        <widget name="station" position="812,284" size="896,70" font="Regular;52" foregroundColor="#00ffffff" backgroundColor="#00131d2f" halign="center" transparent="0" zPosition="2" />
        <widget name="meta" position="812,356" size="896,34" font="Regular;28" foregroundColor="#007de29f" backgroundColor="#00131d2f" halign="center" transparent="0" zPosition="2" />
        <widget name="picon" position="980,450" size="560,120" alphatest="blend" zPosition="2" />
        <widget name="spectrum" position="842,670" size="836,74" font="Regular;62" foregroundColor="#0089f0b0" backgroundColor="#00131d2f" halign="center" transparent="0" zPosition="2" />
        <widget name="hint" position="812,770" size="896,30" font="Regular;24" foregroundColor="#00ffd27d" backgroundColor="#00131d2f" halign="center" transparent="0" zPosition="2" />
    </screen>
    """

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        self.parent = parent
        self["clock"] = Label(text_type(""))
        self["station"] = Label(text_type(""))
        self["meta"] = Label(text_type(""))
        self["hint"] = Label(tr('screensaver_hint'))
        self["spectrum"] = Label(u"▁▂▃▄▅")
        self["cover"] = Pixmap()
        self["picon"] = Pixmap()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions", "InfobarActions"], {
            "ok": self.close,
            "cancel": self.close,
            "red": self.close,
            "green": self.close,
            "yellow": self.close,
            "blue": self.close,
            "menu": self.close,
            "showEventInfo": self.close,
            "up": self.close,
            "down": self.close,
            "left": self.close,
            "right": self.close,
        }, -1)
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.on_timer)
        except Exception:
            self.timer_conn = self.timer.timeout.connect(self.on_timer)
        self.saver_timer = eTimer()
        try:
            self.saver_timer.callback.append(self.on_screensaver_timeout)
        except Exception:
            self.saver_timer_conn = self.saver_timer.timeout.connect(self.on_screensaver_timeout)
        self.last_activity_ts = time.time()
        self.saver_open = False
        self.saver_deadline = 0
        self.onLayoutFinish.append(self.on_layout_ready)
        self.apply_language()

    def set_footer_default(self):
        self.footer_mode = 'default'
        self["footer_brand"].setText(tr('by_author'))
        self["footer_label"].setText(u"")

    def source_label_from_kind(self, kind):
        kind = to_text(kind).strip().lower()
        if kind == 'icy':
            return tr('metadata_source_icy')
        if kind == 'endpoint':
            return tr('metadata_source_endpoint')
        if kind == 'hybrid':
            return tr('metadata_source_hybrid')
        return tr('metadata_source_service')

    def set_footer_metadata(self, kind, detail_text):
        detail_text = shorten_text(detail_text, 94 if self.is_fhd else 54)
        self.footer_mode = 'metadata'
        self["footer_brand"].setText(self.source_label_from_kind(kind))
        self["footer_label"].setText(detail_text)

    def reset_network_metadata(self):
        self.network_meta = {}
        self.network_meta_last_update = 0
        self.network_meta_worker_id += 1
        self.set_footer_default()

    def start_network_metadata_worker(self, station, stream_url):
        self.reset_network_metadata()
        if threading is None:
            return
        worker_id = self.network_meta_worker_id
        safe_station = dict(station or {})
        safe_stream_url = to_text(stream_url).strip()
        if not safe_stream_url:
            return
        try:
            worker = threading.Thread(target=self.network_metadata_worker, args=(worker_id, safe_station, safe_stream_url))
            worker.setDaemon(True)
            worker.start()
        except Exception:
            pass

    def network_metadata_worker(self, worker_id, station, stream_url):
        for _ in range(120):
            if self.network_meta_worker_id != worker_id:
                return
            payload = fetch_station_network_metadata(station, stream_url)
            if self.network_meta_worker_id != worker_id:
                return
            if payload:
                payload['updated_at'] = format_ui_stamp()
                self.network_meta = payload
                self.network_meta_last_update = time.time()
            sleep_left = NETWORK_META_POLL_SECS
            while sleep_left > 0:
                if self.network_meta_worker_id != worker_id:
                    return
                time.sleep(1)
                sleep_left -= 1

    def on_layout_ready(self):
        try:
            self['picon'].instance.setScale(1)
            self['cover'].instance.setScale(1)
        except Exception:
            pass
        self.on_timer()
        self.timer.start(1000)

    def on_timer(self):
        self['clock'].setText(to_text(time.strftime('%H:%M:%S')))
        station = None
        try:
            station = self.parent.get_screensaver_station()
        except Exception:
            station = None
        name = to_text(station.get('name', u'NeoRadio')) if station else u'NeoRadio'
        meta = []
        if station:
            meta.append(to_text(station.get('country', u'')))
            meta.append(to_text(station.get('genre', u'')))
            meta.append(u'%s kbps' % to_text(station.get('bitrate', u'?')))
        self['station'].setText(name)
        self['meta'].setText(u' | '.join([x for x in meta if x]))
        try:
            self['spectrum'].setText(self.parent.spectrum_frames[self.parent.visualizer_idx % len(self.parent.spectrum_frames)])
            self['picon'].instance.setPixmapFromFile(self.parent.current_picon_path or DEFAULT_PICON)
            self['cover'].instance.setPixmapFromFile(self.parent.current_cover_path or DEFAULT_COVER)
        except Exception:
            pass

    def close(self):
        try:
            self.timer.stop()
        except Exception:
            pass
        Screen.close(self)



class NeoRadioMain(Screen):
    skin = get_skin()

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(PLUGIN_TITLE)
        self.is_fhd = getDesktop(0).size().width() >= 1920
        self.ui_width = 1680 if self.is_fhd else 1180
        self.ui_height = 940 if self.is_fhd else 660
        self.base_stations = load_stations()
        self.favorites = load_favorites()
        self.current_filter = text_type("")
        self.search_term = text_type("")
        self.filtered_stations = []
        self.previous_service = self.session.nav.getCurrentlyPlayingServiceReference()
        self.current_service = None
        self.visualizer_frames = [u"[▁▂▃▄▅]", u"[▂▄▆▃▅]", u"[▄▇▅▂▆]", u"[▆▃▇▅▂]", u"[▇▅▃▆▂]", u"[▅▂▄▇▆]", u"[▃▄▂▅▇]", u"[▂▅▇▄▃]"]
        self.spectrum_frames = [u"▁▃▆▂▅▇", u"▂▄▇▃▆▅", u"▄▆▃▇▅▂", u"▆▂▅▄▇▃", u"▇▄▂▆▃▅", u"▅▇▄▃▂▆", u"▃▅▇▂▄▆", u"▂▃▅▇▆▁"]
        self.visualizer_idx = 0
        self.current_cover_path = DEFAULT_COVER
        self.current_picon_path = DEFAULT_PICON
        self.last_meta_blob = text_type("")
        self.picon_cache = {}
        self.picon_dir_cache = None
        self.bouquet_picon_name_map = None
        self.bouquet_service_map = None
        self.playing_station_data = None
        self.playlist_cache = {}
        self.remote_picon_cache = {}
        self.remote_picon_discovery_cache = {}
        self.github_console = None
        self.github_update_info = {}
        self.network_meta = {}
        self.network_meta_worker_id = 0
        self.network_meta_last_update = 0
        self.footer_mode = "default"
        self.saver_visible = False
        self.saver_clock_x = 0
        self.saver_clock_y = 0
        self.saver_dx = 18 if self.is_fhd else 12
        self.saver_dy = 14 if self.is_fhd else 10

        self["list_title"] = Label(text_type(""))
        self["header_title"] = Label(text_type(""))
        self["filter_label"] = Label(text_type(""))
        self["search_label"] = Label(text_type(""))
        self["help_label"] = Label(text_type(""))
        self["status_label"] = Label(text_type(""))
        self["clock_label"] = Label(text_type(""))
        self["hero_clock"] = Label(text_type(""))
        self["hero_date"] = Label(text_type(""))
        self["visualizer_label"] = Label(text_type(""))
        self["footer_brand"] = Label(text_type(""))
        self["footer_label"] = Label(text_type(""))
        self["station_name"] = Label(u"-")
        self["station_meta"] = Label(u"-")
        self["station_url"] = Label(text_type(""))
        self["station_desc_title"] = Label(text_type(""))
        self["station_desc"] = Label(tr("nothing_to_show"))
        self["station_extra"] = Label(text_type(""))
        self["spectrum_title"] = Label(text_type(""))
        self["spectrum_label"] = Label(u"▁▂▃▄▅")
        self["np_header"] = Label(text_type(""))
        self["np_title"] = Label(text_type(""))
        self["np_artist"] = Label(text_type(""))
        self["np_album"] = Label(text_type(""))
        self["np_status"] = Label(text_type(""))
        self["key_red"] = Label(text_type(""))
        self["key_green"] = Label(text_type(""))
        self["key_yellow"] = Label(text_type(""))
        self["key_blue"] = Label(text_type(""))
        self["key_menu"] = Label(text_type(""))
        self["key_info"] = Label(text_type(""))
        self["station_list"] = MenuList([])
        self["cover"] = Pixmap()
        self["picon"] = Pixmap()
        self["picon_large_title"] = Label(text_type(""))
        self["picon_large"] = Pixmap()
        self["saver_bg"] = Label(text_type(""))
        self["saver_clock"] = Label(text_type(""))
        self["saver_date"] = Label(text_type(""))
        self["saver_station"] = Label(text_type(""))
        self["saver_hint"] = Label(tr("screensaver_hint"))
        self["saver_picon"] = Pixmap()

        try:
            self["station_list"].onSelectionChanged.append(self.on_selection_changed)
        except Exception:
            pass

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions", "InfobarActions"],
            {
                "ok": self.play_current,
                "cancel": self.close_plugin,
                "red": self.close_plugin,
                "green": self.play_current,
                "yellow": self.toggle_favorite,
                "blue": self.open_filter_menu,
                "menu": self.open_main_menu,
                "showEventInfo": self.show_details,
                "up": self.move_up,
                "down": self.move_down,
                "left": self.page_up,
                "right": self.page_down,
            },
            -1,
        )

        self.timer = eTimer()
        try:
            self.timer.callback.append(self.on_timer)
        except Exception:
            self.timer_conn = self.timer.timeout.connect(self.on_timer)
        self.saver_timer = eTimer()
        try:
            self.saver_timer.callback.append(self.on_screensaver_timeout)
        except Exception:
            self.saver_timer_conn = self.saver_timer.timeout.connect(self.on_screensaver_timeout)
        self.last_activity_ts = time.time()
        self.saver_open = False
        self.saver_deadline = 0
        self.onLayoutFinish.append(self.on_layout_ready)
        self.apply_language()

    def set_footer_default(self):
        self.footer_mode = 'default'
        self["footer_brand"].setText(tr('by_author'))
        self["footer_label"].setText(u"")

    def source_label_from_kind(self, kind):
        kind = to_text(kind).strip().lower()
        if kind == 'icy':
            return tr('metadata_source_icy')
        if kind == 'endpoint':
            return tr('metadata_source_endpoint')
        if kind == 'hybrid':
            return tr('metadata_source_hybrid')
        return tr('metadata_source_service')

    def set_footer_metadata(self, kind, detail_text):
        detail_text = shorten_text(detail_text, 94 if self.is_fhd else 54)
        self.footer_mode = 'metadata'
        self["footer_brand"].setText(self.source_label_from_kind(kind))
        self["footer_label"].setText(detail_text)

    def reset_network_metadata(self):
        self.network_meta = {}
        self.network_meta_last_update = 0
        self.network_meta_worker_id += 1
        self.set_footer_default()

    def start_network_metadata_worker(self, station, stream_url):
        self.reset_network_metadata()
        if threading is None:
            return
        worker_id = self.network_meta_worker_id
        safe_station = dict(station or {})
        safe_stream_url = to_text(stream_url).strip()
        if not safe_stream_url:
            return
        try:
            worker = threading.Thread(target=self.network_metadata_worker, args=(worker_id, safe_station, safe_stream_url))
            worker.setDaemon(True)
            worker.start()
        except Exception:
            pass

    def network_metadata_worker(self, worker_id, station, stream_url):
        for _ in range(120):
            if self.network_meta_worker_id != worker_id:
                return
            payload = fetch_station_network_metadata(station, stream_url)
            if self.network_meta_worker_id != worker_id:
                return
            if payload:
                payload['updated_at'] = format_ui_stamp()
                self.network_meta = payload
                self.network_meta_last_update = time.time()
            sleep_left = NETWORK_META_POLL_SECS
            while sleep_left > 0:
                if self.network_meta_worker_id != worker_id:
                    return
                time.sleep(1)
                sleep_left -= 1

    def on_layout_ready(self):
        self.touch_activity()
        self.prepare_pixmaps()
        self.setup_screensaver_overlay()
        self.current_filter = self.get_start_filter()
        self.refresh_list(select_name=to_text(config.plugins.neoradio.last_station.value), select_url=to_text(getattr(config.plugins.neoradio, "last_url", "").value))
        self.update_cover(self.get_current_station())
        self.update_picon(self.get_picon_station())
        self.schedule_screensaver()
        self.timer.start(1000)
        if config.plugins.neoradio.autoplay_last.value and (config.plugins.neoradio.last_station.value or getattr(config.plugins.neoradio, "last_url", "").value):
            self.play_current()

    def apply_language(self):
        self["list_title"].setText(tr('stations_online'))
        self["header_title"].setText(tr('header_title'))
        self["help_label"].setText(tr('help'))
        self["status_label"].setText(tr('status_ready'))
        self["footer_brand"].setText(tr('by_author'))
        self["station_desc_title"].setText(tr('station_desc_title'))
        self["spectrum_title"].setText(tr('spectrum_title'))
        self["np_header"].setText(tr('np_header'))
        self["np_title"].setText(tr('np_title'))
        self["np_artist"].setText(tr('np_artist'))
        self["np_album"].setText(tr('np_album'))
        self["np_status"].setText(tr('np_wait'))
        self["key_red"].setText(tr('red_exit'))
        self["key_green"].setText(tr('green_play'))
        self["key_yellow"].setText(tr('yellow_fav'))
        self["key_blue"].setText(tr('blue_filter'))
        self["key_menu"].setText(tr('menu_cfg'))
        self["key_info"].setText(tr('info_details'))
        self["picon_large_title"].setText(tr('picon_title'))
        self.set_footer_default()

    def setup_screensaver_overlay(self):
        for widget_name in ("saver_bg", "saver_clock", "saver_date", "saver_station", "saver_hint", "saver_picon"):
            try:
                self[widget_name].hide()
            except Exception:
                pass
        try:
            self["saver_picon"].instance.setScale(1)
        except Exception:
            pass

    def hide_screensaver_overlay(self):
        self.saver_visible = False
        for widget_name in ("saver_bg", "saver_clock", "saver_date", "saver_station", "saver_hint", "saver_picon"):
            try:
                self[widget_name].hide()
            except Exception:
                pass

    def show_screensaver_overlay(self):
        self.saver_visible = True
        self.saver_clock_x = 140 if self.is_fhd else 80
        self.saver_clock_y = 120 if self.is_fhd else 70
        self.saver_dx = abs(self.saver_dx) or (18 if self.is_fhd else 12)
        self.saver_dy = abs(self.saver_dy) or (14 if self.is_fhd else 10)
        for widget_name in ("saver_bg", "saver_clock", "saver_date", "saver_station", "saver_hint", "saver_picon"):
            try:
                self[widget_name].show()
            except Exception:
                pass
        self.update_screensaver_overlay(reset=True)

    def move_widget_to(self, widget_name, x, y):
        try:
            self[widget_name].instance.move(ePoint(int(x), int(y)))
        except Exception:
            pass

    def update_screensaver_overlay(self, reset=False):
        if not self.saver_visible:
            return
        clock_w = 460 if self.is_fhd else 300
        clock_h = 86 if self.is_fhd else 40
        date_h = 34 if self.is_fhd else 18
        pad = 24 if self.is_fhd else 16
        if reset:
            self.saver_clock_x = 140 if self.is_fhd else 80
            self.saver_clock_y = 120 if self.is_fhd else 70
        else:
            max_x = max(pad, self.ui_width - clock_w - pad)
            max_y = max(pad, self.ui_height - (clock_h + date_h + 18) - pad)
            nx = self.saver_clock_x + self.saver_dx
            ny = self.saver_clock_y + self.saver_dy
            if nx <= pad or nx >= max_x:
                self.saver_dx = -self.saver_dx
                nx = max(pad, min(max_x, nx))
            if ny <= pad or ny >= max_y:
                self.saver_dy = -self.saver_dy
                ny = max(pad, min(max_y, ny))
            self.saver_clock_x = nx
            self.saver_clock_y = ny
        station = self.get_screensaver_station()
        station_name = to_text(station.get("name", u"NeoRadio")) if station else u"NeoRadio"
        self["saver_clock"].setText(to_text(time.strftime("%H:%M:%S")))
        self["saver_date"].setText(format_ui_date(with_weekday=True))
        self["saver_station"].setText(station_name)
        self["saver_hint"].setText(tr("screensaver_hint"))
        self.set_pixmap_file("saver_picon", self.current_picon_path or DEFAULT_PICON)
        self.move_widget_to("saver_clock", self.saver_clock_x, self.saver_clock_y)
        self.move_widget_to("saver_date", self.saver_clock_x, self.saver_clock_y + (92 if self.is_fhd else 46))
        self.move_widget_to("saver_station", self.saver_clock_x, self.saver_clock_y + (138 if self.is_fhd else 70))
        self.move_widget_to("saver_hint", self.saver_clock_x, self.saver_clock_y + (194 if self.is_fhd else 96))

    def consume_screensaver_key(self):
        if not self.saver_visible:
            return False
        self.hide_screensaver_overlay()
        self.touch_activity()
        return True

    def get_screensaver_station(self):
        return self.playing_station_data or self.get_current_station()

    def schedule_screensaver(self):
        timeout_min = get_screensaver_timeout_minutes()
        self.saver_deadline = 0
        try:
            self.saver_timer.stop()
        except Exception:
            pass
        if timeout_min <= 0:
            return
        timeout_ms = int(timeout_min * 60 * 1000)
        self.saver_deadline = time.time() + (timeout_min * 60)
        try:
            self.saver_timer.start(timeout_ms, True)
        except TypeError:
            self.saver_timer.start(timeout_ms)

    def touch_activity(self):
        self.last_activity_ts = time.time()
        if self.saver_visible:
            self.hide_screensaver_overlay()
        if self.saver_open:
            self.saver_open = False
        self.schedule_screensaver()

    def on_screensaver_timeout(self):
        timeout_min = get_screensaver_timeout_minutes()
        if timeout_min <= 0 or self.saver_visible:
            return
        self.show_screensaver_overlay()

    def maybe_open_screensaver(self):
        timeout_min = get_screensaver_timeout_minutes()
        if timeout_min <= 0 or self.saver_visible:
            return
        if not self.saver_deadline:
            self.schedule_screensaver()
            return
        if time.time() >= self.saver_deadline:
            self.show_screensaver_overlay()

    def screensaver_closed(self, *args, **kwargs):
        self.hide_screensaver_overlay()
        self.schedule_screensaver()

    def prepare_pixmaps(self):
        for widget_name in ("cover", "picon", "picon_large", "saver_picon"):
            try:
                self[widget_name].instance.setScale(1)
            except Exception:
                pass

    def set_pixmap_file(self, widget_name, path):
        fallback = DEFAULT_PICON if widget_name in ("picon", "picon_large", "saver_picon") else DEFAULT_COVER
        final_path = path if path and os.path.exists(path) else fallback
        try:
            self[widget_name].instance.setPixmapFromFile(final_path)
            return True
        except Exception:
            return False

    def on_timer(self):
        self["clock_label"].setText(format_ui_stamp())
        self["hero_clock"].setText(to_text(time.strftime("%H:%M:%S")))
        self["hero_date"].setText(format_ui_date(with_weekday=True))
        if self.footer_mode == "default":
            self.set_footer_default()
        self.visualizer_idx = (self.visualizer_idx + 1) % len(self.visualizer_frames)
        self["visualizer_label"].setText(u"EQ %s" % self.visualizer_frames[self.visualizer_idx])
        self["spectrum_label"].setText(self.spectrum_frames[self.visualizer_idx % len(self.spectrum_frames)])
        self.update_now_playing()
        if self.saver_visible:
            self.update_screensaver_overlay()
        else:
            self.maybe_open_screensaver()

    def get_available_countries(self):
        countries = []
        seen = {}
        for station in self.base_stations:
            country = to_text(station.get("country", u"Online")).strip() or u"Online"
            if country not in seen:
                countries.append(country)
                seen[country] = True
        countries.sort()
        return countries

    def get_default_country(self):
        value = to_text(getattr(config.plugins.neoradio.default_country, "value", u"")).strip()
        if value in (u"", u"All", u"Wszystkie", u"Wszystkie kraje"):
            return u""
        return value

    def get_default_filter(self):
        country = self.get_default_country()
        if country and country in self.get_available_countries():
            return format_country_filter(country)
        return tr("all")

    def get_start_filter(self):
        saved = to_text(getattr(config.plugins.neoradio.last_filter, "value", u"")).strip()
        filters = self.get_filters()
        if saved and saved in filters:
            return saved
        legacy = saved.lower()
        if legacy in ("all", "wszystkie"):
            return tr("all")
        if legacy in ("favorites", "ulubione"):
            return tr("favorites")
        if legacy in ("recently played", "ostatnio odtwarzane"):
            return tr("recent")
        for prefix in (u"Kraj:", u"Country:"):
            if saved.startswith(prefix):
                country = normalize_country(saved.split(u":", 1)[1].strip())
                label = format_country_filter(country)
                if label in filters:
                    return label
        for prefix in (u"Język:", u"Language:"):
            if saved.startswith(prefix):
                lang = normalize_station_language(saved.split(u":", 1)[1].strip())
                label = format_language_filter(lang)
                if label in filters:
                    return label
        return self.get_default_filter()

    def get_filters(self):
        items = [tr("all"), tr("favorites"), tr("recent")]
        countries = {}
        genres = {}
        languages = {}
        for station in self.base_stations:
            country = normalize_country(station.get("country", u"Online")) or u"Online"
            genre = to_text(station.get("genre", u"Other")).strip() or u"Other"
            lang = normalize_station_language(station.get("language", u""), country, station.get("name", u""), station.get("group", u""), station.get("url", u""))
            countries[country] = True
            genres[genre] = True
            languages[lang] = True
        for country in sorted(countries.keys()):
            label = format_country_filter(country)
            if label not in items:
                items.append(label)
        for lang in STATION_LANGUAGE_ORDER:
            if lang in languages:
                label = format_language_filter(lang)
                if label not in items:
                    items.append(label)
        for lang in sorted(languages.keys()):
            if lang not in STATION_LANGUAGE_ORDER:
                label = format_language_filter(lang)
                if label not in items:
                    items.append(label)
        for genre in sorted(genres.keys()):
            label = format_genre_filter(genre)
            if label not in items:
                items.append(label)
        return items

    def station_matches_search(self, station, term):
        if not term:
            return True
        country = normalize_country(station.get("country", u""))
        genre = to_text(station.get("genre", u""))
        lang = normalize_station_language(station.get("language", u""), country, station.get("name", u""), station.get("group", u""), station.get("url", u""))
        blob = u"%s %s %s %s %s" % (
            to_text(station.get("name", u"")),
            genre,
            country,
            lang,
            to_text(station.get("description", u"")),
        )
        return term in blob.lower()

    def apply_filters(self):
        result = []
        term = to_text(self.search_term).lower().strip()
        selected_country = None
        selected_genre = None
        selected_language = None
        country_prefix = tr("country_filter", "").split("%s", 1)[0]
        genre_prefix = tr("genre_filter", "").split("%s", 1)[0]
        language_prefix = tr("language_filter", "").split("%s", 1)[0]
        if country_prefix and self.current_filter.startswith(country_prefix):
            selected_country = normalize_country(self.current_filter.split(u":", 1)[1].strip())
        elif language_prefix and self.current_filter.startswith(language_prefix):
            selected_language = normalize_station_language(self.current_filter.split(u":", 1)[1].strip())
        elif genre_prefix and self.current_filter.startswith(genre_prefix):
            selected_genre = self.current_filter.split(u":", 1)[1].strip()
        if self.current_filter == tr("recent"):
            station_map = {}
            for station in self.base_stations:
                station_map[station_identity_key(station)] = station
            for item in load_history():
                station = station_map.get(station_identity_key(item))
                if station and self.station_matches_search(station, term):
                    result.append(station)
            self.filtered_stations = result
            return
        for station in self.base_stations:
            include = True
            country = normalize_country(station.get("country", u""))
            genre = to_text(station.get("genre", u""))
            lang = normalize_station_language(station.get("language", u""), country, station.get("name", u""), station.get("group", u""), station.get("url", u""))
            if self.current_filter == tr("favorites"):
                include = to_text(station.get("name")) in self.favorites
            elif selected_country is not None:
                include = country == selected_country
            elif selected_language is not None:
                include = lang == selected_language
            elif selected_genre is not None:
                include = genre == selected_genre
            if include and not self.station_matches_search(station, term):
                include = False
            if include:
                result.append(station)
        self.filtered_stations = result

    def refresh_list(self, select_name=None, select_url=None):
        self.base_stations = load_stations()
        self.favorites = load_favorites()
        valid_filters = self.get_filters()
        if self.current_filter not in valid_filters:
            self.current_filter = self.get_default_filter()
        self.apply_filters()
        entries = []
        for station in self.filtered_stations:
            prefix = u"★ " if to_text(station.get("name")) in self.favorites else u"  "
            country = to_text(station.get("country", u"Online")).strip()
            if self.current_filter == tr("all"):
                entries.append(u"%s[%s] %s" % (prefix, country, to_text(station.get("name", u"Unknown"))))
            else:
                entries.append(prefix + to_text(station.get("name", u"Unknown")))
        if not entries:
            entries = [tr("no_stations")]
        self["station_list"].setList(entries)
        country_label = self.get_default_country() or tr("all_countries")
        self["filter_label"].setText(tr("summary", country_label, self.current_filter, len(self.filtered_stations)))
        self["search_label"].setText(u"%s: %s" % (tr("search"), (self.search_term if self.search_term else tr("none"))))
        index = 0
        if self.filtered_stations:
            if select_url:
                url_key = normalize_stream_url_key(select_url)
                urls = [normalize_stream_url_key(x.get("url", u"")) for x in self.filtered_stations]
                if url_key in urls:
                    index = urls.index(url_key)
            if index == 0 and select_name:
                names = [to_text(x.get("name")) for x in self.filtered_stations]
                if select_name in names:
                    index = names.index(select_name)
        try:
            self["station_list"].moveToIndex(index)
        except Exception:
            pass
        self.on_selection_changed()

    def get_current_station(self):
        try:
            idx = self["station_list"].getSelectedIndex()
        except Exception:
            idx = 0
        if idx < 0 or idx >= len(self.filtered_stations):
            return None
        return self.filtered_stations[idx]

    def station_cover_path(self, station):
        if not station:
            return DEFAULT_COVER
        path = os.path.join(COVER_DIR, slugify(station.get("name", u"station")) + ".png")
        if os.path.exists(path):
            return path
        return DEFAULT_COVER

    def update_cover(self, station):
        path = self.station_cover_path(station)
        self.current_cover_path = path
        self.set_pixmap_file("cover", path)

    def get_picon_station(self):
        if self.playing_station_data:
            return self.playing_station_data
        return self.get_current_station()

    def clear_picon_cache(self):
        self.picon_cache = {}
        self.picon_dir_cache = None
        self.bouquet_picon_name_map = None
        self.bouquet_service_map = None

    def get_picon_dirs(self):
        if self.picon_dir_cache is not None:
            return self.picon_dir_cache
        candidates = []
        candidates.extend(DEFAULT_PICON_DIRS)
        candidates.extend(discover_mount_picon_dirs())
        candidates.extend(split_picon_paths(config.plugins.neoradio.picon_paths.value))
        result = []
        seen = {}
        for path in candidates:
            path = to_text(path).strip()
            if not path:
                continue
            if os.path.isdir(path) and path not in seen:
                result.append(path)
                seen[path] = True
        self.picon_dir_cache = result
        return result

    def scan_bouquet_service_refs(self):
        if getattr(self, "bouquet_picon_name_map", None) is not None and getattr(self, "bouquet_service_map", None) is not None:
            return
        if not hasattr(self, "bouquet_picon_name_map"):
            self.bouquet_picon_name_map = None
        if not hasattr(self, "bouquet_service_map"):
            self.bouquet_service_map = None
        name_map = {}
        service_map = {}
        bouquet_files = []
        for pattern in ("/etc/enigma2/*.tv", "/etc/enigma2/*.radio"):
            bouquet_files.extend(glob.glob(pattern))
        def add_entry(name, service_ref):
            norm = normalize_lookup_name(name)
            key = service_ref_to_picon_key(service_ref)
            if not norm or not key:
                return
            if norm not in name_map:
                name_map[norm] = []
            if key not in name_map[norm]:
                name_map[norm].append(key)
            service_map[key] = service_ref
        for path in bouquet_files:
            try:
                lines = io.open(path, "r", encoding="utf-8", errors="ignore").read().splitlines()
            except TypeError:
                try:
                    lines = io.open(path, "r", encoding="utf-8").read().splitlines()
                except Exception:
                    continue
            except Exception:
                continue
            pending_ref = None
            pending_name = None
            for raw in lines:
                line = to_text(raw).strip()
                if line.startswith("#SERVICE "):
                    payload = line[9:].strip()
                    if 'FROM BOUQUET' in payload:
                        pending_ref = None
                        pending_name = None
                        continue
                    pending_ref = payload
                    pending_name = None
                    if '::' in payload:
                        pending_name = payload.split('::', 1)[1].strip()
                        add_entry(pending_name, payload)
                elif line.startswith("#DESCRIPTION ") and pending_ref:
                    pending_name = line[13:].strip()
                    add_entry(pending_name, pending_ref)
        self.bouquet_picon_name_map = name_map
        self.bouquet_service_map = service_map

    def bouquet_picon_candidates(self, station):
        try:
            self.scan_bouquet_service_refs()
        except Exception:
            return []
        result = []
        if not station:
            return result
        names = [to_text(station.get("name", u"")), to_text(station.get("picon", u""))]
        for name in names:
            norm = normalize_lookup_name(name)
            if norm and norm in self.bouquet_picon_name_map:
                result.extend(self.bouquet_picon_name_map.get(norm, []))
        return unique_text_list(result)

    def station_picon_candidates(self, station):
        items = []
        if not station:
            return items
        for raw in (to_text(station.get("picon", u"")), to_text(station.get("name", u""))):
            raw = to_text(raw).strip()
            if not raw:
                continue
            base = raw.replace(".png", "")
            slug = slugify(base)
            compact = slug.replace("_", "")
            dehyphen = base.replace("-", " ")
            items.extend([
                raw,
                base,
                dehyphen,
                base.replace(" ", "_"),
                base.replace(" ", ""),
                base.replace("-", "_"),
                base.replace("-", ""),
                slug,
                compact,
            ])
            parts = [p for p in slug.split("_") if p]
            if len(parts) > 1:
                items.append("_".join(parts[:2]))
                items.append("".join(parts))
            if slug.startswith("radio_"):
                items.extend([slug[6:], slug[6:].replace("_", "")])
            if slug.startswith("polskie_radio_"):
                tail = slug[len("polskie_radio_"):]
                items.extend([tail, "pr_" + tail, "polskieradio_" + tail, "polskieradio" + tail.replace("_", "")])
            if slug.endswith("_fm"):
                items.append(slug[:-3] + "fm")
            for alias in PICON_ALIASES.get(slug, []):
                alias = to_text(alias).strip()
                if not alias:
                    continue
                items.extend([
                    alias,
                    alias.replace("_", ""),
                    alias.replace("-", "_"),
                    alias.replace("-", ""),
                ])
        normalized = []
        for x in items:
            x = to_text(x).strip()
            if not x:
                continue
            normalized.extend([
                x,
                x.replace(" ", "_"),
                x.replace(" ", ""),
                x.replace("-", "_"),
                x.replace("-", ""),
            ])
        return unique_text_list([x for x in normalized if x])

    def get_remote_picon_url(self, station):
        if not station:
            return None
        base = to_text(station.get("picon_url", u"")).strip()
        if not base:
            return None
        if base in self.remote_picon_discovery_cache:
            return self.remote_picon_discovery_cache.get(base)
        resolved = base if is_probably_image_url(base) else None
        self.remote_picon_discovery_cache[base] = resolved
        return resolved

    def download_remote_picon(self, station):
        if not station:
            return None
        source_url = self.get_remote_picon_url(station)
        if not source_url:
            return None
        if source_url in self.remote_picon_cache:
            cached = self.remote_picon_cache.get(source_url)
            if cached and os.path.exists(cached):
                return cached
        ensure_dir(REMOTE_PICON_CACHE_DIR)
        digest = hashlib.md5(to_text(source_url).encode('utf-8')).hexdigest()
        target_png = os.path.join(REMOTE_PICON_CACHE_DIR, digest + '.png')
        if os.path.exists(target_png) and os.path.getsize(target_png) > 0:
            self.remote_picon_cache[source_url] = target_png
            return target_png
        try:
            request = Request(source_url, headers={"User-Agent": "NeoRadio/%s" % PLUGIN_VERSION})
            response = urlopen(request, timeout=8)
            data = response.read()
            content_type = to_text(response.info().get('Content-Type', ''))
        except Exception:
            data = None
            content_type = ''
        if data:
            try:
                if Image is not None:
                    stream = io.BytesIO(data)
                    image = Image.open(stream)
                    image.load()
                    if image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGBA')
                    image.save(target_png, 'PNG')
                    if os.path.exists(target_png) and os.path.getsize(target_png) > 0:
                        self.remote_picon_cache[source_url] = target_png
                        return target_png
            except Exception:
                pass
            ext = guess_image_extension(source_url, content_type)
            fallback_target = os.path.join(REMOTE_PICON_CACHE_DIR, digest + ext)
            try:
                with open(fallback_target, 'wb') as handle:
                    handle.write(data)
                if os.path.exists(fallback_target) and os.path.getsize(fallback_target) > 0:
                    self.remote_picon_cache[source_url] = fallback_target
                    return fallback_target
            except Exception:
                pass
        tmp_target = os.path.join(REMOTE_PICON_CACHE_DIR, digest + '.download')
        try:
            os.system('wget -q --timeout=10 --tries=1 --no-check-certificate -O "%s" "%s"' % (tmp_target, source_url))
            if os.path.exists(tmp_target) and os.path.getsize(tmp_target) > 0:
                try:
                    if Image is not None:
                        image = Image.open(tmp_target)
                        image.load()
                        if image.mode not in ('RGB', 'RGBA'):
                            image = image.convert('RGBA')
                        image.save(target_png, 'PNG')
                        if os.path.exists(target_png) and os.path.getsize(target_png) > 0:
                            self.remote_picon_cache[source_url] = target_png
                            return target_png
                except Exception:
                    pass
                ext = guess_image_extension(source_url, '')
                fallback_target = os.path.join(REMOTE_PICON_CACHE_DIR, digest + ext)
                try:
                    os.rename(tmp_target, fallback_target)
                except Exception:
                    try:
                        with open(tmp_target, 'rb') as src:
                            with open(fallback_target, 'wb') as dst:
                                dst.write(src.read())
                        os.unlink(tmp_target)
                    except Exception:
                        pass
                if os.path.exists(fallback_target) and os.path.getsize(fallback_target) > 0:
                    self.remote_picon_cache[source_url] = fallback_target
                    return fallback_target
        except Exception:
            pass
        try:
            if os.path.exists(tmp_target):
                os.unlink(tmp_target)
        except Exception:
            pass
        self.remote_picon_cache[source_url] = None
        return None

    def find_picon_path(self, station):
        if not station:
            return None
        cache_key = u"|".join([
            to_text(station.get("name", u"")),
            to_text(station.get("picon", u"")),
            to_text(station.get("picon_url", u"")),
        ])
        if cache_key in self.picon_cache:
            return self.picon_cache.get(cache_key)
        explicit = to_text(station.get("picon", u""))
        if explicit and os.path.isabs(explicit) and os.path.exists(explicit) and is_usable_picon_image(explicit):
            self.picon_cache[cache_key] = explicit
            return explicit
        dirs = self.get_picon_dirs()
        candidates = unique_text_list(self.station_picon_candidates(station))
        exact_variants = []
        for candidate in candidates:
            candidate = to_text(candidate).strip()
            if not candidate:
                continue
            exact_variants.extend(unique_text_list([
                candidate,
                candidate.lower(),
                candidate.replace(" ", "_"),
                candidate.replace(" ", ""),
                candidate.replace("_", ""),
                candidate.replace("-", "_"),
                candidate.replace("-", ""),
                candidate.replace("_", "-") if "_" in candidate else candidate,
                candidate.replace("_", "").replace("-", ""),
            ]))
        exact_variants = unique_text_list(exact_variants)
        for directory in dirs:
            for variant in exact_variants:
                for ext in ("", ".png", ".jpg", ".jpeg", ".webp"):
                    path = os.path.join(directory, variant + ext)
                    if os.path.exists(path) and is_usable_picon_image(path):
                        self.picon_cache[cache_key] = path
                        return path
        bouquet_variants = self.bouquet_picon_candidates(station)
        for directory in dirs:
            for variant in bouquet_variants:
                for ext in ("", ".png", ".jpg", ".jpeg", ".webp"):
                    path = os.path.join(directory, variant + ext)
                    if os.path.exists(path) and is_usable_picon_image(path):
                        self.picon_cache[cache_key] = path
                        return path
        remote = self.download_remote_picon(station)
        if remote and is_usable_picon_image(remote):
            self.picon_cache[cache_key] = remote
            return remote
        self.picon_cache[cache_key] = DEFAULT_PICON
        return DEFAULT_PICON

    def update_picon(self, station):
        try:
            path = self.find_picon_path(station) or DEFAULT_PICON
        except Exception:
            path = DEFAULT_PICON
        self.current_picon_path = path
        self.set_pixmap_file("picon", path)
        self.set_pixmap_file("picon_large", path)
        title = tr("picon_title")
        if station:
            title = to_text(station.get("name", u"Station"))
        self["picon_large_title"].setText(title)

    def on_selection_changed(self):
        station = self.get_current_station()
        if not station:
            self["station_name"].setText(tr("no_station"))
            self["station_meta"].setText(tr("add_or_change"))
            self["station_url"].setText(text_type(""))
            self["station_desc"].setText(tr("nothing_to_show"))
            self["station_extra"].setText(text_type(""))
            self.update_cover(None)
            self.update_picon(self.get_picon_station())
            self.set_footer_default()
            return
        name = to_text(station.get("name", u"Unknown"))
        genre = to_text(station.get("genre", u"Other"))
        country = to_text(station.get("country", u"Online"))
        bitrate = to_text(station.get("bitrate", u"?"))
        fav = tr("fav_yes") if name in self.favorites else tr("fav_no")
        meta = tr("meta_line", genre, country, bitrate, fav)
        desc = to_text(station.get("description", u""))
        if not desc:
            desc = tr("metadata_waiting")
        url_line = to_text(station.get("homepage", u"")).strip() or to_text(station.get("url", u"")).strip()
        self["station_name"].setText(name)
        self["station_meta"].setText(meta)
        self["station_url"].setText(shorten_text(url_line, 74 if self.is_fhd else 38))
        self["station_desc"].setText(shorten_text(desc, 168 if self.is_fhd else 82))
        extra_items = []
        metadata_url = to_text(station.get("metadata_url", u"")).strip()
        if metadata_url:
            extra_items.append(u"META API")
        if to_text(station.get("picon_url", u"")).strip():
            extra_items.append(u"REMOTE PICON")
        self["station_extra"].setText(u" | ".join(extra_items))
        self.update_cover(station)
        self.update_picon(self.get_picon_station())
        config.plugins.neoradio.last_station.value = name
        config.plugins.neoradio.last_station.save()
        try:
            config.plugins.neoradio.last_url.value = to_text(station.get("url", u""))
            config.plugins.neoradio.last_url.save()
        except Exception:
            pass
        config.plugins.neoradio.last_filter.value = self.current_filter
        config.plugins.neoradio.last_filter.save()
        configfile.save()

    def move_up(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        self["station_list"].up()
        self.on_selection_changed()

    def move_down(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        self["station_list"].down()
        self.on_selection_changed()

    def page_up(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        self["station_list"].pageUp()
        self.on_selection_changed()

    def page_down(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        self["station_list"].pageDown()
        self.on_selection_changed()

    def resolve_station_url(self, station):
        if not station:
            return text_type("")
        base_url = to_text(station.get("url", u"")).strip()
        if not base_url:
            return text_type("")
        if base_url in self.playlist_cache:
            return self.playlist_cache[base_url]
        resolved = base_url
        if is_playlist_like_url(base_url):
            text = fetch_text_url(base_url)
            parsed = parse_playlist_content(text)
            if parsed:
                resolved = parsed
                if is_playlist_like_url(resolved) and resolved != base_url:
                    nested = parse_playlist_content(fetch_text_url(resolved))
                    if nested:
                        resolved = nested
        self.playlist_cache[base_url] = resolved
        return resolved

    def play_current(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        station = self.get_current_station()
        if not station:
            self.session.open(MessageBox, tr("play_missing"), MessageBox.TYPE_INFO, timeout=5)
            return
        stream_url = self.resolve_station_url(station)
        if not stream_url:
            self.session.open(MessageBox, tr("play_resolve_fail"), MessageBox.TYPE_INFO, timeout=6)
            return
        ref = eServiceReference(4097, 0, stream_url)
        ref.setName(to_text(station.get("name", u"NeoRadio")))
        self.current_service = ref
        self.playing_station_data = station
        try:
            config.plugins.neoradio.last_station.value = to_text(station.get("name", u""))
            config.plugins.neoradio.last_station.save()
            config.plugins.neoradio.last_url.value = to_text(station.get("url", u""))
            config.plugins.neoradio.last_url.save()
            config.plugins.neoradio.last_filter.value = self.current_filter
            config.plugins.neoradio.last_filter.save()
            configfile.save()
            remember_played_station(station)
        except Exception:
            pass
        self.session.nav.playService(ref)
        self.schedule_screensaver()
        self.last_meta_blob = text_type("")
        self["status_label"].setText(tr("status_prefix", tr("playing", to_text(station.get("name", u"")))))
        if stream_url != to_text(station.get("url", u"")):
            self["np_status"].setText(tr("playlist_resolved"))
        else:
            self["np_status"].setText(tr("metadata_waiting"))
        self.update_picon(station)
        self.start_network_metadata_worker(station, stream_url)
        self["spectrum_label"].setText(self.spectrum_frames[self.visualizer_idx % len(self.spectrum_frames)])

    def toggle_favorite(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        station = self.get_current_station()
        if not station:
            return
        name = to_text(station.get("name"))
        if name in self.favorites:
            self.favorites.remove(name)
            msg = tr("removed_fav", name)
        else:
            self.favorites.append(name)
            msg = tr("added_fav", name)
        save_favorites(self.favorites)
        self.refresh_list(select_name=name)
        self["status_label"].setText(tr("status_prefix", msg))

    def open_search(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        if VirtualKeyBoard is None:
            self.session.open(MessageBox, tr("no_keyboard"), MessageBox.TYPE_INFO, timeout=6)
            return
        self.session.openWithCallback(self.search_callback, VirtualKeyBoard, title=tr("search_station"), text=to_text(self.search_term))

    def search_callback(self, text=None):
        self.touch_activity()
        if text is None:
            return
        self.search_term = to_text(text).strip()
        self.refresh_list()

    def safe_info_string(self, info, attr_name):
        try:
            tag = getattr(iServiceInformation, attr_name, None)
            if tag is None:
                return text_type("")
            return to_text(info.getInfoString(tag)).strip()
        except Exception:
            return text_type("")

    def update_now_playing(self):
        station = self.playing_station_data or self.get_current_station()
        fallback_name = to_text(station.get("name", u"-")) if station else u"-"
        title = text_type("")
        artist = text_type("")
        album = text_type("")
        organization = text_type("")
        raw = text_type("")
        try:
            service = self.session.nav.getCurrentService()
            if service:
                info = service.info()
                if info:
                    artist = self.safe_info_string(info, "sTagArtist")
                    title = self.safe_info_string(info, "sTagTitle")
                    album = self.safe_info_string(info, "sTagAlbum")
                    organization = self.safe_info_string(info, "sTagOrganization")
                    raw = self.safe_info_string(info, "sTagComment")
        except Exception:
            pass
        merged = title or raw
        if merged and not artist and u" - " in merged:
            parts = merged.split(u" - ", 1)
            if len(parts) == 2:
                artist = artist or parts[0].strip()
                title = parts[1].strip()
        network = dict(self.network_meta or {})
        used_network = False
        if not title:
            network_title = to_text(network.get('title', '')).strip()
            if network_title:
                title = network_title
                used_network = True
        if (not artist or artist == u'-'):
            network_artist = to_text(network.get('artist', '')).strip()
            if network_artist:
                artist = network_artist
                used_network = True
        if not album:
            network_album = to_text(network.get('album', '')).strip() or to_text(network.get('program', '')).strip() or to_text(network.get('stream_name', '')).strip()
            if network_album:
                album = network_album
                used_network = True
        if not raw:
            raw = to_text(network.get('radio_text', '')).strip() or to_text(network.get('raw_title', '')).strip()
        if not title:
            title = fallback_name
        if not artist:
            artist = u"-"
        if not album:
            album = organization or to_text(network.get('stream_description', '')).strip() or u"-"
        meta_blob = u"%s|%s|%s" % (title, artist, album)
        if meta_blob != self.last_meta_blob:
            self.last_meta_blob = meta_blob
            self["np_title"].setText(tr("title_fmt", title))
            self["np_artist"].setText(tr("artist_fmt", artist))
            self["np_album"].setText(tr("album_fmt", album))
        has_service_meta = bool((title and title != fallback_name) or (artist and artist != u'-') or (organization and organization != u'-'))
        has_network_meta = bool(network.get('title') or network.get('artist') or network.get('radio_text') or network.get('program') or network.get('stream_name'))
        if has_network_meta or used_network:
            self["np_status"].setText(tr("metadata_network_active") if has_service_meta else tr("metadata_active"))
            detail_parts = []
            radio_text = to_text(network.get('radio_text', '')).strip() or to_text(network.get('raw_title', '')).strip() or raw
            stream_name = to_text(network.get('stream_name', '')).strip()
            if radio_text:
                detail_parts.append(shorten_text(radio_text, 42 if self.is_fhd else 22))
            elif stream_name:
                detail_parts.append(shorten_text(stream_name, 42 if self.is_fhd else 22))
            updated_at = to_text(network.get('updated_at', '')).strip()
            if updated_at:
                detail_parts.append(updated_at)
            self.set_footer_metadata(network.get('source_kind', 'service'), u" • ".join([x for x in detail_parts if x]))
            current = self.get_current_station()
            if current and station and to_text(current.get('name')) == to_text(station.get('name')) and to_text(current.get('url')) == to_text(station.get('url')):
                desc_parts = []
                base_desc = to_text(station.get('description', u'')).strip()
                if base_desc and base_desc != u'-':
                    desc_parts.append(base_desc)
                if radio_text and radio_text != base_desc:
                    desc_parts.append(radio_text)
                self["station_desc"].setText(shorten_text(u"\n\n".join(desc_parts), 280 if self.is_fhd else 150))
        elif has_service_meta:
            self["np_status"].setText(tr("metadata_active"))
            self.set_footer_metadata('service', shorten_text(u"%s • %s" % (artist, title) if artist != u'-' else title, 62 if self.is_fhd else 34))
        else:
            self["np_status"].setText(tr("metadata_missing"))
            if self.footer_mode != 'default':
                self.set_footer_default()

    def show_details(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        station = self.get_current_station()
        if not station:
            return
        text = tr("details_text", PLUGIN_VERSION, to_text(station.get("name", u"-")), to_text(station.get("genre", u"-")), to_text(station.get("country", u"-")), to_text(station.get("bitrate", u"-")), to_text(station.get("description", u"-")), to_text(station.get("url", u"-")), to_text(station.get("homepage", u"-")))
        self.session.open(MessageBox, text, MessageBox.TYPE_INFO)

    def open_filter_menu(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        options = []
        for item in self.get_filters():
            options.append((item, ("filter", item)))
        self.session.openWithCallback(self.menu_callback, ChoiceBox, title=tr("filter_title"), list=options)

    def open_main_menu(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        options = []
        options.append((tr("menu_choose_filter"), ("choose_filter", None)))
        options.append((tr("menu_search"), ("open_search", None)))
        options.append((tr("menu_clear_search"), ("search", text_type(""))))
        options.append((tr("menu_keep", tr("yes") if config.plugins.neoradio.keep_playing.value else tr("no")), ("toggle_keep", None)))
        options.append((tr("menu_autoplay", tr("yes") if config.plugins.neoradio.autoplay_last.value else tr("no")), ("toggle_autoplay", None)))
        country_value = self.get_default_country() or tr("all_countries")
        picon_value = to_text(config.plugins.neoradio.picon_paths.value).strip() or u"auto"
        if len(picon_value) > 52:
            picon_value = picon_value[:49] + u"..."
        options.append((tr("menu_country", country_value), ("choose_country", None)))
        options.append((tr("menu_station_language", tr("all")), ("choose_station_language", None)))
        options.append((tr("menu_lang", language_label(config.plugins.neoradio.ui_language.value)), ("choose_language", None)))
        options.append((tr("menu_saver", screensaver_timeout_label()), ("choose_screensaver", None)))
        options.append((tr("menu_picons", picon_value), ("picon_paths", None)))
        options.append((tr("menu_github_check"), ("github_check", None)))
        options.append((tr("menu_reload"), ("reload", None)))
        options.append((tr("menu_about"), ("about", None)))
        self.session.openWithCallback(self.menu_callback, ChoiceBox, title=tr("menu_title"), list=options)

    def menu_callback(self, answer):
        if not answer:
            return
        self.touch_activity()
        value = answer[1]
        action = value[0]
        payload = value[1]
        if action == "filter":
            self.current_filter = to_text(payload)
            self.refresh_list()
        elif action == "choose_filter":
            self.open_filter_menu()
        elif action == "open_search":
            self.open_search()
        elif action == "search":
            self.search_term = text_type("")
            self.refresh_list()
        elif action == "toggle_keep":
            config.plugins.neoradio.keep_playing.value = not config.plugins.neoradio.keep_playing.value
            config.plugins.neoradio.keep_playing.save()
            configfile.save()
            self["status_label"].setText(tr("status_prefix", tr("menu_keep", tr("yes") if config.plugins.neoradio.keep_playing.value else tr("no"))))
        elif action == "toggle_autoplay":
            config.plugins.neoradio.autoplay_last.value = not config.plugins.neoradio.autoplay_last.value
            config.plugins.neoradio.autoplay_last.save()
            configfile.save()
            self["status_label"].setText(tr("status_prefix", tr("menu_autoplay", tr("yes") if config.plugins.neoradio.autoplay_last.value else tr("no"))))
        elif action == "choose_country":
            self.choose_country()
        elif action == "choose_language":
            self.choose_language()
        elif action == "choose_station_language":
            self.choose_station_language()
        elif action == "choose_screensaver":
            self.choose_screensaver()
        elif action == "picon_paths":
            current = to_text(config.plugins.neoradio.picon_paths.value)
            if VirtualKeyBoard is None:
                self.session.open(MessageBox, tr("no_keyboard_settings"), MessageBox.TYPE_INFO, timeout=7)
            else:
                self.session.openWithCallback(self.picon_paths_callback, VirtualKeyBoard, title=tr("picon_paths_title"), text=current)
        elif action == "github_check":
            self.check_github_updates()
        elif action == "reload":
            self.clear_picon_cache()
            self.refresh_list(select_name=to_text(config.plugins.neoradio.last_station.value), select_url=to_text(getattr(config.plugins.neoradio, "last_url", "").value))
            self.update_picon(self.get_picon_station())
            self["status_label"].setText(tr("status_prefix", tr("reloaded")))
        elif action == "about":
            about = tr("about_text", PLUGIN_VERSION, FAV_FILE, USER_STATIONS_FILE)
            self.session.open(MessageBox, about, MessageBox.TYPE_INFO)

    def choose_country(self):
        options = [(tr("all_countries"), u"")]
        for country in self.get_available_countries():
            options.append((country, country))
        self.session.openWithCallback(self.country_choice_callback, ChoiceBox, title=tr("choose_country"), list=options)

    def country_choice_callback(self, answer):
        if not answer:
            return
        value = to_text(answer[1]).strip()
        config.plugins.neoradio.default_country.value = value
        config.plugins.neoradio.default_country.save()
        configfile.save()
        self.current_filter = self.get_default_filter()
        self.refresh_list()
        if value:
            self["status_label"].setText(tr("status_prefix", tr("country_set", value)))
        else:
            self["status_label"].setText(tr("status_prefix", tr("country_all")))

    def get_available_station_languages(self):
        seen = {}
        result = []
        for station in self.base_stations:
            lang = normalize_station_language(station.get("language", u""), station.get("country", u""), station.get("name", u""), station.get("group", u""), station.get("url", u""))
            if lang and lang not in seen:
                seen[lang] = True
        for lang in STATION_LANGUAGE_ORDER:
            if lang in seen:
                result.append(lang)
        for lang in sorted(seen.keys()):
            if lang not in result:
                result.append(lang)
        return result

    def choose_station_language(self):
        options = [(tr("all"), u"")]
        for lang in self.get_available_station_languages():
            options.append((lang, lang))
        self.session.openWithCallback(self.station_language_choice_callback, ChoiceBox, title=tr("choose_station_language"), list=options)

    def station_language_choice_callback(self, answer):
        if not answer:
            return
        value = normalize_station_language(answer[1]) if to_text(answer[1]).strip() else u""
        self.current_filter = format_language_filter(value) if value else tr("all")
        config.plugins.neoradio.last_filter.value = self.current_filter
        config.plugins.neoradio.last_filter.save()
        configfile.save()
        self.refresh_list(select_name=to_text(config.plugins.neoradio.last_station.value), select_url=to_text(getattr(config.plugins.neoradio, "last_url", "").value))
        if value:
            self["status_label"].setText(tr("status_prefix", tr("station_language_set", value)))

    def choose_language(self):
        options = [(tr("auto"), "auto"), (tr("polish"), "pl"), (tr("english"), "en")]
        self.session.openWithCallback(self.language_choice_callback, ChoiceBox, title=tr("choose_language"), list=options)

    def language_choice_callback(self, answer):
        if not answer:
            return
        value = to_text(answer[1]).strip() or 'auto'
        config.plugins.neoradio.ui_language.value = value
        config.plugins.neoradio.ui_language.save()
        configfile.save()
        self.apply_language()
        self.current_filter = self.get_default_filter() if self.current_filter in (tr("all"), tr("favorites")) else self.current_filter
        self.refresh_list(select_name=to_text(config.plugins.neoradio.last_station.value), select_url=to_text(getattr(config.plugins.neoradio, "last_url", "").value))
        self["status_label"].setText(tr("status_prefix", tr("lang_set", language_label(value))))

    def choose_screensaver(self):
        options = [(tr("screensaver_off"), "0"), (screensaver_timeout_label(1), "1"), (screensaver_timeout_label(2), "2"), (screensaver_timeout_label(3), "3"), (screensaver_timeout_label(5), "5"), (screensaver_timeout_label(10), "10")]
        self.session.openWithCallback(self.screensaver_choice_callback, ChoiceBox, title=tr("choose_saver"), list=options)

    def screensaver_choice_callback(self, answer):
        if not answer:
            return
        value = to_text(answer[1]).strip() or '0'
        config.plugins.neoradio.screensaver_timeout.value = value
        config.plugins.neoradio.screensaver_timeout.save()
        configfile.save()
        self.touch_activity()
        self["status_label"].setText(tr("status_prefix", tr("saver_set", screensaver_timeout_label(int(value)))))

    def github_url_callback(self, text=None):
        if text is None:
            return
        value = to_text(text).strip()
        config.plugins.neoradio.github_manifest_url.value = value
        config.plugins.neoradio.github_manifest_url.save()
        configfile.save()
        self["status_label"].setText(tr("status_prefix", tr("menu_github_url", value or tr("none"))))

    def check_github_updates(self):
        url = to_text(config.plugins.neoradio.github_manifest_url.value).strip() or DEFAULT_GITHUB_MANIFEST_URL
        if not url:
            self.session.open(MessageBox, tr("github_not_set"), MessageBox.TYPE_INFO, timeout=6)
            return
        self["status_label"].setText(tr("status_prefix", tr("github_checking")))
        try:
            raw = fetch_text_url(url, timeout=10)
            info = json.loads(raw)
            remote_version = to_text(info.get('version', u'')).strip()
            if not remote_version:
                raise Exception('missing version')
            if is_remote_version_newer(remote_version, PLUGIN_VERSION):
                ipk_url = extract_manifest_ipk_url(info)
                if not ipk_url:
                    self.session.open(MessageBox, tr("github_missing_ipk"), MessageBox.TYPE_INFO, timeout=8)
                    return
                changelog = to_text(info.get('changelog', u'-')).strip() or u'-'
                self.github_update_info = {
                    'version': remote_version,
                    'ipk': ipk_url,
                    'changelog': changelog,
                }
                prompt = tr("github_install_prompt", remote_version, changelog)
                self.session.openWithCallback(self.github_install_prompt_callback, MessageBox, prompt, MessageBox.TYPE_YESNO)
            else:
                self.session.open(MessageBox, tr("github_up_to_date"), MessageBox.TYPE_INFO, timeout=6)
        except Exception:
            self.session.open(MessageBox, tr("github_error"), MessageBox.TYPE_INFO, timeout=6)

    def github_install_prompt_callback(self, answer):
        if not answer:
            return
        info = self.github_update_info or {}
        ipk_url = to_text(info.get('ipk', u'')).strip()
        remote_version = to_text(info.get('version', u'')).strip() or u'?'
        if not ipk_url:
            self.session.open(MessageBox, tr("github_missing_ipk"), MessageBox.TYPE_INFO, timeout=8)
            return
        self.install_github_update(ipk_url, remote_version)

    def install_github_update(self, ipk_url, remote_version):
        self.touch_activity()
        self["status_label"].setText(tr("status_prefix", tr("github_installing", remote_version)))
        safe_url = to_text(ipk_url).replace('"', '%22')
        cmd = 'rm -f "%(tmp)s"; wget --no-check-certificate -O "%(tmp)s" "%(url)s" && opkg install --force-reinstall "%(tmp)s"' % {
            'tmp': UPDATE_TEMP_IPK,
            'url': safe_url,
        }
        self.github_update_info['version'] = remote_version
        if ComponentsConsole is not None:
            try:
                self.github_console = ComponentsConsole()
                self.github_console.ePopen(cmd, self.github_install_finished)
                return
            except Exception:
                self.github_console = None
        retval = os.system(cmd)
        self.github_install_finished(text_type(''), retval, None)

    def github_install_finished(self, result, retval, extra_args=None):
        try:
            if os.path.exists(UPDATE_TEMP_IPK):
                os.remove(UPDATE_TEMP_IPK)
        except Exception:
            pass
        remote_version = to_text((self.github_update_info or {}).get('version', u'?'))
        if retval == 0:
            self.session.openWithCallback(self.github_restart_callback, MessageBox, tr("github_install_ok", remote_version), MessageBox.TYPE_YESNO)
        else:
            output = to_text(result).strip()
            if not output:
                output = u'opkg/wget returned code %s' % to_text(retval)
            if len(output) > 700:
                output = output[-700:]
            self.session.open(MessageBox, tr("github_install_fail", remote_version, output), MessageBox.TYPE_INFO, timeout=12)

    def github_restart_callback(self, answer):
        if answer:
            self["status_label"].setText(tr("status_prefix", tr("github_restarting")))
            os.system('(sleep 2; killall -9 enigma2) >/dev/null 2>&1 &')
        else:
            self["status_label"].setText(tr("status_prefix", tr("github_restart_later")))

    def picon_paths_callback(self, text=None):
        if text is None:
            return
        value = to_text(text).strip()
        config.plugins.neoradio.picon_paths.value = value
        config.plugins.neoradio.picon_paths.save()
        configfile.save()
        self.clear_picon_cache()
        self.update_picon(self.get_picon_station())
        if value:
            self["status_label"].setText(tr("status_prefix", tr("saved_picons")))
        else:
            self["status_label"].setText(tr("status_prefix", tr("auto_picons")))

    def close_plugin(self):
        if self.consume_screensaver_key():
            return
        self.touch_activity()
        self.network_meta_worker_id += 1
        try:
            self.timer.stop()
        except Exception:
            pass
        if not config.plugins.neoradio.keep_playing.value:
            try:
                if self.previous_service is not None:
                    self.session.nav.playService(self.previous_service)
            except Exception:
                pass
        self.close()


def main(session, **kwargs):
    session.open(NeoRadioMain)


def Plugins(**kwargs):
    return [PluginDescriptor(name=PLUGIN_TITLE, description=tr("plugin_desc"), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon="plugin.png", fnc=main)]
