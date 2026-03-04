# app/calculation.py
from os import path
from typing import Dict

from .colors import init_colors, paint
from .operations import AbsDiff, Add, IntDivide, Modulus, Percent, Sub, Mul, Div, Pow, Root, Operation
from .history import History
from .calculator_memento import Caretaker
from .exceptions import OperationError, InvalidInputError,PersistenceError
from .observers import Observer 
from .operations import OperationFactory
from pandas.errors import ParserError


class CalculatorFacade:
    def __init__(self, history: History = None,config=None):
        self.config = config  # store config
        self.history = history if history is not None else History()
        self._caretaker = Caretaker()
        self._last_result = None
        # initial snapshot
        self._observers = []
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
        try:
            operation: Operation = OperationFactory.create(op_name)
        except Exception:
            raise InvalidInputError(paint(f"Unknown operation: {op_name}", kind="error"))

        try:
            result = operation.execute(a, b)
        except OperationError as e:
            raise InvalidInputError(paint(f"Operation error: {e}", kind="error"))

        if self.config is not None and getattr(self.config, "precision", None) is not None:
            result = round(result, int(self.config.precision))
        self._last_result = result
        max_size = self.config.max_history_size if self.config is not None else None
        self.history.append(op_name, a, b, result, max_size=max_size)
        self._caretaker.save(self._capture_state())
        self._notify_observers(operation=op_name, a=a, b=b, result=result)
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

    def save_history(self, path: str) -> None:
        try:
            self.history.to_csv(
                path,
                encoding=self.config.default_encoding if self.config else "utf-8"
            )

        except PersistenceError:
            raise

        except PermissionError as e:
            raise PersistenceError(
                paint(f"Cannot write history file (permission denied): {path}", kind="error")
            ) from e

        except OSError as e:
            raise PersistenceError(
                paint(f"Cannot write history file: {path}", kind="error")
            ) from e

        # catches pandas serialization/data errors
        except Exception as e:
            raise PersistenceError(
                paint(f"Failed to save history (data error): {path}", kind="error")
            ) from e

    def load_history(self, path: str) -> None:
        try:
            self.history.load_csv(
                path,
                encoding=self.config.default_encoding if self.config else "utf-8",
            )

        except PersistenceError:
            raise

        # ✅ add these two blocks
        except UnicodeDecodeError as e:
            raise PersistenceError(
                f"Cannot read history file (encoding error). Check CALCULATOR_DEFAULT_ENCODING: {path}"
            ) from e

        except Exception as e:
            # catches pandas ParserError, ValueError, etc. -> malformed CSV
            raise PersistenceError(
                f"History file is malformed or corrupted: {path}"
            ) from e
        except ParserError as e:
            raise PersistenceError(f"History file is malformed or corrupted: {path}") from e

    def get_history_df(self):
        return self.history.df.copy()
    
    def clear_history(self) -> None:
        from .history import History
        self.history = History()
        self._last_result = None
        #  reset caretaker stacks to match cleared state
        self._caretaker.reset(self._capture_state())

    
    def register_observer(self, observer: Observer) -> None:
        self._observers.append(observer)

    
    def _notify_observers(self, *, operation: str, a: float, b: float, result: float) -> None:
        for obs in self._observers:
            obs.update(operation=operation, a=a, b=b, result=result, calc=self)
