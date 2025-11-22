import streamlit as st
from datetime import date
from apply_preferences import apply_preferences

st.title("Dashboard")
db = st.session_state.db
stats = db.get_dashboard_stats()




col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", stats['total_patients'])
with col2:
    st.metric("Pending Tasks", stats['pending_tasks'])
with col3:
    st.metric("Active Medications", stats['active_medications'])
with col4:
    st.metric("Logs Today", stats['logs_today'])

st.divider()


col1, col2 = st.columns(2)
with col1:
    st.subheader("Pending Tasks")
    
    patients = db.get_all_patients()
    has_tasks = False
    checkID = 0
    for patient in patients:
        tasks = db.get_patient_tasks(patient['patient_id'])
        pending = [t for t in tasks if not t['completed']]
        
        if pending:
            has_tasks = True
            st.write(f"**{patient['first_name']} {patient['last_name']}** (ID: {patient['patient_number']})")
            for task in pending[:3]:
                priority_mark = ""
                if task['priority'] == 'Urgent':
                    priority_mark = "[URGENT] "
                elif task['priority'] == 'High':
                    priority_mark = "[HIGH] "
                st.write(f"  - {priority_mark}{task['task_name']}")
                st.checkbox("complete", key = checkID, label_visibility="hidden")
                checkID += 1
    
    if not has_tasks:
        st.info("No pending tasks")

with col2:
    st.subheader("Today's Medications")


    
    has_meds = False
    for patient in patients:
        meds = db.get_patient_medications(patient['patient_id'], active_only=True)
        
        if meds:
            has_meds = True
            st.write(f"**{patient['first_name']} {patient['last_name']}**")
            for med in meds:
                st.write(f"  - {med['scheduled_time']}: {med['name']} ({med['dosage']})")
    
    if not has_meds:
        st.info("No medications scheduled")



st.divider()
st.subheader("Quick Patient Access")

if patients:
    cols = st.columns(3)
    for idx, patient in enumerate(patients[:6]):
        with cols[idx % 3]:
            with st.container(border=True):
                st.write(f"**{patient['patient_number']}**")
                st.write(f"{patient['first_name']} {patient['last_name']}")
                st.write(f"Room: {patient['room_number'] or 'N/A'}")
                

                
                if st.button("View", key=f"view_{patient['patient_id']}", use_container_width=True):
                    st.session_state.current_patient = patient['patient_id']
                    st.switch_page("pages/carer/daily_logs.py")
else:
    st.info("No patients registered")
    if st.button("Add First Patient"):
        st.switch_page("pages/carer/add_patient.py")