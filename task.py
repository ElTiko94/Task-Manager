"""
This module defines the Task class representing a task in a to-do list.

Classes:
- Task: Represents a task with a name and optional sub-tasks.

Usage:
    This module provides the Task class for managing tasks in a to-do list.
"""
class Task:
    """
    Represents a task in the to-do list.

    Attributes:
        name (str): The name of the task.
        sub_tasks (list of Task, optional): A list of sub-tasks associated with the task.

    Methods:
        __init__:
            Initializes a new Task object with a given name and optional sub-tasks.

        __str__:
            Returns a string representation of the task, including its name and sub-tasks.

        add_sub_task:
            Adds a sub-task to the current task.

        remove_sub_task:
            Removes a sub-task from the current task.

        get_sub_tasks:
            Returns the list of sub-tasks associated with the task.

        prt_sbtsk:
            Returns a string representation of the sub-tasks of the task.
    """

    def __init__(self, name, sub_tasks=None, due_date=None, priority=None, completed=False):
        """
        Initializes a new Task object.

        Args:
            name (str): The name of the task.
            sub_tasks (list of Task, optional): A list of sub-tasks associated with the task.
            due_date (str, optional): Optional due date for the task.
            priority (int, optional): Optional priority level for the task.
            completed (bool, optional): Completion status of the task.
        """
        self.name = name
        self.sub_tasks = sub_tasks if sub_tasks is not None else []
        self.due_date = due_date
        self.priority = priority
        self.completed = completed

    def __str__(self):
        """
        Returns a string representation of the task.

        Returns:
            str: A string representation of the task, including its name and sub-tasks.
        """
        name = self.name
        if self.completed:
            name += " (Completed)"
        if self.sub_tasks:
            return f"{name} {{{self.prt_sbtsk()}}}"
        return name

    def add_sub_task(self, task):
        """
        Adds a sub-task to the current task.

        Args:
            task (Task): The sub-task to add to the current task.
        """
        self.sub_tasks.append(task)

    def remove_sub_task(self, task):
        """
        Removes a sub-task from the current task.

        Args:
            task (Task): The sub-task to remove from the current task.
        """
        self.sub_tasks.remove(task)

    def get_sub_tasks(self):
        """
        Returns the list of sub-tasks associated with the task.

        Returns:
            list of Task: The list of sub-tasks associated with the task.
        """
        return self.sub_tasks

    def set_due_date(self, due_date):
        """Set the due date for the task."""
        self.due_date = due_date

    def set_priority(self, priority):
        """Set the priority for the task."""
        self.priority = priority

    def mark_completed(self):
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self):
        """Mark this task as not completed."""
        self.completed = False

    def prt_sbtsk(self):
        """
        Returns a string representation of the sub-tasks of the task.

        Returns:
            str: A string representation of the sub-tasks of the task.
        """
        names = []
        for task in self.sub_tasks:
            if task.sub_tasks:
                names.append(f"{task.name} {{{task.prt_sbtsk()}}}")
            else:
                names.append(task.name)
        return ", ".join(names)
