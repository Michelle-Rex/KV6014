import streamlit as st
import uuid
from datetime import date

st.title("Add New Patient")
db = st.session_state.db

# keep track of emergency contacts count
if 'num_contacts' not in st.session_state:
    st.session_state.num_contacts = 1

st.subheader("Emergency Contacts")
num_contacts = st.number_input("No of emergency contacts", min_value=1, max_value=5, value=st.session_state.num_contacts)
st.session_state.num_contacts = num_contacts

# collects  all the emergency contact info
emergency_contacts = []
for i in range(num_contacts):
    st.write(f"Contact {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name", key=f"ec_name_{i}")
    with col2:
        phone = st.text_input("Phone", key=f"ec_phone_{i}")
    with col3:
        relationship = st.text_input("Relationship", key=f"ec_rel_{i}")
    
    if name and phone and relationship:
        emergency_contacts.append({'name': name, 'phone': phone, 'relationship': relationship})

st.divider()

with st.form("add_patient_form"):
    st.subheader("Basic Information")
    
    col1, col2 = st.columns(2)
    with col1:
        patient_number = st.text_input("Patient ID Number")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
    with col2:
        dob = st.date_input("Date of Birth", max_value=date.today())
        gender = st.selectbox("Gender", ["Male", "Female"])
        room_number = st.text_input("Room Number")
    
    stage = st.selectbox("Dementia Stage", ["Early", "Mid", "Late"])
    
    st.subheader("Doctor Information")
    col1, col2 = st.columns(2)
    with col1:
        gp_name = st.text_input("GP Name")
        gp_phone = st.text_input("GP Phone")
    with col2:
        gp_practice = st.text_input("GP Practice")
    
    st.subheader("Medical Information")
    col1, col2 = st.columns(2)
    with col1:
        allergies = st.text_input("Allergies")
        medical_conditions = st.text_input("Medical Conditions")
    with col2:
        mobility = st.selectbox("Mobility", ["Independent", "Walks with aid", "Wheelchair user", "Bedridden"])
        dietary = st.text_input("Dietary Requirements")
    
    care_notes = st.text_area("Care Notes")
    
    submitted = st.form_submit_button("Save Patient")


if submitted:
    # basic validation to ensure required fields are filled
    if not patient_number or not first_name or not last_name:
        st.error("Please fill in Patient ID, First Name, and Last Name")
    elif not emergency_contacts:
        st.error("Please add at least one emergency contact")
    else:
        # first add to their Patient table
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Patient (FirstName, LastName, DementiaStage)
                VALUES (?, ?, ?)
            """, (first_name, last_name, stage))
            
            patient_id = cursor.lastrowid
            conn.commit()
            
            # thens this gets added to PatientDetails table
            details = {
                'patient_number': patient_number,
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': dob.isoformat(),
                'gender': gender,
                'room_number': room_number,
                'dementia_stage': stage,
                'gp_name': gp_name,
                'gp_phone': gp_phone,
                'gp_practice': gp_practice,
                'allergies': allergies,
                'medical_conditions': medical_conditions,
                'mobility': mobility,
                'dietary_requirements': dietary,
                'care_notes': care_notes,
                'emergency_contacts': emergency_contacts
            }
            
            result = db.add_patient_details(patient_id, details)
            
            if result:
                st.success(f"Patient {patient_number} added successfully")
                st.session_state.num_contacts = 1
                if st.button("View Patient List"):
                    st.switch_page("pages/carer/patient_list.py")
            else:
                st.error("Failed to add patient details")
                
        except Exception as e:
            st.error(f"Failed to add patient: {e}")
        finally:
            conn.close()