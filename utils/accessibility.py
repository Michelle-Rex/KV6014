import streamlit as st

def apply_accessibility_css(theme: str, font_size: str, high_contrast: bool):
    font_scale = {
        "small": "14px",
        "medium": "16px",
        "large": "18px",
        "x-large": "20px"
    }.get(font_size, "16px")
    
    # Define colors based on theme
    if theme == "dark":
        # Dark mode colors
        main_bg = "#0E1117"
        main_text = "#FAFAFA"
        sidebar_bg = "#262730"
        sidebar_text = "#FAFAFA"
        button_bg = "#8B5CF6"  # Purple for dark mode
        button_text = "#FFFFFF"
        button_hover = "#7C3AED"
        message_sent_bg = "#8B5CF6"  # Purple bubble for sent messages
        message_sent_text = "#000000"  # Black text for readability in dark mode
        message_received_bg = "#404040"
        message_received_text = "#000000"
    else:
        # Light mode colors  
        main_bg = "#FFFFFF"
        main_text = "#000000"
        sidebar_bg = "#4A90E2"  # Blue sidebar
        sidebar_text = "#FFFFFF"  # White text on blue sidebar
        button_bg = "#7C3AED"  # Violet buttons
        button_text = "#FFFFFF"
        button_hover = "#6D28D9"
        message_sent_bg = "#DCF8C6"  # Keep WhatsApp green for sent
        message_sent_text = "#000000"
        message_received_bg = "#E8E8E8"
        message_received_text = "#000000"
    
    # Adjust for high contrast
    if high_contrast:
        if theme == "dark":
            main_bg = "#000000"
            main_text = "#FFD700"  # Gold text
            sidebar_bg = "#000000"
            sidebar_text = "#FFD700"
        else:
            main_bg = "#FFFFFF"
            main_text = "#000000"
            sidebar_bg = "#000080"  # Darker blue for high contrast
            sidebar_text = "#FFFFFF"
    
    # Inject CSS
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {main_bg} !important;
            }}
            
            .main, .block-container, [data-testid="stAppViewContainer"] {{
                background-color: {main_bg} !important;
            }}
            
            .main .element-container, .stAppToolbar,
            .main [data-testid="stVerticalBlock"],
            .main [data-testid="stHorizontalBlock"] {{
                background-color: {main_bg} !important;
            }}
            
            /* Sidebar */
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] > div {{
                background-color: {sidebar_bg} !important;
            }}
            
            /* All sidebar text elements */
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] *,
            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] span {{
                color: {sidebar_text} !important;
            }}
            
            /* COMPREHENSIVE Main content text - target EVERYTHING at this point... */
            .main *,
            .main,
            .main .stMarkdown,
            .main .stMarkdown *,
            .main p,
            .main label,
            .main h1,
            .main h2,
            .main h3,
            .main h4,
            .main h5,
            .main h6,
            .main li,
            .main span,
            .main div,
            .main td,
            .main th,
            .main a,
            .main strong,
            .main em,
            .main code,
            .main pre,
            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] *,
            [data-testid="stText"],
            [data-testid="stCaption"],
            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"],
            .stAlert,
            .stInfo,
            .stSuccess,
            .stWarning,
            .stError, .stAppToolbar {{
                color: {main_text} !important;
            }}
            
            /* Font size */
            html, body, [class*="st-"] {{
                font-size: {font_scale} !important;
            }}
            
            /* ALL Buttons - comprehensive targeting */
            .stButton button,
            .stButton > button,
            button[kind="primary"],
            button[kind="secondary"],
            .stDownloadButton button,
            .stFormSubmitButton button,
            [data-testid="stFormSubmitButton"] button,
            .row-widget.stButton button {{
                background-color: {button_bg} !important;
                color: {button_text} !important;
                border: none !important;
                font-size: {font_scale} !important;
                transition: background-color 0.3s ease !important;
            }}
            
            /* Button hover state */
            .stButton button:hover,
            button[kind="primary"]:hover,
            button[kind="secondary"]:hover,
            .stDownloadButton button:hover,
            .stFormSubmitButton button:hover {{
                background-color: {button_hover} !important;
            }}
            
            /* Form inputs */
            .stTextInput input, 
            .stTextArea textarea, 
            .stSelectbox select,
            .stNumberInput input,
            input, textarea, select {{
                font-size: {font_scale} !important;
                background-color: {main_bg} !important;
                color: {main_text} !important;
                border-color: {sidebar_bg} !important;
            }}
            
            /* Containers and boxes */
            .stContainer,
            [data-testid="stExpander"],
            [data-testid="stContainer"] {{
                background-color: {main_bg} !important;
            }}
            
            /* Tables and dataframes */
            .stDataFrame,
            .stDataFrame *,
            .dataframe,
            .dataframe * {{
                color: {main_text} !important;
                background-color: {main_bg} !important;
            }}
            
            /* Metrics - force text color */
            [data-testid="stMetric"],
            [data-testid="stMetric"] *,
            [data-testid="stMetricValue"],
            [data-testid="stMetricValue"] *,
            [data-testid="stMetricLabel"],
            [data-testid="stMetricLabel"] * {{
                color: {main_text} !important;
            }}
            
            /* Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background-color: rgba(100, 100, 100, 0.4);
                border-radius: 4px;
            }}
            
            /* Message bubbles styling (for messages page) */
            .message-sent {{
                background-color: {message_sent_bg} !important;
                color: {message_sent_text} !important;
            }}
            
            .message-received {{
                background-color: {message_received_bg} !important;
                color: {message_received_text} !important;
            }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def load_and_apply_preferences(db, user_id: int):
    # Load preferences from database
    prefs = db.get_user_preferences(user_id)
    
    # If preferences don't exist in database yet, create them with defaults
    # This ensures every user has a database entry
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT PreferenceID FROM UserPreferences WHERE UserID = ?', (user_id,))
    exists = cursor.fetchone()
    conn.close()
    
    if not exists:
        # Create default preferences in database
        db.save_user_preferences(user_id, prefs['theme'], prefs['font_size'], prefs['high_contrast'])
    
    # Store in session state for easy access
    st.session_state.user_theme = prefs['theme']
    st.session_state.user_font_size = prefs['font_size']
    st.session_state.user_high_contrast = prefs['high_contrast']
    
    # Apply CSS
    apply_accessibility_css(prefs['theme'], prefs['font_size'], prefs['high_contrast'])