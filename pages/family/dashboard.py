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

st.title("Family Dashboard")

# Welcome message
st.markdown(f"### Welcome, {st.session_state.get('user_name', 'User')}!")

# Get patients for this family member
patients = db.get_family_patients(st.session_state.user_id)

if not patients:
    st.info("""
    **No Patients Assigned**
    
    You don't have any patients assigned to your account yet.
    Please contact the care administrator to link your account to your loved one.
    """)
else:
    st.markdown("### Your Loved Ones")
    
    # Display patient cards
    for patient in patients:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"#### {patient['first_name']} {patient['last_name']}")
                if patient.get('patient_number'):
                    st.caption(f"Patient ID: {patient['patient_number']}")
                if patient.get('room_number'):
                    st.caption(f"Room: {patient['room_number']}")
                if patient.get('dementia_stage'):
                    st.caption(f"Stage: {patient['dementia_stage']}")
            
            with col2:
                if st.button("View Details", key=f"view_{patient['patient_id']}", use_container_width=True):
                    st.info("Patient details page coming soon!")

    st.markdown("---")
    
    # Quick stats
    st.markdown("### Quick Overview")
    
    # Get unread notifications
    unread_notifs = db.get_user_notifications(st.session_state.user_id, unread_only=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Your Patients", len(patients))
    
    with col2:
        st.metric("Unread Notifications", len(unread_notifs))
    
    with col3:
        # Count unread messages
        st.metric("Unread Messages", 0, help="Message viewing coming soon")

# Recent activity placeholder
st.markdown("---")
st.markdown("### Recent Activity")
st.info("Recent activity feed coming soon!")

# Footer
st.markdown("---")
st.caption(f"""
**User:** {st.session_state.get('user_name', '')} {st.session_state.get('user_last_name', '')}  
**Role:** Family Member  
**User ID:** {st.session_state.get('user_id', 'N/A')}
""")