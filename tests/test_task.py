import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from task import Task


def test_task_str_without_subtasks():
    task = Task('Task1')
    assert str(task) == 'Task1'


def test_add_and_remove_subtask():
    task = Task('Main')
    sub = Task('Sub')
    task.add_sub_task(sub)
    assert task.get_sub_tasks() == [sub]
    task.remove_sub_task(sub)
    assert task.get_sub_tasks() == []


def test_prt_sbtsk_and_str_with_subtasks():
    main = Task('Main')
    sub1 = Task('Sub1')
    sub2 = Task('Sub2')
    sub1.add_sub_task(Task('SubSub'))
    main.add_sub_task(sub1)
    main.add_sub_task(sub2)
    # prt_sbtsk should include nested representation
    assert main.prt_sbtsk() == 'Sub1 {SubSub}, Sub2'
    assert str(main) == 'Main {Sub1 {SubSub}, Sub2}'


def test_task_due_date_priority_and_completion():
    task = Task('Todo', due_date='2025-12-31', priority=2)
    assert task.due_date == '2025-12-31'
    assert task.priority == 2
    assert not task.completed
    task.mark_completed()
    assert task.completed
    task.mark_incomplete()
    assert not task.completed
