import pytest
from types import SimpleNamespace
import pandas as pd

from app.history import History
from app.exceptions import PersistenceError
from pandas.errors import EmptyDataError, ParserError


def test_to_csv_permission_error(monkeypatch, tmp_path):
    h = History()

    # monkeypatch the dataframe to_csv to raise PermissionError
    def bad_to_csv(path, index=False, encoding=None):
        raise PermissionError("denied")

    h.df.to_csv = bad_to_csv

    with pytest.raises((PersistenceError, PermissionError)):
        h.to_csv(str(tmp_path / "cannot_write" / "history.csv"))


def test_to_csv_os_error(monkeypatch, tmp_path):
    h = History()

    def bad_to_csv(path, index=False, encoding=None):
        raise OSError("disk full")

    h.df.to_csv = bad_to_csv

    with pytest.raises((PersistenceError, OSError)):
        h.to_csv(str(tmp_path / "no_space" / "history.csv"))


def test_load_csv_empty_and_parser_errors(monkeypatch, tmp_path):
    h = History()
    p = tmp_path / "f.csv"

    # EmptyDataError
    monkeypatch.setattr(pd, "read_csv", lambda path, encoding=None: (_ for _ in ()).throw(EmptyDataError("empty")))
    with pytest.raises((PersistenceError, EmptyDataError)):
        h.load_csv(str(p))

    # ParserError
    monkeypatch.setattr(pd, "read_csv", lambda path, encoding=None: (_ for _ in ()).throw(ParserError("bad")))
    with pytest.raises((PersistenceError, ParserError)):
        h.load_csv(str(p))

    # UnicodeDecodeError
    def raise_unicode(path, encoding=None):
        raise UnicodeDecodeError("utf-8", b"", 0, 1, "err")

    monkeypatch.setattr(pd, "read_csv", raise_unicode)
    with pytest.raises((PersistenceError, UnicodeDecodeError)):
        h.load_csv(str(p))

    # Generic OSError
    monkeypatch.setattr(pd, "read_csv", lambda path, encoding=None: (_ for _ in ()).throw(OSError("io")))
    with pytest.raises((PersistenceError, OSError)):
        h.load_csv(str(p))
