import streamlit as st
import datetime

#this file is the classes used for the To Do List feature

class Task:
    def __init__(self, task_name, task_desc, dueDate: datetime): #constructor
        self.task_name = task_name
        self.task_desc = task_desc
        self.dueDate = dueDate
        self.task_id = ""
        self.isComplete = False
        self.dateTime_complete = ""

    #get/set task name
    def getTaskName(self): 
        return self.task_name
    
    def setTaskName(self, task):
        self.task_name = task

    #get/set task description
    def getTaskDesc(self):
        return self.task_desc
    
    def setTaskDesc(self, desc):
        self.task_desc = desc

    #get/set task due date
    def setdueDate(self):
        return self.dueDate

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

    

