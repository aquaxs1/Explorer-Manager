"""
Explorer Manager - Professional Version
Fixes: Scrollable Rules, GUI Realignment, Autostart Crash, AppData Save.

BY SEBASTIAN/AQUAXS - All rights reserved
"""

import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import customtkinter as ctk
import winreg as reg

try:
    from watcher import start_watcher
    from help_texts import HELP_TEXTS
except ImportError:
    HELP_TEXTS = {"en": "Help file missing."}

# --- Settings live in AppData, which is always writable ---
appdata_dir = Path(os.getenv('APPDATA')) / "ExplorerManager"
appdata_dir.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE = appdata_dir / "settings.json"


def resource_path(*parts):
    """Locate a bundled file, both in the source tree and inside the .exe."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


ICON_FILE = resource_path("assets", "icon.ico")   # title bar / taskbar on Windows
ICON_PNG = resource_path("assets", "icon.png")    # fallback for iconphoto()
LOGO_FILE = resource_path("assets", "logo.png")   # the mark shown in the header

# Shown in a rule until a destination folder has been picked. A rule still
# carrying it is unfinished: it is never saved and never handed to a watcher.
DEST_PLACEHOLDER = "-- select destination --"

FILE_TYPES = [
    "not defined",
    ".exe", ".jar", ".pdf", ".txt", ".zip", ".rar", ".7z",
    ".docx", ".xlsx", ".pptx", ".doc", ".xls",
    ".mp3", ".mp4", ".wav", ".mkv", ".avi",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".csv", ".json", ".xml", ".html", ".py", ".js", ".ts",
    ".iso", ".dmg", ".apk", ".deb", ".rpm",
]

LANGUAGES = {
    "Deutsch": "de",
    "English": "en",
    "Francais": "fr",
    "Espanol": "es",
    "Italiano": "it",
    "Polski": "pl",
    "Japanese": "ja",
}

def has_destination(rule):
    """True if the rule points at a real folder instead of the placeholder."""
    dest = str(rule.get("destination", "")).strip()
    return bool(dest) and dest != DEST_PLACEHOLDER and not dest.startswith(("-", "\u2014"))

def clean_rules(rules):
    """Keep only usable rules, so no half-finished filter is stored or applied.

    A rule without a destination cannot move anything - it only produces
    warnings in the log and clutters the list on the next start.
    """
    cleaned = []
    for rule in rules if isinstance(rules, list) else []:
        if not isinstance(rule, dict) or not has_destination(rule):
            continue
        cleaned.append({
            "filename": str(rule.get("filename", "")).strip(),
            "filetype": str(rule.get("filetype", "not defined")).strip() or "not defined",
            "destination": str(rule.get("destination", "")).strip(),
        })
    return cleaned

def clean_folders(folders):
    """Unique, non-empty folder paths, in the order they were added."""
    cleaned = []
    for folder in folders if isinstance(folders, list) else []:
        if not isinstance(folder, str):
            continue
        folder = folder.strip()
        if folder and folder not in cleaned:
            cleaned.append(folder)
    return cleaned

def load_settings():
    """Read the settings file. A fresh install always starts completely empty."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {
                    "rules": clean_rules(data.get("rules", [])),
                    "watch_folders": clean_folders(data.get("watch_folders", [])),
                }
        except (json.JSONDecodeError, OSError):
            pass
    return {"rules": [], "watch_folders": []}

def save_settings(rules, watch_folders):
    data = {"rules": clean_rules(rules), "watch_folders": clean_folders(watch_folders)}
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def toggle_autostart(enable=True):
    app_path = os.path.realpath(sys.argv[0])
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "ExplorerManager"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        if enable:
            reg.SetValueEx(key, app_name, 0, reg.REG_SZ, f'"{app_path}" --silent')
        else:
            try: reg.DeleteValue(key, app_name)
            except FileNotFoundError: pass
        reg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Autostart Error: {e}")
        return False

class WatchFolderRow(ctk.CTkFrame):
    def __init__(self, parent, folder_path, on_toggle, on_delete, **kwargs):
        super().__init__(parent, fg_color="#ffffff", border_width=1, border_color="#e0e0e0", corner_radius=6, **kwargs)
        self.folder_path = folder_path
        
        self.active_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="", variable=self.active_var, command=lambda: on_toggle(folder_path, self.active_var.get()), width=20).pack(side="left", padx=10)
        
        lbl = ctk.CTkLabel(self, text=folder_path, font=("Segoe UI", 11), text_color="#333333", anchor="w")
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(self, text="Delete", width=60, height=24, fg_color="#eb4d4b", hover_color="#ff7979", command=lambda: on_delete(folder_path)).pack(side="right", padx=10)
        self.pack(fill="x", padx=10, pady=2)

