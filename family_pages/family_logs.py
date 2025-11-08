import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
"""
Family Logs View Module
Read-only view for family members to see patient care logs.

Displays daily logs including vitals, nutrition, tasks completed, and notes.
Family members can view but not edit this information.
"""

class FamilyPatientSelector:
    """
    Allows family members to select which patient to view.

    **** This logic should be changed as it cause privacy issues ****
    """
    
    @staticmethod
    def render_selector() -> Optional[tuple[str, str]]:
        """
        """
        if not st.session_state.patients:
            st.warning("No patients registered in the system.")
            return None
        
        default_index = 0
        if st.session_state.current_patient:
            try:
                default_index = list(st.session_state.patients.keys()).index(
                    st.session_state.current_patient
                )
            except ValueError:
                default_index = 0
        
        patient_options = {
            pid: f"{p.get('patient_id_number', 'N/A')} - {p['name']}"
            for pid, p in st.session_state.patients.items()
        }
        
        selected_display = st.selectbox(
            "Select Your Loved One",
            options=list(patient_options.values()),
            index=default_index
        )
        
        selected_patient_id = [
            pid for pid, display in patient_options.items()
            if display == selected_display
        ][0]
        
        st.session_state.current_patient = selected_patient_id
        patient_name = st.session_state.patients[selected_patient_id]['name']
        
        return selected_patient_id, patient_name


