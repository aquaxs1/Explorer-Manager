"""What survives a restart, and what must not."""

import json

import pytest

import settings


@pytest.fixture
def store(tmp_path):
    return tmp_path / "settings.json"


def rule(**kwargs):
    base = {"filename": "Invoice", "filetype": ".pdf", "destination": "D:/Docs"}
    base.update(kwargs)
    return base


def test_missing_file_starts_empty(store):
    assert settings.load_settings(store) == {"version": 2, "rules": [], "watch_folders": []}


def test_unreadable_file_starts_empty(store):
    store.write_text("{not json at all", encoding="utf-8")
    assert settings.load_settings(store)["rules"] == []


def test_unfinished_rule_is_dropped(store):
    store.write_text(json.dumps({"rules": [
        rule(destination=settings.DEST_PLACEHOLDER),
        rule(destination=""),
        rule(),
    ]}), encoding="utf-8")
    kept = settings.load_settings(store)["rules"]
    assert [r["destination"] for r in kept] == ["D:/Docs"]


def test_unfinished_rule_is_never_written(store):
    settings.save_settings([rule(destination=settings.DEST_PLACEHOLDER), rule()], [], store)
    assert len(json.loads(store.read_text(encoding="utf-8"))["rules"]) == 1


def test_catch_all_rule_is_kept(store):
    """An empty filename with no file type matches everything - on purpose."""
    kept = settings.clean_rules([rule(filename="", filetype="not defined")])
    assert len(kept) == 1


def test_rule_order_and_switch_survive(store):
    settings.save_settings(
        [rule(filename="A"), rule(filename="B", enabled=False)], [], store)
    kept = settings.load_settings(store)["rules"]
    assert [(r["filename"], r["enabled"]) for r in kept] == [("A", True), ("B", False)]
    assert [r["filename"] for r in settings.active_rules(kept)] == ["A"]


def test_version_1_settings_are_migrated(store):
    """Version 1 stored plain strings and had no on/off flag."""
    store.write_text(json.dumps({
        "rules": [{"filename": "x", "filetype": ".pdf", "destination": "D:/Docs"}],
        "watch_folders": ["C:/Downloads", "C:/Desktop"],
    }), encoding="utf-8")
    data = settings.load_settings(store)
    assert data["version"] == settings.SETTINGS_VERSION
    assert data["rules"][0]["enabled"] is True
    assert data["watch_folders"][0] == {"path": "C:/Downloads", "active": True, "recursive": False}


def test_folders_keep_their_flags_and_stay_unique(store):
    settings.save_settings([], [
        {"path": "C:/Downloads", "active": False, "recursive": True},
        "C:/Downloads",
        "C:/Desktop",
        {"path": "  "},
    ], store)
    folders = settings.load_settings(store)["watch_folders"]
    assert [f["path"] for f in folders] == ["C:/Downloads", "C:/Desktop"]
    assert folders[0] == {"path": "C:/Downloads", "active": False, "recursive": True}


def test_save_leaves_no_temp_file_behind(store):
    settings.save_settings([rule()], ["C:/Downloads"], store)
    assert store.exists()
    assert list(store.parent.glob("*.tmp")) == []


def test_app_dir_follows_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("EXPLORER_MANAGER_HOME", str(tmp_path / "em"))
    assert settings.app_dir() == tmp_path / "em"
    assert settings.settings_file().name == "settings.json"
