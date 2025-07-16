"""
This module defines a Window class representing the main application window for a to-do list.

Classes:
- Window: Represents the main application window for managing tasks.

Usage:
    This module provides the Window class for managing the main application window of a to-do list.
"""

import tkinter as tk
from task import Task
from controller import TaskController

class Window:
    """
    Represents the main application window for managing tasks.

    Attributes:
        root: The root tkinter window.
        task_list: The list of tasks associated with the window.
        controller: The task controller managing the tasks.
        name: The name of the task associated with the window.

    Methods:
        __init__: Initializes a new Window object.
        view_subtasks: Opens a new window to view the sub-tasks of a selected task.
        delete_task: Deletes the selected task from the task controller.
        add_task: Displays a dialog to add a new task.
        create_task_button: Creates a new task based on the entered name.
        edit_task: Displays a dialog to edit the selected task.
        confirm_edit: Confirms the edit of a task and updates the listbox.
        refresh_window: Refreshes the listbox displaying the tasks.
    """
    def __init__(self, root, controller):
        """
        Initializes a new Window object.

        Args:
            root: The root tkinter window.
            controller: The task controller managing the tasks.
        """
        self.root = root
        self.task_list = controller.get_sub_tasks()
        self.controller = controller
        self.name = controller.get_task_name()


        tk.Label(self.root, text=f"Sub-tasks for {self.name}: ").pack()
        add_task_button = tk.Button(self.root, text="Add Task", command= self.add_task)
        add_task_button.pack()

        sort_btn = tk.Button(self.root, text="Sort by Priority", command=self.sort_tasks_by_priority)
        sort_btn.pack()

        self.listbox = tk.Listbox(self.root)
        self.listbox.pack()

        view_subtasks_btn = tk.Button(self.root, text="View Subtasks", command= self.view_subtasks)
        view_subtasks_btn.pack()

        edit_button = tk.Button(self.root, text="Edit", command= self.edit_task)
        edit_button.pack()

        dlt_btn = tk.Button(self.root, text="Delete", command=self.delete_task)
        dlt_btn.pack()

        self.root.resizable(True, True)
        self.refresh_window()

    # ...
    def view_subtasks(self):
        """
        Opens a new window to view the sub-tasks of a selected task.
        """
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_task = self.controller.get_sub_tasks()[selected_index[0]]
        r = tk.Tk()
        Window(r, TaskController(selected_task))

    def delete_task(self):
        """
        Deletes the selected task from the task controller.
        """
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        self.controller.delete_task(selected_index[0])
        self.refresh_window()

    # Functions
    def add_task(self):
        """Displays a dialog to add a new task."""
        task_name_field = tk.StringVar()
        due_date_field = tk.StringVar()
        priority_field = tk.StringVar()
        completed_var = tk.IntVar()

        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        due_date_entry = tk.Entry(self.root, textvariable=due_date_field)
        priority_entry = tk.Entry(self.root, textvariable=priority_field)
        completed_check = tk.Checkbutton(self.root, text="Completed", variable=completed_var)

        task_entry.pack()
        due_date_entry.pack()
        priority_entry.pack()
        completed_check.pack()

        confirm_button = tk.Button(
            self.root,
            text="Confirm",
            command=lambda: self.create_task_button(
                task_entry,
                due_date_entry,
                priority_entry,
                completed_var,
                completed_check,
                confirm_button,
            ),
        )
        confirm_button.pack()

    def create_task_button(
        self,
        task_entry,
        due_date_entry,
        priority_entry,
        completed_var,
        completed_check,
        confirm_button,
    ):
        """
        Creates a new task based on the entered name.

        Args:
            task_entry (tk.Entry): The entry field containing the task name.
            confirm_button (tk.Button): The confirm button for adding the task.
        """
        task_name = task_entry.get()
        due_date = due_date_entry.get()
        priority_text = priority_entry.get()
        priority = int(priority_text) if priority_text else None
        completed = bool(completed_var.get())

        task_entry.destroy()
        due_date_entry.destroy()
        priority_entry.destroy()
        completed_check.destroy()
        confirm_button.destroy()

        self.controller.add_task(task_name, due_date=due_date or None, priority=priority)
        if completed:
            idx = len(self.controller.get_sub_tasks()) - 1
            self.controller.mark_task_completed(idx)
        self.refresh_window()

    def edit_task(self):
        """Displays a dialog to edit the selected task."""
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        task = self.controller.get_sub_tasks()[selected_index[0]]

        task_name_field = tk.StringVar()
        due_date_field = tk.StringVar()
        priority_field = tk.StringVar()
        completed_var = tk.IntVar()

        task_name_field.set(task.name)
        if task.due_date:
            due_date_field.set(task.due_date)
        if task.priority is not None:
            priority_field.set(str(task.priority))
        completed_var.set(1 if task.completed else 0)

        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        due_date_entry = tk.Entry(self.root, textvariable=due_date_field)
        priority_entry = tk.Entry(self.root, textvariable=priority_field)
        completed_check = tk.Checkbutton(self.root, text="Completed", variable=completed_var)

        task_entry.pack()
        due_date_entry.pack()
        priority_entry.pack()
        completed_check.pack()

        confirm_button = tk.Button(
            self.root,
            text="Confirm",
            command=lambda: self.confirm_edit(
                task_entry,
                due_date_entry,
                priority_entry,
                completed_var,
                completed_check,
                selected_index,
                confirm_button,
            ),
        )
        confirm_button.pack()

    # Function to handle task editing and updating the listbox
    def confirm_edit(
        self,
        task_name_field,
        due_date_entry,
        priority_entry,
        completed_var,
        completed_check,
        selected_index,
        confirm_button,
    ):
        """
        Confirms the edit of a task and updates the listbox.

        Args:
            task_name_field (tk.Entry): The entry widget containing the new task name.
            selected_index (int): The index of the task being edited.
            confirm_button (tk.Button): The confirm button for editing the task.
        """
        new_name = task_name_field.get()
        new_due = due_date_entry.get()
        priority_text = priority_entry.get()
        new_priority = int(priority_text) if priority_text else None
        completed = bool(completed_var.get())

        task_name_field.destroy()
        due_date_entry.destroy()
        priority_entry.destroy()
        completed_check.destroy()
        confirm_button.destroy()

        idx = selected_index[0]
        self.controller.edit_task(idx, new_name)
        self.controller.set_task_due_date(idx, new_due or None)
        self.controller.set_task_priority(idx, new_priority)
        if completed:
            self.controller.mark_task_completed(idx)
        else:
            self.controller.mark_task_incomplete(idx)
        self.refresh_window()

    def sort_tasks_by_priority(self):
        """Sort tasks by priority using the controller and refresh the view."""
        self.controller.sort_tasks_by_priority()
        self.refresh_window()

    def refresh_window(self):
        """Refreshes the listbox displaying the tasks."""
        self.listbox.delete(0, tk.END)
        for task in self.controller.get_sub_tasks():
            if isinstance(task, Task):
                display = str(task)
                if getattr(task, "due_date", None):
                    display += f" - Due: {task.due_date}"
                if getattr(task, "priority", None) is not None:
                    display += f" - Priority: {task.priority}"
                self.listbox.insert(tk.END, display)
