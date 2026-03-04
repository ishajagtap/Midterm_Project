# tests/test_run_module_main.py
import runpy
import builtins
import pytest
from pathlib import Path
import sys

def test_run_module_main(monkeypatch, tmp_path):
    """
    Execute the calculator_repl module as __main__ in-process. We monkeypatch
    input() so the REPL loop receives a sequence of commands and then exits.
    This exercises the module-level '__main__' entrypoint and many REPL branches
    under the pytest-cov measured process.
    """
    # Prepare inputs to exercise many branches then exit
    seq = iter([
        "",               # empty -> skipped
        "help",           # prints welcome
        "unknown 1 2",    # unknown operation -> error branch
        "add 1 2",        # performs an operation
        "history",        # prints history
        "save",           # save branch
        "exit"            # exit -> should raise SystemExit
    ])

    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "True")

    monkeypatch.setattr(builtins, "input", lambda prompt="": next(seq))

    # Running as __main__ will call repl(); it will sys.exit on "exit" -> catch SystemExit
    # Ensure a prior import of app.calculator_repl doesn't trigger a RuntimeWarning
    sys.modules.pop("app.calculator_repl", None)
    with pytest.raises(SystemExit):
        runpy.run_module("app.calculator_repl", run_name="__main__")

    # Ensure history file was created by AUTO_SAVE=True
    assert Path(tmp_path / "history.csv").exists()