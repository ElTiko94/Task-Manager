import tkinter as tk
from task import Task


class Window:
    def __init__(self, root, task):
        self.root = root
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

    # Functions
    def add_task(self, task):
        task_name_field = tk.StringVar()
        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        task_entry.pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.create_task_button(task_entry, confirm_button, task))
        confirm_button.pack()

    def create_task_button(self, task_entry, confirm_button, task):
        task_name = task_entry.get()
        task_entry.destroy()
        confirm_button.destroy()

        new_task = Task(task_name)
        task.add_sub_task(new_task)
        self.refresh_window()

    def edit_task(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_task = self.task_list[selected_index[0]]

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