import streamlit as st

st.title("Patient List")
db = st.session_state.db

search = st.text_input("Search patients", placeholder="Search by ID, name, or room")

col1, col2 = st.columns(2)
with col1:
    stage_filter = st.selectbox("Filter by Stage", ["All", "Early", "Mid", "Late"])
with col2:
    sort_by = st.selectbox("Sort by", ["Patient ID", "Name", "Room"])
st.divider()

# search the patients based on search/filter
if search:
    patients = db.search_patient_details(search)
elif stage_filter != "All":
    patients = db.filter_patients_by_stage(stage_filter)
else:
    patients = db.get_all_patient_details()
if not patients:
    st.info("No patients found")
    if st.button("Add First Patient"):
        st.switch_page("pages/carer/add_patient.py")
else:
    st.write(f"Showing {len(patients)} patients")



    
    for patient in patients:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**ID: {patient['patient_number']}**")
                st.write(f"{patient['first_name']} {patient['last_name']}")
                age = "N/A"
                if patient.get('date_of_birth'):
                    try:
                        birth_year = int(patient['date_of_birth'][:4])
                        age = 2025 - birth_year
                    except:
                        age = "N/A"
                st.write(f"Age: {age}")
                st.write(f"Room: {patient.get('room_number') or 'N/A'}")
            with col2:
                st.write("Emergency Contact:")
                if patient.get('emergency_contacts'):
                    contact = patient['emergency_contacts'][0]
                    st.write(f"{contact['name']} ({contact['relationship']})")
                    st.write(f"Phone: {contact['phone']}")
                else:
                    st.write("No contacts")
            with col3:
                if st.button("View Logs", key=f"logs_{patient['patient_id']}"):
                    st.session_state.current_patient = patient['patient_id']
                    st.switch_page("pages/carer/daily_logs.py")
                
                if st.button("Medications", key=f"meds_{patient['patient_id']}"):
                    st.session_state.current_patient = patient['patient_id']
                    st.switch_page("pages/carer/medications.py")