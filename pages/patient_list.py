import streamlit as st
import pandas as pd
from typing import Dict, Any
"""
Patient List Module
Displays and manages the list of all registered dementia patients. This feature provides search, filter, and quick navigation capabilities
for accessing patient information and related features.
"""

class PatientFilter:
    """
    Handles filtering and searching of patient list.
    Provides search by ID/name and filter by dementia stage.
    """
    @staticmethod
    def render_search_controls() -> tuple[str, str, str]:
        """
        Render search and filter controls.
        
        Returns:
            Tuple of (search_term, stage_filter, sort_by)
        """
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search = st.text_input("Search", placeholder="Search by ID or name")
        
        with col2:
            stage_filter = st.selectbox(
                "Filter by Stage",
                ["All", "Early", "Middle", "Late"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["ID", "Name", "Age", "Room", "Recently Added"]
            )
        
        return search, stage_filter, sort_by
    
    @staticmethod
    def apply_filters(
        patients: Dict[str, Dict],
        search_term: str,
        stage_filter: str
    ) -> Dict[str, Dict]:
        """
        Apply search and filter criteria to patient list.
        
        Args:
            patients: Dictionary of all patients
            search_term: Search string to filter by
            stage_filter: Dementia stage to filter by
            
        Returns:
            Filtered dictionary of patients
        """
        filtered_patients = {}
        
        for patient_id, patient in patients.items():
            if not PatientFilter._matches_search(patient, search_term):
                continue
            
            if not PatientFilter._matches_stage(patient, stage_filter):
                continue
            
            filtered_patients[patient_id] = patient
        
        return filtered_patients
    
    @staticmethod
    def _matches_search(patient: Dict, search_term: str) -> bool:
        """
        Check if patient matches search criteria.
        
        Args:
            patient: Patient dictionary
            search_term: Search string
            
        Returns:
            True if patient matches search
        """
        if not search_term:
            return True
        
        search_lower = search_term.lower()
        
        return (
            search_lower in patient.get('patient_id_number', '').lower() or
            search_lower in patient['name'].lower() or
            search_lower in str(patient.get('room', '')).lower()
        )
    
    @staticmethod
    def _matches_stage(patient: Dict, stage_filter: str) -> bool:
        """
        Check if patient matches stage filter.
        
        Args:
            patient: Patient dictionary
            stage_filter: Stage to filter by
            
        Returns:
            True if patient matches stage filter
        """
        if stage_filter == "All":
            return True
        
        return patient.get('stage') == stage_filter


class PatientSorter:
    """
    Handles sorting of patient list by various criteria.
    """
    
    @staticmethod
    def sort_patients(
        patients: Dict[str, Dict],
        sort_by: str
    ) -> Dict[str, Dict]:
        """
        Sort patients by specified criteria.
        
        Args:
            patients: Dictionary of patients to sort
            sort_by: Sorting criteria
            
        Returns:
            Sorted dictionary of patients
        """
        sort_functions = {
            "ID": lambda x: x[1].get('patient_id_number', ''),
            "Name": lambda x: x[1]['name'],
            "Age": lambda x: x[1]['age'],
            "Room": lambda x: x[1].get('room', ''),
            "Recently Added": lambda x: x[1].get('created_date', '')
        }
        
        sort_func = sort_functions.get(sort_by)
        reverse = (sort_by == "Recently Added")
        
        return dict(sorted(patients.items(), key=sort_func, reverse=reverse))


class PatientCardRenderer:
    """
    Renders individual patient cards with summary information.
    """
    
    @staticmethod
    def render_card(patient_id: str, patient: Dict[str, Any]) -> None:
        """
        Render a patient information card.
        
        Args:
            patient_id: Patient's unique ID
            patient: Patient data dictionary
        """
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            PatientCardRenderer._render_basic_info(col1, patient)
            PatientCardRenderer._render_contacts(col2, patient)
            PatientCardRenderer._render_action_buttons(col3, patient_id)
            PatientCardRenderer._render_details_expander(patient)
    
    @staticmethod
    def _render_basic_info(col, patient: Dict[str, Any]) -> None:
        """
        Render basic patient information.
        
        Args:
            col: Streamlit column object
            patient: Patient data dictionary
        """
        with col:
            st.subheader(f"ID: {patient.get('patient_id_number', 'N/A')}")
            st.write(f"**Name:** {patient['name']}")
            st.write(
                f"**Age:** {patient['age']} | "
                f"**Gender:** {patient['gender']}"
            )
            st.write(
                f"**Room:** {patient.get('room', 'N/A')} | "
                f"**Stage:** {patient.get('stage', 'N/A')}"
            )
    
    @staticmethod
    def _render_contacts(col, patient: Dict[str, Any]) -> None:
        """
        Render emergency contacts and doctor information.
        
        Args:
            col: Streamlit column object
            patient: Patient data dictionary
        """
        with col:
            st.write("**Emergency Contacts:**")
            
            if patient.get('emergency_contacts'):
                for contact in patient['emergency_contacts']:
                    st.write(
                        f"{contact['name']} ({contact['relationship']})"
                    )
                    st.write(f"Phone: {contact['phone']}")
            else:
                st.write("No contacts listed")
            
            st.write("**Doctor:**")
            st.write(f"{patient.get('gp_name', 'N/A')}")
            st.write(f"Phone: {patient.get('gp_phone', 'N/A')}")
    
    @staticmethod
    def _render_action_buttons(col, patient_id: str) -> None:
        """
        Render quick action buttons for patient.
        
        Args:
            col: Streamlit column object
            patient_id: Patient's unique ID
        """
        with col:
            if st.button(
                "View Logs",
                key=f"logs_{patient_id}",
                use_container_width=True
            ):
                st.session_state.current_patient = patient_id
                st.switch_page("pages/daily_logs.py")
            
            if st.button(
                "Medications",
                key=f"meds_{patient_id}",
                use_container_width=True
            ):
                st.session_state.current_patient = patient_id
                st.switch_page("pages/medication.py")
            
            if st.button(
                "Tasks",
                key=f"tasks_{patient_id}",
                use_container_width=True
            ):
                st.session_state.current_patient = patient_id
                st.switch_page("pages/tasks.py")
    
    @staticmethod
    def _render_details_expander(patient: Dict[str, Any]) -> None:
        """
        Render expandable section with additional patient details.
        
        Args:
            patient: Patient data dictionary
        """
        with st.expander("More Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Mobility:** {patient.get('mobility', 'N/A')}")
                st.write(
                    f"**Allergies:** "
                    f"{patient.get('allergies', 'None listed')}"
                )
            
            with col2:
                st.write(
                    f"**Dietary:** "
                    f"{patient.get('dietary_requirements', 'None')}"
                )
                st.write(
                    f"**Medical Conditions:** "
                    f"{patient.get('medical_conditions', 'None')}"
                )
            
            if patient.get('care_notes'):
                st.write(f"**Care Notes:** {patient['care_notes']}")


class PatientExporter:
    """
    Handles exporting patient list to CSV format.
    """
    
    @staticmethod
    def export_to_csv(patients: Dict[str, Dict]) -> str:
        """
        Export patient list to CSV format.
        
        Args:
            patients: Dictionary of patients to export
            
        Returns:
            CSV string
        """
        patient_list = []
        
        for patient_id, patient in patients.items():
            emergency_names = ", ".join([
                c['name']
                for c in patient.get('emergency_contacts', [])
            ])
            
            emergency_phones = ", ".join([
                c['phone']
                for c in patient.get('emergency_contacts', [])
            ])
            
            patient_list.append({
                'Patient ID': patient.get('patient_id_number', ''),
                'Name': patient['name'],
                'Age': patient['age'],
                'Gender': patient['gender'],
                'Room': patient.get('room', ''),
                'Stage': patient.get('stage', ''),
                'Emergency Contacts': emergency_names,
                'Emergency Phones': emergency_phones,
                'GP': patient.get('gp_name', ''),
                'GP Phone': patient.get('gp_phone', '')
            })
        
        df = pd.DataFrame(patient_list)
        return df.to_csv(index=False)


def render_page() -> None:
    """Main function to render the Patient List page."""
    st.title("Patient List")
    
    search, stage_filter, sort_by = PatientFilter.render_search_controls()
    
    st.divider()
    
    if not st.session_state.patients:
        st.info("No patients registered yet.")
        if st.button("Add First Patient"):
            st.switch_page("pages/add_patient.py")
        st.stop()
    
    filtered_patients = PatientFilter.apply_filters(
        st.session_state.patients,
        search,
        stage_filter
    )
    
    sorted_patients = PatientSorter.sort_patients(filtered_patients, sort_by)
    
    st.write(f"**Showing {len(sorted_patients)} patient(s)**")
    
    for patient_id, patient in sorted_patients.items():
        PatientCardRenderer.render_card(patient_id, patient)
    
    if st.session_state.patients:
        st.divider()
        if st.button("Export Patient List to CSV"):
            csv_data = PatientExporter.export_to_csv(st.session_state.patients)
            
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="patient_list.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    render_page()