import streamlit as st
from datetime import datetime, date, timedelta

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("Access Denied: This page is only accessible to family members.")
    st.stop()

st.title("Care Logs")
db = st.session_state.db

family_patients = db.get_family_patients(st.session_state.user_id)

if not family_patients:
    st.warning("No patients linked to your account")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in family_patients}
selected_display = st.selectbox("Select Patient", list(patient_options.values()))
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()

view_mode = st.radio("View Mode", ["Recent Logs", "Date Range"], horizontal=True)

if view_mode == "Recent Logs":
    num_days = st.selectbox("Show logs from", ["Last 7 days", "Last 30 days", "Last 90 days"])
    
    if num_days == "Last 7 days":
        days = 7
    elif num_days == "Last 30 days":
        days = 30
    else:
        days = 90
    
    start_date = (date.today() - timedelta(days=days)).isoformat()
    end_date = date.today().isoformat()
    
else:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", value=date.today())
    
    start_date = start_date.isoformat()
    end_date = end_date.isoformat()

st.divider()

logs = db.get_patient_logs(selected_patient_id, start_date, end_date)

if logs:
    st.success(f"Found {len(logs)} logs")
    
    for log in logs:
        log_date = datetime.fromisoformat(log['date']).strftime('%A, %d %B %Y')
        
        with st.expander(f"{log_date} at {log['time']}"):
            tab1, tab2, tab3 = st.tabs(["Vitals", "Daily Status", "Nutrition"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Temperature", f"{log['vitals']['temperature']}°C")
                    st.metric("Heart Rate", f"{log['vitals']['heart_rate']} bpm")
                with col2:
                    st.metric("Blood Pressure", log['vitals']['blood_pressure'])
                    st.metric("Oxygen", f"{log['vitals']['oxygen_saturation']}%")
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Mood:** {log['activities']['mood']}")
                    st.write(f"**Sleep Quality:** {log['activities']['sleep_quality']}")
                    st.write(f"**Appetite:** {log['activities']['appetite']}")
                with col2:
                    st.write(f"**Activity Level:** {log['activities']['activity_level']}")
                    st.write(f"**Social Engagement:** {log['activities']['social_engagement']}")
                
                if log['general_notes']:
                    st.info(f"**Notes:** {log['general_notes']}")
            
            with tab3:
                if log['meals']:
                    for meal_type, meal_data in log['meals'].items():
                        st.write(f"**{meal_type.title()}:** {meal_data['amount']} ({meal_data['calories']} cal)")
                    st.metric("Total Calories", f"{log['total_calories']} kcal")
                else:
                    st.info("No meal data recorded")
else:
    st.info("No logs found for this date range")