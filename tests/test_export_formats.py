import os, sys
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from task import Task
from persistence import save_tasks_to_csv, save_tasks_to_ics


def build_task_tree():
    main = Task('Main', due_date='2025-12-31', priority=1)
    sub1 = Task('Sub1', completed=True)
    sub2 = Task('Sub2', due_date='2026-01-01')
    main.add_sub_task(sub1)
    main.add_sub_task(sub2)
    return main


def test_csv_export(tmp_path):
    task = build_task_tree()
    path = tmp_path / 'tasks.csv'
    save_tasks_to_csv(task, path)
    with open(path, newline='', encoding='utf-8') as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ['Name', 'Due Date', 'Priority', 'Completed']
    assert rows[1] == ['Main', '2025-12-31', '1', '0']
    assert rows[2] == ['Sub1', '', '', '1']
    assert rows[3] == ['Sub2', '2026-01-01', '', '0']


def test_ics_export(tmp_path):
    task = build_task_tree()
    path = tmp_path / 'tasks.ics'
    save_tasks_to_ics(task, path)
    text = path.read_text(encoding='utf-8')
    assert 'BEGIN:VCALENDAR' in text
    assert 'END:VCALENDAR' in text
    assert 'SUMMARY:Main' in text
    assert 'SUMMARY:Sub1' in text
    assert 'SUMMARY:Sub2' in text
    assert 'DUE:20251231T000000Z' in text
