import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
"""
Family Memory Book Module
Editable memory book for family members to upload and manage photos, videos, and audio.

Family members can add, view, and delete media to support their loved one's memory.
"""

class MediaCategories:
    """
    Defines available media categories for organization.
    """
    
    CATEGORIES = ["Family", "Friends", "Events", "Music", "Other"]
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get list of available categories."""
        return MediaCategories.CATEGORIES


class FamilyPatientSelector:
    """
    Allows family members to select which patient's memory book to manage.
    """
    
    @staticmethod
    def render_selector() -> Optional[tuple[str, str]]:
        """
        Render patient selection dropdown for family members.
        
        """
        if not st.session_state.patients:
            st.warning("No patients registered in the system.")
            return None
        
        default_index = 0
        if st.session_state.current_patient:
            try:
                default_index = list(st.session_state.patients.keys()).index(
                    st.session_state.current_patient
                )
            except ValueError:
                default_index = 0
        
        patient_options = {
            pid: f"{p.get('patient_id_number', 'N/A')} - {p['name']}"
            for pid, p in st.session_state.patients.items()
        }
        
        selected_display = st.selectbox(
            "Select Your Loved One",
            options=list(patient_options.values()),
            index=default_index
        )
        
        selected_patient_id = [
            pid for pid, display in patient_options.items()
            if display == selected_display
        ][0]
        
        st.session_state.current_patient = selected_patient_id
        patient_name = st.session_state.patients[selected_patient_id]['name']
        
        return selected_patient_id, patient_name


class MediaUploadForm:
    """
    Handles media upload form for family members.
    """
    
    @staticmethod
    def render() -> Optional[Dict[str, Any]]:
        """
        Render media upload form.
        
        Returns:
            Media data dictionary or None if not submitted
        """
        st.subheader("Upload New Memory")
        st.info("💝 Share photos, videos, or music to help your loved one remember happy times")
        
        with st.form("family_upload_media_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                media_type = st.selectbox(
                    "Media Type",
                    ["Photo", "Video", "Audio"]
                )
                title = st.text_input(
                    "Title*",
                    placeholder="e.g., Christmas 2023, Dad's Birthday"
                )
            
            with col2:
                category = st.selectbox(
                    "Category",
                    MediaCategories.get_categories()
                )
                uploaded_file = st.file_uploader(
                    "Upload File*",
                    type=["jpg", "jpeg", "png", "mp4", "mp3", "wav"]
                )
            
            description = st.text_area(
                "Description",
                placeholder="Describe this memory and why it's special"
            )
            
            people_tagged = st.text_input(
                "People in this memory",
                placeholder="Names of people in the photo/video"
            )
            
            submitted = st.form_submit_button("Upload Memory", use_container_width=True)
            
            if submitted and uploaded_file and title:
                return MediaUploadForm._create_media_entry(
                    media_type,
                    title,
                    category,
                    uploaded_file,
                    description,
                    people_tagged
                )
            elif submitted:
                st.error("Please provide both a title and file")
            
            return None
    
    @staticmethod
    def _create_media_entry(
        media_type: str,
        title: str,
        category: str,
        uploaded_file,
        description: str,
        people_tagged: str
    ) -> Dict[str, Any]:
        """Create media entry from form data."""
        file_data = uploaded_file.read()
        
        return {
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
            'uploaded_by': "Family Member"
        }


class MediaFilter:
    """
    Handles filtering of media by category.
    """
    
    @staticmethod
    def render_filter() -> str:
        """Render category filter."""
        return st.selectbox(
            "Filter by Category",
            ["All"] + MediaCategories.get_categories()
        )
    
    @staticmethod
    def apply_filter(media_list: List[Dict], category_filter: str) -> List[Dict]:
        """Apply category filter to media list."""
        if category_filter == "All":
            return media_list
        
        return [m for m in media_list if m['category'] == category_filter]


class MediaRenderer:
    """
    Renders media items in grid layout.
    """
    
    @staticmethod
    def render_media_grid(patient_id: str, media_list: List[Dict]) -> None:
        """
        Render media items in grid layout.
        
        Args:
            patient_id: ID of the patient
            media_list: List of media items
        """
        if not media_list:
            st.info("No memories uploaded yet. Be the first to add one!")
            return
        
        st.write(f"**Showing {len(media_list)} memory/memories**")
        
        sorted_media = sorted(
            media_list,
            key=lambda x: x['uploaded_on'],
            reverse=True
        )
        
        cols = st.columns(2)
        
        for idx, memory in enumerate(sorted_media):
            with cols[idx % 2]:
                MediaRenderer._render_media_card(patient_id, memory)
    
    @staticmethod
    def _render_media_card(patient_id: str, memory: Dict[str, Any]) -> None:
        """individual media card."""
        with st.container(border=True):
            st.write(f"### {memory['title']}")
            st.write(f"**Type:** {memory['media_type']} | **Category:** {memory['category']}")
            
            MediaRenderer._render_media_preview(memory)
            
            if memory.get('description'):
                st.write(f"**Description:** {memory['description']}")
            
            if memory.get('people'):
                st.write(f"**People:** {memory['people']}")
            
            uploaded_date = datetime.fromisoformat(
                memory['uploaded_on']
            ).strftime('%d %b %Y')
            
            uploaded_by = memory.get('uploaded_by', 'Unknown')
            st.caption(f"Uploaded by {uploaded_by} on {uploaded_date}")
            
            if st.button(
                "Delete Memory",
                key=f"del_{memory['id']}",
                use_container_width=True
            ):
                if st.session_state.get(f"confirm_delete_{memory['id']}", False):
                    st.session_state.memory_book[patient_id].remove(memory)
                    st.success("Memory deleted")
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{memory['id']}"] = True
                    st.warning("Click again to confirm deletion")
    
    @staticmethod
    def _render_media_preview(memory: Dict[str, Any]) -> None:
        """Render media preview."""
        if memory['media_type'] == 'Photo':
            st.image(memory['file_data'], use_container_width=True)
        elif memory['media_type'] == 'Video':
            st.video(memory['file_data'])
        elif memory['media_type'] == 'Audio':
            st.audio(memory['file_data'])


class MediaStatistics:
    """
    Displays the media statistics.
    """
    
    @staticmethod
    def render(media_list: List[Dict]) -> None:
        """Displays the   media statistics."""
        if not media_list:
            return
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Memories", len(media_list))
        
        with col2:
            photos = sum(1 for m in media_list if m['media_type'] == 'Photo')
            st.metric("Photos", photos)
        
        with col3:
            videos = sum(1 for m in media_list if m['media_type'] == 'Video')
            st.metric("Videos", videos)


class MemoryBookManager:
    """
    Main memory book management controller.
    """
    
    @staticmethod
    def initialize_memory_book(patient_id: str) -> None:
        """Initialize memory book for patient."""
        if patient_id not in st.session_state.memory_book:
            st.session_state.memory_book[patient_id] = []
    
    @staticmethod
    def add_media(patient_id: str, media_data: Dict[str, Any]) -> None:
        """Add media item to memory book."""
        st.session_state.memory_book[patient_id].append(media_data)
    
    @staticmethod
    def get_media(patient_id: str) -> List[Dict]:
        """Get all media for patient."""
        return st.session_state.memory_book.get(patient_id, [])


def render_page() -> None:
    """Main function to render the Family Memory Book page."""
    st.title("Memory Book")
    st.success("✏️ You can add, view, and manage memories for your loved one")
    
    patient_info = FamilyPatientSelector.render_selector()
    
    if not patient_info:
        st.stop()
    
    patient_id, patient_name = patient_info
    
    st.divider()
    
    MemoryBookManager.initialize_memory_book(patient_id)
    
    media_data = MediaUploadForm.render()
    
    if media_data:
        MemoryBookManager.add_media(patient_id, media_data)
        st.success(f"Memory '{media_data['title']}' uploaded successfully!")
        st.rerun()
    
    st.divider()
    
    st.subheader(f"Memory Book for {patient_name}")
    
    category_filter = MediaFilter.render_filter()
    
    all_media = MemoryBookManager.get_media(patient_id)
    filtered_media = MediaFilter.apply_filter(all_media, category_filter)
    
    MediaRenderer.render_media_grid(patient_id, filtered_media)
    MediaStatistics.render(all_media)


if __name__ == "__main__":
    render_page()