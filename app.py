import streamlit as st
from database.db_manager import Database

st.set_page_config(
    page_title="Dementia Care Manager",
    layout="wide"
)

if 'db' not in st.session_state:
    st.session_state.db = Database()

st.sidebar.title("Dementia Care Manager")
st.sidebar.write("**Role:** Carer")

pages = {
    "Dashboard": [
        st.Page("pages/carer/dashboard.py", title="Dashboard"),
    ],
    "Patients": [
        st.Page("pages/carer/patient_list.py", title="Patient List"),
        st.Page("pages/carer/add_patient.py", title="Add Patient"),
    ],
    "Daily Care": [
        st.Page("pages/carer/daily_logs.py", title="Daily Logs"),
        st.Page("pages/carer/medications.py", title="Medications"),
        st.Page("pages/carer/tasks.py", title="Tasks"),
    ],
    "Records": [
        st.Page("pages/carer/historical_logs.py", title="Historical Logs"),
        st.Page("pages/carer/memory_book.py", title="Memory Book"),
    ],
    "Settings": [st.Page("pages/carer/settings.py", title="Settings")]
}

pg = st.navigation(pages, position="sidebar")
pg.run()
