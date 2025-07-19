"""
This module defines the TaskController class for managing tasks in a to-do list.

Classes:
- TaskController: Represents a controller for managing tasks.

Usage:
    This module provides the TaskController class for managing tasks in a to-do list.
    It can be used to add, edit, delete tasks, and retrieve task information.
"""
from pathlib import Path

from task import Task
import persistence


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

    def __init__(self, task, save_path=None):
        """
        Initializes a new TaskController object.

        Args:
            task (Task): The main task managed by the controller.
            save_path (str or Path, optional): Path used for automatic JSON
                persistence.  If ``None`` (default), auto-saving is disabled.
        """
        self.task = task
        self.save_path = Path(save_path) if save_path is not None else None
        # Stacks used to store undo and redo operations.  Each entry is a
        # tuple describing the operation that should be executed when popped.
        #
        # Supported operations:
        #   ('add', index, task)        -> insert ``task`` at ``index``
        #   ('delete', index, task)     -> remove task at ``index``
        #   ('setattr', index, values)  -> set attributes on task ``index``
        #   ('move', from_idx, to_idx)  -> move task from ``from_idx`` to ``to_idx``
        self._undo_stack = []
        self._redo_stack = []

    # ------------------------------------------------------------------
    def _auto_save(self):
        """Write current tasks to :pyattr:`save_path` if configured."""
        if self.save_path is not None:
            try:
                persistence.save_tasks_to_json(self.task, self.save_path)
            except Exception:
                pass

    def add_task(self, task_name, due_date=None, priority=None):
        """
        Adds a new task to the task controller.

        Args:
            task_name (str): The name of the new task to be added.
        """
        new_task = Task(task_name, due_date=due_date, priority=priority)
        self.task.add_sub_task(new_task)
        idx = len(self.task.sub_tasks) - 1
        self._undo_stack.append(("delete", idx, new_task))
        self._redo_stack.clear()
        self._auto_save()

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
        old_name = sub_tasks[task_index].name
        sub_tasks[task_index].name = new_name
        self._undo_stack.append(("setattr", task_index, {"name": old_name}))
        self._redo_stack.clear()
        self._auto_save()

    def delete_task(self, index):
        """
        Deletes a task at the specified index.

        Args:
            index (int): The index of the task to be deleted.
        """
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        removed = sub_tasks[index]
        self.task.remove_sub_task(removed)
        self._undo_stack.append(("add", index, removed))
        self._redo_stack.clear()
        self._auto_save()

    def move_task(self, old_index, new_index):
        """Move a task from ``old_index`` to ``new_index`` in the sub task list."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= old_index < len(sub_tasks):
            raise InvalidTaskIndexError(old_index)
        if not 0 <= new_index < len(sub_tasks):
            raise InvalidTaskIndexError(new_index)
        task = sub_tasks.pop(old_index)
        # ``list.insert`` appends when index >= len, which handles moves to end
        sub_tasks.insert(new_index, task)
        # push inverse for undo
        self._undo_stack.append(("move", new_index, old_index))
        self._redo_stack.clear()

    def mark_task_completed(self, index):
        """Mark the task at the given index as completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        prev = sub_tasks[index].completed
        sub_tasks[index].mark_completed()
        self._undo_stack.append(("setattr", index, {"completed": prev}))
        self._redo_stack.clear()
        self._auto_save()

    def mark_task_incomplete(self, index):
        """Mark the task at the given index as not completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        prev = sub_tasks[index].completed
        sub_tasks[index].mark_incomplete()
        self._undo_stack.append(("setattr", index, {"completed": prev}))
        self._redo_stack.clear()
        self._auto_save()

    def set_task_due_date(self, index, due_date):
        """Set the due date for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        prev = sub_tasks[index].due_date
        sub_tasks[index].set_due_date(due_date)
        self._undo_stack.append(("setattr", index, {"due_date": prev}))
        self._redo_stack.clear()
        self._auto_save()

    def set_task_priority(self, index, priority):
        """Set the priority for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        prev = sub_tasks[index].priority
        sub_tasks[index].set_priority(priority)
        self._undo_stack.append(("setattr", index, {"priority": prev}))
        self._redo_stack.clear()
        self._auto_save()


    def move_task(self, from_index, to_index):
        """Move a task from ``from_index`` to ``to_index``.

        ``to_index`` may be equal to ``len(sub_tasks)`` to move the item to the
        end of the list.  ``InvalidTaskIndexError`` is raised if either index is
        out of range.
        """
        sub_tasks = self.get_sub_tasks()
        if not 0 <= from_index < len(sub_tasks):
            raise InvalidTaskIndexError(from_index)
        if not 0 <= to_index <= len(sub_tasks):
            raise InvalidTaskIndexError(to_index)
        task = sub_tasks.pop(from_index)
        sub_tasks.insert(to_index, task)
        self._undo_stack.append(("move", to_index, from_index))
        self._redo_stack.clear()

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
        self._auto_save()

    def sort_tasks_by_due_date(self):
        """Sort the controller's sub tasks by due date (None values last)."""
        self.task.sub_tasks.sort(key=lambda t: (t.due_date is None, t.due_date))
        self._auto_save()

    # --- Undo/Redo support -------------------------------------------------

    def _apply_operation(self, operation):
        """Execute ``operation`` and return the inverse operation."""
        op_type = operation[0]
        if op_type == "add":
            index, task = operation[1], operation[2]
            self.task.sub_tasks.insert(index, task)
            return ("delete", index, task)
        if op_type == "delete":
            index, task = operation[1], operation[2]
            self.task.sub_tasks.pop(index)
            return ("add", index, task)
        if op_type == "setattr":
            index, values = operation[1], operation[2]
            sub_tasks = self.get_sub_tasks()
            if not 0 <= index < len(sub_tasks):
                raise InvalidTaskIndexError(index)
            task = sub_tasks[index]
            prev = {}
            for attr, val in values.items():
                prev[attr] = getattr(task, attr)
                setattr(task, attr, val)
            return ("setattr", index, prev)
        if op_type == "move":
            old_i, new_i = operation[1], operation[2]
            sub_tasks = self.get_sub_tasks()
            if not 0 <= old_i < len(sub_tasks):
                raise InvalidTaskIndexError(old_i)
            if not 0 <= new_i < len(sub_tasks):
                raise InvalidTaskIndexError(new_i)
            task = sub_tasks.pop(old_i)
            sub_tasks.insert(new_i, task)
            return ("move", new_i, old_i)
            from_idx, to_idx = operation[1], operation[2]
            sub_tasks = self.get_sub_tasks()
            if not 0 <= from_idx < len(sub_tasks):
                raise InvalidTaskIndexError(from_idx)
            if not 0 <= to_idx <= len(sub_tasks):
                raise InvalidTaskIndexError(to_idx)
            task = sub_tasks.pop(from_idx)
            sub_tasks.insert(to_idx, task)
            return ("move", to_idx, from_idx)
        return None

    def undo(self):
        """Undo the most recent operation, if any."""
        if not self._undo_stack:
            return
        op = self._undo_stack.pop()
        inverse = self._apply_operation(op)
        if inverse:
            self._redo_stack.append(inverse)
        self._auto_save()

    def redo(self):
        """Redo the most recently undone operation, if any."""
        if not self._redo_stack:
            return
        op = self._redo_stack.pop()
        inverse = self._apply_operation(op)
        if inverse:
            self._undo_stack.append(inverse)
        self._auto_save()
