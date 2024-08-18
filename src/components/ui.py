import streamlit as st
from src.database.knowledge import delete_knowledge
from src.database.study import delete_study
from src.modules.utils import get_study_title
import pandas as pd
from collections import defaultdict
import json

def example_questions():
    col1, col2 = st.columns(2)
    questions = [
        "What are recent advancements in field of AI ?",
        "Recent researches in the field of lung cancer ?"
    ]
    if col1.button(questions[0], use_container_width=True):
        st.session_state.question = questions[0]
        st.rerun()
    if col2.button(questions[1], use_container_width=True):
        st.session_state.question = questions[1]
        st.rerun()

def display_chat_messages(messages):
    icons = {"assistant": "🧠", "user": "👤"}
    for message in messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

def display_chat_results(results):
    if len(results) > 0:
        merged_results = defaultdict(lambda: {"texts": [], "sources": set()})
        for result in results:
            metadata_id = result['metadata']['id']
            merged_results[metadata_id]["texts"].append(result['text'])
            merged_results[metadata_id]["sources"].add(result['metadata'].get('source'))
        col1, col2 = st.columns(2)
        id = 0
        for key, value in merged_results.items():
            title = get_study_title(key)
            if id % 2 == 0:
                if col1.button(f"{title}", key=f"result_{title}", use_container_width=True):
                    view_result_studies(title, value)
            else:
                if col2.button(f"{title}", key=f"result_{title}", use_container_width=True):
                    view_result_studies(title, value)
            id += 1


def display_search_result(results):
    results_df = pd.DataFrame(results)
    edited_result = st.data_editor(
        results_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link"),
            "Select": st.column_config.CheckboxColumn("Select")
        }
    )
    selected_results = edited_result[edited_result["Select"] == True] if "Select" in edited_result.columns else None
    if selected_results is not None and len(selected_results) > 0 and not st.session_state.deep_dive:
        if st.button("Generate quick overview 🚀 ", type="primary"):
            st.session_state.search_results = selected_results.to_dict(orient="records")
            st.session_state.deep_dive = True
            st.rerun()

def followup_questions():
    if st.session_state.followup_query and len(st.session_state.followup_query) > 0:
        selected_followup_query = st.radio("Follow-up Questions:", st.session_state.followup_query, index=None)
        if selected_followup_query is not None:
            if st.button("Ask now ⏩", type="primary"):
                st.session_state.messages.append({"role": "user", "content": selected_followup_query})
                st.session_state.followup_query = []
                st.rerun()

@st.dialog("Result sources")
def view_result_studies(title, value):
    st.title(f":orange[{title}]")
    for source in value["sources"]:
        if source:
            st.caption(source)
    with st.container(height=280):
        for text in value["texts"]:
            st.caption(text.replace("\n", " "))

@st.dialog("Study Details", width="large")
def view_studies(studies, title):
    studies = json.loads(studies)
    st.title(f":orange[{title}]")
    tab_list = [f"{idx+1} | {study['type']}" for idx, study in enumerate(studies)]
    tabs = st.tabs(tab_list)
    for tab, study in zip(tabs, studies):
        with tab:
            with st.container(height=400):
                st.write(study['summary'])
            for link in study['results']:
                st.write(link)

@st.dialog("Delete Study")
def delete_Study(study):
    st.title(f":orange[{study['title']}]")
    st.write("Are you sure you want to delete this study?")
    col1, col2 = st.columns(2)
    if col1.button("Yes sure", type="primary", use_container_width=True):
        delete_knowledge(study["id"])
        delete_study(study["id"])
        st.toast("Study deleted successfully.")
        st.session_state.studies.remove(study)
        st.rerun()
    if col2.button("Cancel", type="secondary", use_container_width=True):
        st.rerun()