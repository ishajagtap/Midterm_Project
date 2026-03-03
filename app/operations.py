# app/operations.py
from abc import ABC, abstractmethod
import math
from .exceptions import DivisionByZeroError

class Operation(ABC):
    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Execute operation and return result."""
        raise NotImplementedError

class Add(Operation):
    def execute(self, a, b):
        return a + b

class Sub(Operation):
    def execute(self, a, b):
        return a - b

class Mul(Operation):
    def execute(self, a, b):
        return a * b

class Div(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Division by zero is not allowed.")
        return a / b

class Pow(Operation):
    def execute(self, a, b):
        return a ** b

class Root(Operation):
    def execute(self, a, b):
        if b == 0:
            raise ValueError("Root degree cannot be zero.")
        try:
            ib = int(b)
        except Exception:
            ib = None
        if a < 0:
            if ib is not None and ib % 2 == 1:
                return - (abs(a) ** (1.0 / b))
            raise ValueError("Even root of negative number is invalid.")
        return a ** (1.0 / b)

class Modulus(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Modulus by zero is not allowed.")
        return a % b

class IntDivide(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Integer division by zero is not allowed.")
        # Discard fractional part (truncate toward 0)
        return math.trunc(a / b)

class Percent(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Percentage with divisor zero is not allowed.")
        return (a / b) * 100.0

class AbsDiff(Operation):
    def execute(self, a, b):
        return abs(a - b)
