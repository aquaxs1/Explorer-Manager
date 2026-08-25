"""
help_texts.py - the in-app user manual.

Kept as a plain string so main.py can show it without pulling in a
documentation dependency. The labels below must match the ones in main.py; if
you rename a button there, rename it here too.
"""

HELP_TEXT = """USER MANUAL - Explorer Manager
══════════════════════════════════

WHAT DOES THIS PROGRAM DO?
Explorer Manager watches the folders you choose and automatically moves
newly arriving files into the destinations you define - and keeps doing it
in the background after you close the window.


SETUP
─────

1. ADD A SOURCE FOLDER
   Click "+ Add Source" and pick a folder to watch, for example your
   Downloads folder. Add as many as you like; the checkbox next to each one
   turns it on and off without deleting it.

2. CREATE RULES
   Click "+ Create New Rule" for each sorting rule:

   • Filename contains
     Part of a filename, for example "Invoice" to catch every file with
     "Invoice" in its name. Leave it empty to match any filename.

   • File Type
     A file extension from the list. "not defined" matches any extension.

   • Move to
     Click "..." and choose the destination folder.

3. SAVE
   Click "Save & Restart". Your rules are written to settings.json and the
   watchers restart immediately.

4. AUTOSTART (OPTIONAL)
   Click "Autostart ON" to register Explorer Manager with Windows. It then
   starts hidden on boot and sorts without ever showing a window.


HOW RULES ARE APPLIED
─────────────────────
Rules are checked from top to bottom and the first match wins - the file is
moved and the remaining rules are skipped. Order them from most specific to
most general.

The status line at the bottom shows what is happening:
  ● System Ready          - no folder is being watched yet
  ● Monitoring N Folders  - N sources are active


TROUBLESHOOTING
───────────────
• A file was not moved
  → Check that the destination folder still exists.
  → Check that the filename and extension really match the rule.
  → An earlier, broader rule may have claimed the file first.
  → Look at the console output for log messages.

• Two files with the same name
  → Nothing is ever overwritten. A number is appended instead,
    for example Invoice_1.pdf.

• Files appear and vanish again
  → That is the point: they were moved to their destination. The log line
    tells you where.


WHERE YOUR SETTINGS LIVE
────────────────────────
%APPDATA%\\ExplorerManager\\settings.json - plain JSON, safe to back up or
edit by hand while the program is closed.
"""

# Kept for backwards compatibility with older callers that expected a dict.
HELP_TEXTS = {"en": HELP_TEXT}
