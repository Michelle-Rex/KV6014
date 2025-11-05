import streamlit as st
from datetime import  date
from typing import Dict, Any
"""
Dashboard Module
Main overview page displaying key metrics and quick access to patient information.

This module provides carers with a comprehensive overview of daily priorities,
including pending tasks, medication schedules, and patient quick access cards.
"""

class DashboardMetrics:
    """
    Calculates and displays dashboard statistics.
    """
    
    @staticmethod
    def render() -> None:
        """Render key metrics in the dashboard header."""
        col1, col2, col3, col4 = st.columns(4)
        
        total_patients = DashboardMetrics._count_total_patients()
        pending_tasks = DashboardMetrics._count_pending_tasks()
        today_medications = DashboardMetrics._count_today_medications()
        today_logs = DashboardMetrics._count_today_logs()
        
        with col1:
            st.metric("Total Patients", total_patients)
        
        with col2:
            st.metric("Pending Tasks", pending_tasks)
        
        with col3:
            st.metric("Today's Medications", today_medications)
        
        with col4:
            st.metric("Logs Today", today_logs)
    
    @staticmethod
    def _count_total_patients() -> int:
        """
        Count total number of registered patients.
        
        Returns:
            Number of patients
        """
        return len(st.session_state.patients)
    
    @staticmethod
    def _count_pending_tasks() -> int:
        """
        Counts total number of pending tasks across all patients.
        
        Returns:
            Number of pending tasks
        """
        pending_count = 0
        for patient_id, task_list in st.session_state.tasks.items():
            pending_count += sum(
                1 for task in task_list
                if not task.get('completed', False)
            )
        return pending_count
    
    @staticmethod
    def _count_today_medications() -> int:
        """
        Counts total medications scheduled for today.

        """
        medication_count = 0
        for patient_id, meds in st.session_state.medications.items():
            medication_count += len(meds)
        return medication_count
    
    @staticmethod
    def _count_today_logs() -> int:
        """
        Counts the number of logs recorded today.
        """
        today = date.today().isoformat()
        log_count = 0
        
        for logs in st.session_state.daily_logs.values():
            log_count += sum(
                1 for log in logs
                if log.get('date') == today
            )
        
        return log_count


class TaskOverview:
    """
    Displays overview of pending tasks by patient.
    """
    
    @staticmethod
    def render() -> None:
        """Render pending tasks overview."""
        st.subheader("Pending Tasks")
        
        if not st.session_state.tasks:
            st.info("No pending tasks")
            return
        
        has_pending = False
        
        for patient_id, task_list in st.session_state.tasks.items():
            patient_name = st.session_state.patients.get(
                patient_id, {}
            ).get('name', 'Unknown')
            
            pending_tasks = [
                task for task in task_list
                if not task.get('completed', False)
            ]
            
            if pending_tasks:
                has_pending = True
                st.write(f"**{patient_name}**")
                
                for task in pending_tasks:
                    priority_emoji = TaskOverview._get_priority_emoji(
                        task.get('priority', 'Low')
                    )
                    task_text = f"{priority_emoji} {task['task']}"
                    
                    if task.get('time'):
                        task_text += f" (at {task['time']})"
                    
                    st.write(f"  - {task_text}")
        
        if not has_pending:
            st.info("No pending tasks")
    
    @staticmethod
    def _get_priority_emoji(priority: str) -> str:
        """
        Get emoji indicator for task priority.
        
        Args:
            priority: Priority level
            
        Returns:
            Emoji string
        """
        priority_emojis = {
            "Urgent": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }
        return priority_emojis.get(priority, "⚪")


class MedicationSchedule:
    """
    Displays today's medication schedule by patient.
    """
    
    @staticmethod
    def render() -> None:
        """Render medication schedule overview."""
        st.subheader("Today's Medications")
        
        if not st.session_state.medications:
            st.info("No medications scheduled")
            return
        
        has_medications = False
        
        for patient_id, meds in st.session_state.medications.items():
            patient_name = st.session_state.patients.get(
                patient_id, {}
            ).get('name', 'Unknown')
            
            active_meds = [
                med for med in meds
                if med.get('active', True)
            ]
            
            if active_meds:
                has_medications = True
                st.write(f"**{patient_name}**")
                
                sorted_meds = sorted(active_meds, key=lambda x: x['time'])
                
                for med in sorted_meds:
                    st.write(
                        f"  - {med['time']}: {med['name']} ({med['dosage']})"
                    )
        
        if not has_medications:
            st.info("No medications scheduled")


class PatientQuickAccess:
    """
    Displays patient cards for quick access to patient information.
    """
    
    @staticmethod
    def render() -> None:
        """
        """
        st.subheader("Quick Patient Access")
        
        if not st.session_state.patients:
            st.info("No patients registered yet. Add a patient to get started.")
            if st.button("Add Patient"):
                st.switch_page("pages/add_patient.py")
            return
        
        cols = st.columns(3)
        
        for idx, (patient_id, patient) in enumerate(
            st.session_state.patients.items()
        ):
            with cols[idx % 3]:
                PatientQuickAccess._render_patient_card(patient_id, patient)
    
    @staticmethod
    def _render_patient_card(patient_id: str, patient: Dict[str, Any]) -> None:
        """
        """
        with st.container(border=True):
            st.write(f"**{patient['name']}**")
            st.write(f"ID: {patient.get('patient_id_number', 'N/A')}")
            st.write(f"Age: {patient['age']}")
            st.write(f"Room: {patient.get('room', 'N/A')}")
            
            if st.button(
                "View Details",
                key=f"view_{patient_id}",
                use_container_width=True
            ):
                st.session_state.current_patient = patient_id
                st.switch_page("pages/daily_logs.py")


class DashboardLayoutManager:
    """
    Manages the overall dashboard layout and component arrangement.
    """
    
    @staticmethod
    def render() -> None:
        """"""
        st.title("Dashboard")
        
        DashboardMetrics.render()
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            TaskOverview.render()
        
        with col2:
            MedicationSchedule.render()
        
        st.divider()
        
        PatientQuickAccess.render()


def render_page() -> None:
    """Main function to start the Dashboard page."""
    DashboardLayoutManager.render()


if __name__ == "__main__":
    render_page()