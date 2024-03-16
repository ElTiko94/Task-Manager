# Task Class
class Task:
    def __init__(self, name, sub_tasks=[]):
        self.name = name
        self.sub_tasks = sub_tasks if sub_tasks is not None else []

    def __str__(self):

        return self.name + " {" + self.print_subtasks() + "}" if self.print_subtasks() is not None else self.name

    def add_sub_task(self, task):
        self.sub_tasks.append(task)

    def remove_sub_task(self, task):
        self.sub_tasks.remove(task)

    def get_sub_tasks(self):
        return self.sub_tasks

    def print_subtasks(self):
        output = ""
        for task in self.sub_tasks:
            if task.sub_tasks != []:
                output += " " + task.name + " {"+task.print_subtasks()+"}"
            else :
                output += " "+task.name+", "
        return output