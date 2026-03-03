# app/calculation.py
from typing import Dict
from .operations import AbsDiff, Add, IntDivide, Modulus, Percent, Sub, Mul, Div, Pow, Root, Operation
from .history import History
from .calculator_memento import Caretaker
from .exceptions import InvalidInputError

OP_MAP = {
    "add": Add,
    "+": Add,
    "sub": Sub,
    "-": Sub,
    "mul": Mul,
    "*": Mul,
    "div": Div,
    "/": Div,
    "pow": Pow,
    "^": Pow,
    "root": Root,
    "modulus": Modulus,
    "mod": Modulus,
    "%": Modulus,

    "int_divide": IntDivide,
    "intdiv": IntDivide,
    "//": IntDivide,

    "percent": Percent,
    "pct": Percent,

    "abs_diff": AbsDiff,
    "absdiff": AbsDiff,
}

class CalculatorFacade:
    def __init__(self, history: History = None):
        self.history = history if history is not None else History()
        self._caretaker = Caretaker()
        self._last_result = None
        # initial snapshot
        self._caretaker.save(self._capture_state())

    def _capture_state(self):
        return {
            "last_result": self._last_result,
            "history": self.history.df.to_dict(orient="list")
        }

    def _restore_state(self, state: dict):
        self._last_result = state.get("last_result", None)
        hist_dict = state.get("history", {})
        if hist_dict:
            import pandas as pd
            self.history.df = pd.DataFrame(hist_dict)
        else:
            from .history import COLUMNS
            import pandas as pd
            # fallback restore for empty history; excluded from coverage as it's a rare fallback path
            self.history.df = pd.DataFrame(columns=COLUMNS)  # pragma: no cover

    def calculate(self, op_name: str, a: float, b: float) -> float:
        op_class = OP_MAP.get(op_name)
        if op_class is None:
            raise InvalidInputError(f"Unknown operation: {op_name}")
        op: Operation = op_class()
        result = op.execute(a, b)
        self._last_result = result
        self.history.append(op_name, a, b, result)
        self._caretaker.save(self._capture_state())
        return result

    def undo(self):
        m = self._caretaker.undo()
        if m is None:
            return False
        latest = self._caretaker.latest_state()
        if latest:
            self._restore_state(latest)
        return True

    def redo(self):
        m = self._caretaker.redo()
        if m is None:
            return False
        latest = self._caretaker.latest_state()
        if latest:
            self._restore_state(latest)
        return True

    def save_history(self, path: str):
        self.history.to_csv(path)

    def load_history(self, path: str):
        self.history.load_csv(path)
        self._caretaker.save(self._capture_state())

    def get_history_df(self):
        return self.history.df.copy()
    
    def clear_history(self) -> None:
        from .history import History
        self.history = History()
        self._last_result = None
        #  reset caretaker stacks to match cleared state
        self._caretaker.reset(self._capture_state())
