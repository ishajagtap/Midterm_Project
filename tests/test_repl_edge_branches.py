# tests/test_repl_edge_branches.py
import builtins
import sys
import io
import pytest
import app.calculator_repl as repl_module
from types import SimpleNamespace

def _make_input_sequence(lines):
    it = iter(lines)
    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
    return fake_input

def test_repl_invalid_and_unknown_commands(monkeypatch, tmp_path):
    # prepare inputs:
    # 1) blank line (should be skipped)
    # 2) clear (recognized by parse_command but REPL doesn't handle explicitly -> InvalidInputError path)
    # 3) unknown 1 2 (should raise InvalidInputError from CalculatorFacade.calculate -> printed as Calculation error)
    # 4) help (prints welcome)
    # 5) exit (to stop the loop)
    inputs = ["", "clear", "unknown 1 2", "help", "exit"]

    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "False")

    monkeypatch.setattr(builtins, "input", _make_input_sequence(inputs))

    # Capture stdout/stderr
    saved_out = sys.stdout
    saved_err = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    with pytest.raises(SystemExit):
        repl_module.repl()

    out = sys.stdout.getvalue()
    err = sys.stderr.getvalue()

    # restore
    sys.stdout = saved_out
    sys.stderr = saved_err

    # Ensure the help/welcome printed
    assert "Enhanced Calculator REPL" in out
    # Because we passed "clear" and "unknown 1 2", REPL should have printed an input or calculation error
    assert ("Input error:" in out) or ("Calculation error:" in out)