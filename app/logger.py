# app/logger.py
import logging
from pathlib import Path

def build_logger(log_path: str) -> logging.Logger:
    """
    Create (or return) a configured logger that writes to log_path.
    """
    logger = logging.getLogger("calculator")
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if build_logger is called again
    if any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        return logger

    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    # Flush after each log message to ensure data is written immediately
    fh.flush()

    logger.addHandler(fh)
    return logger