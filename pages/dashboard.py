import streamlit as st
from datetime import datetime, date

st.title("Dashboard")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", len(st.session_state.patients))

with col2:
    # Count pending tasks
    pending_tasks = 0
    for patient_id, task_list in st.session_state.tasks.items():
        pending_tasks += sum(1 for task in task_list if not task.get('completed', False))
    st.metric("Pending Tasks", pending_tasks)

with col3:
    # Count today's medications
    today_meds = 0
    for patient_id, meds in st.session_state.medications.items():
        today_meds += len(meds)
    st.metric("Today's Medications", today_meds)

with col4:
    # Count today's logs
    today = date.today().isoformat()
    today_logs = sum(1 for logs in st.session_state.daily_logs.values() 
                     if any(log.get('date') == today for log in logs))
    st.metric("Logs Today", today_logs)

st.divider()

# Today's Schedule
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Pending Tasks")
    if st.session_state.tasks:
        for patient_id, task_list in st.session_state.tasks.items():
            patient_name = st.session_state.patients.get(patient_id, {}).get('name', 'Unknown')
            pending = [task for task in task_list if not task.get('completed', False)]
            if pending:
                st.write(f"**{patient_name}**")
                for task in pending:
                    st.write(f"  - {task['task']}")
    else:
        st.info("No pending tasks")

with col2:
    st.subheader("💊 Today's Medications")
    if st.session_state.medications:
        for patient_id, meds in st.session_state.medications.items():
            patient_name = st.session_state.patients.get(patient_id, {}).get('name', 'Unknown')
            if meds:
                st.write(f"**{patient_name}**")
                for med in sorted(meds, key=lambda x: x['time']):
                    st.write(f"  - {med['time']}: {med['name']} ({med['dosage']})")
    else:
        st.info("No medications scheduled")

st.divider()

# Patient Quick Access
st.subheader("Quick Patient Access")

if st.session_state.patients:
    cols = st.columns(3)
    for idx, (patient_id, patient) in enumerate(st.session_state.patients.items()):
        with cols[idx % 3]:
            with st.container(border=True):
                st.write(f"**{patient['name']}**")
                st.write(f"Age: {patient['age']}")
                st.write(f"Room: {patient.get('room', 'N/A')}")
                if st.button("View Details", key=f"view_{patient_id}", use_container_width=True):
                    st.session_state.current_patient = patient_id
                    st.switch_page("pages/daily_logs.py")
else:
    st.info("No patients registered yet. Add a patient to get started.")
    if st.button("Add Patient"):
        st.switch_page("pages/add_patient.py")
