# app/commands.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from .colors import paint
from .operations import OperationFactory

class Command(ABC):
    """Abstract base class for all calculator commands."""
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Execute the command.
        Returns a dict containing:
        - 'printed': Expected text to output to the user.
        - 'exit': Bool indicating whether to terminate the REPL.
        """
        pass  # pragma: no cover

class CalculateCommand(Command):
    def __init__(self, calc, op_name: str, a: float, b: float):
        self.calc = calc
        self.op_name = op_name
        self.a = a
        self.b = b

    def execute(self) -> Dict[str, Any]:
        result = self.calc.calculate(self.op_name, self.a, self.b)
        return {"printed": paint(f"=> {result}", kind="ok"), "exit": False}

class HistoryCommand(Command):
    def __init__(self, calc):
        self.calc = calc

    def execute(self) -> Dict[str, Any]:
        df = self.calc.get_history_df()
        if df.empty:
            return {"printed": paint("No history.", kind="info"), "exit": False}
        return {"printed": paint(df.to_string(index=False), kind="title"), "exit": False}

class SaveCommand(Command):
    def __init__(self, calc, path: str):
        self.calc = calc
        self.path = path

    def execute(self) -> Dict[str, Any]:
        self.calc.save_history(self.path)
        return {"printed": paint(f"Saved history to {self.path}", kind="info"), "exit": False}

class LoadCommand(Command):
    def __init__(self, calc, path: str):
        self.calc = calc
        self.path = path

    def execute(self) -> Dict[str, Any]:
        self.calc.load_history(self.path)
        return {"printed": paint(f"Loaded history from {self.path}", kind="info"), "exit": False}

class ClearCommand(Command):
    def __init__(self, calc):
        self.calc = calc

    def execute(self) -> Dict[str, Any]:
        self.calc.clear_history()
        return {"printed": paint("Cleared history.", kind="info"), "exit": False}

class UndoCommand(Command):
    def __init__(self, calc):
        self.calc = calc

    def execute(self) -> Dict[str, Any]:
        ok = self.calc.undo()
        return {"printed": paint(f"Undo: {ok}", kind="info"), "exit": False}

class RedoCommand(Command):
    def __init__(self, calc):
        self.calc = calc

    def execute(self) -> Dict[str, Any]:
        ok = self.calc.redo()
        return {"printed": paint(f"Redo: {ok}", kind="info"), "exit": False}

class HelpCommand(Command):
    def execute(self) -> Dict[str, Any]:
        help_text = OperationFactory.generate_help()
        return {"printed": paint(help_text, kind="title"), "exit": False}

class ExitCommand(Command):
    def __init__(self, calc, cfg):
        self.calc = calc
        self.cfg = cfg

    def execute(self) -> Dict[str, Any]:
        # Optionally auto-saving on exit
        if self.cfg.auto_save:
            self.calc.save_history(str(self.cfg.history_file))
        return {"printed": paint("Goodbye.", kind="info"), "exit": True}

class CommandInvoker:
    """Invoker class for executing commands, applying the Command Pattern."""
    def execute_command(self, command: Command) -> Dict[str, Any]:
        return command.execute()
