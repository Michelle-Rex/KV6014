import streamlit as st
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import uuid
"""
Task Checklist Module
Manages daily task lists and completion tracking for patient care. This feature allows carers to create, assign, and track completion of
daily care tasks for each patient.
"""

class TaskTemplates:
    """
    Provides predefined task templates for common care activities.
    """
    
    TEMPLATES = [
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
    
    @staticmethod
    def get_templates() -> List[str]:
        """
        Get list of available task templates.
        
        Returns:
            List of template task names
        """
        return TaskTemplates.TEMPLATES


class TaskFormRenderer:
    """
    Renders task creation form with template support.
    """
    
    @staticmethod
    def render() -> Optional[Dict[str, Any]]:
        """
        Render task creation form.
        
        Returns:
            Task dictionary or None if not submitted
        """
        with st.expander("Add New Task", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                use_template = st.checkbox("Use template")
                
                if use_template:
                    task_name = st.selectbox(
                        "Select task template",
                        TaskTemplates.get_templates()
                    )
                else:
                    task_name = st.text_input(
                        "Task name",
                        placeholder="Enter custom task"
                    )
            
            with col2:
                priority = st.selectbox(
                    "Priority",
                    ["Low", "Medium", "High", "Urgent"]
                )
            
            task_time = st.time_input("Scheduled time (optional)", value=None)
            task_notes = st.text_area("Notes", placeholder="Additional instructions")
            recurring = st.checkbox("Recurring daily task")
            
            if st.button("Add Task", use_container_width=True):
                if task_name:
                    return TaskFormRenderer._create_task(
                        task_name,
                        priority,
                        task_time,
                        task_notes,
                        recurring
                    )
                else:
                    st.error("Please enter a task name")
                    return None
        
        return None
    
    @staticmethod
    def _create_task(
        task_name: str,
        priority: str,
        task_time: Optional[Any],
        task_notes: str,
        recurring: bool
    ) -> Dict[str, Any]:
        """
        Create a task dictionary from form data.
        
        Args:
            task_name: Name of the task
            priority: Priority level
            task_time: Scheduled time
            task_notes: Additional notes
            recurring: Whether task recurs daily
            
        Returns:
            Task dictionary
        """
        return {
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


class TaskFilter:
    """
    Handles task filtering options.
    """
    
    @staticmethod
    def render_filter_controls() -> tuple[bool, List[str]]:
        """
        Render filter control options.
        
        Returns:
            Tuple of (show_completed, priority_filter)
        """
        col1, col2 = st.columns(2)
        
        with col1:
            show_completed = st.checkbox("Show completed tasks", value=False)
        
        with col2:
            priority_filter = st.multiselect(
                "Filter by priority",
                ["Low", "Medium", "High", "Urgent"],
                default=["Low", "Medium", "High", "Urgent"]
            )
        
        return show_completed, priority_filter
    
    @staticmethod
    def apply_filters(
        tasks: List[Dict],
        show_completed: bool,
        priority_filter: List[str]
    ) -> List[Dict]:
        """
        Apply filters to task list.
        
        Args:
            tasks: List of all tasks
            show_completed: Whether to show completed tasks
            priority_filter: List of priorities to include
            
        Returns:
            Filtered list of tasks
        """
        return [
            task for task in tasks
            if (show_completed or not task.get('completed', False))
            and task.get('priority') in priority_filter
        ]


class TaskSorter:
    """
    Handles sorting of tasks by priority and time.
    """
    
    PRIORITY_ORDER = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
    
    @staticmethod
    def sort_tasks(tasks: List[Dict]) -> List[Dict]:
        """
        Sort tasks by priority and scheduled time.
        
        Args:
            tasks: List of tasks to sort
            
        Returns:
            Sorted list of tasks
        """
        return sorted(
            tasks,
            key=lambda x: (
                TaskSorter.PRIORITY_ORDER.get(x['priority'], 999),
                x.get('time') or '99:99'
            )
        )


class TaskRenderer:
    """
    this displays the task list with completion checkboxes and slider buttons.
    """
    
    @staticmethod
    def render_tasks(patient_id: str, tasks: List[Dict]) -> None:
        """
        Displays the task list grouped bypriority.
        
        """
        if not tasks:
            st.info("No tasks match the current filters")
            return
        
        sorted_tasks = TaskSorter.sort_tasks(tasks)
        
        for priority in ["Urgent", "High", "Medium", "Low"]:
            priority_tasks = [
                t for t in sorted_tasks if t['priority'] == priority
            ]
            
            if priority_tasks:
                st.write(f"### {priority} Priority")
                
                for task in priority_tasks:
                    TaskRenderer._render_task_card(patient_id, task)
                
                st.divider()
    
    @staticmethod
    def _render_task_card(patient_id: str, task: Dict[str, Any]) -> None:
        """
        Render individual task card.
        
        Args:
            patient_id: ID of the patient
            task: Task dictionary
        """
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                is_completed = task.get('completed', False)
                task_label = (
                    f"~~{task['task']}~~" if is_completed
                    else task['task']
                )
                
                completed = st.checkbox(
                    task_label,
                    value=is_completed,
                    key=f"task_{task['id']}"
                )
                
                if completed != is_completed:
                    TaskRenderer._toggle_task_completion(task, completed)
                    st.rerun()
                
                if task.get('time'):
                    st.caption(f"Scheduled: {task['time']}")
                
                if task.get('recurring'):
                    st.caption("Recurring daily")
            
            with col2:
                if task.get('notes'):
                    st.caption(f"Notes: {task['notes']}")
                
                if task.get('completed'):
                    completed_time = datetime.fromisoformat(
                        task.get('completed_at')
                    ).strftime('%H:%M')
                    st.caption(f"Completed: {completed_time}")
            
            with col3:
                if st.button(
                    "Delete",
                    key=f"del_{task['id']}",
                    use_container_width=True
                ):
                    st.session_state.tasks[patient_id].remove(task)
                    st.success("Task deleted")
                    st.rerun()
    
    @staticmethod
    def _toggle_task_completion(task: Dict[str, Any], completed: bool) -> None:
        """
        Toggle task completion status.
        
        Args:
            task: Task dictionary
            completed: New completion status
        """
        task['completed'] = completed
        task['completed_at'] = (
            datetime.now().isoformat() if completed else None
        )
        task['completed_by'] = "Carer" if completed else None


class TaskStatistics:
    """
    Calculates and displays task statistics.
    """
    
    @staticmethod
    def render(tasks: List[Dict]) -> None:
        """
        Display task statistics summary.
        
        Args:
            tasks: List of all tasks
        """
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


class TaskBulkActions:
    """
    Handles bulk operations on tasks.
    """
    
    @staticmethod
    def render(patient_id: str) -> None:
        """
        Render bulk action buttons.
        
        Args:
            patient_id: ID of the patient
        """
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Daily Tasks", use_container_width=True):
                TaskBulkActions._reset_recurring_tasks(patient_id)
                st.success("Recurring tasks reset")
                st.rerun()
        
        with col2:
            if st.button("Mark All Complete", use_container_width=True):
                TaskBulkActions._complete_all_tasks(patient_id)
                st.success("All tasks marked complete")
                st.rerun()
    
    @staticmethod
    def _reset_recurring_tasks(patient_id: str) -> None:
        """
        Reset all recurring tasks to incomplete.
        
        Args:
            patient_id: ID of the patient
        """
        for task in st.session_state.tasks[patient_id]:
            if task.get('recurring'):
                task['completed'] = False
                task['completed_at'] = None
                task['completed_by'] = None
    
    @staticmethod
    def _complete_all_tasks(patient_id: str) -> None:
        """
        Mark all tasks as complete.
        
        Args:
            patient_id: ID of the patient
        """
        for task in st.session_state.tasks[patient_id]:
            if not task.get('completed'):
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                task['completed_by'] = "Carer"






def render_page() -> None:
    """Main function to Display the Task to do list page."""
    st.title("Daily Task Checklist")
    
    from pages.daily_logs import PatientSelector
    patient_info = PatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    new_task = TaskFormRenderer.render()
    
    if new_task:
        if patient_id not in st.session_state.tasks:
            st.session_state.tasks[patient_id] = []
        
        st.session_state.tasks[patient_id].append(new_task)
        st.success(f"Task '{new_task['task']}' added")
        st.rerun()
    
    st.divider()
    st.subheader(f"Tasks for {patient_name}")
    
    show_completed, priority_filter = TaskFilter.render_filter_controls()
    



    if patient_id in st.session_state.tasks and st.session_state.tasks[patient_id]:
        tasks = st.session_state.tasks[patient_id]
        
        filtered_tasks = TaskFilter.apply_filters(
            tasks,
            show_completed,
            priority_filter
        )
        
        TaskRenderer.render_tasks(patient_id, filtered_tasks)
        
        TaskStatistics.render(tasks)
        TaskBulkActions.render(patient_id)
    else:
        st.info("No tasks created yet for this patient")





if __name__ == "__main__":
    render_page()