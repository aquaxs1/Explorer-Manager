"""
help_texts.py - the in-app user manual, shown by the "?" button.

Kept as a plain string so main.py can show it without pulling in a
documentation dependency. The labels below must match the ones in main.py; if
you rename a button there, rename it here too.
"""

HELP_TEXT = """USER MANUAL - Explorer Manager
══════════════════════════════════

WHAT DOES THIS PROGRAM DO?
Explorer Manager watches the folders you choose and automatically moves
newly arriving files into the destinations you define. Closing the window
does not stop it: the app keeps running in the notification area next to the
clock and carries on sorting.


SETUP
─────

1. ADD A SOURCE FOLDER
   Click "+ Add Source" and pick a folder to watch, for example your
   Downloads folder. Add as many as you like.

   • The checkbox on the left turns a folder on and off without deleting it.
   • "Subfolders" also watches everything inside that folder.

2. CREATE RULES
   Click "+ Create New Rule" for each sorting rule:

   • Filename contains
     Part of a filename, for example "Invoice" to catch every file with
     "Invoice" in its name. Leave it empty to match any filename.

   • File Type
     A file extension from the list. "not defined" matches any extension.

   • Move to
     Click "..." and choose the destination folder. A rule without a
     destination is never saved and never moves anything.

   The checkbox next to "RULE n" switches a single rule off, and the arrows
   ▲ ▼ move it up and down.

3. SAVE
   Click "Save & Restart". Your rules are written to settings.json and the
   watchers restart immediately.

4. AUTOSTART (OPTIONAL)
   The button shows the current state: "Autostart: OFF" or "Autostart: ON".
   Click it to switch. When it is on, Explorer Manager starts hidden with
   Windows and sorts without ever showing a window.


THE BUTTONS
───────────
+ Add Source          Pick another folder to watch.
+ Create New Rule     Add an empty rule.
Clear all             Delete every rule at once (with a confirmation).
Sort existing files   Apply the rules to the files that are already lying in
                      your source folders. The watcher only sees new
                      arrivals - this is how you clean up the old pile.
Autostart: ON / OFF   Start with Windows, or stop doing so.
Save & Restart        Write the settings and restart the watchers.
Log                   Open the log file, which lists every moved file.
?                     This manual.


HOW RULES ARE APPLIED
─────────────────────
Rules are checked from top to bottom and the first match wins - the file is
moved and the remaining rules are skipped. Order them from most specific to
most general, and use ▲ ▼ to correct the order.

Switched-off rules and rules without a destination are skipped entirely.

The status line at the bottom shows what is happening:
  ● System Ready                        - no source folder yet
  ● Monitoring N folder(s) with M rules  - everything is running


DOWNLOADS AND HALF-WRITTEN FILES
────────────────────────────────
A file is only moved once it has stopped growing, so a large download is
never torn away from the browser mid-transfer. Temporary files such as
.crdownload, .part, .tmp and Office's ~$ files are ignored completely.


THE TRAY ICON
─────────────
Closing the window hides it. The icon next to the clock offers:
  • Open Explorer Manager - bring the window back
  • Sort existing files   - clean up the source folders right now
  • Quit                  - really stop the program

If your desktop has no notification area, the app says so and closing the
window asks whether you want to quit.


TROUBLESHOOTING
───────────────
• A file was not moved
  → Is the rule switched on?
  → Does the filename or extension really match the rule?
  → An earlier, broader rule may have claimed the file first.
  → Open the log with the "Log" button - every move is listed there.

• The destination folder does not exist
  → It is created automatically the first time a file needs it.

• Two files with the same name
  → Nothing is ever overwritten. A number is appended instead,
    for example Invoice_1.pdf.

• Files appear and vanish again
  → That is the point: they were moved to their destination. The log line
    tells you where.


WHERE YOUR FILES LIVE
─────────────────────
%APPDATA%\\ExplorerManager\\settings.json     - your rules, plain JSON,
                                               safe to back up or to edit by
                                               hand while the program is
                                               closed.
%APPDATA%\\ExplorerManager\\explorer-manager.log - what was moved and when.
"""
