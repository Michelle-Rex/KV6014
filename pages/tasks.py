import streamlit as st
from datetime import datetime, date
import uuid

st.title("Daily Task Checklist")

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

TASK_TEMPLATES = [
    "Morning medication",
    "Breakfast",
    "Personal hygiene",
    "Dressing",
    "Morning activities",
    "Mid-morning medication",
    "Lunch",
    "Afternoon activities",
    "Afternoon medication",
    "Dinner",
    "Evening medication",
    "Evening routine",
    "Bedtime preparation",
    "Night medication",
    "Room check",
    "Vital signs check",
    "Fluid intake monitoring",
    "Comfort check",
]

with st.expander("Add New Task", expanded=False):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        use_template = st.checkbox("Use template")
        
        if use_template:
            task_name = st.selectbox("Select task template", TASK_TEMPLATES)
        else:
            task_name = st.text_input("Task name", placeholder="Enter custom task")
    
    with col2:
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
    
    task_time = st.time_input("Scheduled time (optional)", value=None)
    task_notes = st.text_area("Notes", placeholder="Additional instructions")
    recurring = st.checkbox("Recurring daily task")
    
    if st.button("Add Task", use_container_width=True):
        if task_name:
            if selected_patient_id not in st.session_state.tasks:
                st.session_state.tasks[selected_patient_id] = []
            
            task = {
                'id': str(uuid.uuid4()),
                'task': task_name,
                'priority': priority,
                'time': task_time.strftime('%H:%M') if task_time else None,
                'notes': task_notes,
                'recurring': recurring,
                'completed': False,
                'created_date': date.today().isoformat(),
                'created_by': "Carer"
            }
            
            st.session_state.tasks[selected_patient_id].append(task)
            st.success(f"Task '{task_name}' added")
            st.rerun()
        else:
            st.error("Please enter a task name")

st.divider()

st.subheader(f"Tasks for {selected_patient_name}")

col1, col2 = st.columns(2)
with col1:
    show_completed = st.checkbox("Show completed tasks", value=False)
with col2:
    priority_filter = st.multiselect("Filter by priority", 
                                    ["Low", "Medium", "High", "Urgent"],
                                    default=["Low", "Medium", "High", "Urgent"])

if selected_patient_id in st.session_state.tasks and st.session_state.tasks[selected_patient_id]:
    tasks = st.session_state.tasks[selected_patient_id]
    
    filtered_tasks = [
        task for task in tasks
        if (show_completed or not task.get('completed', False))
        and task.get('priority') in priority_filter
    ]
    
    if filtered_tasks:
        priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_tasks = sorted(filtered_tasks, 
                            key=lambda x: (priority_order.get(x['priority'], 999), 
                                         x.get('time') or '99:99'))
        
        for priority in ["Urgent", "High", "Medium", "Low"]:
            priority_tasks = [t for t in sorted_tasks if t['priority'] == priority]
            
            if priority_tasks:
                st.write(f"### {priority} Priority")
                
                for task in priority_tasks:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            is_completed = task.get('completed', False)
                            task_label = f"~~{task['task']}~~" if is_completed else task['task']
                            
                            completed = st.checkbox(task_label, value=is_completed, key=f"task_{task['id']}")
                            
                            if completed != is_completed:
                                task['completed'] = completed
                                task['completed_at'] = datetime.now().isoformat() if completed else None
                                task['completed_by'] = "Carer" if completed else None
                                st.rerun()
                            
                            if task.get('time'):
                                st.caption(f"Scheduled: {task['time']}")
                            
                            if task.get('recurring'):
                                st.caption("Recurring daily")
                        
                        with col2:
                            if task.get('notes'):
                                st.caption(f"Notes: {task['notes']}")
                            
                            if task.get('completed'):
                                st.caption(f"Completed: {datetime.fromisoformat(task.get('completed_at')).strftime('%H:%M')}")
                        
                        with col3:
                            if st.button("Delete", key=f"del_{task['id']}", use_container_width=True):
                                st.session_state.tasks[selected_patient_id].remove(task)
                                st.success("Task deleted")
                                st.rerun()
                
                st.divider()
    else:
        st.info("No tasks match the current filters")
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get('completed', False))
    pending_tasks = total_tasks - completed_tasks
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", total_tasks)
    with col2:
        st.metric("Completed", completed_tasks)
    with col3:
        st.metric("Pending", pending_tasks)
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Reset Daily Tasks", use_container_width=True):
            for task in st.session_state.tasks[selected_patient_id]:
                if task.get('recurring'):
                    task['completed'] = False
                    task['completed_at'] = None
                    task['completed_by'] = None
            st.success("Recurring tasks reset")
            st.rerun()
    
    with col2:
        if st.button("Mark All Complete", use_container_width=True):
            for task in st.session_state.tasks[selected_patient_id]:
                if not task.get('completed'):
                    task['completed'] = True
                    task['completed_at'] = datetime.now().isoformat()
                    task['completed_by'] = "Carer"
            st.success("All tasks marked complete")
            st.rerun()

else:
    st.info("No tasks created yet for this patient")