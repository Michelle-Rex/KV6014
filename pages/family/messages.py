import streamlit as st
from datetime import datetime

# Role check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("⛔ Access Denied: This page is only accessible to family members.")
    st.stop()

# Get database instance
db = st.session_state.get('db')
if not db:
    st.error("Database connection error.")
    st.stop()

st.title("💬 Messages")

st.info("""**Family Messaging - Coming Soon!**

The messaging system for family members is currently under development.

**Planned Features:**
- View messages from your loved one's carers
- Reply to carer messages
- Send questions or updates
- Receive notifications when carers message you

For now, carers can send you messages and you'll receive notifications.
""")


st.markdown("---")
st.caption(f"Logged in as: {st.session_state.get('user_name', 'User')} (Family Member)")