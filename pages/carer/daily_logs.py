import streamlit as st
from datetime import datetime, date
import uuid

st.title("Daily Care Log")
db = st.session_state.db

patients = db.get_all_patients()

if not patients:
    st.warning("No patients registered")
    if st.button("Add Patient"):
        st.switch_page("pages/carer/add_patient.py")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in patients}

if 'current_patient' in st.session_state and st.session_state.current_patient:
    default_idx = list(patient_options.keys()).index(st.session_state.current_patient) if st.session_state.current_patient in patient_options else 0
else:
    default_idx = 0

selected_display = st.selectbox("Select Patient", list(patient_options.values()), index=default_idx)
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()

with st.form("daily_log_form", clear_on_submit=True):
    log_date = st.date_input("Date", value=date.today(), max_value=date.today())
    
    st.write("### Vitals")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.number_input("Temperature (C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
        blood_pressure = st.text_input("Blood Pressure", placeholder="120/80")
    
    with col2:
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75)
        oxygen = st.number_input("Oxygen (%)", min_value=70, max_value=100, value=98)
    
    with col3:
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    
    st.write("### Daily Status")
    col1, col2 = st.columns(2)
    
    with col1:
        mood = st.select_slider("Mood", ["Very Low","Low","Neutral","Good","Very Good"], value="Neutral")
        sleep = st.select_slider("Sleep", ["VeryPoor","Poor", "Fair", "Good","Excellent"], value="Fair")
        appetite = st.select_slider("Appetite", ["None","Poor","Fair","Good","Excellent"], value="Good")
    
    with col2:
        activity = st.select_slider("Activity", ["Bedridden","Limited", "Moderate", "Active", "Very Active"], value="Moderate")
        social = st.select_slider("Social", ["None", "Minimal","Moderate","Good","Excellent"], value="Moderate")
    
    st.write("### Meals")
    col1, col2 = st.columns(2)
    
    with col1:
        breakfast_amt = st.select_slider("Breakfast", ["None","25%", "50%","75%","100%"], value="75%")
        lunch_amt = st.select_slider("Lunch", ["None", "25%","50%", "75%", "100%"], value="75%")
        dinner_amt = st.select_slider("Dinner", ["None","25%","50%","75%","100%"], value="75%")
    
    with col2:
        breakfast_cal = st.number_input("Breakfast Calories", 0, 1000, 0, 50)
        lunch_cal = st.number_input("Lunch Calories", 0, 1000, 0, 50)
        dinner_cal = st.number_input("Dinner Calories", 0, 1000, 0, 50)
    
    total_cal = breakfast_cal + lunch_cal + dinner_cal
    st.info(f"Total Calories: {total_cal} kcal")
    
    st.write("### Notes")
    notes = st.text_area("General Notes")
    incidents = st.text_area("Incidents")
    
    carer_name = st.text_input("Logged by", value="Carer")
    
    submitted = st.form_submit_button("Save Log")

if submitted:
    log_data = {
        'patient_id': selected_patient_id,
        'log_date': log_date.isoformat(),
        'log_time': datetime.now().strftime('%H:%M'),
        'temperature': temperature,
        'blood_pressure': blood_pressure,
        'heart_rate': heart_rate,
        'oxygen_saturation': oxygen,
        'weight': weight,
        'mood': mood,
        'sleep_quality': sleep,
        'appetite': appetite,
        'activity_level': activity,
        'social_engagement': social,
        'general_notes': notes,
        'incidents': incidents,
        'meals': {
            'Breakfast': {'amount': breakfast_amt, 'calories': breakfast_cal},
            'Lunch': {'amount': lunch_amt, 'calories': lunch_cal},
            'Dinner': {'amount': dinner_amt, 'calories': dinner_cal}
        }
    }
    
    log_id = db.add_daily_log(log_data)
    
    if log_id:
        st.success("Log saved successfully")
        st.rerun()
    else:
        st.error("Failed to save log")

st.divider()
st.subheader("Recent Logs")



logs = db.get_patient_logs(selected_patient_id)
if logs:
    for log in logs[:3]:
        with st.expander(f"{log['date']} at {log['time']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Vitals:**")
                st.write(f"Temp: {log['vitals']['temperature']}C | BP: {log['vitals']['blood_pressure']}")
                st.write(f"Heart Rate: {log['vitals']['heart_rate']} | O2: {log['vitals']['oxygen_saturation']}%")
                st.write("**Status:**")
                st.write(f"Mood: {log['activities']['mood']}")
                st.write(f"Appetite: {log['activities']['appetite']}")
            
            with col2:
                st.write("**Nutrition:**")
                st.write(f"Total Calories: {log['total_calories']} kcal")
                if log.get('general_notes'):
                    st.write(f"**Notes:** {log['general_notes']}")
else:
    st.info("No logs recorded yet")