from types import SimpleNamespace
from pathlib import Path
import importlib
import pytest

from app import calculator_repl as replmod
from app.calculator_config import CalculatorConfig


class FakeCalc:
    def __init__(self):
        self.saved = []
        self.loaded = False
        self.cleared = False
        self.history_df = SimpleNamespace(empty=True)

    def save_history(self, path):
        self.saved.append(path)

    def load_history(self, path):
        self.loaded = True

    def clear_history(self):
        self.cleared = True

    def get_history_df(self):
        return self.history_df

    def undo(self):
        return True

    def redo(self):
        return True

    def calculate(self, cmd, a, b):
        return 123.456


@pytest.fixture
def cfg(tmp_path):
    return CalculatorConfig(
        log_dir=Path(tmp_path / "logs"),
        history_dir=Path(tmp_path / "history"),
        max_history_size=100,
        auto_save=True,
        precision=4,
        max_input_value=1000.0,
        default_encoding="utf-8",
        log_file=Path(tmp_path / "logs" / "calculator.log"),
        history_file=Path(tmp_path / "history" / "history.csv"),
    )


def test_process_help(cfg):
    calc = FakeCalc()
    res = replmod.process_command(calc, calc, cfg, "help")
    assert "Enhanced Calculator REPL" in res["printed"]
    assert res["exit"] is False


def test_process_exit_auto_save(cfg, tmp_path):
    calc = FakeCalc()
    res = replmod.process_command(calc, calc, cfg, "exit")
    assert res["exit"] is True
    assert len(calc.saved) == 1


def test_process_exit_no_auto_save(cfg, tmp_path):
    calc = FakeCalc()
    cfg2 = cfg
    # create a copy with auto_save False
    cfg2 = cfg2.__class__(**{**cfg2.__dict__, "auto_save": False})
    res = replmod.process_command(calc, calc, cfg2, "exit")
    assert res["exit"] is True
    assert len(calc.saved) == 0


def test_process_history_empty(cfg):
    calc = FakeCalc()
    res = replmod.process_command(calc, calc, cfg, "history")
    assert "No history." in res["printed"]


def test_process_save_load_clear_undo_redo(cfg):
    calc = FakeCalc()
    assert replmod.process_command(calc, calc, cfg, "save")["exit"] is False
    assert len(calc.saved) == 1
    assert replmod.process_command(calc, calc, cfg, "load")["exit"] is False
    assert calc.loaded is True
    assert replmod.process_command(calc, calc, cfg, "clear")["exit"] is False
    assert calc.cleared is True
    assert replmod.process_command(calc, calc, cfg, "undo")["exit"] is False
    assert replmod.process_command(calc, calc, cfg, "redo")["exit"] is False


def test_process_operation_and_exceptions(monkeypatch, cfg):
    calc = FakeCalc()
    # normal operation
    res = replmod.process_command(calc, calc, cfg, "add 1 2")
    assert "=>" in res["printed"]

    # simulate parse errors and calculation exceptions
    def raise_invalid(_):
        raise replmod.InvalidInputError("bad")

    monkeypatch.setattr(replmod, "parse_command", lambda line: (_ for _ in ()).throw(replmod.InvalidInputError("bad")))
    r = replmod.process_command(calc, calc, cfg, "whatever")
    assert "Input error:" in r["printed"]

    monkeypatch.setattr(replmod, "parse_command", lambda line: (_ for _ in ()).throw(replmod.DivisionByZeroError("zero")))
    r = replmod.process_command(calc, calc, cfg, "whatever")
    assert "Math error:" in r["printed"]

    monkeypatch.setattr(replmod, "parse_command", lambda line: (_ for _ in ()).throw(replmod.PersistenceError("p")))
    r = replmod.process_command(calc, calc, cfg, "whatever")
    assert "File error:" in r["printed"]

    monkeypatch.setattr(replmod, "parse_command", lambda line: (_ for _ in ()).throw(replmod.CalculationError("c")))
    r = replmod.process_command(calc, calc, cfg, "whatever")
    assert "Calculation error:" in r["printed"]
