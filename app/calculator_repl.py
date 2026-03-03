import sys
from .input_validators import parse_command
from .calculation import CalculatorFacade
from .calculator_config import  load_config
from .exceptions import InvalidInputError, DivisionByZeroError, CalculationError, PersistenceError
from .logger import build_logger
from .observers import LoggingObserver, AutoSaveObserver
from .colors import init_colors, paint

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

def process_command(calc: CalculatorFacade, history, cfg, line: str):
    """
    Process one REPL command line using configuration from cfg.
    cfg must have:
      - cfg.auto_save (bool)
      - cfg.history_file (Path)
    """
    try:
        cmd, a, b = parse_command(line)

        if cmd == "help":
            return {"printed": paint(WELCOME, kind="title"), "exit": False}

        if cmd == "exit":
            if cfg.auto_save:
                calc.save_history(str(cfg.history_file))
            return {"printed": paint("Goodbye.", kind="info"), "exit": True}

        if cmd == "history":
            df = calc.get_history_df()
            if df.empty:
                return {"printed": paint("No history.", kind="info"), "exit": False}
            return {"printed": paint(df.to_string(index=False), kind="title"), "exit": False}

        if cmd == "save":
            calc.save_history(str(cfg.history_file))
            return {"printed": paint(f"Saved history to {cfg.history_file}", kind="info"), "exit": False}

        if cmd == "load":
            calc.load_history(str(cfg.history_file))
            return {"printed": paint(f"Loaded history from {cfg.history_file}", kind="info"), "exit": False}

        if cmd == "clear":
            calc.clear_history()
            return {"printed": paint("Cleared history.", kind="info"), "exit": False}

        if cmd == "undo":
            ok = calc.undo()
            return {"printed": paint(f"Undo: {ok}", kind="info"), "exit": False}

        if cmd == "redo":
            ok = calc.redo()
            return {"printed": paint(f"Redo: {ok}", kind="info"), "exit": False}

        # Otherwise it's an operation
        result = calc.calculate(cmd, a, b)
        return {"printed": paint(f"=> {result}", kind="ok"), "exit": False}

    except InvalidInputError as e:
        return {"printed": paint(f"Input error: {e}", kind="error"), "exit": False}

    except DivisionByZeroError as e:
        return {"printed": paint(f"Math error: {e}", kind="error"), "exit": False}

    except PersistenceError as e:
        return {"printed": paint(f"File error: {e}", kind="error"), "exit": False}

    except CalculationError as e:
        return {"printed": paint(f"Calculation error: {e}", kind="error"), "exit": False}

    except Exception as e:
        return {"printed": paint(f"Unexpected error: {e}", kind="error"), "exit": False}  # pragma: no cover
    

def repl():
    init_colors()
    cfg = load_config()
    calc = CalculatorFacade(config=cfg)
    if cfg.auto_save:
        calc.save_history(str(cfg.history_file))

    logger = build_logger(str(cfg.log_file))
    calc.register_observer(LoggingObserver(logger))
    calc.register_observer(AutoSaveObserver(history_path=str(cfg.history_file), enabled=cfg.auto_save))

    print(paint(WELCOME, kind="title"))
    while True:
        try:
            line = input("calc> ").strip()
            if not line:
                continue
            res = process_command(calc, calc, cfg, line)
            print(res["printed"])
            if res["exit"]:
                # Flush and close logger handlers on exit
                for handler in logger.handlers:
                    handler.flush()
                    handler.close()
                sys.exit(0)
        except EOFError:
            if cfg.auto_save:
                calc.save_history(str(cfg.history_file))
            # Flush and close logger handlers on EOF
            for handler in logger.handlers:
                handler.flush()
                handler.close()
            print(paint("Goodbye.", kind="info"))
            sys.exit(0)
        except SystemExit:
            raise
        except Exception as e:
            print(paint(f"REPL-level unexpected error: {e}", kind="error"))  # pragma: no cover



if __name__ == "__main__":
    repl()  # pragma: no cover
