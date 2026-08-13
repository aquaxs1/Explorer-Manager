# Explorer Manager — Website

Static landing page for Explorer Manager. No build step, no dependencies — plain HTML, CSS and one small JS file.

```
site/
├── index.html        # landing page (install command, features, how it works)
├── terms.html        # Terms of Use
├── rights.html       # Rights & License
└── assets/
    ├── mark.svg      # logo icon (also used as favicon)
    ├── logo.svg      # logo icon + wordmark
    ├── styles.css    # all styling
    └── main.js       # copy button, install tabs, scroll reveal
```

## Preview locally

```bash
cd site
python -m http.server 8000
```

Then open <http://localhost:8000>.

## Publish with GitHub Pages

1. Repository → **Settings** → **Pages**
2. Source: *Deploy from a branch*
3. Branch: `main`, folder: `/site` → **Save**

The page goes live at `https://aquaxs1.github.io/Explorer-Manager/` a minute later.

## Updating the download link

The install command and the download buttons point at the release asset:

```
https://github.com/aquaxs1/Explorer-Manager/releases/download/manager/ExplorerManager-v1.1.exe
```

When you publish a new release, update that URL (and the version labels) in
`index.html` — it appears in the install command and in the bottom call-to-action.
