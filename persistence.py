import json
from task import Task


def save_tasks_to_json(task, path):
    """Save ``task`` hierarchy to ``path`` in JSON format."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(task.to_dict(), fh, indent=2)


def load_tasks_from_json(path):
    """Load tasks from a JSON file at ``path`` and return a ``Task``."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Task.from_dict(data)
