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

    def __init__(self, name, sub_tasks=None):
        """
        Initializes a new Task object.

        Args:
            name (str): The name of the task.
            sub_tasks (list of Task, optional): A list of sub-tasks associated with the task.
        """
        self.name = name
        self.sub_tasks = sub_tasks if sub_tasks is not None else []

    def __str__(self):
        """
        Returns a string representation of the task.

        Returns:
            str: A string representation of the task, including its name and sub-tasks.
        """
        return self.name +" {" +self.prt_sbtsk() +"}" if self.prt_sbtsk() is not None else self.name

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

    def prt_sbtsk(self):
        """
        Returns a string representation of the sub-tasks of the task.

        Returns:
            str: A string representation of the sub-tasks of the task.
        """
        output = ""
        for task in self.sub_tasks:
            if task.sub_tasks != []:
                output += " " + task.name + " {" + task.prt_sbtsk() + "}"
            else:
                output += " " + task.name + ", "
        return output
