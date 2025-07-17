import json
from task import Task


def save_tasks_to_json(task, path):
    """Save ``task`` hierarchy to ``path`` in JSON format."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(task.to_dict(), fh, indent=2)


def load_tasks_from_json(path):
    """Load tasks from a JSON file at ``path`` and return a ``Task``.

    If the file is missing or contains invalid JSON, a new ``Task('Main')`` is
    returned and a warning is printed.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return Task.from_dict(data)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        print(f"Warning: Failed to load tasks from {path}: {err}")
        return Task("Main")
