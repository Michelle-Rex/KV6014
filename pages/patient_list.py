import streamlit as st
import pandas as pd

st.title("Patient List")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("Search", placeholder="Search by ID or name")

with col2:
    stage_filter = st.selectbox("Filter by Stage", ["All", "Early", "Middle", "Late"])

with col3:
    sort_by = st.selectbox("Sort by", ["ID", "Name", "Age", "Room", "Recently Added"])

st.divider()

if st.session_state.patients:
    filtered_patients = {}
    for patient_id, patient in st.session_state.patients.items():
        if search:
            search_lower = search.lower()
            if not (search_lower in patient.get('patient_id_number', '').lower() or 
                   search_lower in patient['name'].lower() or 
                   search_lower in str(patient.get('room', '')).lower()):
                continue
        
        if stage_filter != "All" and patient.get('stage') != stage_filter:
            continue
        
        filtered_patients[patient_id] = patient
    
    if sort_by == "ID":
        sorted_patients = dict(sorted(filtered_patients.items(), key=lambda x: x[1].get('patient_id_number', '')))
    elif sort_by == "Name":
        sorted_patients = dict(sorted(filtered_patients.items(), key=lambda x: x[1]['name']))
    elif sort_by == "Age":
        sorted_patients = dict(sorted(filtered_patients.items(), key=lambda x: x[1]['age']))
    elif sort_by == "Room":
        sorted_patients = dict(sorted(filtered_patients.items(), key=lambda x: x[1].get('room', '')))
    else:
        sorted_patients = dict(sorted(filtered_patients.items(), 
                                     key=lambda x: x[1].get('created_date', ''), reverse=True))
    
    st.write(f"**Showing {len(sorted_patients)} patient(s)**")
    
    for patient_id, patient in sorted_patients.items():
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.subheader(f"ID: {patient.get('patient_id_number', 'N/A')}")
                st.write(f"**Name:** {patient['name']}")
                st.write(f"**Age:** {patient['age']} | **Gender:** {patient['gender']}")
                st.write(f"**Room:** {patient.get('room', 'N/A')} | **Stage:** {patient.get('stage', 'N/A')}")
            
            with col2:
                st.write("**Emergency Contacts:**")
                if patient.get('emergency_contacts'):
                    for contact in patient['emergency_contacts']:
                        st.write(f"{contact['name']} ({contact['relationship']})")
                        st.write(f"Phone: {contact['phone']}")
                else:
                    st.write("No contacts listed")
                
                st.write("**Doctor:**")
                st.write(f"{patient.get('gp_name', 'N/A')}")
                st.write(f"Phone: {patient.get('gp_phone', 'N/A')}")
            
            with col3:
                if st.button("View Logs", key=f"logs_{patient_id}", use_container_width=True):
                    st.session_state.current_patient = patient_id
                    st.switch_page("pages/daily_logs.py")
                
                if st.button("Medications", key=f"meds_{patient_id}", use_container_width=True):
                    st.session_state.current_patient = patient_id
                    st.switch_page("pages/medication.py")
                
                if st.button("Tasks", key=f"tasks_{patient_id}", use_container_width=True):
                    st.session_state.current_patient = patient_id
                    st.switch_page("pages/tasks.py")
            
            with st.expander("More Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mobility:** {patient.get('mobility', 'N/A')}")
                    st.write(f"**Allergies:** {patient.get('allergies', 'None listed')}")
                with col2:
                    st.write(f"**Dietary:** {patient.get('dietary_requirements', 'None')}")
                    st.write(f"**Medical Conditions:** {patient.get('medical_conditions', 'None')}")
                
                if patient.get('care_notes'):
                    st.write(f"**Care Notes:** {patient['care_notes']}")

else:
    st.info("No patients registered yet.")
    if st.button("Add First Patient"):
        st.switch_page("pages/add_patient.py")

if st.session_state.patients:
    st.divider()
    if st.button("Export Patient List to CSV"):
        patient_list = []
        for patient_id, patient in st.session_state.patients.items():
            emergency_contact_names = ", ".join([c['name'] for c in patient.get('emergency_contacts', [])])
            emergency_contact_phones = ", ".join([c['phone'] for c in patient.get('emergency_contacts', [])])
            
            patient_list.append({
                'Patient ID': patient.get('patient_id_number', ''),
                'Name': patient['name'],
                'Age': patient['age'],
                'Gender': patient['gender'],
                'Room': patient.get('room', ''),
                'Stage': patient.get('stage', ''),
                'Emergency Contacts': emergency_contact_names,
                'Emergency Phones': emergency_contact_phones,
                'GP': patient.get('gp_name', ''),
                'GP Phone': patient.get('gp_phone', '')
            })
        
        df = pd.DataFrame(patient_list)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="patient_list.csv",
            mime="text/csv"
        )