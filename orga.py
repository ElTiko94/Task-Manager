"""
This script demonstrates a simple to-do list application using tkinter.
It allows users to create, edit, and delete tasks. The tasks can be
saved to a file ('object.pkl') upon closing the application.

Modules:
- tkinter: provides the Tk GUI toolkit for building the application's GUI.
- messagebox: a sub-module of tkinter used for displaying message boxes.
- pickle: for serializing and deserializing Python object structures.

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
import pickle
from task import Task
from window import Window
from controller import TaskController


# Main program
def on_closing(task,rt):
    """Function to handle closing event of the application."""
    save_changes = tkMessageBox.askyesno("Quit", "Save your modification?")
    if save_changes:
        with open("object.pkl", "wb") as file:
            pickle.dump(task, file)
    rt.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    try:
        with open("object.pkl", "rb") as f:
            main_tasks = pickle.load(f)
    except FileNotFoundError:
        main_tasks = Task("Main")

    controller = TaskController(main_tasks)
    window = Window(root, controller)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(main_tasks, root))
    root.mainloop()
