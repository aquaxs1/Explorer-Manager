# Explorer Manager 🗂️

Ein automatischer Datei-Sortierer mit GUI und Hintergrundprozess.

## Installation

### 1. Python installieren
Python 3.8+ von https://python.org herunterladen und installieren.

### 2. Abhängigkeiten installieren
```bash
pip install watchdog
```

### 3. Programm starten
```bash
python main.py
```

---

## Dateien

| Datei | Beschreibung |
|---|---|
| `main.py` | Hauptprogramm + GUI |
| `watcher.py` | Hintergrundprozess (Datei-Wächter) |
| `help_texts.py` | Bedienungsanleitung (7 Sprachen) |
| `settings.json` | Automatisch erzeugt beim ersten Speichern |

---

## Autostart unter Windows

Damit Explorer Manager beim Windows-Login automatisch startet:

1. `Win + R` drücken → `shell:startup` eingeben → Enter
2. Eine Verknüpfung zu `main.py` in den geöffneten Ordner legen

**Alternativ als .exe (kein Python nötig):**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
Die fertige `.exe` liegt dann im `dist/`-Ordner.

---

## Wie funktioniert es?

```
[Überwachter Ordner]
        |
    Neue Datei!
        |
   Regel 1 prüfen → passt? → Zielordner 1 ✓
   Regel 2 prüfen → passt? → Zielordner 2 ✓
   ...
        |
   Datei verschieben
```

Regeln werden der Reihe nach geprüft. Die **erste passende Regel** gewinnt.

---

## Unterstützte Sprachen in der Hilfe

🇩🇪 Deutsch · 🇬🇧 English · 🇫🇷 Français · 🇪🇸 Español · 🇮🇹 Italiano · 🇵🇱 Polski · 🇯🇵 日本語