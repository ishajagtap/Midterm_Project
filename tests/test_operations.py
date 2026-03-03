# tests/test_operations.py
import pytest
from app.operations import Add, Sub, Mul, Div, Pow, Root
from app.exceptions import DivisionByZeroError, OperationError

def test_add():
    assert Add().execute(2, 3) == 5

def test_sub():
    assert Sub().execute(5, 3) == 2

def test_mul():
    assert Mul().execute(4, 2.5) == 10

def test_div():
    assert Div().execute(9, 3) == 3

def test_div_by_zero():
    with pytest.raises(DivisionByZeroError):
        Div().execute(1, 0)

def test_pow():
    assert Pow().execute(2, 3) == 8

def test_root_positive():
    assert pytest.approx(Root().execute(27, 3)) == 3

def test_root_negative_odd():
    assert pytest.approx(Root().execute(-27, 3)) == -3

def test_root_negative_even():
    with pytest.raises(OperationError):
        Root().execute(-16, 2)