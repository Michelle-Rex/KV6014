import streamlit as st
from datetime import date
from typing import Dict, List, Any
import uuid
"""
Add Patient Module
Handles the creation and registration of new dementia patients in the system.

This feature provides a form-based interface for carers to register new patients
with their personal information, emergency contacts, doctor details, and medical information.
"""

class EmergencyContactManager:
    """
    Manages emergency contact collection and validation for patients.
    Supports multiple emergency contacts per patient.
    """
    @staticmethod
    def initialize_contact_count() -> None:
        """Initialize the emergency contact counter in session state."""
        if 'num_emergency_contacts' not in st.session_state:
            st.session_state.num_emergency_contacts = 1
    
    @staticmethod
    def render_contact_selector() -> int:
        """
        Render the emergency contact number selector.
        
        Returns:
            Number of emergency contacts selected by user
        """
        st.subheader("Emergency Contacts")
        num_contacts = st.number_input(
            "Number of Emergency Contacts",
            min_value=1,
            max_value=5,
            value=st.session_state.num_emergency_contacts,
            key="num_contacts_input"
        )
        st.session_state.num_emergency_contacts = num_contacts
        return num_contacts
    
    @staticmethod
    def render_contact_forms(num_contacts: int) -> List[Dict[str, str]]:
        """
        Render input forms for emergency contacts.
        Args:
            num_contacts: Number of contact forms to display
        Returns:
            List of emergency contact dictionaries
        """
        emergency_contacts = []
        
        for i in range(num_contacts):
            st.write(f"**Emergency Contact {i+1}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                contact_name = st.text_input(
                    "Name*",
                    key=f"ec_name_{i}",
                    placeholder="Contact name"
                )
            with col2:
                contact_phone = st.text_input(
                    "Phone*",
                    key=f"ec_phone_{i}",
                    placeholder="Phone number"
                )
            with col3:
                contact_relation = st.text_input(
                    "Relationship*",
                    key=f"ec_relation_{i}",
                    placeholder="Son/Daughter/Spouse"
                )
            if contact_name and contact_phone and contact_relation:
                emergency_contacts.append({
                    'name': contact_name,
                    'phone': contact_phone,
                    'relationship': contact_relation
                })
        return emergency_contacts





class PatientFormRenderer:
    """
    Renders the patient information form with all required fields.
    Organizes form into logical sections for better user experience.
    """
    @staticmethod
    def render_basic_information() -> Dict[str, Any]:
        """
        Render basic patient information section.
        
        Returns:
            Dictionary containing basic patient data
        """
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id_number = st.text_input(
                "Patient ID Number*",
                placeholder="e.g., P001, P002"
            )
            name = st.text_input("Full Name*")
            age = st.number_input("Age*", min_value=1, max_value=120, value=70)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            room_number = st.text_input("Room Number")
            stage = st.selectbox("Dementia Stage", ["Early", "Middle", "Late"])
        
        return {
            'patient_id_number': patient_id_number,
            'name': name,
            'age': age,
            'gender': gender,
            'room': room_number,
            'stage': stage
        }
    
    @staticmethod
    def render_doctor_information() -> Dict[str, str]:
        """
        Displays the doctor/GP information.
        Returns:
            Dictionary containing doctor information
        """
        st.divider()
        st.subheader("Doctor Information")
        
        col1, col2 = st.columns(2)
        with col1:
            gp_name = st.text_input("GP/Doctor Name*")
            gp_phone = st.text_input("GP Phone*")
        with col2:
            gp_practice = st.text_input("GP Practice/Clinic")
            gp_email = st.text_input("GP Email")
        return {
            'gp_name': gp_name,
            'gp_phone': gp_phone,
            'gp_practice': gp_practice,
            'gp_email': gp_email
        }
    
    @staticmethod
    def render_medical_information() -> Dict[str, str]:
        """
        Displays medical information.
        
        Returns:
            Dictionary containing medical information
        """
        st.divider()
        st.subheader("Medical Information")
        
        col1, col2 = st.columns(2)
        with col1:
            allergies = st.text_input("Allergies (if any)")
            medical_conditions = st.text_input("Medical Conditions")
        with col2:
            mobility = st.selectbox(
                "Mobility",
                ["Independent", "Walks with aid", "Wheelchair user", "Bedridden"]
            )
            dietary_requirements = st.text_input("Dietary Requirements")
        care_notes = st.text_area("Important Notes")
        return {
            'allergies': allergies,
            'medical_conditions': medical_conditions,
            'mobility': mobility,
            'dietary_requirements': dietary_requirements,
            'care_notes': care_notes
        }





