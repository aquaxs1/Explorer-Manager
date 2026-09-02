# Explorer Manager — Website

Static landing page for Explorer Manager. No build step, no dependencies — plain HTML, CSS and one small JS file.

```
site/
├── index.html        # landing page (hero, features, what Windows can't do)
├── download.html     # the download and the command-line alternatives
├── setup.html        # set up in four steps
├── terms.html        # Terms of Use, including Rights & License
├── 404.html
├── vercel.json       # used when Root Directory is set to `site`
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

Nothing to update. Every button points at:

```
https://github.com/aquaxs1/Explorer-Manager/releases/latest/download/ExplorerManager-windows-x64.zip
```

`releases/latest/download/...` is resolved by GitHub to the newest release, and
[`.github/workflows/release.yml`](../.github/workflows/release.yml) always
publishes the archive under that same name. Bump `version.py`, push a matching
tag (`git tag v1.3 && git push origin v1.3`), and the site picks it up with no
edit at all.

The one thing that fixed name cannot do is invent an asset. GitHub answers
`releases/latest/download/<name>` with a 404 when the newest release has no file
under that name, and the button looks fine right up until someone clicks it. So
the newest release has to have been built by this workflow: after changing the
asset name, or when a release was published without it, re-run **Actions →
Release → Run workflow**, which attaches the archive to the release matching
`version.py`. The run's last step follows the public link and fails if it does
not resolve, and `tests/test_site_download.py` keeps the name on the page and
the name in the workflow from drifting apart.

The executable ships inside a zip on purpose: browsers and antivirus engines
flag a freshly downloaded, unsigned `.exe` far more readily than the same binary
in an archive. The release also carries a `.sha256` for the archive, linked from
the download page.

`assets/main.js` then fills the card in from
`api.github.com/repos/aquaxs1/Explorer-Manager/releases/latest`: the version and
the size, neither of which a static page can know, and a fallback to whatever
Windows asset the release does carry if the expected name is missing.
It is decoration only — the served markup already links the archive, and any
failure leaves the page as it is. The API host is in `connect-src` in both
`vercel.json` files; drop the fetch and it can come back out.
