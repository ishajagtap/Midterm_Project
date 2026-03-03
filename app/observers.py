# app/observers.py
from __future__ import annotations
from abc import ABC, abstractmethod
import logging

class Observer(ABC):
    @abstractmethod
    def update(self, *, operation: str, a: float, b: float, result: float, calc) -> None:
        """
        Called after a new calculation is performed.
        `calc` is the calculator instance so observers can access history/config.
        """
        raise NotImplementedError

class LoggingObserver(Observer):
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def update(self, *, operation: str, a: float, b: float, result: float, calc) -> None:
        self._logger.info(
            "op=%s a=%s b=%s result=%s",
            operation, a, b, result
        )
        # Flush handlers to ensure logs are written to disk immediately
        for handler in self._logger.handlers:
            handler.flush()

class AutoSaveObserver(Observer):
    def __init__(self, history_path: str, enabled: bool = True):
        self._history_path = history_path
        self._enabled = enabled

    def update(self, *, operation: str, a: float, b: float, result: float, calc) -> None:
        if not self._enabled:
            return
        # Save current history to CSV using pandas (your History already does this)
        calc.save_history(self._history_path)