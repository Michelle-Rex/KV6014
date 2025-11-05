import streamlit as st
from datetime import datetime, date
from typing import Dict, Any, Optional
import uuid
"""
Daily Logs Module
Handles recording of daily care observations, vitals, and nutrition tracking.
This module provides comprehensive daily logging capabilities including vital signs,
activity assessments, meal tracking, and general observations for dementia patients.
"""

class PatientSelector:
    """
    Manages patient selection for daily log entry.
    Provides dropdown interface for selecting patients.
    """
    @staticmethod
    def render_selector() -> Optional[tuple[str, str]]:
        """
        """
        if not st.session_state.patients:
            st.warning("No patients registered. Please add a patient first.")
            if st.button("Add Patient"):
                st.switch_page("pages/add_patient.py")
            return None
        default_index = 0
        if st.session_state.current_patient:
            try:
                default_index = list(st.session_state.patients.keys()).index(
                    st.session_state.current_patient
                )
            except ValueError:
                default_index = 0
        
        patient_names = {
            pid: p['name'] 
            for pid, p in st.session_state.patients.items()
        }
        
        selected_patient_name = st.selectbox(
            "Select Patient",
            options=list(patient_names.values()),
            index=default_index
        )
        
        selected_patient_id = [
            pid for pid, name in patient_names.items() 
            if name == selected_patient_name
        ][0]
        
        st.session_state.current_patient = selected_patient_id
        return selected_patient_id, selected_patient_name


class VitalsFormRenderer:
    """
    Handles temperature, blood pressure, heart rate, oxygen saturation, and weight.
    """
    
    @staticmethod
    def render() -> Dict[str, Any]:
        """
        """
        st.write("### Vitals")
        col1, col2, col3 = st.columns(3)
        with col1:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=35.0,
                max_value=42.0,
                value=37.0,
                step=0.1
            )
            blood_pressure = st.text_input(
                "Blood Pressure",
                placeholder=""
            )
        with col2:
            heart_rate = st.number_input(
                "Heart Rate (bpm)",
                min_value=40,
                max_value=200,
                value=75
            )
            oxygen_saturation = st.number_input(
                "Oxygen (%)",
                min_value=70,
                max_value=100,
                value=98
            )
        
        with col3:
            weight = st.number_input(
                "Weight (kg)",
                min_value=30.0,
                max_value=200.0,
                value=70.0,
                step=0.1
            )
        
        return {
            'temperature': temperature,
            'blood_pressure': blood_pressure,
            'heart_rate': heart_rate,
            'respiratory_rate': 16,
            'oxygen_saturation': oxygen_saturation,
            'weight': weight
        }


class StatusFormRenderer:
    """
    """
    @staticmethod
    def render() -> Dict[str, str]:
        """
        """
        st.write("### Daily Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mood = st.select_slider(
                "Mood",
                options=["Very Low", "Low", "Neutral", "Good", "Very Good"],
                value="Neutral"
            )
            sleep_quality = st.select_slider(
                "Sleep",
                options=["Very Poor", "Poor", "Fair", "Good", "Excellent"],
                value="Fair"
            )
        with col2:
            appetite = st.select_slider(
                "Appetite",
                options=["None", "Poor", "Fair", "Good", "Excellent"],
                value="Good"
            )
            activity_level = st.select_slider(
                "Activity",
                options=["Bedridden", "Limited", "Moderate", "Active", "Very Active"],
                value="Moderate"
            )
        with col3:
            social_engagement = st.select_slider(
                "Social",
                options=["None", "Minimal", "Moderate", "Good", "Excellent"],
                value="Moderate"
            )
            communication = st.select_slider(
                "Communication",
                options=["Non-verbal", "Very Limited", "Limited", "Good", "Excellent"],
                value="Good"
            )
        return {
            'mood': mood,
            'sleep_quality': sleep_quality,
            'appetite': appetite,
            'activity_level': activity_level,
            'social_engagement': social_engagement,
            'communication': communication
        }


class NutritionFormRenderer:
    """
    Handles meal consumption, calorie tracking, and fluid intake.
    """
    
    @staticmethod
    def render() -> Dict[str, Any]:
        """
        """
        st.write("### Meals & Nutrition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            breakfast_eaten = st.select_slider(
                "Breakfast",
                options=["None", "25%", "50%", "75%", "100%"],
                value="75%"
            )
            lunch_eaten = st.select_slider(
                "Lunch",
                options=["None", "25%", "50%", "75%", "100%"],
                value="75%"
            )
            dinner_eaten = st.select_slider(
                "Dinner",
                options=["None", "25%", "50%", "75%", "100%"],
                value="75%"
            )
        
        with col2:
            breakfast_cal = st.number_input(
                "Breakfast Calories",
                min_value=0,
                max_value=1000,
                value=0,
                step=50
            )
            lunch_cal = st.number_input(
                "Lunch Calories",
                min_value=0,
                max_value=1000,
                value=0,
                step=50
            )
            dinner_cal = st.number_input(
                "Dinner Calories",
                min_value=0,
                max_value=1000,
                value=0,
                step=50
            )
        
        total_fluids = st.number_input(
            "Total Fluids (ml)",
            min_value=0,
            max_value=5000,
            value=0,
            step=100
        )
        
        total_calories = breakfast_cal + lunch_cal + dinner_cal
        
        st.info(
            f"Total Daily Calories: {total_calories} kcal | "
            f"Total Fluids: {total_fluids} ml"
        )
        
        return {
            'breakfast': {'amount': breakfast_eaten, 'calories': breakfast_cal},
            'lunch': {'amount': lunch_eaten, 'calories': lunch_cal},
            'dinner': {'amount': dinner_eaten, 'calories': dinner_cal},
            'total_calories': total_calories,
            'total_fluids': total_fluids
        }


