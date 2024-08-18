import streamlit as st
from src.database.study import fetch_all_studies

def init_session_state():
    state_defaults = {
        "stream_response": None,
        "search_results": None,
        "chat_search_results": None,
        "feedback": None,
        "question": None,
        "deep_dive": False,
        "trace_id": None,
        "cache_key": None,
        "title": None,
        "search_type": None,
        "documents": [],
        "studies": fetch_all_studies(),
        "chat_ids": [],
        "messages": [{"role": "assistant", "content": "Hi. I'm BrainBox.AI your super-smart AI assistant. Ask me anything you are looking for from your studies 🪄."}],
        "followup_query": []
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def refresh():
    st.session_state.search_results = None
    st.session_state.stream_response = None
    st.session_state.question = None
    st.session_state.title = None
    st.session_state.deep_dive = False
    st.session_state.documents = []
    st.session_state.trace_id = None
    st.rerun()

def clear_chat_history():
    st.session_state.chat_search_results = None
    st.session_state.followup_query = None
    st.session_state.feedback = None
    st.session_state.question = None
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm WizSearch your super-smart AI assistant. Ask me anything you are looking for 🪄."}]

def get_study_id(study_title):
    study_id = None
    for study in st.session_state.studies:
        if study["title"] == study_title:
            study_id = study["id"]
            break
    return study_id

def get_study_title(study_id):
    study_title = None
    for study in st.session_state.studies:
        if study["id"] == study_id:
            study_title = study["title"]
            break
    return study_title

def study_already_exists(study_title):
    for study in st.session_state.studies:
        if study["title"] == study_title:
            return True
    return False


def handle_study_selection():
    st.session_state.chat_ids = [study['id'] for study in st.session_state.studies if study['title'] in st.session_state.study_selection]
