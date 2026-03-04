import os
import pytest
from pathlib import Path

import app.calculator_config as cfgmod
from app.calculator_config import load_config, get_auto_save, get_history_path
from app.exceptions import ConfigError


def test_precision_out_of_range_low(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_PRECISION", "-1")
    with pytest.raises(ConfigError):
        load_config()


def test_precision_out_of_range_high(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_PRECISION", "100")
    with pytest.raises(ConfigError):
        load_config()


def test_max_input_value_invalid(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "not_a_number")
    with pytest.raises(ConfigError):
        load_config()


def test_get_auto_save_variants_and_history_path(monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "yes")
    assert get_auto_save() is True

    assert get_auto_save("false") is False

    # history path returns configured file
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "historydir"))
    p = get_history_path()
    assert isinstance(p, Path)
    # does not raise even if directories creation fails (function is resilient)