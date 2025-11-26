import streamlit as st

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
        st.info("Recent daily logs will appear here. Coming soon!")
    
    with tab2:
        st.info("Current medications list will appear here. Coming soon!")
    
    with tab3:
        st.info("Upcoming tasks and activities will appear here. Coming soon!")
    
    with tab4:
        st.info("Medical information (based on access level) will appear here. Coming soon!")

st.markdown("---")
st.caption(f"Logged in as: {st.session_state.get('user_name', 'User')} (Family Member)")