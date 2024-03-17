from task import Task

# controller.py
class TaskController:
    def __init__(self, task):
        self.task = task

    def add_task(self, task_name):
        new_task = Task(task_name)
        self.task.add_sub_task(new_task)

    def edit_task(self, task_index, new_name):
        task = self.task.get_sub_tasks()[task_index]
        task.name = new_name

    def delete_task(self, index):
        self.task.remove_sub_task(self.get_sub_tasks()[index])

    def get_task_name(self):
        return self.task.name

    def get_sub_tasks(self):
        return self.task.get_sub_tasks()

        
        