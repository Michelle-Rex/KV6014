# CarerToDoListClass.py
from datetime import datetime

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
