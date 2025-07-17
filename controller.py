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
        """
        Initializes a new TaskController object.

        Args:
            task (Task): The main task managed by the controller.
        """
        self.task = task

    def add_task(self, task_name, due_date=None, priority=None):
        """
        Adds a new task to the task controller.

        Args:
            task_name (str): The name of the new task to be added.
        """
        new_task = Task(task_name, due_date=due_date, priority=priority)
        self.task.add_sub_task(new_task)

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
        sub_tasks[task_index].name = new_name

    def delete_task(self, index):
        """
        Deletes a task at the specified index.

        Args:
            index (int): The index of the task to be deleted.
        """
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        self.task.remove_sub_task(sub_tasks[index])

    def mark_task_completed(self, index):
        """Mark the task at the given index as completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        sub_tasks[index].mark_completed()

    def mark_task_incomplete(self, index):
        """Mark the task at the given index as not completed."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        sub_tasks[index].mark_incomplete()

    def set_task_due_date(self, index, due_date):
        """Set the due date for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        sub_tasks[index].set_due_date(due_date)

    def set_task_priority(self, index, priority):
        """Set the priority for a task at the given index."""
        sub_tasks = self.get_sub_tasks()
        if not 0 <= index < len(sub_tasks):
            raise InvalidTaskIndexError(index)
        sub_tasks[index].set_priority(priority)

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
