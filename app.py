import streamlit as st
import hashlib # we may need this in future :P
from database.db_manager import Database
from utils.accessibility import load_and_apply_preferences

st.set_page_config(
    page_title="Dementia Care Manager",
    layout="wide"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login page
if not st.session_state.logged_in:
    # Show login form
    st.markdown("<h1 style='text-align: center;'>Dementia Care Manager</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Please login to continue</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    # Get database connection
                    conn = st.session_state.db.get_connection()
                    
                    # Query user with role information
                    query = """
                        SELECT u.UserID, u.FirstName, u.LastName, u.RoleID, r.RoleName 
                        FROM User u
                        JOIN Role r ON u.RoleID = r.RoleID
                        WHERE u.Email = ? AND u.PasswordHash = ?
                    """
                    
                    cursor = conn.execute(query, (email, password))
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        # Set session state
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_name = user[1]
                        st.session_state.user_last_name = user[2]
                        st.session_state.role_id = user[3]
                        st.session_state.role = user[4]
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
        
        st.markdown("---")
        st.caption("Note: This is a prototype. Passwords should be hashed in production.")
    
    st.stop()

# After Login

# Load and apply user's accessibility preferences
load_and_apply_preferences(st.session_state.db, st.session_state.user_id)

# Display user info in sidebar
st.sidebar.title("Dementia Care Manager")
if 'user_name' in st.session_state:
    st.sidebar.write(f"**User:** {st.session_state.user_name}")
    st.sidebar.write(f"**Role:** {st.session_state.role.replace('_', ' ').title()}")
    
    # Add logout button
    if st.sidebar.button("Logout"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Define pages based on user role
if st.session_state.get('role') == 'carer':
    pages = {
        "Dashboard": [
            st.Page("pages/carer/dashboard.py", title="Dashboard", default=True),
        ],
        "Communication": [
            st.Page("pages/carer/messages.py", title="Messages"),
            st.Page("pages/carer/notifications.py", title="Notifications"),
        ],
        "Patients": [
            st.Page("pages/carer/patient_list.py", title="Patient List"),
            st.Page("pages/carer/add_patient.py", title="Add Patient"),
        ],
        "Daily Care": [
            st.Page("pages/carer/daily_logs.py", title="Daily Logs"),
            st.Page("pages/carer/medications.py", title="Medications"),
            st.Page("pages/carer/tasks.py", title="Tasks"),
        ],
        "Records": [
            st.Page("pages/carer/historical_logs.py", title="Historical Logs"),
            st.Page("pages/carer/memory_book.py", title="Memory Book"),
        ],
        "Settings": [st.Page("pages/carer/settings.py", title="Settings")]
    }
elif st.session_state.get('role') == 'family_member':
    # Family member pages
    pages = {
        "Dashboard": [
            st.Page("pages/family/dashboard.py", title="Dashboard", default=True),
        ]
    }
else:
    st.error("Unknown role. Please contact administrator.")
    st.stop()

pg = st.navigation(pages, position="sidebar")
pg.run()
