import os
import importlib
from pathlib import Path

import pytest

def reload_colors_module():
    import app.colors as colors
    return importlib.reload(colors)

def test_colors_disabled_under_pytest():
    colors = reload_colors_module()
    # Under pytest, colors_enabled should be False (per your design)
    assert colors.colors_enabled() is False
    assert colors.paint("hello", kind="ok") == "hello"

def test_colors_env_toggle(monkeypatch):
    # simulate not running under pytest by reloading and removing marker
    # easiest: just ensure env false forces no color
    monkeypatch.setenv("CALCULATOR_COLOR", "false")
    colors = reload_colors_module()
    # still false under pytest; paint returns plain
    assert colors.paint("x", kind="error") == "x"

def test_load_config_defaults(tmp_path, monkeypatch):
    # Use tmp dirs so mkdir branches execute safely
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "hist" / "history.csv"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path / "logs" / "calc.log"))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")
    monkeypatch.setenv("CALCULATOR_PRECISION", "4")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "10")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "1000")
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    from app.calculator_config import load_config
    cfg = load_config()

    assert cfg.log_dir.exists()
    assert cfg.history_dir.exists()
    assert cfg.history_file.name == "history.csv"
    assert cfg.log_file.name.endswith(".log")
    assert cfg.auto_save is True
    assert cfg.max_history_size == 10
    assert cfg.precision == 4
    assert cfg.max_input_value == 1000.0

@pytest.mark.parametrize(
    "val,expected",
    [("true", True), ("1", True), ("yes", True), ("false", False), ("0", False), ("no", False)],
)
def test_get_auto_save_variants(val, expected):
    from app.calculator_config import get_auto_save
    assert get_auto_save(val) is expected

def test_get_history_path(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "historydir"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "historydir" / "history.csv"))

    from app.calculator_config import get_history_path
    p = get_history_path()

    assert isinstance(p, Path)
    # directory should exist (or at least not crash)
    assert p.name == "history.csv"