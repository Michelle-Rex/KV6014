import streamlit as st
import CarerToDoListClass as toDo
import db_conn

def main():
    st.title("To Do List")

    st.button("Create New Task", type = "secondary", on_click=makeNewTask())


def makeNewTask():
    st.subheader("New Task")
    col1, col2 = st.beta_columns(2)

    with col1:
        task_name = st.text_area("Task Name")  
        task_desc = st.text_area("Task Description")      

    with col2:
        task_due_date = st.date_input("Due Date")
        
    if st.button("Add To List"):
        newTask = toDo.Task(task_name, task_desc, task_due_date)
        st.success("Task Added")

def showToDoList():
    #get data from db
    #make task instance (to allow for functionality, like checking tasks as complete)
    #make a task element with the check box and everything for each returned tuple from db
    pass

def deleteTask():
    pass

def editTask():
    pass
