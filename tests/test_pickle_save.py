import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pickle
import builtins
from task import Task
from orga import on_closing, tkMessageBox


def test_on_closing_saves_and_loads(tmp_path, monkeypatch):
    main = Task('Main')
    sub = Task('Sub', due_date='2025-12-31', priority=1, completed=True)
    main.add_sub_task(sub)

    monkeypatch.setattr(tkMessageBox, 'askyesno', lambda *a, **k: True)

    class DummyRoot:
        def __init__(self):
            self.destroyed = False
        def destroy(self):
            self.destroyed = True

    root = DummyRoot()
    file_path = tmp_path / 'object.pkl'

    original_open = builtins.open
    def fake_open(path, mode='r', *args, **kwargs):
        if path == 'object.pkl':
            return original_open(file_path, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fake_open)

    on_closing(main, root)
    assert root.destroyed

    with original_open(file_path, 'rb') as f:
        loaded = pickle.load(f)

    assert loaded.name == 'Main'
    loaded_sub = loaded.get_sub_tasks()[0]
    assert loaded_sub.name == 'Sub'
    assert loaded_sub.due_date == '2025-12-31'
    assert loaded_sub.priority == 1
    assert loaded_sub.completed
