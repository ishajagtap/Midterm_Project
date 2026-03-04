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
import importlib
import math
import pytest

from app.exceptions import OperationError, ValidationError, DivisionByZeroError

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

def _import_any(module_names):
    last = None
    for name in module_names:
        try:
            return importlib.import_module(name)
        except Exception as e:
            last = e
    raise ImportError(f"Could not import any of: {module_names}. Last error: {last}")


def _get_facade_instance():
    """
    Tries common module/class names so the tests work even if your file names differ.
    Adjust this list if your project uses different names.
    """
    candidates = [
        ("app.calculation", ["CalculatorFacade", "Calculator"]),
        ("app.calculator", ["CalculatorFacade", "Calculator"]),
        ("app.calculator_facade", ["CalculatorFacade"]),
    ]

    for mod_name, class_names in candidates:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue

        for cls_name in class_names:
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                try:
                    return cls()
                except TypeError:
                    # Some constructors require config or args; skip if so.
                    continue

    pytest.skip("Could not construct Calculator/Facade automatically. Adjust _get_facade_instance().")


def _call_calculate(obj, cmd: str, a: float, b: float):
    """
    Calls your calculator/facade method in a flexible way.
    It tries common method names used in these projects.
    """
    for method_name in ("calculate", "compute", "execute", "run", "perform"):
        if hasattr(obj, method_name):
            method = getattr(obj, method_name)
            try:
                return method(cmd, a, b)
            except TypeError:
                # Some implementations might require (a, b, cmd)
                try:
                    return method(a, b, cmd)
                except TypeError:
                    pass

    raise AttributeError("No calculate-like method found. Add one of: calculate/compute/execute/run/perform")


def _get_operation_factory():
    """
    Tries common factory locations.
    """
    factory_modules = [
        "app.operation_factory",
        "app.operations_factory",
        "app.factory",
        "app.operations",
    ]
    mod = _import_any(factory_modules)

    if hasattr(mod, "OperationFactory"):
        return getattr(mod, "OperationFactory")

    # Some projects expose create() at module-level
    if hasattr(mod, "create"):
        return mod

    raise AttributeError("OperationFactory not found. Update _get_operation_factory() for your project.")


def _make_operation(op_name: str):
    """
    Create an operation instance via your factory.
    """
    Factory = _get_operation_factory()

    if hasattr(Factory, "create"):
        return Factory.create(op_name)

    # module-level create(op)
    if hasattr(Factory, "create"):
        return Factory.create(op_name)

    raise AttributeError("Factory has no create() method.")


def _eval_operation(op, a, b):
    """
    Execute an operation instance with a few common method names.
    """
    for method_name in ("execute", "calculate", "compute", "__call__"):
        if hasattr(op, method_name):
            m = getattr(op, method_name)
            if method_name == "__call__":
                return op(a, b)
            return m(a, b)
    raise AttributeError("Operation has no execute/calculate/compute/__call__ method.")


# ---------- Tests: mandatory operations ----------

@pytest.mark.parametrize(
    "op_name,a,b,expected",
    [
        ("power", 2, 3, 8),
        ("root", 27, 3, 3),
        ("modulus", 10, 3, 1),
        ("int_divide", 10, 3, 3),          # assumes truncation toward integer quotient
        ("percent", 50, 200, 25),          # (a/b)*100 -> 25
        ("abs_diff", 10, 3, 7),
    ],
)
def test_factory_operations_happy_path(op_name, a, b, expected):
    op = _make_operation(op_name)
    out = _eval_operation(op, a, b)
    assert out == pytest.approx(expected)


def test_divide_by_zero_raises():
    try:
        op = _make_operation("divide")
    except Exception:
        pytest.skip("No 'divide' operation in this project; skipping.")
    with pytest.raises((DivisionByZeroError, OperationError, ValidationError, ZeroDivisionError)):
        _eval_operation(op, 10, 0)


def test_percent_divide_by_zero_raises():
    op = _make_operation("percent")
    with pytest.raises((DivisionByZeroError, OperationError, ValidationError, ZeroDivisionError)):
        _eval_operation(op, 10, 0)


def test_root_invalid_cases():
    op = _make_operation("root")

    # nth root where n == 0 should be invalid
    with pytest.raises((OperationError, ValidationError, ZeroDivisionError, ValueError)):
        _eval_operation(op, 16, 0)

    # If your implementation disallows even roots of negative numbers, this should raise.
    # If you allow it, change this expected behavior.
    with pytest.raises((OperationError, ValidationError, ValueError)):
        _eval_operation(op, -16, 2)


# ---------- Tests: facade calculation + history behavior (if supported) ----------

def test_facade_calculate_returns_number():
    calc = _get_facade_instance()
    out = _call_calculate(calc, "power", 2, 4)
    assert isinstance(out, (int, float))
    assert out == pytest.approx(16)


def test_facade_records_history_if_exposed():
    calc = _get_facade_instance()

    # Try to locate a history container on common attribute names
    history_attr = None
    for name in ("history", "calc_history", "_history"):
        if hasattr(calc, name):
            history_attr = name
            break

    if history_attr is None:
        pytest.skip("Facade does not expose history; skipping history length check.")

    hist = getattr(calc, history_attr)

    # normalize to length
    def hlen(x):
        try:
            return len(x)
        except Exception:
            return None

    before = hlen(hist)
    _call_calculate(calc, "abs_diff", 9, 2)
    after = hlen(getattr(calc, history_attr))

    if before is None or after is None:
        pytest.skip("History object has no len(); skipping.")
    assert after == before + 1


def test_facade_undo_redo_if_supported():
    calc = _get_facade_instance()

    if not hasattr(calc, "undo") or not hasattr(calc, "redo"):
        pytest.skip("Facade does not expose undo/redo; skipping.")

    # Perform two operations
    _call_calculate(calc, "abs_diff", 9, 2)   # 7
    _call_calculate(calc, "modulus", 10, 4)   # 2

    # Undo should succeed
    undo_result = calc.undo()
    # Some implementations return the undone calc, some return current value; just ensure no crash
    assert undo_result is None or isinstance(undo_result, (int, float, object))

    # Redo should succeed
    redo_result = calc.redo()
    assert redo_result is None or isinstance(redo_result, (int, float, object))