# pages/patient_details.py
import streamlit as st
from datetime import datetime


from db import get_connection, execute_db
from apply_preferences import apply_preferences
#from topbar import top_navigation


def get_patient_details(patient_id):
    conn = get_connection()
    patient = conn.execute("""
        SELECT FirstName, LastName, DementiaType, DementiaStage, ResidenceType, Address
        FROM Patient WHERE PatientID = ?;
    """, (patient_id,)).fetchone()
    conn.close()
    return patient


def get_medication_list(patient_id):
    conn = get_connection()
    meds = conn.execute("""
        SELECT Name, Dosage, Time, Active
        FROM Medication WHERE PatientID = ? AND Active = 1;
    """, (patient_id,)).fetchall()
    conn.close()
    return meds


def get_latest_logs(patient_id, limit=3):
    conn = get_connection()
    logs = conn.execute("""
        SELECT Content, ContentLvl, DateTime
        FROM Log_Item WHERE PatientID = ?
        ORDER BY DateTime DESC LIMIT ?;
    """, (patient_id, limit)).fetchall()
    conn.close()
    return logs


def submit_new_log(patient_id, author_id, content):
    execute_db("""
        INSERT INTO Log_Item (PatientID, AuthorID, Content, ContentLvl)
        VALUES (?, ?, ?, 'general');
    """, (patient_id, author_id, content))


def render_page():
    # Authentication and setup
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in first.")
        st.switch_page("login.py")
        return

    if "current_patient" not in st.session_state:
        st.warning("No patient selected.")
        st.switch_page("pages/dashboard.py")
        return

    apply_preferences()
    #accessibility_settings_panel()
    #top_navigation()

    user_role = st.session_state["role"]
    patient_id = st.session_state["current_patient"]

    patient = get_patient_details(patient_id)
    if not patient:
        st.error("Patient not found.")
        return

    full_name = f"{patient['FirstName']} {patient['LastName']}"
    st.title(f"{full_name} — Patient Details")

    st.markdown(f"[View Log History](history.py)")
    if st.button("View Log History", key="view_history_button", use_container_width=True):
        st.session_state["history_patient_id"] = st.session_state["current_patient"]
        st.switch_page("pages/history.py")# TODO Add this page ig

    if user_role == "carer":
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Patient Info")
            st.write(f"**Residence:** {patient['ResidenceType']}")
            st.write(f"**Address:** {patient['Address']}")
            st.write(f"**Dementia Type:** {patient['DementiaType']}")
            st.write(f"**Stage:** {patient['DementiaStage']}")

        with col2:
            st.subheader("Medication List")
            meds = get_medication_list(patient_id)
            if not meds:
                st.info("No active medications.")
            else:
                for m in meds:
                    st.write(f"- **{m['Name']}** {m['Dosage']} at {m['Time']}")

        with col3:
            st.subheader("Last Log Entry")
            logs = get_latest_logs(patient_id, 1)
            if logs:
                log = logs[0]
                st.write(log["Content"])
                st.caption(f"{log['DateTime']}")
            else:
                st.info("No logs yet.")

        st.divider()

        st.subheader("Add a New Log Entry")
        new_log = st.text_area("Write notes or updates about the patient here...")
        if st.button("Submit Log", key="submit_log", use_container_width=True):
            if new_log.strip():
                submit_new_log(patient_id, st.session_state["user_id"], new_log)
                st.success("New log submitted successfully.")
            else:
                st.warning("Please write something before submitting.")


    elif user_role == "family_member":
        col1, col2 = st.columns(2)

        # Patient Info
        with col1:
            st.subheader("Patient Info")
            st.write(f"**Residence:** {patient['ResidenceType']}")
            st.write(f"**Address:** {patient['Address']}")
            st.write(f"**Dementia Type:** {patient['DementiaType']}")
            st.write(f"**Stage:** {patient['DementiaStage']}")

        # Medications
        with col2:
            st.subheader("Medication List")
            meds = get_medication_list(patient_id)
            if not meds:
                st.info("No medications recorded.")
            else:
                for m in meds:
                    st.write(f"- {m['Name']} {m['Dosage']} ({m['Time']})")

        st.divider()

        # Recent Logs
        st.subheader("Recent Logs")
        logs = get_latest_logs(patient_id, 2)
        if not logs:
            st.info("No logs yet.")
        else:
            cols = st.columns(len(logs))
            for i, log in enumerate(logs):
                with cols[i]:
                    st.write(log["Content"])
                    st.caption(f"{log['DateTime']}")
        st.markdown("[View Full History](pages/history.py)")

    else:
        st.error("Invalid user role.")

if __name__ == "__main__":
    render_page()
