import streamlit as st
from datetime import datetime

st.title("Task Checklist")
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




TASK_TEMPLATES = [
    "Morning medication",
    "Breakfast",
    "Personal hygiene",
    "Dressing",
    "Vital signs check",
    "Lunch",
    "Afternoon activities",
    "Dinner",
    "Evening medication",
    "Bedtime routine"
]

with st.expander("Add New Task"):

    use_template = st.checkbox("Use template")
    if use_template:
        task_name = st.selectbox("Select template", TASK_TEMPLATES)
    else:
        task_name = st.text_input("Task name")
    


    col1, col2 = st.columns(2)
    with col1:
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        scheduled_time = st.time_input("Scheduled time (optional)", value=None)
    with col2:
        recurring = st.checkbox("Recurring daily")
        task_notes = st.text_area("Notes")
    


    if st.button("Add Task"):
        if task_name:
            task_data = {
                'patient_id': selected_patient_id,
                'task_name': task_name,
                'priority': priority,
                'scheduled_time': scheduled_time.strftime('%H:%M') if scheduled_time else '',
                'notes': task_notes,
                'recurring': 1 if recurring else 0
            }
            task_id = db.add_task(task_data)
            if task_id:
                st.success(f"Task {task_name} added")
                st.rerun()
            else:
                st.error("Failed to add task")
        else:
            st.error("Please enter a task name")


st.divider()
st.subheader("Tasks")



col1, col2 = st.columns(2)
with col1:
    show_completed = st.checkbox("Show completed tasks")
with col2:
    priority_filter = st.multiselect("Filter by priority", ["Low", "Medium", "High", "Urgent"], default=["Low", "Medium", "High", "Urgent"])



tasks = db.get_patient_tasks(selected_patient_id)
filtered_tasks = [
    t for t in tasks
    if (show_completed or not t['completed']) and t['priority'] in priority_filter]

if filtered_tasks:
    for priority in ["Urgent", "High", "Medium", "Low"]:
        priority_tasks = [t for t in filtered_tasks if t['priority'] == priority]
        


        if priority_tasks:
            st.write(f"### {priority} Priority")
            for task in priority_tasks:



                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        is_completed = task['completed']
                        label = f"{task['task_name']}" if is_completed else task['task_name']
                        

                        completed = st.checkbox(label, value=is_completed, key=f"task_{task['task_id']}")
                        if completed != is_completed:
                            db.update_task_completion(task['task_id'], completed, completed_by=1)
                            st.rerun()
                        
                        if task['scheduled_time']:
                            st.caption(f"Scheduled: {task['scheduled_time']}")
                        if task['recurring']:
                            st.caption("Recurring daily")
                    
                    with col2:
                        if task['notes']:
                            st.caption(f"Notes: {task['notes']}")
                        
                        if task['completed'] and task['completed_at']:
                            completed_time = task['completed_at'][:16]
                            st.caption(f"Completed: {completed_time}")
                    
                    with col3:
                        if st.button("Delete", key=f"del_{task['task_id']}", use_container_width=True):
                            db.delete_task(task['task_id'])
                            st.success("Task deleted")
                            st.rerun()
            
            st.divider()

            
else:
    st.info("No tasks found")

total = len(tasks)
completed_count = sum(1 for t in tasks if t['completed'])
pending = total - completed_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total", total)
with col2:
    st.metric("Completed", completed_count)
with col3:
    st.metric("Pending", pending)