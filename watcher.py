"""
watcher.py - background process that watches folders and sorts new files.
Requires: pip install watchdog
"""

import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Watcher] %(message)s",
    datefmt="%H:%M:%S"
)


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


def sort_file(filepath: Path, rules: list):
    """Move a file to the destination of the first rule it matches."""
    # Wait briefly so the file is written completely before it is moved
    time.sleep(0.5)

    if not filepath.exists():
        return  # already moved by something else

    for rule in rules:
        dest_str = rule.get("destination", "").strip()
        if not dest_str or dest_str.startswith("—"):
            continue

        dest = Path(dest_str)
        if not dest.exists():
            logging.warning(f"Destination folder does not exist: {dest}")
            continue

        if matches_rule(filepath, rule):
            target = dest / filepath.name

            # Avoid overwriting an existing file
            counter = 1
            while target.exists():
                target = dest / f"{filepath.stem}_{counter}{filepath.suffix}"
                counter += 1

            try:
                shutil.move(str(filepath), str(target))
                logging.info(f"Moved: {filepath.name} -> {dest}")
            except Exception as e:
                logging.error(f"Could not move the file: {e}")
            return  # first matching rule wins


class SorterHandler(FileSystemEventHandler):
    def __init__(self, rules: list):
        super().__init__()
        self.rules = rules

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        logging.info(f"New file detected: {filepath.name}")
        sort_file(filepath, self.rules)

    def on_moved(self, event):
        """Also react to drag & drop and renames, not just new files."""
        if event.is_directory:
            return
        filepath = Path(event.dest_path)
        logging.info(f"File moved in: {filepath.name}")
        sort_file(filepath, self.rules)


def start_watcher(watch_folder: str, rules: list, stop_event):
    """Start watching a folder. Runs until stop_event is set."""
    folder = Path(watch_folder)
    if not folder.exists():
        logging.error(f"Watched folder does not exist: {folder}")
        return

    handler = SorterHandler(rules)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()
    logging.info(f"Watching: {folder}")

    try:
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
        logging.info("Watcher stopped.")


def stop_watcher(stop_event):
    """Stop the running watcher."""
    stop_event.set()