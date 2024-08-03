import asyncio, json
import streamlit as st
from src.components.sidebar import side_info
from src.components.ui import view_studies
from src.modules.utils import init_session_state


def display_studies(study):
    with st.container(border=True, height=72):
        col1, col2, col3 = st.columns([3,1,1])
        col1.subheader(f":blue[{study['title']}]")
        if col2.button("View 📄", use_container_width=True):
            view_studies(study["study_data"], study["title"])
        if col3.button(f"{ 'Remove' if study['id'] in st.session_state.chat_ids else 'Add'} 💬", use_container_width=True, key=f"add_{study['id']}", type="primary"):
            if study["id"] in st.session_state.chat_ids:
                st.session_state.chat_ids.remove(study["id"])
            else:
                st.session_state.chat_ids.append(study["id"])
            st.rerun()

async def main():
    st.title("📚 :blue[My.]:blue-background[Studies]")
    side_info()
    init_session_state()
    st.markdown("---")
    with st.container(height=600, border=False):
        if st.session_state.studies:
            for study in st.session_state.studies:
                display_studies(study)
        else:
            st.error("No studies found.")


if __name__ == "__main__":
    st.set_page_config(page_title="My Studies", page_icon="📚", layout="wide")
    _, col, _ = st.columns([1, 8, 1])
    with col:
        asyncio.run(main())
