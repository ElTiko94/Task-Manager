import csv
from helpers import load_module

task = load_module("task")
persistence_mod = load_module("persistence")
Task = task.Task
save_tasks_to_csv = persistence_mod.save_tasks_to_csv
save_tasks_to_ics = persistence_mod.save_tasks_to_ics
load_tasks_from_csv = persistence_mod.load_tasks_from_csv
load_tasks_from_ics = persistence_mod.load_tasks_from_ics


def build_task_tree():
    main = Task('Main', due_date='2025-12-31', priority=1)
    sub1 = Task('Sub1', completed=True)
    sub2 = Task('Sub2', due_date='2026-01-01')
    main.add_sub_task(sub1)
    main.add_sub_task(sub2)
    return main


def build_deep_task_tree():
    """Return a task tree with multiple nesting levels."""
    main = build_task_tree()
    deep = Task("SubSub1")
    deeper = Task("Deep")
    deep.add_sub_task(deeper)
    main.get_sub_tasks()[0].add_sub_task(deep)  # attach under Sub1
    return main


def test_csv_export(tmp_path):
    task = build_task_tree()
    path = tmp_path / 'tasks.csv'
    save_tasks_to_csv(task, path)
    with open(path, newline='', encoding='utf-8') as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ['Name', 'Due Date', 'Priority', 'Completed', 'Depth']
    assert rows[1] == ['Main', '2025-12-31', '1', '0', '0']
    assert rows[2] == ['Sub1', '', '', '1', '1']
    assert rows[3] == ['Sub2', '2026-01-01', '', '0', '1']


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


def test_csv_round_trip(tmp_path):
    task = build_task_tree()
    path = tmp_path / 'round.csv'
    save_tasks_to_csv(task, path)
    loaded = load_tasks_from_csv(path)
    assert loaded.name == 'Main'
    names = [t.name for t in loaded.get_sub_tasks()]
    assert names == ['Sub1', 'Sub2']
    assert loaded.due_date == '2025-12-31'
    assert loaded.priority == 1
    assert loaded.get_sub_tasks()[0].completed


def test_csv_round_trip_nested(tmp_path):
    """A tree with nested subtasks should round-trip through CSV."""
    task = build_deep_task_tree()
    path = tmp_path / "nested.csv"
    save_tasks_to_csv(task, path)
    loaded = load_tasks_from_csv(path)
    assert loaded.to_dict() == task.to_dict()


def test_ics_round_trip(tmp_path):
    task = build_task_tree()
    path = tmp_path / 'round.ics'
    save_tasks_to_ics(task, path)
    loaded = load_tasks_from_ics(path)
    assert loaded.name == 'Main'
    names = {t.name for t in loaded.get_sub_tasks()}
    assert names == {'Sub1', 'Sub2'}
    assert loaded.due_date == '2025-12-31'
    assert loaded.priority == 1


