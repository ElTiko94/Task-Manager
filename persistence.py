import json
import logging
import csv
from task import Task


logger = logging.getLogger(__name__)


def save_tasks_to_json(task, path):
    """Save ``task`` hierarchy to ``path`` in JSON format."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(task.to_dict(), fh, indent=2)


def load_tasks_from_json(path):
    """Load tasks from a JSON file at ``path`` and return a ``Task``.

    If the file cannot be read or contains invalid JSON, a new ``Task('Main')``
    is returned and a warning is printed.

    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return Task.from_dict(data)
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError) as err:
        logger.warning("Failed to load tasks from %s: %s", path, err)
        print("Warning:", err)
        return Task("Main")


def _iterate_tasks(task):
    """Yield ``task`` and all of its subtasks recursively."""
    yield task
    for sub in task.get_sub_tasks():
        yield from _iterate_tasks(sub)


def save_tasks_to_csv(task, path):
    """Write the task hierarchy to ``path`` in CSV format."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Name", "Due Date", "Priority", "Completed"])
        for t in _iterate_tasks(task):
            writer.writerow(
                [
                    t.name,
                    t.due_date or "",
                    "" if t.priority is None else t.priority,
                    1 if t.completed else 0,
                ]
            )


def save_tasks_to_ics(task, path):
    """Write the task hierarchy to ``path`` as an iCalendar file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("BEGIN:VCALENDAR\n")
        fh.write("VERSION:2.0\n")
        fh.write("PRODID:-//Task Manager//EN\n")
        for t in _iterate_tasks(task):
            fh.write("BEGIN:VTODO\n")
            fh.write(f"SUMMARY:{t.name}\n")
            if t.due_date:
                dt = t.due_date.replace("-", "") + "T000000Z"
                fh.write(f"DUE:{dt}\n")
            if t.priority is not None:
                fh.write(f"PRIORITY:{t.priority}\n")
            fh.write(f"STATUS:{'COMPLETED' if t.completed else 'NEEDS-ACTION'}\n")
            fh.write("END:VTODO\n")
        fh.write("END:VCALENDAR\n")
