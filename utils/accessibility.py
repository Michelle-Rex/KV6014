import streamlit as st

def apply_accessibility_css(theme: str, font_size: str, high_contrast: bool):
    font_scale = {
        "small": "14px",
        "medium": "16px",
        "large": "18px",
        "x-large": "20px"
    }.get(font_size, "16px")
    
    if theme == "dark":
        bg_colour = "#0E1117"
        text_colour = "#FAFAFA"
    else:
        bg_colour = "#FFFFFF"
        text_colour = "#000000"
    
    # Adjust for high contrast
    if high_contrast and theme == "dark":
        bg_colour = "#000000"
        text_colour = "#FFD700"
    elif high_contrast and theme == "light":
        bg_colour = "#FFFFFF"
        text_colour = "#000000"
    
    # Inject CSS
    st.markdown(
        f"""
        <style>
            html, body, [class*="st-"] {{
                background-color: {bg_colour} !important;
                color: {text_colour} !important;
                font-size: {font_scale} !important;
                transition: all 0.3s ease-in-out;
            }}
            
            .stButton button {{
                font-size: {font_scale} !important;
            }}
            
            .stTextInput input, .stTextArea textarea, .stSelectbox select {{
                font-size: {font_scale} !important;
            }}
            
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background-color: rgba(100, 100, 100, 0.4);
                border-radius: 4px;
            }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def load_and_apply_preferences(db, user_id: int):
    # Load preferences from database
    prefs = db.get_user_preferences(user_id)
    
    # Store in session state for easy access
    st.session_state.user_theme = prefs['theme']
    st.session_state.user_font_size = prefs['font_size']
    st.session_state.user_high_contrast = prefs['high_contrast']
    
    # Apply CSS
    apply_accessibility_css(prefs['theme'], prefs['font_size'], prefs['high_contrast'])
