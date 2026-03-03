# tests/test_repl_inprocess.py
import builtins
import sys
import io
import pytest
from types import SimpleNamespace

import app.calculator_repl as repl_module

def _make_input_sequence(lines):
    """Return a function that behaves like input(), yielding items from lines list."""
    it = iter(lines)
    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            # If input is requested beyond our sequence, raise EOF to stop
            raise EOFError()
    return fake_input

def test_repl_handles_commands_and_exits(monkeypatch, tmp_path):
    # Prepare an input sequence: perform a calculation, show history, then exit.
    lines = [
        "add 1 2",   # calculation
        "history",   # print history
        "undo",      # undo (exercises undo branch)
        "redo",      # redo
        "save",      # save to default path (reads env)
        "exit"       # exit will call sys.exit(0)
    ]

    # Ensure history path points to tmp_path so REPL's save does not pollute home dir
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "True")

    fake_input = _make_input_sequence(lines)
    monkeypatch.setattr(builtins, "input", fake_input)

    # Capture stdout/stderr
    saved_out = sys.stdout
    saved_err = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    # Running repl() will call sys.exit(0) on exit -> catch SystemExit
    with pytest.raises(SystemExit) as excinfo:
        repl_module.repl()

    # restore streams
    out = sys.stdout.getvalue()
    err = sys.stderr.getvalue()
    sys.stdout = saved_out
    sys.stderr = saved_err

    # assert that sys.exit was called with code 0 (or None)
    assert excinfo.value.code in (0, None)
    # ensure the REPL printed the welcome message at start
    assert "Enhanced Calculator REPL" in out
    # ensure history file was created due to AUTO_SAVE=True
    assert (tmp_path / "history.csv").exists()