import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'family_member':
    st.error("Access Denied: This page is only accessible to family members.")
    st.stop()

st.title("Communication Guide")
db = st.session_state.db



family_patients = db.get_family_patients(st.session_state.user_id)
if not family_patients:
    st.warning("No patients linked to your account")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in family_patients}
selected_display = st.selectbox("Select Patient", list(patient_options.values()))
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()
with st.expander("Add New Topic"):
    with st.form("add_topic_form"):
        topic = st.text_input("Topic", placeholder="e.g. Gardening, War memories")
        topic_type = st.radio("Type", ["positive", "avoid"], 
            format_func=lambda x: "Good to discuss" if x == "positive" else "Avoid discussing")
        notes = st.text_area("Notes", placeholder="Why?")
        submitted = st.form_submit_button("Add Topic")
        
        if submitted and topic:
            topic_data = {
                'patient_id': selected_patient_id,
                'topic': topic,
                'topic_type': topic_type,
                'notes': notes,
                'added_by': st.session_state.get('user_id', 1)
            }
            if db.add_communication_topic(topic_data):
                st.success(f"Added: {topic}")
                st.rerun()

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Good Topics")
    positive_topics = db.get_patient_topics(selected_patient_id, 'positive')
    
    if positive_topics:
        for topic in positive_topics:
            with st.container(border=True):
                st.write(f"**{topic['topic']}**")
                if topic['notes']:
                    st.caption(topic['notes'])
                if st.button("Delete", key=f"del_pos_{topic['topic_id']}"):
                    db.delete_communication_topic(topic['topic_id'])
                    st.rerun()
    else:
        st.info("No topics yet")




with col2:
    st.subheader("Avoid These")
    avoid_topics = db.get_patient_topics(selected_patient_id, 'avoid')
    
    if avoid_topics:
        for topic in avoid_topics:
            with st.container(border=True):
                st.write(f"**{topic['topic']}**")
                if topic['notes']:
                    st.caption(topic['notes'])
                if st.button("Delete", key=f"del_avoid_{topic['topic_id']}"):
                    db.delete_communication_topic(topic['topic_id'])
                    st.rerun()
    else:
        st.info("No topics yet")

st.divider()
st.caption(f"Total: {len(positive_topics)} good, {len(avoid_topics)} avoid")