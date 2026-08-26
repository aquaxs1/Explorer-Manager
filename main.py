"""
Explorer Manager - real-time folder automation for Windows.

The GUI: source folders, rules, autostart, tray icon. The sorting itself lives
in watcher.py, everything that is written to disk in settings.py.

BY SEBASTIAN/AQUAXS - All rights reserved
"""

import logging
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

import settings as store
from version import __version__

try:
    import winreg as reg
except ImportError:  # not Windows - autostart is simply unavailable
    reg = None

try:
    from PIL import Image
except ImportError:  # no logo and no tray icon, the app still runs
    Image = None

try:
    import pystray
except Exception:  # not installed, or no usable tray backend on this desktop
    # Closing the window then asks before quitting instead of hiding the app.
    pystray = None

try:
    from help_texts import HELP_TEXT
except ImportError:
    HELP_TEXT = "The user manual (help_texts.py) is missing from this build."

WATCHER_IMPORT_ERROR = None
try:
    from watcher import sort_existing, start_watcher
except ImportError as error:  # watchdog missing - report it instead of crashing later
    WATCHER_IMPORT_ERROR = error
    sort_existing = start_watcher = None

ICON_FILE = store.resource_path("assets", "icon.ico")   # title bar / taskbar on Windows
ICON_PNG = store.resource_path("assets", "icon.png")    # tray icon and iconphoto() fallback
LOGO_FILE = store.resource_path("assets", "logo.png")   # the mark shown in the header

APP_NAME = "ExplorerManager"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

FILE_TYPES = [
    "not defined",
    ".exe", ".jar", ".pdf", ".txt", ".zip", ".rar", ".7z",
    ".docx", ".xlsx", ".pptx", ".doc", ".xls",
    ".mp3", ".mp4", ".wav", ".mkv", ".avi",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".csv", ".json", ".xml", ".html", ".py", ".js", ".ts",
    ".iso", ".dmg", ".apk", ".deb", ".rpm",
]

log = logging.getLogger(__name__)


# ----------------------------------------------------------------- autostart

def autostart_command():
    """The command Windows should run at logon."""
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable)}" --silent'
    # From source: pythonw.exe keeps the console window away.
    interpreter = Path(sys.executable)
    windowless = interpreter.with_name("pythonw.exe")
    if windowless.exists():
        interpreter = windowless
    return f'"{interpreter}" "{Path(__file__).resolve()}" --silent'


def autostart_enabled():
    """True if Explorer Manager is registered to start with Windows."""
    if reg is None:
        return False
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY, 0, reg.KEY_READ) as key:
            reg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def set_autostart(enable):
    """Register or unregister the app. Returns True on success."""
    if reg is None:
        return False
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY, 0, reg.KEY_ALL_ACCESS) as key:
            if enable:
                reg.SetValueEx(key, APP_NAME, 0, reg.REG_SZ, autostart_command())
            else:
                try:
                    reg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError as error:
        log.error("Autostart could not be changed: %s", error)
        return False


def open_in_explorer(path):
    """Show a file or folder in the system file manager."""
    path = Path(path)
    try:
        if hasattr(os, "startfile"):
            os.startfile(str(path))  # noqa: S606 - Windows only
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except OSError as error:
        log.error("Could not open %s: %s", path, error)
        return False


# ----------------------------------------------------------------- GUI parts

def shorten_path(path, limit=58):
    """Keep the end of a long path visible - that is where the folder name is."""
    path = str(path)
    return path if len(path) <= limit else "..." + path[-(limit - 3):]


