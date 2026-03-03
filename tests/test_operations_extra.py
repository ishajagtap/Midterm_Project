# tests/test_operations_extra.py
import pytest
from app.operations import Root, Add
from app.exceptions import OperationError

def test_root_degree_zero_raises():
    with pytest.raises(OperationError):
        Root().execute(16, 0)

def test_root_even_negative_raises_and_degree_zero():
    with pytest.raises(OperationError):
        # even root of negative number -> OperationError
        Root().execute(-8, 2)
    with pytest.raises(OperationError):
        # degree zero invalid
        Root().execute(16, 0)

def test_add_basic():
    # small sanity check to ensure Add executed (helps cover small missing lines)
    assert Add().execute(0, 0) == 0