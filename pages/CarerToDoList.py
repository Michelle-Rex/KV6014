import streamlit as st
import datetime

class Task:
    def __init__(self, task):
        self.task = task
        self.task_ID = ""
        self.isComplete = False
        self.date_complete = ""
        self.time_complete = ""

    def mark_complete(self):
        self.isComplete = True
        self.date_complete = datetime.datetime.now().strftime("%x")
        self.time_complete = datetime.datetime.now().strftime("%X")

class ToDoList:
    def __init__(self):
        self.taskList = []

    def addTask(self, task: Task):
        self.taskList.append(task)

