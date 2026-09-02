"""The site links a release asset it does not build.

The download page hard-codes releases/latest/download/<name>, and the release
workflow decides what <name> is. Nothing connects the two but this test: rename
the asset on one side only and every download button on the site quietly starts
serving a 404, which is exactly what happened once already.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"

RELEASE_URL = re.compile(
    r"https://github\.com/aquaxs1/Explorer-Manager/releases/(?P<path>[^\s\"'<>]*)"
)


def published_asset_name():
    """The asset name release.yml attaches to every release."""
    match = re.search(r'^\s*echo "asset=(?P<name>\S+)"', WORKFLOW.read_text(), re.M)
    assert match, "release.yml no longer sets an 'asset=' output"
    return match.group("name")


def pages():
    return sorted(SITE.glob("*.html"))


def release_links():
    for page in pages():
        for match in RELEASE_URL.finditer(page.read_text(encoding="utf-8")):
            yield page.name, match.group("path")


def test_the_download_button_points_at_the_asset_the_workflow_builds():
    asset = published_asset_name()
    wanted = f"latest/download/{asset}"

    downloads = [
        (page, path)
        for page, path in release_links()
        if "/download/" in path and not path.endswith(".sha256")
    ]
    assert downloads, "no download link left on the site"
    for page, path in downloads:
        assert path == wanted, f"{page} links {path}, but the workflow ships {asset}"


def test_the_checksum_link_matches_the_archive():
    asset = published_asset_name()
    for page, path in release_links():
        if path.endswith(".sha256"):
            assert path == f"latest/download/{asset}.sha256", f"{page} links {path}"


def test_no_page_pins_a_version():
    """releases/latest/... resolves itself; a pinned tag goes stale in silence."""
    for page, path in release_links():
        assert not re.match(r"(download|tag)/v?\d", path), (
            f"{page} pins a release ({path}); use releases/latest/..."
        )
