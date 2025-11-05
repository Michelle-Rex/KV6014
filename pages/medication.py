import streamlit as st
from datetime import datetime, date, time as dt_time
from typing import Dict, List, Any, Optional
import uuid
"""
Handles medication tracking, scheduling, and administration recording.
This feature allows carers to add medications, schedule dosing times,
and record when medications are administered to patients.
"""


class MedicationFormRenderer:
    """
    medication input form.
    Handles all medication details including name, dosage, timing, and prescriber.
    """
    
    @staticmethod
    def render() -> Optional[Dict[str, Any]]:
        """
        medication input form.
        
        Returns:
            Dictionary containing medication data or None if cancelled
        """
        with st.form("add_medication_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                med_name = st.text_input(
                    "Medication Name*",
                    placeholder="e.g., Donepezil"
                )
                dosage = st.text_input(
                    "Dosage*",
                    placeholder="e.g., 10mg"
                )
                frequency = st.selectbox(
                    "Frequency",
                    ["Once daily", "Twice daily", "Three times daily",
                     "Four times daily", "As needed"]
                )
            
            with col2:
                med_time = st.time_input("Time*", value=dt_time(9, 0))
                route = st.selectbox(
                    "Route",
                    ["Oral", "Injection", "Topical", "Inhaler", "Eye drops"]
                )
                prescriber = st.text_input(
                    "Prescribed by",
                    placeholder="Dr. Smith"
                )
            
            purpose = st.text_area(
                "Purpose/Notes",
                placeholder="e.g., For memory improvement, Alzheimer's treatment"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=date.today())
            with col2:
                end_date = st.date_input("End Date (Optional)", value=None)
            
            submitted = st.form_submit_button("Save Medication", use_container_width=True)
            
            if submitted:
                if not (med_name and dosage and med_time):
                    st.error("Please fill in all required fields marked with *")
                    return None
                
                return {
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
            
            return None


class MedicationListRenderer:
    """
    Renders list of active and inactive medications.
    Provides interface for marking medications as given or discontinuing them.
    """
    
    @staticmethod
    def render_active_medications(
        patient_id: str,
        patient_name: str,
        medications: List[Dict[str, Any]]
    ) -> None:
        """
        Display active medications with action buttons.
        
        Args:
            patient_id: ID of the patient
            patient_name: Name of the patient
            medications: List of medication dictionaries
        """
        st.subheader(f"Current Medications for {patient_name}")
        
        active_meds = [med for med in medications if med.get('active', True)]
        
        if not active_meds:
            st.info("No active medications for this patient")
            return
        
        sorted_meds = sorted(active_meds, key=lambda x: x['time'])
        
        for med in sorted_meds:
            MedicationListRenderer._render_medication_card(patient_id, med)
    
    @staticmethod
    def _render_medication_card(patient_id: str, med: Dict[str, Any]) -> None:
        """
        Render a single medication card with details and actions.
        
        Args:
            patient_id: ID of the patient
            med: Medication dictionary
        """
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
                if st.button("Given", key=f"given_{med['id']}", use_container_width=True):
                    MedicationAdministrationLogger.log_administration(patient_id, med)
                    st.success(f"Marked '{med['name']}' as given")
                    st.rerun()
                
                if st.button("Stop", key=f"stop_{med['id']}", use_container_width=True):
                    med['active'] = False
                    st.success(f"Medication '{med['name']}' discontinued")
                    st.rerun()
    
    @staticmethod
    def render_inactive_medications(medications: List[Dict[str, Any]]) -> None:
        """
        Display history of discontinued medications.
        
        Args:
            medications: List of all medications
        """
        inactive_meds = [med for med in medications if not med.get('active', True)]
        
        if not inactive_meds:
            return
        
        with st.expander("Medication History (Discontinued)"):
            for med in inactive_meds:
                st.write(f"**{med['name']}** - {med['dosage']} at {med['time']}")
                st.write(f"Duration: {med['start_date']} to "
                        f"{med.get('end_date', 'Discontinued')}")
                st.divider()


class MedicationAdministrationLogger:
    """
    Logs medication administration events.
    Records when medications are given and by whom.
    """
    
    @staticmethod
    def log_administration(patient_id: str, med: Dict[str, Any]) -> None:
        """
        Log that a medication was administered.
        
        Args:
            patient_id: ID of the patient
            med: Medication dictionary
        """
        log_entry = {
            'id': str(uuid.uuid4()),
            'date': datetime.now().isoformat(),
            'medication': med['name'],
            'dosage': med['dosage'],
            'time_given': datetime.now().strftime('%H:%M'),
            'scheduled_time': med['time'],
            'given_by': "Carer"
        }
        
        if patient_id not in st.session_state.daily_logs:
            st.session_state.daily_logs[patient_id] = []
        
        today = datetime.now().date().isoformat()
        today_log = MedicationAdministrationLogger._find_or_create_today_log(
            patient_id,
            today
        )
        
        if 'medications_given' not in today_log:
            today_log['medications_given'] = []
        
        today_log['medications_given'].append(log_entry)
    
    @staticmethod
    def _find_or_create_today_log(patient_id: str, today: str) -> Dict[str, Any]:
        """
        Find or create today's log entry.
        
        Args:
            patient_id: ID of the patient
            today: Today's date in ISO format
            
        Returns:
            Today's log entry dictionary
        """
        for log in st.session_state.daily_logs[patient_id]:
            if log.get('date') == today:
                return log
        
        new_log = {
            'date': today,
            'medications_given': []
        }
        st.session_state.daily_logs[patient_id].append(new_log)
        return new_log


class MedicationManager:
    """
    Main medication management controller.
    Coordinates medication operations and display.
    """
    
    @staticmethod
    def add_medication(patient_id: str, medication: Dict[str, Any]) -> None:
        """
        Add a new medication to patient's medication list.
        
        Args:
            patient_id: ID of the patient
            medication: Medication dictionary to add
        """
        if patient_id not in st.session_state.medications:
            st.session_state.medications[patient_id] = []
        
        st.session_state.medications[patient_id].append(medication)
    
    @staticmethod
    def get_medications(patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all medications for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            List of medication dictionaries
        """
        return st.session_state.medications.get(patient_id, [])


def render_page() -> None:
    """Main function to render the Medication Management page."""
    st.title("Medication Management")
    
    patient_info = PatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    with st.expander("Add New Medication", expanded=False):
        medication_data = MedicationFormRenderer.render()
        
        if medication_data:
            MedicationManager.add_medication(patient_id, medication_data)
            st.success(f"Medication '{medication_data['name']}' added successfully")
            st.rerun()
    
    st.divider()
    
    medications = MedicationManager.get_medications(patient_id)
    
    MedicationListRenderer.render_active_medications(
        patient_id,
        patient_name,
        medications
    )
    
    MedicationListRenderer.render_inactive_medications(medications)


# Import PatientSelector from daily_logs (reusable component)
from pages.daily_logs import PatientSelector


if __name__ == "__main__":
    render_page()