class RuleRow(ctk.CTkFrame):
    def __init__(self, parent, on_delete, rule_number, **kwargs):
        super().__init__(parent, fg_color="#fcfcfc", border_width=1, border_color="#dcdde1", corner_radius=8, **kwargs)
        self.on_delete = on_delete
        
        # Header
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(5, 0))
        self.label = ctk.CTkLabel(top_row, text=f"RULE {rule_number}", font=("Segoe UI", 12, "bold"), text_color="#2f3640")
        self.label.pack(side="left")
        ctk.CTkButton(top_row, text="Remove", width=70, height=22, fg_color="transparent", text_color="#eb4d4b", hover_color="#f5f6fa", border_width=1, border_color="#eb4d4b", command=self.on_delete).pack(side="right")

        # Input Grid
        input_grid = ctk.CTkFrame(self, fg_color="transparent")
        input_grid.pack(fill="x", padx=10, pady=10)
        input_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_grid, text="Filename contains:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=2)
        self.filename_var = tk.StringVar()
        ctk.CTkEntry(input_grid, textvariable=self.filename_var, placeholder_text="e.g. Invoice", height=28).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        ctk.CTkLabel(input_grid, text="File Type:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=2)
        self.filetype_var = tk.StringVar(value="not defined")
        ctk.CTkComboBox(input_grid, variable=self.filetype_var, values=FILE_TYPES, height=28).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        ctk.CTkLabel(input_grid, text="Move to:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=2)
        dest_frame = ctk.CTkFrame(input_grid, fg_color="transparent")
        dest_frame.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        self.dest_var = tk.StringVar(value=DEST_PLACEHOLDER)
        ctk.CTkEntry(dest_frame, textvariable=self.dest_var, state="readonly", height=28).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dest_frame, text="...", width=30, height=28, fg_color="#7f8c8d", command=self._browse).pack(side="right")

        self.pack(fill="x", padx=10, pady=5)

    def _browse(self):
        folder = filedialog.askdirectory()
        if folder: self.dest_var.set(folder)

    def get_data(self):
        return {"filename": self.filename_var.get().strip(), "filetype": self.filetype_var.get(), "destination": self.dest_var.get()}

    def set_data(self, data):
        self.filename_var.set(data.get("filename", ""))
        self.filetype_var.set(data.get("filetype", "not defined"))
        self.dest_var.set(data.get("destination", DEST_PLACEHOLDER))

class FileSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Explorer Manager v1.1")
        self.geometry("750x700")
        self.configure(fg_color="#f5f6fa")
        
        self.watch_folders = []
        self.active_folders = set()
        self.rule_rows = []
        self._watcher_stops = []
        
        self._apply_window_icon()
        self._build_ui()
        self._load()

    def _apply_window_icon(self):
        """Put the Explorer Manager logo in the title bar and the taskbar."""
        if ICON_FILE.exists():
            try:
                self.iconbitmap(str(ICON_FILE))
                # CustomTkinter redraws the title bar shortly after start-up,
                # which drops the icon again - so set it a second time.
                self.after(250, self._reapply_window_icon)
                return
            except tk.TclError:
                pass
        if ICON_PNG.exists():
            try:
                self._icon_image = tk.PhotoImage(file=str(ICON_PNG))
                self.iconphoto(True, self._icon_image)
            except tk.TclError:
                pass

    def _reapply_window_icon(self):
        try:
            self.iconbitmap(str(ICON_FILE))
        except tk.TclError:
            pass

    def _load_logo(self, size=(38, 34)):
        """The website mark as a CTkImage, or None if it cannot be loaded."""
        if not LOGO_FILE.exists():
            return None
        try:
            from PIL import Image
            return ctk.CTkImage(Image.open(LOGO_FILE), size=size)
        except Exception:
            return None

    def _build_ui(self):
        ctk.set_appearance_mode("light")
        
        # Header
        header = ctk.CTkFrame(self, fg_color="#2980b9", height=70, corner_radius=0)
        header.pack(fill="x")
        logo = self._load_logo()
        if logo:
            ctk.CTkLabel(header, image=logo, text="").pack(side="left", padx=(22, 12))
        ctk.CTkLabel(header, text="EXPLORER MANAGER", text_color="white", font=("Segoe UI", 22, "bold")).pack(side="left", padx=(0 if logo else 25, 25))
        
        # Watch Folders
        wf_box = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#dcdde1")
        wf_box.pack(fill="x", padx=20, pady=15)
        
        wf_header = ctk.CTkFrame(wf_box, fg_color="transparent")
        wf_header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(wf_header, text="Source Folders (to watch)", font=("Segoe UI", 14, "bold")).pack(side="left")
        ctk.CTkButton(wf_header, text="+ Add Source", width=100, height=28, fg_color="#27ae60", hover_color="#2ecc71", command=self._add_watch_folder).pack(side="right")
        
        self.watch_list_frame = ctk.CTkFrame(wf_box, fg_color="transparent")
        self.watch_list_frame.pack(fill="x", padx=5, pady=(0, 10))

        # Rules Scroll Area
        rules_container = ctk.CTkFrame(self, fg_color="transparent")
        rules_container.pack(fill="both", expand=True, padx=20)
        rules_header = ctk.CTkFrame(rules_container, fg_color="transparent")
        rules_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(rules_header, text="Automation Rules", font=("Segoe UI", 14, "bold"), anchor="w").pack(side="left")
        ctk.CTkButton(rules_header, text="Clear all", width=80, height=24, fg_color="transparent", text_color="#eb4d4b", hover_color="#e8eaf0", border_width=1, border_color="#eb4d4b", command=self._clear_rules).pack(side="right")
        
        self.rules_scroll = ctk.CTkScrollableFrame(rules_container, fg_color="#ffffff", border_width=1, border_color="#dcdde1", corner_radius=10)
        self.rules_scroll.pack(fill="both", expand=True)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="#ffffff", height=60, corner_radius=0, border_width=1, border_color="#dcdde1")
        footer.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(footer, text="● System Ready", text_color="#27ae60", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side="left", padx=25)
        
        ctk.CTkButton(footer, text="Save & Restart", fg_color="#2980b9", width=140, command=self._save).pack(side="right", padx=20)
        ctk.CTkButton(footer, text="Autostart ON", fg_color="#f1f2f6", text_color="#2f3640", border_width=1, border_color="#dcdde1", width=120, command=self._enable_autostart).pack(side="right")
        
        ctk.CTkButton(self, text="+ Create New Rule", font=("Segoe UI", 13, "bold"), fg_color="#2980b9", height=40, command=self._add_rule).pack(fill="x", padx=30, pady=15)

    def _add_watch_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.watch_folders:
            self.watch_folders.append(folder)
            self.active_folders.add(folder)
            self._update_wf_ui()

    def _enable_autostart(self):
        if toggle_autostart(True):
            messagebox.showinfo("Autostart", "Program will now start with Windows (minimized).")

    def _add_rule(self, data=None):
        row = RuleRow(self.rules_scroll, on_delete=lambda: self._remove_rule(row), rule_number=len(self.rule_rows)+1)
        if data: row.set_data(data)
        self.rule_rows.append(row)

    def _remove_rule(self, row):
        row.destroy()
        self.rule_rows.remove(row)
        for i, r in enumerate(self.rule_rows, 1): r.label.configure(text=f"RULE {i}")

    def _clear_rules(self):
        """Throw away every rule - the way back to a clean, empty setup."""
        if not self.rule_rows:
            return
        if not messagebox.askyesno("Clear all rules", f"Delete all {len(self.rule_rows)} rules? This cannot be undone."):
            return
        for row in self.rule_rows: row.destroy()
        self.rule_rows.clear()
        save_settings([], self.watch_folders)
        self._restart_watchers()

    def _update_wf_ui(self):
        for w in self.watch_list_frame.winfo_children(): w.destroy()
        for f in self.watch_folders:
            WatchFolderRow(self.watch_list_frame, f, self._on_toggle_wf, self._on_delete_wf)

    def _on_toggle_wf(self, path, active):
        if active: self.active_folders.add(path)
        else: self.active_folders.discard(path)

    def _on_delete_wf(self, path):
        self.watch_folders.remove(path)
        self.active_folders.discard(path)
        self._update_wf_ui()

    def _save(self):
        rules = [r.get_data() for r in self.rule_rows]
        usable = clean_rules(rules)
        save_settings(usable, self.watch_folders)
        self._restart_watchers()
        message = "Settings saved and Watchers restarted!"
        unfinished = len(rules) - len(usable)
        if unfinished:
            message += (f"\n\n{unfinished} rule(s) without a destination folder were "
                        "skipped. Pick a destination for them or remove them.")
        messagebox.showinfo("Success", message)

    def _load(self):
        data = load_settings()
        self.watch_folders = data.get("watch_folders", [])
        self.active_folders = set(self.watch_folders)
        self._update_wf_ui()
        for r in data.get("rules", []): self._add_rule(r)
        self._restart_watchers()

    def _restart_watchers(self):
        for s in self._watcher_stops: s.set()
        self._watcher_stops.clear()
        rules = clean_rules([r.get_data() for r in self.rule_rows])
        for folder in self.active_folders:
            if Path(folder).exists():
                stop_event = threading.Event()
                self._watcher_stops.append(stop_event)
                threading.Thread(target=start_watcher, args=(folder, rules, stop_event), daemon=True).start()
        self.status_label.configure(text=f"● Monitoring {len(self.active_folders)} Folders")

if __name__ == "__main__":
    app = FileSorterApp()
    if "--silent" in sys.argv:
        app.withdraw()
    app.mainloop()