
import os
import sys

_COLOR_ENABLED = None

# If colorama is not installed, or colors disabled, fall back to plain text.
try:
    from colorama import Fore, Style, init as colorama_init
except Exception:  # pragma: no cover
    Fore = None
    Style = None
    colorama_init = None

_COLOR_ENABLED = None

def colors_enabled() -> bool:
    """
    Enable colors by default unless disabled via env var:
    CALCULATOR_COLOR=false
    """
    global _COLOR_ENABLED
    if _COLOR_ENABLED is not None:
        return _COLOR_ENABLED
    
    if "pytest" in sys.modules: # pragma: no cover
        _COLOR_ENABLED = False
        return _COLOR_ENABLED

    val = os.getenv("CALCULATOR_COLOR", "true").strip().lower()
    _COLOR_ENABLED = val in {"1", "true", "yes", "y", "on"}
    return _COLOR_ENABLED

def init_colors() -> None:
    """
    Initialize colorama on Windows; safe no-op elsewhere.
    """
    if colorama_init and colors_enabled():
        colorama_init(autoreset=True)

def paint(text: str, *, kind: str) -> str:
    """
    kind: "ok" | "error" | "warn" | "info" | "title"
    """
    if not colors_enabled() or Fore is None or Style is None:
        return text

    if kind == "ok":
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
    if kind == "error":
        return f"{Fore.RED}{text}{Style.RESET_ALL}"
    if kind == "warn":
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
    if kind == "title":
        return f"{Fore.BLUE}{text}{Style.RESET_ALL}"
    # info/default
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"