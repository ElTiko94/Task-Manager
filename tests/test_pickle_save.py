import os, sys
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import builtins
from pathlib import Path
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

    on_closing(main, root, file_path)
    assert root.destroyed

    loaded = load_tasks_from_json(file_path)

    assert loaded.name == 'Main'
    loaded_sub = loaded.get_sub_tasks()[0]
    assert loaded_sub.name == 'Sub'
    assert loaded_sub.due_date == '2025-12-31'
    assert loaded_sub.priority == 1
    assert loaded_sub.completed


def test_load_tasks_with_corrupt_json(tmp_path, monkeypatch, caplog):
    bad_file = tmp_path / 'tasks.json'
    bad_file.write_text('not json', encoding='utf-8')

    with caplog.at_level(logging.WARNING):
        task = load_tasks(bad_file)
    assert isinstance(task, Task)
    assert task.name == 'Main'
    assert any('Failed to load tasks' in rec.getMessage() for rec in caplog.records)


def test_on_closing_no_prompt_when_unmodified(tmp_path, monkeypatch):
    """Closing without changes should not prompt to save."""
    main = Task('Main')
    main.add_sub_task(Task('Sub'))

    file_path = tmp_path / 'tasks.json'
    save_tasks_to_json(main, file_path)

    asked = []
    monkeypatch.setattr(tkMessageBox, 'askyesno', lambda *a, **k: asked.append(True))

    class DummyRoot:
        def __init__(self):
            self.destroyed = False
        def destroy(self):
            self.destroyed = True

    root = DummyRoot()
    on_closing(main, root, file_path)

    assert root.destroyed
    assert not asked


def test_on_closing_write_failure(tmp_path, monkeypatch):
    main = Task('Main')
    main.add_sub_task(Task('Sub'))

    monkeypatch.setattr(tkMessageBox, 'askyesno', lambda *a, **k: True)

    warnings = []
    monkeypatch.setattr(tkMessageBox, 'showwarning', lambda *a, **k: warnings.append(True))

    class DummyRoot:
        def __init__(self):
            self.destroyed = False
        def destroy(self):
            self.destroyed = True

    root = DummyRoot()
    file_path = tmp_path / 'tasks.json'

    original_open = builtins.open

    def fail_open(path, mode='r', *args, **kwargs):
        if Path(path) == file_path and 'w' in mode:
            raise OSError('write failed')
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', fail_open)

    on_closing(main, root, file_path)

    assert root.destroyed
    assert warnings
