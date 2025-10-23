import streamlit as st
from datetime import datetime, time
import json

st.set_page_config(
    page_title="Dementia Care Manager",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)




if 'patients' not in st.session_state:
    st.session_state.patients = {}
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'medications' not in st.session_state:
    st.session_state.medications = {}
if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = {}
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}
if 'memory_book' not in st.session_state:
    st.session_state.memory_book = {}

with st.sidebar:
    st.title("Dementia Care Manager")
    st.write(f"**Current Time:** {datetime.now().strftime('%d %B %Y, %H:%M')}")
    
    st.divider()
    st.subheader("Medication Alerts")
    
    current_time = datetime.now().time()
    current_hour = current_time.hour
    current_minute = current_time.minute


    
    
    if st.session_state.medications:
        alerts = []
        for patient_id, meds in st.session_state.medications.items():
            patient_name = st.session_state.patients.get(patient_id, {}).get('name', 'Unknown')
            for med in meds:
                if med.get('active', True):
                    med_time = datetime.strptime(med['time'], '%H:%M').time()
                    time_diff = (med_time.hour * 60 + med_time.minute) - (current_hour * 60 + current_minute)
                    
                    if 0 <= time_diff <= 30:
                        alerts.append({
                            'patient': patient_name,
                            'medication': med['name'],
                            'time': med['time'],
                            'minutes': time_diff
                        })
        
        if alerts:
            for alert in alerts:
                st.warning(f"**{alert['patient']}**\n{alert['medication']} at {alert['time']}\n(in {alert['minutes']} min)")
        else:
            st.info("No upcoming medications in next 30 mins")
    else:
        st.info("No medications scheduled")

pages = {
    "Dashboard": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
    ],
    "Patient Management": [
        st.Page("pages/patient_list.py", title="Patient List", icon="👥"),
        st.Page("pages/add_patient.py", title="Add New Patient", icon="➕"),
    ],
    "Daily Care": [
        st.Page("pages/daily_logs.py", title="Daily Logs", icon="📝"),
        st.Page("pages/medication.py", title="Medications", icon="💊"),
        st.Page("pages/tasks.py", title="Task Checklist", icon="✅"),
    ],
    "History": [
        st.Page("pages/historical_logs.py", title="Historical Logs", icon="📆"),
    ],
    "Memory Book": [
        st.Page("pages/memory_book.py", title="Photos & Media", icon="📷"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()