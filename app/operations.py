# app/operations.py
from abc import ABC, abstractmethod
import math
from .exceptions import DivisionByZeroError ,OperationError

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
            raise OperationError("Root degree cannot be zero.")
        try:
            ib = int(b)
        except Exception:
            ib = None
        if a < 0:
            if ib is not None and ib % 2 == 1:
                return - (abs(a) ** (1.0 / b))
            raise OperationError("Even root of a negative number is invalid.")
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

class OperationFactory:
    """Factory class to create operation instances."""

    _operations = {
        "add": Add,
        "+": Add,

        "sub": Sub,
        "-": Sub,
        "subtract": Sub,          # ✅ added

        "mul": Mul,
        "*": Mul,
        "multiply": Mul,          # ✅ added

        "div": Div,
        "/": Div,
        "divide": Div,            # ✅ added

        "pow": Pow,
        "^": Pow,
        "power": Pow,             # ✅ added

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

    @classmethod
    def create(cls, op_name: str) -> Operation:
        op_name = op_name.lower()
        if op_name not in cls._operations:
            from .exceptions import OperationError
            raise OperationError(f"Unsupported operation: {op_name}")
        return cls._operations[op_name]()