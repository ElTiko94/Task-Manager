import json
import logging
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
