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

    @property
    def log_file(self) -> Path:
        return self.log_dir / "calculator.log"

    @property
    def history_file(self) -> Path:
        return self.history_dir / "history.csv"

def load_config() -> CalculatorConfig:
    log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", "data/logs"))
    history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", "data/history"))

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
    log_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)

    return CalculatorConfig(
        log_dir=log_dir,
        history_dir=history_dir,
        max_history_size=max_history_size,
        auto_save=auto_save,
        precision=precision,
        max_input_value=max_input_value,
        default_encoding=default_encoding,
    )