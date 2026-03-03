import os
import importlib
from pathlib import Path

import pytest


def test_calculate_rounding_and_history_max_size(tmp_path, monkeypatch):
    """
    Covers calculation.py branches:
    - rounding with cfg.precision
    - max_history_size trimming
    - observer notify path
    """
    from app.calculator_config import load_config
    from app.calculation import CalculatorFacade

    # use temp dirs so config mkdir runs
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "hist" / "history.csv"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path / "logs" / "calc.log"))

    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_PRECISION", "2")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "2")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "1000000")
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    cfg = load_config()
    calc = CalculatorFacade(config=cfg)

    # dummy observer to cover notify path
    seen = []
    class DummyObserver:
        def update(self, **kwargs):
            seen.append(kwargs)

    calc.register_observer(DummyObserver())

    r1 = calc.calculate("div", 1, 3)  # 0.33 after rounding
    assert r1 == 0.33

    calc.calculate("add", 1, 1)
    calc.calculate("add", 2, 2)  # history should cap at 2 entries

    df = calc.get_history_df()
    assert len(df) == 2
    assert len(seen) >= 1


@pytest.mark.parametrize(
    "val,expected",
    [("true", True), ("1", True), ("yes", True), ("y", True),
     ("false", False), ("0", False), ("no", False), ("n", False)]
)
def test_get_auto_save_variants(val, expected):
    from app.calculator_config import get_auto_save
    assert get_auto_save(val) is expected


def test_get_history_path_does_not_crash(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "h"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "h" / "history.csv"))
    from app.calculator_config import get_history_path
    p = get_history_path()
    assert isinstance(p, Path)
    assert p.name == "history.csv"


def test_colors_paint_kinds_plain_under_pytest():
    # Under pytest, colors are disabled, but paint should still return the original text.
    import app.colors as colors
    colors = importlib.reload(colors)

    assert colors.paint("ok", kind="ok") == "ok"
    assert colors.paint("err", kind="error") == "err"
    assert colors.paint("warn", kind="warn") == "warn"
    assert colors.paint("info", kind="info") == "info"
    assert colors.paint("title", kind="title") == "title"
    # unknown kind should still return text
    assert colors.paint("x", kind="something") == "x"