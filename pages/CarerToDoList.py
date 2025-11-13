# pages/CarerToDoList.py
import streamlit as st
from datetime import date


from db import get_connection, execute_db
from apply_preferences import apply_preferences
from topbar import top_navigation


from CarerToDoListClass import Task


def get_tasks_for_patient(patient_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT TaskID, Title, Description, DueDate, Completed FROM Task WHERE PatientID = ? ORDER BY DueDate ASC",
        (patient_id,),
    ).fetchall()
    conn.close()
    return rows


def add_task(patient_id, title, desc, due_date):
    execute_db(
        "INSERT INTO Task (PatientID, Title, Description, DueDate, Completed) VALUES (?, ?, ?, ?, 0)",
        (patient_id, title, desc, due_date),)


def mark_task_complete(task_id, complete=True):
    execute_db("UPDATE Task SET Completed = ? WHERE TaskID = ?", (1 if complete else 0, task_id))


def delete_task(task_id):
    execute_db("DELETE FROM Task WHERE TaskID = ?", (task_id,))


def render_page():
    # auth checker
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        st.switch_page("login.py")
        return

    if st.session_state.get("role") != "carer":
        st.warning("This page is only for carers.")
        st.switch_page("pages/dashboard.py")
        return

    apply_preferences()
    top_navigation()

    st.title("Carer To-Do List")

    # select patient before entering this page,
    # similar to other pages related to specfic patients btw
    if "current_patient" not in st.session_state:
        st.info("Please select a patient first from the dashboard.")
        st.stop()

    patient_id = st.session_state["current_patient"]

    st.markdown(f"**Managing tasks for Patient ID:** {patient_id}")

    # new task adding
    with st.expander("Create a New Task", expanded=False):
        with st.form("new_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Task Title")
                desc = st.text_area("Description")
            with col2:
                due_date = st.date_input("Due Date", min_value=date.today())

            submitted = st.form_submit_button("Add Task", use_container_width=True)
            if submitted:
                if title.strip():
                    add_task(patient_id, title, desc, due_date.isoformat())
                    st.success("Task successfully added.")
                    st.rerun()
                else:
                    st.warning("Please enter a task title.")

    st.divider()

    # existing tasks
    st.subheader("Current To-Do List")
    tasks = get_tasks_for_patient(patient_id)

    if not tasks:
        st.info("No tasks have been added yet.")
        return

    for t in tasks:
        with st.container(border=True):
            cols = st.columns([4, 2, 1, 1])
            with cols[0]:
                st.markdown(f"**{t['Title']}**")
                st.caption(t["Description"] or "(No description)")
            with cols[1]:
                st.write(f"Due: {t['DueDate']}")
            with cols[2]:
                complete_state = st.checkbox(
                    "Done",
                    value=bool(t["Completed"]),
                    key=f"complete_{t['TaskID']}",
                    on_change=mark_task_complete,
                    args=(t["TaskID"], not bool(t["Completed"])),
                )
            with cols[3]:
                if st.button("Delete", key=f"delete_{t['TaskID']}"):
                    delete_task(t["TaskID"])
                    st.success(f"Deleted task '{t['Title']}'")
                    st.rerun()


if __name__ == "__main__":
    render_page()
