# tests/test_process_command_all_branches.py
import os
from pathlib import Path
import builtins
import io
import sys
import pytest

from app.calculation import CalculatorFacade
from app.calculator_repl import process_command
from app.calculator_config import load_config
from app.history import History

def setup_env(tmp_path, monkeypatch, autosave="True"):
    hist = tmp_path / "history.csv"
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", autosave)
    return str(hist)

def test_process_command_help_and_ops_and_exit_and_clear(tmp_path, monkeypatch):
    setup_env(tmp_path, monkeypatch, autosave="False")
    cfg = load_config()
    calc = CalculatorFacade(config=cfg)
    history = History()

    # help
    r = process_command(calc, history, cfg, "help")
    assert "Enhanced Calculator REPL" in r["printed"]

    # basic op
    r2 = process_command(calc, history, cfg, "add 4 5")
    assert "=> 9.0" in r2["printed"]

    # history (should have one entry now)
    r3 = process_command(calc, history, cfg, "history")
    assert "operation" in r3["printed"] or "add" in r3["printed"]

    # clear
    r4 = process_command(calc, history, cfg, "clear")
    assert "Cleared history." in r4["printed"]
    # history now empty
    r5 = process_command(calc, history, cfg, "history")
    assert "No history." in r5["printed"]

    # undo/redo on fresh (should return printed booleans)
    r6 = process_command(calc, history, cfg, "undo")
    assert r6["printed"].startswith("Undo:")
    r7 = process_command(calc, history, cfg, "redo")
    assert r7["printed"].startswith("Redo:")

    # save and load (save to path, then load)
    r8 = process_command(calc, history, cfg, "save")
    assert "Saved history to" in r8["printed"]
    r9 = process_command(calc, history, cfg, "load")
    assert "Loaded history from" in r9["printed"]

def test_process_command_division_by_zero_and_unknown(tmp_path, monkeypatch):
    setup_env(tmp_path, monkeypatch)
    cfg = load_config()
    calc = CalculatorFacade(config=cfg)
    history = History()

    # div by zero
    r1 = process_command(calc, history, cfg, "div 1 0")
    assert "Math error" in r1["printed"] or "Division by zero" in r1["printed"]

    # unknown operation
    r2 = process_command(calc, history, cfg, "unknown_op 1 2")
    assert "Input error" in r2["printed"] or "Unknown" in r2["printed"]

def test_process_command_exit_autosave_true(tmp_path, monkeypatch):
    setup_env(tmp_path, monkeypatch, autosave="True")
    cfg = load_config()
    calc = CalculatorFacade(config=cfg)
    history = History()

    # perform operation
    r1 = process_command(calc, history, cfg, "add 2 3")
    assert "=> 5.0" in r1["printed"]

    # exit (should save)
    r2 = process_command(calc, history, cfg, "exit")
    assert r2["exit"] is True
    assert "Goodbye." in r2["printed"]