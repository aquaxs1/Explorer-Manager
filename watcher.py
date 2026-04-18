"""
watcher.py – Hintergrundprozess der Dateien überwacht und sortiert.
Benötigt: pip install watchdog
"""

import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Wächter] %(message)s",
    datefmt="%H:%M:%S"
)


def matches_rule(filepath: Path, rule: dict) -> bool:
    """Prüft ob eine Datei zu einer Regel passt."""
    filename_filter = rule.get("filename", "").strip().lower()
    filetype_filter = rule.get("filetype", "not defined").strip().lower()

    # Dateiname prüfen (leer = alle)
    if filename_filter and filename_filter not in filepath.name.lower():
        return False

    # Dateiendung prüfen
    if filetype_filter != "not defined":
        if filepath.suffix.lower() != filetype_filter:
            return False

    return True


def sort_file(filepath: Path, rules: list):
    """Versucht eine Datei anhand der Regeln zu sortieren."""
    # Kurz warten damit die Datei vollständig geschrieben ist
    time.sleep(0.5)

    if not filepath.exists():
        return  # Datei wurde schon verschoben

    for rule in rules:
        dest_str = rule.get("destination", "").strip()
        if not dest_str or dest_str.startswith("—"):
            continue

        dest = Path(dest_str)
        if not dest.exists():
            logging.warning(f"Zielordner existiert nicht: {dest}")
            continue

        if matches_rule(filepath, rule):
            target = dest / filepath.name

            # Namenskonflikt vermeiden
            counter = 1
            while target.exists():
                target = dest / f"{filepath.stem}_{counter}{filepath.suffix}"
                counter += 1

            try:
                shutil.move(str(filepath), str(target))
                logging.info(f"Verschoben: {filepath.name} → {dest}")
            except Exception as e:
                logging.error(f"Fehler beim Verschieben: {e}")
            return  # Erste passende Regel gewinnt


class SorterHandler(FileSystemEventHandler):
    def __init__(self, rules: list):
        super().__init__()
        self.rules = rules

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        logging.info(f"Neue Datei erkannt: {filepath.name}")
        sort_file(filepath, self.rules)

    def on_moved(self, event):
        """Auch beim Einfügen per Drag & Drop / Umbenennen reagieren."""
        if event.is_directory:
            return
        filepath = Path(event.dest_path)
        logging.info(f"Datei bewegt: {filepath.name}")
        sort_file(filepath, self.rules)


def start_watcher(watch_folder: str, rules: list, stop_event):
    """Startet den Ordner-Wächter. Läuft bis stop_event gesetzt wird."""
    folder = Path(watch_folder)
    if not folder.exists():
        logging.error(f"Überwachter Ordner existiert nicht: {folder}")
        return

    handler = SorterHandler(rules)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()
    logging.info(f"Wächter gestartet für: {folder}")

    try:
        while not stop_event.is_set():
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
        logging.info("Wächter gestoppt.")


def stop_watcher(stop_event):
    """Stoppt den laufenden Wächter."""
    stop_event.set()