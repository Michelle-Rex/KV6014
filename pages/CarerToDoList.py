import streamlit as st

def main():
    st.title("To Do List")

    st.button("Create New Task", type = "secondary", on_click=makeNewTask())


def makeNewTask():
    st.subheader("New Task")
    col1, col2 = st.beta_columns(2)

    with col1:
        task = st.text_area("Task")        

    with col2:
        task_due_date = st.date_input("Due Date")
        
    if st.button("Add To List"):
        st.success("Task Added")

def showToDoList():
    pass

def deleteTask():
    pass

def editTask():
    pass