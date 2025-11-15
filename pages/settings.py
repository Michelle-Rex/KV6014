# Settings Page
import streamlit as st


from db import execute_db
from apply_preferences import apply_preferences, accessibility_settings_panel
#from topbar import top_navigation

def update_user_details(user_id, new_name, new_email):
    first, last = new_name.split(" ", 1)
    execute_db("UPDATE User SET FirstName=?, LastName=?, Email=? WHERE UserID=?",
               (first, last, new_email, user_id))

def render_page():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        st.switch_page("login.py")
        return

    apply_preferences()
    #top_navigation()

    st.title("Settings")

    st.subheader("Profile Information")
    new_name = st.text_input("Full Name", f"{st.session_state['user_name']}")
    new_email = st.text_input("Email", "")
    if st.button("Update Profile", key="update_profile", use_container_width=True):
        if new_name.strip() and new_email.strip():
            update_user_details(st.session_state["user_id"], new_name, new_email)
            st.success("Profile updated successfully.")
        else:
            st.warning("Please fill all fields.")

    st.divider()

    st.subheader("Accessibility Options")
    with st.container(border=True):
        theme_choice = st.radio(
            "Theme",
            ["light", "dark"],
            index=0 if st.session_state.get("theme", "light") == "light" else 1,
            horizontal=True
        )

        font_choice = st.select_slider(
            "Font Size",
            options=["small", "medium", "large", "x-large"],
            value=st.session_state.get("font_size", "medium")
        )

        high_contrast_choice = st.toggle(
            "High Contrast Mode",
            value=st.session_state.get("high_contrast", False)
        )

        if st.button("Apply Accessibility Preferences", use_container_width=True, type="primary"):
            st.session_state["theme"] = theme_choice
            st.session_state["font_size"] = font_choice
            st.session_state["high_contrast"] = high_contrast_choice
            apply_preferences()
            st.success("Accessibility preferences updated.")
            st.rerun()

    st.divider()

    st.subheader("Logout")
    if st.button("Logout", key="logout_button", use_container_width=True):
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.switch_page("login.py")

if __name__ == "__main__":
    render_page()
