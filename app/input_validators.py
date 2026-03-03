# app/input_validators.py
from typing import Tuple, Optional
from .exceptions import InvalidInputError, ValidationError

def parse_command(calc,line: str) ->  Tuple[str, Optional[float], Optional[float]]:
    """
    Accepts strings like:
      add 2 3
      + 2 3
      pow 2 3
      root 27 3
    Returns (command, a, b)
    For one-argument commands like 'undo' or 'history', returns (command, None, None)
    """
    if not line:
        raise InvalidInputError("Empty input.")
    parts = line.strip().split()
    cmd = parts[0].lower()
    if cmd in {"undo", "redo", "history", "help", "exit", "save", "load", "clear"}:
        return cmd, None, None
    if len(parts) != 3:
        raise InvalidInputError("Expected: <operation> <a> <b>")
    try:
        a = float(parts[1])
        b = float(parts[2])

        if calc.config is not None:
            m = calc.config.max_input_value
            if abs(a) > m or abs(b) > m:
                raise ValidationError(f"Inputs must be within ±{m}.")
    except ValueError:
        raise InvalidInputError("Operands must be numbers.")
    return cmd, a, b