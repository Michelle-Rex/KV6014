# This is the log in page and honestly should be our main page, it sets session data

# NOTE : This is a prototype log in page, so barebones for now

import streamlit as st

from db import get_connection

st.title("Login to MyCarer or whatever it is called")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# UI
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    conn = get_connection()
    # Do some sort of hashing function here ???
    user = conn.execute("SELECT UserID, FirstName, RoleID, (SELECT RoleName FROM Role WHERE RoleID=User.RoleID) FROM User WHERE Email=? AND PasswordHash=?", (email, password)).fetchone()

    if user:
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = user[0]
        st.session_state["user_name"] = user[1]
        st.session_state["role"] = user[3]

        st.success(f"Welcome back, {user[1]} ({user[3]})!")
        st.switch_page("pages/dashboard.py")
    else:
        st.error("Invalid email or password.")

