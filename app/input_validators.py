# app/input_validators.py
import math
from typing import Tuple, Optional
from .exceptions import InvalidInputError, ValidationError
from .calculator_config import load_config


def parse_command(line: str) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Accepts strings like:
      add 2 3
      + 2 3
      pow 2 3
      root 27 3

    Returns (command, a, b)
    For zero-operand commands like 'undo' or 'history', returns (command, None, None)
    """
    if line is None or not line.strip():
        raise InvalidInputError("Empty input.")

    parts = line.strip().split()
    cmd = parts[0].lower()

    if cmd in {"undo", "redo", "history", "help", "exit", "save", "load", "clear"}:
        if len(parts) != 1:
            raise InvalidInputError(f"Command '{cmd}' takes no operands.")
        return cmd, None, None

    if len(parts) != 3:
        raise InvalidInputError("Expected: <operation> <a> <b>")

    try:
        a = float(parts[1])
        b = float(parts[2])
    except ValueError:
        raise InvalidInputError("Operands must be numbers.")

    if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
        raise ValidationError("Inputs must be real finite numbers (not NaN/Infinity).")
        
    cfg = load_config()
    lim = cfg.max_input_value
    if abs(a) > lim or abs(b) > lim:
        raise ValidationError(f"Inputs must be within ±{lim}.")

    return cmd, a, b