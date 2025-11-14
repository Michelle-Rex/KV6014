import streamlit as st
from datetime import time as dt_time, datetime

st.title("Medication Management")
db = st.session_state.db
patients = db.get_all_patients()

if not patients:
    st.warning("No patients registered")
    if st.button("Add Patient"):
        st.switch_page("pages/carer/add_patient.py")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in patients}

if 'current_patient' in st.session_state and st.session_state.current_patient:
    default_idx = list(patient_options.keys()).index(st.session_state.current_patient) if st.session_state.current_patient in patient_options else 0
else:
    default_idx = 0

selected_display = st.selectbox("Select Patient", list(patient_options.values()), index=default_idx)
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()

with st.expander("Add New Medication"):
    with st.form("add_med_form"):
        col1, col2 = st.columns(2)
        with col1:
            med_name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage", placeholder="10mg")
            frequency = st.selectbox("Frequency", ["Once daily", "Twice daily", "Three times daily", "Four times daily", "As needed"])
        with col2:
            med_time = st.time_input("Time", value=dt_time(9, 0))
            route = st.selectbox("Route", ["Oral", "Injection", "Topical", "Inhaler", "Eye drops"])
            prescriber = st.text_input("Prescribed by")
        
        purpose = st.text_area("Purpose")
        submitted = st.form_submit_button("Save Medication")
        


        if submitted:
            if med_name and dosage:
                med_data = {
                    'patient_id': selected_patient_id,
                    'name': med_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'scheduled_time': med_time.strftime('%H:%M'),
                    'route': route,
                    'prescriber': prescriber,
                    'purpose': purpose
                }


                
                med_id = db.add_medication(med_data)
                
                if med_id:
                    st.success(f"Medication {med_name} added")
                    st.rerun()
                else:
                    st.error("Failed to add medication")
            else:
                st.error("Please enter medication name and dosage")



st.divider()
st.subheader("Current Medications")



medications = db.get_patient_medications(selected_patient_id, active_only=True)
if medications:
    sorted_meds = sorted(medications, key=lambda x: x['scheduled_time'])
    
    for med in sorted_meds:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{med['name']}**")
                st.write(f"Dosage: {med['dosage']} | Route: {med['route']}")
                st.write(f"Time: {med['scheduled_time']} | Frequency: {med['frequency']}")
            
            with col2:
                if med['purpose']:
                    st.write(f"Purpose: {med['purpose']}")
                if med['prescriber']:
                    st.write(f"Prescribed by: {med['prescriber']}")
            
            with col3:
                if st.button("Mark Given", key=f"given_{med['medication_id']}", use_container_width=True):
                    st.success(f"{med['name']} marked as given at {datetime.now().strftime('%H:%M')}")
                
                if st.button("Stop", key=f"stop_{med['medication_id']}", use_container_width=True):
                    db.update_medication_status(med['medication_id'], False)
                    st.success(f"{med['name']} discontinued")
                    st.rerun()
else:
    st.info("No active medications for this patient")

inactive_meds = db.get_patient_medications(selected_patient_id, active_only=False)
inactive = [m for m in inactive_meds if not m['active']]

if inactive:
    with st.expander("Discontinued Medications"):
        for med in inactive:
            st.write(f"{med['name']}- {med['dosage']} at {med['scheduled_time']}")