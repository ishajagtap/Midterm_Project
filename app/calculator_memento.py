# app/calculator_memento.py
from dataclasses import dataclass
import pandas as pd
from typing import Any, Optional

@dataclass
class Memento:
    state: dict

class Caretaker:
    def __init__(self):
        self._undos = []
        self._redos = []

    def save(self, state: dict) -> Memento:
        m = Memento(state=state.copy())
        self._undos.append(m)
        self._redos.clear()
        return m

    def undo(self) -> Optional[Memento]:
        #  Do not undo past the initial snapshot
        if len(self._undos) <= 1:
            return None
        m = self._undos.pop()
        self._redos.append(m)
        return m

    def redo(self) -> Optional[Memento]:
        if not self._redos:
            return None
        m = self._redos.pop()
        self._undos.append(m)
        return m

    def latest_state(self) -> Optional[dict]:
        if not self._undos:
            return None
        return self._undos[-1].state.copy()

    #  Add a reset helper (needed for clear)
    def reset(self, initial_state: dict) -> None:
        self._undos = [Memento(state=initial_state.copy())]
        self._redos = []