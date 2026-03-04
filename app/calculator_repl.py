import sys
from .input_validators import parse_command
from .calculation import CalculatorFacade
from .calculator_config import load_config
from .exceptions import InvalidInputError, DivisionByZeroError, CalculationError, PersistenceError
from .logger import build_logger
from .observers import LoggingObserver, AutoSaveObserver
from .colors import init_colors, paint
from .commands import (
    CommandInvoker, CalculateCommand, HistoryCommand, SaveCommand, 
    LoadCommand, ClearCommand, UndoCommand, RedoCommand, HelpCommand, ExitCommand
)
from .operations import OperationFactory

def process_command(calc: CalculatorFacade, history, cfg, line: str):
    """
    Process one REPL command line using configuration from cfg.
    Encapsulates command request using the Command Pattern.
    """
    try:
        cmd, a, b = parse_command(line)
        command_obj = None

        if cmd == "help":
            command_obj = HelpCommand()
        elif cmd == "exit":
            command_obj = ExitCommand(calc, cfg)
        elif cmd == "history":
            command_obj = HistoryCommand(calc)
        elif cmd == "save":
            command_obj = SaveCommand(calc, str(cfg.history_file))
        elif cmd == "load":
            command_obj = LoadCommand(calc, str(cfg.history_file))
        elif cmd == "clear":
            command_obj = ClearCommand(calc)
        elif cmd == "undo":
            command_obj = UndoCommand(calc)
        elif cmd == "redo":
            command_obj = RedoCommand(calc)
        else:
            command_obj = CalculateCommand(calc, cmd, a, b)

        invoker = CommandInvoker()
        return invoker.execute_command(command_obj)

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

    welcome_text = OperationFactory.generate_help()
    print(paint(welcome_text, kind="title"))
    
    while True:
        try:
            line = input("calc> ").strip()
            if not line:
                continue
            res = process_command(calc, calc.history, cfg, line)
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
