#!/usr/bin/env python3
"""
This script demonstrates a simple to-do list application using tkinter.
It allows users to create, edit, and delete tasks. The tasks can be
saved to a JSON file (``tasks.json``) upon closing the application.

Modules:
- tkinter: provides the Tk GUI toolkit for building the application's GUI.
- messagebox: a sub-module of tkinter used for displaying message boxes.
- persistence: helper functions for saving and loading task data in JSON.

Classes:
- Task: represents a single task in the to-do list.
- Window: creates the main application window.
- TaskController: manages the tasks and their interactions.

Functions:
- on_closing(): handles the closing event of the application,
                prompting the user to save modifications before closing.

Usage:
    Run this script to launch the to-do list application.
"""
import tkinter as tk
from tkinter import messagebox as tkMessageBox
from task import Task
from window import Window
from controller import TaskController
from persistence import load_tasks_from_json, save_tasks_to_json


def load_tasks():
    """Load tasks from ``tasks.json`` using JSON persistence."""
    return load_tasks_from_json("tasks.json")


# Main program
def _tasks_equal(t1, t2):
    """Return ``True`` if the two task trees are identical."""
    try:
        return t1.to_dict() == t2.to_dict()
    except Exception:
        return False


def on_closing(task, rt):
    """Handle the closing event and optionally save modifications."""
    try:
        existing = load_tasks_from_json("tasks.json")
    except Exception:
        existing = None

    if existing is not None and _tasks_equal(task, existing):
        rt.destroy()
        return

    save_changes = tkMessageBox.askyesno("Quit", "Save your modification?")
    if save_changes:
        try:
            save_tasks_to_json(task, "tasks.json")
        except OSError:
            try:
                tkMessageBox.showwarning(
                    "Save Error",
                    "Failed to save tasks, closing without saving.",
                )
            except Exception:
                pass
    rt.destroy()


if __name__ == "__main__":

    root = tk.Tk()
    root.title("Task Manager")

    main_tasks = load_tasks()

    controller = TaskController(main_tasks)
    window = Window(root, controller)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(main_tasks, root))
    root.mainloop()
