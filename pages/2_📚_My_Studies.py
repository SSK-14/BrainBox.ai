import asyncio
import streamlit as st
from src.components.sidebar import side_info
from src.components.ui import view_studies, delete_Study
from src.modules.utils import init_session_state


def display_studies(study):
    with st.container(border=True, height=75):
        col1, col2, col3 = st.columns([4,1,1])
        col1.markdown(f"### *:orange[{study['title']}]*")
        if col2.button("Delete 🗑️", use_container_width=True, key=f"delete_{study['id']}"):
            delete_Study(study)
        if col3.button("View 📄", use_container_width=True, key=f"view_{study['id']}", type="primary"):
            view_studies(study["study_data"], study["title"])

async def main():
    st.title("📚 :orange[My.Studies]")
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
