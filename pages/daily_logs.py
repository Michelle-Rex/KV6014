import streamlit as st
from datetime import datetime, date
import uuid

st.title("Daily Care Log")

if not st.session_state.patients:
    st.warning("No patients registered. Please add a patient first.")
    if st.button("Add Patient"):
        st.switch_page("pages/add_patient.py")
    st.stop()

if st.session_state.current_patient:
    default_index = list(st.session_state.patients.keys()).index(st.session_state.current_patient)
else:
    default_index = 0

patient_names = {pid: p['name'] for pid, p in st.session_state.patients.items()}
selected_patient_name = st.selectbox("Select Patient", options=list(patient_names.values()), index=default_index)
selected_patient_id = [pid for pid, name in patient_names.items() if name == selected_patient_name][0]
st.session_state.current_patient = selected_patient_id

st.divider()

with st.form("daily_log_form", clear_on_submit=True):
    log_date = st.date_input("Date", value=date.today(), max_value=date.today())
    
    st.write("### Vitals")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
        blood_pressure = st.text_input("Blood Pressure", placeholder="120/80")
    
    with col2:
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75)
        oxygen_saturation = st.number_input("Oxygen (%)", min_value=70, max_value=100, value=98)
    
    with col3:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    
    st.write("### Daily Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mood = st.select_slider("Mood", options=["Very Low", "Low", "Neutral", "Good", "Very Good"], value="Neutral")
        sleep_quality = st.select_slider("Sleep", options=["Very Poor", "Poor", "Fair", "Good", "Excellent"], value="Fair")
    
    with col2:
        appetite = st.select_slider("Appetite", options=["None", "Poor", "Fair", "Good", "Excellent"], value="Good")
        activity_level = st.select_slider("Activity", options=["Bedridden", "Limited", "Moderate", "Active", "Very Active"], value="Moderate")
    
    with col3:
        social_engagement = st.select_slider("Social", options=["None", "Minimal", "Moderate", "Good", "Excellent"], value="Moderate")
        communication = st.select_slider("Communication", options=["Non-verbal", "Very Limited", "Limited", "Good", "Excellent"], value="Good")
    
    st.write("### Meals & Nutrition")
    
    col1, col2 = st.columns(2)
    with col1:
        breakfast_eaten = st.select_slider("Breakfast", options=["None", "25%", "50%", "75%", "100%"], value="75%")
        lunch_eaten = st.select_slider("Lunch", options=["None", "25%", "50%", "75%", "100%"], value="75%")
        dinner_eaten = st.select_slider("Dinner", options=["None", "25%", "50%", "75%", "100%"], value="75%")
    
    with col2:
        breakfast_cal = st.number_input("Breakfast Calories", min_value=0, max_value=1000, value=0, step=50)
        lunch_cal = st.number_input("Lunch Calories", min_value=0, max_value=1000, value=0, step=50)
        dinner_cal = st.number_input("Dinner Calories", min_value=0, max_value=1000, value=0, step=50)
    
    total_fluids = st.number_input("Total Fluids (ml)", min_value=0, max_value=5000, value=0, step=100)
    
    total_calories = breakfast_cal + lunch_cal + dinner_cal
    st.info(f"Total Daily Calories: {total_calories} kcal | Total Fluids: {total_fluids} ml")
    
    st.write("### Notes")
    general_notes = st.text_area("General Notes", placeholder="Any important observations")
    incidents = st.text_area("Incidents/Issues", placeholder="Any falls, behavioral issues, etc.")
    
    carer_name = st.text_input("Logged by", value="Carer")
    
    submitted = st.form_submit_button("Save Log", use_container_width=True)

if submitted:
    log_entry = {
        'id': str(uuid.uuid4()),
        'date': log_date.isoformat(),
        'time': datetime.now().strftime('%H:%M'),
        'timestamp': datetime.now().isoformat(),
        'vitals': {
            'temperature': temperature,
            'blood_pressure': blood_pressure,
            'heart_rate': heart_rate,
            'respiratory_rate': 16,
            'oxygen_saturation': oxygen_saturation,
            'weight': weight
        },
        'activities': {
            'mood': mood,
            'sleep_quality': sleep_quality,
            'appetite': appetite,
            'activity_level': activity_level,
            'social_engagement': social_engagement,
            'communication': communication
        },
        'self_care': {
            'bathing': False,
            'toileting': False,
            'dressing': False,
            'grooming': False,
            'eating': False,
            'mobility': False
        },
        'meals': {
            'breakfast': {'amount': breakfast_eaten, 'calories': breakfast_cal},
            'lunch': {'amount': lunch_eaten, 'calories': lunch_cal},
            'dinner': {'amount': dinner_eaten, 'calories': dinner_cal},
            'total_calories': total_calories,
            'total_fluids': total_fluids
        },
        'general_notes': general_notes,
        'incidents': incidents,
        'logged_by': carer_name
    }
    
    if selected_patient_id not in st.session_state.daily_logs:
        st.session_state.daily_logs[selected_patient_id] = []
    
    st.session_state.daily_logs[selected_patient_id].append(log_entry)
    st.success(f"Log saved for {selected_patient_name}")
    st.rerun()

st.divider()

st.subheader("Recent Logs")

if selected_patient_id in st.session_state.daily_logs and st.session_state.daily_logs[selected_patient_id]:
    logs = st.session_state.daily_logs[selected_patient_id]
    sorted_logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
    
    for log in sorted_logs[:3]:
        with st.expander(f"{log['date']} at {log['time']} - by {log['logged_by']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Vitals:**")
                st.write(f"Temp: {log['vitals']['temperature']}°C | BP: {log['vitals']['blood_pressure']}")
                st.write(f"Heart Rate: {log['vitals']['heart_rate']} bpm | O2: {log['vitals']['oxygen_saturation']}%")
                
                st.write("**Status:**")
                st.write(f"Mood: {log['activities']['mood']} | Sleep: {log['activities']['sleep_quality']}")
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
    
    if st.button("View All Logs"):
        st.switch_page("pages/historical_logs.py")
else:
    st.info("No logs recorded yet for this patient")