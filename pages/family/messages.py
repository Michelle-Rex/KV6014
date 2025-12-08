import streamlit as st
from datetime import datetime


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

st.title("Messages")

# Get all carers for this family member's patients
carers = db.get_carers_for_family_member_patients(st.session_state.user_id)

if not carers:
    st.info("""
    **No Carers to Message**
    
    You don't have any carers registered for your loved ones yet.
    Once your loved ones are assigned carers, you'll be able to message them here.
    """)
    st.stop()

# Create sidebar for selecting conversations
st.sidebar.title("Conversations")

# Group by patient for better organization
patients_dict = {}
for carer in carers:
    patient_id = carer['patient_id']
    if patient_id not in patients_dict:
        patients_dict[patient_id] = {
            'patient_name': carer['patient_name'],
            'carers': []
        }
    patients_dict[patient_id]['carers'].append(carer)

# Session state for selected conversation
if 'selected_carer' not in st.session_state:
    st.session_state.selected_carer = None
if 'selected_patient_id' not in st.session_state:
    st.session_state.selected_patient_id = None

# Display conversations grouped by patient
for patient_id, patient_data in patients_dict.items():
    st.sidebar.markdown(f"**{patient_data['patient_name']}**")
    
    for carer in patient_data['carers']:
        # Create a button for each carer
        button_label = f"{carer['full_name']}"
        
        # Highlight if this is the selected conversation
        button_type = "primary" if (st.session_state.selected_carer == carer['user_id'] and 
                                    st.session_state.selected_patient_id == patient_id) else "secondary"
        
        if st.sidebar.button(button_label, key=f"chat_{carer['user_id']}_{patient_id}", 
                            use_container_width=True, type=button_type):
            st.session_state.selected_carer = carer['user_id']
            st.session_state.selected_patient_id = patient_id
            st.rerun()
    
    st.sidebar.markdown("---")

# Main chat area
if st.session_state.selected_carer is None:
    # No conversation selected
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px;'>
        <h2>Select a conversation to start messaging</h2>
        <p>Choose a carer from the sidebar to begin chatting about your loved one.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Get selected carer details
    selected_carer = next((c for c in carers 
                       if c['user_id'] == st.session_state.selected_carer 
                       and c['patient_id'] == st.session_state.selected_patient_id), None)
    
    if not selected_carer:
        st.error("Selected conversation not found.")
        st.stop()
    
    # Chat header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### Chat with {selected_carer['full_name']}")
        st.caption(f"About: {selected_carer['patient_name']} | Your Access Level: {selected_carer['access_level'].title()}")
    
    with col2:
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Get messages for this conversation
    messages = db.get_messages_for_patient(
        selected_carer['patient_id'], 
        st.session_state.user_id
    )
    
    # Filter messages between these two users
    conversation_messages = [
        msg for msg in messages 
        if (msg['from_user_id'] == selected_carer['user_id'] or 
            msg['to_user_id'] == selected_carer['user_id'])
    ]
    
    # Display messages in WhatsApp style
    chat_container = st.container(height=400)
    
    with chat_container:
        if not conversation_messages:
            st.info(f"Start a conversation with {selected_carer['full_name']} about {selected_carer['patient_name']}")
        else:
            for msg in conversation_messages:
                # Format timestamp it broke a lot earlier on so doing try-catch
                try:
                    msg_time = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                    time_str = msg_time.strftime('%I:%M %p')
                except:
                    time_str = msg['timestamp']
                
                if msg['is_sent_by_me']:
                    # Sent by family member (current user) - align right, green background
                    st.markdown(f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div class='message-sent' style='display: inline-block; padding: 10px 15px; 
                                    border-radius: 15px; max-width: 70%; text-align: left;'>
                            <div style='font-size: 14px;'>{msg['content']}</div>
                            <div style='font-size: 11px; margin-top: 5px;'>{time_str}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Received from carer - align left, gray background
                    st.markdown(f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div class='message-received' style='display: inline-block; padding: 10px 15px; 
                                    border-radius: 15px; max-width: 70%; text-align: left;'>
                            <div style='font-weight: bold; font-size: 12px; margin-bottom: 3px;'>
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
                placeholder=f"Send a message to {selected_carer['full_name']} about {selected_carer['patient_name']}",
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
                    to_user_id=selected_carer['user_id'],
                    patient_id=selected_carer['patient_id'],
                    content=message_content.strip()
                )
                
                if message_id:
                    # Create notification for the recipient
                    db.create_notification(
                        selected_carer['user_id'],
                        'message',
                        f"New message from {st.session_state.user_name} about {selected_carer['patient_name']}"
                    )
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.error("Failed to send message. Please try again.")
            else:
                st.warning("Please enter a message before sending.")

# Footer tips
st.markdown("---")
with st.expander("Messaging Tips For Family Members"):
    st.markdown("""
    - **Stay Updated**: Ask carers about your loved one's daily activities
    - **Share Information**: Let carers know about preferences or special requests
    - **Ask Questions**: Don't hesitate to ask about care, medications, or activities
    - **Coordinate Visits**: Arrange visit times or special occasions
    - **Express Concerns**: Share any worries or observations you have
    
    **Remember**: Your carer is here to help and keep you informed about your loved one's wellbeing.
    Feel free to reach out anytime with questions or concerns.
    """)
