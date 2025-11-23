import streamlit as st
from datetime import datetime, timedelta

def show_notifications_banner(db, user_id: int):
    # Get unread notifications
    notifications = db.get_user_notifications(user_id, unread_only=True)
    
    if not notifications:
        return
    
    # Display each notification as a banner
    for notif in notifications[:5]:  # Show max 5 at a time
        notification_type = notif['type'] or 'info'
        
        # Choose appropriate Streamlit notification type
        if notification_type in ['medication', 'urgent', 'emergency']:
            st.error(f"**{notif['message']}**")
        elif notification_type in ['task', 'reminder']:
            st.warning(f"**{notif['message']}**")
        elif notification_type in ['update', 'log_update']:
            st.info(f"**{notif['message']}**")
        else:
            st.success(f"**{notif['message']}**")
        
        # Add dismiss button
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("Dismiss", key=f"dismiss_{notif['notification_id']}", type="secondary", use_container_width=True):
                db.mark_notification_read(notif['notification_id'])
                st.rerun()

def check_medication_reminders(db, user_id: int):
    # Get all patients for this carer
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get medications due in the next hour
    cursor.execute('''
        SELECT m.MedicationID, m.Name, m.Dosage, m.Time,
               p.FirstName, p.LastName, p.PatientID
        FROM Medication m
        JOIN Patient p ON m.PatientID = p.PatientID
        WHERE p.CarerID = ? AND m.Active = 1
    ''', (user_id,))
    
    medications = cursor.fetchall()
    conn.close()
    
    # Check current time and create notifications for upcoming medications
    # (This is a simplified version - in production, you'd use proper time comparison)
    for med in medications:
        # Create notification if not already created today
        message = f"Medication Due: {med['Name']} ({med['Dosage']}) for {med['FirstName']} {med['LastName']}"
        # In real implementation, check if notification already exists for today
        # db.create_notification(user_id, 'medication', message)

def create_log_update_notification(db, patient_id: int, log_content: str):
    """
    Create notifications for family members when a patient log is updated
    
    Args:
        db: Database instance
        patient_id: Patient's ID
        log_content: Summary of the log update
    """
    # Get all family members for this patient
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT fm.UserID, p.FirstName, p.LastName
        FROM Family_Member fm
        JOIN Patient p ON fm.PatientID = p.PatientID
        WHERE fm.PatientID = ?
    ''', (patient_id,))
    
    family_members = cursor.fetchall()
    conn.close()
    
    # Create notification for each family member
    for family in family_members:
        patient_name = f"{family['FirstName']} {family['LastName']}"
        message = f"New update for {patient_name}: {log_content[:100]}..."
        db.create_notification(family['UserID'], 'log_update', message)

def show_notification_center():
    db = st.session_state.get('db')
    user_id = st.session_state.get('user_id')
    
    if not db or not user_id:
        st.error("Session error. Please login again.")
        return
    
    st.title("Notifications")
    
    # Tabs for unread and all notifications
    tab1, tab2 = st.tabs(["Unread", "All Notifications"])
    
    with tab1:
        unread_notifs = db.get_user_notifications(user_id, unread_only=True)
        
        if not unread_notifs:
            st.info("No unread notifications!")
        else:
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Mark All Read", use_container_width=True):
                    db.mark_all_notifications_read(user_id)
                    st.success("All marked as read!")
                    st.rerun()
            
            for notif in unread_notifs:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Icon based on type
                        icon = "📝" if notif['type'] == 'log_update' else "⏰" if notif['type'] == 'medication' else "💬"
                        st.markdown(f"### {icon} {notif['message']}")
                        st.caption(f"{notif['created_at']}")
                    
                    with col3:
                        if st.button("Mark Read", key=f"read_{notif['notification_id']}", use_container_width=True):
                            db.mark_notification_read(notif['notification_id'])
                            st.rerun()
    
    with tab2:
        all_notifs = db.get_user_notifications(user_id, unread_only=False)
        
        if not all_notifs:
            st.info("No notifications yet.")
        else:
            for notif in all_notifs:
                with st.container(border=True):
                    icon = "📝" if notif['type'] == 'log_update' else "⏰" if notif['type'] == 'medication' else "💬"
                    
                    # Gray out if read
                    if notif['read']:
                        st.markdown(f"<div style='opacity: 0.5'>{icon} {notif['message']}<br><small>🕐 {notif['created_at']}</small></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"### {icon} {notif['message']}")
                        st.caption(f"{notif['created_at']}")
