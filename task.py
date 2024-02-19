import tkinter as tk
from tkinter import messagebox as tkMessageBox
import pickle


# Task Class
class Task:
    def __init__(self, name, sub_tasks=None):
        self.name = name
        self.sub_tasks = sub_tasks if sub_tasks is not None else []

    def __str__(self):

        return self.name + " {" + self.print_subtasks() + "}"

    def add_sub_task(self, task):
        self.sub_tasks.append(task)

    def remove_sub_task(self, task):
        self.sub_tasks.remove(task)

    def get_sub_tasks(self):
        return self.sub_tasks

    def print_subtasks(self):
        output = ""
        for subtask in self.sub_tasks:
            if subtask.sub_tasks is not None:
                output += " " + subtask.name + " {"+subtask.print_subtasks()+"}"
            else :
                output += " "+subtask.name+" "
        return output




class Window:
    def __init__(self, rt, task):
        self.root = rt
        self.task_list = task.get_sub_tasks()
        self.name = task.name

        tk.Label(self.root, text=f"Sub-tasks for {self.name}: ").pack()
        add_task_button = tk.Button(self.root, text="Add Task", command=lambda: self.add_task(task))
        add_task_button.pack()

        self.listbox = tk.Listbox(self.root)
        self.listbox.pack()

        view_subtasks_button = tk.Button(self.root, text="View Subtasks", command=lambda: self.view_subtasks())
        view_subtasks_button.pack()

        edit_button = tk.Button(self.root, text="Edit", command=lambda: self.edit_task())
        edit_button.pack()

        delete_button = tk.Button(self.root, text="Delete", command=lambda: self.delete_task(task))
        delete_button.pack()

        self.root.resizable(True, True)
        self.refresh_window()

    # ...

    def add_task(self, task):
        task_name_field = tk.StringVar()
        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        task_entry.pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.create_task_button(task_entry, confirm_button, task))
        confirm_button.pack()
        print(str(self))


    def create_task_button(self, task_entry, confirm_button, task):
        task_name = task_entry.get()
        task_entry.destroy()
        confirm_button.destroy()

        new_task = Task(task_name)
        task.add_sub_task(new_task)
        self.refresh_window()

    def on_closing(main_tasks):
        save_changes = tkMessageBox.askyesno("Quit", "Save your modification?")
        if save_changes:
            with open("object.pkl", "wb") as f:
                pickle.dump(main_tasks, f)
        root.destroy()

    def view_subtasks(self):
        selected_index = self.listbox.curselection()
        selected_task = self.task_list[selected_index[0]]
        r = tk.Tk()
        window = Window(r, selected_task)

    def delete_task(self, task):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_task = self.task_list[selected_index[0]]
        task.remove_sub_task(selected_task)
        self.refresh_window()

    def edit_task(self):
        print("Editing...")
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_task = self.task_list[selected_index[0]]

        print(selected_task)

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")

        task_name_field = tk.StringVar()
        task_name_field.set(selected_task.name)
        task_entry = tk.Entry(edit_window, textvariable=task_name_field)
        task_entry.pack()

        def confirm_edit():
            new_name = task_name_field.get()
            selected_task.name = new_name
            self.refresh_window()
            edit_window.destroy()

        confirm_button = tk.Button(edit_window, text="Confirm", command=confirm_edit)
        confirm_button.pack()

    def refresh_window(self):
        self.listbox.delete(0, tk.END)
        for task in self.task_list:
            if isinstance(task, Task):
                self.listbox.insert(tk.END, task.name)


# Main program

if __name__ == "__main__":
    root = tk.Tk()

    try:
        with open("object.pkl", "rb") as f:
            main_tasks = pickle.load(f)
    except FileNotFoundError:
        main_tasks = Task("Main")

    window = Window(root, main_tasks)
    root.protocol("WM_DELETE_WINDOW", lambda: Window.on_closing(main_tasks))
    root.mainloop()
    print(main_tasks)
