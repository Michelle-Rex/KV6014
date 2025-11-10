import streamlit as st

# I am using streamlit session data rather than the database as erm we don't need to use the database if we are smart :)

def apply_preferences():
    # read current user's session data
    # apply session_state data via CSS injection
    # should be safe for mobile and tablets as it only changes font sizes, colour contrasts, and theme(light/dark)

    st.session_state.setdefault("theme", "light")
    st.session_state.setdefault("font_size", "medium")
    st.session_state.setdefault("high_contrast", False)

    theme = st.session_state["theme"] # on second thought, we could try this as a ternary operator
    font_size = st.session_state["font_size"]
    high_contrast = st.session_state["high_contrast"]

    font_scale = { # note to self: ask Adam about CSS values like rem values
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

    # adjust for high contrast as that is a thing sites do I think
    if high_contrast and (theme == "dark"):
        bg_colour = "#000000"
        text_colour = "#FFD700"

    # Inject the CSS

    st.markdown(
            f"""
            <style>
                html, body, [class*="st-"] {{
                    background-color: {bg_colour} !important;
                    color: {text_colour} !important;
                    font-size: {font_scale} !important;
                    transition: all 0.3s ease-in-out;
                }}

                ::-webkit-scrollbar {{
                    width: 8px;
                }}

                ::-webkit-scrollbar-thumb {{
                    background-color: rgba(100, 100, 100, 0.4);
                    border-radius: 4px;
                }}
            </style>
            """, unsafe_allow_html=True,
            )


# Settings panel for users

def accessibility_settings_panel():
    # This just allows us to put the widget on any page, pretty neat :D

    with st.sidebar.expander("Accessibility Settings", expanded=False):
        # Use local variables for temporary choices
        theme_choice = st.radio(
            "Theme",
            ["light", "dark"],
            index=0 if st.session_state.get("theme", "light") == "light" else 1)

        font_choice = st.selectbox(
            "Font Size",
            ["small", "medium", "large", "x-large"],
            index=["small", "medium", "large", "x-large"].index(st.session_state.get("font_size", "medium")))

        high_contrast_choice = st.checkbox(
            "High Contrast Mode",
            st.session_state.get("high_contrast", False))

        # Apply button
        if st.button("Apply Preferences"):

            st.session_state["theme"] = theme_choice
            st.session_state["font_size"] = font_choice
            st.session_state["high_contrast"] = high_contrast_choice

            apply_preferences()
            st.rerun()
        
            # TODO Maybe a reset button too
