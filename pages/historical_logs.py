import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd

st.title("Historical Logs")

if not st.session_state.patients:
    st.warning("No patients registered. Please add a patient first.")
    if st.button("Add Patient"):
        st.switch_page("pages/add_patient.py")
    st.stop()

patient_names = {pid: p['name'] for pid, p in st.session_state.patients.items()}
selected_patient_name = st.selectbox("Select Patient", options=list(patient_names.values()))
selected_patient_id = [pid for pid, name in patient_names.items() if name == selected_patient_name][0]

st.divider()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("From Date", value=date.today() - timedelta(days=30), max_value=date.today())

with col2:
    end_date = st.date_input("To Date", value=date.today(), max_value=date.today())

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Last 7 Days"):
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        st.rerun()

with col2:
    if st.button("Last 30 Days"):
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        st.rerun()

with col3:
    if st.button("Last 3 Months"):
        start_date = date.today() - timedelta(days=90)
        end_date = date.today()
        st.rerun()

with col4:
    if st.button("This Year"):
        start_date = date(date.today().year, 1, 1)
        end_date = date.today()
        st.rerun()

st.divider()

if selected_patient_id in st.session_state.daily_logs:
    all_logs = st.session_state.daily_logs[selected_patient_id]
    
    filtered_logs = [
        log for log in all_logs
        if start_date.isoformat() <= log['date'] <= end_date.isoformat()
    ]
    
    if filtered_logs:
        st.success(f"Found {len(filtered_logs)} logs between {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}")
        
        sorted_logs = sorted(filtered_logs, key=lambda x: x['date'], reverse=True)
        
        for log in sorted_logs:
            log_date = datetime.fromisoformat(log['date']).strftime('%A, %d %B %Y')
            
            with st.expander(f"{log_date} at {log.get('time', 'N/A')} - by {log.get('logged_by', 'Unknown')}"):
                tab1, tab2, tab3, tab4 = st.tabs(["Vitals", "Status", "Medications", "Notes"])
                
                with tab1:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Temperature", f"{log['vitals']['temperature']}°C")
                        st.metric("Heart Rate", f"{log['vitals']['heart_rate']} bpm")
                    
                    with col2:
                        st.metric("Blood Pressure", log['vitals']['blood_pressure'])
                        st.metric("Oxygen", f"{log['vitals']['oxygen_saturation']}%")
                    
                    with col3:
                        st.metric("Weight", f"{log['vitals']['weight']} kg")
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Mood:** {log['activities']['mood']}")
                        st.write(f"**Sleep:** {log['activities']['sleep_quality']}")
                        st.write(f"**Appetite:** {log['activities']['appetite']}")
                    
                    with col2:
                        st.write(f"**Activity:** {log['activities']['activity_level']}")
                        st.write(f"**Social:** {log['activities']['social_engagement']}")
                        st.write(f"**Communication:** {log['activities']['communication']}")
                    
                    if log.get('meals'):
                        st.write("**Nutrition:**")
                        st.write(f"Calories: {log['meals'].get('total_calories', 0)} kcal | Fluids: {log['meals'].get('total_fluids', 0)} ml")
                        st.write(f"Breakfast: {log['meals']['breakfast'].get('amount', 'N/A')} | Lunch: {log['meals']['lunch'].get('amount', 'N/A')} | Dinner: {log['meals']['dinner'].get('amount', 'N/A')}")
                
                with tab3:
                    if log.get('medications_given'):
                        st.write("**Medications Administered:**")
                        for med in log['medications_given']:
                            st.write(f"- **{med['medication']}** ({med['dosage']})")
                            st.write(f"  Scheduled: {med['scheduled_time']} | Given: {med['time_given']}")
                            st.write(f"  By: {med.get('given_by', 'Unknown')}")
                            st.divider()
                    else:
                        st.info("No medications recorded for this day")
                
                with tab4:
                    if log.get('general_notes'):
                        st.info(f"**Notes:** {log['general_notes']}")
                    
                    if log.get('incidents'):
                        st.error(f"**Incidents:** {log['incidents']}")
        
        st.divider()
        if st.button("Export to CSV"):
            export_data = []
            for log in sorted_logs:
                meds_given = ""
                if log.get('medications_given'):
                    meds_list = [f"{m['medication']} ({m['dosage']}) at {m['time_given']}" for m in log['medications_given']]
                    meds_given = "; ".join(meds_list)
                
                export_data.append({
                    'Date': log['date'],
                    'Time': log.get('time', 'N/A'),
                    'Temperature': log['vitals']['temperature'],
                    'Blood Pressure': log['vitals']['blood_pressure'],
                    'Heart Rate': log['vitals']['heart_rate'],
                    'Oxygen': log['vitals']['oxygen_saturation'],
                    'Mood': log['activities']['mood'],
                    'Sleep': log['activities']['sleep_quality'],
                    'Appetite': log['activities']['appetite'],
                    'Total Calories': log['meals'].get('total_calories', 0) if log.get('meals') else 0,
                    'Total Fluids': log['meals'].get('total_fluids', 0) if log.get('meals') else 0,
                    'Medications Given': meds_given,
                    'Notes': log.get('general_notes', ''),
                    'Incidents': log.get('incidents', ''),
                    'Logged By': log.get('logged_by', 'Unknown')
                })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_patient_name}_logs_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
    
    else:
        st.info(f"No logs found between {start_date.strftime('%d %b %Y')} and {end_date.strftime('%d %b %Y')}")

else:
    st.info("No logs recorded yet for this patient")
    if st.button("Add First Log"):
        st.session_state.current_patient = selected_patient_id
        st.switch_page("pages/daily_logs.py")