import streamlit as st
from datetime import datetime, date, timedelta
import calendar as cal

st.title("Historical Logs")
db = st.session_state.db
patients = db.get_all_patients()

if not patients:
    st.warning("No patients registered")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in patients}
selected_display = st.selectbox("Select Patient", list(patient_options.values()))
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()


view_mode = st.radio("View Mode", ["Calendar View", "Date Range"], horizontal=True)
if view_mode == "Calendar View":
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Year", range(2020, 2030), index=date.today().year - 2020)
    with col2:
        selected_month = st.selectbox("Month", range(1, 13), format_func=lambda x: cal.month_name[x], index=date.today().month - 1)
    
    st.divider()




    
    all_logs = db.get_patient_logs(selected_patient_id)
    
    month_start = date(selected_year, selected_month, 1)
    if selected_month == 12:
        month_end = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    logs_by_date = {}
    for log in all_logs:
        log_date = log['date']
        if month_start.isoformat() <= log_date <= month_end.isoformat():
            if log_date not in logs_by_date:
                logs_by_date[log_date] = []
            logs_by_date[log_date].append(log)
    
    st.subheader(f"{cal.month_name[selected_month]} {selected_year}")
    


    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    cols = st.columns(7)
    for idx, day in enumerate(days):
        cols[idx].markdown(f"**{day}**")
    
    calendar_grid = cal.monthcalendar(selected_year, selected_month)
    for week in calendar_grid:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            if day == 0:
                cols[idx].write("")
            else:
                day_date = date(selected_year, selected_month, day)
                day_str = day_date.isoformat()
                
                if day_str in logs_by_date:
                    num_logs = len(logs_by_date[day_str])
                    if cols[idx].button(f"{day} ({num_logs})", key=f"day_{day}", use_container_width=True):
                        st.session_state.selected_date = day_str
                else:
                    cols[idx].button(f"{day}", key=f"day_{day}", disabled=True, use_container_width=True)
    
    st.divider()



    if 'selected_date' in st.session_state and st.session_state.selected_date in logs_by_date:
        selected_logs = logs_by_date[st.session_state.selected_date]
        selected_date_obj = datetime.fromisoformat(st.session_state.selected_date)
        
        st.subheader(f"Logs for {selected_date_obj.strftime('%A, %d %B %Y')}")
        
        for log in selected_logs:
            with st.expander(f"{log['time']} - Vitals & Status"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Vitals:**")
                    st.write(f"Temperature: {log['vitals']['temperature']}C")
                    st.write(f"Blood Pressure: {log['vitals']['blood_pressure']}")
                    st.write(f"Heart Rate: {log['vitals']['heart_rate']} bpm")
                    st.write(f"Oxygen: {log['vitals']['oxygen_saturation']}%")
                
                with col2:
                    st.write("**Status:**")
                    st.write(f"Mood: {log['activities']['mood']}")
                    st.write(f"Sleep: {log['activities']['sleep_quality']}")
                    st.write(f"Appetite: {log['activities']['appetite']}")
                    
                    st.write("**Nutrition:**")
                    st.write(f"Total Calories: {log['total_calories']} kcal")
                
                if log['general_notes']:
                    st.info(f"Notes: {log['general_notes']}")

else:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", value=date.today())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Last 7 Days"):
            st.session_state.start = date.today() - timedelta(days=7)
            st.session_state.end = date.today()
            st.rerun()
    with col2:
        if st.button("Last 30 Days"):
            st.session_state.start = date.today() - timedelta(days=30)
            st.session_state.end = date.today()
            st.rerun()
    with col3:
        if st.button("This Month"):
            st.session_state.start = date(date.today().year, date.today().month, 1)
            st.session_state.end = date.today()
            st.rerun()
    
    st.divider()
    logs = db.get_patient_logs(selected_patient_id, start_date.isoformat(), end_date.isoformat())
    if logs:
        st.success(f"Found {len(logs)} logs")
        
        for log in logs:
            log_date = datetime.fromisoformat(log['date']).strftime('%A, %d %B %Y')
            
            with st.expander(f"{log_date} at {log['time']}"):
                tab1, tab2, tab3 = st.tabs(["Vitals", "Status", "Notes"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Temperature", f"{log['vitals']['temperature']}C")
                        st.metric("Heart Rate", f"{log['vitals']['heart_rate']} bpm")
                    with col2:
                        st.metric("BP", log['vitals']['blood_pressure'])
                        st.metric("Oxygen", f"{log['vitals']['oxygen_saturation']}%")
                
                with tab2:
                    st.write(f"Mood: {log['activities']['mood']}")
                    st.write(f"Sleep: {log['activities']['sleep_quality']}")
                    st.write(f"Appetite: {log['activities']['appetite']}")
                    st.write(f"Activity: {log['activities']['activity_level']}")
                    st.write(f"Total Calories: {log['total_calories']} kcal")
                
                with tab3:
                    if log['general_notes']:
                        st.info(log['general_notes'])
                    if log['incidents']:
                        st.error(f"Incidents: {log['incidents']}")
    else:
        st.info("No logs found for this date range")