import streamlit as st
from datetime import datetime


if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access this page.")
    st.stop()

if st.session_state.get('role') != 'carer':
    st.error("Access Denied: This page is only accessible to carers.")
    st.stop()


# Get database instance
db = st.session_state.get('db')
if not db:
    st.error("Database connection error.")
    st.stop()

st.title("Messages")

# Get all family members for this carer's patients
family_members = db.get_family_members_for_carer_patients(st.session_state.user_id)

if not family_members:
    st.info("""
    **No Family Members to Message**
    
    Your patients don't have any family members registered yet.
    Once family members are added to your patients, you'll be able to message them here.
    """)
    st.stop()

# Create sidebar for selecting conversations
st.sidebar.title("Conversations")

# Group by patient for better organization
patients_dict = {}
for fm in family_members:
    patient_id = fm['patient_id']
    if patient_id not in patients_dict:
        patients_dict[patient_id] = {
            'patient_name': fm['patient_name'],
            'family_members': []
        }
    patients_dict[patient_id]['family_members'].append(fm)

# Session state for selected conversation
if 'selected_family_member' not in st.session_state:
    st.session_state.selected_family_member = None
if 'selected_patient_id' not in st.session_state:
    st.session_state.selected_patient_id = None

# Display conversations grouped by patient
for patient_id, patient_data in patients_dict.items():
    st.sidebar.markdown(f"**{patient_data['patient_name']}**")
    
    for fm in patient_data['family_members']:
        # Create a button for each family member
        button_label = f"{fm['full_name']}"
        
        # Highlight if this is the selected conversation
        button_type = "primary" if (st.session_state.selected_family_member == fm['user_id'] and 
                                    st.session_state.selected_patient_id == patient_id) else "secondary"
        
        if st.sidebar.button(button_label, key=f"chat_{fm['user_id']}_{patient_id}", 
                            use_container_width=True, type=button_type):
            st.session_state.selected_family_member = fm['user_id']
            st.session_state.selected_patient_id = patient_id
            st.rerun()
    
    st.sidebar.markdown("---")

# Main chat area
if st.session_state.selected_family_member is None:
    # No conversation selected
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px;'>
        <h2>Select a conversation to start messaging</h2>
        <p>Choose a family member from the sidebar to begin chatting about their loved one.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Get selected family member details
    selected_fm = next((fm for fm in family_members 
                       if fm['user_id'] == st.session_state.selected_family_member 
                       and fm['patient_id'] == st.session_state.selected_patient_id), None)
    
    if not selected_fm:
        st.error("Selected conversation not found.")
        st.stop()
    
    # Chat header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### Chat with {selected_fm['full_name']}")
        st.caption(f"About: {selected_fm['patient_name']} | Access Level: {selected_fm['access_level'].title()}")
    
    with col2:
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Get messages for this conversation
    messages = db.get_messages_for_patient(
        selected_fm['patient_id'], 
        st.session_state.user_id
    )
    
    # Filter messages between these two users
    conversation_messages = [
        msg for msg in messages 
        if (msg['from_user_id'] == selected_fm['user_id'] or 
            msg['to_user_id'] == selected_fm['user_id'])
    ]
    
    # Display messages in WhatsApp style
    chat_container = st.container(height=400)
    
    with chat_container:
        if not conversation_messages:
            st.info(f"Start a conversation with {selected_fm['full_name']} about {selected_fm['patient_name']}")
        else:
            for msg in conversation_messages:
                # Format timestamp
                try:
                    msg_time = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                    time_str = msg_time.strftime('%I:%M %p')
                except:
                    time_str = msg['timestamp']
                
                if msg['is_sent_by_me']:
                    # Sent by carer (current user) - align right, blue background
                    st.markdown(f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div class='message-sent' style='display: inline-block; padding: 10px 15px; 
                                    border-radius: 15px; max-width: 70%; text-align: left;'>
                            <div style='font-size: 14px; '>{msg['content']}</div>
                            <div style='font-size: 11px; margin-top: 5px;'>{time_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Received from family member - align left, gray background
                    st.markdown(f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div class='message-received' style='display: inline-block; padding: 10px 15px; 
                                    border-radius: 15px; max-width: 70%; text-align: left;'>
                            <div style='font-weight: bold; font-size: 12px; color: #075E54; margin-bottom: 3px;'>
                                {msg['from_name']}
                            </div>
                            <div style='font-size: 14px;'>{msg['content']}</div>
                            <div style='font-size: 11px; margin-top: 5px;'>{time_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Message input area
    st.markdown("---")
    
    with st.form("message_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            message_content = st.text_area(
                "Type your message...",
                placeholder=f"Send a message to {selected_fm['full_name']} about {selected_fm['patient_name']}",
                height=100,
                label_visibility="collapsed"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            send_button = st.form_submit_button("Send", use_container_width=True, type="primary")
        
        if send_button:
            if message_content.strip():
                # Send the message
                message_id = db.send_message(
                    from_user_id=st.session_state.user_id,
                    to_user_id=selected_fm['user_id'],
                    patient_id=selected_fm['patient_id'],
                    content=message_content.strip()
                )
                
                if message_id:
                    # Create notification for the recipient
                    db.create_notification(
                        selected_fm['user_id'],
                        'message',
                        f"New message from {st.session_state.user_name} about {selected_fm['patient_name']}"
                    )
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.error("Failed to send message. Please try again.")
            else:
                st.warning("Please enter a message before sending.")

# Footer tips
st.markdown("---")
with st.expander("Messaging Tips For Carerrs"):
    st.markdown("""
    - **Quick Updates**: Share brief updates about the patient's day
    - **Questions**: Ask family about preferences or special requests
    - **Coordination**: Coordinate visit times or special occasions
    - **Reminders**: Remind famliy about appointments or events
    
    **Remember**: Family members have different access levels to patient information.
    Be mindful of what details you share based on their access level.
    """)
