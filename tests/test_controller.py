import pytest
from helpers import load_module

task = load_module("task")
controller_mod = load_module("controller")
Task = task.Task
TaskController = controller_mod.TaskController
InvalidTaskIndexError = controller_mod.InvalidTaskIndexError


def create_controller():
    main = Task('Main')
    return TaskController(main)


def test_add_task():
    c = create_controller()
    c.add_task('A')
    assert [t.name for t in c.get_sub_tasks()] == ['A']


def test_edit_and_delete_task():
    c = create_controller()
    c.add_task('A')
    c.edit_task(0, 'B')
    assert c.get_sub_tasks()[0].name == 'B'
    c.delete_task(0)
    assert c.get_sub_tasks() == []


def test_get_task_name():
    c = create_controller()
    assert c.get_task_name() == 'Main'


def test_add_task_with_extras_and_completion():
    c = create_controller()
    c.add_task('A', due_date='2025-12-31', priority=1)
    t = c.get_sub_tasks()[0]
    assert t.due_date == '2025-12-31'
    assert t.priority == 1
    c.mark_task_completed(0)
    assert c.get_sub_tasks()[0].completed
    c.mark_task_incomplete(0)
    assert not c.get_sub_tasks()[0].completed


def test_sort_tasks_by_priority():
    c = create_controller()
    c.add_task('Low', priority=5)
    c.add_task('High', priority=1)
    c.add_task('None')
    c.sort_tasks_by_priority()
    assert [t.name for t in c.get_sub_tasks()] == ['High', 'Low', 'None']


def test_sort_tasks_by_due_date():
    c = create_controller()
    c.add_task('Later', due_date='2025-01-01')
    c.add_task('Sooner', due_date='2024-01-01')
    c.add_task('NoDue')
    c.sort_tasks_by_due_date()
    assert [t.name for t in c.get_sub_tasks()] == ['Sooner', 'Later', 'NoDue']


def test_invalid_index_operations():
    c = create_controller()
    c.add_task('Only')
    with pytest.raises(InvalidTaskIndexError):
        c.edit_task(5, 'X')
    with pytest.raises(InvalidTaskIndexError):
        c.delete_task(2)
    with pytest.raises(InvalidTaskIndexError):
        c.mark_task_completed(-1)


def test_undo_and_redo_add():
    c = create_controller()
    c.add_task('A')
    c.undo()
    assert c.get_sub_tasks() == []
    c.redo()
    assert [t.name for t in c.get_sub_tasks()] == ['A']


def test_undo_and_redo_edit():
    c = create_controller()
    c.add_task('A')
    c.edit_task(0, 'B')
    c.undo()
    assert c.get_sub_tasks()[0].name == 'A'
    c.redo()
    assert c.get_sub_tasks()[0].name == 'B'


def test_move_task_changes_order():
    c = create_controller()
    c.add_task('A')
    c.add_task('B')
    c.add_task('C')
    c.move_task(0, 2)
    assert [t.name for t in c.get_sub_tasks()] == ['B', 'C', 'A']


def test_undo_redo_move(monkeypatch=None):
    c = create_controller()
    c.add_task('A')
    c.add_task('B')
    c.move_task(0, 1)
    c.undo()
    assert [t.name for t in c.get_sub_tasks()] == ['A', 'B']
    c.redo()
    assert [t.name for t in c.get_sub_tasks()] == ['B', 'A']
