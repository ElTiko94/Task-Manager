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
        logger.warning("Warning: %s", err)
        return Task("Main")


def _iterate_tasks(task, depth=0):
    """Yield ``(task, depth)`` for ``task`` and all of its subtasks recursively."""
    yield task, depth
    for sub in task.get_sub_tasks():
        yield from _iterate_tasks(sub, depth + 1)


def save_tasks_to_csv(task, path):
    """Write the task hierarchy to ``path`` in CSV format."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Name", "Due Date", "Priority", "Completed", "Depth"])
        for t, depth in _iterate_tasks(task):
            writer.writerow(
                [
                    t.name,
                    t.due_date or "",
                    "" if t.priority is None else t.priority,
                    1 if t.completed else 0,
                    depth,
                ]
            )


def save_tasks_to_ics(task, path):
    """Write the task hierarchy to ``path`` as an iCalendar file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("BEGIN:VCALENDAR\n")
        fh.write("VERSION:2.0\n")
        fh.write("PRODID:-//Task Manager//EN\n")
        for t, _ in _iterate_tasks(task):
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


def load_tasks_from_csv(path):
    """Load tasks from a CSV file at ``path`` and return a ``Task``.

    The first row after the header becomes the root task and remaining rows
    become its direct subtasks.  If loading fails, a new ``Task('Main')`` is
    returned and a warning is printed.
    """
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            rows = list(reader)
        if not rows:
            return Task("Main")

        if header and "Depth" in header:
            depth_index = header.index("Depth")
        else:
            depth_index = None

        if depth_index is None:
            # Legacy format without depth information
            root_row = rows[0]
            name, due, prio, completed = root_row[:4]
            priority = int(prio) if prio else None
            completed = bool(int(completed)) if completed else False
            root = Task(name, due_date=due or None, priority=priority, completed=completed)
            for row in rows[1:]:
                try:
                    r_name, r_due, r_prio, r_comp = row[:4]
                except ValueError:
                    continue
                r_priority = int(r_prio) if r_prio else None
                r_completed = bool(int(r_comp)) if r_comp else False
                root.add_sub_task(
                    Task(r_name, due_date=r_due or None, priority=r_priority, completed=r_completed)
                )
            return root

        stack = []
        root = None
        for row in rows:
            try:
                name, due, prio, comp = row[:4]
                depth = int(row[depth_index]) if len(row) > depth_index and row[depth_index] != "" else 0
            except (ValueError, IndexError):
                continue
            priority = int(prio) if prio else None
            completed = bool(int(comp)) if comp else False
            task = Task(name, due_date=due or None, priority=priority, completed=completed)
            if depth == 0:
                root = task
                stack = [task]
                continue
            while len(stack) > depth:
                stack.pop()
            parent = stack[-1] if stack else None
            if parent is None:
                root = task
                stack = [task]
            else:
                parent.add_sub_task(task)
                stack.append(task)
        return root if root is not None else Task("Main")
    except Exception as err:
        logger.warning("Failed to load tasks from %s: %s", path, err)
        logger.warning("Warning: %s", err)
        return Task("Main")


def load_tasks_from_ics(path):
    """Load tasks from an iCalendar file written by :py:meth:`save_tasks_to_ics`."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh]
        tasks = []
        current = None
        for line in lines:
            if line == "BEGIN:VTODO":
                current = {}
            elif line == "END:VTODO":
                if current is not None:
                    name = current.get("SUMMARY", "Unnamed")
                    due = current.get("DUE")
                    if due and len(due) >= 8:
                        due = f"{due[0:4]}-{due[4:6]}-{due[6:8]}"
                    prio = current.get("PRIORITY")
                    try:
                        prio_val = int(prio) if prio else None
                    except ValueError:
                        prio_val = None
                    status = current.get("STATUS", "NEEDS-ACTION").upper()
                    completed = status == "COMPLETED"
                    tasks.append(Task(name, due_date=due or None, priority=prio_val, completed=completed))
                current = None
            elif current is not None and ":" in line:
                key, value = line.split(":", 1)
                current[key] = value

        if not tasks:
            return Task("Main")
        root = tasks[0]
        for t in tasks[1:]:
            root.add_sub_task(t)
        return root
    except Exception as err:
        logger.warning("Failed to load tasks from %s: %s", path, err)
        logger.warning("Warning: %s", err)
        return Task("Main")
