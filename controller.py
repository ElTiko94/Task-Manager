"""
This module defines the TaskController class for managing tasks in a to-do list.

Classes:
- TaskController: Represents a controller for managing tasks.

Usage:
    This module provides the TaskController class for managing tasks in a to-do list.
    It can be used to add, edit, delete tasks, and retrieve task information.
"""
from task import Task

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
    """

    def __init__(self, task):
        """
        Initializes a new TaskController object.

        Args:
            task (Task): The main task managed by the controller.
        """
        self.task = task

    def add_task(self, task_name):
        """
        Adds a new task to the task controller.

        Args:
            task_name (str): The name of the new task to be added.
        """
        new_task = Task(task_name)
        self.task.add_sub_task(new_task)

    def edit_task(self, task_index, new_name):
        """
        Edits the name of a task at the specified index.

        Args:
            task_index (int): The index of the task to be edited.
            new_name (str): The new name for the task.
        """
        task = self.task.get_sub_tasks()[task_index]
        task.name = new_name

    def delete_task(self, index):
        """
        Deletes a task at the specified index.

        Args:
            index (int): The index of the task to be deleted.
        """
        self.task.remove_sub_task(self.get_sub_tasks()[index])

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
