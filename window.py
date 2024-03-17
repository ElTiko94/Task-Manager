import tkinter as tk
from task import Task
from controller import TaskController

class Window:
    def __init__(self, root, controller):
        self.root = root
        self.task_list = controller.get_sub_tasks()
        self.controller = controller
        self.name = controller.get_task_name()
        


        tk.Label(self.root, text=f"Sub-tasks for {self.name}: ").pack()
        add_task_button = tk.Button(self.root, text="Add Task", command=lambda: self.add_task())
        add_task_button.pack()

        self.listbox = tk.Listbox(self.root)
        self.listbox.pack()

        view_subtasks_button = tk.Button(self.root, text="View Subtasks", command=lambda: self.view_subtasks())
        view_subtasks_button.pack()

        edit_button = tk.Button(self.root, text="Edit", command=lambda: self.edit_task())
        edit_button.pack()

        delete_button = tk.Button(self.root, text="Delete", command=lambda: self.delete_task(controller))
        delete_button.pack()

        self.root.resizable(True, True)
        self.refresh_window()

    # ...

    def view_subtasks(self):
        selected_index = self.listbox.curselection()
        selected_task = self.controller.get_sub_tasks()[selected_index[0]]
        r = tk.Tk()
        window = Window(r, TaskController(selected_task))

    def delete_task(self, controller):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        controller.delete_task(selected_index[0])
        self.refresh_window()

    # Functions
    def add_task(self):
        task_name_field = tk.StringVar()
        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        task_entry.pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.create_task_button(task_entry, confirm_button))
        confirm_button.pack()

    def create_task_button(self, task_entry, confirm_button):
        task_name = task_entry.get()
        task_entry.destroy()
        confirm_button.destroy()

        self.controller.add_task(task_name)
        self.refresh_window()

    def edit_task(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        task_name_field = tk.StringVar()
        task_name_field.set(self.controller.get_sub_tasks()[selected_index[0]].name)
        task_entry = tk.Entry(self.root, textvariable=task_name_field)
        task_entry.pack()

        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.confirm_edit(task_entry, selected_index, confirm_button))
        confirm_button.pack()

    # Function to handle task editing and updating the listbox
    def confirm_edit(self, task_name_field, selected_index, confirm_button):
        new_name = task_name_field.get()
        task_name_field.destroy()
        confirm_button.destroy()

        self.controller.edit_task(selected_index[0], new_name)
        self.refresh_window()

    def refresh_window(self):
        self.listbox.delete(0, tk.END)
        for task in self.controller.get_sub_tasks():
            if isinstance(task, Task):
                self.listbox.insert(tk.END, task.name)