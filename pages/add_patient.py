import streamlit as st
from datetime import date
import uuid

st.title("Add New Patient")

if 'num_emergency_contacts' not in st.session_state:
    st.session_state.num_emergency_contacts = 1

st.subheader("Emergency Contacts")
num_contacts = st.number_input("Number of Emergency Contacts", 
                               min_value=1, max_value=5, 
                               value=st.session_state.num_emergency_contacts,
                               key="num_contacts_input")

st.session_state.num_emergency_contacts = num_contacts

emergency_contacts = []
for i in range(num_contacts):
    st.write(f"**Emergency Contact {i+1}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        contact_name = st.text_input("Name*", key=f"ec_name_{i}", placeholder="Contact name")
    with col2:
        contact_phone = st.text_input("Phone*", key=f"ec_phone_{i}", placeholder="Phone number")
    with col3:
        contact_relation = st.text_input("Relationship*", key=f"ec_relation_{i}", placeholder="Son/Daughter/Spouse")
    
    if contact_name and contact_phone and contact_relation:
        emergency_contacts.append({
            'name': contact_name,
            'phone': contact_phone,
            'relationship': contact_relation
        })

st.divider()

with st.form("add_patient_form"):
    st.subheader("Basic Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id_number = st.text_input("Patient ID Number*", placeholder="e.g., P001, P002")
        name = st.text_input("Full Name*")
        age = st.number_input("Age*", min_value=1, max_value=120, value=70)
        
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        room_number = st.text_input("Room Number")
        stage = st.selectbox("Dementia Stage", ["Early", "Middle", "Late"])
    
    st.divider()
    st.subheader("Doctor Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gp_name = st.text_input("GP/Doctor Name*")
        gp_phone = st.text_input("GP Phone*")
        
    with col2:
        gp_practice = st.text_input("GP Practice/Clinic")
        gp_email = st.text_input("GP Email")
    
    st.divider()
    st.subheader("Medical Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        allergies = st.text_input("Allergies (if any)")
        medical_conditions = st.text_input("Medical Conditions")
        
    with col2:
        mobility = st.selectbox("Mobility", ["Independent", "Walks with aid", "Wheelchair user", "Bedridden"])
        dietary_requirements = st.text_input("Dietary Requirements")
    
    care_notes = st.text_area("Important Notes")
    
    submitted = st.form_submit_button("Save Patient", use_container_width=True)

if submitted:
    if patient_id_number and name and age and emergency_contacts and gp_name and gp_phone:
        existing_ids = [p.get('patient_id_number') for p in st.session_state.patients.values()]
        if patient_id_number in existing_ids:
            st.error(f"Patient ID {patient_id_number} already exists. Please use a different ID.")
        else:
            patient_id = str(uuid.uuid4())
            
            patient_data = {
                'id': patient_id,
                'patient_id_number': patient_id_number,
                'name': name,
                'age': age,
                'dob': date.today().isoformat(),
                'gender': gender,
                'room': room_number,
                'diagnosis_date': date.today().isoformat(),
                'stage': stage,
                'address': '',
                'phone': '',
                'email': '',
                'gp_name': gp_name,
                'gp_phone': gp_phone,
                'gp_practice': gp_practice,
                'gp_email': gp_email,
                'emergency_contacts': emergency_contacts,
                'family_members': [],
                'allergies': allergies,
                'medical_conditions': medical_conditions,
                'mobility': mobility,
                'dietary_requirements': dietary_requirements,
                'care_notes': care_notes,
                'created_date': date.today().isoformat()
            }
            
            st.session_state.patients[patient_id] = patient_data
            st.session_state.tasks[patient_id] = []
            st.session_state.medications[patient_id] = []
            st.session_state.daily_logs[patient_id] = []
            
            st.success(f"Patient {patient_id_number} - {name} added successfully")
            st.session_state.num_emergency_contacts = 1
            
            if st.button("View Patient List"):
                st.switch_page("pages/patient_list.py")
    else:
        st.error("Please fill in all required fields marked with *")