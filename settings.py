"""
settings.py - where Explorer Manager keeps its configuration.

Pure logic, no GUI: main.py and watcher.py both import from here and the tests
exercise it directly. Everything a rule or a source folder needs to survive a
restart is normalised in this module, so a broken or half-finished entry never
reaches the watchers.
"""

import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

SETTINGS_VERSION = 2

# Shown in a rule until a destination folder has been picked. A rule still
# carrying it is unfinished: it is never saved and never handed to a watcher.
DEST_PLACEHOLDER = "-- select destination --"

LOG_MAX_BYTES = 512 * 1024
LOG_BACKUPS = 2


def resource_path(*parts):
    """Locate a bundled file, both in the source tree and inside the .exe."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def app_dir():
    """The writable folder the app owns - %APPDATA%\\ExplorerManager on Windows."""
    override = os.getenv("EXPLORER_MANAGER_HOME")
    if override:
        return Path(override)
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "ExplorerManager"
    # Keeps the app (and the tests) usable when there is no %APPDATA%.
    return Path.home() / ".config" / "ExplorerManager"


def settings_file():
    return app_dir() / "settings.json"


def log_file():
    return app_dir() / "explorer-manager.log"


def ensure_app_dir():
    directory = app_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def configure_logging(to_file=True):
    """Log to the console and, when possible, to a file next to the settings.

    The file matters most in silent mode, where the window never appears and
    the console output goes nowhere.
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)

    if not to_file or any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return
    try:
        ensure_app_dir()
        handler = RotatingFileHandler(log_file(), maxBytes=LOG_MAX_BYTES,
                                      backupCount=LOG_BACKUPS, encoding="utf-8")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    except OSError as error:
        logging.warning("No log file (%s)", error)


# --------------------------------------------------------------------- rules

def has_destination(rule):
    """True if the rule points at a real folder instead of the placeholder."""
    dest = str(rule.get("destination", "")).strip()
    return bool(dest) and dest != DEST_PLACEHOLDER and not dest.startswith(("-", "—"))


def normalise_rule(raw):
    """One stored rule, or None if it is unusable.

    A rule without a destination cannot move anything - it only produces
    warnings in the log and clutters the list on the next start.
    """
    if not isinstance(raw, dict) or not has_destination(raw):
        return None
    return {
        "filename": str(raw.get("filename", "")).strip(),
        "filetype": str(raw.get("filetype", "not defined")).strip() or "not defined",
        "destination": str(raw.get("destination", "")).strip(),
        "enabled": bool(raw.get("enabled", True)),
    }


def clean_rules(rules):
    """Keep only usable rules, in their original order."""
    if not isinstance(rules, list):
        return []
    return [rule for rule in (normalise_rule(raw) for raw in rules) if rule]


def active_rules(rules):
    """The rules a watcher should actually apply."""
    return [rule for rule in clean_rules(rules) if rule["enabled"]]


# ------------------------------------------------------------ source folders

def normalise_folder(raw):
    """One stored source folder, or None if there is no path in it.

    Accepts the plain strings written by version 1 as well as the dicts used
    since version 2.
    """
    if isinstance(raw, str):
        raw = {"path": raw}
    if not isinstance(raw, dict):
        return None
    path = str(raw.get("path", "")).strip()
    if not path:
        return None
    return {
        "path": path,
        "active": bool(raw.get("active", True)),
        "recursive": bool(raw.get("recursive", False)),
    }


def clean_folders(folders):
    """Unique source folders, in the order they were added."""
    if not isinstance(folders, list):
        return []
    cleaned, seen = [], set()
    for raw in folders:
        folder = normalise_folder(raw)
        if folder and folder["path"] not in seen:
            seen.add(folder["path"])
            cleaned.append(folder)
    return cleaned


# ------------------------------------------------------------------- file io

def load_settings(path=None):
    """Read the settings file. A fresh install always starts completely empty.

    Files written by version 1 (plain folder strings, rules without an on/off
    flag) are migrated on the way in.
    """
    path = Path(path) if path else settings_file()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {
                    "version": SETTINGS_VERSION,
                    "rules": clean_rules(data.get("rules", [])),
                    "watch_folders": clean_folders(data.get("watch_folders", [])),
                }
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
            logging.warning("Could not read %s (%s) - starting empty", path, error)
    return {"version": SETTINGS_VERSION, "rules": [], "watch_folders": []}


def save_settings(rules, watch_folders, path=None):
    """Write the settings file. Raises OSError if the file cannot be written."""
    path = Path(path) if path else settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": SETTINGS_VERSION,
        "rules": clean_rules(rules),
        "watch_folders": clean_folders(watch_folders),
    }
    # Write beside the target first so a crash cannot leave a half-written file.
    temp = path.with_suffix(".json.tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp.replace(path)
    return data
