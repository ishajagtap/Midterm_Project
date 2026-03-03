import sys
from .input_validators import parse_command
from .calculation import CalculatorFacade
from .calculator_config import  load_config
from .exceptions import InvalidInputError, DivisionByZeroError, CalculationError, PersistenceError
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
            return {"printed": WELCOME, "exit": False}

        if cmd == "exit":
            if cfg.auto_save:
                calc.save_history(str(cfg.history_file))
            return {"printed": "Goodbye.", "exit": True}

        if cmd == "history":
            df = calc.get_history_df()
            if df.empty:
                return {"printed": "No history.", "exit": False}
            return {"printed": df.to_string(index=False), "exit": False}

        if cmd == "save":
            calc.save_history(str(cfg.history_file))
            return {"printed": f"Saved history to {cfg.history_file}", "exit": False}

        if cmd == "load":
            calc.load_history(str(cfg.history_file))
            return {"printed": f"Loaded history from {cfg.history_file}", "exit": False}

        if cmd == "clear":
            calc.clear_history()
            return {"printed": "Cleared history.", "exit": False}

        if cmd == "undo":
            ok = calc.undo()
            return {"printed": f"Undo: {ok}", "exit": False}

        if cmd == "redo":
            ok = calc.redo()
            return {"printed": f"Redo: {ok}", "exit": False}

        # Otherwise it's an operation
        result = calc.calculate(cmd, a, b)
        return {"printed": f"=> {result}", "exit": False}

    except InvalidInputError as e:
        return {"printed": f"Input error: {e}", "exit": False}

    except DivisionByZeroError as e:
        return {"printed": f"Math error: {e}", "exit": False}

    except PersistenceError as e:
        return {"printed": f"File error: {e}", "exit": False}

    except CalculationError as e:
        return {"printed": f"Calculation error: {e}", "exit": False}

    except Exception as e:
        return {"printed": f"Unexpected error: {e}", "exit": False}  # pragma: no cover
    

def repl():
    cfg = load_config()
    calc = CalculatorFacade(config=cfg)
    if cfg.auto_save:
        calc.save_history(str(cfg.history_file))

    logger = build_logger(str(cfg.log_file))
    calc.register_observer(LoggingObserver(logger))
    calc.register_observer(AutoSaveObserver(history_path=str(cfg.history_file), enabled=cfg.auto_save))

    print(WELCOME)
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
            print("Goodbye.")
            sys.exit(0)
        except SystemExit:
            raise
        except Exception as e:
            print("REPL-level unexpected error:", e)  # pragma: no cover

# def repl():

#     cfg = load_config()
#     calc = CalculatorFacade(config=cfg)
#     # history_path = get_history_path()
#     # auto_save = get_auto_save()
#     logger = build_logger(str(cfg.log_file))
    
    


#     calc.register_observer(LoggingObserver(logger))
#     calc.register_observer(
#         AutoSaveObserver(history_path=str(cfg.history_file), enabled=cfg.auto_save))
#     print(WELCOME)
#     while True:
#         try:
#             line = input("calc> ").strip()
#             if not line:
#                 continue
#             res = process_command(calc, line, history_path, auto_save)
#             print(res["printed"])
#             if res["exit"]:
#                 sys.exit(0)
#         except EOFError:
#             if auto_save:
#                 calc.save_history(history_path)
#             print("Goodbye.")
#             sys.exit(0)
#         except SystemExit:
#             raise
#         except Exception as e:
#             # This is an REPL-level unexpected error path that is difficult to exercise reliably in tests.
#             # Mark it as intentionally excluded from coverage measurement.
#             print("REPL-level unexpected error:", e)  # pragma: no cover

if __name__ == "__main__":
    repl()  # pragma: no cover
