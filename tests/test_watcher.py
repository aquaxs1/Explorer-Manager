"""The sorting itself: what gets moved, what is left alone."""

from pathlib import Path

import pytest

import watcher


@pytest.fixture
def src(tmp_path):
    folder = tmp_path / "downloads"
    folder.mkdir()
    return folder


@pytest.fixture
def dest(tmp_path):
    return tmp_path / "invoices"


def rule(dest, **kwargs):
    base = {"filename": "Invoice", "filetype": ".pdf", "destination": str(dest), "enabled": True}
    base.update(kwargs)
    return base


def make(folder, name, content="x"):
    path = folder / name
    path.write_text(content, encoding="utf-8")
    return path


# ------------------------------------------------------------------ matching

@pytest.mark.parametrize("name, filename, filetype, expected", [
    ("Invoice_2026.pdf", "invoice", ".pdf", True),
    ("Invoice_2026.pdf", "INVOICE", ".PDF", True),
    ("Invoice_2026.pdf", "receipt", ".pdf", False),
    ("Invoice_2026.txt", "invoice", ".pdf", False),
    ("holiday.png", "", ".png", True),
    ("holiday.png", "", "not defined", True),
])
def test_matches_rule(name, filename, filetype, expected):
    match = watcher.matches_rule(Path(name), {"filename": filename, "filetype": filetype})
    assert match is expected


@pytest.mark.parametrize("name", [
    "movie.mkv.crdownload", "setup.exe.part", "notes.tmp", "~$report.docx",
])
def test_temporary_files_are_recognised(name):
    assert watcher.is_temporary(Path(name))


def test_a_normal_file_is_not_temporary():
    assert not watcher.is_temporary(Path("Invoice_2026.pdf"))


# -------------------------------------------------------------------- moving

def test_matching_file_is_moved(src, dest):
    f = make(src, "Invoice_2026.pdf")
    assert watcher.sort_file(f, [rule(dest)], wait=False)
    assert (dest / "Invoice_2026.pdf").exists()
    assert not f.exists()


def test_missing_destination_is_created(src, dest):
    watcher.sort_file(make(src, "Invoice_2026.pdf"), [rule(dest / "deep" / "deeper")], wait=False)
    assert (dest / "deep" / "deeper" / "Invoice_2026.pdf").exists()


def test_nothing_is_overwritten(src, dest):
    dest.mkdir()
    (dest / "Invoice_2026.pdf").write_text("old", encoding="utf-8")
    watcher.sort_file(make(src, "Invoice_2026.pdf", "new"), [rule(dest)], wait=False)
    assert (dest / "Invoice_2026.pdf").read_text(encoding="utf-8") == "old"
    assert (dest / "Invoice_2026_1.pdf").read_text(encoding="utf-8") == "new"


def test_first_matching_rule_wins(src, tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    rules = [rule(first, filename=""), rule(second)]
    watcher.sort_file(make(src, "Invoice_2026.pdf"), rules, wait=False)
    assert (first / "Invoice_2026.pdf").exists()
    assert not second.exists()


def test_disabled_rule_claims_nothing(src, dest):
    assert not watcher.sort_file(make(src, "Invoice_2026.pdf"), [rule(dest, enabled=False)], wait=False)
    assert not dest.exists()


def test_unfinished_rule_claims_nothing(src, dest):
    rules = [{"filename": "", "filetype": "not defined", "destination": "-- select destination --"},
             rule(dest)]
    assert watcher.sort_file(make(src, "Invoice_2026.pdf"), rules, wait=False)
    assert (dest / "Invoice_2026.pdf").exists()


def test_half_finished_download_is_left_alone(src, dest):
    f = make(src, "Invoice_2026.pdf.crdownload")
    assert not watcher.sort_file(f, [rule(dest, filetype="not defined")], wait=False)
    assert f.exists()


def test_non_matching_file_stays(src, dest):
    f = make(src, "holiday.png")
    assert not watcher.sort_file(f, [rule(dest)], wait=False)
    assert f.exists()


def test_a_file_already_in_its_destination_is_not_moved(src):
    f = make(src, "Invoice_2026.pdf")
    assert not watcher.sort_file(f, [rule(src)], wait=False)
    assert f.exists()


# ------------------------------------------------------- waiting for the file

def test_wait_until_complete_accepts_a_finished_file(src):
    assert watcher.wait_until_complete(make(src, "done.pdf"), timeout=5, interval=0.01)


def test_wait_until_complete_gives_up_on_a_missing_file(src):
    assert not watcher.wait_until_complete(src / "gone.pdf", timeout=5, interval=0.01)


def test_a_growing_file_is_not_moved_yet(src, dest, monkeypatch):
    """The old version slept half a second and moved whatever was there."""
    f = make(src, "Invoice_big.pdf")
    monkeypatch.setattr(watcher, "STABLE_INTERVAL", 0.01)
    monkeypatch.setattr(watcher.Path, "stat", lambda self: _growing(self))
    assert not watcher.wait_until_complete(f, timeout=0.2, interval=0.01)
    assert f.exists()


_sizes = iter(range(1, 10_000))


def _growing(path):
    class Stat:
        st_size = next(_sizes)
    return Stat()


# ------------------------------------------------------------ sort existing

def test_sort_existing_cleans_up_the_pile(src, dest):
    make(src, "Invoice_1.pdf")
    make(src, "Invoice_2.pdf")
    make(src, "holiday.png")
    assert watcher.sort_existing(src, [rule(dest)]) == 2
    assert sorted(p.name for p in dest.iterdir()) == ["Invoice_1.pdf", "Invoice_2.pdf"]
    assert (src / "holiday.png").exists()


def test_sort_existing_can_include_subfolders(src, dest):
    sub = src / "old"
    sub.mkdir()
    make(sub, "Invoice_3.pdf")
    assert watcher.sort_existing(src, [rule(dest)], recursive=False) == 0
    assert watcher.sort_existing(src, [rule(dest)], recursive=True) == 1
    assert (dest / "Invoice_3.pdf").exists()


def test_sort_existing_on_a_missing_folder_is_harmless(tmp_path, dest):
    assert watcher.sort_existing(tmp_path / "nope", [rule(dest)]) == 0
