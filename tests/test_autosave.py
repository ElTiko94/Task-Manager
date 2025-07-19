import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import persistence
from controller import TaskController
from task import Task


def test_add_task_autosaves(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    called = {}

    def fake_save(task, file_path):
        called['task'] = task
        called['path'] = file_path

    monkeypatch.setattr(persistence, "save_tasks_to_json", fake_save)
    controller = TaskController(Task("Main"), save_path=path)
    controller.add_task("A")
    assert called['task'] is controller.task
    assert called['path'] == path


def test_move_task_autosaves(tmp_path, monkeypatch):
    path = tmp_path / "tasks.json"
    controller = TaskController(Task("Main"), save_path=path)
    controller.add_task("A")
    controller.add_task("B")

    called = {}

    def fake_save(task, file_path):
        called['task'] = task
        called['path'] = file_path

    monkeypatch.setattr(persistence, "save_tasks_to_json", fake_save)
    controller.move_task(0, 1)
    assert called['task'] is controller.task
    assert called['path'] == path
