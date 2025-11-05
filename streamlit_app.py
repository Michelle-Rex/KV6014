import streamlit as st
from datetime import datetime
from typing import Dict, Any


class SessionManager:
    """
    Manages application session state and initialization.
    Ensures all required session state variables are properly initialized.
    """
    
    @staticmethod
    def initialize_session_state() -> None:
        """Initialize all session state variables if they don't exist."""
        default_states = {
            'patients': {},
            'current_patient': None,
            'medications': {},
            'daily_logs': {},
            'tasks': {},
            'memory_book': {},
            'num_emergency_contacts': 1,
            'user_role': None,
            'selected_role': None
        }
        
        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value


class RoleSelector:
    """
    Handles user role selection (Carer or Family Member).
    """
    
    @staticmethod
    def render() -> str:
        """
        Render role selection interface.
        
        Returns:
            Selected role
        """
        st.title("Dementia Care Manager")
        st.subheader("Select Your Role")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            role = st.radio(
                "I am a:",
                ["Carer", "Family Member"],
                key="role_selector"
            )
            
            if st.button("Continue", use_container_width=True):
                st.session_state.selected_role = role
                st.rerun()
        
        return role


class MedicationAlertSystem:
    """
    Handles medication alerts and notifications for carers.
    Displays alerts for medications due within the next 30 minutes.
    """
    
    @staticmethod
    def get_upcoming_alerts(medications: Dict, patients: Dict, time_window: int = 30) -> list:
        """
        Get list of medications due within specified time window.
        
        Args:
            medications: Dictionary of patient medications
            patients: Dictionary of patient information
            time_window: Alert window in minutes
            
        Returns:
            List of alert dictionaries
        """
        current_time = datetime.now().time()
        current_minutes = current_time.hour * 60 + current_time.minute
        alerts = []
        
        for patient_id, meds in medications.items():
            patient_name = patients.get(patient_id, {}).get('name', 'Unknown')
            
            for med in meds:
                if not med.get('active', True):
                    continue
                
                try:
                    med_time = datetime.strptime(med['time'], '%H:%M').time()
                    med_minutes = med_time.hour * 60 + med_time.minute
                    time_diff = med_minutes - current_minutes
                    
                    if 0 <= time_diff <= time_window:
                        alerts.append({
                            'patient': patient_name,
                            'medication': med['name'],
                            'time': med['time'],
                            'minutes': time_diff
                        })
                except (ValueError, KeyError):
                    continue
        
        return alerts
    
    @staticmethod
    def display_alerts(alerts: list) -> None:
        """
        Display medication alerts in the sidebar.
        
        Args:
            alerts: List of alert dictionaries
        """
        if alerts:
            for alert in alerts:
                st.warning(
                    f"**{alert['patient']}**\n"
                    f"{alert['medication']} at {alert['time']}\n"
                    f"(in {alert['minutes']} min)"
                )
        else:
            st.info("No upcoming medications in next 30 mins")


class NavigationManager:
    """
    Manages application navigation and page routing based on user role.
    """
    
    @staticmethod
    def get_carer_pages() -> Dict[str, list]:
        """
        Define pages available to carers.
        
        Returns:
            Dictionary mapping section names to lists of pages
        """
        return {
            "Dashboard": [
                st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
            ],
            "Patient Management": [
                st.Page("pages/patient_list.py", title="Patient List", icon="👥"),
                st.Page("pages/add_patient.py", title="Add New Patient", icon="➕"),
            ],
            "Daily Care": [
                st.Page("pages/daily_logs.py", title="Daily Logs", icon="📝"),
                st.Page("pages/medication.py", title="Medications", icon="💊"),
                st.Page("pages/tasks.py", title="Task Checklist", icon="✅"),
            ],
            "History": [
                st.Page("pages/historical_logs.py", title="Historical Logs", icon="📆"),
            ],
            "Memory Book": [
                st.Page("pages/memory_book.py", title="Photos & Media", icon="📷"),
            ],
        }
    
    @staticmethod
    def get_family_pages() -> Dict[str, list]:
        """
        Define pages available to family members.
        
        Returns:
            Dictionary mapping section names to lists of pages
        """
        return {
            "View Care Records": [
                st.Page("family_pages/family_logs.py", title="Care Logs", icon="📝"),
            ],
            "Memory Book": [
                st.Page("family_pages/family_memory_book.py", title="Photos & Media", icon="📷"),
            ],
        }


class SidebarManager:
    """
    Manages the sidebar content based on user role.
    """
    
    @staticmethod
    def render_sidebar(role: str) -> None:
        """
        Render the complete sidebar with header and role-specific content.
        
        Args:
            role: User role (Carer or Family Member)
        """
        with st.sidebar:
            SidebarManager._render_header(role)
            st.divider()
            
            if role == "Carer":
                SidebarManager._render_medication_alerts()
            
            st.divider()
            if st.button("Change Role", use_container_width=True):
                st.session_state.selected_role = None
                st.rerun()
    
    @staticmethod
    def _render_header(role: str) -> None:
        """
        Render sidebar header with title, role, and current time.
        
        Args:
            role: User role
        """
        st.title("Dementia Care Manager")
        st.write(f"**Role:** {role}")
        current_time = datetime.now().strftime('%d %B %Y, %H:%M')
        st.write(f"**Current Time:** {current_time}")
    
    @staticmethod
    def _render_medication_alerts() -> None:
        """Render medication alert section in sidebar for carers."""
        st.subheader("Medication Alerts")
        
        alerts = MedicationAlertSystem.get_upcoming_alerts(
            st.session_state.medications,
            st.session_state.patients
        )
        
        if st.session_state.medications:
            MedicationAlertSystem.display_alerts(alerts)
        else:
            st.info("No medications scheduled")


def configure_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Dementia Care Manager",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def main() -> None:
    """
    Main application entry point.
    Initializes session, renders UI, and handles navigation based on role.
    """
    configure_page()
    SessionManager.initialize_session_state()
    
    if not st.session_state.selected_role:
        RoleSelector.render()
        st.stop()
    
    role = st.session_state.selected_role
    
    SidebarManager.render_sidebar(role)
    
    if role == "Carer":
        pages = NavigationManager.get_carer_pages()
    else:
        pages = NavigationManager.get_family_pages()
    
    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    main()
