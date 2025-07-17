import os, sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from task import Task
from persistence import save_tasks_to_json, load_tasks_from_json


def build_task_tree():
    main = Task('Main', due_date='2025-12-31', priority=1)
    sub1 = Task('Sub1', completed=True)
    sub2 = Task('Sub2', due_date='2026-01-01')
    main.add_sub_task(sub1)
    main.add_sub_task(sub2)
    return main


def test_json_round_trip(tmp_path):
    task = build_task_tree()
    file_path = tmp_path / 'tasks.json'
    save_tasks_to_json(task, file_path)
    loaded = load_tasks_from_json(file_path)
    assert loaded.to_dict() == task.to_dict()


def test_json_round_trip_optional_fields(tmp_path):
    task = Task('Main')
    task.add_sub_task(Task('Child', priority=None, due_date=None))
    path = tmp_path / 'opt.json'
    save_tasks_to_json(task, path)
    loaded = load_tasks_from_json(path)
    assert loaded.to_dict() == task.to_dict()

def test_load_tasks_missing_file(tmp_path, capsys):
    path = tmp_path / 'missing.json'
    task = load_tasks_from_json(path)
    assert isinstance(task, Task)
    assert task.name == 'Main'
    captured = capsys.readouterr()
    assert 'Warning:' in captured.out


def test_load_tasks_invalid_json(tmp_path, capsys):
    path = tmp_path / 'bad.json'
    path.write_text('{ invalid json', encoding='utf-8')
    task = load_tasks_from_json(path)
    assert isinstance(task, Task)
    assert task.name == 'Main'
    captured = capsys.readouterr()
    assert 'Warning:' in captured.out