class NotesFormRenderer:
    """
    Displays the notes and observations.
    Handles general notes and incident reporting.
    """
    
    @staticmethod
    def render() -> Dict[str, str]:
        """
        """
        st.write("### Notes")
        
        general_notes = st.text_area(
            "General Notes",
            placeholder="Any important observations"
        )
        
        incidents = st.text_area(
            "Incidents/Issues",
            placeholder="Any falls, behavioral issues, etc."
        )
        
        carer_name = st.text_input("Logged by", value="Carer")
        
        return {
            'general_notes': general_notes,
            'incidents': incidents,
            'logged_by': carer_name
        }


class DailyLogManager:
    """
    Manages creation and storage of daily log entries.
    """
    
    @staticmethod
    def create_log_entry(
        log_date: date,
        vitals: Dict,
        activities: Dict,
        meals: Dict,
        notes: Dict
    ) -> Dict[str, Any]:

        return {
            'id': str(uuid.uuid4()),
            'date': log_date.isoformat(),
            'time': datetime.now().strftime('%H:%M'),
            'timestamp': datetime.now().isoformat(),
            'vitals': vitals,
            'activities': activities,
            'self_care': {
                'bathing': False,
                'toileting': False,
                'dressing': False,
                'grooming': False,
                'eating': False,
                'mobility': False
            },
            'meals': meals,
            'general_notes': notes['general_notes'],
            'incidents': notes['incidents'],
            'logged_by': notes['logged_by']
        }
    
    @staticmethod
    def save_log(patient_id: str, log_entry: Dict[str, Any]) -> None:
        """
        """
        if patient_id not in st.session_state.daily_logs:
            st.session_state.daily_logs[patient_id] = []
        
        st.session_state.daily_logs[patient_id].append(log_entry)


class RecentLogsDisplay:
    """
    Displays recent log entries for quick review.
    """
    
    @staticmethod
    def render(patient_id: str, patient_name: str, num_logs: int = 3) -> None:
        """
        Display recent log entries.
        
        patient_id: ID of the patient
        patient_name: Name of the patient
        num_logs: Number of recent logs to display (default: 3)
        """
        st.divider()
        st.subheader("Recent Logs")
        
        if patient_id not in st.session_state.daily_logs:
            st.info("No logs recorded yet for this patient")
            return
        
        logs = st.session_state.daily_logs[patient_id]
        
        if not logs:
            st.info("No logs recorded yet for this patient")
            return
        
        sorted_logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        
        for log in sorted_logs[:num_logs]:
            RecentLogsDisplay._render_log_summary(log)
        
        if st.button("View All Logs"):
            st.switch_page("pages/historical_logs.py")
    
    @staticmethod
    def _render_log_summary(log: Dict[str, Any]) -> None:
        """
        Display a single log entry summary.

        """
        with st.expander(
            f"{log['date']} at {log['time']} - by {log['logged_by']}"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Vitals:**")
                st.write(f"Temp: {log['vitals']['temperature']}°C | "
                        f"BP: {log['vitals']['blood_pressure']}")
                st.write(f"Heart Rate: {log['vitals']['heart_rate']} bpm | "
                        f"O2: {log['vitals']['oxygen_saturation']}%")
                
                st.write("**Status:**")
                st.write(f"Mood: {log['activities']['mood']} | "
                        f"Sleep: {log['activities']['sleep_quality']}")
                st.write(f"Appetite: {log['activities']['appetite']}")
            
            with col2:
                if log.get('meals'):
                    st.write("**Nutrition:**")
                    st.write(f"Calories: {log['meals'].get('total_calories', 0)} kcal")
                    st.write(f"Fluids: {log['meals'].get('total_fluids', 0)} ml")
                
                if log.get('incidents'):
                    st.warning(f"**Incidents:** {log['incidents']}")
            
            if log.get('general_notes'):
                st.write(f"**Notes:** {log['general_notes']}")


def render_page() -> None:
    """Main function to render the Daily Care Log page."""
    st.title("Daily Care Log")
    
    patient_info = PatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    with st.form("daily_log_form", clear_on_submit=True):
        log_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today()
        )
        
        vitals = VitalsFormRenderer.render()
        activities = StatusFormRenderer.render()
        meals = NutritionFormRenderer.render()
        notes = NotesFormRenderer.render()
        
        submitted = st.form_submit_button("Save Log", use_container_width=True)
    
    if submitted:
        log_entry = DailyLogManager.create_log_entry(
            log_date,
            vitals,
            activities,
            meals,
            notes
        )
        
        DailyLogManager.save_log(patient_id, log_entry)
        
        st.success(f"Log saved for {patient_name}")
        st.rerun()
    
    RecentLogsDisplay.render(patient_id, patient_name)


if __name__ == "__main__":
    render_page()