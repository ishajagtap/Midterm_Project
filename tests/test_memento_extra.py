from app.calculator_memento import Caretaker


def test_caretaker_undo_redo_reset_save():
    c = Caretaker()
    # initial reset
    c.reset({"x": 1})
    assert c.latest_state() == {"x": 1}

    # save new states
    c.save({"x": 2})
    c.save({"x": 3})
    assert c.latest_state() == {"x": 3}

    # undo should remove latest
    m = c.undo()
    assert m is not None
    assert c.latest_state() == {"x": 2}

    # redo should restore
    m2 = c.redo()
    assert m2 is not None
    assert c.latest_state() == {"x": 3}

    # undo repeatedly until None (cannot go past initial)
    while True:
        if c.undo() is None:
            break

    assert c.latest_state() == {"x": 1}

    # ensure no redos available now (clear any and assert None)
    c._redos.clear()
    assert c.redo() is None
