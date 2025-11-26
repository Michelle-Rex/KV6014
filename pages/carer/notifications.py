import streamlit as st
from utils.notifications import show_notification_center

# Check authentication

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'carer':
    st.error("Access Denied: This page is only accessible to carers.")
    st.stop()


# Display the notification center
show_notification_center() # I should move a lot of code to here but I am too tired TODO?