class PatientValidator:
    """
    Validates patient data before saving to ensure data integrity.
    """
    @staticmethod
    def validate_required_fields(
        basic_info: Dict,
        emergency_contacts: List[Dict],
        doctor_info: Dict
    ) -> tuple[bool, str]:
   
        if not basic_info['patient_id_number']:
            return False, "Patient ID Number is required"
        
        if not basic_info['name']:
            return False, "Patient name is required"
        
        if not basic_info['age']:
            return False, "Patient age is required"
        
        if not emergency_contacts:
            return False, "At least one emergency contact is required"
        
        if not doctor_info['gp_name']:
            return False, "GP/Doctor name is required"
        
        if not doctor_info['gp_phone']:
            return False, "GP phone number is required"
        
        return True, ""
    
    @staticmethod
    def check_duplicate_id(patient_id: str, existing_patients: Dict) -> bool:
        """
        Check if patient ID already exists.
        
        Args:
            patient_id: Patient ID to check
            existing_patients: Dictionary of existing patients
            
        Returns:
            True if ID exists, False otherwise
        """
        existing_ids = [
            p.get('patient_id_number')
            for p in existing_patients.values()
        ]
        return patient_id in existing_ids


class PatientDataManager:
    """
    Manages patient data creation and storage in session state.
    """
    @staticmethod
    def create_patient_record(
        basic_info: Dict,
        doctor_info: Dict,
        medical_info: Dict,
        emergency_contacts: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create a complete patient record from form data.
        
        Args:
            basic_info: Basic patient information
            doctor_info: Doctor information
            medical_info: Medical information
            emergency_contacts: List of emergency contacts
            
        Returns:
            Complete patient data dictionary
        """
        patient_id = str(uuid.uuid4())
        
        return {
            'id': patient_id,
            'patient_id_number': basic_info['patient_id_number'],
            'name': basic_info['name'],
            'age': basic_info['age'],
            'dob': date.today().isoformat(),
            'gender': basic_info['gender'],
            'room': basic_info['room'],
            'diagnosis_date': date.today().isoformat(),
            'stage': basic_info['stage'],
            'address': '',
            'phone': '',
            'email': '',
            'gp_name': doctor_info['gp_name'],
            'gp_phone': doctor_info['gp_phone'],
            'gp_practice': doctor_info['gp_practice'],
            'gp_email': doctor_info['gp_email'],
            'emergency_contacts': emergency_contacts,
            'family_members': [],
            'allergies': medical_info['allergies'],
            'medical_conditions': medical_info['medical_conditions'],
            'mobility': medical_info['mobility'],
            'dietary_requirements': medical_info['dietary_requirements'],
            'care_notes': medical_info['care_notes'],
            'created_date': date.today().isoformat()
        }
    
    @staticmethod
    def save_patient(patient_data: Dict[str, Any]) -> None:
        """
        Save patient data to session state and initialize related data structures.
        Args:
            patient_data: Complete patient record to save
        """
        patient_id = patient_data['id']
        st.session_state.patients[patient_id] = patient_data
        st.session_state.tasks[patient_id] = []
        st.session_state.medications[patient_id] = []
        st.session_state.daily_logs[patient_id] = []


def render_page() -> None:
    """Main function to display the Add Patient page of the webapp."""
    st.title("Add New Patient")
    
    EmergencyContactManager.initialize_contact_count()
    num_contacts = EmergencyContactManager.render_contact_selector()
    emergency_contacts = EmergencyContactManager.render_contact_forms(num_contacts)
    
    st.divider()
    
    with st.form("add_patient_form"):
        basic_info = PatientFormRenderer.render_basic_information()
        doctor_info = PatientFormRenderer.render_doctor_information()
        medical_info = PatientFormRenderer.render_medical_information()
        
        submitted = st.form_submit_button("Save Patient", use_container_width=True)
    
    if submitted:
        is_valid, error_message = PatientValidator.validate_required_fields(
            basic_info,
            emergency_contacts,
            doctor_info
        )
        
        if not is_valid:
            st.error(f"Please fill in all required fields: {error_message}")
            return
        
        if PatientValidator.check_duplicate_id(
            basic_info['patient_id_number'],
            st.session_state.patients
        ):
            st.error(
                f"Patient ID {basic_info['patient_id_number']} already exists. "
                "Please use a different ID."
            )
            return
        
        patient_data = PatientDataManager.create_patient_record(
            basic_info,
            doctor_info,
            medical_info,
            emergency_contacts
        )
        PatientDataManager.save_patient(patient_data)
        
        st.success(
            f"Patient {basic_info['patient_id_number']} - "
            f"{basic_info['name']} added successfully"
        )
        st.session_state.num_emergency_contacts = 1
        
        if st.button("View Patient List"):
            st.switch_page("pages/patient_list.py")


if __name__ == "__main__":
    render_page()