class DateRangeSelector:
    """
    Handles date range selection for viewing logs.
    """
    
    @staticmethod
    def render() -> tuple[date, date]:
        """
        Render date range selector.
        
        Returns:
            Tuple of (start_date, end_date)
        """
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "From Date",
                value=date.today() - timedelta(days=7),
                max_value=date.today()
            )
        
        with col2:
            end_date = st.date_input(
                "To Date",
                value=date.today(),
                max_value=date.today()
            )
        
        DateRangeSelector._render_quick_buttons()
        
        return start_date, end_date
    
    @staticmethod
    def _render_quick_buttons() -> None:
        """Render quick date selection buttons."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Last 7 Days"):
                st.session_state.family_start = date.today() - timedelta(days=7)
                st.session_state.family_end = date.today()
                st.rerun()
        
        with col2:
            if st.button("Last 30 Days"):
                st.session_state.family_start = date.today() - timedelta(days=30)
                st.session_state.family_end = date.today()
                st.rerun()
        
        with col3:
            if st.button("This Month"):
                st.session_state.family_start = date(date.today().year, date.today().month, 1)
                st.session_state.family_end = date.today()
                st.rerun()


class LogSummaryCard:
    """
    Displays summary information for a single log entry.
    """
    
    @staticmethod
    def render(log: Dict[str, Any]) -> None:
        """
        Displays tehe care log card (A quick look out).

        """
        log_date = datetime.fromisoformat(log['date']).strftime('%A, %d %B %Y')
        
        with st.expander(f"{log_date} at {log.get('time', 'N/A')}"):
            tab1, tab2, tab3, tab4 = st.tabs([
                "Vitals", 
                "Nutrition & Meals", 
                "Tasks Completed", 
                "Notes"
            ])
            
            with tab1:
                LogSummaryCard._render_vitals(log)
            
            with tab2:
                LogSummaryCard._render_nutrition(log)
            
            with tab3:
                LogSummaryCard._render_tasks(log)
            
            with tab4:
                LogSummaryCard._render_notes(log)
    
    @staticmethod
    def _render_vitals(log: Dict[str, Any]) -> None:
        """Render vitals information."""
        st.subheader("Vital Signs")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Temperature", f"{log['vitals']['temperature']}°C")
            st.metric("Heart Rate", f"{log['vitals']['heart_rate']} bpm")
        
        with col2:
            st.metric("Blood Pressure", log['vitals']['blood_pressure'])
            st.metric("Oxygen", f"{log['vitals']['oxygen_saturation']}%")
        
        with col3:
            st.metric("Weight", f"{log['vitals']['weight']} kg")
        
        st.divider()
        st.subheader("Daily Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Mood:** {log['activities']['mood']}")
            st.write(f"**Sleep Quality:** {log['activities']['sleep_quality']}")
            st.write(f"**Appetite:** {log['activities']['appetite']}")
        
        with col2:
            st.write(f"**Activity Level:** {log['activities']['activity_level']}")
            st.write(f"**Social Engagement:** {log['activities']['social_engagement']}")
            st.write(f"**Communication:** {log['activities']['communication']}")
    
    @staticmethod
    def _render_nutrition(log: Dict[str, Any]) -> None:
        """Render nutrition and meals information."""
        st.subheader("Nutrition Summary")
        
        if not log.get('meals'):
            st.info("No meal information recorded")
            return
        
        meals = log['meals']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Calories", f"{meals.get('total_calories', 0)} kcal")
        
        with col2:
            st.metric("Total Fluids", f"{meals.get('total_fluids', 0)} ml")
        
        with col3:
            fluid_target = 2000
            percentage = (meals.get('total_fluids', 0) / fluid_target * 100)
            st.metric("Fluid Target", f"{percentage:.0f}%")
        
        st.divider()
        st.subheader("Meals Consumed")
        
        meal_info = [
            ("Breakfast", meals.get('breakfast', {})),
            ("Lunch", meals.get('lunch', {})),
            ("Dinner", meals.get('dinner', {}))
        ]
        
        for meal_name, meal_data in meal_info:
            if isinstance(meal_data, dict):
                amount = meal_data.get('amount', 'Not recorded')
                calories = meal_data.get('calories', 0)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{meal_name}:**")
                with col2:
                    st.write(f"{amount} consumed | {calories} kcal")
        
        if log.get('medications_given'):
            st.divider()
            st.subheader("Medications Given")
            for med in log['medications_given']:
                st.write(
                    f"- **{med['medication']}** ({med['dosage']}) at {med['time_given']}"
                )
    
    @staticmethod
    def _render_tasks(log: Dict[str, Any]) -> None:
        """Render tasks completed information."""
        st.subheader("Self-Care Tasks Completed")
        
        if not log.get('self_care'):
            st.info("No task information recorded")
            return
        
        completed_tasks = []
        not_completed = []
        
        task_labels = {
            'bathing': 'Bathing/Washing',
            'toileting': 'Toileting',
            'dressing': 'Dressing',
            'grooming': 'Grooming',
            'eating': 'Eating (Independent)',
            'mobility': 'Mobility (Independent)'
        }
        
        for task_key, task_label in task_labels.items():
            if log['self_care'].get(task_key, False):
                completed_tasks.append(task_label)
            else:
                not_completed.append(task_label)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Completed:**")
            if completed_tasks:
                for task in completed_tasks:
                    st.write(f"✅ {task}")
            else:
                st.write("None recorded")
        
        with col2:
            st.write("**Assistance Needed:**")
            if not_completed:
                for task in not_completed:
                    st.write(f"⚪ {task}")
            else:
                st.write("None")
    
    @staticmethod
    def _render_notes(log: Dict[str, Any]) -> None:
        """Render notes and observations."""
        st.subheader("Care Notes & Observations")
        
        if log.get('general_notes'):
            st.info(f"**General Notes:** {log['general_notes']}")
        
        if log.get('behavioral_changes'):
            st.warning(f"**Behavioral Changes:** {log['behavioral_changes']}")
        
        if log.get('incidents'):
            st.error(f"**Incidents:** {log['incidents']}")
        
        if not any([
            log.get('general_notes'),
            log.get('behavioral_changes'),
            log.get('incidents')
        ]):
            st.info("No additional notes recorded")
        
        st.divider()
        st.caption(f"Logged by: {log.get('logged_by', 'Unknown')}")


def render_page() -> None:
    """Main function to render the Family Logs page."""
    st.title("Care Logs - View Only")
    st.info("📖 This is a read-only view. Only care staff can edit logs.")
    
    patient_info = FamilyPatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    start_date, end_date = DateRangeSelector.render()
    
    st.divider()
    
    if patient_id not in st.session_state.daily_logs:
        st.info(f"No care logs available for {patient_name} yet")
        return
    
    all_logs = st.session_state.daily_logs[patient_id]
    
    filtered_logs = [
        log for log in all_logs
        if start_date.isoformat() <= log['date'] <= end_date.isoformat()
    ]
    
    if not filtered_logs:
        st.info(
            f"No logs found between {start_date.strftime('%d %b %Y')} and "
            f"{end_date.strftime('%d %b %Y')}"
        )
        return
    
    st.success(
        f"Found {len(filtered_logs)} care log(s) for {patient_name} between "
        f"{start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}"
    )
    
    sorted_logs = sorted(filtered_logs, key=lambda x: x['date'], reverse=True)
    
    for log in sorted_logs:
        LogSummaryCard.render(log)


if __name__ == "__main__":
    render_page()