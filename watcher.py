"""
watcher.py - the background half of Explorer Manager.

Watches folders and moves new files where the rules say they belong. Also used
for "Sort existing files", which applies the same rules to what is already
lying in a source folder.

Requires: pip install watchdog
"""

import logging
import shutil
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from settings import active_rules

log = logging.getLogger(__name__)

# Half-finished downloads and the temp files editors leave behind. Moving one
# of these breaks the program that is still writing it.
IGNORED_SUFFIXES = {
    ".crdownload", ".part", ".partial", ".download", ".opdownload",
    ".tmp", ".temp", ".!ut", ".aria2",
}
IGNORED_PREFIXES = ("~$", ".~")

# How long to wait for a file to stop growing before giving up on it.
STABLE_TIMEOUT = 120.0
STABLE_INTERVAL = 0.5
STABLE_READINGS = 2


def is_temporary(filepath: Path) -> bool:
    """True for browser part-files and editor scratch files."""
    return (filepath.suffix.lower() in IGNORED_SUFFIXES
            or filepath.name.startswith(IGNORED_PREFIXES))


def wait_until_complete(filepath: Path, timeout: float = STABLE_TIMEOUT,
                        interval: float = STABLE_INTERVAL) -> bool:
    """Wait until the file has stopped growing.

    A 12 GB download needs minutes, not the half second the old version waited,
    and moving it early leaves the browser writing into thin air. Returns False
    if the file disappeared or never settled within the timeout.
    """
    deadline = time.monotonic() + timeout
    last_size = -1
    stable = 0
    while time.monotonic() < deadline:
        try:
            size = filepath.stat().st_size
        except FileNotFoundError:
            return False
        except OSError:
            # Still locked by the writer - give it another round.
            size = -1
        if size >= 0 and size == last_size:
            stable += 1
            if stable >= STABLE_READINGS:
                return True
        else:
            stable = 0
        last_size = size
        time.sleep(interval)
    log.warning("Gave up waiting for %s to finish writing", filepath.name)
    return False


def matches_rule(filepath: Path, rule: dict) -> bool:
    """Return True if the file matches the rule."""
    filename_filter = rule.get("filename", "").strip().lower()
    filetype_filter = rule.get("filetype", "not defined").strip().lower()

    # Filename filter (empty matches everything)
    if filename_filter and filename_filter not in filepath.name.lower():
        return False

    # File extension filter
    if filetype_filter != "not defined":
        if filepath.suffix.lower() != filetype_filter:
            return False

    return True


def unique_target(dest: Path, filepath: Path) -> Path:
    """A free path in dest - existing files are never overwritten."""
    target = dest / filepath.name
    counter = 1
    while target.exists():
        target = dest / f"{filepath.stem}_{counter}{filepath.suffix}"
        counter += 1
    return target


def move_file(filepath: Path, dest: Path) -> bool:
    """Move one file into dest, creating dest if it is missing."""
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        log.error("Could not create the destination folder %s: %s", dest, error)
        return False

    try:
        target = unique_target(dest, filepath)
        shutil.move(str(filepath), str(target))
        log.info("Moved: %s -> %s", filepath.name, target.parent)
        return True
    except (OSError, shutil.Error) as error:
        log.error("Could not move %s: %s", filepath.name, error)
        return False


def sort_file(filepath: Path, rules: list, wait: bool = True) -> bool:
    """Move a file to the destination of the first rule it matches.

    Returns True if the file was moved. Disabled and unfinished rules are
    ignored, so only rules the user actually switched on can claim a file.
    """
    filepath = Path(filepath)
    if is_temporary(filepath):
        log.debug("Ignoring temporary file: %s", filepath.name)
        return False

    usable = active_rules(rules)
    if not usable:
        return False

    if wait:
        if not wait_until_complete(filepath):
            return False
    elif not filepath.exists():
        return False

    if not filepath.exists():
        return False  # already moved by something else

    for rule in usable:
        dest = Path(rule["destination"])
        try:
            same_folder = dest.resolve() == filepath.parent.resolve()
        except OSError:
            same_folder = False
        if same_folder:
            continue  # the file is already where this rule wants it

        if matches_rule(filepath, rule):
            return move_file(filepath, dest)  # first matching rule wins
    return False


def sort_existing(folder, rules: list, recursive: bool = False) -> int:
    """Apply the rules to the files already lying in a folder.

    The watcher only ever sees new arrivals; this is how the pile that was
    there before gets cleaned up. Returns the number of files moved.
    """
    folder = Path(folder)
    if not folder.exists():
        log.error("Source folder does not exist: %s", folder)
        return 0

    usable = active_rules(rules)
    if not usable:
        return 0

    paths = sorted(folder.rglob("*") if recursive else folder.glob("*"))
    moved = 0
    for path in paths:
        if path.is_dir():
            continue
        if sort_file(path, usable, wait=False):
            moved += 1
    log.info("Sorted %s existing file(s) in %s", moved, folder)
    return moved


class SorterHandler(FileSystemEventHandler):
    def __init__(self, rules: list):
        super().__init__()
        self.rules = rules

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if is_temporary(filepath):
            return
        log.info("New file detected: %s", filepath.name)
        sort_file(filepath, self.rules)

    def on_moved(self, event):
        """Also react to drag & drop and renames, not just new files.

        A finished download is renamed from .crdownload to its real name, so
        this is where most browser downloads actually arrive.
        """
        if event.is_directory:
            return
        filepath = Path(event.dest_path)
        if is_temporary(filepath):
            return
        log.info("File moved in: %s", filepath.name)
        sort_file(filepath, self.rules)


def start_watcher(watch_folder: str, rules: list, stop_event, recursive: bool = False):
    """Start watching a folder. Runs until stop_event is set."""
    folder = Path(watch_folder)
    if not folder.exists():
        log.error("Watched folder does not exist: %s", folder)
        return

    handler = SorterHandler(rules)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=recursive)
    observer.start()
    log.info("Watching: %s%s", folder, " (with subfolders)" if recursive else "")

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    finally:
        observer.stop()
        observer.join()
        log.info("Stopped watching: %s", folder)


def stop_watcher(stop_event):
    """Stop the running watcher."""
    stop_event.set()