class WatchFolderRow(ctk.CTkFrame):
    """One source folder: on/off, path, subfolders, delete."""

    def __init__(self, parent, folder, on_change, on_delete, **kwargs):
        super().__init__(parent, fg_color="#ffffff", border_width=1,
                         border_color="#e0e0e0", corner_radius=6, **kwargs)
        self.folder = folder

        self.active_var = tk.BooleanVar(value=folder["active"])
        ctk.CTkCheckBox(self, text="", variable=self.active_var, width=20,
                        command=self._changed).pack(side="left", padx=(10, 6))

        # The buttons on the right claim their width first, so a long path
        # shortens instead of pushing them out of the row.
        ctk.CTkButton(self, text="Delete", width=60, height=24, fg_color="#eb4d4b",
                      hover_color="#ff7979",
                      command=lambda: on_delete(folder["path"])).pack(side="right", padx=10)

        self.recursive_var = tk.BooleanVar(value=folder["recursive"])
        ctk.CTkCheckBox(self, text="Subfolders", variable=self.recursive_var,
                        font=("Segoe UI", 11), checkbox_width=18, checkbox_height=18,
                        command=self._changed).pack(side="right", padx=10)

        ctk.CTkLabel(self, text=shorten_path(folder["path"]), font=("Segoe UI", 11),
                     text_color="#333333", anchor="w").pack(side="left", fill="x",
                                                            expand=True, padx=5)

        self.on_change = on_change
        self.pack(fill="x", padx=10, pady=2)

    def _changed(self):
        self.folder["active"] = self.active_var.get()
        self.folder["recursive"] = self.recursive_var.get()
        self.on_change()


class RuleRow(ctk.CTkFrame):
    """One automation rule: on/off, filters, destination, order."""

    def __init__(self, parent, on_delete, on_move, **kwargs):
        super().__init__(parent, fg_color="#fcfcfc", border_width=1,
                         border_color="#dcdde1", corner_radius=8, **kwargs)

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(5, 0))

        self.enabled_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(top_row, text="", variable=self.enabled_var, width=20,
                        command=self._refresh_state).pack(side="left")
        self.label = ctk.CTkLabel(top_row, text="RULE 1", font=("Segoe UI", 12, "bold"),
                                  text_color="#2f3640")
        self.label.pack(side="left", padx=(4, 0))

        ctk.CTkButton(top_row, text="Remove", width=70, height=22, fg_color="transparent",
                      text_color="#eb4d4b", hover_color="#f5f6fa", border_width=1,
                      border_color="#eb4d4b", command=on_delete).pack(side="right")
        ctk.CTkButton(top_row, text="▼", width=28, height=22, fg_color="transparent",
                      text_color="#2f3640", hover_color="#f5f6fa", border_width=1,
                      border_color="#dcdde1",
                      command=lambda: on_move(self, 1)).pack(side="right", padx=(4, 8))
        ctk.CTkButton(top_row, text="▲", width=28, height=22, fg_color="transparent",
                      text_color="#2f3640", hover_color="#f5f6fa", border_width=1,
                      border_color="#dcdde1",
                      command=lambda: on_move(self, -1)).pack(side="right")

        input_grid = ctk.CTkFrame(self, fg_color="transparent")
        input_grid.pack(fill="x", padx=10, pady=10)
        input_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_grid, text="Filename contains:",
                     font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=2)
        self.filename_var = tk.StringVar()
        ctk.CTkEntry(input_grid, textvariable=self.filename_var, placeholder_text="e.g. Invoice",
                     height=28).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        ctk.CTkLabel(input_grid, text="File Type:",
                     font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=2)
        self.filetype_var = tk.StringVar(value="not defined")
        ctk.CTkComboBox(input_grid, variable=self.filetype_var, values=FILE_TYPES,
                        height=28).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        ctk.CTkLabel(input_grid, text="Move to:",
                     font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=2)
        dest_frame = ctk.CTkFrame(input_grid, fg_color="transparent")
        dest_frame.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

        self.dest_var = tk.StringVar(value=store.DEST_PLACEHOLDER)
        ctk.CTkEntry(dest_frame, textvariable=self.dest_var, state="readonly",
                     height=28).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(dest_frame, text="...", width=30, height=28, fg_color="#7f8c8d",
                      command=self._browse).pack(side="right")

        self.pack(fill="x", padx=10, pady=5)

    def _browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_var.set(folder)

    def _refresh_state(self):
        self.label.configure(text_color="#2f3640" if self.enabled_var.get() else "#a4b0be")

    def get_data(self):
        return {
            "filename": self.filename_var.get().strip(),
            "filetype": self.filetype_var.get(),
            "destination": self.dest_var.get(),
            "enabled": self.enabled_var.get(),
        }

    def set_data(self, data):
        self.filename_var.set(data.get("filename", ""))
        self.filetype_var.set(data.get("filetype", "not defined"))
        self.dest_var.set(data.get("destination", store.DEST_PLACEHOLDER))
        self.enabled_var.set(bool(data.get("enabled", True)))
        self._refresh_state()


class FileSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Explorer Manager v{__version__}")
        self.geometry("820x760")
        self.minsize(720, 600)
        self.configure(fg_color="#f5f6fa")

        self.watch_folders = []      # list of {"path", "active", "recursive"}
        self.rule_rows = []
        self._watcher_stops = []
        self.tray_icon = None
        self._sorting = False

        self._apply_window_icon()
        self._build_ui()
        self._load()
        self._start_tray()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------- chrome

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
        if not LOGO_FILE.exists() or Image is None:
            return None
        try:
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
        ctk.CTkLabel(header, text="EXPLORER MANAGER", text_color="white",
                     font=("Segoe UI", 22, "bold")).pack(side="left",
                                                         padx=(0 if logo else 25, 10))
        ctk.CTkLabel(header, text=f"v{__version__}", text_color="#d6eaf8",
                     font=("Segoe UI", 12)).pack(side="left", pady=(6, 0))

        ctk.CTkButton(header, text="?", width=34, height=28, fg_color="#2471a3",
                      hover_color="#1f618d", font=("Segoe UI", 14, "bold"),
                      command=self._show_help).pack(side="right", padx=(6, 22))
        ctk.CTkButton(header, text="Log", width=60, height=28, fg_color="#2471a3",
                      hover_color="#1f618d", command=self._open_log).pack(side="right")

        # Watch Folders
        wf_box = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1,
                              border_color="#dcdde1")
        wf_box.pack(fill="x", padx=20, pady=15)

        wf_header = ctk.CTkFrame(wf_box, fg_color="transparent")
        wf_header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(wf_header, text="Source Folders (to watch)",
                     font=("Segoe UI", 14, "bold")).pack(side="left")
        ctk.CTkButton(wf_header, text="+ Add Source", width=100, height=28,
                      fg_color="#27ae60", hover_color="#2ecc71",
                      command=self._add_watch_folder).pack(side="right")

        # height=0 so the empty container does not reserve CustomTkinter's
        # default frame height while there is no source folder yet.
        self.watch_list_frame = ctk.CTkFrame(wf_box, fg_color="transparent", height=0)
        self.watch_list_frame.pack(fill="x", padx=5, pady=(0, 4))
        self.wf_empty_label = ctk.CTkLabel(wf_box, text="No source folder yet - add one to start.",
                                           font=("Segoe UI", 11), text_color="#7f8c8d")

        # Rules
        rules_container = ctk.CTkFrame(self, fg_color="transparent")
        rules_container.pack(fill="both", expand=True, padx=20)
        rules_header = ctk.CTkFrame(rules_container, fg_color="transparent")
        rules_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(rules_header, text="Automation Rules",
                     font=("Segoe UI", 14, "bold"), anchor="w").pack(side="left")
        ctk.CTkLabel(rules_header, text="checked from top to bottom - the first match wins",
                     font=("Segoe UI", 11), text_color="#7f8c8d").pack(side="left", padx=10)
        ctk.CTkButton(rules_header, text="Clear all", width=80, height=24,
                      fg_color="transparent", text_color="#eb4d4b", hover_color="#e8eaf0",
                      border_width=1, border_color="#eb4d4b",
                      command=self._clear_rules).pack(side="right")

        self.rules_scroll = ctk.CTkScrollableFrame(rules_container, fg_color="#ffffff",
                                                   border_width=1, border_color="#dcdde1",
                                                   corner_radius=10)
        self.rules_scroll.pack(fill="both", expand=True)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="#ffffff", height=60, corner_radius=0,
                              border_width=1, border_color="#dcdde1")
        footer.pack(fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(footer, text="● System Ready", text_color="#27ae60",
                                         font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side="left", padx=25)

        ctk.CTkButton(footer, text="Save & Restart", fg_color="#2980b9", width=130,
                      command=self._save).pack(side="right", padx=(8, 20), pady=12)
        self.autostart_button = ctk.CTkButton(footer, text="Autostart: OFF", fg_color="#f1f2f6",
                                              text_color="#2f3640", border_width=1,
                                              border_color="#dcdde1", width=130,
                                              command=self._toggle_autostart)
        self.autostart_button.pack(side="right", padx=8)
        self.sort_button = ctk.CTkButton(footer, text="Sort existing files", fg_color="#f1f2f6",
                                         text_color="#2f3640", border_width=1,
                                         border_color="#dcdde1", width=140,
                                         command=self._sort_existing)
        self.sort_button.pack(side="right", padx=8)

        ctk.CTkButton(self, text="+ Create New Rule", font=("Segoe UI", 13, "bold"),
                      fg_color="#2980b9", height=40,
                      command=self._add_rule).pack(fill="x", padx=30, pady=15)

        self._refresh_autostart_button()

    # -------------------------------------------------------- source folders

    def _add_watch_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        if any(f["path"] == folder for f in self.watch_folders):
            return
        self.watch_folders.append({"path": folder, "active": True, "recursive": False})
        self._update_wf_ui()
        self._folders_changed()

    def _delete_watch_folder(self, path):
        self.watch_folders = [f for f in self.watch_folders if f["path"] != path]
        self._update_wf_ui()
        self._folders_changed()

    def _folders_changed(self):
        """A source folder was added, removed or toggled - apply it at once."""
        self._persist()
        self._restart_watchers()

    def _update_wf_ui(self):
        for widget in self.watch_list_frame.winfo_children():
            widget.destroy()
        for folder in self.watch_folders:
            WatchFolderRow(self.watch_list_frame, folder, self._folders_changed,
                           self._delete_watch_folder)
        if self.watch_folders:
            self.wf_empty_label.pack_forget()
        else:
            self.wf_empty_label.pack(pady=(0, 12))

    def active_folders(self):
        return [f for f in self.watch_folders if f["active"]]

    # ----------------------------------------------------------------- rules

    def _add_rule(self, data=None):
        row = RuleRow(self.rules_scroll, on_delete=lambda: self._remove_rule(row),
                      on_move=self._move_rule)
        if data:
            row.set_data(data)
        self.rule_rows.append(row)
        self._renumber_rules()

    def _remove_rule(self, row):
        row.destroy()
        self.rule_rows.remove(row)
        self._renumber_rules()

    def _move_rule(self, row, offset):
        """Reorder a rule - the order decides which rule claims a file."""
        index = self.rule_rows.index(row)
        target = index + offset
        if not 0 <= target < len(self.rule_rows):
            return
        self.rule_rows[index], self.rule_rows[target] = self.rule_rows[target], self.rule_rows[index]
        for item in self.rule_rows:
            item.pack_forget()
        for item in self.rule_rows:
            item.pack(fill="x", padx=10, pady=5)
        self._renumber_rules()

    def _renumber_rules(self):
        for number, row in enumerate(self.rule_rows, 1):
            row.label.configure(text=f"RULE {number}")

    def _clear_rules(self):
        """Throw away every rule - the way back to a clean, empty setup."""
        if not self.rule_rows:
            return
        if not messagebox.askyesno("Clear all rules",
                                   f"Delete all {len(self.rule_rows)} rules? This cannot be undone."):
            return
        for row in self.rule_rows:
            row.destroy()
        self.rule_rows.clear()
        self._persist()
        self._restart_watchers()

    def current_rules(self):
        return [row.get_data() for row in self.rule_rows]

    # -------------------------------------------------------------- settings

    def _persist(self):
        """Write the current state to disk. Returns True on success."""
        try:
            store.save_settings(self.current_rules(), self.watch_folders)
            return True
        except OSError as error:
            log.error("Settings could not be saved: %s", error)
            messagebox.showerror("Settings not saved",
                                 f"Could not write {store.settings_file()}:\n{error}")
            return False

    def _save(self):
        rules = self.current_rules()
        usable = store.clean_rules(rules)
        if not self._persist():
            return
        self._restart_watchers()
        message = "Settings saved and watchers restarted."
        unfinished = len(rules) - len(usable)
        if unfinished:
            message += (f"\n\n{unfinished} rule(s) without a destination folder were "
                        "skipped. Pick a destination for them or remove them.")
        messagebox.showinfo("Saved", message)

    def _load(self):
        data = store.load_settings()
        self.watch_folders = data["watch_folders"]
        self._update_wf_ui()
        for rule in data["rules"]:
            self._add_rule(rule)
        self._restart_watchers()

    # -------------------------------------------------------------- watchers

    def _restart_watchers(self):
        for stop_event in self._watcher_stops:
            stop_event.set()
        self._watcher_stops.clear()

        rules = store.active_rules(self.current_rules())
        running = 0
        if start_watcher is not None:
            for folder in self.active_folders():
                if not Path(folder["path"]).exists():
                    log.warning("Source folder is gone: %s", folder["path"])
                    continue
                stop_event = threading.Event()
                self._watcher_stops.append(stop_event)
                threading.Thread(target=start_watcher,
                                 args=(folder["path"], rules, stop_event),
                                 kwargs={"recursive": folder["recursive"]},
                                 daemon=True).start()
                running += 1
        self._update_status(running, len(rules))

    def _refresh_status(self):
        self._update_status(len(self._watcher_stops),
                            len(store.active_rules(self.current_rules())))

    def _update_status(self, folders, rules):
        if folders and rules:
            text, color = f"● Monitoring {folders} folder(s) with {rules} rule(s)", "#27ae60"
        elif folders:
            text, color = f"● Monitoring {folders} folder(s) - no active rule yet", "#e67e22"
        else:
            text, color = "● System Ready - add a source folder", "#e67e22"
        if self.tray_icon:
            text += " · runs in the tray"
        self.status_label.configure(text=text, text_color=color)

    # ------------------------------------------------------------- actions

    def _sort_existing(self):
        """Apply the rules to the files that are already lying around."""
        if self._sorting or sort_existing is None:
            return
        folders = self.active_folders()
        rules = store.active_rules(self.current_rules())
        if not folders or not rules:
            messagebox.showinfo("Nothing to do",
                                "Add at least one active source folder and one active rule first.")
            return
        if not messagebox.askyesno(
                "Sort existing files",
                f"Apply {len(rules)} rule(s) to the files already in "
                f"{len(folders)} source folder(s)?\n\nFiles are moved, not copied."):
            return

        self._sorting = True
        self.sort_button.configure(state="disabled", text="Sorting...")

        def work():
            moved = 0
            for folder in folders:
                moved += sort_existing(folder["path"], rules, recursive=folder["recursive"])
            self.after(0, lambda: self._sort_finished(moved))

        threading.Thread(target=work, daemon=True).start()

    def _sort_finished(self, moved):
        self._sorting = False
        self.sort_button.configure(state="normal", text="Sort existing files")
        messagebox.showinfo("Sorted", f"{moved} file(s) moved.")

    def _toggle_autostart(self):
        if reg is None:
            messagebox.showinfo("Autostart", "Autostart is only available on Windows.")
            return
        enable = not autostart_enabled()
        if not set_autostart(enable):
            messagebox.showerror("Autostart", "The registry entry could not be changed.")
            return
        self._refresh_autostart_button()
        if enable:
            messagebox.showinfo("Autostart", "Explorer Manager now starts with Windows, hidden in the tray.")

    def _refresh_autostart_button(self):
        on = autostart_enabled()
        self.autostart_button.configure(
            text=f"Autostart: {'ON' if on else 'OFF'}",
            fg_color="#27ae60" if on else "#f1f2f6",
            text_color="white" if on else "#2f3640")

    def _open_log(self):
        path = store.log_file()
        if not path.exists():
            messagebox.showinfo("Log", f"No log file yet.\nIt will appear at:\n{path}")
            return
        if not open_in_explorer(path):
            messagebox.showinfo("Log", f"The log file is here:\n{path}")

    def _show_help(self):
        window = ctk.CTkToplevel(self)
        window.title("Explorer Manager - User Manual")
        window.geometry("720x620")
        window.configure(fg_color="#f5f6fa")
        window.transient(self)
        # CustomTkinter creates the toplevel first and styles it a moment later.
        window.after(250, lambda: self._icon_for(window))

        box = ctk.CTkTextbox(window, font=("Consolas", 12), fg_color="white",
                             text_color="#2f3640", wrap="word")
        box.pack(fill="both", expand=True, padx=16, pady=16)
        box.insert("1.0", f"{HELP_TEXT}\n\nSettings file: {store.settings_file()}\n"
                          f"Log file: {store.log_file()}\n")
        box.configure(state="disabled")

        ctk.CTkButton(window, text="Close", width=110,
                      command=window.destroy).pack(pady=(0, 16))
        window.focus()

    def _icon_for(self, window):
        try:
            window.iconbitmap(str(ICON_FILE))
        except tk.TclError:
            pass

    # ----------------------------------------------------------------- tray

    def _start_tray(self):
        """Keep sorting after the window is closed, reachable from the tray."""
        if pystray is None or Image is None or not ICON_PNG.exists():
            return
        try:
            image = Image.open(ICON_PNG)
            menu = pystray.Menu(
                pystray.MenuItem("Open Explorer Manager", self._tray_open, default=True),
                pystray.MenuItem("Sort existing files", self._tray_sort),
                pystray.MenuItem("Quit", self._tray_quit),
            )
            icon = pystray.Icon(APP_NAME, image, "Explorer Manager", menu)
        except Exception as error:  # pragma: no cover - depends on the desktop
            log.warning("No tray icon: %s", error)
            return

        ready = threading.Event()

        def setup(tray):
            tray.visible = True
            ready.set()

        def run():
            try:
                icon.run(setup=setup)
            except Exception as error:  # pragma: no cover - depends on the desktop
                log.warning("Tray icon stopped: %s", error)
                ready.set()

        threading.Thread(target=run, daemon=True).start()
        if ready.wait(3) and getattr(icon, "visible", False):
            self.tray_icon = icon
            self._refresh_status()
        else:
            log.warning("No system tray available - closing the window will quit the app.")
            try:
                icon.stop()
            except Exception:  # pragma: no cover
                pass

    def _tray_open(self, *_):
        self.after(0, self._show_window)

    def _tray_sort(self, *_):
        def show_and_sort():
            self._show_window()
            self._sort_existing()
        self.after(0, show_and_sort)

    def _tray_quit(self, *_):
        self.after(0, self._quit)

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    # ------------------------------------------------------------- shutdown

    def _on_close(self):
        if self.tray_icon:
            self.withdraw()
            log.info("Window hidden - Explorer Manager keeps sorting in the tray.")
            try:
                self.tray_icon.notify("Still running - your folders stay watched.",
                                      "Explorer Manager")
            except Exception:  # not every tray backend can show a balloon
                pass
            return
        if messagebox.askokcancel(
                "Quit Explorer Manager",
                "Closing the window stops the sorting.\n\n"
                "Turn on Autostart to have it running after every logon."):
            self._quit()

    def _quit(self):
        for stop_event in self._watcher_stops:
            stop_event.set()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:  # pragma: no cover
                pass
        self.destroy()


def main():
    store.configure_logging()
    log.info("Explorer Manager v%s starting", __version__)

    app = FileSorterApp()
    if WATCHER_IMPORT_ERROR is not None:
        messagebox.showerror(
            "watchdog is missing",
            "Explorer Manager cannot watch any folder because the 'watchdog' "
            f"package is missing:\n\n{WATCHER_IMPORT_ERROR}\n\n"
            "Install it with:  pip install watchdog")
    if "--silent" in sys.argv:
        app.withdraw()
    app.mainloop()


if __name__ == "__main__":
    main()
