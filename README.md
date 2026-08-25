<div align="center">

<img src="site/assets/mark.svg" width="96" alt="Explorer Manager">

# Explorer Manager

**Your files sort themselves.**

Real-time folder automation for Windows. Explorer Manager watches the folders
you choose and moves every new file where it belongs — by filename and file
type — and keeps doing it silently after you close the window.

[![Website](https://img.shields.io/badge/website-explorer--manager.vercel.app-2C7BE5)](https://explorer-manager.vercel.app)
[![Download](https://img.shields.io/badge/download-v1.1%20·%2013%20MB-27ae60)](https://github.com/aquaxs1/Explorer-Manager/releases/latest)
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
- **Rules that stack** — match on a filename keyword, a file extension, or
  both. Rules run top to bottom and the first match wins.
- **Many folders at once** — watch Downloads, Desktop and a network share in
  parallel. Toggle each source on or off without deleting it.
- **Silent autostart** — one click registers Explorer Manager with Windows.
  It boots hidden and sorts without ever showing a window.
- **40+ file types** — documents, archives, media, images, code and
  installers are preselected, or leave the type open to match everything.
- **Nothing is ever overwritten** — name collisions get a number appended.
- **Catches drag & drop and renames**, not just freshly created files.
- **No cloud, no subscription, no telemetry.** Your rules live in a local
  JSON file.

---

## Install

### Ready-to-run executable

No Python required. Open PowerShell, paste, press Enter — the app downloads
to your desktop and starts right away:

```powershell
irm https://github.com/aquaxs1/Explorer-Manager/releases/download/manager/ExplorerManager-v1.1.exe -OutFile "$env:USERPROFILE\Desktop\ExplorerManager.exe"; & "$env:USERPROFILE\Desktop\ExplorerManager.exe"
```

Or [download it from the release page](https://github.com/aquaxs1/Explorer-Manager/releases/latest).

### From source

Needs Python 3.10+ and git on your PATH:

```bash
git clone https://github.com/aquaxs1/Explorer-Manager.git
cd Explorer-Manager
pip install watchdog customtkinter
python main.py
```

---

## Usage

1. **Add a source** — click `+ Add Source` and pick the folder to watch.
2. **Create a rule** — click `+ Create New Rule`, then set a filename
   keyword, a file type, or both, and choose the destination.
3. **Save** — `Save & Restart` stores your rules and restarts the watchers
   immediately.
4. **Turn on autostart** — `Autostart ON` so it launches hidden with Windows.

The status line shows `● System Ready` until a folder is active, then
`● Monitoring N Folders`.

> **Rule order matters.** Rules are checked top to bottom and the first match
> wins. Put specific rules above general ones — a rule with an empty filename
> and no file type matches everything and will claim every file below it.

---

## How it works

| File | Role |
|---|---|
| `main.py` | The CustomTkinter GUI, autostart registration, settings I/O |
| `watcher.py` | The watchdog observer — matching and moving happens here |
| `help_texts.py` | The in-app user manual |

Settings live in `%APPDATA%\ExplorerManager\settings.json` as plain JSON.
Safe to back up, and safe to edit by hand while the program is closed.

---

## Links

- **Website** — <https://explorer-manager.vercel.app>
- **Terms of Use** — <https://explorer-manager.vercel.app/terms.html>
- **Rights & License** — <https://explorer-manager.vercel.app/rights.html>
- **Report an issue** — <https://github.com/aquaxs1/Explorer-Manager/issues>

Free for personal, non-commercial use. See [LICENSE.md](LICENSE.md).
