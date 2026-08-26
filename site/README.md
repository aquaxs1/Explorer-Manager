# Explorer Manager — Website

Static landing page for Explorer Manager. No build step, no dependencies — plain HTML, CSS and one small JS file.

```
site/
├── index.html        # landing page (download, features, how it works)
├── terms.html        # Terms of Use
├── rights.html       # Rights & License
└── assets/
    ├── mark.svg      # logo icon (also used as favicon)
    ├── logo.svg      # logo icon + wordmark
    ├── styles.css    # all styling
    └── main.js       # copy buttons, scroll reveal
```

## Preview locally

```bash
cd site
python -m http.server 8000
```

Then open <http://localhost:8000>.

## Publish with Vercel

Either option works — pick one:

**A · Root Directory = `Explorer-Manager (root)`** (nothing to configure)
The `vercel.json` in the repository root sets `"outputDirectory": "site"`, so Vercel
serves this folder automatically. Framework Preset: **Other**, no build command.

**B · Root Directory = `site`**
In the import dialog, open *Root Directory* → **Edit**, select the `site` folder and
confirm. Vercel then serves the folder directly as a static site.

In both cases `index.html` is the entry point — there is no build step.
Deployments track the `main` branch, so the `site/` folder has to be merged into
`main` for a deployment to show anything.

## Publish with GitHub Pages

1. Repository → **Settings** → **Pages**
2. Source: *Deploy from a branch*
3. Branch: `main`, folder: `/site` → **Save**

The page goes live at `https://aquaxs1.github.io/Explorer-Manager/` a minute later.

## Updating the download link

The hero button, the download card, the PowerShell one-liner and the bottom
call-to-action all point at one release asset:

```
https://github.com/aquaxs1/Explorer-Manager/releases/download/v1.2/ExplorerManager-v1.2.exe
```

That file is built by [`.github/workflows/release.yml`](../.github/workflows/release.yml):
bump `version.py`, push a matching tag (`git tag v1.3 && git push origin v1.3`)
and the workflow builds `ExplorerManager-v1.3.exe` and attaches it to the
release. Then update the site:

1. the four `releases/download/...` links in `index.html`
2. the version labels — the hero badge, the file name on the download card,
   the button in the bottom call-to-action and the footer line
3. the version badge in the repository `README.md`

A quick search for `v1.2` in `site/index.html` finds every one of them.
