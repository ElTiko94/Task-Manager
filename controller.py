"""
This module defines the TaskController class for managing tasks in a to-do list.

Classes:
- TaskController: Represents a controller for managing tasks.

Usage:
    This module provides the TaskController class for managing tasks in a to-do list.
    It can be used to add, edit, delete tasks, and retrieve task information.
"""
from task import Task


class InvalidTaskIndexError(IndexError):
    """Raised when a provided task index does not exist."""


class TaskController:
    """
    Represents a controller for managing tasks in a to-do list.

    Attributes:
        task (Task): The main task managed by the controller.

    Methods:
        __init__: Initializes a new TaskController object with a given task.
        add_task: Adds a new task to the task controller.
        edit_task: Edits the name of a task at the specified index.
        delete_task: Deletes a task at the specified index.
        get_task_name: Returns the name of the task.
        get_sub_tasks: Returns the list of sub-tasks associated with the task.
        sort_tasks_by_priority: Sort tasks by their priority value.
    """

    def __init__(self, task):
        """Initialize a new TaskController object."""
        self.task = task
        self.undo_stack = []
        self.redo_stack = []

    # --- internal helpers -------------------------------------------------

    def _apply(self, op, inverse=False):
        """Apply ``op`` and optionally return the inverse operation."""
        action = op.get("action")
        if action == "add":
            idx = op["index"]
            task = op["task"]
            self.task.sub_tasks.insert(idx, task)
            if inverse:
                return {"action": "delete", "index": idx, "task": task}
        elif action == "delete":
            idx = op["index"]
            task = self.task.sub_tasks.pop(idx)
            if inverse:
                return {"action": "add", "index": idx, "task": task}
        elif action == "set":
            task = op["task"]
            values = op["values"]
            inv = {}
            for attr, val in values.items():
                inv[attr] = getattr(task, attr)
                setattr(task, attr, val)
            if inverse:
                return {"action": "set", "task": task, "values": inv}


    def add_task(self, task_name, due_date=None, priority=None):
        """
        Adds a new task to the task controller.

        Args:
            task_name (str): The name of the new task to be added.
        """
        new_task = Task(task_name, due_date=due_date, priority=priority)
        self.task.add_sub_task(new_task)
        idx = len(self.task.sub_tasks) - 1
        self.undo_stack.append({"action": "delete", "index": idx, "task": new_task})
        self.redo_stack.clear()

    def edit_task(self, task_index, new_name):
        """
        Edits the name of a task at the specified index.

        Args:
            task_index (int): The index of the task to be edited.
            new_name (str): The new name for the task.
        """
        sub_tasks = self.get_sub_tasks()
        if not 0 <= task_index < len(sub_tasks):
            raise InvalidTaskIndexError(task_index)
        task = sub_tasks[task_index]
        old = task.name
        task.name = new_name
        self.undo_stack.append({"action": "set", "task": task, "values": {"name": old}})
        self.redo_stack.clear()

    def delete_task(self, index):
        """
        Deletes a task at the specified index.

        Args:
            index (int): The index of the task to be deleted.
        """
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        task = sub_tasks[index]
        self.task.remove_sub_task(task)
        self.undo_stack.append({"action": "add", "index": index, "task": task})
        self.redo_stack.clear()

    def mark_task_completed(self, index):
        """Mark the task at the given index as completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        task = sub_tasks[index]
        prev = task.completed
        task.mark_completed()
        self.undo_stack.append({"action": "set", "task": task, "values": {"completed": prev}})
        self.redo_stack.clear()

    def mark_task_incomplete(self, index):
        """Mark the task at the given index as not completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        task = sub_tasks[index]
        prev = task.completed
        task.mark_incomplete()
        self.undo_stack.append({"action": "set", "task": task, "values": {"completed": prev}})
        self.redo_stack.clear()

    def set_task_due_date(self, index, due_date):
        """Set the due date for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        task = sub_tasks[index]
        prev = task.due_date
        task.set_due_date(due_date)
        self.undo_stack.append({"action": "set", "task": task, "values": {"due_date": prev}})
        self.redo_stack.clear()

    def set_task_priority(self, index, priority):
        """Set the priority for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        task = sub_tasks[index]
        prev = task.priority
        task.set_priority(priority)
        self.undo_stack.append({"action": "set", "task": task, "values": {"priority": prev}})
        self.redo_stack.clear()

    def get_task_name(self):
        """
        Returns the name of the task.

        Returns:
            str: The name of the task.
        """
        return self.task.name

    def get_sub_tasks(self):
        """
        Returns the list of sub-tasks associated with the task.

        Returns:
            list of Task: The list of sub-tasks associated with the task.
        """
        return self.task.get_sub_tasks()

    def sort_tasks_by_priority(self):
        """Sort the controller's sub tasks by priority (None values last)."""
        self.task.sub_tasks.sort(key=lambda t: (t.priority is None, t.priority))

    def sort_tasks_by_due_date(self):
        """Sort the controller's sub tasks by due date (None values last)."""
        self.task.sub_tasks.sort(key=lambda t: (t.due_date is None, t.due_date))

    # --- history ---------------------------------------------------------

    def undo(self):
        """Undo the most recent operation if possible."""
        if not self.undo_stack:
            return
        op = self.undo_stack.pop()
        redo = self._apply(op, inverse=True)
        self.redo_stack.append(redo)

    def redo(self):
        """Redo the most recently undone operation if possible."""
        if not self.redo_stack:
            return
        op = self.redo_stack.pop()
        undo = self._apply(op, inverse=True)
        self.undo_stack.append(undo)
