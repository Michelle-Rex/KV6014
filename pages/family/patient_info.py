import streamlit as st
from datetime import date, timedelta, datetime

# Role check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("Access Denied: This page is only accessible to family members.")
    st.stop()

# Get database instance
db = st.session_state.get('db')
if not db:
    st.error("Database connection error.")
    st.stop()

st.title("Patient Information")

# Get patients for this family member
patients = db.get_family_patients(st.session_state.user_id)

if not patients:
    st.info("""**No Patients Assigned**
    
    You don't have any patients assigned to your account yet.
    Please contact the care administrator to link your account to your loved one.
    """)
else:
    # Patient selector
    patient_names = [f"{p['first_name']} {p['last_name']}" for p in patients]
    selected_patient_name = st.selectbox("Select Patient", patient_names)
    
    # Get selected patient
    selected_index = patient_names.index(selected_patient_name)
    patient = patients[selected_index]
    
    st.markdown("---")
    
    # Display patient information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Information")
        st.write(f"**Name:** {patient['first_name']} {patient['last_name']}")
        if patient.get('patient_number'):
            st.write(f"**Patient ID:** {patient['patient_number']}")
        if patient.get('room_number'):
            st.write(f"**Room:** {patient['room_number']}")
        if patient.get('dementia_stage'):
            st.write(f"**Dementia Stage:** {patient['dementia_stage']}")
    
    with col2:
        st.markdown("### Your Access")
        st.info("Your access level determines what information you can view about your loved one.")
        st.write("**Current Access:** Coming soon")
    
    st.markdown("---")
    
    # Tabs for different information
    tab1, tab2, tab3, tab4 = st.tabs(["Recent Logs", "Medications", "Tasks", "Medical Info"])
    
    with tab1:
        #st.info("Recent daily logs will appear here. Coming soon!")
    
        # Get last 5 days of logs, the rest they could see in the Care Logs page, as it is only meant for recent overview
        start_date = (date.today() - timedelta(days=5)).isoformat()
        end_date = date.today().isoformat()
    
        logs = db.get_patient_logs(patient['patient_id'], start_date, end_date)
        
        if logs:
            st.write(f"Showing logs from last 5 days ({len(logs)} entries)")
            
            for log in logs[:5]:  
                log_date = datetime.fromisoformat(log['date']).strftime('%A, %d %B')
                
                with st.expander(f"{log_date} at {log['time']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Vitals:**")
                        st.write(f"Temperature: {log['vitals']['temperature']}°C")
                        st.write(f"Blood Pressure: {log['vitals']['blood_pressure']}")
                        st.write(f"Heart Rate: {log['vitals']['heart_rate']} bpm")
                    
                    with col2:
                        st.write("**Status:**")
                        st.write(f"Mood: {log['activities']['mood']}")
                        st.write(f"Appetite: {log['activities']['appetite']}")
                        st.write(f"Calories: {log['total_calories']} kcal")
                    
                    if log['general_notes']:
                        st.info(f"Notes: {log['general_notes']}")
            
            if st.button("View All Logs", use_container_width=True):
                st.switch_page("pages/family/care_logs.py")
        else:
            st.info("No recent logs available for the last 5 days")
            if st.button("View All Logs", use_container_width=True):
                st.switch_page("pages/family/care_logs.py")
        

    
    with tab2:
        #st.info("Current medications list will appear here. Coming soon!")

        medications = db.get_patient_medications(patient['patient_id'], active_only=True)
        
        if medications:
            st.write(f"**Current Medications** ({len(medications)} active)")
            
            sorted_meds = sorted(medications, key=lambda x: x['scheduled_time'])
            
            for med in sorted_meds:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{med['name']}** - {med['dosage']}")
                        st.write(f"{med['scheduled_time']} | {med['frequency']}")
                        if med['purpose']:
                            st.caption(f"Purpose: {med['purpose']}")
                    
                    with col2:
                        st.write(f"**Route:** {med['route']}")
                        if med['prescriber']:
                            st.caption(f"By: {med['prescriber']}")
        else:
            st.info("No active medications")
        
    
        inactive_meds = db.get_patient_medications(patient['patient_id'], active_only=False)
        inactive = [m for m in inactive_meds if not m['active']]
        
        if inactive:
            with st.expander("Discontinued Medications"):
                for med in inactive:
                    st.write(f"{med['name']} - {med['dosage']} at {med['scheduled_time']}")
    
    with tab3:
        st.info("Upcoming tasks and activities will appear here. Coming soon!")
    
    with tab4:
        st.info("Medical information (based on access level) will appear here. Coming soon!")

st.markdown("---")
st.caption(f"Logged in as: {st.session_state.get('user_name', 'User')} (Family Member)")