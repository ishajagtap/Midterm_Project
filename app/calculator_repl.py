import sys
from .input_validators import parse_command
from .calculation import CalculatorFacade
from .calculator_config import get_history_path, get_auto_save
from .exceptions import InvalidInputError, DivisionByZeroError, CalculationError
from .calculator_config import get_history_path, get_auto_save, get_log_path  # add get_log_path
from .logger import build_logger
from .observers import LoggingObserver, AutoSaveObserver

WELCOME = """Enhanced Calculator REPL

Commands:
  add|+ a b          -> addition
  sub|- a b          -> subtraction
  mul|* a b          -> multiplication
  div|/ a b          -> division
  pow|^ a b          -> power (a^b)
  root a b           -> b-th root of a

  modulus|mod|% a b  -> remainder of a divided by b
  int_divide|// a b  -> integer division (discard fractional part)
  percent a b        -> (a / b) * 100
  abs_diff a b       -> absolute difference |a - b|

  history            -> print calculation history
  undo               -> undo last operation
  redo               -> redo last undone operation
  save               -> save history to default path
  load               -> load history from default path
  clear              -> clear history
  help               -> show this help
  exit               -> quit
"""

def process_command(calc: CalculatorFacade, line: str, history_path: str, auto_save: bool):
    printed = ""
    exit_now = False
    try:
        cmd, a, b = parse_command(line)
        if cmd == "help":
            printed = WELCOME
            return {"printed": printed, "exit": False}
        if cmd == "exit":
            if auto_save:
                calc.save_history(history_path)
            exit_now = True
            printed = "Goodbye."
            return {"printed": printed, "exit": True}
        if cmd == "history":
            df = calc.get_history_df()
            if df.empty:
                printed = "No history."
            else:
                printed = df.to_string(index=False)
            return {"printed": printed, "exit": False}
        if cmd == "save":
            calc.save_history(history_path)
            printed = f"Saved history to {history_path}"
            return {"printed": printed, "exit": False}
        if cmd == "load":
            calc.load_history(history_path)
            printed = f"Loaded history from {history_path}"
            return {"printed": printed, "exit": False}
        if cmd == "clear":
            calc.clear_history()
            printed = "Cleared history."
            return {"printed": printed, "exit": False}
        if cmd == "undo":
            ok = calc.undo()
            printed = f"Undo: {ok}"
            return {"printed": printed, "exit": False}
        if cmd == "redo":
            ok = calc.redo()
            printed = f"Redo: {ok}"
            return {"printed": printed, "exit": False}

        result = calc.calculate(cmd, a, b)
        printed = f"=> {result}"
        return {"printed": printed, "exit": False}

    except InvalidInputError as e:
        printed = f"Input error: {e}"
        return {"printed": printed, "exit": False}
    except DivisionByZeroError as e:
        printed = f"Math error: {e}"
        return {"printed": printed, "exit": False}
    except CalculationError as e:
        printed = f"Calculation error: {e}"
        return {"printed": printed, "exit": False}
    except Exception as e:
        printed = f"Unexpected error: {e}"
        return {"printed": printed, "exit": False}

def repl():
    calc = CalculatorFacade()
    history_path = get_history_path()
    auto_save = get_auto_save()
    logger = build_logger(get_log_path())

    calc.register_observer(LoggingObserver(logger))
    calc.register_observer(
        AutoSaveObserver(history_path=history_path, enabled=auto_save))
    print(WELCOME)
    while True:
        try:
            line = input("calc> ").strip()
            if not line:
                continue
            res = process_command(calc, line, history_path, auto_save)
            print(res["printed"])
            if res["exit"]:
                sys.exit(0)
        except EOFError:
            if auto_save:
                calc.save_history(history_path)
            print("Goodbye.")
            sys.exit(0)
        except SystemExit:
            raise
        except Exception as e:
            # This is an REPL-level unexpected error path that is difficult to exercise reliably in tests.
            # Mark it as intentionally excluded from coverage measurement.
            print("REPL-level unexpected error:", e)  # pragma: no cover

if __name__ == "__main__":
    repl()  # pragma: no cover
