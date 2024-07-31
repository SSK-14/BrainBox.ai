import streamlit as st
import pandas as pd

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

def display_search_result(search_results):
    with st.expander("Search Results", expanded=False):
        if search_results["results"]:
            for result in search_results["results"]:
                st.write(f"- [{result['title']}]({result['url']})")

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
        if st.button("Do a Deep Dive 🤿"):
            st.session_state.search_results = selected_results.to_dict(orient="records")
            st.session_state.deep_dive = True
            st.rerun()
