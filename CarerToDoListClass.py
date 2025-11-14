# CarerToDoListClass.py
from datetime import datetime
#Classes needed for the to do list


class Task:
    def __init__(self, title, description, due_date, completed=False, task_id=None):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = completed
        self.date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_complete(self):
        self.completed = True
        self.date_completed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_incomplete(self):
        self.completed = False
        self.date_completed = None

    def to_tuple(self, patient_id):
        return (patient_id, self.title, self.description, self.due_date, int(self.completed))
    
    #getters and setters
    def change_title(self, title):
        self.title = title

    def get_title(self):
        return self.title
    
    def change_description(self, desc):
        self.description = desc

    def get_description(self):
        return self.description
    
    def change_due_date(self, dueDate):
        self.due_date = dueDate

    def get_due_date(self):
        return self.due_date
