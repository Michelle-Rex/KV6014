# The old code is basically just scafolding and not at all integrated with the database, login system and accessibility features.
# It would be too much time and effort to go through and change it to work, so I renamed it and am basically rewriting my own tonight, starting at 09/11 22:45 (finished at: 09/11 23:57)

import streamlit as st
from datetime import date, datetime
from typing import Dict, Any
from pathlib import Path
import sqlite3

# local imports
from apply_preferences import apply_preferences, accessibility_settings_panel
from db import get_connection
#from topbar import top_navigation

#   UTILITY FUNCTIONS


def get_patient_count(conn):
    query = "SELECT COUNT(*) FROM Patient WHERE CarerID = ?"
    result = conn.execute(query, (st.session_state['user_id'],)).fetchone() # I should update this as I updated my db code, on my todo list
    return result[0] if result else 0

def get_log_count_today(conn):
    today_str = date.today().isoformat() # sqlite uses isoformat
    query = "SELECT COUNT(*) FROM Log_Item WHERE AuthorID = ? AND DATE(DateTime) = ?"
    result = conn.execute(query, (st.session_state['user_id'], today_str)).fetchone()
    return result[0] if result else 0

def get_patients_for_carer(conn):
    query = "SELECT PatientID, FirstName, LastName, DementiaStage, ResidenceType FROM Patient WHERE CarerID = ?"
    return conn.execute(query, (st.session_state['user_id'],)).fetchall()

def get_recent_logs(conn, limit=5):
    query = """
    SELECT Log_Item.Content, Log_Item.ContentLvl, Log_Item.DateTime, Patient.FirstName || ' ' || Patient.LastName as PatientName
    FROM Log_Item
    JOIN Patient ON Patient.PatientID = Log_Item.PatientID
    WHERE Patient.CarerID = ?
    ORDER BY Log_Item.DateTime DESC
    LIMIT ?
    """
    return conn.execute(query, (st.session_state['user_id'], limit)).fetchall()


#   PAGE RENDERING


def render_dashboard():
    st.title("Dashboard")
    # Check login status
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']: # this is also insecure
        st.warning("Please log in to the access the dashboard")
        st.switch_page("login.py")
    if st.session_state['role'] != 'carer':
        st.warning("This is for carers only.")
        st.switch_page(login.py)

    #top_navigation()

    # Apply accessibility preferences
    apply_preferences()
    ##accessibility_settings_panel()

    # Cconnect to the database
    conn = get_connection()

    # Retrieve metrics
    total_patients = get_patient_count(conn) # now we should have the dashboard allow us to change which patient we are seeing today
    today_logs = get_log_count_today(conn)

    # Placeholder metrics for the TODO tables
    pending_tasks = 0
    today_medication = 0


    # Dashboard Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", total_patients)
    col2.metric("Pending Tasks", pending_tasks)
    col3.metric("Today's Medications", today_medication)
    col4.metric("Logs Today", today_logs)

    st.divider()

    # Patient Quick Access
    st.subheader("Patient Quick Access")
    patients = get_patients_for_carer(conn)
    if not patients:
        st.info("No patients registered yet. Add a patient to get started.")
        if st.button("Add Patient"):
            st.switch_page("pages/add_patient.py")
        conn.close()
        return

    cols = st.columns(3)
    for idx, patient in enumerate(patients):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{patient['FirstName']} {patient['LastName']}**")
                st.caption(f"Stage: {patient['DementiaStage']} | Residence: {patient['ResidenceType']}")
                if st.button("View Details", key=f"view_{patient['PatientID']}", use_container_width=True):
                    st.session_state['current_patient'] = patient['PatientID']
                    st.switch_page("pages/patient_details.py") # TODO Add this page ig

    st.divider()

    # RECENT LOG ENTRIES
    st.subheader("Recent Logs")

    logs = get_recent_logs(conn)
    if not logs:
        st.info("No logs have been recorded yet.")
    else:
        for log in logs:
            with st.container(border=True):
                st.write(f"**{log['PatientName']}** - {log['ContentLvl'].capitalize()}")
                st.write(log['Content'])
                st.caption(datetime.strptime(log['DateTime'], '%Y-%m-%d %H:%M:%S'.strftime('%d%b%y, %H:%M')))

    conn.close()


# ENTRY


def render_page():
    render_dashboard()

if __name__ == "__main__":
    render_page()
