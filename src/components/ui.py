import streamlit as st

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
