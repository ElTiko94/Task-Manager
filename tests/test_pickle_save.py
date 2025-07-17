import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import builtins
from task import Task
from orga import on_closing, load_tasks, tkMessageBox
from persistence import load_tasks_from_json, save_tasks_to_json


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
    file_path = tmp_path / 'tasks.json'

    original_open = builtins.open
    def fake_open(path, mode='r', *args, **kwargs):
        if path == 'tasks.json':
            return original_open(file_path, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fake_open)

    on_closing(main, root)
    assert root.destroyed

    loaded = load_tasks_from_json(file_path)

    assert loaded.name == 'Main'
    loaded_sub = loaded.get_sub_tasks()[0]
    assert loaded_sub.name == 'Sub'
    assert loaded_sub.due_date == '2025-12-31'
    assert loaded_sub.priority == 1
    assert loaded_sub.completed


def test_load_tasks_with_corrupt_json(tmp_path, monkeypatch, capsys):
    bad_file = tmp_path / 'tasks.json'
    bad_file.write_text('not json', encoding='utf-8')

    original_open = builtins.open

    def fake_open(path, mode='r', *args, **kwargs):
        if path == 'tasks.json':
            return original_open(bad_file, mode, *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fake_open)

    task = load_tasks()
    assert isinstance(task, Task)
    assert task.name == 'Main'
    captured = capsys.readouterr()
    assert 'Warning:' in captured.out


def test_on_closing_no_prompt_when_unmodified(tmp_path, monkeypatch):
    """Closing without changes should not prompt to save."""
    main = Task('Main')
    main.add_sub_task(Task('Sub'))

    file_path = tmp_path / 'tasks.json'
    save_tasks_to_json(main, file_path)

    original_open = builtins.open

    def fake_open(path, mode='r', *args, **kwargs):
        if path == 'tasks.json':
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
