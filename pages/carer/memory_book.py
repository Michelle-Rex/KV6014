import streamlit as st

st.title("Memory Book")
db = st.session_state.db
patients = db.get_all_patients()

if not patients:
    st.warning("No patients are. registered")
    st.stop()

patient_options = {p['patient_id']: f"{p['patient_number']} - {p['first_name']} {p['last_name']}" for p in patients}
selected_display = st.selectbox("Select Patient", list(patient_options.values()))
selected_patient_id = [pid for pid, display in patient_options.items() if display == selected_display][0]

st.divider()

st.subheader("Upload New Media")




with st.form("upload_form"):
    col1, col2 = st.columns(2)
    with col1:
        media_type = st.selectbox("Media Type", ["Photo", "Video", "Audio"])
        title = st.text_input("Title")
    with col2:
        category = st.selectbox("Category", ["Family", "Friends", "Events", "Music", "Other"])
        uploaded_file = st.file_uploader("Upload File", type=["jpg", "jpeg", "png", "mp4", "mp3", "wav"])
    


    description = st.text_area("Description")
    people = st.text_input("People in this")
    


    submitted = st.form_submit_button("Upload")
    if submitted and uploaded_file and title:
        file_data = uploaded_file.read()
        memory_data = {
            'patient_id': selected_patient_id,
            'uploaded_by': 1,
            'title': title,
            'media_type': media_type,
            'category': category,
            'description': description,
            'people_tagged': people,
            'file_name': uploaded_file.name,
            'file_type': uploaded_file.type,
            'file_data': file_data
        }
        memory_id = db.add_memory(memory_data)
        
        if memory_id:
            st.success(f"Media {title} uploaded")
            st.rerun()
        else:
            st.error("Failed to upload")
    elif submitted:
        st.error("Please provide title and file")

st.divider()

st.subheader("Memory Book")

category_filter = st.selectbox("Filter by Category", ["All", "Family", "Friends", "Events", "Music", "Other"])

memories = db.get_patient_memories(selected_patient_id, category_filter)

if memories:
    st.write(f"Showing {len(memories)} items")
    
    cols = st.columns(2)
    
    for idx, memory in enumerate(memories):
        with cols[idx % 2]:
            with st.container(border=True):
                st.write(f"**{memory['title']}**")
                st.write(f"Type: {memory['media_type']} | Category: {memory['category']}")
                
                if memory['media_type'] == 'Photo':
                    st.image(memory['file_data'], use_container_width=True)


                elif memory['media_type'] == 'Video':
                    st.video(memory['file_data'])

                elif memory['media_type'] == 'Audio':
                    st.audio(memory['file_data'])
                if memory['description']:
                    st.write(memory['description'])

                if memory['people_tagged']:
                    st.caption(f"People: {memory['people_tagged']}")


                if st.button("Delete", key=f"del_{memory['memory_id']}", use_container_width=True):
                    db.delete_memory(memory['memory_id'])
                    st.success("Memory deleted")
                    st.rerun()
else:
    st.info("No memories uploaded")