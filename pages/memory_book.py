import streamlit as st
from datetime import datetime
import uuid

st.title("Memory Book - Photos & Media")

if not st.session_state.patients:
    st.warning("No patients registered. Please add a patient first.")
    if st.button("Add Patient"):
        st.switch_page("pages/add_patient.py")
    st.stop()

patient_names = {pid: p['name'] for pid, p in st.session_state.patients.items()}
selected_patient_name = st.selectbox("Select Patient", options=list(patient_names.values()))
selected_patient_id = [pid for pid, name in patient_names.items() if name == selected_patient_name][0]

st.divider()

if selected_patient_id not in st.session_state.memory_book:
    st.session_state.memory_book[selected_patient_id] = []

st.subheader("Upload New Media")

with st.form("upload_media_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        media_type = st.selectbox("Media Type", ["Photo", "Video", "Audio"])
        title = st.text_input("Title", placeholder="e.g., Family gathering 2023")
    
    with col2:
        category = st.selectbox("Category", ["Family", "Friends", "Events", "Music", "Other"])
        uploaded_file = st.file_uploader("Upload File", type=["jpg", "jpeg", "png", "mp4", "mp3", "wav"])
    
    description = st.text_area("Description", placeholder="Brief description of this memory")
    people_tagged = st.text_input("People in this", placeholder="Names of people")
    
    submitted = st.form_submit_button("Upload", use_container_width=True)

if submitted and uploaded_file and title:
    file_data = uploaded_file.read()
    
    memory_entry = {
        'id': str(uuid.uuid4()),
        'title': title,
        'media_type': media_type,
        'category': category,
        'description': description,
        'people': people_tagged,
        'file_name': uploaded_file.name,
        'file_type': uploaded_file.type,
        'file_data': file_data,
        'uploaded_on': datetime.now().isoformat(),
        'uploaded_by': "Carer"
    }
    
    st.session_state.memory_book[selected_patient_id].append(memory_entry)
    st.success(f"Media '{title}' uploaded successfully")
    st.rerun()

st.divider()

st.subheader(f"Memory Book for {selected_patient_name}")

category_filter = st.selectbox("Filter by Category", ["All", "Family", "Friends", "Events", "Music", "Other"])

if st.session_state.memory_book[selected_patient_id]:
    memories = st.session_state.memory_book[selected_patient_id]
    
    if category_filter != "All":
        filtered_memories = [m for m in memories if m['category'] == category_filter]
    else:
        filtered_memories = memories
    
    if filtered_memories:
        st.write(f"**Showing {len(filtered_memories)} items**")
        
        sorted_memories = sorted(filtered_memories, key=lambda x: x['uploaded_on'], reverse=True)
        
        cols = st.columns(2)
        
        for idx, memory in enumerate(sorted_memories):
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
                    
                    if memory.get('description'):
                        st.write(f"**Description:** {memory['description']}")
                    
                    if memory.get('people'):
                        st.write(f"**People:** {memory['people']}")
                    
                    st.caption(f"Uploaded on {datetime.fromisoformat(memory['uploaded_on']).strftime('%d %b %Y')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Full", key=f"view_{memory['id']}", use_container_width=True):
                            st.info("Viewing full media")
                    with col2:
                        if st.button("Delete", key=f"del_{memory['id']}", use_container_width=True):
                            st.session_state.memory_book[selected_patient_id].remove(memory)
                            st.success("Media deleted")
                            st.rerun()
    else:
        st.info(f"No items in the '{category_filter}' category")
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Items", len(memories))
    
    with col2:
        photos = sum(1 for m in memories if m['media_type'] == 'Photo')
        st.metric("Photos", photos)

else:
    st.info("No media uploaded yet")
    st.write("Upload photos, videos, or music to help patients with memory recall and provide comfort.")