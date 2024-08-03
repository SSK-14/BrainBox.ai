import streamlit as st
import pandas as pd
import json

def example_questions():
    col1, col2 = st.columns(2)
    questions = [
        "What are recent advancements in field of AI?",
        "Recent researches in the field of lung cancer"
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

def display_search_result(search_results):
    with st.expander("Search Results", expanded=False):
        if search_results["results"]:
            col1, col2 = st.columns(2)
            for result, idx in zip(search_results["results"], range(len(search_results["results"]))):
                if idx % 2 == 0:
                    col1.link_button(result['title'], result['url'], use_container_width=True)
                else:
                    col2.link_button(result['title'], result['url'], use_container_width=True)

def display_arxiv_results(results):
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
        if st.button("Quick overview 🤿"):
            st.session_state.search_results = selected_results.to_dict(orient="records")
            st.session_state.deep_dive = True
            st.rerun()

def followup_questions():
    if st.session_state.followup_query and len(st.session_state.followup_query) > 0:
        selected_followup_query = st.radio("Follow-up Questions:", st.session_state.followup_query, index=None)
        if selected_followup_query is not None:
            if st.button("Ask now ⏩", type="primary"):
                st.session_state.messages.append({"role": "user", "content": selected_followup_query})
                st.selected_followup_query = None
                st.session_state.followup_query = []
                st.rerun()

@st.experimental_dialog("Study Details", width="large")
def view_studies(studies, title):
    studies = json.loads(studies)
    st.title(f":blue[{title}]")
    tab_list = [f"{idx+1} | {study['type']}" for idx, study in enumerate(studies)]
    tabs = st.tabs(tab_list)
    for tab, study in zip(tabs, studies):
        with tab:
            with st.container(height=400):
                st.write(study['summary'])
            for link in study['results']:
                st.write(link)