# tests/test_calculator_config_and_repl.py
import os
import subprocess
import sys
import json
from pathlib import Path
import tempfile

import pytest

from app import calculator_config as cfg
from app.calculator_config import load_config

def test_load_config_default(tmp_path, monkeypatch):
    """Test that load_config creates directories and returns valid config."""
    log_dir = tmp_path / "logs"
    hist_dir = tmp_path / "history"
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(log_dir))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(hist_dir))
    
    config = load_config()
    assert config.log_dir == log_dir
    assert config.history_dir == hist_dir
    assert log_dir.exists()
    assert hist_dir.exists()

def test_load_config_auto_save_variants(monkeypatch):
    """Test auto_save config parsing."""
    test_cases = [
        ("True", True),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("False", False),
        ("false", False),
        ("0", False),
        ("no", False),
    ]
    for val, expected in test_cases:
        monkeypatch.setenv("CALCULATOR_AUTO_SAVE", val)
        config = load_config()
        assert config.auto_save is expected, f"Failed for value: {val}"

def test_load_config_invalid_auto_save(monkeypatch):
    """Test invalid auto_save raises error."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "notabool")
    with pytest.raises(Exception):
        load_config()

def test_repl_runs_and_exits(tmp_path, monkeypatch):
    """Test REPL subprocess runs and exits correctly."""
    log_dir = tmp_path / "logs"
    hist_dir = tmp_path / "history"
    env = os.environ.copy()
    env["CALCULATOR_LOG_DIR"] = str(log_dir)
    env["CALCULATOR_HISTORY_DIR"] = str(hist_dir)
    env["CALCULATOR_AUTO_SAVE"] = "True"
    
    proc = subprocess.run(
        [sys.executable, "-m", "app.calculator_repl"],
        input="exit\n",
        text=True,
        capture_output=True,
        env=env,
        timeout=5
    )
    out = proc.stdout + proc.stderr
    assert "Goodbye." in out
    # history file should be created
    assert (hist_dir / "history.csv").exists()