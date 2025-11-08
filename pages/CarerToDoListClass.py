import streamlit as st
import datetime

#this file is the classes used for the To Do List feature

class Task:
    def __init__(self, task): #constructor
        self.task = task
        self.task_id = ""
        self.isComplete = False
        self.date_complete = ""
        self.time_complete = ""

    #getters and setters
    def getTask(self): 
        return self.task
    
    def setTask(self, task):
        self.task = task

    def getID(self):
        return self.task_id

    def markComplete(self): #mark task as complete and get the date and time of completion
        self.isComplete = True
        self.date_complete = datetime.datetime.now().strftime("%x")
        self.time_complete = datetime.datetime.now().strftime("%X")
    
    def markIncomplete(self): #reset the task competion
        if self.isComplete == True:
            self.isComplete = False
            self.date_complete = ""
            self.time_complete = ""


class ToDoList:
    def __init__(self): #make the list, should trigger when carer selects a patient, should run something to get the existing list from the database
        self.taskList = []

    def addTask(self, task: Task): #add task to list
        self.taskList.append(task)

    

