import tkinter as tk
from tkinter import messagebox as tkMessageBox
import pickle
from task import Task
from window import Window


# Main program
def on_closing():
    save_changes = tkMessageBox.askyesno("Quit", "Save your modification?")
    if save_changes:
        with open("object.pkl", "wb") as f:
            pickle.dump(main_tasks, f)
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    try:
        with open("object.pkl", "rb") as f:
            main_tasks = pickle.load(f)
    except FileNotFoundError:
        main_tasks = Task("Main")

    window = Window(root, main_tasks)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()