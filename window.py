"""
This module defines a Window class representing the main application window for a to-do list.

Classes:
- Window: Represents the main application window for managing tasks.

Usage:
    This module provides the Window class for managing the main application window of a to-do list.
"""

import tkinter as tk
import tkinter.ttk as ttk

import calendar as _calendar
import datetime as _datetime

try:
    from tkcalendar import DateEntry
except ModuleNotFoundError:  # Fallback when tkcalendar is unavailable
    class _SimpleCalendar(ttk.Frame):
        """Very small calendar widget with month navigation."""

        def __init__(self, master, variable, close_cb):
            super().__init__(master)
            self._var = variable
            self._close_cb = close_cb
            today = _datetime.date.today()
            self._year = today.year
            self._month = today.month

            # Header with navigation
            header = ttk.Frame(self)
            header.grid(row=0, column=0, columnspan=7)
            ttk.Button(header, text="<", command=self._prev_month).grid(row=0, column=0)
            self._title = ttk.Label(header)
            self._title.grid(row=0, column=1, columnspan=5)
            ttk.Button(header, text=">", command=self._next_month).grid(row=0, column=6)

            self._days = ttk.Frame(self)
            self._days.grid(row=1, column=0, columnspan=7)
            self._build_days()

        def _build_days(self):
            for w in self._days.winfo_children():
                w.destroy()

            self._title.config(text=f"{_calendar.month_name[self._month]} {self._year}")
            for i, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                ttk.Label(self._days, text=name).grid(row=0, column=i)

            cal = _calendar.Calendar()
            row = 1
            for week in cal.monthdayscalendar(self._year, self._month):
                for col, day in enumerate(week):
                    if day == 0:
                        ttk.Label(self._days, text="").grid(row=row, column=col)
                    else:
                        btn = ttk.Button(
                            self._days,
                            text=str(day),
                            width=2,
                            command=lambda d=day: self._select_day(d),
                        )
                        btn.grid(row=row, column=col)
                row += 1

        def _select_day(self, day):
            self._var.set(f"{self._year:04d}-{self._month:02d}-{day:02d}")
            self._close_cb()

        def _prev_month(self):
            if self._month == 1:
                self._month = 12
                self._year -= 1
            else:
                self._month -= 1
            self._build_days()

        def _next_month(self):
            if self._month == 12:
                self._month = 1
                self._year += 1
            else:
                self._month += 1
            self._build_days()

    class DateEntry(ttk.Entry):
        """Fallback DateEntry showing a popup calendar."""

        def __init__(self, master=None, textvariable=None, **kwargs):
            self._var = textvariable or tk.StringVar()
            super().__init__(master, textvariable=self._var, **kwargs)
            self._popup = None
            self.bind("<Button-1>", self._open_popup)

        def _open_popup(self, event=None):
            if self._popup:
                return
            self._popup = tk.Toplevel(self)
            self._popup.transient(self)
            self._popup.protocol("WM_DELETE_WINDOW", self._close_popup)
            cal = _SimpleCalendar(self._popup, self._var, self._close_popup)
            cal.pack()
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self._popup.geometry(f"+{x}+{y}")

        def _close_popup(self):
            if self._popup is not None:
                self._popup.destroy()
                self._popup = None

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


        # Configure ttk theme for a more modern look
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            # Fallback silently if theme is unavailable
            pass
        # Optional file menu for JSON import/export when available
        if hasattr(tk, "Menu") and hasattr(self.root, "config"):
            menubar = tk.Menu(self.root)
            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="Export to JSON", command=self.export_tasks)
            file_menu.add_command(label="Import from JSON", command=self.import_tasks)
            menubar.add_cascade(label="File", menu=file_menu)
            self.root.config(menu=menubar)


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

        # --- Filtering widgets ---
        self.search_var = tk.StringVar()
        self.hide_completed_var = tk.IntVar()

        search_entry = ttk.Entry(self.main_frame, textvariable=self.search_var)
        search_entry.grid(row=4, column=0, sticky="ew", padx=2)

        hide_check = tk.Checkbutton(
            self.main_frame,
            text="Hide completed",
            variable=self.hide_completed_var,
        )
        hide_check.grid(row=4, column=1, sticky="ew", padx=2)

        filter_btn = ttk.Button(
            self.main_frame, text="Apply Filter", command=self.refresh_window
        )
        filter_btn.grid(row=4, column=2, sticky="ew", padx=2)

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

        # Keep a reference on the dialog so these vars aren't garbage collected
        # while the window is open
        dialog.task_name_var = task_name_field
        dialog.due_date_var = due_date_field
        dialog.priority_var = priority_field
        dialog.completed_var = completed_var

        form = ttk.Frame(dialog)
        form.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(form, text="Task Name:").grid(row=0, column=0, sticky="e")
        task_entry = ttk.Entry(form, textvariable=task_name_field)
        task_entry.grid(row=0, column=1)
        ttk.Label(form, text="Due Date:").grid(row=1, column=0, sticky="e")
        due_date_entry = DateEntry(form, textvariable=due_date_field)
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
        # Keep a reference on the dialog so these vars aren't garbage collected
        # while the window is open
        dialog.task_name_var = task_name_field
        dialog.due_date_var = due_date_field
        dialog.priority_var = priority_field
        dialog.completed_var = completed_var

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
        due_date_entry = DateEntry(form, textvariable=due_date_field)
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

    def export_tasks(self):
        """Prompt for a path and export tasks as JSON."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            from persistence import save_tasks_to_json
            save_tasks_to_json(self.controller.task, path)

    def import_tasks(self):
        """Prompt for a JSON file and replace current tasks."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            from persistence import load_tasks_from_json
            task = load_tasks_from_json(path)
            self.controller.task = task
            self.task_list = task.get_sub_tasks()
            self.name = task.name
            self.refresh_window()

    def refresh_window(self):
        """Refreshes the listbox displaying the tasks."""
        self.listbox.delete(0, tk.END)

        search_term = self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        hide_completed = bool(self.hide_completed_var.get()) if hasattr(self, "hide_completed_var") else False

        for idx, task in enumerate(self.controller.get_sub_tasks()):

            if not isinstance(task, Task):
                continue

            if hide_completed and task.completed:
                continue

            if search_term and search_term not in task.name.lower():
                continue

            display = task.name
            if task.completed:
                display += " (Completed)"
            if getattr(task, "due_date", None):
                display += f" - Due: {task.due_date}"
            if getattr(task, "priority", None) is not None:
                display += f" - Priority: {task.priority}"
            self.listbox.insert(tk.END, display)

            # Determine the foreground color for this item
            color = "black"
            if task.completed:
                color = "gray"
            elif getattr(task, "due_date", None):
                try:
                    due = _datetime.date.fromisoformat(str(task.due_date))
                    if due < _datetime.date.today():
                        color = "red"
                except ValueError:
                    pass

            self.listbox.itemconfig(idx, fg=color)

    def use_theme(self, theme_name):
        """Change the ttk theme for this window."""
        try:
            self.style.theme_use(theme_name)
        except Exception:
            pass
