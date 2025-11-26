import streamlit as st
from utils.accessibility import apply_accessibility_css

# Role check
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("Access Denied: This page is only accessible to family members.")
    st.stop()

# Get database instance
db = st.session_state.get('db')
if not db:
    st.error("Database connection error.")
    st.stop()

# Load user preferences from database
user_prefs = db.get_user_preferences(st.session_state.user_id)

# Apply current preferences
apply_accessibility_css(user_prefs['theme'], user_prefs['font_size'], user_prefs['high_contrast'])

# Page content
st.title("Settings")

# Profile Information Section
st.header("Profile Information")

with st.form("profile_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input(
            "First Name", 
            value=st.session_state.get('user_name', ''),
            help="Your first name"
        )
    
    with col2:
        last_name = st.text_input(
            "Last Name",
            value=st.session_state.get('user_last_name', ''),
            help="Your last name"
        )
    
    # Get current email from database
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Email FROM User WHERE UserID = ?", (st.session_state.user_id,))
    current_email = cursor.fetchone()[0]
    conn.close()
    
    email = st.text_input(
        "Email Address",
        value=current_email,
        help="Your email address for login"
    )
    
    submit_profile = st.form_submit_button("Update Profile", use_container_width=True)
    
    if submit_profile:
        if not first_name.strip() or not last_name.strip() or not email.strip():
            st.error("All fields are required.")
        else:
            success = db.update_user_profile(
                st.session_state.user_id,
                first_name.strip(),
                last_name.strip(),
                email.strip()
            )
            
            if success:
                st.session_state.user_name = first_name.strip()
                st.session_state.user_last_name = last_name.strip()
                st.success("Profile updated successfully!")
            else:
                st.error("Failed to update profile. Please try again.")

st.divider()

# Accessibility Settings Section
st.header("Accessibility Settings")

st.markdown("""
Customize your experience with these accessibility options. 
Changes will be saved and applied across all your sessions.
""")

with st.form("accessibility_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        theme_choice = st.radio(
            "Theme",
            options=["light", "dark"],
            index=0 if user_prefs['theme'] == "light" else 1,
            horizontal=True,
            help="Choose your preferred color theme"
        )
        
        font_choice = st.select_slider(
            "Font Size",
            options=["small", "medium", "large", "x-large"],
            value=user_prefs['font_size'],
            help="Adjust text size for better readability"
        )
    
    with col2:
        high_contrast_choice = st.toggle(
            "🔆 High Contrast Mode",
            value=user_prefs['high_contrast'],
            help="Enable high contrast for better visibility"
        )
        
        # Preview box
        st.info(f"""
        **Current Settings:**
        - Theme: {theme_choice.title()}
        - Font: {font_choice.title()}
        - High Contrast: {'Enabled' if high_contrast_choice else 'Disabled'}
        """)
    
    submit_accessibility = st.form_submit_button(
        "Save Accessibility Settings", 
        use_container_width=True,
        type="primary"
    )
    
    if submit_accessibility:
        success = db.save_user_preferences(
            st.session_state.user_id,
            theme_choice,
            font_choice,
            high_contrast_choice
        )
        
        if success:
            st.success("Accessibility settings saved! Refreshing page...")
            st.rerun()
        else:
            st.error("Failed to save settings. Please try again.")

st.divider()

# Notification Preferences (placeholder for future)
st.header("Notification Preferences")
st.info("Notification preferences coming soon! You can manage which types of updates you receive.")

st.divider()

# Account Actions Section
st.header("Account Actions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Change Password")
    st.info("🚧 Password change feature coming soon!")

with col2:
    st.markdown("### Logout")
    st.markdown("End your current session and return to the login page.")
    
    if st.button("Logout", use_container_width=True, type="secondary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()

st.divider()

# Footer info
st.caption(f"""
**User:** {st.session_state.get('user_name', '')} {st.session_state.get('user_last_name', '')}  
**Role:** Family Member  
**User ID:** {st.session_state.get('user_id', 'N/A')}
""")