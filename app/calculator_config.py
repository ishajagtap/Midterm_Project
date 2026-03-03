# app/calculator_config.py
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from .exceptions import ConfigError

load_dotenv()

def _bool_from_env(val: str) -> bool:
    v = val.strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n"}:
        return False
    raise ConfigError("CALCULATOR_AUTO_SAVE must be true/false (or 1/0).")

def _int_from_env(key: str, val: str) -> int:
    try:
        return int(val)
    except Exception as e:
        raise ConfigError(f"{key} must be an integer.") from e

@dataclass(frozen=True)
class CalculatorConfig:
    log_dir: Path
    history_dir: Path
    max_history_size: int
    auto_save: bool
    precision: int
    max_input_value: float
    default_encoding: str
    log_file: Path 
    history_file: Path

    # @property
    # def log_file(self) -> Path:
    #     return self.log_dir / "calculator.log"

    # @property
    # def history_file(self) -> Path:
    #     return self.history_dir / "history.csv"

def load_config() -> CalculatorConfig:
    log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", "data/logs"))
    history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", "data/history"))
    history_file_env = os.getenv("CALCULATOR_HISTORY_FILE", "").strip()
    log_file_env = os.getenv("CALCULATOR_LOG_FILE", "").strip()

    

    if log_file_env:
        log_file = Path(log_file_env)
    else:
        log_file = log_dir / "calculator.log"

    if history_file_env:
        history_file = Path(history_file_env)
    else:
        history_file = history_dir / "history.csv"

    max_history_size = _int_from_env(
        "CALCULATOR_MAX_HISTORY_SIZE",
        os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100"),
    )

    auto_save = _bool_from_env(os.getenv("CALCULATOR_AUTO_SAVE", "true"))

    precision = _int_from_env(
        "CALCULATOR_PRECISION",
        os.getenv("CALCULATOR_PRECISION", "4"),
    )
    if precision < 0 or precision > 15:
        raise ConfigError("CALCULATOR_PRECISION must be between 0 and 15.")

    try:
        
        max_input_value = float(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000000"))
    except Exception as e:
        raise ConfigError("CALCULATOR_MAX_INPUT_VALUE must be a number.") from e
    if max_input_value <= 0:
        raise ConfigError("CALCULATOR_MAX_INPUT_VALUE must be > 0.")

    default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8").strip() or "utf-8"

    # Ensure dirs exist on startup (spec wants configs validated/usable)
    try:
        history_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
    # Do not fail at config-load time if the history path is invalid.
    # Tests expect persistence errors to be handled during save/load.
        pass
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ConfigError(f"Cannot create log directory: {log_dir}") from e

    try:
        history_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
    # Don't fail at config-load time.
    # Tests expect persistence errors to be handled when saving/loading history.
        pass

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ConfigError(f"Cannot create log file directory: {log_file.parent}") from e

    return CalculatorConfig(
        log_dir=log_dir,
        history_dir=history_dir,
        max_history_size=max_history_size,
        auto_save=auto_save,
        precision=precision,
        max_input_value=max_input_value,
        default_encoding=default_encoding,
        log_file=log_file,
        history_file=history_file,
    )

def get_history_path() -> Path:
    """
    Return the path to the history CSV and ensure the directory exists.
    Some unit tests expect this function.
    """
    cfg = load_config()
    try:
        cfg.history_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
    # Keep it non-fatal; persistence should fail on save/load, not config read.
        pass
    return cfg.history_file


def get_auto_save(val: object = None) -> bool:
    """
    Parse boolean variants for auto-save. Some unit tests call:
    get_auto_save("true"), get_auto_save("1"), get_auto_save("yes"), etc.

    If val is None, read CALCULATOR_AUTO_SAVE from environment.
    """
    if val is None:
        val = os.getenv("CALCULATOR_AUTO_SAVE", "true")
    return _bool_from_env(str(val))