"""
help_texts.py – Bedienungsanleitung in mehreren Sprachen.
"""

HELP_TEXTS = {
    "de": """BEDIENUNGSANLEITUNG – Explorer Manager
══════════════════════════════════

WAS MACHT DIESES PROGRAMM?
Explorer Manager überwacht einen Ordner deiner Wahl und verschiebt
neu eintreffende Dateien automatisch in definierte Zielordner –
auch wenn das Programmfenster geschlossen ist.


SO RICHTEST DU ES EIN
──────────────────────

1. ÜBERWACHTEN ORDNER WÄHLEN
   Klicke oben auf „Ordner wählen" und wähle den Ordner,
   der überwacht werden soll (z. B. Downloads).

2. REGELN ERSTELLEN
   Klicke auf „+ Regel hinzufügen" für jede Sortiervorgabe:

   • Filename:
     Gib einen Teil des Dateinamens ein.
     Beispiel: „Rechnung" → sortiert alle Dateien mit
     „Rechnung" im Namen.
     Leer lassen = gilt für alle Dateinamen.

   • File Type:
     Wähle eine Dateiendung aus der Liste.
     Beispiel: „.pdf" → nur PDF-Dateien werden sortiert.
     „not defined" = egal welche Endung.

   • Sorted to:
     Klicke auf „Durchsuchen" und wähle den Ordner,
     in den die Dateien verschoben werden sollen.

3. SPEICHERN
   Klicke auf „💾 Speichern". Die Regeln werden in
   settings.json gespeichert und beim nächsten Start
   automatisch geladen.


HINTERGRUNDPROZESS
──────────────────
Der Wächter läuft im Hintergrund. Du siehst unten links:
  ● grün = Wächter aktiv und überwacht den Ordner
  ○ grau  = kein Ordner gewählt

Die Regeln werden der Reihe nach geprüft.
Die erste passende Regel gewinnt – danach wird die
nächste Datei abgewartet.


AUTOSTART (WINDOWS)
────────────────────
Um Explorer Manager automatisch beim Windows-Start zu laden:
1. Drücke Win + R, tippe: shell:startup
2. Lege dort eine Verknüpfung zu main.py (oder .exe) ab.


FEHLERBEHEBUNG
──────────────
• Datei wird nicht verschoben?
  → Prüfe ob der Zielordner existiert.
  → Prüfe ob Dateiname / Endung zur Regel passt.
  → Schaue in die Konsole für Log-Meldungen.

• Namenskonflikt?
  → Bei doppelten Dateinamen wird automatisch eine
    Nummer angehängt (z. B. Datei_1.pdf).
""",

    "en": """USER MANUAL – Explorer Manager
══════════════════════════════════

WHAT DOES THIS PROGRAM DO?
Explorer Manager watches a folder of your choice and automatically
moves newly arriving files into defined destination folders –
even when the program window is closed.


SETUP
──────────────────────

1. CHOOSE WATCH FOLDER
   Click "Ordner wählen" (Choose folder) and select the
   folder to watch (e.g. Downloads).

2. CREATE RULES
   Click "+ Regel hinzufügen" (Add rule) for each sorting rule:

   • Filename:
     Enter part of a filename.
     Example: "Invoice" → sorts all files containing
     "Invoice" in their name.
     Leave empty = matches all filenames.

   • File Type:
     Choose a file extension from the list.
     Example: ".pdf" → only PDF files are sorted.
     "not defined" = any extension.

   • Sorted to:
     Click "Durchsuchen" (Browse) and choose the
     destination folder.

3. SAVE
   Click "💾 Speichern" (Save). Rules are stored in
   settings.json and loaded automatically on next start.


BACKGROUND PROCESS
──────────────────
The watcher runs silently in the background. Status (bottom left):
  ● green = watcher active, monitoring the folder
  ○ grey  = no folder selected

Rules are checked in order. The first matching rule wins.


AUTOSTART (WINDOWS)
────────────────────
To start Explorer Manager automatically with Windows:
1. Press Win + R, type: shell:startup
2. Place a shortcut to main.py (or .exe) there.


TROUBLESHOOTING
────────────────
• File not moved?
  → Check that the destination folder exists.
  → Check that filename / extension matches the rule.
  → Look at the console for log messages.

• Name conflict?
  → Duplicate filenames get a number appended automatically
    (e.g. File_1.pdf).
""",

    "fr": """MANUEL D'UTILISATION – Explorer Manager
══════════════════════════════════

QUE FAIT CE PROGRAMME ?
Explorer Manager surveille un dossier et déplace automatiquement
les nouveaux fichiers vers des dossiers cibles définis –
même lorsque la fenêtre du programme est fermée.


CONFIGURATION
──────────────

1. CHOISIR LE DOSSIER À SURVEILLER
   Cliquez sur « Ordner wählen » et sélectionnez le
   dossier à surveiller (ex. Téléchargements).

2. CRÉER DES RÈGLES
   Cliquez sur « + Regel hinzufügen » pour chaque règle :

   • Filename : Entrez une partie du nom de fichier.
     Exemple : « Facture » → trie tous les fichiers
     contenant « Facture » dans leur nom.
     Vide = s'applique à tous les noms.

   • File Type : Choisissez une extension.
     « not defined » = n'importe quelle extension.

   • Sorted to : Cliquez sur « Durchsuchen »
     et choisissez le dossier de destination.

3. SAUVEGARDER
   Cliquez sur « 💾 Speichern ». Les règles sont
   stockées dans settings.json.


PROCESSUS EN ARRIÈRE-PLAN
──────────────────────────
Le veilleur tourne silencieusement. Statut (en bas à gauche) :
  ● vert = actif, surveillance en cours
  ○ gris  = aucun dossier sélectionné
""",

    "es": """MANUAL DE USUARIO – Explorer Manager
══════════════════════════════════

¿QUÉ HACE ESTE PROGRAMA?
Explorer Manager vigila una carpeta y mueve automáticamente los
archivos nuevos a carpetas de destino definidas, incluso
cuando la ventana del programa está cerrada.


CONFIGURACIÓN
──────────────

1. ELEGIR CARPETA A VIGILAR
   Haz clic en « Ordner wählen » y selecciona la carpeta
   que deseas vigilar (p. ej. Descargas).

2. CREAR REGLAS
   Haz clic en « + Regel hinzufügen » para cada regla:

   • Filename: Escribe parte del nombre del archivo.
     Vacío = se aplica a todos los nombres.

   • File Type: Elige una extensión de la lista.
     « not defined » = cualquier extensión.

   • Sorted to: Haz clic en « Durchsuchen » y elige
     la carpeta de destino.

3. GUARDAR
   Haz clic en « 💾 Speichern ». Las reglas se guardan
   en settings.json y se cargan automáticamente.


PROCESO EN SEGUNDO PLANO
─────────────────────────
El vigilante se ejecuta silenciosamente. Estado (abajo a la izquierda):
  ● verde = activo, vigilando la carpeta
  ○ gris   = ninguna carpeta seleccionada
""",

    "it": """MANUALE UTENTE – Explorer Manager
══════════════════════════════════

COSA FA QUESTO PROGRAMMA?
Explorer Manager monitora una cartella e sposta automaticamente
i nuovi file in cartelle di destinazione definite, anche
quando la finestra del programma è chiusa.


CONFIGURAZIONE
──────────────

1. SCEGLIERE LA CARTELLA DA MONITORARE
   Clicca su « Ordner wählen » e seleziona la cartella
   da monitorare (es. Download).

2. CREARE REGOLE
   Clicca su « + Regel hinzufügen » per ogni regola:

   • Filename: Inserisci parte del nome del file.
     Vuoto = si applica a tutti i nomi.

   • File Type: Scegli un'estensione dall'elenco.
     « not defined » = qualsiasi estensione.

   • Sorted to: Clicca su « Durchsuchen » e scegli
     la cartella di destinazione.

3. SALVARE
   Clicca su « 💾 Speichern ». Le regole vengono
   salvate in settings.json.


PROCESSO IN BACKGROUND
───────────────────────
Il guardiano gira silenziosamente. Stato (in basso a sinistra):
  ● verde = attivo, cartella monitorata
  ○ grigio = nessuna cartella selezionata
""",

    "pl": """INSTRUKCJA OBSŁUGI – Explorer Manager
══════════════════════════════════

CO ROBI TEN PROGRAM?
Explorer Manager obserwuje wybrany folder i automatycznie
przenosi nowe pliki do zdefiniowanych folderów docelowych –
nawet gdy okno programu jest zamknięte.


KONFIGURACJA
─────────────

1. WYBIERZ FOLDER DO OBSERWACJI
   Kliknij „Ordner wählen" i wybierz folder
   (np. Pobrane).

2. UTWÓRZ REGUŁY
   Kliknij „+ Regel hinzufügen" dla każdej reguły:

   • Filename: Wpisz część nazwy pliku.
     Puste = dotyczy wszystkich plików.

   • File Type: Wybierz rozszerzenie z listy.
     „not defined" = dowolne rozszerzenie.

   • Sorted to: Kliknij „Durchsuchen" i wybierz
     folder docelowy.

3. ZAPISZ
   Kliknij „💾 Speichern". Reguły są zapisywane
   w pliku settings.json.
""",

    "ja": """ユーザーマニュアル – Explorer Manager
══════════════════════════════════

このプログラムの機能
Explorer Managerは指定したフォルダを監視し、新しく追加された
ファイルを自動的に定義済みの宛先フォルダに移動します。
ウィンドウが閉じていても動作し続けます。


設定方法
─────────

1. 監視フォルダの選択
   「Ordner wählen」をクリックして監視するフォルダ
   （例：ダウンロード）を選択してください。

2. ルールの作成
   「+ Regel hinzufügen」をクリックして各ルールを追加：

   • Filename: ファイル名の一部を入力します。
     空白 = すべてのファイル名に適用。

   • File Type: リストから拡張子を選択します。
     「not defined」= 任意の拡張子。

   • Sorted to: 「Durchsuchen」をクリックして
     移動先フォルダを選択します。

3. 保存
   「💾 Speichern」をクリック。ルールはsettings.jsonに
   保存され、次回起動時に自動で読み込まれます。


バックグラウンドプロセス
────────────────────────
監視はバックグラウンドで実行されます。ステータス（左下）：
  ● 緑 = アクティブ、フォルダを監視中
  ○ グレー = フォルダ未選択
""",
}