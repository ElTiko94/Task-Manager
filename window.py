"""
This module defines a Window class representing the main application window for a to-do list.

Classes:
- Window: Represents the main application window for managing tasks.

Usage:
    This module provides the Window class for managing the main application window of a to-do list.
"""

import tkinter as tk
import tkinter.ttk as ttk

if not hasattr(ttk, "Listbox"):
    ttk.Listbox = tk.Listbox
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


        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            self.main_frame, text=f"Sub-tasks for {self.name}: "
        ).grid(row=0, column=0, columnspan=3, pady=2)

        add_task_button = ttk.Button(
            self.main_frame, text="Add Task", command=self.add_task
        )
        add_task_button.grid(row=1, column=0, sticky="ew", padx=2)

        sort_btn = ttk.Button(
            self.main_frame, text="Sort by Priority", command=self.sort_tasks_by_priority
        )
        sort_btn.grid(row=1, column=1, sticky="ew", padx=2)

        sort_due_btn = ttk.Button(
            self.main_frame, text="Sort by Due Date", command=self.sort_tasks_by_due_date
        )
        sort_due_btn.grid(row=1, column=2, sticky="ew", padx=2)

        self.listbox = ttk.Listbox(self.main_frame)
        self.listbox.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=5)

        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient="vertical", command=self.listbox.yview
        )
        self.scrollbar.grid(row=2, column=3, sticky="ns")
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        # Bind double-click on a task to open its subtasks
        self.listbox.bind("<Double-Button-1>", lambda e: self.view_subtasks())

        view_subtasks_btn = ttk.Button(
            self.main_frame, text="View Subtasks", command=self.view_subtasks
        )
        view_subtasks_btn.grid(row=3, column=0, sticky="ew", padx=2, pady=2)

        edit_button = ttk.Button(
            self.main_frame, text="Edit", command=self.edit_task
        )
        edit_button.grid(row=3, column=1, sticky="ew", padx=2)

        dlt_btn = ttk.Button(
            self.main_frame, text="Delete", command=self.delete_task
        )
        dlt_btn.grid(row=3, column=2, sticky="ew", padx=2)

        self.root.resizable(True, True)
        self.refresh_window()

    def view_subtasks(self):
        """
        Opens a new window to view the sub-tasks of a selected task.
        """
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_task = self.controller.get_sub_tasks()[selected_index[0]]
        r = tk.Toplevel(self.root)
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

    def add_task(self):
        """Displays a dialog to add a new task using a Toplevel window."""
        dialog = tk.Toplevel(self.root)

        task_name_field = tk.StringVar()
        due_date_field = tk.StringVar()
        priority_field = tk.StringVar()
        completed_var = tk.IntVar()

        form = ttk.Frame(dialog)
        form.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(form, text="Task Name:").grid(row=0, column=0, sticky="e")
        task_entry = ttk.Entry(form, textvariable=task_name_field)
        task_entry.grid(row=0, column=1)
        ttk.Label(form, text="Due Date:").grid(row=1, column=0, sticky="e")
        due_date_entry = ttk.Entry(form, textvariable=due_date_field)
        due_date_entry.grid(row=1, column=1)
        ttk.Label(form, text="Priority:").grid(row=2, column=0, sticky="e")
        priority_entry = ttk.Entry(form, textvariable=priority_field)
        priority_entry.grid(row=2, column=1)
        completed_check = tk.Checkbutton(form, text="Completed", variable=completed_var)
        completed_check.grid(row=3, column=0, columnspan=2)

        confirm_button = ttk.Button(
            form,
            text="Confirm",
            command=lambda: self.create_task_button(
                task_entry,
                due_date_entry,
                priority_entry,
                completed_var,
                completed_check,
                confirm_button,
                dialog,
            ),
        )
        confirm_button.grid(row=4, column=0, columnspan=2, pady=2)

    def create_task_button(
        self,
        task_entry,
        due_date_entry,
        priority_entry,
        completed_var,
        completed_check,
        confirm_button,
        dialog=None,
    ):
        """
        Creates a new task based on the entered name.

        Args:
            task_entry (ttk.Entry): The entry field containing the task name.
            confirm_button (ttk.Button): The confirm button for adding the task.
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

        if dialog is not None:
            dialog.destroy()

        self.controller.add_task(task_name, due_date=due_date or None, priority=priority)
        if completed:
            idx = len(self.controller.get_sub_tasks()) - 1
            self.controller.mark_task_completed(idx)
        self.refresh_window()

    def edit_task(self):
        """Displays a dialog to edit the selected task using a Toplevel."""
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        task = self.controller.get_sub_tasks()[selected_index[0]]

        dialog = tk.Toplevel(self.root)

        task_name_field = tk.StringVar()
        due_date_field = tk.StringVar()
        priority_field = tk.StringVar()
        completed_var = tk.IntVar()

        task_name_field.set(task.name)
        if task.due_date:
            due_date_field.set(str(task.due_date))
        if task.priority is not None:
            priority_field.set(str(task.priority))
        completed_var.set(1 if task.completed else 0)

        form = ttk.Frame(dialog)
        form.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(form, text="Task Name:").grid(row=0, column=0, sticky="e")
        task_entry = ttk.Entry(form, textvariable=task_name_field)
        task_entry.grid(row=0, column=1)
        ttk.Label(form, text="Due Date:").grid(row=1, column=0, sticky="e")
        due_date_entry = ttk.Entry(form, textvariable=due_date_field)
        due_date_entry.grid(row=1, column=1)
        ttk.Label(form, text="Priority:").grid(row=2, column=0, sticky="e")
        priority_entry = ttk.Entry(form, textvariable=priority_field)
        priority_entry.grid(row=2, column=1)
        completed_check = tk.Checkbutton(form, text="Completed", variable=completed_var)
        completed_check.grid(row=3, column=0, columnspan=2)

        confirm_button = ttk.Button(
            form,
            text="Confirm",
            command=lambda: self.confirm_edit(
                task_entry,
                due_date_entry,
                priority_entry,
                completed_var,
                completed_check,
                selected_index,
                confirm_button,
                dialog,
            ),
        )
        confirm_button.grid(row=4, column=0, columnspan=2, pady=2)

    def confirm_edit(
        self,
        task_name_field,
        due_date_entry,
        priority_entry,
        completed_var,
        completed_check,
        selected_index,
        confirm_button,
        dialog=None,
    ):
        """
        Confirms the edit of a task and updates the listbox.

        Args:
            task_name_field (ttk.Entry): The entry widget containing the new task name.
            selected_index (int): The index of the task being edited.
            confirm_button (ttk.Button): The confirm button for editing the task.
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

        if dialog is not None:
            dialog.destroy()

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

    def sort_tasks_by_due_date(self):
        """Sort tasks by due date using the controller and refresh the view."""
        self.controller.sort_tasks_by_due_date()
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
