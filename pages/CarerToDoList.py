import streamlit as st

def main():
    st.title("To Do List")

    st.button("Create New Task", type = "secondary", on_click=makeTaskMenu())


def makeTaskMenu():
    st.subheader("New Task")
    col1 = st.beta_columns(2)

    with col1:
        task = st.text_area("Task")
        

    if st.button("Add To List"):
        st.success("Task Added")