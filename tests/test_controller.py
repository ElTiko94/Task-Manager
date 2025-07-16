import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from task import Task
from controller import TaskController


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
