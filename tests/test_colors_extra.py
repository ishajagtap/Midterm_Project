# tests/test_colors_extra.py
import importlib
import sys
from types import SimpleNamespace

import app.colors as colors


def reload_colors():
    return importlib.reload(colors)


def test_paint_kinds_when_enabled(monkeypatch):
    # Ensure module is reloaded and force colors enabled
    m = reload_colors()
    m._COLOR_ENABLED = True

    # Replace Fore/Style with simple markers
    m.Fore = SimpleNamespace(GREEN="<G>", RED="<R>", YELLOW="<Y>", BLUE="<B>", CYAN="<C>")
    m.Style = SimpleNamespace(RESET_ALL="</>")

    assert m.paint("ok", kind="ok") == "<G>ok</>"
    assert m.paint("err", kind="error") == "<R>err</>"
    assert m.paint("warn", kind="warn") == "<Y>warn</>"
    assert m.paint("title", kind="title") == "<B>title</>"
    assert m.paint("info", kind="info") == "<C>info</>"


def test_init_colors_calls_colorama_init(monkeypatch):
    m = reload_colors()
    called = {"ok": False}

    def fake_init(**kwargs):
        called["ok"] = True

    # Ensure colorama_init exists and colors are enabled
    m.colorama_init = fake_init
    m._COLOR_ENABLED = True

    m.init_colors()
    assert called["ok"] is True


def test_colors_enabled_respects_env(monkeypatch):
    # Temporarily remove pytest from sys.modules to let the function read env
    had_pytest = "pytest" in sys.modules
    saved = sys.modules.pop("pytest", None)
    try:
        monkeypatch.setenv("CALCULATOR_COLOR", "false")
        # Force reload so cached _COLOR_ENABLED resets
        m = reload_colors()
        m._COLOR_ENABLED = None
        assert m.colors_enabled() is False

        monkeypatch.setenv("CALCULATOR_COLOR", "true")
        m = reload_colors()
        m._COLOR_ENABLED = None
        assert m.colors_enabled() is True
    finally:
        # restore pytest module in sys.modules if it was present
        if had_pytest:
            sys.modules["pytest"] = saved


def test_paint_when_disabled_returns_plain(monkeypatch):
    m = reload_colors()
    # Simulate pytest environment: disable colors
    m._COLOR_ENABLED = False
    m.Fore = SimpleNamespace(GREEN="G")
    m.Style = SimpleNamespace(RESET_ALL="/")

    assert m.paint("text", kind="ok") == "text"
