import streamlit as st

def init_session_state():
    state_defaults = {
        "stream_response": None,
        "question": None,
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
