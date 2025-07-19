"""
This module defines a Window class representing the main application window for a to-do list.

Classes:
- Window: Represents the main application window for managing tasks.

Usage:
    This module provides the Window class for managing the main application window of a to-do list.
"""

import tkinter as tk
import tkinter.ttk as _ttk
ttk = _ttk  # default ttk module

# Try to load ttkbootstrap for optional theming enhancements.  When available
# we use its ``Style`` class and widget set so ``bootstyle`` keywords work.
try:
    from ttkbootstrap import Style as BootstrapStyle
    import ttkbootstrap as ttkb
except Exception:  # Library not installed or failed to load
    BootstrapStyle = None
    ttkb = None
else:
    ttk = ttkb

# Convenience flag used throughout the class to enable ttkbootstrap enhancements
USE_BOOTSTRAP = BootstrapStyle is not None
from tkinter import messagebox as tkMessageBox

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
        confirm_edit: Confirms the edit of a task and updates the tree view.
        refresh_window: Refreshes the tree view displaying the tasks.
    """

    def __init__(self, root, controller, parent_window=None):
        """
        Initializes a new Window object.

        Args:
            root: The root tkinter window.
            controller: The task controller managing the tasks.
        """
        self.root = root
        self.task_list = controller.get_sub_tasks()
        self.controller = controller
        # Expose current save path for convenience
        self.file_path = controller.save_path
        self.parent_window = parent_window
        self.child_windows = []
        self.name = controller.get_task_name()

        # Determine which theme to apply.  If a parent window exists, re-use its
        # current theme so that all windows share consistent styling.
        theme = "flatly" if USE_BOOTSTRAP else "clam"
        if parent_window is not None and hasattr(parent_window, "style"):
            try:
                existing = parent_window.style.theme_use()
                if existing:
                    theme = existing
            except Exception:
                pass

        # Configure ttk theme for a more modern look.  Only attempt to use
        # ttkbootstrap when a real ``tk.Tk`` instance is supplied; otherwise the
        # themed style may try to create its own root window which breaks unit
        # tests that pass in dummy objects.
        bootstrap_ok = (
            BootstrapStyle is not None and isinstance(self.root, tk.Tk)
        )

        if bootstrap_ok:
            try:
                try:
                    self.style = BootstrapStyle(master=self.root)
                except TypeError:
                    # Older ttkbootstrap versions do not accept ``master``.  Do
                    # not replace the provided root unless one wasn't supplied
                    # at all.
                    self.style = BootstrapStyle()
                    if hasattr(self.style, "master") and root is None:
                        self.root = self.style.master
                self.style.theme_use(theme)
            except Exception:
                # Fallback to regular ttk in case of errors
                fallback_mod = ttk if ttk is not ttkb else _ttk
                self.style = fallback_mod.Style(self.root)
                try:
                    self.style.theme_use(theme)
                except Exception:
                    pass
        else:
            fallback_mod = ttk if ttk is not ttkb else _ttk
            self.style = fallback_mod.Style(self.root)
            try:
                self.style.theme_use(theme)
            except Exception:
                # Fallback silently if theme is unavailable
                pass
        # Optional file menu for JSON import/export when available
        if hasattr(tk, "Menu") and hasattr(self.root, "config"):
            menubar = tk.Menu(self.root)
            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="Export to JSON", command=self.export_tasks)
            file_menu.add_command(label="Export to CSV", command=self.export_tasks_csv)
            file_menu.add_command(label="Export to ICS", command=self.export_tasks_ics)
            file_menu.add_command(label="Import from JSON", command=self.import_tasks_json)
            file_menu.add_command(label="Import from CSV", command=self.import_tasks_csv)
            file_menu.add_command(label="Import from ICS", command=self.import_tasks_ics)
            menubar.add_cascade(label="File", menu=file_menu)

            edit_menu = tk.Menu(menubar, tearoff=0)
            edit_menu.add_command(label="Undo", command=self.undo)
            edit_menu.add_command(label="Redo", command=self.redo)
            menubar.add_cascade(label="Edit", menu=edit_menu)

            view_menu = tk.Menu(menubar, tearoff=0)
            theme_names = list(self.style.theme_names())
            current = self.style.theme_use()
            if current not in theme_names:
                theme_names.insert(0, current)
            for theme in theme_names:
                view_menu.add_command(
                    label=theme, command=lambda t=theme: self.use_theme(t)
                )
            menubar.add_cascade(label="View", menu=view_menu)

            self.root.config(menu=menubar)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Ensure the frame and tree view expand when the window is resized
        if hasattr(self.root, "rowconfigure") and hasattr(self.root, "columnconfigure"):
            self.root.rowconfigure(0, weight=1)
            self.root.columnconfigure(0, weight=1)
        if hasattr(self.main_frame, "rowconfigure") and hasattr(
            self.main_frame, "columnconfigure"
        ):
            self.main_frame.rowconfigure(2, weight=1)
            self.main_frame.columnconfigure(0, weight=1)

        ttk.Label(self.main_frame, text=f"Sub-tasks for {self.name}: ").grid(
            row=0, column=0, columnspan=3, pady=2
        )

        btn_opts = {}
        if USE_BOOTSTRAP:
            btn_opts["bootstyle"] = "success"
        add_task_button = ttk.Button(
            self.main_frame, text="Add Task", command=self.add_task, **btn_opts
        )
        add_task_button.grid(row=1, column=0, sticky="ew", padx=2)

        btn_opts = {"bootstyle": "info"} if USE_BOOTSTRAP else {}
        sort_btn = ttk.Button(
            self.main_frame,
            text="Sort by Priority",
            command=self.sort_tasks_by_priority,
            **btn_opts,
        )
        sort_btn.grid(row=1, column=1, sticky="ew", padx=2)

        sort_due_btn = ttk.Button(
            self.main_frame,
            text="Sort by Due Date",
            command=self.sort_tasks_by_due_date,
            **btn_opts,
        )
        sort_due_btn.grid(row=1, column=2, sticky="ew", padx=2)

        self.tree = ttk.Treeview(self.main_frame, show="tree")
        self.tree.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=5)
        self.tree_items = {}

        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient="vertical", command=self.tree.yview
        )
        self.scrollbar.grid(row=2, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Context menu for tree items
        if hasattr(tk, "Menu"):
            self.tree_menu = tk.Menu(self.root, tearoff=0)
            self.tree_menu.add_command(label="Edit", command=self.edit_task)
            self.tree_menu.add_command(label="Delete", command=self.delete_task)
            self.tree_menu.add_command(
                label="Toggle Complete", command=self.toggle_completion
            )
            self.tree_menu.add_separator()
            self.tree_menu.add_command(
                label="Move Up", command=lambda: self.move_selected_task(-1)
            )
            self.tree_menu.add_command(
                label="Move Down", command=lambda: self.move_selected_task(1)
            )

        # Bind double-click on a task to open its subtasks
        self.tree.bind("<Double-Button-1>", lambda e: self.view_subtasks())
        # Bind right-click to show the context menu
        self.tree.bind("<Button-3>", self._show_tree_menu)

        btn_opts = {"bootstyle": "secondary"} if USE_BOOTSTRAP else {}
        view_subtasks_btn = ttk.Button(
            self.main_frame,
            text="View Subtasks",
            command=self.view_subtasks,
            **btn_opts,
        )
        view_subtasks_btn.grid(row=3, column=0, sticky="ew", padx=2, pady=2)

        btn_opts = {"bootstyle": "warning"} if USE_BOOTSTRAP else {}
        edit_button = ttk.Button(
            self.main_frame, text="Edit", command=self.edit_task, **btn_opts
        )
        edit_button.grid(row=3, column=1, sticky="ew", padx=2)

        btn_opts = {"bootstyle": "danger"} if USE_BOOTSTRAP else {}
        dlt_btn = ttk.Button(
            self.main_frame, text="Delete", command=self.delete_task, **btn_opts
        )
        dlt_btn.grid(row=3, column=2, sticky="ew", padx=2)

        btn_opts = {"bootstyle": "secondary"} if USE_BOOTSTRAP else {}
        up_btn = ttk.Button(
            self.main_frame,
            text="Move Up",
            command=self.move_selected_up,
            **btn_opts,
        )
        up_btn.grid(row=3, column=3, sticky="ew", padx=2)

        down_btn = ttk.Button(
            self.main_frame,
            text="Move Down",
            command=self.move_selected_down,
            **btn_opts,
        )
        down_btn.grid(row=3, column=4, sticky="ew", padx=2)

        # --- Filtering widgets ---
        self.search_var = tk.StringVar()
        self.hide_completed_var = tk.IntVar()
        self.show_completed_only_var = tk.IntVar()

        search_entry = ttk.Entry(self.main_frame, textvariable=self.search_var)
        search_entry.grid(row=4, column=0, sticky="ew", padx=2)

        hide_check = tk.Checkbutton(
            self.main_frame,
            text="Hide completed",
            variable=self.hide_completed_var,
            command=self.refresh_window,
        )
        hide_check.grid(row=4, column=1, sticky="ew", padx=2)

        show_only_check = tk.Checkbutton(
            self.main_frame,
            text="Show completed only",
            variable=self.show_completed_only_var,
            command=self.refresh_window,
        )
        show_only_check.grid(row=4, column=2, sticky="ew", padx=2)

        btn_opts = {"bootstyle": "primary"} if USE_BOOTSTRAP else {}
        filter_btn = ttk.Button(
            self.main_frame,
            text="Apply Filter",
            command=self.refresh_window,
            **btn_opts,
        )
        filter_btn.grid(row=4, column=3, sticky="ew", padx=2)

        # Additional filtering controls
        self.due_filter_var = tk.StringVar()
        self.due_before_var = tk.IntVar()
        self.due_after_var = tk.IntVar()
        ttk.Label(self.main_frame, text="Due Date:").grid(row=5, column=0, sticky="e")
        DateEntry(self.main_frame, textvariable=self.due_filter_var).grid(
            row=5, column=1
        )
        tk.Checkbutton(
            self.main_frame,
            text="Before",
            variable=self.due_before_var,
            command=self.refresh_window,
        ).grid(row=5, column=2, sticky="w")
        tk.Checkbutton(
            self.main_frame,
            text="After",
            variable=self.due_after_var,
            command=self.refresh_window,
        ).grid(row=5, column=3, sticky="w")

        self.priority_filter_var = tk.StringVar()
        self.priority_above_var = tk.IntVar()
        self.priority_below_var = tk.IntVar()
        ttk.Label(self.main_frame, text="Priority:").grid(row=6, column=0, sticky="e")
        ttk.Entry(self.main_frame, textvariable=self.priority_filter_var).grid(
            row=6, column=1
        )
        tk.Checkbutton(
            self.main_frame,
            text="Above",
            variable=self.priority_above_var,
            command=self.refresh_window,
        ).grid(row=6, column=2, sticky="w")
        tk.Checkbutton(
            self.main_frame,
            text="Below",
            variable=self.priority_below_var,
            command=self.refresh_window,
        ).grid(row=6, column=3, sticky="w")

        self.root.resizable(True, True)
        self.refresh_window()

    def view_subtasks(self):
        """Open a new window to view the subtasks of the selected tree item."""
        sel = self.tree.selection()
        if not sel:
            return

        task, _parent = self.tree_items.get(sel[0], (None, None))
        if task is None:
            return

        r = tk.Toplevel(self.root)
        sub = Window(r, TaskController(task), parent_window=self)
        self.child_windows.append(sub)

        def _close():
            try:
                self.child_windows.remove(sub)
            except ValueError:
                pass
            r.destroy()

        if hasattr(r, "protocol"):
            r.protocol("WM_DELETE_WINDOW", _close)

    def delete_task(self):
        """Delete the selected task from the controller."""
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        task, parent = self.tree_items.get(item, (None, None))
        if task is None:
            return

        if parent is None:
            idx = self.controller.get_sub_tasks().index(task)
            self.controller.delete_task(idx)
        else:
            parent.remove_sub_task(task)
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

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
        try:
            priority = int(priority_text) if priority_text else None
        except ValueError:
            priority = None
            try:
                tkMessageBox.showwarning(
                    "Invalid Priority", "Priority must be an integer."
                )
            except Exception:
                pass
        completed = bool(completed_var.get())

        task_entry.destroy()
        due_date_entry.destroy()
        priority_entry.destroy()
        completed_check.destroy()
        confirm_button.destroy()

        if dialog is not None:
            dialog.destroy()

        self.controller.add_task(
            task_name, due_date=due_date or None, priority=priority
        )
        if completed:
            idx = len(self.controller.get_sub_tasks()) - 1
            self.controller.mark_task_completed(idx)
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def edit_task(self):
        """Display a dialog to edit the selected task."""
        sel = self.tree.selection()
        if not sel:
            return

        task, _parent = self.tree_items.get(sel[0], (None, None))
        if task is None:
            return

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
                sel[0],
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
        selected_item,
        confirm_button,
        dialog=None,
    ):
        """Confirm the edit of ``selected_item`` and refresh the tree."""
        new_name = task_name_field.get()
        new_due = due_date_entry.get()
        priority_text = priority_entry.get()
        try:
            new_priority = int(priority_text) if priority_text else None
        except ValueError:
            new_priority = None
            try:
                tkMessageBox.showwarning(
                    "Invalid Priority", "Priority must be an integer."
                )
            except Exception:
                pass
        completed = bool(completed_var.get())

        task_name_field.destroy()
        due_date_entry.destroy()
        priority_entry.destroy()
        completed_check.destroy()
        confirm_button.destroy()

        if dialog is not None:
            dialog.destroy()

        task, _parent = self.tree_items.get(selected_item, (None, None))
        if task is None:
            return

        task.name = new_name
        task.set_due_date(new_due or None)
        task.set_priority(new_priority)
        if completed:
            task.mark_completed()
        else:
            task.mark_incomplete()
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def sort_tasks_by_priority(self):
        """Sort tasks by priority using the controller and refresh the view."""
        self.controller.sort_tasks_by_priority()
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def sort_tasks_by_due_date(self):
        """Sort tasks by due date using the controller and refresh the view."""
        self.controller.sort_tasks_by_due_date()
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def move_selected_up(self):
        """Move the selected task up in the list."""
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        task, parent = self.tree_items.get(item, (None, None))
        if task is None:
            return
        if parent is None:
            lst = self.controller.get_sub_tasks()
            idx = lst.index(task)
            if idx == 0:
                return
            self.controller.move_task(idx, idx - 1)
        else:
            lst = parent.get_sub_tasks()
            idx = lst.index(task)
            if idx == 0:
                return
            lst.insert(idx - 1, lst.pop(idx))
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def move_selected_down(self):
        """Move the selected task down in the list."""
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        task, parent = self.tree_items.get(item, (None, None))
        if task is None:
            return
        if parent is None:
            lst = self.controller.get_sub_tasks()
            idx = lst.index(task)
            if idx >= len(lst) - 1:
                return
            self.controller.move_task(idx, idx + 1)
        else:
            lst = parent.get_sub_tasks()
            idx = lst.index(task)
            if idx >= len(lst) - 1:
                return
            lst.insert(idx + 1, lst.pop(idx))
        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def toggle_completion(self):
        """Toggle the completion state of the selected task."""
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        task, parent = self.tree_items.get(item, (None, None))
        if task is None:
            return

        if parent is None:
            idx = self.controller.get_sub_tasks().index(task)
            if task.completed:
                self.controller.mark_task_incomplete(idx)
            else:
                self.controller.mark_task_completed(idx)
        else:
            task.completed = not task.completed
            try:
                self.controller._auto_save()
            except Exception:
                pass

        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def move_selected_task(self, offset):
        """Move the selected task up or down by ``offset`` positions."""
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        task, parent = self.tree_items.get(item, (None, None))
        if task is None:
            return

        if parent is None:
            lst = self.controller.get_sub_tasks()
            idx = lst.index(task)
            new_idx = idx + offset
            if new_idx < 0 or new_idx >= len(lst):
                return
            self.controller.move_task(idx, new_idx)
        else:
            lst = parent.get_sub_tasks()
            idx = lst.index(task)
            new_idx = idx + offset
            if new_idx < 0 or new_idx >= len(lst):
                return
            lst.pop(idx)
            lst.insert(new_idx, task)

        self.refresh_window()
        if self.parent_window is not None:
            self.parent_window.refresh_window()

    def _show_tree_menu(self, event):
        """Display the context menu at the pointer position."""
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                self.tree.selection_set(iid)
            except Exception:
                pass
            if hasattr(self, "tree_menu"):
                try:
                    self.tree_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.tree_menu.grab_release()

    # --- Undo/Redo ------------------------------------------------------

    def undo(self):
        """Undo the last action via the controller and refresh."""
        try:
            self.controller.undo()
        finally:
            self.refresh_window()
            if self.parent_window is not None:
                self.parent_window.refresh_window()

    def redo(self):
        """Redo the last undone action via the controller and refresh."""
        try:
            self.controller.redo()
        finally:
            self.refresh_window()
            if self.parent_window is not None:
                self.parent_window.refresh_window()

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

    def export_tasks_csv(self):
        """Prompt for a path and export tasks as CSV."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            from persistence import save_tasks_to_csv

            save_tasks_to_csv(self.controller.task, path)

    def export_tasks_ics(self):
        """Prompt for a path and export tasks in ICS format."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")],
        )
        if path:
            from persistence import save_tasks_to_ics

            save_tasks_to_ics(self.controller.task, path)

    def import_tasks_json(self):
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
            if self.parent_window is not None:
                self.parent_window.refresh_window()

    def import_tasks_csv(self):
        """Prompt for a CSV file and replace current tasks."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            from persistence import load_tasks_from_csv

            task = load_tasks_from_csv(path)
            self.controller.task = task
            self.task_list = task.get_sub_tasks()
            self.name = task.name
            self.refresh_window()
            if self.parent_window is not None:
                self.parent_window.refresh_window()

    def import_tasks_ics(self):
        """Prompt for an ICS file and replace current tasks."""
        if not hasattr(tk, "filedialog"):
            from tkinter import filedialog
        else:
            filedialog = tk.filedialog
        path = filedialog.askopenfilename(
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")]
        )
        if path:
            from persistence import load_tasks_from_ics

            task = load_tasks_from_ics(path)
            self.controller.task = task
            self.task_list = task.get_sub_tasks()
            self.name = task.name
            self.refresh_window()
            if self.parent_window is not None:
                self.parent_window.refresh_window()

    def _task_visible(
        self,
        task,
        search_term="",
        hide_completed=False,
        show_completed_only=False,
        due_value="",
        before=False,
        after=False,
        prio_value="",
        above=False,
        below=False,
    ):
        """Return True if ``task`` should be shown with the current filters."""
        if not isinstance(task, Task):
            return False

        if show_completed_only and not task.completed:
            return False

        if hide_completed and task.completed:
            return False

        if search_term and search_term not in task.name.lower():
            return False

        if due_value and (before or after):
            try:
                fdate = _datetime.date.fromisoformat(due_value)
            except ValueError:
                # Invalid user input - skip due date filtering entirely
                return True

            try:
                tdate = (
                    _datetime.date.fromisoformat(str(task.due_date))
                    if getattr(task, "due_date", None)
                    else None
                )
            except ValueError:
                tdate = None
            if before and (tdate is None or tdate >= fdate):
                return False
            if after and (tdate is None or tdate <= fdate):
                return False

        if prio_value and (above or below):
            try:
                threshold = int(prio_value)
            except ValueError:
                threshold = None
            if threshold is not None:
                pval = getattr(task, "priority", None)
                if above and (pval is None or pval <= threshold):
                    return False
                if below and (pval is None or pval >= threshold):
                    return False

        return True

    def _format_task(self, task):
        """Return display text and color for ``task``."""
        display = task.name
        if task.completed:
            display += " (Completed)"
        if getattr(task, "due_date", None):
            display += f" - Due: {task.due_date}"
        if getattr(task, "priority", None) is not None:
            display += f" - Priority: {task.priority}"

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

        prio = getattr(task, "priority", None)
        if not task.completed:
            if prio == 1:
                color = "red"
            elif prio == 2 and color != "red":
                color = "orange"

        return display, color

    def _insert_task(
        self,
        task,
        parent_id="",
        parent_task=None,
        search_term="",
        hide_completed=False,
        show_completed_only=False,
        due_value="",
        before=False,
        after=False,
        prio_value="",
        above=False,
        below=False,
    ):
        """Insert ``task`` and its subtasks into the tree if visible."""
        if not self._task_visible(
            task,
            search_term=search_term,
            hide_completed=hide_completed,
            show_completed_only=show_completed_only,
            due_value=due_value,
            before=before,
            after=after,
            prio_value=prio_value,
            above=above,
            below=below,
        ):
            return

        display, color = self._format_task(task)
        self.tree.tag_configure(color, foreground=color)
        iid = self.tree.insert(parent_id, tk.END, text=display, tags=(color,))
        self.tree_items[iid] = (task, parent_task)

        for sub in task.get_sub_tasks():
            self._insert_task(
                sub,
                iid,
                task,
                search_term,
                hide_completed,
                show_completed_only,
                due_value,
                before,
                after,
                prio_value,
                above,
                below,
            )

    def refresh_window(self):
        """Refresh the Treeview displaying the tasks."""
        # Capture which tasks are currently expanded so we can restore the
        # state after rebuilding the tree.  Also remember the currently
        # selected task, if any.
        open_tasks = set()
        selected_task = None
        for iid, (task, _parent) in self.tree_items.items():
            try:
                if self.tree.item(iid, "open"):
                    open_tasks.add(task)
            except Exception:
                pass
        sel = self.tree.selection()
        if sel:
            selected_task = self.tree_items.get(sel[0], (None, None))[0]

        for child in self.tree.get_children():
            self.tree.delete(child)
        self.tree_items.clear()

        search_term = (
            self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        )
        hide_completed = (
            bool(self.hide_completed_var.get())
            if hasattr(self, "hide_completed_var")
            else False
        )
        show_completed_only = (
            bool(self.show_completed_only_var.get())
            if hasattr(self, "show_completed_only_var")
            else False
        )
        due_value = (
            self.due_filter_var.get().strip() if hasattr(self, "due_filter_var") else ""
        )
        before = (
            bool(self.due_before_var.get())
            if hasattr(self, "due_before_var")
            else False
        )
        after = (
            bool(self.due_after_var.get()) if hasattr(self, "due_after_var") else False
        )
        prio_value = (
            self.priority_filter_var.get().strip()
            if hasattr(self, "priority_filter_var")
            else ""
        )
        above = (
            bool(self.priority_above_var.get())
            if hasattr(self, "priority_above_var")
            else False
        )
        below = (
            bool(self.priority_below_var.get())
            if hasattr(self, "priority_below_var")
            else False
        )

        for task in self.controller.get_sub_tasks():
            self._insert_task(
                task,
                "",
                None,
                search_term=search_term,
                hide_completed=hide_completed,
                show_completed_only=show_completed_only,
                due_value=due_value,
                before=before,
                after=after,
                prio_value=prio_value,
                above=above,
                below=below,
            )

        # Restore previously expanded nodes and selection after rebuilding the
        # tree so that the user's view is preserved.
        for iid, (task, _parent) in self.tree_items.items():
            if task in open_tasks:
                try:
                    self.tree.item(iid, open=True)
                except Exception:
                    pass
            if selected_task is task:
                try:
                    self.tree.selection_set(iid)
                except Exception:
                    pass

    def use_theme(self, theme_name):
        """Change the ttk theme for this window."""
        try:
            self.style.theme_use(theme_name)
        except Exception:
            pass
