import streamlit as st
from utils.notifications import show_notification_center

# Role check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("Access Denied: This page is only accessible to family members.")
    st.stop()

# Display the notification center (works for any user type)
show_notification_center()