# app/history.py
from importlib.resources import path

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional
from datetime import timezone


COLUMNS = ["timestamp", "operation", "a", "b", "result"]

class History:
    def __init__(self):
        self.df = pd.DataFrame(columns=COLUMNS)

    def append(self, operation: str, a: float, b: float, result: float,max_size: Optional[int] = None):
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "a": a,
            "b": b,
            "result": result
        }
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        if max_size is not None and len(self.df) > max_size:
            self.df = self.df.iloc[-max_size:].reset_index(drop=True)

    def to_csv(self, path: str, encoding: str = "utf-8"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(path, index=False, encoding=encoding)

    def load_csv(self, path: str, encoding: str = "utf-8"):
        self.df = pd.read_csv(path, encoding=encoding)
        self.df = self.df[[c for c in COLUMNS if c in self.df.columns]]

   