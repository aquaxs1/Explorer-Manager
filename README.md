<div align="center">

<img src="site/assets/mark.svg" width="96" alt="Explorer Manager">

# Explorer Manager

**Your files sort themselves.**

Real-time folder automation for Windows. Explorer Manager watches the folders
you choose and moves every new file where it belongs — by filename and file
type — and keeps doing it from the tray after you close the window.

[![Website](https://img.shields.io/badge/website-explorer--manager.vercel.app-2C7BE5)](https://explorer-manager.vercel.app)
[![Download](https://img.shields.io/badge/download-v1.2-27ae60)](https://github.com/aquaxs1/Explorer-Manager/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6)](https://explorer-manager.vercel.app)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://python.org)
[![License](https://img.shields.io/badge/license-personal%20use-lightgrey)](LICENSE.md)

</div>

---

## Why not just use File Explorer?

File Explorer sorts what is already there. Explorer Manager decides where
things go in the first place.

| | Without | With Explorer Manager |
|---|---|---|
| **New downloads** | Pile up in one folder until you clean up | Filed the moment they arrive |
| **Routing by name** | Not possible — no rule engine | `Invoice` → your invoice folder |
| **Duplicate names** | An overwrite dialog stops everything | Numbered automatically, never overwritten |
| **Scripts / scheduled tasks** | Run on a timer, minutes late | Reacts within a second |

---

## Features

- **Real-time watching** — a file lands in Downloads and is gone within a
  second. Moved, not copied, with no scan schedule.
- **Runs from the tray** — closing the window hides it next to the clock and
  the sorting continues. Open it again, sort on demand, or quit from there.
- **Waits for downloads to finish** — a file is only moved once it has stopped
  growing, and `.crdownload`, `.part`, `.tmp` and Office's `~$` files are
  ignored entirely.
- **Sort existing files** — one button applies your rules to the pile that was
  already lying in the folder, not just to new arrivals.
- **Rules that stack** — match on a filename keyword, a file extension, or
  both. Switch a single rule off, move it up or down; the first match wins.
- **Many folders at once** — watch Downloads, Desktop and a network share in
  parallel, each with its own on/off switch and optional subfolders.
- **Silent autostart** — one click registers Explorer Manager with Windows,
  and the button always shows whether it is on.
- **40+ file types** — documents, archives, media, images, code and
  installers are preselected, or leave the type open to match everything.
- **Nothing is ever overwritten** — name collisions get a number appended,
  and a missing destination folder is created on the spot.
- **A log you can read** — every move is written to a file in `%APPDATA%`,
  which is the only way to see what happened while the app ran silently.
- **No cloud, no subscription, no telemetry.** Your rules live in a local
  JSON file.

---

## Install

### Download the .exe (recommended)

**[Download ExplorerManager-v1.2.exe](https://github.com/aquaxs1/Explorer-Manager/releases/download/v1.2/ExplorerManager-v1.2.exe)**
— one file, no installer, no Python. Save it anywhere and double-click it.
Windows may show a SmartScreen notice for a new publisher: choose
**More info → Run anyway**. All releases are on the
[release page](https://github.com/aquaxs1/Explorer-Manager/releases/latest).

### Download it with PowerShell

Fetches the same .exe to your desktop and starts it right away:

```powershell
irm https://github.com/aquaxs1/Explorer-Manager/releases/download/v1.2/ExplorerManager-v1.2.exe -OutFile "$env:USERPROFILE\Desktop\ExplorerManager.exe"; & "$env:USERPROFILE\Desktop\ExplorerManager.exe"
```

### From source

Needs Python 3.10+ and git on your PATH:

```bash
git clone https://github.com/aquaxs1/Explorer-Manager.git
cd Explorer-Manager
pip install -r requirements.txt
python main.py
```

### Build the .exe yourself

Pushing a `v*` tag builds it on GitHub and attaches it to the release — see
[`.github/workflows/release.yml`](.github/workflows/release.yml). Locally:

```powershell
pip install -r requirements-dev.txt
pyinstaller --noconfirm --onefile --windowed --name ExplorerManager `
            --icon assets\icon.ico --add-data "assets;assets" main.py
```

`--icon` gives the executable the Explorer Manager logo, `--add-data` ships the
same logo for the window, the taskbar and the app header. The build lands in
`dist\ExplorerManager.exe`.

---

## Usage

1. **Add a source** — click `+ Add Source` and pick the folder to watch. The
   checkbox turns it off without deleting it, `Subfolders` includes everything
   inside it.
2. **Create a rule** — click `+ Create New Rule`, then set a filename
   keyword, a file type, or both, and choose the destination.
3. **Save** — `Save & Restart` stores your rules and restarts the watchers
   immediately.
4. **Clean up the backlog** — `Sort existing files` applies the same rules to
   what is already in your source folders.
5. **Turn on autostart** — `Autostart: OFF` → `ON` so it launches hidden with
   Windows.

Closing the window hides Explorer Manager in the tray and it keeps sorting.
Right-click the tray icon to open it again, sort on demand or quit. Without a
notification area the app says so, and closing asks whether you really want to
stop.

The status line shows `● System Ready` until a folder is active, then
`● Monitoring N folder(s) with M rule(s)`. `Log` opens the log file, `?` opens
the manual.

> **Rule order matters.** Rules are checked top to bottom and the first match
> wins. Put specific rules above general ones — a rule with an empty filename
> and no file type matches everything and will claim every file below it. Use
> ▲ ▼ to fix the order.

---

## How it works

| File | Role |
|---|---|
| `main.py` | The CustomTkinter GUI, tray icon, autostart registration |
| `watcher.py` | The watchdog observer — matching, waiting and moving happens here |
| `settings.py` | Everything that is written to disk, plus the logging setup |
| `help_texts.py` | The in-app user manual behind the `?` button |
| `version.py` | The one place the version number lives |
| `assets/` | Window icon and header logo, generated from `site/assets/mark.svg` by `tools/make_icons.py` |
| `tests/` | `pytest` suite for the settings and the sorting — no GUI needed |
| `site/` | The website, deployed to Vercel |

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

Settings live in `%APPDATA%\ExplorerManager\settings.json` as plain JSON, the
log next to it in `explorer-manager.log`. Both are safe to back up, and the
settings are safe to edit by hand while the program is closed. A fresh install
starts with no rules at all; a rule without a destination folder is never saved
and never applied, and `Clear all` next to *Automation Rules* removes every
rule at once.

---

## Links

- **Website** — <https://explorer-manager.vercel.app>
- **Terms of Use** — <https://explorer-manager.vercel.app/terms.html>
- **Rights & License** — <https://explorer-manager.vercel.app/rights.html>
- **Report an issue** — <https://github.com/aquaxs1/Explorer-Manager/issues>

Free for personal, non-commercial use. See [LICENSE.md](LICENSE.md).
