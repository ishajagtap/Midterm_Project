# tests/test_input_validators.py
import pytest
from app.input_validators import parse_command
from app.exceptions import InvalidInputError, ValidationError

def test_parse_valid():
    cmd, a, b = parse_command("add 2 3")
    assert cmd == "add"
    assert a == 2.0 and b == 3.0

def test_parse_short_command():
    cmd, a, b = parse_command("undo")
    assert cmd == "undo" and a is None and b is None

def test_parse_invalid_format():
    with pytest.raises(InvalidInputError):
        parse_command("add 2")

def test_parse_command_valid_operation():
    cmd, a, b = parse_command("add 2 3")
    assert cmd == "add"
    assert a == 2.0
    assert b == 3.0


def test_parse_command_valid_alias():
    cmd, a, b = parse_command("+ 5 6")
    assert cmd == "+"
    assert a == 5.0
    assert b == 6.0


def test_parse_command_empty_input():
    with pytest.raises(InvalidInputError):
        parse_command("")


def test_parse_command_none_input():
    with pytest.raises(InvalidInputError):
        parse_command(None)


def test_parse_command_invalid_operand_count():
    with pytest.raises(InvalidInputError):
        parse_command("add 5")


def test_parse_command_non_numeric_operands():
    with pytest.raises(InvalidInputError):
        parse_command("add a b")


def test_parse_command_nan_input():
    with pytest.raises(ValidationError):
        parse_command("add nan 5")


def test_parse_command_inf_input():
    with pytest.raises(ValidationError):
        parse_command("add inf 5")


def test_parse_command_zero_operand_commands():
    for cmd in ["undo", "redo", "history", "help", "exit", "save", "load", "clear"]:
        c, a, b = parse_command(cmd)
        assert c == cmd
        assert a is None
        assert b is None


def test_parse_command_zero_operand_with_extra_args():
    with pytest.raises(InvalidInputError):
        parse_command("undo 5")


def test_parse_command_out_of_range(monkeypatch):
    import app.input_validators as iv

    class DummyConfig:
        max_input_value = 10

    # Patch the symbol actually used inside parse_command()
    monkeypatch.setattr(iv, "load_config", lambda: DummyConfig())

    with pytest.raises(ValidationError):
        iv.parse_command("add 20 5")