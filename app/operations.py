# app/operations.py
from abc import ABC, abstractmethod
import math
from .exceptions import DivisionByZeroError, OperationError

class OperationFactory:
    """Factory class to create operation instances."""
    _operations = {}
    _help_registry = []

    @classmethod
    def register(cls, names: list[str], description: str):
        """Decorator to register a new operation to the factory and help menu."""
        def wrapper(operation_class):
            cls._help_registry.append({"commands": names, "description": description})
            for name in names:
                cls._operations[name.lower()] = operation_class
            return operation_class
        return wrapper

    @classmethod
    def create(cls, op_name: str):
        op_name = op_name.lower()
        if op_name not in cls._operations:
            from .exceptions import OperationError
            raise OperationError(f"Unsupported operation: {op_name}")
        return cls._operations[op_name]()
    
    @classmethod
    def generate_help(cls) -> str:
        help_text = "Enhanced Calculator REPL\n\nCommands:\n"
        for entry in cls._help_registry:
            cmds = "|".join(entry["commands"]) + " a b"
            help_text += f"  {cmds:<18} -> {entry['description']}\n"
            
        static_help = [
            ("history", "print calculation history"),
            ("undo", "undo last operation"),
            ("redo", "redo last undone operation"),
            ("save", "save history to default path"),
            ("load", "load history from default path"),
            ("clear", "clear history"),
            ("help", "show this help"),
            ("exit", "quit"),
        ]
        help_text += "\n"
        for cmd, desc in static_help:
            help_text += f"  {cmd:<18} -> {desc}\n"
        return help_text

class Operation(ABC):
    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Execute operation and return result."""
        raise NotImplementedError

@OperationFactory.register(["add", "+"], "addition")
class Add(Operation):
    def execute(self, a, b):
        return a + b

@OperationFactory.register(["sub", "-", "subtract"], "subtraction")
class Sub(Operation):
    def execute(self, a, b):
        return a - b

@OperationFactory.register(["mul", "*", "multiply"], "multiplication")
class Mul(Operation):
    def execute(self, a, b):
        return a * b

@OperationFactory.register(["div", "/", "divide"], "division")
class Div(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Division by zero is not allowed.")
        return a / b

@OperationFactory.register(["pow", "^", "power"], "power (a^b)")
class Pow(Operation):
    def execute(self, a, b):
        return a ** b

@OperationFactory.register(["root"], "b-th root of a")
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

@OperationFactory.register(["modulus", "mod", "%"], "remainder of a divided by b")
class Modulus(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Modulus by zero is not allowed.")
        return a % b

@OperationFactory.register(["int_divide", "intdiv", "//"], "integer division (discard fractional part)")
class IntDivide(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Integer division by zero is not allowed.")
        return math.trunc(a / b)

@OperationFactory.register(["percent", "pct"], "(a / b) * 100")
class Percent(Operation):
    def execute(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Percentage with divisor zero is not allowed.")
        return (a / b) * 100.0

@OperationFactory.register(["abs_diff", "absdiff"], "absolute difference |a - b|")
class AbsDiff(Operation):
    def execute(self, a, b):
        return abs(a - b)