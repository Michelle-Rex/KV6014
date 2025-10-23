import streamlit as st
from datetime import datetime, time as dt_time
import uuid

st.title("💊 Medication Management")

# Patient selector
if not st.session_state.patients:
    st.warning("No patients registered. Please add a patient first.")
    if st.button("Add Patient"):
        st.switch_page("pages/add_patient.py")
    st.stop()

# Select patient
if st.session_state.current_patient:
    default_index = list(st.session_state.patients.keys()).index(st.session_state.current_patient)
else:
    default_index = 0

patient_names = {pid: p['name'] for pid, p in st.session_state.patients.items()}
selected_patient_name = st.selectbox(
    "Select Patient",
    options=list(patient_names.values()),
    index=default_index
)

selected_patient_id = [pid for pid, name in patient_names.items() if name == selected_patient_name][0]
st.session_state.current_patient = selected_patient_id

st.divider()

# Add new medication
with st.expander("➕ Add New Medication", expanded=False):
    with st.form("add_medication_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            med_name = st.text_input("Medication Name*", placeholder="e.g., Donepezil")
            dosage = st.text_input("Dosage*", placeholder="e.g., 10mg")
            frequency = st.selectbox("Frequency", 
                                    ["Once daily", "Twice daily", "Three times daily", 
                                     "Four times daily", "As needed"])
        
        with col2:
            med_time = st.time_input("Time*", value=dt_time(9, 0))
            route = st.selectbox("Route", ["Oral", "Injection", "Topical", "Inhaler", "Eye drops"])
            prescriber = st.text_input("Prescribed by", placeholder="Dr. Smith")
        
        purpose = st.text_area("Purpose/Notes", 
                               placeholder="e.g., For memory improvement, Alzheimer's treatment")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date (Optional)", value=None)
        
        submitted = st.form_submit_button("💾 Save Medication", use_container_width=True)
        
        if submitted:
            if med_name and dosage and med_time:
                if selected_patient_id not in st.session_state.medications:
                    st.session_state.medications[selected_patient_id] = []
                
                medication = {
                    'id': str(uuid.uuid4()),
                    'name': med_name,
                    'dosage': dosage,
                    'frequency': frequency,
                    'time': med_time.strftime('%H:%M'),
                    'route': route,
                    'prescriber': prescriber,
                    'purpose': purpose,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat() if end_date else None,
                    'active': True
                }
                
                st.session_state.medications[selected_patient_id].append(medication)
                st.success(f"✅ Medication '{med_name}' added successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields marked with *")

st.divider()

# Display current medications
st.subheader(f"Current Medications for {selected_patient_name}")

if selected_patient_id in st.session_state.medications and st.session_state.medications[selected_patient_id]:
    medications = st.session_state.medications[selected_patient_id]
    active_meds = [med for med in medications if med.get('active', True)]
    
    if active_meds:
        # Sort by time
        sorted_meds = sorted(active_meds, key=lambda x: x['time'])
        
        for med in sorted_meds:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"### {med['name']}")
                    st.write(f"**Dosage:** {med['dosage']} | **Route:** {med['route']}")
                    st.write(f"**Time:** {med['time']} | **Frequency:** {med['frequency']}")
                
                with col2:
                    if med.get('purpose'):
                        st.write(f"**Purpose:** {med['purpose']}")
                    if med.get('prescriber'):
                        st.write(f"**Prescribed by:** {med['prescriber']}")
                    st.write(f"**Start Date:** {med['start_date']}")
                
                with col3:
                    # Mark as given
                    if st.button("✅ Given", key=f"given_{med['id']}", use_container_width=True):
                        # Log medication administration
                        log_entry = {
                            'id': str(uuid.uuid4()),
                            'date': datetime.now().isoformat(),
                            'medication': med['name'],
                            'dosage': med['dosage'],
                            'time_given': datetime.now().strftime('%H:%M'),
                            'scheduled_time': med['time'],
                            'given_by': "Carer"
                        }
                        
                        if selected_patient_id not in st.session_state.daily_logs:
                            st.session_state.daily_logs[selected_patient_id] = []
                        
                        # Find or create today's log
                        today = datetime.now().date().isoformat()
                        today_log = None
                        for log in st.session_state.daily_logs[selected_patient_id]:
                            if log.get('date') == today:
                                today_log = log
                                break
                        
                        if not today_log:
                            today_log = {
                                'date': today,
                                'medications_given': []
                            }
                            st.session_state.daily_logs[selected_patient_id].append(today_log)
                        
                        if 'medications_given' not in today_log:
                            today_log['medications_given'] = []
                        
                        today_log['medications_given'].append(log_entry)
                        
                        st.success(f"✅ Marked '{med['name']}' as given at {datetime.now().strftime('%H:%M')}")
                        st.rerun()
                    
                    # Discontinue
                    if st.button("🚫 Stop", key=f"stop_{med['id']}", use_container_width=True):
                        med['active'] = False
                        st.success(f"Medication '{med['name']}' discontinued")
                        st.rerun()
    else:
        st.info("No active medications for this patient")
else:
    st.info("No medications added yet for this patient")

# Medication history
if selected_patient_id in st.session_state.medications:
    inactive_meds = [med for med in st.session_state.medications[selected_patient_id] 
                     if not med.get('active', True)]
    
    if inactive_meds:
        with st.expander("📋 Medication History (Discontinued)"):
            for med in inactive_meds:
                st.write(f"**{med['name']}** - {med['dosage']} at {med['time']}")
                st.write(f"Duration: {med['start_date']} to {med.get('end_date', 'Discontinued')}")
                st.divider()