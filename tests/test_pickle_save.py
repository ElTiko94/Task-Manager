import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pickle
import builtins
from task import Task
from orga import on_closing, load_tasks, tkMessageBox


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


def test_load_tasks_with_corrupt_pickle(tmp_path, monkeypatch):
    bad_file = tmp_path / 'object.pkl'
    bad_file.write_bytes(b'not a pickle')

    original_open = builtins.open

    def fake_open(path, mode='rb', *args, **kwargs):
        if path == 'object.pkl':
            return original_open(bad_file, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fake_open)

    warnings = []
    monkeypatch.setattr(tkMessageBox, 'showwarning', lambda *a, **k: warnings.append(True))

    task = load_tasks()
    assert isinstance(task, Task)
    assert task.name == 'Main'
    assert warnings  # ensure warning was triggered


def test_on_closing_no_prompt_when_unmodified(tmp_path, monkeypatch):
    """Closing without changes should not prompt to save."""
    main = Task('Main')
    main.add_sub_task(Task('Sub'))

    file_path = tmp_path / 'object.pkl'
    with open(file_path, 'wb') as f:
        pickle.dump(main, f)

    original_open = builtins.open

    def fake_open(path, mode='r', *args, **kwargs):
        if path == 'object.pkl':
            return original_open(file_path, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fake_open)

    asked = []
    monkeypatch.setattr(tkMessageBox, 'askyesno', lambda *a, **k: asked.append(True))

    class DummyRoot:
        def __init__(self):
            self.destroyed = False
        def destroy(self):
            self.destroyed = True

    root = DummyRoot()
    on_closing(main, root)

    assert root.destroyed
    assert not asked


def test_on_closing_write_failure(tmp_path, monkeypatch):
    main = Task('Main')

    monkeypatch.setattr(tkMessageBox, 'askyesno', lambda *a, **k: True)

    warnings = []
    monkeypatch.setattr(tkMessageBox, 'showwarning', lambda *a, **k: warnings.append(True))

    class DummyRoot:
        def __init__(self):
            self.destroyed = False
        def destroy(self):
            self.destroyed = True

    root = DummyRoot()

    original_open = builtins.open

    def fail_open(path, mode='r', *args, **kwargs):
        if path == 'object.pkl' and 'w' in mode:
            raise OSError('write failed')
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fail_open)

    on_closing(main, root)

    assert root.destroyed
    assert warnings
