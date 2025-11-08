import streamlit as st

class Task:
    def __init__(self, task):
        self.task = task
        self.task_ID = ""
        self.isComplete = False
        self.date_complete = ""
        self.time_complete = ""


